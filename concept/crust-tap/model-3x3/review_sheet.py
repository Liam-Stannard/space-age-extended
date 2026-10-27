#!/usr/bin/env python3
"""Gas Pump 3x3 model (gas-pump-3x3 T08): the review sheet, the clipping crops and the 1x GIF.

  python3 -B review_sheet.py --run <render.sh out-dir> --measure <measure.py --out of that run>
        --concept <the concept's own renders: options/round-3x3-refine/gp_2_flywheel_compressor.py -- <dir>>
        --concept-sheets <gp_pack.py's sheets of those renders> --concept-measure <its measures.json>
        --tints <gas_pump.py --tints out-dir> --before <a render.sh out-dir of gas_pump.py --outlet stub>
        --out <concept/crust-tap/model-3x3> --scratch <dir>

Writes into --out:
  review.png             the new plate beside the concept's on one ground at one scale (2x), idle and working, in
                         both gases; the four directions beside the concept's turned renders; the model, the concept
                         and the pumpjack at 1x; the glass as the engine tints it beside the gas painted in Blender;
                         the lubricator through the loop; a frame strip of every animation; the figures
  review-crops.png       the clipping check by eye: every run's two ends at 4x and its whole course at 3x, in all
                         four directions, from the still (the stopped machine as packed)
  fitting-4x.png         the outlet's fitting at 4x in every direction, connected and unconnected (the review's 8.)
  gas-pump-working-1x.gif  the working loop at 1x and at game speed (one turn a second), the four directions,
                         siderane above and helium-3 below
and into --scratch: gas-pump-working-2x.gif (not for git).

Every model panel is composed from the packed sheets (pack.py's meta.json: each sheet at its shift), as
measure.py composes them: the shadow at half strength under the plate, the mech frame over it, and the glass's
white frame multiplied by the vent's tint (apply_tint = "resource-color", the 2x2 pump's wiring) over that.
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
import measure  # noqa: E402
import pack  # noqa: E402

ap = argparse.ArgumentParser()
for a in ("run", "measure", "concept", "concept_sheets", "concept_measure", "tints", "out", "scratch", "before"):
    ap.add_argument("--" + a.replace("_", "-"), required=True)
args = ap.parse_args()

DIRS = ("north", "east", "south", "west")
GROUND = (74, 66, 58, 255)
BG = (30, 29, 28, 255)
HEAD, SUB, TXT = (240, 200, 120), (175, 168, 156), (220, 214, 204)
GRID = (96, 88, 78, 255)
FOOT = (150, 138, 120, 255)
TINT = {"siderane": (0xA8, 0xD9, 0x29), "helium-3": (0xB6, 0xA6, 0xC8)}
NF = 24
SPEED = 0.4
CANVAS = 416
C_CANVAS, C_ORIGIN = 352, (160, 208)          # the concept's renders at 1x


def font(n, b=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if b else "") + ".ttf", n)


F_H, F_S, F_T = font(30, True), font(18, True), font(15)

# ---------------------------------------------------------------- the model, from its sheets
SHEETS = os.path.join(args.run, "sheets")
META = json.load(open(os.path.join(SHEETS, "meta.json")))
_cache = {}


def sheet(name):
    if name not in _cache:
        _cache[name] = Image.open(os.path.join(SHEETS, name + ".png")).convert("RGBA")
    return _cache[name]


def layer(name, f=0):
    """Sheet `name`'s frame f placed on the model's canvas (the origin at its centre)."""
    m = META[name]
    w, h = m["size"]
    im = sheet(name)
    if "frames" in m:
        ll = m.get("line_length", m["frames"])
        im = im.crop(((f % ll) * w, (f // ll) * h, (f % ll) * w + w, (f // ll) * h + h))
    out = Image.new("RGBA", (CANVAS, CANVAS))
    out.alpha_composite(im, (round(CANVAS / 2 + m["shift"][0] * 64 - w / 2), round(CANVAS / 2 + m["shift"][1] * 64 - h / 2)))
    return out


def half_shadow(im):
    a = im.getchannel("A").point(lambda v: v // 2)
    return Image.merge("RGBA", (*Image.new("RGB", im.size).split(), a))


def tinted(im, rgb):
    r, g, b, a = im.split()
    r = r.point(lambda v: v * rgb[0] // 255)
    g = g.point(lambda v: v * rgb[1] // 255)
    b = b.point(lambda v: v * rgb[2] // 255)
    return Image.merge("RGBA", (r, g, b, a))


def model(d, f=0, gas=None, mech=True, ground=True):
    """The model in direction d at frame f as the engine draws it: shadow, plate, mech, the glass tinted."""
    out = Image.new("RGBA", (CANVAS, CANVAS), GROUND if ground else (0, 0, 0, 0))
    out.alpha_composite(half_shadow(layer(f"shadow-{d}")))
    out.alpha_composite(layer(f"base-{d}"))
    if mech:
        out.alpha_composite(layer(f"mech-{d}", f))
    if gas:
        out.alpha_composite(tinted(layer(f"glass-{d}", f), TINT[gas]))
    return out


def grid(im, origin, foot, k):
    """The footprint's tiles over a panel at scale k (origin in panel px)."""
    d = ImageDraw.Draw(im)
    fw, fh = foot
    x0, y0 = origin[0] - fw / 2 * 64 * k, origin[1] - fh / 2 * 64 * k
    for i in range(fw + 1):
        d.line([(x0 + i * 64 * k, y0), (x0 + i * 64 * k, y0 + fh * 64 * k)], fill=GRID if 0 < i < fw else FOOT, width=1)
    for j in range(fh + 1):
        d.line([(x0, y0 + j * 64 * k), (x0 + fw * 64 * k, y0 + j * 64 * k)], fill=GRID if 0 < j < fh else FOOT, width=1)
    return im


def scaled(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def model_panel(d, f=0, gas=None, k=2):
    im = scaled(model(d, f, gas), k)
    grid(im, (CANVAS * k / 2, CANVAS * k / 2), (3, 3), k)
    return trim(im, k)


def trim(im, k, tiles=2.6):
    """A window `tiles` from the origin on each side (a 3x3 machine and its shadow), in panel px."""
    c = im.width / 2
    r = tiles * 64 * k
    return im.crop((round(c - r), round(c - r * 1.05), round(c + r), round(c + r * 0.95)))


# ---------------------------------------------------------------- the concept, from its renders and its gp_pack sheets
def c_load(name):
    """A concept render (4x, 352 px canvas at 1x, the origin at (160, 208)) at 1x, moved onto the model's canvas."""
    im = Image.open(os.path.join(args.concept, name)).convert("RGBA")
    im = im.resize((C_CANVAS, C_CANVAS), Image.LANCZOS) if im.width != C_CANVAS else im
    out = Image.new("RGBA", (CANVAS, CANVAS))
    out.alpha_composite(im, (CANVAS // 2 - C_ORIGIN[0], CANVAS // 2 - C_ORIGIN[1]))
    return out


CMETA = json.load(open(os.path.join(args.concept_sheets, "meta.json")))


def c_layer(name, f=0):
    m = CMETA[name]
    w, h = m["size"]
    im = Image.open(os.path.join(args.concept_sheets, name + ".png")).convert("RGBA")
    if "frames" in m:
        ll = m.get("line_length", m["frames"])
        im = im.crop(((f % ll) * w, (f // ll) * h, (f % ll) * w + w, (f // ll) * h + h))
    out = Image.new("RGBA", (CANVAS, CANVAS))
    out.alpha_composite(im, (round(CANVAS / 2 + m["shift"][0] * 64 - w / 2), round(CANVAS / 2 + m["shift"][1] * 64 - h / 2)))
    return out


def concept(f=None):
    """The concept facing north, from its gp_pack sheets as measure.py drew it: the shadow at half, the plate, and
    working frame f (the whole machine, the glass painted siderane) or the idle plate alone."""
    out = Image.new("RGBA", (CANVAS, CANVAS), GROUND)
    out.alpha_composite(half_shadow(c_layer("shadow")))
    out.alpha_composite(c_layer("base"))
    if f is not None:
        out.alpha_composite(c_layer("working", f))
    return out


def concept_panel(f=None, k=2):
    im = scaled(concept(f), k)
    grid(im, (CANVAS * k / 2, CANVAS * k / 2), (3, 3), k)
    return trim(im, k)


def concept_turned(d, k=2):
    """The concept's own turned render (working frame 0 over its catcher, shadow at the catcher's full strength)."""
    out = Image.new("RGBA", (CANVAS, CANVAS), GROUND)
    out.alpha_composite(c_load("working-00.png" if d == "north" else f"rot-{d}.png"))
    im = scaled(out, k)
    grid(im, (CANVAS * k / 2, CANVAS * k / 2), (3, 3), k)
    return trim(im, k)


# ---------------------------------------------------------------- the pumpjack (measure.py's reference)
def pumpjack(d, k=1):
    label, foot, still, shadow, light = measure.vanilla("pumpjack", d)
    S = still.width
    out = Image.new("RGBA", (S, S), GROUND)
    out.alpha_composite(shadow)
    out.alpha_composite(still)
    S2 = CANVAS
    can = Image.new("RGBA", (S2, S2), GROUND)
    can.alpha_composite(out.crop(((S - S2) // 2, (S - S2) // 2, (S + S2) // 2, (S + S2) // 2)) if S > S2 else out,
                        (0, 0) if S > S2 else ((S2 - S) // 2, (S2 - S) // 2))
    im = scaled(can, k)
    grid(im, (S2 * k / 2, S2 * k / 2), foot, k)
    return trim(im, k), label


# ---------------------------------------------------------------- layout
def captioned(im, title, lines=(), w=None):
    w = max(w or 0, im.width)
    lh = 22
    h = 28 + lh * len(lines)
    out = Image.new("RGBA", (w, im.height + h + 6), BG)
    out.alpha_composite(im, (0, h))
    d = ImageDraw.Draw(out)
    d.text((2, 2), title, font=F_S, fill=HEAD)
    for i, s in enumerate(lines):
        d.text((2, 28 + i * lh), s, font=F_T, fill=SUB)
    return out


def row(panels, gap=14):
    w = sum(p.width for p in panels) + gap * (len(panels) - 1)
    h = max(p.height for p in panels)
    out = Image.new("RGBA", (w, h), BG)
    x = 0
    for p in panels:
        out.alpha_composite(p, (x, 0))
        x += p.width + gap
    return out


def text_block(title, lines, width, mono=False):
    lh = 24 if mono else 22
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 18) if mono else F_T
    out = Image.new("RGBA", (width, 40 + lh * len(lines) + 8), BG)
    d = ImageDraw.Draw(out)
    d.text((0, 0), title, font=F_H if title.isupper() else F_S, fill=HEAD)
    for i, s in enumerate(lines):
        d.text((0, 40 + i * lh), s, font=f, fill=TXT)
    return out


def stack(blocks, gap=22, pad=24):
    w = max(b.width for b in blocks) + 2 * pad
    h = sum(b.height for b in blocks) + gap * (len(blocks) - 1) + 2 * pad
    out = Image.new("RGBA", (w, h), BG)
    y = pad
    for b in blocks:
        out.alpha_composite(b, (pad, y))
        y += b.height + gap
    return out


def pages(blocks, max_side=7999, gap=22, pad=24):
    """Split the blocks into pages under max_side tall (each block is narrower than max_side)."""
    out, cur, h = [], [], pad * 2
    for b in blocks:
        if cur and h + b.height + gap > max_side:
            out.append(stack(cur, gap, pad))
            cur, h = [], pad * 2
        cur.append(b)
        h += b.height + gap
    if cur:
        out.append(stack(cur, gap, pad))
    return out


# ================================================================ the figures
MS = json.load(open(os.path.join(args.measure, "measures.json")))
CM = json.load(open(args.concept_measure))


def figs(m):
    cov, ton, fin, col = m["coverage"], m["tonal"], m["finish"], m["colour"]
    mo = m.get("motion", {})
    return dict(cov=cov["footprint_pct"], corners=cov["corners_pct"], rise=cov["rise_tiles"],
                p50=ton["plate"]["p50"] if "plate" in ton else ton["p50"],
                p95=ton["plate"]["p95"] if "plate" in ton else ton["p95"],
                black=fin["plate"]["black_pct"] if "plate" in fin else fin["black_pct"],
                white=col.get("white_px"), clipped=col.get("clipped_px"),
                moving=mo.get("moving_pct"), strobe=mo.get("strobe_pct"))


MODEL_F = {d: figs(MS["directions"][d]) for d in DIRS}
CONCEPT_F = figs(next(iter(CM["directions"].values())))
PJ = MS.get("vanilla", {}).get("pumpjack", {})
PJ_F = figs(PJ.get("north") or next(iter(PJ.values()))) if PJ else None
JOINS = {d: MS["directions"][d].get("joins") for d in DIRS}


def join_txt(d):
    js = JOINS[d] or []
    return "; ".join(f"{'PASS' if j.get('pass') else 'FAIL'} ({j['gap']['columns']} gap columns of {j['gap']['of_columns']})"
                     for j in js) or "none"


def collide_txt():
    import re
    out = []
    for l_ in open(os.path.join(args.run, "collide", "collide.txt")).read().splitlines():
        m = re.match(r"COLLIDE (\w+) (moving|model): (\d+) clashes", l_)
        if m:
            out.append(f"{m.group(1)} {m.group(2)} {m.group(3)}")
    return ", ".join(out) + " clashes"


def fig_rows():
    hdr = f"{'':10s}{'cover %':>9s}{'rise':>7s}{'p50':>6s}{'p95':>6s}{'black %':>9s}{'white':>7s}{'clip':>6s}" \
          f"{'moving %':>10s}{'strobe %':>10s}"
    out = [hdr]

    def line(name, f):
        def v(x, fmt):
            return format(x, fmt) if isinstance(x, (int, float)) else format("-", ">" + fmt.split(".")[0].rstrip("df"))
        return (f"{name:10s}{v(f['cov'], '9.1f')}{v(f['rise'], '7.2f')}{v(f['p50'], '6d')}{v(f['p95'], '6d')}"
                f"{v(f['black'], '9.1f')}{v(f['white'], '7d')}{v(f['clipped'], '6d')}{v(f['moving'], '10.2f')}"
                f"{v(f['strobe'], '10.2f')}")
    for d in DIRS:
        out.append(line(d, MODEL_F[d]))
    out.append(line("concept", CONCEPT_F))
    if PJ_F:
        out.append(line("pumpjack", PJ_F))
    return out


# ================================================================ the sheet
W_PAGE = 3000
blocks = [text_block("GAS PUMP 3x3 -- THE SHIPPING MODEL (T08): THE FLYWHEEL COMPRESSOR", [
    "concept/crust-tap/model-3x3/gas_pump.py through tools/blender/render.sh --ports --icon --collide: the signed-off concept "
    "(round-3x3-refine, take 2) built verbatim, with Liam's T05 changes:",
    "the lubricator off the flywheel hub by a short rod (placed east of the flywheel; its lever rocks once a turn), the yellow "
    "weight kept, helium-3 #B6A6C8 / siderane #A8D929 in the glass (a white layer the engine tints with the vent's",
    "mining_visualisation_tint), the Vent Pump finish, the gas engine as art only, one flywheel turn a second (24 frames at "
    "animation_speed 0.4), the whole machine turned in four directions, the output at {0, -1} facing north.",
    "Every model panel is the packed sheets composed as the engine draws them: shadow at half, plate, mech frame, the glass tinted.",
], W_PAGE)]

# 1. north, 2x: concept beside model, idle and working, both gases
p = [captioned(concept_panel(None), "concept, idle (gp_pack sheets)"),
     captioned(model_panel("north", 0), "model, idle (plate + mech frame 0)"),
     captioned(concept_panel(6), "concept, working frame 6 (siderane, painted in Blender)"),
     captioned(model_panel("north", 6, "siderane"), "model, working frame 6, siderane"),
     captioned(model_panel("north", 6, "helium-3"), "model, working frame 6, helium-3 #B6A6C8")]
blocks.append(captioned(row(p[:2]), "1. NORTH, 2x, ONE GROUND: THE CONCEPT BESIDE THE MODEL, IDLE"))
blocks.append(captioned(row(p[2:]), "   NORTH, 2x: WORKING, THE CONCEPT BESIDE THE MODEL IN BOTH GASES"))

# 2. the four directions, 2x
for d in DIRS:
    blocks.append(captioned(row([captioned(concept_turned(d), f"concept {d} (its own render, catcher shadow full)"),
                                 captioned(model_panel(d, 0), f"model {d}, idle"),
                                 captioned(model_panel(d, 6, "siderane"), f"model {d}, working frame 6, siderane")]),
                            f"2. {d.upper()}, 2x" + (": THE OUTLET AT {0, -1}" if d == "north" else "")))

# 3. beside the pumpjack, 1x
pj = [pumpjack(d) for d in DIRS]
blocks.append(captioned(row([captioned(model_panel(d, 0, None, k=1), f"model {d}") for d in DIRS]
                            + [captioned(concept_panel(None, k=1), "concept")]
                            + [captioned(im, lab) for im, lab in pj[:2]]),
                        "3. 1x, AS THE GAME DRAWS IT: THE MODEL, THE CONCEPT AND THE PUMPJACK"))

# 4. the glass: the engine's tint of the white layer beside the gas painted in Blender (gas_pump.py --tints)
def tint_crop(path_or_im, box, k=4):
    im = path_or_im if isinstance(path_or_im, Image.Image) else Image.open(path_or_im).convert("RGBA")
    if im.width != CANVAS:
        im = im.resize((CANVAS, CANVAS), Image.LANCZOS)
    bg = Image.new("RGBA", im.size, GROUND)
    bg.alpha_composite(im)
    return scaled(bg.crop(box), k)


gl = layer("glass-north", 0)
gb = gl.getbbox()
box = (gb[0] - 14, gb[1] - 14, gb[2] + 14, gb[3] + 14)
tp = []
for gas, key in (("siderane", "siderane"), ("helium-3", "helium")):
    for f in (0, 6):
        eng = model("north", f, gas)
        tp.append(captioned(tint_crop(eng, box), f"{gas[:4]} f{f} engine"))
        tp.append(captioned(tint_crop(os.path.join(args.tints, f"tint-{key}-{f:02d}.png"), box), f"{gas[:4]} f{f} painted"))
tp.append(captioned(tint_crop(model("north", 0, None), box), "idle: empty"))
blocks.append(captioned(row(tp, gap=10), "4. THE SIGHT GLASS, 4x: THE WHITE LAYER AS THE ENGINE TINTS IT, BESIDE THE GAS "
                                         "PAINTED IN BLENDER (no ground shadow difference: the glass alone differs)"))

# 5. the lubricator through the loop, 4x
mo = json.load(open(os.path.join(args.run, "model.json")))
cx, cy = CANVAS / 2 + 0.38 * 64, CANVAS / 2 + 0.95 * 64      # the hub's east half and the lubricator, on the sprite
lbox = (round(cx - 46), round(cy - 34), round(cx + 46), round(cy + 34))
blocks.append(captioned(row([captioned(scaled(model("north", f, None).crop(lbox), 3), f"frame {f}")
                             for f in range(0, NF, 3)], gap=8),
                        "5. THE LUBRICATOR, 3x, EVERY THIRD FRAME: THE CRANK PIN ON THE HUB, THE ROD, THE LEVER ROCKING ONCE A TURN"))

# 6. frame strips: every frame of each animation, north
mech_bb = None
for f in range(NF):
    b = layer("mech-north", f).getbbox()
    mech_bb = b if mech_bb is None else (min(mech_bb[0], b[0]), min(mech_bb[1], b[1]), max(mech_bb[2], b[2]), max(mech_bb[3], b[3]))
mb = (mech_bb[0] - 4, mech_bb[1] - 4, mech_bb[2] + 4, mech_bb[3] + 4)
strip = []
for f in range(NF):
    im = Image.new("RGBA", (CANVAS, CANVAS), GROUND)
    im.alpha_composite(layer("mech-north", f))
    strip.append(captioned(scaled(im.crop(mb), 1), f"{f}"))
blocks.append(captioned(row(strip[:12], gap=6), "6. MECH, NORTH, 1x, ALONE ON THE GROUND: FRAMES 0-11"))
blocks.append(captioned(row(strip[12:], gap=6), "   MECH, FRAMES 12-23"))
gstrip = []
for f in range(NF):
    im = Image.new("RGBA", (CANVAS, CANVAS), GROUND)
    im.alpha_composite(layer("glass-north", f))
    gstrip.append(captioned(scaled(im.crop(box), 3), f"{f}"))
blocks.append(captioned(row(gstrip[:12], gap=6), "   GLASS (WHITE, BEFORE THE TINT), NORTH, 3x: FRAMES 0-11"))
blocks.append(captioned(row(gstrip[12:], gap=6), "   GLASS, FRAMES 12-23"))

# 8. the outlet's fitting (Liam's standing rule, 2026-10-21), 4x, every direction: connected (our pipe picture and a
# vanilla straight pipe on the next tile) and unconnected (vanilla's cover, the wiring's pipe_covers), beside the
# concept's stub (the --before run: gas_pump.py --outlet stub)
sys.path.insert(1, os.path.join(REPO, "tools"))
import paths  # noqa: E402  (tools/paths.conf: where this machine's Factorio is)
FD = os.path.join(paths.factorio_data(), "base", "graphics", "entity")
FACE = {"north": "N", "east": "E", "south": "S", "west": "W"}
INTO = {"N": (0, -2), "E": (2, 0), "S": (0, 2), "W": (-2, 0)}
PM = json.load(open(os.path.join(SHEETS, "ports", "meta.json")))


def at_tile(im, tile, shift=(0, 0), scale_half=False):
    if scale_half:
        im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
    out = Image.new("RGBA", (CANVAS, CANVAS))
    out.alpha_composite(im, (round(CANVAS / 2 + (tile[0] + shift[0]) * 64 - im.width / 2),
                             round(CANVAS / 2 + (tile[1] + shift[1]) * 64 - im.height / 2)))
    return out


def fitting_view(d, how, run_dir=None):
    f = FACE[d]
    tile = INTO[f]
    if run_dir:                                  # the before: the stub run's own still
        st = Image.open(os.path.join(run_dir, "renders", f"still-{d}.png")).convert("RGBA")
        sh = Image.open(os.path.join(run_dir, "renders", f"shadow-{d}.png")).convert("RGBA")
    else:
        st = Image.open(os.path.join(args.run, "renders", f"still-{d}.png")).convert("RGBA")
        sh = Image.open(os.path.join(args.run, "renders", f"shadow-{d}.png")).convert("RGBA")
    building = st.copy()
    out = Image.new("RGBA", (CANVAS, CANVAS), GROUND)
    out.alpha_composite(half_shadow(sh))
    # the pipe picture is drawn whether a pipe is joined or not (the foundry's arrangement, prototypes/derive.lua);
    # vanilla's cover goes over its open end when nothing is joined (always_draw_covers = false)
    psheets = os.path.join(run_dir or args.run, "sheets", "ports")
    pm = json.load(open(os.path.join(psheets, "meta.json")))[f"port-{f}"]
    port = Image.open(os.path.join(psheets, f"port-{f}.png")).convert("RGBA")
    pic = at_tile(port, tile, pm["shift"])
    if f == "N":                                 # a north picture is drawn behind the building (secondary_draw_orders
        under = pic                              # north = -1, as vanilla's assemblers set it)
        under.alpha_composite(building)
        building = under
    else:
        building.alpha_composite(pic)
    if how == "connected":
        pipe = at_tile(Image.open(os.path.join(FD, "pipe", "pipe-straight-" + ("vertical" if f in "NS" else "horizontal")
                                               + ".png")).convert("RGBA"), tile, scale_half=True)
        for lay in ((building, pipe) if tile[1] > 0 else (pipe, building)):
            out.alpha_composite(lay)
    else:
        name = {"N": "north", "E": "east", "S": "south", "W": "west"}[f]
        cov = Image.open(os.path.join(FD, "pipe-covers", f"pipe-cover-{name}.png")).convert("RGBA")
        csh = Image.open(os.path.join(FD, "pipe-covers", f"pipe-cover-{name}-shadow.png")).convert("RGBA")
        out.alpha_composite(half_shadow(at_tile(csh, tile, scale_half=True)))
        out.alpha_composite(building)
        out.alpha_composite(at_tile(cov, tile, scale_half=True))
    c = (CANVAS / 2 + (tile[0] * 0.75) * 64, CANVAS / 2 + (tile[1] * 0.75) * 64 - 10)
    return scaled(out.crop((round(c[0] - 40), round(c[1] - 40), round(c[0] + 40), round(c[1] + 40))), 4)


fit_blocks = []
for d in DIRS:
    fit_blocks.append(captioned(row([captioned(fitting_view(d, "unconnected", args.before), "before: the stub, unconnected"),
                                 captioned(fitting_view(d, "connected"), "connected: picture + pipe"),
                                 captioned(fitting_view(d, "unconnected"), "unconnected: picture + vanilla cover")]),
                            f"8. THE OUTLET'S FITTING, {d.upper()}, 4x" + (
                                ": A PAD WELDED ON THE BOTTLE, A FLANGED SLEEVE TO THE EDGE, THE BORE OPEN" if d == "north" else "")))
blocks += fit_blocks
stack(fit_blocks).convert("RGB").save(os.path.join(args.out, "fitting-4x.png"))

# 7. the figures
blocks.append(text_block("7. FIGURES (tools/blender/measure.py; the concept's from its T04 measures.json)",
                         fig_rows() + ["", "joins at the output {0, -1}: " + "; ".join(f"{d} {join_txt(d)}" for d in DIRS),
                                       "collide (render.sh --collide; the north, east and west variants): " + collide_txt()],
                         W_PAGE, mono=True))
for i, pg in enumerate(pages(blocks)):
    pg.convert("RGB").save(os.path.join(args.out, "review.png" if i == 0 else f"review-{i + 1}.png"))
    print("sheet", i + 1, pg.size)

# ================================================================ the clipping crops
STILLS = {d: Image.open(os.path.join(args.run, "renders", f"still-{d}.png")).convert("RGBA") for d in DIRS}


def on_ground(im):
    bg = Image.new("RGBA", im.size, GROUND)
    bg.alpha_composite(im)
    return bg


def mark(im, pts, k, colour=(255, 60, 200, 255)):
    d = ImageDraw.Draw(im)
    for x, y in pts:
        d.ellipse((x * k - 4, y * k - 4, x * k + 4, y * k + 4), outline=colour, width=2)
    return im


HALF = 22
crop_rows = [text_block("GAS PUMP 3x3 MODEL -- THE CLIPPING CHECK BY EYE", [
    "Every run the model registers (the kit's pipes, hoses and cables): its two ends at 4x (a ring marks the end) and its "
    "whole course at 3x, where it crosses other parts,",
    "in all four directions, from the still (the stopped machine as packed, on the ground). Moving rods are in the review's "
    "lubricator strip and the mech frames.",
], 2400)]
for run in mo["runs"]:
    cells = []
    for d in DIRS:
        st = on_ground(STILLS[d])
        for e in run["ends"]:
            sx, sy = e["screen"][d]
            x, y = CANVAS / 2 + sx * 64, CANVAS / 2 + sy * 64
            c = scaled(st.crop((round(x - HALF), round(y - HALF), round(x + HALF), round(y + HALF))), 4)
            mark(c, [(HALF, HALF)], 4)
            cells.append(captioned(c, f"{d} end"))
        pts = [(CANVAS / 2 + a * 64, CANVAS / 2 + b * 64) for a, b in run["course"][d]]
        x0, y0 = min(p_[0] for p_ in pts) - 10, min(p_[1] for p_ in pts) - 10
        x1, y1 = max(p_[0] for p_ in pts) + 10, max(p_[1] for p_ in pts) + 10
        c = scaled(st.crop((round(x0), round(y0), round(x1), round(y1))), 3)
        cells.append(captioned(c, f"{d} course"))
    crop_rows.append(captioned(row(cells, gap=8), run["name"]))
for i, pg in enumerate(pages(crop_rows)):
    pg.convert("RGB").save(os.path.join(args.out, "review-crops.png" if i == 0 else f"review-crops-{i + 1}.png"))
    print("crops", i + 1, pg.size)

# ================================================================ the GIFs: 24 frames over 60 ticks (one turn a second)
ticks = [round((f + 1) * 100 / NF) - round(f * 100 / NF) for f in range(NF)]       # hundredths, summing to 100


def gif(k, path):
    frames = []
    for f in range(NF):
        cells = []
        for gas in ("siderane", "helium-3"):
            cells.append(row([trim(scaled(model(d, f, gas), k), k, 2.4) for d in DIRS], gap=4 * k))
        im = Image.new("RGBA", (cells[0].width, cells[0].height * 2 + 4 * k), BG)
        im.alpha_composite(cells[0], (0, 0))
        im.alpha_composite(cells[1], (0, cells[0].height + 4 * k))
        frames.append(im.convert("RGB"))
    # one palette for the loop (from frames 0 and 12 side by side), no dither, so a still pixel keeps its index
    # from frame to frame and the encoder stores only what moves
    pal = Image.new("RGB", (frames[0].width * 2, frames[0].height))
    pal.paste(frames[0], (0, 0))
    pal.paste(frames[NF // 2], (frames[0].width, 0))
    pal = pal.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    frames = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=[t * 10 for t in ticks], loop=0,
                   optimize=True, disposal=1)
    print("gif", path, frames[0].size)


gif(1, os.path.join(args.out, "gas-pump-working-1x.gif"))
gif(2, os.path.join(args.scratch, "gas-pump-working-2x.gif"))
