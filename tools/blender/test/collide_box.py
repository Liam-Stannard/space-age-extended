"""Test model: the test box (box.py) with a --collide, for render.sh --collide.

  tools/blender/render.sh tools/blender/test/collide_box.py <out-dir> --collide [--ports] [--icon]
  SAE_TEST_CLASH=1 tools/blender/render.sh tools/blender/test/collide_box.py <out-dir> --collide

Without --collide it is box.py, run as it stands: the same declaration, the same renders and
the same numbers (box.py's docstring says what they are).

With --collide it renders nothing. It builds box.py's scene (box.py run with rig.render made
a no-op), puts the slider at each frame of its declared path in turn, and tests it against
every other part of the box, printing in the shape the models' --collide print and
measure.py's collide step reads (render.sh --collide uses that step):

  COLLIDE parts <n>, slider frames <n>
  COLLIDE slider x <group> <part>: frames [...]     one line a clash
  COLLIDE clashes <n>

A clash is two parts' boxes -- each part's bounding box in the box's own space, in tiles --
overlapping by more than EPS on all three axes, so a part resting on another (the slider on
the roof, 0 deep) is not one. Every part of the box is a block, a slab or a post, so its
bounding box is near enough its volume for a fixture; a building's own check is its own
(the reaction plant's is by BVH).

SAE_TEST_CLASH=1 stands a stop on the roof in the slider's path, which its last frame runs
into, so the run prints

  COLLIDE slider x stop <part>: frames [3]
  COLLIDE clashes 1

and render.sh --collide exits 1 before it renders anything.
"""
import os
import runpy
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
BOX = os.path.join(HERE, "box.py")
sys.path.insert(0, os.path.dirname(HERE))
import rig  # noqa: E402

EPS = 0.005                 # tiles: deeper than this on every axis is a clash
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def bounds(o, into):
    """o's bounding box in the space `into` maps world space to: (lows, highs), x y z."""
    m = into @ o.matrix_world
    pts = [m @ Vector(c) for c in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def depth(a, b):
    """How far two boxes overlap on the axis they overlap least: <= 0 when they do not."""
    return min(min(a[1][i], b[1][i]) - max(a[0][i], b[0][i]) for i in range(3))


def collide():
    rig.render = lambda path: None          # box.py builds its scene and renders nothing
    box = runpy.run_path(BOX, run_name="__main__")
    if os.environ.get("SAE_TEST_CLASH") == "1":
        # a stop on the roof, in the slider's path: its last frame (0.4375 tiles east) runs into it
        box["box"]((0.05, -0.35, box["TOP"] + 0.075), (0.1, 0.3, 0.15), "cap", "stop")
    root, slider, start = box["ROOT"], box["SLIDER"], box["SLIDER0"]
    path = box["DECL"]["animations"][0]["path"]
    bpy.context.view_layer.update()
    into = root.matrix_world.inverted()     # the box's own space: tiles, as modelled
    others = [(g, o) for g, objs in box["PARTS"].items() for o in objs if o is not slider]
    print(f"COLLIDE parts {len(others) + 1}, slider frames {len(path)}")
    hits = {}
    for f, (dx, dy, dz) in enumerate(path):
        slider.location = (start[0] + dx, start[1] + dy, start[2] + dz)
        bpy.context.view_layer.update()
        mine = bounds(slider, into)
        for g, o in others:
            if depth(mine, bounds(o, into)) > EPS:
                hits.setdefault((g, o.name), []).append(f)
    for (g, name), frames in sorted(hits.items()):
        print(f"COLLIDE slider x {g} {name}: frames {frames}")
    print(f"COLLIDE clashes {len(hits)}")


if "--collide" in argv:
    collide()
else:
    runpy.run_path(BOX, run_name="__main__")
