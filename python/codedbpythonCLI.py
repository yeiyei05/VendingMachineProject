import time
import threading
import sys
import re
import os
import serial
import mysql.connector

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Imports prompt_toolkit
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import HTML, ANSI
from prompt_toolkit.shortcuts import print_formatted_text

# ── Configuration Initiale ────────────────────────────────────────────────────
PORT = "COM3"
BAUD = 115200
TIMEOUT = 0.1

DB_HOST = 'mysql.mrlojnat.fr'
DB_PORT = 3306
DB_NAME = 'app'
DB_USER = 'g3b'
DB_PASSWORD = 'am$S&y39i$5k%^BV'

# ── Variables Globales & État ─────────────────────────────────────────────────
console = Console()
stop_event = threading.Event()
ser = None

state = {
    "tx_count": 0,  # Compte désormais ce qu'on REÇOIT de la carte
    "rx_count": 0,  # Compte désormais ce qu'on ENVOIE à la carte
    "save_interval": 1.0,
    "last_save_time": 0,
    "last_moteur_id": 0,
    "live_logs": True
}

# ── LA SÉCURITÉ ANTI-BUG ANSI ─────────────────────────────────────────────────
def rprint_safe(rich_text_string):
    """Capture le rendu Rich (couleurs/styles) et le passe proprement à prompt_toolkit."""
    with console.capture() as capture:
        console.print(rich_text_string)
    print_formatted_text(ANSI(capture.get()), end="")

# ── Fonctions Utilitaires d'Affichage ─────────────────────────────────────────
def log_ts():
    return f"[dim white][{time.strftime('%H:%M:%S')}.{int((time.time() % 1) * 1000):03d}][/dim white]"

def log_info(msg):
    if state["live_logs"]: rprint_safe(f"{log_ts()} [bold blue]INFO[/bold blue] | {msg}")

def log_success(msg):
    if state["live_logs"]: rprint_safe(f"{log_ts()} [bold green]SUCCESS[/bold green] | {msg}")

def log_warn(msg):
    if state["live_logs"]: rprint_safe(f"{log_ts()} [bold yellow]WARN[/bold yellow] | {msg}")

def log_error(msg):
    if state["live_logs"]: rprint_safe(f"{log_ts()} [bold red]ERROR[/bold red] | {msg}")

def log_rx(msg):
    """Ce qu'on ENVOIE à la carte (Saisie utilisateur)"""
    if state["live_logs"]: rprint_safe(f"{log_ts()} [bold cyan]RX[/bold cyan] | {msg}")

def log_tx(msg):
    """Ce qu'on REÇOIT de la carte (Données STM32)"""
    if state["live_logs"]: rprint_safe(f"{log_ts()} [bold magenta]TX[/bold magenta] | {msg}")

def print_banner():
    banner = """[bold cyan]
  ██████  ████████ ███    ███ ██████  ██████
 ██    ██    ██    ████  ████      ██      ██
 ██    ██    ██    ██ ████ ██  █████   █████
  ██████     ██    ██  ██  ██ ██      ██
       ██    ██    ██      ██ ███████ ███████
[/bold cyan]
[bold white]SUPERVISEUR CLI & BDD MYSQL[/bold white]
    """
    rprint_safe(Panel(banner, border_style="cyan", expand=False))

def print_help():
    table = Table(title="[bold]COMMANDES DISPONIBLES[/bold]", show_header=True, header_style="bold magenta")
    table.add_column("Commande", style="cyan")
    table.add_column("Paramètres", style="yellow")
    table.add_column("Description", style="white")

    table.add_row("send", "<cmd>", "Envoie une commande directe au STM32 (génère du RX)")
    table.add_row("moteur", "<A/R>", "Injecte un ordre Avancer(A) ou Reculer(R) dans la BDD")
    table.add_row("interval", "<sec>", "Change l'intervalle de sauvegarde des distances")
    table.add_row("fetch", "", "Affiche les 25 dernières valeurs de la table 'distance'")
    table.add_row("clear", "", "Vide complètement la table 'distance' (TRUNCATE)")
    table.add_row("toggle", "", "Active/Désactive l'affichage des logs en direct")
    table.add_row("help", "", "Affiche ce menu d'aide")
    table.add_row("exit / quit", "", "Ferme proprement le programme")

    rprint_safe(table)

# ── Logique Métier (Base de Données & Série) ──────────────────────────────────
def init_system():
    global ser
    try:
        db = mysql.connector.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, connect_timeout=3)
        cursor = db.cursor()
        cursor.execute("SELECT MAX(id) FROM moteur")
        res = cursor.fetchone()
        state["last_moteur_id"] = res[0] if (res and res[0] is not None) else 0
        cursor.close()
        db.close()
        log_success(f"Connexion BDD [{DB_HOST}] établie.")
    except Exception as e:
        log_error(f"Erreur d'initialisation BDD: {e}")

    try:
        ser = serial.Serial(port=PORT, baudrate=BAUD, timeout=TIMEOUT)
        ser.rts = False
        ser.dtr = False
        log_success(f"Port Série [{PORT} @ {BAUD}] ouvert.")
    except Exception as e:
        log_error(f"Erreur d'ouverture du port série: {e}")

def background_worker():
    db_conn, db_cursor = None, None
    try:
        db_conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        db_cursor = db_conn.cursor()
    except Exception as e:
        log_error(f"Le worker BDD a échoué: {e}")

    buffer = b""
    regex_parser = re.compile(r'Distance:\s*(\d+)\s*mm\s*\|\s*Stock:\s*(\d+)')
    last_moteur_poll_time = 0

    while not stop_event.is_set() and ser and ser.is_open:
        now = time.time()

        if now - last_moteur_poll_time >= 1.0:
            last_moteur_poll_time = now
            if db_conn and db_conn.is_connected():
                try:
                    db_cursor.execute("SELECT id, action FROM moteur ORDER BY id DESC LIMIT 1")
                    row = db_cursor.fetchone()
                    if row:
                        m_id, m_action = row[0], row[1]
                        if m_id > state["last_moteur_id"]:
                            state["last_moteur_id"] = m_id
                            if m_action in ("A", "R"):
                                ser.write((m_action + "\n").encode("utf-8"))
                                ser.flush()
                                log_info(f"BDD -> STM32 : Nouvel ordre détecté ! Action: '{m_action}' (ID: {m_id})")
                except:
                    pass

        try:
            chunk = ser.read(ser.in_waiting or 1)
            if not chunk: continue
            buffer += chunk

            while b"\n" in buffer:
                line_bytes, buffer = buffer.split(b"\n", 1)
                ligne = line_bytes.decode("utf-8", errors="ignore").rstrip("\r").strip()
                if not ligne: continue

                # Ce qu'on reçoit de la carte = Émission de la carte -> Incrémentation TX
                state["tx_count"] += 1

                if "[ERR]" in ligne or "/!\\" in ligne:
                    log_error(f"STM32: {ligne}")
                elif "[WARN]" in ligne:
                    log_warn(f"STM32: {ligne}")
                else:
                    log_tx(ligne)  # Affiché sous le tag TX (Magenta)

                match = regex_parser.search(ligne)
                if match:
                    distance, stock = int(match.group(1)), int(match.group(2))
                    if now - state["last_save_time"] >= state["save_interval"]:
                        if db_conn and db_conn.is_connected():
                            try:
                                db_cursor.execute("INSERT INTO distance (distance, stock) VALUES (%s, %s)", (distance, stock))
                                db_conn.commit()
                                state["last_save_time"] = now
                                log_success(f"Insert DB | Dist: {distance}mm | Stock: {stock}")
                            except Exception as e:
                                log_error(f"Erreur Insert DB: {e}")
        except Exception:
            break

    if db_cursor: db_cursor.close()
    if db_conn: db_conn.close()

# ── Commandes Utilisateur ─────────────────────────────────────────────────────
def cmd_send(args):
    if not ser or not ser.is_open:
        log_error("Le port série n'est pas ouvert.")
        return
    cmd = " ".join(args)
    try:
        ser.write((cmd + "\n").encode("utf-8"))
        ser.flush()

        # Ce qu'on envoie à la carte = Réception de la carte -> Incrémentation RX
        state["rx_count"] += 1
        log_rx(f"Envoyé: {cmd}")  # Affiché sous le tag RX (Cyan)
    except Exception as e:
        log_error(f"Erreur d'envoi: {e}")

def cmd_moteur(args):
    if not args or args[0].upper() not in ["A", "R"]:
        log_error("Usage: moteur <A ou R>")
        return
    action = args[0].upper()
    try:
        conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO moteur (action) VALUES (%s)", (action,))
        conn.commit()
        cursor.close()
        conn.close()
        log_success(f"Action '{action}' poussée en base de données.")
    except Exception as e:
        log_error(f"Erreur d'ajout moteur: {e}")

def cmd_interval(args):
    if not args:
        log_error("Usage: interval <secondes>")
        return
    try:
        val = float(args[0])
        if val < 0: raise ValueError
        state["save_interval"] = val
        log_success(f"Intervalle de sauvegarde réglé sur {val}s")
    except ValueError:
        log_error("Veuillez entrer un nombre positif valide.")

def cmd_fetch():
    try:
        conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM distance ORDER BY id DESC LIMIT 25")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            log_warn("La table 'distance' est vide.")
            return

        table = Table(title="Historique des Distances (25 dernières)", style="cyan")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Distance (mm)", justify="right", style="magenta")
        table.add_column("Stock", justify="right", style="green")

        for row in reversed(rows):
            table.add_row(str(row[0]), str(row[1]), str(row[2]))

        rprint_safe(table)
    except Exception as e:
        log_error(f"Erreur de récupération: {e}")

def cmd_clear():
    reponse = input("⚠️ Es-tu sûr de vouloir vider la table 'distance' ? (y/n): ")
    if reponse.lower() == 'y':
        try:
            conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
            cursor = conn.cursor()
            cursor.execute("TRUNCATE TABLE distance")
            conn.commit()
            cursor.close()
            conn.close()
            log_success("Table 'distance' vidée avec succès.")
        except Exception as e:
            log_error(f"Erreur Truncate: {e}")

# ── Boucle Principale Interactive ─────────────────────────────────────────────
def main():
    console.clear()

    print_banner()
    rprint_safe("[dim]Initialisation des connexions...[/dim]")
    init_system()

    worker = threading.Thread(target=background_worker, daemon=True)
    worker.start()

    print_help()

    session = PromptSession()

    try:
        with patch_stdout():
            while True:
                time.sleep(0.05)

                user_input = session.prompt(HTML('<ansiyellow><b>STM32-CLI ❯</b></ansiyellow> ')).strip()

                if not user_input: continue

                parts = user_input.split()
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd in ["exit", "quit"]:
                    break
                elif cmd == "help" or cmd == "?":
                    print_help()
                elif cmd == "send":
                    cmd_send(args)
                elif cmd == "moteur":
                    cmd_moteur(args)
                elif cmd == "interval":
                    cmd_interval(args)
                elif cmd == "fetch":
                    cmd_fetch()
                elif cmd == "clear":
                    cmd_clear()
                elif cmd == "toggle":
                    state["live_logs"] = not state["live_logs"]
                    etat = "ACTIVÉS" if state["live_logs"] else "DÉSACTIVÉS"
                    rprint_safe(f"[bold magenta]Logs en direct {etat}.[/bold magenta]")
                else:
                    log_error(f"Commande inconnue: {cmd}. Tapez 'help' pour la liste.")

    except KeyboardInterrupt:
        pass
    finally:
        rprint_safe("\n[bold red]Arrêt du système en cours...[/bold red]")
        stop_event.set()
        if ser and ser.is_open:
            ser.close()
        rprint_safe("[bold green]Système arrêté proprement. À bientôt ![/bold green]")

if __name__ == "__main__":
    main()