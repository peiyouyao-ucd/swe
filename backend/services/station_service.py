from repository.station_repo import StationRepository
import time
import pickle
import pandas as pd
import os
import logging
from datetime import datetime

class StationService:
    def __init__(self, repo: StationRepository, weather_service=None):
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
        Processes raw station data from API and persists each station to the SQL database.
        """
       
        processed_stations = [
            {
                'number': station.get('number'),
                'name': station.get('name'),
                'address': station.get('address'),
                'position': station.get('position', {}),
                'bike_stands': station.get('bike_stands'),
                'status': station.get('status'),
                'banking': station.get('banking'),
                'bonus': station.get('bonus'),
              
                'available_bikes': station.get('available_bikes'),
                'available_bike_stands': station.get('available_bike_stands'),
                'last_update': station.get('last_update')
            }
            for station in raw_stations_data
        ]

        # 2. Iterate and save each station
        for station in processed_stations:
            try:
                self._repo.save(station)
            except Exception as e:
                logging.error(f"Failed to save station {station.get('number')}: {e}")


    def get_latest_all_stations(self) -> list:
        """
        Retrieves current snapshots of all stations from the database.
        """
        # Aligning with SQLStationRepository.get_all()
        return self._repo.get()

    def get_one_station(self, station_number: int) -> dict:
        """
        Retrieves a single station's details by its ID.
        """
        # Aligning with SQLStationRepository.get_by_id()
        return self._repo.get(station_number=station_number)
    

    def predict_for_one_station(self, station_number: int) -> int:
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
            # 1. Get current weather
            weather_data = self._weather_service.get_latest_weather_data()
            if not weather_data:
                logging.warning("No weather data available for prediction.")
                return -1

            # 2. Get current time features
            now = datetime.now()
            hour = now.hour
            day_of_week = now.weekday()

            # 3. Prepare features (matches training schema)
            # features = ['station_id','temperature', 'humidity', 'wind_speed', 'precipitation', 'hour', 'day_of_week']
            input_df = pd.DataFrame([{
                'station_id': station_number,
                'temperature': weather_data.get('temp', 15.0), # Default if missing
                'humidity': weather_data.get('humidity', 50),
                'wind_speed': weather_data.get('wind_speed', 0.0),
                'precipitation': weather_data.get('precipitation', 0.0), # Note: we might need to handle this key carefully if it doesn't exist
                'hour': hour,
                'day_of_week': day_of_week
            }])

            # 4. Make prediction
            prediction = self._model.predict(input_df)
            
            # Ensure output is a non-negative integer
            return max(0, int(round(prediction[0])))

        except Exception as e:
            logging.error(f"Error during prediction for station {station_number}: {e}")
            return -1
