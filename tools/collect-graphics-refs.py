#!/usr/bin/env python3
"""List every graphics/sound path the mod's prototypes name, one per line.

Split out of check-graphics.sh because a single grep for a whole quoted path
cannot see the pattern every building plate uses. Sprite blocks are written as

    local ART = "__space-age-extended__/graphics/entity/arc-mast/"
    ...
    filename = ART .. "base.png",

and the path only exists once the two halves are joined. The old regex matched
the prefix -- a directory, which is never a file -- and skipped the four plates
entirely, so `check-graphics.sh` was reporting OK on a mod whose building art it
had never looked at. Every building added from here uses that pattern, so the
blind spot would have grown with each one.

So: collect the whole-literal paths as before, and additionally resolve
`local NAME = "__mod__/dir/"` bindings against `NAME .. "file.png"` uses. The
binding is file-local and last-assignment-wins, which is how the prototypes
actually use it -- no attempt is made to interpret Lua beyond that.
"""

import os
import re
import sys

LITERAL = re.compile(r'"(__[a-z-]+__/[^"]+\.(?:png|ogg))"')
BINDING = re.compile(r'^\s*local\s+([A-Za-z_]\w*)\s*=\s*"(__[a-z-]+__/[^"]*)"')
JOINED = re.compile(r'\b([A-Za-z_]\w*)\s*\.\.\s*"([^"]+\.(?:png|ogg))"')


def refs_in(path):
    out = set()
    prefixes = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.split("--", 1)[0] if line.lstrip().startswith("--") else line
            out.update(LITERAL.findall(line))
            bind = BINDING.match(line)
            if bind:
                prefixes[bind.group(1)] = bind.group(2)
            for name, tail in JOINED.findall(line):
                if name in prefixes:
                    out.add(prefixes[name] + tail)
    return out


def main():
    roots = sys.argv[1:]
    found = set()
    for root in roots:
        if os.path.isfile(root):
            found |= refs_in(root)
            continue
        for dirpath, _, names in os.walk(root):
            for name in names:
                if name.endswith(".lua"):
                    found |= refs_in(os.path.join(dirpath, name))
    for ref in sorted(found):
        print(ref)


if __name__ == "__main__":
    main()
