#!/usr/bin/env python3
"""Texture-style measures: how vanilla's finish differs from a plate's, in numbers.

  python3 finish.py <plate.png> [...]

  black%   share of opaque pixels darker than L 12 -- vanilla's shadows are
           coloured, never crushed
  fine     mean |pixel - 3x3 blur|: pixel-scale noise (speckle)
  mid      mean |3x3 blur - 9x9 blur|: mottling and form at a few pixels
  ratio    fine / mid -- speckle against soft variation; vanilla is low
  darkchr  mean chroma of the darkest quarter -- coloured shadows

Measured on the pixels well inside the sprite: those whose 9 x 9 neighbourhood is all above
alpha 250 (MinFilter 9). A sprite too thin to have FEW of them -- a small ore pile, a resource cell of scattered
bits -- prints "too thin" with the count instead (exit 0: nothing to measure is not a failure,
so render.sh goes on), and ratio is "n/a" when mid is 0, as measure.py's finish() gives None.
"""
import sys
from PIL import Image, ImageFilter

FEW = 4             # the fewest pixels well inside the sprite measured: measure.py's finish() too


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
    name = f"{path.split('/')[-1][:26]:26s}"
    if n < FEW:
        print(f"{name} too thin: {n} px well inside the sprite (a 9 x 9 neighbourhood all above alpha 250), under {FEW}; not measured")
        return
    black = sum(1 for p in px if p[0] < 12) / n
    fine = sum(abs(p[0] - p[1]) for p in px) / n
    mid = sum(abs(p[1] - p[2]) for p in px) / n
    dark = sorted(px, key=lambda p: p[0])[: n // 4]
    chroma = sum(max(p[3]) - min(p[3]) for p in dark) / len(dark)
    ratio = f"{fine/mid:4.2f}" if mid else " n/a"
    print(f"{name} black {100*black:5.1f}%  fine {fine:5.2f}  mid {mid:5.2f}"
          f"  ratio {ratio}  darkchr {chroma:5.1f}")


for p in sys.argv[1:]:
    measure(p)
