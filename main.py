import tkinter as tk
from app.main_ui import DrishtiKeyboardUI
from app.calibration_ui import run_calibration_ui
from app.learn_ui import run_learn_ui

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()  # Keep base root hidden

    run_calibration_ui(root)
    run_learn_ui(root)

    # Destroy and recreate a clean root for the main UI
    root.destroy()
    app = DrishtiKeyboardUI()
    app.mainloop()
