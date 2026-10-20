#!/usr/bin/env python3
"""Round 2, option C: heaviest -- drop 7 and pawls 8 semitones down, a strong iron body under each, round 1 C's trip.

  <venv>/bin/python concept/drop-crusher/sound/round-2/C/option_c.py

Writes bed.ogg (today's, copied), trip.ogg (round 1 C's, copied), pawl.ogg and
drop.ogg beside this file, through round-2/heavier.py: each pitched down by
`semitones`, an iron body laid under it (`body_hz`, `body_db` against the
strike's peak, dying over `body_s`, plus `shelf_db` at 250 Hz), then round 1
B's softening and today's level (momentary max).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import heavier  # noqa: E402

TRIP_FROM = "C"
PARAMS = {
    "drop": {"semitones": -7, "body_hz": 40.0, "body_db": -2.0, "body_s": 0.55, "shelf_db": 4.0},
    "pawl": {"semitones": -8, "body_hz": 115.0, "body_db": -2.0, "body_s": 0.18, "shelf_db": 4.0},
}

if __name__ == "__main__":
    heavier.build("C", PARAMS, TRIP_FROM, HERE)
