#!/usr/bin/env python3
"""T06g: how vanilla takes a pipe into its casing -- each reference's connection at 2x, a vanilla pipe joined to it.

  python3 vanilla_fittings.py <out-dir>

Writes <out-dir>/vanilla-<ref>-<face>.png: a 2.6 x 2.6 tile window round one connection of the chemical plant,
oil refinery, cryogenic plant and foundry (north view), drawn as the engine draws it (shadow, the plate, the
per-face pipework overlay where the prototype has one, a vanilla straight pipe on the tile outside), at 128 px
a tile. form_crops.py puts our fittings beside these. A picture, not a measure.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import measure  # noqa: E402

FD = measure.FD
K = 128                      # px a tile in the crops (2x the engine's 64)
GROUND = (74, 66, 58, 255)
PIPE = os.path.join(FD, "base/graphics/entity/pipe/")
FACE = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
WIN = 2.6                    # the crop's side, tiles

# each reference's connections as it stands facing north (prototype tiles, y down), from the prototypes
REFS = {
    "chemical-plant": dict(label="chemical plant", foot=(3, 3), conns=[(-1, -1, "N"), (1, -1, "N"), (-1, 1, "S")]),
    "oil-refinery": dict(label="oil refinery", foot=(5, 5), conns=[(-1, 2, "S"), (0, -2, "N")]),
    "cryogenic-plant": dict(label="cryogenic plant", foot=(5, 5), conns=[(0, 2, "S"), (0, -2, "N")]),
    "foundry": dict(label="foundry", foot=(5, 5), conns=[(-1, 2, "S"), (1, -2, "N")]),
}


def big(im):
    return im.resize((im.width * 2, im.height * 2), Image.LANCZOS)


def parts(name):
    """[(image at 128 px a tile, shift px at 128)] drawn in order."""
    if name in ("chemical-plant", "oil-refinery"):
        _, _, still, shadow, _ = measure.vanilla(name, "north")
        return [(big(shadow), 0, 0), (big(still), 0, 0)]
    if name == "cryogenic-plant":
        b = "space-age/graphics/entity/cryogenic-plant/cryogenic-plant-"
        rels = ["shadow.png", "main.png", "anim1-base.png", "anim2-base.png", "anim4-base.png", "anim5-base.png",
                "anim6-base.png", "pipe-connections-v.png"]
        out = []
        for r in rels:
            try:
                im, sx, sy = measure.vanilla_sprite(b + r)
            except Exception:
                continue
            out.append((big(im), sx * 2, sy * 2))
        return out
    b = "space-age/graphics/entity/foundry/foundry-"
    out = []
    for r in ("shadow.png", "base.png", "anim-1.png:foundry-anim.lua", "pipe-connections-north.png",
              "pipe-connections-south.png"):
        im, sx, sy = measure.vanilla_sprite(b + r)
        out.append((big(im), sx * 2, sy * 2))
    return out


def scene(name):
    S = 9 * K
    can = Image.new("RGBA", (S, S), GROUND)
    o = S / 2
    ps = parts(name)
    conns = REFS[name]["conns"]
    pipes = []
    for x, y, f in conns:
        dx, dy = FACE[f]
        sp = Image.open(PIPE + ("pipe-straight-vertical.png" if f in "NS" else "pipe-straight-horizontal.png")).convert("RGBA")
        pipes.append((sp, (x + dx) * K, (y + dy) * K, f))
    for sp, px, py, f in pipes:              # a pipe north of the building is behind it
        if f == "N":
            can.alpha_composite(sp, (round(o + px - sp.width / 2), round(o + py - sp.height / 2)))
    for im, sx, sy in ps:
        can.alpha_composite(im, (round(o + sx - im.width / 2), round(o + sy - im.height / 2)))
    for sp, px, py, f in pipes:
        if f != "N":
            can.alpha_composite(sp, (round(o + px - sp.width / 2), round(o + py - sp.height / 2)))
    return can, o


def crop(can, o, conn, foot):
    """The window round one connection: centred across the face on its column, along the face from a tile
    and a half outside the wall to a little over a tile inside it."""
    x, y, f = conn
    dx, dy = FACE[f]
    fw, fh = foot
    if f in "NS":
        wall = dy * fh / 2
        cy = wall + dy * 0.2
        box = (x - WIN / 2, cy - WIN / 2, x + WIN / 2, cy + WIN / 2)
    else:
        wall = dx * fw / 2
        cx = wall + dx * 0.2
        box = (cx - WIN / 2, y - WIN / 2, cx + WIN / 2, y + WIN / 2)
    return can.crop(tuple(round(o + v * K) for v in box))


def main(out):
    os.makedirs(out, exist_ok=True)
    for name, r in REFS.items():
        can, o = scene(name)
        for c in r["conns"]:
            crop(can, o, c, r["foot"]).save(os.path.join(out, f"vanilla-{name}-{c[2]}{c[0]:+d}.png"))
            print("wrote", name, c)


if __name__ == "__main__":
    main(sys.argv[1])
