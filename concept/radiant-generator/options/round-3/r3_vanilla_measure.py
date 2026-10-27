#!/usr/bin/env python3
"""Round 3: measure vanilla's tall showpieces the way r3_sheets.py measures the variants.

  python3 r3_vanilla_measure.py            prints JSON

rise      = tiles the opaque sprite (alpha > 200) reaches above the footprint's north edge
coverage  = share of the footprint's pixels the opaque sprite covers (shadows excluded:
            vanilla's shadows are separate layers, ours are not opaque past alpha 200)
"""
import json, os, re
from PIL import Image

FD = os.environ.get("FACTORIO_DATA", os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/data"))
PPT = 64


def lua(rel):
    t = open(os.path.join(FD, rel)).read()
    w = int(re.search(r"width\s*=\s*(\d+)", t).group(1))
    h = int(re.search(r"height\s*=\s*(\d+)", t).group(1))
    sx, sy = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", t).groups())
    return w, h, (sx / 32, sy / 32)


def canvas(layers, foot, pad=4):
    W = H = int((max(foot) + 2 * pad) * PPT)
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    o = (W / 2, H / 2)
    for im, sh in layers:
        x = round(o[0] + sh[0] * PPT - im.width / 2)
        y = round(o[1] + sh[1] * PPT - im.height / 2)
        c.alpha_composite(im, (x, y))
    return c, o


def measure(layers, foot):
    c, o = canvas(layers, foot)
    a = c.split()[3].point(lambda v: 255 if v > 200 else 0)
    top = a.getbbox()[1]
    fx0, fy0 = o[0] - foot[0] / 2 * PPT, o[1] - foot[1] / 2 * PPT
    rise = (fy0 - top) / PPT
    box = a.crop((round(fx0), round(fy0), round(fx0 + foot[0] * PPT), round(fy0 + foot[1] * PPT)))
    cov = box.histogram()[255] / (box.width * box.height)
    return round(rise, 2), round(100 * cov, 1)


def img(rel):
    return Image.open(os.path.join(FD, rel)).convert("RGBA")


def first(rel_png, rel_lua):
    w, h, sh = lua(rel_lua)
    return img(rel_png).crop((0, 0, w, h)), sh


out = {}
NUC = "base/graphics/entity/nuclear-reactor/"
out["nuclear reactor 5x5"] = measure([(img(NUC + "reactor-pipes.png"), (-1 / 32, -5 / 32)),
                                      (img(NUC + "reactor.png"), (-5 / 32, -7 / 32))], (5, 5))
FUS = "space-age/graphics/entity/fusion-reactor/"
lay = [(img(FUS + "fusion-reactor-main.png"), (1 / 32, -5.5 / 32))]
for n in range(1, 9):
    lay.append(first(FUS + "fusion-reactor-connection-%d.png" % n, FUS + "fusion-reactor-connection-%d.lua" % n))
out["fusion reactor 6x6"] = measure(lay, (6, 6))
REF = "base/graphics/entity/oil-refinery/north/"
lay = [first(REF + "oil-refinery-north.png", REF + "oil-refinery-north.lua")]
out["oil refinery 5x5 (north)"] = measure(lay, (5, 5))
GEN = "space-age/graphics/entity/fusion-generator/north/"
out["fusion generator 3x5"] = measure([(img(GEN + "fusion-generator-north.png").crop((0, 0, 244, 376)), (-2 / 32, -2 / 32))],
                                      (3, 5))
print(json.dumps({k: dict(rise_tiles=v[0], coverage_pct=v[1]) for k, v in out.items()}, indent=1))
