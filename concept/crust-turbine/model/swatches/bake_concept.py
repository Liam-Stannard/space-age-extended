#!/usr/bin/env python3
"""Cut the material swatches out of the adopted concept sheet and make them tile.

  python3 concept/crust-turbine/model/swatches/bake_concept.py

concept/crust-turbine/adopted/E-sheet.png ends in a palette panel of eight rendered
material swatches (x 951-1492, y 817-912 on the sheet). Each is lit with a soft
gradient, so the gradient is divided out (swatch / heavy blur x swatch mean): the
concept's grain stays, its lighting goes, and the render's own light is applied.
Made to tile by cross-fading, not mirroring. The method is the Vacuum Furnace's
(concept/vacuum-furnace/model/swatches/bake_concept.py).

Colour: where spec section 3.3 names a hex for the material, the swatch is
re-centred on it, keeping the concept's grain: the body (the light and dark ends
of #4A463F -> #6E685C), the collars and fittings (#8A857C), the generator can
(#5A5047) and the frost (#BFD8E8, the dark end of 3.3's range: lit, it rises toward #E8F2F8). Copper and brass keep the
concept's own colour, which 3.3's #8A5A32 -> #C88A4A range already holds.
"""
import math
import os

from PIL import Image, ImageFilter, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "..", "..", "adopted", "E-sheet.png")
# the palette panel, inset 6 px inside each swatch (y 817-912 on the sheet)
SWATCHES = {
    "body": (1025, 823, 1074, 906),      # the second: mid brown-grey
    "body_dark": (957, 823, 1005, 906),  # the first: darkest brown-grey
    "collar": (1093, 823, 1142, 906),    # pale grey: the machined collars
    "gencan": (1439, 823, 1486, 906),    # the last: dark warm brown
    "copper": (1369, 823, 1419, 906),
    "brass": (1231, 823, 1280, 906),
    "frost": (1300, 823, 1349, 906),     # palest blue
}
RECENTRE = {"body": "#6E685C", "body_dark": "#4A463F", "collar": "#8A857C", "gencan": "#5A5047",
            "frost": "#BFD8E8"}
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
