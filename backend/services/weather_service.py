from repository.weather_repo import WeatherRepository

class WeatherService:
    def __init__(self, repo: WeatherRepository):
        self._repo = repo
    
    def save_from_raw_weather_data(self, raw_weather_data: dict):
        """Processes raw weather data and saves it to the repository.

        This method takes the nested dictionary returned by the OWM API,
        flattens it into a structured format (`saving_weather_data`),
        and then calls the repository's save method to persist it.

        Args:
            raw_weather_data (dict): The raw weather data from the API.
                See `weather_scraper.py` for the detailed structure.
        """
        # Extract data from nested structures, providing default values
        weather_info = raw_weather_data.get('weather', [{}])[0]
        main_info = raw_weather_data.get('main', {})
        wind_info = raw_weather_data.get('wind', {})
        coord_info = raw_weather_data.get('coord', {})
        sys_info = raw_weather_data.get('sys', {})

        saving_weather_data = {
            'city_id': raw_weather_data.get('id'),
            'city_name': raw_weather_data.get('name'),
            'country': sys_info.get('country'),
            'lon': coord_info.get('lon'),
            'lat': coord_info.get('lat'),
            'timestamp': raw_weather_data.get('dt'),
            'timezone': raw_weather_data.get('timezone'),
            'sunrise': sys_info.get('sunrise'),
            'sunset': sys_info.get('sunset'),
            'temp': main_info.get('temp'),
            'feels_like': main_info.get('feels_like'),
            'temp_min': main_info.get('temp_min'),
            'temp_max': main_info.get('temp_max'),
            'pressure': main_info.get('pressure'),
            'humidity': main_info.get('humidity'),
            'wind_speed': wind_info.get('speed'),
            'wind_deg': wind_info.get('deg'),
            'clouds_all': raw_weather_data.get('clouds', {}).get('all'),
            'visibility': raw_weather_data.get('visibility'),
            'weather_id': weather_info.get('id'),
            'weather_main': weather_info.get('main'),
            'weather_description': weather_info.get('description'),
            'weather_icon': weather_info.get('icon'),
        }
        self._repo.save(saving_weather_data)

    def get_latest_weather_data(self) -> dict:
        """Retrieves the most recent weather data from the repository.

        Returns:
            dict: A dictionary containing the latest weather data, formatted as
            the `saving_weather_data` schema. Returns an empty dict
            if no data is available.
        """
        latest_data = self._repo.get()
        return latest_data[0] if latest_data else {}
