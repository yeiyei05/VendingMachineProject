import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial
import mysql.connector
import threading
import queue
import time
import sys
import re

# ── Configuration Initiale ────────────────────────────────────────────────────
PORT = "COM3"
BAUD = 115200
TIMEOUT = 0.1

DB_HOST = 'mysql.mrlojnat.fr'
DB_PORT = 3306
DB_NAME = 'app'
DB_USER = 'g3b'
DB_PASSWORD = 'am$S&y39i$5k%^BV'

# ── Palette de Couleurs Modern Dark ───────────────────────────────────────────
BG_MAIN      = "#121214"  # Fond principal ultra-sombre
BG_PANEL     = "#1a1a1e"  # Fond des sections
BG_INPUT     = "#26262b"  # Fond des zones de saisie
FG_TEXT      = "#e1e1e6"  # Texte principal
FG_MUTED     = "#7c7c8a"  # Texte secondaire

COLOR_CYAN   = "#61afef"  # Flux RX
COLOR_GREEN  = "#98c379"  # ACK / BDD Succès
COLOR_RED    = "#e06c75"  # ERREUR / ALERTE
COLOR_YELLOW = "#e5c07b"  # WARN / Attention
COLOR_BLUE   = "#4dc4ff"  # Flux TX
COLOR_PURPLE = "#c678dd"  # Actions BDD

class STM32DbCommanderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ STM32 Nucleo & MySQL Advanced Supervisor")
        self.root.geometry("1200x750")
        self.root.configure(bg=BG_MAIN)

        # États globaux
        self.tx_count = 0
        self.rx_count = 0
        self.save_interval = 1.0     # Pour la table 'distance'
        self.last_save_time = 0
        self.last_moteur_id = 0      # Retient le dernier ID traité de la table 'moteur'

        self.ser = None
        self.stop_event = threading.Event()
        self.ui_queue = queue.Queue()

        # Initialisation UI
        self.setup_styles()
        self.create_layout()

        # Connexions matérielles et logicielles
        self.init_hardware_and_db()

        # Protocoles de boucles IHM
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.after(50, self.process_ui_queue)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=BG_MAIN, foreground=FG_TEXT)
        style.configure("TLabel", background=BG_PANEL, foreground=FG_TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG_PANEL, font=("Segoe UI", 11, "bold"), foreground=COLOR_CYAN)

        style.configure("TButton", background=BG_INPUT, foreground=FG_TEXT, borderwidth=0, font=("Segoe UI", 10, "bold"), padding=6)
        style.map("TButton", background=[("active", "#323239")])
        style.configure("Action.TButton", background=COLOR_BLUE, foreground=BG_MAIN)
        style.map("Action.TButton", background=[("active", "#7ad5ff")])
        style.configure("Alert.TButton", background=COLOR_RED, foreground=FG_TEXT)
        style.map("Alert.TButton", background=[("active", "#ff8890")])
        style.configure("Purple.TButton", background=COLOR_PURPLE, foreground=FG_TEXT)
        style.map("Purple.TButton", background=[("active", "#d58be3")])

    def create_layout(self):
        # ── 1. BARRE SUPÉRIEURE DE STATUT ─────────────────────────────────────
        top_bar = tk.Frame(self.root, bg=BG_PANEL, height=45)
        top_bar.pack(fill=tk.X, padx=10, pady=5)

        lbl_info = ttk.Label(top_bar, text=f" 🔌 {PORT} @ {BAUD} | 🗄️ {DB_HOST}", font=("Consolas", 10, "bold"), background=BG_PANEL)
        lbl_info.pack(side=tk.LEFT, padx=15, pady=10)

        self.lbl_status_ser = tk.Label(top_bar, text="SÉRIE: INIT...", bg=BG_PANEL, fg=COLOR_YELLOW, font=("Segoe UI", 9, "bold"))
        self.lbl_status_ser.pack(side=tk.RIGHT, padx=10)
        self.lbl_status_db = tk.Label(top_bar, text="BDD: INIT...", bg=BG_PANEL, fg=COLOR_YELLOW, font=("Segoe UI", 9, "bold"))
        self.lbl_status_db.pack(side=tk.RIGHT, padx=10)

        main_container = tk.Frame(self.root, bg=BG_MAIN)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ── 2. PANNEAU DE GAUCHE (Contrôles & Actions BDD) ────────────────────
        left_panel = tk.Frame(main_container, bg=BG_PANEL, width=280)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)

        # Commandes Directes STM32
        self.create_panel_section(left_panel, "📟 COMMANDES EN DIRECT")
        ttk.Button(left_panel, text="PING", command=lambda: self.send_cmd("PING")).pack(fill=tk.X, padx=15, pady=3)
        ttk.Button(left_panel, text="STATUS", command=lambda: self.send_cmd("STATUS")).pack(fill=tk.X, padx=15, pady=3)
        ttk.Button(left_panel, text="LED:ON", style="Action.TButton", command=lambda: self.send_cmd("LED:ON")).pack(fill=tk.X, padx=15, pady=3)
        ttk.Button(left_panel, text="LED:OFF", command=lambda: self.send_cmd("LED:OFF")).pack(fill=tk.X, padx=15, pady=3)

        # Ordres d'écriture table 'moteur'
        self.create_panel_section(left_panel, "⚙️ INJECTION TABLE MOTEUR")
        ttk.Button(left_panel, text="Pousser 'A' (Avancer)", style="Purple.TButton", command=lambda: self.action_add_moteur_db("A")).pack(fill=tk.X, padx=15, pady=3)
        ttk.Button(left_panel, text="Pousser 'R' (Reculer)", style="Purple.TButton", command=lambda: self.action_add_moteur_db("R")).pack(fill=tk.X, padx=15, pady=3)

        # Configuration Intervalle Table 'distance'
        self.create_panel_section(left_panel, "🗄️ PARAMÈTRES TABLE DISTANCE")
        interval_frame = tk.Frame(left_panel, bg=BG_PANEL)
        interval_frame.pack(fill=tk.X, padx=15, pady=5)
        ttk.Label(interval_frame, text="Intervalle (s) :", background=BG_PANEL).pack(side=tk.LEFT)
        self.ent_interval = tk.Entry(interval_frame, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0, width=8, font=("Segoe UI", 10))
        self.ent_interval.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0), ipady=2)
        self.ent_interval.insert(0, str(self.save_interval))
        ttk.Button(left_panel, text="💾 Enregistrer l'intervalle", command=self.action_update_interval).pack(fill=tk.X, padx=15, pady=(5, 10))

        ttk.Button(left_panel, text="🔄 Rafraîchir l'historique", command=self.action_fetch_last_db).pack(fill=tk.X, padx=15, pady=3)
        ttk.Button(left_panel, text="⚠️ Vider la table distance", style="Alert.TButton", command=self.action_clear_db).pack(fill=tk.X, padx=15, pady=25)

        # ── 3. PANNEAU DE DROITE (Double Terminal de Supervision) ─────────────
        right_panel = tk.Frame(main_container, bg=BG_MAIN)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Flux Série Live
        tk.Label(right_panel, text="📜 LIAISON SÉRIE EN TEMPS RÉEL (COM)", bg=BG_MAIN, fg=FG_MUTED, font=("Segoe UI", 9, "bold"), anchor="w").pack(fill=tk.X, pady=(0,2))
        self.txt_serial = scrolledtext.ScrolledText(right_panel, bg=BG_PANEL, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0, font=("Consolas", 10), height=18, highlightthickness=0)
        self.txt_serial.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Enregistrements BDD
        tk.Label(right_panel, text="📊 TRACABILITÉ LOGS BASE DE DONNÉES (MYSQL)", bg=BG_MAIN, fg=FG_MUTED, font=("Segoe UI", 9, "bold"), anchor="w").pack(fill=tk.X, pady=(0,2))
        self.txt_db = scrolledtext.ScrolledText(right_panel, bg=BG_PANEL, fg=COLOR_GREEN, insertbackground=FG_TEXT, bd=0, font=("Consolas", 10), height=10, highlightthickness=0)
        self.txt_db.pack(fill=tk.BOTH, expand=True)

        for txt_area in (self.txt_serial, self.txt_db):
            txt_area.tag_config("ts", foreground=FG_MUTED)
            txt_area.tag_config("default", foreground=FG_TEXT)
            txt_area.tag_config("err", foreground=COLOR_RED, font=("Consolas", 10, "bold"))
            txt_area.tag_config("warn", foreground=COLOR_YELLOW)
            txt_area.tag_config("ack", foreground=COLOR_GREEN, font=("Consolas", 10, "bold"))
            txt_area.tag_config("tx", foreground=COLOR_BLUE)
            txt_area.tag_config("cyan", foreground=COLOR_CYAN)
            txt_area.tag_config("bdd", foreground=COLOR_PURPLE, font=("Consolas", 10, "bold"))

        # Champ d'envoi manuel
        input_frame = tk.Frame(right_panel, bg=BG_MAIN)
        input_frame.pack(fill=tk.X, pady=(10, 0))
        self.ent_cmd = tk.Entry(input_frame, bg=BG_PANEL, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0, font=("Consolas", 11))
        self.ent_cmd.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=6, padx=(0, 5))
        self.ent_cmd.bind("<Return>", lambda e: self.action_send_manual())
        ttk.Button(input_frame, text="ENVOYER", command=self.action_send_manual).pack(side=tk.RIGHT)

        # ── 4. PIED DE PAGE ───────────────────────────────────────────────────
        status_bar = tk.Frame(self.root, bg=BG_PANEL, height=25)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 5))
        self.lbl_tx_counter = ttk.Label(status_bar, text="TX: 0", font=("Consolas", 9))
        self.lbl_tx_counter.pack(side=tk.LEFT, padx=15, pady=3)
        self.lbl_rx_counter = ttk.Label(status_bar, text="RX: 0", font=("Consolas", 9))
        self.lbl_rx_counter.pack(side=tk.LEFT, padx=15, pady=3)

    def create_panel_section(self, parent, title):
        lbl = ttk.Label(parent, text=title, style="Title.TLabel")
        lbl.pack(fill=tk.X, padx=10, pady=(12, 4))
        sep = tk.Frame(parent, height=1, bg="#2d2d34", bd=0)
        sep.pack(fill=tk.X, padx=10, pady=(0, 8))

    # ── ⚙️ TRAITEMENT BACKEND & SYNCHRONISATION ───────────────────────────────
    def init_hardware_and_db(self):
        # 1. Vérification BDD & Lecture du dernier ID de la table 'moteur'
        try:
            db_test = mysql.connector.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, connect_timeout=3)
            cursor = db_test.cursor()

            # On récupère le MAX(id) existant pour ne pas exécuter les ordres historiques au boot
            cursor.execute("SELECT MAX(id) FROM moteur")
            res = cursor.fetchone()
            self.last_moteur_id = res[0] if (res and res[0] is not None) else 0

            cursor.close()
            db_test.close()
            self.lbl_status_db.config(text="● BDD OK", fg=COLOR_GREEN)
        except mysql.connector.Error as e:
            self.lbl_status_db.config(text="● BDD DISCONNECTED", fg=COLOR_RED)
            self.log_to_area(self.txt_serial, f"[ERREUR BDD INIT] Impossible d'accéder au serveur MySQL : {e}\n", "err")

        # 2. Ouverture de la liaison Série et lancement du Worker
        try:
            self.ser = serial.Serial(port=PORT, baudrate=BAUD, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=TIMEOUT)
            self.ser.rts = False
            self.ser.dtr = False
            self.lbl_status_ser.config(text="● SÉRIE OK", fg=COLOR_GREEN)
            self.log_to_area(self.txt_serial, f"[SÉRIE] Liaison établie sur {PORT} ({BAUD} bauds)\n", "ack")

            # Start Central Worker Thread
            self.worker_thread = threading.Thread(target=self.background_core_loop, daemon=True)
            self.worker_thread.start()
        except serial.SerialException as e:
            self.lbl_status_ser.config(text="● SÉRIE ERROR", fg=COLOR_RED)
            self.log_to_area(self.txt_serial, f"[ERREUR SÉRIE] Impossible d'ouvrir {PORT} : {e}\n", "err")
            messagebox.showerror("Erreur Port Série", f"Échec de l'ouverture du port {PORT}.")

    def background_core_loop(self):
        """Thread maître : écoute l'UART, enregistre les distances et surveille les ordres SQL 'moteur'"""
        db_conn = None
        db_cursor = None
        try:
            db_conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
            db_cursor = db_conn.cursor()
            self.ui_queue.put(("log_ser", ("[BDD Thread] Synchronisation arrière-plan active.\n", "bdd")))
        except mysql.connector.Error as e:
            self.ui_queue.put(("log_ser", (f"[BDD Thread ERREUR] Fonctionnement en mode dégradé (sans écriture) : {e}\n", "err")))

        buffer = b""
        regex_parser = re.compile(r'Distance:\s*(\d+)\s*mm\s*\|\s*Stock:\s*(\d+)')
        last_moteur_poll_time = 0

        while not self.stop_event.is_set() and self.ser and self.ser.is_open:
            now = time.time()

            # ── SYNCHRO 1 : Lecture de la table 'moteur' (Fréquence : 1 seconde) ──
            if now - last_moteur_poll_time >= 1.0:
                last_moteur_poll_time = now
                if db_conn and db_conn.is_connected():
                    try:
                        db_cursor.execute("SELECT id, action FROM moteur ORDER BY id DESC LIMIT 1")
                        row = db_cursor.fetchone()
                        if row:
                            m_id, m_action = row[0], row[1]
                            # Si un nouvel ID supérieur apparaît : on traite l'action une seule fois
                            if m_id > self.last_moteur_id:
                                self.last_moteur_id = m_id
                                if m_action in ("A", "R"):
                                    # Envoi direct à la carte STM32
                                    self.ser.write((m_action + "\n").encode("utf-8"))
                                    self.ser.flush()

                                    # Log de l'événement distant
                                    log_str = f"[BDD -> STM32] Nouvel ordre détecté en table ! Action: '{m_action}' (ID: {m_id})\n"
                                    self.ui_queue.put(("log_ser", (log_str, "bdd")))
                    except mysql.connector.Error:
                        pass # Évite de saturer la console sur des micros-coupures réseau

            # ── SYNCHRO 2 : Écoute du port Série & parsing de la table 'distance' ──
            try:
                chunk = self.ser.read(self.ser.in_waiting or 1)
                if not chunk:
                    continue
                buffer += chunk

                while b"\n" in buffer:
                    line_bytes, buffer = buffer.split(b"\n", 1)
                    ligne = line_bytes.decode("utf-8", errors="ignore").rstrip("\r").strip()
                    if not ligne:
                        continue

                    self.ui_queue.put(("rx_line", ligne))

                    if '/!\\' in ligne or '!!!' in ligne:
                        self.ui_queue.put(("log_ser", (f"⚠️ ALERTE STM32 : {ligne}\n", "err")))
                        continue

                    match = regex_parser.search(ligne)
                    if match:
                        distance, stock = int(match.group(1)), int(match.group(2))

                        if now - self.last_save_time >= self.save_interval:
                            if db_conn and db_conn.is_connected():
                                try:
                                    db_cursor.execute("INSERT INTO distance (distance, stock) VALUES (%s, %s)", (distance, stock))
                                    db_conn.commit()
                                    self.last_save_time = now

                                    self.ui_queue.put(("log_ser", (f"[BDD ✓] Capteur synchro | Dist: {distance} mm | Stock: {stock}\n", "ack")))
                                    self.ui_queue.put(("refresh_db_view", None))
                                except mysql.connector.Error as err:
                                    self.ui_queue.put(("log_ser", (f"[ERREUR INSERT distance] {err}\n", "err")))
                        else:
                            restant = int(self.save_interval - (now - self.last_save_time))
                            self.ui_queue.put(("log_ser", (f"[INFO] Seuil intervalle (Ignoré, dispo dans {restant}s)\n", "ts")))

            except Exception as e:
                break

        if db_cursor: db_cursor.close()
        if db_conn: db_conn.close()

    def process_ui_queue(self):
        """Réceptionne les paquets asynchrones du thread maître pour rafraîchir le rendu graphique"""
        while not self.ui_queue.empty():
            try:
                task_type, data = self.ui_queue.get_nowait()

                if task_type == "rx_line":
                    self.rx_count += 1
                    self.lbl_rx_counter.config(text=f"RX: {self.rx_count}")
                    tag = "cyan"
                    if data.startswith("[ERR]"): tag = "err"
                    elif data.startswith("[WARN]"): tag = "warn"
                    elif data.startswith("[ACK]"): tag = "ack"
                    elif "PONG" in data: tag = "ack"
                    self.log_to_area(self.txt_serial, data + "\n", tag)

                elif task_type == "log_ser":
                    text, tag = data
                    self.log_to_area(self.txt_serial, text, tag)

                elif task_type == "refresh_db_view":
                    self.action_fetch_last_db()

            except queue.Empty:
                break
        self.root.after(50, self.process_ui_queue)

    # ── 🛠️ CONTRÔLEURS DE L'INTERFACE ─────────────────────────────────────────
    def send_cmd(self, cmd_string):
        if not self.ser or not self.ser.is_open:
            return
        try:
            self.tx_count += 1
            self.lbl_tx_counter.config(text=f"TX: {self.tx_count}")
            self.ser.write((cmd_string.strip() + "\n").encode("utf-8"))
            self.ser.flush()
            self.log_to_area(self.txt_serial, f"[TX #{self.tx_count}] {cmd_string}\n", "tx")
        except Exception as e:
            self.log_to_area(self.txt_serial, f"[ERREUR TX SÉRIE] {e}\n", "err")

    def action_send_manual(self):
        cmd = self.ent_cmd.get().strip()
        if cmd:
            self.send_cmd(cmd)
            self.ent_cmd.delete(0, tk.END)

    def action_add_moteur_db(self, action_value):
        """Injecte un ordre 'A' ou 'R' directement dans la table 'moteur' en BDD via un sous-thread"""
        def worker():
            try:
                conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO moteur (action) VALUES (%s)", (action_value,))
                conn.commit()
                cursor.close()
                conn.close()
                self.ui_queue.put(("log_ser", (f"[BDD LOCAL] Action '{action_value}' poussée en table 'moteur'.\n", "bdd")))
            except mysql.connector.Error as e:
                self.ui_queue.put(("log_ser", (f"[ERREUR AJOUT MOTEUR] {e}\n", "err")))

        threading.Thread(target=worker, daemon=True).start()

    def action_update_interval(self):
        val = self.ent_interval.get().strip()
        try:
            f_val = float(val)
            if f_val < 0: raise ValueError
            self.save_interval = f_val
            self.log_to_area(self.txt_serial, f"[CONFIG] Fréquence de capture changée à : {self.save_interval}s\n", "bdd")
        except ValueError:
            messagebox.showerror("Erreur de Saisie", "Entrez un format numérique positif.")

    def action_fetch_last_db(self):
        """Récupère l'affichage des 25 derniers logs de la table distance"""
        def worker():
            try:
                conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, connect_timeout=3)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM distance ORDER BY id DESC LIMIT 25")
                rows = cursor.fetchall()
                cursor.close()
                conn.close()

                self.txt_db.config(state=tk.NORMAL)
                self.txt_db.delete("1.0", tk.END)
                if not rows:
                    self.txt_db.insert(tk.END, "--- Aucune donnée capturée dans la table 'distance' ---\n", "warn")
                else:
                    for row in reversed(rows):
                        self.txt_db.insert(tk.END, f"📦 SQL Donnée -> {row}\n", "default")
                self.txt_db.see(tk.END)
                self.txt_db.config(state=tk.DISABLED)
            except mysql.connector.Error as e:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def action_clear_db(self):
        confirm = messagebox.askyesno("⚠️ TRUNCATE TABLE", "Confirmer la suppression définitive des données 'distance' ?")
        if not confirm: return
        def worker():
            try:
                conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
                cursor = conn.cursor()
                cursor.execute("TRUNCATE TABLE distance")
                conn.commit()
                cursor.close()
                conn.close()
                self.ui_queue.put(("log_ser", ("[BDD] Table distance vidée.\n", "err")))
                self.action_fetch_last_db()
            except mysql.connector.Error as e:
                self.ui_queue.put(("log_ser", (f"[ERREUR TRUNCATE] {e}\n", "err")))
        threading.Thread(target=worker, daemon=True).start()

    def log_to_area(self, text_widget, text, tag="default"):
        text_widget.config(state=tk.NORMAL)
        ts = time.strftime("%H:%M:%S", time.localtime()) + f".{int((time.time() % 1) * 1000):03d} "
        text_widget.insert(tk.END, f"[{ts}] ", "ts")
        text_widget.insert(tk.END, text, tag)
        text_widget.see(tk.END)
        text_widget.config(state=tk.DISABLED)

    def on_closing(self):
        self.stop_event.set()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = STM32DbCommanderGUI(root)
    root.after(500, app.action_fetch_last_db)
    root.mainloop()