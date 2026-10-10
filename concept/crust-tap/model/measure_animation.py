#!/usr/bin/env python3
"""The gas-pump-animation task's pass criteria 2 to 4, measured off a render.sh output directory.

  python3 measure_animation.py <out-dir> [measures-animation.json]

  <out-dir>  render.sh's: <out-dir>/renders (pump-NN-<d>, sight-glass-NN-<d>, diag-glass-<d>,
             idle-<d>, still-<d>, pump.json) and <out-dir>/sheets/meta.json
Criterion 1 (round 13's criteria) is measure.py's.

 2  the moving layer loops: its last frame steps to frame 0 as any frame steps to the next
    (the pose itself is periodic by construction: the crank's angle runs 2 pi a loop, the
    needle's kick and the glass's level are 0 at both ends of it); measured as the count of
    pixels (alpha or a channel more than 8 apart) changed between consecutive frames, the
    wrap 23 -> 0 against the rest; and frame 0 over the plate against the still, as pack.py
    measures it (meta.json's frame0_vs_still: at most 3 % of pixels over 8);
 3  the glass layer neutral (channel means within 12) in every frame and nothing outside the
    glass -- measure.py's criterion_glass, all frames, restated here;
 4  the motion reads at 1x: the sheets are at 1x (64 px a tile); the count of pixels the
    moving parts' layer changes (a channel or alpha more than 24 apart) between its two most
    different frames, which must be at least 20 (and, for scale, vanilla's pumpjack head
    measured the same way); with the piston's travel, the crank pin's and the needle tip's,
    in px;
and, as round 13's criterion 4 holds the plate to it, no pixel of the moving layer or of
the glass layer within spec 3.3's frost or seam ranges (the glass's measured after tinting
is the engine's business: it is white).
"""
import json
import math
import os
import sys

from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measure  # noqa: E402

DIRS = measure.DIRS


def load(p):
    return Image.open(p).convert("RGBA")


def changed(a, b, thr):
    d = ImageChops.difference(a, b).get_flattened_data()
    return sum(1 for p in d if max(p) > thr)


def frames_of(sheets, meta, stem):
    im = load(os.path.join(sheets, stem + ".png"))
    m = meta[stem]
    w, h = m["size"]
    line = m["line_length"]
    return [im.crop(((f % line) * w, (f // line) * h, (f % line) * w + w, (f // line) * h + h))
            for f in range(m["frames"])]


def pumpjack():
    """Vanilla's pumpjack nodding head, measured the same way at 1x: its 40 frames of 206 x 172
    at scale 0.5 brought to 103 x 86, the two most different frames' changed pixels (over 24)."""
    path = os.path.join(os.path.dirname(measure.FD), "pumpjack", "pumpjack-horsehead.png")
    im = load(path)
    fr = [im.crop(((i % 8) * 206, (i // 8) * 172, (i % 8) * 206 + 206, (i // 8) * 172 + 172)).resize(
        (103, 86), Image.LANCZOS) for i in range(40)]
    best = max((changed(fr[i], fr[j], 24), i, j) for i in range(40) for j in range(i + 1, 40))
    return dict(most_changed_px=best[0], between_frames=best[1:], source=path)


def main(out, dump=None):
    r, sheets = os.path.join(out, "renders"), os.path.join(out, "sheets")
    meta = json.load(open(os.path.join(sheets, "meta.json")))
    pump = json.load(open(os.path.join(out, "hi", "pump.json")))
    n = pump["frames"]
    res = dict(frames=n, loop_s=pump["loop_s"], declared_fps=n / pump["loop_s"],
               animation_speed_at_progress_1=round(n / pump["loop_s"] / 60, 4))
    c2, c4, ranges = {}, {}, {}
    for d in DIRS:
        fr = frames_of(sheets, meta, f"pump-{d}")
        steps = [changed(fr[f], fr[(f + 1) % n], 8) for f in range(n)]
        c2[d] = dict(step_px=steps[:-1], wrap_px=steps[-1], step_range=[min(steps[:-1]), max(steps[:-1])],
                     wrap_within_steps=min(steps[:-1]) <= steps[-1] <= max(steps[:-1]),
                     frame0_vs_still=meta["checks"][d].get("frame0_vs_still"),
                     slide=meta["checks"][d].get("pump_path_px"))
        best = max(((changed(fr[i], fr[j], 24), i, j) for i in range(n) for j in range(i + 1, n)))
        c4[d] = dict(most_changed_px=best[0], between_frames=best[1:], at_1x=True,
                     frame_px=meta[f"pump-{d}"]["size"])
        frost = seam = 0
        for f in fr + frames_of(sheets, meta, f"sight-glass-{d}"):
            px = [p[:3] for p in f.get_flattened_data() if p[3] > 128]
            frost += sum(measure.near_segment(c, measure.FROST) for c in px)
            seam += sum(measure.near_segment(c, measure.SEAM) for c in px)
        ranges[d] = dict(frost_px=frost, seam_px=seam)
        g = frames_of(sheets, meta, f"sight-glass-{d}")
        gsteps = [changed(g[f], g[(f + 1) % n], 8) for f in range(n)]
        c2[d]["glass_step_range"], c2[d]["glass_wrap_px"] = [min(gsteps[:-1]), max(gsteps[:-1])], gsteps[-1]
    xs = [p[0] for p in pump["path"]]
    travel = dict(piston_px=round((max(xs) - min(xs)) * 64, 1),
                  crank_pin_px=dict(across=round(2 * pump.get("throw", 0.075) * 64, 1),
                                    up_down=round(2 * pump.get("throw", 0.075) * 64 * math.cos(math.radians(60)), 1)),
                  needle_tip_px=round(2 * math.sin(pump["needle_kick"] / 2) * pump.get("needle_len", 0.039) * 64, 1))
    res.update(c2=c2, c3=measure.criterion_glass(r, n), c4=c4, c4_travel=travel, frost_seam=ranges,
               vanilla_pumpjack=pumpjack())
    print(json.dumps(res, indent=1))
    if dump:
        with open(dump, "w") as f:
            json.dump(res, f, indent=1)


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("usage: measure_animation.py <out-dir> [measures-animation.json]")
    main(*sys.argv[1:])
