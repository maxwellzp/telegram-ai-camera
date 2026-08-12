import asyncio
import logging
import os
import threading

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from logging_config import setup_logging
from motion_watcher import MotionWatcher
from services import (
    analyze_photo,
    capture_photo,
    describe_photo,
)
from motion_processor import MotionProcessor
from camera_service import CameraService


load_dotenv()

setup_logging()

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

# camera_service = CameraService()

watcher = None
watcher_thread = None

motion_queue = None
watch_chat_id = None

motion_consumer_task = None
motion_processor = None
shutdown_event = None


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id

    logger.info(
        "Received /start from user %s",
        user_id,
    )

    await update.message.reply_text(
        "Hello! I am VisionPi, your AI camera assistant.\n\n"
        "/photo - Take a photo\n"
        "/look - Describe what the camera sees\n"
        "/ask <question> - Ask AI about what the camera sees\n"
        "/watch - Start motion detection\n"
        "/stop - Stop motion detection"
    )


async def photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id

    logger.info(
        "User %s requested a photo",
        user_id,
    )

    try:
        await update.message.reply_text(
            "📷 Taking a photo..."
        )

        photo_path = camera_service.capture_photo()

        with photo_path.open("rb") as photo_file:
            await update.message.reply_photo(
                photo=photo_file
            )

        logger.info(
            "Photo sent to user %s",
            user_id,
        )

    except Exception:
        logger.exception(
            "Failed to take or send photo for user %s",
            user_id,
        )

        await update.message.reply_text(
            "❌ Failed to take a photo."
        )


async def look(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id

    logger.info(
        "User %s requested /look",
        user_id,
    )

    try:
        await update.message.reply_text(
            "📷 Taking a photo..."
        )

        photo_path = capture_photo(
            camera_service
            )

        await update.message.reply_text(
            "🤖 Analyzing the photo..."
        )

        description = describe_photo(
            photo_path
        )

        await update.message.reply_text(
            description
        )

        logger.info(
            "AI analysis completed for user %s",
            user_id,
        )

    except Exception:
        logger.exception(
            "Failed to process /look for user %s",
            user_id,
        )

        await update.message.reply_text(
            "❌ Failed to analyze the photo."
        )


async def ask(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id

    question = " ".join(
        context.args
    ).strip()

    if not question:
        await update.message.reply_text(
            "Please provide a question.\n\n"
            "Example:\n"
            "/ask What is in front of the camera?"
        )

        return

    logger.info(
        "User %s requested /ask: %s",
        user_id,
        question,
    )

    try:
        await update.message.reply_text(
            "📷 Taking a photo..."
        )

        photo_path = capture_photo(camera_service)

        await update.message.reply_text(
            "🤖 Analyzing the photo..."
        )

        answer = analyze_photo(
            photo_path,
            question,
        )

        await update.message.reply_text(
            answer
        )

        logger.info(
            "AI analysis completed for user %s",
            user_id,
        )

    except Exception:
        logger.exception(
            "Failed to process /ask for user %s",
            user_id,
        )

        await update.message.reply_text(
            "❌ Failed to analyze the photo."
        )


def handle_motion(frame):
    global motion_queue
    global watch_chat_id

    if motion_queue is None:
        logger.warning(
            "Motion event received but queue is not available"
        )
        return

    if watch_chat_id is None:
        logger.warning(
            "Motion event received but no chat is registered"
        )
        return

    logger.info(
        "Motion event received from watcher"
    )

    try:
        motion_queue.put_nowait(
            (
                watch_chat_id,
                frame.copy(),
            )
        )

    except Exception:
        logger.exception(
            "Failed to add motion event to queue"
        )


async def process_motion_events():
    logger.info(
        "Motion event consumer started"
    )

    while True:
        chat_id, frame = await motion_queue.get()

        try:
            await motion_processor.process(
                chat_id,
                frame,
            )

        except Exception:
            logger.exception(
                "Failed to process motion event"
            )

        finally:
            motion_queue.task_done()


async def watch(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    global watcher
    global watcher_thread
    global watch_chat_id

    chat_id = update.effective_chat.id

    if (
        watcher_thread is not None
        and watcher_thread.is_alive()
    ):
        await update.message.reply_text(
            "👁️ VisionPi is already watching."
        )
        return

    watch_chat_id = chat_id

    watcher = MotionWatcher(
        camera=camera_service,
        on_motion=handle_motion,
    )

    watcher_thread = threading.Thread(
        target=watcher.start,
        name="motion-watcher",
        daemon=True,
    )

    watcher_thread.start()

    logger.info(
        "Motion watcher started for chat %s",
        chat_id,
    )

    await update.message.reply_text(
        "👁️ VisionPi is now watching."
    )


async def stop_watch(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    global watcher
    global watcher_thread
    global watch_chat_id

    if watcher is None:
        await update.message.reply_text(
            "👁️ VisionPi is not watching."
        )
        return

    watcher.stop()

    if (
        watcher_thread is not None
        and watcher_thread.is_alive()
    ):
        await asyncio.to_thread(
            watcher_thread.join,
            2.0,
        )

    watcher = None
    watcher_thread = None
    watch_chat_id = None

    clear_motion_queue()

    logger.info(
        "Motion watcher stopped by chat %s",
        update.effective_chat.id,
    )

    await update.message.reply_text(
        "🛑 VisionPi stopped watching."
    )


async def post_init(
    application_instance: Application,
):
    global application
    global motion_queue
    global motion_consumer_task
    global motion_processor
    global camera_service

    application = application_instance

    motion_queue = asyncio.Queue()

    camera_service = CameraService()
    camera_service.start()

    motion_processor = MotionProcessor(
        bot=application.bot,
    )

    motion_consumer_task = asyncio.create_task(
        process_motion_events()
    )

    logger.info(
        "VisionPi initialization completed"
    )

async def post_shutdown(
    application_instance: Application,
):
    global watcher
    global watcher_thread
    global motion_consumer_task
    global camera_service

    logger.info(
        "Starting VisionPi graceful shutdown"
    )

    # Stop motion watcher
    if watcher is not None:
        logger.info(
            "Stopping motion watcher"
        )

        watcher.stop()

    # Wait for watcher thread to finish
    if (
        watcher_thread is not None
        and watcher_thread.is_alive()
    ):
        logger.info(
            "Waiting for motion watcher thread"
        )

        await asyncio.to_thread(
            watcher_thread.join,
            5.0,
        )

    watcher = None
    watcher_thread = None

    # Stop motion consumer
    if motion_consumer_task is not None:
        logger.info(
            "Stopping motion event consumer"
        )

        motion_consumer_task.cancel()

        try:
            await motion_consumer_task
        except asyncio.CancelledError:
            logger.info(
                "Motion event consumer stopped"
            )

        motion_consumer_task = None

    # Stop camera
    if camera_service is not None:
        logger.info(
            "Stopping camera service"
        )

        camera_service.stop()

    logger.info(
        "VisionPi graceful shutdown completed"
    )

def clear_motion_queue():
    if motion_queue is None:
        return

    cleared = 0

    while True:
        try:
            motion_queue.get_nowait()
            motion_queue.task_done()
            cleared += 1
        except asyncio.QueueEmpty:
            break

    if cleared:
        logger.info(
            "Cleared %s pending motion events",
            cleared,
        )


def main():
    logger.info(
        "Starting VisionPi bot"
    )

    application_instance = (Application.builder()
    .token(TELEGRAM_BOT_TOKEN)
    .post_init(post_init)
    .post_shutdown(post_shutdown)
    .build()
)

    application_instance.add_handler(
        CommandHandler("start", start)
    )

    application_instance.add_handler(
        CommandHandler("photo", photo)
    )

    application_instance.add_handler(
        CommandHandler("look", look)
    )

    application_instance.add_handler(
        CommandHandler("ask", ask)
    )

    application_instance.add_handler(
        CommandHandler("watch", watch)
    )

    application_instance.add_handler(
        CommandHandler("stop", stop_watch)
    )

    logger.info(
        "VisionPi bot started"
    )

    application_instance.run_polling()


if __name__ == "__main__":
    main()