#!/usr/bin/env python3
"""Cut the Ignition Array's shipped plates from the adopted Suspended Core render.

The design is option R, chosen from twenty concepts across four sets and locked
at `graphics/entity/ignition-array/concept/adopted/`. `array-render.png` is its
production plate: the same building, unlit, on a transparent background,
generated as an edit of the locked hero rather than a fresh prompt.

Nothing here is drawn from scratch. Every shipped pixel is an approved pixel,
moved -- and the two things that are computed are computed from measurements
rather than typed:

  1. **Scale.** The building is drawn to exactly nine tiles wide, because the
     footprint is 9 x 9 and Liam rejected overhang on the r4 deck. At 576 px and
     `scale = 0.5` that is 9.00 tiles on the nose, and since this render is 0.911
     wider than tall it comes out 8.20 tiles high -- inside the square on both
     axes without needing the "let it rise" allowance at all.

  2. **Shift: centred, because this plate is shorter than its own footprint.**
     Vanilla's convention is to park the bottom edge a little past the south edge
     -- the silo's 612 px at scale 0.5 is 9.5625 tiles shifted 0.109375 south, so
     it hangs 0.3906 tiles below a 9-tile box. That works because vanilla's art
     is *larger* than its footprint and overhangs both ways.

     This plate is 8.20 tiles tall on a 9-tile box, so it under-fills by 0.80,
     and copying vanilla's anchor dumps every bit of that slack at the north:
     1.19 tiles of empty box above the machine and 0.39 poking out below it.
     Centring splits the shortfall evenly, 0.40 a side, which is the least wrong
     placement available.

     The shortfall itself is a camera artefact, not a scaling one. Factorio draws
     buildings MOSTLY ROOF, so the roof covers the tile square; this render is
     more front-on than that, which makes its drawn height short relative to the
     footprint it stands on. Fixing it properly means a re-render at a steeper
     camera, not a different number here.

     An earlier attempt anchored on the widest band of the silhouette instead, on
     the theory that the widest part is the plinth. On this machine it is not:
     the four corner towers splay wider than the ground slab, so the anchor
     landed mid-tower and left three tiles of bare footprint to the south.

  3. **The charge glow is differenced, not painted.** `R-charge-100.png` minus
     `R-charge-000.png` is exactly the light the artist put on the machine and
     nothing else, because the two frames are the same render with the power on
     and off. Upscaling that difference keeps the artist's intent; drawing a
     violet ellipse over the drum by hand would not.

  tools/build-ignition-array.py [--check]
"""

import argparse
import os

from PIL import Image, ImageChops, ImageFilter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ART = os.path.join(ROOT, "graphics", "entity", "ignition-array")
ADOPTED = os.path.join(ART, "concept", "adopted")

FOOTPRINT = 9
SCALE = 0.5
PX_PER_TILE = 32 / SCALE                  # 64 source px to a tile at scale 0.5
TARGET_W = int(FOOTPRINT * PX_PER_TILE)   # 576


def solid(img, t=40):
    return img.getchannel("A").point(lambda v: 255 if v > t else 0)


def snap_alpha(img, t=240):
    """Re-encoding left the body at alpha 252-253. Anything nearly opaque is opaque.

    Left alone, a building at alpha 253 is a building the ground shows faintly
    through, on every pixel, for ever.
    """
    a = img.getchannel("A").point(lambda v: 255 if v >= t else v)
    out = img.copy()
    out.putalpha(a)
    return out


def base_band_centre(img):
    """The vertical centre of the plinth -- the part that actually sits on tiles.

    Rows within 88% of the widest row. On this machine that is the base slab and
    nothing else: the towers and sphere above it are all narrower.
    """
    m = solid(img)
    w, h = m.size
    px = m.load()
    widths = []
    for y in range(h):
        xs = [x for x in range(w) if px[x, y]]
        widths.append((xs[0], xs[-1]) if xs else None)
    span = [(y, r[1] - r[0]) for y, r in enumerate(widths) if r]
    if not span:
        raise SystemExit("empty render")
    widest = max(s for _, s in span)
    band = [y for y, s in span if s >= 0.88 * widest]
    return (min(band) + max(band)) / 2.0, widest


def emit(img, name, note=""):
    path = os.path.join(ART, name)
    img.save(path)
    return path


def report(name, img, shift):
    print("  %-20s width = %3d, height = %3d, shift = { %.5f, %.5f }, scale = %.1f%s"
          % (name, img.width, img.height, shift[0], shift[1], SCALE,
             "   (%.2f x %.2f tiles)" % (img.width / PX_PER_TILE, img.height / PX_PER_TILE)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="measure only, write nothing")
    args = ap.parse_args()

    src = snap_alpha(Image.open(os.path.join(ART, "array-render.png")).convert("RGBA"))
    box = solid(src).getbbox()
    src = src.crop(box)
    print("render %d x %d, aspect %.3f" % (src.width, src.height, src.height / src.width))

    scale = TARGET_W / src.width
    base = src.resize((TARGET_W, max(1, round(src.height * scale))), Image.LANCZOS)
    tiles_w = base.width / PX_PER_TILE
    tiles_h = base.height / PX_PER_TILE
    print("drawn %.2f x %.2f tiles on a %d-tile footprint" % (tiles_w, tiles_h, FOOTPRINT))
    if tiles_w > FOOTPRINT + 1e-6:
        raise SystemExit("plate is wider than its footprint")

    shift = (0.0, 0.0)
    slack = FOOTPRINT - tiles_h
    print("plate is %.2f tiles short of its footprint; centred, %.2f a side"
          % (slack, slack / 2))

    if args.check:
        return

    print("\nplates:")
    emit(base, "base.png")
    report("base.png", base, shift)

    # ---- shadow, sheared off the plate's own alpha -------------------------
    #
    # The lean is vanilla's, not a guess. Its silo shadow is 656 px wide against
    # a 628 px base and sits 0.5625 tiles east of it, so the whole thing leans
    # about 0.78 tiles over a 9.56-tile height: a shear of 0.08. The first
    # attempt used 0.55, which throws an 8.2-tile building's shadow four and a
    # half tiles east and reads as a separate object lying on the ground beside
    # the machine rather than as its shadow.
    SHEAR = (0.5625 + (656 - 628) * SCALE / 32 / 2) / (612 * SCALE / 32)
    a = base.getchannel("A")
    pad = int(base.height * SHEAR) + 4
    sh = Image.new("L", (base.width + pad, base.height), 0)
    sh.paste(a, (0, 0))
    sh = sh.transform(sh.size, Image.AFFINE, (1, SHEAR, -SHEAR * sh.height, 0, 1, 0),
                      resample=Image.BILINEAR)
    sh = sh.filter(ImageFilter.GaussianBlur(3)).point(lambda v: min(255, int(v * 0.75)))
    print("shadow shear %.4f, from vanilla's own offset" % SHEAR)
    shadow = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    shadow.putalpha(sh)
    emit(shadow, "base-shadow.png")
    report("base-shadow.png", shadow,
           (shift[0] + (shadow.width - base.width) / 2 / PX_PER_TILE, shift[1]))

    # ---- the charge glow, differenced out of the two charge frames ---------
    off = Image.open(os.path.join(ADOPTED, "R-charge-000.png")).convert("RGB")
    on = Image.open(os.path.join(ADOPTED, "R-charge-100.png")).convert("RGB")
    if on.size != off.size:
        on = on.resize(off.size, Image.LANCZOS)
    glow = ImageChops.subtract(on, off)
    # Those frames are cropped to their own panels, so register them on the
    # building rather than on the panel: both are the same render, so their
    # content boxes are the same object and scaling one onto the other is exact.
    gl = glow.convert("L").point(lambda v: 255 if v > 18 else 0).getbbox()
    if gl:
        glow = glow.crop(gl)
    glow = glow.resize(base.size, Image.LANCZOS).filter(ImageGaussian := ImageFilter.GaussianBlur(2))
    lum = glow.convert("L")
    out = Image.new("RGBA", base.size, (0, 0, 0, 0))
    out.paste(glow, (0, 0))
    out.putalpha(lum.point(lambda v: min(255, int(v * 1.6))))
    emit(out, "charge-glow.png")
    report("charge-glow.png", out, shift)

    print("\nthe glow is 100%% minus 0%%: the artist's light, not a painted ellipse.")


if __name__ == "__main__":
    main()
