import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any

import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
CITIES_ENV = os.getenv("CITIES", "")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_cities_from_env() -> List[str]:
    return [city.strip() for city in CITIES_ENV.split(",") if city.strip()]


def create_s3_client():
    """
    Create and return a boto3 S3 client.
    """
    return boto3.client("s3", region_name=AWS_REGION)


def fetch_weather_for_city(city: str) -> Dict[str, Any]:
    """
    Fetch weather data from OpenWeather API for a given city.
    Returns parsed JSON if successful, raises exception otherwise.
    """
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "imperial",  # Fahrenheit
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] HTTP error for city {city}: {http_err}")
        raise
    except requests.exceptions.RequestException as req_err:
        print(f"[ERROR] Request error for city {city}: {req_err}")
        raise


def extract_relevant_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract temperature (F), humidity, and weather condition, plus timestamp and city.
    """
    city_name = raw_data.get("name")
    main = raw_data.get("main", {})
    weather = raw_data.get("weather", [{}])[0]

    return {
        "city": city_name,
        "temperature_f": main.get("temp"),
        "humidity": main.get("humidity"),
        "condition": weather.get("description"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw": raw_data,
    }



def upload_to_s3(s3_client, data: Dict[str, Any]) -> None:
    """
    Uploads JSON data to S3 bucket with a timestamped key.
    """
    city = data.get("city", "unknown").replace(" ", "_")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    key = f"weather-data/{city}/{city}_{timestamp}.json"

    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=key,
            Body=json.dumps(data).encode("utf-8"),
            ContentType="application/json",
        )
        print(f"[INFO] Uploaded data for {city} to s3://{S3_BUCKET_NAME}/{key}")
    except (BotoCoreError, ClientError) as e:
        print(f"[ERROR] Failed to upload data for {city} to S3: {e}")
        raise


def save_to_local_file(data: Dict[str, Any]) -> None:
    """
    Saves JSON data to a local file in the docs directory.
    """
    city = data.get("city", "unknown").replace(" ", "_")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{city}_{timestamp}.json"
    file_path = os.path.join("docs", filename)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[INFO] Saved data for {city} to {file_path}")
    except IOError as e:
        print(f"[ERROR] Failed to save data for {city} locally: {e}")



def main():
    if not OPENWEATHER_API_KEY:
        print("[FATAL] OPENWEATHER_API_KEY is not set in .env")
        return

    if not S3_BUCKET_NAME:
        print("[FATAL] S3_BUCKET_NAME is not set in .env")
        return

    cities = get_cities_from_env()
    if not cities:
        print("[FATAL] No cities configured. Please set CITIES in .env")
        return

    s3_client = create_s3_client()

    for city in cities:
        print(f"[INFO] Fetching weather for {city}...")
        try:
            raw_data = fetch_weather_for_city(city)
            cleaned = extract_relevant_data(raw_data)
            print(
                f"[INFO] {cleaned['city']}: "
                f"{cleaned['temperature_f']}°F, "
                f"{cleaned['humidity']}% humidity, "
                f"{cleaned['condition']}"
            )
            upload_to_s3(s3_client, cleaned)
            save_to_local_file(cleaned)
        except Exception as e:
            # Do not stop the whole script for one failed city
            print(f"[WARN] Skipping city {city} due to error: {e}")


if __name__ == "__main__":
    main()
