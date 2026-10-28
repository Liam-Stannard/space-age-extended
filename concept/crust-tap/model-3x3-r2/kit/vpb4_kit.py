"""Copied into the Gas Pump's T15 model round (gas-pump-3x3 T15, 2026-10-28) from concept/crust-tap/model-3x3/kit/vpb4_kit.py (6ff4325); changed here: nothing. Its own first line follows.
Copied into the 3x3 Gas Pump's shipping model (gas-pump-3x3 T08, 2026-10-21) from concept/crust-tap/options/round-3x3-refine/kit/vpb4_kit.py (ba32d3d); changed here: nothing. Its own first line follows.
Copied into the Gas Pump 3x3 options round (gas-pump-3x3 T02, 2026-10-21) from the vent-pump-model worktree's concept/vent-pump/model/kit/vpb4_kit.py (a184f70); changed here: nothing. Its own first line follows.
Copied into the shipping model (T07, 2026-10-20) from options/round-4/vpb4_kit.py; changed here: the import path (round 3's kit is beside it).

Vent Pump, round 4 (T03), artist B's half (concepts 8, 9, 10, 19): round 3's kit
(../round-3/vpb3_kit.py), used unchanged, with the helium sight glass and the study's kit changes
from vp4_glass.py:

  build_materials4()   round 3's build_materials(), then vp4_glass.carry(): bands #9C8CB0, ceramic
                       gauge faces, every pane and glass a window (non-refracting);
  he_line()            round 3's, its end collars dark steel;
  sight_tank()         the sight glass in mix A, set in the helium line;
  run4()               round 3's run(), then the helium-only glow frames and the glass mask.

No round-1, -2 or -3 file is changed; nothing is written beside them (no bytecode).
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from vpb3_kit import *  # noqa: F401,F403,E402
import vpb3_kit as K  # noqa: E402
import vp4_glass as G  # noqa: E402


def build_materials4(lead_tops=((0.6, 0.3), (1.0, 0.3))):
    K.build_materials(lead_tops)
    G.carry(K)


he_line = G.dark_flanges(K, K.he_line)
stroke_pulse = G.stroke_pulse


def sight_tank(p0, p1, drawn, **kw):
    return G.sight_tank(K, p0, p1, drawn, **kw)


def axis_pts(p0, p1, d=0.1):
    """The point d before p0 and d past p1 on the tank's axis, so a line meets each stub square."""
    a = (Vector(p1) - Vector(p0)).normalized()
    return tuple(Vector(p0) - a * d), tuple(Vector(p1) + a * d)


def run4(meta, nf=24):
    G.run4(K, K.run, meta, nf)
