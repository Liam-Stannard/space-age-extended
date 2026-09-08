#!/usr/bin/env python3
"""Measure a generated Array deck against the plate plan, and say pass or fail.

Every round of this building has been judged by eye and then re-measured three
different ways, which is how the lid came to be sized to the shaft's floor
rather than its mouth. `graphics/array-plate-plan.md` section 7 lists what a
round has to hit; this applies that list, mechanically, and prints the same
numbers in the same units every time.

Two measurements, and the difference matters:

  * **The deck** is the keyed silhouette's bounding box.
  * **The hole** is the transparent region *enclosed* by it -- found by flooding
    the background in from the frame and taking what the flood cannot reach.
    Not by looking for dark pixels: vanilla lights the far wall of its shaft, so
    dark-pixel methods measure the floor and undersize the opening by 40%.

  tools/check-array-plate.py RENDER.png
"""

import argparse
import sys
from collections import deque

from PIL import Image

KEY, TOL = (247, 1, 248), 90

# Section 7, verbatim. Target, then the band a round may land in.
BANDS = {
    "aspect": (1.4815, 1.45, 1.52),
    "hole width": (637, 600, 680),
    "hole height": (430, 405, 460),
    "centre across": (478, 460, 500),
    "centre down": (527, 505, 555),
}


def silhouette(img):
    w, h = img.size
    px = img.convert("RGB").load()
    m = Image.new("L", (w, h), 0)
    mp = m.load()
    kr, kg, kb = KEY
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if max(abs(r - kr), abs(g - kg), abs(b - kb)) > TOL:
                mp[x, y] = 255
    return m


def enclosed_hole(m):
    """The background region the outside cannot reach -- the hole, and only it."""
    w, h = m.size
    mp = m.load()
    seen = bytearray(w * h)
    q = deque([(x, y) for x in range(w) for y in (0, h - 1)] +
              [(x, y) for y in range(h) for x in (0, w - 1)])
    while q:
        x, y = q.popleft()
        if not (0 <= x < w and 0 <= y < h) or seen[y * w + x] or mp[x, y]:
            continue
        seen[y * w + x] = 1
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    box = [w, h, -1, -1]
    n = 0
    for y in range(h):
        row = y * w
        for x in range(w):
            if not mp[x, y] and not seen[row + x]:
                box = [min(box[0], x), min(box[1], y), max(box[2], x), max(box[3], y)]
                n += 1
    if n == 0:
        return None, 0
    return (box[0], box[1], box[2] + 1, box[3] + 1), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("render")
    args = ap.parse_args()

    m = silhouette(Image.open(args.render))
    deck = m.getbbox()
    hole, npx = enclosed_hole(m)
    if hole is None:
        print("FAIL  no hole: the background does not show through the deck")
        return 1

    dw, dh = deck[2] - deck[0], deck[3] - deck[1]
    hw, hh = hole[2] - hole[0], hole[3] - hole[1]
    u = 1000.0 / dw                      # into the plan's 1000-wide units

    got = {
        "aspect": hw / hh,
        "hole width": hw * u,
        "hole height": hh * u,
        "centre across": ((hole[0] + hole[2]) / 2 - deck[0]) * u,
        "centre down": ((hole[1] + hole[3]) / 2 - deck[1]) * u,
    }
    print("deck %d x %d px  ->  1000 x %.0f" % (dw, dh, dh * u))
    print("hole %d x %d px, %d px filled\n" % (hw, hh, npx))

    ok = True
    for k, (target, lo, hi) in BANDS.items():
        v = got[k]
        good = lo <= v <= hi
        ok &= good
        print("  %-14s %8.3f   target %8.3f   band %.3f - %.3f   %s"
              % (k, v, target, lo, hi, "ok" if good else "MISS"))

    ratio = hw / dw
    good = 0.60 <= ratio <= 0.68
    ok &= good
    print("  %-14s %8.3f   target %8.3f   band %.3f - %.3f   %s"
          % ("hole / deck", ratio, 0.637, 0.60, 0.68, "ok" if good else "MISS"))

    print("\n%s" % ("PASS" if ok else "REJECT"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
