#!/usr/bin/env python3
"""Draw what leaves the Ignition Array at ignition.

Nothing leaves it. That is the point of the machine -- control.lua says it
"delivers nothing; it fires a current into the crust" -- but the engine insists
on a `rocket-silo-rocket` all the same, and it really does fly: measured on the
rig, the discharge goes from y = 0.5 to y = -144 and the silo returns to work.
So the entity stays and its art stops being a vehicle. What rises is a column of
violet-white light, section 9's last step: "the iris opens, the shaft floods with
light, and the sequence does not return to idle."

Four pieces, and the shape of each is dictated by the slot it fills:

  column.png        `rocket_sprite`. Hangs *below* its origin, the way vanilla's
                    rocket art does, so that as the nose climbs the tail still
                    stands in the shaft rather than tearing away from it.
  column-glare.png  `rocket_glare_overlay_sprite`. A soft bloom around the head.
  column-flame.png  `rocket_flame_animation`, 8 frames -- the only animated slot
                    the rocket prototype has. The flicker at the column's foot.
  ignition-glow.png The silo's own `rocket_glow_overlay_sprite`, additive, which
                    is the deck itself lit by what is coming out of it.

Drawn at 2x and shipped at `scale = 0.5`, like every other plate in this set.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "graphics", "entity", "ignition-array")

GLOW = (0xC9, 0xB6, 0xFF)        # section 3.3 working glow
WHITE = (0xFF, 0xFF, 0xFF)

COL_W, COL_H = 208, 512          # 3.25 x 8 tiles on screen at scale 0.5


def _mix(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def column():
    """The rising column: a white core in a violet sheath, hottest at its foot."""
    img = Image.new("RGBA", (COL_W, COL_H), (0, 0, 0, 0))
    px = img.load()
    cx = COL_W / 2
    for y in range(COL_H):
        # 0 at the foot, 1 at the head. The column thins and cools as it climbs.
        t = 1 - y / COL_H
        width = (0.30 + 0.55 * (1 - t) ** 0.7) * COL_W / 2
        strength = (1 - t) ** 0.55
        for x in range(COL_W):
            d = abs(x - cx) / width
            if d >= 1:
                continue
            fall = math.cos(d * math.pi / 2) ** 2
            core = max(0.0, 1 - d * 3.0)
            c = _mix(GLOW, WHITE, core)
            px[x, y] = c + (int(255 * fall * strength),)
    return img.filter(ImageFilter.GaussianBlur(3))


def glare(size=384):
    """A round bloom, for the overlay the engine draws over the rising head."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, (f, a) in enumerate([(1.0, 22), (0.78, 32), (0.58, 48),
                                (0.40, 74), (0.25, 120), (0.13, 190)]):
        r = size / 2 * f
        c = _mix(GLOW, WHITE, (i / 5.0) ** 2)
        d.ellipse((size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r), fill=c + (a,))
    return img.filter(ImageFilter.GaussianBlur(size / 24))


def flame(frames=8, w=232, h=232):
    """Eight frames of flare at the column's foot.

    Not fire -- section 10 forbids flame and smoke outright, on a world where
    nothing burns. This is the discharge unsteadying, so the variation is in
    brightness and spread rather than in tongues of anything.
    """
    sheet = Image.new("RGBA", (w * frames, h), (0, 0, 0, 0))
    for f in range(frames):
        # Two beats per loop, so it reads as a flicker rather than a slow pulse.
        k = 0.68 + 0.32 * math.sin(2 * math.pi * (2 * f / frames))
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for i, (fx, fy, a) in enumerate([(1.00, 0.62, 26), (0.74, 0.46, 44),
                                         (0.50, 0.32, 82), (0.28, 0.20, 150),
                                         (0.14, 0.11, 230)]):
            rx, ry = w / 2 * fx * k, h / 2 * fy * k
            c = _mix(GLOW, WHITE, (i / 4.0) ** 1.5)
            d.ellipse((w / 2 - rx, h / 2 - ry, w / 2 + rx, h / 2 + ry),
                      fill=c + (int(a * k),))
        sheet.alpha_composite(img.filter(ImageFilter.GaussianBlur(6)), (f * w, 0))
    return sheet


def deck_glow(w=520, h=470):
    """The deck lit from its own shaft. Additive, so it adds light and no colour cast."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, (f, a) in enumerate([(1.0, 20), (0.80, 28), (0.62, 40),
                                (0.46, 58), (0.32, 88), (0.20, 140), (0.10, 210)]):
        rx, ry = w / 2 * f, h / 2 * f
        c = _mix(GLOW, WHITE, (i / 6.0) ** 2)
        d.ellipse((w / 2 - rx, h / 2 - ry, w / 2 + rx, h / 2 + ry), fill=c + (a,))
    return img.filter(ImageFilter.GaussianBlur(14))


def main():
    for img, name in ((column(), "column.png"), (glare(), "column-glare.png"),
                      (flame(), "column-flame.png"), (deck_glow(), "ignition-glow.png")):
        img.save(os.path.join(ART, name))
        print("  %-20s %dx%d" % (name, img.width, img.height))


if __name__ == "__main__":
    main()
