from __future__ import division
import os
import cv2
import dlib
from collections import deque
from .eye import Eye
from .calibration import Calibration
import time

class GazeTracking(object):
    """
    Tracks gaze with 2D iris displacement and detects:
    - Slow blink (selection)
    - Double blink (navigation)
    - Left eye blink (deletion)
    """

    def __init__(self):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.calibration = Calibration()
        self._face_detector = dlib.get_frontal_face_detector()
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat")
        self._predictor = dlib.shape_predictor(model_path)

        # Blink detection
        self.blink_history = deque(maxlen=20)
        self.SHORT_BLINK_MIN = 1   # frames for double blink
        self.SHORT_BLINK_MAX = 4
        self.SLOW_BLINK_MIN  = 6   # frames for slow blink
        self.SLOW_BLINK_MAX  = 15
        self.blink_timestamps = deque(maxlen=5)

        # Iris smoothing
        self.dx_buffer = deque(maxlen=5)
        self.dy_buffer = deque(maxlen=5)

    # -------------------- Face & Eye Detection --------------------
    @property
    def pupils_located(self):
        try:
            int(self.eye_left.pupil.x)
            int(self.eye_left.pupil.y)
            int(self.eye_right.pupil.x)
            int(self.eye_right.pupil.y)
            return True
        except Exception:
            return False

    def _analyze(self):
        frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame_gray)
        try:
            landmarks = self._predictor(frame_gray, faces[0])
            self.eye_left = Eye(frame_gray, landmarks, 0, self.calibration)
            self.eye_right = Eye(frame_gray, landmarks, 1, self.calibration)
        except IndexError:
            self.eye_left = None
            self.eye_right = None

    def refresh(self, frame):
        self.frame = frame
        self._analyze()
        self.update_blink_history()

    # -------------------- Pupils Coordinates --------------------
    def pupil_left_coords(self):
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)

    def pupil_right_coords(self):
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return (x, y)

    # -------------------- 2D Iris Position --------------------
    def iris_position(self):
        if self.pupils_located:
            # x-axis: left = negative, right = positive
            dx_left  = self.eye_left.pupil.x - self.eye_left.center[0]
            dx_right = self.eye_right.pupil.x - self.eye_right.center[0]
            dx = (dx_right + dx_left) / (2 * self.eye_left.center[0])  # normalized [-1,1]

            # y-axis: up = positive, down = negative
            dy_left  = self.eye_left.center[1] - self.eye_left.pupil.y
            dy_right = self.eye_right.center[1] - self.eye_right.pupil.y
            dy = (dy_left + dy_right) / (2 * self.eye_left.center[1])  # normalized [-1,1]

            # smoothing
            self.dx_buffer.append(dx)
            self.dy_buffer.append(dy)
            dx_smooth = sum(self.dx_buffer)/len(self.dx_buffer)
            dy_smooth = sum(self.dy_buffer)/len(self.dy_buffer)

            return dx_smooth, dy_smooth
        return 0.0, 0.0

    # -------------------- Blinking --------------------
    def is_blinking(self):
        if self.pupils_located:
            blinking_ratio = (self.eye_left.blinking + self.eye_right.blinking)/2
            return blinking_ratio > 3.8
        return False

    def update_blink_history(self):
        blink = int(self.is_blinking())
        self.blink_history.append(blink)

    # -------------------- Slow Blink --------------------
    def is_slow_blink(self):
        hist = list(self.blink_history)
        blink_length = 0
        for b in reversed(hist):
            if b == 1:
                blink_length += 1
            elif blink_length > 0:
                if self.SLOW_BLINK_MIN <= blink_length <= self.SLOW_BLINK_MAX:
                    return True
                break
        return False

    # -------------------- Double Blink --------------------
    def is_double_blink(self):
        hist = list(self.blink_history)
        current_time = time.time()
        blink_length = 0
        for b in hist[::-1]:
            if b == 1:
                blink_length += 1
            elif blink_length > 0:
                if self.SHORT_BLINK_MIN <= blink_length <= self.SHORT_BLINK_MAX:
                    self.blink_timestamps.append(current_time)
                blink_length = 0

        if len(self.blink_timestamps) >= 2:
            t1, t2 = self.blink_timestamps[-2], self.blink_timestamps[-1]
            if (t2 - t1) <= 0.7:
                self.blink_timestamps.clear()
                return True
        return False

    # -------------------- One-eye blink for deletion --------------------
    def is_left_eye_blink(self):
        if self.pupils_located:
            left_ratio = self.eye_left.blinking
            right_ratio = self.eye_right.blinking
            return left_ratio > 3.8 and right_ratio < 2.0
        return False

    # -------------------- Annotated Frame --------------------
    def annotated_frame(self):
        frame = self.frame.copy()
        if self.pupils_located:
            color = (0,255,0)
            x_left, y_left = self.pupil_left_coords()
            x_right, y_right = self.pupil_right_coords()
            cv2.line(frame, (x_left-5, y_left), (x_left+5, y_left), color)
            cv2.line(frame, (x_left, y_left-5), (x_left, y_left+5), color)
            cv2.line(frame, (x_right-5, y_right), (x_right+5, y_right), color)
            cv2.line(frame, (x_right, y_right-5), (x_right, y_right+5), color)
        return frame
