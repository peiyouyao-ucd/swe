from config import OWM_URL, OWM_APIKEY, OWM_CITY
from services.weather_service import WeatherService
import requests


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
    # TODO: 把 print 换成 log, 并设置适当的日志等级
    try:
        response = requests.get(OWM_URL, params={"q": OWM_CITY, "appid": OWM_APIKEY, "units": "metric"})
        if response.status_code == 200:
            raw_weather_data = response.json()
            weather_service.save_from_raw_weather_data(raw_weather_data)
            print("Successfully scraped weather data.")
        else:
            print(f"Failed to fetch weather data: {response.status_code}")
    except Exception as e:
        print(f"Error in weather scraper: {e}")
