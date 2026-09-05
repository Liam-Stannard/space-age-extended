#!/usr/bin/env python3
"""Cut a grouped harvest sheet into one PNG per icon.

Usage:
    tools/cut-icon-sheet.py SHEET.png OUT_DIR [name1 name2 ...]

A harvest sheet (see graphics/icon-sheet-prompts.md) is several rendered
objects laid out on a flat, uniform field with clear gaps between them. This
finds the objects rather than assuming a grid: the background colour is taken
from the border band, every pixel far enough from it is marked, and the mask is
split into rows and then into columns by looking for runs of empty scanlines.
That survives a generator that does not space its cells perfectly evenly, which
they never do.

Each object is written square, padded, at the size `tools/key-icons.py` wants
as input. Names are applied in reading order; unnamed cells get cell-NN.png.

Pillow only, no numpy.
"""

import os
import sys
from PIL import Image

BORDER = 12       # px band around the edge assumed to be pure background
THRESHOLD = 26    # colour distance from the background before a pixel counts
MIN_RUN = 8       # a gap shorter than this does not separate two objects
MIN_SPAN = 24     # a band shorter than this is noise, not an object
PAD = 0.10        # padding around the object, as a fraction of its longest side


def background(im):
    w, h = im.size
    px = im.load()
    band = [px[x, y] for y in range(h) for x in range(w)
            if x < BORDER or y < BORDER or x >= w - BORDER or y >= h - BORDER]
    return tuple(sum(c[i] for c in band) // len(band) for i in range(3))


def mask(im, bg):
    w, h = im.size
    px = im.load()
    m = bytearray(w * h)
    for y in range(h):
        row = y * w
        for x in range(w):
            p = px[x, y]
            if abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) > THRESHOLD:
                m[row + x] = 1
    return m


def bands(counts):
    """Runs of non-empty entries, merging gaps shorter than MIN_RUN."""
    out, start, gap = [], None, 0
    for i, c in enumerate(counts):
        if c:
            if start is None:
                start = i - gap if gap and out and i - gap <= out[-1][1] + MIN_RUN else i
            gap = 0
        else:
            if start is not None:
                gap += 1
                if gap >= MIN_RUN:
                    out.append((start, i - gap))
                    start, gap = None, 0
    if start is not None:
        out.append((start, len(counts) - 1))
    return [(a, b) for a, b in out if b - a >= MIN_SPAN]


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, out_dir, names = sys.argv[1], sys.argv[2], sys.argv[3:]
    im = Image.open(src).convert("RGB")
    w, h = im.size
    bg = background(im)
    m = mask(im, bg)

    rows = bands([sum(m[y * w:(y + 1) * w]) for y in range(h)])
    cells = []
    for y0, y1 in rows:
        cols = bands([sum(m[y * w + x] for y in range(y0, y1 + 1)) for x in range(w)])
        for x0, x1 in cols:
            cells.append((x0, y0, x1, y1))

    os.makedirs(out_dir, exist_ok=True)
    print(f"background {bg}, {len(rows)} row(s), {len(cells)} object(s)")
    for i, (x0, y0, x1, y1) in enumerate(cells):
        cw, ch = x1 - x0 + 1, y1 - y0 + 1
        # Take only the object's own pixels, then centre them on a square field
        # of the background colour. Squaring the *crop box* instead would reach
        # sideways or downwards into whatever is next on the sheet -- a wide,
        # short scene pulls in the row beneath it -- and cropping out of bounds
        # pads with BLACK, which a later keyer reads as a second background
        # colour and leaves welded to the edge of the icon.
        pad = int(max(cw, ch) * PAD)
        side = max(cw, ch) + 2 * pad
        cell = Image.new("RGB", (side, side), bg)
        cell.paste(im.crop((x0, y0, x1 + 1, y1 + 1)),
                   ((side - cw) // 2, (side - ch) // 2))
        name = names[i] if i < len(names) else f"cell-{i + 1:02d}"
        path = os.path.join(out_dir, name + ".png")
        cell.save(path)
        print(f"  {name}: {cw}x{ch} at ({x0},{y0}) -> {side}px  {path}")

    if names and len(names) != len(cells):
        print(f"\nWARNING: {len(names)} name(s) given but {len(cells)} object(s) "
              f"found. Check the sheet before trusting these files.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
