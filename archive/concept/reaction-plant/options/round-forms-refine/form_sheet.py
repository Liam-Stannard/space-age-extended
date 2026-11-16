#!/usr/bin/env python3
"""T06h: the refined casing's review sheet (a copy of round-forms/form_sheet.py, T06g; titles and notes changed).
T06g: one building form's review sheet and 1x GIF, from its four runs (render.sh, one a direction) and measure.py.
(T06e's take_sheet.py, with the chain drawn through each connection's wall sleeve and riser.)

  python3 form_sheet.py <full-dir> <form> <out-dir> [--probe <probe.json>]

<full-dir> holds run-<d>/ (tools/blender/render.sh's output for forms.py with RP_FORM and RP_DIRECTION)
and measure-<d>/measures.json (tools/blender/measure.py on each run). Everything is drawn from the PACKED
sheets placed by their meta.json shifts, as the engine places them (the four-way review_sheet.py's
compositor, model/four-way/review_sheet.py). Writes into <out-dir>:

  form-<K>.png     the lit sheet: per direction, idle at 2x (no recipe: all three boxes, vanilla's covers),
                   working at 2x (precipitation: vanilla pipes joined to the two inputs, the legs lit), the
                   input-to-output chain labelled over the 2x plate with each connection's run traced from
                   the pipe to its vessel, the motion map, and measure.py's figures
  form-<K>-1x.gif  every motion together at 1x, the four directions side by side (the 24-frame loops twice,
                   the press once in frames 24-39), 14 fps

Every figure quoted on the sheet is measure.py's (measures.json); the legs' and press's pixel counts are the
model's own --probe (frame 0 of the layer alone, px over half alpha at 4x), not a measure.py figure.
"""
import json
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import form_plans as takes  # noqa: E402

FULL = KEY = OUTD = None
PROBE, TK = {}, None
FD = os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data")
ENT = f"{FD}/base/graphics/entity"
PIPE, COVER = f"{ENT}/pipe/", f"{ENT}/pipe-covers/pipe-cover-"
DIRS = ("north", "east", "south", "west")
DEG = dict(zip(DIRS, (0, 90, 180, 270)))
PPT = 64
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT, SUB, HEAD = (228, 222, 210), (175, 168, 156), (240, 200, 120)
GREEN, AMBER = (90, 255, 110), (255, 196, 60)
NF, PRESS_NF = 24, 16
FACE = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
NAME = {"N": "north", "E": "east", "S": "south", "W": "west"}
LOOPS = ("drive", "coupling-compressor", "coupling-dosing", "coupling-pump", "gauge-reactor-upper",
         "gauge-reactor-lower", "gauge-scrubber", "drip")
ZA = 0.42


def turn(c):
    x, y, f = c
    return (-y, x, "NESW"[("NESW".index(f) + 1) % 4])


CONNS = {"north": [(-1, -2, "N"), (1, -2, "N"), (0, 2, "S")]}
for a_, b_ in zip(DIRS, DIRS[1:]):
    CONNS[b_] = [turn(c) for c in CONNS[a_]]


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
                              size)


class Sheets:
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
        (add_light if add else place)(canvas, im, centre, k)


def place(canvas, im, centre, k=1):
    if k != 1:
        im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    x, y = round(centre[0] - im.width / 2), round(centre[1] - im.height / 2)
    canvas.alpha_composite(im, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))


def add_light(canvas, im, centre, k=1):
    if k != 1:
        im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    x, y = round(centre[0] - im.width / 2), round(centre[1] - im.height / 2)
    r, g, b, a = im.split()
    lit = Image.merge("RGB", [Image.composite(c, Image.new("L", im.size, 0), a) for c in (r, g, b)])
    region = canvas.crop((x, y, x + im.width, y + im.height)).convert("RGB")
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
    x, y, f = conn
    dx, dy = FACE[f]
    sp = sprite(PIPE + ("pipe-straight-vertical.png" if f in "NS" else "pipe-straight-horizontal.png"), k)
    place(canvas, sp, (origin[0] + (x + dx) * PPT * k, origin[1] + (y + dy) * PPT * k))


def cover_at(canvas, origin, k, conn):
    x, y, f = conn
    dx, dy = FACE[f]
    place(canvas, sprite(COVER + NAME[f] + ".png", k), (origin[0] + (x + dx) * PPT * k, origin[1] + (y + dy) * PPT * k))


def machine(sh, canvas, origin, k, f=0, press=0, working=False, conns=(), covers=(), lamps=True):
    behind = lambda c: c[1] + FACE[c[2]][1] <= 0
    sh.draw(canvas, origin, "shadow", 0, k)
    for c in conns:
        if behind(c):
            pipe_at(canvas, origin, k, c)
    for c in covers:
        if behind(c):
            cover_at(canvas, origin, k, c)
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
    for c in conns:
        if not behind(c):
            pipe_at(canvas, origin, k, c)
    for c in covers:
        if not behind(c):
            cover_at(canvas, origin, k, c)
    return canvas


def panel(k, w_tiles=7.6, h_tiles=8.4, oy_tiles=4.4):
    size = (int(w_tiles * PPT * k), int(h_tiles * PPT * k))
    origin = (size[0] // 2, int(oy_tiles * PPT * k))
    return ground(size, origin, k), origin


def label(im, text, sub=None, size=22):
    top = int(size * 2.3) if sub else int(size * 1.4)
    out = Image.new("RGBA", (im.width, im.height + top), BG)
    d = ImageDraw.Draw(out)
    d.text((6, 4), text, font=font(size, True), fill=TEXT)
    if sub:
        d.text((6, 6 + size * 1.15), sub, font=font(int(size * 0.8)), fill=SUB)
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


def stack(ims, gap=20, pad=20):
    w = max(i.width for i in ims) + 2 * pad
    out = Image.new("RGBA", (w, sum(i.height for i in ims) + gap * (len(ims) - 1) + 2 * pad), BG)
    y = pad
    for i in ims:
        out.alpha_composite(i, (pad, y))
        y += i.height + gap
    return out


def heading(text, width, size=34):
    im = Image.new("RGBA", (width, int(size * 1.5)), BG)
    ImageDraw.Draw(im).text((0, 4), text, font=font(size, True), fill=HEAD)
    return im


def para(lines, width, size=22):
    im = Image.new("RGBA", (width, (size + 9) * len(lines) + 8), BG)
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        d.text((0, 3 + i * (size + 9)), ln, font=font(size), fill=TEXT)
    return im


def screen(p_, deg, origin, k):
    x, y, z = p_
    a = -math.radians(deg)
    e, n = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
    return origin[0] + e * PPT * k, origin[1] - (n + z * 0.5) * PPT * k


# ---------------------------------------------------------------- the chain, from the take's own plan
def chain_points():
    """The input-to-output chain (model space): each stop's label and point, in the order the fluid goes."""
    L = TK.get("lift", {})
    d = TK["drum"]
    dz = d.get("z", 0.5) + L.get("feed_drum", 0) + d.get("r", 0.48)
    drum = (((d["x0"] + d["x1"]) / 2, d["y"], dz) if d["kind"] == "ew"
            else (d["x"], (d["y0"] + d["y1"]) / 2, dz))
    c = TK["compressor"]
    comp = (c["bottle"][0], c["bottle"][1], 1.1 + L.get("compressor", 0)) if c.get("kind") == "v" else \
        ((c["bottle"][0] + c["bottle"][1]) / 2, c["bottle"][2], 0.85 + L.get("compressor", 0))
    (rx, ry), (dx, dy) = TK["legs"]
    reactor = (TK["reactor"][0], TK["reactor"][1], 2.6)
    st = (TK["settle"][0], TK["settle"][1], 1.2 + L.get("settling", 0))
    pr = (TK["press"][0], TK["press"][1], 1.3)
    ry_, rz_ = TK.get("recv_yz", (-2.04, 0.47))
    rv = ((TK["receiver"][0] + TK["receiver"][1]) / 2, ry_, rz_ + 0.4 + L.get("receiver", 0))
    return drum, comp, (rx, ry, 1.5), reactor, (dx, dy, 1.5), st, pr, rv


def conn_path(k):
    """Connection k's run, model space, from the pipe tile outside to its user: the wall it enters through its
    sleeve, then the riser up out of the roof or deck into the vessel over it (or, with no riser, the vessel
    standing right behind the wall)."""
    sgn = 1 if k < 2 else -1
    x = (-1.0, 1.0, 0.0)[k]
    d = TK["walls"][k]
    pts = [(x, sgn * 3.0, 0.42), (x, sgn * d, 0.42)]
    rs = [r_ for r_ in TK["building"].get("risers", ()) if abs(r_[0] - x) < 0.01 and r_[1] * sgn > 0]
    if rs:
        x_, y_, z0, z1 = rs[0][:4]
        pts += [(x_, y_, 0.42), (x_, y_, z1)]
    else:
        drum, comp, _, _, _, _, _, rv = chain_points()
        pts += [(rv[0], rv[1], 0.6)]
    return pts


CH_COL = (255, 238, 170)
RUN_COL = {"solution": (255, 214, 90), "gas": (120, 230, 255), "output": (255, 120, 200)}


def arrow(dr, a, b, col, w=5, head=20):
    dr.line([a, b], fill=col, width=w)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    dr.polygon([b, (b[0] - head * math.cos(ang - 0.4), b[1] - head * math.sin(ang - 0.4)),
                (b[0] - head * math.cos(ang + 0.4), b[1] - head * math.sin(ang + 0.4))], fill=col)


def chain_panel(sh, d, model):
    k = 2
    g, origin = panel(k)
    machine(sh, g, origin, k, conns=CONNS[d][:2], lamps=False)
    dim = Image.new("RGBA", g.size, (20, 18, 16, 110))
    g.alpha_composite(dim)
    ov = Image.new("RGBA", g.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    deg = DEG[d]
    drum, comp, riser, reactor, down, st, pr, rv = chain_points()
    # each connection's run: from the pipe tile outside, in through its sleeve in the wall, up its riser into the
    # vessel that uses it (the output the other way)
    ends = {}
    for kk, name in enumerate(("solution", "gas", "output")):
        pts = [screen(p_, deg, origin, k) for p_ in conn_path(kk)]
        if name == "output":
            pts = pts[::-1]
        dr.line(pts, fill=RUN_COL[name] + (255,), width=12, joint="curve")
        ends[name] = (pts[0], pts[-1])
    stops = [("1", "solution in", None), ("2", "feed drum", drum), ("3", "gas in", None), ("4", "compressor", comp),
             ("5", "riser (gas lift)", riser), ("6", "reactor", reactor), ("7", "downcomer", down),
             ("8", "settling pot", st), ("9", "filter press", pr), ("10", "receiver", rv), ("11", "output", None)]
    P = {n: (screen(p_, deg, origin, k) if p_ else None) for n, _, p_ in stops}
    P["1"] = ends["solution"][0]
    P["3"] = ends["gas"][0]
    P["11"] = ends["output"][1]
    col = CH_COL + (255,)
    feed = ("2", "7")      # every form: the drum feeds the downcomer leg's foot
    for a, b in (("1", "2"), ("3", "4"), feed, ("4", "5"), ("5", "6"), ("6", "7"), ("7", "8"), ("8", "9"),
                 ("9", "10"), ("10", "11")):
        pa, pb = P[a], P[b]
        L = math.dist(pa, pb)
        if L < 40:
            continue
        sh_ = 22 / L
        arrow(dr, (pa[0] + (pb[0] - pa[0]) * sh_, pa[1] + (pb[1] - pa[1]) * sh_),
              (pb[0] - (pb[0] - pa[0]) * sh_, pb[1] - (pb[1] - pa[1]) * sh_), (30, 26, 20, 200), 9, 26)
        arrow(dr, (pa[0] + (pb[0] - pa[0]) * sh_, pa[1] + (pb[1] - pa[1]) * sh_),
              (pb[0] - (pb[0] - pa[0]) * sh_, pb[1] - (pb[1] - pa[1]) * sh_), col, 4, 20)
    for n, txt, _ in stops:
        x, y = P[n]
        cc = RUN_COL["solution"] if n in ("1", "2") else RUN_COL["gas"] if n in ("3", "4") else \
            RUN_COL["output"] if n in ("10", "11") else CH_COL
        dr.ellipse([x - 19, y - 19, x + 19, y + 19], fill=(25, 22, 18, 235), outline=cc + (255,), width=4)
        f_ = font(20, True)
        tw = dr.textlength(n, font=f_)
        dr.text((x - tw / 2, y - 12), n, font=f_, fill=cc + (255,))
    g.alpha_composite(ov)
    return g, stops


def motion_map(sh, d):
    k = 2
    frames = []
    for t in range(NF + PRESS_NF):
        g, origin = panel(k)
        machine(sh, g, origin, k, t % NF, t - NF if t >= NF else 0, working=True, lamps=False)
        frames.append(g)
    base = frames[0].convert("L")
    moved = Image.new("L", base.size, 0)
    for fr in frames[1:]:
        dif = ImageChops.difference(fr.convert("L"), base).point(lambda v: 255 if v > 30 else 0)
        moved = ImageChops.lighter(moved, dif)
    out = Image.blend(frames[0].convert("RGB"), Image.new("RGB", base.size, (40, 36, 32)), 0.55).convert("RGBA")
    red = Image.new("RGBA", base.size, (255, 70, 40, 255))
    out.paste(red, (0, 0), moved)
    return out


def fig_lines(m, d):
    dn = m["directions"][next(iter(m["directions"]))]
    c, t, fn, col = dn["coverage"], dn["tonal"], dn["finish"], dn.get("colour", {})
    mo = dn.get("motion") or {}
    js = dn.get("joins", [])
    tp, ts = t.get("plate", {}), t.get("still", {})
    lp = PROBE.get(f"legs-{d}")
    pp = PROBE.get(f"press-{d}")
    return [f"cover {c['footprint_pct']} % (bar 92), rise {c['rise_tiles']} tile (refinery 0.97), corners "
            + ", ".join(f"{a} {v:.0f}" for a, v in c["corners_pct"].items()),
            f"tonal p50/p95 plate {tp.get('p50')}/{tp.get('p95')}, still {ts.get('p50')}/{ts.get('p95')}; "
            f"black {fn.get('plate', {}).get('black_pct')} %, ratio {fn.get('plate', {}).get('ratio')}",
            f"blue {col.get('blue_pct')} %, white {col.get('white_px')} px, clipped {col.get('clipped_px')} px; "
            f"moving {mo.get('moving_pct')} %, strobe {mo.get('strobe_pct')} %",
            "joins (no gap): " + ", ".join(f"{'PASS' if j['pass'] else 'FAIL'}" for j in js)
            + (f"; legs {lp} px, press {pp} px (probe, 4x)" if lp else "")]


def take_sheet():
    SH = {d: Sheets(os.path.join(FULL, f"run-{d}", "sheets")) for d in DIRS}
    MEAS = {d: json.load(open(os.path.join(FULL, f"measure-{d}", "measures.json"))) for d in DIRS
            if os.path.isfile(os.path.join(FULL, f"measure-{d}", "measures.json"))}
    MODEL = {d: json.load(open(os.path.join(FULL, f"run-{d}", "hi", "model.json"))) for d in DIRS}
    k = 2
    idle = [label(machine(SH[d], *panel(k), k, covers=CONNS[d]), f"facing {d}, idle, 2x",
                  "no recipe: all three boxes, vanilla's covers on the ports") for d in DIRS]
    work = [label(machine(SH[d], *panel(k), k, working=True, conns=CONNS[d][:2]), f"facing {d}, working, 2x",
                  "precipitation: vanilla pipes joined to the two inputs") for d in DIRS]
    chains = []
    stops = None
    for d in DIRS:
        g, stops = chain_panel(SH[d], d, MODEL[d])
        chains.append(label(g, f"facing {d}: the chain", "each connection's run (thick): pipe, wall sleeve, riser, vessel"))
    motion = [label(motion_map(SH[d], d), f"facing {d}: what moves", "red: changes over the loop and the press")
              for d in DIRS]
    W = row(idle).width
    figs = []
    for d in DIRS:
        ls = fig_lines(MEAS[d], d) if d in MEAS else ["not measured"]
        figs.append(para([f"facing {d}: " + ls[0]] + ["    " + l_ for l_ in ls[1:]], W, 22))
    key = ("   ".join(f"{n} {t}" for n, t, _ in stops))
    sec = [heading(f"Form {FORM_NO[KEY]}, \"{TK['pitch']}\" -- the Circulator's vessel set as one building, each connection "
                   f"entering its wall -- refined (T06h)", W),
           para(TK_PITCH.get(KEY, []), W, 24),
           para(RUNS_TEXT, W, 21),
           row(idle), row(work),
           para(["The chain: " + key], W, 22), row(chains), row(motion)]
    sec += [heading("measure.py (factorio-art-measure), per direction", W, 28)] + figs
    out = stack(sec)
    if max(out.size) >= 8000:
        r_ = 7990 / max(out.size)
        out = out.resize((round(out.width * r_), round(out.height * r_)), Image.LANCZOS)
    p = os.path.join(OUTD, f"form-{FORM_NO[KEY]}-{KEY}.png")
    out.convert("RGB").save(p, optimize=True)
    print(p, out.size)
    return SH


def gif(SH):
    frames = []
    for t in range(48):
        f = t % NF
        press = t - 24 if 24 <= t < 24 + PRESS_NF else 0
        cells = []
        for d in DIRS:
            g, origin = panel(1, 6.4, 7.4, 4.0)
            machine(SH[d], g, origin, 1, f, press, working=True, conns=CONNS[d][:2])
            ImageDraw.Draw(g).text((4, 3), f"{FORM_NO[KEY]} {KEY}: {d}", font=font(12, True), fill=TEXT)
            cells.append(g)
        frames.append(row(cells, 6).convert("RGB"))
    pal = frames[0].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    frames = [f_.quantize(palette=pal, dither=Image.Dither.NONE) for f_ in frames]
    p = os.path.join(OUTD, f"form-{FORM_NO[KEY]}-{KEY}-1x.gif")
    frames[0].save(p, save_all=True, append_images=frames[1:], duration=71, loop=0, optimize=True)
    print(p, frames[0].size)


RUNS_TEXT = [
    "Connections, every direction (tiles across; vanilla's pipe is 0.61): each enters the building's wall through a fitting drawn from "
    "vanilla's ports -- in a recess 0.12 deep, a bolted square boss (0.70 on a north or south face, 0.62 on an east or west one), a welded",
    "sleeve 1.22 x the bore (0.66 / 0.59) with a bolted flange at each end (0.78 / 0.70) -- the neck running on through it at the "
    "connection's full bore (0.54 / 0.48). Over or behind that wall stands the vessel that uses it: a riser comes up out of",
    "the roof or deck in a bolted collar, steps down at a visible cone reducer (0.54 to 0.40) and is bolted into the vessel (Liam, "
    "2026-10-20: a narrowing only at a visible reducer). Inside, thin hoses (Liam, 2026-10-21): 0.20 (make-up 0.16, dosing",
    "0.12), cast foot headers and the lagged feed main 0.22, every end on a bolted flange-and-collar nozzle; cable bundles end in a "
    "brass gland. The barrels, junction boxes and valves are the added kit (\"Keep it\").",
    "T06h (Liam, 2026-10-21, \"Restore in refine\"): the signed-off kit T06g left out stands on the roof again -- the side-nozzle pot "
    "(north of the reactor, its nozzle off the shell), the exchanger (between the legs and the receiver),",
    "the sampling manifold (between the instrument house and the compressor), the scrubber's drain skid (down the west roof edge, "
    "ending in its drain valve). Tone (\"Set it in the refine\"): sun 10.8 (was 9.46), the world's fill 0.55 (was 0.24), the putty grey "
    "kept; west stays ~7 under north at every sun and fill (tone-options.png).",
]
FORM_NO = {"casing": 1, "frame": 2, "rotunda": 3}
TK_PITCH = {k_: v_.get("pitch_lines", []) for k_, v_ in takes.TAKES.items()}

def setup(full, key, outd=None, probe=None):
    global FULL, KEY, OUTD, PROBE, TK
    FULL, KEY, OUTD = full, key, outd
    PROBE = json.load(open(probe)) if probe else {}
    TK = takes.TAKES[KEY]


if __name__ == "__main__":
    setup(sys.argv[1], sys.argv[2], sys.argv[3],
          sys.argv[sys.argv.index("--probe") + 1] if "--probe" in sys.argv else None)
    os.makedirs(OUTD, exist_ok=True)
    gif(take_sheet())
