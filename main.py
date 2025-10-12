import cv2
import mediapipe as mp
import numpy as np

from face_gesture_detector import GestureDetector

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Initialize
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="face_landmarker.task"),
    running_mode=VisionRunningMode.IMAGE,
    num_faces=1,
    output_face_blendshapes = True
)

detector = FaceLandmarker.create_from_options(options)
gesture_detector = GestureDetector()

# Webcam
cap = cv2.VideoCapture(0)

blink_count = 0
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

    result = detector.detect(mp_image)

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

        blink_event = gesture_detector.updateBlinks(left_blink, right_blink)
        if len(blink_event) == 1:
            print(blink_event[0])

        gaze_event = gesture_detector.updateHorizontalGaze(
            eye_look_in_left, eye_look_out_right, eye_look_in_right, eye_look_out_left
        )
        if (len(gaze_event) == 1):
            print(gaze_event[0])

        gaze_up_event = gesture_detector.updateUpGaze(eye_look_up_left, eye_look_up_right)
        if (len(gaze_up_event) == 1):
            print(gaze_up_event[0])

    cv2.imshow("Eye Landmarks", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
