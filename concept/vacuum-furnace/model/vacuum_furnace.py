"""Vacuum furnace (sae-vacuum-furnace), built from its spec, rendered in every pass.

  blender -b --python vacuum_furnace.py -- <out-dir> [--idle | --icon | --ports]
  tools/blender/render.sh concept/vacuum-furnace/model/vacuum_furnace.py <out-dir> [--icon]

  --idle   idle.png and working.png only: the quick loop
  --ports  the four pipe pictures, port-<face>.png, rendered alone on the port canvas;
           pipe_pictures.py (beside this file) cuts them to assembler 3's sheets. Not
           through render.sh --ports: pack_ports.py packs a rendered cover with every
           fitting, and this building's covers are vanilla's (spec 8)

The layout is blockout revision 4, approved by Liam 2026-10-07
(blockout-v4.png, vacuum_furnace_blockout_v4.py); the finish is the first finished
model's (materials.py's layered finish through this building's concept swatches).
Spec: concept/vacuum-furnace/building-spec-vacuum-furnace.md -- 3.2 the parts, 3.3
the palette, 5 four directions and a building that never turns, 6 what moves,
8 the input.

  - a battered octagonal hull filling the footprint: its walls lean back 0.22 over
    1.2, so at the middle of each face the wall reaches the top of the pipe
    picture's plate (0.688 tiles below the origin on screen for the south one);
  - the welded drum (R 1.08), round and on the footprint's centre, its deck level
    with the hull's rail, so the parapet runs round the hatch evenly;
  - the hatch flat in the roof, with its eight dogs; no dome and no lifting eye;
  - the sight port at the hatch's centre, its glass flat in the roof: the only heat
    glow, and the indicator -- its glass, cut white, is the light pass the engine
    tints by status (spec 3.2); there is no separate lamp;
  - three radiator stacks across the corners, in niches cut into the hull: each one
    wide column of oval fins in brass collars between steel posts, on a foot block,
    bulky as the adopted plate draws them (Liam, 2026-10-08);
  - the vacuum pump in the south-east niche: a barrel, a heavy flywheel upright in
    front of it on its drive motor's shaft (the animation: 16 frames through 60 degrees, its six-fold
    symmetry), free all round, and a vacuum gauge flat on the barrel's head, its dull
    dial recessed in a hood and bare -- the needle is Animatorio's (spec 6);
  - a copper ring on the deck round the hatch, and each stack's loop teed off it in
    heavy steel pipe (#6E685C, spec 3.3), flanged and bolted to nozzles on the
    stack's collars, none crossing a face's middle;
  - no base and no socket: the input is the engine's pipe picture, rendered here
    to assembler 3's outline exactly (a backing slab traced from its pixels), in
    the furnace's metal, and vanilla's cover;
  - no frost anywhere (Liam, 2026-10-02);
  - made up, so no surface is a bare band (Liam, 2026-10-08): the cap rail kerbed,
    mitre-welded and bolted all round, the drum's lid bolted down, the walls in
    plates with bolted stiffeners and bolt rows, a brass maker's plate on the south
    face, a faded warning ring on the hatch under the dogs; rust run down from the
    rail and the girth weld, and grime rising from the ground (materials.py's
    drips and ground);
  - and in finer detail (Liam, 2026-10-08): the hatch's plate welded from six
    segments, the dogs' wear polished into the warning ring, each wall plate its
    own object and so its own tone, angle iron worn bare down every corner,
    verdigris on the copper, a valve on the suction line, the gauge's line into the
    hull, and a power feed -- the drive motor's starter box on the south-east
    chamfer, leaning with it, and a conduit down to the motor;
  - the roof's working fittings off its symmetry (Liam, 2026-10-08: the hatch looked
    too perfect): the viewport's cover flung back on its straps behind the glass, a
    vacuum-break valve, a welded repair patch, the dogs each a few degrees off true,
    and the evacuation hose -- ribbed, from a port on the hatch, over the rail,
    clipped down the chamfer into a flanged inlet on the pump.

Roof and clamps: the roof warmed toward the adopted plate's beige (#958577) and the
dogs bronze, as spec 3.3 has them.

Units are tiles; north is +Y. A model point (x, y, z) lands on screen at
(x, y + z/2) tiles from the origin.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))


def swatch(name):
    """This building's concept swatches: swatches/bake_concept.py."""
    return os.path.join(HERE, "swatches", f"concept_{name}.png")


import rig  # noqa: E402
import contract  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = argv[0]
os.makedirs(OUT_DIR, exist_ok=True)
ICON = "--icon" in argv
IDLE = "--idle" in argv
PORTS = "--ports" in argv

FACES = "NESW"
CANVAS = (320, 288)                   # entity origin at (160, 144); the shadow reaches east
PORT_CANVAS = (320, 320)              # the pictures reach a tile outside on every side
DECL = dict(
    footprint=(3, 3),
    directions="one",                 # drawn once; only the input turns (spec 5)
    passes=[
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="still", kind="still"),
        dict(name="working", kind="glow", over="idle", sheet="port-glow"),
        dict(name="shadow", kind="shadow", sheet="base-shadow"),
        dict(name="indicator", kind="light", sheet="viewport-status"),
    ],
    # spec 6: the flywheel turns while working; six spokes, so 60 degrees is a loop
    animations=[dict(name="flywheel", frames=16, motion="turn")],
    # the one input, {0, 1} facing south at rest, and where the engine turns it
    ports=[dict(tile=(0, -1), face="N"), dict(tile=(1, 0), face="E"),
           dict(tile=(0, 1), face="S"), dict(tile=(-1, 0), face="W")],
)

sc = rig.reset()
ROOT = rig.turntable(rig.stretch_root())

# ---------------------------------------------------------------- the hull's shape
# Defined before the materials because the finish places its marks and streaks on
# the hull's faces (the signature finish, below); the hull itself is built in 1.
HZ, E, C, LEAN = 1.2, 1.482, 0.9, 0.22     # the foot band, 0.01 proud, lands at 1.492
CT = C - LEAN * (2 - math.sqrt(2))     # the chamfer leans back by LEAN too, square to it


def octagon(e, c):
    return [(-e, -e + c), (-e + c, -e), (e - c, -e), (e, -e + c), (e, e - c), (e - c, e), (-e + c, e), (-e, e - c)]


def at_lean(z):
    """The hull's half-width, and chamfer, at height z."""
    f = z / HZ
    return E - LEAN * f, C + (CT - C) * f


def wall_pt(i, f, z, out=0.0):
    """On the hull's face i (octagon order, 1 the south face), f along it from its
    west/south end, at height z, stood out from the wall by out."""
    e, c = at_lean(z)
    pts = octagon(e, c)
    (ax, ay), (bx, by) = pts[i], pts[(i + 1) % 8]
    nx, ny = by - ay, -(bx - ax)                  # outward: the octagon runs anticlockwise
    n = math.hypot(nx, ny)
    return (ax + (bx - ax) * f + out * nx / n, ay + (by - ay) * f + out * ny / n, z)


# ---------------------------------------------------------------- materials

from materials import TEX, layered, hazard_pattern  # noqa: E402

# The signature finish (spec 3.3, Liam 2026-10-09): heat-tempered steel. Every Core
# building keeps the shared base -- dark steel, the shared rust, dust and ground dirt,
# all still materials.layered's -- and this one carries the temper colours of steel
# that has been hot. Round 2 (Liam: "could be refined further"): the colours follow
# the heat, visibly. Smooth graded bands, only a slight waver at their edges, in
# temper's fixed sequence away from a source -- blue nearest (the hottest), then
# purple, brown, a thin pale straw, then plain dark steel -- from three sources:
#   the hatch flange   concentric rings out across the drum's top, the deck and the rail;
#   the hull's top     level bands down the upper course, plain by the course line;
#   each radiator      from its inlet at the top collar down, plain by the foot.
# The purple step is what makes it read as temper and not as rust or paint, and the
# straw is thin and pale so it cannot read as a stain or as warm light: the orange
# viewport stays the only warm-bright thing, and nothing here emits.
#
# Rust keeps out of the bands: the dry orange on tops and the wet streaks below the
# fittings only start where the steel is plain again, and the drip from the rail is
# gone; rust and drips are on the cooler, lower and outer metal.
#
# Variation (3.3): two replacement plates, a shade lighter and untempered, so they
# break the bands; one bold stencil on the south face and one on the hatch.
#
# Two strengths for Liam to choose between, by $VF_TEMPER ("subtle" or "bold"; the
# default is TEMPER_DEFAULT): the bands and their order are the same, only their
# strength differs.
#
# All of it goes through layered's `pattern` hook, which takes the place of a swatch:
# so each pattern below starts from this building's own concept swatch, as the
# materials did before, and lays the finish over it. layered then adds its own
# blotch and grain on top (the swatch path skips them); COMP evens out the grain's
# mean so the steel keeps its value.
TEMPER_DEFAULT = "bold"
TEMPER_STRENGTH = {"subtle": 0.6, "bold": 1.0}[os.environ.get("VF_TEMPER", TEMPER_DEFAULT)]
# (hex, from, to, strength) over the heat distance t, 0 at the source, 1 plain steel
TEMPER = (("#3E4A66", 0.00, 0.20, 0.90),    # blue, nearest the heat (spec 3.3)
          ("#5C4A6E", 0.29, 0.42, 0.85),    # purple: between bronze and blue (round 2)
          ("#8A5A3A", 0.51, 0.64, 0.75),    # bronze/brown (spec 3.3)
          ("#B8964A", 0.72, 0.77, 0.32))    # straw (spec 3.3): thin and pale
TEMPER_PLAIN = 0.88
COMP = 1.03
WET = ("#1E140E", "#3A2416")                # rust run wet below a fitting: dark, brown
DRY = ("#8E4A1E", "#B4682E")                # rust dried on a top: orange, powdery
PZ_ = HZ + 0.05                             # the deck and cap rail's top (PZ, in 1.)
RAD_TOP = 1.1                               # the radiator stacks' top collar (RZ1, in 6.)
FLANGE_R = 0.92                             # the hatch flange's rim (R + 0.03, in 2.)
ROOF_SPAN = 0.36                            # from the flange to plain steel, across the roof
WALL_SPAN = 0.62                            # from the hull's top to plain, down the walls
RAD_SPAN = 0.85                             # from the inlet to plain, down a stack


def _geometry(g):
    """The shading point in the model's own units: the rig's STRETCH scales world Y by
    1/sin(elevation) (the projection), so position and normal are taken back through
    it before anything is placed by the model's coordinates."""
    geo = g.node("ShaderNodeNewGeometry")
    k = 1.0 / math.sin(rig.ELEVATION)
    pos = _vmath(g, "MULTIPLY", geo.outputs["Position"], (1.0, 1.0 / k, 1.0))
    nrm = g.n.new("ShaderNodeVectorMath")
    nrm.operation = "NORMALIZE"
    g.l.new(_vmath(g, "MULTIPLY", geo.outputs["Normal"], (1.0, k, 1.0)), nrm.inputs[0])
    nrm = nrm.outputs["Vector"]
    p = g.node("ShaderNodeSeparateXYZ", Vector=pos).outputs
    n = g.node("ShaderNodeSeparateXYZ", Vector=nrm).outputs
    return pos, nrm, (p["X"], p["Y"], p["Z"]), (n["X"], n["Y"], n["Z"])


def _vmath(g, op, a, b):
    nd = g.n.new("ShaderNodeVectorMath")
    nd.operation = op
    for i, v in enumerate((a, b)):
        if isinstance(v, bpy.types.NodeSocket):
            g.l.new(v, nd.inputs[i])
        else:
            nd.inputs[i].default_value = v
    return nd.outputs["Value"] if op == "DOT_PRODUCT" else nd.outputs["Vector"]


def _flat(g, hexcol):
    nd = g.n.new("ShaderNodeRGB")
    nd.outputs[0].default_value = rig.srgb(hexcol)
    return nd.outputs[0]


def _swatch(g, name, gain=1.0):
    pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
    c = g.image(swatch(name), pos, 1.0, data=False).outputs["Color"]
    k = (gain if isinstance(gain, tuple) else (gain,) * 3)
    return g.mulc(c, tuple(v * COMP for v in k) + (1.0,))


def _waver(g, pos, t):
    """Only a slight waver at the bands' edges: one gentle, low-frequency nudge."""
    return g.math("ADD", t, g.math("MULTIPLY", g.math("SUBTRACT", g.noise(pos, 2.2, detail=1), 0.5), 0.07))


def heat_roof(g, pos, x, y):
    """From the hatch flange, outward across the drum's top, the deck and the rail."""
    r = g.math("SQRT", g.math("ADD", g.math("MULTIPLY", x, x), g.math("MULTIPLY", y, y)))
    return _waver(g, pos, g.math("DIVIDE", g.math("MAXIMUM", g.math("SUBTRACT", r, FLANGE_R), 0.0), ROOF_SPAN))


def heat_wall(g, pos, z):
    """From the hull's top, down the upper course: plain by the course line."""
    return _waver(g, pos, g.math("DIVIDE", g.math("MAXIMUM", g.math("SUBTRACT", HZ, z), 0.0), WALL_SPAN))


def heat_hull(g, pos, x, y, z, nz):
    """The roof's rings on what faces up (the deck), the walls' bands on what stands."""
    return g.mixf(g.remap(nz, 0.5, 0.8), heat_wall(g, pos, z), heat_roof(g, pos, x, y))


def heat_radiator(g, pos, z):
    """From the inlet at the top collar (and the hot loop above it), down to the foot."""
    return _waver(g, pos, g.math("DIVIDE", g.math("MAXIMUM", g.math("SUBTRACT", RAD_TOP, z), 0.0), RAD_SPAN))


def cool(g, t):
    """1 where the steel is plain again, 0 in the bands: where rust may be."""
    return g.remap(t, TEMPER_PLAIN - 0.08, TEMPER_PLAIN + 0.05)


def temper(g, col, mean_hex, t, strength=1.0):
    """Lay the temper colours over col by heat distance t, keeping col's grain: each band
    is its hex at col's own relative brightness, mixed in at the band's strength."""
    ramp = g.n.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "EASE"
    els = ramp.color_ramp.elements
    stops = [(p, hx, a) for hx, p0, p1, a in TEMPER for p in (p0, p1)] + [(TEMPER_PLAIN, TEMPER[-1][0], 0.0)]
    els[0].position, els[1].position = stops[0][0], stops[-1][0]
    for p, hx, a in stops[1:-1]:
        els.new(p)
    for e, (p, hx, a) in zip(sorted(els, key=lambda e: e.position), stops):
        e.color = (*rig.srgb(hx)[:3], a)
    g.l.new(t, ramp.inputs["Fac"])
    m = rig.srgb(mean_hex)
    tinted = g.mulc(g.mulc(col, (1 / m[0], 1 / m[1], 1 / m[2], 1.0)), ramp.outputs["Color"])
    return g.mixc(g.math("MULTIPLY", ramp.outputs["Alpha"], strength * TEMPER_STRENGTH, clamp=True), col, tinted)


def face_frame(i, f, z):
    """Face i's frame at (f, z): the point on the wall, the unit vector along it, and
    its outward normal, leaning back with the wall."""
    o = wall_pt(i, f, z)
    a, b = wall_pt(i, 0, z), wall_pt(i, 1, z)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    t = ((b[0] - a[0]) / L, (b[1] - a[1]) / L, 0.0)
    k = math.hypot(HZ, LEAN)
    n = (t[1] * HZ / k, -t[0] * HZ / k, LEAN / k)
    return o, t, n


# The stencils: (mask, centre, the mask's across and up axes, the surface's normal,
# width, height, paint, opacity). Masks are swatches/bake_stencils.py's. On the walls
# the height is in z, which the camera halves (and the lean adds back a little).
# One per face at most, bold enough to read at 2x (round 2).
def _wall_mark(name, i, f, z, w, h, paint, opacity):
    o, t, n = face_frame(i, f, z)
    return (name, o, t, (0.0, 0.0, 1.0), n, w, h, paint, opacity)


def _roof_mark(name, a_deg, r, z, w, h, paint, opacity):
    a = math.radians(a_deg)
    return (name, (r * math.cos(a), r * math.sin(a), z), (-math.sin(a), math.cos(a), 0.0),
            (-math.cos(a), -math.sin(a), 0.0), (0.0, 0.0, 1.0), w, h, paint, opacity)


# the unit's number on the south-east chamfer's upper plate, left of the starter box:
# not the south face, whose upper course the south pipe picture's flange covers at rest
WALL_MARKS = [_wall_mark("07", 2, 0.17, 0.9, 0.28, 0.22, "#CFC7B2", 0.95)]
# on the hatch, in the free segment south-south-east of the viewport, along its ring
HATCH_MARKS = [_roof_mark("vac", 300, 0.44, HZ + 0.05 + 0.09 + 0.03 * math.sqrt(1 - (0.44 / 0.78) ** 2),
                          0.33, 0.13, "#2E2924", 1.0)]


def stencils(g, col, pos, normal, marks):
    """Paint each mark over col, where the surface faces its way and lies in its plane,
    the paint a little broken, as an old stencil's is."""
    for name, o, U, V, N, w, h, paint, opacity in marks:
        rel = _vmath(g, "SUBTRACT", pos, o)
        u = g.math("ADD", g.math("DIVIDE", _vmath(g, "DOT_PRODUCT", rel, U), w), 0.5)
        v = g.math("ADD", g.math("DIVIDE", _vmath(g, "DOT_PRODUCT", rel, V), h), 0.5)
        img = bpy.data.images.load(os.path.join(HERE, "swatches", f"stencil_{name}.png"), check_existing=True)
        img.colorspace_settings.name = "Non-Color"
        tex = g.n.new("ShaderNodeTexImage")
        tex.image, tex.extension, tex.interpolation = img, "CLIP", "Linear"
        g.l.new(g.node("ShaderNodeCombineXYZ", X=u, Y=v).outputs[0], tex.inputs["Vector"])
        facing = g.remap(_vmath(g, "DOT_PRODUCT", normal, N), 0.8, 0.9)
        inplane = g.remap(g.math("ABSOLUTE", _vmath(g, "DOT_PRODUCT", rel, N)), 0.03, 0.015)
        worn = g.remap(g.noise(pos, 45, detail=3), 0.3, 0.5, 0.7, 1.0)
        m = g.math("MULTIPLY", g.math("MULTIPLY", tex.outputs["Color"], g.math("MULTIPLY", facing, inplane)),
                   g.math("MULTIPLY", worn, opacity), clamp=True)
        col = g.mixc(m, col, _flat(g, paint))
    return col


# Wet rust: dark streaks run down the wall below its fittings, (face, f, the
# fitting's foot, width, length); each fitting is where vacuum_furnace builds it.
# They show only where the steel is plain (cool), so below the bands.
WET_UNDER = [
    (1, 0.27, 0.74, 0.17, 0.4),         # the maker's plate
    (1, 0.9, 0.70, 0.05, 0.35),         # a stiffener's lower bolt
    (2, 0.46, 0.83, 0.2, 0.55),         # the starter box
    (2, 0.5, 0.685, 0.05, 0.35),        # the conduit's clip
    (2, 0.8, 0.865, 0.09, 0.5),         # the hose's lower clip
    (2, 0.62, 0.65, 0.05, 0.35),        # the gauge line's gland
    (1, 0.5, 0.56, 0.6, 0.3),           # the girth weld, across the south face
]


def wet_streaks(g, col, pos, normal, z, under, where, strength=1.0):
    stretch = g.node("ShaderNodeMapping", Vector=pos)
    stretch.inputs["Scale"].default_value = (1.0, 1.0, 0.12)
    runs = g.remap(g.image(f"{TEX}/maps/rust_streak.png", stretch.outputs[0], 2.6).outputs["Color"], 0.3, 0.6)
    hang = None
    for i, f, zb, w, L in under:
        o, t, n = face_frame(i, f, zb)
        rel = _vmath(g, "SUBTRACT", pos, o)
        across = g.remap(g.math("ABSOLUTE", _vmath(g, "DOT_PRODUCT", rel, t)), w / 2, w * 0.15)
        below = g.math("MULTIPLY", g.remap(z, zb - L, zb - 0.02), g.remap(z, zb + 0.005, zb - 0.005))
        facing = g.remap(_vmath(g, "DOT_PRODUCT", normal, n), 0.75, 0.9)
        inplane = g.remap(g.math("ABSOLUTE", _vmath(g, "DOT_PRODUCT", rel, n)), 0.06, 0.03)
        m = g.math("MULTIPLY", g.math("MULTIPLY", across, below), g.math("MULTIPLY", facing, inplane))
        hang = m if hang is None else g.math("MAXIMUM", hang, m)
    wet = g.math("MULTIPLY", g.math("MULTIPLY", hang, runs), g.math("MULTIPLY", where, strength), clamp=True)
    return g.mixc(wet, col, g.mixc(g.noise(pos, 19, detail=3), _flat(g, WET[0]), _flat(g, WET[1])))


def dry_rust(g, col, pos, nz, amount, where):
    """Rust dried on the tops, where the water stood and went: orange and powdery, in
    patches, not a wash; only on cool metal."""
    up = g.remap(nz, 0.75, 0.97)
    patches = g.remap(g.noise(pos, 6, detail=6, rough=0.6), 0.56, 0.7)
    chips = g.remap(g.image(f"{TEX}/maps/paint_mask.png", pos, 1.7).outputs["Color"], 0.5, 0.15)
    m = g.math("MULTIPLY", up, g.math("MAXIMUM", patches, g.math("MULTIPLY", chips, 0.6)))
    m = g.math("MULTIPLY", g.math("MULTIPLY", m, where), amount, clamp=True)
    return g.mixc(m, col, g.mixc(g.noise(pos, 27, detail=3), _flat(g, DRY[0]), _flat(g, DRY[1])))


def grime_streaks(g, col, pos, z, where):
    """Uneven grime (round 3: less machined): dirty water and oil run down the lower
    course in streaks of uneven strength, never in the bands."""
    stretch = g.node("ShaderNodeMapping", Vector=pos)
    stretch.inputs["Scale"].default_value = (1.0, 1.0, 0.08)
    runs = g.remap(g.image(f"{TEX}/maps/rust_streak.png", stretch.outputs[0], 1.7).outputs["Color"], 0.45, 0.8)
    uneven = g.remap(g.noise(pos, 1.8, detail=2), 0.35, 0.65)
    low = g.remap(z, 0.62, 0.45)
    m = g.math("MULTIPLY", g.math("MULTIPLY", runs, uneven), g.math("MULTIPLY", low, where))
    return g.mixc(g.math("MULTIPLY", m, 0.55, clamp=True), col, _flat(g, "#221C16"))


def hull_finish(tempered=1.0, gain=1.0, marks=True):
    """The hull's plates: the plinth swatch, tempered from the roof and the top course,
    stencilled, and rusted only where it is cool."""
    def pattern(g):
        pos, normal, (x, y, z), (nx, ny, nz) = _geometry(g)
        t = heat_hull(g, pos, x, y, z, nz)
        col = temper(g, _swatch(g, "plinth", gain), "#3E3B36", t, tempered)
        if marks:
            col = stencils(g, col, pos, normal, WALL_MARKS)
        where = cool(g, t) if tempered else 1.0
        col = wet_streaks(g, col, pos, normal, z, WET_UNDER, where)
        col = grime_streaks(g, col, pos, z, where)
        return dry_rust(g, col, pos, nz, 0.7, where)
    return pattern


def drum_finish(g):
    pos, normal, (x, y, z), (nx, ny, nz) = _geometry(g)
    t = heat_roof(g, pos, x, y)
    return dry_rust(g, temper(g, _swatch(g, "drum"), "#5E584E", t), pos, nz, 0.6, cool(g, t))


def radiator_finish(g):
    pos, normal, (x, y, z), (nx, ny, nz) = _geometry(g)
    return temper(g, _swatch(g, "radiator"), "#6E685C", heat_radiator(g, pos, z))


def rail_finish(g):
    """The cap rail: bare steel round the drum, so the roof's rings run onto it."""
    pos, normal, (x, y, z), (nx, ny, nz) = _geometry(g)
    t = heat_roof(g, pos, x, y)
    return dry_rust(g, temper(g, _flat(g, "#77716A"), "#77716A", t, 0.8), pos, nz, 0.4, cool(g, t))


def hatch_finish(g):
    pos, normal, (x, y, z), (nx, ny, nz) = _geometry(g)
    return stencils(g, _swatch(g, "hatch_warm"), pos, normal, HATCH_MARKS)


M = {
    # spec 3.3, each on the concept's own swatch (recentred on the 3.3 hex), and the
    # signature finish over it. Round 2: the layered rust (cavities, streaks, blooms)
    # turned down on the tempered parts, so the bands stay clean; the cool metal
    # carries the rust in the patterns above, and in the girth weld's and ground's drips
    "drum":     layered("drum", "#5E584E", paint_metal=0.0, paint_rough=0.65, wear=0.45, rust=0.15,
                        dust=0.2, pattern=drum_finish),
    # the shell -- the hull's wall plates and its deck, and the south pipe picture's
    # wall -- is what the heat reaches; the hull's paint on everything else (the pump's
    # barrel and motor, the starter box, the stacks' feet, the hatch's grooves) stays
    # plain, so no fitting stands striped in the walls' bands
    # grime 0.75: dark contact lines where the hoses, cables and fittings meet the walls
    "shell":    layered("shell", "#3E3B36", paint_metal=0.0, paint_rough=0.7, wear=0.5, rust=0.12,
                        dust=0.3, pattern=hull_finish(), ground=0.7, jitter=0.12, grime=0.75,
                        # rust run down from the girth weld's bolts, wet and dark, below the bands
                        drips=((0.6, 0.35),), drip=0.8, rust_tint=("#2E1A0E", "#6A3818")),
    "hull":     layered("hull", "#3E3B36", paint_metal=0.0, paint_rough=0.7, wear=0.5, rust=0.22,
                        dust=0.3, pattern=hull_finish(tempered=0.0, marks=False), ground=0.7, jitter=0.16,
                        drips=((0.6, 0.35),), drip=0.8, rust_tint=("#2E1A0E", "#6A3818")),
    "radiator": layered("radiator", "#6E685C", metal="#9A9488", paint_metal=0.3, paint_rough=0.45,
                        wear=0.4, rust=0.15, dust=0.15, grime=0.3, pattern=radiator_finish),
    "seam":     layered("seam", "#7A7268", metal="#A49C90", paint_metal=0.7, paint_rough=0.4,
                        wear=0.3, rust=0.2, dust=0.0, jitter=0.04, ground=0.7),
    "steel":    layered("steel", "#77716A", metal="#B4AEA4", paint_metal=0.8, paint_rough=0.35,
                        wear=0.45, rust=0.25, dust=0.1, grime=0.5, ground=0.7),
    "rail":     layered("rail", "#77716A", metal="#B4AEA4", paint_metal=0.8, paint_rough=0.35,
                        wear=0.45, rust=0.1, dust=0.1, grime=0.5, pattern=rail_finish),
    "copper":   layered("copper", "#94592C", metal="#C08452", paint_metal=0.9, paint_rough=0.38,
                        wear=0.4, rust=0.1, dust=0.15, grime=0.5, swatch=swatch("copper"),
                        patina=1.0),
    "brass":    layered("brass", "#9C7034", metal="#C49C5C", paint_metal=0.9, paint_rough=0.38,
                        wear=0.4, rust=0.15, dust=0.15, swatch=swatch("brass")),
}
# Two replacement plates (3.3's variation): newer steel, painted after the rest, so a
# shade lighter and cooler, unstencilled and untempered -- they break the bands.
# Both upper plates either side of the south-west corner: one repair, round the corner.
REPLACED = {(0, 0.0, 0.58), (1, 0.0, 0.58)}          # (face, f0, z0) of the panels in 1.
M["hull_new"] = layered("hull_new", "#45433E", paint_metal=0.0, paint_rough=0.65, wear=0.3, rust=0.12,
                        dust=0.3, pattern=hull_finish(tempered=0.0, gain=(1.12, 1.13, 1.16), marks=False),
                        ground=0.7, jitter=0.04, drips=((0.6, 0.35),), drip=0.5,
                        rust_tint=("#2E1A0E", "#6A3818"))
# the roof warmed toward the adopted plate's beige and the dogs bronze (spec 3.3);
# a stencil on it (3.3's variation)
M["hatch"] = layered("hatch", "#958577", metal="#B8B0A4", paint_metal=0.25, paint_rough=0.6,
                     wear=0.35, rust=0.2, dust=1.0, grime=0.9, pattern=hatch_finish)
M["dog"] = M["copper"]
# a repair plate: plain steel, darker than the hatch's warm paint and dirtier
M["patch"] = layered("patch", "#5C564D", metal="#A8A296", paint_metal=0.3, paint_rough=0.6,
                     wear=0.5, rust=0.35, dust=0.15, grime=0.9)
# the corner angles: the hull's steel, knocked back to bare metal along their edges
M["edge"] = layered("edge", "#4A463F", metal="#B4AEA4", paint_metal=0.2, paint_rough=0.6,
                    wear=0.95, rust=0.25, dust=0.2, grime=0.5, ground=0.7)
# the dogs' wear on the warning ring: bare steel, polished by the dogs swinging over it
M["scuff"] = layered("scuff", "#8A847A", metal="#C4BEB4", paint_metal=0.9, paint_rough=0.3,
                     wear=0.6, rust=0.1, dust=0.3, grime=0.4)
# a warning ring round the hatch's rim, faded and worn by the dogs (Liam, 2026-10-08)
M["hazard"] = layered("hazard", "#B8962E", paint_metal=0.1, paint_rough=0.85, wear=0.75,
                      rust=0.35, dust=0.9, grime=0.8,
                      pattern=lambda g: g.mixc(0.45, hazard_pattern(g), (0.16, 0.13, 0.09, 1.0)))
M["hinge"] = M["brass"]
# the gauge's dial: dull, so it never reads as a second light (spec 3.3)
# the flywheel: bare steel, darker than the fittings so it never glares in the niche
M["wheel"] = layered("wheel", "#55504A", metal="#9A948C", paint_metal=0.8, paint_rough=0.4,
                     wear=0.5, rust=0.3, dust=0.1, grime=0.6)
# its rim turned bright, as a flywheel's machined rim is, so the ellipse reads at 1x
# and the dark spokes move against it (Liam, 2026-10-08)
M["rim"] = layered("rim", "#9A948C", metal="#D2CCC2", paint_metal=1.0, paint_rough=0.28,
                   wear=0.15, rust=0.08, dust=0.05, grime=0.25)
M["dial"] = layered("dial", "#8E877B", paint_metal=0.0, paint_rough=0.75, wear=0.15, rust=0.05,
                    dust=0.4, grime=0.6)

# Round 3 (Liam: "too well machined"; add wiring and hoses as vanilla layers them):
# the services' materials. Hoses in dull rust-brown rubber, as the electromagnetic
# plant's; cables insulated in muted colours, as the foundry's; zip ties black.
# FFF #146's rule, done in the model: clear value separation, crisp light edges. The
# hoses and cables sit a step lighter than the dark walls they lie on, and their
# worn edges go lighter still (the `metal` colour is the edge's), so each reads as a
# line at 1x (FFF #350) instead of sinking into the hull.
M["rubber"] = layered("rubber", "#93603F", metal="#C89270", paint_metal=0.0, paint_rough=0.7, wear=0.4,
                      rust=0.0, dust=0.35, grime=0.6, jitter=0.06)
for _name, _hex, _edge in (("red", "#B24C38", "#E09078"), ("blue", "#5678A6", "#A0B8D8"),
                           ("yellow", "#CCA848", "#EED898"), ("green", "#5E8452", "#A0C090"),
                           ("black", "#3A3836", "#7A7672"), ("grey", "#4C4A47", "#7E7A74"),
                           ("muted", "#4A5260", "#7A8290")):
    M[f"cable-{_name}"] = layered(f"cable-{_name}", _hex, metal=_edge, paint_metal=0.0, paint_rough=0.5,
                                  wear=0.3, rust=0.0, dust=0.25, grime=0.4, jitter=0.05)
M["tie"] = layered("tie", "#1E1D1B", paint_metal=0.0, paint_rough=0.5, wear=0.0, rust=0.0, dust=0.2, grime=0.3)
# a junction box in another maker's grey-green, bolted on later than the hull was built
M["jbox"] = layered("jbox", "#5A6052", metal="#A8A498", paint_metal=0.1, paint_rough=0.6, wear=0.5, rust=0.25,
                    dust=0.4, grime=0.7)
# a mismatched newer plate: brighter steel, little worn
M["newplate"] = layered("newplate", "#6E6A62", metal="#B4AEA4", paint_metal=0.5, paint_rough=0.45, wear=0.2,
                        rust=0.05, dust=0.3, grime=0.5, jitter=0.02)


def oil_material():
    """Oil soaked into the ground under the pump: dark and glossy, its edge feathered
    into the ground by noise, so it reads as a stain and not as a mat."""
    m = bpy.data.materials.new("oil")
    m.use_nodes = True
    t = m.node_tree
    b = t.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#16120E")
    b.inputs["Roughness"].default_value = 0.22
    co = t.nodes.new("ShaderNodeTexCoord")
    ln = t.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    t.links.new(co.outputs["Object"], ln.inputs[0])
    nz = t.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 6.0
    nz.inputs["Detail"].default_value = 4.0
    t.links.new(co.outputs["Object"], nz.inputs["Vector"])
    add = t.nodes.new("ShaderNodeMath")
    add.operation = "MULTIPLY_ADD"
    t.links.new(nz.outputs["Fac"], add.inputs[0])
    add.inputs[1].default_value = 0.6
    t.links.new(ln.outputs["Value"], add.inputs[2])
    rng = t.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = 1.15
    rng.inputs["From Max"].default_value = 0.75
    rng.inputs["To Max"].default_value = 0.85
    t.links.new(add.outputs[0], rng.inputs["Value"])
    t.links.new(rng.outputs[0], b.inputs["Alpha"])
    return m


M["oil"] = oil_material()


VIEW_R = 0.145                         # the porthole glass


def port_material():
    """The porthole: a furnace seen through thick glass, not a lamp (Liam, round 4:
    "more like a furnace than a light"). Idle, dark smoky glass with a reflection
    streak across it. Working, what the glass shows lights up: the sintering tray's
    bed of powder and preforms glowing in uneven clumps with darker gaps between
    them, hottest at the core -- #FFD9A0 to #E8A24A (spec 3.3) -- then orange, then
    deep red where the chamber's walls fall away into the dark at the rim. Only the
    emission changes between idle and working, so the glow pass (working minus
    idle) holds the bed and nothing else; the streak is the same in both, so it
    cancels out of it. A value node, "white", turns the whole glass white for the
    indicator pass (indicator_cut)."""
    m = bpy.data.materials.new("port")
    m.use_nodes = True
    t = m.node_tree
    N, L = t.nodes, t.links
    b = N["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.06
    b.inputs["Coat Weight"].default_value = 1.0                         # thick glass's sheen
    b.inputs["Coat Roughness"].default_value = 0.03

    def node(kind, **kw):
        nd = N.new(kind)
        for k, v in kw.items():
            setattr(nd, k, v)
        return nd

    def math_(op, a_, b_=None, clamp=False):
        nd = node("ShaderNodeMath", operation=op, use_clamp=clamp)
        for i, v in enumerate((a_, b_)):
            if v is None:
                continue
            if isinstance(v, bpy.types.NodeSocket):
                L.new(v, nd.inputs[i])
            else:
                nd.inputs[i].default_value = v
        return nd.outputs[0]

    def remap(v, lo, hi, a_=0.0, b_=1.0):
        nd = node("ShaderNodeMapRange")
        L.new(v, nd.inputs["Value"])
        nd.inputs["From Min"].default_value, nd.inputs["From Max"].default_value = lo, hi
        nd.inputs["To Min"].default_value, nd.inputs["To Max"].default_value = a_, b_
        return nd.outputs[0]

    def noise(scale, detail):
        nd = node("ShaderNodeTexNoise")
        nd.inputs["Scale"].default_value = scale
        nd.inputs["Detail"].default_value = detail
        nd.inputs["Roughness"].default_value = 0.6
        L.new(co.outputs["Object"], nd.inputs["Vector"])
        return nd.outputs["Fac"]

    co = node("ShaderNodeTexCoord")
    xyz = node("ShaderNodeSeparateXYZ")
    L.new(co.outputs["Object"], xyz.inputs[0])
    x, y = xyz.outputs["X"], xyz.outputs["Y"]
    rr = math_("DIVIDE", math_("SQRT", math_("ADD", math_("MULTIPLY", x, x), math_("MULTIPLY", y, y))), VIEW_R)
    # the bed: hottest at the core, cooling outward to the chamber's walls; clumps of
    # preforms brighter, the gaps between them darker
    core = math_("SUBTRACT", 1.0, math_("POWER", math_("MINIMUM", rr, 1.0), 1.7))
    clumps = remap(noise(30.0, 3.0), 0.3, 0.7, 0.6, 1.3)
    gaps = remap(noise(70.0, 2.0), 0.55, 0.72, 1.0, 0.55)
    heat = math_("MULTIPLY", math_("MULTIPLY", core, clumps), gaps, clamp=True)
    ramp = node("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    stops = [(0.0, "#000000"), (0.1, "#1E0603"), (0.24, "#6E1E0C"), (0.4, "#B8461A"), (0.56, "#E07E30"),
             (0.68, "#E8A24A"), (0.84, "#FFD9A0")]
    els[0].position, els[1].position = stops[0][0], stops[-1][0]
    for p_, _ in stops[1:-1]:
        els.new(p_)
    for e, (p_, hx) in zip(sorted(els, key=lambda e: e.position), stops):
        e.color = rig.srgb(hx)
    L.new(heat, ramp.inputs["Fac"])
    white = node("ShaderNodeValue", name="white", label="white")
    white.outputs[0].default_value = 0.0
    emit = node("ShaderNodeMix", data_type="RGBA")
    L.new(white.outputs[0], emit.inputs[0])
    L.new(ramp.outputs["Color"], emit.inputs[6])
    emit.inputs[7].default_value = (1, 1, 1, 1)
    L.new(emit.outputs[2], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.0
    # the glass: smoky, and a reflection streak across it (and a fainter second one),
    # fading before the rim; none of it in the indicator's white cut
    band = math_("ADD", math_("MULTIPLY", x, 0.707), math_("MULTIPLY", y, 0.707))
    s1 = math_("MULTIPLY", remap(math_("ABSOLUTE", math_("SUBTRACT", band, 0.06)), 0.016, 0.004), 0.7)
    s2 = math_("MULTIPLY", remap(math_("ABSOLUTE", math_("SUBTRACT", band, 0.095)), 0.008, 0.002), 0.35)
    streak = math_("MULTIPLY", math_("MAXIMUM", s1, s2), remap(rr, 0.95, 0.7))
    streak = math_("MULTIPLY", streak, math_("SUBTRACT", 1.0, white.outputs[0]))
    base = node("ShaderNodeMix", data_type="RGBA")
    L.new(streak, base.inputs[0])
    base.inputs[6].default_value = rig.srgb("#26292C")
    base.inputs[7].default_value = rig.srgb("#7A8088")
    L.new(base.outputs[2], b.inputs["Base Color"])
    return m


M["port"] = port_material()

# ---------------------------------------------------------------- geometry

PARTS = {}          # group name -> [objects]; the passes toggle whole groups


def _finish(obj, mat, group, bevel=0.012, smooth=False, parent=None):
    obj.data.materials.append(M[mat])
    if bevel:
        mod = obj.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    obj.parent = parent or ROOT
    PARTS.setdefault(group, []).append(obj)
    return obj


def box(loc, size, mat, group="static", rot=(0, 0, 0), bevel=0.012, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, group, bevel, parent=parent)


def cyl(loc, r, h, mat, group="static", verts=48, rot=(0, 0, 0), bevel=0.01, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    o = _finish(bpy.context.active_object, mat, group, bevel, smooth=True, parent=parent)
    for p in o.data.polygons:          # the caps flat: a smoothed n-gon cap shades as a dark star
        if len(p.vertices) > 4:
            p.use_smooth = False
    return o


def torus(loc, major, minor, mat, group="static", rot=(0, 0, 0), parent=None, seg=64):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot,
                                     major_segments=seg, minor_segments=10)
    return _finish(bpy.context.active_object, mat, group, bevel=0, smooth=True, parent=parent)


def rivet(loc, r=0.016, mat="steel", group="static", parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=8, ring_count=5)
    o = bpy.context.active_object
    o.scale.z = 0.6
    return _finish(o, mat, group, bevel=0, smooth=True, parent=parent)


def mesh_object(name, build, mat, group, bevel, smooth=False, parent=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    return _finish(o, mat, group, bevel, smooth=smooth, parent=parent)


def loft(lo, hi, z0, z1, mat, group="static", bevel=0.02):
    """A slab from outline `lo` at z0 to outline `hi` at z1 (same point count)."""
    def build(bm):
        a = [bm.verts.new((x, y, z0)) for x, y in lo]
        b = [bm.verts.new((x, y, z1)) for x, y in hi]
        bm.faces.new(list(reversed(a)))
        bm.faces.new(b)
        for i in range(len(lo)):
            j = (i + 1) % len(lo)
            bm.faces.new((a[i], a[j], b[j], b[i]))
    return mesh_object("loft", build, mat, group, bevel)


def prism(points, z0, z1, mat, group="static", bevel=0.015):
    return loft(points, points, z0, z1, mat, group, bevel)


def ring(loc, r_out, r_in, h, mat, group="static", parent=None, verts=64, bevel=0.01, rot=(0, 0, 0)):
    """A thick washer about local Z: open through the middle."""
    def build(bm):
        rows = [[bm.verts.new((r * math.cos(2 * math.pi * i / verts), r * math.sin(2 * math.pi * i / verts), z))
                 for i in range(verts)] for r, z in ((r_out, -h / 2), (r_out, h / 2), (r_in, h / 2), (r_in, -h / 2))]
        for k in range(4):
            a, b = rows[k], rows[(k + 1) % 4]
            for i in range(verts):
                j = (i + 1) % verts
                bm.faces.new((a[i], a[j], b[j], b[i]))
    o = mesh_object("ring", build, mat, group, bevel, smooth=True, parent=parent)
    o.location, o.rotation_euler = loc, rot
    return o


def tube(pts, r, mat, group="static", parent=None):
    cu = bpy.data.curves.new("tube", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, co in zip(sp.bezier_points, pts):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    ob = bpy.data.objects.new("tube", cu)
    sc.collection.objects.link(ob)
    return _finish(ob, mat, group, bevel=0, parent=parent)


def pipe(pts, r, mat, bend=0.07, group="static"):
    """A rigid pipe through pts, each corner turned through an elbow of radius ~bend."""
    out = [Vector(pts[0])]
    for i in range(1, len(pts) - 1):
        p, a_, b_ = Vector(pts[i]), Vector(pts[i - 1]), Vector(pts[i + 1])
        e = min(bend, 0.45 * (a_ - p).length, 0.45 * (b_ - p).length)
        s0, s1 = p + (a_ - p).normalized() * e, p + (b_ - p).normalized() * e
        for k in range(9):
            t = k / 8
            out.append((1 - t) ** 2 * s0 + 2 * (1 - t) * t * p + t * t * s1)
    out.append(Vector(pts[-1]))
    cu = bpy.data.curves.new("pipe", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(out) - 1)
    for pt, co in zip(sp.points, out):
        pt.co = (*co, 1)
    ob = bpy.data.objects.new("pipe", cu)
    sc.collection.objects.link(ob)
    return _finish(ob, mat, group, bevel=0)


def spline(ctrl, per=10):
    """A smooth path through ctrl (Catmull-Rom), sampled densely: hoses and cables
    hang through their points, never overshooting them as Bezier handles would."""
    P = [Vector(c) for c in ctrl]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(per):
            t = k / per
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return out


def droop(a, b, sag, n=6):
    """Control points for a slack run from a to b, hanging sag below the chord."""
    a, b = Vector(a), Vector(b)
    return [tuple(a + (b - a) * (k / n) - Vector((0, 0, sag * 4 * (k / n) * (1 - k / n)))) for k in range(n + 1)]


def poly_tube(pts, r, mat, group="static", name="cable"):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for pt, co in zip(sp.points, pts):
        pt.co = (*co, 1)
    ob = bpy.data.objects.new(name, cu)
    sc.collection.objects.link(ob)
    return _finish(ob, mat, group, bevel=0)


def _arc(pts):
    s_ = [0.0]
    for a, b in zip(pts, pts[1:]):
        s_.append(s_[-1] + (b - a).length)
    return s_


def ferrule(pos, direction, r):
    """A crimped hose end: a steel sleeve over the hose, pinched by two crimp rings."""
    dv = Vector(direction).normalized()
    rot = dv.to_track_quat("Z", "Y").to_euler()
    cyl(tuple(pos), r + 0.012, 0.055, "steel", verts=20, rot=rot, bevel=0.004)
    for o in (-0.014, 0.014):
        torus(tuple(Vector(pos) + dv * o), r + 0.011, 0.005, "seam", rot=rot, seg=20)


def hose(ctrl, r, mat="rubber", pitch=0.034, ends=True):
    """A flexible hose, vanilla's way: corrugated, hanging slack through ctrl, a
    crimped ferrule at each end."""
    pts = spline(ctrl)
    poly_tube(pts, r, mat, name="hose")
    s_ = _arc(pts)
    nxt = 0.07
    for i in range(1, len(pts) - 1):
        if nxt <= s_[i] <= s_[-1] - 0.07:
            nxt = s_[i] + pitch
            torus(tuple(pts[i]), r + 0.002, r * 0.16, mat, rot=(pts[i + 1] - pts[i - 1]).normalized()
                  .to_track_quat("Z", "Y").to_euler(), seg=16)
    if ends:
        ferrule(pts[0] + (pts[3] - pts[0]).normalized() * 0.03, pts[3] - pts[0], r)
        ferrule(pts[-1] + (pts[-4] - pts[-1]).normalized() * 0.03, pts[-4] - pts[-1], r)
    return pts


def bundle(ctrl, mats, r=0.011, gap=0.023, ties=0.11, lie=(0.0, 0.0, 1.0), rows=1):
    """Insulated cables side by side through ctrl, zip-tied every `ties`: each cable
    offset across the run, in the surface it lies on (whose normal is `lie`); with
    rows=2, a chunky bundle, half the cables heaped on the other half."""
    pts = spline(ctrl)
    L = Vector(lie)
    sides, prev = [], Vector((1, 0, 0))
    for i in range(len(pts)):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        sd = t.cross(L)
        sd = sd.normalized() if sd.length > 0.2 else prev
        if sd.dot(prev) < 0:
            sd = -sd
        sides.append(sd)
        prev = sd
    n = len(mats)
    per = (n + rows - 1) // rows
    ups = []
    for i, sd in enumerate(sides):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        u = sd.cross(t)
        ups.append(u.normalized() if u.length > 0.2 else L)
    for k, m in enumerate(mats):
        row, col = divmod(k, per)
        off = (col - (per - 1) / 2 + 0.35 * row) * gap
        lift = row * gap * 0.85
        poly_tube([p + sd * off + u * lift for p, sd, u in zip(pts, sides, ups)], r, m)
    n = per
    s_ = _arc(pts)
    nxt = 0.05
    for i in range(1, len(pts) - 1):
        if nxt <= s_[i] <= s_[-1] - 0.04:
            nxt = s_[i] + ties
            rot = (pts[i + 1] - pts[i - 1]).normalized().to_track_quat("Z", "Y").to_euler()
            bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.12, location=tuple(pts[i]),
                                             rotation=rot, major_segments=16, minor_segments=6)
            o = bpy.context.active_object
            o.scale = ((n - 1) / 2 * gap + r + 0.004, r + 0.004 + (rows - 1) * gap * 0.45, 0.035)
            _finish(o, "tie", "static", bevel=0, smooth=True)
    return pts


def oval(c, ra, rb, ang, z, h, mat, bevel=0.004, n=32):
    """A flat oval slab, ra along ang and rb across it, h thick, centred at height z."""
    ca, sa = math.cos(ang), math.sin(ang)

    def build(bm):
        rows = [[bm.verts.new((c[0] + ra * math.cos(u) * ca - rb * math.sin(u) * sa,
                               c[1] + ra * math.cos(u) * sa + rb * math.sin(u) * ca, zz))
                 for u in (2 * math.pi * k / n for k in range(n))] for zz in (z - h / 2, z + h / 2)]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((rows[0][i], rows[0][j], rows[1][j], rows[1][i]))
        bm.faces.new(rows[1])
        bm.faces.new(rows[0][::-1])
    return mesh_object("oval", build, mat, "static", bevel)


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.parent = parent or ROOT
    e.location, e.rotation_euler, e.scale = loc, rot, scale
    return e


# A face that lands on screen as a circle: tilted back 53.13 degrees, normal (0, -0.8, 0.6).
TILT = (math.atan2(0.8, 0.6), 0, 0)

import random  # noqa: E402
PLATE_RNG = random.Random(1009)

# 1. The hull: battered, octagonal, filling the footprint; its face middles stand on
# the footprint edge, its corners cut into niches for the stacks. (Its shape, HZ to
# wall_pt, is defined above the materials: the finish places marks on its faces.)
# An open shell: the battered walls, 0.06 thick, with no lid -- the drum stands inside
# them on a deck (below), and its front wall comes through the south face.
def build_panel(i, f0, f1, z0, z1):
    """One plate of face i: f0..f1 along it, z0..z1 up it."""
    def build(bm):
        q = [bm.verts.new(octagon_pt(i, f, z)) for f, z in ((f0, z0), (f1, z0), (f1, z1), (f0, z1))]
        bm.faces.new(q)
    return build


def octagon_pt(i, f, z):
    e, c = E - LEAN * z / HZ, C + (CT - C) * z / HZ
    pts = octagon(e, c)
    (ax, ay), (bx, by) = pts[i], pts[(i + 1) % 8]
    return (ax + (bx - ax) * f, ay + (by - ay) * f, z)


# The walls in plates, each its own object, so each takes its own slight tone of the
# paint as a fabricated hull does (Liam, 2026-10-08): two courses split at the girth
# weld, the long faces' middle plates between their stiffeners.
for i in range(8):
    cols = (0.0, 0.1, 0.9, 1.0) if i % 2 else (0.0, 1.0)
    for f0, f1 in zip(cols, cols[1:]):
        for z0, z1 in ((0.0, 0.58), (0.58, HZ)):
            mat = "hull_new" if (i, f0, z0) in REPLACED else "shell"
            pl = mesh_object("hull", build_panel(i, f0, f1, z0, z1), mat, "hull", bevel=0.0)
            sol = pl.modifiers.new("solid", "SOLIDIFY")
            sol.thickness = 0.06
            sol.offset = -1.0                    # inward: the outside is the approved hull
            # Plates hung by hand, not machined (round 3): each stands a few
            # thousandths proud of its neighbours, so its edges step; the replaced
            # ones, newer and thicker, a little more.
            d = 0.012 if mat == "hull_new" else PLATE_RNG.uniform(0.0, 0.007)
            n_ = face_frame(i, 0.5, 0.6)[2]
            pl.location = (n_[0] * d, n_[1] * d, 0.0)
for z0, z1 in ((0.0, 0.07), (0.56, 0.6)):                         # a foot band and a girth weld
    e0, c0 = at_lean(z0)
    e1, c1 = at_lean(z1)
    loft(octagon(e0 + 0.01, c0), octagon(e1 + 0.01, c1), z0, z1, "seam", group="hull", bevel=0.004)
ER, CR = at_lean(HZ)
ON_CHAMFER = (-math.atan2(LEAN, HZ), 0, math.radians(45))     # square to the south-east chamfer, leaning with it


def wall_strip(i, f, w, z0, z1, d, mat, group="hull"):
    """A strip standing d proud of face i, w wide, from z0 to z1, leaning with it."""
    run = math.hypot(*(a - b for a, b in zip(wall_pt(i, 1, z0)[:2], wall_pt(i, 0, z0)[:2])))
    h = w / 2 / run

    def build(bm):
        v = [bm.verts.new(wall_pt(i, f + s * h, z, o)) for z in (z0, z1) for s in (-1, 1) for o in (-0.01, d)]
        for q in ((0, 2, 6, 4), (1, 5, 7, 3), (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6)):
            bm.faces.new([v[k] for k in q])
    return mesh_object("strip", build, mat, group, bevel=0.006)


# The walls made up of plates (Liam, 2026-10-08: the textures overall): on each long
# face a welded joint either side of the pipe picture, clear of its plate, each
# capped by a bolted stiffener; and bolts along the girth weld and the foot band.
for i in (1, 3, 5, 7):
    for f in (0.1, 0.9):
        wall_strip(i, f, 0.07, 0.07, 0.56, 0.018, "steel")
        wall_strip(i, f, 0.07, 0.6, HZ - 0.02, 0.018, "steel")
        for z in (0.16, 0.36, 0.72, 0.92):
            rivet(wall_pt(i, f, z, 0.024), 0.016)
# Angle iron down every vertical corner, its edge worn to bare metal where things
# have knocked it (Liam, 2026-10-08): two leaves, one on each face.
for i in range(8):
    wall_strip(i, 0.018 / math.hypot(*(a - b for a, b in zip(wall_pt(i, 1, 0.6)[:2], wall_pt(i, 0, 0.6)[:2]))),
               0.036, 0.07, HZ - 0.02, 0.014, "edge")
    j = (i - 1) % 8
    wall_strip(j, 1 - 0.018 / math.hypot(*(a - b for a, b in zip(wall_pt(j, 1, 0.6)[:2], wall_pt(j, 0, 0.6)[:2]))),
               0.036, 0.07, HZ - 0.02, 0.014, "edge")
# the maker's plate: brass, riveted to the south face's upper band, off the pipe's middle
wall_strip(1, 0.27, 0.19, 0.74, 0.88, 0.012, "brass", group="static")
for df in (-0.075, 0.075):
    for z in (0.765, 0.855):
        rivet(wall_pt(1, 0.27 + df / 1.164, z, 0.02), 0.011)
for i in range(8):
    run = math.hypot(*(a - b for a, b in zip(wall_pt(i, 1, 0.58)[:2], wall_pt(i, 0, 0.58)[:2])))
    n = max(2, round(run / 0.14))
    for k in range(1, n):
        rivet(wall_pt(i, k / n, 0.58, 0.016), 0.015)
        rivet(wall_pt(i, k / n, 0.035, 0.008), 0.013)          # sunk: the foot band is at the footprint


def octagon_ring(outer, inner, z0, z1, mat, group):
    """A slab between two octagons: the cap rail round the shell's open top."""
    def build(bm):
        rows = [[bm.verts.new((x, y, z)) for x, y in pts] for pts, z in
                ((outer, z0), (outer, z1), (inner, z1), (inner, z0))]
        n = len(outer)
        for k in range(4):
            r0, r1 = rows[k], rows[(k + 1) % 4]
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    return mesh_object("rail", build, mat, group, bevel=0.012)


octagon_ring(octagon(ER + 0.01, CR), octagon(ER - 0.1, CR - 0.04), HZ - 0.01, HZ + 0.05, "rail", "hull")
PZ = HZ + 0.05
# The cap rail made up, so the roof's edge is not a bare band (Liam, 2026-10-08): a
# kerb along its outer edge, a weld across each mitred corner, and a row of bolts
# all the way round at an even pitch.
octagon_ring(octagon(ER + 0.01, CR), octagon(ER - 0.022, CR - 0.009), PZ - 0.005, PZ + 0.022,
             "rail", "hull")
_ro, _ri = octagon(ER + 0.01, CR), octagon(ER - 0.1, CR - 0.04)
for (ox, oy), (ix, iy) in zip(_ro, _ri):
    box(((ox + ix) / 2, (oy + iy) / 2, PZ + 0.002), (math.hypot(ox - ix, oy - iy), 0.016, 0.012),
        "seam", rot=(0, 0, math.atan2(oy - iy, ox - ix)), bevel=0.004)
_rm = octagon(ER - 0.06, CR - 0.025)
for i, (ax, ay) in enumerate(_rm):
    bx, by = _rm[(i + 1) % len(_rm)]
    run = math.hypot(bx - ax, by - ay)
    n = max(1, round((run - 0.12) / 0.13))
    for k in range(n + 1):
        f = (0.06 + (run - 0.12) * k / n) / run
        rivet((ax + (bx - ax) * f, ay + (by - ay) * f, PZ + 0.004), 0.019)

# 2. The drum: one welded piece, raised on the hull, round and on the footprint's
# centre, its deck level with the top of the hull's rail, which runs round it as an
# even parapet (blockout revision 4, Liam 2026-10-07).
YC, K, R, H = 0.0, 1.0, 0.89, PZ
RD = 1.08                                   # the drum wall; the hatch keeps R
BODY = empty("body", loc=(0, YC, 0), scale=(1, K, 1))


def on_body(a, r, z):
    return (r * math.cos(a), r * math.sin(a), z)


cyl((0, 0, H / 2), RD, H, "drum", verts=128, bevel=0.02, parent=BODY)
torus((0, 0, 0.55), RD + 0.002, 0.011, "seam", parent=BODY, seg=128)                       # girth weld
# the deck inside the hull's walls, level with the drum's top
ED, CD = at_lean(H)
deck = prism(octagon(ED - 0.05, CD), 0.0, H - 0.012, "shell", group="hull", bevel=0.0)
# Where the drum comes through, the hull gives way to it: its walls, rail and deck are
# cut by the drum's own shape (a hidden cutter), so nothing of the hull crosses the roof.
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=RD + 0.004, depth=4.0, location=(0, 0, 0))
CUTTER = bpy.context.active_object
CUTTER.parent = BODY
CUTTER.hide_render = True
CUTTER.display_type = "WIRE"
for o in PARTS["hull"]:
    if o.name.startswith(("hull", "rail")) or o is deck:
        b = o.modifiers.new("drum", "BOOLEAN")
        b.operation = "DIFFERENCE"
        b.object = CUTTER
        b.solver = "EXACT"
for k in range(6):                                                                          # long welds
    a = math.radians(-60 + k * 60)
    box(on_body(a, RD + 0.002, (0.1 + H - 0.04) / 2), (0.014, 0.022, H - 0.04 - 0.1), "seam",
        rot=(0, 0, a), bevel=0.004, parent=BODY)
torus((0, 0, H - 0.005), RD - 0.005, 0.016, "seam", parent=BODY, seg=128)                  # deck edge
# the drum's lid flange bolted down: hex heads in threes between the dogs
for k in range(8):
    for j in (1, 2, 3):
        a = math.radians(k * 45 + j * 11.25)
        cyl(on_body(a, 0.985, H + 0.008), 0.02, 0.018, "steel", verts=6, rot=(0, 0, a), bevel=0.004,
            parent=BODY)

# the roof: flange ring and the hatch, flat in the roof (spec 3.2), with its groove
# rings; the viewport (5.) takes the middle
cyl((0, 0, H + 0.02), R + 0.03, 0.06, "hatch", verts=128, bevel=0.015, parent=BODY)
cyl((0, 0, H + 0.07), R - 0.04, 0.05, "hatch", verts=128, bevel=0.012, parent=BODY)
DOME_R, DOME_H, DZ = R - 0.11, 0.03, H + 0.09
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, DZ), segments=128, ring_count=48)
dome = bpy.context.active_object
dome.scale = (DOME_R, DOME_R, DOME_H)
bpy.ops.object.transform_apply(scale=True)
_finish(dome, "hatch", "static", bevel=0, smooth=True, parent=BODY)


def domez(r):
    return DZ + DOME_H * math.sqrt(max(0.0, 1 - (r / DOME_R) ** 2))


torus((0, 0, H + 0.096), R - 0.035, 0.012, "hull", parent=BODY, seg=128)            # flange gap
torus((0, 0, domez(0.62) - 0.004), 0.62, 0.014, "hull", parent=BODY, seg=128)       # groove
torus((0, 0, domez(0.66) + 0.002), 0.66, 0.012, "hatch", parent=BODY, seg=128)
torus((0, 0, DZ + 0.004), DOME_R - 0.01, 0.018, "hatch", parent=BODY, seg=128)
# a warning ring round the hatch's outer band, under the dogs, worn where they bear
ring((0, 0, DZ + 0.013), 0.762, 0.676, 0.012, "hazard", parent=BODY, verts=128, bevel=0.0)
# the dogs' wear on it: a bare, polished patch either side of each dog, where it swings
for k in range(8):
    for side in (-1, 1):
        a = math.radians(k * 45 + side * 10.0)
        box(on_body(a, 0.719, DZ + 0.0205), (0.05, 0.035, 0.003), "scuff", rot=(0, 0, a), bevel=0.0,
            parent=BODY)
# The hatch's plate welded up from six segments (Liam, 2026-10-08): a seam from the
# viewport's skirt out to the groove ring, between the dogs, lying on the roof.
for k in range(6):
    a = math.radians(30 + k * 60)
    r0, r1 = 0.27, 0.605
    rm = (r0 + r1) / 2
    box(on_body(a, rm, domez(rm) + 0.003), (r1 - r0, 0.02, 0.012), "seam",
        rot=(0, math.atan2(domez(r0) - domez(r1), r1 - r0), a), bevel=0.004, parent=BODY)
TOPZ = domez(0)
# 3. The radial dogs: one every eighth of a turn.
# Not quite even: each dog sits where it was last swung to, a few degrees either way
# (Liam, 2026-10-08: the hatch looked too perfect).
DOG_SET = (0.0, 2.5, -3.0, 1.0, -1.5, 3.0, -2.0, 1.5)
for k in range(8):
    a = math.radians(k * 45 + DOG_SET[k])
    box(on_body(a, 0.84, H + 0.13), (0.32, 0.17, 0.11), "dog", rot=(0, 0, a), bevel=0.018, parent=BODY)
    box(on_body(a, 0.97, H + 0.0), (0.09, 0.2, 0.3), "dog", rot=(0, 0, a), bevel=0.015, parent=BODY)
    box(on_body(a, 0.7, H + 0.16), (0.09, 0.21, 0.13), "hinge", rot=(0, 0, a), bevel=0.015, parent=BODY)
    rivet(on_body(a, 0.86, H + 0.195), 0.024, "steel", parent=BODY)
    rivet(on_body(a, 0.7, H + 0.23), 0.02, "steel", parent=BODY)

# 4. (there is no fault lamp: the viewport is the indicator, spec 3.2)
# 5. The sight port: at the hatch's centre, a raised boss carrying a heavy bolted ring
# and thick glass, set flat in the roof so it reads at the roof's angle (Liam,
# 2026-10-07). Dark glass when idle; working, the glass fills with orange light, the
# building's only glow; and its glass, cut white, is the indicator's light pass.
vx, vy = 0.0, YC
vz = domez(0)
cyl((vx, vy, vz - 0.04), 0.25, 0.12, "hatch", verts=64, bevel=0.02)                # the boss's skirt, on the dome
cyl((vx, vy, vz + 0.025), 0.265, 0.02, "steel", verts=64, bevel=0.006)              # its collar
# the head sits on the skirt, flat, its glass level with the roof
VP = empty("viewport", loc=(vx, vy, vz + 0.12))
cyl((0, 0, -0.14), 0.24, 0.22, "hatch", verts=64, bevel=0.015, parent=VP)           # the boss's face block
ring((0, 0, 0.0), 0.26, VIEW_R + 0.01, 0.07, "steel", parent=VP, bevel=0.015)       # heavy bolted ring
for k in range(10):
    t = 2 * math.pi * k / 10 + math.pi / 10
    rivet((0.21 * math.cos(t), 0.21 * math.sin(t), 0.04), 0.02, parent=VP)
ring((0, 0, 0.01), VIEW_R + 0.03, VIEW_R + 0.006, 0.06, "hull", parent=VP, bevel=0.008)   # glass bezel
cyl((0, 0, -0.035), VIEW_R + 0.008, 0.05, "port", group="port", verts=64, bevel=0.0, parent=VP)  # thick glass

# The roof's working fittings, off the hatch's symmetry as a used machine's are (Liam,
# 2026-10-08: the hatch looked too perfect; vanilla's round tops carry their fittings
# off-centre, and pipes cross them).
# The viewport's cover, hinged on the port's north side and flung right back, lying
# face-up on the hatch behind the glass, so it never hides the glass or its light: a
# knuckle on the boss, two straps down from it to the cover, and the cover's inside
# showing -- its gasket and the boss it bears on.
CZ = domez(0.45) + 0.018
KY, KZ = 0.262, vz + 0.05
cyl((0, KY, KZ), 0.022, 0.2, "steel", verts=16, rot=(0, math.pi / 2, 0), bevel=0.0)        # the knuckle
for sx in (-0.07, 0.07):
    ly, lz = 0.33 - KY, CZ + 0.012 - KZ
    box((sx, (KY + 0.33) / 2, (KZ + CZ + 0.012) / 2), (0.035, math.hypot(ly, lz) + 0.03, 0.016), "steel",
        rot=(math.atan2(lz, ly), 0, 0), bevel=0.005)                                        # strap
COVER = empty("cover", loc=(0, 0.45, CZ))         # its far edge at 0.60: inside the groove, clear of the north dog
cyl((0, 0, 0), 0.15, 0.03, "hatch", verts=48, bevel=0.008, parent=COVER)
torus((0, 0, 0.016), 0.122, 0.01, "hull", parent=COVER, seg=48)                            # its gasket
cyl((0, 0, 0.018), 0.07, 0.012, "steel", verts=32, bevel=0.004, parent=COVER)             # the boss it bears on
for sx in (-0.07, 0.07):
    rivet((sx, -0.11, 0.018), 0.012, parent=COVER)                                          # the straps' bolts
# The vacuum break: an off-centre valve that lets air back into the chamber before
# the hatch is opened. An angle valve: a squat body on the flange, its bonnet and stem
# out sideways, and the handwheel standing upright on the stem's end,
# so it draws at the camera's angle (Liam, 2026-10-08: lying level it drew as a full
# circle and looked turned to the camera, as the lifting eyes did).
a = math.radians(180)                       # mid-segment: clear of the seams at 150 and 210
bx_, by_ = on_body(a, 0.43, 0)[:2]          # its wheel ends at 0.6, inside the groove, clear of the dog
bz = domez(0.43)
ux, uy = math.cos(math.radians(225)), math.sin(math.radians(225))   # the stem points south-west:
# the wheel then draws as an ellipse at the lifting eyes' angle, not edge-on
cyl((bx_, by_, bz + 0.02), 0.06, 0.04, "steel", verts=24, bevel=0.008)                    # its flange
cyl((bx_, by_, bz + 0.075), 0.045, 0.07, "brass", verts=24, bevel=0.01)                   # body
cyl((bx_ + 0.055 * ux, by_ + 0.055 * uy, bz + 0.08), 0.03, 0.06, "brass", verts=16,
    rot=(0, math.pi / 2, math.radians(225)), bevel=0.006)                                  # bonnet
cyl((bx_ + 0.1 * ux, by_ + 0.1 * uy, bz + 0.08), 0.009, 0.05, "steel", verts=12,
    rot=(0, math.pi / 2, math.radians(225)), bevel=0.0)                                    # stem
WHL = empty("break-wheel", loc=(bx_ + 0.125 * ux, by_ + 0.125 * uy, bz + 0.08),
            rot=Vector((ux, uy, 0)).to_track_quat("Z", "Y").to_euler())
torus((0, 0, 0), 0.05, 0.011, "copper", parent=WHL, seg=32)                                # handwheel
for k in range(3):
    t = math.radians(90 + k * 120)
    box((0.025 * math.cos(t), 0.025 * math.sin(t), 0), (0.05, 0.01, 0.008), "copper", rot=(0, 0, t),
        bevel=0.0, parent=WHL)
cyl((bx_, by_, bz + 0.125), 0.02, 0.04, "brass", verts=12, bevel=0.0)                      # the vent, up
ring((bx_, by_, bz + 0.15), 0.026, 0.012, 0.012, "brass", verts=12, bevel=0.0)              # its mouth
# A repair: a plate patched over one of the hatch's segments, set slightly askew,
# its edges welded and its corners bolted.
a = math.radians(245)
pr = 0.44
PATCH = empty("patch", loc=(*on_body(a, pr, 0)[:2], domez(pr) + 0.006), rot=(0, 0, a + math.radians(14)))
box((0, 0, 0), (0.16, 0.13, 0.012), "patch", bevel=0.004, parent=PATCH)
for sx in (-1, 1):
    for sy in (-1, 1):
        rivet((sx * 0.06, sy * 0.045, 0.008), 0.012, parent=PATCH)
for sy in (-1, 1):
    box((0, sy * 0.068, 0.0), (0.18, 0.02, 0.016), "seam", bevel=0.005, parent=PATCH)
for sx in (-1, 1):
    box((sx * 0.083, 0, 0.0), (0.02, 0.15, 0.016), "seam", bevel=0.005, parent=PATCH)

# 6. The radiator stacks: one in each corner niche but the south-east, set across the
# diagonal. Bulky, as the adopted plate draws them (Liam, 2026-10-08): one wide column
# of flat oval fins stacked up a core -- through this camera a heavy coil -- gripped
# top and foot by brass collars, between two steel posts, on a foot block on the
# ground, and bracketed from its posts back to the hull's chamfer. Its loop is in 7.
SZ = 0.55                                         # the bank's middle height
RZ0, RZ1 = 0.12, 1.1                              # the collars, foot and top
FA, FB = 0.21, 0.1                                # a fin: half its width across the diagonal, half its depth
STACKS = []
for cx in (-1, 1):
    for cy in (-1, 1):
        if (cx, cy) == (1, -1):
            continue                              # the south-east niche is the pump's (6b.)
        d = math.atan2(cy, cx)
        px, py = cx * 1.16, cy * 1.16
        t = d + math.pi / 2                       # across the diagonal
        tx, ty = math.cos(t), math.sin(t)
        dx, dy = math.cos(d), math.sin(d)
        STACKS.append((cx, cy, px, py, d))
        box((px, py, 0.04), (0.64, 0.3, 0.08), "hull", rot=(0, 0, t), bevel=0.012)                 # foot block
        oval((px, py), 0.12, 0.055, t, (RZ0 + RZ1) / 2, RZ1 - RZ0, "steel")                       # core
        n = 16                                    # open enough that light reaches between the fins
        for i in range(n):
            oval((px, py), FA, FB, t, RZ0 + 0.06 + i * (RZ1 - RZ0 - 0.12) / (n - 1), 0.024, "radiator")  # fins
        for zc in (RZ0, RZ1):                     # collars: a brass band round a steel cap
            oval((px, py), FA + 0.004, FB + 0.004, t, zc + 0.012, 0.05, "steel", bevel=0.01)
            oval((px, py), FA + 0.02, FB + 0.02, t, zc - 0.006, 0.045, "brass", bevel=0.008)
        for k in range(10):                       # the top cap's bolts, and its bleed plug
            u = 2 * math.pi * k / 10
            rivet((px + (FA - 0.035) * math.cos(u) * tx - (FB - 0.03) * math.sin(u) * ty,
                   py + (FA - 0.035) * math.cos(u) * ty + (FB - 0.03) * math.sin(u) * tx, RZ1 + 0.038), 0.012)
        cyl((px, py, RZ1 + 0.05), 0.03, 0.03, "brass", verts=6, bevel=0.004)
        for sd in (-1, 1):                        # the posts, ground to above the top collar
            qx, qy = px + sd * 0.29 * tx, py + sd * 0.29 * ty
            box((qx, qy, 0.65), (0.055, 0.09, 1.22), "steel", rot=(0, 0, t), bevel=0.01)
            for zc in (RZ0, RZ1):                 # each collar's lug, bolted to the post
                box((px + sd * 0.25 * tx, py + sd * 0.25 * ty, zc), (0.08, 0.06, 0.05), "brass",
                    rot=(0, 0, t), bevel=0.006)
                rivet((qx, qy, zc + 0.03), 0.014)
            box((qx - 0.18 * dx, qy - 0.18 * dy, 0.9), (0.36, 0.045, 0.045), "steel", rot=(0, 0, d),
                bevel=0.008)                      # bracket back to the chamfer
        box((px, py, 1.27), (0.64, 0.08, 0.05), "steel", rot=(0, 0, t), bevel=0.01)                # top rail
        if cy > 0:                                # the lifting lugs, on the hull's back corners
            # beside the corner, the other side from the loop's nozzle (7.)
            sl = -min((-1, 1), key=lambda k: py + k * 0.15 * ty)
            lx, ly = cx * 0.84 + sl * 0.1 * tx, 0.84 + sl * 0.1 * ty
            box((lx, ly, PZ + 0.04), (0.14, 0.14, 0.08), "brass", bevel=0.012)
            # upright, the eye's plane along the corner's diagonal, so it draws at the
            # camera's angle like the rest of the machine (Liam, 2026-10-08: facing the
            # camera head-on, the eyes stuck up at an off angle)
            lug = empty("lug", loc=(lx, ly, PZ + 0.18), rot=(math.pi / 2, 0, math.atan2(ly, lx)))
            box((0, -0.07, 0), (0.18, 0.14, 0.06), "steel", bevel=0.014, parent=lug)
            torus((0, 0.03, 0), 0.075, 0.035, "steel", parent=lug, seg=32)

# 6b. The vacuum pump, in the south-east niche (the corner triangle outside the
# hull's chamfer), as blockout revision 4 has it. A barrel in the hull's paint stands
# at the back of the niche on a foot; its suction line runs into the chamfer.
BX, BY, BR, BH = 1.24, -1.06, 0.17, 0.62
box((BX, BY, 0.035), (0.32, 0.32, 0.07), "steel", rot=(0, 0, math.radians(45)), bevel=0.012)  # foot: its corner at x 1.47, inside the footprint
for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    rivet((BX + 0.1 * (sx - sy) * 0.707, BY + 0.1 * (sx + sy) * 0.707, 0.072), 0.016)
cyl((BX, BY, 0.07 + BH / 2), BR, BH, "hull", verts=48, bevel=0.012)                          # barrel
cyl((BX, BY, 0.07 + BH + 0.025), BR + 0.025, 0.05, "steel", verts=48, bevel=0.01)          # its head
for k in range(8):
    a = 2 * math.pi * k / 8
    rivet((BX + (BR + 0.012) * math.cos(a), BY + (BR + 0.012) * math.sin(a), 0.07 + BH + 0.052), 0.012)
for zr in (0.22, 0.52):
    torus((BX, BY, zr), BR + 0.006, 0.015, "seam", seg=48)                                 # barrel bands
SUCK = empty("suction", loc=(BX - 0.2, BY + 0.2, 0.5), rot=(0, math.pi / 2, math.radians(135)))
cyl((0, 0, 0), 0.055, 0.26, "steel", verts=24, parent=SUCK)                                 # suction line
ring((0, 0, -0.1), 0.075, 0.05, 0.03, "steel", parent=SUCK, verts=24)                        # its flange
# The flywheel (spec 6): upright on a level north-south shaft in front of the
# barrel, facing south, so it draws as an ellipse half as tall as it is wide, at the
# camera's angle like the rest of the machine (Liam, 2026-10-08: a wheel facing the
# camera head-on looked pasted on). Heavy: a deep flat-faced rim, where a flywheel
# keeps its mass, and six short thick spokes. Free all round -- nothing touches its
# rim; behind it the shaft runs north into its drive motor, butted against the
# barrel. Its own group: the plate leaves it out and the frames draw it.
WX, WY, WZ, WR = 1.0, -1.32, 0.3, 0.26
HUB = 0.065
WHEEL_AXIS = empty("wheel-axis", loc=(WX, WY, WZ), rot=(math.pi / 2, 0, 0))   # local Z points south
WHEEL = empty("wheel", parent=WHEEL_AXIS)            # spins about its local Z, the shaft
cyl((0, 0, -0.1), 0.03, 0.14, "steel", verts=24, bevel=0.0, parent=WHEEL_AXIS)            # shaft
cyl((0, 0, -0.26), 0.1, 0.18, "hull", verts=32, bevel=0.012, parent=WHEEL_AXIS)            # drive motor
ring((0, 0, -0.17), 0.105, 0.04, 0.02, "steel", parent=WHEEL_AXIS, verts=32)               # its end plate
for k in range(4):
    t = 2 * math.pi * k / 4 + math.pi / 4
    rivet((0.078 * math.cos(t), 0.078 * math.sin(t), -0.158), 0.012, parent=WHEEL_AXIS)
box((0, -0.2, -0.26), (0.16, 0.2, 0.16), "steel", bevel=0.008, parent=WHEEL_AXIS)         # motor pedestal, to the ground
ring((0, 0, 0), WR, WR - 0.065, 0.085, "rim", group="flywheel", parent=WHEEL, verts=64)    # rim, machined bright
for k in range(6):                                                                         # spokes
    a = 2 * math.pi * k / 6
    L = WR - 0.06 - HUB + 0.02
    rr = HUB - 0.01 + L / 2
    box((rr * math.cos(a), rr * math.sin(a), 0), (L, 0.05, 0.045), "wheel", group="flywheel",
        rot=(0, 0, a), bevel=0.008, parent=WHEEL)
cyl((0, 0, 0), HUB, 0.1, "wheel", group="flywheel", verts=32, bevel=0.01, parent=WHEEL)     # hub
rivet((0, 0, 0.052), 0.024, group="flywheel", parent=WHEEL)                                # the shaft's nut
# the suction line's valve: a flange at the barrel's end too, and a valve body halfway,
# its stem out to the south-west and the handwheel upright on it, at the lifting eyes'
# angle like the roof's valve (Liam, 2026-10-08)
ring((0, 0, 0.11), 0.075, 0.05, 0.03, "steel", parent=SUCK, verts=24)
cyl((0, 0, 0.0), 0.075, 0.07, "steel", verts=24, bevel=0.008, parent=SUCK)
sw = math.radians(225)
vx_, vy_ = math.cos(sw), math.sin(sw)
cyl((BX - 0.2 + 0.1 * vx_, BY + 0.2 + 0.1 * vy_, 0.5), 0.012, 0.07, "steel", verts=12,
    rot=(0, math.pi / 2, sw), bevel=0.0)                                                    # stem
VALVE = empty("valve", loc=(BX - 0.2 + 0.13 * vx_, BY + 0.2 + 0.13 * vy_, 0.5),
              rot=Vector((vx_, vy_, 0)).to_track_quat("Z", "Y").to_euler())
torus((0, 0, 0), 0.045, 0.011, "brass", parent=VALVE, seg=32)                              # handwheel
for k in range(3):
    t = math.radians(90 + k * 120)
    box((0.022 * math.cos(t), 0.022 * math.sin(t), 0), (0.045, 0.009, 0.008), "brass", rot=(0, 0, t),
        bevel=0.0, parent=VALVE)
# The gauge's line: a thin brass tube from the gauge's case into the hull's chamfer,
# where the furnace's vacuum is read (Liam, 2026-10-08).
tube([(BX - 0.11, BY + 0.07, 0.07 + BH + 0.06), (BX - 0.17, BY + 0.13, 0.07 + BH + 0.03),
      wall_pt(2, 0.62, 0.07 + BH + 0.0, 0.03), wall_pt(2, 0.62, 0.07 + BH - 0.04, -0.01)], 0.016, "brass")
box(wall_pt(2, 0.62, 0.07 + BH - 0.02, 0.01), (0.05, 0.05, 0.06), "steel",
    rot=ON_CHAMFER, bevel=0.008)                                                            # its gland
# The power feed (Liam, 2026-10-08): the furnace runs on electricity, so it shows it --
# the drive motor's starter box on the south-east chamfer's upper band, square to the
# wall and leaning with it, and a conduit from it down the wall to the motor.
JB = 0.46
box(wall_pt(2, JB, 0.93, 0.045), (0.24, 0.09, 0.2), "hull", rot=ON_CHAMFER, bevel=0.012)
box(wall_pt(2, JB, 0.93, 0.093), (0.25, 0.012, 0.21), "steel", rot=ON_CHAMFER, bevel=0.004)  # its lid
for df in (-0.07, 0.07):
    for z in (0.85, 1.01):
        rivet(wall_pt(2, JB + df * 1.25 / 1.22, z, 0.1), 0.011)
tube([wall_pt(2, JB + 0.04, 0.85, 0.05), wall_pt(2, JB + 0.04, 0.6, 0.04),
      (WX + 0.02, WY + 0.3, WZ + 0.16), (WX + 0.02, WY + 0.26, WZ + 0.1)], 0.022, "steel")
box(wall_pt(2, JB + 0.04, 0.7, 0.04), (0.06, 0.03, 0.025), "brass", rot=ON_CHAMFER, bevel=0.004)  # conduit clip
# The vacuum gauge, flat on the barrel's head and facing up, at the roof's angle like
# the viewport glass: a level circle draws as a full circle through this camera, so it
# stays as readable as a dial facing the camera head-on (Liam, 2026-10-08). Set deep in
# a hooded case so it sits in shade (spec 3.2). Bare: the needle is Animatorio's.
GAUGE = empty("gauge", loc=(BX, BY, 0.07 + BH + 0.05 + 0.06))
cyl((0, 0, -0.03), 0.13, 0.06, "brass", verts=48, bevel=0.01, parent=GAUGE)                 # case
ring((0, 0, 0.02), 0.13, 0.1, 0.05, "brass", parent=GAUGE, verts=48)                        # the hood
cyl((0, 0, 0.0), 0.1, 0.004, "dial", verts=48, bevel=0.0, parent=GAUGE)                     # dial face
cyl((0, 0, 0.004), 0.012, 0.006, "steel", verts=16, bevel=0.0, parent=GAUGE)                 # the needle's pivot

# The evacuation hose: the pump draws the chamber down through a ribbed hose from a
# flanged port on the hatch -- in the middle of a segment, clear of its seams -- out
# between two dogs, over the rim and the cap rail, clipped down the south-east
# chamfer into the pump barrel's side. The port carries a rigid elbow, so the hose
# leaves it already running out across the roof.
a = math.radians(-8)
hx, hy = on_body(a, 0.45, 0)[:2]
hz0 = domez(0.45)
cyl((hx, hy, hz0 + 0.02), 0.07, 0.04, "steel", verts=24, bevel=0.008)                     # the port's flange
for k in range(6):
    t = 2 * math.pi * k / 6 + math.pi / 6
    rivet((hx + 0.055 * math.cos(t), hy + 0.055 * math.sin(t), hz0 + 0.042), 0.01)
ah = math.radians(-30)                                                                      # the hose's way out
ux, uy = math.cos(ah), math.sin(ah)
EL = (hx + 0.09 * ux, hy + 0.09 * uy, hz0 + 0.1)                                            # the elbow's mouth
tube([(hx, hy, hz0 + 0.03), (hx, hy, hz0 + 0.07), (hx + 0.04 * ux, hy + 0.04 * uy, hz0 + 0.1), EL],
     0.042, "steel")                                                                       # the rigid elbow
torus(EL, 0.044, 0.012, "brass", rot=Vector((ux, uy, 0)).to_track_quat("Z", "Y").to_euler(), seg=24)  # its clamp
HF = 0.8                                     # where it comes down the chamfer
HOSE_R = 0.044
BIN = (BX - 0.02, BY + BR + 0.05, 0.6)       # the barrel's inlet, on its north side
HOSE = [EL, (*on_body(math.radians(-22.5), 0.7, 0)[:2], H + 0.22),
        (*on_body(math.radians(-29), 1.0, 0)[:2], H + 0.17), wall_pt(2, HF, PZ + 0.07, -0.02),
        wall_pt(2, HF, HZ - 0.06, 0.05), wall_pt(2, HF, 0.86, 0.05),
        (BIN[0], BIN[1] + 0.12, BIN[2] + 0.1), (BIN[0], BIN[1] + 0.05, BIN[2])]
tube(HOSE, HOSE_R, "rubber")                  # reinforced: heavier, and rubber (round 3)
# its ribs: fine rings at an even pitch along the curve itself, square to it, clear
# of both ends' fittings
spl = PARTS["static"][-1].data.splines[0]


def _bez(p0, h0, h1, p1, t):
    u = 1 - t
    return [u ** 3 * a0 + 3 * u * u * t * b0 + 3 * u * t * t * c0 + t ** 3 * d0 for a0, b0, c0, d0 in zip(p0, h0, h1, p1)]


_pts = []
for i in range(len(spl.bezier_points) - 1):
    b0, b1 = spl.bezier_points[i], spl.bezier_points[i + 1]
    for j in range(48):
        _pts.append(_bez(b0.co, b0.handle_right, b1.handle_left, b1.co, j / 48))
_pts.append(list(spl.bezier_points[-1].co))
_s = [0.0]
for p0, p1 in zip(_pts, _pts[1:]):
    _s.append(_s[-1] + math.dist(p0, p1))
nxt = 0.05
for i in range(1, len(_pts) - 1):
    if nxt <= _s[i] <= _s[-1] - 0.05:
        nxt = _s[i] + 0.032
        d = Vector(_pts[i + 1]) - Vector(_pts[i - 1])
        torus(_pts[i], HOSE_R + 0.002, 0.007, "rubber", rot=d.normalized().to_track_quat("Z", "Y").to_euler(),
              seg=16)
# crimped ferrules at both ends, where the hose meets the elbow and the inlet
for k0, k1 in ((0, 6), (len(_pts) - 1, len(_pts) - 7)):
    a_, b_ = Vector(_pts[k0]), Vector(_pts[k1])
    ferrule(a_ + (b_ - a_).normalized() * 0.03, (b_ - a_), HOSE_R)
box(wall_pt(2, HF, PZ + 0.03, -0.03), (0.1, 0.07, 0.04), "brass", rot=(0, 0, math.radians(45)),
    bevel=0.006)                                                                             # its saddle on the rail
for z in (1.0, 0.88):                                                                       # clipped to the wall
    box(wall_pt(2, HF, z, 0.05), (0.11, 0.09, 0.03), "brass", rot=ON_CHAMFER, bevel=0.006)
    for df in (-0.05, 0.05):
        rivet(wall_pt(2, HF + df / 1.22, z, 0.012), 0.01)
# the inlet: a stub out of the barrel's side, flanged, the hose clamped onto it
cyl((BIN[0], BIN[1] - 0.02, BIN[2]), 0.045, 0.07, "steel", verts=24, rot=(math.pi / 2, 0, 0), bevel=0.0)
ring((BIN[0], BIN[1] + 0.015, BIN[2]), 0.07, 0.035, 0.025, "steel", verts=24, rot=(math.pi / 2, 0, 0))
torus((BIN[0], BIN[1] + 0.05, BIN[2]), 0.04, 0.012, "brass", rot=(math.pi / 2, 0, 0), seg=24)

# 7. The copper: a ring on the deck round the hatch, clamped down, and a feeder down
# each diagonal to its corner's stack -- none crosses a face's middle; three stacks, three feeders.
RING_R = 1.045
pts = [on_body(2 * math.pi * k / 96, RING_R, H + 0.03) for k in range(96)]
cu = bpy.data.curves.new("deckring", "CURVE")
cu.dimensions = "3D"
cu.bevel_depth = 0.026
cu.bevel_resolution = 4
sp = cu.splines.new("POLY")
sp.points.add(len(pts) - 1)
for p, co in zip(sp.points, pts):
    p.co = (*co, 1)
sp.use_cyclic_u = True
ob = bpy.data.objects.new("deckring", cu)
sc.collection.objects.link(ob)
_finish(ob, "copper", "static", bevel=0, parent=BODY)
for k in range(16):
    a = 2 * math.pi * (k + 0.5) / 16
    box(on_body(a, RING_R, H + 0.03), (0.035, 0.07, 0.065), "brass", rot=(0, 0, a), bevel=0.006, parent=BODY)
# Each stack's loop (spec 3.3: radiator loops, #6E685C), industrial pipework (Liam,
# 2026-10-08): heavy steel pipe with proper elbows, made up in flanged spools bolted
# together, and bolted to flanged nozzles standing out of the radiator's collars.
# The flow leaves the hull through a nozzle welded into the cap rail beside the corner
# -- not the copper deck ring (Liam, 2026-10-08) -- goosenecks over the rail's edge,
# drops down the chamfer on a stand-off bracket, and turns into the top collar's nozzle; the return is a short flanged spool from the foot
# collar's nozzle straight into a pad on the hull.
LOOP_R = 0.04


def flange(pos, direction, r=LOOP_R, n=6):
    """A bolted flange pair across a pipe of radius r at pos, square to direction."""
    F = empty("flange", loc=pos, rot=Vector(direction).normalized().to_track_quat("Z", "Y").to_euler())
    for z in (-0.012, 0.012):
        cyl((0, 0, z), r + 0.036, 0.02, "steel", verts=32, bevel=0.004, parent=F)
    for k in range(n):
        u = 2 * math.pi * (k + 0.5) / n
        cyl(((r + 0.024) * math.cos(u), (r + 0.024) * math.sin(u), 0), 0.009, 0.058, "steel", verts=6,
            bevel=0.0, parent=F)


def nozzle(base, direction, length, r=LOOP_R, mat="radiator"):
    """A stub out of a vessel at base along direction, its flange at the end; returns the end."""
    dv = Vector(direction).normalized()
    end = Vector(base) + dv * length
    rot = dv.to_track_quat("Z", "Y").to_euler()
    cyl(tuple((Vector(base) + end) / 2), r + 0.006, length, mat, verts=24, rot=rot, bevel=0.0)
    cyl(tuple(Vector(base) + dv * 0.012), r + 0.03, 0.024, mat, verts=24, rot=rot, bevel=0.006)  # its weld boss
    flange(tuple(end), dv, r)
    return tuple(end)


for cx, cy, px, py, d in STACKS:
    t = d + math.pi / 2
    tx, ty = math.cos(t), math.sin(t)
    dx, dy = math.cos(d), math.sin(d)
    i = {(1, 1): 4, (-1, 1): 6, (-1, -1): 0}[(cx, cy)]            # this corner's chamfer
    sd = min((-1, 1), key=lambda k: py + k * 0.15 * ty)          # the flow comes down on the camera's side
    fx, fy = px + sd * 0.15 * tx, py + sd * 0.15 * ty
    # the top collar's nozzle, facing the hull
    top = nozzle((fx - (FB + 0.015) * dx, fy - (FB + 0.015) * dy, RZ1 - 0.01), (-dx, -dy, 0), 0.07)
    ax_, ay_, _ = wall_pt(i, 0, RZ1)
    bx_, by_, _ = wall_pt(i, 1, RZ1)
    f = ((fx - ax_) * (bx_ - ax_) + (fy - ay_) * (by_ - ay_)) / ((bx_ - ax_) ** 2 + (by_ - ay_) ** 2)
    # out of the hull: a nozzle welded into the cap rail, then a gooseneck over its edge
    up = nozzle(wall_pt(i, f, HZ, -0.05)[:2] + (PZ + 0.005,), (0, 0, 1), 0.06)
    pipe([up, (up[0], up[1], PZ + 0.13), wall_pt(i, f, PZ + 0.13, 0.07), wall_pt(i, f, RZ1 - 0.01, 0.07), top],
         LOOP_R, "radiator", bend=0.09)
    flange(wall_pt(i, f, PZ - 0.06, 0.07), (0, 0, 1))                                             # a joint on the drop
    lean = (-math.atan2(LEAN, HZ), 0, d - math.pi / 2)
    box(wall_pt(i, f, 1.15, 0.03), (0.05, 0.06, 0.04), "steel", rot=lean, bevel=0.006)          # stand-off bracket
    box(wall_pt(i, f, 1.15, 0.07), (0.12, 0.1, 0.022), "steel", rot=lean, bevel=0.006)          # its strap
    # the return: the foot collar's nozzle bolted straight to a pad on the hull
    rx, ry = px - sd * 0.08 * tx, py - sd * 0.08 * ty
    foot = nozzle((rx - (FB + 0.015) * dx, ry - (FB + 0.015) * dy, RZ0 + 0.01), (-dx, -dy, 0), 0.045)
    box((foot[0] - 0.03 * dx, foot[1] - 0.03 * dy, RZ0 + 0.01), (0.03, 0.16, 0.16), "steel", rot=(0, 0, d),
        bevel=0.008)                                                                              # its pad

# 7b. Services (Liam, round 3: "add more wiring and hoses and things, to make it look
# similar to vanilla factorio assets; these look too well machined" -- and "keep the
# furnace low": everything here lies on the roof's rail, the walls or the ground, and
# nothing rises above what was already drawn). Vanilla layers its services on in
# plain view: the electromagnetic plant's slack corrugated hoses, the foundry's
# bundled cables and boxes. Nothing crosses the hatch, its dogs or the viewport.


def face_len(i, z):
    a, b = wall_pt(i, 0, z), wall_pt(i, 1, z)
    return math.hypot(b[0] - a[0], b[1] - a[1])


def on_wall(i, f, z, out):
    return Vector(wall_pt(i, f, z, out))


def wall_dir(i):
    """Face i's outward normal, level."""
    n_ = face_frame(i, 0.5, 0.6)[2]
    k = math.hypot(n_[0], n_[1])
    return Vector((n_[0] / k, n_[1] / k, 0.0))


# Round 4 (Liam: denser, higher contrast; vanilla makes its services a major part of
# the image): fewer, chunkier pieces that survive at 1x. A tray round the front of
# the rail and another round the back carry heaped four-colour bundles; a junction
# box on each side; glands and clamps at each radiator bank, with short drops into
# them; and two hoses -- the vacuum hose and a heavier one on the east -- lying on
# the roof, the rail and the walls, not hung in the air to cast black.
RAIL = octagon(ER - 0.06, CR - 0.025)          # the rail's middle line, vertex by vertex


def rail_pt(i, f, inset=0.0):
    (ax, ay), (bx, by) = RAIL[i], RAIL[(i + 1) % 8]
    p_ = Vector((ax + (bx - ax) * f, ay + (by - ay) * f, 0.0))
    return p_ - wall_dir(i) * inset


TZ = PZ + 0.022                                 # a tray's floor


def tray(path):
    """An open steel channel along the rail through path (rail-level points), on
    feet, its ends welded on."""
    for a_, b_ in zip(path, path[1:]):
        a_, b_ = Vector(a_), Vector(b_)
        mid, d_ = (a_ + b_) / 2, b_ - a_
        rot = (0, 0, math.atan2(d_.y, d_.x))
        n_ = Vector((-d_.y, d_.x, 0)).normalized()
        L_ = d_.length + 0.03
        box((mid.x, mid.y, TZ - 0.002), (L_, 0.078, 0.006), "steel", rot=rot, bevel=0.002)
        for sy in (-1, 1):
            q = mid + n_ * (sy * 0.037)
            box((q.x, q.y, TZ + 0.014), (L_, 0.006, 0.03), "steel", rot=rot, bevel=0.002)
        for k in range(max(1, int(d_.length / 0.22))):
            q = a_ + d_ * ((k + 0.5) / max(1, int(d_.length / 0.22)))
            box((q.x, q.y, PZ + 0.009), (0.03, 0.05, 0.02), "steel", rot=rot, bevel=0.003)
    for e_, o_ in ((Vector(path[0]), Vector(path[1])), (Vector(path[-1]), Vector(path[-2]))):
        d_ = (e_ - o_).normalized()
        q = e_ + d_ * 0.02
        box((q.x, q.y, TZ + 0.01), (0.024, 0.084, 0.03), "seam", rot=(0, 0, math.atan2(d_.y, d_.x)), bevel=0.004)


def in_tray(p_, dz=0.016):
    return (p_.x, p_.y, TZ + dz)


FOUR = ("cable-red", "cable-yellow", "cable-blue", "cable-green")
CR_ = 0.014                                      # a cable's radius in the heaped bundles

# Junction box 1, on a welded angle bracket on the south-west chamfer's upper plate.
J1F, J1Z = 0.9, 1.0
L0 = face_len(0, J1Z)
SW_SQUARE = (-math.atan2(LEAN, HZ), 0, math.radians(-45))        # square to face 0, leaning with it
box(tuple(on_wall(0, J1F, J1Z - 0.11, 0.035)), (0.2, 0.07, 0.02), "steel", rot=SW_SQUARE, bevel=0.004)   # bracket
box(tuple(on_wall(0, J1F, J1Z - 0.11, 0.004)), (0.22, 0.012, 0.035), "seam", rot=SW_SQUARE, bevel=0.003)  # its weld
box(tuple(on_wall(0, J1F, J1Z, 0.05)), (0.17, 0.08, 0.2), "jbox", rot=SW_SQUARE, bevel=0.01)
box(tuple(on_wall(0, J1F, J1Z, 0.093)), (0.18, 0.01, 0.21), "jbox", rot=SW_SQUARE, bevel=0.004)          # lid
for df in (-0.06, 0.06):
    for dz in (-0.08, 0.08):
        rivet(tuple(on_wall(0, J1F + df / L0, J1Z + dz, 0.1)), 0.009)
cyl(tuple(on_wall(0, J1F, J1Z + 0.11, 0.05)), 0.03, 0.03, "brass", verts=10, bevel=0.0)        # the top gland
side_gland = on_wall(0, J1F - 0.1 / L0, J1Z + 0.02, 0.05)
cyl(tuple(side_gland), 0.016, 0.03, "brass", verts=8, rot=(0, math.pi / 2, math.radians(-45)), bevel=0.0)

# The front tray: up the south-west chamfer from beyond its radiator's loop, along
# the south rail, and on round the south-east chamfer to above the starter box.
front = [rail_pt(0, 0.77), rail_pt(1, 0.0), rail_pt(2, 0.0), rail_pt(2, 0.42)]
tray(front)
SB_TOP = 0.93 + 0.1
run = [tuple(on_wall(0, J1F, J1Z + 0.13, 0.05)), tuple(on_wall(0, J1F, HZ - 0.03, 0.055)),
       tuple(on_wall(0, J1F, PZ + 0.05, 0.02)), in_tray(rail_pt(0, J1F - 0.02), 0.02),
       in_tray(rail_pt(0, 0.97)), in_tray(rail_pt(1, 0.03)), in_tray(rail_pt(1, 0.5)), in_tray(rail_pt(1, 0.97)),
       in_tray(rail_pt(2, 0.03)), in_tray(rail_pt(2, 0.36)), in_tray(rail_pt(2, 0.42), 0.03),
       tuple(on_wall(2, 0.42, PZ + 0.05, 0.03)), tuple(on_wall(2, 0.42, HZ - 0.04, 0.06)),
       tuple(on_wall(2, 0.41, 1.12, 0.05)), tuple(on_wall(2, 0.4, SB_TOP + 0.02, 0.045))]
bundle(run, FOUR, r=CR_, gap=0.026, rows=2)
# a P-clip holding the run to the south-west chamfer where it comes up to the rail
box(tuple(on_wall(0, J1F, HZ - 0.08, 0.035)), (0.1, 0.05, 0.026), "steel", rot=SW_SQUARE, bevel=0.004)

# The radiator banks' glands and clamps, each with a short drop into it. The
# south-west bank's is a clamp on its post nearest the camera, fed from junction box 1.
def stack(cx, cy):
    return next(st for st in STACKS if st[:2] == (cx, cy))


_, _, px_, py_, d_ = stack(-1, -1)
t_ = d_ + math.pi / 2
post = Vector((px_ + 0.29 * math.cos(t_), py_ + 0.29 * math.sin(t_), 1.12))
box(tuple(post), (0.09, 0.12, 0.06), "jbox", rot=(0, 0, t_), bevel=0.008)                     # the clamp
cl = post + Vector((-math.cos(d_), -math.sin(d_), 0.0)) * 0.065                                # its gland, hull-side
cyl(tuple(cl), 0.018, 0.035, "brass", verts=8, rot=(0, math.pi / 2, d_), bevel=0.0)
bundle(droop(side_gland + Vector((0, 0, 0.0)) - wall_dir(0) * 0.0 + wall_dir(0) * 0.02, cl, 0.03, n=4),
       ("cable-yellow", "cable-red"), r=0.013, gap=0.026, lie=(0, 0, 1))

# The back: junction box 2 on the north rail, a tray either side of it along the rail
# and round the chamfers short of the lifting lugs, and from each tray's end a drop
# out over the niche to a gland clamped on the radiator's top rail.
J2 = Vector((0.12, RAIL[5][1] - 0.02, PZ + 0.035))
box(tuple(J2), (0.22, 0.08, 0.07), "jbox", bevel=0.01)
box(tuple(J2 + Vector((0, 0, 0.037))), (0.23, 0.085, 0.008), "jbox", bevel=0.003)             # lid
for sx in (-1, 1):
    for sy in (-1, 1):
        rivet(tuple(J2 + Vector((sx * 0.09, sy * 0.028, 0.043))), 0.008)
    cyl(tuple(J2 + Vector((sx * 0.12, 0, -0.005))), 0.022, 0.03, "brass", verts=10, rot=(0, math.pi / 2, 0),
        bevel=0.0)
back_e = [Vector((J2.x + 0.14, J2.y, 0)), rail_pt(4, 1.0), rail_pt(4, 0.78)]
back_w = [Vector((J2.x - 0.14, J2.y, 0)), rail_pt(5, 0.0), rail_pt(6, 0.22)]
tray(back_e)
tray(back_w)
for side, path, (cx, cy), i_, f_ in ((1, back_e, (1, 1), 4, 0.78), (-1, back_w, (-1, 1), 6, 0.22)):
    _, _, px_, py_, d_ = stack(cx, cy)
    top = Vector((px_, py_, 1.27 + 0.025))
    box(tuple(top + Vector((0, 0, 0.012))), (0.1, 0.11, 0.024), "jbox", rot=(0, 0, d_ + math.pi / 2),
        bevel=0.005)                                                                            # the clamp
    gl_ = top + Vector((0, 0, 0.035))
    cyl(tuple(gl_), 0.022, 0.03, "brass", verts=10, bevel=0.0)                                  # its gland
    ends_ = [Vector((J2.x + side * 0.135, J2.y, 0))] + path[1:]
    pts_ = [in_tray(ends_[0], 0.02)] + [in_tray(p_) for p_ in ends_[1:-1]] + [in_tray(ends_[-1], 0.03)]
    out_ = Vector(wall_pt(i_, f_, PZ + 0.04, 0.04))
    # Muted (Liam, round 4b): at 1x a four-colour bundle here drew a striped line along
    # the top of the silhouette that read as trim. Two dark cables, one of them a
    # dull blue-grey, lying low in the tray so its dark steel sides show more than
    # they do, held down by straps.
    bundle(pts_ + [tuple(out_)] + droop(out_, gl_ + Vector((0, 0, 0.03)), 0.04, n=4)[1:],
           ("cable-black", "cable-grey") if side > 0 else ("cable-grey", "cable-muted"), r=0.012, gap=0.026,
           ties=1.0)
    for a_, b_ in zip(path, path[1:]):
        a_, b_ = Vector(a_), Vector(b_)
        d_ = b_ - a_
        k_ = max(1, int(d_.length / 0.14))
        for j in range(1, k_ + 1):
            q = a_ + d_ * (j / (k_ + 1))
            box((q.x, q.y, TZ + 0.034), (0.022, 0.086, 0.008), "steel", rot=(0, 0, math.atan2(d_.y, d_.x)),
                bevel=0.002)                                                                   # a strap

# The starter box's own cables: glands under it either side of the conduit, a slack
# pair down to the drive motor, and a yellow instrument cable to the gauge's hood.
L2 = face_len(2, 0.83)
gl = [on_wall(2, JB + df / L2, 0.815, 0.05) for df in (-0.09, -0.045, 0.11)]
for g_ in gl:
    cyl(tuple(g_), 0.015, 0.03, "brass", verts=8, bevel=0.0)
motor = Vector((WX - 0.06, WY + 0.26, WZ + 0.095))
m0 = (gl[0] + gl[1]) / 2 + Vector((0, 0, -0.02))
bundle([tuple(m0), tuple(m0 + Vector((0.01, -0.01, -0.12))),
        tuple((m0 + motor) / 2 + Vector((-0.03, -0.03, -0.04))), tuple(motor + Vector((0, 0, 0.04))),
        tuple(motor)], ("cable-red", "cable-black"), r=0.014, gap=0.028, lie=tuple(wall_dir(2)))
gauge = Vector((BX - 0.12, BY - 0.07, 0.07 + BH + 0.12))
bundle(droop(gl[2] + Vector((0, 0, -0.02)), gauge, 0.015, n=4), ("cable-yellow",), r=0.014, lie=(0, 0, 1))

# The east hose: heavier than the vacuum hose, from a flanged stub standing on the
# east rail, lying along the rail southward, over the rail's edge at the south-east
# chamfer's end, down that wall beside the vacuum hose, and into the pump barrel's
# north-east side.
ER_R = 0.052
stub = rail_pt(3, 0.82)
nozzle((stub.x, stub.y, PZ - 0.005), (0, 0, 1), 0.05, r=0.036, mat="steel")
bd = Vector((math.cos(math.radians(50)), math.sin(math.radians(50)), 0.0))
be = Vector(nozzle(tuple(Vector((BX, BY, 0.5)) + bd * (BR - 0.01)), tuple(bd), 0.03, r=0.036, mat="steel"))
hz = PZ + ER_R + 0.008
hose([(stub.x, stub.y, PZ + 0.09), (stub.x, stub.y - 0.06, hz + 0.01), tuple(rail_pt(3, 0.45) + Vector((0, 0, hz))),
      tuple(rail_pt(3, 0.08) + Vector((0, 0, hz))), tuple(rail_pt(2, 0.93) + Vector((0, 0, hz))),
      tuple(on_wall(2, 0.93, PZ + 0.02, ER_R + 0.01)), tuple(on_wall(2, 0.93, 0.95, ER_R + 0.008)),
      tuple(on_wall(2, 0.93, 0.68, ER_R + 0.01)), tuple(be + bd * 0.05 + Vector((0, 0.04, 0.06))),
      tuple(be + bd * 0.03)], ER_R)
for z_ in (1.02, 0.78):                                                                       # its wall clips
    box(tuple(on_wall(2, 0.93, z_, 0.02)), (0.13, 0.04, 0.03), "steel", rot=ON_CHAMFER, bevel=0.005)

# Less machined (round 3): a mismatched newer plate bolted over the south-west
# chamfer's lower course beside the south corner, a little askew, and oil soaked into
# the ground under the pump.
wall_strip(0, 0.86, 0.19, 0.1, 0.42, 0.014, "newplate", group="hull")
for df in (-0.075, 0.075):
    for z in (0.14, 0.38):
        rivet(tuple(on_wall(0, 0.86 + df / face_len(0, z), z + (0.01 if df > 0 else 0.0), 0.02)), 0.012)
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=1.0, depth=0.004, location=(BX - 0.1, BY - 0.12, 0.003),
                                    rotation=(0, 0, math.radians(20)))
OIL = bpy.context.active_object
OIL.scale = (0.3, 0.2, 1.0)
_finish(OIL, "oil", "static", bevel=0)


# 8. The pipe pictures: the engine draws one at whichever face the input is turned
# to. Each is a stub on the pipe's own centreline, ending in a flange the size of the
# pipe's bolted end ring, so the joint reads as pipe meeting pipe (Liam, 2026-10-02);
# in assembler 3's sheet size and shift, and its outline within 2 px of assembler 3's.
#
# The centrelines and rings are vanilla's straight pipes as the engine draws them in
# the tile the input points into (base/graphics/entity/pipe, 128 px at scale 0.5,
# centred on the tile; measured on the opaque body, the painted-in shadow left out):
#   horizontal (east, west): axis 1.0 px above the tile's centre; body 40 px tall,
#                            the bolted end ring 52 px tall at the tile's edge
#   vertical (north, south): axis 0.5 px right of the tile's centre; body 39 px wide,
#                            the end ring 51 px wide
# A flange is a disc square to its pipe: one across a horizontal pipe shows 1.118 r
# above and below its axis on the screen (r along y, r/2 of height), one across a
# vertical pipe r either side and r/2 above and below.
#
# Behind each stub stands its backplate: a slab of quads, one per pixel assembler
# 3's picture draws (alpha over 127), laid where the engine puts that pixel, in a
# plane that maps the screen to the model one to one -- the wall the stub comes out
# of, in vanilla's outline. The stub and its flanges stand in front of it.
import re  # noqa: E402

VANILLA = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/assembling-machine-3")
OUTSIDE = {"N": (0, -2), "E": (2, 0), "S": (0, 2), "W": (-2, 0)}     # the tile each turn points into
H_AXIS_V = 1.0 / 64          # horizontal pipe: axis, screen tiles above its tile's centre
V_AXIS_U = 0.5 / 64          # vertical pipe: axis, screen tiles right of its tile's centre
H_RING_R = 26 / 64 / 1.118   # a flange that shows 52 px tall across a horizontal pipe: 0.363
V_RING_R = 25.5 / 64         # a flange that shows 51 px wide across a vertical pipe: 0.398
ZA = 0.62                    # the stubs' axis height


def vanilla_mask(face):
    """Assembler 3's picture for `face`: its drawn pixels (alpha over 127) as (i, j),
    j down from the top, and the screen px of its top-left corner from the origin."""
    stem = os.path.join(VANILLA, f"assembling-machine-3-pipe-{face}")
    bx, by = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)",
                                           open(stem + ".lua").read()).groups())
    img = bpy.data.images.load(stem + ".png", check_existing=True)
    w, h = img.size
    px = list(img.pixels)
    drawn = {(i, j) for j in range(h) for i in range(w) if px[((h - 1 - j) * w + i) * 4 + 3] > 127 / 255}
    tx, ty = OUTSIDE[face]
    return drawn, (tx + bx / 32) * 64 - w / 2, (ty + by / 32) * 64 - h / 2


def slab(face, lift, mat):
    """The backplate: a quad per drawn pixel, its corners lifted into the model by
    `lift(u, v)` (screen tiles, u right, v up). Its own group, so the stub can be
    rendered without it to measure."""
    drawn, x0, y0 = vanilla_mask(face)

    def build(bm):
        corners = {}

        def corner(i, j):
            if (i, j) not in corners:
                corners[(i, j)] = bm.verts.new(lift((x0 + i) / 64, -(y0 + j) / 64))
            return corners[(i, j)]
        for i, j in drawn:
            bm.faces.new((corner(i, j + 1), corner(i + 1, j + 1), corner(i + 1, j), corner(i, j)))
    return mesh_object(f"slab-{face}", build, mat, f"slab-{face}", bevel=0)


def fitting_S():
    g = "port-S"
    k = LEAN / HZ + 0.5                              # screen v per unit height on the face

    def lift(u, v):
        z = (v + E + 0.035) / k
        return Vector((u, -E + LEAN * z / HZ - 0.035, z))
    slab("S", lift, "shell")                        # the wall it stands in front of, bands and all

    def face_pt(x, z, out=0.0):
        return (x, -E + LEAN * z / HZ - out, z)
    for k_ in range(13):                             # bolts round the plate's edge
        rivet(face_pt(-0.36 + 0.72 * k_ / 12, 1.06, 0.045), 0.017, group=g)
    for z in (0.35, 0.6, 0.85):
        for x in (-0.41, 0.41):
            rivet(face_pt(x, z, 0.045), 0.017, group=g)
    x = V_AXIS_U                                     # on the vertical pipe's centreline
    yf = -E + LEAN * ZA / HZ - 0.035
    ax = (math.pi / 2, 0, 0)
    ring((x, yf - 0.03, ZA), 0.44, 0.33, 0.05, "steel", g, rot=ax, bevel=0.01)          # wall flange
    for k_ in range(16):
        t = 2 * math.pi * k_ / 16
        rivet((x + 0.39 * math.cos(t), yf - 0.06, ZA + 0.39 * math.sin(t)), 0.016, group=g)
    # the stub, out to a closed end disc the width of the pipe's end ring, its face
    # landing where assembler 3's does (widest at v -1.47 to -1.53)
    YE = -1.53 - ZA / 2
    cyl((x, (yf + YE) / 2, ZA), 0.33, yf - YE, "steel", g, verts=64, rot=ax, bevel=0.0)
    cyl((x, YE + 0.03, ZA), V_RING_R, 0.06, "steel", g, verts=64, rot=ax, bevel=0.012)        # closed disc
    cyl((x, YE - 0.002, ZA), V_RING_R - 0.035, 0.006, "drum", g, verts=64, rot=ax, bevel=0.0)  # its painted face


SIDE = {"E": dict(sign=1, x_plate=1.22), "W": dict(sign=-1, x_plate=-1.2)}


def fitting_side(face):
    """East or west: a dark backplate, a neck, and an end flange the height of the
    horizontal pipe's end ring, all on the pipe's centreline; the flange's outer face
    on the footprint edge, where the pipe's ring meets it."""
    p = SIDE[face]
    g, sign = f"port-{face}", p["sign"]
    x0 = p["x_plate"]

    def lift(u, v):
        z = ZA - sign * 1.6 * (u - x0)
        return Vector((u, v - z / 2, z))
    slab(face, lift, "hull")                        # the hull's dark paint: vanilla's side plate is dark
    ya = H_AXIS_V - ZA / 2                          # the axis lands on the pipe's, on the screen
    ax = (0, math.pi / 2, 0)
    t = 0.045
    xf = sign * (1.5 - t / 2)
    cyl(((x0 + xf) / 2, ya, ZA), 0.24, abs(xf - x0), "steel", g, verts=64, rot=ax, bevel=0.0)  # neck
    cyl((xf, ya, ZA), H_RING_R, t, "steel", g, verts=64, rot=ax, bevel=0.008)                  # end flange
    cyl((xf - sign * (t / 2 + 0.01), ya, ZA), H_RING_R - 0.04, 0.02, "steel", g, verts=64, rot=ax, bevel=0.004)
    for k in range(12):
        a = 2 * math.pi * k / 12
        rivet((xf - sign * (t / 2 + 0.02), ya + 0.3 * math.cos(a), ZA + 0.3 * math.sin(a)), 0.015, group=g)


def fitting_N():
    """North: a flange the width of the vertical pipe's end ring, on its centreline,
    facing the camera's way; the engine draws it behind the hull."""
    g = "port-N"
    yN, zN = 1.2, 0.62
    v0 = yN + zN / 2

    def lift(u, v):
        b = v - v0
        return Vector((u, yN + 0.6 * b, zN + 0.8 * b))
    slab("N", lift, "steel")
    ax = (math.pi / 2, 0, 0)
    # Thin, as vanilla's ring is, and leant back 7.7 degrees: assembler 3 draws this
    # ring 16 px tall above its widest row, which a disc square to the pipe shows as
    # 12.7 (r/2) -- leant back, its upper half reads r(sin 7.7 + cos 7.7 / 2) = 0.25
    # tiles. Centred at v 1.544 its top lands on assembler 3's (v 1.81) and it is
    # widest where assembler 3's is (v 1.56).
    phi = math.radians(7.7)
    cyl((V_AXIS_U, 1.544 - ZA / 2, ZA), V_RING_R, 0.04, "steel", g, verts=64,
        rot=(math.pi / 2 - phi, 0, 0), bevel=0.008)
    ys = 1.544 - ZA / 2 - 0.025
    for k in range(16):
        a = 2 * math.pi * k / 16
        rivet((V_AXIS_U + 0.34 * math.cos(a), ys - 0.005, ZA + 0.34 * math.sin(a)), 0.015, group=g)


# ---------------------------------------------------------------- passes

rig.sun()
# The shadows lifted (Liam, 2026-10-08): the warm fill at 0.26, so the walls turned
# from the sun -- the south-east chamfer, the radiator niches -- stay coloured instead
# of crushing to black. The rig's own default since dec5a59, so this changes nothing.
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.26
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()

if PORTS:
    fitting_S()
    fitting_side("E")
    fitting_side("W")
    fitting_N()


def setup(visible=(), catchers=(), holdouts=(), ground=False):
    """Per pass: which groups the camera sees, catch shadow on, or cut out."""
    for g, objs in PARTS.items():
        for o in objs:
            o.hide_render = g not in visible and g not in catchers and g not in holdouts
            o.is_shadow_catcher = g in catchers
            o.is_holdout = g in holdouts
            o.visible_camera = True
    GROUND.hide_render = not ground
    BOUNCE.hide_render = ground


for o in PARTS["port"]:
    # the glass lights nothing: its glow stays inside the viewport (3.3, one circle)
    for prop in ("visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
        setattr(o, prop, False)

if PORTS:
    contract.declare(OUT_DIR, canvas=PORT_CANVAS, **DECL)
    rig.camera(*PORT_CANVAS)
    for f in FACES:
        setup(visible=(f"port-{f}", f"slab-{f}"))
        rig.render(f"{OUT_DIR}/port-{f}.png")
        setup(visible=(f"port-{f}",))              # the stub alone, to measure its axis and flange
        rig.render(f"{OUT_DIR}/axis-{f}.png")
    sys.exit(0)

# Through the contrast look anything much above this clips the glass to white.
GLOW = 1.2


def glow(on):
    M["port"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = \
        GLOW if on else 0.0


STATIC = ("static", "hull", "port")
MOVING = ("flywheel",)

if ICON:
    sc.cycles.samples = 128
    cam = rig.camera(1024, 1024, centre_px=(512, 500), ss=1)
    cam.data.ortho_scale = 3.7
    setup(visible=STATIC + MOVING)
    glow(True)
    rig.render(f"{OUT_DIR}/icon.png")
    sys.exit(0)

contract.declare(OUT_DIR, canvas=CANVAS, **DECL)
rig.camera(*CANVAS)


def indicator_cut(on):
    """The viewport glass as the light pass wants it: lit white, for the engine to tint."""
    t = M["port"].node_tree
    t.nodes["white"].outputs[0].default_value = 1.0 if on else 0.0
    t.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.0 if on else 0.0


FLY = DECL["animations"][0]

for d in contract.each_direction(ROOT, DECL["directions"]):
    def path(stem, d=d):
        return f"{OUT_DIR}/{contract.named(stem, d)}.png"
    sc.render.use_border = False
    WHEEL.rotation_euler.z = 0.0

    # the plate leaves the flywheel out: the engine draws it, frame by frame, over
    # the barrel and niche it uncovers
    setup(visible=STATIC)
    glow(False)
    rig.render(path("idle"))
    glow(True)
    rig.render(path("working"))
    glow(False)
    if IDLE:
        break
    # the stopped machine in one render, the flywheel at frame 0: what pack.py holds
    # idle + flywheel-00 to
    setup(visible=STATIC + MOVING)
    rig.render(path("still"))

    setup(visible=STATIC + MOVING, ground=True)
    for o in [o for objs in PARTS.values() for o in objs]:
        o.visible_camera = False
    rig.render(path("shadow"))

    # the indicator: the viewport glass alone, white, everything in front of it cut out
    setup(visible=("port",), holdouts=("static", "hull") + MOVING)
    indicator_cut(True)
    rig.render(path("indicator"))
    indicator_cut(False)

    # the flywheel: 16 frames through 60 degrees (its six spokes), its own shadow
    # caught on the barrel and niche behind it; only that window changes, so only it
    # is rendered
    setup(visible=MOVING, catchers=STATIC)
    sc.render.use_border = True
    sc.render.use_crop_to_border = False
    sc.render.border_min_x, sc.render.border_max_x = 0.55, 0.9
    sc.render.border_min_y, sc.render.border_max_y = 0.06, 0.45
    for f in range(FLY["frames"]):
        WHEEL.rotation_euler.z = -math.radians(60 / FLY["frames"] * f)
        rig.render(path(contract.frame(FLY["name"], f)))
    WHEEL.rotation_euler.z = 0.0
    sc.render.use_border = False
