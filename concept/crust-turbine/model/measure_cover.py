#!/usr/bin/env python3
"""How much of the 3 x 5 footprint the Siderane turbine covers, beside vanilla's steam turbine.

  python3 measure_cover.py <render-dir> [--round1 <sheets-dir>]

<render-dir> is render.sh's <out-dir>/renders: still-<direction>.png on the model's canvas,
the entity origin at its centre, 64 px a tile. Vanilla's steam-turbine-H / -V frame 0 is
placed at its prototype shift. --round1 composes round 1's plate from its packed sheets
(base-<direction>.png and rotor frame 0, at meta.json's shifts).

Two numbers per plate, alpha above 127 counted as covered:
  footprint  the share of the footprint's own rectangle on the screen (5 x 3 tiles
             horizontal, 3 x 5 vertical, centred on the origin) that the plate covers
  mass       every opaque pixel, inside the footprint or not, over the footprint's area
             (a tall machine draws up past its north edge; this counts that too)
"""
import json
import os
import sys

from PIL import Image

PPT = 64
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../tools"))
import paths  # noqa: E402   tools/paths.py: where Factorio is
VAN = os.path.join(paths.factorio_data(), "base/graphics/entity/steam-turbine")
FOOT = {"horizontal": (5, 3), "vertical": (3, 5)}
VANILLA = {"horizontal": ("steam-turbine-H.png", 320, 245, (0, -5.5)),
           "vertical": ("steam-turbine-V.png", 217, 374, (9.5, 0))}
C = 512                                    # a working canvas, origin at its centre


def placed(layer, shift_px):
    im = Image.new("RGBA", (C, C))
    im.alpha_composite(layer, (round(C / 2 - layer.width / 2 + shift_px[0]),
                               round(C / 2 - layer.height / 2 + shift_px[1])))
    return im


def measure(im, d):
    a = im.getchannel("A").point(lambda v: 255 if v > 127 else 0)
    w, h = FOOT[d]
    box = (C // 2 - w * PPT // 2, C // 2 - h * PPT // 2, C // 2 + w * PPT // 2, C // 2 + h * PPT // 2)
    inside = a.crop(box).histogram()[255]
    total = a.histogram()[255]
    area = w * h * PPT * PPT
    return dict(footprint=round(inside / area, 3), mass=round(total / area, 3))


def ours(rd, d):
    return placed(Image.open(os.path.join(rd, f"still-{d}.png")).convert("RGBA"), (0, 0))


def vanilla(d):
    f, w, h, sh = VANILLA[d]
    return placed(Image.open(os.path.join(VAN, f)).convert("RGBA").crop((0, 0, w, h)), sh)


def from_sheets(sd, d):
    meta = json.load(open(os.path.join(sd, "meta.json")))
    im = Image.new("RGBA", (C, C))
    for stem in (f"base-{d}", f"rotor-{d}"):
        m = meta[stem]
        lay = Image.open(os.path.join(sd, f"{stem}.png")).convert("RGBA").crop((0, 0, *m["size"]))
        im.alpha_composite(placed(lay, (m["shift"][0] * PPT, m["shift"][1] * PPT)))
    return im


def main():
    rd = sys.argv[1]
    r1 = sys.argv[sys.argv.index("--round1") + 1] if "--round1" in sys.argv else None
    for d in ("horizontal", "vertical"):
        print(d, "ours", measure(ours(rd, d), d))
        if r1:
            print(d, "round1", measure(from_sheets(r1, d), d))
        print(d, "vanilla", measure(vanilla(d), d))


if __name__ == "__main__":
    main()
