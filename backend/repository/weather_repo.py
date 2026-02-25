from abc import ABC, abstractmethod
import threading

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
                # ... and all other fields
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