#!/usr/bin/env python3
"""Overlay a true tile grid on a building plate, and measure the overhang.

The grid panels a generator draws on a concept sheet are decorative. They are
not measured, they do not line up, and they prove nothing -- which is exactly
the failure mode Appendix C warns about for colour: never judge by eye what a
tool can measure.

This draws the grid instead. Give it a plate with a transparent background and
the footprint in tiles; it finds the sprite's visible bounds, fits the declared
footprint to them, draws the grid at the true pitch, and reports how far the art
spills past the box in each direction.

  tools/check-footprint.py plate.png --tiles 3
  tools/check-footprint.py plate.png --tiles 5 --out check.png
  tools/check-footprint.py plate.png --tiles 2 5      # a rectangular footprint
"""
import argparse, sys
from PIL import Image, ImageDraw


def visible_bounds(im):
    """Bounding box of pixels with meaningful alpha."""
    if im.mode != "RGBA":
        return (0, 0, im.size[0], im.size[1])
    a = im.getchannel("A").point(lambda v: 255 if v > 8 else 0)
    box = a.getbbox()
    return box or (0, 0, im.size[0], im.size[1])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("plate")
    p.add_argument("--tiles", type=int, nargs="+", required=True,
                   help="footprint in tiles: one number for a square, or WIDTH HEIGHT")
    p.add_argument("--out", help="write an annotated PNG here")
    a = p.parse_args()

    im = Image.open(a.plate).convert("RGBA")
    x0, y0, x1, y1 = visible_bounds(im)
    w, h = x1 - x0, y1 - y0

    tw = a.tiles[0]
    th = a.tiles[1] if len(a.tiles) > 1 else tw

    # The pitch comes from the WIDTH, always. An earlier version took the
    # narrower visible axis, on the reasoning that a building overhangs
    # vertically and never horizontally -- which is true of a tall building and
    # false of a squat one. The Ring Mast is 2.83 tiles tall on a 3 tile box, so
    # the narrower axis was its height, the inferred pitch came out at 60.3
    # instead of 64, and a plate cut to exactly 3.000 tiles was reported as
    # overhanging by 0.09 each side. Sideways is the measurement that matters and
    # sideways is the axis to take it from.
    pitch = w / tw
    box_w, box_h = pitch * tw, pitch * th
    # Centre the box on the visible content horizontally, and sit it on the base.
    cx = (x0 + x1) / 2
    bx0, bx1 = cx - box_w / 2, cx + box_w / 2
    by1 = y1                      # the base of the sprite sits on the box's bottom
    by0 = by1 - box_h

    over = {
        "left":   max(0.0, bx0 - x0) / pitch,
        "right":  max(0.0, x1 - bx1) / pitch,
        "top":    max(0.0, by0 - y0) / pitch,
        "bottom": max(0.0, y1 - by1) / pitch,
    }

    print(f"plate         {a.plate}")
    print(f"visible       {w} x {h} px at ({x0},{y0})")
    print(f"tile pitch    {pitch:.2f} px  ->  {tw}x{th} box = {box_w:.0f} x {box_h:.0f} px")
    # Only sideways overhang breaks tiling. A tall building is *supposed* to
    # rise above its footprint -- the arc mast stands 5.1 tiles tall on a 3 tile
    # box -- and the engine places it with a shift rather than by shrinking it.
    for k in ("left", "right"):
        v = over[k]
        flag = "OK" if v < 0.02 else ("lip" if v < 0.25 else "OVERHANG")
        print(f"  {k:<7} {v:5.2f} tiles   {flag}")
    print(f"  height  {h / pitch:5.2f} tiles   "
          f"(box is {th}; above it: {over['top']:.2f} -- expected on a tall building)")
    worst = max(over["left"], over["right"])
    print()
    if worst < 0.02:
        print("PASS -- the art sits inside its footprint horizontally.")
    elif worst < 0.25:
        print("PASS with a lip -- vanilla tolerates a little; the collector's is a quarter tile.")
    else:
        print(f"FAIL -- {worst:.2f} tiles of sideways overhang. A row of these will interleave.")

    if a.out:
        canvas = Image.new("RGBA", im.size, (60, 60, 64, 255))
        canvas.alpha_composite(im)
        d = ImageDraw.Draw(canvas)
        for i in range(a.tiles + 1):
            x = bx0 + i * pitch
            y = by0 + i * pitch
            d.line([(x, by0), (x, by1)], fill=(255, 90, 90, 255), width=2)
            d.line([(bx0, y), (bx1, y)], fill=(255, 90, 90, 255), width=2)
        d.rectangle([bx0, by0, bx1, by1], outline=(90, 220, 120, 255), width=3)
        canvas.convert("RGB").save(a.out)
        print(f"wrote {a.out}")
    return 0 if worst < 0.25 else 1


if __name__ == "__main__":
    sys.exit(main())
