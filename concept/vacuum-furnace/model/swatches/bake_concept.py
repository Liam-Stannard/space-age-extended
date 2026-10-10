#!/usr/bin/env python3
"""Cut the material swatches out of the adopted concept sheet and make them tile.

  python3 concept/vacuum-furnace/model/swatches/bake_concept.py

concept/vacuum-furnace/adopted/A-sheet.png ends in a row of nine rendered
material swatches. Each is lit with a soft gradient, so the gradient is divided
out (swatch / heavy blur x swatch mean): the concept's grain stays, its
lighting goes, and the render's own light is applied instead. Made to tile by
cross-fading, not mirroring (the reaction plant's mirror tile drew a rust
"butterfly").

Colour: where spec section 3.3 names a hex for the material, the swatch is
re-centred on it, keeping the concept's grain: the drum, the hatch, the
radiator loops and the frost. Copper and brass are not in 3.3, so they keep
the concept's own colour.
"""
import math
import os

from PIL import Image, ImageFilter, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "..", "..", "adopted", "A-sheet.png")
# the palette row, inset 6 px past each swatch's frame (y 910-990 on the sheet)
SWATCHES = {
    "drum": (128, 916, 230, 984),        # darkest brown-grey
    "plinth": (128, 916, 230, 984),      # the same swatch, at the dark end of 3.3's range
    "radiator": (270, 916, 369, 984),    # mid brown-grey
    "hatch": (548, 916, 648, 984),       # pale grey
    "hatch_warm": (548, 916, 648, 984),  # the same, warmed toward the adopted plate's roof beige
    "copper": (687, 916, 784, 984),
    "brass": (822, 916, 917, 984),
    "frost": (1210, 916, 1304, 984),     # palest blue
}
# spec 3.3: the drum body runs #3E3B36 -> #5E584E -- its walls the light end, the
# plinth it stands on the dark end, as the plate draws them
RECENTRE = {"drum": "#5E584E", "plinth": "#3E3B36", "radiator": "#6E685C", "hatch": "#8A8580", "frost": "#BFD8E8",
            # not 3.3: the alternative roof reading for Liam, #8A8580 scaled channel by channel by
            # the adopted plate's lit roof over our render's (173,153,134 / 160,152,144)
            "hatch_warm": "#958577"}
GAIN = 1.7


def hexrgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def seamless(im):
    """Wrap without a seam or a mirror: cross-fade with a half-rolled copy, per axis,
    then rescale each channel to the swatch's own mean and spread."""
    w, h = im.size
    st0 = ImageStat.Stat(im)
    for axis in (0, 1):
        n = w if axis == 0 else h
        rolled = Image.new("RGB", im.size)
        if axis == 0:
            rolled.paste(im.crop((n // 2, 0, w, h)), (0, 0))
            rolled.paste(im.crop((0, 0, n // 2, h)), (w - n // 2, 0))
        else:
            rolled.paste(im.crop((0, n // 2, w, h)), (0, 0))
            rolled.paste(im.crop((0, 0, w, n // 2)), (0, h - n // 2))
        a, b = im.load(), rolled.load()
        out = Image.new("RGB", im.size)
        o = out.load()
        for y in range(h):
            for x in range(w):
                k = math.cos(math.pi * (x if axis == 0 else y) / n) ** 2
                o[x, y] = tuple(round((1 - k) * a[x, y][c] + k * b[x, y][c]) for c in range(3))
        im = out
    st1 = ImageStat.Stat(im)
    return Image.merge("RGB", [im.getchannel(c).point(
        lambda v, c=c: max(0, min(255, round(st0.mean[c] + (v - st1.mean[c]) * st0.stddev[c] / max(1e-6, st1.stddev[c])))))
        for c in range(3)])


sheet = Image.open(SHEET).convert("RGB")
for name, box in SWATCHES.items():
    sw = sheet.crop(box).resize(((box[2] - box[0]) * 2, (box[3] - box[1]) * 2), Image.LANCZOS)
    mean = ImageStat.Stat(sw).mean
    if name in RECENTRE:
        target = hexrgb(RECENTRE[name])
        sw = Image.merge("RGB", [sw.getchannel(c).point(lambda v, k=target[c] / mean[c]: min(255, round(v * k)))
                                 for c in range(3)])
        mean = target
    blur = sw.filter(ImageFilter.GaussianBlur(max(sw.size) / 5))
    px, bx = sw.load(), blur.load()
    out = Image.new("RGB", sw.size)
    ox = out.load()
    for y in range(sw.size[1]):
        for x in range(sw.size[0]):
            ox[x, y] = tuple(max(0, min(255, round(mean[c] + GAIN * (px[x, y][c] * mean[c] / max(1, bx[x, y][c]) - mean[c]))))
                             for c in range(3))
    out = seamless(out)
    w, h = out.size
    tile = Image.new("RGB", (w * 2, h * 2))
    for i in range(2):
        for j in range(2):
            tile.paste(out, (i * w, j * h))
    tile.save(os.path.join(HERE, f"concept_{name}.png"))
    print(name, tile.size, "mean", [round(m) for m in mean])
