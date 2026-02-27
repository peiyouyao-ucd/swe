import requests
import logging
from config import JCD_URL, JCD_APIKEY, JCD_CONTRACT_NAME
from services.station_service import StationService

def fetch_and_store_stations(station_service: StationService):
    """Fetches real-time station data from JCDecaux and stores it via the StationService.

    This function retrieves the current status of all bike stations and passes the raw
    data to the service layer for processing and storage.

    Args:
        station_service (StationService): The service responsible for handling station data.

    The `raw_stations_data` fetched from the API is a list of dictionaries, where
    each dictionary represents a station:
    .. code-block:: python

        [
            {
                'address': str,
                'available_bike_stands': int,
                'available_bikes': int,
                'banking': bool,
                'bike_stands': int,
                'bonus': bool,
                'contract_name': str,
                'last_update': int,  # Unix timestamp in milliseconds
                'name': str,
                'number': int,       # Station ID
                'position': {'lat': float, 'lng': float},
                'status': str,       # e.g., 'OPEN'
            },
            ...
        ]
    """
    try:
        response = requests.get(JCD_URL, params={"apiKey": JCD_APIKEY, "contract": JCD_CONTRACT_NAME})
        if response.status_code == 200:
            data = response.json()
            station_service.save_station_data(data)
            logging.info(f"Successfully scraped {len(data)} stations.")
        else:
            logging.error(f"Failed to fetch station data: {response.status_code}")
    except Exception as e:
        logging.error(f"Error in station scraper: {e}")
