from db import db
from datetime import datetime 


class User(db.Model):
    """
    User Model for DublinBikes App。
    """
    __tablename__ = 'users'

    
    email = db.Column(db.String(120), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    
    
    member_since = db.Column(db.String(20), default=lambda: datetime.now().strftime('%B %Y'))
    
    
    total_rides = db.Column(db.Integer, default=0)
    total_distance = db.Column(db.Integer, default=0)
    co2_saved = db.Column(db.Integer, default=0)
    rides_this_month = db.Column(db.Integer, default=0)
    fav_station = db.Column(db.String(100), default="None Yet")

    def __repr__(self):
        return f'<User {self.name}>'
    


class Weather(db.Model):
    """Model for storing weather snapshots."""
    __tablename__ = 'weather'
    dt = db.Column(db.BigInteger, primary_key=True)
    temp = db.Column(db.Float)
    feels_like = db.Column(db.Float)
    temp_min = db.Column(db.Float)
    temp_max = db.Column(db.Float)
    visibility = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    wind_speed = db.Column(db.Float)
    precipitation = db.Column(db.Float, default=0.0)
    description = db.Column(db.String(100))
    main = db.Column(db.String(50))

    def to_dict(self):
        """Converts model instance to a dictionary for JSON responses."""
        return {
            "dt": self.dt,
            "temp": self.temp,
            "feels_like": self.feels_like,
            "temp_min": self.temp_min,
            "temp_max": self.temp_max,
            "visibility": self.visibility,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "precipitation": self.precipitation,
            "weather_description": self.description,
            "weather_main": self.main
        }

# --- Existing Station model remains the same ---
class Station(db.Model):
    __tablename__ = 'stations'
    number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    bike_stands = db.Column(db.Integer)
    status = db.Column(db.String(50))
    banking = db.Column(db.Boolean)
    bonus = db.Column(db.Boolean)

    def to_dict(self):
       
        return {
            "number": self.number,
            "name": self.name,
            "address": self.address,
            "lat": self.lat,               
            "lng": self.lng,             
            "bike_stands": self.bike_stands,
            "status": self.status,
            "banking": self.banking,
            "bonus": self.bonus
        }


class Availability(db.Model):
    __tablename__ = 'availability'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer, db.ForeignKey('stations.number'), nullable=False)
    available_bikes = db.Column(db.Integer)
    available_bike_stands = db.Column(db.Integer)
    status = db.Column(db.String(20))
    last_update = db.Column(db.BigInteger)

    def to_dict(self):
        return {
            "available_bikes": self.available_bikes,
            "available_bike_stands": self.available_bike_stands,
            "status": self.status,
            "last_update": self.last_update
        }