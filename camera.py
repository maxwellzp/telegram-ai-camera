from pathlib import Path

from picamera2 import Picamera2
from libcamera import Transform

from config import PHOTO_DIR


def take_photo(filename: str = "test.jpg") -> Path:
    photo_path = PHOTO_DIR / filename

    camera = Picamera2()

    config = camera.create_still_configuration(
        main={"size": (2304, 1296)}, transform=Transform(vflip=1)
    )

    camera.configure(config)
    camera.start()

    camera.capture_file(str(photo_path))

    camera.stop()
    camera.close()

    return photo_path


if __name__ == "__main__":
    photo = take_photo()
    print(f"Photo saved to: {photo}")