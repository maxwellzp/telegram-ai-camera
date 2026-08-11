import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from logging_config import setup_logging
from services import (
    analyze_photo,
    capture_photo,
    describe_photo,
)


load_dotenv()

setup_logging()

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]


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
        "/ask <question> - Ask AI about what the camera sees"
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
            "Taking a photo..."
        )

        photo_path = capture_photo()

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
            "Taking a photo..."
        )

        photo_path = capture_photo()

        await update.message.reply_text(
            "Analyzing the photo..."
        )

        description = describe_photo(
            photo_path
        )

        logger.info(
            "AI analysis completed for user %s",
            user_id,
        )

        await update.message.reply_text(
            description
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
        logger.info(
            "User %s sent /ask without a question",
            user_id,
        )

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
            "Taking a photo..."
        )

        photo_path = capture_photo()

        await update.message.reply_text(
            "Analyzing the photo..."
        )

        answer = analyze_photo(
            photo_path,
            question,
        )

        logger.info(
            "AI analysis completed for user %s",
            user_id,
        )

        await update.message.reply_text(
            answer
        )

    except Exception:
        logger.exception(
            "Failed to process /ask for user %s",
            user_id,
        )

        await update.message.reply_text(
            "❌ Failed to analyze the photo."
        )


def main():
    logger.info("Starting VisionPi bot")

    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("photo", photo)
    )

    application.add_handler(
        CommandHandler("look", look)
    )

    application.add_handler(
        CommandHandler("ask", ask)
    )

    logger.info("VisionPi bot started")

    application.run_polling()


if __name__ == "__main__":
    main()

