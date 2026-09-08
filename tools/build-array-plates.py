#!/usr/bin/env python3
"""Cut the Ignition Array's shipped plates out of its two approved magenta renders.

The design is `concept/v3-around-hole.png` (the deck ring, built around vanilla's
own hole sprite) and `concept/v3-lid.png` (the closed lid). Both were generated
on flat magenta precisely so this step could be arithmetic rather than another
generation round -- see building-spec-ignition-array-v2.md, "What is left on the
Ignition Array", for why eight re-renders failed to hold the geometry and handing
the generator the actual hole succeeded first time.

Nothing here is drawn. Every shipped pixel is an approved pixel, moved.

Four jobs, and three of them exist because of something measured:

  1. **The lid is scaled vertically by 0.909.** It came back at aspect 1.346
     against vanilla's 1.481. A lid is an ellipse, so a single vertical scale
     lands it exactly -- no redraw, no round, no drift.

  2. **Vanilla's shaft pixels are cut out of the deck.** The deck render was
     built *around* Wube's actual hole sprite, so those pixels are in it and must
     not ship. This costs nothing: section 6.1 needs `base_day_sprite` to be a
     ring with a hole through it anyway, because `hole_sprite` draws the shaft
     inside that gap and the doors sit over it. The excision and the requirement
     are the same operation.

  3. **The lid is split on the NW-SE diagonal** into the engine's two door
     slots. Vanilla slides its leaves apart along the NE-SW axis -- measured off
     its own leaf alpha masks at about 51 degrees from horizontal, over 226
     sample rows -- so the seam has to be perpendicular to that, which is what
     the lid is drawn with.

  4. **Everything is cropped and its shift reported**, because a shift typed by
     hand is a shift that drifts.

  tools/build-array-plates.py [--check]
"""

import argparse
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "graphics", "entity", "ignition-array")
CONCEPT = os.path.join(ART, "concept")

# The magenta both renders were made on. Sampled, not assumed: the two came back
# a shade apart, so the key is generous and the tolerances below carry it.
KEY = (247, 1, 248)
NEAR, FAR = 70, 120

# Vanilla's mouth, from the rocket-silo prototype: 400 x 270 source px at 64 px
# per tile, which is 6.25 x 4.22 tiles at aspect 1.481.
MOUTH_ASPECT = 400 / 270


def key_out(img):
    """Flat-colour chroma key, with the spill pulled off the edges."""
    w, h = img.size
    out = img.convert("RGB").copy()
    op = out.load()
    px = out.load()
    alpha = Image.new("L", (w, h), 255)
    ap = alpha.load()
    kr, kg, kb = KEY
    span = max(1, FAR - NEAR)
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            d = max(abs(r - kr), abs(g - kg), abs(b - kb))
            if d <= NEAR:
                ap[x, y] = 0
            elif d < FAR:
                ap[x, y] = int(255 * (d - NEAR) / span)
            # Magenta spill reads as red and blue running ahead of green on metal
            # that is meant to be grey-brown.
            if ap[x, y] and r > g and b > g and (r - g) + (b - g) > 30:
                op[x, y] = (min(r, g + 12), g, min(b, g + 12))
    out = out.convert("RGBA")
    out.putalpha(alpha)
    return out


def content_box(img):
    """The drawn content, ignoring the alpha fringe a feathered key leaves."""
    a = img.getchannel("A").point(lambda v: 255 if v > 40 else 0)
    return a.getbbox()


# Vanilla's opening, in tiles, straight off the rocket-silo prototype:
# 400 x 270 source px at 64 px per tile.
MOUTH_TILES_W = 400 / 64          # 6.25
FOOTPRINT_TILES = 9


def find_shaft(img, dark=72):
    """Where the opening is, and how big.

    Its *centre* is measured; its *size* is derived. That split matters, and
    three attempts got it wrong before the reason was clear.

    The shaft is not uniformly dark. Vanilla's hole sprite has a brightly lit far
    wall along its top -- that lit wall is what gives the hole depth and makes it
    read as a shaft rather than a disc. So anything that looks for dark pixels
    measures the *floor*, not the opening:

      * Scoring an ellipse against dark points gives a perfect 1.000 to any
        ellipse inside the floor, and settles on whichever it meets first.
      * Flooding the dark pixels leaks through the machine's own shadowed
        recesses, which connect to the hole, and swallowed almost the whole deck.
      * Growing the largest inscribed dark ellipse stops the moment it touches
        the lit wall -- rx 344 against an opening half as wide again. That is
        why the lid did not cover the hole: it was sized to the floor.

    The size is therefore taken from what option C exists to match. The opening
    is vanilla's, 6.25 tiles across, and the deck is the 9-tile footprint, so the
    opening is 6.25/9 of the drawn deck however the render scaled it. The centre
    still comes from the dark floor, whose centroid is reliable even when its
    extent is not.
    """
    w, h = img.size
    g = img.convert("L").load()
    a = img.getchannel("A").load()
    sx = sy = n = 0
    for y in range(h):
        for x in range(w):
            if a[x, y] > 128 and g[x, y] < dark:
                sx += x
                sy += y
                n += 1
    if not n:
        raise SystemExit("no shaft found in the deck render")
    cx, cy = sx // n, sy // n

    box = content_box(img)
    deck_w = box[2] - box[0]
    rx = int(deck_w * (MOUTH_TILES_W / FOOTPRINT_TILES) / 2)
    ry = int(rx / MOUTH_ASPECT)
    return cx, cy, rx, ry, n


def emit(img, name, px_per_tile):
    """Crop to content, save, and print the prototype geometry.

    `shift` is in **tiles**, and the engine converts a sprite pixel to tiles as
    `pixels * scale / 32`. At the usual scale of 0.5 that is pixels/64, which is
    why every other plate in this mod divides by 64 -- but this deck ships at
    0.2317, where a tile is 138.1 px. Dividing by 64 here put every shift out by
    a factor of 2.16, which is a building sitting two tiles from its own
    footprint. Hence the parameter.
    """
    box = content_box(img)
    if box is None:
        raise SystemExit("%s came out empty" % name)
    piece = img.crop(box)
    piece.save(os.path.join(ART, name))
    cx = (box[0] + box[2]) / 2 - img.width / 2
    cy = (box[1] + box[3]) / 2 - img.height / 2
    print("  %-18s width = %4d, height = %4d, shift = { %.5f, %.5f }"
          % (name, piece.width, piece.height, cx / px_per_tile, cy / px_per_tile))
    return piece


def seam_half(size, centre, keep):
    """Half the plane, split on the NW-SE diagonal through the lid's centre.

    Perpendicular to the axis the engine slides the leaves along -- see the
    module docstring. `keep` is "ne" for the upper-right half, "sw" for the
    lower-left.
    """
    m = Image.new("L", size, 0)
    cx, cy = centre
    r = 2 * max(size)
    pts = ([(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r)] if keep == "ne"
           else [(cx - r, cy - r), (cx - r, cy + r), (cx + r, cy + r)])
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="measure only, write nothing")
    args = ap.parse_args()

    # ---- the deck ---------------------------------------------------------
    deck = key_out(Image.open(os.path.join(CONCEPT, "v3-around-hole.png")))
    box = content_box(deck)
    print("deck content %dx%d" % (box[2] - box[0], box[3] - box[1]))

    cx, cy, rx, ry, npx = find_shaft(deck)
    print("  shaft found: centre (%d,%d) rx %d ry %d  aspect %.3f  (%d px)"
          % (cx, cy, rx, ry, rx / max(ry, 1), npx))
    fit = (1.0, cx, cy, rx, ry)

    # ---- the lid ----------------------------------------------------------
    lid = key_out(Image.open(os.path.join(CONCEPT, "v3-lid.png")))
    lb = content_box(lid)
    lw, lh = lb[2] - lb[0], lb[3] - lb[1]
    scale = (lw / MOUTH_ASPECT) / lh
    print("lid content %dx%d aspect %.3f -> vertical x%.4f" % (lw, lh, lw / lh, scale))

    if args.check:
        return

    # Scale the lid to vanilla's aspect, on its own canvas, then trim.
    lid = lid.resize((lid.width, max(1, int(round(lid.height * scale)))), Image.LANCZOS)
    lid = lid.crop(content_box(lid))
    print("  lid scaled to %dx%d, aspect %.3f" % (lid.width, lid.height, lid.width / lid.height))

    # The lid has to sit on the deck's shaft. Both are cut to their own content,
    # so the deck's fitted ellipse is what says where -- resize the lid to that
    # ellipse and place its centre there.
    # A few per cent proud of the opening, so the lid tucks under the ring rather
    # than butting against it. Measured at exactly the opening's size it covered
    # 87% and left a hairline of ring showing all the way round -- a door that
    # only just reaches its frame does not read as closed.
    overlap = 1.07
    target_w = int(fit[3] * 2 * overlap)
    target_h = int(fit[4] * 2 * overlap)
    lid = lid.resize((target_w, target_h), Image.LANCZOS)

    canvas = Image.new("RGBA", deck.size, (0, 0, 0, 0))
    canvas.alpha_composite(lid, (fit[1] - target_w // 2, fit[2] - target_h // 2))

    # ---- cut the shaft out of the deck ------------------------------------
    # Vanilla's pixels live inside the fitted ellipse. Removing them is both the
    # licensing requirement and the ring the engine needs.
    hole = Image.new("L", deck.size, 0)
    ImageDraw.Draw(hole).ellipse(
        (fit[1] - fit[3], fit[2] - fit[4], fit[1] + fit[3], fit[2] + fit[4]), fill=255)
    hole = hole.filter(ImageFilter.GaussianBlur(1.2))
    ring = deck.copy()
    ring.putalpha(ImageChops.subtract(deck.getchannel("A"), hole))

    # Scale: the deck fits inside its footprint, and does not overhang it.
    #
    # Vanilla does overhang -- the rocket silo is 628 x 612 at scale 0.5, which
    # is 9.81 x 9.56 tiles on a 9 x 9 collision box, 9% proud -- and this tool
    # used to copy that. Liam rejected it on the r4 deck at 9.65 x 9.42: art that
    # spills past its own square overlaps whatever is built beside it, and
    # "slightly" is still overlapping. So the width is the footprint exactly.
    #
    # An earlier round argued the other way, because drawn to 9 tiles the v3 deck
    # came out 9.00 x 7.78 and read as small and cut off inside its square. That
    # was the old art's aspect, not the rule: v3 was far too flat. r4 is 1000 x
    # 976, so 9 tiles wide is 8.79 tall and the footprint is properly filled.
    deck_w = box[2] - box[0]
    tiles_wide = FOOTPRINT_TILES
    scale = tiles_wide * 32.0 / deck_w
    px_per_tile = 32.0 / scale
    tiles_high = (box[3] - box[1]) * scale / 32
    print("\ndeck %d px -> %.2f x %.2f tiles on a %d-tile footprint, scale = %.4f"
          % (deck_w, tiles_wide, tiles_high, FOOTPRINT_TILES, scale))
    if tiles_wide > FOOTPRINT_TILES or tiles_high > FOOTPRINT_TILES:
        raise SystemExit("deck overhangs its footprint")

    print("\nplates:")
    emit(ring, "base.png", px_per_tile)

    for keep, name in (("ne", "door-back.png"), ("sw", "door-front.png")):
        half = canvas.copy()
        half.putalpha(ImageChops.multiply(
            canvas.getchannel("A"), seam_half(canvas.size, (fit[1], fit[2]), keep)))
        emit(half, name, px_per_tile)

    # Keep the recombined lid too: it is the source the two halves came from, and
    # the thing to re-cut if the seam angle ever changes.
    canvas.save(os.path.join(CONCEPT, "v3-lid-placed.png"))
    print("\nvanilla shaft pixels removed from base.png -- none ship.")


if __name__ == "__main__":
    main()
