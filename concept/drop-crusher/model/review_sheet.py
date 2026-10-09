#!/usr/bin/env python3
"""The Drop Crusher's review sheet and stroke GIF.

  python3 review_sheet.py <out-dir> <review.png> <stroke.gif>

  <out-dir>  render.sh's output directory: <out-dir>/renders (idle, still, shadow,
             lamp, stroke-NN) and <out-dir>/sheets (icon.png, meta.json)

Everything is layered as the engine draws it, on one ground at 64 px a tile with the
tile grid: the cast shadow at 50 %, the plate, the stroke's frame over it, and the
status lamp's white lens tinted by status with vanilla's mining-drill colours (the
task: the crusher's lamp is a status lamp). The adopted plate is drawn from
graphics/entity/drop-crusher/ at its own shifts, with its own shadow.

Row 1: the adopted plate; the new plate seated, working (green); the top of the
stroke, pawl clear; idle (red); full output (yellow).
Row 2: 4x on the collar at the seat, mid-wind, the top and mid-fall; the frame-0
check (the plate with frame 0 | the still render), 8x.
Rows 3-6: every frame of the stroke, 2x on the roof, its lift in tiles and the
travel since the frame before in screen px.
Row 7: the icon strip at 1x and 4x.

The GIF loops the stroke at game speed: animation_speed 0.2 is 12 frames a second,
2 s a stroke; the machine at 1x, beside the roof at 3x.
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import pack  # noqa: E402

ADOPTED = os.path.join(REPO, "graphics", "entity", "drop-crusher")
PPT, TILES = 64, 5
SIZE = PPT * TILES
O = SIZE / 2
GROUND = (74, 66, 58, 255)
STATUS = {"working": (0, 1, 0), "idle": (1, 0, 0), "full": (1, 1, 0), "off": None}
ROOFLINE = (0.0, -1.4)          # the zooms' centre: the collar, tiles right and down


def grid(c):
    d = ImageDraw.Draw(c, "RGBA")
    for i in range(TILES + 1):
        v = round(O + (i - TILES / 2) * PPT)
        d.line([(v, 0), (v, SIZE)], fill=(255, 255, 255, 40))
        d.line([(0, v), (SIZE, v)], fill=(255, 255, 255, 40))
    d.rectangle([O - 1.5 * PPT, O - 1.5 * PPT, O + 1.5 * PPT, O + 1.5 * PPT], outline=(255, 255, 255, 110))


def shadow_layer(c, alpha, at):
    lay = Image.new("RGBA", c.size)
    lay.paste(Image.new("RGBA", alpha.size, (0, 0, 0, 255)), at, alpha.point(lambda v: v // 2))
    c.alpha_composite(lay)


def adopted():
    c = Image.new("RGBA", (SIZE, SIZE), GROUND)
    sh = Image.open(os.path.join(ADOPTED, "base-shadow.png")).convert("RGBA")
    shadow_layer(c, sh.getchannel("A"), (round(O + 1.23438 * PPT - sh.width / 2), round(O + 0.05469 * PPT - sh.height / 2)))
    base = Image.open(os.path.join(ADOPTED, "base.png")).convert("RGBA")
    c.alpha_composite(base, (round(O - base.width / 2), round(O - 0.03125 * PPT - base.height / 2)))
    grid(c)
    return c


class Crusher:
    def __init__(self, out):
        self.r = os.path.join(out, "renders")
        self.sheets = os.path.join(out, "sheets")
        self.decl = json.load(open(os.path.join(self.r, "render.json")))
        self.n = self.decl["animations"][0]["frames"]
        self.lift = [p[2] for p in self.decl["animations"][0]["path"]]
        self.cache = {}

    def open(self, stem):
        if stem not in self.cache:
            self.cache[stem] = Image.open(os.path.join(self.r, stem + ".png")).convert("RGBA")
        return self.cache[stem]

    def panel(self, f=0, status="working", grid_on=True):
        c = Image.new("RGBA", (SIZE, SIZE), GROUND)
        idle = self.open("idle")
        pos = (round(O - idle.width / 2), round(O - idle.height / 2))
        shadow_layer(c, pack.clean(self.open("shadow").copy()).getchannel("A"), pos)
        c.alpha_composite(idle, pos)
        c.alpha_composite(self.open(f"stroke-{f:02d}"), pos)
        tint = STATUS[status]
        if tint:
            light = pack.light_layer(self.open("lamp"))
            r, g, b, a = light.split()
            tinted = Image.merge("RGBA", (r.point(lambda v: round(v * tint[0])), g.point(lambda v: round(v * tint[1])),
                                          b.point(lambda v: round(v * tint[2])), a))
            c.alpha_composite(tinted, pos)
        if grid_on:
            grid(c)
        return c


def zoom(panel, at, k):
    cx, cy = O + at[0] * PPT, O + at[1] * PPT
    r = SIZE / k / 2
    return panel.crop((round(cx - r), round(cy - r), round(cx + r), round(cy + r))).resize((SIZE, SIZE), Image.NEAREST)


def label(im, text, bar=14):
    o = Image.new("RGBA", (im.width, im.height + bar), (30, 30, 30, 255))
    o.alpha_composite(im, (0, bar))
    ImageDraw.Draw(o).text((4, 2), text, fill=(220, 220, 220, 255))
    return o


def still_check(cr):
    comp = cr.open("idle").copy()
    comp.alpha_composite(cr.open("stroke-00"))
    halves = []
    for im in (comp, cr.open("still")):
        c = Image.new("RGBA", (SIZE, SIZE), GROUND)
        c.alpha_composite(im, (round(O - im.width / 2), round(O - im.height / 2)))
        halves.append(zoom(c, ROOFLINE, 8))
    out = Image.new("RGBA", (SIZE, SIZE))
    out.alpha_composite(halves[0].crop((0, 0, SIZE // 2, SIZE)))
    out.alpha_composite(halves[1].crop((SIZE // 2, 0, SIZE, SIZE)), (SIZE // 2, 0))
    ImageDraw.Draw(out).line([(SIZE // 2, 0), (SIZE // 2, SIZE)], fill=(255, 255, 255, 160))
    return out


def strip_frame(cr, f, w_t=3.0, h_t=1.6, k=2):
    p = cr.panel(f, "working", grid_on=False)
    cx, cy = O + ROOFLINE[0] * PPT, O + ROOFLINE[1] * PPT
    box = (round(cx - w_t / 2 * PPT), round(cy - h_t / 2 * PPT), round(cx + w_t / 2 * PPT), round(cy + h_t / 2 * PPT))
    im = p.crop(box)
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def main(out, review, gif):
    cr = Crusher(out)
    top = max(range(cr.n), key=lambda f: cr.lift[f])
    rows = [[label(adopted(), "wired plate (graphics/entity/drop-crusher)"),
             label(cr.panel(0, "working"), "new plate, seated: working (green)"),
             label(cr.panel(top, "working"), f"top of the stroke, frame {top}: pawl clear"),
             label(cr.panel(0, "idle"), "idle (red)"),
             label(cr.panel(0, "full"), "full output (yellow)")]]
    picks = [0, top // 2, top, top + (cr.n - top) // 2 + 1]
    rows.append([label(zoom(cr.panel(f, "working"), ROOFLINE, 4), f"frame {f}, lift {cr.lift[f]:.3f}, 4x")
                 for f in picks] + [label(still_check(cr), "8x: plate + frame 0 | still")])
    strip = []
    for f in range(cr.n):
        prev = cr.lift[(f - 1) % cr.n]
        step = (cr.lift[f] - prev) * PPT * math.cos(math.radians(cr.decl["rig"]["elevation"]))
        strip.append(label(strip_frame(cr, f), f"{f:2d}  lift {cr.lift[f]:.3f}  {step:+5.1f} px"))
    for i in range(0, cr.n, 6):
        rows.append(strip[i:i + 6])
    icon_path = os.path.join(cr.sheets, "icon.png")
    if os.path.isfile(icon_path):
        icon = Image.open(icon_path).convert("RGBA")
        bg = Image.new("RGBA", icon.size, GROUND)
        bg.alpha_composite(icon)
        big = bg.crop((0, 0, 64, 64)).resize((256, 256), Image.NEAREST)
        holder = Image.new("RGBA", (SIZE, 270), (30, 30, 30, 255))
        holder.alpha_composite(bg, (4, 4))
        holder.alpha_composite(big, (4, 4 + icon.height + 6) if icon.height + 6 + 256 < 270 else (130, 4))
        rows.append([label(holder, "icon strip (120x64), and 64 px at 4x")])

    gap = 8
    width = max(sum(im.width for im in row) + gap * (len(row) + 1) for row in rows)
    height = sum(max(im.height for im in row) for row in rows) + gap * (len(rows) + 1)
    sheet = Image.new("RGBA", (width, height), (30, 30, 30, 255))
    y = gap
    for row in rows:
        x = gap
        for im in row:
            sheet.alpha_composite(im, (x, y))
            x += im.width + gap
        y += max(im.height for im in row) + gap
    sheet.save(review)
    print(review, sheet.size)

    frames = []
    for f in range(cr.n):
        p = cr.panel(f, "working")
        fr = Image.new("RGBA", (2 * SIZE, SIZE))
        fr.paste(p, (0, 0))
        fr.paste(zoom(p, ROOFLINE, 3), (SIZE, 0))
        frames.append(fr.convert("RGB"))
    # 12 frames a second: Pillow's GIF duration is in ms and rounds to the 10 ms the
    # format stores, so alternate 80 and 90 for 83.3 on average
    durations = [80 if f % 3 else 90 for f in range(cr.n)]
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=durations, loop=0)
    print(gif, f"{sum(durations)} ms a loop")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: review_sheet.py <out-dir> <review.png> <stroke.gif>")
    main(*sys.argv[1:])
