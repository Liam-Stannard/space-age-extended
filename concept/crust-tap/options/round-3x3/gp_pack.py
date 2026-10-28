#!/usr/bin/env python3
"""Gas Pump 3x3, options round: a take's 4x renders packed as 1x sheets for tools/blender/measure.py.

  python3 -B gp_pack.py <render-dir> <out-dir>

The Vent Pump round 5's vp5_pack.py, for this round's renders (gp_<n>_*.py: 352 px canvas at 1x, the origin
at (160, 208)); measure.py reads a packed sheets directory: meta.json and the sheets, 64 px a tile, each
placed at its shift from the entity's origin.

  base.png      the plate (idle, no ground) at 1x
  shadow.png    the shadow alone: idle.png (the plate over the catcher) where the plate is empty
  working.png   the working loop at 1x, 8 frames a row, the shadow cut away: a pixel is kept where the plate
                covers it (dilated a px) or where the frame itself is opaque (alpha >= 250, the machine: the
                catcher's shadow is never that dense), dilated a px -- so a part that moves past the plate's
                outline (the beam, the bell, the weights) stays whole
  meta.json     {"base", "shadow", "working": {size, shift[, frames, line_length]}}

Downsampled premultiplied with LANCZOS (tools/blender/downsample.py's way), the faint catcher fog under alpha
24 cut first, then the highlight roll-off (the Vent Pump round 5's vp5_roll.py: a px whose brightest channel
passes 236 is scaled whole to land under 250, hue kept; below the knee nothing changes).
"""
import json
import math
import os
import sys

from PIL import Image, ImageChops, ImageFilter

C, ORIGIN = 352, (160, 208)
SHIFT = [(C / 2 - ORIGIN[0]) / 64, (C / 2 - ORIGIN[1]) / 64]
KNEE, TOP = 236, 250
LUT = [255 if m <= KNEE else round(255 * (KNEE + (TOP - KNEE) * (1 - math.exp(-(m - KNEE) / (TOP - KNEE)))) / m)
       for m in range(256)]


def roll(im):
    r, g, b, a = im.convert("RGBA").split()
    k = ImageChops.lighter(ImageChops.lighter(r, g), b).point(LUT)
    return Image.merge("RGBA", [ImageChops.multiply(c, k) for c in (r, g, b)] + [a])


def down(path, k=1):
    im = Image.open(path).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 24 else v))
    return roll(im.convert("RGBa").resize((C * k, C * k), Image.LANCZOS).convert("RGBA"))


def solid(im):
    """The machine's own pixels in a frame drawn over the catcher (the plate's way of telling them apart)."""
    return im.getchannel("A").point(lambda v: 255 if v >= 250 else 0).filter(ImageFilter.MaxFilter(3))


def main(src, out):
    os.makedirs(out, exist_ok=True)
    meta = json.load(open(os.path.join(src, "meta.json")))
    nf = meta["frames"]
    plate = down(os.path.join(src, "plate.png"))
    plate.save(os.path.join(out, "base.png"))
    keep = plate.getchannel("A").point(lambda v: 255 if v > 0 else 0).filter(ImageFilter.MaxFilter(3))
    idle = down(os.path.join(src, "idle.png"))
    sh = idle.copy()
    sh.putalpha(ImageChops.multiply(idle.getchannel("A"), ImageChops.invert(keep)))
    sh.save(os.path.join(out, "shadow.png"))
    line = 8
    rows = (nf + line - 1) // line
    sheet = Image.new("RGBA", (C * line, C * rows))
    for f in range(nf):
        fr = down(os.path.join(src, f"working-{f:02d}.png"))
        m = ImageChops.lighter(keep, solid(fr))
        fr.putalpha(ImageChops.multiply(fr.getchannel("A"), m))
        sheet.paste(fr, ((f % line) * C, (f // line) * C))
    sheet.save(os.path.join(out, "working.png"))
    json.dump({"base": dict(size=[C, C], shift=SHIFT), "shadow": dict(size=[C, C], shift=SHIFT),
               "working": dict(size=[C, C], shift=SHIFT, frames=nf, line_length=line)},
              open(os.path.join(out, "meta.json"), "w"), indent=1)
    print(out, nf, "frames")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
