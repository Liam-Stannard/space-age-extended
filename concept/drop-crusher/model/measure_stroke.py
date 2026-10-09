#!/usr/bin/env python3
"""The Drop Crusher's stroke, measured off its renders: the task's pass criteria 2 and 3.

  python3 measure_stroke.py <out-dir>

  <out-dir>  render.sh's output directory: <out-dir>/renders (sprite size) and
             <out-dir>/hi (the 4x renders and stroke.json the model wrote)

pack.py now measures the crown's slide itself, on the contract's tracked part (the
stroke's `track`, "crown": stroke-crown-NN, the crown and shank rendered alone); this
script measures it again the same way, and the gears, which pack.py does not: the
model also renders the east gear alone (diag-gear-NN), unpacked, in every frame.

2. The crown: its centroid in every frame, against the declared curve (render.json's
   path, put on the screen: a tile of height is cos(elevation) tiles up the screen),
   the constant offset between the crown's centroid and the seat fitted out, as
   pack.py's slide check does; across the line, its drift from the vertical. And the
   fall: each frame's travel from 16 to 24 (= 0) larger than the last.
3. The gears: the east gear's turn in every frame, measured by matching the frame
   against frame 0 turned, the gear's plane stretched back to a circle (it lies
   upright in the east-west plane, so it draws half as tall as wide). Unwrapped
   frame to frame; held to the rack's travel over the pitch radius, in teeth.
"""
import json
import math
import os
import sys

from PIL import Image, ImageChops, ImageStat  # noqa: F401

LIMIT_PX = 1.0


def centroid(im):
    a = im.getchannel("A")
    w = h = 0
    sx = sy = 0.0
    W = a.width
    for i, v in enumerate(a.get_flattened_data()):
        if v:
            w += v
            sx += v * (i % W)
            sy += v * (i // W)
    return sx / w, sy / w


def crown(out, info):
    n = info["frames"]
    cs = [centroid(Image.open(os.path.join(out, "renders", f"stroke-crown-{f:02d}.png")).convert("RGBA"))
          for f in range(n)]
    k = info["px_per_tile"] * info["cos_elevation"]
    declared = [-k * s for s in info["lift"]]                 # screen px, down positive
    res = [(cy - cs[0][1]) - d for (cx, cy), d in zip(cs, declared)]
    off = sum(res) / n
    curve = [r - off for r in res]
    mx = sum(cx for cx, _ in cs) / n
    line = [cx - mx for cx, _ in cs]
    measured = [round(-(cy - cs[0][1]), 2) for _, cy in cs]
    # the fall: frames RISE..n-1 and back to 0
    rise = info["rise"]
    ys = [cs[f % n][1] for f in range(rise, n + 1)]
    steps = [round(b - a, 2) for a, b in zip(ys, ys[1:])]
    grows = all(b > a for a, b in zip(steps, steps[1:]))
    proud_px = max(measured)
    return dict(declared_up_px=[round(-d, 2) for d in declared], measured_up_px=measured,
                off_curve_px=round(max(abs(v) for v in curve), 2), off_line_px=round(max(abs(v) for v in line), 2),
                fall_steps_px=steps, fall_grows_strictly=grows,
                top_lift_tiles=round(max(info["lift"]), 3),
                crown_proud_at_top=f"{max(info['lift']):.2f} tiles of a {info['crown_height']:.2f}-tile crown "
                                   f"({max(info['lift']) / info['crown_height']:.2f} x its height)")


def gear_image(path, info, centre):
    """The east gear, un-squashed to a circle, greyscale on mid grey, at 4x, about
    `centre` (4x px)."""
    ss = info["ss"]
    cx, cy = centre
    r = (info["gear_tip"] + 0.02) * info["px_per_tile"] * ss
    im = Image.open(path).convert("RGBA")
    box = (round(cx - r), round(cy - r / 2), round(cx + r), round(cy + r / 2))
    crop = im.crop(box)
    bg = Image.new("RGBA", crop.size, (128, 128, 128, 255))
    bg.alpha_composite(crop)
    g = bg.convert("L").resize((round(2 * r), round(2 * r)), Image.BICUBIC)
    return g.resize((160, 160), Image.LANCZOS)


def turned(base, deg):
    return base.rotate(deg, resample=Image.BICUBIC, fillcolor=128)


def score(a, b, mask):
    d = ImageChops.difference(a, b)
    return ImageStat.Stat(d, mask).mean[0]


def gears(out, info):
    n = info["frames"]
    paths = [os.path.join(out, "hi", f"diag-gear-{f:02d}.png") for f in range(n)]
    # the gear's centre: its alpha centroid in frame 0 (it is round, so its centroid is its axle)
    # (its axle's), moved down to the spokes' front faces, 0.04 tiles south of the
    # gear's mid-plane: on the screen a tile south is a tile down
    cx, cy = centroid(Image.open(paths[0]).convert("RGBA"))
    centre = (cx, cy + 0.04 * info["px_per_tile"] * info["ss"])
    frames = [gear_image(p, info, centre) for p in paths]
    # the five lightening holes: brightness round the ring through them, and the phase
    # of its fifth harmonic, which turns with the gear (mod 72 degrees); unwrapped frame
    # to frame, as no frame turns it as much as 36
    rr = 80 / (info["gear_tip"] + 0.02) * info["hole_r"]

    def phase(im):
        px = im.load()
        c = s_ = 0.0
        for k in range(720):
            t = math.radians(k / 2)
            v = sum(px[80 + r * math.cos(t), 80 - r * math.sin(t)] for r in (rr - 3, rr - 1.5, rr, rr + 1.5, rr + 3))
            c += v * math.cos(5 * t)
            s_ += v * math.sin(5 * t)
        return math.degrees(math.atan2(s_, c)) / 5
    p0 = phase(frames[0])
    got = [0.0]
    for f in range(1, n):
        d = (phase(frames[f]) - p0 - got[-1] + 36) % 72 - 36
        got.append(round(got[-1] + d, 1))
    # the model turns the east gear by -lift / rg (radians): clockwise on the screen as the
    # rack rises past its west side; on the screen, PIL's positive angle is anticlockwise
    want = [round(-math.degrees(s / info["rg"]), 1) for s in info["lift"]]
    tooth = 360 / info["teeth"]
    err = [round(abs(g - w), 1) for g, w in zip(got, want)]
    return dict(declared_deg=want, measured_deg=got, max_error_deg=max(err),
                max_error_teeth=round(max(err) / tooth, 2), tooth_deg=tooth,
                note="the gear's turn against the rack's travel over its pitch radius; within one tooth passes")


def main(out):
    info = json.load(open(os.path.join(out, "hi", "stroke.json")))
    c = crown(out, info)
    g = gears(out, info)
    res = dict(crown=c, gear=g,
               pass_2=c["off_curve_px"] <= LIMIT_PX and c["off_line_px"] <= LIMIT_PX and c["fall_grows_strictly"],
               pass_3=g["max_error_teeth"] <= 1.0)
    print(json.dumps(res, indent=1))
    with open(os.path.join(out, "stroke-measures.json"), "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: measure_stroke.py <out-dir>")
    main(sys.argv[1])
