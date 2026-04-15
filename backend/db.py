# backend/utils/db.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import logging

db = SQLAlchemy()

def init_db(app):
    """
    Initializes the database and tests the connection.
    The DB config is injected to app by
    ```
    app.config.from_object(Config)
    ```
    Then `db.init_app(app)` will automatically read DB config fields,
    like 'DB_USER', and create DB connection.
    """
    db.init_app(app)

    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            logging.info("Database connection successful")
        except Exception as e:
            logging.fatal("Database connection failed", error=e)