# Dublin Bike-Sharing App

Dublin City bike-sharing system visualization and prediction application.

## Project Structure

- `/backend`: Flask application, scrapers, and ML logic.
- `/frontend`: HTML, CSS, and JavaScript files.
- `/docker`: Docker configuration and DB initialization.
- `/code_example`: Original example code from teacher.
- `plan.md`: Project planning document.

## Setup Instructions

### 1. Database (Docker)
Ensure Docker is installed and run:
`docker compose up -d`

### 2. Backend Setup
Navigate to `/backend` and use `uv` to install dependencies:
`uv sync`

Run the development server:
`uv run python app.py`

### 3. Frontend Setup
The frontend is served as static files by the Flask backend or can be opened directly in a browser during UI development.
Navigate to `http://localhost:5000` once the backend is running.
