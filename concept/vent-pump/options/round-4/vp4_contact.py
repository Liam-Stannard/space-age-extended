#!/usr/bin/env python3
"""Vent Pump, round 4 (T03): the contact sheet of all eight concepts, round 3 above round 4, at game scale.

  python3 vp4_contact.py [--out contact-sheet.png]

Round 3: frame 0 of each concept's 1x GIF in ../round-3/. Round 4: the frame of the deepest draw of
each concept's 1x GIF here (the helium sight glass flushed peach-pink), and frame 0 beside it is in
each concept's own sheet. Captions from measures-a.json and measures-b.json here (round 4) and in
../round-3/ (round 3). 64 px a tile, one ground.
"""
import argparse
import glob
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.join(HERE, "..", "round-3")
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(HERE, "contact-sheet.png"))
args = ap.parse_args()
BG = (30, 29, 28, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)
A = ["01", "02", "05", "07"]
B = ["08", "09", "10", "19"]


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def frame(path, i=0):
    g = Image.open(path)
    g.seek(i)
    return g.convert("RGBA")


def cap(im, lines, w=None):
    w = max(im.width, w or 0, max(int(font(12, True).getlength(s)) + 4 for s in lines))
    h = 18 * len(lines) + 6
    o = Image.new("RGBA", (w, im.height + h), BG)
    d = ImageDraw.Draw(o)
    for i, s in enumerate(lines):
        d.text((0, 18 * i), s, font=font(12, i == 0), fill=TEXT if i == 0 else SUB)
    o.alpha_composite(im, (0, h))
    return o


def row(ims, gap=16):
    o = Image.new("RGBA", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), BG)
    x = 0
    for i in ims:
        o.alpha_composite(i, (x, 0))
        x += i.width + gap
    return o


m3 = {**{k.zfill(2): v for k, v in json.load(open(os.path.join(R3, "measures-a.json"))).items()},
      **json.load(open(os.path.join(R3, "measures-b.json")))}
m4 = {**{k.zfill(2): v for k, v in json.load(open(os.path.join(HERE, "measures-a.json"))).items()},
      **json.load(open(os.path.join(HERE, "measures-b.json")))}


def cover(m):
    return m.get("cover_north", m.get("cover_pct"))


rows = []
for half, nums in (("ARTIST A", A), ("ARTIST B", B)):
    r3, r4 = [], []
    for n in nums:
        g3 = sorted(glob.glob(os.path.join(R3, f"{n}-*-1x.gif")) + glob.glob(os.path.join(R3, f"{int(n)}-*-1x.gif")))[0]
        g4 = sorted(glob.glob(os.path.join(HERE, f"{n}-*-1x.gif")))[0]
        name = os.path.basename(g4)[3:-7].replace("-", " ").title()
        a, b = m3[n], m4[n]
        gm = b["glass"]
        r3.append(cap(frame(g3), [f"{int(n)}. {name}, round 3", f"cover {cover(a)} %, frame 0"]))
        r4.append(cap(frame(g4, gm["draw_frame"]),
                      [f"{int(n)}. {name}, round 4", f"cover {cover(b)} %, frame {gm['draw_frame']} (the draw)",
                       f"helium glow peak {gm['he_peak_1x']} (1x)",
                       f"in the glass: white {gm['in_glass']['white_1x'] + gm['in_glass']['white_2x']}, "
                       f"clipped {gm['in_glass']['clipped_1x'] + gm['in_glass']['clipped_2x']}",
                       f"pale cyan {gm['pale_cyan_px']}, frost {gm['frost_px']}"]))
    rows.append((half + ", ROUND 3", row(r3)))
    rows.append((half + ", ROUND 4: THE HELIUM SIGHT GLASS (MIX A)", row(r4)))
W = max(r.width for _, r in rows) + 40
title = "VENT PUMP, ROUND 4 (T03) -- THE EIGHT CONCEPTS, ROUND 3 ABOVE ROUND 4"
note = ("64 px a tile, one ground, facing north (helium-3 in south, melt out north). Round 3: frame 0 of its 1x GIF. "
        "Round 4: its 1x GIF at the deepest draw, the helium sight glass flushed peach-pink (mix A); idle it is unlit "
        "and still. The study's kit changes carried over: bands #9C8CB0, ceramic gauge faces, dark-steel flanges, "
        "non-refracting glass.")
H = 70 + 16 * 3 + sum(r.height + 34 for _, r in rows)
o = Image.new("RGBA", (W, H), BG)
d = ImageDraw.Draw(o)
d.text((20, 10), title, font=font(20, True), fill=HEAD)
words, line, nl = note.split(), "", []
for w_ in words:
    if font(12).getlength(line + " " + w_) > W - 40 and line:
        nl.append(line)
        line = w_
    else:
        line = (line + " " + w_).strip()
nl.append(line)
for i, ln in enumerate(nl):
    d.text((20, 40 + 16 * i), ln, font=font(12), fill=SUB)
y = 70 + 16 * (len(nl) - 1)
for t, r in rows:
    d.text((20, y), t, font=font(14, True), fill=HEAD)
    o.alpha_composite(r, (20, y + 24))
    y += r.height + 34
if max(o.size) > 7900:
    k = 7900 / max(o.size)
    o = o.resize((round(o.width * k), round(o.height * k)), Image.LANCZOS)
o.convert("RGB").save(args.out)
print(args.out, o.size)
