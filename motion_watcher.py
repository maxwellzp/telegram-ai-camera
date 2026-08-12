import logging
import time
from collections.abc import Callable

import cv2

from config import (
    MIN_MOTION_AREA,
    MOTION_CHECK_INTERVAL,
    MOTION_COOLDOWN,
    MOTION_THRESHOLD,
    WATCHER_FRAME_SIZE,
)
from motion_detector import MotionDetector


logger = logging.getLogger(__name__)


class MotionWatcher:
    def __init__(
        self,
        camera,
        on_motion: Callable,
    ):
        self.camera = camera
        self.on_motion = on_motion

        self.detector = MotionDetector(
            threshold=MOTION_THRESHOLD,
            min_area=MIN_MOTION_AREA,
        )

        self.last_motion_time = 0.0
        self.running = False

    def start(self):
        logger.info("Starting motion watcher")

        self.running = True

        logger.info("Motion watcher started")

        try:
            while self.running:
                frame = self.camera.capture_frame()

                small_frame = cv2.resize(
                    frame,
                    WATCHER_FRAME_SIZE,
                )

                if self.detector.detect(
                    small_frame
                ):
                    self._handle_motion(frame)

                time.sleep(
                    MOTION_CHECK_INTERVAL
                )

        except Exception:
            logger.exception(
                "Motion watcher failed"
            )

        finally:
            logger.info(
                "Motion watcher stopped"
            )

    def stop(self):
        logger.info(
            "Stopping motion watcher"
        )

        self.running = False

    def _handle_motion(self, frame):
        current_time = time.monotonic()

        if (
            current_time - self.last_motion_time
            < MOTION_COOLDOWN
        ):
            return

        self.last_motion_time = current_time

        logger.info(
            "Motion event detected"
        )

        try:
            self.on_motion(frame)

        except Exception:
            logger.exception(
                "Motion event callback failed"
            )