"""Action card composition -- overlay icons and title onto dark action backgrounds.

Ports logic from cards/scripts/generate_final_action.py.

Each action card has:
  - Top-left: discard icons (discard -> discard[workshop badge])
  - Top-right: card title in white, Cochin Italic
  - Bottom-left: card-specific effect (workshop -> variable content)
"""

import os
from PIL import Image, ImageDraw

from .card_data import ICON_DIR, PIG_DIR, BG_DIR, BASE_BG_DIR, ARTWORK_DIR, COMPOSED_DIR
from .rendering import (
    W, H, EDGE, PAD, GAP_H, GAP_V,
    H_TOP, H_ARROW, H_WORK, H_PIG, H_COIN,
    load_icon, paste_icon, get_font, tsize, cloud_panel,
    draw_text, draw_text_with_glow, draw_title_right_aligned,
    composite_artwork_on_base_opaque, COMPOSITE_PARAMS,
)


# ── Bottom-left content builders ─────────────────────────────────────────────

def _build_bottom_content(card):
    """Returns (content_width, content_height, list_of_(icon, rel_x, rel_y), or_positions)
    for everything below the workshop+arrow in the bottom panel."""
    bottom = card["bottom"]
    btype = bottom["type"]
    or_font = get_font("cochin-italic", 36)

    if btype == "coin":
        ic = load_icon(f"{ICON_DIR}/coin.png", H_COIN)
        return ic.width, ic.height, [(ic, 0, 0)], []

    elif btype == "pigment_choice":
        pigs = [load_icon(f"{PIG_DIR}/{p}.png", H_PIG) for p in bottom["pigments"]]
        max_pw = max(p.width for p in pigs)
        or_w, or_h = tsize("or", or_font)
        items = []
        or_positions = []
        cy = 0
        for i, pig in enumerate(pigs):
            items.append((pig, (max_pw - pig.width) // 2, cy))
            cy += pig.height + GAP_V
            if i < len(pigs) - 1:
                or_positions.append(((max_pw - or_w) // 2, cy))
                cy += or_h + GAP_V
        total_w = max(max_pw, or_w)
        return total_w, cy - GAP_V, items, or_positions

    elif btype == "draw_cards":
        ic_card = load_icon(f"{ICON_DIR}/blank-card.png", 100)
        num_font = get_font("georgia-bold", 42)
        nw, nh = tsize(bottom["count"], num_font)
        overlay = Image.new("RGBA", ic_card.size, (0, 0, 0, 0))
        nx = (ic_card.width - nw) // 2
        ny = (ic_card.height - nh) // 2
        ImageDraw.Draw(overlay).text((nx, ny), bottom["count"], font=num_font,
                                      fill=(80, 55, 35, 255))
        ic_card = Image.alpha_composite(ic_card, overlay)
        return ic_card.width, ic_card.height, [(ic_card, 0, 0)], []

    elif btype in ("materials", "workshop_picks"):
        ic_wrk2 = load_icon(f"{ICON_DIR}/workshop.png", H_WORK)
        items = [(ic_wrk2, 0, 0)]
        return ic_wrk2.width, ic_wrk2.height, items, []

    elif btype == "mix":
        ic_mix = load_icon(f"{ICON_DIR}/mix.png", int(H_WORK * 0.85))
        items = [(ic_mix, 0, 0)]
        return ic_mix.width, ic_mix.height, items, []

    elif btype == "swap":
        bottle_h = 78
        arrow_h = 30
        ic_bot1 = load_icon(f"{ICON_DIR}/empty-bottle.png", bottle_h)
        ic_bot2 = load_icon(f"{ICON_DIR}/empty-bottle.png", bottle_h)
        ic_arr_r = load_icon(f"{ICON_DIR}/arrow.png", arrow_h)
        ic_arr_l = ic_arr_r.transpose(Image.FLIP_LEFT_RIGHT)

        arrow_gap = 4
        arrows_h = ic_arr_r.height + arrow_gap + ic_arr_l.height
        arrows_w = max(ic_arr_r.width, ic_arr_l.width)
        mid_gap = 6

        total_w = ic_bot1.width + mid_gap + arrows_w + mid_gap + ic_bot2.width
        total_h = max(bottle_h, arrows_h)

        items = []
        # Left bottle
        items.append((ic_bot1, 0, (total_h - bottle_h) // 2))
        # Right arrow
        ax = ic_bot1.width + mid_gap
        arrows_top = (total_h - arrows_h) // 2
        items.append((ic_arr_r, ax + (arrows_w - ic_arr_r.width) // 2, arrows_top))
        # Left arrow
        items.append((ic_arr_l, ax + (arrows_w - ic_arr_l.width) // 2,
                       arrows_top + ic_arr_r.height + arrow_gap))
        # Right bottle
        items.append((ic_bot2, ax + arrows_w + mid_gap, (total_h - bottle_h) // 2))

        return total_w, total_h, items, []

    return 0, 0, [], []


# ── Icon bounds ──────────────────────────────────────────────────────────────

def get_icon_bounds(card):
    """Compute icon region bounding boxes for splotch hint placement."""
    ic_dis1 = load_icon(f"{ICON_DIR}/discard.png", H_TOP)
    ic_arr_h = load_icon(f"{ICON_DIR}/arrow.png", H_ARROW)

    ability = card.get("ability", "destroyCards")
    if ability == "destroyCards":
        ic_action = load_icon(f"{ICON_DIR}/blank-card.png", H_TOP)
    elif ability == "draw2":
        ic_action = load_icon(f"{ICON_DIR}/blank-card.png", H_TOP)
    elif ability == "sell":
        ic_action = load_icon(f"{ICON_DIR}/project.png", H_TOP)
    else:
        ic_action = load_icon(f"{ICON_DIR}/blank-card.png", H_TOP)

    top_cw = ic_dis1.width + GAP_H + ic_arr_h.width + GAP_H + ic_action.width
    top_ch = max(ic_dis1.height, ic_arr_h.height, ic_action.height)
    tb = (EDGE, EDGE, EDGE + top_cw + PAD * 2, EDGE + top_ch + PAD * 2)

    ic_wrk = load_icon(f"{ICON_DIR}/workshop.png", H_WORK)
    ic_arr_d = load_icon(f"{ICON_DIR}/arrow.png", H_ARROW).rotate(
        -90, expand=True, resample=Image.LANCZOS
    )
    content_w, content_h, _, _ = _build_bottom_content(card)

    bot_cw = max(ic_wrk.width, ic_arr_d.width, content_w)
    bot_ch = ic_wrk.height + GAP_V + ic_arr_d.height + GAP_V + content_h
    by = H - EDGE - bot_ch - PAD * 2
    bb = (EDGE, by, EDGE + bot_cw + PAD * 2, by + bot_ch + PAD * 2)

    return [tb, bb]


# ── Composition ──────────────────────────────────────────────────────────────

def compose(card):
    """Compose a final action card image from background + icons + title.

    Args:
        card: Dict with name, title, bottom fields.

    Returns:
        PIL Image (RGBA) of the composed card, or None if background missing.
    """
    # Try layered compositing: base texture + artwork vignette
    base_path = BASE_BG_DIR / "action.png"
    artwork_path = ARTWORK_DIR / "action" / f"{card['name']}.png"

    if os.path.exists(base_path) and os.path.exists(artwork_path):
        base = Image.open(base_path).resize((W, H), Image.LANCZOS).convert("RGBA")
        artwork = Image.open(artwork_path).convert("RGBA")
        c = composite_artwork_on_base_opaque(base, artwork, **COMPOSITE_PARAMS["action"])
    else:
        # Fallback to old single-background approach
        bg_path = os.path.join(BG_DIR / "action", f"{card['name']}.png")
        if not os.path.exists(bg_path):
            return None
        c = Image.open(bg_path).resize((W, H), Image.LANCZOS).convert("RGBA")

    # ── Load top-left icons ───────────────────────────────────────────────
    ic_dis1 = load_icon(f"{ICON_DIR}/discard.png", H_TOP)
    ic_arr_h = load_icon(f"{ICON_DIR}/arrow.png", H_ARROW)

    ability = card.get("ability", "destroyCards")
    mult_font = get_font("georgia-bold", 52)

    if ability == "destroyCards":
        ic_action = load_icon(f"{ICON_DIR}/blank-card.png", H_TOP)
        ic_arr_up = load_icon(f"{ICON_DIR}/arrow.png", H_ARROW).rotate(
            90, expand=True, resample=Image.LANCZOS
        )
        top_multiplier = None
    elif ability == "draw2":
        ic_action = load_icon(f"{ICON_DIR}/blank-card.png", H_TOP)
        top_multiplier = "+2"
    elif ability == "sell":
        ic_action = load_icon(f"{ICON_DIR}/project.png", H_TOP)
        top_multiplier = None
    else:
        ic_action = load_icon(f"{ICON_DIR}/blank-card.png", H_TOP)
        top_multiplier = None

    # ── Compute bounding box for top-left ─────────────────────────────────
    top_cw = ic_dis1.width + GAP_H + ic_arr_h.width + GAP_H + ic_action.width
    top_ch = max(ic_dis1.height, ic_arr_h.height, ic_action.height)
    tb = (EDGE, EDGE, EDGE + top_cw + PAD * 2, EDGE + top_ch + PAD * 2)

    # ── Load bottom-left icons ────────────────────────────────────────────
    ic_wrk = load_icon(f"{ICON_DIR}/workshop.png", H_WORK)
    ic_arr_d = load_icon(f"{ICON_DIR}/arrow.png", H_ARROW).rotate(
        -90, expand=True, resample=Image.LANCZOS
    )
    content_w, content_h, content_items, or_positions = _build_bottom_content(card)

    # Bottom panel
    bot_cw = max(ic_wrk.width, ic_arr_d.width, content_w)
    bot_ch = ic_wrk.height + GAP_V + ic_arr_d.height + GAP_V + content_h
    by = H - EDGE - bot_ch - PAD * 2
    bb = (EDGE, by, EDGE + bot_cw + PAD * 2, by + bot_ch + PAD * 2)

    # ── Place top-left icons ──────────────────────────────────────────────
    cx = EDGE + PAD
    cy_base = EDGE + PAD

    c = paste_icon(c, ic_dis1, (cx, cy_base + (top_ch - ic_dis1.height) // 2))
    cx += ic_dis1.width + GAP_H

    c = paste_icon(c, ic_arr_h, (cx, cy_base + (top_ch - ic_arr_h.height) // 2))
    cx += ic_arr_h.width + GAP_H

    # Nudge action icon when multiplier is an above-left badge (not draw2 where text is centered on icon)
    needs_badge_offset = top_multiplier is not None and ability != "draw2"
    action_offset_x = 22 if needs_badge_offset else 0
    action_offset_y = 16 if needs_badge_offset else 0
    action_x = cx + action_offset_x
    action_y = cy_base + (top_ch - ic_action.height) // 2 + action_offset_y
    c = paste_icon(c, ic_action, (action_x, action_y))

    # Upward arrow at top of action icon (destroyCards only)
    if ability == "destroyCards":
        arr_x = action_x + (ic_action.width - ic_arr_up.width) // 2
        arr_y = action_y - ic_arr_up.height // 2
        c = paste_icon(c, ic_arr_up, (arr_x, arr_y))

    # Multiplier badge for top ability (e.g., "+2" for draw cards)
    if top_multiplier:
        mw, mh = tsize(top_multiplier, mult_font)
        if ability == "draw2":
            # Center text on the card icon (dark text on light card)
            mx = action_x + (ic_action.width - mw) // 2
            my = action_y + (ic_action.height - mh) // 2
            c = draw_text(c, (mx, my), top_multiplier, mult_font,
                          fill=(65, 48, 28, 255))
        else:
            mx = action_x - 18
            my = action_y - 42
            c = draw_text(c, (mx, my), top_multiplier, mult_font,
                          fill=(220, 200, 180, 255))

    # ── Glow behind bottom-left icons ───────────────────────────────────
    c = cloud_panel(c, bb, color=(255, 255, 255, 90), blur=40)

    # ── Place bottom-left icons ───────────────────────────────────────────
    cy = by + PAD

    # Workshop icon
    ix = EDGE + PAD + (bot_cw - ic_wrk.width) // 2
    c = paste_icon(c, ic_wrk, (ix, cy))
    cy += ic_wrk.height + GAP_V

    # Down arrow
    ix = EDGE + PAD + (bot_cw - ic_arr_d.width) // 2
    c = paste_icon(c, ic_arr_d, (ix, cy))
    cy += ic_arr_d.height + GAP_V

    # Card-specific content
    content_base_x = EDGE + PAD + (bot_cw - content_w) // 2
    content_base_y = cy
    for item_img, rel_x, rel_y in content_items:
        c = paste_icon(c, item_img, (content_base_x + rel_x, content_base_y + rel_y))

    # Draw count badge on top-left of bottom workshop icon (materials or workshop_picks)
    if card["bottom"]["type"] in ("materials", "workshop_picks", "mix"):
        badge_font = get_font("georgia-bold", 52)
        c = draw_text(c, (content_base_x - 10, content_base_y - 18),
                      card["bottom"]["count"], badge_font,
                      fill=(220, 200, 180, 255))

    # Draw "or" text directly on canvas
    if or_positions:
        or_font = get_font("cochin-italic", 36)
        for rel_x, rel_y in or_positions:
            ox = content_base_x + rel_x
            oy = content_base_y + rel_y
            c = draw_text(c, (ox, oy - 16), "or", or_font,
                          fill=(255, 255, 255, 255))

    # ── Title (multi-line, right-aligned, WHITE text) ─────────────────────
    title = card["title"]
    title_size = 58 if len(title) > 12 else 72
    title_font = get_font("cochin-italic", title_size)
    c = draw_title_right_aligned(
        c, title, title_font,
        color=(255, 255, 255, 255),
        glow_color=(0, 0, 0, 120),
        glow_r=6,
    )

    return c


def save(card, output_dir=None):
    """Compose and save an action card.

    Returns:
        True on success, False if background missing.
    """
    if output_dir is None:
        output_dir = COMPOSED_DIR / "action"
    os.makedirs(output_dir, exist_ok=True)

    result = compose(card)
    if result is None:
        return False

    out_path = os.path.join(output_dir, f"{card['name']}.png")
    result.convert("RGB").save(out_path, "PNG")
    return True
