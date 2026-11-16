#!/usr/bin/env python3
"""Reaction Plant redesign, animation previews after the clash fixes: the "all together" GIF
again, its measures, and a 4x before/after of every fix.

  python3 anim_fixed.py <hi-fixed> <hi-before> <out-dir> [--factorio <data>]

Liam, 2026-10-11, on the previews: "All of the animations look good, a small problem is the
vent pump clips." anim_previews.py --mode collide found what clipped (every moving part in
every frame of "all", and the fixed additions, against the model); the fixes are in
anim_previews.py, and --before renders the previews as first shown.

<hi-fixed>/all/ and <hi-before>/all/ hold anim_previews.py's 4x renders of --mode all, fixed
and --before (working-NN.png, plate.png, idle.png); <hi-before>/gauges_big/ frame 0 of
--mode gauges_big --before (the double dials as first shown). Writes into <out-dir>, never
over the earlier previews:

  6-all-fixed.gif              the 48-frame loop as 6-all.gif lays it out (2x beside 1x)
  fixes-4x-fixed.png           every fix at 4x: before above, after below, same frames
  condenser-4x-fixed.gif       the vent condenser at 4x, before beside after, all 48 frames
  press-4x-fixed.gif           the press cycle at 4x, before beside after (frames 24-39)
  measures-fixed.txt           frames, moving share and crops of the fixed "all"

The layout, ground, port pictures and measures are anim_sheets.py's own (its functions are
loaded from it, so the two cannot drift apart).
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:]]
FIX, BEF, OUTD = args[0], args[1], args[2]
fd = args[args.index("--factorio") + 1] if "--factorio" in args else None

# anim_sheets.py's definitions, without its run: HI and OUT pointed at the fixed renders
src = open(os.path.join(HERE, "anim_sheets.py")).read()
src = src[:src.index("\nresults = []")]
sys.argv = ["anim_sheets.py", FIX, OUTD] + (["--factorio", fd] if fd else [])
G = {"__file__": os.path.join(HERE, "anim_sheets.py"), "__name__": "anim_sheets"}
exec(compile(src, "anim_sheets.py", "exec"), G)
compose, load, font, measure, gif, area = (G[k] for k in ("compose", "load", "font", "measure", "gif", "area"))
BG, TEXT, SUB, HEAD = G["BG"], G["TEXT"], G["SUB"], G["HEAD"]
os.makedirs(OUTD, exist_ok=True)

TITLE = "6. All together, fixed (48 f): no clashes; double dials; the cake toned down; the press opens west"

# ---- the GIF, through anim_sheets.gif() into a scratch name, then renamed: 6-all.gif stays
tmp_out = os.path.join(OUTD, ".fixed-tmp")
os.makedirs(tmp_out, exist_ok=True)
G["OUT"] = tmp_out
path, size = gif("6", "all", TITLE, 48, None)
gif_path = os.path.join(OUTD, "6-all-fixed.gif")
os.replace(path, gif_path)
os.rmdir(tmp_out)

# ---- measures
r = measure("all", 48)
u = r["union"]
lines = ["Reaction Plant, animation previews after the clash fixes (anim_previews.py, anim_fixed.py)",
         "measured as measures.txt measures the first previews (anim_sheets.py)", "",
         TITLE,
         f"  frames 48; moving {r['moving']} px of {r['opaque']} opaque = {r['share'] * 100:.1f} %; "
         f"plate rises {r['rise']:.2f} tiles above the north edge (round 5 0.78)",
         f"  union crop {u[2] - u[0]} x {u[3] - u[1]} px = {area(u)} px^2 at ({u[0]}, {u[1]})"]
for b in r["clusters"][:8]:
    lines.append(f"    cluster {b[2] - b[0]} x {b[3] - b[1]} px at ({b[0]}, {b[1]}), {b[4]} moving px")
lines.append(f"    ({r['flicker']} specks under 10 px left out: render flicker, not motion)")
lines.append(f"  GIF {gif_path}  {size / 1e6:.2f} MB")


# ---- the 4x before/after crops
def crop4(root, mode, f, box):
    p = os.path.join(root, mode, f"working-{f:02d}.png")
    x0, y0, x1, y1 = box
    return compose(load(p, 4), 4).crop((x0 * 4, y0 * 4, x1 * 4, y1 * 4))


# (title, what was wrong, what changed, box in 1x px, [(before root, mode, frame), ...], [after ...])
FIXES = [
    ("1. Vent condenser: drain cock, drops and beads",
     "before: the cock on the east flank reached x 2.60, 6 px past the footprint's east edge (dashed); "
     "drops and the wet patch fell outside it; three beads ran down through the upper band, one through the cock",
     "after: the cock on the south-east flank, 0.11 out, lip at x 2.44; drops land in the footprint, clear of "
     "the foot ring; beads run between the bands, clear of the cock, rivets and gauge",
     (318, 70, 418, 200), [(BEF, "all", 0), (BEF, "all", 3), (BEF, "all", 21)],
     [(FIX, "all", 0), (FIX, "all", 3), (FIX, "all", 21)]),
    ("2. Exchanger's east head into the vent condenser (round 5, static; mostly behind the reactor)",
     "before: the exchanger's dished east head ran 0.05-0.1 tile into the condenser's copper shell and foot ring",
     "after: the exchanger ends 1.45 east of centre (was 1.55): its head clear of the condenser",
     (272, 78, 342, 132), [(BEF, "all", 0)], [(FIX, "all", 0)]),
    ("2b. Exchanger's west head into the scrubber (round 5, static)",
     "before: the west head ran into the scrubber's oxide shell", "after: the exchanger starts 1.42 west of "
     "centre (was 1.55): clear", (92, 78, 150, 128), [(BEF, "all", 0)], [(FIX, "all", 0)]),
    ("3. Compressor and dosing-pump couplings",
     "before: the compressor's coupling turned 0.015 into the compressor's end and its stripe into the motor; "
     "the dosing pump's turned into the pump, its shaft housing and the hose over it",
     "after: each centred in the gap between its machines and made thinner along its shaft (0.7, 0.6); "
     "the dosing pump's hose lifted 0.04 over it. Both couplings are hidden in the plate (the compressor's "
     "behind the legs, the dosing pump's under its hose): the clash was inside, unseen; the one visible change "
     "is the hose, shown here",
     (100, 200, 182, 272), [(BEF, "all", 0), (BEF, "all", 12)], [(FIX, "all", 0), (FIX, "all", 12)]),
    ("4. Agitator drive: belt lacing clips",
     "before: each clip was turned a quarter, its 0.05 length standing radial: it cut 0.007 into both "
     "pulley rims as it went round",
     "after: the clips lie along the belt (0.05 long, 0.026 over the belt's 0.02)",
     (262, 108, 342, 186), [(BEF, "all", 4), (BEF, "all", 20)], [(FIX, "all", 4), (FIX, "all", 20)]),
    ("5. Filter press: the opening stroke and the cake",
     "before: the head, ram and handwheel backed off east, 0.24 tile into the filtrate receiver they stand "
     "over, the flexed hose through its rail; the cake tilted into its leaf, near white",
     "after: the head stays bolted down; the leaves and tail stand back off west 0.18 on rails run on by "
     "the stroke; the cake (#8C8476, toned down) peels away from its leaf into a dark chute mouth",
     (70, 305, 240, 425), [(BEF, "all", 28), (BEF, "all", 31), (BEF, "all", 33)],
     [(FIX, "all", 28), (FIX, "all", 31), (FIX, "all", 33)]),
    ("6. Gauges: the double-size dials",
     "before (3b, the double dials as first shown): needles turned 0.6 rad out of the dial's plane, one end "
     "into the case and the reactor's wall; the dials sat across weld beads and seams, the upper one on "
     "the ladder's rail",
     "after: needles lie on their faces; the dials stand 0.02 off the wall on a stem; the reactor's upper "
     "dial 0.12 rad west of the ladder",
     (236, 228, 352, 330), [(BEF, "gauges_big", 0)], [(FIX, "all", 0)]),
    ("6b. The scrubber's double dial",
     "before: across the scrubber's weld bead", "after: on its stem, clear",
     (82, 106, 134, 154), [(BEF, "gauges_big", 0)], [(FIX, "all", 0)]),
]


def edge_line(img, box):
    """The footprint's east edge (x = +2.5 tiles), dashed, where it crosses the crop."""
    ex = (208 + 2.5 * 64 - box[0]) * 4
    if 0 <= ex < img.width:
        d = ImageDraw.Draw(img)
        for y in range(0, img.height, 16):
            d.line([(ex, y), (ex, y + 8)], fill=(255, 220, 90, 255), width=2)


rows = []
MAXW = 1500
for title, before, after, box, bs, as_ in FIXES:
    tiles_b = [crop4(rt, m, f, box) for rt, m, f in bs]
    tiles_a = [crop4(rt, m, f, box) for rt, m, f in as_]
    for t in tiles_b + tiles_a:
        edge_line(t, box)
    k = min(1.0, MAXW / (sum(t.width for t in tiles_b) + 12 * len(tiles_b)))
    if k < 1.0:
        tiles_b = [t.resize((int(t.width * k), int(t.height * k)), Image.LANCZOS) for t in tiles_b]
        tiles_a = [t.resize((int(t.width * k), int(t.height * k)), Image.LANCZOS) for t in tiles_a]
    tw = sum(t.width for t in tiles_b) + 12 * (len(tiles_b) - 1)
    th = tiles_b[0].height
    w = max(tw + 24, 1200)
    import textwrap
    wb = textwrap.wrap(before, 190)
    wa = textwrap.wrap(after, 190)
    row = Image.new("RGBA", (w, 2 * th + 120 + 16 * (len(wb) + len(wa))), BG)
    d = ImageDraw.Draw(row)
    d.text((12, 8), title + ("  (4x" + (f", shown at {k:.2f}" if k < 1 else "") + ")"), font=font(17, True), fill=HEAD)
    for i, ln in enumerate(wb):
        d.text((12, 34 + 16 * i), ln, font=font(12), fill=TEXT)
    y0 = 40 + 16 * len(wb)
    x = 12
    for (rt, m, f), t in zip(bs, tiles_b):
        row.alpha_composite(t, (x, y0))
        d.text((x + 6, y0 + 4), f"BEFORE  f{f:02d}" + ("  (3b)" if m != "all" else ""), font=font(13, True),
               fill=(255, 140, 110))
        x += t.width + 12
    for i, ln in enumerate(wa):
        d.text((12, y0 + th + 6 + 16 * i), ln, font=font(12), fill=TEXT)
    y1 = y0 + th + 12 + 16 * len(wa)
    x = 12
    for (rt, m, f), t in zip(as_, tiles_a):
        row.alpha_composite(t, (x, y1))
        d.text((x + 6, y1 + 4), f"AFTER  f{f:02d}", font=font(13, True), fill=(140, 230, 140))
        x += t.width + 12
    rows.append(row)
W = max(r_.width for r_ in rows)
sheet = Image.new("RGBA", (W, sum(r_.height for r_ in rows) + 10 * len(rows) + 60), BG)
ImageDraw.Draw(sheet).text((12, 16), "THE CLASH FIXES, 4x: each before (first previews) above its after, the same "
                                     "frames of the 48-frame \"all\" loop; dashed: the footprint's east edge",
                           font=font(16, True), fill=HEAD)
y = 60
for r_ in rows:
    sheet.alpha_composite(r_, (0, y))
    y += r_.height + 10
fixes_path = os.path.join(OUTD, "fixes-4x-fixed.png")
sheet.convert("RGB").save(fixes_path)


def pair_gif(name, box, frames, note):
    out = []
    for f in frames:
        b, a = crop4(BEF, "all", f, box), crop4(FIX, "all", f, box)
        edge_line(b, box)
        edge_line(a, box)
        im = Image.new("RGBA", (b.width * 2 + 36, b.height + 64), BG)
        d = ImageDraw.Draw(im)
        d.text((12, 8), note, font=font(15, True), fill=HEAD)
        im.alpha_composite(b, (12, 52))
        im.alpha_composite(a, (24 + b.width, 52))
        d.text((18, 30), "BEFORE", font=font(14, True), fill=(255, 140, 110))
        d.text((30 + b.width, 30), "AFTER", font=font(14, True), fill=(140, 230, 140))
        d.text((im.width - 70, 30), f"f{f:02d}", font=font(14), fill=SUB)
        out.append(im.convert("RGB"))
    pal = out[len(out) // 2].quantize(colors=255)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in out]
    p = os.path.join(OUTD, name)
    q[0].save(p, save_all=True, append_images=q[1:], duration=70, loop=0, optimize=True)
    return p, os.path.getsize(p)


cg = pair_gif("condenser-4x-fixed.gif", (318, 70, 418, 200), range(48),
              "Vent condenser, 4x: drain cock, drops, beads (dashed: the east edge)")
pg = pair_gif("press-4x-fixed.gif", (70, 305, 240, 425), range(24, 40),
              "Filter press, 4x: one cycle (frames 24-39 of 48), the cake lands on f34")
lines += ["", f"fixes sheet {fixes_path}", f"condenser GIF {cg[0]}  {cg[1] / 1e6:.2f} MB",
          f"press GIF {pg[0]}  {pg[1] / 1e6:.2f} MB"]
mp = os.path.join(OUTD, "measures-fixed.txt")
open(mp, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
