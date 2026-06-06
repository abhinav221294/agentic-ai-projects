# =========================
# image_tools.py
# =========================

from langchain.tools import tool

from src.integrations.image_client import generate_image


@tool
def image_generation_tool(
    prompt: str
):

    """
    Generates image using OpenAI image model.
    """

    image_url = generate_image(prompt)

    return image_url