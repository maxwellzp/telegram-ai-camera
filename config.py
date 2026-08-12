from pathlib import Path


MODEL = "gpt-5-mini"

AI_IMAGE_SIZE = (768, 432)
JPEG_QUALITY = 85

PHOTO_DIR = Path("photos")
PHOTO_DIR.mkdir(exist_ok=True)


# Camera
CAMERA_SIZE = (2304, 1296)
WATCHER_FRAME_SIZE = (640, 360)


# Motion detection
MOTION_THRESHOLD = 25
MIN_MOTION_AREA = 5000
MOTION_CHECK_INTERVAL = 0.1
MOTION_COOLDOWN = 10

MOTION_AI_ENABLED = True

MOTION_AI_COOLDOWN = 30

MOTION_AI_PROMPT = (
    "You are analyzing a security camera image.\n\n"
    "Determine whether the image contains something that "
    "should trigger a security notification.\n\n"
    "Important events include:\n"
    "- a person\n"
    "- an animal\n"
    "- an unfamiliar or unusual object\n"
    "- something that appears to have changed significantly\n\n"
    "Do not trigger an alert for minor lighting changes, "
    "shadows, reflections, or insignificant movements.\n\n"
    "Respond with exactly two lines:\n"
    "ALERT: YES or NO\n"
    "DESCRIPTION: <short description>"
)

PHOTO_RETENTION_HOURS = 24
MAX_PHOTOS = 100
PHOTO_CLEANUP_INTERVAL = 60 * 60