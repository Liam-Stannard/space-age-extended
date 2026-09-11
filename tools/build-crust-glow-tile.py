#!/usr/bin/env python3
"""Recolour Vulcanus's hot-crack tile sheets into the Core's own glow tile.

The Core's lit cracks are `volcanic-cracks-hot`'s art -- the one tile family in
the game that carries a real light layer -- placed along the crust's joints by
the Core's own rule (see prototypes/core/tiles.lua). The ember version uses the
sheets as they ship; any other colour is these sheets with their hue rotated,
which is what this writes. It is the whisker bed's approach: vanilla's geometry,
because a tile is sixteen variants and a transition set that must seam, with
only the material changed.

Only saturated pixels turn: the rock between the cracks is near-grey and is left
alone, so a rotation moves the embers and nothing else. The light sheet is
rotated by the same amount so the glow at night matches the paint by day.

Usage:
  tools/build-crust-glow-tile.py <space-age data dir> <name> <hue degrees>
  e.g. tools/build-crust-glow-tile.py "$FACTORIO_DATA/space-age" arc 200

Writes graphics/terrain/crust-glow/<name>.png and <name>-light.png.
"""
import os, sys
from PIL import Image

def rotate_hue(path, out, degrees, min_sat=0.22):
    im = Image.open(path).convert("RGBA")
    rgb = im.convert("RGB"); a = im.getchannel("A")
    h, s, v = rgb.convert("HSV").split()
    shift = int(round(degrees / 360 * 255)) % 256
    # rotate only where the pixel carries colour; greys keep their hue value,
    # which is meaningless for them anyway
    mask = s.point(lambda x: 255 if x >= min_sat * 255 else 0)
    h_rot = h.point(lambda x: (x + shift) % 256)
    h2 = Image.composite(h_rot, h, mask)
    outim = Image.merge("HSV", (h2, s, v)).convert("RGB")
    outim.putalpha(a)
    outim.save(out, optimize=True)
    return im.size

def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    src, name, degrees = sys.argv[1], sys.argv[2], float(sys.argv[3])
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = os.path.join(repo, "graphics", "terrain", "crust-glow")
    os.makedirs(outdir, exist_ok=True)
    for suffix in ("", "-light"):
        p = os.path.join(src, "graphics", "terrain", "vulcanus", f"volcanic-cracks-hot{suffix}.png")
        o = os.path.join(outdir, f"{name}{suffix}.png")
        print(f"  {os.path.relpath(o, repo)}  {rotate_hue(p, o, degrees)}")

if __name__ == "__main__":
    main()
