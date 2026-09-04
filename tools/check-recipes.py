#!/usr/bin/env python3
"""Verify every mod recipe can actually be made somewhere.

A recipe with more fluid connections than any machine in its category has fluid
boxes is accepted by the data stage, accepted by set_recipe, and then never
runs -- the machine simply sits there with no recipe. Nothing else catches it.

Reads a data-raw dump; pass its path, or let it find the usual one.
"""
import json, sys, glob, os

def find_dump():
    if len(sys.argv) > 1:
        return sys.argv[1]
    for pattern in (
        os.path.expanduser("~/.factorio/script-output/data-raw-dump.json"),
        "/tmp/claude-1000/**/data-raw-dump.json",
    ):
        hits = sorted(glob.glob(pattern, recursive=True), key=os.path.getmtime)
        if hits:
            return hits[-1]
    sys.exit("no data-raw dump found; pass one as an argument")

d = json.load(open(find_dump()))

# how many fluid boxes each crafting machine offers, by category
capacity = {}
for ptype in ("assembling-machine", "furnace", "rocket-silo"):
    for name, p in d.get(ptype, {}).items():
        ins = outs = 0
        for box in (p.get("fluid_boxes") or []):
            if isinstance(box, dict):
                if box.get("production_type") == "input":
                    ins += 1
                elif box.get("production_type") == "output":
                    outs += 1
        for cat in (p.get("crafting_categories") or []):
            best = capacity.get(cat, (0, 0, name))
            if (ins, outs) > best[:2]:
                capacity[cat] = (ins, outs, name)

problems = []
for name, r in d.get("recipe", {}).items():
    if not name.startswith("sae-"):
        continue
    fin = sum(1 for i in (r.get("ingredients") or []) if i.get("type") == "fluid")
    fout = sum(1 for o in (r.get("results") or []) if o.get("type") == "fluid")
    if fin == 0 and fout == 0:
        continue
    cats = r.get("categories") or ([r["category"]] if "category" in r else ["crafting"])
    ok = False
    detail = []
    for cat in cats:
        ins, outs, machine = capacity.get(cat, (0, 0, "(no machine)"))
        detail.append(f"{cat} best={machine} {ins}in/{outs}out")
        if ins >= fin and outs >= fout:
            ok = True
    if not ok:
        problems.append(f"  {name}: needs {fin}in/{fout}out -- " + "; ".join(detail))

if problems:
    print("Recipe check FAILED: no machine can hold these recipes' fluids.")
    print("\n".join(problems))
    sys.exit(1)

print("Recipes OK -- every mod recipe fits a machine that can hold its fluids.")
