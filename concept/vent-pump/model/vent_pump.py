"""Vent pump (sae-vent-pump): the gas-lift wellhead, modelled from its spec.

  BLENDER=<blender 5> tools/blender/render.sh concept/vent-pump/model/vent_pump.py <out-dir> --ports --icon
  (or directly: blender -b --python vent_pump.py -- <out-dir> [--idle | --ports | --icon | --collide]
                [--samples N] [--anim-samples N] [--sun E])

  --idle     idle-, still- and working-<direction>.png only: the quick loop for the finish
  --ports    the four pipe pictures and their caps, port-<face>.png and cover-<face>.png
  --icon     icon.png: the machine facing east (frosted intake left, hot riser right, spec 16), lit
  --collide  no render: every moving part in every frame against every other part, and every
             fixed part against every other, by BVH; collide.txt and collide-model.txt in <out-dir>

Spec: concept/vent-pump/building-spec-vent-pump.md. The adopted design is v4-sheet.png and
its rotation strip, rotation-strip-v2.png (spec 19, round log: v4 locked), cut into the
plates in graphics/entity/vent-pump/: a chamfered armoured housing filling the 3x3 with
bolted corner bosses and wall buttresses, a christmas-tree valve stack in the middle (bore
collar, master valve, a cross with four wing bonnets on the diagonals, an upper valve and its
handwheel), a hot copper-stained riser with an armoured sight port on its top leaving one
face, a frost-sleeved intake entering low from the opposite face, hazard-striped hatches on
the two faces without pipes. Spec 8 and the prototype (prototypes/core/entities.lua): melt
out of the north face at [0, -1], helium in at the south face at [0, 1], straight through.

Built to the Core standard reached on the Reaction Plant (its round 5 and circulator.py): a
paint per unit (worn_paint over materials.layered, vanilla's warmth and saturation, rust only
where it forms), services and clutter (FFF #146, #350), its own pipe pictures to assembler 3's
outline in its own metal with vanilla's covers (template rules 6 and 7), every colour render
cut at the footprint's east and west edges, and --collide.

Where this model departs from the ChatGPT-era plates and spec (listed for the spec's
rewording, with Liam):
  - nothing crosses the footprint: the riser and intake end at the edge in bare fittings, and
    the engine's pipe pictures carry the pipe on into the next tile (rules 4-6, 5). The plates
    hang both pipes a tile over the edge; their frost and glow run to the flange (rule 4);
  - the plate is the machine idle -- the sight port dark, the seams unlit (spec 9, step 1);
    the melt is a working layer and the heat a glow (spec 7). The shipped prototype keeps the
    glow in the plate only because split-glow.py could not part it from copper (spec 13);
  - sixteen frames (spec 6.1, 13 and the prototype), not thirty-two (spec 9, 15): the melt
    runs two wavelengths a loop toward the outlet (spec 9, "two full travels"), and the flow
    meter's three-vane disc turns a third of a turn (spec 7, "a small flow-meter disc turning
    in the injection line"). Both seamless;
  - no cold glow and no boil-off wisp (spec 3.3, 7, 10): the adopted strip's prompt says "the
    frost is pale blue-white and does NOT glow" and "no steam ... there is no air here";
  - one amber status lamp on the stack (spec 3.3), a lens the engine tints (apply_tint status).

Units are tiles; north is +Y; the model faces north as built, and the whole of it turns
for east, south and west (spec 5: the same machine, its plumbing a quarter turn round). Nothing
here is adopted: the sheets move to graphics/ only on Liam's sign-off.
"""
import math
import os
import random
import re
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import rig  # noqa: E402
import contract  # noqa: E402
from materials import TEX, layered, hazard_pattern, _G  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0]
IDLE = "--idle" in argv
PORTS = "--ports" in argv
ICON = "--icon" in argv
COLLIDE = "--collide" in argv


def _opt(name, default):
    return type(default)(argv[argv.index(name) + 1]) if name in argv else default


SUN_E = _opt("--sun", 10.0)          # the circulator's; tuned on the measured p50 (measures.txt)
os.makedirs(OUT, exist_ok=True)
PI = math.pi
TAU = 2 * PI

# ---------------------------------------------------------------- what the packers are told
# Entity origin at the canvas centre; 5 x 5 tiles: the stack's wheel rises 0.8 tile up the
# screen, the outlet head 0.5 over the north edge, the shadow falls right.
CANVAS = (320, 320)
PORT_CANVAS = (320, 320)            # the pictures reach a tile outside every face
NF = 16                             # spec 6.1 and 13: sixteen frames, animation_speed 0.25
WAVES = 2                           # the melt's wavelengths a loop (spec 9: two full travels)

DECL = dict(
    footprint=(3, 3),
    directions="four",
    passes=[
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="still", kind="still"),
        dict(name="shadow", kind="shadow", sheet="shadow"),
        # the melt in the port and the riser's seams lit, minus the plate (spec 7: the hot glow)
        dict(name="working", kind="glow", over="idle", sheet="glow"),
        # the amber status lamp's lens, cut white for the engine to tint (spec 3.3)
        dict(name="lamp", kind="light", sheet="status-lamp"),
    ],
    animations=[
        # the melt running past the sight port: drawn only while working, over the dark port
        dict(name="melt", frames=NF, motion="flow", working=True),
        # the flow meter's three-vane disc in the injection line: a third of a turn a loop
        dict(name="meter", frames=NF, motion="turn"),
    ],
    # one picture per face, on the middle tile of each; facing north the output is on the
    # north face and the input on the south (spec 8), and turned, the same pictures serve
    ports=[dict(tile=(0, -1), face="N"), dict(tile=(1, 0), face="E"),
           dict(tile=(0, 1), face="S"), dict(tile=(-1, 0), face="W", neck=True)],
)

sc = rig.reset()
PLATE_SAMPLES = _opt("--samples", 96)
ANIM_SAMPLES = _opt("--anim-samples", 48)
sc.cycles.samples = PLATE_SAMPLES
ROOT = rig.turntable(rig.stretch_root())

# ---------------------------------------------------------------- groups
#   body    everything that stands still
#   seams   the riser's hot gasket lines (unlit in the plate, lit in the glow)
#   melt    the melt under the sight port, its slag flecks and the port's glass
#   meter   the flow meter's disc and its glass (not in the plate: the meter layer)
#   lens    the status lamp's lens
PART = {}
CUR = ["body"]
ASM = {}
_ASM = [None]
_NEXT = [0]
RUN_ENDS = {}
OBJS = []


class grp:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        CUR.append(self.name)

    def __exit__(self, *a):
        CUR.pop()


class asm:
    """with asm(): every part built inside is one assembly (a casting, a valve, a pipe run)."""

    def __enter__(self):
        self.outer = _ASM[0] is not None
        if not self.outer:
            _NEXT[0] += 1
            _ASM[0] = _NEXT[0]

    def __exit__(self, *a):
        if not self.outer:
            _ASM[0] = None


# ---------------------------------------------------------------- the finish (circulator.py's)
GRAIN = (0.94, 1.04)
BUMP = 0.08


def soften_grain(mat, lo=0.86, hi=1.1):
    """FFF #146 in numbers: narrow layered()'s photo grain on this model's own materials."""
    for nd in mat.node_tree.nodes:
        if nd.type == "MAP_RANGE" and abs(nd.inputs["To Min"].default_value - 0.7) < 1e-6 \
                and abs(nd.inputs["To Max"].default_value - 1.22) < 1e-6:
            nd.inputs["To Min"].default_value = lo
            nd.inputs["To Max"].default_value = hi
        if nd.type == "BUMP" and BUMP is not None:
            nd.inputs["Strength"].default_value = BUMP


def worn_paint(mat, paint, chips=0.5, under="#4A4642", rust=0.5, wiped=0.4, warm=0.6, sheen=None, mottle=0.12,
               film=0.3):
    """The Reaction Plant's round-5 finish, unchanged: the paint stays its colour across a
    surface and the wear is local -- chips to the metal at edges, rust in the seams, at the foot
    and down from fittings, a few wiped patches, warm-brown dirt in the contact lines."""
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    col = next(l for l in nt.links if l.to_socket == bsdf.inputs["Base Color"]).from_socket
    rough_link = next((l for l in nt.links if l.to_socket == bsdf.inputs["Roughness"]), None)
    rough = rough_link.from_socket if rough_link is not None else None
    met_link = next((l for l in nt.links if l.to_socket == bsdf.inputs["Metallic"]), None)
    g = _G(mat)
    geo = g.node("ShaderNodeNewGeometry")
    pos, normal = geo.outputs["Position"], geo.outputs["Normal"]
    ao = g.node("ShaderNodeAmbientOcclusion", Distance=0.25).outputs["AO"]
    cav = g.math("SUBTRACT", 1.0, ao)
    if mottle:
        big = g.noise(pos, 3.2, detail=5, rough=0.6, distortion=0.4)
        rm = g.math("MULTIPLY", g.remap(big, 0.6, 0.7), mottle, clamp=True)
        col = g.mixc(rm, col, rig.srgb("#5A3418"))
    if film:
        fm = g.math("MULTIPLY", g.remap(g.noise(pos, 4.5, detail=6, rough=0.62, distortion=0.3), 0.38, 0.7), film,
                    clamp=True)
        col = g.mixc(fm, col, g.mulc(col, rig.srgb("#8A7258")))
    wipe = None
    if wiped:
        wipe = g.math("MULTIPLY", g.remap(g.noise(pos, 2.4, detail=2, rough=0.4), 0.6, 0.68), wiped, clamp=True)
        clean = g.mulc(rig.srgb(paint), (1.06, 1.05, 1.02, 1.0))
        col = g.mixc(wipe, col, g.mixc(0.3, clean, col))
    if chips:
        bevel = g.node("ShaderNodeBevel", Radius=0.06).outputs[0]
        dot = g.node("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        g.l.new(bevel, dot.inputs[0])
        g.l.new(normal, dot.inputs[1])
        edge = g.remap(dot.outputs["Value"], 0.998, 0.93)
        flake = g.noise(pos, 15, detail=4, rough=0.72, distortion=0.8)
        thr = g.math("SUBTRACT", 0.63, g.math("MULTIPLY", edge, 0.14))
        bare = g.math("MULTIPLY", g.math("GREATER_THAN", flake, thr), chips, clamp=True)
        rim = g.math("MULTIPLY", g.math("GREATER_THAN", flake, g.math("SUBTRACT", thr, 0.03)), chips, clamp=True)
        col = g.mixc(rim, col, rig.srgb("#4E2A14"))
        metal = g.mixc(g.noise(pos, 60, detail=2), rig.srgb(under), g.mulc(rig.srgb(under), (1.35, 1.32, 1.28, 1)))
        rusty = g.mixc(g.noise(pos, 31, detail=3), rig.srgb("#4A230E"), rig.srgb("#7E4420"))
        metal = g.mixc(g.remap(g.noise(pos, 5.5, detail=2), 0.45, 0.55), metal, rusty)
        col = g.mixc(bare, col, metal)
        if met_link is not None:
            nt.links.new(g.mixf(bare, met_link.from_socket, 0.6), bsdf.inputs["Metallic"])
        if rough is not None:
            rough = g.mixf(bare, rough, 0.4)
    if film:
        nz0 = g.node("ShaderNodeSeparateXYZ", Vector=normal).outputs["Z"]
        st = g.node("ShaderNodeMapping", Vector=pos)
        st.inputs["Scale"].default_value = (1.0, 1.0, 0.15)
        runs = g.remap(g.image(f"{TEX}/maps/rust_streak.png", st.outputs[0], 1.6).outputs["Color"], 0.5, 0.85)
        streak = g.math("MULTIPLY", g.math("MULTIPLY", runs, g.remap(nz0, 0.6, 0.2)), 0.55 * film * 2, clamp=True)
        col = g.mixc(streak, col, g.mulc(col, rig.srgb("#7A6450")))
        nz = g.node("ShaderNodeSeparateXYZ", Vector=normal).outputs["Z"]
        down = g.math("MULTIPLY", g.remap(nz, 0.1, -0.7), 0.55 * min(1.0, film * 2), clamp=True)
        col = g.mixc(down, col, g.mulc(col, rig.srgb("#6A5440")))
        zz = g.node("ShaderNodeSeparateXYZ", Vector=pos).outputs["Z"]
        foot = g.math("MULTIPLY", g.remap(zz, 0.22, 0.03), g.remap(g.noise(pos, 8, detail=4, rough=0.6), 0.45, 0.62),
                      clamp=True)
        col = g.mixc(g.math("MULTIPLY", foot, rust, clamp=True), col,
                     g.mixc(g.noise(pos, 19, detail=3), rig.srgb("#40200C"), rig.srgb("#7A4220")))
    if rust:
        rc = g.mixc(g.noise(pos, 9, detail=4), rig.srgb("#3A1C0A"), rig.srgb("#7A4220"))
        seam = g.math("MULTIPLY", g.math("MULTIPLY", cav, 2.2),
                      g.remap(g.noise(pos, 14, detail=4), 0.35, 0.6), clamp=True)
        col = g.mixc(g.math("MULTIPLY", seam, rust, clamp=True), col, rc)
    col = g.mulc(col, (1.0 + 0.02 * warm, 1.0, 1.0 - 0.06 * warm, 1.0))
    dm = g.noise(pos, 7.5, detail=5, rough=0.6)
    col = g.mulc(col, g.gray(g.remap(dm, 0.3, 0.7, 0.8, 1.04)))
    fg = g.noise(pos, 22, detail=4, rough=0.7)
    col = g.mulc(col, g.gray(g.remap(fg, 0.3, 0.7, 0.84, 1.06)))
    dirt = g.math("MULTIPLY", cav, 1.2, clamp=True)
    if wipe is not None:
        dirt = g.math("MULTIPLY", dirt, g.math("SUBTRACT", 1.0, g.math("MULTIPLY", wipe, 0.6)))
    col = g.mixc(dirt, col, rig.srgb("#352820"))
    nt.links.new(col, bsdf.inputs["Base Color"])
    if rough is not None:
        r = rough
        if wipe is not None:
            r = g.mixf(wipe, r, 0.34)
        if sheen is not None:
            sh = g.mixf(g.remap(dm, 0.4, 0.62), sheen, min(0.8, sheen + 0.3))
            r = g.mixf(0.75, r, sh)
        nt.links.new(r, bsdf.inputs["Roughness"])
    return mat


WET = ("#3A1E0C", "#7A4018")
RUNS = ((0.5, 0.3), (0.56, 0.35), (0.74, 0.3))       # the rim, the bosses: rust runs hang from them


def heat_pattern(g):
    """The riser (spec 3.2, the adopted copper-orange): heat-stained steel gone to a copper-brown
    oxide, darker in broad scale-coloured patches, never blue (blue is the cold side's)."""
    pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
    a = g.remap(g.noise(pos, 3.0, detail=4, rough=0.6), 0.35, 0.65)
    b = g.mixc(a, rig.srgb("#5E3420"), rig.srgb("#8E5430"))
    scale = g.remap(g.noise(pos, 11, detail=3), 0.55, 0.7)
    return g.mixc(scale, b, rig.srgb("#4A2A1C"))


def frost_pattern(g):
    """Rime (spec 3.2: "pale insulating sleeve, rimed white-blue"): a pale blue-white crust,
    a faint helium cyan (#8CC7E5) in its hollows, never bright enough to read as light."""
    pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
    ao = g.node("ShaderNodeAmbientOcclusion", Distance=0.08).outputs["AO"]
    n = g.remap(g.noise(pos, 26, detail=5, rough=0.7), 0.3, 0.7)
    crust = g.mixc(n, rig.srgb("#A8BCC6"), rig.srgb("#D0DADE"))
    return g.mixc(g.remap(ao, 0.95, 0.5), crust, rig.srgb("#7FA6BC"))


M = {
    # the housing: spec 3.3's iron-nickel grey-brown, #4A463F -> #6E685C, a warm oxidised paint
    "iron": layered("iron", "#57524A", metal="#9A9284", paint_metal=0.12, paint_rough=0.58, wear=0.3,
                    rust=0.18, dust=0.35, grime=0.65, jitter=0.07, ground=0.8, ground_h=0.3, drips=RUNS,
                    drip=0.8, rust_tint=WET),
    # the deck: the same plate in the open, darker with dust and wear (the adopted deck is dark)
    "deck": layered("deck", "#2A2825", metal="#8E877A", paint_metal=0.2, paint_rough=0.55, wear=0.3,
                    rust=0.12, dust=0.2, grime=0.7, jitter=0.05, rust_tint=WET),
    # the stack's castings: the same metal a step darker, so the tree reads off the deck
    "iron_dk": layered("iron_dk", "#433F39", metal="#9A9284", paint_metal=0.2, paint_rough=0.55, wear=0.35,
                       rust=0.2, dust=0.3, grime=0.7, jitter=0.06, rust_tint=WET),
    # nickel-white machined bands and flange faces (spec 3.3 secondary #B9B4A8), sparingly
    "nickel": layered("nickel", "#ABA698", metal="#D6D2C6", paint_metal=0.8, paint_rough=0.32, wear=0.4,
                      rust=0.12, dust=0.15, grime=0.5),
    # the corner bosses and the hatch inserts: the adopted plate's worn ochre
    "ochre": layered("ochre", "#8E6A2A", metal="#5E544A", paint_metal=0.08, paint_rough=0.55, wear=0.3,
                     rust=0.15, dust=0.35, grime=0.6, jitter=0.05, drips=RUNS, drip=0.85, rust_tint=WET),
    # the junction box and the transmitter: grey-painted steel
    "grey": layered("grey", "#6E6A62", metal="#9A9488", paint_metal=0.15, paint_rough=0.55, wear=0.3,
                    rust=0.2, dust=0.35, grime=0.7, jitter=0.06, rust_tint=WET),
    "dark_steel": layered("dark_steel", "#3E3934", metal="#8C8272", paint_metal=0.35, paint_rough=0.55,
                          wear=0.4, rust=0.35, dust=0.35, grime=0.7, ground=0.8, rust_tint=WET),
    "bare": layered("bare", "#A8A090", metal="#D8D0BE", paint_metal=0.85, paint_rough=0.3, wear=0.5,
                    rust=0.16, dust=0.12, grime=0.5, ground=0.6),
    "seam": layered("seam", "#8A8070", metal="#B0A690", paint_metal=0.7, paint_rough=0.4, wear=0.3,
                    rust=0.25, dust=0.0, jitter=0.04, ground=0.7),
    "bolt": layered("bolt", "#5A4A3A", metal="#A89880", paint_metal=0.5, paint_rough=0.5, wear=0.5,
                    rust=0.75, dust=0.2, grime=0.6, rust_tint=WET),
    "heat": layered("heat", "#7A4A2C", metal="#C08A5E", paint_metal=0.6, paint_rough=0.4, wear=0.4,
                    rust=0.1, dust=0.1, grime=0.55, jitter=0.05, pattern=heat_pattern),
    "frost": layered("frost", "#C4D0D6", metal="#E0E8EA", paint_metal=0.0, paint_rough=0.78, wear=0.0,
                     rust=0.0, dust=0.0, grime=0.2, jitter=0.03, pattern=frost_pattern),
    "brass": layered("brass", "#9A7438", metal="#D0AC66", paint_metal=0.9, paint_rough=0.35, wear=0.5,
                     rust=0.1, dust=0.2),
    "hose_k": layered("hose_k", "#38302A", metal="#7A6E62", paint_metal=0.0, paint_rough=0.6, wear=0.35,
                      rust=0.0, dust=0.55, grime=0.5, jitter=0.06),
    "red": layered("red", "#A8301E", metal="#6A5A50", paint_metal=0.05, paint_rough=0.5, wear=0.35,
                   rust=0.1, dust=0.2, grime=0.4, jitter=0.04),
    "yellow": layered("yellow", "#D0A428", metal="#6A5A50", paint_metal=0.05, paint_rough=0.5, wear=0.35,
                      rust=0.1, dust=0.25, grime=0.4, jitter=0.04),
    "hazard": layered("hazard", "#B8962E", paint_metal=0.1, paint_rough=0.85, wear=0.6, rust=0.3,
                      dust=0.6, grime=0.6,
                      pattern=lambda g: g.mixc(0.25, hazard_pattern(g), (0.16, 0.12, 0.08, 1.0))),
    "stencil": layered("stencil", "#CEC2A4", metal="#5A5044", paint_metal=0.05, paint_rough=0.8, wear=0.5,
                       rust=0.2, dust=0.3, grime=0.4, jitter=0.05),
    "label": layered("label", "#D8CCAE", paint_metal=0.0, paint_rough=0.7, wear=0.2, rust=0.0, dust=0.3,
                     grime=0.3, jitter=0.08),
    "gauge": layered("gauge", "#DCD2BA", paint_metal=0.0, paint_rough=0.3, wear=0.1, rust=0.0,
                     dust=0.2, grime=0.4),
    "needle": layered("needle", "#9A2A1A", paint_metal=0.0, paint_rough=0.5, wear=0.0, rust=0.0, dust=0.0,
                      grime=0.0),
    "rubber": layered("rubber", "#26201C", metal="#4A4038", paint_metal=0.0, paint_rough=0.6, wear=0.1,
                      rust=0.0, dust=0.3, grime=0.3),
    "dark": layered("dark", "#1E1814", paint_metal=0.0, paint_rough=0.8, wear=0.0, rust=0.0, dust=0.0, grime=0.0),
}
for _n, _c, _e in (("red", "#9E4430", "#C88068"), ("yellow", "#B89440", "#DCC488"),
                   ("black", "#34302C", "#746C64"), ("grey", "#4A443E", "#7C746A")):
    M["cable_" + _n] = layered("cable_" + _n, _c, metal=_e, paint_metal=0.0, paint_rough=0.5, wear=0.3,
                               rust=0.0, dust=0.3, grime=0.4, jitter=0.05)

FINISH = {   # (paint hex, chips, under-metal, seam rust, wiped, warm, sheen, mottle, film)
    "iron": ("#57524A", 0.55, "#8A8274", 0.55, 0.25, 0.45, None, 0.12, 0.3),
    "deck": ("#2A2825", 0.3, "#8A8274", 0.5, 0.25, 0.3, None, 0.08, 0.25),
    "iron_dk": ("#433F39", 0.35, "#8A8274", 0.55, 0.2, 0.6, 0.45, 0.15, 0.3),
    "nickel": ("#ABA698", 0.0, "#D6D2C6", 0.35, 0.2, 0.5, 0.2, 0.0, 0.2),
    "ochre": ("#8E6A2A", 0.6, "#4E463E", 0.65, 0.25, 0.3, None, 0.2, 0.45),
    "grey": ("#6E6A62", 0.6, "#8A8478", 0.65, 0.25, 0.5, None, 0.2, 0.4),
    "dark_steel": ("#3E3934", 0.3, "#8C8272", 0.7, 0.15, 0.6, 0.45, 0.25, 0.2),
    "bare": ("#A8A090", 0.0, "#D8D0BE", 0.45, 0.2, 0.5, 0.2, 0.1, 0.25),
    "seam": ("#8A8070", 0.0, "#B0A690", 0.4, 0.0, 0.6, None, 0.0, 0.0),
    "bolt": ("#5A4A3A", 0.0, "#A89880", 0.8, 0.0, 0.8, None, 0.3, 0.0),
    "heat": ("#7A4A2C", 0.0, "#C08A5E", 0.3, 0.15, 0.3, 0.3, 0.0, 0.25),
    "brass": ("#9A7438", 0.0, "#D0AC66", 0.2, 0.3, 0.3, 0.28, 0.0, 0.2),
    "red": ("#A8301E", 0.5, "#6A5A50", 0.3, 0.0, 0.0, None, 0.0, 0.2),
    "yellow": ("#D0A428", 0.5, "#6A5A50", 0.3, 0.0, 0.0, None, 0.0, 0.2),
    "hazard": ("#B8962E", 0.4, "#5A4E46", 0.4, 0.0, 0.4, None, 0.1, 0.3),
    "stencil": ("#CEC2A4", 0.4, "#5A5044", 0.4, 0.0, 0.4, None, 0.0, 0.3),
}
for _k, _m in M.items():
    if GRAIN:
        soften_grain(_m, *GRAIN)
    if _k in FINISH:
        p, ch, und, ru, wi, wa, sh, mo, fi = FINISH[_k]
        worn_paint(_m, p, chips=ch, under=und, rust=ru, wiped=wi, warm=wa, sheen=sh, mottle=mo, film=fi)

# the sight port's glass: thin, low-reflection, or it mirrors the sky grey (circulator's pane)
pane = bpy.data.materials.new("pane")
pane.use_nodes = True
pb = pane.node_tree.nodes["Principled BSDF"]
pb.inputs["Base Color"].default_value = rig.srgb("#D8E4EA")
pb.inputs["Roughness"].default_value = 0.04
pb.inputs["IOR"].default_value = 1.08
pb.inputs["Transmission Weight"].default_value = 1.0
pb.inputs["Specular IOR Level"].default_value = 0.25
M["pane"] = pane

PHASES = []       # (value node, cycles a loop): set per frame
GLOWS = []        # (emission strength socket, its working value): 0 when idle
GLOW = 3.0
MELT_GLOW = 1.5                     # the melt: its crests at #FF9E52, not driven past it to yellow


def melt_material(name="melt"):
    """Molten kamacite (spec 3.3: #D96B29 -> #FF9E52 at the hottest): bands along +Y, the way
    the melt runs from the stack to the outlet, distorted by the wave's own noise; dark crust in
    the troughs. Idle (emission 0) it is a near-black glassy slag: the port is black (spec 9)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    phase = N.new("ShaderNodeValue")
    PHASES.append((phase, WAVES))
    wave = N.new("ShaderNodeTexWave")
    wave.bands_direction = "Y"
    # a wavelength of 0.105 tile: 2 pi / (20 * scale)
    wave.inputs["Scale"].default_value = TAU / (20 * 0.105)
    wave.inputs["Distortion"].default_value = 6.0
    wave.inputs["Detail"].default_value = 3.0
    wave.inputs["Detail Scale"].default_value = 1.2
    L.new(tc.outputs["Object"], wave.inputs["Vector"])
    neg = N.new("ShaderNodeMath")
    neg.operation = "MULTIPLY"
    neg.inputs[1].default_value = -1.0        # a rising phase moves the bands toward -Y; negated, +Y
    L.new(phase.outputs[0], neg.inputs[0])
    L.new(neg.outputs[0], wave.inputs["Phase Offset"])
    ramp = N.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.15, rig.srgb("#7A2A0E")
    cr.elements[1].position, cr.elements[1].color = 0.85, rig.srgb("#FF9E52")
    e = cr.elements.new(0.5)
    e.color = rig.srgb("#D96B29")
    L.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    b.inputs["Base Color"].default_value = rig.srgb("#20120C")
    b.inputs["Roughness"].default_value = 0.25
    L.new(ramp.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = MELT_GLOW
    GLOWS.append((b.inputs["Emission Strength"], MELT_GLOW))
    M[name] = m
    return m, ramp, b


MELT, MELT_RAMP, MELT_BSDF = melt_material()


def seam_material():
    """The riser's gasket lines (spec 3.2: "dull orange at the seams"): dark iron idle, lit
    #D96B29 working."""
    m = bpy.data.materials.new("hotseam")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#3A2418")
    b.inputs["Roughness"].default_value = 0.5
    b.inputs["Emission Color"].default_value = rig.srgb("#D96B29")
    b.inputs["Emission Strength"].default_value = GLOW * 0.7
    GLOWS.append((b.inputs["Emission Strength"], GLOW * 0.7))
    M["hotseam"] = m


seam_material()
M["slag"] = layered("slag", "#2A160C", paint_metal=0.0, paint_rough=0.6, wear=0, rust=0, dust=0, grime=0)

lamp = bpy.data.materials.new("lamp")
lamp.use_nodes = True
lb = lamp.node_tree.nodes["Principled BSDF"]
lb.inputs["Base Color"].default_value = rig.srgb("#C8B898")      # an amber-tinted glass, unlit
lb.inputs["Roughness"].default_value = 0.25
lb.inputs["Coat Weight"].default_value = 0.6
lb.inputs["Emission Color"].default_value = (1, 1, 1, 1)
lb.inputs["Emission Strength"].default_value = 0.0
M["lamp"] = lamp


def lamp_cut(on):
    lb.inputs["Emission Strength"].default_value = 1.0 if on else 0.0
    lb.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1) if on else rig.srgb("#C8B898")


def working(on):
    for sock, v in GLOWS:
        sock.default_value = v if on else 0.0


def flat_glow(on):
    """The glow pass: the melt lit at one strength, its bands flattened to their middle colour, so
    the glow is the same in every frame and needs no animation of its own (as the circulator's legs)."""
    nt = MELT.node_tree
    for l_ in list(nt.links):
        if l_.to_socket == MELT_BSDF.inputs["Emission Color"]:
            nt.links.remove(l_)
    if on:
        MELT_BSDF.inputs["Emission Color"].default_value = rig.srgb("#E07A32")
        MELT_BSDF.inputs["Emission Strength"].default_value = MELT_GLOW * 0.7
    else:
        nt.links.new(MELT_RAMP.outputs["Color"], MELT_BSDF.inputs["Emission Color"])


# ---------------------------------------------------------------- geometry helpers
NOICON = set()                      # the housing and the deck's services: not in the icon (spec 16)
_NOICON = [False]


def _finish(o, mat, bevel=0.012, smooth=False, parent=None):
    if _NOICON[0]:
        NOICON.add(o.name)
    o.data.materials.append(M[mat])
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments, mod.limit_method = bevel, 2, "ANGLE"
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    o.parent = parent or ROOT
    OBJS.append(o)
    PART[o.name] = CUR[-1]
    if _ASM[0] is None:
        _NEXT[0] += 1
    ASM[o.name] = _ASM[0] if _ASM[0] is not None else _NEXT[0]
    return o


def box(loc, size, mat, rz=0.0, rot=None, bevel=0.012, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot or (0, 0, rz))
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, bevel, parent=parent)


def cyl(loc, r, h, mat, rot=(0, 0, 0), verts=48, bevel=0.01, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    return _finish(bpy.context.active_object, mat, bevel, smooth=True, parent=parent)


def torus(loc, major, minor, mat, rot=(0, 0, 0), seg=48, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot,
                                     major_segments=seg, minor_segments=10)
    return _finish(bpy.context.active_object, mat, 0, smooth=True, parent=parent)


def annulus(loc, r_in, r_out, h, mat, rot=(0, 0, 0), seg=64, parent=None):
    me = bpy.data.meshes.new("annulus")
    bm = bmesh.new()
    rows = []
    for r, z in ((r_out, -h / 2), (r_out, h / 2), (r_in, h / 2), (r_in, -h / 2)):
        rows.append([bm.verts.new((r * math.cos(TAU * k / seg), r * math.sin(TAU * k / seg), z))
                     for k in range(seg)])
    for i in range(4):
        a_, b_ = rows[i], rows[(i + 1) % 4]
        for k in range(seg):
            j = (k + 1) % seg
            bm.faces.new((a_[k], a_[j], b_[j], b_[k]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("annulus", me)
    sc.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    return _finish(o, mat, 0.006, smooth=True, parent=parent)


def sphere(loc, r, mat, scale=(1, 1, 1), seg=24, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    o = bpy.context.active_object
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, 0, smooth=True, parent=parent)


def along(t):
    return Vector(t).normalized().to_track_quat("Z", "Y").to_euler()


def catmull(pts, step=0.01):
    P = [Vector(p) for p in pts]
    ext = [2 * P[0] - P[1]] + P + [2 * P[-1] - P[-2]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1:i + 3]
        n = max(2, math.ceil((p2 - p1).length / step))
        for k in range(n):
            t = k / n
            out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (3 * p1 - p0 - 3 * p2 + p3) * t * t * t))
    out.append(P[-1])
    return out


def frames(P):
    T = [(P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized() for i in range(len(P))]
    up = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0))
    N = [T[0].cross(up).normalized()]
    for i in range(1, len(P)):
        n = N[-1] - T[i] * N[-1].dot(T[i])
        N.append(n.normalized() if n.length > 1e-6 else N[-1])
    B = [t.cross(n) for t, n in zip(T, N)]
    return T, N, B


def sweep(P, r, mat, corr=0.0, pitch=0.03, seg=16):
    T, N, B = frames(P)
    s = [0.0]
    for a_, b_ in zip(P, P[1:]):
        s.append(s[-1] + (b_ - a_).length)
    me = bpy.data.meshes.new("sweep")
    bm = bmesh.new()
    rings = []
    for i, p in enumerate(P):
        rr = r * (1 + corr * (0.5 + 0.5 * math.cos(TAU * s[i] / pitch)))
        rings.append([bm.verts.new(p + rr * (math.cos(TAU * k / seg) * N[i]
                                             + math.sin(TAU * k / seg) * B[i])) for k in range(seg)])
    for a_, b_ in zip(rings, rings[1:]):
        for k in range(seg):
            j = (k + 1) % seg
            bm.faces.new((a_[k], a_[j], b_[j], b_[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("sweep", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, 0, smooth=True), P, T, s


def hose(pts, r=0.03, mat="hose_k"):
    """A small corrugated instrument hose, crimped ferrules and nuts at both ends."""
    with asm():
        P = catmull(pts)
        RUN_ENDS[_ASM[0]] = (P[0], P[-1])
        sweep(P, r, mat, corr=0.08, pitch=0.035, seg=12)
        for p, q in ((P[0], P[1]), (P[-1], P[-2])):
            t = (p - q).normalized()
            cyl(tuple(p - t * 0.03), r * 1.35, 0.06, "bare", rot=along(t), verts=16, bevel=0.004)
            cyl(tuple(p + t * 0.003), r * 1.7, 0.025, "brass", rot=along(t), verts=6, bevel=0.0)
    return P


def bundle(pts, cols=("black", "yellow"), r=0.012):
    with asm():
        P = catmull(pts)
        RUN_ENDS[_ASM[0]] = (P[0], P[-1])
        T, N, B = frames(P)
        s = [0.0]
        for a_, b_ in zip(P, P[1:]):
            s.append(s[-1] + (b_ - a_).length)
        n = len(cols)
        for k, c in enumerate(cols):
            off = [r * 1.3 * (math.cos(TAU * k / n + 9 * s[i]) * N[i]
                              + math.sin(TAU * k / n + 9 * s[i]) * B[i]) for i in range(len(P))]
            sweep([p + o for p, o in zip(P, off)], r, "cable_" + c, seg=8)
        nxt = 0.15
        for i, p in enumerate(P):
            if s[i] >= nxt and s[i] < s[-1] - 0.08:
                cyl(tuple(p), r * 2.9, 0.035, "label", rot=along(T[i]), verts=12, bevel=0.002)
                nxt += 0.45


def bolts(cx, cy, z, R, n, r=0.018, mat="bolt", a0=0.0):
    for i in range(n):
        a = a0 + TAU * i / n
        cyl((cx + R * math.cos(a), cy + R * math.sin(a), z), r, 0.022, mat, verts=6, bevel=0)


def bolts_on(c, axis, R, n, r=0.016, a0=0.0, h=0.02):
    """A bolt ring on a flange facing `axis`, its heads standing on the face at c."""
    t = Vector(axis).normalized()
    u = t.cross(Vector((0, 0, 1)))
    u = u.normalized() if u.length > 1e-6 else Vector((1, 0, 0))
    w = t.cross(u)
    for i in range(n):
        a = a0 + TAU * (i + 0.5) / n
        p = Vector(c) + R * (math.cos(a) * u + math.sin(a) * w) + t * h / 2
        cyl(tuple(p), r, h, "bolt", rot=along(t), verts=6, bevel=0)


def rivet(loc, r=0.015):
    return sphere(loc, r, "bolt", scale=(1, 1, 0.7), seg=8)


def nut(loc, r, h, rot):
    o = cyl(loc, r, h, "bare", rot=rot, verts=6, bevel=0)
    o.rotation_euler.rotate_axis("Z", random.uniform(0, PI / 3))
    return o


def prism(pts, z0, z1, mat, bevel=0.025, cutters=()):
    """A block on a polygon footprint (x, y pairs, anticlockwise), from z0 to z1, with boxes
    (centre, size) cut out of it."""
    me = bpy.data.meshes.new("prism")
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, z0)) for x, y in pts]
    hi = [bm.verts.new((x, y, z1)) for x, y in pts]
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("prism", me)
    sc.collection.objects.link(o)
    cut(o, cutters)
    return _finish(o, mat, bevel)


def ring_prism(outer, inner, z0, z1, mat, bevel=0.012, cutters=()):
    """A band between two polygons (the same number of corners), z0 to z1."""
    me = bpy.data.meshes.new("ring")
    bm = bmesh.new()
    n = len(outer)
    ol = [bm.verts.new((x, y, z0)) for x, y in outer]
    oh = [bm.verts.new((x, y, z1)) for x, y in outer]
    il = [bm.verts.new((x, y, z0)) for x, y in inner]
    ih = [bm.verts.new((x, y, z1)) for x, y in inner]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ol[i], ol[j], oh[j], oh[i]))
        bm.faces.new((ih[i], ih[j], il[j], il[i]))
        bm.faces.new((oh[i], oh[j], ih[j], ih[i]))
        bm.faces.new((il[i], il[j], ol[j], ol[i]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("ring", me)
    sc.collection.objects.link(o)
    cut(o, cutters)
    return _finish(o, mat, bevel)


def cut(o, cutters):
    """Boolean the boxes out of o and apply, before the bevel goes on."""
    if not cutters:
        return
    bpy.context.view_layer.objects.active = o
    for c, s in cutters:
        bpy.ops.mesh.primitive_cube_add(size=1, location=c)
        k = bpy.context.active_object
        k.scale = s
        bpy.ops.object.transform_apply(scale=True)
        mod = o.modifiers.new("cut", "BOOLEAN")
        mod.operation, mod.solver, mod.object = "DIFFERENCE", "EXACT", k
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(k)


def octagon(a, c):
    return [(a - c, -a), (a, -a + c), (a, a - c), (a - c, a), (-a + c, a), (-a, a - c), (-a, -a + c), (-a + c, -a)]


def gauge(loc, facing, r=0.06):
    """A brass-cased gauge: a cream face, a red needle lying on it."""
    with asm():
        t = Vector(facing).normalized()
        cyl(loc, r, 0.03, "brass", rot=along(t), verts=24, bevel=0.004)
        cyl(tuple(Vector(loc) + t * 0.017), r * 0.8, 0.006, "gauge", rot=along(t), verts=24, bevel=0)
        u = t.cross(Vector((0, 0, 1)))
        u = u.normalized() if u.length > 1e-6 else Vector((1, 0, 0))
        v = u.cross(t).normalized()
        d = (u * math.cos(0.6) + v * math.sin(0.6)).normalized()
        tt = (t - d * t.dot(d)).normalized()
        box(tuple(Vector(loc) + t * 0.022 + d * r * 0.2), (r * 0.9, 0.006, 0.01), "needle",
            rot=tuple(Matrix((d, tt, d.cross(tt))).transposed().to_euler()), bevel=0)


def handwheel(loc, r=0.27, mat="nickel", spokes=6):
    """The stack's handwheel (spec 3.2: hand-wheel valve caps): a rim, spokes, a hub."""
    with asm():
        torus(loc, r, 0.03, mat, seg=48)
        for k in range(spokes):
            a = TAU * k / spokes
            o = Vector((math.cos(a), math.sin(a), 0))
            cyl(tuple(Vector(loc) + o * r / 2), 0.015, r, mat, rot=along(o), verts=8, bevel=0)
        cyl(loc, 0.045, 0.05, "iron_dk", verts=16)
        cyl((loc[0], loc[1], loc[2] + 0.03), 0.022, 0.03, "bare", verts=6, bevel=0)


# ======================================================================= the model, facing north
A, C = 1.40, 0.34                  # the housing: half-width, corner chamfer
ZH = 0.46                          # the housing's top
ZD = 0.50                          # the deck's top
ZR = 0.56                          # the rim's top
ZA = 0.42                          # the pipe axis at the edge (the drill's, assembler 3's pictures)
RA = 0.20                          # the intake's bore
RR = 0.20                          # the riser's bore
ZRS = 0.98                         # the riser's axis
EDGE = 1.5
E3 = EDGE - 0.005                  # a wall's face at the footprint edge, less a hair
# the intake's trench: the low pipe lies in it (spec 3.1, "entering low")
TRENCH = ((0.0, -0.95, 0.66), (0.70, 1.3, 1.0))
# the riser's outlet head: a cast elbow standing at the north edge (spec 3.1, "elbowing out to the
# pipe connection"); its north wall is where the picture butts
HEAD = (0.30, 1.0, 1.40, 1.14)     # half-width, its south face, its north face, its top
# the sight port: the window's opening along the riser (y), half-width across (x)
WIN_Y0, WIN_Y1, WIN_X = 0.50, 0.90, 0.085
STACK_R = 0.33


def housing():
    with asm():
        # the body: one armoured block filling the footprint, its corners chamfered (FFF #350)
        prism(octagon(A, C), 0.0, ZH, "iron", bevel=0.03, cutters=(TRENCH,))
        # the deck inside the rim and the rim round it; the rim parts for the trench and the head
        prism(octagon(A - 0.16, C - 0.07), ZH, ZD, "deck", bevel=0.01, cutters=(TRENCH,))
        ring_prism(octagon(A, C), octagon(A - 0.16, C - 0.07), ZH, ZR, "iron", bevel=0.012,
                   cutters=(TRENCH, ((0, 1.32, 0.6), (0.62, 0.3, 0.3))))
        # an inner octagon of seam strips on the deck (the adopted plate's raised panel line)
        oc = octagon(0.86, 0.3)
        for i in range(8):
            (x0, y0), (x1, y1) = oc[i], oc[(i + 1) % 8]
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            if abs(mx) < 0.4 and abs(my) > 0.5:
                continue                   # not across the trench, nor under the head
            L = math.hypot(x1 - x0, y1 - y0)
            box((mx, my, ZD + 0.006), (L, 0.025, 0.012), "seam", rz=math.atan2(y1 - y0, x1 - x0), bevel=0.003)
        # rivet rows along the rim's inner edge
        for i in range(8):
            (x0, y0), (x1, y1) = octagon(A - 0.08, C - 0.035)[i], octagon(A - 0.08, C - 0.035)[(i + 1) % 8]
            n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 0.16))
            for k in range(1, n):
                x, y = x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n
                if abs(x) < 0.4 and abs(y) > 1.0:
                    continue
                rivet((x, y, ZR + 0.004))
        # buttresses down every wall (the adopted plate's ribs), clear of each face's middle tile
        for s in (-1, 1):
            for u in (0.62, 0.98):
                for ax in ("x", "y"):
                    if ax == "x":
                        loc, size = (s * u, -A - 0.04, 0.25), (0.1, 0.08, 0.5)
                        locn = (s * u, A + 0.04, 0.25)
                    else:
                        loc, size = (-A - 0.04, s * u, 0.25), (0.08, 0.1, 0.5)
                        locn = (A + 0.04, s * u, 0.25)
                    for L_ in (loc, locn):
                        box(L_, size, "iron", bevel=0.01)
                        bx, by = L_[0] + (0.02 if L_[0] > 1 else -0.02 if L_[0] < -1 else 0), \
                            L_[1] + (0.02 if L_[1] > 1 else -0.02 if L_[1] < -1 else 0)
                        cyl((bx, by, 0.515), 0.022, 0.03, "bolt", verts=6, bevel=0)
        # the corner bosses: square bolted blocks set on the chamfers, ochre-worn, a hazard face
        for sx in (-1, 1):
            for sy in (-1, 1):
                cx, cy = sx * 1.12, sy * 1.12
                box((cx, cy, (ZH + 0.76) / 2), (0.34, 0.34, 0.76 - ZH), "ochre", rz=PI / 4, bevel=0.02)
                box((cx, cy, 0.77), (0.24, 0.24, 0.025), "dark_steel", rz=PI / 4, bevel=0.005)
                cyl((cx, cy, 0.79), 0.05, 0.04, "bolt", verts=6, bevel=0)
                n_ = Vector((sx, sy, 0)).normalized()
                box((cx + n_.x * 0.172, cy + n_.y * 0.172, 0.62), (0.2, 0.012, 0.16), "hazard",
                    rz=math.atan2(n_.y, n_.x) + PI / 2, bevel=0)
        # the faces without pipes (east and west, facing north): long hatches on the rim with
        # hazard inserts (the adopted plate's side panels)
        for s in (-1, 1):
            box((s * (A - 0.08), 0, ZR + 0.02), (0.13, 1.0, 0.04), "dark_steel", bevel=0.008)
            box((s * (A - 0.08), 0, ZR + 0.043), (0.07, 0.86, 0.008), "hazard", bevel=0)
            for y in (-0.44, 0.44):
                rivet((s * (A - 0.08), y, ZR + 0.045))
            # and a stencil plate on the wall under it
            box((s * (A + 0.006), 0, 0.3), (0.012, 0.42, 0.1), "stencil", bevel=0.002)
        # the rim's bolted blocks (the adopted plate's studded perimeter), clear of the middle tiles
        for s in (-1, 1):
            for u in (0.62, 0.98):
                for x, y, rz in ((s * u, -(A - 0.08), 0), (s * u, A - 0.08, 0), (-(A - 0.08), s * u, PI / 2),
                                 (A - 0.08, s * u, PI / 2)):
                    box((x, y, ZR + 0.05), (0.18, 0.13, 0.1), "iron_dk", rz=rz, bevel=0.012)
                    box((x, y, ZR + 0.106), (0.15, 0.1, 0.012), "nickel", rz=rz, bevel=0.004)
                    cyl((x, y, ZR + 0.12), 0.026, 0.02, "bolt", verts=6, bevel=0)
        # bolted inspection plates on the deck's four diagonals
        for sx in (-1, 1):
            for sy in (-1, 1):
                cx, cy = sx * 0.74, sy * 0.74
                box((cx, cy, ZD + 0.012), (0.34, 0.2, 0.024), "iron_dk", rz=sx * sy * PI / 4, bevel=0.006)
                q = Matrix.Rotation(sx * sy * PI / 4, 3, "Z")
                for dx, dy in ((-0.13, -0.065), (0.13, -0.065), (-0.13, 0.065), (0.13, 0.065)):
                    v = q @ Vector((dx, dy, 0))
                    cyl((cx + v.x, cy + v.y, ZD + 0.03), 0.014, 0.014, "bolt", verts=6, bevel=0)
        # the trench's floor saddles, under the intake
        for y in (-1.3, -0.82):
            box((0, y, 0.16 + 0.02), (0.36, 0.1, 0.04), "dark_steel", bevel=0.006)


def stack():
    """The christmas tree over the bore (spec 3.2): collar, master valve, cross with four wing
    bonnets on the diagonals, upper valve, handwheel; the riser's nozzle north, the injection
    boss south and low."""
    with asm():
        # the bore collar, gasketed and bolted to the deck
        cyl((0, 0, ZD + 0.05), 0.56, 0.1, "iron_dk", verts=72)
        torus((0, 0, ZD + 0.1), 0.47, 0.016, "rubber", seg=64)
        bolts(0, 0, ZD + 0.11, 0.52, 16, r=0.022)
        # the master valve body
        cyl((0, 0, 0.74), 0.28, 0.24, "iron_dk", verts=48)
        cyl((0, 0, 0.865), 0.35, 0.05, "nickel", verts=64)
        bolts(0, 0, 0.895, 0.32, 12, r=0.017)
        # the cross
        cyl((0, 0, 1.01), 0.36, 0.26, "iron_dk", verts=64)
        for k in range(4):
            a = PI / 4 + k * PI / 2
            d = Vector((math.cos(a), math.sin(a), 0))
            cyl(tuple(Vector((0, 0, 1.0)) + d * 0.45), 0.14, 0.24, "iron_dk", rot=along(d), verts=32)
            cyl(tuple(Vector((0, 0, 1.0)) + d * 0.58), 0.17, 0.04, "nickel", rot=along(d), verts=32)
            bolts_on(tuple(Vector((0, 0, 1.0)) + d * 0.6), d, 0.135, 6, r=0.015)
            cyl(tuple(Vector((0, 0, 1.0)) + d * 0.615), 0.055, 0.03, "bare", rot=along(d), verts=6, bevel=0)
        # the riser's nozzle (north) at the riser's axis
        cyl((0, 0.36, ZRS), RR + 0.01, 0.12, "iron_dk", rot=(PI / 2, 0, 0), verts=48)
        # the upper valve, its flange, the bonnet, the stem
        cyl((0, 0, 1.15), 0.31, 0.05, "nickel", verts=64)
        bolts(0, 0, 1.18, 0.28, 12, r=0.016)
        cyl((0, 0, 1.25), 0.24, 0.16, "iron_dk", verts=48)
        cyl((0, 0, 1.34), 0.27, 0.03, "nickel", verts=48)
        cyl((0, 0, 1.42), 0.15, 0.14, "iron_dk", verts=32)
        cyl((0, 0, 1.53), 0.035, 0.1, "bare", verts=12)
        # the injection boss: low on the south, where the helium goes down the bore
        cyl((0, -0.57, ZA), RA + 0.03, 0.3, "iron_dk", rot=(PI / 2, 0, 0), verts=48)
        cyl((0, -0.72, ZA), RA + 0.08, 0.05, "nickel", rot=(PI / 2, 0, 0), verts=48)
        bolts_on((0, -0.745, ZA), (0, -1, 0), RA + 0.05, 8, r=0.014)
        # a gauge tap low on the master valve's south face, its gauge looking up the screen
        cyl((0, -0.32, 0.74), 0.045, 0.1, "bare", rot=(PI / 2, 0, 0), verts=12)
    gauge((0, -0.39, 0.79), (0, -1, 0.9), r=0.055)
    handwheel((0, 0, 1.585))
    # the cable's gland on the upper flange
    with asm():
        a = -PI / 5
        x, y = 0.285 * math.cos(a), 0.285 * math.sin(a)
        cyl((x, y, 1.205), 0.036, 0.04, "dark_steel", verts=16)
        cyl((x, y, 1.232), 0.022, 0.016, "bare", verts=6, bevel=0)
    # the amber status lamp (spec 3.3), on the stack's axis above the handwheel: the building turns
    # whole, and anywhere off the axis the stack hides it in one direction or another
    with asm():
        cyl((0, 0, 1.645), 0.032, 0.03, "dark_steel", verts=16)
        with grp("lens"):
            sphere((0, 0, 1.672), 0.03, "lamp", seg=12)


def riser():
    """The production riser (spec 3.2): bare heat-stained pipe leaving the stack high, the
    armoured sight port on its top, flange joints whose gaskets glow, into the outlet head."""
    with asm():
        RUN_ENDS[_ASM[0]] = (Vector((0, 0.36, ZRS)), Vector((0, HEAD[1], ZRS)))
        y0, y1 = 0.42, HEAD[1]
        cyl((0, (y0 + y1) / 2, ZRS), RR, y1 - y0, "heat", rot=(PI / 2, 0, 0), verts=48)
        for yf in (0.44, 0.96):
            for dy in (-0.022, 0.022):
                cyl((0, yf + dy, ZRS), RR + 0.055, 0.032, "heat", rot=(PI / 2, 0, 0), verts=48)
            bolts_on((0, yf + 0.04, ZRS), (0, 1, 0), RR + 0.035, 8, r=0.013)
            with grp("seams"):
                torus((0, yf, ZRS), RR + 0.03, 0.012, "hotseam", rot=(PI / 2, 0, 0), seg=48)
        # the sight port's armoured frame: two long bars and two cross bars on the pipe's crown
        zt = ZRS + RR
        for s in (-1, 1):
            box((s * (WIN_X + 0.025), (WIN_Y0 + WIN_Y1) / 2, zt + 0.005), (0.05, WIN_Y1 - WIN_Y0 + 0.1, 0.08),
                "dark_steel", bevel=0.006)
            for y in (WIN_Y0 + 0.02, (WIN_Y0 + WIN_Y1) / 2, WIN_Y1 - 0.02):
                rivet((s * (WIN_X + 0.025), y, zt + 0.047), 0.012)
        # the end straps bridge the melt: the flecks run on under them, where they wrap unseen
        for y in (WIN_Y0 - 0.025, WIN_Y1 + 0.025):
            box((0, y, zt + 0.031), (2 * WIN_X + 0.1, 0.05, 0.038), "dark_steel", bevel=0.006)
        # the melt under the glass, and the glass (the melt layer)
        with grp("melt"):
            box((0, (WIN_Y0 + WIN_Y1) / 2, zt - 0.012), (2 * WIN_X, WIN_Y1 - WIN_Y0 + 0.04, 0.035), "melt", bevel=0)
            box((0, (WIN_Y0 + WIN_Y1) / 2, zt + 0.022), (2 * WIN_X + 0.01, WIN_Y1 - WIN_Y0 + 0.01, 0.006), "pane",
                bevel=0)
    # slag flecks riding the melt toward the outlet, each the window's length once a loop
    rnd = random.Random(7)
    fl = []
    with grp("melt"):
        for i in range(5):
            with asm():
                o = sphere((0, 0, 0), rnd.uniform(0.011, 0.017), "slag", scale=(1, 1.4, 0.35), seg=10)
            fl.append((o, rnd.uniform(-0.6, 0.6), rnd.random()))
    zt = ZRS + RR

    def pose(t):
        for o, x, ph in fl:
            u = (ph + t) % 1.0
            o.location = (x * WIN_X, WIN_Y0 - 0.02 + (WIN_Y1 - WIN_Y0 + 0.04) * u, zt + 0.0055)
    POSES.append(pose)


def outlet_head():
    """The cast elbow at the north edge: the riser turns down in it to the port at ZA."""
    hw, ys, yn, top = HEAD
    with asm():
        box((0, (ys + yn) / 2, (ZD + top) / 2), (2 * hw, yn - ys, top - ZD), "dark_steel", bevel=0.04)
        box((0, (ys + yn) / 2, top + 0.015), (2 * hw - 0.08, yn - ys - 0.08, 0.03), "nickel", bevel=0.008)
        for x in (-hw + 0.07, hw - 0.07):
            for y in (ys + 0.07, yn - 0.07):
                cyl((x, y, top + 0.04), 0.02, 0.025, "bolt", verts=6, bevel=0)
        box((0, ys - 0.004, top - 0.05), (2 * hw - 0.04, 0.008, 0.05), "hazard", bevel=0)
        # the wall it stands in at the edge: the plate the north picture butts against
        box((0, E3 - 0.05, ZA + 0.02), (0.86, 0.1, 0.8), "iron", bevel=0.012)
    gauge((0.17, (ys + yn) / 2, top + 0.075), (0, -0.35, 1), r=0.05)


def intake():
    """The injection line (spec 3.2): a bare spool at the edge (rule 4: the fitting is plain
    machine metal), then the frost sleeve, ribbed and rimed, into the injection boss."""
    with asm():
        RUN_ENDS[_ASM[0]] = (Vector((0, -E3, ZA)), Vector((0, -0.745, ZA)))
        # the wall flange at the edge and the spool through it
        annulus((0, -E3 + 0.03, ZA), RA - 0.01, RA + 0.13, 0.05, "nickel", rot=(PI / 2, 0, 0))
        bolts_on((0, -E3 + 0.055, ZA), (0, 1, 0), RA + 0.09, 10, r=0.014)
        cyl((0, -1.31, ZA), RA, 0.36, "bare", rot=(PI / 2, 0, 0), verts=48)
        for dy in (-0.02, 0.02):
            cyl((0, -1.12 + dy, ZA), RA + 0.07, 0.035, "dark_steel", rot=(PI / 2, 0, 0), verts=48)
        bolts_on((0, -1.10, ZA), (0, 1, 0), RA + 0.045, 8, r=0.013)
        # the frost sleeve: lagging thick with rime, banded
        y0, y1 = -1.09, -0.75
        cyl((0, (y0 + y1) / 2, ZA), RA + 0.035, y1 - y0, "frost", rot=(PI / 2, 0, 0), verts=48)
        for k in range(4):
            y = y0 + 0.04 + (y1 - y0 - 0.08) * k / 3
            torus((0, y, ZA), RA + 0.04, 0.016, "frost", rot=(PI / 2, 0, 0), seg=40)
    # the rime: a crust of crystals over the sleeve's crown, heaviest where it meets the warm
    # boss (spec 3.2, "a visible frost bloom where it meets the warm stack")
    rnd = random.Random(11)
    with asm():
        for i in range(60):
            y = rnd.uniform(-1.08, -0.7)
            bloom = max(0.0, (y + 0.86) / 0.16)
            a = rnd.uniform(0.15, PI - 0.15)
            r0 = RA + 0.045 + 0.01 * bloom
            x, z = r0 * math.cos(a), ZA + r0 * math.sin(a)
            s = rnd.uniform(0.008, 0.014) * (1 + 0.6 * bloom)
            sphere((x, y, z), s, "frost", scale=(1.3, rnd.uniform(1.0, 2.0), 0.45), seg=8)
        for i in range(26):
            a = rnd.uniform(0.0, PI)
            r0 = RA + 0.09
            sphere((r0 * math.cos(a), -0.715 - rnd.uniform(0, 0.03), ZA + r0 * math.sin(a)),
                   rnd.uniform(0.01, 0.018), "frost", scale=(1.2, 0.7, 0.6), seg=8)
    # the flow meter on the sleeve's crown (spec 7): a bolted cup, the three-vane disc turning in it
    mx, my = 0.0, -0.92
    zb = ZA + RA + 0.035
    with asm():
        annulus((mx, my, zb + 0.04), 0.075, 0.11, 0.1, "nickel")
        cyl((mx, my, zb + 0.005), 0.11, 0.03, "dark_steel", verts=32, bevel=0.004)
        cyl((mx, my, zb + 0.06), 0.074, 0.01, "dark_steel", verts=32, bevel=0)
        bolts(mx, my, zb + 0.095, 0.093, 6, r=0.011)
    with grp("meter"):
        root = bpy.data.objects.new("meter", None)
        sc.collection.objects.link(root)
        root.parent = ROOT
        root.location = (mx, my, zb + 0.074)
        with asm():
            cyl((0, 0, 0.002), 0.02, 0.012, "brass", verts=12, bevel=0, parent=root)
            for k in range(3):
                a = TAU * k / 3
                box((0.036 * math.cos(a), 0.036 * math.sin(a), 0), (0.064, 0.03, 0.006), "yellow", rz=a,
                    bevel=0, parent=root)
            box((0.05, 0, 0.0035), (0.016, 0.03, 0.002), "red", bevel=0, parent=root)   # one vane marked

    def pose(t):
        root.rotation_euler = (0, 0, -TAU / 3 * t)        # a third of a turn a loop: three vanes
    POSES.append(pose)
    METER.append(root)


def services():
    """FFF #146: hoses and cables, a junction box, a transmitter -- the machine in service."""
    # the junction box on the deck, east of the stack, its cables to the lamp and to the meter
    jx, jy = 0.97, -0.3
    with asm():
        box((jx, jy, ZD + 0.13), (0.22, 0.3, 0.26), "grey", bevel=0.01)
        box((jx - 0.111, jy, ZD + 0.15), (0.01, 0.2, 0.16), "dark_steel", bevel=0.003)
        box((jx - 0.117, jy + 0.05, ZD + 0.2), (0.004, 0.08, 0.03), "label", bevel=0)
        cyl((jx, jy + 0.08, ZD + 0.28), 0.022, 0.05, "bare", verts=8)
        cyl((jx, jy - 0.08, ZD + 0.28), 0.022, 0.05, "bare", verts=8)
    a = -PI / 5
    lx, ly = 0.285 * math.cos(a), 0.285 * math.sin(a)
    bundle([(jx, jy + 0.08, ZD + 0.3), (jx - 0.12, jy + 0.12, ZD + 0.52), (0.55, -0.12, 1.18),
            (lx + 0.05, ly, 1.205)], cols=("black", "yellow"))
    bundle([(jx, jy - 0.08, ZD + 0.3), (jx - 0.2, -0.72, 0.62), (0.3, -0.92, 0.7), (0.115, -0.92, 0.715)],
           cols=("grey", "red"))
    # a thermocouple lead off the riser's flange into the box
    bundle([(0.27, 0.44, ZRS), (0.5, 0.25, 0.85), (jx, jy + 0.15, ZD + 0.28)], cols=("yellow",), r=0.011)
    # the pressure transmitter south-west, its hose off the SW wing's cap
    tx, ty = -0.82, -0.5
    with asm():
        box((tx, ty, ZD + 0.08), (0.18, 0.14, 0.16), "grey", bevel=0.008)
        cyl((tx, ty, ZD + 0.19), 0.04, 0.06, "brass", verts=12)
    gauge((tx, ty - 0.073, ZD + 0.1), (0, -1, 0.3), r=0.04)
    d = Vector((-1, -1, 0)).normalized()
    p0 = Vector((0, 0, 0.88)) + d * 0.42
    hose([tuple(p0), tuple(p0 + d * 0.08 + Vector((0, 0, -0.2))), (-0.66, -0.5, ZD + 0.06),
          (tx + 0.06, ty + 0.02, ZD + 0.1), (tx + 0.02, ty, ZD + 0.2), (tx, ty, ZD + 0.23)], r=0.02)
    # a helium relief valve standing on the injection boss, its vent stub turned down
    with asm():
        cyl((0.12, -0.66, ZA + 0.25), 0.04, 0.1, "brass", verts=16)
        cyl((0.12, -0.66, ZA + 0.32), 0.05, 0.03, "bare", verts=6, bevel=0)
        cyl((0.12, -0.66, ZA + 0.36), 0.025, 0.05, "red", verts=12)
        cyl((0.12, -0.66, ZA + 0.16), 0.03, 0.1, "bare", verts=12)
    # oil and slag stains on the deck where hands and spills go (rust where it forms)
    for x, y, rx, ry in ((0.55, 0.62, 0.16, 0.1), (-0.62, 0.48, 0.12, 0.09), (0.62, -0.95, 0.1, 0.07)):
        with asm():
            bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, ZD + 0.002))
            o = bpy.context.active_object
            o.scale = (rx * 2, ry * 2, 1)
            bpy.ops.object.transform_apply(scale=True)
            o.visible_shadow = False
            STAINS.append(o)
            _finish(o, "oil", 0)


STAINS = []
POSES = []
METER = []
OIL = bpy.data.materials.new("oil")
OIL.use_nodes = True
_ot = OIL.node_tree
_ob = _ot.nodes["Principled BSDF"]
_ob.inputs["Base Color"].default_value = rig.srgb("#1E1610")
_ob.inputs["Roughness"].default_value = 0.35
_g = _G(OIL)
_tc = _g.node("ShaderNodeTexCoord")
_r = _g.node("ShaderNodeVectorMath")
_r.operation = "LENGTH"
_g.l.new(_tc.outputs["Generated"], _r.inputs[0])
_sub = _g.node("ShaderNodeVectorMath")
_sub.operation = "SUBTRACT"
_g.l.new(_tc.outputs["Generated"], _sub.inputs[0])
_sub.inputs[1].default_value = (0.5, 0.5, 0.5)
_len = _g.node("ShaderNodeVectorMath")
_len.operation = "LENGTH"
_g.l.new(_sub.outputs[0], _len.inputs[0])
_edge = _g.math("ADD", _len.outputs["Value"],
                _g.math("MULTIPLY", _g.node("ShaderNodeTexNoise", Scale=6.0).outputs["Fac"], 0.25))
_alpha = _g.math("MULTIPLY", _g.remap(_edge, 0.55, 0.3), 0.55, clamp=True)
_g.l.new(_alpha, _ob.inputs["Alpha"])
M["oil"] = OIL

random.seed(3)
_NOICON[0] = True
housing()
_NOICON[0] = False
stack()
riser()
outlet_head()
intake()
_NOICON[0] = True
services()
_NOICON[0] = False


def set_pose(f):
    t = (f % NF) / NF
    for p_ in POSES:
        p_(t)
    for node, k in PHASES:
        node.outputs[0].default_value = TAU * k * t


# ======================================================================= the pipe pictures
# Assembler 3's outline for each face, in this building's metal (template rules 6 and 7, as the
# circulator's): the picture's plate is a dark-steel slab cut to the outline, lifted onto the
# plane the stub stands in, the stub and its end ring at the axis. port-<face> open (a dark
# bore), cover-<face> capped; the covers the prototype uses are vanilla's (pipecoverspictures()).
VANILLA = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/assembling-machine-3")
H_AXIS_V = 1.0 / 64
V_AXIS_U = 0.5 / 64
H_RING_R = 26 / 64 / 1.118
V_RING_R = 25.5 / 64
HC = ZR                      # the south wall's height there: the rim
GROUPS = {}


def vanilla_mask(face, tile):
    stem = os.path.join(VANILLA, f"assembling-machine-3-pipe-{face}")
    bx, by = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)",
                                           open(stem + ".lua").read()).groups())
    img = bpy.data.images.load(stem + ".png", check_existing=True)
    w, h = img.size
    px = list(img.pixels)
    drawn = {(i, j) for j in range(h) for i in range(w) if px[((h - 1 - j) * w + i) * 4 + 3] > 127 / 255}
    n8 = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
    grown = {(i + a, j + b) for i, j in drawn for a, b in n8}
    drawn = {(i, j) for i, j in grown if all((i + a, j + b) in grown for a, b in n8)} | drawn
    dx, dy = contract.FACES[face]
    tx, ty = tile[0] + dx, tile[1] + dy
    return drawn, (tx + bx / 32) * 64 - w / 2, (ty + by / 32) * 64 - h / 2


def slab(face, tile, lift, mat="dark_steel"):
    drawn, x0, y0 = vanilla_mask(face, tile)
    me = bpy.data.meshes.new(f"slab-{face}")
    bm = bmesh.new()
    corners = {}

    def corner(i, j):
        if (i, j) not in corners:
            corners[(i, j)] = bm.verts.new(lift((x0 + i) / 64, -(y0 + j) / 64))
        return corners[(i, j)]
    for i, j in drawn:
        bm.faces.new((corner(i, j + 1), corner(i + 1, j + 1), corner(i + 1, j), corner(i, j)))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(f"slab-{face}", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, 0)


def fitting(p, cap):
    face, tile = p["face"], p["tile"]
    g = f"{'cover' if cap else 'port'}-{face}"
    first = len(OBJS)
    cx, cy = tile[0], -tile[1]
    if face == "S":
        yw = -(E3 + 0.035)

        def lift(u, v):
            z = 2 * (v - yw)
            return Vector((u, yw, z)) if z <= HC else Vector((u, yw + (v - yw - HC / 2), HC + 0.004))
        slab(face, tile, lift, "dark_steel")
        ax = (PI / 2, 0, 0)
        x = cx + V_AXIS_U
        for k in range(11):
            rivet((x - 0.36 + 0.072 * k, yw - 0.012, HC - 0.06), 0.017)
        for z in (0.12, 0.36):
            for sx_ in (-0.39, 0.39):
                rivet((x + sx_, yw - 0.012, z), 0.017)
        ye = -(EDGE + 0.03) - ZA / 2
        annulus((x, yw - 0.03, ZA), 0.3, 0.42, 0.05, "bare", rot=ax)
        for k in range(14):
            t = TAU * k / 14
            rivet((x + 0.37 * math.cos(t), yw - 0.06, ZA + 0.37 * math.sin(t)), 0.016)
        cyl((x, (yw + ye) / 2, ZA), 0.28, abs(ye - yw), "bare", rot=ax, verts=48, bevel=0.0)
        cyl((x, ye + 0.03, ZA), V_RING_R - 0.02, 0.06, "bare", rot=ax, verts=48, bevel=0.01)
        for k in range(8):
            t = TAU * (k + 0.5) / 8
            nut((x + 0.33 * math.cos(t), ye - 0.002, ZA + 0.33 * math.sin(t)), 0.02, 0.014, ax)
        cyl((x, ye - 0.003, ZA), 0.2 if not cap else V_RING_R - 0.06, 0.006, "dark" if not cap else "bare",
            rot=ax, verts=32, bevel=0.0)
    elif face == "N":
        yw = E3 + 0.035

        def lift(u, v):
            return Vector((u, yw, 2 * (v - yw)))
        slab(face, tile, lift, "dark_steel")
        for k in range(7):
            t = 0.35 + (PI - 0.7) * k / 6
            u, v = cx + V_AXIS_U + 0.3 * math.cos(t), EDGE + 0.2 * math.sin(t)
            rivet((u, yw - 0.015, 2 * (v - yw)), 0.016)
    else:
        sgn = 1 if face == "E" else -1
        x0 = sgn * (EDGE - 0.28)

        def lift(u, v):
            z = ZA - sgn * 1.6 * (u - x0)
            return Vector((u, v - z / 2, z))
        slab(face, tile, lift, "dark_steel")
        ya = cy + H_AXIS_V - ZA / 2
        ax = (0, PI / 2, 0)
        xf = sgn * (EDGE - 0.03)
        cyl(((x0 + xf) / 2, ya, ZA), 0.24, abs(xf - x0), "bare", rot=ax, verts=48, bevel=0.0)
        cyl((xf, ya, ZA), H_RING_R - 0.02, 0.045, "bare", rot=ax, verts=48, bevel=0.006)
        for k in range(8):
            t = TAU * (k + 0.5) / 8
            nut((xf - sgn * 0.025, ya + 0.27 * math.cos(t), ZA + 0.27 * math.sin(t)), 0.018, 0.012, ax)
    GROUPS[g] = OBJS[first:]


# ---------------------------------------------------------------- lights
SUN = rig.sun(SUN_E)
SUN.data.color = (1.0, 0.94, 0.82)     # a warm white (round 5)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.24

LAYERS = ("meter",)                     # the moving parts not in the plate
SHOW_ALL = ("body", "seams", "melt", "lens", "meter")


def members(*groups):
    return [o for o in OBJS if PART[o.name] in groups]


def setup(visible=(), catchers=(), holdouts=(), ground=False, unseen=()):
    for o in OBJS:
        g = PART[o.name]
        o.hide_render = not (g in visible or g in catchers or g in holdouts or g in unseen)
        o.is_shadow_catcher = g in catchers
        o.is_holdout = g in holdouts
        o.visible_camera = g not in unseen
    GROUND.hide_render = not ground
    BOUNCE.hide_render = ground


# ---------------------------------------------------------------- --collide
DEEP = 0.03
DETAIL_MATS = {"bolt", "seam", "stencil", "hazard", "label", "gauge", "needle", "red", "yellow", "brass", "dark",
               "lamp", "oil", "hotseam", "pane", "rubber"}
MEANT = [
    (r"^melt$", "", r"\[(melt|pane|heat)\]", "a slag fleck riding the melt, under the port's glass"),
    (r"^meter$", "", r"\[(dark_steel|nickel)\] at \(\+0\.00,-0\.92", "the disc in its cup"),
]
MEANT_FIXED = []


def seated(a, b, inside_pts):
    for x, y in ((a, b), (b, a)):
        for xr, yr, why in MEANT_FIXED:
            if re.search(xr, x.desc) and re.search(yr, y.desc):
                return why
    if ASM.get(a.o.name) == ASM.get(b.o.name):
        return "one assembly's own parts"
    for x, y in ((a, b), (b, a)):
        if x.mat in DETAIL_MATS or x.mat.startswith("cable_"):
            return f"a {x.mat} detail on its host"
        if x.size < 0.16:
            return "a small fitting on its host"
    for x, y in ((a, b), (b, a)):
        ends = RUN_ENDS.get(ASM.get(x.o.name))
        if ends:
            pts = inside_pts(x, y) or inside_pts(y, x)
            if pts and all(min((p_ - ends[0]).length, (p_ - ends[1]).length) < 0.45 for p_ in pts):
                return "a pipe or hose's end let into what it serves"
    return None


def collide_check():
    """As the circulator's: every moving part in every frame against every fixed part and every
    other layer's moving parts, then the fixed model part against part. The model turns rigidly
    for east, south and west, so facing north is every direction."""
    from mathutils.bvhtree import BVHTree
    lines = []

    def out(s_):
        print(s_)
        lines.append(s_)
    RI = ROOT.matrix_world.inverted()

    def mat_of(o):
        return o.data.materials[0].name if getattr(o.data, "materials", None) and o.data.materials else "-"

    def world_mesh(o):
        dg = bpy.context.evaluated_depsgraph_get()
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ev.matrix_world
        vs = [mw @ v.co for v in me.vertices]
        ps = [tuple(p_.vertices) for p_ in me.polygons]
        ev.to_mesh_clear()
        return vs, ps

    def aabb(vs):
        xs, ys, zs = zip(*vs)
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def meet(a, b):
        return all(a[0][i] <= b[1][i] and b[0][i] <= a[1][i] for i in range(3))

    def inside(tree, p_):
        d = Vector((0.5774, 0.5771, 0.5777))
        n, o = 0, p_.copy()
        for _ in range(64):
            hit = tree.ray_cast(o, d)
            if hit[0] is None:
                break
            n += 1
            o = hit[0] + d * 1e-5
        return n % 2 == 1

    class Part:
        def __init__(self, o):
            self.o = o
            self.vs, ps = world_mesh(o)
            self.box = aabb(self.vs) if self.vs else None
            self.tree = BVHTree.FromPolygons(self.vs, ps) if ps else None
            c = RI @ (sum(self.vs, Vector()) / len(self.vs)) if self.vs else Vector()
            lo, hi = (RI @ Vector(self.box[0]), RI @ Vector(self.box[1])) if self.vs else (c, c)
            self.lo = Vector((min(lo.x, hi.x), min(lo.y, hi.y), min(lo.z, hi.z)))
            self.hi = Vector((max(lo.x, hi.x), max(lo.y, hi.y), max(lo.z, hi.z)))
            self.c = c
            self.size = max(abs(hi.x - lo.x), abs(hi.y - lo.y), abs(hi.z - lo.z))
            self.desc = f"{o.name}[{mat_of(o)}] at ({c.x:+.2f},{c.y:+.2f},{c.z:.2f})"
            self.mat = mat_of(o)

    def clash(a, b):
        if a.tree is None or b.tree is None or not meet(a.box, b.box):
            return None
        if a.tree.overlap(b.tree):
            return "cross"
        if meet(b.box, (a.vs[0], a.vs[0])) and inside(b.tree, a.vs[0]):
            return "inside"
        if meet(a.box, (b.vs[0], b.vs[0])) and inside(a.tree, b.vs[0]):
            return "contains"
        return None

    meshes = [o for o in OBJS if o.type == "MESH" and o not in STAINS]
    m0, moving = {}, set()
    for f in range(NF):
        set_pose(f)
        bpy.context.view_layer.update()
        for o in meshes:
            m = o.matrix_world.copy()
            if o.name not in m0:
                m0[o.name] = m
            elif any(abs(m[i][j] - m0[o.name][i][j]) > 1e-6 for i in range(4) for j in range(4)):
                moving.add(o.name)
    out(f"COLLIDE {len(meshes)} parts, {len(moving)} moving; frames 0-{NF - 1}")
    fixed_cache, hits = {}, {}
    for f in range(NF):
        set_pose(f)
        bpy.context.view_layer.update()
        mv = [o for o in meshes if o.name in moving]
        fx = [o for o in meshes if o.name not in moving]
        for o in fx:
            if o.name not in fixed_cache:
                fixed_cache[o.name] = Part(o)
        mparts = [(PART[o.name], Part(o)) for o in mv]
        for lab, a in mparts:
            for o in fx:
                kind = clash(a, fixed_cache[o.name])
                if kind:
                    hits.setdefault((lab, a.desc if lab != "melt" else "fleck", fixed_cache[o.name].desc, kind),
                                    []).append(f)
        for i, (la, a) in enumerate(mparts):
            for lb_, b in mparts[i + 1:]:
                if la == lb_:
                    continue
                kind = clash(a, b)
                if kind:
                    hits.setdefault((la, a.desc, lb_ + ": " + b.desc, kind), []).append(f)
    n_meant = n_clash = 0
    for (g, ad, bd, kind), fs in sorted(hits.items(), key=lambda kv: kv[0]):
        why = next((w for gr, ar, br, w in MEANT if re.search(gr, g) and re.search(ar, ad) and re.search(br, bd)),
                   None)
        n_meant += bool(why)
        n_clash += not why
        fr = f"{fs[0]}-{fs[-1]}" if fs == list(range(fs[0], fs[-1] + 1)) else ",".join(map(str, fs))
        out(f"COLLIDE {'meant' if why else 'CLASH'} moving [{g}] {ad} x {bd}: {kind}, frames {fr}" +
            (f"  ({why})" if why else ""))
    out(f"COLLIDE moving: {n_clash} clashes, {n_meant} meant contacts")

    set_pose(0)
    bpy.context.view_layer.update()
    fixed = [fixed_cache[o.name] for o in meshes if o.name in fixed_cache]

    def depth(a, b):
        d = 0.0
        for v in a.vs:
            if meet(b.box, (v, v)) and inside(b.tree, v):
                hit = b.tree.find_nearest(v)
                if hit[0] is not None:
                    d = max(d, (RI.to_3x3() @ (hit[0] - v)).length)
        return d

    def inside_pts(x, y):
        return [RI @ v for v in x.vs if meet(y.box, (v, v)) and inside(y.tree, v)]
    pairs, n_real, n_deep = [], 0, 0
    for i, a in enumerate(fixed):
        for b in fixed[i + 1:]:
            kind = clash(a, b)
            if not kind:
                continue
            why = seated(a, b, inside_pts)
            dp = max(depth(a, b), depth(b, a)) if why is None else 0.0
            tag = "seated" if why else ("REAL" if dp > DEEP else "touch")
            n_real += tag == "REAL"
            n_deep += tag == "touch"
            pairs.append((tag, -dp, f"{tag} {a.desc} x {b.desc}: {kind}, {dp:.3f} deep" + (f"  ({why})" if why else "")))
    order = {"REAL": 0, "touch": 1, "seated": 2}
    with open(os.path.join(OUT, "collide-model.txt"), "w") as f_:
        f_.write("\n".join(l_ for _, _, l_ in sorted(pairs, key=lambda p_: (order[p_[0]], p_[1], p_[2]))) + "\n")
    out(f"COLLIDE model: {len(fixed)} fixed parts, {len(pairs)} touching pairs: {n_real} reach more than "
        f"{DEEP} tile into each other and no rule explains them (REAL), {n_deep} touch at under {DEEP} "
        f"(collide-model.txt)")
    with open(os.path.join(OUT, "collide.txt"), "w") as f_:
        f_.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- the cut and the windows
def cut_to_footprint(path):
    """Clear every pixel of a colour render outside the footprint's east and west edges
    (+-1.5 tiles): the plate is at most 3.000 tiles wide. Returns the pixels cleared."""
    import numpy as np
    img = bpy.data.images.load(path)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)
    k = w // CANVAS[0]
    x0 = (CANVAS[0] // 2 - 96) * k
    x1 = (CANVAS[0] // 2 + 96) * k
    n = int((a[:, :x0, 3] > 0).sum() + (a[:, x1:, 3] > 0).sum())
    if n:
        a[:, :x0, :] = 0.0
        a[:, x1:, :] = 0.0
        img.pixels.foreach_set(a.ravel())
        img.filepath_raw = path
        img.file_format = "PNG"
        img.save()
    bpy.data.images.remove(img)
    return n


def over_black(path):
    """The glow pass flattened onto black (the circulator's): its colour is the light alone."""
    import numpy as np
    img = bpy.data.images.load(path)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)
    a[:, :, :3] *= a[:, :, 3:4]
    a[:, :, 3] = 1.0
    img.pixels.foreach_set(a.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


CUT = {}


def render(path, cut=True):
    rig.render(path)
    if cut:
        CUT[os.path.basename(path)] = cut_to_footprint(path)


def window(objs, pad=(0.15, 0.15, 0.25, 0.2)):
    """The render border (sprite px) round objs' projection over every frame, padded (left,
    down, right, up, tiles) for the shadows they cast."""
    cam = sc.camera
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for f in range(NF):
        set_pose(f)
        bpy.context.view_layer.update()
        for o in objs:
            if o.type != "MESH":
                continue
            ev = o.evaluated_get(dg)
            for c in ev.bound_box:
                p_ = inv @ (ev.matrix_world @ Vector(c))
                xs.append(p_.x)
                ys.append(p_.y)
    set_pose(0)
    ppt = rig.PX_PER_TILE
    W, Hc = CANVAS
    x0 = max(0, int(W / 2 + (min(xs) - pad[0]) * ppt))
    x1 = min(W, int(W / 2 + (max(xs) + pad[2]) * ppt) + 1)
    y0 = max(0, int(Hc / 2 - (max(ys) + pad[3]) * ppt))
    y1 = min(Hc, int(Hc / 2 - (min(ys) - pad[1]) * ppt) + 1)
    return x0, y0, x1, y1


def border(win):
    W, Hc = CANVAS
    x0, y0, x1, y1 = win
    sc.render.use_border = True
    sc.render.use_crop_to_border = False
    sc.render.border_min_x, sc.render.border_max_x = x0 / W, x1 / W
    sc.render.border_min_y, sc.render.border_max_y = 1 - y1 / Hc, 1 - y0 / Hc


def no_border():
    sc.render.use_border = False


# ---------------------------------------------------------------- --collide
if COLLIDE:
    collide_check()
    print("done")
    sys.exit(0)

# ---------------------------------------------------------------- --ports
if PORTS:
    random.seed(4)
    for p_ in DECL["ports"]:
        fitting(p_, cap=False)
        fitting(p_, cap=True)
    BOUNCE = rig.bounce_ground()
    contract.declare(OUT, canvas=PORT_CANVAS, **DECL)
    rig.camera(*PORT_CANVAS)
    for f_ in "NESW":
        for kind in ("port", "cover"):
            show = set(map(id, GROUPS[f"{kind}-{f_}"]))
            for o in OBJS:
                o.hide_render = id(o) not in show
            rig.render(os.path.join(OUT, f"{kind}-{f_}.png"))
    print("done")
    sys.exit(0)

GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()

# ---------------------------------------------------------------- --icon
if ICON:
    # spec 16: the valve stack with its cold end and its hot end, the base plate dropped ("at 32 px
    # it is a grey smudge") -- facing east, the frosted intake on the left and the riser on the
    # right, lit, on the plate's camera, framed to fill the square
    sc.cycles.samples = 128
    cam = rig.camera(1024, 1024, ss=1)
    ROOT.rotation_euler.z = -PI / 2
    set_pose(0)
    working(True)
    for o in OBJS:
        o.hide_render = o in STAINS or o.name in NOICON
        o.is_holdout = False
    GROUND.hide_render = True
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for o in OBJS:
        if o.hide_render or o.type != "MESH":
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        for v in me.vertices:
            p_ = inv @ (ev.matrix_world @ v.co)
            xs.append(p_.x)
            ys.append(p_.y)
        ev.to_mesh_clear()
    span = max(max(xs) - min(xs), max(ys) - min(ys)) / 0.94
    cam.data.ortho_scale = span
    cam.data.shift_x = (max(xs) + min(xs)) / 2 / span
    cam.data.shift_y = (max(ys) + min(ys)) / 2 / span
    rig.render(os.path.join(OUT, "icon.png"))
    print(f"icon: {span:.2f} tiles across")
    print("done")
    sys.exit(0)

# ---------------------------------------------------------------- the passes, per direction
rig.camera(*CANVAS)
if not IDLE:
    contract.declare(OUT, canvas=CANVAS, **DECL)
WINDOWS = {}
for d in contract.each_direction(ROOT, DECL["directions"]):
    def path(stem, d=d):
        return os.path.join(OUT, contract.named(stem, d) + ".png")
    bpy.context.view_layer.update()
    no_border()
    set_pose(0)
    working(False)
    sc.cycles.samples = PLATE_SAMPLES
    # the plate: the machine idle -- the port dark, the seams unlit, the meter's disc unseen in the
    # scene (its shadow and reflections are the plate's, so frame 0 matches the still)
    setup(visible=("body", "seams", "melt", "lens"), unseen=LAYERS)
    render(path("idle"))
    setup(visible=SHOW_ALL)
    render(path("still"))
    # the glow: the melt flattened and lit, the seams lit, everything else held out
    working(True)
    flat_glow(True)
    setup(visible=("melt", "seams"), holdouts=("body", "lens"), unseen=LAYERS)
    render(path("working"))
    over_black(path("working"))
    flat_glow(False)
    working(False)
    if IDLE:
        continue
    setup(visible=SHOW_ALL, ground=True)
    for o in OBJS:
        o.visible_camera = False
    render(path("shadow"), cut=False)
    setup(visible=("lens",), holdouts=("body", "seams", "melt", "meter"))
    lamp_cut(True)
    render(path("lamp"))
    lamp_cut(False)
    sc.cycles.samples = ANIM_SAMPLES
    # the meter: its disc and glass alone, everything else holding out what stands in front
    win = window(members("meter"))
    WINDOWS[f"meter-{d}"] = win
    border(win)
    for f in range(NF):
        set_pose(f)
        setup(visible=("meter",), holdouts=("body", "seams", "melt", "lens"))
        render(path(contract.frame("meter", f)))
    # the melt: lit and running, drawn only while working over the plate's dark port
    working(True)
    win = window(members("melt"), pad=(0.08, 0.08, 0.08, 0.08))
    WINDOWS[f"melt-{d}"] = win
    border(win)
    for f in range(NF):
        set_pose(f)
        setup(visible=("melt",), holdouts=("body", "seams", "lens") + LAYERS)
        render(path(contract.frame("melt", f)))
    working(False)
    no_border()
    set_pose(0)

with open(os.path.join(OUT, "model.json"), "w") as f_:
    import json
    json.dump(dict(windows=WINDOWS, cut=CUT, frames=NF, waves=WAVES,
                   samples=dict(plate=PLATE_SAMPLES, anim=ANIM_SAMPLES),
                   groups={g: len(members(g)) for g in SHOW_ALL}, sun=SUN_E), f_, indent=1)
print("cut past the footprint's edges (px with alpha, per render):", {k: v for k, v in CUT.items() if v})
print("done")
