import pandas as pd
import numpy as np
import os

# Generate 1000 rows of dummy data
num_rows = 1000
np.random.seed(42)

# Features: station_id, temperature, humidity, wind_speed, precipitation, hour, day_of_week
data = {
    'station_id': np.random.randint(1, 100, num_rows),
    'temperature': np.random.uniform(0, 35, num_rows),
    'humidity': np.random.uniform(30, 90, num_rows),
    'wind_speed': np.random.uniform(0, 20, num_rows),
    'precipitation': np.random.choice([0, 0, 0, 0, 1.0, 5.0], num_rows), # Mostly 0
    'hour': np.random.randint(0, 24, num_rows),
    'day_of_week': np.random.randint(0, 7, num_rows),
}

# Target: available_bikes (simple linear combination with some noise)
# Bikes decrease with temperature (people ride more), decrease with rain (people ride less), etc.
data['available_bikes'] = (
    20 + 
    -0.2 * data['temperature'] + 
    0.1 * data['humidity'] + 
    1.5 * data['precipitation'] + # More bikes left when it rains
    5 * np.sin(data['hour'] * np.pi / 12) + # Temporal pattern
    np.random.normal(0, 5, num_rows)
).clip(0, 40).astype(int)

df = pd.DataFrame(data)
output_path = 'bike_weather_data.csv'
df.to_csv(output_path, index=False)
print(f"Dummy data saved to {output_path}")
