-- 1. Create the Stations table to store static information
CREATE TABLE IF NOT EXISTS stations (
    number INT PRIMARY KEY,                       -- Unique station identifier from JCDecaux 
    name VARCHAR(255) NOT NULL,                   -- Station name (e.g., 'SMITHFIELD NORTH')
    address VARCHAR(255),                         -- Street address
    lat DOUBLE NOT NULL,                          -- Latitude for Google Maps markers [cite: 3459, 3702]
    lng DOUBLE NOT NULL,                          -- Longitude for Google Maps markers [cite: 3459, 3702]
    bike_stands INT,                              -- Total number of bike docks at the station
    CONSTRAINT uc_station_number UNIQUE (number)
) COMMENT='Stores static information about bike stations';

-- 2. Create the Availability table to store dynamic history
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

-- 3. Create the Weather table to store Dublin weather data
CREATE TABLE IF NOT EXISTS weather (
    dt BIGINT PRIMARY KEY,                        -- 10-digit unix timestamp (seconds) from OpenWeather [cite: 5225]
    temp FLOAT,                                   -- Current temperature in Celsius [cite: 3970]
    humidity INT,                                 -- Humidity percentage
    wind_speed FLOAT,                             -- Wind speed in meters per second
    description VARCHAR(100),                     -- Short description (e.g., 'broken clouds') [cite: 3971]
    main VARCHAR(50),                             -- Main weather category (e.g., 'Clouds')
    scrape_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Internal record creation time
) COMMENT='Stores hourly weather data for Dublin to be used as ML features';
