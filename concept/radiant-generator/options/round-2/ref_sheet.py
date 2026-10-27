#!/usr/bin/env python3
"""Radiant Generator, round 2: the reference sheet -- what vanilla's showpieces do.

  python3 ref_sheet.py <out.png> [<panel-dir>]

Reads the nuclear reactor, the fusion reactor and the fusion generator from the
local install ($FACTORIO_DATA) at the sizes and shifts their prototypes give
(base/prototypes/entity/entities.lua, space-age/prototypes/entity/
fusion-system-pictures.lua and the per-sprite .lua files beside the pngs) and lays
out, at game scale (64 px a tile) and at 2x:

  * each building idle and working, on the ground with its footprint, with its
    height above the footprint marked;
  * the layers that make "working": the nuclear reactor's working_light_picture
    and heat glow, the fusion reactor's glow and plasma, the fusion generator's
    6-frame animation and its plasma;
  * the plasma-UV trick, reproduced from core/graphics/shaders/fusion-effect.frag
    in Python: the UV map's R runs along the duct, G across it, B is the mask; the
    shader scrolls a bright line along R with time and wobbles it with noise.
    Reproduced closely enough to show the read, not pixel-exact.

Every number on the sheet is measured here, printed to stdout as well.
"""
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

OUT = sys.argv[1]
FD = os.environ.get("FACTORIO_DATA", os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
PPT = 64
GROUND = (74, 66, 58, 255)
BG = (30, 30, 30, 255)
GRID = (255, 255, 255, 30)
FOOT = (255, 255, 255, 110)
TEXT = (225, 220, 210, 255)
SUB = (165, 160, 150, 255)
MARK = (120, 200, 255, 255)
PINK = (1.0, 0.0, 0.4)          # glow_color / default_fuel_glow_color {1, 0, 0.4}


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""), size)


def img(rel):
    return Image.open(os.path.join(FD, rel)).convert("RGBA")


def frame(rel, w, h, i, line):
    im = img(rel)
    return im.crop(((i % line) * w, (i // line) * h, (i % line) * w + w, (i // line) * h + h))


def half(im):
    """hr sprite (scale 0.5): already 64 px a tile, as drawn at 1x. Kept as a no-op for clarity."""
    return im


def as_glow(im):
    """An additive layer stored RGB (no alpha): alpha from brightness, for compositing."""
    rgb = im.convert("RGB")
    a = rgb.convert("L")
    return Image.merge("RGBA", (*rgb.split(), a))


def add(base, glow):
    g = glow.convert("RGBa")
    r, gg, b, _ = g.split()
    rgb = ImageChops.add(base.convert("RGB"), Image.merge("RGB", (r, gg, b)))
    return Image.merge("RGBA", (*rgb.split(), base.split()[3]))


# ---------------------------------------------------------------- the plasma shader

def _rand(x, y):
    s = x * 12.3456 + y * 34.1415
    return (math.sin(s) * 45678.8984375) % 1.0


def _perlin(x, y):
    cx, cy = math.floor(x), math.floor(y)
    fx, fy = x - cx, y - cy
    s00, s01 = _rand(cx, cy), _rand(cx, cy + 1)
    s10, s11 = _rand(cx + 1, cy), _rand(cx + 1, cy + 1)
    return (s00 * (1 - fx) + s10 * fx) * (1 - fy) + (s01 * (1 - fx) + s11 * fx) * fy


def plasma(uv, t, power=1.0, level=1.0, colour=PINK):
    """fusion-effect.frag, per pixel, on the UV map (an RGB image). Returns RGBA."""
    W, H = uv.size
    src = uv.convert("RGB").load()
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = out.load()
    bg_power = max(level, power * 0.25)
    for y in range(H):
        for x in range(W):
            r, g, b = src[x, y]
            if b == 0:
                continue
            white = _rand(x / W, y / H)
            mask = max(b / 255 - white * 0.125, 0.0)
            ex, ey = r / 255 * 12.0 + t * 2.0, g / 255
            ny = (_perlin(ex + t + 47.1, ey + t + 47.1) - 0.5) * 2
            ey += ny * 0.2
            grad = 1.0 - abs(ey - 0.5)
            bgk = bg_power ** 1.5
            bgv = ((bgk * grad) * (1 - power) + bgk * power) * mask
            mid = grad ** (30 * min(bg_power, 1.0)) * power * 2
            line = (mid + grad ** 30 * power * 2) * mask ** 0.5
            line *= 1 - mask * 0.5
            rgb = []
            for c in colour:
                coloured = line * c * (1 - bg_power * mask) + line * (bg_power * mask)
                rgb.append(min(1.0, bgv * c + coloured))
            v = max(rgb)
            if v <= 0.004:
                continue
            px[x, y] = tuple(int(c / v * 255) for c in rgb) + (int(v * 255),)
    return out


# ---------------------------------------------------------------- panels

def ground(w, h, origin, foot):
    W, H = int(w * PPT), int(h * PPT)
    g = Image.new("RGBA", (W, H), GROUND)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    ox, oy = origin[0] * PPT, origin[1] * PPT
    x0, y0 = ox - foot[0] / 2 * PPT, oy - foot[1] / 2 * PPT
    x = x0 % PPT
    while x < W:
        dr.line([(x, 0), (x, H)], fill=GRID)
        x += PPT
    y = y0 % PPT
    while y < H:
        dr.line([(0, y), (W, y)], fill=GRID)
        y += PPT
    dr.rectangle([x0, y0, x0 + foot[0] * PPT, y0 + foot[1] * PPT], outline=FOOT)
    g.alpha_composite(ov)
    return g


def put(dst, im, o, shift):
    x = round(o[0] + shift[0] * PPT - im.width / 2)
    y = round(o[1] + shift[1] * PPT - im.height / 2)
    cx, cy = max(0, -x), max(0, -y)
    dst.alpha_composite(im.crop((cx, cy, im.width, im.height)), (x + cx, y + cy))


def panel(layers, foot, h_tiles, w_tiles, height_of=None):
    """layers: (image at game px, shift in tiles, 'alpha'|'add'). Marks the height above the footprint."""
    origin = (w_tiles / 2, h_tiles - foot[1] / 2 - 0.6)
    g = ground(w_tiles, h_tiles, origin, foot)
    o = (origin[0] * PPT, origin[1] * PPT)
    for im, shift, mode in layers:
        if mode == "alpha":
            put(g, im, o, shift)
        else:
            layer = Image.new("RGBA", g.size, (0, 0, 0, 0))
            put(layer, im, o, shift)
            g = add(g, layer)
    if height_of is not None:
        im, shift = height_of
        a = im.split()[3].point(lambda v: 255 if v > 24 else 0)
        top = a.getbbox()[1]
        top_px = o[1] + shift[1] * PPT - im.height / 2 + top
        foot_top = o[1] - foot[1] / 2 * PPT
        dr = ImageDraw.Draw(g)
        x = o[0] + foot[0] / 2 * PPT + 8
        dr.line([(x, top_px), (x, foot_top)], fill=MARK, width=2)
        dr.line([(x - 4, top_px), (x + 4, top_px)], fill=MARK, width=2)
        dr.line([(x - 4, foot_top), (x + 4, foot_top)], fill=MARK, width=2)
        above = (foot_top - top_px) / PPT
        dr.text((x + 6, (top_px + foot_top) / 2 - 7), "+%.2f t" % above, font=font(11), fill=MARK)
        return g, above
    return g, None


def lit_fraction(glow, body):
    """Share of the building's opaque pixels where the glow is visibly on (luma > 40)."""
    gl = glow.convert("L")
    a = body.split()[3]
    n_body = sum(1 for v in a.getdata() if v > 24)
    n_lit = sum(1 for v in gl.getdata() if v > 40)
    return n_lit, n_body


def label(im, xy, text, size=12, fill=TEXT, bold=False):
    ImageDraw.Draw(im).text(xy, text, font=font(size, bold), fill=fill)


def row(panels, labels, gap=12, top=20):
    W = sum(p.width for p in panels) + gap * (len(panels) + 1)
    H = max(p.height for p in panels) + top + gap
    out = Image.new("RGBA", (W, H), BG)
    x = gap
    for p, t in zip(panels, labels):
        out.alpha_composite(p, (x, top))
        label(out, (x + 2, 3), t, 12, SUB)
        x += p.width + gap
    return out


def on_ground(im, pad=6):
    g = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), GROUND)
    g.alpha_composite(im, (pad, pad))
    return g


def x2(im):
    return im.resize((im.width * 2, im.height * 2), Image.NEAREST)


def stack_v(rows, gap=8):
    W = max(r.width for r in rows)
    out = Image.new("RGBA", (W, sum(r.height for r in rows) + gap * (len(rows) - 1)), BG)
    y = 0
    for r in rows:
        out.alpha_composite(r, (0, y))
        y += r.height + gap
    return out


# ---------------------------------------------------------------- measure

NUC = "base/graphics/entity/nuclear-reactor/"
FUS = "space-age/graphics/entity/fusion-reactor/"
GEN = "space-age/graphics/entity/fusion-generator/north/"

nuc = half(img(NUC + "reactor.png"))
nuc_s = (-5 / 32, -7 / 32)
nuc_pipes = half(img(NUC + "reactor-pipes.png"))
nuc_pipes_s = (-1 / 32, -5 / 32)
nuc_light = half(as_glow(img(NUC + "reactor-lights-color.png")))
nuc_light_s = (-0.03125, -0.1875)
nuc_heat = half(img(NUC + "reactor-heated.png"))
nuc_heat_s = (3 / 32, -6.5 / 32)

fus = half(img(FUS + "fusion-reactor-main.png"))
fus_s = (1 / 32, -5.5 / 32)
fus_glow = half(as_glow(img(FUS + "fusion-reactor-glow.png")))
fus_glow_s = (1.5 / 32, -11 / 32)
fus_uv = img(FUS + "plasma-UV.png")


def lua_box(rel):
    """width, height, shift (tiles) from a sprite's .lua beside its png."""
    import re
    t = open(os.path.join(FD, rel)).read()
    w = int(re.search(r"width\s*=\s*(\d+)", t).group(1))
    h = int(re.search(r"height\s*=\s*(\d+)", t).group(1))
    sx, sy = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", t).groups())
    return w, h, (sx / 32, sy / 32)


# the eight edge pieces the main sprite leaves holes for; frame 0 of 5 is the
# unconnected variant (the frame chosen by what the neighbour is)
fus_conn, fus_conn_glow = [], []
for n in range(1, 9):
    w, h, sh = lua_box(FUS + "fusion-reactor-connection-%d.lua" % n)
    fus_conn.append((frame(FUS + "fusion-reactor-connection-%d.png" % n, w, h, 0, 5), sh, "alpha"))
    w, h, sh = lua_box(FUS + "fusion-reactor-connection-%d-glow.lua" % n)
    fus_conn_glow.append((as_glow(frame(FUS + "fusion-reactor-connection-%d-glow.png" % n, w, h, 0, 5)), sh, "add"))

gen = [half(frame(GEN + "fusion-generator-north.png", 244, 376, i, 3)) for i in range(6)]
gen_s = (-2 / 32, -2 / 32)
gen_glow = [half(as_glow(frame(GEN + "fusion-generator-north-glow.png", 202, 336, i, 3))) for i in range(6)]
gen_glow_s = (0, -4 / 32)
gen_uv = img(GEN + "fusion-generator-north-uv.png")

# the plasma, at three times; the reactor's UV map is one 384 px image (diced 2x5 in
# the engine only for batching), the generator's 192 px; both at scale 0.5
fus_pl_hr = [plasma(fus_uv, t) for t in (0.0, 0.35, 0.7)]
fus_pl = [half(p) for p in fus_pl_hr]
gen_pl = [half(plasma(gen_uv, t)) for t in (0.0, 0.35, 0.7)]

stats = []
n_lit, n_body = lit_fraction(nuc_light, nuc)
stats.append(("nuclear reactor", "5x5", n_body, n_lit))
n_lit2, n_body2 = lit_fraction(fus_glow, fus)
pl_lit = sum(1 for v in fus_pl[0].split()[3].getdata() if v > 40)
stats.append(("fusion reactor", "6x6", n_body2, n_lit2 + pl_lit))
n_lit3, n_body3 = lit_fraction(gen_glow[0], gen[0])
gpl_lit = sum(1 for v in gen_pl[0].split()[3].getdata() if v > 40)
stats.append(("fusion generator", "3x5", n_body3, n_lit3 + gpl_lit))

# frame-to-frame change in the generator's 6 frames (the moving part)
moved = []
for i in range(1, 6):
    d = ImageChops.difference(gen[i].convert("RGB"), gen[0].convert("RGB")).convert("L")
    moved.append(sum(1 for v in d.getdata() if v > 12))

# ---------------------------------------------------------------- row 1: idle vs working, 1x

p_nuc_i, h_nuc = panel([(nuc_pipes, nuc_pipes_s, "alpha"), (nuc, nuc_s, "alpha")], (5, 5), 7.2, 7.2, (nuc, nuc_s))
p_nuc_w, _ = panel([(nuc_pipes, nuc_pipes_s, "alpha"), (nuc, nuc_s, "alpha"), (nuc_heat, nuc_heat_s, "alpha"),
                    (nuc_light, nuc_light_s, "add")], (5, 5), 7.2, 7.2)
p_fus_i, h_fus = panel([(fus, fus_s, "alpha")] + fus_conn, (6, 6), 8.2, 8.2, (fus, fus_s))
p_fus_w, _ = panel([(fus, fus_s, "alpha")] + fus_conn + [(fus_glow, fus_glow_s, "add")] + fus_conn_glow
                   + [(fus_pl[0], (0, 0), "add")],
                   (6, 6), 8.2, 8.2)
p_gen_i, h_gen = panel([(gen[0], gen_s, "alpha")], (3, 5), 7.2, 5, (gen[0], gen_s))
p_gen_w, _ = panel([(gen[0], gen_s, "alpha"), (gen_glow[0], gen_glow_s, "add"), (gen_pl[0], (0, 0.5), "add")],
                   (3, 5), 7.2, 5)

r1 = row([p_nuc_i, p_nuc_w, p_fus_i, p_fus_w, p_gen_i, p_gen_w],
         ["nuclear reactor 5x5, idle", "working: lights + heat glow",
          "fusion reactor 6x6, idle", "working: glow + plasma",
          "fusion generator 3x5, idle", "working: glow + plasma"])

# ---------------------------------------------------------------- row 2: the layers, 2x

r2 = row([on_ground(nuc_light), on_ground(nuc_heat), on_ground(fus_glow)],
         ["nuclear: working_light_picture alone (additive)", "nuclear: heat glow (by temperature)",
          "fusion reactor: glow layer alone (additive)"])

# ---------------------------------------------------------------- row 3: plasma-UV, the generator's frames

uvp = Image.new("RGBA", fus_uv.size, (0, 0, 0, 255))
uvp.alpha_composite(fus_uv)
pl_frames = []
for p in fus_pl_hr:
    g = Image.new("RGBA", p.size, (20, 18, 16, 255))
    g.alpha_composite(p)
    pl_frames.append(g)
crop_box = (40, 60, 200, 250)          # the generator's cog and rotor band, sprite px
gear = [on_ground(g.crop(crop_box), 2) for g in gen[:3]]
r3 = row([uvp] + pl_frames + gear,
         ["plasma-UV map (R along, G across, B mask)", "plasma alone, t = 0", "t + 0.35 s", "t + 0.7 s",
          "fusion gen frame 0", "frame 1", "frame 2"])

# ---------------------------------------------------------------- findings

lines = [
    ("WHAT MOVES", True),
    ("Nuclear reactor: nothing. A static picture; working = an additive working_light_picture (green ports and seams,"
     " %d lit px = %.1f%% of the body) plus heat glow on the plate and heat-pipe patches, by temperature."
     % (n_lit, 100 * n_lit / n_body), False),
    ("Fusion reactor: nothing mechanical. Structure static; working = glow layer plus the plasma shader over a 384 px"
     " UV map: a white-hot line scrolling through ten ring ducts (lit, glow + plasma: %.1f%% of the body)."
     % (100 * (n_lit2 + pl_lit) / n_body2), False),
    ("   Its 8 neighbour-connection sprites have 5 variants each (open / plasma / coolant ...): selected by neighbours,"
     " not played. A block of reactors reads as one machine.", False),
    ("Fusion generator: a 6-frame loop (a cog and rotor band; %d-%d px change a frame, ~%.0f%% of the body) under"
     " the same plasma shader in four small viewports (lit: %.1f%%). Glow layer also 6 frames."
     % (min(moved), max(moved), 100 * max(moved) / n_body3, 100 * (n_lit3 + gpl_lit) / n_body3), False),
    ("HEIGHT AND MASS", True),
    ("Nuclear: a dome that barely clears its footprint (+%.2f tiles over 5x5). Fusion reactor: a central column on"
     " a ring, +%.2f tiles over 6x6. Fusion generator: +%.2f tiles over 3x5, its rotor drum the mass."
     % (h_nuc, h_fus, h_gen), False),
    ("WHAT MAKES THEM READ AT 1X", True),
    ("Light, not motion: one saturated colour against a desaturated body (FFF #146), laid out as a ring or radial"
     " pattern so the shape reads in the dark. The lit area is small, but it is the brightest thing on screen.", False),
    ("The only fluid motion is shader plasma: a line flowing along ducts. The mechanical motion is tiny. Their"
     " look changes with neighbours, so a block of them reads as one machine.", False),
    ("FOR THE RADIANT GENERATOR (burner-generator): animation + idle_animation with the same frame count;"
     " perceived_performance scales playback speed with load; glow = draw_as_glow layers in the animation.", False),
    ("No shader, no working_visualisations: any flow has to be drawn into frames. We can out-move vanilla, but must"
     " match its light discipline.", False),
]
for name, foot, body, lit in stats:
    print(f"{name} {foot}: opaque {body} px at 1x, glow-lit {lit} px = {100 * lit / body:.1f}%")
print(f"heights above footprint (tiles): nuclear {h_nuc:.2f}, fusion reactor {h_fus:.2f}, fusion generator {h_gen:.2f}")
print("fusion generator frame changes (px at 1x):", moved)

W = max(r1.width, r2.width, r3.width)
txt = Image.new("RGBA", (W, 16 + 19 * len(lines)), BG)
y = 6
for t, bold in lines:
    label(txt, (12, y), t, 13 if bold else 12, TEXT if bold else SUB, bold)
    y += 19
head = Image.new("RGBA", (W, 50), BG)
label(head, (10, 6), "RADIANT GENERATOR, ROUND 2 -- REFERENCE: VANILLA'S SHOWPIECES", 20, bold=True)
label(head, (10, 32), "Measured from the local install. Everything at game scale (64 px a tile, scale-0.5 sprites at 1x), no shadows."
      " Plasma reproduced from fusion-effect.frag in Python (approximate).", 12, SUB)
sheet = stack_v([head, r1, r2, r3, txt])
sheet.save(OUT)
print(OUT, sheet.size)

# with a second argument, keep the working panels for the contact sheet (r2_sheets.py)
if len(sys.argv) > 2:
    os.makedirs(sys.argv[2], exist_ok=True)
    for name, p in (("nuclear-reactor", p_nuc_w), ("fusion-reactor", p_fus_w), ("fusion-generator", p_gen_w)):
        p.save(os.path.join(sys.argv[2], f"{name}-working.png"))
