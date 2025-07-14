import cv2
import threading

class CameraHandler:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"[CameraHandler] Failed to open camera at index {camera_index}")
        
        self.lock = threading.Lock()
        self.frame = None
        self.running = True

        self.thread = threading.Thread(target=self._update_frame, daemon=True)
        self.thread.start()

    def _update_frame(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame

    def get_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def set_brightness(self, value):
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value / 255.0)

    def set_gain(self, value):
        self.cap.set(cv2.CAP_PROP_GAIN, value / 255.0)

    def set_exposure(self, value):
        self.cap.set(cv2.CAP_PROP_EXPOSURE, float(value))

    def release(self):
        self.running = False
        self.thread.join()
        self.cap.release()
class CameraHandler:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)

    def set_camera_index(self, index):
        if self.cap is not None:
            self.cap.release()
        self.camera_index = index
        self.cap = cv2.VideoCapture(self.camera_index)

    def get_frame(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

    def set_brightness(self, value):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value)

    def set_gain(self, value):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_GAIN, value)

    def set_exposure(self, value):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_EXPOSURE, float(value))