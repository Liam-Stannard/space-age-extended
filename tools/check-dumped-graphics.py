#!/usr/bin/env python3
"""Check every file the mod's prototypes reference, as the engine resolved them.

`check-graphics.sh` scans the Lua source for quoted paths. That works until a
path is built rather than written, and this mod builds most of them:

    local ART = "__mod__/graphics/entity/arc-mast/"
    filename = ART .. "base.png"                    -- two parts
    filename = RG .. "base-" .. dir .. ".png"       -- three, one a variable
    t[k] = v:gsub(STONE, BED)                       -- rewritten at load time

`tools/collect-graphics-refs.py` learned the two-part form after the arc mast's
four plates turned out never to have been checked at all. It cannot learn the
rest without becoming a Lua interpreter -- and the radiant generator's plates
slipped straight past it the same day it was written.

So stop parsing and ask the engine. `--dump-data` writes every prototype with
every path already resolved, whatever Lua did to build it. This walks that dump
and checks the files exist. It is the only check here that cannot be fooled by
how a path was assembled.

Usage: tools/check-dumped-graphics.py <data-raw-dump.json> [factorio-data-dir]
"""

import glob
import json
import os
import re
import sys

REF = re.compile(r'"(__[a-z0-9-]+__/[^"]+\.(?:png|ogg))"')


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: check-dumped-graphics.py <data-raw-dump.json> [data-dir]")
    dump_path = sys.argv[1]
    data = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser(
        "~/.steam/debian-installation/steamapps/common/Factorio/data")
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    mods = {f"__{os.path.basename(p)}__": p
            for p in glob.glob(os.path.join(data, "*")) if os.path.isdir(p)}
    mods["__space-age-extended__"] = repo

    with open(dump_path) as fh:
        dump = json.load(fh)

    refs, missing = set(), []
    for ptype, protos in dump.items():
        if not isinstance(protos, dict):
            continue
        for name, proto in protos.items():
            # Only what this mod defines. Vanilla's own art is vanilla's problem,
            # and walking all of it would take far longer for no information.
            if not isinstance(proto, dict) or not name.startswith("sae-"):
                continue
            for ref in set(REF.findall(json.dumps(proto))):
                refs.add(ref)
                prefix, rest = ref.split("/", 1)
                base = mods.get(prefix)
                if not base or not os.path.isfile(os.path.join(base, rest)):
                    missing.append((ptype, name, ref))

    ours = sum(1 for r in refs if r.startswith("__space-age-extended__"))
    if missing:
        print(f"Dumped graphics check FAILED: {len(missing)} of {len(refs)} "
              f"referenced files do not exist.", file=sys.stderr)
        for ptype, name, ref in sorted(missing):
            print(f"  MISSING  {ptype}/{name}: {ref}", file=sys.stderr)
        return 1

    print(f"Dumped graphics OK -- {len(refs)} files referenced by sae-* "
          f"prototypes all exist ({ours} of them this mod's own).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
