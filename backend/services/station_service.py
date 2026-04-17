import os
import logging
import time
from datetime import datetime, timedelta

import pickle
import pandas as pd

from repository.station_repo import StationRepository
from services.weather_service import WeatherService
from models import Station, Availability

class StationService:
    def __init__(self, repo: StationRepository, weather_service: WeatherService=None):
        """Initializes the StationService with a data repository and weather service.

        Args:
            repo (StationRepository): An implementation of the StationRepository
                used for data persistence.
            weather_service (WeatherService, optional): The service to fetch current weather data.
        """
        self._repo = repo
        self._weather_service = weather_service
        self._model = None
        self._load_model()

    def _load_model(self):
        """Loads the pre-trained machine learning model."""
        try:
            model_path = os.path.join(os.path.dirname(__file__), '../../ml_training/bike_availability_model.pkl')
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self._model = pickle.load(f)
                logging.info(f"Machine learning model loaded successfully from {model_path}")
            else:
                logging.warning(f"Model file not found at {model_path}. Predictions will be unavailable.")
        except Exception as e:
            logging.error(f"Failed to load machine learning model: {e}")

    def save_station_data(self, raw_stations_data: list[dict]):
        """
        Transforms raw API data into Station and Availability model instances 
        and persists them via the repository.
        """
        stations = []
        availabilities = []

        for item in raw_stations_data:
            # 1. Create Station Metadata Model
            station = Station(
                number=item.get('number'),
                name=item.get('name'),
                address=item.get('address'),
                lat=item.get('position', {}).get('lat'),
                lng=item.get('position', {}).get('lng'),
                bike_stands=item.get('bike_stands'),
                status=item.get('status'),
                banking=item.get('banking'),
                bonus=item.get('bonus')
            )
            stations.append(station)

            # 2. Create Availability Timeseries Model
            availability = Availability(
                number=item.get('number'),
                available_bikes=item.get('available_bikes', 0),
                available_bike_stands=item.get('available_bike_stands', 0),
                status=item.get('status'),
                last_update=item.get('last_update')
            )
            availabilities.append(availability)

        # 3. Batch Save
        try:
            # We save metadata and dynamics separately
            self._repo.save_stations(stations)
            self._repo.save_availabilities(availabilities)
        except Exception as e:
            logging.error(f"Failed to perform batch save: {e}")


    def get_latest_all_stations(self) -> list[tuple[Station, Availability]]:
        """
        Retrieves current snapshots of all stations from the database.
        Returns: list[tuple[Station, Availability]]
        """
        return self._repo.get_stations_latest()

    def get_one_station_details(self, station_number: int) -> dict:
        """
        Retrieves a comprehensive data package for a single station.
        Includes history availabilities, and ML predictions.
        """
        # Explicit 24h time bound (in ms)
        time_from = int((time.time() - 24 * 3600) * 1000)
        
        history_records = self._repo.get_history(station_number=station_number, time_from=time_from)
        if not history_records:
            return None
        
        # Latest record from history or repo
        latest_record = history_records[-1] if history_records else None
        prediction_value = self._predict_for_one_station(station_number)
        
        # Build composite result containing Models
        result = {
            "latest": latest_record,
            "prediction": prediction_value if prediction_value != -1 else "N/A",
            "history": history_records,
            "forecast_24h": self._get_24h_forecast(station_number)
        }
        return result
    

    def _predict_for_one_station(self, station_number: int) -> int:
        """Predicts future availability for a single station using current weather and time.

        Args:
            station_number (int): The ID of the station to predict for.

        Returns:
            int: Predicted number of available bikes. Returns -1 if prediction fails.
        """
        if self._model is None:
            logging.error("Model not loaded. Cannot predict.")
            return -1

        if self._weather_service is None:
            logging.error("Weather service not provided. Cannot fetch weather features.")
            return -1

        try:
            # Get current weather
            weather_data = self._weather_service.get_latest_weather_data()
            if not weather_data:
                logging.warning("No weather data available for prediction.")
                return -1

            # Prepare features and make prediction
            input_df = self._prepare_ml_features(station_number, weather_data, datetime.now())
            prediction = self._model.predict(input_df)
            
            # Ensure output is a non-negative integer
            return max(0, int(round(prediction[0])))

        except Exception as e:
            logging.error(f"Error during prediction for station {station_number}: {e}")
            return -1


    def _get_24h_forecast(self, station_number: int) -> list:

        if self._model is None:
            return []

        forecast_list = []
        now = datetime.now()
        weather_data = self._weather_service.get_latest_weather_data() if self._weather_service else None

        for i in range(24):
            future_time = now + timedelta(hours=i)
            input_df = self._prepare_ml_features(station_number, weather_data, future_time)
            try:
                prediction = self._model.predict(input_df)
                pred_value = max(0, int(round(prediction[0])))
            except Exception:
                pred_value = -1
            forecast_list.append({
                'hours_ahead': i,
                'time_label': f"{future_time.hour:02d}:00", # "14:00"
                'prediction': pred_value
            })
        return forecast_list

    def _prepare_ml_features(self, station_number: int, weather_data, target_time: datetime) -> pd.DataFrame:
        """Helper to prepare a DataFrame of features for the ML model."""
        # Detect if we have a Model or a dict (fallback for empty state)
        if hasattr(weather_data, 'temp'):
            temp = weather_data.temp
            humidity = weather_data.humidity
        elif isinstance(weather_data, dict):
            temp = weather_data.get('temp', 15.0)
            humidity = weather_data.get('humidity', 50)
        else:
            temp = 15.0
            humidity = 50

        return pd.DataFrame([{
            'station_id': station_number,
            'temperature': temp,
            'humidity': humidity,
            'hour': target_time.hour,
            'day_of_week': target_time.weekday()
        }])