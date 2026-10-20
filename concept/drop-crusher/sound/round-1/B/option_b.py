#!/usr/bin/env python3
"""Round 1, option B: medium -- low-pass at 5 kHz; transients 60 % of the way to the body, a 10 ms fade-in.

  <venv>/bin/python concept/drop-crusher/sound/round-1/B/option_b.py

Writes bed.ogg (the shipped bed, copied), pawl.ogg, trip.ogg and drop.ogg beside
this file: the generator's own accents (drop_crusher_sound.py, unchanged) through
round-1/soften.py with the amounts below. Every accent is level-matched to the
shipped file's momentary max, so the option changes character, not loudness.

  cutoff   low-pass, Butterworth order 4: what is left of the high end
  amount   the transient shaper: 0 leaves every crack as it is, 1 flattens it
           to the body (the slow envelope, SLOW_MS RMS)
  attack   the strike fades in from silence over ATTACK_MS, on a raised cosine
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import soften  # noqa: E402

ATTACK_MS, AMOUNT, SLOW_MS, CUTOFF_HZ, ORDER = 10, 0.6, 20, 5000, 4
PARAMS = {name: {"attack_ms": ATTACK_MS, "amount": AMOUNT, "slow_ms": SLOW_MS,
                 "cutoff_hz": CUTOFF_HZ, "order": ORDER}
          for name in soften.ACCENTS}

if __name__ == "__main__":
    soften.build("B", PARAMS, HERE)
