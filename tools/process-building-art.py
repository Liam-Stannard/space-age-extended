#!/usr/bin/env python3
"""Turn an approved concept PNG into Factorio sprite plates.

A generator produces a picture; Factorio wants a sprite of an exact size whose
features land on exact pixel rows (see building-spec-<name>.md sections 12 and
13). This does the mechanical half of that: trim, scale, place on the sprite
canvas, and derive a separate draw_as_shadow plate.

It does NOT invent art. The colour plate it writes is the concept, resized and
positioned; anything the spec says must be repainted -- a baked shadow left in
the colour layer, scorch that needs separating -- is still a manual step, and
--report tells you whether that is needed.

Usage:
  tools/process-building-art.py <concept.png> --out-dir graphics/entity/arc-mast \\
      --name arc-mast --width 224 --height 448 --top-margin 25 --tip-row 53
  tools/process-building-art.py <concept.png> --report
"""

import argparse
import os
import statistics
import sys

from PIL import Image, ImageFilter


def dekey_checkerboard(im, tol=10):
    """Restore alpha on a plate that was flattened onto a grey checkerboard.

    ChatGPT's image editor exports edited images composited onto its
    transparency checkerboard, so the PNG arrives fully opaque with the
    pattern baked in. The pattern is two neutral greys; the building is not
    neutral. Flood fill inward from the border over neutral-grey pixels so
    light-but-chromatic parts (the ceramic discs) are never punched through.
    """
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()

    # Read the two greys off the border rather than assuming them. A single
    # bright-neutral floor (>= 195) was enough for the arc mast, whose exports
    # came back on a light checkerboard; the superconducting store's arrived on
    # a 199/141 pair and the floor cleared 1% of the frame. The pattern's
    # period is fractional -- 1254 px over 160 squares -- so reconstructing the
    # grid drifts; matching the two values it is actually made of does not.
    band = []
    for x in range(0, w, 2):
        band += [px[x, 1], px[x, h - 2]]
    for y in range(0, h, 2):
        band += [px[1, y], px[w - 2, y]]
    # Take the two commonest neutral values, not the min and max: the border
    # can carry a stray dark pixel, and widening the window down to it would
    # clear every neutral grey in the building too.
    hist = {}
    for p in band:
        if max(p[:3]) - min(p[:3]) <= 6:
            v = round(sum(p[:3]) / 3)
            hist[v] = hist.get(v, 0) + 1
    peaks = sorted(hist, key=hist.get, reverse=True)
    modes = []
    for v in peaks:                      # two clusters, not two adjacent values
        if all(abs(v - m) > 3 * tol for m in modes):
            modes.append(v)
        if len(modes) == 2:
            break
    lo, hi = (min(modes), max(modes)) if len(modes) == 2 else \
             (peaks[0], peaks[0]) if peaks else (199, 199)

    def neutral(p):
        if p[3] == 0:
            return True          # already cleared: the fill must pass through
        r, g, b = p[0], p[1], p[2]
        if abs(r - g) > 6 or abs(g - b) > 6 or abs(r - b) > 6:
            return False
        # Either checkerboard grey, or any blend between them -- the squares'
        # own boundaries are anti-aliased, and a two-window test misses those.
        return lo - tol <= (r + g + b) / 3 <= hi + tol

    seen = bytearray(w * h)
    stack = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)]
    stack += [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y * w + x]:
            continue
        if not neutral(px[x, y]):
            continue
        seen[y * w + x] = 1
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

    for y in range(h):
        row = y * w
        for x in range(w):
            if seen[row + x]:
                px[x, y] = (0, 0, 0, 0)

    # The squares are anti-aliased against each other, so their boundaries land
    # outside both grey windows and survive the fill as a fine speckle across
    # the whole frame -- dense enough that solid_bbox() read it as content and
    # trimmed the store's plate to 1247x1254 of a 1254 canvas, i.e. not at all.
    # Everything that is really the building is one connected mass, so keep that
    # and drop the rest.
    keep = bytearray(w * h)
    best, best_n = None, 0
    for sy in range(h):
        for sx in range(w):
            i0 = sy * w + sx
            if keep[i0] or px[sx, sy][3] == 0:
                continue
            comp, stack, n = [], [(sx, sy)], 0
            keep[i0] = 1
            while stack:
                x, y = stack.pop()
                comp.append(y * w + x)
                n += 1
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h:
                        j = ny * w + nx
                        if not keep[j] and px[nx, ny][3] != 0:
                            keep[j] = 1
                            stack.append((nx, ny))
            if n > best_n:
                best, best_n = comp, n
    if best is not None:
        main = bytearray(w * h)
        for i in best:
            main[i] = 1
        for y in range(h):
            row = y * w
            for x in range(w):
                if px[x, y][3] != 0 and not main[row + x]:
                    px[x, y] = (0, 0, 0, 0)
    return im


def solid_bbox(im, alpha=20, min_run=8):
    """Bounding box of the content you can actually see.

    `getbbox()` answers "any pixel with any alpha at all", and a generator's
    output is not that clean: v11-idle.png carries 95 columns of fringe down its
    right side holding a single speck above alpha 20 and nothing else. Cropping
    to that squeezed the visible mast into 814/909 of its canvas and pushed it
    hard against the left edge, where the foot pad was cut off mid-bolt at alpha
    255 and the whole building drew 0.18 tiles left of its own tile.

    So require a row or column to carry `min_run` pixels above `alpha` before it
    counts as content. Thin real geometry is safe -- min_run is under 1% of a
    plate's height -- and specks are not.
    """
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    a = im.getchannel("A")
    w, h = a.size
    px = a.load()
    cols = [x for x in range(w)
            if sum(1 for y in range(h) if px[x, y] > alpha) >= min_run]
    rows = [y for y in range(h)
            if sum(1 for x in range(w) if px[x, y] > alpha) >= min_run]
    if not cols or not rows:
        return None
    return (cols[0], rows[0], cols[-1] + 1, rows[-1] + 1)


def trimmed(im):
    """Crop to the visible content, warning if that differs from the raw box."""
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    box = solid_bbox(im)
    if not box:
        sys.exit("the image is fully transparent -- nothing to process")
    raw = im.getchannel("A").getbbox()
    slack = max(abs(box[i] - raw[i]) for i in range(4))
    if slack > 4:
        print(f"  note  trimmed on visible content, not raw alpha: "
              f"{raw[2] - raw[0]}x{raw[3] - raw[1]} -> "
              f"{box[2] - box[0]}x{box[3] - box[1]} ({slack} px of fringe)")
    return im.crop(box)


def alpha_split(im):
    """Fractions of the frame that are clear, partial and opaque."""
    h = im.getchannel("A").histogram()
    n = im.width * im.height
    return h[0] / n, sum(h[1:251]) / n, sum(h[251:]) / n


def body_metal(im):
    """Median colour of the body, ignoring darkest 30% and brightest 15%.

    Judging palette by eye off a preview does not work: these plates are
    transparent, so every viewer composites them onto its own background and
    the apparent value of the metal moves with it. Measure instead.
    """
    px = [p for p in im.getdata() if p[3] > 200]
    if not px:
        return None, None
    lum = sorted((0.2126 * r + 0.7152 * g + 0.0722 * b, (r, g, b))
                 for r, g, b, _ in px)
    body = [c for _, c in lum[int(len(lum) * 0.30):int(len(lum) * 0.85)]]
    med = tuple(statistics.median(c[i] for c in body) for i in range(3))
    return med, 0.2126 * med[0] + 0.7152 * med[1] + 0.0722 * med[2]


def stretch_y(im, factor):
    """Resample the plate taller, to deepen a camera that came back too flat.

    Not a substitute for asking again -- three rounds of asking got the
    superconducting store from 1:0.61 to 1:0.96 and then stopped moving, with
    the target at 1:1.10. The residual is a uniform vertical under-scale of the
    whole projection, so the inverse is a uniform vertical resample, and at the
    5-15% these plates need it is invisible on the details: a bolt block on a
    2x2 building is a handful of pixels across in game.

    Record the factor in the spec's section 13. A plate that needed more than
    about 1.2 here should have been regenerated instead -- past that the drum
    stops reading as round and the frost runs visibly downhill.
    """
    return im.resize((im.width, max(1, round(im.height * factor))), Image.LANCZOS)


def place(im, width, height, top_margin, bottom_margin=0):
    """Scale to fit the canvas between the margins, then centre horizontally.

    bottom_margin exists so the cut plate can satisfy the pipeline's second
    geometry check -- alpha zero along *both* edge rows. Without it the art
    lands flush against the canvas floor, which ends the building on a razor
    line with no antialiased rim; the arc mast shipped that way.
    """
    target_h = height - top_margin - bottom_margin
    scale = target_h / im.height
    if im.width * scale > width:
        scale = width / im.width
    new = im.resize((max(1, round(im.width * scale)),
                     max(1, round(im.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas.paste(new, ((width - new.width) // 2, top_margin), new)
    return canvas


def shadow(colour, kx=0.79, ky=0.25, blur=3.5, opacity=155):
    """Project a building's silhouette onto the ground as a cast shadow.

    The shadow lies flat, anchored at the foot: a pixel `up` rows above the
    object's base is `up` units up the building, so on the ground it lands
    `up*kx` to the right and `up*ky` *further up the screen* -- away from the
    camera, not down it. Keeping the pixel's own row instead only squashes the
    silhouette, which is what the first arc-mast plate did: 4.1 tiles of
    standing shadow rather than the flat smear Factorio draws.

    kx and ky are measured off vanilla's lightning collector, whose shadow
    reaches 0.79 of the building's height to the right and 0.25 of it upward.

    The plate needs its own canvas and its own shift -- both returned here so
    nothing has to be guessed downstream. Only the width grows; leaning upward
    means the shadow never needs rows the colour plate does not already have.
    """
    a = colour.getchannel("A")
    w, h = a.size
    foot = a.getbbox()[3] - 1                      # last row the object touches
    dx, dy = round(foot * kx), 0

    canvas = Image.new("L", (w + dx, h + dy), 0)
    src, dst = a.load(), canvas.load()
    for y in range(h):
        up = foot - y
        if up < 0:
            continue
        ox, oy = round(up * kx), round(up * ky)
        for x in range(w):
            v = src[x, y]
            if v > 8:
                px, py = x + ox, foot - oy
                if px < canvas.width and 0 <= py < canvas.height and v > dst[px, py]:
                    dst[px, py] = v

    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    # Normalise against the actual peak, not 255. The blur spreads a projection
    # that stacks hundreds of source rows onto a few dozen, so the raw peak is
    # nowhere near 255 and scaling against it makes `opacity` a ceiling the
    # plate never reaches.
    peak = canvas.getextrema()[1] or 255
    canvas = canvas.point(lambda p: min(opacity, round(p * opacity / peak)))
    # One flat colour, alpha carries the shape -- the same shape vanilla's
    # shadow PNGs have. Compositing this over a transparent plate *through its
    # own alpha* would square it, which is what left the first arc-mast shadow
    # at alpha 94 out of the 155 asked for: invisible against Core basalt.
    plate = Image.new("RGBA", canvas.size, (16, 15, 14, 0))
    plate.putalpha(canvas)
    return plate, dx, dy


def report(im, path, tip_row, tolerance, target=("4A463F", "6E685C")):
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    t = trimmed(im)
    clear, partial, opaque = alpha_split(im)
    med, lum = body_metal(im)

    print(f"{os.path.basename(path)}")
    print(f"  size            {im.width}×{im.height}")
    print(f"  alpha           {clear:.0%} clear · {partial:.0%} partial · "
          f"{opaque:.0%} opaque")
    if clear < 0.02:
        print("  REJECT          no transparency -- the background is painted")
    else:
        print("  transparency    ok")
    print(f"  aspect          1:{t.height / t.width:.2f}  (trimmed "
          f"{t.width}×{t.height})")
    if med:
        print(f"  body metal      #{int(med[0]):02X}{int(med[1]):02X}"
              f"{int(med[2]):02X}  luminance {lum:.0f}  warmth R-B "
              f"{med[0] - med[2]:+.0f}")
        lo, hi = (sum(c * w for c, w in zip(
            (int(h[i:i + 2], 16) for i in (0, 2, 4)),
            (0.2126, 0.7152, 0.0722))) for h in target)
        if lum < lo - 4:
            print(f"  WARNING         darker than the palette floor "
                  f"(#{target[0]}, luminance {lo:.0f}) -- do not ask for more")
        elif lum > hi + 4:
            print(f"  WARNING         lighter than the palette ceiling "
                  f"(#{target[1]}, luminance {hi:.0f})")
        else:
            print(f"  palette         within #{target[0]}–#{target[1]}")
    band = t.crop((0, 0, t.width, max(1, t.height // 8)))
    print(f"  tip band        {band.height} px tall; target row {tip_row} "
          f"± {tolerance} on the sprite canvas")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("concept")
    ap.add_argument("--out-dir")
    ap.add_argument("--name")
    ap.add_argument("--width", type=int, default=224)
    ap.add_argument("--height", type=int, default=448)
    ap.add_argument("--top-margin", type=int, default=25)
    ap.add_argument("--stretch-y", type=float, default=1.0,
                    help="resample the plate this much taller before cutting, "
                         "to correct a camera that came back too shallow")
    ap.add_argument("--bottom-margin", type=int, default=0,
                    help="clear rows to leave under the art, so the plate has "
                         "an antialiased rim rather than a razor-cut floor")
    ap.add_argument("--tip-row", type=int, default=53)
    ap.add_argument("--tolerance", type=int, default=4)
    ap.add_argument("--shift-y", type=float, default=-81.0,
                    help="the colour plate's y shift in in-game px, so the "
                         "shadow's own shift can be derived from it")
    ap.add_argument("--report", action="store_true",
                    help="inspect the concept and exit")
    ap.add_argument("--dekey", action="store_true",
                    help="restore alpha on a plate flattened onto a checkerboard")
    args = ap.parse_args()

    im = Image.open(args.concept)
    if args.dekey:
        im = dekey_checkerboard(im)
        if not args.report:
            im.save(args.concept)
            print(f"  ok  de-keyed {args.concept}")
    if args.report:
        report(im, args.concept, args.tip_row, args.tolerance)
        return

    if not args.out_dir or not args.name:
        sys.exit("--out-dir and --name are required unless --report")

    art = trimmed(im)
    if args.stretch_y != 1.0:
        art = stretch_y(art, args.stretch_y)
        print(f"  note  stretched {args.stretch_y:g}x vertically: "
              f"aspect 1:{art.height / art.width:.2f}")
    colour = place(art, args.width, args.height, args.top_margin,
                   args.bottom_margin)
    os.makedirs(args.out_dir, exist_ok=True)
    cpath = os.path.join(args.out_dir, f"{args.name}.png")
    spath = os.path.join(args.out_dir, f"{args.name}-shadow.png")
    colour.save(cpath)
    plate, dx, dy = shadow(colour)
    plate.save(spath)

    # Both plates are drawn at scale 0.5, so source px halve into in-game px.
    # The colour plate's centre is args.shift_y in-game px from the origin; the
    # shadow canvas is dx wider and dy taller, anchored top-left with it, so its
    # centre sits dx/2 right and dy/2 below the colour plate's centre.
    sx = (dx / 2) / 2 / 32
    sy = (args.shift_y + (dy / 2) / 2) / 32
    print(f"  ok  {cpath}  {args.width}×{args.height}")
    print(f"  ok  {spath}  {plate.width}×{plate.height}  cast shadow")
    print(f"      shadow shift = {{ {sx:.5f}, {sy:.5f} }}  "
          f"(colour plate shift {{ 0, {args.shift_y/32:.5f} }})")


if __name__ == "__main__":
    main()
