import os

from dotenv import load_dotenv

load_dotenv()

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from camera import take_photo
from ai import ask_about_photo, look_at_photo


TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
    "Hello! I am PiSight, your AI camera assistant.\n\n"
    "/photo - Take a photo\n"
    "/look - Describe what the camera sees\n"
    "/ask <question> - Ask AI about what the camera sees"
)


async def photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "Taking a photo..."
    )

    photo_path = take_photo()

    with photo_path.open("rb") as photo_file:
        await update.message.reply_photo(
            photo=photo_file
        )


async def ask(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    question = " ".join(context.args).strip()

    if not question:
        await update.message.reply_text(
            "Please provide a question.\n\n"
            "Example:\n"
            "/ask What is in front of the camera?"
        )
        return

    await update.message.reply_text(
        "Taking a photo..."
    )

    photo_path = take_photo()

    await update.message.reply_text(
        "Analyzing the photo..."
    )

    answer = ask_about_photo(
        photo_path,
        question,
    )

    await update.message.reply_text(
        answer
    )

async def look(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "📷 Taking a photo..."
    )

    photo_path = take_photo()

    await update.message.reply_text(
        "🤖 Analyzing the photo..."
    )

    description = look_at_photo(photo_path)

    await update.message.reply_text(
        description
    )

def main():
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
        CommandHandler("ask", ask)
    )

    application.add_handler(
    CommandHandler("look", look)
    )

    print("VisionPi bot started.")

    application.run_polling()


if __name__ == "__main__":
    main()
