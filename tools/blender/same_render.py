#!/usr/bin/env python3
"""Two render.sh runs of one model, held to the repeatability bar: the same render or not.

  python3 tools/blender/same_render.py <out-a> <out-b> [--renders] [--json <file>]

<out-a> and <out-b> are render.sh <out-dir>s of one model on one device, packed with the same
rolloff setting (render.json's "rolloff", contract.py): pack.py rolls highlights off by default
since T07, so a fresh render held against sheets packed before T07 needs "rolloff": false on
the fresh side. A GPU render is not the same twice to the bit (the determinism study,
blender-pipeline-fixes T01: the order the GPU sums a pixel's samples in moves a value at a
rounding edge one level; an emissive mesh lit as a light moves the glows up to 3 levels, on
either device), so "the same" is a bar, Liam's (T02, 2026-10-20, "GPU tolerance"), and this
applies exactly it:

  sheets   every PNG under sheets/ (ports/, masters/ and icon.png too), compared by its
           pixels, never its bytes, in premultiplied colour (each of R, G, B times alpha / 255,
           rounded half up; alpha as it is). Per sheet:
             - the same file names on both sides, and each sheet the same size;
             - every pixel within LEVELS (3) levels, on every channel;
             - but an alpha flip -- alpha moved more than LEVELS -- passes where the pixel's
               premultiplied colour is FLIP_COLOUR (3) or less on both sides (the glows' faint
               edge, cut at pack.py's GLOW_FLOOR one run and kept the next);
             - under SHARE (2 %) of the sheet's visible pixels (alpha above 0 on either side)
               differing at all.
  meta     every .json under sheets/ (meta.json, ports/meta.json) equal, key for key and value
           for value (-0.0 equal to 0.0), but for its light stats -- a dict of exactly peak,
           core and halo, pack.py's light_stats(), the <glow>_light checks -- whose core and
           halo (%) may differ by up to CORE_HALO (0.1) and peak by up to PEAK (1); and for
           its roll-off counts -- checks/<direction>/rolloff_px/0/<sheet>, a dict of exactly px
           and most, pack.py's rolloff() -- whose px (pixels rolled) and most (levels a channel
           moved) may each differ by 1 % of the larger count, or by 1, whichever is more
           (Liam, blender-pipeline-fixes T11b, 2026-10-20: "Within 1 %", "1 % or 1 px", most
           "1 % or 1 level"; a level at the roll-off's knee moves a pixel in or out of it).
           Any other count under checks (cut_px among them) must be equal.
  other    any other file under sheets/: the same bytes.

With --renders, every PNG under renders/ is held to the sheets' bar as well (renders/ is
what the sheets are packed from; it carries no shift or meta of its own). hi/ is never
compared: its PNGs carry the render's date and times, and hi/ is not shipped.

Prints a line a sheet -- its size, visible pixels, pixels differing and their share, the
worst premultiplied colour and alpha levels, the alpha flips and the brightest colour any of
them had -- then each meta difference, allowed or not, then PASS or FAIL with what failed.
--json writes the same as data (compare()'s result). Exits 0 on PASS, 1 on FAIL, 2 when an
<out-dir> has no sheets/ (or no renders/, with --renders).
"""
import argparse
import json
import os
import re
import sys

from PIL import Image, ImageChops

LEVELS = 3          # every premultiplied channel within this many levels
FLIP_COLOUR = 3     # an alpha flip passes where the premultiplied colour is at most this
SHARE = 0.02        # under this share of a sheet's visible pixels may differ at all
CORE_HALO = 0.1     # light stats: core and halo % within this
PEAK = 1            # light stats: peak luminance within this
LIGHT_KEYS = frozenset(("peak", "core", "halo"))
ROLL_SHARE = 0.01   # roll-off counts: px and most within this share of the larger count ...
ROLL_FLOOR = 1      # ... or within this, whichever is more
ROLL_KEYS = frozenset(("px", "most"))
ROLL_PATH = re.compile(r"^/checks/[^/]+/rolloff_px/0/[^/]+$")
EPS = 1e-6          # for the float sums a stat's rounding leaves (5.8 + 0.1)


class Usage(Exception):
    pass


def premul(px):
    """(r, g, b, a) straight -> premultiplied, each colour channel rounded half up."""
    r, g, b, a = px
    return ((2 * r * a + 255) // 510, (2 * g * a + 255) // 510, (2 * b * a + 255) // 510, a)


def compare_image(pa, pb):
    """One image pair against the bar: a dict of its figures and its failures ("fail")."""
    a, b = Image.open(pa).convert("RGBA"), Image.open(pb).convert("RGBA")
    res = dict(size=list(a.size), fail=[])
    if a.size != b.size:
        res["size_b"] = list(b.size)
        res["fail"].append(f"size {a.size[0]}x{a.size[1]} v {b.size[0]}x{b.size[1]}")
        return res
    alpha = ImageChops.lighter(a.getchannel("A"), b.getchannel("A"))
    visible = a.size[0] * a.size[1] - alpha.histogram()[0]
    res.update(visible=visible, differ=0, share=0.0, worst_colour=0, worst_alpha=0,
               flips=0, flip_colour_max=0, over_levels=0, bad_flips=0)
    da, db = a.tobytes(), b.tobytes()
    if da == db:
        return res
    diff = ImageChops.difference(a, b).split()
    m = diff[0]
    for c in diff[1:]:
        m = ImageChops.lighter(m, c)
    w = a.size[0]
    first = None
    for i, v in enumerate(m.tobytes()):
        if not v:
            continue
        qa, qb = premul(da[4 * i:4 * i + 4]), premul(db[4 * i:4 * i + 4])
        if qa == qb:
            continue                       # straight colour under alpha 0: not a difference
        res["differ"] += 1
        dc = max(abs(x - y) for x, y in zip(qa[:3], qb[:3]))
        dal = abs(qa[3] - qb[3])
        res["worst_colour"] = max(res["worst_colour"], dc)
        colour = max(qa[:3] + qb[:3])
        if dal > LEVELS:
            res["flips"] += 1
            res["flip_colour_max"] = max(res["flip_colour_max"], colour)
            if colour > FLIP_COLOUR:
                res["bad_flips"] += 1
        else:
            res["worst_alpha"] = max(res["worst_alpha"], dal)
        if dc > LEVELS or (dal > LEVELS and colour > FLIP_COLOUR):
            res["over_levels"] += 1
            if first is None:
                first = (i % w, i // w, tuple(da[4 * i:4 * i + 4]), tuple(db[4 * i:4 * i + 4]))
    res["share"] = res["differ"] / visible if visible else 0.0
    if res["worst_colour"] > LEVELS:
        res["fail"].append(f"colour {res['worst_colour']} levels (over {LEVELS})")
    if res["bad_flips"]:
        res["fail"].append(f"{res['bad_flips']} alpha flip(s) where the colour is over {FLIP_COLOUR}"
                           f" (brightest {res['flip_colour_max']})")
    if res["share"] >= SHARE:
        res["fail"].append(f"{100 * res['share']:.2f} % of visible pixels differ (bar: under {100 * SHARE:g} %)")
    if first is not None:
        res["first_over"] = dict(xy=first[:2], a=first[2], b=first[3])
    return res


def files_under(root):
    out = set()
    for dp, _, fs in os.walk(root):
        for f in fs:
            out.add(os.path.relpath(os.path.join(dp, f), root))
    return out


def is_light(o):
    return isinstance(o, dict) and set(o) == LIGHT_KEYS


def is_roll(o, path):
    return isinstance(o, dict) and set(o) == ROLL_KEYS and bool(ROLL_PATH.match(path))


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def roll_ok(x, y):
    """Two roll-off counts within ROLL_SHARE of the larger, or within ROLL_FLOOR."""
    return abs(x - y) <= max(ROLL_FLOOR, ROLL_SHARE * max(abs(x), abs(y))) + EPS


def compare_json(a, b, path=""):
    """Every difference between two JSON values: (path, a, b, allowed, rule) a leaf, rule the
    tolerance that allowed it ("light stat", "rolloff count") or None."""
    if is_light(a) and is_light(b):
        out = []
        for k, tol in (("peak", PEAK), ("core", CORE_HALO), ("halo", CORE_HALO)):
            x, y = a[k], b[k]
            if x != y:
                ok = is_num(x) and is_num(y) and abs(x - y) <= tol + EPS
                out.append((f"{path}/{k}", x, y, ok, "light stat" if ok else None))
        return out
    if is_roll(a, path) and is_roll(b, path):
        out = []
        for k in ("px", "most"):
            x, y = a[k], b[k]
            if x != y:
                ok = is_num(x) and is_num(y) and roll_ok(x, y)
                out.append((f"{path}/{k}", x, y, ok, "rolloff count" if ok else None))
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append((f"{path}/{k}", a.get(k, "<absent>"), b.get(k, "<absent>"), False, None))
            else:
                out += compare_json(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [(path, f"<{len(a)} items>", f"<{len(b)} items>", False, None)]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += compare_json(x, y, f"{path}/{i}")
        return out
    if a == b and isinstance(a, bool) == isinstance(b, bool) and isinstance(a, str) == isinstance(b, str):
        return []
    return [(path, a, b, False, None)]


def compare_stage(da, db):
    """Every file of two stage directories: per image, per JSON, per other file."""
    fa, fb = files_under(da), files_under(db)
    res = dict(only_a=sorted(fa - fb), only_b=sorted(fb - fa), images={}, json={}, other={})
    for rel in sorted(fa & fb):
        pa, pb = os.path.join(da, rel), os.path.join(db, rel)
        if rel.endswith(".png"):
            res["images"][rel] = compare_image(pa, pb)
        elif rel.endswith(".json"):
            with open(pa) as f:
                ja = json.load(f)
            with open(pb) as f:
                jb = json.load(f)
            res["json"][rel] = [dict(path=p, a=x, b=y, allowed=ok, rule=rule)
                                for p, x, y, ok, rule in compare_json(ja, jb)]
        else:
            with open(pa, "rb") as f:
                ba = f.read()
            with open(pb, "rb") as f:
                bb = f.read()
            res["other"][rel] = ba == bb
    return res


def compare(out_a, out_b, renders=False):
    """Two render.sh <out-dir>s against the bar: {"pass": bool, "fail": [...], stage: {...}}."""
    stages = ["sheets"] + (["renders"] if renders else [])
    res = dict(a=os.path.abspath(out_a), b=os.path.abspath(out_b), stages={}, fail=[])
    for st in stages:
        for out in (out_a, out_b):
            if not os.path.isdir(os.path.join(out, st)):
                raise Usage(f"{out} has no {st}/")
    for st in stages:
        r = compare_stage(os.path.join(out_a, st), os.path.join(out_b, st))
        res["stages"][st] = r
        for rel in r["only_a"]:
            res["fail"].append(f"{st}/{rel}: only in a")
        for rel in r["only_b"]:
            res["fail"].append(f"{st}/{rel}: only in b")
        for rel, ir in r["images"].items():
            for why in ir["fail"]:
                res["fail"].append(f"{st}/{rel}: {why}")
        for rel, diffs in r["json"].items():
            for d in diffs:
                if not d["allowed"]:
                    res["fail"].append(f"{st}/{rel}: {d['path']} {d['a']!r} v {d['b']!r}")
        for rel, same in r["other"].items():
            if not same:
                res["fail"].append(f"{st}/{rel}: bytes differ")
    res["pass"] = not res["fail"]
    return res


def report(res):
    """compare()'s result as text, a line a sheet."""
    lines = [f"a {res['a']}", f"b {res['b']}",
             f"bar: premultiplied, every px within {LEVELS} levels; under {100 * SHARE:g} % of visible px "
             f"differ; alpha flips only where colour <= {FLIP_COLOUR}; light stats core/halo within "
             f"{CORE_HALO}, peak within {PEAK}; rolloff_px px and most within {100 * ROLL_SHARE:g} % of the "
             f"larger or {ROLL_FLOOR}"]
    for st, r in res["stages"].items():
        lines.append(f"[{st}]")
        lines.append(f"  {'image':34s} {'size':>9s} {'visible':>8s} {'differ':>7s} {'share':>7s} "
                     f"{'colour':>6s} {'alpha':>5s} {'flips':>5s} {'flipc':>5s}  verdict")
        for rel, ir in r["images"].items():
            size = f"{ir['size'][0]}x{ir['size'][1]}"
            if "visible" not in ir:
                lines.append(f"  {rel:34s} {size:>9s}  FAIL: {'; '.join(ir['fail'])}")
                continue
            verdict = "FAIL: " + "; ".join(ir["fail"]) if ir["fail"] else "ok"
            lines.append(f"  {rel:34s} {size:>9s} {ir['visible']:8d} {ir['differ']:7d} "
                         f"{100 * ir['share']:6.2f}% {ir['worst_colour']:6d} {ir['worst_alpha']:5d} "
                         f"{ir['flips']:5d} {ir['flip_colour_max']:5d}  {verdict}")
            if "first_over" in ir:
                fo = ir["first_over"]
                lines.append(f"    first pixel over the bar at {tuple(fo['xy'])}: {fo['a']} v {fo['b']} (straight)")
        for rel in r["only_a"]:
            lines.append(f"  {rel}: only in a")
        for rel in r["only_b"]:
            lines.append(f"  {rel}: only in b")
        for rel, diffs in r["json"].items():
            lines.append(f"  {rel}: " + (f"{len(diffs)} difference(s)" if diffs else "equal"))
            for d in diffs:
                lines.append(f"    {d['path']}: {d['a']!r} v {d['b']!r}  "
                             + (f"allowed ({d['rule']})" if d["allowed"] else "FAIL"))
        for rel, same in r["other"].items():
            lines.append(f"  {rel}: " + ("same bytes" if same else "FAIL: bytes differ"))
    lines.append("PASS" if res["pass"] else f"FAIL ({len(res['fail'])}):")
    lines += [f"  {f}" for f in res["fail"]]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out_a")
    ap.add_argument("out_b")
    ap.add_argument("--renders", action="store_true", help="hold renders/ to the bar as well")
    ap.add_argument("--json", help="write the result here as JSON")
    args = ap.parse_args()
    try:
        res = compare(args.out_a, args.out_b, renders=args.renders)
    except Usage as e:
        print(f"same_render.py: {e}", file=sys.stderr)
        return 2
    print(report(res))
    if args.json:
        with open(args.json, "w") as f:
            json.dump(res, f, indent=1)
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
