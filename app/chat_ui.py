import os
import tkinter as tk
import random
import threading
import time
import json
from pathlib import Path
from app.utils.speech import speak
from dotenv import load_dotenv
from groq import Groq
from app.core.eye_gesture import get_gesture_frame

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
USERNAME_FILE = Path("cache/username.json")


def chat_with_gemini(prompt, user_name=None):
    try:
        system_prompt = f"""
        You are Drishti, a friendly, empathetic, and supportive AI companion for people with ALS.
        - Always maintain a gentle and caring tone.
        - Use the user's name naturally if known.
        """
        if user_name:
            system_prompt += f"\n- User's name is {user_name}."
        full_prompt = f"{system_prompt}\nUser: {prompt}\nDrishti:"
        main_resp = client.chat.completions.create(
            messages=[{"role": "system", "content": full_prompt}, {"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        main_text = main_resp.choices[0].message.content.strip()
        return main_text
    except Exception as e:
        print(f"Groq API failed: {e}")
        return "Drishti response unavailable due to API error."


def use_speak(text):
    threading.Thread(target=lambda: speak(text), daemon=True).start()


MUSIC_FOLDER = "C:\\Users\\HOME-PC\\Music"

def play_song():
    try:
        songs = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(".mp3")]
        if not songs:
            speak("No songs found in your music folder.")
            return
        song_to_play = os.path.join(MUSIC_FOLDER, random.choice(songs))
        speak(f"Playing {os.path.basename(song_to_play)}")
        os.system(f'start "" "{song_to_play}"')
    except Exception as e:
        speak(f"Error playing song: {e}.")


class DrishtiAIUI(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.title("Drishti - From Vision To Voice")
        self.configure(bg="#121212")
        self.geometry("1150x700")
        self.minsize(600, 500)

        self.bg_color = "#121212"
        self.key_color = "#1e1e1e"
        self.text_color = "#ffffff"
        self.accent_color = "#03dac6"
        self.highlight_color = "#2673CC"
        self.close_highlight = "#FF4E4E"

        self.user_name = self.load_username()
        self.current_focus = "suggestion"
        self.highlighted_suggestion_index = 0
        self.highlighted_action_index = 0
        self.running = True

        self.setup_layout()
        self.after(1000, self.initial_greeting)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        threading.Thread(target=self.monitor_blinks, daemon=True).start()

    def load_username(self):
        try:
            if USERNAME_FILE.exists():
                with open(USERNAME_FILE, "r") as f:
                    return json.load(f).get("name", "Friend")
        except Exception:
            pass
        return "Friend"

    def setup_layout(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title = tk.Label(self, text="DRISHTI", fg=self.accent_color, bg=self.bg_color,
                         font=("Segoe UI", 28, "bold"))
        title.grid(row=0, column=0, pady=(20, 10), sticky="n")

        self.chat_box = tk.Text(self, state=tk.DISABLED, bg="#1c1c1c", fg="#ffffff",
                                font=("Segoe UI", 14), padx=15, pady=15, relief="flat")
        self.chat_box.grid(row=2, column=0, padx=50, pady=(0, 10), sticky="nsew")

        self.suggestion_frame = tk.Frame(self, bg=self.bg_color)
        self.suggestion_frame.grid(row=3, column=0, pady=(0, 15), sticky="n")

        self.action_frame = tk.Frame(self, bg=self.bg_color)
        self.action_frame.grid(row=4, column=0, pady=(0, 20), sticky="n")

        self.close_btn = tk.Button(self.action_frame, text="Close", command=self.close_program,
                                   bg=self.accent_color, fg="#000000", width=12,
                                   font=("Segoe UI", 12, "bold"), relief="flat", bd=2)
        self.close_btn.pack(side="left", padx=15)

        self.music_btn = tk.Button(self.action_frame, text="Play Music", command=play_song,
                                   bg=self.accent_color, fg="#000000", width=12,
                                   font=("Segoe UI", 12, "bold"), relief="flat", bd=2)
        self.music_btn.pack(side="left", padx=15)

        self.action_buttons = [self.close_btn, self.music_btn]

        # Focus indicator
        self.focus_label = tk.Label(self, text="Focus: Suggestions", fg=self.highlight_color,
                                    bg=self.bg_color, font=("Segoe UI", 12, "italic"))
        self.focus_label.grid(row=5, column=0, pady=(0, 10))

    def initial_greeting(self):
        greetings = [
            f"Hi {self.user_name}! How are you feeling today?",
            f"Hey {self.user_name}, how’s your day going?",
            f"Good to see you, {self.user_name}! How have you been?"
        ]
        message = random.choice(greetings)
        use_speak(message)
        self.type_ai_response(message)
        self.show_suggestions(["I'm good", "Feeling tired", "Let's talk about something"])

    def update_chat(self, sender, message):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"{sender}: {message}\n")
        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)

    def type_ai_response(self, message):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, "Drishti: ")
        self.chat_box.config(state=tk.DISABLED)

        def animate():
            for char in message:
                self.chat_box.config(state=tk.NORMAL)
                self.chat_box.insert(tk.END, char)
                self.chat_box.see(tk.END)
                self.chat_box.config(state=tk.DISABLED)
                time.sleep(0.02)
            self.chat_box.config(state=tk.NORMAL)
            self.chat_box.insert(tk.END, "\n")
            self.chat_box.config(state=tk.DISABLED)
        threading.Thread(target=animate, daemon=True).start()

    def show_suggestions(self, suggestions):
        for widget in self.suggestion_frame.winfo_children():
            widget.destroy()
        self.suggestion_buttons = []
        for s in suggestions[:3]:
            btn = tk.Button(self.suggestion_frame, text=s, command=lambda t=s: self.send_to_ai(t),
                            bg=self.accent_color, fg="#000000", padx=10, pady=5,
                            font=("Segoe UI", 11), relief="flat", bd=2, width=20)
            btn.pack(side="left", padx=5)
            self.suggestion_buttons.append(btn)
        self.highlighted_suggestion_index = 0
        self.highlight_suggestion()

    def highlight_suggestion(self):
        if not hasattr(self, 'suggestion_buttons') or not self.suggestion_buttons:
            return
        for i, btn in enumerate(self.suggestion_buttons):
            if i == self.highlighted_suggestion_index:
                btn.config(bg=self.highlight_color, fg="#FFFFFF")
            else:
                btn.config(bg=self.accent_color, fg="#000000")

    def highlight_action(self):
        for i, btn in enumerate(self.action_buttons):
            if i == self.highlighted_action_index:
                color = self.close_highlight if btn == self.close_btn else self.highlight_color
                btn.config(bg=color, fg="#FFFFFF")
            else:
                btn.config(bg=self.accent_color, fg="#000000")

    def monitor_blinks(self):
        while self.running:
            event = get_gesture_frame()
            if not self.running:
                break
            if event == "FU":
                self.toggle_focus()
            elif self.current_focus == "suggestion":
                if event == "FB":
                    self.cycle_suggestion()
                elif event in ("SB", "VSB"):
                    self.select_highlighted_suggestion()
            elif self.current_focus == "action":
                if event == "FB":
                    self.cycle_action()
                elif event in ("SB", "VSB"):
                    self.select_highlighted_action()

    def clear_suggestion_highlight(self):
        """Reset all suggestion button colors to normal."""
        if hasattr(self, "suggestion_buttons"):
            for btn in self.suggestion_buttons:
                btn.config(bg=self.accent_color, fg="#000000")

    def clear_action_highlight(self):
        """Reset all action button colors to normal."""
        for btn in self.action_buttons:
            btn.config(bg=self.accent_color, fg="#000000")

    def toggle_focus(self):
        """Switch between suggestion and action focus."""
        # Switch the focus
        self.current_focus = "action" if self.current_focus == "suggestion" else "suggestion"

        if self.current_focus == "suggestion":
            # Clear highlights from action buttons
            self.clear_action_highlight()
            # Update label and highlight selected suggestion
            self.focus_label.config(text="Focus: Suggestions", fg=self.highlight_color)
            self.highlight_suggestion()

        else:
            # Clear highlights from suggestion buttons
            self.clear_suggestion_highlight()
            # Update label and highlight selected action
            self.focus_label.config(text="Focus: Actions", fg="#FFA500")
            self.highlight_action()

    def cycle_suggestion(self):
        if not hasattr(self, 'suggestion_buttons') or not self.suggestion_buttons:
            return
        self.highlighted_suggestion_index = (self.highlighted_suggestion_index + 1) % len(self.suggestion_buttons)
        self.highlight_suggestion()

    def cycle_action(self):
        self.highlighted_action_index = (self.highlighted_action_index + 1) % len(self.action_buttons)
        self.highlight_action()

    def select_highlighted_suggestion(self):
        if hasattr(self, 'suggestion_buttons') and self.suggestion_buttons:
            btn = self.suggestion_buttons[self.highlighted_suggestion_index]
            btn.invoke()

    def select_highlighted_action(self):
        btn = self.action_buttons[self.highlighted_action_index]
        btn.invoke()

    def send_to_ai(self, text):
        self.update_chat("You", text)
        response = chat_with_gemini(text, self.user_name)
        use_speak(response)
        self.type_ai_response(response)
        self.show_suggestions(["Tell me more", "Thanks", "Change topic"])

    def close_program(self):
        use_speak("Goodbye!")
        self.on_close()

    def on_close(self):
        self.running = False
        self.destroy()
        if self.master:
            self.master.deiconify()


def run_chat_ui(root):
    root.withdraw()
    app = DrishtiAIUI(root)
    app.mainloop()
