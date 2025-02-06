import requests
import json
from typing import Optional
import sqlite3

def get_location_name(latitude: float, longitude: float) -> str:

    BASE_URL = "https://nominatim.openstreetmap.org/"
    ENDPOINT_1 = f"reverse?lat={latitude}&lon={longitude}&format=json"
    url = f"{BASE_URL}{ENDPOINT_1}"
    headers = {"User-Agent": "geo-request"}

    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        if "address" in data:
            address = data["address"]

            if "city" in address:
                return address["city"]
            elif "town" in address:
                return address["town"]
            elif "village" in address:
                return address["village"]
            elif "hamlet" in address:
                return address["hamlet"]
        return "Ort nicht gefunden"
    else:
        return "Fehler bei der Anfrage"

# def get_temperature(latitude: float, longitude: float, city_name: Optional[str] = None) -> Optional[float]:
#     """Ruft die aktuelle Temperatur für die angegebene Breiten- und Längengrad ab.

#     Args:
#         latitude (float): Breitangrad als float
#         longitude (float): Längengrad als float
#         city_name (Optional[str], optional): Name der Stadt. Defaults to None.

#     Returns:
#         Optional[float]: Temperatur in Grad Celsius
#     """

#     BASE_URL = "https://api.open-meteo.com/"
#     ENDPOINT_1 = f"v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true"

#     response = requests.get(BASE_URL + ENDPOINT_1)

#     if response.status_code == 200:
#         data = response.json()
#         # print(json.dumps(data, indent=4, sort_keys=True))

#         current_weather = data["current_weather"] # Über Indexer ansprechen
#         # print(json.dumps(current_weather, indent=4))

#         temperature = current_weather["temperature"]
#         print(f"Temperatur in {city_name} ist: {temperature} Grad Celsius!")
#         return temperature
#     else:
#         print("Fehler beim Abrufen der Wetterdaten")
#         return None

def get_temperature(locations: list):

    BASE_URL = "https://api.open-meteo.com/"
    temperature_storage = []

    for location in locations:
        latitude =  location["latitude"]
        longitude = location["longitude"]
        location_name = get_location_name(latitude, longitude)

        ENDPOINT_1 = f"v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        response = requests.get(BASE_URL + ENDPOINT_1)

        if response.status_code == 200:
            data = response.json()
            current_weather = data["current_weather"]
            temperature = current_weather["temperature"]

            save_weather_data_to_db(location_name, latitude, longitude, temperature)

            temperature_storage.append({
                "city": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "temperature": temperature
            })

            print(f"Temperature in {location_name}: {temperature} Grad Celsius!")
        else:
            print(f"Fehler beim Abrufen der Wetterdaten für {location_name}")
            temperature_storage.append({
                "city": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "temperature": None
            })
    return temperature_storage

def create_database():

    # Verbindung zur Datenbank herstellen (erstellt Datei falls nicht vorhanden)
    conn = sqlite3.connect("wetter.db")
    # Cursor erstellen (ein spezielles Objekt, das SQL-Befehle ausführt)
    cursor = conn.cursor()
    # Tabelle erstellen (falls nichr vorhanden), fürht ein SQL-Statement aus:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wetterdaten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            temperature REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )               
    """)

def save_weather_data_to_db(city, latitude, longitude, temperature):

    conn = sqlite3.connect("wetter.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO wetterdaten (city, latitude, longitude, temperature)
        VALUES (?, ?, ?, ?)               
    """, (city, latitude, longitude, temperature))

    conn.commit()
    conn.close()

def get_saved_weather():
    conn = sqlite3.connect("wetter.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM wetterdaten ORDER BY timestamp DESC")
    data = cursor.fetchall()
    conn.close()

    return data

if __name__ == "__main__":

    locations = [
    {"latitude": 52.52, "longitude": 13.41},
    {"latitude": 48.85, "longitude": 2.35},
    {"latitude": 40.71, "longitude": -74.01},
    {"latitude": 35.68, "longitude": 139.69}
    ]

    create_database()
    get_temperature(locations)
    data_from_db = get_saved_weather()
    print(json.dumps(data_from_db, indent=4, ensure_ascii=False))
 