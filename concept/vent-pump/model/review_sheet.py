#!/usr/bin/env python3
"""Vent pump: the model's review sheet, compare plates, working GIF and measures.

  python3 review_sheet.py <run-dir> [--render-log <render.sh stdout>] [--collide <collide.txt>]
                          [--factorio <data>]

<run-dir> is tools/blender/render.sh's output for vent_pump.py with --ports --icon: renders/
(sprite size), sheets/ (the packed sheets and meta.json), sheets/ports/, sheets/icon.png.
Everything is drawn from the PACKED sheets, placed by their meta.json shifts as the engine
places them, so the sheet checks the packing too. Writes beside this script:

  review.png             the new plate beside the adopted one and vanilla's pumpjack, same
                         ground, same scale, 1x and 2x; idle and working in all four
                         directions; the glow alone; a frame strip of every animation;
                         the icon; the circuit connector's inherited position; the measures
  compare-plates.png     the pumpjack, the adopted plate and the model at 1x (facing north)
  compare-plates-2x.png  the same at 2x
  motion-1x.gif          working, all four directions, the 16-frame loop twice at the
                         engine's pace (animation_speed 0.25: 15 frames a second)
  measures.txt           every check and measure
  sheets/                a copy of the packed sheets (and ports/, icon.png), for sign-off

1x is the sprites' own 64 px a tile (the game's high-resolution scale, drawn at scale 0.5).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("run")
ap.add_argument("--render-log", default=None)
ap.add_argument("--collide", default=None)
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
args = ap.parse_args()
RUN, FD = args.run, args.factorio
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
TOOLS = os.path.join(REPO, "tools", "blender")
SHEETS = os.path.join(RUN, "sheets")
RENDERS = os.path.join(RUN, "renders")
ENT = f"{FD}/base/graphics/entity"
COVER = f"{ENT}/pipe-covers/pipe-cover-"
ADOPTED = os.path.join(REPO, "graphics", "entity", "vent-pump")
META = json.load(open(os.path.join(SHEETS, "meta.json")))
PMETA = json.load(open(os.path.join(SHEETS, "ports", "meta.json")))
PPT = 64
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)
NF = 16
DIRS = ("north", "east", "south", "west")
FACE = {"north": "N", "east": "E", "south": "S", "west": "W"}
OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}
NAME = {"N": "north", "E": "east", "S": "south", "W": "west"}
GREEN, AMBER = (90, 255, 110), (255, 176, 40)
# the adopted plates as shipped (prototypes/core/entities.lua: vp_plate), shifts in tiles
ADOPTED_SHIFT = {"north": (0.00781, -0.23438), "east": (0.0, -0.02344), "south": (-0.00781, -0.14844),
                 "west": (-0.01562, -0.02344)}
# circuit_connector_definitions["pumpjack"], inherited (spec 15): by_pixel(3, -28.5), all four
CONNECTOR = (3 / 32, -28.5 / 32)


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


SH = {n: Image.open(os.path.join(SHEETS, n + ".png")).convert("RGBA") for n in META if n != "checks"}


def frame_of(name, f=0):
    m = META[name]
    w, h = m["size"]
    n = m.get("frames", 1)
    f %= n
    line = m.get("line_length", 1)
    x, y = (f % line) * w, (f // line) * h
    return SH[name].crop((x, y, x + w, y + h))


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


def at_shift(canvas, origin, name, f=0, k=1, tint=None, add=False):
    im = frame_of(name, f)
    if tint:
        a = im.getchannel("A")
        im = Image.merge("RGBA", (*Image.new("RGB", im.size, tint).split(), a))
    sx, sy = META[name]["shift"]
    place(canvas, im, (origin[0] + sx * PPT * k, origin[1] + sy * PPT * k), k, add=add)


def ground(size, origin, k, foot=3, grid=True):
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


def port_layers(face, k):
    """(picture, cover, their centres) for a port on `face`'s middle tile: our picture at
    pack_ports.py's shift from the tile the connection points into, vanilla's cover centred there."""
    off = {"N": (0, -2), "S": (0, 2), "E": (2, 0), "W": (-2, 0)}[face]
    cx, cy = off[0] * PPT * k, off[1] * PPT * k
    sx, sy = PMETA[f"port-{face}"]["shift"]
    pic = Image.open(os.path.join(SHEETS, "ports", f"port-{face}.png")).convert("RGBA")
    cov = Image.open(COVER + NAME[face] + ".png").convert("RGBA")
    if k != 1:
        pic = pic.resize((pic.width * k, pic.height * k), Image.LANCZOS)
        cov = cov.resize((cov.width * k, cov.height * k), Image.LANCZOS)
    return pic, cov, (cx + sx * PPT * k, cy + sy * PPT * k), (cx, cy)


def machine(canvas, origin, k, d="north", f=0, working=True, ports=True, shadow=True, lamp=True):
    """The pump as the engine draws it facing d: shadow, a north picture behind, the plate, the
    meter at frame f, while working the melt and the glow (additive), the lamp tinted, the other
    pictures and vanilla's covers (nothing connected)."""
    faces = [FACE[d], OPP[FACE[d]]] if ports else []
    layers = [(fc, port_layers(fc, k)) for fc in faces]

    def draw(north):
        for fc, (pic, cov, pc, cc) in layers:
            if (fc == "N") == north:
                place(canvas, pic, (origin[0] + pc[0], origin[1] + pc[1]))
                place(canvas, cov, (origin[0] + cc[0], origin[1] + cc[1]))
    if shadow:
        at_shift(canvas, origin, f"shadow-{d}", 0, k)
    draw(True)
    at_shift(canvas, origin, f"base-{d}", 0, k)
    at_shift(canvas, origin, f"meter-{d}", f, k)
    if working:
        at_shift(canvas, origin, f"melt-{d}", f, k)
        at_shift(canvas, origin, f"glow-{d}", 0, k, add=True)
    if lamp:
        at_shift(canvas, origin, f"status-lamp-{d}", 0, k, tint=GREEN if working else AMBER)
    draw(False)
    return canvas


def panel(size_tiles, k, origin_tiles, foot=3):
    W, H = (round(v * PPT * k) for v in size_tiles)
    o = (round(origin_tiles[0] * PPT * k), round(origin_tiles[1] * PPT * k))
    return ground((W, H), o, k, foot), o


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


def sidecar_pumpjack():
    """Vanilla's pumpjack, frame 0, composited from its base (north) and horsehead layers as
    base/prototypes/entity/mining-drill.lua declares them."""
    base = Image.open(f"{ENT}/pumpjack/pumpjack-base.png").convert("RGBA").crop((0, 0, 261, 273))
    head = Image.open(f"{ENT}/pumpjack/pumpjack-horsehead.png").convert("RGBA").crop((0, 0, 206, 172))
    W, H = 400, 400
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    place(c, base, (W / 2 - 2.25 * 2, H / 2 - 4.75 * 2))
    place(c, head, (W / 2 - 4.5 * 2, H / 2 - 29 * 2))
    return c


def adopted(d):
    im = Image.open(os.path.join(ADOPTED, f"base-{d}.png")).convert("RGBA")
    return im, ADOPTED_SHIFT[d]


# ===================================================================== measures
def tool(name, path):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, name), path], capture_output=True, text=True)
    return " ".join(r.stdout.split()[1:]).split("(vanilla")[0].strip()


def cnt(im):
    return sum(1 for v in im.get_flattened_data() if v)


def alone(d, f=0, working=True, lamp=False):
    W, H = 320, 320
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return machine(c, (W // 2, H // 2), 1, d, f, working, ports=False, shadow=False, lamp=lamp)


def measures():
    m = {}
    for d in DIRS:
        idle = Image.open(os.path.join(RENDERS, f"idle-{d}.png")).convert("RGBA")
        W, H = idle.size
        ox, oy = W / 2, H / 2
        mask = idle.getchannel("A").point(lambda v: 255 if v > 128 else 0)
        h = 3 * PPT // 2
        m[f"cover-{d}"] = cnt(mask.crop((int(ox - h), int(oy - h), int(ox + h), int(oy + h)))) / (2 * h) ** 2
        bb = mask.getbbox()
        m[f"rise-{d}"] = (oy - h - bb[1]) / PPT
        m[f"bbox-{d}"] = ((bb[2] - bb[0]) / PPT, (bb[3] - bb[1]) / PPT)
        w0 = alone(d, 0, True)
        opaque = cnt(w0.getchannel("A").point(lambda v: 255 if v > 128 else 0))
        acc = Image.new("L", (W, H), 0)
        for f in range(1, NF):
            dd = ImageChops.difference(w0, alone(d, f, True)).convert("L").point(lambda v: 255 if v > 10 else 0)
            acc = ImageChops.lighter(acc, dd)
        m[f"moving-{d}"] = cnt(acc) / opaque
        # orange: lit px in the working frame that the idle machine does not have, and where
        i0 = alone(d, 0, False)
        lit = [i for i, (p, q) in enumerate(zip(w0.get_flattened_data(), i0.get_flattened_data()))
               if p[3] > 128 and p[0] - q[0] > 40]
        xs, ys = [i % W for i in lit], [i // W for i in lit]
        m[f"lit-{d}"] = (len(lit) / opaque, ((min(xs) - ox) / PPT, (min(ys) - oy) / PPT, (max(xs) + 1 - ox) / PPT,
                                              (max(ys) + 1 - oy) / PPT) if lit else None)
        # the inherited connector: what of the machine stands within 10 px of it
        cx, cy = ox + CONNECTOR[0] * PPT, oy + CONNECTOR[1] * PPT
        m[f"connector-{d}"] = cnt(mask.crop((int(cx - 10), int(cy - 10), int(cx + 10), int(cy + 10)))) / 400
    return m


# ===================================================================== the pictures
def compare(k):
    """Vanilla's pumpjack, the adopted plate (as shipped) and the model, facing north, at k x on
    one ground. The adopted plate carries its own pipes; the model's are the engine's pictures
    and vanilla's covers, as nothing is connected."""
    tiles, origin = (5.0, 6.0), (2.5, 3.3)
    out = []
    pj = sidecar_pumpjack()
    g, o = panel(tiles, k, origin)
    place(g, pj, o, k)
    out.append(label(g, "vanilla pumpjack (3x3)", "base and horsehead, frame 0"))
    for d in ("north",):
        im, s = adopted(d)
        g, o = panel(tiles, k, origin)
        place(g, im, (o[0] + s[0] * PPT * k, o[1] + s[1] * PPT * k), k)
        out.append(label(g, "adopted plate (graphics/, shipped)", "cut from rotation-strip-v2.png, glow baked in"))
    g, o = panel(tiles, k, origin)
    machine(g, o, k, "north", 0, working=False, shadow=False, lamp=False)
    out.append(label(g, "the model, idle", "plate, meter frame 0, its pictures and vanilla's covers"))
    g, o = panel(tiles, k, origin)
    machine(g, o, k, "north", 0, working=True, shadow=False, lamp=False)
    out.append(label(g, "the model, working, frame 0", "with the melt layer and the glow added"))
    return row(out)


def compare_all(k):
    """The adopted plate and the model in each direction, at k x, the model with its shadow."""
    tiles, origin = (5.0, 5.6), (2.4, 3.0)
    out = []
    for d in DIRS:
        im, s = adopted(d)
        g, o = panel(tiles, k, origin)
        place(g, im, (o[0] + s[0] * PPT * k, o[1] + s[1] * PPT * k), k)
        a = label(g, f"adopted, {d}")
        g, o = panel(tiles, k, origin)
        machine(g, o, k, d, 0, working=True, lamp=False)
        b = label(g, f"model, {d}, working f0")
        out.append(stack([a, b], gap=6, pad=0))
    return row(out)


def states(k=2):
    tiles, origin = (5.0, 5.4), (2.4, 2.9)
    ims = []
    for d in DIRS:
        col = []
        for title, working in (("idle", False), ("working, f0", True)):
            g, o = panel(tiles, k, origin)
            machine(g, o, k, d, 0, working=working)
            col.append(label(g, f"{d}: {title}", "lamp amber (no helium)" if not working else "lamp green"))
        ims.append(stack(col, gap=6, pad=0))
    return row(ims)


def glow_alone(k=2):
    ims = []
    for d in DIRS:
        g = Image.new("RGBA", (round(4.2 * PPT * k), round(4.6 * PPT * k)), (0, 0, 0, 255))
        o = (round(2.1 * PPT * k), round(2.6 * PPT * k))
        at_shift(g, o, f"glow-{d}", 0, k, add=True)
        ims.append(label(g, f"glow-{d} (additive) on black"))
    return row(ims)


def strip(d, name, k=4, per_row=16):
    m = META[f"{name}-{d}"]
    w, h = m["size"]
    sx, sy = m["shift"]
    W, H = 320, 320
    cx, cy = W / 2 + sx * PPT, H / 2 + sy * PPT
    pad = 6
    box = (int(cx - w / 2 - pad), int(cy - h / 2 - pad), int(cx + w / 2 + pad), int(cy + h / 2 + pad))
    tiles = []
    for f in range(NF):
        c = alone(d, f, True)
        g = Image.new("RGBA", (W, H), GROUND)
        g.alpha_composite(c)
        t = g.crop(box)
        t = t.resize((t.width * k, t.height * k), Image.LANCZOS)
        ImageDraw.Draw(t).text((3, 2), f"{f}", font=font(12, True), fill=(255, 240, 200))
        tiles.append(t)
    return row(tiles, gap=4)


def connector_panel(k=2):
    ims = []
    for d in DIRS:
        g, o = panel((4.4, 4.8), k, (2.2, 2.6))
        machine(g, o, k, d, 0, working=False, lamp=False)
        dr = ImageDraw.Draw(g)
        cx, cy = o[0] + CONNECTOR[0] * PPT * k, o[1] + CONNECTOR[1] * PPT * k
        r = 9 * k
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(80, 220, 255, 255), width=3)
        ims.append(label(g, f"{d}: pumpjack's connector", "by_pixel(3, -28.5), inherited"))
    return row(ims)


def icon_panel():
    ic = Image.open(os.path.join(SHEETS, "icon.png")).convert("RGBA")
    big = ic.crop((0, 0, 64, 64)).resize((256, 256), Image.NEAREST)
    old = Image.open(os.path.join(REPO, "graphics", "icons", "vent-pump.png")).convert("RGBA")
    ims = []
    for im, t in ((ic, "icon.png, 120 x 64 (64/32/16/8)"), (big, "the 64 at 4x"),
                  (ic.crop((64, 0, 96, 32)).resize((128, 128), Image.NEAREST), "the 32 at 4x"),
                  (old, "shipped icon (graphics/icons)")):
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
    tiles, origin = (4.4, 4.8), (2.2, 2.6)
    frames = []
    for f in range(2 * NF):
        ims = []
        for d in DIRS:
            g, o = panel(tiles, k, origin)
            machine(g, o, k, d, f % NF, working=True)
            ims.append(g)
        r = row(ims, gap=4)
        ImageDraw.Draw(r).text((6, 4), f"f{f % NF:02d}", font=font(11), fill=(240, 230, 210))
        frames.append(r.convert("RGB"))
    pal = frames[3].quantize(colors=255)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=67, loop=0, optimize=True)
    return os.path.getsize(path)


# ===================================================================== write
m = measures()
checks = META.get("checks", {})
lines = ["Vent pump (sae-vent-pump), 3x3, four directions: the model -- concept/vent-pump/model/vent_pump.py",
         "rendered by tools/blender/render.sh --ports --icon on the GPU; packed by pack.py", ""]
lines.append("PACK CHECKS (pack.py, meta.json 'checks', per direction)")
for d in DIRS:
    c = checks.get(d, checks)
    lines.append(f"  {d}:")
    for k_, v in c.items():
        lines.append(f"    {k_}: {v}")
lines.append("")
lines.append("FINISH AND TONE (finish.py; tonal.py) -- vanilla: black 5-12 %, ratio ~0.5, darkchr 7-15; "
             "p50 41-63 (the mod ~75-81), p95 143-189")
pj = sidecar_pumpjack()
pj_path = os.path.join(RUN, "pumpjack-f0.png")
pj.save(pj_path)
pjb = Image.open(f"{ENT}/pumpjack/pumpjack-base.png").convert("RGBA").crop((0, 0, 261, 273))
pjb_path = os.path.join(RUN, "pumpjack-base-north.png")
pjb.save(pjb_path)
for t, p in (("vanilla pumpjack (base and horsehead, f0)", pj_path), ("vanilla pumpjack base (north)", pjb_path),
             ("adopted plate, north (shipped)", os.path.join(ADOPTED, "base-north.png"))):
    lines.append(f"  {t:44s} {tool('finish.py', p)}")
    lines.append(f"  {'':44s} {tool('tonal.py', p)}")
for d in DIRS:
    for what, p in (("plate", os.path.join(SHEETS, f"base-{d}.png")),
                    ("still (frame 0, idle)", os.path.join(RENDERS, f"still-{d}.png"))):
        lines.append(f"  the model, {d}, {what:22s} {tool('finish.py', p)}")
        lines.append(f"  {'':44s} {tool('tonal.py', p)}")
lines.append("")
lines.append("OUTLINE (the plate, alpha over 128)")
for d in DIRS:
    lines.append(f"  {d}: footprint covered {m[f'cover-{d}'] * 100:.1f} %; rises {m[f'rise-{d}']:.2f} tile above the "
                 f"north edge; mass {m[f'bbox-{d}'][0]:.2f} wide x {m[f'bbox-{d}'][1]:.2f} tall tiles")
lines.append("")
lines.append("MOTION AND LIGHT (working, every frame against frame 0)")
for d in DIRS:
    sh, bb = m[f"lit-{d}"]
    lines.append(f"  {d}: moving / opaque {m[f'moving-{d}'] * 100:.1f} %; working orange / opaque {sh * 100:.1f} % in "
                 f"(x0, y0, x1, y1 tiles) {tuple(round(v, 2) for v in bb) if bb else None}")
lines.append("")
lines.append("CIRCUIT CONNECTOR (inherited pumpjack: by_pixel(3, -28.5), every direction)")
for d in DIRS:
    lines.append(f"  {d}: the plate covers {m[f'connector-{d}'] * 100:.0f} % of a 20 px box round it")
lines.append("")
pm = subprocess.run([sys.executable, os.path.join(REPO, "concept", "ballast-drill", "model", "measure_ports.py"),
                     os.path.join(SHEETS, "ports"), os.path.join(RUN, "ports-vs-am3.png")],
                    capture_output=True, text=True)
lines.append("PORTS against assembler 3's outline (concept/ballast-drill/model/measure_ports.py; far_px 1 or less)")
lines += ["  " + ln for ln in pm.stdout.strip().splitlines()]
lines.append("")
if args.collide and os.path.isfile(args.collide):
    lines.append("COLLIDE (vent_pump.py --collide; facing north: the model turns rigidly)")
    lines += ["  " + ln for ln in open(args.collide).read().splitlines() if "moving:" in ln or "model:" in ln
              or "CLASH" in ln]
    lines.append("")
if args.render_log and os.path.isfile(args.render_log):
    lines.append("RENDER LOG (render.sh)")
    lines += ["  " + ln for ln in open(args.render_log).read().splitlines()
              if ln.startswith(("render device", "checks", "exit", "ports", "icon"))]
    lines.append("")
lines.append("LAYERS (sheets/; 320 x 320 canvas, the origin at (160, 160))")
lines.append(f"  {'sheet':22s} {'frames':>6s} {'line':>5s} {'frame w x h':>12s}  shift (tiles)")
for n_, v in META.items():
    if n_ == "checks":
        continue
    w, h = v["size"]
    lines.append(f"  {n_:22s} {v.get('frames', 1):6d} {v.get('line_length', 1):5d} {w:5d} x {h:<5d}  "
                 f"{v['shift'][0]:+.5f}, {v['shift'][1]:+.5f}")
for n_, v in PMETA.items():
    if n_ == "checks" or not isinstance(v, dict) or "size" not in v:
        continue
    lines.append(f"  ports/{n_:16s} {1:6d} {1:5d} {v['size'][0]:5d} x {v['size'][1]:<5d}  "
                 f"{v['shift'][0]:+.5f}, {v['shift'][1]:+.5f}")
txt = "\n".join(lines) + "\n"
open(os.path.join(HERE, "measures.txt"), "w").write(txt)

c1, c2 = compare(1), compare(2)
c1.save(os.path.join(HERE, "compare-plates.png"))
c2.save(os.path.join(HERE, "compare-plates-2x.png"))
size = gif(os.path.join(HERE, "motion-1x.gif"))

Wd = 2600
parts = [heading("VENT PUMP -- the model: review (nothing here is signed off)", Wd, 26),
         para(["vent_pump.py: the gas-lift wellhead from its spec and the adopted plates (v4-sheet.png, "
               "rotation-strip-v2.png), to the Core standard of the Reaction Plant's round 5.",
               "64 px a tile. The model's pipes stop at the footprint in bare fittings; the engine's pipe pictures (ours, "
               "assembler 3's outline) carry them on, and vanilla's covers cap them when nothing is connected.",
               "Idle, the sight port is dark and the seams unlit (spec 9); working, the melt runs toward the outlet "
               "and the riser's gaskets glow (spec 7). Melt out north, helium in south, turned with the building."], Wd),
         heading("Facing north beside vanilla's pumpjack and the adopted plate, 1x", Wd), c1,
         heading("... and at 2x", Wd), c2,
         heading("The adopted plate and the model in every direction, 1x", Wd), compare_all(1),
         heading("Idle and working, every direction, 2x (shadow, pictures and covers, lamp tinted)", Wd), states(2),
         heading("The glow alone, 2x", Wd), glow_alone(2)]
for d in DIRS:
    parts += [heading(f"melt-{d}: 16 frames, 4x, working layer over the plate", Wd, 16), strip(d, "melt", 4)]
parts += [heading("meter-north: 16 frames, 4x (the disc turns a third of a turn a loop)", Wd, 16),
          strip("north", "meter", 4),
          heading("The inherited circuit connector (cyan ring): spec 17 asks that the stack not cover it", Wd),
          connector_panel(2),
          heading("The icon (spec 16: the stack and its pipes, the base dropped; cold end left, hot end right)", Wd), icon_panel(),
          heading("Measures (measures.txt)", Wd), para(txt.splitlines(), Wd, 12)]
rev = stack(parts, gap=14)
rev.save(os.path.join(HERE, "review.png"))
dst = os.path.join(HERE, "sheets")
if os.path.isdir(dst):
    shutil.rmtree(dst)
shutil.copytree(SHEETS, dst)
for extra in ("ports-vs-am3.png",):
    if os.path.isfile(os.path.join(RUN, extra)):
        shutil.copy(os.path.join(RUN, extra), os.path.join(HERE, extra))
print("review:", os.path.join(HERE, "review.png"), rev.size, "gif bytes", size)
