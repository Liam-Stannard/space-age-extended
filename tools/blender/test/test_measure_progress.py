#!/usr/bin/env python3
"""measure.py's animation_progress (--graphics-set, --animation-progress; task drop-crusher-reanimation,
T04b): every layer played at animation_speed x the graphics set's animation_progress, as the engine
plays a crafting machine's, held to values worked by hand, the Drop Crusher's committed stroke and
vanilla's assembler 3.

  python3 tools/blender/test/test_measure_progress.py --out <dir>

Nothing is rendered: test_measure_timing.py's fixture sheets are drawn under --out, the crusher's
committed sheets are read where they are, and assembler 3's sheets are copied from the vanilla data
(tools/paths.conf's FACTORIO_ROOT) under --out. Everything written is kept. Exits 0 when every case
below comes out as listed, 1 naming those that do not.

  play       entries [0, 1, 2] at speed 2 show frames 0, 2, 1 at progress 1 and 0, 1, 2 over 3 ticks at
             progress 1/2 (an entry every tick: none skipped); entries [0, 1] at speed 2 never change
             at progress 1, and do at 1/2. A Layer of meta.json speed 0.5 at progress 1/2: per tick 1/4.
  fixture    test_measure_timing.py's timed fixture (press 116 entries at 0.5, its glow, the beacon
             at 1/3) with --graphics-set crafting-machine (progress 0.5, the engine's default):
             loop_ticks 1392 (696 x 2), 23.2 s; frame_ticks each the progress-1 run's doubled; every
             figure but the tick figures (step_px, wrap, moving, strobe, strobe_own_loop, per layer,
             flicker, the layers alone) the same as the run with neither option; per layer per_tick
             press 1/4, beacon 1/6, press-glow 1/4, own loops 464, 12, 464 (as_fraction still the
             declared 1/2, 1/3); the glow's loop_ticks 464; timing and source say 0.5,
             crafting-machine, at crafting speed 1.
  given      --animation-progress 0.5 alone: the same figures. --animation-progress 0.25 (the
             electromagnetic plant's): loop_ticks 2784. --graphics-set crafting-machine
             --animation-progress 1 (the Reaction Plant's), --graphics-set mining-drill and
             --graphics-set none: every figure as with neither option (only the labels differ).
  untimed    the untimed fixture (no sequence, no speed) with --graphics-set crafting-machine: now
             timed, loop_ticks 8, frame_ticks [0, 2, 4, 6]; step_px [152, 152, 152], wrap 152, strobe
             52 px as untimed; the layers alone played in sprite order.
  refused    (exit 2, measure.Usage) --graphics-set foundry; --animation-progress 0, -1, nan, inf;
             --graphics-set none with --animation-progress; either option on a resource model.
  crusher    (T04b criterion 1) concept/drop-crusher/model/sheets, --footprint 3x3, --graphics-set
             crafting-machine: the stroke's 60 entries at 0.5 x 0.5 loop in 240 ticks (4 s), per_tick
             1/4, 44 drawn frames; with --animation-progress 1 120 (the figure before T04b, which
             its meta.json's graphics_set, T04d, now gives with neither option: 240); motion
             otherwise the same.
  assembler  (T04b criterion 2) vanilla's assembler 3, its sheets copied from the game's data: base
             frame 0 the plate, assembling-machine-3-anim 64 frames, 8 a row, the animation. The
             source is checked first: assembler-pictures.lua's assembler3_graphics_set sets
             animation_progress = 0.5 and no animation_speed (1, the engine's default), its anim
             layer frame_count = 64, its .lua line_length 8 at 140 x 160; entities.lua's
             assembling-machine-3 crafting_speed = 1.25. Measured with --graphics-set
             crafting-machine --animation-progress 0.5, as vanilla declares it: 64 drawn frames,
             each 2 ticks, loop_ticks 128 at crafting speed 1 (the engine at the machine's own 1.25:
             64 / (1 x 1.25 x 0.5) = 102.4 ticks, which measure.py does not model); per_tick 1/2;
             with --graphics-set crafting-machine alone (the default) the same.
"""
import argparse
import copy
import json
import math
import os
import re
import shutil
import sys
from fractions import Fraction

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(1, HERE)
import measure  # noqa: E402
import paths  # noqa: E402
import test_measure_timing as tmt  # noqa: E402

FAILED = []
LABELS = ("animation_progress", "graphics_set", "progress_from")     # where the progress came from


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def measure_run(sheets, out, footprint, *flags):
    """measure.run on sheets; (exit code, the one direction's figures, the source)."""
    code = measure.run([sheets, "--out", out, "--footprint", footprint, *flags])
    with open(os.path.join(out, "measures.json")) as f:
        m = json.load(f)
    return code, m["directions"][""], m["source"]


def unticked(d):
    """A direction's figures less every tick figure and the progress's labels: what a progress must
    leave alone while every layer goes at most an entry a tick."""
    d = copy.deepcopy(d)
    mo = d.get("motion") or {}
    mo.pop("timing", None)
    for g in d.get("glow", {}).values():
        g.pop("loop_ticks", None)
    return d


def unlabelled(d):
    """A direction's figures less the progress's labels (timing's animation_progress, graphics_set,
    progress_from)."""
    d = copy.deepcopy(d)
    t = (d.get("motion") or {}).get("timing")
    for k in LABELS:
        (t or {}).pop(k, None)
    return d


def test_play():
    half = Fraction(1, 2)
    tl1 = measure.Timeline([measure.Play([0, 1, 2], Fraction(2))])
    tl2 = measure.Timeline([measure.Play([0, 1, 2], Fraction(2) * half)])
    check("play: [0, 1, 2] at speed 2: frames 0, 2, 1 at progress 1; 0, 1, 2 over 3 ticks at 1/2",
          ([s[0] for s in tl1.states], tl1.ticks, [s[0] for s in tl2.states], tl2.ticks)
          == ([0, 2, 1], 3, [0, 1, 2], 3),
          f"got {tl1.states} {tl1.ticks}, {tl2.states} {tl2.ticks}")
    check("play: [0, 1] at speed 2 never changes at progress 1, does at 1/2",
          measure.Play([0, 1], Fraction(2)).static and not measure.Play([0, 1], Fraction(2) * half).static)
    lay = measure.Layer("x", "anim", dict(frames=4, animation_speed=0.5), progress=half)
    check("play: a Layer at speed 0.5 and progress 1/2 goes 1/4 an entry a tick, timed",
          (lay.play.speed, lay.declared_speed, lay.timed, lay.play.loop) == (Fraction(1, 4), half, True, 16),
          f"got {lay.play.speed}, {lay.declared_speed}, {lay.timed}, {lay.play.loop}")
    lay = measure.Layer("x", "anim", dict(frames=4), progress=half)
    check("play: a Layer with no speed or sequence at progress 1/2 is timed", lay.timed and lay.play.loop == 8)
    check("play: at progress 1 it is not", not measure.Layer("x", "anim", dict(frames=4)).timed)


def test_fixture(out):
    sheets = os.path.join(out, "fixture", "sheets")
    tmt.write_fixture(sheets, True)
    _, plain, src0 = measure_run(sheets, os.path.join(out, "fixture", "plain"), "1x1")
    code, cm, src = measure_run(sheets, os.path.join(out, "fixture", "crafting"), "1x1",
                                "--graphics-set", "crafting-machine")
    check("fixture: exit 0", code == 0, f"exit {code}")
    t0, t = plain["motion"]["timing"], cm["motion"]["timing"]
    check("fixture: with neither option, progress 1, as before",
          (t0["loop_ticks"], t0["animation_progress"], t0["graphics_set"], src0["animation_progress"])
          == (696, 1, None, 1), f"got {t0['loop_ticks']}, {t0['animation_progress']}, {t0['graphics_set']}")
    check("fixture: loop_ticks 1392, 23.2 s, complete", (t["loop_ticks"], t["loop_seconds"], t["complete"],
                                                         t["measured_ticks"]) == (1392, 23.2, True, 1392),
          f"got {t['loop_ticks']}, {t['loop_seconds']}, {t['complete']}")
    check("fixture: frame_ticks doubled", t["frame_ticks"] == [2 * x for x in t0["frame_ticks"]],
          f"got {t['frame_ticks'][:10]}")
    check("fixture: every other figure as at progress 1", unticked(cm) == unticked(plain))
    check("fixture: step_px, strobe as worked in test_measure_timing (240 frames, 152 px)",
          (cm["motion"]["loop_frames"], cm["motion"]["strobe_px"], cm["motion"]["strobe_own_loop_px"])
          == (240, 152, 36), f"got {cm['motion']['loop_frames']}, {cm['motion']['strobe_px']}")
    check("fixture: per layer", t["layers"] == {
        "press": dict(entries=116, frame_sequence=True, animation_speed=0.5, as_fraction="1/2", per_tick="1/4",
                      loop_ticks=464),
        "beacon": dict(entries=2, frame_sequence=False, animation_speed=1 / 3, as_fraction="1/3", per_tick="1/6",
                       loop_ticks=12),
        "press-glow": dict(entries=116, frame_sequence=True, animation_speed=0.5, as_fraction="1/2",
                           per_tick="1/4", loop_ticks=464)}, f"got {t['layers']}")
    check("fixture: the glow's own loop 464 ticks", cm["glow"]["press-glow"]["loop_ticks"] == 464,
          f"got {cm['glow']['press-glow'].get('loop_ticks')}")
    check("fixture: timing and source say where the progress came from",
          (t["animation_progress"], t["graphics_set"], t["at_crafting_speed"], src["animation_progress"],
           src["graphics_set"]) == (0.5, "crafting-machine", 1, 0.5, "crafting-machine")
          and "default" in t["progress_from"] and t["progress_from"] == src["progress_from"], f"got {t}")
    return sheets, plain, cm


def test_given(out, sheets, plain, cm):
    _, d, _ = measure_run(sheets, os.path.join(out, "fixture", "given-0.5"), "1x1", "--animation-progress", "0.5")
    check("given: --animation-progress 0.5 alone: the crafting machine's figures", unlabelled(d) == unlabelled(cm)
          and d["motion"]["timing"]["graphics_set"] is None
          and d["motion"]["timing"]["progress_from"].startswith("--animation-progress"))
    _, d, _ = measure_run(sheets, os.path.join(out, "fixture", "given-0.25"), "1x1", "--animation-progress", "0.25")
    t = d["motion"]["timing"]
    check("given: 0.25: loop_ticks 2784, per_tick press 1/8", (t["loop_ticks"], t["layers"]["press"]["per_tick"])
          == (2784, "1/8") and unticked(d) == unticked(plain), f"got {t['loop_ticks']}")
    for label, flags in (("crafting-machine, progress 1 (the Reaction Plant's)",
                          ("--graphics-set", "crafting-machine", "--animation-progress", "1")),
                         ("mining-drill", ("--graphics-set", "mining-drill")),
                         ("none", ("--graphics-set", "none"))):
        _, d, _ = measure_run(sheets, os.path.join(out, "fixture", "given-" + flags[1]), "1x1", *flags)
        check(f"given: {label}: every figure as with neither option", unlabelled(d) == unlabelled(plain),
              f"loop {d['motion']['timing']['loop_ticks']}")


def test_untimed(out):
    sheets = os.path.join(out, "untimed", "sheets")
    tmt.write_fixture(sheets, False)
    _, plain, _ = measure_run(sheets, os.path.join(out, "untimed", "plain"), "1x1")
    _, d, _ = measure_run(sheets, os.path.join(out, "untimed", "crafting"), "1x1", "--graphics-set", "crafting-machine")
    mo = d["motion"]
    check("untimed: progress 1 stays untimed", "timing" not in plain["motion"])
    check("untimed: progress 0.5 is timed: 8 ticks, frames at 0, 2, 4, 6",
          (mo.get("timing", {}).get("loop_ticks"), mo.get("timing", {}).get("frame_ticks")) == (8, [0, 2, 4, 6]),
          f"got {mo.get('timing')}")
    pm = plain["motion"]
    check("untimed: step_px [152] x 3, wrap 152, strobe 52 px, as untimed",
          (mo["step_px"], mo["wrap_px"], mo["strobe_px"]) == ([152] * 3, 152, 52)
          == (pm["step_px"], pm["wrap_px"], pm["strobe_px"]),
          f"got {mo['step_px']}, {mo['wrap_px']}, {mo['strobe_px']}")
    check("untimed: the layers alone played in sprite order",
          [d["layers_alone"][k].get("played") for k in ("press", "beacon")] == [[0, 1, 2, 3], [0, 1]],
          f"got {d['layers_alone']}")


def resource_sheets(d):
    os.makedirs(d, exist_ok=True)
    Image.new("RGBA", (64, 64), (90, 90, 90, 255)).save(os.path.join(d, "ore.png"))
    with open(os.path.join(d, "meta.json"), "w") as f:
        json.dump({"ore": dict(kind="resource", size=[64, 64], shift=[0.0, 0.0], variation_count=1, frame_count=1,
                               line_length=1), "checks": {}}, f)


def test_refused(out):
    sheets = os.path.join(out, "fixture", "sheets")
    res = os.path.join(out, "resource", "sheets")
    resource_sheets(res)
    for label, src, flags in (("--graphics-set foundry", sheets, ("--graphics-set", "foundry")),
                              ("--animation-progress 0", sheets, ("--animation-progress", "0")),
                              ("--animation-progress -1", sheets, ("--animation-progress=-1",)),
                              ("--animation-progress nan", sheets, ("--animation-progress", "nan")),
                              ("--animation-progress inf", sheets, ("--animation-progress", "inf")),
                              ("--graphics-set none with a progress", sheets,
                               ("--graphics-set", "none", "--animation-progress", "0.5")),
                              ("a resource model with --graphics-set", res, ("--graphics-set", "mining-drill")),
                              ("a resource model with --animation-progress", res, ("--animation-progress", "1"))):
        try:
            measure.run([src, "--out", os.path.join(out, "refused"), "--footprint", "1x1", *flags])
            check(f"refused: {label}", False, "ran")
        except measure.Usage as e:
            check(f"refused: {label}", True)
            print(f"        ({e})")
    try:
        measure.run([res, "--out", os.path.join(out, "resource", "measures"), "--footprint", "1x1"])
        check("refused: a resource model with neither option still measures", True)
    except measure.Usage as e:
        check("refused: a resource model with neither option still measures", False, str(e))


def test_crusher(out):
    sheets = os.path.join(REPO, "concept", "drop-crusher", "model", "sheets")
    code, d, _ = measure_run(sheets, os.path.join(out, "crusher", "crafting"), "3x3",
                             "--graphics-set", "crafting-machine")
    _, plain, _ = measure_run(sheets, os.path.join(out, "crusher", "plain"), "3x3", "--animation-progress", "1")
    t = d["motion"]["timing"]
    st = t["layers"]["stroke"]
    print(f"        crusher: loop_ticks {t['loop_ticks']} ({t['loop_seconds']} s), stroke {st}")
    check("crusher: exit 0", code == 0, f"exit {code}")
    check("crusher: the stroke loops in 240 ticks, 4 s",
          (t["loop_ticks"], t["loop_seconds"], t["complete"]) == (240, 4.0, True), f"got {t['loop_ticks']}")
    check("crusher: 60 entries at 0.5 x 0.5", (st["entries"], st["animation_speed"], st["per_tick"], st["loop_ticks"])
          == (60, 0.5, "1/4", 240), f"got {st}")
    check("crusher: 44 drawn frames", d["motion"]["loop_frames"] == 44, f"got {d['motion']['loop_frames']}")
    check("crusher: at progress 1 120 ticks, as before T04b",
          plain["motion"]["timing"]["loop_ticks"] == 120, f"got {plain['motion']['timing']['loop_ticks']}")
    check("crusher: motion otherwise the same", unticked(d) == unticked(plain))


def lua_block(text, name):
    """The table `name = { ... }` in a Lua file's text, braces matched."""
    i = text.index(name)
    a = text.index("{", i)
    depth = 0
    for b in range(a, len(text)):
        depth += {"{": 1, "}": -1}.get(text[b], 0)
        if depth == 0:
            return text[a:b + 1]
    raise ValueError(f"{name}: no closing brace")


def assembler_source():
    """Assembler 3's timing as the vanilla data declares it: (progress, frames, line_length, w, h,
    crafting_speed), each read from the file and checked against what this test assumes."""
    data = paths.factorio_data()
    with open(os.path.join(data, "base", "prototypes", "entity", "assembler-pictures.lua")) as f:
        gs = lua_block(f.read(), "assembler3_graphics_set")
    anim = gs[gs.index("assembling-machine-3-anim"):]
    anim = anim[:anim.index("})")]
    progress = float(re.search(r"animation_progress\s*=\s*([\d.]+)", gs).group(1))
    frames = int(re.search(r"frame_count\s*=\s*(\d+)", anim).group(1))
    check("assembler: the graphics set sets animation_progress = 0.5", progress == 0.5, f"got {progress}")
    check("assembler: the anim layer has frame_count = 64", frames == 64, f"got {frames}")
    check("assembler: no animation_speed in the graphics set (the engine's default, 1)",
          "animation_speed" not in gs)
    with open(os.path.join(data, "base", "graphics", "entity", "assembling-machine-3",
                           "assembling-machine-3-anim.lua")) as f:
        side = f.read()
    line = int(re.search(r"line_length\s*=\s*(\d+)", side).group(1))
    _, w, h, _, _ = measure.sprite_geometry("base/graphics/entity/assembling-machine-3/assembling-machine-3-anim.png")
    check("assembler: the anim sheet 8 a row of 140 x 160", (line, w, h) == (8, 140, 160), f"got {line}, {w} x {h}")
    with open(os.path.join(data, "base", "prototypes", "entity", "entities.lua")) as f:
        ent = f.read()
    i = ent.index('name = "assembling-machine-3"')
    speed = float(re.search(r"crafting_speed\s*=\s*([\d.]+)", ent[i:]).group(1))
    check("assembler: crafting_speed = 1.25", speed == 1.25, f"got {speed}")
    return progress, frames, line, w, h, speed


def assembler_sheets(d, frames, line, w, h):
    """Assembler 3 as packed sheets: base frame 0 the plate, anim the animation, shifts in tiles."""
    os.makedirs(d, exist_ok=True)
    rel = "base/graphics/entity/assembling-machine-3/assembling-machine-3-"
    meta = {"checks": {}}
    png, bw, bh, (sx, sy), _ = measure.sprite_geometry(rel + "base.png")
    Image.open(png).convert("RGBA").crop((0, 0, bw, bh)).save(os.path.join(d, "base.png"))
    meta["base"] = dict(size=[bw, bh], shift=[sx / measure.PPT, sy / measure.PPT])
    png, _, _, (sx, sy), _ = measure.sprite_geometry(rel + "anim.png")
    im = Image.open(png)
    check("assembler: the anim sheet holds 64 frames", im.size == (w * line, h * math.ceil(frames / line)),
          f"got {im.size}")
    shutil.copyfile(png, os.path.join(d, "anim.png"))
    meta["anim"] = dict(size=[w, h], shift=[sx / measure.PPT, sy / measure.PPT], frames=frames, line_length=line)
    with open(os.path.join(d, "meta.json"), "w") as f:
        json.dump(meta, f)


def test_assembler(out):
    progress, frames, line, w, h, speed = assembler_source()
    sheets = os.path.join(out, "assembler-3", "sheets")
    assembler_sheets(sheets, frames, line, w, h)
    code, d, _ = measure_run(sheets, os.path.join(out, "assembler-3", "declared"), "3x3",
                             "--graphics-set", "crafting-machine", "--animation-progress", f"{progress}")
    check("assembler: exit 0", code == 0, f"exit {code}")
    t = d["motion"]["timing"]
    want = frames / progress                    # ticks a loop at crafting speed 1
    print(f"        assembler 3: loop_ticks {t['loop_ticks']} at crafting speed 1, {d['motion']['loop_frames']} drawn "
          f"frames; at its own crafting speed {speed}: {frames / (1 * speed * progress):g} ticks "
          f"(not modelled); per_tick {t['layers']['anim']['per_tick']}")
    check("assembler: 64 drawn frames, each 2 ticks, 128 ticks a loop at crafting speed 1",
          (d["motion"]["loop_frames"], t["loop_ticks"], t["frame_ticks"], t["layers"]["anim"]["per_tick"])
          == (64, want, list(range(0, 128, 2)), "1/2"), f"got {d['motion']['loop_frames']}, {t['loop_ticks']}")
    _, dflt, _ = measure_run(sheets, os.path.join(out, "assembler-3", "default"), "3x3",
                             "--graphics-set", "crafting-machine")
    check("assembler: the crafting machine's default gives the same", unlabelled(dflt) == unlabelled(d))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    test_play()
    sheets, plain, cm = test_fixture(a.out)
    test_given(a.out, sheets, plain, cm)
    test_untimed(a.out)
    test_refused(a.out)
    test_crusher(a.out)
    test_assembler(a.out)
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
