import time
import threading
import sys
import re
import os

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import mysql.connector
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import HTML, ANSI
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style

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
    "tx_count": 0,
    "rx_count": 0,
    "save_interval": 1.0,
    "last_save_time": 0,
    "last_moteur_id": 0,
    "live_logs": True,
    "db_connected": False,
    "serial_connected": False,
    "last_distance": None,
    "last_stock": None,
    "last_action": None,
    "last_action_time": None,
    "start_time": time.time(),
    "last_insert_time": None,
    "error_count": 0,
    "last_error": None,
    "watch_mode": False,
    "db_insert_count": 0,
}

# ── Style prompt_toolkit ──────────────────────────────────────────────────────
prompt_style = Style.from_dict({
    "prompt": "#00d7ff bold",
    "rprompt": "#888888",
})

# ── Anti-bug ANSI ─────────────────────────────────────────────────────────────
def rprint_safe(rich_text_string, end="\n"):
    with console.capture() as capture:
        console.print(rich_text_string, end=end)
    print_formatted_text(ANSI(capture.get()), end="")

# ── Utilitaires d'affichage ───────────────────────────────────────────────────
def log_ts():
    return f"[dim white][{time.strftime('%H:%M:%S')}.{int((time.time() % 1) * 1000):03d}][/dim white]"

def log_info(msg):
    if state["live_logs"]:
        rprint_safe(f"{log_ts()} [bold blue]INFO   [/bold blue] │ {msg}")

def log_success(msg):
    if state["live_logs"]:
        rprint_safe(f"{log_ts()} [bold green]OK     [/bold green] │ {msg}")

def log_warn(msg):
    if state["live_logs"]:
        rprint_safe(f"{log_ts()} [bold yellow]WARN   [/bold yellow] │ {msg}")

def log_error(msg):
    state["error_count"] += 1
    state["last_error"] = msg
    if state["live_logs"]:
        rprint_safe(f"{log_ts()} [bold red]ERROR  [/bold red] │ {msg}")

def log_rx(msg):
    """Ce qu'on ENVOIE à la carte (saisie utilisateur)"""
    if state["live_logs"]:
        rprint_safe(f"{log_ts()} [bold cyan]RX ▶   [/bold cyan] │ {msg}")

def log_tx(msg):
    """Ce qu'on REÇOIT de la carte (données STM32)"""
    if state["live_logs"]:
        rprint_safe(f"{log_ts()} [bold magenta]TX ◀   [/bold magenta] │ {msg}")

def log_db(msg):
    """Log des opérations DB"""
    if state["live_logs"]:
        rprint_safe(f"{log_ts()} [bold white on blue] DB [/bold white on blue]  │ {msg}")

# ── Indicateurs de statut ─────────────────────────────────────────────────────
def status_dot(ok):
    return "[bold green]●[/bold green]" if ok else "[bold red]●[/bold red]"

def format_uptime():
    elapsed = int(time.time() - state["start_time"])
    h, r = divmod(elapsed, 3600)
    m, s = divmod(r, 60)
    if h > 0:
        return f"{h:02d}h{m:02d}m{s:02d}s"
    return f"{m:02d}m{s:02d}s"

def print_status_bar():
    """Affiche une barre de statut compacte."""
    serial_dot = status_dot(state["serial_connected"])
    db_dot = status_dot(state["db_connected"])

    dist_str = f"[bold cyan]{state['last_distance']}mm[/bold cyan]" if state['last_distance'] is not None else "[dim]—[/dim]"
    stock_str = f"[bold green]{state['last_stock']}[/bold green]" if state['last_stock'] is not None else "[dim]—[/dim]"

    parts = [
        f"[dim]Uptime:[/dim] [white]{format_uptime()}[/white]",
        f"[dim]Série:[/dim] {serial_dot} [dim]{PORT}[/dim]",
        f"[dim]BDD:[/dim] {db_dot} [dim]{DB_HOST}[/dim]",
        f"[dim]TX:[/dim] [magenta]{state['tx_count']}[/magenta]  [dim]RX:[/dim] [cyan]{state['rx_count']}[/cyan]",
        f"[dim]Dist:[/dim] {dist_str}  [dim]Stock:[/dim] {stock_str}",
        f"[dim]Inserts:[/dim] [white]{state['db_insert_count']}[/white]",
    ]

    bar = "  │  ".join(parts)
    rprint_safe(f"\n[dim]┌{'─'*78}┐[/dim]")
    rprint_safe(f"[dim]│[/dim] {bar}  [dim]│[/dim]")
    rprint_safe(f"[dim]└{'─'*78}┘[/dim]\n")

# ── Banner ────────────────────────────────────────────────────────────────────
def print_banner():
    banner = """[bold cyan]
⠀⠀⠀⠀⢠⡶⠚⢷⣤⡀⠀⠀⠀⠀⠀⣲⡶⠛⠻⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢠⡿⠁⠀⠀⠙⣷⣄⠀⢀⣴⡟⠁⠀⠀⢷⢹⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣾⠃⠀⠠⠶⠚⠛⠛⠛⠛⠋⠀⠀⣀⡀⢸⠈⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢸⣏⡔⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠚⠉⠉⣿⠀⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢾⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢠⣿⢠⣶⡆⠀⠀⠀⠀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
⢒⡾⠁⠘⠟⠁⠀⠀⠀⠀⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠉⣧⠀⠀⠀⠀⠃⠀⠀⠀⠈⠉⠠⣍⠀⠀⠀⠀⠀⠀⣸⡇⢀⣤⠶⠛⠛⠻⢦⣄
⠀⠸⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⡟⣴⠟⠁⠀⠀⠀⠀⠀⢻
⠀⠀⠀⠛⣷⡦⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⡴⠞⠋⢠⡟⠀⠀⠀⠀⠀⠀⢀⡾
⠀⠀⠀⢰⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠳⣤⡀⢸⠃⠀⠀⠀⠀⢠⡶⠟⠁
⠀⠀⠀⣸⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢷⣹⡄⠀⠀⠀⠀⣼⠀⠀⠀
⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠈⢿⣇⠀⠀⠀⠀⢹⡄⠀⠀
⠀⠀⠀⢸⡀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⡄⠀⠀⠀⠈⣧⠀⠀
⠀⠀⠀⢸⡇⠘⡇⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⢹⡇⠀
⠀⠀⠀⢸⡇⠀⠙⠀⠀⠀⠀⠀⢠⠞⠁⠀⠀⠀⠀⠀⠀⠀⣿⠇⠀⠀⠀⢸⡇⠀
⠀⠀⠀⢸⡇⠀⢸⡆⠀⠀⠀⠀⣟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠀⠀⠀⠀⣸⠇⠀
⠀⠀⠀⢸⣿⠀⠀⡇⠀⠀⠀⠀⣿⡀⠀⠀⠀⠀⠀⠀⠀⢀⡇⠀⠀⢀⣴⡟⠁⠀
⠀⠀⠀⠘⠿⠶⢶⢧⣦⣦⡴⢾⣥⣽⣤⣤⣤⣤⣤⣤⡴⣯⡤⠴⠶⠛⠋⠀⠀⠀ [bold white]██████╗ ██████╗ ██████╗[/bold white]
[bold white]                              ██╔════╝ ╚════██╗██╔══██╗[/bold white]
[bold white]                              ██║  ███╗ █████╔╝██████╔╝[/bold white]
[bold white]                              ██║   ██║ ╚═══██╗██╔══██╗[/bold white]
[bold white]                              ╚██████╔╝██████╔╝██████╔╝[/bold white]
[bold white]                               ╚═════╝ ╚═════╝ ╚═════╝[/bold white]
[/bold cyan]"""

    version_line = "[dim]v2.0  │  Superviseur CLI & BDD MySQL  │  STM32 UART Bridge[/dim]"
    rprint_safe(Panel(banner + "\n" + version_line, border_style="cyan", padding=(0, 2)))

# ── Aide améliorée ─────────────────────────────────────────────────────────────
def print_help():
    rprint_safe(Rule("[bold]COMMANDES[/bold]", style="dim cyan"))

    t1 = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan", padding=(0, 1))
    t1.add_column("Commande", style="bold cyan", min_width=16)
    t1.add_column("Paramètres", style="yellow", min_width=12)
    t1.add_column("Description", style="white")

    t1.add_row("send",     "[dim]<cmd>[/dim]",    "Envoie une commande directe au STM32")
    t1.add_row("moteur",   "[dim]<A|R>[/dim]",    "Pousse un ordre Avancer / Reculer en BDD")
    t1.add_row("interval", "[dim]<sec>[/dim]",    "Change l'intervalle de sauvegarde (défaut: 1.0s)")
    t1.add_row("fetch",    "[dim][N][/dim]",      "Affiche les N dernières valeurs de 'distance' (défaut: 25)")
    t1.add_row("watch",    "",                    "Mode surveillance en direct de la distance")
    t1.add_row("stats",    "",                    "Résumé complet : connexions, compteurs, dernières valeurs")
    t1.add_row("clear",    "",                    "Vide la table 'distance' (TRUNCATE, confirmation requise)")
    t1.add_row("toggle",   "",                    "Active / Désactive l'affichage des logs en direct")
    t1.add_row("status",   "",                    "Barre de statut : série, BDD, TX/RX, distance, stock")
    t1.add_row("help / ?", "",                    "Affiche ce menu")
    t1.add_row("exit / quit", "",                 "Arrêt propre du programme")

    rprint_safe(t1)
    rprint_safe("[dim]  Tab = complétion auto   │   ↑↓ = historique   │   Ctrl+C = quitter[/dim]\n")

# ── Init système ──────────────────────────────────────────────────────────────
def init_system():
    global ser
    rprint_safe(f"[dim]  Connexion BDD {DB_HOST}:{DB_PORT}...[/dim]", end="")
    try:
        db = mysql.connector.connect(
            host=DB_HOST, port=DB_PORT, database=DB_NAME,
            user=DB_USER, password=DB_PASSWORD, connect_timeout=5
        )
        cursor = db.cursor()
        cursor.execute("SELECT MAX(id) FROM moteur")
        res = cursor.fetchone()
        state["last_moteur_id"] = res[0] if (res and res[0] is not None) else 0
        cursor.close()
        db.close()
        state["db_connected"] = True
        rprint_safe(" [bold green]✓ OK[/bold green]")
    except Exception as e:
        state["db_connected"] = False
        rprint_safe(f" [bold red]✗ ERREUR[/bold red] [dim]{e}[/dim]")

    rprint_safe(f"[dim]  Ouverture port série {PORT} @ {BAUD}...[/dim]", end="")
    if not SERIAL_AVAILABLE:
        rprint_safe(" [bold yellow]⚠ pyserial non installé[/bold yellow]")
        return

    try:
        ser = serial.Serial(port=PORT, baudrate=BAUD, timeout=TIMEOUT)
        ser.rts = False
        ser.dtr = False
        state["serial_connected"] = True
        rprint_safe(" [bold green]✓ OK[/bold green]")
    except Exception as e:
        state["serial_connected"] = False
        rprint_safe(f" [bold yellow]⚠ {e}[/bold yellow]")

# ── Worker background ─────────────────────────────────────────────────────────
def background_worker():
    db_conn, db_cursor = None, None

    def connect_db():
        nonlocal db_conn, db_cursor
        try:
            if db_conn and db_conn.is_connected():
                return True
            db_conn = mysql.connector.connect(
                host=DB_HOST, port=DB_PORT, database=DB_NAME,
                user=DB_USER, password=DB_PASSWORD, connection_timeout=5
            )
            db_cursor = db_conn.cursor()
            state["db_connected"] = True
            return True
        except Exception as e:
            state["db_connected"] = False
            return False

    connect_db()

    buffer = b""
    regex_parser = re.compile(r'Distance:\s*(\d+)\s*mm\s*\|\s*Stock:\s*(\d+)')
    last_moteur_poll = 0
    last_db_reconnect = 0
    DB_RECONNECT_INTERVAL = 10.0

    while not stop_event.is_set():
        # Tentative auto-reconnexion BDD
        if not state["db_connected"]:
            now = time.time()
            if now - last_db_reconnect >= DB_RECONNECT_INTERVAL:
                last_db_reconnect = now
                if connect_db():
                    log_success("Reconnexion BDD réussie.")

        now = time.time()

        # Polling moteur (BDD → STM32)
        if now - last_moteur_poll >= 1.0:
            last_moteur_poll = now
            if state["db_connected"] and db_conn and db_conn.is_connected():
                try:
                    db_cursor.execute("SELECT id, action FROM moteur ORDER BY id DESC LIMIT 1")
                    row = db_cursor.fetchone()
                    if row:
                        m_id, m_action = row[0], row[1]
                        if m_id > state["last_moteur_id"]:
                            state["last_moteur_id"] = m_id
                            state["last_action"] = m_action
                            state["last_action_time"] = time.strftime('%H:%M:%S')
                            if m_action in ("A", "R") and ser and ser.is_open:
                                ser.write((m_action + "\n").encode("utf-8"))
                                ser.flush()
                                label = "Avancer" if m_action == "A" else "Reculer"
                                log_info(f"BDD → STM32 : [bold]{label}[/bold] (ID={m_id})")
                except Exception as e:
                    state["db_connected"] = False

        # Lecture port série
        if not (ser and ser.is_open):
            time.sleep(0.05)
            continue

        try:
            chunk = ser.read(ser.in_waiting or 1)
            if not chunk:
                continue
            buffer += chunk

            while b"\n" in buffer:
                line_bytes, buffer = buffer.split(b"\n", 1)
                ligne = line_bytes.decode("utf-8", errors="ignore").rstrip("\r").strip()
                if not ligne:
                    continue

                state["tx_count"] += 1

                if "[ERR]" in ligne:
                    log_error(f"STM32: {ligne}")
                elif "[WARN]" in ligne or "/!\\" in ligne:
                    log_warn(f"STM32: {ligne}")
                else:
                    log_tx(ligne)

                    # Mode watch : affichage condensé
                    if state["watch_mode"] and state["last_distance"] is not None:
                        pass  # géré dans cmd_watch

                match = regex_parser.search(ligne)
                if match:
                    distance = int(match.group(1))
                    stock = int(match.group(2))
                    state["last_distance"] = distance
                    state["last_stock"] = stock

                    if now - state["last_save_time"] >= state["save_interval"]:
                        if state["db_connected"] and db_conn and db_conn.is_connected():
                            try:
                                db_cursor.execute(
                                    "INSERT INTO distance (distance, stock) VALUES (%s, %s)",
                                    (distance, stock)
                                )
                                db_conn.commit()
                                state["last_save_time"] = now
                                state["last_insert_time"] = time.strftime('%H:%M:%S')
                                state["db_insert_count"] += 1
                                log_success(f"Insert DB │ Dist: [bold cyan]{distance}mm[/bold cyan] │ Stock: [bold green]{stock}[/bold green]")
                            except Exception as e:
                                log_error(f"Insert DB: {e}")
                                state["db_connected"] = False
        except Exception:
            state["serial_connected"] = False
            break

    if db_cursor:
        try: db_cursor.close()
        except: pass
    if db_conn:
        try: db_conn.close()
        except: pass

# ── Commandes ─────────────────────────────────────────────────────────────────
def cmd_send(args):
    if not (ser and ser.is_open):
        log_error("Port série non disponible.")
        return
    if not args:
        log_error("Usage: send <commande>")
        return
    cmd = " ".join(args)
    try:
        ser.write((cmd + "\n").encode("utf-8"))
        ser.flush()
        state["rx_count"] += 1
        log_rx(f"[bold]{cmd}[/bold]")
    except Exception as e:
        log_error(f"Envoi série: {e}")

def cmd_moteur(args):
    if not args or args[0].upper() not in ["A", "R"]:
        log_error("Usage: moteur <A|R>  (A=Avancer, R=Reculer)")
        return
    action = args[0].upper()
    label = "[bold green]Avancer ▶[/bold green]" if action == "A" else "[bold red]◀ Reculer[/bold red]"
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, port=DB_PORT, database=DB_NAME,
            user=DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO moteur (action) VALUES (%s)", (action,))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        state["last_action"] = action
        state["last_action_time"] = time.strftime('%H:%M:%S')
        log_success(f"Ordre {label} inséré en BDD (ID: {new_id})")
    except Exception as e:
        log_error(f"Insertion moteur: {e}")

def cmd_interval(args):
    if not args:
        rprint_safe(f"[dim]Intervalle actuel :[/dim] [bold white]{state['save_interval']}s[/bold white]")
        return
    try:
        val = float(args[0])
        if val < 0:
            raise ValueError
        old = state["save_interval"]
        state["save_interval"] = val
        log_success(f"Intervalle : {old}s → [bold]{val}s[/bold]")
    except ValueError:
        log_error("Valeur invalide. Exemple: interval 2.5")

def cmd_fetch(args):
    limit = 25
    if args:
        try:
            limit = max(1, min(int(args[0]), 500))
        except ValueError:
            log_error("Usage: fetch [nombre]")
            return
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, port=DB_PORT, database=DB_NAME,
            user=DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id, distance, stock, created_at FROM distance ORDER BY id DESC LIMIT %s", (limit,))
        rows = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM distance")
        total = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        if not rows:
            log_warn("La table 'distance' est vide.")
            return

        table = Table(
            title=f"[bold]Historique — {len(rows)} sur {total} entrées[/bold]",
            box=box.SIMPLE_HEAD,
            border_style="dim",
            header_style="bold cyan",
            show_lines=False,
        )
        table.add_column("ID", justify="right", style="dim", width=8)
        table.add_column("Distance", justify="right", style="bold cyan", width=12)
        table.add_column("Stock", justify="right", style="bold green", width=10)
        table.add_column("Horodatage", style="dim white", width=22)

        for row in reversed(rows):
            id_val = str(row[0])
            dist_val = f"{row[1]} mm"
            stock_val = str(row[2])
            ts_val = str(row[3]) if len(row) > 3 and row[3] else "—"
            table.add_row(id_val, dist_val, stock_val, ts_val)

        rprint_safe(table)
    except Exception as e:
        log_error(f"Fetch: {e}")

def cmd_stats():
    """Affiche un résumé complet de l'état du système."""
    uptime = format_uptime()

    rprint_safe(Rule("[bold]ÉTAT DU SYSTÈME[/bold]", style="cyan"))

    # Connexions
    t_conn = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    t_conn.add_column("Clé", style="dim")
    t_conn.add_column("Valeur")

    serial_status = f"[bold green]● Connecté[/bold green]  {PORT} @ {BAUD}" if state["serial_connected"] else f"[bold red]● Déconnecté[/bold red]  {PORT}"
    db_status = f"[bold green]● Connecté[/bold green]  {DB_HOST}:{DB_PORT}/{DB_NAME}" if state["db_connected"] else f"[bold red]● Déconnecté[/bold red]  {DB_HOST}"

    t_conn.add_row("Port Série", serial_status)
    t_conn.add_row("Base de Données", db_status)
    t_conn.add_row("Uptime", f"[white]{uptime}[/white]")
    t_conn.add_row("Logs en direct", "[green]Activés[/green]" if state["live_logs"] else "[red]Désactivés[/red]")
    rprint_safe(t_conn)

    rprint_safe(Rule(style="dim"))

    # Trafic
    t_traffic = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    t_traffic.add_column("Clé", style="dim")
    t_traffic.add_column("Valeur")
    t_traffic.add_row("Trames reçues (TX ◀)", f"[bold magenta]{state['tx_count']}[/bold magenta]")
    t_traffic.add_row("Trames envoyées (RX ▶)", f"[bold cyan]{state['rx_count']}[/bold cyan]")
    t_traffic.add_row("Inserts BDD", f"[bold white]{state['db_insert_count']}[/bold white]")
    t_traffic.add_row("Intervalle sauvegarde", f"[white]{state['save_interval']}s[/white]")
    t_traffic.add_row("Erreurs totales", f"[bold red]{state['error_count']}[/bold red]")
    if state["last_error"]:
        t_traffic.add_row("Dernière erreur", f"[dim red]{state['last_error'][:60]}[/dim red]")
    rprint_safe(t_traffic)

    rprint_safe(Rule(style="dim"))

    # Dernières valeurs
    t_vals = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    t_vals.add_column("Clé", style="dim")
    t_vals.add_column("Valeur")

    dist = f"[bold cyan]{state['last_distance']} mm[/bold cyan]" if state["last_distance"] is not None else "[dim]Aucune donnée[/dim]"
    stock = f"[bold green]{state['last_stock']}[/bold green]" if state["last_stock"] is not None else "[dim]—[/dim]"
    insert_ts = f"[white]{state['last_insert_time']}[/white]" if state["last_insert_time"] else "[dim]—[/dim]"
    action_str = f"[bold]{'Avancer' if state['last_action']=='A' else 'Reculer'}[/bold] à {state['last_action_time']}" if state["last_action"] else "[dim]Aucun[/dim]"

    t_vals.add_row("Dernière distance", dist)
    t_vals.add_row("Dernier stock", stock)
    t_vals.add_row("Dernier insert BDD", insert_ts)
    t_vals.add_row("Dernier ordre moteur", action_str)
    rprint_safe(t_vals)

    rprint_safe(Rule(style="dim"))

def cmd_watch():
    """Mode surveillance : affichage en live de la distance toutes les secondes."""
    rprint_safe("[dim]Mode surveillance actif. [bold white]Entrée[/bold white] ou [bold white]q[/bold white] pour quitter.[/dim]")
    state["watch_mode"] = True
    try:
        last_val = None
        while True:
            time.sleep(1.0)
            d = state["last_distance"]
            s = state["last_stock"]
            if d != last_val:
                last_val = d
                dist_str = f"[bold cyan]{d} mm[/bold cyan]" if d is not None else "[dim]—[/dim]"
                stock_str = f"[bold green]{s}[/bold green]" if s is not None else "[dim]—[/dim]"
                rprint_safe(f"  {log_ts()}  Distance: {dist_str}   Stock: {stock_str}")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        state["watch_mode"] = False
        rprint_safe("[dim]Mode surveillance terminé.[/dim]")

def cmd_clear():
    rprint_safe("[bold yellow]⚠  Cette action est irréversible et vide toute la table 'distance'.[/bold yellow]")
    try:
        confirm = input("   Confirmer ? (tapez 'oui' pour valider) : ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        rprint_safe("[dim]Annulé.[/dim]")
        return

    if confirm == "oui":
        try:
            conn = mysql.connector.connect(
                host=DB_HOST, port=DB_PORT, database=DB_NAME,
                user=DB_USER, password=DB_PASSWORD
            )
            cursor = conn.cursor()
            cursor.execute("TRUNCATE TABLE distance")
            conn.commit()
            cursor.close()
            conn.close()
            state["db_insert_count"] = 0
            state["last_distance"] = None
            state["last_stock"] = None
            log_success("Table 'distance' vidée avec succès.")
        except Exception as e:
            log_error(f"TRUNCATE: {e}")
    else:
        rprint_safe("[dim]Opération annulée.[/dim]")

# ── Complétion & Boucle principale ────────────────────────────────────────────
COMMANDS = [
    "send", "moteur", "interval", "fetch", "watch",
    "stats", "clear", "toggle", "status", "help", "exit", "quit",
]

def get_rprompt():
    """Affiche un indicateur de statut à droite du prompt."""
    parts = []
    parts.append("●" if state["serial_connected"] else "○")
    parts.append("●" if state["db_connected"] else "○")
    if state["last_distance"] is not None:
        parts.append(f"{state['last_distance']}mm")
    return " ".join(parts)

def main():
    console.clear()
    print_banner()

    rprint_safe("")
    rprint_safe("[dim]  Initialisation...[/dim]")
    init_system()
    rprint_safe("")

    worker = threading.Thread(target=background_worker, daemon=True)
    worker.start()

    print_help()
    print_status_bar()

    completer = WordCompleter(COMMANDS + ["A", "R"], ignore_case=True)
    session = PromptSession(
        completer=completer,
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
        style=prompt_style,
    )

    try:
        with patch_stdout():
            while True:
                time.sleep(0.02)

                # Indicateur statut dans le rprompt
                serial_dot = "◉" if state["serial_connected"] else "○"
                db_dot = "◉" if state["db_connected"] else "○"
                dist_hint = f"  {state['last_distance']}mm" if state["last_distance"] is not None else ""
                rprompt_str = f"<ansiblue>{serial_dot}</ansiblue> <ansicyan>{db_dot}</ansicyan><ansigray>{dist_hint}</ansigray>"

                user_input = session.prompt(
                    HTML('<ansicyan><b>STM32</b></ansicyan><ansiwhite> ❯</ansiwhite> '),
                    rprompt=HTML(rprompt_str),
                ).strip()

                if not user_input:
                    continue

                parts = user_input.split()
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd in ["exit", "quit"]:
                    break
                elif cmd in ["help", "?"]:
                    print_help()
                elif cmd == "send":
                    cmd_send(args)
                elif cmd == "moteur":
                    cmd_moteur(args)
                elif cmd == "interval":
                    cmd_interval(args)
                elif cmd == "fetch":
                    cmd_fetch(args)
                elif cmd == "watch":
                    cmd_watch()
                elif cmd == "stats":
                    cmd_stats()
                elif cmd == "clear":
                    cmd_clear()
                elif cmd == "status":
                    print_status_bar()
                elif cmd == "toggle":
                    state["live_logs"] = not state["live_logs"]
                    etat = "[bold green]ACTIVÉS[/bold green]" if state["live_logs"] else "[bold red]DÉSACTIVÉS[/bold red]"
                    rprint_safe(f"  Logs {etat}")
                else:
                    log_warn(f"Commande inconnue: [bold]{cmd}[/bold]  — tapez [bold]help[/bold] pour la liste")

    except KeyboardInterrupt:
        pass
    finally:
        rprint_safe("\n[dim]Arrêt en cours...[/dim]")
        stop_event.set()
        if ser and ser.is_open:
            try:
                ser.close()
            except:
                pass
        rprint_safe("[bold green]✓ Arrêt propre.[/bold green]\n")


if __name__ == "__main__":
    main()