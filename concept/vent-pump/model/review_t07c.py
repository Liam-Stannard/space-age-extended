#!/usr/bin/env python3
"""Vent Pump model (T07c): the review sheets and the 1x GIFs for the per-direction variations and the effects.

  python3 -B review_t07c.py --run <render.sh out-dir> --measure <measure.py --out of it>
        --t07 <T07's packed sheets dir> --t07-measure <T07's measures.json>
        --effects <effects.py --out> --out <concept/vent-pump/model> --scratch <dir>

Writes into --out (each page under 8000 px a side):
  review-t07c-directions.png  the four directions, stopped and working, beside T07's four and the chemical plant's
                             four, the same ground and scale (2x); the figures
  review-t07c-strips.png     a frame strip of every animation in every direction, over the plate (2x)
  review-t07c-checks.png     the stray-light map, the lenses, the riser and the glass close up beside T07's
  review-t07c-effects.png    the effect sheets, and each effect placed on the machine in the four directions
  motion-1x.gif              the four directions working at animation_speed 0.2, 1x (the green lens lit)
  effects-1x.gif             the same with the wisp, the embers and the two charge puffs drawn as the engine
                             would place them (E3 is a light: shown on the sheet as a night mock-up)
and into --scratch: motion-2x.gif (not for git).

Everything is composed from the packed sheets as measure.py composes them: each sheet at its shift, shadows
at half strength, glows added as light, the lenses' white cuts tinted and added as the engine adds a glow.
"""
import argparse
import json
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import measure  # noqa: E402

ap = argparse.ArgumentParser()
for k in ("run", "measure", "t07", "t07_measure", "effects", "out", "scratch"):
    ap.add_argument("--" + k.replace("_", "-"), required=True)
A = ap.parse_args()
os.makedirs(A.scratch, exist_ok=True)
os.makedirs(A.out, exist_ok=True)
FD = measure.FD
PPT = 64
GROUND = (74, 66, 58)
BG = (30, 28, 26)
TXT = (226, 220, 210)
HEAD = (240, 200, 120)
DIRS = ("north", "east", "south", "west")
DECL = json.load(open(os.path.join(A.run, "renders", "render.json")))
META = json.load(open(os.path.join(A.run, "sheets", "meta.json")))
T07META = json.load(open(os.path.join(A.t07, "meta.json")))
MEAS = json.load(open(os.path.join(A.measure, "measures.json")))
T07MEAS = json.load(open(A.t07_measure))
MODEL = json.load(open(os.path.join(A.run, "model.json")))
FX = json.load(open(os.path.join(A.effects, "effects.json")))["effects"]
C = DECL["canvas"][0]
NF = 24
MECH = ("mech",)
HALO = {"lens-working": (0.30, 1.0, 0.35), "lens-no-fluid": (1.0, 0.66, 0.12)}


def font(n, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if bold else "") + ".ttf", n)


F1, F2, FB = font(13), font(11), font(16, True)


# ---------------------------------------------------------------- the packed sheets, placed
_cache = {}


def sheet(stem, src):
    key = (src, stem)
    if key not in _cache:
        _cache[key] = Image.open(os.path.join(src, stem + ".png")).convert("RGBA")
    return _cache[key]


def placed(stem, f=0, src=None, meta=None, canvas=C):
    src = src or os.path.join(A.run, "sheets")
    meta = meta or META
    m = meta[stem]
    w, h = m["size"]
    im = sheet(stem, src)
    if "frames" in m:
        ll, f = m["line_length"], f % m["frames"]
        im = im.crop(((f % ll) * w, (f // ll) * h, (f % ll) * w + w, (f // ll) * h + h))
    out = Image.new("RGBA", (canvas, canvas))
    out.alpha_composite(im, (round(canvas / 2 + m["shift"][0] * PPT - w / 2), round(canvas / 2 + m["shift"][1] * PPT - h / 2)))
    return out


def tinted(alpha_im, tint, k=0.95):
    a = alpha_im.getchannel("A")
    return Image.merge("RGB", [a.point(lambda v, t=t: round(v * t * k)) for t in tint])


def shadow_under(out, stem, src=None, meta=None):
    sh = placed(stem, src=src, meta=meta)
    a = sh.getchannel("A").point(lambda v: v // 2)
    out.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (C, C)).split(), a)))


def compose(d, f=0, working=True, shadow=True, lenses=(), ground=GROUND, halo=False, light=True, only=None):
    """T07c as drawn in direction d at frame f: ground, shadow at half strength, the plate, every moving part
    at f (drawn always: frozen when stopped, so frame 0 stopped), the working layers and their light while
    working, each lit lens's glow added. only: draw just these layers over the plate."""
    out = Image.new("RGBA", (C, C), ground + (255,))
    if shadow:
        shadow_under(out, f"shadow-{d}")
    out.alpha_composite(placed(f"base-{d}"))
    for m in MECH:
        if only is None or m in only:
            out.alpha_composite(placed(f"{m}-{d}", f if working else 0))
    if working:
        for g in ("riser", "glass"):
            if only is None or g in only:
                out.alpha_composite(placed(f"{g}-{d}", f))
    rgb = out.convert("RGB")
    if working and light:
        for g in ("riser", "glass"):
            if only is None or g in only:
                rgb = ImageChops.add(rgb, measure.light_of(placed(f"{g}-light-{d}", f)))
    for ln in lenses:
        rgb = ImageChops.add(rgb, measure.light_of(placed(f"{ln}-glow-{d}")))
        if halo:
            rgb = ImageChops.add(rgb, tinted(placed(f"{ln}-halo-{d}"), HALO[ln], 0.5))
    return rgb


def compose_t07(d, f=0, working=True, shadow=True, lenses=()):
    src = A.t07
    out = Image.new("RGBA", (C, C), GROUND + (255,))
    if shadow:
        shadow_under(out, f"shadow-{d}", src, T07META)
    out.alpha_composite(placed(f"base-{d}", src=src, meta=T07META))
    if working:
        out.alpha_composite(placed(f"working-{d}", f, src=src, meta=T07META))
    rgb = out.convert("RGB")
    for ln in lenses:
        rgb = ImageChops.add(rgb, measure.light_of(placed(f"{ln}-glow-{d}", src=src, meta=T07META)))
    return rgb


def chem(d, f):
    """Vanilla's chemical plant in direction d, its two animation layers at frame f, its own shadow."""
    base = "base/graphics/entity/chemical-plant/"
    out = Image.new("RGBA", (C, C), GROUND + (255,))
    i = DIRS.index(d)
    sh, sx, sy = measure.vanilla_sprite(base + "chemical-plant-shadow.png", dict(geom=(312, 222, (54, 12)), col=i))
    lay = Image.new("RGBA", (C, C))
    lay.alpha_composite(sh, (round(C / 2 + sx - sh.width / 2), round(C / 2 + sy - sh.height / 2)))
    out.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (C, C)).split(), lay.getchannel("A").point(lambda v: v // 2))))
    for part in ("base", "anim-1", "anim-2"):
        png, w, h, (sx, sy), _ = measure.sprite_geometry(base + f"chemical-plant-{d}-{part}.png")
        ll = int(open(png[:-4] + ".lua").read().split("line_length")[1].split("=")[1].split(",")[0])
        k = 0 if part == "base" else f
        im = measure.load(png).crop(((k % ll) * w, (k // ll) * h, (k % ll) * w + w, (k // ll) * h + h))
        out.alpha_composite(im, (round(C / 2 + sx - w / 2), round(C / 2 + sy - 18 - h / 2)))
    return out.convert("RGB")


def crop_content(ims, pad=10):
    box = None
    for im in ims:
        diff = ImageChops.difference(im.convert("RGB"), Image.new("RGB", im.size, GROUND)).getbbox()
        if diff:
            box = diff if box is None else (min(box[0], diff[0]), min(box[1], diff[1]), max(box[2], diff[2]),
                                            max(box[3], diff[3]))
    W_, H_ = ims[0].size
    box = (max(0, box[0] - pad), max(0, box[1] - pad), min(W_, box[2] + pad), min(H_, box[3] + pad))
    return [im.crop(box) for im in ims], box


def up(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST if k >= 3 else Image.LANCZOS)


def captioned(im, lines, width=None):
    lines = [lines] if isinstance(lines, str) else lines
    lh = 16
    w = max(im.width, width or 0)
    out = Image.new("RGB", (w, im.height + lh * len(lines) + 6), BG)
    dr = ImageDraw.Draw(out)
    for i, ln in enumerate(lines):
        dr.text((2, 2 + lh * i), ln, fill=HEAD if i == 0 else TXT, font=F1 if i == 0 else F2)
    out.paste(im.convert("RGB"), (0, lh * len(lines) + 6))
    return out


def row(panels, gap=14):
    w = sum(p.width for p in panels) + gap * (len(panels) - 1)
    h = max(p.height for p in panels)
    out = Image.new("RGB", (w, h), BG)
    x = 0
    for p in panels:
        out.paste(p, (x, 0))
        x += p.width + gap
    return out


def column(blocks, gap=22, width=None):
    w = width or max(b.width for b in blocks)
    out = Image.new("RGB", (w, sum(b.height for b in blocks) + gap * (len(blocks) - 1)), BG)
    y = 0
    for b in blocks:
        out.paste(b, (0, y))
        y += b.height + gap
    return out


def text_block(title, lines, width):
    lh = 15
    out = Image.new("RGB", (width, 24 + lh * len(lines)), BG)
    dr = ImageDraw.Draw(out)
    dr.text((2, 2), title, fill=HEAD, font=FB)
    for i, ln in enumerate(lines):
        dr.text((2, 24 + lh * i), ln, fill=TXT, font=F2)
    return out


def wrap_rows(panels, max_w, gap=14):
    rows, cur, w = [], [], 0
    for p in panels:
        if cur and w + gap + p.width > max_w:
            rows.append(row(cur, gap))
            cur, w = [], 0
        cur.append(p)
        w += p.width + (gap if len(cur) > 1 else 0)
    if cur:
        rows.append(row(cur, gap))
    return column(rows, 12)


def save(im, name):
    assert max(im.size) < 8000, (name, im.size)
    p = os.path.join(A.out, name)
    im.save(p, optimize=True)
    print(p, im.size)
    return p


W = 3000

# ---------------------------------------------------------------- the figures
def g(m, *ks, default="-"):
    for k in ks:
        if not isinstance(m, dict) or k not in m:
            return default
        m = m[k]
    return m


fig = ["direction | cover % | rise t | p50 plate/still | p95 plate/still | white | clipped | glow peaks f0: riser / glass / "
       "green lens / amber lens | glow layers non-empty | joins | strobe % | moving %"]
for src, name in ((T07MEAS, "T07"), (MEAS, "T07c")):
    for d in DIRS:
        m = src["directions"][d]
        cv, tn, co, mo = m["coverage"], m["tonal"], m["colour"], m.get("motion") or {}
        gl = m.get("glow", {})
        peaks = " / ".join(str(g(gl, k, "peak")) for k in (f"riser-light-{d}", f"glass-light-{d}",
                                                            f"lens-working-glow-{d}", f"lens-no-fluid-glow-{d}"))
        nonempty = "-" if name == "T07" else ("yes" if all(f"{k}-{d}" in META for k in ("riser-light", "glass-light")) else "NO")
        js = "/".join(("pass" if j["pass"] else "FAIL") for j in m["joins"])
        fig.append(f"{name} {d} | {cv['footprint_pct']} | {cv['rise_tiles']} | {tn['plate']['p50']} / {tn['still']['p50']} | "
                   f"{tn['plate']['p95']} / {tn['still']['p95']} | {co['white_px']} | {co['clipped_px']} | {peaks} | {nonempty} | "
                   f"{js} | {mo.get('strobe_pct')} | {mo.get('moving_pct')}")
coll = MEAS.get("collide") or {}
fig.append(f"collide (T07c, four directions): {'PASS' if coll.get('pass') else coll.get('why', 'not run')}; gates {MEAS.get('gates')}")
block_fig = text_block("Figures (measure.py, every direction): T07 above, T07c below", fig, W)

# ---------------------------------------------------------------- 1. the four directions beside T07 and the chemical plant
rows_ = []
for label, fn in (("T07c: each direction its own variation", "c"), ("T07: the whole machine turned", "t07"),
                  ("vanilla chemical plant: a base and two animations per direction", "chem")):
    panels = []
    for d in DIRS:
        if fn == "c":
            ims = [compose(d, 0, working=False), compose(d, 4, working=True, lenses=("lens-working",))]
            m = MEAS["directions"][d]
        elif fn == "t07":
            ims = [compose_t07(d, 0, working=False), compose_t07(d, 4, working=True, lenses=("lens-working",))]
            m = T07MEAS["directions"][d]
        else:
            ims = [chem(d, 0), chem(d, 12)]
            m = None
        cr, _ = crop_content(ims, pad=6)
        cap = (f"cover {m['coverage']['footprint_pct']} %, rise {m['coverage']['rise_tiles']} t, p50 {m['tonal']['plate']['p50']}"
               if m else "frame 0 / frame 12 (its windows are recipe-tinted visualisations: not drawn)")
        panels.append(captioned(row([up(cr[0], 2), up(cr[1], 2)], 4), [f"{d}: stopped | working (frame 4, a charge)", cap]))
    rows_.append(column([text_block(label, [], W), row(panels, 26)], 4))
block_dirs = column([text_block("1. The four directions at 2x, stopped and working, on one ground: T07c, T07, the chemical plant", [
    "T07c (vent_pump.py's docstring): the tower, its glass riser and the head tank's window face the camera in every direction, as the "
    "chemical plant's vessel window does; the plumbing and the units turn with the fluid boxes (helium in, melt out on the faces the "
    "prototype turns them to);",
    "the lines between them are routed per direction; the sight glass and the dials face the camera; south, the sight glass stands east of the "
    "tower; west is east's arrangement mirrored (turned, west hid the amber lens behind the tower).",
    "Working: the plate, every moving part at the frame, the riser and the glass with their light added, the green lens lit; shadow at half strength."], W)]
    + rows_)
save(column([block_fig, block_dirs]), "review-t07c-directions.png")

# ---------------------------------------------------------------- 2. a frame strip of every animation, every direction
def layer_box(d, names, pad=4):
    box = None
    for n in names:
        m = META[f"{n}-{d}"]
        w, h = m["size"]
        x0 = round(C / 2 + m["shift"][0] * PPT - w / 2)
        y0 = round(C / 2 + m["shift"][1] * PPT - h / 2)
        b = (x0 - pad, y0 - pad, x0 + w + pad, y0 + h + pad)
        box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    return box


strip_blocks = []
for d in DIRS:
    panels = []
    for lay, names in (("riser + riser-light", ("riser", "riser-light")), ("glass + glass-light", ("glass", "glass-light")),
                       ("mech: the meter, two gauges, the float lever, the coupling", ("mech",))):
        box = layer_box(d, names)
        only = (names[0],)
        frames = [compose(d, f, working=True, shadow=False, only=only).crop(box) for f in range(NF)]
        k = 2 if box[3] - box[1] > 60 else 3
        fr = [up(x, k) for x in frames]
        lm = (MEAS["directions"][d].get("layers_alone") or {}).get(f"{names[0]}-{d}", {})
        panels.append(captioned(column([row(fr[:12], 2), row(fr[12:], 2)], 2),
                                [f"{d}: {lay}, frames 0-23, {k}x", f"step px {min(lm.get('step_px') or [0])}-"
                                 f"{max(lm.get('step_px') or [0])}, wrap {lm.get('wrap_px')}"]))
    strip_blocks.append(wrap_rows(panels, W, 18))
save(column([text_block("2. Every animation, every direction: each layer's 24 frames over the plate (the working layers with their light)", [
    "riser and glass draw only while working (render.json working: true), their light a glow animation over each; the meter, the two gauges, "
    "the float lever and the coupling are one layer (mech), part of the stopped machine at frame 0 (pack.py's frame-0 check)."], W)]
    + strip_blocks), "review-t07c-strips.png")

# ---------------------------------------------------------------- 3. checks: stray light, the lenses, close-ups beside T07
def quarter(p):
    im = Image.open(p).convert("RGBa")
    return im.resize((im.width // 4, im.height // 4), Image.LANCZOS).convert("RGBA")


stray_panels, stray_lines = [], []
for d in DIRS:
    plate = compose(d, working=False, shadow=False)
    mapim = Image.blend(plate, Image.new("RGB", plate.size, (0, 0, 0)), 0.55)
    px = mapim.load()
    masks = {g_: quarter(os.path.join(A.run, "masks", f"{g_}-{d}.png")).getchannel("A").point(lambda v: 255 if v > 8 else 0)
             .filter(ImageFilter.MaxFilter(3)) for g_ in ("riser", "glass")}
    both_ = ImageChops.lighter(masks["riser"], masks["glass"])
    worst = None
    for f in range(NF):
        light = ImageChops.add(measure.light_of(placed(f"riser-light-{d}", f)), measure.light_of(placed(f"glass-light-{d}", f)))
        L = light.convert("L").point(lambda v: 255 if v > 8 else 0)
        off = ImageChops.multiply(L, ImageChops.invert(both_))
        n_off, n_on = measure.count(off), measure.count(ImageChops.multiply(L, both_))
        if worst is None or n_off > worst[0]:
            worst = (n_off, n_on, f, L, off)
    n_off, n_on, f, L, off = worst
    # coloured by the group that is solid there (alpha > 128): each mask also carries a faint haze (alpha just
    # over 8) where the other group is held out, which the counts above take as "on" either way
    solid = quarter(os.path.join(A.run, "masks", f"riser-{d}.png")).getchannel("A").point(lambda v: 255 if v > 128 else 0)
    Ld, Od, Rd = L.load(), off.load(), solid.filter(ImageFilter.MaxFilter(3)).load()
    for y in range(C):
        for x in range(C):
            if Od[x, y]:
                px[x, y] = (255, 0, 255)
            elif Ld[x, y]:
                px[x, y] = (255, 150, 40) if Rd[x, y] else (170, 130, 255)
    stray_lines.append(f"{d}: lit px (the packed riser-light and glass-light, luminance > 8) {n_on} on the melt or the glass, "
                       f"{n_off} off both (the most, frame {f})")
    (mi,), _ = crop_content([mapim], pad=4)
    stray_panels.append(captioned(up(mi, 2), [d, "orange: on the melt; violet: on the glass; magenta: off both"]))
block_stray = column([text_block("3. Stray light (model-stage check): the light mapped to the melt or the helium glass, every direction", [
    "The two glow animations as packed, every frame, against silhouettes of the riser's melt, glass and window and of the sight glass "
    "(run/masks), grown 1 px for the anti-aliased rim; the frame with the most off them. Each glow is rendered with everything but its "
    "own group held out, so its light can only fall on the melt or the glass."] + stray_lines, W), row(stray_panels, 16)])

lens_panels = []
for d in DIRS:
    a = compose(d, working=False, shadow=False)
    b = compose(d, 4, working=True, shadow=False, lenses=("lens-working",), halo=True)
    c = compose(d, working=False, shadow=False, lenses=("lens-no-fluid",), halo=True)
    (ia, ib, ic), _ = crop_content([a, b, c], pad=4)
    lens_panels.append(captioned(row([up(ia, 2), up(ib, 2), up(ic, 2)], 4),
                                 [f"{d}: unlit | green (working) | amber (fluid missing)", "glow + halo, as T07"]))
block_lens = column([text_block("4. The two status lenses in every direction (as T07: glow + light, Liam 2026-10-20)", [], W),
                     wrap_rows(lens_panels, W, 18)])

close = []
for d in DIRS:
    a = compose_t07(d, 4, working=True, shadow=False)
    b = compose(d, 4, working=True, shadow=False)
    (ia, ib), _ = crop_content([a, b], pad=4)
    close.append(captioned(row([up(ia, 2), up(ib, 2)], 6), [f"{d}: T07 | T07c, working frame 4 (a charge)"]))
block_close = column([text_block("5. Working, T07 beside T07c, every direction (2x): where the glass, the melt and the helium are seen", [], W),
                      wrap_rows(close, W, 18)])
save(column([block_stray, block_lens, block_close]), "review-t07c-checks.png")

# ---------------------------------------------------------------- 4. effects
FXS = os.path.join(A.effects)


def fx_frame(name, k):
    e = FX[name]
    im = Image.open(os.path.join(FXS, e["file"])).convert("RGBA")
    w, h, ll = e["width"], e["height"], e["line_length"]
    k %= e["frame_count"]
    return im.crop(((k % ll) * w, (k // ll) * h, (k % ll) * w + w, (k // ll) * h + h))


TOP = 128          # headroom over the canvas: the wisp rises past its top


def fx_place(rgb, name, d, k):
    e = FX[name]
    fr = fx_frame(name, k)
    px, py = e[f"{d}_position"]
    sx, sy = e["shift"]
    x = round(C / 2 + (px + sx) * PPT - fr.width / 2)
    y = round(TOP + C / 2 + (py + sy) * PPT - fr.height / 2)
    if "additive" in e["blend"]:
        lay = Image.new("RGBA", rgb.size)
        lay.alpha_composite(fr, (x, y))
        return ImageChops.add(rgb, measure.light_of(lay))
    out = rgb.convert("RGBA")
    out.alpha_composite(fr, (x, y))
    return out.convert("RGB")


def night(rgb, d):
    """E3 mock-up: the machine darkened as the Core's night, the melt's light pool round the tower's foot."""
    e = FX["ground-light-e3"]
    dark = Image.blend(rgb, Image.new("RGB", rgb.size, (0, 0, 0)), 0.72)
    lay = Image.new("RGB", rgb.size)
    pxl = lay.load()
    cx, cy = C / 2 + e[f"{d}_position"][0] * PPT, C / 2 + e[f"{d}_position"][1] * PPT
    rad = e["light"]["size"] / 2 * PPT * 0.55
    col = [round(255 * c) for c in e["light"]["color"]]
    for y in range(C):
        for x in range(C):
            q = math.hypot(x - cx, y - cy) / rad
            if q < 1:
                f_ = e["light"]["intensity"] * (1 - q) ** 2
                pxl[x, y] = tuple(round(c * f_) for c in col)
    return ImageChops.add(dark, ImageChops.multiply(lay, Image.new("RGB", rgb.size, (255, 255, 255))))


def tick_frame(name, tick):
    e = FX[name]
    return math.floor(tick * e["animation_speed"])


def with_fx(d, tick, names=("wisp-a2", "embers-e2", "cold-breath-e4", "purge-e5")):
    f = math.floor(tick * 0.2) % NF
    rgb = Image.new("RGB", (C, C + TOP), GROUND)
    rgb.paste(compose(d, f, working=True, shadow=True, lenses=("lens-working",)), (0, TOP))
    for n in names:
        if n == "cold-breath-e4" and d == "south":
            continue                            # behind the tower facing south: Liam's question
        k = f if not FX[n]["constant_speed"] else tick_frame(n, tick)
        rgb = fx_place(rgb, n, d, k)
    return rgb


sheets_row = []
for n in ("wisp-a2", "embers-e2", "cold-breath-e4", "purge-e5"):
    e = FX[n]
    frs = [fx_frame(n, k) for k in range(e["frame_count"])]
    bgim = [Image.alpha_composite(Image.new("RGBA", fr.size, GROUND + (255,)), fr) if "additive" not in e["blend"]
            else ImageChops.add(Image.new("RGB", fr.size, GROUND), measure.light_of(fr)).convert("RGBA") for fr in frs]
    step = max(1, e["frame_count"] // 12)
    sheets_row.append(captioned(row([b.convert("RGB") for b in bgim[::step]], 2),
                                [f"{n}: {e['frame_count']} frames {e['width']}x{e['height']} at scale 0.5, speed {e['animation_speed']}"
                                 + (" (constant)" if e["constant_speed"] else " (synced to the loop)"),
                                 e["what"][:120], f"checks {e['checks']}"]))
mock = []
for d in DIRS:
    ims = [with_fx(d, t) for t in (5, 25, 45, 70)]
    nt = Image.new("RGB", (C, C + TOP), tuple(round(c * 0.28) for c in GROUND))
    nt.paste(night(compose(d, 4, working=True, shadow=False), d), (0, TOP))
    cr, box = crop_content(ims, pad=10)
    cr.append(nt.crop(box))
    mock.append(captioned(row([up(x, 2) for x in cr], 4),
                          [f"{d}: ticks 5, 25, 45, 70 (the wisp, the embers, a charge's cold breath and purge puff); last: E3 at night",
                           "positions per direction from model.json (the model's own anchors)" + ("; E4 not drawn (behind the tower)" if d == "south" else "")]))
lines = []
for n, e in FX.items():
    pos = ", ".join(f"{d[0].upper()} {tuple(e[f'{d}_position'])}" for d in DIRS)
    if "light" in e:
        lines.append(f"{n}: light {e['light']}; positions {pos}")
    else:
        lines.append(f"{n}: {e['file']} {e['width']}x{e['height']} x{e['frame_count']} line {e['line_length']}, scale 0.5, speed "
                     f"{e['animation_speed']}, {'constant_speed' if e['constant_speed'] else 'synced'}, {e['blend']}, layer "
                     f"{e['render_layer']}; shift {tuple(e['shift'])}; positions {pos}")
save(column([text_block("6. The effects (Liam, 2026-10-21): A2 wisp, E2 embers, E3 ground light, E4 cold breath, E5 purge puff", [
    "Drawn by effects.py (PIL, procedural; not Blender volumes, not vanilla's files). Each is one working_visualisation of the drill, "
    "placed per direction as the chemical plant places its smoke (north_position ... west_position); E3 is a light, not a sheet.",
    "Mock-ups below are composed from the sheets at those positions (unchecked in a client)."] + lines, W),
    wrap_rows(sheets_row, W, 18), wrap_rows(mock, W, 18)]), "review-t07c-effects.png")

# ---------------------------------------------------------------- the GIFs (1x; 2x to scratch)
def loop(d_list, k=1, fx=False):
    frames = []
    for t in range(0, 120, 5):              # 24 frames, a frame every 5 ticks at speed 0.2: the 2 s loop
        ims = [with_fx(d, t) if fx else compose(d, t // 5, working=True, shadow=True, lenses=("lens-working",)) for d in d_list]
        frames.append(ims)
    _, box = crop_content([im for ims in frames for im in ims], pad=6)
    return [row([up(im.crop(box), k) if k > 1 else im.crop(box) for im in ims], 8) for ims in frames]


DUR = [80, 90, 80] * 8                       # ms, 83.3 on average: 5 ticks at 60 a second
for name, fr in (("motion-1x.gif", loop(DIRS)), ("effects-1x.gif", loop(DIRS, fx=True))):
    p = os.path.join(A.out, name)
    fr[0].save(p, save_all=True, append_images=fr[1:], duration=DUR, loop=0, optimize=True)
    print(p, os.path.getsize(p))
fr2 = loop(("north",), k=2, fx=True)
p2 = os.path.join(A.scratch, "motion-2x.gif")
fr2[0].save(p2, save_all=True, append_images=fr2[1:], duration=DUR, loop=0)
print(p2)
