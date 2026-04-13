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
| **Dye** | 18 (3 starter + 3 primary + 6 secondary + 6 tertiary) | White watercolor vignette |
| **Action** | 9 (chalk starter + alum, cream-of-tartar, gum-arabic, potash, vinegar, linseed-oil, lye, sal-ammoniac) | Dark chiaroscuro |
| **Material** | 18 (3 starter + 15 draft) | TBD |
| **Buyer** | 54 (18 textile 2-star + 18 ceramic 3-star + 18 painting 4-star) | Gold/ornate |
| **Total** | **99 unique card faces** | |

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
  cards.yaml                   # Card data — names, abilities, art descriptions, copy counts
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

- **Image generation model:** `nano-banana-pro-preview` (google-genai SDK)
- **API key env var:** `GOOGLE_API_KEY`
- **Card size:** 750x1050px (2.5x3.5in @ 300 DPI, 5:7 aspect ratio)
- **Rate limiting:** 5-second pause between API calls, 1 retry on failure

## Card Naming

- **Dye/Action/Material:** `{card-name}.png` (e.g., `kermes.png`, `alum.png`)
- **Buyer:** `{color(s)}-{material}.png` (e.g., `vermilion-textile.png`, `amber-blue-ceramic.png`)

## Source of Truth

- **Game logic:** `/Users/tylercheves/lgr/colori/src/data/cards.ts`
- **Art pipeline:** `cards.yaml` (this repo)
