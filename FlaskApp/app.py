from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_saved_weather():
    conn = sqlite3.connect("wetter.db")
    cursor = conn.cursor()
    cursor.execute("SELECT city, latitude, longitude, temperature, humidity, wind_speed, uv_index, timestamp FROM extrawetter ORDER BY timestamp DESC")
    data = cursor.fetchall()
    conn.close()
    return data

@app.route("/")
def index():
    weather_data = get_saved_weather()
    return render_template("index.html", weather_data=weather_data)

if __name__ == "__main__":
    app.run(debug=True)
