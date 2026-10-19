#!/usr/bin/env python3
"""Each pipe-picture sheet against assembler 3's outline, aligned on its shift.

  python3 tools/blender/measure_ports.py <ports-sheets-dir> [<out.png>]

(Moved from concept/ballast-drill/model/, where it was the drill's criterion 4;
measure.py runs it on <out-dir>/sheets/ports when a model has port pictures.)

<ports-sheets-dir> is pack_ports.py's output (port-<face>.png and meta.json). For each
face, both pictures are placed on one canvas by their shifts (ours from meta.json, which
pack_ports.py measures from the tile the port points into; assembler 3's from the .lua
beside its sheet, from the same tile, as the engine draws them), and their silhouettes
compared at alpha over 127:

  missed   px assembler 3 draws that ours does not
  extra    px ours draws that assembler 3 does not
  far_px   the farthest any of those pixels lies from the other silhouette: the outline's
           worst miss. Criterion 4 asks for 1 or less.

<out.png>: per face at 6x, assembler 3's silhouette in blue, ours in orange, both in white.
"""
import json
import math
import os
import re
import sys

from PIL import Image

VAN = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/assembling-machine-3")


def silhouette(im, cx, cy, size=160):
    """The image's alpha over 127 as a set of canvas px, its centre placed at (cx, cy) px."""
    a = im.getchannel("A").load()
    x0, y0 = round(size / 2 + cx - im.width / 2), round(size / 2 + cy - im.height / 2)
    return {(x0 + i, y0 + j) for j in range(im.height) for i in range(im.width) if a[i, j] > 127}


def far(points, other):
    if not points:
        return 0.0
    if not other:
        return math.inf
    return max(min(math.hypot(px - qx, py - qy) for qx, qy in other) for px, py in points)


def main(src, out=None, quiet=False):
    meta = json.load(open(os.path.join(src, "meta.json")))
    panels, result = [], {}
    for face in "NESW":
        lua = open(os.path.join(VAN, f"assembling-machine-3-pipe-{face}.lua")).read()
        w = int(re.search(r"width = (\d+)", lua).group(1))
        h = int(re.search(r"height = (\d+)", lua).group(1))
        bx, by = (float(v) * 2 for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", lua).groups())
        van = Image.open(os.path.join(VAN, f"assembling-machine-3-pipe-{face}.png")).convert("RGBA").crop((0, 0, w, h))
        ours = Image.open(os.path.join(src, f"port-{face}.png")).convert("RGBA")
        sx, sy = (v * 64 for v in meta[f"port-{face}"]["shift"])
        A, B = silhouette(van, bx, by), silhouette(ours, sx, sy)
        missed, extra = A - B, B - A
        f = max(far(missed, B), far(extra, A))
        result[face] = dict(missed=len(missed), extra=len(extra), far_px=round(f, 2),
                            vanilla=[w, h, round(bx / 64, 5), round(by / 64, 5)],
                            ours=[*meta[f"port-{face}"]["size"], *meta[f"port-{face}"]["shift"]])
        if not quiet:
            print(face, result[face])
        if out:
            im = Image.new("RGB", (160, 160), (30, 30, 30))
            px = im.load()
            for p in A | B:
                if 0 <= p[0] < 160 and 0 <= p[1] < 160:
                    px[p] = (240, 240, 240) if p in A and p in B else (60, 140, 255) if p in A else (255, 140, 40)
            panels.append(im.resize((960, 960), Image.NEAREST))
    if out:
        sheet = Image.new("RGB", (len(panels) * 966, 960), (0, 0, 0))
        for i, p in enumerate(panels):
            sheet.paste(p, (i * 966, 0))
        sheet.save(out)
    return result


if __name__ == "__main__":
    main(*sys.argv[1:])
