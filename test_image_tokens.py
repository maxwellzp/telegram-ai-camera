import base64
import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SOURCE_IMAGE = Path("photos/test.jpg")

QUESTION = "Describe briefly what you see in this image."


def image_to_base64(image: Image.Image) -> str:
    buffer = BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=85,
    )

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def test_image(image: Image.Image, name: str):
    print(f"\n{'=' * 50}")
    print(f"{name}")
    print(f"Resolution: {image.width} x {image.height}")

    image_data = image_to_base64(image)

    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": QUESTION,
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

    print(f"Answer: {response.output_text}")

    print("\nUsage:")
    print(f"  Input tokens:  {response.usage.input_tokens}")
    print(f"  Output tokens: {response.usage.output_tokens}")
    print(f"  Total tokens:  {response.usage.total_tokens}")


def main():
    if not SOURCE_IMAGE.exists():
        raise FileNotFoundError(
            f"Image not found: {SOURCE_IMAGE}"
        )

    original = Image.open(SOURCE_IMAGE)

    print(f"Original image: {original.width} x {original.height}")

    test_image(
        original,
        "ORIGINAL",
    )

    test_image(
        original.resize((1152, 648)),
        "HALF SIZE",
    )

    test_image(
        original.resize((768, 432)),
        "SMALL",
    )


if __name__ == "__main__":
    main()

# (.venv) maksim@raspberrypi:~/telegram-ai-camera $ python3 test_image_tokens.py
# Original image: 2304 x 1296

# ==================================================
# ORIGINAL
# Resolution: 2304 x 1296
# Answer: A close-up of a smartphone or small tablet lying on a wooden surface. The device's glossy screen is reflecting a camera (with a small green LED) and some room details; the phone's white bezel and a headphone cable are also visible. The image is out of focus and slightly tilted.

# Usage:
#   Input tokens:  2780
#   Output tokens: 148
#   Total tokens:  2928

# ==================================================
# HALF SIZE
# Resolution: 1152 x 648
# Answer: A blurry close-up of a smartphone or touchscreen device lying on a wooden surface. The device's reflective screen shows faint reflections (including a small green LED), with a red cable and a white cord visible nearby.

# Usage:
#   Input tokens:  923
#   Output tokens: 299
#   Total tokens:  1222

# ==================================================
# SMALL
# Resolution: 768 x 432
# Answer: A slightly blurred, tilted photo of a white smartphone lying on a wooden shelf. The phone’s screen is reflecting the surroundings (including two small green lights), and a red cable is visible near the top of the frame.

# Usage:
#   Input tokens:  419
#   Output tokens: 148
#   Total tokens:  567
# (.venv) maksim@raspberrypi:~/telegram-ai-camera $ 
