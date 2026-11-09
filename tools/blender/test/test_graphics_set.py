#!/usr/bin/env python3
"""A model's declared graphics set, measure.py's --crafting-speed and the lights entry (task
drop-crusher-reanimation, T04d): contract.declare() takes graphics_set and animation_progress,
pack.py copies them into meta.json, measure.py plays every layer at them (the options over them),
at --crafting-speed, and never reads meta.json's "lights" entry as a sheet.

  python3 tools/blender/test/test_graphics_set.py --out <dir>

Nothing is rendered: small render directories and sheets are drawn under --out (test_sheet_rows.py's
and test_measure_timing.py's fixtures) and packed by pack.py; the committed sheets of the Drop
Crusher, the Vacuum Furnace and the Radiant Generator are read where they are. Everything written is
kept. Exits 0 when every case below comes out as listed, 1 naming those that do not.

  contract   validate() takes graphics_set crafting-machine, mining-drill and none, and
             animation_progress (1, 0.25) with the first two; it refuses (naming the field) a set
             not one of them or not a string, animation_progress without graphics_set, with none,
             or not a number above 0 (0, -1, nan, inf, true, "1"), either in a resource model, and
             a sheet named "graphics_set" or "animation_progress" once a set is declared.
             declare() (with a stand-in for Blender's rig) writes each into render.json when
             given and leaves both out when not.
  pack       a 4-frame render directory packed as declared: meta.json gains "graphics_set" (and
             "animation_progress" when declared), after the sheets and the lights and before
             "checks"; every sheet byte for byte and meta.json key for key as the same directory
             packed with neither declared, which has no such keys.
  declared   test_measure_timing.py's timed fixture with meta.json's graphics_set crafting-machine:
             with no option the figures of --graphics-set crafting-machine (loop_ticks 1392), and
             progress_from says meta.json; with crafting-machine and animation_progress 1 declared
             (the Reaction Plant's), those of progress 1 (696); --graphics-set crafting-machine
             keeps the declared 1, --graphics-set mining-drill and none take their own 1, and
             --animation-progress 0.25 is over it (2784) with the set kept. The render.json
             fallback: a packed directory whose meta.json lost the keys reads render.json's.
  crafting   the timed fixture, crafting-machine declared, --crafting-speed 1.5: per_tick press
             3/8 (1/2 x 1/2 x 3/2), beacon 1/4, loop_ticks 928 (1392 / 1.5), at_crafting_speed 1.5
             in timing and source; the same 240 drawn frames, in the same order, and every figure
             of them as at crafting speed 1 (coverage, tonal, finish, colour, motion's moving,
             strobe, steps and wrap, the glow's flicker). A layer's own loop is the ticks until its
             entry 0 starts on a tick again: at 3/8 that is three of its cycles (928 ticks), so the
             press and its glow alone are played three times over (played [0, 1, 2, 3] x 3, the
             glow's played_frames 12) and strobe_own_loop counts over that loop. The
             untimed fixture at 0.5 x 2 (a rate of 1): timed (at_crafting_speed 2, loop_ticks 4,
             per_tick 1) and every other figure as the plain untimed run.
  furnace    (T04d criterion 2) the Vacuum Furnace's committed sheets with --crafting-speed 1.5: the
             flywheel's 16 entries at 1 (meta.json declares no speed) x 1.5 x 0.5 = 3/4 an entry a
             tick, the engine's 16 / (1 x 1.5 x 0.5) = 21.33 ticks a cycle; loop_ticks 64, three
             cycles, the first that starts on a tick. With no option per_tick 1/2, 32 ticks.
  crusher    the Drop Crusher's committed sheets with no option: 240 ticks (its meta.json declares
             crafting-machine); --animation-progress 1: 120.
  refused    (exit 2, measure.Usage) --crafting-speed with a mining drill, a generator or no set
             declared or given, and at 0, -1, nan and inf; --animation-progress where meta.json
             declares graphics_set none; meta.json's graphics_set "foundry", animation_progress 0,
             animation_progress with none, animation_progress without a set, and graphics_set on a
             resource.
  lights     sheets whose meta.json has the lights entry pack.py writes (a light of each kind, no
             size) measure, the entry listed as ignored and not drawn or measured; a light sheet
             named "lights" (with a size) is still measured as a light. (T04d criterion 3) the
             Radiant Generator's committed sheets measure, exit 0, "lights" ignored.
  header     (T04c finding 1) the sheet's header and the output carry the timing line only when
             something animates: not for a plate alone, and for the timed fixture.
"""
import argparse
import contextlib
import io
import json
import math
import os
import sys
import types
from fractions import Fraction

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
sys.path.insert(1, HERE)
import contract  # noqa: E402
import measure  # noqa: E402
import test_measure_progress as tmp  # noqa: E402
import test_measure_timing as tmt  # noqa: E402
import test_sheet_rows as tsr  # noqa: E402

FAILED = []
LIGHT = dict(name="port-light", kind="layer", filename="__core__/graphics/light-medium.png", width=300,
             height=300, scale=0.2, tint=[0.1, 0.2, 0.5], shift=[-1.0, 0.0], working=True)


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def refused(case, fn):
    """fn() must raise measure.Usage (or contract.ContractError)."""
    try:
        fn()
        check(f"refused: {case}", False, "ran")
    except (measure.Usage, contract.ContractError) as e:
        check(f"refused: {case}", True)
        print(f"        ({e})")


def base_decl(**extra):
    d = dict(footprint=[2, 2], canvas=[200, 160], directions="one",
             passes=[dict(name="idle", kind="plate", sheet="base"), dict(name="still", kind="still")],
             animations=[dict(name="bar", frames=4, motion="cycle")],
             ports=[], rig=dict(elevation=60.0, px_per_tile=64))
    d.update(extra)
    return d


def resource_decl(**extra):
    d = dict(footprint=[3, 3], canvas=[200, 200], directions="one",
             passes=[dict(name="ore", kind="resource", sheet="ore", stages=1, variations=1)],
             animations=[], ports=[], rig=dict(elevation=60.0, px_per_tile=64))
    d.update(extra)
    return d


def test_contract(out):
    for gs in contract.GRAPHICS_SETS:
        contract.validate(base_decl(graphics_set=gs), "fixture")
        check(f"contract: graphics_set {gs} holds", True)
    for gs, p in (("crafting-machine", 1), ("crafting-machine", 0.25), ("mining-drill", 1)):
        contract.validate(base_decl(graphics_set=gs, animation_progress=p), "fixture")
        check(f"contract: {gs} with animation_progress {p} holds", True)
    for label, decl in (("graphics_set foundry", base_decl(graphics_set="foundry")),
                        ("graphics_set a list", base_decl(graphics_set=["crafting-machine"])),
                        ("animation_progress without graphics_set", base_decl(animation_progress=1)),
                        ("animation_progress with none", base_decl(graphics_set="none", animation_progress=1)),
                        *[(f"animation_progress {v!r}", base_decl(graphics_set="crafting-machine",
                                                                   animation_progress=v))
                          for v in (0, -1, float("nan"), float("inf"), True, "1")],
                        ("graphics_set on a resource", resource_decl(graphics_set="mining-drill")),
                        ("a sheet named animation_progress", base_decl(
                            graphics_set="crafting-machine",
                            passes=[dict(name="idle", kind="plate", sheet="base"), dict(name="still", kind="still"),
                                    dict(name="lamp", kind="light", sheet="animation_progress")])),
                        ("an animation named graphics_set", base_decl(
                            graphics_set="none", animations=[dict(name="graphics_set", frames=4, motion="cycle")]))):
        refused(f"contract: {label}", lambda d=decl: contract.validate(d, "fixture"))
    # declare(), with a stand-in for Blender's rig (the packers' numbers)
    saved = sys.modules.get("rig")
    sys.modules["rig"] = types.SimpleNamespace(ELEVATION=math.radians(60.0), PX_PER_TILE=64)
    try:
        kw = {k: v for k, v in base_decl().items() if k not in ("rig", "canvas")}
        d = contract.declare(os.path.join(out, "declare", "both"), canvas=[200, 160], graphics_set="crafting-machine",
                             animation_progress=1, **kw)
        with open(os.path.join(out, "declare", "both", contract.FILE)) as f:
            written = json.load(f)
        check("contract: declare() writes graphics_set and animation_progress",
              (written.get("graphics_set"), written.get("animation_progress"), d.get("graphics_set"))
              == ("crafting-machine", 1, "crafting-machine"), f"got {written}")
        contract.declare(os.path.join(out, "declare", "none"), canvas=[200, 160], **kw)
        with open(os.path.join(out, "declare", "none", contract.FILE)) as f:
            written = json.load(f)
        check("contract: declare() without them leaves both out",
              not any(k in written for k in contract.GRAPHICS_KEYS), f"got {sorted(written)}")
    finally:
        if saved is None:
            sys.modules.pop("rig", None)
        else:
            sys.modules["rig"] = saved


def render_dir(rdir, **extra):
    """test_sheet_rows.py's 4-frame render directory, render.json with extra declared."""
    tsr.write_fixture(rdir, 4)
    path = os.path.join(rdir, contract.FILE)
    with open(path) as f:
        decl = json.load(f)
    decl.update(extra)
    contract.validate(decl, rdir)
    with open(path, "w") as f:
        json.dump(decl, f, indent=1)
    return rdir


def same_files(a, b):
    """Every .png in a and b, byte for byte; (equal, names)."""
    na = sorted(f for f in os.listdir(a) if f.endswith(".png"))
    nb = sorted(f for f in os.listdir(b) if f.endswith(".png"))
    if na != nb:
        return False, (na, nb)
    for n in na:
        with open(os.path.join(a, n), "rb") as fa, open(os.path.join(b, n), "rb") as fb:
            if fa.read() != fb.read():
                return False, n
    return True, na


def test_pack(out):
    plain = render_dir(os.path.join(out, "pack", "plain", "renders"), lights=[LIGHT])
    both = render_dir(os.path.join(out, "pack", "both", "renders"), lights=[LIGHT], graphics_set="crafting-machine",
                      animation_progress=1)
    one = render_dir(os.path.join(out, "pack", "set", "renders"), graphics_set="mining-drill")
    res = {}
    for label, rdir in (("plain", plain), ("both", both), ("set", one)):
        code, text, meta = tsr.packed(rdir, os.path.join(os.path.dirname(rdir), "sheets"))
        check(f"pack: {label}: pack.py exits 0", code == 0, text[-400:])
        res[label] = meta
    keys = list(res["both"])
    check("pack: meta.json carries graphics_set and animation_progress after the lights, before checks",
          keys[-4:] == ["lights", "graphics_set", "animation_progress", "checks"]
          and (res["both"]["graphics_set"], res["both"]["animation_progress"]) == ("crafting-machine", 1),
          f"got {keys}")
    check("pack: only graphics_set when no progress is declared",
          list(res["set"])[-2:] == ["graphics_set", "checks"] and "animation_progress" not in res["set"]
          and res["set"]["graphics_set"] == "mining-drill", f"got {list(res['set'])}")
    check("pack: neither declared, neither key", not any(k in res["plain"] for k in contract.GRAPHICS_KEYS))
    rest = {k: v for k, v in res["both"].items() if k not in contract.GRAPHICS_KEYS}
    check("pack: meta.json otherwise key for key as packed without them", rest == res["plain"]
          and list(rest) == list(res["plain"]))
    ok, what = same_files(os.path.join(out, "pack", "plain", "sheets"), os.path.join(out, "pack", "both", "sheets"))
    check("pack: every sheet byte for byte as packed without them", ok, f"differs: {what}")
    return os.path.join(out, "pack", "both")


def timed_sheets(d, timed=True, **declared):
    """test_measure_timing.py's fixture, with declared added to its meta.json as pack.py puts them."""
    tmt.write_fixture(d, timed)
    path = os.path.join(d, "meta.json")
    with open(path) as f:
        meta = json.load(f)
    checks = meta.pop("checks")
    meta.update(declared)
    meta["checks"] = checks
    with open(path, "w") as f:
        json.dump(meta, f)
    return d


def run(sheets, out, footprint, *flags):
    return tmp.measure_run(sheets, out, footprint, *flags)


def test_declared(out, packed_dir):
    plain_s = timed_sheets(os.path.join(out, "declared", "plain", "sheets"))
    cm_s = timed_sheets(os.path.join(out, "declared", "cm", "sheets"), graphics_set="crafting-machine")
    rp_s = timed_sheets(os.path.join(out, "declared", "rp", "sheets"), graphics_set="crafting-machine",
                        animation_progress=1)
    _, plain, _ = run(plain_s, os.path.join(out, "declared", "plain", "m"), "1x1")
    _, flag, _ = run(plain_s, os.path.join(out, "declared", "plain", "flag"), "1x1", "--graphics-set", "crafting-machine")
    code, d, src = run(cm_s, os.path.join(out, "declared", "cm", "m"), "1x1")
    t = d["motion"]["timing"]
    check("declared: crafting-machine in meta.json, no option: exit 0, loop_ticks 1392", (code, t["loop_ticks"])
          == (0, 1392), f"got {code}, {t['loop_ticks']}")
    check("declared: every figure as --graphics-set crafting-machine", tmp.unlabelled(d) == tmp.unlabelled(flag))
    check("declared: progress_from says meta.json, the engine's default",
          "meta.json" in t["progress_from"] and "default" in t["progress_from"]
          and (src["graphics_set"], src["animation_progress"]) == ("crafting-machine", 0.5), f"got {t['progress_from']}")
    _, d, _ = run(rp_s, os.path.join(out, "declared", "rp", "m"), "1x1")
    check("declared: crafting-machine with animation_progress 1: as progress 1 (696)",
          d["motion"]["timing"]["loop_ticks"] == 696 and tmp.unlabelled(d) == tmp.unlabelled(plain)
          and d["motion"]["timing"]["animation_progress"] == 1, f"got {d['motion']['timing']['loop_ticks']}")
    for label, flags, want, want_set in (
            ("--graphics-set crafting-machine keeps the declared 1", ("--graphics-set", "crafting-machine"), 696,
             "crafting-machine"),
            ("--graphics-set mining-drill: its own 1", ("--graphics-set", "mining-drill"), 696, "mining-drill"),
            ("--graphics-set none: 1", ("--graphics-set", "none"), 696, "none"),
            ("--animation-progress 0.25 over it, the set kept", ("--animation-progress", "0.25"), 2784,
             "crafting-machine")):
        _, d, _ = run(rp_s, os.path.join(out, "declared", "rp", flags[1]), "1x1", *flags)
        t = d["motion"]["timing"]
        check(f"declared: {label}", (t["loop_ticks"], t["graphics_set"]) == (want, want_set),
              f"got {t['loop_ticks']}, {t['graphics_set']} ({t['progress_from']})")
    _, d, _ = run(cm_s, os.path.join(out, "declared", "cm", "mining"), "1x1", "--graphics-set", "mining-drill")
    check("declared: --graphics-set mining-drill over a declared crafting-machine: 696",
          d["motion"]["timing"]["loop_ticks"] == 696, f"got {d['motion']['timing']['loop_ticks']}")
    # render.json's, for a meta.json packed before the keys were copied
    meta_path = os.path.join(packed_dir, "sheets", "meta.json")
    with open(meta_path) as f:
        meta = json.load(f)
    for k in contract.GRAPHICS_KEYS:
        meta.pop(k)
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=1)
    measure.run([packed_dir, "--out", os.path.join(out, "declared", "render-json")])
    with open(os.path.join(out, "declared", "render-json", "measures.json")) as f:
        s = json.load(f)["source"]
    check("declared: render.json's when meta.json has none",
          (s["graphics_set"], s["animation_progress"]) == ("crafting-machine", 1) and "render.json" in s["progress_from"],
          f"got {s['graphics_set']}, {s['animation_progress']}, {s['progress_from']}")


def test_crafting(out):
    cm_s = os.path.join(out, "declared", "cm", "sheets")
    _, one, _ = run(cm_s, os.path.join(out, "crafting", "1"), "1x1")
    code, d, src = run(cm_s, os.path.join(out, "crafting", "1.5"), "1x1", "--crafting-speed", "1.5")
    t = d["motion"]["timing"]
    check("crafting: 1.5: exit 0", code == 0, f"exit {code}")
    check("crafting: 1.5: per_tick press 3/8, beacon 1/4, press-glow 3/8",
          [t["layers"][k]["per_tick"] for k in ("press", "beacon", "press-glow")] == ["3/8", "1/4", "3/8"],
          f"got {t['layers']}")
    check("crafting: 1.5: loop_ticks 928 (1392 / 1.5)", (t["loop_ticks"], t["complete"]) == (928, True),
          f"got {t['loop_ticks']}")
    check("crafting: 1.5: at_crafting_speed in timing and source", (t["at_crafting_speed"], src["at_crafting_speed"],
                                                                    one["motion"]["timing"]["at_crafting_speed"])
          == (1.5, 1.5, 1), f"got {t['at_crafting_speed']}, {src['at_crafting_speed']}")
    own = ("strobe_own_loop_pct", "strobe_own_loop_px")
    a, b = tmp.unticked(d), tmp.unticked(one)
    for x in (a, b):
        x.pop("layers_alone")
        x["glow"]["press-glow"].pop("played_frames")
        for k in own:
            x["motion"].pop(k)
    check("crafting: 1.5: the same drawn frames, every figure of them as at crafting speed 1", a == b)
    la = d["layers_alone"]
    check("crafting: 1.5: the press and its glow alone, their own loop three cycles: played 3 times",
          (la["press"]["played"], la["press-glow"]["played"], d["glow"]["press-glow"]["played_frames"])
          == ([0, 1, 2, 3] * 3, [0, 1, 2, 3] * 3, 12), f"got {la['press'].get('played')}")
    un_s = timed_sheets(os.path.join(out, "crafting", "untimed", "sheets"), False, graphics_set="crafting-machine")
    plain_s = timed_sheets(os.path.join(out, "crafting", "untimed-plain", "sheets"), False)
    _, plain, _ = run(plain_s, os.path.join(out, "crafting", "untimed-plain", "m"), "1x1")
    _, d, _ = run(un_s, os.path.join(out, "crafting", "untimed", "2"), "1x1", "--crafting-speed", "2")
    t = d["motion"].get("timing") or {}
    check("crafting: 0.5 x 2, a rate of 1: timed, at_crafting_speed 2, loop_ticks 4, per_tick 1",
          (t.get("at_crafting_speed"), t.get("loop_ticks"), t.get("layers", {}).get("press", {}).get("per_tick"))
          == (2, 4, "1"), f"got {t}")
    motion = ("loop_frames", "moving_pct", "strobe_px", "step_px", "wrap_px", "per_layer_moving_pct")
    check("crafting: 0.5 x 2: the motion as the plain untimed run's",
          [d["motion"][k] for k in motion] == [plain["motion"][k] for k in motion],
          f"got {[d['motion'][k] for k in motion]}")


def test_furnace(out):
    sheets = os.path.join(REPO, "concept", "vacuum-furnace", "model", "sheets")
    code, d, src = run(sheets, os.path.join(out, "furnace", "1.5"), "3x3", "--crafting-speed", "1.5")
    t = d["motion"]["timing"]
    fw = t["layers"]["flywheel"]
    cycle = Fraction(fw["entries"]) / Fraction(fw["per_tick"])
    engine = fw["entries"] / (1 * 1.5 * 0.5)
    print(f"        furnace at crafting speed 1.5: flywheel {fw}; a cycle {float(cycle):.4g} ticks (the engine's "
          f"16 / (1 x 1.5 x 0.5) = {engine:.4g}); loop_ticks {t['loop_ticks']}")
    check("furnace: exit 0, crafting-machine declared, at 1.5", (code, src["graphics_set"], t["at_crafting_speed"])
          == (0, "crafting-machine", 1.5), f"got {code}, {src['graphics_set']}")
    check("furnace: 16 entries at 3/4 a tick, a cycle of 64/3 ticks, the engine's figure",
          (fw["entries"], fw["as_fraction"], fw["per_tick"], cycle) == (16, "1", "3/4", Fraction(64, 3))
          and abs(float(cycle) - engine) < 1e-9, f"got {fw}")
    check("furnace: loop_ticks 64, three cycles", (t["loop_ticks"], fw["loop_ticks"]) == (64, 64), f"got {t['loop_ticks']}")
    _, d, _ = run(sheets, os.path.join(out, "furnace", "1"), "3x3")
    fw = d["motion"]["timing"]["layers"]["flywheel"]
    check("furnace: with no option 1/2 a tick, 32 ticks", (fw["per_tick"], d["motion"]["timing"]["loop_ticks"])
          == ("1/2", 32), f"got {fw}")


def test_crusher(out):
    sheets = os.path.join(REPO, "concept", "drop-crusher", "model", "sheets")
    _, d, src = run(sheets, os.path.join(out, "crusher", "none"), "3x3")
    check("crusher: no option: 240 ticks, crafting-machine from meta.json",
          (d["motion"]["timing"]["loop_ticks"], src["graphics_set"], src["animation_progress"]) == (240, "crafting-machine", 0.5)
          and "meta.json" in src["progress_from"], f"got {d['motion']['timing']['loop_ticks']}, {src}")
    _, d, _ = run(sheets, os.path.join(out, "crusher", "progress-1"), "3x3", "--animation-progress", "1")
    check("crusher: --animation-progress 1: 120 ticks", d["motion"]["timing"]["loop_ticks"] == 120,
          f"got {d['motion']['timing']['loop_ticks']}")


def bad_meta(d, **declared):
    """The timed fixture with declared written into meta.json as given, valid or not."""
    return timed_sheets(d, True, **declared)


def test_refused(out):
    mining = timed_sheets(os.path.join(out, "refused", "mining", "sheets"), graphics_set="mining-drill")
    gen = timed_sheets(os.path.join(out, "refused", "none", "sheets"), graphics_set="none")
    bare = timed_sheets(os.path.join(out, "refused", "bare", "sheets"))
    cm = os.path.join(out, "declared", "cm", "sheets")
    o = os.path.join(out, "refused", "m")
    for label, src, flags in (("--crafting-speed with a mining drill declared", mining, ("--crafting-speed", "1.5")),
                              ("--crafting-speed 1 with a mining drill declared", mining, ("--crafting-speed", "1")),
                              ("--crafting-speed with a generator declared", gen, ("--crafting-speed", "1.5")),
                              ("--crafting-speed with no set", bare, ("--crafting-speed", "1.5")),
                              ("--crafting-speed with --graphics-set mining-drill", bare,
                               ("--graphics-set", "mining-drill", "--crafting-speed", "1.5")),
                              ("--crafting-speed 0", cm, ("--crafting-speed", "0")),
                              ("--crafting-speed -1", cm, ("--crafting-speed=-1",)),
                              ("--crafting-speed nan", cm, ("--crafting-speed", "nan")),
                              ("--crafting-speed inf", cm, ("--crafting-speed", "inf")),
                              ("--animation-progress where none is declared", gen, ("--animation-progress", "0.5"))):
        refused(label, lambda s=src, f=flags: measure.run([s, "--out", o, "--footprint", "1x1", *f]))
    for label, declared in (("meta.json's graphics_set foundry", dict(graphics_set="foundry")),
                            ("meta.json's animation_progress 0", dict(graphics_set="crafting-machine",
                                                                      animation_progress=0)),
                            ("meta.json's animation_progress with none", dict(graphics_set="none",
                                                                              animation_progress=1)),
                            ("meta.json's animation_progress without a set", dict(animation_progress=1))):
        src = bad_meta(os.path.join(out, "refused", label.replace(" ", "-").replace("'", ""), "sheets"), **declared)
        refused(label, lambda s=src: measure.run([s, "--out", o, "--footprint", "1x1"]))
    res = os.path.join(out, "refused", "resource", "sheets")
    tmp.resource_sheets(res)
    with open(os.path.join(res, "meta.json")) as f:
        meta = json.load(f)
    meta = {"ore": meta["ore"], "graphics_set": "mining-drill", "checks": {}}
    with open(os.path.join(res, "meta.json"), "w") as f:
        json.dump(meta, f)
    refused("meta.json's graphics_set on a resource", lambda: measure.run([res, "--out", o, "--footprint", "1x1"]))


def test_lights(out):
    d = os.path.join(out, "lights", "sheets")
    tmt.write_fixture(d, True)
    with open(os.path.join(d, "meta.json")) as f:
        meta = json.load(f)
    checks = meta.pop("checks")
    meta["lights"] = {"port-light": {k: v for k, v in LIGHT.items() if k != "name"} | {"draw_as_light": True},
                      "lamp-light": dict(kind="definition", type="basic", intensity=0.5, size=4, shift=[0, 0],
                                         working=False)}
    meta["checks"] = checks
    with open(os.path.join(d, "meta.json"), "w") as f:
        json.dump(meta, f)
    code, r, _ = run(d, os.path.join(out, "lights", "m"), "1x1")
    check("lights: the lights entry measures, exit 0", code == 0, f"exit {code}")
    check("lights: listed as ignored, not measured as a light", any(i.startswith("lights ") for i in r["ignored"])
          and "lights" not in r["light"], f"got {r['ignored']}, {list(r['light'])}")
    # a light sheet that is named "lights" is a sheet, and still measured as one
    Image.new("RGBA", (8, 8), (255, 255, 255, 200)).save(os.path.join(d, "lights.png"))
    meta["lights"] = dict(size=[8, 8], shift=[0.0, 0.0])
    with open(os.path.join(d, "meta.json"), "w") as f:
        json.dump(meta, f)
    _, r, _ = run(d, os.path.join(out, "lights", "sheet"), "1x1")
    check("lights: a light sheet named lights is still measured as one", "lights" in r["light"],
          f"got {list(r['light'])}")
    sheets = os.path.join(REPO, "concept", "radiant-generator", "model", "sheets")
    code, r, src = run(sheets, os.path.join(out, "lights", "radiant-generator"), "5x5")
    check("lights: the Radiant Generator's sheets measure, exit 0, lights ignored, graphics_set none",
          code == 0 and any(i.startswith("lights ") for i in r["ignored"]) and src["graphics_set"] == "none",
          f"exit {code}, {r['ignored']}")
    print(f"        radiant generator: {os.path.join(out, 'lights', 'radiant-generator', 'measures.json')}")


def headed(sheets, out, footprint):
    """measure.run, with the sheet's header lines (its first text block) and the output caught."""
    seen = []
    real = measure.text_block

    def spy(title, lines, width):
        seen.append(list(lines))
        return real(title, lines, width)
    measure.text_block = spy
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            measure.run([sheets, "--out", out, "--footprint", footprint])
    finally:
        measure.text_block = real
    return seen[0], buf.getvalue()


def test_header(out):
    still = os.path.join(out, "header", "still", "sheets")
    os.makedirs(still, exist_ok=True)
    Image.new("RGBA", (64, 64), (60, 60, 60, 255)).save(os.path.join(still, "base.png"))
    with open(os.path.join(still, "meta.json"), "w") as f:
        json.dump({"base": dict(size=[64, 64], shift=[0.0, 0.0]), "checks": {}}, f)
    head, text = headed(still, os.path.join(out, "header", "still", "m"), "1x1")
    check("header: a plate alone: no timing line on the sheet or in the output",
          not any(h.startswith("timing:") for h in head) and "timing:" not in text, f"got {head}")
    head, text = headed(os.path.join(out, "declared", "cm", "sheets"), os.path.join(out, "header", "anim"), "1x1")
    line = [h for h in head if h.startswith("timing:")]
    check("header: something animates: the timing line on the sheet and in the output, at crafting speed 1",
          len(line) == 1 and line[0] in text and line[0].endswith("at crafting speed 1"), f"got {head}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    test_contract(a.out)
    packed_dir = test_pack(a.out)
    test_declared(a.out, packed_dir)
    test_crafting(a.out)
    test_furnace(a.out)
    test_crusher(a.out)
    test_refused(a.out)
    test_lights(a.out)
    test_header(a.out)
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
