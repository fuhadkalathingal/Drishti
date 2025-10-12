import time

class BlinkDetector:
    def __init__(
        self, closed_threshold=0.6, open_threshold=0.2, max_fast_blink_duration=0.5,
        max_slow_blink_duration=1.0,
        gaze_threshold=0.6, 
        max_fast_gaze_duration=0.5, max_slow_gaze_duration=1.0
    ):
        # Blink Detection
        self.closed_threshold = closed_threshold
        self.open_threshold = open_threshold
        self.max_fast_blink_duration = max_fast_blink_duration
        self.max_slow_blink_duration = max_slow_blink_duration
        self.left_closed = False
        self.right_closed = False
        self.left_start_time = 0
        self.right_start_time = 0

        # Gaze Detection
        self.gaze_threshold = gaze_threshold
        self.max_fast_gaze_duration = max_fast_gaze_duration
        self.max_slow_gaze_duration = max_slow_gaze_duration
        self.looking_left = False
        self.looking_right = False
        self.looking_start_time_right = 0
        self.looking_start_time_left = 0

    def updateBlinks(self, left_blink, right_blink):
        blink_events = []

        # Left eye
        if left_blink > self.closed_threshold and not self.left_closed:
            self.left_closed = True
            self.left_start_time = time.time()
        elif left_blink < self.open_threshold and self.left_closed:
            self.left_closed = False
            duration = time.time() - self.left_start_time
            if duration < self.max_fast_blink_duration:
                blink_events.append("Left blink fast")
            elif duration < self.max_slow_blink_duration:
                blink_events.append("Left blink slow")

        # Right eye
        if right_blink > self.closed_threshold and not self.right_closed:
            self.right_closed = True
            self.right_start_time = time.time()
        elif right_blink < self.open_threshold and self.right_closed:
            self.right_closed = False
            duration = time.time() - self.right_start_time
            if duration < self.max_fast_blink_duration:
                blink_events.append("Right blink fast")
            elif duration < self.max_slow_blink_duration:
                blink_events.append("Right blink slow")

        return blink_events

    def updateGaze(self, eye_look_in_left, eye_look_out_right, eye_look_in_right, eye_look_out_left):
        gaze_event = []

        eye_look_left = (eye_look_out_left + eye_look_in_right) / 2
        eye_look_right = (eye_look_out_right + eye_look_in_left) / 2

        # Neutral zone (avoid small noise)
        if abs(eye_look_left - eye_look_right) < 0.05:
            return []

        if self.looking_left:
            self.looking_right = False
        elif self.looking_right:
            self.looking_left = False

        # --- LEFT GAZE ---
        if eye_look_left > self.gaze_threshold or self.looking_left:
            if not self.looking_left:
                self.looking_left = True
                self.looking_start_time_left = time.time()
            elif eye_look_left < self.gaze_threshold and self.looking_left:
                self.looking_left = False
                duration = time.time() - self.looking_start_time_left
                if duration < self.max_fast_gaze_duration:
                    gaze_event.append("Look left fast")
                elif duration < self.max_slow_gaze_duration:
                    gaze_event.append("Look left slow")

        # --- RIGHT GAZE ---
        elif eye_look_right > self.gaze_threshold or self.looking_right:
            if not self.looking_right:
                self.looking_right = True
                self.looking_start_time_right = time.time()
            elif eye_look_right < self.gaze_threshold and self.looking_right:
                self.looking_right = False
                duration = time.time() - self.looking_start_time_right
                if duration < self.max_fast_gaze_duration:
                    gaze_event.append("Look right fast")
                elif duration < self.max_slow_gaze_duration:
                    gaze_event.append("Look right slow")

        return gaze_event
