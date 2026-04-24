"""Buyer/project card composition -- overlay pigment icons and coin cost onto gold backgrounds.

Ports logic from cards/scripts/generate_final_project.py.

Each buyer card has:
  - Top-center: pigment requirement icons + material icon
  - Bottom-center: coin icons showing star cost (textile=2, ceramic=3, painting=4)
"""

import os
from PIL import Image

from .card_data import (
    ICON_DIR, PIG_DIR, BG_DIR, COMPOSED_DIR,
    MATERIAL_ICON, BUYER_COST, parse_buyer_name,
)
from .rendering import (
    W, H, EDGE, PAD, H_TOP, H_COIN,
    load_icon, find_background_image,
)

GAP_H = 34
GAP_COIN = 8


def get_icon_bounds(name):
    """Compute icon region bounding boxes for splotch hint placement."""
    colors, material = parse_buyer_name(name)
    cost = BUYER_COST[material]

    top_icons = []
    for clr in colors:
        top_icons.append(load_icon(f"{PIG_DIR}/{clr}-pigment.png", H_TOP))
    top_icons.append(load_icon(f"{ICON_DIR}/{MATERIAL_ICON[material]}", H_TOP))

    top_cw = sum(ic.width for ic in top_icons) + GAP_H * (len(top_icons) - 1)
    top_ch = max(ic.height for ic in top_icons)
    top_x_start = (W - top_cw) // 2
    top_y = EDGE + 85
    tb = (top_x_start - PAD, top_y, top_x_start + top_cw + PAD, top_y + top_ch + PAD * 2)

    ic_coin = load_icon(f"{ICON_DIR}/coin.png", H_COIN)
    total_coins_w = cost * ic_coin.width + (cost - 1) * GAP_COIN
    coin_x_start = (W - total_coins_w) // 2
    coin_y = H - EDGE - PAD - ic_coin.height - 30
    bb = (coin_x_start - PAD, coin_y - PAD,
          coin_x_start + total_coins_w + PAD, coin_y + ic_coin.height + PAD)

    return [tb, bb]


def compose(name):
    """Compose a final buyer card image from background + icons.

    Args:
        name: Card name string (e.g., 'vermilion-textile').

    Returns:
        PIL Image (RGBA) of the composed card, or None if background missing.
    """
    bg_path = find_background_image(BG_DIR / "project", name)
    if bg_path is None:
        return None

    bg = Image.open(bg_path).resize((W, H), Image.LANCZOS).convert("RGBA")
    c = bg.copy()

    colors, material = parse_buyer_name(name)
    cost = BUYER_COST[material]

    # ── Top-center: pigment icons + material icon ─────────────────────────
    top_icons = []
    for clr in colors:
        top_icons.append(load_icon(f"{PIG_DIR}/{clr}-pigment.png", H_TOP))
    top_icons.append(load_icon(f"{ICON_DIR}/{MATERIAL_ICON[material]}", H_TOP))

    top_cw = sum(ic.width for ic in top_icons) + GAP_H * (len(top_icons) - 1)
    top_ch = max(ic.height for ic in top_icons)
    top_x_start = (W - top_cw) // 2
    top_y = EDGE + 85
    tb = (top_x_start - PAD, top_y, top_x_start + top_cw + PAD, top_y + top_ch + PAD * 2)

    # ── Bottom-center: coin icons ────────────────────────────────────────
    ic_coin = load_icon(f"{ICON_DIR}/coin.png", H_COIN)
    total_coins_w = cost * ic_coin.width + (cost - 1) * GAP_COIN
    coin_x_start = (W - total_coins_w) // 2
    coin_y = H - EDGE - PAD - ic_coin.height - 30

    # Place icons
    cx = top_x_start
    cy_base = top_y + PAD
    for ic in top_icons:
        c.paste(ic, (cx, cy_base + (top_ch - ic.height) // 2), ic)
        cx += ic.width + GAP_H

    # Place coins
    cx = coin_x_start
    for _ in range(cost):
        c.paste(ic_coin, (cx, coin_y), ic_coin)
        cx += ic_coin.width + GAP_COIN

    return c


def save(name, output_dir=None):
    """Compose and save a buyer card.

    Returns:
        True on success, False if background missing.
    """
    if output_dir is None:
        output_dir = COMPOSED_DIR / "buyer"
    os.makedirs(output_dir, exist_ok=True)

    result = compose(name)
    if result is None:
        return False

    out_path = os.path.join(output_dir, f"{name}.png")
    result.convert("RGB").save(out_path, "PNG")
    return True
