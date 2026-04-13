"""Dye card composition -- overlay icons and title onto dye backgrounds.

Ports logic from cards/scripts/generate_final_dye.py.

Each dye card has:
  - Top-left: ability icons (discard -> action) with optional multiplier
  - Bottom-left: pigment production (workshop -> pigments), pinned to bottom edge
  - Top-right: card title in Cochin Italic with white glow
"""

import os
from PIL import Image

from .card_data import ICON_DIR, PIG_DIR, BG_DIR, BASE_BG_DIR, ARTWORK_DIR, COMPOSED_DIR
from .rendering import (
    W, H, EDGE, PAD, GAP_H, GAP_V,
    H_TOP, H_ARROW, H_WORK, H_PIG,
    load_icon, paste_icon, get_font,
    draw_text, draw_text_with_glow, draw_title_right_aligned,
    composite_artwork_on_base, COMPOSITE_PARAMS,
)

# Set of tertiary pigments that render larger
TERTIARY_PIGS = {
    "vermilion-pigment", "amber-pigment", "chartreuse-pigment",
    "teal-pigment", "indigo-pigment", "magenta-pigment",
}


def get_icon_bounds(card):
    """Compute icon region bounding boxes for splotch hint placement."""
    ic_dis = load_icon(f"{ICON_DIR}/discard.png", H_TOP)
    ic_arr_h = load_icon(f"{ICON_DIR}/arrow.png", H_ARROW)
    ic_arr_d = ic_arr_h.rotate(-90, expand=True, resample=Image.LANCZOS)

    ability = card["ability"]
    if ability == "sell":
        ic_action = load_icon(f"{ICON_DIR}/project.png", H_TOP)
    elif ability == "destroyCards":
        ic_action = load_icon(f"{ICON_DIR}/blank-card.png", H_TOP)
    elif ability == "workshop3":
        ic_action = load_icon(f"{ICON_DIR}/workshop.png", int(H_TOP * 0.85))
    elif ability == "mix2":
        ic_action = load_icon(f"{ICON_DIR}/mix.png", int(H_TOP * 0.85))
    else:
        ic_action = load_icon(f"{ICON_DIR}/project.png", H_TOP)

    ic_wrk = load_icon(f"{ICON_DIR}/workshop.png", H_WORK)
    pig_icons = [
        load_icon(f"{PIG_DIR}/{p}.png", int(H_PIG * 1.5) if p in TERTIARY_PIGS else H_PIG)
        for p in card["pigments"]
    ]

    top_cw = ic_dis.width + GAP_H + ic_arr_h.width + GAP_H + ic_action.width
    top_ch = max(ic_dis.height, ic_arr_h.height, ic_action.height)
    tb = (EDGE, EDGE, EDGE + top_cw + PAD * 2, EDGE + top_ch + PAD * 2)

    bot_cw = max(ic_wrk.width, ic_arr_d.width, max(p.width for p in pig_icons))
    bot_ch = ic_wrk.height + GAP_V + ic_arr_d.height + GAP_V
    for p in pig_icons:
        bot_ch += p.height + GAP_V
    by = H - EDGE - bot_ch - PAD * 2
    bb = (EDGE, by, EDGE + bot_cw + PAD * 2, by + bot_ch + PAD * 2)

    return [tb, bb]


def compose(card):
    """Compose a final dye card image from background + icons + title.

    Args:
        card: Dict with name, title, ability, pigments, color fields.

    Returns:
        PIL Image (RGBA) of the composed card, or None if background missing.
    """
    # Try layered compositing: base texture + artwork vignette
    base_path = BASE_BG_DIR / "dye.png"
    artwork_path = ARTWORK_DIR / "dye" / f"{card['name']}.png"

    if os.path.exists(base_path) and os.path.exists(artwork_path):
        base = Image.open(base_path).resize((W, H), Image.LANCZOS).convert("RGBA")
        artwork = Image.open(artwork_path).convert("RGBA")
        c = composite_artwork_on_base(base, artwork, **COMPOSITE_PARAMS["dye"])
    else:
        # Fallback to old single-background approach
        bg_path = os.path.join(BG_DIR / "dye", f"{card['name']}.png")
        if not os.path.exists(bg_path):
            return None
        c = Image.open(bg_path).resize((W, H), Image.LANCZOS).convert("RGBA")

    # ── Load icons ────────────────────────────────────────────────────────
    ic_dis = load_icon(f"{ICON_DIR}/discard.png", H_TOP)
    ic_arr_h = load_icon(f"{ICON_DIR}/arrow.png", H_ARROW)
    ic_arr_d = ic_arr_h.rotate(-90, expand=True, resample=Image.LANCZOS)

    # Top-left action icon
    ability = card["ability"]
    if ability == "sell":
        ic_action = load_icon(f"{ICON_DIR}/project.png", H_TOP)
        multiplier = None
    elif ability == "destroyCards":
        ic_action = load_icon(f"{ICON_DIR}/blank-card.png", H_TOP)
        ic_arr_up = load_icon(f"{ICON_DIR}/arrow.png", H_ARROW).rotate(
            90, expand=True, resample=Image.LANCZOS
        )
        multiplier = None
    elif ability == "workshop3":
        ic_action = load_icon(f"{ICON_DIR}/workshop.png", int(H_TOP * 0.85))
        multiplier = "3"
    elif ability == "mix2":
        ic_action = load_icon(f"{ICON_DIR}/mix.png", int(H_TOP * 0.85))
        multiplier = "2"
    else:
        ic_action = load_icon(f"{ICON_DIR}/project.png", H_TOP)
        multiplier = None

    # Bottom-left icons
    ic_wrk = load_icon(f"{ICON_DIR}/workshop.png", H_WORK)
    pig_icons = [
        load_icon(f"{PIG_DIR}/{p}.png", int(H_PIG * 1.5) if p in TERTIARY_PIGS else H_PIG)
        for p in card["pigments"]
    ]

    # Multiplier font
    mult_font = get_font("georgia-bold", 52)

    # ── Compute bounding boxes ────────────────────────────────────────────

    # Top row: [discard] [arrow] [action]
    top_cw = ic_dis.width + GAP_H + ic_arr_h.width + GAP_H + ic_action.width
    top_ch = max(ic_dis.height, ic_arr_h.height, ic_action.height)
    tb = (EDGE, EDGE, EDGE + top_cw + PAD * 2, EDGE + top_ch + PAD * 2)

    # Bottom column: [workshop] [arrow_d] [pig1] [pig2] ...  pinned to bottom
    bot_cw = max(ic_wrk.width, ic_arr_d.width, max(p.width for p in pig_icons))
    bot_ch = ic_wrk.height + GAP_V + ic_arr_d.height + GAP_V
    for p in pig_icons:
        bot_ch += p.height + GAP_V
    by = H - EDGE - bot_ch - PAD * 2
    bb = (EDGE, by, EDGE + bot_cw + PAD * 2, by + bot_ch + PAD * 2)

    # ── Place top-left icons ──────────────────────────────────────────────
    cx = EDGE + PAD
    cy_base = EDGE + PAD

    c = paste_icon(c, ic_dis, (cx, cy_base + (top_ch - ic_dis.height) // 2))
    cx += ic_dis.width + GAP_H

    c = paste_icon(c, ic_arr_h, (cx, cy_base + (top_ch - ic_arr_h.height) // 2))
    cx += ic_arr_h.width + GAP_H

    # Nudge action icon right+down when multiplier present to make room
    action_offset_x = 22 if multiplier else 0
    action_offset_y = 16 if multiplier else 0
    action_x = cx + action_offset_x
    action_y = cy_base + (top_ch - ic_action.height) // 2 + action_offset_y
    c = paste_icon(c, ic_action, (action_x, action_y))

    # Upward arrow at top of action icon (destroyCards only)
    if ability == "destroyCards":
        arr_x = action_x + (ic_action.width - ic_arr_up.width) // 2
        arr_y = action_y - ic_arr_up.height // 2
        c = paste_icon(c, ic_arr_up, (arr_x, arr_y))

    if multiplier:
        mx = action_x - 18
        my = action_y - 42
        c = draw_text(c, (mx, my), multiplier, mult_font,
                      fill=(65, 48, 28, 255))

    # ── Place bottom-left icons ───────────────────────────────────────────
    cy = by + PAD

    ix = EDGE + PAD + (bot_cw - ic_wrk.width) // 2
    c = paste_icon(c, ic_wrk, (ix, cy))
    cy += ic_wrk.height + GAP_V

    ix = EDGE + PAD + (bot_cw - ic_arr_d.width) // 2
    c = paste_icon(c, ic_arr_d, (ix, cy))
    cy += ic_arr_d.height + GAP_V

    for pig in pig_icons:
        ix = EDGE + PAD + (bot_cw - pig.width) // 2
        c = paste_icon(c, pig, (ix, cy))
        cy += pig.height + GAP_V

    # ── Title (multi-line, right-aligned) ─────────────────────────────────
    title = card["title"]
    title_size = 58 if len(title) > 10 else 72
    title_font = get_font("cochin-italic", title_size)
    title_color = card.get("color", (48, 72, 102))
    c = draw_title_right_aligned(
        c, title, title_font,
        color=(*title_color, 255),
        glow_color=(255, 255, 255, 100),
        glow_r=6,
    )

    # ── Starter badge (basic dyes only) ──────────────────────────────────
    if card["name"].startswith("basic-"):
        s_font = get_font("cochin-italic", 56)
        sx = W - EDGE - 60
        sy = H - EDGE - 62
        c = draw_text_with_glow(
            c, (sx, sy), "S", s_font,
            fill=(*title_color, 180),
            glow_color=(255, 255, 255, 100),
            glow_r=4,
        )

    return c


def save(card, output_dir=None):
    """Compose and save a dye card.

    Returns:
        True on success, False if background missing.
    """
    if output_dir is None:
        output_dir = COMPOSED_DIR / "dye"
    os.makedirs(output_dir, exist_ok=True)

    result = compose(card)
    if result is None:
        return False

    out_path = os.path.join(output_dir, f"{card['name']}.png")
    result.convert("RGB").save(out_path, "PNG")
    return True
