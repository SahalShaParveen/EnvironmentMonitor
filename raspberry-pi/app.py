from flask import Flask
import sqlite3

app = Flask(__name__)
DB = "data.db"


def get_latest_metric(metric_name, device_name):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT value
    FROM readings
    WHERE metric = ? AND device=?
    ORDER BY id DESC
    LIMIT 1
    """, (metric_name, device_name))

    row = cursor.fetchone()
    conn.close()

    value = row[0] if row is not None else None
    return value


@app.route("/api/latest")
def latest_data():
    return {
        "esp32_1": {
            "temperature": get_latest_metric("temperature", "esp32_1"),
            "humidity": get_latest_metric("humidity", "esp32_1"),
        },
        "pi": {
            "cpu_temp": get_latest_metric("cpu_temp", "pi"),
            "ram_usage": get_latest_metric("ram_usage", "pi"),
            "disk_usage": get_latest_metric("disk_usage", "pi")
        }
    }


@app.route("/")
def home():
    temp = get_latest_metric("temperature", "esp32_1")
    humidity = get_latest_metric("humidity", "esp32_1")
    cpu_temp = get_latest_metric("cpu_temp", "pi")
    ram_usage = get_latest_metric("ram_usage", "pi")
    disk_usage = get_latest_metric("disk_usage", "pi")

    return f"""
        <h2>ESP32_1</h2>

        <p>Temperature: {temp} °C</p>
        <p>Humidity: {humidity} %</p>
        
        <h2>Raspberry Pi</h2>
        <p>CPU Temperature: {cpu_temp} °C</p>
        <p>RAM Usage : {ram_usage}%</p>
        <p>Disk Usage : {disk_usage}%</p>
    
    """


app.run(host="0.0.0.0", port=5000)
