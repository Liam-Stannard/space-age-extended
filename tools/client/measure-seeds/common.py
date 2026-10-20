"""Shared by measure.py (the numbers, on a headless server) and rings.py (the
ring screenshots, in a client through tools/client/launch.sh)."""

import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MOD_NAME = "sae-measure-seeds"
DEFAULT_SETTINGS = os.path.join(HERE, "settings", "core.json")
# The launcher's lock (tools/client/launch.sh): holding it keeps every client
# out while the server runs, and the server out while a client runs.
LOCK_FILE = os.path.join(os.environ.get("XDG_RUNTIME_DIR") or "/tmp", "sae-factorio-client.lock")


class Usage(Exception):
    """A bad argument: exit 2."""


def factorio_bin():
    b = os.environ.get("FACTORIO_BIN")
    if b:
        return b
    for c in (os.path.expanduser("~/.steam/debian-installation/steamapps/common/Factorio/bin/x64/factorio"),
              os.path.expanduser("~/.steam/steam/steamapps/common/Factorio/bin/x64/factorio")):
        if os.access(c, os.X_OK):
            return c
    raise Usage("no Factorio binary (set FACTORIO_BIN)")


def parse_seed(text, where):
    try:
        s = int(text, 10)
    except ValueError:
        raise Usage(f"{where}: '{text}' is not a seed") from None
    if not 0 <= s <= 0xFFFFFFFF:
        raise Usage(f"{where}: {s} is not a 32-bit seed")
    return s


def read_seeds(seeds_arg, seeds_file):
    """A comma list (--seeds) and/or a file, one seed a line, '#' comments."""
    out = []
    if seeds_file:
        with open(seeds_file, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                line = line.split("#", 1)[0].strip()
                if line:
                    out.append(parse_seed(line, f"{seeds_file}:{n}"))
    if seeds_arg:
        out += [parse_seed(t.strip(), "--seeds") for t in seeds_arg.split(",") if t.strip()]
    if not out:
        raise Usage("no seeds (--seeds or --seeds-file)")
    if len(set(out)) != len(out):
        raise Usage("a seed is listed twice")
    return out


def load_settings(path):
    with open(path, encoding="utf-8") as f:
        s = json.load(f)
    for k in ("planet", "landing", "radius", "pool_tile", "shore_tile", "rule", "patches"):
        if k not in s:
            raise Usage(f"{path}: no '{k}'")
    r = s["rule"]
    for k in ("none_within", "nearest_min", "nearest_max"):
        if not isinstance(r.get(k), (int, float)):
            raise Usage(f"{path}: rule.{k} must be a number")
    keys = [p.get("key") for p in s["patches"]]
    if len(set(keys)) != len(keys) or not all(isinstance(k, str) and k for k in keys):
        raise Usage(f"{path}: every patch needs its own key")
    return s


def build_mod(dest_dir, config):
    """Copy the harness mod into dest_dir with config.lua beside it; return its path."""
    text = json.dumps(config, separators=(",", ":"))
    if "]==]" in text:
        raise Usage("the settings may not contain ]==]")
    mod = os.path.join(dest_dir, MOD_NAME)
    shutil.copytree(os.path.join(HERE, "mod"), mod)
    with open(os.path.join(mod, "config.lua"), "w", encoding="utf-8") as f:
        f.write("return [==[%s]==]\n" % text)
    return mod


def running_factorio():
    """Every running factorio process, as pgrep -a -x prints it (launch.sh's test)."""
    r = subprocess.run(["pgrep", "-a", "-x", "factorio"], capture_output=True, text=True, check=False)
    return r.stdout.strip()


def mod_name_of(path):
    with open(os.path.join(path, "info.json"), encoding="utf-8") as f:
        return json.load(f)["name"]


def die(prog, msg, code=2):
    print(f"{prog}: {msg}", file=sys.stderr)
    sys.exit(code)
