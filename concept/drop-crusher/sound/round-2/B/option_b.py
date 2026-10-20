#!/usr/bin/env python3
"""Round 2, option B: heavier -- drop 4 and pawls 5 semitones down, an iron body under each.

  <venv>/bin/python concept/drop-crusher/sound/round-2/B/option_b.py

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
    "drop": {"semitones": -4, "body_hz": 47.0, "body_db": -5.0, "body_s": 0.45, "shelf_db": 2.0},
    "pawl": {"semitones": -5, "body_hz": 150.0, "body_db": -5.0, "body_s": 0.14, "shelf_db": 2.0},
}

if __name__ == "__main__":
    heavier.build("B", PARAMS, TRIP_FROM, HERE)
