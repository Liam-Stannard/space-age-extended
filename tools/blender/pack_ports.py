#!/usr/bin/env python3
"""Pack the port fittings and blind caps into pipe_picture / pipe_covers sheets.

  python3 pack_ports.py <render-dir> <out-dir>

What to pack comes from the model's render.json (contract.py): one fitting per
declared port, rendered as port-<face>.png and cover-<face>.png on the declared
canvas with the entity origin at its centre. The engine positions a pipe
picture relative to the tile the connection points INTO (one tile outside the
port), so each shift is taken from that tile's centre: the declared tile plus
one tile out through its face.

A sheet keeps only the alpha region that touches its fitting. A fitting is
rendered on one tile of its face, with the body as a shadow catcher, but the
engine draws the same sheet at whichever tile a port on that face is on -- so
anything the catcher recorded away from the fitting belongs to the tile it was
rendered on and not to the port. Two kinds of it, both dropped:

  * specks of sky occlusion scattered over the body, which the noise floor
    misses and which stretched the crop to most of the canvas (the reaction
    plant's port-W was 194 px wide around a 26 px fitting);
  * a port's shadow running along the face below its flange. It is contiguous
    with the flange -- on the reaction plant's east port its alpha fades from
    ~80 to ~25 without a break -- so connectivity alone keeps it, and drawn at
    another port on that face it trails off the footprint onto the ground.

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

import contract

NOISE = 24
SOLID = 250         # an object's own pixel; caught shadow stays below this
NEIGHBOURS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
KINDS = ("port", "cover")


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


def pack(src, out, decl):
    cx, cy = decl["canvas"][0] / 2, decl["canvas"][1] / 2
    ppt = float(decl["rig"]["px_per_tile"])
    meta = {}
    for p in decl["ports"]:
        d = p["face"]
        images, alphas, cores = {}, {}, {}
        for kind in KINDS:
            im = Image.open(os.path.join(src, f"{kind}-{d}.png")).convert("RGBA")
            if list(im.size) != list(decl["canvas"]):
                sys.exit(f"pack_ports.py: {kind}-{d}.png is {im.size[0]}x{im.size[1]}, but render.json "
                         f"declares a {decl['canvas'][0]}x{decl['canvas'][1]} canvas")
            images[kind] = im
            alphas[kind] = [0 if v < NOISE else v for v in im.getchannel("A").get_flattened_data()]
            cores[kind] = core(alphas[kind], im.width, im.height)
            if not cores[kind]:
                sys.exit(f"pack_ports.py: {kind}-{d}.png has no opaque pixel to call its fitting")
        W, H = images["port"].size
        # across the face: x for a port on the north or south face, y for east or west
        across = (lambda i: i % W) if d in "NS" else (lambda i: i // W)
        span = [across(i) for i in cores["port"] | cores["cover"]]
        lo, hi = min(span) - 1, max(span) + 1          # and the antialiased rim
        tx, ty = contract.outside(p)
        ox, oy = cx + tx * ppt, cy + ty * ppt
        for kind in KINDS:
            a = alphas[kind]
            kept = flood(list(cores[kind]), lambda j: a[j] > 0 and lo <= across(j) <= hi, W, H)
            im = images[kind]
            im.putalpha(Image.frombytes("L", (W, H), bytes(v if i in kept else 0 for i, v in enumerate(a))))
            x0, y0, x1, y1 = im.getchannel("A").getbbox()
            bb = (x0 - 1, y0 - 1, x1 + 1, y1 + 1)
            im.crop(bb).save(os.path.join(out, f"{kind}-{d}.png"))
            meta[f"{kind}-{d}"] = dict(size=(bb[2] - bb[0], bb[3] - bb[1]),
                                       shift=(round(((bb[0] + bb[2]) / 2 - ox) / ppt, 5),
                                              round(((bb[1] + bb[3]) / 2 - oy) / ppt, 5)),
                                       tile=p["tile"], into=[tx, ty])
    order = "NESW"
    return {k: meta[k] for k in sorted(meta, key=lambda k: (KINDS.index(k.split("-")[0]), order.index(k[-1])))}


def main(src, out):
    try:
        decl = contract.load(src)
    except contract.ContractError as e:
        sys.exit(f"pack_ports.py: {e}")
    if not decl["ports"]:
        sys.exit(f"pack_ports.py: {src}/render.json declares no ports")
    gone = [f"{kind}-{p['face']}.png" for p in decl["ports"] for kind in KINDS
            if not os.path.isfile(os.path.join(src, f"{kind}-{p['face']}.png"))]
    if gone:
        sys.exit(f"pack_ports.py: {src} is missing {len(gone)} declared render(s):\n" +
                 "\n".join(f"  {g}  (port on face {g[-5]})" for g in gone))
    os.makedirs(out, exist_ok=True)
    meta = pack(src, out, decl)
    with open(os.path.join(out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    for k, v in meta.items():
        print(k, v)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: pack_ports.py <render-dir> <out-dir>")
    main(sys.argv[1], sys.argv[2])
