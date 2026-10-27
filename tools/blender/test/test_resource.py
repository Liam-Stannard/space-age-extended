#!/usr/bin/env python3
"""The resource model (contract.py's resource and effect passes, pack.py's resource sheets) held to its docs.

  python3 tools/blender/test/test_resource.py <resource-out> [--baseline <git-rev> [--renders <render-out> ...]]
                                              [--out <dir>]

<resource-out> is render.sh's <out-dir> for test/resource_box.py: a target disc in three stages of
four variations, with an effect over it. Nothing is rendered here: copies of its renders, with
render.json edited, are packed by pack.py. --baseline names a commit with T02's resource model,
from before its animations (vents 15d2ab7; one before the resource model, cd10283, cannot pack the
fixture without animations, so its identity cases fail), or a later one a change is held to: its
tools (BASELINE_FILES), taken out with `git show`, are run beside
this tree's on every --renders <render-out> (any render.sh output of a building, test/box.py's
and test/radiant_box.py's say, or a real model's), and every file they write must be byte for
byte the same; so must `contract.py plates`. Everything is written under --out (default
<resource-out>/resource-test) and kept.

Exits 0 when every case below comes out as listed, 1 naming those that do not.

  contract   the fixture's declaration accepted, its animations (a cycle and a glow over it) and no
             still pass with them; cell("vent", 2, 3) is "vent-02-03"; cells() runs
             row by row from stage 0. Refused, each naming its field: stages 0, stages missing,
             variations "4" (passes[0].stages / .variations); two resource passes, two effect
             passes, an effect pass alone (passes); a plate beside the resource (passes[k].kind);
             a building's declaration (a plate, four directions; accepted alone) with an effect
             added (passes); an effect over a name not the
             resource's, an effect with stages of its own, an effect with a bloom of [[0, 1]]
             (passes[1].over / .stages / .bloom); a sheet "checks" (passes[0].sheet); directions
             "four", a port, a cut, ports_turn (each its own key). A flow paint animation alone,
             no still: accepted. Refused, naming animations[0]'s field: a turn and a slide
             (.motion), a light (.kind), a working one (.working), one named "resource-00", whose
             frames are the resource's cells' (.name). A building's paint animation with no still
             pass: still refused (passes).
  sheet      the fixture packed, exit 0: meta.json's keys resource, resource-effect, bubble,
             bubble-light, checks in that order; each sheet's entry frame_count 4, variation_count 3, line_length 4, its kind;
             each png 4 x 3 of its size; each cell, pixel for pixel, its render as pack.py takes
             it (cleaned below NOISE; the effect's turned to light with its bloom), rolled off and
             cropped to the box its size and shift give on the canvas; that box holds every cell,
             each side within 1 px (the rim) of one of them; stage 0's row holds more pixels than
             stage 1's and stage 1's than stage 2's (the fixture shrinks as it depletes). Each
             animation's entry frames 4, line_length 4, animation_speed 0.2 (the glow its paint
             layer's), kind "glow" for bubble-light and none for bubble; its png 4 frames of its
             size; each frame, pixel for pixel, its render as packed (cleaned; the glow turned to
             light with its bloom), rolled off and cropped to its box.
  checks     resource_edge_px 0, resource-effect_edge_px 0, resource-effect_white_px 0,
             resource_reach_tiles within 0.05 of 0.9 past every edge (the cyan ring, 2.4 tiles, less
             the 3 x 3 footprint's 1.5), rolloff_px naming all four sheets; bubble_cycle 4;
             bubble-light_white_px, _clipped_px and _edge_px 0, _frames [4, 4]; contract.py plates
             lists the four stage-0 cells. glow_checks over a list of plates takes the most of
             them: a light that whitens nothing over a dark plate and one pixel over a pale one
             counts 1 over both, 0 over the dark alone.
  one stage  the renders with stages 1 (the other stages' renders gone): variation_count 1, and the
             sheet the full sheet's top row, size and shift the same (stage 0 is the widest); with
             stages 1 and variations 1 and no effect or animations: a 1 x 1 sheet.
  rolloff    rolloff false: no rolloff_px, and each sheet, the animations' too, as the renders
             cropped, unrolled.
  refused    each exits non-zero naming what it names: a resource cell gone (resource-01-02.png);
             an effect cell gone (resource-effect-02-03.png); a cell on the wrong canvas (the
             canvas); a resource cell emptied (resource-02-01.png, "is empty"); every effect cell
             dark ("every cell"); a block on the canvas's edge of resource-00-03 ("canvas's edge",
             that cell, meta.json written); a white square in resource-effect-01-02 ("clipped to
             white", that cell); variations 30 ("does not wrap"); an animation frame gone
             (bubble-02.png); a white square in a glow animation's frame ("bubble-light", "white",
             meta.json written). One effect cell dark: accepted.
  effect under  every effect cell made a light (no bloom) that lifts its resource cell to 240 in
             every channel wherever the cell is opaque: bubble-light's light, added over bubble on
             each cell alone, whitens nothing, and with the effect's light under it some pixels;
             bubble-light_clipped_px is that count (pack.py: the effect's light added under a glow
             animation, the cell drawn over the bright ground, pack.lit_readings' readings, the light
             added to it, then the paint over that), the pack refused naming bubble-light, meta.json
             written; the effect's own white_px 0.
  effect exact  pack.lit_cell, lit_readings and glow_checks on a 4 x 4 cell, pixel by pixel (vents
             T02d, T02e), worked by hand over pack.GROUND (204, 210, 234), snow-flat's: a clear pixel
             reads the ground, lit 20 the ground + 20; the reviewer's case, a clear pixel lit (20, 20,
             20) under paint (50, 0, 0, 128), is within a level of (136.7, 114.5, 126.5), and a glow
             of (125, 150, 150) whitens it, (60, 60, 60) does not; an opaque (100, 100, 100) pixel lit
             100, a glow of 50, whitens; a clear pixel lit 20, a glow of 30, whitens (254, 255, 255);
             a clear unlit pixel, a glow of 40, does not (red 244), of 41 does; a pixel cleaned clear
             with its colour (240, 240, 240) kept, a glow of 10, does not (the ground). Partly
             transparent: (100, 100, 100, 128) exact (151.8, 154.8, 166.7), a glow of 95 whitens it
             exact, not at full colour; (0, 0, 0, 64), a glow of 100, the same; (240, 240, 240, 128)
             exact (222.1, 225.1, 237.0), a glow of 6 whitens it at full colour alone. g_clipped_px
             exact 6, full colour 5, over lit_readings 6; that pale pixel alone: exact 0, over
             lit_readings 1; an opaque cell one reading. Over black (the T02d rule) only (3, 1) and
             (3, 0) whiten: the reviewer's pixel, (2, 2) and (0, 2) clip over the ground alone.
  preview    preview.py on the renders, exit 0: a sheet of a row a stage, each with its night row
             under it, each of the four variations' panels and then the four with the effect, the
             panel size the canvas and its pads; every effect panel at least its plain panel's every
             channel (the light is added) and brighter somewhere, by day and at night; every night
             panel's ground preview.NIGHT times the day's, the panel nowhere brighter than its day
             one and nowhere under the day times NIGHT (less a level), and over that by 20 or more
             somewhere (a glow added at full strength); --adopted with one picture adds a panel to
             the top row alone, its place in the night row under it empty, with two is refused;
             --gif bubble --speed 0.2: 4 frames, the four stage-0 cells side by side.
  measure    measure.py on the fixture (its packed sheets and its render.json), exit 0: every cell
             "SS-VV" in order, each with the cell as the plate, the effect as a glow, bubble an
             anim and bubble-light a glow-anim; motion over 4 frames; glow figures for the effect
             and bubble-light; pack_checks meta.json's flat checks; no joins; cell 00-00's coverage
             past every edge of the footprint within 0.05 of pack.py's reach, and stage 2's extent
             less than stage 0's. --connection refused (exit 2). The sheets alone, --footprint 3x3:
             exit 0 and every cell's figures the same. --vanilla crude-oil --vanilla fluorine-vent:
             exit 0, both references' figures in every cell and ours as without them; crude oil's
             in cell 00-00 its variation 0, in 02-01 its variation 1 (another picture), a 3 x 3
             footprint; each reference's figures the same in 00-00 and 02-00, others in 01-01.
  finish     finish.py on the four stage-0 cells: exit 0, each measured; on a 6 px square: exit 0,
             "too thin"; on a flat square: exit 0, ratio "n/a".
  tonal      tonal.py on the four stage-0 cells: exit 0, each measured; on an empty cell, one all at
             alpha 200, and a stage-0 cell in one run: exit 0, "no opaque pixel" for the first two,
             the third measured.
  identity   with --baseline: on every --renders, on the fixture with its animations dropped
             (a resource model as T02 packed it) and on it declared four ways (refused by both,
             before either writes a file), pack.py's every output file (sheets and meta.json)
             and `contract.py plates`' output byte for byte as the baseline's, or both refusing
             alike: the same exit and message, the same files (none) written. Where both pack, the
             same of finish.py's output on the plates and, for a building (the baseline's preview.py
             and measure.py had no resource model), of preview.py's sheet (the --gif of its first
             paint animation too) and measure.py's every file (measures.json and its sheets; exit
             as the baseline's).
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
import pack  # noqa: E402

FAILED = []
RES, FX = "resource", "resource-effect"         # resource_box.py's passes, and their sheets
BUBBLE, LIGHT = "bubble", "bubble-light"        # its animations: a cycle and the glow over it


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
    """The files in d, by name; none when d is not there (a pack refused before it made it)."""
    if not os.path.isdir(d):
        return []
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

    def anims(*a):
        return lambda d: d.update(animations=list(a))
    case("a flow paint animation alone, no still pass, accepted", anims(dict(name="wisp", frames=4, motion="flow")))
    case("a turn animation refused", anims(dict(name="spin", frames=4, motion="turn")), "animations[0].motion")
    case("a slide animation refused", anims(dict(name="s", frames=2, motion="slide", path=[[0, 0, 0], [1, 0, 0]])),
         "animations[0].motion")
    case("a light animation refused", anims(dict(name="lamp", frames=2, motion="flow", kind="light")),
         "animations[0].kind")
    case("a working animation refused", anims(dict(name="dust", frames=2, motion="flow", working=True)),
         "animations[0].working")
    case("an animation whose frame takes a cell's name refused", anims(dict(name=f"{RES}-00", frames=2, motion="flow")),
         "animations[0].name")
    case("a building's paint animation with no still pass still refused",
         lambda d: d["animations"].append(dict(name="wisp", frames=4, motion="flow")), "passes", decl=BUILDING)
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


def held_anim(rdir, out_dir, meta, decl, a, rolled=True):
    """One animation's sheet held to its docs: its entry, its size, each frame pixel for pixel."""
    name, n = a["name"], a["frames"]
    e = meta[name]
    glow = a.get("kind") == "glow"
    speed = contract.speed(decl, a)
    check(f"{name}: frames {n}, line_length {n}, animation_speed {speed}, kind {a.get('kind')}",
          (e["frames"], e["line_length"], e.get("animation_speed"), e.get("kind")) ==
          (n, n, speed, "glow" if glow else None), f"{e}")
    im = Image.open(os.path.join(out_dir, name + ".png"))
    w, h = e["size"]
    check(f"{name}.png is {n} frames of its size", im.size == (w * n, h), f"{im.size}, size {w}x{h}")
    bb = cell_box(meta, name, decl)
    bad = []
    for f in range(n):
        src = Image.open(os.path.join(rdir, contract.frame(name, f) + ".png")).convert("RGBA")
        src = pack.glow_frame(src, a.get("bloom")) if glow else pack.clean(src)
        want = pack.roll(src)[0] if rolled else src
        if not same_pixels(im.crop((f * w, 0, (f + 1) * w, h)), want.crop(bb)):
            bad.append(contract.frame(name, f))
    check(f"{name}: every frame is its render as packed{', rolled off,' if rolled else ''} cropped to its box",
          not bad, f"differ: {bad}")


def test_sheet(rdir, out):
    print("sheet")
    decl = load_decl(rdir)
    sheets = os.path.join(out, "sheets")
    code, text, meta = packed(rdir, sheets)
    check("the fixture packs, exit 0", code == 0, text[-600:])
    if meta is None:
        return None
    check("meta.json: resource, resource-effect, bubble, bubble-light, checks, in that order",
          list(meta) == [RES, FX, BUBBLE, LIGHT, "checks"], f"{list(meta)}")
    im, e = held_sheet(rdir, sheets, meta, decl, decl["passes"][0])
    held_sheet(rdir, sheets, meta, decl, decl["passes"][1])
    for a in decl["animations"]:
        held_anim(rdir, sheets, meta, decl, a)
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
    check("rolloff_px names all four sheets", sorted(c.get("rolloff_px", [{}])[0]) == sorted([RES, FX, BUBBLE, LIGHT]),
          f"{c.get('rolloff_px')}")
    check("bubble_cycle 4", c.get(f"{BUBBLE}_cycle", [None])[0] == 4, f"{c.get(f'{BUBBLE}_cycle')}")
    for k in (f"{LIGHT}_white_px", f"{LIGHT}_clipped_px", f"{LIGHT}_edge_px"):
        check(f"{k} 0", c.get(k, [None])[0] == 0, f"{c.get(k)}")
    check("bubble-light_frames [4, 4]", c.get(f"{LIGHT}_frames", [None])[0] == [4, 4], f"{c.get(f'{LIGHT}_frames')}")
    # glow_checks over several plates (a resource's cells): the most clipping over any of them
    tiny = dict(footprint=[1, 1], canvas=[4, 4], directions="one", rig=dict(elevation=60.0, px_per_tile=64))
    packer = pack.Packer(rdir, out, tiny)
    light = Image.new("RGBA", (4, 4))
    light.putpixel((1, 1), (20, 20, 20, 255))
    frames = {"g": [light], "p": [Image.new("RGBA", (4, 4))]}
    dark, pale = Image.new("RGBA", (4, 4), (40, 40, 40, 255)), Image.new("RGBA", (4, 4), (240, 240, 240, 255))
    anim = dict(name="g", over="p")
    both = packer.glow_checks(anim, frames, [dark, pale], "")["g_clipped_px"][0]
    alone = packer.glow_checks(anim, frames, [dark], "")["g_clipped_px"][0]
    check("glow_checks over a list of plates: the most of them (1 over dark and pale, 0 over dark alone)",
          (both, alone) == (1, 0), f"{both}, {alone}")
    code, text = run([sys.executable, os.path.join(TOOLS, "contract.py"), "plates", rdir])
    want = [os.path.join(rdir, contract.cell(RES, 0, v) + ".png") for v in range(4)]
    check("contract.py plates lists the four stage-0 cells", code == 0 and text.split() == want, text)
    return im, meta


def one_stage(variations=None, effect=True, anims=True):
    """An edit for renders_copy: the renders as a model of stage 0 alone (the other stages'
    renders gone), of its first `variations` (all, None), with its effect or without, and its
    animations or without."""
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
        if not anims:
            d["animations"] = []
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
    single = renders_copy(rdir, os.path.join(out, "one-cell-renders"), one_stage(1, effect=False, anims=False))
    code, text, meta = packed(single, os.path.join(out, "one-cell-sheets"))
    ok = code == 0 and meta is not None and list(meta) == [RES, "checks"] and \
        (meta[RES]["frame_count"], meta[RES]["variation_count"]) == (1, 1) and \
        Image.open(os.path.join(out, "one-cell-sheets", RES + ".png")).size == tuple(meta[RES]["size"])
    check("stages 1, variations 1, no effect or animations: a 1 x 1 sheet", ok, text[-600:])


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
    for a in decl["animations"]:
        held_anim(src, sheets, meta, decl, a, rolled=False)


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
    refused("an animation frame gone", gone(contract.frame(BUBBLE, 2)), contract.frame(BUBBLE, 2) + ".png")
    refused("a white square in a glow animation's frame", painted(contract.frame(LIGHT, 1), lambda im: ImageDraw.Draw(
        im).rectangle((150, 150, 157, 157), fill=(255, 255, 255, 255))), LIGHT, "white", want_meta=True)
    one_dark = renders_copy(rdir, os.path.join(out, "one-effect-cell-dark-renders"), painted(
        "resource-effect-02-02", lambda im: im.putalpha(0)))
    code, text, _ = packed(one_dark, os.path.join(out, "one-effect-cell-dark-sheets"))
    check("one effect cell dark: accepted", code == 0, text[-600:])


def test_effect_under(rdir, out):
    """A glow animation's clipping counted with the effect's light added under it (vents T02c)."""
    print("effect under")

    def open_(d, stem):
        return Image.open(os.path.join(d, stem + ".png")).convert("RGBA")

    def lift(d, dst):
        # each effect cell a light that lifts its resource cell to 240 in every channel wherever the
        # cell is opaque (no bloom): white nowhere alone, and anything more in every channel whitens
        d["passes"][1].pop("bloom", None)
        for s, v in contract.cells(d):
            cell = pack.clean(open_(dst, contract.cell(RES, s, v)))
            r, g, b, a = cell.split()
            full = a.point(lambda x: 255 if x == 255 else 0)
            light = [ImageChops.multiply(ch.point(lambda x: max(0, 240 - x)), full) for ch in (r, g, b)]
            Image.merge("RGBA", (*light, full)).save(os.path.join(dst, contract.cell(FX, s, v) + ".png"))
    src = renders_copy(rdir, os.path.join(out, "effect-under-renders"), lift)
    code, text, meta = packed(src, os.path.join(out, "effect-under-sheets"))
    decl = load_decl(src)
    a = next(x for x in decl["animations"] if x["name"] == LIGHT)
    bubble = [pack.clean(open_(src, contract.frame(BUBBLE, f))) for f in range(4)]
    glow = [pack.glow_frame(open_(src, contract.frame(LIGHT, f)), a.get("bloom")) for f in range(4)]
    with_fx = without = 0
    for s, v in contract.cells(decl):
        cell = pack.clean(open_(src, contract.cell(RES, s, v)))
        lit = pack.lit_readings(cell, pack.glow_frame(open_(src, contract.cell(FX, s, v))))
        for base, which in [(r, "with") for r in lit] + [(r, "without") for r in pack.lit_readings(cell)]:
            for b, g in zip(bubble, glow):
                under = base.copy()
                under.alpha_composite(b)
                n = ImageChops.subtract(pack.white(pack.add_light(under, g)), pack.white(under)).histogram()[255]
                if which == "with":
                    with_fx = max(with_fx, n)
                else:
                    without = max(without, n)
    got = (meta or {}).get("checks", {}).get(f"{LIGHT}_clipped_px", [None])[0]
    check("the effect lifting every cell to 240: bubble-light's light whitens nothing over a cell alone, and some "
          "pixels with the effect under it", without == 0 and with_fx > 0, f"without {without}, with {with_fx}")
    check("bubble-light_clipped_px counts with the effect's light added under it; the pack refuses it, naming "
          "bubble-light, meta.json written",
          code != 0 and LIGHT in text and got == with_fx, f"exit {code}, clipped_px {got} vs {with_fx}: {text[-400:]}")
    fx = (meta or {}).get("checks", {}).get(f"{FX}_white_px", [None])[0]
    check("the lifting effect: its own white_px 0", fx == 0, f"{fx}")


def test_effect_exact(rdir, out):
    """The effect's light under a glow animation, pixel by pixel (vents T02d, T02e): the cell drawn
    over the bright ground (pack.GROUND), light added on the screen whatever the cell's alpha, a
    paint layer over it letting (1 - its alpha) of it through, a partly transparent pixel read both
    exact and at full colour and the count the higher."""
    print("effect exact")
    size = (4, 4)
    gr = pack.GROUND
    cell, light, paint, glow = (Image.new("RGBA", size) for _ in range(4))
    # (pixel, cell, the effect's light, paint, the glow, whitened exact, whitened at full colour); worked
    # by hand over the ground (204, 210, 234), a paint p over a screen pixel D giving (p 128 + D 127) / 255
    cases = [
        # the reviewer's: ground + 20 = (224, 230, 254), the paint over it (136.7, 114.5, 126.5); + the glow
        # (261.7, 264.5, 276.5): white. Over black, (20, 20, 20) under the paint, (35.1, 10.0, 10.0) + it: 160
        ((1, 1), (0, 0, 0, 0), (20, 20, 20), (50, 0, 0, 128), (125, 150, 150), True, True),
        ((2, 1), (0, 0, 0, 0), (20, 20, 20), (50, 0, 0, 128), (60, 60, 60), False, False),   # (196.7, ...)
        ((3, 1), (100, 100, 100, 255), (100, 100, 100), None, (50, 50, 50), True, True),     # 250, as add_light
        # light + glow clipping over the ground, not over black: (224, 230, 254) + 30 = (254, 260, 284); 20 + 30
        ((2, 2), (0, 0, 0, 0), (20, 20, 20), None, (30, 30, 30), True, True),
        ((0, 3), (0, 0, 0, 0), None, None, (40, 40, 40), False, False),      # (244, 250, 274): red 244
        ((0, 2), (0, 0, 0, 0), None, None, (41, 41, 41), True, True),        # (245, 251, 275)
        ((1, 3), (240, 240, 240, 0), None, None, (10, 10, 10), False, False),  # cleaned clear: (214, 220, 244)
        # partly transparent, darker than the ground: exact (151.8, 154.8, 166.7) + 95 white, full 195 not
        ((0, 0), (100, 100, 100, 128), None, None, (95, 95, 95), True, False),
        ((1, 0), (0, 0, 0, 64), None, None, (100, 100, 100), True, False),   # exact (152.8, 157.3, 175.3); 100
        # paler than the ground: exact (222.1, 225.1, 237.0) + 6 not white, full 240 + 6 = 246 white
        ((3, 0), (240, 240, 240, 128), None, None, (6, 6, 6), False, True),
    ]
    for xy, c, li, pa, gl, *_ in cases:
        cell.putpixel(xy, c)
        if li:
            light.putpixel(xy, li + (255,))
        if pa:
            paint.putpixel(xy, pa)
        glow.putpixel(xy, gl + (255,))
    tiny = dict(footprint=[1, 1], canvas=list(size), directions="one", rig=dict(elevation=60.0, px_per_tile=64))
    packer = pack.Packer(rdir, out, tiny)
    anim = dict(name="g", over="p")

    def whitened(base, pa=paint, gl=glow):
        under = base.copy()
        under.alpha_composite(pa)
        lit = pack.add_light(under, gl)
        return {xy for xy, *_ in cases if pack.white(lit).getpixel(xy) and not pack.white(under).getpixel(xy)}, under

    def counted(plates, pa=paint, gl=glow):
        return packer.glow_checks(anim, {"g": [gl], "p": [pa]}, plates, "")["g_clipped_px"][0]
    exact, full = pack.lit_cell(cell, light), pack.lit_cell(cell, light, full=True)
    near = [(exact, (2, 0), gr), (exact, (2, 2), (224, 230, 254)), (exact, (3, 1), (200, 200, 200)),
            (exact, (0, 0), (151.8, 154.8, 166.7)), (exact, (3, 0), (222.1, 225.1, 237.0)),
            (full, (3, 0), (240, 240, 240))]
    got = [im.getpixel(xy)[:3] for im, xy, _ in near]
    check(f"lit_cell over the ground {gr}: a clear pixel the ground, lit 20 the ground + 20, an opaque one its colour "
          "+ its light; partly transparent, exact its colour times its alpha over the ground, full its colour",
          gr == (204, 210, 234) and all(abs(g - w) <= 1 for px, (_, _, want) in zip(got, near)
                                        for g, w in zip(px, want)), f"{got}")
    ex_set, under = whitened(exact)
    got = under.getpixel((1, 1))
    check("the reviewer's case: a clear cell pixel lit (20, 20, 20) under paint (50, 0, 0, 128) is the paint over the "
          "ground and the light, within a level of (136.7, 114.5, 126.5)",
          all(abs(g - w) <= 1 for g, w in zip(got[:3], (136.7, 114.5, 126.5))), f"{got}")
    full_set = whitened(full)[0]
    want_ex = {xy for xy, *_, w, _ in cases if w}
    want_full = {xy for xy, *_, w in cases if w}
    check("each pixel whitened as listed, exact (the paint over the ground and the light; the opaque cell as "
          "add_light reads it; the ground's own edge, red 244 and 245; a partly transparent pixel darker than the "
          "ground) and at full colour (one paler than it)", ex_set == want_ex and full_set == want_full,
          f"exact {sorted(ex_set)}, want {sorted(want_ex)}; full {sorted(full_set)}, want {sorted(want_full)}")
    readings = pack.lit_readings(cell, light)
    n_ex, n_full, n = counted([exact]), counted([full]), counted(readings)
    check("glow_checks: exact 6, full 5, over lit_readings (both) the higher, 6", (len(readings), n_ex, n_full, n) ==
          (2, 6, 5, 6), f"readings {len(readings)}, exact {n_ex}, full {n_full}, both {n}")
    # a cell whose one partly transparent pixel is paler than the ground: there full colour counts more
    pale = Image.new("RGBA", size)
    pale.putpixel((3, 0), (240, 240, 240, 128))
    pale_glow = Image.new("RGBA", size)
    pale_glow.putpixel((3, 0), (6, 6, 6, 255))
    clear = Image.new("RGBA", size)
    n_pale = counted(pack.lit_readings(pale), clear, pale_glow)
    n_pale_ex = counted([pack.lit_cell(pale)], clear, pale_glow)
    opaque_one = Image.new("RGBA", size, (100, 100, 100, 255))
    check("a paler partly transparent pixel: exact 0, over lit_readings 1 (full colour's); an opaque cell one reading",
          (n_pale_ex, n_pale, len(pack.lit_readings(opaque_one))) == (0, 1, 1),
          f"exact {n_pale_ex}, both {n_pale}, readings of an opaque cell {len(pack.lit_readings(opaque_one))}")
    # the T02d rule: the cell at full colour where drawn, black where not, the light added
    drawn = cell.getchannel("A").point(lambda x: 255 if x else 0)
    black = ImageChops.add(ImageChops.multiply(cell.convert("RGB"), Image.merge("RGB", (drawn,) * 3)),
                           light.convert("RGB"))
    black.putalpha(255)
    black_set = whitened(black)[0]
    check("over black (the T02d rule) only (3, 1) and (3, 0) whiten: the reviewer's pixel, light + glow at (2, 2) and "
          "the ground's edge at (0, 2) clip over the bright ground and not over black",
          black_set == {(3, 1), (3, 0)} and {(1, 1), (2, 2), (0, 2)} <= ex_set, f"{sorted(black_set)}")


# ---------------------------------------------------------------- preview, measure, finish

def test_preview(rdir, out):
    print("preview")
    import preview
    decl = load_decl(rdir)
    png = os.path.join(out, "preview.png")
    code, text = run([sys.executable, os.path.join(TOOLS, "preview.py"), rdir, png])
    check("preview.py: exit 0", code == 0 and os.path.isfile(png), text[-600:])
    if code != 0:
        return
    im = Image.open(png).convert("RGB")
    pw = decl["canvas"][0] + 2 * preview.PAD
    ph = decl["canvas"][1] + 2 * preview.PAD + preview.LABEL
    want = (preview.PAD + 8 * (pw + preview.PAD), preview.PAD + 6 * (ph + preview.PAD))
    check("preview.py: a row a stage and its night row under it, four variations then the four with the effect",
          im.size == want, f"{im.size} vs {want}")
    lit, below = [], []

    def panel(r, c, sheet=im):
        x, y = preview.PAD + c * (pw + preview.PAD), preview.PAD + r * (ph + preview.PAD) + preview.LABEL
        return sheet.crop((x, y, x + pw, y + ph - preview.LABEL))
    for r in range(0, 6, 2):
        for c in range(4):
            plain, fx = panel(r, c), panel(r, c + 4)
            if ImageChops.subtract(plain, fx).getbbox() is not None:
                below.append((r, c))
            if ImageChops.subtract(fx, plain).getbbox() is None:
                lit.append((r, c))
    check("preview.py: every effect panel at least its plain one, and brighter somewhere", not below and not lit,
          f"darker in {below}, no brighter in {lit}")
    # the night rows: the ground at NIGHT; never brighter than by day; at least the day times NIGHT
    # (less a level for rounding), and well over it where a glow is added (the bubble's light); the
    # effect panels at night at least their plain ones, and brighter somewhere (the effect added)
    night_ground = tuple(round(c * preview.NIGHT) for c in preview.GROUND[:3])
    bright, dull, unlit, fx_bad = [], [], [], []
    for r in range(1, 6, 2):
        for c in range(8):
            day, night = panel(r - 1, c), panel(r, c)
            if night.getpixel((1, 1)) != night_ground:
                fx_bad.append((r, c, "ground", night.getpixel((1, 1))))
            if ImageChops.subtract(night, day).getbbox() is not None:
                bright.append((r, c))
            dimmed = day.point(lambda v: max(0, round(v * preview.NIGHT) - 1))
            if ImageChops.subtract(dimmed, night).getbbox() is not None:
                dull.append((r, c))
            if max(ImageChops.subtract(night, day.point(lambda v: round(v * preview.NIGHT))).convert("L")
                   .getextrema()) < 20:
                unlit.append((r, c))
        for c in range(4):
            plain, fx = panel(r, c), panel(r, c + 4)
            if ImageChops.subtract(plain, fx).getbbox() is not None or ImageChops.subtract(fx, plain).getbbox() is None:
                fx_bad.append((r, c))
    check("preview.py: every night panel on the ground at NIGHT, the effect's at least its plain one and "
          "brighter somewhere", not fx_bad, f"{fx_bad}")
    check("preview.py: every night panel no brighter than its day one anywhere, and at least the day times NIGHT",
          not bright and not dull, f"brighter in {bright}, darker in {dull}")
    check("preview.py: every night panel lit over the dimmed day where a glow is added", not unlit, f"{unlit}")
    one = os.path.join(out, "preview-adopted.png")
    ref = os.path.join(rdir, contract.cell(RES, 0, 0) + ".png")
    code, text = run([sys.executable, os.path.join(TOOLS, "preview.py"), rdir, one, "--adopted", ref])
    got = Image.open(one) if code == 0 else None
    empty = got is not None and panel(1, 0, got.convert("RGB")).getcolors() == [(pw * (ph - preview.LABEL),
                                                                                preview.GAP[:3])]
    check("preview.py --adopted <one picture>: a panel more in the top row alone, its place in the night row "
          "under it empty", got is not None and got.size == (want[0] + pw + preview.PAD, want[1]) and empty,
          f"exit {code}, {got and got.size}, empty {empty}: {text[-300:]}")
    code, text = run([sys.executable, os.path.join(TOOLS, "preview.py"), rdir, one, "--adopted", ref, ref])
    check("preview.py --adopted <two pictures>: refused", code != 0 and "one plate per direction" in text, text[-300:])
    gif = os.path.join(out, "preview.gif")
    code, text = run([sys.executable, os.path.join(TOOLS, "preview.py"), rdir, gif, "--gif", BUBBLE, "--speed", "0.2"])
    ok = code == 0 and os.path.isfile(gif)
    g = Image.open(gif) if ok else None
    check("preview.py --gif bubble: 4 frames, the four stage-0 cells side by side",
          ok and g.n_frames == 4 and g.size == (4 * decl["canvas"][0], decl["canvas"][1]),
          f"exit {code}, {(g.n_frames, g.size) if g else None}: {text[-300:]}")


def test_measure(rdir, out, sheets_meta):
    print("measure")
    if sheets_meta is None:
        check("measure.py: the fixture's sheets", False, "the fixture did not pack")
        return
    sheets, meta = sheets_meta
    src = os.path.join(out, "measure-src")
    if os.path.exists(src):
        shutil.rmtree(src)
    os.makedirs(src)
    os.symlink(os.path.abspath(sheets), os.path.join(src, "sheets"))
    os.symlink(os.path.abspath(rdir), os.path.join(src, "renders"))
    mout = os.path.join(out, "measure")
    code, text = run([sys.executable, os.path.join(TOOLS, "measure.py"), src, "--out", mout])
    check("measure.py: exit 0", code == 0, text[-600:])
    if code != 0:
        return
    m = json.load(open(os.path.join(mout, "measures.json")))
    want = [f"{s:02d}-{v:02d}" for s in range(3) for v in range(4)]
    dirs = m["directions"]
    check("measure.py: every cell, SS-VV, in order", list(dirs) == want, f"{list(dirs)}")
    kinds = dict(resource="plate", **{FX: "glow", BUBBLE: "anim, 4 frames", LIGHT: "glow-anim, 4 frames"})
    bad = [k for k, d in dirs.items() if d["layers"] != kinds or d["motion"] is None or d["motion"]["loop_frames"] != 4
           or sorted(d["glow"]) != sorted([FX, LIGHT]) or d["pack_checks"] != meta["checks"] or d["joins"]]
    check("measure.py: each cell its plate, effect, animations, motion over 4 frames, glow, pack_checks, no joins",
          not bad, f"{bad}: {dirs[bad[0]]['layers'] if bad else ''}")
    past = dirs["00-00"]["coverage"].get("past_edges_tiles", {})
    reach = meta["checks"][f"{RES}_reach_tiles"][0]
    check("measure.py: cell 00-00's coverage past the footprint within 0.05 of pack.py's reach",
          past and all(abs(past[k] - reach[e]) <= 0.05 for k, e in (("west", "W"), ("east", "E"), ("south", "S"))),
          f"{past} vs {reach}")
    e0, e2 = dirs["00-00"]["coverage"]["extent_tiles"], dirs["02-00"]["coverage"]["extent_tiles"]
    check("measure.py: stage 2's extent less than stage 0's", e2[0] < e0[0] and e2[1] < e0[1], f"{e2} vs {e0}")
    code, text = run([sys.executable, os.path.join(TOOLS, "measure.py"), src, "--out", mout + "-conn",
                      "--connection", "0,1,S"])
    check("measure.py --connection on a resource: refused, exit 2", code == 2 and "pipe connections" in text, text[-300:])
    alone = os.path.join(out, "measure-alone")
    code, text = run([sys.executable, os.path.join(TOOLS, "measure.py"), sheets, "--out", alone, "--footprint", "3x3"])
    same = code == 0 and json.load(open(os.path.join(alone, "measures.json")))["directions"] == dirs
    check("measure.py on the sheets alone, --footprint 3x3: exit 0, every cell's figures the same", same,
          text[-400:])
    vout = os.path.join(out, "measure-vanilla")
    code, text = run([sys.executable, os.path.join(TOOLS, "measure.py"), src, "--out", vout,
                      "--vanilla", "crude-oil", "--vanilla", "fluorine-vent"])
    check("measure.py --vanilla crude-oil --vanilla fluorine-vent: exit 0", code == 0, text[-600:])
    if code != 0:
        return
    v = json.load(open(os.path.join(vout, "measures.json")))
    van = v["vanilla"]
    check("measure.py: both references' figures in every cell, our cells' as without them",
          sorted(van) == ["crude-oil", "fluorine-vent"] and all(list(van[n]) == want for n in van)
          and v["directions"] == dirs, f"{ {n: list(c) for n, c in van.items()} }")
    import measure
    label0, foot, still0, _, _ = measure.vanilla("crude-oil", "00-00")
    label1, _, still1, _, _ = measure.vanilla("crude-oil", "02-01")
    check("measure.py: crude oil's cell 00-00 its variation 0, 02-01 its variation 1, a 3 x 3 footprint",
          ("variation 0" in label0 and "variation 1" in label1 and foot == (3, 3)
           and not same_pixels(still0, still1)), f"{label0}, {label1}, {foot}")
    for n in van:
        c0, c1, c4 = (van[n][k]["coverage"] for k in ("00-00", "02-00", "01-01"))
        check(f"measure.py: {n}'s figures the same in cells of one variation (00-00, 02-00), another in 01-01",
              c0 == c1 and c0 != c4, f"{c0} / {c1} / {c4}")


def test_tonal(rdir, out):
    print("tonal")
    plates = [os.path.join(rdir, contract.cell(RES, 0, v) + ".png") for v in range(4)]
    code, text = run([sys.executable, os.path.join(TOOLS, "tonal.py")] + plates)
    lines = text.strip().splitlines()
    check("tonal.py on the four stage-0 cells: exit 0, each measured",
          code == 0 and len(lines) == 4 and all("p50" in ln and "spread" in ln for ln in lines), text[-400:])
    empty, faint = os.path.join(out, "tonal-empty.png"), os.path.join(out, "tonal-faint.png")
    Image.new("RGBA", (64, 64)).save(empty)
    Image.new("RGBA", (64, 64), (120, 100, 80, 200)).save(faint)
    code, text = run([sys.executable, os.path.join(TOOLS, "tonal.py"), empty, faint, plates[0]])
    lines = text.strip().splitlines()
    check("tonal.py on an empty cell, one at alpha 200, then a cell: exit 0, the first two \"no opaque pixel\", "
          "the third measured", code == 0 and len(lines) == 3 and all("no opaque pixel" in ln for ln in lines[:2])
          and "p50" in lines[2], text[-400:])


def test_finish(rdir, out):
    print("finish")
    plates = [os.path.join(rdir, contract.cell(RES, 0, v) + ".png") for v in range(4)]
    code, text = run([sys.executable, os.path.join(TOOLS, "finish.py")] + plates)
    lines = text.strip().splitlines()
    check("finish.py on the four stage-0 cells: exit 0, each measured",
          code == 0 and len(lines) == 4 and all("black" in ln and "ratio" in ln for ln in lines), text[-400:])
    thin, flat = os.path.join(out, "finish-thin.png"), os.path.join(out, "finish-flat.png")
    im = Image.new("RGBA", (64, 64))
    ImageDraw.Draw(im).rectangle((10, 10, 15, 15), fill=(120, 100, 80, 255))
    im.save(thin)
    im = Image.new("RGBA", (64, 64))
    ImageDraw.Draw(im).rectangle((10, 10, 40, 40), fill=(120, 100, 80, 255))
    im.save(flat)
    code, text = run([sys.executable, os.path.join(TOOLS, "finish.py"), thin])
    check("finish.py on a 6 px square: exit 0, too thin", code == 0 and "too thin" in text, text[-300:])
    code, text = run([sys.executable, os.path.join(TOOLS, "finish.py"), flat])
    check("finish.py on a flat square: exit 0, ratio n/a", code == 0 and "ratio  n/a" in text, text[-300:])


# ---------------------------------------------------------------- identity

BASELINE_FILES = ("contract.py", "pack.py", "preview.py", "measure.py", "measure_ports.py", "finish.py")


def baseline_tools(rev, out):
    """The tools as they stood at rev (BASELINE_FILES), in a directory of their own, blender/, beside
    this tree's paths.py and paths.conf, which measure.py reads from the directory above its own."""
    top_dir = os.path.join(out, f"baseline-{rev}")
    d = os.path.join(top_dir, "blender")
    os.makedirs(d, exist_ok=True)
    top = subprocess.run(["git", "-C", TOOLS, "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                         check=True).stdout.strip()
    rel = os.path.relpath(TOOLS, top)
    for f in BASELINE_FILES:
        body = subprocess.run(["git", "-C", top, "show", f"{rev}:{rel}/{f}"], capture_output=True, check=True).stdout
        with open(os.path.join(d, f), "wb") as fh:
            fh.write(body)
    for f in ("paths.py", "paths.conf"):
        shutil.copy(os.path.join(os.path.dirname(TOOLS), f), os.path.join(top_dir, f))
    return d


def same_runs(label, base, out, what, args):
    """A tool (what, a file in the tools dirs) run by the baseline and by this tree on one input:
    args(out) its arguments, writing what it writes under one path, `out`, moved aside after each
    run so the two runs see the same paths. Checks its exit, its output and every file it wrote."""
    got = {}
    for who, tools in (("baseline", base), ("tree", TOOLS)):
        if os.path.exists(out):
            shutil.rmtree(out)
        os.makedirs(out)
        code, text = run([sys.executable, os.path.join(tools, what)] + args(out))
        kept = f"{out}-{who}"
        if os.path.exists(kept):
            shutil.rmtree(kept)
        os.rename(out, kept)
        got[who] = (code, text, kept)
    (bc, bt, bd), (tc, tt, td) = got["baseline"], got["tree"]
    ok, why = same_dirs(bd, td)
    flags = "".join(f" {a}" for a in args("<out>") if a.startswith("--"))
    check(f"{label}: {what}{flags} as the baseline's: exit {bc}, its output, its {len(files(bd))} file(s) byte for byte",
          bc == tc and bt == tt and ok, f"exit {bc} vs {tc}; {why}; output {'same' if bt == tt else 'differs'}: "
          f"{tt[-300:]}")


def test_identity(rdir0, out, rev, renders):
    print("identity")
    if not rev:
        print("  (no --baseline: skipped)")
        return
    base = baseline_tools(rev, out)
    # the fixture as T02 packed it: a resource model with no animations
    still = renders_copy(rdir0, os.path.join(out, "identity-fixture-renders"),
                         lambda d, _: d.update(animations=[]))
    # and one both refuse before they write anything (a resource never turns): refused alike, no crash
    turned = renders_copy(rdir0, os.path.join(out, "identity-turned-renders"),
                          lambda d, _: d.update(animations=[], directions="four"))
    dirs = [(os.path.basename(os.path.normpath(r)), os.path.join(r, "renders")) for r in renders]
    for i, (name, rdir) in enumerate(dirs + [("the fixture, no animations", still),
                                             ("the fixture declared four ways", turned)]):
        label = f"{i + 1} {name}"
        results = {}
        for who, tools in (("baseline", base), ("this tree", TOOLS)):
            dst = os.path.join(out, f"identity-{i + 1}-{'baseline' if tools == base else 'tree'}")
            code, text, _ = packed(rdir, dst, tools)
            plates = run([sys.executable, os.path.join(tools, "contract.py"), "plates", rdir])
            results[who] = (code, text, dst, plates)
        (bc, bt, bd, bp), (tc, tt, td, tp) = results["baseline"], results["this tree"]
        check(f"{label}: pack.py exits as the baseline's ({bc})", bc == tc, f"baseline {bc}, this tree {tc}: {tt[-400:]}")
        ok, why = same_dirs(bd, td)
        if bc != 0 and tc != 0:
            # both refused: alike when they say the same, their own output paths aside, and wrote the same
            alike = bt.replace(bd, "<out>") == tt.replace(td, "<out>")
            check(f"{label}: both refused alike, the same message and the same {len(files(bd))} file(s)",
                  alike and ok, f"{why}; baseline: {bt[-300:]}; this tree: {tt[-300:]}")
        else:
            check(f"{label}: pack.py's every file byte for byte as the baseline's ({len(files(bd))} files)", ok, why)
        check(f"{label}: contract.py plates as the baseline's", bp == tp, f"{bp} vs {tp}")
        if bc != 0 or tc != 0:
            continue
        tag = os.path.join(out, f"identity-{i + 1}")
        plates = tp[1].split()
        same_runs(label, base, f"{tag}-finish", "finish.py", lambda _: plates)
        if contract.is_resource(load_decl(rdir)):
            continue                    # the baseline's preview.py and measure.py had no resource model
        # the review and measure tools, on the same sheets (this tree's, the same as the baseline's)
        same_runs(label, base, f"{tag}-preview", "preview.py", lambda o: [rdir, os.path.join(o, "preview.png")])
        anims = [a for a in load_decl(rdir)["animations"] if a.get("kind", "paint") == "paint"]
        if anims:
            same_runs(label, base, f"{tag}-gif", "preview.py",
                      lambda o: [rdir, os.path.join(o, "preview.gif"), "--gif", anims[0]["name"], "--speed", "1"])
        msrc = f"{tag}-msrc"
        if os.path.exists(msrc):
            shutil.rmtree(msrc)
        os.makedirs(msrc)
        os.symlink(os.path.abspath(td), os.path.join(msrc, "sheets"))
        os.symlink(os.path.abspath(rdir), os.path.join(msrc, "renders"))
        same_runs(label, base, f"{tag}-measure", "measure.py", lambda o: [msrc, "--out", o])


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
    test_effect_under(rdir, out)
    test_effect_exact(rdir, out)
    test_preview(rdir, out)
    test_measure(rdir, out, None if full is None else (os.path.join(out, "sheets"), full[1]))
    test_finish(rdir, out)
    test_tonal(rdir, out)
    test_identity(rdir, out, a.baseline, a.renders)
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
