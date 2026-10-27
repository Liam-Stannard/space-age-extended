#!/usr/bin/env python3
"""T06i: the phone-sized top sheet (1080 px wide): the four directions, a few run ends before and after at 4x,
and the bars.

  python3 top_sheet.py <before-idle-dir> <full-dir> <ports.json> <bars.txt> <out.png>

<before-idle-dir>: T06h's forms.py --idle renders (idle-<d>.png, 4x); <full-dir>: T06i's render.sh runs (run-<d>/hi/
idle.png, 4x); <bars.txt>: one line a bar, written by hand from measures.txt. A picture, not a measure.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ends_crops as ec  # noqa: E402

W = 1080
BG = (30, 29, 28, 255)
GROUND = (74, 66, 58, 255)
HEAD, TEXT, SUB = (240, 200, 120), (240, 220, 170), (200, 194, 182)
SHOW = [("press1", "b"), ("dosing1", "b"), ("drain1", "b"), ("makeup1", "a"), ("legs1", "a"), ("socket1", "b")]


def font(n, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""), n)


def ground(path):
    im = Image.open(path).convert("RGBA")
    g = Image.new("RGBA", im.size, GROUND)
    g.alpha_composite(im)
    return g


def main(bdir, full, ports, bars, out):
    P = json.load(open(ports))
    parts = []
    t = Image.new("RGBA", (W, 120), BG)
    dr = ImageDraw.Draw(t)
    dr.text((16, 10), "Circulator T06i: every hose lands in a port", font=font(34, True), fill=HEAD)
    dr.text((16, 58), "Nozzles on pads, adaptors on the tanks' own nozzles, saddles on the", font=font(22), fill=SUB)
    dr.text((16, 86), "glass legs, glands for cables. Form, tone, fittings and kit unchanged.", font=font(22), fill=SUB)
    parts.append(t)
    cell = (W - 3 * 12) // 2
    grid = Image.new("RGBA", (W, 2 * (cell + 34) + 12), BG)
    for i, d in enumerate(ec.DIRS):
        g = ground(os.path.join(full, f"run-{d}", "hi", "idle.png"))
        g = g.crop((g.width * 0.06, g.height * 0.08, g.width * 0.94, g.height * 0.94))
        g.thumbnail((cell, cell), Image.LANCZOS)
        x, y = 12 + (i % 2) * (cell + 12), (i // 2) * (cell + 34)
        ImageDraw.Draw(grid).text((x + 4, y + 4), f"facing {d}", font=font(22, True), fill=TEXT)
        grid.alpha_composite(g, (x + (cell - g.width) // 2, y + 32))
    parts.append(grid)
    h = Image.new("RGBA", (W, 44), BG)
    ImageDraw.Draw(h).text((16, 8), "Before (T06h) | after (T06i), facing north, 4x", font=font(24, True), fill=HEAD)
    parts.append(h)
    gb = ec.plate(bdir, "north")
    ga = ground(os.path.join(full, "run-north", "hi", "idle.png"))
    pw = (W - 3 * 12) // 2
    side = 0.8
    for nm, e_ in SHOW:
        e = P[nm][e_]
        b = ec.crop(gb, e["p"], "north", side).resize((pw // 2 - 3, pw // 2 - 3), Image.LANCZOS)
        a = ec.crop(ga, ec.port_centre(e), "north", side).resize((pw // 2 - 3, pw // 2 - 3), Image.LANCZOS)
        parts.append((nm, e_, b, a))
    rows = []
    pairs = [p for p in parts if isinstance(p, tuple)]
    parts = [p for p in parts if not isinstance(p, tuple)]
    for k in range(0, len(pairs), 2):
        r = Image.new("RGBA", (W, pw // 2 + 40), BG)
        for j, (nm, e_, b, a) in enumerate(pairs[k:k + 2]):
            x = 12 + j * (pw + 12)
            r.alpha_composite(b, (x, 0))
            r.alpha_composite(a, (x + b.width + 6, 0))
            what = ec.RUNS[nm][0]
            to = ec.RUNS[nm][1 if e_ == "a" else 2]
            ImageDraw.Draw(r).text((x, b.height + 4), f"{what}: {to}"[:52], font=font(15), fill=SUB)
        rows.append(r)
    parts += rows
    lines = [ln.rstrip("\n") for ln in open(bars)]
    b_ = Image.new("RGBA", (W, 50 + 30 * len(lines)), BG)
    dr = ImageDraw.Draw(b_)
    dr.text((16, 8), "Bars", font=font(26, True), fill=HEAD)
    for i, ln in enumerate(lines):
        dr.text((16, 48 + 30 * i), ln, font=font(20), fill=TEXT)
    parts.append(b_)
    out_im = Image.new("RGBA", (W, sum(p.height for p in parts) + 10), BG)
    y = 0
    for p in parts:
        out_im.alpha_composite(p, (0, y))
        y += p.height
    out_im.convert("RGB").save(out)
    print("wrote", out, out_im.size)


if __name__ == "__main__":
    main(*sys.argv[1:6])
