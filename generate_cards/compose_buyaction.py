"""Buy action punchboard tile composition and AI generation.

Punchboard tiles: 600x300px (2in x 1in at 300 DPI).
Action icons centered on tile with brief description text below.
Background generated via Nano Banana 2.
"""

import os
from PIL import Image, ImageDraw

from .card_data import ICON_DIR, PIG_DIR, COMPOSED_DIR
from .rendering import load_icon, paste_icon, get_font, tsize, draw_text, draw_text_with_glow


# Tile dimensions (2in x 1in at 300 DPI)
TW, TH = 600, 300

# Layout constants
GAP = 10
ICH = 120       # Main icon height
ICH_SM = 85     # Smaller icons for multi-icon layouts
ARR_H = 38      # Arrow height in chains
ARR_SWAP = 28   # Arrow height in swap/triangle layout
LABEL_SIZE = 38  # Description text font size
LABEL_GAP = 8   # Gap between icons and label

# Output directories
BUYACTION_REF_DIR = COMPOSED_DIR / "buyaction-ref"
BUYACTION_DIR = COMPOSED_DIR / "buyaction"

# ── Buy action data ─────────────────────────────────────────────────────────

BUY_ACTIONS = [
    {"name": "workshop-1", "label": "Workshop 1 Card from Hand"},
    {"name": "draw-1", "label": "Draw 1 Card from Deck"},
    {"name": "mix-1", "label": "Mix 1 Pair of Pigments"},
    {"name": "draft-slot", "label": "Gain 1 Extra Draft Slot"},
    {"name": "swap-material", "label": "Swap 1 Material for Another"},
    {"name": "draft-to-workshop", "label": "Move a Drafted Card to Workshop"},
    {"name": "unmix-1", "label": "Unmix 1 Pigment into Components"},
    {"name": "sell-tertiary", "label": "Sell 1 Tertiary Pigment for 1 Ducat"},
    {"name": "re-workshop", "label": "Re-workshop the Bottom Card"},
    {"name": "gain-primary", "label": "Gain 1 Primary Pigment of Choice"},
    {"name": "trash-workshop", "label": "Trash a Card from Workshop (don't trigger trash ability)"},
]


# ── Composition helpers ─────────────────────────────────────────────────────

def _card_with_text(text, height=ICH):
    """Create a blank card icon with text centered on it."""
    ic = load_icon(f"{ICON_DIR}/blank-card.png", height)
    overlay = Image.new("RGBA", ic.size, (0, 0, 0, 0))
    font = get_font("georgia-bold", int(height * 0.38))
    tw, th = tsize(text, font)
    ImageDraw.Draw(overlay).text(
        ((ic.width - tw) // 2, (ic.height - th) // 2),
        text, font=font, fill=(80, 55, 35, 255)
    )
    return Image.alpha_composite(ic, overlay)


def _build_icons(name):
    """Build the list of icon elements for an action.

    Returns:
        (elements, total_width, total_height, or_positions)
        elements: list of (icon, rel_x, rel_y) tuples
        or_positions: list of (rel_x, rel_y) for "or" text, or []
    """
    if name == "workshop-1":
        ic = load_icon(f"{ICON_DIR}/workshop.png", ICH)
        return [(ic, 0, 0)], ic.width, ic.height, []

    elif name == "draw-1":
        ic = _card_with_text("1")
        return [(ic, 0, 0)], ic.width, ic.height, []

    elif name == "mix-1":
        ic = load_icon(f"{ICON_DIR}/mix.png", ICH)
        return [(ic, 0, 0)], ic.width, ic.height, []

    elif name == "draft-slot":
        ic = _card_with_text("+1")
        return [(ic, 0, 0)], ic.width, ic.height, []

    elif name == "swap-material":
        # Three material icons in a triangle with gaps
        mat_h = 55
        ic_paint = load_icon(f"{ICON_DIR}/painting.png", mat_h)
        ic_ceram = load_icon(f"{ICON_DIR}/ceramics.png", mat_h)
        ic_text = load_icon(f"{ICON_DIR}/textile.png", mat_h)

        # Triangle: painting top-center, ceramics bottom-left, textile bottom-right
        v_gap = 12
        h_spread = 20

        bot_y = ic_paint.height + v_gap
        bot_row_w = ic_ceram.width + h_spread * 2 + ic_text.width
        total_w = max(ic_paint.width, bot_row_w)
        total_h = bot_y + max(ic_ceram.height, ic_text.height)
        cx = total_w // 2

        paint_x = cx - ic_paint.width // 2
        ceram_x = cx - h_spread - ic_ceram.width
        text_x = cx + h_spread

        elems = [
            (ic_paint, paint_x, 0),
            (ic_ceram, ceram_x, bot_y),
            (ic_text, text_x, bot_y),
        ]

        return elems, total_w, total_h, []

    elif name == "draft-to-workshop":
        ic_card = load_icon(f"{ICON_DIR}/blank-card.png", ICH_SM)
        ic_arr = load_icon(f"{ICON_DIR}/arrow.png", ARR_H)
        ic_wrk = load_icon(f"{ICON_DIR}/workshop.png", ICH_SM)
        gap = 14
        total_w = ic_card.width + gap + ic_arr.width + gap + ic_wrk.width
        total_h = max(ic_card.height, ic_arr.height, ic_wrk.height)
        mid_y = total_h // 2
        x = 0
        elems = [
            (ic_card, x, mid_y - ic_card.height // 2),
        ]
        x += ic_card.width + gap
        elems.append((ic_arr, x, mid_y - ic_arr.height // 2))
        x += ic_arr.width + gap
        elems.append((ic_wrk, x, mid_y - ic_wrk.height // 2))
        return elems, total_w, total_h, []

    elif name == "unmix-1":
        ic = load_icon(f"{ICON_DIR}/unmix.png", ICH)
        return [(ic, 0, 0)], ic.width, ic.height, []

    elif name == "sell-tertiary":
        ic_pig = load_icon(f"{PIG_DIR}/empty-pigment.png", ICH_SM)
        ic_arr = load_icon(f"{ICON_DIR}/arrow.png", ARR_H)
        ic_coin = load_icon(f"{ICON_DIR}/coin.png", ICH_SM)
        gap = 14
        total_w = ic_pig.width + gap + ic_arr.width + gap + ic_coin.width
        total_h = max(ic_pig.height, ic_arr.height, ic_coin.height)
        mid_y = total_h // 2
        x = 0
        elems = [
            (ic_pig, x, mid_y - ic_pig.height // 2),
        ]
        x += ic_pig.width + gap
        elems.append((ic_arr, x, mid_y - ic_arr.height // 2))
        x += ic_arr.width + gap
        elems.append((ic_coin, x, mid_y - ic_coin.height // 2))
        return elems, total_w, total_h, []

    elif name == "re-workshop":
        ic = load_icon(f"{ICON_DIR}/workshop.png", ICH)
        ic_arr_u = load_icon(f"{ICON_DIR}/arrow.png", ARR_H)
        ic_arr_u = ic_arr_u.rotate(90, expand=True, resample=Image.LANCZOS)
        total_w = max(ic.width, ic_arr_u.width)
        arr_gap = 6
        total_h = ic_arr_u.height + arr_gap + ic.height
        elems = [
            (ic_arr_u, (total_w - ic_arr_u.width) // 2, 0),
            (ic, (total_w - ic.width) // 2, ic_arr_u.height + arr_gap),
        ]
        return elems, total_w, total_h, []

    elif name == "gain-primary":
        # Three primary pigment bowls with "or" text between them
        pigs = [
            load_icon(f"{PIG_DIR}/red-pigment.png", ICH_SM),
            load_icon(f"{PIG_DIR}/yellow-pigment.png", ICH_SM),
            load_icon(f"{PIG_DIR}/blue-pigment.png", ICH_SM),
        ]
        or_font = get_font("cochin-italic", 36)
        or_w, or_h = tsize("or", or_font)
        or_gap = 6  # gap on each side of "or"
        or_slot = or_w + or_gap * 2  # total space for each "or"
        total_w = sum(p.width for p in pigs) + or_slot * 2
        total_h = max(p.height for p in pigs)
        mid_y = total_h // 2

        x = 0
        elems = []
        or_positions = []
        for i, pig in enumerate(pigs):
            elems.append((pig, x, mid_y - pig.height // 2))
            x += pig.width
            if i < len(pigs) - 1:
                # Position for "or" text (centered in the slot)
                or_x = x + or_gap + (or_w) // 2 - or_w // 2
                or_positions.append((x + or_gap, mid_y - or_h // 2))
                x += or_slot
        return elems, total_w, total_h, or_positions

    elif name == "trash-workshop":
        ic_dis = load_icon(f"{ICON_DIR}/discard.png", ICH)
        ic_wrk_sm = load_icon(f"{ICON_DIR}/workshop.png", 42)
        total_w = ic_dis.width
        total_h = ic_dis.height
        elems = [
            (ic_dis, 0, 0),
            (ic_wrk_sm, -4, ic_dis.height - ic_wrk_sm.height + 4),
        ]
        return elems, total_w, total_h, []

    return [], 0, 0, []


# ── Main composition ────────────────────────────────────────────────────────

def compose(action, bg=None):
    """Compose a punchboard tile with action icons centered and label below.

    Args:
        action: Dict with 'name' and 'label' fields.
        bg: Optional background PIL Image (RGBA). If None, uses white.

    Returns:
        PIL Image (RGBA) of the composed tile.
    """
    if bg is not None:
        c = bg.copy()
    else:
        c = Image.new("RGBA", (TW, TH), (255, 255, 255, 255))

    name = action["name"]
    label = action["label"]

    elements, group_w, group_h, or_positions = _build_icons(name)
    if not elements:
        return c

    # Word-wrap label to fit tile width
    label_font = get_font("cochin-italic", LABEL_SIZE)
    max_label_w = TW - 20  # small margin
    words = label.split()
    lines = []
    cur = words[0]
    for w in words[1:]:
        test = cur + " " + w
        tw, _ = tsize(test, label_font)
        if tw <= max_label_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    # If only 1 line, force split at midpoint for consistency
    if len(lines) == 1:
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    line_sizes = [tsize(l, label_font) for l in lines]
    line_gap = 4
    label_block_h = sum(h for _, h in line_sizes) + line_gap * (len(lines) - 1)

    # Vertically center icons + label as a combined block
    total_content_h = group_h + LABEL_GAP + label_block_h
    content_top = (TH - total_content_h) // 2

    # Center icon group horizontally
    offset_x = (TW - group_w) // 2
    offset_y = content_top

    # Place icons
    for icon, rel_x, rel_y in elements:
        c = paste_icon(c, icon, (offset_x + rel_x, offset_y + rel_y))

    # Draw "or" text for gain-primary with dark shadow
    shadow_color = (0, 0, 0, 40)
    shadow_r = 4
    if or_positions:
        or_font = get_font("cochin-italic", 36)
        for rel_x, rel_y in or_positions:
            c = draw_text_with_glow(
                c, (offset_x + rel_x, offset_y + rel_y),
                "or", or_font, fill=(80, 55, 35, 255),
                glow_color=shadow_color, glow_r=shadow_r)

    # Draw label lines centered below icons with dark shadow
    cur_y = content_top + group_h + LABEL_GAP
    for i, (line, (lw, lh)) in enumerate(zip(lines, line_sizes)):
        c = draw_text_with_glow(
            c, ((TW - lw) // 2, cur_y), line, label_font,
            fill=(80, 55, 35, 255), glow_color=shadow_color, glow_r=shadow_r)
        cur_y += lh + line_gap

    return c


# ── AI prompt ───────────────────────────────────────────────────────────────

def _touchup_prompt():
    """Build the AI prompt for punchboard tile watercolor styling."""
    return (
        "This is a reference layout for a small punchboard game token (2 inches wide by 1 inch tall) "
        "for a Renaissance Venice board game about dye trading called Colori.\n\n"
        "TASK: Add a warm aged parchment watercolor background texture behind and around the icons. "
        "Make the background look like authentic watercolor on textured paper — subtle cream and warm "
        "tones, visible paper grain, soft watercolor washes and blooms at the edges.\n\n"
        "CRITICAL RULES:\n"
        "- Keep ALL icons and text EXACTLY as they are — do not modify, redraw, move, or resize anything\n"
        "- Only change the white background areas between and around the icons and text\n"
        "- No extra text, letters, words, or numbers added\n"
        "- No border or frame around the tile\n"
        "- Full bleed — the watercolor texture should extend to all edges\n"
        "- The result should look like game icons printed on aged Italian watercolor paper\n"
        "- Warm golden parchment tones — think Renaissance Venetian manuscript paper\n"
    )


# ── Save / Generate ────────────────────────────────────────────────────────

def save_ref(action, output_dir=None):
    """Compose and save a reference tile (icons only, no AI).

    Returns:
        True on success.
    """
    if output_dir is None:
        output_dir = BUYACTION_REF_DIR
    os.makedirs(str(output_dir), exist_ok=True)

    result = compose(action)
    out_path = os.path.join(str(output_dir), f"{action['name']}.png")
    result.convert("RGB").save(out_path, "PNG")
    return True


def generate(action, output_dir=None):
    """Compose icons then generate final tile via Nano Banana 2.

    Args:
        action: Buy action dict with 'name' and 'label' fields.
        output_dir: Where to save final output.

    Returns:
        True on success, False on failure.
    """
    from .api import touchup_image

    if output_dir is None:
        output_dir = BUYACTION_DIR
    os.makedirs(str(output_dir), exist_ok=True)

    out_path = os.path.join(str(output_dir), f"{action['name']}.png")

    # Compose the reference image with icons on white
    ref_img = compose(action)

    # Send to Nano Banana 2 for watercolor background
    prompt = _touchup_prompt()
    return touchup_image(None, prompt, out_path, input_image=ref_img)
