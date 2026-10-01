from requests.exceptions import HTTPError,Timeout,ConnectionError,JSONDecodeError
from fastapi import FastAPI,HTTPException,Request
import os
import requests
import redis
import json

weather_api_key = os.getenv('VISUAL_CROSSING_API_KEY')
redis_url = os.getenv('REDIS_URL')


redis_client = redis.from_url(
    redis_url,
    decode_responses=True
)

app = FastAPI()


@app.get("/weather")
def get_weather(request: Request, city: str):

    client_ip = request.client.host

    rate_key = f"rate_limit:{client_ip}"

    request_count = redis_client.incr(rate_key)

    if request_count > 10:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Try again later"
        )

    if request_count == 1:
        redis_client.expire(rate_key, 60)

    params = {'key': weather_api_key,
              'contentType': 'json',
              'include':'current',
              'unitGroup':'metric'}

    cache_key = f"weather:{city.strip().lower()}"
    cached_weather = redis_client.get(cache_key)
    if cached_weather:
        return json.loads(cached_weather)

    try:
        response = requests.get(
        f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}',
            params=params,
            timeout=5)

        response.raise_for_status()
        data = response.json()

        weather_now = data['currentConditions']
        temperature = weather_now['temp']
        conditions = weather_now['conditions']

        result = {
            'city': city,
            'weather': temperature,
            'weather_status': conditions
        }

        redis_client.setex(
            cache_key,
            43200,
            json.dumps(result)
        )
        return result

    except HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Weather service returned an error"
        )
    except Timeout:
        raise HTTPException(
            status_code=504,
            detail="Weather service timed out"
        )
    except ConnectionError:
        raise HTTPException(
           status_code=503,
            detail="Weather service unavailable"
       )
    except KeyError:
        raise HTTPException(
            status_code=502,
            detail="Weather data format is invalid"
        )

    except JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail="Weather service returned invalid data"
        )



