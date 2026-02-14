from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from backend.services.station_service import get_all_stations, get_station_details
from apscheduler.schedulers.background import BackgroundScheduler
from backend.scraper.jcdecaux import fetch_and_store_stations
from backend.scraper.weather import fetch_and_store_weather
import os
import atexit

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Scheduler for Background Tasks
# In a real production app, consider running this in a separate worker process
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_store_stations, trigger="interval", minutes=5)
scheduler.add_job(func=fetch_and_store_weather, trigger="interval", hours=1)
scheduler.start()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/stations')
def stations():
    try:
        data = get_all_stations()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stations/<int:number>')
def station_detail(number):
    try:
        data = get_station_details(number)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status')
def status():
    return jsonify({"status": "Backend is running", "version": "0.1.0"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
