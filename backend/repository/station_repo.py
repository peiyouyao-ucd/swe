from abc import ABC, abstractmethod
import threading
from utils.db import db
import time

class StationRepository(ABC):
    @abstractmethod
    def save(self, saving_stations_data: dict):
        """Saves the processed and structured station data.

        Args:
            saving_stations_data (dict): A dictionary containing the processed
                station data, conforming to the `saving_stations_data` schema.

        The `saving_stations_data` schema is:
        .. code-block:: python

            {
                'timestamp': int,
                'stations': [
                    {
                        'address': str,
                        'available_bike_stands': int,
                        'available_bikes': int,
                        'banking': bool,
                        'bike_stands': int,
                        'bonus': bool,
                        'contract_name': str,
                        'name': str,
                        'number': int,
                        'lat': float,
                        'lon': float,
                        'status': str,
                    }
                ]
            }
        """
        pass

    @abstractmethod
    def get(self, time_from: int = None, time_to: int = None, station_number: int = None) -> list[dict]:
        """Retrieves historical station data based on time range and station ID.

        Args:
            time_from (int, optional): The start of the time range (UTC Unix timestamp).
                If None, retrieves data from the beginning. Defaults to None.
            time_to (int, optional): The end of the time range (UTC Unix timestamp).
                If None, retrieves data up to the latest record. Defaults to None.
            station_number (int, optional): The specific station ID to filter by.
                If None, returns data for all stations. Defaults to None.

        Returns:
            list[dict]: A list of dictionaries containing station data. The structure
            of the list depends on the arguments provided:

            - If `station_number` is None, returns a list of `saving_stations_data`
              snapshots that fall within the specified time range.
              `[{'timestamp': int, 'stations': [...]}, ...]`

            - If `station_number` is not None, returns a list of historical records
              for that specific station within the time range.
              `[{'timestamp': int, 'station': {...}}, ...]`

        Special Cases:
            - If `time_from` and `time_to` are both None, all available data is returned.
            - If `time_from` and `time_to` are both -1, only the single most recent
              data snapshot is returned.
        """
        pass


import threading

class InMemoStationRepository(StationRepository):
    """An in-memory implementation of the StationRepository.

    This implementation is thread-safe.
    """
    def __init__(self, max_size: int = 100_000_000):
        self._data = []
        self._max_size = max_size
        self._lock = threading.Lock()

    def save(self, saving_stations_data: dict):
        with self._lock:
            self._data.append(saving_stations_data)
            if len(self._data) > self._max_size * 1.5:
                self._data = self._data[-self._max_size:]

    def get(self, time_from: int = None, time_to: int = None, station_number: int = None) -> list[dict]:
        with self._lock:
            # Handle special case for latest record
            if time_from == -1 and time_to == -1:
                return self._data[-1:] if self._data else []

            # Filter by time range
            time_filtered_snapshots = self._data
            if time_from is not None:
                time_filtered_snapshots = [
                    s for s in time_filtered_snapshots if s.get('timestamp', 0) >= time_from
                ]
            if time_to is not None:
                time_filtered_snapshots = [
                    s for s in time_filtered_snapshots if s.get('timestamp', 0) <= time_to
                ]

            # If no station number is specified, return the filtered snapshots
            if station_number is None:
                return time_filtered_snapshots

            # If a station number is specified, transform the data structure
            station_history = []
            for snapshot in time_filtered_snapshots:
                for station in snapshot.get('stations', []):
                    if station.get('number') == station_number:
                        station_history.append({
                            'timestamp': snapshot.get('timestamp'),
                            'station': station
                        })
                        break # Move to the next snapshot
            return station_history
        


class SQLStationRepository(StationRepository):
    """
    MySQL implementation of the StationRepository using SQLAlchemy.
    """

    def save(self, data: dict):
        from models import Station, Availability
        try:
         
            station = Station(
                number=data['number'],
                name=data['name'],
                address=data['address'],
                lat=data['position']['lat'],
                lng=data['position']['lng'],
                bike_stands=data['bike_stands'],
                status=data.get('status'),
                banking=data.get('banking'),
                bonus=data.get('bonus')
            )
            db.session.merge(station)
            
         
            db.session.flush() 

          
            new_avail = Availability(
                number=data['number'],
                available_bikes=data.get('available_bikes', 0),
                available_bike_stands=data.get('available_bike_stands', 0),
                status=data.get('status'),
                last_update=data.get('last_update')
            )
            db.session.add(new_avail)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saving station {data.get('number')}: {e}")


    def get(self, time_from=None, time_to=None, station_number=None):
        from models import Station, Availability
        from sqlalchemy import func, select
        if station_number is not None:

            if time_from is None:
                time_from = int((time.time() - 24 * 3600) * 1000)

            query = db.session.query(Availability).filter(
                Availability.number == station_number,
                Availability.last_update >= time_from
            )

            if time_to:
                query = query.filter(Availability.last_update <= time_to)

            results = query.order_by(Availability.last_update.asc()).all()
            
            return [avail.to_dict() for avail in results]


        subq = select(func.max(Availability.id)).group_by(Availability.number)

        query = db.session.query(Station, Availability).outerjoin(
            Availability, Station.number == Availability.number
        ).filter(
            (Availability.id.in_(subq)) | (Availability.id == None)
        )

        results = query.all()
        
        output = []
        for station, avail in results:
            s_dict = station.to_dict()
            if avail:
                s_dict.update(avail.to_dict())
            else:
                s_dict.update({"available_bikes": 0, "available_bike_stands": 0})
            output.append(s_dict)
        
        return output