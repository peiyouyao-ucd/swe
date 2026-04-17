from abc import ABC, abstractmethod
import logging

from sqlalchemy import func, select

from db import db
from models import Station, Availability

class StationRepository(ABC):
    @abstractmethod
    def save_stations(self, stations: list[Station]):
        """
        Persists station metadata. Compares with existing data 
        and only inserts/updates if necessary.
        """
        pass

    @abstractmethod
    def save_availabilities(self, availabilities: list[Availability]):
        """
        Persists a batch of availability timeseries records.
        """
        pass

    @abstractmethod
    def get_stations_latest(self) -> list[tuple[Station, Availability]]:
        """
        Retrieves the latest state for all stations.
        Returns: list[tuple[Station, Availability]]
        """
        pass

    @abstractmethod
    def get_history(self, station_number: int, time_from: int = None, time_to: int = None) -> list[Availability]:
        """
        Retrieves historical records for a specific station.
        Returns: list[Availability]
        """
        pass

class SQLStationRepository(StationRepository):
    """
    MySQL implementation with decoupled metadata and dynamic status updates.
    """

    def save_stations(self, stations: list[Station]):
        try:
            # Upsert logic: only save if doesn't exist or changes suspected
            # For simplicity and robustness, we use session.merge (performs SELECT then INSERT/UPDATE)
            for s in stations:
                db.session.merge(s)
            db.session.flush() # Ensure foreign key constraints will be met
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving station metadata: {e}")

    def save_availabilities(self, availabilities: list[Availability]):
        try:
            # Bulk add for efficiency
            db.session.add_all(availabilities)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving availabilities: {e}")

    def get_stations_latest(self) -> list[tuple[Station, Availability]]:
        # Subquery to find the latest availability ID for each station
        subq = select(func.max(Availability.id)).group_by(Availability.number)

        # Join stations with their latest availability status
        query = db.session.query(Station, Availability).outerjoin(
            Availability, Station.number == Availability.number
        ).filter(
            (Availability.id.in_(subq)) | (Availability.id == None)
        )

        return query.all() # Returns list[tuple[Station, Availability]]

    def get_history(self, station_number: int, time_from: int = None, time_to: int = None) -> list[Availability]:
        query = db.session.query(Availability).filter(Availability.number == station_number)
        
        if time_from:
            query = query.filter(Availability.last_update >= time_from)
        if time_to:
            query = query.filter(Availability.last_update <= time_to)

        return query.order_by(Availability.last_update.asc()).all()

class InMemoStationRepository(StationRepository):
    """Refactored In-Memory implementation matching the new model-based interface."""
    def __init__(self):
        import threading
        self._stations = {}  # number -> Station model
        self._availability = [] # list of Availability models
        self._lock = threading.Lock()

    def save_stations(self, stations: list[Station]):
        with self._lock:
            for s in stations:
                self._stations[s.number] = s

    def save_availabilities(self, availabilities: list[Availability]):
        with self._lock:
            self._availability.extend(availabilities)

    def get_stations_latest(self) -> list[tuple[Station, Availability]]:
        with self._lock:
            results = []
            for num, s in self._stations.items():
                station_avail = [a for a in self._availability if a.number == num]
                latest = station_avail[-1] if station_avail else None
                results.append((s, latest))
            return results

    def get_history(self, station_number: int, time_from: int = None, time_to: int = None) -> list[Availability]:
        with self._lock:
            history = [a for a in self._availability if a.number == station_number]
            if time_from:
                history = [a for a in history if a.last_update >= time_from]
            if time_to:
                history = [a for a in history if a.last_update <= time_to]
            return history
