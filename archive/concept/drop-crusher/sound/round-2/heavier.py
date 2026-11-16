#!/usr/bin/env python3
"""Round 2 of the crusher-sound task (T01b): a heavier, lower body.

Liam (2026-10-20), after round 1: "Heavier, lower body" -- pitch the drop and
pawls down and add weight, so they read as heavy iron rather than clicks.

This module is the change; each option's script (A/option_a.py, ...) names its
amounts and calls build(). Built on round 1's softening:

  drop, pawl  the generator's own accent (drop_crusher_sound.py, unchanged),
              1. pitched down by `semitones` (tape-style: lower and longer,
                 sfx.pitch), so the whole strike sits lower;
              2. with an iron body laid under the strike: a decaying,
                 slightly sagging tone at `body_hz` with two inharmonic
                 partials (x2.76 at -8 dB, x5.40 at -16 dB, as a struck bar's
                 are), `body_db` against the pitched strike's peak, dying away
                 over `body_s`; and, if `shelf_db`, a low shelf at 250 Hz;
              3. then round 1's softening (round-1/soften.py) with round 1 B's
                 amounts -- 5 kHz low-pass, transients 60 % of the way to the
                 body, a 10 ms fade-in -- and level-matched to today's file on
                 momentary max, as round 1 was.
  trip        not changed again: round 1's B or C file, copied byte for byte
              (the option says which).
  bed         today's, copied byte for byte. Frames unchanged.
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUND1 = HERE.parent / "round-1"
sys.path.insert(0, str(ROUND1))

import numpy as np  # noqa: E402
import soften  # noqa: E402  (round 1's; it puts tools/audio and the generator on the path)
import sfx  # noqa: E402
import drop_crusher_sound as dc  # noqa: E402

SHIPPED = soften.SHIPPED
ROUND1_B = {"attack_ms": 10, "amount": 0.6, "slow_ms": 20, "cutoff_hz": 5000, "order": 4}
PARTIALS = ((1.0, 0.0), (2.76, -8.0), (5.40, -16.0))


def iron_body(hz, seconds, sag=0.92):
    """A struck-iron body: decaying partials, each sagging a little in pitch, 2 ms attack."""
    out = sfx.silence(seconds)
    for ratio, db in PARTIALS:
        tau = seconds / 4.0 / ratio ** 0.5            # higher partials die sooner
        t = sfx.tone(seconds, hz * ratio, to_hz=hz * ratio * sag)
        n = len(t)
        env = np.exp(-np.arange(n) / sfx.SR / tau)
        env[:sfx.samples(0.002)] *= np.linspace(0, 1, sfx.samples(0.002))
        out += sfx.gain(t * env[:, None].astype(np.float32), db)
    return out


def heavier(x, semitones, body_hz, body_db, body_s, shelf_db=0.0):
    y = sfx.pitch(x, semitones) if semitones else x
    y = sfx.normalize(y, 0.0)
    body = sfx.gain(sfx.normalize(iron_body(body_hz, body_s), 0.0), body_db)
    y = sfx.layer(y, body)
    if shelf_db:
        y = sfx.low_shelf(y, 250, shelf_db)
    return sfx.highpass(y, 30, order=2)


def build(option, params, trip_from, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SHIPPED / "bed.ogg", out_dir / "bed.ogg")
    shutil.copyfile(ROUND1 / trip_from / "trip.ogg", out_dir / "trip.ogg")
    for name, x in (("pawl", dc.pawl()), ("drop", dc.drop())):
        target = soften.mmax(sfx.read(SHIPPED / f"{name}.ogg")[0])
        y = soften.soften(heavier(x, **params[name]), target_mmax=target, **ROUND1_B)
        sfx.write(out_dir / f"{name}.ogg", y)
        r = dc.check(out_dir / f"{name}.ogg")
        print(f"{option} {name:5s} {r['fmt']} {r['sr']} Hz {r['ch']} ch {r['secs']:.3f} s  "
              f"peak {20 * np.log10(r['peak']):+.2f} dBFS  M max {r['mmax']:.1f} (today {target:.1f})"
              + ("  OK" if r["ok"] else "  FAIL"))
    print(f"{option} trip  copied from {ROUND1 / trip_from / 'trip.ogg'}")
    r = dc.check(out_dir / "bed.ogg", loop=True)
    print(f"{option} bed   copied from {SHIPPED / 'bed.ogg'}" + ("  OK" if r["ok"] else "  FAIL"))


if __name__ == "__main__":
    print(__doc__)
