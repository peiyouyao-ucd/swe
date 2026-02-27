import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import os

from repository.station_repo import InMemoStationRepository
from repository.weather_repo import InMemoWeatherRepository
from services.station_service import StationService
from services.weather_service import WeatherService
from scraper.station_scraper import fetch_and_store_stations
from scraper.weather_scraper import fetch_and_store_weather


# --- Initialization ---
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)
logging.basicConfig(level=logging.INFO)


# --- Repositories ---
station_repo = InMemoStationRepository(max_size=100)
weather_repo = InMemoWeatherRepository(max_size=24)


# --- Services ---
station_service = StationService(station_repo)
weather_service = WeatherService(weather_repo)


# --- Background Scraper Tasks ---
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_store_stations, args=[station_service], trigger="interval", minutes=5)
scheduler.add_job(func=fetch_and_store_weather, args=[weather_service], trigger="interval", hours=1)
scheduler.start()


# --- API Endpoints ---
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/stations')
def stations():
    """Returns all station information along with their latest availability."""
    try:
        data = station_service.get_latest_all_stations()
        return jsonify(data)
    except Exception as e:
        # It's good practice to log the exception here
        return jsonify({"error": "An error occurred fetching station data."}), 500

@app.route('/api/weather')
def weather():
    """Returns the latest available weather data."""
    try:
        data = weather_service.get_latest_weather_data()
        return jsonify(data)
    except Exception as e:
        logging.error(f"An error occurred fetching weather data: {e}")
        return jsonify({"error": "An error occurred fetching weather data."}), 500

@app.route('/api/status')
def status():
    """Returns the running status of the backend."""
    return jsonify({"status": "Backend is running", "version": "0.4.0-weather-integration"})


if __name__ == '__main__':
    # Trigger an initial data fetch for both services on startup
    logging.info("Performing initial data fetch...")
    try:
        fetch_and_store_stations(station_service)
        fetch_and_store_weather(weather_service)
        logging.info("Initial data fetch successful.")
    except Exception as e:
        logging.error(f"An error occurred during initial data fetch: {e}")
    
    # Run the Flask app
    logging.info("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5000)
