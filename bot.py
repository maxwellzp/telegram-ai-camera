import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from camera import take_photo


load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I'm AI Camera Assistant.\n\n"
        "/photo — to take a photo"
    )


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Taking a photo...")

    photo_path = take_photo()

    with photo_path.open("rb") as photo_file:
        await update.message.reply_photo(photo=photo_file)


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("photo", photo))

    print("Bot started")

    application.run_polling()


if __name__ == "__main__":
    main()
