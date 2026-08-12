import logging
from datetime import datetime, timedelta
from pathlib import Path

from config import (
    MAX_PHOTOS,
    PHOTO_DIR,
    PHOTO_RETENTION_HOURS,
)

logger = logging.getLogger(__name__)


class PhotoStorage:
    def __init__(
        self,
        photo_dir: Path = PHOTO_DIR,
    ):
        self.photo_dir = photo_dir

        self.photo_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def cleanup(self) -> None:
        logger.info("Starting photo storage cleanup")

        photos = self._get_photos()

        if not photos:
            logger.info("No photos to clean up")
            return

        removed_by_age = self._remove_old_photos(photos)

        photos = self._get_photos()

        removed_by_limit = self._remove_excess_photos(
            photos
        )

        logger.info(
            "Photo storage cleanup completed: "
            "removed %d old photos and %d excess photos",
            removed_by_age,
            removed_by_limit,
        )

    def _get_photos(self) -> list[Path]:
        return sorted(
            (
                path
                for path in self.photo_dir.iterdir()
                if path.is_file()
                and path.suffix.lower() in {".jpg", ".jpeg"}
            ),
            key=lambda path: path.stat().st_mtime,
        )

    def _remove_old_photos(
        self,
        photos: list[Path],
    ) -> int:
        cutoff = datetime.now() - timedelta(
            hours=PHOTO_RETENTION_HOURS
        )

        removed = 0

        for photo in photos:
            modified_time = datetime.fromtimestamp(
                photo.stat().st_mtime
            )

            if modified_time >= cutoff:
                continue

            self._delete(photo)
            removed += 1

        return removed

    def _remove_excess_photos(
        self,
        photos: list[Path],
    ) -> int:
        if len(photos) <= MAX_PHOTOS:
            return 0

        excess_count = len(photos) - MAX_PHOTOS
        removed = 0

        for photo in photos[:excess_count]:
            if self._delete(photo):
                removed += 1

        return removed

    def _delete(self, photo: Path) -> bool:
        try:
            photo.unlink()

            logger.info(
                "Deleted photo: %s",
                photo,
            )

            return True

        except FileNotFoundError:
            return False

        except OSError:
            logger.exception(
                "Failed to delete photo: %s",
                photo,
            )

            return False

    def format_size(self, size_bytes: int) -> str:
        size = float(size_bytes)

        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f} {unit}"

            size /= 1024

        return f"{size:.1f} TB"
    
    def get_stats(self) -> dict:
        photos = self._get_photos()

        total_size = sum(
            photo.stat().st_size
            for photo in photos
            if photo.exists()
        )

        oldest_photo = photos[0] if photos else None

        return {
            "count": len(photos),
            "max_photos": MAX_PHOTOS,
            "size_bytes": total_size,
            "retention_hours": PHOTO_RETENTION_HOURS,
            "oldest_photo": oldest_photo,
        }