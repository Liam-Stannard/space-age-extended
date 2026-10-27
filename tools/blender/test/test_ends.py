#!/usr/bin/env python3
"""runs.py's check (a run's ends and body, the ground) through measure.py's collide step, held to
test/ends_box.py's cases.

  python3 tools/blender/test/test_ends.py [--out <dir>] [--no-render]

Each case of ends_box.py (SAE_TEST_ENDS) is run as render.sh runs a model's --collide: measure.py's
collide(), with the Blender tools/paths.conf names. Everything is written under --out (default: a
new directory under the system's temporary one, named when it starts) and kept: <out>/<case>/
holds the case's collide.log. Exits 0 when every case below comes out as listed, 1 naming those
that do not, 2 when tools/paths.conf names no Blender.

  <case>       each case's lines after the box's own two (collide_box.py's), exactly: its
               LOOSE, UNTESTED, BODY and BELOW lines and below_ok line, its four counts (ends,
               untested, body, ground), one LOOSE line an end at most; and the verdict: PASS for
               fitted, ground-ok, into-ground and untagged, FAIL (exit 1 from render.sh) for every
               other. host-moves and shown-later: a fitting that moves off a fixed run and a part
               shown only after frame 0 are caught in the frames they happen; tee: a tee is let
               off only by the run it stands on; untestable: a run with nothing to test fails;
               unchecked: records never checked fail at exit ("runs not checked"), in a block of
               their own (unchecked-absorbed: an allowed pair line printed after the model's last
               count cannot answer for it); duplicate: a second run of one name raises.
  untagged     the COLLIDE lines are collide_box.py's own, byte for byte (ends_box.py calls
               nothing in runs.py): an untagged model prints nothing new.
  allowed      the loose case with --collide-allow naming its LOOSE line whole: PASS, one pair
               line allowed; the pattern with a frame list it does not print: FAIL.
  info         no information line (runs, below_ok, unrecorded tubes) names a pair or counts a
               clash, as measure.py reads them.
  render.sh    (skipped with --no-render) render.sh --collide on the loose case: exit 1,
               render.done "exit 1", nothing rendered; on the loose case allowed: it renders
               the box (exit 0).
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import measure  # noqa: E402
import paths  # noqa: E402

MODEL = os.path.join(HERE, "ends_box.py")
FAILED = []

BLOCK = "Cube.001[body] at (+0.00,+0.00,0.30)"       # the box's block
PLINTH = "Cube[body] at (+0.00,+0.00,0.04)"
# case -> (the pair lines, after "COLLIDE "; the counts (ends, body, ground); PASS)
CASES = {
    "fitted": ([], (0, 0, 0, 0), True),
    "loose": (["LOOSE hose end 1 at (+0.93,+0.30,0.45) x nothing: no fitting within 0.02, frames 0"],
              (1, 0, 0, 0), False),
    "short": (["LOOSE hose end 0 at (+0.91,-0.30,0.35) x nothing: no fitting within 0.02, frames 0"],
              (1, 0, 0, 0), False),
    "side": ([f"LOOSE hose end 0 at (+0.80,-0.60,0.35) x {BLOCK}: a bare end on it, no fitting within 0.02, "
              "frames 0"], (1, 0, 0, 0), False),
    "narrow": (["LOOSE hose end 0 at (+0.85,-0.30,0.35) x nozzle: fitting nozzle narrower than 0.9 of the run's "
                "0.060 across its end, frames 0"], (1, 0, 0, 0), False),
    "tangent": ([f"LOOSE hose end 1 at (+0.93,+0.30,0.12) x {PLINTH}: does not face into what it serves (the point "
                 "0.030 past its end is in nothing), frames 0"], (1, 0, 0, 0), False),
    "axis": ([f"LOOSE hose end 0 at (+0.85,-0.30,0.35) x {BLOCK}: arrives 45 deg off nozzle's axis (at most 30), "
              "frames 0"], (1, 0, 0, 0), False),
    "buried": ([f"LOOSE hose end 0 at (+0.60,-0.60,0.35) x {BLOCK}: buried in {BLOCK} (the point 0.060 back from "
                "its end is inside it), frames 0",
                f"BODY hose x {BLOCK}: 0.138 deep, frames 0"], (1, 0, 1, 0), False),
    "floating": (["LOOSE hose end 0 at (+0.92,-0.30,0.35) x nozzle: nozzle on no host (nothing within 0.02, not on "
                  "the ground), frames 0"], (1, 0, 0, 0), False),
    "body": (["BODY hose x rung[steel] at (+0.93,-0.15,0.32): 0.028 deep, frames 0"], (0, 0, 1, 0), False),
    "ground": (["BELOW post[steel] at (+1.30,-0.60,0.08) x ground: 0.050 deep, frames 0"], (0, 0, 0, 1), False),
    "ground-ok": ([], (0, 0, 0, 0), True),
    "ground-moving": (["BELOW plunger[steel] at (+1.30,+0.60,0.01) x ground: 0.020 deep, frames 2"], (0, 0, 0, 1),
                      False),
    "into-ground": ([], (0, 0, 0, 0), True),
    "host-moves": (["LOOSE hose end 0 at (+0.85,-0.30,0.35) x nothing: no fitting within 0.02, frames 1-3"],
                   (1, 0, 0, 0), False),
    "shown-later": (["BELOW post[steel] at (+1.30,-0.60,-0.03) x ground: 0.150 deep, frames 1-3"], (0, 0, 0, 1), False),
    "tee": (["BODY branch x stub[steel] at (+0.93,-0.15,0.38): 0.022 deep, frames 0"], (0, 0, 1, 0), False),
    "untestable": (["UNTESTED wire x nothing: no part of it shown with polygons in any frame (hidden, a curve with no "
                    "bevel, or no faces)"], (0, 1, 0, 0), False),
    "unchecked": ([], None, False),
    "unchecked-absorbed": (["meant slider x roof: frames [0]"], None, False),
    "duplicate": ([], None, False),
    "untagged": ([], None, True),
}
UNCHECKED = "COLLIDE runs not checked: 2 clashes (2 records made after the last runs.check, or with none called)"
FOLLOW = "COLLIDE runs not checked follow: 0 clashes"           # the line closing the block before it
DUPLICATE = "run 'hose': a run of that name is already recorded; run names must be unique"
BELOW_OK = "COLLIDE below_ok post[steel] at (+1.30,-0.60,0.08): 0.050 deep  (a footing poured into the ground)"
BOX_LINES = ["COLLIDE parts 7, slider frames 4", "COLLIDE clashes 0"]       # collide_box.py's


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + ("" if ok else f": {detail}"))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def collide(out, case, blender, allow=(), model=MODEL):
    os.environ["SAE_TEST_ENDS"] = case
    try:
        return measure.collide(model, os.path.join(out, case), blender, allow=allow)
    finally:
        os.environ.pop("SAE_TEST_ENDS", None)


def counts(lines):
    """ends, untested, body, ground: the four count lines' numbers."""
    got = {}
    for ln in lines:
        for kind in ("ends", "untested", "body", "ground"):
            if ln.startswith(f"COLLIDE {kind}: "):
                got[kind] = int(ln.split()[2])
    return tuple(got.get(k) for k in ("ends", "untested", "body", "ground")) if got else None


def test_cases(out, blender):
    print("cases (measure.py's collide step on ends_box.py)")
    for case, (pairs, cnt, ok) in CASES.items():
        res = collide(out, case, blender)
        lines = res["lines"]
        check(f"{case}: the box's own two lines first", lines[:2] == BOX_LINES, lines[:2])
        mine = [ln[len("COLLIDE "):] for ln in res["clash_lines"] if ln not in BOX_LINES]
        check(f"{case}: its pair lines", mine == pairs, f"got {mine}")
        check(f"{case}: its counts (ends, untested, body, ground) {cnt}", counts(lines) == cnt, f"got {counts(lines)}")
        ends = [tuple(ln.split()[2:5]) for ln in lines if ln.startswith("COLLIDE LOOSE ")]
        check(f"{case}: one LOOSE line an end", len(ends) == len(set(ends)), ends)
        check(f"{case}: {'PASS' if ok else 'FAIL'}", res["pass"] is ok, res["why"])
        if case == "ground-ok":
            check("ground-ok: the below_ok line", BELOW_OK in lines, [ln for ln in lines if "below_ok" in ln])
        if case == "unchecked":
            check("unchecked: the exit lines, a 0 count closing the block and then the clash count, and nothing "
                  "of runs.check's", lines[-2:] == [FOLLOW, UNCHECKED]
                  and not any(ln.startswith("COLLIDE runs:") for ln in lines), lines)
        if case == "unchecked-absorbed":
            allowed = collide(out, case, blender, allow=[r"meant slider x roof: frames \[0\]"])
            check("unchecked-absorbed, its pair line allowed: still FAIL (runs not checked: 1 clashes, its block 0 "
                  "allowed)", not allowed["pass"] and len(allowed["allowed"]) == 1
                  and "'COLLIDE runs not checked: 1 clashes" in (allowed["why"] or ""), allowed["why"])
        if case == "duplicate":
            text = open(res["log"]).read()
            check("duplicate: runs.run raises naming the run (a Traceback in the log)",
                  DUPLICATE in text and "Traceback" in (res["why"] or ""), res["why"])
        if case == "untagged":
            box = measure.collide(os.path.join(HERE, "collide_box.py"), os.path.join(out, "collide_box"), blender)
            check("untagged: its COLLIDE lines are collide_box.py's, byte for byte", lines == box["lines"],
                  f"{lines} / {box['lines']}")
        info = [ln for ln in lines if ln.startswith(("COLLIDE runs:", "COLLIDE below_ok", "COLLIDE unrecorded"))]
        bad = [ln for ln in info if measure.names_pair(measure.collide_text(ln)) or measure.COLLIDE_COUNT.search(ln)]
        check(f"{case}: info lines name no pair and count nothing", not bad, bad)


def test_allowed(out, blender):
    print("allowed (--collide-allow on a LOOSE line)")
    line = CASES["loose"][0][0]
    pattern = re.escape(line)
    res = collide(out, "loose", blender, allow=[pattern])
    check("loose, its LOOSE line allowed whole: PASS, 1 allowed", res["pass"] and len(res["allowed"]) == 1,
          res["why"])
    res = collide(out, "loose", blender, allow=[re.escape(line.replace("frames 0", "frames 1"))])
    check("loose, a pattern for frames it does not print: FAIL", not res["pass"], res["why"])


def test_render_sh(out):
    print("render.sh --collide (the GPU Blender tools/paths.conf names)")
    render_sh = os.path.join(TOOLS, "render.sh")
    line = CASES["loose"][0][0]
    for name, allow, code_want in (("loose", [], 1), ("loose-allowed", ["--collide-allow", re.escape(line)], 0)):
        o = os.path.join(out, "render-" + name)
        env = dict(os.environ, SAE_TEST_ENDS="loose")
        p = subprocess.run(["bash", render_sh, MODEL, o, "--collide", *allow], env=env, capture_output=True, text=True)
        done = open(os.path.join(o, "render.done")).read().strip() if os.path.isfile(os.path.join(o, "render.done")) \
            else None
        rendered = os.path.isdir(os.path.join(o, "sheets"))
        check(f"render.sh {name}: exit {code_want}, render.done 'exit {code_want}', "
              + ("nothing rendered" if code_want else "the box rendered"),
              p.returncode == code_want and done == f"exit {code_want}" and rendered == (code_want == 0),
              f"exit {p.returncode}, done {done!r}, rendered {rendered}: {(p.stdout + p.stderr)[-500:]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out")
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    try:
        blender = paths.blender()
    except paths.PathsError as e:
        print(e, file=sys.stderr)
        return 2
    out = a.out or tempfile.mkdtemp(prefix="test-ends-")
    if os.path.isdir(out):
        for c in list(CASES) + ["collide_box", "render-loose", "render-loose-allowed"]:
            shutil.rmtree(os.path.join(out, c), ignore_errors=True)
    os.makedirs(out, exist_ok=True)
    print(f"out: {out}")
    test_cases(out, blender)
    test_allowed(out, blender)
    if not a.no_render:
        test_render_sh(out)
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
