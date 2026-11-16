#!/usr/bin/env python3
"""The round's figures, per take, from measure.py's measures.json and the collide log
(task ballast-drill-ports, T03d; T03f adds runs.py's counts).

  python3 summarise.py <signed-off measures.json> <out.json> <take>=<take out-dir> ...

Per take: joins passed of 16 (wet, vanilla's covers and pipe per measure.py's rule); collide
clashes (rig_parts.collide via render.sh --collide); finish and tonal of the plate and of the
still, wet and dry, beside the signed-off drill's; footprint coverage dry and wet; the run
diameters (rig.json).
"""
import json
import os
import re
import sys


def load(p):
    return json.load(open(p)) if os.path.isfile(p) else None


def main():
    signed, out = load(sys.argv[1]), sys.argv[2]
    res = {"signed": {"still_north": {k: signed["directions"]["north"][k]["still"] for k in ("tonal", "finish")},
                      "plate_north": {k: signed["directions"]["north"][k]["plate"] for k in ("tonal", "finish")},
                      "coverage_pct": signed["directions"]["north"]["coverage"]["footprint_pct"]}}
    for arg in sys.argv[3:]:
        name, d = arg.split("=", 1)
        wet, dry = load(os.path.join(d, "measures-wet", "measures.json")), load(os.path.join(d, "measures-dry",
                                                                                              "measures.json"))
        r = {}
        if wet:
            joins = [j for dn in wet["directions"].values() for j in dn.get("joins", [])]
            r["joins"] = f"{sum(1 for j in joins if j['pass'])}/{len(joins)}"
            r["join_gap_columns_max"] = max(j["gap"]["columns"] for j in joins)
            r["wet"] = {dn: {"coverage_pct": x["coverage"]["footprint_pct"], "tonal_still": x["tonal"]["still"],
                             "finish_still": x["finish"]["still"]} for dn, x in wet["directions"].items()}
            r["plate"] = {k: wet["directions"]["north"][k]["plate"] for k in ("tonal", "finish")}
        if dry:
            r["dry"] = {dn: {"coverage_pct": x["coverage"]["footprint_pct"], "tonal_still": x["tonal"]["still"],
                             "finish_still": x["finish"]["still"]} for dn, x in dry["directions"].items()}
        log = os.path.join(d, "rig", "collide.log")
        if os.path.isfile(log):
            text = open(log).read()
            m = re.findall(r"COLLIDE clashes (\d+)", text)
            r["collide_clashes"] = int(m[-1]) if m else None
            # T03f: and runs.py's counts, per direction (ends, untested, body, ground)
            r["runs_clashes"] = sum(int(x) for x in re.findall(r"COLLIDE (?:ends|untested|body|ground|runs not "
                                                                r"checked): (\d+) clashes", text))
        rj = load(os.path.join(d, "rig", "hi", "rig.json"))
        if rj:
            r["diameters"] = rj["directions"]
        res[name] = r
    json.dump(res, open(out, "w"), indent=1)
    for name, r in res.items():
        if name == "signed":
            print("signed-off:", r)
            continue
        print(f"{name}: joins {r.get('joins')} (max gap cols {r.get('join_gap_columns_max')}), clashes "
              f"{r.get('collide_clashes')}, runs.py {r.get('runs_clashes')}, plate {r.get('plate')}")
        for dn in ("north", "east", "south", "west"):
            w, y = r.get("wet", {}).get(dn), r.get("dry", {}).get(dn)
            if w and y:
                print(f"   {dn}: cover wet {w['coverage_pct']} dry {y['coverage_pct']}; still wet "
                      f"{w['tonal_still']} {w['finish_still']}; dry {y['tonal_still']} {y['finish_still']}")


if __name__ == "__main__":
    main()
