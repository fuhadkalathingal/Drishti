import cv2
import os
import numpy as np
import dlib
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical
from threading import Thread
from datetime import datetime
import csv
import time

# ================================================
# CONFIGURATION
# ================================================
MODEL_PATH = "gaze_tracking/gaze_model.keras"
DATA_DIR = "data"
IMAGE_SIZE = (96, 48)  # height, width
BATCH_SIZE = 16
EPOCHS = 5
RETRAIN_INTERVAL = 60  # seconds

LABELS = ["normal", "left", "right", "up", "blink", "slow_blink"]
label_to_index = {label: idx for idx, label in enumerate(LABELS)}

CSV_PATH = os.path.join(DATA_DIR, "adaptive_iris.csv")
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "label"])

# ================================================
# LOAD MODEL
# ================================================
model = load_model(MODEL_PATH)

# ================================================
# DLIB FACE + LANDMARK DETECTOR
# ================================================
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(os.path.join("gaze_tracking", "trained_models", "shape_predictor_68_face_landmarks.dat"))

# ================================================
# HELPER: Extract eye region
# ================================================
def get_eye(frame, landmarks, eye_points):
    region = np.array([(landmarks.part(p).x, landmarks.part(p).y) for p in eye_points])
    min_x, max_x = np.min(region[:,0]), np.max(region[:,0])
    min_y, max_y = np.min(region[:,1]), np.max(region[:,1])

    pad_x = int((max_x - min_x)*0.3)
    pad_y = int((max_y - min_y)*0.6)
    min_x = max(min_x - pad_x, 0)
    max_x = min(max_x + pad_x, frame.shape[1])
    min_y = max(min_y - pad_y, 0)
    max_y = min(max_y + pad_y, frame.shape[0])

    eye = frame[min_y:max_y, min_x:max_x]
    gray_eye = cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)
    gray_eye = cv2.resize(gray_eye, IMAGE_SIZE)
    gray_eye = gray_eye.astype("float32") / 255.0
    gray_eye = np.expand_dims(gray_eye, axis=-1)
    return gray_eye, eye

# ================================================
# BACKGROUND RETRAINING
# ================================================
def retrain_model_periodically():
    global model
    while True:
        time.sleep(RETRAIN_INTERVAL)
        print("[INFO] Starting adaptive retraining...")

        images = []
        labels_list = []
        for label in LABELS:
            folder = os.path.join(DATA_DIR, label)
            if not os.path.exists(folder):
                continue
            for file in os.listdir(folder):
                if file.lower().endswith((".jpg", ".png")):
                    path = os.path.join(folder, file)
                    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                    if img is None:
                        continue
                    img = cv2.resize(img, IMAGE_SIZE)
                    img = img.astype("float32") / 255.0
                    img = np.expand_dims(img, axis=-1)
                    images.append(img)
                    labels_list.append(label_to_index[label])

        if len(images) < 5:
            print("[WARN] Not enough samples for retraining. Skipping.")
            continue

        X = np.array(images)
        y = to_categorical(labels_list, num_classes=len(LABELS))
        model.fit(X, y, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=0)
        model.save(MODEL_PATH)
        print("[INFO] Adaptive retraining completed. Model updated.")

# Start background retraining
Thread(target=retrain_model_periodically, daemon=True).start()

# ================================================
# REAL-TIME PREDICTION LOOP
# ================================================
cap = cv2.VideoCapture(0)
print("[INFO] Real-time adaptive gaze prediction running...")
print("Press 'R' if prediction is correct, 'W' if wrong, 'Q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    prediction_text = "No face"

    for face in faces:
        landmarks = predictor(gray, face)

        left_eye_img, left_eye_display = get_eye(frame, landmarks, list(range(36, 42)))
        right_eye_img, right_eye_display = get_eye(frame, landmarks, list(range(42, 48)))

        # Resize for display
        height = max(left_eye_display.shape[0], right_eye_display.shape[0])
        left_w = int(left_eye_display.shape[1] * (height / left_eye_display.shape[0]))
        right_w = int(right_eye_display.shape[1] * (height / right_eye_display.shape[0]))
        left_resized = cv2.resize(left_eye_display, (left_w, height))
        right_resized = cv2.resize(right_eye_display, (right_w, height))
        display_eyes = np.hstack((left_resized, right_resized))
        cv2.imshow("Eye Zoom", display_eyes)

        # Predict each eye separately
        left_input = np.expand_dims(left_eye_img, axis=0)
        right_input = np.expand_dims(right_eye_img, axis=0)
        left_probs = model.predict(left_input, verbose=0)[0]
        right_probs = model.predict(right_input, verbose=0)[0]

        probs = (left_probs + right_probs) / 2.0
        pred_index = np.argmax(probs)
        prediction_text = LABELS[pred_index]

        # Confidence threshold for normal eyes
        if np.max(probs) < 0.6:
            prediction_text = "normal"

        break  # first face only

    cv2.putText(frame, f"Prediction: {prediction_text}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imshow("Gaze Prediction", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        continue  # prediction correct
    elif key == ord('w'):
        correct_label = input(f"Enter correct label ({'/'.join(LABELS)}): ").strip()
        if correct_label in LABELS:
            save_path = os.path.join(DATA_DIR, correct_label, f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            combined_display = np.hstack((left_resized, right_resized))
            cv2.imwrite(save_path, combined_display)
            with open(CSV_PATH, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([save_path, correct_label])
            print(f"[INFO] Saved corrected sample: {save_path}")
        else:
            print("[WARN] Invalid label. Skipped.")

cap.release()
cv2.destroyAllWindows()
