#!/usr/bin/env python3
"""Rebuild vanilla's rock sprites in the Core's own material.

The boulder (sae-core-boulder) and the shard scatter (sae-crust-shards-*) are
vanilla's huge, medium, small and tiny rocks with their shape and alpha kept
and every opaque pixel's luminance remapped onto a three-stop gradient, the
way tools/build-core-cliff.py rebuilds the cliff. A tint could not do this: a
tint multiplies, and multiplying warm sandstone by blue-grey gives brown.

Usage:
  tools/build-core-rocks.py <base data dir> <material>
    material: slate | nickel      (or three hex stops: dark,mid,pale)

Writes graphics/entity/core-boulder/huge-rock-NN.png and
graphics/decorative/crust-shards/{medium,small,tiny}-rock-NN.png -- the sheets
the prototypes point at, whatever material was asked for.
"""
import os, sys, glob
from PIL import Image

MATERIALS = {
    "slate":  ((26, 30, 38), (84, 94, 108), (168, 176, 186)),
    "nickel": ((52, 54, 56), (132, 134, 132), (206, 208, 208)),
}

def remap(path, out, stops):
    im = Image.open(path).convert("RGBA")
    lum = im.convert("L"); a = im.getchannel("A")
    d, m, p = stops
    def lut(i):
        return [int(round(d[i] + (m[i] - d[i]) * v / 127)) if v < 128
                else int(round(m[i] + (p[i] - m[i]) * (v - 128) / 127)) for v in range(256)]
    Image.merge("RGBA", (lum.point(lut(0)), lum.point(lut(1)), lum.point(lut(2)), a)).save(out, optimize=True)

def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, material = sys.argv[1], sys.argv[2]
    stops = MATERIALS.get(material) or tuple(tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) for h in material.split(","))
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    jobs = [("huge-rock", os.path.join("graphics", "entity", "core-boulder"))]
    jobs += [(k, os.path.join("graphics", "decorative", "crust-shards")) for k in ("medium-rock", "small-rock", "tiny-rock")]
    for kind, outdir in jobs:
        os.makedirs(os.path.join(repo, outdir), exist_ok=True)
        files = sorted(glob.glob(os.path.join(src, "graphics", "decorative", kind, f"{kind}-*.png")))
        for f in files:
            remap(f, os.path.join(repo, outdir, os.path.basename(f)), stops)
        print(f"  {outdir}: {len(files)} sprites")

if __name__ == "__main__":
    main()
