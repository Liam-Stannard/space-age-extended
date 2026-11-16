"""Vanilla's big mining drill drawn as the engine layers it, dry (graphics_set) and wet
(wet_mining_graphics_set), for the rig round (task ballast-drill-ports, T03d).

Layer order is the prototype's working_visualisations order (space-age
big-mining-drill.lua:229-546): drill head, still/reel, output, [pipe-connections],
support, still-front, [pipe-connections-front], top. Shadows (still, support,
pipe-connections, covers, top) are one shadow, the most alpha wins, at half strength.
The moving parts (drill, support, top) stand at their first waypoint, frame 0.
Covers and pipes: vanilla's, at the tile outside each connection; a tile south of the
centre is drawn over the building, otherwise under it (measure.py's rule).

All at the sheets' own scale: 64 px a tile (scale 0.5 sprites).
"""
import os
import re
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
FD = subprocess.run([sys.executable, os.path.join(REPO, "tools", "paths.py"), "factorio-data"],
                    capture_output=True, text=True, check=True).stdout.strip()
BMD = os.path.join(FD, "space-age/graphics/entity/big-mining-drill")
GROUND = (74, 66, 58)
PPT = 64
DIRS = ("north", "east", "south", "west")
FACE = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
FACE_NAME = {"N": "north", "E": "east", "S": "south", "W": "west"}
CONNS = [(-2, -1, "W"), (2, -1, "E"), (1, 2, "S"), (-1, 2, "S")]     # big-mining-drill.lua:570-580
POS = {"north": (0, 0.15), "east": (0, 0), "south": (0, 0.15), "west": (0, 0)}
WAY0 = {"north": (0, -0.3), "east": (-0.85, 0), "south": (0, -0.9), "west": (-0.2, 0)}


def conns(d):
    out = []
    for x, y, f in CONNS:
        for _ in range(DIRS.index(d)):
            x, y, f = -y, x, "NESW"[("NESW".index(f) + 1) % 4]
        out.append((x, y, f))
    return out


def font(size=15):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not os.path.isfile(p):
        for c in ("/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf"):
            if os.path.isfile(c):
                p = c
    return ImageFont.truetype(p, size) if os.path.isfile(p) else ImageFont.load_default()


def sprite(path_stem, frame=0):
    """A vanilla sprite's frame and its shift in tiles, from its .lua beside it."""
    txt = open(path_stem + ".lua").read()
    w = int(re.search(r"width\s*=\s*(\d+)", txt).group(1))
    h = int(re.search(r"height\s*=\s*(\d+)", txt).group(1))
    m = re.search(r"line_length\s*=\s*(\d+)", txt)
    line = int(m.group(1)) if m else 1
    sx, sy = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", txt).groups())
    im = Image.open(path_stem + ".png").convert("RGBA")
    x, y = (frame % line) * w, (frame // line) * h
    return im.crop((x, y, x + w, y + h)), (sx / 32, sy / 32)


def bmd(name, d=None):
    if d is None:
        return sprite(os.path.join(BMD, f"big-mining-drill-{name}"))
    return sprite(os.path.join(BMD, d.capitalize(), f"big-mining-drill-{d[0].upper()}-{name}"))


def place(canvas, im, shift, at=(0, 0)):
    cx, cy = canvas.width / 2, canvas.height / 2
    x = round(cx + (at[0] + shift[0]) * PPT - im.width / 2)
    y = round(cy + (at[1] + shift[1]) * PPT - im.height / 2)
    canvas.alpha_composite(im, (x, y))


def shadow_union(size, parts):
    acc = Image.new("L", size, 0)
    for im, shift, at in parts:
        c = Image.new("RGBA", size)
        place(c, im, shift, at)
        acc = ImageChops.lighter(acc, c.getchannel("A"))
    sh = Image.new("RGBA", size, (0, 0, 0, 0))
    sh.putalpha(acc.point(lambda v: v // 2))
    return sh


def vanilla_pipe(face, cover):
    if cover:
        base = os.path.join(FD, "base/graphics/entity/pipe-covers/pipe-cover-" + FACE_NAME[face])
        return Image.open(base + ".png").convert("RGBA"), Image.open(base + "-shadow.png").convert("RGBA")
    p = os.path.join(FD, "base/graphics/entity/pipe/pipe-straight-" + ("vertical" if face in "NS" else "horizontal")
                     + ".png")
    return Image.open(p).convert("RGBA"), None


def outside(cs, cover):
    """Each connection's cover or pipe: (image, its shadow or None, tile, drawn over)."""
    out = []
    for x, y, f in cs:
        dx, dy = FACE[f]
        im, sh = vanilla_pipe(f, cover)
        out.append((im, sh, (x + dx, y + dy), y + dy > 0))
    return out


def vanilla(d, wet=True, cover=True, size=(480, 480), moving=True):
    """The big drill in direction d, dry or wet, unpiped (covers) or piped."""
    c = Image.new("RGBA", size, GROUND + (255,))
    pieces = outside(conns(d), cover) if wet else []
    w0 = WAY0[d]
    mv = (POS[d][0] + w0[0], POS[d][1] + w0[1])
    shadows = [bmd("still-shadow", d) + ((0, 0),)]
    if moving:
        shadows += [bmd("support-shadow", d) + (w0,), bmd("top-shadow", d) + (w0,), bmd("drill-shadow") + (mv,)]
    if wet:
        shadows.append(bmd("pipe-connections-shadow", d) + ((0, 0),))
        shadows += [(sh, (0, 0), at) for _, sh, at, _ in pieces if sh is not None]
    c.alpha_composite(shadow_union(size, shadows))
    for im, _, at, over in pieces:
        if not over:
            place(c, im, (0, 0), at)
    if moving:
        place(c, *bmd("drill"), mv)
    place(c, *bmd("still", d))
    place(c, *bmd("output", d))
    if wet:
        place(c, *bmd("pipe-connections", d))
    if moving:
        place(c, *bmd("support", d), w0)
    place(c, *bmd("still-front", d))
    if wet:
        place(c, *bmd("pipe-connections-front", d))
    if moving:
        place(c, *bmd("top", d), w0)
    for im, _, at, over in pieces:
        if over:
            place(c, im, (0, 0), at)
    return c


def alone(d, name, size=(480, 480), shadow=False, ghost=None):
    """One layer alone on the ground; ghost: the dry drill faint under it, for place."""
    c = Image.new("RGBA", size, GROUND + (255,))
    if ghost is not None:
        g = ghost.copy()
        g.putalpha(70)
        c.alpha_composite(g)
    im, shift = bmd(name, d)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sh.putalpha(im.getchannel("A").point(lambda a: a // 2))
        im = sh
    place(c, im, shift)
    return c


def grid(c, tiles=5, conns_=None, colour=(255, 255, 255, 50)):
    """The footprint's outline, faint; with conns_, each connection's tile ringed."""
    dr = ImageDraw.Draw(c, "RGBA")
    cx, cy = c.width / 2, c.height / 2
    h = tiles / 2 * PPT
    dr.rectangle([cx - h, cy - h, cx + h, cy + h], outline=colour)
    for x, y, f in conns_ or ():
        dr.rectangle([cx + (x - 0.5) * PPT, cy + (y - 0.5) * PPT, cx + (x + 0.5) * PPT, cy + (y + 0.5) * PPT],
                     outline=(90, 200, 255, 160))
    return c
