"""Apply blended-3 style to alum-edited and cinnabar-edited."""

import os
import sys
import time
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

API_KEY = os.environ.get("GOOGLE_API_KEY")
MODEL = "nano-banana-pro-preview"
OUTPUT_DIR = "new-drafts"

CARDS = [
    ("alum-edited", "new-drafts/alum-edited.png", "Alum"),
    ("cinnabar-edited", "new-drafts/cinnabar-edited.png", "Cinnabar"),
]

NUM_VARIANTS = 3


def make_prompt(card_name):
    return (
        "This is a card illustration. Edit this image to make the two white rounded-rectangle "
        "pill-shaped boxes (one in the upper-left corner and one in the lower-left corner) look "
        "like they are hand-painted and blended into the surrounding artwork. They should appear "
        "as if they were brushed onto the surface with visible watercolor brushstrokes, with soft "
        "edges that blend naturally into the surrounding painted scene. Keep them white/cream colored "
        "but make them look like part of the original painting rather than flat digital overlays. "
        f"IMPORTANT: Keep the rest of the image EXACTLY the same — the subject, the '{card_name}' "
        "text, and all other details must remain completely unchanged. Only modify the appearance "
        "of the two pill-shaped white boxes to make them look hand-painted and blended in."
    )


def main():
    if not API_KEY:
        print("ERROR: Set GOOGLE_API_KEY environment variable")
        sys.exit(1)

    client = genai.Client(api_key=API_KEY)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for card_slug, input_path, card_name in CARDS:
        print(f"\n=== {card_name} ===")

        with open(input_path, "rb") as f:
            img_bytes = f.read()
        img_part = types.Part.from_bytes(data=img_bytes, mime_type="image/png")
        prompt = make_prompt(card_name)

        for i in range(1, NUM_VARIANTS + 1):
            print(f"  Generating variant {i}/{NUM_VARIANTS}...")

            for attempt in range(2):
                time.sleep(5)
                try:
                    response = client.models.generate_content(
                        model=MODEL,
                        contents=[img_part, prompt],
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
                        img = img.resize((750, 1050), Image.LANCZOS)
                        out_path = os.path.join(OUTPUT_DIR, f"{card_slug}-blended-{i}.png")
                        img.save(out_path, "PNG")
                        print(f"    Saved: {out_path}")
                        break
                    else:
                        if attempt == 0:
                            print("    No image in response, retrying in 10s...")
                            time.sleep(10)
                        else:
                            print(f"    No image after retry, skipping variant {i}")

                except Exception as e:
                    if attempt == 0:
                        print(f"    Error: {e}, retrying in 10s...")
                        time.sleep(10)
                    else:
                        print(f"    Error after retry: {e}, skipping variant {i}")

    print("\nDone!")


if __name__ == "__main__":
    main()
