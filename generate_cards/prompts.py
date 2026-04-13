"""Prompt templates for Gemini API background generation and touchup."""

# ── Shared style blocks ──────────────────────────────────────────────────────

DYE_STYLE_BLOCK = (
    "STYLE (match the reference image exactly):\n"
    "- Authentic watercolor painting technique -- wet-on-wet washes, pigment blooms, soft bleeding edges, "
    "visible water stains, and areas where color pools and dries with granulation\n"
    "- The painting should look like it was done on textured watercolor paper with visible paper grain\n"
    "- Loose, flowing brushwork -- not tight or digital-looking\n"
    "- Warm golden light, Renaissance Venice workshop setting\n"
    "- NO border, NO frame -- the watercolor painting bleeds to every edge\n"
    "\n"
    "LAYOUT:\n"
    "- Compose the scene so the TOP and LEFT SIDE naturally have faded whitespace -- "
    "like a watercolor vignette where the pigment thins out and white paper shows through. "
    "The left side should have generous open space, especially the bottom-left.\n"
    "- Position the main subject LOW and to the RIGHT -- the centerpiece of the artwork should "
    "sit in the lower-right area of the card, not centered\n"
    "- Full bleed -- no border or frame\n"
    "\n"
    "CRITICAL: Do NOT include any text, letters, numbers, words, or symbols anywhere on the card. "
    "Purely artistic -- only illustration and decorative elements."
)

ACTION_STYLE_BLOCK = (
    "STYLE (match the reference image's dark, moody watercolor style exactly):\n"
    "- Authentic watercolor painting technique -- wet-on-wet washes, pigment blooms, soft bleeding edges, "
    "visible water stains, and areas where color pools and dries with granulation\n"
    "- CRITICAL: The entire background is a deep, dark wash -- "
    "rich burnt umber, charcoal brown, and deep warm shadows filling the ENTIRE card edge to edge. "
    "The dark wash covers every inch of the card. No white paper visible anywhere.\n"
    "- The subject emerges from this darkness like a Caravaggio painting rendered in watercolor.\n"
    "- Light sources are dramatic and focused -- warm golden candlelight or furnace glow illuminating "
    "the central subject while the surroundings fall into deep shadow\n"
    "- The painting should still look like watercolor (visible brushwork, pigment granulation, soft edges) "
    "but on a dark-washed ground rather than white paper\n"
    "- Loose, flowing brushwork -- not tight or digital-looking\n"
    "- Warm golden light, Renaissance Venice workshop setting, chiaroscuro mood\n"
    "- NO border, NO frame -- the dark watercolor wash bleeds to every edge\n"
    "\n"
    "LAYOUT:\n"
    "- The dark wash covers the ENTIRE card edge to edge -- no white paper anywhere\n"
    "- Compose the scene so the TOP and LEFT SIDE naturally have just dark atmospheric wash -- "
    "the scene detail fades into shadow in those areas. "
    "The left side should have generous open space, especially the bottom-left.\n"
    "- Position the main subject LOW and to the RIGHT -- the centerpiece of the artwork should "
    "sit in the lower-right area of the card, not centered\n"
    "\n"
    "CRITICAL: Do NOT include any text, letters, numbers, words, or symbols anywhere on the card. "
    "Purely artistic -- only illustration and decorative elements. No border or frame. "
    "The dark wash must reach every edge of the card -- NO white paper."
)

BUYER_STYLE_BLOCK = (
    "STYLE -- match the reference image EXACTLY:\n"
    "- Reproduce the EXACT same golden watercolor wash, ornate edge filigree, and background design\n"
    "- Reproduce the EXACT same central artwork composition and material objects -- "
    "same shapes, same arrangement, same level of detail\n"
    "- The ONLY difference from the reference should be the COLOR of the watercolor splashes/blooms\n"
    "- Authentic watercolor painting technique -- wet-on-wet washes, pigment blooms, soft bleeding edges\n"
    "- Textured watercolor paper with visible paper grain\n"
    "- Loose, flowing brushwork -- not tight or digital-looking\n"
    "- Warm golden light throughout\n"
    "- NO border, NO frame -- the golden watercolor wash bleeds to every edge\n"
    "\n"
    "LAYOUT -- match the reference image EXACTLY:\n"
    "- Same ornamental edge flourishes as the reference\n"
    "- Same centered, compact composition as the reference\n"
    "- TOP 20%: Just golden wash and ornamental edge design -- no detailed objects\n"
    "- BOTTOM-LEFT: Golden wash with minimal detail\n"
    "\n"
    "CRITICAL: Do NOT include any text, letters, numbers, words, or symbols anywhere on the card. "
    "Purely artistic -- only illustration and decorative elements. No border or frame."
)


MATERIAL_STYLE_BLOCK = (
    "STYLE:\n"
    "- Warm parchment-toned watercolor painting -- aged paper feel with sepia, ochre, and cream tones\n"
    "- Authentic watercolor technique -- wet-on-wet washes, pigment blooms, soft bleeding edges, "
    "visible water stains, and areas where color pools and dries with granulation\n"
    "- Textured watercolor paper with visible paper grain\n"
    "- Loose, flowing brushwork -- not tight or digital-looking\n"
    "- Warm golden light, Renaissance Venice workshop setting\n"
    "- NO border, NO frame -- the watercolor painting bleeds to every edge\n"
    "\n"
    "LAYOUT:\n"
    "- Compose the scene so the TOP and LEFT SIDE naturally have faded whitespace -- "
    "like a watercolor vignette where the pigment thins out and warm parchment shows through. "
    "The left side should have generous open space, especially the bottom-left.\n"
    "- Position the main subject LOW and to the RIGHT -- the centerpiece of the artwork should "
    "sit in the lower-right area of the card, not centered\n"
    "- Full bleed -- no border or frame\n"
    "\n"
    "CRITICAL: Do NOT include any text, letters, numbers, words, or symbols anywhere on the card. "
    "Purely artistic -- only illustration and decorative elements."
)

MATERIAL_ART = {
    "ceramic": (
        "A Venetian ceramics workshop -- a brick kiln with an arched opening glowing orange with heat, "
        "shelves of glazed maiolica tiles and bowls climbing the wall, a potter's wheel with a half-formed vase "
        "at the base. Clay dust and terracotta tones dominate, with splashes of colorful glaze."
    ),
    "painting": (
        "A Renaissance painter's studio -- a tall easel with a blank empty canvas, stretched canvases "
        "leaning against walls, jars of ground pigment in brilliant colors, linseed oil bottles, "
        "and sable brushes fanned out on a marble palette. Golden afternoon light streams in. "
        "The scene should fill the right side of the card from bottom to top."
    ),
    "textile": (
        "A Venetian weaving workshop -- a compact wooden loom with partially woven fabric, "
        "skeins of dyed wool and silk thread hanging from pegs, spindles and bobbins on a small workbench. "
        "Bolts of finished fabric in rich colors lean against each other."
    ),
}


# ── Base background prompts (texture only, no subjects) ──────────────────────

BASE_BG_PROMPTS = {
    "dye": (
        "Create a plain watercolor paper texture filling the entire image. "
        "White watercolor paper with subtle cream undertones and visible paper grain. "
        "No subject, no objects, no illustration -- ONLY paper texture. "
        "Soft variations in the white/cream tone as if water has been lightly washed across the surface "
        "and dried, leaving faint tide marks and subtle tonal shifts. "
        "The texture should look like high-quality cold-pressed watercolor paper. "
        "The image is 2.5 inches wide by 3.5 inches tall (portrait, 5:7 aspect ratio). "
        "CRITICAL: No text, no objects, no borders -- pure paper texture only."
    ),
    "action": (
        "Create a dark, moody watercolor wash texture filling the entire image edge to edge. "
        "Deep burnt umber, charcoal brown, and warm dark shadows covering every inch. "
        "No subject, no objects, no illustration -- ONLY dark wash texture. "
        "Subtle variations in the dark tones -- areas where pigment pooled darker, "
        "visible brushwork texture, granulation in the wash. "
        "Like a sheet of paper that has been entirely covered with dark watercolor paint. "
        "The image is 2.5 inches wide by 3.5 inches tall (portrait, 5:7 aspect ratio). "
        "CRITICAL: No text, no objects, no borders -- pure dark wash texture only. "
        "No white paper visible anywhere."
    ),
    "material": (
        "Create a warm parchment texture filling the entire image. "
        "Warm yellowed parchment paper with an aged, rougher texture feel. "
        "No subject, no objects, no illustration -- ONLY parchment texture. "
        "Subtle sepia and ochre tonal variations, faint staining as if from age, "
        "visible paper fiber texture. Like an old document or manuscript page. "
        "The image is 2.5 inches wide by 3.5 inches tall (portrait, 5:7 aspect ratio). "
        "CRITICAL: No text, no objects, no borders -- pure parchment texture only."
    ),
}


# ── Artwork prompts (centered subject, fades to edges) ───────────────────────

def artwork_dye_prompt(card):
    """Build artwork generation prompt for a dye card -- centered subject fading to white."""
    return (
        f"Create a watercolor illustration of the following subject, CENTERED in the image. "
        f"The card is 2.5 inches wide by 3.5 inches tall (portrait, 5:7 aspect ratio).\n\n"
        f"SUBJECT: {card['art']}\n\n"
        f"Dominant colors: {card['bg_color']} watercolor pigments\n\n"
        f"STYLE:\n"
        f"- Authentic watercolor painting -- wet-on-wet washes, pigment blooms, soft bleeding edges\n"
        f"- Loose, flowing brushwork -- not tight or digital-looking\n"
        f"- Warm golden light, Renaissance Venice workshop setting\n\n"
        f"CRITICAL LAYOUT:\n"
        f"- The subject must be CENTERED in the image\n"
        f"- The watercolor painting MUST fade to pure white on ALL four edges\n"
        f"- The edges should be bare white paper -- a natural watercolor vignette\n"
        f"- The richest detail and color is in the CENTER, thinning out organically in every direction\n"
        f"- No hard edges -- the pigment dissolves naturally into white paper\n\n"
        f"CRITICAL: No text, letters, numbers, words, or symbols. No border or frame. "
        f"The background MUST be white/transparent at all edges."
    )


def artwork_action_prompt(card):
    """Build artwork generation prompt for an action card -- subject on dark background."""
    return (
        f"Create a dark, moody watercolor illustration of the following subject, "
        f"CENTERED in the image. "
        f"The card is 2.5 inches wide by 3.5 inches tall (portrait, 5:7 aspect ratio).\n\n"
        f"SUBJECT: {card['art']}\n\n"
        f"Dominant colors: {card['bg_color']} watercolor pigments emerging from deep shadow\n\n"
        f"STYLE:\n"
        f"- Dark watercolor chiaroscuro -- the subject emerges from deep shadow\n"
        f"- The ENTIRE background is a deep dark wash: burnt umber, charcoal brown, warm shadows\n"
        f"- The dark wash covers every inch of the image edge to edge -- no white paper anywhere\n"
        f"- Warm golden candlelight or furnace glow illuminating the central subject\n"
        f"- Loose, flowing brushwork, visible pigment granulation\n\n"
        f"CRITICAL LAYOUT:\n"
        f"- The subject must be CENTERED in the image\n"
        f"- The dark wash MUST cover the ENTIRE image edge to edge\n"
        f"- The subject fades into deep shadow on ALL four edges\n"
        f"- No white paper visible ANYWHERE -- pure dark wash at all edges\n\n"
        f"CRITICAL: No text, letters, numbers, words, or symbols. No border or frame. "
        f"The background MUST be dark at all edges."
    )


def artwork_material_prompt(bg_type):
    """Build artwork generation prompt for a material card -- centered subject on white background."""
    art = MATERIAL_ART[bg_type]
    return (
        f"Create a watercolor illustration of the following subject, CENTERED in the image. "
        f"The card is 2.5 inches wide by 3.5 inches tall (portrait, 5:7 aspect ratio).\n\n"
        f"SUBJECT: {art}\n\n"
        f"Dominant colors: warm sepia, ochre, cream, and parchment tones\n\n"
        f"STYLE:\n"
        f"- Authentic watercolor painting -- wet-on-wet washes, pigment blooms, soft edges\n"
        f"- Loose, flowing brushwork -- not tight or digital-looking\n"
        f"- Warm golden light, Renaissance Venice workshop setting\n\n"
        f"CRITICAL LAYOUT:\n"
        f"- The subject must be CENTERED in the image\n"
        f"- The watercolor painting MUST fade to pure white on ALL four edges\n"
        f"- The edges should be bare white paper -- a natural watercolor vignette\n"
        f"- The richest detail is in the CENTER, thinning out organically in every direction\n"
        f"- No hard edges -- the pigment dissolves naturally into white paper\n\n"
        f"CRITICAL: No text, letters, numbers, words, or symbols. No border or frame. "
        f"The background MUST be white at all edges."
    )


# ── Color and material maps for buyer prompts ────────────────────────────────

COLOR_MAP = {
    "vermilion": "brilliant orange-red vermilion",
    "amber": "warm golden amber",
    "chartreuse": "bright yellow-green chartreuse",
    "teal": "deep blue-green teal",
    "indigo": "deep blue-black indigo",
    "magenta": "vivid carmine magenta",
    "orange": "warm burnt orange",
    "green": "rich emerald green",
    "purple": "deep violet purple",
    "red": "deep crimson red",
    "yellow": "warm golden yellow",
    "blue": "rich cerulean blue",
}


# ── Prompt builders ──────────────────────────────────────────────────────────

def dye_prompt(card):
    """Build background generation prompt for a dye card."""
    return (
        f"Using the attached reference image as your style guide, create a trading card illustration "
        f"in the EXACT same watercolor painting style, composition, and layout. "
        f"The card is 2.5 inches wide by 3.5 inches tall (portrait orientation, 5:7 aspect ratio). "
        f"\n\n"
        f"SCENE: {card['art']}\n\n"
        f"Dominant color palette: {card['bg_color']} watercolor pigments\n\n"
        f"{DYE_STYLE_BLOCK}"
    )


def action_prompt(card):
    """Build background generation prompt for an action card."""
    return (
        f"Using the attached reference image as your style guide, create a trading card illustration "
        f"in the EXACT same dark, moody watercolor painting style, composition, and layout. "
        f"The card is 2.5 inches wide by 3.5 inches tall (portrait orientation, 5:7 aspect ratio). "
        f"\n\n"
        f"SCENE: {card['art']}\n\n"
        f"Dominant color palette: {card['bg_color']} watercolor pigments emerging from deep shadow\n\n"
        f"{ACTION_STYLE_BLOCK}"
    )


def material_prompt(bg_type):
    """Build background generation prompt for a material card."""
    art = MATERIAL_ART[bg_type]
    return (
        f"Using the attached reference image as your style guide, create a trading card illustration "
        f"in a warm parchment-toned watercolor painting style. "
        f"The card is 2.5 inches wide by 3.5 inches tall (portrait orientation, 5:7 aspect ratio). "
        f"\n\n"
        f"SCENE: {art}\n\n"
        f"Dominant color palette: warm sepia, ochre, cream, and parchment tones\n\n"
        f"{MATERIAL_STYLE_BLOCK}"
    )


def buyer_prompt(card_name):
    """Build background generation prompt for a buyer/project card."""
    parts = card_name.split("-")
    material = parts[-1]
    colors = parts[:-1]
    color_descriptions = [COLOR_MAP.get(c, c) for c in colors]

    if len(color_descriptions) == 1:
        splash_text = f"bold splashes and blooms of {color_descriptions[0]} watercolor pigment"
    else:
        splash_text = " and ".join(
            [f"splashes of {c} watercolor pigment" for c in color_descriptions]
        )

    return (
        f"Using the attached reference image, create a trading card illustration that is "
        f"IDENTICAL to the reference in every way -- same golden background, same ornate edge design, "
        f"same central artwork -- EXCEPT change the color of the watercolor splashes/blooms. "
        f"The card is 2.5 inches wide by 3.5 inches tall (portrait orientation, 5:7 aspect ratio).\n\n"
        f"COLOR CHANGE: Replace the color splashes in the reference with {splash_text}. "
        f"The colored blooms should pool around and bleed into the raw materials in the center, "
        f"as if dyes have just been laid out alongside the craft supplies.\n\n"
        f"{BUYER_STYLE_BLOCK}"
    )


def touchup_dye_prompt(card):
    """Build touchup prompt for a dye card."""
    return f"""Edit this card image with one specific change. The card is 750x1050px portrait.

CHANGE -- HAND-PAINTED CALLIGRAPHIC TITLE:
In the top-right corner, there is the word "{card['title']}" in a digital serif font. Re-render this text as hand-painted watercolor calligraphy in the style of a Renaissance Venetian chancery italic hand, as if painted with a pointed sable brush and slightly diluted watercolor paint. The lettering should have:
- Slightly uneven baselines and natural variation in stroke width (thicker on downstrokes, thinner on cross-strokes)
- Subtle pigment pooling where the brush paused, and lighter areas where paint thinned
- The same {card.get('touchup_color_desc', 'matching')} color palette as the current text
- Scale the lettering to fit comfortably in the top-right corner, adjusting size to the word length
- Use the same lettering style as all other cards in this set -- consistent calligraphic character

PRESERVE -- DO NOT CHANGE:
- The central watercolor artwork, composition, and colors
- All icons, symbols, numbers, and their exact positions
- The background areas behind icon groups -- keep them exactly as they are
- The card dimensions (750x1050px portrait)
- The overall color palette and mood

COHESION:
The final card should feel like a unified watercolor artwork created by a single artist in one session -- the calligraphic title and the central painting should feel like they belong together as one cohesive piece."""


def touchup_action_prompt(card):
    """Build touchup prompt for an action card."""
    return f"""Edit this card image with one specific change. The card is 750x1050px portrait with a dark, moody chiaroscuro watercolor background.

CHANGE -- HAND-PAINTED CALLIGRAPHIC TITLE:
In the top-right corner, there is the word "{card['title']}" in white digital text. Re-render this text as hand-painted watercolor calligraphy in the style of a Renaissance Venetian chancery italic hand, as if painted with a pointed sable brush using white/cream watercolor paint on dark paper. The lettering should have:
- Slightly uneven baselines and natural variation in stroke width
- Subtle paint pooling where the brush paused, with areas where the white paint thins to reveal the dark background beneath
- Keep the WHITE/CREAM color -- this is a dark card, the text must remain light
- Scale the lettering to fit comfortably in the top-right corner, adjusting size to the word length
- Use the same lettering style as all other cards in this set -- consistent calligraphic character

PRESERVE -- DO NOT CHANGE:
- The central artwork, dark background wash, and moody atmosphere
- All icons, numbers, and symbols exactly as they appear -- do NOT reinterpret any number or icon
- The background areas behind icon groups -- keep them exactly as they are
- The card dimensions (750x1050px portrait)

COHESION:
The final card should feel like a unified dark watercolor artwork -- the calligraphic white title and the chiaroscuro painting should feel painted by the same hand."""


def touchup_material_prompt(card):
    """Build touchup prompt for a material card."""
    return f"""Edit this card image with one specific change. The card is 750x1050px portrait with a warm parchment-toned watercolor background.

CHANGE -- HAND-PAINTED CALLIGRAPHIC TITLE:
In the top-right corner, there is the word "{card['title']}" in a digital serif font. Re-render this text as hand-painted watercolor calligraphy in the style of a Renaissance Venetian chancery italic hand, as if painted with a pointed sable brush and warm brown watercolor paint. The lettering should have:
- Slightly uneven baselines and natural variation in stroke width
- Subtle pigment pooling where the brush paused, and lighter areas where paint thinned
- Keep the warm brown color palette
- Scale the lettering to fit comfortably in the top-right corner, adjusting size to the word length
- Use the same lettering style as all other cards in this set -- consistent calligraphic character

PRESERVE -- DO NOT CHANGE:
- The central artwork, warm background, and composition
- All icons, numbers, and symbols exactly as they appear
- The background areas behind icon groups -- keep them exactly as they are
- The card dimensions (750x1050px portrait)

COHESION:
The final card should feel like a unified warm watercolor artwork on aged parchment -- the calligraphic title and the central painting should feel like one cohesive piece."""


def touchup_buyer_prompt(card):
    """Build touchup prompt for a buyer card.

    Note: Buyer cards have no title text, so touchup is minimal.
    """
    return f"""This card image is 750x1050px portrait with a golden watercolor background.

The card is already complete. Output the image unchanged -- do NOT modify any icons, artwork, golden background, ornate filigree edges, or any other element. Every colored square, circle, coin, and symbol must remain pixel-perfect.

Output must be EXACTLY 750x1050 pixels."""
