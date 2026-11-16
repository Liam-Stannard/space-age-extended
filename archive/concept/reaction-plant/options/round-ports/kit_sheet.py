#!/usr/bin/env python3
"""T06i: the restored kit, for the question T06h left open (Liam, 2026-10-21; re-asked with T06i): the kit T06h
restored on the roof at a step smaller than T06e's (the side-nozzle pot 0.26 for 0.30, the exchanger 0.25 for
0.30), the pot hidden facing north, and the added kit (barrels, junction boxes) moved off the gaps it took.

  python3 kit_sheet.py <full-dir> <out.png>

<full-dir> holds run-<d>/ (render.sh's out-dir; its hi/idle.png is the 4x plate). Each item is cropped at 2x
(the 4x render halved), 1.5 tiles square, in all four directions. A picture for the question, not a measure.
"""
import math
import textwrap
import os
import sys

from PIL import Image, ImageDraw, ImageFont

DIRS = ("north", "east", "south", "west")
DEG = dict(zip(DIRS, (0, 90, 180, 270)))
K4 = 256
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
HEAD, TEXT, SUB = (240, 200, 120), (240, 220, 170), (200, 194, 182)
ITEMS = [
    ("side-nozzle pot", "r 0.26 (T06e 0.30); north of the reactor", (0.3, 1.5, 1.7)),
    ("exchanger", "r 0.25 (T06e 0.30); between the legs and the receiver", (0.5, -1.15, 1.25)),
    ("sampling manifold", "between the instrument house and the compressor", (1.9, 1.2, 1.2)),
    ("drain skid", "down the west roof edge, its valve and header", (-2.215, -0.8, 1.15)),
    ("barrels (moved)", "east roof edge, 3", (2.24, -1.3, 1.15)),
    ("barrels + box (moved)", "by the loop valve; a box by the scrubber", (-0.09, -1.26, 1.15)),
    ("junction box (moved)", "between the instrument house and the gas hose", (1.87, 0.75, 1.1)),
]


def font(n, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""), n)


def plate(full, d):
    im = Image.open(os.path.join(full, f"run-{d}", "hi", "idle.png")).convert("RGBA")
    g = Image.new("RGBA", im.size, GROUND)
    g.alpha_composite(im)
    return g


def crop(g, p, d, side=1.5):
    x, y, z = p
    a = -math.radians(DEG[d])
    e, n = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
    cx, cy = g.width / 2 + e * K4, g.height / 2 - (n + z * 0.5) * K4
    s = side * K4 / 2
    c = g.crop((round(cx - s), round(cy - s), round(cx + s), round(cy + s)))
    c = c.resize((c.width // 2, c.height // 2), Image.LANCZOS)
    dr = ImageDraw.Draw(c)                    # a ring round the item (its point, as the camera sees it)
    m, rr = c.width / 2, 0.3 * K4 / 2
    dr.ellipse([m - rr, m - rr, m + rr, m + rr], outline=(255, 210, 60), width=2)
    return c


def main(full, out):
    P = {d: plate(full, d) for d in DIRS}
    cw = 192
    lw = 300
    rows = []
    for name, sub, p in ITEMS:
        r = Image.new("RGBA", (lw + 4 * (cw + 6), cw + 6), BG)
        dr = ImageDraw.Draw(r)
        dr.text((8, 8), name, font=font(19, True), fill=TEXT)
        for i, ln in enumerate(textwrap.wrap(sub, 32)):
            dr.text((8, 36 + 22 * i), ln, font=font(15), fill=SUB)
        for i, d in enumerate(DIRS):
            r.alpha_composite(crop(P[d], p, d), (lw + i * (cw + 6), 3))
        rows.append(r)
    W = rows[0].width
    head = Image.new("RGBA", (W, 230), BG)
    dr = ImageDraw.Draw(head)
    dr.text((10, 8), "The restored kit (T06h): accept, free space, or swap?", font=font(26, True), fill=HEAD)
    for i, ln in enumerate([
        "T06h set the kit T06g left out back on the roof, a step smaller than T06e's where the roof is tight (pot 0.26, exchanger",
        "0.25, both 0.30 before), and moved the added barrels and boxes off the gaps it took. Facing north the pot stands behind the",
        "reactor and is hidden. Columns: facing north, east, south, west; each crop 1.5 tiles at 2x (T06i's model).",
        "A accept as built.   B free space: take out added barrels or boxes so the pot and exchanger go back to 0.30.",
        "C swap: trade a restored item's spot with an added item's, so the pot shows facing north. Yellow ring: the item.",
    ]):
        dr.text((10, 48 + 30 * i), ln, font=font(17), fill=SUB)
    for i, d in enumerate(DIRS):
        dr.text((lw + i * (cw + 6) + 6, 205), f"facing {d}", font=font(16, True), fill=TEXT)
    out_im = Image.new("RGBA", (W, head.height + sum(r.height for r in rows)), BG)
    out_im.alpha_composite(head, (0, 0))
    y = head.height
    for r in rows:
        out_im.alpha_composite(r, (0, y))
        y += r.height
    out_im.convert("RGB").save(out)
    print("wrote", out, out_im.size)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
