#!/usr/bin/env python3
"""Round 2, option A: a little heavier -- drop 2 and pawls 3 semitones down, a light iron body under each.

  <venv>/bin/python concept/drop-crusher/sound/round-2/A/option_a.py

Writes bed.ogg (today's, copied), trip.ogg (round 1 B's, copied), pawl.ogg and
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

TRIP_FROM = "B"
PARAMS = {
    "drop": {"semitones": -2, "body_hz": 55.0, "body_db": -9.0, "body_s": 0.35, "shelf_db": 0.0},
    "pawl": {"semitones": -3, "body_hz": 190.0, "body_db": -9.0, "body_s": 0.10, "shelf_db": 0.0},
}

if __name__ == "__main__":
    heavier.build("A", PARAMS, TRIP_FROM, HERE)
