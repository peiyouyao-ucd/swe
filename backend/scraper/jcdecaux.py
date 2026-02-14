import requests
import time
from backend.utils.db import get_engine
import sqlalchemy as sqla

# API Details
from backend.config import JCD_APIKEY, JCD_CONTRACT_NAME, JCD_URL
from backend.models.model import Station, Availability
import traceback

def fetch_and_store_stations():
    """Fetches real-time data from JCDecaux and stores it in the database."""
    try:
        response = requests.get(JCD_URL, params={"apiKey": JCD_APIKEY, "contract": JCD_CONTRACT_NAME})
        if response.status_code == 200:
            data = response.json()
            engine = get_engine()
            
            with engine.connect() as conn:
                for station in data:
                    # Update station static info
                    conn.execute(sqla.text("""
                        INSERT INTO stations (number, name, address, lat, lng, bike_stands)
                        VALUES (:number, :name, :address, :lat, :lng, :bike_stands)
                        ON DUPLICATE KEY UPDATE name=VALUES(name)
                    """), {
                        "number": station['number'],
                        "name": station['name'],
                        "address": station['address'],
                        "lat": station['position']['lat'],
                        "lng": station['position']['lng'],
                        "bike_stands": station['bike_stands']
                    })

                    # Insert availability snapshot
                    conn.execute(sqla.text("""
                        INSERT INTO availability (number, available_bikes, available_bike_stands, status, last_update)
                        VALUES (:number, :bikes, :stands, :status, :last_update)
                    """), {
                        "number": station['number'],
                        "bikes": station['available_bikes'],
                        "stands": station['available_bike_stands'],
                        "status": station['status'],
                        "last_update": station['last_update']
                    })
            print(f"Successfully updated {len(data)} stations.")
        else:
            print(f"Failed to fetch data: {response.status_code}")
    except Exception as e:
        print(f"Error in scraper: {e}")
