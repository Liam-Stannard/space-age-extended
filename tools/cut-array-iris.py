#!/usr/bin/env python3
"""Cut the Ignition Array's iris out of its locked plate.

A rocket-silo does not draw its shaft the way an assembling machine draws a
working animation. Vanilla's own `base_day_sprite` has a *hole* in the middle --
look at 06-rocket-silo.png and the deck is a ring -- `hole_sprite` is the shaft
interior drawn inside that hole, and the two door sprites sit over the hole and
are slid apart by the engine at `door_opening_speed`. So the closed iris cannot
stay painted on the deck: the doors would part and reveal a second, closed iris
underneath it.

Everything here is cut from `concept/base-closed.png`, the approved plate with
the iris still on it, so every piece registers with the deck by construction
rather than by eye. Nothing is generated.

Measured off that plate, not guessed: the iris rim is a dark ellipse fitted at
centre (302, 276), semi-axes 100 x 88, with 93% of sampled points on it dark.
Inside that rim runs a ring of bolts, found the same way: sampled brightness
along the ellipse peaks at r = 88. Rim and bolts are the housing and stay on the
deck; the blades inside them are the moving part, and they are what gets cut, at
83 x 73.

  tools/cut-array-iris.py                # the real cut
  tools/cut-array-iris.py --diagnostic   # flat-colour halves, so the engine's
                                         # door travel can be measured off a render
"""

import argparse
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "graphics", "entity", "ignition-array")
SRC = os.path.join(ART, "concept", "base-closed.png")

# The fitted iris. Changing these moves every piece at once, which is the point.
CX, CY = 302, 276
BLADE_X, BLADE_Y = 83, 73


def blade_mask(size, feather=1.2):
    """The ellipse the blades occupy, as an alpha mask."""
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).ellipse(
        (CX - BLADE_X, CY - BLADE_Y, CX + BLADE_X, CY + BLADE_Y), fill=255)
    return m.filter(ImageFilter.GaussianBlur(feather))


def seam_mask(size, keep):
    """Half of the plane, split along the NE-SW seam through the iris centre.

    Vanilla splits its hatch on that diagonal -- its two leaves rest at x = +1.16
    and x = -0.88 and the engine slides them apart along the axis between them --
    and on this building the seam then lies along two of the cable trunks, which
    is where a seam wants to be anyway.
    """
    m = Image.new("L", size, 0)
    r = 2 * max(size)
    corners = ([(CX - r, CY - r), (CX + r, CY - r), (CX + r, CY + r)] if keep == "ne"
               else [(CX - r, CY - r), (CX - r, CY + r), (CX + r, CY + r)])
    ImageDraw.Draw(m).polygon(corners, fill=255)
    return m


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
    ap = argparse.ArgumentParser()
    ap.add_argument("--diagnostic", action="store_true",
                    help="flat-colour door halves, for measuring door travel")
    args = ap.parse_args()

    src = Image.open(SRC).convert("RGBA")
    blades = blade_mask(src.size)

    # The deck: the plate with the blades lifted out, rim and everything else
    # left exactly as approved.
    deck = src.copy()
    deck.putalpha(ImageChops.subtract(src.getchannel("A"), blades))
    deck.save(os.path.join(ART, "base.png"))   # full canvas: shift stays { 0, 0 }

    # The two leaves, each the blades masked to its side of the seam. Cut from
    # the same plate, so closed they are indistinguishable from the original.
    for keep, out in (("ne", "door-back.png"), ("sw", "door-front.png")):
        leaf = src.copy()
        if args.diagnostic:
            leaf = Image.new("RGBA", src.size,
                             (255, 0, 255, 255) if keep == "ne" else (0, 255, 255, 255))
        leaf.putalpha(ImageChops.multiply(blades, seam_mask(src.size, keep)))
        emit(leaf, out, os.path.join(ART, out))

    print("iris centre (%d,%d) blades %dx%d%s"
          % (CX, CY, BLADE_X, BLADE_Y,
             "  [diagnostic colours]" if args.diagnostic else ""))


if __name__ == "__main__":
    main()
