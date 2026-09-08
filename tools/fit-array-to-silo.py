#!/usr/bin/env python3
"""Render the Ignition Array's art into the rocket silo's own sprite slots.

Liam's suggestion, and it is a better idea than what it replaces. Deriving each
plate's size, scale and shift independently -- from its own content, its own
centroid, its own measured ellipse -- gives five numbers that are each defensible
and collectively wrong, because nothing ties them to one another. The doors
stopped closing over the hole and the lid stopped reading as a circle.

Vanilla already solved this. Its five slots are mutually consistent by
construction: two leaves resting 2.031 tiles apart in x and 0.656 in y, closing
over a hole at (-0.15625, +0.5), under a deck at (0.0625, +0.109). The engine
slides those leaves apart over 255 ticks and they clear the hole exactly, because
Wube placed them that way. Copy the geometry and all of that comes free.

So the anchor is vanilla's hole. Our opening is mapped onto it -- 6.25 x 4.22
tiles at vanilla's own shift -- and every plate is then resampled into vanilla's
canvas at vanilla's shift and scale. Nothing is positioned by measurement any
more; one affine transform carries everything.

The consequence worth stating: our deck lands at 9.01 tiles wide against
vanilla's 9.81, because our ring is proportionally thinner around a mouth of the
same size. That is the design -- v3 exists to be mostly shaft -- and 9.01 on a
9-tile footprint is right, where vanilla's 9.81 overhangs.
"""

import os

from PIL import Image, ImageFilter

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "graphics", "entity", "ignition-array")
CONCEPT = os.path.join(ART, "concept")

# Vanilla's slots, read off the rocket-silo prototype. Size, shift in tiles, and
# scale -- these are what make the doors close and part correctly.
SILO = {
    "base":       ((628, 612), (0.0625, 0.109375)),
    "shadow":     ((656, 600), (0.625, -0.125)),
    "hole":       ((400, 270), (-0.15625, 0.5)),
    "door_back":  ((312, 286), (1.15625, 0.375)),
    "door_front": ((332, 300), (-0.875, 1.03125)),
}
SCALE = 0.5
PX_PER_TILE = 32 / SCALE          # 64: a sprite pixel is 1/64 tile at scale 0.5

# Where our opening sits on the concept canvas, and how big it is. The centre is
# measured off the render's dark floor; the size is vanilla's, because that is
# what the whole v3 design was built around.
SRC_CX, SRC_CY = 704, 580
SRC_RX = 431                       # canvas px for vanilla's 3.125-tile half-width
TILES_PER_PX = 3.125 / SRC_RX


def to_slot(src, slot):
    """Resample source-canvas art into one of vanilla's plates.

    A single affine map does the whole job: plate pixel -> tile -> source pixel.
    Because every plate uses the same map, they cannot drift apart -- which is
    the failure this function exists to remove.
    """
    (w, h), (sx, sy) = SILO[slot]
    a = (1.0 / PX_PER_TILE) / TILES_PER_PX
    c = SRC_CX + (sx - (w / 2) / PX_PER_TILE + 0.15625) / TILES_PER_PX
    f = SRC_CY + (sy - (h / 2) / PX_PER_TILE - 0.5) / TILES_PER_PX
    return src.transform((w, h), Image.AFFINE, (a, 0, c, 0, a, f),
                         resample=Image.BICUBIC)


def report(name, slot):
    (w, h), (sx, sy) = SILO[slot]
    print("  %-18s width = %d, height = %d, shift = { %s, %s }, scale = 0.5"
          % (name, w, h, sx, sy))


def main():
    src_deck = Image.open(os.path.join(ART, "base.png")).convert("RGBA")
    # base.png is already the holed ring, but cropped to its content. Put it back
    # on the concept canvas so the affine map's coordinates mean what they say.
    canvas_size = Image.open(os.path.join(CONCEPT, "v3-around-hole.png")).size
    def recentre(img, shift_tiles, px_per_tile):
        c = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        x = int(canvas_size[0] / 2 + shift_tiles[0] * px_per_tile - img.width / 2)
        y = int(canvas_size[1] / 2 + shift_tiles[1] * px_per_tile - img.height / 2)
        c.alpha_composite(img, (x, y))
        return c

    PPT = 126.75                    # what the previous pass emitted shifts in
    deck = recentre(src_deck, (0.01184, -0.11052), PPT)
    db = recentre(Image.open(os.path.join(ART, "door-back.png")).convert("RGBA"),
                  (0.85257, -0.07894), PPT)
    df = recentre(Image.open(os.path.join(ART, "door-front.png")).convert("RGBA"),
                  (-0.71443, 0.29998), PPT)
    hole = recentre(Image.open(os.path.join(ART, "hole.png")).convert("RGBA"),
                    (0.07495, 0.11440), PPT)

    print("into vanilla's slots:")
    to_slot(deck, "base").save(os.path.join(ART, "base.png"))
    report("base.png", "base")

    to_slot(hole, "hole").save(os.path.join(ART, "hole.png"))
    report("hole.png", "hole")

    to_slot(db, "door_back").save(os.path.join(ART, "door-back.png"))
    report("door-back.png", "door_back")

    to_slot(df, "door_front").save(os.path.join(ART, "door-front.png"))
    report("door-front.png", "door_front")

    # The shadow is derived from the deck as it now sits in its slot, sheared the
    # way vanilla lays one on the ground.
    base_slot = to_slot(deck, "base")
    a = base_slot.getchannel("A")
    sh = Image.new("L", SILO["shadow"][0], 0)
    sh.paste(a, (0, 0))
    sh = sh.transform(sh.size, Image.AFFINE, (1, -0.55, 0.55 * sh.height, 0, 1, 0),
                      resample=Image.BILINEAR)
    sh = sh.filter(ImageFilter.GaussianBlur(4)).point(lambda v: min(255, int(v * 0.8)))
    shadow = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    shadow.putalpha(sh)
    shadow.save(os.path.join(ART, "base-shadow.png"))
    report("base-shadow.png", "shadow")

    dw = base_slot.getchannel("A").point(lambda v: 255 if v > 60 else 0).getbbox()
    print("\ndeck draws %.2f x %.2f tiles (vanilla silo 9.81 x 9.56, footprint 9)"
          % ((dw[2] - dw[0]) / PX_PER_TILE, (dw[3] - dw[1]) / PX_PER_TILE))


if __name__ == "__main__":
    main()
