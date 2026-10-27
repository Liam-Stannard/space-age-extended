#!/usr/bin/env python3
"""Radiant Generator, round 5, suggestions 1-5: sheets, GIFs, measures, contact sheet A.

  python3 r5a_sheets.py <full-dir> <cmap-dir> <out-dir> [--factorio <data>] [--rp-gif <gif>]
                        [--turbine <graphics/entity/crust-turbine>] [--only 1,2,...]

<full-dir>/<n>/ is r5a_<n>_*.py's output (idle.png, plate.png, working-NN.png at 4x,
meta.json with the labelled chain); <cmap-dir>/<n>/ its --colourmap run (colourmap.png at
2x, colourmap.json). Writes into <out-dir>:

  <n>-<slug>.png        the sheet: working and idle at 2x on the ground with the footprint,
                        the chain numbered on the working plate and listed, the motion map,
                        the colour map and palette, key frames, 1x working and idle, the
                        pitch, the animation plan, the Reactor headroom, the finish, measures
  <n>-<slug>-1x.gif     the working loop at game scale on the ground (kept under 5 MB)
  <n>-<slug>-2x.gif     the same at 2x (out of git, as rounds 2-4's)
  contact-sheet-a.png   the five working at game scale beside vanilla's steam engine, steam
                        turbine and fusion generator (working), the Reaction Plant's round 5
                        and the Siderane turbine, all at 64 px a tile on one ground
  measures-a.json       cover, rise, blue share, moving share, per suggestion
"""
import argparse
import json
import os
import re

from PIL import Image, ImageChops, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("full")
ap.add_argument("cmap")
ap.add_argument("out")
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
ap.add_argument("--rp-gif", default=os.path.expanduser(
    "~/git/space-age-extended/.claude/worktrees/reaction-plant-redesign/concept/reaction-plant/options/round-5/"
    "F-the-circulator-r5-working.gif"))
ap.add_argument("--turbine", default=os.path.expanduser(
    "~/git/space-age-extended/.claude/worktrees/master-merge/graphics/entity/crust-turbine"))
ap.add_argument("--only", default="1,2,3,4,5")
args = ap.parse_args()
FULL, CMAP, OUT, FD = args.full, args.cmap, args.out, args.factorio
os.makedirs(OUT, exist_ok=True)

PPT = 64
CANVAS, ORIGIN = (512, 448), (208, 272)
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)
GIF_MS = 70


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def load(path, k):
    """A 4x render brought to k x game scale, premultiplied, faint catcher fog cut."""
    im = Image.open(path).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    src = im.width // CANVAS[0]
    im = im.convert("RGBa").resize((CANVAS[0] * k, CANVAS[1] * k), Image.LANCZOS)
    return im.convert("RGBA")


def ground(size, origin, ppt, foot):
    """The game's ground with the tile grid and the footprint outlined."""
    g = Image.new("RGBA", size, GROUND)
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ox, oy = origin
    fw, fh = foot
    offx = 0.5 if fw % 2 else 0.0
    offy = 0.5 if fh % 2 else 0.0
    for i in range(-24, 25):
        x = ox + (i + offx) * ppt
        y = oy + (i + offy) * ppt
        d.line([(x, 0), (x, size[1])], fill=(255, 255, 255, 22))
        d.line([(0, y), (size[0], y)], fill=(255, 255, 255, 22))
    d.rectangle([ox - fw * ppt / 2, oy - fh * ppt / 2, ox + fw * ppt / 2, oy + fh * ppt / 2],
                outline=(255, 255, 255, 110))
    g.alpha_composite(ov)
    return g


def on_ground(im, k, foot):
    g = ground(im.size, (ORIGIN[0] * k, ORIGIN[1] * k), PPT * k, foot)
    g.alpha_composite(im)
    return g


def text(d, xy, s, size=13, fill=TEXT, bold=False):
    d.text(xy, s, font=font(size, bold), fill=fill)


def wrap(s, size, width):
    f = font(size)
    out, line = [], ""
    for w in s.split(" "):
        t = (line + " " + w).strip()
        if f.getlength(t) > width and line:
            out.append(line)
            line = w
        else:
            line = t
    if line:
        out.append(line)
    return out


def block(title, paras, width, size=13, tight=False):
    lines = []
    for p in paras:
        lines += wrap(p, size, width - 20) + ([] if tight else [""])
    h = 30 + len(lines) * (size + 5)
    im = Image.new("RGBA", (width, h), BG)
    d = ImageDraw.Draw(im)
    text(d, (10, 6), title, 15, HEAD, bold=True)
    y = 30
    for ln in lines:
        text(d, (14, y), ln, size)
        y += size + 5
    return im


def captioned(im, cap, size=13):
    lines = cap.split("\n")
    w = max([im.width] + [int(font(size, True).getlength(ln)) + 10 for ln in lines])
    hh = 6 + (size + 6) * len(lines)
    c = Image.new("RGBA", (w, im.height + hh), BG)
    d = ImageDraw.Draw(c)
    for i, ln in enumerate(lines):
        text(d, (4, 4 + (size + 6) * i), ln, size, HEAD if i == 0 else SUB, bold=(i == 0))
    c.alpha_composite(im, (0, hh))
    return c


def hrow(ims, gap=12):
    w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    h = max(i.height for i in ims)
    r = Image.new("RGBA", (w, h), BG)
    x = 0
    for i in ims:
        r.alpha_composite(i, (x, 0))
        x += i.width + gap
    return r


def vstack(ims, gap=12, width=None):
    w = width or max(i.width for i in ims)
    h = sum(i.height for i in ims) + gap * (len(ims) - 1)
    r = Image.new("RGBA", (w, h), BG)
    y = 0
    for i in ims:
        r.alpha_composite(i, (0, y))
        y += i.height + gap
    return r


def bbox_of(ims, k, pad=10):
    box = None
    for im in ims:
        b = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    p = pad * k
    return (max(0, box[0] - p), max(0, box[1] - p), min(CANVAS[0] * k, box[2] + p), min(CANVAS[1] * k, box[3] + p))


def blue_mask(im):
    """255 where a pixel is the isotope's blue: B > 110, B > R + 45, B > G + 10."""
    r, g, b = im.convert("RGB").split()
    m1 = b.point(lambda v: 255 if v > 110 else 0)
    m2 = ImageChops.subtract(b, r).point(lambda v: 255 if v > 45 else 0)
    m3 = ImageChops.subtract(b, g).point(lambda v: 255 if v > 10 else 0)
    return ImageChops.multiply(ImageChops.multiply(m1, m2), m3)


def count(mask, within):
    return ImageChops.multiply(mask, within).histogram()[255]


# ---------------------------------------------------------------- the suggestions' words
S = {
    1: dict(slug="the-thermopile-stack", name="THE THERMOPILE STACK", foot=(4, 4),
            why="4 x 4: a core, three stacks and a converter want a square; 10 MW on 16 tiles leaves the 40 MW "
                "Reactor room to be a 6 x 6 or 7 x 7 hall. A block of them tiles in rows with the radiators "
                "back to back on the north edge, the converters and trunks facing the aisle.",
            read="A squat lead hot-core clamped between three tall stacks of ceramic-and-copper plates, the "
                 "isotope's blue in hairlines between the plates; radiator panels behind it, a red rotary "
                 "converter in front. It reads as heat into a battery of plates: a generator with no engine.",
            anim=["24 frames, one loop, all in `animation` (draw_as_glow for the light); `idle_animation` is "
                  "frame 0 unlit.",
                  "Indexing plug: half a turn a loop, still for half of it then an eased turn (two pockets: the "
                  "two fuel slots).",
                  "Rotary converter: the commutator, its brush ring and the shaft coupling, two turns a loop; "
                  "the pump couplings two turns.",
                  "Glow: the stacks' plate gaps breathe +-20 % with a rising flow; the core's two sight slots "
                  "+-15 %; status lamp green; gauge needles swing.",
                  "Idle: everything still and dark. Scales with perceived_performance: animation speed (the "
                  "converter) and the glow's alpha."],
            headroom="Stage 1 turns heat straight into DC with no prime mover: thermopiles are the low-efficiency "
                     "answer, and they need a rotary converter to make AC. The Reactor gets what this one lacks: "
                     "a real turbine hall, a coolant loop it shares with its neighbours (the bonus, visible as "
                     "headers joining across the gap), bigger cores, and its blue in an open core rather than "
                     "hairlines.",
            finish="Lead hot-core with its bloom and banded collars (the isotope's holder); the signature is the "
                   "striped stack, cream ceramic and copper plates on bare tie rods; oxide-red converter, weathered "
                   "green pump motors, grey radiators with copper serpentines, cream expansion tank, dark-steel "
                   "skids, ochre ladder; worn paint chipped at edges, rust in seams and at the foot, oil at the "
                   "pumps and the converter."),
    2: dict(slug="the-brayton-loop", name="THE BRAYTON LOOP", foot=(4, 4),
            why="4 x 4: the cask, the machine train and the radiator wing are three masses that pack into a "
                "square; the wing's tilt rises 0.5 tile over the north edge. Tiles in rows with the wings to the "
                "north, the trains along the south aisle, the switchgear and trunks at the east.",
            read="A lead cask feeding a fat lagged duct down into a machine train on a skid (compressor, a cream "
                 "turbine scroll, an open alternator frame whose red-and-copper rotor rolls in plain sight) under "
                 "a tilted teal radiator wing. Not the Siderane turbine: no barrel, no bladed face; a train of "
                 "separate machines, the motion a side-on drum of poles.",
            anim=["24 frames, one loop.",
                  "Alternator rotor: one turn a loop, four poles alternating red and copper so it reads at 1x as "
                  "a rolling drum; the exciter's slip rings two turns; the turbine coupling two turns.",
                  "Glow: the cask's three sight slots breathe +-18 % (draw_as_glow); status lamp; gauge needles.",
                  "The charging ports do not move (a cell every 50 s is not a loop).",
                  "Idle: all still, the slots dark. Scales with perceived_performance: rotor speed and glow."],
            headroom="One cask, one small turbine, one radiator wing: the wing is the limit at 10 MW. The Reactor "
                     "is the same loop grown up: several casks on a common hot header, a big turbine-alternator "
                     "set, and radiator wings that join between neighbours.",
            finish="Lead cask with bands and bloom; cream turbine scroll, grey compressor and recuperator, an ochre "
                   "alternator frame with red and copper poles, teal radiator panels (the family's roof paint) "
                   "with copper tubes on dark steel, lagging canvas with steel straps and coloured marking rings, "
                   "green and grey gas bottles, grey switchgear."),
    3: dict(slug="the-carousel-collector", name="THE CAROUSEL COLLECTOR", foot=(5, 5),
            why="5 x 5: the turntable is the show and the magazine holds a visible reserve of eight cells; at the "
                "limit Liam set, so the Reactor must be 6 x 6 or bigger. Tiles in rows with the hoppers on the "
                "west (one belt between two rows) and the trunks on the east.",
            read="A great lead turntable of eight capped pockets on a ring gear; an oxide-red collector head "
                 "bridges the south pocket with a blue window; the drive motor sits at the gear. It reads as a "
                 "magazine being read, cell by cell.",
            anim=["24 frames, one loop.",
                  "Turntable: an eighth of a turn a loop, still for 55 % then an eased move; the deck, the caps, "
                  "the rim's hazard marks and 64 gear teeth all move. Pinion two turns and motor coupling three "
                  "turns, in the move only.",
                  "Glow: the collector window is full while a cell sits under the head and dims to 25 % as the "
                  "table moves (draw_as_glow); the head's gauge follows it; status lamp.",
                  "Idle: still, the window dark. Scales with perceived_performance: the index rate and glow."],
            headroom="One head reads one cell at a time: direct collection at stage 1 is a trickle per cell. The "
                     "Reactor is a ring of heads round a bigger table (every pocket read at once), or tables "
                     "set edge to edge sharing heads with their neighbours.",
            finish="Lead deck, caps and hub dome (the signature: the ring of capped pockets), dark-steel ring gear "
                   "and base, oxide-red collector hood with grey fins, green capacitor cans, a grey finned "
                   "transformer, ochre ladder, hazard marks on the rim, lead hopper and spent bin."),
    4: dict(slug="the-thermionic-gantry", name="THE THERMIONIC GANTRY", foot=(5, 3),
            why="5 x 3, long east-west: the crucible and the crane's travel want a length. 10 MW on 15 tiles. "
                "Placed end to end, the rails run on as one crane bay; side by side, the trunks meet in the "
                "aisle.",
            read="An ochre overhead crane over a long lead crucible, two rows of glass converter tubes along its "
                 "flanks, each with a finned copper cap and its blue low in the glass. It reads as a foundry for "
                 "light: a crane feeding a trough.",
            anim=["32 frames, one loop (the crane is the longest move of the five).",
                  "Gantry: hold at the magazine, hoist up, run 2.2 tiles west, lower into the well, release (the "
                  "cell is gone), raise, run back, lower. The bridge, the trolley, the hook block and the cables "
                  "all move.",
                  "Glow: each tube's emitter brightens in a chase along the rows, twice a loop; the served well's "
                  "mouth glows while its lid is off; status lamp; gauges.",
                  "Idle: crane parked at the magazine, hook down, tubes and well dark. Scales with "
                  "perceived_performance: the crane's pace and the tubes' glow."],
            headroom="Thermionic tubes are the low-efficiency stage-1 converter, and one crane feeds one crucible. "
                     "The Reactor is the crane hall: the bridge spans several crucibles, the tubes become cassette "
                     "banks, and neighbours share the rails (the bonus visible as continuous track).",
            finish="Ochre crane (vanilla's yellow, worn), lead crucible and magazine, clear glass tubes, copper "
                   "caps, fins and bus, green finned transformer, grey inverter, cream caesium reservoir, dark "
                   "steel posts' feet, hazard bands on the bridge."),
    5: dict(slug="the-chopper-wheel", name="THE CHOPPER WHEEL", foot=(3, 3),
            why="3 x 3: one cask, one wheel; the densest at 10 MW (1.1 MW a tile), and the smallest step on the "
                "ladder. Tiles in a dense grid, wheels all facing south, the trunks on the east.",
            read="A squat lead cask with one bolted window and a copper-sectored wheel turning across it, the blue "
                 "flickering through its slots; a finned red transformer beside. It reads as a machine that cuts "
                 "light into current. (Replaces the heat-pipe spider: the spider's pods need one of the other "
                 "conversions, so it repeats 1 or 2; the chopper's moving part is the conversion.)",
            anim=["24 frames, one loop.",
                  "Wheel: three-eighths of a turn a loop (eight sectors: three slots cross the window, so the "
                  "flicker is the generator's frequency); the drive coupling three turns.",
                  "Glow: the window behind the wheel, a slow swirl +-10 % (draw_as_glow); the wheel masks it, so "
                  "the flicker is in the base layer's frames; status lamp; gauges.",
                  "Idle: wheel still, the window dark. Scales with perceived_performance: wheel speed."],
            headroom="One window and one wheel per cask: the stage-1 trick is cheap and small. The Reactor puts "
                     "many windows round one big core, a wheel at each, and gears its wheels to its neighbours' "
                     "(the bonus visible as a shared drive shaft across the gap).",
            finish="Lead cask with bands and bloom (the signature: the window and its wheel), copper sectors on a "
                   "lead rim, dark-steel guard with a hazard band, weathered green motor, oxide-red finned "
                   "transformer with ceramic bushings' stubs, lead spent-cell drawer, ochre ladder."),
}


def chain_lines(meta):
    return [f"{L['n']}. {L['text']}" for L in sorted(meta["labels"], key=lambda L: L["n"])]


def measure(n, plate, work0, frames1, foot):
    """Cover (plate alpha > 128 inside the footprint), rise over the north edge, blue share
    of the working plate, moving share across the loop; all at 1x."""
    fw, fh = foot
    x0, y0 = ORIGIN[0] - fw * 32, ORIGIN[1] - fh * 32
    a = plate.getchannel("A")
    opq = a.point(lambda v: 255 if v > 128 else 0)
    inside = a.crop((int(x0), int(y0), int(x0 + fw * 64), int(y0 + fh * 64))).point(lambda v: 255 if v > 128 else 0)
    cover = inside.histogram()[255] / (fw * fh * 64 * 64)
    bb = a.point(lambda v: 255 if v > 128 else 0).getbbox()
    rise = (y0 - bb[1]) / 64
    n_op = opq.histogram()[255]
    blue = count(blue_mask(work0), opq) / n_op
    f0 = frames1[0].convert("RGB")
    diff = None
    for f in frames1[1:]:
        dd = ImageChops.difference(f0, f.convert("RGB")).convert("L").point(lambda v: 255 if v > 30 else 0)
        diff = dd if diff is None else ImageChops.lighter(diff, dd)
    moving = count(diff, opq) / n_op
    return dict(cover_pct=round(100 * cover, 1), rise_tiles=round(rise, 2), blue_pct=round(100 * blue, 1),
                changing_pct=round(100 * moving, 1), footprint=f"{fw} x {fh}",
                mw_per_tile=round(10 / (fw * fh), 2))


def motion_map(idle2, frames2):
    """Idle at 2x, dimmed; pixels that change over the loop in magenta (moving metal) and
    cyan (the light)."""
    base = idle2.convert("RGB")
    f0 = frames2[0].convert("RGB")
    move = None
    light = None
    for f in frames2:
        fr = f.convert("RGB")
        dd = ImageChops.difference(f0, fr).convert("L").point(lambda v: 255 if v > 30 else 0)
        move = dd if move is None else ImageChops.lighter(move, dd)
        bl = blue_mask(fr)
        light = bl if light is None else ImageChops.lighter(light, bl)
    out = Image.blend(base, Image.new("RGB", base.size, (40, 36, 32)), 0.55)
    out.paste((230, 40, 200), mask=move)
    out.paste((60, 220, 255), mask=light)
    o = out.convert("RGBA")
    o.putalpha(idle2.getchannel("A"))
    return o


def numbered(im2, meta):
    d = ImageDraw.Draw(im2)
    for L in meta["labels"]:
        x, y = L["px"][0] * 2, L["px"][1] * 2
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(240, 200, 120), outline=(20, 18, 16), width=2)
        s = str(L["n"])
        w = font(15, True).getlength(s)
        d.text((x - w / 2, y - 9), s, font=font(15, True), fill=(20, 18, 16))
    return im2


def palette(cm_json, used, width):
    groups = json.load(open(cm_json))
    items = [(g, h) for g, h in groups.items() if g in used]
    im = Image.new("RGBA", (width, 22 * ((len(items) + 1) // 2) + 8), BG)
    d = ImageDraw.Draw(im)
    for i, (g, h) in enumerate(items):
        x = 8 + (i % 2) * (width // 2)
        y = 4 + 22 * (i // 2)
        d.rectangle([x, y, x + 16, y + 16], fill=h, outline=(0, 0, 0))
        text(d, (x + 24, y), g, 12)
    return im


def used_groups(cmap_png, cm_json):
    groups = json.load(open(cm_json))
    im = Image.open(cmap_png).convert("RGBA")
    cols = {c[1][:3] for c in im.getcolors(1 << 20) if c[1][3] > 200}
    out = set()
    for g, h in groups.items():
        rgb = tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        if any(max(abs(rgb[j] - c[j]) for j in range(3)) <= 6 for c in cols):
            out.add(g)
    return out


def gif(frames, path):
    strip = Image.new("RGB", (frames[0].width, frames[0].height * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f.convert("RGB"), (0, i * f.height))
    pal = strip.quantize(colors=256)
    q = [f.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=GIF_MS, loop=0, optimize=True)
    return os.path.getsize(path) / 1e6


MEAS = {}
FIRST = {}


def build(n):
    o = S[n]
    d = os.path.join(FULL, str(n))
    meta = json.load(open(os.path.join(d, "meta.json")))
    nf = meta["frames"]
    foot = tuple(meta["footprint"])
    work2 = [load(os.path.join(d, f"working-{f:02d}.png"), 2) for f in range(nf)]
    work1 = [load(os.path.join(d, f"working-{f:02d}.png"), 1) for f in range(nf)]
    idle2 = load(os.path.join(d, "idle.png"), 2)
    idle1 = load(os.path.join(d, "idle.png"), 1)
    plate1 = load(os.path.join(d, "plate.png"), 1)
    plate2 = load(os.path.join(d, "plate.png"), 2)
    m = measure(n, plate1, work1[0], work1, foot)
    MEAS[n] = m
    bb1 = bbox_of([idle1] + work1[::4], 1, pad=14)
    bb2 = tuple(2 * v for v in bb1)
    g_w2 = [on_ground(f, 2, foot).crop(bb2) for f in work2]
    g_i2 = on_ground(idle2, 2, foot).crop(bb2)
    g_w1 = [on_ground(f, 1, foot).crop(bb1) for f in work1]
    g_i1 = on_ground(idle1, 1, foot).crop(bb1)
    FIRST[n] = (g_w1[0], meta, foot, m)
    # GIFs
    s1 = gif(g_w1, os.path.join(OUT, f"{n}-{o['slug']}-1x.gif"))
    s2 = gif(g_w2, os.path.join(OUT, f"{n}-{o['slug']}-2x.gif"))
    m["gif_1x_mb"], m["gif_2x_mb"] = round(s1, 2), round(s2, 2)
    # panels
    chain = numbered(g_w2[0].copy(), dict(labels=[dict(L, px=[L["px"][0] - bb1[0], L["px"][1] - bb1[1]])
                                                   for L in meta["labels"]]))
    mm = motion_map(plate2.crop(bb2), [w.crop(bb2) for w in work2])
    mmg = ground(mm.size, ((ORIGIN[0] - bb1[0]) * 2, (ORIGIN[1] - bb1[1]) * 2), 128, foot)
    mmg.alpha_composite(mm)
    cm = Image.open(os.path.join(CMAP, str(n), "colourmap.png")).convert("RGBA")
    cmg = ground(cm.size, (ORIGIN[0] * 2, ORIGIN[1] * 2), 128, foot)
    cmg.alpha_composite(cm)
    cmg = cmg.crop(bb2)
    used = used_groups(os.path.join(CMAP, str(n), "colourmap.png"), os.path.join(CMAP, str(n), "colourmap.json"))
    kf = [int(i * nf / 4) for i in range(4)]
    keys = [g_w1[i] for i in kf]
    r1 = hrow([captioned(g_w2[0], "WORKING, 2x (frame 0)"), captioned(g_i2, "IDLE, 2x (stopped, unlit)")])
    r1b = hrow([captioned(g_w1[0], "WORKING, 1x"), captioned(g_i1, "IDLE, 1x")])
    r2 = hrow([captioned(chain, "THE CHAIN, CELL TO WIRE (numbered, 2x)"),
               captioned(mmg, "MOTION MAP: magenta moves, cyan is the isotope's light")])
    W = max(r1.width, r2.width) + 20
    chain_blk = block("CELL TO WIRE (the numbers on the plate above)", chain_lines(meta), W, tight=True)
    r3 = hrow([captioned(cmg, "COLOUR MAP (each part in its palette group's key colour), 2x"),
               vstack([captioned(palette(os.path.join(CMAP, str(n), "colourmap.json"), used, 520),
                                 "PALETTE"), r1b])])
    r4 = captioned(hrow(keys, 6), f"KEY FRAMES, 1x: frames {', '.join(map(str, kf))} of {nf}")
    sub = wrap("A generator, not a reactor: 10 MW, a cell every 50 s, a spent cell out. Lit Blender concept on "
               "the GPU in the Reaction Plant round 5's finish (worn_paint, the per-part palette, the lead bloom). "
               "Not adopted; nothing in graphics/.", 13, W - 20)
    head = Image.new("RGBA", (W, 44 + 18 * len(sub)), BG)
    dd = ImageDraw.Draw(head)
    text(dd, (10, 6), f"RADIANT GENERATOR, ROUND 5 -- {n}. {o['name']}  ({foot[0]} x {foot[1]})", 22, HEAD, True)
    for i, ln in enumerate(sub):
        text(dd, (10, 40 + 18 * i), ln, 13, SUB)
    meas = (f"Footprint {m['footprint']} ({m['mw_per_tile']} MW a tile). Cover {m['cover_pct']} % of the footprint "
            f"(plate alpha > 128). Rise over the north edge {m['rise_tiles']:+.2f} tile. Blue (the isotope's light, "
            f"lit) {m['blue_pct']} % of the opaque plate. Pixels that change over the loop {m['changing_pct']} %. "
            f"GIF 1x {m['gif_1x_mb']} MB.")
    blocks = [
        block("PITCH", ["READ: " + o["read"], "FOOTPRINT: " + o["why"]], W),
        chain_blk,
        block("ANIMATION PLAN (for spec 6.2)", o["anim"], W),
        block("REACTOR HEADROOM (stage 1 of 4)", [o["headroom"]], W),
        block("FINISH", [o["finish"]], W),
        block("MEASURED (64 px a tile)", [meas], W),
    ]
    sheet = vstack([head, r1, r2] + blocks[:2] + [r3, r4] + blocks[2:], width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    path = os.path.join(OUT, f"{n}-{o['slug']}.png")
    pad.convert("RGB").save(path)
    print(path, pad.size, m)


# ---------------------------------------------------------------- references at game scale
def lua_shift(path):
    t = open(path).read()
    return tuple(float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", t).groups())


def ref_canvas(w_t, h_t, layers, foot, glow=()):
    """Compose sprites on a ground of w_t x h_t tiles centred on the entity; layers are
    (image, shift px at 64 px a tile, mode)."""
    W, H = int(w_t * 64), int(h_t * 64)
    c = ground((W, H), (W // 2, H // 2), 64, foot)
    for im, (sx, sy), mode in layers:
        x = round(W / 2 + sx - im.width / 2)
        y = round(H / 2 + sy - im.height / 2)
        if mode == "shadow":
            sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
            sh.putalpha(im.getchannel("A").point(lambda v: int(v * 0.5)))
            c.alpha_composite(sh, (x, y))
        elif mode == "add":
            rgb = Image.new("RGB", c.size, (0, 0, 0))
            rgb.paste(im.convert("RGB"), (x, y), im.getchannel("A"))
            c = Image.merge("RGBA", (*ImageChops.add(c.convert("RGB"), rgb).split(), c.getchannel("A")))
        else:
            c.alpha_composite(im, (x, y))
    return c


def frame(path, w, h, i=0, line=1):
    im = Image.open(path).convert("RGBA")
    return im.crop(((i % line) * w, (i // line) * h, (i % line) * w + w, (i // line) * h + h))


def references():
    B, SA = f"{FD}/base/graphics/entity", f"{FD}/space-age/graphics/entity"
    out = []
    se = frame(f"{B}/steam-engine/steam-engine-H.png", 352, 257, 0, 8)
    ses = frame(f"{B}/steam-engine/steam-engine-H-shadow.png", 508, 160, 0, 8)
    out.append(("vanilla steam engine 5x3 (0.9 MW)",
                ref_canvas(8, 5, [(ses, (96, 48), "shadow"), (se, (2, -9.5), "n")], (5, 3))))
    st = frame(f"{B}/steam-turbine/steam-turbine-H.png", 320, 245, 0, 4)
    sts = frame(f"{B}/steam-turbine/steam-turbine-H-shadow.png", 435, 150, 0, 1)
    out.append(("vanilla steam turbine 5x3 (5.8 MW)",
                ref_canvas(8, 5, [(sts, (57, 36), "shadow"), (st, (0, -5.5), "n")], (5, 3))))
    G = f"{SA}/fusion-generator/north/fusion-generator-north"
    fg = frame(G + ".png", 244, 376, 0, 3)
    fgs = Image.open(G + "-shadow.png").convert("RGBA")
    fgg = frame(G + "-glow.png", 202, 336, 0, 3)
    out.append(("fusion generator 3x5, working (50 MW)",
                ref_canvas(6, 7, [(fgs, (25, 8), "shadow"), (fg, (-4, -4), "n"), (fgg, (0, -8), "add")], (3, 5))))
    rp = Image.open(args.rp_gif).convert("RGBA").crop((908, 0, 908 + 448, 434))
    out.append(("Reaction Plant round 5, 5x5 (its GIF, frame 0)", rp))
    T = args.turbine
    tb = Image.open(f"{T}/base-horizontal.png").convert("RGBA")
    tbs = Image.open(f"{T}/base-shadow-horizontal.png").convert("RGBA")
    tr = frame(f"{T}/rotor-horizontal.png", 58, 55, 0, 8)
    out.append(("Siderane turbine 5x3 (its sheets, 1.8 MW)",
                ref_canvas(8, 5, [(tbs, (25, 10), "shadow"), (tb, (0, -3.5), "n"), (tr, (-1, -20.5), "n")], (5, 3))))
    return out


def contact():
    refs = references()
    row_r = hrow([captioned(im, nm, 12) for nm, im in refs], 16)
    ours = []
    for n in sorted(FIRST):
        im, meta, foot, m = FIRST[n]
        ours.append(captioned(im, f"{n}. {S[n]['name'].title()}, {foot[0]}x{foot[1]}\n"
                                  f"cover {m['cover_pct']} %, rise {m['rise_tiles']:+.2f} t, "
                                  f"{m['mw_per_tile']} MW/tile", 12))
    row_o = hrow(ours, 16)
    W = max(row_r.width, row_o.width) + 20
    head = Image.new("RGBA", (W, 56), BG)
    d = ImageDraw.Draw(head)
    text(d, (10, 6), "RADIANT GENERATOR, ROUND 5 -- SUGGESTIONS 1-5 (artist A) AT GAME SCALE", 20, HEAD, True)
    text(d, (10, 32), "64 px a tile, one ground. Top: vanilla's steam engine and steam turbine (frame 0), the "
         "fusion generator working (base + glow, frame 0), the Reaction Plant's round 5 and the Siderane turbine. "
         "Below: suggestions 1-5 working, frame 0.", 12, SUB)
    sheet = vstack([head, row_r, row_o], 16, width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    pad.convert("RGB").save(os.path.join(OUT, "contact-sheet-a.png"))
    print(os.path.join(OUT, "contact-sheet-a.png"), pad.size)


for n in [int(v) for v in args.only.split(",")]:
    build(n)
json.dump(MEAS, open(os.path.join(OUT, "measures-a.json"), "w"), indent=1)
if len(FIRST) == 5:
    contact()
