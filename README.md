# 1. Project Overview

The **Dublin Bike-Sharing Data & Analytics Platform** is a full-stack web application designed to help users track real-time bike and stand availability across Dublin. It combines real-time data ingestion, historical data persistence, and machine learning to provide predictive insights.

- **Secure Authentication & Profiles**: Integrated Login/Signup system allowing users to create accounts and manage personalized profiles.
- **Comprehensive User Analytics**: Tracks detailed riding statistics including total rides, distance travelled, CO2 saved, and favorite stations.
- **User Subscription System**: Secure multi-tier membership system (Day, Monthly, Annual) featuring real-time database synchronization, dynamic plan locking, and automated expiration tracking.
- **Smart Route Planning**: Integrates Google Maps APIs with a custom Haversine-based algorithm to generate seamless "Walk-Cycle-Walk" multi-leg journeys.
- **Containerized Data Persistence**: Robust MySQL backend managed via **Docker**, ensuring that all user credentials and profile data are securely stored and persistent across sessions.
- **Real-time Monitoring & Prediction**: Integrates JCDecaux and OpenWeather APIs for live status updates and uses a Scikit-learn model for availability forecasting.

# 2. Project structure

```bash
.
├── backend/            # Flask API, Business Logic, and DB utilities
│   ├── db.py           # Database connection and initialization
│   ├── models.py       # SQLAlchemy ORM schemas
│   ├── routes/         # API endpoints and page routing
│   ├── services/       # Business logic (Auth, Predictions, etc.)
│   ├── repository/     # Abstracted data access layer
│   └── scraper/        # Background data collection tasks
├── frontend/           # Presentation layer
│   ├── templates/      # Jinja2 HTML views
│   └── static/         # Frontend assets (CSS, JS, Images)
├── ml_training/        # ML pipeline (data prep, training, and pickles)
├── docker/             # Infrastructure as Code (MySQL init scripts)
├── tests/              # Comprehensive test suites
├── pyproject.toml      # Dependency management via uv
└── docker-compose.yml  # Local environment orchestration
```

# 3. Run book

## Install UV

macOS and Linux

```bash
# Use curl to download the script and execute it with sh:
curl -LsSf https://astral.sh/uv/install.sh | sh

# If your system doesn't have curl, you can use wget:
wget -qO- https://astral.sh/uv/install.sh | sh
```

Windows

```powershell
# Use irm to download the script and execute it with iex:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Python environment / dependencies

Using uv to install dependencies:

```bash
# /swe
uv sync
```

Activate venv:

```bash
# /swe

# MacOS / Linux
source .venv/bin/activate

# Windows
.\.venv\Scripts\activate
```

## Run model training

We need run model training firstly. We can run / generate / get model in 3 ways:

1. Run `ml_training/training.ipynb` which will generate a model file: `ml_training/bike_availability_model.pkl`. This way is suitable to research which model is best in **LOCAL**, with jupyter notebook.
2. Download raw `bike_weather_data.csv` from [here](https://drive.google.com/file/d/1CCBICc9XKv4SjipXQQV3Kbv5Uv6ELTVW/view?usp=drive_link). Place that file under `ml_train/bike_weather_data.csv` and using
    ```bash
    # /swe
    uv run python ml_training/training.py
    ```
    to generate model file, which will take several mins. This way is suitable for **deployment**.
3. Directly download model file [here](https://drive.google.com/file/d/1WpCTOXdx3GmuKOMfMkKZUGRF06H1YG7P/view?usp=drive_link), and place it under `ml_training/bike_availability_model.pkl`. **BUT**, I am not sure this `.pkl` program can run smoothly in EC2, because it is trained under Window WLS environment. So I recommend the deployer use way 2 to generate model file.


We don't upload model file and raw data to Github because of its big size.

Backend application will read that `.pkl` model file when `StationService` is initialized.

## Start database (docker)

Firstly, install docker if you don't have

```bash
# install docker in linux
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
# if you are in Window or MacOS, you can install docker desktop application
```

Start database using docker command:

```bash
# /swe

docker-compose up -d # start container, where is MySQL database running
docker-compose ps # check docker status

# Close docker container, you don't need these commands in deployment
docker-compose down # stop and remove container
docker-compose down -v # stop and remove container, delete data volume
```

## Inject secrets

We need to configure API Keys and URLs then.

Create `backend/.env` with

```txt
# Backend App Config
APP_IP=0.0.0.0
APP_PORT=5000

# Database Configuration
DB_USER=root
DB_PASSWORD=root_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=dublin_bikes

# JCDecaux API Configuration
JCD_APIKEY=52f9ba4359889ed1c9aefe45d17b308f7aa80967
JCD_URL=https://api.jcdecaux.com/vls/v1/stations
JCD_CONTRACT_NAME=dublin

# OpenWeatherMap API Configuration
OWM_APIKEY=e598ac30c7b447fd32315b33743efbc1
OWM_URL=http://api.openweathermap.org/data/2.5/weather
OWM_CITY=Dublin,IE

# Google Maps API Configuration
GOOGLE_MAPS_KEY=AIzaSyAgyAIhr_Smqjx2XN9GAz_O_XEOyNLhn-Q
```

## Run backend

Then, use command to run backend

```bash
# /swe
uv run python backend/app.py
```

## Run tests

```bash
# /swe

# Run all tests using discovery
uv run python -m unittest discover tests

# Or run a specific test file
uv run python tests/services/test_station_service.py
```
