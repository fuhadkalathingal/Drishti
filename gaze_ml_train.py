import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

# ================================================
# CONFIGURATION
# ================================================
DATA_DIR = "data"  # folders: data/normal, data/left, data/right, data/up, data/blink, data/slow_blink
IMAGE_SIZE = (96, 48)  # must match real-time gaze_ml
BATCH_SIZE = 32
EPOCHS = 20

LABELS = ["normal", "left", "right", "up", "blink", "slow_blink"]
label_to_index = {label: idx for idx, label in enumerate(LABELS)}

images = []
labels = []

print("[INFO] Loading images...")

for label in LABELS:
    folder = os.path.join(DATA_DIR, label)
    if not os.path.exists(folder):
        print(f"[WARN] Missing folder: {folder} — skipping this label")
        continue

    for file in os.listdir(folder):
        if file.lower().endswith((".jpg", ".png")):
            path = os.path.join(folder, file)
            img = cv2.imread(path)
            if img is None:
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, IMAGE_SIZE)
            gray = gray.astype("float32") / 255.0
            gray = np.expand_dims(gray, axis=-1)  # CNN expects (H,W,1)
            images.append(gray)
            labels.append(label_to_index[label])

if len(images) == 0:
    raise ValueError("[ERROR] No images found! Capture data first using gaze_ml_collect.py")

X = np.array(images)
y = to_categorical(labels, num_classes=len(LABELS))

print(f"[INFO] Dataset loaded: {X.shape[0]} samples, {X.shape[1:]} per image")

# ================================================
# Train/Test Split
# ================================================
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"[INFO] Training samples: {X_train.shape[0]}, Testing samples: {X_test.shape[0]}")

# ================================================
# MODEL DEFINITION
# ================================================
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(IMAGE_SIZE[1], IMAGE_SIZE[0], 1)),  # (H,W,1)
    MaxPooling2D((2,2)),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D((2,2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(len(LABELS), activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

# ================================================
# TRAIN MODEL
# ================================================
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=EPOCHS, batch_size=BATCH_SIZE)

# ================================================
# SAVE MODEL (native Keras format)
# ================================================
model_path = os.path.join("gaze_tracking", "gaze_model.keras")
model.save(model_path)
print(f"[INFO] Model saved to {model_path}")
