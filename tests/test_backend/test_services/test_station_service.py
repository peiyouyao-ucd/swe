import os
import sys
import unittest
import logging

# Ensure the backend directory is in the path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../backend')))

from repository.station_repo import InMemoStationRepository
from repository.weather_repo import InMemoWeatherRepository
from services.station_service import StationService
from services.weather_service import WeatherService

class TestStationService(unittest.TestCase):
    def setUp(self):
        """Sets up the test environment with in-memory repositories and services."""
        # Use In-Memory repositories to avoid side effects
        self.station_repo = InMemoStationRepository(max_size=10)
        self.weather_repo = InMemoWeatherRepository(max_size=10)
        
        # Initialize services
        self.weather_service = WeatherService(self.weather_repo)
        self.station_service = StationService(self.station_repo, self.weather_service)

    def test_save_and_get_stations(self):
        """Tests if station data is correctly transformed and saved."""
        raw_data = [
            {
                'number': 42,
                'name': 'Test Station',
                'address': '123 Fake St',
                'available_bikes': 10,
                'available_bike_stands': 20,
                'bike_stands': 30,
                'status': 'OPEN',
                'position': {'lat': 53.3, 'lng': -6.2}
            }
        ]
        
        # Save data
        self.station_service.save_station_data(raw_data)
        
        # Retrieve data
        result = self.station_service.get_latest_all_stations()
        
        # In current implementation, get_latest_all_stations returns a list of snapshots
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        latest_snapshot = result[0]
        self.assertIn('stations', latest_snapshot)
        self.assertEqual(len(latest_snapshot['stations']), 1)
        self.assertEqual(latest_snapshot['stations'][0]['number'], 42)
        self.assertEqual(latest_snapshot['stations'][0]['available_bikes'], 10)

    def test_prediction_with_dummy_data(self):
        """Tests the prediction logic using mocked weather and station data."""
        # 1. Prepare Dummy Weather (matching OpenWeatherMap raw structure)
        raw_weather = {
            'main': {'temp': 18.5, 'humidity': 60, 'pressure': 1013},
            'wind': {'speed': 5.5, 'deg': 200},
            'clouds': {'all': 20},
            'dt': 1711641600,
            'id': 2964574,
            'name': 'Dublin',
            'sys': {'country': 'IE'},
            'coord': {'lon': -6.2, 'lat': 53.3},
            'weather': [{'id': 800, 'main': 'Clear', 'description': 'clear sky', 'icon': '01d'}]
        }
        self.weather_service.save_from_raw_weather_data(raw_weather)
        
        # 2. Run Prediction
        # Even without station data saved, the model should work if it's loaded
        prediction = self.station_service.predict_for_one_station(42)
        
        # 3. Assertions
        if self.station_service._model is not None:
            logging.info(f"Test prediction result: {prediction}")
            self.assertIsInstance(prediction, int)
            self.assertGreaterEqual(prediction, 0)
        else:
            # If model file doesn't exist during test, it should return -1
            self.assertEqual(prediction, -1)

if __name__ == '__main__':
    unittest.main()
