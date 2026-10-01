#!/usr/bin/env python3
"""Texture-style measures: how vanilla's finish differs from a plate's, in numbers.

  python3 finish.py <plate.png> [...]

  black%   share of opaque pixels darker than L 12 -- vanilla's shadows are
           coloured, never crushed
  fine     mean |pixel - 3x3 blur|: pixel-scale noise (speckle)
  mid      mean |3x3 blur - 9x9 blur|: mottling and form at a few pixels
  ratio    fine / mid -- speckle against soft variation; vanilla is low
  darkchr  mean chroma of the darkest quarter -- coloured shadows
"""
import sys
from PIL import Image, ImageFilter


def measure(path):
    im = Image.open(path).convert("RGBA")
    a = im.getchannel("A")
    L = im.convert("L")
    b3 = L.filter(ImageFilter.BoxBlur(1))
    b9 = L.filter(ImageFilter.BoxBlur(4))
    ero = a.filter(ImageFilter.MinFilter(9))           # well inside the sprite only
    px = [(l, s3, s9, c) for l, s3, s9, e, c in zip(L.get_flattened_data(), b3.get_flattened_data(),
          b9.get_flattened_data(), ero.get_flattened_data(), im.convert("RGB").get_flattened_data()) if e > 250]
    n = len(px)
    black = sum(1 for p in px if p[0] < 12) / n
    fine = sum(abs(p[0] - p[1]) for p in px) / n
    mid = sum(abs(p[1] - p[2]) for p in px) / n
    dark = sorted(px, key=lambda p: p[0])[: n // 4]
    chroma = sum(max(p[3]) - min(p[3]) for p in dark) / len(dark)
    print(f"{path.split('/')[-1][:26]:26s} black {100*black:5.1f}%  fine {fine:5.2f}  mid {mid:5.2f}"
          f"  ratio {fine/mid:4.2f}  darkchr {chroma:5.1f}")


for p in sys.argv[1:]:
    measure(p)
