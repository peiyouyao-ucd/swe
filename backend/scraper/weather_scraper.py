from config import OWM_URL, OWM_APIKEY, OWM_CITY
from services.weather_service import WeatherService
import requests
import logging


def fetch_and_store_weather(weather_service: WeatherService):
    """Fetches raw weather data from the OpenWeatherMap API and triggers the storage process.

    This function sends a request to the OWM API to get the current weather
    for a configured city. If the request is successful, it calls the
    weather service to handle the processing and saving of the data.

    Args:
        weather_service (WeatherService): An instance of the weather service
            that will handle the data.

    The raw_weather_data fetched from the API has the following structure:
    .. code-block:: python

        {
            'base': 'stations',
            'clouds': {'all': 20},
            'cod': 200,
            'coord': {'lat': 53.344, 'lon': -6.2672},
            'dt': 1771030622,
            'id': 2964574,
            'main': {
                'feels_like': -5.19,
                'grnd_level': 999,
                'humidity': 83,
                'pressure': 1015,
                'sea_level': 1015,
                'temp': -0.4,
                'temp_max': 1.04,
                'temp_min': -1.9
            },
            'name': 'Dublin',
            'sys': {
                'country': 'IE',
                'id': 2091862,
                'sunrise': 1771055154,
                'sunset': 1771090370,
                'type': 2
            },
            'timezone': 0,
            'visibility': 10000,
            'weather': [{
                'description': 'few clouds',
                'icon': '02n',
                'id': 801,
                'main': 'Clouds'
            }],
            'wind': {'deg': 300, 'speed': 4.63}
        }
    """
    try:
        response = requests.get(OWM_URL, params={
            "q": OWM_CITY, 
            "appid": OWM_APIKEY, 
            "units": "metric"
        })

        if response.status_code == 200:
            raw_weather_data = response.json()


            rain_data = raw_weather_data.get('rain', {})
            precipitation = rain_data.get('1h', rain_data.get('3h', 0))
            main_data = raw_weather_data.get('main', {})
            
            raw_weather_data['temp'] = main_data.get('temp')
            raw_weather_data['feels_like'] = main_data.get('feels_like')
            raw_weather_data['temp_min'] = main_data.get('temp_min')
            raw_weather_data['temp_max'] = main_data.get('temp_max')
            raw_weather_data['humidity'] = main_data.get('humidity')
            raw_weather_data['visibility'] = raw_weather_data.get('visibility') # 它本來就在第一層
            raw_weather_data['wind_speed'] = raw_weather_data.get('wind', {}).get('speed')
            raw_weather_data['precipitation'] = precipitation
            
    
            weather_info = raw_weather_data.get('weather', [{}])[0]
            raw_weather_data['description'] = weather_info.get('description')
            raw_weather_data['main_weather'] = weather_info.get('main')

       
            weather_service.save_from_raw_weather_data(raw_weather_data)
            
            logging.info(f"Successfully scraped weather: {precipitation}mm rain, {raw_weather_data['temp']}°C")
        else:
            logging.error(f"Failed to fetch weather data: {response.status_code}")
            
    except Exception as e:
        logging.error(f"Error in weather scraper: {e}")
