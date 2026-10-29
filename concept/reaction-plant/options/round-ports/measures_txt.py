#!/usr/bin/env python3
"""T06i: measures.txt for the casing with every run end on a port (a copy of round-forms-refine/measures_txt.py,
T06h, with T06h's own figures quoted beside it).

  python3 measures_txt.py <scratch> <out.txt>

<scratch> holds full/measure-<d>/measures.json (measure.py on render.sh's run-<d>). legs / press are the model's own
--probe (frame 0 of the layer alone, px over half alpha at 4x; probe/probe.json), not measure.py figures.
"""
import json
import os
import sys

SCR, OUT = sys.argv[1], sys.argv[2]
DIRS = ("north", "east", "south", "west")
lines = ["T06i casing, every run end on a port: measure.py (tools/blender/measure.py, factorio-art-measure) on its four runs",
         "(render.sh on the GPU, one run a direction, sun 10.8, the world's fill 0.55, as T06h; --vanilla chemical-plant",
         "oil-refinery; collide on north with 11 allow patterns, one for each meant contact of the animation (forms.py's",
         "MEANT reasons, none of them a port)). Bars: cover >= 92, joins 12/12, collide 0, the clipping check (--clash 0 and by",
         "eye), tonal and finish as T06h.", "",
         "T06h (round-forms-refine/measures.txt, 7114e50):",
         "  north cover 95.3 rise 0.64 p50/p95 plate 81/177 black 8.9 ratio 0.61 blue 2.09 white 0 clipped 3",
         "  east  cover 94.3 rise 0.81 p50/p95 plate 78/176 black 5.9 ratio 0.61 blue 1.21 white 0 clipped 1",
         "  south cover 95.1 rise 0.52 p50/p95 plate 80/181 black 7.8 ratio 0.6  blue 1.34 white 0 clipped 0",
         "  west  cover 94.0 rise 0.73 p50/p95 plate 74/173 black 9.2 ratio 0.6  blue 1.52 white 0 clipped 2", ""]
for n, key in enumerate(("casing",), 1):
    probe = {}
    pp = os.path.join(SCR, "probe", "probe.json")
    if os.path.isfile(pp):
        probe = json.load(open(pp))
    for d in DIRS:
        mp = os.path.join(SCR, "full", f"measure-{d}", "measures.json")
        if not os.path.isfile(mp):
            lines.append(f"{n} {key} {d}: not measured")
            continue
        m = json.load(open(mp))
        dn = m["directions"][next(iter(m["directions"]))]
        c, t, fn, col = dn["coverage"], dn["tonal"], dn["finish"], dn.get("colour", {})
        mo = dn.get("motion") or {}
        tp, ts = t.get("plate", {}), t.get("still", {})
        js = "/".join("PASS" if j["pass"] else "FAIL" for j in dn.get("joins", []))
        cl = m.get("collide")
        cs = "" if d != "north" else f"  collide {'PASS' if (cl or {}).get('pass') else cl}"
        lines.append(
            f"{n} {key:8s} {d:5s} cover {c['footprint_pct']:5.1f}  rise {c['rise_tiles']:.2f}  p50/p95 plate "
            f"{tp.get('p50')}/{tp.get('p95')} still {ts.get('p50')}/{ts.get('p95')}  black {fn.get('plate', {}).get('black_pct')}"
            f" ratio {fn.get('plate', {}).get('ratio')}  blue {col.get('blue_pct')}  white {col.get('white_px')}  clipped "
            f"{col.get('clipped_px')}  moving {mo.get('moving_pct')}  strobe {mo.get('strobe_pct')}  joins {js}  legs "
            f"{probe.get(f'legs-{d}')}  press {probe.get(f'press-{d}')}{cs}")
    lines.append("")
open(OUT, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
