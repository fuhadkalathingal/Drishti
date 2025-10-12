import time

class BlinkDetector:
    def __init__(
        self, closed_threshold=0.6, open_threshold=0.2, max_fast_blink_duration=0.5,
        max_slow_blink_duration=1.0
    ):
        self.closed_threshold = closed_threshold
        self.open_threshold = open_threshold
        self.max_fast_blink_duration = max_fast_blink_duration
        self.max_slow_blink_duration = max_slow_blink_duration
        self.left_closed = False
        self.right_closed = False
        self.left_start_time = 0
        self.right_start_time = 0

    def update(self, left_blink, right_blink):
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
