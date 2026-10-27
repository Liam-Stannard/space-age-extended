#!/usr/bin/env python3
"""Vent Pump, round 4 (T03), artist A's half (concepts 1, 2, 5, 7): sheets, GIFs, measures.

Round 3's vpa3_sheets.py (../round-3/), copied, with the helium sight glass (mix A) added: a HELIUM
GLASS block (where it sits, its measures from vp4_measure.py: the helium glow's peak alone, white
and clipped px over every frame, pale cyan and frost inside the glass, the level's motion) and a
panel of the glass at game scale (1x shown x4 idle, level full and the draw; the loop at 2x). The
contact sheet of all eight is vp4_contact.py's. Round 3's words follow.

Round 3: artist A (concepts 1, 2, 5, 7): sheets, GIFs, measures, contact sheet A.

  python3 vpa3_sheets.py <full-dir> <cmap-dir> <out-dir> [--factorio <data>] [--only 1,2,5,7]

Round 2's sheets (../round-2/vpa_sheets.py) with round 3's additions: a PATH OVERLAY at 2x
(helium violet, the melt orange, spent or recovered gas teal, from the paths each model writes
into meta.json), a HELIUM AT WORK block (what helium does, and the sync) and a PLUMBING block
(every run, both its ends, and what was removed). The ports are drawn as ports.txt agrees for
all eight: vanilla's straight pipe on the tile outside each port, under the render; the model's
own flange at the edge on assembler 3's axis (z 0.42). Measures as round 2, at 1x:

  cover    plate alpha > 128 inside the 3 x 3 (the bar is 92 %), per direction
  rise     the plate's top over the footprint's north edge, tiles, per direction
  glow     orange (R > 150, R > G + 45, R > B + 90) in working frame 0 and not in the idle frame,
           of the opaque plate: the melt's light, facing north
  moving   pixels that change by > 30 over the loop, of the opaque plate; split into moving
           metal and the melt's light (orange in any frame)
  helium   the lagged line's grey-violet as lit (B > G + 8, luma 70..220) of the opaque plate
  finish   tools/blender/finish.py and tonal.py on the plate (facing north)

Writes <n>-<slug>.png (the sheet), <n>-<slug>-paths.png (the overlay alone, 2x),
<n>-<slug>-1x.gif (working, game scale, under 5 MB), <n>-<slug>-2x.gif (keep out of git),
contact-sheet-a.png (round 3 beside round 2 and the references), measures-a.json.
"""
import argparse
import math
import json
import os
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp4_measure as GM  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
ap = argparse.ArgumentParser()
ap.add_argument("full")
ap.add_argument("cmap")
ap.add_argument("out")
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
ap.add_argument("--only", default="1,2,5,7")
args = ap.parse_args()
FULL, CMAP, OUT, FD = args.full, args.cmap, args.out, args.factorio
os.makedirs(OUT, exist_ok=True)
R1 = os.path.join(REPO, "concept", "vent-pump", "model", "sheets")
ADOPTED = os.path.join(REPO, "graphics", "entity", "vent-pump")
ENT = f"{FD}/base/graphics/entity"
TOOLS = os.path.join(REPO, "tools", "blender")

PPT = 64
CANVAS, ORIGIN = (384, 384), (192, 224)
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)
GIF_MS = 66                          # 15 frames a second (round 1: animation_speed 0.25)
DIRS = ("north", "east", "south", "west")
FACE = {"north": "N", "east": "E", "south": "S", "west": "W"}
OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}
NAME = {"N": "north", "E": "east", "S": "south", "W": "west"}


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def load(path, k):
    """A 4x render brought to k x game scale, premultiplied, faint catcher fog cut."""
    im = Image.open(path).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    im = im.convert("RGBa").resize((CANVAS[0] * k, CANVAS[1] * k), Image.LANCZOS)
    return im.convert("RGBA")


def ground(size, origin, ppt, foot=(3, 3)):
    g = Image.new("RGBA", size, GROUND)
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ox, oy = origin
    fw, fh = foot
    for i in range(-24, 25):
        x = ox + (i + 0.5) * ppt
        y = oy + (i + 0.5) * ppt
        d.line([(x, 0), (x, size[1])], fill=(255, 255, 255, 22))
        d.line([(0, y), (size[0], y)], fill=(255, 255, 255, 22))
    d.rectangle([ox - fw * ppt / 2, oy - fh * ppt / 2, ox + fw * ppt / 2, oy + fh * ppt / 2],
                outline=(255, 255, 255, 110))
    g.alpha_composite(ov)
    return g


def place(canvas, im, centre, k=1, add=False):
    if k != 1:
        im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    x = round(centre[0] - im.width / 2)
    y = round(centre[1] - im.height / 2)
    if add:
        box = (x, y, x + im.width, y + im.height)
        under = canvas.crop(box)
        rgb = ImageChops.add(under.convert("RGB"), ImageChops.multiply(
            im.convert("RGB"), Image.merge("RGB", [im.getchannel("A")] * 3)))
        canvas.paste(Image.merge("RGBA", (*rgb.split(), under.getchannel("A"))), box[:2])
        return
    canvas.alpha_composite(im, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))


def pipe_sprite(face, k):
    name = "pipe-straight-vertical" if face in "NS" else "pipe-straight-horizontal"
    im = Image.open(f"{ENT}/pipe/{name}.png").convert("RGBA")
    return im.resize((64 * k, 64 * k), Image.LANCZOS)


PORT_TILES = {"north": (((0, -2), "N"), ((0, 2), "S")), "south": (((0, -2), "N"), ((0, 2), "S")),
              "east": (((2, 0), "E"), ((-2, 0), "W")), "west": (((2, 0), "E"), ((-2, 0), "W"))}


def with_ports(body, k, d, size=None, origin=None, grid=True):
    """body (a k x render on the canvas) on the ground, a vanilla straight pipe joined to each
    port on the tile outside it, under the render (ports.txt: the same for all eight)."""
    size = size or body.size
    origin = origin or (ORIGIN[0] * k, ORIGIN[1] * k)
    g = ground(size, origin, PPT * k) if grid else Image.new("RGBA", size, (0, 0, 0, 0))
    for (tx, ty), face in PORT_TILES[d]:
        im = pipe_sprite(face, k)
        cx, cy = origin[0] + tx * PPT * k, origin[1] + ty * PPT * k
        g.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))
    g.alpha_composite(body, (origin[0] - ORIGIN[0] * k, origin[1] - ORIGIN[1] * k))
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


def orange(im):
    r, g, b = im.convert("RGB").split()
    m1 = r.point(lambda v: 255 if v > 150 else 0)
    m2 = ImageChops.subtract(r, g).point(lambda v: 255 if v > 45 else 0)
    m3 = ImageChops.subtract(r, b).point(lambda v: 255 if v > 90 else 0)
    return ImageChops.multiply(ImageChops.multiply(m1, m2), m3)


def count(mask, within):
    return ImageChops.multiply(mask, within).histogram()[255]


def cover_rise(plate):
    a = plate.getchannel("A")
    x0, y0 = ORIGIN[0] - 96, ORIGIN[1] - 96
    inside = a.crop((x0, y0, x0 + 192, y0 + 192)).point(lambda v: 255 if v > 128 else 0)
    bb = a.point(lambda v: 255 if v > 128 else 0).getbbox()
    return round(100 * inside.histogram()[255] / 192 ** 2, 1), round((y0 - bb[1]) / 64, 2)


def tool(name, path):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, name), path], capture_output=True, text=True)
    return " ".join(r.stdout.split()[1:]).split("(vanilla")[0].strip()


def measure(d, plate1, idle1, frames1):
    m = {}
    for dd in DIRS:
        p = plate1 if dd == "north" else load(os.path.join(d, f"rot-{dd}-plate.png"), 1)
        m[f"cover_{dd}"], m[f"rise_{dd}"] = cover_rise(p)
    opq = plate1.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    n_op = opq.histogram()[255]
    lit0 = ImageChops.subtract(orange(frames1[0]), orange(idle1))
    m["glow_pct"] = round(100 * count(lit0, opq) / n_op, 1)
    f0 = frames1[0].convert("RGB")
    diff = light = None
    for f in frames1:
        dd_ = ImageChops.difference(f0, f.convert("RGB")).convert("L").point(lambda v: 255 if v > 30 else 0)
        diff = dd_ if diff is None else ImageChops.lighter(diff, dd_)
        o = orange(f)
        light = o if light is None else ImageChops.lighter(light, o)
    light = ImageChops.subtract(light, orange(idle1))
    m["moving_pct"] = round(100 * count(diff, opq) / n_op, 1)
    metal = ImageChops.subtract(diff, light)
    m["moving_metal_pct"] = round(100 * count(metal, opq) / n_op, 1)
    m["moving_light_pct"] = round(100 * count(ImageChops.multiply(diff, light), opq) / n_op, 1)
    m["helium_pct"] = round(100 * count(violet(plate1), opq) / n_op, 1)
    return m, metal, light


def violet(im):
    """The helium line's grey-violet as lit (warm light turns it mauve, R above B): blue over
    green by more than 8, luma 70-220. Nothing else in the palette passes; a lower bound."""
    r, g, b = im.convert("RGB").split()
    m2 = ImageChops.subtract(b, g).point(lambda v: 255 if v > 8 else 0)
    lum = im.convert("L").point(lambda v: 255 if 70 <= v <= 220 else 0)
    return ImageChops.multiply(m2, lum)


PCOL = {"helium": (186, 140, 255), "melt": (255, 128, 48), "spent": (76, 214, 192)}
PNAME = {"helium": "helium-3 (in, to its point of use)", "melt": "molten kamacite (vent to outlet)",
         "spent": "spent or recovered gas"}


def overlay(im2, paths, off):
    """The 2x view dimmed, each run drawn over it in its colour with arrows along the flow."""
    base = Image.blend(im2.convert("RGB"), Image.new("RGB", im2.size, (24, 22, 20)), 0.5).convert("RGBA")
    d = ImageDraw.Draw(base)
    for kind in ("melt", "spent", "helium"):
        for P in paths.get(kind, []):
            pts = [((ORIGIN[0] + 64 * x) * 2 + off[0], (ORIGIN[1] - 64 * (y + z / 2)) * 2 + off[1]) for x, y, z in P]
            if len(pts) < 2:
                continue
            d.line(pts, fill=(10, 10, 10), width=10, joint="curve")
            d.line(pts, fill=PCOL[kind], width=5, joint="curve")
            acc, nxt = 0.0, 34.0
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                seg = math.hypot(x1 - x0, y1 - y0)
                while seg > 0 and acc + seg >= nxt:
                    f = (nxt - acc) / seg
                    cx, cy = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
                    ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
                    tri = [(cx + ux * 9, cy + uy * 9), (cx - ux * 6 - uy * 7, cy - uy * 6 + ux * 7),
                           (cx - ux * 6 + uy * 7, cy - uy * 6 - ux * 7)]
                    d.polygon(tri, fill=PCOL[kind], outline=(10, 10, 10))
                    nxt += 60.0
                acc += seg
    y = 8
    for kind in ("helium", "melt", "spent"):
        d.rectangle([8, y, 40, y + 12], fill=PCOL[kind], outline=(0, 0, 0))
        d.text((48, y - 2), PNAME[kind], font=font(13, True), fill=TEXT)
        y += 20
    return base


def chain_lines(meta):
    return [f"{L['n']}. {L['text']}" for L in sorted(meta["labels"], key=lambda L: L["n"])]


def numbered(im2, labels, off):
    d = ImageDraw.Draw(im2)
    for L in labels:
        x, y = L["px"][0] * 2 + off[0], L["px"][1] * 2 + off[1]
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
    cols = {c[1][:3] for c in im.getcolors(1 << 22) if c[1][3] > 200}
    out = set()
    for g, h in groups.items():
        rgb = tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        if "isotope" not in g and any(max(abs(rgb[j] - c[j]) for j in range(3)) <= 1 for c in cols):
            out.add(g)
    return out


def gif(frames, path):
    strip = Image.new("RGB", (frames[0].width, frames[0].height * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f.convert("RGB"), (0, i * f.height))
    # libimagequant (round 4): the median cut merged the glass's few violet and peach px into grey-beige
    pal = strip.quantize(colors=256, method=Image.Quantize.LIBIMAGEQUANT)
    q = [f.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=GIF_MS, loop=0, optimize=True)
    return os.path.getsize(path) / 1e6


# the box every view of a concept is cut to, at 1x: the canvas less a margin, ports included
VIEW = (40, 40, 344, 368)


def crop1(im, k):
    return im.crop(tuple(v * k for v in VIEW))


# ---------------------------------------------------------------- the concepts' words
S = {
    1: dict(slug="gas-lift-derrick", name="GAS-LIFT DERRICK",
            helium="Helium is the lifting gas: the injector on the crown sends it down the lance into the bore, where "
                   "it lightens the melt column so each charge drives a surge up the side riser; the gas breaks out "
                   "in the surge pot and is pumped back round.",
            seen=["The player follows the grey-violet lagged line from the south flange through the station and the "
                  "turning meter, up the derrick's south face to the injector on the crown.",
                  "Each charge, in order: the meter spurts, the injector's red lever kicks and the crown gauge jumps "
                  "(frames 25 and 9), then the riser's sight glass floods orange (peaks at frames 0 and 16) and the "
                  "wellhead gauge swings with it.",
                  "Where it goes: off the surge pot's head along the bare return line (violet bands) to the green "
                  "booster compressor, whose coupling turns; its discharge (lagged again) runs back into the "
                  "valve station."],
            read="A squat oxide-red lattice derrick over the vent, the injector on its crown, a hot riser and a "
                 "refractory surge pot beside it; now a pale grey-violet helium line climbs the derrick's face and "
                 "a bare return arcs over the north from the pot to the compressor. Reads as a gas-lift wellhead.",
            motion=["32 frames, two charges a loop; frame 0 is the top of a surge.",
                    "Flow meter (on the line beside the station): its half-red rotor turns four times a loop, "
                    "fastest at each charge.",
                    "Injector on the crown: lever and rod kick 0.06 of a loop before each surge (frames 25 and 9) "
                    "and ease back; the crown gauge on the line jumps with it.",
                    "Riser sight glass: the melt floods to the top with each surge and drains to a sixth "
                    "(draw_as_glow in the game); the wellhead gauge swings with the level.",
                    "Booster compressor: its coupling turns twice a loop. Idle: all still, the glass dark, the "
                    "meter stopped."],
            plumbing=["Helium in: south flange > valve station (gate valve) > flow meter > lagged line up the "
                      "derrick's south face (clamped at two levels) > injector valve > lance down the bore > "
                      "wellhead.",
                      "Start-up bottles: four valves pigtailed into a header > lagged line > the station's west face.",
                      "Melt: vent > wellhead's east wing > riser (sight glass) > over the top > surge pot > the pot's "
                      "foot > north flange.",
                      "Spent gas: the pot head's separator dome > bare return line > compressor suction; compressor "
                      "discharge > lagged line > the station's west face (a closed loop).",
                      "Cables: switch cabinet > injector actuator and > compressor motor; transformer > the riser's "
                      "heater (now ending on the riser, not in air).",
                      "Removed from round 2: the hose from the compressor to the wellhead's blind west wing (a blank "
                      "flange; the wing is now a tapping carrying the bore gauge); the bottle pipe that started at "
                      "the bottles' blank ends (their valves now face the header)."],
            finish="As round 2: oxide-red derrick, refractory cellar and surge pot, heat-stained steel for the riser "
                   "and hot lines, green compressor, grey cabinet, cream desk. New: the helium line and lance in "
                   "grey-violet canvas lagging with pale-violet bands (helium-colour.txt, shared by all eight); "
                   "the spent return bare steel with violet bands at its ends; the meter brass-bezelled.",
            departs=["The derrick replaces the spec's 'no tall structure' read (spec 3.1); the lance is the spec's "
                     "injection, the riser its production riser.",
                     "No frost or cold colour: the spec's frost-jacketed intake (3.2) is left to effects; the helium "
                     "colour is grey-violet, not helium-3's pale-blue base_color.",
                     "Four corners chamfered (desk, bottle skid, cabinet, the pot's skid) to break the square."]),
    2: dict(slug="bucket-ladder", name="BUCKET LADDER",
            helium="Helium is the cover gas: it blankets the melt in the sump and under the launder's sealed hood, "
                   "and is purged out each time a bucket tips, so the melt meets nothing else; the purged gas is "
                   "recovered and fed back to the sump.",
            seen=["The player follows the lagged line from the south flange through the meter to a tee: one branch "
                  "into the sump's hood, one along the drive frame and up the east side into the launder's sealed "
                  "hood.",
                  "Each tip, in order: a bucket tips into the launder's mouth (the spill peaks at frames 0 and 16), "
                  "then the hood's two red purge valves lift in turn (frames 3/5 and 19/21), the meter spurts to make "
                  "up the gas and the hood line's gauge dips.",
                  "Where it goes: the purge vents into the bare spent-gas header that crosses the north to the "
                  "helium receiver (north-west); the recovery compressor beside it returns it, lagged, into the "
                  "sump's hood."],
            read="An ochre armoured ladder slanting up across the machine, ladle-buckets climbing it full of orange "
                 "melt and tipping into a launder whose run is now a sealed grey hood with red purge valves; "
                 "grey-violet helium lines at the south and east, a bare header over the north. Reads as a bucket "
                 "elevator working under a gas blanket.",
            motion=["32 frames; the bucket chain advances two pitches a loop (16 buckets): seamless.",
                    "Buckets climb full (melt lit), tip over the head, return empty underneath. Spill: an orange "
                    "stream into the launder's open mouth, pulsing twice a loop.",
                    "Purge valves on the launder's hood: lift in turn after each tip and drop back.",
                    "Flow meter: turns four times a loop, spurting after each tip. Gauges: the hood line's dips at "
                    "each purge; the manifold's rises a little.",
                    "Drive: the motor's coupling turns three times a loop. Idle: chain stopped, every bucket empty, "
                    "pool, mouth and window dark, valves seated, meter stopped."],
            plumbing=["Helium in: south flange > inlet manifold > lagged line > flow meter > tee > (a) the sump's "
                      "cover-gas hood, south face; (b) along the drive frame, between its beams, up the east side "
                      "> the launder hood's east side.",
                      "Purged gas: two purge valves on the hood > short vents > the spent-gas header (from a nozzle "
                      "on the hood) > over the north > the helium receiver's head.",
                      "Recovered gas: receiver > recovery compressor > lagged return > the sump hood's west end.",
                      "Melt: vent > sump pool > buckets up the ladder > tip > the launder's open mouth > under the "
                      "sealed hood (sight window) > receiving pot > north flange.",
                      "Cables: heater transformer > the launder's mouth (round the south and east edge).",
                      "Removed from round 2: the receiver-to-launder pipe (fed the launder from a vessel nothing "
                      "filled); the lube unit's hose that ended in air over the sump wall; the manifold's launder "
                      "pipe that ended beside the launder; the receiver's blank top nozzle."],
            finish="As round 2: ochre ladder and head frame, heat-stained buckets, refractory sump and pot, green "
                   "drive, cream transformer, oxide receiver. New: the launder's sealed hood grey with dark-steel "
                   "end frames and bolts; helium lines in the shared grey-violet lagging; the spent header bare "
                   "steel with violet bands.",
            departs=["Helium-3 is cover gas, not the lifting agent: the ladder lifts mechanically (a spec question "
                     "for Liam, as in round 2).",
                     "The launder hood sits between the ochre head hood and the pot: at 1x it reads as a grey box with "
                     "two red caps that bob; its sight window is mostly hidden.",
                     "The drive frame pulled in off the south-east corner so the corner can be chamfered; four "
                     "corners chamfered."]),
    5: dict(slug="siphon-bell", name="SIPHON BELL",
            helium="Helium is the piston: each charge pressurises the bell and pushes the melt up the gooseneck, "
                   "then it is vented off to the recovery receiver and the bell refills from the vent.",
            seen=["The player follows the lagged line from the south flange through the charging valve and the meter, "
                  "up and over the vent ring into a nozzle on the dome's south-east shoulder.",
                  "Each cycle, in order: the charging valve's red lever kicks and the meter spurts (frames 28 and 12), "
                  "the bell's gauge rises, the gooseneck window glows with the surge (frames 0 and 16), then the "
                  "three red vent poppets lift in turn (frames 5-7 and 21-23).",
                  "Where it goes: each poppet's tail into the vent header ring round the south of the bell, and the "
                  "ring into the side of the cream recovery receiver (north-east)."],
            read="A squat, ribbed, oxide-red bell held down on the vent by a ring of clamps, the heat-stained "
                 "gooseneck arching off its crown, three red poppets on its shoulder tied into a bare vent ring, and "
                 "now a grey-violet helium line climbing over the ring into the dome. Reads as a pressure vessel "
                 "that pushes and breathes.",
            motion=["32 frames, two charge-and-vent cycles a loop; frame 0 is the top of a surge.",
                    "Charging valve: its red lever kicks just before each surge; the valve gauge jumps with it.",
                    "Flow meter: four turns a loop, nearly all of it in the charge.",
                    "Bell gauge (by the dome nozzle): rises with the surge. Gooseneck window: brightens from a fifth "
                    "to full as each surge passes (draw_as_glow).",
                    "Vent poppets: lift in turn after the surge and drop back. Clamp hydraulics: coupling turns "
                    "three times a loop. Idle: still, window dark, poppets seated, meter stopped."],
            plumbing=["Helium in: south flange > charging valve > flow meter > lagged line up over the vent ring > "
                      "the dome's south-east nozzle (the bell's gas space).",
                      "Charging bottles: four valves pigtailed into a header > lagged line > the valve's west face.",
                      "Melt: vent > under the bell > the gooseneck from the crown > over the arch (window) > north "
                      "flange.",
                      "Spent gas: three poppets > their tails > the vent header ring > the receiver's wall (flanged).",
                      "Hydraulics: power unit > three hoses > the clamp cylinders' bodies. Cables: cabinet > first "
                      "poppet's solenoid; cabinet > the power unit's motor.",
                      "Fixed from round 2: the poppet tails ended short of the ring; the ring ended inside the "
                      "receiver; the receiver had a blank top nozzle (now a relief valve); the hydraulic hoses ended "
                      "on rod tops; the bottle pipe started at the bottles' blank ends; the charging line into the "
                      "flank was hidden under the clamps (now over the ring, into the dome)."],
            finish="As round 2: oxide-red bell with dark-steel ribs, yellow clamp cylinders, heat-stained gooseneck, "
                   "cream receiver, green power unit, grey cabinet. New: the helium line in the shared grey-violet "
                   "lagging; the vent tails and ring bare steel with violet bands; a bolted nozzle on the dome.",
            departs=["The bell is painted steel, lined inside (implied): the only melt seen is the gooseneck window.",
                     "The vented gas goes to a recovery receiver (the Core has no air); the receiver's onward use "
                     "(re-compression to the charging valve) is not drawn.",
                     "Four corners chamfered (bottle skid, power unit skid, receiver skid, cabinet)."]),
    7: dict(slug="electromagnetic-pump", name="ELECTROMAGNETIC PUMP",
            helium="Helium is the coolant: three circulators drive it through jacket blocks on the coil yokes, and "
                   "the warm gas is collected off the yokes and bled into the bore at the wellhead.",
            seen=["The player follows the lagged header from the south flange through the meter, north beside the "
                  "east skid to a buffer receiver; three circulators draw from it and push it up three lagged lines "
                  "into the grey jacket blocks on the yokes' east ends.",
                  "While working: the circulators' couplings turn, the meter turns (quickening as each glow packet "
                  "passes, frames 0 and 16), and the bleed valve's gauge and the inlet gauge swing with each packet.",
                  "Where it goes: off each yoke's top into the bare return collector along the duct's west side, "
                  "down to the bleed valve on the wellhead's top flange, and into the bore."],
            read="Three green coil yokes with copper end-turns clamp a flat hot duct climbing from a refractory "
                 "wellhead; orange glow slides up slots between them. Now grey-violet lines feed jacket blocks on the "
                 "yokes' east ends and a bare collector returns down their west side to the wellhead. Reads as "
                 "cooled electrical machinery.",
            motion=["32 frames; the flow glow runs up the duct twice a loop, each slot brightening in turn "
                    "(draw_as_glow).",
                    "Circulators: couplings turn two, three and two times a loop. Flow meter: four turns a loop, "
                    "quicker with each packet.",
                    "Gauges: the bleed valve's and the inlet's swing with each packet.",
                    "Idle: still, the slots dark, the meter stopped."],
            plumbing=["Helium in: south flange > inlet valve > flow meter > lagged header north along the east skid "
                      "> the buffer receiver's wall (north-east).",
                      "Coolant: header > three short suction lines > circulators > three lagged lines > jacket "
                      "blocks on the yokes' east ends.",
                      "Warm gas: each yoke's top > a short pipe > the return collector along the duct's west side > "
                      "bleed valve > the wellhead's top flange (into the bore).",
                      "Melt: vent > wellhead > duct up through the yokes > head elbow > down > north flange.",
                      "Power: capacitor bank > transformer (trunk); transformer > copper busbars > each yoke's west "
                      "end-turns; frequency converter > the top yoke's terminal box.",
                      "Fixed from round 2: the bleed pipe started in air; the jacket hoses, busbars and converter "
                      "cables ended in air above the yokes; the header ran into the receiver by a blank top nozzle."],
            finish="As round 2: green yokes over dark laminated iron, copper end-turns bound in black tape, "
                   "heat-stained duct, refractory wellhead, ochre A-frames, cream transformer, grey capacitors and "
                   "converter, yellow receiver. New: grey jacket blocks; helium lines in the shared grey-violet "
                   "lagging; the return collector bare steel with violet bands; a bleed valve and gauge on the "
                   "wellhead.",
            departs=["Helium-3 cools the yokes and is bled into the bore, rather than lifting the melt: a change to "
                     "what the helium is for (spec 1), for Liam.",
                     "The header runs under the yokes' overhang: at 1x it shows south of the yokes and again at the "
                     "jacket lines; its middle is hidden.",
                     "Four corners chamfered (capacitor skid, east skid, receiver skid, converter cabinet)."]),
}


def reference_views(k=1):
    """Vanilla's pumpjack (frame 0), the adopted plate (shipped), round 1's model (working f0,
    its pictures and vanilla's covers), each on the ground at k x, cut to VIEW."""
    size = (CANVAS[0] * k, CANVAS[1] * k)
    o = (ORIGIN[0] * k, ORIGIN[1] * k)
    out = []
    base = Image.open(f"{ENT}/pumpjack/pumpjack-base.png").convert("RGBA").crop((0, 0, 261, 273))
    head = Image.open(f"{ENT}/pumpjack/pumpjack-horsehead.png").convert("RGBA").crop((0, 0, 206, 172))
    g = ground(size, o, PPT * k)
    place(g, base, (o[0] - 2.25 * 2 * k, o[1] - 4.75 * 2 * k), k)
    place(g, head, (o[0] - 4.5 * 2 * k, o[1] - 29 * 2 * k), k)
    out.append(("vanilla pumpjack, frame 0", crop1(g, k)))
    g = ground(size, o, PPT * k)
    place(g, Image.open(os.path.join(ADOPTED, "base-north.png")).convert("RGBA"),
          (o[0] + 0.00781 * PPT * k, o[1] - 0.23438 * PPT * k), k)
    out.append(("adopted plate (shipped)", crop1(g, k)))
    meta = json.load(open(os.path.join(R1, "meta.json")))

    def fr(name, f=0):
        m = meta[name]
        w, h = m["size"]
        line = m.get("line_length", 1)
        im = Image.open(os.path.join(R1, name + ".png")).convert("RGBA")
        return im.crop(((f % line) * w, (f // line) * h, (f % line) * w + w, (f // line) * h + h)), m["shift"]
    body = Image.new("RGBA", size, (0, 0, 0, 0))
    for name, add in (("shadow-north", False), ("base-north", False), ("meter-north", False),
                      ("melt-north", False), ("glow-north", True)):
        im, s = fr(name)
        place(body, im, (o[0] + s[0] * PPT * k, o[1] + s[1] * PPT * k), k, add=add)
    out.append(("round 1's model, working f0", crop1(with_ports(body, k, "north"), k)))
    return out


MEAS = {}
FIRST = {}
GLASS_WHERE = {
    1: "Where: in the lagged line's climb up the derrick's south face, between the two lower clamps, tilted with "
       "the face: the line runs into its foot and out of its head on to the injector. It draws at each injector "
       "kick (frames 25 and 9): the level drops and flushes peach-pink, then refills violet.",
    2: "Where: standing after the flow meter on the inlet skid, the tee to the sump's and the launder's hoods on "
       "its head: it draws as the hood purges (frames 3 and 19).",
    5: "Where: in the line's rise beside the charging valve, before it climbs over the vent ring into the dome: "
       "it draws at each charge (frames 28 and 12) as the bell is pressed.",
    7: "Where: between the meter and the coolant header, beside the wellhead on the east: the header leaves its "
       "head and drops under the yokes to the circulators; it draws with each field packet (frames 0 and 16).",
}


def build(n):
    o = S[n]
    d = os.path.join(FULL, str(n))
    meta = json.load(open(os.path.join(d, "meta.json")))
    nf = meta["frames"]
    work4 = [os.path.join(d, f"working-{f:02d}.png") for f in range(nf)]
    work1 = [load(p, 1) for p in work4]
    work2 = [load(p, 2) for p in work4]
    idle1, idle2 = load(os.path.join(d, "idle.png"), 1), load(os.path.join(d, "idle.png"), 2)
    plate1, plate2 = load(os.path.join(d, "plate.png"), 1), load(os.path.join(d, "plate.png"), 2)
    m, metal1, light1 = measure(d, plate1, idle1, work1)
    plate_png = os.path.join(d, "plate-1x.png")
    plate1.save(plate_png)
    m["finish"] = tool("finish.py", plate_png)
    m["tonal"] = tool("tonal.py", plate_png)
    g_w1 = [crop1(with_ports(f, 1, "north"), 1) for f in work1]
    g_w2 = [crop1(with_ports(f, 2, "north"), 2) for f in work2]
    g_i2 = crop1(with_ports(idle2, 2, "north"), 2)
    g_i1 = crop1(with_ports(idle1, 1, "north"), 1)
    m["gif_1x_mb"] = round(gif(g_w1, os.path.join(OUT, f"{n:02d}-{o['slug']}-1x.gif")), 2)
    m["gif_2x_mb"] = round(gif(g_w2, os.path.join(OUT, f"{n:02d}-{o['slug']}-2x.gif")), 2)
    gm = GM.measure(d, CANVAS, nf)
    m["glass"] = gm
    MEAS[n] = m
    FIRST[n] = (g_w1[0], m)
    gpanel = GM.panel(d, CANVAS, nf, gm, font=font)
    chain = numbered(g_w2[0].copy(), meta["labels"], (-VIEW[0] * 2, -VIEW[1] * 2))
    paths = overlay(g_w2[0], meta.get("paths", {}), (-VIEW[0] * 2, -VIEW[1] * 2))
    paths.convert("RGB").save(os.path.join(OUT, f"{n:02d}-{o['slug']}-paths.png"))
    # the motion map: plate dimmed, moving metal magenta, the melt's light cyan (at 1x, shown 2x)
    base = plate2.convert("RGB")
    mm = Image.blend(base, Image.new("RGB", base.size, (40, 36, 32)), 0.55)
    mm.paste((230, 40, 200), mask=metal1.resize(base.size, Image.NEAREST))
    mm.paste((60, 220, 255), mask=ImageChops.multiply(light1, plate1.getchannel("A").point(
        lambda v: 255 if v > 0 else 0)).resize(base.size, Image.NEAREST))
    mm = mm.convert("RGBA")
    mm.putalpha(plate2.getchannel("A"))
    mmg = crop1(with_ports(mm, 2, "north"), 2)
    cm = Image.open(os.path.join(CMAP, str(n), "colourmap.png")).convert("RGBA").resize(
        (CANVAS[0] * 2, CANVAS[1] * 2), Image.NEAREST)
    cmg = crop1(with_ports(cm, 2, "north"), 2)
    used = used_groups(os.path.join(CMAP, str(n), "colourmap.png"), os.path.join(CMAP, str(n), "colourmap.json"))
    rots = [None]
    for dd in DIRS[1:]:
        rots.append(captioned(crop1(with_ports(load(os.path.join(d, f"rot-{dd}.png"), 1), 1, dd), 1),
                              f"{dd}, working f0\ncover {m[f'cover_{dd}']} %, rise {m[f'rise_{dd}']:+.2f} t"))
    rots[0] = captioned(g_w1[0], f"north, working f0\ncover {m['cover_north']} %, rise {m['rise_north']:+.2f} t")
    kf = [int(i * nf / 8) for i in range(8)]
    kc = (24, 30, 280, 300)
    keys = vstack([hrow([g_w1[i].crop(kc) for i in kf[:4]], 6), hrow([g_w1[i].crop(kc) for i in kf[4:]], 6)], 6)
    r1 = hrow([captioned(g_w2[0], "WORKING, 2x (frame 0)"), captioned(g_i2, "IDLE, 2x (stopped, the melt dark)")])
    r2 = hrow([captioned(chain, "THE CHAIN (numbered, 2x, working frame 0)"),
               captioned(paths, "PATH OVERLAY, 2x: helium violet, melt orange, spent gas teal")])
    r3 = hrow([captioned(mmg, "MOTION MAP, 2x: magenta moves, cyan is the melt's light"),
               captioned(cmg, "COLOUR MAP, 2x (each part in its group's key colour)")])
    W = max(r1.width, r2.width, r3.width) + 20
    head_lines = wrap("Round 4 (T03; Liam, 2026-10-15: mix A, 'violet, pink pulse per stroke', and the study's kit "
                      "changes carried over: ID bands #9C8CB0, ceramic gauge faces, dark-steel flanges, non-refracting "
                      "glass; a helium glow allowed beside the melt's orange): round 3's concept with an armoured glass "
                      "sight tank set in its helium line, grey-violet liquid with rising bubbles lit faintly violet, "
                      "its level drawn down and flushing peach-pink at each stroke, refilling violet; idle unlit and "
                      "still. Round 3 (Liam, 2026-10-12: helium seen at work, honest plumbing): round 2's concept revised so "
                      "the player can follow helium-3 from the south flange to where it does its job and see the job "
                      "happen every loop, and every pipe runs between two devices. The helium line is the shared "
                      "grey-violet lagging (helium-colour.txt); the ports are vanilla straight pipes on the tile "
                      "outside each face, the model's flange at the edge on assembler 3's axis (ports.txt). Reaction "
                      "Plant finish, no frost or cold colour; orange only where melt is seen. Not a model; nothing adopted; "
                      "nothing in graphics/.", 13, W - 20)
    head_ = Image.new("RGBA", (W, 44 + 18 * len(head_lines)), BG)
    dd_ = ImageDraw.Draw(head_)
    text(dd_, (10, 6), f"VENT PUMP, ROUND 4 -- {n}. {o['name']}  (3 x 3), THE HELIUM SEEN IN GLASS", 22, HEAD, True)
    for i, ln in enumerate(head_lines):
        text(dd_, (10, 40 + 18 * i), ln, 13, SUB)
    meas = [f"Cover (plate alpha > 128 inside the 3 x 3; the bar 92 %): north {m['cover_north']} %, east "
            f"{m['cover_east']} %, south {m['cover_south']} %, west {m['cover_west']} %.",
            f"Rise over the north edge: north {m['rise_north']:+.2f}, east {m['rise_east']:+.2f}, south "
            f"{m['rise_south']:+.2f}, west {m['rise_west']:+.2f} tile.",
            f"Glow (the melt's orange, working frame 0, of the opaque plate): {m['glow_pct']} %.",
            f"Helium line seen (its grey-violet as lit: B > G + 8, luma 70-220, of the opaque plate; a lower "
            f"bound, the bands and lit flanks): "
            f"{m['helium_pct']} %.",
            f"Moving share (pixels changing > 30 over the loop, of the opaque plate): {m['moving_pct']} % "
            f"(moving metal {m['moving_metal_pct']} %, the melt's light {m['moving_light_pct']} %: a pixel orange in any "
            f"frame counts as light, so melt carried by moving parts counts there).",
            f"finish.py (plate, north): {m['finish']}.  tonal.py: {m['tonal']} (vanilla p50 41-63, the mod ~75-81; "
            f"p95 143-189).",
            f"GIF 1x {m['gif_1x_mb']} MB ({nf} frames at {GIF_MS} ms); 2x {m['gif_2x_mb']} MB (keep out of git)."]
    sheet = vstack([
        head_, r1, r2,
        block("THE CHAIN (the numbers on the plate above)", chain_lines(meta), W, tight=True),
        block("HELIUM AT WORK", [o["helium"]] + o["seen"], W),
        block("THE HELIUM SIGHT GLASS (round 4, mix A)", [GLASS_WHERE[n]] + GM.lines(gm), W, tight=True),
        captioned(gpanel, "THE GLASS AT GAME SCALE: 1x shown x4 (nearest): idle, level full, the draw; then the loop "
                          "at 2x round the glass"),
        block("PLUMBING: EVERY RUN AND ITS TWO ENDS", o["plumbing"], W, tight=True),
        r3,
        captioned(palette(os.path.join(CMAP, str(n), "colourmap.json"), used, 1040), "PALETTE"),
        captioned(hrow(rots, 14), "FOUR ROTATIONS, 1x (64 px a tile), working frame 0, the ports of each"),
        captioned(keys, f"KEY FRAMES, 1x: frames {', '.join(map(str, kf))} of {nf}"),
        block("READ", [o["read"]], W),
        block("MOTION (for spec 6.2)", o["motion"], W, tight=True),
        block("FINISH", [o["finish"]], W),
        block("MEASURED (64 px a tile)", meas, W, tight=True),
        block("DEPARTS FROM THE BRIEF OR THE SPEC, AND NOTES", o["departs"], W, tight=True),
    ], width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    path = os.path.join(OUT, f"{n:02d}-{o['slug']}.png")
    if max(pad.size) > 7900:
        pad = pad.resize((round(pad.width * 7900 / max(pad.size)), round(pad.height * 7900 / max(pad.size))),
                         Image.LANCZOS)
    pad.convert("RGB").save(path)
    print(path, pad.size, json.dumps(m))


R2 = os.path.join(HERE, "..", "round-2")


def round2_first(n):
    """Round 2's 1x GIF, frame 0 (its own view: round 1's pipe pictures and covers)."""
    im = Image.open(os.path.join(R2, f"{n:02d}-{S[n]['slug']}-1x.gif"))
    im.seek(0)
    return im.convert("RGBA")


def contact():
    refs = reference_views(1)
    row_r = hrow([captioned(im, nm, 12) for nm, im in refs], 16)
    r2m = json.load(open(os.path.join(R2, "measures-a.json")))
    old, ours = [], []
    for n in sorted(FIRST):
        m2 = r2m[str(n)]
        old.append(captioned(round2_first(n), f"{n}. round 2\ncover {m2['cover_north']} %, rise "
                                              f"{m2['rise_north']:+.2f} t\nglow {m2['glow_pct']} %, moving "
                                              f"{m2['moving_pct']} %", 12))
        im, m = FIRST[n]
        ours.append(captioned(im, f"{n}. {S[n]['name'].title()}, round 3\n"
                                  f"cover {m['cover_north']} % (min {min(m['cover_' + d] for d in DIRS)} %), "
                                  f"rise {m['rise_north']:+.2f} t\nglow {m['glow_pct']} %, moving "
                                  f"{m['moving_pct']} %, helium line {m['helium_pct']} %", 12))
    row_2 = hrow(old, 16)
    row_o = hrow(ours, 16)
    W = max(row_r.width, row_o.width, row_2.width) + 20
    head_ = Image.new("RGBA", (W, 92), BG)
    d = ImageDraw.Draw(head_)
    text(d, (10, 6), "VENT PUMP, ROUND 3 -- ARTIST A: CONCEPTS 1, 2, 5 AND 7 AT GAME SCALE", 20, HEAD, True)
    for i, ln in enumerate(wrap("64 px a tile, one ground, facing north (helium in south, melt out north). Top: "
                                "vanilla's pumpjack (frame 0), the adopted plate as shipped, round 1's model working. "
                                "Middle: round 2, working frame 0, as shipped (round 1's pipe pictures and covers). "
                                "Bottom: round 3, working frame 0: helium seen at work (the grey-violet line, meter, "
                                "gauges and the action it drives) and every pipe going somewhere; ports as ports.txt "
                                "(vanilla straight pipes). Concepts 8, 9, 10 and 19 are contact sheet B.", 12, W - 20)):
        text(d, (10, 34 + 16 * i), ln, 12, SUB)
    sheet = vstack([head_, row_r, captioned(row_2, "ROUND 2", 13), captioned(row_o, "ROUND 3", 13)], 16, width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    p = os.path.join(OUT, "contact-sheet-a.png")
    pad.convert("RGB").save(p)
    print(p, pad.size)


for n in [int(v) for v in args.only.split(",")]:
    build(n)
old = {}
mp = os.path.join(OUT, "measures-a.json")  # round 4
if os.path.exists(mp):
    old = json.load(open(mp))
old.update({str(k): v for k, v in MEAS.items()})
json.dump(old, open(mp, "w"), indent=1)
# the contact sheet of all eight, round 3 above round 4, is vp4_contact.py's
