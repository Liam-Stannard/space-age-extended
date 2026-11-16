#!/usr/bin/env python3
"""One sheets directory per take for measure.py (task ballast-drill-ports, T03d): the take's
plate and its shadow, the take's wet rig, and the signed-off animated layers, in the order the
engine draws them as a wet drill (vanilla's wet_mining_graphics_set, big-mining-drill.lua:
229-546):

  base (plate), base-shadow, rig-shadow, rig (behind), chute, stroke, rig-front

  python3 combine.py <signed-off sheets> <take plate out-dir> <take rig out-dir> <out sheets dir> [--dry]

--dry leaves the rig out (the drill on an ore with no fluid). No render.json is written:
measure.py reads the sheets alone (--footprint 5x5), classing them by name and drawing them in
meta.json's order; ore and dust (working only) are left out, so the still is the stopped
machine's. Each single-frame rig sheet is given frames 1, so measure.py draws it as a layer of
the still rather than ignoring it.
"""
import json
import os
import shutil
import sys

DIRS = ("north", "east", "south", "west")


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    dry = "--dry" in sys.argv
    signed, plate, rigd, out = a
    os.makedirs(out, exist_ok=True)
    sm = json.load(open(os.path.join(signed, "meta.json")))
    pm = json.load(open(os.path.join(plate, "sheets", "meta.json")))
    rm = {} if dry else json.load(open(os.path.join(rigd, "sheets", "meta.json")))
    meta = {}

    def take(src_meta, src_dir, stem, frames=None):
        m = dict(src_meta[stem])
        if frames is not None and "frames" not in m:
            m["frames"], m["line_length"] = frames, 1
        meta[stem] = m
        shutil.copy(os.path.join(src_dir, stem + ".png"), os.path.join(out, stem + ".png"))
    for d in DIRS:
        take(pm, os.path.join(plate, "sheets"), f"base-{d}")
        take(pm, os.path.join(plate, "sheets"), f"base-shadow-{d}")
        if not dry:
            take(rm, os.path.join(rigd, "sheets"), f"rig-shadow-{d}")
            take(rm, os.path.join(rigd, "sheets"), f"rig-{d}", frames=1)
        take(sm, signed, f"chute-{d}")
        take(sm, signed, f"stroke-{d}")
        if not dry:
            stem = f"rig-front-{d}"
            m = dict(rm[stem])
            meta[stem] = m
            shutil.copy(os.path.join(rigd, "sheets", stem + ".png"), os.path.join(out, stem + ".png"))
    with open(os.path.join(out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(out, len(meta), "sheets")


if __name__ == "__main__":
    main()
