import tkinter as tk
from tkinter import messagebox
import threading
import pyttsx3

# Audio setup
engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    threading.Thread(target=lambda: engine.say(text) or engine.runAndWait(), daemon=True).start()

# Levels
LEVELS = {
    "Basic Functions": ["Dot", "Dash", "Delete", "Enter"],
    "Alphabets": [chr(i) for i in range(65, 91)],  # A-Z
    "Common Words": ["YES", "NO", "HELP", "WATER", "TOILET"]
}

BLINK_CLUES = {
    "Dot": "Fast Blink",
    "Dash": "Slow Blink",
    "Delete": "Left Eye",
    "Enter": "Very Slow Blink"
}

MORSE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..'
}

SYMBOLS = {
    "Dot": "●",
    "Dash": "▬"
}

class LearnUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drishti — ALS Morse Learning")
        self.geometry("1150x700")
        self.configure(bg="#121212")
        self.level_names = list(LEVELS.keys())
        self.level_index = 0
        self.sublevel_index = 0
        self.current_items = LEVELS[self.level_names[self.level_index]]
        self.star_labels = []

        # Colors
        self.bg_color = "#121212"
        self.key_color = "#1e1e1e"
        self.correct_color = "#00ff7f"
        self.wrong_color = "#ff4d4d"
        self.text_color = "#ffffff"
        self.accent_color = "#03dac6"

        # Build UI
        self.build_ui()
        self.load_level(self.level_index, self.sublevel_index)

        # Start gaze check loop (placeholder)
        self.after(100, self.up_gaze_loop)

    def build_ui(self):
        # Header
        self.header = tk.Label(self, text="DRISHTI — Morse Learning Game",
                               fg=self.accent_color, bg=self.bg_color, font=("Segoe UI", 28, "bold"))
        self.header.pack(pady=15)

        # Sublevel display
        self.sublevel_lbl = tk.Label(self, text="", fg=self.text_color,
                                     bg=self.bg_color, font=("Segoe UI", 60, "bold"))
        self.sublevel_lbl.pack(pady=30)

        # Morse clue
        self.morse_lbl = tk.Label(self, text="", fg=self.accent_color,
                                  bg=self.bg_color, font=("Segoe UI", 36))
        self.morse_lbl.pack(pady=15)

        # Buttons frame
        self.button_frame = tk.Frame(self, bg=self.bg_color)
        self.button_frame.pack(pady=20)

        self.buttons = {}
        for i, key in enumerate(["Dot", "Dash", "Delete", "Enter"]):
            btn = tk.Button(self.button_frame, text=key, font=("Segoe UI", 22, "bold"),
                            width=14, height=3, bg=self.key_color, fg=self.text_color,
                            command=lambda k=key: self.check_answer(k))
            btn.grid(row=0, column=i, padx=15, pady=15)
            self.buttons[key] = btn

        # Blink clues (centered)
        self.clue_frame = tk.Frame(self, bg=self.bg_color)
        self.clue_frame.pack(pady=20)
        self.clues_lbls = []
        for key in ["Dot", "Dash", "Delete", "Enter"]:
            lbl = tk.Label(self.clue_frame, text=f"{key}: {BLINK_CLUES[key]} {SYMBOLS.get(key,'')}",
                           fg=self.accent_color, bg=self.bg_color, font=("Segoe UI", 18))
            lbl.grid(row=0, column=list(["Dot", "Dash", "Delete", "Enter"]).index(key), padx=25)
            self.clues_lbls.append(lbl)

        # Feedback label
        self.feedback_lbl = tk.Label(self, text="", fg=self.text_color,
                                     bg=self.bg_color, font=("Segoe UI", 26))
        self.feedback_lbl.pack(pady=15)

        # Star animation container
        self.star_frame = tk.Frame(self, bg=self.bg_color)
        self.star_frame.pack(pady=15)

    def load_level(self, level_index, sublevel_index):
        level_name = self.level_names[level_index]
        self.current_items = LEVELS[level_name]
        current_item = self.current_items[sublevel_index]
        self.sublevel_lbl.config(text=current_item)
        speak(f"Level: {level_name}, learn: {current_item}")

        if level_name == "Basic Functions":
            for btn in self.buttons.values():
                btn.grid()
            self.clue_frame.pack(pady=20)
            self.morse_lbl.config(text="")
        elif level_name == "Alphabets":
            for btn in self.buttons.values():
                btn.grid_remove()
            self.clue_frame.pack_forget()
            morse_code = MORSE_DICT[current_item]
            morse_display = "".join("●" if ch == "." else "▬" for ch in morse_code)
            self.morse_lbl.config(text=morse_display)
        else:
            for btn in self.buttons.values():
                btn.grid_remove()
            self.clue_frame.pack_forget()
            self.morse_lbl.config(text="")

    def check_answer(self, choice):
        target = self.current_items[self.sublevel_index]
        if choice == target:
            self.correct_feedback()
            self.sublevel_index += 1
            if self.sublevel_index >= len(self.current_items):
                self.level_index += 1
                self.sublevel_index = 0
                self.star_labels_clear()
                if self.level_index >= len(self.level_names):
                    self.congratulations()
                    return
        else:
            self.wrong_feedback()
            self.sublevel_index = 0
            self.star_labels_clear()

        self.load_level(self.level_index, self.sublevel_index)

    def correct_feedback(self):
        self.feedback_lbl.config(text="Correct!", fg=self.correct_color)
        speak("Correct!")
        self.animate_star()

    def wrong_feedback(self):
        self.feedback_lbl.config(text="Wrong! Restarting Level", fg=self.wrong_color)
        speak("Incorrect! Restarting this level.")

    def animate_star(self):
        star = tk.Label(self.star_frame, text="★", font=("Segoe UI", 36), fg=self.accent_color, bg=self.bg_color)
        star.pack(side="left", padx=7)
        self.star_labels.append(star)
        self.after(1000, lambda: star.destroy())

    def star_labels_clear(self):
        for star in self.star_labels:
            star.destroy()
        self.star_labels.clear()

    def congratulations(self):
        self.feedback_lbl.config(text="Congratulations! All Levels Completed!", fg=self.accent_color)
        speak("Congratulations! You have completed all levels.")
        self.after(3000, self.switch_to_main)

    def switch_to_main(self):
        self.destroy()
        import main_ui

    def up_gaze_loop(self):
        # Placeholder for up gaze integration
        self.after(100, self.up_gaze_loop)

if __name__ == "__main__":
    app = LearnUI()
    app.mainloop()
