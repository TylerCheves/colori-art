"""Generate new cinnabar drafts: full-bleed art with light tan background."""

import os
import sys
import time
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

API_KEY = os.environ.get("GOOGLE_API_KEY")
MODEL = "nano-banana-pro-preview"
WIDTH, HEIGHT = 750, 1050

REF_IMAGE = "new-drafts/full-cinnabar.jpg"
LIGHT_TAN_REF = "new-drafts/Pigment Card Cinnabar Light Tan Borders.jpg"
OUTPUT_DIR = "new-drafts"

PROMPT = (
    "Using the attached reference images as your style guide, create a full-bleed "
    "illustration that fills the entire canvas edge to edge with no borders or margins. "
    "The scene depicts a stone mortar and pestle on a wooden workbench in a Renaissance "
    "Venice dye workshop. The mortar is filled with vibrant red cinnabar pigment powder. "
    "Red pigment is scattered and spilled across the wooden planks. In the background, "
    "a wrapped bundle and small clay pots sit on the table. "
    "IMPORTANT: The overall background tone and lighting should be LIGHT — use a warm, "
    "light tan/cream/parchment color palette for the background areas, similar to aged "
    "parchment paper. The scene should feel bright and warmly lit, not dark or moody. "
    "The wooden table should be light-toned wood. The art fills the full width and full "
    "height of the image with no white space, no borders, no margins. "
    "Style: rich painterly illustration with visible brushstrokes, Renaissance workshop "
    "atmosphere, warm earth tones with bright red cinnabar as the focal color."
)

NUM_DRAFTS = 3


def main():
    if not API_KEY:
        print("ERROR: Set GOOGLE_API_KEY environment variable")
        sys.exit(1)

    client = genai.Client(api_key=API_KEY)

    # Load both reference images
    with open(REF_IMAGE, "rb") as f:
        ref_bytes = f.read()
    ref_part = types.Part.from_bytes(data=ref_bytes, mime_type="image/jpeg")

    with open(LIGHT_TAN_REF, "rb") as f:
        tan_bytes = f.read()
    tan_part = types.Part.from_bytes(data=tan_bytes, mime_type="image/jpeg")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i in range(1, NUM_DRAFTS + 1):
        print(f"Generating draft {i}/{NUM_DRAFTS}...")

        for attempt in range(2):
            time.sleep(5)  # rate limit
            try:
                response = client.models.generate_content(
                    model=MODEL,
                    contents=[ref_part, tan_part, PROMPT],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"],
                    ),
                )

                img = None
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        mime = getattr(part.inline_data, "mime_type", "")
                        if mime.startswith("image/") or part.inline_data.data:
                            img = Image.open(BytesIO(part.inline_data.data))
                            break

                if img:
                    img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
                    out_path = os.path.join(OUTPUT_DIR, f"cinnabar-light-fullbleed-{i}.png")
                    img.save(out_path, "PNG")
                    print(f"  Saved: {out_path}")
                    break
                else:
                    if attempt == 0:
                        print(f"  No image in response, retrying in 10s...")
                        time.sleep(10)
                    else:
                        print(f"  No image after retry, skipping draft {i}")

            except Exception as e:
                if attempt == 0:
                    print(f"  Error: {e}, retrying in 10s...")
                    time.sleep(10)
                else:
                    print(f"  Error after retry: {e}, skipping draft {i}")

    print("Done!")


if __name__ == "__main__":
    main()
