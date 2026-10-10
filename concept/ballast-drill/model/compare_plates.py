#!/usr/bin/env python3
"""The Ballast Drill's plate, with its ring drawn in, beside vanilla's big mining drill and
the Drop Crusher's plate, at 1x and 2x.

  python3 compare_plates.py <out-dir> <compare.png>

<out-dir> is render.sh's output directory. Ours is drawn as the engine draws the stopped
machine: the plate (sheets/base-north.png at its meta.json shift) with every animation's
frame 0 over it -- the chute's and the stroke's (the ring raised), from renders/, which
are on the model's canvas with the origin at its centre. Vanilla's big mining drill is
composed from its own north layers at their .lua shifts (still, drill frame 0, output,
support, top, still-front). The Drop Crusher twice: the modelled plate (concept/drop-crusher/
model/sheets/base.png at its meta.json shift: the one the finish rounds were measured
against) and graphics/entity/drop-crusher/base.png in the main checkout, which there is
still the generated plate from before the model, drawn centred. All on one ground at
64 px a tile with their footprints' grids; then a 2x crop of the north-west quarter of
each of the first three, the same screen size; finish.py's and tonal.py's measures under
each plate (ours measured on the plate alone, as render.sh measures it).
"""
import json
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
MAIN = os.path.expanduser("~/git/space-age-extended")         # the main checkout
TOOLS = os.path.join(REPO, "tools", "blender")
VAN = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "space-age/graphics/entity/big-mining-drill")
GROUND = (74, 66, 58, 255)
PPT = 64
S = 440                                    # each 1x panel; the origin at its centre


def panel():
    return Image.new("RGBA", (S, S), GROUND)


def grid(c, tiles):
    d = ImageDraw.Draw(c, "RGBA")
    O = S / 2
    for i in range(tiles + 1):
        v = O + (i - tiles / 2) * PPT
        d.line([(v, O - tiles * 32), (v, O + tiles * 32)], fill=(255, 255, 255, 35))
        d.line([(O - tiles * 32, v), (O + tiles * 32, v)], fill=(255, 255, 255, 35))


def at(c, im, sx=0.0, sy=0.0):
    """Draw im with its centre at shift (sx, sy) tiles from the panel's origin."""
    c.alpha_composite(im, (round(S / 2 + sx * PPT - im.width / 2), round(S / 2 + sy * PPT - im.height / 2)))


def vanilla_layer(rel, frame=0, pos=(0.0, 0.0)):
    lua = open(os.path.join(VAN, rel + ".lua")).read()
    w, h = (int(re.search(rf"{k}\s*=\s*(\d+)", lua).group(1)) for k in ("width", "height"))
    bx, by = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", lua).groups())
    ll = re.search(r"line_length\s*=\s*(\d+)", lua)
    im = Image.open(os.path.join(VAN, rel + ".png")).convert("RGBA")
    ll = int(ll.group(1)) if ll and int(ll.group(1)) else im.width // w
    fr = im.crop(((frame % ll) * w, (frame // ll) * h, (frame % ll) * w + w, (frame // ll) * h + h))
    return fr, bx / 32 + pos[0], by / 32 + pos[1]


def vanilla_north():
    c = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    for rel, f, pos in (("North/big-mining-drill-N-still", 0, (0, 0)), ("big-mining-drill-drill", 0, (0, 0.15)),
                        ("North/big-mining-drill-N-output", 0, (0, 0)), ("North/big-mining-drill-N-support", 0, (0, 0)),
                        ("North/big-mining-drill-N-top", 0, (0, 0)), ("North/big-mining-drill-N-still-front", 0, (0, 0))):
        im, sx, sy = vanilla_layer(rel, f, pos)
        at(c, im, sx, sy)
    return c


def drawn_top(im):
    bb = im.getchannel("A").point(lambda a: 255 if a > 127 else 0).getbbox()
    return bb[1] - S / 2


def measures(path):
    out = []
    for tool in ("finish.py", "tonal.py"):
        r = subprocess.run([sys.executable, os.path.join(TOOLS, tool), path], capture_output=True, text=True)
        out.append(" ".join(r.stdout.split()[1:]))
    return out


def main(out_dir, dest):
    meta = json.load(open(os.path.join(out_dir, "sheets", "meta.json")))
    ours_sheet = os.path.join(out_dir, "sheets", "base-north.png")
    R = os.path.join(out_dir, "renders")

    # ours: the plate at its shift, then frame 0 of the chute and the stroke (the ring)
    ours = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    at(ours, Image.open(ours_sheet).convert("RGBA"), *meta["base-north"]["shift"])
    for stem in ("chute-00-north", "stroke-00-north"):
        at(ours, Image.open(os.path.join(R, stem + ".png")).convert("RGBA"))
    van = vanilla_north()
    dc_dir = os.path.join(REPO, "concept", "drop-crusher", "model", "sheets")
    dc = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    at(dc, Image.open(os.path.join(dc_dir, "base.png")).convert("RGBA"),
       *json.load(open(os.path.join(dc_dir, "meta.json")))["base"]["shift"])
    old_path = os.path.join(MAIN, "graphics", "entity", "drop-crusher", "base.png")
    old = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    at(old, Image.open(old_path).convert("RGBA"))

    def on_ground(im, tiles):
        c = panel()
        c.alpha_composite(im)
        grid(c, tiles)
        return c

    plates = [(on_ground(ours, 5), f"Ballast Drill, ring raised (frame 0), 1x; top {drawn_top(ours):.0f} px"),
              (on_ground(van, 5), f"vanilla big mining drill, north, 1x; top {drawn_top(van):.0f} px"),
              (on_ground(dc, 3), "Drop Crusher, modelled plate, 1x"),
              (on_ground(old, 3), "graphics/.../drop-crusher/base.png (main: pre-model), 1x")]
    q5 = (round(S / 2 - 2.7 * PPT), round(S / 2 - 3.1 * PPT))                # the 5x5s' north-west quarters
    q3 = (round(S / 2 - 1.8 * PPT), round(S / 2 - 2.4 * PPT))
    zoom = []
    for (c, _), (x0, y0), t in ((plates[0], q5, "Ballast Drill, 2x"), (plates[1], q5, "vanilla big mining drill, 2x"),
                                (plates[2], q3, "Drop Crusher (modelled), 2x")):
        zoom.append((c.crop((x0, y0, x0 + S // 2, y0 + S // 2)).resize((S, S), Image.NEAREST), t))

    gap, head, foot = 6, 18, 40
    W = 4 * (S + gap)
    sheet = Image.new("RGBA", (W, 2 * (S + head) + foot + gap), (30, 30, 30, 255))
    d = ImageDraw.Draw(sheet)
    for i, (c, t) in enumerate(plates):
        sheet.paste(c, (i * (S + gap), head))
        d.text((i * (S + gap) + 4, 3), t, fill=(235, 235, 235, 255))
    for i, (path, x) in enumerate(((ours_sheet, 0), (os.path.join(dc_dir, "base.png"), 2), (old_path, 3))):
        for j, line in enumerate(measures(path)):
            d.text((x * (S + gap) + 4, S + head + 4 + 14 * j), line[:72], fill=(220, 220, 220, 255))
    d.text((1 * (S + gap) + 4, S + head + 4), "(vanilla: composed from its layers; not measured)", fill=(160, 160, 160, 255))
    y = S + head + foot + gap
    for i, (c, t) in enumerate(zoom):
        sheet.paste(c, (i * (S + gap), y + head))
        d.text((i * (S + gap) + 4, y + 3), t, fill=(235, 235, 235, 255))
    sheet.save(dest)
    print(dest, sheet.size)


if __name__ == "__main__":
    main(*sys.argv[1:])
