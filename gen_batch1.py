"""Generate card art for dye + action cards using new art style references.

Feeds the appropriate style reference image into each generation call:
  - Dye cards → cinnabar.png reference
  - Action cards → alum.png reference

Outputs to finals-without-iconography/ as pure illustrations
(no brush overlays, no typography).
"""

import os
import sys
import time
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

API_KEY = os.environ.get("GOOGLE_API_KEY")
MODEL = "gemini-3.1-flash-image-preview"
WIDTH, HEIGHT = 750, 1050
OUTPUT_DIR = "finals-without-iconography"
RATE_LIMIT = 5  # seconds between calls

# Style reference images
DYE_REF = "finals-without-iconography/cinnabar.png"
ACTION_REF = "finals-without-iconography/alum.png"

# ── Card definitions ────────────────────────────────────────────────────────

DYE_CARDS = [
    # Starter basics
    {
        "name": "basic-red",
        "art": (
            "A simple clay bowl filled with a generic red dye bath, sitting on a worn wooden "
            "workbench in a Renaissance Venice dye workshop. Plain and functional — a beginner's "
            "tool. The bowl is chipped and well-used. Red dye stains the wood around it."
        ),
        "palette": "deep crimson red, warm wood tones",
    },
    {
        "name": "basic-yellow",
        "art": (
            "A simple clay bowl filled with a generic yellow dye bath, sitting on a worn wooden "
            "workbench in a Renaissance Venice dye workshop. Plain and functional — a beginner's "
            "tool. The bowl is chipped and well-used. Yellow dye stains the wood around it."
        ),
        "palette": "warm golden yellow, warm wood tones",
    },
    {
        "name": "basic-blue",
        "art": (
            "A simple clay bowl filled with a generic blue dye bath, sitting on a worn wooden "
            "workbench in a Renaissance Venice dye workshop. Plain and functional — a beginner's "
            "tool. The bowl is chipped and well-used. Blue dye stains the wood around it."
        ),
        "palette": "rich cerulean blue, warm wood tones",
    },
    # Primaries
    {
        "name": "kermes",
        "art": (
            "A gnarled Mediterranean oak branch crawling with tiny scarlet insects on a wooden "
            "workbench. A dyer's hand reaches in with a small brush, carefully sweeping the "
            "precious creatures into a ceramic bowl already stained deep crimson. Scattered red "
            "pigment and insects on the planks."
        ),
        "palette": "scarlet red and crimson, warm wood tones",
    },
    {
        "name": "weld",
        "art": (
            "Tall spikes of tiny yellow-green weld flowers bundled and hanging upside down to "
            "dry in a Renaissance workshop. Below them on the workbench, a dye bath glows an "
            "almost electric yellow, a skein of wool being lifted out with a wooden rod, "
            "dripping brilliant gold."
        ),
        "palette": "electric yellow and gold, warm wood tones",
    },
    {
        "name": "woad",
        "art": (
            "Broad green woad leaves being crushed in a stone trough by wooden mallets on a "
            "workshop bench. The pulp formed into dark balls set out to dry on wooden racks. "
            "A fermentation vat in the background bubbles with a foul-smelling blue-black liquor, "
            "a copper-blue sheen on its surface."
        ),
        "palette": "deep indigo blue and blue-black, warm wood tones",
    },
    # Secondaries
    {
        "name": "madder",
        "art": (
            "Thick ruddy madder roots being pulled from dark earth by weathered hands on a "
            "workshop table. A cutting board nearby shows sliced cross-sections of the root "
            "revealing rings of deepening red toward the center. Root debris and soil scattered "
            "on the wooden planks."
        ),
        "palette": "ruddy orange-red and deep red, warm earth tones",
    },
    {
        "name": "turmeric",
        "art": (
            "Knobbly orange-yellow turmeric roots freshly cut on a wooden workbench, their "
            "interior a shocking bright orange that stains everything it touches. A merchant's "
            "hands are permanently yellowed from handling the spice. Powder spills from a cloth "
            "sack onto the table."
        ),
        "palette": "bright orange and deep yellow, warm wood tones",
    },
    {
        "name": "dyers-greenweed",
        "art": (
            "Low bushy shrubs of dyer's greenweed covered in small bright yellow flowers, "
            "gathered in armfuls on a workshop table. A dyer's apprentice sorts the flowering "
            "branches, their apron already stained yellow. A dye bath nearby glows yellow-green."
        ),
        "palette": "bright yellow-green and chartreuse, warm wood tones",
    },
    {
        "name": "verdigris",
        "art": (
            "Copper plates stacked with grape skins and pomace, pulled open on a workshop bench "
            "to reveal the metal surfaces crusted with a brilliant blue-green patina. A craftsman "
            "carefully scrapes the vivid green verdigris powder into a glass bottle. Green-blue "
            "dust on the planks."
        ),
        "palette": "brilliant blue-green and teal, warm wood tones",
    },
    {
        "name": "orchil",
        "art": (
            "Crusts of pale grey-green lichen in a basket on a workshop table, being sorted for "
            "the dye vat. In covered clay pots nearby, the lichen ferments — a lid lifted to "
            "reveal a vivid reddish-purple paste inside. Stained rags and purple splotches on "
            "the wooden planks."
        ),
        "palette": "reddish-purple and violet, warm wood tones",
    },
    {
        "name": "logwood",
        "art": (
            "Dark heartwood chips steeping in a copper cauldron on a workshop bench, the liquid "
            "a deep blue-violet that shifts color as it catches the light. A dyer tests the shade "
            "by dipping a white linen strip, pulling it out to reveal a rich purple-blue stain "
            "spreading through the fibers."
        ),
        "palette": "deep blue-violet and purple, warm wood tones",
    },
    # Tertiaries (minus vermilion which is done as cinnabar)
    {
        "name": "saffron",
        "art": (
            "Delicate purple crocus flowers laid open on a workshop table, their precious "
            "red-orange stigmas being plucked with tweezers by careful hands. Only a tiny pile "
            "of saffron threads sits in a golden dish — a fortune's worth of the rarest spice. "
            "The brilliant orange-red threads contrast against the wooden planks."
        ),
        "palette": "red-orange and amber gold, warm wood tones",
    },
    {
        "name": "persian-berries",
        "art": (
            "Small clusters of dark green-to-black Persian berries on thorny branches, being "
            "sorted by a merchant on a woven tray atop a workbench. Some crushed berries in a "
            "ceramic bowl show their bright chartreuse-yellow juice against the white glaze. "
            "Berry stains on the wooden planks."
        ),
        "palette": "chartreuse yellow-green, warm wood tones",
    },
    {
        "name": "azurite",
        "art": (
            "A rough chunk of brilliant blue azurite mineral with botryoidal surface, sitting "
            "on a workshop bench alongside scales and small brass weights. The stone seems to "
            "glow from within, a vivid sky blue against the dark wood. Blue mineral dust "
            "scattered on the planks."
        ),
        "palette": "vivid sky blue and teal, warm wood tones",
    },
    {
        "name": "indigo",
        "art": (
            "A merchant opens a tightly wrapped bundle from the East on a workshop table, "
            "revealing dense cakes of dark blue-black indigo pigment. He snaps a piece and the "
            "fracture line gleams an iridescent metallic blue. Deep blue powder dusts the "
            "wooden planks."
        ),
        "palette": "deep blue-black and iridescent metallic blue, warm wood tones",
    },
    {
        "name": "cochineal",
        "art": (
            "A cactus pad covered in white cottony clusters on a workshop table, split open to "
            "reveal brilliant carmine-red cochineal insects beneath. Dried insects are being "
            "ground in a mortar nearby, releasing vivid magenta-red pigment. Carmine stains "
            "on the wooden planks."
        ),
        "palette": "brilliant carmine-red and magenta, warm wood tones",
    },
]

ACTION_CARDS = [
    {
        "name": "chalk",
        "art": (
            "A crumbling block of soft white chalk on a worn workbench, shavings and dust "
            "scattered around it. Three small piles of freshly made pigment powder sit nearby — "
            "red, yellow, and blue — each made by grinding chalk with a different raw colorant. "
            "A flat grinding stone shows streaks of all three colors."
        ),
        "palette": "soft white, with red, yellow, and blue pigment accents",
    },
    {
        "name": "cream-of-tartar",
        "art": (
            "Reddish crystalline crusts being chipped from the inside of a dark wine barrel "
            "with a small chisel in a dim workshop. The scraped crystals collect in a linen "
            "cloth below, pale pink and sparkling. Empty wine barrels are stacked high in "
            "the background, an endless supply of this useful byproduct."
        ),
        "palette": "reddish-pink crystals, dark wood tones, and pale sparkling whites",
    },
    {
        "name": "gum-arabic",
        "art": (
            "Amber-golden lumps of dried tree resin spread on a workbench, some already ground "
            "to a fine powder in a stone mortar. A craftsman presses the sticky powder into a "
            "wooden mold alongside concentrated dye, forming a dense colored block. Finished "
            "blocks in orange, green, and purple dry on a shelf behind."
        ),
        "palette": "amber-golden resin, warm honey tones",
    },
    {
        "name": "potash",
        "art": (
            "A coarse grey-white powder being scooped from a heavy burlap sack with a wooden "
            "ladle, clouds of fine dust rising in the workshop air. Three dye vats stand in a "
            "row behind, each receiving a measure. A brick kiln for burning wood to ash smolders "
            "in the courtyard beyond the door."
        ),
        "palette": "coarse grey-white, warm earth tones, and muted browns",
    },
]


# ── Prompt builders ─────────────────────────────────────────────────────────

def build_dye_prompt(card):
    return (
        "Using the attached reference image as your style guide, create a card illustration "
        "in the EXACT same painterly style — same gouache/watercolor technique, same warm "
        "lighting, same level of detail, same full-bleed composition filling the entire canvas. "
        f"The card is {WIDTH}x{HEIGHT} pixels (portrait, 5:7 aspect ratio).\n\n"
        f"SCENE: {card['art']}\n\n"
        f"COLOR PALETTE: {card['palette']}\n\n"
        "STYLE (match the reference exactly):\n"
        "- Rich painterly illustration with visible brushstrokes, gouache/watercolor feel\n"
        "- Warm, bright lighting — light tan/cream/parchment background tone like the reference\n"
        "- Renaissance Venice dye workshop setting\n"
        "- Full-bleed: the art fills the ENTIRE canvas edge to edge, no white borders or margins\n"
        "- The wooden workbench/table surface should be visible as in the reference\n"
        "- Rich saturated colors for the subject, warm earth tones for the surroundings\n\n"
        "CRITICAL:\n"
        "- Do NOT include any text, letters, words, title, or typography\n"
        "- Do NOT include any white rounded rectangles, pill shapes, or overlay boxes\n"
        "- Do NOT include any UI elements, icons, or symbols\n"
        "- Just the pure illustration filling the entire card, edge to edge"
    )


def build_action_prompt(card):
    return (
        "Using the attached reference image as your style guide, create a card illustration "
        "in the EXACT same painterly style — same dark chiaroscuro mood, same gouache/watercolor "
        "technique, same dramatic lighting, same full-bleed composition. "
        f"The card is {WIDTH}x{HEIGHT} pixels (portrait, 5:7 aspect ratio).\n\n"
        f"SCENE: {card['art']}\n\n"
        f"COLOR PALETTE: {card['palette']}\n\n"
        "STYLE (match the reference exactly):\n"
        "- Rich painterly illustration with visible brushstrokes, gouache/watercolor feel\n"
        "- DARK chiaroscuro background — deep blacks, dark blues, and warm shadows\n"
        "- Dramatic focused lighting like a Caravaggio painting, warm golden glow on the subject\n"
        "- Renaissance Venice workshop setting\n"
        "- Full-bleed: the dark background fills the ENTIRE canvas edge to edge\n"
        "- The subject emerges dramatically from the darkness\n\n"
        "CRITICAL:\n"
        "- Do NOT include any text, letters, words, title, or typography\n"
        "- Do NOT include any white rounded rectangles, pill shapes, or overlay boxes\n"
        "- Do NOT include any gold/olive brush strokes on the sides\n"
        "- Do NOT include any UI elements, icons, or symbols\n"
        "- Just the pure illustration filling the entire card, edge to edge\n"
        "- The ENTIRE background must be dark — no white space anywhere"
    )


# ── Generation logic ────────────────────────────────────────────────────────

def load_ref_image(path):
    """Load a reference image as a genai Part."""
    mime = "image/jpeg" if path.endswith(".jpg") else "image/png"
    with open(path, "rb") as f:
        return types.Part.from_bytes(data=f.read(), mime_type=mime)


def generate_card(client, ref_part, prompt, output_path):
    """Generate a single card image. Returns True on success."""
    for attempt in range(2):
        time.sleep(RATE_LIMIT)
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[ref_part, prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    mime = getattr(part.inline_data, "mime_type", "")
                    if mime.startswith("image/") or part.inline_data.data:
                        img = Image.open(BytesIO(part.inline_data.data))
                        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        img.save(output_path, "PNG")
                        return True

            if attempt == 0:
                print(f"    No image in response, retrying in 10s...")
                time.sleep(10)
            else:
                print(f"    No image after retry")
                return False

        except Exception as e:
            if attempt == 0:
                print(f"    Error: {e}, retrying in 10s...")
                time.sleep(10)
            else:
                print(f"    Error after retry: {e}")
                return False

    return False


def main():
    if not API_KEY:
        print("ERROR: Set GOOGLE_API_KEY environment variable")
        sys.exit(1)

    client = genai.Client(api_key=API_KEY)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load reference images
    print("Loading style references...")
    dye_ref = load_ref_image(DYE_REF)
    action_ref = load_ref_image(ACTION_REF)

    total = len(DYE_CARDS) + len(ACTION_CARDS)
    done = 0
    failed = []

    # Generate dye cards
    print(f"\n=== Dye Cards ({len(DYE_CARDS)}) ===")
    for card in DYE_CARDS:
        done += 1
        out_path = os.path.join(OUTPUT_DIR, f"{card['name']}.png")
        if os.path.exists(out_path):
            print(f"[{done}/{total}] {card['name']} — already exists, skipping")
            continue

        print(f"[{done}/{total}] Generating {card['name']}...")
        prompt = build_dye_prompt(card)
        ok = generate_card(client, dye_ref, prompt, out_path)
        if ok:
            print(f"    ✓ Saved: {out_path}")
        else:
            print(f"    ✗ FAILED: {card['name']}")
            failed.append(card["name"])

    # Generate action cards
    print(f"\n=== Action Cards ({len(ACTION_CARDS)}) ===")
    for card in ACTION_CARDS:
        done += 1
        out_path = os.path.join(OUTPUT_DIR, f"{card['name']}.png")
        if os.path.exists(out_path):
            print(f"[{done}/{total}] {card['name']} — already exists, skipping")
            continue

        print(f"[{done}/{total}] Generating {card['name']}...")
        prompt = build_action_prompt(card)
        ok = generate_card(client, action_ref, prompt, out_path)
        if ok:
            print(f"    ✓ Saved: {out_path}")
        else:
            print(f"    ✗ FAILED: {card['name']}")
            failed.append(card["name"])

    # Summary
    print(f"\n=== Done ===")
    print(f"Generated: {total - len(failed)}/{total}")
    if failed:
        print(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
