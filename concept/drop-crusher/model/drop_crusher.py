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
    def build(bm):
        rows = []
        for z in (z0, z1):
            rows.append([bm.verts.new(wall(a0 + (a1 - a0) * k / n, z)) for k in range(n + 1)])
        for k in range(n):
            bm.faces.new((rows[0][k], rows[0][k + 1], rows[1][k + 1], rows[1][k]))
    return build


# the wall in plates, each its own object and so its own tone (the furnace's way); two
# of them replaced since, in fresher primer (the signature finish's variation): the
# upper course west of the old lamp boss, and the middle course east of the hatch
REPLACED = {(236.25, COURSES[2]), (281.25, COURSES[1])}
for a in SEAMS:
    for z0, z1 in zip(COURSES, COURSES[1:]):
        p = mesh_object("stave", stave(a, a + 22.5, z0, z1), "fresh" if (a, z0) in REPLACED else "armour", "hull",
                        bevel=0.0, smooth=True)
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
