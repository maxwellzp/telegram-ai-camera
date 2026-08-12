import logging
from pathlib import Path
from datetime import datetime
from PIL import Image
import cv2

from config import JPEG_QUALITY, PHOTO_DIR
from ai import (
    analyze_motion,
    ask_about_photo,
    look_at_photo,
)



logger = logging.getLogger(__name__)


def capture_photo(camera_service) -> Path:
    logger.info("Capturing photo")

    photo_path = camera_service.capture_photo()

    logger.info(
        "Photo captured: %s",
        photo_path,
    )

    return photo_path


def analyze_photo(
    photo_path: Path,
    question: str,
) -> str:
    logger.info(
        "Analyzing photo with question: %s",
        question,
    )

    answer = ask_about_photo(
        photo_path,
        question,
    )

    logger.info("Photo analysis completed")

    return answer


def describe_photo(photo_path: Path) -> str:
    logger.info(
        "Describing photo: %s",
        photo_path,
    )

    description = look_at_photo(
        photo_path
    )

    logger.info("Photo description completed")

    return description

def save_motion_frame(frame) -> Path:
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    photo_path = (
        PHOTO_DIR / f"motion_{timestamp}.jpg"
    )

    cv2.imwrite(
        str(photo_path),
        frame,
        [
            cv2.IMWRITE_JPEG_QUALITY,
            JPEG_QUALITY,
        ],
    )

    logger.info(
        "Motion photo saved: %s",
        photo_path,
    )

    return photo_path

def analyze_motion_photo(
    photo_path: Path,
) -> tuple[bool, str]:
    logger.info(
        "Analyzing motion photo: %s",
        photo_path,
    )

    alert, description = analyze_motion(
        photo_path
    )

    logger.info(
        "Motion AI analysis completed: "
        "alert=%s",
        alert,
    )

    return alert, description