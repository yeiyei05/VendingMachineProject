import serial
import mysql.connector
import time
import re

# ── Configuration ──────────────────────────────────────────
SERIAL_PORT = 'COM4'        # À adapter (Gestionnaire de périphériques)
BAUD_RATE = 115200          # Correspond à MX_USART2_UART_Init

DB_HOST = 'localhost'
DB_NAME = 'vending_machine_db'
DB_USER = 'root'
DB_PASSWORD = ''

DEVICE_NAME = 'HC-SR04'
INTERVALLE = 0.5            # La STM32 envoie toutes les 500ms (HAL_Delay(500))
# ───────────────────────────────────────────────────────────


def get_or_create_device(cursor, conn):
    """Récupère l'ID du HC-SR04 dans devices, le crée si absent."""
    cursor.execute(
        "SELECT id FROM devices WHERE name = %s AND type = 'sensor'",
        (DEVICE_NAME,)
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(
        "INSERT INTO devices (name, type, location) VALUES (%s, 'sensor', 'Distributeur A')",
        (DEVICE_NAME,)
    )
    conn.commit()
    return cursor.lastrowid


def parse_ligne(ligne):
    """
    Parse une ligne du type :
      'Distance: 150 mm | Stock: 3 aliments'
    Retourne (distance, stock) ou None si la ligne ne correspond pas.
    """
    match = re.search(r'Distance:\s*(\d+)\s*mm\s*\|\s*Stock:\s*(\d+)', ligne)
    if match:
        distance = int(match.group(1))
        stock = int(match.group(2))
        return distance, stock
    return None


def main():
    # Connexion BDD
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        device_id = get_or_create_device(cursor, conn)
        print(f"[BDD] Connecté — device_id = {device_id}")
    except mysql.connector.Error as e:
        print(f"[ERREUR BDD] {e}")
        return

    # Connexion port série
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        time.sleep(2)  # Attendre reset STM32
        print(f"[SERIAL] Connecté sur {SERIAL_PORT} à {BAUD_RATE} baud\n")
    except serial.SerialException as e:
        print(f"[ERREUR SERIAL] {e}")
        conn.close()
        return

    print("[INFO] En écoute... (Ctrl+C pour arrêter)\n")

    try:
        while True:
            ligne = ser.readline().decode('utf-8', errors='ignore').strip()

            if not ligne:
                continue

            print(f"[SERIAL] {ligne}")

            # Alertes STM32 — on les affiche mais on n'insère pas
            if '/!\\' in ligne or '!!!' in ligne:
                print(f"  ⚠️  ALERTE : {ligne}")
                continue

            # Ligne de données principale
            result = parse_ligne(ligne)
            if result:
                distance, stock = result

                # On stocke le stock calculé dans value_recorded
                cursor.execute(
                    "INSERT INTO device_history (device_id, value_recorded) VALUES (%s, %s)",
                    (device_id, str(stock))
                )
                conn.commit()
                print(f"  → Distance : {distance} mm | Stock : {stock} aliments | Enregistré ✓\n")

    except KeyboardInterrupt:
        print("\n[INFO] Arrêt propre.")
    finally:
        ser.close()
        cursor.close()
        conn.close()
        print("[INFO] Connexions fermées.")


if __name__ == '__main__':
    main()