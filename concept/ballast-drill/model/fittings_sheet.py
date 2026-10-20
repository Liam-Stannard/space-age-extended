#!/usr/bin/env python3
"""Review sheets for the drill's fittings (task ballast-drill-ports, T03a): the drill as the
engine would draw it in each direction with its fittings layers, beside vanilla's big mining
drill drawn the same way.

  python3 fittings_sheet.py <signed-off sheets> <fittings sheets> <out.png> [--before <ports dir>]
                            [--blind <fittings sheets>]

Per direction, at 1x (64 px a tile, the sheets' own scale), on preview.py's ground:
  ours, unpiped    shadows (plate's, fittings', covers') at half strength; the plate; fittings
                   behind; chute and stroke frame 0; fittings front; vanilla's pipe cover at
                   each of the direction's four connections
  ours, piped      the same with vanilla's straight pipe on each connection's outside tile in
                   place of its cover
  ours, working    unpiped, frame 7 of the chute, stroke, ore and dust (seated, the dust out),
                   the ore and dust between the fittings behind and front
  behind / front / shadow   the three fittings layers alone
  vanilla          big mining drill: still-shadow, still, pipe-connections, still-front,
                   pipe-connections-front and -shadow, unpiped with covers (its drill head,
                   support and top, the moving parts, left out), and its three layers alone
With --before, a first column: the signed-off drill as it ships (its pipe pictures, one per
face, stamped at every connection, covers at all: T01's reading). With --blind, a column of
the blind-capped variant, unpiped.
A cover or pipe on a tile south of the centre is drawn over the building, otherwise under it
(measure.py's rule for the joins). Shadows are emulated, not a client's.
"""
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

FD = os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data")
BMD = os.path.join(FD, "space-age/graphics/entity/big-mining-drill")
GROUND = (74, 66, 58)
PPT = 64
CELL = 480
HEAD = 22
DIRS = ("north", "east", "south", "west")
FACE = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
FACE_NAME = {"N": "north", "E": "east", "S": "south", "W": "west"}
CONNS = [(-2, -1, "W"), (2, -1, "E"), (1, 2, "S"), (-1, 2, "S")]     # big-mining-drill.lua:570-580


def conns(d):
    out = []
    for x, y, f in CONNS:
        for _ in range(DIRS.index(d)):
            x, y, f = -y, x, "NESW"[("NESW".index(f) + 1) % 4]
        out.append((x, y, f))
    return out


def font(size=15):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


class Sheets:
    def __init__(self, d):
        self.dir = d
        self.meta = json.load(open(os.path.join(d, "meta.json")))

    def frame0(self, stem, f=0):
        m = self.meta[stem]
        im = Image.open(os.path.join(self.dir, stem + ".png")).convert("RGBA")
        w, h = m["size"]
        f %= m.get("frames", 1)
        line = m.get("line_length", 1)
        x, y = (f % line) * w, (f // line) * h
        return im.crop((x, y, x + w, y + h)), m["shift"]


def place(canvas, im, shift, at=(0, 0)):
    x = round(CELL / 2 + (at[0] + shift[0]) * PPT - im.width / 2)
    y = round(CELL / 2 + (at[1] + shift[1]) * PPT - im.height / 2)
    canvas.alpha_composite(im, (x, y))


def shadow_union(parts):
    """Shadows as the engine draws them: one shadow, not stacked (the most alpha wins)."""
    acc = Image.new("L", (CELL, CELL), 0)
    for im, shift, at in parts:
        c = Image.new("RGBA", (CELL, CELL))
        place(c, im, shift, at)
        from PIL import ImageChops
        acc = ImageChops.lighter(acc, c.getchannel("A"))
    sh = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    sh.putalpha(acc.point(lambda v: v // 2))
    return sh


def vanilla_pipe(face, cover):
    if cover:
        n = FACE_NAME[face]
        base = os.path.join(FD, "base/graphics/entity/pipe-covers/pipe-cover-" + n)
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


def ours(sig, d, fit=None, cover=True, ports=None, working=None):
    c = Image.new("RGBA", (CELL, CELL), GROUND + (255,))
    pieces = outside(conns(d), cover)
    shadows = [sig.frame0(f"base-shadow-{d}") + ((0, 0),)]
    if fit:
        shadows.append(fit.frame0(f"fittings-shadow-{d}") + ((0, 0),))
    shadows += [(sh, (0, 0), at) for _, sh, at, _ in pieces if sh is not None]
    c.alpha_composite(shadow_union(shadows))
    for im, _, at, over in pieces:
        if not over:
            place(c, im, (0, 0), at)
    place(c, *sig.frame0(f"base-{d}"))
    if fit:
        place(c, *fit.frame0(f"fittings-{d}"))
    f = working or 0
    place(c, *sig.frame0(f"chute-{d}", f))
    place(c, *sig.frame0(f"stroke-{d}", f))
    if working is not None:                  # the working layers, drawn only while mining
        place(c, *sig.frame0(f"ore-{d}", f))
        place(c, *sig.frame0(f"dust-{d}", f))
    if fit:
        place(c, *fit.frame0(f"fittings-front-{d}"))
    if ports:            # as shipped: the face's picture stamped at every connection on that face
        for x, y, f in conns(d):
            dx, dy = FACE[f]
            m = ports.meta[f"port-{f}"]
            im = Image.open(os.path.join(ports.dir, f"port-{f}.png")).convert("RGBA")
            place(c, im, m["shift"], (x + dx, y + dy))
    for im, _, at, over in pieces:
        if over:
            place(c, im, (0, 0), at)
    return c


def alone(sheets, stem, shadow=False):
    c = Image.new("RGBA", (CELL, CELL), GROUND + (255,))
    im, shift = sheets.frame0(stem)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sh.putalpha(im.getchannel("A"))
        im = sh
    place(c, im, shift)
    return c


def bmd(name, d):
    L = d[0].upper()
    stem = os.path.join(BMD, d.capitalize(), f"big-mining-drill-{L}-{name}")
    txt = open(stem + ".lua").read()
    import re
    w = int(re.search(r"width\s*=\s*(\d+)", txt).group(1))
    h = int(re.search(r"height\s*=\s*(\d+)", txt).group(1))
    sx, sy = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", txt).groups())
    im = Image.open(stem + ".png").convert("RGBA").crop((0, 0, w, h))
    return im, (sx / 32, sy / 32)


def vanilla(d):
    c = Image.new("RGBA", (CELL, CELL), GROUND + (255,))
    pieces = outside(conns(d), True)
    shadows = [bmd("still-shadow", d) + ((0, 0),), bmd("pipe-connections-shadow", d) + ((0, 0),)]
    shadows += [(sh, (0, 0), at) for _, sh, at, _ in pieces]
    c.alpha_composite(shadow_union(shadows))
    for im, _, at, over in pieces:
        if not over:
            place(c, im, (0, 0), at)
    for n in ("still", "pipe-connections", "still-front", "pipe-connections-front"):
        place(c, *bmd(n, d))
    for im, _, at, over in pieces:
        if over:
            place(c, im, (0, 0), at)
    return c


def vanilla_alone(d, n, shadow=False):
    c = Image.new("RGBA", (CELL, CELL), GROUND + (255,))
    im, shift = bmd(n, d)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sh.putalpha(im.getchannel("A"))
        im = sh
    place(c, im, shift)
    return c


def grid(c):
    """The footprint's outline, faint."""
    dr = ImageDraw.Draw(c, "RGBA")
    e0, e1 = CELL / 2 - 2.5 * PPT, CELL / 2 + 2.5 * PPT
    dr.rectangle([e0, e0, e1, e1], outline=(255, 255, 255, 40))
    return c


def main():
    a = sys.argv[1:]
    sig, fit, out = Sheets(a[0]), Sheets(a[1]), a[2]
    before = Sheets(a[a.index("--before") + 1]) if "--before" in a else None
    blind = Sheets(a[a.index("--blind") + 1]) if "--blind" in a else None
    cols = []
    if before:
        cols.append(("as shipped: face pictures, covers", lambda d: ours(sig, d, None, True, before)))
    cols += [("ours: fittings, vanilla covers", lambda d: ours(sig, d, fit, True)),
             ("ours: fittings, piped", lambda d: ours(sig, d, fit, False)),
             ("ours: working, frame 7 (landed)", lambda d: ours(sig, d, fit, True, working=7))]
    if blind:
        cols.append(("ours, blind-capped: covers", lambda d: ours(sig, d, blind, True)))
    cols += [("ours: fittings behind", lambda d: alone(fit, f"fittings-{d}")),
             ("ours: fittings front", lambda d: alone(fit, f"fittings-front-{d}")),
             ("ours: fittings shadow", lambda d: alone(fit, f"fittings-shadow-{d}", True)),
             ("vanilla big drill: covers", vanilla),
             ("vanilla: pipe-connections", lambda d: vanilla_alone(d, "pipe-connections")),
             ("vanilla: -front", lambda d: vanilla_alone(d, "pipe-connections-front")),
             ("vanilla: -shadow", lambda d: vanilla_alone(d, "pipe-connections-shadow", True))]
    W, H = len(cols) * CELL, 34 + len(DIRS) * (CELL + HEAD)
    sheet = Image.new("RGB", (W, H), (32, 32, 34))
    dr = ImageDraw.Draw(sheet)
    dr.text((8, 8), "Ballast drill fittings per direction (T03a), 1x, beside vanilla's big mining drill; "
                    "connections as big-mining-drill.lua:570-580, turned", fill=(240, 240, 240), font=font(17))
    for r, d in enumerate(DIRS):
        y = 34 + r * (CELL + HEAD)
        for k, (label, fn) in enumerate(cols):
            dr.text((k * CELL + 6, y + 3), f"{d}: {label}", fill=(240, 200, 90), font=font(14))
            sheet.paste(grid(fn(d)).convert("RGB"), (k * CELL, y + HEAD))
    assert max(sheet.size) < 8000, sheet.size
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
