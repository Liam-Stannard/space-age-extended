"""Drop crusher (sae-drop-crusher), built from its spec, rendered in every pass.

  blender -b --python drop_crusher.py -- <out-dir> [--idle | --icon]
  tools/blender/render.sh concept/drop-crusher/model/drop_crusher.py <out-dir> --icon

  --idle   idle.png and still.png only: the quick loop
  --icon   icon.png: the whole machine, its crown standing proud of its collar (spec 16)

The design is the adopted Sealed Hammer (concept/drop-crusher/adopted/A-sheet.png,
graphics/entity/drop-crusher/base.png); spec 3.2 the parts, 3.3 the palette, 9 the
stroke. The task: .claude/tasks/drop-crusher-model.md.

  - an armoured cylinder filling most of the footprint, nearly straight-sided (R 1.28
    at the base plate to 1.22 at the roof), 1.74 tall, 0.12 south of centre: the
    machine draws 3.56 tiles tall with the crown seated (round 3: round 2's 2.96-tall
    tower drew 4.1 and towered over its neighbours), in 16 staves and three courses,
    each plate its own object and so its own tone, the courses banded and
    double-riveted, the joints the camera sees strapped steel and copper by turns,
    copper clips over the bands, a bolted foot skirt;
  - a square base plate in worn steel showing only as a lip, its hazard band (3.3:
    the base plate's edge only) a narrow worn strip on the front edge and the front
    halves of the sides, broken by the buttresses' feet;
  - four buttresses on the diagonals, tight to the wall and flared into it, tapered,
    a weld seam down and across each, copper bands, angle iron worn bright on their
    corners, worn-steel caps and a lifting eye upright on each;
  - a slim pier off the east and west sides under each motor (the plate's shoulders);
  - the roof a crowded working deck in the hull's dark paint (round 3): riveted
    radial welds, a bolted ring round the collar, a worn kerb round its edge, an
    inspection plate, a repair patch, a lubricator with grease lines to the bearings,
    a junction box with conduits to the motors, grease and scuffs;
  - the collar: a hard machined neck at the roof's centre, its rim polished by the
    crown landing on it (3.3's palest note), bolted flanges at its foot and head and a
    copper band, slotted east and west where the gears reach the racks (its front rim
    whole), the trip pawl's window south-south-east;
  - the weight: an octagonal crown on a shank in forged steel (its own material, not
    the layered finish), the shank cut with racks east and west for the gears and a
    deep ratchet on its south face for the pawl;
  - the lift gear: two big gears (pitch radius 0.46) squarely east and west of the
    collar on the roof, upright in the east-west plane, faces to the camera: five
    spokes, lightening holes, a keyed boss, teeth worn bright; on pillow blocks; each
    driven through a flanged coupling by a pinion meshing 30 degrees below its level,
    off a finned geared motor at the roof's edge on its pier;
  - the trip pawl: a sprung lever hung off the collar on a cheek bracket, its nose
    through the collar's window on the ratchet;
  - the armoured inspection hatch with eight locking dogs on the south face, and the
    status lamp: round 10, a caged lamp on the kerb at the south-east (its old boss
    on the wall above the hatch blanked off);
  - copper and brass as the plate uses them, rust run down from every band and
    fitting, ground dirt at the foot, scuffs, a repair patch, a maker's plate.
Round 4, finish (2026-10-08): the collar worked outside (a heavy riveted head flange
with a lip worn bright, a copper band and a riveted steel band, a weld seam, rust run
down it) and a pale guide bushing in its bore -- its height is fixed by the crown-
clearance assert and the gears' clearance over the roof (rim 0.84 above the roof, the
least is 0.83); the deck's grain calmed; bright worn steel, diffuse rather than
metallic so it reads at this camera, on the gear teeth, the kerb's lip, the ring plate
round the collar and the lifting eyes; copper course bands, a copper lip band and a
clamped copper ring main on the deck; each buttress panelled its own way; the pawl
moved south of the collar, clear of the east gear's face.
Round 5: the kerb, the ring plate round the collar and the lifting eyes back to mid
steel (the furnace's rail), worn bright only in short broken arcs at the front and the
corners and on the eyes' top edges; the crown mostly diffuse with a wide bright bevel,
so its facets separate at 1x; the wall's rust warmer (materials.py's opt-in rust_tint)
and run in streaks from the bands and rivet rows rather than laid on more thickly.
No output chute, no glow, no pipe (spec 8).

The stroke (spec 9, the task): one animation layer, `stroke`, 24 frames -- the
weight, the gears, the pinions, the pawl and its spring, their shadows caught on
the plate. Frame 0 is the crown seated on the collar, pawl engaged. Frames 0-16
wind it up at constant speed, the gears turning; at 16 the pawl kicks clear; 17-23
fall with the distance going as t^2, so each frame's travel is larger than the
last, and the loop lands back on frame 0, seated, hard. The gears stay meshed:
their angle is the rack's travel over their pitch radius in every frame, so they
spin back fast as it falls.

Units are tiles; north is +Y. A model point (x, y, z) lands on screen at
(x, y + z/2) tiles from the origin.
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))

import rig  # noqa: E402
import contract  # noqa: E402
from materials import layered, hazard_pattern  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = argv[0]
os.makedirs(OUT_DIR, exist_ok=True)
ICON = "--icon" in argv
IDLE = "--idle" in argv


def swatch(name):
    """This building's concept swatches: swatches/bake_concept.py."""
    return os.path.join(HERE, "swatches", f"concept_{name}.png")


# ---------------------------------------------------------------- the stroke

FRAMES = 24
RISE = 16                          # frames 0..16 wind it up; 16 is the top, where the pawl trips
TRAVEL = 0.70                      # tiles of lift: 22.4 px on the screen
FALL = FRAMES - RISE               # 8 frames from the top back to the seat


def lift(f):
    """The weight's height above its seat in frame f (tiles)."""
    f %= FRAMES
    if f <= RISE:
        return TRAVEL * f / RISE
    k = (f - RISE) / FALL                 # 0 at the top .. 1 at the seat (frame 24 = 0)
    return TRAVEL * (1 - k * k)


def tripped(f):
    """The pawl is clear of the ratchet from the top of the stroke until the seat."""
    return RISE <= f % FRAMES < FRAMES


PATH = [[0.0, 0.0, round(lift(f), 6)] for f in range(FRAMES)]

CANVAS = (320, 304)                # entity origin at (160, 152); the shadow reaches east
DECL = dict(
    footprint=(3, 3),
    directions="one",              # spec 5: north only
    passes=[
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="still", kind="still"),
        dict(name="shadow", kind="shadow", sheet="base-shadow"),
        dict(name="lamp", kind="light", sheet="status-lamp"),
    ],
    # the slide is measured on the crown and shank alone (contract: track), rendered as
    # stroke-crown-NN: the layer's own centroid is the gears' and the pawl's as well
    animations=[dict(name="stroke", frames=FRAMES, motion="slide", path=PATH, track="crown")],
    ports=[],
)

sc = rig.reset()
ROOT = rig.turntable(rig.stretch_root())

# ---------------------------------------------------------------- materials

def stripes(g):
    """Hazard stripes at 45 degrees, 0.07 tiles each, #C8A23A on a dark ground, their
    edges chipped by noise: the adopted plate's banding, not the photo's fine tape."""
    pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
    xyz = g.node("ShaderNodeSeparateXYZ", Vector=pos)
    u = g.math("ADD", xyz.outputs["X"], xyz.outputs["Y"])
    u = g.math("ADD", u, g.math("MULTIPLY", g.noise(pos, 40, detail=2), 0.03))
    f = g.math("FRACT", g.math("DIVIDE", u, 0.14))
    band = g.math("GREATER_THAN", f, 0.5)
    paint = g.mixc(band, rig.srgb("#C8A23A"), rig.srgb("#26221C"))
    # worn: the paint chipped back to dirty steel in patches, as a kerb is by boots and carts
    chip = g.remap(g.noise(pos, 22, detail=5, rough=0.6), 0.5, 0.62)
    return g.mixc(chip, paint, rig.srgb("#4A4036"))


def forged(name, body, edge, rough=0.42, metallic=0.6, bevel_r=0.012):
    """Forged steel for the weight: smooth, darker-mid, its bevels catching the light --
    no photo grain and no scratch mask, which read as stone at this size. Each chamfer
    facet takes the sun at its own value; the edges between them go bright."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    t = m.node_tree
    n, ln = t.nodes, t.links
    b = n["Principled BSDF"]
    geo = n.new("ShaderNodeNewGeometry")
    bev = n.new("ShaderNodeBevel")
    bev.inputs["Radius"].default_value = bevel_r
    dot = n.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    ln.new(bev.outputs[0], dot.inputs[0])
    ln.new(geo.outputs["Normal"], dot.inputs[1])
    rng = n.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = 0.995
    rng.inputs["From Max"].default_value = 0.93
    ln.new(dot.outputs["Value"], rng.inputs["Value"])
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 6.0
    noise.inputs["Detail"].default_value = 2.0
    ln.new(geo.outputs["Position"], noise.inputs["Vector"])
    tone = n.new("ShaderNodeMapRange")                      # a soft forging mottle, +-8 %
    tone.inputs["To Min"].default_value = 0.92
    tone.inputs["To Max"].default_value = 1.08
    ln.new(noise.outputs["Fac"], tone.inputs["Value"])
    mul = n.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    mul.inputs[6].default_value = rig.srgb(body)
    comb = n.new("ShaderNodeCombineColor")
    for i in range(3):
        ln.new(tone.outputs[0], comb.inputs[i])
    ln.new(comb.outputs[0], mul.inputs[7])
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    ln.new(rng.outputs[0], mix.inputs[0])
    ln.new(mul.outputs[2], mix.inputs[6])
    mix.inputs[7].default_value = rig.srgb(edge)
    ln.new(mix.outputs[2], b.inputs["Base Color"])
    rmix = n.new("ShaderNodeMix")
    rmix.data_type = "FLOAT"
    ln.new(rng.outputs[0], rmix.inputs[0])
    rmix.inputs[2].default_value = rough
    rmix.inputs[3].default_value = 0.25
    ln.new(rmix.outputs[0], b.inputs["Roughness"])
    b.inputs["Metallic"].default_value = metallic
    return m


# ---- the signature finish (spec 3.3, 2026-10-09): red-oxide primer
#
# The armour and the buttresses are painted #6E2E22 -> #8A3E2C, painted once and
# battered since: chipped through to bare steel where the machine is struck or worked
# (the buttresses' edges and angle iron, the ring of the hatch door the dogs swing
# over). The deck, the collar, the gears and the weight keep their bare-metal colours.
# Variation within it: two replacement staves in fresher primer, a few stencilled
# markings, and rust by place -- dark wet streaks run down the walls from every band,
# rivet row and fitting (the primer's own rust, tinted dark), dry orange on the tops
# (the roof deck, the caps, the base plate: their rust tinted dry).
PRIMER = ("#6E2E22", "#8A3E2C")
FRESH = ("#86392A", "#A44C36")             # the replacement staves: newer primer, a shade brighter
BARE = "#9C968C"                            # bare steel, where the primer is knocked off
WET_RUST = ("#2C1610", "#5A2C18")           # streaks below fittings, on the walls
DRY_RUST = ("#8A4A1E", "#D48C48")           # on the tops
DECK_RUST = ("#6E3A1A", "#A8642E")          # the deck's: the same dry rust, quieter, so the deck stays steel
_SIN_E = math.sin(math.radians(60.0))       # rig.ELEVATION: world Y is model Y / sin(elevation)
# the hatch's centre, in world space (section 10 asserts it against the hatch itself)
HATCH_C = (0.0, (-0.12 - (1.28 + (1.22 - 1.28) * (0.83 - 0.10) / (1.74 - 0.10))) / _SIN_E, 0.83)


def primer(lo, hi, hatch=False):
    """The primer's colour: two shades drifting across a plate, dry orange rust on any
    face turned to the sky, and (hatch) the door chipped bare in a ring under its dogs,
    which the crew knock open and shut."""
    def pat(g):
        geo = g.node("ShaderNodeNewGeometry")
        pos, normal = geo.outputs["Position"], geo.outputs["Normal"]
        col = g.mixc(g.remap(g.noise(pos, 1.7, detail=2), 0.35, 0.65), rig.srgb(lo), rig.srgb(hi))
        up = g.remap(g.node("ShaderNodeSeparateXYZ", Vector=normal).outputs["Z"], 0.55, 0.9)
        dry = g.math("MULTIPLY", up, g.remap(g.noise(pos, 9, detail=5), 0.45, 0.68), clamp=True)
        col = g.mixc(g.math("MULTIPLY", dry, 0.85), col,
                     g.mixc(g.noise(pos, 23, detail=3), rig.srgb(DRY_RUST[0]), rig.srgb(DRY_RUST[1])))
        if hatch:
            d = g.node("ShaderNodeVectorMath", Vector=pos)
            d.operation = "DISTANCE"
            d.inputs[1].default_value = HATCH_C
            dist = d.outputs["Value"]
            band = g.math("MULTIPLY", g.remap(dist, 0.2, 0.26), g.remap(dist, 0.44, 0.36))
            chips = g.math("MULTIPLY", band, g.remap(g.noise(pos, 28, detail=4, rough=0.6), 0.4, 0.5), clamp=True)
            col = g.mixc(chips, col, rig.srgb(BARE))
        return col
    return pat


def stencil_paint(g):
    """Stencilled paint, off-white, worn through to the primer in patches."""
    pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
    worn = g.remap(g.noise(pos, 40, detail=4, rough=0.6), 0.5, 0.62)
    return g.mixc(worn, rig.srgb("#D2C9B2"), rig.srgb(PRIMER[0]))


M = {
    # spec 3.3: the wall's staves in red-oxide primer (the signature finish, above); its
    # rust dark and wet, run in streaks from the copper bands, the rivet rows and the
    # fittings (the drips), with dry orange only where a face turns up
    "armour": layered("armour", PRIMER[1], metal=BARE, paint_metal=0.05, paint_rough=0.62, wear=0.6,
                      rust=0.4, rust_tint=WET_RUST, pattern=primer(*PRIMER),
                      dust=0.25, grime=0.6, ground=0.85, ground_h=0.6, jitter=0.12,
                      drips=((1.7, 0.7), (1.56, 0.35), (1.38, 0.55), (0.86, 0.35), (0.34, 0.25), (0.22, 0.12)),
                      drip=0.8),
    # the replacement staves: newer primer, less worn and less rusted than the plates round them
    "fresh": layered("fresh", FRESH[1], metal=BARE, paint_metal=0.05, paint_rough=0.55, wear=0.3,
                     rust=0.3, rust_tint=WET_RUST, pattern=primer(*FRESH),
                     dust=0.2, grime=0.6, ground=0.85, ground_h=0.6, jitter=0.06,
                     drips=((1.7, 0.5), (1.38, 0.4), (0.86, 0.25)), drip=0.7),
    # the buttresses: the same primer, struck more -- their edges chipped bare
    "buttress": layered("buttress", PRIMER[1], metal=BARE, paint_metal=0.05, paint_rough=0.62, wear=0.95,
                        rust=0.5, rust_tint=WET_RUST, pattern=primer(*PRIMER),
                        dust=0.3, grime=0.7, ground=0.85, ground_h=0.6, jitter=0.12,
                        drips=((1.5, 0.5), (1.12, 0.4), (0.78, 0.3)), drip=0.9),
    # the hatch door: the primer, chipped bare in a ring under its dogs
    "door": layered("door", PRIMER[1], metal=BARE, paint_metal=0.05, paint_rough=0.6, wear=0.8,
                    rust=0.45, rust_tint=WET_RUST, pattern=primer(*PRIMER, hatch=True),
                    dust=0.15, grime=0.7, jitter=0.06),
    "stencil": layered("stencil", "#D2C9B2", metal=BARE, paint_metal=0.05, paint_rough=0.7, wear=0.25,
                       rust=0.3, rust_tint=WET_RUST, dust=0.3, grime=0.5, jitter=0.05, pattern=stencil_paint),
    "frame": layered("frame", "#4A463F", metal="#BEB8AC", paint_metal=0.05, paint_rough=0.7, wear=0.6, rust=0.5,
                     dust=0.5, grime=0.7, swatch=swatch("frame"), swatch_gain=0.9, ground=0.8, jitter=0.12,
                     drips=((1.78, 0.6), (1.6, 0.6)), drip=0.7),
    # the roof: the hull's own paint, darker, dirty and greasy as a working deck is
    # (signature finish: the deck stays bare metal; its rust is the tops' dry orange)
    "roof": layered("roof", "#6E685C", metal="#B8B2A6", paint_metal=0.05, paint_rough=0.65, wear=0.15,
                    rust=0.5, rust_tint=DECK_RUST, swatch_gain=0.95, dust=0.2, grime=0.5, swatch=swatch("deck"), swatch_scale=2.2, jitter=0.14),
    # the base plate: worn steel, scuffed pale where it is walked on, so the corners the
    # tower shades stay steel and not black
    "plate": layered("plate", "#6A655C", metal="#C8C2B6", paint_metal=0.3, paint_rough=0.6, wear=0.6,
                     rust=0.4, rust_tint=DRY_RUST, dust=0.6, grime=0.6, swatch=swatch("deck"), swatch_gain=1.35, ground=0.4,
                     jitter=0.1),
    # mid steel, the furnace's rail: the kerb, the ring plate, the lifting eyes (round 5)
    "rail": layered("rail", "#77716A", metal="#B4AEA4", paint_metal=0.8, paint_rough=0.35,
                    wear=0.45, rust=0.25, rust_tint=DRY_RUST, dust=0.1, grime=0.5),
    # bright worn steel where real wear is: gear teeth, the kerb's lip, the lifting eyes (round 4)
    # (mostly diffuse: a metallic finish only glints at the mirror angle, which this
    # camera rarely sees, and otherwise reflects the dim sky as dark)
    "polish": layered("polish", "#CBC5BA", metal="#ECE6DA", paint_metal=0.25, paint_rough=0.38, wear=0.2,
                      rust=0.05, dust=0.05, grime=0.25, jitter=0.05),
    # the collar: the lift gear's metal, grimy, rust run down from its head flange and its band
    # (the heights are 4.'s: the head flange at ZCT - 0.08 = 2.54, the band at ZCT - 0.32 = 2.3)
    "collar": layered("collar", "#8A857C", metal="#EEE8DC", paint_metal=0.25, paint_rough=0.4, wear=0.75,
                      rust=0.35, dust=0.1, grime=0.45, swatch=swatch("gear"), swatch_gain=1.55, jitter=0.06,
                      drips=((2.54, 0.4), (2.3, 0.3)), drip=0.9),
    # the gears' housings: the collar's steel, darker (#5A554E) because their caps' tops
    # take the full sun from this camera, and smooth -- a nearly grainless swatch, little
    # wear (its scratch mask speckles) and no dust -- with grime in the corners and along
    # the bolt rows, so they read as bolted steel guides of a piece with the collar
    # (rounds 7 and 8)
    "guide": layered("guide", "#5A554E", metal="#A8A296", paint_metal=0.35, paint_rough=0.5, wear=0.12,
                     rust=0.15, dust=0.0, grime=0.9, swatch=swatch("guide"), jitter=0.04),
    # the lift gear: brighter than the armour (3.3), its teeth worn bright where they mesh
    "gear": layered("gear", "#8A857C", metal="#E8E2D6", paint_metal=0.25, paint_rough=0.38, wear=0.85,
                    rust=0.15, dust=0.1, grime=0.35, swatch=swatch("gear"), swatch_gain=1.55, jitter=0.08),
    "anvil": layered("anvil", "#A8A296", metal="#F0EAE0", paint_metal=0.95, paint_rough=0.26, wear=0.3,
                     rust=0.05, dust=0.05, grime=0.3, swatch=swatch("anvil")),
    "seam": layered("seam", "#7A7268", metal="#A49C90", paint_metal=0.7, paint_rough=0.4,
                    wear=0.3, rust=0.45, dust=0.0, jitter=0.04, ground=0.7),
    "steel": layered("steel", "#77716A", metal="#C4BEB4", paint_metal=0.8, paint_rough=0.35,
                     wear=0.5, rust=0.35, dust=0.1, grime=0.5, ground=0.7),
    "copper": layered("copper", "#8A5A32", metal="#D49450", paint_metal=0.9, paint_rough=0.36,
                      wear=0.45, rust=0.1, dust=0.15, grime=0.5, swatch=swatch("copper"), swatch_gain=1.1,
                      patina=0.3),
    "brass": layered("brass", "#9C7034", metal="#D0A864", paint_metal=0.9, paint_rough=0.36,
                     wear=0.45, rust=0.15, dust=0.15, swatch=swatch("brass")),
    # the weight: dark forged steel, its chamfers knocked bright (3.3: #2E2C29, chamfers to #6A6660)
    # (round 5: mostly diffuse, so the sun separates the facets' values at 1x, and a
    # wider, brighter bevel on the edges)
    "weight": forged("weight", "#4C4842", "#D2CCC2", rough=0.5, metallic=0.25, bevel_r=0.02),
    # a repair plate, darker and dirtier than the armour round it
    "patch": layered("patch", "#5C564D", metal="#A8A296", paint_metal=0.3, paint_rough=0.6,
                     wear=0.5, rust=0.6, dust=0.15, grime=0.9),
    # angle iron and caps on the buttresses and piers: primed with them, knocked back to
    # bare metal along every edge (signature finish: the buttress edges); their rust
    # the tops' dry orange
    "edge": layered("edge", PRIMER[1], metal="#F0EAE0", paint_metal=0.05, paint_rough=0.55,
                    wear=1.0, rust=0.35, rust_tint=DRY_RUST, pattern=primer(*PRIMER), dust=0.2, grime=0.5,
                    ground=0.7),
    # bare steel, scuffed bright where boots and tools have rubbed the paint off
    "scuff": layered("scuff", "#8A847A", metal="#C4BEB4", paint_metal=0.9, paint_rough=0.3,
                     wear=0.6, rust=0.15, dust=0.3, grime=0.4),
    # the base plate's front edge, banded (3.3: #C8A23A, the base plate edge only), worn
    # and dirtied, as the furnace's warning ring is
    "hazard": layered("hazard", "#C8A23A", paint_metal=0.1, paint_rough=0.85, wear=0.8,
                      rust=0.45, dust=0.9, grime=0.9, ground=0.9, ground_h=0.3,
                      pattern=lambda g: stripes(g)),
    # grease where the gears run, dark and glossy
    "grease": layered("grease", "#3A3229", metal="#4A4238", paint_metal=0.2, paint_rough=0.2,
                      wear=0.0, rust=0.0, dust=0.0, grime=0.2, jitter=0.03),
}


def plain(name, hexcol, rough=0.9, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(hexcol)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


M["dark"] = plain("dark", "#3E342A")            # the inside of the gear wells and the collar

# ---- round 11: the retrofit layer's materials (hoses, cables, the hydraulic unit,
# a newer plate, oil and grime), and a battered stave
M["battered"] = layered("battered", PRIMER[0], metal=BARE, paint_metal=0.05, paint_rough=0.65, wear=0.95,
                        rust=0.65, rust_tint=WET_RUST, pattern=primer(*PRIMER),
                        dust=0.35, grime=0.75, ground=0.9, ground_h=0.7, jitter=0.1,
                        drips=((1.7, 0.8), (1.38, 0.6), (0.86, 0.45), (0.34, 0.25)), drip=1.0)
# rubber hydraulic hose: a warm dark grey, not black, so it separates from the deck's
# contact shadows (FFF #146: shadows coloured, values kept apart); its ribs catch the
# sun in a crisp sheen; dusty on top, scuffed paler where it rubs
# (round 12: a lighter, warmer rust-brown rubber -- vanilla's foundry and electromagnetic
# plant hoses -- that parts from both the grey deck and the red walls at 1x)
M["hose"] = layered("hose", "#9A5C38", metal="#C89468", paint_metal=0.0, paint_rough=0.42, wear=0.3,
                    rust=0.05, dust=0.45, grime=0.4, jitter=0.12)
# insulated cable in muted colours, dusty
# (round 12: clearer colours, less dust, so they survive at 1x)
for _n, _c in (("red", "#B04A3A"), ("blue", "#4A74B0"), ("green", "#5C8E46"), ("yellow", "#D2A83E"),
               ("black", "#2E2C29")):
    M["cable_" + _n] = layered("cable_" + _n, _c, metal="#B0AA9E", paint_metal=0.0, paint_rough=0.45, wear=0.1,
                               rust=0.0, dust=0.25, grime=0.3, jitter=0.06)
M["tie"] = layered("tie", "#24221F", metal="#4A453E", paint_metal=0.0, paint_rough=0.4, wear=0.1, rust=0.0,
                   dust=0.3, grime=0.3)
# the hydraulic unit, bought in and bolted down later, in its maker's dull olive
M["olive"] = layered("olive", "#5C6248", metal="#A8A496", paint_metal=0.05, paint_rough=0.55, wear=0.55,
                     rust=0.35, dust=0.35, grime=0.7, jitter=0.08, drips=((2.05, 0.2),), drip=0.6)
# a newer plate, unpainted galvanised steel, mismatched with the primer round it
M["newplate"] = layered("newplate", "#7E8486", metal="#B8BEC0", paint_metal=0.45, paint_rough=0.45, wear=0.25,
                        rust=0.12, dust=0.25, grime=0.5, jitter=0.05)


def oil_material():
    """Oil soaked into a surface: dark, glossy in the middle, thinning to nothing at its
    edge (the decal's alpha falls off with distance from its middle and with noise)."""
    m = bpy.data.materials.new("oil")
    m.use_nodes = True
    t = m.node_tree
    n, ln = t.nodes, t.links
    b = n["Principled BSDF"]
    # (a warm dark brown, not black: in the collar's shadow a black stain crushes to
    # nothing -- FFF #146, shadows stay coloured)
    b.inputs["Base Color"].default_value = rig.srgb("#2E2219")
    b.inputs["Roughness"].default_value = 0.18
    tc = n.new("ShaderNodeTexCoord")
    grad = n.new("ShaderNodeTexGradient")
    grad.gradient_type = "SPHERICAL"
    ln.new(tc.outputs["Object"], grad.inputs["Vector"])
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.0
    noise.inputs["Detail"].default_value = 4.0
    ln.new(tc.outputs["Object"], noise.inputs["Vector"])
    mix = n.new("ShaderNodeMath")
    mix.operation = "MULTIPLY"
    ln.new(grad.outputs["Fac"], mix.inputs[0])
    rng = n.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = 0.3
    rng.inputs["From Max"].default_value = 0.65
    rng.inputs["To Min"].default_value = 0.35
    rng.inputs["To Max"].default_value = 1.2
    ln.new(noise.outputs["Fac"], rng.inputs["Value"])
    ln.new(rng.outputs[0], mix.inputs[1])
    a = n.new("ShaderNodeMath")
    a.operation = "MULTIPLY"
    a.use_clamp = True
    ln.new(mix.outputs[0], a.inputs[0])
    a.inputs[1].default_value = 1.15
    ln.new(a.outputs[0], b.inputs["Alpha"])
    return m


def streak_material():
    """A grime streak run down a face from a fitting: dark brown, strongest at its top,
    fading to nothing at its foot, in vertical runs (a decal in the decal's own UVs:
    local Y up the streak, 0 at the foot, 1 at the top)."""
    m = bpy.data.materials.new("streak")
    m.use_nodes = True
    t = m.node_tree
    n, ln = t.nodes, t.links
    b = n["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#1E140C")
    b.inputs["Roughness"].default_value = 0.8
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    ln.new(tc.outputs["Generated"], sep.inputs[0])
    mp = n.new("ShaderNodeMapping")                 # stretched tall: streaks run down
    mp.inputs["Scale"].default_value = (40.0, 2.0, 40.0)
    ln.new(tc.outputs["Generated"], mp.inputs["Vector"])
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 1.0
    noise.inputs["Detail"].default_value = 3.0
    ln.new(mp.outputs[0], noise.inputs["Vector"])
    runs = n.new("ShaderNodeMapRange")
    runs.inputs["From Min"].default_value = 0.42
    runs.inputs["From Max"].default_value = 0.62
    ln.new(noise.outputs["Fac"], runs.inputs["Value"])
    fade = n.new("ShaderNodeMath")                  # Y up the streak: 0 at its foot
    fade.operation = "POWER"
    ln.new(sep.outputs["Y"], fade.inputs[0])
    fade.inputs[1].default_value = 1.6
    side = n.new("ShaderNodeMath")                  # thinning to its sides
    side.operation = "SINE"
    pi = n.new("ShaderNodeMath")
    pi.operation = "MULTIPLY"
    ln.new(sep.outputs["X"], pi.inputs[0])
    pi.inputs[1].default_value = math.pi
    ln.new(pi.outputs[0], side.inputs[0])
    m1 = n.new("ShaderNodeMath")
    m1.operation = "MULTIPLY"
    ln.new(runs.outputs[0], m1.inputs[0])
    ln.new(fade.outputs[0], m1.inputs[1])
    m2 = n.new("ShaderNodeMath")
    m2.operation = "MULTIPLY"
    m2.use_clamp = True
    ln.new(m1.outputs[0], m2.inputs[0])
    ln.new(side.outputs[0], m2.inputs[1])
    m3 = n.new("ShaderNodeMath")
    m3.operation = "MULTIPLY"
    m3.use_clamp = True
    ln.new(m2.outputs[0], m3.inputs[0])
    m3.inputs[1].default_value = 0.55
    ln.new(m3.outputs[0], b.inputs["Alpha"])
    return m


M["oil"] = oil_material()
M["streak"] = streak_material()


def lens_material():
    """The status lamp's lens, painted white (3.3); the light pass lights it white."""
    m = bpy.data.materials.new("lens")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#E6E4DE")
    b.inputs["Roughness"].default_value = 0.3
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat Roughness"].default_value = 0.05
    b.inputs["Emission Color"].default_value = (1, 1, 1, 1)
    b.inputs["Emission Strength"].default_value = 0.0
    return m


M["lens"] = lens_material()

# ---------------------------------------------------------------- geometry helpers

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


def bolt(loc, r=0.018, h=0.016, mat="steel", group="static", rot=(0, 0, 0), parent=None):
    """A hex head."""
    return cyl(loc, r, h, mat, group, verts=6, rot=rot, bevel=0.0, parent=parent)


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


def stack(levels, mat, group="static", bevel=0.01, parent=None, name="stack"):
    """A closed solid through outlines at heights: levels = [(outline, z), ...], bottom up,
    every outline the same point count."""
    def build(bm):
        rows = [[bm.verts.new((x, y, z)) for x, y in pts] for pts, z in levels]
        bm.faces.new(list(reversed(rows[0])))
        bm.faces.new(rows[-1])
        for a, b in zip(rows, rows[1:]):
            n = len(a)
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new((a[i], a[j], b[j], b[i]))
    return mesh_object(name, build, mat, group, bevel, parent=parent)


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


def pipe(pts, r, mat, bend=0.06, group="static", parent=None):
    """A rigid run through pts, each corner turned through an elbow of radius ~bend."""
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
    return _finish(ob, mat, group, bevel=0, parent=parent)


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.parent = parent or ROOT
    e.location, e.rotation_euler, e.scale = loc, rot, scale
    return e


def cutter(loc, size, rot=(0, 0, 0)):
    """A hidden box to cut with."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    o.parent = ROOT
    o.hide_render = True
    o.display_type = "WIRE"
    return o


def cut(obj, *cutters):
    """Cut obj by the cutters, then triangulate: a cut cap leaves a concave n-gon that
    the renderer can fill wrongly (it drew a pier's top as a hole)."""
    for m in [m for m in obj.modifiers if m.type == "TRIANGULATE"]:
        obj.modifiers.remove(m)
    for c in cutters:
        b = obj.modifiers.new("cut", "BOOLEAN")
        b.operation = "DIFFERENCE"
        b.object = c
        b.solver = "EXACT"
    t = obj.modifiers.new("tri", "TRIANGULATE")
    t.min_vertices = 5
    return obj


def arc_band(r_out, r_in, z, h, a0, a1, mat, group="static", n=24, bevel=0.002):
    """A short arc of ring from a0 to a1 degrees round the tower's centre line: worn
    bright only where it is worn (round 5), not a whole hoop."""
    def build(bm):
        rows = []
        for r, zz in ((r_out, z - h / 2), (r_out, z + h / 2), (r_in, z + h / 2), (r_in, z - h / 2)):
            rows.append([bm.verts.new((r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
                                       YC + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)), zz))
                         for k in range(n + 1)])
        for k in range(4):
            a, b = rows[k], rows[(k + 1) % 4]
            for i in range(n):
                bm.faces.new((a[i], a[i + 1], b[i + 1], b[i]))
        bm.faces.new([rows[k][0] for k in range(4)])
        bm.faces.new([rows[k][n] for k in reversed(range(4))])
    return mesh_object("arc", build, mat, group, bevel)


WORN = ((222, 262), (275, 318), (40, 50), (130, 140), (219, 231), (309, 321))   # the front arc, broken; the corners


def octagon(half, cx=0.0, cy=0.0):
    """A regular octagon with flats facing east, north, west and south, `half` across
    the flats from its centre."""
    R = half / math.cos(math.pi / 8)
    return [(cx + R * math.cos(math.pi / 8 + k * math.pi / 4), cy + R * math.sin(math.pi / 8 + k * math.pi / 4))
            for k in range(8)]


def circle(r, n=64, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def stencil(text, loc, rot, size):
    """A stencilled marking (the signature finish's variation): flat text a hair proud of
    the surface, its local Z out of it, read along its local X."""
    bpy.ops.object.text_add(location=(0, 0, 0))
    t = bpy.context.active_object
    t.data.body = text
    t.data.size = size
    t.data.align_x, t.data.align_y = "CENTER", "CENTER"
    # a hair of thickness, so its face has an outward normal: a flat fill faced into the
    # wall shades as an occluded cavity, black
    t.data.extrude = 0.002
    t.location, t.rotation_euler = loc, rot
    return _finish(t, "stencil", "static", bevel=0)


# ---------------------------------------------------------------- 1. the base plate

BE, BH = 1.495, 0.10                 # half-width (the footprint, less a hair) and height
BC = 0.16                            # its corners cut


def chamfered_square(e, c):
    return [(-e, -e + c), (-e + c, -e), (e - c, -e), (e, -e + c), (e, e - c), (e - c, e), (-e + c, e), (-e, e - c)]


# a lip round the tower and its buttresses: the plate itself, mostly hidden under them
stack([(chamfered_square(BE, BC), 0.0), (chamfered_square(BE, BC), BH)], "plate", bevel=0.01, name="base")
# The hazard band (3.3: the base plate's edge only): a narrow strip on the front edge
# and the front halves of the sides, over the top and down the edge, worn and dirty;
# the buttresses' feet stand on it and break it up, as the plate draws it.
HW = 0.07


def hazard_run(p0, p1):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    nx, ny = d.y / d.length, -d.x / d.length          # outward, for a run anticlockwise round the plate
    m = (p0 + p1) / 2 - Vector((nx, ny)) * (HW / 2 - 0.002)
    box((m.x, m.y, BH / 2 + 0.002), (d.length, HW, BH + 0.006), "hazard", rot=(0, 0, math.atan2(d.y, d.x)),
        bevel=0.004)


hazard_run((-BE + BC, -BE), (BE - BC, -BE))
hazard_run((BE - BC, -BE), (BE, -BE + BC))
hazard_run((-BE, -BE + BC), (-BE + BC, -BE))
hazard_run((BE, -BE + BC), (BE, -0.35))
hazard_run((-BE, -0.35), (-BE, -BE + BC))
_bm = chamfered_square(BE - 0.12, BC * 0.6)
for i, (ax, ay) in enumerate(_bm):
    bx, by = _bm[(i + 1) % 8]
    run = math.hypot(bx - ax, by - ay)
    n = max(1, round(run / 0.17))
    for k in range(n):
        f = (k + 0.5) / n
        bolt((ax + (bx - ax) * f, ay + (by - ay) * f, BH + 0.008), 0.017, 0.016)

# ---------------------------------------------------------------- 2. the tower

YC = -0.12                           # the tower's centre: south of the footprint's, as the plate stands it
Z0, ZR = BH, 1.74                    # its wall, base plate to roof: tall, so its front wall is the
                                     # largest surface on the screen, as the plate's is
R0, R1 = 1.28, 1.22                  # tapered (3.2); a lip of base plate shows round it
LEAN = math.atan2(R0 - R1, ZR - Z0)


def r_at(z):
    return R0 + (R1 - R0) * (z - Z0) / (ZR - Z0)


def wall(a, z, out=0.0):
    """On the tower's wall at angle a (degrees, from east, anticlockwise), height z,
    stood out from it by out along its normal."""
    t = math.radians(a)
    r = r_at(z) + out * math.cos(LEAN)
    return (r * math.cos(t), YC + r * math.sin(t), z + out * math.sin(LEAN))


def on_wall(a, z, out=0.0):
    """(location, rotation): local Z out of the wall, local X along it anticlockwise
    (east on the south face), local Y up it, leaning back with it."""
    t = math.radians(a)
    n = Vector((math.cos(t) * math.cos(LEAN), math.sin(t) * math.cos(LEAN), math.sin(LEAN)))
    x = Vector((-math.sin(t), math.cos(t), 0.0))
    y = n.cross(x)
    m = Matrix((x, y, n)).transposed()
    return wall(a, z, out), m.to_euler()


BUTT = (45, 135, 225, 315)
HZ = 0.86                            # the hatch's centre, mid-course
COURSES = (Z0, 0.34, 1.38, ZR)
STAVES = 16
SEAMS = [11.25 + 22.5 * k for k in range(STAVES)]   # -90 is mid-stave, for the hatch


def near_buttress(a, by=14):
    return any(abs((a - b + 180) % 360 - 180) < by for b in BUTT)


def stave(a0, a1, z0, z1, n=8):
    """A wall plate, hand-hung (round 11, less machined): its edges a little out of true
    -- each edge vertex stood off or sunk by a few thousandths, its top and bottom
    wandering in height under the bands -- and its face oil-canned, bowed between them."""
    rnd = random.Random(f"{a0:.2f}/{z0:.2f}")

    def build(bm):
        rows = []
        for i, z in enumerate((z0, z1)):
            row = []
            for k in range(n + 1):
                edge = k in (0, n)
                out = rnd.uniform(-0.004, 0.006) if edge else 0.004 * math.sin(math.pi * k / n) * rnd.uniform(0.3, 1.0)
                zz = z + rnd.uniform(-0.007, 0.007) * (0 if z in (Z0, ZR) else 1)
                row.append(bm.verts.new(wall(a0 + (a1 - a0) * k / n, zz, out)))
            rows.append(row)
        for k in range(n):
            bm.faces.new((rows[0][k], rows[0][k + 1], rows[1][k + 1], rows[1][k]))
    return build


# the wall in plates, each its own object and so its own tone (the furnace's way); two
# of them replaced since, in fresher primer (the signature finish's variation): the
# upper course west of the old lamp boss, and the middle course east of the hatch
REPLACED = {(236.25, COURSES[2]), (281.25, COURSES[1])}
# and three that have had the worst of it (round 11: uneven wear), worn and rusted
# further -- on the west flank and by the hatch, none in the east's shade (round 12:
# there they crushed to black)
BATTERED = {(213.75, COURSES[1]), (191.25, COURSES[1]), (303.75, COURSES[2])}
for a in SEAMS:
    for z0, z1 in zip(COURSES, COURSES[1:]):
        mat = "fresh" if (a, z0) in REPLACED else "battered" if (a, z0) in BATTERED else "armour"
        p = mesh_object("stave", stave(a, a + 22.5, z0, z1), mat, "hull", bevel=0.0, smooth=True)
        sol = p.modifiers.new("solid", "SOLIDIFY")
        sol.thickness = 0.07
        sol.offset = -1.0
        bv = p.modifiers.new("bevel", "BEVEL")
        bv.width = 0.008
        bv.segments = 2
        bv.limit_method = "ANGLE"


def band(z, w, d, mat, seg=160):
    """A strap round the tower at height z, w tall, d proud."""
    def build(bm):
        rows = []
        for zz, o in ((z - w / 2, -0.01), (z - w / 2, d), (z + w / 2, d), (z + w / 2, -0.01)):
            rows.append([bm.verts.new(wall(360 * k / seg, zz, o)) for k in range(seg)])
        for k in range(4):
            a, b = rows[k], rows[(k + 1) % 4]
            for i in range(seg):
                j = (i + 1) % seg
                bm.faces.new((a[i], a[j], b[j], b[i]))
    return mesh_object("band", build, mat, "hull", bevel=0.004, smooth=True)


# the courses: a riveted strap on each joint, a foot band at the base and a lip band under the roof
for z in COURSES[1:-1]:
    band(z, 0.07, 0.02, "copper")
    for k in range(80):
        a = 360 * (k + 0.5) / 80
        if not near_buttress(a, 10):
            rivet(wall(a, z + 0.018, 0.027), 0.013)
            rivet(wall(a, z - 0.018, 0.027), 0.013)
band(Z0 + 0.045, 0.08, 0.025, "seam")
band(ZR - 0.04, 0.08, 0.022, "copper")
for k in range(72):
    a = 360 * (k + 0.5) / 72
    if not near_buttress(a, 10):
        rivet(wall(a, ZR - 0.04, 0.03), 0.014)
        rivet(wall(a, Z0 + 0.045, 0.032), 0.014)


def wall_strip(a, w, z0, z1, d, mat, group="hull", bevel=0.005):
    """A vertical strip on the wall at angle a, w wide, from z0 to z1, d proud."""
    def build(bm):
        v = []
        for z in (z0, z1):
            for s in (-1, 1):
                for o in (-0.01, d):
                    r = r_at(z)
                    v.append(bm.verts.new(wall(a + math.degrees(s * w / 2 / r), z, o)))
        for q in ((0, 2, 6, 4), (1, 5, 7, 3), (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6)):
            bm.faces.new([v[k] for k in q])
    return mesh_object("strip", build, mat, group, bevel=bevel)


# The staves' vertical joints the camera sees: a riveted cover strap on each, steel and
# copper by turns (the plate's copper bolt lines, 3.3), and a copper clip bolted over
# each band where a steel strap crosses it.
for i, a in enumerate(SEAMS):
    if math.sin(math.radians(a)) > 0.45 or near_buttress(a):
        continue
    mat = "copper" if i % 2 else "steel"
    for z0, z1 in zip(COURSES, COURSES[1:]):
        wall_strip(a, 0.075, z0 + 0.04, z1 - 0.04, 0.018, mat, group="static" if mat == "copper" else "hull")
        n = max(3, round((z1 - z0) / 0.16))
        for k in range(n):
            rivet(wall(a, z0 + 0.1 + (z1 - z0 - 0.2) * k / (n - 1), 0.026), 0.014)
    if mat == "steel":
        for z in COURSES[1:-1]:
            wall_strip(a, 0.11, z - 0.065, z + 0.065, 0.034, "copper", group="static")
            for dz in (-0.04, 0.04):
                bolt(wall(a, z + dz, 0.04), 0.013, 0.012, "steel", rot=on_wall(a, z, 0)[1])

# a weld line round the middle of each course, its plates' horizontal joints
for z0, z1 in zip(COURSES, COURSES[1:]):
    zm = (z0 + z1) / 2
    if z0 < HZ < z1:
        continue                      # the hatch's course
    band(zm, 0.018, 0.008, "seam")
# the foot skirt: a low bolted ring round the tower's base, between the buttresses'
# feet, its top sloped to the sky so the shadowed corners are steel, not black
skirt = []
for zz, r in ((BH - 0.01, R0 + 0.08), (0.2, R0 + 0.07), (0.27, R0 + 0.005)):  # its front 1.48 south: on the footprint
    skirt.append((circle(r, 96, 0.0, YC), zz))
stack(skirt, "frame", bevel=0.01, name="skirt")
for k in range(48):
    a = 360 * (k + 0.5) / 48
    if not near_buttress(a, 12):
        t = math.radians(a)
        bolt(((R0 + 0.055) * math.cos(t), YC + (R0 + 0.055) * math.sin(t), 0.215), 0.015, 0.016)

# ---------------------------------------------------------------- 3. the roof

ROOF = ZR + 0.04                     # its top
RL = R1 + 0.045                      # its lip, over the wall
roof = cyl((0, YC, (ZR + ROOF) / 2 - 0.01), RL, ROOF - ZR + 0.02, "roof", group="hull", verts=160, bevel=0.012)
torus((0, YC, ROOF - 0.002), RL - 0.006, 0.013, "seam", seg=160)                       # its edge weld
for k in range(60):
    a = 360 * (k + 0.5) / 60
    t = math.radians(a)
    bolt(((RL - 0.05) * math.cos(t), YC + (RL - 0.05) * math.sin(t), ROOF + 0.006), 0.016, 0.014)

# ---------------------------------------------------------------- 4. the collar

ZCT = ROOF + 0.84                    # the collar's rim: where the crown seats
NO, NI = 0.44, 0.27                  # the collar's outer and inner radius
RG, NG = 0.46, 26                    # the lift gears' pitch radius and teeth
ZA = ROOF + 0.52                     # the gears' axle: their teeth clear the roof by 0.03
assert ZCT - ZA >= 0.31, "the gears' teeth would touch the seated crown"
neck = ring((0, YC, (ROOF + ZCT) / 2), NO, NI, ZCT - ROOF, "collar", group="neck", verts=96, bevel=0.012)

PITCH = 2 * math.pi * RG / NG        # the rack's pitch
RACK_X = 0.242                       # the racks' pitch line, either side of the shank's centre
XG = RACK_X + RG                     # the gears' centres, east and west
TIP = RG + 0.03                      # tooth tips
RP, NP = PITCH * 7 / (2 * math.pi), 7  # the motor pinions: same pitch, seven teeth

# the pawl: its pivot on a pedestal at the collar's south-east, its nose on the ratchet
PIV = Vector((0.2, YC - 0.6, ZCT - 0.18))            # south of the collar: clear of the east gear's face
NOSE = Vector((0.03, YC - 0.245, ZCT - 0.30))
PAWL_U = (NOSE - PIV).normalized()
PAWL_A = math.atan2(PAWL_U.y, PAWL_U.x)            # its plane's heading
_cross = [PIV + (NOSE - PIV) * (t / 100) for t in range(101)]
_cross = [p for p in _cross if NI - 0.02 <= math.hypot(p.x, p.y - YC) <= NO + 0.02]
WIN = sum(_cross, Vector()) / len(_cross)

# The gears' slots: through the collar's east and west sides, rim and all, where the
# gears' teeth reach the shank's racks; its front rim stays whole. The pawl's window,
# south-south-east, under the rim.
win_cut = [cutter((sgn * 0.35, YC, (ROOF + ZCT) / 2), (0.3, 0.152, ZCT - ROOF + 0.2)) for sgn in (-1, 1)]
win_cut.append(cutter((WIN.x, WIN.y, ZCT - 0.21), (0.3, 0.12, 0.22), rot=(0, 0, PAWL_A)))
cut(neck, *win_cut)
# the collar's foot flange, bolted to the roof
fl = ring((0, YC, ROOF + 0.025), NO + 0.06, NO - 0.01, 0.05, "collar", group="neck", verts=96, bevel=0.01)
cut(fl, *[cutter((sgn * 0.5, YC, ROOF + 0.02), (0.24, 0.42, 0.2)) for sgn in (-1, 1)])
for k in range(24):
    a = 360 * (k + 0.5) / 24
    if min(abs((a - c + 180) % 360 - 180) for c in (0, 180)) < 27:
        continue
    t = math.radians(a)
    bolt(((NO + 0.032) * math.cos(t), YC + (NO + 0.032) * math.sin(t), ROOF + 0.058), 0.017, 0.018, "brass")
# the rim: a hard ring the crown lands on, polished pale by it (3.3), and a bolted
# flange round the collar's head under it
rim = ring((0, YC, ZCT - 0.012), NO - 0.005, NI - 0.004, 0.026, "anvil", group="neck", verts=96, bevel=0.008)
cut(rim, *win_cut[:2])
hf = ring((0, YC, ZCT - 0.08), NO + 0.06, NO - 0.01, 0.09, "collar", group="neck", verts=96, bevel=0.012)
cut(hf, *win_cut[:2])
# its lip worn bright where the crown and the crew's tools have rubbed it
for a0, a1 in ((228, 256), (266, 300), (100, 118)):
    arc_band(NO + 0.002, NO - 0.035, ZCT - 0.003, 0.012, a0, a1, "polish", group="neck")
# a riveted row round the head flange's outer face
for k in range(40):
    a = 360 * (k + 0.5) / 40
    t = math.radians(a)
    if min(abs((a - c + 180) % 360 - 180) for c in (0, 180)) < 14:
        continue
    rivet(((NO + 0.062) * math.cos(t), YC + (NO + 0.062) * math.sin(t), ZCT - 0.08), 0.011)
# a guide bushing in the bore under the rim, pale where the shank runs: the idle
# plate's bore is a ring of steel round the shank's hole, not a black hole
bush = ring((0, YC, ZCT - 0.06), NI + 0.004, 0.232, 0.04, "anvil", group="neck", verts=96, bevel=0.004)
cut(bush, *[cutter((sgn * 0.25, YC, ZCT - 0.06), (0.12, 0.17, 0.2)) for sgn in (-1, 1)],
    cutter((0, YC - 0.25, ZCT - 0.06), (0.2, 0.1, 0.2)))
# a second band low down, steel, riveted, and a weld seam up the collar's front,
# off its middle
lb = ring((0, YC, ROOF + 0.2), NO + 0.016, NO - 0.01, 0.045, "steel", group="neck", verts=96, bevel=0.006)
cut(lb, *win_cut)
for k in range(24):
    a = 360 * (k + 0.5) / 24
    t = math.radians(a)
    if min(abs((a - c + 180) % 360 - 180) for c in (0, 180)) < 18:
        continue
    rivet(((NO + 0.018) * math.cos(t), YC + (NO + 0.018) * math.sin(t), ROOF + 0.2), 0.011)
_ws = math.radians(-118)
box(((NO + 0.004) * math.cos(_ws), YC + (NO + 0.004) * math.sin(_ws), (ROOF + 0.24 + ZCT - 0.36) / 2),
    (0.016, 0.022, ZCT - 0.36 - ROOF - 0.24), "seam", rot=(0, 0, _ws), bevel=0.004)
for k in range(28):
    a = 360 * (k + 0.5) / 28
    t = math.radians(a)
    if min(abs((a - c + 180) % 360 - 180) for c in (0, 180)) < 16:
        continue
    bolt(((NO + 0.02) * math.cos(t), YC + (NO + 0.02) * math.sin(t), ZCT - 0.04), 0.016, 0.016, "steel")
# a copper band round its middle, broken by the slots and the window
mb = ring((0, YC, ZCT - 0.32), NO + 0.022, NO - 0.01, 0.06, "copper", group="neck", verts=96, bevel=0.008)
cut(mb, *win_cut)
for k in range(20):
    a = 360 * (k + 0.5) / 20
    t = math.radians(a)
    p = Vector(((NO + 0.024) * math.cos(t), YC + (NO + 0.024) * math.sin(t), ZCT - 0.32))
    if min(abs((a - c + 180) % 360 - 180) for c in (0, 180)) < 20 or (p.xy - WIN.xy).length < 0.12:
        continue
    bolt(tuple(p), 0.015, 0.02, "steel", rot=(0, math.pi / 2, t))
# The gears' housings (round 6): where each gear passes the collar's wall and rises
# past its rim, it runs between two bolted cheek plates under a cap, so it plainly
# enters a guide in the collar's side, never crosses the rim. The cheeks clear the
# gear's faces by 0.014, the cap its tooth tips by 0.035; the crown rises between the
# two housings, 0.018 clear of each.
CW = 0.30                                # the crown's half-width across the flats (5.)
HX0, HX1 = CW + 0.018, 0.6              # the housing's inner and outer ends
HTOP = ROOF + 1.045                       # the cap's underside: the gear's top is ZA + RG + 0.03 = ROOF + 1.01
for sgn in (-1, 1):
    for dy in (-1, 1):
        y = YC + dy * 0.08
        # below the rim, outside the collar's wall; above it, in to the crown's side
        box((sgn * (NO - 0.02 + HX1) / 2, y, (ROOF + 0.04 + ZCT) / 2), (HX1 - NO + 0.02, 0.022, ZCT - ROOF - 0.04),
            "guide", group="neck", bevel=0.006)
        box((sgn * (HX0 + HX1) / 2, y, (ZCT - 0.02 + HTOP) / 2), (HX1 - HX0, 0.022, HTOP - ZCT + 0.02), "guide",
            group="neck", bevel=0.006)
        # its bolted frame: a row of rivets down its outer edge, a row of hex bolts along
        # its top, and a weld where the cap meets it
        for k in range(6):
            rivet((sgn * (HX1 - 0.025), y + dy * 0.013, ROOF + 0.1 + (HTOP - ROOF - 0.15) * k / 5), 0.011)
        for k in range(5):
            bolt((sgn * (HX0 + 0.03 + (HX1 - HX0 - 0.06) * k / 4), y + dy * 0.013, HTOP - 0.032), 0.012, 0.01,
                 "steel", rot=(math.pi / 2, 0, 0))
        box((sgn * (HX0 + HX1) / 2, y + dy * 0.0115, HTOP + 0.001), (HX1 - HX0, 0.006, 0.012), "seam", bevel=0.002)
    box((sgn * (HX0 + HX1) / 2, YC, HTOP + 0.016), (HX1 - HX0 + 0.01, 0.184, 0.032), "guide", group="neck",
        bevel=0.008)                                                                     # the cap
    for k in range(3):
        for dy in (-1, 1):
            bolt((sgn * (HX0 + 0.05 + (HX1 - HX0 - 0.1) * k / 2), YC + dy * 0.07, HTOP + 0.034), 0.011, 0.01)
    # its outer edge worn bright only in two short broken stretches
    for y0, y1 in ((-0.085, -0.035), (0.01, 0.045)):
        box((sgn * (HX1 + 0.004), YC + (y0 + y1) / 2, HTOP + 0.03), (0.01, y1 - y0, 0.008), "polish", group="neck",
            bevel=0.002)

# ---------------------------------------------------------------- 5. the weight

WEIGHT = empty("weight", loc=(0, YC, ZCT))       # its seat: the crown's underside on the rim
CH = 0.42                                        # the crown's height (task: proud by >= CH/2 at the top)
SW = 0.20                                        # the shank's
# the crown: forged, chamfered top and bottom; a faceted top, eight sloped facets each
# taking the sun at its own value, the edges between them bright (3.3)
stack([(octagon(CW - 0.04), 0.002), (octagon(CW), 0.04), (octagon(CW), 0.27),
       (octagon(CW - 0.02), 0.29), (octagon(0.12), CH - 0.008), (octagon(0.11), CH)],
      "weight", group="crown", bevel=0.014, parent=WEIGHT, name="crown")
stack([(octagon(CW + 0.008), 0.13), (octagon(CW + 0.008), 0.16)], "weight", group="crown", bevel=0.006,
      parent=WEIGHT, name="forging")
cyl((0, 0, CH + 0.012), 0.075, 0.025, "weight", group="crown", verts=8, bevel=0.008, parent=WEIGHT)
for sx in (-1, 1):
    # lifting lugs, upright in the east-west plane: they draw at the camera's angle
    lug = empty("lug", loc=(sx * 0.05, 0, CH + 0.045), rot=(math.pi / 2, 0, 0), parent=WEIGHT)
    box((0, -0.01, 0), (0.06, 0.05, 0.03), "weight", group="crown", bevel=0.01, parent=lug)
    torus((0, 0.035, 0), 0.026, 0.011, "weight", group="crown", parent=lug, seg=24)
# the shank, down into the collar and the tower
SHANK = 1.6
stack([(octagon(SW), -SHANK), (octagon(SW), 0.004)], "weight", group="shank", bevel=0.01, parent=WEIGHT,
      name="shank")
# the racks on its east and west faces: a backing bar between cheeks, teeth on the pitch line
RACK_TOP, RACK_BOT = -0.02, -1.5
ks = [k for k in range(-30, 30) if RACK_BOT < (ZA - ZCT) + k * PITCH < RACK_TOP]
for sx in (-1, 1):
    box((sx * (SW + 0.004), 0, (RACK_TOP + RACK_BOT) / 2), (0.012, 0.11, RACK_TOP - RACK_BOT), "gear",
        group="shank", bevel=0.004, parent=WEIGHT)
    for sy in (-1, 1):
        # the rack's cheeks: a channel either side of it and of the gear's teeth, out to
        # the housing, so the bore beside the shank shows steel, not a hole (round 7)
        box((sx * (SW + 0.054), sy * 0.064, (RACK_TOP + RACK_BOT) / 2), (0.1, 0.014, RACK_TOP - RACK_BOT),
            "gear", group="shank", bevel=0.003, parent=WEIGHT)
    for k in ks:
        z = (ZA - ZCT) + k * PITCH

        def tooth(bm, sx=sx, z=z):
            r0, r1 = sx * (SW + 0.008), sx * (SW + 0.008 + 0.054)
            pts = [(r0, -0.028), (r1, -0.016), (r1, 0.016), (r0, 0.028)]
            rows = [[bm.verts.new((x, y, z + dz)) for x, dz in pts] for y in (-0.055, 0.055)]
            bm.faces.new(list(reversed(rows[0])))
            bm.faces.new(rows[1])
            for i in range(4):
                j = (i + 1) % 4
                bm.faces.new((rows[0][i], rows[0][j], rows[1][j], rows[1][i]))
        mesh_object("tooth", tooth, "gear", "shank", bevel=0.003, parent=WEIGHT)
# the ratchet on its south face, for the pawl: saw teeth, square faces up, cut deep and
# bright so the rack plainly pays out of the collar (the plate shows it)
RP_STEP = 0.06
for k in range(int(1.4 / RP_STEP)):
    z = -0.035 - k * RP_STEP

    def saw(bm, z=z):
        y0 = -SW + 0.002
        pts = [(y0, z - RP_STEP + 0.004), (y0 - 0.05, z), (y0, z)]
        rows = [[bm.verts.new((x, y, zz)) for y, zz in pts] for x in (-0.075, 0.075)]
        bm.faces.new(list(reversed(rows[0])))
        bm.faces.new(rows[1])
        for i in range(3):
            j = (i + 1) % 3
            bm.faces.new((rows[0][i], rows[0][j], rows[1][j], rows[1][i]))
    mesh_object("saw", saw, "gear", "shank", bevel=0.002, parent=WEIGHT)
for sx in (-1, 1):                                # the ratchet's cheeks
    box((sx * 0.085, -SW - 0.012, -0.72), (0.016, 0.034, 1.36), "gear", group="shank", bevel=0.003, parent=WEIGHT)

# ---------------------------------------------------------------- 6. the lift gear

HUB = 0.1                                         # the lift gears' hub
RIM_W = 0.09                                      # their rim, inside the teeth


def gear(parent, r, n, th, mat, group, spokes=5, phase=0.0, hub=0.07):
    """A spur gear about the parent's local Z, in its local XY plane: rim, n teeth (one
    centred at `phase` degrees), a web with lightening holes between spokes, and a
    hub with a keyed boss."""
    rim_in = r - RIM_W if r > 0.2 else r * 0.45
    ring((0, 0, 0), r - 0.03, rim_in, th, mat, group, parent=parent, verts=128, bevel=0.007)
    for k in range(n):
        a = math.radians(phase + 360 * k / n)

        def tooth(bm, a=a):
            pts = [(r - 0.035, -0.55), (r + 0.03, -0.3), (r + 0.03, 0.3), (r - 0.035, 0.55)]
            hw = math.pi * r / n
            rows = []
            for z in (-th / 2, th / 2):
                row = []
                for rr, s in pts:
                    lx, ly = rr, s * hw
                    row.append(bm.verts.new((lx * math.cos(a) - ly * math.sin(a), lx * math.sin(a) + ly * math.cos(a), z)))
                rows.append(row)
            bm.faces.new(list(reversed(rows[0])))
            bm.faces.new(rows[1])
            for i in range(4):
                j = (i + 1) % 4
                bm.faces.new((rows[0][i], rows[0][j], rows[1][j], rows[1][i]))
        mesh_object("tooth", tooth, "polish" if r > 0.2 else mat, group, bevel=0.005, parent=parent)
    if r > 0.2:
        cyl((0, 0, 0), rim_in + 0.005, th * 0.4, mat, group, verts=96, bevel=0.0, parent=parent)   # the web
        rr = (hub + rim_in) / 2
        hole = min(0.085, 0.42 * (rim_in - hub))
        for k in range(spokes):
            a = 2 * math.pi * (k + 0.5) / spokes
            # lightening holes: dark discs set into the web, ringed by a raised lip
            cyl((rr * math.cos(a), rr * math.sin(a), 0), hole, th * 0.42, "dark", group, verts=32, bevel=0.0,
                parent=parent)
            torus((rr * math.cos(a), rr * math.sin(a), th * 0.21), hole + 0.004, 0.008, mat, group,
                  parent=parent, seg=32)
            box((rr * math.cos(a + math.pi / spokes), rr * math.sin(a + math.pi / spokes), 0),
                (rim_in - hub + 0.01, 0.06, th * 0.8), mat, group, rot=(0, 0, a + math.pi / spokes), bevel=0.01,
                parent=parent)
    cyl((0, 0, 0), hub, th * 1.4, mat, group, verts=48, bevel=0.012, parent=parent)              # hub
    if r > 0.2:
        cyl((0, 0, th * 0.75), hub * 0.62, 0.03, "steel", group, verts=32, bevel=0.006, parent=parent)  # boss
        box((0, hub * 0.62, th * 0.75), (0.035, 0.05, 0.034), "brass", group, bevel=0.004, parent=parent)  # key
        for k in range(6):
            u = 2 * math.pi * k / 6
            bolt((hub * 0.82 * math.cos(u), hub * 0.82 * math.sin(u), th * 0.72), 0.011, 0.016, "steel", group,
                 parent=parent)
    cyl((0, 0, th * 0.78), hub * 0.35, 0.03, "brass", group, verts=6, bevel=0.0, parent=parent)   # its nut
    cyl((0, 0, -th * 0.72), hub * 0.6, 0.02, "brass", group, verts=6, bevel=0.0, parent=parent)


def mesh_phase(theta, phase_g, n_g, r_g, r_p, n_p):
    """The pinion's tooth phase (degrees) so it meshes the gear at direction theta
    (degrees, from the gear's centre): the gear's teeth roll onto the pinion's gaps."""
    pg = 360 / n_g
    d = (theta - phase_g) % pg                     # the gear's nearest tooth, d degrees short of theta
    return theta + 180 + d * r_g / r_p + 180 / n_p


GEARS = {}
PINIONS = {}
GT = 0.11                                         # the gears' face width
MR = 0.10                                         # the motors' drums
PANG = 0.0                                        # the pinion meshes at the gear's level, outboard (round 6):
                                                  # a clear mesh point at its 3 o'clock, the motor beyond the gear
for sx in (-1, 1):
    # squarely east and west of the collar on the roof, upright in the east-west plane,
    # their full faces to the camera; local Z of the axle points south, local Y up
    axle = empty("axle", loc=(sx * XG, YC, ZA), rot=(math.pi / 2, 0, 0))
    spin = empty("gear", parent=axle)
    ph = (180 if sx > 0 else 0) + 180 / NG         # a gap faces the rack at rest
    gear(spin, RG, NG, GT, "gear", "gears", phase=ph, hub=HUB)
    GEARS[sx] = spin
    # the pinion, outboard and below: in the gear's local frame (x east, y up) the mesh
    # direction is PANG on the east gear, 180 - PANG on the west
    th = PANG if sx > 0 else 180 - PANG
    pz = ZA + (RG + RP) * math.sin(math.radians(th))
    pax = empty("pinion-axle", loc=(sx * XG + (RG + RP) * math.cos(math.radians(th)), YC, pz), rot=(math.pi / 2, 0, 0))
    pspin = empty("pinion", parent=pax)
    gear(pspin, RP, NP, 0.09, "gear", "gears", phase=mesh_phase(th, ph, NG, RG, RP, NP), hub=0.045)
    PINIONS[sx] = pspin
    x, MZ = pax.location.x, pz
    # the gear's axle, out north into a pillow block on the roof, brass-capped
    cyl((sx * XG, YC + 0.1, ZA), 0.035, 0.22, "steel", verts=24, rot=(math.pi / 2, 0, 0), bevel=0.0)
    y = YC + 0.15
    box((sx * XG, y, (ROOF + ZA) / 2 + 0.02), (0.17, 0.09, ZA - ROOF + 0.04), "frame", bevel=0.012)
    box((sx * XG, y, ZA + 0.055), (0.18, 0.1, 0.05), "brass", bevel=0.01)                      # its cap
    for dx in (-0.06, 0.06):
        bolt((sx * XG + dx, y, ZA + 0.085), 0.014, 0.02, "steel")
    box((sx * XG, y + 0.01, ROOF + 0.015), (0.3, 0.15, 0.03), "frame", bevel=0.006)           # its foot
    for dx in (-0.12, 0.12):
        bolt((sx * XG + dx, y + 0.01, ROOF + 0.034), 0.013, 0.012)
    # grease flung off the teeth onto the deck under the gear, and run down the block
    box((sx * XG, YC - 0.02, ROOF + 0.001), (0.7, 0.1, 0.003), "grease", rot=(0, 0, sx * 0.04), bevel=0.0)

    # the motor at the roof's edge: a finned drum on the pinion's axle north of it, a
    # gearhead, and a flanged coupling between them and the pinion
    cyl((x, YC + 0.035, MZ), 0.02, 0.07, "steel", verts=16, rot=(math.pi / 2, 0, 0), bevel=0.0)       # shaft
    for yy in (0.055, 0.072):                                                                      # coupling
        cyl((x, YC + yy, MZ), 0.06, 0.016, "steel", verts=32, rot=(math.pi / 2, 0, 0), bevel=0.003)
    for k in range(4):
        u = 2 * math.pi * (k + 0.5) / 4
        bolt((x + 0.044 * math.cos(u), YC + 0.0635, MZ + 0.044 * math.sin(u)), 0.009, 0.034, "brass",
             rot=(math.pi / 2, 0, 0))
    cyl((x, YC + 0.11, MZ), MR - 0.015, 0.06, "frame", verts=48, rot=(math.pi / 2, 0, 0), bevel=0.01)    # gearhead
    cyl((x, YC + 0.27, MZ), MR, 0.26, "armour", verts=48, rot=(math.pi / 2, 0, 0), bevel=0.012)       # the drum
    for yy in (0.16, 0.39):
        cyl((x, YC + yy, MZ), MR + 0.016, 0.03, "copper", verts=48, rot=(math.pi / 2, 0, 0), bevel=0.006)
    for k in range(4):
        torus((x, YC + 0.2 + k * 0.045, MZ), MR + 0.003, 0.007, "steel", rot=(math.pi / 2, 0, 0), seg=48)
    for k in range(6):
        t = 2 * math.pi * k / 6
        bolt((x + (MR - 0.03) * math.cos(t), YC + 0.08, MZ + (MR - 0.03) * math.sin(t)), 0.01, 0.012,
             rot=(math.pi / 2, 0, 0))

    # The pier under it: a slim battered column off the tower's east (west) side, base
    # plate to the shoulder, the motor at the roof's edge on its top (the plate's
    # shoulders). Its south face takes the sun, and it covers the strip of base plate
    # the tower would otherwise throw into black shadow.
    def rect(x0, x1, y0, y1, z, sx=sx):
        return ([(sx * x0, y0), (sx * x1, y0), (sx * x1, y1), (sx * x0, y1)][::sx], z)
    PT = ROOF - 0.06
    # (its south face 0.1 south of the tower's centre line: the tower hides the part of it
    # its own shadow falls on)
    stack([rect(1.05, 1.47, YC - 0.12, YC + 0.6, BH), rect(1.05, 1.44, YC - 0.12, YC + 0.6, 0.8),
           rect(1.0, 1.36, YC - 0.1, YC + 0.56, PT - 0.03)], "armour", group="hull", bevel=0.025, name="pier")
    stack([rect(1.0, 1.4, YC - 0.12, YC + 0.6, PT - 0.08), rect(1.0, 1.4, YC - 0.12, YC + 0.6, PT)],
          "edge", bevel=0.014, name="pcap")
    for z in (0.55, 1.3):                                       # copper bands across its face
        f = z / PT
        xo = 1.47 + (1.36 - 1.47) * f
        box((sx * (xo - 0.2), YC - 0.12 + 0.02 * f - 0.012, z), (0.42, 0.03, 0.06), "copper", bevel=0.006)
    for z in [0.32 + 0.15 * i for i in range(12)]:              # rivet rows down its front edges
        if z < PT - 0.1:
            f = z / PT
            for xx in (1.1, 1.42 + (1.32 - 1.42) * f):
                rivet((sx * xx, YC - 0.125 + 0.02 * f, z), 0.013)
    box((x, YC + 0.27, (PT + MZ - MR) / 2 + 0.01), (0.14, 0.22, MZ - MR - PT + 0.03), "frame", bevel=0.008)
    box((x, YC + 0.27, PT + 0.015), (0.24, 0.3, 0.03), "frame", bevel=0.006)                 # its foot
    for dx in (-0.095, 0.095):
        for dy in (0.15, 0.39):
            bolt((x + dx, YC + dy, PT + 0.034), 0.011, 0.012)
    # the pinion's outboard bearing, a slim bracket south of it
    box((x, YC - 0.07, (PT + MZ) / 2), (0.07, 0.035, MZ - PT + 0.04), "frame", bevel=0.006)
    cyl((x, YC - 0.07, MZ), 0.035, 0.045, "brass", verts=24, rot=(math.pi / 2, 0, 0), bevel=0.006)
    # its terminal box on top, for the conduit from the junction box
    box((x, YC + 0.28, MZ + MR + 0.03), (0.1, 0.12, 0.06), "brass", bevel=0.01)
    box((x, YC + 0.28, MZ + MR + 0.065), (0.11, 0.13, 0.012), "steel", bevel=0.004)
    MOTOR_X, MOTOR_Z = abs(x), MZ

# ---------------------------------------------------------------- 8. the trip pawl

# Hung off the collar, not stood on a pedestal (round 3): a cheek bracket bolted to
# the collar's wall carries the pin; a strap down from it carries the spring's shelf
# under the lever's tail.
PERP = Vector((-PAWL_U.y, PAWL_U.x, 0)).normalized()
for s_ in (-1, 1):
    c = PIV + PERP * s_ * 0.045
    box((c.x, c.y, PIV.z - 0.02), (0.11, 0.018, 0.12), "steel", rot=(0, 0, PAWL_A), bevel=0.004)
    # the cheek's arm back to the collar's wall, along the lever's line
    w = Vector((NO * math.cos(math.atan2(c.y - YC, c.x)), YC + NO * math.sin(math.atan2(c.y - YC, c.x)), PIV.z - 0.04))
    e = Vector((c.x, c.y, PIV.z - 0.04))
    d = e - w
    box(tuple((w + e) / 2), (d.length + 0.02, 0.022, 0.06), "frame", rot=(0, 0, math.atan2(d.y, d.x)), bevel=0.005)
    bolt(tuple(w + d.normalized() * 0.03 + Vector((0, 0, 0.033))), 0.011, 0.01)
cyl(tuple(PIV), 0.018, 0.13, "brass", verts=16, rot=Vector((PERP.x, PERP.y, 0)).to_track_quat("Z", "Y").to_euler(),
    bevel=0.0)
TAIL_L = 0.13
SHELF = PIV - PAWL_U * TAIL_L
SHELF_Z = PIV.z - 0.26
box((SHELF.x, SHELF.y, SHELF_Z), (0.09, 0.09, 0.03), "steel", rot=(0, 0, PAWL_A), bevel=0.004)
st = PIV + PERP * 0.062 - PAWL_U * 0.06
box((st.x, st.y, (PIV.z + SHELF_Z) / 2 - 0.02), (0.1, 0.016, PIV.z - SHELF_Z), "frame", rot=(0, 0, PAWL_A),
    bevel=0.004)

PIN = -PERP                                        # the pin's axis: local Z, so local Y is up the plane
PAWL = empty("pawl", loc=tuple(PIV),
             rot=Matrix((PAWL_U, PAWL_U.cross(PERP).normalized(), PIN)).transposed().to_euler())
L = (NOSE - PIV).length
box((L / 2 - 0.04, 0, 0), (L - 0.02, 0.06, 0.05), "gear", group="pawl", bevel=0.01, parent=PAWL)
box((-TAIL_L / 2, 0, 0), (TAIL_L + 0.03, 0.05, 0.05), "gear", group="pawl", bevel=0.01, parent=PAWL)
cyl((0, 0, 0), 0.04, 0.07, "gear", group="pawl", verts=24, bevel=0.008, parent=PAWL)              # its boss


def nose(bm):
    pts = [(L - 0.06, 0.03), (L + 0.01, -0.005), (L - 0.02, -0.045), (L - 0.07, -0.03)]
    rows = [[bm.verts.new((x, y, z)) for x, y in pts] for z in (-0.024, 0.024)]
    bm.faces.new(list(reversed(rows[0])))
    bm.faces.new(rows[1])
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((rows[0][i], rows[0][j], rows[1][j], rows[1][i]))


mesh_object("nose", nose, "steel", "pawl", bevel=0.004, parent=PAWL)
box((0.02, 0.06, 0), (0.04, 0.09, 0.04), "gear", group="pawl", rot=(0, 0, -0.3), bevel=0.006, parent=PAWL)
rivet((0, 0, 0.038), 0.016, "brass", group="pawl", parent=PAWL)
SPRING = empty("spring", loc=(SHELF.x, SHELF.y, SHELF_Z + 0.015))
_coil = []
for i in range(7 * 24 + 1):
    t = i / 24
    _coil.append((0.028 * math.cos(2 * math.pi * t), 0.028 * math.sin(2 * math.pi * t), t / 7))
cu = bpy.data.curves.new("coil", "CURVE")
cu.dimensions = "3D"
cu.bevel_depth = 0.007
cu.bevel_resolution = 3
sp = cu.splines.new("POLY")
sp.points.add(len(_coil) - 1)
for p_, co in zip(sp.points, _coil):
    p_.co = (*co, 1)
ob = bpy.data.objects.new("coil", cu)
sc.collection.objects.link(ob)
_finish(ob, "steel", "pawl", bevel=0, parent=SPRING)

# ---------------------------------------------------------------- 9. the buttresses

ZT = ZR - 0.14                                    # just under the roof (3.2)
# tight against the wall, tall and tapered: (z, inner r, outer r, half-width)
BSEC = ((0.3, 1.12, 1.58, 0.25), (0.95, 1.1, 1.5, 0.21), (ZT, 1.08, 1.42, 0.17))


def b_at(z):
    """The buttress's outer r and half-width at height z."""
    for (z0, _, r0, h0), (z1, _, r1, h1) in zip(BSEC, BSEC[1:]):
        if z <= z1:
            f = (z - z0) / (z1 - z0)
            return r0 + (r1 - r0) * f, h0 + (h1 - h0) * f
    return BSEC[-1][2], BSEC[-1][3]


for a in BUTT:
    t = math.radians(a)
    c, s = math.cos(t), math.sin(t)
    tx, ty = -s, c

    def section(r_in, r_out, hw, z, flare=0.0, c=c, s=s, tx=tx, ty=ty):
        """A trapezoid: hw at the outer face, wider by flare per unit depth at the
        wall, so its sides meet the wall open, not in a slot that fills with shadow."""
        wi = hw + (r_out - r_in) * flare
        return ([(r * c + k * w * tx, YC + r * s + k * w * ty) for r, k, w in
                 ((r_in, -1, wi), (r_out, -1, hw), (r_out, 1, hw), (r_in, 1, wi))], z)

    def on_face(r_off, k, z, c=c, s=s, tx=tx, ty=ty):
        ro, hw = b_at(z)
        return (( ro + r_off) * c + k * hw * tx, YC + (ro + r_off) * s + k * hw * ty, z)
    stack([section(r_in, r_out, hw, z, flare=0.5) for z, r_in, r_out, hw in BSEC], "buttress", group="hull", bevel=0.045,
          name="buttress")
    # its stepped plinth on the base plate, standing on the hazard band
    stack([section(1.02, 1.62, 0.255, BH - 0.01), section(1.02, 1.6, 0.25, 0.2), section(1.02, 1.5, 0.23, 0.32)],
          "frame", bevel=0.016, name="plinth")
    for k in (-1, 1):
        for r, z in ((1.54, 0.2), (1.44, 0.32)):
            bolt((r * c + k * 0.19 * tx, YC + r * s + k * 0.19 * ty, z + 0.008), 0.018, 0.016)
    # Panelled, each one its own way (round 4: the faces had read as a grid): a weld
    # seam across at its own height, a vertical seam up only the upper plate and off
    # the middle, one copper band, a riveted steel strap low down, and a plate bolted
    # over part of the upper face on the other side from the seam.
    bi = BUTT.index(a)
    zs, kx, zc, zp = ((0.48, 0.32, 1.12, 1.38), (0.58, -0.28, 1.06, 1.36),
                      (0.52, -0.3, 1.02, 1.34), (0.44, 0.26, 1.15, 1.4))[bi]
    ro, hw = b_at(zs)
    box((ro * c, YC + ro * s, zs), (0.025, 2 * hw - 0.02, 0.022), "seam", rot=(0, 0, t), bevel=0.004)
    p0, p1 = Vector(on_face(0.004, kx, zs + 0.02)), Vector(on_face(0.004, kx, ZT - 0.04))
    d = p1 - p0
    box(tuple((p0 + p1) / 2), (0.022, 0.016, d.length), "seam", rot=d.to_track_quat("Z", "Y").to_euler(), bevel=0.003)
    ro, hw = b_at(zc)
    box(((ro - 0.24) * c, YC + (ro - 0.24) * s, zc), (0.5, 2 * hw + 0.03, 0.08), "copper", rot=(0, 0, t),
        bevel=0.01)
    for k in (-1, 1):
        bolt(on_face(0.02, k * 0.55, zc), 0.013, 0.012, "steel", rot=(0, math.pi / 2, t))
    ro, hw = b_at(0.78)
    box(((ro - 0.2) * c, YC + (ro - 0.2) * s, 0.78), (0.42, 2 * hw + 0.02, 0.045), "steel", rot=(0, 0, t),
        bevel=0.006)
    for k in (-0.5, 0.0, 0.5):
        rivet(on_face(0.024, k, 0.78), 0.012)
    pc = Vector(on_face(0.012, -kx * 1.3, zp))
    box(tuple(pc), (0.02, 0.13, 0.2), "patch", rot=(0, 0, t), bevel=0.004)
    for dk, dz in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        bolt(on_face(0.024, -kx * 1.3 + dk * 0.22, zp + dz * 0.075), 0.01, 0.01, "steel", rot=(0, math.pi / 2, t))
    for k in (-1, 1):
        pts = [Vector(on_face(0.0, k, z)) for z in (0.34, 0.95, ZT - 0.03)]
        for p0, p1 in zip(pts, pts[1:]):
            d = p1 - p0
            box(tuple((p0 + p1) / 2), (0.04, 0.04, d.length), "edge", rot=d.to_track_quat("Z", "Y").to_euler(),
                bevel=0.006)
        for z in [0.42 + 0.155 * i + (0.077 if k > 0 else 0.0) for i in range(16)]:   # staggered
            if z < ZT - 0.08 and min(abs(z - zz) for zz in (zc, 0.78)) > 0.07:
                rivet(on_face(0.006, k * 0.62, z), 0.013)
    # its cap, and the lifting eye on it, upright along the diagonal so it draws at the
    # camera's angle (the vacuum furnace's lesson)
    stack([section(1.06, 1.46, 0.19, ZT - 0.02), section(1.06, 1.46, 0.19, ZT + 0.1)], "edge", bevel=0.02,
          name="cap")
    ex, ey = 1.27 * c, YC + 1.27 * s
    box((ex, ey, ZT + 0.14), (0.2, 0.13, 0.08), "steel", rot=(0, 0, t), bevel=0.012)
    lug = empty("eye", loc=(ex, ey, ZT + 0.31), rot=(math.pi / 2, 0, t))
    box((0, -0.08, 0), (0.2, 0.13, 0.07), "steel", bevel=0.016, parent=lug)
    torus((0, 0.03, 0), 0.08, 0.034, "rail", parent=lug, seg=32)
    # its top edge worn bright where the hook bears: the top third of the ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.08, minor_radius=0.036, location=(0, 0.03, 0),
                                     major_segments=32, minor_segments=8)
    top = bpy.context.active_object
    bm = bmesh.new()
    bm.from_mesh(top.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < 0.03 + 0.055], context="VERTS")
    bm.to_mesh(top.data)
    bm.free()
    _finish(top, "polish", "static", bevel=0, smooth=True, parent=lug)
    for k in (-1, 1):
        bolt((ex + k * 0.07 * c, ey + k * 0.07 * s, ZT + 0.182), 0.014, 0.014)
    if a == 315:
        # its rated load stencilled on the south-east buttress, between the strap and the band
        stencil("8T", on_face(0.012, -0.25, 0.97), Matrix(((-s, c, 0), (0, 0, 1), (c, s, 0))).transposed().to_euler(),
                0.09)

# ---------------------------------------------------------------- 10. the hatch, the ladder and the lamp

HATCH = empty("hatch", *on_wall(-90, HZ - 0.03, 0.0), scale=(1.15, 1.15, 1.15))
ring((0, 0, -0.03), 0.36, 0.27, 0.16, "frame", parent=HATCH, verts=64, bevel=0.012)
bpy.context.view_layer.update()
assert (HATCH.matrix_world.translation - Vector(HATCH_C)).length < 1e-3, "HATCH_C is not the hatch's centre"
cyl((0, 0, 0.0), 0.28, 0.06, "door", verts=64, bevel=0.012, parent=HATCH)                         # the door
cyl((0, 0, 0.035), 0.2, 0.025, "door", verts=64, bevel=0.01, parent=HATCH)                        # its boss
torus((0, 0, 0.05), 0.31, 0.012, "seam", parent=HATCH, seg=64)
for k in range(20):
    u = 2 * math.pi * (k + 0.5) / 20
    rivet((0.335 * math.cos(u), 0.335 * math.sin(u), 0.055), 0.012, parent=HATCH)
DOG_SET = (0.0, 3.0, -2.0, 1.5, -3.0, 2.0, -1.0, 2.5)
for k in range(8):
    u = math.radians(22.5 + k * 45 + DOG_SET[k])
    box((0.29 * math.cos(u), 0.29 * math.sin(u), 0.07), (0.13, 0.055, 0.04), "copper", rot=(0, 0, u), bevel=0.01,
        parent=HATCH)
    box((0.35 * math.cos(u), 0.35 * math.sin(u), 0.03), (0.04, 0.07, 0.1), "copper", rot=(0, 0, u), bevel=0.008,
        parent=HATCH)
    rivet((0.245 * math.cos(u), 0.245 * math.sin(u), 0.092), 0.012, "steel", parent=HATCH)
for dz in (-0.12, 0.12):
    box((-0.37, dz, 0.04), (0.08, 0.09, 0.07), "steel", bevel=0.01, parent=HATCH)
cyl((-0.37, 0, 0.04), 0.022, 0.36, "steel", verts=16, rot=(math.pi / 2, 0, 0), bevel=0.0, parent=HATCH)
torus((0, 0, 0.09), 0.09, 0.014, "steel", parent=HATCH, seg=32)
for k in range(3):
    u = math.radians(90 + k * 120)
    box((0.045 * math.cos(u), 0.045 * math.sin(u), 0.085), (0.09, 0.015, 0.012), "steel", rot=(0, 0, u),
        bevel=0.0, parent=HATCH)
cyl((0, 0, 0.08), 0.022, 0.03, "brass", verts=16, bevel=0.004, parent=HATCH)
# scuffs on the wall under the hatch, where it is worked from
for da, z, w in ((-4, 0.6, 0.16), (5, 0.52, 0.1), (-1, 1.72, 0.12)):
    loc, rot = on_wall(-90 + da, z, 0.003)
    box(loc, (w, 0.05, 0.004), "scuff", rot=rot, bevel=0.0)

# Where the status lamp was (round 10): its boss on the wall face above the hatch,
# blanked off with a bolted steel cover now the lamp stands on the kerb.
BLANK = empty("blank", *on_wall(-90, ZR - 0.2, 0.0))
cyl((0, 0, 0.0), 0.14, 0.08, "frame", verts=32, bevel=0.01, parent=BLANK)                     # the boss
cyl((0, 0, 0.05), 0.115, 0.028, "steel", verts=32, bevel=0.008, parent=BLANK)                 # its cover
for k in range(4):
    u = 2 * math.pi * (k + 0.5) / 4
    bolt((0.085 * math.cos(u), 0.085 * math.sin(u), 0.068), 0.013, 0.012, parent=BLANK)

# The status lamp (round 10): a caged lamp on a bolted bracket on the roof's kerb, at
# the south-east, west of the maker's plate and the buttress's lifting eye -- in front of the deck, so
# nothing that moves passes in front of it in any frame. A domed white lens in a brass
# housing on a short post, a wire cage over the dome (Factorio's lamp, not a flat
# disc); 0.19 tiles across, ~12 px in the sheet. The light pass is the lens, lit white,
# the cage and everything else cut out of it.
LAMP_A = 288                      # (the maker's plate is at 300, the eye at 315)
_t = math.radians(LAMP_A)
LAMP = empty("lamp", loc=((RL - 0.025) * math.cos(_t), YC + (RL - 0.025) * math.sin(_t), ROOF + 0.05),
             rot=(0, 0, _t))
box((0.0, 0, 0.008), (0.13, 0.15, 0.016), "frame", bevel=0.004, parent=LAMP)                   # the foot, over the kerb
for dx in (-0.045, 0.045):
    for dy in (-0.05, 0.05):
        bolt((dx, dy, 0.022), 0.011, 0.01, parent=LAMP)
cyl((0, 0, 0.07), 0.026, 0.11, "steel", verts=16, bevel=0.0, parent=LAMP)                     # the post
LH = 0.15                                                                                        # the housing's top
cyl((0, 0, LH - 0.025), 0.085, 0.05, "brass", verts=32, bevel=0.008, parent=LAMP)             # the housing
torus((0, 0, LH), 0.088, 0.01, "brass", parent=LAMP, seg=48)                                   # its lip
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.082, location=(0, 0, 0), segments=32, ring_count=16)
lens = bpy.context.active_object
lens.scale.z = 0.95
bpy.ops.object.transform_apply(scale=True)
_finish(lens, "lens", "lens", bevel=0, smooth=True, parent=LAMP)
lens.location = (0, 0, LH)
# the cage: two wire hoops crossed over the dome, a ring round its waist, a knob on top
for rz in (0.0, math.pi / 2):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.092, minor_radius=0.0065, location=(0, 0, 0),
                                     rotation=(math.pi / 2, 0, rz), major_segments=40, minor_segments=6)
    hoop = bpy.context.active_object
    bpy.ops.object.transform_apply(rotation=True)
    bm = bmesh.new()
    bm.from_mesh(hoop.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.004], context="VERTS")
    bm.to_mesh(hoop.data)
    bm.free()
    _finish(hoop, "steel", "static", bevel=0, smooth=True, parent=LAMP)
    hoop.location = (0, 0, LH)
torus((0, 0, LH + 0.045), 0.08, 0.006, "steel", parent=LAMP, seg=40)
cyl((0, 0, LH + 0.094), 0.016, 0.014, "brass", verts=12, bevel=0.0, parent=LAMP)

# ---------------------------------------------------------------- 11. the roof's furniture

# A working deck, as the furnace's roof is (round 3): radial welds between its plates,
# each riveted both sides, clear of the collar, the gears and the pawl
for a in (40, 72, 108, 140, 222, 255, 285, 318):
    t = math.radians(a)
    ux, uy = math.cos(t), math.sin(t)
    r0, r1 = NO + 0.16, RL - 0.1
    rm = (r0 + r1) / 2
    box((rm * ux, YC + rm * uy, ROOF + 0.004), (r1 - r0, 0.018, 0.01), "seam", rot=(0, 0, t), bevel=0.003)
    n = round((r1 - r0) / 0.085)
    for k in range(n + 1):
        r = r0 + (r1 - r0) * k / n
        for side in (-1, 1):
            rivet((r * ux - side * 0.03 * uy, YC + r * uy + side * 0.03 * ux, ROOF + 0.004), 0.012)
# a bolted ring plate round the collar's foot
ring((0, YC, ROOF + 0.01), NO + 0.12, NO + 0.055, 0.02, "rail", verts=96, bevel=0.005)
for a0, a1 in ((238, 268), (282, 300)):
    arc_band(NO + 0.118, NO + 0.07, ROOF + 0.021, 0.004, a0, a1, "polish")
for k in range(30):
    t = 2 * math.pi * (k + 0.5) / 30
    bolt(((NO + 0.09) * math.cos(t), YC + (NO + 0.09) * math.sin(t), ROOF + 0.026), 0.013, 0.012)
# a kerb round the roof's edge, riveted, with a weld at its foot
ring((0, YC, ROOF + 0.025), RL, RL - 0.05, 0.05, "rail", verts=160, bevel=0.008)
for a0, a1 in WORN:                                  # its top worn bright only where it is hit
    arc_band(RL - 0.002, RL - 0.03, ROOF + 0.052, 0.008, a0, a1, "polish")
for k in range(64):
    t = 2 * math.pi * (k + 0.5) / 64
    rivet(((RL - 0.025) * math.cos(t), YC + (RL - 0.025) * math.sin(t), ROOF + 0.052), 0.011)
# an inspection plate in the south-west plates: bolted down, two lifting handles
INS = empty("inspection", loc=(-0.5, YC - 0.43, ROOF + 0.008), rot=(0, 0, math.radians(-8)))
box((0, 0, 0), (0.3, 0.24, 0.016), "roof", bevel=0.005, parent=INS)
box((0, 0, -0.002), (0.34, 0.28, 0.012), "steel", bevel=0.004, parent=INS)
for k in range(10):
    u = k / 10
    for p in ((-0.15 + 0.3 * u, -0.12), (0.15 - 0.3 * u, 0.12), (-0.15, 0.12 - 0.24 * u), (0.15, -0.12 + 0.24 * u)):
        if k % 2 == 0:
            bolt((p[0] * 1.06, p[1] * 1.08, 0.01), 0.01, 0.01, parent=INS)
for dx in (-0.08, 0.08):
    lug = empty("handle", loc=(dx, 0, 0.03), rot=(math.pi / 2, 0, 0), parent=INS)
    torus((0, 0, 0), 0.03, 0.007, "steel", parent=lug, seg=16)
# A copper ring main on the deck, the furnace's way (round 4: warmth): the south arc
# round the collar, clamped down, each end turning down through a flanged gland
RING_R, RZ_ = 0.93, ROOF + 0.03
arc = [((RING_R * math.cos(math.radians(a))), YC + RING_R * math.sin(math.radians(a)), RZ_)
       for a in [200 + 140 * k / 48 for k in range(49)]]
cu = bpy.data.curves.new("ringmain", "CURVE")
cu.dimensions = "3D"
cu.bevel_depth = 0.024
cu.bevel_resolution = 4
cu.use_fill_caps = True
sp = cu.splines.new("POLY")
sp.points.add(len(arc) - 1)
for p_, co in zip(sp.points, arc):
    p_.co = (*co, 1)
ob = bpy.data.objects.new("ringmain", cu)
sc.collection.objects.link(ob)
_finish(ob, "copper", "static", bevel=0)
for k in range(8):
    a = math.radians(200 + 140 * (k + 0.5) / 8)
    box((RING_R * math.cos(a), YC + RING_R * math.sin(a), RZ_), (0.035, 0.075, 0.06), "brass", rot=(0, 0, a),
        bevel=0.006)
for a in (200, 340):
    t = math.radians(a)
    cyl((RING_R * math.cos(t), YC + RING_R * math.sin(t), ROOF + 0.02), 0.05, 0.04, "brass", verts=24, bevel=0.006)
    for k in range(4):
        u = 2 * math.pi * (k + 0.5) / 4
        bolt((RING_R * math.cos(t) + 0.036 * math.cos(u), YC + RING_R * math.sin(t) + 0.036 * math.sin(u),
              ROOF + 0.042), 0.008, 0.008)
# a repair: a plate patched over the north-west, askew, welded and bolted
PATCH = empty("patch", loc=(-0.62, YC + 0.6, ROOF + 0.006), rot=(0, 0, math.radians(18)))
box((0, 0, 0), (0.22, 0.15, 0.012), "patch", bevel=0.004, parent=PATCH)
for sx in (-1, 1):
    for sy in (-1, 1):
        rivet((sx * 0.085, sy * 0.055, 0.008), 0.012, parent=PATCH)
for sy in (-1, 1):
    box((0, sy * 0.078, 0.0), (0.24, 0.018, 0.016), "seam", bevel=0.005, parent=PATCH)
for sx in (-1, 1):
    box((sx * 0.113, 0, 0.0), (0.018, 0.17, 0.016), "seam", bevel=0.005, parent=PATCH)
# scuffs where the crew walk, and grease and dirt round the gear furniture
for x, y, r in ((-0.3, YC - 0.85, 0.3), (0.25, YC - 0.88, -0.4), (-0.95, YC - 0.3, 1.2), (0.0, YC - 0.66, 0.1)):
    box((x, y, ROOF + 0.002), (0.2, 0.05, 0.004), "scuff", rot=(0, 0, r), bevel=0.0)
for x, y, sxy in ((0.55, YC + 0.32, 0.18), (-0.52, YC + 0.3, 0.14), (0.95, YC + 0.12, 0.12)):
    cyl((x, y, ROOF + 0.0015), sxy, 0.003, "grease", verts=24, bevel=0.0)
# a lubricator on the north deck, its grease lines run along the roof to each pillow
# block's cap, clipped down
LUB = (0.0, YC + 0.62)
box((LUB[0], LUB[1], ROOF + 0.07), (0.14, 0.1, 0.14), "brass", bevel=0.012)
cyl((LUB[0], LUB[1], ROOF + 0.17), 0.04, 0.06, "steel", verts=16, bevel=0.006)
for sx in (-1, 1):
    # (round 6: along the deck to behind the gear, up a clipped riser well north of it,
    # and over into the cap's top from behind: never behind the gear's web)
    pipe([(LUB[0] + sx * 0.07, LUB[1], ROOF + 0.03), (sx * 0.4, LUB[1] - 0.02, ROOF + 0.03),
          (sx * XG, YC + 0.62, ROOF + 0.03), (sx * XG, YC + 0.62, ZA + 0.1), (sx * XG, YC + 0.19, ZA + 0.1),
          (sx * XG, YC + 0.19, ZA + 0.08)], 0.008, "copper", bend=0.05)
    box((sx * XG, YC + 0.64, ROOF + 0.25), (0.04, 0.03, 0.04), "steel", bevel=0.004)          # the riser's clip
    box((sx * XG, YC + 0.66, (ROOF + ZA) / 2), (0.03, 0.02, ZA - ROOF), "frame", bevel=0.004)  # and its post
    for p in ((sx * 0.25, LUB[1] - 0.01),):
        box((p[0], p[1], ROOF + 0.02), (0.035, 0.03, 0.02), "steel", bevel=0.003)
# a junction box at the roof's north edge feeding both motors
JX, JY = 0.0, YC + 0.95
box((JX, JY, ROOF + 0.06), (0.28, 0.13, 0.12), "frame", bevel=0.01)
box((JX, JY, ROOF + 0.125), (0.29, 0.14, 0.012), "steel", bevel=0.004)
for sx in (-1, 1):
    pipe([(JX + sx * 0.14, JY, ROOF + 0.05), (sx * 0.5, JY - 0.05, ROOF + 0.05),
          (sx * MOTOR_X, YC + 0.55, ROOF + 0.05), (sx * MOTOR_X, YC + 0.28, MOTOR_Z + MR + 0.03)],
         0.014, "copper", bend=0.08)
    for f in (0.35, 0.75):                                          # its saddle clips on the roof
        p = Vector((sx * (0.14 + 0.36 * f), JY - 0.05 * f, ROOF + 0.02))
        box(tuple(p), (0.05, 0.04, 0.03), "steel", bevel=0.004)
# the maker's plate: brass, riveted to the south face's upper course, off the hatch
loc, rot = on_wall(-60, 2.0, 0.012)
mp = empty("makers", loc=loc, rot=rot)
box((0, 0, 0), (0.24, 0.14, 0.012), "brass", bevel=0.004, parent=mp)
for sx in (-1, 1):
    for sy in (-1, 1):
        rivet((sx * 0.1, sy * 0.05, 0.008), 0.01, parent=mp)
# a repair patch on the wall, lower course, west of the hatch, askew
loc, rot = on_wall(-122, 0.42, 0.01)
wp = empty("wallpatch", loc=loc, rot=rot)
wp.rotation_euler.rotate_axis("Z", math.radians(-9))
box((0, 0, 0), (0.22, 0.16, 0.014), "patch", bevel=0.004, parent=wp)
for sx in (-1, 1):
    for sy in (-1, 1):
        rivet((sx * 0.09, sy * 0.06, 0.01), 0.011, parent=wp)

# Stencilled markings (the signature finish): the machine's number on the replaced
# upper stave west of the old lamp boss, a warning beside the hatch on the replaced middle stave,
# and each motor's number on the south face of its pier.
stencil("DC-03", *on_wall(-112, 1.47, 0.012), 0.085)        # (above 1.5 the roof's lip hides it)
stencil("KEEP\nCLEAR", *on_wall(-62.5, 0.45, 0.012), 0.07)       # (clear of the dogs' swing)
for sx, label in ((1, "M2"), (-1, "M1")):
    # (on the strip of pier face clear of the tower's wall: x 1.27 to 1.43)
    stencil(label, (sx * 1.355, YC - 0.128, 0.92), (math.pi / 2, 0, 0), 0.075)

# ---------------------------------------------------------------- 12. the retrofit (round 11)
#
# Liam, against vanilla: "we need to add more wiring and hoses and things ... these look
# too well machined". Vanilla layers a working machine with what was added to it after
# it was built (the electromagnetic plant's corrugated hoses round its rim, the foundry's
# coloured cables and clamps): so here, a hydraulic unit bolted to the deck feeding the
# gear housings and the pinions' bearings through drooping rubber hoses with crimped
# fittings; a junction box on the deck, its cables in an open tray inside the kerb to
# the lamp and over the edge to both motors, one bundle looping down the wall; a feed
# cable down the south-west buttress's flank to the ground; welded brackets and clips
# holding all of it; a newer plate on the wall; oil under the gears and the motors, and
# grime run down from the fittings. Everything sits on something. Nothing enters the
# volume any moving part sweeps in any frame: `--collide` checks it, below.
RETRO_BEFORE = set(bpy.data.objects)


def catmull(pts, step=0.008):
    """A smooth path through pts (Catmull-Rom), sampled about every `step` tiles."""
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
    """Tangents and parallel-transported normals along a sampled path."""
    T = [(P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized() for i in range(len(P))]
    up = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0))
    N = [T[0].cross(up).normalized()]
    for i in range(1, len(P)):
        n = N[-1] - T[i] * N[-1].dot(T[i])
        N.append(n.normalized() if n.length > 1e-6 else N[-1])
    B = [t.cross(n) for t, n in zip(T, N)]
    return T, N, B


def sweep_raw(P, r, mat, corr=0.0, pitch=0.03, seg=10, name="hose", group="static"):
    """A tube along the sampled path P; corr ribs it (a corrugated hose)."""
    T, N, B = frames(P)
    s = [0.0]
    for a_, b_ in zip(P, P[1:]):
        s.append(s[-1] + (b_ - a_).length)

    def build(bm):
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
    return mesh_object(name, build, mat, group, bevel=0, smooth=True)


def along(t):
    """A rotation whose local Z runs along t."""
    return Vector(t).normalized().to_track_quat("Z", "Y").to_euler()


def hose(pts, r=0.032, mat="hose", ends=True):
    """A rubber hydraulic hose, ribbed, through pts; a crimped ferrule and a hex nut at
    each end, the nut at the end point (on the port)."""
    P = catmull(pts)
    sweep_raw(P, r, mat, corr=0.14, pitch=0.022, seg=12)
    if ends:
        for p, q in ((P[0], P[1]), (P[-1], P[-2])):
            t = (p - q).normalized()                       # out of the hose, into the port
            cyl(tuple(p - t * 0.03), r * 1.45, 0.055, "steel", verts=16, rot=along(t), bevel=0.004)   # ferrule
            for d in (-0.045, -0.015):                     # its crimp rings
                torus(tuple(p + t * d), r * 1.45, 0.004, "steel", rot=along(t), seg=16)
            cyl(tuple(p + t * 0.002), r * 1.75, 0.022, "brass", verts=6, rot=along(t), bevel=0.0)      # the nut
    return P


CABLE = {"r": "cable_red", "b": "cable_blue", "g": "cable_green", "y": "cable_yellow", "k": "cable_black"}


def bundle(pts, cols="rbgy", r=0.011, ties=0.16, twist=9.0, spread=None, flat=False):
    """Insulated cables in muted colours, laid together through pts and zip-tied; flat
    lays them side by side (in a tray) instead of twisted round each other."""
    P = catmull(pts)
    T, N, B = frames(P)
    s = [0.0]
    for a_, b_ in zip(P, P[1:]):
        s.append(s[-1] + (b_ - a_).length)
    n = len(cols)
    sp = spread if spread is not None else (r * 1.25 if n > 1 else 0.0)
    for k, c in enumerate(cols):
        if flat:
            off = [(k - (n - 1) / 2) * 2.05 * r * N[i] for i in range(len(P))]
        else:
            off = [sp * (math.cos(2 * math.pi * k / n + twist * s[i]) * N[i]
                         + math.sin(2 * math.pi * k / n + twist * s[i]) * B[i]) for i in range(len(P))]
        sweep_raw([p + o for p, o in zip(P, off)], r, CABLE[c], seg=8, name="cable")
    if ties and not flat:
        nxt = ties / 2
        for i, p in enumerate(P):
            if s[i] >= nxt and s[i] < s[-1] - 0.03:
                torus(tuple(p), sp + r + 0.003, 0.0045, "tie", rot=along(T[i]), seg=16)
                nxt += ties
    return P


def gland(p, t, r=0.016, mat="brass"):
    """A cable or hose gland: a bushing out of a face along t, and its hex nut."""
    t = Vector(t).normalized()
    p = Vector(p)
    cyl(tuple(p + t * 0.012), r, 0.024, mat, verts=12, rot=along(t), bevel=0.003)
    cyl(tuple(p + t * 0.026), r * 1.25, 0.012, mat, verts=6, rot=along(t), bevel=0.0)
    return p + t * 0.034


def weld_bracket(loc, rot, size=(0.05, 0.04, 0.035), mat="steel"):
    """A retrofitted bracket: a bent plate welded on, its bead along its foot."""
    e = empty("bracket", loc=loc, rot=rot)
    box((0, 0, size[2] / 2), size, mat, bevel=0.004, parent=e)
    box((0, 0, 0.003), (size[0] + 0.012, size[1] + 0.012, 0.008), "seam", bevel=0.003, parent=e)
    return e


def saddle(p, t, r, z_floor):
    """A strap clip holding a hose or cable down: a strap over it, a welded foot each side."""
    t = Vector(t)
    yaw = math.atan2(t.y, t.x)
    e = empty("saddle", loc=(p.x, p.y, z_floor), rot=(0, 0, yaw))
    top = p.z - z_floor + r
    box((0, 0, top + 0.004), (0.022, 2 * r + 0.02, 0.008), "steel", bevel=0.002, parent=e)
    for sy in (-1, 1):
        box((0, sy * (r + 0.008), (top + 0.008) / 2), (0.022, 0.008, top + 0.008), "steel", bevel=0.0, parent=e)
        box((0, sy * (r + 0.024), 0.004), (0.03, 0.03, 0.008), "seam", bevel=0.002, parent=e)


def decal_plane(name, w, h, mat, loc, rot, top=True, group="static"):
    """A flat decal (oil, a grime streak): local X across, local Y up, its top at loc
    (top) or centred on it; it casts no shadow."""
    y0, y1 = (-h, 0.0) if top else (-h / 2, h / 2)

    def build(bm):
        v = [bm.verts.new((x, y, 0.0)) for x, y in ((-w / 2, y0), (w / 2, y0), (w / 2, y1), (-w / 2, y1))]
        bm.faces.new(v)
    o = mesh_object(name, build, mat, group, bevel=0)
    o.location, o.rotation_euler = loc, rot
    o.visible_shadow = False
    return o


def oil(x, y, z, rx, ry, yaw=0.0, seed=0):
    """An oil stain on a level surface: an irregular blob, soaked dark, thinning out."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 2 * math.pi) for _ in range(3)]

    def build(bm):
        n = 28
        c = bm.verts.new((0, 0, 0))
        ring_ = [bm.verts.new((math.cos(2 * math.pi * k / n) * (1 + 0.18 * math.sin(3 * 2 * math.pi * k / n + ph[0])
                                                                 + 0.1 * math.sin(5 * 2 * math.pi * k / n + ph[1])),
                               math.sin(2 * math.pi * k / n) * (1 + 0.18 * math.sin(3 * 2 * math.pi * k / n + ph[0])
                                                                 + 0.1 * math.sin(7 * 2 * math.pi * k / n + ph[2])), 0))
                 for k in range(n)]
        for k in range(n):
            bm.faces.new((c, ring_[k], ring_[(k + 1) % n]))
    o = mesh_object("oil", build, "oil", "static", bevel=0)
    o.location, o.rotation_euler, o.scale = (x, y, z), (0, 0, yaw), (rx, ry, 1.0)
    o.visible_shadow = False
    return o


def polar(r, a, z):
    t = math.radians(a)
    return Vector((r * math.cos(t), YC + r * math.sin(t), z))


# -- the hydraulic unit: bought in, in its maker's olive, on a newer galvanised mounting
# plate on the south-east deck, its long axis along the deck's curve (between the ring
# plate round the collar, r 0.56, and the copper ring main, r 0.93)
HU_A, HU_R = 323.0, 0.74
_hc = polar(HU_R, HU_A, ROOF)
_tu = Vector((-math.sin(math.radians(HU_A)), math.cos(math.radians(HU_A)), 0))   # along the curve
_ru = Vector((-math.cos(math.radians(HU_A)), -math.sin(math.radians(HU_A)), 0))  # inward
HU = empty("hydraulic", loc=tuple(_hc), rot=(0, 0, math.atan2(_tu.y, _tu.x)))


def hu(x, y, z):
    """The unit's local point (x along the curve, y inward, z up from the deck) in model space."""
    return _hc + _tu * x + _ru * y + Vector((0, 0, z))


box((0, 0, 0.008), (0.27, 0.16, 0.016), "newplate", bevel=0.004, parent=HU)                    # mounting plate
for sx in (-1, 1):
    for sy in (-1, 1):
        bolt((sx * 0.115, sy * 0.06, 0.02), 0.011, 0.01, parent=HU)
    box((sx * 0.07, 0, 0.04), (0.03, 0.12, 0.05), "olive", bevel=0.005, parent=HU)                # saddles
cyl((0, 0.01, 0.1), 0.058, 0.2, "olive", verts=32, rot=(0, math.pi / 2, 0), bevel=0.01, parent=HU)   # reservoir
for sx in (-1, 1):
    torus((sx * 0.07, 0.01, 0.1), 0.059, 0.006, "steel", rot=(0, math.pi / 2, 0), parent=HU, seg=32)  # straps
cyl((0.04, 0.01, 0.165), 0.018, 0.02, "brass", verts=12, bevel=0.003, parent=HU)                # filler cap
M["glass"] = plain("glass", "#9AA49C", rough=0.15)
cyl((-0.03, -0.066, 0.1), 0.014, 0.006, "glass", verts=12, rot=(math.pi / 2, 0, 0), bevel=0.0, parent=HU)   # sight glass
cyl((-0.085, -0.055, 0.06), 0.032, 0.07, "olive", verts=24, rot=(0, math.pi / 2, 0), bevel=0.006, parent=HU)   # pump motor
for k in range(3):
    torus((-0.07 - k * 0.015, -0.055, 0.06), 0.033, 0.004, "steel", rot=(0, math.pi / 2, 0), parent=HU, seg=24)
cyl((0.1, -0.055, 0.055), 0.022, 0.07, "steel", verts=16, bevel=0.004, parent=HU)              # filter canister

# -- the hoses (round 12: chunkier, rust-brown, and laid on the deck rather than looped
# in the air in the collar's shade). Each gear housing carries a manifold block welded to
# its south cheek low down, sitting on the collar's ring plate, two ports facing
# south: the unit feeds each manifold along the deck, and each manifold feeds its
# pinion's outboard bearing along the deck and over the kerb. Every hose stays
# south of the gears' faces (y <= -0.24 against their -0.175) and below the pinions
# (z <= 2.0 against their 2.15).
MAN = {}
for sx in (-1, 1):
    c = Vector((sx * 0.552, YC - 0.115, ROOF + 0.065))
    box(tuple(c), (0.1, 0.05, 0.09), "steel", bevel=0.006)
    box((c.x, YC - 0.092, c.z + 0.045), (0.11, 0.012, 0.012), "seam", bevel=0.003)                # its weld
    for dx in (-0.032, 0.032):
        bolt((c.x + dx, c.y - 0.026, c.z + 0.026), 0.009, 0.008, rot=(math.pi / 2, 0, 0))
    # (both ports face south: a port on its outer end reached under the gear's rim)
    MAN[sx] = dict(south=gland(Vector((sx * 0.515, c.y - 0.025, ROOF + 0.06)), (0, -1, 0), 0.026, "steel"),
                   out=gland(Vector((sx * 0.588, c.y - 0.025, ROOF + 0.06)), (0, -1, 0), 0.026, "steel"))
# the pinions' bearing brackets take a port on their south faces
BRG = {sx: gland(Vector((sx * MOTOR_X, YC - 0.0875, 1.98)), (0, -1, 0), 0.026, "steel") for sx in (-1, 1)}

R_H = 0.042
Z_DECK = ROOF + R_H                                   # a hose lying on the deck
# (a) the unit to the east manifold: out of the reservoir's north end, down onto the
# deck and in from the south
p_a0 = gland(hu(0.1, 0.01, 0.09), _tu, 0.026, "steel")
hose([p_a0, p_a0 + _tu * 0.04 + Vector((0, 0, -0.03)), Vector((0.63, -0.40, Z_DECK)), Vector((0.55, -0.36, Z_DECK + 0.012)),
      MAN[1]["south"] + Vector((0, -0.04, 0)), MAN[1]["south"]], R_H)
# (b) the unit to the west manifold: along the south deck, round the collar's ring plate
# and the inspection plate's handles, clipped down, then in from the south
p_b0 = gland(hu(-0.1, 0.01, 0.09), -_tu, 0.026, "steel")
pb = [p_b0, p_b0 - _tu * 0.05 + Vector((0, 0, -0.03)), Vector((0.36, -0.78, Z_DECK)), Vector((0.12, -0.82, Z_DECK)),
      Vector((-0.12, -0.80, Z_DECK)), Vector((-0.36, -0.76, Z_DECK)), Vector((-0.6, -0.71, Z_DECK)),
      Vector((-0.71, -0.57, Z_DECK)), Vector((-0.64, -0.42, Z_DECK)), Vector((-0.55, -0.36, Z_DECK + 0.012)),
      MAN[-1]["south"] + Vector((0, -0.04, 0)), MAN[-1]["south"]]
P = hose(pb, R_H)
for i in (len(P) * 2 // 7, len(P) * 3 // 7, len(P) * 5 // 7):
    saddle(P[i], P[i + 1] - P[i], R_H, ROOF)
# (c, d) each manifold to its pinion's bearing: out along the deck south of the gear,
# over the kerb's lip in a welded saddle, and up into the bracket from the south
for sx in (-1, 1):
    m = MAN[sx]["out"]
    P = hose([m, m + Vector((0, -0.035, 0)), Vector((sx * 0.70, YC - 0.2, Z_DECK)), Vector((sx * 0.86, YC - 0.175, Z_DECK)),
              Vector((sx * 1.06, YC - 0.17, Z_DECK)), Vector((sx * 1.2, YC - 0.2, ROOF + 0.05 + R_H + 0.004)),
              Vector((sx * 1.272, YC - 0.215, 1.95)), BRG[sx] + Vector((0, -0.06, -0.01)), BRG[sx]], R_H)
    saddle(Vector((sx * 1.2, YC - 0.2, ROOF + 0.05 + R_H + 0.004)), Vector((sx, -0.15, 0)), R_H, ROOF + 0.05)
    saddle(P[len(P) // 3], P[len(P) // 3 + 1] - P[len(P) // 3], R_H, ROOF)


def clamp(P, i, r, wall_dir):
    """A visible clamp on a cable run: a steel band round the bundle at P[i] and a welded
    bracket from it back to the face it hangs on (wall_dir: from the face to the cable)."""
    t = (P[min(i + 1, len(P) - 1)] - P[i]).normalized()
    torus(tuple(P[i]), r + 0.006, 0.008, "steel", rot=along(t), seg=20)
    w = Vector(wall_dir).normalized()
    a = P[i] - w * (r + 0.03)
    box(tuple(a), (0.03, 0.03, 0.03), "steel", rot=along(w), bevel=0.004)
    box(tuple(a - w * 0.02), (0.05, 0.05, 0.008), "seam", rot=along(w), bevel=0.002)


R_C = 0.011                                            # a cable, round 12: fewer, thicker

# -- the junction box: on the south deck between the hose and the ring main, its glands
# facing out to the tray
JB_A, JB_R = 255.0, 0.84
_jc = polar(JB_R, JB_A, ROOF)
_jo = Vector((math.cos(math.radians(JB_A)), math.sin(math.radians(JB_A)), 0))      # out
JB = empty("junction", loc=tuple(_jc), rot=(0, 0, math.radians(JB_A)))
box((0, 0, 0.075), (0.11, 0.19, 0.15), "frame", bevel=0.008, parent=JB)
box((0.002, 0, 0.155), (0.12, 0.2, 0.014), "newplate", bevel=0.004, parent=JB)                  # its lid, a later one
for dy in (-0.08, 0.08):
    for dx in (-0.045, 0.045):
        bolt((dx, dy, 0.163), 0.009, 0.008, parent=JB)
for dy in (-0.07, 0.07):                                                                        # its feet, welded down
    box((0, dy, 0.006), (0.12, 0.03, 0.012), "frame", bevel=0.003, parent=JB)
    box((0, dy, 0.002), (0.125, 0.04, 0.006), "seam", bevel=0.002, parent=JB)
JG = {}
for k, dy in enumerate((-0.045, 0.045)):
    _p = _jc + _jo * 0.055 + Vector((0, 0, 0.095)) + Vector((-_jo.y, _jo.x, 0)) * dy
    JG[k] = gland(_p, _jo, 0.028)

# -- the open cable tray inside the kerb, south-west to south-east, on welded stools
TR0, TR1, TRR, TRW = 206.0, 338.0, 1.128, 0.042
arc_band(TRR + TRW, TRR - TRW, ROOF + 0.012, 0.008, TR0, TR1, "steel", n=96)
for rr in (TRR + TRW, TRR - TRW + 0.006):
    arc_band(rr, rr - 0.006, ROOF + 0.032, 0.04, TR0, TR1, "steel", n=96)
for a in range(int(TR0) + 6, int(TR1), 22):
    weld_bracket(tuple(polar(TRR + 0.062, a, ROOF + 0.004)), (0, 0, math.radians(a)), (0.03, 0.05, 0.03))
# the cables in it, side by side, and out of the box into it, over the ring main
TRAY_Z = ROOF + 0.016 + R_C
tray_path = [polar(TRR, a, TRAY_Z) for a in range(int(TR0) + 2, int(TR1) - 1, 6)]
bundle(tray_path, "yrb", r=R_C, flat=True)
for k, cols in enumerate(("yr", "bk")):
    g0 = JG[k]
    a_in = JB_A + (k - 0.5) * 3.0
    bundle([g0, polar(0.99, a_in, ROOF + 0.09), polar(1.07, a_in + 1.5, ROOF + 0.06),
            polar(TRR, a_in + 3, TRAY_Z + 0.012)], cols, r=R_C, ties=0.08)
# to the lamp: out of the tray and up its post
bundle([polar(TRR, LAMP_A - 7, TRAY_Z + 0.006), polar(TRR + 0.012, LAMP_A - 4, ROOF + 0.068),
        polar(RL - 0.065, LAMP_A - 1.2, ROOF + 0.092), polar(RL - 0.051, LAMP_A, ROOF + 0.12)], "y", r=0.01, ties=0)

# -- a second junction box, on the west pier's south face beside the motor's stencil:
# the feed comes up into it from the ground, the tray's west run drops into it from
# the kerb, and the west motor's cable leaves it up the pier
WB = Vector((-1.35, YC - 0.12 - 0.047, 1.25))
box(tuple(WB), (0.15, 0.075, 0.24), "frame", bevel=0.01)
box((WB.x, WB.y - 0.041, WB.z), (0.16, 0.012, 0.25), "newplate", bevel=0.004)                    # its door
for dx in (-0.06, 0.06):
    for dz in (-0.105, 0.105):
        bolt((WB.x + dx, WB.y - 0.048, WB.z + dz), 0.009, 0.008, rot=(math.pi / 2, 0, 0))
box((WB.x - 0.072, WB.y - 0.052, WB.z), (0.012, 0.02, 0.05), "brass", bevel=0.003)                 # its latch
for dz in (-0.13, 0.13):                                                                         # welded on
    box((WB.x, YC - 0.12 - 0.012, WB.z + dz), (0.12, 0.03, 0.02), "steel", bevel=0.003)
    box((WB.x, YC - 0.12 - 0.004, WB.z + dz), (0.13, 0.012, 0.03), "seam", bevel=0.002)
WG_in = gland(Vector((-1.30, WB.y, WB.z + 0.12)), (0, 0, 1), 0.024)
WG_out = gland(Vector((-1.395, WB.y, WB.z + 0.12)), (0, 0, 1), 0.024)
WG_feed = gland(Vector((-1.30, WB.y, WB.z - 0.12)), (0, 0, -1), 0.026)

# -- the motors' cables. The tray's west end drops over the kerb, clamped to the wall,
# into the west box; the west motor's leaves the box up the pier's face. The tray's
# east end hangs in a slack loop down the wall beside the south-east buttress, clamped,
# and climbs the east pier's face. Both run up the piers' tops, clear of the pinions
# (y >= 0.0 against their -0.075 at z <= 1.95), into glands on the motors' stools.
MG = {sx: gland(Vector((sx * (MOTOR_X + 0.07), YC + 0.24, 1.95)), (sx, 0, 0), 0.026) for sx in (-1, 1)}
P = bundle([polar(TRR, TR0 + 3, TRAY_Z + 0.006), polar(TRR + 0.06, 201, ROOF + 0.075), polar(RL + 0.016, 198, ROOF + 0.09),
            Vector(wall(197.5, 1.62, 0.085)), Vector(wall(196.5, 1.5, 0.09)), Vector((-1.29, -0.36, 1.46)),
            WG_in + Vector((0, 0, 0.05)), WG_in], "yrb", r=R_C, ties=0.1)
clamp(P, len(P) // 4, 2.3 * R_C, -Vector(wall(197.5, 1.62, 0.0)).xy.to_3d() + Vector(wall(197.5, 1.62, 0.1)))
P = bundle([WG_out, WG_out + Vector((0, 0, 0.06)), Vector((-1.40, -0.262, 1.58)), Vector((-1.40, -0.245, 1.70)),
            Vector((-1.39, -0.19, 1.745)), Vector((-1.39, 0.0, 1.745)), Vector((-1.43, YC + 0.24, 1.86)), MG[-1]],
           "yrb", r=R_C, ties=0.1)
clamp(P, len(P) // 5, 2.3 * R_C, (0, -1, 0))
P = bundle([polar(TRR, TR1 - 3, TRAY_Z + 0.006), polar(TRR + 0.06, 342, ROOF + 0.075), polar(RL + 0.016, 345, ROOF + 0.09),
            Vector(wall(343, 1.62, 0.085)), Vector(wall(341, 1.32, 0.09)), Vector(wall(343.5, 1.12, 0.09)),
            Vector(wall(349, 1.17, 0.085)), Vector((1.37, -0.30, 1.3)), Vector((1.40, -0.29, 1.5)),
            Vector((1.40, -0.262, 1.67)), Vector((1.39, -0.19, 1.755)), Vector((1.39, 0.0, 1.75)),
            Vector((1.43, YC + 0.24, 1.86)), MG[1]], "yrb", r=R_C, ties=0.1)
for f, wd in ((0.2, Vector(wall(342, 1.45, 0.1)) - Vector(wall(342, 1.45, 0.0))),
              (0.33, Vector(wall(343.5, 1.12, 0.1)) - Vector(wall(343.5, 1.12, 0.0))), (0.55, Vector((0, -1, 0)))):
    clamp(P, int(len(P) * f), 2.3 * R_C, wd)

# the feed: one heavy black cable up out of a gland in the base plate, clamped up the
# pier's face into the west box
FEED_G = gland(Vector((-1.40, -0.40, BH)), (0, 0, 1), 0.03, "steel")
P = bundle([FEED_G, FEED_G + Vector((0, 0, 0.08)), Vector((-1.36, -0.36, 0.34)), Vector((-1.30, -0.31, 0.62)),
            Vector((-1.29, -0.30, 0.95)), WG_feed + Vector((0, 0, -0.06)), WG_feed], "k", r=0.02)
clamp(P, int(len(P) * 0.6), 0.02, (0, -1, 0))

# -- a newer plate, bolted over the primer between the south-west buttress and the hatch:
# unpainted, a different steel, not quite square
NP = empty("newplate", *on_wall(245.5, 1.0, 0.012))
NP.rotation_euler.rotate_axis("Z", math.radians(2.5))
box((0, 0, 0), (0.16, 0.28, 0.012), "newplate", bevel=0.003, parent=NP)
for dx in (-0.06, 0.06):
    for dy in (-0.11, 0.0, 0.11):
        bolt((dx, dy, 0.009), 0.01, 0.01, parent=NP)

# -- oil and grime: soaked into the deck south of the gears, round the hydraulic unit,
# beside the junction box and on the piers' tops under the motors; run down the piers'
# faces from the motors, and down the wall from the kerb and the bands
for sx, sd in ((1, 1), (-1, 2)):
    if sx < 0:                       # (round 12: the east one lay in the collar's shade and crushed to black)
        oil(sx * 0.76, YC - 0.25, ROOF + 0.0015, 0.17, 0.075, yaw=sx * 0.12, seed=sd)
    oil(sx * 1.335, YC + 0.1, PT + 0.0015, 0.06, 0.15, seed=sd + 10)
    decal_plane("streak", 0.07, 0.6, "streak", (sx * 1.34, YC - 0.12 - 0.004, PT - 0.035), (math.pi / 2, 0, 0))
_o = hu(-0.02, 0.06, 0.0)
oil(_o.x, _o.y, ROOF + 0.0015, 0.16, 0.11, yaw=math.radians(HU_A + 90), seed=5)
_o = polar(0.78, 262, 0)
oil(_o.x, _o.y, ROOF + 0.0015, 0.07, 0.05, seed=6)
for a, z, w, h in ((LAMP_A, 1.725, 0.07, 0.42), (247, 1.33, 0.06, 0.32), (299, 1.33, 0.08, 0.4),
                   (205, 1.33, 0.07, 0.36), (264, 0.43, 0.05, 0.2), (343.5, 1.08, 0.05, 0.3)):
    decal_plane("streak", w, h, "streak", *on_wall(a, z, 0.011))

RETRO = [o for o in bpy.data.objects if o not in RETRO_BEFORE and o.type in ("MESH", "CURVE", "FONT")
         and not o.hide_render]

# ---------------------------------------------------------------- passes

rig.sun()
# The shadows lifted, as the vacuum furnace's are: the rig's warm fill raised for this
# building, so the niches between buttresses and piers stay coloured, not black.
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.26   # the rig: 0.14
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()

if "--blend" in argv:                    # debugging: the scene as built, not rendered
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "scene.blend"))
    sys.exit(0)

STATIC = ("static", "hull", "neck", "lens")
MOVING = ("crown", "shank", "gears", "pawl")


def setup(visible=(), catchers=(), holdouts=(), ground=False):
    for g, objs in PARTS.items():
        for o in objs:
            o.hide_render = g not in visible and g not in catchers and g not in holdouts
            o.is_shadow_catcher = g in catchers
            o.is_holdout = g in holdouts
            o.visible_camera = True
    GROUND.hide_render = not ground
    BOUNCE.hide_render = ground


PAWL_REST = PAWL.rotation_euler.copy()
TRIP = math.radians(15)                           # the pawl kicked clear: nose up off the ratchet


def pose(f):
    """Put every moving part where frame f has it."""
    s = lift(f)
    WEIGHT.location.z = ZCT + s
    for sx, g in GEARS.items():
        # meshed: the contact point on the gear travels with the rack
        g.rotation_euler.z = -sx * s / RG
    for sx, p in PINIONS.items():
        p.rotation_euler.z = sx * s / RP
    m = PAWL_REST.to_matrix()
    if tripped(f):
        m = Matrix.Rotation(TRIP, 3, PIN) @ m           # nose up, about the pin
    PAWL.rotation_euler = m.to_euler()
    # the spring, from its shelf to the tail's underside
    tail = PIV + m @ Vector((-TAIL_L, -0.03, 0))
    SPRING.scale.z = tail.z - SPRING.location.z
    bpy.context.view_layer.update()


if "--collide" in argv:
    # Round 11's check: does anything the retrofit added enter the volume a moving part
    # occupies, in any frame? Every added object against every moving one, as one BVH
    # each, in world space; prints the clashes and exits.
    from mathutils.bvhtree import BVHTree

    def tree(objs):
        dg = bpy.context.evaluated_depsgraph_get()
        verts, polys, owner = [], [], []
        for o in objs:
            ev = o.evaluated_get(dg)
            me = ev.to_mesh()
            mw = ev.matrix_world
            base = len(verts)
            verts.extend(mw @ v.co for v in me.vertices)
            for pl in me.polygons:
                polys.append([base + i for i in pl.vertices])
                owner.append(o.name)
            ev.to_mesh_clear()
        return BVHTree.FromPolygons(verts, polys), owner
    retro, r_own = tree(RETRO)
    moving = [o for g in MOVING for o in PARTS.get(g, []) if o.type in ("MESH", "CURVE")]
    clashes = {}
    for f in range(FRAMES):
        pose(f)
        mv, m_own = tree(moving)
        for i, j in retro.overlap(mv):
            clashes.setdefault((r_own[i], m_own[j]), []).append(f)
    print(f"COLLIDE retro objects {len(RETRO)}, moving objects {len(moving)}, frames {FRAMES}")
    for (a, b), fs in sorted(clashes.items()):
        o = bpy.data.objects[a]
        at = o.matrix_world.translation
        print(f"COLLIDE {a} at ({at.x:.3f}, {at.y:.3f}, {at.z:.3f}) x {b}: frames {sorted(set(fs))}")
    print(f"COLLIDE clashes {len(clashes)}")
    sys.exit(0)

if ICON:
    sc.cycles.samples = 128
    pose(RISE)
    # the whole machine, the crown standing proud of its collar (spec 16), with margin:
    # 3.9 tiles across, centred on the drawn machine (base edge 1.5 below the origin to
    # the roof's back 2.1 above), so its silhouette reads at 32 px
    k = 1024 / 3.9
    rig.camera(1024, 1024, centre_px=(512, 512 + k * 0.3), ss=1).data.ortho_scale = 3.9
    setup(visible=STATIC + MOVING)
    rig.render(f"{OUT_DIR}/icon.png")
    sys.exit(0)

contract.declare(OUT_DIR, canvas=CANVAS, **DECL)
rig.camera(*CANVAS)
# what measure_stroke.py needs to hold the frames to the mechanism, without Blender
with open(os.path.join(OUT_DIR, "stroke.json"), "w") as _f:
    json.dump(dict(frames=FRAMES, rise=RISE, travel=TRAVEL, lift=[lift(f) for f in range(FRAMES)],
                   rg=RG, teeth=NG, spokes=5, crown_height=CH,
                   gear_centre_px=[CANVAS[0] / 2 + XG * rig.PX_PER_TILE,
                                   CANVAS[1] / 2 - (YC + ZA * math.cos(rig.ELEVATION)) * rig.PX_PER_TILE],
                   gear_tip=RG + 0.03, hole_r=(HUB + RG - RIM_W) / 2, ss=rig.SS, px_per_tile=rig.PX_PER_TILE,
                   cos_elevation=math.cos(rig.ELEVATION)), _f, indent=1)


def lamp_cut(on):
    b = M["lens"].node_tree.nodes["Principled BSDF"]
    b.inputs["Emission Strength"].default_value = 1.0 if on else 0.0
    b.inputs["Base Color"].default_value = (1, 1, 1, 1) if on else rig.srgb("#E6E4DE")


STROKE = DECL["animations"][0]

for d in contract.each_direction(ROOT, DECL["directions"]):
    def path(stem, d=d):
        return f"{OUT_DIR}/{contract.named(stem, d)}.png"
    sc.render.use_border = False
    pose(0)

    # the plate: everything but the moving parts; the collar complete under the crown
    setup(visible=STATIC)
    rig.render(path("idle"))
    # the stopped machine in one render, every moving part at frame 0
    setup(visible=STATIC + MOVING)
    rig.render(path("still"))
    if IDLE:
        pose(RISE)
        rig.render(f"{OUT_DIR}/top.png")
        break

    setup(visible=STATIC + MOVING, ground=True)
    for o in [o for objs in PARTS.values() for o in objs]:
        o.visible_camera = False
    rig.render(path("shadow"))

    # the lamp: the lens alone, white, everything in front of it cut out
    setup(visible=("lens",), holdouts=tuple(g for g in STATIC + MOVING if g != "lens"))
    lamp_cut(True)
    rig.render(path("lamp"))
    lamp_cut(False)

    # the stroke: 24 frames of the moving parts, their shadows caught on the plate;
    # only the window round the collar changes, so only it is rendered
    sc.render.use_border = True
    sc.render.use_crop_to_border = False
    # the window: pinion to pinion and the crown's shadow east of them; the pawl's
    # spring at the bottom to the crown's top at the top of the stroke, with margin
    sc.render.border_min_x, sc.render.border_max_x = 0.15, 0.95
    sc.render.border_min_y, sc.render.border_max_y = 0.48, 1.0
    for f in range(FRAMES):
        pose(f)
        setup(visible=MOVING, catchers=STATIC)
        rig.render(path(contract.frame(STROKE["name"], f)))
    # the east gear alone, in every frame: not packed, what measure_stroke.py holds to
    # the rack's travel
    for f in range(FRAMES):
        pose(f)
        setup(visible=("gears",))
        for o in PARTS["gears"]:
            o.hide_render = o.parent is None or not (o.parent == GEARS[1] or o.parent.parent == GEARS[1])
        rig.render(f"{OUT_DIR}/diag-gear-{f:02d}.png")
    # the tracked part (contract: track): the crown and shank alone, whole, on the full
    # canvas -- the long shank would run out of the stroke's window -- measured by
    # pack.py's slide check and never packed
    sc.render.use_border = False
    for f in range(FRAMES):
        pose(f)
        setup(visible=("crown", "shank"))
        rig.render(path(contract.track_frame(STROKE["name"], STROKE["track"], f, d)))
    pose(0)
