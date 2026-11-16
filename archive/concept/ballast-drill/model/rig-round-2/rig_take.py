"""The Ballast Drill's fluid rig, one take (task ballast-drill-ports, T03e: round 2, for Liam).

  SAE_RIG_TAKE=<take> SAE_RIG_PASS=<plate|rig> tools/blender/render.sh \
      concept/ballast-drill/model/rig-round-2/rig_take.py <out-dir> [--collide]

The signed-off model (../ballast_drill.py) is not changed. This script runs its scene build
(everything up to its passes) and its pass helpers (setup and the rest) in its own namespace,
then rig_parts.py cuts the casings back and builds the take's rig, and one of two passes
renders:
  plate  the body with its casings cut back and the take's dry rig (what draws on every drill,
         wet or dry): base-<d> and base-shadow-<d>, the same in every direction as the
         signed-off plate is. The stroke, chute, ore and dust layers are the signed-off ones.
  rig    the wet layers per direction (wet_mining_graphics_set only, as vanilla's
         pipe-connections): "behind" (rig-<d>: over the plate, under the chute, stroke, ore and
         dust), "front" (rig-front-<d>: over all of them) and the shadow (rig-shadow-<d>);
         each rendered with the plate's parts, the press frame and the raised ring held out,
         so whatever stands in front of a part hides it.
--collide (render.sh's): rig_parts.collide(): every part of the take's rig and wall fittings
against every other mesh of the drill and against each other, by BVH overlap of the
evaluated meshes; meant contacts (a flange bolted to the wall it sits on) are named in the
take, not wildcarded. Prints "COLLIDE <a> x <b>" per clash and "COLLIDE clashes <n>".
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.normpath(os.path.join(HERE, "..", "ballast_drill.py"))
TAKE = os.environ.get("SAE_RIG_TAKE", "")
PASS = os.environ.get("SAE_RIG_PASS", "rig")

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
COLLIDE = "--collide" in _argv
# the model sees its out-dir and no flag of ours: its own --collide (the tanks') would exit
sys.argv = sys.argv[:sys.argv.index("--") + 1] + [a for a in _argv if a != "--collide"] if "--" in sys.argv \
    else sys.argv
for a in _argv:
    if a.startswith("--take="):
        TAKE = a.split("=", 1)[1]
    elif a.startswith("--pass="):
        PASS = a.split("=", 1)[1]

src = open(MODEL).read().split("\n")


def _line(prefix, after=0):
    return next(i for i, s in enumerate(src) if i >= after and s.startswith(prefix))


a_end = _line("if PORTS:", _line("BOUNCE = rig.bounce_ground()"))
b0 = _line("DOORS = tuple(")
b1 = _line("if FITTINGS:", b0)
G = {"__name__": "__main__", "__file__": MODEL}
t0 = time.time()
exec(compile("\n".join(src[:a_end]), MODEL, "exec"), G)
exec(compile("\n" * b0 + "\n".join(src[b0:b1]), MODEL, "exec"), G)
print(f"RIG scene built in {time.time() - t0:.0f} s; take {TAKE!r}, pass {PASS!r}", flush=True)

sys.path.insert(0, HERE)
import rig_parts  # noqa: E402

rig_parts.main(G, TAKE, PASS, COLLIDE)
