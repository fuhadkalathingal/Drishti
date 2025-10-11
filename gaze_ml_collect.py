import cv2
import os
import numpy as np
import dlib
from datetime import datetime
import csv

# ================================================
# CONFIGURATION
# ================================================
DATA_DIR = "data"
EYE_SIZE = (96, 48)
LABELS = ["left", "right", "up", "blink", "slow_blink"]

# Auto-create folders
for label in LABELS:
    os.makedirs(os.path.join(DATA_DIR, label), exist_ok=True)

CSV_PATH = os.path.join(DATA_DIR, "iris_coordinates.csv")
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "label", "left_x", "left_y", "right_x", "right_y"])

# ================================================
# DLIB FACE + LANDMARK DETECTOR
# ================================================
detector = dlib.get_frontal_face_detector()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
predictor_path = os.path.join(BASE_DIR, "gaze_tracking", "trained_models", "shape_predictor_68_face_landmarks.dat")
predictor = dlib.shape_predictor(predictor_path)

# ================================================
# HELPER: Extract and zoom eye region
# ================================================
def get_eye(frame, landmarks, eye_points):
    region = np.array([(landmarks.part(p).x, landmarks.part(p).y) for p in eye_points])
    min_x = np.min(region[:, 0])
    max_x = np.max(region[:, 0])
    min_y = np.min(region[:, 1])
    max_y = np.max(region[:, 1])

    # Add padding around eye to zoom in slightly
    pad_x = int((max_x - min_x) * 0.3)
    pad_y = int((max_y - min_y) * 0.6)
    min_x = max(min_x - pad_x, 0)
    max_x = min(max_x + pad_x, frame.shape[1])
    min_y = max(min_y - pad_y, 0)
    max_y = min(max_y + pad_y, frame.shape[0])

    eye = frame[min_y:max_y, min_x:max_x]
    gray_eye = cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)
    gray_eye = cv2.GaussianBlur(gray_eye, (7, 7), 0)

    # Threshold for iris detection
    _, thresh_eye = cv2.threshold(gray_eye, 45, 255, cv2.THRESH_BINARY_INV)
    moments = cv2.moments(thresh_eye)
    cx, cy = 0, 0
    if moments['m00'] != 0:
        cx = int(moments['m10'] / moments['m00'])
        cy = int(moments['m01'] / moments['m00'])

    # Normalize coordinates
    nx = (cx - gray_eye.shape[1] / 2) / (gray_eye.shape[1] / 2)
    ny = (cy - gray_eye.shape[0] / 2) / (gray_eye.shape[0] / 2)

    # Draw iris for display
    cv2.circle(eye, (cx, cy), 2, (0, 0, 255), -1)

    # Resize eye region
    resized_eye = cv2.resize(eye, EYE_SIZE)

    return resized_eye, (nx, ny)

# ================================================
# CAPTURE LOOP
# ================================================
cap = cv2.VideoCapture(0)
current_label = None
sample_count = 0

print("Press key for label: [L]eft, [R]ight, [U]p, [B]link, [S]low Blink, [Q]uit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    left_eye_display = None
    right_eye_display = None
    left_coords, right_coords = (0, 0), (0, 0)

    for face in faces:
        landmarks = predictor(gray, face)
        left_eye_display, left_coords = get_eye(frame, landmarks, list(range(36, 42)))
        right_eye_display, right_coords = get_eye(frame, landmarks, list(range(42, 48)))

        both_eyes = np.hstack((left_eye_display, right_eye_display))

        # Show cropped eye regions only
        cv2.imshow("Eye Region (Zoomed)", both_eyes)

        # Display info
        if current_label:
            cv2.putText(frame, f"Recording: {current_label} ({sample_count})", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow("Face Tracking (Preview)", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('l'):
        current_label = "left"
    elif key == ord('r'):
        current_label = "right"
    elif key == ord('u'):
        current_label = "up"
    elif key == ord('b'):
        current_label = "blink"
    elif key == ord('s'):
        current_label = "slow_blink"
    elif key == ord('q'):
        break

    # Capture with spacebar
    if key == 32 and current_label and left_eye_display is not None:
        filename = os.path.join(DATA_DIR, current_label, f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg")
        cv2.imwrite(filename, both_eyes)

        # Save coordinates to CSV
        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([filename, current_label, left_coords[0], left_coords[1], right_coords[0], right_coords[1]])

        sample_count += 1
        print(f"Captured {current_label}: {filename}")

cap.release()
cv2.destroyAllWindows()
