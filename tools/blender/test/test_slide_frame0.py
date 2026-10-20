#!/usr/bin/env python3
"""pack.py's slide check, measured from frame 0 (the still), held to its docs.

  python3 tools/blender/test/test_slide_frame0.py <box-out> [--baseline <git-rev>] [--out <dir>]

<box-out> is render.sh's <out-dir> for the test box (test/box.py), whose slider slides 0, 4, 12
and 28 px east in four frames. Nothing is rendered here: copies of its renders, one slider frame
moved by a fraction of a pixel (bilinear, so its centroid moves by as much), are packed by
pack.py. --baseline names a commit from before the check measured from frame 0 (23c85a2): its
contract.py and pack.py, taken out with `git show`, are run beside this tree's. Everything is
written under --out (default <box-out>/slide-test) and kept.

Exits 0 when every case below comes out as listed, 1 naming those that do not.

  exact      Packer.slide on centroids put on the box's declared path (north), nothing pack.py
             rendered: as declared -> off 0, frames_over []; frame 2 1.2 px along the line ->
             off_curve 1.2, frames_over [2], where the old mean fit made it 0.9; 1.0 px -> passes
             (within 1); 1.01 px -> frames_over [2]; frame 1 1.2 px across -> off_line 1.2,
             frames_over [1]; frame 0 1.2 px along -> frames_over [1, 2, 3] (frame 0 is the
             reference: the rest are off from it), measured [0, ...] all the same.
  as is      the box's renders: pack.py exits 0; in every direction slider_path_px has
             frames_over [], off_curve and off_line within 1, and measured[0] 0.
  moved      slider-02-north.png moved 1.2 px along the line: pack.py exits 1, naming
             direction north and frame 2 (slider-02-north.png) and no other direction or frame;
             meta.json written, north's frames_over [2] and off_curve 1.1-1.3, the other
             directions' []. slider-01-east.png moved 1.2 px across: exits 1 naming frame 1
             (slider-01-east.png), off_line 1.1-1.3. slider-02-north.png moved 0.8 px: exits 0.
  tracked    the slider declared as tracking a part "slider", its renders copied as the
             tracked part's (slider-slider-NN-<d>.png): as they are, exits 0 and slider_path_px
             is the untracked one's plus tracked "slider"; the tracked frame 2 north moved 1.2
             px (the packed frame left alone): exits 1 naming slider-slider-02-north.png.
  baseline   with --baseline: the old pack.py passes the 1.2 px move along (the bug: the mean
             fit shares the miss, ~0.9 px); on the box as is, this tree's sheets byte for byte
             as the baseline's, and meta.json equal, every key in order, but for slider_path_px
             -- both packing a copy whose render.json says rolloff false, as pack.py rolls the
             highlights of every sheet but a shadow's or a light's off by default since T07 and
             the baseline does not (test_rolloff.py holds the roll-off). A glow pass's sheets,
             and their size and shift in meta.json, are set aside (each in both, or it fails):
             T06 crops a still glow to the box holding pack.LIGHT_SHARE of its light, which the
             baseline does not (test_glow_crop.py holds the crop).
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import contract  # noqa: E402
import pack  # noqa: E402

FAILED = []
ANIM = "slider"


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def load_decl(rdir):
    with open(os.path.join(rdir, contract.FILE)) as f:
        return json.load(f)


def packed(src, out, tools=TOOLS):
    """pack.py (tools') src -> out: its exit code, output and meta.json (None if it wrote none)."""
    if os.path.exists(out):
        shutil.rmtree(out)
    code, text = run([sys.executable, os.path.join(tools, "pack.py"), src, out])
    meta = os.path.join(out, "meta.json")
    return code, text, (json.load(open(meta)) if os.path.isfile(meta) else None)


def path_of(meta, d):
    return meta["checks"][d][f"{ANIM}_path_px"]


def anim_of(decl):
    return next(a for a in decl["animations"] if a["name"] == ANIM)


def line_px(decl, d):
    """The unit vector along the slider's line on the screen in direction d, and across it."""
    want = [contract.screen(decl, p, d) for p in anim_of(decl)["path"]]
    fx, fy = want[-1][0] - want[0][0], want[-1][1] - want[0][1]
    n = math.hypot(fx, fy)
    return (fx / n, fy / n), (-fy / n, fx / n)


def moved(rdir, stem, by):
    """Move one render by `by` (px, x right, y down), bilinear, in place."""
    p = os.path.join(rdir, stem + ".png")
    im = Image.open(p).convert("RGBA")
    im.transform(im.size, Image.Transform.AFFINE, (1, 0, -by[0], 0, 1, -by[1]),
                 resample=Image.Resampling.BILINEAR).save(p)


def copy(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return dst


def named_frames(text, d):
    """The frames pack.py's slide failure names for direction d."""
    lines = [ln for ln in text.splitlines() if f"animation {ANIM!r}, direction {d}:" in ln]
    return [int(f) for ln in lines for f in re.findall(r"\b(\d+) \(\S+\.png\)", ln)]


# ---------------------------------------------------------------- exact

def test_exact(decl):
    print("exact")
    a = anim_of(decl)
    want = [contract.screen(decl, p, "north") for p in a["path"]]
    (ux, uy), (vx, vy) = line_px(decl, "north")
    packer = object.__new__(pack.Packer)
    packer.decl = decl
    off = (96.3, 71.8)          # where the centroid sits from the point the path follows: any fixed offset

    def cs(frame=None, along=0.0, across=0.0):
        out = [(w[0] + off[0], w[1] + off[1]) for w in want]
        if frame is not None:
            x, y = out[frame]
            out[frame] = (x + along * ux + across * vx, y + along * uy + across * vy)
        return out

    p = packer.slide(a, cs(), "north")
    check("as declared: off 0 and 0, frames_over []", (p["off_curve"], p["off_line"], p["frames_over"]) == (0, 0, []),
          str(p))
    check("as declared: measured is declared", p["measured"] == p["declared"], str(p))
    p = packer.slide(a, cs(2, 1.2), "north")
    n = len(want)
    check("frame 2 1.2 px along: off_curve 1.2, frames_over [2]", (p["off_curve"], p["frames_over"]) == (1.2, [2]),
          str(p))
    check(f"  where the old mean fit made it {round(1.2 * (n - 1) / n, 2)} (passing)", 1.2 * (n - 1) / n <= 1.0)
    p = packer.slide(a, cs(2, 1.0), "north")
    check("frame 2 1.0 px along: passes (within 1)", p["frames_over"] == [] and p["off_curve"] == 1.0, str(p))
    p = packer.slide(a, cs(2, 1.01), "north")
    check("frame 2 1.01 px along: frames_over [2]", p["frames_over"] == [2], str(p))
    p = packer.slide(a, cs(1, 0.0, 1.2), "north")
    check("frame 1 1.2 px across: off_line 1.2, off_curve 0, frames_over [1]",
          (p["off_line"], p["off_curve"], p["frames_over"]) == (1.2, 0, [1]), str(p))
    p = packer.slide(a, cs(0, 1.2), "north")
    check("frame 0 1.2 px along: frames_over [1, 2, 3] (frame 0 is the reference)",
          p["frames_over"] == [1, 2, 3] and p["measured"][0] == 0, str(p))


# ---------------------------------------------------------------- the box's renders

def test_as_is(rdir, out):
    print("as is")
    code, text, meta = packed(rdir, os.path.join(out, "as-is"))
    check("pack.py exits 0", code == 0, text[-400:])
    if meta is None:
        return
    for d, _ in contract.DIRECTIONS[load_decl(rdir)["directions"]]:
        p = path_of(meta, d)
        check(f"{d}: frames_over [], off {p['off_curve']} / {p['off_line']} within 1, measured[0] 0",
              p["frames_over"] == [] and max(p["off_curve"], p["off_line"]) <= 1 and p["measured"][0] == 0, str(p))


def test_moved(rdir, out, decl):
    print("moved")
    dirs = [d for d, _ in contract.DIRECTIONS[decl["directions"]]]
    cases = (("north", 2, 1.2, 0.0, True), ("east", 1, 0.0, 1.2, True), ("north", 2, 0.8, 0.0, False))
    for d, f, along, across, fails in cases:
        (ux, uy), (vx, vy) = line_px(decl, d)
        label = f"{contract.frame(ANIM, f, d)}.png {along or across} px {'along' if along else 'across'}"
        src = copy(rdir, os.path.join(out, f"moved-{d}-{f}-{along}-{across}-renders"))
        moved(src, contract.frame(ANIM, f, d), (along * ux + across * vx, along * uy + across * vy))
        code, text, meta = packed(src, os.path.join(out, f"moved-{d}-{f}-{along}-{across}"))
        if not fails:
            check(f"{label}: exits 0", code == 0, text[-400:])
            continue
        check(f"{label}: exits 1", code == 1, f"exit {code}")
        check(f"{label}: names frame {f} ({contract.frame(ANIM, f, d)}.png) in {d}",
              f"{f} ({contract.frame(ANIM, f, d)}.png)" in text and named_frames(text, d) == [f],
              text[-600:])
        check(f"{label}: names no other direction",
              all(not named_frames(text, o) for o in dirs if o != d), text[-600:])
        if meta is None:
            check(f"{label}: meta.json written", False)
            continue
        p = path_of(meta, d)
        off = p["off_curve"] if along else p["off_line"]
        check(f"{label}: meta.json frames_over [{f}], off {off} in 1.1-1.3",
              p["frames_over"] == [f] and 1.1 <= off <= 1.3, str(p))
        check(f"{label}: the other directions' frames_over []",
              all(path_of(meta, o)["frames_over"] == [] for o in dirs if o != d))


def test_tracked(rdir, out, decl):
    print("tracked")
    src = copy(rdir, os.path.join(out, "tracked-renders"))
    t = json.loads(json.dumps(decl))
    anim_of(t)["track"] = ANIM
    with open(os.path.join(src, contract.FILE), "w") as fh:
        json.dump(t, fh, indent=1)
    for d, _ in contract.DIRECTIONS[decl["directions"]]:
        for f in range(int(anim_of(decl)["frames"])):
            shutil.copy(os.path.join(src, contract.frame(ANIM, f, d) + ".png"),
                        os.path.join(src, contract.track_frame(ANIM, ANIM, f, d) + ".png"))
    code, text, meta = packed(src, os.path.join(out, "tracked"))
    _, _, plain = packed(rdir, os.path.join(out, "untracked"))
    check("as they are: exits 0", code == 0, text[-400:])
    if meta and plain:
        p = path_of(meta, "north")
        q = dict(path_of(plain, "north"), tracked=ANIM)
        check("slider_path_px the untracked one's plus tracked", p == q, f"{p} vs {q}")
    (ux, uy), _ = line_px(decl, "north")
    moved(src, contract.track_frame(ANIM, ANIM, 2, "north"), (1.2 * ux, 1.2 * uy))
    code, text, meta = packed(src, os.path.join(out, "tracked-moved"))
    stem = contract.track_frame(ANIM, ANIM, 2, "north")
    check(f"tracked frame 2 north 1.2 px along: exits 1 naming {stem}.png",
          code == 1 and f"2 ({stem}.png)" in text and named_frames(text, "north") == [2],
          f"exit {code}: {text[-600:]}")


# ---------------------------------------------------------------- baseline

def baseline_tools(rev, out):
    """contract.py and pack.py as they stood at rev, in a directory of their own."""
    d = os.path.join(out, f"baseline-{rev}")
    os.makedirs(d, exist_ok=True)
    top = subprocess.run(["git", "-C", TOOLS, "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                         check=True).stdout.strip()
    rel = os.path.relpath(TOOLS, top)
    for f in ("contract.py", "pack.py"):
        body = subprocess.run(["git", "-C", top, "show", f"{rev}:{rel}/{f}"], capture_output=True, check=True).stdout
        with open(os.path.join(d, f), "wb") as fh:
            fh.write(body)
    return d


def test_baseline(rdir, out, rev):
    print(f"baseline {rev}")
    base = baseline_tools(rev, out)
    code, text, meta = packed(os.path.join(out, "moved-north-2-1.2-0.0-renders"), os.path.join(out, "base-moved"),
                              base)
    old = path_of(meta, "north")["off_curve"] if meta else None
    check(f"the old pack.py passes slider-02-north.png 1.2 px along (off_curve {old}: the bug)",
          code == 0 and old is not None and old <= 1.0, text[-400:])
    off = os.path.join(out, "as-is-rolloff-off-renders")
    if os.path.exists(off):
        shutil.rmtree(off)
    os.makedirs(off)
    for f in os.listdir(rdir):          # every render a link to the box's; render.json opted out
        if f != contract.FILE and os.path.isfile(os.path.join(rdir, f)):
            os.symlink(os.path.join(os.path.abspath(rdir), f), os.path.join(off, f))
    with open(os.path.join(off, contract.FILE), "w") as f:
        json.dump(dict(load_decl(rdir), rolloff=False), f, indent=1)
    mine, theirs = os.path.join(out, "as-is-rolloff-off"), os.path.join(out, "base-as-is")
    code, text, _ = packed(off, mine)
    check("this tree's pack.py on the box as is, roll-off opted out, exits 0", code == 0, text[-400:])
    code, text, meta_b = packed(off, theirs, base)
    check("the old pack.py on the box as is exits 0", code == 0, text[-400:])
    decl = load_decl(rdir)
    glows = [contract.named(p["sheet"], d) for p in decl["passes"] if p["kind"] == "glow"
             for d, _ in contract.DIRECTIONS[decl["directions"]]]
    check(f"every glow pass's sheet written by both ({len(glows)}; set aside: T06's crop)",
          all(os.path.isfile(os.path.join(o, g + ".png")) for o in (mine, theirs) for g in glows))
    sheets = sorted(f for f in os.listdir(mine) if f != "meta.json" and f[:-4] not in glows)
    same = [f for f in sheets
            if open(os.path.join(mine, f), "rb").read() == open(os.path.join(theirs, f), "rb").read()]
    check(f"every sheet but the glow passes' byte for byte as the baseline's ({len(sheets)})",
          same == sheets and sorted(os.listdir(mine)) == sorted(os.listdir(theirs)), str(set(sheets) - set(same)))
    meta_m = json.load(open(os.path.join(mine, "meta.json")))
    missing = [g for g in glows for m in (meta_m, meta_b) if g not in m]
    for m in (meta_m, meta_b):
        for c in m["checks"].values():
            c.pop(f"{ANIM}_path_px")
        for g in glows:
            if g in m:
                m[g] = {k: v for k, v in m[g].items() if k not in ("size", "shift")}
    check("meta.json equal, every key in order, but for slider_path_px and the glow passes' size and shift",
          not missing and json.dumps(meta_m) == json.dumps(meta_b), f"missing {missing}" if missing else "")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("box")
    ap.add_argument("--baseline", metavar="GIT_REV")
    ap.add_argument("--out")
    a = ap.parse_args()
    rdir = os.path.join(a.box, "renders")
    out = os.path.abspath(a.out or os.path.join(a.box, "slide-test"))
    os.makedirs(out, exist_ok=True)
    decl = load_decl(rdir)
    test_exact(decl)
    test_as_is(rdir, out)
    test_moved(rdir, out, decl)
    test_tracked(rdir, out, decl)
    if a.baseline:
        test_baseline(rdir, out, a.baseline)
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
