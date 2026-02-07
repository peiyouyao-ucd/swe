## 1. Project Overview

The goal is to build a web application for the Dublin bike-sharing system. The app will show real-time bike availability and predict future occupancy using Machine Learning.

## 2. System Architecture

- **Separated Frontend and Backend**: Use a REST API to connect the two.
- **Backend Structure**: A **Monolithic** app (all-in-one).
  - The **Scraper** and **ML Predictor** will run as internal functions/tasks within the Flask process.
  - **No independent services**: This avoids complex network calls and saves deployment time.
- **Tech Stack**: Python, Flask, MySQL, and **UV** for fast dependency management.

## 3. Frontend (Client Side)

- **Tools**: HTML5, CSS, and JavaScript (with **JQuery** for easier DOM/AJAX).
- **Google Maps JavaScript API**:
  - Embed a map to show all bike stations.
  - Use **Markers** to show station locations.
  - Use **Info Windows** to show real-time bike counts when a user clicks a station.
- **Data Visualization**: Use a library like **Chart.js** to draw occupancy charts (hourly/daily).

## 4. Backend Services

### `BikeStationService`

- **`fetch_and_store_bike_info()`**:
  - A scheduled task running every **5 minutes**.
  - Scrapes real-time station data from the **JCDecaux API** and saves it to MySQL.
- **`get_all_bike_station_briefs()`**:
  - Returns basic data (ID, name, lat, lng, current bikes) for all stations to show on the map.
- **`get_one_bike_station_detail()`**:
  - Returns historical trends for a specific station so the frontend can draw charts.
- **`predict_for_one_bike_station()`**:
  - **Training**: We will train a model using the `.csv` file provided by the course.
  - **Usage**: Save the model as a `.pkl` file. The Flask app loads this file into memory and makes predictions when called.

### `WeatherService`

- **`fetch_and_store_weather_info()`**:
  - A scheduled task running every **1 hour**.
  - Scrapes current weather and forecasts from **OpenWeather**.
- **`get_weather()`**:
  - Provides Dublin's current weather data for the frontend header.

### `UserService` (Additional Feature)

- **`register()`** & **`login()`**:
  - Acts as a "gatekeeper". Guest users can view the map, but only logged-in users can use the **Predict** function.
- **`delete_account()`**:
  - Basic account management.
- **Note**: Do **NOT** use personal info (student/worker) to "enhance" predictions. The school's training data doesn't have these categories, so it won't work.