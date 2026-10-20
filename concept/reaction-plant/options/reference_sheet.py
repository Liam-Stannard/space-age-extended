#!/usr/bin/env python3
"""Reaction Plant redesign: the vanilla study, one annotated reference sheet.

  python3 reference_sheet.py <factorio-data> <out.png> [--measures <out.txt>]

Builds the oil refinery and the chemical plant the way their prototypes layer
them (base/prototypes/entity/oil-refinery-animation.lua, entities.lua's
chemical-plant), from the sprite files and their .lua sidecars, at 1x (64 px a
tile) and 2x, working with a recipe tint, plus:

  - all four directions of each, small, to show how the asymmetry is drawn
  - a motion map: every pixel that changes across the working loop, in magenta
  - the fluid layers alone (chemical plant liquid + foam, refinery fluid),
    as a frame strip, to show what the "window" really is
  - silhouette measures: height above the footprint's top edge, how much of
    the footprint the mass covers, fluid area as a share of the sprite

Nothing here is ours; it is read off the game's files and only measured.
"""
import argparse
import os
import re

from PIL import Image, ImageChops, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
GROUND = (74, 66, 58, 255)
HR = 64                        # a scale-0.5 sprite: 64 of its px to a tile in game (1x here)

ap = argparse.ArgumentParser()
ap.add_argument("data")
ap.add_argument("out")
ap.add_argument("--measures")
args = ap.parse_args()
D = args.data
ENT = f"{D}/base/graphics/entity"


def sidecar(stem):
    txt = open(stem + ".lua").read()
    w = int(re.search(r"width\s*=\s*(\d+)", txt).group(1))
    h = int(re.search(r"height\s*=\s*(\d+)", txt).group(1))
    sx, sy = map(float, re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", txt).groups())
    ll = int(re.search(r"line_length\s*=\s*(\d+)", txt).group(1))
    return w, h, (sx, sy), ll


class Layer:
    """One sprite layer: a sheet, its frame size, its shift in 1x px, frames."""

    def __init__(self, path, w, h, shift, ll, frames, seq=None, blend="normal",
                 tint=None, overlay=False, glow=False, repeat=1):
        self.sheet = Image.open(path).convert("RGBA")
        self.w, self.h, self.shift, self.ll, self.frames = w, h, shift, ll, frames
        self.seq = seq or list(range(frames))
        self.blend, self.tint, self.overlay, self.glow = blend, tint, overlay, glow

    @classmethod
    def load(cls, stem, frames=1, extra=(0, 0), **kw):
        w, h, s, ll = sidecar(stem)
        return cls(stem + ".png", w, h, (s[0] + extra[0], s[1] + extra[1]), ll, frames, **kw)

    def frame(self, t):
        i = self.seq[t % len(self.seq)] if self.frames > 1 else 0
        x, y = (i % self.ll) * self.w, (i // self.ll) * self.h
        im = self.sheet.crop((x, y, x + self.w, y + self.h))
        if self.tint:
            im = tinted(im, self.tint, self.overlay)
        return im


def tinted(im, t, overlay):
    r, g, b, a = im.split()
    out = []
    for ch, tv in zip((r, g, b), t):
        if overlay:      # tint_as_overlay: overlay blend of the sprite with the tint
            out.append(ch.point(lambda v, tv=tv: int(2 * v * tv / 255) if v < 128
                                else int(255 - 2 * (255 - v) * (255 - tv) / 255)))
        else:            # the engine's default: multiply
            out.append(ch.point(lambda v, tv=tv: v * tv // 255))
    return Image.merge("RGBA", (*out, a))


def compose(layers, t, size=(640, 640), centre=(320, 352)):
    """Canvas at sprite px (64 a tile), entity centre at `centre`; by_pixel shifts are 32-a-tile, so x2."""
    base = Image.new("RGBA", size, (0, 0, 0, 0))
    for L in layers:
        im = L.frame(t)
        x = round(centre[0] + 2 * L.shift[0] - L.w / 2)
        y = round(centre[1] + 2 * L.shift[1] - L.h / 2)
        if L.blend == "additive":
            pad = Image.new("RGBA", size, (0, 0, 0, 0))
            pad.alpha_composite(im, (x, y))
            pr = Image.merge("RGB", pad.split()[:3])
            pr = ImageChops.multiply(pr, Image.merge("RGB", [pad.getchannel("A")] * 3))
            rgb = ImageChops.add(Image.merge("RGB", base.split()[:3]), pr)
            base = Image.merge("RGBA", (*rgb.split(), base.getchannel("A")))
        else:
            base.alpha_composite(im, (max(x, 0), max(y, 0)),
                                 (max(-x, 0), max(-y, 0)))
    return base


# ---------------------------------------------------------------- the refinery
ORANGE = (253, 115, 15)      # advanced-oil-processing primary
REF_SPEED = 0.75
REF_ANIMS = {"north": 6, "east": 6, "south": 5, "west": 7}
REF_FLUID = {"north": 6, "east": 5, "south": 5, "west": 7}


def refinery(d, working=True, fluid_only=False):
    p = f"{ENT}/oil-refinery/{d}/oil-refinery"
    body = [Layer.load(f"{p}-{d}")]
    seq40 = list(range(40)) + list(range(19, -1, -1))
    body.append(Layer.load(f"{p}-anim-{d}-1", frames=40, seq=seq40))
    for i in range(2, REF_ANIMS[d] + 1):
        body.append(Layer.load(f"{p}-anim-{d}-{i}", frames=20))
    fluid = [Layer.load(f"{p}-fluid-{d}-{i}", frames=20, tint=ORANGE, overlay=True)
             for i in range(1, REF_FLUID[d] + 1)]
    if fluid_only:
        return fluid
    if not working:
        return body + fluid         # fluid is always_draw: it shows idle too
    smoke = [Layer.load(f"{p}-smoke-{d}", frames=20)]
    lights = [Layer.load(f"{p}-lights-{d}", blend="additive")]
    return body + fluid + smoke + lights


# ----------------------------------------------------------- the chemical plant
YELLOW = (255, 244, 0)        # sulfuric-acid primary
YELLOW2 = (255, 217, 43)
CHEM = {
    "north": ((0, -9), (23, 15), (24, 15), 0),
    "east": ((0, -9), (0, 22), (0, 22), 1),
    "south": ((0, -9), (0, 17), (1, 17), 2),
    "west": ((0, -9), (-10, 13), (-9, 15), 3),
}
CHEM_WH = {"north": ((66, 44), (62, 42)), "east": ((70, 36), (68, 36)),
           "south": ((66, 42), (60, 40)), "west": ((74, 36), (68, 28))}


def chem(d, working=True, fluid_only=False):
    p = f"{ENT}/chemical-plant/chemical-plant-{d}"
    off, lq, fm, _ = CHEM[d]
    body = [Layer.load(f"{p}-base", extra=off),
            Layer.load(f"{p}-anim-1", frames=24, extra=off),
            Layer.load(f"{p}-anim-2", frames=24, extra=off)]
    (lw, lh), (fw, fh) = CHEM_WH[d]
    fluid = [Layer(f"{ENT}/chemical-plant/chemical-plant-liquid-{d}.png", lw, lh, lq, 6, 24, tint=YELLOW),
             Layer(f"{ENT}/chemical-plant/chemical-plant-foam-{d}.png", fw, fh, fm, 6, 24, tint=YELLOW2)]
    if fluid_only:
        return fluid
    return body + fluid if working else body


def shadow_of(kind, d):
    if kind == "chem":
        x = CHEM[d][3]
        L = Layer(f"{ENT}/chemical-plant/chemical-plant-shadow.png", 312, 222, (27, 6), 1, 1)
        L.sheet = L.sheet.crop((312 * x, 0, 312 * (x + 1), 222))
        return [L]
    return [Layer.load(f"{ENT}/oil-refinery/{d}/oil-refinery-shadow-{d}")]


def shadowed(img_layers, sh_layers, t, size, centre):
    sh = compose(sh_layers, 0, size, centre)
    a = sh.getchannel("A").point(lambda v: v // 2)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.putalpha(a)
    out.alpha_composite(compose(img_layers, t, size, centre))
    return out


def motion_map(layers, n, size, centre):
    """Pixels that differ from frame 0 anywhere in the loop."""
    f0 = compose(layers, 0, size, centre)
    acc = Image.new("L", size, 0)
    for t in range(1, n):
        d = ImageChops.difference(f0, compose(layers, t, size, centre)).convert("L")
        acc = ImageChops.lighter(acc, d.point(lambda v: 255 if v > 10 else 0))
    return f0, acc


def alpha_bbox(im, thr=40):
    return im.getchannel("A").point(lambda v: 255 if v > thr else 0).getbbox()


# -------------------------------------------------------------------- layout
def half(im):
    return im.resize((im.width // 2, im.height // 2), Image.LANCZOS)


def on_ground(im, grid_tiles, centre, ppt):
    g = Image.new("RGBA", im.size, GROUND)
    dr = ImageDraw.Draw(g)
    cx, cy = centre
    n = grid_tiles
    for i in range(-n, n + 1):
        dr.line([(cx + i * ppt, 0), (cx + i * ppt, im.height)], fill=(255, 255, 255, 22))
        dr.line([(0, cy + i * ppt), (im.width, cy + i * ppt)], fill=(255, 255, 255, 22))
    g.alpha_composite(im)
    return g


def footprint(dr, centre, ppt, tiles, col=(255, 255, 255, 140)):
    cx, cy = centre
    h = tiles * ppt / 2
    dr.rectangle([cx - h, cy - h, cx + h, cy + h], outline=col)


f = lambda s: ImageFont.truetype(FONT, s)
fb = lambda s: ImageFont.truetype(BOLD, s)
M = []                     # measures, to print and to a text file

W, H = 2600, 3200
sheet = Image.new("RGBA", (W, H), (34, 32, 30, 255))
dr = ImageDraw.Draw(sheet)
dr.text((20, 14), "REACTION PLANT REDESIGN -- THE VANILLA STUDY: OIL REFINERY AND CHEMICAL PLANT",
        font=fb(26), fill=(235, 230, 220))
dr.text((20, 50), "Composited from the game's own sprite layers as the prototypes stack them (Factorio 2.1 data). "
        "Working, recipe-tinted: refinery = advanced oil processing #fd730f (tint_as_overlay), "
        "chemical plant = sulfuric acid #fff400 / #ffd92b (multiply).", font=f(15), fill=(200, 195, 185))

# --- row 1: the two hero views at 2x with motion maps, and the facts
RS, RC = (500, 560), (250, 330)      # refinery canvas, sprite px
CS, CC = (300, 340), (150, 200)      # chemical canvas, sprite px
y0 = 90
ref_l = refinery("north")
r0, rmov = motion_map(ref_l, 60, RS, RC)
ref_img = shadowed(ref_l, shadow_of("ref", "north"), 0, RS, RC)
chem_l = chem("north")
c0, cmov = motion_map(chem_l, 24, CS, CC)
chem_img = shadowed(chem_l, shadow_of("chem", "north"), 0, CS, CC)


def panel(img, mov, centre, tiles, title, x, y, scale=0.75):
    """Left: the frame at `scale` x game size; right: the same with motion in magenta."""
    s = lambda im: im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    c = (int(centre[0] * scale), int(centre[1] * scale))
    ppt = int(HR * scale)
    a = on_ground(s(img), 6, c, ppt)
    m = a.copy()
    tint = Image.new("RGBA", m.size, (255, 0, 200, 0))
    tint.putalpha(s(mov.convert("RGBA")).getchannel("R").point(lambda v: int(v * 0.7)))
    m.alpha_composite(tint)
    for im in (a, m):
        footprint(ImageDraw.Draw(im), c, ppt, tiles)
    sheet.alpha_composite(a, (x, y + 24))
    sheet.alpha_composite(m, (x + a.width + 8, y + 24))
    dr.text((x, y), title, font=fb(17), fill=(235, 230, 220))
    dr.text((x + a.width + 8, y + 4), "magenta: every pixel that moves in the working loop",
            font=f(13), fill=(255, 140, 230))
    return a.width * 2 + 8, a.height + 24


pw, ph = panel(ref_img, rmov, RC, 5, "OIL REFINERY, north, 5x5, frame 0 (1x)", 20, y0, 1.0)
cw, chh = panel(chem_img, cmov, CC, 3, "CHEMICAL PLANT, north, 3x3, frame 0 (1.5x)",
                20 + pw + 24, y0, 1.5)


def measure(name, img, mov, centre, tiles, fluid_layers, size, ppt=HR):
    bb = alpha_bbox(img)
    top_tiles = (centre[1] - tiles * ppt / 2 - bb[1]) / ppt
    A = img.getchannel("A").point(lambda v: 255 if v > 40 else 0)
    fx0, fy0 = centre[0] - tiles * ppt // 2, centre[1] - tiles * ppt // 2
    fp = A.crop((fx0, fy0, fx0 + tiles * ppt, fy0 + tiles * ppt))
    cover = sum(1 for v in fp.get_flattened_data() if v) / (tiles * ppt) ** 2
    opaque = sum(1 for v in A.get_flattened_data() if v)
    moving = sum(1 for v in mov.get_flattened_data() if v)
    fl = compose(fluid_layers, 0, size, centre).getchannel("A").point(lambda v: 255 if v > 40 else 0)
    fluid_px = sum(1 for v in fl.get_flattened_data() if v)
    fbb = fl.getbbox()
    rec = {
        "name": name,
        "sprite bbox (tiles)": f"{(bb[2]-bb[0])/ppt:.2f} wide x {(bb[3]-bb[1])/ppt:.2f} tall",
        "rises above footprint top edge": f"{top_tiles:.2f} tiles",
        "footprint covered by mass": f"{cover*100:.0f} %",
        "moving pixels / opaque": f"{moving/opaque*100:.1f} %",
        "fluid (tinted) pixels / opaque": f"{fluid_px/opaque*100:.1f} %",
        "fluid area bbox (tiles)": f"{(fbb[2]-fbb[0])/ppt:.2f} x {(fbb[3]-fbb[1])/ppt:.2f}"
                                    f", centre {((fbb[0]+fbb[2])/2-centre[0])/ppt:+.2f},"
                                    f"{((fbb[1]+fbb[3])/2-centre[1])/ppt:+.2f} from entity centre",
    }
    M.append(rec)
    return rec


mr = measure("oil refinery (north)", r0, rmov, RC, 5, refinery("north", fluid_only=True), RS)
mc = measure("chemical plant (north)", c0, cmov, CC, 3, chem("north", fluid_only=True), CS)

# facts column
fx = 20 + pw + 24 + cw + 24
fy = y0
dr.text((fx, fy), "WHAT THE PROTOTYPES SAY", font=fb(17), fill=(235, 230, 220))
facts = [
    ("Oil refinery (2.1 redraw)", [
        "4 directions, each its own drawing; use_mirroring",
        "body 1 frame + anim-1: 40 f ping-pong (1..40..1 = 60)",
        "+ 4-6 anim layers of 20 f x3 (gears, pumps, valves)",
        "fluid: 5-7 layers, 20 f, tint_as_overlay, recipe",
        "  'primary', always_draw + fadeout -> shows idle too",
        "smoke 20 f, lights additive draw_as_glow 'flicker',",
        "flare fire + light on the tallest stack",
        "animation_speed 0.75 -> 20 f loop = 0.44 s at x1",
    ]),
    ("Chemical plant", [
        "4 directions, each its own drawing; use_mirroring",
        "base 1 f + anim-1, anim-2: 24 f (the mixer motion)",
        "liquid 24 f (recipe primary, multiply) +",
        "foam 24 f (secondary): the round sight bowl",
        "smoke outer/inner 47 f at 0.5 (tertiary/quaternary),",
        "  render_layer wires, from the two chimneys",
        "speed 1 -> 24 f = 0.4 s; smoke 1.6 s",
    ]),
]
fy += 30
for head, lines in facts:
    dr.text((fx, fy), head, font=fb(15), fill=(240, 200, 120))
    fy += 22
    for ln in lines:
        dr.text((fx + 8, fy), ln, font=f(13), fill=(210, 205, 195))
        fy += 18
    fy += 10
dr.text((fx, fy), "MEASURED (north, frame 0, sprite px / 64)", font=fb(15), fill=(240, 200, 120))
fy += 22
for rec in (mr, mc):
    dr.text((fx + 8, fy), rec["name"], font=fb(13), fill=(225, 220, 210))
    fy += 18
    for k, v in rec.items():
        if k == "name":
            continue
        dr.text((fx + 16, fy), f"{k}: {v}", font=f(12), fill=(205, 200, 190))
        fy += 17
    fy += 6

# --- row 2: four directions of each at 1x
y1 = y0 + max(ph, chh) + 30
dr.text((20, y1), "FOUR DIRECTIONS AT GAME SCALE (64 px a tile) -- vanilla draws each direction separately; "
        "ours is ONE plate under rotation, so the asymmetry must not name a port face", font=fb(16),
        fill=(235, 230, 220))
x = 20
for d in ("north", "east", "south", "west"):
    im = shadowed(refinery(d), shadow_of("ref", d), 0, RS, RC)
    g = on_ground(im, 6, RC, 64)
    footprint(ImageDraw.Draw(g), RC, 64, 5)
    g = g.crop((60, 60, 450, 520))
    sheet.alpha_composite(g, (x, y1 + 28))
    dr.text((x + 4, y1 + 32), f"refinery {d}", font=f(13), fill=(240, 235, 225))
    x += g.width + 6
for d in ("north", "east", "south", "west"):
    im = shadowed(chem(d), shadow_of("chem", d), 0, CS, CC)
    g = on_ground(im, 4, CC, 64)
    footprint(ImageDraw.Draw(g), CC, 64, 3)
    g = g.crop((35, 20, 265, 320))
    sheet.alpha_composite(g, (x, y1 + 28))
    dr.text((x + 4, y1 + 32), f"chem {d}", font=f(13), fill=(240, 235, 225))
    x += g.width + 6

# --- row 3: the fluid layers alone, as frame strips at 2x hr (4x game)
y2 = y1 + 28 + 460 + 24
dr.text((20, y2), "THE FLUID, ALONE -- what the 'window' is: a tinted animated layer over a dark recess "
        "(every 4th / 5th frame, at 3x / 2x game scale)", font=fb(16), fill=(235, 230, 220))
x, yy = 20, y2 + 28


def strip(layers, size, centre, crop, n, step, label, scale=2):
    global x
    dr.text((x, yy), label, font=fb(13), fill=(240, 200, 120))
    for t in range(0, n, step):
        fr = compose(layers, t, size, centre).crop(crop)
        fr = fr.resize((fr.width * scale, fr.height * scale), Image.LANCZOS) if scale != 1 else fr
        bg = Image.new("RGBA", fr.size, (20, 20, 22, 255))
        bg.alpha_composite(fr)
        sheet.alpha_composite(bg, (x, yy + 20))
        x += bg.width + 4
    x += 24


cbody = chem("north")
cfl = chem("north", fluid_only=True)
fb_c = compose(cfl, 0, CS, CC).getbbox()
pad = 14
crop_c = (fb_c[0] - pad, fb_c[1] - pad, fb_c[2] + pad, fb_c[3] + pad)
strip(cbody, CS, CC, crop_c, 24, 4, "chemical plant: body + liquid + foam, the sight bowl (3x)", 3)
strip(cfl, CS, CC, crop_c, 24, 4, "the same, fluid layers only", 3)
x = 20
yy += 20 + (crop_c[3] - crop_c[1]) * 3 + 30
rfl = refinery("north", fluid_only=True)
fb_r = compose(rfl, 0, RS, RC).getbbox()
crop_r = (fb_r[0] - pad, fb_r[1] - pad, fb_r[2] + pad, fb_r[3] + pad)
strip(rfl, RS, RC, crop_r, 20, 5, "refinery north: fluid layers only (1x) -- small glass runs spread over the pipework", 1)
strip(refinery("north"), RS, RC, crop_r, 20, 5, "with the body (1x)", 1)

# --- row 4: findings
y3 = yy + 20 + (crop_r[3] - crop_r[1]) + 30
dr.text((20, y3), "FINDINGS FOR THE REACTION PLANT", font=fb(18), fill=(235, 230, 220))
findings = [
    "1  NEITHER IS A BOX, AND NEITHER STANDS ON A PLINTH. Both fill 92-94 % of their footprint with mass and rise about 1 tile above its top edge "
    "(refinery 0.97, chemical plant 1.05). The refinery is a cluster of",
    "    vessels of different heights round a pipe deck: its tallest column and flare stack sit to one side, the low plant (pumps, valve gear, "
    "manifolds, small tanks) runs along the front. The chemical plant is one",
    "    big low round tank with two chimneys pushed to the back corner, so it is high at one end and low at the other.",
    "2  THE PIPEWORK IS THE BUILDING. Pipes run about 0.3-0.45 tiles thick at game scale (20-28 px), banded and flanged, in bundles of 2-4 that "
    "arch over the vessels in the open. Big elbows break the silhouette.",
    "3  THE FLUID IS A BRIGHT TINTED PATCH IN A DARK FRAME. Chemical plant: one sight bowl, 0.98 x 0.66 tiles, low on the front-right "
    "(+0.74, +0.47 from centre), liquid + foam, 24 frames, recipe-tinted; 3.2 % of the",
    "    sprite. Refinery: six small glass runs and sight tubes spread over the pipework, overlay-tinted so the glass highlights survive; 2.0 % "
    "of the sprite. Small area, high contrast -- that is what reads at 1x.",
    "4  MANY SHORT MOTIONS, EACH FREE TO MOVE. Refinery: 15.9 % of its pixels move -- gears, pumps, valve wheels and fluid, 6-8 layers in "
    "20-frame loops (one 40-frame ping-pong). Chemical plant: 5.2 % -- the mixer",
    "    head and the fluid, 24 frames. Every moving part sits clear of what stays put (the magenta maps).",
    "5  BOTH NEED FOUR DRAWINGS TO BE ASYMMETRIC. Ours is one plate under rotation (spec 5): inputs on one face, the output opposite, turning "
    "with the entity. So our asymmetry goes on a DIAGONAL (tall vessel in one corner,",
    "    low plant in the opposite corner) or across the E-W axis, and the two port faces stay plain enough to take a stub on any tile.",
]
yy = y3 + 30
for ln in findings:
    dr.text((20, yy), ln, font=f(14), fill=(215, 210, 200))
    yy += 20

sheet = sheet.crop((0, 0, W, min(H, yy + 20)))
sheet.convert("RGB").save(args.out)
print(args.out, sheet.size)
txt = "\n".join(f"{r['name']}\n" + "\n".join(f"  {k}: {v}" for k, v in r.items() if k != "name") for r in M)
print(txt)
if args.measures:
    open(args.measures, "w").write(txt + "\n")
