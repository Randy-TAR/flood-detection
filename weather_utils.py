import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
import os
API_KEY = os.getenv("API_KEY")

cities = {
    "Yaoundé": (3.8480, 11.5021),
    "Douala": (4.0511, 9.7075),
    "Garoua": (9.3000, 13.4000),
    "Bertoua": (4.5833, 13.7000),
    "Buea": (4.1500, 9.3000),
    "Bamenda": (5.9631, 10.1591),
    "Maroua": (10.5950, 14.3190),
    "Ngaoundéré": (5.6167, 12.2833),
    "Ebolowa": (3.0667, 11.5667),
    "Limbe": (4.0000, 9.2000),
    "Bafoussam": (5.4500, 10.4000),
    "Dschang": (5.4667, 10.0667),
    "Kumba": (4.6333, 9.4500),
    "Bafang": (5.0000, 10.0000),
    "Nkongsamba": (4.9500, 10.1167),
    "Mbouda": (5.6333, 10.0167),
    "Bandjoun": (5.4667, 10.0833),
    "Foumban": (5.7167, 10.9667),
    "Banyo": (5.3667, 10.3667),
    "Edea": (3.6500, 10.1500),
    "Obala": (4.0000, 11.5000)
}

def get_rain_intensity(weather_id):
    mapping = {
        500: "Light rain",
        501: "Moderate rain",
        502: "Heavy intensity rain",
        503: "Very heavy rain",
        504: "Extreme rain",
        520: "Light intensity shower rain",
        521: "Shower rain",
        522: "Heavy intensity shower rain",
        531: "Ragged shower rain"
    }
    return mapping.get(weather_id, "Unknown rain intensity")

def find_closest_forecast(forecasts):
    """Find forecast closest to current time"""
    now_ts = int(datetime.now().timestamp())
    closest = min(forecasts, key=lambda x: abs(x['dt'] - now_ts))
    return closest

def get_weather_data():
    import pandas as pd
    data_list = []
    for city, (lat, lon) in cities.items():
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
        try:
            data = requests.get(url, params=params, timeout=10).json()
            if "list" not in data:
                continue
            forecast = find_closest_forecast(data["list"])
            rain_mm = forecast.get("rain", {}).get("3h", 0)
            temp = round(forecast["main"]["temp"])
            weather_id = forecast["weather"][0]["id"]
            weather_desc = get_rain_intensity(weather_id)
            time_label = datetime.fromtimestamp(forecast["dt"]).strftime("%I:%M %p")
            
            # Only include cities with some rain (optional)
            if rain_mm > 0:
                data_list.append({
                    "city": city,
                    "rain_mm": round(rain_mm, 2),
                    "temp": temp,
                    "weather_id": weather_id,
                    "weather_desc": weather_desc,
                    "time_label": time_label
                })
        except Exception as e:
            print(f"❌ Error fetching data for {city}: {e}")
    return pd.DataFrame(data_list)
