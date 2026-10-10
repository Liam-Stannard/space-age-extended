#!/usr/bin/env python3
"""The Ballast Drill's blockout review: the plate with its chute in every direction,
beside the adopted plate and vanilla's big mining drill, and the stroke and chain frames.

  python3 review_blockout.py <out-dir> <review.png> <stroke.png> <stroke.gif> [<ports-dir>]

  <out-dir>    render.sh's output directory (renders/, sheets/meta.json)
  <ports-dir>  the model run with --ports and downsampled: port-<face>.png, drawn on the
               plate in a last row as the engine turns them with the drill

Everything is on one ground at 64 px a tile, with the 5x5 tile grid, layered as the
engine draws it: the shadow at 50 %, the plate, the chute's frame, the stroke's frame,
the lamp (left white: the blockout's lens).

Row 1: the adopted plate (graphics/entity/ballast-drill/base.png at its shift), then the
       blockout facing north, east, south and west. On each, vanilla's
       big-mining-drill-<D>-output rectangle at its own size and shift (cyan), and the
       chute layer's crop (magenta): criterion 2 is their centres within 2 px.
Row 2: vanilla's big mining drill facing north (still, top, output), the blockout north,
       and the two side by side as silhouettes with their drawn heights.
Row 3: the chain, 5 frames and the loop frame (frame 5, rendered to check it is frame 0)
       in every direction, 2x on the chute's own crop.
Row 5: every bay, shut (the plate) and working (its chute over it), 2x with the 1x inset;
       the label counts the shut door's pixels (door-<d>.png: the door alone, everything in
       front held out, alpha over 127) where the chute layer is less opaque than the
       door by more than 8 (on an occluder's antialiased edge both are clipped alike).
Row 6 (with <ports-dir>): every direction with all four fluid connections fitted, as the
       engine turns them with the drill; north-facing pictures behind the plate.

<stroke.png>: all 24 stroke frames, 1.5x on the press, each with its drop in px.
<stroke.gif>: the stroke at game speed (animation_speed 0.4: 24 frames a second), north.
"""
import json
import os
import re
import sys

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import contract  # noqa: E402

FD = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "space-age/graphics/entity/big-mining-drill")
PPT = 64
C = 448                                  # panel size; origin at its centre
O = C / 2
GROUND = (74, 66, 58, 255)
GAP = (30, 30, 30, 255)
DIRS = ("north", "east", "south", "west")
FACES_ = "NESW"
LONG = dict(N="North", E="East", S="South", W="West")


def lua(stem):
    t = open(stem + ".lua").read()
    w = int(re.search(r"width = (\d+)", t).group(1))
    h = int(re.search(r"height = (\d+)", t).group(1))
    sx, sy = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)", t).groups())
    return w, h, sx / 32, sy / 32


def vanilla(d, part):
    stem = os.path.join(FD, LONG[d], f"big-mining-drill-{d}-{part}")
    w, h, sx, sy = lua(stem)
    return Image.open(stem + ".png").convert("RGBA").crop((0, 0, w, h)), sx, sy


def panel():
    return Image.new("RGBA", (C, C), GROUND)


def grid(c):
    d = ImageDraw.Draw(c, "RGBA")
    for i in range(6):
        v = O + (i - 2.5) * PPT
        d.line([(v, O - 160), (v, O + 160)], fill=(255, 255, 255, 45))
        d.line([(O - 160, v), (O + 160, v)], fill=(255, 255, 255, 45))


def put(c, im, sx=0.0, sy=0.0):
    """An image centred on the origin moved by (sx, sy) tiles."""
    c.alpha_composite(im, (round(O + sx * PPT - im.width / 2), round(O + sy * PPT - im.height / 2)))


def shadow(c, im):
    a = im.getchannel("A").point(lambda v: v // 2 if v >= 24 else 0)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    lay.putalpha(a)
    put(c, lay)


def label(c, text):
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, C, 16], fill=(20, 20, 20, 200))
    d.text((5, 2), text, fill=(235, 235, 235, 255))


def row(panels, scale=1):
    w = sum(p.width for p in panels) + 6 * (len(panels) - 1)
    h = max(p.height for p in panels)
    out = Image.new("RGBA", (w, h), GAP)
    x = 0
    for p in panels:
        out.paste(p, (x, 0))
        x += p.width + 6
    return out


def main(out_dir, dest, stroke_png, stroke_gif, ports_dir=None):
    R = os.path.join(out_dir, "renders")
    meta = json.load(open(os.path.join(out_dir, "sheets", "meta.json")))
    ren = lambda stem: Image.open(os.path.join(R, stem + ".png")).convert("RGBA")  # noqa: E731

    def machine(d, f_stroke=0, f_chain=0, with_shadow=True):
        c = panel()
        if with_shadow:
            shadow(c, ren(f"shadow-{d}"))
        put(c, ren(f"idle-{d}"))
        put(c, ren(contract.frame("chute", f_chain, d)))
        put(c, ren(contract.frame("stroke", f_stroke, d)))
        return c

    # row 1
    r1 = []
    c = panel()
    ad = Image.open(os.path.join(REPO, "graphics/entity/ballast-drill/base.png")).convert("RGBA")
    put(c, ad, 0, 0.13281)
    grid(c)
    label(c, "adopted plate (base.png)")
    r1.append(c)
    for d in DIRS:
        c = machine(d)
        grid(c)
        dd = ImageDraw.Draw(c, "RGBA")
        v, sx, sy = vanilla(d[0].upper(), "output")
        dd.rectangle([O + sx * PPT - v.width / 2, O + sy * PPT - v.height / 2,
                      O + sx * PPT + v.width / 2, O + sy * PPT + v.height / 2], outline=(0, 230, 255, 220))
        m = meta[f"chute-{d}"]
        w, h = m["size"]
        mx, my = m["shift"]
        dd.rectangle([O + mx * PPT - w / 2, O + my * PPT - h / 2, O + mx * PPT + w / 2, O + my * PPT + h / 2],
                     outline=(255, 60, 220, 220))
        off = ((mx - sx) * PPT, (my - sy) * PPT)
        label(c, f"blockout {d}: chute crop off vanilla's by ({off[0]:+.1f}, {off[1]:+.1f}) px")
        r1.append(c)

    # row 2: height against vanilla's big mining drill
    r2 = []
    c = panel()
    for part in ("still", "top", "output"):
        im, sx, sy = vanilla("N", part)
        put(c, im, sx, sy)
    grid(c)
    van_alpha = Image.new("L", (C, C))
    tmp = Image.new("RGBA", (C, C))
    for part in ("still", "top", "output"):
        im, sx, sy = vanilla("N", part)
        tmp.alpha_composite(im, (round(O + sx * PPT - im.width / 2), round(O + sy * PPT - im.height / 2)))
    van_alpha = tmp.getchannel("A").point(lambda v: 255 if v > 20 else 0)
    vb = van_alpha.getbbox()
    label(c, f"vanilla big mining drill N: {vb[3] - vb[1]} px drawn, top {vb[1] - O:+.0f}")
    r2.append(c)
    c = machine("north")
    grid(c)
    ours = Image.new("RGBA", (C, C))
    for stem in ("idle-north", contract.frame("chute", 0, "north"), contract.frame("stroke", 0, "north")):
        im = ren(stem)
        ours.alpha_composite(im, (round(O - im.width / 2), round(O - im.height / 2)))
    ob = ours.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    adb = Image.new("RGBA", (C, C))
    adb.alpha_composite(ad, (round(O - ad.width / 2), round(O + 0.13281 * PPT - ad.height / 2)))
    ab = adb.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    label(c, f"blockout N: {ob[3] - ob[1]} px drawn, top {ob[1] - O:+.0f} (adopted {ab[3] - ab[1]})")
    r2.append(c)
    c = panel()
    sil = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    sil.paste((40, 200, 255, 110), (0, 0), van_alpha.point(lambda v: v))
    c.alpha_composite(sil)
    sil = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    sil.paste((255, 120, 40, 110), (0, 0), ours.getchannel("A").point(lambda v: 255 if v > 20 else 0))
    c.alpha_composite(sil)
    grid(c)
    dd = ImageDraw.Draw(c)
    for y, col in ((vb[1], (40, 200, 255)), (ob[1], (255, 120, 40)), (ab[1], (255, 255, 255))):
        dd.line([(0, y), (C, y)], fill=(*col, 255))
    label(c, "silhouettes: vanilla (blue), blockout N (orange); white = adopted top")
    r2.append(c)
    c = panel()
    put(c, ren("still-north"))
    grid(c)
    label(c, "the still render (frame-0 reference)")
    r2.append(c)
    c = machine("north", f_stroke=12)
    grid(c)
    label(c, "blockout N, stroke frame 12: the ring seated")
    r2.append(c)

    # the stroke: its own strip and GIF
    box = tuple(round(v) for v in (O - 2.4 * PPT, O - 2.75 * PPT, O + 2.4 * PPT, O + 1.3 * PPT))
    drops = json.load(open(os.path.join(out_dir, "hi", "stroke.json")))["drop"]       # the model's, in tiles
    frames = []
    for f in range(24):
        c = machine("north", f_stroke=f)
        im = c.crop(box)
        im = im.resize((round(im.width * 1.5), round(im.height * 1.5)), Image.LANCZOS)
        frames.append(im.copy())
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 150, 16], fill=(20, 20, 20, 200))
        d.text((4, 2), f"frame {f}: drop {drops[f] * 32:.2f} px", fill=(235, 235, 235, 255))
        frames[-1] = (frames[-1], im)
    fw, fh = frames[0][1].size
    strip = Image.new("RGBA", (6 * (fw + 4), 4 * (fh + 4)), GAP)
    for i, (_, im) in enumerate(frames):
        strip.paste(im, ((i % 6) * (fw + 4), (i // 6) * (fh + 4)))
    strip.save(stroke_png)
    gif = [fr.convert("RGB") for fr, _ in frames]
    gif[0].save(stroke_gif, save_all=True, append_images=gif[1:], duration=42, loop=0)

    # row 3: the chain, per direction, on its own crop (meta.json)
    r4 = []
    for d in DIRS:
        cx, cy = meta[f"chute-{d}"]["shift"]
        for f in list(range(5)) + ["loop"]:
            c = panel()
            put(c, ren(f"idle-{d}"))
            stem = contract.frame("chute", f, d) if f != "loop" else f"chute-loop-{d}"
            src = os.path.join(R, stem + ".png")
            if not os.path.isfile(src):
                continue
            put(c, Image.open(src).convert("RGBA"))
            im = c.crop((round(O + (cx - 0.75) * PPT), round(O + (cy - 0.75) * PPT),
                         round(O + (cx + 0.75) * PPT), round(O + (cy + 0.75) * PPT)))
            im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
            dr = ImageDraw.Draw(im)
            dr.rectangle([0, 0, 64, 14], fill=(20, 20, 20, 200))
            dr.text((3, 1), f"{d[0].upper()} {f}", fill=(235, 235, 235, 255))
            r4.append(im)
    r4a, r4b = r4[:12], r4[12:]

    # row 5: the bays, shut and working
    r6 = []
    for d in DIRS:
        cx, cy = meta[f"chute-{d}"]["shift"]
        idle = ren(f"idle-{d}")
        ch = ren(contract.frame("chute", 0, d))
        da, ca = ren(f"door-{d}").getchannel("A").load(), ch.getchannel("A").load()
        door = uncovered = 0
        for y in range(idle.height):
            for x in range(idle.width):
                if da[x, y] > 127:                # the shut door, as the camera sees it in the plate
                    door += 1
                    # covered where the chute is at least as opaque as the door: on an
                    # occluder's antialiased edge both are clipped alike
                    uncovered += da[x, y] > ca[x, y] + 8
        for working in (False, True):
            c = panel()
            put(c, idle)
            if working:
                put(c, ch)
            put(c, ren(contract.frame("stroke", 0, d)))
            box_ = (round(O + (cx - 0.8) * PPT), round(O + (cy - 0.8) * PPT),
                    round(O + (cx + 0.8) * PPT), round(O + (cy + 0.8) * PPT))
            one = c.crop(box_)
            two = one.resize((one.width * 2, one.height * 2), Image.NEAREST)
            im = Image.new("RGBA", (two.width + one.width + 4, two.height), GAP)
            im.paste(two, (0, 0))
            im.paste(one, (two.width + 4, two.height - one.height))
            dr = ImageDraw.Draw(im)
            dr.rectangle([0, 0, im.width, 14], fill=(20, 20, 20, 200))
            dr.text((3, 1), f"{d} {'working' if working else 'shut'}" +
                    (f": door px {door}, uncovered {uncovered}" if working else ""), fill=(235, 235, 235, 255))
            r6.append(im)

    rows = [row(r1), row(r2), row(r4a), row(r4b), row(r6)]
    if ports_dir:
        decl = contract.load(ports_dir)
        declared = {p["face"]: p["tile"] for p in decl["ports"]}
        conns = [((-2, -1), "W"), ((2, -1), "E"), ((1, 2), "S"), ((-1, 2), "S")]   # big-mining-drill's
        pics = {f: Image.open(os.path.join(ports_dir, f"port-{f}.png")).convert("RGBA") for f in FACES_}
        r5 = []
        for k, d in enumerate(DIRS):
            turned = []
            for (x, y), face in conns:
                for _ in range(k):
                    x, y = -y, x
                    face = FACES_[(FACES_.index(face) + 1) % 4]
                turned.append(((x, y), face))
            c = panel()
            shadow(c, ren(f"shadow-{d}"))
            for front in (False, True):
                if front:
                    put(c, ren(f"idle-{d}"))
                    put(c, ren(contract.frame("chute", 0, d)))
                    put(c, ren(contract.frame("stroke", 0, d)))
                for (x, y), face in turned:
                    if (face != "N") == front:
                        tx, ty = declared[face]
                        put(c, pics[face], x - tx, y - ty)
            grid(c)
            label(c, f"{d}: all four connections fitted (" + ", ".join(f"{f}{t}" for t, f in turned) + ")")
            r5.append(c)
        rows.append(row(r5))
    W = max(r.width for r in rows)
    H = sum(r.height for r in rows) + 10 * (len(rows) - 1)
    sheet = Image.new("RGBA", (W, H), GAP)
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height + 10
    sheet.save(dest)
    print(dest, sheet.size)


if __name__ == "__main__":
    main(*sys.argv[1:])
