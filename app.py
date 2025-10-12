import streamlit as st
from eye_gesture import get_gesture_frame, release_camera
import cv2
import numpy as np

st.title("Live Eye Gesture Dashboard")

placeholder = st.empty()
event_placeholder = st.empty()

try:
    while True:
        event = get_gesture_frame()

        if event:
            event_placeholder.text(f"Detected Event: {event}")

except KeyboardInterrupt:
    release_camera()
