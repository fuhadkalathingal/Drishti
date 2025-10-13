import streamlit as st
import time
from eye_gesture import get_gesture_frame, release_camera
from morse_decoder import event_to_letter

st.title("Live Eye Gesture Dashboard")

# Initialize session state once
if "morse_buffer" not in st.session_state:
    st.session_state.morse_buffer = ""
if "string" not in st.session_state:
    st.session_state.string = ""

event_placeholder = st.empty()
buffer_placeholder = st.empty()
string_placeholder = st.empty()

try:
    while True:
        event = get_gesture_frame()
        if event:
            event_placeholder.text(f"Detected Event: {event}")
            # Update buffer and string in session_state
            st.session_state.morse_buffer, st.session_state.string = event_to_letter(
                event,
                st.session_state.morse_buffer,
                st.session_state.string
            )
            buffer_placeholder.text(f"Morse buffer: {st.session_state.morse_buffer}")
            string_placeholder.text(f"String : {st.session_state.string}")
        time.sleep(0.05)  # small pause for UI updates

except Exception as e:
    release_camera()
    st.error(f"Error: {e}")
