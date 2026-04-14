from abc import ABC, abstractmethod
import threading 
from utils.db import db

class WeatherRepository(ABC):
    @abstractmethod
    def save(self, saving_weather_data):
        """Saves the processed and flattened weather data.

        Args:
            saving_weather_data (dict): A dictionary containing the processed
                weather data, conforming to the `saving_weather_data` schema
                as defined in the `WeatherService`.

        The `saving_weather_data` schema is:
        .. code-block:: python

            {
                'city_id': int,
                'city_name': str,
                'country': str,
                'lon': float,
                'lat': float,
                'timestamp': int,
                'temp': float,
                'feels_like': float,
                'temp_min': float,
                'temp_max': float,
                'pressure': int,
                'humidity': int,
                'wind_speed': float,
                'wind_deg': int,
                'precipitation': float,
                'clouds_all': int,
                'weather_id': int,
                'weather_main': str,
                'weather_description': str,
                'weather_icon': str
            }
        """
        pass
    
    @abstractmethod
    def get(self, time_from=None, time_to=None):
        """Retrieves weather data from the repository within a given time range.

        Args:
            time_from (int, optional): The start of the time range as a
                UTC Unix timestamp. If None, retrieves data from the
                beginning. Defaults to None.
            time_to (int, optional): The end of the time range as a
                UTC Unix timestamp. If None, retrieves data up to the
                latest record. Defaults to None.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary is a
            weather record conforming to the `saving_weather_data` schema.
            If `time_from` and `time_to` are both None, it should return
            only the single most recent record.
        """
        pass


class InMemoWeatherRepository(WeatherRepository):
    """An in-memory implementation of the WeatherRepository.

    Stores weather data in a list, with a configurable maximum size.
    This implementation is thread-safe.
    """
    def __init__(self, max_size: int = 100):
        self._data = []
        self._max_size = max_size
        self._lock = threading.Lock()

    def save(self, saving_weather_data: dict):
        with self._lock:
            # Add new data and sort by timestamp to easily find the oldest
            self._data.append(saving_weather_data)
            self._data.sort(key=lambda x: x.get('timestamp', 0))

            # Trim old data if the list is too large
            if len(self._data) > self._max_size:
                self._data = self._data[-self._max_size:]

    def get(self, time_from: int = None, time_to: int = None) -> list[dict]:
        with self._lock:
            # If no time range is specified, return the latest entry
            if time_from is None and time_to is None:
                return self._data[-1:] if self._data else []

            # Filter data based on the provided time range
            filtered_data = self._data
            if time_from is not None:
                filtered_data = [d for d in filtered_data if d.get('timestamp', 0) >= time_from]
            if time_to is not None:
                filtered_data = [d for d in filtered_data if d.get('timestamp', 0) <= time_to]
            
            return filtered_data
        

class SQLWeatherRepository(WeatherRepository):
    def save(self, saving_weather_data: dict):
        from models import Weather
        
     
        new_weather = Weather(
            dt=saving_weather_data['timestamp'],
            temp=saving_weather_data['temp'],
            feels_like=saving_weather_data.get('feels_like'), 
            temp_min=saving_weather_data.get('temp_min'),    
            temp_max=saving_weather_data.get('temp_max'),     
            visibility=saving_weather_data.get('visibility'), 
            precipitation=saving_weather_data.get('precipitation', 0),
            humidity=saving_weather_data['humidity'],
            wind_speed=saving_weather_data['wind_speed'],
            description=saving_weather_data['weather_description'],
            main=saving_weather_data['weather_main']
        )
        
      
        db.session.merge(new_weather) 
        db.session.commit()

    def get(self, time_from=None, time_to=None):
        from models import Weather
      
        latest = Weather.query.order_by(Weather.dt.desc()).first()
        
      
        if latest is None:
            return [{
                "temp": 0,
                "feels_like": 0,    
                "temp_min": 0,
                "temp_max": 0,
                "visibility": 0,
                "precipitation": 0,
                "humidity": 0,
                "wind_speed": 0,
                "weather_description": "Database is empty",
                "weather_main": "None",
                "dt": 0
            }]
            
     
        return [latest.to_dict()]