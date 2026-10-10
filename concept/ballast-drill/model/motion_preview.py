#!/usr/bin/env python3
"""The Ballast Drill's working motion (round 6: spec 3.2 as agreed 2026-10-10), at 1x and 2x and
beside vanilla's big mining drill, composed from the packed layers as the engine draws them.

  python3 motion_preview.py <out-dir> <dest-dir>

  <out-dir>   render.sh's output directory: renders/ (idle, shadow, lamp, chute-NN,
              stroke-NN, ore-NN, dust-NN, facing north)
  <dest-dir>  writes:
    motion-1x.gif            north, working, at game speed (animation_speed 0.4: 24 frames a
                             second; each GIF frame is 2.5 ticks, 40 ms)
    motion-2x.gif            the same, 2x nearest-neighbour
    motion-vs-vanilla.gif    1x, ours beside vanilla's big mining drill at work (north, its
                             steady drilling loop: drill, dust, support, top, nozzle, output,
                             particles, each at its own frame for the same tick), 240 ticks so
                             every loop closes
    motion-preview.png       1x: every frame in a strip, the stroke curve against the sine it
                             replaced, and the dust layer alone with its channel means

Each machine on one ground at 64 px a tile, its shadow at 50 %, the status lamp tinted
vanilla's working green. Every layer that takes the ore's tint (ours: ore and dust;
vanilla's: dust-tint and particles) is tinted with iron ore's mining_visualisation_tint, as
on an iron patch; the preview's dust strip is the layer as rendered, neutral.
"""
import os
import re
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compare_plates as cp  # noqa: E402   vanilla_layer(), at()

GROUND = (74, 66, 58, 255)
PPT = 64
S = 440                                 # the 1x panel; origin at its centre
CANVAS = (416, 400)                     # the model's canvas, origin at (208, 200)
FRAMES = 24
TICKS_PER_GIF_FRAME = 2.5               # ours: one frame; vanilla (speed 0.5): 1.25 frames
GIF_MS = 40
IRON = (0.895, 0.965, 1.0)              # iron ore's mining_visualisation_tint
GREEN = (0, 255, 0)


def panel():
    return Image.new("RGBA", (S, S), GROUND)


def put(c, im):
    """A render on the model's canvas, its origin on the panel's."""
    c.alpha_composite(im, (S // 2 - CANVAS[0] // 2, S // 2 - CANVAS[1] // 2))


def as_shadow(im, k=0.5):
    a = im.getchannel("A").point(lambda v: int(v * k))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.putalpha(a)
    return out


def tint(im, rgb):
    r, g, b, a = im.split()
    return Image.merge("RGBA", (r.point(lambda v: int(v * rgb[0])), g.point(lambda v: int(v * rgb[1])),
                                b.point(lambda v: int(v * rgb[2])), a))


def lamp_green(im):
    lum = im.convert("L")
    return Image.merge("RGBA", (*[lum.point(lambda v, c=c: v * c // 255) for c in GREEN], im.getchannel("A")))


def ours(out_dir):
    R = os.path.join(out_dir, "renders")
    ren = lambda stem: Image.open(os.path.join(R, stem + ".png")).convert("RGBA")  # noqa: E731
    shadow = as_shadow(ren("shadow-north"))
    plate = ren("idle-north")
    lamp = lamp_green(ren("lamp-north"))
    frames = []
    for f in range(FRAMES):
        c = panel()
        put(c, shadow)
        put(c, plate)
        put(c, ren(f"chute-{f % 5:02d}-north"))
        put(c, ren(f"stroke-{f:02d}-north"))
        put(c, tint(ren(f"ore-{f:02d}-north"), IRON))
        put(c, tint(ren(f"dust-{f:02d}-north"), IRON))
        put(c, lamp)
        frames.append(c)
    return frames


def vanilla_frame(tick):
    """Vanilla's big mining drill facing north at tick `tick` of its steady drilling loop."""
    n = int(tick * 0.5)                                  # its animation_speed
    c = panel()
    layers = [  # (file, frame, position, kind)
        ("North/big-mining-drill-N-still-shadow", 0, (0, 0), "shadow"),
        ("big-mining-drill-drill-shadow", 12 + n % 12, (0, 0.15), "shadow"),
        ("North/big-mining-drill-N-support-shadow", 0, (0, 0), "shadow"),
        ("North/big-mining-drill-N-top-shadow", n % 6, (0, 0), "shadow"),
        ("North/big-mining-drill-N-still", 0, (0, 0), None),
        ("big-mining-drill-drill", 12 + n % 12, (0, 0.15), None),
        ("big-mining-drill-drill-dust", n % 24, (0, 0.15), None),
        ("big-mining-drill-drill-dust-tint", n % 24, (0, 0.15), "tint"),
        ("North/big-mining-drill-N-still", 0, (0, 0), None),
        ("North/big-mining-drill-N-output", n % 5, (0, 0), None),
        ("North/big-mining-drill-N-support", n % 6, (0, 0), None),
        ("North/big-mining-drill-N-still-front", 0, (0, 0), None),
        ("North/big-mining-drill-N-output-particles", n % 24, (0, 0), "tint"),
        ("North/big-mining-drill-N-top-nozzle", n % 6, (0, 0), None),
        ("North/big-mining-drill-N-top", n % 6, (0, 0), None),
    ]
    for rel, fr, pos, kind in layers:
        im, sx, sy = cp.vanilla_layer(rel, fr, pos)
        if kind == "shadow":
            im = as_shadow(im)
        elif kind == "tint":
            im = tint(im, IRON)
        x, y = round(S / 2 + sx * PPT - im.width / 2), round(S / 2 + sy * PPT - im.height / 2)
        c.alpha_composite(im, (x, y))
    return c


def crop_machine(c):
    x0, y0 = S // 2 - round(2.85 * PPT), S // 2 - round(3.3 * PPT)
    return c.crop((x0, y0, x0 + round(5.7 * PPT), y0 + round(6.1 * PPT)))


def label(im, text):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, im.width, 14), fill=(20, 20, 20, 255))
    d.text((3, 1), text, fill=(235, 235, 235, 255))
    return im


def save_gif(frames, path):
    pal = [f.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
           for f in frames]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=GIF_MS, loop=0, disposal=1)
    print(path, len(frames), "frames")


def side_by_side(a, b, la, lb, k=1):
    a, b = crop_machine(a), crop_machine(b)
    if k != 1:
        a, b = (q.resize((q.width * k, q.height * k), Image.NEAREST) for q in (a, b))
    w, h = a.size
    out = Image.new("RGBA", (2 * w + 6, h + 16), (30, 30, 30, 255))
    out.paste(a, (0, 16))
    out.paste(b, (w + 6, 16))
    d = ImageDraw.Draw(out)
    d.text((3, 2), la, fill=(235, 235, 235, 255))
    d.text((w + 9, 2), lb, fill=(235, 235, 235, 255))
    return out


def curve_plot(w, h):
    """The proposal's drop against the packed sine, read back from the model's own tables."""
    src = open(os.path.join(HERE, "ballast_drill.py")).read()
    import math
    sine = [(1 - math.cos(2 * math.pi * f / FRAMES)) / 2 for f in range(FRAMES)]
    ns = {"FRAMES": FRAMES}
    exec(re.search(r"def _lift\(f\):.*?\n\n\n", src, re.S).group(0), ns)
    exec(re.search(r"W_DROP = .*", src).group(0), ns)
    prop = ns["W_DROP"]
    im = Image.new("RGBA", (w, h), (24, 24, 24, 255))
    d = ImageDraw.Draw(im)
    x = lambda f: 30 + (w - 50) * f / FRAMES  # noqa: E731
    y = lambda v: 20 + (h - 40) * v  # noqa: E731   0 raised (top), 1 seated (bottom)
    for f in range(FRAMES + 1):
        d.line([(x(f), 18), (x(f), h - 18)], fill=(50, 50, 50, 255))
    for v, t in ((0, "raised"), (1, "seated (12 px)")):
        d.text((x(0) + 2, y(v) - 12 if v else y(v) + 2), t, fill=(150, 150, 150, 255))
    for seq, col, name in ((sine, (120, 120, 200, 255), "sine"), (prop, (240, 170, 60, 255), "stroke")):
        pts = [(x(f), y(seq[f % FRAMES])) for f in range(FRAMES + 1)]
        d.line(pts, fill=col, width=2)
        for p in pts:
            d.ellipse((p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2), fill=col)
    d.text((w - 170, 4), "sine (round 5)", fill=(120, 120, 200, 255))
    d.text((w - 70, 4), "stroke", fill=(240, 170, 60, 255))
    for f in range(0, FRAMES, 2):
        d.text((x(f) - 4, h - 15), str(f), fill=(150, 150, 150, 255))
    return im


def dust_strip(out_dir):
    """The dust layer alone, on the ground, at 1x, and its mean colour over its opaque pixels."""
    R = os.path.join(out_dir, "renders")
    names = sorted(n for n in os.listdir(R) if n.startswith("dust-") and n.endswith("-north.png"))
    tiles, tot, n = [], [0, 0, 0], 0
    for name in names:
        im = Image.open(os.path.join(R, name)).convert("RGBA")
        if im.getchannel("A").getbbox() is None:
            continue
        for (r, g, b, a) in im.get_flattened_data():
            if a > 64:
                tot[0] += r
                tot[1] += g
                tot[2] += b
                n += 1
        c = Image.new("RGBA", CANVAS, GROUND)
        c.alpha_composite(im)
        cx, cy = CANVAS[0] // 2, CANVAS[1] // 2
        tiles.append(label(c.crop((cx - 120, cy - 110, cx + 120, cy + 70)), name[:-4]))
    mean = [round(v / max(n, 1)) for v in tot]
    return tiles, mean


def main(out_dir, dest):
    os.makedirs(dest, exist_ok=True)
    mine = ours(out_dir)
    save_gif([crop_machine(f) for f in mine], os.path.join(dest, "motion-1x.gif"))
    save_gif([crop_machine(f).resize((crop_machine(f).width * 2, crop_machine(f).height * 2), Image.NEAREST)
              for f in mine], os.path.join(dest, "motion-2x.gif"))
    n_gif = int(240 / TICKS_PER_GIF_FRAME)
    pairs = []
    for i in range(n_gif):
        tick = i * TICKS_PER_GIF_FRAME
        pairs.append((mine[i % FRAMES], vanilla_frame(tick)))
    la, lb = "Ballast Drill, working (iron)", "vanilla big mining drill, working (iron)"
    save_gif([side_by_side(a, b, la, lb) for a, b in pairs], os.path.join(dest, "motion-vs-vanilla.gif"))
    # (no 2x side by side: at 37 MB it was too big to send)

    # the preview: every frame at 1x in a strip (three rows of eight), the curve, the dust
    tiles = [label(crop_machine(f), f"frame {i}" + ("  landing" if i == 5 else "")) for i, f in enumerate(mine)]
    tw, th = tiles[0].size
    dtiles, mean = dust_strip(out_dir)
    dw, dh = dtiles[0].size if dtiles else (0, 0)
    W = 8 * (tw + 4)
    H = 3 * (th + 4) + 190 + (dh + 24 if dtiles else 0)
    sheet = Image.new("RGBA", (W, H), (30, 30, 30, 255))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 8) * (tw + 4), (i // 8) * (th + 4)))
    y = 3 * (th + 4)
    sheet.paste(curve_plot(min(W, 900), 180), (0, y + 4))
    d = ImageDraw.Draw(sheet)
    d.text((min(W, 900) + 12, y + 10), "the stroke (orange) against the sine it replaced (blue)", fill=(220, 220, 220, 255))
    d.text((min(W, 900) + 12, y + 26), "frames 0-1 hang; 2-5 fall under gravity (1/16, 4/16, 9/16, 1);", fill=(200, 200, 200, 255))
    d.text((min(W, 900) + 12, y + 40), "5 lands dead; 6 rebounds 1 px; 7-12 seated; 13-23 winched up", fill=(200, 200, 200, 255))
    d.text((min(W, 900) + 12, y + 60), "jolt at 5-7: frame, winches, roof cables 2, -1, 0.5 px", fill=(200, 200, 200, 255))
    d.text((min(W, 900) + 12, y + 74), "slung hose swings toward the camera and dies out", fill=(200, 200, 200, 255))
    d.text((min(W, 900) + 12, y + 88), "winch gears turn with the rope: slow up, fast down", fill=(200, 200, 200, 255))
    d.text((min(W, 900) + 12, y + 102), "dust bursts out from under the band at 5, gone by 14", fill=(200, 200, 200, 255))
    if dtiles:
        y += 190
        d.text((4, y + 4), f"the dust layer alone, neutral (mean RGB of its pixels {mean}; spread "
                           f"{max(mean) - min(mean)}), as the engine would tint it by the ore", fill=(220, 220, 220, 255))
        for i, t in enumerate(dtiles[: W // (dw + 4)]):
            sheet.paste(t, (i * (dw + 4), y + 20))
    sheet.save(os.path.join(dest, "motion-preview.png"))
    print(os.path.join(dest, "motion-preview.png"), sheet.size, "dust mean", mean)


if __name__ == "__main__":
    main(*sys.argv[1:])
