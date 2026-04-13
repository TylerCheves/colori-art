"""Print layout tiling -- tile card images onto printable 8.5x11 letter-size sheets.

Sources:
  - Dye cards: enhanced/dye/ (falling back to composed/dye/)
  - Action cards: composed/action/
  - Buyer cards: composed/buyer/
"""

import os
import math
from PIL import Image, ImageDraw

from .card_data import COMPOSED_DIR, PRINT_DIR, PKG_DIR, DYE_PRINT_COPIES, ACTION_PRINT_COPIES

ENHANCED_DYE_DIR = PKG_DIR / "enhanced" / "dye"

# ── Configuration ────────────────────────────────────────────────────────────

DPI = 300
SHEET_W = int(8.5 * DPI)   # 2550
SHEET_H = int(11 * DPI)    # 3300
CARD_W = int(2.5 * DPI)    # 750
CARD_H = int(3.5 * DPI)    # 1050

COLS = SHEET_W // CARD_W    # 3
ROWS = SHEET_H // CARD_H   # 3
CARDS_PER_SHEET = COLS * ROWS  # 9

MARGIN_X = (SHEET_W - COLS * CARD_W) // 2
MARGIN_Y = (SHEET_H - ROWS * CARD_H) // 2

CUT_COLOR = (160, 160, 160)
CUT_WIDTH = 2
TICK_LEN = int(0.25 * DPI)


# ── Layout helpers ───────────────────────────────────────────────────────────

def _draw_cut_lines(sheet, num_cards):
    """Draw corner tick marks for cutting guides."""
    draw = ImageDraw.Draw(sheet)
    num_rows = min(ROWS, math.ceil(num_cards / COLS))
    num_cols = min(COLS, num_cards)

    for c in range(num_cols + 1):
        x = MARGIN_X + c * CARD_W
        draw.line([(x, 0), (x, TICK_LEN)], fill=CUT_COLOR, width=CUT_WIDTH)
        draw.line([(x, SHEET_H - TICK_LEN), (x, SHEET_H)], fill=CUT_COLOR, width=CUT_WIDTH)

    for r in range(num_rows + 1):
        y = MARGIN_Y + r * CARD_H
        draw.line([(0, y), (TICK_LEN, y)], fill=CUT_COLOR, width=CUT_WIDTH)
        draw.line([(SHEET_W - TICK_LEN, y), (SHEET_W, y)], fill=CUT_COLOR, width=CUT_WIDTH)


def _create_sheet(card_paths):
    """Create a single sheet with cards tiled in a 3x3 grid."""
    sheet = Image.new("RGB", (SHEET_W, SHEET_H), "white")
    for i, card_path in enumerate(card_paths):
        row = i // COLS
        col = i % COLS
        x = MARGIN_X + col * CARD_W
        y = MARGIN_Y + row * CARD_H

        card = Image.open(card_path)
        if card.size != (CARD_W, CARD_H):
            card = card.resize((CARD_W, CARD_H), Image.LANCZOS)
        if card.mode == "RGBA":
            sheet.paste(card, (x, y), card)
        else:
            sheet.paste(card, (x, y))

    _draw_cut_lines(sheet, len(card_paths))
    return sheet


def _build_paths(card_list, source_dir):
    """Expand (name, copies) list into flat list of file paths."""
    paths = []
    for name, copies in card_list:
        path = os.path.join(source_dir, f"{name}.png")
        if not os.path.exists(path):
            print(f"  WARNING: Missing {path}")
            continue
        paths.extend([path] * copies)
    return paths


def _generate_sheets(paths, prefix, label, output_dir):
    """Generate printable sheets from a list of card paths."""
    total = len(paths)
    if total == 0:
        print(f"No {label} to print.")
        return 0
    num_sheets = math.ceil(total / CARDS_PER_SHEET)
    print(f"{label}: {total} cards -> {num_sheets} sheets")

    for s in range(num_sheets):
        start = s * CARDS_PER_SHEET
        end = min(start + CARDS_PER_SHEET, total)
        batch = paths[start:end]

        sheet = _create_sheet(batch)
        out_path = os.path.join(output_dir, f"{prefix}-{s + 1:02d}.jpg")
        sheet.save(out_path, dpi=(DPI, DPI), quality=95)
        print(f"  Sheet {s + 1}/{num_sheets}: {len(batch)} cards -> {out_path}")

    return num_sheets


def generate_print_layout(output_dir=None):
    """Generate all print layout sheets.

    Returns:
        Total number of sheets generated.
    """
    if output_dir is None:
        output_dir = str(PRINT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    action_dir = str(COMPOSED_DIR / "action")
    buyer_dir = str(COMPOSED_DIR / "buyer")

    # Dye cards: prefer enhanced, fall back to composed
    dye_dir_enhanced = str(ENHANCED_DYE_DIR)
    dye_dir_composed = str(COMPOSED_DIR / "dye")

    # Build buyer cards list from directory
    buyer_cards = []
    if os.path.isdir(buyer_dir):
        files = sorted(f for f in os.listdir(buyer_dir) if f.endswith(".png"))
        buyer_cards = [(f.replace(".png", ""), 1) for f in files]

    # For dye, check enhanced first, then composed
    dye_paths = []
    for name, copies in DYE_PRINT_COPIES:
        enhanced_path = os.path.join(dye_dir_enhanced, f"{name}.png")
        composed_path = os.path.join(dye_dir_composed, f"{name}.png")
        path = enhanced_path if os.path.exists(enhanced_path) else composed_path
        if not os.path.exists(path):
            print(f"  WARNING: Missing {path}")
            continue
        dye_paths.extend([path] * copies)
    action_paths = _build_paths(ACTION_PRINT_COPIES, action_dir)
    buyer_paths = _build_paths(buyer_cards, buyer_dir)

    print(f"Dye cards:     {len(dye_paths)} total")
    print(f"Action cards:  {len(action_paths)} total")
    print(f"Buyer cards:   {len(buyer_paths)} total")
    print(f"Grand total:   {len(dye_paths) + len(action_paths) + len(buyer_paths)} cards")
    print(f"Cards per sheet: {CARDS_PER_SHEET}")
    print()

    total_sheets = 0
    total_sheets += _generate_sheets(dye_paths, "dye", "Dye cards", output_dir)
    print()
    total_sheets += _generate_sheets(action_paths, "action", "Action cards", output_dir)
    print()
    total_sheets += _generate_sheets(buyer_paths, "buyer", "Buyer cards", output_dir)

    print(f"\nDone! {total_sheets} total sheets saved to {output_dir}/")
    return total_sheets
