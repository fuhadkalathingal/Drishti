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
        # ---------- MAIN GRID ----------
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ---------- TOP SECTION ----------
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))
        top_frame.grid_columnconfigure(0, weight=1)

        # --- Title and Subtitle ---
        title = ttk.Label(top_frame, text="DRISHTI", font=("Segoe UI", 34, "bold"))
        title.grid(row=0, column=0, pady=(0, 5))

        subtitle = ttk.Label(top_frame, text="From Vision To Voice", font=("Segoe UI", 20, "italic"), foreground="#AAAAAA")
        subtitle.grid(row=1, column=0, pady=(0, 15))

        # --- Suggestion Buttons ---
        suggestion_frame = ttk.Frame(top_frame)
        suggestion_frame.grid(row=2, column=0, pady=(5, 0))
        for i in range(4):
            btn = ttk.Button(suggestion_frame, text=f"Option {i+1}")
            btn.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            suggestion_frame.grid_columnconfigure(i, weight=1)

        # ---------- TEXT BOX ----------
        middle_frame = ttk.Frame(self)
        middle_frame.grid(row=1, column=0, sticky="ew", padx=300, pady=(10, 5))
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

        # ---------- TRIANGULAR BOTTOM SECTION ----------
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=2, column=0, sticky="nsew", padx=40, pady=20)
        for i in range(3):
            bottom_frame.grid_columnconfigure(i, weight=1)
        for i in range(3):
            bottom_frame.grid_rowconfigure(i, weight=1)

        # --- Load clue images from images folder ---
        self.top_clue_image = self.load_image("images/up.jpg", (200, 80))
        self.left_clue_image = self.load_image("images/left.jpg", (200, 80))
        self.right_clue_image = self.load_image("images/right.jpg", (200, 80))

        # --- Center Top Box (A–H) ---
        top_clue = tk.Label(bottom_frame, image=self.top_clue_image, bg="#121212")
        top_clue.grid(row=0, column=1, pady=(0, 10), sticky="n")

        top_box = ttk.Frame(bottom_frame, style="Card.TFrame")
        top_box.grid(row=1, column=1, sticky="nsew", padx=20, pady=10)
        for ch in "ABCDEFGH":
            lbl = ttk.Label(top_box, text=ch, style="BoxLabel.TLabel")
            lbl.pack(side="left", expand=True, fill="both", padx=8, pady=8)

        # --- Left Bottom Box (I–Q) ---
        left_clue = tk.Label(bottom_frame, image=self.left_clue_image, bg="#121212")
        left_clue.grid(row=1, column=0, pady=(0, 10), sticky="s")

        left_box = ttk.Frame(bottom_frame, style="Card.TFrame")
        left_box.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        for ch in "IJKLMNOPQ":
            lbl = ttk.Label(left_box, text=ch, style="BoxLabel.TLabel")
            lbl.pack(side="left", expand=True, fill="both", padx=8, pady=8)

        # --- Right Bottom Box (R–Z) ---
        right_clue = tk.Label(bottom_frame, image=self.right_clue_image, bg="#121212")
        right_clue.grid(row=1, column=2, pady=(0, 10), sticky="s")

        right_box = ttk.Frame(bottom_frame, style="Card.TFrame")
        right_box.grid(row=2, column=2, sticky="nsew", padx=20, pady=10)
        for ch in "RSTUVWXYZ":
            lbl = ttk.Label(right_box, text=ch, style="BoxLabel.TLabel")
            lbl.pack(side="left", expand=True, fill="both", padx=8, pady=8)

    def load_image(self, path, size):
        """Load and resize an image from the given path, compatible with all Pillow versions."""
        # Determine the correct resampling method
        try:
            resample = Image.Resampling.LANCZOS  # Pillow >= 10
        except AttributeError:
            resample = Image.LANCZOS  # Older versions

        if not os.path.exists(path):
            # fallback to placeholder if image not found
            img = Image.new("RGB", size, color=(60, 60, 60))
        else:
            img = Image.open(path).resize(size, resample)
        return ImageTk.PhotoImage(img)

if __name__ == "__main__":
    app = DrishtiUI()
    app.mainloop()
