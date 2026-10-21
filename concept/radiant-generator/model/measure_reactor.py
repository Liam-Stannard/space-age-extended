#!/usr/bin/env python3
"""The nuclear reactor's coverage and rise, measured the way tools/blender/measure.py measures
every building -- its coverage() on its vanilla() still -- for the rise bar Liam set for the
Radiant Generator ("Nuclear reactor", task radiant-generator-options, T08: "rise <= the nuclear
reactor's (measured)").

Why a script of its own: measure.py's --vanilla references (REFS) have no nuclear reactor. This
adds one entry to its REFS for this run only -- the picture's two layers and its pipes under
them, as base/prototypes/entity/entities.lua draws them (lower_layer_picture under picture;
geometry read from the prototype by measure.sprite_geometry) -- and calls the same functions,
so the figure is measure.py's.

  python3 concept/radiant-generator/model/measure_reactor.py [--out <json>]
"""
import json
import os
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import measure  # noqa: E402

measure.REFS["nuclear-reactor"] = dict(label="nuclear reactor", footprint=(5, 5), layers={"*": [
    ("base/graphics/entity/nuclear-reactor/reactor-pipes.png", "base"),
    ("base/graphics/entity/nuclear-reactor/reactor.png", "base"),
    ("base/graphics/entity/nuclear-reactor/reactor-shadow.png", "shadow"),
]})

out = {}
for name in ("nuclear-reactor", "steam-engine", "steam-turbine", "fusion-generator"):
    label, foot, still, shadow, light = measure.vanilla(name, "")
    out[name] = dict(label=label, coverage=measure.coverage(still, foot, (still.width / 2, still.height / 2)),
                     tonal=measure.tonal(still))
text = json.dumps(out, indent=1)
if "--out" in sys.argv:
    with open(sys.argv[sys.argv.index("--out") + 1], "w") as f:
        f.write(text + "\n")
print(text)
