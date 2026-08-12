# VisionPi

VisionPi is an AI-powered Telegram camera assistant running on a Raspberry Pi 5.

It combines a Raspberry Pi camera, Telegram Bot API, OpenAI vision models, and local motion detection.

The bot can take photos, analyze what the camera sees, answer questions about images, and monitor the camera for motion.

## Hardware

### Required

- Raspberry Pi 5
- Raspberry Pi Camera Module 3
- Internet connection

### Tested configuration

- Raspberry Pi 5
- Camera Module 3 (IMX708)
- Raspberry Pi OS
- Python 3.13
- Picamera2
- OpenCV

## Software Stack

- Python
- python-telegram-bot
- OpenAI API
- Picamera2
- libcamera
- OpenCV
- Pillow
- python-dotenv

## Installation

Clone the repository:
```bash
git clone git@github.com:maxwellzp/telegram-ai-camera.git
cd telegram-ai-camera
```

Create a virtual environment:

```bash
python3 -m venv --system-site-packages .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a .env file in the project root:

```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```
Replace your_telegram_bot_token with the token provided by BotFather.
```bash
OPENAI_API_KEY=your_openai_api_key
```
Replace your_openai_api_key with the Api key provided by platform.openai.com.

## Running the bot
From the project root:

source .venv/bin/activate
python3 bot.py
If everything is configured correctly, the terminal will display:
```text
Starting VisionPi bot
VisionPi bot started
```

Open the bot in Telegram and send:

```text
/start
```
You should see the menu.

## License
MIT