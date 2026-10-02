#!/usr/bin/env python3
"""Downsample a supersampled render directory to sprite size, in premultiplied alpha.

  python3 downsample.py <hi-dir> <out-dir> [factor]

Premultiplied, because averaging straight RGBA drags transparent black into every
edge pixel and leaves a dark fringe round the plate. The model's render.json
(contract.py) goes across with the renders; its canvas is already in sprite px.
"""
import os
import shutil
import sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
k = int(sys.argv[3]) if len(sys.argv) > 3 else 4
os.makedirs(dst, exist_ok=True)
if not os.path.isdir(src):
    sys.exit(0)             # the model rendered nothing; pack.py says what is missing
if not os.path.isfile(os.path.join(src, "render.json")) and os.path.isfile(os.path.join(dst, "render.json")):
    os.remove(os.path.join(dst, "render.json"))         # not a stale one from an earlier run
for f in sorted(os.listdir(src)):
    if f == "render.json":
        shutil.copy(os.path.join(src, f), os.path.join(dst, f))
    if not f.endswith(".png"):
        continue
    im = Image.open(os.path.join(src, f)).convert("RGBa")
    im = im.resize((im.width // k, im.height // k), Image.LANCZOS).convert("RGBA")
    im.save(os.path.join(dst, f))
