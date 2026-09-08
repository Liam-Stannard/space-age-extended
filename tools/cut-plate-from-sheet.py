#!/usr/bin/env python3
"""Lift a building off a concept sheet and give it a transparent background.

This exists because a generator cannot do it. Asked twice, in two different
framings, to remove the background from an approved plate and change nothing
else, it re-rendered the building both times and lost the very proportion the
plate had been approved for -- the Ignition Array's mouth went from 1.48 back to
1.13 in both attempts. An image generator can change a design or change a
presentation; it cannot hold one still while changing the other.

So the cut is done here, where it cannot drift. Nothing is redrawn: every pixel
of the building is the approved pixel.

The background is found by flooding inward from the canvas border rather than by
thresholding the whole image. That distinction is the whole trick: the shaft
inside the building is as dark as the ground outside it, and a threshold would
punch a hole straight through the lid. A flood cannot reach it, because the rim
encloses it.

  tools/cut-plate-from-sheet.py SHEET --box X0 Y0 X1 Y1 --out PLATE [--threshold N]
"""

import argparse
from collections import deque

from PIL import Image, ImageChops, ImageFilter


def luminance(p):
    return (p[0] * 299 + p[1] * 587 + p[2] * 114) // 1000


def background_mask(img, cap, step):
    """Grow inward from the border, stopping at edges rather than at a value.

    A plain brightness flood does not work here and the failure is instructive:
    the building's own shadowed crevices are as dark as the ground, they connect
    to the outside, and the flood pours through them and hollows the machine out.
    So growth is *neighbour-relative* -- a pixel joins the background only if it
    is within `step` of the pixel it was reached from. The sheet's ground is a
    slow mottle and passes that test everywhere; the building's edge is a hard
    step and stops it. `cap` is a backstop so a long gentle ramp cannot climb
    from the ground onto lit metal.
    """
    w, h = img.size
    px = img.load()
    seen = bytearray(w * h)
    q = deque()

    def push(x, y, from_lum):
        i = y * w + x
        if seen[i]:
            return
        l = luminance(px[x, y])
        if l <= cap and abs(l - from_lum) <= step:
            seen[i] = 1
            q.append((x, y, l))

    for x in range(w):
        push(x, 0, luminance(px[x, 0])); push(x, h - 1, luminance(px[x, h - 1]))
    for y in range(h):
        push(0, y, luminance(px[0, y])); push(w - 1, y, luminance(px[w - 1, y]))

    while q:
        x, y, l = q.popleft()
        for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
            if 0 <= nx < w and 0 <= ny < h:
                push(nx, ny, l)
    return seen


def background_reachable(alpha):
    """Which transparent pixels the canvas border can actually reach."""
    w, h = alpha.size
    px = alpha.load()
    seen = bytearray(w * h)
    q = deque()

    def push(x, y):
        i = y * w + x
        if not seen[i] and px[x, y] < 8:
            seen[i] = 1
            q.append((x, y))

    for x in range(w):
        push(x, 0); push(x, h - 1)
    for y in range(h):
        push(0, y); push(w - 1, y)
    while q:
        x, y = q.popleft()
        for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
            if 0 <= nx < w and 0 <= ny < h:
                push(nx, ny)
    return seen


def chroma_key(img, key, near, far):
    """Key a flat background colour, and pull its spill off the edges.

    Far easier and far safer than the flood above, and the reason this mode
    exists: a plate drawn on a flat, saturated ground that appears nowhere on the
    building separates perfectly by colour, whatever the building's own values
    are. The flood mode is only for plates that were drawn on a dark ground
    before anyone thought about cutting them out.
    """
    w, h = img.size
    px = img.load()
    out = img.copy()
    op = out.load()
    alpha = Image.new("L", (w, h), 255)
    ap = alpha.load()
    kr, kg, kb = key
    span = max(1, far - near)
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            d = max(abs(r - kr), abs(g - kg), abs(b - kb))
            if d <= near:
                ap[x, y] = 0
            elif d < far:
                ap[x, y] = int(255 * (d - near) / span)
            # Despill: on this key, spill shows as red and blue running ahead of
            # green on pixels that are meant to be grey-brown metal.
            if ap[x, y] and r > g and b > g and (r - g) + (b - g) > 30:
                op[x, y] = (min(r, g + 12), g, min(b, g + 12))
    return alpha, out


def smooth_close(alpha, radius, shrink=4):
    """A closing with a round kernel rather than a square one.

    PIL only offers square Max/Min filters, and a square structuring element
    leaves axis-aligned ledges hanging off the silhouette -- rectangles of ground
    welded to the building's corners. Doing the same closing on a shrunken copy
    and scaling back up approximates a disc: the downscale blurs the kernel's
    corners away, and the upscale returns a smooth boundary.
    """
    w, h = alpha.size
    small = alpha.resize((max(1, w // shrink), max(1, h // shrink)), Image.BOX)
    k = 2 * max(1, radius // shrink) + 1
    small = small.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MinFilter(k))
    return small.resize((w, h), Image.BILINEAR).point(lambda v: 255 if v >= 128 else 0)


def fill_gaps_only(alpha, radius, enclosure):
    """Close the shadow channels without welding ground to the silhouette.

    A plain closing fills the gaps between the rim blocks -- which is wanted --
    but it also merges the building with any ground lying within the radius, and
    that ground survives the erode as rectangular ledges hanging off the corners.

    So the closing is used only as a *proposal*. Every region it would add is
    examined separately, and kept only if it is genuinely a gap: enclosed by the
    building around most of its perimeter. A shadow channel between two rim
    blocks is walled in on nearly every side; a ledge of ground opens onto the
    rest of the ground and fails the test.
    """
    w, h = alpha.size
    closed = smooth_close(alpha, radius)
    a, c = alpha.load(), closed.load()

    added = [1 if (c[x, y] >= 128 and a[x, y] < 128) else 0
             for y in range(h) for x in range(w)]
    label = [0] * (w * h)
    cur = 0
    for sy in range(h):
        for sx in range(w):
            i = sy * w + sx
            if label[i] or not added[i]:
                continue
            cur += 1
            cells, border_building, border_open = [], 0, 0
            q = deque([(sx, sy)])
            label[i] = cur
            while q:
                x, y = q.popleft()
                cells.append((x, y))
                for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
                    if not (0 <= nx < w and 0 <= ny < h):
                        border_open += 1
                        continue
                    j = ny * w + nx
                    if added[j]:
                        if not label[j]:
                            label[j] = cur
                            q.append((nx, ny))
                    elif a[nx, ny] >= 128:
                        border_building += 1
                    else:
                        border_open += 1
            total = border_building + border_open
            if total and border_building / total >= enclosure:
                for x, y in cells:
                    a[x, y] = 255
    return alpha


def keep_largest(alpha):
    """Zero every opaque island except the biggest one."""
    w, h = alpha.size
    px = alpha.load()
    label = [0] * (w * h)
    best, best_n = 0, 0
    cur = 0
    for sy in range(h):
        for sx in range(w):
            i = sy * w + sx
            if label[i] or px[sx, sy] < 128:
                continue
            cur += 1
            n = 0
            q = deque([(sx, sy)])
            label[i] = cur
            while q:
                x, y = q.popleft()
                n += 1
                for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
                    if 0 <= nx < w and 0 <= ny < h:
                        j = ny * w + nx
                        if not label[j] and px[nx, ny] >= 128:
                            label[j] = cur
                            q.append((nx, ny))
            if n > best_n:
                best, best_n = cur, n
    for y in range(h):
        row = y * w
        for x in range(w):
            if label[row + x] != best:
                px[x, y] = 0
    return alpha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("--box", nargs=4, type=int, default=None,
                    metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--key", nargs=3, type=int, default=None, metavar=("R", "G", "B"),
                    help="chroma-key this flat background colour instead of flooding")
    ap.add_argument("--near", type=int, default=60, help="fully transparent within this")
    ap.add_argument("--far", type=int, default=110, help="fully opaque beyond this")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cap", type=int, default=72,
                    help="nothing brighter than this can ever be background")
    ap.add_argument("--step", type=int, default=9,
                    help="how far the background may change between neighbouring "
                         "pixels before the growth stops (default 9)")
    ap.add_argument("--close", type=int, default=12,
                    help="radius of the closing that seals shadow channels (0 = off)")
    ap.add_argument("--enclosure", type=float, default=0.72,
                    help="fraction of a gap's perimeter that must be building "
                         "before the gap is filled (default 0.72)")
    ap.add_argument("--feather", type=float, default=0.8)
    args = ap.parse_args()

    sheet = Image.open(args.sheet).convert("RGB")
    crop = sheet.crop(tuple(args.box)) if args.box else sheet
    w, h = crop.size

    if args.key:
        alpha, crop = chroma_key(crop, tuple(args.key), args.near, args.far)
    else:
        seen = background_mask(crop, args.cap, args.step)
        alpha = Image.new("L", (w, h), 255)
        ap_ = alpha.load()
        for y in range(h):
            row = y * w
            for x in range(w):
                if seen[row + x]:
                    ap_[x, y] = 0

    # Seal the channels the growth came in through.
    #
    # The building's shadowed recesses -- between the rim blocks, under the
    # cradles -- are as dark as the ground *and* they open onto it, so growth
    # reaches them however carefully it is tuned, and the machine comes out full
    # of holes. A morphological closing at a radius wider than those channels
    # shuts them without touching the outer silhouette, which is much larger than
    # the radius. This is legitimate for a game sprite: a building is a solid
    # object, and nothing inside its outline should be see-through.
    if args.close:
        alpha = fill_gaps_only(alpha, args.close, args.enclosure)
    # Anything transparent that the border cannot reach is an enclosed hole, and
    # a building has none. Fill them.
    holes = background_reachable(alpha)
    ap2 = alpha.load()
    for y in range(h):
        row = y * w
        for x in range(w):
            if ap2[x, y] < 8 and not holes[row + x]:
                ap2[x, y] = 255

    # Keep only the building. Scraps of sheet ground survive the growth wherever
    # a vignette or a panel edge separates them from the border, and they come
    # out as floating rectangles of dirt beside the machine.
    alpha = keep_largest(alpha)

    alpha = alpha.filter(ImageFilter.GaussianBlur(args.feather))

    out = crop.convert("RGBA")
    out.putalpha(alpha)
    box = out.getbbox()
    out = out.crop(box)
    out.save(args.out)

    clear = sum(1 for v in alpha.getdata() if v < 8) * 100 // (w * h)
    print("%s  %dx%d  (%d%% of the crop keyed clear)" % (args.out, out.width, out.height, clear))


if __name__ == "__main__":
    main()
