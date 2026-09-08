#!/usr/bin/env python3
"""The Ignition Array's plate geometry, as code -- and the images that state it.

**Why this is a tool and not three PNGs.** The plan's numbers previously lived in
`graphics/array-plate-plan.md` and in two diagrams that an ad-hoc script had
produced and thrown away. Nothing could regenerate them, so nothing could check
them against each other, which is the same failure the plan itself exists to
prevent one level down. Every number below is read off vanilla's `rocket-silo`
prototype; everything drawn is derived from them.

It emits three images:

  * `plate-plan-deck.png` -- the dimensioned drawing, for the record.
  * `plate-plan-lid.png`  -- the lid and the true seam angle.
  * `plate-paint-template.png` -- **the one to hand a generator.**

**The template is the point of round 4.** Rounds 1-3 were given a diagram that
drew the *hole* -- a filled ellipse on a dark ground -- and stated the ring's
size in words and arithmetic. The hole came out right and the ring did not: r3
put the hole at 0.582 of the deck's width where vanilla is at 0.637, so fitting
the hole to vanilla's 6.25 tiles pushed the deck to 10.74 tiles on a 9-tile
footprint. That is not a generator being careless. The diagram never showed the
ring, so its thickness was the one quantity there was nothing to copy.

The round log's own conclusion was that a generator will not hit a stated ratio
but will hit a shape it is shown. So the ring is now shown: flat grey where
armour goes, magenta where the hole and the ground go, at exactly the
proportions the slots require. Painting inside a given silhouette is the thing
that worked first time on v3, when the actual hole sprite was handed over.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "graphics", "entity", "ignition-array", "concept")

# ---------------------------------------------------------------------------
# The geometry, on a base where the building is 1000 units wide.
#
# Straight off the rocket silo: base_day_sprite is 628 x 612 and hole_sprite is
# 400 x 270, both at scale 0.5, with the hole shifted half a tile south of the
# entity origin and the deck 0.109 north of it.
# ---------------------------------------------------------------------------
BASE_PX, HOLE_PX = (628, 612), (400, 270)
DECK_SHIFT, HOLE_SHIFT = (0.0625, 0.109375), (-0.15625, 0.5)
PX_PER_TILE = 64.0                       # a sprite pixel at scale 0.5

W = 1000.0
H = W * BASE_PX[1] / BASE_PX[0]                       # 975
HW = W * HOLE_PX[0] / BASE_PX[0]                      # 637
HH = W * HOLE_PX[1] / BASE_PX[0]                      # 430
# The hole is not concentric: its shift and the deck's differ by 0.219 tiles
# west and 0.391 south, which on this base is where 478 / 527 comes from.
HCX = W / 2 + (HOLE_SHIFT[0] - DECK_SHIFT[0]) * PX_PER_TILE * W / BASE_PX[0]
HCY = H / 2 + (HOLE_SHIFT[1] - DECK_SHIFT[1]) * PX_PER_TILE * W / BASE_PX[0]

LID_PROUD = 1.05                         # the lid tucks under the collar
LW, LH = HW * LID_PROUD, HH * LID_PROUD

# The engine parts the leaves along the vector between their rest shifts. A seam
# must be perpendicular to the direction its halves separate.
PART = (DECK_SHIFT[0] * 0 + 1.15625 - (-0.875), 0.375 - 1.03125)      # (+2.031, -0.656)
SEAM_DEG = math.degrees(math.atan2(PART[0], PART[1])) % 180           # 108

MAGENTA = (247, 1, 248)
ARMOUR = (138, 138, 140)
INK = (24, 25, 28)


# A regular octagon's flat edge is 1/(1+sqrt2) of its span, so each chamfer eats
# the remaining 0.293. That is not a guess: measured across the accepted r3
# render, its flat top edge is 445 units wide on the 1000 base against this
# shape's 414, and the two silhouettes track each other down the chamfers to
# within a few per cent. The octagon is the shape r3 drew, stated exactly.
CHAMFER = (1 - 1 / (1 + math.sqrt(2))) / 2               # 0.2929


def octagon(x0, y0, w, h):
    """The deck's outline, as a regular octagon filling the given box."""
    cx, cy = CHAMFER * w, CHAMFER * h
    return [(x0 + cx, y0), (x0 + w - cx, y0), (x0 + w, y0 + cy),
            (x0 + w, y0 + h - cy), (x0 + w - cx, y0 + h), (x0 + cx, y0 + h),
            (x0, y0 + h - cy), (x0, y0 + cy)]


def canvas(px_wide, bg):
    s = px_wide / W
    img = Image.new("RGB", (int(round(W * s)), int(round(H * s))), bg)
    return img, s


def font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()


def paint_template(px_wide=1400):
    """Flat grey ring on flat magenta -- the silhouette to paint inside.

    Nothing here is styling. The grey is featureless on purpose: anything drawn
    on it would be copied, and what is wanted is the boundary, not the content.
    """
    # A margin of ground all round. Drawn to the frame edge, a generator reframes
    # the composition and the proportions go with it.
    s = px_wide / W
    m = 0.10 * px_wide
    img = Image.new("RGB", (int(round(W * s + 2 * m)), int(round(H * s + 2 * m))), MAGENTA)
    d = ImageDraw.Draw(img)
    d.polygon([(m + x * s, m + y * s) for x, y in octagon(0, 0, W, H)], fill=ARMOUR)
    d.ellipse([m + (HCX - HW / 2) * s, m + (HCY - HH / 2) * s,
               m + (HCX + HW / 2) * s, m + (HCY + HH / 2) * s], fill=MAGENTA)
    img.save(os.path.join(OUT, "plate-paint-template.png"))
    return img


def deck_diagram(px_wide=1256):
    """The same geometry, dimensioned, for a human reading the plan."""
    img, s = canvas(px_wide, INK)
    pad = int(0.09 * px_wide)
    sheet = Image.new("RGB", (img.width + 2 * pad, img.height + 2 * pad), INK)
    d = ImageDraw.Draw(sheet)

    def P(x, y):
        return (pad + x * s, pad + y * s)

    d.polygon([P(x, y) for x, y in octagon(0, 0, W, H)],
              fill=(52, 54, 60), outline=(120, 200, 250), width=3)
    d.ellipse([P(HCX - HW / 2, HCY - HH / 2), P(HCX + HW / 2, HCY + HH / 2)],
              fill=INK, outline=(235, 200, 110), width=3)
    d.rectangle([P(0, 0), P(W, H)], outline=(90, 94, 104), width=2)

    fb, fs = font(int(0.021 * px_wide)), font(int(0.017 * px_wide))
    d.line([P(HCX - HW / 2, HCY), P(HCX + HW / 2, HCY)], fill=(235, 110, 110), width=3)
    d.text(P(HCX - 60, HCY - 46), "hole 637", font=fb, fill=(235, 110, 110))
    d.line([P(HCX, HCY - HH / 2), P(HCX, HCY + HH / 2)], fill=(235, 110, 110), width=3)
    d.text(P(HCX + 14, HCY + 60), "430", font=fb, fill=(235, 110, 110))

    # The ring, which is what rounds 1-3 were never shown.
    for (x0, y0), (x1, y1), label in (
            ((0, HCY), (HCX - HW / 2, HCY), "ring 159"),
            ((HCX + HW / 2, HCY), (W, HCY), "204"),
            ((HCX, 0), (HCX, HCY - HH / 2), "312"),
            ((HCX, HCY + HH / 2), (HCX, H), "233")):
        d.line([P(x0, y0), P(x1, y1)], fill=(120, 250, 160), width=4)
        d.text(P((x0 + x1) / 2 - 40, (y0 + y1) / 2 - 40), label, font=fb, fill=(120, 250, 160))

    for i, line in enumerate((
            "IF THE BUILDING IS 1000 UNITS WIDE IT IS 975 TALL",
            "HOLE 637 x 430, exactly 1.4815 : 1, centred 478 across and 527 down",
            "RING left 159, right 204, top 312, bottom 233 -- the hole is 0.637 of the width")):
        d.text((pad, int(0.012 * px_wide) + i * int(0.026 * px_wide)), line,
               font=fs, fill=(240, 240, 240))
    sheet.save(os.path.join(OUT, "plate-plan-deck.png"))


def lid_diagram(px_wide=1000):
    """The lid, and the seam angle the engine's parting vector demands."""
    m = 0.12 * px_wide
    s = px_wide / LW
    img = Image.new("RGB", (int(px_wide + 2 * m), int(LH * s + 2 * m)), INK)
    d = ImageDraw.Draw(img)
    cx, cy = img.width / 2, img.height / 2
    d.ellipse([cx - LW * s / 2, cy - LH * s / 2, cx + LW * s / 2, cy + LH * s / 2],
              fill=(52, 54, 60), outline=(235, 200, 110), width=3)
    r = max(img.size)
    a = math.radians(SEAM_DEG)
    d.line([cx - r * math.cos(a), cy + r * math.sin(a),
            cx + r * math.cos(a), cy - r * math.sin(a)], fill=(120, 250, 160), width=4)
    fs = font(int(0.026 * px_wide))
    for i, line in enumerate((
            "LID %d x %d on the 1000-unit base, exactly 1.4815 : 1" % (round(LW), round(LH)),
            "SEAM %.0f degrees from horizontal, through the centre" % SEAM_DEG,
            "five per cent proud of the hole, so it tucks under the collar")):
        d.text((14, 12 + i * int(0.034 * px_wide)), line, font=fs, fill=(240, 240, 240))
    img.save(os.path.join(OUT, "plate-plan-lid.png"))


def main():
    print("on a 1000-wide building:")
    print("  building   %.0f x %.0f" % (W, H))
    print("  hole       %.0f x %.0f  (%.4f : 1) centred %.0f, %.0f"
          % (HW, HH, HW / HH, HCX, HCY))
    print("  hole edges left %.0f right %.0f top %.0f bottom %.0f"
          % (HCX - HW / 2, HCX + HW / 2, HCY - HH / 2, HCY + HH / 2))
    print("  ring       left %.0f right %.0f top %.0f bottom %.0f"
          % (HCX - HW / 2, W - (HCX + HW / 2), HCY - HH / 2, H - (HCY + HH / 2)))
    print("  hole / deck width = %.3f" % (HW / W))
    print("  lid        %.0f x %.0f, seam %.0f degrees" % (LW, LH, SEAM_DEG))
    paint_template()
    deck_diagram()
    lid_diagram()
    print("wrote plate-paint-template.png, plate-plan-deck.png, plate-plan-lid.png")


if __name__ == "__main__":
    main()
