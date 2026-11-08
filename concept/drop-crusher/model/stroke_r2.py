#!/usr/bin/env python3
"""The re-timed stroke (2026-11, .claude/tasks/drop-crusher-reanimation.md T03): its GIFs
and its crops sheet, drawn from the packed sheets as the engine draws them.

  python3 stroke_r2.py <sheets-dir> <dest-dir>

  <sheets-dir>  the packed sheets and their meta.json: base.png, base-shadow.png,
                status-lamp.png, stroke.png (44 frames) and the stroke's frame_sequence
                -- concept/drop-crusher/model/sheets, the committed ones
  <dest-dir>    writes the files below

Every picture is the sprites put down at their meta.json shifts round the entity's
origin, in the engine's order: the shadow (its alpha at half, as the game darkens the
ground), the plate, the stroke's frame, the status lamp's white cut tinted green
(working). The sheets are scale 0.5: 64 sprite px a tile.

Game zoom: at zoom 1 the game draws 32 px a tile, so a scale-0.5 sprite at half its own
size; at zoom 2, 64 px a tile, the sprite's own pixels.

  stroke-r2.gif              game zoom 1: the sprites halved (2 x 2 box average), 160 px
                             for the 5-tile ground
  stroke-r2-zoom2.gif        game zoom 2: the sprites' own pixels, 320 px
  stroke-r2-slow.gif         zoom 1 at 0.25x speed
  stroke-r2-zoom2-slow.gif   zoom 2 at 0.25x speed
  crops-r2.png               the clipping check by eye: sprite px x 2, which is game
                             zoom 1 x 4 (zoom 2 x 2)

The GIFs play the 60 entries in the sequence's order at game speed, 4 ticks an entry, 15
a second (GIF durations are whole 10 ms: 70, 70, 60 for 66.7 ms on average, 4.0 s a
loop); the slow copies 270, 270, 260 ms, 16.0 s. Every frame of a GIF is quantised to one
palette, shared by all of them and built from all of them, without dithering, so held
entries are the same pixels in the GIF, not only in the sheet: checked after writing,
by reading the GIF back (main() prints it). Frame numbers are the sheet's, 1-based, as
the prototype's frame_sequence counts them.

crops-r2.png: two sheet frames a row (each played entry named), four crops each: the
crown, its shank and ratchet in the collar; the pawl in its window and its spring; the
west gear and pinion; the east gear and pinion. Its first row is the stillness test:
the plate alone, the same crops, so what any moving part uncovers is on the plate
already; beside it sheet frame 1 with the crops named.
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw

GROUND = (74, 66, 58, 255)
PPT = 64                        # sprite px a tile (scale 0.5 sheets): game zoom 2
TILES = 5
SIZE = TILES * PPT
O = SIZE / 2
STEPS = [(0, 12, "wind-up"), (13, 19, "top hold"), (20, 21, "trip"), (22, 27, "fall"), (28, 28, "land"),
         (29, 41, "seated hold"), (42, 59, "wind-up")]
ACCENTS = {6: "pawl", 20: "trip", 28: "drop", 50: "pawl", 58: "pawl"}
# crops: (name, centre in tiles from the entity's origin, right and down; width, height in tiles)
CROPS = [("crown, shank + ratchet", (0.0, -1.25), 1.2, 1.4),
         ("pawl + spring", (0.24, -0.45), 0.7, 0.7),
         ("west gear + pinion", (-0.95, -1.05), 1.1, 0.9),
         ("east gear + pinion", (0.95, -1.05), 1.1, 0.9)]
BAR = (30, 30, 30, 255)


def step_of(e):
    return next(n for a, b, n in STEPS if a <= e <= b)


class Sheets:
    def __init__(self, src):
        self.src = src
        self.meta = json.load(open(os.path.join(src, "meta.json")))
        st = self.meta["stroke"]
        self.n, self.seq, self.line = st["frames"], st["frame_sequence"], st["line_length"]
        self.fw, self.fh = st["size"]
        self.im = {k: Image.open(os.path.join(src, k + ".png")).convert("RGBA")
                   for k in ("base", "base-shadow", "status-lamp", "stroke")}

    def put(self, canvas, im, key):
        sx, sy = self.meta[key]["shift"]
        x = round(O + sx * PPT - im.width / 2)
        y = round(O + sy * PPT - im.height / 2)
        canvas.alpha_composite(im, (x, y))

    def frame(self, f):
        """Sheet frame f (0-based) cut from stroke.png."""
        x, y = (f % self.line) * self.fw, (f // self.line) * self.fh
        return self.im["stroke"].crop((x, y, x + self.fw, y + self.fh))

    def panel(self, f=None, lamp=True):
        """The machine on the ground at game zoom 2; f the sheet frame (0-based), None for
        the plate alone."""
        c = Image.new("RGBA", (SIZE, SIZE), GROUND)
        sh = self.im["base-shadow"]
        a = sh.getchannel("A").point(lambda v: v // 2)
        self.put(c, Image.merge("RGBA", (*Image.new("RGB", sh.size, (0, 0, 0)).split(), a)), "base-shadow")
        self.put(c, self.im["base"], "base")
        if f is not None:
            self.put(c, self.frame(f), "stroke")
        if lamp:
            r, g, b, al = self.im["status-lamp"].split()
            z = r.point(lambda v: 0)
            self.put(c, Image.merge("RGBA", (z, g, z, al)), "status-lamp")
        return c


def grid(c, ppt):
    d = ImageDraw.Draw(c, "RGBA")
    o = c.width / 2
    for i in range(TILES + 1):
        v = round(o + (i - TILES / 2) * ppt)
        d.line([(v, 0), (v, c.height)], fill=(255, 255, 255, 40))
        d.line([(0, v), (c.width, v)], fill=(255, 255, 255, 40))
    return c


def label(im, lines, fill=(220, 220, 220, 255)):
    lines = [lines] if isinstance(lines, str) else lines
    bar = 4 + 11 * len(lines)
    o = Image.new("RGBA", (im.width, im.height + bar), BAR)
    o.alpha_composite(im, (0, bar))
    d = ImageDraw.Draw(o)
    for i, t in enumerate(lines):
        d.text((3, 2 + 11 * i), t, fill=fill)
    return o, bar


def gif_frames(sh, zoom):
    """The 60 entries' frames at game zoom 1 or 2, and the label bar's height."""
    out, bar = [], 0
    for e, f1 in enumerate(sh.seq):
        p = sh.panel(f1 - 1)
        acc = f"* {ACCENTS[e]} sound" if e in ACCENTS else ""
        if zoom == 1:
            p = grid(p.resize((SIZE // 2, SIZE // 2), Image.BOX), PPT // 2)
            fr, bar = label(p, [f"zoom 1  entry {e}", f"frame {f1} {step_of(e)} {acc}".rstrip()])
        else:
            fr, bar = label(grid(p, PPT), f"zoom 2  entry {e}  frame {f1}  {step_of(e)}  {acc}".rstrip())
        out.append(fr.convert("RGB"))
    return out, bar


def save_gif(frames, path, unit):
    """One palette for every frame, built from all of them; no dithering."""
    w, h = frames[0].size
    strip = Image.new("RGB", (w, h * len(frames)))
    for i, fr in enumerate(frames):
        strip.paste(fr, (0, h * i))
    pal = strip.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    dur = [unit[e % 3] for e in range(len(q))]
    q[0].save(path, save_all=True, append_images=q[1:], duration=dur, loop=0, optimize=False)
    return sum(dur)


def check_gif(path, seq, bar, src_frames):
    """Read the GIF back: every held entry's picture (below the label) the same pixels as
    its run's first; and the most any entry's picture is off its source frame."""
    g = Image.open(path)
    got = []
    for i in range(g.n_frames):
        g.seek(i)
        im = g.convert("RGB")
        got.append(im.crop((0, bar, im.width, im.height)))
    assert len(got) == len(seq), f"{path}: {len(got)} frames, not {len(seq)}"
    runs = {}
    for e, f1 in enumerate(seq):
        runs.setdefault(f1, []).append(e)
    held = []
    for f1, es in runs.items():
        if len(es) > 1:
            same = all(ImageChops.difference(got[es[0]], got[e]).getbbox() is None for e in es[1:])
            held.append((f1, es[0], es[-1], same))
    worst = 0
    for e, fr in enumerate(src_frames):
        d = ImageChops.difference(fr.crop((0, bar, fr.width, fr.height)), got[e])
        worst = max(worst, max(hi for _, hi in d.getextrema()))
    return held, worst


def crop(panel, at, w, h, k=2):
    cx, cy = O + at[0] * PPT, O + at[1] * PPT
    box = (round(cx - w / 2 * PPT), round(cy - h / 2 * PPT), round(cx + w / 2 * PPT), round(cy + h / 2 * PPT))
    im = panel.crop(box)
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def crops(sh, dest, page_h=7900):
    cells = []
    plate = sh.panel(None, lamp=False)
    cells.append([label(crop(plate, at, w, h), "PLATE ALONE" if i == 0 else "plate alone",
                        fill=(255, 200, 120, 255))[0] for i, (name, at, w, h) in enumerate(CROPS)])
    cells.append([label(crop(sh.panel(0, lamp=False), at, w, h), name)[0] for name, at, w, h in CROPS])
    for f in range(sh.n):
        es = [e for e, f1 in enumerate(sh.seq) if f1 == f + 1]
        p = sh.panel(f, lamp=False)
        txt = f"frame {f + 1}: entr{'ies' if len(es) > 1 else 'y'} {es[0]}" + (f"-{es[-1]}" if len(es) > 1 else "")
        txt += f" {step_of(es[0])}"
        cells.append([label(crop(p, at, w, h), txt if i == 0 else "")[0] for i, (name, at, w, h) in enumerate(CROPS)])
    gap = 6
    rows = []
    for i in range(0, len(cells), 2):
        row = []
        for c in cells[i:i + 2]:
            row += c + [Image.new("RGBA", (gap * 3, 1), BAR)]
        rows.append(row[:-1])
    title = ("Drop Crusher stroke r2, clipping crops: sprite px x 2 = game zoom 1 x 4 (zoom 2 x 2). "
             "From the committed sheets. Frames 1-based.")
    pages, cur, hh = [], [], gap + 18
    for row in rows:
        rh = max(im.height for im in row) + gap
        if cur and hh + rh > page_h:
            pages.append(cur)
            cur, hh = [], gap + 18
        cur.append(row)
        hh += rh
    pages.append(cur)
    paths = []
    for i, pg in enumerate(pages):
        width = max(sum(im.width for im in row) + gap * (len(row) + 1) for row in pg)
        height = sum(max(im.height for im in row) + gap for row in pg) + gap + 18
        sheet = Image.new("RGBA", (width, height), BAR)
        ImageDraw.Draw(sheet).text((gap, 4), title, fill=(255, 230, 160, 255))
        y = gap + 18
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


def main(src, dest):
    sh = Sheets(src)
    ok = True
    for zoom, names in ((1, ("stroke-r2.gif", "stroke-r2-slow.gif")),
                        (2, ("stroke-r2-zoom2.gif", "stroke-r2-zoom2-slow.gif"))):
        frames, bar = gif_frames(sh, zoom)
        for name, unit in zip(names, ((70, 70, 60), (270, 270, 260))):
            path = os.path.join(dest, name)
            ms = save_gif(frames, path, unit)
            held, worst = check_gif(path, sh.seq, bar, frames)
            ok &= all(s for *_, s in held)
            runs = ", ".join(f"frame {f1} entries {a}-{b} {'identical' if s else 'DIFFER'}" for f1, a, b, s in held)
            print(f"{path}: {frames[0].size[0]} x {frames[0].size[1]}, {len(frames)} frames, {ms} ms a loop; "
                  f"held: {runs}; most a channel is off its source frame: {worst}")
    for path, size in crops(sh, dest):
        print(path, f"{size[0]} x {size[1]}")
    if not ok:
        sys.exit("stroke_r2.py: a held entry differs in a GIF")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: stroke_r2.py <sheets-dir> <dest-dir>")
    main(*sys.argv[1:])
