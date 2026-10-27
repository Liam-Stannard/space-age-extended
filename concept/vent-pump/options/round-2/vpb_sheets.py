#!/usr/bin/env python3
"""Vent Pump, round 2, artist B (concepts 8, 9, 10, 19): sheets, GIFs, measures, contact sheets.

  python3 vpb_sheets.py <full-dir> <cmap-dir> <out-dir> [--only 08,09,10,19] [--factorio <data>]

<full-dir>/<n>/ is vpb_<n>_*.py's output (idle.png, plate.png, working-NN.png, rot-<dir>.png at
4x, meta.json with the labelled chain); <cmap-dir>/<n>/ its --colourmap run. The helpers
(load, ground, motion map, palette, GIF) are the Radiant Generator round 6's (r6_sheets.py),
so the measures are taken the same way, all at 1x:

  cover   plate alpha > 128 inside the 3x3 footprint (the bar is 92 %)
  rise    the plate's top over the footprint's north edge, in tiles
  glow    pixels the melt lights: working frame 0 brighter than idle by > 40 in red and
          orange (R > 150, R - B > 80, G < 0.66 R), of the opaque plate
  moving  pixels that change by > 30 over the loop, of the opaque plate
  cold    pale blue pixels in the plate (B > R + 12 and B > G + 6, luma > 80): the frost bar is 0
  tonal   tools/blender/tonal.py's p50 and p95 of the plate (alpha > 200)

Every view joins a vanilla straight pipe to each port, on the tile outside it; the model's
own flange stands at the edge on assembler 3's pipe axis (z 0.42). Round 1's pipe pictures
(concept/vent-pump/model/sheets/ports) are not used: they carry round 1's deck slab (S) and
housing wall (E, W), which these buildings do not have.

Writes, in <out-dir>:
  <n>-<slug>.png         the sheet
  <n>-<slug>-1x.gif      the working loop at game scale on the ground, ports joined (< 5 MB)
  <n>-<slug>-2x.gif      the same at 2x (keep out of git)
  contact-sheet-b.png    the four at game scale beside vanilla's pumpjack, round 1's model and
                         the adopted plate
  contact-sheet.png      all eight, when artist A's contact-sheet-a.png and 1x GIFs are there
  measures-b.json
"""
import argparse
import glob
import json
import os
import re

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VP = os.path.normpath(os.path.join(HERE, "..", ".."))
ap = argparse.ArgumentParser()
ap.add_argument("full")
ap.add_argument("cmap")
ap.add_argument("out")
ap.add_argument("--only", default="08,09,10,19")
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
args = ap.parse_args()
FULL, CMAP, OUT, FD = args.full, args.cmap, args.out, args.factorio
os.makedirs(OUT, exist_ok=True)

PPT = 64
CANVAS, ORIGIN = (352, 352), (160, 208)
FOOT = (3, 3)
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
    """A 4x render brought to k x game scale, faint catcher fog cut."""
    im = Image.open(path).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    im = im.convert("RGBa").resize((CANVAS[0] * k, CANVAS[1] * k), Image.LANCZOS)
    return im.convert("RGBA")


def ground(size, origin, ppt, foot=FOOT):
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


def count(mask, within):
    return ImageChops.multiply(mask, within).histogram()[255]


def glow_mask(work, idle):
    """Pixels the melt lights: brighter in red than idle by > 40, and orange (R > 150, R - B > 80)."""
    r, g, b = work.convert("RGB").split()
    r0 = idle.convert("RGB").getchannel("R")
    lit = ImageChops.subtract(r, r0).point(lambda v: 255 if v > 40 else 0)
    hot = ImageChops.multiply(r.point(lambda v: 255 if v > 150 else 0),
                              ImageChops.subtract(r, b).point(lambda v: 255 if v > 80 else 0))
    # the melt's own hue (G under two thirds of R): not ochre, hazard yellow or brass moving into view
    hue = ImageChops.subtract(r.point(lambda v: int(v * 0.66)), g).point(lambda v: 255 if v > 0 else 0)
    return ImageChops.multiply(ImageChops.multiply(lit, hot), hue)


def cold_mask(im):
    r, g, b = im.convert("RGB").split()
    m1 = ImageChops.subtract(b, r).point(lambda v: 255 if v > 12 else 0)
    m2 = ImageChops.subtract(b, g).point(lambda v: 255 if v > 6 else 0)
    lum = im.convert("L").point(lambda v: 255 if v > 80 else 0)
    return ImageChops.multiply(ImageChops.multiply(m1, m2), lum)


def tonal(im):
    px = [p for p in im.get_flattened_data() if p[3] > 200]
    L = sorted(0.299 * r + 0.587 * g + 0.114 * b for r, g, b, a in px)
    q = lambda f: round(L[int(f * (len(L) - 1))])  # noqa: E731
    return q(.05), q(.5), q(.95)


def measure(plate, idle0, work0, frames1):
    fw, fh = FOOT
    x0, y0 = ORIGIN[0] - fw * 32, ORIGIN[1] - fh * 32
    a = plate.getchannel("A")
    opq = a.point(lambda v: 255 if v > 128 else 0)
    inside = a.crop((x0, y0, x0 + fw * 64, y0 + fh * 64)).point(lambda v: 255 if v > 128 else 0)
    cover = inside.histogram()[255] / (fw * fh * 64 * 64)
    bb = opq.getbbox()
    rise = (y0 - bb[1]) / 64
    n_op = opq.histogram()[255]
    glow = count(glow_mask(work0, idle0), opq) / n_op
    f0 = frames1[0].convert("RGB")
    diff = None
    for f in frames1[1:]:
        dd = ImageChops.difference(f0, f.convert("RGB")).convert("L").point(lambda v: 255 if v > 30 else 0)
        diff = dd if diff is None else ImageChops.lighter(diff, dd)
    moving = count(diff, opq) / n_op
    cold = count(cold_mask(plate), opq)
    p5, p50, p95 = tonal(plate)
    return dict(cover_pct=round(100 * cover, 1), rise_tiles=round(rise, 2), glow_pct=round(100 * glow, 1),
                moving_pct=round(100 * moving, 1), cold_px=cold, p5=p5, p50=p50, p95=p95)


def motion_map(plate2, idle2, frames2):
    """The plate at 2x, dimmed; what moves over the loop in magenta, what the melt lights in orange."""
    base = plate2.convert("RGB")
    f0 = frames2[0].convert("RGB")
    move = None
    light = None
    for f in frames2:
        fr = f.convert("RGB")
        dd = ImageChops.difference(f0, fr).convert("L").point(lambda v: 255 if v > 30 else 0)
        move = dd if move is None else ImageChops.lighter(move, dd)
        gl = glow_mask(f, idle2)
        light = gl if light is None else ImageChops.lighter(light, gl)
    still = ImageChops.subtract(move, light)
    out = Image.blend(base, Image.new("RGB", base.size, (40, 36, 32)), 0.55)
    out.paste((230, 40, 200), mask=still)
    out.paste((255, 140, 40), mask=light)
    o = out.convert("RGBA")
    o.putalpha(plate2.getchannel("A"))
    return o


def numbered(im2, labels, k=2):
    d = ImageDraw.Draw(im2)
    for L in labels:
        x, y = L["px"][0] * k, L["px"][1] * k
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


# ---------------------------------------------------------------- the ports, drawn as the engine does
def pipe_sprite(face, k):
    name = "pipe-straight-vertical" if face in "NS" else "pipe-straight-horizontal"
    im = Image.open(f"{FD}/base/graphics/entity/pipe/{name}.png").convert("RGBA")
    return im.resize((64 * k, 64 * k), Image.LANCZOS)


# facing d, the machine's output and input: (into tile, face)
FACING = {"north": [((0, -2), "N"), ((0, 2), "S")], "east": [((2, 0), "E"), ((-2, 0), "W")],
          "south": [((0, 2), "S"), ((0, -2), "N")], "west": [((-2, 0), "W"), ((2, 0), "E")]}


def put(canvas, im, origin, tx, ty, k):
    cx, cy = origin[0] + tx * 64 * k, origin[1] + ty * 64 * k
    canvas.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))


def with_ports(render, d, k, foot=FOOT):
    """The render (machine plus its shadow, k x) on the ground, a vanilla straight pipe joined to
    each port: the model's own flange at the edge (assembler 3's pipe axis) meets it. Round 1's
    pictures are not used: they carry round 1's deck slab (S) and housing wall (E, W)."""
    origin = (ORIGIN[0] * k, ORIGIN[1] * k)
    c = ground(render.size, origin, PPT * k, foot)
    for (tx, ty), face in FACING[d]:
        put(c, pipe_sprite(face, k), origin, tx, ty, k)
    c.alpha_composite(render)
    return c


# ---------------------------------------------------------------- the references
def references():
    """Vanilla's pumpjack (working frame 0), round 1's model and the adopted plate, each cropped
    from round 1's compare-plates.png (1x, the same ground) -- one panel each."""
    cp = Image.open(os.path.join(VP, "model", "compare-plates.png")).convert("RGBA")
    out = []
    for i, cap in ((0, "vanilla pumpjack 3x3 (frame 0)"), (1, "the adopted plate (v4, shipped)"),
                   (3, "round 1's model (set aside), working")):
        out.append((cap, cp.crop((336 * i, 46, 336 * i + 320, 430))))
    return out


# ---------------------------------------------------------------- the concepts' words
COMMON_FINISH = ("The Reaction Plant's round-5 finish (worn_paint over materials.layered, a paint per unit, "
                 "vanilla's warmth, rust only in seams, at the feet and down from bands). The casing is "
                 "spec 3.3's iron-nickel grey-brown (#57524A), pale nickel bands sparingly, refractory "
                 "(or heat-stained steel) wherever the melt is held or runs. The helium side is bare "
                 "steel: no frost, rime, ice or cold colour (measured: the cold count). The only light "
                 "is the melt, #D96B29 to #FF9E52, and only where it is seen; the status lamp is an "
                 "unlit amber lens.")
S = {
    "08": dict(slug="the-gas-lift-tower", name="THE GAS-LIFT TOWER",
               read="A tall narrow riveted tower over the vent with a glass riser in a slot down its south "
                    "face, the melt climbing it in orange with dark helium bubbles; a horizontal head tank "
                    "on the tower top with a float chamber whose lever rocks; a lagged downcomer down the "
                    "north-west. Around its foot, each on its own footing: the helium receiver, the "
                    "recovery compressor, the switchgear, the control house, the skimmings bin.",
               motion=["Bubbles: 2 x 3 columns of helium bubbles climb the glass riser, two pitches a loop "
                       "(seamless); the melt's bands rise twice a loop and breathe +-10 %.",
                       "Float: the separator float lever rocks +-18 degrees, twice a loop.",
                       "Recovery compressor: its coupling turns three times a loop; the flow meter's gauge "
                       "needle swings.",
                       "Idle: still and unlit; the riser's glass is dark slag with the bubbles where they "
                       "stopped."],
               finish="Iron-nickel casing paint on the tower and the head tank, nickel clamp bands on the "
                      "glass, refractory footing and vent collar, oxide-red compressor and skimmings bin, "
                      "green motor and dryer, ochre ladder and dryer, cream control house, grey receiver "
                      "and switchgear, lagging on the downcomer.",
               departs=["The brief's 'helium bubbles carry melt up' is shown as dark voids climbing an "
                        "orange core: helium is not visible, so its bubbles read as holes in the glow.",
                        "Added: the recovery compressor's coupling turns (the brief names only the bubbles "
                        "and the float); it is what makes the helium loop read."]),
    "09": dict(slug="the-rotary-vane-pump", name="THE ROTARY VANE PUMP",
               read="A big ribbed cast pump drum bolted over the vent, its axis north-south, the drive "
                    "open on its south side: the motor on a stool, the slotted brake drum and the "
                    "coupling turning between two bearing pedestals, toward the camera. A sight chest on the drum's "
                    "top with an armoured round port lit orange; a heat-stained gooseneck over to the "
                    "north nozzle. Lube unit, starter cabinet, transformer, drums and a helium bottle "
                    "rack round it.",
               motion=["Drive: the slotted brake drum (a hazard key on its face) and the spider coupling "
                       "turn twice a loop on the open shaft, facing the camera. A shaft, no crank.",
                       "Sight port: the melt's bands run up past the window twice a loop, its strength "
                       "breathing +-15 %.",
                       "Seal-gas gauges swing. Idle: still, the port dark."],
               finish="Iron-nickel casing paint on the pump drum, darker iron on its covers, feet, "
                      "pedestals and stools; nickel on the seal face and the nameplate boss; heat-stained "
                      "steel on the sight chest and the gooseneck; refractory suction bell; green motor "
                      "and lube unit; grey transformer, cabinets and helium bottles; ochre bottle rack; a "
                      "bare brake drum.",
               departs=["The brief does not set the axis; it is north-south so the coupling faces the "
                        "camera (east-west, the first try, showed it edge-on: the turn did not read).",
                        "Added: a slotted brake drum on the shaft, so the turn reads at 1x (the coupling alone "
                        "is small).", "The helium's role is spelled out as seal and blanket gas for the shaft seals and "
                        "the vane chamber: a vane pump does not need helium to lift."]),
    "10": dict(slug="the-twin-cylinder-lift", name="THE TWIN CYLINDER LIFT",
               read="Two tall refractory-lined cylinders side by side over the vent, banded and riveted, "
                    "each with an armoured window down its south face; valve actuators with yellow bodies "
                    "and red and green flags on their domed heads; a catwalk and ladder between them; the "
                    "dip tubes arch into a heat-stained header over the middle and down to the north "
                    "nozzle; the switching valve chest in front on the south.",
               motion=["Windows: each shows its melt level -- cylinder A fills over the first half of the "
                       "loop and empties over the second, B half a loop behind; the emptying one burns "
                       "brighter (it is under helium).",
                       "Actuators: on each head the admit valve's rod strokes up and its red flag turns a "
                       "quarter while that cylinder is being emptied; the vent valve (green flag) does "
                       "the opposite. Both cylinders change over at 0 and 0.5.",
                       "Pilot-air compressor coupling: three turns a loop; gauge needles swing. Idle: "
                       "stopped as at frame 0 (A empty and venting, B full), the windows dark."],
               finish="Refractory (castable) shells -- what holds the melt -- with dark steel hoops and "
                      "rivets, iron-nickel domed heads, nickel head flanges; heat-stained steel on the dip "
                      "tubes and header; lagging on the outlet leg; yellow actuators; grey valve chest, "
                      "receivers and cabinet; ochre catwalk and pilot receiver; oxide drain pot; cream "
                      "level transmitters.",
               departs=["Nothing from the brief left out. Added: a pilot-air compressor in the south-east "
                        "for the actuators (its coupling turns) and a vent receiver with a relief stack "
                        "(no plume: effects are not modelled)."]),
    "19": dict(slug="the-peristaltic-hose-pump", name="THE PERISTALTIC HOSE PUMP",
               read="A round cast track on a ribbed pedestal over the vent, open-topped, a huge black "
                    "armoured hose laid in a U round its south half; a three-armed ochre rotor in the "
                    "middle with nickel rollers pressing the hose. The hose's ends rise out of the track "
                    "on the north side: suction riser in on the north-west, a sight glass and the north "
                    "nozzle out on the north-east. The drive's motor and coupling in the south-east, a "
                    "spare-hose coil and a hoist post for hose changes in the north-east.",
               motion=["Rotor: a third of a turn a loop (one roller pitch, seamless); the rollers press "
                       "the hose flat where they stand.",
                       "Bulges: the hose's cross-section is rebuilt every frame -- squeezed under each "
                       "roller, a slug bulging ahead of it -- so the bulges travel round the U with the "
                       "rollers.",
                       "Sight glass: each slug shows as it passes (one pulse a loop; it is small at 1x). Drive coupling: "
                       "three turns a loop. Idle: the rotor stops where it is, still squeezing."],
               finish="Iron-nickel casing paint on the track pedestal, darker iron on the track wall and "
                      "floor; black armoured hose with dark steel bands; ochre rotor with "
                      "hazard stripes, nickel rollers; refractory riser foot; heat-stained outlet; green "
                      "motor and lube box; oxide-red lube points; grey cabinets; spare hose coil.",
               departs=["Added: a sight glass on the outlet, the only place the melt is seen (the hose is "
                        "opaque), so the building has its orange.",
                        "Helium's role here is a gas cap on the vent collar that presses the melt into the "
                        "hose's suction (a peristaltic pump primes poorly on a hot, gassy feed); the brief "
                        "does not say where the helium goes."]),
}

MEAS = {}
FIRST = {}
# the sun each was rendered under (vpb_kit.py --sun): 13.5 by default, 12 where the plate's p50 ran
# over the mod's ~75-81 at 13.5 (9: 86, 19: 87) -- round 1 tuned its sun on the measured p50 the same way
SUN = {"08": 13.5, "09": 12.0, "10": 13.5, "19": 12.0}


def chain_lines(meta):
    return [f"{L['n']}. {L['text']}" for L in sorted(meta["labels"], key=lambda L: L["n"])]


def bbox_of(ims, k, pad=10):
    box = None
    for im in ims:
        b = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    p = pad * k
    return (max(0, box[0] - p), max(0, box[1] - p), min(CANVAS[0] * k, box[2] + p), min(CANVAS[1] * k, box[3] + p))


def build(n):
    o = S[n]
    d = os.path.join(FULL, n)
    meta = json.load(open(os.path.join(d, "meta.json")))
    nf = meta["frames"]
    work2 = [load(os.path.join(d, f"working-{f:02d}.png"), 2) for f in range(nf)]
    work1 = [load(os.path.join(d, f"working-{f:02d}.png"), 1) for f in range(nf)]
    idle2 = load(os.path.join(d, "idle.png"), 2)
    idle1 = load(os.path.join(d, "idle.png"), 1)
    plate1 = load(os.path.join(d, "plate.png"), 1)
    plate2 = load(os.path.join(d, "plate.png"), 2)
    m = measure(plate1, idle1, work1[0], work1)
    MEAS[n] = m
    # the frame: the whole machine, its shadow, and a tile beyond each port
    bb1 = bbox_of([idle1] + work1[::4], 1, pad=6)
    bb1 = (min(bb1[0], ORIGIN[0] - 112), min(bb1[1], ORIGIN[1] - 168), max(bb1[2], ORIGIN[0] + 112),
           max(bb1[3], ORIGIN[1] + 168))
    bb1 = (max(0, bb1[0]), max(0, bb1[1]), min(CANVAS[0], bb1[2]), min(CANVAS[1], bb1[3]))
    bb2 = tuple(2 * v for v in bb1)
    g_w2 = [with_ports(f, "north", 2).crop(bb2) for f in work2]
    g_i2 = with_ports(idle2, "north", 2).crop(bb2)
    g_w1 = [with_ports(f, "north", 1).crop(bb1) for f in work1]
    g_i1 = with_ports(idle1, "north", 1).crop(bb1)
    FIRST[n] = g_w1[0]
    s1 = gif(g_w1, os.path.join(OUT, f"{n}-{o['slug']}-1x.gif"))
    s2 = gif(g_w2, os.path.join(OUT, f"{n}-{o['slug']}-2x.gif"))
    m["gif_1x_mb"], m["gif_2x_mb"] = round(s1, 2), round(s2, 2)
    labels = [dict(L, px=[L["px"][0] - bb1[0], L["px"][1] - bb1[1]]) for L in meta["labels"]]
    chain = numbered(g_w2[0].copy(), labels)
    mm = motion_map(plate2.crop(bb2), idle2.crop(bb2), [w.crop(bb2) for w in work2])
    mmg = ground(mm.size, ((ORIGIN[0] - bb1[0]) * 2, (ORIGIN[1] - bb1[1]) * 2), 128)
    mmg.alpha_composite(mm)
    cm = Image.open(os.path.join(CMAP, n, "colourmap.png")).convert("RGBA")
    cmg = ground(cm.size, (ORIGIN[0] * 2, ORIGIN[1] * 2), 128)
    cmg.alpha_composite(cm)
    cmg = cmg.crop(bb2)
    used = used_groups(os.path.join(CMAP, n, "colourmap.png"), os.path.join(CMAP, n, "colourmap.json"))
    RC = (16, 40, 344, 352)                       # the footprint, a tile beyond each port, the shadow
    rots = [captioned(with_ports(work1[0], "north", 1).crop(RC), "north (as built)")]
    for dn in ("east", "south", "west"):
        rots.append(captioned(with_ports(load(os.path.join(d, f"rot-{dn}.png"), 1), dn, 1).crop(RC), dn))
    kf = [int(i * nf / 8) for i in range(8)]
    keys = [g_w1[i] for i in kf]
    r1 = hrow([captioned(g_w2[0], "WORKING, 2x (frame 0), vanilla pipes joined"),
               captioned(g_i2, "IDLE, 2x (stopped, unlit)")])
    r2 = hrow([captioned(chain, "THE CHAIN, VENT TO OUTLET (numbered, 2x)"),
               captioned(mmg, "MOTION MAP, 2x: magenta moves, orange is the melt's light")])
    rot_grid = vstack([hrow(rots[:2], 10), hrow(rots[2:], 10)], 10)
    refs = references()
    beside = hrow([captioned(g_w1[0], f"{int(n)}. {o['name'].title()}, working"), captioned(g_i1, "idle")] +
                  [captioned(im, cap) for cap, im in refs], 14)
    W = max(r1.width, r2.width, rot_grid.width, beside.width) + 20
    head_lines = wrap("Round 2, artist B. A lit Blender concept on the GPU in the Reaction Plant's finish; 3x3 on "
                      "the vent, helium-3 in on the south face, molten kamacite out on the north, straight "
                      "through; each port's own flange at the edge (assembler 3's pipe axis) with a vanilla "
                      "pipe on the next tile -- round 1's pipe pictures carry round 1's deck and do not fit, so "
                      "pipe pictures are left for the model. Not a model, nothing adopted, nothing in graphics/.", 13, W - 20)
    head_ = Image.new("RGBA", (W, 44 + 18 * len(head_lines)), BG)
    dd = ImageDraw.Draw(head_)
    text(dd, (10, 6), f"VENT PUMP, ROUND 2 -- {int(n)}. {o['name']}  (3 x 3)", 22, HEAD, True)
    for i, ln in enumerate(head_lines):
        text(dd, (10, 40 + 18 * i), ln, 13, SUB)
    meas = (f"Cover {m['cover_pct']} % of the footprint (plate alpha > 128, 1x; the bar is 92 %). Rise over the "
            f"north edge {m['rise_tiles']:+.2f} tile. Glow (pixels the melt lights, frame 0) {m['glow_pct']} % of "
            f"the opaque plate. Moving share (pixels that change over the loop) {m['moving_pct']} %. Cold "
            f"(pale blue) pixels in the plate: {m['cold_px']} (the frost bar is none). Tonal (plate, "
            f"tonal.py): p5 {m['p5']}, p50 {m['p50']}, p95 {m['p95']} (the mod ~75-81; vanilla p95 "
            f"143-189); sun {SUN[n]}. {nf} frames. GIF 1x {m['gif_1x_mb']} MB, 2x {m['gif_2x_mb']} MB.")
    blocks_a = [block("THE READ", [o["read"]], W),
                block("VENT TO OUTLET (the numbers on the plate above)", chain_lines(meta), W, tight=True)]
    blocks_b = [block("MOTION (for spec 6.2)", o["motion"], W),
                block("FINISH", [o["finish"], COMMON_FINISH], W),
                block("DEPARTURES FROM THE BRIEF", o["departs"], W),
                block("MEASURED (64 px a tile)", [meas], W)]
    sheet = vstack([head_, r1, r2] + blocks_a +
                   [captioned(rot_grid, "FOUR ROTATIONS, 1x (working frame 0; the engine turns the ports "
                                              "with it: out on the facing side, in opposite)"),
                    captioned(beside, "BESIDE VANILLA, THE ADOPTED PLATE AND ROUND 1, 1x (64 px a tile)"),
                    hrow([captioned(cmg, "COLOUR MAP, 2x"),
                          captioned(palette(os.path.join(CMAP, n, "colourmap.json"), used, 520), "PALETTE")]),
                    captioned(hrow(keys, 6), f"KEY FRAMES, 1x: frames {', '.join(map(str, kf))} of {nf}")] +
                   blocks_b, width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    path = os.path.join(OUT, f"{n}-{o['slug']}.png")
    pad.convert("RGB").save(path)
    print(path, pad.size, m)


def contact_row(items, gap=16):
    return hrow([captioned(im, cap, 12) for cap, im in items], gap)


def contact(name, ours, title, note):
    refs = references()
    rows = [contact_row(refs)] + [contact_row(r) for r in ours]
    W = max(r.width for r in rows) + 20
    head_ = Image.new("RGBA", (W, 56), BG)
    d = ImageDraw.Draw(head_)
    text(d, (10, 6), title, 20, HEAD, True)
    text(d, (10, 32), note, 12, SUB)
    sheet = vstack([head_] + rows, 16, width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    pad.convert("RGB").save(os.path.join(OUT, name))
    print(os.path.join(OUT, name), pad.size)


def ours_items():
    out = []
    for n in sorted(FIRST):
        m = MEAS[n]
        out.append((f"{int(n)}. {S[n]['name'].title()}, working\ncover {m['cover_pct']} %, rise {m['rise_tiles']:+.2f} t, "
                    f"glow {m['glow_pct']} %, moving {m['moving_pct']} %", FIRST[n]))
    return out


for n in args.only.split(","):
    build(n)
json.dump(MEAS, open(os.path.join(OUT, "measures-b.json"), "w"), indent=1)
if len(FIRST) == 4:
    contact("contact-sheet-b.png", [ours_items()],
            "VENT PUMP, ROUND 2 -- ARTIST B: 8, 9, 10 AND 19 AT GAME SCALE",
            "64 px a tile, one ground. Top: vanilla's pumpjack, the adopted plate, round 1's model (from round 1's "
            "compare plates). Below: concepts 8, 9, 10 and 19, working frame 0, each port joined to a vanilla pipe.")
    a_gifs = sorted((g for g in glob.glob(os.path.join(OUT, "*-1x.gif"))
                     if re.match(r"0?[1257]-", os.path.basename(g))), key=lambda g: int(os.path.basename(g).split("-")[0]))
    if os.path.exists(os.path.join(OUT, "contact-sheet-a.png")) and len(a_gifs) == 4:
        a_items = []
        mp = os.path.join(OUT, "measures-a.json")
        MA = json.load(open(mp)) if os.path.exists(mp) else {}
        for g in a_gifs:
            im = Image.open(g)
            im.seek(0)
            num, rest = os.path.basename(g)[:-7].split("-", 1)
            nm = rest.replace("-", " ").title()
            ma = MA.get(str(int(num)), {})
            ms = (f"cover {ma.get('cover_north')} %, rise {ma.get('rise_north', 0):+.2f} t, glow {ma.get('glow_pct')} %, "
                  f"moving {ma.get('moving_pct')} % (A's measures)") if ma else "(A's measures not found)"
            a_items.append((f"{int(num)}. {nm}, working (A's 1x GIF, frame 0)\n{ms}",
                            im.convert("RGBA")))
        contact("contact-sheet.png", [a_items, ours_items()],
                "VENT PUMP, ROUND 2 -- THE EIGHT CONCEPTS AT GAME SCALE",
                "64 px a tile. Top: vanilla's pumpjack, the adopted plate, round 1's model. Middle: artist A's 1, 2, 5 "
                "and 7 (frame 0 of their 1x GIFs). Bottom: artist B's 8, 9, 10 and 19.")
    else:
        print("contact-sheet.png not built: contact-sheet-a.png or artist A's four 1x GIFs are not there yet",
              a_gifs)
