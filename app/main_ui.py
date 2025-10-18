import tkinter as tk
from app.core.morse_based_typing import DataProvider
import time
import statistics

datas_obj = DataProvider()

class DrishtiKeyboardUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drishti - From Vision To Voice")
        self.configure(bg="#121212")
        self.geometry("1150x700")
        self.minsize(900, 600)

        # Theme colors
        self.bg_color = "#121212"
        self.key_color = "#1e1e1e"
        self.text_color = "#ffffff"
        self.dot_color = "#00ff7f"   # Green
        self.dash_color = "#ff4d4d"  # Red
        self.accent_color = "#03dac6"

        # Title
        title = tk.Label(self, text="DRISHTI", fg=self.accent_color, bg=self.bg_color,
                         font=("Segoe UI", 24, "bold"))
        title.pack(pady=(10, 5))

        # A frame to contain both input boxes
        input_frame = tk.Frame(self, bg=self.key_color)
        input_frame.pack(fill="x", padx=50, pady=(10, 20))

        # --- First input box (full width) ---
        self.input_var = tk.StringVar()
        input_box = tk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=("Segoe UI", 18),
            bg=self.key_color,
            fg=self.text_color,
            insertbackground=self.text_color,
            relief="flat",
            justify="left"
        )
        input_box.pack(fill="x", pady=(0, 10), ipady=10)
        self.input_box = input_box

        # --- Second input box (25% width, left-aligned) ---
        self.buffer_var = tk.StringVar()
        buffer_box = tk.Entry(
            input_frame,
            textvariable=self.buffer_var,
            font=("Segoe UI", 18),
            bg=self.key_color,
            fg=self.text_color,
            insertbackground=self.text_color,
            relief="flat",
            justify="left"
        )
        buffer_box.pack(side="left", fill="x", expand=False, ipadx=10, ipady=10)
        input_frame.bind(
            "<Configure>",
            lambda e: buffer_box.config(width=int(e.width * 0.25 / 10))
        )
        self.second_box = buffer_box

        # Suggestion boxes
        self.word_labels = []
        self.create_suggestions()

        # Main container (keyboard + clue)
        layout_frame = tk.Frame(self, bg=self.bg_color)
        layout_frame.pack(expand=True, fill="both", padx=20, pady=10)
        layout_frame.columnconfigure(0, weight=3)
        layout_frame.columnconfigure(1, weight=1)
        layout_frame.rowconfigure(0, weight=1)

        # Keyboard (left)
        kb_frame = tk.Frame(layout_frame, bg=self.bg_color)
        kb_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        self.create_keyboard(kb_frame)

        # Blink clue box (right)
        self.create_blink_clue(layout_frame)

        # Responsive resizing
        self.bind("<Configure>", self.on_resize)

        # Metrics setup (added)
        self.metrics_logger = PerformanceLogger(self)

        # Button to view metrics
        tk.Button(self, text="View Metrics", bg=self.accent_color, fg="black",
                  font=("Segoe UI", 12, "bold"), relief="flat",
                  command=self.metrics_logger.show_metrics_window).pack(pady=(0, 10))

        # Updating the main input class
        self.fast_loop()

    def fast_loop(self):
        datas_obj.update_all()
        self.input_var.set(f'"{datas_obj.written_string}"')
        buffer_string = datas_obj.buffer.replace('.', '●').replace('-', '▬')
        self.buffer_var.set(buffer_string)

        for i in range(4):
            self.word_labels[i].config(text=datas_obj.current_suggestion["suggestion"][i],
                                       bg=self.key_color)
        if datas_obj.current_level == 1:
            self.word_labels[datas_obj.selected_suggestion_index].config(bg="dark blue")

        # --- Added metric tracking ---
        self.metrics_logger.update(self.input_var.get())

        self.after(100, self.fast_loop)  # slightly slower loop (100ms)

    def create_suggestions(self):
        suggestion_frame = tk.Frame(self, bg=self.bg_color)
        suggestion_frame.pack(pady=(0, 10))

        word_frame = tk.Frame(suggestion_frame, bg=self.bg_color)
        word_frame.pack()
        for i in range(4):
            lbl = tk.Label(word_frame, text="", bg=self.key_color, fg=self.text_color,
                           font=("Segoe UI", 12), padx=15, pady=8)
            lbl.grid(row=0, column=i, padx=5)
            self.word_labels.append(lbl)

        sent_frame = tk.Frame(suggestion_frame, bg=self.bg_color)
        sent_frame.pack(pady=(10, 0))
        for i in range(2):
            lbl = tk.Label(sent_frame, text=f"Sentence{i+1}", bg=self.key_color,
                           fg=self.text_color, font=("Segoe UI", 12),
                           padx=30, pady=10)
            lbl.grid(row=0, column=i, padx=10)

    def create_keyboard(self, parent):
        self.keyboard_layout = [
            ['A','B','C','D','E','F','G','H','I','J'],
            ['K','L','M','N','O','P','Q','R','S','T'],
            ['U','V','W','X','Y','Z'],
            ['Space','Delete','Play','Chat']
        ]

        self.morse_dict = {
            'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....',
            'I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.',
            'Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-',
            'Y':'-.--','Z':'--..','Space':'.....','Delete':'-----','Play':'...--','Chat':'---..'
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

    def create_blink_clue(self, parent):
        clue_frame = tk.Frame(parent, bg=self.key_color, relief="flat", padx=20, pady=20)
        clue_frame.grid(row=0, column=1, sticky="nsew")

        tk.Label(clue_frame, text="Blink Timing Guide", fg=self.accent_color,
                 bg=self.key_color, font=("Segoe UI", 14, "bold")).pack(pady=(0,10))
        tk.Label(clue_frame, text="●  Fast Blink → Dot", fg=self.dot_color,
                 bg=self.key_color, font=("Segoe UI", 12)).pack(anchor="w")
        tk.Label(clue_frame, text="▬  Slow Blink → Dash", fg=self.dash_color,
                 bg=self.key_color, font=("Segoe UI", 12)).pack(anchor="w")
        tk.Label(clue_frame, text="⏱  Very Slow Blink → Enter", fg=self.text_color,
                 bg=self.key_color, font=("Segoe UI", 12)).pack(anchor="w", pady=(10,0))
        tk.Label(clue_frame, text="Left → Delete Letter", fg=self.text_color,
                 bg=self.key_color, font=("Segoe UI", 12)).pack(anchor="w", pady=(10, 0))

    def on_key_press(self, key):
        if key == "Space":
            self.input_var.set(self.input_var.get() + " ")
        elif key == "Delete":
            self.input_var.set(self.input_var.get()[:-1])
        else:
            self.input_var.set(self.input_var.get() + key)
        self.input_box.icursor(tk.END)
        self.highlight_key(key)
        # Add keystroke event to metrics
        self.metrics_logger.record_key(key)

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


# ---------------------- NEW METRICS CLASS ----------------------
class PerformanceLogger:
    def __init__(self, app):
        self.app = app
        self.start_time = time.time()
        self.last_text = ""
        self.key_events = []
        self.metrics_window = None
        self.false_blinks = 0

    def record_key(self, key):
        self.key_events.append((key, time.time()))

    def update(self, current_text):
        # Update metrics continuously
        text = current_text.strip('"')
        if len(text) < len(self.last_text):
            # deletion detected
            pass
        elif len(text) > len(self.last_text):
            # new character added
            pass
        self.last_text = text

    def calculate_metrics(self):
        elapsed_min = max((time.time() - self.start_time) / 60.0, 1e-6)
        chars = len(self.last_text)
        wpm = (chars / 5.0) / elapsed_min
        errors = self.last_text.count("❌")  # optional marker
        accuracy = 100 - (errors / max(1, chars)) * 100
        avg_latency = 0
        if len(self.key_events) > 1:
            intervals = [self.key_events[i+1][1] - self.key_events[i][1] for i in range(len(self.key_events)-1)]
            avg_latency = statistics.mean(intervals)
        return {
            "Elapsed Time (min)": round(elapsed_min, 2),
            "Typed Chars": chars,
            "WPM": round(wpm, 2),
            "Accuracy (%)": round(accuracy, 2),
            "False Blinks": self.false_blinks,
            "Avg Key Interval (s)": round(avg_latency, 2)
        }

    def show_metrics_window(self):
        if self.metrics_window and tk.Toplevel.winfo_exists(self.metrics_window):
            self.metrics_window.lift()
            return

        self.metrics_window = tk.Toplevel(self.app)
        self.metrics_window.title("Drishti - Performance Metrics")
        self.metrics_window.geometry("500x300")
        self.metrics_window.configure(bg="#121212")

        tk.Label(self.metrics_window, text="Performance Metrics",
                 bg="#121212", fg="#03dac6", font=("Segoe UI", 16, "bold")).pack(pady=10)

        self.metric_labels = {}
        for k, v in self.calculate_metrics().items():
            frame = tk.Frame(self.metrics_window, bg="#121212")
            frame.pack(anchor="w", pady=3)
            tk.Label(frame, text=f"{k}:", bg="#121212", fg="#ffffff", width=22,
                     anchor="w", font=("Segoe UI", 12)).pack(side="left")
            val = tk.Label(frame, text=str(v), bg="#121212", fg="#00ff7f",
                           font=("Segoe UI", 12, "bold"))
            val.pack(side="left")
            self.metric_labels[k] = val

        tk.Button(self.metrics_window, text="Refresh Metrics", bg="#03dac6", fg="black",
                  font=("Segoe UI", 11, "bold"), relief="flat",
                  command=self.refresh_metrics).pack(pady=10)

    def refresh_metrics(self):
        metrics = self.calculate_metrics()
        for k, lbl in self.metric_labels.items():
            lbl.config(text=str(metrics[k]))


# ---------------------- RUN APP ----------------------
if __name__ == "__main__":
    app = DrishtiKeyboardUI()
    app.mainloop()
