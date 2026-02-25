from repository.station_repo import StationRepository

class StationService:
    def __init__(self, repo: StationRepository):
        self._repo = repo

    def save_stations(self, data):
        self._repo.save(data)

    def get_all_stations_with_latest_availability(self):
        pass
