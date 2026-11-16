"""T08 (task ballast-drill-ports, the icon): the icon from the signed-off cast take, dry.

  SAE_RIG_TAKE=cast <BLENDER> -b --python concept/ballast-drill/model/rig-round-8/icon_take.py -- <dir> --icon
  python3 tools/key-icons.py <sheets> <dir>/icon.png:icon

(render.sh's --icon step, without its main pass.) rig_take.py's anim path: ballast_drill_b2.py's
scene build, rig_parts.py's plate and the take's dry rig (both in the body, so STATIC), then the
model's own passes from its FITTINGS check on, of which --icon renders icon.png: the whole machine,
every hatch shut, the ring raised, nothing wet.

One change from the model's --icon, and the only reason this file exists: the frame. Round 7's
5.9 tiles cut B2's plate wall off at the top of the render (the plate fills the footprint to its
north edge, so the machine stands taller in the camera than round 7's did); ICON_SCALE tiles
across leave margin all round. key-icons.py crops to the drawn machine, so the frame only has to
hold it. Neither rig_take.py nor ballast_drill_b2.py is changed.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "ballast_drill_b2.py")
TAKE = os.environ.get("SAE_RIG_TAKE", "cast")
ICON_SCALE = float(os.environ.get("SAE_ICON_SCALE", "7.0"))
assert "--icon" in sys.argv, "icon_take.py renders the icon only: pass --icon"

src = open(MODEL).read().split("\n")


def _line(prefix, after=0):
    return next(i for i, s in enumerate(src) if i >= after and s.startswith(prefix))


a_end = _line("if PORTS:", _line("BOUNCE = rig.bounce_ground()"))
b0 = _line("DOORS = tuple(")
b1 = _line("if FITTINGS:", b0)
G = {"__name__": "__main__", "__file__": MODEL}
exec(compile("\n".join(src[:a_end]), MODEL, "exec"), G)
exec(compile("\n" * b0 + "\n".join(src[b0:b1]), MODEL, "exec"), G)

sys.path.insert(0, HERE)
import rig_parts  # noqa: E402

rig_parts.main(G, TAKE, "anim", False)
old = ("    k = 1024 / 5.9\n"
       "    rig.camera(1024, 1024, centre_px=(512, 512 + k * 0.18), ss=1).data.ortho_scale = 5.9")
assert old in "\n".join(src[b1:]), "the model's icon camera has changed: recheck icon_take.py"
rest = ("\n" * b1 + "\n".join(src[b1:])).replace(
    old, f"    k = 1024 / {ICON_SCALE}\n"
         f"    rig.camera(1024, 1024, centre_px=(512, 512 + k * 0.18), ss=1).data.ortho_scale = {ICON_SCALE}", 1)
print(f"ICON take {TAKE!r}, frame {ICON_SCALE} tiles", flush=True)
exec(compile(rest, MODEL, "exec"), G)
