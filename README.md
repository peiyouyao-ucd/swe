# 1. Project overview

The **Dublin Bike-Sharing Data & Analytics Platform** is a full-stack web application designed to help users track real-time bike and stand availability across Dublin. It combines real-time data ingestion, historical data persistence, and machine learning to provide predictive insights.

**Key Features:**
- **Real-time Monitoring**: Integrates JCDecaux and OpenWeather APIs for live bike and weather status.
- **Predictive Analytics**: Uses a Scikit-learn model to predict availability based on time-series data and weather conditions.
- **Automated Ingestion**: Background scrapers periodically fetch and store data for analysis.
- **Persistent Storage**: Robust MySQL backend managed via Docker for reliable data history.

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

We need run model training firstly.

Run `ml_training/training.ipynb` which will generate a model file: `ml_training/bike_availability_model.pkl` 

We don't upload this model file to Github because of its big size.

Backend application will read that `.pkl` model file when `StationService` is initialized.

## Start database (docker)

Start database using docker command:

```bash
# install docker in linux
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
# if you are in Window or MacOS, you can install docker desktop application

# /swe

docker-compose up -d # start container

docker-compose ps # check docker status

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
