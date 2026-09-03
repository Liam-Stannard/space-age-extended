#!/usr/bin/env python3
"""Turn AI-generated icon renders into the mod's 64px mipmapped icon strips.

Usage:
    tools/key-icons.py OUT_DIR SRC.png[:target-name] ...

For each source image (1024x1024 renders from an image generator):

1. If the PNG has no real alpha channel, key out the background. The
   generators we use paint a fake "transparency" checkerboard (two greys on a
   regular grid) or a flat white sheet straight into the pixels. The checker
   grid's period, phase and two colours are recovered from the border band,
   an expected-background image is built, and every pixel is compared against
   it: matches become transparent, shadows (darker, unsaturated) become a
   black layer at the shadow's own strength, anti-aliased edges are un-mixed,
   and anything not reachable from the border through background-like pixels
   is forced opaque (so grey parts of a grey object survive).
2. Crop to the opaque bounding box plus a small margin, square, and
   downsample to 64x64.
3. Bake the 120x64 mipmap strip (64/32/16/8 packed left to right) the repo's
   icons already use with `icon_mipmaps = 4`.

Also writes a keyed 1024px master next to the strip under OUT_DIR/masters/
so the keying can be judged at full size. Pillow only, no numpy.
"""

import os
import sys
from PIL import Image, ImageDraw

MIP_SIZES = (64, 32, 16, 8)
BORDER = 28          # px band around the edge assumed to be pure background
EDGE_LO, EDGE_HI = 10, 80   # colour distance from expected background -> alpha ramp
BG_ALPHA_CUT = 0.35  # flood fill treats pixels below this alpha as background
MARGIN = 0.07        # padding around the object as a fraction of its size
SOLID_ALPHA = 235    # premultiplied sources leave the body just under opaque


def luminance(p):
    return (p[0] * 299 + p[1] * 587 + p[2] * 114) // 1000


def saturation(p):
    return max(p[:3]) - min(p[:3])


def estimate_background(im):
    """The two background colours (a checker's two greys, or a flat sheet
    twice), from the border band. The generators' checkers drift off a true
    grid across 1024px, so no geometry is assumed: each pixel is later judged
    against whichever of the two colours it is nearer to."""
    w, h = im.size
    px = im.load()
    band = [px[x, y][:3] for y in range(h) for x in range(w)
            if x < BORDER or y < BORDER or x >= w - BORDER or y >= h - BORDER]
    lums = sorted(luminance(p) for p in band)
    lo, hi = lums[len(lums) // 10], lums[len(lums) * 9 // 10]
    mid = (lo + hi) // 2
    dark = [p for p in band if luminance(p) <= mid]
    light = [p for p in band if luminance(p) > mid]

    def median(pts):
        return tuple(sorted(c[i] for c in pts)[len(pts) // 2] for i in range(3))

    a = median(dark) if dark else median(light)
    b = median(light) if light else a
    return a, b


def key_background(im):
    w, h = im.size
    src = im.load()
    a_col, b_col = estimate_background(im)
    desc = "bg %s / %s" % (a_col, b_col)
    lum_a, lum_b = sorted((luminance(a_col), luminance(b_col)))
    checker = lum_b - lum_a > 8

    def dist(p, c):
        return max(abs(p[i] - c[i]) for i in range(3))

    # Pass 1: which background colour each pixel is nearest, and whether it
    # matches it outright. cls: 0 = matches A, 1 = matches B, 2 = neither.
    cls = [[2] * w for _ in range(h)]
    near = [[None] * w for _ in range(h)]
    for y in range(h):
        row_c, row_n, = cls[y], near[y]
        for x in range(w):
            p = src[x, y]
            da, db = dist(p, a_col), dist(p, b_col)
            if da <= db:
                row_n[x] = a_col
                if da <= EDGE_LO:
                    row_c[x] = 0
            else:
                row_n[x] = b_col
                if db <= EDGE_LO:
                    row_c[x] = 1

    # Pass 2 (checkers only): the blurred 1px seam between two squares is an
    # in-between grey touching both colours. Two sweeps so seam crossings
    # (which touch a seam pixel rather than both colours) get picked up too.
    seam = set()
    if checker:
        for _ in range(2):
            for y in range(1, h - 1):
                for x in range(1, w - 1):
                    if cls[y][x] != 2 or (x, y) in seam:
                        continue
                    p = src[x, y]
                    if saturation(p) > 24 or not (lum_a - 6 <= luminance(p) <= lum_b + 6):
                        continue
                    nb = [cls[y - 1][x], cls[y + 1][x], cls[y][x - 1], cls[y][x + 1]]
                    nbs = [(x, y - 1) in seam, (x, y + 1) in seam, (x - 1, y) in seam, (x + 1, y) in seam]
                    if (0 in nb and 1 in nb) or (any(nbs) and (0 in nb or 1 in nb)):
                        seam.add((x, y))

    out = Image.new("RGBA", im.size)
    dst = out.load()
    mask = Image.new("L", im.size, 0)
    mpx = mask.load()
    for y in range(h):
        for x in range(w):
            p = src[x, y]
            if cls[y][x] != 2 or (x, y) in seam:
                dst[x, y] = (0, 0, 0, 0)
                mpx[x, y] = 255
                continue
            e = near[y][x]
            d = dist(p, e)
            darker = all(p[i] <= e[i] + 6 for i in range(3))
            if darker and saturation(p) <= 14:
                # Shadow model: pixel = background * (1 - s). Black at alpha s.
                ratios = [p[i] / max(e[i], 8) for i in range(3)]
                a = max(0.0, min(1.0, 1.0 - sum(ratios) / 3.0))
                dst[x, y] = (0, 0, 0, int(round(a * 255)))
            else:
                a = max(0.0, min(1.0, (d - EDGE_LO) / float(EDGE_HI - EDGE_LO)))
                if a >= 1.0:
                    dst[x, y] = (p[0], p[1], p[2], 255)
                else:
                    # Un-mix the object colour from the background it was blended over.
                    c = tuple(int(max(0, min(255, (p[i] - (1 - a) * e[i]) / a))) for i in range(3))
                    dst[x, y] = c + (int(round(a * 255)),)
            if a < BG_ALPHA_CUT:
                mpx[x, y] = 255

    # Everything background-like but NOT reachable from the border is object interior.
    fill = mask.copy()
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if fill.getpixel(seed) == 255:
            ImageDraw.floodfill(fill, seed, 128)
    fpx = fill.load()
    forced = 0
    for y in range(h):
        for x in range(w):
            if fpx[x, y] == 255:
                p = src[x, y]
                dst[x, y] = (p[0], p[1], p[2], 255)
                forced += 1
    # Drop floating islands: checker squares whose grey drifted past the
    # tolerance survive as small opaque blocks away from the object. Keep only
    # what is connected (through any non-zero alpha) to the largest blob.
    alpha = out.getchannel("A").point(lambda a: 255 if a > 0 else 0)
    labels = alpha.copy()
    lpx = labels.load()
    best, best_seed = 0, None
    for y in range(0, h, 4):
        for x in range(0, w, 4):
            if lpx[x, y] == 255:
                ImageDraw.floodfill(labels, (x, y), 128)
                size = labels.histogram()[128]
                ImageDraw.floodfill(labels, (x, y), 64)
                if size > best:
                    best, best_seed = size, (x, y)
    if best_seed:
        keep = alpha.copy()
        ImageDraw.floodfill(keep, best_seed, 128)
        kpx = keep.load()
        dropped = 0
        for y in range(h):
            for x in range(w):
                if kpx[x, y] == 255:
                    dst[x, y] = (0, 0, 0, 0)
                    dropped += 1
        desc += " islands-dropped=%d" % dropped
    return out, desc, forced


def unpremultiply(im):
    """Some background-removal tools return premultiplied alpha (RGB already
    scaled by coverage, so nothing is brighter than its own alpha). Factorio
    expects straight alpha, so premultiplied art loads dark and washed out.
    Detected by "no pixel's colour exceeds its alpha", then divided back out.
    Alpha at or above SOLID_ALPHA is snapped to opaque, since these tools tend
    to leave the whole object one or two steps below 255."""
    w, h = im.size
    px = im.load()
    checked = violations = 0
    for y in range(0, h, 3):
        for x in range(0, w, 3):
            r, g, b, a = px[x, y]
            if 0 < a < 255:
                checked += 1
                if max(r, g, b) > a + 2:
                    violations += 1
    if checked < 200 or violations > checked * 0.01:
        return im, False
    out = Image.new("RGBA", im.size)
    dst = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                dst[x, y] = (0, 0, 0, 0)
            else:
                f = 255.0 / a
                dst[x, y] = (min(255, int(r * f + 0.5)), min(255, int(g * f + 0.5)),
                             min(255, int(b * f + 0.5)), 255 if a >= SOLID_ALPHA else a)
    return out, True


def crop_square(im):
    bbox = im.getchannel("A").point(lambda a: 255 if a > 12 else 0).getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    side = max(x1 - x0, y1 - y0)
    side = int(side * (1 + 2 * MARGIN))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    box = (cx - side // 2, cy - side // 2, cx - side // 2 + side, cy - side // 2 + side)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, (-box[0], -box[1]))
    return canvas


def mip_strip(icon64):
    strip = Image.new("RGBA", (sum(MIP_SIZES), MIP_SIZES[0]), (0, 0, 0, 0))
    x = 0
    for s in MIP_SIZES:
        strip.paste(icon64.resize((s, s), Image.LANCZOS), (x, 0))
        x += s
    return strip


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    out_dir = argv[1]
    os.makedirs(os.path.join(out_dir, "masters"), exist_ok=True)
    for spec in argv[2:]:
        src, _, name = spec.partition(":")
        if not name:
            name = os.path.splitext(os.path.basename(src))[0]
        im = Image.open(src).convert("RGBA")
        lo, hi = im.getchannel("A").getextrema()
        if lo == 255:
            keyed, desc, forced = key_background(im)
        else:
            keyed, premul = unpremultiply(im)
            desc = "alpha, un-premultiplied" if premul else "alpha, straight"
            forced = 0
        for sub in ("", "masters"):
            os.makedirs(os.path.dirname(os.path.join(out_dir, sub, name + ".png")), exist_ok=True)
        keyed.save(os.path.join(out_dir, "masters", name + ".png"))
        icon = crop_square(keyed).resize((64, 64), Image.LANCZOS)
        mip_strip(icon).save(os.path.join(out_dir, name + ".png"))
        print("%-32s %-40s interior-forced=%d" % (name, desc, forced))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
