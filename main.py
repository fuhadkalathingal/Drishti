import cv2
import mediapipe as mp
import numpy as np

from face_gesture_detector import BlinkDetector

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
gesture_detector = BlinkDetector(closed_threshold=0.6, open_threshold=0.2)

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

        blink_events = gesture_detector.updateBlinks(left_blink, right_blink)
        if len(blink_events) == 2:
            if blink_events[0] == "Left blink fast" and blink_events[1] == "Right blink fast":
                print("fast blink")
            elif blink_events[0] == "Left blink slow" and blink_events[1] == "Right blink slow":
                print("slow blink")

        gaze_event = gesture_detector.updateGaze(eye_look_in_left, eye_look_out_right, eye_look_in_right, eye_look_out_left)
        if (len(gaze_event) == 1):
            print(gaze_event[0])

    cv2.imshow("Eye Landmarks", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
