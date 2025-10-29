import cv2
import mediapipe as mp
import yaml
from pathlib import Path
from app.utils.eye_gesture_detector import GestureDetector

# --- Mediapipe setup ---
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# --- Paths ---
CONFIG_PATH = Path("cache/config.yaml")

# --- Initialize Mediapipe face detector ---
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="data/face_landmarker.task"),
    running_mode=VisionRunningMode.IMAGE,
    num_faces=1,
    output_face_blendshapes=True
)
detector = FaceLandmarker.create_from_options(options)

# --- Camera capture object ---
cap = cv2.VideoCapture(0)

# --- Global gesture detector instance ---
gesture_detector = None


# -------------------------------------------------------------------
# CONFIG / CLASS RELOAD MANAGEMENT
# -------------------------------------------------------------------
def load_config():
    """Load thresholds safely from config.yaml."""
    with open(CONFIG_PATH, "r") as f:
        data = yaml.safe_load(f)
    return data


def reload_gesture_detector():
    """
    Recreate the GestureDetector instance using the latest config.yaml.
    Safe to call any time from other modules.
    """
    global gesture_detector

    cfg = load_config()
    gesture_detector = GestureDetector(
        closed_threshold=cfg["closed_threshold"],
        open_threshold=cfg["open_threshold"],
        gaze_enter_threshold=cfg["gaze_enter_threshold"],
        gaze_exit_threshold=cfg["gaze_exit_threshold"],
        gaze_up_enter_threshold=cfg["gaze_up_enter_threshold"],
        gaze_up_exit_threshold=cfg["gaze_up_exit_threshold"],
    )


# Load it once on module import
reload_gesture_detector()


# -------------------------------------------------------------------
# MAIN EVENT READER
# -------------------------------------------------------------------
def get_gesture_frame():
    """Returns detected event string or None."""
    success, frame = cap.read()
    if not success:
        return None

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    result = detector.detect(mp_image)

    event = None
    if result.face_blendshapes:
        blendshapes = result.face_blendshapes[0]
        left_blink = next((b.score for b in blendshapes if b.category_name == "eyeBlinkLeft"), 0.0)
        right_blink = next((b.score for b in blendshapes if b.category_name == "eyeBlinkRight"), 0.0)
        eye_look_in_left = next((b.score for b in blendshapes if b.category_name == "eyeLookInLeft"), 0.0)
        eye_look_out_left = next((b.score for b in blendshapes if b.category_name == "eyeLookOutLeft"), 0.0)
        eye_look_in_right = next((b.score for b in blendshapes if b.category_name == "eyeLookInRight"), 0.0)
        eye_look_out_right = next((b.score for b in blendshapes if b.category_name == "eyeLookOutRight"), 0.0)
        eye_look_up_left = next((b.score for b in blendshapes if b.category_name == "eyeLookUpLeft"), 0.0)
        eye_look_up_right = next((b.score for b in blendshapes if b.category_name == "eyeLookUpRight"), 0.0)

        events = gesture_detector.update(
            left_blink, right_blink,
            eye_look_in_left, eye_look_out_right,
            eye_look_in_right, eye_look_out_left,
            eye_look_up_left, eye_look_up_right
        )

        if len(events) == 1:
            event = events[0]

    return event


def release_camera():
    cap.release()
