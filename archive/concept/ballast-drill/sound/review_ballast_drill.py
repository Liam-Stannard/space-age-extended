#!/usr/bin/env python3
"""The Ballast Drill's sound against its stroke, and beside vanilla's big mining drill.

  tools/audio/.venv/bin/python concept/ballast-drill/sound/review_ballast_drill.py

Run ballast_drill_sound.py first. Writes, beside this file:

  review.mp4        the stroke (model/motion-1x.gif) at the game's 0.4 frames a
                    tick, eight one-second loops, the bed under it at its proposed
                    volume and the landing (frame 5) and ratchet (frame 23) on
                    their frames
  side-by-side.mp4  the same eight loops, then vanilla's big mining drill for one
                    whole 360-tick drilling cycle, each heard in turn

and prints: the loudness of each mix as the game would play it (every Sound at
its `volume`), ours beside vanilla's; and where each accent actually sits in the
MP4's decoded audio, found by cross-correlating the accent against the track
near the time its frame is due -- the measured form of review.py's own timing.

**Vanilla's drill, as drawn here**, north-facing, from its own sheets and its own
frame sequences (space-age/prototypes/entity/big-mining-drill.lua): the still,
the drill head (drill_sequence, 180 frames, at its north_position), the still
again over it, the support, the front frame, the nozzle and the top, shadows
under all. The head's `animated_shift` waypoints, the dust and the output
particles are left out: it is a reference for timing, not a portrait. Its sound
is its prototype's: the working loop at 0.3 throughout; the drilling loop at 0.7
from frame 12 to frame 156 of the drill animation, with its 10-tick fades; and
the start clank at 0.75 on frame 8.
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
import ballast_drill_sound as bd  # noqa: E402

SND = REPO / "sound" / "ballast-drill"
GROUND = (74, 66, 58)          # the motion GIF's own ground, so both panels share it
LOOPS = 8

BMD_G = sfx.data_dir() / "space-age" / "graphics" / "entity" / "big-mining-drill"
BMD_S = "__space-age__/sound/entity/big-mining-drill/"
V_SPEED = 0.5                  # big-mining-drill.lua: animation_speed 0.5, animation_progress 1

DRILL_SEQ = ([f for f in range(1, 13) for _ in (0, 1)] + list(range(13, 25)) * 11
             + [f for f in range(25, 37) for _ in (0, 1)])
SUPPORT_SEQ = ([1] * 16 + [2, 2, 3, 3, 4, 4, 6, 6] + [1, 2, 3, 4, 5, 6] * 22
               + [1, 2, 3, 4, 5, 6] + [1] * 18)
TOP_SEQ = ([18, 17, 16, 15, 14, 13, 13, 12, 11, 10, 9, 9, 9, 10, 11, 10, 10, 9, 9, 8, 8, 7, 7, 6]
           + [1, 2, 3, 4, 5, 6] * 22 + [6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11,
                                        12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17])
NOZZLE_SEQ = TOP_SEQ + [19 if i % 2 == 0 else 18 for i in range(1, 51)]


def _sheet(name, w, h, line, count):
    """Frames of a vanilla sheet, RGBA."""
    path = (BMD_G / name) if not str(name).startswith("/") else Path(name)
    img = review._decode(path)[0]
    return [img[(i // line) * h:(i // line + 1) * h, (i % line) * w:(i % line + 1) * w]
            for i in range(count)]


def _paste(canvas, rgba, cx, cy, shadow=False):
    """Alpha-composite `rgba` centred at (cx, cy) on a float RGB canvas."""
    h, w = rgba.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    a = rgba[..., 3:4].astype(np.float32) / 255.0
    src = np.zeros_like(rgba[..., :3], dtype=np.float32) if shadow else rgba[..., :3].astype(np.float32)
    region = canvas[y0:y0 + h, x0:x0 + w]
    region[:] = src * a + region * (1 - a)


def vanilla_frames():
    """Vanilla's big mining drill, north, one composite per frame of its 180-frame cycle."""
    px = 2.0  # util.by_pixel is 32 px a tile; these sheets are 64 (scale 0.5)
    L = {  # name: (file, w, h, line, count, shift_x, shift_y) from the sheets' .lua
        "still": ("North/big-mining-drill-N-still.png", 324, 324, 1, 1, 0.0, -12.0),
        "still_sh": ("North/big-mining-drill-N-still-shadow.png", 382, 318, 1, 1, 14.5, -3.5),
        "front": ("North/big-mining-drill-N-still-front.png", 338, 164, 1, 1, -1.0, -38.0),
        "drill": ("big-mining-drill-drill.png", 168, 226, 6, 36, 0.0, -23.5),
        "drill_sh": ("big-mining-drill-drill-shadow.png", 272, 120, 6, 36, 22.0, 3.0),
        "support": ("North/big-mining-drill-N-support.png", 290, 190, 3, 6, 0.5, -21.0),
        "support_sh": ("North/big-mining-drill-N-support-shadow.png", 380, 138, 1, 1, 22.0, -5.5),
        "nozzle": ("North/big-mining-drill-N-top-nozzle.png", 40, 142, 6, 19, -18.0, -73.5),
        "top": ("North/big-mining-drill-N-top.png", 150, 176, 6, 18, 1.0, -61.5),
        "top_sh": ("North/big-mining-drill-N-top-shadow.png", 216, 138, 6, 18, 72.0, 1.5),
    }
    sheets = {k: _sheet(f, w, h, line, n) for k, (f, w, h, line, n, _, _) in L.items()}
    W, H = 448, 400              # holds every layer: x -162..252, y -218..152 about the origin
    ox, oy = 178, 232
    drill_pos = 0.15 * 64                    # north_position {0, 0.15}

    def put(c, key, idx, dy=0.0, shadow=False):
        sx, sy = L[key][5] * px, L[key][6] * px
        _paste(c, sheets[key][idx], ox + sx, oy + sy + dy, shadow)

    frames = []
    for i in range(len(DRILL_SEQ)):
        c = np.empty((H, W, 3), np.float32)
        c[:] = GROUND
        t = TOP_SEQ[i % len(TOP_SEQ)] - 1
        s = SUPPORT_SEQ[i % len(SUPPORT_SEQ)] - 1
        d = DRILL_SEQ[i] - 1
        # shadows first, as the engine draws them under everything
        sh = np.zeros((H, W, 3), np.float32)
        sh[:] = GROUND
        for key, idx, dy in (("still_sh", 0, 0), ("drill_sh", d, drill_pos), ("support_sh", 0, 0),
                             ("top_sh", t, 0)):
            put(sh, key, idx, dy, shadow=True)
        c = np.minimum(c, sh)                # shadows darken, never stack past their own
        put(c, "still", 0)
        put(c, "drill", d, drill_pos)
        put(c, "still", 0)
        put(c, "support", s)
        put(c, "front", 0)
        put(c, "nozzle", NOZZLE_SEQ[i] - 1)
        put(c, "top", t)
        frames.append(np.concatenate([c.astype(np.uint8), np.full((H, W, 1), 255, np.uint8)], 2))
    return frames


def vanilla_clip():
    drilling = sfx.load(BMD_S + "big-mining-drill-loop.ogg")
    run = sfx.frame(156 - 12, V_SPEED)
    drilling = np.tile(drilling, (int(np.ceil(run / sfx.seconds(drilling))) + 1, 1))
    drilling = sfx.fade(sfx.trim(drilling, 0, run), 10 / 60, 10 / 60, curve="linear")
    return review.Clip(frames=vanilla_frames(), speed=V_SPEED,
                       bed=BMD_S + "big-mining-drill-working-loop.ogg", bed_volume=0.3,
                       accents=[(8, BMD_S + "big-mining-drill-start.ogg", 0.75),
                                (12, drilling, 0.7)])


def our_clip():
    return review.Clip(frames=str(HERE.parent / "model" / "motion-1x.gif"), speed=bd.SPEED,
                       bed=str(SND / "bed.ogg"), bed_volume=bd.VOLUME["bed"],
                       accents=[(bd.LANDING_FRAME, str(SND / "landing.ogg"), bd.VOLUME["landing"]),
                                (bd.RATCHET_FRAME, str(SND / "ratchet.ogg"), bd.VOLUME["ratchet"])])


def decoded_audio(mp4):
    out = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(mp4),
                          "-f", "f32le", "-ac", "2", "-ar", str(sfx.SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).reshape(-1, 2)


def locate(track, template, due, window=0.05, hp=None):
    """Where `template` best matches `track` within +-window s of `due`: the offset, in ms."""
    tr, tp = track.mean(1), template.mean(1)
    if hp:
        tr, tp = sfx.highpass(tr, hp)[:, 0], sfx.highpass(tp, hp)[:, 0]
    # an accent near the end of the clip is cut there: match only what is heard
    n = min(len(tp), len(tr) - sfx.samples(due) - sfx.samples(window))
    tp = tp[:n]
    best, best_off = -np.inf, None
    for off in range(-sfx.samples(window), sfx.samples(window) + 1):
        s = sfx.samples(due) + off
        if s < 0 or s + n > len(tr):
            continue
        seg = tr[s:s + n]
        r = float(np.dot(seg, tp) / (np.linalg.norm(seg) * np.linalg.norm(tp) + 1e-12))
        if r > best:
            best, best_off = r, off
    return best_off / sfx.SR * 1000.0, best


# Each accent's template, and the high-pass it is found through: the bright ones
# above everything the bed and the landing put there.
FIND = {bd.LANDING_FRAME: (0.08, 150), bd.RATCHET_FRAME: (0.16, 1000)}


def accent_report(mp4, clip, n_frames, loops, label):
    track = decoded_audio(mp4)
    worst = 0.0
    lines = []
    for frame, snd, _vol in clip.accents:
        snd = snd[0] if isinstance(snd, (list, tuple)) else snd
        length, hp = FIND[frame]
        tpl = review._sound(snd)[:sfx.samples(length)]
        offs = []
        for k in range(loops):
            due = sfx.frame(k * n_frames + frame, clip.speed)
            off, r = locate(track, tpl, due, hp=hp)
            offs.append((off, r))
        mx = max(abs(o) for o, _ in offs)
        worst = max(worst, mx)
        lines.append(f"  {label} frame {frame:2d}: {loops} hits, offset from due "
                     f"{min(o for o, _ in offs):+.2f}..{max(o for o, _ in offs):+.2f} ms, "
                     f"match r {min(r for _, r in offs):.2f}..{max(r for _, r in offs):.2f}")
    return worst, lines


def mix_loudness(clip, n_frames, ticks):
    a = review.clip_audio(clip, n_frames, ticks)
    m = loudness.measure(a, sfx.SR)
    return m


def main():
    ours, van = our_clip(), vanilla_clip()
    n_ours = len(review.load_frames(ours))
    n_van = len(van.frames)

    out1 = HERE / "review.mp4"
    out2 = HERE / "side-by-side.mp4"
    review.make(out1, ours, loops=LOOPS, bg=GROUND)
    review.make(out2, ours, vs=van, loops=LOOPS, bg=GROUND)

    t_ours = int(round(LOOPS * n_ours / ours.speed))
    t_van = int(round(n_van / van.speed))
    mo, mv = mix_loudness(ours, n_ours, t_ours), mix_loudness(van, n_van, t_van)
    print("mix as heard (every Sound at its volume):")
    print(f"  ours     {LOOPS} cycles {t_ours / 60:.2f} s: I {mo['integrated']:.1f} LUFS  "
          f"M max {mo['momentary_max']:.1f}  dBTP {mo['true_peak']:+.1f}")
    print(f"  vanilla  1 cycle  {t_van / 60:.2f} s: I {mv['integrated']:.1f} LUFS  "
          f"M max {mv['momentary_max']:.1f}  dBTP {mv['true_peak']:+.1f}")
    print(f"  difference: {mo['integrated'] - mv['integrated']:+.1f} LU integrated")

    print("accents, measured in the decoded MP4 audio:")
    w, lines = accent_report(out1, ours, n_ours, LOOPS, "review.mp4")
    print("\n".join(lines))
    w2, lines = accent_report(out2, ours, n_ours, LOOPS, "side-by-side.mp4")
    print("\n".join(lines))
    for p in (out1, out2):
        print(f"{p}: {p.stat().st_size / 1e6:.2f} MB")
    print(f"worst accent offset: {max(w, w2):.2f} ms")


if __name__ == "__main__":
    main()
