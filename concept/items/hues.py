#!/usr/bin/env python3
"""Colour identity survey: the mean hue and saturation of an icon's lit pixels.

  python3 concept/items/hues.py [icon.png[:label] ...]

With no arguments, surveys vanilla's and Space Age's raw resources, raw materials
and plates, plus the mod's own fluid colours (siderane, helium-3), and prints each.

"Lit pixels": the 64 px level's opaque pixels (alpha > 200) in the brighter half
of the icon's own luminance -- the faces the sun catches, which is where vanilla
puts an item's colour (iron ore's lit faces are its blue; its shadows are grey).
Hue is the saturation-weighted circular mean of HSV hue, in degrees; saturation
the mean HSV saturation (0-1) of the same pixels.
"""
import colorsys
import math
import sys

from PIL import Image

V = "/home/liam-stannard/.steam/steam/steamapps/common/Factorio/data"
BASE = ["iron-ore", "iron-plate", "copper-ore", "copper-plate", "uranium-ore", "stone", "coal",
        "steel-plate", "stone-brick", "sulfur", "wood", "solid-fuel", "plastic-bar", "uranium-238", "uranium-235"]
SPACE_AGE = ["tungsten-ore", "tungsten-plate", "tungsten-carbide", "holmium-ore", "holmium-plate", "calcite",
             "scrap", "lithium", "lithium-plate", "carbon", "ice"]
OURS = {"siderane (fluid)": (0.66, 0.85, 0.16), "helium-3 (fluid)": (0.55, 0.78, 0.90)}


def lit(im):
    im = im.convert("RGBA").crop((0, 0, 64, 64)) if im.width > im.height else im.convert("RGBA")
    px = [p for p in im.get_flattened_data() if p[3] > 200]
    if not px:
        return []
    L = sorted(0.299 * r + 0.587 * g + 0.114 * b for r, g, b, a in px)
    med = L[len(L) // 2]
    return [p for p in px if 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] >= med]


def hue_sat(pixels):
    sx = sy = st = 0.0
    for r, g, b, *_ in pixels:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        sx += s * math.cos(2 * math.pi * h)
        sy += s * math.sin(2 * math.pi * h)
        st += s
    n = max(len(pixels), 1)
    return (math.degrees(math.atan2(sy, sx)) % 360, st / n)


def icon(path):
    return hue_sat(lit(Image.open(path)))


def colour(rgb):
    h, s, v = colorsys.rgb_to_hsv(*rgb)
    return (h * 360, s)


def survey():
    out = {}
    for n in BASE:
        out[n] = icon(f"{V}/base/graphics/icons/{n}.png")
    for n in SPACE_AGE:
        out[n] = icon(f"{V}/space-age/graphics/icons/{n}.png")
    for n, c in OURS.items():
        out[n] = colour(c)
    return out


def dist(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def nearest(h, table, min_sat=0.12):
    """The nearest hue among entries saturated enough to have one."""
    best = None
    for n, (hh, s) in table.items():
        if s < min_sat:
            continue
        d = dist(h, hh)
        if best is None or d < best[1]:
            best = (n, d)
    return best


if __name__ == "__main__":
    table = survey()
    for a in sys.argv[1:]:
        p, _, lab = a.partition(":")
        table[lab or p] = icon(p)
    for n, (h, s) in sorted(table.items(), key=lambda kv: kv[1][0]):
        print(f"{n:22s} hue {h:5.0f}  sat {s:.2f}" + ("   (grey: no hue)" if s < 0.12 else ""))
