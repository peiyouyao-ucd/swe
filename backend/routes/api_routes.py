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
    """
    try:
        # Access the pre-initialized service from current_app config
        station_service = current_app.config.get('STATION_SERVICE')
        
        if not station_service:
            logging.error("StationService not found in app config.")
            return jsonify({"error": "Station service unavailable"}), 500

        # Retrieve processed station data (e.g., from cache or repository)
        data = station_service.get_latest_all_stations()
        return jsonify(data)
        
    except Exception as e:
        logging.error(f"Error fetching stations API: {e}")
        return jsonify({"error": "Internal server error while fetching station data"}), 500

@api_bp.route('/api/stations/<int:station_number>')
def get_station_details(station_number):
    """
    Fetches detailed information or historical data for a specific station.
    :param station_number: The unique ID of the bike station.
    """
    try:
        station_service = current_app.config.get('STATION_SERVICE')
        data = station_service.get_one_station(station_number)
        
        if not data:
            return jsonify({"error": f"Station {station_number} not found"}), 404
            
        return jsonify(data)
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
            logging.error("WeatherService not found in app config.")
            return jsonify({"error": "Weather service unavailable"}), 500

        # Retrieve the latest processed weather snapshot
        data = weather_service.get_latest_weather_data()
        return jsonify(data)
        
    except Exception as e:
        print(f"DEBUG ERROR: {e}")  
        return jsonify({"error": str(e)}), 500