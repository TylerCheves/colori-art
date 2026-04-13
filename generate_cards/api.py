"""Gemini API wrapper for image generation and touchup."""

import os
import time
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

API_KEY = os.environ.get("GOOGLE_API_KEY")
BG_MODEL = "nano-banana-pro-preview"
TOUCHUP_MODEL = "gemini-3.1-flash-image-preview"
WIDTH, HEIGHT = 750, 1050

# Rate limiting
_last_call_time = 0.0
RATE_LIMIT_SECONDS = 5


def _rate_limit():
    """Enforce minimum delay between API calls."""
    global _last_call_time
    elapsed = time.time() - _last_call_time
    if elapsed < RATE_LIMIT_SECONDS:
        time.sleep(RATE_LIMIT_SECONDS - elapsed)
    _last_call_time = time.time()


def _get_client():
    """Create and return a Gemini client."""
    if not API_KEY:
        raise RuntimeError("GOOGLE_API_KEY environment variable is not set")
    return genai.Client(api_key=API_KEY)


def _extract_image(response):
    """Extract the first image from a Gemini response. Returns PIL Image or None."""
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            mime = getattr(part.inline_data, "mime_type", "")
            if mime.startswith("image/") or part.inline_data.data:
                return Image.open(BytesIO(part.inline_data.data))
    return None


def generate_image_no_ref(prompt, output_path):
    """Generate an image from a text prompt only (no reference image).

    Used for base background textures that don't need a style reference.

    Args:
        prompt: Text prompt for the generation.
        output_path: Where to save the generated image.

    Returns:
        True on success, False on failure.
    """
    client = _get_client()

    for attempt in range(2):
        _rate_limit()
        try:
            response = client.models.generate_content(
                model=BG_MODEL,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            img = _extract_image(response)
            if img:
                img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                img.save(output_path, "PNG")
                return True

            if attempt == 0:
                print(f"    No image in response, retrying in 10s...")
                time.sleep(10)
                continue
            else:
                print(f"    No image in response after retry")
                return False

        except Exception as e:
            if attempt == 0:
                print(f"    Error: {e}, retrying in 10s...")
                time.sleep(10)
                continue
            else:
                print(f"    Error after retry: {e}")
                return False

    return False


def generate_image(prompt, reference_image_path, output_path):
    """Generate a card background using a reference image and prompt.

    Args:
        prompt: Text prompt for the generation.
        reference_image_path: Path to the reference style image.
        output_path: Where to save the generated image.

    Returns:
        True on success, False on failure.
    """
    client = _get_client()

    with open(reference_image_path, "rb") as f:
        ref_bytes = f.read()
    ref_image = types.Part.from_bytes(data=ref_bytes, mime_type="image/png")

    for attempt in range(2):
        _rate_limit()
        try:
            response = client.models.generate_content(
                model=BG_MODEL,
                contents=[ref_image, prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            img = _extract_image(response)
            if img:
                img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                img.save(output_path, "PNG")
                return True

            if attempt == 0:
                print(f"    No image in response, retrying in 10s...")
                time.sleep(10)
                continue
            else:
                print(f"    No image in response after retry")
                return False

        except Exception as e:
            if attempt == 0:
                print(f"    Error: {e}, retrying in 10s...")
                time.sleep(10)
                continue
            else:
                print(f"    Error after retry: {e}")
                return False

    return False


def touchup_image(input_path, prompt, output_path, input_image=None):
    """Touch up a card image using Gemini editing.

    Args:
        input_path: Path to the card image to edit (used if input_image is None).
        prompt: Touchup instructions.
        output_path: Where to save the result.
        input_image: Optional pre-loaded PIL Image (e.g., with splotch hints applied).

    Returns:
        True on success, False on failure.
    """
    client = _get_client()

    card_img = input_image if input_image is not None else Image.open(input_path)
    img_buf = BytesIO()
    card_img.save(img_buf, format="PNG")
    img_bytes = img_buf.getvalue()

    for attempt in range(2):
        _rate_limit()
        try:
            response = client.models.generate_content(
                model=TOUCHUP_MODEL,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                    thinking_config=types.ThinkingConfig(thinking_budget=8192),
                ),
            )

            img = _extract_image(response)
            if img:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                img.save(output_path, "PNG")
                return True

            if attempt == 0:
                print(f"    No image in response, retrying in 10s...")
                time.sleep(10)
                continue
            else:
                print(f"    No image in response after retry")
                return False

        except Exception as e:
            if attempt == 0:
                print(f"    Error: {e}, retrying in 10s...")
                time.sleep(10)
                continue
            else:
                print(f"    Error after retry: {e}")
                return False

    return False
