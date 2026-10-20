"""Reaction plant (sae-reaction-plant): F, the Circulator, at 5x5 -- in four directions (T06).

  BLENDER=<blender 5> tools/blender/render.sh concept/reaction-plant/model/four-way/circulator.py <out-dir>
  (or directly: blender -b --python circulator.py -- <out-dir> [--idle | --probe | --collide]
                [--samples N] [--anim-samples N])

  --idle     idle-<d>.png, still-<d>.png and working-<d>.png only (frame 0), every direction
  --probe    frame 0 of every layer alone in every direction at 8 samples, and how many px each
             draws: a layer the camera never sees in some direction is refused by pack.py
  --collide  no render: every moving part in every frame of every layer against every other
             part, and every fixed part against every other, by BVH; collide.txt in <out-dir>.
             A direction's own parts (its fittings and connector socket) are tested against the
             rest of the model and never against another direction's

The signed-off model (concept/reaction-plant/model/circulator.py, Liam 2026-10-19 "Sign off",
83fe586) turned to face each direction, as vanilla's chemical plant and oil refinery are: one
model, the camera and sun fixed, the building turned on its turntable (contract.each_direction).
Liam, 2026-10-20: "The model should be adjusted so the pipe connections make sense and follow
the flow of the fluid/gas through the model. We could draw a model for each rotation rotate like
factorio does for some of the vanilla models"; the connector: "All of them - the model should
cater for them". This reverses spec 5's one plate. What changes from the signed-off model, and
nothing else:

  - no engine pipe pictures: a real fitting is modelled at each of the three connections in
    every direction (12), on the vanilla pipe's centreline for the face it lands on as turned
    (FITTINGS); each is built for that direction alone and turned back into the model, so it
    casts its own shadow and takes the building's. The covers stay vanilla's;
  - each input's line leads to where it is used (LEADS): both inputs enter the north header
    (the exchanger) and leave it from its crown straight above the fitting, the west one to
    the feed drum's crown (the solution, under sae-radiant-precipitation), the east one to the
    crust-gas compressor; the output leaves the filtrate receiver's flank, as before;
  - a circuit connector socket per direction (SOCKETS), on the wall that faces the camera:
    north and east on the instrument house (candidate 2), south and west on the scrubber's
    foot (candidate 3); the engine's own connector sprite is drawn over it.

Everything else -- every part, colour, finish, light, layer, frame count and motion -- is the
signed-off model's, unchanged. Units are tiles; north is +Y. Nothing is adopted here: the
sheets move to graphics/ only on Liam's sign-off.

The signed-off model's own notes follow.

Spec: concept/reaction-plant/building-spec-reaction-plant.md (agreed 2026-10-11): 0 gates,
3 visual design, 6.2 the six motions, 7 layers, 8 constraints, 11-13 sheets, 15 QA. Built
from the signed-off concept: options/round-5/r5_circulator.py (the model and its finish,
"The colours are good") with the animation set as fixed in options/animation/.
The plate (pass "idle", sheet base) is the machine with every moving part of the
animation taken out and the legs unlit; the still is the whole machine at frame 0; each
layer is its moving parts alone, the rest of the machine holding out what it stands in
front of. The moving parts stand unseen in the plate's scene at frame 0, so their shadows
and reflections are the plate's and frame 0 matches the still.
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
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))
import rig  # noqa: E402
import contract  # noqa: E402
from materials import TEX, layered, hazard_pattern, _G  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0]
IDLE = "--idle" in argv
PORTS = "--ports" in argv
ICON = "--icon" in argv
PROBE = "--probe" in argv
# The direction this run renders (render.sh passes the model nothing but its out-dir and flags, so
# it is read from the environment): RP_DIRECTION=north|east|south|west renders that direction alone,
# declared as one direction with its own layers (SEEN); unset, --idle and --probe render all four
# for a look, and a full run is refused.
RUN_DIR = os.environ.get("RP_DIRECTION", "")
if RUN_DIR and RUN_DIR not in dict(contract.DIRECTIONS["four"]):
    sys.exit(f"RP_DIRECTION={RUN_DIR!r} is not north, east, south or west")
COLLIDE = "--collide" in argv


def _opt(name, default):
    return type(default)(argv[argv.index(name) + 1]) if name in argv else default


# round 5's sun was 8.8 (round 4's 8.0 left p95 short). The plate here is the machine without
# the animation's moving parts, and with the fixes it measured p50 74 at 8.8, under the spec's
# 75-81 (spec 0, gate 3): 9.1 (+3 %) brings it back; 9.3 measured p50 77, p95 167
SUN_E = _opt("--sun", 9.1)
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- what the packers are told
# The canvas has the entity origin at its centre (contract.py). Above it: the plate rises
# 0.78 tile over the north edge (3.28 tiles, 210 px); below, the south edge (160 px) and the
# stains at the feet; east, the shadow (the reactor's reaches ~190 px). 416 x 480.
CANVAS = (416, 480)
PORT_CANVAS = (448, 448)            # the pictures reach a tile outside every face
NF = 24                             # the 24-frame loops (spec 6.2): ~1.7 s at 14 fps
PRESS_NF = 16                       # the filter press, once per craft
PRESS_LAND = 10                     # the frame the cake lands in the drop box: the sound accent
STROKE = 0.18                       # the press's opening stroke, tiles, west


def _smooth(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


# 16 unique frames: 0 closed (the plate), 1-4 the press opens, 5 the cake hangs, 6-9 it peels
# and falls (gravity at 14 fps), 10 it is in the box (the accent), 11-15 the press closes.
PRESS_OPEN = [0.0, _smooth(1 / 4), _smooth(2 / 4), _smooth(3 / 4), 1, 1, 1, 1, 1, 1, 1,
              1 - _smooth(1 / 6), 1 - _smooth(2 / 6), 1 - _smooth(3 / 6), 1 - _smooth(4 / 6), 1 - _smooth(5 / 6)]
# the cake's fall below its foot, tiles (None: not drawn); it shows once the gap is wider than it
PRESS_FALL = [None, None, None, 0.0, 0.0, 0.0, 0.025, 0.10, 0.225, 0.40, None, None, None, None, None, None]
PRESS_TILT = [0, 0, 0, 0, 0, 0, 2, 4, 5, 5, 0, 0, 0, 0, 0, 0]       # degrees, away from its leaf
PRESS_PATH = [[round(-STROKE * PRESS_OPEN[k], 6), 0.0, 0.0] for k in range(PRESS_NF)]


def _turned_path(path, deg):
    """A model-space path turned deg clockwise with the building (x east, y north)."""
    out = []
    for x, y, z in path:
        for _ in range(deg // 90):
            x, y = y, -x
        out.append([round(x, 6) + 0.0, round(y, 6) + 0.0, z])
    return out
# one layer per coupling and per double dial (2026-10-12; they were two layers, "couplings"
# and "gauges", whose crops round far-apart parts were mostly empty)
COUPLINGS = ("coupling-compressor", "coupling-dosing", "coupling-pump")
GAUGES = ("gauge-reactor-upper", "gauge-reactor-lower", "gauge-scrubber")
# a moving part the camera never sees: the compressor's coupling, wholly behind the legs and the
# compressor's motor in every frame (rendered alone with the rest held out, 24 frames: alpha 0
# in every pixel, 2026-10-12). It turns in the scene (and in --collide), stands unseen in the
# plate's, and has no sheet: an empty layer would draw nothing and pack.py refuses one.
HIDDEN = ("coupling-compressor",)
# Turned, some moving parts face away from the camera. A layer the camera does not see in a
# direction has no sheet there (pack.py refuses an empty layer, and the engine draws a
# direction's own layers: Animation4Way, a working_visualisation's north/east/south/west_animation);
# its parts stand in that direction's plate at frame 0, unseen behind what hides them. Each
# direction is therefore rendered as its own run with the layers seen in it. From --probe
# (2026-10-20: frame 0 of each layer alone, px over half alpha at 4x; under 40, a px or two at 1x,
# is not a motion anyone sees, and north keeps the signed-off set exactly):
#   north  every layer but coupling-compressor (0), as signed off; drip 47
#   east   all nine and coupling-compressor (76): dosing 133, gauges 100 / 61 / 87, drip 209
#   south  coupling-compressor 323, drip 40; not coupling-dosing (0) nor any gauge (0, 0, 0):
#          the dials face away
#   west   coupling-dosing 83, gauge-reactor-lower 65; not coupling-compressor (0),
#          gauge-reactor-upper (24), gauge-scrubber (0) nor drip (0)
ALL_LAYERS = ("drive",) + COUPLINGS + ("press",) + GAUGES + ("drip",)
UNSEEN = {
    "north": ("coupling-compressor",),
    "east": (),
    "south": ("coupling-dosing",) + GAUGES,
    "west": ("coupling-compressor", "gauge-reactor-upper", "gauge-scrubber", "drip"),
}
if RUN_DIR:
    HIDDEN = UNSEEN[RUN_DIR]
PRESS_PATH_RUN = _turned_path(PRESS_PATH, dict(contract.DIRECTIONS["four"])[RUN_DIR] if RUN_DIR else 0)

DECL = dict(
    footprint=(5, 5),
    directions="one",               # one run a direction (RP_DIRECTION): see SEEN
    passes=[
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="still", kind="still"),
        dict(name="shadow", kind="shadow", sheet="shadow"),
        # the legs lit at one strength (spec 6.1), lit minus the plate: the legs only (spec 7)
        dict(name="working", kind="glow", over="idle", sheet="legs-glow"),
        # the two status lamps' lenses, cut white for the engine to tint (spec 7)
        dict(name="lamp", kind="light", sheet="status-lamp"),
    ],
    animations=[
        # the solution going round: drawn only while crafting, over the plate's dark legs
        dict(name="legs", frames=NF, motion="flow", working=True),
        dict(name="drive", frames=NF, motion="cycle"),
        # the three couplings and the three double dials: each its own layer, cropped tight
        # round its own moving pixels (the amendment of 2026-10-12)
        *[dict(name=n_, frames=NF, motion="cycle") for n_ in COUPLINGS if n_ not in HIDDEN],
        # the leaf pack and tail stand slide west on the rails (held to PRESS_PATH, measured
        # on the pack alone: press-pack-NN); the cake falls on its own
        # (in a one-direction run of the turned building the path is declared as it moves there,
        # turned as the building is: PRESS_PATH_RUN)
        dict(name="press", frames=PRESS_NF, motion="slide", path=PRESS_PATH_RUN, track="pack"),
        *[dict(name=n_, frames=NF, motion="cycle") for n_ in GAUGES if n_ not in HIDDEN],
        *([dict(name="drip", frames=NF, motion="cycle")] if "drip" not in HIDDEN else []),
    ],
    # no engine pipe pictures: the fittings are in the plate, one per connection per direction
    ports=[],
)

sc = rig.reset()
PLATE_SAMPLES = _opt("--samples", 96)          # round 5's
ANIM_SAMPLES = _opt("--anim-samples", 48)
sc.cycles.samples = PLATE_SAMPLES
ROOT = rig.turntable(rig.stretch_root())
PI = math.pi

# ---------------------------------------------------------------- groups
# Every part belongs to one group; the passes show, catch on or hold out whole groups.
#   body     everything that stands still (the plate)
#   legs     the glass, the solution and its bubbles and flecks (in the plate unlit; the
#            legs layer lit, moving)
#   lens     the two status lamps' lenses
#   drive, coupling-*, press, gauge-*, drip: the moving parts of each layer (not in the plate)
#   pack     the press's leaf pack and tail stand, also in "press": rendered alone, measured
PART = {}                           # object name -> group
CUR = ["body"]
ICON_SET = set()                    # the parts the icon draws: the reactor, its legs, the drive
_ICON = [False]


class grp:
    """with grp("legs"): every part built inside belongs to that group."""

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        CUR.append(self.name)

    def __exit__(self, *a):
        CUR.pop()


class icon_parts:
    def __enter__(self):
        _ICON[0] = True

    def __exit__(self, *a):
        _ICON[0] = False


# ---------------------------------------------------------------- the signature finish, warmed
# Heights (z_top, run length) the bloom hangs from: the reactor's bands and its head
# flange, the scrubber's bands. World z, so one material serves every vessel.
BLOOM_TOPS = ((0.5, 0.32), (1.25, 0.42), (2.0, 0.42), (2.62, 0.5), (3.05, 0.4), (0.95, 0.3), (1.65, 0.4))


def lead_finish(tops=BLOOM_TOPS, bloom=1.0, gain=1.0):
    """Weathered lead sheet (round 4's, unchanged): a dull warm grey in sheets of slightly
    different age; the bloom -- the white salts lead grows where the solution weeps -- a
    dry cream hanging in runs below every band and flange and crusted in the seams."""
    def pat(g):
        geo = g.node("ShaderNodeNewGeometry")
        pos, nrm = geo.outputs["Position"], geo.outputs["Normal"]
        z = g.node("ShaderNodeSeparateXYZ", Vector=pos).outputs["Z"]
        nz = g.node("ShaderNodeSeparateXYZ", Vector=nrm).outputs["Z"]
        tone = g.remap(g.noise(pos, 1.8, detail=2), 0.42, 0.58)
        base = g.mixc(tone, rig.srgb("#66625C"), rig.srgb("#86807A"))
        if gain != 1.0:
            base = g.mulc(base, (gain, gain, gain * 0.98, 1.0))
        if not bloom:
            return base
        vertical = g.remap(nz, 0.5, 0.1)
        st = g.node("ShaderNodeMapping", Vector=pos)
        st.inputs["Scale"].default_value = (1.0, 1.0, 0.3)
        runs = g.image(f"{TEX}/maps/rust_streak.png", st.outputs[0], 0.8).outputs["Color"]
        patches = g.remap(g.noise(pos, 5, detail=3), 0.62, 0.74)
        hang = None
        for top, length in tops:
            below = g.math("MULTIPLY", g.remap(z, top - length, top), g.remap(z, top + 0.015, top))
            hang = below if hang is None else g.math("MAXIMUM", hang, below)
        streak = g.math("MULTIPLY", g.math("MULTIPLY", hang, g.remap(runs, 0.35, 0.7)), vertical)
        ao = g.node("ShaderNodeAmbientOcclusion", Distance=0.1).outputs["AO"]
        cav = g.math("MULTIPLY", g.math("SUBTRACT", 1.0, ao), g.remap(g.noise(pos, 22, detail=4), 0.4, 0.6))
        m = g.math("ADD", g.math("MULTIPLY", streak, 1.3), g.math("MULTIPLY", cav, 1.2))
        m = g.math("ADD", m, g.math("MULTIPLY", patches, 0.4))
        m = g.math("MULTIPLY", m, 0.8 * bloom, clamp=True)
        crust = g.mixc(g.noise(pos, 37, detail=3), rig.srgb("#B4A486"), rig.srgb("#D8CAA6"))
        return g.mixc(m, base, crust)
    return pat


GRAIN = (0.94, 1.04)   # the photo grain's range, from layered()'s 0.7-1.22: vanilla's speckle is low
BUMP = 0.08            # the photo relief's strength, from layered()'s 0.3


def soften_grain(mat, lo=0.86, hi=1.1):
    """FFF #146 in numbers (finish.py's ratio, the study's soft): narrow the shared
    layered()'s photo grain on this concept's own materials (materials.py untouched)."""
    for nd in mat.node_tree.nodes:
        if nd.type == "MAP_RANGE" and abs(nd.inputs["To Min"].default_value - 0.7) < 1e-6 \
                and abs(nd.inputs["To Max"].default_value - 1.22) < 1e-6:
            nd.inputs["To Min"].default_value = lo
            nd.inputs["To Max"].default_value = hi
        if nd.type == "BUMP" and BUMP is not None:
            nd.inputs["Strength"].default_value = BUMP


def worn_paint(mat, paint, chips=0.5, under="#4A4642", rust=0.5, wiped=0.4, warm=0.6, sheen=None, mottle=0.12,
               film=0.3):
    """Round 5's finish over a layered() part, in place of round 4's vanilla_idiom(), which
    laid one broad rust-and-ochre mottle over everything until every part was the same
    brown. Vanilla's paint stays the paint's colour across a surface, and the wear is local:

      - chips: small flakes knocked off to the metal underneath (`under`), thickest at
        edges and corners, sparse on the flats, each with a thin rust rim;
      - rust where it forms, not all over: in the seams and contact lines (AO), at the
        foot (layered()'s ground), down from the bands and fittings (layered()'s drips);
        `mottle` keeps only a faint trace of round 4's broad mottle;
      - wiped patches: a few hand-sized areas where the dust and grime are rubbed off,
        the paint cleaner and a little glossier (round handles, panels, a ladder);
      - warm-brown dirt in the contact lines, and a warm cast, kept from round 4;
      - sheen: a lower roughness on round bare parts, so a cream band runs along them."""
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
    # a trace of broad weathering, much fainter than round 4's
    if mottle:
        big = g.noise(pos, 3.2, detail=5, rough=0.6, distortion=0.4)
        rm = g.math("MULTIPLY", g.remap(big, 0.6, 0.7), mottle, clamp=True)
        col = g.mixc(rm, col, rig.srgb("#5A3418"))
    # a dirt film: paint in service is never clean -- warm-brown, broken, a few px to a tile
    if film:
        fm = g.math("MULTIPLY", g.remap(g.noise(pos, 4.5, detail=6, rough=0.62, distortion=0.3), 0.38, 0.7), film,
                    clamp=True)
        col = g.mixc(fm, col, g.mulc(col, rig.srgb("#8A7258")))
    # wiped: low-frequency, high threshold -- a few clean patches
    wipe = None
    if wiped:
        wipe = g.math("MULTIPLY", g.remap(g.noise(pos, 2.4, detail=2, rough=0.4), 0.6, 0.68), wiped, clamp=True)
        clean = g.mulc(rig.srgb(paint), (1.06, 1.05, 1.02, 1.0))
        col = g.mixc(wipe, col, g.mixc(0.3, clean, col))
    # chips: flakes a few px across, densest along edges and corners, each to the metal or
    # to rust beneath, with a thin rust rim
    if chips:
        bevel = g.node("ShaderNodeBevel", Radius=0.06).outputs[0]
        dot = g.node("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        g.l.new(bevel, dot.inputs[0])
        g.l.new(normal, dot.inputs[1])
        edge = g.remap(dot.outputs["Value"], 0.998, 0.93)            # 1 near an edge
        flake = g.noise(pos, 15, detail=4, rough=0.72, distortion=0.8)
        thr = g.math("SUBTRACT", 0.63, g.math("MULTIPLY", edge, 0.14))  # easier to chip at edges
        bare = g.math("MULTIPLY", g.math("GREATER_THAN", flake, thr), chips, clamp=True)
        rim = g.math("MULTIPLY", g.math("GREATER_THAN", flake, g.math("SUBTRACT", thr, 0.03)), chips, clamp=True)
        col = g.mixc(rim, col, rig.srgb("#4E2A14"))                 # the rust rim round a chip
        metal = g.mixc(g.noise(pos, 60, detail=2), rig.srgb(under), g.mulc(rig.srgb(under), (1.35, 1.32, 1.28, 1)))
        rusty = g.mixc(g.noise(pos, 31, detail=3), rig.srgb("#4A230E"), rig.srgb("#7E4420"))
        metal = g.mixc(g.remap(g.noise(pos, 5.5, detail=2), 0.45, 0.55), metal, rusty)
        col = g.mixc(bare, col, metal)
        if met_link is not None:
            nt.links.new(g.mixf(bare, met_link.from_socket, 0.6), bsdf.inputs["Metallic"])
        if rough is not None:
            rough = g.mixf(bare, rough, 0.4)
    # dirt streaks: dark-brown runs down the vertical faces (washed dirt, not rust)
    if film:
        nz0 = g.node("ShaderNodeSeparateXYZ", Vector=normal).outputs["Z"]
        st = g.node("ShaderNodeMapping", Vector=pos)
        st.inputs["Scale"].default_value = (1.0, 1.0, 0.15)
        runs = g.remap(g.image(f"{TEX}/maps/rust_streak.png", st.outputs[0], 1.6).outputs["Color"], 0.5, 0.85)
        streak = g.math("MULTIPLY", g.math("MULTIPLY", runs, g.remap(nz0, 0.6, 0.2)), 0.55 * film * 2, clamp=True)
        col = g.mixc(streak, col, g.mulc(col, rig.srgb("#7A6450")))
    # undersides: baked-in shade and grime on the faces turned to the ground, as vanilla's
    # vessels darken into their lower halves
    if film:
        nz = g.node("ShaderNodeSeparateXYZ", Vector=normal).outputs["Z"]
        down = g.math("MULTIPLY", g.remap(nz, 0.1, -0.7), 0.55 * min(1.0, film * 2), clamp=True)
        col = g.mixc(down, col, g.mulc(col, rig.srgb("#6A5440")))
        # rust patches at the foot, where water stands
        zz = g.node("ShaderNodeSeparateXYZ", Vector=pos).outputs["Z"]
        foot = g.math("MULTIPLY", g.remap(zz, 0.32, 0.04), g.remap(g.noise(pos, 8, detail=4, rough=0.6), 0.45, 0.62),
                      clamp=True)
        col = g.mixc(g.math("MULTIPLY", foot, rust, clamp=True), col,
                     g.mixc(g.noise(pos, 19, detail=3), rig.srgb("#40200C"), rig.srgb("#7A4220")))
    # rust in the seams and contact lines only
    if rust:
        rc = g.mixc(g.noise(pos, 9, detail=4), rig.srgb("#3A1C0A"), rig.srgb("#7A4220"))
        seam = g.math("MULTIPLY", g.math("MULTIPLY", cav, 2.2),
                      g.remap(g.noise(pos, 14, detail=4), 0.35, 0.6), clamp=True)
        col = g.mixc(g.math("MULTIPLY", seam, rust, clamp=True), col, rc)
    # warm cast
    col = g.mulc(col, (1.0 + 0.02 * warm, 1.0, 1.0 - 0.06 * warm, 1.0))
    # dirt mottle at a few px, gentler than round 4's, and a fine grime breakup at 1-2 px
    dm = g.noise(pos, 7.5, detail=5, rough=0.6)
    col = g.mulc(col, g.gray(g.remap(dm, 0.3, 0.7, 0.8, 1.04)))
    fg = g.noise(pos, 22, detail=4, rough=0.7)
    col = g.mulc(col, g.gray(g.remap(fg, 0.3, 0.7, 0.84, 1.06)))
    # warm-brown dirt in the contact lines
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


WET = ("#3A1E0C", "#7A4018")        # rust runs below fittings
# Paint heights the rust runs hang from: bands, flanges, nozzle rings (world z)
RUNS = ((0.62, 0.3), (0.95, 0.3), (1.35, 0.3), (1.65, 0.35))
# (name, paint, under-metal, colour-map group). The per-part palette: what each piece of
# equipment is painted or made of (see PALETTE on the sheet).
M = {
    # the signature: the vessels' lead cladding (reactor, settling pot, drop box, leg caps, press leaves)
    "lead": layered("lead", "#6A6258", metal="#BCB4A2", paint_metal=0.3, paint_rough=0.55, wear=0.3,
                    rust=0.06, dust=0.5, grime=0.8, jitter=0.08, ground=0.75, pattern=lead_finish(),
                    drips=tuple((t - 0.03, l * 0.8) for t, l in BLOOM_TOPS), drip=0.6, rust_tint=WET),
    "lead_new": layered("lead_new", "#7A7266", metal="#B4AC9C", paint_metal=0.35, paint_rough=0.55, wear=0.2,
                        rust=0.0, dust=0.3, grime=0.6, jitter=0.03, ground=0.5,
                        pattern=lead_finish(bloom=0.0, gain=1.12)),
    # oxide red: the scrubber (the foundry's red vessel)
    "oxide": layered("oxide", "#6E2C1E", metal="#5A4E46", paint_metal=0.1, paint_rough=0.7, wear=0.25,
                     rust=0.18, dust=0.35, grime=0.6, jitter=0.06, ground=0.8, drips=RUNS, drip=0.85,
                     rust_tint=WET),
    # ochre: the feed drum, the ladder (the chemical plant's yellow)
    "ochre": layered("ochre", "#9C7426", metal="#5E544A", paint_metal=0.08, paint_rough=0.55, wear=0.25,
                     rust=0.15, dust=0.35, grime=0.6, jitter=0.05, ground=0.8, drips=RUNS, drip=0.85,
                     rust_tint=WET),
    # weathered green: the receiver and every motor (the refinery's green tanks)
    "green": layered("green", "#4E6034", metal="#5A544C", paint_metal=0.08, paint_rough=0.62, wear=0.25,
                     rust=0.18, dust=0.4, grime=0.65, jitter=0.07, ground=0.75, drips=RUNS, drip=0.85,
                     rust_tint=WET),
    # cream / off-white: the pump house, the make-up pot, the press's filter leaves (the storage tank,
    # the foundry's units)
    "cream": layered("cream", "#ACA084", metal="#5E564C", paint_metal=0.06, paint_rough=0.6, wear=0.25,
                     rust=0.15, dust=0.3, grime=0.7, jitter=0.05, ground=0.85, drips=RUNS, drip=0.85,
                     rust_tint=WET),
    # grey-painted steel: the exchanger, the instrument house
    "grey": layered("grey", "#6E6A62", metal="#9A9488", paint_metal=0.15, paint_rough=0.55, wear=0.3,
                    rust=0.2, dust=0.35, grime=0.7, jitter=0.06, ground=0.8, drips=RUNS, drip=0.85,
                    rust_tint=WET),
    # dark steel: skids, saddles, foot rings, the press frame, headers, valve bodies
    "dark_steel": layered("dark_steel", "#3E3934", metal="#8C8272", paint_metal=0.35, paint_rough=0.55,
                          wear=0.4, rust=0.35, dust=0.35, grime=0.7, ground=0.8, rust_tint=WET),
    # bare bright steel: pipes, flanges, straps, nozzles, rails -- vanilla's pale pipe metal
    "bare": layered("bare", "#A8A090", metal="#D8D0BE", paint_metal=0.85, paint_rough=0.3, wear=0.5,
                    rust=0.16, dust=0.12, grime=0.5, ground=0.6),
    "seam": layered("seam", "#8A8070", metal="#B0A690", paint_metal=0.7, paint_rough=0.4, wear=0.3,
                    rust=0.25, dust=0.0, jitter=0.04, ground=0.7),
    # bolt heads and rivets: where the rust lives
    "bolt": layered("bolt", "#5A4A3A", metal="#A89880", paint_metal=0.5, paint_rough=0.5, wear=0.5,
                    rust=0.75, dust=0.2, grime=0.6, rust_tint=WET),
    # copper: the vent condenser and its coil (verdigris in the cavities)
    "copper": layered("copper", "#94592C", metal="#D09060", paint_metal=0.9, paint_rough=0.32, wear=0.45,
                      rust=0.04, dust=0.2, grime=0.5, patina=0.9),
    "brass": layered("brass", "#9A7438", metal="#D0AC66", paint_metal=0.9, paint_rough=0.35, wear=0.5,
                     rust=0.1, dust=0.2),
    # hoses: tan and black rubber
    "hose": layered("hose", "#5E4636", metal="#9A7E66", paint_metal=0.0, paint_rough=0.62, wear=0.35,
                    rust=0.0, dust=0.5, grime=0.6, jitter=0.06),
    "hose_k": layered("hose_k", "#38302A", metal="#7A6E62", paint_metal=0.0, paint_rough=0.6, wear=0.35,
                      rust=0.0, dust=0.55, grime=0.5, jitter=0.06),
    # lagging: cream-tan canvas, steel straps
    "lag": layered("lag", "#9A8A68", metal="#B0A080", paint_metal=0.0, paint_rough=0.9, wear=0.25,
                   rust=0.15, dust=0.5, grime=0.7, jitter=0.1, ground=0.6),
    # accents: handwheels, pipe-marking rings, ID panels, cable labels, hazard tape
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
    "slab": layered("slab", "#4A4038", metal="#A49480", paint_metal=0.25, paint_rough=0.55, wear=0.45,
                    rust=0.3, dust=0.2, grime=0.6, jitter=0.0),
    "dark": layered("dark", "#1E1814", paint_metal=0.0, paint_rough=0.8, wear=0.0, rust=0.0, dust=0.0, grime=0.0),
}
# cables: muted, warm; never blue -- blue is the solution's alone
for _n, _c, _e in (("red", "#9E4430", "#C88068"), ("yellow", "#B89440", "#DCC488"),
                   ("green", "#5A6E42", "#98A880"), ("black", "#34302C", "#746C64"),
                   ("grey", "#4A443E", "#7C746A")):
    M["cable_" + _n] = layered("cable_" + _n, _c, metal=_e, paint_metal=0.0, paint_rough=0.5, wear=0.3,
                               rust=0.0, dust=0.3, grime=0.4, jitter=0.05)
M["cable_blue"] = M["cable_grey"]

FINISH = {   # (paint hex, chips, under-metal, seam rust, wiped, warm, sheen, mottle, film)
    "lead": ("#7A746C", 0.0, "#8A8478", 0.55, 0.2, 0.6, 0.5, 0.4, 0.4),
    "lead_new": ("#7A7266", 0.0, "#8A8478", 0.2, 0.2, 0.6, 0.38, 0.1, 0.15),
    "oxide": ("#6E2C1E", 0.75, "#4A403A", 0.7, 0.25, 0.3, None, 0.2, 0.4),
    "ochre": ("#9C7426", 0.55, "#4E463E", 0.65, 0.25, 0.3, None, 0.2, 0.45),
    "green": ("#4E6034", 0.7, "#4A443E", 0.65, 0.25, 0.3, None, 0.2, 0.4),
    "cream": ("#ACA084", 0.65, "#4E463E", 0.65, 0.3, 0.3, None, 0.18, 0.45),
    "grey": ("#6E6A62", 0.6, "#8A8478", 0.65, 0.25, 0.5, None, 0.2, 0.4),
    "dark_steel": ("#3E3934", 0.3, "#8C8272", 0.7, 0.15, 0.6, 0.45, 0.25, 0.2),
    "bare": ("#A8A090", 0.0, "#D8D0BE", 0.45, 0.2, 0.5, 0.2, 0.1, 0.25),
    "seam": ("#8A8070", 0.0, "#B0A690", 0.4, 0.0, 0.6, None, 0.0, 0.0),
    "bolt": ("#5A4A3A", 0.0, "#A89880", 0.8, 0.0, 0.8, None, 0.3, 0.0),
    "copper": ("#94592C", 0.0, "#D09060", 0.15, 0.25, 0.3, 0.26, 0.05, 0.35),
    "brass": ("#9A7438", 0.0, "#D0AC66", 0.2, 0.3, 0.3, 0.28, 0.0, 0.2),
    "hose": ("#5E4636", 0.0, "#5E4636", 0.0, 0.2, 0.5, None, 0.0, 0.2),
    "hose_k": ("#38302A", 0.0, "#38302A", 0.0, 0.2, 0.6, None, 0.0, 0.0),
    "lag": ("#9A8A68", 0.0, "#9A8A68", 0.45, 0.2, 0.6, None, 0.2, 0.45),
    "red": ("#A8301E", 0.5, "#6A5A50", 0.3, 0.0, 0.0, None, 0.0, 0.2),
    "yellow": ("#D0A428", 0.5, "#6A5A50", 0.3, 0.0, 0.0, None, 0.0, 0.2),
    "hazard": ("#B8962E", 0.4, "#5A4E46", 0.4, 0.0, 0.4, None, 0.1, 0.3),
    "stencil": ("#CEC2A4", 0.4, "#5A5044", 0.4, 0.0, 0.4, None, 0.0, 0.3),
    "slab": ("#4A4038", 0.3, "#A49480", 0.5, 0.0, 0.8, None, 0.2, 0.2),
}
for _k, _m in M.items():
    if GRAIN:
        soften_grain(_m, *GRAIN)
    if _k in FINISH:
        p, ch, und, ru, wi, wa, sh, mo, fi = FINISH[_k]
        worn_paint(_m, p, chips=ch, under=und, rust=ru, wiped=wi, warm=wa, sheen=sh, mottle=mo, film=fi)

# the animation set's own materials (options/animation/anim_previews.py), made after the
# shared finish as they were there: the cake toned down from white (Liam), a damp grey-buff
# a step under the cream leaves; the condensate; the wet patch under the drain cock
M["cake"] = layered("cake", "#8C8476", paint_metal=0.0, paint_rough=0.85, wear=0.0, rust=0.0, dust=0.3, grime=0.35)
M["water"] = bpy.data.materials.new("water")
M["water"].use_nodes = True
_wb = M["water"].node_tree.nodes["Principled BSDF"]
_wb.inputs["Base Color"].default_value = rig.srgb("#BFD0D4")
_wb.inputs["Roughness"].default_value = 0.05
_wb.inputs["Coat Weight"].default_value = 1.0
_wb.inputs["Specular IOR Level"].default_value = 1.0
M["wet"] = bpy.data.materials.new("wet")
M["wet"].use_nodes = True
_tb = M["wet"].node_tree.nodes["Principled BSDF"]
_tb.inputs["Base Color"].default_value = rig.srgb("#2A2622")
_tb.inputs["Roughness"].default_value = 0.12
_tb.inputs["Alpha"].default_value = 0.4


# ---------------------------------------------------------------- round 2's helpers (r2_blockout.py), the hose's ribs coarsened
# glass: thick, slightly smoky borosilicate
glass = bpy.data.materials.new("glass")
glass.use_nodes = True
gb = glass.node_tree.nodes["Principled BSDF"]
gb.inputs["Base Color"].default_value = rig.srgb("#C8D8E0")
gb.inputs["Roughness"].default_value = 0.06
gb.inputs["IOR"].default_value = 1.47
gb.inputs["Transmission Weight"].default_value = 0.92
gb.inputs["Coat Weight"].default_value = 0.4
M["glass"] = glass
# a flat window seen at 30 deg: thin, low-reflection, or it mirrors the sky grey
pane = bpy.data.materials.new("pane")
pane.use_nodes = True
pb = pane.node_tree.nodes["Principled BSDF"]
pb.inputs["Base Color"].default_value = rig.srgb("#D8E4EA")
pb.inputs["Roughness"].default_value = 0.04
pb.inputs["IOR"].default_value = 1.08
pb.inputs["Transmission Weight"].default_value = 1.0
pb.inputs["Specular IOR Level"].default_value = 0.25
M["pane"] = pane

PHASES = []       # (value node, cycles per loop): set per frame
GLOWS = []        # emission strength nodes, 0 when idle
FLUIDS = []       # (node tree, the ramp's colour output, the BSDF): the glow pass flattens them
GLOW = 2.4


def fluid(name, mode, scale=6.0, k=1, arms=3, bright=1.0):
    """The radiant solution: an emissive blue whose pattern moves with a phase.

    mode "flow": bands along the object's local Z, distorted by noise, travelling
    k band-widths a loop. mode "swirl": a spiral of `arms` arms about local Z,
    turning k/arms of a revolution a loop. Dark troughs, bright crests, inside
    #1F63FF -> #73ADFF; with the light off, a dark navy liquid with a sheen.
    """
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    phase = N.new("ShaderNodeValue")
    PHASES.append((phase, k))
    noise = N.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale * 0.7
    noise.inputs["Detail"].default_value = 3.0
    L.new(tc.outputs["Object"], noise.inputs["Vector"])
    if mode == "flow":
        wave = N.new("ShaderNodeTexWave")
        wave.bands_direction = "Z"
        wave.inputs["Scale"].default_value = scale
        wave.inputs["Distortion"].default_value = 11.0
        wave.inputs["Detail"].default_value = 4.0
        wave.inputs["Detail Scale"].default_value = 1.5
        L.new(tc.outputs["Object"], wave.inputs["Vector"])
        neg = N.new("ShaderNodeMath")
        neg.operation = "MULTIPLY"
        neg.inputs[1].default_value = -1.0
        L.new(phase.outputs[0], neg.inputs[0])
        L.new(neg.outputs[0], wave.inputs["Phase Offset"])
        pat = wave.outputs["Fac"]
    else:
        sep = N.new("ShaderNodeSeparateXYZ")
        L.new(tc.outputs["Object"], sep.inputs[0])
        ang = N.new("ShaderNodeMath")
        ang.operation = "ARCTAN2"
        L.new(sep.outputs[1], ang.inputs[0])
        L.new(sep.outputs[0], ang.inputs[1])
        rad = N.new("ShaderNodeVectorMath")
        rad.operation = "LENGTH"
        L.new(tc.outputs["Object"], rad.inputs[0])
        a1 = N.new("ShaderNodeMath")
        a1.operation = "MULTIPLY"
        a1.inputs[1].default_value = float(arms)
        L.new(ang.outputs[0], a1.inputs[0])
        r1 = N.new("ShaderNodeMath")
        r1.operation = "MULTIPLY"
        r1.inputs[1].default_value = scale * 2.2
        L.new(rad.outputs["Value"], r1.inputs[0])
        nz = N.new("ShaderNodeMath")
        nz.operation = "MULTIPLY"
        nz.inputs[1].default_value = 2.5
        L.new(noise.outputs["Fac"], nz.inputs[0])
        s1 = N.new("ShaderNodeMath")
        s1.operation = "ADD"
        L.new(a1.outputs[0], s1.inputs[0])
        L.new(r1.outputs[0], s1.inputs[1])
        s2 = N.new("ShaderNodeMath")
        s2.operation = "ADD"
        L.new(s1.outputs[0], s2.inputs[0])
        L.new(nz.outputs[0], s2.inputs[1])
        s3 = N.new("ShaderNodeMath")
        s3.operation = "SUBTRACT"
        L.new(s2.outputs[0], s3.inputs[0])
        L.new(phase.outputs[0], s3.inputs[1])
        sn = N.new("ShaderNodeMath")
        sn.operation = "SINE"
        L.new(s3.outputs[0], sn.inputs[0])
        mr = N.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = -1.0
        L.new(sn.outputs[0], mr.inputs["Value"])
        pat = mr.outputs["Result"]
    mix = N.new("ShaderNodeMix")
    mix.data_type = "FLOAT"
    mix.inputs["Factor"].default_value = 0.45 if mode == "flow" else 0.22
    L.new(pat, mix.inputs["A"])
    L.new(noise.outputs["Fac"], mix.inputs["B"])
    ramp = N.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.25, rig.srgb("#0B2A8C")
    cr.elements[1].position, cr.elements[1].color = 0.8, rig.srgb("#73ADFF")
    e = cr.elements.new(0.52)
    e.color = rig.srgb("#1F63FF")
    L.new(mix.outputs["Result"], ramp.inputs["Fac"])
    dark = N.new("ShaderNodeMix")
    dark.data_type = "RGBA"
    dark.inputs["Factor"].default_value = 0.82
    L.new(ramp.outputs["Color"], dark.inputs["A"])
    dark.inputs["B"].default_value = rig.srgb("#0A1022")
    L.new(dark.outputs["Result"], b.inputs["Base Color"])
    L.new(ramp.outputs["Color"], b.inputs["Emission Color"])
    FLUIDS.append((nt, ramp.outputs["Color"], b))
    b.inputs["Roughness"].default_value = 0.15
    b.inputs["Emission Strength"].default_value = GLOW * bright
    GLOWS.append((b.inputs["Emission Strength"], GLOW * bright))
    M[name] = m
    return name


def emissive(name, hexcol, bright=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#141C30")
    b.inputs["Emission Color"].default_value = rig.srgb(hexcol)
    b.inputs["Emission Strength"].default_value = GLOW * bright
    GLOWS.append((b.inputs["Emission Strength"], GLOW * bright))
    M[name] = m
    return name


emissive("bubble", "#A8CCFF", 1.3)
# the status lamps' lens (spec 7): an unlit pale glass in the plate; in the light pass lit
# white, for the engine to tint (apply_tint "status"). Never blue: blue is the legs' alone.
lamp = bpy.data.materials.new("lamp")
lamp.use_nodes = True
lb = lamp.node_tree.nodes["Principled BSDF"]
lb.inputs["Base Color"].default_value = rig.srgb("#C8C4BA")
lb.inputs["Roughness"].default_value = 0.25
lb.inputs["Coat Weight"].default_value = 0.6
lb.inputs["Emission Color"].default_value = (1, 1, 1, 1)
lb.inputs["Emission Strength"].default_value = 0.0
M["lamp"] = lamp


def lamp_cut(on):
    """The lens as the light pass wants it: lit white; else the plate's unlit glass."""
    lb.inputs["Emission Strength"].default_value = 1.0 if on else 0.0
    lb.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1) if on else rig.srgb("#C8C4BA")
M["fleck"] = layered("fleck", "#1A1E28", paint_metal=0.2, paint_rough=0.5, wear=0, rust=0, dust=0, grime=0)

# ---------------------------------------------------------------- geometry
OBJS = []
LEG_POSES = []     # callables(t in [0,1)) that pose the legs' bubbles and flecks
CPL_POSES = []     # and the couplings
STUBS = []


ASM = {}           # object name -> the assembly it was built in (a kit call, or itself)
_ASM = [None]
_NEXT = [0]
RUN_ENDS = {}      # a hose's, lagged pipe's, pipe's or bundle's assembly -> its two end points (model space)
HEADS = set()      # the dished heads, which fittings stand in


class asm:
    """with asm(): every part built inside is one assembly (unless already inside one)."""

    def __enter__(self):
        self.outer = _ASM[0] is not None
        if not self.outer:
            _NEXT[0] += 1
            _ASM[0] = _NEXT[0]

    def __exit__(self, *a):
        if not self.outer:
            _ASM[0] = None


def kit(fn):
    """A kit function builds one assembly: a vessel with its bands, a hose with its ferrules."""
    def wrapped(*a, **k):
        with asm():
            return fn(*a, **k)
    wrapped.__name__ = fn.__name__
    return wrapped


def _finish(o, mat, bevel=0.012, smooth=False, parent=None):
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
    if _ICON[0]:
        ICON_SET.add(o.name)
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
    """A thick ring: a frame, a collar, a hoop with its middle open."""
    me = bpy.data.meshes.new("annulus")
    bm = bmesh.new()
    rows = []
    for r, z in ((r_out, -h / 2), (r_out, h / 2), (r_in, h / 2), (r_in, -h / 2)):
        rows.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z))
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


def head(x, y, z, r, h, mat, up=True):
    """A dished head: the top of a sphere, squashed to height h."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0), segments=48, ring_count=24)
    o = bpy.context.active_object
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if (v.co.z < -0.01 if up else v.co.z > 0.01)], context="VERTS")
    bm.to_mesh(me)
    bm.free()
    o.scale = (r, r, h)
    o.location = (x, y, z)
    # scale only: the head keeps its own origin, so a drum can turn it about its end
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    HEADS.add(o.name)
    return _finish(o, mat, 0, smooth=True)


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
        rr = r * (1 + corr * (0.5 + 0.5 * math.cos(2 * math.pi * s[i] / pitch)))
        rings.append([bm.verts.new(p + rr * (math.cos(2 * math.pi * k / seg) * N[i]
                                             + math.sin(2 * math.pi * k / seg) * B[i])) for k in range(seg)])
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


def hose(pts, r=0.085, mat="hose"):
    """A fat corrugated hose with crimped ferrules and big nuts at both ends."""
    P = catmull(pts)
    RUN_ENDS[_ASM[0]] = (P[0], P[-1])
    sweep(P, r, mat, corr=0.055, pitch=0.095, seg=18)  # round 4: ribs shallower, less small detail
    for p, q in ((P[0], P[1]), (P[-1], P[-2])):
        t = (p - q).normalized()
        cyl(tuple(p - t * 0.05), r * 1.3, 0.11, "bare", rot=along(t), verts=20, bevel=0.006)
        torus(tuple(p - t * 0.09), r * 1.3, 0.010, "bare", rot=along(t), seg=20)
        cyl(tuple(p + t * 0.005), r * 1.6, 0.04, "brass", rot=along(t), verts=6, bevel=0.0)
    return P


def mark(P, frac, mat, r, w=0.035):
    """A pipe-marking ring (round 5): a painted band round a line at frac of its length,
    the colour saying what it carries -- never blue."""
    i = max(1, min(len(P) - 2, int(frac * (len(P) - 1))))
    t = (P[i + 1] - P[i - 1]).normalized()
    cyl(tuple(P[i]), r + 0.008, w, mat, rot=along(t), verts=24, bevel=0.003)


def lagged(pts, r=0.11, bands=0.22, marks=()):
    """A lagged pipe: canvas-wrapped insulation with steel straps, flanged ends."""
    P = catmull(pts)
    RUN_ENDS[_ASM[0]] = (P[0], P[-1])
    for f, m in marks:
        mark(P, f, m, r, 0.05)
    _, P, T, s = sweep(P, r, "lag", seg=20)
    nxt = bands / 2
    for i, p in enumerate(P):
        if s[i] >= nxt and s[i] < s[-1] - 0.05:
            torus(tuple(p), r + 0.004, 0.009, "bare", rot=along(T[i]), seg=24)
            nxt += bands
    for p, t in ((P[0], T[0]), (P[-1], T[-1])):
        cyl(tuple(p), r * 1.25, 0.04, "bare", rot=along(t), verts=24, bevel=0.005)
    return P


def pipe(pts, r=0.06, mat="bare", marks=()):
    P = catmull(pts)
    RUN_ENDS[_ASM[0]] = (P[0], P[-1])
    sweep(P, r, mat, seg=16)
    for f, m in marks:
        mark(P, f, m, r)
    return P


def bundle(pts, cols=("red", "blue", "yellow", "black"), r=0.014):
    P = catmull(pts)
    RUN_ENDS[_ASM[0]] = (P[0], P[-1])
    T, N, B = frames(P)
    s = [0.0]
    for a_, b_ in zip(P, P[1:]):
        s.append(s[-1] + (b_ - a_).length)
    n = len(cols)
    for k, c in enumerate(cols):
        off = [r * 1.3 * (math.cos(2 * math.pi * k / n + 9 * s[i]) * N[i]
                          + math.sin(2 * math.pi * k / n + 9 * s[i]) * B[i]) for i in range(len(P))]
        sweep([p + o for p, o in zip(P, off)], r, "cable_" + c, seg=8)
    # round 5: cable labels, cream sleeves round the bundle every ~0.4 tile
    nxt = 0.2
    for i, p in enumerate(P):
        if s[i] >= nxt and s[i] < s[-1] - 0.1:
            cyl(tuple(p), r * 2.9, 0.045, "label", rot=along(T[i]), verts=12, bevel=0.002)
            nxt += 0.4


def bolts(cx, cy, z, R, n, r=0.022, mat="bolt"):
    for i in range(n):
        a = 2 * math.pi * i / n
        cyl((cx + R * math.cos(a), cy + R * math.sin(a), z), r, 0.025, mat, verts=6, bevel=0)


def band(x, y, z, r, h=0.07, mat="lead", lugs=2, lug_a=-math.pi / 2):
    cyl((x, y, z), r + 0.025, h, mat, verts=64)
    for i in range(lugs):
        a = lug_a + 2 * math.pi * i / lugs
        box((x + (r + 0.05) * math.cos(a), y + (r + 0.05) * math.sin(a), z), (0.06, 0.06, h + 0.05),
            "dark_steel", rz=a, bevel=0.006)


def flange_ring(x, y, z, r, mat="dark_steel", h=0.06, nb=16):
    cyl((x, y, z), r + 0.045, h, mat, verts=64)
    bolts(x, y, z + h / 2 + 0.008, r + 0.03, nb, r=0.016)


NEEDLES = []       # (needle, its pose at rest, its dial's centre, the dial's axis, index): its gauge-* layer
N_GAUGE = [0]      # every gauge built, in order: a needle's index sets its twitch's phase (as the previews)


def _nd(t, u):
    """A needle's direction: in its dial's plane, 0.6 rad up from the horizontal u."""
    v = Vector(u).cross(Vector(t)).normalized()
    return (Vector(u) * math.cos(0.6) + v * math.sin(0.6)).normalized()


def _nrot(t, u):
    d = _nd(t, u)
    tt = Vector(t).normalized()
    tt = (tt - d * tt.dot(d)).normalized()
    return tuple(Matrix((d, tt, d.cross(tt))).transposed().to_euler())


def gauge(loc, facing, r=0.07, double=None):
    """A brass-cased gauge: a cream face, a red needle lying on it. double: one of the three
    double-size dials on a stem (the reactor's two, the scrubber's), whose needle twitches;
    its value is the needle's layer, one of GAUGES (spec 6.2)."""
    t = Vector(facing).normalized()
    if double:
        r *= 2.0
        cyl(tuple(Vector(loc) - t * 0.01), 0.035, 0.05, "bare", rot=along(t), verts=12, bevel=0)   # the stem
        loc = tuple(Vector(loc) + t * 0.02)
    cyl(loc, r, 0.03, "brass", rot=along(t), verts=24, bevel=0.004)
    cyl(tuple(Vector(loc) + t * 0.017), r * 0.8, 0.006, "gauge", rot=along(t), verts=24, bevel=0)
    u = t.cross(Vector((0, 0, 1)))
    u = u.normalized() if u.length > 1e-6 else Vector((1, 0, 0))
    assert double is None or double in GAUGES, double
    with grp(double or CUR[-1]):
        o = box(tuple(Vector(loc) + t * 0.022 + _nd(t, u) * r * 0.2), (r * 0.9, 0.006, 0.012 * (2 if double else 1)),
                "needle", rot=_nrot(t, u), bevel=0)
    if double:
        NEEDLES.append((o, o.matrix_basis.copy(), Vector(loc), t.copy(), N_GAUGE[0]))
    N_GAUGE[0] += 1


def handwheel(loc, r=0.09, axis=(0, 0, 1), mat="red"):
    """A valve handwheel: red or yellow paint, worn to metal (vanilla's chemical plant)."""
    t = Vector(axis).normalized()
    torus(loc, r, 0.016, mat, rot=along(t), seg=24)
    for k in range(3):                       # spokes
        a = 2 * PI * k / 3
        o = Vector((math.cos(a), math.sin(a), 0))
        q = t.to_track_quat("Z", "Y")
        o = q @ o
        cyl(tuple(Vector(loc) + o * r / 2), 0.008, r, mat, rot=along(o), verts=6, bevel=0)
    cyl(loc, 0.022, 0.05, "bare", rot=along(t), verts=12)


def coupling(x, y, z, r, axis=(0, 0, 1), mat="brass", axial=1.0, layer=None):
    """A free-turning six-lobed spider coupling: its own object, posed per frame, in its own
    layer (one of COUPLINGS). axial: made thinner along its shaft, to turn in the gap between its
    two machines (the clip fixes)."""
    root = bpy.data.objects.new("coupling", None)
    sc.collection.objects.link(root)
    root.parent = ROOT
    root.location = (x, y, z)
    root.rotation_euler = along(axis)
    root.scale = (1.0, 1.0, axial)
    assert layer in COUPLINGS, layer
    with grp(layer):
        cyl((0, 0, 0), r * 0.55, 0.09, "dark_steel", verts=24, parent=root)
        for i in range(6):
            a = 2 * math.pi * i / 6
            box((r * 0.7 * math.cos(a), r * 0.7 * math.sin(a), 0), (r * 0.5, r * 0.32, 0.075), mat,
                rz=a, bevel=0.006, parent=root)
        box((0, 0, 0.047), (r * 0.25, r * 1.5, 0.012), "hazard", bevel=0, parent=root)   # a stripe to see it turn
    base = root.rotation_euler.copy()

    def pose(t):
        root.rotation_euler = base
        root.rotation_euler.rotate_axis("Z", 2 * math.pi / 6 * t)
    CPL_POSES.append(pose)
    return root


def bubbles(cx, cy, z0, z1, r, n, seed, front=True):
    """Bright bubbles rising in the gap between the fluid and the glass; each
    climbs exactly the column's height a loop, so the loop is seamless."""
    rnd = random.Random(seed)
    objs = []
    for i in range(n):
        a = (-math.pi / 2 + rnd.uniform(-1.1, 1.1)) if front else rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0.008, 0.02)
        o = sphere((0, 0, 0), rr, "bubble", seg=10)
        objs.append((o, a, rnd.random(), rr))
    H = z1 - z0

    def pose(t):
        for o, a, ph, rr in objs:
            u = (ph + t) % 1.0
            o.location = (cx + r * math.cos(a + 0.4 * math.sin(6.28 * (u + ph))),
                          cy + r * math.sin(a + 0.4 * math.sin(6.28 * (u + ph))), z0 + H * u)
    LEG_POSES.append(pose)



def status_lamp(x, y, z):
    cyl((x, y, z), 0.045, 0.05, "dark_steel", verts=16)
    with grp("lens"):
        sphere((x, y, z + 0.035), 0.032, "lamp", seg=12)

# ======================================================================= round-2 kit
PI = math.pi


def valve(x, y, z=0.0, h=0.42, r=0.07, wheel="red"):
    """A standing gate valve: body, bonnet, stem and handwheel."""
    cyl((x, y, z + 0.1), r * 1.3, 0.2, "dark_steel", verts=20)
    cyl((x, y, z + 0.1 + h * 0.4), r * 0.7, h * 0.5, "bare", verts=16)
    handwheel((x, y, z + h), 0.085, mat=wheel)


def drum_ns(x, y0, y1, z, r, mat="grey", bands=(), saddles=(), band_mat="dark_steel"):
    """A drum lying north-south on saddles, with dished ends."""
    cyl((x, (y0 + y1) / 2, z), r, y1 - y0, mat, rot=(PI / 2, 0, 0), verts=48)
    for yy, s in ((y0, -1), (y1, 1)):
        h = head(x, yy, z, r, 0.13, mat)
        h.rotation_euler = (-s * PI / 2, 0, 0)
    for yy in bands:
        cyl((x, yy, z), r + 0.025, 0.07, band_mat, rot=(PI / 2, 0, 0), verts=48)
    for yy in saddles:
        box((x, yy, (z - r * 0.5) / 2 + 0.02), (r * 1.6, 0.12, z - r * 0.5 + 0.04), "dark_steel")


def drum_ew(x0, x1, y, z, r, mat="grey", bands=(), saddles=(), band_mat="dark_steel"):
    """A drum lying east-west on saddles, with dished ends."""
    cyl(((x0 + x1) / 2, y, z), r, x1 - x0, mat, rot=(0, PI / 2, 0), verts=48)
    for xx, s in ((x0, -1), (x1, 1)):
        h = head(xx, y, z, r, 0.13, mat)
        h.rotation_euler = (0, s * PI / 2, 0)
    for xx in bands:
        cyl((xx, y, z), r + 0.025, 0.07, band_mat, rot=(0, PI / 2, 0), verts=48)
    for xx in saddles:
        box((xx, y, (z - r * 0.5) / 2 + 0.02), (0.12, r * 1.6, z - r * 0.5 + 0.04), "dark_steel")


def vtank(x, y, r, h, mat="grey", bands=(), top="lead", lug_a=-PI / 2, nozzle=(0.3, 0.0), band_mat="dark_steel"):
    """A standing vessel on a cast foot ring, banded, dished head, a nozzle."""
    cyl((x, y, 0.07), r + 0.08, 0.14, "dark_steel", verts=64)
    cyl((x, y, h / 2 + 0.07), r, h - 0.14, mat, verts=64)
    for z in bands:
        band(x, y, z, r, mat=band_mat, lug_a=lug_a)
    hh = min(0.24, r * 0.38)
    head(x, y, h, r, hh, top)
    if nozzle:
        nx, ny = x + nozzle[0] * r, y + nozzle[1] * r
        cyl((nx, ny, h + hh * 0.7 + 0.06), 0.085, 0.16, "bare", verts=24)
        flange_ring(nx, ny, h + hh * 0.7 + 0.14, 0.08, mat="bare", h=0.035, nb=8)
    return h + hh


def ladder(x, y, z0, z1, axis="y", mat="ochre"):
    for z in [z0 + 0.3 * i for i in range(int((z1 - z0) / 0.3) + 1)]:
        box((x, y, z), (0.04, 0.16, 0.025) if axis == "y" else (0.16, 0.04, 0.025), mat, bevel=0.004)
    for s in (-1, 1):
        o = (0, s * 0.08) if axis == "y" else (s * 0.08, 0)
        box((x + o[0], y + o[1], (z0 + z1) / 2), (0.025, 0.025, z1 - z0), mat, bevel=0.003)


def pump(x, y, d=(1, 0), s=1.0, z0=0.0, layer="coupling-pump"):
    """A pump skid along d, standing at z0: motor (olive), free coupling, volute. Returns the volute's outlet top."""
    dx, dy = d
    L, Wd = 1.05 * s, 0.55 * s
    box((x, y, z0 + 0.07), (L if dx else Wd, Wd if dx else L, 0.14), "dark_steel")
    mx, my = x - dx * 0.3 * s, y - dy * 0.3 * s
    zc = z0 + 0.14 + 0.2 * s
    box((mx, my, zc), (0.4 * s if dx else 0.38 * s, 0.38 * s if dx else 0.4 * s, 0.4 * s), "green")
    for i in range(5):
        o = 0.065 * s * (i - 2)
        box((mx + (0 if dx else o), my + (o if dx else 0), zc + 0.21 * s),
            (0.36 * s if dx else 0.025, 0.025 if dx else 0.36 * s, 0.025), "dark_steel", bevel=0)
    coupling(x, y, zc, 0.15 * s, axis=(dx, dy, 0), layer=layer)
    vx, vy = x + dx * 0.3 * s, y + dy * 0.3 * s
    cyl((vx, vy, zc + 0.02), 0.22 * s, 0.24 * s, "dark_steel", rot=along((dx, dy, 0)), verts=32)
    cyl((vx, vy, zc + 0.27 * s), 0.07 * s, 0.16 * s, "bare", verts=16)
    return (vx, vy, zc + 0.36 * s)


def cellbox(x, y, w, d, h, wheel=True):
    """A lead-lined cell box: the solid product's drop box."""
    box((x, y, h / 2), (w, d, h), "lead", bevel=0.02)
    box((x, y, h + 0.015), (w - 0.14, d - 0.14, 0.03), "dark_steel", bevel=0.006)
    bolts(x, y, h + 0.04, min(w, d) / 2 - 0.08, 12, r=0.014)
    box((x, y - d / 2 - 0.005, h * 0.5), (w - 0.12, 0.02, 0.1), "hazard", bevel=0)
    if wheel:
        handwheel((x, y, h + 0.1), 0.12)


def cabinet(x, y, w, d, h, mat="grey"):
    """A control cabinet: louvres, a gauge and the status lamp on the south face."""
    box((x, y, h / 2), (w, d, h), mat, bevel=0.015)
    for i in range(4):
        box((x - w * 0.15, y - d / 2 - 0.01, h * 0.35 + 0.07 * i), (w * 0.45, 0.02, 0.025), "dark_steel", bevel=0)
    gauge((x + w * 0.25, y - d / 2 - 0.01, h * 0.7), (0, -1, 0.15), r=0.06)
    status_lamp(x + w * 0.25, y - d * 0.2, h + 0.02)


def drift(path, n, seed, mat="bubble", size=(0.012, 0.024), scale=(1, 1, 1), down=False):
    """n particles moving along path(u, a), u in [0,1) a loop: each covers the whole
    path exactly once a loop, so it wraps seamlessly. a is a fixed random in [-1,1)."""
    rnd = random.Random(seed)
    objs = []
    for i in range(n):
        o = sphere((0, 0, 0), rnd.uniform(*size), mat, scale=scale, seg=8)
        objs.append((o, rnd.random(), rnd.uniform(-1, 1)))

    def pose(t):
        for o, ph, a in objs:
            u = (ph + (-t if down else t)) % 1.0
            o.location = path(u, a)
    LEG_POSES.append(pose)


def porthole(cx, cy, z, R, ang, r, name, k=3, arms=3, spin=0.0):
    """A bolted bullseye porthole on a vessel of radius R at angle ang: cast frame,
    a glass disc, the solution behind turning in an arms-armed vortex."""
    t = Vector((math.cos(ang), math.sin(ang), 0))
    u = t.cross(Vector((0, 0, 1))).normalized()
    w = Vector((0, 0, 1))
    c = Vector((cx, cy, z)) + t * (R - 0.02)
    cyl(tuple(c + t * 0.02), r + 0.04, 0.12, "grey", rot=along(t), verts=48)           # boss
    annulus(tuple(c + t * 0.1), r - 0.01, r + 0.1, 0.06, "dark_steel", rot=along(t))
    for i in range(12):
        a = 2 * PI * i / 12
        cyl(tuple(c + t * 0.135 + (r + 0.055) * (math.cos(a) * u + math.sin(a) * w)), 0.017, 0.025, "bare",
            rot=along(t), verts=6, bevel=0)
    cyl(tuple(c + t * 0.095), r, 0.02, "pane", rot=along(t), verts=48, bevel=0)
    fl = cyl(tuple(c + t * 0.07), r, 0.02, fluid(name, "swirl", scale=1.2 / r, k=k, arms=arms), rot=along(t),
             verts=48, bevel=0)
    fl.rotation_euler.rotate_axis("Z", spin)
    box(tuple(c + t * 0.115), (0.04, 0.04, 2 * r + 0.06), "bare", rz=ang + PI / 2, bevel=0.004)   # a bar
    return c


def helix(cx, cy, R, z0, z1, turns, a0=0.0, n_per=56):
    n = int(turns * n_per)
    return [Vector((cx + R * math.cos(a0 + 2 * PI * turns * i / n), cy + R * math.sin(a0 + 2 * PI * turns * i / n),
                    z0 + (z1 - z0) * i / n)) for i in range(n + 1)]


def strips(x0, x1, y, zb, h0, amp, n, name, waves=1.5):
    """The sloshing surface seen through a flat window: n vertical strips of fluid
    whose tops ride a travelling wave, whole wavelengths a loop."""
    W = (x1 - x0) / n
    fl = fluid(name, "flow", scale=3.0, k=1)
    objs = []
    for i in range(n):
        o = box((x0 + W * (i + 0.5), y, zb + h0 / 2), (W * 1.02, 0.08, h0), fl, bevel=0)
        objs.append((o, i / n))

    def pose(t):
        for o, f in objs:
            hh = h0 - amp + amp * math.sin(2 * PI * (waves * f - t))
            s = hh / h0                      # box() bakes its location: scale about the floor zb
            o.scale = (1, 1, s)
            o.location.z = zb * (1 - s)
    LEG_POSES.append(pose)




def deck(x0, y0, x1, y1, h=0.12, mat="dark_steel", stripe=True):
    """A low bolted plant deck under the low run (a skid, not the building's base)."""
    box(((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), mat, bevel=0.015)
    n = max(2, int((x1 - x0) / 0.35))
    for i in range(n + 1):
        xx = x0 + 0.06 + (x1 - x0 - 0.12) * i / n
        for yy in (y0 + 0.06, y1 - 0.06):
            cyl((xx, yy, h + 0.008), 0.018, 0.02, "bare", verts=6, bevel=0)
    if stripe:
        box(((x0 + x1) / 2, y0 - 0.004, h * 0.55), ((x1 - x0) * 0.6, 0.012, h * 0.5), "hazard", bevel=0)


def barrels(x, y, n=3, seed=0, z=0.0):
    rnd = random.Random(seed)
    for dx, dy in [(0, 0), (0.27, 0.06), (0.12, -0.23), (-0.15, -0.2), (0.4, -0.18), (-0.27, 0.05)][:n]:
        m = rnd.choice(["grey", "grey", "green", "lead", "hazard"])
        cyl((x + dx, y + dy, z + 0.19), 0.12, 0.38, m, verts=24)
        for zz in (0.1, 0.28):
            torus((x + dx, y + dy, z + zz), 0.122, 0.011, "bare", seg=24)
        cyl((x + dx + 0.05, y + dy + 0.03, z + 0.385), 0.025, 0.02, "brass", verts=8)


def jbox(x, y, w=0.32, d=0.22, h=0.4, mat="grey", z=0.0):
    box((x, y, z + h / 2), (w, d, h), mat, bevel=0.01)
    box((x, y - d / 2 - 0.01, z + h * 0.55), (w * 0.7, 0.02, h * 0.6), "dark_steel", bevel=0.004)
    cyl((x + w * 0.3, y, z + h + 0.04), 0.03, 0.08, "bare", verts=8)


def exchanger(x0, x1, y, z, r, mat="grey"):
    """A shell-and-tube exchanger on saddles: flanged channel heads and two nozzles."""
    drum_ew(x0, x1, y, z, r, mat=mat, bands=(), saddles=(x0 + 0.25, x1 - 0.25))
    for xx in (x0 + 0.08, x1 - 0.08):
        cyl((xx, y, z), r + 0.06, 0.07, "dark_steel", rot=(0, PI / 2, 0), verts=40)
        for i in range(10):
            a = 2 * PI * i / 10
            cyl((xx, y + (r + 0.035) * math.cos(a), z + (r + 0.035) * math.sin(a)), 0.014, 0.09, "bare",
                rot=(0, PI / 2, 0), verts=6, bevel=0)
    for xx in (x0 + 0.45, x1 - 0.45):
        cyl((xx, y, z + r + 0.06), 0.07, 0.14, "bare", verts=16)


def riser(x, y, z1, r=0.09, mat="bare"):
    cyl((x, y, z1 / 2), r, z1, mat, verts=20)
    for z in (0.15, z1 - 0.08):
        cyl((x, y, z), r + 0.04, 0.05, "dark_steel", verts=20)


def reel(x, y, axis=(1, 0, 0)):
    """A hose reel: two cheeks, a drum of black hose."""
    t = Vector(axis).normalized()
    box((x, y, 0.12), (0.5, 0.5, 0.24) if t.x else (0.5, 0.5, 0.24), "dark_steel")
    for s in (-1, 1):
        cyl(tuple(Vector((x, y, 0.42)) + t * 0.17 * s), 0.27, 0.03, "green", rot=along(t), verts=32)
    cyl((x, y, 0.42), 0.2, 0.3, "hose_k", rot=along(t), verts=32)
    for k in range(5):
        torus(tuple(Vector((x, y, 0.42)) + t * (-0.12 + 0.06 * k)), 0.2, 0.035, "hose_k", rot=along(t), seg=24)


# ======================================================================= round-3 kit
def arc_panel(cx, cy, r, z0, z1, a0, a1, mat, seg=24):
    """A curved sheet laid on a vessel of radius r between angles a0..a1: a
    replacement panel or a stencil field, standing just proud of the wall."""
    me = bpy.data.meshes.new("arc")
    bm = bmesh.new()
    rows = []
    for rr in (r, r + 0.012):
        ring = []
        for k in range(seg + 1):
            a = a0 + (a1 - a0) * k / seg
            ring.append((bm.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), z0)),
                         bm.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), z1))))
        rows.append(ring)
    inner, outer = rows
    for k in range(seg):
        bm.faces.new((outer[k][0], outer[k + 1][0], outer[k + 1][1], outer[k][1]))
        bm.faces.new((inner[k][1], inner[k + 1][1], inner[k + 1][0], inner[k][0]))
        bm.faces.new((inner[k][1], outer[k][1], outer[k + 1][1], inner[k + 1][1]))
        bm.faces.new((inner[k + 1][0], outer[k + 1][0], outer[k][0], inner[k][0]))
    for k in (0, seg):
        s = 1 if k == 0 else -1
        f = (inner[k][0], outer[k][0], outer[k][1], inner[k][1])
        bm.faces.new(f if s > 0 else tuple(reversed(f)))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("arc", me)
    sc.collection.objects.link(o)
    return _finish(o, mat, 0.004, smooth=True)


def weld_ring(cx, cy, z, r):
    torus((cx, cy, z), r + 0.004, 0.011, "seam", seg=72)


def rivet_ring(cx, cy, z, r, n, mat="bolt", rr=0.019):
    for i in range(n):
        a = 2 * PI * (i + 0.5) / n
        sphere((cx + r * math.cos(a), cy + r * math.sin(a), z), rr, mat, scale=(1, 1, 0.8), seg=8)


def vessel_band(cx, cy, z, r, n_rivets=16, lugs=3, lug_a=-PI / 2):
    """A steel band: riveted both edges, bolted lugs. Rust runs from it (the plate's drips),
    the lead's bloom hangs below it."""
    band(cx, cy, z, r, h=0.075, mat="bare", lugs=lugs, lug_a=lug_a)
    rivet_ring(cx, cy, z, r + 0.032, n_rivets)


def vertical_seams(cx, cy, r, z0, z1, angles):
    for a in angles:
        box((cx + (r + 0.004) * math.cos(a), cy + (r + 0.004) * math.sin(a), (z0 + z1) / 2),
            (0.02, 0.02, z1 - z0), "seam", rz=a, bevel=0.005)


def press(x0, x1, y, d=0.72):
    """A plate-and-frame filter press lying E-W: cast feet and rails, leaves of lead and
    plate, the hydraulic head at the east end, a drip tray below."""
    L = x1 - x0
    box(((x0 + x1) / 2, y, 0.05), (L + 0.05, d + 0.06, 0.1), "dark_steel")                      # drip tray
    for s in (-1, 1):
        box(((x0 + x1) / 2, y + s * (d / 2 - 0.03), 0.66), (L, 0.06, 0.07), "bare", bevel=0.008)  # rails
    box((x0 + 0.06, y, 0.4), (0.12, d, 0.72), "dark_steel")                                       # tail stand
    n = int((L - 0.5) / 0.1)
    for i in range(n):
        xx = x0 + 0.17 + 0.1 * i
        box((xx, y, 0.4), (0.094, d - 0.1, 0.5 + 0.02 * (i % 3 == 0)), "lead" if i % 2 else "grey",
            bevel=0.006)
    hx = x0 + 0.17 + 0.1 * n + 0.12
    box((hx, y, 0.42), (0.16, d + 0.02, 0.78), "dark_steel")                                       # head
    cyl((hx + 0.18, y, 0.45), 0.13, 0.26, "green", rot=(0, PI / 2, 0), verts=24)            # ram cylinder
    handwheel((hx + 0.34, y, 0.45), 0.14, axis=(1, 0, 0))
    box(((x0 + x1) / 2, y - d / 2 - 0.035, 0.05), (L * 0.8, 0.01, 0.06), "hazard", bevel=0)
    return hx


def stencil(loc, size, rz):
    box(loc, size, "stencil", rz=rz, bevel=0.002)


def tray(pts, w=0.16):
    """A cable tray on stand-off posts: a shallow channel, the bundle lying in it."""
    P = catmull(pts, 0.05)
    for a_, b_ in zip(P[::3], P[3::3]):
        m = (a_ + b_) / 2
        t = (b_ - a_)
        box(tuple(m), (w, t.length + 0.01, 0.02), "bare", rz=math.atan2(t.y, t.x) - PI / 2, bevel=0.003)


def prism(pts, z0, z1, mat, bevel=0.025):
    """A house on a polygon footprint (x, y pairs, anticlockwise), from z0 to z1."""
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
    return _finish(o, mat, bevel)


# ======================================================================= the circulator, round 4
# The plan (tiles, x east, y north; the footprint is +-2.5). The middle three tiles of
# every edge meet it with a wall, for the pipe pictures (template rule 6); the corners
# drop out unevenly (FFF #350): the north-west and north-east hold round vessels with
# ground round them, the south-west and south-east are ground. The mass is three piles:
# the reactor with its legs and the compressor (the centre and east), the scrubber and
# the feed drum (the west), the press house, the receiver and the pump house (the south).
RX, RY, R, H = 1.3, 0.1, 0.9, 3.05
LEGS = [(-0.32, 0.62, 2, "fl_f1"), (0.12, -0.72, -2, "fl_f2")]
Z0, Z1, LR = 0.42, 2.45, 0.27
EDGE = 2.465                     # a wall's face at the footprint edge, less a hair
# The corner vessels, drawn in so their foot rings stop at the footprint's edge (+-2.5):
# round 5 had the scrubber's at -2.57, the condenser's and the east pot's at +2.52
SX, SY, SR, SH = -1.92, 1.85, 0.5, 1.85          # the scrubber (round 5: x -1.99)
TX, TY, TR = 2.01, 1.92, 0.4                      # the vent condenser (round 5: x 2.04)
PX, PY, PR = 2.09, 1.06, 0.30                     # the east nozzle's pot (round 5: 2.12, 1.02, r 0.32: its
                                                  # foot over the edge, its band into the reactor's)
XC0, XC1 = -1.30, 1.42                            # the exchanger (round 5 -1.55, 1.55; the clip fixes -1.42, 1.45)
MX, MY, MR = -1.04, 0.76, 0.22                    # the make-up pot (round 5: -1.02, 0.62, r 0.3)
CAB = (-0.38, -0.33, 0.36, 0.36)                  # the sampling cabinet: centre, w, d (round 5: -0.38, -0.5, 0.44, 0.42)


def reactor():
    cyl((RX, RY, 0.08), R + 0.12, 0.16, "dark_steel", verts=72)
    bolts(RX, RY, 0.17, R + 0.07, 20, r=0.018)
    cyl((RX, RY, H / 2 + 0.08), R, H - 0.16, "lead", verts=96)
    for z in (0.5, 1.25, 2.0, 2.65):
        vessel_band(RX, RY, z, R, n_rivets=12, lug_a=-PI / 2 - 0.4)
    for z in (0.88, 1.62):
        weld_ring(RX, RY, z, R)
    vertical_seams(RX, RY, R, 0.55, 1.2, (-2.0, -0.4))
    vertical_seams(RX, RY, R, 1.3, 1.95, (-1.2, 0.6))
    arc_panel(RX, RY, R, 1.3, 1.95, -2.4, -1.75, "lead_new")
    arc_panel(RX, RY, R + 0.002, 2.08, 2.26, -1.85, -1.25, "stencil")
    # the head: lead, the agitator drive and its motor, a manway
    head(RX, RY, H, R, 0.3, "lead")
    flange_ring(RX, RY, H + 0.005, R - 0.02, mat="bare", h=0.06, nb=20)
    cyl((RX + 0.42, RY - 0.32, H + 0.26), 0.19, 0.12, "dark_steel", verts=32)
    bolts(RX + 0.42, RY - 0.32, H + 0.33, 0.15, 8, r=0.018)
    cyl((RX - 0.48, RY + 0.3, H + 0.28), 0.07, 0.18, "bare", verts=16)          # relief valve
    cyl((RX - 0.48, RY + 0.3, H + 0.39), 0.1, 0.07, "brass", verts=6, bevel=0)
    cyl((RX - 0.1, RY - 0.05, H + 0.34), 0.22, 0.18, "dark_steel", verts=32)     # the agitator's gearbox
    box((RX + 0.24, RY + 0.24, H + 0.44), (0.36, 0.38, 0.32), "green", rz=0.3)
    bundle([(RX + 0.24, RY + 0.42, H + 0.47), (RX + 0.5, RY + 0.62, H + 0.1), (RX + 0.66, RY + 0.55, 2.4)],
           cols=("black", "yellow"))
    ladder(RX + 0.44, RY - R * 0.88 - 0.09, 0.2, H - 0.05, axis="x")     # (round 5: 0.04 nearer, into the shell)
    gauge((RX - 0.05, RY - R - 0.02, 1.0), (0.0, -1, 0.15), r=0.08, double="gauge-reactor-lower")
    # the east wall at tile 0 is the reactor's own foot; at tile +1 its side nozzle runs
    # out to the edge on a pot, at tile -1 the instrument house
    pipe([(RX + R * 0.62, RY + R * 0.75, 0.62), (PX - 0.12, PY - 0.02, 0.62), (PX - 0.02, PY - 0.02, 0.62)],
         r=0.13, mat="bare", marks=((0.45, "yellow"),))
    vtank(PX, PY, PR, 1.15, "lead", bands=(0.55,), top="dark_steel", nozzle=(0.0, 0.0))
    # its flange at the pot's wall, on the pipe's axis (round 5 laid a flat ring across the
    # pipe 0.2 inside the pot, its rim through the pot's west wall)
    xf = PX - PR - 0.02
    cyl((xf, PY - 0.02, 0.62), 0.15, 0.04, "dark_steel", rot=(0, PI / 2, 0), verts=32)
    for i in range(6):
        a = TAU * (i + 0.5) / 6
        cyl((xf - 0.025, PY - 0.02 + 0.125 * math.cos(a), 0.62 + 0.125 * math.sin(a)), 0.016, 0.02, "bolt",
            rot=(0, PI / 2, 0), verts=6, bevel=0)


def legs():
    for lx, ly, k, nm in LEGS:
        with asm():
            leg(lx, ly, k, nm)
    return legs_loop()


def leg(lx, ly, k, nm):
    """One glass leg: its cast foot, flanges, the glass, the solution, a middle band, four
    straps, its cap."""
    cyl((lx, ly, 0.2), LR + 0.1, 0.4, "dark_steel", verts=40)
    bolts(lx, ly, 0.41, LR + 0.06, 8, r=0.018)
    flange_ring(lx, ly, Z0 - 0.03, LR, mat="bare", h=0.06, nb=12)
    flange_ring(lx, ly, Z1 + 0.01, LR, mat="bare", h=0.06, nb=12)
    with grp("legs"):
        cyl((lx, ly, (Z0 + Z1) / 2), LR, Z1 - Z0, "glass", verts=48, bevel=0)
        fl = cyl((lx, ly, (Z0 + Z1) / 2), LR - 0.05, Z1 - Z0 - 0.02, fluid(nm, "flow", scale=3.2, k=k),
                 verts=48, bevel=0)
    fl.visible_diffuse = False      # the solution lights its glass, not the lead beside it
    fl.visible_glossy = False       # nor is it mirrored in the vessels round it: the glow is the legs only
    band(lx, ly, (Z0 + Z1) / 2, LR, h=0.07, mat="bare", lugs=2, lug_a=0.3)
    for j in range(4):
        a = 2 * PI * (j + 0.5) / 4 + 0.3
        box((lx + (LR + 0.01) * math.cos(a), ly + (LR + 0.01) * math.sin(a), (Z0 + Z1) / 2),
            (0.045, 0.045, Z1 - Z0), "bare", rz=a, bevel=0.006)
    cyl((lx, ly, Z1 + 0.16), LR * 0.78, 0.24, "dark_steel", verts=32)
    head(lx, ly, Z1 + 0.28, LR * 0.78, 0.1, "lead")


def legs_loop():
    (ax, ay, _, _), (bx, by, _, _) = LEGS
    with grp("legs"):
        drift(lambda u, a: (ax + (LR - 0.04) * math.cos(-PI / 2 + a), ay + (LR - 0.04) * math.sin(-PI / 2 + a),
                            Z0 + 0.04 + (Z1 - Z0 - 0.08) * u), 20, 11)
        drift(lambda u, a: (bx + (LR - 0.05) * math.cos(-PI / 2 + a), by + (LR - 0.05) * math.sin(-PI / 2 + a),
                            Z0 + 0.04 + (Z1 - Z0 - 0.08) * u), 16, 12, mat="fleck", size=(0.014, 0.024),
              scale=(1.5, 1, 0.6), down=True)
    # the loop's top: fat hoses from each leg's cap into the reactor's shoulder
    hose([(ax, ay, Z1 + 0.42), (ax + 0.14, ay + 0.06, 3.0), (0.3, 0.62, 3.05), (RX - R + 0.04, RY + 0.3, 2.74)],
         r=0.13, mat="hose")
    hose([(bx, by, Z1 + 0.42), (bx + 0.16, by + 0.02, 2.95), (0.62, -0.55, 2.8),
          (RX - R * 0.62, RY - R * 0.72, 2.4)], r=0.13, mat="hose_k")
    # the loop's foot: a cast header from the reactor's foot to both legs, a valve on it
    pipe([(RX - R + 0.02, RY + 0.25, 0.3), (0.3, 0.5, 0.24), (ax + LR, ay, 0.24)], r=0.11, mat="dark_steel",
         marks=((0.5, "red"),))
    pipe([(RX - R * 0.65, RY - R * 0.7, 0.3), (0.65, -0.68, 0.24), (bx + LR, by, 0.24)], r=0.11, mat="dark_steel",
         marks=((0.5, "red"),))
    valve(0.15, 0.0, 0.0, 0.62)
    return ax, ay, bx, by


def north():
    """The north edge's wall at tiles -1, 0, +1: a low exchanger on saddles, under the
    band the north pictures draw in (behind the building). The north-west corner holds
    the scrubber, round, ground round it; the north-east the vent condenser."""
    sx, sy, sr, sh = SX, SY, SR, SH
    cyl((sx, sy, 0.07), sr + 0.08, 0.14, "dark_steel", verts=64)
    cyl((sx, sy, sh / 2 + 0.07), sr, sh - 0.14, "oxide", verts=64)
    for z in (0.95, 1.65):
        vessel_band(sx, sy, z, sr, n_rivets=9, lugs=2, lug_a=-PI / 4)
    head(sx, sy, sh, sr, 0.2, "oxide")
    nx, ny = sx + 0.16, sy - 0.16
    cyl((nx, ny, sh + 0.2), 0.09, 0.16, "bare", verts=24)
    flange_ring(nx, ny, sh + 0.28, 0.08, mat="bare", h=0.04, nb=6)
    arc_panel(sx, sy, sr + 0.002, 1.18, 1.32, -1.6, -0.9, "stencil")
    tx, ty = TX, TY
    vtank(tx, ty, TR, 1.75, "copper", bands=(0.7, 1.35), top="dark_steel", nozzle=None)
    cyl((tx - 0.1, ty - 0.06, 1.98), 0.06, 0.28, "copper", verts=16)
    torus((tx - 0.1, ty - 0.06, 2.12), 0.07, 0.02, "copper", seg=16)
    # (the clip fixes: its heads ran into the condenser and the scrubber; drawn in again with them)
    exchanger(XC0, XC1, 2.14, 0.38, 0.3, mat="grey")
    stencil((0.15, 1.81, 0.52), (0.5, 0.01, 0.12), 0.0)
    # the crust-gas compressor, low, behind the legs
    box((0.35, 1.36, 0.08), (1.05, 0.52, 0.16), "dark_steel")
    cyl((0.15, 1.36, 0.4), 0.24, 0.48, "dark_steel", rot=(0, PI / 2, 0), verts=32)
    for i in range(4):
        cyl((-0.03 + 0.12 * i, 1.36, 0.4), 0.265, 0.03, "bare", rot=(0, PI / 2, 0), verts=32, bevel=0)
    box((0.66, 1.36, 0.38), (0.38, 0.4, 0.42), "green")
    coupling(0.43, 1.36, 0.38, 0.12, axis=(1, 0, 0), axial=0.7, layer="coupling-compressor")     # centred in its 0.08 gap
    hose([(0.15, 1.36, 0.66), (0.08, 1.05, 0.98), (LEGS[0][0] + 0.2, LEGS[0][1] + 0.2, 1.25)], r=0.1, mat="hose")
    # the scrubber's line, high, into the reactor head
    hose([(nx, ny, sh + 0.32), (-1.3, 1.35, 2.35), (-0.4, 1.12, 2.8), (0.6, 0.85, 3.12),
          (RX - 0.25, RY + 0.42, 3.22)], r=0.12, mat="hose")
    hose([(1.35, 2.08, 0.78), (1.6, 1.42, 1.12), (RX + 0.3, RY + R - 0.02, 1.25)], r=0.1, mat="hose_k")
    pipe([(tx - 0.32, ty - 0.12, 0.9), (1.55, 1.25, 0.92), (RX + 0.45, RY + R * 0.75, 0.95)], r=0.07, mat="copper")


def west():
    """The feed drum lying north-south: the west wall at tiles -1, 0, +1. Its south head
    stops short of the corner, and its north end runs into the scrubber's foot."""
    drum_ns(-1.97, -1.5, 1.12, 0.6, 0.5, mat="ochre", bands=(-0.75, 0.45), saddles=(-1.0, 0.7))
    box((-1.9, -0.1, 1.1), (0.34, 0.4, 0.07), "green")
    stencil((-1.46, -0.15, 0.66), (0.01, 0.55, 0.15), 0.0)
    gauge((-1.47, 0.3, 0.8), (1, 0, 0.3), r=0.08)
    ax, ay = LEGS[0][0], LEGS[0][1]
    # (round 5 ran it 0.05 through the dosing pump's motor; the clip fixes lifted it 0.05 over the
    # coupling: now north of the motor, under the make-up pot)
    hose([(-1.5, 0.42, 0.5), (-1.0, 0.43, 0.46), (ax - LR - 0.08, ay - 0.08, 0.3)], r=0.11, mat="hose")
    # a dosing pump between the drum and the riser, olive, on its skid
    skid(-1.42, -0.05, -0.62, 0.32, 0.1)
    box((-1.2, 0.13, 0.3), (0.34, 0.3, 0.3), "green")
    cyl((-0.85, 0.13, 0.28), 0.14, 0.22, "dark_steel", rot=(0, PI / 2, 0), verts=24)
    coupling(-0.995, 0.13, 0.28, 0.09, axis=(1, 0, 0), axial=0.6, layer="coupling-dosing")
    hose([(-0.85, 0.13, 0.45), (-0.62, 0.3, 0.7), (ax - 0.18, ay - 0.2, 0.62)], r=0.06, mat="hose_k")
    # the scrubber's drain header, on its skid behind the make-up pot
    skid(-1.33, 1.12, -0.5, 1.76, 0.12)
    lagged([(-1.5, 1.46, 0.36), (-1.0, 1.42, 0.38), (-0.52, 1.36, 0.36)], r=0.13,
           marks=((0.62, "green"),))
    valve(-0.75, 1.62, 0.12, 0.5, wheel="yellow")
    # the settling pot between the drum and the downcomer: the hollow filled with one mass
    vtank(-0.92, -0.92, 0.44, 1.4, "lead", bands=(0.6, 1.05), top="dark_steel", nozzle=(0.3, 0.3))
    hose([(-0.92 + 0.13, -0.92 + 0.13, 1.72), (-0.55, -0.7, 1.9), (LEGS[1][0] - LR - 0.02, LEGS[1][1] + 0.05, 1.7)],
         r=0.1, mat="hose")
    hose([(-1.5, -0.95, 0.45), (-1.3, -1.25, 0.3), (-0.92, -1.42, 0.3)], r=0.09, mat="hose_k")
    # the feed main from the drum to the riser's foot, lagged, a valve station on it
    lagged([(-1.48, 1.1, 0.42), (-1.05, 1.1, 0.45), (-0.62, 0.92, 0.4), (LEGS[0][0] - LR, LEGS[0][1] + 0.05, 0.32)],
           r=0.11, marks=((0.3, "green"), (0.62, "yellow")))
    # the make-up pot over the feed main, olive-banded lead: the hollow behind the dosing pump
    vtank(MX, MY, MR, 1.05, "cream", bands=(0.5,), top="dark_steel", nozzle=(0.2, -0.3))
    hose([(MX + 0.06 * MR / 0.3, MY - 0.09 * MR / 0.3, 1.35), (-0.8, 0.52, 1.5),
          (LEGS[0][0] - LR - 0.02, LEGS[0][1] - 0.05, 1.45)],
         r=0.08, mat="hose_k")
    bundle([(-1.42, -0.62, 0.4), (-1.0, -0.55, 0.14), (-0.5, -0.2, 0.14), (LEGS[1][0] - 0.3, LEGS[1][1], 0.3)],
           cols=("red", "black", "grey"))


def skid(x0, y0, x1, y1, h, mat="dark_steel"):
    box(((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), mat, bevel=0.012)
    for xx in (x0 + 0.06, x1 - 0.06):
        for yy in (y0 + 0.06, y1 - 0.06):
            cyl((xx, yy, h + 0.008), 0.022, 0.02, "bare", verts=6, bevel=0)


PRESS = (-1.42, -0.62, -1.98, 0.66)            # the filter press: tail x, head x, its line y, depth
PACK = []                                       # the leaf pack and the tail stand
CAKE = []
LAST_LEAF_E = PRESS[0] + 0.2 + 0.1 * 4 + 0.045  # the last leaf's east face, where the cake hangs
CAKE_T, CAKE_Z0, CAKE_D = 0.08, 0.62, PRESS[3] - 0.18
RAM_Z = 1.14                                    # the ram's axis: over the receiver's crown (z 0.975)


def south():
    """Three masses meeting the south edge: the press house at tile -1 (the filter press
    on its lead-lined drop box: the solid out), the filtrate receiver at tile 0 (the
    output's wall: its picture stands on the receiver's flank), the pump house at +1.
    The south-west and south-east corners are ground."""
    bx, by = LEGS[1][0], LEGS[1][1]
    # the drop box, lead-lined, with the press standing on it
    box((-1.055, -1.98, 0.27), (0.91, 0.9, 0.54), "lead", bevel=0.025)   # (round 5: to x -0.53, under the receiver's head)
    box((-1.02, -2.43 - 0.005, 0.27), (0.8, 0.02, 0.12), "hazard", bevel=0)
    cyl((-1.02, -1.98, 0.56), 0.36, 0.04, "dark_steel", verts=32)
    L0, L1, yp, d = PRESS
    # the side rails, run on west under the tail stand's stroke (the clip fixes)
    for s_ in (-1, 1):
        box(((L0 - STROKE + L1) / 2, yp + s_ * (d / 2 - 0.03), 1.18), (L1 - L0 + STROKE, 0.07, 0.08), "bare",
            bevel=0.01)
    # the leaf pack and the tail stand: they back off west along the rails, once a craft
    # (the press layer). The tail stand's foot stands 0.04 over the drop box's lid disc,
    # which it slides over
    with grp("press"):
        PACK.append(box((L0 + 0.06, yp, 0.92), (0.12, d, 0.66), "dark_steel"))
        for i in range(5):
            PACK.append(box((L0 + 0.2 + 0.1 * i, yp, 0.9), (0.09, d - 0.08, 0.56), "lead" if i % 2 else "cream",
                            bevel=0.01))
    # the head: bolted down, it does not move. Its ram and handwheel stand over the
    # receiver's crown (round 5 sat them in it, at z 0.95, and the receiver's west head in
    # the press head)
    box((L1 - 0.1, yp, 0.94), (0.18, d + 0.04, 0.72), "dark_steel")
    cyl((L1 + 0.08, yp, RAM_Z), 0.14, 0.2, "green", rot=(0, PI / 2, 0), verts=24)
    handwheel((L1 + 0.22, yp, RAM_Z), 0.15, axis=(1, 0, 0), mat="yellow")
    # the chute mouth the cake drops into: a dark opening in the drop box's steel lid, under
    # the gap the stroke opens
    x0, x1 = LAST_LEAF_E - STROKE - 0.015, L1 - 0.1 - 0.09 - 0.005
    box(((x0 + x1) / 2, yp, 0.582), (x1 - x0, CAKE_D + 0.03, 0.006), "dark", bevel=0)
    # the cake: grey-buff filter cake on the last leaf, only ever drawn in motion (spec 8.7)
    with grp("press"):
        CAKE.append(box((LAST_LEAF_E + CAKE_T / 2, yp, CAKE_Z0 + 0.25), (CAKE_T, CAKE_D, 0.5), "cake", bevel=0.02))
    # the filtrate receiver: lying east-west on saddles, its flank at the edge; its west
    # head drawn back clear of the press head, its skid clear of the drop box
    skid(-0.56, -2.46, 0.66, -1.6, 0.12)
    drum_ew(-0.46, 0.54, -2.04, 0.58, 0.4, mat="green", bands=(-0.25, 0.3), saddles=(-0.31, 0.38))
    stencil((0.05, -2.43, 0.62), (0.36, 0.01, 0.1), 0.0)
    # (the clip fixes: it started 0.04 over the last leaf)
    hose([(L1 - 0.08, yp + 0.06, 1.33), (-0.35, -1.55, 1.25), (-0.1, -1.75, 0.95)], r=0.1, mat="hose_k")
    # the pump house: the motor olive, it lifts the downcomer's return
    box((1.12, -1.98, 0.42), (0.86, 0.92, 0.84), "cream", bevel=0.025)
    for i in range(4):
        box((0.9, -2.445, 0.3 + 0.1 * i), (0.36, 0.02, 0.035), "dark_steel", bevel=0)
    gauge((1.35, -2.45, 0.62), (0, -1, 0.15), r=0.07)
    status_lamp(1.42, -2.2, 0.86)
    pv = pump(1.1, -1.9, (-1, 0), 0.75, z0=0.84)
    hose([pv, (0.7, -1.55, 1.45), (0.4, -1.25, 1.25), (bx + 0.1, by - LR - 0.04, 0.9)], r=0.12, mat="hose")
    # under the legs, west of the downcomer: the sampling cabinet, where the precipitate is drawn off
    # (moved north and narrowed: round 5's stood into the settling pot's foot and shell and the
    # downcomer's foot)
    cx_, cy_, cw_, cd_ = CAB
    box((cx_, cy_, 0.38), (cw_, cd_, 0.76), "oxide", bevel=0.02)
    box((cx_, cy_ - cd_ / 2 - 0.01, 0.42), (cw_ * 0.68, 0.02, 0.36), "dark_steel", bevel=0.004)
    gauge((cx_ + 0.1, cy_ - cd_ / 2 - 0.02, 0.62), (0, -1, 0.2), r=0.06)
    hose([(cx_, cy_, 0.8), (-0.2, -0.5, 1.0), (LEGS[1][0] - LR - 0.02, LEGS[1][1] + 0.08, 1.05)], r=0.05,
         mat="cable_black")
    # between the legs' feet and the south units: the sampling manifold, low, its valves
    skid(-0.48, -1.55, 0.62, -1.1, 0.14)
    cyl((0.07, -1.32, 0.32), 0.15, 0.95, "dark_steel", rot=(0, PI / 2, 0), verts=24)
    for xx, wh in ((-0.3, "red"), (0.07, "yellow"), (0.42, "red")):
        valve(xx, -1.32, 0.3, 0.45, wheel=wh)
    bundle([(1.42, -1.6, 0.85), (1.6, -1.2, 0.2), (RX + R * 0.55, RY - R * 0.75, 0.45)],
           cols=("red", "yellow", "black"))


def east():
    """The east edge: the instrument house at tile -1, the reactor's foot at 0, the side
    nozzle's pot at +1 (reactor()). The south-east corner is ground."""
    # its north-west corner chamfered along the reactor's foot ring (round 5's box stood 0.06-0.12
    # into the reactor's foot ring, shell, bands and ladder)
    prism([(1.77, -1.42), (2.43, -1.42), (2.43, -0.58), (2.11, -0.58), (1.77, -0.92)], 0.0, 1.3, "grey")
    for i in range(4):
        box((2.1, -1.43, 0.45 + 0.08 * i), (0.4, 0.02, 0.03), "dark_steel", bevel=0)
    gauge((1.76, -1.12, 0.95), (-1, -0.2, 0.2), r=0.07)
    status_lamp(2.2, -0.9, 1.32)
    bundle([(2.22, -0.72, 1.2), (2.0, -0.42, 0.3), (RX + R * 0.8, RY - R * 0.5, 0.35)], cols=("grey", "red"))


# ======================================================================= round 5: the details
# Small surface detail only: the model (shape, layout, pipe pictures, silhouette) is
# approved as round 4 left it. Each piece sits on a surface the camera sees (south-facing
# walls and the tops) and none changes the outline.
def on_wall(cx, cy, r, ang, z, out=0.0):
    """A point on a standing vessel's wall at angle ang, height z, `out` proud of it;
    and the outward normal."""
    n = Vector((math.cos(ang), math.sin(ang), 0))
    return Vector((cx, cy, z)) + n * (r + out), n


def insp_plate(cx, cy, r, ang, z0, z1, half, mat="bare", nb=3):
    """A bolted inspection plate on a vessel: a curved cover, a bolt row down each side
    and along top and bottom."""
    arc_panel(cx, cy, r + 0.004, z0, z1, ang - half, ang + half, mat)
    for a in (ang - half * 0.82, ang + half * 0.82):
        for k in range(nb):
            p, n = on_wall(cx, cy, r, a, z0 + (z1 - z0) * (k + 0.5) / nb, 0.018)
            cyl(tuple(p), 0.014, 0.018, "bolt", rot=along(n), verts=6, bevel=0)
    for zz in (z0 + 0.025, z1 - 0.025):
        for k in range(3):
            p, n = on_wall(cx, cy, r, ang - half * 0.4 + half * 0.4 * k, zz, 0.018)
            cyl(tuple(p), 0.014, 0.018, "bolt", rot=along(n), verts=6, bevel=0)


def rivet_column(cx, cy, r, ang, z0, z1, step=0.075):
    """A riveted vertical seam: a strap and a row of rivet heads (the foundry's panels)."""
    vertical_seams(cx, cy, r, z0, z1, (ang,))
    n = int((z1 - z0) / step)
    for k in range(n + 1):
        p, _ = on_wall(cx, cy, r, ang, z0 + step * k, 0.016)
        sphere(tuple(p), 0.016, "bolt", scale=(1, 1, 0.8), seg=8)


def flat_plate(loc, w, h, face="S", mat="bare", bolts_=True):
    """A bolted plate on a flat south (or top) face."""
    x, y, z = loc
    if face == "S":
        box((x, y - 0.006, z), (w, 0.012, h), mat, bevel=0.003)
        if bolts_:
            for sx_ in (-1, 1):
                for sz_ in (-1, 1):
                    cyl((x + sx_ * (w / 2 - 0.025), y - 0.014, z + sz_ * (h / 2 - 0.025)), 0.012, 0.012, "bolt",
                        rot=(PI / 2, 0, 0), verts=6, bevel=0)
    else:
        box((x, y, z + 0.006), (w, h, 0.012), mat, bevel=0.003)
        if bolts_:
            for sx_ in (-1, 1):
                for sy_ in (-1, 1):
                    cyl((x + sx_ * (w / 2 - 0.025), y + sy_ * (h / 2 - 0.025), z + 0.014), 0.012, 0.012, "bolt",
                        verts=6, bevel=0)


def id_panel(loc, w, h, stripe="red", face="S"):
    """An identification plate, no text: a cream field, a coloured band across it, four
    corner screws."""
    x, y, z = loc
    flat_plate(loc, w, h, face, "stencil")
    if face == "S":
        box((x, y - 0.014, z + h * 0.15), (w * 0.92, 0.006, h * 0.28), stripe, bevel=0)
    else:
        box((x, y + h * 0.15, z + 0.014), (w * 0.92, h * 0.28, 0.006), stripe, bevel=0)


def hazard_tag(loc, w, h, face="S"):
    x, y, z = loc
    if face == "S":
        box((x, y - 0.007, z), (w, 0.014, h), "hazard", bevel=0.002)
    else:
        box((x, y, z + 0.007), (w, h, 0.014), "hazard", bevel=0.002)


def weld_ring_x(x, y, z, r):
    torus((x, y, z), r + 0.004, 0.01, "seam", rot=(0, PI / 2, 0), seg=64)


def weld_ring_y(x, y, z, r):
    torus((x, y, z), r + 0.004, 0.01, "seam", rot=(PI / 2, 0, 0), seg=64)


def manway_top(x, y, z, r=0.13, nb=10):
    """A bolted manway cover on a top: a disc, its bolt ring, a lifting handle."""
    cyl((x, y, z + 0.015), r, 0.03, "bare", verts=32, bevel=0.004)
    bolts(x, y, z + 0.035, r - 0.025, nb, r=0.012)
    torus((x, y, z + 0.05), 0.04, 0.008, "yellow", rot=(PI / 2, 0, 0), seg=16)


OIL = bpy.data.materials.new("oil")
OIL.use_nodes = True
M["oil"] = OIL


def _oil_material():
    """Oil and wet dirt on the ground: a dark, slightly glossy film whose coverage is a
    broken noise inside an elliptical falloff -- at most 45 % opaque, so the plate's
    outline (alpha over 128) is not changed by it."""
    nt = OIL.node_tree
    g = _G(OIL)
    out = nt.nodes["Material Output"]
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#1C140C")
    b.inputs["Roughness"].default_value = 0.3
    tc = g.node("ShaderNodeTexCoord").outputs["Generated"]
    sep = g.node("ShaderNodeSeparateXYZ", Vector=tc)
    dx = g.math("SUBTRACT", sep.outputs["X"], 0.5)
    dy = g.math("SUBTRACT", sep.outputs["Y"], 0.5)
    rr = g.math("SQRT", g.math("ADD", g.math("MULTIPLY", dx, dx), g.math("MULTIPLY", dy, dy)))
    fall = g.remap(rr, 0.5, 0.15)
    pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
    blot = g.remap(g.noise(pos, 6, detail=5, rough=0.6, distortion=0.5), 0.42, 0.62)
    alpha = g.math("MULTIPLY", g.math("MULTIPLY", fall, blot), 0.8, clamp=True)
    alpha = g.math("MINIMUM", alpha, 0.45)
    tr = g.node("ShaderNodeBsdfTransparent")
    mix = g.node("ShaderNodeMixShader", Fac=alpha)
    g.l.new(tr.outputs[0], mix.inputs[1])
    g.l.new(b.outputs[0], mix.inputs[2])
    g.l.new(mix.outputs[0], out.inputs["Surface"])


_oil_material()
STAINS = []


def stain(x, y, rx, ry, rz=0.0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, 0.004), rotation=(0, 0, rz))
    o = bpy.context.active_object
    o.scale = (rx * 2, ry * 2, 1)
    bpy.ops.object.transform_apply(scale=True)
    o.visible_shadow = False
    STAINS.append(o)
    return _finish(o, "oil", 0)


def details():
    # ---- the reactor (lead): a bolted inspection plate low on its front, a hazard tag and
    # an ID plate under the stencil, a rivet column on the replacement sheet's edge
    insp_plate(RX, RY, R, -2.12, 0.62, 0.98, 0.22, mat="lead_new")
    p, _ = on_wall(RX, RY, R, -1.55, 2.4, 0.0)
    hazard_tag((p.x, p.y - 0.004, 2.4), 0.22, 0.07)
    rivet_column(RX, RY, R, -2.42, 1.32, 1.93)
    rivet_column(RX, RY, R, -1.73, 1.32, 1.93)
    p, _ = on_wall(RX, RY, R, -1.42, 1.68, 0.0)      # (the clip fixes: 0.12 rad west, off the ladder's rail)
    gauge((p.x, p.y - 0.02, 1.68), (0.35, -1, 0.15), r=0.065, double="gauge-reactor-upper")
    # ---- the scrubber (oxide red): riveted panel seams, weld rings, an inspection plate,
    # a gauge, a red pipe-marking band on its nozzle
    sx, sy, sr = SX, SY, SR
    for a in (-2.15, -1.05):
        rivet_column(sx, sy, sr, a, 1.0, 1.6)
    weld_ring(sx, sy, 1.3, sr)
    insp_plate(sx, sy, sr, -2.45, 1.12, 1.5, 0.3, mat="bare")
    p, _ = on_wall(sx, sy, sr, -0.75, 1.42, 0.0)
    gauge((p.x, p.y - 0.01, 1.42), (0.6, -1, 0.15), r=0.06, double="gauge-scrubber")
    cyl((sx + 0.16, sy - 0.16, 1.95), 0.098, 0.04, "red", verts=24, bevel=0.003)
    # ---- the feed drum (ochre): weld rings round it, a longitudinal weld bead, a bolted
    # manway on top, an ID plate and a hazard tag on its flank
    for yy in (-0.2, 0.92):
        weld_ring_y(-1.97, yy, 0.6, 0.5)
    box((-1.97 + 0.2, -0.2, 0.6 + 0.46), (0.018, 2.4, 0.018), "seam", bevel=0.004)
    manway_top(-1.97, -1.12, 1.1)
    id_panel((-1.97, -1.69, 0.66), 0.22, 0.14, stripe="green")
    # ---- the make-up pot (cream): a gauge and a red ID band
    cyl((MX, MY, 0.86), MR + 0.01, 0.05, "red", verts=40, bevel=0.003)
    p, _ = on_wall(MX, MY, MR, -1.9, 0.62, 0.0)
    gauge((p.x, p.y - 0.01, 0.62), (-0.4, -1, 0.15), r=0.05)
    # ---- the settling pot (lead): a manway on its head
    manway_top(-0.92 - 0.14, -0.92 - 0.1, 1.4 + 0.1, r=0.1, nb=8)
    # ---- the vent condenser (copper): rivet columns, an ID plate on its band
    for a in (-2.0, -1.0):
        rivet_column(TX, TY, TR, a, 0.2, 0.65)
        rivet_column(TX, TY, TR, a, 0.78, 1.3)
    p, _ = on_wall(TX, TY, TR, -1.55, 1.04, 0.0)
    gauge((p.x, p.y - 0.01, 1.04), (0, -1, 0.15), r=0.06)
    # ---- the receiver (green): weld rings, a manway on top, a hazard tag on its west head side
    for xx in (-0.02, 0.48):
        weld_ring_x(xx, -2.04, 0.58, 0.4)
    manway_top(0.32, -2.0, 0.98, r=0.11, nb=8)
    # ---- the pump house (cream): a riveted top edge, a hazard tag, an ID plate, a bolted
    # inspection plate
    for k in range(11):
        cyl((0.74 + 0.077 * k, -2.452, 0.79), 0.013, 0.014, "bolt", rot=(PI / 2, 0, 0), verts=6, bevel=0)
    hazard_tag((1.42, -2.44, 0.3), 0.18, 0.12)
    id_panel((1.15, -2.44, 0.2), 0.2, 0.12, stripe="red")
    # ---- the instrument house (grey): a hazard band, an ID plate, a bolted plate
    hazard_tag((2.1, -1.425, 1.16), 0.56, 0.06)
    id_panel((1.92, -1.425, 0.95), 0.2, 0.13, stripe="yellow")
    flat_plate((2.28, -1.425, 0.86), 0.18, 0.2, mat="bare")
    # ---- the sampling cabinet (oxide): an ID plate on its top
    id_panel((CAB[0], CAB[1], 0.76), 0.24, 0.15, stripe="yellow", face="T")
    # ---- the press: a hazard tag on the head
    hazard_tag((-0.72, -2.335, 1.12), 0.14, 0.06)
    # ---- the compressor (dark steel, green motor): a gauge on its casing
    gauge((0.15, 1.1, 0.5), (0, -1, 0.3), r=0.055)
    # ---- oil and wet dirt on the ground at the feet: under the pumps and the press, at
    # the reactor's foot, the legs' feet, the drum's saddles
    stain(1.05, -2.34, 0.42, 0.14, 0.1)
    stain(-1.0, -2.37, 0.5, 0.12, -0.05)      # (four stains pulled inside the footprint's edges)
    stain(2.26, -1.52, 0.22, 0.12)
    stain(1.55, -0.95, 0.3, 0.25)
    stain(-0.5, -1.62, 0.35, 0.12)
    stain(-1.65, -1.6, 0.25, 0.15)
    stain(-2.2, -1.0, 0.15, 0.3)
    stain(2.3, 0.4, 0.15, 0.3)
    stain(1.85, -1.95, 0.32, 0.22, 0.4)
    stain(-1.95, -2.05, 0.28, 0.2, -0.3)
    stain(-0.2, -2.38, 0.3, 0.1)


# ======================================================================= the animation set's parts
# options/animation/anim_previews.py as fixed (6-all-fixed.gif), built here rather than patched on.
TAU = 2 * math.pi
ZB = H + 0.66                                   # the drive's belt line
C1, R1 = Vector((RX - 0.1, RY - 0.05)), 0.3     # the big five-spoked pulley, on the agitator's shaft
C2, R2 = Vector((RX + 0.36, RY + 0.34)), 0.12   # the motor's three-spoked pulley
DRIVE = {}


def drive():
    """The agitator drive on the reactor head, in place of round 5's head coupling: the shaft
    out of the gearbox, a bearing collar, the motor's stub shaft, a big five-spoked pulley,
    an open flat belt with steel lacing clips, the motor's pulley. 24 f: the big pulley turns
    two spoke steps (144 deg) a loop, the small one TRAVEL / R2 radians, the clips ride the
    belt (they lie along it: the clip fixes)."""
    cyl((C1.x, C1.y, H + 0.6), 0.055, 0.34, "bare", verts=20)
    cyl((C1.x, C1.y, H + 0.47), 0.1, 0.06, "dark_steel", verts=24)
    bolts(C1.x, C1.y, H + 0.505, 0.08, 6, r=0.014)
    cyl((C2.x, C2.y, H + 0.63), 0.04, 0.1, "bare", verts=16)

    def pulley(c, r, spokes, rim_mat, spoke_mat, h):
        root = bpy.data.objects.new("pulley", None)
        sc.collection.objects.link(root)
        root.parent = ROOT
        root.location = (c.x, c.y, ZB)
        with grp("drive"):
            annulus((0, 0, 0), r - 0.045, r, h, rim_mat, parent=root)
            torus((0, 0, h / 2), r - 0.02, 0.008, "bare", seg=48, parent=root)          # a worn bright lip
            cyl((0, 0, 0), r * 0.3, h + 0.02, "dark_steel", verts=24, parent=root)
            for i in range(spokes):
                a = TAU * i / spokes
                rr = (r * 0.3 + r - 0.045) / 2
                box((rr * math.cos(a), rr * math.sin(a), 0), (r - 0.045 - r * 0.3 + 0.02, r * 0.22, h * 0.7),
                    spoke_mat, rz=a, bevel=0.006, parent=root)
            cyl((0, 0, h / 2 + 0.012), 0.035, 0.03, "bare", verts=6, bevel=0, parent=root)   # the shaft nut
        return root

    P1 = pulley(C1, R1, 5, "yellow", "yellow", 0.07)
    P2 = pulley(C2, R2, 3, "dark_steel", "yellow", 0.06)
    # an open flat belt: tangents of the two rims, the big arc on the far side of C1
    rb1, rb2 = R1 + 0.018, R2 + 0.018
    dv = C2 - C1
    dist, phi = dv.length, math.atan2(dv.y, dv.x)
    beta = math.acos((rb1 - rb2) / dist)
    pts = []

    def arc(c, r, a0, a1, n):
        for k in range(n):
            a = a0 + (a1 - a0) * k / n
            pts.append(Vector((c.x + r * math.cos(a), c.y + r * math.sin(a), ZB)))

    def line(p_, q, n):
        for k in range(n):
            pts.append(p_.lerp(q, k / n))

    def pc(c, r, a):
        return Vector((c.x + r * math.cos(a), c.y + r * math.sin(a), ZB))
    line(pc(C1, rb1, phi + beta), pc(C2, rb2, phi + beta), 40)
    arc(C2, rb2, phi + beta, phi - beta, 40)
    line(pc(C2, rb2, phi - beta), pc(C1, rb1, phi - beta), 40)
    arc(C1, rb1, phi - beta, phi + beta - TAU, 120)
    seglen = [(pts[(i + 1) % len(pts)] - pts[i]).length for i in range(len(pts))]
    LB = sum(seglen)
    # the belt: a flat strip, 0.055 tall, 0.02 thick (it stands still: the plate's)
    me = bpy.data.meshes.new("belt")
    bm = bmesh.new()
    rings = []
    for i, p_ in enumerate(pts):
        tng = (pts[(i + 1) % len(pts)] - pts[i - 1]).normalized()
        nrm = Vector((tng.y, -tng.x, 0))
        rings.append([bm.verts.new(p_ + nrm * sx_ + Vector((0, 0, sz_))) for sx_, sz_ in
                      ((-0.01, -0.028), (0.01, -0.028), (0.01, 0.028), (-0.01, 0.028))])
    for i in range(len(rings)):
        a_, b_ = rings[i], rings[(i + 1) % len(rings)]
        for k in range(4):
            j = (k + 1) % 4
            bm.faces.new((a_[k], a_[j], b_[j], b_[k]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    belt = bpy.data.objects.new("belt", me)
    sc.collection.objects.link(belt)
    _finish(belt, "hose_k", 0, smooth=True)
    travel = R1 * TAU * 2 / 5               # belt travel a loop: the big pulley turns two spoke steps
    nclip = max(2, round(LB / travel))
    with grp("drive"):
        clips = [box((0, 0, 0), (0.05, 0.026, 0.062), "bare", bevel=0.004) for _ in range(nclip)]
    cum = [0.0]
    for s_ in seglen:
        cum.append(cum[-1] + s_)

    def at_s(s_):
        s_ %= LB
        lo, hi = 0, len(pts)
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if cum[mid] <= s_:
                lo = mid
            else:
                hi = mid
        a_, b_ = pts[lo], pts[(lo + 1) % len(pts)]
        u = (s_ - cum[lo]) / max(seglen[lo], 1e-9)
        return a_.lerp(b_, u), (b_ - a_).normalized()

    m1, m2 = P1.matrix_basis.copy(), P2.matrix_basis.copy()

    def pose_drive(t):
        P1.matrix_basis = m1 @ Matrix.Rotation(-TAU * 2 / 5 * t, 4, "Z")
        P2.matrix_basis = m2 @ Matrix.Rotation(-travel / R2 * t, 4, "Z")
        for i, c in enumerate(clips):
            p_, tg = at_s(LB * (i / nclip + t / nclip))
            c.location = p_
            c.rotation_euler = (0, 0, math.atan2(tg.y, tg.x))
    DRIVE.update(pose=pose_drive, belt=LB, clips=nclip, small_turns=travel / R2 / TAU, P1=P1, P2=P2)


DRIP = {}


def drip():
    """The vent condenser's drip: a brass plug-cock on its south-east flank, inside the
    footprint (the clip fixes: on the east flank it reached 0.1 tile past the edge), turned
    down over a glossy wet patch; condensate beads running down the copper between the
    bands, and two drops a loop falling from the cock's lip. No steam (spec 3.1)."""
    da, reach = -0.75, 0.11
    dp = Vector((TX + TR * math.cos(da), TY + TR * math.sin(da), 0.0))
    out = Vector((math.cos(da), math.sin(da), 0))
    z_cock = 1.0
    k_ = reach / 0.14
    cyl(tuple(dp + out * 0.06 * k_ + Vector((0, 0, z_cock))), 0.03, 0.14 * k_, "copper", rot=along(out), verts=16)
    cyl(tuple(dp + out * 0.1 * k_ + Vector((0, 0, z_cock + 0.035))), 0.025, 0.05, "brass", verts=6, bevel=0)
    tip = dp + out * reach
    cyl(tuple(tip + Vector((0, 0, z_cock - 0.05))), 0.028, 0.1, "copper", verts=16)
    lip = tip + Vector((0, 0, z_cock - 0.1))
    bpy.ops.mesh.primitive_circle_add(vertices=24, radius=0.05, fill_type="NGON", location=(lip.x, lip.y, 0.003))
    wp = bpy.context.active_object
    wp.scale = (1.0, 1.3, 1)
    _finish(wp, "wet", 0)
    with grp("drip"):
        # two drops a loop, each falling the 0.9 tile from the lip to the ground in 6 frames of 24
        drops = [sphere((0, 0, 0), 0.018, "water", scale=(1, 1, 1.4), seg=10) for _ in range(2)]
        # four beads, each starting under the upper band's lower edge and stopping above the lower
        # band, 0.1 tile round the flank from the cock and the rivets
        beads = [(sphere((0, 0, 0), 0.015, "water", scale=(1, 1, 1.6), seg=10), a, z0, z1, ph)
                 for a, z0, z1, ph in ((-0.4, 1.28, 0.86, 0.0), (-0.05, 1.27, 0.95, 0.5), (0.25, 1.26, 0.84, 0.25),
                                       (-1.3, 1.25, 0.88, 0.7))]

    def pose_drip(t):
        for j, o in enumerate(drops):
            u = round(t * 24 - j * 12) % 24     # frames since this drop let go
            if 0 < u <= 6 and t:
                s_ = (u / 6) ** 2
                o.location = (lip.x, lip.y, (lip.z - 0.02) * (1 - s_) + 0.01)
                o.hide_render = False
            elif u == 0 or u > 22 or not t:     # swelling on the lip
                o.location = (lip.x, lip.y, lip.z - 0.024)
                o.hide_render = j != 0
            else:
                o.hide_render = True
        for o, a, z0, z1, ph in beads:
            u = (ph + t) % 1.0
            z = z0 + (z1 - z0) * (u ** 1.3)
            rr = TR + 0.008
            o.location = (TX + rr * math.cos(a), TY + rr * math.sin(a), z)
    DRIP.update(pose=pose_drip, drops=drops, beads=[b[0] for b in beads], lip=lip)


# every kit call builds one assembly (the collide check's classifier)
for _fn in ("vtank", "drum_ns", "drum_ew", "exchanger", "pump", "valve", "ladder", "hose", "lagged", "pipe",
            "bundle", "handwheel", "band", "vessel_band", "flange_ring", "gauge", "insp_plate", "rivet_column",
            "id_panel", "hazard_tag", "manway_top", "skid", "status_lamp", "flat_plate", "weld_ring", "weld_ring_x",
            "weld_ring_y", "coupling", "arc_panel"):
    globals()[_fn] = kit(globals()[_fn])


with icon_parts():
    reactor()
    legs()
north()
west()
south()
east()
details()
with icon_parts():
    drive()
drip()

# ---------------------------------------------------------------- the fittings, in every direction
#
# The connections, as the plant faces north (prototype tiles, y down; spec 8): the two inputs
# on the north face at -1 and +1, the output on the south face at 0. They turn with the
# building. Each direction gets its own three fittings, built for the face each connection
# lands on as turned -- on the vanilla pipe's centreline there (a vertical pipe's axis 0.5 px
# right of its tile's centre; a horizontal pipe's 1 px above it, which a stub standing ZA
# high reaches by sitting ZA/2 south of it), as the signed-off pipe pictures were -- and is
# then turned back into the model, so that the turntable lands it where it was built. A
# direction's fittings are drawn in that direction only (DIRONLY). What each is, by the face
# it lands on (the signed-off pictures' stubs, less the backplates the engine's pictures
# needed to land on any wall; the vanilla pipe now joins the fitting itself):
#   S  the wall flange, the stub out to where the vanilla pipe's end ring lands, its bolted
#      end ring and the open bore (round 5's south picture's stub)
#   N  a short neck to the edge and its bolted end ring; the vanilla pipe is drawn under it
#   E, W  the neck out of the wall to the edge, its end ring and nuts, seen edge-on
# Every one comes out of the wall the connection's middle tile meets: the north header (the
# exchanger) for the inputs, the filtrate receiver's flank for the output.
VANILLA = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/assembling-machine-3")
H_AXIS_V = 1.0 / 64          # horizontal pipe: axis, screen tiles above its tile's centre
V_AXIS_U = 0.5 / 64          # vertical pipe: axis, screen tiles right of its tile's centre
H_RING_R = 26 / 64 / 1.118
V_RING_R = 25.5 / 64
ZA = 0.42                    # the stubs' axis height, as the drill's
E5 = 2.495                   # the wall's face: the footprint edge, less a hair
NECK0 = 2.18                 # where a neck starts, inside the wall it leaves (the header, the receiver)
CONNS = (((-1, -2), "N"), ((1, -2), "N"), ((0, 2), "S"))
FACE_ORDER = "NESW"
DIRONLY = {}                 # object name -> the one direction it is drawn in
CUR_DIR = [None]
FITTINGS = {}                # direction -> [(tile, face, [objects])], as turned
SOCKETS = {}                 # direction -> the socket's centre, model space, and the candidate it is


def turned(tile, face, deg):
    """A connection turned deg clockwise with the building (prototype tiles, y down)."""
    x, y = tile
    for _ in range(deg // 90):
        x, y = -y, x
    return (x, y), FACE_ORDER[(FACE_ORDER.index(face) + deg // 90) % 4]


def rivet(loc, r=0.017):
    return sphere(loc, r, "bolt", scale=(1, 1, 0.7), seg=8)


def nut(loc, r, h, rot):
    o = cyl(loc, r, h, "bare", rot=rot, verts=6, bevel=0)
    o.rotation_euler.rotate_axis("Z", random.uniform(0, PI / 3))
    return o


def fitting(face, tile):
    """One fitting, built as the building stands turned: x east, y north, the connection's
    `tile` (prototype, y down) on `face` of the footprint as it stands."""
    cx, cy = tile[0], -tile[1]
    if face in "NS":
        sgn = -1 if face == "S" else 1
        x = cx + V_AXIS_U
        ax = (PI / 2, 0, 0)
        if face == "S":
            yw = -(E5 + 0.035)
            ye = -2.53 - ZA / 2              # the end ring widest 0.47 above the outside tile's centre
            pipe([(x, -NECK0, ZA), (x, yw + 0.02, ZA)], r=0.27, mat="bare")      # out of the wall
            annulus((x, yw - 0.03, ZA), 0.3, 0.42, 0.05, "bare", rot=ax)        # wall flange
            for k in range(14):
                t = 2 * PI * k / 14
                rivet((x + 0.37 * math.cos(t), yw - 0.06, ZA + 0.37 * math.sin(t)), 0.016)
            cyl((x, (yw + ye) / 2, ZA), 0.28, abs(ye - yw), "bare", rot=ax, verts=48, bevel=0.0)
            cyl((x, ye + 0.03, ZA), V_RING_R - 0.02, 0.06, "bare", rot=ax, verts=48, bevel=0.01)
            for k in range(8):
                t = 2 * PI * (k + 0.5) / 8
                nut((x + 0.33 * math.cos(t), ye - 0.002, ZA + 0.33 * math.sin(t)), 0.02, 0.014, ax)
            cyl((x, ye - 0.003, ZA), 0.2, 0.006, "dark", rot=ax, verts=32, bevel=0.0)
        else:
            yr = E5 - 0.025                  # the end ring's centre: its outer face on the edge
            pipe([(x, NECK0, ZA), (x, yr - 0.02, ZA)], r=0.27, mat="bare")
            cyl((x, yr, ZA), V_RING_R - 0.02, 0.05, "bare", rot=ax, verts=48, bevel=0.01)
            for k in range(8):
                t = 2 * PI * (k + 0.5) / 8
                nut((x + 0.33 * math.cos(t), yr - 0.032, ZA + 0.33 * math.sin(t)), 0.02, 0.014, ax)
    else:
        sgn = 1 if face == "E" else -1
        ya = cy + H_AXIS_V - ZA / 2
        ax = (0, PI / 2, 0)
        xf = sgn * (2.5 - 0.03)
        pipe([(sgn * NECK0, ya, ZA), (xf - sgn * 0.01, ya, ZA)], r=0.24, mat="bare")          # neck
        cyl((xf, ya, ZA), H_RING_R - 0.02, 0.045, "bare", rot=ax, verts=48, bevel=0.006)
        for k in range(8):
            t = 2 * PI * (k + 0.5) / 8
            nut((xf - sgn * 0.025, ya + 0.27 * math.cos(t), ZA + 0.27 * math.sin(t)), 0.018, 0.012, ax)


def for_direction(d, deg, build):
    """Build parts for direction d as the building stands turned deg, then turn them back into
    the model (the turntable turns them -deg again), drawn in d alone."""
    first, a0 = len(OBJS), _NEXT[0]
    build()
    R = Matrix.Rotation(math.radians(deg), 4, "Z")
    for o in OBJS[first:]:
        o.matrix_basis = R @ o.matrix_basis
        DIRONLY[o.name] = d
    R3 = R.to_3x3()
    for k in range(a0 + 1, _NEXT[0] + 1):
        if k in RUN_ENDS:
            RUN_ENDS[k] = tuple(R3 @ Vector(p_) for p_ in RUN_ENDS[k])
    return OBJS[first:]


random.seed(4)
for _d, _deg in contract.DIRECTIONS["four"]:
    FITTINGS[_d] = []
    for _tile, _face in CONNS:
        _t, _f = turned(_tile, _face, _deg)

        def _b(_t=_t, _f=_f):
            with asm():
                fitting(_f, _t)
        FITTINGS[_d].append((_t, _f, for_direction(_d, _deg, _b)))


# ---------------------------------------------------------------- the leads: each input to where it is used
# Both inputs meet the north header (the exchanger, which spans tiles -1 to +1 on the north
# wall); each leaves it again from its crown straight over its fitting, so the line reads
# through it. Under sae-radiant-precipitation the west box takes the solution and the east the
# gas (spec 8.4): the west line drops into the feed drum's crown, the east line into the
# crust-gas compressor's barrel. Plain bare steel, no marking ring: no marking names a fluid.
def leads():
    for x in (-1.0, 1.0):
        cyl((x, 2.14, 0.7), 0.1, 0.1, "bare", verts=24)                 # the crown branch
        flange_ring(x, 2.14, 0.75, 0.1, mat="bare", h=0.035, nb=6)
    with asm():
        pipe([(-1.0, 2.14, 0.72), (-1.0, 2.06, 0.97), (-1.3, 1.45, 1.1), (-1.7, 1.0, 1.2), (-1.93, 0.8, 1.04)],
             r=0.075, mat="bare")
        cyl((-1.93, 0.8, 1.1), 0.11, 0.04, "dark_steel", verts=24)         # its flange on the drum's crown
    with asm():
        pipe([(1.0, 2.14, 0.72), (1.0, 2.04, 0.97), (0.75, 1.75, 1.02), (0.42, 1.55, 0.86), (0.3, 1.45, 0.58)],
             r=0.075, mat="bare")


leads()


# ---------------------------------------------------------------- the circuit connector sockets
# One per direction, at the candidate spot (T02b's shots, evidence/rp-wiring-t02b/figures/
# connector-candidates.png) that faces the camera as the building stands: a small terminal
# box with its backing plate on the wall that faces south on the screen, and its cable run
# down into the unit. The engine draws its own connector sprite over it (circuit_connector,
# one per direction, at the socket's screen position: SOCKETS, printed by every run).
#   north, east: the instrument house (candidate 2, (2.05, 0.95) facing north): its south
#                face, then (turned east) its east face
#   south, west: the scrubber's foot (candidate 3, (-2.0, -1.85) facing north): its north
#                wall, then (turned west) its west wall
SOCKET_AT = {   # direction: (centre, the wall's outward normal, candidate), model space
    "north": ((2.1, -1.47, 0.78), (0, -1, 0), 2),
    "east": ((2.47, -0.95, 0.78), (1, 0, 0), 2),
    "south": ((-2.0, 2.385, 1.25), (0, 1, 0), 3),
    "west": ((-2.455, 1.85, 1.25), (-1, 0, 0), 3),
}


def socket(c, n):
    c, n = Vector(c), Vector(n)
    side = Vector((-n.y, n.x, 0))
    sz = lambda a, b, h: (abs(side.x) * a + abs(n.x) * b, abs(side.y) * a + abs(n.y) * b, h)
    box(tuple(c - n * 0.028), sz(0.15, 0.012, 0.15), "dark_steel", bevel=0.003)       # backing plate
    box(tuple(c), sz(0.12, 0.055, 0.12), "grey", bevel=0.008)                         # terminal box
    for s_ in (-1, 1):
        for z_ in (-1, 1):
            cyl(tuple(c - n * 0.02 + side * 0.065 * s_ + Vector((0, 0, 0.065 * z_))), 0.009, 0.012, "bolt",
                rot=along(n), verts=6, bevel=0)
    cyl(tuple(c + n * 0.03), 0.03, 0.01, "dark", rot=along(n), verts=12, bevel=0)      # its gland
    hose([tuple(c - Vector((0, 0, 0.07)) + n * 0.005), tuple(c - Vector((0, 0, 0.3)) + n * 0.01),
          tuple(c - Vector((0, 0, c.z - 0.12)) - n * 0.0)], r=0.018, mat="cable_black")


for _d, (_c, _n, _k) in SOCKET_AT.items():
    first = len(OBJS)
    with asm():
        socket(_c, _n)
    for o in OBJS[first:]:
        DIRONLY[o.name] = _d
    SOCKETS[_d] = dict(centre=_c, candidate=_k)


# ---------------------------------------------------------------- lights
SUN = rig.sun(SUN_E)
SUN.data.color = (1.0, 0.94, 0.82)     # a warm white: vanilla's highlights are cream (round 5)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.24

LAYERS = ("drive",) + COUPLINGS + ("press",) + GAUGES + ("drip",)    # the animation's moving parts: not in the plate
STILL_GROUPS = ("body", "legs", "lens") + LAYERS
SHOW = {}                     # object name -> drawn this frame (the cake, the drops): set by the poses


def members(*groups):
    return [o for o in OBJS if PART[o.name] in groups]


# ---------------------------------------------------------------- the poses
def set_legs(t):
    for p_ in LEG_POSES:
        p_(t)
    for node, k in PHASES:
        node.outputs[0].default_value = TAU * k * t


def set_couplings(t):
    for p_ in CPL_POSES:
        p_(t)


PACK_M0 = [(o, o.matrix_basis.copy()) for o in PACK]
CAKE_M0 = CAKE[0].matrix_basis.copy()


def set_press(k):
    """Press frame k: the pack backed off west by STROKE * PRESS_OPEN[k] (PRESS_PATH), the
    cake peeling off the last leaf and falling into the chute mouth."""
    dx = STROKE * PRESS_OPEN[k]
    T = Matrix.Translation((-dx, 0, 0))
    for o, m0 in PACK_M0:
        o.matrix_basis = T @ m0
    fall = PRESS_FALL[k]
    SHOW[CAKE[0].name] = fall is not None
    if fall is not None:
        pivot = Vector((LAST_LEAF_E, PRESS[2], CAKE_Z0))
        Rm = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(PRESS_TILT[k]), 4, "Y") @ \
            Matrix.Translation(-pivot)
        CAKE[0].matrix_basis = Matrix.Translation((-dx, 0, -fall)) @ Rm @ CAKE_M0


def needle_angle(t, i):
    """Degrees; 0 at t = 0, seamless over the loop: a slow swell, a flutter, two flicks."""
    a = 9 * math.sin(TAU * t) + 6 * math.sin(TAU * 3 * t) * math.cos(TAU * (i * 0.17))
    a += 5 * math.sin(TAU * 7 * t) * (0.6 + 0.4 * math.sin(TAU * t + i))
    return a * (1.0 if i % 2 == 0 else -0.8)


def set_gauges(t):
    for o, m0, loc, ax, i in NEEDLES:
        a = math.radians(needle_angle(t, i)) if t else 0.0
        o.matrix_basis = Matrix.Translation(loc) @ Matrix.Rotation(a, 4, ax) @ Matrix.Translation(-loc) @ m0


def set_drip(t):
    DRIP["pose"](t)
    for o in DRIP["drops"]:
        SHOW[o.name] = not o.hide_render       # pose_drip hides a drop between falls


def pose(f, k=0):
    """Frame f of the 24-frame loops (legs, drive, couplings, gauges, drip) and press frame k."""
    t = (f % NF) / NF
    set_legs(t)
    set_couplings(t)
    DRIVE["pose"](t)
    set_gauges(t)
    set_drip(t)
    set_press(k)


def working(on):
    """The legs lit (crafting) or a still dark navy (idle)."""
    for sock, v in GLOWS:
        sock.default_value = v if on else 0.0


def flat_glow(on):
    """The glow pass: the legs lit at one strength (spec 6.1), the solution's pattern
    flattened to its middle colour and the bubbles left dark, so the glow is the same in
    every frame of the legs and needs no animation of its own."""
    for nt, col, b in FLUIDS:
        for l_ in list(nt.links):
            if l_.to_socket == b.inputs["Emission Color"]:
                nt.links.remove(l_)
        if on:
            b.inputs["Emission Color"].default_value = rig.srgb("#1A58E8")   # a step under #1F63FF
            b.inputs["Emission Strength"].default_value = GLOW * 0.8         # and under the pattern's crests:
            # at full strength the glass's highlights clipped to white (pack.py's legs-glow_white_px 4-5)
        else:
            nt.links.new(col, b.inputs["Emission Color"])
    M["bubble"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = \
        0.0 if on else GLOW * 1.3
    # the lit glass is not mirrored in the dials and bands round it either: their faint blue
    # glints sat on white paint and clipped (pack.py's white check)
    for o in members("legs"):
        if o.data.materials and o.data.materials[0].name == "glass":
            o.visible_glossy = not on


def setup(visible=(), catchers=(), holdouts=(), ground=False, unseen=()):
    """Per pass: which groups the camera sees, catch shadow on, or cut out; `unseen` groups are
    in the scene (they cast their shadows and are reflected) but the camera does not see them."""
    for o in OBJS:
        g = PART[o.name]
        shown = (g in visible or g in catchers or g in holdouts or g in unseen) and SHOW.get(o.name, True) \
            and DIRONLY.get(o.name, CUR_DIR[0]) == CUR_DIR[0]
        o.hide_render = not shown
        o.is_shadow_catcher = g in catchers
        o.is_holdout = g in holdouts
        o.visible_camera = g not in unseen
    GROUND.hide_render = not ground
    BOUNCE.hide_render = ground


# ---------------------------------------------------------------- --collide
def collide_check():
    """Every moving part in every frame of every layer (the 24 loop frames, the press's 16
    in frames 0-15) against every fixed part shown that frame and every other layer's
    moving parts; then the fixed model, part against part. A clash is two parts' faces
    crossing, or one wholly inside a closed other. MEANT lists the contacts that are the
    design: a part seated on, in or against what it is fastened to."""
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
        da, db = DIRONLY.get(a.o.name), DIRONLY.get(b.o.name)
        if da and db and da != db:
            return None                 # two directions' own parts are never drawn together
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
    states = [(f, f if f < PRESS_NF else 0) for f in range(NF)]
    m0, moving = {}, set()
    for f, k in states:
        pose(f, k)
        bpy.context.view_layer.update()
        for o in meshes:
            m = o.matrix_world.copy()
            if o.name not in m0:
                m0[o.name] = m
            elif any(abs(m[i][j] - m0[o.name][i][j]) > 1e-6 for i in range(4) for j in range(4)):
                moving.add(o.name)
    moving |= {CAKE[0].name} | {o.name for o in DRIP["drops"]}

    def label(o):
        g = PART[o.name]
        if g == "legs":
            return "leg particle"
        if g == "press":
            return "press pack" if o in PACK else "cake"
        if g == "drive":
            return "drive"
        if g == "drip":
            return "drip"
        return g

    def meant(g, ad, bd):
        for gr, ar, br, why in MEANT:
            if re.search(gr, g) and re.search(ar, ad) and re.search(br, bd):
                return why
        return None

    out(f"COLLIDE {len(meshes)} parts, {len(moving)} moving; frames: the 24 loop frames, press frames 0-15 in 0-15")
    fixed_cache, hits = {}, {}
    for f, k in states:
        pose(f, k)
        bpy.context.view_layer.update()
        live = [o for o in meshes if SHOW.get(o.name, True)]
        mv = [o for o in live if o.name in moving]
        fx = [o for o in live if o.name not in moving]
        for o in fx:
            if o.name not in fixed_cache:
                fixed_cache[o.name] = Part(o)
        mparts = [(label(o), Part(o)) for o in mv]
        for lab, a in mparts:
            for o in fx:
                b = fixed_cache[o.name]
                kind = clash(a, b)
                if kind:
                    hits.setdefault((lab, a.desc if lab != "leg particle" else "particle", b.desc, kind),
                                    []).append(f)
        for i, (la, a) in enumerate(mparts):
            for lb, b in mparts[i + 1:]:
                if la == lb:
                    continue
                kind = clash(a, b)
                if kind:
                    hits.setdefault((la, a.desc, lb + ": " + b.desc, kind), []).append(f)
    n_meant = n_clash = 0
    for (g, ad, bd, kind), fs in sorted(hits.items(), key=lambda kv: kv[0]):
        why = meant(g, ad, bd)
        n_meant += bool(why)
        n_clash += not why
        fr = f"{fs[0]}-{fs[-1]}" if fs == list(range(fs[0], fs[-1] + 1)) else ",".join(map(str, fs))
        out(f"COLLIDE {'meant' if why else 'CLASH'} moving [{g}] {ad} x {bd}: {kind}, frames {fr}" +
            (f"  ({why})" if why else ""))
    out(f"COLLIDE moving: {n_clash} clashes, {n_meant} meant contacts")

    # the fixed model, part against part, at frame 0
    pose(0)
    bpy.context.view_layer.update()
    fixed = [fixed_cache[o.name] for o in meshes if o.name in fixed_cache]
    def depth(a, b):
        """How far a's vertices reach inside b (tiles, model space): the deepest one's distance
        to b's surface. A band round its vessel or a part set on a face reaches ~0; a part
        sunk into another reaches its own depth."""
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
            if tag == "REAL":                  # a pair line measure.py's collide gates (no allow names it)
                out(f"COLLIDE REAL fixed {a.desc} x {b.desc}: {kind}, {dp:.3f} deep")
    order = {"REAL": 0, "touch": 1, "seated": 2}
    with open(os.path.join(OUT, "collide-model.txt"), "w") as f_:
        f_.write("\n".join(l_ for _, _, l_ in sorted(pairs, key=lambda p_: (order[p_[0]], p_[1], p_[2]))) + "\n")
    out(f"COLLIDE model: {n_real} clashes (REAL: reach more than {DEEP} tile into each other and no rule "
        f"explains them), {len(fixed)} fixed parts, {len(pairs)} touching pairs, {n_deep} touch at under "
        f"{DEEP} (collide-model.txt)")
    with open(os.path.join(OUT, "collide.txt"), "w") as f_:
        f_.write("\n".join(lines) + "\n")


# (group, this part, the other part: regexes on "name[material] at (x,y,z)", why): contacts that
# are the design. Every other crossing by a moving part is a CLASH. Tiles, model space.
_C = rf"\(\+{TX:.2f},\+{TY:.2f}"                 # the vent condenser's shell, foot ring and bands
MEANT = [
    (r"^gauge-", "", r"\[(brass|gauge)\]", "a needle on its own dial"),
    (r"^drip$", r"\[water\]", r"Cylinder\.\d+\[copper\] at " + _C, "a bead running on the condenser's wall"),
    (r"^drip$", "", r"\[wet\]", "a drop landing in its wet patch"),
    (r"^drip$", "", r"\[(copper|brass)\] at \(\+2\.[234]", "a drop swelling on the cock's lip"),
    (r"^drive$", "", r"^belt\[", "a lacing clip on the belt"),
    (r"^drive$", "", rf"\[bare\] at \(\+({C1.x:.2f}|{C2.x:.2f})", "a pulley on its shaft"),
    (r"^leg particle$", "", r"\[(glass|fl_f\d)\]", "a fleck or bubble in the solution, inside the glass"),
    (r"^leg particle$", "", r"\[bare\] at \((-0\.32,\+0\.62|\+0\.12,-0\.72),1\.43\)",
     "inside the glass, behind the leg's middle band"),
    (r"^leg particle$", "", r"\[(bare|brass|hose|hose_k)\] at \((-0\.5|-0\.6|\+0\.2|\+0\.5)",
     "inside the glass, past the end of a hose let into the leg (round 5)"),
    (r"^press pack$", "", r"\[bare\] at \(-1\.\d+,-(2\.28|1\.68),1\.18\)", "the leaves and tail stand riding on the rails"),
    (r"^press pack$", "", r"\[dark_steel\] at \(-0\.72,-1\.98", "the last leaf shut against the head"),
    (r"^press pack$", "", r"^cake: ", "the cake on the leaf it peels off"),
    (r"^cake$", "", r"\[cream\] at \(-(0\.[89]|1\.0)", "the cake on the leaf it peels off"),
    (r"^cake$", "", r"\[(lead|dark_steel|dark)\] at \(-(1\.0[256]|0\.89),-1\.98,0\.(27|56|58)",
     "the cake dropping through the chute mouth into the drop box"),
]

# Fixed parts that touch by design: a fastener or a fitting (small, or one of the detail
# materials) on what carries it; a hose or pipe let into its vessel; a vessel on its skid,
# saddle or foot ring. collide-model.txt lists every pair; the ones none of these explain are
# REAL, and FIXES says what became of each.
DEEP = 0.03                                    # tiles: 2 px at the sprite's scale; less is two faces meeting
DETAIL_MATS = {"bolt", "seam", "stencil", "hazard", "label", "gauge", "needle", "red", "yellow", "brass", "dark",
               "lamp", "wet", "oil"}


# Fixed contacts that are the design but no rule above can tell: (this part, the other, why).
MEANT_FIXED = [
    (r"^Cylinder\[dark_steel\] at \(\+1\.30,\+0\.10,0\.08\)", rf"\[dark_steel\] at \(\+{PX:.2f},\+{PY:.2f},0\.07\)",
     "the side nozzle's pot stands on the reactor's foot ring: the two cast feet run together"),
    (r"^Cylinder\.\d+\[dark_steel\] at \(\+0\.07,-1\.32,0\.32\)", r"\[dark_steel\] at \([-+]0\.\d+,-1\.32,0\.40\)",
     "a valve's body standing on the sampling manifold"),
]


def seated(a, b, inside_pts):
    """Why two touching fixed parts are meant to touch, or None. inside_pts(x, y): x's vertices
    inside y, in model space."""
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
            if pts and all(min((p_ - ends[0]).length, (p_ - ends[1]).length) < 0.6 for p_ in pts):
                return "a hose or pipe's end let into what it serves"
    for x, y in ((a, b), (b, a)):
        if x.o.name in HEADS and y.lo.z > x.lo.z - 0.01 and y.size < 0.5 and \
                (Vector((y.c.x, y.c.y)) - Vector((x.c.x, x.c.y))).length < max(x.hi.x - x.lo.x, x.hi.y - x.lo.y) / 2:
            return "a fitting standing in its vessel's head"
    return None


# ---------------------------------------------------------------- the cut and the windows
def cut_to_footprint(path):
    """Clear every pixel of a colour render outside the footprint's east and west edges
    (+-2.5 tiles): the plate is exactly 5.000 tiles wide (spec 8.6). Returns how many
    pixels with any alpha were cleared; the model keeps nothing past the edge, so 0."""
    import numpy as np
    img = bpy.data.images.load(path)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)
    k = w // CANVAS[0]                       # the supersampling
    x0 = (CANVAS[0] // 2 - 160) * k
    x1 = (CANVAS[0] // 2 + 160) * k
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


CUT = {}


def over_black(path):
    """The glow pass's render flattened onto black: its colour is the light it carries and
    nothing else. Held out, the rest of the machine is transparent, and the anti-aliased rims
    of the holdouts (alpha 1 or 2) unpremultiply to white specks, which pack.py's glow takes
    as clipped light. pack.py reads only this pass's colour (lit minus the plate)."""
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


def render(path, cut=True):
    rig.render(path)
    if cut:
        CUT[os.path.basename(path)] = cut_to_footprint(path)


def window(objs, poses, pad=(0.35, 0.35, 0.7, 0.45)):
    """The render border (sprite px, x0, y0, x1, y1 from the canvas's top left) round objs
    over every pose: their projection, padded (left, down, right, up, in tiles) for the
    shadows they cast (the sun throws them right and up the screen)."""
    cam = sc.camera
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for ps in poses:
        ps()
        bpy.context.view_layer.update()
        for o in objs:
            if o.type != "MESH":
                continue
            ev = o.evaluated_get(dg)
            for c in ev.bound_box:
                p_ = inv @ (ev.matrix_world @ Vector(c))
                xs.append(p_.x)
                ys.append(p_.y)
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
    sys.exit("circulator.py (four-way): no pipe pictures -- the fittings are modelled into every "
             "direction's plate; render without --ports")

GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()

# ---------------------------------------------------------------- --icon
if ICON:
    # spec 14: the lead reactor and its two lit legs (with the drive on its head and the
    # loop's hoses and header), on the plate's camera, framed to fill a 1024 px square
    sc.cycles.samples = 128
    cam = rig.camera(1024, 1024, ss=1)
    pose(0)
    working(True)
    for o in OBJS:
        o.hide_render = o.name not in ICON_SET or not SHOW.get(o.name, True)
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
    print(f"icon: {len(ICON_SET)} parts, {span:.2f} tiles across")
    print("done")
    sys.exit(0)

# ---------------------------------------------------------------- the passes, in every direction
rig.camera(*CANVAS)


def path(stem):
    return os.path.join(OUT, stem + ".png")


ALL = ("body", "legs", "lens") + LAYERS
WINDOWS = {}
PROBED = {}
if not IDLE and not PROBE:
    if not RUN_DIR:
        sys.exit("circulator.py (four-way): a full run renders one direction: set RP_DIRECTION")
    contract.declare(OUT, canvas=CANVAS, **DECL)
for D_, _deg in contract.DIRECTIONS["four"]:
    if RUN_DIR and D_ != RUN_DIR:
        continue
    ROOT.rotation_euler.z = -math.radians(_deg)        # contract.each_direction's turn
    CUR_DIR[0] = D_
    bpy.context.view_layer.update()
    seen = tuple(n_ for n_ in LAYERS if n_ not in UNSEEN[D_])
    still_in_plate = tuple(n_ for n_ in LAYERS if n_ in UNSEEN[D_])
    # one run renders one direction: its file names carry none (directions "one"); a look at all
    # four (--idle without RP_DIRECTION) names each
    stem = (lambda x: x) if RUN_DIR else (lambda x: contract.named(x, D_))
    if PROBE:
        # every layer's frame 0 alone, at 8 samples: does the camera see it in this direction?
        import numpy as np
        sc.cycles.samples = 8
        pose(0)
        for name in [n_ for n_ in LAYERS] + ["legs"]:
            others = tuple(g for g in ALL if g != name)
            setup(visible=(name,), holdouts=others)
            fp = path(f"probe-{name}-{D_}")
            rig.render(fp)
            img = bpy.data.images.load(fp)
            a_ = np.empty(img.size[0] * img.size[1] * 4, dtype=np.float32)
            img.pixels.foreach_get(a_)
            PROBED[f"{name}-{D_}"] = int((a_[3::4] > 0.5).sum())
            bpy.data.images.remove(img)
        continue
    pose(0)
    working(False)
    sc.cycles.samples = PLATE_SAMPLES
    # the plate: the machine without the animation's moving parts, which stand in the scene at
    # frame 0 unseen, so their shadows and reflections are the plate's (frame 0 then matches the
    # still by construction); the legs unlit
    setup(visible=("body", "legs", "lens") + still_in_plate, unseen=seen)
    render(path(stem("idle")))
    # the still: the whole machine at frame 0, idle (the reference for the frame-0 check)
    setup(visible=ALL)
    render(path(stem("still")))
    # the glow: the plate's scene, the legs lit at one strength
    working(True)
    flat_glow(True)
    setup(visible=("legs",), holdouts=("body", "lens") + still_in_plate, unseen=seen)
    render(path(stem("working")))
    over_black(path(stem("working")))
    working(False)
    flat_glow(False)
    if IDLE:
        continue
    # the shadow: the whole machine at frame 0 on the ground catcher, seen by nothing else
    setup(visible=ALL, ground=True)
    for o in OBJS:
        o.visible_camera = False
    render(path("shadow"), cut=False)
    # the status lamps' lenses, lit white, everything else held out
    setup(visible=("lens",), holdouts=("body", "legs") + LAYERS)
    lamp_cut(True)
    render(path("lamp"))
    lamp_cut(False)

    # the layers: each its moving parts alone, everything else holding out what it stands in
    # front of, inside its own window
    sc.cycles.samples = ANIM_SAMPLES
    for name in LAYERS:
        if name in HIDDEN:
            continue
        objs = members(name)
        n = PRESS_NF if name == "press" else NF
        poses = [(lambda f=f: pose(0, f)) if name == "press" else (lambda f=f: pose(f)) for f in range(n)]
        win = window(objs, poses)
        WINDOWS[name] = win
        border(win)
        others = tuple(g for g in ALL if g != name)
        for f in range(n):
            pose(0, f) if name == "press" else pose(f)
            setup(visible=(name,), holdouts=others)
            render(path(contract.frame(name, f)))
        no_border()
    # the press's tracked part: the leaf pack and tail stand alone, measured, not packed
    border(WINDOWS["press"])
    for f in range(PRESS_NF):
        pose(0, f)
        setup()
        for o in PACK:
            o.hide_render = False
        render(path(contract.track_frame("press", "pack", f, "")))
    no_border()
    # the legs: lit and moving, drawn only while crafting, over the plate's dark legs
    working(True)
    win = window(members("legs"), [lambda: pose(0)], pad=(0.1, 0.1, 0.1, 0.1))
    WINDOWS["legs"] = win
    border(win)
    for f in range(NF):
        pose(f)
        setup(visible=("legs",), holdouts=("body", "lens") + LAYERS)
        render(path(contract.frame("legs", f)))
    no_border()
    working(False)
    pose(0)
ROOT.rotation_euler.z = 0.0
CUR_DIR[0] = None


def proto(p_, deg):
    """A model-space point in prototype tiles (x right, y down the screen) as the building
    stands turned deg: where the engine draws a sprite shifted by it."""
    x, y, z = p_
    a = -math.radians(deg)
    e, nn = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
    return round(e, 4), round(-(nn + z * math.cos(rig.ELEVATION)), 4), round(e, 4), round(-nn, 4)


SOCKET_REPORT = {}
for _d, _deg in contract.DIRECTIONS["four"]:
    sx_, sy_, gx_, gy_ = proto(SOCKETS[_d]["centre"], _deg)
    SOCKET_REPORT[_d] = dict(candidate=SOCKETS[_d]["candidate"], model=SOCKETS[_d]["centre"],
                             screen_tiles=(sx_, sy_), ground_tiles=(gx_, gy_))
    print(f"socket {_d}: candidate {SOCKETS[_d]['candidate']}, on screen at {sx_:+.3f}, {sy_:+.3f} tiles "
          f"(its ground point {gx_:+.3f}, {gy_:+.3f})")
if PROBE:
    with open(os.path.join(OUT, "probe.json"), "w") as f_:
        import json
        json.dump(PROBED, f_, indent=1)
    print("probe:", PROBED)
    print("done")
    sys.exit(0)
if IDLE:
    print("done")
    sys.exit(0)

with open(os.path.join(OUT, "model.json"), "w") as f_:
    import json
    json.dump(dict(windows=WINDOWS, cut=CUT, press=dict(frames=PRESS_NF, land=PRESS_LAND, stroke=STROKE,
                                                        open=PRESS_OPEN, fall=PRESS_FALL, path=PRESS_PATH),
                   drive=dict(belt=DRIVE["belt"], clips=DRIVE["clips"], small_turns=DRIVE["small_turns"]),
                   samples=dict(plate=PLATE_SAMPLES, anim=ANIM_SAMPLES), groups={g: len(members(g)) for g in ALL},
                   icon_parts=len(ICON_SET), sun=SUN_E, sockets=SOCKET_REPORT,
                   fittings={d: [dict(tile=t, face=f) for t, f, _ in v] for d, v in FITTINGS.items()}), f_, indent=1)
print("cut past the footprint's edges (px with alpha, per render):", {k: v for k, v in CUT.items() if v})
print("done")
