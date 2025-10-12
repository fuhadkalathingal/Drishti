import streamlit as st
from eye_gesture import get_gesture_frame, release_camera
import cv2
import numpy as np

st.title("Live Eye Gesture Dashboard")

placeholder = st.empty()
event_placeholder = st.empty()

try:
    while True:
        frame, event = get_gesture_frame()
        if frame is None:
            continue

        # Convert BGR to RGB for Streamlit
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        placeholder.image(frame_rgb, channels="RGB")

        if event:
            event_placeholder.text(f"Detected Event: {event}")

except KeyboardInterrupt:
    release_camera()
