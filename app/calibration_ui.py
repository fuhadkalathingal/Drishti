import tkinter as tk
from tkinter import ttk
import time
import yaml
import shutil
import threading
from pathlib import Path
from collections import deque
from app.core.eye_gesture import get_gesture_frame
from app.core.eye_gesture import reload_gesture_detector

# ---------------------------------------------------------------------
# CONFIGURATION CONSTANTS
# ---------------------------------------------------------------------
CONFIG_PATH = Path("../config.yaml")
BACKUP_DIR = Path("../config_backups")
BACKUP_DIR.mkdir(exist_ok=True)

MIN_VAL, MAX_VAL = 0.0, 1.0
STEP_SMALL = 0.01
STEP_LARGE = 0.03
REQUIRED_FAILURES = 3
HYSTERESIS_MARGIN = 0.05
ROLLING_WINDOW = 6

file_lock = threading.Lock()
failure_counters = {"FB": 0, "SB": 0, "VSB": 0, "FL": 0, "FR": 0, "FU": 0}
recent_outcomes = deque(maxlen=ROLLING_WINDOW)


# ---------------------------------------------------------------------
# CONFIG FUNCTIONS
# ---------------------------------------------------------------------
def backup_config():
    ts = time.strftime("%Y%m%d-%H%M%S")
    dst = BACKUP_DIR / f"config_{ts}.yaml"
    shutil.copy(CONFIG_PATH, dst)
    print(f"[calib] Backup created: {dst}")


def clamp(v: float) -> float:
    return max(MIN_VAL, min(MAX_VAL, v))


def safe_load_config():
    with file_lock:
        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)


def safe_save_config(d):
    backup_config()
    with file_lock:
        with open(CONFIG_PATH, "w") as f:
            yaml.safe_dump(d, f, sort_keys=False)


def consider_adjustment(expected_event: str):
    failure_counters[expected_event] += 1
    recent_outcomes.append((expected_event, time.time()))

    if failure_counters[expected_event] < REQUIRED_FAILURES:
        print(f"[calib] {expected_event} failed ({failure_counters[expected_event]}/{REQUIRED_FAILURES}), waiting...")
        return

    cfg = safe_load_config()
    for k in cfg:
        cfg[k] = float(cfg[k])

    step = STEP_SMALL if failure_counters[expected_event] < (REQUIRED_FAILURES * 2) else STEP_LARGE

    if expected_event in ["FB", "SB", "VSB"]:
        cfg["closed_threshold"] = clamp(cfg["closed_threshold"] - step)
        cfg["open_threshold"] = clamp(cfg["open_threshold"] + step)
        if cfg["closed_threshold"] <= cfg["open_threshold"] + HYSTERESIS_MARGIN:
            cfg["closed_threshold"] = clamp(cfg["open_threshold"] + HYSTERESIS_MARGIN)
    elif expected_event in ["FL", "FR"]:
        cfg["gaze_enter_threshold"] = clamp(cfg["gaze_enter_threshold"] - step)
        cfg["gaze_exit_threshold"] = clamp(cfg["gaze_exit_threshold"] + step)
        if cfg["gaze_exit_threshold"] <= cfg["gaze_enter_threshold"] + HYSTERESIS_MARGIN:
            cfg["gaze_exit_threshold"] = clamp(cfg["gaze_enter_threshold"] + HYSTERESIS_MARGIN)
    elif expected_event == "FU":
        cfg["gaze_up_enter_threshold"] = clamp(cfg["gaze_up_enter_threshold"] - step)
        cfg["gaze_up_exit_threshold"] = clamp(cfg["gaze_up_exit_threshold"] + step)
        if cfg["gaze_up_exit_threshold"] <= cfg["gaze_up_enter_threshold"] + HYSTERESIS_MARGIN:
            cfg["gaze_up_exit_threshold"] = clamp(cfg["gaze_up_enter_threshold"] + HYSTERESIS_MARGIN)

    for k in cfg:
        cfg[k] = round(cfg[k], 6)

    safe_save_config(cfg)
    reload_gesture_detector()

    print(f"[calib] Adjusted config for {expected_event}. Step={step}. New values:")
    for k, v in cfg.items():
        print(f"   {k}: {v}")

    failure_counters[expected_event] = 0


# ---------------------------------------------------------------------
# MODERN DARK UI
# ---------------------------------------------------------------------
class CalibrationUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✨ Gaze Calibration")
        self.geometry("720x420")
        self.configure(bg="#0F1115")

        # Modern ttk styling
        style = ttk.Style(self)
        self.tk.call("source", "sun-valley.tcl") if Path("sun-valley.tcl").exists() else None
        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "TLabel",
            background="#0F1115",
            foreground="#E0E0E0",
            font=("Segoe UI", 12),
        )
        style.configure(
            "Header.TLabel",
            background="#0F1115",
            foreground="#00FFC6",
            font=("Segoe UI Semibold", 22),
        )
        style.configure(
            "Status.TLabel",
            background="#0F1115",
            foreground="#AAAAAA",
            font=("Segoe UI", 14),
        )
        style.configure(
            "TButton",
            background="#1F2127",
            foreground="#FFFFFF",
            font=("Segoe UI", 12),
            padding=8,
            relief="flat",
        )
        style.map(
            "TButton",
            background=[("active", "#00FFC6"), ("pressed", "#00D4A0")],
            foreground=[("active", "#000000"), ("pressed", "#000000")],
        )

        # Steps
        self.steps = [
            ("Blink fast (under 0.4s)", "FB"),
            ("Blink slow (0.4–1.0s)", "SB"),
            ("Blink very slow (over 1.0s)", "VSB"),
            ("Look left", "FL"),
            ("Look right", "FR"),
            ("Look up", "FU")
        ]
        self.current_step = 0

        # Header label
        self.label = ttk.Label(self, text="", style="Header.TLabel")
        self.label.pack(expand=True, pady=30)

        self.status_label = ttk.Label(self, text="", style="Status.TLabel")
        self.status_label.pack()

        # Start button
        self.start_button = ttk.Button(self, text="Start Calibration", command=self.start_calibration)
        self.start_button.pack(pady=25)

        # subtle bottom info
        self.footer = ttk.Label(self, text="Eye gesture calibration system", font=("Segoe UI", 9), foreground="#555555")
        self.footer.pack(side="bottom", pady=10)

    def start_calibration(self):
        self.start_button.pack_forget()
        self.run_next_step()

    def run_next_step(self):
        if self.current_step >= len(self.steps):
            self.label.config(text="✅ Calibration Complete!", foreground="#00FFC6")
            self.status_label.config(text="")
            return

        step_text, expected_event = self.steps[self.current_step]
        self.expected_event = expected_event
        self.start_time = time.time()
        self.label.config(text=f"Please {step_text}", foreground="#FFFFFF")
        self.status_label.config(text="Waiting for detection...", foreground="#AAAAAA")
        self.check_event()

    def check_event(self):
        event = get_gesture_frame()

        if event == self.expected_event:
            self.status_label.config(text=f"✔ {self.expected_event} detected!", foreground="#00FFC6")
            print(f"[calib] Step {self.expected_event} successful.")
            self.after(1000, self.next_step)
        elif time.time() - self.start_time > 6.0:
            self.status_label.config(text=f"❌ Not detected. Try again.", foreground="#FF4E4E")
            self.retry_button = ttk.Button(self, text="Retry", command=self.retry_step)
            self.retry_button.pack(pady=10)
            consider_adjustment(self.expected_event)
        else:
            self.after(100, self.check_event)

    def retry_step(self):
        if hasattr(self, "retry_button"):
            self.retry_button.destroy()
        self.status_label.config(text="")
        self.run_next_step()

    def next_step(self):
        self.current_step += 1
        self.run_next_step()


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------
if __name__ == "__main__":
    app = CalibrationUI()
    app.mainloop()
