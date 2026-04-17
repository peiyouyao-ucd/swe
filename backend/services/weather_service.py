from repository.weather_repo import WeatherRepository
from models import Weather

class WeatherService:
    def __init__(self, repo: WeatherRepository):
        self._repo = repo
    
    def save_from_raw_weather_data(self, raw_weather_data: dict):
        """
        Extracts weather information and persists it as a Weather model instance.
        """
        weather_info = raw_weather_data.get('weather', [{}])[0]
        main_info = raw_weather_data.get('main', {})
        rain_info = raw_weather_data.get('rain', {})
        
        # Standardize precipitation
        precipitation = rain_info.get('1h', rain_info.get('3h', 0))

        # Instantiate Model
        weather = Weather(
            dt=raw_weather_data.get('dt'),
            temp=main_info.get('temp'),
            feels_like=main_info.get('feels_like'),
            temp_min=main_info.get('temp_min'),
            temp_max=main_info.get('temp_max'),
            visibility=raw_weather_data.get('visibility'),
            humidity=main_info.get('humidity'),
            wind_speed=raw_weather_data.get('wind', {}).get('speed'),
            precipitation=precipitation,
            description=weather_info.get('description'),
            main=weather_info.get('main'),
        )
        
        self._repo.save(weather)
    
    
    def get_latest_weather_data(self) -> Weather:
        """Retrieves the most recent weather data from the repository.

        Returns:
            Weather: The latest weather model instance.
        """
        latest_data = self._repo.get()
        return latest_data[0] if latest_data else None
