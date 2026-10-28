#!/usr/bin/env python3
"""Vent Pump, round 3: contact-sheet.png, all eight concepts, round 2 above round 3.

  python3 vpa3_contact_all.py

Built by whichever artist finishes second (the orchestrator's rule). Reads only what both halves
have already written: frame 0 of each concept's 1x GIF in round-2/ and round-3/, the measures in
measures-a.json and measures-b.json, and the references from round 1's compare-plates.png
(concept/vent-pump/model/, 1x, one ground) as contact sheet B crops them.
"""
import glob
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
R2 = os.path.join(HERE, "..", "round-2")
VP = os.path.normpath(os.path.join(HERE, "..", ".."))
BG, HEAD, SUB = (30, 29, 28, 255), (240, 200, 120), (175, 168, 156)


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def frame0(path):
    im = Image.open(path)
    im.seek(0)
    return im.convert("RGBA")


def captioned(im, cap, size=12):
    lines = cap.split("\n")
    w = max([im.width] + [int(font(size, True).getlength(ln)) + 10 for ln in lines])
    hh = 6 + (size + 6) * len(lines)
    c = Image.new("RGBA", (w, im.height + hh), BG)
    d = ImageDraw.Draw(c)
    for i, ln in enumerate(lines):
        d.text((4, 4 + (size + 6) * i), ln, font=font(size, i == 0), fill=HEAD if i == 0 else SUB)
    c.alpha_composite(im, (0, hh))
    return c


def hrow(ims, gap=16):
    r = Image.new("RGBA", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), BG)
    x = 0
    for i in ims:
        r.alpha_composite(i, (x, 0))
        x += i.width + gap
    return r


def vstack(ims, gap=16):
    r = Image.new("RGBA", (max(i.width for i in ims), sum(i.height for i in ims) + gap * (len(ims) - 1)), BG)
    y = 0
    for i in ims:
        r.alpha_composite(i, (0, y))
        y += i.height + gap
    return r


ma = json.load(open(os.path.join(HERE, "measures-a.json")))
mb = json.load(open(os.path.join(HERE, "measures-b.json")))


def caption3(num):
    if num in ("01", "02", "05", "07"):
        m = ma[str(int(num))]
        return f"cover {m['cover_north']} %, glow {m['glow_pct']} %, moving {m['moving_pct']} %"
    m = mb[num]
    return f"cover {m['cover_pct']} %, glow {m['glow_pct']} %, moving {m['moving_pct']} %"


def row(nums, folder, rnd):
    out = []
    for num in nums:
        g = sorted(glob.glob(os.path.join(folder, f"{num}-*-1x.gif")))[0]
        nm = os.path.basename(g)[3:-7].replace("the-", "").replace("-", " ").title()
        cap = f"{int(num)}. {nm}, round {rnd}" + (f"\n{caption3(num)}" if rnd == 3 else "")
        out.append(captioned(frame0(g), cap))
    return hrow(out)


cp = Image.open(os.path.join(VP, "model", "compare-plates.png")).convert("RGBA")
refs = hrow([captioned(cp.crop((336 * i, 46, 336 * i + 320, 430)), cap) for i, cap in
             ((0, "vanilla pumpjack 3x3 (frame 0)"), (1, "the adopted plate (v4, shipped)"),
              (3, "round 1's model (set aside), working"))])
A, B = ("01", "02", "05", "07"), ("08", "09", "10", "19")
rows = [refs, captioned(row(A, R2, 2), "ARTIST A, ROUND 2", 13), captioned(row(A, HERE, 3), "ARTIST A, ROUND 3", 13),
        captioned(row(B, R2, 2), "ARTIST B, ROUND 2", 13), captioned(row(B, HERE, 3), "ARTIST B, ROUND 3", 13)]
W = max(r.width for r in rows) + 20
head = Image.new("RGBA", (W, 76), BG)
d = ImageDraw.Draw(head)
d.text((10, 6), "VENT PUMP, ROUND 3 -- THE EIGHT CONCEPTS, ROUND 2 ABOVE ROUND 3", font=font(20, True), fill=HEAD)
d.text((10, 34), "64 px a tile, one ground, facing north (helium-3 in south, molten kamacite out north). Top: vanilla's "
                 "pumpjack, the adopted plate, round 1's model.", font=font(12), fill=SUB)
d.text((10, 52), "Then each half's four, round 2 above round 3 (frame 0 of each 1x GIF). Round 3: the grey-violet "
                 "helium line (helium-colour.txt), ports as ports.txt.", font=font(12), fill=SUB)
sheet = vstack([head] + rows)
pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
pad.alpha_composite(sheet, (10, 10))
p = os.path.join(HERE, "contact-sheet.png")
pad.convert("RGB").save(p)
print(p, pad.size)
