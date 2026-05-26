import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/environment_log.csv",
                 names=["timestamp", "temperature", "humidity"])

df["timestamp"] = pd.to_datetime(df["timestamp"])

plt.plot(df["timestamp"], df["temperature"])
plt.title("Temperature Over Time")
plt.xlabel("Time")
plt.ylabel("°C")
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()
