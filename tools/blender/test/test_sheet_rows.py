#!/usr/bin/env python3
"""pack.py's animation sheet layout (sheet_layout) held to its docs: one row when the frames fit
in MAX_SHEET_W, else the fewest rows that fit with the frames spread evenly over them
(drop-crusher-reanimation T04a).

  python3 tools/blender/test/test_sheet_rows.py [--out <dir>] [--baseline <git-rev>
                                                [--renders <render-dir> ...]]

Nothing is rendered: small render directories are drawn here and written under --out (default a
new temporary directory; kept), and packed by pack.py. --baseline names a commit from before the
rows were balanced (359d809): its contract.py and pack.py, taken out with `git show`, are run beside
this tree's. --renders names render directories (a render.sh <out-dir>/renders, render.json in it)
to pack with both. Exits 0 when every case below comes out as listed, 1 naming those that do not.

  exact     sheet_layout(frames, frame width) worked by hand: (44, 191) the Drop Crusher's stroke
            -> 22 a row, 2 rows (it was 42 and 2); (42, 191) -> 42, 1 (8022 px, fits); (43, 191)
            -> 22, 2; (32, 271) and (32, 260), the Radiant Generator's carousel and window glow
            -> 16, 2 (they were 30 and 31); (64, 128) -> 64, 1 (exactly 8192); (65, 128) -> 33, 2;
            (100, 200) -> 34, 3; (4, 50) -> 4, 1; (1, 9000) -> 1, 1; (3, 9000) -> 1, 3 (a frame
            wider than the limit alone in its row, as before).
  bounds    every frame count 1-300 at widths 1, 7, 64, 191, 271, 1000, 4096, 4097, 8192 and
            9000: one row exactly when the frames fit (or there is one); else rows the fewest that fit
            (ceil(frames / the most a row holds)), a row no wider than MAX_SHEET_W (a frame wider
            than it alone), every row full but the last, the last short by fewer than rows
            frames, and no row empty.
  packed    a render directory of one plate, its still and a 191 x 136 cycle animation (each
            frame a different block, colours under the roll-off's knee): 44 frames pack to a
            4202 x 272 sheet, line_length 22 in meta.json, frame i in column i % 22 and row
            i // 22, the same pixels as its render's crop; 42 frames to 8022 x 136, line_length
            42; 43 frames to 22 a row, the last cell clear. pack.py exits 0 on each.
  baseline  with --baseline: the 42-frame directory (one row) packs byte for byte as the
            baseline packs it, meta.json equal; the 44-frame one packs differently, every frame
            the same pixels in both sheets, and meta.json equal but for the animation's
            line_length (the baseline's 42). With --renders, each directory likewise: every
            animation's frames the same pixels, every sheet but a wrapped animation's byte for
            byte, meta.json equal but for the wrapped animations' line_length; the sheets
            that change are printed.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import contract  # noqa: E402
import pack  # noqa: E402

FAILED = []
CANVAS = (200, 160)
PPT = 64
FRAME = (189, 134)      # each frame's block: with pack.py's 1 px rim, a 191 x 136 cell
ANIM = "bar"


def check(case, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def packed(src, out, tools=TOOLS):
    """pack.py (tools') src -> out: its exit code, output and meta.json (None if it wrote none)."""
    if os.path.exists(out):
        shutil.rmtree(out)
    code, text = run([sys.executable, os.path.join(tools, "pack.py"), src, out])
    meta = os.path.join(out, "meta.json")
    return code, text, (json.load(open(meta)) if os.path.isfile(meta) else None)


# ---------------------------------------------------------------- exact and bounds

def test_exact():
    print("exact")
    want = {(44, 191): (22, 2), (42, 191): (42, 1), (43, 191): (22, 2), (32, 271): (16, 2), (32, 260): (16, 2),
            (64, 128): (64, 1), (65, 128): (33, 2), (100, 200): (34, 3), (4, 50): (4, 1), (1, 9000): (1, 1),
            (3, 9000): (1, 3)}
    for (n, fw), lr in want.items():
        got = pack.sheet_layout(n, fw)
        check(f"sheet_layout({n}, {fw}) = {lr}", got == lr, f"got {got}")


def test_bounds():
    print("bounds")
    bad = []
    for fw in (1, 7, 64, 191, 271, 1000, 4096, 4097, 8192, 9000):
        most = max(1, pack.MAX_SHEET_W // fw)
        for n in range(1, 301):
            line, rows = pack.sheet_layout(n, fw)
            ok = (rows == 1) == (n * fw <= pack.MAX_SHEET_W or n == 1) and rows == math.ceil(n / min(n, most))
            ok = ok and (line * fw <= pack.MAX_SHEET_W or line == 1)
            ok = ok and line * rows >= n and (rows - 1) * line < n and line * rows - n < rows
            if not ok:
                bad.append((n, fw, line, rows))
    check("3000 layouts: fewest rows, none wider than the limit, the last row the only short one, none empty",
          not bad, f"{len(bad)} wrong, first {bad[:5]}")


# ---------------------------------------------------------------- packed

def frame(i):
    """Frame i: a FRAME block of a colour of its own, a mark at a place of its own (under the knee)."""
    im = Image.new("RGBA", CANVAS)
    x0, y0 = (CANVAS[0] - FRAME[0]) // 2, (CANVAS[1] - FRAME[1]) // 2
    d = ImageDraw.Draw(im)
    d.rectangle((x0, y0, x0 + FRAME[0] - 1, y0 + FRAME[1] - 1), fill=(20 + 4 * i, 200 - 3 * i, 90, 255))
    mx, my = x0 + (i * 7) % (FRAME[0] - 10), y0 + (i * 5) % (FRAME[1] - 10)
    d.rectangle((mx, my, mx + 9, my + 9), fill=(10, 10, 10 + 4 * i, 255))
    return im


def write_fixture(rdir, n):
    if os.path.exists(rdir):
        shutil.rmtree(rdir)
    os.makedirs(rdir)
    decl = dict(footprint=[2, 2], canvas=list(CANVAS), directions="one",
                passes=[dict(name="idle", kind="plate", sheet="base"), dict(name="still", kind="still")],
                animations=[dict(name=ANIM, frames=n, motion="cycle")],
                ports=[], rig=dict(elevation=60.0, px_per_tile=PPT))
    contract.validate(decl, rdir)
    with open(os.path.join(rdir, contract.FILE), "w") as f:
        json.dump(decl, f, indent=1)
    idle = Image.new("RGBA", CANVAS)
    cx, cy = CANVAS[0] // 2, CANVAS[1] // 2
    ImageDraw.Draw(idle).rectangle((cx - PPT, cy - PPT, cx + PPT - 1, cy + PPT - 1), fill=(60, 60, 60, 255))
    idle.save(os.path.join(rdir, "idle.png"))
    still = idle.copy()
    still.alpha_composite(frame(0))
    still.save(os.path.join(rdir, "still.png"))
    for i in range(n):
        frame(i).save(os.path.join(rdir, contract.frame(ANIM, i) + ".png"))
    return rdir


def cells(sheet, n, size, line):
    """The n cells of an animation sheet, line_length line, each size."""
    fw, fh = size
    return [sheet.crop(((i % line) * fw, (i // line) * fh, (i % line + 1) * fw, (i // line + 1) * fh))
            for i in range(n)]


def test_packed(out):
    print("packed")
    fw, fh = FRAME[0] + 2, FRAME[1] + 2
    for n, line, rows in ((44, 22, 2), (42, 42, 1), (43, 22, 2)):
        src = write_fixture(os.path.join(out, f"renders-{n}"), n)
        code, text, meta = packed(src, os.path.join(out, f"sheets-{n}"))
        check(f"{n} frames: pack.py exits 0", code == 0, text[-400:])
        if meta is None:
            continue
        m = meta[ANIM]
        sheet = Image.open(os.path.join(out, f"sheets-{n}", ANIM + ".png")).convert("RGBA")
        check(f"{n} frames: {fw * line} x {fh * rows} sheet, line_length {line}, cell {fw} x {fh}",
              sheet.size == (fw * line, fh * rows) and m["line_length"] == line and list(m["size"]) == [fw, fh]
              and m["frames"] == n, f"sheet {sheet.size}, meta {m}")
        x0, y0 = (CANVAS[0] - FRAME[0]) // 2 - 1, (CANVAS[1] - FRAME[1]) // 2 - 1
        miss = [i for i, c in enumerate(cells(sheet, n, (fw, fh), line))
                if c.tobytes() != frame(i).crop((x0, y0, x0 + fw, y0 + fh)).tobytes()]
        check(f"{n} frames: frame i at column i % {line}, row i // {line}, its render's pixels", not miss,
              f"frames {miss[:8]} differ")
        spare = line * rows - n
        if spare:
            empty = sheet.crop((fw * (line - spare), fh * (rows - 1), fw * line, fh * rows)).getbbox()
            check(f"{n} frames: the last row's {spare} spare cell(s) clear", empty is None, f"drawn in {empty}")


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


def animations(meta):
    """meta.json's animation entries: {sheet: entry}, those with frames and a line_length."""
    return {k: v for k, v in meta.items() if isinstance(v, dict) and "frames" in v and "line_length" in v}


def compare(label, src, out, base):
    """This tree's pack.py and the baseline's on src: the sheets that differ, as a list."""
    print(f"baseline: {label}")
    tag = label.replace("/", "_")
    ours, theirs = os.path.join(out, f"cmp-{tag}-tree"), os.path.join(out, f"cmp-{tag}-baseline")
    (ca, ta, ma), (cb, tb, mb) = packed(src, ours), packed(src, theirs, base)
    check(f"{label}: both exit alike", ca == cb, f"tree {ca}, baseline {cb}\n{ta[-300:]}\n{tb[-300:]}")
    if ma is None or mb is None:
        check(f"{label}: both write meta.json", False, f"tree {ma is not None}, baseline {mb is not None}")
        return None
    pngs = sorted(f for f in os.listdir(theirs) if f.endswith(".png"))
    check(f"{label}: the same sheets", pngs == sorted(f for f in os.listdir(ours) if f.endswith(".png")))
    changed, anims = [], animations(mb)
    for f in pngs:
        a, b = (Image.open(os.path.join(d, f)).convert("RGBA") for d in (ours, theirs))
        if a.tobytes() == b.tobytes() and a.size == b.size:
            continue
        changed.append(f)
        stem = f[:-4]
        if stem not in anims:
            check(f"{label}: {f} byte for byte (not an animation)", False, f"{a.size} vs {b.size}")
            continue
        n, size = anims[stem]["frames"], anims[stem]["size"]
        miss = [i for i, (x, y) in enumerate(zip(cells(a, n, size, ma[stem]["line_length"]),
                                                 cells(b, n, size, mb[stem]["line_length"])))
                if x.tobytes() != y.tobytes()]
        check(f"{label}: {stem}'s {n} frames the same pixels, {b.size[0]}x{b.size[1]} -> {a.size[0]}x{a.size[1]}",
              not miss, f"frames {miss[:8]} differ")
    # meta.json equal but for the changed animations' line_length
    for stem in (f[:-4] for f in changed):
        if stem in ma and stem in mb:
            mb[stem] = dict(mb[stem], line_length=ma[stem]["line_length"])
    check(f"{label}: meta.json equal but for the changed sheets' line_length", json.dumps(ma) == json.dumps(mb))
    print(f"  sheets that pack differently: {changed or 'none'}")
    return changed


def test_baseline(out, base, renders):
    one = write_fixture(os.path.join(out, "renders-42"), 42)
    check("42 frames (one row): every sheet byte for byte as the baseline's", compare("one row", one, out, base) == [])
    two = write_fixture(os.path.join(out, "renders-44"), 44)
    check("44 frames (wrapped): only the animation's sheet changes",
          compare("wrapped", two, out, base) == [ANIM + ".png"])
    for r in renders:
        compare(r, r, out, base)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out")
    ap.add_argument("--baseline", metavar="GIT_REV")
    ap.add_argument("--renders", nargs="+", default=[], metavar="RENDER_DIR")
    a = ap.parse_args()
    if a.renders and not a.baseline:
        ap.error("--renders goes with --baseline")
    out = os.path.abspath(a.out or tempfile.mkdtemp(prefix="sheet-rows-test-"))
    os.makedirs(out, exist_ok=True)
    print(f"writing under {out}")
    test_exact()
    test_bounds()
    test_packed(out)
    if a.baseline:
        test_baseline(out, baseline_tools(a.baseline, out), [os.path.abspath(r) for r in a.renders])
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
