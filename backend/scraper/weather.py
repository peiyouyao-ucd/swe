import requests
from backend.utils.db import get_engine
import sqlalchemy as sqla
from datetime import datetime

from backend.config import OWM_APIKEY, OWM_CITY, OWM_URL

def fetch_and_store_weather():
    """Fetches current weather and stores it."""
    try:
        response = requests.get(OWM_URL, params={"q": OWM_CITY, "appid": OWM_APIKEY, "units": "metric"})
        if response.status_code == 200:
            data = response.json()
            engine = get_engine()
            
            with engine.connect() as conn:
                conn.execute(sqla.text("""
                    INSERT INTO weather (dt, temp, humidity, wind_speed, description, main)
                    VALUES (:dt, :temp, :humidity, :wind_speed, :description, :main)
                """), {
                    "dt": data['dt'],
                    "temp": data['main']['temp'],
                    "humidity": data['main']['humidity'],
                    "wind_speed": data['wind']['speed'],
                    "description": data['weather'][0]['description'],
                    "main": data['weather'][0]['main']
                })
            print("Successfully updated weather data.")
        else:
            print(f"Failed to fetch weather: {response.status_code}")
    except Exception as e:
        print(f"Error in weather scraper: {e}")
