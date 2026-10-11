#!/usr/bin/env python3
"""Where the Siderane turbine's two stubs land against vanilla's pipe, in each direction.

  python3 measure_ports.py <render-dir>

<render-dir> is render.sh's <out-dir>/renders: idle-<direction>.png on the model's canvas,
the entity origin at its centre, 64 px a tile. The connections are {0, -2} and {0, 2} (as
the steam turbine's): a pipe joins on the tile beyond each end, so each stub must end on
its tile's edge, 2.5 tiles from the origin, on the pipe's line. Vanilla's straight pipe
(base/graphics/entity/pipe), as the Vacuum Furnace measured it: horizontal, its axis 1 px
above its tile's centre and its end ring 52 px tall; vertical, its axis 0.5 px right of the
centre and its ring 51 px wide; the vertical pipe's sprite reaches 21 px above its tile's
top edge, so a south stub that stops up to 21 px short of the edge is still met.

Horizontal: in the 3 px columns inside each end (x +-2.5 tiles), the opaque run's top,
bottom, height and centre (px from the origin, y down). Vertical: the stubs' rows -- the
widest row of the end flange near each end, its width and centre (px, x right), and the
lowest and highest opaque rows. Vanilla's steam turbine, measured the same way, beside.
"""
import os
import sys

from PIL import Image

VAN = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/steam-turbine")
PPT = 64


def opaque(a, x=None, y=None):
    if x is not None:
        return [yy for yy in range(a.height) if a.getpixel((x, yy)) > 127]
    return [xx for xx in range(a.width) if a.getpixel((xx, y)) > 127]


def horizontal(a, ox, oy):
    out = {}
    for side, x in (("W", round(ox - 2.5 * PPT) + 1), ("E", round(ox + 2.5 * PPT) - 2)):
        ys = opaque(a, x=x)
        if not ys:
            out[side] = "nothing drawn at the edge"
            continue
        top, bot = ys[0] - oy, ys[-1] + 1 - oy
        out[side] = dict(column=x - ox, top=top, bottom=bot, height=bot - top, axis=(top + bot) / 2,
                         want="height 52, axis -1")
    return out


def vertical(a, ox, oy):
    rows = [y for y in range(a.height) if opaque(a, y=y)]
    out = dict(top=rows[0] - oy, bottom=rows[-1] + 1 - oy, want="bottom ~160 (2.5 tiles), met from 139")
    # the end flange's centre, from the 6 px at each end (its width is the model's R_END: further in, the
    # collar overlaps it on the screen, so no row there is the flange alone)
    for side, rng in (("N", range(rows[0], rows[0] + 6)), ("S", range(rows[-1] - 5, rows[-1] + 1))):
        best = max(rng, key=lambda y: len(opaque(a, y=y)))
        xs = opaque(a, y=best)
        out[side] = dict(row=best - oy, width=len(xs), centre=(xs[0] + xs[-1] + 1) / 2 - ox, want="width 51, centre 0.5")
    return out


def main():
    rd = sys.argv[1]
    for d, fn in (("horizontal", horizontal), ("vertical", vertical)):
        im = Image.open(os.path.join(rd, f"idle-{d}.png")).convert("RGBA")
        print(d, "ours", fn(im.getchannel("A"), im.width / 2, im.height / 2))
    h = Image.open(os.path.join(VAN, "steam-turbine-H.png")).convert("RGBA").crop((0, 0, 320, 245))
    print("horizontal vanilla", horizontal(h.getchannel("A"), 160, 122.5 + 5.5))
    v = Image.open(os.path.join(VAN, "steam-turbine-V.png")).convert("RGBA").crop((0, 0, 217, 374))
    print("vertical vanilla", vertical(v.getchannel("A"), 108.5 - 9.5, 187))


if __name__ == "__main__":
    main()
