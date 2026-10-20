#!/usr/bin/env python3
"""The Drop Crusher's sound against its stroke, and beside vanilla's crusher.

  tools/audio/.venv/bin/python concept/drop-crusher/sound/review_drop_crusher.py

Run drop_crusher_sound.py first. Writes, beside this file:

  review.mp4        the stroke at the game's 0.1 frames a tick (four seconds a
                    drop), three strokes, the bed under it at its proposed volume,
                    the pawl on frames 18, 22 and 2, the trip on 6 and the drop on 14
                    (the loop starts cocked: drop_crusher_sound.py)
  side-by-side.mp4  the same three strokes, then vanilla's crusher for the whole
                    number of its 192-tick cycles nearest that (four), each heard in turn

and prints the loudness of each mix as the game would play it, ours beside
vanilla's, and where each accent actually sits in the MP4's decoded audio.

**Our crusher, as drawn here**, is put together from the shipped sheets the way
the prototype layers them (model/sheets/meta.json, prototypes/core/machines.lua):
the cast shadow, the plate (base.png) and the 24-frame stroke window over it,
each at its own shift, at the sheets' own scale (64 px a tile). **Vanilla's**
is its north-facing sheet, crusher-vertical.png, 48 frames of 140 x 194 eight to
a row, with its shadow, at the same scale; it plays at 0.5 x crafting speed 1 x
animation_progress 0.5 = 0.25 frames a tick (crusher-pictures.lua sets no
progress, so the default), and its sound is its prototype's: crusher-loop.ogg at
0.8, no accents.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools" / "audio"))
sys.path.insert(0, str(HERE))

import imageio_ffmpeg  # noqa: E402
import numpy as np  # noqa: E402
import loudness  # noqa: E402
import review  # noqa: E402
import sfx  # noqa: E402
import drop_crusher_sound as dc  # noqa: E402

SND = REPO / "sound" / "drop-crusher"
SHEETS = HERE.parent / "model" / "sheets"
GROUND = (74, 66, 58)          # the Ballast Drill review's ground, so the two reviews match
LOOPS = 3

VC_G = sfx.data_dir() / "space-age" / "graphics" / "entity" / "crusher"
V_SPEED = 0.25
W, H, OX, OY = 320, 288, 150, 160    # holds both machines and their shadows


def _paste(canvas, rgba, cx, cy, shadow=False):
    h, w = rgba.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    a = rgba[..., 3:4].astype(np.float32) / 255.0
    src = np.zeros_like(rgba[..., :3], dtype=np.float32) if shadow else rgba[..., :3].astype(np.float32)
    region = canvas[y0:y0 + h, x0:x0 + w]
    region[:] = src * a + region * (1 - a)


def _cut(img, w, h, line, count):
    return [img[(i // line) * h:(i // line + 1) * h, (i % line) * w:(i % line + 1) * w] for i in range(count)]


def _rgba(c):
    return np.concatenate([c.astype(np.uint8), np.full(c.shape[:2] + (1,), 255, np.uint8)], 2)


def our_frames():
    import json
    meta = json.loads((SHEETS / "meta.json").read_text())
    base = review._decode(SHEETS / "base.png")[0]
    shadow = review._decode(SHEETS / "base-shadow.png")[0]
    st = meta["stroke"]
    stroke = _cut(review._decode(SHEETS / "stroke.png")[0], st["size"][0], st["size"][1],
                  st["line_length"], st["frames"])
    sh = lambda k: (meta[k]["shift"][0] * 64, meta[k]["shift"][1] * 64)  # noqa: E731
    frames = []
    for f in stroke:
        c = np.empty((H, W, 3), np.float32)
        c[:] = GROUND
        _paste(c, shadow, OX + sh("base-shadow")[0], OY + sh("base-shadow")[1], shadow=True)
        _paste(c, base, OX + sh("base")[0], OY + sh("base")[1])
        _paste(c, f, OX + sh("stroke")[0], OY + sh("stroke")[1])
        frames.append(_rgba(c))
    return frames


def vanilla_frames():
    main = _cut(review._decode(VC_G / "crusher-vertical.png")[0], 140, 194, 8, 48)
    shadow = review._decode(VC_G / "crusher-vertical-shadow.png")[0]
    # crusher-vertical(.lua) shift by_pixel(2, -15.5), shadow (38, -26), plus the
    # vertical set's by_pixel(0, 8); by_pixel is 32 px a tile, the sheet 64
    frames = []
    for f in main:
        c = np.empty((H, W, 3), np.float32)
        c[:] = GROUND
        _paste(c, shadow, OX + 38 * 2, OY + (-26 + 8) * 2, shadow=True)
        _paste(c, f, OX + 2 * 2, OY + (-15.5 + 8) * 2)
        frames.append(_rgba(c))
    return frames


def our_clip(frames=None):
    s = lambda n: str(SND / f"{n}.ogg")  # noqa: E731
    acc = [(dc.DROP_FRAME, s("drop"), dc.VOLUME["drop"]),
           (dc.TRIP_FRAME, s("trip"), dc.VOLUME["trip"])]
    acc += [(f, s("pawl"), dc.VOLUME["pawl"]) for f in dc.PAWL_FRAMES]
    return review.Clip(frames=frames, speed=dc.SPEED, bed=s("bed"), bed_volume=dc.VOLUME["bed"],
                       accents=acc)


def vanilla_clip(frames=None):
    return review.Clip(frames=frames, speed=V_SPEED, bed=dc.CRUSHER, bed_volume=0.8)


def decoded_audio(mp4):
    out = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(mp4),
                          "-f", "f32le", "-ac", "2", "-ar", str(sfx.SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).reshape(-1, 2)


def locate(track_hp, template_hp, due, window=0.05):
    """Where the template best matches the track within +-window s of `due`: offset ms, and r."""
    # an accent near the end of the clip is cut there: match only what is heard
    n = min(len(template_hp), len(track_hp) - sfx.samples(due) - sfx.samples(window))
    template_hp = template_hp[:n]
    best, best_off = -np.inf, None
    for off in range(-sfx.samples(window), sfx.samples(window) + 1):
        s = sfx.samples(due) + off
        if s < 0 or s + n > len(track_hp):
            continue
        seg = track_hp[s:s + n]
        r = float(np.dot(seg, template_hp) / (np.linalg.norm(seg) * np.linalg.norm(template_hp) + 1e-12))
        if r > best:
            best, best_off = r, off
    return best_off / sfx.SR * 1000.0, best


# Each accent's template length and the high-pass it is found through.
FIND = {"drop": (0.08, 150), "trip": (0.08, 1000), "pawl": (0.06, 1000)}


def accent_report(mp4, clip, n_frames, loops, label):
    track = decoded_audio(mp4).mean(1)
    worst, lines, cache = 0.0, [], {}
    for frame, snd, _vol in clip.accents:
        name = Path(snd).stem
        length, hp = FIND[name]
        if hp not in cache:
            cache[hp] = sfx.highpass(track, hp)[:, 0]
        tpl = sfx.highpass(review._sound(snd)[:sfx.samples(length)].mean(1), hp)[:, 0]
        offs = [locate(cache[hp], tpl, sfx.frame(k * n_frames + frame, clip.speed)) for k in range(loops)]
        mx = max(abs(o) for o, _ in offs)
        worst = max(worst, mx)
        lines.append(f"  {label} {name:5s} frame {frame:2d}: {loops} hits, offset from due "
                     f"{min(o for o, _ in offs):+.2f}..{max(o for o, _ in offs):+.2f} ms, "
                     f"match r {min(r for _, r in offs):.2f}..{max(r for _, r in offs):.2f}")
    return worst, lines


def mix_loudness(clip, n_frames, ticks):
    return loudness.measure(review.clip_audio(clip, n_frames, ticks), sfx.SR)


def main():
    ours, van = our_clip(our_frames()), vanilla_clip(vanilla_frames())
    n_ours, n_van = len(ours.frames), len(van.frames)
    out1, out2 = HERE / "review.mp4", HERE / "side-by-side.mp4"
    review.make(out1, ours, loops=LOOPS, bg=GROUND)
    review.make(out2, ours, vs=van, loops=LOOPS, bg=GROUND)

    t_ours = int(round(LOOPS * n_ours / ours.speed))
    v_cycles = max(1, int(round(t_ours / (n_van / van.speed))))
    t_van = int(round(v_cycles * n_van / van.speed))
    mo, mv = mix_loudness(ours, n_ours, t_ours), mix_loudness(van, n_van, t_van)
    print("mix as heard (every Sound at its volume):")
    print(f"  ours     {LOOPS} cycles {t_ours / 60:.2f} s: I {mo['integrated']:.1f} LUFS  "
          f"M max {mo['momentary_max']:.1f}  dBTP {mo['true_peak']:+.1f}")
    print(f"  vanilla  {v_cycles} cycles {t_van / 60:.2f} s: I {mv['integrated']:.1f} LUFS  "
          f"M max {mv['momentary_max']:.1f}  dBTP {mv['true_peak']:+.1f}")
    print(f"  difference: {mo['integrated'] - mv['integrated']:+.1f} LU integrated")

    print("accents, measured in the decoded MP4 audio:")
    w1, lines = accent_report(out1, ours, n_ours, LOOPS, "review.mp4")
    print("\n".join(lines))
    w2, lines = accent_report(out2, ours, n_ours, LOOPS, "side-by-side.mp4")
    print("\n".join(lines))
    for p in (out1, out2):
        print(f"{p}: {p.stat().st_size / 1e6:.2f} MB")
    print(f"worst accent offset: {max(w1, w2):.2f} ms")


if __name__ == "__main__":
    main()
