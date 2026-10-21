#!/usr/bin/env python3
"""Gas Pump 3x3, options round: the clipping check by eye (Liam, 2026-10-21), one crops sheet a take.

  python3 -B gp_crops.py --full <renders> --out <round dir> [--only 1,2,3]

For every cable, hose and pipe run the take registers (meta.json's "pipes", the kit's check_ends: name and both
ends in model tiles), each end cropped at 2x in all four directions: north from working frame 0, east, south and
west from the kit's turned renders (rot-<d>.png, the whole machine a quarter turn round, working frame 0). The end
is placed on the canvas by the camera's projection (64 px a tile; a point at height z shows z/2 tiles up the screen;
the turn applied to x, y first), so a crop is centred within a few px of it. Above the crops, the whole take at 2x
in the four directions, for runs that cross other parts. Every crop is looked at; what was found is in the report.

Writes <n>-<slug>-crops.png into <out>.
"""
import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("--full", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--only", default="1,2,3")
args = ap.parse_args()
CANVAS, ORIGIN = (352, 352), (160, 208)
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
HEAD, SUB = (240, 200, 120), (175, 168, 156)
SLUG = {1: "the-gas-jack", 2: "the-flywheel-compressor", 3: "the-gas-bell"}
TURN = {"north": lambda x, y: (x, y), "east": lambda x, y: (y, -x), "south": lambda x, y: (-x, -y),
        "west": lambda x, y: (-y, x)}
K = 2
HALF = 30                         # the crop's half size at 1x (a ~1 tile window)


def font(n, b=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if b else "") + ".ttf", n)


def load(path):
    im = Image.open(path).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    im = im.convert("RGBa").resize((CANVAS[0] * K, CANVAS[1] * K), Image.LANCZOS).convert("RGBA")
    g = Image.new("RGBA", im.size, GROUND)
    g.alpha_composite(im)
    return g


def px(p, d):
    x, y = TURN[d](p[0], p[1])
    return (ORIGIN[0] + 64 * x) * K, (ORIGIN[1] - 64 * (y + p[2] / 2)) * K


def cap(im, text, size=11):
    c = Image.new("RGBA", (im.width, im.height + size + 6), BG)
    ImageDraw.Draw(c).text((2, 2), text, font=font(size), fill=SUB)
    c.alpha_composite(im, (0, size + 6))
    return c


def row(ims, gap=6):
    r = Image.new("RGBA", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), BG)
    x = 0
    for i in ims:
        r.alpha_composite(i, (x, 0))
        x += i.width + gap
    return r


def stack(ims, gap=8):
    r = Image.new("RGBA", (max(i.width for i in ims), sum(i.height for i in ims) + gap * (len(ims) - 1)), BG)
    y = 0
    for i in ims:
        r.alpha_composite(i, (0, y))
        y += i.height + gap
    return r


def build(n):
    d = os.path.join(args.full, str(n))
    meta = json.load(open(os.path.join(d, "meta.json")))
    views = {"north": load(os.path.join(d, "working-00.png"))}
    for dn in ("east", "south", "west"):
        views[dn] = load(os.path.join(d, f"rot-{dn}.png"))
    whole = row([cap(v.crop((0, 40, CANVAS[0] * K, CANVAS[1] * K - 20)), dn, 14) for dn, v in views.items()], 10)
    rows = []
    for P in meta["pipes"]:
        cells = []
        for k, e in enumerate(P["ends"]):
            for dn in ("north", "east", "south", "west"):
                cx, cy = px(e["at"], dn)
                box = (int(cx - HALF * K), int(cy - HALF * K), int(cx + HALF * K), int(cy + HALF * K))
                c = views[dn].crop(box)
                dr = ImageDraw.Draw(c)
                dr.ellipse([HALF * K - 5, HALF * K - 5, HALF * K + 5, HALF * K + 5], outline=(120, 200, 255), width=1)
                cells.append(cap(c, f"{'from' if k == 0 else 'to'} {e['to'] or 'AIR'}, {dn}"))
        r = row(cells)
        head = Image.new("RGBA", (r.width, 22), BG)
        ImageDraw.Draw(head).text((2, 2), f"{'OK' if P['ok'] else 'LOOSE'} -- {P['name']}", font=font(14, True),
                                  fill=HEAD)
        rows.append(stack([head, r], 2))
    title = Image.new("RGBA", (whole.width, 52), BG)
    dt = ImageDraw.Draw(title)
    dt.text((6, 4), f"GAS PUMP 3x3, TAKE {n}: CLIPPING CHECK BY EYE, 2x, FOUR DIRECTIONS", font=font(20, True), fill=HEAD)
    dt.text((6, 30), "Each run's two ends (blue ring: the end as registered), working frame 0; the whole take above for "
                     "crossings. Turned renders are the whole machine a quarter turn round.", font=font(12), fill=SUB)
    sheet = stack([title, whole] + rows, 12)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    path = os.path.join(args.out, f"{n}-{SLUG[n]}-crops.png")
    pad.convert("RGB").save(path)
    print(path, pad.size)


for n in [int(v) for v in args.only.split(",")]:
    build(n)
