import serial
import mysql.connector
import time
import re

# ── Configuration ──────────────────────────────────────────
SERIAL_PORT = 'COM3'        # À adapter
BAUD_RATE = 115200          # Correspond à MX_USART2_UART_Init

DB_HOST = 'localhost'
DB_NAME = 'vending_machine_db'
DB_USER = 'root'
DB_PASSWORD = ''

DEVICE_NAME = 'HC-SR04'

# Intervalle entre deux enregistrements en base (secondes)
SAVE_INTERVAL = 60
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
        """
        INSERT INTO devices (name, type, location)
        VALUES (%s, 'sensor', 'Distributeur A')
        """,
        (DEVICE_NAME,)
    )

    conn.commit()
    return cursor.lastrowid


def parse_ligne(ligne):
    """
    Parse une ligne du type :
    'Distance: 150 mm | Stock: 3 aliments'

    Retourne :
    (distance, stock)
    ou None si format invalide.
    """

    match = re.search(
        r'Distance:\s*(\d+)\s*mm\s*\|\s*Stock:\s*(\d+)',
        ligne
    )

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

    # Connexion série
    try:
        ser = serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=2
        )

        # Attendre le reset éventuel de la STM32
        time.sleep(2)

        print(
            f"[SERIAL] Connecté sur {SERIAL_PORT} "
            f"à {BAUD_RATE} baud\n"
        )

    except serial.SerialException as e:
        print(f"[ERREUR SERIAL] {e}")
        conn.close()
        return

    print("[INFO] En écoute... (Ctrl+C pour arrêter)\n")

    # Permet d'enregistrer immédiatement la première mesure
    last_save_time = 0

    try:

        while True:

            ligne = ser.readline() \
                .decode('utf-8', errors='ignore') \
                .strip()

            if not ligne:
                continue

            print(f"[SERIAL] {ligne}")

            # Messages d'alerte envoyés par la STM32
            if '/!\\' in ligne or '!!!' in ligne:
                print(f"⚠️  ALERTE : {ligne}")
                continue

            result = parse_ligne(ligne)

            if result:

                distance, stock = result

                current_time = time.time()

                # Enregistrement seulement toutes les 60 secondes
                if current_time - last_save_time >= SAVE_INTERVAL:

                    cursor.execute(
                        """
                        INSERT INTO device_history
                        (device_id, value_recorded)
                        VALUES (%s, %s)
                        """,
                        (device_id, str(stock))
                    )

                    conn.commit()

                    last_save_time = current_time

                    print(
                        f"[BDD] Enregistré ✓ "
                        f"| Distance : {distance} mm "
                        f"| Stock : {stock} aliments"
                    )

                else:

                    secondes_restantes = int(
                        SAVE_INTERVAL
                        - (current_time - last_save_time)
                    )

                    print(
                        f"[INFO] Mesure ignorée "
                        f"(prochain enregistrement dans "
                        f"{secondes_restantes}s)"
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