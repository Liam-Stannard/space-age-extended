#!/usr/bin/env python3
"""Composite plate + port fittings + vanilla neighbour pipes as the engine layers them."""
import json
import os
import sys
from PIL import Image

S, P, OUTP = sys.argv[1], sys.argv[2], sys.argv[3]
FD = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/pipe")
pm = json.load(open(f"{P}/meta.json"))
bm = json.load(open(f"{S}/meta.json"))
T = 64
W, H = 7 * T, 7 * T
CX, CY = W / 2, H / 2                       # entity centre
DIRV = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


def put(canvas, im, cx, cy):
    canvas.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))


def scene(ports, connected):
    """ports: list of (tile_x, tile_y, dir); connected: set of indices with a pipe attached."""
    im = Image.new("RGBA", (W, H), (58, 52, 46, 255))
    base = Image.open(f"{S}/base.png").convert("RGBA")
    shadow = Image.open(f"{S}/shadow.png").convert("RGBA")
    sh = Image.merge("RGBA", (*shadow.split()[:3], shadow.getchannel("A").point(lambda v: v // 2)))
    put(im, sh, CX + bm["shadow"]["shift"][0] * T, CY + bm["shadow"]["shift"][1] * T)
    # vanilla pipes in the outside tiles of connected ports
    for i, (tx, ty, d) in enumerate(ports):
        if i in connected:
            ox, oy = tx + DIRV[d][0], ty + DIRV[d][1]
            name = "pipe-straight-vertical" if d in "NS" else "pipe-straight-horizontal"
            put(im, Image.open(f"{FD}/{name}.png").convert("RGBA"), CX + ox * T, CY + oy * T)

    def fitting(i, tx, ty, d):
        ox, oy = tx + DIRV[d][0], ty + DIRV[d][1]
        for kind in ("port",) + (() if i in connected else ("cover",)):
            m = pm[f"{kind}-{d}"]
            put(im, Image.open(f"{P}/{kind}-{d}.png").convert("RGBA"),
                CX + (ox + m["shift"][0]) * T, CY + (oy + m["shift"][1]) * T)
    for i, (tx, ty, d) in enumerate(ports):       # north: behind the machine
        if d == "N":
            fitting(i, tx, ty, d)
    put(im, base, CX + bm["base"]["shift"][0] * T, CY + bm["base"]["shift"][1] * T)
    for i, (tx, ty, d) in enumerate(ports):
        if d != "N":
            fitting(i, tx, ty, d)
    return im


north = [(-1, -1, "N"), (1, -1, "N"), (0, 1, "S")]
east = [(1, -1, "E"), (1, 1, "E"), (-1, 0, "W")]
a = scene(north, {0})             # one input piped, one capped, output capped
b = scene(east, {0, 2})           # facing east: one input piped, one capped, output piped
out = Image.new("RGB", (W * 2 + 16, H), (30, 30, 30))
out.paste(a.convert("RGB"), (0, 0))
out.paste(b.convert("RGB"), (W + 16, 0))
out = out.resize((out.width * 2, out.height * 2), Image.NEAREST)
out.save(OUTP)
