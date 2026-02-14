import requests
import json
from pprint import pprint

# --- CONFIGURATION ---
# Please fill in your API keys here
JCD_APIKEY = "52f9ba4359889ed1c9aefe45d17b308f7aa80967"
OWM_APIKEY = "e598ac30c7b447fd32315b33743efbc1"

JCD_CONTRACT_NAME = "dublin"
OWM_CITY = "Dublin,IE"

# --- API ENDPOINTS ---
JCD_URL = "https://api.jcdecaux.com/vls/v1/stations"
OWM_URL = "http://api.openweathermap.org/data/2.5/weather"

def scrape_jcdecaux():
    print("\n--- Exploring JCDecaux Data ---")
    try:
        response = requests.get(JCD_URL, params={"apiKey": JCD_APIKEY, "contract": JCD_CONTRACT_NAME})
        if response.status_code == 200:
            data = response.json()
            print(f"Total stations found: {len(data)}")
            print("Schema of the first station:")
            pprint(data[0])
        else:
            print(f"Error fetching JCDecaux: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection error (JCDecaux): {e}")

def scrape_openweather():
    print("\n--- Exploring OpenWeather Data ---")
    try:
        response = requests.get(OWM_URL, params={"q": OWM_CITY, "appid": OWM_APIKEY, "units": "metric"})
        if response.status_code == 200:
            data = response.json()
            print("Full Weather Data Schema:")
            pprint(data)
        else:
            print(f"Error fetching OpenWeather: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection error (OpenWeather): {e}")

if __name__ == "__main__":
    print("Show API Data Schema")
    print("================================")
    scrape_jcdecaux()
    scrape_openweather()
    print("\nNote: Once you see the schema, we can adjust the database models in 'backend' if needed.")

"""
Show API Data Schema
================================

--- Exploring JCDecaux Data ---
Total stations found: 115
Schema of the first station:
{'address': 'Smithfield North',
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
 'status': 'OPEN'}

--- Exploring OpenWeather Data ---
Full Weather Data Schema:
{'base': 'stations',
 'clouds': {'all': 20},
 'cod': 200,
 'coord': {'lat': 53.344, 'lon': -6.2672},
 'dt': 1771030622,
 'id': 2964574,
 'main': {'feels_like': -5.19,
          'grnd_level': 999,
          'humidity': 83,
          'pressure': 1015,
          'sea_level': 1015,
          'temp': -0.4,
          'temp_max': 1.04,
          'temp_min': -1.9},
 'name': 'Dublin',
 'sys': {'country': 'IE',
         'id': 2091862,
         'sunrise': 1771055154,
         'sunset': 1771090370,
         'type': 2},
 'timezone': 0,
 'visibility': 10000,
 'weather': [{'description': 'few clouds',
              'icon': '02n',
              'id': 801,
              'main': 'Clouds'}],
 'wind': {'deg': 300, 'speed': 4.63}}

Note: Once you see the schema, we can adjust the database models in 'backend' if needed.
"""