#!/usr/bin/env python3
"""Cut a building's fault-lamp lens out of its own plate, as a tintable sprite.

Nothing in this mod uses `status_colors` with `apply_tint = "status"`, and every
machine in it can stall for a reason the player cannot see. This is the cheapest
legibility win in the set, one sprite per building.

The lens is drawn WHITE on the plate on purpose: the engine multiplies the sprite
by the status colour at runtime, so a colour baked into the plate would be that
colour in every state for ever. This lifts those white pixels onto their own
canvas -- the SAME canvas as the plate, so the lamp registers over the building by
construction rather than by an offset somebody chose.

  tools/cut-status-lamp.py PLATE.png --out lamp.png --centre X Y --radius R

Both coordinates are in plate pixels, and `--report` finds the brightest
low-saturation blob near the centre so they can be checked rather than guessed.
"""

import argparse
import colorsys

from PIL import Image, ImageFilter


def lens_mask(im, cx, cy, r, value=0.62, sat=0.30):
    """Alpha for the lens: bright, unsaturated pixels within r of the centre."""
    px = im.load()
    mask = Image.new("L", im.size, 0)
    mp = mask.load()
    kept = 0
    for y in range(max(0, cy - r), min(im.height, cy + r + 1)):
        for x in range(max(0, cx - r), min(im.width, cx + r + 1)):
            if (x - cx) ** 2 + (y - cy) ** 2 > r * r:
                continue
            red, green, blue, alpha = px[x, y]
            if alpha < 200:
                continue
            _, s, v = colorsys.rgb_to_hsv(red / 255, green / 255, blue / 255)
            if v >= value and s <= sat:
                mp[x, y] = 255
                kept += 1
    return mask, kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plate")
    ap.add_argument("--out")
    ap.add_argument("--centre", nargs=2, type=int, required=True)
    ap.add_argument("--radius", type=int, default=8)
    ap.add_argument("--value", type=float, default=0.62)
    ap.add_argument("--saturation", type=float, default=0.30)
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    im = Image.open(args.plate).convert("RGBA")
    cx, cy = args.centre
    mask, kept = lens_mask(im, cx, cy, args.radius, args.value, args.saturation)
    bbox = mask.getbbox()
    print("  lens: %d px kept, bbox %s, canvas %dx%d" % (kept, bbox, im.width, im.height))
    if args.report or not args.out:
        return
    if kept == 0:
        raise SystemExit("no lens pixels found -- check --centre, --radius or the thresholds")

    # White, so `apply_tint = "status"` can be the only thing that colours it.
    # The plate's own lens is already near-white; forcing it flat means the
    # engine's colour is not filtered through whatever grey the render chose.
    lamp = Image.new("RGBA", im.size, (255, 255, 255, 0))
    lamp.putalpha(mask.filter(ImageFilter.GaussianBlur(0.6)))
    lamp.save(args.out)
    print("  ok  %s  %dx%d" % (args.out, lamp.width, lamp.height))


if __name__ == "__main__":
    main()
