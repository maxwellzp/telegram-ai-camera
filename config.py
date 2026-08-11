from pathlib import Path


MODEL = "gpt-5-mini"

AI_IMAGE_SIZE = (768, 432)
JPEG_QUALITY = 85

PHOTO_DIR = Path("photos")
PHOTO_DIR.mkdir(exist_ok=True)