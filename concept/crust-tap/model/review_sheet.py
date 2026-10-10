#!/usr/bin/env python3
"""The Crust Tap's review sheet.

  python3 review_sheet.py <out-dir> <review.png> [<glass-tints.png> [<working-tints-2x.png>]]

  <out-dir>  render.sh's output directory: <out-dir>/sheets (base-<d>, base-shadow-<d>,
             icon.png, meta.json) and <out-dir>/renders

Everything is layered as the engine draws it, on one ground at 64 px a tile with the tile
grid and the 2x2 footprint outlined: the cast shadow at 50 %, then the plate, with a
vanilla straight pipe (base/graphics/entity/pipe) in the tile spec 24's connection points
into, drawn under the plate when it lies north of the tap's centre and over it when it lies
south, as the engine orders them. The adopted plates are the wired round 13, graphics/entity/gas-pump/,
at the shifts prototypes/core/crust-tap.lua gives them, with their own shadows and the
same vanilla pipe on the same tile.

The plate is the whole tap in every state (the task's 2026-10-02 amendment: no frost, no
heat seam), so each panel is the tap idle and working at once.

One row per direction: the adopted plate with its pipe; the new plate idle with its pipe;
the new plate working (its sight glass lit, tinted siderane) with its pipe; the new plate's
joint at 4x. Then the four new plates at 2x, and the icon strip at 1x and its 64 px icon at
4x. Each plate is drawn with the moving parts' frame 0 over it, the stopped machine; the
glass's frame 0 where it is working. The animations' frames are animation_review.py's.

The working-tints sheet: each direction's shadow, plate and tinted sight glass composited
at their meta.json shifts, at 2x, one row tinted siderane and one helium-3.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
ADOPTED = os.path.join(REPO, "graphics", "entity", "gas-pump")      # the signed-off round 13, as wired
FD = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/pipe")
PPT, TILES = 64, 5
SIZE = PPT * TILES
O = SIZE / 2
GROUND = (74, 66, 58, 255)
BG = (30, 30, 30, 255)
DIRS = ("north", "east", "south", "west")
# spec 24: the connection tile (tiles, y down) and the face it leaves by
CONN = {"north": ((0.5, -0.5), (0, -1)), "east": ((0.5, 0.5), (1, 0)), "south": ((-0.5, 0.5), (0, 1)),
        "west": ((-0.5, -0.5), (-1, 0))}
# prototypes/core/crust-tap.lua: the wired round 13 plates' shifts and their shadows' (each copied
# there from round 13's meta.json)
ADOPTED_SHIFT = {"north": ((0.0, -0.15625), (0.21094, -0.03125)), "east": ((0.00781, -0.04688), (0.21094, -0.00781)),
                 "south": ((0.0, -0.03906), (0.21094, 0.03906)), "west": ((-0.00781, -0.04688), (0.21094, -0.00781))}


def grid(c):
    d = ImageDraw.Draw(c, "RGBA")
    for i in range(TILES + 1):
        v = round(O + (i - TILES / 2) * PPT)
        d.line([(v, 0), (v, SIZE)], fill=(255, 255, 255, 40))
        d.line([(0, v), (SIZE, v)], fill=(255, 255, 255, 40))
    d.rectangle([O - PPT, O - PPT, O + PPT, O + PPT], outline=(255, 255, 255, 110))


def put(c, im, sx, sy, shadow=False):
    if shadow:
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        lay.paste(Image.new("RGBA", im.size, (0, 0, 0, 255)), (0, 0), im.getchannel("A").point(lambda v: v // 2))
        im = lay
    c.alpha_composite(im, (round(O + sx * PPT - im.width / 2), round(O + sy * PPT - im.height / 2)))


def pipe_sprite(d):
    (tx, ty), (dx, dy) = CONN[d]
    name = "pipe-straight-vertical" if dx == 0 else "pipe-straight-horizontal"
    return Image.open(os.path.join(FD, name + ".png")).convert("RGBA"), tx + dx, ty + dy


def panel(plate, pshift, shadow, sshift, d, with_pipe=True):
    c = Image.new("RGBA", (SIZE, SIZE), GROUND)
    put(c, shadow, *sshift, shadow=True)
    sp, px, py = pipe_sprite(d)
    if with_pipe and py < 0:
        put(c, sp, px, py)                   # north of the tap's centre: drawn first
    put(c, plate, *pshift)
    if with_pipe and py >= 0:
        put(c, sp, px, py)
    grid(c)
    return c


def adopted(d):
    base = Image.open(os.path.join(ADOPTED, f"base-{d}.png")).convert("RGBA")
    sh = Image.open(os.path.join(ADOPTED, f"base-shadow-{d}.png")).convert("RGBA")
    bs, ss = ADOPTED_SHIFT[d]
    return panel(base, bs, sh, ss, d)


def new(meta, sheets, d, with_pipe=True, tint=None):
    """The new plate on the ground with its shadow (and the vanilla pipe); with `tint`, the
    sight glass's light layer over it, tinted, as it draws while the pump works."""
    base = Image.open(os.path.join(sheets, f"base-{d}.png")).convert("RGBA").copy()
    sh = Image.open(os.path.join(sheets, f"base-shadow-{d}.png")).convert("RGBA")
    # (the gas-pump-animation task) the stopped machine: the moving parts' frame 0 over the plate
    pump, bs, ps = frame_of(sheets, meta, f"pump-{d}", 0), meta[f"base-{d}"]["shift"], meta[f"pump-{d}"]["shift"]
    base.alpha_composite(pump, (round(base.width / 2 + (ps[0] - bs[0]) * PPT - pump.width / 2),
                                round(base.height / 2 + (ps[1] - bs[1]) * PPT - pump.height / 2)))
    if tint is not None:
        light = tinted(frame_of(sheets, meta, f"sight-glass-{d}", 0), tint)
        bs, ls = meta[f"base-{d}"]["shift"], meta[f"sight-glass-{d}"]["shift"]
        at = (round(base.width / 2 + (ls[0] - bs[0]) * PPT - light.width / 2),
              round(base.height / 2 + (ls[1] - bs[1]) * PPT - light.height / 2))
        base.alpha_composite(light, at)
    return panel(base, meta[f"base-{d}"]["shift"], sh, meta[f"base-shadow-{d}"]["shift"], d, with_pipe)


def frame_of(sheets, meta, stem, f):
    """Frame f of a packed sheet (a still sheet is its own frame 0)."""
    im = Image.open(os.path.join(sheets, stem + ".png")).convert("RGBA")
    m = meta[stem]
    if "frames" not in m:
        return im
    w, h = m["size"]
    line = m["line_length"]
    return im.crop(((f % line) * w, (f // line) * h, (f % line) * w + w, (f // line) * h + h))


def zoom(im, at, k):
    cx, cy = O + at[0] * PPT, O + at[1] * PPT
    r = SIZE / k / 2
    return im.crop((round(cx - r), round(cy - r), round(cx + r), round(cy + r))).resize((SIZE, SIZE), Image.NEAREST)


def label(im, text, bar=16):
    o = Image.new("RGBA", (im.width, im.height + bar), BG)
    o.alpha_composite(im, (0, bar))
    ImageDraw.Draw(o).text((4, 3), text, fill=(220, 220, 220, 255))
    return o


# preview tints for the sight glass, as each vent's mining_visualisation_tint gives them:
# siderane chartreuse (0.66, 0.85, 0.16), helium-3 (0.55, 0.78, 0.90)
TINTS = (("siderane", tuple(round(255 * c) for c in (0.66, 0.85, 0.16))),
         ("helium-3", tuple(round(255 * c) for c in (0.55, 0.78, 0.90))))


def tinted(light, rgb):
    r, g, b, a = light.split()
    return Image.merge("RGBA", (r.point(lambda v: v * rgb[0] // 255), g.point(lambda v: v * rgb[1] // 255),
                                b.point(lambda v: v * rgb[2] // 255), a))


def glass_strip(out, path):
    """Each direction's plate with its sight glass lit, tinted as each gas: the plate at 1x,
    and the glass at 4x; and the bare white layer."""
    sheets = os.path.join(out, "sheets")
    meta = json.load(open(os.path.join(sheets, "meta.json")))
    rows = []
    for name, rgb in (("white (as rendered)", (255, 255, 255)),) + TINTS:
        row = []
        for d in DIRS:
            c = new(meta, sheets, d, with_pipe=False)
            light = frame_of(sheets, meta, f"sight-glass-{d}", 0)
            put(c, tinted(light, rgb), *meta[f"sight-glass-{d}"]["shift"])
            sx, sy = meta[f"sight-glass-{d}"]["shift"]
            row.append(label(c, f"{d}: {name}"))
            row.append(label(zoom(c, (sx, sy), 4), f"{d}: {name}, glass 4x"))
        rows.append(row)
    gap = 8
    width = max(sum(im.width for im in row) + gap * (len(row) + 1) for row in rows)
    height = sum(max(im.height for im in row) for row in rows) + gap * (len(rows) + 1)
    sheet = Image.new("RGBA", (width, height), BG)
    y = gap
    for row in rows:
        x = gap
        for im in row:
            sheet.alpha_composite(im, (x, y))
            x += im.width + gap
        y += max(im.height for im in row) + gap
    sheet.save(path)
    print(path, sheet.size)


def working_tints(out, path):
    """Each direction's shadow, plate and tinted sight glass at their meta.json shifts, 2x,
    no pipe: a row tinted siderane, a row helium-3."""
    sheets = os.path.join(out, "sheets")
    meta = json.load(open(os.path.join(sheets, "meta.json")))
    rows = []
    for name, rgb in TINTS:
        row = []
        for d in DIRS:
            c = new(meta, sheets, d, with_pipe=False, tint=rgb)
            # x -1.15..1.45, y -1.55..1.25 tiles: the plate, both mouths' reach and the east shadow
            box_ = (round(O - 1.15 * PPT), round(O - 1.55 * PPT), round(O + 1.45 * PPT), round(O + 1.25 * PPT))
            c = c.crop(box_)
            row.append(label(c.resize((c.width * 2, c.height * 2), Image.NEAREST), f"{d}, working, {name}, 2x"))
        rows.append(row)
    gap = 8
    width = sum(im.width for im in rows[0]) + gap * 5
    height = sum(max(im.height for im in row) for row in rows) + gap * 3
    sheet = Image.new("RGBA", (width, height), BG)
    y = gap
    for row in rows:
        x = gap
        for im in row:
            sheet.alpha_composite(im, (x, y))
            x += im.width + gap
        y += max(im.height for im in row) + gap
    sheet.save(path)
    print(path, sheet.size)


def main(out, review, glass=None, working=None):
    sheets = os.path.join(out, "sheets")
    meta = json.load(open(os.path.join(sheets, "meta.json")))
    rows = []
    for d in DIRS:
        (tx, ty), (dx, dy) = CONN[d]
        joint = (tx + dx * 0.5, ty + dy * 0.5)
        withp = new(meta, sheets, d)
        rows.append([label(adopted(d), f"{d}: adopted plate, vanilla pipe on {tx + dx:+.1f},{ty + dy:+.1f}"),
                     label(withp, f"{d}: new plate, idle, same pipe"),
                     label(new(meta, sheets, d, tint=TINTS[0][1]), f"{d}: working (siderane glass), same pipe"),
                     label(zoom(withp, joint, 4), f"{d}: the joint, 4x")])
    # the four new plates at 2x, side by side
    two = []
    for d in DIRS:
        p = new(meta, sheets, d, with_pipe=False)
        two.append(label(zoom(p, (0, 0.05), 2), f"{d}, 2x"))
    rows.append(two)
    icon_path = os.path.join(sheets, "icon.png")
    if os.path.isfile(icon_path):
        icon = Image.open(icon_path).convert("RGBA")
        bg = Image.new("RGBA", icon.size, GROUND)
        bg.alpha_composite(icon)
        holder = Image.new("RGBA", (SIZE, SIZE), BG)
        holder.alpha_composite(bg, (4, 4))
        holder.alpha_composite(bg.crop((0, 0, 64, 64)).resize((256, 256), Image.NEAREST), (4, icon.height + 12))
        rows.append([label(holder, "icon strip (120x64), its 64 px icon at 4x")])

    gap = 8
    width = max(sum(im.width for im in row) + gap * (len(row) + 1) for row in rows)
    height = sum(max(im.height for im in row) for row in rows) + gap * (len(rows) + 1)
    sheet = Image.new("RGBA", (width, height), BG)
    y = gap
    for row in rows:
        x = gap
        for im in row:
            sheet.alpha_composite(im, (x, y))
            x += im.width + gap
        y += max(im.height for im in row) + gap
    sheet.save(review)
    print(review, sheet.size)
    if glass:
        glass_strip(out, glass)
    if working:
        working_tints(out, working)


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4, 5):
        sys.exit("usage: review_sheet.py <out-dir> <review.png> [<glass-tints.png> [<working-tints-2x.png>]]")
    main(*sys.argv[1:])
