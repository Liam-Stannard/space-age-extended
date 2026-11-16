#!/usr/bin/env python3
"""One sheets directory per take for measure.py (task ballast-drill-ports, T03d): the take's
plate and its shadow, the take's wet rig, and the signed-off animated layers, in the order the
engine draws them as a wet drill (vanilla's wet_mining_graphics_set, big-mining-drill.lua:
229-546):

  base (plate), base-shadow, rig-shadow, rig (behind), chute, stroke, rig-front

  python3 combine.py <signed-off sheets> <take plate out-dir> <take rig out-dir> <out sheets dir> [--dry]

--one <direction> (T03h, the one-direction proof): the take's plate and rig were rendered for that
direction alone (directions "one", files unsuffixed); the signed-off layers of that direction are
taken with the suffix dropped, so measure.py reads one direction.
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
    argv = sys.argv[1:]
    one = ""
    if "--one" in argv:
        i = argv.index("--one")
        one = argv[i + 1]
        del argv[i:i + 2]
    a = [x for x in argv if not x.startswith("--")]
    dry = "--dry" in argv
    signed, plate, rigd, out = a
    os.makedirs(out, exist_ok=True)
    sm = json.load(open(os.path.join(signed, "meta.json")))
    pm = json.load(open(os.path.join(plate, "sheets", "meta.json")))
    rm = {} if dry else json.load(open(os.path.join(rigd, "sheets", "meta.json")))
    meta = {}

    def take(src_meta, src_dir, stem, frames=None, dest=None):
        dest = dest or stem
        m = dict(src_meta[stem])
        if frames is not None and "frames" not in m:
            m["frames"], m["line_length"] = frames, 1
        meta[dest] = m
        shutil.copy(os.path.join(src_dir, stem + ".png"), os.path.join(out, dest + ".png"))
    for d in ((one,) if one else DIRS):
        sfx = "" if one else f"-{d}"
        take(pm, os.path.join(plate, "sheets"), f"base{sfx}")
        take(pm, os.path.join(plate, "sheets"), f"base-shadow{sfx}")
        if not dry:
            take(rm, os.path.join(rigd, "sheets"), f"rig-shadow{sfx}")
            take(rm, os.path.join(rigd, "sheets"), f"rig{sfx}", frames=1)
        # T03i: the animated layers are the take's own (anim pass); one-direction ones unsuffixed
        for stem in ("chute", "stroke"):
            take(sm, signed, f"{stem}-{d}" if f"{stem}-{d}" in sm else stem, dest=f"{stem}{sfx}")
        if not dry:
            take(rm, os.path.join(rigd, "sheets"), f"rig-front{sfx}")
    with open(os.path.join(out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(out, len(meta), "sheets")


if __name__ == "__main__":
    main()
