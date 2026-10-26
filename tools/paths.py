#!/usr/bin/env python3
"""tools/paths.conf, read: where this checkout's Factorio and Blender are, for the Python scripts.

    sys.path.insert(0, "<repo>/tools"); import paths
    paths.factorio_bin()     # <FACTORIO_ROOT>/bin/x64/factorio
    paths.factorio_data()    # <FACTORIO_ROOT>/data
    paths.blender()          # BLENDER

Each returns the path as a string, or raises PathsError naming paths.conf and the key: a key
missing, empty or named twice, a path that does not exist, a line that is not KEY=value.
PathsError is a SystemExit, so a script that does not catch it stops (exit 1) with that message
and no traceback -- in Blender's Python too. The paths.conf read is the one beside this file, so
each checkout reads its own. It is parsed line by line, never executed or expanded; the format
is in paths.conf, and tools/paths.sh is the same reader for the shell.

  python3 tools/paths.py          prints all four, labelled; exit 1 naming the first that fails
  python3 tools/paths.py <name>   prints that one path alone (for "$(...)" in a shell): <name> is
                                  factorio-bin, factorio-data, factorio-root or blender. Exit 1,
                                  the message on stderr and nothing on stdout, when it fails;
                                  exit 2 with usage for any other name
"""
import os
import re
import sys

CONF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paths.conf")
LINE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)[ \t\n\r\f\v]*=(.*)\Z", re.S)
BLANK = " \t\n\r\f\v"                   # bash's [[:space:]], as tools/paths.sh trims


class PathsError(SystemExit):
    """paths.conf cannot answer for a key."""


def value(key):
    """KEY's value in paths.conf, as written."""
    try:
        with open(CONF, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise PathsError(f"{CONF}: cannot read it ({e.strerror}), so {key} is unknown") from None
    found = None
    for n, line in enumerate(text.split("\n"), 1):
        line = line[:-1] if line.endswith("\r") else line
        line = line.lstrip(BLANK)
        if not line or line.startswith("#"):
            continue
        m = LINE.match(line)
        if not m:
            raise PathsError(f"{CONF}: line {n} is not KEY=value (reading {key})")
        if m.group(1) != key:
            continue
        if found is not None:
            raise PathsError(f"{CONF}: {key} is set twice (line {n})")
        found = m.group(2).strip(BLANK)
    if found is None:
        raise PathsError(f"{CONF}: no {key}= line")
    if not found:
        raise PathsError(f"{CONF}: {key} is empty")
    return found


def factorio_root():
    """The Factorio install folder."""
    root = value("FACTORIO_ROOT")
    if not os.path.isdir(root):
        raise PathsError(f"{CONF}: FACTORIO_ROOT={root}: no such directory")
    return root


def factorio_bin():
    """<FACTORIO_ROOT>/bin/x64/factorio."""
    root = factorio_root()
    b = os.path.join(root, "bin", "x64", "factorio")
    if not (os.path.isfile(b) and os.access(b, os.X_OK)):
        raise PathsError(f"{CONF}: FACTORIO_ROOT={root} has no executable bin/x64/factorio")
    return b


def factorio_data():
    """<FACTORIO_ROOT>/data: base/, space-age/ and the rest under it."""
    root = factorio_root()
    d = os.path.join(root, "data")
    if not os.path.isdir(os.path.join(d, "base")):
        raise PathsError(f"{CONF}: FACTORIO_ROOT={root} has no data/base directory")
    return d


def blender():
    """The Blender binary."""
    b = value("BLENDER")
    if not (os.path.isfile(b) and os.access(b, os.X_OK)):
        raise PathsError(f"{CONF}: BLENDER={b}: no such executable file")
    return b


NAMES = {"factorio-bin": factorio_bin, "factorio-data": factorio_data, "factorio-root": factorio_root,
         "blender": blender}                # the command line's: one path alone
USAGE = f"usage: python3 tools/paths.py [{' | '.join(NAMES)}]"


def main(argv):
    if not argv:
        for label, get in (("FACTORIO_ROOT", factorio_root), ("factorio binary", factorio_bin),
                           ("factorio data", factorio_data), ("BLENDER", blender)):
            print(f"{label}: {get()}")
        return 0
    if len(argv) != 1 or argv[0] not in NAMES:
        print(USAGE, file=sys.stderr)
        return 2
    print(NAMES[argv[0]]())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
