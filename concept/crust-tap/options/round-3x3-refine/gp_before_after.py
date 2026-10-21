#!/usr/bin/env python3
"""Gas Pump 3x3, refine (T04): before/after crops of what changed, take 2 (T02, baf235d) against the refine.

  python3 -B gp_before_after.py --before <T02 renders/2> --before-he <T02 helium/2> --after <renders/2>
                                --after-he <helium/2> [--alt-he <helium render, another violet>]
                                --before-measure <measures.json> --after-measure <measures.json> --out <dir>

Each changed part cropped from the same frames of both loops (0, 3, 6, 9: a quarter turn apart over the first
three eighths) at 4x, before above after, with each loop's motion map (magenta: luminance changed over 30 from
frame 0 in any of the 24 frames, measure.py's moving rule drawn, not counted) and, where measure.py marks it,
nothing else: the figures quoted are measures.json's. The sight glass in helium-3, before and after. Also a 1x
GIF of both loops side by side.

Writes before-after.png and before-after-1x.gif into <out>.
"""
import argparse
import json
import os

from PIL import Image, ImageChops, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
for a in ("--before", "--before-he", "--after", "--after-he", "--before-measure", "--after-measure", "--out"):
    ap.add_argument(a, required=True)
ap.add_argument("--alt-he", default=None)
ap.add_argument("--alt-hex", default="#B6A6C8")
args = ap.parse_args()
CANVAS, ORIGIN = 352, (160, 208)
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
HEAD, SUB, TEXT = (240, 200, 120), (175, 168, 156), (228, 222, 210)
FR = (0, 3, 6, 9)


def font(n, b=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if b else "") + ".ttf", n)


def load(path, k=1):
    im = Image.open(path).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    im = im.convert("RGBa").resize((CANVAS * k, CANVAS * k), Image.LANCZOS).convert("RGBA")
    g = Image.new("RGBA", im.size, GROUND)
    g.alpha_composite(im)
    return g


def px(p):
    """A model point (tiles, z up) to 1x canvas px: 64 px a tile, z/2 tiles up the screen."""
    return ORIGIN[0] + 64 * p[0], ORIGIN[1] - 64 * (p[1] + p[2] / 2)


def crop(im, c, hw, hh, k):
    x, y = px(c)
    return im.crop((round((x - hw) * k), round((y - hh) * k), round((x + hw) * k), round((y + hh) * k)))


def motion(frames):
    f0 = frames[0].convert("RGB")
    mv = None
    for f in frames[1:]:
        d = ImageChops.difference(f0, f.convert("RGB")).convert("L").point(lambda v: 255 if v > 30 else 0)
        mv = d if mv is None else ImageChops.lighter(mv, d)
    out = Image.blend(frames[0].convert("RGB"), Image.new("RGB", frames[0].size, (40, 36, 32)), 0.55)
    out.paste((230, 40, 200), mask=mv)
    return out.convert("RGBA")


def cap(im, lines, size=13):
    hh = 4 + (size + 5) * len(lines)
    w = max([im.width] + [int(font(size, True).getlength(t)) + 8 for t in lines])
    c = Image.new("RGBA", (w, im.height + hh), BG)
    d = ImageDraw.Draw(c)
    for i, t in enumerate(lines):
        d.text((3, 2 + (size + 5) * i), t, font=font(size, i == 0), fill=HEAD if i == 0 else SUB)
    c.alpha_composite(im, (0, hh))
    return c


def row(ims, gap=8):
    r = Image.new("RGBA", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), BG)
    x = 0
    for i in ims:
        r.alpha_composite(i, (x, 0))
        x += i.width + gap
    return r


def stack(ims, gap=10, width=None):
    r = Image.new("RGBA", (width or max(i.width for i in ims), sum(i.height for i in ims) + gap * (len(ims) - 1)), BG)
    y = 0
    for i in ims:
        r.alpha_composite(i, (0, y))
        y += i.height + gap
    return r


def wrap(s, size, width):
    f, out, line = font(size), [], ""
    for w in s.split(" "):
        t = (line + " " + w).strip()
        if f.getlength(t) > width and line:
            out.append(line)
            line = w
        else:
            line = t
    return out + ([line] if line else [])


def para(title, texts, W, size=14):
    lines = []
    for t in texts:
        lines += wrap(t, size, W - 24)
    im = Image.new("RGBA", (W, 34 + (size + 5) * len(lines)), BG)
    d = ImageDraw.Draw(im)
    d.text((10, 6), title, font=font(17, True), fill=HEAD)
    for i, t in enumerate(lines):
        d.text((14, 32 + (size + 5) * i), t, font=font(size), fill=TEXT)
    return im


K = 4
before = [load(os.path.join(args.before, f"working-{f:02d}.png"), K) for f in range(24)]
after = [load(os.path.join(args.after, f"working-{f:02d}.png"), K) for f in range(24)]
mb, ma = motion(before), motion(after)
MB = json.load(open(args.before_measure))["directions"][""]
MA = json.load(open(args.after_measure))["directions"][""]

PARTS = [
    ("THE FLYWHEEL", (0, -1.28, 0.68), 40, 30,
     "Before: six open green spokes on a dark rim; each spoke jumps more than its own width a frame, so the "
     "inside flickers (take 2's strobe was all here) and the turn does not read. After: the spokes cast into a "
     "web in the same green, standing only a little proud, and a big yellow balance weight bolted between two "
     "spokes in place of the small red lug: one bold mark goes round once a loop."),
    ("THE CROSSHEADS AND RODS (west and east frames)", (0, -0.76, 0.5), 66, 20,
     "Before: nickel crossheads over a green guide floor, 0.13 tile either side. After: bare steel with a "
     "yellow slipper on top over an oil-dark floor, 0.15 tile either side (mid 0.02 tile further out, clear of the "
     "crankcase's rod bore), so each slide reads against its frame."),
    ("THE POWER CYLINDERS' ROCKERS", (0, -0.76, 1.45), 22, 24,
     "Before: nod 0.28 rad. After: 0.40 rad (both half a loop apart, as before)."),
]
blocks = []
W = 0
for title, c, hw, hh, why in PARTS:
    rb = row([cap(crop(before[f], c, hw, hh, K), [f"before, frame {f}"]) for f in FR] +
             [cap(crop(mb, c, hw, hh, K), ["before, motion map"])])
    ra = row([cap(crop(after[f], c, hw, hh, K), [f"after, frame {f}"]) for f in FR] +
             [cap(crop(ma, c, hw, hh, K), ["after, motion map"])])
    blocks.append((title, why, stack([rb, ra], 8)))
    W = max(W, rb.width, ra.width)
W += 20

# the sight glass in helium-3, before (pale blue) and after (the Vent Pump's violet)
gc, ghw, ghh = (1.16, 0.13, 0.62), 22, 30
he = [cap(crop(load(os.path.join(args.before_he, "working-00.png"), K), gc, ghw, ghh, K), ["before: helium-3", "#8CC7E6"]),
      cap(crop(load(os.path.join(args.after_he, "working-00.png"), K), gc, ghw, ghh, K), ["after: helium-3", "#9C86CC (VIO)"])]
if args.alt_he:
    he.append(cap(crop(load(os.path.join(args.alt_he, "working-00.png"), K), gc, ghw, ghh, K),
                  ["option: helium-3", f"{args.alt_hex}"]))
he.append(cap(crop(after[0], gc, ghw, ghh, K), ["siderane (unchanged)", "#A8D929"]))


def fig(M):
    c, t, col, mo = M["coverage"], M["tonal"]["plate"], M["colour"], M["motion"]
    return (f"moving {mo['moving_pct']} %, strobe {mo['strobe_pct']} % ({mo['strobe_px']} px); coverage "
            f"{c['footprint_pct']} %, rise {c['rise_tiles']} t; p50 {t['p50']}, p95 {t['p95']}; white {col['white_px']} px, "
            f"clipped {col['clipped_px']} px")


head = Image.new("RGBA", (W, 10), BG)
parts = [para("GAS PUMP 3x3, REFINE (T04): TAKE 2, BEFORE AND AFTER", [
    "What changed, cropped at 4x from the same frames of both 24-frame loops (a quarter turn apart), before "
    "above after; the motion map beside each (magenta: changed over 30 in luminance from frame 0 at some frame).",
    "Before (T02, measure.py): " + fig(MB) + ".",
    "After (T04, measure.py): " + fig(MA) + "."], W)]
for title, why, im in blocks:
    parts.append(para(title, [why], W))
    parts.append(im)
parts.append(para("THE SIGHT GLASS IN HELIUM-3, 4x (working frame 0)", [
    "Liam: \"Violet, like the Vent Pump\". After: the Vent Pump's violet (#9C86CC, its sight glass's working "
    "violet, vp4_glass VIO) as the gas paint, from 0.42 to 0.86 of it as before. Paint, never light."], W))
parts.append(row(he))
sheet = stack(parts, 10, W)
pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
pad.alpha_composite(sheet, (10, 10))
os.makedirs(args.out, exist_ok=True)
pad.convert("RGB").save(os.path.join(args.out, "before-after.png"))
print(os.path.join(args.out, "before-after.png"), pad.size)

# a 1x GIF: before and after side by side, the whole machine, 70 ms a frame
b1 = [load(os.path.join(args.before, f"working-{f:02d}.png"), 1).crop((8, 24, 344, 344)) for f in range(24)]
a1 = [load(os.path.join(args.after, f"working-{f:02d}.png"), 1).crop((8, 24, 344, 344)) for f in range(24)]
fr = []
for b, a in zip(b1, a1):
    c = Image.new("RGB", (b.width * 2 + 8, b.height + 18), BG[:3])
    d = ImageDraw.Draw(c)
    d.text((4, 2), "before (T02)", font=font(12, True), fill=HEAD)
    d.text((b.width + 12, 2), "after (T04)", font=font(12, True), fill=HEAD)
    c.paste(b.convert("RGB"), (0, 18))
    c.paste(a.convert("RGB"), (b.width + 8, 18))
    fr.append(c)
strip = Image.new("RGB", (fr[0].width, fr[0].height * len(fr)))
for i, f in enumerate(fr):
    strip.paste(f, (0, i * f.height))
pal = strip.quantize(colors=256)
q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in fr]
q[0].save(os.path.join(args.out, "before-after-1x.gif"), save_all=True, append_images=q[1:], duration=70, loop=0,
          optimize=True)
print(os.path.join(args.out, "before-after-1x.gif"))
