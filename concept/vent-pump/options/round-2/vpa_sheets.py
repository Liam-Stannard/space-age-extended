#!/usr/bin/env python3
"""Vent Pump, round 2, artist A (concepts 1, 2, 5, 7): sheets, GIFs, measures, contact sheet A.

  python3 vpa_sheets.py <full-dir> <cmap-dir> <out-dir> [--factorio <data>] [--only 1,2,5,7]

<full-dir>/<n>/ is vpa_<n>_*.py's output at 4x (idle.png, plate.png, working-NN.png, rot-<d>.png,
rot-<d>-plate.png, meta.json with the labelled chain); <cmap-dir>/<n>/ its --colourmap run.
The helpers follow the Radiant Generator's round-6 sheets (round-6/r6_sheets.py); every view on
the ground carries round 1's pipe pictures (concept/vent-pump/model/sheets/ports, to assembler
3's outline) and vanilla's covers, placed as the engine places them, as round 1's review sheet
does: the output face's and the input face's, nothing connected. Measures, at 1x (64 px a tile):

  cover    plate alpha > 128 inside the 3 x 3 (the bar is 92 %), per direction
  rise     the plate's top over the footprint's north edge, tiles, per direction
  glow     orange (R > 150, R > G + 45, R > B + 90) in working frame 0 and not in the idle frame,
           of the opaque plate: the melt's light, facing north
  moving   pixels that change by > 30 over the loop, of the opaque plate; split into moving
           metal and the melt's light (orange in any frame)
  finish   tools/blender/finish.py and tonal.py on the plate (facing north)

Writes <n>-<slug>.png (the sheet), <n>-<slug>-1x.gif (working, game scale, under 5 MB),
<n>-<slug>-2x.gif (keep out of git), contact-sheet-a.png, measures-a.json.
"""
import argparse
import json
import os
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

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
PMETA = json.load(open(os.path.join(R1, "ports", "meta.json")))


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


def port_layers(face, k):
    """Round 1's picture for a port on `face`'s middle tile, at its packed shift from the tile the
    connection points into, and vanilla's cover centred there (review_sheet.py's port_layers)."""
    off = {"N": (0, -2), "S": (0, 2), "E": (2, 0), "W": (-2, 0)}[face]
    cx, cy = off[0] * PPT * k, off[1] * PPT * k
    sx, sy = PMETA[f"port-{face}"]["shift"]
    pic = Image.open(os.path.join(R1, "ports", f"port-{face}.png")).convert("RGBA")
    cov = Image.open(f"{ENT}/pipe-covers/pipe-cover-{NAME[face]}.png").convert("RGBA")
    return pic, cov, (cx + sx * PPT * k, cy + sy * PPT * k), (cx, cy)


def with_ports(body, k, d, size=None, origin=None, grid=True):
    """body (a k x render on the canvas) on the ground with the pictures and covers of facing d:
    the north face's behind the machine, the rest in front."""
    size = size or body.size
    origin = origin or (ORIGIN[0] * k, ORIGIN[1] * k)
    g = ground(size, origin, PPT * k) if grid else Image.new("RGBA", size, (0, 0, 0, 0))
    faces = [FACE[d], OPP[FACE[d]]]
    layers = [(fc, port_layers(fc, k)) for fc in faces]

    def draw(north):
        for fc, (pic, cov, pc, cc) in layers:
            if (fc == "N") == north:
                place(g, pic, (origin[0] + pc[0], origin[1] + pc[1]), k)
                place(g, cov, (origin[0] + cc[0], origin[1] + cc[1]), k)
    draw(True)
    g.alpha_composite(body, (origin[0] - ORIGIN[0] * k, origin[1] - ORIGIN[1] * k))
    draw(False)
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
    return m, metal, light


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
    pal = strip.quantize(colors=256)
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
            read="A squat oxide-red lattice derrick over the vent, the injector on its crown, a hot riser and a "
                 "refractory surge pot beside it. Reads as a wellhead under a derrick: oil-field, but nothing "
                 "nods and nothing is open; the melt shows only in the riser's sight glass.",
            motion=["32 frames, two surges a loop; frame 0 is the top of a surge.",
                    "Injector valve on the crown: its red lever and the actuator's rod kick at the start of each "
                    "surge and ease back (frames 27 and 11).",
                    "Riser sight glass: the melt column floods to the top with each surge and drains to a "
                    "sixth (draw_as_glow in the game; the glass's frame stays).",
                    "Booster compressor: its coupling turns twice a loop. Gauges: the wellhead's needle swings "
                    "with the surge, the meter's flickers.",
                    "Idle: still, the glass dark."],
            finish="Oxide-red derrick (worn_paint, rust in its joints); a refractory cellar and surge pot "
                   "(castable, scorched low); heat-stained steel for the riser and the hot lines; bare steel for "
                   "every helium part (no frost); green compressor, grey switch cabinet, cream control desk, "
                   "bare bottles; hazard plate on the crown; oil at the cellar.",
            departs=["Not round 1's christmas tree: the brief's derrick replaces the spec's 'no open shaft, no "
                     "tall structure' read (spec 3.1); the lance is the spec's injection, the riser its "
                     "production riser.",
                     "The spec's frost-jacketed intake and frost bloom (3.2) are left out: the brief rules out "
                     "frost and cold colour in the model.",
                     "The surge pot's gas off its head is drawn as a relief valve only; no plume (effects)."]),
    2: dict(slug="bucket-ladder", name="BUCKET LADDER",
            read="An ochre armoured ladder slanting up across the machine, ladle-buckets climbing it full of "
                 "orange melt, tipping at the head into a heated launder; a refractory sump and receiving pot. "
                 "Reads as a dredge or bucket elevator: unmistakably lifting, and unlike any vanilla building.",
            motion=["32 frames; the bucket chain advances two pitches a loop (16 buckets), so the loop is seamless.",
                    "Buckets: climb the top run full (melt lit), turn over the head tumbler and tip, return "
                    "empty underneath; the melt in a bucket shows from the pool to the turn.",
                    "Spill: an orange stream from the head into the launder, pulsing twice a loop as buckets "
                    "tip; the launder's open stretch and the sump's pool flow (draw_as_glow).",
                    "Drive: the motor's coupling turns three times a loop.",
                    "Idle: the chain stopped, every bucket empty, pool and launder dark."],
            finish="Ochre ladder side plates, head frame and hood (vanilla's yellow, worn, dark-steel ribs, rivet "
                   "lines, hazard plates); heat-stained buckets with bare lips; refractory sump and pot; green "
                   "gearbox and motor; cream heater transformer; oxide helium receiver; bare helium lines.",
            departs=["The ladder runs west-east, across the camera, so the climb and the slant read from the "
                     "south at 1x; facing north the melt still rises at the vent and leaves north.",
                     "Helium-3 is used as cover gas (sump and launder blanket) rather than as the lifting "
                     "agent: the bucket ladder lifts mechanically. The prototype's helium draw stays as is; "
                     "the reason it burns helium is a spec question for Liam.",
                     "The most moving metal of the four (see measures): a big animation sheet to budget."]),
    5: dict(slug="siphon-bell", name="SIPHON BELL",
            read="A squat, ribbed, oxide-red bell held down on the vent by a ring of hydraulic clamps, a heavy "
                 "heat-stained gooseneck arching off its crown to the north face, three red vent valves on its "
                 "shoulder and a vent header round it. Reads as a pressure vessel that pushes: one dominant form.",
            motion=["32 frames, two charge-and-vent cycles a loop; frame 0 is the top of a surge.",
                    "Gooseneck window: the melt in it brightens from a fifth to full as each surge passes and "
                    "flows toward the outlet (draw_as_glow).",
                    "Vent valves: the three red poppets lift in turn after each surge and drop back.",
                    "Clamp hydraulics: the pump's coupling turns three times a loop; the charging gauge rises "
                    "with each charge.",
                    "Idle: still, the window dark, the poppets seated."],
            finish="Oxide-red bell with dark-steel ribs, skirt and bands (worn_paint, rust in the seams and at "
                   "the skirt), yellow clamp cylinders; heat-stained gooseneck with bare flanges; bare helium "
                   "lines and bottles; cream recovery receiver; green power unit; grey cabinet.",
            departs=["The bell is painted steel, lined inside (refractory implied, not seen): the only melt seen is "
                     "in the gooseneck window.",
                     "The vented gas is drawn going to a recovery receiver rather than to air (the Core has no "
                     "air), which is a new part the spec does not have.",
                     "Least glow of the four in idle-to-working difference: the bell reads by its form, not its "
                     "light."]),
    7: dict(slug="electromagnetic-pump", name="ELECTROMAGNETIC PUMP",
            read="Three green coil yokes with copper end-turns clamp a flat hot duct that climbs from a "
                 "refractory wellhead to a hot head elbow; orange glow slides up slots between the yokes. A "
                 "capacitor bank, transformer and busbars on the west, helium circulators on the east. Reads as "
                 "electrical machinery: no moving part in the metal.",
            motion=["32 frames; the flow glow runs up the duct twice a loop: each slot brightens in turn from the "
                    "wellhead to the head, its bands flowing uphill (draw_as_glow).",
                    "Cooling: the three helium circulators' couplings turn (two, three and two turns a loop).",
                    "Idle: still, the slots dark."],
            finish="Green yokes (electrical machine green, worn) over dark laminated iron with bare lamination "
                   "lines, copper end-turns bound in black tape; heat-stained duct and elbows; refractory "
                   "wellhead; ochre A-frames; cream transformer with ceramic bushings and copper busbars; grey "
                   "capacitor cans and converter cabinet; yellow helium return receiver; bare helium lines.",
            departs=["Helium-3 here cools the yokes and is then bled into the bore, rather than lifting the melt: "
                     "a change to what the helium is for (spec 1), for Liam.",
                     "The duct is inclined so the yokes and slots face the camera at 1x."]),
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
    MEAS[n] = m
    FIRST[n] = (g_w1[0], m)
    chain = numbered(g_w2[0].copy(), meta["labels"], (-VIEW[0] * 2, -VIEW[1] * 2))
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
    r2 = hrow([captioned(chain, "VENT TO OUTLET (numbered, 2x)"),
               captioned(mmg, "MOTION MAP, 2x: magenta moves, cyan is the melt's light")])
    W = max(r1.width, r2.width) + 20
    head_lines = wrap("Round 2 (Liam's eight from twenty): a lit Blender concept on the GPU in the Reaction Plant's "
                      "finish (worn_paint, a paint per unit, refractory or heat-stained steel where the melt is held, "
                      "orange only where melt is seen, no frost or cold colour). Helium-3 in at the south face, "
                      "molten kamacite out at the north, straight through (the prototype). Round 1's pipe pictures "
                      "and vanilla's covers on both faces. Not a model; nothing adopted; nothing in graphics/.",
                      13, W - 20)
    head_ = Image.new("RGBA", (W, 44 + 18 * len(head_lines)), BG)
    dd_ = ImageDraw.Draw(head_)
    text(dd_, (10, 6), f"VENT PUMP, ROUND 2 -- {n}. {o['name']}  (3 x 3)", 22, HEAD, True)
    for i, ln in enumerate(head_lines):
        text(dd_, (10, 40 + 18 * i), ln, 13, SUB)
    meas = [f"Cover (plate alpha > 128 inside the 3 x 3; the bar 92 %): north {m['cover_north']} %, east "
            f"{m['cover_east']} %, south {m['cover_south']} %, west {m['cover_west']} %.",
            f"Rise over the north edge: north {m['rise_north']:+.2f}, east {m['rise_east']:+.2f}, south "
            f"{m['rise_south']:+.2f}, west {m['rise_west']:+.2f} tile.",
            f"Glow (the melt's orange, working frame 0, of the opaque plate): {m['glow_pct']} %.",
            f"Moving share (pixels changing > 30 over the loop, of the opaque plate): {m['moving_pct']} % "
            f"(moving metal {m['moving_metal_pct']} %, the melt's light {m['moving_light_pct']} %: a pixel orange in any "
            f"frame counts as light, so melt carried by moving parts counts there).",
            f"finish.py (plate, north): {m['finish']}.  tonal.py: {m['tonal']} (vanilla p50 41-63, the mod ~75-81; "
            f"p95 143-189).",
            f"GIF 1x {m['gif_1x_mb']} MB ({nf} frames at {GIF_MS} ms); 2x {m['gif_2x_mb']} MB (keep out of git)."]
    sheet = vstack([
        head_, r1, r2,
        block("VENT TO OUTLET (the numbers on the plate above)", chain_lines(meta), W, tight=True),
        captioned(hrow(rots, 14), "FOUR ROTATIONS, 1x (64 px a tile), working frame 0, the pictures and covers of each"),
        captioned(keys, f"KEY FRAMES, 1x: frames {', '.join(map(str, kf))} of {nf}"),
        hrow([captioned(cmg, "COLOUR MAP, 2x (each part in its group's key colour)"),
              captioned(palette(os.path.join(CMAP, str(n), "colourmap.json"), used, 520), "PALETTE")]),
        block("READ", [o["read"]], W),
        block("MOTION (for spec 6.2)", o["motion"], W, tight=True),
        block("FINISH", [o["finish"]], W),
        block("MEASURED (64 px a tile)", meas, W, tight=True),
        block("DEPARTS FROM THE BRIEF OR THE SPEC", o["departs"], W, tight=True),
    ], width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    path = os.path.join(OUT, f"{n:02d}-{o['slug']}.png")
    pad.convert("RGB").save(path)
    print(path, pad.size, json.dumps(m))


def contact():
    refs = reference_views(1)
    row_r = hrow([captioned(im, nm, 12) for nm, im in refs], 16)
    ours = []
    for n in sorted(FIRST):
        im, m = FIRST[n]
        ours.append(captioned(im, f"{n}. {S[n]['name'].title()}, working f0\n"
                                  f"cover {m['cover_north']} % (min {min(m['cover_' + d] for d in DIRS)} %), "
                                  f"rise {m['rise_north']:+.2f} t\nglow {m['glow_pct']} %, moving "
                                  f"{m['moving_pct']} %", 12))
    row_o = hrow(ours, 16)
    W = max(row_r.width, row_o.width) + 20
    head_ = Image.new("RGBA", (W, 74), BG)
    d = ImageDraw.Draw(head_)
    text(d, (10, 6), "VENT PUMP, ROUND 2 -- ARTIST A: CONCEPTS 1, 2, 5 AND 7 AT GAME SCALE", 20, HEAD, True)
    for i, ln in enumerate(wrap("64 px a tile, one ground, facing north (helium in south, melt out north). Top: "
                                "vanilla's pumpjack (frame 0), the adopted plate as shipped, round 1's model working. "
                                "Bottom: this half's four, working, frame 0, with round 1's pipe pictures and "
                                "vanilla's covers. Concepts 8, 9, 10 and 19 are contact sheet B.", 12, W - 20)):
        text(d, (10, 34 + 16 * i), ln, 12, SUB)
    sheet = vstack([head_, row_r, row_o], 16, width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    p = os.path.join(OUT, "contact-sheet-a.png")
    pad.convert("RGB").save(p)
    print(p, pad.size)


for n in [int(v) for v in args.only.split(",")]:
    build(n)
old = {}
mp = os.path.join(OUT, "measures-a.json")
if os.path.exists(mp):
    old = json.load(open(mp))
old.update({str(k): v for k, v in MEAS.items()})
json.dump(old, open(mp, "w"), indent=1)
if len(FIRST) == 4:
    contact()
