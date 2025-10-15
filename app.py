import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class DrishtiUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drishti - From Vision To Voice")
        self.configure(bg="#121212")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self.create_styles()
        self.build_layout()

    def create_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background="#121212")
        style.configure("Card.TFrame", background="#1E1E1E", relief="solid", borderwidth=2)
        style.configure("TLabel", background="#121212", foreground="white", font=("Segoe UI", 16))
        style.configure("BoxLabel.TLabel", background="#1E1E1E", foreground="white", font=("Segoe UI", 22, "bold"))
        style.configure("TButton", background="#1E1E1E", foreground="white", font=("Segoe UI", 14), padding=10)
        style.map("TButton", background=[("active", "#333333")])

    def build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # ---------- SMALL TITLE ----------
        title_label = ttk.Label(self, text="Drishti", font=("Segoe UI", 18, "bold"), foreground="#FFFFFF", background="#121212")
        title_label.grid(row=0, column=0, sticky="nw", padx=20, pady=10)

        # ---------- LETTER BOXES TRIANGLE ----------
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=1, column=0, sticky="nsew")
        bottom_frame.grid_columnconfigure((0,1,2), weight=1)
        bottom_frame.grid_rowconfigure((0,1), weight=1)

        # --- Load clue images ---
        self.top_clue_image = self.load_image("images/up.jpg", (150, 60))
        self.left_clue_image = self.load_image("images/left.jpg", (150, 60))
        self.right_clue_image = self.load_image("images/right.jpg", (150, 60))

        # --- Middle Top Box (A-H) ---
        top_frame_box = ttk.Frame(bottom_frame)
        top_frame_box.grid(row=0, column=1, pady=(10,0))  # center top
        top_clue = tk.Label(top_frame_box, image=self.top_clue_image, bg="#121212")
        top_clue.pack(pady=5)
        top_box = ttk.Frame(top_frame_box, style="Card.TFrame")
        top_box.pack()
        for ch in "ABCDEFGH":
            lbl = ttk.Label(top_box, text=ch, style="BoxLabel.TLabel")
            lbl.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        # --- Left Bottom Box (I-Q) ---
        left_frame_box = ttk.Frame(bottom_frame)
        left_frame_box.grid(row=1, column=0, padx=20, pady=(0,10))
        left_clue = tk.Label(left_frame_box, image=self.left_clue_image, bg="#121212")
        left_clue.pack(pady=5)
        left_box = ttk.Frame(left_frame_box, style="Card.TFrame")
        left_box.pack()
        for ch in "IJKLMNOPQ":
            lbl = ttk.Label(left_box, text=ch, style="BoxLabel.TLabel")
            lbl.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        # --- Right Bottom Box (R-Z) ---
        right_frame_box = ttk.Frame(bottom_frame)
        right_frame_box.grid(row=1, column=2, padx=20, pady=(0,10))
        right_clue = tk.Label(right_frame_box, image=self.right_clue_image, bg="#121212")
        right_clue.pack(pady=5)
        right_box = ttk.Frame(right_frame_box, style="Card.TFrame")
        right_box.pack()
        for ch in "RSTUVWXYZ":
            lbl = ttk.Label(right_box, text=ch, style="BoxLabel.TLabel")
            lbl.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        # ---------- SUGGESTION BUTTONS ----------
        suggestion_frame = ttk.Frame(self)
        suggestion_frame.grid(row=2, column=0, pady=(10, 5), padx=300, sticky="ew")
        suggestion_frame.grid_columnconfigure((0,1,2,3), weight=1)
        for i in range(4):
            btn = ttk.Button(suggestion_frame, text=f"Option {i+1}")
            btn.grid(row=0, column=i, padx=10, sticky="nsew")

        # ---------- TEXT BOX BELOW ----------
        middle_frame = ttk.Frame(self)
        middle_frame.grid(row=3, column=0, sticky="ew", padx=300, pady=(20, 10))
        middle_frame.grid_columnconfigure(0, weight=1)

        text_display = tk.Text(
            middle_frame,
            bg="#1E1E1E",
            fg="white",
            font=("Consolas", 18),
            wrap="word",
            relief="solid",
            bd=2,
            height=3,
        )
        text_display.insert("1.0", "Text will appear here...")
        text_display.configure(state="disabled")
        text_display.grid(row=0, column=0, sticky="ew")

    def load_image(self, path, size):
        """Load and resize an image from the given path, compatible with all Pillow versions."""
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.LANCZOS

        if not os.path.exists(path):
            img = Image.new("RGB", size, color=(60, 60, 60))
        else:
            img = Image.open(path).resize(size, resample)
        return ImageTk.PhotoImage(img)

if __name__ == "__main__":
    app = DrishtiUI()
    app.mainloop()
