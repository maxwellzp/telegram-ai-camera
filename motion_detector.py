import cv2


class MotionDetector:
    def __init__(
        self,
        threshold: int,
        min_area: int,
    ):
        self.threshold = threshold
        self.min_area = min_area
        self.previous_frame = None

    def detect(self, frame) -> bool:
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY,
        )

        gray = cv2.GaussianBlur(
            gray,
            (21, 21),
            0,
        )

        if self.previous_frame is None:
            self.previous_frame = gray
            return False

        difference = cv2.absdiff(
            self.previous_frame,
            gray,
        )

        _, thresholded = cv2.threshold(
            difference,
            self.threshold,
            255,
            cv2.THRESH_BINARY,
        )

        thresholded = cv2.dilate(
            thresholded,
            None,
            iterations=2,
        )

        contours, _ = cv2.findContours(
            thresholded,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        self.previous_frame = gray

        for contour in contours:
            if cv2.contourArea(contour) >= self.min_area:
                return True

        return False