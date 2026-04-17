from flask import Blueprint, jsonify, current_app
import logging

# Define the blueprint for API endpoints
# These routes return JSON data instead of HTML templates
api_bp = Blueprint('api', __name__)

@api_bp.route('/api/stations')
def get_stations():
    """
    Fetches the latest real-time data for all Dublin Bike stations.
    Retrieves the StationService instance from the global app configuration.

    Response Schema:
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
        station_service = current_app.config.get('STATION_SERVICE')
        if not station_service:
            return jsonify({"error": "Station service unavailable"}), 500

        data = station_service.get_latest_all_stations()
        
        # Serialization: Convert Models/Tuples to dicts
        output = []
        for station, avail in data:
            s_dict = station.to_dict()
            if avail:
                s_dict.update(avail.to_dict())
            else:
                s_dict.update({"available_bikes": 0, "available_bike_stands": 0})
            output.append(s_dict)
            
        return jsonify(output)
    except Exception as e:
        logging.error(f"Error fetching stations API: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/stations/<int:station_number>')
def get_station_details(station_number):
    """
    Fetches detailed information and history for a specific station.
    
    :param station_number: The unique ID of the bike station.
    
    Response Schema:
    {
        "number": int,
        "metadata": { 
            "number": int, "name": str, "address": str, "lat": float, "lng": float, "bike_stands": int, "status": str, "banking": bool, "bonus": bool
        },
        "latest": { 
            "available_bikes": int, "available_bike_stands": int, "status": str, "last_update": int
        },
        "prediction": int or "N/A",
        "history": [
            { "last_update": int (Unix MS), "available_bikes": int, ... },
            ...
        ],
        "forecast_24h": [
            { "hours_ahead": int, "time_label": "HH:00", "prediction": int },
            ...
        ]
    }
    """
    try:
        station_service = current_app.config.get('STATION_SERVICE')
        data = station_service.get_one_station(station_number)
        
        if not data:
            return jsonify({"error": f"Station {station_number} not found"}), 404
            
        # Serialization: Convert Model instances within the result dict
        result = {
            "number": station_number,
            "metadata": data['metadata'].to_dict() if data['metadata'] else {},
            "latest": data['latest'].to_dict() if data['latest'] else {},
            "prediction": data['prediction'],
            "history": [record.to_dict() for record in data['history']],
            "forecast_24h": data['forecast_24h']
        }
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error fetching station {station_number} API: {e}")
        return jsonify({"error": "Data retrieval failed"}), 500

@api_bp.route('/api/weather')
def get_weather():
    """
    Fetches the most recent weather data for Dublin.
    Uses the WeatherService to bridge the Gap between the scraper and the UI.
    """
    try:
        weather_service = current_app.config.get('WEATHER_SERVICE')
        if not weather_service:
            return jsonify({"error": "Weather service unavailable"}), 500

        # Retrieve the latest processed weather model
        weather = weather_service.get_latest_weather_data()
        return jsonify(weather.to_dict() if weather else {})
        
    except Exception as e:
        logging.error(f"DEBUG ERROR: {e}")  
        return jsonify({"error": str(e)}), 500