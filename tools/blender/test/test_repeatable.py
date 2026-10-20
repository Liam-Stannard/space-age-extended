#!/usr/bin/env python3
"""A render repeated on the GPU passes the repeatability bar, and the bar fails a real change.

  BLENDER=<blender> python3 tools/blender/test/test_repeatable.py [--out <dir>] [--reuse]

The bar is Liam's (blender-pipeline-fixes T02, 2026-10-20, "GPU tolerance"), applied by
same_render.py (its docstring has it): sheets compared by their pixels in premultiplied colour,
every pixel within 3 levels, under 2 % of a sheet's visible pixels differing, alpha flips only
where the colour is 3 or less; meta.json equal but for the light stats (core/halo within 0.1,
peak within 1).

Renders, one at a time, through render.sh on the GPU (SAE_BLENDER_DEVICE=GPU): the test box
(test/box.py --ports --icon) twice and the radiant box (test/radiant_box.py) twice, into
<out>/box-1, box-2, radiant-1, radiant-2; each run's output in <out>/<run>.log. With --reuse a
run whose render.done already says "exit 0" is not rendered again (for the cases below on
runs already made). Everything is written under --out (default: a new directory under the
system's temporary one, named when it starts) and kept: <out>/<model>-pair.txt and .json, the
comparator's report on each pair, and <out>/fixtures/<case>/{a,b}, each case's two sides.

Exits 0 when every case below comes out as listed, 1 naming those that do not (2 with no
$BLENDER).

  render     each of the four runs: render.sh exits 0, render.done "exit 0", and it printed
             "render device: GPU ... on ..." (no CPU fallback).
  box        same_render.py box-1 box-2: PASS.
  radiant    same_render.py radiant-1 radiant-2: PASS.
Then cases made from the first run of each, its sheets copied to two sides a and b and one of
them changed, a sheet or meta.json; a FAIL must name that sheet (or meta.json) and the reason
listed, and nothing else:
  identical  a copy against itself: PASS.
  png-bytes  base-north re-saved with a "Date" text chunk and another compression: its bytes
             differ, its pixels do not -> PASS.
  colour-3   one opaque base-north pixel moved 3 levels -> PASS.
  colour-4   the same pixel moved 4 levels -> FAIL, base-north, colour 4 levels.
  share-1.9  1.9 % of base-north's visible pixels (rounded down) moved 1 level -> PASS.
  share-2    2 % of them (rounded up): not under 2 % -> FAIL, base-north, the share.
  share-3    3 % of them -> FAIL, base-north, the share.
  flips-t01  the radiant glow's flips as the study found them (T01: 1-26 a sheet on pixels of
             colour 0-3, GLOW_FLOOR's cut): 26 opaque column-glow-south pixels of colour 3 or
             less cleared to (0,0,0,0) -> PASS, the 26 counted as flips.
  flip-c3    a clear column-glow-south pixel opaque at (3,3,3) on one side -> PASS.
  flip-c6    one pixel (6,6,6) opaque on one side, at alpha 200 on the other (premultiplied
             colour 6 v 5, within the levels; alpha 55 apart) -> FAIL, column-glow-south,
             an alpha flip where the colour is over 3.
  core-0.1   radiant meta.json: checks/south/column-glow_light core +0.1 -> PASS.
  core-0.2   core +0.2 -> FAIL, meta.json, that core.
  halo-0.2   halo +0.2 -> FAIL, meta.json, that halo.
  peak-1     peak +1 -> PASS.
  peak-2     peak +2 -> FAIL, meta.json, that peak.
  shift      box meta.json: base-north's shift x + 1/128 -> FAIL, meta.json, that shift.
  note       box meta.json: a check's note reworded -> FAIL, meta.json, that note.
  missing    slider-east.png gone from b -> FAIL, slider-east "only in a".
  size       base-north a column narrower in b -> FAIL, base-north, its size.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, PngImagePlugin

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import same_render  # noqa: E402

FAILED = []
RUNS = (("box", "box.py", ("--ports", "--icon")), ("radiant", "radiant_box.py", ()))


def check(name, ok, detail=""):
    print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f": {detail}" if detail else ""))
    if not ok:
        FAILED.append(name)


def render(out, model, flags, reuse):
    """render.sh <model> <out> on the GPU; True when it ended "exit 0" on a GPU."""
    done = os.path.join(out, "render.done")
    log = out + ".log"
    if reuse and os.path.isfile(done) and os.path.isfile(log):
        with open(done) as f:
            if f.read().strip() == "exit 0":
                print(f"     {os.path.basename(out)}: reused")
                return True, log
    env = dict(os.environ, SAE_BLENDER_DEVICE="GPU")
    with open(log, "w") as f:
        rc = subprocess.run([os.path.join(TOOLS, "render.sh"), os.path.join(HERE, model), out, *flags],
                            stdout=f, stderr=subprocess.STDOUT, env=env).returncode
    with open(log) as f:
        text = f.read()
    gpu = any(ln.startswith("render device: GPU ") and " on " in ln for ln in text.splitlines())
    marker = "<none>"
    if os.path.isfile(done):
        with open(done) as f:
            marker = f.read().strip()
    ok = rc == 0 and marker == "exit 0" and gpu
    return ok, f"{log}: exit {rc}, render.done {marker!r}, GPU line {'found' if gpu else 'missing'}"


# ---- fixtures: two copies of a run's sheets, one changed --------------------------------

def sides(root, src):
    """<root>/a/sheets and <root>/b/sheets, copies of <src>/sheets."""
    if os.path.isdir(root):
        shutil.rmtree(root)
    for s in ("a", "b"):
        shutil.copytree(os.path.join(src, "sheets"), os.path.join(root, s, "sheets"))
    return os.path.join(root, "a"), os.path.join(root, "b")


def sheet(side, name):
    return os.path.join(side, "sheets", name)


def pixels(path):
    im = Image.open(path).convert("RGBA")
    return im, im.load()


def find(im, px, pred, n=1):
    """The first n (x, y) in raster order whose pixel satisfies pred."""
    out = []
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            if pred(px[x, y]):
                out.append((x, y))
                if len(out) == n:
                    return out
    return out


def nudge(path, at, levels):
    """Each opaque pixel at <at> moved <levels> on red (down where up would clip)."""
    im, px = pixels(path)
    for x, y in at:
        r, g, b, a = px[x, y]
        px[x, y] = (r + levels if r + levels <= 255 else r - levels, g, b, a)
    im.save(path)


def opaque(levels):
    """An opaque pixel: its premultiplied red moves as its red does."""
    return lambda p: p[3] == 255 and (p[0] + levels <= 255 or p[0] - levels >= 0)


def visible(path):
    im = Image.open(path).convert("RGBA")
    return im.size[0] * im.size[1] - im.getchannel("A").histogram()[0]


def edit_meta(side, fn):
    p = sheet(side, "meta.json")
    with open(p) as f:
        m = json.load(f)
    fn(m)
    with open(p, "w") as f:
        json.dump(m, f, indent=1)


def light(m):
    return m["checks"]["south"]["column-glow_light"][0]


def case(out, name, src, change, expect):
    """Make the case's sides, change them, compare. expect: None for PASS, else a list of
    (prefix, substring) every failure must match one of, each matched by one."""
    a, b = sides(os.path.join(out, "fixtures", name), src)
    info = change(a, b) or {}
    res = same_render.compare(a, b)
    with open(os.path.join(out, "fixtures", name, "report.txt"), "w") as f:
        f.write(same_render.report(res) + "\n")
    if expect is None:
        ok = res["pass"]
    else:
        ok = (not res["pass"]
              and all(any(f.startswith(p) and s in f for p, s in expect) for f in res["fail"])
              and all(any(f.startswith(p) and s in f for f in res["fail"]) for p, s in expect))
    for key, want in info.get("assert", []):
        got = key(res)
        if got != want:
            ok = False
            res["fail"].append(f"(test) expected {want!r}, got {got!r}")
    check(name, ok, "PASS" if res["pass"] else "FAIL: " + "; ".join(res["fail"]))
    return res


def img(res, rel):
    return res["stages"]["sheets"]["images"][rel]


def cases(out, box, radiant):
    base = "base-north.png"
    glow = "column-glow-south.png"
    base_vis = visible(sheet(box, base))

    def none(a, b):
        return None

    def png_bytes(a, b):
        p = sheet(b, base)
        info = PngImagePlugin.PngInfo()
        info.add_text("Date", "2026/10/20 12:00:00")
        Image.open(p).save(p, pnginfo=info, compress_level=1)
        with open(sheet(a, base), "rb") as fa, open(p, "rb") as fb:
            if fa.read() == fb.read():
                FAILED.append("png-bytes (bytes did not change)")

    def colour(levels):
        def change(a, b):
            im, px = pixels(sheet(b, base))
            at = find(im, px, opaque(levels))
            nudge(sheet(b, base), at, levels)
            return {"assert": [(lambda r: img(r, base)["worst_colour"], levels)]}
        return change

    def share(frac, rnd):
        n = rnd(frac * base_vis)

        def change(a, b):
            im, px = pixels(sheet(b, base))
            at = find(im, px, opaque(1), n)
            if len(at) < n:
                FAILED.append(f"share-{frac} (only {len(at)} opaque pixels)")
            nudge(sheet(b, base), at, 1)
            return {"assert": [(lambda r: img(r, base)["differ"], n)]}
        return change

    def flips_t01(a, b):
        im, px = pixels(sheet(b, glow))
        at = find(im, px, lambda p: p[3] == 255 and max(p[:3]) <= 3, 26)
        for xy in at:
            px[xy] = (0, 0, 0, 0)
        im.save(sheet(b, glow))
        return {"assert": [(lambda r: img(r, glow)["flips"], 26),
                           (lambda r: img(r, glow)["flip_colour_max"] <= 3, True)]}

    def flip(pa, pb):
        def change(a, b):
            im, px = pixels(sheet(a, glow))
            xy = find(im, px, lambda p: p[3] == 0)[0]
            for side, p in ((a, pa), (b, pb)):
                im, px = pixels(sheet(side, glow))
                px[xy] = p
                im.save(sheet(side, glow))
        return change

    def stat(key, by):
        def change(a, b):
            def f(m):
                s = light(m)
                s[key] = round(s[key] + by, 1) if isinstance(by, float) else s[key] + by
            edit_meta(b, f)
        return change

    def shift(a, b):
        def f(m):
            m["base-north"]["shift"][0] += 1 / 128
        edit_meta(b, f)

    def note(a, b):
        def f(m):
            c = m["checks"]["north"]["half_width_tiles"]
            c[1] = c[1] + " (reworded)"
        edit_meta(b, f)

    def missing(a, b):
        os.remove(sheet(b, "slider-east.png"))

    def size(a, b):
        im = Image.open(sheet(b, base))
        im.crop((0, 0, im.size[0] - 1, im.size[1])).save(sheet(b, base))

    sb = f"sheets/{base}: "
    sg = f"sheets/{glow}: "
    sm = "sheets/meta.json: "
    lp = "/checks/south/column-glow_light/0/"
    case(out, "identical", box, none, None)
    case(out, "png-bytes", box, png_bytes, None)
    case(out, "colour-3", box, colour(3), None)
    case(out, "colour-4", box, colour(4), [(sb, "colour 4 levels")])
    case(out, "share-1.9", box, share(0.019, math.floor), None)
    case(out, "share-2", box, share(0.02, math.ceil), [(sb, "% of visible pixels differ")])
    case(out, "share-3", box, share(0.03, math.ceil), [(sb, "% of visible pixels differ")])
    case(out, "flips-t01", radiant, flips_t01, None)
    case(out, "flip-c3", radiant, flip((0, 0, 0, 0), (3, 3, 3, 255)), None)
    case(out, "flip-c6", radiant, flip((6, 6, 6, 255), (6, 6, 6, 200)),
         [(sg, "1 alpha flip(s) where the colour is over 3")])
    case(out, "core-0.1", radiant, stat("core", 0.1), None)
    case(out, "core-0.2", radiant, stat("core", 0.2), [(sm + lp + "core", "")])
    case(out, "halo-0.2", radiant, stat("halo", 0.2), [(sm + lp + "halo", "")])
    case(out, "peak-1", radiant, stat("peak", 1), None)
    case(out, "peak-2", radiant, stat("peak", 2), [(sm + lp + "peak", "")])
    case(out, "shift", box, shift, [(sm + "/base-north/shift/0", "")])
    case(out, "note", box, note, [(sm + "/checks/north/half_width_tiles/1", "")])
    case(out, "missing", box, missing, [("sheets/slider-east.png: only in a", "")])
    case(out, "size", box, size, [(sb, "size ")])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", help="where everything is written (default: a new temporary directory)")
    ap.add_argument("--reuse", action="store_true", help="keep a run whose render.done says exit 0")
    args = ap.parse_args()
    if not os.environ.get("BLENDER"):
        print("test_repeatable.py: set BLENDER to a Blender 5 binary (blender.org's, for the GPU)",
              file=sys.stderr)
        return 2
    out = os.path.abspath(args.out) if args.out else tempfile.mkdtemp(prefix="sae-repeatable-")
    os.makedirs(out, exist_ok=True)
    print(f"out: {out}")
    rendered = {}
    for model, script, flags in RUNS:
        for k in (1, 2):
            run = os.path.join(out, f"{model}-{k}")
            ok, detail = render(run, script, flags, args.reuse)
            check(f"render {model}-{k}", ok, detail)
            rendered[run] = ok
    for model, _, _ in RUNS:
        a, b = os.path.join(out, f"{model}-1"), os.path.join(out, f"{model}-2")
        if not (rendered[a] and rendered[b]):
            check(model, False, "not compared: a render failed")
            continue
        res = same_render.compare(a, b)
        text = same_render.report(res)
        with open(os.path.join(out, f"{model}-pair.txt"), "w") as f:
            f.write(text + "\n")
        with open(os.path.join(out, f"{model}-pair.json"), "w") as f:
            json.dump(res, f, indent=1)
        print(text)
        check(model, res["pass"], f"{out}/{model}-pair.txt")
    box, radiant = os.path.join(out, "box-1"), os.path.join(out, "radiant-1")
    if rendered[box] and rendered[radiant]:
        cases(out, box, radiant)
    else:
        check("cases", False, "not run: a first render failed")
    print("PASS" if not FAILED else f"FAIL: {', '.join(FAILED)}")
    return 0 if not FAILED else 1


if __name__ == "__main__":
    sys.exit(main())
