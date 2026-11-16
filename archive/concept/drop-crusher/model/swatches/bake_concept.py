#!/usr/bin/env python3
"""Cut the material swatches out of the adopted sheet and make them tile.

  python3 concept/drop-crusher/model/swatches/bake_concept.py

concept/drop-crusher/adopted/A-sheet.png ends in a palette row of eight rendered
material chips (y 920-984). The technique is the vacuum furnace's
(concept/vacuum-furnace/model/swatches/bake_concept.py): each chip's soft lighting
is divided out (chip / heavy blur x chip mean), so the concept's grain stays and
the render's own light is applied; it is made to tile by cross-fading with a
half-rolled copy, never by mirroring.

Colour: where spec 3.3 names a hex for the material the swatch is re-centred on
it, keeping the concept's grain. Copper and brass keep the concept's own colour,
as 3.3's range (#8A5A32 -> #C88A4A) is the chips' own.
"""
import math
import os

from PIL import Image, ImageFilter, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "..", "..", "adopted", "A-sheet.png")
# the palette row, inset 6 px inside each chip's edge
SWATCHES = {
    "armour": (159, 926, 246, 979),      # mid brown-grey: the cylinder and buttresses
    "roof": (159, 926, 246, 979),        # the same chip, its grain gentler: a big flat plate in the sun
    "deck": (39, 926, 130, 979),
    "guide": (39, 926, 130, 979),        # the dark chip, nearly without grain: the gear housings' smooth plate         # the dark chip, gently grained: the roof deck in the hull's paint
    "frame": (39, 926, 130, 979),        # darkest brown: the base plate and housings
    "gear": (276, 926, 372, 979),        # light grey-brown: gears, rack, pawl, collar
    "weight": (39, 926, 130, 979),       # the dark chip again, at the weight's own value
    "anvil": (402, 926, 479, 979),       # pale: the collar's struck rim
    "copper": (508, 926, 597, 979),
    "brass": (627, 926, 711, 979),
}
# spec 3.3
RECENTRE = {"armour": "#6E685C", "roof": "#6E685C", "deck": "#524D45", "guide": "#5A554E", "frame": "#4A463F", "gear": "#8A857C", "weight": "#3A3733",
            "anvil": "#9A948A"}
GAIN = 3.6
GAINS = {"roof": 1.8, "deck": 1.0, "guide": 0.3}                    # the grain's contrast per swatch, where it is not GAIN


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
