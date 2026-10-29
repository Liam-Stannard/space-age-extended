#!/usr/bin/env python3
"""T06h: measures.txt for the refined casing (a copy of round-forms/measures_txt.py, T06g; <scratch> holds full/
and probe/, and form 1 as T06g measured it is quoted beside it).
T06g: measures.txt -- measure.py's figures for each form's four runs, one line a direction (factorio-art-measure).

  python3 measures_txt.py <scratch> <out.txt>

<scratch> holds full-<form>/measure-<d>/measures.json (run-form.sh). legs / press are the model's own --probe (frame
0 of the layer alone, px over half alpha at 4x; probe-<form>/probe.json), not measure.py figures.
"""
import json
import os
import sys

SCR, OUT = sys.argv[1], sys.argv[2]
DIRS = ("north", "east", "south", "west")
lines = ["T06h refined casing: measure.py (tools/blender/measure.py, factorio-art-measure) on its four runs",
         "(render.sh on the GPU, one run a direction, sun 10.8, the world's fill 0.55; --vanilla chemical-plant oil-refinery;",
         "collide on north with the plant's 13 allow patterns and T06g's one more meant contact). Bars (T06h): cover >= 92,",
         "joins 12/12, collide 0, the clipping check, tonal p50 75-81 in every direction.", "",
         "Form 1 as T06g committed it (round-forms/measures.txt, sun 9.46, fill 0.24): plate p50 N 75, E 70, S 74, W 67;",
         "cover 95.3/94.3/95.1/94.0; joins 12/12; collide PASS.", ""]
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
