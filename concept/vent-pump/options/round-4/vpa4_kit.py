"""Vent Pump, round 4 (T03), artist A's half (concepts 1, 2, 5, 7): round 3's kit (../round-3/vpa3_kit.py,
itself over ../round-2/vpa_kit.py), used unchanged, with the helium sight glass and the study's kit
changes from vp4_glass.py:

  build_materials4()   round 3's build_materials3(), then vp4_glass.carry(): bands #9C8CB0, ceramic
                       gauge faces, every pane and glass a window (non-refracting);
  he_line()            round 3's, its end flanges dark steel;
  sight_tank()         the sight glass in mix A, set in the helium line;
  run4()               round 3's run3(), then the helium-only glow frames and the glass mask.

No round-1, -2 or -3 file is changed; nothing is written beside them (no bytecode).
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "round-3"))
from vpa3_kit import *  # noqa: F401,F403,E402
import vpa3_kit as K3  # noqa: E402
import vpa_kit as K  # noqa: E402
import vp4_glass as G  # noqa: E402


def build_materials4(lead_tops):
    build_materials3(lead_tops)
    G.carry(K)


he_line = G.dark_flanges(K, K3.he_line)
stroke_pulse = G.stroke_pulse


def sight_tank(p0, p1, drawn, **kw):
    return G.sight_tank(K, p0, p1, drawn, **kw)


def axis_pts(p0, p1, d=0.1):
    """The point d before p0 and d past p1 on the tank's axis, so a line meets each stub square."""
    from mathutils import Vector
    a = (Vector(p1) - Vector(p0)).normalized()
    return tuple(Vector(p0) - a * d), tuple(Vector(p1) + a * d)


def run4(meta, nf=32):
    G.run4(K, run3, meta, nf)
