#!/usr/bin/env python3
"""Round 3, option A: round 2 C with the grit taken out.

  <venv>/bin/python concept/drop-crusher/sound/round-3/A/option_a.py

Writes drop.ogg (round 2 C's drop, rebuilt with tail "none": round-3/clean_tail.py),
pawl.ogg and trip.ogg (round 2 C's, copied) and bed.ogg (today's, copied).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import clean_tail  # noqa: E402

TAIL = "none"

if __name__ == "__main__":
    clean_tail.build("A", TAIL, HERE)
