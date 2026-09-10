#!/usr/bin/env python3
"""Build a looping "level rising" glow sheet from one lit plate.

`build-glow-frames.py` is the other one, and it is deliberately not this: its two
modes are one-shot charge and discharge, built around an envelope that starts and
ends dark, because the arc mast's light *arrives* and *leaves*. A level rising in
a sight glass does neither. It loops, it never goes out, and its brightest frame
sits next to its darkest -- so bolting a third mode onto that tool would mean
disabling the part of it that makes it what it is.

**The base plate keeps its glow.** The first attempt here split the lit port off
into an unlit base and a separate glow, which is what `split-glow.py` is for and
what most of this mod's lit buildings do. It is wrong on the Vent Pump: that tool
works when "the emissive parts are strongly chromatic against bodywork that is
deliberately near-neutral iron-nickel", and this riser is *copper*. The hue
window cannot tell the molten in the port from the metal around it, and every
threshold that saved the port took half the riser with it.

So the plate stays lit and this sheet is a **brightening** laid over it. That is
also the truer reading: a wellhead full of melt is warm whether or not it is
pumping, and what changes when it runs is how much of the glass is full.

  tools/build-fill-frames.py PLATE.png --region X0 Y0 X1 Y1 --frames 16 \\
      --out graphics/entity/vent-pump/port-north.png

The sheet is cropped to the region, not left on the plate's canvas, because a
16-frame sheet of a 200x280 plate is four megabytes to say something that happens
inside twenty pixels. The shift that puts it back is printed, and it is measured
rather than chosen.
"""

import argparse
import colorsys
import math
import os
import sys

from PIL import Image, ImageFilter

PX_PER_TILE = 64          # 32 in-game px at scale 0.5


def molten(im, region, min_light, min_sat, hue_lo, hue_hi):
    """A mask of the lit fluid inside the region, and nothing else.

    Judged on lightness first and hue second. Inside the port the molten burns
    out toward white, which has almost no hue at all -- the same trap
    `split-glow.py` documents -- so a hue-only test drops the brightest part of
    the very thing it is looking for.
    """
    x0, y0, x1, y1 = region
    px = im.load()
    mask = Image.new("L", im.size, 0)
    mp = mask.load()
    kept = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b, a = px[x, y]
            if a < 40:
                continue
            hh, ll, ss = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
            deg = hh * 360.0
            warm = deg <= hue_hi or deg >= hue_lo
            if ll >= min_light and (ss >= min_sat or ll >= 0.80) and warm:
                mp[x, y] = 255
                kept += 1
    return largest_blob(mask), kept


def largest_blob(mask):
    """Keep only the biggest connected run of the mask.

    The sight glass is one shape, and everything else the colour test finds is
    not it: the bezel's lit rim, a highlight on a bolt, the warm edge of the
    riser behind. Those are small and detached, and left in they bleed light
    *outside* the window as the level rises -- which was visible on the first
    Vent Pump sheet, orange running down the riser's left side and round its
    foot in the middle frames.
    """
    w, h = mask.size
    mp = mask.load()
    seen = [[False] * h for _ in range(w)]
    best = []
    for sx in range(w):
        for sy in range(h):
            if seen[sx][sy] or not mp[sx, sy]:
                continue
            stack, comp = [(sx, sy)], []
            seen[sx][sy] = True
            while stack:
                x, y = stack.pop()
                comp.append((x, y))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h and not seen[nx][ny] \
                                and mp[nx, ny]:
                            seen[nx][ny] = True
                            stack.append((nx, ny))
            if len(comp) > len(best):
                best = comp
    out = Image.new("L", (w, h), 0)
    op = out.load()
    for x, y in best:
        op[x, y] = 255
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plate")
    ap.add_argument("--region", nargs=4, type=int, required=True,
                    metavar=("X0", "Y0", "X1", "Y1"),
                    help="the sight glass, in plate pixels")
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames", type=int, default=16)
    ap.add_argument("--line-length", type=int, default=8)
    ap.add_argument("--gain", type=float, default=0.55,
                    help="how much of the port's own brightness the top frame "
                         "adds back. This is a GLOW layer: the engine adds it to "
                         "a plate that is already lit, so 1.0 doubles the light "
                         "and blows the port out to white.")
    ap.add_argument("--min-lightness", type=float, default=0.42)
    ap.add_argument("--min-saturation", type=float, default=0.35)
    ap.add_argument("--hue-lo", type=float, default=330.0)
    ap.add_argument("--hue-hi", type=float, default=60.0)
    ap.add_argument("--meniscus", type=float, default=1.6,
                    help="softness of the level's top edge, in pixels. A "
                         "perfectly hard line reads as a wipe rather than a "
                         "liquid.")
    a = ap.parse_args()

    im = Image.open(a.plate).convert("RGBA")
    x0, y0, x1, y1 = a.region
    mask, kept = molten(im, a.region, a.min_lightness, a.min_saturation,
                        a.hue_lo, a.hue_hi)
    if not kept:
        sys.exit("no lit fluid found in that region -- widen it or drop "
                 "--min-lightness")
    bbox = mask.getbbox()
    if not bbox:
        sys.exit("mask is empty")
    print(f"  {kept} lit px, fluid bbox {bbox[0]},{bbox[1]}..{bbox[2]},{bbox[3]} "
          f"({bbox[2]-bbox[0]}x{bbox[3]-bbox[1]}) inside region "
          f"{x0},{y0}..{x1},{y1}")

    fw, fh = x1 - x0, y1 - y0
    lit = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    lit.paste(im.crop((x0, y0, x1, y1)), (0, 0))
    lit.putalpha(mask.crop((x0, y0, x1, y1)))

    # The level sweeps the FLUID's own extent, not the region's. A region drawn
    # with a margin -- which it should be, or the meniscus clips -- would
    # otherwise spend frames filling metal.
    top, bot = bbox[1] - y0, bbox[3] - y0
    span = bot - top

    frames = []
    for i in range(a.frames):
        # 0 -> empty, frames-1 -> full, and the loop closes by going back down
        # rather than snapping: a level that resets is a leak, not a cycle.
        t = i / a.frames
        level = (1 - math.cos(2 * math.pi * t)) / 2          # 0..1..0, smooth
        surface = bot - level * span
        m = Image.new("L", (fw, fh), 0)
        mp = m.load()
        for y in range(fh):
            if y >= surface:
                mp_row = 255
            elif y >= surface - a.meniscus:
                mp_row = int(255 * (1 - (surface - y) / a.meniscus))
            else:
                mp_row = 0
            for x in range(fw):
                mp[x, y] = mp_row
        m = m.filter(ImageFilter.GaussianBlur(0.6))
        f = lit.copy()
        alpha = f.getchannel("A").point(lambda v: int(v * a.gain))
        f.putalpha(Image.composite(alpha, Image.new("L", (fw, fh), 0), m))
        frames.append(f)

    cols = min(a.line_length, a.frames)
    rows = -(-a.frames // a.line_length)
    sheet = Image.new("RGBA", (cols * fw, rows * fh), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, ((i % a.line_length) * fw, (i // a.line_length) * fh))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    sheet.save(a.out)

    # Where the crop sits relative to the plate's centre, in tiles.
    sx = ((x0 + x1) / 2 - im.width / 2) / PX_PER_TILE
    sy = ((y0 + y1) / 2 - im.height / 2) / PX_PER_TILE
    print(f"  ok  {a.out}  {sheet.width}x{sheet.height}  "
          f"{a.frames} frames of {fw}x{fh}, line_length {a.line_length}")
    print(f"      shift = {{ {sx:.5f}, {sy:.5f} }}  (add the plate's own shift)")
    lo = min(f.getchannel("A").getextrema()[1] for f in frames)
    hi = max(f.getchannel("A").getextrema()[1] for f in frames)
    print(f"      peak alpha across the loop: {lo}..{hi}")


if __name__ == "__main__":
    main()
