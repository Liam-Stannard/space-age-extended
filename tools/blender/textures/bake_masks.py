#!/usr/bin/env python3
"""Bake photo-texture STRUCTURE into greyscale masks; colour stays the spec palette.

  tools/blender/textures/bake_masks.py <ambientcg-download-dir>

Sources are ambientCG 1K JPG sets, CC0 (https://ambientcg.com): PaintedMetal006
(green paint chipped to rust), PaintedMetal004 (red paint, pale scratches),
Rust006 (vertical streaking). Fetch each as
https://ambientcg.com/get?file=<id>_1K-JPG.zip and unzip into <dir>/<id>/.
The sources are not committed; the masks they bake to are. hazard-stripe.jpg is
PaintedMetal016's colour map, used as it is.
"""
import os
import sys

from PIL import Image, ImageChops, ImageFilter, ImageOps

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps")


def load(n, k="Color"):
    return Image.open(f"{SRC}/{n}/{n}_1K-JPG_{k}.jpg")


c = load("PaintedMetal006").convert("RGB")
r, g, b = c.split()
paint = ImageChops.subtract(g, r).point(lambda v: 255 if v > 18 else (0 if v < 6 else int((v - 6) / 12 * 255)))
paint.filter(ImageFilter.GaussianBlur(1)).save(f"{OUT}/paint_mask.png")           # 1 = paint, 0 = rust
ImageOps.autocontrast(c.convert("L"), cutoff=2).save(f"{OUT}/grain.png")
s = load("PaintedMetal004").convert("HSV").split()[1]
s.point(lambda v: 255 if v < 90 else (0 if v > 160 else int((160 - v) / 70 * 255))).save(f"{OUT}/scratch_mask.png")
ImageOps.autocontrast(load("Rust006").convert("L"), cutoff=2).save(f"{OUT}/rust_streak.png")
