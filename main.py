from requests.exceptions import HTTPError
from fastapi import FastAPI
import os
import requests
from requests import ConnectionError

weather_api_key = os.getenv('VISUAL_CROSSING_API_KEY')
app = FastAPI()


@app.get("/weather")
def get_weather(city:str):

    params = {'key': weather_api_key,
                                      'contentType': 'json',
                                      'include':'current',
                                      'unitGroup':'metric'}
    response = requests.get(f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}',
                            params=params)
    try:
        response.raise_for_status()
        if response.status_code == 200:
            print('Weather Request OK')
        else:
            print('Weather Request Error')
        data = response.json()
        weather_now = data['currentConditions']
        print(type(weather_now))
        print(weather_now.keys())
        temperature = weather_now['temp']
        conditions = weather_now['conditions']


    except HTTPError as e:
        print(f'Http error: {e}')


    return {'city':city,
        'weather': temperature,
        'weather_status': conditions}

