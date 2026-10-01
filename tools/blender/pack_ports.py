#!/usr/bin/env python3
"""Pack the port fittings and blind caps into pipe_picture / pipe_covers sheets.

  python3 pack_ports.py <render-dir> <out-dir>

Rendered on a 320x320 canvas with the entity origin at its centre. The engine
positions a pipe picture relative to the tile the connection points INTO (one
tile outside the port), so each shift is taken from that tile's centre:
two tiles out from the entity centre on a 3x3, on the port's face.

A sheet keeps only the alpha region that touches its fitting. Each fitting is
rendered on the MIDDLE tile of its face, with the body as a shadow catcher, but
the engine draws the same sheet at whichever tile the port is on -- so anything
the catcher recorded away from the fitting belongs to the middle tile and not
to the port. Two kinds of it, both dropped:

  * specks of sky occlusion scattered over the body, which the noise floor
    misses and which stretched the crop to most of the canvas (port-W was
    194 px wide around a 26 px fitting);
  * the east port's shadow running down the gutter below its flange. It is
    contiguous with the flange -- its alpha fades from ~80 to ~25 without a
    break -- so connectivity alone keeps it, and drawn at the {1,1} port it
    trails off the footprint onto the ground.

So: the fitting is the opaque core of the port and its cap together (alpha at
or above SOLID, which a caught shadow does not reach), and a sheet keeps the
pixels connected to its own core that lie within the fitting's span across the
face -- screen x for a north or south port, screen y for an east or west one.
That keeps the cap's shadow on its own stub and the fitting's contact shadow
on the skirt beside it, and nothing that runs off along the face.
"""
import json
import os
import sys
from collections import deque
from PIL import Image

D, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
C, PPT, NOISE = 160.0, 64.0, 24
SOLID = 250         # an object's own pixel; caught shadow stays below this
OUTSIDE = {"N": (0, -2), "E": (2, 0), "S": (0, 2), "W": (-2, 0)}   # tiles, y down
NEIGHBOURS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


def flood(seeds, ok, w, h):
    """Indices 8-connected to `seeds` through pixels where ok(index) holds."""
    seen = set(seeds)
    queue = deque(seeds)
    while queue:
        i = queue.popleft()
        x, y = i % w, i // w
        for dx, dy in NEIGHBOURS:
            u, v = x + dx, y + dy
            j = v * w + u
            if 0 <= u < w and 0 <= v < h and j not in seen and ok(j):
                seen.add(j)
                queue.append(j)
    return seen


def core(alpha, w, h):
    """The largest 8-connected run of opaque pixels: the fitting itself."""
    left = {i for i, v in enumerate(alpha) if v >= SOLID}
    best = set()
    while left:
        part = flood([left.pop()], lambda j: alpha[j] >= SOLID, w, h)
        left -= part
        if len(part) > len(best):
            best = part
    return best


meta = {}
for d in "NESW":
    images, alphas, cores = {}, {}, {}
    for kind in ("port", "cover"):
        im = Image.open(f"{D}/{kind}-{d}.png").convert("RGBA")
        images[kind] = im
        alphas[kind] = [0 if v < NOISE else v for v in im.getchannel("A").get_flattened_data()]
        cores[kind] = core(alphas[kind], im.width, im.height)
    W, H = images["port"].size
    # across the face: x for a port on the north or south face, y for east or west
    across = (lambda i: i % W) if d in "NS" else (lambda i: i // W)
    span = [across(i) for i in cores["port"] | cores["cover"]]
    lo, hi = min(span) - 1, max(span) + 1          # and the antialiased rim
    for kind in ("port", "cover"):
        a = alphas[kind]
        kept = flood(list(cores[kind]), lambda j: a[j] > 0 and lo <= across(j) <= hi, W, H)
        im = images[kind]
        im.putalpha(Image.frombytes("L", (W, H), bytes(v if i in kept else 0 for i, v in enumerate(a))))
        x0, y0, x1, y1 = im.getchannel("A").getbbox()
        bb = (x0 - 1, y0 - 1, x1 + 1, y1 + 1)
        im.crop(bb).save(f"{OUT}/{kind}-{d}.png")
        ox, oy = C + OUTSIDE[d][0] * PPT, C + OUTSIDE[d][1] * PPT
        meta[f"{kind}-{d}"] = dict(size=(bb[2] - bb[0], bb[3] - bb[1]),
                                   shift=(round(((bb[0] + bb[2]) / 2 - ox) / PPT, 5),
                                          round(((bb[1] + bb[3]) / 2 - oy) / PPT, 5)))
meta = {k: meta[k] for k in sorted(meta, key=lambda k: (k.split("-")[0] != "port", "NESW".index(k[-1])))}
json.dump(meta, open(f"{OUT}/meta.json", "w"), indent=1)
for k, v in meta.items():
    print(k, v)
