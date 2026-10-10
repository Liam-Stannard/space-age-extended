#!/usr/bin/env python3
"""The Gas Pump's sight glass, close up (round 9).

  python3 glass_closeup.py <out-dir> <direction> <glass-closeup.png>

  <out-dir>  render.sh's output directory (<out-dir>/renders: idle-<d>, light-<d>)

Three panels of one direction's sight glass, each at 4x of the sprite (nearest neighbour):
the plate as it is idle (dark empty glass), and the plate with the light layer over it tinted
as each vent's gas tints it -- siderane chartreuse (0.66, 0.85, 0.16) and helium-3 (0.55, 0.78,
0.90) -- multiplied in as ordinary tinted paint.
"""
import sys

from PIL import Image, ImageDraw

TINTS = (("idle (plate)", None), ("siderane", (0.66, 0.85, 0.16)), ("helium-3", (0.55, 0.78, 0.90)))
K = 4


def main(run, d, out):
    idle = Image.open(f"{run}/renders/idle-{d}.png").convert("RGBA")
    light = Image.open(f"{run}/renders/light-{d}.png").convert("RGBA")
    bb = light.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    cx, cy = (bb[0] + bb[2]) // 2, (bb[1] + bb[3]) // 2
    box = (cx - 24, cy - 14, cx + 24, cy + 14)
    tiles = []
    for name, rgb in TINTS:
        c = Image.new("RGBA", idle.size, (74, 66, 58, 255))
        c.alpha_composite(idle)
        if rgb:
            r, g, b, a = light.split()
            c.alpha_composite(Image.merge("RGBA", (r.point(lambda v: int(v * rgb[0])), g.point(lambda v: int(v * rgb[1])),
                                                   b.point(lambda v: int(v * rgb[2])), a)))
        tl = c.crop(box).resize(((box[2] - box[0]) * K, (box[3] - box[1]) * K), Image.NEAREST)
        o = Image.new("RGBA", (tl.width, tl.height + 18), (30, 30, 30, 255))
        o.paste(tl, (0, 18))
        ImageDraw.Draw(o).text((4, 3), f"{d}: sight glass, {name}, 4x", fill=(220, 220, 220, 255))
        tiles.append(o)
    sheet = Image.new("RGBA", (sum(t.width for t in tiles) + 8 * (len(tiles) + 1), tiles[0].height + 16),
                      (30, 30, 30, 255))
    x = 8
    for t in tiles:
        sheet.paste(t, (x, 8))
        x += t.width + 8
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: glass_closeup.py <out-dir> <direction> <glass-closeup.png>")
    main(*sys.argv[1:])
