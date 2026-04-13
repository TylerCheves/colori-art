"""Clear a small top-right corner area on cinnabar-light-fullbleed-1 for title text."""

from PIL import Image, ImageFilter
import numpy as np
import os

INPUT = "new-drafts/cinnabar-light-fullbleed-1.png"
OUTPUT = "new-drafts/cinnabar-light-titlespace.png"

img = Image.open(INPUT)
w, h = img.size  # 750 x 1050

# Area to clear: right half of top ~10%
# x: from midpoint to right edge, y: from top to ~10% down
clear_left = w // 2       # 375
clear_top = 0
clear_right = w            # 750
clear_bottom = int(h * 0.10)  # 105

# Sample the background color from the top-right corner (very corner pixels)
# which is already mostly light tan
sample_region = img.crop((w - 50, 0, w, 30))
pixels = np.array(sample_region)
bg_color = tuple(np.mean(pixels.reshape(-1, 3), axis=0).astype(int))
print(f"Sampled background color: {bg_color}")

# Create a copy to work on
result = img.copy()
px = np.array(result)

# Fill the clear zone with background color
px[clear_top:clear_bottom, clear_left:clear_right] = bg_color

# Create a soft feathered transition on the left edge and bottom edge
# so it blends naturally into the art
feather = 40  # pixels of gradient

# Left edge feather (horizontal gradient)
for x_offset in range(feather):
    alpha = x_offset / feather  # 0 at art side, 1 at clear side
    x = clear_left - feather + x_offset
    if 0 <= x < w:
        for y in range(clear_top, clear_bottom):
            orig = np.array(img.getpixel((x, y))[:3])
            blended = (orig * (1 - alpha) + np.array(bg_color) * alpha).astype(int)
            px[y, x] = blended

# Bottom edge feather (vertical gradient)
for y_offset in range(feather):
    alpha = y_offset / feather  # 0 at art side, 1 at clear side
    y = clear_bottom + feather - y_offset
    if 0 <= y < h:
        for x in range(clear_left - feather, clear_right):
            if 0 <= x < w:
                orig = np.array(img.getpixel((x, y))[:3])
                blended = (orig * (1 - alpha) + np.array(bg_color) * alpha).astype(int)
                px[y, x] = blended

# Corner feather (diagonal blend where left and bottom feathers meet)
for x_offset in range(feather):
    for y_offset in range(feather):
        x = clear_left - feather + x_offset
        y = clear_bottom + feather - y_offset
        if 0 <= x < w and 0 <= y < h:
            alpha_x = x_offset / feather
            alpha_y = y_offset / feather
            alpha = alpha_x * alpha_y
            orig = np.array(img.getpixel((x, y))[:3])
            blended = (orig * (1 - alpha) + np.array(bg_color) * alpha).astype(int)
            px[y, x] = blended

result = Image.fromarray(px)
result.save(OUTPUT, "PNG")
print(f"Saved: {OUTPUT}")
print(f"Cleared area: x={clear_left}-{clear_right}, y={clear_top}-{clear_bottom} ({clear_right-clear_left}x{clear_bottom}px)")
