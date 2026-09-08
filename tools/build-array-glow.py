#!/usr/bin/env python3
"""Build the Ignition Array's assembly glow sheet.

Section 9 of the spec: while the array is building segments, violet light pulses
*inward* along the four cable trunks, and the iris seams take it up and breathe
in time. Continuous, not a completion animation -- crafting time varies, so
anything depicting "a segment finished" desynchronises from what the machine is
actually doing, while light travelling inward never does.

Derived, not generated, for the same reason as the Arc Mast's sheets: 32 separate
renders of a building drift, and a mask over one approved plate cannot. The
trunks are found in the plate itself by their copper -- section 3.3 puts copper
*only* on the trunk terminations and the busbars -- restricted to the four
diagonal corridors so the ochre trim elsewhere on the deck is left alone. The
seams are the dark lines inside the fitted iris ellipse.

Budget matters here, and it is measured against vanilla rather than guessed: the
silo's own crafting sheet is 208x210 at 64 frames, 2.9 Mpx. A glow across this
whole 608x602 plate at 64 frames would be 23 Mpx. So the sheet is drawn at *half*
the plate's resolution and shipped at `scale = 1.0` instead of 0.5 -- identical
on screen, a quarter of the pixels -- at 32 frames, which lands on vanilla's
budget almost exactly.
"""

import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "graphics", "entity", "ignition-array")
SRC = os.path.join(ART, "concept", "v3-around-hole.png")

CX, CY = 704, 580                # the opening's centre, shared with build-array-plates.py
BLADE_X, BLADE_Y = 431, 290
FRAMES = 32
COLS = 6
GLOW = (0xC9, 0xB6, 0xFF)        # section 3.3 working glow


def trunk_pixels(src):
    """The four cable trunks: copper, inside the diagonals, outside the ring.

    Returned as a list rather than a mask because only these pixels change from
    frame to frame -- walking the whole plate 32 times is thirty times the work
    for the same sheet.
    """
    w, h = src.size
    px = src.load()
    out = []
    for y in range(h):
        dy = y - CY
        for x in range(w):
            dx = x - CX
            if abs(abs(dx) - abs(dy)) > 70:
                continue
            rr = math.hypot(dx, dy)
            if rr < 470:                     # inside the collar: not a trunk
                continue
            r, g, b, a = px[x, y]
            if a < 100:
                continue
            if r > g > b and (r - b) > 34 and r > 60:
                out.append((x, y, rr))
    # Normalise against the trunks' own extent, not the plate's corner. Scaled
    # to the corner, the trunks occupy only the outer two thirds of the range and
    # a pulse sweeping 0..1 spends a third of every loop somewhere there is no
    # copper to light, so the arms sit dark for a beat.
    lo = min(d for _, _, d in out)
    hi = max(d for _, _, d in out)
    return [(x, y, (d - lo) / (hi - lo)) for x, y, d in out]


def seam_mask(src):
    """The blade seams: the dark lines inside the iris ellipse."""
    px = src.load()
    m = Image.new("L", src.size, 0)
    d = ImageDraw.Draw(m)
    for y in range(CY - BLADE_Y, CY + BLADE_Y + 1):
        ny = (y - CY) / BLADE_Y
        for x in range(CX - BLADE_X, CX + BLADE_X + 1):
            nx = (x - CX) / BLADE_X
            if nx * nx + ny * ny > 1:
                continue
            r, g, b, a = px[x, y]
            if a > 100 and (r + g + b) < 210:
                d.point((x, y), 255)
    return m.filter(ImageFilter.GaussianBlur(1.4))


def main():
    src = Image.open(SRC).convert("RGBA")
    trunks = trunk_pixels(src)
    seams = seam_mask(src)
    print("trunk pixels: %d" % len(trunks))

    # Quarter resolution, not half. The v3 plate is 1390 px wide where v1's was
    # 608, so halving it left 32 frames at 14.2 Mpx against the 2.9 vanilla
    # spends on its own crafting sheet. Quartering lands at 3.5 -- the same place
    # the v1 sheet sat -- and the frames are still drawn larger than they are
    # displayed, because the deck itself ships at scale 0.2317.
    half = (src.width // 4, src.height // 4)
    rows = (FRAMES + COLS - 1) // COLS
    sheet = Image.new("RGBA", (half[0] * COLS, half[1] * rows), (0, 0, 0, 0))

    for f in range(FRAMES):
        phase = f / FRAMES
        frame = Image.new("L", src.size, 0)
        fp = frame.load()
        # Two pulses in flight at once, half a loop apart, so a trunk never reads
        # as dead between beats. Adding the phase to the radius moves the bright
        # window toward the centre as the loop runs.
        for x, y, d in trunks:
            v = 0.0
            for k in (0.0, 0.5):
                u = (d + phase + k) % 1.0
                v = max(v, math.exp(-((u - 0.5) ** 2) / 0.006))
            if v > 0.004:
                fp[x, y] = int(255 * min(1.0, v))

        # The seams take the light up, breathing once per loop.
        breath = 0.35 + 0.65 * (0.5 - 0.5 * math.cos(2 * math.pi * phase))
        frame = ImageChops.lighter(frame, seams.point(lambda v, b=breath: int(v * b)))

        rgb = Image.new("RGBA", src.size, GLOW + (0,))
        rgb.putalpha(frame.filter(ImageFilter.GaussianBlur(1.8)))
        sheet.alpha_composite(rgb.resize(half, Image.LANCZOS),
                              ((f % COLS) * half[0], (f // COLS) * half[1]))

    sheet.save(os.path.join(ART, "working.png"))
    print("working.png %dx%d  frame %dx%d  %d frames, %d per row  (%.2f Mpx)"
          % (sheet.width, sheet.height, half[0], half[1], FRAMES, COLS,
             sheet.width * sheet.height / 1e6))
    # The deck ships at 0.2317 and this sheet is a quarter of the deck's
    # resolution, so it needs four times that scale to land on the same pixels.
    print("  shift = { 0, 0 }, scale = %.4f  -- quarter-resolution, matches the deck"
          % (0.2317 * 4))


if __name__ == "__main__":
    main()
