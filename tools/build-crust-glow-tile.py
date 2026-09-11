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
  tools/build-crust-glow-tile.py --sheet <in.png> <out.png> <hue degrees>
  any one sheet, the same rotation -- the radiant pool's surface is Vulcanus's
  lava-hot sheet turned to blue this way.
  tools/build-crust-glow-tile.py --light <in.png> <out.png> <hue degrees>
  a light sheet made from a lit main sheet: the bright, saturated pixels kept
  (the lava between the crust), the rest black, then the same rotation. The
  pool's shore wears Vulcanus's cooler lava crust, which ships without one.

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

def light_from(path, out, degrees, low=0.30, high=0.65):
    im = Image.open(path).convert("RGBA")
    rgb = im.convert("RGB"); a = im.getchannel("A")
    h, s, v = rgb.convert("HSV").split()
    # keep what glows: a soft ramp on value, gated on saturation so the grey
    # crust never lights
    lo, hi = int(low * 255), int(high * 255)
    ramp = v.point(lambda x: 0 if x <= lo else 255 if x >= hi else int(255 * (x - lo) / (hi - lo)))
    sat = s.point(lambda x: 255 if x >= 0.5 * 255 else 0)
    mask = Image.composite(ramp, Image.new("L", im.size, 0), sat)
    lit = Image.composite(rgb, Image.new("RGB", im.size, (0, 0, 0)), mask)
    lit.putalpha(a)
    tmp = out + ".unrotated.png"
    lit.save(tmp)
    size = rotate_hue(tmp, out, degrees)
    os.remove(tmp)
    return size

def main():
    if len(sys.argv) == 5 and sys.argv[1] == "--light":
        os.makedirs(os.path.dirname(os.path.abspath(sys.argv[3])), exist_ok=True)
        print(f"  {sys.argv[3]}  {light_from(sys.argv[2], sys.argv[3], float(sys.argv[4]))}")
        return
    if len(sys.argv) == 5 and sys.argv[1] == "--sheet":
        os.makedirs(os.path.dirname(os.path.abspath(sys.argv[3])), exist_ok=True)
        print(f"  {sys.argv[3]}  {rotate_hue(sys.argv[2], sys.argv[3], float(sys.argv[4]))}")
        return
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
