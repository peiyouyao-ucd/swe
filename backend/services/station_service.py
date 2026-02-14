from backend.utils.db import get_engine
import sqlalchemy as sqla
import json

def get_all_stations():
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(sqla.text("""
            SELECT s.number, s.name, s.address, s.lat, s.lng, s.bike_stands, 
                   a.available_bikes, a.available_bike_stands, a.status, a.last_update
            FROM stations s
            JOIN (
                SELECT number, available_bikes, available_bike_stands, status, last_update
                FROM availability
                WHERE id IN (
                    SELECT MAX(id) 
                    FROM availability 
                    GROUP BY number
                )
            ) a ON s.number = a.number
        """))
        stations = [dict(row) for row in result]
    return stations

def get_station_details(station_number):
    engine = get_engine()
    with engine.connect() as conn:
        # Get historical availability for chart
        history = conn.execute(sqla.text("""
            SELECT available_bikes, last_update
            FROM availability
            WHERE number = :number
            ORDER BY last_update DESC
            LIMIT 24
        """), {"number": station_number})
        
        return [dict(row) for row in history]
