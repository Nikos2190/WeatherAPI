from fastapi import FastAPI

app = FastAPI()


@app.get("/weather")
def get_weather():
    return {'city':'Athens',
        'weather': 25,
        'weather_status':'foggy'}

