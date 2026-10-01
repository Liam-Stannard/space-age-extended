#!/usr/bin/env python3
"""Composite the passes the way the engine layers them, beside vanilla, for review.

  python3 preview.py <render-dir> <out.png>

Layers: ground, shadow at 50 %, idle plate, coupling frame, additive glow, lamp.
Vanilla chemical plant and assembling machine 3 go on the same ground at the
same scale, as the camera and finish reference.
"""
import os
import sys
from PIL import Image, ImageChops

D, OUT = sys.argv[1], sys.argv[2]
FD = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity")
GROUND = (74, 66, 58, 255)


def ours(working, frame=0):
    idle = Image.open(f"{D}/idle.png").convert("RGBA")
    W, H = idle.size
    im = Image.new("RGBA", (W, H), GROUND)
    sh = Image.open(f"{D}/shadow.png").convert("RGBA")
    a = sh.getchannel("A").point(lambda v: v // 2)
    im.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 0), a)
    im.alpha_composite(idle)
    im.alpha_composite(Image.open(f"{D}/coupling-{frame:02d}.png").convert("RGBA"))
    if working:
        glow = ImageChops.subtract(Image.open(f"{D}/working.png").convert("RGB"),
                                   idle.convert("RGB"))
        im = Image.merge("RGBA", (*ImageChops.add(im.convert("RGB"), glow).split(),
                                  im.getchannel("A")))
    lamp = Image.open(f"{D}/lamp.png").convert("RGBA")
    tint = Image.new("RGBA", lamp.size, (80, 255, 80, 255))
    im.alpha_composite(ImageChops.multiply(lamp, tint))
    return im


def vanilla(base_png, frame_w, frame_h, shadow_png=None, sw=0, sh=0, sdx=0, sdy=0, bdx=0, bdy=0):
    im = Image.new("RGBA", (256, 256), GROUND)
    if shadow_png:
        s = Image.open(f"{FD}/{shadow_png}").convert("RGBA").crop((0, 0, sw, sh))
        a = s.getchannel("A").point(lambda v: v // 2)
        blk = Image.new("RGBA", s.size, (0, 0, 0, 255))
        im.paste(blk, (128 - sw // 2 + sdx, 128 - sh // 2 + sdy), a)
    b = Image.open(f"{FD}/{base_png}").convert("RGBA").crop((0, 0, frame_w, frame_h))
    im.alpha_composite(b, (128 - frame_w // 2 + bdx, 128 - frame_h // 2 + bdy))
    return im


panels = [
    vanilla("chemical-plant/chemical-plant-north-base.png", 204, 292, "chemical-plant/chemical-plant-shadow.png",
            312, 222, 54, 12, 2, -18),
    vanilla("assembling-machine-3/assembling-machine-3-base.png", 196, 192,
            None, 0, 0, 0, 0, -1, 5),
    ours(False), ours(True), ours(True, 6),
]
sheet = Image.new("RGBA", (256 * len(panels), 256), GROUND)
for i, p in enumerate(panels):
    sheet.alpha_composite(p, (256 * i, 0))
# the true tile grid, so the footprint can be read off
from PIL import ImageDraw
d = ImageDraw.Draw(sheet)
for i in range(len(panels)):
    for k in range(-2, 3):
        x0 = 256 * i + 128 + 64 * k - 32
        d.line([(x0, 0), (x0, 255)], fill=(255, 255, 255, 40))
        d.line([(256 * i, 128 + 64 * k - 32), (256 * i + 255, 128 + 64 * k - 32)], fill=(255, 255, 255, 40))
sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST)
sheet.save(OUT)
