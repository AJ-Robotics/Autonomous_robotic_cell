import cv2

class CameraSettings:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera {camera_index}")

    def set_brightness(self, value):
        if self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value / 255.0):
            print(f"[CameraSettings] Brightness set to {value}")
        else:
            print("[CameraSettings] Failed to set brightness")

    def set_gain(self, value):
        if self.cap.set(cv2.CAP_PROP_GAIN, value / 255.0):
            print(f"[CameraSettings] Gain set to {value}")
        else:
            print("[CameraSettings] Failed to set gain")

    def set_exposure(self, value):
        if self.cap.set(cv2.CAP_PROP_EXPOSURE, float(value)):
            print(f"[CameraSettings] Exposure set to {value}")
        else:
            print("[CameraSettings] Failed to set exposure")

    def get_frame(self):
        ret, frame = self.cap.read()
        return frame if ret else None

    def release(self):
        self.cap.release()
