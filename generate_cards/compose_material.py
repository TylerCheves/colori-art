"""Material card composition -- overlay ability icons, material types, and title onto backgrounds.

Each material card has:
  - Top-left: ability icons (discard -> arrow -> action) with optional multiplier
  - Bottom-left: material type icons + optional color pip
  - Top-right: card title in Cochin Italic with warm brown glow

Backgrounds are warm parchment-toned watercolor. Three base backgrounds
(ceramic, painting, textile) are shared across all 18 material cards.
"""

import os
from PIL import Image

from .card_data import ICON_DIR, PIG_DIR, BG_DIR, BASE_BG_DIR, ARTWORK_DIR, COMPOSED_DIR
from .rendering import (
    W, H, EDGE, PAD, GAP_H, GAP_V,
    H_TOP, H_ARROW, H_WORK, H_PIG,
    load_icon, paste_icon, get_font,
    draw_text_with_glow, draw_title_right_aligned,
    composite_artwork_on_base, COMPOSITE_PARAMS,
)

# Material type -> icon filename
MAT_ICON = {
    "ceramic": "ceramics.png",
    "painting": "painting.png",
    "textile": "textile.png",
}

# Color pip -> pigment filename
PIP_PIGMENT = {
    "red": "red-pigment.png",
    "yellow": "yellow-pigment.png",
    "blue": "blue-pigment.png",
}


def get_icon_bounds(card):
    """Compute icon region bounding boxes for splotch hint placement."""
    ic_dis = load_icon(f"{ICON_DIR}/discard.png", H_TOP)
    ic_arr_h = load_icon(f"{ICON_DIR}/arrow.png", H_ARROW)

    ability = card["ability"]
    if ability == "sell":
        ic_action = load_icon(f"{ICON_DIR}/project.png", H_TOP)
    elif ability in ("workshop4", "workshop3", "workshop2"):
        ic_action = load_icon(f"{ICON_DIR}/workshop.png", int(H_TOP * 0.85))
    else:
        ic_action = load_icon(f"{ICON_DIR}/project.png", H_TOP)

    top_cw = ic_dis.width + GAP_H + ic_arr_h.width + GAP_H + ic_action.width
    top_ch = max(ic_dis.height, ic_arr_h.height, ic_action.height)
    tb = (EDGE, EDGE, EDGE + top_cw + PAD * 2, EDGE + top_ch + PAD * 2)

    ic_wrk = load_icon(f"{ICON_DIR}/workshop.png", H_WORK)
    ic_arr_d = load_icon(f"{ICON_DIR}/arrow.png", H_ARROW)
    ic_arr_d = ic_arr_d.rotate(-90, expand=True, resample=Image.LANCZOS)

    mat_icons = [load_icon(f"{ICON_DIR}/{MAT_ICON[mt]}", H_PIG) for mt in card["material_types"]]
    pip_icon = None
    if card.get("color_pip"):
        pip_icon = load_icon(f"{PIG_DIR}/{PIP_PIGMENT[card['color_pip']]}", H_PIG)

    all_output_icons = mat_icons + ([pip_icon] if pip_icon else [])
    bot_cw = max(ic_wrk.width, ic_arr_d.width, max(ic.width for ic in all_output_icons))
    bot_ch = ic_wrk.height + GAP_V + ic_arr_d.height + GAP_V
    for ic in all_output_icons:
        bot_ch += ic.height + GAP_V

    by = H - EDGE - bot_ch - PAD * 2
    bb = (EDGE, by, EDGE + bot_cw + PAD * 2, by + bot_ch + PAD * 2)

    return [tb, bb]


def compose(card):
    """Compose a material card from background + icons + title.

    Args:
        card: Dict with name, title, material_types, ability, color_pip, bg_type.

    Returns:
        PIL Image (RGBA) of the composed card, or None if background missing.
    """
    # Try layered compositing: base texture + artwork vignette
    base_path = BASE_BG_DIR / "material.png"
    artwork_path = ARTWORK_DIR / "material" / f"{card['bg_type']}.png"

    if os.path.exists(base_path) and os.path.exists(artwork_path):
        base = Image.open(base_path).resize((W, H), Image.LANCZOS).convert("RGBA")
        artwork = Image.open(artwork_path).convert("RGBA")
        c = composite_artwork_on_base(base, artwork, **COMPOSITE_PARAMS["material"])
    else:
        # Fallback to old single-background approach
        bg_path = os.path.join(BG_DIR / "materials", f"{card['bg_type']}.png")
        if not os.path.exists(bg_path):
            return None
        c = Image.open(bg_path).resize((W, H), Image.LANCZOS).convert("RGBA")

    # ── Load top-left ability icons ──────────────────────────────────────
    ic_dis = load_icon(f"{ICON_DIR}/discard.png", H_TOP)
    ic_arr_h = load_icon(f"{ICON_DIR}/arrow.png", H_ARROW)

    ability = card["ability"]
    if ability == "sell":
        ic_action = load_icon(f"{ICON_DIR}/project.png", H_TOP)
        multiplier = None
    elif ability == "workshop4":
        ic_action = load_icon(f"{ICON_DIR}/workshop.png", int(H_TOP * 0.85))
        multiplier = "4"
    elif ability == "workshop3":
        ic_action = load_icon(f"{ICON_DIR}/workshop.png", int(H_TOP * 0.85))
        multiplier = "3"
    elif ability == "workshop2":
        ic_action = load_icon(f"{ICON_DIR}/workshop.png", int(H_TOP * 0.85))
        multiplier = "2"
    else:
        ic_action = load_icon(f"{ICON_DIR}/project.png", H_TOP)
        multiplier = None

    mult_font = get_font("georgia-bold", 52)

    # ── Compute top-left bounding box ────────────────────────────────────
    top_cw = ic_dis.width + GAP_H + ic_arr_h.width + GAP_H + ic_action.width
    top_ch = max(ic_dis.height, ic_arr_h.height, ic_action.height)
    tb = (EDGE, EDGE, EDGE + top_cw + PAD * 2, EDGE + top_ch + PAD * 2)

    # ── Load bottom-left icons: workshop -> arrow -> materials + pip ─────
    ic_wrk = load_icon(f"{ICON_DIR}/workshop.png", H_WORK)
    ic_arr_d = load_icon(f"{ICON_DIR}/arrow.png", H_ARROW)
    ic_arr_d = ic_arr_d.rotate(-90, expand=True, resample=Image.LANCZOS)

    mat_icons = [
        load_icon(f"{ICON_DIR}/{MAT_ICON[mt]}", H_PIG)
        for mt in card["material_types"]
    ]
    pip_icon = None
    if card.get("color_pip"):
        pip_icon = load_icon(f"{PIG_DIR}/{PIP_PIGMENT[card['color_pip']]}", H_PIG)

    # Bottom column: [workshop] [down arrow] [mat1] [mat2] ... [pip]
    all_output_icons = mat_icons + ([pip_icon] if pip_icon else [])
    bot_cw = max(ic_wrk.width, ic_arr_d.width, max(ic.width for ic in all_output_icons))
    bot_ch = ic_wrk.height + GAP_V + ic_arr_d.height + GAP_V
    for ic in all_output_icons:
        bot_ch += ic.height + GAP_V

    by = H - EDGE - bot_ch - PAD * 2
    bb = (EDGE, by, EDGE + bot_cw + PAD * 2, by + bot_ch + PAD * 2)

    # ── Place top-left icons ─────────────────────────────────────────────
    cx = EDGE + PAD
    cy_base = EDGE + PAD

    c = paste_icon(c, ic_dis, (cx, cy_base + (top_ch - ic_dis.height) // 2))
    cx += ic_dis.width + GAP_H

    c = paste_icon(c, ic_arr_h, (cx, cy_base + (top_ch - ic_arr_h.height) // 2))
    cx += ic_arr_h.width + GAP_H

    # Nudge action icon when multiplier badge sits above-left (workshop/mix)
    # No offset for draw2 (text centered on card) or no-multiplier abilities
    needs_badge_offset = multiplier and ability not in ("draw2", "destroy1")
    action_offset_x = 22 if needs_badge_offset else 0
    action_offset_y = 16 if needs_badge_offset else 0
    action_x = cx + action_offset_x
    action_y = cy_base + (top_ch - ic_action.height) // 2 + action_offset_y
    c = paste_icon(c, ic_action, (action_x, action_y))

    if multiplier:
        from .rendering import tsize, draw_text
        mw, mh = tsize(multiplier, mult_font)
        if ability == "draw2":
            # Center text on the card icon, no glow
            mx = action_x + (ic_action.width - mw) // 2
            my = action_y + (ic_action.height - mh) // 2
            c = draw_text(c, (mx, my), multiplier, mult_font,
                          fill=(65, 48, 28, 255))
        else:
            # Badge above-left of the action icon
            mx = action_x - 18
            my = action_y - 42
            c = draw_text(c, (mx, my), multiplier, mult_font,
                          fill=(65, 48, 28, 255))

    # ── Place bottom-left icons: workshop -> arrow -> outputs ────────────
    cy = by + PAD

    ix = EDGE + PAD + (bot_cw - ic_wrk.width) // 2
    c = paste_icon(c, ic_wrk, (ix, cy))
    cy += ic_wrk.height + GAP_V

    ix = EDGE + PAD + (bot_cw - ic_arr_d.width) // 2
    c = paste_icon(c, ic_arr_d, (ix, cy))
    cy += ic_arr_d.height + GAP_V

    for ic in all_output_icons:
        ix = EDGE + PAD + (bot_cw - ic.width) // 2
        c = paste_icon(c, ic, (ix, cy))
        cy += ic.height + GAP_V

    # ── Title (top-right, warm brown) ────────────────────────────────────
    title = card["title"]
    title_size = 48 if len(title) > 14 else 58 if len(title) > 10 else 72
    title_font = get_font("cochin-italic", title_size)
    c = draw_title_right_aligned(
        c, title, title_font,
        color=(65, 48, 28, 255),
        glow_color=(240, 225, 200, 160),
        glow_r=6,
    )

    return c


def save(card, output_dir=None):
    """Compose and save a material card.

    Returns:
        True on success, False if background missing.
    """
    if output_dir is None:
        output_dir = COMPOSED_DIR / "material"
    os.makedirs(output_dir, exist_ok=True)

    result = compose(card)
    if result is None:
        return False

    out_path = os.path.join(output_dir, f"{card['name']}.png")
    result.convert("RGB").save(out_path, "PNG")
    return True
