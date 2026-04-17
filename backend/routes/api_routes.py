from typing import List, Tuple
import logging

from flask import Blueprint, jsonify, current_app
from services.weather_service import WeatherService
from services.station_service import StationService
from models import Station, Availability, Weather

# Define the blueprint for API endpoints
# These routes return JSON data instead of HTML templates
api_bp = Blueprint('api', __name__)

@api_bp.route('/api/stations')
def get_stations():
    """
    Fetches the latest real-time data for all Dublin Bike stations.
    Retrieves the StationService instance from the global app configuration.

    Response Schema:
    .. List[Tuple[Station, Availability]]
    [
        {
            "number": int,
            "name": str,
            "address": str,
            "lat": float,
            "lng": float,
            "status": str,
            "bike_stands": int,
            "available_bikes": int,
            "available_bike_stands": int,
            "last_update": int (Unix MS)
        },
        ...
    ]
    """
    try:
        station_service: StationService = current_app.config.get('STATION_SERVICE')
        data: List[Tuple[Station, Availability]] = station_service.get_latest_all_stations()
        
        response = []
        for station, avail in data:
            s_dict = station.to_dict()
            if avail:
                s_dict.update(avail.to_dict())
            else:
                s_dict.update({"available_bikes": 0, "available_bike_stands": 0})
            response.append(s_dict)
            
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error fetching stations API: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/stations/<int:station_number>')
def get_station_details(station_number):
    """
    Fetches detailed availability history and forecase for a specific station.
    
    :param station_number: The unique ID of the bike station.
    
    Response Schema:
    {
        "number": int,
        "latest": Availability,
        "prediction": int or "N/A",
        "history": List[Availability],
        "forecast_24h": [
            { "hours_ahead": int, "time_label": "HH:00", "prediction": int },
            ...
        ]
    }
    """
    try:
        station_service: StationService = current_app.config.get('STATION_SERVICE')
        data = station_service.get_one_station_details(station_number)
            
        response = {
            "number": station_number,
            "latest": data['latest'].to_dict() if data['latest'] else {},
            "prediction": data['prediction'],
            "history": [record.to_dict() for record in data['history']],
            "forecast_24h": data['forecast_24h']
        }
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error fetching station {station_number} API: {e}")
        return jsonify({"error": "Data retrieval failed"}), 500

@api_bp.route('/api/weather')
def get_weather():
    """
    Fetches the most recent weather data for Dublin.
    """
    try:
        weather_service: WeatherService = current_app.config.get('WEATHER_SERVICE')

        weather: Weather = weather_service.get_latest_weather_data()
        return jsonify(weather.to_dict() if weather else {})
        
    except Exception as e:
        logging.error(error=e)  
        return jsonify({"error": str(e)}), 500