#!/usr/bin/env python3
"""The remnants pass (contract.py, pack.py, preview.py, measure.py) held to its docs.

  python3 tools/blender/test/test_remnants.py <box-out> [--baseline <git-rev>] [--also <render-out> ...]
                                              [--no-catcher <render-dir> ...] [--out <dir>]

<box-out> is render.sh's <out-dir> for the test box (test/box.py), whose wreck is its remnants
pass, and whose wreck-bare-<direction>.png renders are the same wreck with no catcher. Nothing
is rendered here: copies of its renders, with render.json edited, are packed by pack.py and
drawn by preview.py. --baseline names a commit from before the remnants pass (master
8740c38): its contract.py, pack.py and preview.py, taken out with `git show`, are run beside
this tree's on renders that declare no remnants -- the box's with its remnants pass taken out,
and each --also <render-out> (any render.sh output, test/radiant_box.py's say) -- and every file
they write must be byte for byte the same. --no-catcher names other directories holding a
wreck-<direction>.png for each of the box's directions rendered with no catcher (a reviewer's,
say): each must be refused as the box's own wreck-bare renders are. Everything is written
under --out (default <box-out>/remnants-test) and kept.

Exits 0 when every case below comes out as listed, 1 naming those that do not.

  contract   the box's declaration accepted; refused, each naming its field: two remnants passes
             (passes), a canvas on a plate (passes[0].canvas), a canvas of [0, 256] or a string
             on the remnants pass, a remnants pass with no sheet; a remnants sheet that is another
             sheet's name in one of the model's directions -- "base-north", "lamp-west", the
             animation's "slider-east", "base-vertical" in a horizontal-vertical model -- or
             "base" itself, or "checks" (passes[k].sheet); "base-vertical" in the four-direction
             box accepted. pack.py on renders whose remnants sheet is "base-north": non-zero,
             naming the field, and no sheet written over. remnant_rows: four -> north,
             east, south, west; horizontal-vertical -> vertical, horizontal, vertical,
             horizontal; one -> one row.
  sheet      the box packed: meta.json's remnants entry has direction_count 4, line_length 1,
             rows north, east, south, west, kind and final_render_layer "remnants", and no
             entry per direction; remnants.png is size[0] x 4 size[1]; each row is that
             direction's render, cleaned of haze below NOISE, cropped to the box its size and
             shift give on the wreck's 256 px canvas, pixel for pixel; that box holds every
             direction's wreck, each side within 1 px (the rim) of one of them.
  checks     in every direction remnants_shadow_px at least SHADOW_MIN_PX and a share of at least
             SHADOW_SHARE (pack.py), and the sheet's row has as many near-black part-transparent
             pixels; remnants_edge_px 0; remnants_reach_tiles' debris past all four footprint
             edges (the box's thrown pieces) and "all" at least as far.
  never cut  cut [E, W, S]: remnants.png byte for byte as uncut, and cut_px names no wreck
             render.
  refused    the box's wreck rendered with no catcher (wreck-bare) in every direction: pack.py exits
             non-zero naming "no shadow baked in" in all four, with meta.json written, every
             share under SHADOW_SHARE; in east alone: refused naming east and no other; each
             --no-catcher directory likewise in all four; a block painted on the
             canvas's edge of one: non-zero, naming the canvas's edge; a wreck render at the
             model's canvas (192) instead of its own (256): non-zero, naming the canvas.
  layouts    the box's renders as a horizontal-vertical model (north as vertical, east as
             horizontal): four rows, vertical, horizontal, vertical, horizontal, rows 1 and 3
             and rows 2 and 4 the same bytes; as a one-direction model (north alone):
             direction_count 1, one row, size the sheet's own; measure.py on that one: no layer
             is the remnants sheet, and it is listed as ignored; on the box's sheets directory
             alone (no render.json, four directions): listed as ignored in every direction.
  identity   the box with its remnants pass taken out (and its wreck renders gone): every sheet
             and meta.json as the box's own packed with it, less remnants.png, its meta.json
             entry and its remnants_* checks. preview.py with remnants: three panels a row
             (idle, working, wreck), 256 + 2 x 8 px square; without: two, of the 192 canvas;
             Model.wreck None without it. With --baseline: pack.py's output (sheets and
             meta.json), preview.py's sheet and its --gif of each paint animation (every run
             exiting 0), byte for byte as the baseline's, on the box without remnants and on
             every --also.
"""
import argparse
import copy
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import contract  # noqa: E402
import measure  # noqa: E402
import pack  # noqa: E402
import preview  # noqa: E402

FAILED = []
NO_CATCHER = []         # --no-catcher directories
WRECK = "wreck"         # box.py's remnants pass and its sheet
SHEET = "remnants"


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


def same_bytes(a, b):
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def files(d):
    return sorted(f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)))


def same_dirs(a, b, skip=()):
    """Whether two directories hold the same files, byte for byte (but those in skip): (ok, why)."""
    fa, fb = [f for f in files(a) if f not in skip], [f for f in files(b) if f not in skip]
    if fa != fb:
        return False, f"files differ: {sorted(set(fa) ^ set(fb))}"
    bad = [f for f in fa if not same_bytes(os.path.join(a, f), os.path.join(b, f))]
    return not bad, f"differ: {bad}"


def differs(a, b):
    return ImageChops.difference(a.convert("RGBA"), b.convert("RGBA")).getbbox(alpha_only=False) is not None


def checks_of(meta, d):
    return meta["checks"][d] if d else meta["checks"]


def dirs_of(decl):
    return [d for d, _ in contract.DIRECTIONS[decl["directions"]]]


def without_remnants(decl, dst):
    """The declaration (and renders) of the model as it was before it had a wreck."""
    for d in dirs_of(decl):
        os.remove(os.path.join(dst, contract.named(WRECK, d) + ".png"))
    decl["passes"] = [p for p in decl["passes"] if p["kind"] != "remnants"]


# ---------------------------------------------------------------- contract

def test_contract(decl0):
    print("contract")

    def case(label, edit, want_field=None):
        d = copy.deepcopy(decl0)
        edit(d)
        try:
            contract.validate(d, "test")
            check(label, want_field is None, "accepted, but should be refused naming " + str(want_field))
        except contract.ContractError as e:
            check(label, want_field is not None and f": {want_field}:" in str(e),
                  f"refused: {e}" if want_field is None else f"refused, not naming {want_field}: {e}")
    k = next(i for i, p in enumerate(decl0["passes"]) if p["kind"] == "remnants")
    plate = next(i for i, p in enumerate(decl0["passes"]) if p["kind"] == "plate")

    def wreck(**kw):
        return lambda d: d["passes"][k].update(**kw)
    case("the box's declaration accepted", lambda d: None)
    case("two remnants passes refused",
         lambda d: d["passes"].append(dict(name="wreck2", kind="remnants", sheet="remnants2")), "passes")
    case("a canvas on a plate refused", lambda d: d["passes"][plate].update(canvas=[256, 256]),
         f"passes[{plate}].canvas")
    case("a remnants canvas of [0, 256] refused", wreck(canvas=[0, 256]), f"passes[{k}].canvas")
    case("a remnants canvas of a string refused", wreck(canvas="256x256"), f"passes[{k}].canvas")
    case("a remnants pass with no sheet refused", lambda d: d["passes"][k].pop("sheet"), f"passes[{k}].sheet")
    case("a remnants pass on the model's canvas accepted", lambda d: d["passes"][k].pop("canvas"))
    for name in ("base-north", "lamp-west", "slider-east", "base", "checks"):
        case(f"a remnants sheet {name!r} refused", wreck(sheet=name), f"passes[{k}].sheet")
    case("a remnants sheet 'base-vertical' accepted in a four-direction model", wreck(sheet="base-vertical"))
    case("a remnants sheet 'base-vertical' refused in a horizontal-vertical model",
         lambda d: (d.update(directions="horizontal-vertical"), d["passes"][k].update(sheet="base-vertical")),
         f"passes[{k}].sheet")
    for dirs, want in (("four", ["north", "east", "south", "west"]),
                       ("horizontal-vertical", ["vertical", "horizontal", "vertical", "horizontal"]), ("one", [""])):
        got = contract.remnant_rows(dict(directions=dirs))
        check(f"remnant_rows {dirs}: {want}", got == want, f"{got}")


# ---------------------------------------------------------------- the sheet and its checks

def row_box(meta, decl, p):
    """The box on the wreck's canvas that meta.json's size and shift say every row was cut from."""
    w, h = meta[SHEET]["size"]
    sx, sy = meta[SHEET]["shift"]
    cw, ch = contract.canvas_of(decl, p)
    ppt = decl["rig"]["px_per_tile"]
    x0, y0 = round(cw / 2 + sx * ppt - w / 2), round(ch / 2 + sy * ppt - h / 2)
    return x0, y0, x0 + w, y0 + h


def near_black_part(im):
    return sum(1 for px in im.get_flattened_data() if 0 < px[3] < 255 and max(px[:3]) <= pack.SHADOW_RGB)


def test_sheet(box, out):
    print("sheet and checks")
    src = os.path.join(box, "renders")
    decl = load_decl(src)
    p = next(q for q in decl["passes"] if q["kind"] == "remnants")
    code, text, meta = packed(renders_copy(src, os.path.join(out, "own")), os.path.join(out, "own-sheets"))
    check("the box packs: exit 0", code == 0, text[-400:])
    if meta is None:
        return None
    m = meta.get(SHEET, {})
    want = dict(direction_count=4, line_length=1, rows=["north", "east", "south", "west"], kind="remnants",
                final_render_layer="remnants")
    check("meta.json remnants: direction_count 4, line_length 1, rows N E S W, kind and render layer",
          {k: m.get(k) for k in want} == want, f"{m}")
    check("meta.json: no remnants entry per direction",
          not any(k.startswith(SHEET + "-") for k in meta), f"{[k for k in meta if k.startswith(SHEET)]}")
    sheet = Image.open(os.path.join(out, "own-sheets", SHEET + ".png")).convert("RGBA")
    w, h = m["size"]
    check(f"remnants.png is {w} x 4 x {h}", sheet.size == (w, 4 * h), f"{sheet.size}")
    u = row_box(meta, decl, p)
    cleaned = {d: pack.clean(Image.open(os.path.join(src, contract.named(WRECK, d) + ".png")).convert("RGBA"))
               for d in dirs_of(decl)}
    for i, d in enumerate(m["rows"]):
        row = sheet.crop((0, i * h, w, (i + 1) * h))
        check(f"row {i + 1} ({d}): its render cleaned, cut at size and shift, pixel for pixel",
              not differs(row, cleaned[d].crop(u)))
    bbs = [im.getchannel("A").getbbox() for im in cleaned.values()]
    holds = all(u[0] < b[0] and u[1] < b[1] and b[2] < u[2] and b[3] < u[3] for b in bbs)
    tight = (min(b[0] for b in bbs) - u[0], min(b[1] for b in bbs) - u[1],
             u[2] - max(b[2] for b in bbs), u[3] - max(b[3] for b in bbs))
    check("the one box holds every direction's wreck, each side 1 px (the rim) from one",
          holds and tight == (1, 1, 1, 1), f"holds {holds}, margins {tight}")
    for i, d in enumerate(m["rows"]):
        c = checks_of(meta, d)
        got = c[f"{SHEET}_shadow_px"][0]
        n, share = got["px"], got["share"]
        row = sheet.crop((0, i * h, w, (i + 1) * h))
        check(f"{d}: shadow baked in, remnants_shadow_px {n} (share {share}) over the floor and as many in its row",
              n >= pack.SHADOW_MIN_PX and share >= pack.SHADOW_SHARE and near_black_part(row) == n,
              f"row has {near_black_part(row)}")
        check(f"{d}: remnants_edge_px 0", c[f"{SHEET}_edge_px"][0] == 0, f"{c[f'{SHEET}_edge_px'][0]}")
        r = c[f"{SHEET}_reach_tiles"][0]
        check(f"{d}: debris past all four footprint edges, everything at least as far",
              all(r["debris"][f] > 0 and r["all"][f] >= r["debris"][f] for f in "NESW"), f"{r}")
    return meta


def test_cut(box, out):
    print("never cut")
    src = os.path.join(box, "renders")
    rd = renders_copy(src, os.path.join(out, "cut"), lambda d, _: d.update(cut=["E", "W", "S"]))
    code, text, meta = packed(rd, os.path.join(out, "cut-sheets"))
    check("cut [E, W, S]: exit 0", code == 0, text[-400:])
    check("cut [E, W, S]: remnants.png byte for byte as uncut",
          code == 0 and same_bytes(os.path.join(out, "cut-sheets", SHEET + ".png"),
                                   os.path.join(out, "own-sheets", SHEET + ".png")))
    named = [k for d in dirs_of(load_decl(src)) for k in checks_of(meta, d).get("cut_px", [{}])[0]
             if k.startswith(WRECK)] if meta else ["(no meta.json)"]
    check("cut [E, W, S]: cut_px names no wreck render", not named, f"{named}")


def test_refused(box, out):
    print("refused")
    src = os.path.join(box, "renders")
    decl = load_decl(src)
    p = next(q for q in decl["passes"] if q["kind"] == "remnants")

    dirs = dirs_of(decl)

    def bare(from_dir, stem, only=None):
        def edit(_, dst):
            for d in only or dirs:
                shutil.copy(os.path.join(from_dir, contract.named(stem, d) + ".png"),
                            os.path.join(dst, contract.named(WRECK, d) + ".png"))
        return edit
    for label, from_dir, stem in [("the box's wreck-bare", src, "wreck-bare")] + \
            [(f"--no-catcher {nc}", nc, WRECK) for nc in NO_CATCHER]:
        tag = "no-catcher" if from_dir == src else f"no-catcher-{NO_CATCHER.index(from_dir) + 1}"
        code, text, meta = packed(renders_copy(src, os.path.join(out, tag), bare(from_dir, stem)),
                                  os.path.join(out, tag + "-sheets"))
        shares = {d: checks_of(meta, d)[f"{SHEET}_shadow_px"][0] for d in dirs} if meta else {}
        check(f"{label}, no catcher in every direction: refused in all four, meta.json written, every share under "
              f"{pack.SHADOW_SHARE:g}",
              code != 0 and all(f"direction {d}: no shadow baked in" in text for d in dirs) and meta is not None
              and all(v["share"] < pack.SHADOW_SHARE for v in shares.values()),
              f"exit {code}, {shares}: {text[-400:]}")
    code, text, _ = packed(renders_copy(src, os.path.join(out, "no-catcher-east"), bare(src, "wreck-bare", ["east"])),
                           os.path.join(out, "no-catcher-east-sheets"))
    check("no catcher in east alone: refused naming east and no other",
          code != 0 and "direction east: no shadow baked in" in text
          and not any(f"direction {d}: no shadow" in text for d in dirs if d != "east"), f"exit {code}: {text[-400:]}")

    def on_edge(_, dst):
        f = os.path.join(dst, contract.named(WRECK, "south") + ".png")
        im = Image.open(f).convert("RGBA")
        ImageDraw.Draw(im).rectangle((0, 100, 5, 110), fill=(120, 110, 100, 255))
        im.save(f)
    code, text, _ = packed(renders_copy(src, os.path.join(out, "on-edge"), on_edge),
                           os.path.join(out, "on-edge-sheets"))
    check("a block on the canvas's edge: refused, naming the edge",
          code != 0 and "canvas's edge" in text and "direction south" in text, f"exit {code}: {text[-300:]}")

    collide_dir = renders_copy(src, os.path.join(out, "sheet-base-north"),
                               lambda d, _: next(q for q in d["passes"] if q["kind"] == "remnants").update(
                                   sheet="base-north"))
    code, text, _ = packed(collide_dir, os.path.join(out, "sheet-base-north-sheets"))
    written = os.path.isdir(os.path.join(out, "sheet-base-north-sheets")) and \
        os.listdir(os.path.join(out, "sheet-base-north-sheets"))
    check("a remnants sheet 'base-north': pack.py refuses it, naming the field, writing nothing",
          code != 0 and ".sheet" in text and "base-north" in text and not written, f"exit {code}: {text[-300:]}")

    def small(_, dst):
        f = os.path.join(dst, contract.named(WRECK, "north") + ".png")
        Image.open(f).convert("RGBA").crop((32, 32, 224, 224)).save(f)
    code, text, _ = packed(renders_copy(src, os.path.join(out, "small"), small), os.path.join(out, "small-sheets"))
    cw, ch = contract.canvas_of(decl, p)
    check(f"a wreck render on the model's canvas, not its own: refused, naming {cw}x{ch}",
          code != 0 and f"{cw}x{ch} canvas" in text, f"exit {code}: {text[-300:]}")


# ---------------------------------------------------------------- other layouts

def as_directions(src, dst, directions, names):
    """A copy of the box's renders as a model of other directions: names {new: box direction}."""
    decl = load_decl(src)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    stems = [p["name"] for p in decl["passes"]] + [contract.frame(a["name"], f) for a in decl["animations"]
                                                   for f in range(a["frames"])]
    for new, old in names.items():
        for stem in stems:
            shutil.copy(os.path.join(src, contract.named(stem, old) + ".png"),
                        os.path.join(dst, contract.named(stem, new) + ".png"))
    decl["directions"] = directions
    save_decl(dst, decl)
    return dst


def test_layouts(box, out):
    print("layouts")
    src = os.path.join(box, "renders")
    hv = as_directions(src, os.path.join(out, "hv"), "horizontal-vertical", dict(vertical="north", horizontal="east"))
    code, text, meta = packed(hv, os.path.join(out, "hv-sheets"))
    check("horizontal-vertical: exit 0", code == 0, text[-400:])
    if meta:
        m = meta[SHEET]
        w, h = m["size"]
        sheet = Image.open(os.path.join(out, "hv-sheets", SHEET + ".png")).convert("RGBA")
        rows = [sheet.crop((0, i * h, w, (i + 1) * h)) for i in range(4)]
        check("horizontal-vertical: four rows, vertical, horizontal, vertical, horizontal",
              m["direction_count"] == 4 and m["rows"] == ["vertical", "horizontal"] * 2 and sheet.size == (w, 4 * h),
              f"{m}, {sheet.size}")
        check("horizontal-vertical: rows 1 and 3, 2 and 4 the same, 1 and 2 not",
              rows[0].tobytes() == rows[2].tobytes() and rows[1].tobytes() == rows[3].tobytes()
              and differs(rows[0], rows[1]))

    one = os.path.join(out, "one")
    as_directions(src, os.path.join(one, "renders"), "one", {"": "north"})
    code, text, meta = packed(os.path.join(one, "renders"), os.path.join(one, "sheets"))
    check("one direction: exit 0", code == 0, text[-400:])
    if meta:
        m = meta[SHEET]
        sheet = Image.open(os.path.join(one, "sheets", SHEET + ".png"))
        check("one direction: direction_count 1, one row, the sheet its size",
              m["direction_count"] == 1 and m["rows"] == [""] and list(sheet.size) == list(m["size"]),
              f"{m}, {sheet.size}")
        try:
            s = measure.Source(one)
            stems = [lay.stem for lay in s.layers[""]]
            check("measure.py, one direction: no layer is the remnants sheet; listed as ignored",
                  SHEET not in stems and any(i.startswith(SHEET + " (remnants") for i in s.ignored[""]),
                  f"layers {stems}, ignored {s.ignored['']}")
        except measure.Usage as e:
            check("measure.py, one direction: reads it", False, str(e))

    alone = os.path.join(out, "sheets-alone", "sheets")       # no renders/ beside it: no render.json
    if os.path.exists(os.path.dirname(alone)):
        shutil.rmtree(os.path.dirname(alone))
    shutil.copytree(os.path.join(out, "own-sheets"), alone)
    try:
        s = measure.Source(alone, footprint=[2, 2])
        dirs = dirs_of(load_decl(src))
        listed = {d: any(i.startswith(SHEET + " (remnants") for i in s.ignored[d]) for d in dirs}
        stems = [lay.stem for d in dirs for lay in s.layers[d]]
        check("measure.py, the sheets alone (four directions): the remnants sheet listed as ignored in each, no layer",
              all(listed.values()) and SHEET not in stems, f"{listed}, layers {stems}")
    except measure.Usage as e:
        check("measure.py, the sheets alone: reads them", False, str(e))


# ---------------------------------------------------------------- identity

def baseline_tools(rev, out):
    """contract.py, pack.py and preview.py as they stood at rev, in a directory of their own."""
    d = os.path.join(out, f"baseline-{rev}")
    os.makedirs(d, exist_ok=True)
    top = subprocess.run(["git", "-C", TOOLS, "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                         check=True).stdout.strip()
    rel = os.path.relpath(TOOLS, top)
    for f in ("contract.py", "pack.py", "preview.py"):
        body = subprocess.run(["git", "-C", top, "show", f"{rev}:{rel}/{f}"], capture_output=True, check=True).stdout
        with open(os.path.join(d, f), "wb") as fh:
            fh.write(body)
    return d


def against_baseline(label, rdir, out, base):
    """pack.py and preview.py (its sheet and a GIF of each paint animation) of this tree and of the
    baseline on one render directory: byte for byte."""
    mine, theirs = os.path.join(out, f"{label}-mine"), os.path.join(out, f"{label}-base")
    for tools, o in ((TOOLS, mine), (base, theirs)):
        code, text, _ = packed(rdir, os.path.join(o, "sheets"), tools)
        if code != 0:
            check(f"{label}: pack.py ({'this tree' if tools == TOOLS else 'baseline'}) exits 0", False,
                  text[-300:])
            return
        who = "this tree" if tools == TOOLS else "baseline"
        code, text = run([sys.executable, os.path.join(tools, "preview.py"), rdir, os.path.join(o, "preview.png")])
        check(f"{label}: preview.py ({who}) exits 0", code == 0, text[-300:])
        for a in load_decl(rdir)["animations"]:
            if a.get("kind", "paint") == "paint":
                code, text = run([sys.executable, os.path.join(tools, "preview.py"), rdir,
                                  os.path.join(o, f"{a['name']}.gif"), "--gif", a["name"], "--speed", "0.25"])
                check(f"{label}: preview.py --gif {a['name']} ({who}) exits 0", code == 0, text[-300:])
    ok, why = same_dirs(os.path.join(mine, "sheets"), os.path.join(theirs, "sheets"))
    n = len(files(os.path.join(mine, "sheets")))
    check(f"{label}: pack.py's sheets and meta.json byte for byte as the baseline's ({n} files)", ok, why)
    ok, why = same_dirs(mine, theirs)
    check(f"{label}: preview.py's sheet and GIFs byte for byte as the baseline's ({', '.join(files(mine))})", ok, why)


def test_identity(box, out, meta_with, rev, also):
    print("identity")
    src = os.path.join(box, "renders")
    bare = renders_copy(src, os.path.join(out, "bare"), without_remnants)
    code, text, meta = packed(bare, os.path.join(out, "bare-sheets"))
    check("without remnants: exit 0", code == 0, text[-400:])
    ok, why = same_dirs(os.path.join(out, "bare-sheets"), os.path.join(out, "own-sheets"),
                        skip=("meta.json", SHEET + ".png"))
    check("without remnants: every sheet byte for byte as the box's own", ok, why)
    if meta and meta_with:
        stripped = copy.deepcopy(meta_with)
        stripped.pop(SHEET)
        for d in dirs_of(load_decl(src)):
            c = checks_of(stripped, d)
            for k in [k for k in c if k.startswith(SHEET + "_")]:
                c.pop(k)
        check("without remnants: meta.json as the box's own less its remnants entry and checks", stripped == meta)
        check("without remnants: meta.json keeps its order", list(stripped) == list(meta))

    decl = load_decl(src)
    p = next(q for q in decl["passes"] if q["kind"] == "remnants")
    cw = contract.canvas_of(decl, p)[0]
    for label, rdir, n, side in (("with", src, 3, cw), ("without", bare, 2, decl["canvas"][0])):
        o = os.path.join(out, f"preview-{label}.png")
        code, text = run([sys.executable, os.path.join(TOOLS, "preview.py"), rdir, o])
        pw = side + 2 * preview.PAD
        want = (preview.PAD + n * (pw + preview.PAD), preview.PAD + 4 * (pw + preview.LABEL + preview.PAD))
        got = Image.open(o).size if code == 0 else None
        check(f"preview {label} remnants: {n} panels a row of {pw} px, {want[0]}x{want[1]}", got == want,
              f"exit {code}, {got}: {text[-200:]}")
    check("preview: Model.wreck None without remnants", preview.Model(bare).wreck("north") is None)
    wreck = preview.Model(src).wreck("north")
    check("preview: Model.wreck draws the wreck on the ground, at its own canvas",
          wreck is not None and wreck.size == tuple(contract.canvas_of(decl, p))
          and differs(wreck, Image.new("RGBA", wreck.size, preview.GROUND)))

    if rev:
        base = baseline_tools(rev, out)
        against_baseline("box without remnants", bare, out, base)
        for i, a in enumerate(also):
            rdir = os.path.join(a, "renders")
            if any(q["kind"] == "remnants" for q in load_decl(rdir)["passes"]):
                check(f"--also {a}: declares no remnants", False, "it does: not a model from before them")
                continue
            against_baseline(f"also-{i + 1} {os.path.basename(os.path.normpath(a))}", rdir, out, base)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("box")
    ap.add_argument("--baseline", metavar="GIT_REV")
    ap.add_argument("--also", nargs="+", default=[], metavar="RENDER_OUT")
    ap.add_argument("--no-catcher", nargs="+", default=[], metavar="RENDER_DIR")
    ap.add_argument("--out")
    a = ap.parse_args()
    NO_CATCHER.extend(os.path.abspath(d) for d in a.no_catcher)
    if a.also and not a.baseline:
        ap.error("--also goes with --baseline")
    out = a.out or os.path.join(a.box, "remnants-test")
    os.makedirs(out, exist_ok=True)
    test_contract(load_decl(os.path.join(a.box, "renders")))
    meta = test_sheet(a.box, out)
    test_cut(a.box, out)
    test_refused(a.box, out)
    test_layouts(a.box, out)
    test_identity(a.box, out, meta, a.baseline, a.also)
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
