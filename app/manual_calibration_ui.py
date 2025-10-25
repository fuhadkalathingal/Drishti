import tkinter as tk
from tkinter import ttk
import yaml

class SliderUI(tk.Tk):
    def __init__(self, config_path="config.yaml"):
        super().__init__()
        self.config_path = config_path

        # Window setup
        self.title("10 Sliders (0.0 - 1.0)")
        self.geometry("1150x700")
        self.minsize(900, 600)
        self.configure(bg="#121212")
        self.resizable(True, True)

        # Main frame
        self.frame = ttk.Frame(self, padding=20)
        self.frame.pack(fill="both", expand=True)

        # Load config
        self.loaded_data = self.load_config()

        # Store slider variables and labels
        self.slider_vars = []

        # Create sliders dynamically
        self.create_sliders()

        # Save button
        save_button = ttk.Button(self.frame, text="Save", command=self.save_config)
        save_button.pack(pady=20)

    def load_config(self):
        """Load YAML config into a dictionary."""
        try:
            with open(self.config_path, 'r') as file:
                return dict(yaml.safe_load(file))
        except FileNotFoundError:
            # Default config if file doesn't exist
            return {f"Slider {i+1}": 0.5 for i in range(10)}

    def create_sliders(self):
        """Dynamically create sliders from loaded config."""
        for idx, (key, value) in enumerate(self.loaded_data.items()):
            row_frame = ttk.Frame(self.frame)
            row_frame.pack(fill="x", pady=10)

            label = ttk.Label(row_frame, text=key, background="#121212", foreground="white")
            label.pack(side="left")

            var = tk.DoubleVar(value=value)
            scale = ttk.Scale(
                row_frame,
                from_=0.0,
                to=1.0,
                orient="horizontal",
                variable=var,
                command=lambda val, idx=idx: self.update_value(idx)
            )
            scale.pack(side="left", fill="x", expand=True, padx=10)

            value_label = ttk.Label(row_frame, text=f"{var.get():.2f}", background="#121212", foreground="white")
            value_label.pack(side="right")

            self.slider_vars.append((var, value_label))

    def update_value(self, idx):
        """Update the label when slider changes."""
        var, label = self.slider_vars[idx]
        label.config(text=f"{var.get():.2f}")

    def save_config(self):
        """Save current slider values back to YAML config."""
        for key, (var, _) in zip(self.loaded_data.keys(), self.slider_vars):
            self.loaded_data[key] = var.get()

        with open(self.config_path, 'w') as file:
            yaml.dump(self.loaded_data, file, sort_keys=False)

        print("Configuration saved successfully!")

# Run the app
if __name__ == "__main__":
    app = SliderUI()
    app.mainloop()
