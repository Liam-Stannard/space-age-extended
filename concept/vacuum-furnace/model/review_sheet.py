#!/usr/bin/env python3
"""The vacuum furnace's review sheet: the viewport in every state, the flywheel, and
the input on every face.

  python3 review_sheet.py <render-dir> <pipe-dir> <out.png> [<out.gif>]

  <render-dir>  render.sh's <out>/renders (idle, working, still, shadow, indicator,
                flywheel-NN)
  <pipe-dir>    pipe_pictures.py's output: pipe-<face>.png and meta.json
  <out.gif>     the flywheel turning, the machine working, at 1x and at 4x

Layered as the engine draws them, on one ground at 64 px a tile with the tile grid:
the shadow at 50 %, the north-facing picture or cover behind the building
(secondary_draw_orders north = -1), the plate, the flywheel's frame, the gauge's
needle (Animatorio's, from sheets/needle.png), while working
the viewport's glow added, the indicator tinted by status, then the other pictures
and covers. The input in use gets the furnace's own pipe picture (pipe_pictures.py:
a stub on the pipe's centreline, on assembler 3's size and shift) and a vanilla
straight pipe from the tile it points into; the other three faces get vanilla's pipe
cover (pipecoverspictures()). Shadows of the pictures, covers and pipe are left off.

The indicator is the viewport glass, tinted with spec 3.2's status_colors: clear
while working (the orange glow says it), pale blue for full output, clear when idle
(dark glass). The latch has no colour: the engine reports it as no_ingredients, the
same as an unfed furnace (spec 3.2).

Row 1: the adopted plate, then input south idle, working and full output.
Row 2: the flywheel at 4x, frames 0, 4, 8 and 12, and the plate with frame 0 beside
the still render (spec 6: the stopped machine is the plate with every frame 0).
Then one row per face: idle, working, and the join at 3x, idle and working.
"""
import json
import math
import os
import sys
from PIL import Image, ImageChops, ImageDraw

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import pack  # noqa: E402

sys.path.insert(0, os.path.join(REPO, "tools"))
import paths  # noqa: E402   tools/paths.py: where Factorio is
VAN = os.path.join(paths.factorio_data(), "base/graphics/entity")
ADOPTED = os.path.join(REPO, "concept/vacuum-furnace/adopted/base.png")
PPT, TILES = 64, 5
SIZE = PPT * TILES
O = SIZE / 2
GROUND = (74, 66, 58, 255)
STATUS = {"idle": None, "working": None,                                         # spec 3.2: clear
          "latch": (1, 0.3, 0.9), "full": (0.4, 0.7, 1)}
# the gauge's needle: Animatorio's layer (gauge.json), cut from sheets/base.png at this
# window by tools/build-animatorio-layers.py, 16 frames in step with the flywheel
SHEETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sheets")
# The window is the 18 px square round the dial's pivot, read from gauge.json, so it
# follows the dial when the plate's canvas changes (it moved 10 px down when the
# radiators grew, 2026-10-08); build the needle with --window x y x+18 y+18.
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gauge.json")) as _f:
    _cx, _cy = json.load(_f)["motions"][0]["center"]
NEEDLE_WINDOW = (math.floor(_cx) - 8, math.floor(_cy) - 9)
FLY = (1.0, 1.17)                       # the flywheel's centre on screen, tiles right and down
FACE_NAME = {"N": "north", "E": "east", "S": "south", "W": "west"}
OUTSIDE = {"N": (0, -2), "E": (2, 0), "S": (0, 2), "W": (-2, 0)}
JOIN = {"N": (0, -1.55), "E": (1.3, 0), "S": (0, 1.3), "W": (-1.3, 0)}      # crop centres, tiles


def put(c, im, tx, ty):
    c.alpha_composite(im, (round(O + tx * PPT - im.width / 2), round(O + ty * PPT - im.height / 2)))


def strip_shadow(im):
    """The straight pipe's shadow, painted into its sprite: pure black under alpha 250."""
    px = [(0, 0, 0, 0) if p[3] and max(p[:3]) <= 2 and p[3] < 250 else p for p in im.get_flattened_data()]
    out = Image.new("RGBA", im.size)
    out.putdata(px)
    return out


class Furnace:
    def __init__(self, src, pipes):
        self.src, self.pipes = src, pipes
        meta = json.load(open(os.path.join(SHEETS, "meta.json")))
        self.needles = Image.open(os.path.join(SHEETS, "needle.png")).convert("RGBA")
        bw, bh = meta["base"]["size"]
        sx, sy = meta["base"]["shift"]
        self.needle_at = (round(sx * PPT - bw / 2) + NEEDLE_WINDOW[0], round(sy * PPT - bh / 2) + NEEDLE_WINDOW[1])
        self.meta = json.load(open(os.path.join(pipes, "meta.json")))

    def open(self, d, stem):
        return Image.open(os.path.join(d, stem + ".png")).convert("RGBA")

    def pieces(self, use):
        """(face, image, tx, ty, kind) for every piece outside the plate."""
        out = []
        for f in "NESW":
            ox, oy = OUTSIDE[f]
            if f == use:
                pipe = "pipe-straight-vertical" if f in "NS" else "pipe-straight-horizontal"
                p = (f, strip_shadow(Image.open(f"{VAN}/pipe/{pipe}.png").convert("RGBA")), ox, oy, "pipe")
                sx, sy = self.meta[f"pipe-{f}"]["shift"]
                q = (f, self.open(self.pipes, f"pipe-{f}"), ox + sx, oy + sy, "picture")
                # entities draw in order of position: the pipe south of the furnace over
                # its picture, the others under it (unchecked in a client)
                out += [q, p] if f == "S" else [p, q]
            else:
                out.append((f, Image.open(f"{VAN}/pipe-covers/pipe-cover-{FACE_NAME[f]}.png").convert("RGBA"),
                            ox, oy, "cover"))
        return out

    def panel(self, use, state="idle", frame=0):
        src, working = self.src, state == "working"
        c = Image.new("RGBA", (SIZE, SIZE), GROUND)
        idle = self.open(src, "idle")
        pos = (round(O - idle.width / 2), round(O - idle.height / 2))
        if os.path.isfile(os.path.join(src, "shadow.png")):
            sh = pack.clean(self.open(src, "shadow")).getchannel("A").point(lambda v: v // 2)
            lay = Image.new("RGBA", c.size)
            lay.paste(Image.new("RGBA", idle.size, (0, 0, 0, 255)), pos, sh)
            c.alpha_composite(lay)
        pieces = self.pieces(use)
        for f, im, tx, ty, _ in pieces:
            if f == "N":
                put(c, im, tx, ty)
        c.alpha_composite(idle, pos)
        c.alpha_composite(self.open(src, f"flywheel-{frame:02d}"), pos)
        n = self.needles.height
        c.alpha_composite(self.needles.crop((frame * n, 0, frame * n + n, n)),
                          (round(O + self.needle_at[0]), round(O + self.needle_at[1])))
        if working:
            glow = pack.glow_layer(self.open(src, "working"), idle).convert("RGB")
            g = Image.new("RGB", c.size)
            g.paste(glow, pos)
            c = Image.merge("RGBA", (*ImageChops.add(c.convert("RGB"), g).split(), c.getchannel("A")))
        if STATUS[state]:
            light = pack.light_layer(self.open(src, "indicator"))
            tint = tuple(round(v * 255) for v in STATUS[state]) + (255,)
            c.alpha_composite(ImageChops.multiply(light, Image.new("RGBA", light.size, tint)), pos)
        for f, im, tx, ty, _ in pieces:
            if f != "N":
                put(c, im, tx, ty)
        grid(c)
        return c


def grid(c):
    d = ImageDraw.Draw(c, "RGBA")
    for i in range(TILES + 1):
        v = round(O + (i - TILES / 2) * PPT)
        d.line([(v, 0), (v, SIZE)], fill=(255, 255, 255, 40))
        d.line([(0, v), (SIZE, v)], fill=(255, 255, 255, 40))
    d.rectangle([O - 1.5 * PPT, O - 1.5 * PPT, O + 1.5 * PPT, O + 1.5 * PPT], outline=(255, 255, 255, 110))


def adopted():
    c = Image.new("RGBA", (SIZE, SIZE), GROUND)
    put(c, Image.open(ADOPTED).convert("RGBA"), 0, 0)
    grid(c)
    return c


def join(panel, f, k=3):
    return zoom(panel, JOIN[f], k)


def zoom(panel, at, k):
    cx, cy = O + at[0] * PPT, O + at[1] * PPT
    r = SIZE / k / 2
    return panel.crop((round(cx - r), round(cy - r), round(cx + r), round(cy + r))).resize((SIZE, SIZE), Image.NEAREST)


def label(im, text):
    o = Image.new("RGBA", (im.width, im.height + 14), (30, 30, 30, 255))
    o.alpha_composite(im, (0, 14))
    ImageDraw.Draw(o).text((4, 2), text, fill=(220, 220, 220, 255))
    return o


def still_check(fur):
    """The plate with flywheel frame 0, beside the still render, at 4x round the wheel."""
    idle, f0, still = (fur.open(fur.src, n) for n in ("idle", "flywheel-00", "still"))
    comp = idle.copy()
    comp.alpha_composite(f0)
    out = []
    for im in (comp, still):
        c = Image.new("RGBA", (SIZE, SIZE), GROUND)
        c.alpha_composite(im, (round(O - im.width / 2), round(O - im.height / 2)))
        out.append(zoom(c, FLY, 8))
    half = Image.new("RGBA", (SIZE, SIZE))
    half.alpha_composite(out[0].crop((0, 0, SIZE // 2, SIZE)))
    half.alpha_composite(out[1].crop((SIZE // 2, 0, SIZE, SIZE)), (SIZE // 2, 0))
    ImageDraw.Draw(half).line([(SIZE // 2, 0), (SIZE // 2, SIZE)], fill=(255, 255, 255, 160))
    return half


def main(src, pipes, out, gif=None):
    fur = Furnace(src, pipes)
    rows = [[label(adopted(), "adopted plate"),
             label(fur.panel("S", "idle"), "idle: dark glass"),
             label(fur.panel("S", "working"), "working: orange"),
             label(fur.panel("S", "full"), "full output: pale blue")]]
    rows.append([label(zoom(fur.panel("S", "working", f), FLY, 4), f"flywheel, frame {f}, 4x")
                 for f in (0, 4, 8, 12)] +
                [label(still_check(fur), "8x: plate + frame 0 | still")])
    for f in "SENW":
        idle, work = fur.panel(f, "idle"), fur.panel(f, "working")
        rows.append([label(idle, f"input {FACE_NAME[f]}: idle"),
                     label(work, f"input {FACE_NAME[f]}: working"),
                     label(join(idle, f), f"{FACE_NAME[f]} join, 3x, idle"),
                     label(join(work, f), f"{FACE_NAME[f]} join, 3x, working")])
    pw, ph = rows[0][0].size
    cols = max(len(r) for r in rows)
    sheet = Image.new("RGBA", (8 + cols * (pw + 8), 8 + len(rows) * (ph + 8)), (30, 30, 30, 255))
    for r, row in enumerate(rows):
        for k, im in enumerate(row):
            sheet.alpha_composite(im, (8 + k * (pw + 8), 8 + r * (ph + 8)))
    sheet.save(out)
    print(out, sheet.size)
    if gif:
        frames = []
        for f in range(16):
            p = fur.panel("S", "working", f)
            fr = Image.new("RGBA", (2 * SIZE, SIZE))
            fr.paste(p, (0, 0))
            fr.paste(zoom(p, FLY, 4), (SIZE, 0))
            frames.append(fr.convert("RGB"))
        frames[0].save(gif, save_all=True, append_images=frames[1:], duration=50, loop=0)
        print(gif)


if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        sys.exit("usage: review_sheet.py <render-dir> <pipe-dir> <out.png> [<out.gif>]")
    main(*sys.argv[1:])
