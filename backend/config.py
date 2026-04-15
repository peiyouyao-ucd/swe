import requests
import os
from pprint import pprint
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
class Config:
    """Class-based config for Flask"""
    # APP Config
    APP_IP = os.getenv("APP_IP", "0.0.0.0")
    APP_PORT = os.getenv("APP_PORT", "5000")

    # DB Config
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root_password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "dublin_bikes")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI", 
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API Keys and URLs
    JCD_APIKEY = os.getenv("JCD_APIKEY")
    OWM_APIKEY = os.getenv("OWM_APIKEY")
    GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY")

    JCD_CONTRACT_NAME = os.getenv("JCD_CONTRACT_NAME", "dublin")
    OWM_CITY = os.getenv("OWM_CITY", "Dublin,IE")
    JCD_URL = os.getenv("JCD_URL", "https://api.jcdecaux.com/vls/v1/stations")
    OWM_URL = os.getenv("OWM_URL", "http://api.openweathermap.org/data/2.5/weather")

JCD_URL = Config.JCD_URL
JCD_APIKEY = Config.JCD_APIKEY
JCD_CONTRACT_NAME = Config.JCD_CONTRACT_NAME

OWM_URL = Config.OWM_URL
OWM_APIKEY = Config.OWM_APIKEY
OWM_CITY = Config.OWM_CITY

def scrape_jcdecaux():
    print("\n--- Exploring JCDecaux Data ---")
    try:
        response = requests.get(JCD_URL, params={"apiKey": JCD_APIKEY, "contract": JCD_CONTRACT_NAME})
        if response.status_code == 200:
            data = response.json()
            print(f"Total stations found: {len(data)}")
            print("Schema of the first two station:")
            pprint(data[:2])
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
Schema of the first two station:
[{'address': 'Smithfield North',
  'available_bike_stands': 5,
  'available_bikes': 25,
  'banking': False,
  'bike_stands': 30,
  'bonus': False,
  'contract_name': 'dublin',
  'last_update': 1772151439000,
  'name': 'SMITHFIELD NORTH',
  'number': 42,
  'position': {'lat': 53.349562, 'lng': -6.278198},
  'status': 'OPEN'},
 {'address': 'Parnell Square North',
  'available_bike_stands': 11,
  'available_bikes': 9,
  'banking': False,
  'bike_stands': 20,
  'bonus': False,
  'contract_name': 'dublin',
  'last_update': 1772151755000,
  'name': 'PARNELL SQUARE NORTH',
  'number': 30,
  'position': {'lat': 53.3537415547453, 'lng': -6.26530144781526},
  'status': 'OPEN'}]

--- Exploring OpenWeather Data ---
Full Weather Data Schema:
{'base': 'stations',
 'clouds': {'all': 75},
 'cod': 200,
 'coord': {'lat': 53.344, 'lon': -6.2672},
 'dt': 1772151302,
 'id': 2964574,
 'main': {'feels_like': 7.81,
          'grnd_level': 992,
          'humidity': 82,
          'pressure': 1007,
          'sea_level': 1007,
          'temp': 9.69,
          'temp_max': 9.93,
          'temp_min': 9.22},
 'name': 'Dublin',
 'rain': {'1h': 0.65},
 'sys': {'country': 'IE',
         'id': 2031847,
         'sunrise': 1772176671,
         'sunset': 1772215088,
         'type': 2},
 'timezone': 0,
 'visibility': 10000,
 'weather': [{'description': 'light rain',
              'icon': '10n',
              'id': 500,
              'main': 'Rain'}],
 'wind': {'deg': 230, 'speed': 3.6}}

Note: Once you see the schema, we can adjust the database models in 'backend' if needed.
"""