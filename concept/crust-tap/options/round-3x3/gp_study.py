#!/usr/bin/env python3
"""Gas Pump 3x3, options round: the study of vanilla's pumpjack, before the takes.

  python3 -B gp_study.py <out.png> [--json <figures.json>]

Everything is read from the vanilla data (base/prototypes/entity/mining-drill.lua, the pumpjack and its two
helper functions; base/graphics/entity/pumpjack/) and drawn at 64 px a tile. The figures (coverage, rise,
tonal, finish) are tools/blender/measure.py's own functions on measure.py's own composite of the pumpjack
(measure.vanilla(), vanilla_figures()); the motion figures are measure.py's moving() and strobe() over the
horsehead's 40 frames drawn over the base. Nothing here is our art.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import measure as MT  # noqa: E402

out = sys.argv[1]
FD = MT.FD
PJ = os.path.join(FD, "base/graphics/entity/pumpjack")
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
HEAD, SUB, TEXT = (240, 200, 120), (175, 168, 156), (228, 222, 210)


def font(n, bold=False):
    return MT.font(n, bold)


# the horsehead: 40 frames, 8 a row, 206 x 172, shift by_pixel(-4.5, -29) (x2 at 64 px a tile)
HH = Image.open(os.path.join(PJ, "pumpjack-horsehead.png")).convert("RGBA")
HHS = Image.open(os.path.join(PJ, "pumpjack-horsehead-shadow.png")).convert("RGBA")


def hh(i):
    return HH.crop(((i % 8) * 206, (i // 8) * 172, (i % 8) * 206 + 206, (i // 8) * 172 + 172))


def hhs(i):
    return HHS.crop(((i % 8) * 292, (i // 8) * 78, (i % 8) * 292 + 292, (i // 8) * 78 + 78))


BASE = Image.open(os.path.join(PJ, "pumpjack-base.png")).convert("RGBA")
BASES = Image.open(os.path.join(PJ, "pumpjack-base-shadow.png")).convert("RGBA")
S = 448
O = (S // 2, S // 2)


def put(c, im, sx, sy):
    c.alpha_composite(im, (round(O[0] + sx - im.width / 2), round(O[1] + sy - im.height / 2)))


def frame(i, col, ground=True, shadow=True):
    """The pumpjack facing col (0 north .. 3 west) at horsehead frame i, as the engine draws it."""
    c = Image.new("RGBA", (S, S), GROUND if ground else (0, 0, 0, 0))
    if ground:
        d = ImageDraw.Draw(c)
        for k in range(-4, 5):
            d.line([(O[0] + (k + 0.5) * 64, 0), (O[0] + (k + 0.5) * 64, S)], fill=(84, 76, 68))
            d.line([(0, O[1] + (k + 0.5) * 64), (S, O[1] + (k + 0.5) * 64)], fill=(84, 76, 68))
        d.rectangle([O[0] - 96, O[1] - 96, O[0] + 96, O[1] + 96], outline=(150, 140, 125))
    if shadow:
        sh = Image.new("RGBA", (S, S))
        put(sh, BASES.crop((261 * col, 0, 261 * col + 261, 273)), -4.0, -10.0)
        put(sh, hhs(i), 35.5, 29.0)
        a = sh.getchannel("A").point(lambda v: v // 2)
        c.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (S, S)).split(), a)))
    put(c, BASE.crop((261 * col, 0, 261 * col + 261, 273)), -4.5, -9.5)
    put(c, hh(i), -9.0, -58.0)
    return c


def captioned(im, cap, size=13):
    lines = cap.split("\n")
    hh_ = 6 + (size + 6) * len(lines)
    c = Image.new("RGBA", (im.width, im.height + hh_), BG)
    d = ImageDraw.Draw(c)
    for k, ln in enumerate(lines):
        d.text((4, 4 + (size + 6) * k), ln, font=font(size, k == 0), fill=HEAD if k == 0 else SUB)
    c.alpha_composite(im, (0, hh_))
    return c


def hrow(ims, gap=12):
    r = Image.new("RGBA", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), BG)
    x = 0
    for i in ims:
        r.alpha_composite(i, (x, 0))
        x += i.width + gap
    return r


def vstack(ims, gap=14):
    r = Image.new("RGBA", (max(i.width for i in ims), sum(i.height for i in ims) + gap * (len(ims) - 1)), BG)
    y = 0
    for i in ims:
        r.alpha_composite(i, (0, y))
        y += i.height + gap
    return r


def block(title, paras, width, size=14):
    lines = []
    f = font(size)
    for p in paras:
        line = ""
        for w in p.split(" "):
            t = (line + " " + w).strip()
            if f.getlength(t) > width - 24 and line:
                lines.append(line)
                line = w
            else:
                line = t
        lines.append(line)
        lines.append("")
    im = Image.new("RGBA", (width, 34 + len(lines) * (size + 5)), BG)
    d = ImageDraw.Draw(im)
    d.text((10, 6), title, font=font(16, True), fill=HEAD)
    y = 32
    for ln in lines:
        d.text((14, y), ln, font=f, fill=TEXT)
        y += size + 5
    return im


# ---------------------------------------------------------------- the figures, measure.py's own
label, foot, still, shadow, light = MT.vanilla("pumpjack", "north")
fig = MT.vanilla_figures(still, light, foot)
frames_rgb = [MT.on_ground(frame(i, 0, ground=False, shadow=False)) for i in range(40)]
mask = frame(0, 0, ground=False, shadow=False)
cov_a = MT.covered(mask.getchannel("A"))
mv = MT.moving(frames_rgb)
st = MT.strobe(frames_rgb)
cov = fig["coverage"]


def share(m):
    return round(100 * MT.count(MT.both(m, cov_a)) / max(1, MT.count(cov_a)), 1)


figs = dict(label=label, coverage=cov, tonal=fig["tonal"], finish=fig["finish"],
            moving_pct=share(mv), strobe_pct=share(st), frames=40, animation_speed=0.5, loop_ticks=80,
            loop_seconds=round(80 / 60, 2))
if "--json" in sys.argv:
    json.dump(figs, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)

# ---------------------------------------------------------------- the panels
dirs = [captioned(frame(0, k).crop((64, 40, 384, 400)), f"facing {n}: base column {k}, horsehead frame 0")
        for k, n in enumerate(("north", "east", "south", "west"))]
# its output: north face, positions {1,-1} {1,1} {-1,1} {-1,-1}: a corner tile, round the four corners
for k, (tx, ty) in enumerate(((1, -2), (2, 1), (-1, 2), (-2, -1))):
    d = ImageDraw.Draw(dirs[k])
    x, y = 160 + 64 * tx, 184 + 64 * ty
    d.ellipse([x - 9, y - 9, x + 9, y + 9], outline=(120, 200, 255), width=3)
keys = [8 * k // 1 for k in range(5)]
nod = [captioned(frame(i, 0).crop((96, 64, 352, 330)).resize((512, 532), Image.NEAREST), f"frame {i} (2x)")
       for i in (0, 10, 20, 30)]
mm = frame(0, 0).convert("RGB")
dim = Image.blend(mm, Image.new("RGB", mm.size, (40, 36, 32)), 0.55)
dim.paste((230, 40, 200), mask=MT.both(mv, cov_a))
mmap = captioned(dim.convert("RGBA").crop((64, 40, 384, 400)), "motion map: magenta changes over the 40 frames")
c = cov
notes = [
    "Size and placing: 3x3, collision +-1.2 (a 0.3 walkway round it), selection +-1.5; it finds its oil within "
    "resource_searching_radius 0.49, so it always stands centred on the well -- what T01 gave the Gas Pump.",
    "Two drawings, split by what turns. The base is a working_visualisation drawn always (always_draw, "
    "secondary_draw_order -1), one sheet of four columns, one a direction: its outlet goes round the corners "
    "with the output ({1,-1} north, then {1,1}, {-1,1}, {-1,-1}: a corner tile, never a middle one). The horsehead "
    "is the animation, one 40-frame strip (8 a row) used in every direction: the moving part never turns; only "
    "the base under it does. use_mirroring adds a flipped base (graphics_set_flipped), the horsehead shared.",
    "Motion: one nod a loop, 40 frames at animation_speed 0.5 = 80 ticks, 1.33 s a nod, eased at the ends; the "
    f"horsehead, beam, pitman and crank are the whole moving share, {figs['moving_pct']} % of the covered px "
    f"(changed by over 30 in any frame), strobe {figs['strobe_pct']} %. No status lamp, no light, no glow. "
    "Idle it stops mid-nod (the mining drill's animation freezes).",
    f"Form: coverage {c['footprint_pct']} % of the footprint (mass {c['mass_pct']} %), corners "
    f"{', '.join(f'{k} {v}' for k, v in c['corners_pct'].items())}, rise {c['rise_tiles']} tile over the north "
    f"edge, extent {c['extent_tiles'][0]} x {c['extent_tiles'][1]} tiles. Not a deck: an open frame -- the A-frame "
    "samson post and the beam over a motor-and-crank block, and a ring of bare and rusted pipework walking the "
    "footprint's edge round to the outlet, ground showing between. It reads as a machine by its silhouette and "
    "its nod, not by its mass: under our 92 % bar, which is the Core's showpieces' figure, not vanilla's.",
    f"Finish: tonal p5 {fig['tonal']['p5']}, p50 {fig['tonal']['p50']}, p95 {fig['tonal']['p95']}; black "
    f"{fig['finish']['black_pct']} % (darker than our accepted ~75-81). Green paint on the beam, the post and the "
    "motor, a yellow highlight on the beam's top edge, rusted bare-steel pipes with green handwheels; no hoses, "
    "no cables: the clutter is pipework and valves.",
    "What the takes keep: 3x3 centred on the vent; the output on one face, turning with the building (ours "
    "at the middle tile, {0,-1}, not a corner); one big readable motion a loop, a part the player can name; idle "
    "stops where it is; pipework and valves as the clutter. What they do not: its open, 73 %-covered frame (our bar is 92 %). The question it leaves for the model stage: the pumpjack's "
    "split (the moving core drawn once, never turned; the base and outlet per direction), or the whole machine "
    "turned in four drawings (the Vent Pump's T07c chose per-direction variations with the core facing the "
    "camera).",
]
W = 4 * 320 + 3 * 12
top = Image.new("RGBA", (W, 40), BG)
ImageDraw.Draw(top).text((10, 8), "GAS PUMP 3x3 -- STUDY: VANILLA'S PUMPJACK (64 px a tile, one ground)",
                         font=font(20, True), fill=HEAD)
sheet = vstack([top, captioned(hrow(dirs), "THE FOUR DIRECTIONS, 1x: the base turns, the horsehead does not; "
                                           "blue ring: the output's pipe tile"),
                captioned(hrow(nod[:2] + [mmap]), "THE NOD, 2x (frames 0 and 10 of 40), and its motion map at 1x"),
                block("WHAT IT DOES, AND WHAT WE TAKE", notes, W)])
pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
pad.alpha_composite(sheet, (10, 10))
pad.convert("RGB").save(out)
print(out, pad.size, json.dumps(figs))
