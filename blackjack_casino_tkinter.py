import tkinter as tk
from tkinter import ttk, messagebox
import random

# Constantes de Diseño y Colores (Estilo Casino Premium - Frosted Glass Luxe)
COLOR_BACKGROUND = "#0b3d2e"  # Tapete verde esmeralda profundo de alta gama
COLOR_CARD_BACK = "#043d2e"    # Reverso de carta de la casa real
COLOR_DEALER_BG = "#052f24"    # Panel del Crupier
COLOR_PLAYER_BG = "#0c4c3a"    # Paneles elegantes para jugadores
COLOR_CONTROLS = "#031d17"     # Barra inferior de alta fidelidad
COLOR_TEXT_MAIN = "#ffffff"    # Letras blancas
COLOR_TEXT_GOLD = "#f59e0b"    # Destacados y premios ganados (Ámbar)
COLOR_TEXT_RED = "#ef4444"     # Corazones, diamantes y pérdidas (Rojo)
COLOR_CARD_BG = "#ffffff"      # Fondo brillante de las cartas
COLOR_ACCENT = "#10b981"       # Verde brillante para elementos activos esmeralda

SUITS = ["♥", "♦", "♣", "♠"]
SUIT_COLORS = {
    "♥": COLOR_TEXT_RED,
    "♦": COLOR_TEXT_RED,
    "♣": "#1c1917",
    "♠": "#1c1917"
}
VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        if value in ["J", "Q", "K"]:
            self.score_value = 10
        elif value == "A":
            self.score_value = 11
        else:
            self.score_value = int(value)

class BlackjackController:
    def __init__(self, root):
        self.root = root
        self.root.title("Casino Grand Luxe Blackjack - Simulator & AI")
        self.root.geometry("1180x740")
        self.root.configure(bg=COLOR_BACKGROUND)
        self.root.minsize(1080, 700)

        # Control robusto de hilos con temporizador de Tkinter
        self.active_timers = []

        # Estado del juego
        self.deck = []
        self.game_mode = tk.StringVar(value="human")  # "human", "simulation", "two_humans", "three_humans"
        self.game_state = "idle"  # idle, p1_turn, p2_turn, p3_turn, dealer_turn, ended
        
        self.dealer_cards = []
        self.dealer_score = 0
        
        # Jugadores
        self.players = [
            {"id": 1, "name": "Jugador 1 (H)", "type": "human", "cards": [], "score": 0, "status": ""},
            {"id": 2, "name": "Jugador 2 (IA)", "type": "ai", "cards": [], "score": 0, "status": ""},
            {"id": 3, "name": "Jugador 3 (IA)", "type": "ai", "cards": [], "score": 0, "status": ""}
        ]
        
        # Construir Interfaz de casino pulida
        self.create_widgets()
        self.reset_table()

    def schedule_action(self, delay, action):
        """Registra temporizadores de forma limpia para evitar colisiones lógicas al reiniciar."""
        tid = self.root.after(delay, action)
        self.active_timers.append(tid)
        return tid

    def cancel_all_timers(self):
        """Cancela todos los bucles en cola cuando se reajusta la mesa o inicia nueva ronda."""
        for tid in self.active_timers:
            try:
                self.root.after_cancel(tid)
            except Exception:
                pass
        self.active_timers = []

    def create_widgets(self):
        # 1. Cabecera superior refinada (Logo con estilo insignia digital)
        top_bar = tk.Frame(self.root, bg=COLOR_BACKGROUND, height=70)
        top_bar.pack(fill=tk.X, padx=15, pady=10)
        
        # Insignia de palo
        picas_lbl = tk.Label(top_bar, text="♠", font=("Helvetica", 24, "bold"), fg=COLOR_ACCENT, bg=COLOR_BACKGROUND)
        picas_lbl.pack(side=tk.LEFT, padx=(10, 5))
        
        label_title = tk.Label(top_bar, text="GRAND LUXE BLACKJACK", font=("Arial", 18, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BACKGROUND)
        label_title.pack(side=tk.LEFT, pady=10)
        
        # Selector de Modos de Juego con Bordes Suaves
        mode_frame = tk.LabelFrame(top_bar, text=" CONFIGURACIÓN DE MODO ", fg=COLOR_TEXT_GOLD, bg=COLOR_BACKGROUND, font=("Helvetica", 9, "bold"))
        mode_frame.pack(side=tk.RIGHT, padx=15)
        
        self.mode_radios = []
        modes_spec = [
            ("Humano vs 2 IA", "human"),
            ("Simulación (3 IA)", "simulation"),
            ("2 Humanos vs 1 IA", "two_humans"),
            ("3 Humanos", "three_humans")
        ]
        
        for text, val in modes_spec:
            rb = tk.Radiobutton(
                mode_frame, text=text, variable=self.game_mode, value=val, 
                command=self.on_mode_change, fg=COLOR_TEXT_MAIN, bg=COLOR_BACKGROUND, 
                selectcolor=COLOR_CONTROLS, font=("Helvetica", 9, "bold"), activebackground=COLOR_BACKGROUND, activeforeground=COLOR_TEXT_GOLD
            )
            rb.pack(side=tk.LEFT, padx=10, pady=8)
            self.mode_radios.append(rb)

        # 2. Zona Central: Tablero del Casino (Dealer arriba, jugadores distribuidos abajo)
        self.main_table = tk.Frame(self.root, bg=COLOR_BACKGROUND)
        self.main_table.pack(fill=tk.BOTH, expand=True, padx=25, pady=5)

        # Panel del Crupier (Dealer)
        self.dealer_frame = tk.Frame(self.main_table, bg=COLOR_DEALER_BG, bd=1, relief=tk.SOLID)
        self.dealer_frame.pack(fill=tk.X, pady=(5, 15), ipady=12)
        
        self.dealer_header = tk.Label(self.dealer_frame, text="CRUPIER (DEALER)", font=("Helvetica", 11, "bold"), fg=COLOR_TEXT_GOLD, bg=COLOR_DEALER_BG)
        self.dealer_header.pack(anchor=tk.W, padx=20, pady=(5, 2))
        
        self.dealer_score_label = tk.Label(self.dealer_frame, text="Puntos: -", font=("Helvetica", 10, "bold"), fg="#94a3b8", bg=COLOR_DEALER_BG)
        self.dealer_score_label.pack(anchor=tk.W, padx=20)
        
        self.dealer_cards_container = tk.Frame(self.dealer_frame, bg=COLOR_DEALER_BG)
        self.dealer_cards_container.pack(fill=tk.X, padx=20, pady=8)

        # Panel de Jugadores (Contenedor de 3 Asientos)
        self.players_container = tk.Frame(self.main_table, bg=COLOR_BACKGROUND)
        self.players_container.pack(fill=tk.BOTH, expand=True, pady=5)

        self.player_frames = []
        self.player_name_labels = []
        self.player_score_labels = []
        self.player_status_labels = []
        self.player_cards_containers = []

        for i in range(3):
            p_frame = tk.Frame(self.players_container, bg=COLOR_PLAYER_BG, bd=1, relief=tk.SOLID)
            p_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
            
            # Etiqueta de resultado (WIN, BUST, etc)
            status_lbl = tk.Label(p_frame, text="", font=("Helvetica", 10, "bold"), fg=COLOR_TEXT_GOLD, bg=COLOR_PLAYER_BG)
            status_lbl.pack(pady=(10, 5))
            
            name_lbl = tk.Label(p_frame, text=f"Jugador {i+1}", font=("Helvetica", 11, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_PLAYER_BG)
            name_lbl.pack()
            
            score_lbl = tk.Label(p_frame, text="Puntos: 0", font=("Helvetica", 10, "bold"), fg="#94a3b8", bg=COLOR_PLAYER_BG)
            score_lbl.pack(pady=3)
            
            cards_container = tk.Frame(p_frame, bg=COLOR_PLAYER_BG)
            cards_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            self.player_frames.append(p_frame)
            self.player_name_labels.append(name_lbl)
            self.player_score_labels.append(score_lbl)
            self.player_status_labels.append(status_lbl)
            self.player_cards_containers.append(cards_container)

        # 3. Zona de Control (Barra inferior con botones profesionales de Casino)
        control_bar = tk.Frame(self.root, bg=COLOR_CONTROLS, height=100)
        control_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        style = ttk.Style()
        style.theme_use('default')
        
        # Estilo para botón Iniciar (Dorado elegante)
        style.configure('Casino.TButton', font=('Helvetica', 10, 'bold'), foreground='#ffffff', background='#059669')
        style.map('Casino.TButton', background=[('active', '#10b981'), ('disabled', '#1f2937')])
        
        # Estilo para Pedir Carta (Azul esmeralda)
        style.configure('Action.TButton', font=('Helvetica', 10, 'bold'), foreground='#ffffff', background='#0284c7')
        style.map('Action.TButton', background=[('active', '#38bdf8'), ('disabled', '#1f2937')])

        # Estilo para Plantarse (Gris neutro de alta gama)
        style.configure('Danger.TButton', font=('Helvetica', 10, 'bold'), foreground='#000000', background='#f3f4f6')
        style.map('Danger.TButton', background=[('active', '#e5e7eb'), ('disabled', '#1f2937')])

        # Contenedor interno de botones
        buttons_frame = tk.Frame(control_bar, bg=COLOR_CONTROLS)
        buttons_frame.pack(side=tk.LEFT, padx=30, pady=20)

        # Iniciar Ronda
        self.btn_start = ttk.Button(buttons_frame, text="Iniciar Ronda", style='Casino.TButton', command=self.start_round)
        self.btn_start.pack(side=tk.LEFT, padx=10)

        # Pedir Carta
        self.btn_hit = ttk.Button(buttons_frame, text="Pedir Carta (Hit)", style='Action.TButton', command=self.human_hit)
        self.btn_hit.pack(side=tk.LEFT, padx=1)

        # Plantarse
        self.btn_stand = ttk.Button(buttons_frame, text="Plantarse (Stand)", style='Danger.TButton', command=self.human_stand)
        self.btn_stand.pack(side=tk.LEFT, padx=10)
        
        # Desactivados por defecto
        self.btn_hit.state(['disabled'])
        self.btn_stand.state(['disabled'])

        # Consola Informativa lateral
        self.lbl_info = tk.Label(control_bar, text="Selecciona un modo de juego y presiona Iniciar Ronda", font=("Helvetica", 10, "bold"), fg="#e2e8f0", bg=COLOR_CONTROLS)
        self.lbl_info.pack(side=tk.RIGHT, padx=30, pady=25)

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius=8, **kwargs):
        """Dibuja un rectángulo con bordes curvos y suavizados de alta calidad en Tkinter."""
        points = [
            x1+radius, y1, x1+radius, y1,
            x2-radius, y1, x2-radius, y1,
            x2, y1, x2, y1+radius,
            x2, y1+radius, x2, y2-radius,
            x2, y2-radius, x2, y2,
            x2-radius, y2, x2-radius, y2,
            x1+radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius,
            x1, y2-radius, x1, y1+radius,
            x1, y1+radius, x1, y1
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def draw_card_widget(self, parent, value, suit, face_up=True):
        """Crea una hermosa carta con esquinas curvadas y símbolos claros en un Canvas."""
        card_canvas = tk.Canvas(parent, width=76, height=110, bg=COLOR_PLAYER_BG, highlightthickness=0)
        card_canvas.pack(side=tk.LEFT, padx=6)
        
        if not face_up:
            # Reverso de carta premium con diseño real
            self.draw_rounded_rect(card_canvas, 1, 1, 75, 109, radius=10, fill=COLOR_CARD_BACK, outline="#059669")
            # Símbolo central dorado con corona
            card_canvas.create_text(38, 55, text="♠CASA", fill=COLOR_TEXT_GOLD, font=("Helvetica", 10, "bold"), justify=tk.CENTER)
            return card_canvas
            
        # Anverso con borde suavizado blanco puro
        self.draw_rounded_rect(card_canvas, 1, 1, 75, 109, radius=10, fill=COLOR_CARD_BG, outline="#cbd5e1")
        
        # Color según el palo
        suit_col = SUIT_COLORS.get(suit, "#000000")
        
        # Esquina superior izquierda
        card_canvas.create_text(15, 16, text=value, font=("Helvetica", 12, "bold"), fill=suit_col)
        card_canvas.create_text(15, 30, text=suit, font=("Helvetica", 10), fill=suit_col)
        
        # Gran símbolo principal centrado
        card_canvas.create_text(38, 58, text=suit, font=("Helvetica", 32), fill=suit_col)
        
        # Esquina inferior derecha (Simulamos rotación)
        card_canvas.create_text(61, 94, text=value, font=("Helvetica", 11, "bold"), fill=suit_col)
        card_canvas.create_text(61, 80, text=suit, font=("Helvetica", 10), fill=suit_col)
        
        return card_canvas

    def on_mode_change(self):
        self.cancel_all_timers()
        mode = self.game_mode.get()
        if mode == "human":
            self.players[0]["name"] = "Jugador 1 (H)"
            self.players[0]["type"] = "human"
            self.players[1]["name"] = "Jugador 2 (IA)"
            self.players[1]["type"] = "ai"
            self.players[2]["name"] = "Jugador 3 (IA)"
            self.players[2]["type"] = "ai"
        elif mode == "simulation":
            self.players[0]["name"] = "Jugador 1 (IA)"
            self.players[0]["type"] = "ai"
            self.players[1]["name"] = "Jugador 2 (IA)"
            self.players[1]["type"] = "ai"
            self.players[2]["name"] = "Jugador 3 (IA)"
            self.players[2]["type"] = "ai"
        elif mode == "two_humans":
            self.players[0]["name"] = "Jugador 1 (H)"
            self.players[0]["type"] = "human"
            self.players[1]["name"] = "Jugador 2 (H)"
            self.players[1]["type"] = "human"
            self.players[2]["name"] = "Jugador 3 (IA)"
            self.players[2]["type"] = "ai"
        elif mode == "three_humans":
            self.players[0]["name"] = "Jugador 1 (H)"
            self.players[0]["type"] = "human"
            self.players[1]["name"] = "Jugador 2 (H)"
            self.players[1]["type"] = "human"
            self.players[2]["name"] = "Jugador 3 (H)"
            self.players[2]["type"] = "human"
            
        self.reset_table()
        self.lbl_info.config(text=f"Modo cambiado.")

    def reset_table(self):
        self.cancel_all_timers()
        
        # Limpiar elementos del Canvas
        for widget in self.dealer_cards_container.winfo_children():
            widget.destroy()
        
        for i in range(3):
            for widget in self.player_cards_containers[i].winfo_children():
                widget.destroy()
            self.player_status_labels[i].config(text="", fg=COLOR_TEXT_MAIN)
            self.player_score_labels[i].config(text="Puntos: 0")
            self.player_frames[i].config(bg=COLOR_PLAYER_BG)
            self.player_name_labels[i].config(text=self.players[i]["name"])

        self.dealer_score_label.config(text="Puntos: -")
        self.dealer_frame.config(bg=COLOR_DEALER_BG)
        
        # Resetear variables internas
        self.dealer_cards = []
        self.dealer_score = 0
        for p in self.players:
            p["cards"] = []
            p["score"] = 0
            p["status"] = ""

    def initialize_deck(self):
        """Inicializa un mazo tradicional de 52 cartas barajadas."""
        self.deck = []
        for suit in SUITS:
            for val in VALUES:
                self.deck.append(Card(val, suit))
        random.shuffle(self.deck)

    def draw_card(self):
        """Previene caídas por IndexError si el mazo se drena re-barajando automáticamente."""
        if len(self.deck) < 5:
            self.initialize_deck()
        return self.deck.pop()

    def calculate_hand_score(self, cards):
        score = 0
        aces = 0
        for card in cards:
            score += card.score_value
            if card.value == "A":
                aces += 1
        
        # Ajustar el valor de los Ases de 11 a 1 de forma inteligente si se pasa de 21
        while score > 21 and aces > 0:
            score -= 10
            aces -= 1
        return score

    def update_player_ui(self, index):
        container = self.player_cards_containers[index]
        for widget in container.winfo_children():
            widget.destroy()
            
        p = self.players[index]
        
        # Distribuir las cartas faneadas hacia el lado
        for card in p["cards"]:
            self.draw_card_widget(container, card.value, card.suit, face_up=True)
            
        p["score"] = self.calculate_hand_score(p["cards"])
        self.player_score_labels[index].config(text=f"Puntos: {p['score']}")
        
        # Añadir un resaltado visual nítido para saber quién es el del turno activo
        if self.game_state == f"p{index+1}_turn":
            self.player_frames[index].config(bg="#115e50")  # Resaltado esmeralda
        else:
            self.player_frames[index].config(bg=COLOR_PLAYER_BG)

    def update_dealer_ui(self, hide_first_card=True):
        container = self.dealer_cards_container
        for widget in container.winfo_children():
            widget.destroy()
            
        for i, card in enumerate(self.dealer_cards):
            if i == 0 and hide_first_card:
                self.draw_card_widget(container, card.value, card.suit, face_up=False)
            else:
                self.draw_card_widget(container, card.value, card.suit, face_up=True)
                
        if hide_first_card:
            # Puntos parciales de la carta descubierta
            if len(self.dealer_cards) > 1:
                visible_score = self.dealer_cards[1].score_value
                self.dealer_score_label.config(text=f"Puntos Visibles: {visible_score}")
            else:
                self.dealer_score_label.config(text="Puntos: -")
        else:
            self.dealer_score = self.calculate_hand_score(self.dealer_cards)
            self.dealer_score_label.config(text=f"Puntos: {self.dealer_score}")

    def start_round(self):
        self.cancel_all_timers()
        
        # Desactivar botones de configuración al iniciar para evitar hilos concurrentes
        self.btn_start.state(['disabled'])
        for radial in self.mode_radios:
            radial.config(state=tk.DISABLED)
        
        self.reset_table()
        self.initialize_deck()
        
        self.lbl_info.config(text="Mezclando y repartiendo cartas iniciales...")
        
        # Repartir 2 cartas a todos secuencialmente
        for _ in range(2):
            for i in range(3):
                self.players[i]["cards"].append(self.draw_card())
            self.dealer_cards.append(self.draw_card())
            
        # Actualizar la mesa visualmente
        for i in range(3):
            self.update_player_ui(i)
        self.update_dealer_ui(hide_first_card=True)
        
        # Iniciar el turno del primer jugador
        self.next_turn(1)

    def next_turn(self, player_idx):
        if player_idx <= 3:
            p_idx = player_idx - 1
            curr_player = self.players[p_idx]
            self.game_state = f"p{player_idx}_turn"
            
            # Actualizar resaltado e indicadores visuales de turnos
            for i in range(3):
                self.update_player_ui(i)
                
            self.lbl_info.config(text=f"Turno de: {curr_player['name']}")
            
            # Verificar si hay Blackjack natural (21 exactos al recibir)
            score = self.calculate_hand_score(curr_player["cards"])
            if score == 21:
                curr_player["status"] = "blackjack"
                self.player_status_labels[p_idx].config(text="BLACKJACK Natural! ♠", fg=COLOR_TEXT_GOLD)
                self.schedule_action(1200, lambda: self.next_turn(player_idx + 1))
                return

            if curr_player["type"] == "human":
                # Activar mandos para el humano
                self.btn_hit.state(['!disabled'])
                self.btn_stand.state(['!disabled'])
            else:
                # Simular tiempo de pensamiento de la IA
                self.btn_hit.state(['disabled'])
                self.btn_stand.state(['disabled'])
                self.schedule_action(1200, lambda: self.process_ai_turn(p_idx))
        else:
            # Turno del Crupier
            self.game_state = "dealer_turn"
            for i in range(3):
                self.player_frames[i].config(bg=COLOR_PLAYER_BG)
            self.lbl_info.config(text="Turno de la Casa / Dealer...")
            self.schedule_action(1000, self.process_dealer_turn)

    def get_active_player_index(self):
        if self.game_state == "p1_turn":
            return 0
        elif self.game_state == "p2_turn":
            return 1
        elif self.game_state == "p3_turn":
            return 2
        return -1

    def human_hit(self):
        p_idx = self.get_active_player_index()
        if p_idx == -1:
            return
        p = self.players[p_idx]
        if p["type"] != "human":
            return

        p["cards"].append(self.draw_card())
        self.update_player_ui(p_idx)
        
        if p["score"] > 21:
            p["status"] = "busted"
            self.player_status_labels[p_idx].config(text="TE PASASTE (>21) ❌", fg=COLOR_TEXT_RED)
            self.btn_hit.state(['disabled'])
            self.btn_stand.state(['disabled'])
            self.schedule_action(1200, lambda: self.next_turn(p_idx + 2))
        elif p["score"] == 21:
            self.human_stand()

    def human_stand(self):
        p_idx = self.get_active_player_index()
        if p_idx == -1:
            return
        p = self.players[p_idx]
        if p["type"] != "human":
            return

        p["status"] = "stood"
        self.btn_hit.state(['disabled'])
        self.btn_stand.state(['disabled'])
        self.next_turn(p_idx + 2)

    def process_ai_turn(self, p_idx):
        p = self.players[p_idx]
        score = self.calculate_hand_score(p["cards"])
        
        # Inteligencia de la IA: pide con menos de 16, se planta con 16 o más
        if score < 16:
            p["cards"].append(self.draw_card())
            self.update_player_ui(p_idx)
            new_score = p["score"]
            self.lbl_info.config(text=f"{p['name']} decide pedir carta...")
            
            if new_score > 21:
                p["status"] = "busted"
                self.player_status_labels[p_idx].config(text="PASADO (>21) ❌", fg=COLOR_TEXT_RED)
                self.schedule_action(1200, lambda: self.next_turn(p_idx + 2))
            else:
                self.schedule_action(1000, lambda: self.process_ai_turn(p_idx))
        else:
            p["status"] = "stood"
            self.lbl_info.config(text=f"{p['name']} se planta con {score} puntos.")
            self.player_status_labels[p_idx].config(text=f"Se Planta ({score})", fg="#94a3b8")
            self.schedule_action(1200, lambda: self.next_turn(p_idx + 2))

    def process_dealer_turn(self):
        self.update_dealer_ui(hide_first_card=False)
        self.dealer_score = self.calculate_hand_score(self.dealer_cards)
        
        # Reglas obligatorias de casino de la casa: Pide con 16 o menos, se planta con 17 o más.
        if self.dealer_score < 17:
            self.lbl_info.config(text="Dealer pide carta para llegar a 17...")
            self.dealer_cards.append(self.draw_card())
            self.update_dealer_ui(hide_first_card=False)
            self.schedule_action(1200, self.process_dealer_turn)
        else:
            if self.dealer_score > 21:
                self.lbl_info.config(text=f"¡Dealer se ha pasado de 21 con {self.dealer_score} puntos!")
            else:
                self.lbl_info.config(text=f"Dealer se planta oficialmente con {self.dealer_score} puntos.")
            self.schedule_action(1200, self.evaluate_results)

    def evaluate_results(self):
        d_score = self.dealer_score
        
        for i, p in enumerate(self.players):
            p_score = p["score"]
            
            if p["status"] == "busted":
                p["status"] = "lost"
                self.player_status_labels[i].config(text="PERDIÓ (Bust) ❌", fg=COLOR_TEXT_RED)
                self.player_frames[i].config(bg="#451a03")  # Sutil tono marrón/rojo apagado
            elif d_score > 21:
                p["status"] = "won"
                self.player_status_labels[i].config(text="¡GANÓ! 🏆", fg=COLOR_TEXT_GOLD)
                self.player_frames[i].config(bg="#022c22")  # Tono verde bosque oscuro
            elif p_score > d_score:
                p["status"] = "won"
                self.player_status_labels[i].config(text="¡GANÓ! 🏆", fg=COLOR_TEXT_GOLD)
                self.player_frames[i].config(bg="#022c22")
            elif p_score < d_score:
                p["status"] = "lost"
                self.player_status_labels[i].config(text="PERDIÓ ❌", fg=COLOR_TEXT_RED)
                self.player_frames[i].config(bg="#451a03")
            else:
                p["status"] = "push"
                self.player_status_labels[i].config(text="EMPATE 🤝", fg="#cbd5e1")
                self.player_frames[i].config(bg="#1e293b")

        self.lbl_info.config(text="Ronda completada de forma segura. ¡Inicia otra cuando quieras!")
        
        # Habilitar controles para cambiar modos o re-iniciar
        self.btn_start.state(['!disabled'])
        for radial in self.mode_radios:
            radial.config(state=tk.NORMAL)
        self.game_state = "ended"

if __name__ == "__main__":
    root = tk.Tk()
    app = BlackjackController(root)
    root.mainloop()
