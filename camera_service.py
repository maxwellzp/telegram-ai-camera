import logging
import threading
from pathlib import Path

from libcamera import Transform
from picamera2 import Picamera2

from config import CAMERA_SIZE, PHOTO_DIR


logger = logging.getLogger(__name__)


class CameraService:
    def __init__(self):
        self.camera = Picamera2()
        self.lock = threading.Lock()
        self.running = False

    def start(self):
        if self.running:
            logger.warning("Camera is already running")
            return

        config = self.camera.create_video_configuration(
            main={
                "size": CAMERA_SIZE,
                "format": "RGB888",
            },
            transform=Transform(
                hflip=1,
                vflip=1,
            ),
        )

        self.camera.configure(config)
        self.camera.start()

        self.running = True

        logger.info(
            "Camera started: %dx%d",
            CAMERA_SIZE[0],
            CAMERA_SIZE[1],
        )

    def stop(self):
        if not self.running:
            return

        self.camera.stop()
        self.running = False

        logger.info("Camera stopped")

    def capture_frame(self):
        if not self.running:
            raise RuntimeError(
                "Camera is not running"
            )

        with self.lock:
            return self.camera.capture_array()

    def capture_photo(
        self,
        filename: str = "photo.jpg",
    ) -> Path:
        if not self.running:
            raise RuntimeError(
                "Camera is not running"
            )

        photo_path = PHOTO_DIR / filename

        with self.lock:
            self.camera.capture_file(
                str(photo_path)
            )

        logger.info(
            "Photo captured: %s",
            photo_path,
        )

        return photo_path

    def close(self):
        if self.running:
            self.stop()

        self.camera.close()

        logger.info("Camera service closed")