#!/usr/bin/env python3
"""pack.py's glow crop -- a still glow kept to the box holding LIGHT_SHARE of its light -- held to its docs.

  python3 tools/blender/test/test_glow_crop.py [--out <dir>] [--baseline <git-rev>
                                               [--renders <render-out> ...]]

Every share below is pack.LIGHT_SHARE's (99.9 %, Liam 2026-10-20), and "the share" is it.
Nothing is rendered here. A fixture model is drawn with PIL: a 2x2 plate on a 256 px canvas,
lit by a window -- a 40 x 20 px block adding luma 173, the glow's core -- and by a faint haze
over the noise floor (luma 10, LAYER_FLOOR 8) in three runs of SPECK_PX pixels, so the speck
filter keeps them, far from the window (52 rows below it, 56 px left of it past the plate, 49
rows above it): 0.087 % of the light in all, under 1 - the share. --baseline names a commit
from before the crop (b83505b): its contract.py and pack.py, taken out with `git show`, are
run beside this tree's.
--renders names render.sh output directories (the test box's, a model's) to pack with both,
with --baseline; the table, per glow pass, goes to <out>/glow-crop.json. Everything is written
under --out (default: a new directory under the system's temporary one, named when it starts)
and kept.

Exits 0 when every case below comes out as listed, 1 naming those that do not.

  haze       the fixture packed: pack.py exits 0; glow.png is the window and its 1 px rim, 42 x 22,
             its shift the window's centre from the origin; its pixels inside the rim are
             glow_layer's, byte for byte, and its rim clear; the light it keeps (alpha x luma)
             at least the share of the light glow_layer finds before the box, every pixel of the
             window kept. The box the old crop took -- every lit pixel left after the speck
             filter -- reaches the haze (each group inside it). base.png and glow.png as packed
             with no haze, byte for byte.
  soft       a soft glow (a Gaussian, sigma 6 px, peak luma 200): light_box
             keeps at least the share of its light and shrinking any side by a pixel leaves less;
             its peak inside.
  exact      light_box against a search of every box, on 300 small random images and shares:
             the same box (smallest area, then most light, then topmost, leftmost).
  empty      a glow pass that lights nothing: pack.py exits non-zero naming the glow as empty,
             as before.
  animated   glow_frame (an animated glow's frame) on the haze: its alpha still reaches every
             haze group (its faint tail kept). With --baseline: glow_frame byte for byte as
             the baseline's, with and without a bloom.
  baseline   with --baseline: the old pack.py on the fixture crops to the haze (the bug: its
             glow.png is larger than 42 x 22). On the fixture and every --renders directory,
             every sheet but a glow pass's byte for byte as the baseline's (a glow animation's
             too), and meta.json the same but for the glow passes' size and shift; for each
             glow pass, old and new size and shift, the share of the old sheet's light the new
             keeps (at least the share), the brightest pixel left out (% of the peak), whether
             every core pixel (>= 60 % of the peak, light_stats') is kept, and whether the new
             sheet is the old one's pixels where it lies, byte for byte, but its opaque pixels
             outside the box (in its rim) cleared, colour and all. And with LIGHT_SHARE set to 1
             (the whole light), glow_layer on every glow pass, the fixture's and each
             --renders', byte for byte as the baseline's: the box is all that changed. Both
             pack.py's pack a copy of the renders whose render.json says rolloff false: this
             tree's rolls the highlights of every sheet but a shadow's or a light's off by
             default since T07 and the baseline's does not (test_rolloff.py holds the roll-off).
"""
import argparse
import importlib.util
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import contract  # noqa: E402
import pack  # noqa: E402

FAILED = []
CANVAS = (256, 256)
PPT = 64
SHARE = pack.LIGHT_SHARE
PLATE = (64, 64, 192, 192)              # the 2x2 footprint, its top raised a tile for a roof
PLATE_RGB = (40, 40, 40)
WINDOW = (100, 80, 140, 100)            # the core: x0, y0, x1, y1, ends exclusive
WINDOW_ADDS = (200, 170, 120)           # over the plate, under 255: no channel clips
# the haze: (x0, y0, length) runs of luma 10 a row long, each SPECK_PX
HAZE = ((100, 152, 4), (40, 120, 4), (115, 30, 4))
HAZE_ADDS = (10, 10, 10)


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
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


def luma_light(im):
    """An RGBA image's light: the sum of alpha x luma (PIL's L), alpha as a fraction."""
    im = im.convert("RGBA")
    return sum(a * v for a, v in zip(im.getchannel("A").get_flattened_data(),
                                     im.convert("RGB").convert("L").get_flattened_data())) / 255


# ---------------------------------------------------------------- the fixture

def plate():
    im = Image.new("RGBA", CANVAS)
    ImageDraw.Draw(im).rectangle((PLATE[0], PLATE[1], PLATE[2] - 1, PLATE[3] - 1), fill=PLATE_RGB + (255,))
    return im


def lit(haze=True, window=True):
    im = plate()
    px = im.load()
    spots = [(x, y) for x in range(WINDOW[0], WINDOW[2]) for y in range(WINDOW[1], WINDOW[3])] if window else []
    adds = {s: WINDOW_ADDS for s in spots}
    if haze:
        adds.update({(x0 + i, y): HAZE_ADDS for x0, y, n in HAZE for i in range(n)})
    for (x, y), add in adds.items():
        r, g, b, a = px[x, y]
        px[x, y] = (r + add[0], g + add[1], b + add[2], 255)
    return im


def write_fixture(rdir, haze=True, window=True):
    if os.path.exists(rdir):
        shutil.rmtree(rdir)
    os.makedirs(rdir)
    decl = dict(footprint=[2, 2], canvas=list(CANVAS), directions="one",
                passes=[dict(name="idle", kind="plate", sheet="base"),
                        dict(name="working", kind="glow", over="idle", sheet="glow")],
                animations=[], ports=[], rig=dict(elevation=60.0, px_per_tile=PPT))
    contract.validate(decl, rdir)
    with open(os.path.join(rdir, contract.FILE), "w") as f:
        json.dump(decl, f, indent=1)
    plate().save(os.path.join(rdir, "idle.png"))
    lit(haze, window).save(os.path.join(rdir, "working.png"))
    return rdir


# ---------------------------------------------------------------- haze

def test_haze(out):
    print("haze")
    src = write_fixture(os.path.join(out, "haze-renders"))
    code, text, meta = packed(src, os.path.join(out, "haze-sheets"))
    check("pack.py exits 0", code == 0, text[-400:])
    if meta is None:
        return
    want = (WINDOW[0] - 1, WINDOW[1] - 1, WINDOW[2] + 1, WINDOW[3] + 1)
    cx, cy = (WINDOW[0] + WINDOW[2]) / 2, (WINDOW[1] + WINDOW[3]) / 2
    shift = [round((cx - CANVAS[0] / 2) / PPT, 5), round((cy - CANVAS[1] / 2) / PPT, 5)]
    g = meta["glow"]
    size = [WINDOW[2] - WINDOW[0] + 2, WINDOW[3] - WINDOW[1] + 2]
    check(f"glow.png {size[0]} x {size[1]}, shift {shift} (the window's centre)", list(g["size"]) == size and
          list(g["shift"]) == shift, str(g))
    sheet = Image.open(os.path.join(out, "haze-sheets", "glow.png")).convert("RGBA")
    full = pack.glow_layer(lit().convert("RGBA"), plate())
    check("glow.png is glow_layer's pixels in the window's box, byte for byte",
          sheet.tobytes() == full.crop(want).tobytes())
    inner = Image.new("RGBA", sheet.size)
    inner.paste(sheet.crop((1, 1, sheet.width - 1, sheet.height - 1)), (1, 1))
    check("its 1 px rim is clear (the fixture adds nothing under the floor)", sheet.tobytes() == inner.tobytes())
    # the light before the box: glow_layer without light_box, from its own pieces
    diff = ImageChops.subtract(lit().convert("RGB"), plate().convert("RGB"))
    alpha = pack.drop_specks(diff.convert("L").point(lambda v: 255 if v > pack.LAYER_FLOOR else 0))
    before = luma_light(Image.merge("RGBA", (*diff.split(), alpha)))
    kept = luma_light(sheet)
    check(f"keeps {100 * kept / before:.3f} % of the light, at least {100 * SHARE:g} %", kept >= SHARE * before)
    haze_share = 1 - kept / before
    check(f"the haze is {100 * haze_share:.3f} % of the light, under {100 * (1 - SHARE):.3g} % (the fixture is "
          f"what it says)", 0 < haze_share < 1 - SHARE)
    a = sheet.getchannel("A")
    check("every pixel of the window kept, opaque", all(a.getpixel((x - want[0], y - want[1])) == 255
                                                        for x in range(WINDOW[0], WINDOW[2])
                                                        for y in range(WINDOW[1], WINDOW[3])))
    old = alpha.getbbox()
    check(f"the old crop (every lit pixel, {old}) reaches every haze group",
          all(old[0] <= x0 and x0 + n <= old[2] and old[1] <= y < old[3] for x0, y, n in HAZE), str(old))
    clean = write_fixture(os.path.join(out, "haze-renders-none"), haze=False)
    code, text, _ = packed(clean, os.path.join(out, "haze-sheets-none"))
    check("with no haze: exit 0, base.png and glow.png byte for byte as with it",
          code == 0 and all(open(os.path.join(out, "haze-sheets", f), "rb").read() ==
                            open(os.path.join(out, "haze-sheets-none", f), "rb").read()
                            for f in ("base.png", "glow.png")), text[-300:])


# ---------------------------------------------------------------- soft, exact

def box_light(px, w, bb):
    return sum(px[y * w + x] for y in range(bb[1], bb[3]) for x in range(bb[0], bb[2]))


def test_soft():
    print("soft")
    w = h = 64
    px = [round(200 * math.exp(-((x - 30.5) ** 2 + (y - 33) ** 2) / (2 * 6 ** 2))) for y in range(h) for x in range(w)]
    im = Image.new("L", (w, h))
    im.putdata(px)
    bb = pack.light_box(im, SHARE)
    total, need = sum(px), math.ceil(sum(px) * Fraction(str(SHARE)))
    kept = box_light(px, w, bb)
    check(f"keeps {100 * kept / total:.3f} % of the light, at least {100 * SHARE:g} % ({bb})", kept >= need)
    smaller = [(bb[0] + 1, bb[1], bb[2], bb[3]), (bb[0], bb[1] + 1, bb[2], bb[3]),
               (bb[0], bb[1], bb[2] - 1, bb[3]), (bb[0], bb[1], bb[2], bb[3] - 1)]
    check(f"shrinking any side by a pixel leaves under {100 * SHARE:g} %",
          all(box_light(px, w, s) < need for s in smaller))
    peak = px.index(max(px))
    check("the peak inside", bb[0] <= peak % w < bb[2] and bb[1] <= peak // w < bb[3])


def test_exact():
    print("exact")
    rnd = random.Random(20261020)
    bad = []
    for t in range(300):
        w, h = rnd.randint(1, 8), rnd.randint(1, 8)
        dens = rnd.random()
        px = [rnd.randint(0, 255) if rnd.random() < dens else 0 for _ in range(w * h)]
        share = rnd.choice((SHARE, 0.995, 0.9, 0.5, 1.0))
        im = Image.new("L", (w, h))
        im.putdata(px)
        got = pack.light_box(im, share)
        if not any(px):
            if got is not None:
                bad.append((t, "no light, a box"))
            continue
        need = math.ceil(sum(px) * Fraction(str(share)))
        best = min(((y1 - y0) * (x1 - x0), -box_light(px, w, (x0, y0, x1, y1)), y0, x0, (x0, y0, x1, y1))
                   for y0 in range(h) for y1 in range(y0 + 1, h + 1) for x0 in range(w) for x1 in range(x0 + 1, w + 1)
                   if box_light(px, w, (x0, y0, x1, y1)) >= need)
        if tuple(got) != best[4]:
            bad.append((t, got, best[4]))
    check("light_box is the search's box in every case", not bad, str(bad[:5]))


# ---------------------------------------------------------------- empty, animated

def test_empty(out):
    print("empty")
    src = write_fixture(os.path.join(out, "empty-renders"), haze=False, window=False)
    code, text, _ = packed(src, os.path.join(out, "empty-sheets"))
    check("a glow that lights nothing: non-zero, naming it empty",
          code != 0 and "working.png minus its plate is empty" in text, f"exit {code}: {text[-300:]}")


def test_animated(base):
    print("animated")
    # an animated glow's render is the light alone on transparent film: the window and the haze
    film = Image.new("RGBA", CANVAS)
    d = ImageDraw.Draw(film)
    d.rectangle((WINDOW[0], WINDOW[1], WINDOW[2] - 1, WINDOW[3] - 1), fill=WINDOW_ADDS + (255,))
    for x0, y, n in HAZE:
        d.line((x0, y, x0 + n - 1, y), fill=HAZE_ADDS + (255,))
    fr = pack.glow_frame(film)
    bb = fr.getchannel("A").getbbox()
    check(f"glow_frame keeps every haze group (alpha box {bb})",
          all(bb[0] <= x0 and x0 + n <= bb[2] and bb[1] <= y < bb[3] for x0, y, n in HAZE), str(bb))
    if base is None:
        return
    old = load_module(os.path.join(base, "pack.py"), "pack_baseline")
    for bloom in (None, [[4, 0.5], [12, 0.25]]):
        check(f"glow_frame (bloom {bloom}) byte for byte as the baseline's",
              pack.glow_frame(film, bloom).tobytes() == old.glow_frame(film, bloom).tobytes())


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


def load_module(path, name):
    sys.path.insert(0, os.path.dirname(path))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.pop(0)


def glow_sheets(decl):
    """The sheet names of every glow pass, in every direction."""
    dirs = [d for d, _ in contract.DIRECTIONS[decl["directions"]]]
    return [contract.named(p["sheet"], d) for p in decl["passes"] if p["kind"] == "glow" for d in dirs]


def compare(label, rdir, out, base):
    """This tree's pack.py and the baseline's on one render directory: every sheet but a glow pass's
    byte for byte, meta.json the same but for the glow passes' size and shift, and for each glow
    pass the numbers the ticket asks for. Returns those numbers."""
    print(f"baseline: {label}")
    with open(os.path.join(rdir, contract.FILE)) as f:
        decl = json.load(f)
    mine, theirs = os.path.join(out, f"{label}-mine"), os.path.join(out, f"{label}-base")
    off = os.path.join(out, f"{label}-renders-rolloff-off")
    if os.path.exists(off):
        shutil.rmtree(off)
    os.makedirs(off)
    for f in os.listdir(rdir):          # every render a link to the original's; render.json opted out
        if f != contract.FILE and os.path.isfile(os.path.join(rdir, f)):
            os.symlink(os.path.join(os.path.abspath(rdir), f), os.path.join(off, f))
    with open(os.path.join(off, contract.FILE), "w") as f:
        json.dump(dict(decl, rolloff=False), f, indent=1)
    runs = {}
    for who, tools, o in (("this tree", TOOLS, mine), ("baseline", base, theirs)):
        code, text, meta = packed(off, o, tools)
        runs[who] = (code, meta)
        if meta is None:
            check(f"{label}: pack.py ({who}) writes meta.json", False, f"exit {code}: {text[-300:]}")
            return []
    check(f"{label}: pack.py exits the same ({runs['this tree'][0]}, baseline {runs['baseline'][0]})",
          runs["this tree"][0] == runs["baseline"][0])
    glows = glow_sheets(decl)
    names = sorted(set(os.listdir(mine)) | set(os.listdir(theirs)))
    differ = [n for n in names if n != "meta.json" and n[:-4] not in glows and
              (not os.path.isfile(os.path.join(mine, n)) or not os.path.isfile(os.path.join(theirs, n)) or
               open(os.path.join(mine, n), "rb").read() != open(os.path.join(theirs, n), "rb").read())]
    check(f"{label}: every sheet but the glow passes' ({', '.join(glows) or 'none'}) byte for byte as the "
          f"baseline's ({len([n for n in names if n != 'meta.json']) - len(glows)} files)", not differ, str(differ))
    ma, mb = runs["this tree"][1], runs["baseline"][1]
    rows = []
    for g in glows:
        rows.append(dict(sheet=g, old=dict(size=mb[g]["size"], shift=mb[g]["shift"]),
                         new=dict(size=ma[g]["size"], shift=ma[g]["shift"])))
        for m in (ma, mb):
            m[g] = {k: v for k, v in m[g].items() if k not in ("size", "shift")}
    check(f"{label}: meta.json the same but for the glow passes' size and shift",
          json.dumps(ma) == json.dumps(mb))
    whole_light(label, rdir, decl, out, base)
    for row in rows:
        new = Image.open(os.path.join(mine, row["sheet"] + ".png")).convert("RGBA")
        old = Image.open(os.path.join(theirs, row["sheet"] + ".png")).convert("RGBA")
        nb, ob = box_on(row["new"], decl["canvas"]), box_on(row["old"], decl["canvas"])
        at = (nb[0] - ob[0], nb[1] - ob[1])
        inside = ob[0] <= nb[0] and ob[1] <= nb[1] and nb[2] <= ob[2] and nb[3] <= ob[3]

        def kept(x, y):
            return at[0] + 1 <= x < at[0] + new.width - 1 and at[1] + 1 <= y < at[1] + new.height - 1
        # what the new sheet should be: the old one's pixels where it lies, every opaque one
        # outside the box (its rim) cleared, colour and all, and every other left as it was
        want = old.crop((at[0], at[1], at[0] + new.width, at[1] + new.height))
        wpx = want.load()
        for y in range(want.height):
            for x in range(want.width):
                if wpx[x, y][3] and not kept(at[0] + x, at[1] + y):
                    wpx[x, y] = (0, 0, 0, 0)
        same = inside and new.tobytes() == want.tobytes()
        lum = old.convert("RGB").convert("L")
        lit_px = [(i % old.width, i // old.width, v) for i, (v, a) in
                  enumerate(zip(lum.get_flattened_data(), old.getchannel("A").get_flattened_data())) if a]
        peak = max(v for _, _, v in lit_px)
        out_px = [v for x, y, v in lit_px if not kept(x, y)]
        core_lost = sum(1 for x, y, v in lit_px if v >= 0.6 * peak and not kept(x, y))
        share = luma_light(new) / luma_light(old)
        row.update(share=round(100 * share, 3), dropped_px=len(out_px),
                   brightest_dropped_pct=round(100 * max(out_px, default=0) / peak, 1), peak=peak,
                   core_lost=core_lost, unchanged_inside=same)
        print(f"    {row['sheet']}: old {row['old']}, new {row['new']}, keeps {row['share']} % of the light, "
              f"{row['dropped_px']} lit px left out (brightest {row['brightest_dropped_pct']} % of peak "
              f"{peak}), core px lost {core_lost}, new = old inside it: {same}")
        check(f"{label} {row['sheet']}: keeps at least {100 * SHARE:g} % of the light", share >= SHARE, str(row))
        check(f"{label} {row['sheet']}: no core pixel (>= 60 % of the peak) lost", core_lost == 0, str(row))
        check(f"{label} {row['sheet']}: the old sheet's pixels where it lies, but the opaque ones outside its box",
              same, str(row))
    return rows


def whole_light(label, rdir, decl, out, base):
    """glow_layer with LIGHT_SHARE 1 on every glow pass of rdir: byte for byte as the baseline's."""
    old = load_module(os.path.join(base, "pack.py"), "pack_baseline")
    packer = pack.Packer(rdir, os.path.join(out, f"{label}-whole"), decl)
    differ = []
    keep, pack.LIGHT_SHARE = pack.LIGHT_SHARE, 1.0
    try:
        for d, _ in contract.DIRECTIONS[decl["directions"]]:
            for p in (q for q in decl["passes"] if q["kind"] == "glow"):
                lit_, under = (packer.open(contract.named(n, d), d) for n in (p["name"], p["over"]))
                if pack.glow_layer(lit_, under).tobytes() != old.glow_layer(lit_, under).tobytes():
                    differ.append(contract.named(p["sheet"], d))
    finally:
        pack.LIGHT_SHARE = keep
    check(f"{label}: at LIGHT_SHARE 1, glow_layer byte for byte as the baseline's on every glow pass",
          not differ, str(differ))


def box_on(entry, canvas):
    """A sheet's box on its canvas, from its meta.json size and shift."""
    (w, h), (sx, sy) = entry["size"], entry["shift"]
    cw, ch = canvas
    return (round(cw / 2 + sx * PPT - w / 2), round(ch / 2 + sy * PPT - h / 2),
            round(cw / 2 + sx * PPT - w / 2) + w, round(ch / 2 + sy * PPT - h / 2) + h)


def test_baseline(out, base, renders):
    print("baseline")
    src = os.path.join(out, "haze-renders")
    code, _, meta = packed(src, os.path.join(out, "haze-sheets-old"), base)
    size = meta and meta["glow"]["size"]
    w, h = WINDOW[2] - WINDOW[0] + 2, WINDOW[3] - WINDOW[1] + 2
    check(f"the old pack.py crops the fixture's glow to its haze ({size}, larger than {w} x {h})",
          code == 0 and size is not None and size[0] > w and size[1] > h, f"exit {code}, {size}")
    table = {"fixture": compare("fixture", src, out, base)}
    for r in renders:
        rdir = os.path.join(r, "renders")
        table[os.path.basename(os.path.normpath(r))] = compare(os.path.basename(os.path.normpath(r)), rdir, out, base)
    with open(os.path.join(out, "glow-crop.json"), "w") as f:
        json.dump(table, f, indent=1)
    print(f"  the table: {os.path.join(out, 'glow-crop.json')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out")
    ap.add_argument("--baseline", metavar="GIT_REV")
    ap.add_argument("--renders", nargs="+", default=[], metavar="RENDER_OUT")
    a = ap.parse_args()
    if a.renders and not a.baseline:
        ap.error("--renders goes with --baseline")
    out = a.out or tempfile.mkdtemp(prefix="glow-crop-test-")
    os.makedirs(out, exist_ok=True)
    print(f"writing under {out}")
    base = baseline_tools(a.baseline, out) if a.baseline else None
    test_haze(out)
    test_soft()
    test_exact()
    test_empty(out)
    test_animated(base)
    if base:
        test_baseline(out, base, [os.path.abspath(r) for r in a.renders])
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
