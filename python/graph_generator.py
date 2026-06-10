import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

conn = mysql.connector.connect(
    host="localhost",
    database="vending_machine_db",
    user="root",
    password=""
)

query = """
SELECT timestamp, value_recorded
FROM device_history
WHERE timestamp >= NOW() - INTERVAL 12 HOUR
ORDER BY timestamp
"""

df = pd.read_sql(query, conn)

# Conversion en numérique (important sinon bug possible)
df["value_recorded"] = pd.to_numeric(df["value_recorded"])

plt.figure(figsize=(12, 6))
plt.plot(df["timestamp"], df["value_recorded"])

plt.title("Évolution du stock sur 12 heures")
plt.xlabel("Heure")
plt.ylabel("Stock")
plt.grid(True)



# ✅ nom de fichier avec ID unique
file_id = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"stock_12h_{file_id}.png"

plt.savefig(filename)
plt.close()

print(f"[INFO] Graph sauvegardé : {filename}")