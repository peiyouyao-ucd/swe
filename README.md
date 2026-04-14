# 1. Project overview

# 2. Project structure

# 3. Run book

## 3.0 Install UV

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

## 3.1 Python environment / dependencies

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

## 3.2 Run model training

We need run model training firstly.

Run `ml_training/training.ipynb` which will generate a model file: `ml_training/bike_availability_model.pkl` 

We don't upload this model file to Github because of its big size.

Backend application will read that `.pkl` model file when `StationService` is initialized.

## 3.3 Inject secrets

We need to configure API Keys and URLs then.

Create `backend/.env` with

```txt
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

# Database Configuration
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:root_password@localhost:3306/dublin_bikes
```

## 3.4 Run backend

Then, use command to run backend

```bash
# /swe
uv run python backend/app.py
```

## 3.5 Run tests

```bash
# /swe

# Run all tests using discovery
uv run python -m unittest discover tests

# Or run a specific test file
uv run python tests/services/test_station_service.py
```
