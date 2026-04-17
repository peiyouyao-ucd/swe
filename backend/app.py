import logging
from flask import Flask, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

# --- Core Configuration & Database Imports ---
from db import init_db, db
from config import Config


# --- Blueprint Imports (Organized Routes) ---
from routes.auth_routes import auth_bp
from routes.page_routes import pages_bp
from routes.api_routes import api_bp

# --- Repository & Service Imports ---
from repository.station_repo import SQLStationRepository
from repository.weather_repo import SQLWeatherRepository
from services.station_service import StationService
from services.weather_service import WeatherService
from services.auth_service import AuthService
from scraper.station_scraper import fetch_and_store_stations
from scraper.weather_scraper import fetch_and_store_weather

# --- APP Init ---
app = Flask(__name__, 
            static_folder='../frontend/static', 
            template_folder='../frontend/templates')

# Load settings from Config class
app.config.from_object(Config)

# Enable Cross-Origin Resource Sharing and basic logging
CORS(app)
logging.basicConfig(level=logging.INFO)

# Initialize and test the database connection
init_db(app)

with app.app_context():
    db.create_all()

# --- Repository & Service Setup ---
#station_repo = InMemoStationRepository(max_size=100)
station_repo = SQLStationRepository()
#weather_repo = InMemoWeatherRepository(max_size=24)
weather_repo = SQLWeatherRepository()

# Initialize Services with their respective dependencies
# Note: StationService requires weather_service for logic processing
weather_service = WeatherService(weather_repo)
station_service = StationService(station_repo, weather_service)
auth_service = AuthService()

# Store service instances in app.config so they are accessible
app.config['STATION_SERVICE'] = station_service
app.config['WEATHER_SERVICE'] = weather_service

# --- Background Scheduler Setup ---
# Schedule scrapers to run automatically in the background
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_store_stations, args=[station_service], trigger="interval", minutes=5)
scheduler.add_job(func=fetch_and_store_weather, args=[weather_service], trigger="interval", hours=1)
scheduler.add_job(func=auth_service.check_and_clear_expired_plans, trigger="interval", hours=1)
scheduler.start()

# --- Blueprint Registration ---
# Connect organized route files to the main application
app.register_blueprint(auth_bp)
app.register_blueprint(pages_bp)
app.register_blueprint(api_bp)

# --- Global Template Context ---
@app.context_processor
def inject_user_status():
    """
    Makes 'user_name' globally available to all HTML templates.
    Used for displaying personalized greetings in the navigation bar.
    """
    user_name = request.cookies.get('user_name')
    return dict(user_name=user_name)

# --- Execution Entry Point ---
if __name__ == '__main__':
    logging.info("Initializing system: checking database and performing initial fetch...")
    
    with app.app_context():
        try:
            fetch_and_store_stations(station_service)
            fetch_and_store_weather(weather_service)
            logging.info("Initial data fetch completed successfully.")
        except Exception as e:
            logging.error(f"Error during initial data fetch: {e}")

    # Start the Flask development server
    logging.info("Starting Dublin Bikes Modular Backend on http://0.0.0.0:5000")
    app.run(debug=True, host=Config.APP_IP, port=Config.APP_PORT)