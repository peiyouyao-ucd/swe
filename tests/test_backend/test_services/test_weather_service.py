import os
import sys
import unittest

# Ensure the backend directory is in the path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../backend')))

from repository.weather_repo import InMemoWeatherRepository
from services.weather_service import WeatherService


# Reusable raw OWM API response matching the real API schema
SAMPLE_RAW_WEATHER = {
    'dt': 1711641600,
    'main': {
        'temp': 9.5,
        'feels_like': 7.2,
        'temp_min': 8.1,
        'temp_max': 11.3,
        'humidity': 82,
        'pressure': 1015
    },
    'wind': {'speed': 4.6, 'deg': 230},
    'visibility': 10000,
    'weather': [{'id': 500, 'main': 'Rain', 'description': 'light rain', 'icon': '10d'}],
    'rain': {'1h': 0.65},
    'coord': {'lat': 53.344, 'lon': -6.2672},
    'name': 'Dublin',
    'sys': {'country': 'IE'}
}


class TestWeatherService(unittest.TestCase):

    def setUp(self):
        """Sets up an in-memory weather repository and weather service for each test."""
        self.weather_repo = InMemoWeatherRepository(max_size=10)
        self.weather_service = WeatherService(self.weather_repo)

    def test_save_weather_data_success(self):
        """Tests that raw OWM API data is correctly transformed and saved."""
        self.weather_service.save_from_raw_weather_data(SAMPLE_RAW_WEATHER)
        result = self.weather_service.get_latest_weather_data()
        self.assertIsNotNone(result)

    def test_saved_weather_temperature_correct(self):
        """Tests that temperature is correctly extracted from the raw API response."""
        self.weather_service.save_from_raw_weather_data(SAMPLE_RAW_WEATHER)
        result = self.weather_service.get_latest_weather_data()
        self.assertAlmostEqual(result.temp, 9.5)

    def test_saved_weather_humidity_correct(self):
        """Tests that humidity is correctly extracted from the raw API response."""
        self.weather_service.save_from_raw_weather_data(SAMPLE_RAW_WEATHER)
        result = self.weather_service.get_latest_weather_data()
        self.assertEqual(result.humidity, 82)

    def test_saved_weather_description_correct(self):
        """Tests that the weather description string is correctly extracted."""
        self.weather_service.save_from_raw_weather_data(SAMPLE_RAW_WEATHER)
        result = self.weather_service.get_latest_weather_data()
        self.assertEqual(result.description, 'light rain')

    def test_saved_weather_main_correct(self):
        """Tests that the weather main category (e.g. Rain) is correctly extracted."""
        self.weather_service.save_from_raw_weather_data(SAMPLE_RAW_WEATHER)
        result = self.weather_service.get_latest_weather_data()
        self.assertEqual(result.main, 'Rain')

    def test_precipitation_extracted_from_rain_field(self):
        """Tests that precipitation is correctly read from the rain.1h field."""
        self.weather_service.save_from_raw_weather_data(SAMPLE_RAW_WEATHER)
        result = self.weather_service.get_latest_weather_data()
        self.assertAlmostEqual(result.precipitation, 0.65)

    def test_precipitation_defaults_to_zero_when_no_rain(self):
        """Tests that precipitation defaults to 0.0 when the rain field is absent."""
        dry_weather = dict(SAMPLE_RAW_WEATHER)
        dry_weather.pop('rain', None)
        self.weather_service.save_from_raw_weather_data(dry_weather)
        result = self.weather_service.get_latest_weather_data()
        self.assertEqual(result.precipitation, 0)

    def test_get_latest_returns_none_when_empty(self):
        """Tests that get_latest_weather_data returns None when no data has been saved."""
        result = self.weather_service.get_latest_weather_data()
        self.assertIsNone(result)

    def test_get_latest_returns_most_recent_record(self):
        """Tests that get_latest returns the most recently saved record when multiple exist."""
        # Save an older record first
        older = dict(SAMPLE_RAW_WEATHER)
        older['dt'] = 1711641600
        self.weather_service.save_from_raw_weather_data(older)

        # Save a newer record
        newer = dict(SAMPLE_RAW_WEATHER)
        newer['dt'] = 1711728000
        newer['main'] = dict(newer['main'])
        newer['main']['temp'] = 14.0
        self.weather_service.save_from_raw_weather_data(newer)

        result = self.weather_service.get_latest_weather_data()
        self.assertAlmostEqual(result.temp, 14.0)

    def test_wind_speed_correct(self):
        """Tests that wind speed is correctly extracted from the raw API response."""
        self.weather_service.save_from_raw_weather_data(SAMPLE_RAW_WEATHER)
        result = self.weather_service.get_latest_weather_data()
        self.assertAlmostEqual(result.wind_speed, 4.6)


if __name__ == '__main__':
    unittest.main()
