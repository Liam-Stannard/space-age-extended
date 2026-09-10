#!/usr/bin/env python3
"""Split a lit plate into an unlit base and its additive glow layer, by colour.

The pipeline's first choice for a glow is differencing a lit render against an
unlit twin -- `derive-glow.py` -- because the difference *is* the light and it
registers by construction. That needs two renders of the same machine that have
not moved, and the image editor does not always give you one: the
superconducting store's lit twin came back pixel-identical to the unlit plate
five rounds running.

This is the other way round, and it needs only one render. Ask for the machine
**lit**, then take the light back out by colour: the emissive parts of these
designs are all strongly chromatic against bodywork that is deliberately
near-neutral iron-nickel, so a hue window separates them cleanly. What comes out
is a glow layer holding exactly the lit pixels, and a base plate with those
pixels filled to the recess tone around them -- a slot that is dark rather than
a slot with a hole in it.

Registration is exact for the same reason `ring-glow.py`'s is: both layers are
cut from one image, on one canvas, so nothing can drift.

When to use which. Differencing is better when the light spills widely and
subtly, because it recovers the spill too. This is better when the light is a
small bright feature in a known colour -- a slot, a lamp, a channel -- and when
the lit twin will not come.

Usage:
  tools/split-glow.py lit.png --base base.png --glow glow.png \\
      --hue 120 --hue-width 60 --min-saturation 0.20
"""

import argparse
import colorsys
import statistics

from PIL import Image, ImageChops, ImageFilter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plate")
    ap.add_argument("--base", required=True, help="where to write the unlit plate")
    ap.add_argument("--glow", required=True, help="where to write the glow layer")
    ap.add_argument("--hue", type=float, required=True,
                    help="centre of the emissive hue window, in degrees")
    ap.add_argument("--hue-width", type=float, default=60.0,
                    help="full width of the hue window, in degrees")
    ap.add_argument("--min-saturation", type=float, default=0.18)
    ap.add_argument("--min-lightness", type=float, default=0.30)
    ap.add_argument("--dilate", type=int, default=2,
                    help="pixels to grow the fill by, so no lit fringe survives "
                         "in the base under the glow")
    ap.add_argument("--region", nargs=4, type=int, metavar=("X0","Y0","X1","Y1"),
                    help="split only inside this box, and leave the rest of the "
                         "plate untouched. Needed whenever the building carries "
                         "warm MATERIAL as well as warm LIGHT: the Vent Pump's "
                         "copper fittings and yellow hazard banding sit in the "
                         "same hue window as its sight port, so a whole-plate "
                         "split lifts the paint off the building along with the "
                         "glow. Measured on it: 1157 'hot' pixels across a "
                         "179x226 box when the port is 18x32.")
    ap.add_argument("--fill-darken", type=float, default=0.45,
                    help="how much darker than its surround the filled recess "
                         "is; a slot with the light off is not the same value "
                         "as the metal around it")
    args = ap.parse_args()

    im = Image.open(args.plate).convert("RGBA")
    w, h = im.size
    px = im.load()
    lo = (args.hue - args.hue_width / 2) / 360.0
    hi = (args.hue + args.hue_width / 2) / 360.0

    rx0, ry0, rx1, ry1 = args.region if args.region else (0, 0, w, h)

    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    lit = 0
    for y in range(ry0, min(ry1, h)):
        for x in range(rx0, min(rx1, w)):
            r, g, b, a = px[x, y]
            if a < 40:
                continue
            hh, ll, ss = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
            inside = (lo <= hh <= hi) if lo >= 0 else (hh >= 1 + lo or hh <= hi)
            if inside and ss >= args.min_saturation and ll >= args.min_lightness:
                mp[x, y] = 255
                lit += 1
    if not lit:
        raise SystemExit("no pixels matched that hue window -- check --hue")

    # Close the mask before using it. The bright core of an emissive slot burns
    # out to near-white, which has almost no hue and so fails the window that
    # catches its own coloured rim -- leaving the middle of every slot behind in
    # the base plate. The core is always *enclosed* by that rim, so filling the
    # holes recovers it without widening the window until pale metal qualifies.
    closed = mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
    mask = ImageChops.lighter(mask, closed)
    mp = mask.load()
    lit = sum(1 for y in range(h) for x in range(w) if mp[x, y])

    # The glow keeps a lightly softened edge so it does not end on a hard line
    # when it is drawn back over the base additively.
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow.paste(im, (0, 0), mask.filter(ImageFilter.GaussianBlur(0.6)))
    glow.save(args.glow)

    # The base fills the lit pixels with the median of the unlit metal
    # immediately around them -- the recess the light was sitting in -- rather
    # than a flat guess, so the slot still reads as a shadowed slot.
    grown = mask.filter(ImageFilter.MaxFilter(2 * args.dilate + 1))
    gp = grown.load()
    ring = [px[x, y] for y in range(h) for x in range(w)
            if gp[x, y] and not mp[x, y] and px[x, y][3] > 200]
    if ring:
        fill = tuple(int(statistics.median(c[i] for c in ring) * args.fill_darken)
                     for i in range(3))
    else:
        fill = (40, 38, 34)
    base = im.copy()
    bp = base.load()
    n = 0
    for y in range(h):
        for x in range(w):
            if gp[x, y] and px[x, y][3] > 0:
                bp[x, y] = fill + (px[x, y][3],)
                n += 1
    base.save(args.base)

    print(f"  ok  {args.glow}  {lit} lit px in hue "
          f"{args.hue - args.hue_width / 2:.0f}-{args.hue + args.hue_width / 2:.0f}")
    print(f"  ok  {args.base}  {n} px filled with #%02X%02X%02X" % fill)


if __name__ == "__main__":
    main()
