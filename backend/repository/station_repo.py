from abc import ABC, abstractmethod
from collections import deque

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


# TODO: implement the InMemoStationRepository here