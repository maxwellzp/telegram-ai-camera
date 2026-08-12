import asyncio
import logging

from config import PHOTO_CLEANUP_INTERVAL
from photo_storage import PhotoStorage

logger = logging.getLogger(__name__)


class PhotoCleanupTask:
    def __init__(self, storage: PhotoStorage):
        self.storage = storage
        self.task = None

    async def start(self):
        logger.info("Starting photo cleanup task")

        self.task = asyncio.create_task(
            self._run(),
            name="photo-cleanup",
        )

    async def stop(self):
        if self.task is None:
            return

        logger.info("Stopping photo cleanup task")

        self.task.cancel()

        try:
            await self.task
        except asyncio.CancelledError:
            pass

        self.task = None

        logger.info("Photo cleanup task stopped")

    async def _run(self):
        while True:
            try:
                await asyncio.sleep(
                    PHOTO_CLEANUP_INTERVAL
                )

                logger.info(
                    "Running scheduled photo cleanup"
                )

                self.storage.cleanup()

            except asyncio.CancelledError:
                raise

            except Exception:
                logger.exception(
                    "Photo cleanup task failed"
                )