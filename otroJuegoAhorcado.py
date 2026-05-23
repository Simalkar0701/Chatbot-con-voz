import tkinter as tk
from tkinter import ttk, messagebox
import random

# Constantes de Diseño y Colores (Estilo Casino Premium - El Ahorcado Luxe)
COLOR_BACKGROUND = "#0b3d2e"  # Tapete verde esmeralda profundo de mesa de juego
COLOR_CONTAINER = "#052f24"   # Panel oscuro para contenedor principal
COLOR_INPUT_BG = "#0c4c3a"    # Teclado y paneles activos
COLOR_CONTROLS = "#031d17"    # Barra inferior de comando
COLOR_TEXT_MAIN = "#ffffff"   # Letras blancas principales
COLOR_TEXT_GOLD = "#f59e0b"   # Destacados brillos áureos
COLOR_TEXT_RED = "#ef4444"    # Fallos o peligro (Rojo)
COLOR_LETTER_BOX = "#ffffff"  # Cajas de pistas
COLOR_ACCENT = "#10b981"      # Verde vibrante activo

WORD_BANK = [
    {"word": "COMPUTADORA", "category": "Tecnología", "hint": "Máquina electrónica para procesar datos jerarquizados."},
    {"word": "PROGRAMACION", "category": "Tecnología", "hint": "Arte de escribir instrucciones lógicas de código para ordenadores."},
    {"word": "INTELIGENCIA", "category": "Tecnología", "hint": "Capacidad de razonar, aprender y resolver problemas complejos."},
    {"word": "ALGORITMO", "category": "Tecnología", "hint": "Conjunto de pasos lógicos bien secuenciados para resolver una tarea."},
    {"word": "INTERNET", "category": "Tecnología", "hint": "Red informática mundial para la comunicación de computadoras."},
    {"word": "BASE DE DATOS", "category": "Tecnología", "hint": "Almacén de información digital estructurada de fácil acceso."},
    {"word": "ASTRONAUTA", "category": "Ciencia & Cosmos", "hint": "Persona capacitada para viajar tripulado al espacio exterior."},
    {"word": "GRAVEDAD", "category": "Ciencia & Cosmos", "hint": "Fuerza invisible de atracción mutua de las cosas con masa."},
    {"word": "PLANETA", "category": "Ciencia & Cosmos", "hint": "Cuerpo celeste denso que gira en órbita a una estrella."},
    {"word": "GALAXIA", "category": "Ciencia & Cosmos", "hint": "Enorme conjunto interactivo de estrellas, polvos, nebulosas y gas."},
    {"word": "HOLLYWOOD", "category": "Cine & Arte", "hint": "La zona y meca del cine tradicional y comercial estadounidense."},
    {"word": "DIRECTOR", "category": "Cine & Arte", "hint": "La mente creativa encargada de orquestar la filmación."},
    {"word": "PALOMITAS", "category": "Cine & Arte", "hint": "Aperitivo clásico indispensable de grano tostado de maíz."},
    {"word": "MADAGASCAR", "category": "Geografía", "hint": "Nación isleña en África famosa por la biodiversidad exótica."},
    {"word": "ARGENTINA", "category": "Geografía", "hint": "Nación sudamericana del tango, la Patagonia y los glaciares."},
    {"word": "EGIPTO", "category": "Geografía", "hint": "Tierra desértica milenaria de faraones, jeroglíficos y pirámides."},
    {"word": "BALONCESTO", "category": "Deportes & Ocio", "hint": "Juego de equipo donde se encesta una pelota naranja en un aro elevado."},
    {"word": "ATLETISMO", "category": "Deportes & Ocio", "hint": "Suma de disciplinas de carreras, saltos y lanzamientos."}
]

SPANISH_FREQ_ORDER = [
    'E', 'A', 'O', 'S', 'R', 'N', 'I', 'D', 'L', 'C', 'T', 'U', 'M', 'P', 'B', 'G', 'V', 'Y', 'Q', 'H', 'F', 'Z', 'J', 'Ñ', 'X', 'W', 'K'
]

class HangmanController:
    def __init__(self, root):
        self.root = root
        self.root.title("El Ahorcado Premium - Casino Showcase & Solver AI")
        self.root.geometry("1150x780")
        self.root.configure(bg=COLOR_BACKGROUND)
        self.root.minsize(1050, 720)

        # Variables de estado
        self.secret_word = ""
        self.category = ""
        self.hint = ""
        self.guessed_letters = []
        self.attempts = 0
        self.max_attempts = 8  # Depende de la dificultad
        
        self.difficulty = tk.StringVar(value="easy")  # easy (8), medium (6), hard (5)
        self.game_mode = tk.StringVar(value="solo_human")  # solo_human, human_vs_ai, simulation_ai, pass_and_play
        self.game_state = "idle"  # idle, playing, won, lost
        self.ai_fallibility = tk.IntVar(value=30)

        # Jugadores del Casino
        self.players = [
            {"name": "Jugador 1 (H)", "score": 0, "type": "human", "is_active": True},
            {"name": "Jugador 2 (IA)", "score": 0, "type": "ai", "is_active": True},
            {"name": "Jugador 3 (IA)", "score": 0, "type": "ai", "is_active": True}
        ]
        self.current_player_idx = 0
        self.active_timers = []

        # Interfaz de Usuario
        self.create_widgets()
        self.on_mode_or_difficulty_change()

    def schedule_action(self, delay, action):
        tid = self.root.after(delay, action)
        self.active_timers.append(tid)
        return tid

    def cancel_all_timers(self):
        for tid in self.active_timers:
            try:
                self.root.after_cancel(tid)
            except Exception:
                pass
        self.active_timers = []

    def create_widgets(self):
        # 1. Cabecera Premium
        top_bar = tk.Frame(self.root, bg=COLOR_BACKGROUND, height=75)
        top_bar.pack(fill=tk.X, padx=20, pady=10)

        icon_lbl = tk.Label(top_bar, text="☠", font=("Arial", 26, "bold"), fg=COLOR_TEXT_GOLD, bg=COLOR_BACKGROUND)
        icon_lbl.pack(side=tk.LEFT, padx=(10, 10))

        title_lbl = tk.Label(top_bar, text="EL AHORCADO PREMIUM", font=("Arial", 20, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BACKGROUND)
        title_lbl.pack(side=tk.LEFT, pady=10)

        # Panel de Configuración de Modos en Cabecera
        config_frame = tk.LabelFrame(top_bar, text=" PANEL DE AJUSTES CASINO ", font=("Helvetica", 8, "bold"), fg=COLOR_TEXT_GOLD, bg=COLOR_BACKGROUND)
        config_frame.pack(side=tk.RIGHT, padx=10)

        # Modo de Juego
        mode_menu_lbl = tk.Label(config_frame, text="Modo:", font=("Helvetica", 9, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BACKGROUND)
        mode_menu_lbl.pack(side=tk.LEFT, padx=(10, 5))
        
        self.mode_combo = ttk.Combobox(
            config_frame, textvariable=self.game_mode, state="readonly", width=18,
            values=["Solitario (H)", "Humano vs 2 IA", "Simulación (3 IA)", "3 Humanos (P&J)"]
        )
        self.mode_combo.pack(side=tk.LEFT, padx=5, pady=5)
        self.mode_combo.bind("<<ComboboxSelected>>", lambda e: self.on_mode_or_difficulty_change())

        # Dificultad
        diff_lbl = tk.Label(config_frame, text="Dificultad:", font=("Helvetica", 9, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BACKGROUND)
        diff_lbl.pack(side=tk.LEFT, padx=(15, 5))

        self.diff_combo = ttk.Combobox(
            config_frame, textvariable=self.difficulty, state="readonly", width=10,
            values=["Fácil (8)", "Medio (6)", "Difícil (5)"]
        )
        self.diff_combo.pack(side=tk.LEFT, padx=(5, 10), pady=5)
        self.diff_combo.bind("<<ComboboxSelected>>", lambda e: self.on_mode_or_difficulty_change())

        # Fallabilidad de Bot Inteligente
        fall_lbl = tk.Label(config_frame, text="Fallo IA:", font=("Helvetica", 9, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BACKGROUND)
        fall_lbl.pack(side=tk.LEFT, padx=(10, 5))

        self.fall_combo = ttk.Combobox(
            config_frame, values=["0% (Infalible)", "20% (Humano)", "45% (Pifiador)", "75% (Torpe)"],
            state="readonly", width=14
        )
        self.fall_combo.set("20% (Humano)")
        self.fall_combo.pack(side=tk.LEFT, padx=(5, 15), pady=5)
        self.fall_combo.bind("<<ComboboxSelected>>", lambda e: self.on_fallibility_combo_change())

        # 2. Cuerpo Central (Dos columnas: Izquierda Canvas, Derecha Letras)
        body_frame = tk.Frame(self.root, bg=COLOR_BACKGROUND)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # Columna Izquierda: El Patíbulo del Casino (Visualizer)
        left_panel = tk.Frame(body_frame, bg=COLOR_CONTAINER, bd=1, relief=tk.SOLID, width=420)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_panel.pack_propagate(False)

        canvas_header = tk.Label(left_panel, text="PATÍBULO / DETECTOR DE ERRORES", font=("Helvetica", 10, "bold"), fg=COLOR_TEXT_GOLD, bg=COLOR_CONTAINER)
        canvas_header.pack(anchor=tk.W, padx=20, pady=(15, 5))

        # Canvas para Dibujar la Soga de Ahorcado
        self.canvas = tk.Canvas(left_panel, width=380, height=280, bg=COLOR_CONTAINER, highlightthickness=0)
        self.canvas.pack(padx=20, pady=10)

        # Espacio debajo de la soga para Categoría & Pista
        self.meta_frame = tk.Frame(left_panel, bg=COLOR_CONTAINER)
        self.meta_frame.pack(fill=tk.X, padx=20, pady=10)

        self.lbl_category = tk.Label(self.meta_frame, text="Categoría: ...", font=("Helvetica", 11, "bold"), fg=COLOR_TEXT_GOLD, bg=COLOR_CONTAINER)
        self.lbl_category.pack(anchor=tk.W, pady=2)

        self.lbl_hint = tk.Label(self.meta_frame, text="Pista: Selecciona ajustes e inicia ronda.", font=("Helvetica", 9, "italic"), fg="#94a3b8", bg=COLOR_CONTAINER, wraplength=360, justify=tk.LEFT)
        self.lbl_hint.pack(anchor=tk.W, pady=5)

        # Espectadores / Marcadores de Jugadores del Casino
        self.players_display_frame = tk.LabelFrame(left_panel, text=" ASIENTOS DE JUGADORES ", font=("Helvetica", 8, "bold"), fg=COLOR_TEXT_GOLD, bg=COLOR_CONTAINER, bd=1, relief=tk.SOLID)
        self.players_display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 15))

        self.p_widgets = []
        for i in range(3):
            p_seat = tk.Frame(self.players_display_frame, bg=COLOR_INPUT_BG, bd=1, relief=tk.RIDGE)
            p_seat.pack(fill=tk.X, pady=4, padx=8, ipady=4)
            
            p_name = tk.Label(p_seat, text="Jugador", font=("Helvetica", 10, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_INPUT_BG)
            p_name.pack(side=tk.LEFT, padx=10)
            
            p_score = tk.Label(p_seat, text="Puntos: 0", font=("Helvetica", 9), fg=COLOR_TEXT_GOLD, bg=COLOR_INPUT_BG)
            p_score.pack(side=tk.RIGHT, padx=10)
            
            self.p_widgets.append({"frame": p_seat, "name": p_name, "score": p_score})

        # Columna Derecha: El Tablero de Letras y la Palabra Misterio
        right_panel = tk.Frame(body_frame, bg=COLOR_CONTAINER, bd=1, relief=tk.SOLID)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Palabra Secreta Espacio
        word_title = tk.Label(right_panel, text="PALABRA MISTERIO", font=("Helvetica", 11, "bold"), fg=COLOR_TEXT_GOLD, bg=COLOR_CONTAINER)
        word_title.pack(anchor=tk.W, padx=30, pady=(20, 5))

        self.word_slots_frame = tk.Frame(right_panel, bg=COLOR_CONTAINER)
        self.word_slots_frame.pack(fill=tk.X, padx=30, pady=15)

        # Teclado Virtual de Alfabeto
        letters_title = tk.Label(right_panel, text="TECLADO ALFABÉTICO", font=("Helvetica", 10, "bold"), fg=COLOR_TEXT_GOLD, bg=COLOR_CONTAINER)
        letters_title.pack(anchor=tk.W, padx=30, pady=(15, 5))

        self.keyboard_frame = tk.Frame(right_panel, bg=COLOR_CONTAINER)
        self.keyboard_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        # 3. Barra baja de comando
        control_bar = tk.Frame(self.root, bg=COLOR_CONTROLS, height=100)
        control_bar.pack(fill=tk.X, side=tk.BOTTOM)

        buttons_frame = tk.Frame(control_bar, bg=COLOR_CONTROLS)
        buttons_frame.pack(side=tk.LEFT, padx=30, pady=20)

        # Iniciar Ronda Botón
        self.btn_start = tk.Button(
            buttons_frame, text="Iniciar Nueva Ronda", font=("Helvetica", 10, "bold"), 
            fg=COLOR_TEXT_MAIN, bg="#059669", activebackground="#10b981", activeforeground=COLOR_TEXT_MAIN,
            bd=0, padx=20, pady=8, command=self.start_game
        )
        self.btn_start.pack(side=tk.LEFT, padx=10)

        # Auto Resolver IA Botón
        self.btn_ai_hint = tk.Button(
            buttons_frame, text="Petición de Pista / Mov. IA", font=("Helvetica", 10, "bold"), 
            fg=COLOR_TEXT_MAIN, bg="#0284c7", activebackground="#38bdf8", activeforeground=COLOR_TEXT_MAIN,
            bd=0, padx=15, pady=8, command=self.manual_ai_turn
        )
        self.btn_ai_hint.pack(side=tk.LEFT, padx=10)

        # Consola informativa de eventos
        self.lbl_info = tk.Label(
            control_bar, text="Presiona 'Iniciar Nueva Ronda' para comenzar.", 
            font=("Helvetica", 11, "bold"), fg="#e2e8f0", bg=COLOR_CONTROLS, wraplength=450, justify=tk.RIGHT
        )
        self.lbl_info.pack(side=tk.RIGHT, padx=30, pady=25)

    def on_fallibility_combo_change(self):
        val_str = self.fall_combo.get()
        if "0%" in val_str:
            self.ai_fallibility.set(0)
        elif "20%" in val_str:
            self.ai_fallibility.set(20)
        elif "45%" in val_str:
            self.ai_fallibility.set(45)
        else:
            self.ai_fallibility.set(75)

    def on_mode_or_difficulty_change(self):
        self.cancel_all_timers()
        mode_str = self.game_mode.get()
        diff_str = self.difficulty.get()

        # Configurar dificultad
        if "Fácil" in diff_str:
            self.max_attempts = 8
        elif "Medio" in diff_str:
            self.max_attempts = 6
        else:
            self.max_attempts = 5

        # Configurar tipos de jugadores de la sesión
        if "Solitario" in mode_str:
            self.players[0] = {"name": "Jugador 1 (H)", "score": self.players[0]["score"], "type": "human", "is_active": True}
            self.players[1] = {"name": "(Vacío)", "score": 0, "type": "ai", "is_active": False}
            self.players[2] = {"name": "(Vacío)", "score": 0, "type": "ai", "is_active": False}
        elif "Humano vs 2 IA" in mode_str:
            self.players[0] = {"name": "Jugador 1 (H)", "score": self.players[0]["score"], "type": "human", "is_active": True}
            self.players[1] = {"name": "Jugador 2 (IA)", "score": self.players[1]["score"], "type": "ai", "is_active": True}
            self.players[2] = {"name": "Jugador 3 (IA)", "score": self.players[2]["score"], "type": "ai", "is_active": True}
        elif "Simulación" in mode_str:
            self.players[0] = {"name": "Jugador 1 (IA)", "score": self.players[0]["score"], "type": "ai", "is_active": True}
            self.players[1] = {"name": "Jugador 2 (IA)", "score": self.players[1]["score"], "type": "ai", "is_active": True}
            self.players[2] = {"name": "Jugador 3 (IA)", "score": self.players[2]["score"], "type": "ai", "is_active": True}
        elif "3 Humanos" in mode_str:
            self.players[0] = {"name": "Jugador 1 (H)", "score": self.players[0]["score"], "type": "human", "is_active": True}
            self.players[1] = {"name": "Jugador 2 (H)", "score": self.players[1]["score"], "type": "human", "is_active": True}
            self.players[2] = {"name": "Jugador 3 (H)", "score": self.players[2]["score"], "type": "human", "is_active": True}

        # Actualizar visualmente la tabla de marcas de los jugadores
        self.update_players_display()
        self.reset_keyboard()
        self.draw_gallows()
        
        self.lbl_info.config(text=f"Partida configurada de forma premium. Listo para iniciar.")

    def update_players_display(self):
        for i, seat in enumerate(self.p_widgets):
            player_data = self.players[i]
            if player_data["is_active"]:
                seat["frame"].pack(fill=tk.X, pady=4, padx=8, ipady=4)
                seat["name"].config(text=player_data["name"])
                seat["score"].config(text=f"Puntos: {player_data['score']}")
                
                # Resaltar si es su turno
                if self.game_state == "playing" and self.current_player_idx == i:
                    seat["frame"].config(bg=COLOR_TEXT_GOLD)
                    seat["name"].config(bg=COLOR_TEXT_GOLD, fg=COLOR_CONTROLS)
                    seat["score"].config(bg=COLOR_TEXT_GOLD, fg=COLOR_CONTROLS)
                else:
                    seat["frame"].config(bg=COLOR_INPUT_BG)
                    seat["name"].config(bg=COLOR_INPUT_BG, fg=COLOR_TEXT_MAIN)
                    seat["score"].config(bg=COLOR_INPUT_BG, fg=COLOR_TEXT_GOLD)
            else:
                seat["frame"].pack_forget()

    def draw_gallows(self):
        self.canvas.delete("all")
        
        # Colores
        wood_color = "#3b2314"
        rope_color = "#eab308"
        scaffold_color = COLOR_TEXT_GOLD
        human_color = COLOR_TEXT_MAIN

        # Base del patíbulo
        self.canvas.create_line(30, 240, 220, 240, fill=wood_color, width=10, capstyle=tk.ROUND)
        
        # Proporción dinámica de fallas
        error_step = 0
        if self.attempts > 0:
            error_step = self.attempts
            # Convertimos intentos a escala proporcional si es dificultad diferente
            if self.max_attempts == 6:  # Medio
                # 6 pasos de intentos mapeados a las partes visuales de 8 pasos
                steps_map = [0, 1, 2, 4, 5, 6, 7, 8]
                error_step = steps_map[min(self.attempts, 6)]
            elif self.max_attempts == 5:  # Difícil
                steps_map = [0, 1, 3, 5, 6, 8]
                error_step = steps_map[min(self.attempts, 5)]

        # Paso 1: Poste vertical
        if error_step >= 1:
            self.canvas.create_line(70, 240, 70, 40, fill=wood_color, width=8)
            
        # Paso 2: Travesaño superior
        if error_step >= 2:
            self.canvas.create_line(70, 40, 170, 40, fill=wood_color, width=8)
            # Soporte angular
            self.canvas.create_line(70, 75, 105, 40, fill=wood_color, width=6)
            
        # Paso 3: Soga / Cuerda colgante
        if error_step >= 3:
            self.canvas.create_line(170, 40, 170, 80, fill=rope_color, width=4)
            self.canvas.create_oval(162, 78, 178, 92, outline=rope_color, width=3)

        # Paso 4: Cabeza del ahorcado
        if error_step >= 4:
            self.canvas.create_oval(153, 90, 187, 124, outline=human_color, fill=COLOR_INPUT_BG, width=3)

        # Paso 5: Tronco / Espalda
        if error_step >= 5:
            self.canvas.create_line(170, 124, 170, 180, fill=human_color, width=3)

        # Paso 6: Brazos
        if error_step >= 6:
            # Izquierdo
            self.canvas.create_line(170, 138, 145, 158, fill=human_color, width=3)
            # Derecho
            self.canvas.create_line(170, 138, 195, 158, fill=human_color, width=3)

        # Paso 7: Piernas
        if error_step >= 7:
            # Izquierda
            self.canvas.create_line(170, 180, 148, 222, fill=human_color, width=3)
            # Derecha
            self.canvas.create_line(170, 180, 192, 222, fill=human_color, width=3)

        # Paso 8: Rostro final / Muerto (X X)
        if error_step >= 8:
            # Ojo Izquierdo X
            self.canvas.create_line(160, 101, 166, 107, fill=COLOR_TEXT_RED, width=2)
            self.canvas.create_line(166, 101, 160, 107, fill=COLOR_TEXT_RED, width=2)
            # Ojo Derecho X
            self.canvas.create_line(174, 101, 180, 107, fill=COLOR_TEXT_RED, width=2)
            self.canvas.create_line(180, 101, 174, 107, fill=COLOR_TEXT_RED, width=2)
            # Boca triste o recta
            self.canvas.create_line(165, 116, 175, 116, fill=COLOR_TEXT_RED, width=2)

    def start_game(self):
        self.cancel_all_timers()
        
        # Bloquear menús interactivos durante la ronda activa de casino
        self.mode_combo.config(state="disabled")
        self.diff_combo.config(state="disabled")
        self.fall_combo.config(state="disabled")
        self.btn_start.config(state="disabled", bg="#1f2937")

        # Elegir palabra secreta aleatoria del banco
        selected = random.choice(WORD_BANK)
        self.secret_word = selected["word"].upper()
        self.category = selected["category"]
        self.hint = selected["hint"]

        self.guessed_letters = []
        self.attempts = 0
        self.current_player_idx = 0
        self.game_state = "playing"

        # Mostrar Metadatos
        self.lbl_category.config(text=f"Categoría: {self.category}")
        self.lbl_hint.config(text=f"Pista: {self.hint}")

        self.reset_keyboard()
        self.draw_gallows()
        self.update_word_slots()
        self.update_players_display()

        self.lbl_info.config(text=f"¡Ronda Iniciada! Comienza: {self.get_current_player()['name']}")
        
        # Se activa ciclo IA si el primer jugador resulta ser un Bot inteligente
        self.trigger_ai_if_active()

    def get_current_player(self):
        return self.players[self.current_player_idx]

    def trigger_ai_if_active(self):
        if self.game_state != "playing":
            return
        
        current_p = self.get_current_player()
        if current_p["type"] == "ai":
            # Bloquear teclado durante el pensamiento de la IA para emulación perfecta
            self.set_keyboard_state("disabled")
            self.lbl_info.config(text=f"{current_p['name']} está analizando probabilidades...")
            self.schedule_action(1200, self.auto_ai_decision)
        else:
            self.set_keyboard_state("normal")

    def make_guess(self, letter):
        if self.game_state != "playing":
            return
        
        letter = letter.upper()
        if letter in self.guessed_letters:
            return

        self.guessed_letters.append(letter)

        # Buscar botón para apagarlo limpiamente
        if letter in self.btn_keyboard_map:
            self.btn_keyboard_map[letter].config(state="disabled", bg=COLOR_CONTROLS, fg="#4b5563")

        # Verificar si la letra está en la palabra (Soporte sin acentos)
        # Nota: La palabra del WORD_BANK ya no tiene acentos de por sí.
        if letter in self.secret_word:
            self.lbl_info.config(text=f"¡Letra '{letter}' correcta! Conservas tu turno.")
            self.root.bell()  # Tono ligero
            # Darle puntos parciales por acierto
            self.get_current_player()["score"] += 10
            self.update_players_display()
        else:
            self.attempts += 1
            self.draw_gallows()
            self.lbl_info.config(text=f"Letra '{letter}' incorrecta. Siguiente turno...")
            
            # Pasar al siguiente jugador activo
            self.next_turn()

        self.update_word_slots()
        self.check_game_status()

        # Si el juego sigue y sigue tocando IA, ejecutamos
        if self.game_state == "playing":
            self.trigger_ai_if_active()

    def next_turn(self):
        mode_str = self.game_mode.get()
        # En solitario, sólo juega el Humano 1
        if "Solitario" in mode_str:
            self.current_player_idx = 0
            return

        # De lo contrario rotar entre los 3 asientos
        while True:
            self.current_player_idx = (self.current_player_idx + 1) % 3
            if self.players[self.current_player_idx]["is_active"]:
                break
        
        p = self.get_current_player()
        self.lbl_info.config(text=f"Turno de {p['name']}")
        self.update_players_display()

    def check_game_status(self):
        # Ganado: Si todas las letras de la palabra secreta han sido descubiertas
        clean_secret = self.secret_word.replace(" ", "")
        won = all(char in self.guessed_letters for char in clean_secret)

        if won:
            # Puntos extras al que terminó de revelar la palabra
            self.get_current_player()["score"] += 100
            self.game_state = "won"
            self.end_round(True)
        elif self.attempts >= self.max_attempts:
            self.game_state = "lost"
            self.end_round(False)

    def end_round(self, is_victory):
        self.set_keyboard_state("disabled")
        self.btn_start.config(state="normal", bg="#059669")
        self.mode_combo.config(state="readonly")
        self.diff_combo.config(state="readonly")
        self.fall_combo.config(state="readonly")
        
        # Revelar todas las letras
        self.update_word_slots(reveal_all=True)
        self.update_players_display()

        if is_victory:
            p = self.get_current_player()
            self.lbl_info.config(text=f"¡Felicidades! Victoria declarada para {p['name']}!")
            messagebox.showinfo("VICTORIA PREMIUM", f"¡La palabra secreta ha sido descifrada! Palabra: {self.secret_word} Ganador: {p['name']} Has acumulado puntos premium.")
        else:
            self.lbl_info.config(text=f"Derrota. La palabra correcta era: {self.secret_word}")
            messagebox.showerror("FIN DEL JUEGO", f"Se agotaron los intentos mínimos permitidos. La palabra era: {self.secret_word} ¡Inténtalo otra vez!")

    def auto_ai_decision(self):
        # Pensamiento lógico: IA calcula mejores probabilidades con posibilidad de blunders
        fall_pct = self.ai_fallibility.get()
        letter = self.calculate_best_ai_letter()
        
        if random.randint(1, 100) <= fall_pct:
            # Elegir letra errónea a propósito para emular pifias humanas
            clean_secret = self.secret_word.replace(" ", "")
            bad_letters = [l for l in SPANISH_FREQ_ORDER if l not in self.guessed_letters and l not in clean_secret]
            if bad_letters:
                letter = random.choice(bad_letters)
                p = self.get_current_player()
                self.lbl_info.config(text=f"🤖 {p['name']} duda del patrón y arriesga la letra '{letter}'...")
                self.root.after(400, lambda: self.make_guess(letter))
                return

        self.make_guess(letter)

    def manual_ai_turn(self):
        # Ofrecer pista de IA manual al jugador humano activo o pedir a la IA que juegue
        if self.game_state != "playing":
            messagebox.showinfo("PISTA IA", "Inicia una nueva ronda de casino para solicitar pistas sofisticadas.")
            return
        
        best = self.calculate_best_ai_letter()
        # Verificar si es turno del Humano
        current_p = self.get_current_player()
        if current_p["type"] == "human":
            messagebox.showinfo("CONSEJO DE IA SOLVER", f"El procesador probabilístico de IA aconseja jugar la letra: '{best}'")
        else:
            # Ejecutar inmediatamente si es IA
            self.make_guess(best)

    def calculate_best_ai_letter(self):
        # 1. Buscar correspondencia con el diccionario
        candidates = []
        for word_obj in WORD_BANK:
            word = word_obj["word"].upper()
            if len(word) != len(self.secret_word):
                continue
            
            # Verificar si la palabra encaja con lo apostado
            match = True
            for idx, c_char in enumerate(self.secret_word):
                w_char = word[idx]
                if c_char == " ":
                    if w_char != " ":
                        match = False
                        break
                    continue

                if c_char in self.guessed_letters:
                    if w_char != c_char:
                        match = False
                        break
                else:
                    # No puede tener cargadas letras erróneas en el patrón
                    if w_char in self.guessed_letters:
                        match = False
                        break
            if match:
                candidates.append(word)

        # 2. Elegir letra no revelada que aparece más veces en los candidatos posibles
        freqs = {}
        for cand in candidates:
            unique_chars = set(cand)
            for char in unique_chars:
                if char == " " or char in self.guessed_letters:
                    continue
                freqs[char] = freqs.get(char, 0) + 1

        if freqs:
            sorted_chars = sorted(freqs.items(), key=lambda x: x[1], reverse=True)
            return sorted_chars[0][0]

        # 3. Si no hay candidatos, recurrir al alfabeto por frecuencia tradicional española
        for letter in SPANISH_FREQ_ORDER:
            if letter not in self.guessed_letters:
                return letter
        
        return "E"

    def update_word_slots(self, reveal_all=False):
        for widget in self.word_slots_frame.winfo_children():
            widget.destroy()

        # Generar bloques de cajas elegantes
        for char in self.secret_word:
            if char == " ":
                # Separador de palabras
                space_box = tk.Frame(self.word_slots_frame, width=30, height=45, bg=COLOR_CONTAINER)
                space_box.pack(side=tk.LEFT, padx=3)
            else:
                box_frame = tk.Frame(self.word_slots_frame, bg=COLOR_INPUT_BG, bd=2, relief=tk.SOLID)
                box_frame.pack(side=tk.LEFT, padx=5, ipady=4)
                
                char_to_show = " "
                color_text = COLOR_TEXT_MAIN
                if char in self.guessed_letters or reveal_all:
                    char_to_show = char
                    if reveal_all and char not in self.guessed_letters:
                        color_text = COLOR_TEXT_RED

                char_lbl = tk.Label(
                    box_frame, text=char_to_show, font=("Courier New", 18, "bold"), 
                    width=3, fg=color_text, bg=COLOR_INPUT_BG
                )
                char_lbl.pack()

    def reset_keyboard(self):
        for widget in self.keyboard_frame.winfo_children():
            widget.destroy()

        self.btn_keyboard_map = {}
        # Crear rejilla bonita (3 filas de botones)
        keys_rows = [
            ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
            ["J", "K", "L", "M", "N", "Ñ", "O", "P", "Q"],
            ["R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        ]

        for r_idx, row in enumerate(keys_rows):
            row_frame = tk.Frame(self.keyboard_frame, bg=COLOR_CONTAINER)
            row_frame.pack(pady=4)
            for char in row:
                btn = tk.Button(
                    row_frame, text=char, font=("Helvetica", 11, "bold"), width=4, height=1,
                    bg=COLOR_INPUT_BG, fg=COLOR_TEXT_MAIN, activebackground=COLOR_TEXT_GOLD, activeforeground=COLOR_CONTROLS,
                    bd=1, relief=tk.RAISED, command=lambda c=char: self.make_guess(c)
                )
                btn.pack(side=tk.LEFT, padx=3)
                self.btn_keyboard_map[char] = btn

                # Apagar si el juego no ha iniciado
                if self.game_state != "playing":
                    btn.config(state="disabled")

    def set_keyboard_state(self, state):
        for char, btn in self.btn_keyboard_map.items():
            if char not in self.guessed_letters:
                btn.config(state=state)

if __name__ == "__main__":
    root = tk.Tk()
    app = HangmanController(root)
    root.mainloop()
