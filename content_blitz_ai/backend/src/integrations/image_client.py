from pathlib import Path
import base64
import uuid
from openai import OpenAI
from src.core.config import APP_BASE_URL,IMAGE_MODEL
client = OpenAI()

BASE_DIR = Path(__file__).resolve().parents[2]   # backend
IMAGE_DIR = BASE_DIR / "static" / "images"

IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def generate_image(prompt: str):

    response = client.images.generate(
        model=IMAGE_MODEL,
        prompt=prompt,
        size="1024x1024",
    )

    image_bytes = base64.b64decode(response.data[0].b64_json)

    filename = f"{uuid.uuid4()}.png"
    filepath = IMAGE_DIR / filename

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return f"{APP_BASE_URL}/static/images/{filename}"