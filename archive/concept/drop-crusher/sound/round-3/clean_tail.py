#!/usr/bin/env python3
"""Round 3 of the crusher-sound task (T01c): round 2 C, with the crackle after the drop removed.

Liam (2026-10-20): "C sounds the best but after the drop there is an awful
crackling noise which is hard on the ears".

**Where the crackle comes from** (measured, the study in this round's report):
the drop's grit layer, drop_crusher_sound.grit() -- Poisson clicks of 1-3 ms
noise, 1.8-7.5 kHz, thinning over 0.7 s. Pitched 7 semitones down in round 2 C
it runs on for over a second, and level-matching lifted it with the rest.
Rebuilt without it, round 2 C's tail (after the first 150 ms) falls from
-35.5 to -45.6 dBFS above 2 kHz and from 57 clicks a second to 1. Without the
pebbles, the asteroid break, the mech armour hit or the soft clip, it hardly
moves. So the grit is what each take treats; nothing else changes.

This module rebuilds the generator's drop() layer for layer (checked: with the
grit as it is, the result equals drop_crusher_sound.drop() sample for sample),
with the grit replaced as a take says, then puts it through round 2 C exactly
(round-2/heavier.py: 7 semitones down, a 40 Hz iron body at -2 dB, +4 dB below
250 Hz; then round 1 B's softening; level-matched to today's drop on momentary
max). The pawl and the trip are round 2 C's files and the bed today's, copied
byte for byte.

Takes (`tail` in each option's script):
  "none"    the grit taken out; the pebbles, the break and the hit carry the rubble
  "settle"  the grit replaced by rubble settling: low noise (150-900 Hz) that
            dies away over 0.7 s, with no clicks in it
  "crunch"  the grit kept only as the weight lands: thinned to nothing by
            150 ms and low-passed at 1.5 kHz -- a crunch on the hit, no crackle after
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUND1, ROUND2 = HERE.parent / "round-1", HERE.parent / "round-2"
sys.path.insert(0, str(ROUND1))
sys.path.insert(0, str(ROUND2))

import numpy as np  # noqa: E402
import soften  # noqa: E402
import heavier  # noqa: E402
import sfx  # noqa: E402
import drop_crusher_sound as dc  # noqa: E402

ROUND2_C = {"semitones": -7, "body_hz": 40.0, "body_db": -2.0, "body_s": 0.55, "shelf_db": 4.0}
LENGTH = 1.6


def settle(length, seed=4, tail=0.7):
    """Rubble settling: band-limited noise, 150-900 Hz, dying away over `tail` s, no clicks."""
    n = sfx.noise(length, "pink", seed=seed)
    n = sfx.bandpass(n, 150, 900)
    t = np.arange(len(n)) / sfx.SR
    env = np.clip(1.0 - t / tail, 0.0, 1.0) ** 2
    env[:sfx.samples(0.01)] *= np.linspace(0, 1, sfx.samples(0.01))
    return sfx.normalize((n * env[:, None]).astype(np.float32), 0.0)


def tail_layer(tail):
    if tail == "grit":                                    # the generator's own
        return dc.grit(LENGTH, seed=4), -6
    if tail == "none":
        return None, None
    if tail == "settle":
        return settle(LENGTH), -10
    if tail == "crunch":
        return sfx.lowpass(dc.grit(LENGTH, seed=4, tail=0.15), 1500), -6
    raise ValueError(f"tail {tail!r}: grit, none, settle or crunch")


def drop(tail="grit"):
    """drop_crusher_sound.drop(), layer for layer, with its grit as `tail` says."""
    L = LENGTH
    brk = sfx.trim(sfx.load("__space-age__/sound/entity/asteroid/asteroid-damage-oxide-big-1.ogg"), 0, L)
    hit = sfx.load("__space-age__/sound/entity/mech-armor/mech-armor-land-rock-2.ogg")
    peb1 = sfx.load("__base__/sound/walking/pebble/stones-1.ogg")
    peb2 = sfx.load("__base__/sound/walking/pebble/stones-2.ogg")
    thump = sfx.envelope(sfx.tone(0.35, 75.0, to_hz=42.0),
                         [(0, 0), (0.002, 1), (0.06, 0.6), (0.25, 0.1), (0.35, 0)])
    m = sfx.Mix(L)
    m.add(brk, gain_db=-3)
    m.add(hit, gain_db=0)
    m.add(thump, gain_db=-8)
    m.add(peb1, ms=25, gain_db=-4)
    m.add(peb2, ms=110, gain_db=-9)
    layer, db = tail_layer(tail)
    if layer is not None:
        m.add(layer, gain_db=db)
    x = sfx.fade(m.render(), fade_out=0.3)
    x = sfx.highpass(x, 30, order=2)
    x = sfx.normalize(x, 0.0)
    x = np.tanh(1.6 * x) / np.tanh(1.6)
    return sfx.normalize(x, -1.0)


def build(option, tail, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    assert np.array_equal(drop("grit"), dc.drop()), "the rebuilt drop no longer equals the generator's"
    shutil.copyfile(soften.SHIPPED / "bed.ogg", out_dir / "bed.ogg")
    for name in ("pawl", "trip"):
        shutil.copyfile(ROUND2 / "C" / f"{name}.ogg", out_dir / f"{name}.ogg")
    target = soften.mmax(sfx.read(soften.SHIPPED / "drop.ogg")[0])
    y = soften.soften(heavier.heavier(drop(tail), **ROUND2_C), target_mmax=target, **heavier.ROUND1_B)
    sfx.write(out_dir / "drop.ogg", y)
    r = dc.check(out_dir / "drop.ogg")
    print(f"{option} drop  tail={tail}  {r['fmt']} {r['sr']} Hz {r['ch']} ch {r['secs']:.3f} s  "
          f"peak {20 * np.log10(r['peak']):+.2f} dBFS  M max {r['mmax']:.1f} (today {target:.1f})"
          + ("  OK" if r["ok"] else "  FAIL"))
    print(f"{option} pawl, trip copied from {ROUND2 / 'C'}; bed from {soften.SHIPPED}")


if __name__ == "__main__":
    print(__doc__)
