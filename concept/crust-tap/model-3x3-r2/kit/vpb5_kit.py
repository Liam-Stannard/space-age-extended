"""Copied into the Gas Pump's T15 model round (gas-pump-3x3 T15, 2026-10-28) from concept/crust-tap/model-3x3/kit/vpb5_kit.py (6ff4325); changed here: nothing. Its own first line follows.
Copied into the 3x3 Gas Pump's shipping model (gas-pump-3x3 T08, 2026-10-21) from concept/crust-tap/options/round-3x3-refine/kit/vpb5_kit.py (ba32d3d); changed here: nothing. Its own first line follows.
Copied into the Gas Pump 3x3 options round (gas-pump-3x3 T02, 2026-10-21) from the vent-pump-model worktree's concept/vent-pump/model/kit/vpb5_kit.py (a184f70); changed here: nothing. Its own first line follows.
Copied into the shipping model (T07, 2026-10-20) from options/round-5/vpb5_kit.py; changed here: the import path; the variant fixed at (a), Liam's pick (T06).

Vent Pump, round 5 (T05): the Gas Lift Tower's texture variants and the clipping fixes, over
round 4's kit (../round-4/vpb4_kit.py, itself round 3's vpb3_kit.py with the helium glass), used
unchanged: everything here wraps the kit's material functions before the model is built, so the
geometry is the same in every variant.

  --variant base | a | b | c     (default base)

  base   round 4's surfacing, with only the two clipping fixes
  a      warmer paints: each unit's paint a step warmer and fuller (the Reaction Plant model's
         ochre, oxide, green in vanilla's warmth), the finish's warm cast up
  b      heavier wear: more chipped edges, rust where it forms (seams, the feet, down from the
         bands, the bolts) heavier, a thicker dirt film and runs, more mottling
  c      cleaner, newer: few chips, little rust, a light film, less dust and grime

The clipping fixes, in every variant (Liam, T04: "Fix both in the model"):
  satin bare steel   bare steel, seams and nickel rougher and a little less metallic, so the
                     sun's glints stop short of white;
  the melt's crest   #FF9E52 (R 255 by definition) -> #F89A50, and the melt's glow scaled
                     (MELT_K 0.72) so its crest renders just under R 255 (R 245 alone, at the
                     charge's peak);
  satin floor        satin_floor(): every surface but the melt and the helium liquid held at
                     roughness >= ROUGH_MIN (0.6): layered()'s wear-through polished every chipped
                     edge to roughness 0.18 and those glinted to 255 on every unit. Specular is
                     unchanged (x0.5 took p50 from 76 to 70).
What is left clipping after these is mostly diffuse (the sunlit tops of the brightest paints under the
kit's sun of 13.5) and is rolled off on the frames by vp5_shoulder.py, reported separately.

  $BLENDER -b --python vpb5_08_gas_lift_tower.py -- <out-dir> --variant a [--quick] [--frames N]
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from vpb4_kit import *  # noqa: F401,F403,E402
import vpb4_kit as K4  # noqa: E402
import vpb3_kit as K  # noqa: E402
import vp4_glass as G  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
VARIANT = "a"                      # T06: "(a) Warmer paints"
assert VARIANT in ("base", "a", "b", "c"), VARIANT
CREST = "#F89A50"
MELT_K = float(argv[argv.index("--melt-k") + 1]) if "--melt-k" in argv else 0.72     # the crest at R 245 in the melt-only render at the charge's peak

# ---------------------------------------------------------------- the variants
PALETTE = {
    # warmer and fuller, toward the Reaction Plant model's units (ochre tank, oxide red, green) in vanilla's warmth
    "a": {"iron": "#6A5642", "iron_dk": "#523F33", "oxide": "#963220", "ochre": "#BC8624", "green": "#5C7A2C",
          "cream": "#C0A676", "grey": "#86704C"},
}
# worn_paint() scales: chips, rust, film, mottle, wiped, warm (added)
WORN = {
    "base": dict(chips=1.0, rust=1.0, film=1.0, mottle=1.0, wiped=1.0, warm=0.0),
    "a": dict(chips=1.0, rust=1.0, film=1.0, mottle=1.0, wiped=1.0, warm=0.5),
    "b": dict(chips=2.0, rust=2.6, film=1.9, mottle=3.0, wiped=0.4, warm=0.1),
    "c": dict(chips=0.15, rust=0.1, film=0.25, mottle=0.0, wiped=0.2, warm=0.0),
}
# layered() scales: wear, rust, dust, grime, drip
LAYER = {
    "base": dict(wear=1.0, rust=1.0, dust=1.0, grime=1.0, drip=1.0),
    "a": dict(wear=1.0, rust=1.0, dust=1.0, grime=1.0, drip=1.0),
    "b": dict(wear=1.9, rust=2.6, dust=1.3, grime=1.4, drip=2.0),
    "c": dict(wear=0.3, rust=0.15, dust=0.35, grime=0.4, drip=0.0),
}
SATIN = {"bare": (0.62, 0.35), "seam": (0.62, 0.35), "nickel": (0.62, 0.35)}     # name: (min roughness, max metal)
# the brightest paints a step down so a face square to the kit's sun of 13.5 stops short of 255 (T05: whole
# frame white and clipped 0); name: (paint, metal or None)
CAPS = {"yellow": ("#A8841E", None), "red": ("#8A2618", None), "hazard": ("#92782A", None),
        "lag": ("#867658", "#948468"), "bare": ("#8A8274", "#A49C8C"), "nickel": ("#8E897C", "#A6A296"),
        "seam": ("#7A7062", "#948A78"), "cable_yellow": ("#968036", "#B0A070"), "cable_red": ("#84382A", "#A06858"),
        "cable_grey": ("#46403A", "#6E665E")}
G.BAND = "#84769A"           # the helium line's ID bands, two steps under round 4's #9C8CB0
GLOSS = 0.04                 # the windows' gloss (round 4's 0.1): over the melt a sunlit pane pushed it to 255

_layered = K.layered
_paint = K.paint
_worn = K.worn_paint


def layered_v(name, paint, **kw):
    s = LAYER[VARIANT]
    for k in ("wear", "rust", "dust", "grime"):
        if k in kw:
            kw[k] = min(1.0, kw[k] * s[k])
    if "drip" in kw:
        kw["drip"] = min(1.0, kw["drip"] * s["drip"])
    if name in CAPS:
        paint, mt = CAPS[name]
        if mt and "metal" in kw:
            kw["metal"] = mt
    if name in SATIN:
        r, m = SATIN[name]
        kw["paint_rough"] = max(kw.get("paint_rough", 0.5), r)
        kw["paint_metal"] = min(kw.get("paint_metal", 0.15), m)
    return _layered(name, paint, **kw)


def paint_v(key, hexc, *a, **kw):
    return _paint(key, PALETTE.get(VARIANT, {}).get(key, hexc), *a, **kw)


def worn_v(mat, paint, chips=0.5, under="#4A4642", rust=0.5, wiped=0.4, warm=0.6, sheen=None, mottle=0.12, film=0.3):
    s = WORN[VARIANT]
    if mat.name in SATIN:
        sheen = None                     # satin: no polished patches either
    if mat.name in CAPS:
        paint = CAPS[mat.name][0]
    return _worn(mat, paint, chips=min(0.95, chips * s["chips"]), under=under, rust=min(1.0, rust * s["rust"]),
                 wiped=min(1.0, wiped * s["wiped"]), warm=min(1.0, warm + s["warm"]), sheen=sheen,
                 mottle=min(0.6, max(mottle, 0.06 if s["mottle"] > 1 else 0.0) * s["mottle"]),
                 film=min(0.9, film * s["film"]))


K.layered = layered_v
K.paint = paint_v
K.worn_paint = worn_v


def build_materials5(lead_tops=((0.6, 0.3), (1.0, 0.3))):
    K4.build_materials4(lead_tops)


def fix_melt():
    """The melt's crest just under R 255: the ramp's #FF9E52 -> CREST, the glow scaled by MELT_K."""
    crest = rig.srgb(CREST)
    old = rig.srgb("#FF9E52")
    for name, m in K.M.items():
        if K.GROUP.get(name, ("",))[0].startswith("molten") and m.node_tree:
            for nd in m.node_tree.nodes:
                if nd.type == "VALTORGB":
                    for e in nd.color_ramp.elements:
                        if all(abs(e.color[i] - old[i]) < 1e-4 for i in range(3)):
                            e.color = crest
    K.GLOWS[:] = [(s, v * MELT_K, fn) for s, v, fn in K.GLOWS]


def soften_windows():
    for name, m in K.M.items():
        if name in ("pane", "glass", "he_glass") and m.node_tree:
            for nd in m.node_tree.nodes:
                if nd.type == "MIX_SHADER":
                    nd.inputs["Fac"].default_value = GLOSS
    ce = K.M.get("ceramic")              # the gauge faces (vp4_glass.carry's ceramic): a step down
    if ce is not None:
        for nd in ce.node_tree.nodes:
            if nd.type == "BSDF_PRINCIPLED" and not nd.inputs["Base Color"].is_linked:
                nd.inputs["Base Color"].default_value = rig.srgb("#A09684")


ROUGH_MIN = float(argv[argv.index("--rough-min") + 1]) if "--rough-min" in argv else 0.6
SPEC_K = float(argv[argv.index("--spec-k") + 1]) if "--spec-k" in argv else 1.0
LIT = ("he_liquid", "he_bubble", "mask_")          # the helium's liquid and bubbles keep their own surface


def satin_floor():
    """The satin finish carried to every worn edge (T05: whole frame white and clipped 0): layered()
    wears its paint through to metal at roughness 0.18 and worn_paint() chips it at 0.4, and those
    polished chips on every unit took the sun's glint to 255. Every Principled surface here is held
    at roughness >= ROUGH_MIN (its coat too), the melt and the helium liquid excepted; colours, the
    wear's pattern and the metal itself are unchanged."""
    n = 0
    for m in bpy.data.materials:
        if not m.node_tree or m.name.startswith(LIT) or K.GROUP.get(m.name, ("",))[0].startswith("molten"):
            continue
        nt = m.node_tree
        for b in [nd for nd in nt.nodes if nd.type == "BSDF_PRINCIPLED"]:
            for sock in ("Roughness", "Coat Roughness"):
                s = b.inputs[sock]
                if s.is_linked:
                    src = s.links[0].from_socket
                    mx = nt.nodes.new("ShaderNodeMath")
                    mx.operation = "MAXIMUM"
                    mx.inputs[1].default_value = ROUGH_MIN
                    nt.links.new(src, mx.inputs[0])
                    nt.links.new(mx.outputs[0], s)
                else:
                    s.default_value = max(s.default_value, ROUGH_MIN)
            sp = b.inputs["Specular IOR Level"]
            if not sp.is_linked:
                sp.default_value *= SPEC_K
            n += 1
        for nd in nt.nodes:                       # the windows' gloss (vp4_glass._window)
            if nd.type == "BSDF_GLOSSY":
                nd.inputs["Roughness"].default_value = max(nd.inputs["Roughness"].default_value, ROUGH_MIN)
    print(f"satin floor: {n} surfaces at roughness >= {ROUGH_MIN}, specular x{SPEC_K}")


def glow_all(nf, step=3):
    """The light alone, every glow on (the melt and the helium): the sun, sky, ground and bounce off;
    glowall-NN.png every `step` frames, for criterion 9 (nothing else glows)."""
    hide = [o for o in bpy.data.objects if o.type == "LIGHT" or o.name.startswith(("ground", "bounce"))]
    keep = [o.hide_render for o in hide]
    for o in hide:
        o.hide_render = True
    bg = K.sc.world.node_tree.nodes["Background"].inputs["Strength"]
    b0 = bg.default_value
    bg.default_value = 0.0
    K.ROOT.rotation_euler = (0, 0, 0)
    for f in range(0, nf, step):
        K.pose(f / nf, True)
        rig.render(os.path.join(K.OUT, f"glowall-{f:02d}.png"))
    for o, k in zip(hide, keep):
        o.hide_render = k
    bg.default_value = b0


_catcher = rig.ground_catcher


def catcher_unlit():
    """The shadow catcher catches shadows only (T05, criterion 8): rig.ground_catcher() is a plane with no
    material (albedo 0.8) that also bounced light up onto the machine in every frame drawn over it (idle,
    working, the turns), so those frames read p50 90-92 on the plate's own px while the plate, rendered
    with the catcher hidden, read 76 (the kit's calibration: "p50 ~77 on the 1x plate"). With its diffuse,
    glossy and transmission rays off the frames as seen match the plate; rig.bounce_ground() still warms
    the undersides as before."""
    def ground_catcher(*a, **kw):
        g = _catcher(*a, **kw)
        g.visible_diffuse = g.visible_glossy = g.visible_transmission = False
        return g
    rig.ground_catcher = ground_catcher


WORLD5 = 0.44      # the sky, round 4's 0.32 lifted: with the catcher's bounce gone the frames as seen read
                   # p50 73; at 0.44 the idle frame reads p50 75, black 9.9 % (the plate 77)


def run5(meta, nf=24):
    if "--world" not in argv:
        K.WORLD = WORLD5
    catcher_unlit()
    fix_melt()
    soften_windows()
    satin_floor()
    meta = dict(meta, variant=VARIANT, crest=CREST, melt_k=MELT_K, satin=SATIN, rough_min=ROUGH_MIN, spec_k=SPEC_K, catcher_unlit=True, world=K.WORLD, gloss=GLOSS,
                band=G.BAND,
                caps=CAPS, palette=PALETTE.get(VARIANT, {}), worn=WORN[VARIANT], layer=LAYER[VARIANT])
    K.run(dict(meta, helium_glass=dict(mix="A", tanks=G.TANKS)), nf=nf)
    if K.COLMAP or K.ONLY is not None or K.CHECK:
        return
    glow_all(K.NF_ARG or nf)
    G.run4(K, lambda m, nf: None, meta, nf)      # run4's helium-only frames and the glass mask
