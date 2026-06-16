"""
stm32_commander.py
==================
Interface Python pour STM32 Nucleo L412KB — COM3 / 115200 bauds

- Thread de lecture continu : affiche tout ce que le STM32 envoie en temps réel
- Thread principal : invite de commandes interactive
- Toutes les réponses sont horodatées et colorées

Utilisation :
    python stm32_commander.py

Commandes disponibles (envoyées à la carte) :
    PING              → PONG
    STATUS            → dump état complet
    LED:ON / LED:OFF  → pilote PC3
    MOTOR:<steps>     → avance le moteur
    quit / exit       → quitter le script
"""

import serial
import threading
import time
import sys
import os

# ── Configuration ─────────────────────────────────────────────────────────────

PORT     = "COM3"
BAUD     = 115200
TIMEOUT  = 1          # secondes, timeout lecture série (non bloquant)

# ── Codes couleur ANSI ────────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    GREY   = "\033[90m"
    WHITE  = "\033[97m"

def enable_ansi_windows():
    """Active les couleurs ANSI sur Windows 10+."""
    if sys.platform == "win32":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

# ── Formatage horodaté ─────────────────────────────────────────────────────────

def ts():
    """Retourne un timestamp court : HH:MM:SS.mmm"""
    t = time.time()
    ms = int((t % 1) * 1000)
    return time.strftime("%H:%M:%S", time.localtime(t)) + f".{ms:03d}"

def colorize_rx(line: str) -> str:
    """Colorie une ligne reçue selon son préfixe."""
    if line.startswith("[ERR]"):
        return f"{C.RED}{line}{C.RESET}"
    if line.startswith("[WARN]"):
        return f"{C.YELLOW}{line}{C.RESET}"
    if line.startswith("[ACK]"):
        return f"{C.GREEN}{line}{C.RESET}"
    if line.startswith("[HB]"):
        return f"{C.GREY}{line}{C.RESET}"
    if line.startswith("[RX]"):
        return f"{C.CYAN}{line}{C.RESET}"
    if line.startswith("[CMD]"):
        return f"{C.BLUE}{line}{C.RESET}"
    if line.startswith("[DBG]"):
        return f"{C.GREY}{line}{C.RESET}"
    if line.startswith("PONG"):
        return f"{C.GREEN}{C.BOLD}{line}{C.RESET}"
    if line.startswith("---"):
        return f"{C.YELLOW}{line}{C.RESET}"
    if line.startswith("==="):
        return f"{C.WHITE}{C.BOLD}{line}{C.RESET}"
    return line

# ── État global ────────────────────────────────────────────────────────────────

stop_event   = threading.Event()   # Signal d'arrêt propre
rx_count     = 0                   # Lignes reçues
tx_count     = 0                   # Commandes envoyées
last_ack     = ""                  # Dernier ACK reçu

# ── Thread de lecture ─────────────────────────────────────────────────────────

def reader_thread(ser: serial.Serial):
    """
    Lit en continu sur le port série et affiche chaque ligne.
    S'exécute dans un thread dédié pour ne pas bloquer l'invite de commandes.
    """
    global rx_count, last_ack
    buffer = b""

    while not stop_event.is_set():
        try:
            chunk = ser.read(ser.in_waiting or 1)
        except serial.SerialException as e:
            print(f"\n{C.RED}[READER] Erreur série : {e}{C.RESET}")
            stop_event.set()
            break

        if not chunk:
            continue

        buffer += chunk

        # Traiter toutes les lignes complètes dans le buffer
        while b"\n" in buffer:
            line_bytes, buffer = buffer.split(b"\n", 1)
            # Supprimer \r éventuel
            line = line_bytes.decode("utf-8", errors="replace").rstrip("\r")
            if not line:
                continue

            rx_count += 1
            if "[ACK]" in line:
                last_ack = line

            # Affichage : efface la ligne de saisie courante, affiche, réaffiche le prompt
            sys.stdout.write("\r\033[2K")   # Efface la ligne courante
            print(f"{C.GREY}[{ts()}]{C.RESET} {colorize_rx(line)}")
            sys.stdout.write(f"{C.YELLOW}>>> {C.RESET}")
            sys.stdout.flush()


# ── Envoi d'une commande ──────────────────────────────────────────────────────

def send_cmd(ser: serial.Serial, cmd: str):
    """Envoie une commande (ajoute \\n) et log l'envoi."""
    global tx_count
    tx_count += 1
    raw = (cmd.strip() + "\n").encode("utf-8")
    try:
        ser.write(raw)
        ser.flush()
        print(f"{C.GREY}[{ts()}]{C.RESET} {C.BOLD}{C.WHITE}[TX #{tx_count}]{C.RESET} {cmd}")
    except serial.SerialException as e:
        print(f"{C.RED}[TX] Erreur : {e}{C.RESET}")


# ── Aide ─────────────────────────────────────────────────────────────────────

HELP = f"""
{C.BOLD}{C.WHITE}Commandes disponibles :{C.RESET}
  {C.GREEN}PING{C.RESET}           → Teste la connexion (répond PONG)
  {C.GREEN}STATUS{C.RESET}         → Dump état interne du STM32
  {C.GREEN}LED:ON{C.RESET}         → Allume LED PC3
  {C.GREEN}LED:OFF{C.RESET}        → Éteint LED PC3
  {C.GREEN}MOTOR:<n>{C.RESET}      → Avance le moteur de n pas  (ex: MOTOR:512)
  {C.CYAN}stats{C.RESET}          → Affiche les compteurs locaux Python
  {C.CYAN}help{C.RESET}           → Cet écran
  {C.RED}quit / exit{C.RESET}    → Quitter proprement
"""

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    enable_ansi_windows()

    print(f"""
{C.BOLD}{C.WHITE}╔══════════════════════════════════════════════╗
║   STM32 UART Commander — Python interface    ║
║   Port : {PORT:<10} Baud : {BAUD:<10}     ║
╚══════════════════════════════════════════════╝{C.RESET}
""")

    # ── Ouverture du port ─────────────────────────────────────────────────────
    try:
        ser = serial.Serial(
            port     = PORT,
            baudrate = BAUD,
            bytesize = serial.EIGHTBITS,
            parity   = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            timeout  = TIMEOUT,
            xonxoff  = False,
            rtscts   = False,
            dsrdtr   = False,
        )
        # Pas de toggle RTS/DTR : évite le reset involontaire du Nucleo
        ser.rts = False
        ser.dtr = False
        print(f"{C.GREEN}[OK]{C.RESET} Port {PORT} ouvert à {BAUD} bauds")
    except serial.SerialException as e:
        print(f"{C.RED}[ERREUR]{C.RESET} Impossible d'ouvrir {PORT} : {e}")
        print(f"  → Vérifiez que la carte est branchée et que {PORT} est correct")
        sys.exit(1)

    # ── Démarrage thread lecture ──────────────────────────────────────────────
    t = threading.Thread(target=reader_thread, args=(ser,), daemon=True, name="RX")
    t.start()
    print(f"{C.GREEN}[OK]{C.RESET} Thread lecture RX démarré")
    print(f"{C.GREY}      Tapez 'help' pour la liste des commandes{C.RESET}\n")

    # Petite pause pour laisser le STM32 envoyer sa bannière de boot
    time.sleep(0.5)

    # ── Boucle de commandes interactive ──────────────────────────────────────
    try:
        while not stop_event.is_set():
            try:
                sys.stdout.write(f"{C.YELLOW}>>> {C.RESET}")
                sys.stdout.flush()
                user_input = input().strip()
            except (EOFError, KeyboardInterrupt):
                print(f"\n{C.YELLOW}[INFO]{C.RESET} Interruption clavier")
                break

            if not user_input:
                continue

            cmd_lower = user_input.lower()

            # ── Commandes locales Python ──────────────────────────────────────
            if cmd_lower in ("quit", "exit", "q"):
                print(f"{C.YELLOW}[INFO]{C.RESET} Fermeture...")
                break

            if cmd_lower == "help":
                print(HELP)
                continue

            if cmd_lower == "stats":
                print(f"""
{C.BOLD}Statistiques locales :{C.RESET}
  Lignes reçues  : {rx_count}
  Commandes TX   : {tx_count}
  Dernier ACK    : {last_ack if last_ack else '(aucun)'}
  Port           : {PORT} @ {BAUD}
  Thread RX      : {'vivant' if t.is_alive() else f'{C.RED}MORT{C.RESET}'}
""")
                continue

            # ── Validation basique avant envoi ────────────────────────────────
            valid_prefixes = ("PING", "STATUS", "LED:ON", "LED:OFF", "MOTOR:")
            cmd_upper = user_input.upper()
            is_valid = any(cmd_upper.startswith(p) for p in valid_prefixes)

            if not is_valid:
                print(f"{C.YELLOW}[WARN]{C.RESET} Commande non reconnue localement : '{user_input}'")
                print(f"       Envoi quand même... (tapez 'help' pour la liste)")

            # ── Envoi à la carte ──────────────────────────────────────────────
            send_cmd(ser, user_input.upper() if is_valid else user_input)

            # Attente courte pour laisser la réponse arriver avant le prochain prompt
            time.sleep(0.15)

    finally:
        stop_event.set()
        time.sleep(0.2)
        ser.close()
        print(f"\n{C.GREEN}[OK]{C.RESET} Port {PORT} fermé. Au revoir.")
        print(f"{C.GREY}     TX={tx_count} RX_lignes={rx_count}{C.RESET}")


if __name__ == "__main__":
    main()