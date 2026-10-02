#!/usr/bin/env python3
"""A model's review sheet: its renders composited the way the engine layers them.

  python3 preview.py <render-dir> <out.png> [--adopted <png> [...]]
  python3 preview.py <render-dir> <out.gif> --gif <animation> --speed <animation_speed>

<render-dir> is render.sh's <out-dir>/renders. What to draw comes from its
render.json (contract.py): every pass and frame there is on one canvas, at
sprite size, with the entity origin at its centre, so the layers register by
construction and nothing is placed by hand.

The sheet has one row per direction, every panel on one ground with the
footprint's tile grid drawn over it (the footprint itself brighter):

  idle      each shadow pass at 50 %, the plate, each animation at frame 0, and
            each light pass tinted as the engine tints the status lamp when idle
  working   the same, with the working layers in the order render.json declares
            them, each as pack.py packs it: a paint pass drawn as paint, a glow
            pass added; the lamp tinted as when working

--adopted puts the adopted plate(s) first in each row, one per direction in the
order render.json lists them, on the same ground at the same scale (a sheet's
px_per_tile px to a tile, as the engine draws a high-resolution sprite) with the
same grid: the review sheet the artist's definition asks for. Each is centred
on the entity origin and moved by its shift, given in tiles after an @ as its
prototype gives it -- the vanilla chemical plant's north base, for one, is
util.by_pixel(0, -9) in the prototype plus by_pixel(1, 0) in its .lua:

  --adopted chemical-plant-north-base.png@0.03125,-0.28125

--gif writes a looping GIF of one animation playing in the working panel, every
direction side by side, at game speed: 60 x animation_speed frames a second.
A GIF counts time in hundredths of a second, so each frame is held to the
nearest hundredth of when the engine would show it and the loop as a whole
runs at the game's rate.
"""
import argparse
import os
import sys
from PIL import Image, ImageChops, ImageDraw

import contract
import pack

GROUND = (74, 66, 58, 255)
GAP = (30, 30, 30, 255)                 # between panels
GRID = (255, 255, 255, 40)
FOOTPRINT = (255, 255, 255, 110)
# the status lamp's colours, idle and working: vanilla's electric mining drill's
# status_colors, which the reaction plant copies
LAMP = {False: (255, 0, 0, 255), True: (0, 255, 0, 255)}
LABEL = 14                              # px of label strip over each panel
PAD = 8


class Model:
    def __init__(self, src):
        self.src = src
        try:
            self.decl = contract.load(src)
        except contract.ContractError as e:
            sys.exit(f"preview.py: {e}")
        if not self.decl["passes"]:
            sys.exit(f"preview.py: {src}/render.json declares no passes to draw")
        gone = pack.missing(src, self.decl)
        if gone:
            sys.exit(f"preview.py: {src} is missing {len(gone)} declared render(s):\n" +
                     "\n".join(f"  {stem}.png  ({what})" for what, stem in gone))
        self.directions = [d for d, _ in contract.DIRECTIONS[self.decl["directions"]]]
        self.ppt = float(self.decl["rig"]["px_per_tile"])

    def open(self, stem):
        im = Image.open(os.path.join(self.src, stem + ".png")).convert("RGBA")
        if list(im.size) != list(self.decl["canvas"]):
            sys.exit(f"preview.py: {stem}.png is {im.size[0]}x{im.size[1]}, but render.json "
                     f"declares a {self.decl['canvas'][0]}x{self.decl['canvas'][1]} canvas")
        return im

    def kind(self, kind):
        return [p for p in self.decl["passes"] if p["kind"] == kind]

    def panel(self, d, working, frames=None):
        """The building in direction d on the ground, at canvas size. frames: {animation: frame}, else 0."""
        frames = frames or {}
        plate = self.open(contract.named(self.kind("plate")[0]["name"], d))
        im = Image.new("RGBA", plate.size, GROUND)
        black = Image.new("RGBA", plate.size, (0, 0, 0, 255))
        for p in self.kind("shadow"):
            alpha = pack.clean(self.open(contract.named(p["name"], d))).getchannel("A")
            im.paste(black, (0, 0), alpha.point(lambda v: v // 2))
        im.alpha_composite(plate)
        for a in self.decl["animations"]:
            im.alpha_composite(pack.clean(self.open(contract.frame(a["name"], frames.get(a["name"], 0), d))))
        for p in self.decl["passes"] if working else ():
            if p["kind"] not in contract.WORKING:
                continue
            layer = self.open(contract.named(p["name"], d))
            under = self.open(contract.named(p["over"], d))
            if p["kind"] == "paint":
                im.alpha_composite(pack.paint_layer(layer, under))
            else:
                glow = pack.glow_layer(layer, under).convert("RGB")
                im = Image.merge("RGBA", (*ImageChops.add(im.convert("RGB"), glow).split(), im.getchannel("A")))
        for p in self.kind("light"):
            lamp = pack.light_layer(self.open(contract.named(p["name"], d)))
            im.alpha_composite(ImageChops.multiply(lamp, Image.new("RGBA", lamp.size, LAMP[working])))
        return im


def grid(im, origin, footprint, ppt):
    """The tile grid, aligned to the footprint, over the whole panel; the footprint brighter."""
    draw = ImageDraw.Draw(im, "RGBA")
    ox, oy = origin
    for axis, n in ((0, footprint[0]), (1, footprint[1])):
        o = (ox, oy)[axis]
        size = im.size[axis]
        first = o + (n / 2) * ppt                   # the footprint's far edge, then every tile from it
        k = -int(first // ppt) - 1
        while first + k * ppt < size:
            v = round(first + k * ppt)
            if 0 <= v < size:
                line = [(v, 0), (v, im.height - 1)] if axis == 0 else [(0, v), (im.width - 1, v)]
                draw.line(line, fill=GRID)
            k += 1
    w, h = footprint[0] * ppt, footprint[1] * ppt
    draw.rectangle([round(ox - w / 2), round(oy - h / 2), round(ox + w / 2), round(oy + h / 2)],
                   outline=FOOTPRINT)


def place(art, size, origin, shift=(0, 0)):
    """art centred on the panel's origin, moved by shift (px), on the ground."""
    im = Image.new("RGBA", size, GROUND)
    im.alpha_composite(art, (round(origin[0] + shift[0] - art.width / 2),
                             round(origin[1] + shift[1] - art.height / 2)))
    return im


def adopted_arg(arg):
    """<png>[@<x>,<y>]: a plate and its shift in tiles."""
    path, _, shift = arg.rpartition("@") if "@" in arg else (arg, "", "")
    try:
        x, y = (float(v) for v in shift.split(",")) if shift else (0.0, 0.0)
    except ValueError:
        sys.exit(f"preview.py: --adopted {arg}: the shift after @ is not <x>,<y> in tiles")
    if not os.path.isfile(path):
        sys.exit(f"preview.py: --adopted {path}: no such file")
    return path, (x, y)


def label(im, text):
    out = Image.new("RGBA", (im.width, im.height + LABEL), GAP)
    out.alpha_composite(im, (0, LABEL))
    ImageDraw.Draw(out).text((4, 2), text, fill=(220, 220, 220, 255))
    return out


def sheet(rows):
    """rows: [[panel, ...], ...], every panel the same size."""
    pw, ph = rows[0][0].size
    cols = max(len(r) for r in rows)
    out = Image.new("RGBA", (PAD + cols * (pw + PAD), PAD + len(rows) * (ph + PAD)), GAP)
    for r, row in enumerate(rows):
        for c, im in enumerate(row):
            out.alpha_composite(im, (PAD + c * (pw + PAD), PAD + r * (ph + PAD)))
    return out


def review(model, out, adopted):
    decl = model.decl
    if adopted and len(adopted) != len(model.directions):
        sys.exit(f"preview.py: --adopted takes one plate per direction: render.json declares "
                 f"{len(model.directions)} ({decl['directions']}), and {len(adopted)} given")
    adopted = [adopted_arg(a) for a in adopted]
    plates = [(Image.open(path).convert("RGBA"), (x * model.ppt, y * model.ppt)) for path, (x, y) in adopted]
    cw, ch = decl["canvas"]
    pw = max([cw] + [p.width + 2 * abs(s[0]) for p, s in plates]) + 2 * PAD
    ph = max([ch] + [p.height + 2 * abs(s[1]) for p, s in plates]) + 2 * PAD
    pw, ph = int(-(-pw // 1)), int(-(-ph // 1))
    pw, ph = pw + pw % 2, ph + ph % 2
    origin = (pw / 2, ph / 2)
    rows = []
    for i, d in enumerate(model.directions):
        name = d or decl["directions"]
        fp = contract.footprint_in(decl, d)
        panels = []
        if plates:
            plate, shift = plates[i]
            panels.append((place(plate, (pw, ph), origin, shift),
                           f"{name}: adopted" + (f" @{adopted[i][1][0]:g},{adopted[i][1][1]:g}" if any(shift) else "")))
        panels.append((place(model.panel(d, False), (pw, ph), origin), f"{name}: idle"))
        panels.append((place(model.panel(d, True), (pw, ph), origin), f"{name}: working"))
        for im, _ in panels:
            grid(im, origin, fp, model.ppt)
        rows.append([label(im, text) for im, text in panels])
    sheet(rows).save(out)
    print(f"{out}: {len(rows)} row(s), {', '.join(d or decl['directions'] for d in model.directions)}; "
          f"panels {pw}x{ph}, origin at {origin}, {model.ppt:g} px a tile")


def gif(model, out, name, speed):
    anims = {a["name"]: a for a in model.decl["animations"]}
    if name not in anims:
        sys.exit(f"preview.py: render.json declares no animation {name!r}"
                 f" (it declares {', '.join(map(repr, anims)) or 'none'})")
    if not speed > 0:
        sys.exit(f"preview.py: --speed {speed} is not an animation_speed above 0")
    n = anims[name]["frames"]
    fps = 60 * speed
    frames = []
    for f in range(n):
        row = [model.panel(d, True, {name: f}) for d in model.directions]
        im = Image.new("RGBA", (sum(p.width for p in row), row[0].height), GROUND)
        for i, p in enumerate(row):
            im.alpha_composite(p, (i * p.width, 0))
        frames.append(im.convert("RGB"))
    # one palette for the loop, so nothing flickers between frames
    strip = Image.new("RGB", (frames[0].width, frames[0].height * n))
    for f, im in enumerate(frames):
        strip.paste(im, (0, f * im.height))
    palette = strip.quantize(colors=256)
    frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in frames]
    # frame f is up from f / fps seconds: held to the hundredth, as a GIF counts
    ticks = [round(100 * f / fps) for f in range(n + 1)]
    durations = [10 * (b - a) for a, b in zip(ticks, ticks[1:])]
    if min(durations) < 20:
        print(f"preview.py: at {fps:g} frames a second some frames are held under 2/100 s, "
              f"which most viewers slow to 1/10 s", file=sys.stderr)
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=durations, loop=0)
    print(f"{out}: {name}, {n} frames at {fps:g} a second (held {durations} ms), looping")


def main():
    ap = argparse.ArgumentParser(description="A model's review sheet, or one animation as a GIF.")
    ap.add_argument("render_dir")
    ap.add_argument("out")
    ap.add_argument("--adopted", nargs="+", default=[], metavar="PNG[@X,Y]",
                    help="the adopted plate(s), one per direction, each with its prototype shift in tiles")
    ap.add_argument("--gif", metavar="ANIMATION", help="write a GIF of this animation instead of the sheet")
    ap.add_argument("--speed", type=float, metavar="ANIMATION_SPEED",
                    help="the prototype's animation_speed, for --gif")
    args = ap.parse_args()
    if (args.gif is None) != (args.speed is None):
        ap.error("--gif and --speed go together")
    if args.gif and args.adopted:
        ap.error("--adopted is for the sheet, not the GIF")
    model = Model(args.render_dir)
    if args.gif:
        gif(model, args.out, args.gif, args.speed)
    else:
        review(model, args.out, args.adopted)


if __name__ == "__main__":
    main()
