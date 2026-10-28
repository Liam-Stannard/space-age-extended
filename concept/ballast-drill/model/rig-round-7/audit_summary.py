#!/usr/bin/env python3
"""The support audit, before (T03i, B2) and after (T03l, take C2), as one text list (task
ballast-drill-ports, T03l: "support audit 0 floating"; first written for T03i).

  python3 audit_summary.py <support-before.json> <support-after.json> <out.txt>

Reads audit.py's JSON (dry view: the plate, the press frame at frame 0, the ring, the dry rig; and
wet north). Lists every floating part, and every structural part with open air under part of its
underside, each with the share open, the deepest gap and what carries the rest, grouped by kind:
  span      a roof, floor, lintel, rolled edge or girder carried at its ends (by design)
  collar    a band, collar or cap on a column, wider than the column it rings
  leg       the splayed legs, their bands and root flanges (raked: open under them by nature)
  hatch     a bay's shut hatch over its slot, hung on its hinges
  line      a thin line (grease line, shaft) carried by its fittings
  rig       a wet layer's pipework (runs over the bays and notches, heads, sleeves): carried at its
            junctions, saddles and girders; runs.py checks every run's ends and body (collide)
  port      (T03l) a chute port's lintel over its open mouth (steel angle, 0.30 to 0.34 up, carried
            by its jambs and the plate over it), the tunnel lining's roof, and the chute's own sloping
            bed on its base: spans and slopes by design
  void      anything else: a part over open air
"""
import json
import sys


def kind(o):
    n, m = o["name"], o["mat"]
    if o["group"].startswith("rig-"):
        return "rig"
    if o["group"] == "chute" or (m == "steel" and abs(o["lo"][2] - 0.301) < 0.002 and abs(o["hi"][2] - 0.339) < 0.002):
        return "port"
    if m == "leg" or (m == "iron_worn" and n.startswith("rod")):
        return "leg"
    if o["group"].startswith("door-"):
        return "hatch"
    if m in ("copper", "steel") and (n.startswith("pipe") or n.startswith("Cylinder")):
        return "line"
    if n.startswith(("roof", "housefloor", "lintel", "rigdry-girder")) or m.startswith("house_") and n.startswith("Cylinder"):
        return "span"
    if m in ("column", "copper", "guide", "gear") or (m == "iron" and n.startswith(("lathe", "Cylinder"))):
        return "collar"
    if n.startswith("bastion") and o["deepest_gap"] < 0.05:
        return "edge"
    return "void"


def section(f, label, d):
    f.write(f"== {label}: {d['parts']} parts\n")
    f.write(f"FLOATING (touching nothing that stands): {len(d['floating'])}\n")
    for p in d["floating"]:
        f.write(f"  {p['name']} [{p['mat']}] {p['group']} lo {p['lo']} hi {p['hi']}\n")
    groups = {}
    for o in d["open_under"]:
        groups.setdefault(kind(o), []).append(o)
    f.write(f"OPEN AIR UNDER PART OF THE UNDERSIDE: {len(d['open_under'])} structural parts\n")
    for k in ("void", "port", "edge", "hatch", "span", "collar", "leg", "line", "rig"):
        rows = groups.get(k, [])
        f.write(f"  [{k}] {len(rows)}\n")
        for o in rows:
            f.write(f"    {o['name']} [{o['mat']}] {o['group']}: {o['share'] * 100:.0f}% of {o['samples']} samples open, "
                    f"gap to {o['deepest_gap']}; lo {o['lo']} hi {o['hi']}; carried by {', '.join(o['carried_by'][:4])}\n")


def main():
    b, a, out = sys.argv[1:4]
    B, A = json.load(open(b)), json.load(open(a))
    with open(out, "w") as f:
        f.write(__doc__.split("\n\n")[0] + "\n\n")
        for R in (B, A):
            for v, d in R["views"].items():
                section(f, f"{R['label']}, {v}", d)
                f.write("\n")
    print(out)


if __name__ == "__main__":
    main()
