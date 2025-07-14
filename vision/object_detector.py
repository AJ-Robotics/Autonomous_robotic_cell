import cv2
import numpy as np

class ObjectDetector:
    def __init__(self):
        pass

    def detect_objects(self, frame):
        # Preprocess
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        objects = []
        for idx, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            if area > 500:  # Ignore small noise
                x, y, w, h = cv2.boundingRect(cnt)
                center = (x + w // 2, y + h // 2)
                label = f"Object{idx+1}"

                # Draw detection on the frame
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                # Save for UI
                objects.append({
                    "label": label,
                    "coords": center
                })

        return objects, []
