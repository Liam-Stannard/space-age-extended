#!/usr/bin/env python3
"""T06h: before/after crops of what the refine changed -- form 1 as T06g committed it (round-forms/forms.py at its
sun 9.46) beside the refined casing (round-forms-refine/forms.py at the refine's tone), idle plates (forms.py --idle,
downsampled to sprite size), every direction. A picture, not a measure.

  python3 before_after.py <before x1 dir> <after x1 dir> <out.png> <before label> <after label>

Top: per direction, the whole idle plate at 2x, before and after, the restored kit circled and numbered on both (on
the before, where it now stands). Below: each restored unit at 3x in all four directions, before and after.
Model space to screen (tools/blender/rig.py: a 60-degree camera, the ground stretched 1/sin 60): a point (x, y, z),
y north, lands x tiles right and y + 0.5 z tiles up of the entity's origin, the canvas's centre; a direction is the
building turned as the engine turns it (90 degrees clockwise per step).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import form_plans  # noqa: E402

BEFORE, AFTER, OUT, LB, LA = sys.argv[1:6]
DIRS = ("north", "east", "south", "west")
PPT = 64
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT, HEAD, RING = (228, 222, 210), (240, 200, 120), (255, 196, 60)
ZC = form_plans.ZC
TK = form_plans.TAKES["casing"]
ex, mf, dr = TK["exchanger"], TK["manifold"], TK["drain"]
KIT = [
    ("side-nozzle pot", (TK["pot"][0], TK["pot"][1], ZC + 0.7)),
    ("exchanger", ((ex[0] + ex[1]) / 2, ex[2], ZC + 0.38)),
    ("sampling manifold", ((mf[0] + mf[2]) / 2, (mf[1] + mf[3]) / 2, ZC + 0.3)),
    ("drain skid", ((dr[0] + dr[2]) / 2, (dr[1] + dr[3]) / 2, ZC + 0.3)),
]


def font(n, bold=False):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),):
        if os.path.isfile(f):
            return ImageFont.truetype(f, n)
    return ImageFont.load_default()


def screen(p, d):
    """Model point -> (sx, sy) in tiles from the origin, screen y down, the building facing d."""
    x, y, z = p
    xf, yf = x, -y                        # Factorio's axes: y down
    for _ in range(DIRS.index(d)):
        xf, yf = -yf, xf                  # a quarter turn clockwise, as the engine turns a building
    return xf, yf - 0.5 * z


def plate(src, d, k):
    im = Image.open(os.path.join(src, f"idle-{d}.png")).convert("RGBA")
    g = Image.new("RGBA", im.size, GROUND)
    g.alpha_composite(im)
    return g.resize((im.width * k, im.height * k), Image.NEAREST), (im.width * k / 2, im.height * k / 2)


def ring(g, c, k, n, r=0.42):
    dr_ = ImageDraw.Draw(g)
    R = r * PPT * k
    dr_.ellipse([c[0] - R, c[1] - R, c[0] + R, c[1] + R], outline=RING, width=max(2, k))
    dr_.text((c[0] + R * 0.75, c[1] - R * 1.05), str(n), font=font(10 * k, True), fill=RING)


def label(im, text, size=18):
    h = size + 12
    out = Image.new("RGBA", (im.width, im.height + h), BG)
    ImageDraw.Draw(out).text((6, 4), text, font=font(size, True), fill=TEXT)
    out.alpha_composite(im, (0, h))
    return out


def row(ims, gap=8):
    w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    h = max(i.height for i in ims)
    out = Image.new("RGBA", (w, h), BG)
    x = 0
    for i in ims:
        out.alpha_composite(i, (x, 0))
        x += i.width + gap
    return out


def stack(ims, gap=10):
    w = max(i.width for i in ims)
    h = sum(i.height for i in ims) + gap * (len(ims) - 1)
    out = Image.new("RGBA", (w, h), BG)
    y = 0
    for i in ims:
        out.alpha_composite(i, (0, y))
        y += i.height + gap
    return out


def whole(src, d, k=2):
    g, o = plate(src, d, k)
    for n, (_, p) in enumerate(KIT, 1):
        sx, sy = screen(p, d)
        ring(g, (o[0] + sx * PPT * k, o[1] + sy * PPT * k), k, n)
    m = int(0.3 * PPT * k)     # trim the empty canvas: 5.6 tiles wide round the footprint, the rise above
    return g.crop((int(o[0] - 2.8 * PPT * k), int(o[1] - 3.6 * PPT * k), int(o[0] + 2.8 * PPT * k),
                   int(o[1] + 2.8 * PPT * k) + m))


def zoom(src, d, p, k=3, side=1.5):
    g, o = plate(src, d, k)
    sx, sy = screen(p, d)
    c = (o[0] + sx * PPT * k, o[1] + sy * PPT * k)
    h = side / 2 * PPT * k
    return g.crop((int(c[0] - h), int(c[1] - h), int(c[0] + h), int(c[1] + h)))


sec = [label(Image.new("RGBA", (2300, 1), BG), "Before / after (T06h): form 1 as T06g committed it beside the refined casing; "
             "idle plates", 22),
       label(Image.new("RGBA", (2300, 1), BG), "the restored kit circled where it stands (on the before too, where it was "
             "missing): " + ", ".join(f"{n} {t}" for n, (t, _) in enumerate(KIT, 1)), 18)]
for d in DIRS:
    sec.append(row([label(whole(BEFORE, d), f"facing {d}, before: {LB}"), label(whole(AFTER, d), f"facing {d}, after: {LA}")]))
for n, (t, p) in enumerate(KIT, 1):
    cells = []
    for d in DIRS:
        cells.append(label(zoom(BEFORE, d, p), f"{d} before", 15))
        cells.append(label(zoom(AFTER, d, p), f"{d} after", 15))
    sec.append(label(row(cells, 6), f"{n} {t}, 3x, 1.5 tiles square round where it stands", 18))
out = stack(sec)
if max(out.size) >= 8000:
    r_ = 7990 / max(out.size)
    out = out.resize((round(out.width * r_), round(out.height * r_)), Image.LANCZOS)
out.convert("RGB").save(OUT, optimize=True)
print(OUT, out.size)
