#!/usr/bin/env python3
"""Round 1 of the crusher-sound task (T01): the accents, softer and less harsh.

Liam (2026-10-20): "it's quite sharp and hard on the ears at the moment -
especially when there is multiple". Round 1 changes two things, by a different
amount in each option: a softer attack, and less high end.

This module is the change itself; each option's script (A/option_a.py, ...)
names its amounts and calls build(). It takes the generator's own accents --
drop_crusher_sound.pawl(), trip() and drop(), unchanged -- and puts each through
soften():

  1. a low-pass (Butterworth, `order`, at `cutoff_hz`): the high end rolled off;
  2. a softer attack, in two parts. The strike in these files is not always at
     the file's first sample -- the drop's hit peaks 16 ms in, the pawl's click
     6 ms -- so a fade at the start alone would miss it:
     a. a transient shaper over the whole file: wherever the fast envelope
        (1 ms RMS) stands over the slow one (`slow_ms` RMS, centred), the gain
        is (slow / fast) ** `amount`, smoothed over 1 ms -- every crack, click
        and grit tick comes down towards the body under it, by more as
        `amount` goes from 0 (none) to 1 (flat to the body);
     b. a fade-in from the accent's own onset (its first sample at 10 % of its
        peak) over `attack_ms`, on a raised cosine from silence: the very
        first ms swell in instead of standing out;
  3. the level put back: the result's momentary-max loudness (BS.1770, 400 ms,
     loudness.py) set to the shipped file's, so an option is a change of
     character heard at the same loudness, not just a quieter file; a sample
     peak over -1 dBFS is then pulled down by the soft clip the drop already
     uses (tanh), and the level matched again.

The bed is not touched: each option's bed.ogg is the shipped one, copied byte
for byte. The frames are not touched either (they are the prototype's).

  python soften.py            (nothing: run an option's script)
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "tools" / "audio"))
sys.path.insert(0, str(HERE.parent))

import numpy as np  # noqa: E402
import sfx  # noqa: E402
import loudness  # noqa: E402
import drop_crusher_sound as dc  # noqa: E402

SHIPPED = REPO / "sound" / "drop-crusher"
ACCENTS = ("pawl", "trip", "drop")
PEAK_CEILING_DB = -1.0


def onset(x, frac=0.1):
    m = np.abs(x).max(axis=1)
    return int(np.argmax(m >= frac * m.max()))


def attack_envelope(n, start, attack_ms):
    """Gain per sample: 0 before `start`, a raised cosine up to 1 over attack_ms."""
    g = np.ones(n, np.float64)
    k = sfx.samples(attack_ms / 1000.0)
    g[:start] = 0.0
    ramp = 0.5 * (1.0 - np.cos(np.pi * np.arange(k) / k))
    end = min(n, start + k)
    g[start:end] = ramp[:end - start]
    return g[:, None]


def rms_env(m, win_ms):
    w = max(1, sfx.samples(win_ms / 1000.0))
    return np.sqrt(np.convolve(m ** 2, np.ones(w) / w, mode="same"))


def transient_gain(x, amount, slow_ms):
    """Gain per sample that brings the fast envelope down towards the slow one."""
    m = x.astype(np.float64).mean(axis=1)
    fast, slow = rms_env(m, 1.0), rms_env(m, slow_ms)
    g = np.minimum(1.0, (slow + 1e-9) / (fast + 1e-9)) ** amount
    w = sfx.samples(0.001)
    g = np.convolve(g, np.ones(w) / w, mode="same")
    return g[:, None]


def mmax(x):
    return loudness.measure(x, sfx.SR)["momentary_max"]


def match_mmax(x, target):
    return sfx.gain(x, target - mmax(x))


def soften(x, attack_ms, amount, slow_ms, cutoff_hz, order, target_mmax):
    y = sfx.lowpass(x, cutoff_hz, order=order)
    y = y * transient_gain(y, amount, slow_ms)
    y = (y * attack_envelope(len(y), onset(x), attack_ms)).astype(np.float32)
    y = match_mmax(y, target_mmax)
    ceiling = 10 ** (PEAK_CEILING_DB / 20.0)
    for _ in range(4):
        if np.abs(y).max() <= ceiling:
            break
        p = np.abs(y).max()
        y = (np.tanh(1.6 * y / p) / np.tanh(1.6) * p).astype(np.float32)   # the drop's own soft clip
        y = match_mmax(y, target_mmax)
    if np.abs(y).max() > ceiling:                                          # last resort: plain gain
        y = sfx.normalize(y, PEAK_CEILING_DB)
    return y


def build(option, params, out_dir):
    """Write the option's bed (shipped copy) and softened accents into out_dir."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SHIPPED / "bed.ogg", out_dir / "bed.ogg")
    made = {"pawl": dc.pawl(), "trip": dc.trip(), "drop": dc.drop()}
    for name, x in made.items():
        target = mmax(sfx.read(SHIPPED / f"{name}.ogg")[0])
        y = soften(x, target_mmax=target, **params[name])
        sfx.write(out_dir / f"{name}.ogg", y)
        r = dc.check(out_dir / f"{name}.ogg")
        print(f"{option} {name:5s} {r['fmt']} {r['sr']} Hz {r['ch']} ch {r['secs']:.3f} s  "
              f"peak {20 * np.log10(r['peak']):+.2f} dBFS  M max {r['mmax']:.1f} (shipped {target:.1f})"
              + ("  OK" if r["ok"] else "  FAIL"))
    r = dc.check(out_dir / "bed.ogg", loop=True)
    print(f"{option} bed   copied from {SHIPPED / 'bed.ogg'}" + ("  OK" if r["ok"] else "  FAIL"))


if __name__ == "__main__":
    print(__doc__)
