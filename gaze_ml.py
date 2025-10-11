"""
Gaze & Blink ML Pipeline using Iris Coordinates
Manual Data Collection + ML Training + Real-time Prediction
Labels: LEFT, RIGHT, UP, CENTER, SLOW_BLINK, DOUBLE_BLINK, LEFT_EYE_BLINK
SPACE to capture frame, ESC to exit
"""

import os
import csv
import numpy as np
import cv2
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from gaze_tracking import GazeTracking

# -------------------- CONFIG --------------------
CSV_FILE = "gaze_coordinates.csv"
MODEL_FILE = "gaze_coordinates_model.h5"
labels = {
    "1": "LEFT",
    "2": "RIGHT",
    "3": "UP",
    "4": "CENTER",
    "s": "SLOW_BLINK",
    "d": "DOUBLE_BLINK",
    "l": "LEFT_EYE_BLINK"
}

# -------------------- MANUAL COORDINATE COLLECTION --------------------
def collect_coordinates():
    gaze = GazeTracking()
    cap = cv2.VideoCapture(0)
    current_label = None

    # Open CSV for appending
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write header if file empty
        if file.tell() == 0:
            writer.writerow(["left_x","left_y","right_x","right_y","label"])

        print("Manual Iris Coordinate Collection")
        print("Press key to select label (1-4, s, d, l)")
        print("Press SPACE to capture frame with label, ESC to exit")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gaze.refresh(frame)
            frame_disp = gaze.annotated_frame()

            if current_label:
                cv2.putText(frame_disp, f"Label: {current_label}", (20,50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0),2)

            cv2.imshow("Gaze Capture", frame_disp)
            key = cv2.waitKey(1) & 0xFF

            # Change current label
            if chr(key) in labels:
                current_label = labels[chr(key)]
                print(f"Label selected: {current_label}")

            # Capture coordinates
            if key == 32 and current_label and gaze.pupils_located:  # SPACE
                left = gaze.pupil_left_coords()
                right = gaze.pupil_right_coords()
                writer.writerow([left[0], left[1], right[0], right[1], current_label])
                print(f"Saved coordinates: {left}, {right} for {current_label}")

            if key == 27:  # ESC
                break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Coordinate data saved in {CSV_FILE}")

# -------------------- LOAD DATA --------------------
def load_coordinate_dataset():
    if not os.path.exists(CSV_FILE):
        print("No CSV file found. Collect data first!")
        return None, None, None
    data = []
    labels_list = []
    label_names = list(set(labels.values()))
    with open(CSV_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            coords = [float(row['left_x']), float(row['left_y']),
                      float(row['right_x']), float(row['right_y'])]
            data.append(coords)
            labels_list.append(label_names.index(row['label']))
    X = np.array(data)
    y = to_categorical(np.array(labels_list), num_classes=len(label_names))
    return X, y, label_names

# -------------------- TRAIN MODEL --------------------
def train_model():
    X, y, label_names = load_coordinate_dataset()
    if X is None:
        return label_names

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Sequential([
        Dense(32, activation='relu', input_shape=(4,)),
        Dense(64, activation='relu'),
        Dense(len(label_names), activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=50, batch_size=8)
    model.save(MODEL_FILE)
    print(f"Model trained and saved as {MODEL_FILE}")
    return label_names

# -------------------- REAL-TIME PREDICTION --------------------
def realtime_prediction():
    if not os.path.exists(MODEL_FILE):
        print("Model not found! Train model first.")
        return

    model = load_model(MODEL_FILE)
    _, _, label_names = load_coordinate_dataset()
    gaze = GazeTracking()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gaze.refresh(frame)
        if gaze.pupils_located:
            left = gaze.pupil_left_coords()
            right = gaze.pupil_right_coords()
            inp = np.array([left[0], left[1], right[0], right[1]]).reshape(1,4)
            pred = model.predict(inp)
            label = label_names[pred.argmax()]
        else:
            label = "No pupils"

        frame_disp = gaze.annotated_frame()
        cv2.putText(frame_disp, label, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0),2)
        cv2.imshow("Real-time Prediction", frame_disp)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

# -------------------- MAIN --------------------
if __name__ == "__main__":
    print("Options:\n1. Collect Iris Coordinates\n2. Train Model\n3. Real-time Prediction")
    choice = input("Enter choice (1/2/3): ")
    if choice == "1":
        collect_coordinates()
    elif choice == "2":
        train_model()
    elif choice == "3":
        realtime_prediction()
