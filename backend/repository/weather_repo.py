from abc import ABC, abstractmethod
import logging

from models import Weather
from db import db

class WeatherRepository(ABC):
    @abstractmethod
    def save(self, weather: Weather):
        """
        Persists a Weather model instance to the storage layer.
        """
        pass
    
    @abstractmethod
    def get(self, time_from: int = None, time_to: int = None) -> list[Weather]:
        """
        Retrieves weather records within a given time range.
        If both are None, returns the single most recent record.
        Returns: list[Weather]
        """
        pass

class SQLWeatherRepository(WeatherRepository):
    def save(self, weather: Weather):
        try:
            db.session.merge(weather)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving weather: {e}")

    def get(self, time_from: int = None, time_to: int = None) -> list[Weather]:
        # If no timeframe, return latest
        if time_from is None and time_to is None:
            latest = Weather.query.order_by(Weather.dt.desc()).first()
            return [latest] if latest else []

        query = Weather.query
        if time_from:
            query = query.filter(Weather.dt >= time_from)
        if time_to:
            query = query.filter(Weather.dt <= time_to)
            
        return query.order_by(Weather.dt.asc()).all()
    
class InMemoWeatherRepository(WeatherRepository):
    """Refactored In-Memory implementation matching the model-based interface."""
    def __init__(self, max_size: int = 100):
        import threading
        self._data = []
        self._max_size = max_size
        self._lock = threading.Lock()

    def save(self, weather: Weather):
        with self._lock:
            self._data.append(weather)
            self._data.sort(key=lambda x: x.dt)
            if len(self._data) > self._max_size:
                self._data = self._data[-self._max_size:]

    def get(self, time_from: int = None, time_to: int = None) -> list[Weather]:
        with self._lock:
            if time_from is None and time_to is None:
                return [self._data[-1]] if self._data else []

            filtered = self._data
            if time_from:
                filtered = [d for d in filtered if d.dt >= time_from]
            if time_to:
                filtered = [d for d in filtered if d.dt <= time_to]
            
            return filtered
