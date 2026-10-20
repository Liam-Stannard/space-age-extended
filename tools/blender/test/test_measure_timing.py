#!/usr/bin/env python3
"""measure.py's motion, strobe, steps and glow flicker played as the engine plays them: each
layer's frame_sequence at its animation_speed, over the true loop (task factorio-tools-skills,
T05b), held to values worked by hand.

  python3 tools/blender/test/test_measure_timing.py --out <dir>

Nothing is rendered: small sheets are drawn here and written under --out (kept), and measure.py
is run on them. Exits 0 when every case below comes out as listed, 1 naming those that do not.

  speed      exact_speed: 0.11666666666666667 is 7/60, 0.5 is 1/2, 1/3 written as a float is 1/3.
  play       the Reaction Plant's press, 140 entries at 7/60: its own loop 1200 ticks; its 24-frame
             layers at 14/60: 720; the two together 3600 ticks. Entries [0, 1, 2] at speed 2 (an
             entry skipped every tick): frames 0, 2, 1 over a 3-tick loop. A sequence of one frame
             never changes. A hold across the loop's end: the first drawn frame begins before tick
             0 (a negative tick).
  cap        two layers whose true loop has more drawn frames than the cap: the first cap of them
             from tick 0, complete false, no durations.
  fixture    (the ticket's criterion 1) one direction, footprint 1x1, every sheet 64 x 64 at shift
             0, the plate grey 60 over all of it (4096 covered px):
               press       paint, 4 frames, a 6 x 6 block grey 40, 200, 40, 200; hold {frame 1,
                           entries 108, each 2} written out (116 entries); animation_speed 0.5
               press-glow  glow, 4 frames, a 10 x 10 block of light grey 80, 40, 120, 160; its
                           plate layer's sequence and speed, as pack.py writes them
               beacon      paint, 2 frames, a 4 x 4 block grey 40, 200; animation_speed 1/3
             Worked by hand before it was run (the true loop 696 ticks, 240 drawn frames):
               step_px     239 values: 152 into the frames starting at ticks 12, 240, 468, 480
                           (all three change), 136 at 4, 8, 16, 236, 244, 248, 472, 476 (press
                           and its glow), 16 at every other multiple of 3 from 3 to 693 (the
                           beacon); wrap_px 16; wrap_within_steps true
               moving      152 px, 3.71 %
               strobe      152 px, 3.71 % (beacon 232 reversals, press 12, glow 6 a loop)
               own loop    strobe_own_loop 36 px, 0.88 %: per pixel's own loop the beacon reverses
                           2 times (6 ticks, 116 repeats), the press 4 (232 ticks, 3 repeats),
                           the glow 2
               per layer   press 0.88, beacon 0.39, press-glow 2.44
               flicker     press-glow: flicker_step_pct 98.3, range_pct 147.5 (its light's mean
                           over time, 1888000 / 232; frame 1 held 220 of its 232 ticks)
               timing      loop_ticks 696, loop_seconds 11.6, complete, frame_ticks from
                           [0, 3, 4, 6, 8, 9, 12, 15, 16, ...], each layer's entries, speed and loop
               alone       press played [0, 1, 2, 3], step_px [36, 36, 36], wrap 36, most changed
                           36 between [2, 3]; press-glow the same with 100; beacon played [0, 1],
                           step_px [16], wrap 16
  untimed    the same sheets with no frame_sequence and no animation_speed: sprite order at one
             rate, as before T05b: 4 drawn frames, step_px [152, 152, 152], wrap 152, strobe_px 52
             (1.27 %: the glow's 2 reversals a loop do not count), flicker_step_pct 80.0,
             range_pct 120.0, and no timing in the output.
"""
import argparse
import json
import os
import sys
from fractions import Fraction

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import measure  # noqa: E402

FAILED = []
HOLD = [1, 1, 2, 2, 3, 3, 4, 4] + [1] * 108          # hold {frame 1, entries 108, each 2}, 4 frames


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def test_speed():
    for v, want in ((7 / 60, Fraction(7, 60)), (0.5, Fraction(1, 2)), (1 / 3, Fraction(1, 3)), (1, Fraction(1))):
        got = measure.exact_speed(v)
        check(f"speed: {v!r} is {want}", got == want, f"got {got}")


def test_play():
    press = measure.Play([k - 1 for k in [k for k in range(1, 17) for _ in range(2)] + [1] * 108],
                         measure.exact_speed(7 / 60))
    other = measure.Play(range(24), measure.exact_speed(14 / 60))
    check("play: press, 140 entries at 7/60, loops in 1200 ticks", (press.n, press.loop) == (140, 1200),
          f"got {press.n}, {press.loop}")
    check("play: 24 frames at 14/60 loop in 720 ticks", other.loop == 720, f"got {other.loop}")
    both = measure.Timeline([press, other], cap=10 ** 6)
    check("play: the plant's true loop 3600 ticks", both.ticks == 3600 and both.complete, f"got {both.ticks}")
    fast = measure.Timeline([measure.Play([0, 1, 2], Fraction(2))])
    check("play: speed 2 skips an entry a tick: frames 0, 2, 1 over 3 ticks",
          ([s[0] for s in fast.states], fast.ticks, fast.frames) == ([0, 2, 1], 3, [0, 1, 2]),
          f"got {[s[0] for s in fast.states]}, {fast.ticks}, {fast.frames}")
    flat = measure.Timeline([measure.Play([0, 0, 0], Fraction(1, 2))])
    check("play: one frame throughout never changes", (flat.frames, flat.states) == ([0], [(0,)]),
          f"got {flat.frames}, {flat.states}")
    held = measure.Timeline([measure.Play([k - 1 for k in HOLD], Fraction(1, 2))])
    check("play: a hold across the loop's end begins before tick 0",
          (held.frames, [s[0] for s in held.states], held.durations) == ([-216, 4, 8, 12], [0, 1, 2, 3],
                                                                         [220, 4, 4, 4]),
          f"got {held.frames}, {held.states}, {held.durations}")


def test_cap():
    tl = measure.Timeline([measure.Play(range(7), Fraction(1)), measure.Play(range(11), Fraction(1))], cap=20)
    check("cap: 77 frames over a cap of 20: the first 20 from tick 0, incomplete",
          (tl.ticks, tl.frames, tl.complete, tl.durations) == (77, list(range(20)), False, None),
          f"got {tl.ticks}, {tl.frames}, {tl.complete}")


def frames_sheet(path, values, at, size, light=False):
    """A sheet of 64 x 64 frames, each a size x size block at `at` of grey values[f]."""
    sheet = Image.new("RGBA", (64 * len(values), 64))
    for f, v in enumerate(values):
        sheet.paste((v, v, v, 255), (64 * f + at[0], at[1], 64 * f + at[0] + size, at[1] + size))
    sheet.save(path)
    return dict(size=[64, 64], shift=[0.0, 0.0], frames=len(values), line_length=len(values),
                **({"kind": "glow"} if light else {}))


def write_fixture(d, timed):
    os.makedirs(d, exist_ok=True)
    Image.new("RGBA", (64, 64), (60, 60, 60, 255)).save(os.path.join(d, "base.png"))
    meta = {"base": dict(size=[64, 64], shift=[0.0, 0.0])}
    meta["press"] = frames_sheet(os.path.join(d, "press.png"), [40, 200, 40, 200], (4, 4), 6)
    meta["press-glow"] = frames_sheet(os.path.join(d, "press-glow.png"), [80, 40, 120, 160], (20, 20), 10, True)
    meta["beacon"] = frames_sheet(os.path.join(d, "beacon.png"), [40, 200], (40, 40), 4)
    if timed:
        for k in ("press", "press-glow"):
            meta[k].update(frame_sequence=HOLD, animation_speed=0.5)
        meta["beacon"]["animation_speed"] = 1 / 3
    meta["checks"] = {}
    with open(os.path.join(d, "meta.json"), "w") as f:
        json.dump(meta, f)


def run_fixture(out, timed):
    sd = os.path.join(out, "timed" if timed else "untimed")
    write_fixture(os.path.join(sd, "sheets"), timed)
    code = measure.run([os.path.join(sd, "sheets"), "--out", os.path.join(sd, "measures"), "--footprint", "1x1"])
    check(f"{'fixture' if timed else 'untimed'}: exit 0", code == 0, f"exit {code}")
    with open(os.path.join(sd, "measures", "measures.json")) as f:
        return json.load(f)["directions"][""]


def test_fixture(out):
    r = run_fixture(out, True)
    mo = r["motion"]
    both, press = {12, 240, 468, 480}, {4, 8, 16, 236, 244, 248, 472, 476}
    ticks = sorted(set(range(0, 696, 3)) | both | press)
    want_steps = [152 if t in both else 136 if t in press else 16 for t in ticks[1:]]
    check("fixture: 240 drawn frames", mo["loop_frames"] == 240, f"got {mo['loop_frames']}")
    check("fixture: step_px as worked", mo["step_px"] == want_steps,
          f"got {len(mo['step_px'])} values, first {mo['step_px'][:12]}")
    check("fixture: the step counts: 152 x 4, 136 x 8, 16 x 227",
          [mo["step_px"].count(v) for v in (152, 136, 16)] == [4, 8, 227])
    check("fixture: wrap_px 16, within the steps", (mo["wrap_px"], mo["wrap_within_steps"]) == (16, True),
          f"got {mo['wrap_px']}, {mo['wrap_within_steps']}")
    check("fixture: moving 3.71 %", mo["moving_pct"] == 3.71, f"got {mo['moving_pct']}")
    check("fixture: strobe 152 px, 3.71 %", (mo["strobe_px"], mo["strobe_pct"]) == (152, 3.71),
          f"got {mo['strobe_px']}, {mo['strobe_pct']}")
    check("fixture: strobe_own_loop 36 px, 0.88 %", (mo.get("strobe_own_loop_px"), mo.get("strobe_own_loop_pct"))
          == (36, 0.88), f"got {mo.get('strobe_own_loop_px')}, {mo.get('strobe_own_loop_pct')}")
    check("fixture: per layer moving", mo["per_layer_moving_pct"] == {"press": 0.88, "beacon": 0.39,
                                                                       "press-glow": 2.44},
          f"got {mo['per_layer_moving_pct']}")
    g = r["glow"]["press-glow"]
    check("fixture: glow flicker 98.3, range 147.5",
          (g["flicker_step_pct"], g["range_pct"], g["frames"], g["played_frames"], g["loop_ticks"])
          == (98.3, 147.5, 4, 4, 232), f"got {g}")
    tm = mo.get("timing", {})
    check("fixture: timing", (tm.get("loop_ticks"), tm.get("loop_seconds"), tm.get("complete"))
          == (696, 11.6, True) and tm.get("frame_ticks") == ticks, f"got {dict(tm, frame_ticks=None)}")
    check("fixture: timing layers", tm.get("layers") == {
        "press": dict(entries=116, frame_sequence=True, animation_speed=0.5, as_fraction="1/2", loop_ticks=232),
        "beacon": dict(entries=2, frame_sequence=False, animation_speed=1 / 3, as_fraction="1/3", loop_ticks=6),
        "press-glow": dict(entries=116, frame_sequence=True, animation_speed=0.5, as_fraction="1/2",
                           loop_ticks=232)}, f"got {tm.get('layers')}")
    la = r["layers_alone"]
    for stem, px in (("press", 36), ("press-glow", 100)):
        a = la[stem]
        check(f"fixture: {stem} alone, played", (a["played"], a["step_px"], a["wrap_px"], a["most_changed_px"],
                                                  a["between_frames"]) == ([0, 1, 2, 3], [px] * 3, px, px, [2, 3]),
              f"got {a}")
    a = la["beacon"]
    check("fixture: beacon alone, played", (a["played"], a["step_px"], a["wrap_px"]) == ([0, 1], [16], 16),
          f"got {a}")


def test_untimed(out):
    r = run_fixture(out, False)
    mo, g = r["motion"], r["glow"]["press-glow"]
    check("untimed: sprite order at one rate", (mo["loop_frames"], mo["step_px"], mo["wrap_px"]) == (4, [152] * 3, 152),
          f"got {mo['loop_frames']}, {mo['step_px']}, {mo['wrap_px']}")
    check("untimed: strobe 52 px, 1.27 %", (mo["strobe_px"], mo["strobe_pct"]) == (52, 1.27),
          f"got {mo['strobe_px']}, {mo['strobe_pct']}")
    check("untimed: glow flicker 80.0, range 120.0", (g["flicker_step_pct"], g["range_pct"]) == (80.0, 120.0),
          f"got {g}")
    check("untimed: no timing, no played order", "timing" not in mo and "played_frames" not in g
          and "strobe_own_loop_px" not in mo
          and all("played" not in a for a in r["layers_alone"].values()))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    test_speed()
    test_play()
    test_cap()
    test_fixture(a.out)
    test_untimed(a.out)
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
