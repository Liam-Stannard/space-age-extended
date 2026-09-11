#!/usr/bin/env python3
"""Rebuild Fulgora's cliff sheets in the Core's own material.

A cliff is twenty orientations cut from twelve 4096x2048 sheets, every piece
seamed to its neighbours at every corner, with collision baked to the shape.
Nobody draws that as a first job. What CAN be changed cheaply is the material:
this keeps Fulgora's geometry and alpha and remaps every opaque pixel's
luminance onto a three-stop gradient for the chosen material, so the rock
reads as the Core's crust in the Core's palette. Shadow sheets are not touched;
the prototype keeps pointing at vanilla's.

Usage:
  tools/build-core-cliff.py <space-age data dir> <material>
    material: slate | nickel      (or three hex stops: dark,mid,pale)

Writes graphics/terrain/cliff-core/<material>/cliff-<part>[-lower].png for
sides, inner, outer and entrance.
"""
import os, sys
from PIL import Image

MATERIALS = {
    "slate":  ((26, 30, 38), (84, 94, 108), (168, 176, 186)),
    "nickel": ((52, 54, 56), (132, 134, 132), (206, 208, 208)),
}

def remap(path, out, stops):
    im = Image.open(path).convert("RGBA")
    lum = im.convert("L"); a = im.getchannel("A")
    d, m, p = stops
    # build a 256-entry lookup per channel: dark -> mid over 0..128, mid -> pale over 128..255
    def lut(i):
        table = []
        for v in range(256):
            if v < 128:
                t = v / 127; table.append(int(round(d[i] + (m[i] - d[i]) * t)))
            else:
                t = (v - 128) / 127; table.append(int(round(m[i] + (p[i] - m[i]) * t)))
        return table
    r = lum.point(lut(0)); g = lum.point(lut(1)); b = lum.point(lut(2))
    outim = Image.merge("RGBA", (r, g, b, a))
    outim.save(out, optimize=True)
    return im.size

def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, material = sys.argv[1], sys.argv[2]
    if material in MATERIALS:
        stops = MATERIALS[material]
    else:
        stops = tuple(tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) for h in material.split(","))
        material = "custom"
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = os.path.join(repo, "graphics", "terrain", "cliff-core", material)
    os.makedirs(outdir, exist_ok=True)
    srcdir = os.path.join(src, "graphics", "terrain", "cliffs", "fulgora")
    for part in ("sides", "inner", "outer", "entrance"):
        for suffix in ("", "-lower"):
            p = os.path.join(srcdir, f"cliff-fulgora-{part}{suffix}.png")
            o = os.path.join(outdir, f"cliff-{part}{suffix}.png")
            print(f"  {os.path.relpath(o, repo)}  {remap(p, o, stops)}")

if __name__ == "__main__":
    main()
