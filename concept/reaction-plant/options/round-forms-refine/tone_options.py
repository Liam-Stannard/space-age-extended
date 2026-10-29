#!/usr/bin/env python3
"""T06h: the tone options -- the refined casing's idle plates (forms.py --idle, downsampled) at a few sun / fill pairs,
north (the brightest direction) and west (the darkest) at 2x on the ground, each with measure.py's tonal() p50/p95 for
all four directions. A picture with measure.py's own numbers; the round's figures are the full runs'.

  python3 tone_options.py <out.png> <label>=<x1 dir> ...
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import measure  # noqa: E402

DIRS = ("north", "east", "south", "west")
GROUND, BG, TEXT, HEAD = (74, 66, 58, 255), (30, 29, 28, 255), (228, 222, 210), (240, 200, 120)


def font(n, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""), n)


out_p, opts = sys.argv[1], [a.split("=", 1) for a in sys.argv[2:]]
cols = []
for lab, src in opts:
    t = {d: measure.tonal(Image.open(os.path.join(src, f"idle-{d}.png")).convert("RGBA")) for d in DIRS}
    cells = []
    for d in ("north", "west"):
        im = Image.open(os.path.join(src, f"idle-{d}.png")).convert("RGBA")
        g = Image.new("RGBA", im.size, GROUND)
        g.alpha_composite(im)
        cells.append(g.resize((im.width * 2, im.height * 2), Image.NEAREST))
    w = cells[0].width
    head = Image.new("RGBA", (w, 76), BG)
    dr = ImageDraw.Draw(head)
    dr.text((6, 4), lab, font=font(20, True), fill=HEAD)
    dr.text((6, 32), "p50/p95  " + "  ".join(f"{d[0].upper()} {t[d]['p50']}/{t[d]['p95']}" for d in DIRS),
            font=font(17), fill=TEXT)
    dr.text((6, 54), "top: facing north; below: facing west", font=font(14), fill=TEXT)
    col = Image.new("RGBA", (w, head.height + sum(c.height for c in cells) + 8), BG)
    col.alpha_composite(head, (0, 0))
    y = head.height
    for c in cells:
        col.alpha_composite(c, (0, y))
        y += c.height + 8
    cols.append(col)
title = Image.new("RGBA", (sum(c.width for c in cols) + 8 * (len(cols) - 1), 70), BG)
d = ImageDraw.Draw(title)
d.text((8, 6), "Tone (T06h): the refined casing's idle plates at sun / fill pairs (measure.py tonal(); bar p50 75-81 "
       "in every direction, p95 into vanilla's 143-189)", font=font(22, True), fill=HEAD)
d.text((8, 40), "West stays ~7 under north at every pair: sun and fill lift all four together; the casing's paint "
       "(#9C9280, #AA9F8C) lifted p95, not p50.", font=font(17), fill=TEXT)
out = Image.new("RGBA", (title.width, title.height + max(c.height for c in cols)), BG)
out.alpha_composite(title, (0, 0))
x = 0
for c in cols:
    out.alpha_composite(c, (x, title.height))
    x += c.width + 8
if max(out.size) >= 8000:
    r_ = 7990 / max(out.size)
    out = out.resize((round(out.width * r_), round(out.height * r_)), Image.LANCZOS)
out.convert("RGB").save(out_p, optimize=True)
print(out_p, out.size)
