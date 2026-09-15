# Colori - Card Generation Pipeline

## Project

Board game card generator for Colori (Renaissance Venice dye trade). Uses Google's Nano Banana Pro API to generate watercolor card art, Pillow for card composition, and Nano Banana 2 for finishing touches (typography + icon section design).

## Quick Start

```bash
pip install -e .
export GOOGLE_API_KEY="AIzaSyAzVe44HEWckQJnZAjCHL4m4g_fqu_HFqg"

# Run the full pipeline
python -m generate_cards

# Run specific steps
python -m generate_cards base-backgrounds
python -m generate_cards artwork
python -m generate_cards compose
python -m generate_cards enhance            # dye cards only
python -m generate_cards layout
python -m generate_cards export

# Filter by card type or specific cards
python -m generate_cards compose --cards kermes woad
python -m generate_cards enhance --strength 0.7
python -m generate_cards --force --dry-run
```

## Card Counts

| Type | Count | Style |
|------|-------|-------|
| **Dye** | 24 (3 starter + 3 pure primary + 6 mixed primary + 6 secondary + 6 tertiary) | White watercolor vignette |
| **Pigment** | 8 mineral/resin (artwork only, no tier assigned) | White watercolor vignette |
| **Ingredient dye** | 7: iris, alkanet, buckthorn, lye, sinopia, giallorino, cornflower (artwork only) | White watercolor vignette |
| **Action** | 13 (chalk starter + alum, cream-of-tartar, gum-arabic, potash, vinegar, linseed-oil, sal-ammoniac, rubified-vitriol, green-vitriol, wine-lees, borax, quicksilver) | Dark chiaroscuro |
| **Material** | 18 (3 starter + 15 draft) | TBD |
| **Buyer** | 54 (18 textile 2-star + 18 ceramic 3-star + 18 painting 4-star) | Gold/ornate |
| **Total** | **124 unique card faces** | |

## Pipeline

**Dye / Action / Material cards** use a two-layer background approach:
1. `base-backgrounds` — generates 3 base textures (one per type, no reference image)
2. `artwork` — generates per-card subject artwork (centered, edges fade to white)
3. `compose` — composites base + artwork + icons + text via Pillow

**Buyer cards** have pre-generated backgrounds in `backgrounds/project/` and go straight to compose, which layers pigment icons, material icon, and coin cost on top.

After composition, all card types share the same finishing steps:
- `enhance` — (dye only) saturation boost + color wash via Pillow
- `layout` — tiles cards 3x3 onto print sheets
- `export` — copies card art + icons to `for-colori-web-app/`

```
base-backgrounds → artwork → compose → enhance (dye only) → layout → export
```

## Directory Structure

```
colori-art/
  cards.yaml                   # Reference only — NOT loaded; see card_data.py
  pyproject.toml               # Dependencies: google-genai, Pillow, pyyaml
  for-colori-web-app/          # Exported final art for web app
  generate_cards/
    __main__.py                #   CLI + pipeline orchestration
    card_data.py               #   Card definitions, paths, constants
    api.py                     #   Gemini API wrapper (rate limiting, retry)
    rendering.py               #   Shared Pillow helpers (cloud panels, icons, text)
    compose_dye.py             #   Dye card composition
    compose_action.py          #   Action card composition
    compose_buyer.py           #   Buyer card composition
    compose_material.py        #   Material card composition
    enhance_dye_colors.py      #   Dye color enhancement (saturation + wash)
    prompts.py                 #   AI prompt templates for background/artwork generation
    layout.py                  #   Print layout tiling
    iconography/               #   Icon assets (checked in)
      discard.png, arrow.png, project.png, workshop.png, mix.png, coin.png, ...
      pigments/                #     Color pigment icons (red-pigment.png, etc.)
    backgrounds/               #   AI-generated backgrounds
      base/                    #     Base textures (dye.png, action.png, material.png)
      artwork/                 #     Per-card artwork (dye/, action/, material/)
      project/                 #     Buyer card backgrounds (recolored from material-refs)
    composed/                  #   Finished cards (icons + text composited)
      dye/ action/ material/ buyer/
    enhanced/                  #   Color-enhanced dye cards
      dye/
    print/                     #   Print layout sheets
```

## API

- **Image generation model:** `gemini-3-pro-image` (google-genai SDK)
- **Touchup model:** `gemini-3.1-flash-image`
- **API key env var:** `GOOGLE_API_KEY`
- **Card size:** 750x1050px (2.5x3.5in @ 300 DPI, 5:7 aspect ratio)
- **Generation aspect ratio:** `2:3` — the API offers no 5:7 option, so
  backgrounds and artwork are generated at 2:3 and saved uncropped. Crop to
  5:7 before composing; `compose` stretches anything that isn't already 5:7.
- **Rate limiting:** 5-second pause between API calls, 1 retry on failure

## Card Naming

- **Dye/Action/Material:** `{card-name}.png` (e.g., `kermes.png`, `alum.png`)
- **Buyer:** `{color(s)}-{material}.png` (e.g., `vermilion-textile.png`, `amber-blue-ceramic.png`)

## Source of Truth

- **Game logic:** `/Users/tylercheves/lgr/colori/src/data/cards.ts`
- **Art pipeline:** `generate_cards/card_data.py` (this repo). `cards.yaml`
  documents the same cards but is not loaded by any code and has drifted;
  treat it as a design reference and update it by hand.
