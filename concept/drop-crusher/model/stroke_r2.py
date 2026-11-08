#!/usr/bin/env python3
"""The re-timed stroke (2026-11, .claude/tasks/drop-crusher-reanimation.md T03): its GIFs
and its crops sheet, off a render.sh run.

  python3 stroke_r2.py <out-dir> <dest-dir>

  <out-dir>   render.sh's output directory (renders/: idle, still, shadow, lamp, stroke-NN;
              renders/render.json: the 44 sheet frames and the 60-entry frame_sequence)
  <dest-dir>  writes stroke-r2.gif, stroke-r2-slow.gif, crops-r2.png (and crops-r2-b.png
              if the frames do not fit one page under 8000 px)

stroke-r2.gif: the 60 entries in the sequence's order at game speed, 4 ticks an entry, 15
a second (GIF durations are whole 10 ms: 70, 70, 60 for 66.7 ms on average, 4.0 s a
loop); the machine at 1x (the sprites' own pixels) on one ground with the tile grid, the
working lamp green; the entry, its sheet frame and its step named under it.
stroke-r2-slow.gif: the same at 0.25x (270, 270, 260 ms, 16.0 s a loop).

crops-r2.png: the clipping check by eye, at 2x. Two sheet frames a row (each played entry
named), four crops each, layered as the engine draws them (shadow, plate, the frame):
the crown, its shank and ratchet in the collar; the pawl in its window and its spring;
the west gear and pinion; the east gear and pinion. Its first row is the
stillness test: the plate alone (every moving part off), the same crops, so what any
moving part uncovers is on the plate already; beside it sheet frame 1 with the crops named.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import pack  # noqa: E402

GROUND = (74, 66, 58, 255)
PPT = 64                        # sprite px a tile (scale 0.5 sheets)
SIZE = 5 * PPT
O = SIZE / 2
STEPS = [(0, 12, "wind-up"), (13, 19, "top hold"), (20, 21, "trip"), (22, 27, "fall"), (28, 28, "land"),
         (29, 41, "seated hold"), (42, 59, "wind-up")]
ACCENTS = {6: "pawl", 20: "trip", 28: "drop", 50: "pawl", 58: "pawl"}
# crops: (name, centre in tiles from the entity's origin, right and down; width, height in tiles)
CROPS = [("crown, shank + ratchet", (0.0, -1.25), 1.2, 1.4),
         ("pawl + spring", (0.24, -0.45), 0.7, 0.7),
         ("west gear + pinion", (-0.95, -1.05), 1.1, 0.9),
         ("east gear + pinion", (0.95, -1.05), 1.1, 0.9)]


def step_of(e):
    return next(n for a, b, n in STEPS if a <= e <= b)


class Crusher:
    def __init__(self, out):
        self.r = os.path.join(out, "renders")
        self.decl = json.load(open(os.path.join(self.r, "render.json")))
        a = self.decl["animations"][0]
        self.n, self.seq = a["frames"], a["frame_sequence"]
        self.cache = {}

    def open(self, stem):
        if stem not in self.cache:
            self.cache[stem] = Image.open(os.path.join(self.r, stem + ".png")).convert("RGBA")
        return self.cache[stem]

    def panel(self, f=None, lamp=True, grid=True):
        """The machine on the ground; f the sheet frame (0-based), None for the plate alone."""
        c = Image.new("RGBA", (SIZE, SIZE), GROUND)
        idle = self.open("idle")
        pos = (round(O - idle.width / 2), round(O - idle.height / 2))
        a = pack.clean(self.open("shadow").copy()).getchannel("A")
        lay = Image.new("RGBA", c.size)
        lay.paste(Image.new("RGBA", a.size, (0, 0, 0, 255)), pos, a.point(lambda v: v // 2))
        c.alpha_composite(lay)
        c.alpha_composite(idle, pos)
        if f is not None:
            c.alpha_composite(self.open(f"stroke-{f:02d}"), pos)
        if lamp:
            r, g, b, al = pack.light_layer(self.open("lamp")).split()
            z = r.point(lambda v: 0)
            c.alpha_composite(Image.merge("RGBA", (z, g, z, al)), pos)
        if grid:
            d = ImageDraw.Draw(c, "RGBA")
            for i in range(6):
                v = round(O + (i - 2.5) * PPT)
                d.line([(v, 0), (v, SIZE)], fill=(255, 255, 255, 40))
                d.line([(0, v), (SIZE, v)], fill=(255, 255, 255, 40))
        return c


def label(im, text, bar=14, fill=(220, 220, 220, 255)):
    o = Image.new("RGBA", (im.width, im.height + bar), (30, 30, 30, 255))
    o.alpha_composite(im, (0, bar))
    ImageDraw.Draw(o).text((3, 2), text, fill=fill)
    return o


def gifs(cr, dest):
    frames = []
    for e, f1 in enumerate(cr.seq):
        acc = f"  * {ACCENTS[e]} sound" if e in ACCENTS else ""
        fr = label(cr.panel(f1 - 1), f"entry {e:2d}  frame {f1:2d}  {step_of(e)}{acc}", bar=16)
        frames.append(fr.convert("RGB"))
    out = {}
    for name, unit in (("stroke-r2.gif", (70, 70, 60)), ("stroke-r2-slow.gif", (270, 270, 260))):
        dur = [unit[e % 3] for e in range(len(frames))]
        path = os.path.join(dest, name)
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=dur, loop=0)
        out[name] = (path, sum(dur), frames[0].size)
    return out


def crop(panel, at, w, h, k=2):
    cx, cy = O + at[0] * PPT, O + at[1] * PPT
    box = (round(cx - w / 2 * PPT), round(cy - h / 2 * PPT), round(cx + w / 2 * PPT), round(cy + h / 2 * PPT))
    im = panel.crop(box)
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def crops(cr, dest, page_h=7900):
    cells = []
    plate = cr.panel(None, lamp=False, grid=False)
    cells.append([label(crop(plate, at, w, h), "PLATE ALONE" if i == 0 else "plate alone", fill=(255, 200, 120, 255))
                  for i, (name, at, w, h) in enumerate(CROPS)])
    cells.append([label(crop(cr.panel(0, lamp=False, grid=False), at, w, h), name) for name, at, w, h in CROPS])
    for f in range(cr.n):
        es = [e for e, f1 in enumerate(cr.seq) if f1 == f + 1]
        p = cr.panel(f, lamp=False, grid=False)
        txt = f"frame {f + 1}: entr{'ies' if len(es) > 1 else 'y'} {es[0]}" + (f"-{es[-1]}" if len(es) > 1 else "")
        txt += f" {step_of(es[0])}"
        cells.append([label(crop(p, at, w, h), txt if i == 0 else "") for i, (name, at, w, h) in enumerate(CROPS)])
    # two sheet frames a row (the first row: the plate alone, then the crops' names on frame 1)
    gap = 6
    rows = []
    for i in range(0, len(cells), 2):
        row = []
        for c in cells[i:i + 2]:
            row += c + [Image.new("RGBA", (gap * 3, 1), (30, 30, 30, 255))]
        rows.append(row[:-1])
    pages, cur, hh = [], [], gap
    for row in rows:
        rh = max(im.height for im in row) + gap
        if cur and hh + rh > page_h:
            pages.append(cur)
            cur, hh = [], gap
        cur.append(row)
        hh += rh
    pages.append(cur)
    paths = []
    for i, pg in enumerate(pages):
        width = max(sum(im.width for im in row) + gap * (len(row) + 1) for row in pg)
        height = sum(max(im.height for im in row) + gap for row in pg) + gap
        sheet = Image.new("RGBA", (width, height), (30, 30, 30, 255))
        y = gap
        for row in pg:
            x = gap
            for im in row:
                sheet.alpha_composite(im, (x, y))
                x += im.width + gap
            y += max(im.height for im in row) + gap
        path = os.path.join(dest, "crops-r2.png" if i == 0 else f"crops-r2-{chr(ord('a') + i)}.png")
        sheet.convert("RGB").save(path)
        paths.append((path, sheet.size))
    return paths


def main(out, dest):
    cr = Crusher(out)
    for name, (path, ms, size) in gifs(cr, dest).items():
        print(path, f"{ms} ms a loop, {size[0]} x {size[1]}")
    for path, size in crops(cr, dest):
        print(path, f"{size[0]} x {size[1]}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: stroke_r2.py <out-dir> <dest-dir>")
    main(*sys.argv[1:])
