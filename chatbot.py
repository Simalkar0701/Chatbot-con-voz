import customtkinter as ctk
from tkinter import END

import speech_recognition as sr
import pygame
import threading
import asyncio
import edge_tts

import tempfile
import uuid
import os

# Volvemos al motor de búsqueda puro optimizado
from duckduckgo_search import DDGS

# =========================================================
# CONFIGURACIÓN GENERAL DE LA INTERFAZ
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

pygame.mixer.init()

# =========================================================
# CLASE PRINCIPAL DEL ASISTENTE WEB (SIN IA)
# =========================================================

class ChatBotApp:

    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Asistente de Búsqueda Web Automatizado")
        self.app.geometry("850x760")

        self.audio_lock = threading.Lock()
        self.current_audio = None

        self.crear_interfaz()

        mensaje_inicio = (
            "Hola. Soy tu asistente de información basada en la web. "
            "Dime qué dato necesitas que busque hoy."
        )
        self.mostrar_en_pantalla("Bot", mensaje_inicio)
        self.hablar(mensaje_inicio)

        self.app.bind("<Return>", lambda event: self.enviar_mensaje())
        self.app.protocol("WM_DELETE_WINDOW", self.cerrar_programa)

    # =====================================================
    # INTERFAZ GRÁFICA (CustomTkinter)
    # =====================================================

    def crear_interfaz(self):
        top_frame = ctk.CTkFrame(self.app)
        top_frame.pack(fill="x", pady=10)

        canvas = ctk.CTkCanvas(top_frame, width=100, height=100, bg="#2B2B2B", highlightthickness=0)
        canvas.pack(pady=10)
        canvas.create_oval(10, 10, 90, 90, fill="#1F6AA5", outline="")
        canvas.create_text(50, 50, text="WEB", fill="white", font=("Arial", 24, "bold"))

        titulo = ctk.CTkLabel(top_frame, text="Asistente de Información Web", font=("Arial", 24, "bold"))
        titulo.pack()

        chat_frame = ctk.CTkFrame(self.app)
        chat_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.chat_box = ctk.CTkTextbox(chat_frame, wrap="word", font=("Arial", 15))
        self.chat_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.chat_box.configure(state="disabled")

        bottom_frame = ctk.CTkFrame(self.app)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        self.entrada_texto = ctk.CTkEntry(bottom_frame, placeholder_text="Escribe tu búsqueda aquí...", height=42, font=("Arial", 14))
        self.entrada_texto.pack(side="left", fill="x", expand=True, padx=(0, 10))

        enviar_btn = ctk.CTkButton(bottom_frame, text="Buscar", width=100, command=self.enviar_mensaje)
        enviar_btn.pack(side="left", padx=5)

        voz_btn = ctk.CTkButton(bottom_frame, text="🎤 Hablar", width=120, command=self.escuchar_microfono)
        voz_btn.pack(side="left", padx=5)

        stop_btn = ctk.CTkButton(bottom_frame, text="⛔ Detener Voz", width=150, fg_color="#B22222", hover_color="#8B0000", command=self.detener_voz)
        stop_btn.pack(side="left", padx=5)

    def mostrar_en_pantalla(self, autor, mensaje):
        def actualizar():
            self.chat_box.configure(state="normal")
            self.chat_box.insert(END, f"{autor}: {mensaje}\n\n")
            self.chat_box.configure(state="disabled")
            self.chat_box.see(END)
        self.app.after(0, actualizar)

    # =====================================================
    # CONTROL DE FLUJO DE TRABAJO (HILOS)
    # =====================================================

    def enviar_mensaje(self):
        consulta = self.entrada_texto.get().strip()
        if not consulta:
            return

        self.entrada_texto.delete(0, 'end')
        self.mostrar_en_pantalla("Usuario", consulta)

        hilo = threading.Thread(target=self.procesar_respuesta_hilo, args=(consulta,), daemon=True)
        hilo.start()

    def procesar_respuesta_hilo(self, consulta):
        texto_respuesta = self.obtener_respuesta_web(consulta)
        self.mostrar_en_pantalla("Bot", texto_respuesta)
        self.hablar(texto_respuesta)

    # =====================================================
    # EXTRACCIÓN Y CURACIÓN DE TEXTO WEB (FILTROS MEJORADOS)
    # =====================================================

    def obtener_respuesta_web(self, consulta_usuario):
        consulta_limpia = consulta_usuario.strip()
        if not consulta_limpia:
            return "Por favor ingresa un término de búsqueda válido."

        # Términos que ensucian la lectura por voz del bot
        filtros_basura = [
            "cookies", "iniciar sesión", "iniciar sesion", "derechos reservados", 
            "clic aquí", "privacy policy", "all rights reserved", "enlace permanente",
            "skip to content", "javascript", "navegación", "menú principal"
        ]

        try:
            # Petición limpia a DuckDuckGo usando la sintaxis nativa vigente
            with DDGS() as ddgs:
                resultados = [r for r in ddgs.text(
                    keywords=consulta_limpia,
                    region="es-es",
                    safesearch="moderate",
                    max_results=4
                )]

            if not resultados:
                return f"No encontré páginas web disponibles sobre '{consulta_limpia}'."

            # Recorremos los resultados buscando el extracto más descriptivo y limpio
            for res in resultados:
                texto_cuerpo = res.get("body", "").strip()
                texto_lower = texto_cuerpo.lower()

                # Descartar respuestas excesivamente cortas o vacías
                if not texto_cuerpo or len(texto_cuerpo) < 50:
                    continue

                # Omitir si tiene demasiados avisos técnicos de páginas web
                if any(basura in texto_lower for basura in filtros_basura):
                    continue

                # Segmentamos por oraciones reales para estructurar un párrafo amigable
                oraciones = [o.strip() for o in texto_cuerpo.split(". ") if o.strip()]
                
                if len(oraciones) >= 1:
                    # Unimos las primeras oraciones y forzamos un cierre limpio de la idea
                    parrafo_limpio = ". ".join(oraciones[:2])
                    if not parrafo_limpio.endswith("."):
                        parrafo_limpio += "."
                    
                    # Limpieza final de caracteres extraños remanentes del scrapeo técnico
                    parrafo_limpio = parrafo_limpio.replace("…", "...").replace(" .", ".")
                    return parrafo_limpio

            # Fallback Defensivo: Si los filtros estrictos borraron todo, procesamos el primer título disponible
            primer_res = resultados[0]
            titulo = primer_res.get("title", "").strip()
            resumen = primer_res.get("body", "").strip()[:140]
            
            fallback_salida = f"{titulo}. Encontré este dato: {resumen}"
            if not fallback_salida.endswith("."):
                fallback_salida += "..."
            return fallback_salida

        except Exception as e:
            print("ERROR DUCKDUCKGO SCRAPER:", e)
            return "Lo siento, ocurrió un problema temporal al leer los resultados del buscador."

    # =====================================================
    # SISTEMA TEXT-TO-SPEECH (Edge TTS + Pygame)
    # =====================================================

    def detener_voz(self):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except:
            pass

    async def generar_audio(self, texto, ruta_audio):
        comunicacion = edge_tts.Communicate(text=texto, voice="es-ES-AlvaroNeural", rate="+20%")
        await comunicacion.save(ruta_audio)

    def hablar(self, texto):
        threading.Thread(target=lambda: self.run_tts(texto), daemon=True).start()

    def run_tts(self, texto):
        with self.audio_lock:
            try:
                self.detener_voz()
                
                nombre_audio = f"web_vox_{uuid.uuid4().hex}.mp3"
                ruta_audio = os.path.join(tempfile.gettempdir(), nombre_audio)
                self.current_audio = ruta_audio

                asyncio.run(self.generar_audio(texto, ruta_audio))

                pygame.mixer.music.load(ruta_audio)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(30)

                self.detener_voz()
                if os.path.exists(ruta_audio):
                    os.remove(ruta_audio)
            except Exception as e:
                print("ERROR TTS EN EJECUCIÓN:", e)

    # =====================================================
    # RECONOCIMIENTO DE VOZ (Speech Recognition)
    # =====================================================

    def escuchar_microfono(self):
        self.detener_voz()

        def escuchar():
            recognizer = sr.Recognizer()
            try:
                self.mostrar_en_pantalla("Sistema", "Escuchando lo que dices...")
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.6)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                consulta = recognizer.recognize_google(audio, language="es-ES")
                self.mostrar_en_pantalla("Usuario (Voz)", consulta)

                hilo = threading.Thread(target=self.procesar_respuesta_hilo, args=(consulta,), daemon=True)
                hilo.start()
            except Exception as e:
                self.mostrar_en_pantalla("Sistema", "No se detectó tu voz o el micrófono está ocupado.")
                print("ERROR MIC:", e)

        threading.Thread(target=escuchar, daemon=True).start()

    # =====================================================
    # SALIDA DE LA APP
    # =====================================================

    def cerrar_programa(self):
        self.detener_voz()
        self.app.destroy()

    def run(self):
        self.app.mainloop()

# =========================================================
# ARRANQUE
# =========================================================

if __name__ == "__main__":
    chatbot = ChatBotApp()
    chatbot.run()