#!/usr/bin/env python3
"""Reaction Plant round 4: what vanilla's surfaces do, measured, against rounds 3 and 4.

  python3 r4_texture_study.py <out.png> --plate "label=path[@x,y]" [--plate ...] [--factorio <data>]

Liam on round 3: "the texturing also doesn't fit basegame factorio". Round 3 measured
inside vanilla's finish.py / tonal.py ranges and still did not look like vanilla, so this
measures what those two do not: colour temperature and saturation, where the rust is,
how soft the shading is, the edge highlights and the sheen on round parts, how much
small detail survives. Every number is on the opaque plate at 64 px a tile (sprite
size), well inside the silhouette (alpha eroded 9 px, as finish.py does).

  warmth     mean R - B over the plate (0-255 units): vanilla's steel is brown-grey
  sat        mean HSV saturation (0-1) of pixels with V over 40, and in three tone
             bands: dark (L < 50), mid (50-120), light (L >= 120)
  rust       share of pixels with hue 8-45 deg, saturation over 0.38, V over 45:
             rust, ochre and brown paint
  cool       share of pixels whose B exceeds R: cool greys, blue-greys, teal
  lightW     mean R - B of the brightest 5 %: are the highlights warm cream or cold white
  darkW      mean R - B of the darkest 25 %: are the shadows warm brown or cold grey
  soft       mid / fine (finish.py's ratio inverted): form at a few px against speckle;
             higher = softer, painterly shading
  edgehi     share of pixels 30 above their 5x5 neighbourhood: thin bright edge lines
  detail     share of pixels with a 3x3 Sobel gradient over 60: hard small detail
  p5/p50/p95 luminance, as tonal.py

Crops: one per building, 1.5 tiles square at the sprite's own size, shown at 2x and 4x
side by side; vanilla first, then the plates passed with --plate (label=path@x,y:
the crop's top-left in sprite px; default the sprite's centre).
"""
import argparse
import colorsys
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("--plate", action="append", default=[])
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
args = ap.parse_args()
ENT = f"{args.factorio}/base/graphics/entity"
CROP = 96
BG = (30, 29, 28, 255)
GROUND = (74, 66, 58, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)

# (label, file, the sprite's own rectangle, the crop's top-left)
VANILLA = [
    ("oil refinery", "oil-refinery/north/oil-refinery-north", (0, 0, 356, 446), (120, 150)),
    ("chemical plant", "chemical-plant/chemical-plant-north-base", (0, 0, 204, 292), (8, 110)),
    ("assembler 3", "assembling-machine-3/assembling-machine-3-base", (0, 0, 196, 192), (12, 18)),
    ("pumpjack (base)", "pumpjack/pumpjack-base", (0, 0, 261, 273), (60, 38)),
    ("storage tank", "storage-tank/storage-tank", (0, 0, 219, 235), (14, 10)),
]


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def measure(im):
    a = im.getchannel("A")
    ero = a.filter(ImageFilter.MinFilter(9)).get_flattened_data()
    rgb = im.convert("RGB")
    L = im.convert("L")
    b3 = L.filter(ImageFilter.BoxBlur(1)).get_flattened_data()
    b5 = L.filter(ImageFilter.BoxBlur(2)).get_flattened_data()
    b9 = L.filter(ImageFilter.BoxBlur(4)).get_flattened_data()
    gx = L.filter(ImageFilter.Kernel((3, 3), (-1, 0, 1, -2, 0, 2, -1, 0, 1), 1, 128)).get_flattened_data()
    gy = L.filter(ImageFilter.Kernel((3, 3), (-1, -2, -1, 0, 0, 0, 1, 2, 1), 1, 128)).get_flattened_data()
    px = [(c, l, s3, s5, s9, x, y) for c, l, s3, s5, s9, x, y, e in
          zip(rgb.get_flattened_data(), L.get_flattened_data(), b3, b5, b9, gx, gy, ero) if e > 250]
    n = len(px)
    hsv = [colorsys.rgb_to_hsv(*(v / 255 for v in p[0])) for p in px]
    lit = [(h, s, v, p[1]) for (h, s, v), p in zip(hsv, px) if v > 40 / 255]
    band = lambda lo, hi: [s for h, s, v, l in lit if lo <= l < hi]
    mean = lambda xs: sum(xs) / max(1, len(xs))
    byL = sorted(px, key=lambda p: p[1])
    warm = lambda ps: mean([p[0][0] - p[0][2] for p in ps])
    Ls = [p[1] for p in byL]
    q = lambda f: round(Ls[int(f * (n - 1))])
    fine = mean([abs(p[1] - p[2]) for p in px])
    mid = mean([abs(p[2] - p[4]) for p in px])
    return dict(
        warmth=warm(px),
        sat=mean([s for _, s, _, _ in lit]),
        sat_d=mean(band(0, 50)), sat_m=mean(band(50, 120)), sat_l=mean(band(120, 256)),
        rust=sum(1 for h, s, v, _ in lit if 8 / 360 <= h <= 45 / 360 and s > 0.38 and v > 45 / 255) / n,
        cool=sum(1 for p in px if p[0][2] > p[0][0]) / n,
        lightW=warm(byL[int(0.95 * n):]), darkW=warm(byL[:n // 4]),
        soft=mid / fine if fine else 0.0,
        edgehi=sum(1 for p in px if p[1] - p[3] > 30) / n,
        detail=sum(1 for p in px if ((p[5] - 128) ** 2 + (p[6] - 128) ** 2) ** 0.5 > 60) / n,
        p5=q(0.05), p50=q(0.5), p95=q(0.95))


ROWS = []
for label, stem, rect, at in VANILLA:
    ROWS.append((label, Image.open(f"{ENT}/{stem}.png").convert("RGBA").crop(rect), at, True))
for spec in args.plate:
    label, rest = spec.split("=", 1)
    path, _, xy = rest.partition("@")
    im = Image.open(path).convert("RGBA")
    at = tuple(int(v) for v in xy.split(",")) if xy else (im.width // 2 - CROP // 2, im.height // 2 - CROP // 2)
    ROWS.append((label, im, at, False))

M = [(label, measure(im)) for label, im, _, _ in ROWS]

# --------------------------------------------------------------------- the sheet
GAP = 14
cells = []
for label, im, (x, y), van in ROWS:
    c = im.crop((x, y, x + CROP, y + CROP))
    g = Image.new("RGBA", c.size, GROUND)
    g.alpha_composite(c)
    cells.append((label, g.resize((CROP * 2, CROP * 2), Image.NEAREST),
                  g.resize((CROP * 4, CROP * 4), Image.NEAREST), van))
colw = CROP * 6 + GAP
per_row = 3
rows = (len(cells) + per_row - 1) // per_row
W = GAP + per_row * (colw + GAP)
s = Image.new("RGBA", (W, 4000), BG)
d = ImageDraw.Draw(s)
d.text((GAP, 12), "REACTION PLANT ROUND 4 -- TEXTURE STUDY: VANILLA'S SURFACES AGAINST ROUND 3 AND ROUND 4",
       font=font(24, True), fill=TEXT)
d.text((GAP, 46), "Each crop 1.5 tiles square at sprite size (64 px a tile), shown at 2x and at 4x, on the game's "
       "ground colour. Measures over the whole plate, inside the silhouette.", font=font(14), fill=SUB)
y = 76
for i, (label, c2, c4, van) in enumerate(cells):
    col, row = i % per_row, i // per_row
    x0, y0 = GAP + col * (colw + GAP), y + row * (CROP * 4 + 40)
    d.text((x0, y0), label + ("" if van else "  (ours)"), font=font(15, True), fill=HEAD if not van else TEXT)
    s.alpha_composite(c2, (x0, y0 + 22))
    s.alpha_composite(c4, (x0 + CROP * 2 + GAP, y0 + 22))
y += rows * (CROP * 4 + 40) + 10

# table
cols = [("", 230), ("warmth", 80), ("sat", 60), ("sat dark", 80), ("sat mid", 72), ("sat light", 80),
        ("rust", 64), ("cool", 64), ("lightW", 72), ("darkW", 70), ("soft", 60), ("edgehi", 72),
        ("detail", 70), ("p5", 44), ("p50", 48), ("p95", 48)]
d.text((GAP, y), "MEASURED (whole plate, 64 px a tile)", font=font(16, True), fill=HEAD)
y += 26
x = GAP
for name, w in cols:
    d.text((x, y), name, font=font(13, True), fill=SUB)
    x += w
y += 20
for label, m in M:
    vals = [label, f"{m['warmth']:.1f}", f"{m['sat']:.2f}", f"{m['sat_d']:.2f}", f"{m['sat_m']:.2f}",
            f"{m['sat_l']:.2f}", f"{m['rust'] * 100:.0f} %", f"{m['cool'] * 100:.0f} %", f"{m['lightW']:.1f}",
            f"{m['darkW']:.1f}", f"{m['soft']:.2f}", f"{m['edgehi'] * 100:.1f} %", f"{m['detail'] * 100:.1f} %",
            str(m["p5"]), str(m["p50"]), str(m["p95"])]
    x = GAP
    for v, (_, w) in zip(vals, cols):
        d.text((x, y), v, font=font(13), fill=TEXT)
        x += w
    y += 19
y += 12
NOTES = os.environ.get("STUDY_NOTES", "")
if NOTES:
    d.text((GAP, y), "WHAT VANILLA DOES, AND WHAT ROUND 4 CHANGED", font=font(16, True), fill=HEAD)
    y += 26
    for ln in open(NOTES).read().splitlines():
        d.text((GAP + 8, y), ln, font=font(14), fill=TEXT)
        y += 19
s = s.crop((0, 0, W, y + 16))
s.convert("RGB").save(args.out)
print(args.out, s.size)
for label, m in M:
    print(f"{label:28s} " + " ".join(f"{k} {v:.3f}" if isinstance(v, float) else f"{k} {v}" for k, v in m.items()))
