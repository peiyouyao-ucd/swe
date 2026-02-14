from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Station(db.Model):
    __tablename__ = 'stations'
    number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    bike_stands = db.Column(db.Integer)

class Availability(db.Model):
    __tablename__ = 'availability'
    # 使用复合主键或自增ID均可，及格标准建议用自增ID+索引提升写入速度
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer, db.ForeignKey('stations.number'), index=True)
    available_bikes = db.Column(db.Integer)
    available_bike_stands = db.Column(db.Integer)
    last_update = db.Column(db.BigInteger) 
    status = db.Column(db.String(20))

class Weather(db.Model):
    __tablename__ = 'weather'
    dt = db.Column(db.BigInteger, primary_key=True)
    temp = db.Column(db.Float)
    humidity = db.Column(db.Integer)
    wind_speed = db.Column(db.Float)
    description = db.Column(db.String(50))