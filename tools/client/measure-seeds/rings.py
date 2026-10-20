#!/usr/bin/env python3
"""tools/client/measure-seeds/rings.py -- screenshots of the landing on given
seeds, with distance rings drawn round it (pool-placed criterion 3: 24 and 50
tiles), in a real client.

Usage:
  tools/client/measure-seeds/rings.py --task NAME (--seeds A,B,... | --seeds-file FILE)
      [--settings FILE] [--worktree DIR] [--mod PATH]... [--timeout S]

  --task NAME        Evidence goes to <repo>/evidence/NAME/ (the launcher's run directory).
  --seeds, --seeds-file, --settings, --worktree, --mod: as measure.py's.
  --timeout S        The client's limit (default 600).

The client runs only through tools/client/launch.sh (one at a time, no
WAYLAND_DISPLAY, --disable-audio, everything it started stopped), on
`--load-scenario base/freeplay`, with the harness mod (mod/) in "rings" mode
and the settings and seeds as its config.lua. For each seed the mod makes the
planet's surface with that seed, measures it as measure.py does, draws
settings.shots.rings (radius and colour) round the landing, a cross on the
landing, a dashed line to the nearest pool tile and a caption, and screenshots
`view_tiles` tiles square at `zoom` at each of `daytimes`. The launcher stops
on the mod's `done`.

Written, in the launcher's run directory: data/script-output/sae-measure-seeds/
landing-<seed>-<daytime>.png, landing-<seed>.json (the seed's measures),
log.txt, errors.txt (only if the mod caught an error); and here, rings.json and
rings.txt: each image's size and, for each ring, the share of 720 bearings
round the landing at which a pixel of the ring's colour lies on the ring's
radius (within its drawn width and 2 px) -- the check that the rings show. A
daytime with "check_rings": false (core.json's night: the engine darkens drawn
objects with the night, so the rings are faint) is measured and reported but
not held to the check; its shot is there for the pool's glow.

Exit: 0 every image was written, none over 8000 px on a side, the mod caught no
error, and on every checked image each ring shows on at least 90% of its bearings;
1 otherwise; 2 usage; the launcher's refusal (3) is passed on.
"""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

sys.dont_write_bytecode = True  # no __pycache__ beside the tools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

PROG = "rings.py"
LAUNCH = os.path.join(common.REPO_ROOT, "tools", "client", "launch.sh")
MAX_SIDE = 8000
SHOW_SHARE = 0.9


def ring_share(img, centre, radius_px, color, half_width):
    """Share of 720 bearings at which a pixel near `color` lies within
    half_width of radius_px from centre."""
    want = [round(255 * c) for c in color[:3]]
    w, h = img.size
    px = img.load()
    hits = 0
    for i in range(720):
        a = 2 * math.pi * i / 720
        ca, sa = math.cos(a), math.sin(a)
        found = False
        for dr in range(-half_width, half_width + 1):
            x = round(centre[0] + (radius_px + dr) * ca)
            y = round(centre[1] + (radius_px + dr) * sa)
            if 0 <= x < w and 0 <= y < h:
                p = px[x, y]
                if all(abs(p[k] - want[k]) <= 60 for k in range(3)):
                    found = True
                    break
        hits += found
    return hits / 720


def main():
    ap = argparse.ArgumentParser(prog=PROG, add_help=False)
    ap.add_argument("--task")
    ap.add_argument("--seeds")
    ap.add_argument("--seeds-file")
    ap.add_argument("--settings", default=common.DEFAULT_SETTINGS)
    ap.add_argument("--worktree", default=common.REPO_ROOT)
    ap.add_argument("--mod", action="append", default=[])
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("-h", "--help", action="store_true")
    try:
        a = ap.parse_args()
    except SystemExit:
        sys.exit(2)
    if a.help:
        print(__doc__)
        return 0
    try:
        if not a.task or "/" in a.task or a.task.startswith("."):
            raise common.Usage("--task NAME is required (a plain name)")
        seeds = common.read_seeds(a.seeds, a.seeds_file)
        settings = common.load_settings(a.settings)
        sh = settings.get("shots")
        if not sh or not sh.get("rings") or not sh.get("daytimes"):
            raise common.Usage(f"{a.settings}: no shots.rings or shots.daytimes")
        for d in sh["daytimes"]:
            if not re.fullmatch(r"[A-Za-z0-9._-]+", str(d.get("name", ""))):
                raise common.Usage(f"{a.settings}: a daytime needs a plain name")
        if not any(d.get("check_rings", True) for d in sh["daytimes"]):
            raise common.Usage(f"{a.settings}: no daytime has its rings checked")
        side = math.floor(sh["view_tiles"] * 32 * sh["zoom"])
        if side >= MAX_SIDE:
            raise common.Usage(f"view_tiles * 32 * zoom = {side} px: must stay under {MAX_SIDE}")
    except (common.Usage, OSError, ValueError, KeyError) as e:
        common.die(PROG, str(e))

    scratch = tempfile.mkdtemp(prefix="sae-measure-rings.")
    try:
        mod = common.build_mod(scratch, {"mode": "rings", "settings": settings, "seeds": seeds})
        cmd = [LAUNCH, "--task", a.task, "--worktree", os.path.abspath(a.worktree), "--mod", mod]
        for m in a.mod:
            cmd += ["--mod", os.path.abspath(m)]
        cmd += ["--timeout", str(a.timeout), "--done-file", "sae-measure-seeds/done",
                "--", "--load-scenario", "base/freeplay"]
        p = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, check=False)
        sys.stderr.write(p.stderr)
    finally:
        shutil.rmtree(scratch)
    m = re.search(r" run dir: (\S+)", p.stderr)
    if not m:
        print(f"{PROG}: the client did not start (launcher exit {p.returncode})", file=sys.stderr)
        return 3 if p.returncode == 3 else 1
    run = m.group(1)
    out = os.path.join(run, "data", "script-output", "sae-measure-seeds")
    ok = p.returncode == 0
    if not ok:
        print(f"{PROG}: the launcher ended with exit {p.returncode}", file=sys.stderr)

    errors = os.path.join(out, "errors.txt")
    if os.path.exists(errors) and os.path.getsize(errors) > 0:
        ok = False
        with open(errors, encoding="utf-8") as f:
            print(f"{PROG}: the mod caught errors:\n" + f.read(), file=sys.stderr)
    done = os.path.join(out, "done")
    if not os.path.exists(done):
        ok = False
        print(f"{PROG}: no {done}", file=sys.stderr)

    zoom = sh["zoom"]
    report, lines = [], []
    for seed in seeds:
        measures = None
        mj = os.path.join(out, f"landing-{seed}.json")
        if os.path.exists(mj):
            with open(mj, encoding="utf-8") as f:
                measures = json.load(f)
        for d in sh["daytimes"]:
            path = os.path.join(out, f"landing-{seed}-{d['name']}.png")
            entry = {"seed": seed, "daytime": d["name"], "path": path}
            if not os.path.exists(path):
                ok = False
                entry["missing"] = True
                lines.append(f"{seed} {d['name']}: MISSING {path}")
                report.append(entry)
                continue
            with Image.open(path) as im:
                img = im.convert("RGB")
            w, h = img.size
            entry["size"] = [w, h]
            if max(w, h) >= MAX_SIDE:
                ok = False
            # The screenshot is centred on the landing.
            centre = (w / 2, h / 2)
            checked = d.get("check_rings", True)
            entry["rings_checked"] = checked
            shares = []
            for ring in sh["rings"]:
                r_px = ring["radius"] * 32 * zoom
                half = max(1, round(sh["ring_width"] * zoom / 2)) + 2
                s = ring_share(img, centre, r_px, ring["color"], half)
                shares.append({"radius": ring["radius"], "share": round(s, 3), "shows": s >= SHOW_SHARE})
                if s < SHOW_SHARE and checked:
                    ok = False
            entry["rings"] = shares
            if measures:
                entry["nearest_pool"] = measures["pool"]["nearest"]
                entry["pool_tiles_within"] = measures["pool"]["tiles_within"]
            report.append(entry)
            lines.append(f"{seed} {d['name']}: {w}x{h} px; " + ", ".join(
                f"ring {fmt(x['radius'])} on {x['share'] * 100:.0f}% of bearings" for x in shares)
                + ("" if checked else " (not checked)")
                + (f"; nearest pool {measures['pool']['nearest']:.1f}"
                   if measures and measures["pool"]["nearest"] else "")
                + f"\n    {path}")
    with open(os.path.join(run, "rings.json"), "w", encoding="utf-8") as f:
        json.dump({"seeds": seeds, "settings": settings, "images": report, "pass": ok}, f, indent=1)
    shows = all(x["shows"] for e in report if e.get("rings_checked") for x in e.get("rings", []))
    summary = (f"rings: {len(seeds)} seeds, {sum(1 for e in report if 'size' in e)} of "
               f"{len(seeds) * len(sh['daytimes'])} images; every ring shows on the checked ones: "
               f"{'yes' if shows else 'NO'} -> {'PASS' if ok else 'FAIL'}")
    with open(os.path.join(run, "rings.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines + ["", summary]) + "\n")
    print("\n".join(lines))
    print(summary)
    return 0 if ok else 1


def fmt(v):
    return str(int(v)) if float(v).is_integer() else str(v)


if __name__ == "__main__":
    sys.exit(main())
