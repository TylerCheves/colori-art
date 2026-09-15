# Colori — Card Art Generation Pipeline

This repository generates the card art for **Colori**, a board game about the
Renaissance Venice dye trade. The pipeline combines Google's Nano Banana Pro
image generation API with Pillow-based compositing to produce 123 unique card
faces at print-ready resolution (750×1050px, 2.5×3.5in @ 300 DPI).

## What it produces

| Card type | Count | Visual style |
|-----------|-------|--------------|
| Dye       | 39    | White watercolor vignette |
| Action    | 12    | Dark chiaroscuro |
| Material  | 18    | Varies by material |
| Buyer     | 54    | Gold / ornate |
| **Total** | **123** | |

Fifteen dye cards and five action cards are artwork only: their abilities are
not yet modeled, so only their generated backgrounds are meaningful.

Final art is written to `for-colori-web-app/` for consumption by the game
client.

## Setup

```bash
pip install -e .
export GOOGLE_API_KEY="<your-key>"
```

Dependencies (`pyproject.toml`): `google-genai`, `Pillow`, `pyyaml`.

## Running the pipeline

```bash
# Run every step end-to-end
python -m generate_cards

# Run a single step
python -m generate_cards base-backgrounds
python -m generate_cards artwork
python -m generate_cards compose
python -m generate_cards enhance
python -m generate_cards touchup
python -m generate_cards layout
python -m generate_cards export

# Filters and options (work on any step or the full pipeline)
python -m generate_cards compose --type dye
python -m generate_cards compose --cards kermes woad
python -m generate_cards enhance --strength 0.7
python -m generate_cards --force --dry-run
```

Every step skips outputs that already exist unless `--force` is passed. On
failure, the CLI prints a ready-to-paste re-run command scoped to the failed
cards.

## Pipeline stages

```
base-backgrounds → artwork → compose → enhance (dye) → touchup → layout → export
```

1. **`base-backgrounds`** — Generates 3 base textures (one per card type) with
   no reference image. Output: `generate_cards/backgrounds/base/{dye,action,material}.png`.
2. **`artwork`** — Generates the per-card subject artwork. Each piece is
   centered with edges that fade to white so it can be composited over the
   base texture. Output: `generate_cards/backgrounds/artwork/{type}/{name}.png`.
3. **`compose`** — Pillow composites the base texture, artwork, pigment icons,
   material icons, coin cost, and card text into the finished card. Buyer
   cards skip the first two steps because their backgrounds live in
   `backgrounds/project/`. Output: `generate_cards/composed/{type}/{name}.png`.
4. **`enhance`** (dye only) — Applies a saturation boost and color wash tuned
   per-card to push the dye colors. Controlled by `--strength` (0.0–1.0,
   default 0.45). Output: `generate_cards/enhanced/dye/{name}.png`.
5. **`touchup`** (dye/action/material) — Sends the composed card back through
   the image API to convert the typography into a handwritten Venetian style.
   Output: `generate_cards/touchup/{type}/{name}.png`.
6. **`layout`** — Tiles finished cards 3×3 onto print sheets in
   `generate_cards/print/`.
7. **`export`** — Copies the best available version of each card (touchup →
   enhanced → composed) plus pigment/material icons into
   `for-colori-web-app/`.

## Repository layout

```
colori-art/
  cards.yaml                   # Reference only — NOT loaded; see generate_cards/card_data.py
  pyproject.toml
  for-colori-web-app/          # Exported final art
  generate_cards/
    __main__.py                # CLI + pipeline orchestration
    card_data.py               # Card definitions, paths, constants
    api.py                     # Gemini API wrapper (rate limiting, retry)
    prompts.py                 # Prompt templates for backgrounds / artwork / touchup
    rendering.py               # Shared Pillow helpers (panels, icons, text)
    compose_dye.py             # Per-type composition
    compose_action.py
    compose_material.py
    compose_buyer.py
    compose_buyaction.py       # Buy action punchboard tiles (2in x 1in)
    enhance_dye_colors.py      # Saturation + color wash
    layout.py                  # Print sheet tiling
    iconography/               # Checked-in icon assets
      pigments/                #   Color pigment icons
    backgrounds/
      base/                    # AI-generated base textures (3 total)
      artwork/                 # AI-generated per-card artwork
      project/                 # Buyer card backgrounds
    composed/                  # Finished cards (pre-enhancement)
    enhanced/                  # Color-boosted dye cards
    touchup/                   # API typography pass
    print/                     # Print layout sheets
```

## Configuration notes

- **Card size:** 750×1050px (5:7 aspect at 300 DPI).
- **Image model:** `gemini-3-pro-image` via the `google-genai` SDK; the
  typography touchup pass uses `gemini-3.1-flash-image`.
- **Generation aspect ratio:** `2:3` — the API offers no 5:7 option, so
  backgrounds and artwork are generated at 2:3 and saved uncropped. Crop to
  5:7 before composing; `compose` stretches anything that isn't already 5:7.
- **API behavior:** 5-second pause between calls, 1 retry on failure.
- **Card naming:**
  - Dye/Action/Material: `{card-name}.png` (e.g. `kermes.png`, `alum.png`).
  - Buyer: `{color(s)}-{material}.png` (e.g. `vermilion-textile.png`,
    `amber-blue-ceramic.png`).

## Extra utilities

- `buyaction` step (`python -m generate_cards buyaction [--compose-only]`)
  generates 2in×1in buy action punchboard tiles. `--compose-only` saves the
  icon-only reference without calling the API.
- Top-level scripts `blend_*.py` and `gen_*.py` are one-off experiments /
  drafts from earlier iterations — the supported entry point is
  `python -m generate_cards`.

## Source of truth

- **Game logic** (abilities, costs, deck composition): the Colori web app repo
  (`colori/src/data/cards.ts`).
- **Art pipeline** (names, prompts, copy counts, visual styling):
  `generate_cards/card_data.py`. `cards.yaml` mirrors it as a design
  reference but is not loaded by any code and has drifted from it.
  in this repo.
