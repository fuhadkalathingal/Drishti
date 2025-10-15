import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# -----------------------------
# CONFIG
# -----------------------------
TOP_SENTENCE_SUGGESTIONS = 2
TOP_WORD_SUGGESTIONS = 4
IMAGE_FOLDER = "images"  # Folder where clue images are stored

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

        self.create_styles()
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
        style.configure("BoxLabel.TLabel", background="#1E1E1E", foreground="white", font=("Segoe UI", 18, "bold"), padding=5)
        style.configure("TButton", background="#1E1E1E", foreground="white", font=("Segoe UI", 16), padding=8)
        style.map("TButton", background=[("active", "#333333")])

    # -----------------------------
    # IMAGE LOADER
    # -----------------------------
    def load_image(self, filename, size=(80, 50)):
        path = os.path.join(IMAGE_FOLDER, filename)
        if not os.path.exists(path):
            img = Image.new("RGB", size, color=(60,60,60))
        else:
            img = Image.open(path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    # -----------------------------
    # BUILD LAYOUT
    # -----------------------------
    def build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # ---------- TITLE ----------
        title_label = ttk.Label(self, text="Drishti", font=("Segoe UI", 28, "bold"), foreground="#FFFFFF", background="#121212")
        title_label.grid(row=0, column=0, sticky="nw", padx=20, pady=15)

        # ---------- 2x2 GRID BOXES ----------
        grid_frame = ttk.Frame(self)
        grid_frame.grid(row=1, column=0, sticky="nsew", padx=50, pady=5)
        grid_frame.grid_columnconfigure((0,1), weight=1, uniform="col")
        grid_frame.grid_rowconfigure((0,1), weight=1, uniform="row")

        # Height for letter/special boxes
        box_height = 45  # smaller for balance

        # --- Top Box A-H ---
        top_frame = ttk.Frame(grid_frame, style="Card.TFrame", height=box_height)
        top_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        top_image = self.load_image("up.jpg", (70,40))
        tk.Label(top_frame, image=top_image, bg="#121212").pack(pady=5)
        top_frame.image = top_image
        for ch in "ABCDEFGH":
            lbl = ttk.Label(top_frame, text=ch, style="BoxLabel.TLabel")
            lbl.pack(side="left", expand=True, fill="both", padx=2, pady=2)

        # --- Special Function Box ---
        special_frame = tk.Frame(grid_frame, bg="#1E1E1E", bd=2, relief="raised", height=box_height)
        special_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        special_image = self.load_image("special.jpg", (70,40))
        tk.Label(special_frame, image=special_image, bg="#121212").pack(pady=5)
        special_frame.image = special_image

        special_buttons = ["⌫", "⬜", "🗑️", "🔊", "➕"]
        self.special_btn_refs = []
        for icon in special_buttons:
            btn = tk.Button(
                special_frame,
                text=icon,
                font=("Segoe UI Emoji", 18),
                bg="#1E1E1E",
                fg="white",
                relief="raised",
                bd=2,
                width=4,
                height=2
            )
            btn.pack(side="left", expand=True, fill="both", padx=2, pady=2)
            self.special_btn_refs.append(btn)

        # --- Left Box I-Q ---
        left_frame = ttk.Frame(grid_frame, style="Card.TFrame", height=box_height)
        left_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        left_image = self.load_image("left.jpg", (70,40))
        tk.Label(left_frame, image=left_image, bg="#121212").pack(pady=5)
        left_frame.image = left_image
        for ch in "IJKLMNOPQ":
            lbl = ttk.Label(left_frame, text=ch, style="BoxLabel.TLabel")
            lbl.pack(side="left", expand=True, fill="both", padx=2, pady=2)

        # --- Right Box R-Z ---
        right_frame = ttk.Frame(grid_frame, style="Card.TFrame", height=box_height)
        right_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        right_image = self.load_image("right.jpg", (70,40))
        tk.Label(right_frame, image=right_image, bg="#121212").pack(pady=5)
        right_frame.image = right_image
        for ch in "RSTUVWXYZ":
            lbl = ttk.Label(right_frame, text=ch, style="BoxLabel.TLabel")
            lbl.pack(side="left", expand=True, fill="both", padx=2, pady=2)

        # ---------- WORD SUGGESTION BUTTONS (smaller) ----------
        self.word_frame = ttk.Frame(self)
        self.word_frame.grid(row=2, column=0, pady=(15,5), padx=120, sticky="ew")
        self.word_frame.grid_columnconfigure((0,1,2,3), weight=1)
        self.word_buttons = []
        for i in range(TOP_WORD_SUGGESTIONS):
            btn = ttk.Button(self.word_frame, text=f"Word {i+1}")
            btn.grid(row=0, column=i, padx=5, sticky="nsew", ipadx=20, ipady=10)
            self.word_buttons.append(btn)

        # ---------- SENTENCE SUGGESTION BUTTONS (smaller) ----------
        self.sentence_frame = ttk.Frame(self)
        self.sentence_frame.grid(row=3, column=0, pady=(10,10), padx=80, sticky="ew")
        self.sentence_frame.grid_columnconfigure((0,1), weight=1)
        self.sentence_buttons = []
        for i in range(TOP_SENTENCE_SUGGESTIONS):
            btn = ttk.Button(self.sentence_frame, text=f"Suggestion {i+1}")
            btn.grid(row=0, column=i, padx=15, sticky="nsew", ipadx=20, ipady=15)
            self.sentence_buttons.append(btn)

        # Input box frame
        middle_frame = ttk.Frame(self)
        middle_frame.grid(row=5, column=0, sticky="ew", padx=80, pady=(0, 50))  # bottom margin
        middle_frame.grid_columnconfigure(0, weight=1)

        # Input box itself
        self.text_display = tk.Text(
            middle_frame,
            bg="#1E1E1E",
            fg="white",
            font=("Consolas", 28),
            wrap="word",
            relief="solid",
            bd=2,
            height=10  # bigger input box
        )
        self.text_display.grid(row=0, column=0, sticky="ew")


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app = DrishtiUI()
    app.mainloop()
