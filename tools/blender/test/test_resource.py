#!/usr/bin/env python3
"""The resource model (contract.py's resource and effect passes, pack.py's resource sheets) held to its docs.

  python3 tools/blender/test/test_resource.py <resource-out> [--baseline <git-rev> [--renders <render-out> ...]]
                                              [--out <dir>]

<resource-out> is render.sh's <out-dir> for test/resource_box.py: a target disc in three stages of
four variations, with an effect over it. Nothing is rendered here: copies of its renders, with
render.json edited, are packed by pack.py. --baseline names a commit from before the resource
model (vents cd10283): its contract.py and pack.py, taken out with `git show`, are run beside
this tree's on every --renders <render-out> (any render.sh output of a building, test/box.py's
and test/radiant_box.py's say, or a real model's), and every file they write must be byte for
byte the same; so must `contract.py plates`. Everything is written under --out (default
<resource-out>/resource-test) and kept.

Exits 0 when every case below comes out as listed, 1 naming those that do not.

  contract   the fixture's declaration accepted; cell("vent", 2, 3) is "vent-02-03"; cells() runs
             row by row from stage 0. Refused, each naming its field: stages 0, stages missing,
             variations "4" (passes[0].stages / .variations); two resource passes, two effect
             passes, an effect pass alone (passes); a plate beside the resource (passes[k].kind);
             a building's declaration (a plate, four directions; accepted alone) with an effect
             added (passes); an effect over a name not the
             resource's, an effect with stages of its own, an effect with a bloom of [[0, 1]]
             (passes[1].over / .stages / .bloom); a sheet "checks" (passes[0].sheet); directions
             "four", an animation, a port, a cut, ports_turn (each its own key).
  sheet      the fixture packed, exit 0: meta.json's keys resource, resource-effect, checks in that
             order; each sheet's entry frame_count 4, variation_count 3, line_length 4, its kind;
             each png 4 x 3 of its size; each cell, pixel for pixel, its render as pack.py takes
             it (cleaned below NOISE; the effect's turned to light with its bloom), rolled off and
             cropped to the box its size and shift give on the canvas; that box holds every cell,
             each side within 1 px (the rim) of one of them; stage 0's row holds more pixels than
             stage 1's and stage 1's than stage 2's (the fixture shrinks as it depletes).
  checks     resource_edge_px 0, resource-effect_edge_px 0, resource-effect_white_px 0,
             resource_reach_tiles within 0.05 of 0.9 past every edge (the cyan ring, 2.4 tiles, less
             the 3 x 3 footprint's 1.5), rolloff_px naming both sheets; contract.py plates lists the
             four stage-0 cells.
  one stage  the renders with stages 1 (the other stages' renders gone): variation_count 1, and the
             sheet the full sheet's top row, size and shift the same (stage 0 is the widest); with
             stages 1 and variations 1 and no effect: a 1 x 1 sheet.
  rolloff    rolloff false: no rolloff_px, and each sheet as the renders cropped, unrolled.
  refused    each exits non-zero naming what it names: a resource cell gone (resource-01-02.png);
             an effect cell gone (resource-effect-02-03.png); a cell on the wrong canvas (the
             canvas); a resource cell emptied (resource-02-01.png, "is empty"); every effect cell
             dark ("every cell"); a block on the canvas's edge of resource-00-03 ("canvas's edge",
             that cell, meta.json written); a white square in resource-effect-01-02 ("clipped to
             white", that cell); variations 30 ("does not wrap"). One effect cell dark: accepted.
  identity   with --baseline: on every --renders, pack.py's every output file (sheets and
             meta.json) and `contract.py plates`' output byte for byte as the baseline's.
"""
import argparse
import copy
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import contract  # noqa: E402
import pack  # noqa: E402

FAILED = []
RES, FX = "resource", "resource-effect"         # resource_box.py's passes, and their sheets


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


def save_decl(rdir, decl):
    with open(os.path.join(rdir, contract.FILE), "w") as f:
        json.dump(decl, f, indent=1)


def renders_copy(src, dst, edit=None):
    """A copy of a render directory, its render.json edited by edit(decl, dst)."""
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    if edit:
        decl = load_decl(dst)
        edit(decl, dst)
        save_decl(dst, decl)
    return dst


def packed(src, out, tools=TOOLS):
    """pack.py (tools') src -> out: its exit code, output and meta.json (None if it wrote none)."""
    if os.path.exists(out):
        shutil.rmtree(out)
    code, text = run([sys.executable, os.path.join(tools, "pack.py"), src, out])
    meta = os.path.join(out, "meta.json")
    return code, text, (json.load(open(meta)) if os.path.isfile(meta) else None)


def files(d):
    return sorted(f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)))


def same_dirs(a, b):
    """Whether two directories hold the same files, byte for byte: (ok, why)."""
    fa, fb = files(a), files(b)
    if fa != fb:
        return False, f"files differ: {sorted(set(fa) ^ set(fb))}"
    bad = [f for f in fa if open(os.path.join(a, f), "rb").read() != open(os.path.join(b, f), "rb").read()]
    return not bad, f"differ: {bad}"


def same_pixels(a, b):
    return a.size == b.size and a.convert("RGBA").tobytes() == b.convert("RGBA").tobytes()


def cell_box(meta, sheet, decl):
    """The box on the canvas that meta.json's size and shift say every cell was cut from."""
    w, h = meta[sheet]["size"]
    sx, sy = meta[sheet]["shift"]
    cw, ch = decl["canvas"]
    ppt = decl["rig"]["px_per_tile"]
    x0, y0 = round(cw / 2 + sx * ppt - w / 2), round(ch / 2 + sy * ppt - h / 2)
    return x0, y0, x0 + w, y0 + h


def as_packed(rdir, p, s, v):
    """A cell's render as pack.py takes it, before the roll-off."""
    im = Image.open(os.path.join(rdir, contract.cell(p["name"], s, v) + ".png")).convert("RGBA")
    return pack.glow_frame(im, p.get("bloom")) if p["kind"] == "effect" else pack.clean(im)


def opaque(im):
    return im.getchannel("A").point(lambda a: 255 if a else 0).histogram()[255]


# ---------------------------------------------------------------- contract

# a building's declaration, as small as the contract takes: a plate, four directions
BUILDING = dict(footprint=[2, 2], canvas=[192, 192], directions="four", animations=[], ports=[],
                passes=[dict(name="idle", kind="plate", sheet="base")], rig=dict(elevation=60.0, px_per_tile=64))


def test_contract(decl0):
    print("contract")

    def case(label, edit, want_field=None, decl=decl0):
        d = copy.deepcopy(decl)
        edit(d)
        try:
            contract.validate(d, "test")
            check(label, want_field is None, "accepted, but should be refused naming " + str(want_field))
        except contract.ContractError as e:
            check(label, want_field is not None and f": {want_field}:" in str(e),
                  f"refused: {e}" if want_field is None else f"refused, not naming {want_field}: {e}")

    def on(k, **kw):
        return lambda d: d["passes"][k].update(**kw)
    case("the fixture's declaration accepted", lambda d: None)
    check('cell("vent", 2, 3) is "vent-02-03"', contract.cell("vent", 2, 3) == "vent-02-03",
          contract.cell("vent", 2, 3))
    want = [(s, v) for s in range(3) for v in range(4)]
    check("cells() runs row by row from stage 0", contract.cells(decl0) == want, f"{contract.cells(decl0)}")
    case("stages 0 refused", on(0, stages=0), "passes[0].stages")
    case("stages missing refused", lambda d: d["passes"][0].pop("stages"), "passes[0].stages")
    case('variations "4" refused', on(0, variations="4"), "passes[0].variations")
    case("two resource passes refused",
         lambda d: d["passes"].append(dict(name="r2", kind="resource", sheet="r2", stages=1, variations=1)), "passes")
    case("two effect passes refused",
         lambda d: d["passes"].append(dict(name="e2", kind="effect", sheet="e2", over=RES)), "passes")
    case("an effect pass alone refused", lambda d: d["passes"].pop(0), "passes")
    case("a plate beside the resource refused",
         lambda d: d["passes"].append(dict(name="idle", kind="plate", sheet="base")), "passes[2].kind")
    case("a building's declaration with an effect added refused",
         lambda d: d["passes"].append(dict(name="fx", kind="effect", sheet="fx", over="idle")), "passes",
         decl=BUILDING)
    case("that building's declaration alone accepted", lambda d: None, decl=BUILDING)
    case("an effect over another name refused", on(1, over="ore"), "passes[1].over")
    case("an effect with stages of its own refused", on(1, stages=3), "passes[1].stages")
    case("an effect bloom of [[0, 1]] refused", on(1, bloom=[[0, 1]]), "passes[1].bloom")
    case('a sheet "checks" refused', on(0, sheet="checks"), "passes[0].sheet")
    case('directions "four" refused', lambda d: d.update(directions="four"), "directions")
    case("an animation refused",
         lambda d: d["animations"].append(dict(name="bubble", frames=4, motion="flow")), "animations")
    case("a port refused", lambda d: d["ports"].append(dict(tile=[0, -1], face="N")), "ports")
    case("a cut refused", lambda d: d.update(cut=["S"]), "cut")
    case("ports_turn refused", lambda d: d.update(ports_turn=False), "ports_turn")


# ---------------------------------------------------------------- the sheets

def held_sheet(rdir, out_dir, meta, decl, p, rolled=True):
    """One sheet held to its docs: its entry, its size, each cell pixel for pixel, its box."""
    sheet, res = p["sheet"], contract.resource_pass(decl)
    rows, cols = res["stages"], res["variations"]
    e = meta[sheet]
    check(f"{sheet}: frame_count {cols}, variation_count {rows}, line_length {cols}, kind {p['kind']}",
          (e["frame_count"], e["variation_count"], e["line_length"], e["kind"]) == (cols, rows, cols, p["kind"]),
          f"{e}")
    im = Image.open(os.path.join(out_dir, sheet + ".png"))
    w, h = e["size"]
    check(f"{sheet}.png is {cols} x {rows} of its size", im.size == (w * cols, h * rows), f"{im.size}, size {w}x{h}")
    bb = cell_box(meta, sheet, decl)
    bad, sides = [], [[], [], [], []]
    for s, v in contract.cells(decl):
        src = as_packed(rdir, p, s, v)
        want = pack.roll(src)[0] if rolled else src
        if not same_pixels(im.crop((v * w, s * h, (v + 1) * w, (s + 1) * h)), want.crop(bb)):
            bad.append(contract.cell(p["name"], s, v))
        got = src.getchannel("A").getbbox()
        if got is not None:
            for k in range(4):
                sides[k].append(got[k])
    check(f"{sheet}: every cell is its render as packed{', rolled off,' if rolled else ''} cropped to its box",
          not bad, f"differ: {bad}")
    rim = (min(sides[0]) - 1, min(sides[1]) - 1, max(sides[2]) + 1, max(sides[3]) + 1)
    check(f"{sheet}: its box holds every cell, each side within the 1 px rim", tuple(bb) == rim, f"{bb} vs {rim}")
    return im, e


def test_sheet(rdir, out):
    print("sheet")
    decl = load_decl(rdir)
    sheets = os.path.join(out, "sheets")
    code, text, meta = packed(rdir, sheets)
    check("the fixture packs, exit 0", code == 0, text[-600:])
    if meta is None:
        return None
    check("meta.json: resource, resource-effect, checks, in that order", list(meta) == [RES, FX, "checks"],
          f"{list(meta)}")
    im, e = held_sheet(rdir, sheets, meta, decl, decl["passes"][0])
    held_sheet(rdir, sheets, meta, decl, decl["passes"][1])
    h = e["size"][1]
    rows = [opaque(im.crop((0, s * h, im.width, (s + 1) * h))) for s in range(3)]
    check("stage 0's row holds more than stage 1's, and 1's more than 2's", rows[0] > rows[1] > rows[2], f"{rows}")

    print("checks")
    c = meta["checks"]
    for k in (f"{RES}_edge_px", f"{FX}_edge_px", f"{FX}_white_px"):
        check(f"{k} 0", c.get(k, [None])[0] == 0, f"{c.get(k)}")
    reach = c.get(f"{RES}_reach_tiles", [{}])[0]
    check("resource_reach_tiles within 0.05 of 0.9 past every edge",
          sorted(reach) == ["E", "N", "S", "W"] and all(abs(t - 0.9) <= 0.05 for t in reach.values()), f"{reach}")
    check("rolloff_px names both sheets", sorted(c.get("rolloff_px", [{}])[0]) == sorted([RES, FX]), f"{c.get('rolloff_px')}")
    code, text = run([sys.executable, os.path.join(TOOLS, "contract.py"), "plates", rdir])
    want = [os.path.join(rdir, contract.cell(RES, 0, v) + ".png") for v in range(4)]
    check("contract.py plates lists the four stage-0 cells", code == 0 and text.split() == want, text)
    return im, meta


def one_stage(variations=None, effect=True):
    """An edit for renders_copy: the renders as a model of stage 0 alone (the other stages'
    renders gone), of its first `variations` (all, None), with its effect or without."""
    def edit(d, dst):
        for p in d["passes"]:
            for s, v in contract.cells(d):
                if s > 0 or (variations is not None and v >= variations) or (p["kind"] == "effect" and not effect):
                    os.remove(os.path.join(dst, contract.cell(p["name"], s, v) + ".png"))
        d["passes"][0]["stages"] = 1
        if variations is not None:
            d["passes"][0]["variations"] = variations
        if not effect:
            d["passes"] = d["passes"][:1]
    return edit


def test_one_stage(rdir, out, full):
    print("one stage")
    one = renders_copy(rdir, os.path.join(out, "one-stage-renders"), one_stage())
    code, text, meta = packed(one, os.path.join(out, "one-stage-sheets"))
    check("stages 1: packs, exit 0", code == 0, text[-600:])
    if meta is None or full is None:
        return
    im_full, meta_full = full
    check("stages 1: variation_count 1", meta[RES]["variation_count"] == 1, f"{meta[RES]}")
    check("stages 1: size and shift the full sheet's", (meta[RES]["size"], meta[RES]["shift"]) ==
          (meta_full[RES]["size"], meta_full[RES]["shift"]), f"{meta[RES]} vs {meta_full[RES]}")
    im = Image.open(os.path.join(out, "one-stage-sheets", RES + ".png"))
    h = meta_full[RES]["size"][1]
    check("stages 1: the sheet is the full sheet's top row", same_pixels(im, im_full.crop((0, 0, im_full.width, h))),
          f"{im.size}")
    single = renders_copy(rdir, os.path.join(out, "one-cell-renders"), one_stage(1, effect=False))
    code, text, meta = packed(single, os.path.join(out, "one-cell-sheets"))
    ok = code == 0 and meta is not None and list(meta) == [RES, "checks"] and \
        (meta[RES]["frame_count"], meta[RES]["variation_count"]) == (1, 1) and \
        Image.open(os.path.join(out, "one-cell-sheets", RES + ".png")).size == tuple(meta[RES]["size"])
    check("stages 1, variations 1, no effect: a 1 x 1 sheet", ok, text[-600:])


def test_rolloff(rdir, out):
    print("rolloff")
    src = renders_copy(rdir, os.path.join(out, "rolloff-off-renders"), lambda d, _: d.update(rolloff=False))
    sheets = os.path.join(out, "rolloff-off-sheets")
    code, text, meta = packed(src, sheets)
    check("rolloff false: packs, exit 0", code == 0, text[-600:])
    if meta is None:
        return
    check("rolloff false: no rolloff_px", "rolloff_px" not in meta["checks"], f"{list(meta['checks'])}")
    decl = load_decl(src)
    for p in decl["passes"]:
        held_sheet(src, sheets, meta, decl, p, rolled=False)


# ---------------------------------------------------------------- refused

def test_refused(rdir, out):
    print("refused")

    def refused(label, edit, *names, want_meta=False):
        src = renders_copy(rdir, os.path.join(out, f"refused-{label.replace(' ', '-')}-renders"), edit)
        code, text, meta = packed(src, os.path.join(out, f"refused-{label.replace(' ', '-')}-sheets"))
        missing = [n for n in names if n not in text]
        check(f"{label}: refused, naming {', '.join(repr(n) for n in names)}" + (", meta.json written" if want_meta
                                                                                 else ""),
              code != 0 and not missing and (meta is not None or not want_meta),
              f"exit {code}, not naming {missing}: {text[-600:]}")

    def gone(stem):
        return lambda _, dst: os.remove(os.path.join(dst, stem + ".png"))

    def painted(stem, how):
        def edit(_, dst):
            path = os.path.join(dst, stem + ".png")
            im = Image.open(path).convert("RGBA")
            how(im)
            im.save(path)
        return edit
    refused("a resource cell gone", gone("resource-01-02"), "resource-01-02.png")
    refused("an effect cell gone", gone("resource-effect-02-03"), "resource-effect-02-03.png")

    def small(_, dst):
        path = os.path.join(dst, "resource-00-01.png")
        Image.open(path).crop((0, 0, 256, 256)).save(path)
    refused("a cell on the wrong canvas", small, "resource-00-01.png", "canvas")
    refused("a resource cell emptied", painted("resource-02-01", lambda im: im.putalpha(0)),
            "resource-02-01.png", "is empty")

    def dark(d, dst):
        for s, v in contract.cells(d):
            path = os.path.join(dst, contract.cell(FX, s, v) + ".png")
            Image.new("RGBA", Image.open(path).size).save(path)
    refused("every effect cell dark", dark, "every cell")
    refused("a block on the canvas's edge", painted("resource-00-03", lambda im: ImageDraw.Draw(im).rectangle(
        (0, 150, 6, 170), fill=(90, 80, 70, 255))), "canvas's edge", "resource-00-03", want_meta=True)
    refused("a white square in an effect cell", painted("resource-effect-01-02", lambda im: ImageDraw.Draw(im).rectangle(
        (150, 150, 157, 157), fill=(255, 255, 255, 255))), "clipped to white", "resource-effect-01-02", want_meta=True)

    def wide(d, dst):
        for p in d["passes"]:
            for s in range(3):
                for v in range(4, 30):
                    os.symlink(contract.cell(p["name"], s, 0) + ".png", os.path.join(dst, contract.cell(p["name"], s, v)
                                                                                    + ".png"))
        d["passes"][0]["variations"] = 30
    refused("variations 30", wide, "does not wrap")
    one_dark = renders_copy(rdir, os.path.join(out, "one-effect-cell-dark-renders"), painted(
        "resource-effect-02-02", lambda im: im.putalpha(0)))
    code, text, _ = packed(one_dark, os.path.join(out, "one-effect-cell-dark-sheets"))
    check("one effect cell dark: accepted", code == 0, text[-600:])


# ---------------------------------------------------------------- identity

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


def test_identity(out, rev, renders):
    print("identity")
    if not rev:
        print("  (no --baseline: skipped)")
        return
    base = baseline_tools(rev, out)
    for i, r in enumerate(renders):
        rdir = os.path.join(r, "renders")
        label = f"{i + 1} {os.path.basename(os.path.normpath(r))}"
        results = {}
        for who, tools in (("baseline", base), ("this tree", TOOLS)):
            dst = os.path.join(out, f"identity-{i + 1}-{'baseline' if tools == base else 'tree'}")
            code, text, _ = packed(rdir, dst, tools)
            plates = run([sys.executable, os.path.join(tools, "contract.py"), "plates", rdir])
            results[who] = (code, text, dst, plates)
        (bc, bt, bd, bp), (tc, tt, td, tp) = results["baseline"], results["this tree"]
        check(f"{label}: pack.py exits as the baseline's ({bc})", bc == tc, f"baseline {bc}, this tree {tc}: {tt[-400:]}")
        ok, why = same_dirs(bd, td)
        check(f"{label}: pack.py's every file byte for byte as the baseline's ({len(files(bd))} files)", ok, why)
        check(f"{label}: contract.py plates as the baseline's", bp == tp, f"{bp} vs {tp}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("resource")
    ap.add_argument("--baseline", metavar="GIT_REV")
    ap.add_argument("--renders", nargs="+", default=[], metavar="RENDER_OUT")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.renders and not a.baseline:
        ap.error("--renders goes with --baseline")
    out = a.out or os.path.join(a.resource, "resource-test")
    os.makedirs(out, exist_ok=True)
    rdir = os.path.join(a.resource, "renders")
    test_contract(load_decl(rdir))
    full = test_sheet(rdir, out)
    test_one_stage(rdir, out, full)
    test_rolloff(rdir, out)
    test_refused(rdir, out)
    test_identity(out, a.baseline, a.renders)
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
