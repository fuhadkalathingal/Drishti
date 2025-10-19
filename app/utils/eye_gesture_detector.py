from time import perf_counter

class GestureDetector:
    def __init__(
        self, closed_threshold=0.6, open_threshold=0.2, max_fast_blink_duration=0.4,
        max_slow_blink_duration=0.8,
        gaze_enter_threshold=0.6, gaze_exit_threshold=0.55,
        max_fast_gaze_duration=0.5, max_slow_gaze_duration=1.0,
        gaze_up_enter_threshold=0.2, gaze_up_exit_threshold=0.18
    ):
        # Blink Detection
        self.closed_threshold = closed_threshold
        self.open_threshold = open_threshold
        self.max_fast_blink_duration = max_fast_blink_duration
        self.max_slow_blink_duration = max_slow_blink_duration
        self.eye_closed = False
        self.blink_start_time = 0

        # Gaze Detection
        self.gaze_enter_threshold = gaze_enter_threshold
        self.gaze_exit_threshold = gaze_exit_threshold
        self.max_fast_gaze_duration = max_fast_gaze_duration
        self.max_slow_gaze_duration = max_slow_gaze_duration
        self.looking_left = False
        self.looking_right = False
        self.looking_start_time_right = 0
        self.looking_start_time_left = 0

        # Look Up detection
        self.gaze_up_enter_threshold = gaze_up_enter_threshold
        self.gaze_up_exit_threshold = gaze_up_exit_threshold
        self.looking_start_time_up = 0
        self.looking_up = False

    def updateBlinks(self, left_blink, right_blink):
        blink_events = []

        blink = (left_blink + right_blink) / 2

        if blink > self.closed_threshold and not self.eye_closed:
            self.eye_closed = True
            self.blink_start_time = perf_counter()
        elif blink < self.open_threshold and self.eye_closed:
            self.eye_closed = False
            duration = perf_counter() - self.blink_start_time
            if duration < self.max_fast_blink_duration:
                blink_events.append("FB")
            elif duration < self.max_slow_blink_duration:
                blink_events.append("SB")
            else:
                blink_events.append("VSB")

        return blink_events

    def updateHorizontalGaze(
        self, 
        eye_look_in_left, eye_look_out_right,
        eye_look_in_right, eye_look_out_left
    ):
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
        if eye_look_left > self.gaze_enter_threshold or self.looking_left:
            if not self.looking_left:
                self.looking_left = True
                self.looking_start_time_left = perf_counter()
            elif eye_look_left < self.gaze_exit_threshold and self.looking_left:
                self.looking_left = False
                duration = perf_counter() - self.looking_start_time_left
                if duration < self.max_slow_gaze_duration:
                    gaze_event.append("FL")
                #elif duration < self.max_slow_gaze_duration:
                #    gaze_event.append("SL")

        # --- RIGHT GAZE ---
        elif eye_look_right > self.gaze_enter_threshold or self.looking_right:
            if not self.looking_right:
                self.looking_right = True
                self.looking_start_time_right = perf_counter()
            elif eye_look_right < self.gaze_exit_threshold and self.looking_right:
                self.looking_right = False
                duration = perf_counter() - self.looking_start_time_right
                if duration < self.max_fast_gaze_duration:
                    gaze_event.append("SR")
                #elif duration < self.max_slow_gaze_duration:
                #    gaze_event.append("SR")
                else:
                    gaze_event.append("SR")

        return gaze_event

    def updateUpGaze(self, eyeLookUpLeft, eyeLookUpRight):
        gaze_up_event = []

        gaze_up = (eyeLookUpLeft + eyeLookUpRight) / 2

        if gaze_up > self.gaze_up_enter_threshold and not self.looking_up:
            self.looking_up = True
            self.looking_start_time_up = perf_counter()
        elif gaze_up < self.gaze_up_exit_threshold and self.looking_up:
            self.looking_up = False
            duration = perf_counter() - self.looking_start_time_up
            if duration < self.max_slow_gaze_duration:
                gaze_up_event.append("FU")
            #elif duration < self.max_slow_gaze_duration:
            #    gaze_up_event.append("SU")

        return gaze_up_event

    def update(
        self,
        left_blink, right_blink,
        eye_look_in_left, eye_look_out_right,
        eye_look_in_right, eye_look_out_left,
        eyeLookUpLeft, eyeLookUpRight
    ):
        blink_event = self.updateBlinks(left_blink, right_blink)
        gaze_event = self.updateHorizontalGaze(
            eye_look_in_left, eye_look_out_right, eye_look_in_right, eye_look_out_left
        )
        gaze_up_event = self.updateUpGaze(eyeLookUpLeft, eyeLookUpRight)

        return blink_event + gaze_event + gaze_up_event
