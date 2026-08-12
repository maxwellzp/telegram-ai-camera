import base64
import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

from config import (
    AI_IMAGE_SIZE,
    JPEG_QUALITY,
    MODEL,
    MOTION_AI_PROMPT,
)


load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def image_to_base64(photo_path: Path) -> str:
    with Image.open(photo_path) as image:
        image = image.convert("RGB")
        image = image.resize(AI_IMAGE_SIZE)

        buffer = BytesIO()

        image.save(
            buffer,
            format="JPEG",
            quality=JPEG_QUALITY,
        )

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _analyze_photo(photo_path: Path, prompt: str) -> str:
    image_data = image_to_base64(photo_path)

    response = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            f"data:image/jpeg;base64,{image_data}"
                        ),
                    },
                ],
            }
        ],
    )

    return response.output_text


def ask_about_photo(photo_path: Path, question: str) -> str:
    return _analyze_photo(
        photo_path,
        question,
    )


def look_at_photo(photo_path: Path) -> str:
    prompt = (
        "Describe what you see in this image. "
        "Focus on the main objects, people, "
        "and anything important or unusual. "
        "Be concise."
    )

    return _analyze_photo(
        photo_path,
        prompt,
    )

def analyze_motion(
    photo_path: Path,
) -> tuple[bool, str]:
    prompt = MOTION_AI_PROMPT

    result = _analyze_photo(
        photo_path,
        prompt,
    )

    lines = [
        line.strip()
        for line in result.splitlines()
        if line.strip()
    ]

    alert = False
    description = result

    for line in lines:
        if line.startswith("ALERT:"):
            value = line.split(
                ":", 1
            )[1].strip().upper()

            alert = value == "YES"

        elif line.startswith("DESCRIPTION:"):
            description = line.split(
                ":", 1
            )[1].strip()

    return alert, description