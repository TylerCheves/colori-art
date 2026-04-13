"""Enhance dye card colors to better represent each dye's characteristic color.

Reads composed dye cards, applies color-targeted saturation boost and a soft
color wash to the artwork and title only (icons are preserved as-is), then
saves to generate_cards/enhanced/dye/.

Usage:
    python -m generate_cards.enhance_dye_colors
    python -m generate_cards.enhance_dye_colors --cards weld basic-yellow
    python -m generate_cards.enhance_dye_colors --strength 0.7
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from .card_data import DYE_CARDS, COMPOSED_DIR, PKG_DIR
from .compose_dye import get_icon_bounds

ENHANCED_DIR = PKG_DIR / "enhanced" / "dye"

# Extra padding around icon bounding boxes to ensure clean edges
ICON_MARGIN = 12


def soft_light_blend(base: np.ndarray, overlay: np.ndarray) -> np.ndarray:
    """Photoshop-style soft light blend on float arrays in [0, 1]."""
    mask = base <= 0.5
    result = np.where(
        mask,
        2 * base * overlay + base * base * (1 - 2 * overlay),
        2 * base * (1 - overlay) + np.sqrt(base) * (2 * overlay - 1),
    )
    return np.clip(result, 0, 1)


def make_icon_mask(card, w, h):
    """Create a mask that is 0 over icon regions and 255 elsewhere.

    Uses get_icon_bounds() to find the top-left and bottom-left icon
    bounding boxes, then blocks them out with soft feathered edges.
    """
    mask = Image.new("L", (w, h), 255)
    draw = ImageDraw.Draw(mask)

    for (x0, y0, x1, y1) in get_icon_bounds(card):
        draw.rectangle(
            [x0 - ICON_MARGIN, y0 - ICON_MARGIN,
             x1 + ICON_MARGIN, y1 + ICON_MARGIN],
            fill=0,
        )

    # Feather the edges so the transition isn't jarring
    mask = mask.filter(ImageFilter.GaussianBlur(radius=10))
    return mask


def enhance_card(img: Image.Image, card: dict, strength: float = 0.45) -> Image.Image:
    """Apply color enhancement to a dye card's artwork and title only.

    1. Boost saturation to make existing colors more vivid.
    2. Apply a soft-light color wash using the card's dye color.
    3. Slight contrast bump.
    4. Restore original icon regions untouched.

    Args:
        img: Source card image (RGB or RGBA).
        card: Card dict with 'color', 'pigments', etc.
        strength: Color wash intensity (0.0 = none, 1.0 = full).
    """
    original = img.convert("RGB")
    w, h = original.size
    color = card["color"]

    # --- Step 1: Saturation boost ---
    enhanced = ImageEnhance.Color(original).enhance(1.5)

    # --- Step 2: Soft-light color wash ---
    overlay = Image.new("RGB", (w, h), color)

    # Radial vignette: strongest in center, fades toward edges
    cx, cy = w / 2, h / 2
    y_coords, x_coords = np.mgrid[0:h, 0:w]
    dist = np.sqrt(((x_coords - cx) / (w * 0.45)) ** 2 +
                   ((y_coords - cy) / (h * 0.45)) ** 2)
    vignette = np.clip(1.0 - dist, 0, 1) ** 0.8

    # Reduce wash on very bright pixels (white vignette border)
    arr = np.array(enhanced).astype(np.float32) / 255.0
    brightness = arr.mean(axis=2)
    bright_mask = np.clip(1.0 - ((brightness - 0.85) / 0.15), 0, 1)
    combined_mask = (vignette * bright_mask * strength * 255).astype(np.uint8)

    # Soft-light blend
    overlay_arr = np.array(overlay).astype(np.float32) / 255.0
    blended = soft_light_blend(arr, overlay_arr)
    blended_img = Image.fromarray((blended * 255).astype(np.uint8))

    # Composite wash onto enhanced image
    wash_mask = Image.fromarray(combined_mask)
    wash_mask = wash_mask.filter(ImageFilter.GaussianBlur(radius=20))
    result = Image.composite(blended_img, enhanced, wash_mask)

    # --- Step 3: Slight contrast bump ---
    result = ImageEnhance.Contrast(result).enhance(1.08)

    # --- Step 4: Restore original icon regions ---
    icon_mask = make_icon_mask(card, w, h)
    icon_restore_mask = Image.eval(icon_mask, lambda x: 255 - x)
    result.paste(original, mask=icon_restore_mask)

    return result


def main():
    parser = argparse.ArgumentParser(description="Enhance dye card colors")
    parser.add_argument("--cards", nargs="*", help="Specific card names to process")
    parser.add_argument("--strength", type=float, default=0.45,
                        help="Color wash strength (0.0-1.0, default 0.45)")
    args = parser.parse_args()

    os.makedirs(ENHANCED_DIR, exist_ok=True)

    cards = DYE_CARDS
    if args.cards:
        name_set = set(args.cards)
        cards = [c for c in cards if c["name"] in name_set]
        if not cards:
            print(f"No matching cards found for: {args.cards}")
            sys.exit(1)

    source_dir = COMPOSED_DIR / "dye"
    processed = 0
    skipped = 0

    for card in cards:
        name = card["name"]
        color = card["color"]
        src_path = source_dir / f"{name}.png"

        if not src_path.exists():
            print(f"  SKIP {name} (no composed image)")
            skipped += 1
            continue

        img = Image.open(src_path)
        result = enhance_card(img, card, strength=args.strength)
        out_path = ENHANCED_DIR / f"{name}.png"
        result.save(out_path, "PNG")
        print(f"  OK   {name} -> enhanced/ (color={color})")
        processed += 1

    print(f"\nDone: {processed} enhanced, {skipped} skipped")
    print(f"Output: {ENHANCED_DIR}")


if __name__ == "__main__":
    main()
