import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial
import threading
import queue
import time
import sys

# ── Configuration du Port ─────────────────────────────────────────────────────
PORT = "COM3"
BAUD = 115200
TIMEOUT = 0.1

# ── Palette de Couleurs Modern Dark ───────────────────────────────────────────
BG_MAIN      = "#121214"  # Fond principal ultra-sombre
BG_PANEL     = "#1a1a1e"  # Fond des sections / cartes
BG_INPUT     = "#26262b"  # Fond des zones de saisie
FG_TEXT      = "#e1e1e6"  # Texte principal
FG_MUTED     = "#7c7c8a"  # Texte secondaire / Timestamps

COLOR_CYAN   = "#61afef"  # RX / Info
COLOR_GREEN  = "#98c379"  # ACK / OK
COLOR_RED    = "#e06c75"  # ERR / Alarmes
COLOR_YELLOW = "#e5c07b"  # WARN / Attention
COLOR_BLUE   = "#4dc4ff"  # TX / Commandes

class STM32CommanderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎛️ STM32 Nucleo Commander")
        self.root.geometry("1000x650")
        self.root.configure(bg=BG_MAIN)

        # États globaux
        self.tx_count = 0
        self.rx_count = 0
        self.ser = None
        self.stop_event = threading.Event()
        self.msg_queue = queue.Queue()

        # Style global des widgets
        self.setup_styles()

        # Construction de l'interface
        self.create_layout()

        # Connexion Série & Threads
        self.init_serial()

        # Liaison de la fermeture de fenêtre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Boucle de surveillance de la queue de messages (toutes les 50ms)
        self.root.after(50, self.process_queue)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=BG_MAIN, foreground=FG_TEXT)
        style.configure("TLabel", background=BG_PANEL, foreground=FG_TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG_PANEL, font=("Segoe UI", 11, "bold"))

        # Style des boutons
        style.configure("TButton", background=BG_INPUT, foreground=FG_TEXT, borderwidth=0, font=("Segoe UI", 10, "bold"), padding=8)
        style.map("TButton", background=[("active", "#323239")])

        style.configure("Action.TButton", background=COLOR_BLUE, foreground=BG_MAIN)
        style.map("Action.TButton", background=[("active", "#7ad5ff")])

        style.configure("Alert.TButton", background=COLOR_RED, foreground=FG_TEXT)
        style.map("Alert.TButton", background=[("active", "#ff8890")])

    def create_layout(self):
        # ── 1. BARRE SUPÉRIEURE (Infos Connexion) ──────────────────────────────
        top_bar = tk.Frame(self.root, bg=BG_PANEL, height=50, bd=0)
        top_bar.pack(fill=tk.X, padx=10, pady=5)

        lbl_info = ttk.Label(top_bar, text=f" PORT: {PORT}  |  BAUDRATE: {BAUD} bauds", font=("Consolas", 11, "bold"), background=BG_PANEL)
        lbl_info.pack(side=tk.LEFT, padx=15, pady=10)

        self.lbl_status = tk.Label(top_bar, text="CONNEXION EN COURS...", bg=BG_PANEL, fg=COLOR_YELLOW, font=("Segoe UI", 10, "bold"))
        self.lbl_status.pack(side=tk.RIGHT, padx=15)

        # Conteneur principal splité en 2 (Gauche = Commandes, Droite = Console)
        main_container = tk.Frame(self.root, bg=BG_MAIN)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ── 2. PANNEAU GAUCHE (Contrôles matériels) ────────────────────────────
        ctrl_panel = tk.Frame(main_container, bg=BG_PANEL, width=280)
        ctrl_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        ctrl_panel.pack_propagate(False)

        # Section Système
        self.create_panel_section(ctrl_panel, "📟 SYSTÈME")
        ttk.Button(ctrl_panel, text="PING (Test)", command=lambda: self.send_cmd("PING")).pack(fill=tk.X, padx=15, pady=5)
        ttk.Button(ctrl_panel, text="STATUS (État complet)", command=lambda: self.send_cmd("STATUS")).pack(fill=tk.X, padx=15, pady=5)

        # Section Actuateurs
        self.create_panel_section(ctrl_panel, "💡 PILOTAGE LED (PC3)")
        btn_led_on = ttk.Button(ctrl_panel, text="ALLUMER", style="Action.TButton", command=lambda: self.send_cmd("LED:ON"))
        btn_led_on.pack(fill=tk.X, padx=15, pady=4)
        btn_led_off = ttk.Button(ctrl_panel, text="ÉTEINDRE", command=lambda: self.send_cmd("LED:OFF"))
        btn_led_off.pack(fill=tk.X, padx=15, pady=4)

        # Section Moteur
        self.create_panel_section(ctrl_panel, "⚙️ MOTEUR PAS-À-PAS")
        motor_frame = tk.Frame(ctrl_panel, bg=BG_PANEL)
        motor_frame.pack(fill=tk.X, padx=15, pady=5)

        ttk.Label(motor_frame, text="Nbr de pas :", background=BG_PANEL).pack(side=tk.LEFT)
        self.ent_steps = tk.Entry(motor_frame, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0, width=10, font=("Segoe UI", 11))
        self.ent_steps.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0), ipady=3)
        self.ent_steps.insert(0, "512")

        ttk.Button(ctrl_panel, text="⏩ Avancer Moteur", command=self.send_motor_cmd).pack(fill=tk.X, padx=15, pady=5)

        # ── 3. PANNEAU DROIT (Console temps réel) ──────────────────────────────
        console_panel = tk.Frame(main_container, bg=BG_MAIN)
        console_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Zone de texte ScrolledText pour les logs
        self.txt_console = scrolledtext.ScrolledText(
            console_panel, bg=BG_PANEL, fg=FG_TEXT, insertbackground=FG_TEXT,
            bd=0, font=("Consolas", 10), highlightthickness=0
        )
        self.txt_console.pack(fill=tk.BOTH, expand=True)

        # Configuration des couleurs de tags pour le formatage du texte
        self.txt_console.tag_config("ts", foreground=FG_MUTED)
        self.txt_console.tag_config("default", foreground=FG_TEXT)
        self.txt_console.tag_config("err", foreground=COLOR_RED, font=("Consolas", 10, "bold"))
        self.txt_console.tag_config("warn", foreground=COLOR_YELLOW)
        self.txt_console.tag_config("ack", foreground=COLOR_GREEN, font=("Consolas", 10, "bold"))
        self.txt_console.tag_config("tx", foreground=COLOR_BLUE)
        self.txt_console.tag_config("cyan", foreground=COLOR_CYAN)

        # Barre d'envoi manuelle en bas de la console
        input_frame = tk.Frame(console_panel, bg=BG_MAIN)
        input_frame.pack(fill=tk.X, pady=(5, 0))

        self.ent_cmd = tk.Entry(input_frame, bg=BG_PANEL, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0, font=("Consolas", 11))
        self.ent_cmd.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=8, padx=(0, 5))
        self.ent_cmd.bind("<Return>", lambda event: self.send_manual_cmd())

        btn_send = ttk.Button(input_frame, text="ENVOYER", command=self.send_manual_cmd)
        btn_send.pack(side=tk.RIGHT, ipady=2)

        # ── 4. BARRE DE STATUT (Pied de page) ──────────────────────────────────
        self.status_bar = tk.Frame(self.root, bg=BG_PANEL, height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 5))

        self.lbl_tx_counter = ttk.Label(self.status_bar, text="TX: 0", font=("Consolas", 9))
        self.lbl_tx_counter.pack(side=tk.LEFT, padx=15, pady=3)

        self.lbl_rx_counter = ttk.Label(self.status_bar, text="RX: 0", font=("Consolas", 9))
        self.lbl_rx_counter.pack(side=tk.LEFT, padx=15, pady=3)

        self.lbl_last_ack = ttk.Label(self.status_bar, text="Dernier ACK: Aucun", font=("Consolas", 9), foreground=COLOR_GREEN)
        self.lbl_last_ack.pack(side=tk.RIGHT, padx=15, pady=3)

    def create_panel_section(self, parent, title):
        """Aide visuelle pour séparer les catégories dans le menu de gauche"""
        lbl = ttk.Label(parent, text=title, style="Title.TLabel")
        lbl.pack(fill=tk.X, padx=10, pady=(15, 5))
        sep = tk.Frame(parent, height=1, bg="#2d2d34", bd=0)
        sep.pack(fill=tk.X, padx=10, pady=(0, 10))

    # ── Gestion des événements Série / Threads ─────────────────────────────────
    def init_serial(self):
        try:
            self.ser = serial.Serial(
                port=PORT, baudrate=BAUD, bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                timeout=TIMEOUT, xonxoff=False, rtscts=False, dsrdtr=False
            )
            self.ser.rts = False
            self.ser.dtr = False

            self.lbl_status.config(text="● CONNECTÉ", fg=COLOR_GREEN)
            self.log_to_console(f"[SYSTEM] Connecté avec succès sur {PORT} ({BAUD} bauds)\n", "ack")

            # Start Reader Thread
            self.reader_thread = threading.Thread(target=self.serial_listen_loop, daemon=True)
            self.reader_thread.start()

        except serial.SerialException as e:
            self.lbl_status.config(text="● DÉCONNECTÉ (ERREUR)", fg=COLOR_RED)
            self.log_to_console(f"[ERREUR] Impossible d'ouvrir le port {PORT} : {e}\n", "err")
            messagebox.showerror("Erreur Port Série", f"Impossible d'ouvrir le port {PORT}.\nVérifiez votre carte STM32.")

    def serial_listen_loop(self):
        """Lit en continu les trames du STM32 (Threadé)"""
        buffer = b""
        while not self.stop_event.is_set() and self.ser and self.ser.is_open:
            try:
                chunk = self.ser.read(self.ser.in_waiting or 1)
                if not chunk:
                    continue
                buffer += chunk
                while b"\n" in buffer:
                    line_bytes, buffer = buffer.split(b"\n", 1)
                    line = line_bytes.decode("utf-8", errors="replace").rstrip("\r")
                    if line:
                        self.msg_queue.put(line)
            except Exception:
                break

    def process_queue(self):
        """Vide la file d'attente et met à jour l'IHM graphique de façon thread-safe"""
        while not self.msg_queue.empty():
            try:
                line = self.msg_queue.get_nowait()
                self.rx_count += 1
                self.lbl_rx_counter.config(text=f"RX: {self.rx_count}")

                # Détection du tag de couleur selon la réponse du microcontrôleur
                tag = "cyan"
                if line.startswith("[ERR]"): tag = "err"
                elif line.startswith("[WARN]"): tag = "warn"
                elif line.startswith("[ACK]"):
                    tag = "ack"
                    self.lbl_last_ack.config(text=f"Dernier ACK: {line}")
                elif line.startswith("[HB]") or line.startswith("[DBG]"): tag = "ts"
                elif line.startswith("[CMD]"): tag = "tx"
                elif "PONG" in line: tag = "ack"

                self.log_to_console(line + "\n", tag)
            except queue.Empty:
                break

        # Se relance automatiquement toutes les 50 millisecondes
        self.root.after(50, self.process_queue)

    # ── Actions UI ────────────────────────────────────────────────────────────
    def send_cmd(self, cmd_string):
        """Envoie une commande brute au STM32"""
        if not self.ser or not self.ser.is_open:
            self.log_to_console("[ERREUR GUI] Impossible d'envoyer, port fermé.\n", "err")
            return

        try:
            self.tx_count += 1
            self.lbl_tx_counter.config(text=f"TX: {self.tx_count}")

            # Envoi physique sur l'UART
            raw = (cmd_string.strip() + "\n").encode("utf-8")
            self.ser.write(raw)
            self.ser.flush()

            # Log l'envoi dans la console locale
            self.log_to_console(f"[TX #{self.tx_count}] {cmd_string}\n", "tx")
        except Exception as e:
            self.log_to_console(f"[ERREUR D'ENVOI] {e}\n", "err")

    def send_manual_cmd(self):
        cmd = self.ent_cmd.get().strip()
        if cmd:
            self.send_cmd(cmd)
            self.ent_cmd.delete(0, tk.END)

    def send_motor_cmd(self):
        steps = self.ent_steps.get().strip()
        if steps.isdigit():
            self.send_cmd(f"MOTOR:{steps}")
        else:
            messagebox.showwarning("Saisie invalide", "Veuillez entrer un nombre entier de pas.")

    def log_to_console(self, text, tag="default"):
        """Ajoute du texte horodaté proprement dans le bloc terminal graphique"""
        self.txt_console.config(state=tk.NORMAL)

        # Insertion du Timestamp
        current_ts = time.strftime("%H:%M:%S", time.localtime()) + f".{int((time.time() % 1) * 1000):03d} "
        self.txt_console.insert(tk.END, f"[{current_ts}] ", "ts")

        # Insertion du message typé
        self.txt_console.insert(tk.END, text, tag)

        # Auto-scroll vers le bas
        self.txt_console.see(tk.END)
        self.txt_console.config(state=tk.DISABLED)

    def on_closing(self):
        """Fermeture propre de l'application et libération des ressources"""
        self.stop_event.set()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.root.destroy()

# ── Lancement de l'IHM ────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = STM32CommanderGUI(root)
    root.mainloop()