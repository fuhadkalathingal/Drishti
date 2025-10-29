import json
import os
import tkinter as tk
from app.main_ui import DrishtiKeyboardUI
from app.calibration_ui import run_calibration_ui
from app.learn_ui import run_learn_ui

# JSON progress file
PROGRESS_FILE = "cache/user_progress.json"

def load_progress():
    """Load or initialize the progress JSON file."""
    if not os.path.exists(PROGRESS_FILE):
        data = {"calibrated": False, "learned": False}
        save_progress(data)
        return data
    with open(PROGRESS_FILE, "r") as f:
        return json.load(f)

def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    progress = load_progress()

    # Shared hidden root for the first two UIs
    root = tk.Tk()
    root.withdraw()

    if not progress["calibrated"]:
        print("[INFO] Running calibration...")
        run_calibration_ui(root)
        progress["calibrated"] = True
        save_progress(progress)

    if not progress["learned"]:
        print("[INFO] Running learning module...")
        run_learn_ui(root)
        progress["learned"] = True
        save_progress(progress)

    # Destroy shared root and open main UI
    root.destroy()

    print("[INFO] Launching Drishti Keyboard UI...")
    app = DrishtiKeyboardUI()
    app.mainloop()
