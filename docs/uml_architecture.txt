@startuml
title Dublin Bikes Platform - Architecture Diagram

skinparam componentStyle rectangle
skinparam backgroundColor white
skinparam component {
  BackgroundColor #DDEEFF
  BorderColor #2E75B6
  FontColor #1F4E79
}
skinparam database {
  BackgroundColor #E1F5EE
  BorderColor #0F6E56
}
skinparam cloud {
  BackgroundColor #FFF8E7
  BorderColor #BA7517
}
skinparam node {
  BackgroundColor #F5F5F5
  BorderColor #888780
}

' =====================
' EXTERNAL APIS
' =====================

cloud "JCDecaux API\n(stations, availability)" as JCD
cloud "OpenWeatherMap API\n(current weather)" as OWM
cloud "Google Maps JS API\n(map, directions)" as GMAPS

' =====================
' AWS EC2 INSTANCE
' =====================

node "AWS EC2 Instance" {

  component "APScheduler\n(background jobs)" as SCHED {
    component "Station Scraper\n(every 5 min)" as STNSCRAPER
    component "Weather Scraper\n(every 1 hr)" as WTRSCRAPER
    component "Plan Expiry Check\n(every 1 hr)" as EXPIRY
  }

  component "Flask Application" as FLASK {

    component "auth_routes Blueprint\n/signup, /login, /logout\n/api/subscribe, /api/renew" as AUTHRTS

    component "api_routes Blueprint\nGET /api/stations\nGET /api/stations/<id>\nGET /api/weather" as APIRTS

    component "page_routes Blueprint\n/, /about, /profile\n/subscription, /howto" as PGERTS

    component "StationService\n- save_station_data()\n- get_latest_all_stations()\n- get_one_station_details()\n- _predict_for_one_station()\n- _get_24h_forecast()" as STNSVC

    component "WeatherService\n- save_from_raw_weather_data()\n- get_latest_weather_data()" as WTRSVC

    component "AuthService\n- register_user()\n- authenticate_user()\n- check_and_clear_expired_plans()" as AUTHSVC

    component "SQLStationRepository\n- save_stations()\n- save_availabilities()\n- get_stations_latest()\n- get_history()" as STNREPO

    component "SQLWeatherRepository\n- save()\n- get()" as WTRREPO

    component "ML Model\nbike_availability_model.pkl\n(Random Forest Regressor)" as ML
  }

  component "Frontend Layer" as FRONT {
    component "Jinja2 Templates\n(index, profile, subscription\nhowto, login, signup, about)" as TMPL
    component "Static Assets\n(app.js, styles.css)" as STATIC
  }

  database "MySQL 8\n(Docker Container)" as MYSQL {
    component "stations" as TBLSTN
    component "availability" as TBLAVAIL
    component "weather" as TBLWTR
    component "users" as TBLUSR
  }
}

' =====================
' CLIENT BROWSER
' =====================

node "Client Browser" as BROWSER {
  component "Google Maps\n(interactive map)" as MAPUI
  component "Chart.js\n(24h forecast chart)" as CHARTUI
  component "jQuery / AJAX\n(API polling)" as JSUI
}

' =====================
' CONNECTIONS
' =====================

JCD --> STNSCRAPER : HTTP GET (every 5 min)
OWM --> WTRSCRAPER : HTTP GET (every 1 hr)

STNSCRAPER --> STNSVC : raw station data
WTRSCRAPER --> WTRSVC : raw weather data
EXPIRY --> AUTHSVC : trigger expiry check

STNSVC --> STNREPO
WTRSVC --> WTRREPO
STNSVC --> ML : predict(features)
STNSVC --> WTRSVC : get current weather

STNREPO --> TBLSTN
STNREPO --> TBLAVAIL
WTRREPO --> TBLWTR
AUTHSVC --> TBLUSR

APIRTS --> STNSVC
APIRTS --> WTRSVC
AUTHRTS --> AUTHSVC
PGERTS --> TMPL

TMPL --> BROWSER : HTML (server-rendered)
STATIC --> BROWSER : JS / CSS

BROWSER --> APIRTS : AJAX GET /api/stations
BROWSER --> APIRTS : AJAX GET /api/stations/<id>
BROWSER --> APIRTS : AJAX GET /api/weather
BROWSER --> AUTHRTS : POST /login, /signup
GMAPS --> MAPUI : Maps JS API

@enduml
