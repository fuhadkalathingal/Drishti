import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
import sqlite3
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
GEMINI_API_KEY = "AIzaSyDDPFy86k8vd5Y_3UD3SU4cciIlQjUc2c8"  # Free API key
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
DB_PATH = "user_history.db"
TOP_SUGGESTIONS = 2  # Only 2 large suggestion buttons

# -----------------------------
# DATABASE FUNCTIONS
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_history (
            user_id TEXT,
            sentence TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_sentence_to_history(user_id, sentence):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO user_history (user_id, sentence, timestamp) VALUES (?, ?, ?)",
              (user_id, sentence, datetime.now().isoformat()))
    conn.commit()
    c.execute("DELETE FROM user_history WHERE rowid NOT IN (SELECT rowid FROM user_history WHERE user_id=? ORDER BY timestamp DESC LIMIT 100)",
              (user_id,))
    conn.commit()
    conn.close()

def get_user_history(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT sentence FROM user_history WHERE user_id=? ORDER BY timestamp DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

# -----------------------------
# GEMINI API FUNCTION
# -----------------------------
def fetch_gemini_suggestions(user_id, current_input):
    history_sentences = get_user_history(user_id)
    history_text = " ".join(history_sentences[-10:])
    prompt = f"User often types: '{history_text}'. Current input: '{current_input}'. Suggest 2 full sentence completions."

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "temperature": 0.7,
        "candidate_count": TOP_SUGGESTIONS
    }

    response = requests.post(GEMINI_URL, headers=headers, json=payload)
    suggestions = []
    if response.status_code == 200:
        try:
            result = response.json()
            candidates = result.get("candidates", [])
            for cand in candidates:
                text = cand.get("content", {}).get("text", "").strip()
                if text:
                    suggestions.append(text)
        except Exception as e:
            print("Error parsing Gemini response:", e)
    else:
        print("Gemini API Error:", response.status_code, response.text)

    return suggestions[:TOP_SUGGESTIONS]

# -----------------------------
# AUTOCOMPLETE WITH LOCAL HISTORY
# -----------------------------
suggestion_cache = {}

def get_suggestions(user_id, current_input):
    history_sentences = get_user_history(user_id)
    local_suggestions = [s for s in history_sentences if s.lower().startswith(current_input.lower())]

    if len(local_suggestions) >= TOP_SUGGESTIONS:
        return local_suggestions[:TOP_SUGGESTIONS]

    if current_input in suggestion_cache:
        cached = suggestion_cache[current_input]
        combined = local_suggestions + [s for s in cached if s not in local_suggestions]
        return combined[:TOP_SUGGESTIONS]

    gemini_suggestions = fetch_gemini_suggestions(user_id, current_input)
    suggestion_cache[current_input] = gemini_suggestions

    combined = local_suggestions + [s for s in gemini_suggestions if s not in local_suggestions]
    return combined[:TOP_SUGGESTIONS]

# -----------------------------
# MAIN UI CLASS
# -----------------------------
class DrishtiUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drishti - From Vision To Voice")
        self.configure(bg="#121212")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self.user_id = "user123"
        init_db()

        self.create_styles()
        self.load_clue_images()
        self.build_layout()

    # -----------------------------
    # STYLES
    # -----------------------------
    def create_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#121212")
        style.configure("Card.TFrame", background="#1E1E1E", relief="raised", borderwidth=2)
        style.configure("TLabel", background="#121212", foreground="white", font=("Segoe UI", 16))
        style.configure("BoxLabel.TLabel", background="#1E1E1E", foreground="white", font=("Segoe UI", 22, "bold"), padding=5)
        style.configure("TButton", background="#1E1E1E", foreground="white", font=("Segoe UI", 16), padding=10)
        style.map("TButton", background=[("active", "#333333")])

    # -----------------------------
    # LOAD CLUE IMAGES
    # -----------------------------
    def load_clue_images(self):
        self.clues = {}
        paths = {
            "top": "images/up.jpg",
            "special": "images/special.jpg",
            "left": "images/left.jpg",
            "right": "images/right.jpg"
        }
        for key, path in paths.items():
            if os.path.exists(path):
                img = Image.open(path).resize((100, 60))
            else:
                img = Image.new("RGB", (100,60), color=(60,60,60))
            self.clues[key] = ImageTk.PhotoImage(img)

    # -----------------------------
    # BUILD LAYOUT
    # -----------------------------
    def build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # ---------- TITLE ----------
        title_label = ttk.Label(self, text="Drishti", font=("Segoe UI", 24, "bold"), foreground="#FFFFFF", background="#121212")
        title_label.grid(row=0, column=0, sticky="nw", padx=20, pady=10)

        # ---------- CENTERED 2x2 GRID ----------
        grid_frame = ttk.Frame(self, style="TFrame")
        grid_frame.grid(row=1, column=0, sticky="nsew")
        grid_frame.grid_columnconfigure((0,1), weight=1, uniform="col")
        grid_frame.grid_rowconfigure((0,1), weight=1, uniform="row")

        # --- Top Box A-H ---
        top_frame = ttk.Frame(grid_frame, style="Card.TFrame")
        top_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        top_label = tk.Label(top_frame, image=self.clues["top"], bg="#121212")
        top_label.pack(pady=5)
        for ch in "ABCDEFGH":
            lbl = ttk.Label(top_frame, text=ch, style="BoxLabel.TLabel")
            lbl.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        # --- Special Function Box ---
        special_frame = ttk.Frame(grid_frame, style="Card.TFrame")
        special_frame.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")
        special_label = tk.Label(special_frame, image=self.clues["special"], bg="#121212")
        special_label.pack(pady=5)
        special_buttons = [("⌫", self.delete_char), ("⬜", self.add_space), ("🗑️", self.reset_text)]
        for icon, func in special_buttons:
            btn = ttk.Button(special_frame, text=icon, command=func)
            btn.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        # --- Left Box I-Q ---
        left_frame = ttk.Frame(grid_frame, style="Card.TFrame")
        left_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        left_label = tk.Label(left_frame, image=self.clues["left"], bg="#121212")
        left_label.pack(pady=5)
        for ch in "IJKLMNOPQ":
            lbl = ttk.Label(left_frame, text=ch, style="BoxLabel.TLabel")
            lbl.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        # --- Right Box R-Z ---
        right_frame = ttk.Frame(grid_frame, style="Card.TFrame")
        right_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        right_label = tk.Label(right_frame, image=self.clues["right"], bg="#121212")
        right_label.pack(pady=5)
        for ch in "RSTUVWXYZ":
            lbl = ttk.Label(right_frame, text=ch, style="BoxLabel.TLabel")
            lbl.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        # ---------- SUGGESTION BUTTONS (2 LARGE) ----------
        self.suggestion_frame = ttk.Frame(self)
        self.suggestion_frame.grid(row=2, column=0, pady=(10, 5), padx=200, sticky="ew")
        self.suggestion_frame.grid_columnconfigure((0,1), weight=1)
        self.suggestion_buttons = []
        for i in range(TOP_SUGGESTIONS):
            btn = ttk.Button(self.suggestion_frame, text=f"Suggestion {i+1}", command=lambda idx=i: self.apply_suggestion(idx))
            btn.grid(row=0, column=i, padx=20, sticky="nsew", ipadx=10, ipady=10)
            self.suggestion_buttons.append(btn)

        # ---------- TEXT BOX BELOW ----------
        middle_frame = ttk.Frame(self)
        middle_frame.grid(row=3, column=0, sticky="ew", padx=200, pady=(20, 10))
        middle_frame.grid_columnconfigure(0, weight=1)
        self.text_display = tk.Text(
            middle_frame, bg="#1E1E1E", fg="white", font=("Consolas", 20),
            wrap="word", relief="solid", bd=2, height=3
        )
        self.text_display.grid(row=0, column=0, sticky="ew")
        self.text_display.bind("<KeyRelease>", self.on_text_change)

    # -----------------------------
    # TEXT CHANGE EVENT
    # -----------------------------
    def on_text_change(self, event=None):
        current_input = self.text_display.get("1.0", "end-1c").strip()
        if not current_input:
            for btn in self.suggestion_buttons:
                btn.config(text="Suggestion")
            return
        suggestions = get_suggestions(self.user_id, current_input)
        for i, btn in enumerate(self.suggestion_buttons):
            if i < len(suggestions):
                btn.config(text=suggestions[i])
            else:
                btn.config(text="")

    # -----------------------------
    # APPLY SUGGESTION BUTTON
    # -----------------------------
    def apply_suggestion(self, idx):
        suggestion = self.suggestion_buttons[idx].cget("text")
        if suggestion:
            self.text_display.delete("1.0", "end")
            self.text_display.insert("1.0", suggestion)
            add_sentence_to_history(self.user_id, suggestion)

    # -----------------------------
    # SPECIAL BUTTON FUNCTIONS
    # -----------------------------
    def delete_char(self):
        content = self.text_display.get("1.0", "end-1c")
        if content:
            self.text_display.delete("1.0", "end")
            self.text_display.insert("1.0", content[:-1])
            self.on_text_change()

    def add_space(self):
        self.text_display.insert("end", " ")
        self.on_text_change()

    def reset_text(self):
        self.text_display.delete("1.0", "end")
        self.on_text_change()

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app = DrishtiUI()
    app.mainloop()
