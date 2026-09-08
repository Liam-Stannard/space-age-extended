#!/usr/bin/env python3
"""Draw the Ignition Array's open shaft and the light that comes out of it.

Two of the rocket-silo's named slots, and neither can be generated: they have to
register with the hole `cut-array-iris.py` leaves in the deck, to the pixel, or
the shaft floats inside its own mouth. So both are drawn from the same measured
ellipse the cut uses.

`hole.png` -- what the player sees once the blades part. A vertical shaft seen
from Factorio's tilted camera shows its *far* wall, which on this projection is
the upper one, so the lining is bright along the top of the mouth and falls away
to black at the bottom. Vanilla's own 01-rocket-silo-hole.png reads exactly that
way. Lining ribs follow the mouth's curvature and converge as they recede, which
is what gives the mouth depth rather than looking like a painted disc.

`hole-light.png` -- section 3.3's violet-white, drawn additively over the shaft
and spilling a little onto the deck around it. This is the only slot on the
building the engine drives from launch state, so it is the whole of what the
player sees at ignition.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "graphics", "entity", "ignition-array")

# Shared with cut-array-iris.py. The shaft is drawn a shade wider than the
# blades so no seam of background shows between the two.
CX, CY = 302, 276
RX, RY = 85, 75
SIZE = (608, 602)

LINING = (0x6E, 0x68, 0x5C)     # section 3.3 casing, top of range
GLOW = (0xC9, 0xB6, 0xFF)       # section 3.3 working glow


def shaft():
    """The shaft interior: lining at the far wall, black at the bottom."""
    img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Fifteen rings, each smaller and pushed down-screen, so the shaft recedes
    # away from the camera rather than straight down the page. Each is darker
    # than the last; together they are the wall, and the last one is the bottom.
    rings = 15
    for i in range(rings):
        t = i / (rings - 1)
        rx = RX * (1 - 0.55 * t)
        ry = RY * (1 - 0.55 * t)
        cy = CY + RY * 0.42 * t          # the far wall is what stays in view
        shade = 1 - t
        c = tuple(int(v * (0.10 + 0.62 * shade ** 2)) for v in LINING)
        d.ellipse((CX - rx, cy - ry, CX + rx, cy + ry), fill=c + (255,))

    # Ribs on the visible wall: short arcs following the mouth, fading as they
    # go down. Drawn only across the top half, because that is the only wall the
    # camera can see into.
    for i in range(1, 7):
        t = i / 7.0
        rx = RX * (1 - 0.5 * t)
        ry = RY * (1 - 0.5 * t)
        cy = CY + RY * 0.38 * t
        v = int(150 * (1 - t) ** 1.4)
        d.arc((CX - rx, cy - ry, CX + rx, cy + ry), 185, 355,
              fill=(v, v, int(v * 0.94), 255), width=2)

    img = img.filter(ImageFilter.GaussianBlur(0.6))

    # Clip to the mouth, so nothing of the shaft lands on the deck.
    mask = Image.new("L", SIZE, 0)
    ImageDraw.Draw(mask).ellipse((CX - RX, CY - RY, CX + RX, CY + RY), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.0))
    img.putalpha(mask)
    return img


def light():
    """Violet-white light standing in the shaft and spilling onto the deck."""
    img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # A small white core in the mouth, then wider and fainter violet passes over
    # it, so the falloff is smooth without needing a per-pixel gradient. Only the
    # last two passes go white: section 3.3 wants violet-white reading *violet*,
    # and blending the whole stack toward white turns the shaft into a lightbulb.
    passes = [(2.35, 22), (1.85, 30), (1.45, 42), (1.15, 58),
              (0.90, 88), (0.66, 136), (0.40, 200), (0.20, 255)]
    for i, (f, a) in enumerate(passes):
        rx, ry = RX * f, RY * f
        # Light rises, so each tighter pass sits a little higher up the shaft.
        cy = CY - RY * 0.10 * (1 - f / 2.35)
        w = max(0.0, (i - 5) / 2.0) ** 1.5      # 0 until the last two passes
        c = tuple(int(g + (255 - g) * w) for g in GLOW)
        d.ellipse((CX - rx, cy - ry, CX + rx, cy + ry), fill=c + (a,))

    return img.filter(ImageFilter.GaussianBlur(9))


def emit(img, name, path):
    """Crop to content and print the Lua the prototype needs.

    Every piece here is cut or drawn on `base.png`'s own 608x602 canvas, whose
    centre is the entity origin (the deck ships at shift {0, 0}). So a cropped
    piece's shift is just how far its own centre has moved from that origin,
    converted to tiles: pixels / 64, because the plates are drawn at 2x and the
    prototype scales them by 0.5.
    """
    box = img.getbbox()
    if box is None:
        raise SystemExit("%s came out empty" % name)
    piece = img.crop(box)
    piece.save(path)
    cx = (box[0] + box[2]) / 2 - img.width / 2
    cy = (box[1] + box[3]) / 2 - img.height / 2
    print("  %-16s width = %d, height = %d, shift = { %.5f, %.5f }"
          % (name, piece.width, piece.height, cx / 64, cy / 64))


def main():
    print("shaft and light at (%d,%d) %dx%d" % (CX, CY, RX, RY))
    emit(shaft(), "hole.png", os.path.join(ART, "hole.png"))
    emit(light(), "hole-light.png", os.path.join(ART, "hole-light.png"))


if __name__ == "__main__":
    main()
