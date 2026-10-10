#!/usr/bin/env python3
"""Cut the material swatches out of the adopted sheet and make them tile.

  python3 concept/crust-tap/model/swatches/bake_concept.py

concept/crust-tap/adopted/A-sheet.png ends in a palette panel of six rendered
material chips (y 794-891): the collar's dark brown-grey, a mid grey-brown, the
riser's pale steel, copper, brass and the frost white (unused: the 2026-10-02
amendment drops the frost). The hero view's cap is a diamond tread plate; that is
cut out too, for the cap.

The technique is the vacuum furnace's and the drop crusher's
(concept/drop-crusher/model/swatches/bake_concept.py): each chip's soft lighting
is divided out (chip / heavy blur x chip mean), so the concept's grain stays and
the render's own light is applied; it is made to tile by cross-fading with a
half-rolled copy, never by mirroring.

Colour: where spec 3.3 names a hex the swatch is re-centred on it, keeping the
concept's grain (the collar and anchors #3E3B36 -> #5E584E, the riser #8A8580).
Copper and brass keep the chips' own colour.
"""
import math
import os

from PIL import Image, ImageFilter, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "..", "..", "adopted", "A-sheet.png")
# the palette panel's chips, inset 6 px inside each chip's edge; the hero's cap
SWATCHES = {
    "collar": (989, 800, 1050, 885),     # darkest chip: the collar's staves
    "plate": (989, 800, 1050, 885),      # the same, darker: the base plate, a flat in full sun
    "anchor": (1074, 800, 1134, 885),    # mid grey-brown: the anchors' blocks, the brackets
    "riser": (1159, 800, 1219, 885),     # pale steel: the riser
    "copper": (1244, 800, 1304, 885),
    "brass": (1328, 800, 1388, 885),
    "cap": (210, 215, 260, 250),         # the hero view's cap: diamond tread plate
}
# spec 3.3 (the collar range #3E3B36 -> #5E584E; the riser #8A8580)
RECENTRE = {"collar": "#5C5044", "plate": "#4A3F35", "anchor": "#625548", "riser": "#8A8580",
            "cap": "#52483E"}           # the browns warmed toward the adopted plate's (saturation 0.40)
GAIN = 3.6
GAINS = {"plate": 1.6, "cap": 0.8, "riser": 2.2}    # the grain's contrast per swatch, where it is not GAIN


def hexrgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def seamless(im):
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
            ox[x, y] = tuple(max(0, min(255, round(mean[c] + GAINS.get(name, GAIN) * (px[x, y][c] * mean[c] / max(1, bx[x, y][c]) - mean[c]))))
                             for c in range(3))
    out = seamless(out)
    w, h = out.size
    tile = Image.new("RGB", (w * 2, h * 2))
    for i in range(2):
        for j in range(2):
            tile.paste(out, (i * w, j * h))
    tile.save(os.path.join(HERE, f"concept_{name}.png"))
    print(name, tile.size, "mean", [round(m) for m in mean])
