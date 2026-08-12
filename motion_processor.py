import asyncio
import logging
import time

from telegram import Bot

from config import (
    MOTION_AI_COOLDOWN,
    MOTION_AI_ENABLED,
)

from services import (
    analyze_motion_photo,
    save_motion_frame,
)


logger = logging.getLogger(__name__)


class MotionProcessor:
    def __init__(
        self,
        bot: Bot,
    ):
        self.bot = bot
        self.last_ai_time = 0.0

    async def process(
        self,
        chat_id: int,
        frame,
    ):
        logger.info(
            "Processing motion event for chat %s",
            chat_id,
        )

        try:
            photo_path = save_motion_frame(
                frame
            )

            if not MOTION_AI_ENABLED:
                await self._send_photo(
                    chat_id,
                    photo_path,
                )
                return

            current_time = time.monotonic()

            if (
                current_time - self.last_ai_time
                < MOTION_AI_COOLDOWN
            ):
                logger.info(
                    "Motion AI cooldown active; "
                    "skipping AI analysis"
                )
                return

            self.last_ai_time = current_time

            logger.info(
                "Sending motion photo to OpenAI"
            )

            alert, description = await asyncio.to_thread(
                analyze_motion_photo,
                photo_path,
            )

            logger.info(
                "Motion AI result: alert=%s, "
                "description=%s",
                alert,
                description,
            )

            if not alert:
                logger.info(
                    "Motion event ignored by AI"
                )
                return

            await self.bot.send_message(
                chat_id=chat_id,
                text=(
                    "🚨 Motion detected!\n\n"
                    f"{description}"
                ),
            )

            await self._send_photo(
                chat_id,
                photo_path,
            )

        except Exception:
            logger.exception(
                "Failed to process motion event"
            )

    async def _send_photo(
        self,
        chat_id: int,
        photo_path,
    ):
        with photo_path.open("rb") as photo_file:
            await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo_file,
            )