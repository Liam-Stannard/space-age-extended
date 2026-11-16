#!/usr/bin/env python3
"""Reaction Plant redesign, round 4: F, the Circulator -- sheet, GIF, compare plates, measures.

  python3 r4_sheets.py <hi-dir> <ports-dir> <out-dir> --r3 <round-3-plate-1x.png> [--factorio <data>]

<hi-dir> is r4_circulator.py's output (working-NN.png, idle.png, plate.png,
plate-working.png, all 4x). <ports-dir> is its --ports run, downsampled
(tools/blender/downsample.py) and packed (tools/blender/pack_ports.py): port-<face>.png and
meta.json. --r3 is round 3's plate re-rendered by r3_circulator.py (--only idle), at 1x,
for the finish and tonal rows. Writes into <out-dir>:

  F-the-circulator-r4.png          the sheet: working and idle at 2x, the moving pixels
                                   at 1x, the four rotations at 1x and 2x with the plant's
                                   own pipe pictures, the pictures against assembler 3's at
                                   4x, all twelve at once, the silhouette, the legs' frames,
                                   the finish against vanilla and round 3, the proposal
  F-the-circulator-r4-idle.png     the idle still at 2x on the ground
  F-the-circulator-r4-working.gif  the loop, 2x beside 1x
  compare-plates.png (+ -2x)       the refinery, the chemical plant, round 3's F and round
                                   4's F at 64 px a tile on one ground, frame 0
  measures.txt                     cover, corners, rise, blue, motion, finish, tonal, ports

Ports as the engine draws them: each picture from the centre of the tile the connection
points into, at the shift pack_ports.py measured; vanilla's pipe cover centred on that
tile, over the picture (it caps the stub); north-facing ones behind the plate
(secondary_draw_orders north = -1), the rest over it. Facing X: the inputs at tiles -1 and
+1 on the X side, the output at 0 opposite.
"""
import argparse
import json
import os
import re
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("hi")
ap.add_argument("ports")
ap.add_argument("out")
ap.add_argument("--r3", required=True)
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
args = ap.parse_args()
HI, PORTS, OUT, FD, R3 = args.hi, args.ports, args.out, args.factorio, args.r3
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
TOOLS = os.path.join(REPO, "tools", "blender")
R3_SHEETS = os.path.normpath(os.path.join(HERE, "..", "round-3"))
os.makedirs(OUT, exist_ok=True)

PPT = 64
FOOT = 5
CANVAS, ORIGIN = (512, 448), (208, 272)
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)
NF = 24
GIF_MS = 70
CROP1 = (8, 14, 456, 448)
CROP2 = tuple(2 * v for v in CROP1)
ENT = f"{FD}/base/graphics/entity"
AM3 = f"{ENT}/assembling-machine-3/assembling-machine-3-pipe-"
COVER = f"{ENT}/pipe-covers/pipe-cover-"
SLUG = "F-the-circulator-r4"
PMETA = json.load(open(os.path.join(PORTS, "meta.json")))


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def load(name, k, src=None):
    """A 4x render brought to k x game scale, premultiplied, faint catcher fog cut."""
    im = Image.open(os.path.join(src or HI, name + ".png")).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    im = im.convert("RGBa").resize((im.width * k // 4, im.height * k // 4), Image.LANCZOS)
    return im.convert("RGBA")


def ground(size, origin, ppt, foot=FOOT, extent=10):
    g = Image.new("RGBA", size, GROUND)
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ox, oy = origin
    off = 0.5 if foot % 2 else 0.0
    for i in range(-extent * 2, extent * 2 + 1):
        x = ox + (i + off) * ppt
        y = oy + (i + off) * ppt
        d.line([(x, 0), (x, size[1])], fill=(255, 255, 255, 26))
        d.line([(0, y), (size[0], y)], fill=(255, 255, 255, 26))
    h = foot * ppt / 2
    d.rectangle([ox - h, oy - h, ox + h, oy + h], outline=(255, 255, 255, 120))
    g.alpha_composite(ov)
    return g


def sidecar(stem):
    t = open(stem + ".lua").read()
    w = int(re.search(r"width\s*=\s*(\d+)", t).group(1))
    h = int(re.search(r"height\s*=\s*(\d+)", t).group(1))
    sx, sy = map(float, re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", t).groups())
    return w, h, sx, sy


def paste(canvas, im, centre):
    x = round(centre[0] - im.width / 2)
    y = round(centre[1] - im.height / 2)
    canvas.alpha_composite(im, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))


NAME = {"N": "north", "E": "east", "S": "south", "W": "west"}


def port_layers(face, tile, k):
    """(picture, cover, picture centre, cover centre) in k x px from the origin, for a port
    on `face` at `tile`: the plant's own picture at pack_ports.py's shift, vanilla's cover."""
    off = {"N": (tile, -3), "S": (tile, 3), "E": (3, -tile), "W": (-3, -tile)}[face]
    cx, cy = off[0] * PPT * k, off[1] * PPT * k
    sx, sy = PMETA[f"port-{face}"]["shift"]
    pic = Image.open(os.path.join(PORTS, f"port-{face}.png")).convert("RGBA")
    cov = Image.open(COVER + NAME[face] + ".png").convert("RGBA")
    if k != 1:
        pic = pic.resize((pic.width * k, pic.height * k), Image.LANCZOS)
        cov = cov.resize((cov.width * k, cov.height * k), Image.LANCZOS)
    return pic, cov, (cx + sx * PPT * k, cy + sy * PPT * k), (cx, cy)


def ports_for(direction):
    opp = {"N": "S", "S": "N", "E": "W", "W": "E"}[direction]
    return [(direction, -1), (direction, 1), (opp, 0)]


ALL_PORTS = [(f, t) for f in "NESW" for t in (-1, 0, 1)]


def compose(plate, k, ports, covers=True):
    """Ground, the north fittings behind, the plate (with its shadow), the rest over it;
    each fitting its picture, then the cover capping it."""
    g = ground(plate.size, (ORIGIN[0] * k, ORIGIN[1] * k), PPT * k)
    o = (ORIGIN[0] * k, ORIGIN[1] * k)
    layers = [port_layers(f, t, k) for f, t in ports]

    def draw(north):
        for (f, _), (pic, cov, pc, cc) in zip(ports, layers):
            if (f == "N") == north:
                paste(g, pic, (o[0] + pc[0], o[1] + pc[1]))
                if covers:
                    paste(g, cov, (o[0] + cc[0], o[1] + cc[1]))
    draw(True)
    g.alpha_composite(plate)
    draw(False)
    return g


def tool(name, path):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, name), path], capture_output=True, text=True)
    return " ".join(r.stdout.split()[1:]).split("(vanilla")[0].strip()


# ----------------------------------------------------------------- measures
os.makedirs(os.path.join(OUT, ".x1"), exist_ok=True)
X1 = os.path.join(OUT, ".x1")


def save1(name, src=None, sub=""):
    p = os.path.join(X1, sub + name + ".png")
    load(name, 1, src).save(p)
    return p


def measure():
    w = load("working-00", 1)
    idle = load("idle", 1)
    plate = load("plate", 1)
    mask = plate.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    cnt = lambda im: sum(1 for v in im.get_flattened_data() if v)
    ox, oy = ORIGIN
    h = FOOT * PPT // 2
    cover = cnt(mask.crop((ox - h, oy - h, ox + h, oy + h))) / (2 * h) ** 2
    bb = mask.getbbox()
    rise = (oy - h - bb[1]) / PPT
    opaque = cnt(mask)
    lift = ImageChops.subtract(w.getchannel("B"), idle.getchannel("B")).point(lambda v: 255 if v > 40 else 0)
    lift = ImageChops.multiply(lift, mask)
    hue = ImageChops.subtract(w.getchannel("B"), ImageChops.lighter(w.getchannel("R"), w.getchannel("G")))
    lift = ImageChops.multiply(lift, hue.point(lambda v: 255 if v > 30 else 0))
    blue = cnt(lift)
    acc = Image.new("L", w.size, 0)
    for f in range(1, NF):
        d = ImageChops.difference(w, load(f"working-{f:02d}", 1)).convert("L")
        acc = ImageChops.lighter(acc, d.point(lambda v: 255 if v > 10 else 0))
    moving = cnt(ImageChops.multiply(acc, mask))
    lb = lift.getbbox()
    # the outline (FFF #350): each corner tile's cover, and the outer quarter-tile band's
    corners = {}
    for name, (cx_, cy_) in (("NW", (-1, -1)), ("NE", (1, -1)), ("SW", (-1, 1)), ("SE", (1, 1))):
        x0 = ox + cx_ * h - (PPT if cx_ > 0 else 0)
        y0 = oy + cy_ * h - (PPT if cy_ > 0 else 0)
        corners[name] = cnt(mask.crop((x0, y0, x0 + PPT, y0 + PPT))) / PPT ** 2
    q = PPT // 4
    full = cnt(mask.crop((ox - h, oy - h, ox + h, oy + h)))
    inner = cnt(mask.crop((ox - h + q, oy - h + q, ox + h - q, oy + h - q)))
    band = (full - inner) / ((2 * h) ** 2 - (2 * h - 2 * q) ** 2)
    # rise over the north pictures' band: the plate's top in each port tile's column
    cols = {}
    for t in (-1, 0, 1):
        x0 = ox + t * PPT - 26
        col = mask.crop((x0, 0, x0 + 52, oy))
        cb = col.getbbox()
        cols[t] = (oy - h - cb[1]) / PPT if cb else 0.0
    m = {
        "footprint covered by mass": f"{cover * 100:.1f} %  (vanilla refinery 92-94 %; round 3 92.1 %; "
                                     "the amendment allows ~85 % for the silhouette)",
        "corner tiles covered (NW, NE, SW, SE)": ", ".join(f"{corners[c] * 100:.0f} %" for c in
                                                           ("NW", "NE", "SW", "SE")),
        "outer quarter-tile band covered": f"{band * 100:.0f} %  (a square outline is 100 %)",
        "rises above footprint north edge": f"{rise:.2f} tiles  (vanilla refinery 0.97; round 3 0.73)",
        "rise over the north port tiles -1, 0, +1": ", ".join(f"{cols[t]:.2f}" for t in (-1, 0, 1)) +
        " tiles  (assembler 3's north picture stands 0.0-0.31 above the edge; round 3 0.17, 0.09, 0.17)",
        "sprite bbox (mass)": f"{(bb[2] - bb[0]) / PPT:.2f} wide x {(bb[3] - bb[1]) / PPT:.2f} tall tiles",
        "blue (lit) pixels / opaque": f"{blue / opaque * 100:.1f} %  (vanilla fluid: chem 3.2 %, refinery 2.0 %; "
                                      "round 3 3.7 %)",
        "blue area bbox": f"{(lb[2] - lb[0]) / PPT:.2f} x {(lb[3] - lb[1]) / PPT:.2f} tiles" if lb else "none",
        "moving pixels / opaque": f"{moving / opaque * 100:.1f} %  (vanilla: chem 5.2 %, refinery 15.9 %; "
                                  "round 3 4.0 %)",
    }
    return m, acc


def outline_of(plate):
    """Cover, corner tiles and the outer band of a 1x plate on the 512 x 448 canvas."""
    mask = plate.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    cnt = lambda im: sum(1 for v in im.get_flattened_data() if v)
    ox, oy = ORIGIN
    h = FOOT * PPT // 2
    full = cnt(mask.crop((ox - h, oy - h, ox + h, oy + h)))
    cs = []
    for cx_, cy_ in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        x0 = ox + cx_ * h - (PPT if cx_ > 0 else 0)
        y0 = oy + cy_ * h - (PPT if cy_ > 0 else 0)
        cs.append(cnt(mask.crop((x0, y0, x0 + PPT, y0 + PPT))) / PPT ** 2)
    q = PPT // 4
    inner = cnt(mask.crop((ox - h + q, oy - h + q, ox + h - q, oy + h - q)))
    return {"cover": f"{full / (2 * h) ** 2 * 100:.1f} %",
            "corners (NW, NE, SW, SE)": ", ".join(f"{c * 100:.0f} %" for c in cs),
            "outer band": f"{(full - inner) / ((2 * h) ** 2 - (2 * h - 2 * q) ** 2) * 100:.0f} %"}


def vanilla_plate(stem):
    w, h, _, _ = sidecar(stem)
    p = os.path.join(X1, os.path.basename(stem) + ".png")
    Image.open(stem + ".png").convert("RGBA").crop((0, 0, w, h)).save(p)
    return p


FIN = []          # (label, finish, tonal)


def finish_rows():
    rows = [("vanilla oil refinery (north)", vanilla_plate(f"{ENT}/oil-refinery/north/oil-refinery-north")),
            ("vanilla chemical plant (north base)", vanilla_plate(f"{ENT}/chemical-plant/chemical-plant-north-base")),
            ("round 3 F (plate, idle)", R3),
            ("round 4 F (plate, idle)", save1("plate")),
            ("round 4 F (plate, working f0)", save1("plate-working"))]
    for label, p in rows:
        FIN.append((label, tool("finish.py", p), tool("tonal.py", p)))
    return rows


# ----------------------------------------------------------------- the sheet
PITCH = [
    "Read: a tall lead-clad reactor right of centre with two fat strapped glass legs standing off its west side -- a",
    "riser, where the blue climbs with bright bubbles, and a downcomer, where it falls back with dark flecks of",
    "precipitate. Fat hoses close the loop at the top into the reactor's shoulder, a cast header at the foot: a",
    "thermosiphon you watch go round. Round 4 piles it into three masses: the reactor, its legs and the compressor;",
    "the scrubber and the feed drum on the west; the press house, the filtrate receiver and the pump house on the",
    "south. The corners drop out: round vessels with ground round them in the north-west and north-east, ground in",
    "the south-west and south-east. Fluids in: solution from the feed drum into the riser's foot; crust gas through",
    "the scrubber, over a high hose into the reactor head. Solid out: the filter press drops its cake into the",
    "lead-lined drop box it stands on. Every edge's middle three tiles meet a wall, which the pipe pictures stand in:",
    "N the exchanger, E the instrument house / the reactor's foot / the side nozzle's pot, S the press house / the",
    "receiver / the pump house, W the feed drum.",
]
FINISH = [
    "Signature finish (proposed, carried over warmed): weathered LEAD. The vessels -- reactor, scrubber, the pots, the",
    "drop box, the press's leaves -- are clad in lead sheet: a dull warm grey (#66625C -> #86807A; round 3's cool",
    "#5E6064 read as blue-grey plastic beside vanilla) in sheets of slightly different age, riveted steel bands. Where",
    "the solution weeps, lead bloom (#B4A486 -> #D8CAA6, a dry cream) hangs in runs below the bands and flanges and",
    "crusts the seams; rust runs from the bands' rivets and mottles the lead lightly. The rest is vanilla's idiom:",
    "brown-grey steel (#6A625A) under a broad rust and ochre mottle, cream sheen along the round parts, worn edges,",
    "brown dirt in the contact lines and at the foot; dark tan and black rubber hoses; the motors and the instrument",
    "house in the refinery's weathered green (#4E5C36) where round 3 had teal; worn stencil fields.",
    "Lends the generator: the lead (its shielding collars are already lead-grey) and the bloom at its seams.",
]
ANIM = [
    "fluid in the legs (working_visualisation): 24 f, bands rising two wavelengths a loop in the riser and falling",
    "  in the downcomer; bubbles up the riser, flecks down the downcomer, each wrapping. Loop ~1.7 s at 14 fps",
    "agitator coupling on the head, compressor, dosing and pump couplings: 12 f, 60 deg a loop (six-fold)",
    "glow: the legs only, differenced; the two status lamps. Idle: frame 0, light off, the legs a still dark navy",
    "recipe tint: none now (one recipe); the leg sheet can take apply_recipe_tint later",
]


def am3_beside(k=4):
    """Each face: assembler 3's picture beside the plant's own, at k x."""
    ims = []
    for f in "NESW":
        w, h, _, _ = sidecar(AM3 + f)
        a = Image.open(AM3 + f + ".png").convert("RGBA").crop((0, 0, w, h))
        b = Image.open(os.path.join(PORTS, f"port-{f}.png")).convert("RGBA")
        ims.append((f, a, b))
    W = sum((a.width + b.width) * k + 40 for _, a, b in ims)
    H = max(max(a.height, b.height) * k for _, a, b in ims) + 24
    c = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(c)
    x = 0
    for f, a, b in ims:
        for im, lab in ((a, "am3"), (b, "ours")):
            g = Image.new("RGBA", (im.width * k, im.height * k), GROUND)
            g.alpha_composite(im.resize((im.width * k, im.height * k), Image.NEAREST))
            c.alpha_composite(g, (x, 24))
            d.text((x + 2, 4), f"{f} {lab}", font=font(13, True), fill=TEXT)
            x += g.width + 8
        x += 24
    return c


def silhouette(im, k=1):
    """The plate's alpha over 128 in a light tone on the ground, the footprint outlined."""
    a = im.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    g = ground(im.size, ORIGIN, PPT)
    g.paste(Image.new("RGBA", im.size, (196, 186, 170, 255)), (0, 0), a)
    d = ImageDraw.Draw(g)
    h = FOOT * PPT // 2
    d.rectangle([ORIGIN[0] - h, ORIGIN[1] - h, ORIGIN[0] + h, ORIGIN[1] + h], outline=(255, 90, 60, 255), width=2)
    for i in range(-2, 3):
        for e in (-1, 1):
            pass
    return g.crop(CROP1)


def sheet(m, mov):
    work = compose(load("working-00", 2), 2, ports_for("N")).crop(CROP2)
    idle = compose(load("idle", 2), 2, ports_for("N")).crop(CROP2)
    idle.convert("RGB").save(f"{OUT}/{SLUG}-idle.png")
    w1 = compose(load("working-00", 1), 1, ports_for("N"))
    tint = Image.new("RGBA", w1.size, (255, 0, 200, 0))
    tint.putalpha(mov.point(lambda v: int(v * 0.75)))
    w1m = w1.copy()
    w1m.alpha_composite(tint)
    w1, w1m = w1.crop(CROP1), w1m.crop(CROP1)
    gap = 20
    W = gap + work.width + gap + idle.width + gap + w1.width + gap
    s = Image.new("RGBA", (W, 9000), BG)
    d = ImageDraw.Draw(s)
    d.text((gap, 14), "F  THE CIRCULATOR -- round 4: the plant's own pipe pictures, vanilla's texturing",
           font=font(30, True), fill=TEXT)
    d.text((gap, 54), "Reaction Plant redesign at 5x5, a concept before the spec and the model: lit Blender (Claude in "
           "Chrome had no browser connected). One plate under rotation; the pipe pictures are the plant's own.",
           font=font(15), fill=SUB)
    y = 90
    d.text((gap, y), "WORKING, 2x (frame 0; facing north: inputs at -1, +1 north, output at 0 south)",
           font=font(15, True), fill=HEAD)
    d.text((2 * gap + work.width, y), "IDLE, 2x (light off, stopped)", font=font(15, True), fill=HEAD)
    s.alpha_composite(work, (gap, y + 22))
    s.alpha_composite(idle, (2 * gap + work.width, y + 22))
    x3 = 3 * gap + 2 * work.width
    d.text((x3, y), "WORKING, 1x", font=font(15, True), fill=HEAD)
    s.alpha_composite(w1, (x3, y + 22))
    d.text((x3, y + 22 + w1.height + 10), "1x, MOVING PIXELS IN MAGENTA", font=font(15, True), fill=HEAD)
    s.alpha_composite(w1m, (x3, y + 22 + w1.height + 32))
    y += 22 + max(work.height, 2 * w1.height + 32) + 24
    # the four rotations at 1x
    d.text((gap, y), "THE ONE PLATE UNDER ROTATION, 1x (idle): inputs at -1 and +1 on the faced side, the output "
           "at 0 opposite; the plant's pictures, vanilla's covers on all three, as nothing is joined", font=font(15, True), fill=HEAD)
    y += 24
    x = gap
    for dd in "NESW":
        im = compose(load("idle", 1), 1, ports_for(dd)).crop(CROP1)
        s.alpha_composite(im, (x, y))
        d.text((x + 6, y + 4), f"facing {dd}", font=font(14, True), fill=TEXT)
        x += im.width + 12
    y += im.height + 24
    d.text((gap, y), "THE FOUR ROTATIONS, 2x", font=font(15, True), fill=HEAD)
    y += 24
    for i, dd in enumerate("NESW"):
        im = compose(load("idle", 2), 2, ports_for(dd)).crop(CROP2)
        px, py = gap + (i % 2) * (im.width + 12), y + (i // 2) * (im.height + 12)
        s.alpha_composite(im, (px, py))
        d.text((px + 8, py + 6), f"facing {dd}", font=font(16, True), fill=TEXT)
    y += 2 * (im.height + 12) + 12
    # the pipe pictures
    d.text((gap, y), "THE PIPE PICTURES, 4x: assembler 3's (left of each pair) and the plant's own, rendered by "
           "r4_circulator.py --ports, packed by pack_ports.py", font=font(15, True), fill=HEAD)
    y += 24
    ab = am3_beside()
    s.alpha_composite(ab, (gap, y))
    y += ab.height + 8
    for ln in ["Template rules 6 and 7: assembler 3's outline, size and placement (traced from its pixels, within 1 px "
               "on every face: " + PORTM + "),",
               "  in the plant's own metal: the south stub stands in a bolted plate of the receiver's shell with a "
               "riveted wall flange; east and west",
               "  a neck and flange from a dark cast plate, as the Vacuum Furnace's; north the flange's top behind the "
               "building. The covers are vanilla's,",
               "  drawn over each picture as the engine caps an unjoined port. Round 3 drew assembler 3's own green "
               "pictures under vanilla's covers as stand-ins."]:
        d.text((gap, y), ln, font=font(14), fill=TEXT)
        y += 19
    y += 14
    d.text((gap, y), "ALL TWELVE AT ONCE, 2x (-1, 0, +1 on every edge, no covers), and THE SILHOUETTE at 1x: round 4, "
           "round 3 (alpha over 128, footprint in red)", font=font(15, True), fill=HEAD)
    y += 24
    a = compose(load("idle", 2), 2, ALL_PORTS, covers=False).crop(CROP2)
    s.alpha_composite(a, (gap, y))
    s4 = silhouette(load("plate", 1))
    r3p = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    r3p.alpha_composite(Image.open(R3).convert("RGBA"))
    s3 = silhouette(r3p)
    s.alpha_composite(s4, (2 * gap + a.width, y))
    s.alpha_composite(s3, (3 * gap + a.width + s4.width, y))
    d.text((2 * gap + a.width + 6, y + 4), "round 4", font=font(14, True), fill=(30, 30, 30))
    d.text((3 * gap + a.width + s4.width + 6, y + 4), "round 3", font=font(14, True), fill=(30, 30, 30))
    yy = y + s4.height + 12
    for k_ in ("footprint covered by mass", "corner tiles covered (NW, NE, SW, SE)", "outer quarter-tile band covered",
               "rise over the north port tiles -1, 0, +1"):
        d.text((2 * gap + a.width, yy), f"{k_}: {m[k_].split('  (')[0]}", font=font(13), fill=TEXT)
        yy += 18
    for k_, v in R3M.items():
        d.text((2 * gap + a.width, yy), f"round 3 {k_}: {v}", font=font(13), fill=SUB)
        yy += 18
    y += max(a.height, yy - y) + 16
    # the legs' frame strip
    w2 = load("working-00", 2)
    sat = ImageChops.subtract(w2.getchannel("B"), w2.getchannel("R")).point(lambda v: 255 if v > 110 else 0)
    bb = ImageChops.multiply(sat, w2.getchannel("A").point(lambda v: 255 if v > 200 else 0)).getbbox()
    pad = 16
    bb = (bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad)
    d.text((gap, y), "THE LEGS, 2x: frames 0, 4, 8, 12, 16, 20 of the 24-frame loop", font=font(15, True), fill=HEAD)
    y += 22
    x = gap
    for f in range(0, NF, 4):
        fr = compose(load(f"working-{f:02d}", 2), 2, []).crop(bb)
        s.alpha_composite(fr, (x, y))
        x += fr.width + 6
    y += bb[3] - bb[1] + 24
    # text
    def block(title, lines, size=14):
        nonlocal y
        d.text((gap, y), title, font=font(16, True), fill=HEAD)
        y += 24
        for ln in lines:
            d.text((gap + 8, y), ln, font=font(size), fill=TEXT)
            y += 19
        y += 10
    block("PITCH", PITCH)
    block("FINISH", FINISH)
    block("FINISH AND TONE, MEASURED (tools/blender/finish.py, tonal.py; each plate alone, 64 px a tile)",
          [f"{lab:36s} {fi}" for lab, fi, _ in FIN] + [""] + [f"{lab:36s} {to}" for lab, _, to in FIN] +
          ["", "vanilla's range: black 5-12 %, ratio ~0.5, darkchr 7-15; p50 41-63 (the mod's accepted look ~75-81), "
           "p95 143-189, spread 140-177"], size=13)
    block("BLUE", ["The solution, lit, in the two glass legs and nowhere else: " + m["blue (lit) pixels / opaque"],
                   "Idle, the legs hold a still dark navy. No blue paint, cable or lamp anywhere else on the plate."])
    block("ANIMATION PLAN (spec 6.2)", ANIM)
    block("MEASURED (64 px a tile; cover from the plate alone, no ground shadow)",
          [f"{k}: {v}" for k, v in m.items()], size=13)
    s = s.crop((0, 0, W, y + 10))
    s.convert("RGB").save(f"{OUT}/{SLUG}.png")
    print(f"{OUT}/{SLUG}.png", s.size)


def gif():
    frames = []
    for f in range(NF):
        g2 = compose(load(f"working-{f:02d}", 2), 2, ports_for("N")).crop(CROP2)
        g1 = compose(load(f"working-{f:02d}", 1), 1, ports_for("N")).crop(CROP1)
        im = Image.new("RGBA", (g2.width + g1.width + 12, g2.height), BG)
        im.alpha_composite(g2, (0, 0))
        im.alpha_composite(g1, (g2.width + 12, 0))
        frames.append(im.convert("RGB"))
    strip = Image.new("RGB", (frames[0].width, frames[0].height * NF))
    for i, f in enumerate(frames):
        strip.paste(f, (0, i * f.height))
    pal = strip.quantize(colors=256)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    path = f"{OUT}/{SLUG}-working.gif"
    q[0].save(path, save_all=True, append_images=q[1:], duration=GIF_MS, loop=0, optimize=True)
    print(path, f"{os.path.getsize(path) / 1e6:.1f} MB")


# ----------------------------------------------------------------- compare plates
def shadow_img(im):
    a = im.getchannel("A").point(lambda v: v // 2)
    s = Image.new("RGBA", im.size, (0, 0, 0, 0))
    s.putalpha(a)
    return s


def at(panel, im, origin, shift_px):
    paste(panel, im, (origin[0] + shift_px[0], origin[1] + shift_px[1]))


def vanilla_chem(panel, origin):
    p = f"{ENT}/chemical-plant/chemical-plant-north"
    sh = Image.open(f"{ENT}/chemical-plant/chemical-plant-shadow.png").convert("RGBA").crop((0, 0, 312, 222))
    at(panel, shadow_img(sh), origin, (54, 12))
    for stem in ("-base", "-anim-1", "-anim-2"):
        w, h, sx, sy = sidecar(p + stem)
        im = Image.open(p + stem + ".png").convert("RGBA").crop((0, 0, w, h))
        at(panel, im, origin, (2 * sx, 2 * sy - 18))
    liq = Image.open(f"{ENT}/chemical-plant/chemical-plant-liquid-north.png").convert("RGBA").crop((0, 0, 66, 44))
    r, g, b, a = liq.split()
    liq = Image.merge("RGBA", (r, g.point(lambda v: v * 244 // 255), b.point(lambda v: 0), a))
    at(panel, liq, origin, (46, 30))


def vanilla_refinery(panel, origin):
    p = f"{ENT}/oil-refinery/north/oil-refinery"
    w, h, sx, sy = sidecar(f"{p}-shadow-north")
    at(panel, shadow_img(Image.open(f"{p}-shadow-north.png").convert("RGBA").crop((0, 0, w, h))), origin,
       (2 * sx, 2 * sy))
    stems = ["-north"] + [f"-anim-north-{i}" for i in range(1, 7)] + [f"-fluid-north-{i}" for i in range(1, 7)]
    for st in stems:
        w, h, sx, sy = sidecar(p + st)
        im = Image.open(p + st + ".png").convert("RGBA").crop((0, 0, w, h))
        if "fluid" in st:
            tv = (253, 115, 15)
            ch = [c.point(lambda v, t=t: int(2 * v * t / 255) if v < 128 else int(255 - 2 * (255 - v) * (255 - t) / 255))
                  for c, t in zip(im.split()[:3], tv)]
            im = Image.merge("RGBA", (*ch, im.getchannel("A")))
        at(panel, im, origin, (2 * sx, 2 * sy))


def compare():
    PH = 8 * PPT
    panels = []

    def panel(w_tiles, foot, label, fin, draw):
        size = (w_tiles * PPT, PH)
        origin = (size[0] // 2 - (PPT // 2 if foot == 5 else 0), PH - int((foot / 2 + 1.0) * PPT))
        g = ground(size, origin, PPT, foot)
        draw(g, origin)
        panels.append((label, fin, g))

    fin = {lab: (fi, to) for lab, fi, to in FIN}
    panel(8, 5, "vanilla oil refinery, 5x5", fin["vanilla oil refinery (north)"], vanilla_refinery)
    panel(5, 3, "vanilla chemical plant, 3x3", fin["vanilla chemical plant (north base)"], vanilla_chem)
    # round 3's F, its panel lifted whole from round 3's compare plates (same scale, grid, frame 0 working,
    # assembler 3's pictures and vanilla's covers as its stand-ins)
    r3 = Image.open(f"{R3_SHEETS}/compare-plates.png").convert("RGBA").crop((1376, 82, 1376 + 512, 82 + 512))
    g = Image.new("RGBA", (8 * PPT, PH), GROUND)
    g.alpha_composite(r3, (0, 0))
    panels.append(("round 3: F, textured (stand-in pictures)", fin["round 3 F (plate, idle)"], g))

    def ours(g, origin):
        im = compose(load("working-00", 1), 1, ports_for("N"))
        at(g, im, origin, (CANVAS[0] / 2 - ORIGIN[0], CANVAS[1] / 2 - ORIGIN[1]))
    panel(8, 5, "round 4: F, own pipe pictures, vanilla texturing", fin["round 4 F (plate, idle)"], ours)
    W = sum(p.width for _, _, p in panels) + 8 * (len(panels) + 1)
    sheet = Image.new("RGBA", (W, PH + 150), BG)
    d = ImageDraw.Draw(sheet)
    d.text((10, 8), "REACTION PLANT ROUND 4 -- F AT GAME SCALE BESIDE VANILLA AND ROUND 3", font=font(20, True),
           fill=TEXT)
    d.text((10, 36), "64 px a tile; frame 0 working, with shadows. Vanilla composited from its own layers (refinery "
           "tinted for advanced oil processing, chemical plant for sulfuric acid); round 3's F lifted from its compare "
           "plates. Round 4 carries its own pipe pictures and vanilla's covers (inputs north, output south).", font=font(12), fill=SUB)
    x = 8
    for label, (fi, to), p in panels:
        d.text((x + 2, 62), label, font=font(12, True), fill=TEXT)
        sheet.alpha_composite(p, (x, 82))
        d.text((x + 2, PH + 90), fi, font=font(10), fill=SUB)
        d.text((x + 2, PH + 106), to, font=font(10), fill=SUB)
        x += p.width + 8
    sheet = sheet.crop((0, 0, W, PH + 126))
    sheet.convert("RGB").save(f"{OUT}/compare-plates.png")
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).convert("RGB").save(
        f"{OUT}/compare-plates-2x.png")
    print(f"{OUT}/compare-plates.png", sheet.size)


finish_rows()
M, MOV = measure()
R3M = outline_of(Image.open(R3).convert("RGBA"))
PORT_LINES = subprocess.run([sys.executable, os.path.join(REPO, "concept", "ballast-drill", "model", "measure_ports.py"),
                             PORTS], capture_output=True, text=True).stdout.strip().splitlines()
PORTM = ", ".join(f"{ln[0]} far {re.search(r'far_px.: ([\d.]+)', ln).group(1)} px" for ln in PORT_LINES)
sheet(M, MOV)
gif()
compare()
with open(f"{OUT}/measures.txt", "w") as fh:
    fh.write("F  THE CIRCULATOR, round 4 (own pipe pictures, vanilla texturing)\n" +
             "".join(f"  {k}: {v}\n" for k, v in M.items()))
    fh.write("  round 3, same measures: " + "; ".join(f"{k} {v}" for k, v in R3M.items()) + "\n")
    fh.write("\npipe pictures against assembler 3's outline (concept/ballast-drill/model/measure_ports.py; "
             "criterion: far_px 1 or less)\n" + "".join(f"  {ln}\n" for ln in PORT_LINES))
    fh.write("\nfinish.py (black, fine, mid, ratio, darkchr) -- vanilla: black 5-12 %, ratio ~0.5, darkchr 7-15\n")
    fh.write("".join(f"  {lab:36s} {fi}\n" for lab, fi, _ in FIN))
    fh.write("tonal.py (p5, p50, p95, spread) -- vanilla: p50 41-63 (mod ~75-81), p95 143-189, spread 140-177\n")
    fh.write("".join(f"  {lab:36s} {to}\n" for lab, _, to in FIN))
for f in os.listdir(X1):
    os.remove(os.path.join(X1, f))
os.rmdir(X1)
print(open(f"{OUT}/measures.txt").read())
