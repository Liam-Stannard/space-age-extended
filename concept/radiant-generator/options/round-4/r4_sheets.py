#!/usr/bin/env python3
"""Radiant Generator, round 4: the cooling study, variant sheets, GIFs and the contact sheet.

  python3 r4_sheets.py <render-root> <ref-panel-dir> <out-dir>

<render-root>/<V>-hero, <V>-anim, <V>-reactor, <V>-mask are r4_blockout.py's output for
each variant V (1, 2, 3); <ref-panel-dir> holds round-2/ref_sheet.py's working panels of
the nuclear reactor, fusion reactor and fusion generator. Writes into <out-dir>:

  cooling-study.png     the cooling mass of vanilla's nuclear reactor, heat exchanger,
                        fusion reactor and fusion generator, part by part, beside ours
  reference-sheet.png   round 2's reference sheet with the cooling study added under it
  <V>-<slug>.png        the variant: idle and working at 2x, key frames, 1x idle/working,
                        its cooling map, a 2x2 block, the stage-4 reactor block, the
                        animation plan and every measurement
  <V>-<slug>-1x.gif     the working loop at game scale (64 px a tile)
  <V>-<slug>-2x.gif     the same at 2x
  contact-sheet.png     the three working at game scale beside the nuclear reactor, fusion
                        reactor and fusion generator (working), round 3's three, and the
                        reactor blocks
  measurements.json     every number on the sheets

Measured at game scale (the 2x renders halved), as round 3: rise = tiles the opaque
silhouette (alpha > 200, shadows excluded) reaches above the footprint's north edge;
coverage = share of the footprint's pixels it covers (idle); blue = round 2's measure
(pixels the light changes, spill on metal included) and the emissive-only share.

The cooling shares: ours are exact (r4_blockout.py's mask mode renders every part in a
flat category colour); vanilla's are hand-annotated on the sprites (VANILLA_PARTS below:
ellipses, boxes and stroked paths over each part, drawn in order, later over earlier), so
they are estimates, good to about +-5 points. Where vanilla ships a part as its own layer
(the nuclear reactor's heat-pipe stubs, the fusion reactor's eight connection pieces) that
layer is painted as plumbing first and the annotations go over it, so a connection piece
counts as plumbing only where it stands outside the annotated torus.
"""
import json
import os
import sys
import textwrap

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageSequence

ROOT, REFP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
R2 = os.path.join(HERE, "..", "round-2")
R3 = os.path.join(HERE, "..", "round-3")
FD = os.environ.get("FACTORIO_DATA", os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
os.makedirs(OUT, exist_ok=True)

PPT = 64
GROUND = (74, 66, 58, 255)
BG = (30, 30, 30, 255)
GRID = (255, 255, 255, 30)
FOOT = (255, 255, 255, 110)
TEXT = (225, 220, 210, 255)
SUB = (165, 160, 150, 255)
MARK = (120, 200, 255, 255)
VANILLA = json.load(open(os.path.join(R3, "vanilla-measured.json")))
R3M = json.load(open(os.path.join(R3, "measurements.json")))


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""), size)


SPEED = 0.4          # all three: 48 frames at 0.4 = 2.0 s

# the categories, as r4_blockout.py's MASK_COLOURS
CATS = [("shield", "shielding / core housing", "#3C64C8"),
        ("cool", "coolant plumbing (pipes, hoses, headers, heat pipes)", "#E6B43C"),
        ("vessel", "tanks and exchanger shells", "#D2D2D2"),
        ("pump", "pumps and motors", "#3CB45A"),
        ("radiator", "radiator panels", "#B45AC8"),
        ("mast", "masts and piers", "#8C3C1E"),
        ("light", "glow", "#50E6FF"),
        ("other", "everything else (body, generator, fuel, converter, skids)", "#6E6E6E")]
HEX = {k: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for k, _, h in CATS}

# ---------------------------------------------------------------- vanilla, annotated
# sprite pixels at 64 px a tile, in the main layer's own coordinates.
# ("e", x0, y0, x1, y1, cat) ellipse, ("r", ...) box, ("l", width, [(x, y), ...], cat) stroked path
NUC = "base/graphics/entity/nuclear-reactor/"
FUS = "space-age/graphics/entity/fusion-reactor/"
GEN = "space-age/graphics/entity/fusion-generator/north/"
HXD = "base/graphics/entity/heat-exchanger/"
VANILLA_PARTS = {
    "nuclear reactor 5x5": dict(
        foot=(5, 5),
        main=(NUC + "reactor.png", None, (-5 / 32, -7 / 32)),
        exact=[(NUC + "reactor-pipes.png", None, (-1 / 32, -5 / 32), "cool")],     # its heat-pipe stubs
        parts=[("e", 45, 25, 262, 215, "shield"),
               ("r", 28, 60, 65, 215, "cool"), ("r", 250, 75, 295, 210, "cool"), ("r", 120, 200, 200, 300, "cool"),
               ("e", 40, 118, 82, 170, "vessel"), ("e", 55, 178, 132, 282, "vessel"),
               ("r", 185, 220, 258, 302, "pump"),
               ("l", 22, [(185, 85), (190, 45), (220, 20), (260, 30), (272, 70), (266, 120), (282, 165)], "cool"),
               ("l", 20, [(175, 80), (220, 68), (250, 125), (262, 170)], "cool"),
               ("l", 7, [(100, 145), (130, 140), (170, 150), (210, 190), (220, 208)], "cool"),
               ("l", 7, [(105, 172), (135, 182), (182, 192)], "cool"),
               ("l", 8, [(70, 175), (60, 140), (85, 105), (110, 95)], "cool")],
        thick="corrugated main hoses 0.34 t across, red hoses 0.1 t, riser pipes 0.15 t; the front-right pump "
              "drum 1.1 t; the vessel 3.4 t",
        where="draped over and down the vessel: the two big hoses arch over the top from the back, red hoses "
              "wrap the front, risers stack up both flanks; vessels and the pump drum hold the two front corners"),
    "heat exchanger 3x2": dict(
        foot=(3, 2),
        main=(HXD + "heatex-N-idle.png", None, (-1 / 32, 9.5 / 32)),
        exact=[],
        parts=[("r", 78, 35, 195, 140, "vessel"),
               ("r", 40, 20, 80, 140, "cool"), ("r", 192, 30, 232, 145, "cool"), ("r", 165, 115, 215, 160, "cool"),
               ("r", 40, 90, 66, 135, "cool"), ("r", 112, 0, 165, 35, "pump"), ("r", 127, 55, 150, 145, "cool")],
        thick="the shell 1.8 x 1.6 t; flanged ends 0.35-0.7 t; pipes 0.15 t; the copper heat pipe 0.35 t",
        where="a shell with plumbing on all four sides and a pump-like dome on top; the heat pipe runs down its "
              "face"),
    "fusion reactor 6x6": dict(
        foot=(6, 6),
        main=(FUS + "fusion-reactor-main.png", None, (1 / 32, -5.5 / 32)),
        exact=[(FUS + "fusion-reactor-connection-%d.png" % n, FUS + "fusion-reactor-connection-%d.lua" % n, None,
                "cool") for n in range(1, 9)],                                        # the eight edge ducts
        parts=[("e", 25, 75, 420, 390, "shield"), ("r", 175, 5, 280, 210, "shield"),
               ("r", 120, 165, 175, 260, "cool"), ("r", 260, 200, 310, 260, "cool"), ("r", 150, 320, 310, 380, "cool"),
               ("r", 45, 250, 92, 390, "vessel"), ("r", 307, 205, 360, 335, "vessel"),
               ("e", 97, 45, 155, 95, "vessel"), ("e", 280, 40, 360, 95, "vessel"),
               ("r", 45, 127, 85, 165, "pump"), ("r", 150, 260, 190, 320, "pump"), ("r", 210, 210, 260, 250, "pump")],
        thick="the torus about 1.2 t through; the corner tanks 0.75-0.8 t across and up to 2 t tall; pipes in "
              "the well 0.15-0.25 t; the edge ducts 0.6-0.9 t",
        where="the torus is the mass; tanks stand at the corners outside it, taller than the ring; pumps and "
              "pipework fill the well between ring and column; the ducts cover every edge"),
    "fusion generator 3x5": dict(
        foot=(3, 5),
        main=(GEN + "fusion-generator-north.png", (0, 0, 244, 376), (-2 / 32, -2 / 32)),
        exact=[],
        parts=[("r", 37, 45, 220, 165, "other"),
               ("r", 30, 165, 85, 310, "cool"), ("r", 165, 125, 230, 310, "cool"),
               ("r", 82, 165, 195, 345, "other"),
               ("r", 32, 20, 92, 60, "vessel"), ("r", 160, 17, 220, 60, "vessel"),
               ("r", 30, 220, 75, 260, "pump"), ("r", 182, 190, 222, 225, "pump"),
               ("l", 12, [(45, 60), (50, 85)], "cool"), ("l", 12, [(205, 225), (215, 270)], "cool")],
        thick="the tanks 0.9 t across; the pumps 0.6 t; pipes 0.1-0.15 t",
        where="tanks at the two back corners, pumps on the flanks, pipes down both long sides of the generator "
              "body"),
}


def lua_shift(rel):
    import re
    t = open(os.path.join(FD, rel)).read()
    w = int(re.search(r"width\s*=\s*(\d+)", t).group(1))
    h = int(re.search(r"height\s*=\s*(\d+)", t).group(1))
    sx, sy = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", t).groups())
    return (0, 0, w, h), (sx / 32, sy / 32)


def vanilla_cooling(name, d, pad=1.0):
    """Composite the sprite, paint its category map; returns (sprite-on-ground, map, shares, rise, cover)."""
    fw, fh = d["foot"]
    W, H = int((fw + 2 * pad) * PPT), int((fh + 2 * pad + 1.0) * PPT)
    o = (W / 2, H / 2 + 0.5 * PPT)
    comp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cat = Image.new("RGB", (W, H), HEX["other"])
    layers = []

    def place(rel, crop, shift):
        im = Image.open(os.path.join(FD, rel)).convert("RGBA")
        if crop:
            im = im.crop(crop)
        x = round(o[0] + shift[0] * PPT - im.width / 2)
        y = round(o[1] + shift[1] * PPT - im.height / 2)
        return im, (x, y)

    rel, crop, shift = d["main"]
    main, mo = place(rel, crop, shift)
    comp.alpha_composite(main, mo)
    for rel, lua, shift, c in d["exact"]:
        crop = None
        if lua:
            crop, shift = lua_shift(lua)
        im, po = place(rel, crop, shift)
        layers.append((im, po))
        comp.alpha_composite(im, po)
        a = im.split()[3].point(lambda v: 255 if v > 128 else 0)
        cat.paste(Image.new("RGB", im.size, HEX[c]), po, a)
    dr = ImageDraw.Draw(cat)
    for p in d["parts"]:
        if p[0] in "er":
            x0, y0, x1, y1 = p[1:5]
            box = [x0 + mo[0], y0 + mo[1], x1 + mo[0], y1 + mo[1]]
            (dr.ellipse if p[0] == "e" else dr.rectangle)(box, fill=HEX[p[5]])
        else:
            dr.line([(x + mo[0], y + mo[1]) for x, y in p[2]], fill=HEX[p[3]], width=p[1], joint="curve")
    solid_ = comp.split()[3].point(lambda v: 255 if v > 200 else 0)
    shares = shares_of(cat, solid_)
    g = ground(W / PPT, H / PPT, (o[0] / PPT, o[1] / PPT), (fw, fh))
    g.alpha_composite(comp)
    m = Image.new("RGBA", (W, H), BG)
    m.paste(cat, (0, 0), solid_)
    top = solid_.getbbox()[1]
    rise = (o[1] - fh / 2 * PPT - top) / PPT
    fb = solid_.crop((round(o[0] - fw / 2 * PPT), round(o[1] - fh / 2 * PPT), round(o[0] + fw / 2 * PPT),
                      round(o[1] + fh / 2 * PPT)))
    cover = fb.histogram()[255] / (fb.width * fb.height)
    return g, m, shares, round(rise, 2), round(100 * cover, 1)


def shares_of(cat_rgb, solid_mask):
    """Share of each category among the solid pixels, by nearest category colour."""
    px = cat_rgb.convert("RGB")
    out = {k: 0 for k in HEX}
    total = 0
    data = list(px.getdata())
    mask = list(solid_mask.getdata())
    cache = {}
    for p, m in zip(data, mask):
        if not m:
            continue
        total += 1
        k = cache.get(p)
        if k is None:
            k = min(HEX, key=lambda c: sum((HEX[c][i] - p[i]) ** 2 for i in range(3)))
            cache[p] = k
        out[k] += 1
    return {k: round(100 * v / max(1, total), 1) for k, v in out.items()}


def share_bar(shares, w=360, h=18):
    im = Image.new("RGBA", (w, h), BG)
    dr = ImageDraw.Draw(im)
    x = 0.0
    for k, _, _ in CATS:
        dx = w * shares.get(k, 0) / 100
        if dx > 0:
            dr.rectangle([round(x), 0, round(x + dx), h], fill=HEX[k])
        x += dx
    return im


def cooling_mass(sh):
    """Cooling mass = plumbing + vessels + pumps + radiators (shielding listed apart)."""
    return round(sh["cool"] + sh["vessel"] + sh["pump"] + sh["radiator"], 1)


# ---------------------------------------------------------------- helpers (round 2's)

def info(v, mode):
    return json.load(open(f"{ROOT}/{v}-{mode}/info.json"))


def load(path, k):
    im = Image.open(path).convert("RGBa")
    if k != 1:
        im = im.resize((im.width // k, im.height // k), Image.LANCZOS)
    return im.convert("RGBA")


def bloom(rgb, scale=1.0):
    r, g, b = rgb.convert("RGB").split()
    hot = ImageChops.subtract(b, r)
    m = Image.eval(hot, lambda v: 0 if v < 60 else min(255, (v - 60) * 3))
    bright = Image.eval(b, lambda v: 0 if v < 150 else min(255, (v - 150) * 3))
    m = ImageChops.multiply(m, bright)
    src = Image.composite(rgb.convert("RGB"), Image.new("RGB", rgb.size), m)
    near = src.filter(ImageFilter.GaussianBlur(3 * scale))
    far = src.filter(ImageFilter.GaussianBlur(9 * scale))
    out = ImageChops.add(rgb.convert("RGB"), Image.eval(near, lambda v: int(v * 0.55)))
    out = ImageChops.add(out, Image.eval(far, lambda v: int(v * 0.45)))
    return out.convert("RGBA")


def ground(w, h, origin, foot, ppt=PPT, outline=True):
    W, H = int(w * ppt), int(h * ppt)
    g = Image.new("RGBA", (W, H), GROUND)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    ox, oy = origin[0] * ppt, origin[1] * ppt
    x0, y0 = ox - foot[0] / 2 * ppt, oy - foot[1] / 2 * ppt
    x = x0 % ppt
    while x < W:
        dr.line([(x, 0), (x, H)], fill=GRID)
        x += ppt
    y = y0 % ppt
    while y < H:
        dr.line([(0, y), (W, y)], fill=GRID)
        y += ppt
    if outline and foot[0]:
        dr.rectangle([x0, y0, x0 + foot[0] * ppt, y0 + foot[1] * ppt], outline=FOOT)
    g.alpha_composite(ov)
    return g


def paste(dst, im, x, y):
    x, y = round(x), round(y)
    cx, cy = max(0, -x), max(0, -y)
    dst.alpha_composite(im.crop((cx, cy, im.width, im.height)), (x + cx, y + cy))


def panel(sprites, inf, scale, pad=(0.8, 0.9, 2.2, 0.6), glow=True):
    fw, fh = inf["foot"]
    ppt = PPT * scale
    ox, oy = inf["origin"]
    top = fh / 2 + pad[1]
    w = fw + pad[0] + pad[2]
    h = top + fh / 2 + pad[3]
    origin = (pad[0] + fw / 2, top)
    g = ground(w, h, origin, (fw, fh), ppt)
    for s in sprites:
        paste(g, s, origin[0] * ppt - ox * ppt, origin[1] * ppt - oy * ppt)
    return bloom(g, scale) if glow else g


def label(img, xy, text, size=12, fill=TEXT, bold=False):
    ImageDraw.Draw(img).text(xy, text, font=font(size, bold), fill=fill)


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


def stack_v(rows, gap=8, width=None):
    W = width or max(r.width for r in rows)
    out = Image.new("RGBA", (W, sum(r.height for r in rows) + gap * (len(rows) - 1)), BG)
    y = 0
    for r in rows:
        out.alpha_composite(r, (0, y))
        y += r.height + gap
    return out


def text_block(width, paras, size=13):
    f, fb = font(size), font(size, True)
    chars = int(width / (size * 0.56))
    lines = []
    for head, body in paras:
        lines.append((head, True))
        for para in body if isinstance(body, list) else [body]:
            for i, l in enumerate(textwrap.wrap(para, chars - 3)):
                lines.append((("- " if isinstance(body, list) and i == 0 else ("  " if isinstance(body, list) else ""))
                              + l, False))
        lines.append(("", False))
    out = Image.new("RGBA", (width, 10 + int(size * 1.45) * len(lines)), BG)
    dr = ImageDraw.Draw(out)
    y = 6
    for t, bold in lines:
        dr.text((12, y), t, font=fb if bold else f, fill=TEXT if bold else SUB)
        y += int(size * 1.45)
    return out


def solid(im):
    return im.split()[3].point(lambda v: 255 if v > 200 else 0)


def lit_fraction(work, idle):
    """Round 2's measure: share of solid pixels the light changes (bluer or brighter by > 40)."""
    db = ImageChops.subtract(work.split()[2], idle.split()[2])
    dl = ImageChops.subtract(work.convert("L"), idle.convert("L"))
    d = ImageChops.lighter(db, dl).point(lambda v: 255 if v > 40 else 0)
    s = solid(work)
    return ImageChops.multiply(d, s).histogram()[255] / max(1, s.histogram()[255])


def emissive_fraction(work):
    """Saturated bright blue only (b > 170 and b - r > 70): the glow layer's share, roughly."""
    r, g, b, _ = work.split()
    m1 = b.point(lambda v: 255 if v > 170 else 0)
    m2 = ImageChops.subtract(b, r).point(lambda v: 255 if v > 70 else 0)
    s = solid(work)
    return ImageChops.multiply(ImageChops.multiply(m1, m2), s).histogram()[255] / max(1, s.histogram()[255])


def rise_and_cover(im, inf):
    """At game scale: tiles above the north edge, share of the footprint covered."""
    a = solid(im)
    fw, fh = inf["foot"]
    ox, oy = inf["origin"][0] * PPT, inf["origin"][1] * PPT
    top = a.getbbox()[1]
    rise = (oy - fh / 2 * PPT - top) / PPT
    box = a.crop((round(ox - fw / 2 * PPT), round(oy - fh / 2 * PPT), round(ox + fw / 2 * PPT),
                  round(oy + fh / 2 * PPT)))
    return rise, box.histogram()[255] / (box.width * box.height)


def gif(frames, path, ms, ncol=128):
    rgb = [f.convert("RGB") for f in frames]
    sample = Image.new("RGB", (rgb[0].width, rgb[0].height * 4))
    for j, k in enumerate(range(0, len(rgb), max(1, len(rgb) // 4))):
        if j < 4:
            sample.paste(rgb[k], (0, j * rgb[0].height))
    pal = sample.quantize(ncol, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in rgb]
    q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=False, disposal=1)


def mark_rise(p, inf, scale, pad, rise):
    """Draw the rise bar on a panel made by panel() with the same pad."""
    ppt = PPT * scale
    fw, fh = inf["foot"]
    x = (pad[0] + fw) * ppt + 8
    ny = (pad[1]) * ppt
    ty = ny - rise * ppt
    dr = ImageDraw.Draw(p)
    dr.line([(x, ty), (x, ny)], fill=MARK, width=2)
    for y in (ty, ny):
        dr.line([(x - 4, y), (x + 4, y)], fill=MARK, width=2)
    dr.text((x + 6, (ty + ny) / 2 - 7), "%+.2f t" % rise, font=font(11), fill=MARK)




# ---------------------------------------------------------------- the variants' words

FAMILY = ("Cooling kit (all three, the same parts): a stepped lead shield round the core (a drum and a "
          "narrower tier on it, ribbed, banded, bolted, shield blocks round both feet); a coolant ring header "
          "round the drum; 40-44 heavy radiator panels standing radially, sloping from the shield down to the "
          "rim, a header pipe along each top and a lagged manifold ring over their inner ends; circulation "
          "pumps (volute, red coupling guard, ribbed teal motor, terminal box) on skids; expansion tanks (pale, "
          "teal-banded, ladder, relief valve); heat-exchanger shells (flanged channel heads, saddles, nozzles); "
          "fat lagged loops (0.28 t across) arching over the panels into the shield, ribbed hoses (0.14 t) "
          "beside them. Heat leaves by the radiators and the coolant: no fans, louvres, steam or orange.")

VARIANTS = {
    "1": dict(
        slug="the-gyre-spire", name="THE GYRE SPIRE",
        layout="Round 3's Gyre Spire on a heavy plant. The stepped shield (drum 2.6 t across, 0.9 high; tier "
               "2.0 t, to 1.38) carries the bowl, the core in its counter-rotating bands and the caged column "
               "to 4.65. Forty radiator panels slope from 1.1 t at the shield to 0.5 at the rim; four masts on "
               "lead piers stand among them at the diagonals. Corners: a 1.7 t expansion tank and the "
               "spent-cell rack SW, a pump and tank SE, a pump NW, an exchanger shell and tank NE; exchanger "
               "shells along the W and N edges; magazine S, converter E. Fat lagged loops arch from the pumps "
               "and the big tank over the panels into the shield tier.",
        pitch="Read: a lighthouse in a power station -- the light and its lightning on top, a plant of "
              "tanks, pumps and radiators carrying the heat off below it. Fuel in: teal magazine S, a chute "
              "into the shield tier; spent cells to the rack SW. Blue: the core through the band gaps, beams "
              "sweeping the radiator panels, the column through its cage, the corona, the arcs. Signature: "
              "unchanged -- the bands' counter-rotation at the foot, arcs walking the column above it. "
              "Finish: lead shield and bands edged in copper, pale lagged loops and tanks with teal bands, "
              "teal pump motors, grey radiator panels, brown-glazed porcelain.",
        blue_rule="\"The light is the emitter core and the column standing on it: seen through the gaps of the "
                  "turning bands at its foot, as beams that sweep the radiator banks, between the bars of the "
                  "column's cage, and as arcs from the masts to the column. No other part glows.\"",
        plan=["structure (animation layer 1): 48 frames, animation_speed 0.4 (2.0 s). Moving parts only -- "
              "bands and gimbal, a crop round the core about 2.6 x 2.0 tiles; inner band +90 deg a loop, "
              "outer -60, gimbal +120 (4/6/3-fold, seamless)",
              "glow (draw_as_glow, same Animation): core, column bands climbing 2 a loop, corona, arcs; 48 "
              "frames, crop about 3.6 x 5 tiles (masts to column). Arcs drawn fresh each frame",
              "base: 1 frame repeated (repeat_count 48) -- the whole cooling plant is in it, nothing in it "
              "moves; the shadow 1 frame",
              "idle_animation: the same layers, 48 frames of one parked pose, no glow layer",
              "perceived_performance scales animation speed only: bands turn and arcs crawl faster under "
              "load; brightness does not scale (no working_visualisations on a burner-generator)",
              "the engine swaps idle for working at once: no start-up sequence"],
        reactor="Radiant Reactor 7x7 (the plant at 1.38x; block of four shown): each keeps three of its own "
                "masts; where four reactors meet, their inner corners are left clear for one shared mast, "
                "taller, arcing into all four columns (round 3's Crown link). Neighbours are joined across "
                "each edge by a coolant bridge: two lagged pipes on a plinth with a lit duct between. The "
                "bonus reads as the shared mast and the bridges.",
        block_note="Square and symmetric bar the dressing: one plate serves four directions if the magazine "
                   "and converter turn with it. Generators pack edge to edge; their corner tanks meet."),
    "2": dict(
        slug="the-banded-spire", name="THE BANDED SPIRE",
        layout="Round 3's Banded Spire on a heavy plant. The Reaction Plant's banded drum (2.84 t across, 0.95 "
               "high, teal ring) is now the lower shield, with a tier on it to 1.45 carrying the blue slot "
               "ring; the four turning tiers of the cage rise from it to 4.8. Forty-four radiator panels slope "
               "from 0.9 t to 0.45 at the rim; three masts on lead piers (30/150/270 deg). Corners, edges and "
               "loops as variant 1; magazine SSE, converter E.",
        pitch="Read: a tower that spins in layers on a drum in a ring of radiators -- the most Reaction-Plant "
              "of the three, the sibling read strongest. Fuel in: teal magazine SSE, a chute into the shield "
              "tier. Blue: the column through the moving lattice, the slot ring on the tier, corona, arcs. "
              "Signature: the alternating tiers. Finish: the Reaction Plant's drum and teal ring, lead/collar "
              "tiers edged in copper, pale lagged loops, teal motors, brown-glazed porcelain.",
        blue_rule="\"The light is the column, seen through the gaps between the turning tiers of its cage, "
                  "the ring of slots round the shield, and the arcs from the masts into the cage. No other "
                  "part glows.\"",
        plan=["structure: 48 frames, animation_speed 0.4 (2.0 s); each tier +/-120 deg a loop (3-fold, "
              "seamless); crop about 1.4 x 4.4 tiles -- the narrowest moving crop of the three",
              "glow: column bands (2 climbs a loop), lattice leaks, slots, corona, arcs; 48 frames; crop about "
              "3.9 x 5 tiles",
              "base: 1 frame repeated, the whole plant in it; idle_animation: tiers parked out of step, dark",
              "perceived_performance: tiers turn and arcs step faster under load",
              "a cheap variant: the moving crop is tall and thin"],
        reactor="Radiant Reactor 7x7, five tiers: each keeps its three masts; the shared corner mast where "
                "four meet arcs into all four cages; coolant bridges across each edge.",
        block_note="Three masts break the symmetry: one plate, rotations not needed (masts are dressing)."),
    "3": dict(
        slug="the-crown", name="THE CROWN",
        layout="Round 3's Crown on a heavy plant. The stepped shield (drum 2.56 t across, 0.8 high; tier to "
               "1.2) carries the Gyre whole: bowl, core, counter-rotating bands, four lead pylons to a crown "
               "bearing at 2.5 and the needle to 3.55. Forty radiator panels from 1.0 t to 0.5; the four "
               "porcelain masts stand on octagonal decks at the corners and lean in 20 deg. The equipment "
               "goes along the edges instead: tanks SW and SE, pumps S-E and N-W, exchanger shells N and W, "
               "cell rack and magazine S, converter E.",
        pitch="Read: a crown of lightning over a power station -- four arcs meet over the core above a ring "
              "of radiators, the tallest metal is the corner masts. Fuel in: teal magazine S, a chute into "
              "the shield; spent cells to the rack. Blue: the core through the bands, beams on the panels, "
              "the needle, arcs. Signature: four arcs converging and wandering on the needle while the bands "
              "turn below. Finish: the Gyre's lead and copper, pale tanks and lagging, teal motors, four big "
              "brown-glazed masts framing the corners (the silhouette is a star, not a square).",
        blue_rule="\"The light is the emitter core, seen through the gaps of its turning bands and as beams on "
                  "the radiator banks, the needle over it, and the arcs from the corner masts to the needle. "
                  "No other part glows.\"",
        plan=["structure: 48 frames, animation_speed 0.4 (2.0 s); bands and gimbal as the Gyre; crop about "
              "2.0 x 2.2 tiles",
              "glow: core pulse, needle, arcs; 48 frames; crop nearly the whole sprite (corner to corner), "
              "about 4.4 x 4.4 tiles -- the arcs make the glow sheet the largest of the three",
              "base: 1 frame repeated, the whole plant in it; idle_animation: bands parked, needle and core "
              "dark, no arcs",
              "perceived_performance: bands and arcs faster under load"],
        reactor="Radiant Reactor 7x7: as round 3 -- where four reactors meet, their inner corner masts become "
                "one shared mast, taller, arcing into all four needles; coolant bridges across each edge.",
        block_note="Corner masts sit inside the footprint, so generators pack edge to edge; in a block the "
                   "masts of four neighbours stand in a cluster at each shared corner."),
}


# ---------------------------------------------------------------- the cooling study

meas = {"vanilla": VANILLA, "vanilla_cooling": {}, "categories": {k: d for k, d, _ in CATS}}
study_rows = []
for name, d in VANILLA_PARTS.items():
    g, m, sh, rise, cover = vanilla_cooling(name, d)
    meas["vanilla_cooling"][name] = dict(shares_pct=sh, cooling_mass_pct=cooling_mass(sh), rise_tiles=rise,
                                         coverage_pct=cover, thickness=d["thick"], where=d["where"])
    study_rows.append((name, g, m, sh, d))
    print(name, sh, cooling_mass(sh), rise, cover)


def legend(width):
    im = Image.new("RGBA", (width, 26), BG)
    dr = ImageDraw.Draw(im)
    x = 10
    for k, desc, _ in CATS:
        dr.rectangle([x, 7, x + 14, 21], fill=HEX[k])
        t = desc.split(" (")[0]
        dr.text((x + 19, 6), t, font=font(12), fill=SUB)
        x += 26 + int(dr.textlength(t, font=font(12)))
    return im


def study_panel(title, sprite, catmap, sh, note, scale=2):
    """One building: sprite and category map side by side at `scale`, the share bar and numbers."""
    a = sprite.resize((sprite.width * scale, sprite.height * scale), Image.LANCZOS) if scale != 1 else sprite
    b = catmap.resize((catmap.width * scale, catmap.height * scale), Image.NEAREST) if scale != 1 else catmap
    pr = row([a, b], [title, "parts"], gap=8)
    bar = share_bar(sh, pr.width - 24)
    nums = "  ".join(f"{k} {sh[k]:.0f}%" for k, _, _ in CATS if sh.get(k, 0) >= 0.5)
    txt = text_block(pr.width, [(f"cooling mass {cooling_mass(sh):.0f}%  (plumbing + vessels + pumps + "
                                 f"radiators; shielding {sh['shield']:.0f}%)", [nums] + note)], size=12)
    out = Image.new("RGBA", (pr.width, pr.height + bar.height + 10 + txt.height), BG)
    out.alpha_composite(pr, (0, 0))
    out.alpha_composite(bar, (12, pr.height + 4))
    out.alpha_composite(txt, (0, pr.height + bar.height + 10))
    return out


def build_study(ours):
    """ours: list of (title, sprite at 1x on ground, mask on ground, shares)."""
    van = [study_panel(n, g, m, sh, [f"thickness: {d['thick']}", f"where: {d['where']}"], scale=1)
           for n, g, m, sh, d in study_rows]
    ourp = [study_panel(t, g, m, sh, [], scale=1) for t, g, m, sh in ours]
    rv = stack_v([row(van[:2], ["", ""], top=4), row(van[2:], ["", ""], top=4)])
    ro = row(ourp, ["" for _ in ourp], top=4)
    W = max(rv.width, ro.width, 1600)
    vc = meas["vanilla_cooling"]
    findings = [
        f"Cooling is a third to a half of what you see. Cooling mass (plumbing + vessels + pumps): nuclear "
        f"reactor {vc['nuclear reactor 5x5']['cooling_mass_pct']:.0f}%, heat exchanger "
        f"{vc['heat exchanger 3x2']['cooling_mass_pct']:.0f}%, fusion reactor "
        f"{vc['fusion reactor 6x6']['cooling_mass_pct']:.0f}%, fusion generator "
        f"{vc['fusion generator 3x5']['cooling_mass_pct']:.0f}% (hand-annotated, +-5 points). The core's own "
        f"housing is the rest: the nuclear sphere {vc['nuclear reactor 5x5']['shares_pct']['shield']:.0f}%, "
        f"the fusion torus and column {vc['fusion reactor 6x6']['shares_pct']['shield']:.0f}%.",
        "It is thick. The nuclear reactor's main hoses are a third of a tile across, its pump drum a tile; the "
        "fusion reactor's corner tanks are 0.8 t across and taller than its ring, its edge ducts 0.6-0.9 t. "
        "Nothing that carries heat is drawn thinner than 0.1 t, and the big runs are 0.3 t and up.",
        "It climbs. The nuclear reactor's hoses arch over the top of the vessel; the fusion reactor's tanks "
        "stand up at the corners and its torus is 1.2 t through; the mass is highest round the core and "
        "steps down to the edge, never a flat ring of fins.",
        "It fills the corners. Tanks and pumps sit at the corners (nuclear front corners, fusion all four, "
        "generator the back two), which is how the fusion reactor reaches 92% coverage without a plinth.",
        "It is pale against dark: cream and pale-blue tanks and lagging against dark bodies and pipe-work "
        "(FFF #146), so the cooling reads first at 1x.",
        "For the Core in near-vacuum: no air, so no fans or louvres; heat leaves by coolant to radiators. "
        "Round 4 takes the vanilla parts (pumps with motors, tanks, exchanger shells, headers, fat lagged "
        "runs and ribbed hoses) and turns the round-3 fin bed into heavy radiator panels sloping down from a "
        "stepped lead shield; the mass rises toward the core, the corners carry tanks and pumps."]
    txt = text_block(W, [("FINDINGS", findings), ("ROUND 4'S KIT", FAMILY)], size=13)
    head = Image.new("RGBA", (W, 54), BG)
    label(head, (10, 6), "RADIANT GENERATOR, ROUND 4 -- THE COOLING STUDY: HOW MUCH OF A REACTOR IS COOLING", 20,
          bold=True)
    label(head, (10, 32), "Vanilla at game scale (64 px a tile), each part painted in its category; "
          "ours at 1x from the exact category pass. Shares are of the building's opaque pixels.", 12, SUB)
    sub = Image.new("RGBA", (W, 26), BG)
    label(sub, (10, 6), "ROUND 4 (ours, 1x, exact)", 14, TEXT, bold=True)
    return stack_v([head, legend(W), rv, sub, ro, txt], width=W)


# ---------------------------------------------------------------- per variant

contact = []
ours_study = []
for V, o in VARIANTS.items():
    ih, ia, ir, im_ = info(V, "hero"), info(V, "anim"), info(V, "reactor"), info(V, "mask")
    fw, fh = ih["foot"]
    N = ia["frames"]
    hero_w2 = load(f"{ROOT}/{V}-hero/working.png", 2)
    hero_i2 = load(f"{ROOT}/{V}-hero/idle.png", 2)
    frames2 = [load(f"{ROOT}/{V}-anim/f{i:03d}.png", 1) for i in range(N)]
    frames1 = [f.resize((f.width // 2, f.height // 2), Image.LANCZOS) for f in frames2]
    idle1 = load(f"{ROOT}/{V}-anim/idle.png", 2)
    reactor1 = load(f"{ROOT}/{V}-reactor/reactor.png", 2)
    mask = Image.open(f"{ROOT}/{V}-mask/mask.png").convert("RGBA")

    rises, covers = zip(*(rise_and_cover(f, ia) for f in frames1))
    rise_i, cover_i = rise_and_cover(idle1, ia)
    lit = [lit_fraction(f, idle1) for f in frames1]
    emi = [emissive_fraction(f) for f in frames1]
    sh = shares_of(mask.convert("RGB"), solid(mask))
    m = dict(name=o["name"], footprint=f"{fw}x{fh}", frames=N, animation_speed=SPEED,
             loop_seconds=round(N / (60 * SPEED), 2), rise_tiles_max=round(max(rises), 2),
             rise_tiles_idle=round(rise_i, 2), coverage_pct=round(100 * cover_i, 1),
             blue_lit_mean_pct=round(100 * sum(lit) / N, 1), blue_lit_min_pct=round(100 * min(lit), 1),
             blue_lit_max_pct=round(100 * max(lit), 1), blue_emissive_mean_pct=round(100 * sum(emi) / N, 1),
             reactor=f"{ir['pitch']:g}x{ir['pitch']:g}", shares_pct=sh, cooling_mass_pct=cooling_mass(sh))
    ms = round(1000 / (60 * SPEED))
    m["gif_frame_ms"] = ms
    pad = (0.8, 0.9, 2.2, 0.6)
    gpad = (0.5, 0.6, 1.5, 0.4)                       # tighter for the GIFs (1x under 5 MB)
    g1 = [panel([f], ia, 1, gpad) for f in frames1]
    g2 = [panel([f], ia, 2, gpad) for f in frames2]
    gif(g1, f"{OUT}/{V}-{o['slug']}-1x.gif", ms, ncol=104)       # 104 colours: 1x under 5 MB
    gif(g2, f"{OUT}/{V}-{o['slug']}-2x.gif", ms)
    m["gif_1x_bytes"] = os.path.getsize(f"{OUT}/{V}-{o['slug']}-1x.gif")
    m["gif_2x_bytes"] = os.path.getsize(f"{OUT}/{V}-{o['slug']}-2x.gif")
    meas[V] = m

    hero_i = panel([hero_i2], ih, 2, pad)
    hero_w = panel([hero_w2], ih, 2, pad)
    mark_rise(hero_w, ih, 2, pad, m["rise_tiles_max"])
    keys = [int(N * t) for t in (0, 0.25, 0.5, 0.75)]
    kp = (0.4, 0.9, 1.0, 0.3)
    keyp = [panel([frames1[k]], ia, 1, kp) for k in keys]
    r1 = row([hero_i, hero_w], ["idle (off) -- 2x", f"working, frame 0 -- 2x  (rise {m['rise_tiles_max']:+.2f} t)"])
    r1b = row(keyp, [f"frame {k}/{N} -- 1x" for k in keys])
    w1 = panel([frames1[0]], ia, 1, pad)
    i1 = panel([idle1], ia, 1, pad)
    mk = Image.new("RGBA", mask.size, BG)
    mk.alpha_composite(mask)
    mk1 = panel([mask], im_, 1, pad, glow=False)
    ours_study.append((f"{V} {o['name'].lower()}, 5x5", panel([frames1[0]], ia, 1, (0.3, 0.6, 0.3, 0.3)),
                       panel([mask], im_, 1, (0.3, 0.6, 0.3, 0.3), glow=False), sh))
    bw, bh = 2 * fw + 3.0, 2 * fh + 2.2
    blk = ground(bw, bh, (1 + fw / 2, 1.4 + fh / 2), (0, 0))
    ImageDraw.Draw(blk).rectangle([PPT, 1.4 * PPT, (1 + 2 * fw) * PPT, (1.4 + 2 * fh) * PPT], outline=FOOT)
    for j in range(2):
        for i in range(2):
            f = frames1[(i * 7 + j * 19) % N]
            ox, oy = (1 + fw / 2 + i * fw) * PPT, (1.4 + fh / 2 + j * fh) * PPT
            paste(blk, f, ox - ia["origin"][0] * PPT, oy - ia["origin"][1] * PPT)
    blk = bloom(blk)
    rp = ir["pitch"]
    rpan = ground(ir["canvas"][0], ir["canvas"][1], ir["origin"], (2 * rp, 2 * rp))
    paste(rpan, reactor1, 0, 0)
    rpan = bloom(rpan)
    rpan_h = rpan.resize((rpan.width * 3 // 4, rpan.height * 3 // 4), Image.LANCZOS)
    r2 = row([i1, w1, mk1, blk], ["idle, 1x", "working, 1x", "cooling map, 1x (legend on the cooling study)",
                                  "a block of 4, 1x (frames out of step)"])
    r3 = row([rpan_h], [f"stage 4: Radiant Reactor, {rp:g}x{rp:g}, block of 4 -- 3/4 scale"])
    W = max(r1.width, r1b.width, r2.width, r3.width, 1500)
    van = VANILLA
    vc = meas["vanilla_cooling"]
    facts = (f"Footprint 5x5.  Rise above the north edge: {m['rise_tiles_max']:+.2f} tiles working (vanilla: "
             f"nuclear {van['nuclear reactor 5x5']['rise_tiles']:+.2f}, fusion reactor "
             f"{van['fusion reactor 6x6']['rise_tiles']:+.2f}, refinery "
             f"{van['oil refinery 5x5 (north)']['rise_tiles']:+.2f}).  Coverage: {m['coverage_pct']}% of the "
             f"footprint (fusion reactor {van['fusion reactor 6x6']['coverage_pct']}%, refinery "
             f"{van['oil refinery 5x5 (north)']['coverage_pct']}%, nuclear "
             f"{van['nuclear reactor 5x5']['coverage_pct']}%; round 3 {R3M[V]['coverage_pct']}%).  Blue: "
             f"{m['blue_lit_mean_pct']}% of the building's pixels lit, mean over the loop "
             f"({m['blue_lit_min_pct']}-{m['blue_lit_max_pct']}%; light spill on metal included, round 2's "
             f"measure; round 3 {R3M[V]['blue_lit_mean_pct']}%); emissive blue alone "
             f"{m['blue_emissive_mean_pct']}%.  Loop: {N} frames at animation_speed {SPEED} = "
             f"{m['loop_seconds']} s.  GIF 1x {m['gif_1x_bytes'] / 1e6:.1f} MB.")
    cool = (f"Cooling mass {m['cooling_mass_pct']:.0f}% of the sprite (plumbing {sh['cool']:.0f}%, vessels "
            f"{sh['vessel']:.0f}%, pumps {sh['pump']:.0f}%, radiators {sh['radiator']:.0f}%), shielding "
            f"{sh['shield']:.0f}%, masts {sh['mast']:.0f}%, glow {sh['light']:.0f}%, other {sh['other']:.0f}%. "
            f"Vanilla (annotated): nuclear {vc['nuclear reactor 5x5']['cooling_mass_pct']:.0f}% cooling + "
            f"{vc['nuclear reactor 5x5']['shares_pct']['shield']:.0f}% vessel; fusion reactor "
            f"{vc['fusion reactor 6x6']['cooling_mass_pct']:.0f}% + "
            f"{vc['fusion reactor 6x6']['shares_pct']['shield']:.0f}% torus and column.")
    txt = text_block(W, [("LAYOUT", o["layout"]), ("PITCH", o["pitch"]), ("COOLING", [cool, FAMILY]),
                         ("LIGHT RULE -- spec 3.1/3.3 wording this variant needs", o["blue_rule"]),
                         ("ANIMATION PLAN (burner-generator: animation + idle_animation only; all glow is "
                          "draw_as_glow layers inside them)", o["plan"]),
                         ("STAGE 4: THE RADIANT REACTOR", o["reactor"]), ("TILING", o["block_note"]),
                         ("MEASURED", facts)])
    head = Image.new("RGBA", (W, 54), BG)
    label(head, (10, 6), f"RADIANT GENERATOR, ROUND 4 -- VARIANT {V}: {o['name']} (5x5), BULK AND COOLING", 22,
          bold=True)
    label(head, (10, 34), "Lit Blender blockout (layered finish, emission + core lights, GPU; ChatGPT was not "
          "reachable). Not adopted. 64 px a tile at 1x. The loop is in the GIFs beside this sheet.", 13, SUB)
    sheet = stack_v([head, r1, r1b, r2, r3, txt], width=W)
    sheet.save(f"{OUT}/{V}-{o['slug']}.png")
    contact.append((V, f"{V} {o['name'].lower()}, 5x5, working", w1, rpan))
    print(V, {k: v for k, v in m.items() if k != "shares_pct"})

# ---------------------------------------------------------------- the cooling study and reference sheet

study = build_study(ours_study)
study.save(f"{OUT}/cooling-study.png")
r2ref = Image.open(os.path.join(R2, "reference-sheet.png")).convert("RGBA")
W = max(r2ref.width, study.width)
band = Image.new("RGBA", (W, 40), BG)
label(band, (10, 10), "ROUND 4 ADDITION, 2026-10-11: THE COOLING STUDY (round 2's sheet above, unchanged)", 16,
      TEXT, bold=True)
stack_v([r2ref, band, study], width=W).save(f"{OUT}/reference-sheet.png")

# ---------------------------------------------------------------- contact sheet


def gif_frame0(path):
    return next(ImageSequence.Iterator(Image.open(path))).convert("RGBA")


refs = [
    ("vanilla nuclear reactor 5x5, working", Image.open(f"{REFP}/nuclear-reactor-working.png").convert("RGBA")),
    ("fusion reactor 6x6, working", Image.open(f"{REFP}/fusion-reactor-working.png").convert("RGBA")),
    ("fusion generator 3x5, working", Image.open(f"{REFP}/fusion-generator-working.png").convert("RGBA")),
]
row_r = row([p for _, p in refs], [n for n, _ in refs])
r3s = [(f"round 3: {V} {VARIANTS[V]['name'].lower()} (cover {R3M[V]['coverage_pct']}%)",
        gif_frame0(os.path.join(R3, f"{V}-{VARIANTS[V]['slug']}-1x.gif"))) for V in VARIANTS]
row_3 = row([p for _, p in r3s], [n for n, _ in r3s])
row_o = row([p for _, _, p, _ in contact],
            [f"{n}  (rise {meas[V]['rise_tiles_max']:+.2f} t, cover {meas[V]['coverage_pct']}%, cooling "
             f"{meas[V]['cooling_mass_pct']:.0f}%)" for V, n, _, _ in contact])
half = [(f"{V}: reactor block, 4 x 7x7, shared corner mast -- HALF scale",
         r.resize((r.width // 2, r.height // 2), Image.LANCZOS)) for V, _, _, r in contact]
row_x = row([p for _, p in half], [n for n, _ in half])
W = max(row_r.width, row_o.width, row_x.width, row_3.width)
head = Image.new("RGBA", (W, 52), BG)
label(head, (10, 6), "RADIANT GENERATOR, ROUND 4 -- BULK AND COOLING, AT GAME SCALE", 20, bold=True)
label(head, (10, 32), "64 px a tile. Top: vanilla working. Then round 3 as it was (GIF frame 0, no bloom), round "
      "4 working (frame 0, shadows and bloom), and each variant's stage-4 Radiant Reactor block of four, half "
      "scale. Lit Blender blockouts.", 12, SUB)
stack_v([head, row_r, row_3, row_o, row_x], width=W).save(f"{OUT}/contact-sheet.png")
json.dump(meas, open(f"{OUT}/measurements.json", "w"), indent=1)
print(f"{OUT}/contact-sheet.png")
