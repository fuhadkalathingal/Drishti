import os
from io import BytesIO
import threading
import tkinter as tk
import pygame
from app.core.eye_gesture import get_gesture_frame

# -----------------------------
# Morse dictionary
# -----------------------------
MORSE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..'
}

# -----------------------------
# Gesture to symbol mapping
# -----------------------------
GESTURE_TO_SYMBOL = {
    "FB": ".",       # Fast blink -> Dot
    "SB": "-",       # Slow blink -> Dash
    "VSB": "ENTER"   # Very slow blink -> Enter
}

# -----------------------------
# Colors
# -----------------------------
BG = "#121212"
PANEL = "#1e1e1e"
TEXT = "#ffffff"
HIGHLIGHT = "#ffd54f"
CORRECT = "#00c853"    # green for correct
WRONG = "#ff3d00"      # red for wrong
MORSE_COLOR = "#81d4fa"

# -----------------------------
# Audio cache
# -----------------------------
CACHE_DIR = "audio_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# -----------------------------
# Initialize pygame mixer
# -----------------------------
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# -----------------------------
# Groq AI TTS setup
# -----------------------------
from groq import Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY not found!")

client = Groq(api_key=GROQ_API_KEY)

# -----------------------------
# Non-blocking TTS
# -----------------------------
def speak(text: str):
    if not text.strip():
        return

    def _play_audio():
        try:
            safe_name = text.replace(" ", "_").lower()
            file_path = os.path.join(CACHE_DIR, f"{safe_name}.wav")
            if not os.path.exists(file_path):
                response = client.audio.speech.create(
                    model="playai-tts",
                    voice="Jennifer-PlayAI",
                    response_format="wav",
                    input=text
                )
                audio_bytes = BytesIO(response.read())
                with open(file_path, "wb") as f:
                    f.write(audio_bytes.getbuffer())
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"[Speech Error] {e}")

    threading.Thread(target=_play_audio, daemon=True).start()

# -----------------------------
# Levels
# -----------------------------
BASIC_FUNCTIONS_SEQ = [".", "-", "ENTER"]

# -----------------------------
# ALS-Friendly Guided Morse Learner
# -----------------------------
class GuidedMorseLearner(tk.Toplevel):
    SYMBOL_TRANSITION_DELAY = 800  # ms between symbols
    LETTER_INSERT_DELAY = 500      # ms after ENTER to move next letter

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Drishti — Guided Morse Learning")
        self.geometry("1150x700")
        self.configure(bg=BG)

        # State
        self.levels = ["Basic Functions", "Alphabets"]
        self.current_level_index = 0
        self.letters = list(MORSE_DICT.keys())
        self.letter_index = 0
        self.symbol_index = 0
        self.awaiting_input = False
        self.current_symbol = ""
        self.pattern_widgets = []
        self.instruction_spoken = False
        self.level_completion_spoken = False

        # Build UI
        self._build_ui()
        self.after(50, self.start_next_symbol)

    # --------------------------
    # UI BUILDING
    # --------------------------
    def _build_ui(self):
        self.header = tk.Label(self, text="DRISHTI — Guided Morse Learning",
                               font=("Segoe UI", 26, "bold"), bg=BG, fg=TEXT)
        self.header.pack(pady=(12, 6))

        self.letter_display = tk.Label(self, text="", font=("Segoe UI", 72, "bold"),
                                       bg=BG, fg=MORSE_COLOR)
        self.letter_display.pack(pady=12)

        self.pattern_frame = tk.Frame(self, bg=BG)
        self.pattern_frame.pack(pady=10)

        self.instruction_text = tk.Label(self, text="", font=("Segoe UI", 20), bg=BG, fg=TEXT,
                                         wraplength=600, justify="left")
        self.instruction_text.pack(pady=8)

        self.feedback_lbl = tk.Label(self, text="", font=("Segoe UI", 20, "bold"), bg=BG, fg=TEXT)
        self.feedback_lbl.pack(pady=8)

        controls_frame = tk.Frame(self, bg=BG)
        controls_frame.pack(pady=12)

        self.dot_box = tk.Label(controls_frame, text="• Dot (Fast Blink)", font=("Segoe UI", 16),
                                width=22, height=2, bg=PANEL, fg=TEXT, relief="ridge", bd=2)
        self.dot_box.grid(row=0, column=0, padx=8, pady=6)
        self.dash_box = tk.Label(controls_frame, text="▬ Dash (Slow Blink)", font=("Segoe UI", 16),
                                 width=22, height=2, bg=PANEL, fg=TEXT, relief="ridge", bd=2)
        self.dash_box.grid(row=0, column=1, padx=8, pady=6)
        self.enter_box = tk.Label(controls_frame, text="↵ Enter (Very Slow Blink)", font=("Segoe UI", 16),
                                  width=28, height=2, bg=PANEL, fg=TEXT, relief="ridge", bd=2)
        self.enter_box.grid(row=0, column=2, padx=8, pady=6)

        self.decoded_text = tk.Text(self, height=6, bg="#0c0d0f", fg=TEXT,
                                    font=("Consolas", 20), bd=2)
        self.decoded_text.pack(fill="both", expand=True, padx=18, pady=12)

    # --------------------------
    # Render current letter or function
    # --------------------------
    def _render_current(self):
        for w in self.pattern_frame.winfo_children():
            w.destroy()
        self.pattern_widgets.clear()
        self._update_feedback("")  # Reset feedback

        level = self.levels[self.current_level_index]
        if level == "Basic Functions":
            symbol = BASIC_FUNCTIONS_SEQ[self.symbol_index]
            lbl = tk.Label(self.pattern_frame, text=symbol if symbol != "ENTER" else "↵",
                           font=("Consolas", 28, "bold"), bg=PANEL, fg=MORSE_COLOR, width=6, relief="ridge", bd=2)
            lbl.grid(row=0, column=0, padx=10)
            self.pattern_widgets.append(lbl)
        else:  # Alphabets
            letter = self.letters[self.letter_index]
            self.letter_display.config(text=letter)
            speak(f"Letter {letter}")  # Speak letter immediately
            pattern = MORSE_DICT[letter]
            for i, sym in enumerate(pattern):
                lbl = tk.Label(self.pattern_frame, text=sym, font=("Consolas", 28, "bold"),
                               bg=PANEL, fg=MORSE_COLOR, width=4, relief="ridge", bd=2)
                lbl.grid(row=0, column=i, padx=6)
                self.pattern_widgets.append(lbl)
            enter_lbl = tk.Label(self.pattern_frame, text="↵", font=("Consolas", 20, "bold"),
                                 bg=PANEL, fg=TEXT, width=4, relief="ridge", bd=2)
            enter_lbl.grid(row=0, column=len(pattern), padx=10)
            self.pattern_widgets.append(enter_lbl)
        self.instruction_spoken = False

    # --------------------------
    # Highlight controls
    # --------------------------
    def _highlight_control(self, which, color):
        for box in [self.dot_box, self.dash_box, self.enter_box]:
            box.config(bg=PANEL)
        if which == ".": self.dot_box.config(bg=color)
        if which == "-": self.dash_box.config(bg=color)
        if which == "ENTER": self.enter_box.config(bg=color)

    # --------------------------
    # Feedback
    # --------------------------
    def _update_feedback(self, text, color=TEXT):
        self.feedback_lbl.config(text=text, fg=color)

    # --------------------------
    # Start next symbol
    # --------------------------
    def start_next_symbol(self):
        if self.current_level_index >= len(self.levels):
            self.instruction_text.config(text="All levels completed! Well done!")
            speak("All levels completed. Well done!")
            return

        self._render_current()
        level = self.levels[self.current_level_index]

        if level == "Basic Functions":
            self.current_symbol = BASIC_FUNCTIONS_SEQ[self.symbol_index]
        else:
            letter = self.letters[self.letter_index]
            pattern = MORSE_DICT[letter]
            if self.symbol_index < len(pattern):
                self.current_symbol = pattern[self.symbol_index]
            else:
                self.current_symbol = "ENTER"

        self.awaiting_input = True

        # Highlight waiting symbol
        self._highlight_control(self.current_symbol, HIGHLIGHT)
        if self.symbol_index < len(self.pattern_widgets):
            self.pattern_widgets[self.symbol_index].config(bg=HIGHLIGHT)

        # Speak instruction immediately
        self._speak_instruction(self.current_symbol)

        self.update_idletasks()
        self.after(40, self._poll_gesture)

    # --------------------------
    # Speak instruction
    # --------------------------
    def _speak_instruction(self, symbol):
        if self.instruction_spoken:
            return
        if symbol == ".":
            self.instruction_text.config(text="Blink fast for DOT")
            speak("dot")
        elif symbol == "-":
            self.instruction_text.config(text="Blink slow for DASH")
            speak("dash")
        else:
            self.instruction_text.config(text="Blink very slowly for ENTER")
            speak("enter")
        self.instruction_spoken = True

    # --------------------------
    # Poll gestures
    # --------------------------
    def _poll_gesture(self):
        if not self.awaiting_input:
            self.after(40, self._poll_gesture)
            return
        try:
            event = get_gesture_frame()
            if event:
                mapped = GESTURE_TO_SYMBOL.get(event)
                if mapped == self.current_symbol:
                    # Correct input — green highlight
                    if self.symbol_index < len(self.pattern_widgets):
                        self.pattern_widgets[self.symbol_index].config(bg=CORRECT)
                    self._highlight_control(self.current_symbol, CORRECT)
                    self._update_feedback("Correct!", CORRECT)
                    self.awaiting_input = False
                    self.instruction_spoken = False
                    # Delay before moving to next symbol
                    self.after(self.SYMBOL_TRANSITION_DELAY, self._move_next_symbol)
                elif mapped:
                    # Wrong input — red highlight
                    if self.symbol_index < len(self.pattern_widgets):
                        self.pattern_widgets[self.symbol_index].config(bg=WRONG)
                    self._highlight_control(self.current_symbol, WRONG)
                    self._update_feedback("Wrong — try again", WRONG)
                    speak("wrong")

                    # Reset highlight back to waiting
                    self.after(400, lambda: (self.pattern_widgets[self.symbol_index].config(bg=HIGHLIGHT),
                                             self._highlight_control(self.current_symbol, HIGHLIGHT),
                                             self._update_feedback("")))
        except Exception as e:
            print(f"[Gesture Polling Error] {e}")

        self.after(40, self._poll_gesture)

    # --------------------------
    # Move to next symbol
    # --------------------------
    def _move_next_symbol(self):
        level = self.levels[self.current_level_index]

        if level == "Basic Functions":
            self.symbol_index += 1
            if self.symbol_index >= len(BASIC_FUNCTIONS_SEQ):
                if not self.level_completion_spoken:
                    speak("Level 1 completed. Now Alphabets")
                    self.level_completion_spoken = True
                self.current_level_index += 1
                self.symbol_index = 0
                self.letter_index = 0
                self.after(self.SYMBOL_TRANSITION_DELAY, self.start_next_symbol)
            else:
                self.after(self.SYMBOL_TRANSITION_DELAY, self.start_next_symbol)
        else:  # Alphabets
            if self.current_symbol == "ENTER":
                letter = self.letters[self.letter_index]
                self.decoded_text.insert("end", letter + " ")
                self.decoded_text.see("end")  # Scroll to end to avoid overlap
                self.letter_index += 1
                self.symbol_index = 0
                self.after(self.LETTER_INSERT_DELAY, self.start_next_symbol)
            else:
                self.symbol_index += 1
                self.after(self.SYMBOL_TRANSITION_DELAY, self.start_next_symbol)


def run_learn_ui(root):
    """Run the Guided Morse Learning UI safely inside a shared Tk root."""
    root.withdraw()

    app = GuidedMorseLearner(root)

    def on_complete():
        app.destroy()
        root.quit()

    def on_close():
        """Handle window close (X button)."""
        app.destroy()
        root.quit()

    app.protocol("WM_DELETE_WINDOW", on_close)

    original_start_next_symbol = app.start_next_symbol

    def patched_start_next_symbol():
        if app.current_level_index >= len(app.levels):
            app.instruction_text.config(text="All levels completed! Well done!")
            speak("All levels completed. Well done!")
            app.after(2000, on_complete)
            return
        original_start_next_symbol()

    app.start_next_symbol = patched_start_next_symbol
    app.after(50, app.start_next_symbol)
    root.mainloop()
