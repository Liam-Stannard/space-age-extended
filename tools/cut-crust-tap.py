#!/usr/bin/env python3
"""Cut the Crust Tap's four directional plates out of one rotation strip.

The Crust Tap is an `offshore-pump`, so it rotates, and section 5 of its spec is
blunt about why the art has to rotate with it: *the riser is the fluid box, and a
riser pointing the wrong way is the fluid box in the wrong place.* The four views
are drawn together in one strip so they are unmistakably four rotations of one
machine rather than four machines.

Two things here are not obvious and both are why this is a tool rather than a
one-liner.

**Scale comes from the BASE SQUARE, not the content.** The riser leaves a
different face in each view, so the content box is a different shape four times
over. Scaling each view to fit its own content would draw four machines at four
sizes. The base plate is the part that occupies the footprint, so it is the part
that gets measured: it is fitted to 2.000 tiles and the same scale is then used
for all four.

**Centring is on the base square too.** Centre a north plate on its content and
the machine sits true; centre an east plate on its content and the whole building
slides left to make room for a pipe that is supposed to hang over the edge. The
base's own centre is what lands on the tile.

  tools/cut-crust-tap.py STRIP.png --out-dir graphics/entity/crust-tap
"""

import argparse
import os

from PIL import Image, ImageFilter

TILES = 2
PX_PER_TILE = 64          # 32 in-game px at scale 0.5
MARGIN = 4
DIRECTIONS = ("north", "east", "south", "west")


def columns(mask):
    """Opaque pixel count per column."""
    w, h = mask.size
    px = mask.load()
    return [sum(1 for y in range(h) if px[x, y]) for x in range(w)]


def split(strip, gap=12):
    """Split the strip into its separate views on empty columns."""
    mask = strip.getchannel("A").point(lambda v: 255 if v > 20 else 0)
    cols = columns(mask)
    runs, start = [], None
    for x, n in enumerate(cols):
        if n and start is None:
            start = x
        elif not n and start is not None:
            if x - start > gap:
                runs.append((start, x))
            start = None
    if start is not None:
        runs.append((start, len(cols)))
    return [strip.crop((a, 0, b, strip.height)) for a, b in runs]


def base_span(view, share=0.45):
    """The x range of the base plate: columns taller than `share` of the tallest.

    The riser is a thin protrusion -- a few dozen pixels tall against a base that
    is most of the view's height -- so a height threshold separates them cleanly
    without knowing which way the riser points.
    """
    mask = view.getchannel("A").point(lambda v: 255 if v > 20 else 0)
    cols = columns(mask)
    tallest = max(cols)
    keep = [x for x, n in enumerate(cols) if n >= share * tallest]
    return min(keep), max(keep) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("strip")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    strip = Image.open(args.strip).convert("RGBA")
    views = split(strip)
    if len(views) != 4:
        raise SystemExit("expected 4 views in the strip, found %d" % len(views))

    # One scale for all four, taken from the north view's base square.
    b0, b1 = base_span(views[0])
    scale = (TILES * PX_PER_TILE) / (b1 - b0)
    print("north base %d px wide -> scale %.4f for 2.000 tiles" % (b1 - b0, scale))

    plates = []
    for name, view in zip(DIRECTIONS, views):
        bb = view.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
        view = view.crop(bb)
        big = view.resize((max(1, round(view.width * scale)),
                           max(1, round(view.height * scale))), Image.LANCZOS)
        lo, hi = base_span(big)
        base_w = hi - lo
        base_cx = (lo + hi) / 2
        # Canvas: wide enough for the content, tall enough for it, plus a rim.
        cw = big.width + 2 * MARGIN
        ch = big.height + 2 * MARGIN
        canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        canvas.paste(big, (MARGIN, MARGIN), big)
        # Shift so the BASE's centre, not the canvas's, lands on the tile centre.
        shift_x = ((MARGIN + base_cx) - cw / 2) / 2 / 32
        plates.append((name, canvas, shift_x, base_w))
        print("  %-6s canvas %3dx%-3d  base %.3f tiles  shift x %+.5f"
              % (name, cw, ch, base_w / PX_PER_TILE, -shift_x))

    if args.report:
        return
    os.makedirs(args.out_dir, exist_ok=True)
    for name, canvas, shift_x, _ in plates:
        p = os.path.join(args.out_dir, "base-%s.png" % name)
        canvas.save(p)
        # Shadow, from this view's own alpha, sheared the way the rest of the mod
        # does it. Flat and low: this building is barely off the ground.
        a = canvas.getchannel("A")
        foot = a.getbbox()[3] - 1
        kx, ky, blur = 0.79, 0.25, 3.0
        bleed = 10
        sh = Image.new("L", (canvas.width + round(foot * kx) + 2 * bleed,
                             canvas.height + 2 * bleed), 0)
        src, dst = a.load(), sh.load()
        for y in range(canvas.height):
            up = foot - y
            if up < 0:
                continue
            ox, oy = round(up * kx), round(up * ky)
            for x in range(canvas.width):
                v = src[x, y]
                if v > 8:
                    px, py = x + ox + bleed, foot - oy + bleed
                    if px < sh.width and 0 <= py < sh.height and v > dst[px, py]:
                        dst[px, py] = v
        sh = sh.filter(ImageFilter.GaussianBlur(blur))
        peak = sh.getextrema()[1] or 255
        sh = sh.point(lambda p: min(155, round(p * 155 / peak)))
        shadow = Image.new("RGBA", sh.size, (16, 15, 14, 0))
        shadow.putalpha(sh)
        sp = os.path.join(args.out_dir, "base-%s-shadow.png" % name)
        shadow.save(sp)
        sdx = ((shadow.width - canvas.width) / 2 - bleed) / 2 / 32
        sdy = ((shadow.height - canvas.height) / 2 - bleed) / 2 / 32
        print("  ok  %s %dx%d   %s %dx%d  shadow shift {%+.5f, %+.5f} relative"
              % (p, canvas.width, canvas.height, sp, shadow.width, shadow.height, sdx, sdy))


if __name__ == "__main__":
    main()
