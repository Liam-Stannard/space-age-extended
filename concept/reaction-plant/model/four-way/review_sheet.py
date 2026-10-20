#!/usr/bin/env python3
"""Reaction plant (the Circulator, 5x5) in four directions: the review sheets and GIF for T06.

  python3 review_sheet.py <runs> [--measures <dir>] [--factorio <data>]

<runs> holds run-north, run-east, run-south and run-west: tools/blender/render.sh's output for
four-way/circulator.py, one run a direction (RP_DIRECTION). <measures> holds measure-<d>/
measures.json (tools/blender/measure.py on each run). Everything is drawn from the PACKED
sheets, placed by their meta.json shifts as the engine places them. Writes beside this script:

  four-way.png   the four rotations beside the signed-off plate (one plate, the engine's pipe
                 pictures) and vanilla's 4-way references (the chemical plant, the oil refinery),
                 on one ground at one scale: idle (no recipe, vanilla's covers on the three
                 ports), working (sae-radiant-precipitation, vanilla pipes joined to the two
                 inputs), the model alone at 2x
  joins.png      the twelve connections at 4x, each with a vanilla pipe joined as the engine
                 draws it, and measure.py's verdict for it
  strips.png     a frame strip of every layer in every direction, as packed
  motion-1x.gif  every motion together at 1x, the four directions side by side, 48 frames at
                 14 fps: the 24-frame loops twice, the press once in frames 24-39
  measures.txt   measure.py's figures per direction beside the signed-off model's
  sheets/<d>/    a copy of each direction's packed sheets, for sign-off

1x is the sprites' own 64 px a tile.
"""
import argparse
import json
import os
import re
import shutil

from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("runs")
ap.add_argument("--measures")
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
args = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
SIGNED = os.path.normpath(os.path.join(HERE, "..", "sheets"))
ENT = f"{args.factorio}/base/graphics/entity"
PIPE = f"{ENT}/pipe/"
COVER = f"{ENT}/pipe-covers/pipe-cover-"
DIRS = ("north", "east", "south", "west")
PPT = 64
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT, SUB, HEAD = (228, 222, 210), (175, 168, 156), (240, 200, 120)
GREEN, AMBER = (90, 255, 110), (255, 196, 60)
NF, PRESS_NF = 24, 16
FACE = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
NAME = {"N": "north", "E": "east", "S": "south", "W": "west"}


def turn(c):
    x, y, f = c
    return (-y, x, "NESW"[("NESW".index(f) + 1) % 4])


CONNS = {"north": [(-1, -2, "N"), (1, -2, "N"), (0, 2, "S")]}
for a_, b_ in zip(DIRS, DIRS[1:]):
    CONNS[b_] = [turn(c) for c in CONNS[a_]]


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


class Sheets:
    """One packed sheets directory: its meta.json and its sheets, placed by their shifts."""

    def __init__(self, path):
        self.path = path
        self.meta = json.load(open(os.path.join(path, "meta.json")))
        self.cache = {}

    def has(self, name):
        return name in self.meta

    def frame(self, name, f=0):
        if name not in self.cache:
            self.cache[name] = Image.open(os.path.join(self.path, name + ".png")).convert("RGBA")
        m = self.meta[name]
        w, h = m["size"]
        f %= m.get("frames", 1)
        line = m.get("line_length", 1)
        x, y = (f % line) * w, (f // line) * h
        return self.cache[name].crop((x, y, x + w, y + h))

    def draw(self, canvas, origin, name, f=0, k=1, tint=None, add=False):
        im = self.frame(name, f)
        if tint:
            im = Image.merge("RGBA", (*Image.new("RGB", im.size, tint).split(), im.getchannel("A")))
        sx, sy = self.meta[name]["shift"]
        centre = (origin[0] + sx * PPT * k, origin[1] + sy * PPT * k)
        if add:
            add_light(canvas, im, centre, k)
        else:
            place(canvas, im, centre, k)


def place(canvas, im, centre, k=1):
    if k != 1:
        im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    x, y = round(centre[0] - im.width / 2), round(centre[1] - im.height / 2)
    canvas.alpha_composite(im, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))


def add_light(canvas, im, centre, k=1):
    """A glow drawn additively: its colour times its alpha, added."""
    if k != 1:
        im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    x, y = round(centre[0] - im.width / 2), round(centre[1] - im.height / 2)
    r, g, b, a = im.split()
    lit = Image.merge("RGB", [Image.composite(c, Image.new("L", im.size, 0), a) for c in (r, g, b)])
    region = canvas.crop((x, y, x + im.width, y + im.height)).convert("RGB")
    from PIL import ImageChops
    canvas.paste(ImageChops.add(region, lit), (x, y))


def ground(size, origin, k, foot=5):
    g = Image.new("RGBA", size, GROUND)
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ox, oy = origin
    off = 0.5 if foot % 2 else 0.0
    for i in range(-20, 21):
        x, y = ox + (i + off) * PPT * k, oy + (i + off) * PPT * k
        d.line([(x, 0), (x, size[1])], fill=(255, 255, 255, 22))
        d.line([(0, y), (size[0], y)], fill=(255, 255, 255, 22))
    h = foot * PPT * k / 2
    d.rectangle([ox - h, oy - h, ox + h, oy + h], outline=(255, 255, 255, 110))
    g.alpha_composite(ov)
    return g


def sprite(path, k=1):
    im = Image.open(path).convert("RGBA")
    return im.resize((im.width * k, im.height * k), Image.LANCZOS) if k != 1 else im


def pipe_at(canvas, origin, k, conn):
    """A vanilla straight pipe on the tile the connection points into."""
    x, y, f = conn
    dx, dy = FACE[f]
    sp = sprite(PIPE + ("pipe-straight-vertical.png" if f in "NS" else "pipe-straight-horizontal.png"), k)
    place(canvas, sp, (origin[0] + (x + dx) * PPT * k, origin[1] + (y + dy) * PPT * k))


def cover_at(canvas, origin, k, conn):
    x, y, f = conn
    dx, dy = FACE[f]
    place(canvas, sprite(COVER + NAME[f] + ".png", k), (origin[0] + (x + dx) * PPT * k, origin[1] + (y + dy) * PPT * k))


LOOPS = ("drive", "coupling-compressor", "coupling-dosing", "coupling-pump", "gauge-reactor-upper",
         "gauge-reactor-lower", "gauge-scrubber", "drip")


def machine(sh, canvas, origin, k, f=0, press=0, working=False, conns=(), covers=(), pictures=None, lamps=True):
    """The plant as the engine draws it: its shadow; what is north of the centre (pipes and covers,
    or the signed-off pictures) behind; the plate, the layers it has at frame f (the press at its
    frame), the legs and their glow while working, the lamps; then what is south of the centre."""
    behind = lambda c: c[1] + FACE[c[2]][1] <= 0
    sh.draw(canvas, origin, "shadow", 0, k)
    for c in conns:
        if behind(c):
            pipe_at(canvas, origin, k, c)
    for c in covers:
        if behind(c):
            cover_at(canvas, origin, k, c)
    if pictures:
        pictures(canvas, origin, k, True)
    sh.draw(canvas, origin, "base", 0, k)
    for name in LOOPS:
        if sh.has(name):
            sh.draw(canvas, origin, name, f, k)
    sh.draw(canvas, origin, "press", press, k)
    if working:
        sh.draw(canvas, origin, "legs", f, k)
        sh.draw(canvas, origin, "legs-glow", 0, k, add=True)
    if lamps:
        sh.draw(canvas, origin, "status-lamp", 0, k, tint=GREEN if working else AMBER)
    if pictures:
        pictures(canvas, origin, k, False)
    for c in conns:
        if not behind(c):
            pipe_at(canvas, origin, k, c)
    for c in covers:
        if not behind(c):
            cover_at(canvas, origin, k, c)
    return canvas


def mk(sh, k=1, size=(8, 9, 4.6), **kw):
    g, o = panel(k, *size)
    return machine(sh, g, o, k, **kw)


def signed_pictures(d):
    """The signed-off one-plate wiring: the plant's own picture for each face drawn at every
    connection on it (pack_ports.py's shift from the tile outside), vanilla's cover over it."""
    pm = json.load(open(os.path.join(SIGNED, "ports", "meta.json")))

    def draw(canvas, origin, k, north):
        for x, y, f in CONNS[d]:
            if (f == "N") != north:
                continue
            dx, dy = FACE[f]
            cx, cy = origin[0] + (x + dx) * PPT * k, origin[1] + (y + dy) * PPT * k
            sx, sy = pm[f"port-{f}"]["shift"]
            place(canvas, sprite(os.path.join(SIGNED, "ports", f"port-{f}.png"), k), (cx + sx * PPT * k, cy + sy * PPT * k))
            place(canvas, sprite(COVER + NAME[f] + ".png", k), (cx, cy))
    return draw


def panel(k, w_tiles=8, h_tiles=9, oy_tiles=4.6):
    size = (int(w_tiles * PPT * k), int(h_tiles * PPT * k))
    origin = (size[0] // 2, int(oy_tiles * PPT * k))
    return ground(size, origin, k), origin


def label(im, text, sub=None):
    top = 40 if sub else 24
    out = Image.new("RGBA", (max(im.width, 8 * len(max(text, sub or "", key=len)) + 8), im.height + top), BG)
    d = ImageDraw.Draw(out)
    d.text((4, 3), text, font=font(13, True), fill=TEXT)
    if sub:
        d.text((4, 21), sub, font=font(11), fill=SUB)
    out.alpha_composite(im, (0, top))
    return out


def row(ims, gap=16):
    w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    out = Image.new("RGBA", (w, max(i.height for i in ims)), BG)
    x = 0
    for i in ims:
        out.alpha_composite(i, (x, 0))
        x += i.width + gap
    return out


def stack(ims, gap=20, pad=16):
    w = max(i.width for i in ims) + 2 * pad
    out = Image.new("RGBA", (w, sum(i.height for i in ims) + gap * (len(ims) - 1) + 2 * pad), BG)
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
    im = Image.new("RGBA", (width, (size + 6) * len(lines) + 6), BG)
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        d.text((0, 3 + i * (size + 6)), ln, font=font(size), fill=TEXT)
    return im


def sidecar(stem):
    t = open(stem + ".lua").read()
    w = int(re.search(r"width\s*=\s*(\d+)", t).group(1))
    h = int(re.search(r"height\s*=\s*(\d+)", t).group(1))
    sx, sy = map(float, re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", t).groups())
    return w, h, sx * 2, sy * 2


def vanilla_panel(stem, foot, k=1, extra=(0, 0), shadow=None):
    w, h, sx, sy = sidecar(stem)
    im = Image.open(stem + ".png").convert("RGBA").crop((0, 0, w, h))
    g, origin = panel(k, 8, 9)
    if shadow:
        sw, shh, ssx, ssy = sidecar(shadow)
        si = Image.open(shadow + ".png").convert("RGBA").crop((0, 0, sw, shh))
        place(g, si, (origin[0] + (ssx + extra[0]) * k, origin[1] + (ssy + extra[1]) * k), k)
    place(g, im, (origin[0] + (sx + extra[0]) * k, origin[1] + (sy + extra[1]) * k), k)
    d = ImageDraw.Draw(g)
    hh = foot * PPT * k / 2
    d.rectangle([origin[0] - hh, origin[1] - hh, origin[0] + hh, origin[1] + hh], outline=(255, 220, 140, 120))
    return g


SH = {d: Sheets(os.path.join(args.runs, f"run-{d}", "sheets")) for d in DIRS}
SIGNED_SH = Sheets(SIGNED)
MEAS = {}
if args.measures:
    for d in DIRS:
        p_ = os.path.join(args.measures, f"measure-{d}", "measures.json")
        if os.path.isfile(p_):
            MEAS[d] = json.load(open(p_))
SIGNED_MEAS = None
if args.measures and os.path.isfile(os.path.join(args.measures, "measure-signed", "measures.json")):
    SIGNED_MEAS = json.load(open(os.path.join(args.measures, "measure-signed", "measures.json")))


def unseen_note(d):
    gone = [n for n in LOOPS if not SH[d].has(n)]
    return "no layer for " + ", ".join(gone) + " (not seen)" if gone else "every layer"


# ===================================================================== four-way.png
def four_way():
    WIDE = 4 * 512 + 3 * 16
    sec = [heading("The Circulator in four directions (T06): the model turned, as vanilla's 4-way machines", WIDE, 24),
           para(["Liam, 2026-10-20: \"The model should be adjusted so the pipe connections make sense and follow the flow of the "
                 "fluid/gas through the model. We could draw a model for each rotation rotate like factorio does for some of the vanilla models.\"",
                 "One model, turned on its turntable under the fixed camera and sun; a real fitting at each of the three connections in every "
                 "direction, its shadow cast and caught; the inputs enter the north header and leave its crown, the west line to the feed drum, "
                 "the east to the compressor; a circuit connector socket in each direction. Every panel: 64 px a tile, one ground, the footprint outlined."],
                WIDE)]
    sec.append(heading("1. The signed-off plate, as wired now: one plate, the engine's pipe picture for each face drawn at every connection on it (no recipe)", WIDE, 16))
    sec.append(row([label(mk(SIGNED_SH, pictures=signed_pictures(d)), f"signed off, facing {d}",
                          "one plate; the pictures move, the building does not") for d in DIRS]))
    sec.append(heading("2. The four-way model, idle, no recipe: all three boxes, vanilla's covers on the unconnected ports", WIDE, 16))
    sec.append(row([label(mk(SH[d], covers=CONNS[d]), f"four-way, facing {d}",
                          f"inputs {CONNS[d][0][2]} at {CONNS[d][0][:2]} and {CONNS[d][1][:2]}, output {CONNS[d][2][2]} at {CONNS[d][2][:2]}")
                    for d in DIRS]))
    sec.append(heading("3. Working, sae-radiant-precipitation: vanilla pipes joined to the two inputs; the engine drops the output box, so its stub stands bare", WIDE, 16))
    sec.append(row([label(mk(SH[d], working=True, conns=CONNS[d][:2]), f"four-way, facing {d}, working",
                          unseen_note(d)) for d in DIRS]))
    sec.append(heading("4. The vanilla 4-way references, the same scale and ground: the chemical plant (3x3) and the oil refinery (5x5)", WIDE, 16))
    cp = [label(vanilla_panel(f"{ENT}/chemical-plant/chemical-plant-{d}-base", 3, extra=(0, -18)), f"chemical plant, {d}") for d in DIRS]
    rf = [label(vanilla_panel(f"{ENT}/oil-refinery/{d}/oil-refinery-{d}", 5,
                              shadow=f"{ENT}/oil-refinery/{d}/oil-refinery-shadow-{d}"), f"oil refinery, {d}") for d in DIRS]
    sec.append(row(cp))
    sec.append(row(rf))
    sec.append(heading("5. The four-way model at 2x, idle, no covers or pipes: the fittings, the leads and the sockets", WIDE, 16))
    big = [label(mk(SH[d], 2, (7.6, 8.4, 4.4)), f"facing {d}, 2x") for d in DIRS]
    sec.append(row(big[:2]))
    sec.append(row(big[2:]))
    out = stack(sec)
    out.convert("RGB").save(os.path.join(HERE, "four-way.png"))
    return out.size


# ===================================================================== joins.png
def joins():
    k = 4
    rows_ = [heading("The twelve connections at 4x, each with a vanilla straight pipe joined as the engine draws it "
                     "(over the building south of its centre, under it otherwise); no cover", 2400, 18)]
    for d in DIRS:
        cells = []
        for i, c in enumerate(CONNS[d]):
            x, y, f = c
            dx, dy = FACE[f]
            g, origin = panel(k, 8, 9)
            machine(SH[d], g, origin, k, conns=[c], lamps=False)
            cx, cy = origin[0] + (x + dx * 0.5) * PPT * k, origin[1] + (y + dy * 0.5) * PPT * k
            half = 1.1 * PPT * k
            crop = g.crop((int(cx - half), int(cy - half), int(cx + half), int(cy + half)))
            verdict = ""
            if d in MEAS:
                j = MEAS[d]["directions"][""]["joins"][i]
                verdict = f"measure.py: {'PASS' if j['pass'] else 'FAIL'}, gap columns {j['gap'].get('columns', j['gap']) if isinstance(j['gap'], dict) else j['gap']}"
            cells.append(label(crop, f"{d}: {'input' if i < 2 else 'output'} at {x},{y} facing {f}", verdict))
        rows_.append(row(cells))
    out = stack(rows_)
    out.convert("RGB").save(os.path.join(HERE, "joins.png"))
    return out.size


# ===================================================================== strips.png
def strips():
    rows_ = [heading("Every layer's frames, as packed, per direction (sheets under 20 px tall shown at 4x)", 3200, 18)]
    names = ("legs",) + LOOPS[:1] + ("press",) + LOOPS[1:]
    for d in DIRS:
        rows_.append(heading(f"facing {d}: {unseen_note(d)}", 3200, 15))
        for n in names:
            if not SH[d].has(n):
                continue
            m = SH[d].meta[n]
            im = Image.open(os.path.join(SH[d].path, n + ".png")).convert("RGBA")
            k = 4 if m["size"][1] < 20 else 1
            if k != 1:
                im = im.resize((im.width * k, im.height * k), Image.NEAREST)
            g = Image.new("RGBA", im.size, GROUND)
            g.alpha_composite(im)
            rows_.append(label(g, f"{n}: {m['frames']} frames of {m['size'][0]} x {m['size'][1]}, shift {m['shift']}"
                                  + (f", at {k}x" if k != 1 else "")))
    out = stack(rows_, gap=8)
    out.convert("RGB").save(os.path.join(HERE, "strips.png"))
    return out.size


# ===================================================================== motion-1x.gif
def gif():
    frames = []
    for t in range(48):
        f = t % NF
        press = t - 24 if 24 <= t < 24 + PRESS_NF else 0
        cells = []
        for d in DIRS:
            g, origin = panel(1, 6.4, 7.4, 4.0)
            machine(SH[d], g, origin, 1, f, press, working=True)
            ImageDraw.Draw(g).text((4, 3), d, font=font(12, True), fill=TEXT)
            cells.append(g)
        frames.append(row(cells, 6).convert("RGB"))
    # one palette for every frame (from the first, working: the blue in it), so unchanged pixels
    # stay identical frame to frame and the GIF stores only what moves
    pal = frames[0].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    frames = [f_.quantize(palette=pal, dither=Image.Dither.NONE) for f_ in frames]
    path = os.path.join(HERE, "motion-1x.gif")
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=71, loop=0, optimize=True)
    return frames[0].size


# ===================================================================== measures.txt
def fig(m):
    dn = m["directions"][next(iter(m["directions"]))]
    c, t, fn = dn["coverage"], dn["tonal"], dn["finish"]
    col = dn.get("colour", {})
    mo = dn.get("motion") or {}
    js = dn.get("joins", [])
    return [f"  coverage: footprint {c.get('footprint_pct')} %, corners {c.get('corners_pct')}, rise {c.get('rise_tiles')} tile, "
            f"over columns {c.get('rise_by_column_tiles')}, extent {c.get('extent_tiles')}",
            f"  tonal plate {t.get('plate')}",
            f"  tonal still {t.get('still')}",
            f"  finish plate {fn.get('plate')}",
            f"  finish still {fn.get('still')}",
            f"  colour: blue {col.get('blue_pct')} %, white_px {col.get('white_px')}, clipped_px {col.get('clipped_px')}, "
            f"idle_blue {col.get('idle_blue_pct')} %",
            f"  motion: moving {mo.get('moving_pct')} %, strobe {mo.get('strobe_pct')} %",
            "  joins: " + "; ".join(f"{j['connection']} {'PASS' if j['pass'] else 'FAIL'}" for j in js),
            f"  pack checks: {dn.get('pack_checks')}"]


def measures():
    lines = ["Reaction plant, the Circulator, in four directions (T06): four-way/circulator.py",
             "rendered by tools/blender/render.sh on the GPU, one run a direction (RP_DIRECTION); measured by tools/blender/measure.py",
             ""]
    if SIGNED_MEAS:
        lines += ["THE SIGNED-OFF MODEL (concept/reaction-plant/model/sheets, measured the same way)"] + fig(SIGNED_MEAS) + [""]
    for d in DIRS:
        lines.append(f"FACING {d.upper()}: {unseen_note(d)}")
        if d in MEAS:
            lines += fig(MEAS[d])
        lines.append(f"  checks (pack.py): {SH[d].meta.get('checks')}")
        lines.append("")
    with open(os.path.join(HERE, "measures.txt"), "w") as f_:
        f_.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    for d in DIRS:
        dst = os.path.join(HERE, "sheets", d)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(SH[d].path, dst)
    print("four-way.png", four_way())
    print("joins.png", joins())
    print("strips.png", strips())
    print("motion-1x.gif", gif())
    measures()
    print("measures.txt")
