#!/usr/bin/env python3
"""Reaction Plant round 5: which paints vanilla's machines carry, and how much of the plate each takes.

  python3 r5_colour_study.py <out.png> --plate "label=path" [--plate ...] [--factorio <data>]
                             [--notes <txt>] [--json <out.json>]

Liam on round 4: "everything is the same, add some colour and more details to break up
the rust texture." Round 4's texture study measured warmth, rust share and softness over
the whole plate, and round 4 hit vanilla's numbers by making every part the same rusty
brown. This measures what a whole-plate mean cannot see: whether the plate is made of
different-coloured parts.

Every opaque pixel (alpha over 250, eroded 5 px) at sprite size (64 px a tile) is put in
one family by HSV (hue in degrees, S and V 0-1):

  dark          V < 0.16                               shadow, dark steel, rubber
  bare metal    S < 0.22, V >= 0.55                    bright steel, cream highlights
  grey steel    S < 0.22, 0.16 <= V < 0.55             painted and dirty steel
  tan           S 0.22-0.45, hue 10-55                 brown-grey, dust, weathered paint
  rust          S >= 0.45, hue 10-38, V < 0.62         rust, oxide brown
  copper        S >= 0.45, hue 10-38, V >= 0.62        copper, orange, bright brass
  yellow        S >= 0.40, hue 38-55                   ochre and yellow paint, brass
  red           S >= 0.35, hue < 10 or >= 330          oxide red, red paint, handwheels
  green         S >= 0.22, hue 55-165                  weathered green paint, verdigris
  blue          S >= 0.18, hue 165-290                 blue-grey paint, cables, fluid
  (what is left: low-saturation purples and pinks, counted as "other")

and two numbers say whether the parts differ:

  variety       the spread of colour between 8 x 8 px patches: the standard deviation of
                the patches' mean (a*, b*) in CIELAB, as one radius. Paint zones of
                different colour push it up; one finish everywhere keeps it low.
  families>=4%  how many families hold at least 4 % of the plate.

The sheet: each plate at 1x on the game's ground, a bar of its family shares, each
family's median colour as a swatch, and the table.
"""
import argparse
import colorsys
import json
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("--plate", action="append", default=[])
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
ap.add_argument("--notes")
ap.add_argument("--json")
args = ap.parse_args()
E = f"{args.factorio}/base/graphics/entity"
A = f"{args.factorio}/space-age/graphics/entity"
BG = (30, 29, 28, 255)
GROUND = (74, 66, 58, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)

VANILLA = [
    ("oil refinery", f"{E}/oil-refinery/north/oil-refinery-north.png", (0, 0, 356, 446)),
    ("chemical plant", f"{E}/chemical-plant/chemical-plant-north-base.png", (0, 0, 204, 292)),
    ("pumpjack (base)", f"{E}/pumpjack/pumpjack-base.png", (0, 0, 261, 273)),
    ("assembler 3", f"{E}/assembling-machine-3/assembling-machine-3-base.png", (0, 0, 196, 192)),
    ("foundry (SA)", f"{A}/foundry/foundry-base.png", (0, 0, 356, 384)),
    ("EM plant (SA)", f"{A}/electromagnetic-plant/electromagnetic-plant-base.png", (0, 0, 238, 252)),
    ("storage tank", f"{E}/storage-tank/storage-tank.png", (0, 0, 219, 235)),
]
FAM = ["dark", "bare metal", "grey steel", "tan", "rust", "copper", "yellow", "red", "green", "blue", "other"]
FCOL = {"dark": (40, 36, 34), "bare metal": (214, 206, 190), "grey steel": (120, 116, 110), "tan": (150, 124, 92),
        "rust": (122, 64, 30), "copper": (206, 128, 64), "yellow": (214, 172, 40), "red": (168, 46, 36),
        "green": (92, 120, 56), "blue": (70, 110, 190), "other": (130, 100, 130)}


def family(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    h *= 360
    if v < 0.16:
        return "dark"
    if s < 0.22:
        return "bare metal" if v >= 0.55 else "grey steel"
    if 10 <= h < 38 and s >= 0.45:
        return "copper" if v >= 0.62 else "rust"
    if 38 <= h < 55 and s >= 0.40:
        return "yellow"
    if (h < 10 or h >= 330) and s >= 0.35:
        return "red"
    if 10 <= h < 55:
        return "tan"
    if 55 <= h < 165:
        return "green"
    if 165 <= h < 290:
        return "blue"
    if h < 10 or h >= 330:
        return "tan" if s < 0.35 else "red"
    return "other"


def lab(r, g, b):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    R, G, B = lin(r), lin(g), lin(b)
    X = (0.4124 * R + 0.3576 * G + 0.1805 * B) / 0.95047
    Y = 0.2126 * R + 0.7152 * G + 0.0722 * B
    Z = (0.0193 * R + 0.1192 * G + 0.9505 * B) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(X), f(Y), f(Z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def measure(im):
    a = im.getchannel("A").filter(ImageFilter.MinFilter(5))
    W, H = im.size
    rgb = im.convert("RGB").load()
    am = a.load()
    counts = {f: 0 for f in FAM}
    cols = {f: [] for f in FAM}
    n = 0
    for y in range(H):
        for x in range(W):
            if am[x, y] > 250:
                c = rgb[x, y]
                f = family(*c)
                counts[f] += 1
                if (x + y) % 3 == 0:
                    cols[f].append(c)
                n += 1
    share = {f: counts[f] / n for f in FAM}
    med = {}
    for f, cs in cols.items():
        if cs:
            cs.sort(key=lambda c: sum(c))
            med[f] = cs[len(cs) // 2]
    # variety: 8 x 8 patches wholly inside
    pa, pb = [], []
    for y in range(0, H - 7, 8):
        for x in range(0, W - 7, 8):
            if all(am[x + i, y + j] > 250 for i in (0, 7) for j in (0, 7)) and am[x + 4, y + 4] > 250:
                acc = [0.0, 0.0, 0.0]
                for j in range(8):
                    for i in range(8):
                        c = rgb[x + i, y + j]
                        for k in range(3):
                            acc[k] += c[k]
                _, aa, bb = lab(*(v / 64 for v in acc))
                pa.append(aa)
                pb.append(bb)
    sd = lambda xs: math.sqrt(sum((v - sum(xs) / len(xs)) ** 2 for v in xs) / len(xs))
    variety = math.sqrt(sd(pa) ** 2 + sd(pb) ** 2)
    return dict(share=share, median=med, variety=variety, families=sum(1 for v in share.values() if v >= 0.04),
                n=n)


ROWS = []
for label, path, rect in VANILLA:
    ROWS.append((label, Image.open(path).convert("RGBA").crop(rect), True))
for spec in args.plate:
    label, path = spec.split("=", 1)
    im = Image.open(path).convert("RGBA")
    ROWS.append((label, im.crop(im.getbbox()), False))
M = [(label, measure(im)) for label, im, _ in ROWS]


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


# ------------------------------------------------------------------ the sheet
GAP = 14
TH = 300                                  # thumbnails scaled to this height
cells = []
for (label, im, van), (_, m) in zip(ROWS, M):
    k = min(1.0, TH / im.height)
    t = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    g = Image.new("RGBA", t.size, GROUND)
    g.alpha_composite(t)
    cells.append((label, g, van, m))
per_row = 5
cw = max(c[1].width for c in cells) + GAP
W = GAP + per_row * cw
s = Image.new("RGBA", (max(W, 1500), 6000), BG)
d = ImageDraw.Draw(s)
d.text((GAP, 12), "REACTION PLANT ROUND 5 -- COLOUR STUDY: WHICH PAINTS VANILLA'S MACHINES CARRY, AND HOW MUCH",
       font=font(22, True), fill=TEXT)
d.text((GAP, 44), "Each plate at sprite size (scaled to fit), every opaque pixel in one family by HSV; the bar is the "
       "families' shares, the swatches each family's median colour where it holds 3 % or more.", font=font(14), fill=SUB)
y = 76
for i, (label, g, van, m) in enumerate(cells):
    col, row = i % per_row, i // per_row
    x0, y0 = GAP + col * cw, y + row * (TH + 150)
    d.text((x0, y0), label + ("" if van else "  (ours)"), font=font(14, True), fill=TEXT if van else HEAD)
    s.alpha_composite(g, (x0, y0 + 20))
    by = y0 + 26 + TH
    bw = cw - GAP
    xx = x0
    for f in FAM:
        w = round(bw * m["share"][f])
        if w:
            d.rectangle([xx, by, xx + w, by + 16], fill=FCOL[f])
            xx += w
    sx = x0
    for f in FAM:
        if m["share"][f] >= 0.03 and f in m["median"]:
            d.rectangle([sx, by + 22, sx + 22, by + 44], fill=m["median"][f], outline=(0, 0, 0))
            d.text((sx, by + 46), f[:5], font=font(10), fill=SUB)
            sx += 30
    d.text((x0, by + 64), f"variety {m['variety']:.1f}   families>=4% {m['families']}", font=font(12, True),
           fill=TEXT)
rows = (len(cells) + per_row - 1) // per_row
y += rows * (TH + 150) + 6
# legend
xx = GAP
for f in FAM:
    d.rectangle([xx, y, xx + 14, y + 14], fill=FCOL[f])
    d.text((xx + 18, y), f, font=font(12), fill=TEXT)
    xx += 30 + 8 * len(f)
y += 30
cols = [("", 190)] + [(f, 76) for f in FAM] + [("variety", 70), ("fam>=4%", 70)]
x = GAP
for name, w in cols:
    d.text((x, y), name, font=font(12, True), fill=SUB)
    x += w
y += 20
for label, m in M:
    vals = [label] + [f"{m['share'][f] * 100:.1f} %" for f in FAM] + [f"{m['variety']:.1f}", str(m["families"])]
    x = GAP
    for v, (_, w) in zip(vals, cols):
        d.text((x, y), v, font=font(12), fill=TEXT)
        x += w
    y += 18
y += 14
if args.notes:
    d.text((GAP, y), "WHICH PART CARRIES WHICH PAINT (vanilla), AND WHAT ROUND 5 DOES WITH IT", font=font(16, True),
           fill=HEAD)
    y += 26
    for ln in open(args.notes).read().splitlines():
        d.text((GAP + 8, y), ln, font=font(13), fill=TEXT)
        y += 18
s = s.crop((0, 0, s.width, y + 16))
s.convert("RGB").save(args.out)
print(args.out, s.size)
for label, m in M:
    print(f"{label:24s} var {m['variety']:5.1f} fam {m['families']}  " +
          " ".join(f"{f[:5]} {m['share'][f] * 100:4.1f}" for f in FAM))
if args.json:
    json.dump({label: m for label, m in M}, open(args.json, "w"), indent=1, default=list)
