import serial
import mysql.connector
import time
import re

# ⚠️ CONFIGURATION À ADAPTER AVANT DE LANCER
# 1. Changer SERIAL_PORT selon ton Gestionnaire de périphériques
# 2. Lancer avec : python codedbpython.py

# ── Configuration ──────────────────────────────────────────
SERIAL_PORT = 'COM3'
BAUD_RATE = 115200

DB_HOST = 'mysql.mrlojnat.fr'
DB_PORT = 3306
DB_NAME = 'app'
DB_USER = 'g3b'
DB_PASSWORD = 'am$S&y39i$5k%^BV'

SAVE_INTERVAL = 1
# ───────────────────────────────────────────────────────────


def parse_ligne(ligne):
    """
    Parse une ligne du type :
    'Distance: 150 mm | Stock: 3 aliments'
    Retourne (distance, stock) ou None si format invalide.
    """
    match = re.search(
        r'Distance:\s*(\d+)\s*mm\s*\|\s*Stock:\s*(\d+)',
        ligne
    )
    if match:
        distance = int(match.group(1))
        stock = int(match.group(2))
        return distance, stock
        print(distance,stock)
    return None


def main():

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        print(f"[BDD] Connecté à {DB_HOST}/{DB_NAME}")

    except mysql.connector.Error as e:
        print(f"[ERREUR BDD] {e}")
        return

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        time.sleep(2)
        print(f"[SERIAL] Connecté sur {SERIAL_PORT} à {BAUD_RATE} baud\n")

    except serial.SerialException as e:
        print(f"[ERREUR SERIAL] {e}")
        conn.close()
        return

    print("[INFO] En écoute... (Ctrl+C pour arrêter)\n")

    last_save_time = 0

    try:
        while True:
            ligne = ser.readline().decode('utf-8', errors='ignore').strip()

            if not ligne:
                continue

            print(f"[SERIAL] {ligne}")

            if '/!\\' in ligne or '!!!' in ligne:
                print(f"⚠️  ALERTE : {ligne}")
                continue

            result = parse_ligne(ligne)

            if result:
                distance, stock = result
                current_time = time.time()

                if current_time - last_save_time >= SAVE_INTERVAL:
                    cursor.execute(
                        "INSERT INTO distance (distance) VALUES (%s)",
                        (stock,)
                    )
                    conn.commit()
                    last_save_time = current_time
                    print(
                        f"[BDD] Enregistré ✓ "
                        f"| Distance : {distance} mm "
                        f"| Stock STM32 : {stock} aliments"
                    )
                else:
                    secondes_restantes = int(
                        SAVE_INTERVAL - (current_time - last_save_time)
                    )
                    print(
                        f"[INFO] Mesure ignorée "
                        f"(prochain enregistrement dans {secondes_restantes}s)"
                    )

    except KeyboardInterrupt:
        print("\n[INFO] Arrêt demandé par l'utilisateur.")

    finally:
        try:
            ser.close()
        except:
            pass
        try:
            cursor.close()
            conn.close()
        except:
            pass
        print("[INFO] Connexions fermées.")


if __name__ == '__main__':
    main()