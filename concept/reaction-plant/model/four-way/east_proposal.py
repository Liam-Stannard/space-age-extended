#!/usr/bin/env python3
"""T06b: the east view's legs, before and after the proposal (RP_PROPOSAL=legs-nw), on one sheet.

  python3 east_proposal.py <before-renders> <after-renders> <before-probe.json> <after-probe.json>

<before-renders> is a run's renders/ facing east (still.png, working.png: render.sh, RP_DIRECTION=east);
<after-renders> is circulator.py --idle with RP_PROPOSAL=legs-nw, downsampled (still-<d>.png,
working-<d>.png for all four directions). Each panel is the still with the legs' light added (the
working pass: the legs lit, everything else held out, over black), at 2x on one ground: what a
player sees while it works. The probes (circulator.py --probe) give the legs layer's visible px
(frame 0, over half alpha, at 4x) per direction, before and after. Writes east-proposal.png
beside this script.
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
before, after, pb, pa = sys.argv[1:5]
GROUND, BG, TEXT, SUB, HEAD = (74, 66, 58, 255), (30, 29, 28, 255), (228, 222, 210), (175, 168, 156), (240, 200, 120)
DIRS = ("north", "east", "south", "west")


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def lit(still, working, k=2):
    s = Image.open(still).convert("RGBA")
    g = Image.new("RGBA", s.size, GROUND)
    d = ImageDraw.Draw(g)
    ox, oy = s.width // 2, s.height // 2
    for i in range(-4, 5):
        d.line([(ox + i * 64 - 32, 0), (ox + i * 64 - 32, s.height)], fill=(90, 82, 74))
        d.line([(0, oy + i * 64 - 32), (s.width, oy + i * 64 - 32)], fill=(90, 82, 74))
    d.rectangle([ox - 160, oy - 160, ox + 160, oy + 160], outline=(140, 130, 118))
    g.alpha_composite(s)
    w = Image.open(working).convert("RGB")
    out = ImageChops.add(g.convert("RGB"), w)
    return out.resize((out.width * k, out.height * k), Image.LANCZOS)


def label(im, text, sub):
    out = Image.new("RGB", (im.width, im.height + 44), BG[:3])
    d = ImageDraw.Draw(out)
    d.text((6, 4), text, font=font(15, True), fill=TEXT)
    d.text((6, 24), sub, font=font(12), fill=SUB)
    out.paste(im, (0, 44))
    return out


probe_b, probe_a = json.load(open(pb)), json.load(open(pa))
px = lambda p, d: p.get(f"legs-{d}", 0)
b = label(lit(os.path.join(before, "still.png"), os.path.join(before, "working.png")), "BEFORE: facing east, as modelled (T06b)",
          f"the reactor stands in front of the legs: legs layer {px(probe_b, 'east')} px at 4x "
          f"({100 * px(probe_b, 'east') / px(probe_b, 'north'):.0f} % of north's)")
a = label(lit(os.path.join(after, "still-east.png"), os.path.join(after, "working-east.png")),
          "AFTER (proposal, mock): the leg pair moved north-west of the middle",
          f"legs layer {px(probe_a, 'east')} px ({100 * px(probe_a, 'east') / px(probe_b, 'north'):.0f} % of north's before)")
smalls = [label(lit(os.path.join(after, f"still-{d}.png"), os.path.join(after, f"working-{d}.png"), 1),
                f"proposal, facing {d}", f"legs {px(probe_a, d)} px (before {px(probe_b, d)})") for d in DIRS]
W = b.width + a.width + 16
head = Image.new("RGB", (W, 150), BG[:3])
d = ImageDraw.Draw(head)
d.text((0, 6), "The east view's legs: before and after a proposal (T06b; not modelled clean -- for Liam's decision)",
       font=font(20, True), fill=HEAD)
lines = ["Turned east, the reactor (model east, centre) stands in front of the glass legs (model west of it): the blue the spec calls the",
         "signature reads in a sliver. The proposal moves the leg pair to the north-west of the middle, clear of the reactor in every",
         "direction, and the crust-gas compressor 0.75 tile east beside the gas input. It fixes east (x2.9) but NOT west: there the scrubber",
         "then stands in front of the legs (-63 %). Not a fix as it stands -- the tall vessels leave no spot clear in all four directions",
         "without moving the scrubber too. Mock only: drain header left out, hoses unrevised, not collide-checked or packed."]
for i, ln in enumerate(lines):
    d.text((0, 38 + i * 21), ln, font=font(13), fill=TEXT)
row1 = Image.new("RGB", (W, max(b.height, a.height)), BG[:3])
row1.paste(b, (0, 0))
row1.paste(a, (b.width + 16, 0))
sw = sum(s.width for s in smalls) + 8 * 3
row2 = Image.new("RGB", (max(W, sw), smalls[0].height + 36), BG[:3])
ImageDraw.Draw(row2).text((0, 8), "The proposal in all four directions, 1x (the legs layer's px before -> after):", font=font(15, True), fill=HEAD)
x = 0
for s in smalls:
    row2.paste(s, (x, 36))
    x += s.width + 8
out = Image.new("RGB", (max(W, row2.width) + 32, head.height + row1.height + row2.height + 64), BG[:3])
out.paste(head, (16, 16))
out.paste(row1, (16, 16 + head.height + 16))
out.paste(row2, (16, 16 + head.height + 16 + row1.height + 16))
path = os.path.join(HERE, "east-proposal.png")
out.save(path)
print(path, out.size)
