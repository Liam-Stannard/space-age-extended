#!/usr/bin/env python3
"""Pack the port fittings and blind caps into pipe_picture / pipe_covers sheets.

  python3 pack_ports.py <render-dir> <out-dir>

Rendered on a 320x320 canvas with the entity origin at its centre. The engine
positions a pipe picture relative to the tile the connection points INTO (one
tile outside the port), so each shift is taken from that tile's centre:
two tiles out from the entity centre on a 3x3, on the port's face.
"""
import json
import os
import sys
from PIL import Image

D, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
C, PPT, NOISE = 160.0, 64.0, 24
OUTSIDE = {"N": (0, -2), "E": (2, 0), "S": (0, 2), "W": (-2, 0)}   # tiles, y down
NAME = {"N": "north", "E": "east", "S": "south", "W": "west"}
meta = {}
for kind in ("port", "cover"):
    for d in "NESW":
        im = Image.open(f"{D}/{kind}-{d}.png").convert("RGBA")
        im.putalpha(im.getchannel("A").point(lambda v: 0 if v < NOISE else v))
        x0, y0, x1, y1 = im.getchannel("A").getbbox()
        bb = (x0 - 1, y0 - 1, x1 + 1, y1 + 1)
        im.crop(bb).save(f"{OUT}/{kind}-{d}.png")
        ox, oy = C + OUTSIDE[d][0] * PPT, C + OUTSIDE[d][1] * PPT
        meta[f"{kind}-{d}"] = dict(size=(bb[2] - bb[0], bb[3] - bb[1]),
                                   shift=(round(((bb[0] + bb[2]) / 2 - ox) / PPT, 5),
                                          round(((bb[1] + bb[3]) / 2 - oy) / PPT, 5)))
json.dump(meta, open(f"{OUT}/meta.json", "w"), indent=1)
for k, v in meta.items():
    print(k, v)
