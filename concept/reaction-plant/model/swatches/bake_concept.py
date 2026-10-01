#!/usr/bin/env python3
"""Cut the material swatches out of the concept sheet and make them tile.

  python3 concept/reaction-plant/model/swatches/bake_concept.py

concept/reaction-plant/v2-sheet.png carries a material palette: one rendered
swatch per material. Each is lit with a soft gradient, so the gradient is
divided out (swatch / heavy blur x swatch mean): the concept's colour and grain
stay, its lighting goes, and ours is applied instead. Then made to tile by
cross-fading, not by mirroring: a mirror tile repeats every mark four times about
one centre, and on the hatch cover that showed as a symmetric rust "butterfly".
"""
import math
import os

from PIL import Image, ImageFilter, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "..", "..", "v2-sheet.png")
SWATCHES = {                     # sheet pixel boxes, inset past each swatch's frame
    "drum": (1012, 724, 1111, 782),
    "band": (1138, 724, 1244, 782),
    "cast": (1270, 724, 1351, 782),
    "copper": (1375, 724, 1430, 782),
    "brass": (1444, 724, 1500, 782),
    "teal": (1094, 858, 1218, 912),
}
GAIN = 1.7
# The palette swatches are brighter than the same materials in the sheet's own
# main render (plate 101 vs 71, bands 91 vs 57, measured). Re-centre those on
# the main render's colour, sampled from its drum top and band, keeping the grain.
# The teal swatch is the other way round: cleaner and colder than the paint on
# the main render's hatch cover (hue 178 sat 0.56 against hue 166 sat 0.30), and
# rendered from it the guard read as a sticker on a weathered machine.
MAIN_VIEW = {"drum": (300, 190, 360, 215), "band": (330, 380, 400, 410),
             "teal": (425, 185, 465, 205)}
# The teal is on the roof, in full sun, so matched to the concept it still renders
# lighter than the concept shows it (value 0.57 against 0.43, measured): darkened
# by that ratio so the render, not the swatch, lands on the concept.
DARKEN = {"teal": 0.43 / 0.57}


def seamless(im):
    """Make im wrap without a seam and without mirroring it.

    Along x, the image and its copy rolled by half are blended, the copy weighted
    1 at the edges (where it runs continuously round the wrap) and 0 mid-way
    (where its own seam is); then the same along y. The blend averages two
    unrelated grains, so the result is rescaled to the swatch's own mean and
    spread, channel by channel: the colour the plate was measured against stays.
    """
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
    if name in MAIN_VIEW:
        target = [c * DARKEN.get(name, 1.0) for c in ImageStat.Stat(sheet.crop(MAIN_VIEW[name])).mean]
        sw = Image.merge("RGB", [sw.getchannel(c).point(lambda v, k=target[c] / mean[c]: min(255, round(v * k)))
                                 for c in range(3)])
        mean = target
    blur = sw.filter(ImageFilter.GaussianBlur(max(sw.size) / 5))
    # per-pixel: out = sw * mean / blur
    px, bx = sw.load(), blur.load()
    out = Image.new("RGB", sw.size)
    ox = out.load()
    for y in range(sw.size[1]):
        for x in range(sw.size[0]):
            # detail gain: the swatch's grain is subtle at sheet size and vanishes at sprite
            # size unless it is pushed
            ox[x, y] = tuple(max(0, min(255, round(mean[c] + GAIN * (px[x, y][c] * mean[c] / max(1, bx[x, y][c]) - mean[c]))))
                             for c in range(3))
    # repeated 2x2 so a mark is the same size on the plate as the mirror tile drew it
    out = seamless(out)
    w, h = out.size
    tile = Image.new("RGB", (w * 2, h * 2))
    for i in range(2):
        for j in range(2):
            tile.paste(out, (i * w, j * h))
    tile.save(os.path.join(HERE, f"concept_{name}.png"))
    print(name, tile.size, "mean", [round(m) for m in mean])
