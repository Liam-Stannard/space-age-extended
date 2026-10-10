#!/usr/bin/env python3
"""The Gas Pump beside the vanilla sprites its pipes and hoses were measured against (round 11).

  python3 compare_vanilla.py <sheets-dir> <compare.png> [<label>]

  <sheets-dir>  render.sh's <out-dir>/sheets (base-<d>.png, meta.json)

One ground at 64 px a tile (vanilla's high-resolution sprites at scale 0.5 draw 64 px to a
tile, as ours do), the tile grid on it, each sprite on the entity origin and moved by its
prototype's shift: vanilla's straight pipe (vertical and horizontal), its pump (north, frame 0),
its chemical plant (north base) and its offshore pump (north, frame 0); then our four plates.
A row at 1x, then vanilla and ours each in a row at 2x (nearest neighbour). No shadows: the plates alone, so the pipes and
hoses read for what they are.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

FD = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity")
PPT = 64
GROUND = (74, 66, 58, 255)
BG = (30, 30, 30, 255)


def frame(rel, w, h):
    return Image.open(os.path.join(FD, rel)).convert("RGBA").crop((0, 0, w, h))


# (label, image, shift in tiles, panel size in tiles, footprint) -- shifts from base/prototypes/entity
VANILLA = [
    ("vanilla pipe", frame("pipe/pipe-straight-vertical.png", 128, 128), (0, 0), 2, (1, 1)),
    ("vanilla pipe", frame("pipe/pipe-straight-horizontal.png", 128, 128), (0, 0), 2, (1, 1)),
    ("vanilla pump (1x2)", frame("pump/pump-north.png", 103, 164), (8 / 32, -0.85 / 32), 3, (1, 2)),
    ("vanilla offshore pump", frame("offshore-pump/offshore-pump_North.png", 90, 162), (-1 / 32, -15 / 32), 4,
     (1, 2)),
    ("vanilla chemical plant (3x3)", frame("chemical-plant/chemical-plant-north-base.png", 204, 292),
     (1 / 32, -9 / 32), 5, (3, 3)),
]


def panel(im, shift, tiles, k, foot):
    s = tiles * PPT
    c = Image.new("RGBA", (s, s), GROUND)
    d = ImageDraw.Draw(c, "RGBA")
    o = s / 2
    # tile edges: on whole tiles from the origin along an even side of the footprint, on half
    # tiles along an odd one; the footprint outlined
    for i in range(-tiles, tiles + 1):
        x = round(o + (i + 0.5 * (foot[0] % 2)) * PPT)
        y = round(o + (i + 0.5 * (foot[1] % 2)) * PPT)
        if 0 <= x <= s:
            d.line([(x, 0), (x, s)], fill=(255, 255, 255, 30))
        if 0 <= y <= s:
            d.line([(0, y), (s, y)], fill=(255, 255, 255, 30))
    d.rectangle([o - foot[0] * PPT / 2, o - foot[1] * PPT / 2, o + foot[0] * PPT / 2, o + foot[1] * PPT / 2],
                outline=(255, 255, 255, 90))
    c.alpha_composite(im, (round(o + shift[0] * PPT - im.width / 2), round(o + shift[1] * PPT - im.height / 2)))
    return c.resize((s * k, s * k), Image.NEAREST)


def label(im, text):
    out = Image.new("RGBA", (im.width, im.height + 16), BG)
    out.alpha_composite(im, (0, 16))
    ImageDraw.Draw(out).text((4, 2), text, fill=(230, 230, 230, 255))
    return out


def main(sheets, out, tag="Gas Pump"):
    meta = json.load(open(os.path.join(sheets, "meta.json")))
    ours = [(f"{tag}, {d}", Image.open(os.path.join(sheets, f"base-{d}.png")).convert("RGBA"),
             tuple(meta[f"base-{d}"]["shift"]), 3, (2, 2)) for d in ("north", "east", "south", "west")]
    rows = [[label(panel(im, sh, t, 1, f), f"{name}, 1x") for name, im, sh, t, f in VANILLA + ours]]
    for group in (VANILLA, ours):
        rows.append([label(panel(im, sh, t, 2, f), f"{name}, 2x") for name, im, sh, t, f in group])
    gap = 6
    W = max(sum(p.width for p in r) + gap * (len(r) + 1) for r in rows)
    H = sum(max(p.height for p in r) for r in rows) + gap * (len(rows) + 1)
    sheet = Image.new("RGBA", (W, H), BG)
    y = gap
    for r in rows:
        x = gap
        for p in r:
            sheet.alpha_composite(p, (x, y))
            x += p.width + gap
        y += max(p.height for p in r) + gap
    sheet.save(out)


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    main(*sys.argv[1:])
