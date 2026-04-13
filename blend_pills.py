"""Blend pill boxes in cinnabar-v2 using Nano Banana 2."""

import os
import sys
import time
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

API_KEY = os.environ.get("GOOGLE_API_KEY")
MODEL = "nano-banana-pro-preview"
INPUT = "new-drafts/cinnabar-v2.png"
OUTPUT_DIR = "new-drafts"

BASE_PROMPT = (
    "This is a card illustration. Edit this image to make the two white rounded-rectangle "
    "pill-shaped boxes (one in the upper-left corner and one in the lower-left corner) look "
    "like they are hand-painted and blended into the surrounding artwork. "
    "Keep them white/cream colored but make them look like part of the original painting "
    "rather than flat digital overlays. "
    "IMPORTANT: Keep the rest of the image EXACTLY the same — the mortar and pestle, the red "
    "cinnabar pigment, the wooden table, the background objects, the 'Cinnabar' text, and all "
    "other details must remain completely unchanged. Only modify the appearance of the two "
    "pill-shaped white boxes."
)

STYLES = [
    (
        "thick-impasto",
        " Make the boxes look like thick impasto paint strokes — raised, textured, "
        "with visible palette knife marks and heavy paint buildup along the edges."
    ),
    (
        "wet-watercolor",
        " Make the boxes look like wet watercolor washes — soft bleeding edges, "
        "translucent layers where the wood grain shows through faintly, with pigment "
        "pooling along the borders."
    ),
    (
        "chalk-pastel",
        " Make the boxes look like chalk or pastel smudges — dusty, slightly grainy "
        "texture with soft powdery edges that feather into the surrounding scene."
    ),
    (
        "ink-wash",
        " Make the boxes look like an ink wash or sumi-e brushstroke — confident, "
        "expressive single-stroke shapes with varying opacity and dry-brush texture "
        "at the edges."
    ),
    (
        "fresco-plaster",
        " Make the boxes look like aged fresco plaster patches — slightly cracked, "
        "with a matte chalky surface and irregular edges that look like old plaster "
        "applied to a wall."
    ),
    (
        "oil-glaze",
        " Make the boxes look like translucent oil paint glazes — smooth, luminous, "
        "with subtle warm undertones and softly blended edges that melt into the "
        "surrounding scene."
    ),
]


def main():
    if not API_KEY:
        print("ERROR: Set GOOGLE_API_KEY environment variable")
        sys.exit(1)

    client = genai.Client(api_key=API_KEY)

    with open(INPUT, "rb") as f:
        img_bytes = f.read()
    img_part = types.Part.from_bytes(data=img_bytes, mime_type="image/png")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for style_name, style_suffix in STYLES:
        prompt = BASE_PROMPT + style_suffix
        print(f"Generating style: {style_name}...")

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
                    out_path = os.path.join(OUTPUT_DIR, f"cinnabar-v2-{style_name}.png")
                    img.save(out_path, "PNG")
                    print(f"  Saved: {out_path}")
                    break
                else:
                    if attempt == 0:
                        print("  No image in response, retrying in 10s...")
                        time.sleep(10)
                    else:
                        print(f"  No image after retry, skipping {style_name}")

            except Exception as e:
                if attempt == 0:
                    print(f"  Error: {e}, retrying in 10s...")
                    time.sleep(10)
                else:
                    print(f"  Error after retry: {e}, skipping {style_name}")

    print("Done!")


if __name__ == "__main__":
    main()
