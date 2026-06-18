from flask import Flask, request, render_template
import sqlite3
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
DB = "data.db"

FRESHNESS_SECONDS = 15


def get_latest_metric(metric_name, device_name):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT value, timestamp
    FROM readings
    WHERE metric = ? AND device=?
    ORDER BY id DESC
    LIMIT 1
    """, (metric_name, device_name))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None, None

    value = row[0]
    timestamp = row[1]

    return value, timestamp


def is_fresh(timestamp):
    if timestamp is None:
        return False

    last = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    return (now - last) < timedelta(seconds=FRESHNESS_SECONDS)


@app.route("/api/latest")
def latest_data():
    temperature, temperature_ts = get_latest_metric("temperature", "esp32_1")
    humidity, humidity_ts = get_latest_metric("humidity", "esp32_1")
    cpu_temp, cpu_temp_ts = get_latest_metric("cpu_temp", "pi")
    ram_usage, ram_usage_ts = get_latest_metric("ram_usage", "pi")
    disk_usage, disk_usage_ts = get_latest_metric("disk_usage", "pi")
    return {
        "esp32_1": {
            "temperature": temperature if is_fresh(temperature_ts) else None,
            "humidity": humidity if is_fresh(humidity_ts) else None,
        },
        "pi": {
            "cpu_temp": cpu_temp if is_fresh(cpu_temp_ts) else None,
            "ram_usage": ram_usage if is_fresh(ram_usage_ts) else None,
            "disk_usage": disk_usage if is_fresh(disk_usage_ts) else None
        }
    }


@app.route("/api/history")
def history():
    metric = request.args.get("metric")
    device = request.args.get("device")
    period = request.args.get("period", "24h")

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    now = datetime.now(timezone.utc)

    if period == "1h":
        start_time = now - timedelta(hours=1)
    elif period == "24h":
        start_time = now - timedelta(days=1)
    elif period == "7d":
        start_time = now - timedelta(days=7)
    else:
        start_time = now - timedelta(days=1)

    cursor.execute("""
        SELECT timestamp, value
        FROM readings
        WHERE metric = ?
        AND device = ?
        AND timestamp >= ?
        ORDER BY timestamp ASC
    """, (metric, device, start_time.isoformat()))

    rows = cursor.fetchall()
    conn.close()

    data = []

    for timestamp, value in rows:
        data.append({
            "x": timestamp,
            "y": value
        })

    return {
        "data": data
    }


@app.route("/")
def home():
    return render_template("index.html")


app.run(host="0.0.0.0", port=5000)
