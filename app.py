import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import threading
import time
from eye_gesture import get_gesture_frame, release_camera
from morse_decoder import event_to_letter
from text_suggestion import suggest

# --- Dark theme colors ---
bg_color = "#1e1e1e"
fg_color = "#ffffff"
btn_bg = "#333333"
btn_fg = "#ffffff"

# --- Fullscreen window ---
root = tk.Tk()
root.title("Live Eye Gesture Dashboard")
root.attributes('-fullscreen', True)
root.configure(bg=bg_color)

# --- Top frame ---
top_frame = tk.Frame(root, bg=bg_color)
top_frame.pack(fill='both', expand=False, pady=10)

# Heading
heading = tk.Label(top_frame, text="Live Eye Gesture Dashboard",
                   font=("Helvetica", 32), bg=bg_color, fg=fg_color)
heading.pack(pady=10)

# Option buttons (will show suggestions)
btn_frame = tk.Frame(top_frame, bg=bg_color)
btn_frame.pack(pady=10)

buttons = []
for i in range(4):
    btn = tk.Button(btn_frame, text=f"Option {i+1}", width=20,
                    bg=btn_bg, fg=btn_fg, font=("Helvetica", 16))
    btn.grid(row=0, column=i, padx=5)
    buttons.append(btn)

# String display (2 lines)
display_text = scrolledtext.ScrolledText(top_frame, width=120, height=2,
                                         font=("Helvetica", 20),
                                         bg="#2e2e2e", fg=fg_color)
display_text.insert(tk.END, "")
display_text.config(state=tk.DISABLED)
display_text.pack(pady=10)

# Buffers side by side
buffer_frame = tk.Frame(top_frame, bg=bg_color)
buffer_frame.pack(pady=10)

# Morse buffer display
morse_buffer_display = scrolledtext.ScrolledText(buffer_frame, width=60, height=1,
                                                 font=("Helvetica", 20),
                                                 bg="#2e2e2e", fg=fg_color)
morse_buffer_display.insert(tk.END, "")
morse_buffer_display.config(state=tk.DISABLED)
morse_buffer_display.grid(row=0, column=0, padx=10)

# Event display buffer
event_display = scrolledtext.ScrolledText(buffer_frame, width=60, height=1,
                                          font=("Helvetica", 20),
                                          bg="#2e2e2e", fg=fg_color)
event_display.insert(tk.END, "")
event_display.config(state=tk.DISABLED)
event_display.grid(row=0, column=1, padx=10)

# Bottom image
bottom_frame = tk.Frame(root, bg=bg_color)
bottom_frame.pack(fill='both', expand=True)

img = Image.open("morse_chart.png")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

new_height = screen_height // 2
new_width = int(new_height * (img.width / img.height))
if new_width > screen_width:
    new_width = screen_width
    new_height = int(new_width * (img.height / img.width))

img = img.resize((new_width, new_height))
photo = ImageTk.PhotoImage(img)

img_label = tk.Label(bottom_frame, image=photo, bg=bg_color)
img_label.pack(pady=5, expand=True)

# --- Initialize buffers ---
morse_buffer = ""
string = ""

selected_index = -1

current_section = 0
taking_break = False

# --- Function to continuously update UI ---
def update_ui():
    global morse_buffer, string
    global selected_index
    global current_section, taking_break
    try:
        while True:
            event = get_gesture_frame()
            if event:
                if event == "FU":
                    if current_section == 0:
                        current_section = 1
                        selected_index = 0
                    else:
                        current_section = 0
                        selected_index = -1
                elif event == "SU":
                    if taking_break == False:
                        taking_break = True
                    else:
                        taking_break = False
                elif current_section == 0:
                    morse_buffer, string = event_to_letter(event, morse_buffer, string)

                # Update main string box
                display_text.config(state=tk.NORMAL)
                display_text.delete("1.0", tk.END)
                display_text.insert(tk.END, string)
                display_text.config(state=tk.DISABLED)

                # Update Morse buffer
                morse_buffer_display.config(state=tk.NORMAL)
                morse_buffer_display.delete("1.0", tk.END)
                morse_buffer_display.insert(tk.END, morse_buffer)
                morse_buffer_display.config(state=tk.DISABLED)

                # Show latest event
                event_display.config(state=tk.NORMAL)
                event_display.delete("1.0", tk.END)
                event_display.insert(tk.END, str(event))
                event_display.config(state=tk.DISABLED)

                # Update suggestions
                prefix_sugg, context_sugg = suggest(string)
                suggestions = prefix_sugg if prefix_sugg else context_sugg

                if current_section == 1 and event == "FB":
                    if selected_index < 3:
                        selected_index += 1
                    else:
                        selected_index = 0

                for i, btn in enumerate(buttons):
                    if i < len(suggestions):
                        btn.config(text=suggestions[i])
                    else:
                        btn.config(text="")  # empty if no suggestion

                    # Highlight selected button
                    if i == selected_index:
                        btn.config(bg="#007ACC")  # bright color for selected
                    else:
                        btn.config(bg=btn_bg)  # normal button color

            time.sleep(0.05)
    except Exception as e:
        release_camera()
        print(f"Error: {e}")

# Run in separate thread
thread = threading.Thread(target=update_ui, daemon=True)
thread.start()

# Bind Esc to exit
root.bind("<Escape>", lambda e: root.destroy())

root.mainloop()
