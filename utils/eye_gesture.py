import cv2
import mediapipe as mp
from eye_gesture_detector import GestureDetector

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Initialize
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="face_landmarker.task"),
    running_mode=VisionRunningMode.IMAGE,
    num_faces=1,
    output_face_blendshapes=True
)
detector = FaceLandmarker.create_from_options(options)
gesture_detector = GestureDetector()

# Webcam capture object
cap = cv2.VideoCapture(0)

def get_gesture_frame():
    """Returns the current frame and any detected events."""
    success, frame = cap.read()
    if not success:
        return None, None

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
