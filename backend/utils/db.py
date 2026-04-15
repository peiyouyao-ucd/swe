# backend/utils/db.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text 

db = SQLAlchemy()

def init_db(app):
    """Initializes the database and tests the connection."""
    db.init_app(app)

    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            print("Database connection successful!")
        except Exception as e:
            print(f"Database connection failed: {e}")