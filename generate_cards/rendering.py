"""Shared Pillow helpers for card composition: cloud panels, icon loading, text rendering."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# Extensions tried (in order) when resolving a background/artwork input to a
# file on disk. JPG wins over PNG when both exist, so a hand-dropped JPG
# overrides the machine-generated PNG without needing to delete the PNG.
BG_EXTENSIONS = (".jpg", ".jpeg", ".png")


def find_background_image(directory, stem):
    """Return the first existing `{directory}/{stem}{ext}` path.

    Tries extensions in BG_EXTENSIONS order. Returns a Path, or None if
    no matching file exists.
    """
    directory = Path(directory)
    for ext in BG_EXTENSIONS:
        p = directory / f"{stem}{ext}"
        if p.exists():
            return p
    return None


# ── Layout constants ─────────────────────────────────────────────────────────

W, H = 750, 1050
EDGE = 32
PAD = 22
GAP_H = 12
GAP_V = 10

# Top-left icon heights (larger for prominence)
H_TOP = 105
H_ARROW = 42
# Bottom-left icon heights
H_WORK = 95
H_PIG = 78
H_COIN = 90


# ── Icon helpers ─────────────────────────────────────────────────────────────

def trim(img):
    """Trim transparent border from an RGBA image."""
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def load_icon(path, h):
    """Load an icon, trim whitespace, and resize to target height preserving aspect ratio."""
    img = trim(Image.open(path).convert("RGBA"))
    w = int(img.width * h / img.height)
    return img.resize((w, h), Image.LANCZOS)


def paste_icon(canvas, icon, pos, shadow_offset=2, shadow_blur=4,
               shadow_color=(0, 0, 0, 25)):
    """Paste an RGBA icon onto canvas with a subtle dark drop shadow.

    Args:
        canvas: PIL Image (RGBA) to paste onto (modified in place).
        icon: PIL Image (RGBA) icon to paste.
        pos: (x, y) tuple for icon placement.
        shadow_offset: Pixels to offset shadow down and right.
        shadow_blur: Gaussian blur radius for shadow softness.
        shadow_color: RGBA color for the shadow.

    Returns:
        The canvas (for chaining if needed).
    """
    x, y = pos

    # Build shadow from icon's alpha channel
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", icon.size, shadow_color)
    shadow_layer.putalpha(icon.split()[3])  # use icon's alpha as shadow shape
    shadow.paste(shadow_layer, (x + shadow_offset, y + shadow_offset), shadow_layer)

    # Blur the shadow
    s_r, s_g, s_b, s_a = shadow.split()
    s_a = s_a.filter(ImageFilter.GaussianBlur(shadow_blur))
    shadow.putalpha(s_a)

    # Composite shadow then icon
    canvas = Image.alpha_composite(canvas, shadow)
    canvas.paste(icon, (x, y), icon)
    return canvas


# ── Font helpers ─────────────────────────────────────────────────────────────

def get_font(name, size):
    """Load a named font. Falls back to default if unavailable."""
    fonts = {
        "cochin-italic":  ("/System/Library/Fonts/Supplemental/Cochin.ttc", 1),
        "cochin-bi":      ("/System/Library/Fonts/Supplemental/Cochin.ttc", 3),
        "georgia-bold":   ("/System/Library/Fonts/Supplemental/Georgia Bold.ttf", 0),
        "baskerville":    ("/System/Library/Fonts/Supplemental/Baskerville.ttc", 0),
    }
    entry = fonts.get(name)
    if entry:
        try:
            return ImageFont.truetype(entry[0], size, index=entry[1])
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


def tsize(text, f):
    """Measure text dimensions (width, height) for a given font."""
    bb = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), text, font=f)
    return bb[2] - bb[0], bb[3] - bb[1]


# ── Rendering helpers ────────────────────────────────────────────────────────

def cloud_panel(c, bb, color=(255, 255, 255, 255), blur=30):
    """Render a soft cloud panel. Blurs alpha only to avoid dark fringing.

    Args:
        c: Base RGBA image to composite onto.
        bb: Bounding box tuple (x1, y1, x2, y2).
        color: RGBA tuple for the cloud color.
        blur: Gaussian blur radius for softness.
    """
    pad_inner = blur // 2
    x1, y1, x2, y2 = bb
    mask = Image.new("L", c.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [x1 + pad_inner, y1 + pad_inner, x2 - pad_inner, y2 - pad_inner],
        radius=20, fill=color[3]
    )
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    o = Image.new("RGBA", c.size, (color[0], color[1], color[2], 0))
    o.putalpha(mask)
    return Image.alpha_composite(c, o)


def add_splotch_hints(img, bounds_list, color=(255, 255, 255, 70), blur=38, pad=60):
    """Add subtle cloud panel splotch hints behind icon areas for AI touchup refinement.

    The hints are low-opacity, blurred shapes that give the AI a compositional
    guide for where to place organic watercolor washes. They need to be visible
    enough for the AI to detect across the full icon group.

    Args:
        color: RGBA tuple -- alpha around 60-80 gives the AI a clear signal.
        blur: Gaussian blur radius -- lower values keep the shape more defined.
        pad: Extra pixels to expand each bounding box outward, ensuring the
             splotch fully covers icons at the edges of the group.
    """
    for x1, y1, x2, y2 in bounds_list:
        expanded = (x1 - pad, y1 - pad, x2 + pad, y2 + pad)
        img = cloud_panel(img, expanded, color=color, blur=blur)
    return img


def draw_text(c, pos, text, f, fill):
    """Draw text onto an RGBA canvas via alpha compositing."""
    o = Image.new("RGBA", c.size, (0, 0, 0, 0))
    ImageDraw.Draw(o).text(pos, text, font=f, fill=fill)
    return Image.alpha_composite(c, o)


def draw_text_with_glow(c, pos, text, f, fill, glow_color=(255, 255, 255, 100), glow_r=6):
    """Draw text with a soft glow behind it for legibility."""
    g = Image.new("RGBA", c.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).text(pos, text, font=f, fill=glow_color)
    g = g.filter(ImageFilter.GaussianBlur(glow_r))
    c = Image.alpha_composite(c, g)
    return draw_text(c, pos, text, f, fill)


def word_wrap(text, font, max_width):
    """Word-wrap text to fit within max_width. Returns list of lines."""
    words = text.split()
    if not words:
        return []
    lines = []
    cur = words[0]
    for w in words[1:]:
        test = cur + " " + w
        tw_test, _ = tsize(test, font)
        if tw_test <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def draw_title_right_aligned(c, title, font, color, line_gap=6, **_kwargs):
    """Draw a right-aligned, word-wrapped title in the top-right corner.

    Returns the modified canvas.
    """
    max_title_w = W // 2 - 20
    lines = word_wrap(title, font, max_title_w)

    ty = EDGE + 4
    for line in lines:
        lw, lh = tsize(line, font)
        tx = W - EDGE - 30 - lw
        c = draw_text(c, (tx, ty), line, font, fill=color)
        ty += lh + line_gap
    return c


# ── Layered compositing helpers ─────────────────────────────────────────────

# Per-type tuning for artwork offset and vignette fade
COMPOSITE_PARAMS = {
    "dye":      {"offset_x": 70, "offset_y": 70, "fade_px": 120},
    "action":   {"offset_x": 60, "offset_y": 60, "fade_px": 100},
    "material": {"offset_x": 70, "offset_y": 70, "fade_px": 120},
}


def create_vignette_mask(w, h, fade_px=None, fade_left=None, fade_right=None,
                         fade_top=None, fade_bottom=None):
    """Create an L-mode vignette mask with per-side fade control.

    If only fade_px is given, all sides use that value (symmetric).
    Otherwise, per-side values override. Unset sides default to fade_px or 100.
    """
    default = fade_px if fade_px is not None else 100
    fl = fade_left if fade_left is not None else default
    fr = fade_right if fade_right is not None else default
    ft = fade_top if fade_top is not None else default
    fb = fade_bottom if fade_bottom is not None else default

    x = np.arange(w, dtype=np.float32)
    hgrad = np.clip(x / max(fl, 1), 0, 1) * np.clip((w - 1 - x) / max(fr, 1), 0, 1)

    y = np.arange(h, dtype=np.float32)
    vgrad = np.clip(y / max(ft, 1), 0, 1) * np.clip((h - 1 - y) / max(fb, 1), 0, 1)

    mask_arr = np.outer(vgrad, hgrad) * 255
    return Image.fromarray(mask_arr.astype(np.uint8), mode="L")


def white_to_alpha(img, power=2.0):
    """Convert white background to transparency using a power curve.

    Pure white → fully transparent, dark colors → fully opaque.
    Uses the minimum RGB channel (closest to white) instead of grayscale
    luminance, so light but colorful pixels (e.g. yellow washes) retain
    their opacity. A light yellow pixel like (255, 240, 100) has a low
    blue channel, so it stays opaque; a near-white pixel like (250, 250, 248)
    has all channels high, so it becomes transparent as expected.

    power=1.0: linear (aggressive — light washes become very transparent)
    power=2.0: quadratic (default — light washes stay visible)
    power=3.0: cubic (preserves even the lightest washes)
    """
    img = img.convert("RGBA")
    arr = np.array(img).astype(np.float32)
    # Use the minimum channel distance from white: pixels with ANY strong
    # color channel stay opaque, only truly neutral near-whites go transparent
    min_channel = arr[:, :, :3].min(axis=2) / 255.0
    alpha = 255.0 * (1.0 - min_channel ** power)
    alpha_arr = np.clip(alpha, 0, 255).astype(np.uint8)
    img.putalpha(Image.fromarray(alpha_arr, mode="L"))
    return img


def composite_artwork_on_base(base, artwork, offset_x=0, offset_y=0, fade_px=120):
    """Composite artwork onto base with white-to-alpha conversion and vignette fade.

    For dye/material cards: converts white background to transparent so only
    the painted subject composites onto the base texture.

    Args:
        base: PIL Image (RGBA), the base texture background.
        artwork: PIL Image, the per-card artwork (white background).
        offset_x: Pixels to shift artwork right (positive = more clearance top-left).
        offset_y: Pixels to shift artwork down (positive = more clearance top-left).
        fade_px: Width of the linear fade at each edge.

    Returns:
        PIL Image (RGBA), the composited result.
    """
    w, h = base.size
    artwork = artwork.resize((w, h), Image.LANCZOS)

    # Convert white background to transparency
    artwork = white_to_alpha(artwork)

    # Create a canvas for the shifted artwork
    shifted = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shifted.paste(artwork, (offset_x, offset_y), artwork)

    # Apply vignette mask on top for smooth edge blending
    mask = create_vignette_mask(w, h, fade_px)
    r, g, b, a = shifted.split()
    a_arr = np.array(a, dtype=np.float32)
    m_arr = np.array(mask, dtype=np.float32)
    combined = (a_arr * m_arr / 255).astype(np.uint8)
    shifted.putalpha(Image.fromarray(combined, mode="L"))

    return Image.alpha_composite(base.convert("RGBA"), shifted)


def composite_artwork_on_base_opaque(base, artwork, offset_x=0, offset_y=0, fade_px=100):
    """Composite artwork onto base using only vignette mask (no white removal).

    For action cards: pastes artwork as-is (white background included) onto the
    dark base, using an asymmetric vignette mask. Heavy fade on the left and
    bottom to keep icon areas clear on the dark base. The artwork concentrates
    in the center-right of the card.

    Args:
        base: PIL Image (RGBA), the dark base texture.
        artwork: PIL Image, the per-card artwork (kept opaque with white bg).
        offset_x: Pixels to shift artwork right.
        offset_y: Pixels to shift artwork down.
        fade_px: Base fade width (used for right edge).

    Returns:
        PIL Image (RGBA), the composited result.
    """
    w, h = base.size

    # Crop artwork edges to remove AI-generated border artifacts, then resize to
    # cover the full canvas even after the offset shift
    margin = 20
    artwork = artwork.crop((margin, margin,
                            artwork.width - margin, artwork.height - margin))
    artwork = artwork.resize((w + offset_x, h + offset_y), Image.LANCZOS).convert("RGBA")

    # Create a canvas for the shifted artwork
    shifted = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shifted.paste(artwork, (0, 0), artwork)

    # Asymmetric vignette: heavy fade on left/bottom (icon areas), lighter on right/top
    mask = create_vignette_mask(w, h,
                                fade_left=280,    # clear bottom-left icon column
                                fade_right=100,
                                fade_top=200,     # clear top-left icons
                                fade_bottom=250)  # clear bottom-left icons
    shifted.putalpha(mask)

    return Image.alpha_composite(base.convert("RGBA"), shifted)
