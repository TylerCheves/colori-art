"""CLI and pipeline orchestration for Colori card generation.

Usage:
    python -m generate_cards                          # full pipeline
    python -m generate_cards compose --cards kermes   # specific cards
    python -m generate_cards enhance --type dye       # enhance dye colors
    python -m generate_cards export                   # export final art to web app
    python -m generate_cards layout                   # print layout only
    python -m generate_cards --force --dry-run        # options
"""

import argparse
import os
import shutil
import sys

from .card_data import (
    DYE_CARDS, ACTION_CARDS, MATERIAL_CARDS, BUYER_CARDS,
    BASE_BG_DIR, ARTWORK_DIR,
    COMPOSED_DIR,
    ICON_DIR, PIG_DIR, PKG_DIR,
    filter_cards_by_name,
)
from .prompts import (
    BASE_BG_PROMPTS, artwork_dye_prompt, artwork_action_prompt, artwork_material_prompt,
    touchup_dye_prompt, touchup_action_prompt, touchup_material_prompt,
)
from . import compose_dye, compose_action, compose_material, compose_buyer, compose_buyaction
from .layout import generate_print_layout

ENHANCED_DIR = PKG_DIR / "enhanced"
TOUCHUP_DIR = PKG_DIR / "touchup"
EXPORT_DIR = PKG_DIR.parent / "for-colori-web-app"


def should_generate(output_path, force=False):
    """Check if a file needs to be generated."""
    return force or not os.path.exists(output_path)


# ── Base background generation ──────────────────────────────────────────────

def run_base_backgrounds(force=False, dry_run=False):
    """Generate base texture backgrounds (one per card type: dye, action, material)."""
    from .api import generate_image_no_ref

    tasks = []
    for bg_type, prompt in BASE_BG_PROMPTS.items():
        out = str(BASE_BG_DIR / f"{bg_type}.png")
        if should_generate(out, force):
            tasks.append((bg_type, prompt, out))

    if not tasks:
        print("No base backgrounds to generate (all exist).")
        return []

    print(f"Generating {len(tasks)} base background(s)...")
    if dry_run:
        for bg_type, _, out in tasks:
            print(f"  [DRY RUN] Would generate: {bg_type} -> {out}")
        return []

    failures = []
    for i, (bg_type, prompt, out) in enumerate(tasks, 1):
        print(f"[{i}/{len(tasks)}] Generating {bg_type} base...", end=" ", flush=True)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        ok = generate_image_no_ref(prompt, out)
        print("OK" if ok else "FAILED")
        if not ok:
            failures.append(bg_type)

    return failures


# ── Artwork generation ──────────────────────────────────────────────────────

def run_artwork(card_type, card_names, force=False, dry_run=False):
    """Generate per-card artwork images (centered subject, fading edges)."""
    from .api import generate_image_no_ref

    tasks = []

    if card_type in (None, "dye"):
        cards = filter_cards_by_name(DYE_CARDS, card_names)
        for card in cards:
            out = str(ARTWORK_DIR / "dye" / f"{card['name']}.png")
            if should_generate(out, force):
                tasks.append(("dye", card["name"], card["title"],
                              lambda c=card: artwork_dye_prompt(c), out))

    if card_type in (None, "action"):
        cards = filter_cards_by_name(ACTION_CARDS, card_names)
        for card in cards:
            out = str(ARTWORK_DIR / "action" / f"{card['name']}.png")
            if should_generate(out, force):
                tasks.append(("action", card["name"], card["title"],
                              lambda c=card: artwork_action_prompt(c), out))

    if card_type in (None, "material"):
        seen_bg_types = set()
        cards = filter_cards_by_name(MATERIAL_CARDS, card_names)
        for card in cards:
            bt = card["bg_type"]
            if bt in seen_bg_types:
                continue
            seen_bg_types.add(bt)
            out = str(ARTWORK_DIR / "material" / f"{bt}.png")
            if should_generate(out, force):
                tasks.append(("material", bt, bt,
                              lambda b=bt: artwork_material_prompt(b), out))

    if not tasks:
        print("No artwork to generate (all exist or none matched).")
        return []

    print(f"Generating {len(tasks)} artwork image(s)...")
    if dry_run:
        for _, slug, title, _, out in tasks:
            print(f"  [DRY RUN] Would generate artwork: {title} -> {out}")
        return []

    failures = []
    for i, (ctype, slug, title, prompt_fn, out) in enumerate(tasks, 1):
        print(f"[{i}/{len(tasks)}] Generating {title} artwork...", end=" ", flush=True)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        prompt = prompt_fn()
        ok = generate_image_no_ref(prompt, out)
        print("OK" if ok else "FAILED")
        if not ok:
            failures.append(slug)

    return failures


# ── Composition ──────────────────────────────────────────────────────────────

def run_compose(card_type, card_names, force=False, dry_run=False):
    """Compose cards from backgrounds + icons + text. Output to composed/."""
    tasks = []

    if card_type in (None, "dye"):
        cards = filter_cards_by_name(DYE_CARDS, card_names)
        for card in cards:
            out = str(COMPOSED_DIR / "dye" / f"{card['name']}.png")
            if should_generate(out, force):
                tasks.append(("dye", card["name"], card))

    if card_type in (None, "action"):
        cards = filter_cards_by_name(ACTION_CARDS, card_names)
        for card in cards:
            out = str(COMPOSED_DIR / "action" / f"{card['name']}.png")
            if should_generate(out, force):
                tasks.append(("action", card["name"], card))

    if card_type in (None, "material"):
        cards = filter_cards_by_name(MATERIAL_CARDS, card_names)
        for card in cards:
            out = str(COMPOSED_DIR / "material" / f"{card['name']}.png")
            if should_generate(out, force):
                tasks.append(("material", card["name"], card))

    if card_type in (None, "buyer"):
        names = filter_cards_by_name(BUYER_CARDS, card_names)
        for name in names:
            out = str(COMPOSED_DIR / "buyer" / f"{name}.png")
            if should_generate(out, force):
                tasks.append(("buyer", name, name))

    if not tasks:
        print("No cards to compose (all exist or none matched).")
        return []

    print(f"Composing {len(tasks)} card(s)...")
    if dry_run:
        for _, slug, _ in tasks:
            print(f"  [DRY RUN] Would compose: {slug}")
        return []

    failures = []
    for i, (ctype, slug, data) in enumerate(tasks, 1):
        print(f"[{i}/{len(tasks)}] Composing {slug}...", end=" ", flush=True)
        if ctype == "dye":
            ok = compose_dye.save(data, output_dir=COMPOSED_DIR / "dye")
        elif ctype == "action":
            ok = compose_action.save(data, output_dir=COMPOSED_DIR / "action")
        elif ctype == "material":
            ok = compose_material.save(data, output_dir=COMPOSED_DIR / "material")
        elif ctype == "buyer":
            ok = compose_buyer.save(data, output_dir=COMPOSED_DIR / "buyer")
        else:
            ok = False

        if ok:
            print("OK")
        else:
            print("SKIP (no background)")
            failures.append(slug)

    return failures


# ── Enhancement ──────────────────────────────────────────────────────────────

def run_enhance(card_type, card_names, force=False, dry_run=False, strength=0.45):
    """Enhance dye card colors with saturation boost and color wash.

    Reads from composed/dye/, writes to enhanced/dye/.
    Only applies to dye cards (other types are skipped).
    """
    if card_type is not None and card_type != "dye":
        print("Enhance step only applies to dye cards, skipping.")
        return []

    from .enhance_dye_colors import enhance_card, ENHANCED_DIR
    from PIL import Image

    cards = filter_cards_by_name(DYE_CARDS, card_names)
    tasks = []
    for card in cards:
        inp = str(COMPOSED_DIR / "dye" / f"{card['name']}.png")
        out = str(ENHANCED_DIR / f"{card['name']}.png")
        if should_generate(out, force):
            tasks.append((card, inp, out))

    if not tasks:
        print("No dye cards to enhance (all exist or none matched).")
        return []

    print(f"Enhancing {len(tasks)} dye card(s)...")
    if dry_run:
        for card, _, out in tasks:
            print(f"  [DRY RUN] Would enhance: {card['name']}")
        return []

    os.makedirs(str(ENHANCED_DIR), exist_ok=True)
    failures = []
    for i, (card, inp, out) in enumerate(tasks, 1):
        print(f"[{i}/{len(tasks)}] Enhancing {card['name']}...", end=" ", flush=True)
        if not os.path.exists(inp):
            print("SKIP (no composed input)")
            failures.append(card["name"])
            continue
        img = Image.open(inp)
        result = enhance_card(img, card, strength=strength)
        result.save(out, "PNG")
        print("OK")

    return failures


# ── Touchup (API-based typography) ────────────────────────────────────────────

def run_touchup(card_type, card_names, force=False, dry_run=False):
    """Convert dye/action card typography to handwritten Venetian style via API.

    Dye cards: reads from enhanced/dye/ (falling back to composed/dye/).
    Action cards: reads from composed/action/.
    Writes to touchup/{type}/.
    """
    if card_type is not None and card_type not in ("dye", "action", "material"):
        print("Touchup step only applies to dye, action, and material cards, skipping.")
        return []

    from .api import touchup_image

    tasks = []

    if card_type in (None, "dye"):
        cards = filter_cards_by_name(DYE_CARDS, card_names)
        for card in cards:
            enhanced = ENHANCED_DIR / "dye" / f"{card['name']}.png"
            composed = COMPOSED_DIR / "dye" / f"{card['name']}.png"
            inp = str(enhanced if enhanced.exists() else composed)
            out = str(TOUCHUP_DIR / "dye" / f"{card['name']}.png")
            if should_generate(out, force):
                tasks.append(("dye", card, inp, out, touchup_dye_prompt))

    if card_type in (None, "action"):
        cards = filter_cards_by_name(ACTION_CARDS, card_names)
        for card in cards:
            inp = str(COMPOSED_DIR / "action" / f"{card['name']}.png")
            out = str(TOUCHUP_DIR / "action" / f"{card['name']}.png")
            if should_generate(out, force):
                tasks.append(("action", card, inp, out, touchup_action_prompt))

    if card_type in (None, "material"):
        cards = filter_cards_by_name(MATERIAL_CARDS, card_names)
        for card in cards:
            inp = str(COMPOSED_DIR / "material" / f"{card['name']}.png")
            out = str(TOUCHUP_DIR / "material" / f"{card['name']}.png")
            if should_generate(out, force):
                tasks.append(("material", card, inp, out, touchup_material_prompt))

    if not tasks:
        print("No cards to touch up (all exist or none matched).")
        return []

    print(f"Touching up {len(tasks)} card(s)...")
    if dry_run:
        for ctype, card, _, out, _ in tasks:
            print(f"  [DRY RUN] Would touch up: {card['name']} ({ctype})")
        return []

    failures = []
    for i, (ctype, card, inp, out, prompt_fn) in enumerate(tasks, 1):
        print(f"[{i}/{len(tasks)}] Touching up {card['name']} ({ctype})...", end=" ", flush=True)
        if not os.path.exists(inp):
            print("SKIP (no input)")
            failures.append(card["name"])
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        prompt = prompt_fn(card)
        ok = touchup_image(inp, prompt, out)
        print("OK" if ok else "FAILED")
        if not ok:
            failures.append(card["name"])

    return failures


# ── Buy Action Punchboard Tiles ──────────────────────────────────────────────

def run_buyaction(card_names, force=False, dry_run=False, compose_only=False):
    """Generate buy action punchboard tiles (2in x 1in).

    Composes icon layouts then generates via Nano Banana 2.
    """
    from .compose_buyaction import BUY_ACTIONS, BUYACTION_DIR, BUYACTION_REF_DIR

    actions = BUY_ACTIONS
    if card_names:
        name_set = set(card_names)
        actions = [a for a in actions if a["name"] in name_set]

    tasks = []
    for action in actions:
        out_dir = BUYACTION_REF_DIR if compose_only else BUYACTION_DIR
        out = str(out_dir / f"{action['name']}.png")
        if should_generate(out, force):
            tasks.append(action)

    if not tasks:
        print("No buy action tiles to generate (all exist or none matched).")
        return []

    mode = "Composing" if compose_only else "Generating"
    print(f"{mode} {len(tasks)} buy action tile(s)...")
    if dry_run:
        for action in tasks:
            print(f"  [DRY RUN] Would generate: {action['name']}")
        return []

    failures = []
    for i, action in enumerate(tasks, 1):
        print(f"[{i}/{len(tasks)}] {mode} {action['name']}...", end=" ", flush=True)
        if compose_only:
            ok = compose_buyaction.save_ref(action)
        else:
            ok = compose_buyaction.generate(action)
        print("OK" if ok else "FAILED")
        if not ok:
            failures.append(action["name"])

    return failures


# ── Layout ───────────────────────────────────────────────────────────────────

def run_layout(dry_run=False):
    """Generate print layout sheets."""
    if dry_run:
        print("[DRY RUN] Would generate print layout sheets.")
        return []

    generate_print_layout()
    return []


# ── Export ───────────────────────────────────────────────────────────────────

def run_export(dry_run=False):
    """Export card art and assets to for-colori-web-app/.

    Sources: enhanced/dye/ for dye cards (falling back to composed/dye/),
    composed/{type}/ for all other types.
    Also copies pigment icons and key iconography assets.
    """
    os.makedirs(str(EXPORT_DIR), exist_ok=True)

    exported = 0
    skipped = 0

    # Export card images
    all_cards = []
    for card in DYE_CARDS:
        all_cards.append(("dye", card["name"]))
    for card in ACTION_CARDS:
        all_cards.append(("action", card["name"]))
    for card in MATERIAL_CARDS:
        all_cards.append(("material", card["name"]))
    for name in BUYER_CARDS:
        all_cards.append(("buyer", name))

    if dry_run:
        print(f"[DRY RUN] Would export {len(all_cards)} card(s) + icon assets to {EXPORT_DIR}")
        return []

    for ctype, name in all_cards:
        # Dye cards: prefer touchup > enhanced > composed
        if ctype == "dye":
            touchup = TOUCHUP_DIR / "dye" / f"{name}.png"
            enhanced = ENHANCED_DIR / "dye" / f"{name}.png"
            composed = COMPOSED_DIR / "dye" / f"{name}.png"
            src = (touchup if touchup.exists()
                   else enhanced if enhanced.exists()
                   else composed if composed.exists()
                   else None)
        elif ctype in ("action", "material"):
            touchup = TOUCHUP_DIR / ctype / f"{name}.png"
            composed = COMPOSED_DIR / ctype / f"{name}.png"
            src = touchup if touchup.exists() else composed if composed.exists() else None
        else:
            composed = COMPOSED_DIR / ctype / f"{name}.png"
            src = composed if composed.exists() else None
        dst = EXPORT_DIR / f"{name}.png"

        if src is None:
            skipped += 1
            continue

        shutil.copy2(str(src), str(dst))
        exported += 1

    # Export pigment icons
    if PIG_DIR.exists():
        for pig in PIG_DIR.iterdir():
            if pig.suffix == ".png":
                shutil.copy2(str(pig), str(EXPORT_DIR / pig.name))
                exported += 1

    # Export key iconography assets
    for icon_name in ["coin.png", "mix.png", "workshop.png", "ceramics.png",
                      "painting.png", "textile.png"]:
        src = ICON_DIR / icon_name
        if src.exists():
            shutil.copy2(str(src), str(EXPORT_DIR / icon_name))
            exported += 1

    print(f"Exported {exported} file(s) to {EXPORT_DIR} ({skipped} skipped)")
    return []


# ── CLI ──────────────────────────────────────────────────────────────────────

def _add_common_args(parser):
    """Add shared flags to a parser or subparser."""
    parser.add_argument("--force", action="store_true",
                        help="Regenerate even if output exists")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be generated without doing it")
    parser.add_argument("--type", choices=["dye", "action", "material", "buyer"],
                        help="Filter by card type")
    parser.add_argument("--cards", nargs="+", metavar="NAME",
                        help="Filter by card name(s)")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="generate_cards",
        description="Colori card generation pipeline",
    )
    _add_common_args(parser)
    parser.add_argument("--strength", type=float, default=0.45,
                        help="Color enhancement strength for dye cards (0.0-1.0, default 0.45)")

    sub = parser.add_subparsers(dest="command")

    for name, hlp in [
        ("base-backgrounds", "Generate base texture backgrounds (3 total, API)"),
        ("artwork", "Generate per-card artwork images (API)"),
        ("compose", "Compose cards from backgrounds + icons + text"),
        ("enhance", "Enhance dye card colors (saturation + color wash)"),
        ("touchup", "Convert dye card typography to handwritten style (API)"),
        ("buyaction", "Generate buy action punchboard tiles (2in x 1in, API)"),
        ("layout", "Generate print layout sheets"),
        ("export", "Export final art to for-colori-web-app/"),
    ]:
        sp = sub.add_parser(name, help=hlp)
        _add_common_args(sp)
        if name == "enhance":
            sp.add_argument("--strength", type=float, default=0.45,
                            help="Color wash strength (0.0-1.0, default 0.45)")
        if name == "buyaction":
            sp.add_argument("--compose-only", action="store_true",
                            help="Save icon-only reference (no AI generation)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    card_type = args.type

    card_names = args.cards
    force = args.force
    dry_run = args.dry_run
    strength = getattr(args, "strength", 0.45)

    # Determine which steps to run
    command = args.command
    if command is None:
        # Full pipeline
        steps = ["base-backgrounds", "artwork", "compose",
                 "enhance", "touchup", "layout", "export"]
    else:
        steps = [command]

    all_failures = []

    for step in steps:
        print(f"\n{'='*50}")
        print(f"Step: {step}")
        print(f"{'='*50}\n")

        if step == "base-backgrounds":
            failures = run_base_backgrounds(force, dry_run)
        elif step == "artwork":
            failures = run_artwork(card_type, card_names, force, dry_run)
        elif step == "compose":
            failures = run_compose(card_type, card_names, force, dry_run)
        elif step == "enhance":
            failures = run_enhance(card_type, card_names, force, dry_run, strength)
        elif step == "touchup":
            failures = run_touchup(card_type, card_names, force, dry_run)
        elif step == "buyaction":
            compose_only = getattr(args, "compose_only", False)
            failures = run_buyaction(card_names, force, dry_run, compose_only)
        elif step == "layout":
            failures = run_layout(dry_run)
        elif step == "export":
            failures = run_export(dry_run)
        else:
            print(f"Unknown step: {step}")
            failures = []

        all_failures.extend(failures)

    # Summary
    print(f"\n{'='*50}")
    if all_failures:
        print(f"Pipeline complete with {len(all_failures)} failure(s):")
        for f in all_failures:
            print(f"  - {f}")
        # Build re-run command
        failed_names = " ".join(all_failures)
        print(f"\nRe-run failed cards:")
        print(f"  python -m generate_cards --force --cards {failed_names}")
        sys.exit(1)
    else:
        print("Pipeline complete. All cards generated successfully.")


if __name__ == "__main__":
    main()
