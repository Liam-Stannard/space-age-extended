#!/usr/bin/env python3
"""Build the Whisker Bed tile's terrain sheets from vanilla's stone path.

`prototypes/core/tiles.lua` deep-copies `stone-path` and, until now, kept its
graphics -- so a whisker farm on the Core was indistinguishable from a concrete
pad, which is the complaint that started this pass. A farm is the one place on
the planet where something grows; it should not look like paving.

Why recolour vanilla rather than generate a tile. A Factorio tile is not one
picture: it is three main sheets at 1x, 2x and 4x with sixteen variants each,
plus five transition sheets and their masks, and every one of them has to be
seamlessly tileable against the others. A generator cannot hold that contract.
Vanilla's sheets already satisfy it exactly, so the geometry is kept and only
the material is changed -- the same argument `recolour-turbine.py` makes.

What changes. Stone path is a warm mid-grey cobble. The whisker bed is the
*growing medium* of the kamacite chain: dark iron-nickel grit, a touch cooler
and a good deal darker, with sparse pale whisker glints seeded through it in the
silver-white of the kamacite whiskers icon. Luminance is remapped rather than
tinted -- a tint over a neutral grey only darkens it, and the cobble shading
would survive as cobble shading.

The specks are deterministic (a fixed seed) so re-running this produces the same
tile, and they are applied per pixel rather than per cell, so no speck pattern
can line up across the sixteen variants and read as a repeat.

Usage: tools/build-whisker-bed-tile.py [path-to-factorio-data-dir]
Writes graphics/terrain/whisker-bed/*.png.
"""

import os
import random
import sys

from PIL import Image

# The bed ground of building-spec-bed-tender.md section 3.3, and the whisker
# silver of the chain 2 icons. The ramp runs from a near-black grit shadow to a
# highlight a little above the base colour; stone path's own mid grey lands on
# BASE, so the cobble reads as packed metal grit rather than as stone.
SHADOW = (26, 24, 21)
BASE = (90, 82, 72)          # #5A5248
HIGH = (150, 142, 128)
WHISKER = (214, 218, 224)    # #D6DAE0

SPECK_RATE = 0.010           # fraction of pixels carrying a whisker glint
CONTRAST = 1.22              # stone path is flat; grit wants more bite

SHEETS = [
    "stone-path-1", "stone-path-2", "stone-path-4",
    "stone-path-o", "stone-path-u", "stone-path-side",
    "stone-path-inner-corner", "stone-path-outer-corner",
]
MASKS = [
    "stone-path-o-mask", "stone-path-u-mask", "stone-path-side-mask",
    "stone-path-inner-corner-mask", "stone-path-outer-corner-mask",
]


def ramp(t):
    """Three-stop colour ramp, t in 0..1."""
    if t < 0.5:
        u = t / 0.5
        a, b = SHADOW, BASE
    else:
        u = (t - 0.5) / 0.5
        a, b = BASE, HIGH
    return tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))


def recolour(im, rng):
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    lut = [ramp(i / 255.0) for i in range(256)]
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
            lum = min(1.0, max(0.0, (lum - 0.5) * CONTRAST + 0.5))
            nr, ng, nb = lut[int(lum * 255)]
            if rng.random() < SPECK_RATE:
                # A whisker glint: pale, and blended rather than stamped so it
                # sits in the grit instead of on top of it.
                k = 0.55 + rng.random() * 0.45
                nr = int(nr + (WHISKER[0] - nr) * k)
                ng = int(ng + (WHISKER[1] - ng) * k)
                nb = int(nb + (WHISKER[2] - nb) * k)
            px[x, y] = (nr, ng, nb, a)
    return im


def main():
    data = sys.argv[1] if len(sys.argv) > 1 else None
    if not data:
        for c in (os.path.expanduser("~/.steam/debian-installation/steamapps/"
                                     "common/Factorio/data"),
                  os.path.expanduser("~/.steam/steam/steamapps/common/"
                                     "Factorio/data")):
            if os.path.isdir(c):
                data = c
                break
    if not data or not os.path.isdir(data):
        sys.exit("could not find Factorio's data directory; pass it as arg 1")

    src = os.path.join(data, "base/graphics/terrain/stone-path")
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "graphics/terrain/whisker-bed")
    os.makedirs(out, exist_ok=True)

    rng = random.Random(20260905)
    for name in SHEETS:
        im = Image.open(os.path.join(src, name + ".png"))
        dst = name.replace("stone-path", "whisker-bed")
        new = recolour(im, rng)
        # Sheets that started life without alpha stay without it, so the
        # prototype's expectations about the file are unchanged.
        if Image.open(os.path.join(src, name + ".png")).mode == "RGB":
            new = new.convert("RGB")
        new.save(os.path.join(out, dst + ".png"))
        print(f"  ok  {dst}.png  {new.size}  {new.mode}")

    # Masks are alpha shapes, not material: copied through untouched so the
    # transitions keep cutting exactly where vanilla's do.
    for name in MASKS:
        im = Image.open(os.path.join(src, name + ".png"))
        dst = name.replace("stone-path", "whisker-bed")
        im.save(os.path.join(out, dst + ".png"))
        print(f"  ok  {dst}.png  {im.size}  {im.mode}  (mask, copied)")


if __name__ == "__main__":
    main()
