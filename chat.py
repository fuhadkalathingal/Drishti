import os
import tkinter as tk
from playsound import playsound
import pyttsx3
import random

# ----------------------------
# Gemini API Setup
# ----------------------------
try:
    from google import genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

API_KEY = "AIzaSyDDPFy86k8vd5Y_3UD3SU4cciIlQjUc2c8"  # Replace with your key
MODEL_NAME = "gemini-2.5-flash"


def chat_with_gemini(prompt):
    """
    Returns AI response text and list of contextually relevant suggested follow-up responses.
    """
    if not GEMINI_AVAILABLE:
        return None

    try:
        client = genai.Client(api_key=API_KEY)

        # Step 1: Main AI response
        main_resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"User said: {prompt}\nReply naturally."
        )
        main_text = main_resp.text.strip()

        # Step 2: Generate 3 contextually relevant suggestions
        suggest_prompt = f"""Given the AI reply: "{main_text}", 
        suggest 3 short follow-up replies that the user might say. 
        Return only the 3 responses separated by |."""

        suggestion_resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=suggest_prompt
        )
        suggestion_text = suggestion_resp.text.strip()

        suggestions = [s.strip() for s in suggestion_text.split('|') if s.strip()][:3]
        return main_text, suggestions

    except Exception as e:
        print(f"Gemini API failed: {e}")
        return "AI response unavailable.", []


# ----------------------------
# Text-to-Speech
# ----------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 150)


def speak(text):
    engine.say(text)
    engine.runAndWait()


# ----------------------------
# Music Playback
# ----------------------------
MUSIC_FOLDER = "C:\\Users\\HOME-PC\\Music"  # Replace with your folder


def play_song():
    try:
        songs = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(".mp3")]
        if not songs:
            speak("No songs found in your music folder.")
            return
        song_to_play = os.path.join(MUSIC_FOLDER, random.choice(songs))
        speak(f"Playing {os.path.basename(song_to_play)}")
        playsound(song_to_play)
    except Exception as e:
        speak(f"Error playing song: {e}")


# ----------------------------
# Mindfulness Exercise
# ----------------------------
def mindfulness_exercise():
    steps = [
        "Breathe in slowly through your nose for 4 seconds.",
        "Hold your breath for 4 seconds.",
        "Exhale slowly through your mouth for 6 seconds.",
        "Repeat 3 times."
    ]
    for step in steps:
        speak(step)


# ----------------------------
# Drishti UI (keyboard + AI)
# ----------------------------
class DrishtiAIUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drishti - From Vision To Voice (AI Companion)")
        self.configure(bg="#121212")
        self.geometry("1150x700")
        self.minsize(900, 600)

        # Colors
        self.bg_color = "#121212"
        self.key_color = "#1e1e1e"
        self.text_color = "#ffffff"
        self.dot_color = "#00ff7f"
        self.dash_color = "#ff4d4d"
        self.accent_color = "#03dac6"

        # Title
        title = tk.Label(self, text="DRISHTI", fg=self.accent_color, bg=self.bg_color,
                         font=("Segoe UI", 24, "bold"))
        title.pack(pady=(10, 5))

        # Input box
        self.input_var = tk.StringVar()
        input_box = tk.Entry(
            self,
            textvariable=self.input_var,
            font=("Segoe UI", 18),
            bg=self.key_color,
            fg=self.text_color,
            insertbackground=self.text_color,
            relief="flat",
            justify="left"
        )
        input_box.pack(fill="x", padx=50, pady=(10, 10), ipady=10)
        self.input_box = input_box

        # Chat display
        self.chat_box = tk.Text(self, height=12, width=100, state=tk.DISABLED, bg="#1c1c1c", fg="#ffffff")
        self.chat_box.pack(padx=50, pady=(0, 10))

        # Suggested response buttons
        self.suggestion_frame = tk.Frame(self, bg=self.bg_color)
        self.suggestion_frame.pack(pady=(0, 10))

        # Buttons for general actions
        action_frame = tk.Frame(self, bg=self.bg_color)
        action_frame.pack(pady=(0, 10))
        tk.Button(action_frame, text="Send to AI", command=self.send_to_ai, bg=self.accent_color, fg="#000000",
                  width=15).pack(side="left", padx=10)
        tk.Button(action_frame, text="Play Song", command=play_song, bg=self.accent_color, fg="#000000", width=15).pack(
            side="left", padx=10)
        tk.Button(action_frame, text="Mindfulness", command=mindfulness_exercise, bg=self.accent_color, fg="#000000",
                  width=15).pack(side="left", padx=10)

        # Keyboard
        kb_frame = tk.Frame(self, bg=self.bg_color)
        kb_frame.pack(expand=True, fill="both", padx=20, pady=10)
        self.create_keyboard(kb_frame)

        # Responsive resize
        self.bind("<Configure>", self.on_resize)

    # ---------------- Keyboard ----------------
    def create_keyboard(self, parent):
        self.keyboard_layout = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
            ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T'],
            ['U', 'V', 'W', 'X', 'Y', 'Z'],
            ['Space', 'Delete']
        ]

        self.morse_dict = {
            '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
            '8': '---..', '9': '----.', '0': '-----', 'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
            'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--',
            'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-',
            'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..', 'Space': ' ', 'Delete': 'DEL'
        }

        self.key_labels = []
        max_columns = max(len(row) for row in self.keyboard_layout)

        for r, row in enumerate(self.keyboard_layout):
            num_keys = len(row)
            start_col = (max_columns - num_keys) // 2

            for c, key in enumerate(row):
                frame = tk.Frame(parent, bg=self.bg_color)
                frame.grid(row=r, column=start_col + c, sticky="nsew", padx=3, pady=3)

                label = tk.Label(frame, text=key, bg=self.key_color, fg=self.text_color,
                                 font=("Segoe UI", 12, "bold"), relief="flat")
                label.pack(expand=True, fill="both", padx=1, pady=1)

                morse_frame = tk.Frame(frame, bg=self.key_color)
                morse_frame.pack(pady=2)
                code = self.morse_dict.get(key, "")
                for sym in code:
                    color = self.dot_color if sym == '.' else self.dash_color
                    tk.Label(morse_frame, text='●' if sym == '.' else '▬', fg=color,
                             bg=self.key_color, font=("Segoe UI", 9, "bold")).pack(side="left", padx=1)

                label.bind("<Button-1>", lambda e, k=key: self.on_key_press(k))
                self.key_labels.append(label)

            for i in range(max_columns):
                parent.grid_columnconfigure(i, weight=1)
            parent.grid_rowconfigure(r, weight=1)

    # ---------------- Key Press ----------------
    def on_key_press(self, key):
        if key == "Space":
            self.input_var.set(self.input_var.get() + " ")
        elif key == "Delete":
            self.input_var.set(self.input_var.get()[:-1])
        else:
            self.input_var.set(self.input_var.get() + key)

        self.input_box.icursor(tk.END)
        self.highlight_key(key)

    def highlight_key(self, key):
        for lbl in self.key_labels:
            if lbl.cget("text") == key:
                lbl.config(bg=self.accent_color)
                self.after(200, lambda l=lbl: l.config(bg=self.key_color))

    def on_resize(self, event):
        width = self.winfo_width()
        font_size = max(10, min(14, int(width / 100)))
        for lbl in self.key_labels:
            lbl.config(font=("Segoe UI", font_size, "bold"))

    # ---------------- Send to AI ----------------
    def send_to_ai(self):
        user_input = self.input_var.get()
        if not user_input.strip():
            return
        self.update_chat("You", user_input)

        response, suggestions = chat_with_gemini(user_input)
        self.update_chat("AI", response)
        speak(response)
        self.show_suggestions(suggestions)

        self.input_var.set("")  # Clear input

    # ---------------- Chat display ----------------
    def update_chat(self, sender, message):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"{sender}: {message}\n")
        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)

    # ---------------- Suggestions ----------------
    def show_suggestions(self, suggestions):
        for widget in self.suggestion_frame.winfo_children():
            widget.destroy()
        for s in suggestions:
            btn = tk.Button(self.suggestion_frame, text=s, command=lambda t=s: self.use_suggestion(t),
                            bg=self.accent_color, fg="#000000", width=25)
            btn.pack(side="left", padx=5)

    def use_suggestion(self, text):
        self.input_var.set(text)
        self.send_to_ai()


# ---------------- Run App ----------------
if __name__ == "__main__":
    app = DrishtiAIUI()
    app.mainloop()
