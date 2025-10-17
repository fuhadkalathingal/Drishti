import os
import tkinter as tk
import pyttsx3
import random
import threading
import time

# ----------------------------
# Gemini API Setup
# ----------------------------
try:
    from google import genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    # Note: If the Google GenAI SDK is not available, AI functions will use placeholders.

# WARNING: Replace with your actual key for functionality
API_KEY = "AIzaSyDDPFy86k8vd5Y_3UD3SU4cciIlQjUc2c8"
MODEL_NAME = "gemini-2.5-flash"


def chat_with_gemini(prompt, user_name=None):
    """Handles the communication with the Gemini API for primary response and suggestions."""
    if not GEMINI_AVAILABLE:
        return "Drishti is currently unavailable. Please install the Google GenAI SDK.", []

    try:
        client = genai.Client(api_key=API_KEY)

        # System prompt is enhanced to guide suggestions and conversation flow
        system_prompt = f"""
You are Drishti, a friendly, empathetic, and supportive AI companion for people with ALS.
- Always maintain a gentle and caring tone.
- Your primary goal is to provide comfort, information, or light engagement.
- After every response, ask a single, short, open-ended question that encourages a caring conversation flow.
- Use the user's name naturally if known.
"""
        if user_name:
            system_prompt += f"\n- User's name is {user_name}."

        full_prompt = f"{system_prompt}\nUser: {prompt}\nDrishti:"

        # 1. Get main response (including the suggested follow-up question)
        main_resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt
        )
        main_text = main_resp.text.strip()

        # 2. Generate conversation suggestions based on the response
        suggestion_resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"""
Given Drishti's reply: "{main_text}", suggest 3 short, relevant replies the user might type to keep the conversation flowing naturally.
Format them as: Reply 1 | Reply 2 | Reply 3
"""
        )
        suggestion_text = suggestion_resp.text.strip()
        suggestions = [s.strip() for s in suggestion_text.split('|') if s.strip()][:3]

        return main_text, suggestions

    except Exception as e:
        print(f"Gemini API failed: {e}")
        return "Drishti response unavailable due to API error. Try checking your internet connection.", []


# ----------------------------
# Text-to-Speech Setup (Refactored for Reliability)
# ----------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 150)
voices = engine.getProperty('voices')
target_voice_id = None

# Set a preferred voice (e.g., female if available)
for voice in voices:
    if "female" in voice.name.lower() or "zira" in voice.name.lower() or "samantha" in voice.name.lower():
        target_voice_id = voice.id
        break
if target_voice_id:
    engine.setProperty('voice', target_voice_id)


def speak(text):
    """
    Speaks the text in a separate daemon thread.
    This structure is crucial to prevent the main UI thread from blocking.
    """

    def run_speech():
        try:
            # Ensure any previous speech is stopped before starting a new one
            engine.stop()
            engine.say(text)
            # This blocking call MUST happen inside the thread
            engine.runAndWait()
        except Exception as e:
            # This print is for local debugging, it won't show in the Canvas environment
            print(f"Speech engine error during runAndWait: {e}")

            # Start the daemon thread to handle the blocking speech process

    threading.Thread(target=run_speech, daemon=True).start()


# ----------------------------
# Music Playback (Using OS commands)
# ----------------------------
MUSIC_FOLDER = "C:\\Users\\HOME-PC\\Music"


def play_song():
    """Attempts to play a random song using the OS command line."""
    try:
        songs = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(".mp3")]
        if not songs:
            speak("No songs found in your music folder.")
            return
        song_to_play = os.path.join(MUSIC_FOLDER, random.choice(songs))
        speak(f"Playing {os.path.basename(song_to_play)}")
        os.system(f'start "" "{song_to_play}"')
    except Exception as e:
        speak(f"Error playing song: {e}. Check your MUSIC_FOLDER path and content.")


# ----------------------------
# Drishti AI UI (Responsive Layout)
# ----------------------------
class DrishtiAIUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drishti - From Vision To Voice")
        self.configure(bg="#121212")
        self.geometry("1150x700")
        self.minsize(600, 500)

        # Colors and Settings
        self.bg_color = "#121212"
        self.key_color = "#1e1e1e"
        self.text_color = "#ffffff"
        self.accent_color = "#03dac6"  # Teal for a calm, friendly feel
        self.user_name = None
        self.name_asked = True
        self.last_input_time = time.time()
        self.idle_seconds = 45  # Reduced idle time for more engagement
        self.typing_animation_active = False
        self.typing_animation_id = None

        self.setup_layout()
        # Start idle check after a delay
        self.after(5000, self.check_idle)

    def setup_layout(self):
        """Uses grid layout for superior responsiveness, without the keyboard."""

        # Configure main window grid weights
        self.grid_rowconfigure(2, weight=1)  # Chat box row expands vertically
        self.grid_columnconfigure(0, weight=1)  # Single column expands horizontally

        # ---------------- 1. Title ----------------
        title = tk.Label(self, text="DRISHTI", fg=self.accent_color, bg=self.bg_color,
                         font=("Segoe UI", 28, "bold"))
        title.grid(row=0, column=0, pady=(20, 10), sticky="n")

        # ---------------- 2. Input Box ----------------
        self.input_var = tk.StringVar()
        self.input_box = tk.Entry(self, textvariable=self.input_var,
                                  font=("Segoe UI", 18), bg=self.key_color, fg=self.text_color,
                                  insertbackground=self.text_color, relief="flat", justify="left")
        self.input_box.grid(row=1, column=0, padx=50, pady=(0, 20), ipady=10, sticky="ew")
        self.input_box.insert(0, "Enter your name to begin...")
        self.input_box.bind("<FocusIn>", self.clear_placeholder)
        self.input_box.bind("<FocusOut>", self.add_placeholder)
        self.input_box.bind("<Return>", lambda e: self.send_to_ai())

        # ---------------- 3. Chat Display ----------------
        self.chat_box = tk.Text(self, state=tk.DISABLED, bg="#1c1c1c", fg="#ffffff",
                                font=("Segoe UI", 14), padx=15, pady=15, relief="flat")
        self.chat_box.grid(row=2, column=0, padx=50, pady=(0, 10), sticky="nsew")

        # ---------------- 4. Suggestion Buttons Frame ----------------
        self.suggestion_frame = tk.Frame(self, bg=self.bg_color)
        self.suggestion_frame.grid(row=3, column=0, pady=(0, 15), sticky="n")

        # ---------------- 5. Action Buttons Frame ----------------
        action_frame = tk.Frame(self, bg=self.bg_color)
        action_frame.grid(row=4, column=0, pady=(0, 20), sticky="n")

        tk.Button(action_frame, text="Send", command=self.send_to_ai, bg=self.accent_color,
                  fg="#000000", width=12, font=("Segoe UI", 12, "bold"), relief="flat").pack(side="left", padx=15)

        tk.Button(action_frame, text="Play Music", command=play_song, bg=self.accent_color,
                  fg="#000000", width=12, font=("Segoe UI", 12, "bold"), relief="flat").pack(side="left", padx=15)

    # ---------------- Placeholder Handling ----------------
    def clear_placeholder(self, event):
        """Clears the placeholder text when the box is focused."""
        if self.input_box.get() in ["Enter your name to begin...", "Type your message..."]:
            self.input_box.delete(0, tk.END)

    def add_placeholder(self, event):
        """Adds placeholder text when the box is empty and unfocused."""
        if not self.input_box.get():
            placeholder = "Enter your name to begin..." if self.name_asked else "Type your message..."
            self.input_box.insert(0, placeholder)

    # ---------------- Chat Handling ----------------
    def update_chat(self, sender, message):
        """Adds a standard message (typically user's) and ensures auto-scroll."""
        self.chat_box.config(state=tk.NORMAL)
        # Apply a tag for potential styling later
        self.chat_box.insert(tk.END, f"{sender}: {message}\n", sender.lower().replace(" ", "_"))
        self.chat_box.see(tk.END)  # Auto-scroll functionality
        self.chat_box.config(state=tk.DISABLED)

    # ---------------- Typing Animation ----------------
    def start_thinking_placeholder(self):
        """Starts a simple dot wave animation (text-based) for thinking."""
        if self.typing_animation_active: return

        self.typing_animation_active = True
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, "Drishti: Thinking...", "thinking_tag")
        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)

        def animate_dots(step=0):
            if not self.typing_animation_active: return

            dots = ['.', '..', '...']
            dot_text = dots[step % 3]

            self.chat_box.config(state=tk.NORMAL)
            # Search backwards for the most recent "Drishti: " to find the line
            start_index = self.chat_box.search("Drishti: ", "1.0", tk.END, nocase=True, backwards=True)

            if start_index:
                # Calculate the start of the 'Thinking...' text
                line_start = self.chat_box.index(f"{start_index} + 9 chars")
                # Calculate the end of the line
                line_end = self.chat_box.index(f"{line_start} lineend")

                # Delete old dots and insert new dots
                self.chat_box.delete(line_start, line_end)
                self.chat_box.insert(line_start, f"Thinking{dot_text}")
                self.chat_box.see(tk.END)

            self.chat_box.config(state=tk.DISABLED)
            # Schedule the next step
            self.typing_animation_id = self.after(400, lambda: animate_dots(step + 1))

        self.typing_animation_id = self.after(0, lambda: animate_dots())

    def stop_thinking_placeholder(self):
        """Stops the animation timer."""
        self.typing_animation_active = False
        if self.typing_animation_id:
            self.after_cancel(self.typing_animation_id)
            self.typing_animation_id = None

    def replace_placeholder_with_response(self, message):
        """Replaces the 'Drishti: Thinking...' line with the final, animated response."""
        self.stop_thinking_placeholder()

        self.chat_box.config(state=tk.NORMAL)

        # 1. Find the start of the 'Drishti: Thinking...' line
        start_index = self.chat_box.search("Drishti: ", "1.0", tk.END, nocase=True, backwards=True)

        if start_index:
            line_start = self.chat_box.index(f"{start_index} linestart")
            line_end = self.chat_box.index(f"{line_start} lineend + 1c")

            # 2. Delete the entire placeholder line
            self.chat_box.delete(line_start, line_end)

        self.chat_box.config(state=tk.DISABLED)

        # 3. Start typing the actual response content
        self.type_ai_response(message)

    def type_ai_response(self, message):
        """Animates the AI's final response character by character."""
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, "Drishti: ")
        self.chat_box.config(state=tk.DISABLED)

        def animate():
            for char in message:
                self.chat_box.config(state=tk.NORMAL)
                self.chat_box.insert(tk.END, char)
                self.chat_box.see(tk.END)
                self.chat_box.config(state=tk.DISABLED)
                time.sleep(0.03)

            # Finalize the line
            self.chat_box.config(state=tk.NORMAL)
            self.chat_box.insert(tk.END, "\n")
            self.chat_box.see(tk.END)
            self.chat_box.config(state=tk.DISABLED)

        threading.Thread(target=animate, daemon=True).start()

    # ---------------- Suggestions ----------------
    def show_suggestions(self, suggestions):
        """Displays conversation suggestions as clickable buttons."""
        for widget in self.suggestion_frame.winfo_children():
            widget.destroy()

        for s in suggestions[:3]:
            btn = tk.Button(self.suggestion_frame, text=s, command=lambda t=s: self.use_suggestion(t),
                            bg=self.accent_color, fg="#000000", padx=10, pady=5, font=("Segoe UI", 11), relief="flat")
            btn.pack(side="left", padx=5)

    def use_suggestion(self, text):
        """Fills the input box and sends the suggestion as a new message."""
        self.input_var.set(text)
        self.send_to_ai()

    # ---------------- Send to AI Logic ----------------
    def send_to_ai(self):
        user_input = self.input_var.get().strip()

        placeholder_texts = ["Enter your name to begin...", "Type your message..."]
        if not user_input or user_input in placeholder_texts:
            return

        self.last_input_time = time.time()

        # Update user's message to chat box
        self.update_chat("You", user_input)

        # Clear and reset input box placeholder
        self.input_var.set("")
        self.input_box.delete(0, tk.END)
        self.input_box.insert(0, "Type your message...")

        # 1. Handle first name input (no API call needed)
        if self.user_name is None and self.name_asked:
            self.user_name = user_input
            welcome_msg = f"It's wonderful to meet you, {self.user_name}. I'm Drishti, and I'm here to chat whenever you need me. How are you feeling today?"

            speak(welcome_msg)
            self.replace_placeholder_with_response(welcome_msg)
            self.name_asked = False
            self.show_suggestions(["I'm okay", "A little tired", "What can you do?"])
            return

        # 2. Handle subsequent API calls
        self.start_thinking_placeholder()  # Start dot wave animation

        def get_response():
            response, suggestions = chat_with_gemini(user_input, self.user_name)

            # The AI's response text, ready for output
            full_ai_message = response

            # CRITICAL: Ensure audio starts before or immediately with the text animation
            speak(full_ai_message)

            # Stop animation and replace with the final response text
            self.replace_placeholder_with_response(full_ai_message)

            self.show_suggestions(suggestions if suggestions else ["Tell me more", "Thanks", "Change the subject"])

        # Run the API call in a separate thread
        threading.Thread(target=get_response, daemon=True).start()

    # ---------------- Idle Questions ----------------
    def check_idle(self):
        """Triggers a friendly prompt if the user is inactive."""
        friendly_questions = [
            "Just checking in. Is there anything on your mind right now?",
            "Would you like me to read a positive quote for you?",
            "It's quiet. Would you like to hear a fun fact about the world?",
            "We haven't chatted in a minute. Is there a topic you'd like to discuss?"
        ]

        # Check if user is known, if not busy, and if idle time is exceeded
        if self.user_name and (
                time.time() - self.last_input_time > self.idle_seconds) and not self.typing_animation_active:
            question = random.choice(friendly_questions)

            speak(question)
            self.type_ai_response(question)
            self.show_suggestions(["I'm fine", "Tell me the quote", "Yes, please"])
            self.last_input_time = time.time()

        # Re-schedule the check
        self.after(5000, self.check_idle)


# ---------------- Run ----------------
if __name__ == "__main__":
    app = DrishtiAIUI()
    app.mainloop()