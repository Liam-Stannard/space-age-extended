#!/usr/bin/env python3
"""Gas Pump 3x3 model, T08b (a brighter sight glass): the glass sweep sheet, the before/after review and its GIF.

  python3 -B glass_review.py --before <the T08 sheets dir> --after <the re-rendered sheets dir>
        --variant <label>=<sheets dir> [--variant ...] --tints <gas_pump.py --tints out-dir>
        --figures <json: {label: {"text": [lines]}}> --out <dir> [--gif-scratch <dir>]

Every panel is composed from packed sheets as the engine draws them (review_sheet.py's way, measure.py's order):
the shadow at half strength, the plate, the mech frame, and the glass layer multiplied by the vent's tint
(apply_tint = "resource-color": siderane #A8D929, helium-3 #B6A6C8) over that. A variant's sheets are the T08
sheets with only glass-<direction>.png (and meta.json's glass entries) replaced. The concept's painted gas is
gas_pump.py --tints: the model rendered with the gas painted in its own colour in Blender, the concept's paint
(frames 0 and 6, north, the window round the glass), laid over the T08 composite for the whole-machine panels.

Writes into --out:
  glass-sweep.png        per variant (and the painted reference first): the whole machine facing north at 1x in
                         both gases, and the sight glass at 2x, frames 0 and 6, both gases; its figures
  glass-review.png       before (T08) and after at 1x in both gases, the four directions; the glass at 2x before
                         and after; the by-eye clipping crops (the gas column's ends in their ferrules, 4x, every
                         direction, both gases and idle); the after glass's every frame at 4x; the figures
  glass-before-after-1x.gif  north, before above after, siderane left and helium-3 right, at 1x then the same
                         at 2x, at game speed (24 frames a second, one turn)
"""
import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("--before", required=True)
ap.add_argument("--after", required=True)
ap.add_argument("--variant", action="append", default=[])
ap.add_argument("--tints", required=True)
ap.add_argument("--figures", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

DIRS = ("north", "east", "south", "west")
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
HEAD, SUB, TXT = (240, 200, 120), (175, 168, 156), (220, 214, 204)
TINT = {"siderane": (0xA8, 0xD9, 0x29), "helium-3": (0xB6, 0xA6, 0xC8)}
GASES = ("siderane", "helium-3")
NF, CANVAS = 24, 416
FIG = json.load(open(args.figures))


def font(n, b=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if b else "") + ".ttf", n)


F_H, F_S, F_T = font(28, True), font(17, True), font(14)


class Sheets:
    def __init__(self, d):
        self.d = d
        self.meta = json.load(open(os.path.join(d, "meta.json")))
        self.cache = {}

    def layer(self, name, f=0):
        m = self.meta[name]
        w, h = m["size"]
        if name not in self.cache:
            self.cache[name] = Image.open(os.path.join(self.d, name + ".png")).convert("RGBA")
        im = self.cache[name]
        if "frames" in m:
            ll = m.get("line_length", m["frames"])
            im = im.crop(((f % ll) * w, (f // ll) * h, (f % ll) * w + w, (f // ll) * h + h))
        out = Image.new("RGBA", (CANVAS, CANVAS))
        out.alpha_composite(im, (round(CANVAS / 2 + m["shift"][0] * 64 - w / 2),
                                 round(CANVAS / 2 + m["shift"][1] * 64 - h / 2)))
        return out

    def model(self, d, f=0, gas=None):
        out = Image.new("RGBA", (CANVAS, CANVAS), GROUND)
        sh = self.layer(f"shadow-{d}")
        out.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", sh.size).split(),
                                                 sh.getchannel("A").point(lambda v: v // 2))))
        out.alpha_composite(self.layer(f"base-{d}"))
        out.alpha_composite(self.layer(f"mech-{d}", f))
        if gas:
            out.alpha_composite(tinted(self.layer(f"glass-{d}", f), TINT[gas]))
        return out

    def glass_box(self, d, pad):
        b = None
        for f in range(NF):
            g = self.layer(f"glass-{d}", f).getbbox()
            b = g if b is None else (min(b[0], g[0]), min(b[1], g[1]), max(b[2], g[2]), max(b[3], g[3]))
        return (b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad)


def tinted(im, rgb):
    r, g, b, a = im.split()
    return Image.merge("RGBA", (r.point(lambda v: v * rgb[0] // 255), g.point(lambda v: v * rgb[1] // 255),
                                b.point(lambda v: v * rgb[2] // 255), a))


def painted(base, gas, f):
    """The T08 composite with the concept's painted gas (gas_pump.py --tints, the window round the glass) over it."""
    key = "siderane" if gas == "siderane" else "helium"
    im = Image.open(os.path.join(args.tints, f"tint-{key}-{f:02d}.png")).convert("RGBa")
    im = im.resize((CANVAS, CANVAS), Image.LANCZOS).convert("RGBA")
    out = base.model("north", f, None)
    out.alpha_composite(im)
    return out


def scaled(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def trim(im, k=1, tiles=2.0):
    c = im.width / 2
    r = tiles * 64 * k
    return im.crop((round(c - r), round(c - r * 1.15), round(c + r), round(c + r * 0.85)))


def captioned(im, title, lines=(), w=None):
    w = max(w or 0, im.width)
    lh = 19
    h = 24 + lh * len(lines)
    out = Image.new("RGBA", (w, im.height + h + 4), BG)
    out.alpha_composite(im, (0, h))
    d = ImageDraw.Draw(out)
    d.text((1, 2), title, font=F_S, fill=HEAD)
    for i, s in enumerate(lines):
        d.text((1, 24 + i * lh), s, font=F_T, fill=SUB)
    return out


def row(panels, gap=12):
    w = sum(p.width for p in panels) + gap * (len(panels) - 1)
    out = Image.new("RGBA", (w, max(p.height for p in panels)), BG)
    x = 0
    for p in panels:
        out.alpha_composite(p, (x, 0))
        x += p.width + gap
    return out


def text_block(title, lines, width):
    out = Image.new("RGBA", (width, 38 + 20 * len(lines) + 6), BG)
    d = ImageDraw.Draw(out)
    d.text((0, 0), title, font=F_H, fill=HEAD)
    for i, s in enumerate(lines):
        d.text((0, 38 + i * 20), s, font=F_T, fill=TXT)
    return out


def stack(blocks, gap=20, pad=22):
    w = max(b.width for b in blocks) + 2 * pad
    h = sum(b.height for b in blocks) + gap * (len(blocks) - 1) + 2 * pad
    out = Image.new("RGBA", (w, h), BG)
    y = pad
    for b in blocks:
        out.alpha_composite(b, (pad, y))
        y += b.height + gap
    assert max(out.size) < 8000, out.size
    return out


before, after = Sheets(args.before), Sheets(args.after)
variants = [(lab, Sheets(p)) for lab, p in (v.split("=", 1) for v in args.variant)]
BOX = before.glass_box("north", 22)


def crop2(im, box=BOX, k=2):
    return scaled(im.crop(box), k)


# ================================================================ glass-sweep.png
blocks = [text_block("GAS PUMP 3x3, T08b: THE SIGHT GLASS SWEEP (north; the engine's tint of the white layer)", [
    "Each row: the whole machine at 1x in siderane and helium-3, then the sight glass at 2x, frames 0 and 6. The first row is",
    "the concept's paint (gas_pump.py --tints: the gas painted in its own colour in Blender), the reference. Every other row is",
    "a glass layer packed as pack.py does and tinted as the engine draws it (layer x tint, over the plate's empty glass).",
    "Only the glass differs between rows: plate, mech and shadow are the T08 sheets. The painted gas can be brighter than",
    "its own hex (the sun overdrives it); the engine's tint cannot: a layer at 244 draws 0.96 of the tint, the most it can.",
], 1560)]


def sweep_row(title, lines, whole, crops):
    panels = [captioned(trim(whole[g]), f"1x {g}") for g in GASES]
    panels += [captioned(crop2(c), lab) for lab, c in crops]
    return captioned(row(panels), title, lines, w=1560)


blocks.append(sweep_row("THE CONCEPT'S PAINTED GAS (the reference)", FIG.get("painted", {}).get("text", []),
                        {g: painted(before, g, 0) for g in GASES},
                        [(f"{g[:4]} f{f}", painted(before, g, f)) for g in GASES for f in (0, 6)]))
for lab, sh in variants:
    blocks.append(sweep_row(lab, FIG.get(lab, {}).get("text", []),
                            {g: sh.model("north", 0, g) for g in GASES},
                            [(f"{g[:4]} f{f}", sh.model("north", f, g)) for g in GASES for f in (0, 6)]))
stack(blocks).convert("RGB").save(os.path.join(args.out, "glass-sweep.png"))

# ================================================================ glass-review.png
blocks = [text_block("GAS PUMP 3x3, T08b: THE SIGHT GLASS, BEFORE (T08) AND AFTER", FIG.get("after", {}).get("text", []),
                     1500)]
for g in GASES:
    for lab, sh in (("BEFORE (T08)", before), ("AFTER", after)):
        blocks.append(captioned(row([captioned(trim(sh.model(d, 0, g)), d) for d in DIRS]),
                                f"{lab}, 1x, {g.upper()}, working frame 0"))
# 2x crops, before and after, north, both gases, painted beside
cr = []
for g in GASES:
    cr.append(captioned(crop2(painted(before, g, 0)), f"{g[:4]} painted"))
    cr.append(captioned(crop2(before.model("north", 0, g)), f"{g[:4]} before"))
    cr.append(captioned(crop2(after.model("north", 0, g)), f"{g[:4]} after"))
blocks.append(captioned(row(cr), "THE SIGHT GLASS AT 2x, NORTH, FRAME 0: THE CONCEPT'S PAINT, BEFORE, AFTER"))
# the clipping check by eye: the gas column and its two ferrules, 4x, every direction
for d in DIRS:
    box = after.glass_box(d, 10)
    cc = [captioned(scaled(after.model(d, f, g).crop(box), 4), f"{g[:4]} f{f}") for g in GASES for f in (0, 12)]
    cc.append(captioned(scaled(after.model(d, 0, None).crop(box), 4), "idle (empty)"))
    blocks.append(captioned(row(cc, gap=10), f"CLIPPING BY EYE, AFTER, {d.upper()}, 4x: the gas held between its two "
                                             f"ferrules, nothing past the pane or onto the run"))
# every frame of the after glass, north, 4x, helium-3 and siderane
for g in GASES:
    fs = [scaled(after.model("north", f, g).crop(BOX), 3) for f in range(NF)]
    blocks.append(captioned(row(fs, gap=4), f"AFTER, EVERY FRAME, NORTH, 3x, {g.upper()}: the drift"))
stack(blocks).convert("RGB").save(os.path.join(args.out, "glass-review.png"))

# ================================================================ glass-before-after-1x.gif
frames = []
for f in range(NF):
    tiles1 = [[trim(sh.model("north", f, g)) for g in GASES] for sh in (before, after)]
    big = [[crop2(sh.model("north", f, g)) for g in GASES] for sh in (before, after)]
    w1, h1 = tiles1[0][0].size
    w2, h2 = big[0][0].size
    W = 2 * w1 + 2 * w2 + 3 * 8
    H = max(2 * h1 + 8, 2 * h2 + 8) + 22
    fr = Image.new("RGB", (W, H), BG[:3])
    d = ImageDraw.Draw(fr)
    d.text((2, 2), "before (top) / after (bottom); siderane, helium-3; 1x then 2x", font=F_T, fill=SUB)
    for i in range(2):
        for j in range(2):
            fr.paste(tiles1[i][j].convert("RGB"), (j * (w1 + 8), 22 + i * (h1 + 8)))
            fr.paste(big[i][j].convert("RGB"), (2 * (w1 + 8) + j * (w2 + 8), 22 + i * (h2 + 8)))
    frames.append(fr)
frames[0].save(os.path.join(args.out, "glass-before-after-1x.gif"), save_all=True, append_images=frames[1:],
               duration=round(1000 / 24), loop=0)
print("written:", *(os.path.join(args.out, n) for n in ("glass-sweep.png", "glass-review.png",
                                                       "glass-before-after-1x.gif")))
