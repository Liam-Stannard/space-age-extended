#!/usr/bin/env python3
"""Radiant Generator options round: one sheet per option, and the contact sheet.

  python3 options_sheets.py <hi-root> <out-dir>

<hi-root> holds hi-A ... hi-E, each written by options_blockout.py (4x renders on
a 448 px sprite canvas, entity origin at (224, 256)). Writes into <out-dir>:

  <X>-<slug>.png        the option: hero at 2x, idle and working at 1x, the
                        silhouette, and a block of generators packed edge to edge
  contact-sheet.png     every option at game scale (64 px a tile, as the engine
                        draws a scale-0.5 sprite) on one ground with the tile grid,
                        beside vanilla's steam engine (3x5, both plates) and nuclear
                        reactor (5x5), the Reaction Plant's plate and the Radiant
                        Generator's current in-game plates (the v2 trough)
  contact-sheet-2x.png  the same, nearest-neighbour doubled, to read at

Vanilla sprites are read from the local install ($FACTORIO_DATA), frame 0, at the
shifts their prototypes give, with no shadow -- the precedent of
concept/crust-tap/model/compare_vanilla.py. Shadows are left off every building on
the contact sheet so they compare as plates; the option sheets carry them.
"""
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

HI, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
FD = os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/debian-installation/steamapps/common/Factorio/data"))

PPT = 64
GROUND = (74, 66, 58, 255)
BG = (30, 30, 30, 255)
GRID = (255, 255, 255, 34)
FOOT = (255, 255, 255, 110)
TEXT = (225, 220, 210, 255)
SUB = (165, 160, 150, 255)
CANVAS, ORIGIN = 448, (224, 256)


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)


OPTIONS = [
    ("A", "the-trough", "A  THE TROUGH (v2 refined)", "3x5, two plates", "vertical", "horizontal"),
    ("B", "the-banded-cask", "B  THE BANDED CASK", "3x3, one plate", "one"),
    ("C", "the-radiator-cross", "C  THE RADIATOR CROSS", "4x4, one plate", "one"),
    ("D", "the-twin-cask", "D  THE TWIN CASK", "3x4, two plates", "vertical", "horizontal"),
    ("E", "the-plug-well", "E  THE PLUG WELL", "4x4, one plate", "one"),
]
FOOTPRINT = {"A": (3, 5), "B": (3, 3), "C": (4, 4), "D": (3, 4), "E": (4, 4)}


def down(path, k):
    """4x render -> 4/k x, in premultiplied alpha (as tools/blender/downsample.py)."""
    im = Image.open(path).convert("RGBa")
    return im.resize((im.width * k // 4, im.height * k // 4), Image.LANCZOS).convert("RGBA")


def load(opt, d, k=1):
    base = f"{HI}/hi-{opt}/{d}"
    return {p: down(f"{base}-{p}.png", k) for p in ("working", "idle", "shadow")}


def fp(opt, d):
    w, h = FOOTPRINT[opt]
    return (h, w) if d == "horizontal" else (w, h)


def ground(w_tiles, h_tiles, origin_tiles, foot, ppt=PPT):
    """A ground panel with the tile grid, the footprint brighter; origin in tiles from top-left."""
    W, H = int(w_tiles * ppt), int(h_tiles * ppt)
    g = Image.new("RGBA", (W, H), GROUND)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    ox, oy = origin_tiles[0] * ppt, origin_tiles[1] * ppt
    fx, fy = foot
    # grid lines on tile boundaries aligned with the footprint
    x0 = ox - fx / 2 * ppt
    y0 = oy - fy / 2 * ppt
    x = x0 % ppt
    while x < W:
        dr.line([(x, 0), (x, H)], fill=GRID)
        x += ppt
    y = y0 % ppt
    while y < H:
        dr.line([(0, y), (W, y)], fill=GRID)
        y += ppt
    if fx:
        dr.rectangle([x0, y0, x0 + fx * ppt, y0 + fy * ppt], outline=FOOT)
    g.alpha_composite(ov)
    return g


def put(dst, im, origin_px, shift=(0, 0), ppt=PPT, centre=None):
    """Paste a sprite with its own centre (or `centre`, for our canvases) at origin + shift."""
    cx, cy = centre if centre else (im.width / 2, im.height / 2)
    x = round(origin_px[0] + shift[0] * ppt - cx)
    y = round(origin_px[1] + shift[1] * ppt - cy)
    dst.alpha_composite(im, (x, y)) if x >= 0 and y >= 0 else _paste_clip(dst, im, x, y)


def _paste_clip(dst, im, x, y):
    cx, cy = max(0, -x), max(0, -y)
    dst.alpha_composite(im.crop((cx, cy, im.width, im.height)), (x + cx, y + cy))


def shadow50(im):
    r, g, b, a = im.split()
    return Image.merge("RGBA", (r, g, b, a.point(lambda v: v // 2)))


def additive(base, glow):
    """Base with an additive glow layer over it (straight-alpha glow, premultiplied in)."""
    g = glow.convert("RGBa")
    r, gg, b, _ = g.split()
    add = Image.merge("RGB", (r, gg, b))
    out = base.copy()
    rgb = ImageChops.add(out.convert("RGB"), add)
    out = Image.merge("RGBA", (*rgb.split(), out.split()[3]))
    return out


def label(img, xy, text, size=13, fill=TEXT, bold=False):
    ImageDraw.Draw(img).text(xy, text, font=font(size, bold), fill=fill)


def silhouette(im):
    a = im.split()[3].point(lambda v: 255 if v > 40 else 0)
    s = Image.new("RGBA", im.size, (150, 150, 150, 255))
    s.paste((0, 0, 0, 255), mask=a)
    return s


def panel_for(opt, d, layers, ppt=PPT, extra=(2, 3)):
    """One building alone on a ground just big enough for it."""
    fw, fh = fp(opt, d)
    w, h = fw + extra[0], fh + extra[1]
    origin = (w / 2, h - fh / 2 - 1)
    g = ground(w, h, origin, (fw, fh), ppt)
    o = (origin[0] * ppt, origin[1] * ppt)
    k = ppt / PPT
    for im in layers:
        put(g, im, o, ppt=ppt, centre=(ORIGIN[0] * k, ORIGIN[1] * k))
    return g


def block(opt, d, cols, rows):
    """cols x rows generators packed edge to edge, drawn north to south as the engine sorts them."""
    fw, fh = fp(opt, d)
    r = load(opt, d)
    w, h = cols * fw + 2, rows * fh + 3
    g = ground(w, h, (1 + fw / 2, 2 + fh / 2), (0, 0))
    ov = ImageDraw.Draw(g)
    ov.rectangle([PPT, 2 * PPT, (1 + cols * fw) * PPT, (2 + rows * fh) * PPT], outline=FOOT)
    for j in range(rows):
        for i in range(cols):
            o = ((1 + fw / 2 + i * fw) * PPT, (2 + fh / 2 + j * fh) * PPT)
            put(g, shadow50(r["shadow"]), o, centre=ORIGIN)
    for j in range(rows):
        for i in range(cols):
            o = ((1 + fw / 2 + i * fw) * PPT, (2 + fh / 2 + j * fh) * PPT)
            put(g, r["working"], o, centre=ORIGIN)
    return g


def stack_h(panels, gap=10, bg=BG, labels=None, top=22):
    W = sum(p.width for p in panels) + gap * (len(panels) + 1)
    H = max(p.height for p in panels) + top + gap
    out = Image.new("RGBA", (W, H), bg)
    x = gap
    for i, p in enumerate(panels):
        out.alpha_composite(p, (x, top))
        if labels:
            label(out, (x + 2, 4), labels[i], 12, SUB)
        x += p.width + gap
    return out


def stack_v(rows, gap=10, bg=BG):
    W = max(r.width for r in rows)
    H = sum(r.height for r in rows) + gap * (len(rows) - 1)
    out = Image.new("RGBA", (W, H), bg)
    y = 0
    for r in rows:
        out.alpha_composite(r, (0, y))
        y += r.height + gap
    return out


# ------------------------------------------------------------ option sheets

for opt, slug, title, foot, *dirs in OPTIONS:
    heroes, small, labels_h, labels_s = [], [], [], []
    for d in dirs:
        r2 = load(opt, d, 2)
        heroes.append(panel_for(opt, d, [shadow50(r2["shadow"]), r2["working"]], ppt=2 * PPT))
        labels_h.append(f"{d if d != 'one' else 'hero'} -- working, 2x")
        r1 = load(opt, d)
        small.append(panel_for(opt, d, [shadow50(r1["shadow"]), r1["idle"]]))
        small.append(panel_for(opt, d, [shadow50(r1["shadow"]), r1["working"]]))
        labels_s += [f"{d} idle, 1x" if d != "one" else "idle, 1x",
                     f"{d} working, 1x" if d != "one" else "working, 1x"]
        sil = silhouette(load(opt, d)["working"])
        fw, fh = fp(opt, d)
        crop = sil.crop((ORIGIN[0] - (fw / 2 + 1) * PPT, ORIGIN[1] - (fh / 2 + 2) * PPT,
                         ORIGIN[0] + (fw / 2 + 1) * PPT, ORIGIN[1] + (fh / 2 + 1) * PPT))
        small.append(crop)
        labels_s.append("silhouette")
    fw, fh = fp(opt, dirs[0])
    cols, rows = (4, 2) if fw <= 3 else (3, 2)
    blk = block(opt, dirs[0], cols, rows)
    row1 = stack_h(heroes, labels=labels_h)
    row2 = stack_h(small + [blk], labels=labels_s + [f"a block of {cols * rows}, edge to edge, 1x"])
    head = Image.new("RGBA", (max(row1.width, row2.width), 56), BG)
    label(head, (10, 6), f"RADIANT GENERATOR -- OPTION {title}", 22, bold=True)
    label(head, (10, 34), f"{foot}.  Blender blockout: flat palette, no finish. 64 px a tile at 1x.", 13, SUB)
    sheet = stack_v([head, row1, row2])
    sheet.save(f"{OUT}/{opt}-{slug}.png")
    print(f"{OUT}/{opt}-{slug}.png", sheet.size)

# ------------------------------------------------------------ contact sheet


def vanilla(rel, w, h):
    return Image.open(os.path.join(FD, rel)).convert("RGBA").crop((0, 0, w, h))


def ours(rel):
    return Image.open(os.path.join(REPO, rel)).convert("RGBA")


def sprite_panel(layers, foot, h_tiles=8, w_extra=2):
    """layers: (image, shift in tiles) pasted centred on the entity origin."""
    fw, fh = foot
    w = fw + w_extra
    origin = (w / 2, h_tiles - fh / 2 - 1)
    g = ground(w, h_tiles, origin, foot)
    o = (origin[0] * PPT, origin[1] * PPT)
    for im, shift, *c in layers:
        put(g, im, o, shift, centre=c[0] if c else None)
    return g


rg_v = additive(ours("graphics/entity/radiant-generator/base-vertical.png"),
                ours("graphics/entity/radiant-generator/glow-vertical.png"))
rg_h = additive(ours("graphics/entity/radiant-generator/base-horizontal.png"),
                ours("graphics/entity/radiant-generator/glow-horizontal.png"))
refs = [
    ("vanilla steam engine, 3x5", sprite_panel(
        [(vanilla("base/graphics/entity/steam-engine/steam-engine-V.png", 225, 391), (4.75 / 32, -6.25 / 32))],
        (3, 5))),
    ("(horizontal)", sprite_panel(
        [(vanilla("base/graphics/entity/steam-engine/steam-engine-H.png", 352, 257), (1 / 32, -4.75 / 32))],
        (5, 3))),
    ("vanilla nuclear reactor, 5x5", sprite_panel(
        [(vanilla("base/graphics/entity/nuclear-reactor/reactor.png", 302, 318), (-5 / 32, -7 / 32))],
        (5, 5))),
    ("Reaction Plant, 3x3", sprite_panel(
        [(ours("graphics/entity/reaction-plant/base.png"), (0, -0.14062)),
         (ours("graphics/entity/reaction-plant/coupling.png").crop((0, 0, 46, 37)), (0.10938, -0.78906))],
        (3, 3))),
    ("Radiant Generator now (v2), 3x5", sprite_panel([(rg_v, (0, 0))], (3, 5))),
    ("(horizontal)", sprite_panel([(rg_h, (0, 0))], (5, 3))),
]
opts = []
for opt, slug, title, foot, *dirs in OPTIONS:
    for i, d in enumerate(dirs):
        name = title.split("(")[0].strip().title().replace("  ", " -- ", 1)
        name = f"{opt} {title[3:].split('(')[0].strip().lower()}, {'x'.join(map(str, FOOTPRINT[opt]))}"
        opts.append((name if i == 0 else "(horizontal)",
                     sprite_panel([(load(opt, d)["working"], (0, 0), ORIGIN)], fp(opt, d))))

row_r = stack_h([p for _, p in refs], labels=[n for n, _ in refs])
row_o = stack_h([p for _, p in opts], labels=[n for n, _ in opts])
W = max(row_r.width, row_o.width)
head = Image.new("RGBA", (W, 50), BG)
label(head, (10, 6), "RADIANT GENERATOR -- OPTIONS ROUND, AT GAME SCALE", 20, bold=True)
label(head, (10, 32), "64 px a tile. Top: references (vanilla frame 0, no shadows). "
      "Bottom: the five options, working, no shadows. Blender blockouts.", 12, SUB)
mid = Image.new("RGBA", (W, 4), BG)
contact = stack_v([head, row_r, mid, row_o])
contact.save(f"{OUT}/contact-sheet.png")
contact.resize((contact.width * 2, contact.height * 2), Image.NEAREST).save(f"{OUT}/contact-sheet-2x.png")
print(f"{OUT}/contact-sheet.png", contact.size)
