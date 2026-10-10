"""Ballast drill (sae-ballast-drill), built from its spec, rendered in every pass.

  blender -b --python ballast_drill.py -- <out-dir> [--idle | --ports | --icon | --chutes | --blend]
  BLENDER=/usr/bin/blender tools/blender/render.sh concept/ballast-drill/model/ballast_drill.py <out-dir> --ports --icon

  --idle    idle-north.png, still-north.png and top.png (frame 7: seated, the dust out): the quick loop
  --ports   the four pipe pictures and their caps, port-<face>.png and cover-<face>.png
  --icon    icon.png: the whole machine, ring raised, every bay shut
  --chutes  debugging: each direction's chute frame 0 alone, to measure its crop
  --doors   debugging: each direction's shut hatch alone (door-<d>.png)
  --f0      debugging: north's plate, still and both frame 0s only
  --dust    debugging: every direction's dust frames only (dust-NN-<d>.png)
  --blend   the scene as built, saved, not rendered
  --samples=N, --iron-gain=, --ore-gain=, --warm=, --edge=, --contact=, --sand=, --bump=, --sheen=,
  --pits=, --flat-dust=
            debugging: tuning the finish at low samples; the defaults are the finished values

The finished model, round 7 (rounds 1 to 3 as below, then what rounds 3 to 7 changed).

Round 7 (the task's amendment of 2026-10-10, "motion and ring signed off; the silhouette":
beside vanilla's big mining drill it read as a square tray of boxes, FFF #350). The ring and
its motion are as round 6 left them. Every face's middle three tiles still meet the edge
(the chute's bay and, turned, both fluid connections use them), so the outline is broken
at the corners and in height:
  - the corner notches deeper (2.1 to 1.85); the legs round tapered cast columns, banded,
    splayed to round pads set in from the corners, ground showing round them;
  - the south corner wings cantilevered out over the notches, each propped from its pad
    by three diagonal braces; on the south-west wing the hydraulic reservoir, a round tank
    along the wing's diagonal edge and overhanging it; on the south-east two accumulator
    bottles on a bracket out over the corner;
  - the accent (Liam: "as vanilla's big drill carries its red"): the press frame -- the
    gear-houses and their drive cabinets -- and the tank and bottles painted red oxide over
    the iron, chipped back to it; the gear-houses' roofs with rolled edges and rivet rows;
  - more services: the reservoir's feed to the south-west snubber, the bottles' hoses down
    into the corner to the jack, a festoon of cables and a hose looping down each side from
    the drive cabinets, a bundle clipped along every leg;
  - the sun 6.0 to 7.2 and the edge line 1.2 to 1.5, for the highlights (p95).

Round 6 (the task's amendment of 2026-10-10, "a heavier ring, and weight at the landing";
spec 3.2 and 3.3 as Liam agreed them that day):
  - the ring narrower in plan (3.14 across to 2.6) and its band deeper (0.55 to 0.75), so its
    outer wall shows in the camera as a cast band: a cast lip round the top in lighter iron,
    overhanging so a dark contact line lies under it; webs down the wall worn bright on their
    edges; a foot flange. Its iron within spec 3.3's #3A3A3C to #5A5A5E, three values apart:
    the wall darkest, the top and spokes lighter and dusted, a recessed web plate between
    the spokes (a lightening hole in each bay) and the inner wall under a crust of ore. The
    well and the shoulder narrowed with it, the well's floor raised to the cutting head's
    crown, cast gussets round the shoulder;
  - four lugs on the band's foot land on four hydraulic snubbers on the deck, on the
    diagonals, each with its hose to a housing: the dead stop, and machinery in the space
    the ring gave up; ore dust drifted over the flat round the shoulder;
  - the stroke: a slow lift, a short hang, a fall under gravity and a dead stop with a
    one-pixel rebound (W_DROP), in place of the sine;
  - the jolt: the press frame above the deck (gear-houses, winches, roof fittings, cables,
    the slung hose) is the "frame" group, drawn in the stroke's frames and not the plate; it
    kicks two pixels at the landing, the slung hose swings, the winches' gears turn with
    the rope;
  - the dust: a ring of ore dust breaking out from under the band at the landing, its own
    working layer ("dust", 24 frames in step with the stroke), neutral pale grey for the
    ore's tint;
  - black: the bays' east and west walls' lining had z-fought the chassis's cut face (and
    the well's floor its own), so the pale lining never showed; both fixed. The gear-houses
    lined inside. The edge line up (0.8 to 1.2), the warm cavity fill up (2.2 to 2.8).

Round 5 (Liam's amendment, 2026-10-09: "let the corners rise" -- tall housings and machinery
in all four corner quadrants, which may partly hide the north chute and the pipe stubs):
  - south-west and south-east: the cores to 2.1, the wings to 1.75 (still under the east and
    west chutes' screen line); on the south-west a machinery cabinet stepped up on the roof
    to 2.55, louvred, the breather on it; on the south-east a front step to the wall, over
    the south pipe stub;
  - north-east and north-west: each gear-house closed down to the deck by a drive cabinet on
    its outer edge (outboard of the shoe's sweep), stepped inward north of the sweep under
    the winch's platform, a louvred door and a hatch on its faces; it takes the rear leg,
    the accumulator and the conduit's riser; the starter cabinets taller;
  - a slack hose and an interlock bundle slung between the gear-houses' roofs behind the
    column, high over the ring's travel;
  - the material's contact lines eased (0.4) and the warm fill in sheltered places raised
    (2.2), against the new shadows.

Round 4 (the services, less machined, FFF #146 and #350; below):

Round 4 (Liam, beside vanilla's big mining drill: "we need to add more wiring and hoses
and things, to make it look similar to vanilla factorio assets; these look too well
machined"; with Wube's FFF #146 and #350 on building art):
  - services (5b): ribbed rubber hoses with crimped ends, zip-tied bundles of insulated
    cable in dull red, blue, green, yellow and black, ladder trays, junction boxes on
    welded brackets, the rams' bulkheads, an accumulator under the north-west house, a
    fan cowl and a reservoir on the gear-houses' roofs, levelling jacks on the south legs'
    pads, oil where the hydraulics leak. Laid where this camera sees them (roofs, south
    faces, wings, legs, the deck flanking the bays), each run draped on the body as built
    by ray casts, so it rests on what is under it; none in a bay, over a chute's crop or
    in the ring's travel;
  - less machined: the two gear-houses different castings (the north-east a replacement,
    another iron, four stiffeners, a roof hatch, a welded patch); every bolt head turned
    its own way; grime streaks down the houses;
  - the crown is gone (it read as a big X across the machine): the guide columns stand
    free, the north ones under their houses, the south one capped;
  - FFF #146's paint-over, done in the material: a crisp light line on every top edge
    (EDGE), a dark warm line where castings meet (CONTACT); the ring darker and the
    column lighter, so ring, column, housings and deck separate in value;
  - FFF #350's force: more ore, thrown harder (44 chunks, a 7-frame life). The ring keeps
    the sine Liam chose on 2026-10-02;
  - the west port declares a neck (pack_ports.py, 1f0847b).

The finished model, round 3 (rounds 1 and 2 as below, then what round 3 changed).

Round 3 (Liam, 2026-10-09: "the drill should look bulkier, look at the heavy mining
drill"; the task's amendment of that date). Started by one artist and finished by
another from the half-changed file, not from round 2's: what the first had added --
the gear-houses, the crown, the north perimeter castings, the heavier guide columns,
the starter cabinets, the per-casting tone, the warm cavities -- was the brief's, and
was kept, then corrected where the renders showed it wrong:
  - mass: the gear-houses enclose the winches on the north columns' heads (roof 2.94,
    the plate's drawn top -192 px, vanilla's big drill's own); a crown bridges the two
    houses over the column as a girder (web, top and bottom flanges, stiffeners). A
    third arm to the south guide column, and that column run up to meet it, were taken
    out again: drawn in front of the central column, it hid it. The south corners carry
    two cast housings (1e) -- hydraulics south-west, with the lamp on its roof;
    switchgear south-east, "50" cast raised on its roof -- each a core to 1.85 beside the
    south band and a wing to 1.35 over the corner notch, sized by what they must not
    hide (1e says how). The south perimeter castings and the deck's hydraulic box went
    into them;
  - surface: layered's scratch mask is off on the iron (its marks are pure white, and
    read as speckled granite at 1x); bright wear stays on the edges (iron's edge wear
    raised to 0.85), the bolts, the polished bands and the hammered landing face. Warm
    dirt in every cavity and at the foot of every casting (AO at 0.35 and 0.7), the
    well under a pale crust of ore; ore dust heavier in the corners and beside the bays;
    per-part tone (jitter 0.2) and per-casting cells. The hatches carry one small worn
    chevron, not two bright ones;
  - the ore is measured against our own chute's mouth (measure_ore.py), not vanilla's
    particle shift.

The finished model, round 1. The design is the blockout Liam signed off (round 3,
review-blockout.png; the task's amendment of 2026-10-09), which keeps the adopted Ring
Press's mechanism (graphics/entity/ballast-drill/base.png, adopted/B-sheet.png,
options/B-ring-press.md) under today's rules. The task: .claude/tasks/ballast-drill-model.md.

THE FORM (the signed-off blockout):
  - no deck slab: a raised cast chassis 0.2 off the ground, its wall at the footprint edge
    along the middle three tiles of every face, its top battered up to the press. Round
    each face's centre it steps down to a 0.2 bolted apron, 1.4 wide, from the edge in to
    a riser at 1.63; down the apron's middle runs a slot, shut in the plate by a flush
    bolted hatch hinged at the riser (1b);
  - four splayed legs from the corner notches to broad foot pads, the pads' edges the
    only hazard banding (3.3);
  - the well round the column, the landing shoulder the ring seats on, and under the
    chassis the cutting head's shroud;
  - the fixed column, tall and capped as the adopted plate draws it;
  - the ring: a cast annulus 3.14 across, chamfered, with cast webs on its top face, a hub
    on the column and six spokes, riding three guide columns at 30, 150 and 270 degrees:
    the two north ones outside the ring, wrapped by shoes on arms, the south one through
    a bossed bore in the band. (The adopted plate stands its winches east and west;
    anywhere south of the east-west line they stood in front of a chute.) A spoke runs to
    every column;
  - a winch on each north column's head: a spur gear upright in the east-west plane, its
    lower half in a guard, a copper drum on the same north-south shaft, a motor and
    pinion; from each drum a wire rope down to an eye on the ring's shoe;
  - the white status-lamp lens on a boss on the chassis top, south-west;
  - the chute: a short drag-chain conveyor at ground level in the bay the ore leaves by,
    the slot's width and level with the apron, so it covers the shut hatch; its own layer
    per direction, turned with the drill, 5 frames of the chain advancing one flight;
  - ore particles: neutral pale grey chunks spilling off the chute's head and falling
    just past the mouth, 24 frames, per direction, drawn only while mining.

THE FINISH (spec 3.3, the signature finishes, Liam 2026-10-09): raw cast iron. No paint:
the chassis, legs and ring graphite grey #3A3A3C to #5A5A5E with a faint blue-black
mill-scale sheen; ore dust #7A6A55 heavy on every ledge; hazard banding on the leg feet
only. Within the building: two replacement panels in a slightly different shade, small
stencilled markings, and rust that differs by place -- dry orange on tops, dark wet
streaks below the fittings. All through materials.layered's hooks (pattern, rust_tint,
drips, ground), extended in this file (cast_iron below) for the ore dust, the dry rust
and the sheen: tools/blender/materials.py is not changed.

The body and the ring are the same in every direction; only the chute and its particles
turn. So they hang from BODY (inside the rig's stretch, never turned) and the chute from
the rig's turntable, which contract.each_direction turns.

The stroke (spec 3.2, Liam 2026-10-10, in place of the sine of 2026-10-02): frame 0 is the
ring raised, as the adopted plate has it; it hangs, falls TRAVEL onto the shoulder, lands
dead at frame 5 with a one-pixel rebound, and is winched slowly back up (W_DROP), 24 frames
at animation_speed 0.4. TRAVEL is the adopted stroke's 12 px on the screen. The stroke's
frames carry the ring, hub, spokes, shoes and ropes, the press frame above the deck (round
6: it jolts at the landing), and paint the surfaces under the
ring (the well, its step, the shoulder) lit for real in each frame: a shadow caught on
them came out darker than the still (the catcher darkens in linear light, the plate it
lands on has been through the rig's contrast look). Approved by the orchestrator,
2026-10-09, and accepted at about 3 % in the task's amendment. The column stays in the
plate.

Units are tiles; north is +Y. A model point (x, y, z) lands on screen at
(x, y + z/2) tiles from the origin.
"""
import json
import math
import os
import random
import re
import shutil
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "blender"))

import rig  # noqa: E402
import contract  # noqa: E402
from materials import layered, _G  # noqa: E402   _G: the node helper, to extend a layered finish here

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = argv[0]
os.makedirs(OUT_DIR, exist_ok=True)
IDLE = "--idle" in argv
PORTS = "--ports" in argv
ICON = "--icon" in argv
CHUTES = "--chutes" in argv
DOOR_ONLY = "--doors" in argv
DUST_ONLY = "--dust" in argv              # debugging: every direction's dust frames alone
F0 = "--f0" in argv

# ---------------------------------------------------------------- the stroke, the chain, the ore

FRAMES = 24
TRAVEL = 0.375                     # tiles of drop: the adopted stroke's 12 px (stroke.json rail [0, 12])


# Round 6 (spec 3.2, Liam 2026-10-10: "rises slowly and drops hard"; it replaces the sine of
# 2026-10-02): over the same 24 frames, a short hang at the top (23, 0, 1), a fall under
# gravity (2 to 5: 1/16, 4/16, 9/16, 16/16 of the travel, so the last frame moves 5 px), a
# dead stop on the shoulder at frame 5 with a one-pixel rebound at 6 and down again at 7,
# seated to 12, and a slow winched lift from 13 to 23.
LAND = 5


def _lift(f):
    u = (f - 12) / 12                  # 13..23 -> 1/12..11/12; 24 is frame 0, raised
    return 1 - u * u * (3 - 2 * u)


W_DROP = [0.0, 0.0, 1 / 16, 4 / 16, 9 / 16, 1.0, 0.94, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] + [_lift(f) for f in range(13, 24)]
assert len(W_DROP) == FRAMES
# the jolt: what stands on the chassis above the deck (the gear-houses, winches, their roofs'
# fittings and cables) kicks down at the landing, back up past rest, and settles: in model z,
# 0.06 is two pixels on the screen
W_JOLT = {LAND: 1.0, LAND + 1: -0.45, LAND + 2: 0.2}
JOLT_Z = 0.06


def drop(f):
    """How far below its raised position the ring is in frame f: 0 at frame 0."""
    return TRAVEL * W_DROP[f % FRAMES]


PATH = [[0.0, 0.0, round(-drop(f), 6)] for f in range(FRAMES)]


def w_swing(f):
    """The slung hose's swing about its clips (radians): kicked toward the camera at the
    landing, swinging back and dying out before the next landing."""
    t = (f - LAND) % FRAMES
    return -0.32 * math.exp(-t / 5.0) * math.sin(2 * math.pi * t / 7.0) if t < 14 else 0.0


DUST_LIFE = 9                          # frames from the landing to the dust's last trace
CHAIN_FRAMES = 5                   # vanilla's output: 5 frames
PITCH = 0.125                      # the flights' spacing: the chain advances one in 5 frames
ORE_FRAMES = 24                    # vanilla's output particles: 24 frames

CANVAS = (416, 400)                # origin at (208, 200); the winches' shadow reaches east
PORT_CANVAS = (448, 448)           # the pictures reach a tile outside every face
FACES = "NESW"
DECL = dict(
    footprint=(5, 5),
    directions="four",
    passes=[
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="still", kind="still"),
        dict(name="shadow", kind="shadow", sheet="base-shadow"),
        dict(name="lamp", kind="light", sheet="status-lamp"),
    ],
    # the chute first: the ring is drawn over it, and the stroke's frames are rendered
    # with the chute as a catcher; the ore over both, and only while mining (working)
    animations=[
        dict(name="chute", frames=CHAIN_FRAMES, motion="cycle"),
        dict(name="stroke", frames=FRAMES, motion="slide", path=PATH, track="ring"),
        dict(name="ore", frames=ORE_FRAMES, motion="cycle", working=True),
        # (round 6, spec 3.2) the dust thrown out at the landing: in step with the stroke,
        # drawn only while working; empty but for the frames after the landing
        dict(name="dust", frames=FRAMES, motion="cycle", working=True),
    ],
    # vanilla's big mining drill: W (-2,-1), E (2,-1), S (+-1, 2); turned, the south pair
    # lands on the north face. One picture per face. The west one declares a neck (pack_ports.py,
    # 1f0847b): assembler 3's west outline joins a strip to the rest by a neck too faint to keep
    ports=[dict(tile=(-1, -2), face="N"), dict(tile=(2, -1), face="E"),
           dict(tile=(1, 2), face="S"), dict(tile=(-2, -1), face="W", neck=True)],
)

sc = rig.reset()
# Light paths: the rig leaves Cycles' 12 bounces. This finish is heavy to shade (layered's
# box-projected scans and noises, on hundreds of parts) and at sprite size nothing past
# the second diffuse bounce shows, so four in all: a frame renders in a fraction of the time.
sc.cycles.max_bounces = 4
sc.cycles.diffuse_bounces = 2
sc.cycles.glossy_bounces = 2
sc.cycles.transmission_bounces = 0
sc.cycles.volume_bounces = 0
sc.cycles.transparent_max_bounces = 64    # round 6: the dust's puffs overlap many deep; at 4 a ray
                                          # through more of them stopped, opaque black
for _a in argv:                       # debugging: --samples=N, to time a render's sync against its sampling
    if _a.startswith("--samples="):
        sc.cycles.samples = int(_a.split("=")[1])
PLATE_SAMPLES = sc.cycles.samples     # the plate, the still and the shadow: the rig's 48
# The animations' frames at 16: the finish costs about 4 s a sample on this machine, and
# after the 4x downsample 16 is 256 to a sprite pixel
ANIM_SAMPLES = min(16, PLATE_SAMPLES)
STRETCH = rig.stretch_root()
ROOT = rig.turntable(STRETCH)      # turned per direction: the chute and its ore only
BODY = bpy.data.objects.new("BODY", None)     # never turned: the body and the ring
sc.collection.objects.link(BODY)
BODY.parent = STRETCH

# ---------------------------------------------------------------- materials


# Tuned on the plate's tonal p50 (Liam accepts about 75-78): the iron's albedo at 0.32 of its
# swatch value and the ore dust at 0.7 measure 77, p95 140 (finish round 2, with the deck's
# fittings, the pale liners in shade and the hammered shoulder); the dust adds about 10.
IRON_GAIN = float(next((a.split("=")[1] for a in argv if a.startswith("--iron-gain=")), 0.28))
ORE_GAIN = float(next((a.split("=")[1] for a in argv if a.startswith("--ore-gain=")), 0.5))
# debugging: the open faces' fine detail, tuned by eye at 1x
BUMP = float(next((a.split("=")[1] for a in argv if a.startswith("--bump=")), 0.3))
SHEEN = float(next((a.split("=")[1] for a in argv if a.startswith("--sheen=")), 1.0))
EDGE = float(next((a.split("=")[1] for a in argv if a.startswith("--edge=")), 1.5))       # round 6: 0.8 -> 1.2; round 7: 1.5
CONTACT = float(next((a.split("=")[1] for a in argv if a.startswith("--contact=")), 0.4))
SAND = float(next((a.split("=")[1] for a in argv if a.startswith("--sand=")), 1.0))
WARM = float(next((a.split("=")[1] for a in argv if a.startswith("--warm=")), 2.8))       # round 6: 2.2 -> 2.8
PITS = float(next((a.split("=")[1] for a in argv if a.startswith("--pits=")), 1.0))
FLAT_DUST = float(next((a.split("=")[1] for a in argv if a.startswith("--flat-dust=")), 2.6))


def iron_pattern(lo, hi, scale_amt):
    """Raw cast iron's colour: graphite grey from lo to hi in broad casting variation,
    with blue-black mill scale in patches (spec 3.3)."""
    def pattern(g):
        pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
        cast = g.remap(g.noise(pos, 2.4, detail=3, rough=0.5), 0.4, 0.75)       # mostly toward lo
        col = g.mixc(cast, rig.srgb(lo), rig.srgb(hi))
        sand = g.remap(g.noise(pos, 60, detail=2), 0.3, 0.7, 1.0 - 0.14 * SAND, 1.0 + 0.12 * SAND)   # sand-cast grain
        pits = g.remap(g.noise(pos, 150, detail=1), 0.62, 0.75, 1.0, 1.0 - 0.28 * PITS)        # casting pits, a pixel each
        col = g.mulc(col, g.gray(g.math("MULTIPLY", sand, pits)))
        scale = g.remap(g.noise(pos, 6.5, detail=4, rough=0.6), 0.52, 0.66)
        col = g.mixc(g.math("MULTIPLY", scale, scale_amt), col, rig.srgb("#2B2F37"))
        # each casting its own tone (finish round 3): one random value per plate-sized cell
        cell = g.node("ShaderNodeTexVoronoi", Vector=pos, Scale=1.4).outputs["Color"]
        cell = g.node("ShaderNodeSeparateColor", Color=cell).outputs[0]
        col = g.mulc(col, g.gray(g.remap(cell, 0.0, 1.0, 0.86, 1.14)))
        # the swatch values are the iron's colour in a photo; lit by this rig's sun they
        # come out lighter than vanilla's darks, so the albedo is taken down by IRON_GAIN
        return g.mulc(col, (IRON_GAIN, IRON_GAIN, IRON_GAIN, 1.0))
    return pattern


def cast_iron(name, lo="#3A3A3C", hi="#5A5A5E", ore=0.75, dry=0.35, sheen=0.1, scale_amt=0.4,
              wear=0.3, rust=0.3, drips=(), drip=0.0, ground=0.0, ground_h=0.5, grime=0.7, jitter=0.2,
              metal="#9A9CA2"):
    """The building's signature finish: materials.layered's iron (its wear, cavity rust,
    grime, ground dirt and drips -- the drips and cavity rust dark and wet), extended in
    this file with what layered does not draw:
      ore    ore dust #7A6A55 heavy on every ledge: upward faces, thickest where sheltered
      dry    dry orange rust in patches on the tops
      sheen  the mill scale's faint blue-black sheen: a thin cool coat
    """
    m = layered(name, lo, metal=metal, paint_metal=0.2, paint_rough=0.68, wear=wear, rust=rust,
                dust=0.1, grime=grime, jitter=jitter, pattern=iron_pattern(lo, hi, scale_amt),
                rust_tint=("#2E180C", "#6E3C1C"), drips=drips, drip=drip, ground=ground, ground_h=ground_h)
    t = m.node_tree
    b = t.nodes["Principled BSDF"]
    g = _G(m)
    # (finish round 3) layered's scratch mask draws bright metal across open faces, which
    # read as speckled granite at 1x: narrowed to its strongest marks, so bright wear stays
    # on the edges (its bevel mask), the bolts and the polished faces
    for nd in t.nodes:
        if nd.type == "TEX_IMAGE" and nd.image and "scratch_mask" in nd.image.name:
            for ln in nd.outputs["Color"].links:
                if ln.to_node.type == "MAP_RANGE":
                    # (continued) narrowing was not enough: the mask's marks are pure white, so
                    # they came through whole. Off on the iron's open faces altogether
                    ln.to_node.inputs["To Max"].default_value = 0.0
    col = b.inputs["Base Color"].links[0].from_socket
    rough = b.inputs["Roughness"].links[0].from_socket
    geo = g.node("ShaderNodeNewGeometry")
    pos, normal = geo.outputs["Position"], geo.outputs["Normal"]
    up = g.remap(g.node("ShaderNodeSeparateXYZ", Vector=normal).outputs["Z"], 0.5, 0.9)
    shelter = g.math("SUBTRACT", 1.0, g.node("ShaderNodeAmbientOcclusion", Distance=0.35).outputs["AO"])
    # warm dirt in every cavity and sheltered corner (finish round 3): the shadows carry
    # the ore's brown and the rust's, while the lit faces stay cool iron
    # (continued) stronger and warmer, and at the foot of every casting: AO over a longer
    # reach finds where a wall meets the floor it stands on, and the ore dust and rust that
    # gather there
    foot = g.math("SUBTRACT", 1.0, g.node("ShaderNodeAmbientOcclusion", Distance=0.7).outputs["AO"])
    warm = g.math("ADD", g.math("MULTIPLY", shelter, WARM * 3.0), g.math("MULTIPLY", foot, WARM * 1.2))
    warm = g.math("MULTIPLY", warm, g.remap(g.noise(pos, 10, detail=4), 0.3, 0.7, 0.6, 1.0), clamp=True)
    col = g.mixc(warm, col, g.mixc(g.noise(pos, 26, detail=3), rig.srgb("#5A3420"), rig.srgb("#86603C")))
    if dry:
        patches = g.remap(g.noise(pos, 12, detail=5, rough=0.6), 0.6, 0.72)
        dry_m = g.math("MULTIPLY", g.math("MULTIPLY", up, patches), dry, clamp=True)
        dry_c = g.mixc(g.noise(pos, 34, detail=2), rig.srgb("#8A4A20"), rig.srgb("#B8743A"))
        col = g.mixc(dry_m, col, dry_c)
        rough = g.mixf(dry_m, rough, 0.92)
    if ore:
        # ledges: thick where an upward face is sheltered (against a step, in a corner,
        # round a bolt), drifting thinly across the open tops
        drift = g.remap(g.noise(pos, 8, detail=6, rough=0.6), 0.5, 0.72, 0.0, 0.55)
        heap = g.math("ADD", g.math("MULTIPLY", up, drift), g.math("MULTIPLY", g.math("MULTIPLY", up, shelter), 4.0))
        # heavier beside the bays, where the ore comes out: within the bands either side of
        # each face's centre, out past the riser (model y is world y times sin 60: STRETCH)
        xyz = g.node("ShaderNodeSeparateXYZ", Vector=pos)
        ax = g.math("ABSOLUTE", xyz.outputs["X"])
        ay = g.math("ABSOLUTE", g.math("MULTIPLY", xyz.outputs["Y"], math.sin(rig.ELEVATION)))
        near = g.math("MULTIPLY", g.remap(g.math("MINIMUM", ax, ay), 1.05, 0.72),
                      g.remap(g.math("MAXIMUM", ax, ay), 1.45, 1.7))
        heap = g.math("ADD", heap, g.math("MULTIPLY", g.math("MULTIPLY", up, near), 0.9))
        # (finish round 3) and heavier in the corners, out past the shoulder
        corner = g.math("MULTIPLY", g.remap(g.math("MINIMUM", ax, ay), 0.9, 1.4), g.remap(g.math("MAXIMUM", ax, ay), 1.6, 2.0))
        heap = g.math("ADD", heap, g.math("MULTIPLY", g.math("MULTIPLY", up, corner),
                                          g.remap(g.noise(pos, 7, detail=4), 0.35, 0.65, 0.3, 1.0)))
        # (round 6) and drifted over the flat round the shoulder, out to the housings, where
        # every landing throws it: low surfaces only (the deck, not the roofs)
        rr = g.math("SQRT", g.math("ADD", g.math("MULTIPLY", ax, ax), g.math("MULTIPLY", ay, ay)))
        flat = g.math("MULTIPLY", g.math("MULTIPLY", g.remap(rr, 1.4, 1.52), g.remap(rr, 2.3, 1.95)),
                      g.remap(xyz.outputs["Z"], 1.05, 0.95))
        heap = g.math("ADD", heap, g.math("MULTIPLY", g.math("MULTIPLY", up, flat),
                                          g.remap(g.noise(pos, 5, detail=4), 0.3, 0.7, 0.35, FLAT_DUST)))
        ore_m = g.math("MULTIPLY", heap, ore * ORE_GAIN, clamp=True)
        ore_c = g.mixc(g.noise(pos, 45, detail=2), rig.srgb("#6E5E4A"), rig.srgb("#8C7C63"))
        col = g.mixc(ore_m, col, ore_c)
        rough = g.mixf(ore_m, rough, 0.97)
    # (round 4, after Wube's FFF #146: their renders are hand-finished with masks painted
    # "to enforce contrast, make edges clearer, define shape"; this pipeline has no
    # paint-over, so the material does it) a crisp light line along every top edge, where a
    # painter would catch it, and a dark line wherever one casting meets another
    tight = g.math("SUBTRACT", 1.0, g.node("ShaderNodeAmbientOcclusion", Distance=0.05).outputs["AO"])
    col = g.mixc(g.math("MULTIPLY", tight, CONTACT * 1.6, clamp=True), col, rig.srgb("#2E2016"))
    bev = g.node("ShaderNodeBevel", Radius=0.008).outputs[0]
    dp = g.node("ShaderNodeVectorMath")
    dp.operation = "DOT_PRODUCT"
    g.l.new(bev, dp.inputs[0])
    g.l.new(normal, dp.inputs[1])
    rim = g.remap(dp.outputs["Value"], 0.985, 0.8)
    top_rim = g.math("MULTIPLY", rim, g.remap(g.node("ShaderNodeSeparateXYZ", Vector=normal).outputs["Z"], 0.05, 0.6),
                     clamp=True)
    col = g.mixc(g.math("MULTIPLY", top_rim, EDGE, clamp=True), col, rig.srgb("#D2CFC6"))   # round 7: #B2B0AA
    g.l.new(col, b.inputs["Base Color"])
    g.l.new(rough, b.inputs["Roughness"])
    for nd in t.nodes:
        if nd.type == "BUMP":
            nd.inputs["Strength"].default_value = BUMP
    sheen *= SHEEN
    if sheen:
        b.inputs["Coat Weight"].default_value = sheen
        b.inputs["Coat Roughness"].default_value = 0.4
        b.inputs["Coat Tint"].default_value = (0.78, 0.84, 1.0, 1.0)
    return m


def stripes(g):
    """Hazard stripes at 45 degrees, #C8A23A on a dark ground, chipped by noise (the Drop
    Crusher's banding)."""
    pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
    xyz = g.node("ShaderNodeSeparateXYZ", Vector=pos)
    u = g.math("ADD", xyz.outputs["X"], xyz.outputs["Y"])
    u = g.math("ADD", u, g.math("MULTIPLY", g.noise(pos, 40, detail=2), 0.03))
    band = g.math("GREATER_THAN", g.math("FRACT", g.math("DIVIDE", u, 0.14)), 0.5)
    paint = g.mixc(band, rig.srgb("#C8A23A"), rig.srgb("#26221C"))
    chip = g.remap(g.noise(pos, 22, detail=5, rough=0.6), 0.5, 0.62)
    return g.mixc(chip, paint, rig.srgb("#3E3C3C"))


def plain(name, hexcol, rough=0.9, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(hexcol)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def lens_material():
    """The status lamp's lens, painted white; the light pass lights it white."""
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


WALL_DRIPS = ((0.65, 0.4), (0.87, 0.5), (0.2, 0.18))    # below the wall's top, the batter's edge, the apron
M = {
    # the mass: chassis, legs, apron, riser, the bays' hatches (3.3, signature)
    "iron": cast_iron("iron", drips=WALL_DRIPS, drip=0.8, ground=0.85, wear=0.85, metal="#B4B6BC"),
    "leg": cast_iron("leg", drips=((0.55, 0.45),), drip=0.7, ground=0.9, ground_h=0.4),
    "apron": cast_iron("apron", ore=1.0, dry=0.25, drips=((0.2, 0.18),), drip=0.6, ground=0.7, ground_h=0.25),
    # raised cast features -- ribs, lips, webs, flanges -- worn bright along their edges by
    # boots, chains and tools (round 2: highlights where real wear goes)
    "iron_worn": cast_iron("iron_worn", wear=0.95, metal="#CDCFD4", ore=0.5, dry=0.2),
    "ring_worn": cast_iron("ring_worn", lo="#3E3D41", hi="#5A5A5F", wear=0.95, metal="#C8CACF", ore=0.4,
                           dry=0.2),
    # two replacement panels: newer castings, a touch bluer and less weathered
    "iron_new": cast_iron("iron_new", lo="#44464C", hi="#62656C", ore=0.45, dry=0.1, rust=0.12, wear=0.15,
                          scale_amt=0.6, jitter=0.04),
    # the ring: the same iron, darker (3.3: the ballast, deliberately darker), its chamfers
    # knocked bright
    # (round 4, FFF #146's value separation: the ring is the darkest mass on the machine)
    # (round 6, Liam: the ring no longer near-black over its whole top: three values, the
    # wall still the darkest iron on the machine, the top face and its lip lighter and
    # dusted, the inner wall dustier again, so the well reads apart from it)
    # (spec 3.3 as agreed 2026-10-10: the ring cast iron #3A3A3C to #5A5A5E, its top face,
    # wall and well kept apart in value: the wall at the range's dark end, the top at its
    # light end and dusted, the web plate and inner wall under a crust of ore)
    "ring": cast_iron("ring", lo="#3A3A3C", hi="#5A5A5E", wear=0.8, ore=0.3, dry=0.2, metal="#AEB0B6",
                      drips=((1.0, 0.5),), drip=0.4),
    "ring_top": cast_iron("ring_top", lo="#4E4E51", hi="#5A5A5E", wear=0.9, ore=0.75, dry=0.3, metal="#C4C6CB",
                          scale_amt=0.3),
    "ring_in": cast_iron("ring_in", lo="#4E4E51", hi="#5A5A5E", wear=0.4, ore=1.6, dry=0.2, metal="#A8AAB0"),
    # the column and the press's castings: the chassis's iron
    # (round 4: lighter than the ring round it and the deck under it, so it reads apart)
    "column": cast_iron("column", lo="#505154", hi="#76777B", drips=((2.6, 0.6), (2.08, 0.4)), drip=0.7, ore=0.3),
    # bright worn iron where the ring lands: the shoulder's hammered face
    # (finish round 2: hammered bright, as the adopted sheet's landing shoulder catches the light)
    "anvil": cast_iron("anvil", lo="#6A6C70", hi="#88898D", wear=0.75, ore=0.35, dry=0.08, rust=0.12,
                       metal="#C6C8CC", scale_amt=0.15),
    # guide columns: turned steel, worn bright where the shoes run (3.3: #8A8580)
    "guide": layered("guide", "#8A8580", metal="#D0CCC6", paint_metal=0.7, paint_rough=0.35, wear=0.6,
                     rust=0.18, dust=0.15, grime=0.5, jitter=0.05, rust_tint=("#20140E", "#4A2A1A")),
    # gears: steel, teeth worn bright
    "gear": layered("gear", "#7E7A74", metal="#E2DED6", paint_metal=0.4, paint_rough=0.38, wear=0.85,
                    rust=0.15, dust=0.15, grime=0.4, jitter=0.06),
    "steel": layered("steel", "#5C5C60", metal="#B8B8BC", paint_metal=0.7, paint_rough=0.4, wear=0.5,
                     rust=0.3, dust=0.1, grime=0.5, rust_tint=("#20140E", "#4A2A1A")),
    # bolt heads: their flats rubbed bright by spanners (round 2: highlights)
    "bolt": layered("bolt", "#66666A", metal="#E2E2E6", paint_metal=0.3, paint_rough=0.45, wear=0.9,
                    rust=0.35, dust=0.15, grime=0.4, jitter=0.2, rust_tint=("#3A1E0E", "#8A4A20")),
    # bright worn iron where real wear is (round 2): the ring's top edges and shoe faces,
    # the guide columns' polished bands, the column's wear band, the hatches' edges, the
    # kerbs. Mostly diffuse: a metallic finish only glints at the mirror angle, which this
    # camera rarely sees, and otherwise reflects the dim sky as dark (the crusher's lesson)
    "polish": layered("polish", "#ABADB1", metal="#D0D2D6", paint_metal=0.25, paint_rough=0.42, wear=0.4,
                      rust=0.05, dust=0.1, grime=0.3, jitter=0.06),
    "seam": layered("seam", "#3C3C40", metal="#7A7A80", paint_metal=0.4, paint_rough=0.6, wear=0.3,
                    rust=0.5, dust=0.2, grime=0.7, rust_tint=("#20140E", "#4A2A1A")),
    "copper": layered("copper", "#8A5A32", metal="#D49450", paint_metal=0.9, paint_rough=0.36,
                      wear=0.45, rust=0.1, dust=0.2, grime=0.5, patina=0.35),
    "brass": layered("brass", "#9C7034", metal="#D0A864", paint_metal=0.9, paint_rough=0.36,
                     wear=0.45, rust=0.15, dust=0.2),
    "hazard": layered("hazard", "#C8A23A", paint_metal=0.1, paint_rough=0.85, wear=0.8,
                      rust=0.45, dust=0.9, grime=0.9, ground=0.9, ground_h=0.3, pattern=stripes),
    # stencils: pale paint, sprayed thin and worn
    "stencil": layered("stencil", "#B8B09C", metal="#4A4A4E", paint_metal=0.05, paint_rough=0.9, wear=0.85,
                       rust=0.2, dust=0.6, grime=0.4, jitter=0.05),
    "stencil_worn": layered("stencil_worn", "#7E786A", metal="#4A4A4E", paint_metal=0.05, paint_rough=0.9,
                            wear=0.95, rust=0.3, dust=0.9, grime=0.5, jitter=0.05),
    "chute": cast_iron("chute", ore=0.9, dry=0.3, drips=((0.2, 0.15),), drip=0.5, ground=0.5, ground_h=0.2),
    "flight": layered("flight", "#8A8A8E", metal="#D8D8DC", paint_metal=0.6, paint_rough=0.35, wear=0.8,
                      rust=0.1, dust=0.3, grime=0.4),
    "cable": layered("cable", "#3E3E40", metal="#9A9A9E", paint_metal=0.6, paint_rough=0.5, wear=0.4,
                     rust=0.25, dust=0.05, grime=0.6),
    # pale steel plate lining what stands in shade -- the well, the bands' walls and risers,
    # the slots' floors -- so the shade is coloured, not black (round 2: the plate's black)
    "liner_pale": layered("liner_pale", "#C4C0B6", metal="#D0CEC8", paint_metal=0.15, paint_rough=0.7, wear=0.3,
                          rust=0.2, dust=0.4, grime=0.25, jitter=0.08, rust_tint=("#3A1E0E", "#7A4420")),
    "liner": layered("liner", "#8C8984", metal="#B4B2AC", paint_metal=0.2, paint_rough=0.6, wear=0.35,
                     rust=0.25, dust=0.35, grime=0.35, jitter=0.08, rust_tint=("#20140E", "#4A2A1A")),
    # the well: steel plate under a crust of the ore the cutting head throws up, warm brown
    # where the column's shadow lies (finish round 3: the plate's darkest quarter was grey)
    "welldust": layered("welldust", "#A8946F", metal="#C4BCAE", paint_metal=0.1, paint_rough=0.85, wear=0.25,
                        rust=0.45, dust=0.9, grime=0.45, jitter=0.1, rust_tint=("#3A1E0E", "#7A4420")),
    # the insides of things: lifted off black (round 2: the plate's black share)
    "dark": plain("dark", "#5A4636"),
    "grease": layered("grease", "#2E2822", metal="#3E3830", paint_metal=0.2, paint_rough=0.2,
                      wear=0.0, rust=0.0, dust=0.0, grime=0.2, jitter=0.03),
    # the ore: neutral pale grey, so the engine's resource tint decides its colour
    "ore": plain("ore", "#C6C9CF", rough=0.85),
    "lens": lens_material(),
}
M["port"] = M["iron"]
# The ray-traced nodes' samples: layered's ambient occlusion defaults to 16 rays a shading
# point, and every material here carries one or two. At 4 (and the bevel at 2) the plate
# renders in a fraction of the time and the noise is gone after downsampling.
for _m in {id(m): m for m in M.values()}.values():
    for _n in _m.node_tree.nodes:
        if _n.type == "AMBIENT_OCCLUSION":
            _n.samples = 4
        elif _n.type == "BEVEL":
            _n.samples = 2
M["slab"] = M["iron"]

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
    obj.parent = parent or BODY
    PARTS.setdefault(group, []).append(obj)
    return obj


def box(loc, size, mat, group="body", rot=(0, 0, 0), bevel=0.012, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, group, bevel, parent=parent)


def cyl(loc, r, h, mat, group="body", verts=48, rot=(0, 0, 0), bevel=0.01, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    o = _finish(bpy.context.active_object, mat, group, bevel, smooth=True, parent=parent)
    for p in o.data.polygons:          # the caps flat: a smoothed n-gon cap shades as a dark star
        if len(p.vertices) > 4:
            p.use_smooth = False
    return o


def sphere(loc, r, mat, group="body", parent=None, squash=1.0, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=max(6, seg // 2))
    o = bpy.context.active_object
    o.scale.z = squash
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, group, bevel=0, smooth=True, parent=parent)


_BOLT_RNG = random.Random(4417)


def bolt(loc, r=0.018, h=0.014, mat="bolt", group="body", rot=(0, 0, 0), parent=None):
    """A hex head, turned to wherever its spanner left it (round 4: in rows all square to
    each other they read as machined)."""
    o = cyl(loc, r, h, mat, group, verts=6, rot=(0, 0, 0), bevel=0.0, parent=parent)
    from mathutils import Euler
    o.rotation_euler = (Euler(rot).to_matrix() @ Matrix.Rotation(_BOLT_RNG.uniform(0, math.pi / 3), 3, "Z")).to_euler()
    return o


def rivet(loc, r=0.014, mat="bolt", group="body", parent=None):
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


def stack(levels, mat, group="body", bevel=0.01, parent=None, name="stack"):
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
    o = mesh_object(name, build, mat, group, bevel, parent=parent)
    t = o.modifiers.new("tri", "TRIANGULATE")        # concave caps: triangulate before render
    t.min_vertices = 5
    return o


def lathe(profile, mat, group="body", parent=None, verts=128, bevel=0.0, loc=(0, 0, 0), smooth=True):
    """A closed solid of revolution about local Z through profile [(r, z), ...], a loop."""
    def build(bm):
        rows = [[bm.verts.new((r * math.cos(2 * math.pi * i / verts), r * math.sin(2 * math.pi * i / verts), z))
                 for i in range(verts)] for r, z in profile]
        n = len(rows)
        for k in range(n):
            a, b = rows[k], rows[(k + 1) % n]
            for i in range(verts):
                j = (i + 1) % verts
                bm.faces.new((a[i], a[j], b[j], b[i]))
    o = mesh_object("lathe", build, mat, group, bevel, smooth=smooth, parent=parent)
    o.location = loc
    return o


def ring(loc, r_out, r_in, h, mat, group="body", parent=None, verts=96, bevel=0.01, rot=(0, 0, 0)):
    """A thick washer about local Z: open through the middle."""
    o = lathe([(r_out, -h / 2), (r_out, h / 2), (r_in, h / 2), (r_in, -h / 2)], mat, group, parent, verts, bevel)
    o.location, o.rotation_euler = loc, rot
    return o


def strut(a, b, w0, d0, w1, d1, mat, group="body", parent=None, bevel=0.015):
    """A tapered bar from a to b: w across it in plan, d the other way; w0/d0 at a, w1/d1 at b."""
    a, b = Vector(a), Vector(b)
    u = (b - a).normalized()
    s = u.cross(Vector((0, 0, 1)))
    s = s.normalized() if s.length > 1e-6 else Vector((1, 0, 0))
    t = s.cross(u).normalized()

    def build(bm):
        v = []
        for c, w, d in ((a, w0, d0), (b, w1, d1)):
            for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                v.append(bm.verts.new(c + s * (i * w / 2) + t * (j * d / 2)))
        bm.faces.new((v[3], v[2], v[1], v[0]))
        bm.faces.new((v[4], v[5], v[6], v[7]))
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((v[i], v[j], v[4 + j], v[4 + i]))
    return mesh_object("strut", build, mat, group, bevel, parent=parent)


def side_plate(x, thick, poly_yz, mat, group, parent=None, bevel=0.006):
    """A plate in the y-z plane at x, `thick` across, through the outline poly_yz."""
    def build(bm):
        a = [bm.verts.new((x - thick / 2, y, z)) for y, z in poly_yz]
        b = [bm.verts.new((x + thick / 2, y, z)) for y, z in poly_yz]
        bm.faces.new(a)
        bm.faces.new(list(reversed(b)))
        n = len(a)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[j], a[i], b[i], b[j]))
    return mesh_object("plate", build, mat, group, bevel, parent=parent)


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.parent = parent or BODY
    e.location, e.rotation_euler = loc, rot
    return e


def cutter_cyl(loc, r, h, parent=None, verts=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc)
    o = bpy.context.active_object
    o.parent = parent or BODY
    o.hide_render = True
    o.display_type = "WIRE"
    return o


def cut(obj, *cutters):
    """Cut obj by the cutters, then triangulate: a cut cap leaves a concave n-gon."""
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


def gear(loc, r, teeth, thick, mat, group, parent=None, rot=(math.pi / 2, 0, 0), spokes=0):
    """A spur gear about its local Z (by default turned to lie in the x-z plane, its axis
    north-south): a web, a rim of teeth, a boss; with spokes, lightening holes between."""
    g = empty("gear", loc, rot, parent=parent)
    cyl((0, 0, 0), r - 0.03, thick, mat, group, verts=64, bevel=0.006, parent=g)
    for k in range(teeth):
        a = 2 * math.pi * k / teeth
        box(((r - 0.015) * math.cos(a), (r - 0.015) * math.sin(a), 0), (0.05, 2 * math.pi * r / teeth * 0.5, thick),
            mat, group, rot=(0, 0, a), bevel=0.004, parent=g)
    ring((0, 0, 0), r - 0.035, r - 0.07, thick + 0.02, mat, group, parent=g, verts=64, bevel=0.004)  # its rim
    cyl((0, 0, 0), 0.07, thick + 0.06, mat, group, verts=32, bevel=0.006, parent=g)
    for k in range(spokes):                              # a dark recess between each pair of arms
        a = 2 * math.pi * (k + 0.5) / spokes
        cyl(((r * 0.55) * math.cos(a), (r * 0.55) * math.sin(a), 0), r * 0.17, thick + 0.004, "dark", group,
            verts=20, bevel=0.0, parent=g)
    return g


def stencil(loc, rot, glyphs, size=0.06, group="body", parent=None, mat="stencil", h=0.003):
    """A small marking: glyphs as rows of '#' and '.', each '#' a square laid in the local
    x-y plane at loc -- sprayed paint (the stencil material, a hair thick) or, given an
    iron and a height, figures cast raised in the plate."""
    e = empty("stencil", loc, rot, parent=parent)
    rows = glyphs.split("/")
    for j, row_ in enumerate(rows):
        for i, ch in enumerate(row_):
            if ch == "#":
                box((i * size, -j * size, h / 2 - 0.0015), (size * (0.92 if h < 0.005 else 1.0), size * (0.92 if h < 0.005
                    else 1.0), h), mat, group, bevel=0.0 if h < 0.005 else 0.003, parent=e)
    return e


def arc(r_out, r_in, z, h, a0, a1, mat, group="body", parent=None, cx=0.0, cy=0.0, n=24, bevel=0.002):
    """A short arc of ring from a0 to a1 degrees about (cx, cy): wear worn bright only where
    it is worn, or a pocket, not a whole hoop."""
    def build(bm):
        rows = []
        for r, zz in ((r_out, z - h / 2), (r_out, z + h / 2), (r_in, z + h / 2), (r_in, z - h / 2)):
            rows.append([bm.verts.new((cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
                                       cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)), zz))
                         for k in range(n + 1)])
        for k in range(4):
            a, b = rows[k], rows[(k + 1) % 4]
            for i in range(n):
                bm.faces.new((a[i], a[i + 1], b[i + 1], b[i]))
        bm.faces.new([rows[k][0] for k in range(4)])
        bm.faces.new([rows[k][n] for k in reversed(range(4))])
    return mesh_object("arc", build, mat, group, bevel, parent=parent)


def pipe(pts, r, mat, bend=0.05, group="body", parent=None):
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
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(out) - 1)
    for pt, co in zip(sp.points, out):
        pt.co = (*co, 1)
    ob = bpy.data.objects.new("pipe", cu)
    sc.collection.objects.link(ob)
    return _finish(ob, mat, group, bevel=0, parent=parent)


def eye(loc, a, mat="steel", group="body", parent=None, r=0.035, tilt=0.0):
    """A lifting eye: a bolted foot and a ring upright in the vertical plane at heading a
    (radians) -- upright in its plane, never tilted to the camera; tilt stands it square
    to a sloping face."""
    e = empty("eye", loc, (tilt, 0, a), parent=parent)
    box((0, 0, 0.012), (0.09, 0.05, 0.024), mat, group, parent=e, bevel=0.005)
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.011, location=(0, 0, 0.024 + r),
                                     rotation=(math.pi / 2, 0, 0), major_segments=20, minor_segments=8)
    _finish(bpy.context.active_object, mat, group, bevel=0, smooth=True, parent=e)
    return e


def along(p, t, r, h, mat, verts=16, back=0.0):
    """A short cylinder of radius r and length h on the line through p along t, set back."""
    rot = Vector((0, 0, 1)).rotation_difference(t.normalized()).to_euler()
    c = p - t.normalized() * (back + h / 2)
    return cyl(tuple(c), r, h, mat, verts=verts, rot=tuple(rot), bevel=0.0)


def weld(a, b, r=0.006):
    """A weld bead from a to b."""
    a, b = Vector(a), Vector(b)
    return along(b, b - a, r, (b - a).length, "seam", verts=8)


# ---------------------------------------------------------------- 1. the chassis

E = 2.495                            # the wall's face: the footprint edge, less a hair
NX = 1.5                             # the wall meets the edge along the middle three tiles
NC = 1.85                            # the corner notch's 45-degree face, from (NX, NC) to (NC, NX)
                                     # (round 7: 2.1 -> 1.85, deeper, so ground shows round the legs:
                                     # FFF #350, no square entities)
ZB, HC = 0.2, 0.65                   # the chassis's underside and its top: raised off the ground


def chassis_outline(e=E, nx=NX, nc=NC):
    q = [(nx, -e), (nx, -nc), (nc, -nx), (e, -nx)]                   # south-east quarter, east-going
    pts = [(-nx, -e)]
    for k in range(4):
        rot = Matrix.Rotation(math.pi / 2 * k, 2)
        for p in q:
            v = rot @ Vector(p)
            pts.append((v.x, v.y))
    return pts[:-1]                                                  # the last is the first again


# battered: the wall stands to HC at the footprint edge, and the top rises from it to
# ZT round the press, so the casting climbs toward the ring instead of lying flat
EI = 2.0                              # where the batter meets the flat round the shoulder
ZT = HC + 0.22
SLOPE_B = math.atan2(ZT - HC, E - EI)  # the batter's slope


def top_z(r):
    """The chassis top's height at distance r (along a face's normal) from the centre."""
    return ZT if r <= EI else ZT - (ZT - HC) * (r - EI) / (E - EI)


_out = chassis_outline()
CHASSIS = stack([(_out, ZB), (_out, HC), (chassis_outline(EI, 1.3, 1.75), ZT)],
                "iron", bevel=0.012, name="chassis")
# the well round the column, open to the cutting head below
# (round 6: the ring narrower in plan, so the well and the shoulder with it)
# and its floor raised to the cutting head's crown, so the ring's interior is a shallow
# lit floor between the spokes, not a black pit
WELL_R, WELL_Z = 0.9, 0.62
cut(CHASSIS, cutter_cyl((0, 0, ZT), WELL_R, 2 * (ZT - WELL_Z), verts=96))
# The surfaces under the ring are their own group, "under": the stroke's frames paint them
cyl((0, 0, WELL_Z - 0.01), WELL_R + 0.01, 0.04, "welldust", "under", verts=96, bevel=0.0)       # the well's floor
# (round 6: proud of the chassis's cut face by 0.01, which it z-fought once raised)
# its wall lined in pale steel plate, bolted: the well sits in the column's and the
# shoulder's shadow, and in bare iron it was most of the plate's black (round 2)
ring((0, 0, (WELL_Z + ZT) / 2), WELL_R + 0.005, WELL_R - 0.02, ZT - WELL_Z, "welldust", "under", verts=96, bevel=0.0)
for k in range(24):
    t = 2 * math.pi * (k + 0.5) / 24
    bolt(((WELL_R - 0.022) * math.cos(t), (WELL_R - 0.022) * math.sin(t), (WELL_Z + ZT) / 2), 0.016, 0.012,
         rot=(0, math.pi / 2, t), group="under")
ring((0, 0, WELL_Z + 0.05), 0.8, 0.56, 0.1, "welldust", "under", verts=96)                      # a step round the column's foot
for k in range(14):
    t = 2 * math.pi * (k + 0.5) / 14
    bolt((0.68 * math.cos(t), 0.68 * math.sin(t), WELL_Z + 0.105), 0.02, 0.016, group="under")
# the cutting head's shroud under the chassis: a dark rim, seen in the gap at the front
cyl((0, 0, ZB / 2 + 0.005), 1.35, ZB - 0.01, "dark", verts=96, bevel=0.01)
for k in range(24):                                   # its teeth, just showing at the rim
    t = 2 * math.pi * (k + 0.5) / 24
    box((1.36 * math.cos(t), 1.36 * math.sin(t), 0.05), (0.05, 0.05, 0.08), "steel", rot=(0, 0, t), bevel=0.006)

# the landing shoulder: the annulus the ring seats on, its face hammered bright
SH_OUT, SH_IN = 1.4, WELL_R
ZS = ZT + 0.14                        # its top: where the ring's underside lands
ring((0, 0, (ZT + ZS) / 2 - 0.01), SH_OUT, SH_IN, ZS - ZT - 0.02, "iron", "under", verts=128, bevel=0.015)
ring((0, 0, ZS - 0.012), 1.34, 0.96, 0.024, "anvil", "under", verts=128, bevel=0.006)        # the landing face
for k in range(28):                                   # its bolts round the outer edge
    t = 2 * math.pi * (k + 0.5) / 28
    bolt(((SH_OUT + 0.006) * math.cos(t), (SH_OUT + 0.006) * math.sin(t), ZS - 0.05), 0.016, 0.014,
         rot=(0, math.pi / 2, t), group="under")
# (round 6) cast gussets round the shoulder's outer wall, between its bolts: it is the anvil
# the ring's weight lands on, and reads as one
for k in range(14):
    t = 2 * math.pi * k / 14
    box(((SH_OUT + 0.02) * math.cos(t), (SH_OUT + 0.02) * math.sin(t), (ZT + ZS) / 2 - 0.01), (0.07, 0.04, ZS - ZT - 0.03),
        "iron_worn", "under", rot=(0, 0, t), bevel=0.008)

# the four legs: from the corner notch's face, raked down and out to a pad in the corner
# (round 7, the silhouette: round cast columns, tapered, splayed to round pads set in from
# the corner, ground showing round them; were square struts to square pads flush with it)


def rod(a, b, r0, r1, mat, group="body", seg=24, parent=None):
    """A round tapered column from a (radius r0) to b (radius r1)."""
    a, b = Vector(a), Vector(b)

    def build(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r0, radius2=r1, depth=(b - a).length)
    o = mesh_object("rod", build, mat, group, 0.0, smooth=True, parent=parent)
    for pl in o.data.polygons:
        if len(pl.vertices) > 4:
            pl.use_smooth = False
    o.rotation_euler = Vector((0, 0, 1)).rotation_difference(b - a).to_euler()
    o.location = (a + b) / 2
    return o


PAD = 2.12                                     # the pads' centres, in from the corners
LEGS = {}
for sx in (-1, 1):
    for sy in (-1, 1):
        d = Vector((sx, sy, 0)).normalized()
        root = Vector((sx * (NX + NC) / 2, sy * (NX + NC) / 2, (ZB + HC) / 2 + 0.02))
        foot = Vector((sx * PAD, sy * PAD, 0.17))
        rod(root - d * 0.1, foot, 0.2, 0.15, "leg")
        for t, rr in ((0.25, 0.215), (0.75, 0.18)):                               # cast bands round it
            c = (root - d * 0.1).lerp(foot, t)
            rod(c - (foot - root).normalized() * 0.03, c + (foot - root).normalized() * 0.03, rr, rr, "iron_worn")
        LEGS[(sx, sy)] = (root - d * 0.1, foot)
        # its root: a bolted flange on the notch face
        box(tuple(root - d * 0.02), (0.44, 0.07, 0.46), "leg", rot=(0, 0, math.atan2(sy, sx) + math.pi / 2),
            bevel=0.012)
        for i in (-1, 1):
            for j in (-1, 1):
                p = root + d * 0.02 + Vector((-sy, sx, 0)).normalized() * (0.16 * i) + Vector((0, 0, 0.16 * j))
                bolt(tuple(p), 0.02, 0.02, rot=(math.pi / 2, 0, math.atan2(sy, sx) + math.pi / 2))
        # the pad: a round cast foot, its rim banded (3.3: the leg feet only), anchored
        cyl((sx * PAD, sy * PAD, 0.045), 0.34, 0.09, "hazard", verts=48, bevel=0.02)
        cyl((sx * PAD, sy * PAD, 0.1), 0.27, 0.03, "leg", verts=48, bevel=0.01)
        cyl((sx * PAD, sy * PAD, 0.15), 0.21, 0.08, "leg", verts=48, bevel=0.015)       # its boss
        for k in range(6):
            t = 2 * math.pi * (k + 0.5) / 6
            bolt((sx * PAD + 0.25 * math.cos(t), sy * PAD + 0.25 * math.sin(t), 0.12), 0.022, 0.022)

# ---------------------------------------------------------------- 1a. the chassis's make-up
#
# A casting, so no rivets in its body: bolt rows where it is built up from sections, weld
# seams where they were joined, its top's sections bolted round the shoulder.


def on_top(x, y):
    """A point on the chassis top at plan (x, y): on the batter, or the flat round the press."""
    r = max(abs(x), abs(y))
    return top_z(r)


# bolts round the shoulder's foot, on the flat
for k in range(40):
    t = 2 * math.pi * (k + 0.5) / 40
    x, y = 1.72 * math.cos(t), 1.72 * math.sin(t)
    if min(abs(x), abs(y)) < 0.76:                       # the bands
        continue
    bolt((x, y, ZT + 0.007))
BLOCK_FACES = (0, 2)                                   # south and north: the perimeter castings (1d)
# bolt rows along the wall's top edge, and along the batter's inner edge, either side of
# each band; a weld seam down the batter between them
for k4 in range(4):
    rot = Matrix.Rotation(-math.pi / 2 * k4, 2)
    for lat in [0.78 + 0.1 * i for i in range(7)] + [-0.78 - 0.1 * i for i in range(7)]:
        for r in (E - 0.05, EI - 0.03):
            if r < EI and k4 in BLOCK_FACES:
                continue                                 # the perimeter casting stands there (1d)
            p = rot @ Vector((lat, -r))
            # the inner row bolts down the cast lip along the batter's edge (1c)
            bolt((p.x, p.y, (top_z(r) + 0.007) if r > EI else ZT + 0.037), 0.016, 0.014, rot=(0, 0, 0))
    for lat in ((-1.1, 1.1) if k4 not in BLOCK_FACES else ()):
        # down the batter, on it: a frame tilted with the slope, turned with the face
        rm = (EI + E) / 2
        p = rot @ Vector((lat, -rm))
        se = empty("seam", (p.x, p.y, top_z(rm) + 0.006), (SLOPE_B, 0, -math.pi / 2 * k4))
        box((0, 0, 0), (0.022, (E - EI - 0.06) / math.cos(SLOPE_B), 0.012), "seam", parent=se, bevel=0.004)
# weld seams across the flat corners, shoulder to notch, the joins of the top's sections
for sx in (-1, 1):
    for sy in (-1, 1):
        a = Vector((sx, sy)).normalized() * 1.7
        b = Vector((sx * 1.52, sy * 1.52))
        m = (a + b) / 2
        box((m.x, m.y, ZT + 0.006), ((b - a).length, 0.022, 0.012), "seam", rot=(0, 0, math.atan2(sy, sx)), bevel=0.004)
        nrm = Vector((-sy, sx)).normalized()
        for k in range(5):                                # the joint bolted both sides
            q = a + (b - a) * ((k + 0.5) / 5)
            for side in (-1, 1):
                bolt((q.x + nrm.x * side * 0.05, q.y + nrm.y * side * 0.05, ZT + 0.007), 0.015, 0.012)
# Two replacement panels on the flat, newer castings bolted over the old: north-west and
# south-east, each its own shade (iron_new), bolted all round
for (px, py, pr) in ((-1.42, 1.45, 0.2), (1.82, -1.0, math.pi / 2 - 0.08)):
    pe = empty("patch", (px, py, ZT + 0.008), (0, 0, pr))
    box((0, 0, 0), (0.36, 0.28, 0.016), "iron_new", parent=pe, bevel=0.005)
    for i in range(4):
        for sgn in (-1, 1):
            bolt((-0.15 + 0.1 * i, sgn * 0.115, 0.012), 0.013, 0.01, parent=pe)
        if i in (1, 2):
            continue
    for sgn in (-1, 1):
        bolt((sgn * 0.16, 0, 0.012), 0.013, 0.01, parent=pe)
# (the maker's plate is on the south-west housing's face: 1e)
# stencils: the load mark south-east on the flat (a weight over "50"), and the bay
# numbers beside each band on the batter
# "50", cast raised in the plate, the weight's mark beside it (finish round 3: cast, not paint)
# (on the south-east perimeter casting's top: 1d)
for k4 in (1, 3):                                      # (north and south: the castings carry their marks)
    rot = Matrix.Rotation(-math.pi / 2 * k4, 2)
    p = rot @ Vector((-0.92, -2.2))
    stencil((p.x, p.y, top_z(2.2) + 0.008), (SLOPE_B, 0, -math.pi / 2 * k4),
            ["#./#./#.", "##/.#/##", "##/##/##", "#./##/##"][k4], 0.03)

# ---------------------------------------------------------------- 1b. the discharge bays
#
# The signed-off blockout's (round 3): round each face's centre the chassis steps down to
# a low apron AP tall on the ground, in a band 1.4 wide from the face edge in to a riser
# at Y_STEP; nothing tall stands beside or in front of a chute lying in it. The chassis
# wall meets the footprint edge along the face's middle three tiles: AP tall in the band,
# HC either side of it, where the fluid connections are. Down the apron's middle runs the
# bay, a slot to the ground framed in bolted angle; shut (the plate), a bolted hatch lies
# in it flush with the apron, hinged at the riser; working, the hatch is drawn as dropped
# under the chute, which covers all of it on the screen. Y_STEP puts the east, south and
# west chutes' crops within 2 px of vanilla's.
BAND_HW = 0.70                        # the apron band's half-width
AP = 0.2                              # the apron's height
Y_STEP = 1.63                         # the riser's face
SLOT = 0.45                           # the slot's half-width, to the frame's inner edge
FACE_DEG = {"N": 0, "E": -90, "S": 180, "W": 90}
BAYS = {}
bay_cutters = []
for face, deg in FACE_DEG.items():
    b = empty(f"bay-{face}", rot=(0, 0, math.radians(deg)))
    BAYS[face] = b
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, (Y_STEP - 0.03 + E + 0.3) / 2, 1.0))
    c = bpy.context.active_object
    c.scale = (2 * BAND_HW, E + 0.3 - (Y_STEP - 0.03), 2.6)
    c.parent, c.hide_render, c.display_type = b, True, "WIRE"
    bay_cutters.append(c)
    # the riser: a bolted plate from the ground to the chassis top, across the band, with
    # a cap rail along its head
    box((0, Y_STEP - 0.015, ZT / 2), (2 * BAND_HW, 0.03, ZT), "liner", parent=b, bevel=0.006)
    # the band's cut walls lined with plate (newer iron, lighter): they face into shade
    # (round 6: the east and west bays' north walls face the camera in shade, and were the
    # plate's two black wedges: lined there in paler plate)
    for sx in (-1, 1):
        # (round 6: in front of the chassis's cut face, 0.70 out, not coplanar with it: at
        # 0.706 its face lay on the cut's and z-fought it, and the dark iron mostly won)
        side_plate(sx * (BAND_HW - 0.002), 0.012, [(Y_STEP, AP), (E, AP), (E, HC), (EI, ZT), (Y_STEP, ZT)],
                   "liner_pale" if face in "EW" else "liner", "body", parent=b)
    # its cap rail, behind its face (over the slot it would hide the chute's inner end and
    # move its crop) and in two halves either side of where the shoulder comes closest
    for sx in (-1, 1):
        box((sx * (0.35 + BAND_HW + 0.02) / 2, Y_STEP - 0.02, ZT + 0.012), (BAND_HW + 0.02 - 0.35, 0.04, 0.024),
            "iron", parent=b, bevel=0.006)
    for k in range(7):
        for z in (ZT - 0.08, AP + 0.1):
            bolt((-BAND_HW + 0.1 + (2 * BAND_HW - 0.2) * k / 6, Y_STEP + 0.002, z), 0.018, 0.018,
                 rot=(math.pi / 2, 0, 0), parent=b)
    # the apron either side of the slot, kerbed and bolted along its outer edge
    for sx in (-1, 1):
        x0, x1 = SLOT + 0.02, BAND_HW
        box((sx * (x0 + x1) / 2, (Y_STEP + E) / 2, AP / 2), (x1 - x0, E - Y_STEP, AP), "apron", parent=b,
            bevel=0.008)
        box((sx * (x0 + x1) / 2, E - 0.04, AP + 0.012), (x1 - x0, 0.08, 0.024), "steel", parent=b, bevel=0.005)
        box((sx * (x0 + 0.06), E - 0.02, AP + 0.0245), (0.1, 0.035, 0.002), "polish", parent=b, bevel=0.0)  # worn
        box((sx * (x1 - 0.05), E - 0.03, AP + 0.0245), (0.06, 0.05, 0.002), "polish", parent=b, bevel=0.0)
        for k in range(3):
            bolt((sx * (x0 + 0.04 + (x1 - x0 - 0.08) * k / 2), E - 0.04, AP + 0.03), 0.018, 0.014, parent=b)
        for k in range(5):                               # and a row down its middle, to the frame below
            bolt((sx * (x0 + x1) / 2, Y_STEP + 0.1 + (E - Y_STEP - 0.25) * k / 4, AP + 0.006), 0.016, 0.012,
                 parent=b)
        # the slot's frame: bolted angle down its edge
        box((sx * (SLOT + 0.01), (Y_STEP + E) / 2, AP / 2 + 0.005), (0.04, E - Y_STEP, AP + 0.01), "steel",
            parent=b, bevel=0.004)
        for k in range(6):
            rivet((sx * (SLOT + 0.01), Y_STEP + 0.08 + (E - Y_STEP - 0.16) * k / 5, AP + 0.011), 0.011, parent=b)
    box((0, (Y_STEP + E) / 2, 0.015), (2 * SLOT, E - Y_STEP, 0.03), "liner", parent=b, bevel=0.004)   # its floor
    # the hatch, shut: flush with the apron, hinged at the riser, a lifting eye at its lip
    g = f"door-{face}"
    y0, y1, zt = Y_STEP + 0.03, E - 0.03, AP - 0.006
    box((0, (y0 + y1) / 2, zt - 0.013), (2 * 0.395, y1 - y0, 0.026), "iron_new", g, parent=b, bevel=0.006)
    for xx in (-0.13, 0.13):                             # two stiffening ribs along it
        box((xx, (y0 + y1) / 2, zt + 0.004), (0.03, y1 - y0 - 0.1, 0.012), "iron_new", g, parent=b, bevel=0.003)
    for k in range(6):                                   # bolt rows down both edges
        t = (k + 0.5) / 6
        for sx in (-1, 1):
            bolt((sx * 0.34, y0 + (y1 - y0) * t, zt + 0.004), 0.016, 0.012, group=g, parent=b)
    box((0, y1 - 0.03, zt - 0.006), (2 * 0.395, 0.05, 0.018), "polish", g, parent=b, bevel=0.005)  # its lip, worn
    cyl((0, y1 - 0.08, zt + 0.01), 0.03, 0.012, "steel", g, verts=16, parent=b, bevel=0.0)       # lifting eye's boss
    for sx in (-0.24, 0.24):                             # its hinge knuckles at the riser
        cyl((sx, y0 + 0.02, zt - 0.02), 0.02, 0.12, "polish", g, verts=16, rot=(0, math.pi / 2, 0), parent=b,
            bevel=0.0)
    # (finish round 3, continued: they were the loudest marks at 1x -- one chevron, not two,
    # smaller, in a dulled paint worn back to the iron)
    stencil((-0.028, (y0 + y1) / 2 + 0.03, zt + 0.0015), (0, 0, 0), "..#../.#.#./#...#", 0.014,
            group=g, parent=b, mat="stencil_worn")                           # chevrons, outward: small and worn (finish round 3)
cut(CHASSIS, *bay_cutters)

# ---------------------------------------------------------------- 1c. the chassis top's fittings
#
# Round 2 of the finish: the tops are the largest surfaces the camera sees, so they carry
# a working deck's furniture, as the crusher's roof does, all in the corner quadrants,
# never across a band, so no chute is hidden or its crop moved:
#   - cast stiffening ribs down the batter and a cast lip along its inner edge;
#   - two inspection covers, bolted, with handles; four lifting eyes on the batter;
#   - at the north-east and north-west a motor starter box, its conduit up to the
#     winch's motor; beside it a lubricator, its grease lines up to the winch's bearings;
#   - at the south-west a hydraulic pack (tank, pump, accumulator, gauge, valve block)
#     with hoses to the south and west bays' risers (the hatches' rams) and the lamp's
#     conduit from its control box.


def batter_frame(lat, r, k4, extra=0.0):
    """(location, rotation) on the batter of face k4 (0 south, 1 west, 2 north, 3 east),
    at `lat` across it and `r` out from the centre: local z out of the slope."""
    rot = Matrix.Rotation(-math.pi / 2 * k4, 2)
    p = rot @ Vector((lat, -r))
    return (p.x, p.y, top_z(r) + extra), (SLOPE_B, 0, -math.pi / 2 * k4)


for k4 in (1, 3):                                       # (north and south: under the castings, 1d)
    for lat in (-1.23, -0.93, 0.93, 1.23):                # cast ribs down the batter, between the bolts
        loc, rot = batter_frame(lat, (EI + E) / 2, k4, 0.018)
        rb_ = empty("rib", loc, rot)
        box((0, 0, 0), (0.035, (E - EI - 0.08) / math.cos(SLOPE_B), 0.036), "iron_worn", parent=rb_, bevel=0.008)
    rot = Matrix.Rotation(-math.pi / 2 * k4, 2)
    for sgn in (-1, 1):                                    # the cast lip along the batter's inner edge
        a, b_ = rot @ Vector((sgn * 0.76, -(EI - 0.03))), rot @ Vector((sgn * 1.3, -(EI - 0.03)))
        m = (a + b_) / 2
        box((m.x, m.y, ZT + 0.015), (abs(b_.x - a.x) + 0.035, abs(b_.y - a.y) + 0.035, 0.03), "iron_worn", bevel=0.008)
    for sgn in (-1, 1):                                    # lifting eyes, on the batter
        loc, rot_ = batter_frame(sgn * 1.4, 2.2, k4, 0.0)
        eye(loc, rot_[2], "steel", tilt=SLOPE_B)

# ---------------------------------------------------------------- 1d. the perimeter castings
#
# Finish round 3 (Liam: bulkier): a heavy raised casting either side of the north band,
# from the batter's inner edge to near the wall, 1.12 high (the south ones grew into the
# corner housings, 1e). On the east and
# west faces the gear-houses carry the mass, and nothing tall stands south of a chute
# there (it would hide it from this camera). The north ones' tops stay under the drawn
# height's limit (-190 px against vanilla's -192).
BLOCK_TOP = 1.12
for sy in (1,):                                           # the south ones became the corner housings (1e)
    for sx in (-1, 1):
        cx, cy = sx * 1.135, sy * 2.1
        box((cx, cy, (0.6 + BLOCK_TOP) / 2), (0.63, 0.64, BLOCK_TOP - 0.6), "iron", bevel=0.03)
        box((cx, cy, BLOCK_TOP + 0.015), (0.55, 0.56, 0.03), "iron_worn", bevel=0.01)          # its cap
        for i in range(5):
            for j in (-1, 1):
                bolt((cx - 0.24 + 0.12 * i, cy + j * 0.26, BLOCK_TOP + 0.037), 0.016, 0.012)
        for i in (-1, 1):
            bolt((cx + i * 0.26, cy, BLOCK_TOP + 0.037), 0.016, 0.012)
        for k in range(3):                                # cast ribs down its outer face
            box((cx - 0.2 + 0.2 * k, sy * 2.425, (0.62 + BLOCK_TOP) / 2), (0.05, 0.03, BLOCK_TOP - 0.62),
                "iron_worn", bevel=0.008)
        eye((cx + sx * 0.18, cy - sy * 0.12, BLOCK_TOP + 0.03), 0.0, "steel")

# ---------------------------------------------------------------- 1e. the corner housings
#
# Finish round 3, continued (Liam: "the drill should look bulkier, look at the heavy mining
# drill"): the south corners carry the mass vanilla's drill raises, as two cast housings on
# the chassis -- the hydraulic pack's at the south-west, the drive's switchgear at the
# south-east -- each a tall core beside the south band and a lower wing over the corner
# notch. Their heights are set by what they must not hide, through this camera (a part at
# height z shows z/2 up the screen):
#   - the east and west chutes (x beyond 1.63, y within 0.7, on the ground): a part over
#     their x with its north edge at yn reaches yn + z/2 up the screen, so the wings stop
#     at 1.35 behind a north edge at -1.45 (-0.78, clear of the bay's -0.7);
#   - the south chute: the cores stand outside its band (x beyond 0.8);
#   - the south pipe picture (model (1, -2); on the screen x 0.52-1.47, up to 1.70 below the
#     origin): the south-east core's face stands back at -1.95, so its foot is drawn at
#     -1.52, above the picture's reach; the south-west, with no picture, comes to the wall.
# The cores' tops at 1.65 are drawn at -0.58, under the ring's outer face (about -0.2 at
# x 1.2), so the ring still reads whole and dropping through its frame.
HOUSE_TOP, WING_TOP, HOUSE_N = 2.1, 1.75, -1.4    # (round 5: the corners rise)
M["house"] = cast_iron("house", lo="#3C3B3D", hi="#5C5B5F", drips=((HOUSE_TOP - 0.03, 0.55), (WING_TOP - 0.03, 0.4)),
                       drip=0.8, ore=0.85, dry=0.3, wear=0.85, metal="#B4B6BC")
for _n in M["house"].node_tree.nodes:
    if _n.type == "AMBIENT_OCCLUSION":
        _n.samples = 4
    elif _n.type == "BEVEL":
        _n.samples = 2


def flip(pts, sx):
    return [(sx * x, y) for x, y in pts]


HOUSES = {}
for sx in (-1, 1):
    ys = -2.42 if sx < 0 else -1.95                    # the south-east one stands back of the pipe picture
    core = [(0.8, HOUSE_N), (0.8, ys), (1.47, ys), (1.47, max(ys, -2.08)), (1.55, max(ys, -2.0)), (1.55, HOUSE_N)]
    core = flip(core, sx) if sx > 0 else list(reversed(flip(core, sx)))
    stack([(core, 0.6), (core, HOUSE_TOP)], "house", bevel=0.025, name="house")
    wing = [(1.53, HOUSE_N - 0.05), (1.53, -2.03), (2.0, -1.56), (2.0, HOUSE_N - 0.05)]
    wing = flip(wing, sx) if sx > 0 else list(reversed(flip(wing, sx)))
    stack([(wing, 0.6), (wing, WING_TOP)], "house", bevel=0.02, name="wing")
    cx, cy = sx * 1.175, (ys + HOUSE_N) / 2              # the core's centre in plan
    HOUSES[sx] = (cx, cy, ys)
    # the roof: a cap plate proud of the walls, bolted round
    w_, d_ = 0.79, HOUSE_N - ys + 0.04
    box((cx, cy, HOUSE_TOP + 0.02), (w_, d_, 0.04), "house", bevel=0.012)
    for i in range(6):
        for y_ in (cy - d_ / 2 + 0.05, cy + d_ / 2 - 0.05):
            bolt((cx - 0.33 + 0.132 * i, y_, HOUSE_TOP + 0.044), 0.016, 0.012)
    for f in (0.3, 0.7):
        for x_ in (cx - 0.35, cx + 0.35):
            bolt((x_, cy - d_ / 2 + d_ * f, HOUSE_TOP + 0.044), 0.016, 0.012)
    # the wing's cap and its bolts
    box((sx * 1.765, HOUSE_N - 0.26, WING_TOP + 0.015), (0.44, 0.36, 0.03), "house", bevel=0.01)
    for i in range(3):
        bolt((sx * (1.6 + 0.16 * i), HOUSE_N - 0.12, WING_TOP + 0.034), 0.015, 0.012)
    # cast ribs down the south face, and a foot flange where it meets the chassis
    for k in range(4):
        xr = cx - 0.27 + 0.18 * k
        box((xr, ys - 0.015, (top_z(-ys) + HOUSE_TOP) / 2 - 0.02), (0.045, 0.035, HOUSE_TOP - top_z(-ys) - 0.08),
            "iron_worn", bevel=0.008)
    box((cx, ys - 0.03, top_z(-ys) + 0.03), (0.8, 0.06, 0.08), "house", bevel=0.01)
    for k in range(7):
        bolt((cx - 0.33 + 0.11 * k, ys - 0.062, top_z(-ys) + 0.04), 0.016, 0.014, rot=(math.pi / 2, 0, 0))
    # its east or west face against the band: ribs too
    for k in range(2):
        yr = ys + 0.18 + 0.2 * k
        box((sx * 0.785, yr, (ZT + HOUSE_TOP) / 2), (0.035, 0.045, HOUSE_TOP - ZT - 0.08), "iron_worn", bevel=0.008)
    eye((cx + sx * 0.22, cy + 0.12, HOUSE_TOP + 0.04), 0.0, "steel")

# the south-west housing holds the hydraulic pack: a louvred door on its south face, the
# pressure gauge beside it, the maker's plate, and a breather on its roof
cx, cy, ys = HOUSES[-1]
fz = top_z(-ys) + 0.12                                     # the door's sill
box((cx - 0.06, ys - 0.006, fz + 0.3), (0.42, 0.014, 0.56), "iron_new", bevel=0.006)
for k in range(6):
    box((cx - 0.06, ys - 0.016, fz + 0.12 + 0.06 * k), (0.3, 0.012, 0.014), "steel", bevel=0.0)
for j in (fz + 0.08, fz + 0.52):                           # hinges, east side
    cyl((cx + 0.155, ys - 0.016, j), 0.016, 0.06, "polish", verts=12, bevel=0.0)
box((cx - 0.24, ys - 0.02, fz + 0.3), (0.024, 0.016, 0.08), "polish", bevel=0.002)      # its handle
cyl((cx + 0.24, ys - 0.012, fz + 0.42), 0.05, 0.012, "steel", verts=20, rot=(math.pi / 2, 0, 0), bevel=0.0)
cyl((cx + 0.24, ys - 0.019, fz + 0.42), 0.038, 0.003, "polish", verts=20, rot=(math.pi / 2, 0, 0), bevel=0.0)
mp = empty("makers", (cx + 0.24, ys - 0.012, fz + 0.2), (math.pi / 2, 0, 0))
box((0, 0, 0), (0.16, 0.1, 0.01), "brass", parent=mp, bevel=0.003)
box((0, 0.015, 0.006), (0.11, 0.018, 0.003), "dark", parent=mp, bevel=0.0)
box((0, -0.02, 0.006), (0.08, 0.014, 0.003), "dark", parent=mp, bevel=0.0)
for i in (-1, 1):
    for j in (-1, 1):
        rivet((i * 0.065, j * 0.035, 0.006), 0.008, parent=mp)
# (round 5) a machinery cabinet stepped up on the roof's south-west part, the pump's motor
# under it, louvred on its south face; the breather on its top
RC = (-1.33, -2.18, 0.28, 0.44, 0.45)                      # centre x, y; width, depth, height
box((RC[0], RC[1], HOUSE_TOP + RC[4] / 2), (RC[2], RC[3], RC[4]), "house", bevel=0.02)
box((RC[0], RC[1], HOUSE_TOP + RC[4] + 0.015), (RC[2] + 0.04, RC[3] + 0.04, 0.03), "house", bevel=0.008)
for k in range(5):
    box((RC[0], RC[1] - RC[3] / 2 - 0.006, HOUSE_TOP + 0.08 + 0.065 * k), (RC[2] - 0.08, 0.014, 0.016), "steel",
        bevel=0.0)
for i in (-1, 1):
    for j in (-1, 1):
        bolt((RC[0] + i * (RC[2] / 2 - 0.0), RC[1] + j * (RC[3] / 2 - 0.0), HOUSE_TOP + RC[4] + 0.035), 0.013, 0.01)
    weld((RC[0] + i * RC[2] / 2, RC[1] - RC[3] / 2, HOUSE_TOP + 0.004), (RC[0] + i * RC[2] / 2, RC[1] + RC[3] / 2,
                                                                         HOUSE_TOP + 0.004))
cyl((RC[0] + 0.03, RC[1] + 0.08, HOUSE_TOP + RC[4] + 0.08), 0.05, 0.1, "steel", verts=16, bevel=0.006)   # breather
cyl((RC[0] + 0.03, RC[1] + 0.08, HOUSE_TOP + RC[4] + 0.14), 0.065, 0.02, "steel", verts=16, bevel=0.004)
LAMP = (cx + 0.12, cy - 0.05, HOUSE_TOP + 0.04)            # the status lamp: on its roof (section 5)
# hoses from its east and north faces to the south and west bays' risers (the hatches' rams)
pipe([(-0.8, cy + 0.1, ZT + 0.25), (-0.74, cy + 0.1, ZT + 0.25), (-0.74, -1.62, ZT + 0.03), (-0.66, -1.66, ZT + 0.03)],
     0.011, "grease", bend=0.05)
pipe([(-1.3, HOUSE_N, ZT + 0.25), (-1.3, HOUSE_N + 0.05, ZT + 0.25), (-1.3, -0.74, ZT + 0.03), (-1.66, -0.7, ZT + 0.03)],
     0.011, "grease", bend=0.05)
# (round 5) the south-east housing's front step: a lower block in front of its face, to the
# wall, over the south pipe stub (the amendment accepts a stub partly behind a housing)
_cx5, _cy5, _ys5 = HOUSES[1]
STEP_TOP = 1.3
stack([([(0.8, -2.42), (1.47, -2.42), (1.47, _ys5 + 0.02), (0.8, _ys5 + 0.02)], 0.6),
       ([(0.8, -2.42), (1.47, -2.42), (1.47, _ys5 + 0.02), (0.8, _ys5 + 0.02)], STEP_TOP)], "house", bevel=0.02,
      name="step")
box((1.135, (-2.42 + _ys5) / 2, STEP_TOP + 0.015), (0.71, abs(-2.42 - _ys5) + 0.04, 0.03), "house", bevel=0.008)
for k in range(6):
    bolt((0.83 + 0.12 * k, -2.4, STEP_TOP + 0.034), 0.015, 0.012)
    bolt((0.83 + 0.12 * k, _ys5 - 0.03, STEP_TOP + 0.034), 0.015, 0.012)
for k in range(3):                                      # its cast ribs down the south face
    box((0.95 + 0.25 * k, -2.435, (top_z(2.42) + STEP_TOP) / 2), (0.04, 0.03, STEP_TOP - top_z(2.42) - 0.05),
        "iron_worn", bevel=0.006)
box((1.135, -2.43, STEP_TOP - 0.2), (0.3, 0.012, 0.2), "iron_new", bevel=0.004)          # an access plate
for i in (-1, 1):
    for j in (-1, 1):
        bolt((1.135 + i * 0.13, -2.437, STEP_TOP - 0.2 + j * 0.08), 0.012, 0.01, rot=(math.pi / 2, 0, 0))
# the south-east housing, the switchgear's: an access cover on its roof, "50" cast raised
# beside it with the weight's mark, and a cable gland on its north face
cx, cy, ys = HOUSES[1]
ic = empty("cover", (cx - 0.1, cy, HOUSE_TOP + 0.045), (0, 0, 0))
box((0, 0, 0), (0.3, 0.26, 0.014), "iron_new", parent=ic, bevel=0.005)
for i in range(4):
    for j in (-1, 1):
        bolt((-0.12 + 0.08 * i, j * 0.11, 0.01), 0.012, 0.009, parent=ic)
eye((0, 0, 0.004), 0.0, "polish", parent=ic, r=0.022)
stencil((cx + 0.12, cy + 0.07, HOUSE_TOP + 0.042), (0, 0, 0), "###.###/#...#.#/###.#.#/..#.#.#/###.###", 0.026,
        mat="iron_worn", h=0.014)                         # "50", cast raised
stencil((cx + 0.17, cy - 0.1, HOUSE_TOP + 0.042), (0, 0, 0), ".#./###/###", 0.026, mat="iron_worn", h=0.014)
cyl((cx, HOUSE_N + 0.03, ZT + 0.35), 0.04, 0.06, "brass", verts=16, rot=(math.pi / 2, 0, 0), bevel=0.004)

# inspection cover: west-south-west, bolted, with handles, one rim worn
for (cx, cy, ca) in ((-1.84, -1.0, math.pi / 2),):
    ic = empty("cover", (cx, cy, ZT + 0.006), (0, 0, ca))
    box((0, 0, 0), (0.3, 0.22, 0.014), "iron_new", parent=ic, bevel=0.005)
    box((0, 0, -0.002), (0.34, 0.26, 0.01), "iron", parent=ic, bevel=0.004)
    for i in range(4):
        for j in (-1, 1):
            bolt((-0.135 + 0.09 * i, j * 0.11, 0.01), 0.013, 0.01, parent=ic)
    for j in (-1, 1):
        bolt((j * 0.155, 0, 0.01), 0.013, 0.01, parent=ic)
        eye((j * 0.07, 0, 0.004), 0.0, "polish", parent=ic, r=0.022)
    box((0, -0.105, 0.009), (0.24, 0.012, 0.002), "polish", parent=ic, bevel=0.0)

# (the winches' feeds are in 3b, once the winches stand)

# ---------------------------------------------------------------- 2. the column (fixed)

# Tall and capped, as the adopted plate draws it, and made to read as a column (round 2:
# it read as stacked discs): a plain shaft, polished bright in a band where the hub rides;
# above the hub's travel a copper band, then the shaft cut with four keyways between
# cast ribs up to a bolted collar; a domed cap on it with a lifting eye, and grease cups
# on the collar feeding the cap's bearing. Its top is about 3.3 up, 106 px above the
# origin on the screen.
COL_R = 0.34
COL_TOP = 3.2                         # the shaft: up through the crown's boss (finish round 3)
cyl((0, 0, (WELL_Z + COL_TOP) / 2), COL_R, COL_TOP - WELL_Z, "column", verts=64, bevel=0.01)
# (round 6: the ring's taller band carries the hub higher: it rides 1.40 to 2.14)
ring((0, 0, 1.77), COL_R + 0.004, COL_R - 0.02, 0.74, "polish", verts=64, bevel=0.0)  # the hub's wear band
ring((0, 0, 2.2), COL_R + 0.03, COL_R - 0.01, 0.07, "copper", verts=64)          # a copper band above the hub's travel
for k in range(8):                                                                 # keyways and ribs, alternating
    t = 2 * math.pi * k / 8 + math.pi / 8
    if k % 2:
        box(((COL_R - 0.005) * math.cos(t), (COL_R - 0.005) * math.sin(t), 2.6), (0.03, 0.05, 0.56), "dark",
            rot=(0, 0, t), bevel=0.0)
    else:
        box(((COL_R + 0.012) * math.cos(t), (COL_R + 0.012) * math.sin(t), 2.6), (0.04, 0.035, 0.56), "iron_worn",
            rot=(0, 0, t), bevel=0.006)
cyl((0, 0, COL_TOP + 0.05), 0.44, 0.1, "column", verts=64, bevel=0.015)           # the bolted collar
for k in range(16):
    t = 2 * math.pi * (k + 0.5) / 16
    bolt((0.4 * math.cos(t), 0.4 * math.sin(t), COL_TOP + 0.107), 0.02, 0.016)
arc(0.445, 0.41, COL_TOP + 0.1, 0.012, 200, 340, "polish")                        # its rim worn at the front
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.34, location=(0, 0, COL_TOP + 0.1), segments=48, ring_count=24)
_dome = bpy.context.active_object
_dome.scale.z = 0.42
bpy.ops.object.transform_apply(scale=True)
_finish(_dome, "column", "body", bevel=0, smooth=True)
cut(_dome, cutter_cyl((0, 0, COL_TOP - 0.1), 0.5, 0.4))                           # the dome's lower half off
cyl((0, 0, COL_TOP + 0.24), 0.1, 0.04, "steel", verts=24, bevel=0.006)            # the eye's boss
eye((0, 0, COL_TOP + 0.255), 0.0, "polish", r=0.045)                              # the lifting eye, east-west
for t in (math.radians(202.5), math.radians(337.5)):                              # grease cups on the collar,
    cx, cy = 0.392 * math.cos(t), 0.392 * math.sin(t)                              # between its bolts, off the dome
    cyl((cx, cy, COL_TOP + 0.13), 0.03, 0.05, "brass", verts=16, bevel=0.005)
    cyl((cx, cy, COL_TOP + 0.17), 0.022, 0.03, "brass", verts=16, bevel=0.004)

# ---------------------------------------------------------------- 3. the guide columns and winches

# (round 6, Liam: a heavier ring: narrower in plan, its band deeper, so it reads as a thick
# casting and not a flat dark disc filling the middle three tiles)
RB_OUT, RB_IN, RH = 1.30, 0.98, 0.75  # the ring's band: outer, inner radius, depth
Z_RING = ZS + TRAVEL                  # its underside at frame 0, raised
GR_OUT = 1.95                         # the two north columns (30, 150 degrees), outside the ring
GR_N = (RB_OUT + RB_IN) / 2           # the south one (270), through the band
GUIDE_R = 0.17                        # finish round 3: heavier (Liam: bulkier, as the big mining drill)
GUIDE_TOP = 2.25                      # the north columns' heads: the gear-houses' platforms
GUIDE_S_TOP = 2.36                    # the south one's capped head
HB, HR = GUIDE_TOP + 0.06, 2.94       # the gear-houses' walls: from over the platform to under the roof
COLS = {30: GR_OUT, 150: GR_OUT, 270: GR_N}


def at(a, r):
    t = math.radians(a)
    return r * math.cos(t), r * math.sin(t)


for a, r in COLS.items():
    x, y = at(a, r)
    z0 = ZS if a == 270 else ZT
    top = GUIDE_TOP          # (round 3, continued) the south one no longer climbs to the crown: drawn
                             # in front of the central column, it hid it
    if a == 270:
        top = GUIDE_S_TOP    # (round 6) clear of the deeper band's raised top (2.14)
    cyl((x, y, (z0 + top) / 2), GUIDE_R, top - z0, "guide", verts=32, bevel=0.008)
    if a != 270:
        box((x, y, ZT + 0.07), (0.46, 0.46, 0.14), "iron", bevel=0.02)             # its foot on the chassis
        for i in (-1, 1):
            for j in (-1, 1):
                bolt((x + i * 0.18, y + j * 0.18, ZT + 0.147), 0.022, 0.016)
        ring((x, y, ZT + 0.16), GUIDE_R + 0.06, GUIDE_R - 0.01, 0.05, "iron", verts=32)
        # polished bright where the shoe rides it, seated to raised (round 2)
        ring((x, y, 1.57), GUIDE_R + 0.003, GUIDE_R - 0.02, 0.72, "polish", verts=32, bevel=0.0)
    else:
        ring((x, y, ZS + 0.04), GUIDE_R + 0.07, GUIDE_R - 0.01, 0.08, "iron", verts=32)    # its foot on the shoulder
        ring((x, y, 1.57), GUIDE_R + 0.003, GUIDE_R - 0.02, 1.12, "polish", verts=32, bevel=0.0)  # the band's bore rides it
        cyl((x, y, top + 0.04), GUIDE_R + 0.06, 0.1, "iron", verts=32, bevel=0.012)  # its capped head
        for k in range(6):
            u = 2 * math.pi * (k + 0.5) / 6
            bolt((x + (GUIDE_R + 0.025) * math.cos(u), y + (GUIDE_R + 0.025) * math.sin(u), top + 0.096), 0.014, 0.01)

# The winches, on the north columns' heads (north-east and north-west, behind the east and
# west chutes from this camera, so they hide none): a platform; a north-south shaft in
# two pedestals; on it a spur gear upright in the east-west plane, facing the camera, its
# lower half in a guard; a copper drum north of it; a motor and pinion meshing the gear
# at its outer side. From the drum's outer side a wire rope hangs to an eye on the shoe.
GEAR_R = 0.3
WINCH_Z = GUIDE_TOP + 0.38            # the shaft: the gear's teeth clear the platform by 0.02
DRUM_R = 0.18
WINCHES = []
GEARS = []                            # (empty, turns per radian of drum) -- the proposal turns them (--weight)
for a in (30, 150):
    x, y = at(a, GR_OUT)
    out = 1 if x > 0 else -1
    WINCHES.append((x, y, out))
    box((x, y + 0.05, GUIDE_TOP + 0.03), (0.32, 0.66, 0.06), "iron", bevel=0.01)           # platform
    for i in (-1, 1):
        for j in (-1, 1):
            bolt((x + i * 0.12, y + 0.05 + j * 0.28, GUIDE_TOP + 0.066), 0.014, 0.012)
    for dy in (-0.25, 0.32):                                                               # pedestals
        box((x, y + dy, (GUIDE_TOP + WINCH_Z) / 2 + 0.02), (0.1, 0.07, WINCH_Z - GUIDE_TOP + 0.04), "iron",
            bevel=0.008)
        cyl((x, y + dy, WINCH_Z), 0.05, 0.08, "brass", verts=24, rot=(math.pi / 2, 0, 0), bevel=0.006)  # bearing cap
    cyl((x, y + 0.04, WINCH_Z), 0.035, 0.66, "steel", verts=16, rot=(math.pi / 2, 0, 0), bevel=0.0)  # shaft
    GEARS.append((gear((x, y - 0.12, WINCH_Z), GEAR_R, 32, 0.06, "gear", "body", spokes=5), out))
    # the guard: the gear's lower half runs in it, clear of its faces and teeth
    for dy in (-0.075, 0.075):
        box((x, y - 0.12 + dy, (GUIDE_TOP + 0.06 + WINCH_Z - 0.02) / 2), (2 * GEAR_R + 0.08, 0.02,
            WINCH_Z - 0.08 - GUIDE_TOP), "iron", bevel=0.004)
    cyl((x, y + 0.13, WINCH_Z), DRUM_R, 0.2, "copper", verts=48, rot=(math.pi / 2, 0, 0), bevel=0.01)   # drum
    for k in range(6):                                                                     # rope turns on it
        cyl((x, y + 0.05 + 0.032 * k, WINCH_Z), DRUM_R + 0.012, 0.022, "cable", verts=48,
            rot=(math.pi / 2, 0, 0), bevel=0.0)
    for dy in (0.02, 0.24):
        cyl((x, y + dy, WINCH_Z), 0.22, 0.025, "copper", verts=48, rot=(math.pi / 2, 0, 0), bevel=0.004)  # its cheeks
    # the motor, outboard and low, its pinion meshing the gear from outside
    mx = x + out * math.sqrt((GEAR_R + 0.07) ** 2 - 0.17 ** 2)     # meshed: centres a pitch-radius sum apart
    GEARS.append((gear((mx, y - 0.12, WINCH_Z - 0.17), 0.07, 9, 0.05, "gear", "body"), -out * GEAR_R / 0.07))
    cyl((mx, y + 0.02, WINCH_Z - 0.17), 0.085, 0.24, "copper", verts=32, rot=(math.pi / 2, 0, 0), bevel=0.01)
    for k in range(5):                                                                     # its cooling fins
        cyl((mx, y - 0.06 + 0.04 * k, WINCH_Z - 0.17), 0.1, 0.01, "steel", verts=32, rot=(math.pi / 2, 0, 0),
            bevel=0.0)
    box((mx, y + 0.02, GUIDE_TOP + 0.08), (0.14, 0.2, 0.06), "iron", bevel=0.006)         # its bracket
    # a grease stain on the platform under the gear
    cyl((x, y - 0.1, GUIDE_TOP + 0.061), 0.09, 0.002, "grease", verts=24, bevel=0.0)

# ---------------------------------------------------------------- 3a. the press frame: gear-houses and crown
#
# Finish round 3 (Liam: "bulkier, look at the heavy mining drill"): the mass goes up into
# the air as a press frame. Each winch is enclosed in a gear-house on its column's head --
# back and outer walls, a roof, the front open on the gear -- standing above the ring's
# travel (its walls start at 2.31; the raised ring's top is at 1.94), carried by the
# column and a rear leg to the deck. On the two roofs sits a cast crown, a girder from
# each to a boss round the central column, which passes up through it: the frame closed
# over the ring, as a press's crown closes its columns. (A third arm, to the south guide
# column, came out: that column, run up to meet it, hid the central column.)
# Round 4 (Liam: "these look too well machined"): the two houses are not twins. The
# north-west is the original casting; the north-east a later replacement -- another
# foundry's iron, a touch lighter and bluer, four stiffeners not three, and a bolted
# inspection hatch on its roof; it carries a welded-on patch over a crack on its back
# wall. Both walls streaked with grime and rust below the roof's edge. (The crown that
# bridged them over the column came out: Liam, round 3: it read as a big X across the
# machine. The guide columns stand free, the north ones under their houses, the south one
# capped.)
# Round 7 (Liam: "a stronger accent colour, within the cast-iron finish, as vanilla's big
# drill carries its red"): the press frame -- the gear-houses, their drive cabinets, the
# hydraulic tank and bottles -- painted in red oxide over the iron, chipped back to it on
# every edge and worn through where hands and chains go, rust under the paint. The
# north-west the original coat, darker and more worn; the north-east (the replacement
# casting) a newer, brighter coat.
M["house_nw"] = layered("house_nw", "#6A2618", metal="#8E9096", paint_metal=0.12, paint_rough=0.62, wear=0.85,
                        rust=0.45, dust=0.3, grime=0.75, jitter=0.12, rust_tint=("#2E180C", "#6E3C1C"),
                        drips=((HR, 0.6), (HR - 0.3, 0.4)), drip=0.9)
M["house_ne"] = layered("house_ne", "#842E1E", metal="#9A9CA2", paint_metal=0.12, paint_rough=0.58, wear=0.6,
                        rust=0.3, dust=0.3, grime=0.6, jitter=0.1, rust_tint=("#2E180C", "#6E3C1C"),
                        drips=((HR, 0.55),), drip=0.7)
M["oxide"] = layered("oxide", "#7C2C1E", metal="#9A9CA2", paint_metal=0.12, paint_rough=0.6, wear=0.75, rust=0.4,
                     dust=0.35, grime=0.65, jitter=0.12, rust_tint=("#2E180C", "#6E3C1C"))
for _m in (M["house_nw"], M["house_ne"], M["oxide"]):
    for _n in _m.node_tree.nodes:
        if _n.type == "AMBIENT_OCCLUSION":
            _n.samples = 4
        elif _n.type == "BEVEL":
            _n.samples = 2
CABS = {}
for (x, y, out) in WINCHES:
    hm = "house_ne" if out > 0 else "house_nw"
    gx = x + out * 0.05                                   # the house's centre across, outboard of the column
    box((gx, y + 0.47, (HB + HR) / 2), (0.98, 0.05, HR - HB), hm, bevel=0.01)          # back wall
    box((x + out * 0.515, y + 0.03, (HB + HR) / 2), (0.05, 0.93, HR - HB), hm, bevel=0.01)  # outer wall
    box((gx, y - 0.42, HR - 0.05), (0.98, 0.07, 0.1), "iron_worn", bevel=0.01)           # front lintel
    box((x + out * 0.5, y - 0.42, (HB + HR) / 2), (0.08, 0.08, HR - HB), "iron_worn", bevel=0.01)  # front post
    # (round 7) its roof a cast cover with a rolled edge: the top corners of the drill round,
    # not square
    box((gx, y + 0.03, HR + 0.03), (1.04, 0.98, 0.06), hm, bevel=0.03)                 # roof
    for yy_ in (y + 0.5, y - 0.44):
        cyl((gx, yy_, HR + 0.0), 0.05, 1.02, hm, verts=24, rot=(0, math.pi / 2, 0), bevel=0.0)   # its rolled edge
    # rivet rows round the roof's edges and down the outer wall's seams: the red reads as
    # riveted plate, not a flat colour (round 7)
    for i in range(14):
        for yy_ in (y - 0.4, y + 0.46):
            rivet((gx - 0.48 + 0.074 * i, yy_, HR + 0.062), 0.012)
    for i in range(12):
        for xx_ in (gx - 0.48, gx + 0.48):
            rivet((xx_, y - 0.36 + 0.07 * i, HR + 0.062), 0.012)
    for zz_ in [HB + 0.08 + 0.09 * k for k in range(7)]:
        for yy_ in (y - 0.38, y + 0.42):
            rivet((x + out * 0.542, yy_, zz_), 0.012)
    # (round 6) lined inside in pale plate, bolted: through the open front the house's inside
    # stood in its own shade, and was most of the plate's black behind the ring
    box((gx - out * 0.02, y + 0.44, (HB + HR) / 2), (0.9, 0.012, HR - HB - 0.06), "liner_pale", bevel=0.004)
    box((x + out * 0.488, y + 0.01, (HB + HR) / 2), (0.012, 0.82, HR - HB - 0.06), "liner_pale", bevel=0.004)
    for k in range(5):
        bolt((gx - out * 0.02 - 0.36 + 0.18 * k, y + 0.432, HR - 0.08), 0.012, 0.01, rot=(math.pi / 2, 0, 0))
    for i in range(6):
        for j in (-1, 1):
            bolt((gx - 0.45 + 0.18 * i, y + 0.03 + j * 0.45, HR + 0.067), 0.016, 0.012)
    n_st = 4 if out > 0 else 3
    for k in range(n_st):                                 # the back wall's stiffeners
        box((gx - 0.3 + 0.6 * k / (n_st - 1), y + 0.5, (HB + HR) / 2), (0.04, 0.03, HR - HB), "iron_worn", bevel=0.006)
    if out > 0:
        # the replacement's roof hatch, bolted, a little skew, its lifting eye
        hz = empty("roofhatch", (gx - 0.1, y + 0.1, HR + 0.068), (0, 0, math.radians(2.5)))
        box((0, 0, 0), (0.42, 0.32, 0.016), "iron_new", parent=hz, bevel=0.005)
        for i in range(5):
            for j in (-1, 1):
                bolt((-0.18 + 0.09 * i, j * 0.14, 0.012), 0.013, 0.01, parent=hz)
        eye((0.1, 0, 0.008), 0.0, "polish", parent=hz, r=0.024)
        # a welded patch over a crack in its back wall, off-square, its bead round it
        pz = empty("patch", (gx + 0.16, y + 0.497, HB + 0.22), (math.pi / 2, math.radians(4), 0))
        box((0, 0, 0), (0.22, 0.16, 0.012), "iron_new", parent=pz, bevel=0.003)
        for (px_, py_, sx_, sy_) in ((0, 0.085, 0.24, 0.01), (0, -0.085, 0.24, 0.01), (0.115, 0, 0.01, 0.18),
                                     (-0.115, 0, 0.01, 0.18)):
            box((px_, py_, 0.004), (sx_, sy_, 0.01), "seam", parent=pz, bevel=0.003)
    # (round 5, the corners rise: Liam's amendment) the house closed down to the deck on its
    # outer side by a drive cabinet, which carries the roof's back corner in place of the
    # rear leg: from the deck to the house's floor, outboard of the shoe's travel (the
    # shoe reaches 1.97 out; the cabinet starts at 1.98) and north of the bay (0.78)
    c0, c1, cy0, cy1 = out * 1.98, out * 2.27, 0.78, y + 0.495
    ccx, ccy = (c0 + c1) / 2, (cy0 + cy1) / 2
    zb_ = top_z(2.27) - 0.04
    box((ccx, ccy, (zb_ + HB) / 2), (abs(c1 - c0), cy1 - cy0, HB - zb_), hm, bevel=0.02)
    # its south face: a louvred door, its hinges and handle, a cast rib each side
    fz_ = ZT + 0.1
    box((ccx, cy0 - 0.006, fz_ + 0.45), (0.2, 0.014, 0.8), "liner", bevel=0.006)
    for k in range(8):
        box((ccx, cy0 - 0.016, fz_ + 0.2 + 0.07 * k), (0.15, 0.012, 0.014), "steel", bevel=0.0)
    for zz in (fz_ + 0.12, fz_ + 0.78):
        cyl((ccx - out * 0.105, cy0 - 0.016, zz), 0.014, 0.06, "polish", verts=10, bevel=0.0)
    box((ccx + out * 0.08, cy0 - 0.02, fz_ + 0.5), (0.02, 0.014, 0.08), "polish", bevel=0.002)
    for xr in (c0 + out * 0.012, c1 - out * 0.012):
        box((xr, cy0 - 0.012, (zb_ + HB) / 2), (0.03, 0.03, HB - zb_ - 0.06), "iron_worn", bevel=0.006)
    box((ccx, ccy, zb_ + 0.04), (abs(c1 - c0) + 0.06, cy1 - cy0 + 0.06, 0.08), "iron", bevel=0.012)   # its foot
    for k in range(3):
        bolt((ccx + out * (-0.1 + 0.1 * k), cy0 - 0.025, zb_ + 0.085), 0.016, 0.012)
    # and stepped inward north of the shoe's sweep (which reaches y 1.255), under the winch's
    # platform (2.22): an L, closing the dark gap behind the column
    e0, e1, ey0, ey1, ez = out * 1.5, out * 2.0, 1.27, cy1, 2.18
    box(((e0 + e1) / 2, (ey0 + ey1) / 2, (zb_ + ez) / 2), (abs(e1 - e0), ey1 - ey0, ez - zb_), hm, bevel=0.02)
    box(((e0 + e1) / 2, (ey0 + ey1) / 2, ez + 0.015), (abs(e1 - e0) + 0.04, ey1 - ey0 + 0.04, 0.03), "iron", bevel=0.008)
    for k in range(4):
        bolt((e0 + out * (0.06 + 0.12 * k), ey0 - 0.005, ez + 0.034), 0.014, 0.011)
    box(((e0 + e1) / 2, ey0 - 0.006, ZT + 0.55), (0.26, 0.014, 0.5), "liner", bevel=0.005)     # its hatch
    for i in (-1, 1):
        for j in (-1, 1):
            bolt(((e0 + e1) / 2 + i * 0.11, ey0 - 0.014, ZT + 0.55 + j * 0.22), 0.011, 0.009, rot=(math.pi / 2, 0, 0))
    CABS[out] = (c0, c1, cy0, cy1)

# ---------------------------------------------------------------- 3b. the winches' feeds, the hydraulic pack

for (x, y, out) in WINCHES:
    # the starter box, on the flat between the band and the shoulder
    # (finish round 3: a tall cabinet, not a box)
    bx_, by_ = out * 1.02, 1.62
    CH_ = 0.85                                            # (round 5: taller)
    box((bx_, by_, ZT + CH_ / 2), (0.3, 0.24, CH_), "iron_new", bevel=0.012)
    box((bx_, by_ - 0.121, ZT + CH_ / 2 + 0.02), (0.24, 0.004, CH_ - 0.12), "iron", bevel=0.0)    # its door
    for k in range(4):                                                                      # louvres
        box((bx_, by_ - 0.125, ZT + 0.12 + 0.06 * k), (0.18, 0.012, 0.012), "steel", bevel=0.0)
    box((bx_ + out * 0.09, by_ - 0.127, ZT + CH_ / 2 + 0.08), (0.02, 0.01, 0.06), "polish", bevel=0.002)  # handle
    box((bx_, by_, ZT + CH_ + 0.012), (0.34, 0.28, 0.024), "iron", bevel=0.005)            # its roof
    for i in (-1, 1):
        for j in (-1, 1):
            bolt((bx_ + i * 0.14, by_ + j * 0.11, ZT + CH_ + 0.03), 0.011, 0.008)
    cyl((bx_ + out * 0.155, by_, ZT + 0.07), 0.024, 0.03, "brass", verts=12, rot=(0, math.pi / 2, 0), bevel=0.0)
    # its conduit: out along the deck, up a riser beside the platform, into the motor's end
    mx = x + out * math.sqrt((GEAR_R + 0.07) ** 2 - 0.17 ** 2)
    mz = WINCH_Z - 0.17
    # (round 5: into the drive cabinet's inner face, which takes it on to the motor)
    run = [(bx_ + out * 0.16, by_, ZT + 0.07), (out * 1.42, by_, ZT + 0.07), (out * 1.47, 1.5, ZT + 0.07),
           (out * 1.49, 1.42, ZT + 0.07)]
    pipe(run, 0.016, "steel", bend=0.06)
    for f in (0.3, 0.7):                                  # saddle clips on the deck
        p0, p1 = Vector(run[0]), Vector(run[1])
        q = p0 + (p1 - p0) * f
        box((q.x, q.y, ZT + 0.02), (0.03, 0.05, 0.04), "steel", bevel=0.004)
    # the lubricator, and its grease lines up to the winch's two bearings
    lx, ly = out * 1.35, 1.1
    box((lx, ly, ZT + 0.06), (0.1, 0.1, 0.12), "iron_new", bevel=0.01)
    cyl((lx, ly, ZT + 0.15), 0.035, 0.06, "brass", verts=16, bevel=0.005)
    cyl((lx, ly, ZT + 0.19), 0.02, 0.02, "brass", verts=12, bevel=0.003)
    zg = WINCH_Z + 0.03
    for by2 in (y - 0.25, y + 0.32):
        pipe([(lx, ly, ZT + 0.12), (lx, ly, zg), (lx, by2, zg), (x - out * 0.045, by2, zg)], 0.008, "copper",
             bend=0.04)
    box((lx, ly, (ZT + zg) / 2), (0.03, 0.03, 0.03), "steel", bevel=0.003)                  # a clip on the riser
    cyl((lx, ly - 0.06, ZT + 0.0015), 0.07, 0.003, "grease", verts=20, bevel=0.0)           # its drips

# (the hydraulic pack is in the south-west corner housing, and the lamp on its roof: 1e)

# ---------------------------------------------------------------- 4. the ring (moves)

RING = empty("ring-carrier", (0, 0, Z_RING))     # its z is the stroke: raised at Z_RING, seated at ZS
# Round 6 (Liam, after round 5: "make the ring look heavy"): a deep cast band, its outer wall
# turned to the camera as a cast band in three values (FFF #146): a cast lip round its top,
# lighter iron, its edge catching the light, overhanging the wall so a dark contact line
# lies under it; the wall darker, ribbed with cast webs worn bright on their edges; a foot
# flange at its base; the top face and spokes lighter again, dusted with ore; the band's
# inner wall in a dustier iron, so the well inside reads apart from the ring round it.
band = lathe([(RB_OUT - 0.03, 0.0), (RB_OUT, 0.04), (RB_OUT, RH - 0.07), (RB_IN, RH - 0.07), (RB_IN, 0.03),
              (RB_IN + 0.03, 0.0)], "ring", "ring", parent=RING, verts=192, bevel=0.0)
lathe([(RB_OUT + 0.035, RH - 0.085), (RB_OUT + 0.04, RH - 0.03), (RB_OUT + 0.01, RH), (RB_IN + 0.02, RH),
       (RB_IN - 0.012, RH - 0.03), (RB_IN - 0.012, RH - 0.085)], "ring_top", "ring", parent=RING, verts=192)  # the lip
ring((0, 0, 0.045), RB_OUT + 0.055, RB_OUT - 0.01, 0.09, "ring_worn", "ring", parent=RING, verts=192, bevel=0.012)  # foot
ring((0, 0, RH / 2 - 0.04), RB_IN + 0.001, RB_IN - 0.014, RH - 0.2, "ring_in", "ring", parent=RING, verts=128,
     bevel=0.0)                                                               # the inner wall's dusty face
nx, ny = at(270, GR_N)
cut(band, cutter_cyl((nx, ny, RH / 2), GUIDE_R + 0.03, RH + 0.4, parent=RING, verts=48))
boss = ring((nx, ny, RH / 2), 0.3, GUIDE_R + 0.03, RH, "ring", "ring", parent=RING, verts=48, bevel=0.012)
ring((nx, ny, RH + 0.005), 0.3, GUIDE_R + 0.03, 0.03, "ring_top", "ring", parent=RING, verts=48, bevel=0.006)
ring((nx, ny, RH + 0.025), GUIDE_R + 0.06, GUIDE_R + 0.015, 0.03, "brass", "ring", parent=RING, verts=32)  # its bushing
# the webs down the outer wall, between the foot and the lip: not where an arm, a lug or the
# south boss stands
LUGS = (45, 135, 225, 315)                     # the snubbers' lugs (below)
for k in range(30):
    a_ = 6 + 12 * k
    if any(abs((a_ - c + 180) % 360 - 180) < 9 for c in (30, 150, 270) + LUGS):
        continue
    t = math.radians(a_)
    box(((RB_OUT + 0.022) * math.cos(t), (RB_OUT + 0.022) * math.sin(t), (0.09 + RH - 0.085) / 2),
        (0.05, 0.055, RH - 0.085 - 0.09), "ring_worn", "ring", rot=(0, 0, t), parent=RING, bevel=0.01)
# cast webs across its top face, between the spokes; bolted fishplates over the segment
# joins, on the spokes' lines
for k in range(12):
    t = math.radians(15 + 30 * k)
    if k % 2 == 0:                     # 15 + 60j: the webs
        r = (RB_OUT + RB_IN) / 2
        box((r * math.cos(t), r * math.sin(t), RH + 0.012), (RB_OUT - RB_IN - 0.12, 0.04, 0.03), "ring_worn", "ring",
            rot=(0, 0, t), parent=RING, bevel=0.008)
for k in range(6):
    t = math.radians(30 + 60 * k)
    if 30 + 60 * k == 270:
        continue
    r = (RB_OUT + RB_IN) / 2
    pe = empty("fish", (r * math.cos(t), r * math.sin(t), RH + 0.008), (0, 0, t), parent=RING)
    box((0, 0, 0), (0.24, 0.2, 0.02), "ring_worn", "ring", parent=pe, bevel=0.005)
    for i in (-1, 1):
        for j in (-1, 1):
            bolt((i * 0.08, j * 0.07, 0.014), 0.017, 0.016, group="ring", parent=pe)
# the hub on the column: a bolted flange and a bronze bearing band
HUB_OUT, HUB_IN, HUB_H = 0.56, COL_R + 0.035, 0.42
ring((0, 0, RH - HUB_H / 2), HUB_OUT, HUB_IN, HUB_H, "ring", "ring", parent=RING, verts=96, bevel=0.015)
ring((0, 0, RH - 0.015), HUB_OUT + 0.02, HUB_IN, 0.05, "ring_top", "ring", parent=RING, verts=96, bevel=0.01)
ring((0, 0, RH + 0.015), HUB_IN + 0.06, HUB_IN + 0.005, 0.03, "brass", "ring", parent=RING, verts=64)
for k in range(12):
    t = 2 * math.pi * (k + 0.5) / 12
    bolt((0.48 * math.cos(t), 0.48 * math.sin(t), RH + 0.012), 0.02, 0.016, group="ring", parent=RING)
# (round 6) a cast web plate between the spokes, recessed below their tops, a lightening
# hole in each bay: the ring reads as one heavy wheel, and the dark pit that showed through
# its spokes (most of the frame's black) is closed over
ring((0, 0, RH - 0.15), RB_IN + 0.004, HUB_OUT - 0.01, 0.05, "ring_in", "ring", parent=RING, verts=128, bevel=0.008)
for k in range(6):
    xh, yh = at(60 * k, (RB_IN + HUB_OUT) / 2)
    cyl((xh, yh, RH - 0.124), 0.1, 0.004, "dark", "ring", verts=32, parent=RING, bevel=0.0)       # the hole's shade
    ring((xh, yh, RH - 0.12), 0.12, 0.098, 0.012, "ring_worn", "ring", parent=RING, verts=32, bevel=0.003)  # its lip
# six spokes at 30 + 60k degrees: one to each guide column; deep cast webs, a flange along
# each top in the top face's lighter iron
for k in range(6):
    a = 30 + 60 * k
    r0, r1 = HUB_OUT - 0.03, RB_IN + 0.03
    x, y = at(a, (r0 + r1) / 2)
    box((x, y, RH - 0.2), (r1 - r0, 0.1, 0.36), "ring", "ring", rot=(0, 0, math.radians(a)), parent=RING)
    box((x, y, RH - 0.015), (r1 - r0, 0.17, 0.03), "ring_top", "ring", rot=(0, 0, math.radians(a)), parent=RING,
        bevel=0.006)
    for j in (-1, 1):                                  # its fillets into the hub and the band
        rr = r0 + 0.04 if j < 0 else r1 - 0.04
        xx, yy = at(a, rr)
        box((xx, yy, RH - 0.12), (0.08, 0.22, 0.2), "ring", "ring", rot=(0, 0, math.radians(a)), parent=RING,
            bevel=0.02)
# the shoes: a cast arm off the band to a collar round each north column, with the rope's eye
SHOE_H = 0.3
for a in (30, 150):
    x0, y0 = at(a, RB_OUT - 0.04)
    x1, y1 = at(a, GR_OUT - GUIDE_R - 0.06)
    box(((x0 + x1) / 2, (y0 + y1) / 2, RH / 2), (math.hypot(x1 - x0, y1 - y0), 0.2, 0.26), "ring", "ring",
        rot=(0, 0, math.radians(a)), parent=RING)
    box(((x0 + x1) / 2, (y0 + y1) / 2, RH / 2 + 0.14), (math.hypot(x1 - x0, y1 - y0), 0.24, 0.03), "ring_top", "ring",
        rot=(0, 0, math.radians(a)), parent=RING, bevel=0.006)              # its top flange
    xm, ym = at(a, RB_OUT + 0.05)
    box((xm, ym, RH / 2 - 0.1), (0.12, 0.08, 0.36), "ring", "ring", rot=(0, 0, math.radians(a)), parent=RING,
        bevel=0.015)                                                         # a gusset under it
    cx, cy = at(a, GR_OUT)
    ring((cx, cy, RH / 2), GUIDE_R + 0.11, GUIDE_R + 0.02, SHOE_H, "ring", "ring", parent=RING, verts=48)
    ring((cx, cy, RH / 2 + SHOE_H / 2 + 0.01), GUIDE_R + 0.04, GUIDE_R + 0.005, 0.02, "brass", "ring", parent=RING,
         verts=32)                                    # its bushing's lip
    out = 1 if cx > 0 else -1
    ex, ey = cx + out * (DRUM_R + 0.0), cy + 0.13
    eye = empty("eye", (ex, ey, RH / 2 + SHOE_H / 2 + 0.03), (0, 0, 0), parent=RING)
    box((0, 0, -0.005), (0.05, 0.08, 0.03), "steel", "ring", parent=eye, bevel=0.006)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.025, minor_radius=0.008, location=(0, 0, 0.03),
                                     rotation=(0, math.pi / 2, 0), major_segments=16, minor_segments=6)
    _finish(bpy.context.active_object, "steel", "ring", bevel=0, smooth=True, parent=eye)
# (round 6) the snubbers' lugs: four cast lugs off the band's foot, on the diagonals, that
# land on the snubbers standing on the deck (below) as the band lands on the shoulder
LUG_Z = 0.3                                   # the lug's underside, above the band's
SNUB_R = 1.5
for a in LUGS:
    xm, ym = at(a, (RB_OUT + SNUB_R + 0.1) / 2)
    box((xm, ym, LUG_Z + 0.06), (SNUB_R + 0.1 - RB_OUT, 0.2, 0.12), "ring", "ring", rot=(0, 0, math.radians(a)),
        parent=RING, bevel=0.015)
    box((xm, ym, LUG_Z + 0.125), (SNUB_R + 0.1 - RB_OUT, 0.22, 0.02), "ring_top", "ring", rot=(0, 0, math.radians(a)),
        parent=RING, bevel=0.005)
    xg, yg = at(a, RB_OUT + 0.06)
    box((xg, yg, (0.09 + LUG_Z) / 2 + 0.02), (0.1, 0.07, LUG_Z - 0.05), "ring", "ring", rot=(0, 0, math.radians(a)),
        parent=RING, bevel=0.015)                                            # its gusset to the foot
    xs, ys_ = at(a, SNUB_R)
    bolt((xs, ys_, LUG_Z + 0.14), 0.026, 0.02, group="ring", parent=RING)
for k in range(40):                                   # a bolt row round the lip's top, outer edge
    t = 2 * math.pi * (k + 0.5) / 40
    bolt(((RB_OUT - 0.05) * math.cos(t), (RB_OUT - 0.05) * math.sin(t), RH + 0.004), 0.015, 0.012, group="ring",
         parent=RING)
# the top face worn bright in broken runs where the crew and the shoes rub it
for a0, a1 in ((196, 248), (262, 304), (318, 346), (8, 24), (104, 146), (160, 178)):
    arc(RB_OUT + 0.025, RB_OUT - 0.005, RH - 0.03, 0.03, a0, a1, "polish", "ring", parent=RING)
for a0, a1 in ((222, 286), (54, 84), (300, 318)):
    arc(RB_IN + 0.05, RB_IN + 0.025, RH + 0.002, 0.005, a0, a1, "polish", "ring", parent=RING)
for a in (30, 150):
    cx, cy = at(a, GR_OUT)
    arc(GUIDE_R + 0.108, GUIDE_R + 0.03, RH / 2 + SHOE_H / 2 + 0.002, 0.005, 180, 360, "polish", "ring",
        parent=RING, cx=cx, cy=cy)

# The ropes: from each drum's outer side straight down to its shoe's eye. They hang from
# BODY, not the ring, and pose() sets their length each frame; in the ring's group, so
# they are drawn with the stroke.
ROPES = []
for (x, y, out) in WINCHES:
    me = bpy.data.meshes.new("rope")
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.012, radius2=0.012, depth=1.0)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, -0.5))    # its top at its origin, hanging down a unit
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("rope", me)
    sc.collection.objects.link(o)
    _finish(o, "cable", "ring", bevel=0, smooth=True)
    o.location = (x + out * DRUM_R, y + 0.13, WINCH_Z)
    ROPES.append(o)

# ---------------------------------------------------------------- 5. the status lamp

# on the hydraulic cabinet's roof (finish round 3): high on the south-west corner, where no
# pipe picture reaches in any direction and no chute stands
cyl((LAMP[0], LAMP[1], LAMP[2] + 0.03), 0.12, 0.06, "iron", verts=32, bevel=0.008)
cyl((LAMP[0], LAMP[1], LAMP[2] + 0.075), 0.095, 0.03, "brass", verts=32, bevel=0.006)
for k in range(4):
    u = 2 * math.pi * (k + 0.5) / 4
    bolt((LAMP[0] + 0.105 * math.cos(u), LAMP[1] + 0.105 * math.sin(u), LAMP[2] + 0.064), 0.011, 0.01)
lens = sphere((LAMP[0], LAMP[1], LAMP[2] + 0.09), 0.075, "lens", "lens", squash=0.7)

# ---------------------------------------------------------------- 5b. the services: hoses, cables, junction boxes
#
# Round 4 (Liam, beside vanilla's big mining drill: "we need to add more wiring and hoses
# and things, to make it look similar to vanilla factorio assets; these look too well
# machined"). Vanilla layers its machines with ribbed rubber hoses in heavy loops, thin
# insulated cables in a few muted colours bundled and clamped, and small boxes and fittings
# (the big mining drill's head, the electromagnetic plant's ring, the foundry's flanks).
# Here, as a visible and slightly untidy layer over the deck and the housings:
#   - hoses: ribbed rubber in two kinds and three sizes, sagging between their fittings and
#     lying where they meet the deck, a crimped ferrule and a nut at each end;
#   - cables: bundles of three to five in dull red, blue, green, yellow and black, zip-tied,
#     loose between the ties, in a ladder tray where they run along the deck, clipped where
#     they climb, entering junction boxes through brass glands;
#   - junction boxes, painted, on welded-on brackets: added after the castings were made.
# What they connect, quadrant by quadrant (a quadrant's services cross to another under the
# deck, through floor glands: nothing crosses a bay):
#   south-west: the hydraulic housing to the south and west hatches' rams (the bulkheads at
#     the risers' corners); a junction box on its roof feeding the lamp, its supply over the
#     roof's edge to a floor gland; oil on the deck below it;
#   south-east: the switchgear's bundle out of its north face into a tray along the deck to
#     a floor box; a valve block on its wing, its hose down to the east hatch's ram;
#   north-west: an accumulator bottle under the gear-house, hoses up to the winch brake and
#     along the deck to the north hatch's ram; the starter's cable up to the house's wall;
#   north-east: a floor gland at the rear leg, the motor's bundle clipped up the leg to a
#     junction box on the house's outer wall.
# Nothing stands in a bay, over a chute's crop or in the ring's travel (the ring's band
# reaches 1.59 from the centre; everything here is at 1.65 or more, or on a housing), and
# nothing passes through anything: every hose and cable is laid on the real surface under
# it (surface_z ray-casts the body as built), so where it sags onto something it rests on it.

M.update({
    "hose": layered("hose", "#34302C", metal="#5A5650", paint_metal=0.0, paint_rough=0.62, wear=0.25, rust=0.0,
                    dust=0.75, grime=0.6, jitter=0.12),
    "hose_brown": layered("hose_brown", "#6A4632", metal="#8E6A50", paint_metal=0.0, paint_rough=0.66, wear=0.3,
                          rust=0.1, dust=0.7, grime=0.6, jitter=0.12, rust_tint=("#3A1E0E", "#6E3C1C")),
    "c_red": layered("c_red", "#7A3A30", metal="#9A6A60", paint_metal=0.0, paint_rough=0.5, wear=0.15, rust=0.0,
                     dust=0.6, grime=0.5, jitter=0.1),
    "c_blue": layered("c_blue", "#3E5876", metal="#6A7E96", paint_metal=0.0, paint_rough=0.5, wear=0.15, rust=0.0,
                      dust=0.6, grime=0.5, jitter=0.1),
    "c_green": layered("c_green", "#4A6440", metal="#728A68", paint_metal=0.0, paint_rough=0.5, wear=0.15, rust=0.0,
                       dust=0.6, grime=0.5, jitter=0.1),
    "c_yellow": layered("c_yellow", "#98823A", metal="#B0A070", paint_metal=0.0, paint_rough=0.5, wear=0.15,
                        rust=0.0, dust=0.6, grime=0.5, jitter=0.1),
    "c_black": layered("c_black", "#2E2C2A", metal="#5A5652", paint_metal=0.0, paint_rough=0.5, wear=0.15,
                       rust=0.0, dust=0.6, grime=0.5, jitter=0.1),
    "tie": plain("tie", "#2A2826", rough=0.5),
    # junction boxes: painted steel, a dull grey-green, chipped to the metal at the edges
    "jbox": layered("jbox", "#5E6656", metal="#9A9C98", paint_metal=0.15, paint_rough=0.6, wear=0.55, rust=0.35,
                    dust=0.6, grime=0.6, jitter=0.12, rust_tint=("#3A1E0E", "#7A4420")),
    "tray": layered("tray", "#7C7E7E", metal="#B4B6B6", paint_metal=0.5, paint_rough=0.5, wear=0.4, rust=0.4,
                    dust=0.7, grime=0.5, jitter=0.1, rust_tint=("#3A1E0E", "#7A4420")),
    # oil on the deck: dark, wet and a little glossy
    "oil": plain("oil", "#1E1812", rough=0.22),
})
for _k in ("hose", "hose_brown", "c_red", "c_blue", "c_green", "c_yellow", "c_black", "jbox", "tray"):
    for _n in M[_k].node_tree.nodes:
        if _n.type == "AMBIENT_OCCLUSION":
            _n.samples = 4
        elif _n.type == "BEVEL":
            _n.samples = 2
CABLE = ("c_red", "c_blue", "c_green", "c_yellow", "c_black")
_SVC_RNG = random.Random(9031)

# (round 6) the snubbers: four hydraulic buffers on the deck under the lugs, a cast foot, a
# cylinder, a polished rod and a rubber-faced pad; the lug lands on the pad as the band
# seats, the machine's dead stop. Static: in the plate
SNUBS = []
for a in LUGS:
    xs, ys_ = at(a, SNUB_R)
    top = ZS + LUG_Z                                   # the pad's face: the lug's underside, seated
    box((xs, ys_, ZT + 0.03), (0.24, 0.24, 0.06), "iron", rot=(0, 0, math.radians(a)), bevel=0.012)
    for i in (-1, 1):
        for j in (-1, 1):
            u = Vector((i * 0.09, j * 0.09))
            u.rotate(Matrix.Rotation(math.radians(a), 2))
            bolt((xs + u.x, ys_ + u.y, ZT + 0.065), 0.015, 0.012)
    cyl((xs, ys_, (ZT + 0.06 + top - 0.12) / 2), 0.085, top - 0.12 - ZT - 0.06, "jbox", verts=24, bevel=0.01)
    cyl((xs, ys_, top - 0.12), 0.095, 0.03, "steel", verts=24, bevel=0.006)          # its gland nut
    cyl((xs, ys_, top - 0.07), 0.045, 0.08, "polish", verts=16, bevel=0.0)           # the rod
    cyl((xs, ys_, top - 0.02), 0.075, 0.03, "steel", verts=24, bevel=0.006)          # the pad's plate
    cyl((xs, ys_, top - 0.002), 0.065, 0.008, "hose", verts=24, bevel=0.0)           # its rubber face
    SNUBS.append((xs, ys_, a))


_SURF = []


def _surface_cache():
    """Every mesh of the body as built, with its model-space bounds, for surface_z."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    Binv = BODY.matrix_world.inverted()
    _SURF.clear()
    for g in ("body", "under"):
        for o in PARTS.get(g, []):
            if o.type != "MESH":
                continue
            Mo = Binv @ o.matrix_world
            cs = [Mo @ Vector(c) for c in o.bound_box]
            _SURF.append((o, Mo, Mo.inverted(), min(c.x for c in cs) - 0.02, max(c.x for c in cs) + 0.02,
                          min(c.y for c in cs) - 0.02, max(c.y for c in cs) + 0.02, max(c.z for c in cs)))
    return dg


_DG = []


def surface_z(x, y, below=10.0):
    """The top of whatever stands under (x, y) at or below the height `below`; the ground, 0."""
    dg = _DG[0]
    best = 0.0
    for o, Mo, Mi, x0, x1, y0, y1, z1 in _SURF:
        if x < x0 or x > x1 or y < y0 or y > y1 or z1 <= best:
            continue
        org = Mi @ Vector((x, y, below))
        d = (Mi.to_3x3() @ Vector((0, 0, -1))).normalized()
        ok, loc, _n, _i = o.ray_cast(org, d, depsgraph=dg)
        if ok:
            z = (Mo @ loc).z
            if best < z <= below + 1e-6:
                best = z
    return best


def lay(ctrl, sag=0.0, r=0.02, step=0.012, smooth=4, drape=True):
    """A run through control points, sagging `sag` (one, or one per span) between them, its
    corners rounded, laid on whatever is under it."""
    sags = sag if isinstance(sag, (list, tuple)) else [sag] * (len(ctrl) - 1)
    pts = []
    for i in range(len(ctrl) - 1):
        a, b = Vector(ctrl[i]), Vector(ctrl[i + 1])
        n = max(2, int((b - a).length / step))
        for k in range(n):
            t = k / n
            p = a.lerp(b, t)
            p.z -= sags[i] * 4 * t * (1 - t)
            pts.append(p)
    pts.append(Vector(ctrl[-1]))
    for _ in range(smooth):
        pts = [pts[0]] + [(pts[i - 1] + 2 * pts[i] + pts[i + 1]) / 4 for i in range(1, len(pts) - 1)] + [pts[-1]]
    if drape:
        for _ in range(2):
            for p in pts[2:-2]:
                floor = surface_z(p.x, p.y, p.z + 0.2) + r + 0.003
                if p.z < floor:
                    p.z = floor
            # raise-only smoothing, so it bends over an edge instead of kinking
            pts = [pts[0]] + [Vector((p.x, p.y, max(p.z, (pts[i - 1].z + 2 * p.z + pts[i + 1].z) / 4)))
                              if 1 < i < len(pts) - 2 else p for i, p in enumerate(pts[1:-1], 1)] + [pts[-1]]
    return pts


def frames(pts):
    n = len(pts)
    T = [(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(n)]
    N = T[0].cross(Vector((0, 0, 1)))
    if N.length < 1e-3:
        N = T[0].cross(Vector((1, 0, 0)))
    N.normalize()
    Ns, Bs, S = [], [], [0.0]
    for i in range(n):
        if i:
            S.append(S[-1] + (pts[i] - pts[i - 1]).length)
            v = T[i - 1].cross(T[i])
            if v.length > 1e-7:
                N = Matrix.Rotation(T[i - 1].angle(T[i]), 3, v.normalized()) @ N
            N = (N - T[i] * N.dot(T[i])).normalized()
        Ns.append(N.copy())
        Bs.append(T[i].cross(N))
    return T, Ns, Bs, S


def tube(pts, r, mat, seg=10, rib=0.0, pitch=0.035, name="hose"):
    """A flexible run swept along pts; rib > 0 corrugates it, a rib every `pitch`."""
    T, Ns, Bs, S = frames(pts)

    def build(bm):
        rows = []
        for i, p in enumerate(pts):
            rr = r * (1 - rib * 0.5 * (1 - math.cos(2 * math.pi * S[i] / pitch))) if rib else r
            rows.append([bm.verts.new(p + (Ns[i] * math.cos(a) + Bs[i] * math.sin(a)) * rr)
                         for a in (2 * math.pi * k / seg for k in range(seg))])
        for a, b in zip(rows, rows[1:]):
            for k in range(seg):
                bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
        bm.faces.new(list(reversed(rows[0])))
        bm.faces.new(rows[-1])
    return mesh_object(name, build, mat, "body", 0, smooth=True)


def hose(ctrl, r, mat="hose", sag=0.06, rib=0.22, pitch=None, ends=(True, True)):
    pts = lay(ctrl, sag, r, step=min(0.012, r * 0.45))
    tube(pts, r, mat, seg=12, rib=rib, pitch=pitch or r * 1.4)
    T = frames(pts)[0]
    for end, (p, t) in zip(ends, ((pts[0], -T[0]), (pts[-1], T[-1]))):
        if end:                                           # the crimped ferrule, then the nut
            along(p, t, r * 1.3, r * 2.6, "steel", verts=16, back=r * 1.2)
            for k in range(3):                            # its crimp marks
                along(p, t, r * 1.38, r * 0.25, "steel", verts=16, back=r * (1.6 + 0.75 * k))
            along(p, t, r * 1.55, r * 1.1, "bolt", verts=6, back=0.0)
    return pts


def bundle(ctrl, mats, r=0.011, sag=0.05, ties=0.14, loose=0.01, glands=(True, True)):
    """Cables side by side along a run: zip-tied tight every `ties`, loose between."""
    centre = lay(ctrl, sag, r * 2.6, step=0.01)
    T, Ns, Bs, S = frames(centre)
    L = S[-1]
    n = len(mats)
    rho = r * (1.05 if n > 1 else 0.0) * (1 + 0.15 * (n > 3))
    for j, m in enumerate(mats):
        a0 = 2 * math.pi * j / n
        ph, amp = _SVC_RNG.uniform(0, 6.28), loose * _SVC_RNG.uniform(0.4, 1.0)
        pts = []
        for i, p in enumerate(centre):
            d = min(abs(S[i] - ties * round(S[i] / ties)), S[i], L - S[i])
            f = min(1.0, d / (ties * 0.5))                  # 0 at a tie, 1 midway
            a = a0 + S[i] * 6.0                            # a slow twist
            off = rho + amp * f * (0.5 + 0.5 * math.sin(S[i] * 23 + ph))
            q = p + (Ns[i] * math.cos(a) + Bs[i] * math.sin(a)) * off
            q.z -= amp * f * 0.8 * (j % 2)                 # some hang lower between the ties
            pts.append(q)
        tube(pts, r, m, seg=7, name="cable")
    k = ties
    while k < L - 0.03:                                    # the ties
        i = min(range(len(S)), key=lambda q: abs(S[q] - k))
        rot = Vector((0, 0, 1)).rotation_difference(T[i]).to_euler()
        ring(tuple(centre[i]), rho + r + 0.004, rho + r - 0.001, 0.008, "tie", verts=16, bevel=0.0, rot=tuple(rot))
        k += ties
    for end, (p, t) in zip(glands, ((centre[0], -T[0]), (centre[-1], T[-1]))):
        if end:                                            # a brass gland where it enters
            along(p, t, rho + r + 0.008, 0.035, "brass", verts=12, back=-0.006)
            along(p, t, rho + r + 0.014, 0.012, "brass", verts=6, back=-0.02)
    return centre


def jbox(loc, size, rot_z=0.0, mat="jbox"):
    """A junction box: its body, a lid a hair proud, four lid screws, a hinge pin."""
    e = empty("jbox", loc, (0, 0, rot_z))
    w, d, h = size
    box((0, 0, h / 2), (w, d, h), mat, parent=e, bevel=0.006)
    box((0, 0, h + 0.006), (w + 0.01, d + 0.01, 0.012), mat, parent=e, bevel=0.004)
    for i in (-1, 1):
        for j in (-1, 1):
            bolt((i * (w / 2 - 0.018), j * (d / 2 - 0.018), h + 0.014), 0.008, 0.006, parent=e)
    box((0, -d / 2 - 0.002, h * 0.6), (w * 0.5, 0.004, h * 0.18), "stencil_worn", parent=e, bevel=0.0)  # its tag
    return e


def tray(a, b, z, w=0.09, legs=0.3, zf=ZT):
    """An open ladder tray from a to b (plan) at height z, on welded legs to the deck at zf."""
    a, b = Vector((a[0], a[1], z)), Vector((b[0], b[1], z))
    u = (b - a)
    L = u.length
    t = math.atan2(u.y, u.x)
    m = (a + b) / 2
    side = Vector((-math.sin(t), math.cos(t), 0))
    for sgn in (-1, 1):                                    # its two rails, angle section
        c = m + side * sgn * w / 2
        box(tuple(c), (L, 0.008, 0.03), "tray", rot=(0, 0, t), bevel=0.002)
        box(tuple(c - side * sgn * 0.006 + Vector((0, 0, -0.013))), (L, 0.02, 0.004), "tray", rot=(0, 0, t), bevel=0.0)
    k = 0.03
    while k < L:                                           # its rungs
        c = a + u.normalized() * k + Vector((0, 0, -0.012))
        box(tuple(c), (0.012, w, 0.006), "tray", rot=(0, 0, t), bevel=0.0)
        k += 0.045
    nl = max(2, int(L / legs) + 1)
    for i in range(nl):                                    # legs, welded to the deck at a foot plate
        c = a + u * (i / (nl - 1)) * 0.9 + u * 0.05
        box((c.x, c.y, (zf + z - 0.015) / 2), (0.012, w + 0.02, z - 0.015 - zf), "tray", rot=(0, 0, t), bevel=0.0)
        box((c.x, c.y, zf + 0.004), (0.05, w + 0.04, 0.008), "tray", rot=(0, 0, t), bevel=0.002)
    return a, b


def stain(cx, cy, rx, ry, n=5, z=None):
    """Oil on the deck: a few overlapping wet blots."""
    zz = (surface_z(cx, cy) if z is None else z) + 0.0012
    for k in range(n):
        ox, oy = _SVC_RNG.uniform(-rx, rx) * 0.6, _SVC_RNG.uniform(-ry, ry) * 0.6
        o = cyl((cx + ox, cy + oy, zz + 0.0003 * k), 1.0, 0.0012, "oil", verts=24, bevel=0.0)
        o.scale = (rx * _SVC_RNG.uniform(0.35, 0.8), ry * _SVC_RNG.uniform(0.35, 0.8), 1)
        o.rotation_euler.z = _SVC_RNG.uniform(0, 3.14)


def bulkhead(x, y, z, *ts):
    """A ram's bulkhead fitting at a riser's corner, on the surface at z: a bolted block and
    a nipple facing each of ts (degrees), toward its hose; returns the nipples' tips."""
    box((x, y, z + 0.022), (0.07, 0.07, 0.044), "steel", bevel=0.006)
    for i in (-1, 1):
        for j in (-1, 1):
            bolt((x + i * 0.022, y + j * 0.022, z + 0.047), 0.009, 0.007)
    tips = []
    for t in ts:
        u = Vector((math.cos(math.radians(t)), math.sin(math.radians(t)), 0))
        tip = Vector((x, y, z + 0.024)) + u * 0.06
        along(tip, u, 0.014, 0.03, "brass", verts=12)
        tips.append(tuple(tip + u * 0.004))
    return tips if len(tips) > 1 else tips[0]


# The routes are laid where this camera sees them: it looks from the south, so the deck
# north of a housing is behind it and the north quadrants' deck behind the gear-houses.
# So the services run over the housings' roofs and south faces, the wings, the deck
# either side of the bays, and the gear-houses' roofs and open fronts.
# the fittings and boxes first, so the runs lie on them
cx_sw, cy_sw, ys_sw = HOUSES[-1]
cx_se, cy_se, ys_se = HOUSES[1]
RT = HOUSE_TOP + 0.04                                     # the housings' roof (its cap's top)
# --- south-west: the hydraulic housing
B_S, B_S2 = bulkhead(-0.6, -1.585, ZT + 0.024, 180, 90)    # the south ram's, on its riser's cap rail
B_W, B_W2 = bulkhead(-1.6, -0.86, ZT, -60, -90)             # the west ram's, at its riser's corner
# the roof's manifold: a valve block on a welded plate, its fittings facing east and west
MF = (-0.98, -1.62)
box((MF[0], MF[1], RT + 0.006), (0.2, 0.14, 0.012), "steel", bevel=0.003)
for (a_, b_) in (((MF[0] - 0.1, MF[1] - 0.07), (MF[0] + 0.1, MF[1] - 0.07)),):
    weld((a_[0], a_[1], RT + 0.004), (b_[0], b_[1], RT + 0.004))
box((MF[0], MF[1], RT + 0.06), (0.16, 0.1, 0.09), "jbox", bevel=0.008)
for k, dx in enumerate((-0.05, 0.0, 0.05)):
    cyl((MF[0] + dx, MF[1] + 0.055, RT + 0.07), 0.014, 0.02, "brass", verts=10, rot=(math.pi / 2, 0, 0), bevel=0.0)
cyl((MF[0] + 0.03, MF[1], RT + 0.13), 0.028, 0.05, "copper", verts=12, bevel=0.004)          # a solenoid
P_E1 = (MF[0] + 0.085, MF[1] - 0.02, RT + 0.07)          # its east fittings (to the south ram)
P_E2 = (MF[0] + 0.085, MF[1] + 0.025, RT + 0.05)
P_W1 = (MF[0] - 0.085, MF[1] - 0.01, RT + 0.07)          # its west fittings (to the west ram)
P_W2 = (MF[0] - 0.085, MF[1] + 0.03, RT + 0.05)
for p_ in (P_E1, P_E2, P_W1, P_W2):
    cyl(p_, 0.016, 0.02, "brass", verts=10, rot=(0, math.pi / 2, 0), bevel=0.0)
# the lamp's junction box, on the roof's south-east corner, on a welded bracket
JB_SW = (-0.95, -2.25, RT)
box((JB_SW[0], JB_SW[1], RT + 0.006), (0.12, 0.17, 0.012), "steel", bevel=0.003)
weld((JB_SW[0] - 0.06, JB_SW[1] - 0.085, RT + 0.004), (JB_SW[0] - 0.06, JB_SW[1] + 0.085, RT + 0.004))
jbox((JB_SW[0], JB_SW[1], RT + 0.012), (0.1, 0.14, 0.1), math.radians(3))
# a gland at the east end of the south face (its west end is the core's notch), where the
# supply comes out of the housing
GL_SW = (-0.843, ys_sw - 0.03, 1.05)
box((GL_SW[0], ys_sw - 0.012, GL_SW[2]), (0.07, 0.024, 0.09), "jbox", bevel=0.005)
# --- south-east: the switchgear
VB = (1.78, -1.62, WING_TOP + 0.03)                       # the east ram's valve block, on the wing
box((VB[0], VB[1], VB[2] + 0.045), (0.16, 0.12, 0.09), "jbox", bevel=0.008)
cyl((VB[0] - 0.04, VB[1], VB[2] + 0.13), 0.025, 0.07, "copper", verts=12, bevel=0.004)          # its solenoid
cyl((VB[0] + 0.045, VB[1] + 0.01, VB[2] + 0.12), 0.018, 0.05, "steel", verts=12, bevel=0.003)
for yy in (VB[1] - 0.065, VB[1] + 0.065):
    weld((VB[0] - 0.08, yy, VB[2] + 0.004), (VB[0] + 0.08, yy, VB[2] + 0.004))
B_E = bulkhead(1.56, -0.86, ZT, -120)
# the roof: a junction box at its west end, a ladder tray along its north side
JB_SE = (0.86, -1.62, RT)
box((JB_SE[0], JB_SE[1], RT + 0.006), (0.11, 0.2, 0.012), "steel", bevel=0.003)
weld((JB_SE[0] + 0.055, JB_SE[1] - 0.1, RT + 0.004), (JB_SE[0] + 0.055, JB_SE[1] + 0.1, RT + 0.004))
jbox((JB_SE[0], JB_SE[1], RT + 0.012), (0.1, 0.16, 0.11), math.radians(-2))
TR = tray((0.98, -1.475), (1.32, -1.475), RT + 0.06, w=0.08, zf=RT)
# a wall gland low on its south face, between its edge and the first rib
GL_SE = (0.84, ys_se - 0.012, STEP_TOP + 0.16)            # above the front step (round 5)
box((GL_SE[0], GL_SE[1], GL_SE[2]), (0.08, 0.024, 0.09), "jbox", bevel=0.005)
# --- north: a junction box on each gear-house's roof
JB_N = {}
for (x, y, out) in WINCHES:
    gx = x + out * 0.05
    p_ = (gx + out * 0.2, y - 0.2, HR + 0.06)
    if out > 0:
        p_ = (gx + 0.27, y - 0.22, HR + 0.06)                # beside the roof hatch
    box((p_[0], p_[1], p_[2] + 0.006), (0.18, 0.14, 0.012), "steel", bevel=0.003)
    weld((p_[0] - 0.09, p_[1] - 0.07, p_[2] + 0.004), (p_[0] + 0.09, p_[1] - 0.07, p_[2] + 0.004))
    jbox((p_[0], p_[1], p_[2] + 0.012), (0.15, 0.11, 0.1), math.radians(-4 * out))
    JB_N[out] = p_
# the gear-houses' roofs, the largest flat surfaces the camera sees: on the north-west's
# a fan cowl over the winch motor's cooling duct and a tray to it; on the north-east's a
# lubricant reservoir on saddles, by the hatch (kept south of 1.3, under the drawn top)
xw_, yw_, _ = WINCHES[1]
gxw = xw_ - 0.05
COWL = (gxw + 0.3, yw_ + 0.2, HR + 0.06)
box((COWL[0], COWL[1], COWL[2] + 0.06), (0.24, 0.18, 0.12), "jbox", bevel=0.01)
for k in range(4):
    box((COWL[0], COWL[1] - 0.092, COWL[2] + 0.025 + 0.025 * k), (0.18, 0.012, 0.01), "steel", bevel=0.0)
box((COWL[0], COWL[1], COWL[2] + 0.128), (0.26, 0.2, 0.016), "jbox", bevel=0.004)
for i in (-1, 1):
    weld((COWL[0] + i * 0.12, COWL[1] - 0.09, COWL[2] + 0.004), (COWL[0] + i * 0.12, COWL[1] + 0.09, COWL[2] + 0.004))
TR_NW = tray((gxw - 0.12, yw_ - 0.33), (gxw + 0.18, yw_ - 0.33), HR + 0.12, w=0.08, zf=HR + 0.06)
xe_, ye_, _ = WINCHES[0]
gxe = xe_ + 0.05
RES = (gxe - 0.28, ye_ - 0.28, HR + 0.06)
for dx in (-0.08, 0.08):
    box((RES[0] + dx, RES[1], RES[2] + 0.03), (0.03, 0.14, 0.06), "steel", bevel=0.003)          # saddles
cyl((RES[0], RES[1], RES[2] + 0.1), 0.07, 0.3, "jbox", verts=24, rot=(0, math.pi / 2, 0), bevel=0.01)
for dx in (-0.08, 0.08):
    ring((RES[0] + dx, RES[1], RES[2] + 0.1), 0.077, 0.068, 0.02, "steel", verts=24, bevel=0.0, rot=(0, math.pi / 2, 0))
cyl((RES[0] + 0.06, RES[1], RES[2] + 0.18), 0.022, 0.03, "brass", verts=12, bevel=0.003)          # its filler cap
cyl((RES[0] - 0.06, RES[1] - 0.06, RES[2] + 0.11), 0.02, 0.025, "polish", verts=12, rot=(math.pi / 2, 0, 0), bevel=0.0)

# north-west: the accumulator bottle under the house, on a welded saddle; the brake
# cylinder under the winch's platform; the north ram's bulkhead
# (round 5: the accumulator is inside the drive cabinet now; its fittings on the cabinet's
# south and inner faces)
_c0, _c1, _cy0, _cy1 = CABS[-1]
F_BRK = (_c0 + 0.012, 0.8, 2.0)                           # on its inner face, above the shoe's reach (1.83)
F_NR = (-1.5 + 0.012, 1.35, ZT + 0.12)                     # on its inner step's face, low
for f_, rt_ in ((F_BRK, (0, math.pi / 2, 0)), (F_NR, (0, math.pi / 2, 0))):
    cyl(f_, 0.03, 0.03, "steel", verts=6, rot=rt_, bevel=0.0)
BRK = (WINCHES[1][0] - 0.14, WINCHES[1][1] - 0.215)
cyl((BRK[0], BRK[1], GUIDE_TOP - 0.06), 0.035, 0.1, "steel", verts=16, bevel=0.004)
B_N = bulkhead(-0.76, 1.58, ZT, 200)
FG_N = (0.92, 1.4)                                       # a floor gland by the north-east starter
cyl((FG_N[0], FG_N[1], ZT + 0.012), 0.045, 0.024, "steel", verts=16, bevel=0.004)
cyl((FG_N[0], FG_N[1], ZT + 0.034), 0.028, 0.026, "brass", verts=12, bevel=0.003)

# the south legs' levelling jacks: a ram on each pad, beside the leg, its hose fitting on top
JACKS = {}
for sx, (jx, jy) in ((-1, (-1.95, -2.36)), (1, (2.36, -1.95))):
    box((jx, jy, 0.12), (0.13, 0.13, 0.02), "steel", bevel=0.004)                       # its base, welded on
    cyl((jx, jy, 0.21), 0.05, 0.16, "jbox", verts=20, bevel=0.008)                      # the cylinder
    cyl((jx, jy, 0.3), 0.036, 0.03, "polish", verts=16, bevel=0.003)                    # the rod's gland
    cyl((jx, jy, 0.33), 0.03, 0.04, "steel", verts=16, bevel=0.003)
    cyl((jx + 0.055 * (1 if sx < 0 else 0), jy + 0.055 * (1 if sx > 0 else 0), 0.25), 0.016, 0.03, "brass", verts=10,
        rot=(0, math.pi / 2, 0) if sx < 0 else (math.pi / 2, 0, 0), bevel=0.0)       # its port
    JACKS[sx] = (jx + 0.075 * (1 if sx < 0 else 0), jy + 0.075 * (1 if sx > 0 else 0), 0.25)
# the south-west jack's supply: an outlet block on the housing's foot flange
OUT_SW = (-0.86, ys_sw - 0.06, 0.8)
box((OUT_SW[0], OUT_SW[1], OUT_SW[2]), (0.08, 0.05, 0.07), "steel", bevel=0.005)
cyl((OUT_SW[0] - 0.05, OUT_SW[1], OUT_SW[2]), 0.016, 0.03, "brass", verts=10, rot=(0, math.pi / 2, 0), bevel=0.0)
# --- (round 7) the silhouette: the corner wings cantilevered out over the deeper notches,
# each propped from its leg's pad by a diagonal brace; on the south-west wing the
# hydraulic pack's reservoir, a round tank lying along the wing's diagonal edge and
# overhanging it; on the south-east two accumulator bottles on a bracket out over the
# corner. Round, diagonal masses at a third height between the deck and the roofs.
for sx in (-1, 1):
    pad = Vector((sx * PAD, -PAD, 0.19))
    for (ex, ey) in ((1.62, -1.97), (1.94, -1.65)):
        top = Vector((sx * ex, ey, 0.62))
        rod(pad + (top - pad).normalized() * 0.08, top, 0.05, 0.045, "leg")
        box(tuple(top + Vector((0, 0, 0.0))), (0.12, 0.12, 0.04), "steel", bevel=0.005)          # its cleat
    rod(pad + Vector((0, 0, 0.0)), Vector((sx * 1.78, -1.81, 0.62)), 0.07, 0.06, "leg")            # the main prop
# the south-west reservoir
TK = Vector((-1.76, -1.76, WING_TOP + 0.24))
TK_U = Vector((-1, 1, 0)).normalized()                     # along the wing's diagonal edge
rod(TK - TK_U * 0.4, TK + TK_U * 0.4, 0.21, 0.21, "oxide", seg=36)
for sgn in (-1, 1):                                        # its dished ends
    sphere(tuple(TK + TK_U * (0.33 * sgn)), 0.21, "oxide", seg=24)
    rod(TK + TK_U * (0.33 * sgn) - TK_U * 0.02, TK + TK_U * (0.33 * sgn) + TK_U * 0.02, 0.222, 0.222, "steel")  # its band
    sad = TK + TK_U * (0.25 * sgn)
    box((sad.x, sad.y, WING_TOP + 0.06), (0.1, 0.1, 0.1), "steel", rot=(0, 0, math.radians(45)), bevel=0.006)  # saddle
cyl((TK.x + 0.05, TK.y + 0.05, TK.z + 0.22), 0.035, 0.05, "brass", verts=16, bevel=0.004)     # filler
cyl((TK.x - 0.12, TK.y + 0.12, TK.z + 0.2), 0.03, 0.06, "steel", verts=12, bevel=0.003)        # level switch
TK_OUT = (TK.x + 0.14, TK.y - 0.14, TK.z - 0.1)                                               # its outlet
cyl(TK_OUT, 0.02, 0.05, "brass", verts=12, rot=(0, math.pi / 2, math.radians(-45)), bevel=0.0)
# the south-east bottles, on a bracket out over the corner, along the wing's diagonal edge
BT = []
BT_U = Vector((1, 1, 0)).normalized()                     # along the edge
BT_P = Vector((1, -1, 0)).normalized()                    # across it, outward
for off in (-0.13, 0.13):
    c = Vector((1.9, -1.9, WING_TOP + 0.16)) + BT_P * off
    rod(c - BT_U * 0.28, c + BT_U * 0.28, 0.1, 0.1, "oxide", seg=28)
    for sgn in (-1, 1):
        sphere(tuple(c + BT_U * (0.28 * sgn)), 0.1, "oxide", seg=20)
    cyl(tuple(c - BT_U * 0.38), 0.025, 0.06, "brass", verts=12,
        rot=tuple(Vector((0, 0, 1)).rotation_difference(BT_U).to_euler()), bevel=0.0)          # its valve
    BT.append(tuple(c - BT_U * 0.41))
for sgn in (-1, 1):                                                                             # the bracket's straps
    c = Vector((1.9, -1.9, WING_TOP + 0.04)) + BT_U * (0.18 * sgn)
    box(tuple(c), (0.5, 0.05, 0.08), "steel", rot=(0, 0, math.radians(-45)), bevel=0.004)

_DG.append(_surface_cache())

# --- hoses
# south-west: supply and return from the roof's manifold, over the roof's east edge and
# down to the south ram -- a heavy black one, a thinner brown return
hose([P_E1, (-0.86, -1.64, RT + 0.08), (-0.74, -1.62, RT + 0.04), (-0.72, -1.6, 1.6), (-0.7, -1.59, 1.1),
      (-0.68, -1.585, 0.97), B_S],
     0.034, "hose", sag=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], rib=0.2)
hose([P_E2, (-0.84, -1.58, RT + 0.05), (-0.745, -1.52, RT + 0.02), (-0.72, -1.5, 1.4), (-0.68, -1.47, 1.02),
      (-0.62, -1.455, 0.96), B_S2], 0.022, "hose_brown", sag=0.0, rib=0.25)
# to the west ram: off the roof's west edge onto the wing, over it, and down to the deck
hose([P_W1, (-1.15, -1.6, RT + 0.07), (-1.52, -1.58, RT + 0.06), (-1.62, -1.56, WING_TOP + 0.2), (-1.72, -1.5, WING_TOP + 0.05),
      (-1.78, -1.4, 1.2), (-1.72, -1.15, ZT + 0.04), B_W], 0.04, "hose", sag=[0.0, 0.03, 0.0, 0.0, 0.0, 0.03, 0.02],
     rib=0.2)
hose([P_W2, (-1.2, -1.53, RT + 0.05), (-1.5, -1.52, RT + 0.05), (-1.6, -1.5, WING_TOP + 0.17), (-1.66, -1.46, WING_TOP + 0.04),
      (-1.66, -1.38, 1.15), (-1.6, -1.12, ZT + 0.03), B_W2], 0.024,
     "hose_brown", sag=[0.0, 0.02, 0.0, 0.0, 0.0, 0.03, 0.02], rib=0.25)
# south-east: the valve block's hose off the wing, down to the east ram
hose([(VB[0], VB[1] + 0.065, VB[2] + 0.05), (1.76, -1.42, 1.3), (1.7, -1.25, 1.05), (1.62, -1.05, 0.94), B_E],
     0.034, "hose_brown", sag=[0.0, 0.03, 0.04, 0.02], rib=0.22)
# the legs' jacks: south-west along the wall's ledge and down over its corner; south-east
# off the wing, down beside the notch
hose([(OUT_SW[0] - 0.07, OUT_SW[1], OUT_SW[2]), (-1.0, -2.47, 0.78), (-1.3, -2.48, 0.74), (-1.5, -2.5, 0.68),
      (-1.62, -2.5, 0.5), (-1.75, -2.45, 0.3), (-1.85, -2.38, 0.25), JACKS[-1]], 0.03, "hose", sag=[0.0, 0.0, 0.0, 0.0,
      0.0, 0.03, 0.0], rib=0.22)
hose([(VB[0] + 0.08, VB[1] - 0.02, VB[2] + 0.05), (1.93, -1.66, WING_TOP + 0.04), (2.06, -1.62, 1.2),
      (2.15, -1.66, 0.8), (2.25, -1.78, 0.45), (2.33, -1.86, 0.3), JACKS[1]], 0.028, "hose", sag=[0.0, 0.0, 0.0, 0.03,
      0.0, 0.0], rib=0.22)
# north-west: the accumulator's hoses -- up to the winch's brake cylinder in a slack loop,
# and along the deck to the north ram
hose([(F_BRK[0] + 0.02, F_BRK[1], F_BRK[2]), (-1.92, 0.78, 2.03), (BRK[0] - 0.02, BRK[1] - 0.03, GUIDE_TOP - 0.19),
      (BRK[0], BRK[1], GUIDE_TOP - 0.11)], 0.026, "hose", sag=0.0, rib=0.25)
hose([(F_NR[0] + 0.02, F_NR[1], F_NR[2]), (-1.4, 1.33, ZT + 0.05), (-1.25, 1.38, ZT), (-1.15, 1.44, ZT),
      (-0.88, 1.47, ZT), B_N], 0.034, "hose_brown", sag=0.04, rib=0.22)

# (round 6) the snubbers' hoses: each from a port on its cylinder, slack over the deck, to a
# bulkhead on the nearest housing's face -- the south ones to the housings' north faces, the
# north ones to the drive cabinets' inner steps
for (xs, ys_, a) in SNUBS:
    sx_, sy_ = (1 if xs > 0 else -1), (1 if ys_ > 0 else -1)
    zp = ZT + 0.2
    port = (xs + sx_ * 0.1, ys_, zp)
    cyl(port, 0.018, 0.04, "brass", verts=10, rot=(0, math.pi / 2, 0), bevel=0.0)
    if sy_ < 0:
        end = (sx_ * 1.32, HOUSE_N + 0.012, ZT + 0.32)
        box((end[0], HOUSE_N + 0.01, end[2]), (0.08, 0.02, 0.08), "steel", bevel=0.004)
        mid = [(xs + sx_ * 0.2, ys_ - 0.03, ZT + 0.04), (sx_ * 1.3, -1.28, ZT + 0.04), (sx_ * 1.32, HOUSE_N + 0.08, ZT + 0.2)]
        end = (end[0], HOUSE_N + 0.03, end[2])
    else:
        end = (sx_ * (1.5 - 0.012), 1.48, ZT + 0.3)
        box((sx_ * 1.495, 1.48, end[2]), (0.02, 0.08, 0.08), "steel", bevel=0.004)
        mid = [(xs + sx_ * 0.16, ys_ + 0.14, ZT + 0.04), (sx_ * 1.4, 1.38, ZT + 0.04), (sx_ * 1.44, 1.47, ZT + 0.2)]
        end = (sx_ * 1.47, 1.48, end[2])
    hose([port] + mid + [end], 0.024, "hose" if sy_ < 0 else "hose_brown", sag=0.03, rib=0.24)
    stain(xs + sx_ * 0.05, ys_ - 0.1, 0.06, 0.05, n=3)

_DG[0] = _surface_cache()                                  # the cables lie over the hoses

# --- cables
# south-west: the lamp's supply out of the south face's gland, clipped up the face, over
# the roof's edge to the box; from the box to the lamp, and to the manifold's solenoid
bundle([(GL_SW[0], ys_sw - 0.03, GL_SW[2] + 0.05), (GL_SW[0], ys_sw - 0.04, 1.4),
        (GL_SW[0] - 0.005, ys_sw - 0.04, RT - 0.05), (GL_SW[0] - 0.02, ys_sw - 0.02, RT + 0.06),
        (JB_SW[0] + 0.01, JB_SW[1] - 0.12, RT + 0.06), (JB_SW[0], JB_SW[1] - 0.075, RT + 0.06)],
       ("c_red", "c_black", "c_blue", "c_yellow"), sag=0.0, ties=0.12)
for zc in (1.2, 1.55):                                      # its clips on the face
    box((GL_SW[0], ys_sw - 0.008, zc), (0.05, 0.016, 0.02), "steel", bevel=0.002)
bundle([(JB_SW[0] - 0.02, JB_SW[1] + 0.075, RT + 0.06), (-1.0, -2.13, RT + 0.06), (LAMP[0] + 0.0, LAMP[1] - 0.125,
        LAMP[2] + 0.03)], ("c_green", "c_red"), sag=0.0)
bundle([(JB_SW[0] + 0.03, JB_SW[1] + 0.075, RT + 0.06), (-0.88, -2.08, RT + 0.06), (-0.88, -1.78, RT + 0.06),
        (-0.93, -1.66, RT + 0.14), (MF[0] + 0.03, MF[1] - 0.03, RT + 0.165)], ("c_yellow", "c_black"), sag=0.0)
# south-east: the switchgear's bundle out of the roof box, along the tray, over the roof's
# east edge onto the wing, to the valve block
bundle([(JB_SE[0] + 0.02, JB_SE[1] + 0.085, RT + 0.07), (0.92, -1.48, RT + 0.09), (1.0, -1.475, RT + 0.09),
        (1.32, -1.475, RT + 0.09), (1.48, -1.49, RT + 0.06), (1.58, -1.5, RT + 0.04), (1.62, -1.55, WING_TOP + 0.25),
        (1.68, -1.6, WING_TOP + 0.15), (VB[0] - 0.04, VB[1], VB[2] + 0.17)],
       ("c_red", "c_blue", "c_green", "c_black", "c_yellow"), r=0.01, sag=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.02],
       ties=0.12)
# and from the box over its west edge, down the south face to the wall gland
bundle([(JB_SE[0] - 0.01, JB_SE[1] - 0.085, RT + 0.07), (0.83, -1.8, RT + 0.06), (0.835, -1.95, RT + 0.06),
        (0.84, ys_se - 0.04, RT - 0.1), (GL_SE[0], ys_se - 0.04, GL_SE[2] + 0.25), (GL_SE[0], ys_se - 0.035, GL_SE[2] + 0.05)], ("c_blue", "c_black", "c_red"),
       sag=0.0, ties=0.12)
# north: from each roof box, over the roof's front edge, hanging down into the house's open
# front to the winch's motor
for (x, y, out) in WINCHES:
    jb = JB_N[out]
    mx_ = x + out * math.sqrt((GEAR_R + 0.07) ** 2 - 0.17 ** 2)
    bundle([(jb[0], jb[1] - 0.065, jb[2] + 0.06), (jb[0] + out * 0.02, y - 0.47, HR + 0.08),
            (mx_, y - 0.53, HR - 0.15), (mx_, y - 0.42, WINCH_Z + 0.06), (mx_, y - 0.18, WINCH_Z + 0.05),
            (mx_, y - 0.02, WINCH_Z + 0.04), (mx_, y + 0.12, WINCH_Z - 0.17 + 0.095)],
           ("c_blue", "c_red", "c_black") if out > 0 else ("c_green", "c_black"), sag=[0.0, 0.0, 0.05, 0.0, 0.0, 0.0],
           ties=0.15)
for (x, y, out) in WINCHES:
    jb = JB_N[out]
    gx = x + out * 0.05
    bundle([(jb[0] + out * 0.08, jb[1] + 0.02, jb[2] + 0.06), (jb[0] + out * 0.14, jb[1] + 0.25, HR + 0.08),
            (gx + out * 0.42, y + 0.4, HR + 0.08), (gx + out * 0.535, y + 0.42, HR + 0.0),
            (gx + out * 0.545, y + 0.42, HR - 0.25)], ("c_yellow", "c_black", "c_red", "c_blue"), sag=0.0, ties=0.13,
           glands=(True, False))
# the north-west roof's tray, from its box to the fan cowl; the north-east's box to the
# reservoir's level switch, and a copper line from the reservoir over the roof's front
bundle([(JB_N[-1][0] + 0.08, JB_N[-1][1] + 0.0, JB_N[-1][2] + 0.06), (gxw - 0.12, yw_ - 0.33, HR + 0.14),
        (gxw + 0.18, yw_ - 0.33, HR + 0.14), (COWL[0] - 0.06, COWL[1] - 0.2, HR + 0.13),
        (COWL[0] - 0.06, COWL[1] - 0.093, HR + 0.1)], ("c_red", "c_blue", "c_black"), sag=0.0, ties=0.12)
bundle([(JB_N[1][0] - 0.08, JB_N[1][1] + 0.0, JB_N[1][2] + 0.06), (RES[0] + 0.1, RES[1] - 0.12, HR + 0.09),
        (RES[0] - 0.06, RES[1] - 0.09, RES[2] + 0.11)], ("c_yellow", "c_green"), sag=0.0)
pipe([(RES[0] - 0.15, RES[1], RES[2] + 0.1), (RES[0] - 0.22, RES[1], RES[2] + 0.1), (RES[0] - 0.22, ye_ - 0.5, HR + 0.08),
      (RES[0] - 0.22, ye_ - 0.53, HR - 0.2), (RES[0] - 0.22, ye_ - 0.45, WINCH_Z + 0.1)], 0.009, "copper", bend=0.04)
# (round 5) slung between the two gear-houses' roofs, behind the column and high over the
# ring's travel (the ring's top is at 1.94; the run's low point at about 2.55): the winches'
# interlock cables and the lubricant line from the north-east's reservoir to the
# north-west's winch -- slack, clipped at each roof edge, over the north band
_before_sling = set(bpy.data.objects)
for (mat_, yy, r_, sg) in ((("hose", 1.41, 0.022, 0.16), (None, 1.33, 0.0, 0.12)) if "--nosling" not in argv else ()):
    a_, b_ = (-1.2, yy, HR + 0.08), (1.2, yy + 0.03, HR + 0.08)
    for x_ in (-1.25, 1.25):                                # the clip on each roof's inner edge
        box((x_, yy, HR + 0.07), (0.06, 0.06, 0.03), "steel", bevel=0.004)
    if mat_:
        hose([(-1.5, yy, HR + 0.09), a_, (0.0, yy + 0.02, HR - 0.3), b_, (1.5, yy + 0.04, HR + 0.09)], r_, mat_,
             sag=[0.0, sg, sg, 0.0], rib=0.25, ends=(True, True))
    else:
        bundle([(JB_N[-1][0] + 0.07, JB_N[-1][1] + 0.06, JB_N[-1][2] + 0.06), (-1.62, yy, HR + 0.1), a_,
                (0.0, yy, HR - 0.25), b_, (1.45, yy + 0.03, HR + 0.1), (JB_N[1][0] - 0.07, JB_N[1][1] + 0.06,
                                                                     JB_N[1][2] + 0.06)],
               ("c_black", "c_red", "c_blue", "c_yellow"), sag=[0.0, 0.0, sg, sg, 0.0, 0.0], ties=0.2)
SLUNG = [o for o in bpy.data.objects if o not in _before_sling and o.parent == BODY]   # the proposal swings them
# north-east: the starter's cable out of its roof, over its front edge and down to a floor gland
bundle([(1.02 + 0.06, 1.62 - 0.06, ZT + 0.885), (1.06, 1.47, ZT + 0.9), (1.03, 1.46, ZT + 0.2),
        (FG_N[0], FG_N[1], ZT + 0.06)], ("c_red", "c_black", "c_yellow"), sag=[0.0, 0.0, 0.03])
# north-west: the starter's cable out of its roof, down to the deck beside the north ram's hose
bundle([(-1.02 + 0.06, 1.62 - 0.06, ZT + 0.885), (-0.95, 1.47, ZT + 0.88), (-0.93, 1.45, ZT + 0.25),
        (-0.86, 1.62, ZT + 0.05), (-0.77, 1.635, ZT + 0.03)], ("c_blue", "c_green"),
       sag=[0.0, 0.0, 0.0, 0.0])

# --- (round 7) more of it, where the silhouette is: the reservoir's feed down the wing and
# over the deck to the south-west snubber; the bottles' hoses down into the south-east
# corner to the leg's jack; a festoon of cables and a hose looping down each side from the
# drive cabinets to the walls; a bundle clipped along every leg to its pad.
xs_, ys_ = at(225, SNUB_R)
cyl((xs_, ys_ - 0.09, ZT + 0.2), 0.018, 0.04, "brass", verts=10, rot=(math.pi / 2, 0, 0), bevel=0.0)
hose([TK_OUT, (-1.6, -1.95, WING_TOP + 0.05), (-1.72, -1.5, WING_TOP + 0.12), (-1.7, -1.38, 1.3),
      (-1.5, -1.3, ZT + 0.06), (xs_ - 0.05, ys_ - 0.2, ZT + 0.05), (xs_, ys_ - 0.11, ZT + 0.2)], 0.03, "hose",
     sag=[0.0, 0.02, 0.0, 0.04, 0.03, 0.0], rib=0.22)
for k, v in enumerate(BT):
    hose([v, (1.6 + 0.06 * k, -2.2, 1.55), (1.75 + 0.06 * k, -2.32, 0.9), (1.95 + 0.04 * k, -2.33, 0.5),
          (JACKS[1][0] - 0.02 * k, JACKS[1][1] - 0.04, JACKS[1][2] + 0.12)], 0.022 + 0.006 * k,
         "hose_brown" if k else "hose", sag=[0.03, 0.05, 0.03, 0.02], rib=0.24, ends=(True, k == 0))
for sx in (-1, 1):
    c0_, c1_, cy0_, cy1_ = CABS[sx]
    g0 = (sx * (abs(c1_) + 0.012), 1.25, 1.95)
    box((g0[0] - sx * 0.006, g0[1], g0[2]), (0.024, 0.09, 0.09), "jbox", bevel=0.005)
    bundle([(g0[0] + sx * 0.02, g0[1], g0[2]), (sx * 2.4, 1.2, 1.6), (sx * 2.44, 1.05, 1.05), (sx * 2.42, 0.95, HC + 0.12),
            (sx * 2.3, 0.92, HC + 0.25)], ("c_black", "c_red", "c_yellow", "c_blue"), r=0.012,
           sag=[0.12, 0.06, 0.02, 0.0], ties=0.16, glands=(True, False))
    hose([(g0[0] + sx * 0.02, g0[1] + 0.12, g0[2] - 0.1), (sx * 2.43, 1.32, 1.4), (sx * 2.45, 1.2, 0.85),
          (sx * 2.35, 1.12, HC + 0.3)], 0.026, "hose", sag=[0.15, 0.05, 0.02], rib=0.24, ends=(True, False))
for (sx, sy), (top_, foot_) in LEGS.items():
    u_ = (foot_ - top_).normalized()
    side = u_.cross(Vector((0, 0, 1))).normalized() * (0.1 * sx * sy)
    lift = Vector((0, 0, 0.17))
    a_ = top_ + side + lift + u_ * 0.05
    b_ = foot_ + side + lift - u_ * 0.12
    bundle([tuple(a_), tuple(a_.lerp(b_, 0.5)), tuple(b_), tuple(b_ + Vector((0, 0, -0.1)) + u_ * 0.05)],
           ("c_black", "c_yellow") if sy > 0 else ("c_red", "c_black", "c_blue"), r=0.011, sag=0.0, ties=0.12,
           glands=(False, False))
    for t in (0.3, 0.7):
        q = a_.lerp(b_, t)
        box(tuple(q - lift * 0.4), (0.05, 0.05, 0.05), "steel", rot=(0, 0, math.atan2(u_.y, u_.x)), bevel=0.004)

# --- oil, where the hydraulics leak: on the roof round the manifold, on the wing, on the
# deck at the rams
stain(MF[0] + 0.0, MF[1] - 0.13, 0.12, 0.06, n=5, z=RT)
stain(-1.72, -1.6, 0.1, 0.07, n=4, z=WING_TOP + 0.03)
stain(-1.66, -1.02, 0.09, 0.07, n=5)
stain(-0.72, -1.55, 0.04, 0.06, n=3)
stain(1.66, -1.02, 0.06, 0.06, n=3)
stain(1.82, -1.72, 0.07, 0.05, n=3, z=WING_TOP + 0.03)

# ---------------------------------------------------------------- 6. the chute (turns)

# At ground level in its bay's slot, as vanilla's lies, the slot's width and level with
# the apron, so it covers the shut hatch on the screen. Built facing north, in the north
# bay; the turntable takes it to the bay the ore leaves by. A closed hood over the tail
# sprocket at the riser, the chain's open run, and a head housing across the mouth with
# the head shaft and the drive's gearbox in it. Drawn empty.
CY0, CY1 = Y_STEP + 0.01, E            # the riser to the mouth: 0.855, about vanilla's chute's length
CL = CY1 - CY0
CW = 0.77                              # the bed's width, between the cheeks
CX = 0.415                             # the cheeks' outer faces: 0.015 clear of the bay's
CH = 0.198                             # the cheeks' and housings' tops: level with the apron (AP 0.2)
BED0, BED1 = 0.07, 0.11                # the bed's top at the back and at the mouth: rising to the lip
CHUTE = empty("chute", parent=ROOT)
FLIGHTS = empty("flights", parent=CHUTE)


def bed_z(y):
    return BED0 + (BED1 - BED0) * (y - CY0) / (CY1 - CY0)


SLOPE = math.atan2(BED1 - BED0, CY1 - CY0)
for sx in (-1, 1):                     # the cheeks, on the bay's floor, riveted
    box((sx * (CX - 0.015), (CY0 + CY1) / 2, (0.03 + CH) / 2), (0.03, CL, CH - 0.03), "chute", "chute",
        parent=CHUTE, bevel=0.005)
    for k in range(7):
        rivet((sx * (CX - 0.015), CY0 + 0.06 + (CL - 0.12) * k / 6, CH + 0.002), 0.01, group="chute", parent=CHUTE)
box((0, (CY0 + CY1) / 2, (BED0 + BED1) / 2 - 0.02), (CW, math.hypot(CL, BED1 - BED0), 0.04), "chute", "chute",
    rot=(SLOPE, 0, 0), parent=CHUTE, bevel=0.004)                                    # the bed
box((0, (CY0 + CY1) / 2, 0.04), (CW, CL, 0.02), "chute", "chute", parent=CHUTE, bevel=0.0)  # its base, on the floor
for sx in (-1, 1):                     # the chain's two strands, worn bright, under the flights
    box((sx * 0.25, (CY0 + CY1) / 2, bed_z((CY0 + CY1) / 2) + 0.006), (0.03, CL - 0.05, 0.012), "flight", "chute",
        rot=(SLOPE, 0, 0), parent=CHUTE, bevel=0.0)
HOOD = 0.17                            # the tail hood, against the riser
box((0, CY0 + HOOD / 2, (0.03 + CH) / 2), (2 * CX, HOOD, CH - 0.03), "chute", "chute", parent=CHUTE, bevel=0.01)
for sx in (-1, 0, 1):
    bolt((sx * 0.3, CY0 + HOOD / 2, CH + 0.004), 0.016, 0.012, group="chute", parent=CHUTE)
HEAD = 0.13                            # the head housing, across the mouth
box((0, CY1 - HEAD / 2, (0.03 + CH) / 2 + 0.03), (2 * CX, HEAD, CH - 0.09), "chute", "chute", parent=CHUTE,
    bevel=0.01)
cyl((0, CY1 - HEAD / 2, 0.11), 0.03, 2 * CX + 0.0, "steel", "chute", verts=16, rot=(0, math.pi / 2, 0),
    parent=CHUTE, bevel=0.0)          # the head shaft's ends, in the housing's cheeks
for sx in (-1, 1):
    cyl((sx * (CX - 0.005), CY1 - HEAD / 2, 0.11), 0.045, 0.012, "brass", "chute", verts=16,
        rot=(0, math.pi / 2, 0), parent=CHUTE, bevel=0.0)          # its bearing caps
box((-CX + 0.1, CY1 - HEAD - 0.06, (0.03 + CH) / 2), (0.16, 0.12, CH - 0.03), "copper", "chute", parent=CHUTE,
    bevel=0.01)                       # the drive's gearbox, west, behind the head housing
# the chain's flights, on the open run between the hood and the head housing
FLIGHT_OBJS = []
for k in range(int(CL / PITCH) + 2):
    o = box((0, 0, 0), (CW - 0.06, 0.035, 0.035), "flight", "chute", parent=FLIGHTS, bevel=0.004)
    FLIGHT_OBJS.append(o)


def chain(f):
    """Lay the flights for frame f: every flight a pitch apart, the set moved PITCH/5 a
    frame toward the mouth, so frame 5 is frame 0. Only those on the open run show."""
    s0 = PITCH * (f % CHAIN_FRAMES) / CHAIN_FRAMES
    lo, hi = CY0 + HOOD + 0.02, CY1 - HEAD - 0.13
    for k, o in enumerate(FLIGHT_OBJS):
        y = CY0 + s0 + k * PITCH
        o.hide_render = not (lo <= y <= hi)
        o.location = (0, y, bed_z(y) + 0.0175)
        o.rotation_euler = (SLOPE, 0, 0)


# Per direction, the chute is moved across its face (in its own frame, + is east as
# modelled) to land its crop on vanilla's big-mining-drill-{N,E,S,W}-output shift: by
# the 0.015 its slot has to spare, toward vanilla's offsets. North is hidden by the press.
NUDGE = {"north": 0.0, "east": -0.015, "south": -0.015, "west": 0.015}

# ---------------------------------------------------------------- 6b. the ore (turns)
#
# The amendment's particles: ore spilling off the chute's head and falling just past the
# mouth, where vector_to_place_result puts it, as chunks of neutral pale grey (the engine
# tints them the ore being mined) on 24-frame paths. Each chunk lives ORE_LIFE frames on
# a ballistic arc from the head's lip; its phase is a whole frame, so frame 24 is frame 0.
ORE = empty("ore", parent=CHUTE)
ORE_LIFE = 7                          # (round 4, FFF #350: work that reads as force -- more ore, thrown harder)
_rng = random.Random(1709)
ORE_CHUNKS = []
for k in range(44):
    r = _rng.uniform(0.016, 0.032)
    o = sphere((0, 0, 0), r, "ore", "ore", parent=ORE, squash=_rng.uniform(0.6, 0.9), seg=8)
    o.rotation_euler = (_rng.uniform(0, 3), _rng.uniform(0, 3), _rng.uniform(0, 3))
    ORE_CHUNKS.append(dict(obj=o, x=_rng.uniform(-0.28, 0.28), v=_rng.uniform(0.5, 0.85),
                           up=_rng.uniform(0.0, 0.06), phase=_rng.randrange(ORE_FRAMES), r=r))


def ore(f):
    """Lay the chunks for frame f."""
    for c in ORE_CHUNKS:
        t = ((f + c["phase"]) % ORE_FRAMES) / ORE_LIFE
        o = c["obj"]
        o.hide_render = t >= 1.0
        if t < 1.0:
            z0 = BED1 + 0.03
            o.location = (c["x"] + 0.03 * t, E - 0.03 + c["v"] * t * 0.7, z0 + c["up"] * t - (z0 + c["up"] - c["r"]) * t * t)


# ---------------------------------------------------------------- 7. the pipe pictures (--ports)
#
# Assembler 3's picture for each face (template rule 6), rendered in this building's iron:
# a backplate traced from its pixels (alpha over 127), laid where the engine draws each
# one, and on it a stub on the vanilla pipe's centreline, its flange the size of the
# pipe's bolted end ring, kept inside the traced outline so the sheet matches assembler
# 3's outline (criterion 4). The covers the prototype uses are vanilla's (the task); the
# cover-<face> renders here are the same fitting with a blind cap, for the shared packer.
VANILLA = os.path.join(os.environ.get("FACTORIO_DATA", os.path.expanduser(
    "~/.steam/steam/steamapps/common/Factorio/data")), "base/graphics/entity/assembling-machine-3")
H_AXIS_V = 1.0 / 64          # horizontal pipe: axis, screen tiles above its tile's centre
V_AXIS_U = 0.5 / 64          # vertical pipe: axis, screen tiles right of its tile's centre
H_RING_R = 26 / 64 / 1.118
V_RING_R = 25.5 / 64
ZA = 0.42                    # the stubs' axis height


def vanilla_mask(face, tile):
    """Assembler 3's picture for `face`: its drawn pixels (i, j), and the screen px of
    its top-left from the origin, drawn from the tile the port at `tile` points into."""
    stem = os.path.join(VANILLA, f"assembling-machine-3-pipe-{face}")
    bx, by = (float(v) for v in re.search(r"by_pixel\(\s*([-\d.]+),\s*([-\d.]+)\)",
                                           open(stem + ".lua").read()).groups())
    img = bpy.data.images.load(stem + ".png", check_existing=True)
    w, h = img.size
    px = list(img.pixels)
    drawn = {(i, j) for j in range(h) for i in range(w) if px[((h - 1 - j) * w + i) * 4 + 3] > 127 / 255}
    # Closed (dilated, then eroded, by a pixel): assembler 3's west picture has a strip cut
    # off from its body by a gap a pixel or two wide, and pack_ports.py keeps only what is
    # connected to a fitting. Closing bridges such gaps and adds nothing else, so the
    # outline stays within a pixel of assembler 3's.
    n8 = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
    grown = {(i + a, j + b) for i, j in drawn for a, b in n8}
    drawn = {(i, j) for i, j in grown if all((i + a, j + b) in grown for a, b in n8)} | drawn
    dx, dy = contract.FACES[face]
    tx, ty = tile[0] + dx, tile[1] + dy
    return drawn, (tx + bx / 32) * 64 - w / 2, (ty + by / 32) * 64 - h / 2


def slab(face, tile, lift, group):
    drawn, x0, y0 = vanilla_mask(face, tile)

    def build(bm):
        corners = {}

        def corner(i, j):
            if (i, j) not in corners:
                corners[(i, j)] = bm.verts.new(lift((x0 + i) / 64, -(y0 + j) / 64))
            return corners[(i, j)]
        for i, j in drawn:
            bm.faces.new((corner(i, j + 1), corner(i + 1, j + 1), corner(i + 1, j), corner(i, j)))
    return mesh_object(f"slab-{face}", build, "slab", group, bevel=0)


def fitting(p, cap):
    """One port's picture: the backplate, and inside its outline a flanged stub out to
    where the vanilla pipe's end ring lands, open (the port) or capped (the cover)."""
    face, tile = p["face"], p["tile"]
    g = f"{'cover' if cap else 'port'}-{face}"
    cx, cy = tile[0], -tile[1]                        # the tile's centre, model coordinates (y north)
    if face == "S":
        yw = -(E + 0.035)

        def lift(u, v):                               # the wall's plane; above it, back over the top
            z = 2 * (v - yw)
            return Vector((u, yw, z)) if z <= HC else Vector((u, yw + (v - yw - HC / 2), HC + 0.004))
        slab(face, tile, lift, g)
        ax = (math.pi / 2, 0, 0)
        x = cx + V_AXIS_U
        ye = -2.53 - ZA / 2                           # the end ring widest 0.47 above the outside tile's centre
        cyl((x, (yw + ye) / 2, ZA), 0.28, abs(ye - yw), "steel", g, verts=48, rot=ax, bevel=0.0)
        cyl((x, ye + 0.03, ZA), V_RING_R - 0.02, 0.06, "steel", g, verts=48, rot=ax, bevel=0.01)
        for k in range(8):
            t = 2 * math.pi * (k + 0.5) / 8
            bolt((x + 0.33 * math.cos(t), ye - 0.002, ZA + 0.33 * math.sin(t)), 0.018, 0.012, group=g, rot=ax)
        cyl((x, ye - 0.003, ZA), 0.2 if not cap else V_RING_R - 0.06, 0.006, "dark" if not cap else "steel", g,
            verts=32, rot=ax, bevel=0.0)
    elif face == "N":
        yw = E + 0.035

        def lift(u, v):                               # behind the building, on its north wall's plane
            return Vector((u, yw, 2 * (v - yw)))
        slab(face, tile, lift, g)
        for k in range(4):                            # the flange's bolts, inside its outline
            bolt((cx + V_AXIS_U - 0.18 + 0.12 * k, yw + 0.02, 2 * (2.5 + 0.2 - yw)), 0.016, 0.012, group=g,
                 rot=(math.pi / 2, 0, 0))
    else:
        sgn = 1 if face == "E" else -1
        xw = sgn * (E + 0.035)

        def lift(u, v):
            # edge-on to the camera, so laid on a plane leaning out from the wall, as VF's
            z = ZA - sgn * 1.6 * (u - xw)
            return Vector((u, v - z / 2, z))
        slab(face, tile, lift, g)
        ya = cy + H_AXIS_V - ZA / 2                   # the axis lands on the pipe's, on the screen
        ax = (0, math.pi / 2, 0)
        xf = sgn * (2.5 - 0.03)
        cyl((xf, ya, ZA), H_RING_R - 0.02, 0.04, "steel", g, verts=48, rot=ax, bevel=0.006)
        for k in range(8):
            t = 2 * math.pi * (k + 0.5) / 8
            bolt((xf - sgn * 0.025, ya + 0.27 * math.cos(t), ZA + 0.27 * math.sin(t)), 0.016, 0.01, group=g, rot=ax)


# ---------------------------------------------------------------- 8. weight at the landing
#
# Round 6 (the task's amendment of 2026-10-10; spec 3.2, agreed by Liam the same day): the
# ring rises slowly and drops hard, and the landing jolts through the frame and throws dust.
#   - the stroke: W_DROP (section 0), the packed stroke's path;
#   - the jolt: what stands on the chassis above the deck -- the gear-houses, the winches,
#     the roofs' fittings and cables, the slung hose -- is the "frame" group: drawn in the
#     stroke's frames, not the plate, so it can kick at the landing (W_JOLT);
#   - the slung hose swings about its clips and dies out (w_swing);
#   - the winches' gears turn with the rope: slowly as they wind the ring up, fast as it
#     falls (the drum pays out 2:1 through the shoe's sheave, so the main gear turns 60
#     degrees over the stroke and the motor's pinion 4.3 times as far, the other way);
#   - the dust: a low ring of it squeezed out from under the band as it lands, rolling out
#     over the shoulder's edge onto the deck and settling before the lift. Neutral pale grey,
#     as the ore particles, so the engine tints it by the ore (apply_tint "resource-color"),
#     drawn only while working: its own layer, "dust", 24 frames in step with the stroke's.
JOLT = empty("jolt")
DUST = empty("dust")


def _subtree(o):
    yield o
    for c in o.children:
        yield from _subtree(c)


def _centre(o):
    Binv = BODY.matrix_world.inverted()
    cs = [(Binv @ q.matrix_world @ Vector(c)) for q in _subtree(o) if q.type in ("MESH", "CURVE") for c in q.bound_box]
    return sum(cs, Vector()) / len(cs) if cs else None


def _min_z(o):
    Binv = BODY.matrix_world.inverted()
    zs = [(Binv @ q.matrix_world @ Vector(c)).z for q in _subtree(o) if q.type in ("MESH", "CURVE")
          for c in q.bound_box]
    return min(zs) if zs else None


SWING = empty("swing", (0.0, 1.37, HR + 0.09), parent=JOLT)
bpy.context.view_layer.update()
_jolted = set()
for o in [c for c in BODY.children if c not in (JOLT, DUST, RING, SWING) and c not in SLUNG]:
    z = _min_z(o)
    c = _centre(o)
    # the north press frame only: the column (fixed: criterion 3) and the south guide
    # column's cap stay in the plate
    if z is not None and z >= GUIDE_TOP - 0.1 and c.y > 0.4 and abs(c.x) > 0.5:
        mpi = o.matrix_parent_inverse.copy()
        o.parent = JOLT
        o.matrix_parent_inverse = mpi
        _jolted.update(_subtree(o))
bpy.context.view_layer.update()
for o in SLUNG:
    o.parent = SWING
    o.matrix_parent_inverse = SWING.matrix_world.inverted() @ BODY.matrix_world
    _jolted.update(_subtree(o))
PARTS["frame"] = [o for o in PARTS["body"] if o in _jolted]
PARTS["body"] = [o for o in PARTS["body"] if o not in _jolted]
if True:
    M["dust"] = bpy.data.materials.new("dust")
    M["dust"].use_nodes = True
    _t = M["dust"].node_tree
    _b = _t.nodes["Principled BSDF"]
    _b.inputs["Base Color"].default_value = rig.srgb("#C6C9CF")
    _b.inputs["Roughness"].default_value = 1.0
    _g = _G(M["dust"])
    _info = _t.nodes.new("ShaderNodeObjectInfo")
    _lw = _t.nodes.new("ShaderNodeLayerWeight")
    _lw.inputs["Blend"].default_value = 0.5
    _soft = _g.math("POWER", _g.math("SUBTRACT", 1.0, _lw.outputs["Facing"]), 2.6)
    _pos = _g.node("ShaderNodeNewGeometry").outputs["Position"]
    _wisp = _g.remap(_g.noise(_pos, 14, detail=4), 0.3, 0.7, 0.15, 1.0)
    _t.links.new(_g.math("MULTIPLY", _g.math("MULTIPLY", _soft, _wisp), _info.outputs["Alpha"], clamp=True),
                 _b.inputs["Alpha"])
    _drng = random.Random(5150)
    PUFFS = []
    for k in range(72):
        a = 2 * math.pi * (k + _drng.uniform(-0.45, 0.45)) / 72
        v = _drng.uniform(0.25, 0.6)
        h = _drng.uniform(0.0, 0.08)
        r0 = _drng.uniform(0.06, 0.1)
        blobs = []
        for j in range(4):
            o = sphere((0, 0, 0), 1.0, "dust", "dust", parent=DUST, seg=12)
            # no shadows from it: translucent puffs shadowing each other went dark grey
            # where they piled up
            o.visible_shadow = False
            blobs.append((o, (_drng.uniform(-0.6, 0.6), _drng.uniform(-0.6, 0.6), _drng.uniform(0.0, 0.5)),
                          _drng.uniform(0.6, 1.0)))
        PUFFS.append((a, v, h, r0, blobs))


def dust(f):
    """The dust t = f - LAND frames after the landing: out from the band's foot, decelerating,
    lifting a little, swelling and thinning; gone by DUST_LIFE."""
    t = (f - LAND) % FRAMES
    for a, v, h, r0, blobs in PUFFS:
        R = RB_OUT + 0.06 + v * (1 - math.exp(-t / 2.2))
        floor = ZS - (ZS - ZT) * min(1.0, max(0.0, (R - SH_OUT) / 0.15))
        z = floor + 0.03 + h * (1 - math.exp(-t / 3.0)) + 0.012 * t
        size = r0 * (0.8 + 0.2 * t)
        alpha = max(0.0, 1 - t / DUST_LIFE) ** 1.8 * 0.75 if t <= DUST_LIFE else 0.0
        for o, (ox, oy, oz), sk in blobs:
            ux, uy = math.cos(a), math.sin(a)
            o.location = (R * ux + size * (ox * ux - oy * uy), R * uy + size * (ox * uy + oy * ux), z + size * oz)
            o.scale = (size * sk * 1.2, size * sk * 1.2, size * sk * 0.5)
            o.color = (1, 1, 1, alpha)
            o.hide_render = alpha <= 0.0


def pose(f):
    """Frame f of the stroke: the ring on W_DROP, the ropes to it, the jolt, the swing, the
    gears, the dust."""
    d = drop(f)
    RING.location.z = Z_RING - d
    jz = -JOLT_Z * W_JOLT.get(f % FRAMES, 0.0)
    JOLT.location.z = jz
    SWING.rotation_euler = (w_swing(f), 0.0, 0.0)
    for g_, k_ in GEARS:
        phi = k_ * d / (2 * DRUM_R)
        g_.rotation_euler = (Matrix.Rotation(math.pi / 2, 4, "X") @ Matrix.Rotation(phi, 4, "Z")).to_euler()
    bpy.context.view_layer.update()
    for rope in ROPES:
        rope.location.z = WINCH_Z + jz
        eye_top = RING.location.z + RH / 2 + SHOE_H / 2 + 0.085
        rope.scale.z = WINCH_Z + jz - eye_top
    dust(f)
    bpy.context.view_layer.update()


# ---------------------------------------------------------------- passes

SUN = float(next((a.split("=")[1] for a in argv if a.startswith("--sun=")), 7.2))    # round 7: the rig's 6.0 -> 7.2, for p95 (147)
rig.sun(SUN)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.26   # the rig's fill, as VF and DC
GROUND = rig.ground_catcher()
GROUND.parent = BODY
BOUNCE = rig.bounce_ground()

if PORTS:
    for p in DECL["ports"]:
        fitting(p, cap=False)
        fitting(p, cap=True)

if "--blend" in argv:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "scene.blend"))
    sys.exit(0)

DOORS = tuple(f"door-{f}" for f in FACES)
OPEN = {"north": "N", "east": "E", "south": "S", "west": "W"}     # the bay each direction's chute is in
PAINTED = ("under",)                  # what the stroke's frames paint besides the ring


def setup(visible=(), catchers=(), holdouts=(), ground=False):
    """Per pass: which groups the camera sees, catch shadow on, or cut out."""
    for g, objs in PARTS.items():
        for o in objs:
            shown = g in visible or g in catchers or g in holdouts
            if (g == "chute" and o in FLIGHT_OBJS) or (g == "ore" and shown):
                if not shown:
                    o.hide_render = True
                # else chain() and ore() decide which show
            else:
                o.hide_render = not shown
            o.is_shadow_catcher = g in catchers
            o.is_holdout = g in holdouts
            o.visible_camera = True
    for o in PARTS.get("dust", []):           # dust(): a puff with nothing left of it is not drawn
        if not o.hide_render and o.color[3] <= 0.0:
            o.hide_render = True
    GROUND.hide_render = not ground
    BOUNCE.hide_render = ground


def lamp_cut(on):
    b = M["lens"].node_tree.nodes["Principled BSDF"]
    b.inputs["Emission Strength"].default_value = 1.0 if on else 0.0
    b.inputs["Base Color"].default_value = (1, 1, 1, 1) if on else rig.srgb("#E6E4DE")


STATIC = ("body", "lens", "under")
HELD = STATIC + ("frame",)            # everything that stands, for holding a layer out


def empty_frame(path):
    """A frame with nothing in it, at the render's size: the dust's frames between landings."""
    w = sc.render.resolution_x * sc.render.resolution_percentage // 100
    h = sc.render.resolution_y * sc.render.resolution_percentage // 100
    img = bpy.data.images.new("empty", w, h, alpha=True)
    img.pixels.foreach_set([0.0] * (w * h * 4))
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)

if PORTS:
    contract.declare(OUT_DIR, canvas=PORT_CANVAS, **DECL)
    rig.camera(*PORT_CANVAS)
    for f in FACES:
        setup(visible=(f"port-{f}",))
        rig.render(f"{OUT_DIR}/port-{f}.png")
        setup(visible=(f"cover-{f}",))
        rig.render(f"{OUT_DIR}/cover-{f}.png")
    sys.exit(0)

if ICON:
    sc.cycles.samples = 128
    pose(0)
    # the whole machine, ring raised, every bay shut, with margin: 5.9 tiles across,
    # centred on the drawn machine (its top 2.85 above the origin, its foot 2.5 below)
    k = 1024 / 5.9
    rig.camera(1024, 1024, centre_px=(512, 512 + k * 0.18), ss=1).data.ortho_scale = 5.9
    setup(visible=STATIC + DOORS + ("ring", "frame"))
    rig.render(f"{OUT_DIR}/icon.png")
    sys.exit(0)

contract.declare(OUT_DIR, canvas=CANVAS, **DECL)
rig.camera(*CANVAS)
with open(os.path.join(OUT_DIR, "stroke.json"), "w") as _f:
    json.dump(dict(frames=FRAMES, travel=TRAVEL, drop=[drop(f) for f in range(FRAMES)], chain_frames=CHAIN_FRAMES,
                   pitch=PITCH, ore_frames=ORE_FRAMES, nudge=NUDGE,
                   chute=dict(length=CL, inner=CY0, mouth=CY1, width=CW), stroke_paints=list(PAINTED),
                   px_per_tile=rig.PX_PER_TILE, cos_elevation=math.cos(rig.ELEVATION)), _f, indent=1)


def border(x0, x1, y0, y1):
    """Render only the window x0..x1 right, y0..y1 down (tiles from the origin, on the screen)."""
    W, H = CANVAS
    sc.render.use_border = True
    sc.render.use_crop_to_border = False
    sc.render.border_min_x = max(0.0, (W / 2 + x0 * 64) / W)
    sc.render.border_max_x = min(1.0, (W / 2 + x1 * 64) / W)
    sc.render.border_min_y = max(0.0, 1 - (H / 2 + y1 * 64) / H)
    sc.render.border_max_y = min(1.0, 1 - (H / 2 + y0 * 64) / H)


WINDOWS = {"north": (-0.75, 0.75, -3.15, -1.2), "east": (1.5, 3.15, -1.0, 0.75),
           "south": (-0.75, 0.85, 1.05, 3.1), "west": (-3.15, -1.35, -1.0, 0.75)}


def chute_window(d):
    """The chute's own window in direction d, with room for the ore falling past its mouth."""
    border(*WINDOWS[d])


def door_alone(d, shut):
    """Diagnostic, not packed: this direction's shut door alone, everything in front of it
    held out, in the chute's window: the pixels the chute layer has to cover."""
    chute_window(d)
    setup(visible=(f"door-{OPEN[d]}",), holdouts=HELD + shut + ("ring",))
    rig.render(f"{OUT_DIR}/{contract.named('door', d)}.png")
    sc.render.use_border = False


CHUTE_NAME, STROKE_NAME, ORE_NAME, DUST_NAME = (a["name"] for a in DECL["animations"])
if CHUTES or DOOR_ONLY:
    for d in contract.each_direction(ROOT, DECL["directions"]):
        CHUTE.location.x = NUDGE[d]
        pose(0)
        chain(0)
        shut = tuple(g for g in DOORS if g != f"door-{OPEN[d]}")
        if DOOR_ONLY:
            door_alone(d, shut)
            continue
        chute_window(d)
        setup(visible=("chute",), holdouts=HELD + shut)
        rig.render(f"{OUT_DIR}/{contract.frame(CHUTE_NAME, 0, d)}.png")
        ore(0)
        setup(visible=("ore",), holdouts=HELD + shut + ("chute", "ring"))
        rig.render(f"{OUT_DIR}/{contract.frame(ORE_NAME, 0, d)}.png")
    sys.exit(0)

if DUST_ONLY:
    sc.cycles.samples = ANIM_SAMPLES
    for d in contract.each_direction(ROOT, DECL["directions"]):
        CHUTE.location.x = NUDGE[d]
        chain(0)
        shut = tuple(g for g in DOORS if g != f"door-{OPEN[d]}")
        for f in range(FRAMES):
            pose(f)
            out_ = f"{OUT_DIR}/{contract.frame(DUST_NAME, f, d)}.png"
            if all(o.color[3] <= 0.0 for o in PARTS["dust"]):
                empty_frame(out_)
                continue
            setup(visible=("dust",), holdouts=HELD + shut + ("ring", "chute"))
            rig.render(out_)
    sys.exit(0)

tracked = False
for d in contract.each_direction(ROOT, DECL["directions"]):
    def path(stem, d=d):
        return f"{OUT_DIR}/{contract.named(stem, d)}.png"
    sc.render.use_border = False
    CHUTE.location.x = NUDGE[d]
    pose(0)
    chain(0)
    shut = tuple(g for g in DOORS if g != f"door-{OPEN[d]}")     # this direction's bay is open

    # the plate: the same in every direction, every bay shut
    sc.cycles.samples = PLATE_SAMPLES
    setup(visible=STATIC + DOORS)
    rig.render(path("idle"))
    setup(visible=STATIC + shut + ("ring", "frame", "chute"))
    rig.render(path("still"))
    if IDLE:
        pose(LAND + 2)                # the quick loop's look at the landing: seated, the dust out
        ore(0)
        setup(visible=STATIC + shut + ("ring", "frame", "chute", "ore", "dust"))
        rig.render(f"{OUT_DIR}/top.png")
        break
    if not F0:
        setup(visible=STATIC + shut + ("ring", "frame", "chute"), ground=True)
        for o in [o for objs in PARTS.values() for o in objs]:
            o.visible_camera = False
        rig.render(path("shadow"))

        setup(visible=("lens",), holdouts=("body", "under", "ring", "frame", "chute") + DOORS)
        lamp_cut(True)
        rig.render(path("lamp"))
        lamp_cut(False)

    sc.cycles.samples = ANIM_SAMPLES
    # the chute: its frames, this direction's door gone (dropped under its bed), the body
    # and the other bays' doors held out (at the bottom of its bay a catcher records the
    # sky the chute hides on the bay's walls, which moved its crop); only its window
    chute_window(d)
    for f in range(1 if F0 else CHAIN_FRAMES + 1):   # the sixth is the loop check: it must equal frame 0
        chain(f)
        setup(visible=("chute",), holdouts=HELD + shut)
        name = contract.frame(CHUTE_NAME, f) if f < CHAIN_FRAMES else f"{CHUTE_NAME}-loop"
        rig.render(path(name))
    chain(0)
    # the ore: 24 frames and a loop check, in front of nothing but air, held out by the
    # body, the chute and the ring
    if not F0:
        for f in range(ORE_FRAMES + 1):
            ore(f)
            setup(visible=("ore",), holdouts=HELD + shut + ("chute", "ring"))
            name = contract.frame(ORE_NAME, f) if f < ORE_FRAMES else f"{ORE_NAME}-loop"
            rig.render(path(name))
    sc.render.use_border = False
    if not F0:
        door_alone(d, shut)

    # the stroke: the ring, hub, spokes, shoes and ropes, and the surfaces under the ring
    # lit for real; and (round 6) the frame, which jolts at the landing; the body, the shut
    # doors and this direction's chute catch their shadows and hide what they stand in
    # front of
    border(-2.6, 3.4, -3.3, 1.9)
    for f in range(1 if F0 else FRAMES):
        pose(f)
        setup(visible=("ring", "frame") + PAINTED,
              catchers=tuple(g for g in STATIC if g not in PAINTED) + shut + ("chute",))
        rig.render(path(contract.frame(STROKE_NAME, f)))
    sc.render.use_border = False
    # the dust (round 6): its 24 frames in step with the stroke's, alone, held out by
    # everything that stands in front of it; empty between the landings
    if not F0:
        for f in range(FRAMES):
            pose(f)
            if all(o.color[3] <= 0.0 for o in PARTS["dust"]):
                empty_frame(path(contract.frame(DUST_NAME, f)))
                continue
            setup(visible=("dust",), holdouts=HELD + shut + ("ring", "chute"))
            rig.render(path(contract.frame(DUST_NAME, f)))
        pose(0)
    if F0:
        break
    # the tracked part: the ring assembly alone, for pack.py's slide check. It does not
    # turn, so it is rendered once and copied to every direction's name. The ropes are
    # left out: they stretch, they do not slide
    for f in range(FRAMES):
        src = f"{OUT_DIR}/{contract.track_frame(STROKE_NAME, 'ring', f, 'north')}.png"
        if not tracked:
            pose(f)
            setup(visible=("ring",))
            for rope in ROPES:
                rope.hide_render = True
            rig.render(src)
        if d != "north":
            shutil.copy(src, path(contract.track_frame(STROKE_NAME, "ring", f, "")))
    tracked = True
    pose(0)
