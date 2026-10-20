#!/usr/bin/env python3
"""Round 3, option C: round 2 C with the grit kept only as a dull crunch on the hit, gone by 150 ms.

  <venv>/bin/python concept/drop-crusher/sound/round-3/C/option_c.py

Writes drop.ogg (round 2 C's drop, rebuilt with tail "crunch": round-3/clean_tail.py),
pawl.ogg and trip.ogg (round 2 C's, copied) and bed.ogg (today's, copied).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import clean_tail  # noqa: E402

TAIL = "crunch"

if __name__ == "__main__":
    clean_tail.build("C", TAIL, HERE)
