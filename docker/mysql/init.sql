-- Schema for weather data (Time-series)
CREATE TABLE IF NOT EXISTS weather (
    dt BIGINT PRIMARY KEY,                        -- 10-digit UTC Unix timestamp
    temp FLOAT,                                   -- Current temperature in Celsius
    feels_like FLOAT,                             -- Human-perceived temperature
    temp_min FLOAT,                               -- Minimum temperature at the moment
    temp_max FLOAT,                               -- Maximum temperature at the moment
    visibility INT,                               -- Average visibility in meters
    humidity INT,                                 -- Humidity percentage (%)
    wind_speed FLOAT,                             -- Wind speed in meters per second
    precipitation FLOAT DEFAULT 0,                -- Rain volume for the last 1h/3h (mm)
    description VARCHAR(100),                     -- Weather condition description
    main VARCHAR(50),                             -- Group of weather parameters (Rain, Snow, etc.)
    scrape_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
) COMMENT='Stores historical weather data for ML analysis';

-- Schema for bike stations (Static/Dynamic status)
CREATE TABLE IF NOT EXISTS stations (
    number INT PRIMARY KEY,                       -- Unique station identifier
    name VARCHAR(255) NOT NULL,                   -- Station name
    address VARCHAR(255),                         -- Street address
    lat DOUBLE NOT NULL,                          -- Latitude coordinate
    lng DOUBLE NOT NULL,                          -- Longitude coordinate
    bike_stands INT,                              -- Total number of bike docks
    status VARCHAR(50),                           -- Operational status (OPEN/CLOSED)
    banking BOOLEAN,                              -- Presence of payment terminal
    bonus BOOLEAN,                                -- Whether the station is a bonus station
    CONSTRAINT uc_station_number UNIQUE (number)
) COMMENT='Stores bike station metadata and current status';

-- User accounts and profiles 
CREATE TABLE IF NOT EXISTS users ( 
    email VARCHAR(120) PRIMARY KEY, 
    name VARCHAR(80) NOT NULL, 
    password VARCHAR(80) NOT NULL, 
    member_since VARCHAR(20), 
    total_rides INT DEFAULT 0, 
    total_distance INT DEFAULT 0, 
    co2_saved INT DEFAULT 0, 
    rides_this_month INT DEFAULT 0, 
    fav_station VARCHAR(100) DEFAULT "None Yet" 
) COMMENT="Stores user profile and statistics";

-- Availability table to store dynamic history
CREATE TABLE IF NOT EXISTS availability (
    id INT AUTO_INCREMENT PRIMARY KEY,            -- Internal record ID
    number INT NOT NULL,                          -- Foreign key referencing stations(number) 
    available_bikes INT,                          -- Number of bikes available at the time of scraping [cite: 3494]
    available_bike_stands INT,                    -- Number of free docks at the time of scraping [cite: 3781]
    status VARCHAR(20),                           -- Station status (e.g., 'OPEN')
    last_update BIGINT,                           -- 13-digit timestamp (ms) from JCDecaux [cite: 5225]
    scrape_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Time when the data was saved to our DB
    FOREIGN KEY (number) REFERENCES stations(number)
) COMMENT='Stores time-series data of bike availability for ML training and charts';
