#!/usr/bin/env python3
"""Downsample a supersampled render directory to sprite size, in premultiplied alpha.

  python3 downsample.py <hi-dir> <out-dir> [factor]

Premultiplied, because averaging straight RGBA drags transparent black into every
edge pixel and leaves a dark fringe round the plate.
"""
import os
import sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
k = int(sys.argv[3]) if len(sys.argv) > 3 else 4
os.makedirs(dst, exist_ok=True)
for f in sorted(os.listdir(src)):
    if not f.endswith(".png"):
        continue
    im = Image.open(os.path.join(src, f)).convert("RGBa")
    im = im.resize((im.width // k, im.height // k), Image.LANCZOS).convert("RGBA")
    im.save(os.path.join(dst, f))
