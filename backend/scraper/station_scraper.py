import requests
from config import JCD_URL, JCD_APIKEY, JCD_CONTRACT_NAME

def fetch_and_store_stations(station_service):
    """
    Fetch and Store real-time station data from JCDecaux
    
    ** Fetching Data Schema **
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
    
    The length of the list is around 115
    """
    # TODO: 调整以下逻辑, 修正方法名, 使用log记录日志
    try:
        response = requests.get(JCD_URL, params={"apiKey": JCD_APIKEY, "contract": JCD_CONTRACT_NAME})
        if response.status_code == 200:
            data = response.json()
            station_service.save_station_data(data)
            print(f"Successfully scraped {len(data)} stations.")
        else:
            print(f"Failed to fetch station data: {response.status_code}")
    except Exception as e:
        print(f"Error in station scraper: {e}")
