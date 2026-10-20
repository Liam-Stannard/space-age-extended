#!/usr/bin/env python3
"""Vent Pump model (T07): the review sheet, the 1x GIFs at the candidate speeds, and the proposals.

  python3 -B review_sheet.py --run <render.sh out-dir> --measure <measure.py --out of that run>
        --before <sheets dir: round 5's south footing> --before-measure <measure.py --out of it>
        --after <sheets dir: the fixed footing, packed the same way> --after-measure <its measure.py --out>
        --r5 <round 5 (a)'s own renders: vpb5_08_gas_lift_tower.py --variant a --frames 1 --norot>
        --out <concept/vent-pump/model> --scratch <dir for the 2x GIF and the parts>

Writes into --out:
  review.png, review-2.png   the sheet, two pages (each under 8000 px a side): the new plate beside round 5 (a)'s on the same
                         ground at the same scale, idle and working; the four directions; the pumpjack,
                         chemical plant and foundry beside it at 1x; a frame strip of every animation; the
                         south join before and after; the two lenses; the stray-light map; the boil-off
                         wisp's spots and looks and the effect options (mock-ups); the figures
  motion-1x-speed-<s>.gif  the working loop at 1x, the four directions, at animation_speed s
                         (0.2 proposed, 0.3 and 0.4 beside it)
  and into --scratch: motion-2x.gif (not for git), the parts of the sheet.

Everything drawn here is composed from the packed sheets (pack.py's meta.json: each sheet at its shift),
as measure.py composes them: shadows at half strength, glows added as light, the lenses' white cuts
tinted and added as the engine adds a glow. The wisp and effect panels are mock-ups composited from
vanilla's own smoke and spark sprites, not the engine: they show a place and a look for Liam to pick.
"""
import argparse
import json
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import contract  # noqa: E402
import measure  # noqa: E402
import pack  # noqa: E402

ap = argparse.ArgumentParser()
for k in ("run", "measure", "before", "before_measure", "after", "after_measure", "r5", "out", "scratch"):
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
MEAS = json.load(open(os.path.join(A.measure, "measures.json")))
C = DECL["canvas"][0]
NF = 24
LENS = ("lens-working", "lens-no-fluid")       # each a glow (lit lens minus plate) and a halo (white light cut)
HALO = {"lens-working": (0.30, 1.0, 0.35), "lens-no-fluid": (1.0, 0.66, 0.12)}


def font(n, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if bold else "") + ".ttf", n)


F1, F2, FB = font(13), font(11), font(16, True)


# ---------------------------------------------------------------- the packed sheets, placed
_cache = {}


def sheet(stem):
    if stem not in _cache:
        _cache[stem] = Image.open(os.path.join(A.run, "sheets", stem + ".png")).convert("RGBA")
    return _cache[stem]


def placed(stem, f=0, canvas=C):
    m = META[stem]
    w, h = m["size"]
    im = sheet(stem)
    if "frames" in m:
        ll = m["line_length"]
        im = im.crop(((f % ll) * w, (f // ll) * h, (f % ll) * w + w, (f // ll) * h + h))
    out = Image.new("RGBA", (canvas, canvas))
    out.alpha_composite(im, (round(canvas / 2 + m["shift"][0] * PPT - w / 2), round(canvas / 2 + m["shift"][1] * PPT - h / 2)))
    return out


def add_light(rgb, light):
    return ImageChops.add(rgb, light)


def tinted(alpha_im, tint, k=0.95):
    a = alpha_im.getchannel("A")
    return Image.merge("RGB", [a.point(lambda v, t=t: round(v * t * k)) for t in tint])


def compose(d, f=0, working=True, shadow=True, lenses=(), ground=GROUND, halo=False):
    """The machine as drawn in direction d at frame f: ground, shadow at half strength, the plate, the
    working layer while working, each lit lens's glow added (and its halo, tinted, when halo)."""
    out = Image.new("RGBA", (C, C), ground + (255,))
    if shadow:
        sh = placed(f"shadow-{d}")
        a = sh.getchannel("A").point(lambda v: v // 2)
        out.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (C, C)).split(), a)))
    out.alpha_composite(placed(f"base-{d}"))
    if working:
        out.alpha_composite(placed(f"working-{d}", f))
    rgb = out.convert("RGB")
    for ln in lenses:
        rgb = add_light(rgb, measure.light_of(placed(f"{ln}-glow-{d}")))
        if halo:
            rgb = add_light(rgb, tinted(placed(f"{ln}-halo-{d}"), HALO[ln], 0.5))
    return rgb


def crop_content(ims, pad=10):
    box = None
    for im in ims:
        diff = ImageChops.difference(im.convert("RGB"), Image.new("RGB", im.size, GROUND)).getbbox()
        if diff:
            box = diff if box is None else (min(box[0], diff[0]), min(box[1], diff[1]), max(box[2], diff[2]),
                                            max(box[3], diff[3]))
    box = (max(0, box[0] - pad), max(0, box[1] - pad), min(C, box[2] + pad), min(C, box[3] + pad))
    return [im.crop(box) for im in ims], box


def up(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST if k >= 3 else Image.LANCZOS)


def captioned(im, lines, width=None, title=False):
    lines = [lines] if isinstance(lines, str) else lines
    fnt = FB if title else F1
    lh = 18 if title else 16
    w = max(im.width, width or 0)
    out = Image.new("RGB", (w, im.height + lh * len(lines) + 6), BG)
    dr = ImageDraw.Draw(out)
    for i, ln in enumerate(lines):
        dr.text((2, 2 + lh * i), ln, fill=HEAD if (i == 0) else TXT, font=fnt if i == 0 else F2)
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


# ---------------------------------------------------------------- 1. round 5 (a) beside the model
def r5(name):
    """Round 5 (a)'s own 4x render, at 1x, on this canvas (its kit put the origin at (160, 208) of 352)."""
    im = Image.open(os.path.join(A.r5, name)).convert("RGBa")
    im = im.resize((im.width // 4, im.height // 4), Image.LANCZOS).convert("RGBA")
    im = pack.roll(im)[0]                               # as everything shipped now is (pack.py's roll-off)
    out = Image.new("RGBA", (C, C))
    out.alpha_composite(im, (C // 2 - 160, C // 2 - 208))
    return out


def on(im, ground=GROUND):
    out = Image.new("RGBA", im.size, ground + (255,))
    out.alpha_composite(im)
    return out.convert("RGB")


r5_plate, r5_work = on(r5("plate.png")), on(r5("working-00.png"))
new_plate = compose("north", working=False, shadow=False)
new_work = compose("north", 0, working=True, shadow=False)
(cmp_ims, _) = crop_content([r5_plate, new_plate, r5_work, new_work], pad=8)
cmp_panels = [captioned(up(im, 2), [t, s]) for im, t, s in zip(
    cmp_ims, ("round 5 (a), plate", "T07 model, plate (base-north)", "round 5 (a), working frame 0",
              "T07 model, working frame 0"),
    ("idle: options/round-5, re-rendered", "idle: the melt and helium unlit", "its kit's light and catcher",
     "plate + the working layer, as packed"))]
block_r5 = column([text_block("1. The model beside round 5 (a), the adopted design: same ground, same scale (2x)", [
    "Round 5 (a) re-rendered from its own script (vpb5_08_gas_lift_tower.py --variant a --frames 1 --norot), its 4x render brought to 1x "
    "and rolled off as pack.py rolls off every shipped sheet.",
    "What the model changes (vent_pump.py's docstring): the south footing to the edge; the two lenses (the switchgear's moved to its "
    "south-east corner, (1.34, -0.32): at round 5's spot it was hidden behind the tower facing west); the crankcase 0.46 wide and the motor "
    "0.05 east so the coupling is seen (it stood inside them); the downcomer's foot east of the skimmings bin (it ran through it); the float "
    "lever's stub shortened (it swung into the tank head); the tool chest 0.05 east (on the bottles' feet); the riser's bubbles clear of its end caps.",
], 2400), row(cmp_panels)])

# ---------------------------------------------------------------- 2. the four directions, idle and working
dir_panels = []
for d in DIRS:
    idle = compose(d, working=False, shadow=True)
    work = compose(d, 0, working=True, shadow=True, lenses=("lens-working",))
    (ii, ww), _ = crop_content([idle, work], pad=6)
    m = MEAS["directions"][d]
    cv, tn = m["coverage"], m["tonal"]
    dir_panels.append(row([captioned(ii, [f"{d}: stopped", f"cover {cv['footprint_pct']} %, rise {cv['rise_tiles']} t"]),
                           captioned(ww, [f"{d}: working f0", f"p50 {tn['plate']['p50']}/{tn['still']['p50']} p95 {tn['plate']['p95']}"])], 6))
block_dirs = column([text_block("2. The four directions at 1x: stopped, and working (frame 0, the green lens lit)", [
    "The whole machine turned a quarter turn under the one camera (spec 5); the shadow at half strength, as measure.py draws it."], 2400),
    row(dir_panels, 18)])

# ---------------------------------------------------------------- 3. beside vanilla
refs = []
for name in ("pumpjack", "chemical-plant", "foundry"):
    label, foot, still, shadow, light = measure.vanilla(name, "north")
    im = Image.new("RGBA", still.size, GROUND + (255,))
    im.alpha_composite(shadow)
    im.alpha_composite(still)
    rgb = add_light(im.convert("RGB"), light)
    bb = ImageChops.difference(rgb, Image.new("RGB", rgb.size, GROUND)).getbbox()
    rgb = rgb.crop((bb[0] - 6, bb[1] - 6, bb[2] + 6, bb[3] + 6))
    v = MEAS["vanilla"][name]["north"]
    refs.append(captioned(rgb, [label, f"cover {v['coverage']['footprint_pct']} %, rise {v['coverage']['rise_tiles']} t, "
                                       f"p50 {v['tonal']['p50']} p95 {v['tonal']['p95']}"]))
ours = compose("north", 0, working=True, shadow=True)
(ours,), _ = crop_content([ours], pad=6)
m = MEAS["directions"]["north"]
block_van = column([text_block("3. Beside vanilla at 1x (north): the pumpjack, the chemical plant, the foundry", [
    "measure.py's references and figures (measures.json 'vanilla'); ours working frame 0, its shadow at half strength."], 2400),
    row([captioned(ours, ["Vent Pump (T07)", f"cover {m['coverage']['footprint_pct']} %, rise {m['coverage']['rise_tiles']} t, "
                                             f"p50 {m['tonal']['still']['p50']} p95 {m['tonal']['still']['p95']}"])] + refs, 24)])

# ---------------------------------------------------------------- 4. frame strips
REGIONS = (("the glass riser and the head tank's window", (0.0, -0.11, 1.6), 46, 150),
           ("the helium sight glass, the flow meter, the line gauge", (0.15, -0.75, 0.6), 64, 56),
           ("the float lever", (0.8, 0.05, 3.3), 44, 34),
           ("the compressor's coupling", (1.05, -0.95, 0.5), 30, 30),
           ("the receiver's gauge", (-0.94, -1.35, 0.62), 26, 24))
wf = [compose("north", f, working=True, shadow=False) for f in range(NF)]
(wfc, wbox) = crop_content(wf, pad=4)
strips = [captioned(column([row(wfc[:12], 3), row(wfc[12:], 3)], 3), ["the working layer (north), frames 0-23, 1x", "the whole machine lit"])]
for t, p, w, h in REGIONS:
    sx, sy = contract.screen(DECL, p, "north")
    cx, cy = C / 2 + sx, C / 2 + sy
    box = (round(cx - w / 2), round(cy - h / 2), round(cx + w / 2), round(cy + h / 2))
    k = 3 if h > 100 else 4
    fr = [up(fm.crop(box), k) for fm in wf]
    strips.append(captioned(column([row(fr[:12], 3), row(fr[12:], 3)], 3), [f"{t} (north), frames 0-23, {k}x"]))
lm = MEAS["directions"]["north"]["layers_alone"].get("working-north", {})
block_strips = column([text_block("4. The animation, frame by frame (north): the working layer whole at 1x, and its moving parts close up", [
    "One layer (render.json 'working', 24 frames, drawn only while working): spec 7's split cannot be packed in the four directions (see the "
    "questions). Its parts: bubbles up the riser, the melt flowing, the sight glass's level and flush, the meter, two gauges, the float "
    f"lever, the coupling. Layer alone: step px {min(lm.get('step_px') or [0])}-{max(lm.get('step_px') or [0])}, wrap {lm.get('wrap_px')}."],
    2400), wrap_rows(strips, 2400)])

# ---------------------------------------------------------------- 5. the south join, before and after
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))


def join_pics(sheets_dir, dn="north", conn=(0, 1, "S")):
    src = measure.Source(sheets_dir, (3, 3), "four", "base")       # a sheets dir with no ports/: no picture
    sc = measure.Scene(src, dn)
    deg = dict(contract.DIRECTIONS["four"])[dn]
    res, (plain, marked) = measure.join(sc, measure.turn(conn, deg))
    return res, plain, marked


def gap_txt(res):
    g = res["gap"]
    return (f"{'PASS' if res['pass'] else 'FAIL'}: {g['columns']} gap column(s) of "
            f"{res['pipe_body']['width_px']}, most {g['max_ground_px']} px")


jb = []
for tag, d_, md in (("before: round 5's footing (y -1.18)", A.before, A.before_measure),
                    ("after: the footing to the edge (y -1.485)", A.after, A.after_measure)):
    res, plain, marked = join_pics(d_)
    jb.append(captioned(row([plain.resize((400, 400)), marked.resize((400, 400))], 6), [tag, gap_txt(res)]))
jm = MEAS["directions"]
jlines = []
for d in DIRS:
    for j in jm[d]["joins"]:
        g = j["gap"]
        jlines.append(f"{d} {j['connection']}: {'PASS' if j['pass'] else 'FAIL'} ({j['why'] if not j['pass'] else 'no gap'}); "
                      f"gap columns {g['columns']}, most {g['max_ground_px']} px")
block_join = column([text_block("5. The south join, before and after (measure.py's join at 4x: plain, and gap columns marked red)", [
    "Both pictures: the still (north) and vanilla's pipe on the next tile, WITHOUT the model's pipe picture (as round 5 was measured), so the "
    "footing's own effect shows. With the model's port-S picture over it (as the engine draws a connected pipe) both pass.",
    "Round 5's own measure (no pipe pictures then): FAIL, 7 of 39 columns, up to 6 px. The fix: the inlet footing carried out under the nozzle "
    "to the edge (Liam: 'Fix in the model'); the nozzle itself unchanged.",
    "The full run, every connection in every direction:"] + jlines, 2400), row(jb, 30)])

# ---------------------------------------------------------------- 6. the lenses
lens_panels = []
d = "north"
states = (("stopped, nothing amiss: both unlit", (), False), ("working: the control house's green (glow)", ("lens-working",), False),
          ("input fluid missing: the switchgear's amber (glow)", ("lens-no-fluid",), False),
          ("working, with its halo (dark only)", ("lens-working",), True),
          ("fluid missing, with its halo (dark only)", ("lens-no-fluid",), True))
ims = [compose(d, 0, working=False, shadow=False, lenses=ls, halo=h) for _, ls, h in states]
boxes = [placed(f"{ln}-halo-{d}").getbbox() for ln in LENS]
bx = (min(b[0] for b in boxes) - 26, min(b[1] for b in boxes) - 22, max(b[2] for b in boxes) + 22, max(b[3] for b in boxes) + 26)
for (t, _, _), im in zip(states, ims):
    lens_panels.append(captioned(up(im.crop(bx), 5), [t, "5x, north"]))
for t, im in zip(("1x, working", "1x, fluid missing"), ims[1:3]):
    (c1,), _ = crop_content([im], pad=4)
    lens_panels.append(captioned(c1, [t]))
lt = MEAS["directions"]["north"]["light"]
gl = MEAS["directions"]["north"]["glow"]
block_lens = column([text_block("6. The two status lenses (Liam, 2026-10-20, after T07b): a glow sprite each, lit and unlit, plus a light halo", [
    "Lit: sheets lens-working-glow / lens-no-fluid-glow -- the lens lit in its own colour (#46F05A, #FF9A12) minus the plate, a glow pass "
    "(draw_as_glow: seen by day and by night). Unlit: the plate's own lens (green glass, amber glass), always drawn.",
    "Halo: lens-working-halo / lens-no-fluid-halo, white cuts the engine tints and shows only in the dark (tinted here at half strength).",
    f"glow figures: " + "; ".join(f"{k}: peak {v.get('peak')}, area {v.get('area')}" for k, v in gl.items() if k.startswith("lens")),
    "halo figures: " + "; ".join(f"{k}: px {v.get('px_range')}" for k, v in lt.items()),
    "T07b's note: a lit amber glow samples about (255,108,14) at night and (255,153,0) at noon. The wiring drives them by status "
    "(green: working, low power; amber: missing_required_fluid only).",
    "Each lens is the round-5 kit's (r 0.032 tile): about 3-4 px across at 1x."], 2400), row(lens_panels, 16)])

# ---------------------------------------------------------------- 7. stray light
from PIL import ImageFilter  # noqa: E402
import glob  # noqa: E402


def quarter(p):
    im = Image.open(p).convert("RGBa")
    return im.resize((im.width // 4, im.height // 4), Image.LANCZOS).convert("RGBA")


stray_panels, stray_lines = [], []
for d in DIRS:
    plate = compose(d, working=False, shadow=False)
    mapim = Image.blend(plate, Image.new("RGB", plate.size, (0, 0, 0)), 0.55)
    px = mapim.load()
    masks = {g: quarter(os.path.join(A.run, "masks", f"{g}-{d}.png")).getchannel("A").point(lambda v: 255 if v > 8 else 0)
             .filter(ImageFilter.MaxFilter(3)) for g in ("riser", "glass")}
    both_ = ImageChops.lighter(masks["riser"], masks["glass"])
    worst = None
    for p in sorted(glob.glob(os.path.join(A.run, "masks", f"light-{d}-*.png"))):
        light = measure.light_of(quarter(p))
        L = light.convert("L").point(lambda v: 255 if v > 8 else 0)
        off = ImageChops.multiply(L, ImageChops.invert(both_))
        n_off, n_on = measure.count(off), measure.count(ImageChops.multiply(L, both_))
        if worst is None or n_off > worst[0]:
            worst = (n_off, n_on, p, L, off)
    n_off, n_on, p, L, off = worst
    Ld, Od, Rd = L.load(), off.load(), masks["riser"].load()
    for y in range(C):
        for x in range(C):
            if Od[x, y]:
                px[x, y] = (255, 0, 255)
            elif Ld[x, y]:
                px[x, y] = (255, 150, 40) if Rd[x, y] else (170, 130, 255)
    stray_lines.append(f"{d}: lit px (light alone, luminance > 8) {n_on} on the melt or the glass, {n_off} off both "
                       f"(the most, {os.path.basename(p)})")
    (mi,), _ = crop_content([mapim], pad=4)
    stray_panels.append(captioned(up(mi, 2), [d, "orange: on the melt; violet: on the glass; magenta: off both"]))
block_stray = column([text_block("7. Stray light (model-stage check): the light alone mapped to the melt or the helium glass", [
    "The melt and the helium lit with the sun and sky off (every other frame, not packed: run/masks/light-*), its lit pixels against "
    "silhouettes of the riser's melt, glass and window and of the sight glass, grown 1 px for the anti-aliased rim; the frame with the most off them."]
    + stray_lines, 2400), row(stray_panels, 16)])

# ---------------------------------------------------------------- 8. the boil-off wisp and the effects (mock-ups)
SMOKE = Image.open(os.path.join(FD, "base/graphics/entity/smoke/smoke.png")).convert("RGBA")
SPARK = Image.open(os.path.join(FD, "base/graphics/entity/sparks/sparks-01.png")).convert("RGBA")


def smoke_frame(k):
    k %= 60
    return SMOKE.crop(((k % 5) * 152, (k // 5) * 120, (k % 5) * 152 + 152, (k // 5) * 120 + 120))


def puff(canvas_rgb, at, tint, n=6, rise=44, s0=0.22, s1=0.7, a0=1.0, drift=9, seed=0):
    """A trivial smoke's particles as the engine spreads them: n of them up a rising path from `at`,
    growing from s0 to s1 and fading -- the vanilla smoke sprite, tinted (colour times the sprite)."""
    out = canvas_rgb.convert("RGBA")
    for i in range(n):
        u = i / max(1, n - 1)
        fr = smoke_frame(seed * 7 + i * 11)
        s = s0 + (s1 - s0) * u
        fr = fr.resize((max(1, round(152 * s)), max(1, round(120 * s))), Image.LANCZOS)
        r, g, b, a = fr.split()
        fr = Image.merge("RGBA", (r.point(lambda v: min(255, round(v * tint[0]))), g.point(lambda v: min(255, round(v * tint[1]))),
                                  b.point(lambda v: min(255, round(v * tint[2]))),
                                  a.point(lambda v: round(v * tint[3] * a0 * (1 - 0.7 * u)))))
        x = at[0] + drift * u - fr.width / 2
        y = at[1] - rise * u - fr.height / 2
        out.alpha_composite(fr, (round(x), round(y)))
    return out.convert("RGB")


def sparks(canvas_rgb, at, n=14, seed=3):
    import random
    rnd = random.Random(seed)
    out = canvas_rgb.copy()
    lay = Image.new("RGB", out.size)
    w = SPARK.width // 8 if SPARK.width >= 8 * 16 else SPARK.width
    for i in range(n):
        x, y = at[0] + rnd.uniform(-12, 12), at[1] + rnd.uniform(-14, 2)
        r = rnd.uniform(1.0, 2.0)
        d = ImageDraw.Draw(lay)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 150 + rnd.randint(0, 50), 60))
    return ImageChops.add(out, lay)


def glow_pool(canvas_rgb, at, radius=70, colour=(230, 110, 40), k=0.9):
    lay = Image.new("RGB", canvas_rgb.size)
    px = lay.load()
    for y in range(max(0, at[1] - radius), min(C, at[1] + radius)):
        for x in range(max(0, at[0] - radius), min(C, at[0] + radius)):
            q = math.hypot((x - at[0]) / radius, (y - at[1]) / (radius * 0.7))
            if q < 1:
                f_ = k * (1 - q) ** 2
                px[x, y] = tuple(round(c * f_) for c in colour)
    return ImageChops.add(canvas_rgb, lay)


def scr(p, d="north"):
    sx, sy = contract.screen(DECL, p, d)
    return (round(C / 2 + sx), round(C / 2 + sy))


TX, TY, ZT = 0.0, 0.18, 3.25
SPOTS = (("A: the head tank's gas offtake", (TX + 0.2, TY, ZT + 0.33), "where the helium breaks out of the melt"),
         ("B: the head tank's manway", (TX - 0.12, TY + 0.05, ZT + 0.36), "the tank's top hatch, west of the offtake"),
         ("C: the float chamber's cap", (TX + 0.62, TY, ZT + 0.2), "the vent on the float chamber, east"))
LOOKS = (("1: pale warm vapour", (1.15, 1.08, 1.0, 0.55), "light-smoke's grey, warmed: steam off the melt"),
         ("2: melt-lit fume", (1.3, 0.85, 0.6, 0.6), "lit from below by the melt, orange-grey"),
         ("3: cold helium boil-off", (1.15, 1.18, 1.3, 0.5), "pale and cool; the cold is the effect's, never the model's"))
work_n = compose("north", 4, working=True, shadow=True)
wisp_panels = []
for sname, sp, sdesc in SPOTS:
    for lname, tint, ldesc in LOOKS:
        im = puff(work_n, scr(sp), tint)
        cx, cy = scr((TX, TY, ZT))
        box = (cx - 80, max(0, cy - 110), cx + 80, cy + 40)
        wisp_panels.append(captioned(up(im.crop(box), 2), [f"{sname} x {lname}", f"{sdesc}; {ldesc}"]))
eff = []
base = compose("north", 4, working=True, shadow=True)
bx_all = None
(bc,), bx_all = crop_content([base], pad=26)
bx_all = (bx_all[0], max(0, bx_all[1] - 50), bx_all[2], bx_all[3])
E = [("E1: the boil-off wisp (above)", puff(base, scr(SPOTS[0][1]), LOOKS[0][1]),
      "a trivial-smoke from the tower top, working only (mining drill working_visualisations / smoke)"),
     ("E2: embers off the skimmings bin", sparks(base, scr((-0.92, 0.95, 0.8))),
      "a few sparks or embers over the slag in the bin (vanilla sparks), working only"),
     ("E3: the melt's light on the ground", glow_pool(base, scr((0.0, -0.11, 0.3))),
      "a light_source round the tower's foot, orange, working only (the riser lights the ground)"),
     ("E4: cold breath at the helium inlet", puff(base, scr((0, -1.06, 0.7)), (1.25, 1.28, 1.35, 0.7), n=4, rise=26, s0=0.18,
                                                  s1=0.5, drift=4, seed=2),
      "a faint cold vapour off the stop valve at each charge (cold from effects, never the model)"),
     ("E5: a purge puff at each charge", puff(base, scr(SPOTS[2][1]), (1.1, 1.0, 1.25, 0.55), n=4, rise=22, s0=0.14, s1=0.38,
                                               drift=3, seed=5),
      "a small violet-grey puff from the float chamber as each charge breaks out, synced to the loop"),
     ]
for t, im, desc in E:
    eff.append(captioned(up(im.crop(bx_all), 2), [t, desc[:90], desc[90:]]))
block_fx = column([text_block("8. Proposals for Liam (mock-ups composited from vanilla's smoke and spark sprites, not the engine): "
                              "the boil-off wisp, three spots x three looks; and effect options", [
    "Only while working. The wisp is drawn as the engine spreads a trivial-smoke: particles rising from the spot, growing and fading.",
    "Not shown, also possible: E6 heat shimmer over the head tank (the engine has no distortion pass: not available); E7 the riser's glow "
    "pulsing brighter with each charge (already in the glow); E8 a short spark from the switchgear when the fluid runs out (with the amber).",
], 2400), wrap_rows(wisp_panels, 2400, 10), wrap_rows(eff, 2400, 14)])

# ---------------------------------------------------------------- the GIFs and the speed proposal
def loop(d_list, k=1):
    frames = []
    for f in range(NF):
        ims = [compose(d, f, working=True, shadow=True, lenses=("lens-working",)) for d in d_list]
        cr, _ = crop_content(ims, pad=6) if f == 0 else (None, None)
        frames.append(ims)
    _, box = crop_content(frames[0], pad=6)
    out = []
    for ims in frames:
        r_ = row([up(im.crop(box), k) if k > 1 else im.crop(box) for im in ims], 8)
        out.append(r_)
    return out


fr1 = loop(DIRS)
fr1n = loop(("north",))
SPEEDS = {0.2: [80, 90, 80], 0.3: [60, 50, 60, 50, 60, 50, 60, 50, 50], 0.4: [40, 40, 40, 50, 40, 40]}   # ms, averaging 1000 / (60 s)
gifs = {}
for s, pat in SPEEDS.items():
    p = os.path.join(A.out, f"motion-1x-speed-{s}.gif")
    dur = [pat[i % len(pat)] for i in range(NF)]
    fr = fr1 if s == 0.2 else fr1n
    fr[0].save(p, save_all=True, append_images=fr[1:], duration=dur, loop=0, optimize=True)
    gifs[s] = (p, os.path.getsize(p), sum(dur))
fr2 = loop(("north",), k=2)
p2 = os.path.join(A.scratch, "motion-2x.gif")
fr2[0].save(p2, save_all=True, append_images=fr2[1:], duration=[SPEEDS[0.2][i % 3] for i in range(NF)], loop=0)
mo = MEAS["directions"]["north"]["motion"]
block_speed = text_block("9. The loop's speed (spec 9: 'proposed at the model stage'; Liam picks)", [
    "Proposed: animation_speed 0.2 -- 24 frames over 120 ticks, a 2.0 s loop, a frame every 5 ticks; one helium charge a second.",
    "Why: the Vent Pump mines once a second (mining_speed 1, the melt vent's mining_time 1) and burns 10 helium-3 each time; at 0.2 each of "
    "the loop's two charges lasts one mining operation, so the glass drops once per 10 helium spent.",
    "At 0.3 (1.33 s, the pumpjack's own stroke: 40 frames at 0.5) the meter's race and the glass's flush read busier; at 0.4 (1.0 s) they "
    "flicker at 1x (a frame every 2.5 ticks; the riser's bubbles step 2 px a frame).",
    f"GIFs (1x, the green lens lit; 0.2 the four directions, 0.3 and 0.4 north): " + "; ".join(f"{s}: {os.path.basename(p)} ({sz // 1024} KB, {t} ms)"
                                                                   for s, (p, sz, t) in gifs.items()),
    f"Declared in render.json at 0.2, so measure.py's timing is the proposal's: loop {mo.get('timing', {}).get('loop_ticks')} ticks; "
    f"moving {mo['moving_pct']} %, strobe {mo['strobe_pct']} % ({mo['strobe_px']} px).",
], 2400)

# ---------------------------------------------------------------- the figures
R5 = dict(cover=95.9, rise=0.77, p50="79 / 77", p95="170 / 169", white=0, clipped=0, he_peak=122, pale=0, strobe=0.29,
          north="pass", south="fail: 7 of 39 columns, up to 6 px")
fig = ["direction | cover % | rise t | p50 plate/still | p95 plate/still | white | clipped | blue/pale | strobe % | moving % | joins N-side / S-side",
       "round 5 (a) (the spec's 'must keep') | 95.9 | 0.77 | 79 / 77 | 170 / 169 | 0 | 0 | 0 / 0 | 0.29 | 2.67 | pass / fail 7 of 39"]
for d in DIRS:
    m = MEAS["directions"][d]
    cv, tn, co, mo_ = m["coverage"], m["tonal"], m["colour"], m["motion"] or {}
    js = " / ".join(("pass" if j["pass"] else "FAIL") + f" {j['connection'][2]}" for j in m["joins"])
    fig.append(f"{d} | {cv['footprint_pct']} | {cv['rise_tiles']} | {tn['plate']['p50']} / {tn['still']['p50']} | "
               f"{tn['plate']['p95']} / {tn['still']['p95']} | {co['white_px']} | {co['clipped_px']} | {co['blue_px']} / {co['pale_px']} | "
               f"{mo_.get('strobe_pct')} | {mo_.get('moving_pct')} | {js}")
g = MEAS["directions"]["north"]["glow"]
fig.append("glow (north, frame 0): " + "; ".join(f"{k} peak {v.get('peak')}" for k, v in g.items()))
fig.append(f"collide: {'PASS' if (MEAS.get('collide') or {}).get('pass') else (MEAS.get('collide') or {}).get('why', 'run by render.sh --collide')}; "
           f"gates {MEAS['gates']}")
block_fig = text_block("Figures (measure.py, tools/blender/measure.py, every direction; ours beside round 5 (a)'s, the spec's 'must keep')",
                       fig, 2400)

# ---------------------------------------------------------------- the sheet
title = text_block("Vent Pump -- the shipping model (T07): the Gas Lift Tower, round 5 (a), through render.sh --ports --icon", [
    "concept/vent-pump/model/vent_pump.py, its kit copied from round 5 into model/kit/. Four directions, the whole machine turned. "
    "Nothing in graphics/; Liam signs off (T08).",
], 2400)
blocks = [title, block_fig, block_r5, block_dirs, block_van, block_join, block_lens, block_strips, block_stray, block_fx, block_speed]
for i, b in enumerate(blocks):
    b.save(os.path.join(A.scratch, f"part-{i:02d}.png"))
W = 2440
PAGES = (("review.png", blocks[:7]), ("review-2.png", [blocks[0]] + blocks[7:]))
for name, bl in PAGES:
    sheet_ = column(bl, 30, W)
    pad = Image.new("RGB", (sheet_.width + 40, sheet_.height + 40), BG)
    pad.paste(sheet_, (20, 20))
    assert max(pad.size) < 8000, (name, pad.size)
    p = os.path.join(A.out, name)
    pad.save(p, optimize=True)
    print(p, pad.size)
for s, (gp, sz, t) in gifs.items():
    print(gp, sz)
print(p2, os.path.getsize(p2))
