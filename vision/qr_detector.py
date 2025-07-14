import cv2

class QRDetector:
    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def detect_zones(self, frame):
        zones = []
        retval, decoded_info, points, _ = self.detector.detectAndDecodeMulti(frame)
        if retval and points is not None:
            for i, text in enumerate(decoded_info):
                pts = points[i].astype(int)
                if text:
                    zones.append({
                        "label": text,
                        "coords": tuple(pts[0])
                    })
                    for j in range(4):
                        pt1 = tuple(pts[j])
                        pt2 = tuple(pts[(j + 1) % 4])
                        cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
                    cv2.putText(frame, text, tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return zones
