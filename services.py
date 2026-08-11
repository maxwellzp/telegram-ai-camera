import logging
from pathlib import Path

from ai import ask_about_photo, look_at_photo
from camera import take_photo


logger = logging.getLogger(__name__)


def capture_photo() -> Path:
    logger.info("Capturing photo")

    photo_path = take_photo()

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

