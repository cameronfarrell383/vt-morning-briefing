import requests
import config


def fetch_weather() -> dict:
    """Fetch current weather and forecast from OpenWeatherMap.

    Uses the free-tier /weather and /forecast endpoints to get:
    - Current temp and conditions
    - Today's high/low
    - Precipitation chance
    """
    api_key = config.OPENWEATHER_API_KEY
    lat = config.LOCATION_LAT
    lon = config.LOCATION_LON

    if not api_key:
        return {"error": "OPENWEATHER_API_KEY not set"}

    try:
        # Current weather
        current_url = "https://api.openweathermap.org/data/2.5/weather"
        current_resp = requests.get(current_url, params={
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "imperial",
        }, timeout=10)
        current_resp.raise_for_status()
        current = current_resp.json()

        # 5-day/3-hour forecast (to extract today's high/low and rain chance)
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        forecast_resp = requests.get(forecast_url, params={
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "imperial",
            "cnt": 8,  # next 24 hours (8 x 3-hour blocks)
        }, timeout=10)
        forecast_resp.raise_for_status()
        forecast = forecast_resp.json()
    except requests.RequestException as e:
        return {"error": str(e)}

    # Parse forecast for high/low and max precipitation probability
    temps = [entry["main"]["temp"] for entry in forecast["list"]]
    temps.append(current["main"]["temp"])
    high = round(max(temps))
    low = round(min(temps))

    # Precipitation probability (pop = probability of precipitation, 0-1)
    rain_chances = [entry.get("pop", 0) for entry in forecast["list"]]
    max_rain = round(max(rain_chances) * 100) if rain_chances else 0

    return {
        "current_temp": round(current["main"]["temp"]),
        "high": high,
        "low": low,
        "condition": current["weather"][0]["description"].title(),
        "rain_chance": max_rain,
    }


def format_weather(data: dict) -> str:
    """Format weather data into a briefing-friendly string."""
    if "error" in data:
        return f"⚠️ Weather unavailable: {data['error']}"

    return (
        f"🌤 WEATHER\n"
        f"{data['low']}°F → {data['high']}°F, {data['condition'].lower()}, "
        f"{data['rain_chance']}% rain"
    )
