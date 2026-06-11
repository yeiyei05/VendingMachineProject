import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ── Configuration ──────────────────────────────────────────
DB_HOST = 'mysql.mrlojnat.fr'
DB_PORT = 3306
DB_NAME = 'app'
DB_USER = 'g3b'
DB_PASSWORD = 'am$S&y39i$5k%^BV'

DISTANCE_VIDE_MM = 300
EPAISSEUR_PRODUIT_MM = 50
# ───────────────────────────────────────────────────────────

conn = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

query = """
SELECT timestamp, distance
FROM distance
WHERE timestamp >= NOW() - INTERVAL 12 HOUR
ORDER BY timestamp
"""

df = pd.read_sql(query, conn)
conn.close()

# Calcul du stock à partir de la distance
df["stock"] = ((DISTANCE_VIDE_MM - df["distance"]) / EPAISSEUR_PRODUIT_MM).astype(int).clip(lower=0)

plt.figure(figsize=(12, 6))
plt.plot(df["timestamp"], df["stock"], color='#00f0ff', linewidth=2)

plt.title("Évolution du stock sur 12 heures")
plt.xlabel("Heure")
plt.ylabel("Stock (aliments)")
plt.grid(True)

file_id = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"stock_12h_{file_id}.png"

plt.savefig(filename)
plt.close()

print(f"[INFO] Graphique sauvegardé : {filename}")