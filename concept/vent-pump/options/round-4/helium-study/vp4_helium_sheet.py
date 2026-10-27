#!/usr/bin/env python3
"""Vent Pump, round 4, T01: the helium glass study -- measures, GIFs and the sheet.

  python3 vp4_helium_sheet.py <full-dir> <out-dir> [--factorio <data>] [--mixes A,B,C,D]

<full-dir> is vp4_helium_study.py's output (4x renders). Writes into <out-dir>:
  helium-study.png            the sheet (each mix idle and working at 1x and 2x, a 2x frame
                              strip of the loop, beside vanilla's storage-tank window and the
                              round-3 gas-lift derrick at the same scale)
  helium-<mix>-1x.gif         working, 1x, on the ground, 32 frames at 66 ms
  helium-<mix>-2x.gif         the same at 2x (keep out of git)
  measures.json               per mix, below

Measures (every frame: idle, the 32 working frames, the 32 glow-only frames; at 1x and 2x):
  white      px with alpha >= 8 and R, G, B all >= 250
  clipped    px with alpha >= 8 and any channel at 255
  glow_peak  the brightest pixel's luminance (0.299 R + 0.587 G + 0.114 B, straight colour
             times alpha, i.e. on black) of the glow-only frames at 1x: the glow's own peak,
             vanilla's 87-171 (radiant-look study: fusion 87/97, centrifuge 156, nuclear 171)
  lit_window_peak  the same luminance in the lit working frames, inside the glass window
  glow_hue   the luminance-weighted mean hue of the glow (glow-only px with L >= 24), degrees,
             and the 5th-95th percentile hue range
  pale_cyan  window px in lit frames with hue 165-215 deg, HSV sat >= 0.10 and L >= 110
  frost      window px in lit frames with L >= 200 and HSV sat <= 0.12 (white-grey rime)
  window     the window's mean colour, idle and working (frame 0), and its mean hue
  motion     mean |dL| inside the window between consecutive working frames (1x); idle is
             one frame, so still by construction
"""
import argparse
import colorsys
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", ".."))
ap = argparse.ArgumentParser()
ap.add_argument("full")
ap.add_argument("out")
ap.add_argument("--factorio", default=os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
ap.add_argument("--mixes", default="A,B,C,D")
args = ap.parse_args()
FULL, OUT = args.full, args.out
MIXES = args.mixes.split(",")
os.makedirs(OUT, exist_ok=True)
R3 = os.path.join(REPO, "concept", "vent-pump", "options", "round-3")
TANK = os.path.join(args.factorio, "base", "graphics", "entity", "storage-tank")

CANVAS, ORIGIN = (160, 160), (64, 96)
VIEW = (14, 10, 138, 150)             # the tank's box at 1x, its shadow included
NF = 32
GIF_MS = 66
ZOOM1 = (24, 26, 84, 106)            # the tank itself in a 1x view, for the x3 zoom
FULL_F, DRAW_F = 10, 14              # the level full (between strokes) and at the deepest draw
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
TEXT = (228, 222, 210)
SUB = (175, 168, 156)
HEAD = (240, 200, 120)
HE3_TINT = (140, 199, 230)            # the mod's helium-3 base_color (0.55, 0.78, 0.90), as the game tints it

NAMES = {
    "A": "A. violet body, peach-pink pulse",
    "B": "B. violet-to-peach gradient",
    "C": "C. violet liquid lit faintly violet",
    "D": "D. no glow (the control)",
}
WHAT = {
    "A": "(1) the grey-violet liquid and bubbles, (2) a faint violet glow while working, and (3) a peach-pink "
         "flash through the liquid and its bubbles on each stroke, fading back to violet as the level refills.",
    "B": "(1) the liquid and bubbles, glowing (2) violet low in the column and grading to (3) peach-pink at the "
         "surface, where the helium is drawn off; steady, a little brighter at each stroke; the bubbles peach.",
    "C": "(1) the liquid and bubbles, (2) lit faintly violet from within: a soft band rising up the column, a "
         "touch brighter at each stroke; no peach.",
    "D": "(1) alone: the grey-violet liquid, its bubbles rising and its level drawn down at each stroke, no glow "
         "at all; this keeps round 3's 'melt the only glow'. The artist's fourth.",
}


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" +
                              ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def load(path, k):
    """A 4x render brought to k x, premultiplied, the catcher's faint fog cut (as round 3)."""
    im = Image.open(path).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    if k != 4:
        im = im.convert("RGBa").resize((CANVAS[0] * k, CANVAS[1] * k), Image.LANCZOS).convert("RGBA")
    return im


def grid_ground(size, origin, ppt):
    g = Image.new("RGBA", size, GROUND)
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ox, oy = origin
    for i in range(-40, 41):
        d.line([(ox + (i + 0.5) * ppt, 0), (ox + (i + 0.5) * ppt, size[1])], fill=(255, 255, 255, 22))
        d.line([(0, oy + (i + 0.5) * ppt), (size[0], oy + (i + 0.5) * ppt)], fill=(255, 255, 255, 22))
    g.alpha_composite(ov)
    return g


def on_ground(im, k):
    g = grid_ground(im.size, (ORIGIN[0] * k, ORIGIN[1] * k), 64 * k)
    g.alpha_composite(im)
    return g.crop(tuple(v * k for v in VIEW))


def lum(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b


def px(im):
    return list(im.getdata())


def white_clipped(im):
    w = c = 0
    for r, g, b, a in px(im):
        if a < 8:
            continue
        if r >= 250 and g >= 250 and b >= 250:
            w += 1
        if r == 255 or g == 255 or b == 255:
            c += 1
    return w, c


def mask_of(k):
    m = Image.open(os.path.join(FULL, "mask.png")).convert("L")
    if k != 4:
        m = m.resize((CANVAS[0] * k, CANVAS[1] * k), Image.LANCZOS)
    return [v > 128 for v in m.getdata()]


def hue_sat(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return h * 360, s


def frost_cyan(im, mask):
    cy = fr = 0
    for (r, g, b, a), m in zip(px(im), mask):
        if not m or a < 128:
            continue
        L = lum(r, g, b)
        h, s = hue_sat(r, g, b)
        if 165 <= h <= 215 and s >= 0.10 and L >= 110:
            cy += 1
        if L >= 200 and s <= 0.12:
            fr += 1
    return cy, fr


def window_stats(im, mask):
    P = [(r, g, b) for (r, g, b, a), m in zip(px(im), mask) if m and a >= 128]
    n = max(1, len(P))
    mean = tuple(round(sum(p[i] for p in P) / n) for i in range(3))
    peak = max((lum(*p) for p in P), default=0)
    return mean, peak, len(P)


def glow_stats(im):
    """Glow-only frame (no sun, sky or ground): straight colour times alpha, i.e. on black."""
    peak, hs = 0.0, []
    for r, g, b, a in px(im):
        if a == 0:
            continue
        f = a / 255
        r, g, b = r * f, g * f, b * f
        L = lum(r, g, b)
        peak = max(peak, L)
        if L >= 24:
            h, _ = hue_sat(r, g, b)
            hs.append((h, L))
    return peak, hs


def circ_mean(hs):
    if not hs:
        return None
    x = sum(math.cos(math.radians(h)) * w for h, w in hs)
    y = sum(math.sin(math.radians(h)) * w for h, w in hs)
    return round(math.degrees(math.atan2(y, x)) % 360, 1)


def hue_range(hs):
    if not hs:
        return None
    c = circ_mean(hs)
    d = sorted(((h - c + 180) % 360 - 180) for h, _ in hs)
    lo, hi = d[int(0.05 * (len(d) - 1))], d[int(0.95 * (len(d) - 1))]
    return [round((c + lo) % 360, 1), round((c + hi) % 360, 1)]


def stroke(t, centres=(-0.16, 0.34), rise=0.08, fall=0.36):
    """The study's stroke curve (vp4_helium_study.py): 0 level full, 1 the deepest draw."""
    def sm(u):
        u = max(0.0, min(1.0, u))
        return u * u * (3 - 2 * u)
    v = 0.0
    for c in centres:
        d = (t - c) % 1.0
        v = max(v, sm(d / rise) if d < rise else (1 - sm((d - rise) / fall)) if d < rise + fall else 0.0)
    return v


def gif(frames, path):
    strip = Image.new("RGB", (frames[0].width, frames[0].height * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f.convert("RGB"), (0, i * f.height))
    pal = strip.quantize(colors=256)
    q = [f.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=GIF_MS, loop=0, optimize=True)
    return round(os.path.getsize(path) / 1e6, 3)


# ---------------------------------------------------------------- measure every mix
M1, M2 = mask_of(1), mask_of(2)
MEAS, VIEWS = {}, {}
for mix in MIXES:
    d = os.path.join(FULL, mix)
    m = dict(name=NAMES[mix], white=dict(), clipped=dict())
    W = {"1x": 0, "2x": 0}
    C = {"1x": 0, "2x": 0}
    cyan = frost = 0
    lit_peak = 0
    views = {1: [], 2: []}
    idle = {k: load(os.path.join(d, "idle.png"), k) for k in (1, 2)}
    lit_frames = [("idle", idle)]
    work = []
    for f in range(NF):
        fr = {k: load(os.path.join(d, f"working-{f:02d}.png"), k) for k in (1, 2)}
        work.append(fr)
        lit_frames.append((f"w{f}", fr))
    for tag, fr in lit_frames:
        for k, mk in ((1, M1), (2, M2)):
            w, c = white_clipped(fr[k])
            W[f"{k}x"] += w
            C[f"{k}x"] += c
            cy, fo = frost_cyan(fr[k], mk)
            cyan += cy
            frost += fo
        if tag != "idle":
            lit_peak = max(lit_peak, window_stats(fr[1], M1)[1])
    gpk, gpk2, ghs, gwc = 0.0, 0.0, [], [0, 0]
    if os.path.exists(os.path.join(d, "emit-00.png")):
        for f in range(NF):
            for k in (1, 2):
                e = load(os.path.join(d, f"emit-{f:02d}.png"), k)
                w, c = white_clipped(e)
                gwc[0] += w
                gwc[1] += c
                pk, hs = glow_stats(e)
                if k == 1:
                    gpk = max(gpk, pk)
                    ghs += hs
                else:
                    gpk2 = max(gpk2, pk)
        m["glow_peak_1x"] = round(gpk)
        m["glow_peak_2x"] = round(gpk2)
        m["glow_in_87_171"] = 87 <= round(gpk) <= 171
        m["glow_hue_deg"] = circ_mean(ghs)
        m["glow_hue_p5_p95"] = hue_range(ghs)
    else:
        m["glow_peak_1x"] = None
        m["glow_in_87_171"] = "no glow"
    m["white"] = dict(lit_1x=W["1x"], lit_2x=W["2x"], glow_frames=gwc[0])
    m["clipped"] = dict(lit_1x=C["1x"], lit_2x=C["2x"], glow_frames=gwc[1])
    m["frames_checked"] = dict(lit=len(lit_frames), glow=NF if gpk else 0, scales=["1x", "2x"])
    m["pale_cyan_px"] = cyan
    m["frost_px"] = frost
    m["lit_window_peak_1x"] = round(lit_peak)
    mi, _, n = window_stats(idle[1], M1)
    mw, _, _ = window_stats(work[0][1], M1)
    m["window_px_1x"] = n
    m["window_mean_idle"] = "#%02X%02X%02X" % mi
    m["window_mean_working_f0"] = "#%02X%02X%02X" % mw
    m["window_hue_idle"] = round(hue_sat(*mi)[0], 1)
    m["window_hue_working_f0"] = round(hue_sat(*mw)[0], 1)
    dl = []
    for f in range(NF):
        a, b = work[f][1], work[(f + 1) % NF][1]
        s_ = [abs(lum(*p[:3]) - lum(*q[:3])) for p, q, mk in zip(px(a), px(b), M1) if mk]
        dl.append(sum(s_) / max(1, len(s_)))
    m["motion_mean_dL_1x"] = round(sum(dl) / len(dl), 2)
    g1 = [on_ground(fr[1], 1) for fr in work]
    g2 = [on_ground(fr[2], 2) for fr in work]
    m["gif_1x_mb"] = gif(g1, os.path.join(OUT, f"helium-{mix}-1x.gif"))
    m["gif_2x_mb"] = gif(g2, os.path.join(OUT, f"helium-{mix}-2x.gif"))
    MEAS[mix] = m
    VIEWS[mix] = dict(idle1=on_ground(idle[1], 1), idle2=on_ground(idle[2], 2), g1=g1, g2=g2)
    print(mix, json.dumps(m))

# ---------------------------------------------------------------- references
tank = Image.open(os.path.join(TANK, "storage-tank.png")).convert("RGBA").crop((0, 0, 219, 235))
win = Image.open(os.path.join(TANK, "window-background.png")).convert("RGBA")
# the entity's centre in the frame (shift -0.25, -1.25 game px = -0.5, -2.5 sprite px) and the
# window box {{-0.125, 0.6875}, {0.1875, 1.1875}} tiles at 64 px a tile
EC = (110, 120)
WB = (EC[0] - 8, EC[1] + 44, EC[0] + 12, EC[1] + 76)


def vanilla_tank(fill):
    im = Image.new("RGBA", tank.size, (0, 0, 0, 0))
    wbx = (round((WB[0] + WB[2]) / 2 - win.width / 2), round((WB[1] + WB[3]) / 2 - win.height / 2))
    im.paste(win, wbx)
    if fill:
        top = round(WB[3] - (WB[3] - WB[1]) * 0.6)
        ImageDraw.Draw(im).rectangle([WB[0], top, WB[2] - 1, WB[3] - 1], fill=HE3_TINT + (255,))
    im.alpha_composite(tank)
    g = grid_ground(im.size, EC, 64)
    g.alpha_composite(im)
    return g


van_empty = vanilla_tank(False)
van_he = vanilla_tank(True)


def gif_frame(path, i=0):
    g = Image.open(path)
    g.seek(i)
    return g.convert("RGBA")


der1 = gif_frame(os.path.join(R3, "01-gas-lift-derrick-1x.gif"))
p2 = os.path.join(R3, "01-gas-lift-derrick-2x.gif")
der2 = gif_frame(p2) if os.path.exists(p2) else der1.resize((der1.width * 2, der1.height * 2), Image.NEAREST)

# ---------------------------------------------------------------- the sheet
PAD = 18


def text(d, xy, s, size=13, fill=TEXT, bold=False):
    d.text(xy, s, font=font(size, bold), fill=fill)


def wrap(s, size, width):
    f = font(size)
    out, line = [], ""
    for w in s.split():
        t = (line + " " + w).strip()
        if f.getlength(t) > width and line:
            out.append(line)
            line = w
        else:
            line = t
    if line:
        out.append(line)
    return out


def captioned(im, cap, size=12, width=None):
    width = max(im.width, width or 0)
    lines = []
    for c in cap.split("\n"):
        lines += wrap(c, size, width)
    h = len(lines) * (size + 4) + 4
    o = Image.new("RGBA", (width, im.height + h), BG)
    d = ImageDraw.Draw(o)
    for i, s in enumerate(lines):
        text(d, (0, i * (size + 4)), s, size, SUB if i else TEXT, bold=(i == 0))
    o.alpha_composite(im, (0, h))
    return o


def hrow(ims, gap=14):
    w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    h = max(i.height for i in ims)
    o = Image.new("RGBA", (w, h), BG)
    x = 0
    for i in ims:
        o.alpha_composite(i, (x, 0))
        x += i.width + gap
    return o


def block(title, paras, width, size=13):
    lines = [(title, HEAD, True, size + 3)] if title else []
    for p in paras:
        for s in wrap(p, size, width):
            lines.append((s, SUB, False, size))
        lines.append(("", SUB, False, 4))
    h = sum(l[3] + 5 for l in lines) + 4
    o = Image.new("RGBA", (width, h), BG)
    d = ImageDraw.Draw(o)
    y = 0
    for s, c, b, sz in lines:
        text(d, (0, y), s, sz, c, b)
        y += sz + 5
    return o


def up(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def fmt(m):
    g = m.get("glow_peak_1x")
    gl = (f"glow peak {g} at 1x ({m['glow_peak_2x']} at 2x), hue {m['glow_hue_deg']} deg "
          f"(p5-p95 {m['glow_hue_p5_p95'][0]}-{m['glow_hue_p5_p95'][1]})") if g else "no glow"
    return (f"{gl}; white {m['white']['lit_1x']}/{m['white']['lit_2x']}/{m['white']['glow_frames']}, "
            f"clipped {m['clipped']['lit_1x']}/{m['clipped']['lit_2x']}/{m['clipped']['glow_frames']} "
            f"(lit 1x / lit 2x / glow frames, {m['frames_checked']['lit']} lit frames); pale cyan "
            f"{m['pale_cyan_px']}, frost {m['frost_px']}; window idle {m['window_mean_idle']}, working "
            f"{m['window_mean_working_f0']}; lit window peak {m['lit_window_peak_1x']}; motion dL "
            f"{m['motion_mean_dL_1x']}; GIF 1x {m['gif_1x_mb']} MB")


rows = []
W = 1640
rows.append(block("VENT PUMP, ROUND 4 (T01) -- THE HELIUM SEEN IN GLASS: ONE SIGHT TANK, FOUR MIXES", [
    "One armoured glass sight tank on the lagged helium line, at the size it would have on the 3 x 3 Vent Pump "
    "(glass 0.35 t across, 1.06 t tall: 22 x 34 sprite px at 1x; vanilla's storage-tank window is about 17 x 24), "
    "64 px a tile, one ground, the sun and finish of round 3. Helium in at the tank's foot (south), out of its "
    "head (east, then down and north). A stroke (two a loop, as round 3's derrick) draws the helium: the level "
    "drops and refills, the bubbles rise, the relief poppet lifts and the gauge swings. Idle: unlit and still, "
    "no bubbles.",
    "Liam's three, mixed: (1) grey-violet liquid #7E7488 with slow rising bubbles #B6A6C8; (2) a faint violet "
    "glow from within (#9C86CC); (3) a peach-pink helium-discharge glow (#F2A296). No frost, rime or pale cyan; "
    "the glass is clear and warm-neutral (the kit's pane is faintly blue and is not used).",
    "Conflict for Liam: round 3's rule is 'melt the only glow' (orange only where melt is seen). Mixes A, B and C "
    "add a helium glow; D keeps the rule. The glow is held under vanilla's own lit-window peaks (87-171).",
], W))

ref = []
ref.append(captioned(van_empty, "vanilla storage tank, 1x\n(frame 0, window empty)", width=230))
ref.append(captioned(up(van_he.crop((92, 156, 132, 200)), 2), "its window, 2x\nfilled 60 % with the mod's "
                     "helium-3 tint (pale cyan: what we avoid)", width=150))
ref.append(captioned(der1, "round 3, 1. gas-lift derrick, 1x\n(frame 0, for scale)"))
dmix = MIXES[0]
at_scale = grid_ground((der1.width + 150, der1.height), (0, 0), 64)
at_scale.alpha_composite(der1, (0, 0))
t1 = VIEWS[dmix]["g1"][DRAW_F]
at_scale.alpha_composite(t1, (der1.width + 10, der1.height // 2 - t1.height // 2))
ref.append(captioned(at_scale, f"the tank (mix {dmix}, working) beside it, both 1x"))
ref.append(captioned(der2.crop((der2.width // 4, der2.height // 4, der2.width * 3 // 4, der2.height * 3 // 4)),
                     "the derrick, 2x (centre)"))
rows.append(block("REFERENCES, SAME SCALE (64 px a tile)", [], W))
rows.append(hrow(ref))

for mix in MIXES:
    v, m = VIEWS[mix], MEAS[mix]
    rows.append(block(NAMES[mix].upper(), [WHAT[mix], fmt(m)], W, size=12))
    panels = [
        captioned(v["idle1"], "idle, 1x\nunlit, still"),
        captioned(v["g1"][FULL_F], f"working f{FULL_F}, 1x\nlevel full"),
        captioned(v["g1"][DRAW_F], f"working f{DRAW_F}, 1x\nthe draw"),
        captioned(v["idle2"], "idle, 2x\nunlit, still, no bubbles"),
        captioned(v["g2"][FULL_F], f"working f{FULL_F}, 2x\nlevel full, between strokes"),
        captioned(v["g2"][DRAW_F], f"working f{DRAW_F}, 2x\nthe draw: a stroke"),
    ]
    rows.append(hrow(panels))
    zoom = [captioned(up(im.crop(ZOOM1), 3), cap) for im, cap in (
        (v["idle1"], "1x shown x3 (nearest)\nidle"), (v["g1"][FULL_F], "1x shown x3\nlevel full"),
        (v["g1"][DRAW_F], "1x shown x3\nthe draw"))]
    strip = [captioned(v["g2"][f].crop((50, 20, 200, 240)), f"2x f{f}\ndraw {stroke(f / NF):.2f}")
             for f in range(0, NF, 4)]
    rows.append(hrow(zoom + strip, 8))

H = sum(r.height for r in rows) + PAD * (len(rows) + 1)
Wd = max(r.width for r in rows) + 2 * PAD
sheet = Image.new("RGBA", (Wd, H), BG)
y = PAD
for r in rows:
    sheet.alpha_composite(r, (PAD, y))
    y += r.height + PAD
sheet.convert("RGB").save(os.path.join(OUT, "helium-study.png"))
json.dump(dict(mixes=MEAS, sheet_px=list(sheet.size), frames=NF, gif_ms=GIF_MS,
               definitions=__doc__.split("Measures")[1].strip()),
          open(os.path.join(OUT, "measures.json"), "w"), indent=1)
print("sheet", sheet.size)
