"""T03l (rig-round-7): take C2 on the B2 body with the ports (c2.py; b2/sec_ports.py, b2/sec_chute.py).
T03i (rig-round-6): the body is ballast_drill_b2.py (B2, the drill rebuilt on the 0.85 plate),
and a third pass, anim, renders the model's own passes (plate, still, shadow, lamp, chute, ore,
stroke, dust) on it, since the gear-houses, guide columns and shoes the stroke draws have moved.
  SAE_RIG_PASS=anim  [SAE_RIG_ONE=north]  the model's passes on the B2 body (render.sh packs them)
  SAE_RIG_PASS=support [SAE_RIG_R5=1]     the support audit (audit.py), of B2 or, with SAE_RIG_R5,
                                         of T03h (the signed-off body and rig-round-5's rig), for
                                         the before
The Ballast Drill's fluid rig, one take (task ballast-drill-ports, T03e: round 2; T03f: round 3, the steel frame;
T03g: round 4, the cast take's gaps filled; T03h: round 5, the drill on a raised plate).

  SAE_RIG_TAKE=<take> SAE_RIG_PASS=<plate|rig> tools/blender/render.sh \
      concept/ballast-drill/model/rig-round-5/rig_take.py <out-dir> [--collide]

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
R5 = bool(os.environ.get("SAE_RIG_R5"))
MODEL = os.path.normpath(os.path.join(HERE, "..", "ballast_drill.py") if R5 else os.path.join(HERE, "ballast_drill_b2.py"))
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
if R5:
    # the before: T03h's build (the signed-off body, rig-round-5's rig), audited by this round's audit.py
    import audit  # noqa: E402
    sys.path.insert(0, os.path.join(HERE, "..", "rig-round-5"))
    import importlib.util  # noqa: E402
    spec = importlib.util.spec_from_file_location("rig_parts_r5", os.path.join(HERE, "..", "rig-round-5", "rig_parts.py"))
    r5 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r5)
    rr = r5.Rig(G, TAKE)
    rr.cut_back()
    rr.fix_gaps()
    rr.plate()
    rr.dry_rig()
    rr.pockets()
    rr.wet()
    audit.support(G, rr, "before (T03h, rig-round-5 at 401696a)")
    raise SystemExit(0)

import rig_parts  # noqa: E402

rig_parts.main(G, TAKE, PASS, COLLIDE)
if PASS == "anim":
    # the model's own passes, from its FITTINGS check on, on the B2 body with the take's dry rig; with
    # SAE_RIG_ONE the one direction, unsuffixed
    if rig_parts.ONE:
        assert rig_parts.ONE == "north", "the one-direction anim pass is north's"
        G["DECL"]["directions"] = "one"
        for k in ("OPEN", "NUDGE"):
            G[k][""] = G[k]["north"]
    rest = "\n" * b1 + "\n".join(src[b1:])
    rest = rest.replace('"south": (-0.75, 0.85, 1.05, 3.2), "west": (-3.15, -1.35, -1.0, 0.75)}',
                        '"south": (-0.75, 0.85, 1.05, 3.2), "west": (-3.15, -1.35, -1.0, 0.75)}\n'
                        'WINDOWS[""] = WINDOWS["north"]', 1)
    exec(compile(rest, MODEL, "exec"), G)
