import requests
import json
import sqlite3
import csv
from typing import Optional

def get_location_name(latitude: float, longitude: float) -> str:
    BASE_URL = "https://nominatim.openstreetmap.org/"
    ENDPOINT = f"reverse?lat={latitude}&lon={longitude}&format=json"
    headers = {"User-Agent": "geo-request"}
    response = requests.get(BASE_URL + ENDPOINT, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        address = data.get("address", {})
        return address.get("city") or address.get("town") or address.get("village") or "Unbekannte Stadt"
    return "Fehler bei der Anfrage"

def get_weather_data(latitude: float, longitude: float, days: int = 3):
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min", "uv_index_max"],
        "current_weather": True,
        "timezone": "auto"
    }
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        return response.json()
    return None

def save_weather_data_to_db(city, latitude, longitude, temperature, humidity, wind_speed, uv_index):
    conn = sqlite3.connect("wetter.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO extrawetter (city, latitude, longitude, temperature, humidity, wind_speed, uv_index)
        VALUES (?, ?, ?, ?, ?, ?, ?)               
    """, (city, latitude, longitude, temperature, humidity, wind_speed, uv_index))
    conn.commit()
    conn.close()

def create_database():
    conn = sqlite3.connect("wetter.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extrawetter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            temperature REAL,
            humidity REAL,
            wind_speed REAL,
            uv_index REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )               
    """)
    conn.commit()
    conn.close()

def get_saved_weather():
    conn = sqlite3.connect("wetter.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM extrawetter ORDER BY timestamp DESC")
    data = cursor.fetchall()
    conn.close()
    return data

def export_weather_data_to_csv():
    data = get_saved_weather()
    with open("v1.2/weather_data.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "City", "Latitude", "Longitude", "Temperature", "Humidity", "Wind Speed", "UV Index", "Timestamp"])
        writer.writerows(data)
    print("Weather data exported to weather_data.csv")

def user_input_coordinates():
    try:
        latitude = float(input("Geben Sie die Breite ein: "))
        longitude = float(input("Geben Sie die Länge ein: "))
        weather_data = get_weather_data(latitude, longitude)
        if weather_data:
            city = get_location_name(latitude, longitude)
            temp = weather_data["current_weather"]["temperature"]
            humidity = weather_data.get("humidity", None)
            wind_speed = weather_data["current_weather"]["windspeed"]
            uv_index = weather_data["daily"]["uv_index_max"][0] if "daily" in weather_data else None
            save_weather_data_to_db(city, latitude, longitude, temp, humidity, wind_speed, uv_index)
            print(f"Daten für {city} gespeichert!")
    except ValueError:
        print("Ungültige Eingabe. Bitte geben Sie numerische Werte ein.")

if __name__ == "__main__":
    create_database()
    
    
    export_weather_data_to_csv()
    print(json.dumps(get_saved_weather(), indent=4, ensure_ascii=False))
    
    user_input_coordinates()