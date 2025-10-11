import cv2
import numpy as np
from collections import deque
from gaze_tracking import GazeTracking
import time

# -------------------- Setup --------------------
gaze = GazeTracking()
cap = cv2.VideoCapture(0)

smooth_window = 5
dx_buffer = deque(maxlen=smooth_window)
dy_buffer = deque(maxlen=smooth_window)

# UI Boxes
boxes = {
    "Top-Left": {"pos": (50,50,350,250), "letters": list("ABCDEFGH")},
    "Top-Right": {"pos": (400,50,700,250), "letters": list("IJKLMNOP")},
    "Bottom-Center": {"pos": (225,300,525,450), "letters": list("QRSTUVWXY")},
}
box_names = list(boxes.keys())
current_box_index = 0
current_letter_index = 0
previous_box_index = 0
selected_text = ""

# Thresholds
H_THRESH = 0.25
V_THRESH = 0.25

# Blink cooldowns
last_double_blink = 0
last_slow_blink = 0
last_delete_blink = 0
BLINK_COOLDOWN = 0.6  # seconds

# Previous states to avoid multiple triggers
prev_double_state = False
prev_slow_state = False
prev_delete_state = False

# Flash variables
flash_letter = None
flash_start = 0
FLASH_DURATION = 0.5  # seconds

# -------------------- UI Drawing --------------------
def draw_ui(frame):
    frame[:] = 50
    for i, name in enumerate(box_names):
        box = boxes[name]
        x1,y1,x2,y2 = box["pos"]
        color = (0,255,0) if i == current_box_index else (100,100,100)
        cv2.rectangle(frame, (x1,y1), (x2,y2), color, 3)
        letters = box["letters"]
        spacing = (x2-x1)//len(letters)
        for j, letter in enumerate(letters):
            # Highlight letter if selected recently
            if flash_letter and flash_letter == (i,j):
                l_color = (0,255,255)  # Yellow flash
            else:
                l_color = (0,255,0) if (i==current_box_index and j==current_letter_index) else (200,200,200)
            lx = x1 + j*spacing + spacing//2 - 10
            ly = (y1+y2)//2 + 10
            cv2.putText(frame, letter, (lx,ly), cv2.FONT_HERSHEY_SIMPLEX,1.2,l_color,2)
    # Output text
    cv2.putText(frame, f"Output: {selected_text}", (50,520),
                cv2.FONT_HERSHEY_SIMPLEX,1.0,(255,255,255),2)

# -------------------- Main Loop --------------------
while True:
    ret, _frame = cap.read()
    if not ret:
        break

    gaze.refresh(_frame)
    gaze.update_blink_history()

    dx, dy = gaze.iris_position()
    dx_buffer.append(dx)
    dy_buffer.append(dy)
    dx_smooth = sum(dx_buffer)/len(dx_buffer)
    dy_smooth = sum(dy_buffer)/len(dy_buffer)

    # -------------------- Box Selection via gaze --------------------
    if dx_smooth >= H_THRESH:
        current_box_index = 0  # Top-Left
    elif dx_smooth <= -H_THRESH:
        current_box_index = 1  # Top-Right
    elif dy_smooth >= V_THRESH:
        current_box_index = 2  # Bottom-Center

    # Reset letter index if box changed
    if current_box_index != previous_box_index:
        current_letter_index = 0
        previous_box_index = current_box_index

    now = time.time()

    # -------------------- Letter Navigation (Double Blink) --------------------
    double_state = gaze.is_double_blink()
    if double_state and not prev_double_state and (now - last_double_blink > BLINK_COOLDOWN):
        current_letter_index += 1
        letters_len = len(boxes[box_names[current_box_index]]["letters"])
        if current_letter_index >= letters_len:
            current_letter_index = 0
        last_double_blink = now
    prev_double_state = double_state

    # -------------------- Letter Selection (Slow Blink) --------------------
    slow_state = gaze.is_slow_blink()
    if slow_state and not prev_slow_state and (now - last_slow_blink > BLINK_COOLDOWN):
        current_letter = boxes[box_names[current_box_index]]["letters"][current_letter_index]
        selected_text += current_letter
        flash_letter = (current_box_index, current_letter_index)
        flash_start = now
        last_slow_blink = now
    prev_slow_state = slow_state

    # -------------------- Deletion (Left Eye Blink) --------------------
    delete_state = gaze.is_left_eye_blink()
    if delete_state and not prev_delete_state and (now - last_delete_blink > BLINK_COOLDOWN):
        if selected_text:
            selected_text = selected_text[:-1]
        flash_letter = None
        flash_start = now
        last_delete_blink = now
    prev_delete_state = delete_state

    # Clear flash after duration
    if flash_letter and (now - flash_start > FLASH_DURATION):
        flash_letter = None

    # -------------------- Draw UI --------------------
    ui_frame = np.zeros((600,800,3), np.uint8)
    draw_ui(ui_frame)
    cv2.imshow("ALS Gaze UI", ui_frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
