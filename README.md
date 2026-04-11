# 1. Project overview

    testing github branch

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
source .venv/bin/activate
```

## 3.2 Run backend

```bash
# /swe
uv run python backend/app.py
```

## 3.3 Run model training

Training the model involves generating/collecting data, running the trainer, and copying the model to the backend:

```bash
# /swe

# 1. Generate dummy data (if you don't have CSV yet)
uv run python ml_training/generate_dummy_data.py

# 2. Run the training script
uv run python "ml_training/0. linear_regression.py"

# 3. Inject the trained model to the backend
cp ml_training/bike_availability_model.pkl backend/services/
```

## 3.4 Run tests

```bash
# /swe

# Run all tests using discovery
uv run python -m unittest discover tests

# Or run a specific test file
uv run python tests/services/test_station_service.py
```
