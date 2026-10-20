#!/usr/bin/env python3
"""Reaction plant (the Circulator, 5x5): the full model's review sheet, GIF, rotations and measures.

  python3 review_sheet.py <run-dir> --r5 <r5-hi-dir> [--factorio <data>]

<run-dir> is tools/blender/render.sh's output for circulator.py with --ports --icon:
renders/ (sprite size), sheets/ (the packed sheets and meta.json), sheets/ports/,
sheets/icon.png. <r5-hi-dir> is round 5's model re-rendered for the compare row
(options/round-5/r5_circulator.py -- <dir> --only idle: plate.png at 4x on its 512 x 448
canvas, the origin at (208, 272)). Everything here is drawn from the PACKED sheets, placed
by their meta.json shifts as the engine places them, so the sheet checks the packing too.
Writes beside this script:

  review-top.png   review.png's top section (to the frame strips), under 8000 px tall, for sending
  review.png       the plate beside the oil refinery, the chemical plant and round 5 at 1x
                   and 2x on one ground; idle and working; the glow; a frame strip of every
                   layer; the four rotations; the icon; the measures
  rotations.png    the four rotations at 1x and 2x, each with all three pipe pictures (no
                   recipe) and with the two inputs alone (sae-radiant-precipitation)
  motion-1x.gif    every motion together at 1x, 48 frames at 14 fps: the 24-frame loops
                   twice, the press once in frames 24-39 (in game: once per craft)
  measures.txt     every check and measure, and the layer list
  sheets/          a copy of the packed sheets (and ports/, icon.png), for sign-off

1x is the sprites' own 64 px a tile (the game's high-resolution scale).
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("run")
ap.add_argument("--r5", required=True)
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
args = ap.parse_args()
RUN, R5, FD = args.run, args.r5, args.factorio
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
TOOLS = os.path.join(REPO, "tools", "blender")
SHEETS = os.path.join(RUN, "sheets")
RENDERS = os.path.join(RUN, "renders")
ENT = f"{FD}/base/graphics/entity"
COVER = f"{ENT}/pipe-covers/pipe-cover-"
META = json.load(open(os.path.join(SHEETS, "meta.json")))
PMETA = json.load(open(os.path.join(SHEETS, "ports", "meta.json")))
MODEL = json.load(open(os.path.join(RENDERS, "..", "hi", "model.json")))
PPT = 64
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)
NF, PRESS_NF = 24, 16
COUPLINGS = ("coupling-dosing", "coupling-pump")    # the compressor's is never seen: no sheet (circulator.py HIDDEN)
GAUGES = ("gauge-reactor-upper", "gauge-reactor-lower", "gauge-scrubber")
LOOPS = ("drive",) + COUPLINGS + GAUGES + ("drip",)
# the two sheets these six replaced (the full model's pack of 2026-10-11): name, frame w x h, frames
BEFORE = (("couplings", 142, 120, 24), ("gauges", 200, 168, 24))
GREEN, AMBER = (90, 255, 110), (255, 196, 60)


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def sheet(name):
    return Image.open(os.path.join(SHEETS, name + ".png")).convert("RGBA")


SH = {n: sheet(n) for n in META if n != "checks"}


def frame_of(name, f=0):
    m = META[name]
    w, h = m["size"]
    n = m.get("frames", 1)
    f %= n
    line = m.get("line_length", 1)
    x, y = (f % line) * w, (f // line) * h
    return SH[name].crop((x, y, x + w, y + h))


def place(canvas, im, centre, k=1):
    """Paste im (at 1x) scaled k, its centre at `centre` (canvas px)."""
    if k != 1:
        im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    x = round(centre[0] - im.width / 2)
    y = round(centre[1] - im.height / 2)
    canvas.alpha_composite(im, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))


def at_shift(canvas, origin, name, f=0, k=1, tint=None):
    im = frame_of(name, f)
    if tint:
        r, g, b = tint
        a = im.getchannel("A")
        im = Image.merge("RGBA", (*Image.new("RGB", im.size, (r, g, b)).split(), a))
    sx, sy = META[name]["shift"]
    place(canvas, im, (origin[0] + sx * PPT * k, origin[1] + sy * PPT * k), k)


def ground(size, origin, k, foot=5, grid=True):
    g = Image.new("RGBA", size, GROUND)
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ox, oy = origin
    off = 0.5 if foot % 2 else 0.0
    if grid:
        for i in range(-20, 21):
            x = ox + (i + off) * PPT * k
            y = oy + (i + off) * PPT * k
            d.line([(x, 0), (x, size[1])], fill=(255, 255, 255, 22))
            d.line([(0, y), (size[0], y)], fill=(255, 255, 255, 22))
    h = foot * PPT * k / 2
    d.rectangle([ox - h, oy - h, ox + h, oy + h], outline=(255, 255, 255, 110))
    g.alpha_composite(ov)
    return g


NAME = {"N": "north", "E": "east", "S": "south", "W": "west"}


def port_layers(face, t, k):
    """(picture, cover, picture centre, cover centre) in k x px from the origin, for a port on
    `face` at position t along it: the plant's own picture at pack_ports.py's shift, drawn
    from the tile the connection points into; vanilla's cover centred on that tile."""
    off = {"N": (t, -3), "S": (t, 3), "E": (3, -t), "W": (-3, -t)}[face]
    cx, cy = off[0] * PPT * k, off[1] * PPT * k
    sx, sy = PMETA[f"port-{face}"]["shift"]
    pic = Image.open(os.path.join(SHEETS, "ports", f"port-{face}.png")).convert("RGBA")
    cov = Image.open(COVER + NAME[face] + ".png").convert("RGBA")
    if k != 1:
        pic = pic.resize((pic.width * k, pic.height * k), Image.LANCZOS)
        cov = cov.resize((cov.width * k, cov.height * k), Image.LANCZOS)
    return pic, cov, (cx + sx * PPT * k, cy + sy * PPT * k), (cx, cy)


def ports_for(direction, output=True):
    opp = {"N": "S", "S": "N", "E": "W", "W": "E"}[direction]
    return [(direction, -1), (direction, 1)] + ([(opp, 0)] if output else [])


def machine(canvas, origin, k, f=0, press=0, working=True, ports=(), shadow=True, lamps=True):
    """The plant as the engine draws it: shadow, the north pictures behind, the plate, the
    animation's layers at frame f (the press at its frame), the legs while working, the
    status lamps tinted, then the other pictures and vanilla's covers."""
    layers = [port_layers(fc, t, k) for fc, t in ports]

    def draw(north):
        for (fc, _), (pic, cov, pc, cc) in zip(ports, layers):
            if (fc == "N") == north:
                place(canvas, pic, (origin[0] + pc[0], origin[1] + pc[1]))
                place(canvas, cov, (origin[0] + cc[0], origin[1] + cc[1]))
    if shadow:
        at_shift(canvas, origin, "shadow", 0, k)
    draw(True)
    at_shift(canvas, origin, "base", 0, k)
    for name in LOOPS:
        at_shift(canvas, origin, name, f, k)
    at_shift(canvas, origin, "press", press, k)
    if working:
        at_shift(canvas, origin, "legs", f, k)
    if lamps:
        at_shift(canvas, origin, "status-lamp", 0, k, tint=GREEN if working else AMBER)
    draw(False)
    return canvas


def panel(size_tiles, k, origin_tiles):
    W, H = (round(v * PPT * k) for v in size_tiles)
    o = (round(origin_tiles[0] * PPT * k), round(origin_tiles[1] * PPT * k))
    return ground((W, H), o, k), o


def label(im, text, sub=None):
    out = Image.new("RGBA", (im.width, im.height + (46 if sub else 28)), BG)
    d = ImageDraw.Draw(out)
    d.text((4, 4), text, font=font(15, True), fill=TEXT)
    if sub:
        d.text((4, 24), sub, font=font(12), fill=SUB)
    out.alpha_composite(im, (0, out.height - im.height))
    return out


def row(ims, gap=16):
    W = sum(i.width for i in ims) + gap * (len(ims) - 1)
    H = max(i.height for i in ims)
    out = Image.new("RGBA", (W, H), BG)
    x = 0
    for i in ims:
        out.alpha_composite(i, (x, 0))
        x += i.width + gap
    return out


def stack(ims, gap=24, pad=16):
    W = max(i.width for i in ims) + 2 * pad
    H = sum(i.height for i in ims) + gap * (len(ims) - 1) + 2 * pad
    out = Image.new("RGBA", (W, H), BG)
    y = pad
    for i in ims:
        out.alpha_composite(i, (pad, y))
        y += i.height + gap
    return out


def heading(text, width, size=20):
    im = Image.new("RGBA", (width, size + 14), BG)
    ImageDraw.Draw(im).text((0, 4), text, font=font(size, True), fill=HEAD)
    return im


def para(lines, width, size=13):
    im = Image.new("RGBA", (width, (size + 5) * len(lines) + 6), BG)
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        d.text((0, 3 + (size + 5) * i), ln, font=font(size), fill=TEXT)
    return im


def sidecar(stem):
    t = open(stem + ".lua").read()
    w = int(re.search(r"width\s*=\s*(\d+)", t).group(1))
    h = int(re.search(r"height\s*=\s*(\d+)", t).group(1))
    sx, sy = map(float, re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", t).groups())
    return w, h, sx * 2, sy * 2            # by_pixel is in game px (32 a tile); sprites are 64


def vanilla(stem):
    w, h, sx, sy = sidecar(stem)
    return Image.open(stem + ".png").convert("RGBA").crop((0, 0, w, h)), (sx, sy)


def r5_plate(k):
    im = Image.open(os.path.join(R5, "plate.png")).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    im = im.convert("RGBa").resize((im.width // 4, im.height // 4), Image.LANCZOS).convert("RGBA")
    # its canvas 512 x 448 with the origin at (208, 272): the shift of its centre
    return im, ((256 - 208), (224 - 272))


# ===================================================================== measures
def tool(name, path):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, name), path], capture_output=True, text=True)
    return " ".join(r.stdout.split()[1:]).split("(vanilla")[0].strip()


def composite_1x(f=0, press=0, working=True, lamps=False):
    """The machine alone (no ground, shadow or ports) on the renders' canvas at 1x."""
    W, H = 416, 480
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return machine(c, (W // 2, H // 2), 1, f, press, working, ports=(), shadow=False, lamps=lamps)


def cnt(im):
    return sum(1 for v in im.get_flattened_data() if v)


def is_blue(px):
    r, g, b = px[:3]
    return px[3] > 128 and b > 70 and b - max(r, g) > 35


def measures():
    m = {}
    idle = Image.open(os.path.join(RENDERS, "idle.png")).convert("RGBA")
    W, H = idle.size
    ox, oy = W / 2, H / 2
    mask = idle.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    h = 5 * PPT // 2
    box = (int(ox - h), int(oy - h), int(ox + h), int(oy + h))
    m["cover"] = cnt(mask.crop(box)) / (2 * h) ** 2
    corners = {}
    for nm, (cx_, cy_) in (("NW", (-1, -1)), ("NE", (1, -1)), ("SW", (-1, 1)), ("SE", (1, 1))):
        x0 = int(ox + cx_ * h - (PPT if cx_ > 0 else 0))
        y0 = int(oy + cy_ * h - (PPT if cy_ > 0 else 0))
        corners[nm] = cnt(mask.crop((x0, y0, x0 + PPT, y0 + PPT))) / PPT ** 2
    m["corners"] = corners
    bb = mask.getbbox()
    m["rise"] = (oy - h - bb[1]) / PPT
    m["bbox"] = ((bb[2] - bb[0]) / PPT, (bb[3] - bb[1]) / PPT)
    cols = {}
    for t in (-1, 0, 1):
        x0 = int(ox + t * PPT - 26)
        cb = mask.crop((x0, 0, x0 + 52, int(oy))).getbbox()
        cols[t] = (oy - h - cb[1]) / PPT if cb else 0.0
    m["rise_ports"] = cols
    # blue: the working machine (legs lit) against the idle one
    work0, idle0 = composite_1x(0, working=True), composite_1x(0, working=False)
    opaque = cnt(work0.getchannel("A").point(lambda v: 255 if v > 128 else 0))
    wpx, ipx = list(work0.get_flattened_data()), list(idle0.get_flattened_data())
    blue = [i for i, (p, q) in enumerate(zip(wpx, ipx)) if is_blue(p) and p[2] - q[2] > 40]
    m["blue_share"] = len(blue) / opaque
    xs, ys = [i % W for i in blue], [i // W for i in blue]
    m["blue_bbox_tiles"] = ((min(xs) - ox) / PPT, (min(ys) - oy) / PPT, (max(xs) + 1 - ox) / PPT,
                            (max(ys) + 1 - oy) / PPT) if blue else None
    # blue outside the legs: any blue-hued pixel in the plate, in any frame of the other layers,
    # or in the lamps, outside the legs layer's own footprint (the union of its frames' alpha)
    legs_mask = Image.new("L", (W, H), 0)
    for f in range(NF):
        c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        at_shift(c, (W // 2, H // 2), "legs", f)
        legs_mask = ImageChops.lighter(legs_mask, c.getchannel("A").point(lambda v: 255 if v > 0 else 0))
    lm = list(legs_mask.get_flattened_data())
    stray = {}
    for name, n in [("base", 1)] + [(nm, META[nm]["frames"]) for nm in LOOPS + ("press",)]:
        for f in range(n):
            c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            at_shift(c, (W // 2, H // 2), name, f)
            k_ = sum(1 for p, l_ in zip(c.get_flattened_data(), lm) if not l_ and is_blue(p))
            if k_:
                stray[f"{name}[{f}]"] = k_
    m["blue_outside_legs"] = stray
    # the glow: its colour and where it is
    glow = frame_of("legs-glow")
    gpx = [p for p in glow.get_flattened_data() if p[3]]
    m["glow_px"] = len(gpx)
    m["glow_mean"] = tuple(round(sum(p[i] for p in gpx) / len(gpx)) for i in range(3)) if gpx else None
    # moving share: every frame of every motion against frame 0, working
    acc = Image.new("L", (W, H), 0)
    states = [(f, 0) for f in range(1, NF)] + [(0, k) for k in range(1, PRESS_NF)]
    per = {}
    for f, k in states:
        d = ImageChops.difference(work0, composite_1x(f, k, working=True)).convert("L").point(
            lambda v: 255 if v > 10 else 0)
        acc = ImageChops.lighter(acc, d)
    m["moving_share"] = cnt(ImageChops.multiply(acc, work0.getchannel("A").point(lambda v: 255 if v > 128 else 0))) \
        / opaque
    for name in ("legs",) + LOOPS + ("press",):
        n = META[name]["frames"]
        c0 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        at_shift(c0, (W // 2, H // 2), name, 0)
        a = Image.new("L", (W, H), 0)
        for f in range(1, n):
            c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            at_shift(c, (W // 2, H // 2), name, f)
            a = ImageChops.lighter(a, ImageChops.difference(c0, c).convert("L").point(lambda v: 255 if v > 10 else 0))
        per[name] = cnt(a) / opaque
    m["moving_per_layer"] = per
    return m


# ===================================================================== the pictures
def compare(k):
    """The oil refinery, the chemical plant, round 5's F and the model, frame 0, plates only,
    at k x on one ground."""
    tiles = (6.4, 7.2)
    origin = (3.2, 4.0)
    out = []
    ref, rs = vanilla(f"{ENT}/oil-refinery/north/oil-refinery-north")
    chem, cs = vanilla(f"{ENT}/chemical-plant/chemical-plant-north-base")
    r5, r5s = r5_plate(1)
    for title, foot, im, s in (("oil refinery (5x5)", 5, ref, rs), ("chemical plant (3x3)", 3, chem, cs),
                               ("round 5's F (signed off)", 5, r5, r5s)):
        g, o = panel(tiles, k, origin)
        g = ground(g.size, o, k, foot)
        place(g, im, (o[0] + s[0] * k, o[1] + s[1] * k), k)
        out.append(label(g, title))
    g, o = panel(tiles, k, origin)
    machine(g, o, k, 0, 0, working=False, shadow=False, lamps=False)
    out.append(label(g, "the full model (idle, frame 0)"))
    return row(out)


def states(k=2):
    tiles = (7.2, 7.6)
    origin = (3.2, 4.0)
    ims = []
    for title, working in (("idle: the legs dark navy, the press shut, lamp amber", False),
                           ("working, frame 0: the legs lit, lamp green", True)):
        g, o = panel(tiles, k, origin)
        machine(g, o, k, 0, 0, working=working, ports=ports_for("N", output=False))
        ims.append(label(g, title, "with its shadow and the two input pictures (the precipitation recipe)"))
    # the glow alone, on black, and added over the working machine
    g = Image.new("RGBA", ims[0].size[:1] + (ims[0].height - 46,), (0, 0, 0, 255))
    o = (round(origin[0] * PPT * k), round(origin[1] * PPT * k))
    at_shift(g, o, "legs-glow", 0, k)
    ims.append(label(g, "legs-glow alone (additive), on black", "the legs only; one strength (spec 6.1)"))
    return row(ims)


def strip(name, k=2, per_row=12):
    """Every frame of a layer, drawn over the plate and cropped to the layer's own crop
    (with a margin), at k x."""
    m = META[name]
    w, h = m["size"]
    sx, sy = m["shift"]
    n = m["frames"]
    W, H = 416, 480
    cx, cy = W / 2 + sx * PPT, H / 2 + sy * PPT
    pad = 6
    box = (int(cx - w / 2 - pad), int(cy - h / 2 - pad), int(cx + w / 2 + pad), int(cy + h / 2 + pad))
    tiles = []
    for f in range(n):
        if name == "press":
            c = composite_1x(0, f, working=True)
        else:
            c = composite_1x(f, 0, working=True)
        g = Image.new("RGBA", (W, H), GROUND)
        g.alpha_composite(c)
        t = g.crop(box)
        t = t.resize((t.width * k, t.height * k), Image.LANCZOS)
        d = ImageDraw.Draw(t)
        d.text((3, 2), f"{f}", font=font(12, True), fill=(255, 240, 200))
        if name == "press" and f == 10:
            d.text((3, 16), "lands", font=font(11, True), fill=(255, 140, 110))
        tiles.append(t)
    rows_ = [row(tiles[i:i + per_row], gap=4) for i in range(0, n, per_row)]
    return stack(rows_, gap=4, pad=0)


def rotations(k):
    tiles = (8.0, 8.0)
    origin = (4.0, 4.1)
    ims = []
    for d in "NESW":
        g, o = panel(tiles, k, origin)
        machine(g, o, k, 0, 0, working=False, ports=ports_for(d))
        ims.append(label(g, f"facing {NAME[d]}: three pictures (no recipe)",
                         f"inputs at -1 and +1 on the {NAME[d]} face, the output opposite"))
    return row(ims)


def rotations_two(k):
    tiles = (8.0, 8.0)
    origin = (4.0, 4.1)
    ims = []
    for d in "NESW":
        g, o = panel(tiles, k, origin)
        machine(g, o, k, 0, 0, working=True, ports=ports_for(d, output=False))
        ims.append(label(g, f"facing {NAME[d]}: two inputs (precipitation)", "the engine drops the output box"))
    return row(ims)


def icon_panel():
    ic = Image.open(os.path.join(SHEETS, "icon.png")).convert("RGBA")
    big = ic.crop((0, 0, 64, 64)).resize((256, 256), Image.NEAREST)
    ims = []
    for im, t in ((ic, "icon.png, 120 x 64 (64/32/16/8)"), (big, "the 64 at 4x"),
                  (ic.crop((64, 0, 96, 32)).resize((128, 128), Image.NEAREST), "the 32 at 4x")):
        g = Image.new("RGBA", (max(im.width, 120) + 8, im.height + 8), (52, 50, 48, 255))
        g.alpha_composite(im, (4, 4))
        ims.append(label(g, t))
    mpath = os.path.join(SHEETS, "masters", "icon.png")
    if os.path.isfile(mpath):
        ms = Image.open(mpath).convert("RGBA").resize((256, 256), Image.LANCZOS)
        g = Image.new("RGBA", (264, 264), (52, 50, 48, 255))
        g.alpha_composite(ms, (4, 4))
        ims.append(label(g, "the keyed master"))
    return row(ims)


def gif(path, k=1):
    tiles = (7.0, 7.6)
    origin = (3.2, 4.0)
    frames = []
    for f in range(48):
        pk = f - 24 if 24 <= f < 40 else 0
        g, o = panel(tiles, k, origin)
        machine(g, o, k, f % NF, pk, working=True, ports=ports_for("N", output=False))
        d = ImageDraw.Draw(g)
        d.text((6, 4), f"f{f:02d}" + (f"  press {pk}" if pk else ""), font=font(11), fill=(240, 230, 210))
        frames.append(g.convert("RGB"))
    pal = frames[30].quantize(colors=255)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=70, loop=0, optimize=True)
    return os.path.getsize(path)


# ===================================================================== run
os.makedirs(HERE, exist_ok=True)
M = measures()
checks = META["checks"]
sys.path.insert(0, os.path.join(REPO, "concept", "ballast-drill", "model"))
import measure_ports  # noqa: E402
ports_out = os.path.join(RUN, "ports-vs-am3.png")
PORTS = measure_ports.main(os.path.join(SHEETS, "ports"), ports_out)
plate1 = os.path.join(RENDERS, "idle.png")
ref_stem = f"{ENT}/oil-refinery/north/oil-refinery-north"
chem_stem = f"{ENT}/chemical-plant/chemical-plant-north-base"
os.makedirs(os.path.join(RUN, "x1"), exist_ok=True)
vref = os.path.join(RUN, "x1", "oil-refinery-north.png")
vanilla(ref_stem)[0].save(vref)
vchem = os.path.join(RUN, "x1", "chemical-plant-north-base.png")
vanilla(chem_stem)[0].save(vchem)
still1 = os.path.join(RENDERS, "still.png")
FIN = [(lbl, tool("finish.py", p), tool("tonal.py", p)) for lbl, p in (
    ("vanilla oil refinery (north)", vref), ("vanilla chemical plant (north base)", vchem),
    ("the model: base.png (the moving parts cut out)", plate1), ("the model as seen: the still (frame 0, idle)", still1))]

layers = []
for name in ("base", "shadow", "legs-glow", "status-lamp", "legs", "drive") + COUPLINGS + ("press",) + GAUGES + ("drip",):
    m = META[name]
    w, h = m["size"]
    sx, sy = m["shift"]
    full = SH[name].size
    x0, y0 = 208 + sx * PPT - w / 2, 240 + sy * PPT - h / 2
    layers.append((name, m.get("frames", 1), m.get("line_length", 1), w, h, full, (sx, sy),
                   (round(x0), round(y0), round(x0 + w), round(y0 + h)), M["moving_per_layer"].get(name)))
for f_ in "NESW":
    for kind in ("port", "cover"):
        pm = PMETA[f"{kind}-{f_}"]
        layers.append((f"ports/{kind}-{f_}", 1, 1, pm["size"][0], pm["size"][1], tuple(pm["size"]),
                       tuple(pm["shift"]), None, None))

LAYER_NOTES = {
    "base": "the plate: the machine without the animation's moving parts, the legs unlit",
    "shadow": "draw_as_shadow; the whole machine at frame 0",
    "legs-glow": "working_visualisation, draw_as_light (or draw_as_glow): lit minus the plate",
    "status-lamp": "working_visualisation, apply_tint status, always_draw: the two lenses, white",
    "legs": "working_visualisation (only while crafting), over the plate's dark legs: 24 f",
    "drive": "animation layer: the agitator drive, 24 f",
    "coupling-dosing": "animation layer: the dosing pump's coupling (west), 24 f",
    "coupling-pump": "animation layer: the pump house's pump coupling (south-east), 24 f",
    "press": "animation layer: the filter press, 16 f, once a craft (frame_sequence)",
    "gauge-reactor-upper": "animation layer: the reactor's upper double dial's needle, 24 f",
    "gauge-reactor-lower": "animation layer: the reactor's lower double dial's needle (by the ladder), 24 f",
    "gauge-scrubber": "animation layer: the scrubber's double dial's needle, 24 f",
    "drip": "animation layer: the condenser's beads and drops, 24 f",
}

press_fps = 14
craft_ticks = 20 * 60
# the press: 16 unique frames shown two ticks of the sequence each (7 sequence frames a
# second -> 14 fps on screen), then frame 1 held for the rest of the craft
seq_speed = 7 / 60
seq_len = round(craft_ticks * seq_speed)
seq = [i for i in range(1, PRESS_NF + 1) for _ in (0, 1)] + [1] * (seq_len - 2 * PRESS_NF)
land_seq = [i + 1 for i, v in enumerate(seq) if v == 11]

lines = [
    "Reaction plant, the Circulator (5x5): the full model -- concept/reaction-plant/model/circulator.py",
    f"rendered by tools/blender/render.sh --ports --icon on the GPU; packed by pack.py; sun {MODEL.get('sun', '9.1')}",
    "",
    "PACK CHECKS (pack.py, meta.json 'checks')",
]
for k_, v in checks.items():
    lines.append(f"  {k_}: {v}")
lines += [f"  cut past +-2.5 tiles (cut_to_footprint): " +
          (", ".join(f"{k_} {v} px" for k_, v in MODEL["cut"].items() if v) or "0 px in every render"), ""]
lines += ["FINISH AND TONE (finish.py; tonal.py) -- vanilla: black 5-12 %, ratio ~0.5, darkchr 7-15; "
          "p50 41-63 (the mod ~75-81), p95 143-189"]
for lbl, fin, ton in FIN:
    lines.append(f"  {lbl:44s} {fin}")
    lines.append(f"  {'':44s} {ton}")
lines += ["", "OUTLINE (the plate, alpha over 128) -- spec gate 1: as round 5 (86.8 %; NW 100, NE 97, SW 1, SE 4 %; "
          "0.78 tile)",
          f"  footprint covered {M['cover'] * 100:.1f} %; corners NW {M['corners']['NW'] * 100:.0f} %, "
          f"NE {M['corners']['NE'] * 100:.0f} %, SW {M['corners']['SW'] * 100:.0f} %, SE {M['corners']['SE'] * 100:.0f} %",
          f"  rises {M['rise']:.2f} tile above the north edge (refinery 0.97); over the north port tiles -1, 0, +1: "
          + ", ".join(f"{M['rise_ports'][t]:.2f}" for t in (-1, 0, 1)) + " (assembler 3's north picture 0.0-0.31)",
          f"  mass {M['bbox'][0]:.2f} wide x {M['bbox'][1]:.2f} tall tiles", "",
          "BLUE (spec 3.3: the legs only)",
          f"  lit blue / opaque, working frame 0: {M['blue_share'] * 100:.1f} % (round 5 3.2 %; chemical plant 3.2 %)",
          f"  lit blue's box, tiles from the centre (x0, y0, x1, y1 down the screen): " +
          (", ".join(f"{v:+.2f}" for v in M["blue_bbox_tiles"]) if M["blue_bbox_tiles"] else "none") +
          "  -- more than a tile from every edge (spec 8.5)",
          "  blue-hued px outside the legs' own footprint, in the plate and every frame of every other layer: " +
          (", ".join(f"{k_} {v}" for k_, v in M["blue_outside_legs"].items()) or "0"),
          f"  glow: {M['glow_px']} px, mean colour {M['glow_mean']}", "",
          "MOTION",
          f"  moving / opaque, every frame of every motion against frame 0: {M['moving_share'] * 100:.1f} % "
          "(chemical plant 5.2 %, refinery 15.9 %; the previews 8.5 %)",
          "  per layer: " + ", ".join(f"{k_} {v * 100:.1f} %" for k_, v in M["moving_per_layer"].items()), "",
          "PORTS against assembler 3's outline (concept/ballast-drill/model/measure_ports.py; far_px 1 or less)"]
for f_ in "NESW":
    lines.append(f"  {f_} {PORTS[f_]}")
lines += ["", "LAYERS (sheets/; crops in px on the 416 x 480 render canvas, the origin at (208, 240))",
          f"  {'sheet':20s} {'frames':>6s} {'line':>4s} {'frame w x h':>12s} {'sheet w x h':>12s} "
          f"{'shift (tiles)':>18s}  {'crop':22s} moving"]
for name, n, line, w, h, full, (sx, sy), crop, mv in layers:
    lines.append(f"  {name:20s} {n:6d} {line:4d} {f'{w} x {h}':>12s} {f'{full[0]} x {full[1]}':>12s} "
                 f"{f'{sx:+.5f}, {sy:+.5f}':>18s}  {str(crop) if crop else '':22s} "
                 f"{'' if mv is None else f'{mv * 100:.1f} %'}")
    if name in LAYER_NOTES:
        lines.append(f"  {'':20s} {LAYER_NOTES[name]}")
area_before = sum(w * h * n for _, w, h, n in BEFORE)
area_after = sum(SH[n_].width * SH[n_].height for n_ in COUPLINGS + GAUGES)
lines += ["", "THE TIGHT CROPS (2026-10-12): the couplings and gauges sheets split, one layer per part",
          "  before: " + ", ".join(f"{n_} {n * w} x {h} = {n * w * h:,} px" for n_, w, h, n in BEFORE) +
          f"; {area_before:,} px",
          "  after:  " + ", ".join(f"{n_} {SH[n_].width} x {SH[n_].height} = {SH[n_].width * SH[n_].height:,} px"
                                   for n_ in COUPLINGS + GAUGES),
          f"          {area_after:,} px: {area_after / area_before * 100:.1f} % of before "
          f"({area_before - area_after:,} px fewer)"]
lines += ["",
          "THE PRESS, PROPOSED PLAYBACK (to verify when wired: spec 6.2's two engine details)",
          f"  press layer: animation_speed {seq_speed:.5f} ({7}/60), frame_count {PRESS_NF}, frame_sequence of "
          f"{len(seq)} entries:",
          f"    each of frames 1-16 twice (the motion at {press_fps} fps), then frame 1 x {seq_len - 2 * PRESS_NF}"
          f" (shut, holding);",
          f"    {len(seq)} / {seq_speed:.5f} = {len(seq) / seq_speed:.0f} ticks = one 20 s craft at crafting speed 1; "
          "rate-locked to crafting, not phase-locked",
          f"  the cake lands on sprite frame 11 (1-based; press frame 10, 0-based) = sequence entries {land_seq} "
          "(1-based): sound_accents.frame",
          "    is 11 if it counts sprite frames, 21 if it counts the sequence -- never 1 (frame 0 fires no accent on 2.1.21)",
          f"  the 24-frame layers: animation_speed {14 / 60:.5f} (14/60, 14 fps), ~1.7 s a loop",
          "  idle_animation: the same layers at their frame 1 (the press shut, the legs dark: the plate's)",
          "  the alternative: the press as its own working_visualisation with the same frame_sequence",
          f"  verify 2.1's frame_sequence length limit against these {len(seq)} entries; if it is lower, a lower"
          "    animation_speed shortens the sequence at the cost of a slower stroke (3.5/60, each frame once: 70 entries, the stroke at 3.5 fps)"]
os.makedirs(os.path.join(HERE, "sheets"), exist_ok=True)
open(os.path.join(HERE, "measures.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))

# the sheets, for sign-off (never into graphics/)
dst = os.path.join(HERE, "sheets")
if os.path.isdir(dst):
    shutil.rmtree(dst)
shutil.copytree(SHEETS, dst)

# the pictures
WIDE = 3300
cmp1, cmp2 = compare(1), compare(2)
rot1, rot2 = rotations(1), rotations(2)
two1 = rotations_two(1)
rot_sheet = stack([heading("The four rotations at 1x: all three pictures (no recipe set)", rot1.width), rot1,
                   heading("... and the two inputs alone (sae-radiant-precipitation), working", two1.width), two1,
                   heading("The four rotations at 2x (no recipe set)", rot2.width), rot2])
rot_sheet.convert("RGB").save(os.path.join(HERE, "rotations.png"))
gif_size = gif(os.path.join(HERE, "motion-1x.gif"))

strips = []
for name in ("legs", "drive") + COUPLINGS + ("press",) + GAUGES + ("drip",):
    k_ = 4 if name in COUPLINGS + GAUGES else 2
    st = strip(name, k=k_, per_row=12)
    w_, h_ = META[name]["size"]
    strips.append(heading(f"{name}: {META[name]['frames']} frames of {w_} x {h_} ({k_}x)"
                          f" -- {LAYER_NOTES[name]}", max(st.width, 900), 15))
    strips.append(st)

summary = [
    "F, the Circulator, at 5x5: the shipping model (spec agreed 2026-10-11, 064e9ef). Round 5's model and finish with the",
    "animation set as fixed (6-all-fixed.gif). Changed from the concept: the press head clear of the receiver (its west head",
    "drawn back, its skid and the drop box shortened, the ram and handwheel over the receiver's crown); every fixed",
    "interpenetration --collide found fixed (the instrument house chamfered off the reactor; the make-up pot smaller, between",
    "the feed main and the drum's hose; the sampling cabinet clear of the settling pot and the downcomer; the exchanger clear",
    "of the scrubber; the side nozzle's flange at the pot's wall; the copper line round the pot; the receiver clear of the",
    "pump house; the dosing hose off the pump's motor); the corner vessels drawn in to the footprint's edge and every colour",
    "render cut at +-2.5; the south pipe picture in dark steel; the sun 8.8 -> 9.1. The moving parts stand unseen in the",
    "plate's scene at frame 0, so their shadows are the plate's and every layer's frame 0 lands on the still. Nothing is in graphics/.",
    "2026-10-12, tight crops: the couplings and gauges sheets are now six layers, one per coupling and per double dial, each",
    f"cropped round its own moving part ({area_before:,} px of sheet before, {area_after:,} after); every motion as it was.",
]
parts = [heading("REACTION PLANT -- the Circulator, full model: review", WIDE, 26), para(summary, WIDE),
         heading("The plate beside the oil refinery, the chemical plant and round 5's F, 1x (64 px a tile), frame 0", WIDE),
         cmp1, heading("... and at 2x", WIDE), cmp2,
         heading("Idle and working, 2x, as the engine draws the sheets (the shadow, the plate, every layer, the lamps, "
                 "the pictures and vanilla's covers)", WIDE), states(2),
         heading("Every layer's frames, drawn over the plate, cropped to the layer", WIDE)] + strips + [
         heading("The rotations at 1x (rotations.png has 2x)", WIDE), rot1,
         heading("The icon (spec 14: the lead reactor and its two lit legs)", WIDE), icon_panel(),
         heading("Measures (measures.txt)", WIDE), para(lines, WIDE, 12)]
sheet_ = stack(parts)
sheet_.convert("RGB").save(os.path.join(HERE, "review.png"))
# its top section, for sending (under 8000 px tall): the title through every layer's frames
top = stack(parts[:parts.index(rot1) - 1])
assert top.height < 8000, top.size
top.convert("RGB").save(os.path.join(HERE, "review-top.png"))
print("review top", os.path.join(HERE, "review-top.png"), top.size)
print("review", os.path.join(HERE, "review.png"), sheet_.size)
print("rotations", os.path.join(HERE, "rotations.png"), rot_sheet.size)
print("gif", os.path.join(HERE, "motion-1x.gif"), f"{gif_size / 1e6:.2f} MB")
print("ports vs am3", ports_out)
