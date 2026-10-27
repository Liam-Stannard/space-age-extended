#!/usr/bin/env python3
"""Vent Pump, round 3, artist B (concepts 8, 9, 10, 19): sheets, GIFs, path overlays, measures, contact sheets.

  python3 vpb3_sheets.py <full-dir> <cmap-dir> <out-dir> [--only 08,09,10,19]

Round 2's vpb_sheets.py with round 3's additions: a PATH OVERLAY at 2x on every sheet (helium
in, molten kamacite, spent/recovered gas, in helium-colour.txt's overlay colours, from the
routes each vpb3_<n>_*.py projects through the real camera into meta.json), the one-sentence
helium pitch, and the pipe-end check (vpb3_kit.check_ends(), in meta.json): every pipe, line,
hose and cable with the part each end sits in. The measures are taken as in round 2, at 1x:

  cover   plate alpha > 128 inside the 3x3 footprint (the bar is 92 %)
  rise    the plate's top over the footprint's north edge, in tiles
  glow    pixels the melt lights, working frame 0 against idle, of the opaque plate
  moving  pixels that change by > 30 over the loop, of the opaque plate
  cold    pale blue pixels in the plate (B > R + 12, B > G + 6, luma > 80): the bar is 0
  tonal   p5, p50, p95 of the plate (alpha > 200)

Writes, in <out-dir>:
  <n>-<slug>.png              the sheet
  <n>-<slug>-paths.png        the path overlay alone, 2x
  <n>-<slug>-1x.gif           the working loop at game scale, ports joined (< 5 MB)
  <n>-<slug>-2x.gif           the same at 2x (keep out of git)
  contact-sheet-b.png         round 2 and round 3 of 8, 9, 10, 19 beside vanilla's pumpjack, the adopted
                              plate and round 1's model
  contact-sheet.png           all eight, round 2 beside round 3, when artist A's contact-sheet-a.png and
                              four round-3 1x GIFs are here
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
R2 = os.path.join(HERE, "..", "round-2")


def references():
    """Vanilla's pumpjack (working frame 0), round 1's model and the adopted plate, each cropped
    from round 1's compare-plates.png (1x, the same ground) -- one panel each."""
    cp = Image.open(os.path.join(VP, "model", "compare-plates.png")).convert("RGBA")
    out = []
    for i, cap in ((0, "vanilla pumpjack 3x3 (frame 0)"), (1, "the adopted plate (v4, shipped)"),
                   (3, "round 1's model (set aside), working")):
        out.append((cap, cp.crop((336 * i, 46, 336 * i + 320, 430))))
    return out


def gif_frame0(path):
    im = Image.open(path)
    im.seek(0)
    return im.convert("RGBA")


# ---------------------------------------------------------------- the path overlay
OVER = {"he": ((180, 140, 255), "helium in"), "melt": ((255, 128, 48), "molten kamacite"),
        "spent": ((76, 214, 192), "spent / recovered gas")}


def overlay(base2, meta, off, k=2):
    """The working frame at 2x, dimmed; the routes over it in their colours with arrows, the
    spent gas dashed; the numbered chain on top."""
    im = Image.blend(base2.convert("RGB"), Image.new("RGB", base2.size, (24, 22, 20)), 0.5).convert("RGBA")
    d = ImageDraw.Draw(im)
    order = {"melt": 0, "spent": 1, "he": 2}
    for R in sorted(meta["routes"], key=lambda R: order[R["kind"]]):
        col = OVER[R["kind"]][0]
        P = [((x - off[0]) * k, (y - off[1]) * k) for x, y in R["px"]]
        segs = []
        if R["kind"] == "spent":                          # dashed: 14 px on, 8 px off
            acc, on, cur = 0.0, True, [P[0]]
            for a, b in zip(P, P[1:]):
                L = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
                acc += L
                if on:
                    cur.append(b)
                if acc > (14 if on else 8):
                    if on and len(cur) > 1:
                        segs.append(cur)
                    on, acc, cur = not on, 0.0, [b]
            if on and len(cur) > 1:
                segs.append(cur)
        else:
            segs = [P]
        for sgm in segs:
            d.line(sgm, fill=(12, 10, 8), width=7, joint="curve")
        for sgm in segs:
            d.line(sgm, fill=col, width=3, joint="curve")
        acc = 0.0                                          # arrows every ~40 px, pointing downstream
        for a, b in zip(P, P[1:]):
            L = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
            acc += L
            if acc >= 40 and L > 0.5:
                acc = 0.0
                ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                tip = (b[0] + ux * 5, b[1] + uy * 5)
                l_ = (b[0] - ux * 6 - uy * 6, b[1] - uy * 6 + ux * 6)
                r_ = (b[0] - ux * 6 + uy * 6, b[1] - uy * 6 - ux * 6)
                d.polygon([tip, l_, r_], fill=col, outline=(12, 10, 8))
    labels = [dict(L, px=[L["px"][0] - off[0], L["px"][1] - off[1]]) for L in meta["labels"]]
    numbered(im, labels, k)
    leg = Image.new("RGBA", (im.width, 26), BG)
    dl = ImageDraw.Draw(leg)
    x = 8
    for kind in ("he", "melt", "spent"):
        col, name = OVER[kind]
        dl.line([(x, 13), (x + 30, 13)], fill=col, width=4)
        text(dl, (x + 36, 5), name, 12)
        x += 60 + int(font(12).getlength(name))
    return vstack([im, leg], 0)


# ---------------------------------------------------------------- the concepts' words
COMMON_FINISH = ("The Reaction Plant's round-5 finish (worn_paint over materials.layered, a paint per unit, "
                 "vanilla's warmth, rust only in seams, at the feet and down from bands). The casing is "
                 "spec 3.3's iron-nickel grey-brown (#57524A), refractory or heat-stained steel where the melt "
                 "is held or runs. The helium side carries helium-colour.txt's family colour (artist A's, the "
                 "first written): grey-violet lagging #7E7488, pale violet bands #B6A6C8 with #3A3440 edges, "
                 "bare-steel flanges; the helium vessels in the dark violet #3A3440 with pale violet bands. No "
                 "frost, rime, ice or blue (measured: the cold count). The only light is the melt, #D96B29 to "
                 "#FF9E52, only where it is seen; the status lamp is an unlit amber lens.")
S = {
    "08": dict(slug="the-gas-lift-tower", name="THE GAS-LIFT TOWER",
               helium="Helium is blown into the melt at the tower's foot and its bubbles carry the melt up the "
                      "glass riser; the player sees the violet line run through the racing flow meter to the "
                      "sparger ring, the bubbles climb faster in each of the two charges a loop, and the "
                      "recovered helium come back down the tower to the compressor, the receiver and the line.",
               read="Round 2's tower: a tall riveted shaft over the vent, the glass riser in the slot down its "
                    "south face with the melt and the dark helium bubbles climbing, the head tank and float "
                    "chamber on top, the lagged downcomer down the north-west. New: the grey-violet helium line "
                    "from the south nozzle through the stop valve and a big flow meter to a tee and on to the "
                    "sparger ring; the recovery loop in violet (head tank, down the tower's east side, the "
                    "compressor, over the inlet to the receiver in the south-west, back into the tee).",
               motion=["Charges: helium is let in twice a loop. In each, the flow meter's rotor races (two "
                       "turns a loop, most of them in the charges), the tee's gauge swings up, the bubbles in "
                       "the riser climb faster (their climb follows the meter) and the riser's glow lifts.",
                       "Float: the separator float lever rocks twice a loop, once a charge.",
                       "Recovery: the compressor's coupling turns three times a loop; the receiver's gauge "
                       "swings with its strokes.",
                       "Idle: still and unlit; the meter stops, the riser dark slag with its bubbles."],
               changes=["The inlet: in round 2 the line was bare steel and the meter a small brass can; now the "
                        "lagged violet line and a turning meter on it, the gauge on the tee.",
                        "Recovery made honest: round 2's recovery line ended at the compressor and the "
                        "compressor's pipe at the inlet; now head tank -> compressor -> receiver -> tee, every "
                        "leg ending at a device.",
                        "Removed: round 2's west seal-pot pipe (tank to a box that used nothing) and the hose "
                        "from the green tank that ended in air beside the tower; the two west drums stand "
                        "unpiped, a tool chest beside them.",
                        "Corners broken: the north-east, south-east and north-west units set back from the "
                        "corners (foundations to 1.38-1.4 t)."]),
    "09": dict(slug="the-rotary-vane-pump", name="THE ROTARY VANE PUMP",
               helium="Helium is the seal gas, held over the melt in the shaft seal and the vane chamber so the "
                      "melt cannot creep out along the shaft; the player sees the violet line run through the "
                      "turning meter into the manifold and on to the seal and the chamber, and twice a loop the "
                      "purge valve on the casing ticks the spent gas off to the receiver while the meter races "
                      "and the gauges swing to make it up.",
               read="Round 2's pump: the ribbed cast drum over the vent, north-south, the open drive on the "
                    "south (motor on its stool, brake drum and coupling turning), the sight chest with its "
                    "lit port, the gooseneck to the north nozzle. New: the grey-violet helium line under the "
                    "motor stool to a flow meter and the dark violet seal-gas manifold; two violet lines up "
                    "to the shaft seal housing and the top of the vane chamber; the purge valve on the "
                    "casing's east shoulder with its line to the spent-gas receiver in the east; the reserve "
                    "bottles' header into the manifold.",
               motion=["Purge: twice a loop the purge valve's red lever snaps open, then shut.",
                       "Make-up: just after each purge the manifold's meter races (two turns a loop, most "
                       "of them then) and its two gauges swing up; the receiver's gauge kicks with the purge.",
                       "Drive: brake drum and coupling turn twice a loop. Sight port: the melt runs past.",
                       "Idle: still, the port dark, the meter stopped, the purge shut."],
               changes=["The helium was a bare pipe to a grey box with three thin pipes; now the violet line, "
                        "a turning meter, a dark violet manifold with gauges, two violet lines to the seal and "
                        "the chamber, and a purge to a receiver: the gas's way in and out are both seen.",
                        "The motor stool's legs set back so the helium line passes under it clear (in round 2 "
                        "it ran through the east leg).",
                        "Removed: the third seal-gas pipe (round 2's, to the north cover, routed through the "
                        "casing's side); the south-west drum's pipe into the inlet line and the regulator on "
                        "it (the south-west is now a stop station and a spare-vane crate, cabled to the "
                        "motor); the east oil drums and their hose that ended at nothing.",
                        "The east is now the spent-gas receiver; a power trunk joins the transformer to the "
                        "starter. Corners set back to 1.4-1.42 t."]),
    "10": dict(slug="the-twin-cylinder-lift", name="THE TWIN CYLINDER LIFT",
               helium="Helium is the piston: let into the head of a full cylinder it drives the melt up the dip "
                      "tube and out; the player sees the violet lines climb from the switching chest to each "
                      "head, the admit valve kick open while the meter races and that side's gauge swings, then "
                      "that cylinder's window empty, and the spent helium leave by the vent header to the "
                      "recovery receiver and compressor and come back to the chest.",
               read="Round 2's lift: two tall refractory cylinders over the vent with their level windows, "
                    "yellow actuators with red and green flags on the domed heads, the catwalk and ladder, "
                    "the dip tubes over the heat-stained header to the north nozzle. New: the switching chest "
                    "in dark violet with a gauge a side, the violet lines from it up over the catwalk to each "
                    "admit valve, the violet vent header arching from both vent valves over the top to the "
                    "recovery receiver (north-east), the return down the east side to the recovery "
                    "compressor (south-east) and its line into the chest, the buffer receiver (south-west).",
               motion=["Each half loop (A at 0.5, B at 0): the admit valve's rod strokes up and its red flag "
                       "turns; the meter races (two turns a loop, most in the two charges) and that side's "
                       "gauge on the chest swings up; then that cylinder's window empties over the half loop "
                       "(the melt surging out) and burns brighter. Its vent valve (green) is shut meanwhile, "
                       "the other cylinder's open, that window filling.",
                       "Recovery compressor: three turns a loop; the receivers' gauges swing.",
                       "Idle: stopped as at frame 0 (A empty and venting, B full), windows dark, meter still."],
               changes=["The helium side was bare pipes; now the violet line, a turning meter, gauges per side.",
                        "The vent lines were loose in round 2 (the west one ended in air over the north-west "
                        "drain pot, the east at a point by the receiver); now both end in the recovery receiver, "
                        "which returns to the compressor, which returns to the chest.",
                        "Removed: the north-east instrument box and its hose (it ended in the cylinder's side "
                        "for no use); the SE 'pilot-air' role (the compressor is now the helium's recovery "
                        "compressor, its drum the receiver it discharges from).",
                        "Added a relief pipe from the receiver to its stack (round 2's stack stood alone). "
                        "Corners set back to 1.4-1.42 t."]),
    "19": dict(slug="the-peristaltic-hose-pump", name="THE PERISTALTIC HOSE PUMP",
               helium="Helium is a gas cap over the melt in the vent chamber, pressing it up the suction riser so "
                      "the hose never runs dry; the player sees the violet line through the meter into the "
                      "pressure dome's vessel and over the hose into the rotary union on the hub (down the "
                      "rotor's hollow shaft), the black dome sink as the rollers draw and rise as the meter races "
                      "to refill it, and the relief valve tick the excess to the recovery receiver.",
               read="Round 2's pump: the round cast track on its ribbed pedestal, the black armoured hose in a U, "
                    "the ochre three-roller rotor, the suction riser in on the north-west, the sight glass and "
                    "north nozzle out on the north-east. New: the grey-violet line from the south nozzle up "
                    "through the stop valve and a flow meter into a dark violet vessel in the south-west "
                    "crowned with a black diaphragm dome (the gas cap's accumulator); a violet line from it "
                    "over the hose to a rotary union on the rotor hub; a relief valve and a recovery receiver "
                    "on the east.",
               motion=["Draw and refill, once a loop (one roller pitch): as a roller draws a slug in, the dome "
                       "sinks; then the meter races (two turns a loop, most in the refill), the dome rises "
                       "back and the gauge swings; at the top the relief valve's lever ticks and the "
                       "receiver's gauge kicks.",
                       "Rotor: a third of a turn a loop; bulges travel round the U ahead of the rollers. The "
                       "sight glass pulses as each slug passes. Drive coupling: three turns a loop.",
                       "Idle: the rotor stops squeezing where it is; the dome, meter and valve still."],
               changes=["Round 2's helium was a bare pipe into the pedestal, unseen at 1x; the gas cap is now "
                        "fed from above through the hub's rotary union (the hollow rotor shaft goes down to the "
                        "vent chamber), so the violet line crosses the building to where it works.",
                        "Added the pressure dome (the brief's 'gas cap's pressure dome flexing as the rollers "
                        "draw') and the relief to a recovery receiver.",
                        "Removed: the south-west buffer tank's two bare pipes (one into the track wall for a "
                        "'housing purge', one into the inlet); the east lube-point box and its hose; the "
                        "north-west cabinet's cable that ran into the ground; the hub's hazard bar moved off "
                        "centre to clear the union. Re-tied: the cabinet's cable to the lube unit, the "
                        "starter's to the motor, the gearbox's shaft to the coupling.",
                        "Corners set back to 1.42 t."]),
}

MEAS = {}
FIRST = {}
SUN = {"08": 13.5, "09": 12.0, "10": 13.5, "19": 12.0}


def chain_lines(meta):
    return [f"{L['n']}. {L['text']}" for L in sorted(meta["labels"], key=lambda L: L["n"])]


def pipe_lines(meta):
    out = []
    for P in meta["pipes"]:
        e = P["ends"]
        out.append(f"{'OK' if P['ok'] else 'LOOSE'} -- {P['name']}: from {e[0]['to'] or 'AIR'} to {e[1]['to'] or 'AIR'}")
    return out


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
    m["pipes"] = len(meta["pipes"])
    m["pipes_loose"] = sum(1 for P in meta["pipes"] if not P["ok"])
    MEAS[n] = m
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
    paths = overlay(g_w2[0], meta, bb1)
    paths_c = captioned(paths, "PATH OVERLAY, 2x: violet helium in, orange melt, dashed teal spent / recovered gas")
    paths_c.convert("RGB").save(os.path.join(OUT, f"{n}-{o['slug']}-paths.png"))
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
    RC = (16, 40, 344, 352)
    rots = [captioned(with_ports(work1[0], "north", 1).crop(RC), "north (as built)")]
    for dn in ("east", "south", "west"):
        rots.append(captioned(with_ports(load(os.path.join(d, f"rot-{dn}.png"), 1), dn, 1).crop(RC), dn))
    kf = [int(i * nf / 8) for i in range(8)]
    keys = [g_w1[i] for i in kf]
    r1 = hrow([captioned(g_w2[0], "WORKING, 2x (frame 0), vanilla pipes joined"),
               captioned(g_i2, "IDLE, 2x (stopped, unlit)")])
    r2 = hrow([paths_c, captioned(chain, "THE CHAIN, NUMBERED (2x)")])
    r3 = hrow([captioned(mmg, "MOTION MAP, 2x: magenta moves, orange is the melt's light"),
               captioned(cmg, "COLOUR MAP, 2x")])
    rot_grid = vstack([hrow(rots[:2], 10), hrow(rots[2:], 10)], 10)
    refs = references()
    r2g = os.path.join(R2, f"{n}-{o['slug']}-1x.gif")
    r2c = [captioned(gif_frame0(r2g), "round 2, working")] if os.path.exists(r2g) else []
    beside = hrow([captioned(g_w1[0], f"{int(n)}. {o['name'].title()}, round 3, working"), captioned(g_i1, "idle")]
                  + r2c + [captioned(im, cap) for cap, im in refs], 14)
    W = max(r1.width, r2.width, r3.width, rot_grid.width, beside.width) + 20
    head_lines = wrap("Round 3, artist B: helium seen at work, honest plumbing. A lit Blender concept on the GPU in "
                      "the Reaction Plant's finish; 3x3 on the vent, helium-3 in on the south face, molten kamacite "
                      "out on the north, straight through; each port's own flange at the edge on assembler 3's "
                      "pipe axis (z 0.42), the same for all eight, a vanilla pipe on the next tile. Not a model, "
                      "nothing adopted, nothing in graphics/.", 13, W - 20)
    head_ = Image.new("RGBA", (W, 44 + 18 * len(head_lines)), BG)
    dd = ImageDraw.Draw(head_)
    text(dd, (10, 6), f"VENT PUMP, ROUND 3 -- {int(n)}. {o['name']}  (3 x 3)", 22, HEAD, True)
    for i, ln in enumerate(head_lines):
        text(dd, (10, 40 + 18 * i), ln, 13, SUB)
    meas = (f"Cover {m['cover_pct']} % of the footprint (plate alpha > 128, 1x; the bar is 92 %). Rise over the "
            f"north edge {m['rise_tiles']:+.2f} tile. Glow (pixels the melt lights, frame 0) {m['glow_pct']} % of "
            f"the opaque plate. Moving share {m['moving_pct']} %. Cold (pale blue) pixels in the plate: "
            f"{m['cold_px']} (the bar is none). Tonal (plate): p5 {m['p5']}, p50 {m['p50']}, p95 {m['p95']} (the "
            f"mod ~75-81; vanilla p95 143-189); sun {SUN[n]}. Pipes, lines, hoses and cables checked: {m['pipes']}, "
            f"loose ends {m['pipes_loose']}. {nf} frames. GIF 1x {m['gif_1x_mb']} MB, 2x {m['gif_2x_mb']} MB.")
    sheet = vstack([head_, block("WHAT HELIUM DOES", [o["helium"]], W), r1, r2,
                    block("THE CHAIN (the numbers on the plates above)", chain_lines(meta), W, tight=True),
                    r3, block("THE READ", [o["read"]], W),
                    captioned(rot_grid, "FOUR ROTATIONS, 1x (working frame 0; the engine turns the ports with it)"),
                    captioned(beside, "BESIDE ROUND 2, VANILLA, THE ADOPTED PLATE AND ROUND 1, 1x (64 px a tile)"),
                    captioned(hrow(keys, 6), f"KEY FRAMES, 1x: frames {', '.join(map(str, kf))} of {nf}"),
                    hrow([captioned(palette(os.path.join(CMAP, n, "colourmap.json"), used, 520), "PALETTE")]),
                    block("MOTION (for spec 6.2)", o["motion"], W),
                    block("CHANGED FROM ROUND 2", o["changes"], W),
                    block("EVERY PIPE GOES SOMEWHERE (vpb3_kit.check_ends: each end inside a part, or within "
                          "0.04 t of one, the run's own fittings not counted)", pipe_lines(meta), W, size=12,
                          tight=True),
                    block("FINISH", [COMMON_FINISH], W),
                    block("MEASURED (64 px a tile)", [meas], W)], width=W)
    pad = Image.new("RGBA", (sheet.width + 20, sheet.height + 20), BG)
    pad.alpha_composite(sheet, (10, 10))
    path = os.path.join(OUT, f"{n}-{o['slug']}.png")
    pad.convert("RGB").save(path)
    print(path, pad.size, m)


def contact_row(items, gap=16):
    return hrow([captioned(im, cap, 12) for cap, im in items], gap)


def contact(name, rows_items, title, note):
    rows = [contact_row(references())] + [contact_row(r) for r in rows_items]
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


def pair_rows(nums, here_dir):
    """For each concept number: (round 2 frame 0, round 3 frame 0), from the two rounds' 1x GIFs."""
    r2, r3 = [], []
    for num in nums:
        g3 = sorted(glob.glob(os.path.join(here_dir, f"{num}-*-1x.gif")))
        g2 = sorted(glob.glob(os.path.join(R2, f"{num}-*-1x.gif")))
        if not g3:
            return None
        nm = os.path.basename(g3[0])[len(num) + 1:-7].replace("-", " ").title()
        if g2:
            r2.append((f"{int(num)}. {nm}, round 2", gif_frame0(g2[0])))
        r3.append((f"{int(num)}. {nm}, round 3", gif_frame0(g3[0])))
    return r2, r3


for n in args.only.split(","):
    build(n)
json.dump(MEAS, open(os.path.join(OUT, "measures-b.json"), "w"), indent=1)
if len(FIRST) == 4:
    b2, b3 = pair_rows(["08", "09", "10", "19"], OUT)
    b3 = [(f"{int(n)}. {S[n]['name'].title()}, round 3\ncover {MEAS[n]['cover_pct']} %, glow {MEAS[n]['glow_pct']} %, "
           f"moving {MEAS[n]['moving_pct']} %", FIRST[n]) for n in sorted(FIRST)]
    contact("contact-sheet-b.png", [b2, b3],
            "VENT PUMP, ROUND 3 -- ARTIST B: 8, 9, 10 AND 19, ROUND 2 ABOVE ROUND 3",
            "64 px a tile, one ground. Top: vanilla's pumpjack, the adopted plate, round 1's model. Middle: round 2 "
            "(frame 0 of its 1x GIFs). Bottom: round 3 (working frame 0).")
    a = pair_rows(["01", "02", "05", "07"], OUT)
    if os.path.exists(os.path.join(OUT, "contact-sheet-a.png")) and a is not None:
        a2, a3 = a
        contact("contact-sheet.png", [a2, a3, b2, b3],
                "VENT PUMP, ROUND 3 -- THE EIGHT CONCEPTS, ROUND 2 ABOVE ROUND 3",
                "64 px a tile. Top: vanilla's pumpjack, the adopted plate, round 1's model. Then artist A's 1, 2, 5 and 7 "
                "(round 2, round 3) and artist B's 8, 9, 10 and 19 (round 2, round 3); frame 0 of each 1x GIF.")
    else:
        print("contact-sheet.png not built: contact-sheet-a.png or artist A's four round-3 1x GIFs are not here yet")
