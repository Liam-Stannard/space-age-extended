#!/usr/bin/env python3
"""T06g: measures.txt -- measure.py's figures for each form's four runs, one line a direction (factorio-art-measure).

  python3 measures_txt.py <scratch> <out.txt>

<scratch> holds full-<form>/measure-<d>/measures.json (run-form.sh). legs / press are the model's own --probe (frame
0 of the layer alone, px over half alpha at 4x; probe-<form>/probe.json), not measure.py figures.
"""
import json
import os
import sys

SCR, OUT = sys.argv[1], sys.argv[2]
DIRS = ("north", "east", "south", "west")
lines = ["T06g building forms: measure.py (tools/blender/measure.py, factorio-art-measure) on each form's four runs",
         "(render.sh on the GPU, one run a direction, sun 9.46 = 9.1 x 1.04; --vanilla chemical-plant oil-refinery;",
         "collide on north with the plant's 13 allow patterns and T06g's one more meant contact). Bars (T06g): cover >= 92,",
         "joins 12/12, collide 0, tonal p50 75-81.", ""]
for n, key in enumerate(("casing", "frame", "rotunda"), 1):
    probe = {}
    pp = os.path.join(SCR, f"probe-{key}", "probe.json")
    if os.path.isfile(pp):
        probe = json.load(open(pp))
    for d in DIRS:
        mp = os.path.join(SCR, f"full-{key}", f"measure-{d}", "measures.json")
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
