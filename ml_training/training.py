from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle

# Setup paths relative to script location
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "bike_weather_data.csv"
MODEL_PATH = BASE_DIR / "bike_availability_model.pkl"

def generate_model():
    # Load dataset
    if not DATA_PATH.exists():
        return
        
    data = pd.read_csv(DATA_PATH)

    # Data Cleaning & Feature Engineering
    data['available_bikes'] = data['num_bikes_available']
    data['temperature'] = (data['max_air_temperature_celsius'] + data['min_air_temperature_celsius']) / 2
    data['humidity'] = (data['max_relative_humidity_percent'] + data['min_relative_humidity_percent']) / 2
    data['day_of_week'] = pd.to_datetime(data['last_reported']).dt.dayofweek

    features = ['station_id', 'temperature', 'humidity', 'hour', 'day_of_week']
    target = 'available_bikes'

    X = data[features]
    y = data[target]

    # Train the best-performing model (Random Forest) on the entire dataset
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X, y)

    # Save the model artifact
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(rf_model, f)

if __name__ == "__main__":
    generate_model()