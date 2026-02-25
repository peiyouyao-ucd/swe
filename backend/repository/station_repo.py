from abc import ABC, abstractmethod
from collections import deque

class StationRepository(ABC):
    @abstractmethod
    def save(self, data):
        """
        Save bike station data in json / string / python dict format
        The bike station data at time `t` would be a list
        It is better to label every list with a timestamp `t`
        ** Example station data **
        [
            {
                'address': 'Smithfield North',
                'available_bike_stands': 20,
                'available_bikes': 10,
                'banking': False,
                'bike_stands': 30,
                'bonus': False,
                'contract_name': 'dublin',
                'last_update': 1771030596000,
                'name': 'SMITHFIELD NORTH',
                'number': 42,
                'position': {'lat': 53.349562, 'lng': -6.278198},
                'status': 'OPEN'
            },
            ...
        ]
        """
        pass

    @abstractmethod
    def get(self, time_from, time_to, station_number):
        """
        Get station data in range of `time_from` to `time_to`, both inclusive
        If `time_to` == None, return the data from `time_from` to last piece
        If `time_from` == None, return the data from first piece to `time_to`
        If they are both None, return the last piece
        If station_number != None, return the data for the specific station with filter logic about time
        """
        pass


# TODO: implement the InMemoStationRepository here