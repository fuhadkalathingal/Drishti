import tkinter as tk
from app.core.morse_based_typing import DataProvider

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
        # Use frame width to control size dynamically
        input_frame.bind(
            "<Configure>",
            lambda e: buffer_box.config(width=int(e.width * 0.25 / 10))  # 25% width dynamically
        )

        self.second_box = buffer_box

        # Suggestion boxes
        self.word_labels = []
        self.create_suggestions()

        # Main container (keyboard + clue)
        layout_frame = tk.Frame(self, bg=self.bg_color)
        layout_frame.pack(expand=True, fill="both", padx=20, pady=10)
        layout_frame.columnconfigure(0, weight=3)  # keyboard takes 3 parts
        layout_frame.columnconfigure(1, weight=1)  # clue box takes 1 part
        layout_frame.rowconfigure(0, weight=1)

        # Keyboard (left)
        kb_frame = tk.Frame(layout_frame, bg=self.bg_color)
        kb_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        self.create_keyboard(kb_frame)

        # Blink clue box (right)
        self.create_blink_clue(layout_frame)

        # Responsive resizing behavior
        self.bind("<Configure>", self.on_resize)

        # Updating the main input class
        self.fast_loop()

    def fast_loop(self):
        # Update all of the actions
        datas_obj.update_all()

        # Set the written string onto the textbox
        self.input_var.set(datas_obj.written_string)
        self.buffer_var.set(datas_obj.buffer)

        # Reset all boxes to normal color
        for i in range(4):
            self.word_labels[i].config(text=datas_obj.current_suggestion["suggestion"][i] ,bg=self.key_color)  # reset background

        # Highlight the selected box
        if datas_obj.current_level == 1:
            self.word_labels[datas_obj.selected_suggestion_index].config(bg="dark blue")

        self.after(1, self.fast_loop)

    def create_suggestions(self):
        suggestion_frame = tk.Frame(self, bg=self.bg_color)
        suggestion_frame.pack(pady=(0, 10))

        # Word suggestions
        word_frame = tk.Frame(suggestion_frame, bg=self.bg_color)
        word_frame.pack()
        for i in range(4):
            lbl = tk.Label(word_frame, text="", bg=self.key_color, fg=self.text_color,
                           font=("Segoe UI", 12), padx=15, pady=8)
            lbl.grid(row=0, column=i, padx=5)
            self.word_labels.append(lbl)

        # Sentence suggestions
        sent_frame = tk.Frame(suggestion_frame, bg=self.bg_color)
        sent_frame.pack(pady=(10, 0))
        for i in range(2):
            lbl = tk.Label(sent_frame, text=f"Sentence{i+1}", bg=self.key_color, fg=self.text_color,
                           font=("Segoe UI", 12), padx=30, pady=10)
            lbl.grid(row=0, column=i, padx=10)

    def create_keyboard(self, parent):
        # Updated alphabetical layout
        self.keyboard_layout = [
            #['1','2','3','4','5','6','7','8','9','0'],  # number row stays same
            ['A','B','C','D','E','F','G','H','I','J'],
            ['K','L','M','N','O','P','Q','R','S','T'],
            ['U','V','W','X','Y','Z'],
            ['Space','Delete']
        ]

        self.morse_dict = {
            #'1': '.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...',
            #'8':'---..','9':'----.','0':'-----',
            'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.',
            'F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--',
            'N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-',
            'W':'.--','X':'-..-','Y':'-.--','Z':'--..','Space':'.....','Delete':'-----'
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

                # Morse code inside key
                morse_frame = tk.Frame(frame, bg=self.key_color)
                morse_frame.pack(pady=2)
                code = self.morse_dict.get(key, "")
                for sym in code:
                    color = self.dot_color if sym == '.' else self.dash_color
                    tk.Label(morse_frame, text='●' if sym == '.' else '▬', fg=color,
                             bg=self.key_color, font=("Segoe UI", 9, "bold")).pack(side="left", padx=1)

                label.bind("<Button-1>", lambda e, k=key: self.on_key_press(k))
                self.key_labels.append(label)

            # Equal column weights for uniform key sizes
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
        tk.Label(clue_frame, text="Left Fast → Delete Morse", fg=self.text_color,
                 bg=self.key_color, font=("Segoe UI", 12)).pack(anchor="w", pady=(10, 0))
        tk.Label(clue_frame, text="Left Slow → Delete Leter", fg=self.text_color,
                 bg=self.key_color, font=("Segoe UI", 12)).pack(anchor="w", pady=(10, 0))

    def on_key_press(self, key):
        if key == "Space":
            self.input_var.set(self.input_var.get() + " ")
        elif key == "Delete":
            self.input_var.set(self.input_var.get()[:-1])
        else:
            self.input_var.set(self.input_var.get() + key)

        # Move cursor to the end
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

if __name__ == "__main__":
    app = DrishtiKeyboardUI()
    app.mainloop()
