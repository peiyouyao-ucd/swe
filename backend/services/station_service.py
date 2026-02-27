from repository.station_repo import StationRepository

class StationService:
    def __init__(self, repo: StationRepository):
        """Initializes the StationService with a data repository.

        Args:
            repo (StationRepository): An implementation of the StationRepository
                used for data persistence.
        """
        self._repo = repo

    def save_station_data(self, raw_stations_data: list[dict]):
        """Transforms and saves station data.

        This method takes the raw data from the scraper, transforms it into the
        `saving_stations_data` format, and persists it using the repository.

        Args:
            raw_stations_data (list[dict]): A list of dictionaries, with each
                dictionary representing a station's raw data from the API.
        """
        saving_stations_data = {} # Transformation logic will be implemented here
        self._repo.save(saving_stations_data)

    def get_latest_all_stations(self) -> dict:
        """Retrieves the latest snapshot of all station data.

        Returns:
            dict: A dictionary conforming to the `saving_stations_data` schema,
                  containing the timestamp and a list of all stations.
        """
        return self._repo.get(time_from=-1, time_to=-1)

    def get_one_station(self, station_number: int, time_from: int = None):
        """Retrieves historical data for a single station.

        Args:
            station_number (int): The ID of the station to retrieve.
            time_from (int, optional): A Unix timestamp to filter records from.
                Defaults to None.

        Returns:
            dict: A dictionary containing the station's historical data.
        """
        return self._repo.get(time_from=time_from, time_to=None, station_number=station_number)

    def predict_for_one_station(self, station_number: int):
        """Predicts future availability for a single station. (Not implemented)

        Args:
            station_number (int): The ID of the station to predict for.
        """
        pass
