from backend.scraper.jcdecaux import fetch_and_store_stations
from backend.scraper.weather import fetch_and_store_weather
from backend.utils.db import get_engine
import sqlalchemy as sqla
import time

def verify_system():
    print("1. Running JCDecaux Scraper...")
    try:
        fetch_and_store_stations()
        print("   -> Success")
    except Exception as e:
        print(f"   -> Failed: {e}")

    print("\n2. Running Weather Scraper...")
    try:
        fetch_and_store_weather()
        print("   -> Success")
    except Exception as e:
        print(f"   -> Failed: {e}")

    print("\n3. Verifying Database Data...")
    engine = get_engine()
    with engine.connect() as conn:
        stations_count = conn.execute(sqla.text("SELECT COUNT(*) FROM stations")).scalar()
        availability_count = conn.execute(sqla.text("SELECT COUNT(*) FROM availability")).scalar()
        weather_count = conn.execute(sqla.text("SELECT COUNT(*) FROM weather")).scalar()
        
        print(f"   -> Stations: {stations_count}")
        print(f"   -> Availability Records: {availability_count}")
        print(f"   -> Weather Records: {weather_count}")

if __name__ == "__main__":
    verify_system()
