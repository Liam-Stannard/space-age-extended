"""Crust tap (sae-crust-tap), built from its spec, rendered in every pass and direction.

  blender -b --python crust_tap.py -- <out-dir> [--idle | --icon | --check | --collide]
  tools/blender/render.sh concept/crust-tap/model/crust_tap.py <out-dir> --icon

  --idle   idle- and still-<direction>.png only, all four: the quick loop (SAMPLES=<n> in the
           environment renders at fewer samples while iterating; the full run keeps the rig's;
           POSES=6,12 renders those frames of the stroke as pose-NN-north.png, north only)
  passes: idle (the plate), still (the plate with every moving part at frame 0), shadow;
          animations (10.): pump (the flywheel, rod, piston and gauge needle, FRAMES frames, a
          slide held to the piston's curve, the piston alone rendered as pump-piston-NN) and
          sight-glass (the glass's contents, white, the engine tints them: a light layer,
          moving in place); not packed: diag-mouth-, diag-riser-, diag-glass-<direction> and
          diag-bare, for measure.py; pump.json, for measure_animation.py
  --icon   icon.png: the tap turned three-quarter, its south riser and mouth toward the viewer
  --check  no render: every direction's riser tested against everything fixed for
           intersections (evaluated meshes, world space); prints "CHECK ..." and each clash
  --collide no render: every moving part in every frame against everything fixed; prints
           "COLLIDE ..." and each clash (the hub on its shaft is meant)

The pumping animation (the gas-pump-animation task, Liam 2026-10-10: a crank and flywheel on
the compressor housing's roof driving a connecting rod, the gauge's needle kicking on each
stroke, the gas moving in the sight glass): section 10. Round 13 is otherwise unchanged; its
gauge needle now stands on a pivot so it can kick, at rest where round 13 drew it.

The design began as the adopted Bolted Collar (concept/crust-tap/adopted/A-sheet.png,
graphics/entity/crust-tap/base-{north,east,south,west}.png); spec 3.2 the parts,
3.3 the palette, 24 the connection. The task: .claude/tasks/crust-tap-model.md, with
its 2026-10-02 amendment: no frost and no heat seam, so the plate is the whole tap
in every state -- a bare riser and a dark ground joint.

Round 13 (the task's "round 13, signed off in advance" amendment): brightness stepped back
toward p50 85 -- exposure -0.23 and world fill 0.28 (round 12: -0.12 and 0.30; the rig: -0.3 and
0.26); the plinth's west strip broken up -- its pale dust a third as strong and patchy, oil-dark
blots and rust run along it, two oil stains. Nothing else changes.

Round 12 (Liam, on round 11; the task's "round 12 after the bulkier pipes" amendment, and "a
bit brighter overall", which overrides the p50 75-78 target for this building): the main line
16 px (D1 r 0.125, the header 0.12 -- the header on 0.30 at 0.97, the compressor housing's west
face in to 0.33 for D1's north run), the glass 18 px in 23 px flanges, E1 11, the bypass 7, the
relief 6; D1 and the header painted in the casing's green (vanilla paints its chemical plant's
process pipes in its livery), the lid's greens a step lighter, a red-oxide primer showing where
the paint chips, weathering streaks down the walls and over the lid, the plinth scuffed and
grimed; the sight glass bluer in a bright worn frame, its front tie-rods gone so no bars cross
it (it read like the louvres); hose 1 now E1's flexible end, from the east face onto the
housing's roof (it crossed the north riser's neck); the pressure switch and cable 1 gone, the
transmitter on the glass's west flange; exposure -0.12 (the rig's -0.3) and the world fill 0.30
(0.26) for this model, lifting the shadow side.

Round 11 (Liam, after signing off round 10: "the pipes and hoses on the gas pump need to be
bulkier - see the factorio sprites"; the task's 2026-10-10 amendment): every pipe, hose and the
sight glass's header measured against vanilla's sprites at the same 64 px a tile and thickened
to their proportions (8.): the main line 12 px across (was 3-4), the sight glass 15 px in 20 px
flanges (was 7 in 10), small bore 5-10 px (was 2-3), the riser 10 px (was 8; its stands' foot
flanges, r 0.098 between the anchors' blocks and the casing, cap it), hoses 13, 7 and 7 px with
cuffs as long as they are fat and corrugations 3 px apart (was 4, 3.6 and 2.8 px, ribs 1 px
apart). Flanges are heavy: 2-4 px proud, a pair 3 px deep, bolted proud. Fewer, fatter runs: the
doubled pair, M3 and W1 are gone; D1 is the one main, off its own bolted foot on the plinth,
carrying the bypass loop, the drain cock and the pressure switch, east south of the wellhead
and north beside the compressor housing into the header's east end; the header lies on 0.28
at 0.95 (was 0.20 at 0.875) for the glass's flanges to clear the wellhead, and turns up at its
west end into the vent stack; the relief line leaves a tee in the burst disc's nozzle; hose 2
lands on D1's north run; cable 3 runs between the south cover and the lid band. The square
casing, the compressor housing, the finish and the four mouths are unchanged.

Round 10 (Liam, signing off round 9: "gas pump more bulky"): the casing grown east to 0.68
(from 0.53) -- its west, south and north faces stay where the west run, the front mains with
the east stand, and the north stand hold them -- with a 0.34 north-east cut (its line x + y =
0.84 keeps the north riser's handwheel clear) and 0.20 on the other three, so the plan is
uneven; outline() takes the four faces and four cuts. A compressor housing stands on the lid's
east plate beside the wellhead (x 0.30..0.60, y -0.40..0.08, its walls leaning in 0.035, roof at
1.06): louvres and a brass motor plate in its south face, its foot and roof bolted, a breather
and a lifting eye on its roof -- a stepped top, mass up off the ground. E1 now rises straight
from its pad at the grown east face's foot into the housing's east face; cable 3 feeds the
housing's motor (the instrument box is gone); the relief line, hose 1's pad, hose 3's pot and
the south-east lifting lug moved out with the face. Drawn height: nothing but the north mouth
draws above the footprint's north edge (the vent stack's cap reaches screen y 0.9), within a
small vanilla machine. Tone: the plinth's dust-caked east paler, a drift of grit and a
dust-caked flat bar on the plate's east margin, now in the bigger mass's shadow.

Round 9 (Liam, on round 8: "the gas pump's liquid view hole should be clearer, it currently looks
like a status indicator lamp"): the sight glass moved inline into the lid header, between M3's
tee and D1's -- a glass tube 0.33 long and 0.058 in radius in the header's own axis, between two
heavy bolted flanges with gaskets, four tie-rods across it (two in front of the contents), a
pale glint along its top edge; dark empty glass in the plate. Its contents are a part-filled
mesh (the level 0.6 of the radius under the axis, so from this camera about two thirds of the
window is fluid and the top is dark empty glass) rendered as plain neutral values, mean about
180, 255 at the level line: the flat surface lighter than the body, the bright meniscus along
the surface's back edge (on screen the top of the fluid, right under the empty glass), a
darker band low down, bubbles, a slow drift along its length; drawn in game as tinted paint,
not glow. To make room: the gauge moved onto D1's lid run, the transmitter taps off the glass's
east flange (cable 2 rerouted north of the header), hose 2 lands on a new tee on M3's lid run
(its arch no longer crosses the glass), and the vent stack rises straight out of W1's elbow at
the lid's west edge. The old standing gauge column and its pipes to the south face are gone.

Round 8 (Liam, beside vanilla: "we need to add more wiring and hoses and things ... these look
too well machined"; and FFF #350 and #146): a loose, slightly messy layer over the machined
parts, as vanilla's pumpjack, chemical plant, big mining drill and electromagnetic plant carry
it (section 9) -- three corrugated rubber hoses with crimped ends (the header's east end over
the lid's north-east corner down to a valve pad; the wellhead's flexible connection, which
replaces its rigid nozzle and its hex plug; one slack across the east plinth to a drain pot);
a junction box with cable glands on a skewed welded bracket on the lid; cables in muted
colours from it -- an olive one looped over the lid's south edge into a pressure switch
clamped to M3, a zip-tied black and red pair on clip saddles to a gauge transmitter on the
header, a grey one under the mains and looped over the east edge into an instrument box on
a welded retrofit bracket. Less machined: the three lid plates a hair off true, the east one a
later replacement in a greyer primer standing proud, the west one worn hardest; D2 jogs out
where a length was replaced (flanged on the repair); a bolted patch on the lid; oil stains
under the valves and pads. The gas band and its codes moved off the shaded south face to
the lid's south and north margins (worn through in patches). A vent stack with a rain cap
off the header's north side breaks the casing's top edge (FFF #350: no plain box), the
north-west lifting lug moved to make room for its stay. --check now also tests every part of
the new layer against everything fixed but its own assembly; what it reports is contact
that is meant (a nipple in its pipe, a cable in its gland, a bracket welded on, a clip on the
lid, a stain under a pad). Tone: the plinth's dust-caked east half lifted a step, oil stains
and hose rubber kept off black.

Round 7 (Liam, on round 6: "could it be made less circular"): the body rebuilt square. The
round apron, skirt, drum, shoulder, head flange, cap and ring main are gone, and the dog
clamps with them; in their place a rectangular pump casing with its corners cut (3.), in
riveted plate walls in three courses with riveted bands, one heavy bolted plate bent over
each corner cut, a flat lid in three lapped and riveted plates with two bolted inspection
covers, and ONE round bolted boss on it, the wellhead; the apron a square plinth, its
corners notched round the anchors. The pipework orthogonal, as vanilla's chemical plant
and oil refinery carry it (8.): straight runs up the faces and across the lid, square
welded elbows, no ring mains. The signature finish kept, keyed to the faces now (its
stencils placed along each face in object space). The gauge glass, the maker's plate and
the burst disc kept; the riser and its four mouths unchanged, except that each stand now
stands on the plinth and its foot flange is r 0.098 (from 0.105) and seated rather than
sunk -- the north and south ones stood in an anchor's foot. --check found two copper
straps and the south support's base in round 6's risers (the south-west strap ran through
the south stand's lower flange; the north-east one through the north stand's): those two
straps are gone, the anchors' blocks moved out to 0.745 and the plate's flat bars out to
0.886. The mouths' flange collars cast no shadow (7.): the east one drew a hard black oval
past the footprint in the shadow sheet (a hole, Liam) and the west one a black oval on the
plate; the shadow sheet is rendered with a 14 degree sun so it is soft. Tone: the plinth's
east half and west edge dust-caked (the casing's shadow and the west mouth's), the fixed
pipework a darker steel than the riser ("line"), so the riser stays the clearest pipe; the
walls at the light end of 3.3's green, as the south face takes little sun.

Round 2 (2026-10-09): the building is now the Gas Pump (a capped wellhead pump for any
gas on the Core); the form and the four connections are unchanged, and nothing here
depends on the name.

Round 3: the signature finish (spec 3.3, Liam 2026-10-09) -- faded industrial green on the
collar and the cap, sun-faded on the tops and worn to steel on edges and bolt heads, a
stencilled gas band round the drum's middle course, one replacement plate in fresher
paint, small stencilled markings, dry orange rust on the tops and dark wet streaks down
the walls (see "the signature finish" below); the west riser routed off the apron's
south-west, in view; every mouth a flange face round the pipe's own bore; larger
handwheels with a bright worn rim; the cap's top calm.

Rounds 4 to 6 (superseded by round 7's body and pipework): round 4 put a manifold header,
a bypass, a drain, instrument tubing and the relief line round the round collar, and the
sight glass with its white `light` pass ("light-<d>", sheet "sight-glass-<d>") the engine
tints by the vent's gas; round 5 made the pipework a primary mass and the sight glass a
vertical gauge glass on its own stand, piped in top and bottom like a boiler's level glass;
round 6 carried it round the dome as a ring main, the world fill back at 0.26.

The building, as round 7 has it:
  - a base plate filling the footprint, its rim angle iron worn bright in broken stretches,
    a riveted flat bar inside the rim along each edge, bolt lugs on its edge faces, a bolted
    lug at the middle of its north and south edges, a riveted patch;
  - four ground anchors in its corners: a chamfered foot bolted down round its outer
    edges, two stepped blocks, a washer and a big hex bolt in mid steel, its top edge and
    the cap block's edges worn bright in short broken stretches;
  - the plinth over most of the plate, its corners notched round the anchors, its top edge
    chamfered and riveted, its east half and west edge dust-caked;
  - the casing (3.): plate walls in three courses, staggered, each plate beaten out a
    little, welded and riveted at its joints, two riveted bands, a bolted foot angle and a
    bolted top flange, worn bright in broken stretches; a bolted plate bent over each
    corner cut; the gas band and its stencils on the walls' middle course, a replacement
    plate in fresher paint, small stencils, wet rust down from the bands and fittings;
  - the lid: flat, three plates lapped and riveted, two inspection covers, two lifting lugs
    upright in their diagonals' planes, its edge bolted and knocked bright;
  - the wellhead: one round bolted boss on the lid, a bolted cover, a hex plug and a vent
    cock, its number stencilled on its side;
  - two copper straps, south-east and north-west, from the anchors onto lugs on the
    corner plates;
  - the brass burst disc on a flanged nozzle on the lid's east side, north of east (spec
    3.2: the north-east shoulder);
  - the pipework and the gauge glass (8.);
  - the riser, one design in all four directions: a stand rising off the plinth through a
    bolted foot, a gate valve on it with its handwheel upright, a cast elbow welded in,
    a horizontal run (a flanged joint and a support bracket where it is long), a reducer,
    and the mouth's flange collar on the footprint's edge. The pipe is the furnace's loop
    pipe in scale; only the mouth's collar is vanilla's size.

Only the riser changes with the direction (the task): everything else is one set of
objects that never moves, so the four plates agree everywhere the riser does not reach.
The turntable never turns.

Where each mouth sits is fixed by the vanilla pipe it must meet, in SCREEN terms,
because vanilla's pipe sprites are not drawn at a physical height. Measured off
base/graphics/entity/pipe (64 px to a tile, the sprite centred on its tile; measure.py
measures them again):
  - pipe-straight-horizontal: tube centre about 2 px above the tile centre, a flange
    4 px thick standing at each tile edge, 50 px tall;
  - pipe-straight-vertical: a joint ring 51 px wide and 19 px tall in the rows just past
    the tile edge it joins on (its centre 9.5 px past the edge), tube 39 px wide.
A point (x, y, z) lands on the screen at (x, y + z/2) tiles, so a run at height H draws
H/2 up the screen: every mouth sits H/2 south of where its screen position says.
Hence:
  north  connection { 0.5, -0.5 }: collar on x 0.5, its middle at y 1 + 9.5/64 - H/2
  east   connection { 0.5,  0.5 }: collar's face at x 1, its axis at y -0.5 + 2/64 - H/2
  south  connection {-0.5,  0.5 }: collar on x -0.5, its middle at y -1 + 9.5/64 - H/2
  west   connection {-0.5, -0.5 }: collar's face at x -1, its axis at y 0.5 + 2/64 - H/2
H (0.47) is the least that lets the mouth's collar clear the anchors' feet and the run
clear their bolts. The runs' lines are therefore not quarter turns of each other: north
and south run on x +-0.5 (each the other turned half round), east and west on vanilla's
tube line, 0.2 south of their tiles' centres. Each stand stands on its run's line where
the drum, the anchors and the straps leave room.

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
from materials import layered  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = argv[0]
os.makedirs(OUT_DIR, exist_ok=True)
ICON = "--icon" in argv
IDLE = "--idle" in argv


def swatch(name):
    """This building's concept swatches: swatches/bake_concept.py."""
    return os.path.join(HERE, "swatches", f"concept_{name}.png")


CANVAS = (256, 208)                 # entity origin at (128, 104); the shadow reaches east
DIRS = ("north", "east", "south", "west")
DECL = dict(
    footprint=(2, 2),
    directions="four",
    passes=[
        dict(name="idle", kind="plate", sheet="base"),
        dict(name="shadow", kind="shadow", sheet="base-shadow"),
        # the sight glass's contents, white: the engine tints them by the vent's gas
        # (apply_tint = "resource-color"), drawn while the pump works
        dict(name="light", kind="light", sheet="sight-glass"),
    ],
    animations=[],
    ports=[],                       # the riser and its mouth are the plate's own (task)
)

sc = rig.reset()
# (round 12, Liam: "a bit brighter overall", over the p50 75-78 target for this building) the
# rig's -0.3 exposure raised to -0.12 for this model only: the same contrast look, lifted
sc.view_settings.exposure = float(os.environ.get("EXPOSURE", "-0.23"))
if os.environ.get("SAMPLES"):                # iterating: fewer samples (the full run keeps the rig's)
    sc.cycles.samples = int(os.environ["SAMPLES"])
ROOT = rig.turntable(rig.stretch_root())     # never turned: only the riser changes

# ---------------------------------------------------------------- materials

WARM_RUST = ("#6A3212", "#CC7432")      # the drop crusher's warmer rust (round 2: saturation)
BOSS_TOP_Z = 0.935                        # the wellhead boss's top (3.), for its drips
CASE_HX, CASE_HY = 0.605, 0.50             # the casing's half-widths (3.), for its stencils
CASE_CX = 0.075                            # (round 10) its centre in x: the casing grew east

M = {
    # spec 3.3: the collar and anchors #3E3B36 -> #5E584E, through the adopted chips
    "collar": layered("collar", "#5E574C", metal="#D2CABC", paint_metal=0.08, paint_rough=0.62, wear=0.75,
                      rust=0.38, rust_tint=WARM_RUST, dust=0.2, grime=0.12, swatch=swatch("collar"),
                      swatch_gain=0.88, ground=0.8, ground_h=0.35, jitter=0.16,
                      drips=((0.74, 0.18), (0.53, 0.2), (0.31, 0.17)), drip=1.0),
    # the shoulder: the same plate, its up-facing curve kept darker and smoother (full sun)
    "shoulder": layered("shoulder", "#4E4A43", metal="#C4BCAE", paint_metal=0.08, paint_rough=0.6, wear=0.5,
                        rust=0.25, rust_tint=WARM_RUST, dust=0.08, grime=0.7, swatch=swatch("collar"),
                        swatch_gain=0.95, jitter=0.12),
    # the base plate: dark, as it faces the sun square on
    "plate": layered("plate", "#463C33", metal="#8E887C", paint_metal=0.1, paint_rough=0.7, wear=0.2,
                     rust=0.1, rust_tint=WARM_RUST, dust=0.15, grime=0.3, swatch=swatch("plate"),
                     swatch_gain=0.29, ground=0.5, ground_h=0.08, jitter=0.12),
    "anchor": layered("anchor", "#5E584E", metal="#C8C0B2", paint_metal=0.08, paint_rough=0.6, wear=0.85,
                      rust=0.45, rust_tint=WARM_RUST, dust=0.3, grime=0.7, swatch=swatch("anchor"),
                      swatch_gain=0.54, ground=0.8, ground_h=0.2, jitter=0.12),
    "cap": layered("cap", "#4E4A43", metal="#A49C8E", paint_metal=0.1, paint_rough=0.6, wear=0.15,
                   rust=0.15, rust_tint=WARM_RUST, dust=0.05, grime=0.7, swatch=swatch("cap"), swatch_gain=0.44,
                   jitter=0.06),
    # the riser: #8A8580, bare steel, mostly diffuse so it reads at this camera
    "riser": layered("riser", "#8A8580", metal="#D6D0C6", paint_metal=0.3, paint_rough=0.42, wear=0.45,
                     rust=0.35, rust_tint=WARM_RUST, dust=0.1, grime=0.5, swatch=swatch("riser"),
                     swatch_gain=0.92, jitter=0.08, drips=((0.6, 0.3),), drip=0.6),
    "seam": layered("seam", "#6E675E", metal="#C8C0B2", paint_metal=0.6, paint_rough=0.45,
                    wear=0.45, rust=0.5, dust=0.0, jitter=0.05, ground=0.6, ground_h=0.2),
    "steel": layered("steel", "#615B53", metal="#DCD6CA", paint_metal=0.15, paint_rough=0.4,
                     wear=0.7, rust=0.4, dust=0.1, grime=0.5, ground=0.6, ground_h=0.2),
    "rail": layered("rail", "#605A51", metal="#CCC4B6", paint_metal=0.12, paint_rough=0.45,
                    wear=0.55, rust=0.35, dust=0.15, grime=0.25, ground=0.6, ground_h=0.15),
    # angle iron, knocked back to bare metal along its edges
    "edge": layered("edge", "#3C362F", metal="#C2BBAE", paint_metal=0.2, paint_rough=0.55,
                    wear=0.5, rust=0.4, dust=0.25, grime=0.55, ground=0.6, ground_h=0.15),
    # bright worn steel, diffuse: the bolt heads' tops, the eye's bearing edge
    "polish": layered("polish", "#D6D0C4", metal="#F0EAE0", paint_metal=0.25, paint_rough=0.4, wear=0.2,
                      rust=0.08, dust=0.05, grime=0.3, jitter=0.05),
    "copper": layered("copper", "#8A5A32", metal="#E0A060", paint_metal=0.3, paint_rough=0.42,
                      wear=0.6, rust=0.1, dust=0.1, grime=0.45, swatch=swatch("copper"), swatch_gain=1.35,
                      patina=0.2),
    # spec 3.3: the burst disc #C8A23A
    "brass": layered("brass", "#C8A23A", metal="#E2C47A", paint_metal=0.35, paint_rough=0.38,
                     wear=0.4, rust=0.12, dust=0.15, grime=0.45, swatch=swatch("brass"), swatch_gain=1.05),
    # bolt heads that take the wear: the anchors', the clamps', the cap's (the plates draw them pale)
    "head": layered("head", "#C6C0B4", metal="#F0EAE0", paint_metal=0.2, paint_rough=0.4, wear=0.8,
                    rust=0.2, rust_tint=WARM_RUST, dust=0.1, grime=0.45, jitter=0.08),
    # the apron round the collar's foot: bare steel, scuffed and dusty, sloped to the sky
    "apron": layered("apron", "#40372E", metal="#9E968A", paint_metal=0.2, paint_rough=0.62, wear=0.4,
                     rust=0.15, rust_tint=WARM_RUST, dust=0.75, grime=0.3, ground=0.4, ground_h=0.1, jitter=0.08),
    "apron_e": layered("apron_e", "#5E5246", metal="#A89E90", paint_metal=0.15, paint_rough=0.7, wear=0.35,
                       rust=0.15, rust_tint=WARM_RUST, dust=0.9, grime=0.25, ground=0.4, ground_h=0.1, jitter=0.08),
    # the riser's pipe: mid-value steel, the furnace's loop pipes' finish -- broken wear, rust
    # run down from the joints
    "pipe": layered("pipe", "#6E685C", metal="#B4AC9E", paint_metal=0.1, paint_rough=0.45, wear=0.45,
                    rust=0.45, rust_tint=WARM_RUST, dust=0.15, grime=0.2, jitter=0.1,
                    drips=((0.47, 0.25), (0.37, 0.2)), drip=0.8),
    # the fixed pipework (round 7): a darker, greyer steel than the riser's, so the riser stays
    # the clearest pipe on the building
    "line": layered("line", "#6E695F", metal="#C0BAAC", paint_metal=0.1, paint_rough=0.44, wear=0.4,
                    rust=0.4, rust_tint=WARM_RUST, dust=0.15, grime=0.25, jitter=0.1,
                    drips=((0.875, 0.2), (0.45, 0.2)), drip=0.7),
    "valve": layered("valve", "#5E574C", metal="#B0A898", paint_metal=0.2, paint_rough=0.5, wear=0.6,
                     rust=0.5, rust_tint=WARM_RUST, dust=0.15, grime=0.3),
    # the handwheel, its rim polished by hands: a highlight
    "wheel": layered("wheel", "#B4AEA2", metal="#EAE4D8", paint_metal=0.25, paint_rough=0.38, wear=0.5,
                     rust=0.1, dust=0.05, grime=0.3, jitter=0.04),
    # bare steel, scuffed bright where boots and tools have rubbed the apron
    "scuff": layered("scuff", "#7E776C", metal="#BEB8AC", paint_metal=0.3, paint_rough=0.45,
                     wear=0.5, rust=0.15, dust=0.3, grime=0.4),
    # the cap's raised boss: the collar's steel; its top plate dark and smooth (a sunlit top
    # lands pale otherwise)
    "boss": layered("boss", "#5A5046", metal="#B0A898", paint_metal=0.1, paint_rough=0.55, wear=0.55,
                    rust=0.45, rust_tint=WARM_RUST, dust=0.1, grime=0.7, swatch=swatch("collar"), swatch_gain=0.6,
                    drips=((BOSS_TOP_Z, 0.08),), drip=0.8),
    # (round 3: fine grime and rust in its edges only, no blotches on the flat)
    "captop": layered("captop", "#38312B", metal="#7E766A", paint_metal=0.15, paint_rough=0.5, wear=0.12,
                      rust=0.04, rust_tint=WARM_RUST, dust=0.03, grime=0.9, jitter=0.03),
    "dial": layered("dial", "#B8AE98", paint_metal=0.0, paint_rough=0.75, wear=0.1, rust=0.05, dust=0.3,
                    grime=0.5),
    # worn steel, lighter: the mouth's flange collar and neck, whose back faces sit in hard
    # shade in one direction or another (round 6: black% without a brighter world)
    "worn": layered("worn", "#958F84", metal="#D2CCC0", paint_metal=0.08, paint_rough=0.55, wear=0.6,
                    rust=0.25, rust_tint=WARM_RUST, dust=0.15, grime=0.3, jitter=0.06),
    "patch": layered("patch", "#4C4740", metal="#9C968A", paint_metal=0.2, paint_rough=0.6,
                     wear=0.5, rust=0.35, rust_tint=WARM_RUST, dust=0.2, grime=0.9),
}


def plain(name, hexcol, rough=0.9, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(hexcol)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


M["bore"] = plain("bore", "#2A231C")            # the inside of the open mouth: dark, coloured


def glass_material():
    """The sight glass: dark, empty, glossy glass (the plate shows it so; what is in it is
    the light pass's)."""
    m = bpy.data.materials.new("glass")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb("#2C3437")
    b.inputs["Roughness"].default_value = 0.08
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat Roughness"].default_value = 0.03
    return m


FILL_K = [float(v) for v in os.environ.get("FILL_K", "0.35,0.44,0.85,0.12,0.30").split(",")]


def fill_material():
    """The sight glass's contents, for the light pass (round 9: a fluid seen through glass,
    not a lamp): a neutral grey, mid to light, its value varied the way fluid in a glass
    reads -- the flat surface lighter than the body under it, a bright meniscus line along the
    surface's front edge, a darker band low down, a few bright bubbles, a slow drift along
    its length. Never a colour: the engine tints it. (Rendered as unlit values so they are
    exact; drawn in game as ordinary tinted paint.)"""
    body, surf, menis, band, bub = FILL_K
    m = bpy.data.materials.new("fill")
    m.use_nodes = True
    t = m.node_tree
    n, ln = t.nodes, t.links
    b = n["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0, 0, 0, 1)
    b.inputs["Emission Color"].default_value = (1, 1, 1, 1)
    g = _GN(t)
    co = n.new("ShaderNodeTexCoord")
    xyz = n.new("ShaderNodeSeparateXYZ")
    ln.new(co.outputs["Object"], xyz.inputs[0])
    x, y, z = xyz.outputs["X"], xyz.outputs["Y"], xyz.outputs["Z"]
    geo = n.new("ShaderNodeNewGeometry")
    nxyz = n.new("ShaderNodeSeparateXYZ")
    ln.new(geo.outputs["Normal"], nxyz.inputs[0])
    top = g.cmp("GREATER_THAN", nxyz.outputs["Z"], 0.8)                       # the surface
    side = g.op("SUBTRACT", 1.0, top)
    yr = g.op("SUBTRACT", y, H_Y_FILL)
    zr = g.op("SUBTRACT", z, HZ_FILL)
    v = g.mul(side, body)
    v = g.op("ADD", v, g.mul(side, g.mul(g.cmp("LESS_THAN", zr, -0.8 * FILL_R_), -band)))   # darker low down
    v = g.op("ADD", v, g.mul(top, surf))
    # the meniscus where the surface meets the glass at the back -- from this camera the top of
    # the fluid, right under the empty glass: the level line
    v = g.op("ADD", v, g.mul(top, g.mul(g.cmp("GREATER_THAN", yr, 0.6 * FILL_R_), menis)))
    v = g.op("ADD", v, g.mul(top, g.mul(g.cmp("LESS_THAN", yr, -0.3 * FILL_R_), -0.06)))   # the near surface, calmer
    bubn = n.new("ShaderNodeTexNoise")
    bubn.inputs["Scale"].default_value = 220.0
    ln.new(co.outputs["Object"], bubn.inputs["Vector"])
    v = g.op("ADD", v, g.mul(side, g.mul(g.cmp("GREATER_THAN", bubn.outputs["Fac"], 0.66), bub)))
    drift = n.new("ShaderNodeTexNoise")
    drift.inputs["Scale"].default_value = 9.0
    ln.new(co.outputs["Object"], drift.inputs["Vector"])
    v = g.op("ADD", v, g.mul(g.op("SUBTRACT", drift.outputs["Fac"], 0.5), 0.12))
    ln.new(v, b.inputs["Emission Strength"])
    return m


H_Y_FILL, HZ_FILL, FILL_R_ = 0.30, 0.97, 0.13      # the header's line and axis, the contents' radius (8.)


class _GN:
    """Math nodes, briefly."""

    def __init__(self, tree):
        self.t = tree

    def op(self, kind, a, b=None):
        nd = self.t.nodes.new("ShaderNodeMath")
        nd.operation = kind
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, bpy.types.NodeSocket):
                self.t.links.new(v, nd.inputs[i])
            else:
                nd.inputs[i].default_value = v
        return nd.outputs[0]

    def cmp(self, kind, a, b):
        return self.op(kind, a, b)

    def mul(self, a, b):
        return self.op("MULTIPLY", a, b)


M["glass"] = glass_material()
M["glass"].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rig.srgb("#2E424A")  # (round 12: bluer than the louvres' dark)
M["glint"] = plain("glint", "#B8B4AA", rough=0.1)   # (round 12: warm, off the frost range, criterion 4)       # (round 9) the glass's top-edge highlight
M["fill"] = fill_material()
# (round 12) the gauge's brass a step down: at the brighter exposure its rim lit into 3.3's seam range
M["brass_g"] = layered("brass_g", "#C8A23A", metal="#E2C47A", paint_metal=0.35, paint_rough=0.42, wear=0.4, rust=0.12,
                       dust=0.15, grime=0.5, swatch=swatch("brass"), swatch_gain=0.8)

# ---------------------------------------------------------------- the signature finish
#
# Spec 3.3, signature finish (Liam, 2026-10-09): every Core building shares the dark steel
# base -- the plate, the anchors, the bands, rust, dust and dirt -- and carries one
# material of its own on its main surfaces. This one's is faded industrial green on the
# casing, its lid and the wellhead, #4A5A44 -> #5E6E56, sun-faded on what faces up and worn
# through to steel on its edges and bolt heads; a stencilled band round the casing for its
# gas, as gas plant is colour-coded; the riser and its fittings bare steel and brass.
# Variation: one replacement plate in fresher paint, small stencilled markings, and rust by
# place -- dry orange on the tops (the lid, the wellhead), dark wet streaks run down below
# the bands and fittings on the walls. All of it through materials.layered's own hooks (its `pattern`
# callable, its paint, wear and rust tint): materials.py is not changed.

GREEN = ("#4A5A44", "#5E6E56")
GREEN_FADED = "#6C765F"                 # what the sun leaves of it on the tops
GREEN_FRESH = ("#4E6446", "#60764F")    # the replacement plate: newer paint, less faded
GAS_BAND = "#BE9C4C"                    # the gas band: a faded yellow ochre (round 7: lighter, on a face in shade)
STENCIL = "#26271F"                     # stencil paint, near black
DRY_RUST = ("#7A3E16", "#D08A44")       # dry orange, on the tops
WET_RUST = ("#2A1A10", "#5A341C")       # dark wet streaks, down the walls
GAS_Z = (0.395, 0.505)                  # the gas band: the walls' middle course
K_FACE = 92.0                           # stencil units a tile along a face (the round collar's degrees, kept)
# the gas's code stencilled in the band every 45 units round the casing, a flow arrow after each
GAS_CODES = (-66.0, -21.0, 24.0)
LID_CODES = (-29.0, 20.0)               # on the lid's margin: between the mains that cross it
# small stencilled markings: (along the face, z, width, height) in tiles -- two on the south
# face's lower course; and one on the wellhead boss's side (degrees round it, z from its middle)
MARKS_WALL = ((-0.06, 0.275, 0.09, 0.04), (0.31, 0.29, 0.05, 0.035))
MARKS_BOSS = ((-95.0, 0.0, 14.0, 0.03),)


def _object_xyz(g):
    co = g.node("ShaderNodeTexCoord").outputs["Object"]
    xyz = g.node("ShaderNodeSeparateXYZ", Vector=co)
    return xyz.outputs["X"], xyz.outputs["Y"], xyz.outputs["Z"]


def _face_a_z(g):
    """Where a point is on the casing's walls, in object space (the walls are built at the
    origin): its place along its face in stencil units -- x on the south and north faces, y
    on the east and west -- and its height."""
    x, y, z = _object_xyz(g)
    ns = g.math("GREATER_THAN", g.math("MULTIPLY", g.math("ABSOLUTE", y), CASE_HX),
                g.math("MULTIPLY", g.math("ABSOLUTE", x), CASE_HY))
    s_ = g.math("ADD", g.math("MULTIPLY", ns, x), g.math("MULTIPLY", g.math("SUBTRACT", 1.0, ns), y))
    return g.math("MULTIPLY", s_, K_FACE), z


def _round_a_z(g):
    """Round a round part, in object space (it is placed at its own centre): degrees, height."""
    x, y, z = _object_xyz(g)
    return g.math("MULTIPLY", g.math("ARCTAN2", y, x), 180 / math.pi), z


def _between(g, v, lo, hi):
    return g.math("MULTIPLY", g.math("GREATER_THAN", v, lo), g.math("LESS_THAN", v, hi))


def _glyphs(g, a, z, a0, a1, z0, z1, per_deg):
    """Stencil 'lettering' between a0..a1 and heights z0..z1: rows of short blocks with gaps,
    as a stencilled code reads at this size (no real letters: it is four pixels tall)."""
    win = g.math("MULTIPLY", _between(g, a, a0, a1), _between(g, z, z0, z1))
    u = g.math("FRACT", g.math("MULTIPLY", a, per_deg))
    stroke = g.math("LESS_THAN", u, 0.62)
    # a crossbar in some cells: the glyphs are not all bars
    v = g.math("DIVIDE", g.math("SUBTRACT", z, z0), z1 - z0)
    mid = _between(g, v, 0.42, 0.6)
    cell = g.math("FRACT", g.math("MULTIPLY", a, per_deg / 3.0))
    bar = g.math("MULTIPLY", mid, g.math("LESS_THAN", cell, 0.5))
    return g.math("MULTIPLY", win, g.math("MAXIMUM", g.math("MULTIPLY", stroke, g.math("GREATER_THAN", u, 0.12)), bar))


LID_HX, LID_HY = CASE_HX + 0.025, CASE_HY + 0.025
LID_CUT = CASE_HX + CASE_HY - 0.20 + 0.05 - 0.025 * (2 - math.sqrt(2))   # the lid's corner cut: |x'| + |y| <= LID_CUT
LID_BAND = (0.034, 0.082)               # the gas band along the lid's south and north margins, in from its edge (round 8)


def _lid_margin(g):
    """Where a point is on the lid's margin, from world position (y un-stretched): its place
    along the nearest edge in stencil units, and how far in from that edge it is."""
    pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
    xyz = g.node("ShaderNodeSeparateXYZ", Vector=pos)
    x, y = g.math("SUBTRACT", xyz.outputs["X"], CASE_CX), g.math("MULTIPLY", xyz.outputs["Y"], math.sin(math.radians(60)))
    ax, ay = g.math("ABSOLUTE", x), g.math("ABSOLUTE", y)
    dx, dy = g.math("SUBTRACT", LID_HX, ax), g.math("SUBTRACT", LID_HY, ay)
    dc = g.math("MULTIPLY", g.math("SUBTRACT", LID_CUT, g.math("ADD", ax, ay)), 1 / math.sqrt(2))
    d = g.math("MINIMUM", g.math("MINIMUM", dx, dy), dc)
    ns = g.math("LESS_THAN", dy, dx)                                  # the south or north margin
    s_ = g.math("ADD", g.math("MULTIPLY", ns, x), g.math("MULTIPLY", g.math("SUBTRACT", 1.0, ns), y))
    return g.math("MULTIPLY", s_, K_FACE), d, ns


LID_BAND_COL = "#9C8246"                # the band's ochre on the lid: faded further, in full sun


PRIMER = "#7E4A36"                      # (round 12) the red-oxide primer under the green, where it chips


def green_paint(lo, hi, fade=0.0, band=False, marks=(), where="face", lidband=False, chips=0.9, streaks=False,
                streaks_k=0.16):
    """The paint as a `pattern` for materials.layered: two greens mottled, the tops faded
    toward GREEN_FADED, and -- on the walls -- the gas band and its stencils. `where` says
    how a stencil is placed: along the casing's faces, or round a round part."""
    def pattern(g):
        pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
        a, z = _face_a_z(g) if where == "face" else _round_a_z(g)
        col = g.mixc(g.remap(g.noise(pos, 3.5, detail=3), 0.35, 0.65), rig.srgb(lo), rig.srgb(hi))
        if fade:
            nz = g.node("ShaderNodeSeparateXYZ", Vector=g.node("ShaderNodeNewGeometry").outputs["Normal"]).outputs["Z"]
            sun = g.math("MULTIPLY", g.remap(nz, 0.25, 0.95), g.remap(g.noise(pos, 7, detail=4), 0.3, 0.7, 0.6, 1.0))
            col = g.mixc(g.math("MULTIPLY", sun, fade, clamp=True), col, rig.srgb(GREEN_FADED))
        worn = g.remap(g.noise(pos, 70, detail=2), 0.3, 0.52)          # stencil paint chipped
        ink = None
        if lidband:
            # (round 8) the gas band and its codes moved up off the shaded south face onto the
            # lid's margin, where the camera sees them; the same ochre, codes and arrows
            la, ld, ns = _lid_margin(g)
            # on the south and north margins only (a ring all round read as a frame), worn
            # through in patches
            inband = g.math("MULTIPLY", g.math("MULTIPLY", _between(g, ld, *LID_BAND), ns),
                            g.remap(g.noise(pos, 9, detail=4), 0.3, 0.5))
            col = g.mixc(g.math("MULTIPLY", inband, g.remap(g.noise(pos, 40, detail=3), 0.25, 0.45), clamp=True),
                         col, rig.srgb(LID_BAND_COL))
            v0, v1 = LID_BAND[0] + 0.014, LID_BAND[1] - 0.014
            text = None
            for c in LID_CODES:
                t = _glyphs(g, la, ld, c + 4, c + 22, v0, v1, 0.55)
                text = t if text is None else g.math("MAXIMUM", text, t)
                vc = (v0 + v1) / 2
                dv = g.math("ABSOLUTE", g.math("SUBTRACT", ld, vc))
                tri = g.math("LESS_THAN", dv, g.math("MULTIPLY", g.math("SUBTRACT", c + 36, la), 0.0042))
                text = g.math("MAXIMUM", text, g.math("MULTIPLY", tri, _between(g, la, c + 26, c + 36)))
            ink = g.math("MULTIPLY", text, inband)
        if band:
            inband = _between(g, z, *GAS_Z)
            col = g.mixc(g.math("MULTIPLY", inband, g.remap(g.noise(pos, 40, detail=3), 0.25, 0.45), clamp=True),
                         col, rig.srgb(GAS_BAND))
            z0, z1 = GAS_Z[0] + 0.022, GAS_Z[1] - 0.022
            text = None
            for c in GAS_CODES:
                t = _glyphs(g, a, z, c + 4, c + 22, z0, z1, 0.55)
                text = t if text is None else g.math("MAXIMUM", text, t)
                # a chevron pointing along the face: |z - zc| < (tip - a) * k
                zc = (z0 + z1) / 2
                dz = g.math("ABSOLUTE", g.math("SUBTRACT", z, zc))
                tri = g.math("LESS_THAN", dz, g.math("MULTIPLY", g.math("SUBTRACT", c + 36, a), 0.0042))
                text = g.math("MAXIMUM", text, g.math("MULTIPLY", tri, _between(g, a, c + 26, c + 36)))
            ink = text
        for (am, zm, w, h) in marks:
            m = _glyphs(g, a, z, am - w / 2, am + w / 2, zm - h / 2, zm + h / 2, 0.75)
            ink = m if ink is None else g.math("MAXIMUM", ink, m)
        if ink is not None:
            col = g.mixc(g.math("MULTIPLY", ink, worn, clamp=True), col, rig.srgb(STENCIL))
        # (round 12, Liam: more texture) chipped paint showing the red-oxide primer under it, in
        # scattered clusters; and on the walls, weathering streaks run down the faces
        clus = g.remap(g.noise(pos, 4.5, detail=2), 0.45, 0.6)
        chip = g.math("MULTIPLY", g.remap(g.noise(pos, 34, detail=2), 0.66, 0.72), clus, clamp=True)
        col = g.mixc(g.math("MULTIPLY", chip, chips), col, rig.srgb(PRIMER))
        if where == "face" or streaks:
            sv = g.node("ShaderNodeVectorMath", Vector=pos)
            sv.operation = "MULTIPLY"
            sv.inputs[1].default_value = (26.0, 26.0, 1.6)
            st = g.remap(g.noise(sv.outputs[0], 1.0, detail=3), 0.3, 0.7, 1.0 - streaks_k, 1.0 + 0.5 * streaks_k)
            col = g.mulc(col, g.gray(st))
        return col
    return pattern


_MW = tuple((s_ * K_FACE, z, w * K_FACE, h) for s_, z, w, h in MARKS_WALL)
# the walls' upper two courses: green, the gas band and markings, worn to steel on their
# edges, wet rust run down from the bands, the top flange and the fittings
M["collar"] = layered("collar", GREEN[0], metal="#B8B2A6", paint_metal=0.05, paint_rough=0.66, wear=0.7,
                      rust=0.35, rust_tint=WET_RUST, dust=0.15, grime=0.4, ground=0.8, ground_h=0.35, jitter=0.12,
                      pattern=green_paint("#64765A", "#74886A"),   # the south face takes little sun: the range's light end, a little over
                      drips=((0.74, 0.2), (0.535, 0.22), (0.315, 0.16), (0.66, 0.2)), drip=1.0)
# the lower course, lifted (the pipework's shadows fall on it): the range's light end, a
# little over, so it reads as shaded paint and not black
M["collar_low"] = layered("collar_low", GREEN[1], metal="#B8B2A6", paint_metal=0.05, paint_rough=0.66, wear=0.7,
                          rust=0.3, rust_tint=WET_RUST, dust=0.2, grime=0.1, ground=0.6, ground_h=0.3, jitter=0.12,
                          pattern=green_paint("#6A7C62", "#7A8E70", marks=_MW),
                          drips=((0.315, 0.16), (0.24, 0.12)), drip=0.8)
# one replacement plate: fresher paint, little worn
M["green_alt"] = layered("green_alt", GREEN_FRESH[0], metal="#B8B2A6", paint_metal=0.05, paint_rough=0.6,
                         wear=0.3, rust=0.15, rust_tint=WET_RUST, dust=0.1, grime=0.6, ground=0.8, ground_h=0.35,
                         jitter=0.05, pattern=green_paint("#56704C", "#668258"))
# the lid's hip plates: the same paint, sun-faded, dry orange rust on them
M["lid"] = layered("lid", GREEN[0], metal="#BEB8AC", paint_metal=0.05, paint_rough=0.66, wear=0.3,
                   rust=0.3, rust_tint=DRY_RUST, dust=0.14, grime=0.5, jitter=0.1,
                   pattern=green_paint("#405242", "#4C5E48", fade=0.2, lidband=True, streaks=True, streaks_k=0.12))  # (round 12: a step lighter, so the green reads at 1x)
# its crown: the same, a shade darker and calmer (a sunlit flat lands pale otherwise)
M["lidtop"] = layered("lidtop", GREEN[0], metal="#B4AEA2", paint_metal=0.05, paint_rough=0.62, wear=0.3,
                      rust=0.22, rust_tint=DRY_RUST, dust=0.1, grime=0.7, jitter=0.05,
                      pattern=green_paint("#3A4A3E", "#465842", fade=0.15, lidband=True, streaks=True, streaks_k=0.12))
# (round 8) the west lid plate, worn hardest where the crew climb up: paint through to steel in
# broad scuffed patches, dry rust in them
M["lid_worn"] = layered("lid_worn", GREEN[0], metal="#A49E92", paint_metal=0.05, paint_rough=0.68, wear=0.7,
                        rust=0.45, rust_tint=DRY_RUST, dust=0.2, grime=0.5, jitter=0.1,
                        pattern=green_paint("#405242", "#4C5E48", fade=0.2, lidband=True, chips=1.0, streaks=True))
# the east lid plate: a later replacement, in a different, greyer primer green, barely worn
M["lid_new"] = layered("lid_new", "#56604E", metal="#B4AEA2", paint_metal=0.05, paint_rough=0.55, wear=0.15,
                       rust=0.08, rust_tint=DRY_RUST, dust=0.1, grime=0.35, jitter=0.04,
                       pattern=green_paint("#545E4C", "#5E6A56", fade=0.1, lidband=True, streaks=True))  # (round 12: lifted, in the housing's shade)
# the wellhead boss: green with a stencilled number on its side, worn to steel on its edges
M["boss"] = layered("boss", GREEN[0], metal="#B8B2A6", paint_metal=0.05, paint_rough=0.6, wear=0.6,
                    rust=0.3, rust_tint=DRY_RUST, dust=0.08, grime=0.7, jitter=0.06,
                    pattern=green_paint("#44533F", "#54644E", fade=0.2, marks=MARKS_BOSS, where="round"),
                    drips=((BOSS_TOP_Z, 0.08),), drip=0.6)
M["captop"] = layered("captop", "#36412F", metal="#8A9080", paint_metal=0.08, paint_rough=0.55, wear=0.1,
                      rust=0.04, rust_tint=DRY_RUST, dust=0.03, grime=0.9, jitter=0.03,
                      pattern=green_paint("#2E382B", "#38432F", fade=0.1))


def plinth_paint(g):
    """The plinth's bare steel: dark in the open, caked with pale dust over its east half,
    where the casing's own shadow falls, so that shadow reads as shaded steel and not black
    (the round apron's east half did the same)."""
    pos = g.node("ShaderNodeNewGeometry").outputs["Position"]
    x = g.node("ShaderNodeSeparateXYZ", Vector=pos).outputs["X"]
    drift = g.remap(g.noise(pos, 6, detail=4), 0.3, 0.6, 0.85, 1.0)
    east = g.math("MULTIPLY", g.remap(x, 0.15, 0.55), drift, clamp=True)
    # and drifted against its west edge, where the west mouth's flange throws its shadow
    # (round 13: a third as strong, and broken up -- it read as one long pale strip)
    west = g.math("MULTIPLY", g.remap(x, -0.7, -0.84),
                  g.math("MULTIPLY", g.remap(g.noise(pos, 11, detail=3), 0.4, 0.6), 0.3), clamp=True)
    col = g.mixc(g.math("MAXIMUM", east, west), rig.srgb("#3A3027"), rig.srgb("#9A8C7C"))  # (round 12: base lifted)
    # (round 12, Liam: more texture) no flat slab: boot-scuffed tracks, oily grime blotches,
    # and drifts of grit, each by its own noise
    grime = g.math("MULTIPLY", g.remap(g.noise(pos, 9, detail=4), 0.5, 0.7), 0.55, clamp=True)
    col = g.mixc(grime, col, rig.srgb("#3A3028"))
    sv = g.node("ShaderNodeVectorMath", Vector=pos)
    sv.operation = "MULTIPLY"
    sv.inputs[1].default_value = (3.0, 28.0, 3.0)
    scuff = g.math("MULTIPLY", g.remap(g.noise(sv.outputs[0], 1.0, detail=3), 0.55, 0.72), 0.5, clamp=True)
    col = g.mixc(scuff, col, rig.srgb("#B0A492"))
    # (round 13) the west strip, between the casing and the plinth's edge, no longer one pale
    # slab: oil-darkened patches and rust run along it, value broken up in tile-sized blots
    wz = g.remap(x, -0.56, -0.64)
    oil = g.math("MULTIPLY", wz, g.math("MULTIPLY", g.remap(g.noise(pos, 7, detail=4), 0.42, 0.58), 0.75), clamp=True)
    col = g.mixc(oil, col, rig.srgb("#2E2620"))
    rv = g.node("ShaderNodeVectorMath", Vector=pos)
    rv.operation = "MULTIPLY"
    rv.inputs[1].default_value = (30.0, 2.5, 3.0)
    rst = g.math("MULTIPLY", wz, g.math("MULTIPLY", g.remap(g.noise(rv.outputs[0], 1.0, detail=3), 0.55, 0.7), 0.5),
                 clamp=True)
    col = g.mixc(rst, col, rig.srgb("#6A3A20"))
    spk = g.remap(g.noise(pos, 60, detail=2), 0.3, 0.7, 0.82, 1.14)
    return g.mulc(col, g.gray(spk))


# (round 8) the loose layer: corrugated rubber hose, a dull red-brown as vanilla's are; the
# junction and instrument boxes in grey-green and dull yellow-grey enamel; cables in muted
# colours; nylon ties; oil
M["hose"] = layered("hose", "#7C5240", metal="#9A7A66", paint_metal=0.0, paint_rough=0.72, wear=0.15,
                    rust=0.05, dust=0.25, grime=0.55, jitter=0.12)
M["jbox"] = layered("jbox", "#6E7668", metal="#BCB6AA", paint_metal=0.05, paint_rough=0.55, wear=0.5,
                    rust=0.25, rust_tint=WET_RUST, dust=0.15, grime=0.4, jitter=0.06)
M["instr"] = layered("instr", "#8C8466", metal="#C4BEB2", paint_metal=0.05, paint_rough=0.55, wear=0.45,
                     rust=0.2, rust_tint=WET_RUST, dust=0.15, grime=0.4, jitter=0.06)
M["jgland"] = plain("jgland", "#3E3C38", rough=0.6)
M["tie"] = plain("tie", "#45443F", rough=0.55)
M["cable_olive"] = plain("cable_olive", "#76823E", rough=0.45)
M["cable_black"] = plain("cable_black", "#3E3D39", rough=0.4)
M["cable_red"] = plain("cable_red", "#9A4632", rough=0.45)
M["cable_grey"] = plain("cable_grey", "#8E8C84", rough=0.45)
M["oil"] = plain("oil", "#40342A", rough=0.3)
M["edge_dust"] = layered("edge_dust", "#7E7262", metal="#A89C8C", paint_metal=0.05, paint_rough=0.85, wear=0.3,
                         rust=0.25, rust_tint=WARM_RUST, dust=0.6, grime=0.2, jitter=0.05)
M["grit"] = layered("grit", "#8C7E6C", metal="#A89C8C", paint_metal=0.0, paint_rough=0.9, wear=0.1, rust=0.15,
                    rust_tint=WARM_RUST, dust=0.6, grime=0.2, jitter=0.05)
# (round 10) the compressor housing: the casing's green, a step lighter on its leaning faces
M["housing"] = layered("housing", GREEN[1], metal="#C4BEB2", paint_metal=0.06, paint_rough=0.6, wear=0.6,
                       rust=0.3, rust_tint=WET_RUST, dust=0.15, grime=0.45, jitter=0.1,
                       pattern=green_paint("#627459", "#728668", fade=0.2), drips=((1.06, 0.15),), drip=0.8)
# (round 12) the main line painted in the casing's green, as vanilla paints a chemical plant's
# process pipes in its yellow: worn to steel on its bends and flanges' edges, primer chipped,
# wet rust run from the joints; a step lighter than the walls so its underside stays coloured
M["line_green"] = layered("line_green", GREEN[1], metal="#C8C2B6", paint_metal=0.08, paint_rough=0.38, wear=0.5,
                          rust=0.35, rust_tint=WET_RUST, dust=0.12, grime=0.3, jitter=0.08,
                          pattern=green_paint("#687A5E", "#7A8E70", fade=0.25, chips=1.0),
                          drips=((HZ_FILL, 0.2),), drip=0.5)
# the corner plates: the walls' paint, worn through to steel along their bends
M["corner"] = layered("corner", GREEN[1], metal="#C4BEB2", paint_metal=0.06, paint_rough=0.6, wear=0.85,
                      rust=0.3, rust_tint=WET_RUST, dust=0.15, grime=0.2, ground=0.6, ground_h=0.3, jitter=0.1,
                      pattern=green_paint("#62725A", "#72846A"), drips=((0.74, 0.2), (0.535, 0.2)), drip=0.8)
M["plinth"] = layered("plinth", "#463C32", metal="#A49A8C", paint_metal=0.18, paint_rough=0.66, wear=0.4,
                      rust=0.15, rust_tint=WARM_RUST, dust=0.35, grime=0.25, ground=0.4, ground_h=0.1, jitter=0.06,
                      pattern=plinth_paint)
for _a in argv:                                   # debugging: --plain=<material>:<hex> swaps one out
    if _a.startswith("--plain="):
        _n, _h = _a[len("--plain="):].split(":")
        M[_n] = plain(_n, _h)

# ---------------------------------------------------------------- geometry helpers

PARTS = {}          # group name -> [objects]; the passes toggle whole groups


def _where():
    """The model's own line that built a part (for --check's report)."""
    f = sys._getframe(1)
    lines = []
    while f is not None:
        if f.f_code.co_filename == __file__ and f.f_code.co_name not in _HELPERS:
            lines.append(str(f.f_lineno))
        f = f.f_back
    return "<".join(lines)


_HELPERS = {"_where", "_finish", "box", "cyl", "cone", "torus", "rivet", "bolt", "mesh_object", "stack", "ring",
            "pipe", "place", "bolt_ring", "arc_band", "wall_plate", "ring_outline", "lid_plate", "tee", "<listcomp>"}


def _finish(obj, mat, group, bevel=0.01, smooth=False, parent=None):
    obj["line"] = _where()
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


def box(loc, size, mat, group="static", rot=(0, 0, 0), bevel=0.008, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, mat, group, bevel, parent=parent)


def cyl(loc, r, h, mat, group="static", verts=48, rot=(0, 0, 0), bevel=0.006, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    o = _finish(bpy.context.active_object, mat, group, bevel, smooth=True, parent=parent)
    for p in o.data.polygons:          # the caps flat: a smoothed n-gon cap shades as a dark star
        if len(p.vertices) > 4:
            p.use_smooth = False
    return o


def cone(loc, r0, r1, h, mat, group="static", verts=48, rot=(0, 0, 0), bevel=0.004, parent=None):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r0, radius2=r1, depth=h, location=loc, rotation=rot)
    o = _finish(bpy.context.active_object, mat, group, bevel, smooth=True, parent=parent)
    for p in o.data.polygons:
        if len(p.vertices) > 4:
            p.use_smooth = False
    return o


def torus(loc, major, minor, mat, group="static", rot=(0, 0, 0), parent=None, seg=48):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot,
                                     major_segments=seg, minor_segments=8)
    return _finish(bpy.context.active_object, mat, group, bevel=0, smooth=True, parent=parent)


def rivet(loc, r=0.012, mat="steel", group="static", parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=8, ring_count=5, rotation=rot)
    o = bpy.context.active_object
    o.scale.z = 0.6
    return _finish(o, mat, group, bevel=0, smooth=True, parent=parent)


def bolt(loc, r=0.016, h=0.014, mat="steel", group="static", rot=(0, 0, 0), parent=None):
    """A hex head."""
    return cyl(loc, r, h, mat, group, verts=6, rot=rot, bevel=0.0, parent=parent)


def mesh_object(name, build, mat, group, bevel, smooth=False, parent=None, recalc=True):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    return _finish(o, mat, group, bevel, smooth=smooth, parent=parent)


def stack(levels, mat, group="static", bevel=0.008, parent=None, name="stack", smooth=False):
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
    return mesh_object(name, build, mat, group, bevel, smooth=smooth, parent=parent)


def ring(loc, r_out, r_in, h, mat, group="static", parent=None, verts=64, bevel=0.006, rot=(0, 0, 0)):
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


def pipe(pts, r, mat, bend=0.06, group="static", parent=None):
    """A rigid run through pts, each corner turned through an elbow of radius ~bend."""
    out = [Vector(pts[0])]
    for i in range(1, len(pts) - 1):
        p, a_, b_ = Vector(pts[i]), Vector(pts[i - 1]), Vector(pts[i + 1])
        e = min(bend, 0.45 * (a_ - p).length, 0.45 * (b_ - p).length)
        s0, s1 = p + (a_ - p).normalized() * e, p + (b_ - p).normalized() * e
        for k in range(13):
            t = k / 12
            out.append((1 - t) ** 2 * s0 + 2 * (1 - t) * t * p + t * t * s1)
    out.append(Vector(pts[-1]))
    cu = bpy.data.curves.new("pipe", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(out) - 1)
    for pt, co in zip(sp.points, out):
        pt.co = (*co, 1)
    ob = bpy.data.objects.new("pipe", cu)
    sc.collection.objects.link(ob)
    return _finish(ob, mat, group, bevel=0, parent=parent)


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.parent = parent or ROOT
    e.location, e.rotation_euler = loc, rot
    return e


def facing(d):
    """The rotation taking local +Z to direction d (a Vector), local +Y kept up where it can be."""
    d = Vector(d).normalized()
    up = "Y" if abs(d.z) < 0.9 else "X"
    return d.to_track_quat("Z", up).to_euler()


def place(p0, p1, r0, r1, mat, group, verts=32, bevel=0.003):
    """A cylinder (r0 == r1) or a cone from p0 to p1."""
    v = p1 - p0
    mid = (p0 + p1) / 2
    if abs(r0 - r1) < 1e-6:
        return cyl(tuple(mid), r0, v.length, mat, group, verts=verts, rot=facing(v), bevel=bevel)
    return cone(tuple(mid), r0, r1, v.length, mat, group, verts=verts, rot=facing(v), bevel=bevel)


def bolt_ring(centre, axis, r, n, size, group, mat="steel", phase=0.0, h=0.012):
    rot = facing(axis)
    q = axis.normalized().to_track_quat("Z", "Y" if abs(axis.z) < 0.9 else "X")
    for k in range(n):
        u = 2 * math.pi * (k + phase) / n
        bolt(tuple(centre + q @ Vector((r * math.cos(u), r * math.sin(u), 0))), size, h, mat, group, rot=rot)


def circle(r, n=64, cx=0.0, cy=0.0, a0=0.0):
    return [(cx + r * math.cos(a0 + 2 * math.pi * k / n), cy + r * math.sin(a0 + 2 * math.pi * k / n))
            for k in range(n)]


def chamfered_square(e, c):
    return [(-e, -e + c), (-e + c, -e), (e - c, -e), (e, -e + c), (e, e - c), (e - c, e), (-e + c, e), (-e, e - c)]


def arc_plate(r0, r1, a0, a1, z0, z1, mat, group="static", n=16, bevel=0.003, name="arcplate"):
    """A curved plate on a cylinder about the origin: radii r0..r1, angles a0..a1
    (degrees, from east, anticlockwise), heights z0..z1."""
    def build(bm):
        rows = []
        for r, z in ((r0, z0), (r1, z0), (r1, z1), (r0, z1)):
            rows.append([bm.verts.new((r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
                                       r * math.sin(math.radians(a0 + (a1 - a0) * k / n)), z)) for k in range(n + 1)])
        for k in range(4):
            a, b = rows[k], rows[(k + 1) % 4]
            for i in range(n):
                bm.faces.new((a[i], a[i + 1], b[i + 1], b[i]))
        bm.faces.new([rows[k][0] for k in range(4)])
        bm.faces.new([rows[k][n] for k in reversed(range(4))])
    return mesh_object(name, build, mat, group, bevel, smooth=True)


def polar(r, a, z):
    t = math.radians(a)
    return (r * math.cos(t), r * math.sin(t), z)


def arc_band(r_out, r_in, z, h, a0, a1, mat, group="static", n=20, bevel=0.002, centre=(0.0, 0.0)):
    """A short arc of ring round a vertical axis through centre, a0..a1 degrees: worn
    bright only where it is worn, broken, never a whole hoop."""
    def build(bm):
        rows = []
        for r, zz in ((r_out, z - h / 2), (r_out, z + h / 2), (r_in, z + h / 2), (r_in, z - h / 2)):
            rows.append([bm.verts.new((centre[0] + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
                                       centre[1] + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)), zz))
                         for k in range(n + 1)])
        for k in range(4):
            a, b = rows[k], rows[(k + 1) % 4]
            for i in range(n):
                bm.faces.new((a[i], a[i + 1], b[i + 1], b[i]))
        bm.faces.new([rows[k][0] for k in range(4)])
        bm.faces.new([rows[k][n] for k in reversed(range(4))])
    return mesh_object("arc", build, mat, group, bevel)



# ---------------------------------------------------------------- 1. the base plate

PE, PC = 0.985, 0.12                  # half-width (the footprint, less a hair) and its corners cut
PT = 0.06                             # its top
RT = 0.095                            # its rim's top: the mouths' flange collars clear it
stack([(chamfered_square(PE, PC), 0.0), (chamfered_square(PE, PC), PT)], "plate", bevel=0.008, name="plate")
# the rim: angle iron round the edge, worn bright on its corners, riveted
_rim = chamfered_square(PE - 0.03, PC * 0.8)
for i, (ax, ay) in enumerate(chamfered_square(PE - 0.03, PC * 0.8)):
    bx, by = _rim[(i + 1) % 8]
    d = Vector((bx - ax, by - ay, 0))
    box(((ax + bx) / 2, (ay + by) / 2, (PT + RT) / 2), (d.length + 0.05, 0.065, RT - PT), "edge",
        rot=(0, 0, math.atan2(d.y, d.x)), bevel=0.006)
    n = max(1, round(d.length / 0.11))
    for k in range(n):
        f = (k + 0.5) / n
        rivet((ax + (bx - ax) * f, ay + (by - ay) * f, RT + 0.002), 0.011)
# the rim's top worn bright in broken stretches along the front and the west, where it is
# stepped over
for (x0, y0, x1, y1) in ((-0.62, -0.955, -0.4, -0.955), (-0.1, -0.955, 0.12, -0.955), (0.45, -0.955, 0.62, -0.955),
                         (-0.955, -0.5, -0.955, -0.3), (-0.955, 0.2, -0.955, 0.34),
                         # (round 7) and in shorter stretches round the north and the east
                         (-0.5, 0.955, -0.36, 0.955), (0.1, 0.955, 0.22, 0.955), (0.955, -0.42, 0.955, -0.3),
                         (0.955, 0.1, 0.955, 0.24), (0.955, 0.5, 0.955, 0.6), (-0.955, -0.12, -0.955, -0.02)):
    d = Vector((x1 - x0, y1 - y0, 0))
    box(((x0 + x1) / 2, (y0 + y1) / 2, RT + 0.001), (d.length, 0.012, 0.004), "polish",
        rot=(0, 0, math.atan2(d.y, d.x)), bevel=0.0)
# a riveted flat bar inside the rim along each edge, anchor to anchor: the plate's frame
for k in range(4):
    t = math.radians(90 * k)
    u, v = Vector((math.cos(t), math.sin(t), 0)), Vector((-math.sin(t), math.cos(t), 0))
    c = u * 0.886                                     # (round 7: out from 0.875, clear of the south support)
    box(tuple(c + Vector((0, 0, PT + 0.006))), (0.045, 1.16, 0.012), "edge_dust" if k == 0 else "edge", rot=(0, 0, t),
        bevel=0.003)                                  # (round 10: the east one caked in the grit, 9.)
    for j in range(12):
        f = -0.54 + 1.08 * j / 11
        rivet(tuple(c + v * f + Vector((0, 0, PT + 0.013))), 0.0095)
    # bolt lugs on the plate's edge face, either side of the middle
    for f in (-0.36, 0.36):
        p = u * (PE - 0.01) + v * f                    # inside the footprint: the base square stays 2.000
        box(tuple(p + Vector((0, 0, 0.045))), (0.024, 0.12, 0.07), "anchor", rot=(0, 0, t), bevel=0.005)
        bolt(tuple(p + u * 0.012 + Vector((0, 0, 0.045))), 0.02, 0.008, "head", rot=(0, math.pi / 2, t))
# a bolted lug at the middle of the north and south edges (the plates' edge lugs)
for s in (-1, 1):
    y = s * (PE - 0.07)
    box((0.0, y, RT + 0.025), (0.14, 0.1, 0.05), "anchor", bevel=0.01)
    bolt((0.0, y, RT + 0.06), 0.03, 0.022, "steel")
    cyl((0.0, y, RT + 0.052), 0.04, 0.006, "copper", verts=24, bevel=0.0)       # its copper washer
# scuffs and a repair patch on the plate's west margin
PATCH = empty("patch", loc=(-0.9, -0.3, PT), rot=(0, 0, math.radians(7)))
box((0, 0, 0.004), (0.1, 0.16, 0.008), "patch", bevel=0.003, parent=PATCH)
for sy in (-1, 1):
    rivet((0, sy * 0.06, 0.009), 0.009, parent=PATCH)

# ---------------------------------------------------------------- 2. the anchors

AC, AH = 0.78, 0.18                  # the anchors' foot: its centre (each corner) and half-size
AB = 0.745                           # the blocks' and the bolt's centre, in from the foot's: clear of
                                     # the north mouth's collar, which passes over the foot, and (round 7)
                                     # of the north and south stands' foot flanges
A_TOP = 0.295                        # the bolt's top: the risers pass over it


def anchor(sx, sy):
    """A ground anchor: a chamfered foot bolted down round its outer edges, two stepped
    blocks, a washer and a big hex bolt, the plates' chunky corner."""
    cx, cy = sx * AC, sy * AC
    bx, by = sx * AB, sy * AB
    stack([(chamfered_square(AH, 0.06), PT), (chamfered_square(AH - 0.012, 0.06), 0.11)], "anchor", bevel=0.012,
          name="anchor-foot")
    PARTS["static"][-1].location = (cx, cy, 0)
    stack([(chamfered_square(0.14, 0.045), 0.11), (chamfered_square(0.13, 0.045), 0.18)], "anchor",
          bevel=0.014, name="anchor-block")
    PARTS["static"][-1].location = (bx, by, 0)
    stack([(chamfered_square(0.1, 0.03), 0.18), (chamfered_square(0.092, 0.03), 0.222)], "anchor",
          bevel=0.012, name="anchor-cap")
    PARTS["static"][-1].location = (bx, by, 0)
    cyl((bx, by, 0.229), 0.094, 0.014, "steel", verts=32, bevel=0.003)             # the washer
    # the cap block's outer top edges knocked bright, in two broken stretches each
    for (ux, uy), f0, f1 in (((1, 0), -0.07, 0.02), ((1, 0), 0.05, 0.08), ((0, 1), -0.08, -0.03),
                             ((0, 1), 0.0, 0.07)):
        e = Vector((sx * ux, sy * uy, 0)) * 0.093
        along = Vector((uy * sx, ux * sy, 0))
        mid = Vector((bx, by, 0.221)) + e + along * (f0 + f1) / 2
        box(tuple(mid), (0.008 if ux else f1 - f0, f1 - f0 if ux else 0.008, 0.006), "polish", bevel=0.0)
    bolt((bx, by, 0.26), 0.078, 0.05, "steel")                                      # the hex head: mid steel
    cyl((bx, by, 0.29), 0.032, 0.012, "steel", verts=16, bevel=0.002)               # the stud
    # its top edge worn bright in two short broken stretches, not a pale head
    for a0, a1 in ((200, 228), (300, 318)):
        arc_band(0.074, 0.058, 0.2855, 0.006, a0 + (45 if sx * sy < 0 else 0), a1 + (45 if sx * sy < 0 else 0),
                 "polish", centre=(bx, by))
    # the foot bolted down round its outer edges, clear of the block
    for dx, dy in ((0.15, 0.15), (0.15, 0.0), (0.0, 0.15), (0.15, -0.13), (-0.13, 0.15)):
        bolt((cx + sx * dx, cy + sy * dy, 0.117), 0.018, 0.014)
        cyl((cx + sx * dx, cy + sy * dy, 0.1115), 0.025, 0.003, "copper", verts=16, bevel=0.0)


for sx in (-1, 1):
    for sy in (-1, 1):
        anchor(sx, sy)

# ---------------------------------------------------------------- 3. the housing (round 7)

# Round 7 (Liam: "could it be made less circular"): the round collar, dome, shoulder, head
# flange and cap are replaced by a square-plan pump casing with its corners cut -- riveted
# plate walls in three courses with bolted angle iron up every corner, a shallow hipped lid
# in plates with two inspection covers, and ONE round bolted boss on it, the wellhead. It
# stands on a square plinth with its corners cut.
#
# Its size is set by the risers, which do not change: the north riser's handwheel reaches
# (0.42, 0.47) at z 0.3, so the casing's corner cut is 0.20 (its line |x| + |y| = 0.83);
# the east stand's flange (0.30, -0.70, r 0.105) and the west run (x -0.733, joints r 0.101)
# keep the walls in to 0.50 and 0.53, and the stands' foot flanges keep the plinth in to
# 0.585 and 0.61 (every stand now stands on the base plate, beside the plinth).
HX, HY, HC = 0.53, 0.50, 0.20                  # the casing as round 7 had it (round 10: see outline())
PL_E, PL_N, PL_T = 0.86, 0.595, 0.12          # the plinth: half-width, its corners notched for the anchors, top
WZ0, WT = PL_T + 0.03, 0.74                    # the walls: foot (on the foot angle) and top
BANDS = (0.34, 0.56)                           # the course bands
LZ0 = LZ1 = 0.78                               # the lid's top: flat
L_IN = 0.25
BOSS_C, BOSS_R = Vector((-0.09, -0.05, 0.0)), 0.14  # the wellhead boss
BOSS_Z0 = LZ1
BEAT = 0.012                                   # how far each wall plate is beaten out
SQ2 = math.sqrt(2.0)


# (round 10, Liam: "more bulky") the casing grown east, where nothing of the risers stands
# between it and the plinth's edge: its west face stays at -0.53 (the west run at x -0.733),
# its south face at -0.50 (the mains in front of it and the east stand), its north face at
# 0.50 (the north stand); its east face out to 0.68. The north-east cut is 0.34 (its line
# x + y = 0.84 keeps the north riser's handwheel clear); the other three 0.20.
CW, CE, CS, CN = -0.53, 0.68, -0.50, 0.50
CUTS = (0.20, 0.20, 0.34, 0.20)                 # south-west, south-east, north-east, north-west


def outline(w=CW, e=CE, s_=CS, n=CN, cuts=CUTS):
    """The casing's plan: a rectangle with its corners cut (all at 45 degrees), anticlockwise
    from the west end of the south-west cut. Edge i runs from point i to i + 1: 0 south-west
    cut, 1 south, 2 south-east cut, 3 east, 4 north-east cut, 5 north, 6 north-west cut, 7 west."""
    sw, se, ne, nw = cuts
    return [(w, s_ + sw), (w + sw, s_), (e - se, s_), (e, s_ + se), (e, n - ne), (e - ne, n), (w + nw, n), (w, n - nw)]


def outline_off(d):
    """The casing's plan moved out by d on every face."""
    k = d * (2 - SQ2)
    return outline(CW - d, CE + d, CS - d, CN + d, tuple(c + k for c in CUTS))


def edges(poly):
    """(A, B, tangent, outward normal) for each edge of an anticlockwise outline."""
    out = []
    for i in range(len(poly)):
        a, b = Vector((*poly[i], 0)), Vector((*poly[(i + 1) % len(poly)], 0))
        t = (b - a).normalized()
        out.append((a, b, t, Vector((t.y, -t.x, 0))))
    return out


def ground_z(x, y):
    """The top of what is under (x, y): the plinth, or the base plate."""
    if abs(x) <= PL_E and abs(y) <= PL_E and not (abs(x) > PL_N and abs(y) > PL_N):
        return PL_T
    return PT


def lid_z(x, y):
    """The lid's top at (x, y): flat (round 7 on)."""
    return LZ0


def along(poly, step, inset=0.0, ends=0.0, which=None):
    """Points every ~step along a closed outline's edges, `ends` clear of each corner:
    (point, tangent, normal, edge index)."""
    pts = []
    for i, (a, b, t, n) in enumerate(edges(poly)):
        if which is not None and i not in which:
            continue
        L = (b - a).length - 2 * ends
        if L <= 0:
            continue
        k = max(1, round(L / step))
        for j in range(k):
            pts.append((a + t * (ends + L * (j + 0.5) / k) - n * inset, t, n, i))
    return pts


def ring_outline(z, w, d_out, d_in, mat, name="band", bevel=0.004):
    """A strap round the casing at height z, w tall, from d_in to d_out off its faces."""
    loops = ((d_out, z - w / 2), (d_out, z + w / 2), (d_in, z + w / 2), (d_in, z - w / 2))

    def build(bm):
        rows = [[bm.verts.new((x, y, zz)) for x, y in outline_off(d)] for d, zz in loops]
        for k in range(4):
            a, b = rows[k], rows[(k + 1) % 4]
            for i in range(8):
                j = (i + 1) % 8
                bm.faces.new((a[i], a[j], b[j], b[i]))
    return mesh_object(name, build, mat, "static", bevel=bevel)


def offset_poly(poly, d):
    """An anticlockwise outline moved in by d on every edge (mitred)."""
    out = []
    n = len(poly)
    for i in range(n):
        p0, p1, p2 = (Vector((*poly[(i + k) % n], 0)) for k in (-1, 0, 1))
        t1, t2 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n1, n2 = Vector((-t1.y, t1.x, 0)), Vector((-t2.y, t2.x, 0))
        m = (n1 + n2) / (1 + n1.dot(n2))
        out.append(tuple((p1 + m * d)[:2]))
    return out


# the plinth (the round apron, made square): a low block over most of the plate, its corners
# notched square round the anchors, its top edge chamfered, riveted round its top; the
# risers' stands, the crossings' pads and the gauge glass stand on it
PLINTH = [(-PL_N, -PL_E), (PL_N, -PL_E), (PL_N, -PL_N), (PL_E, -PL_N), (PL_E, PL_N), (PL_N, PL_N), (PL_N, PL_E),
          (-PL_N, PL_E), (-PL_N, PL_N), (-PL_E, PL_N), (-PL_E, -PL_N), (-PL_N, -PL_N)]
stack([(PLINTH, PT), (PLINTH, PL_T - 0.02), (offset_poly(PLINTH, 0.02), PL_T)], "plinth", bevel=0.005, name="plinth")
FEET = [(0.5, 0.67), (0.30, -0.704), (-0.5, -0.67), (-0.733, -0.267), (0.52, -0.704), (-0.5, -0.80), (-0.733, 0.15),
        (0.80, 0.52), (0.775, -0.43), (0.77, -0.01)]                # (round 10: and the pads by the east face)
for p, t, n, i in along(offset_poly(PLINTH, 0.035), 0.085, ends=0.03):
    if min(math.hypot(p.x - fx, p.y - fy) for fx, fy in FEET) > 0.12:     # none under a riser's stand or support
        rivet((p.x, p.y, PL_T + 0.002), 0.009, "head")
for (x0, y0, x1, y1) in ((-0.42, -0.842, -0.25, -0.842), (0.02, -0.842, 0.14, -0.842), (0.36, -0.842, 0.5, -0.842),
                         (-0.842, -0.4, -0.842, -0.2), (-0.842, 0.05, -0.842, 0.16), (-0.842, 0.42, -0.842, 0.52),
                         (0.842, -0.3, 0.842, -0.18), (0.842, 0.2, 0.842, 0.3), (-0.3, 0.842, -0.1, 0.842),
                         (0.15, 0.842, 0.3, 0.842), (-0.582, -0.76, -0.582, -0.84), (0.582, -0.66, 0.582, -0.8)):
    d = Vector((x1 - x0, y1 - y0, 0))
    box(((x0 + x1) / 2, (y0 + y1) / 2, PL_T + 0.001), (d.length, 0.012, 0.004), "polish",
        rot=(0, 0, math.atan2(d.y, d.x)), bevel=0.0)                            # its edge worn bright, broken
for a, (x, y), w in ((0.4, (-0.3, -0.74), 0.12), (1.1, (-0.7, -0.45), 0.09), (2.0, (0.1, -0.78), 0.1)):
    box((x, y, PL_T + 0.001), (0.03, w, 0.003), "scuff", rot=(0, 0, a), bevel=0.0)  # scuffed where the crew stand

import random as _random
# the casing's foot: an angle round it on the plinth, bolted down, its edge scuffed bright
ring_outline(PL_T + 0.015, 0.03, 0.04, -0.01, "rail", name="foot")
_rf = _random.Random(3)
for p, t, n, i in along(outline_off(0.038), 0.07, ends=0.03):
    if _rf.random() < 0.5:
        box(tuple(p + Vector((0, 0, PL_T + 0.03))), (0.03 + 0.03 * _rf.random(), 0.006, 0.005), "polish",
            rot=(0, 0, math.atan2(t.y, t.x)), bevel=0.0)
for p, t, n, i in along(outline_off(0.022), 0.09, ends=0.04):
    bolt((p.x, p.y, PL_T + 0.036), 0.013, 0.012, "head")
band_z = (PL_T + 0.03, *BANDS, WT)                  # the courses' feet and tops


def wall_plate(a, b, z0, z1, mat, n=6, m=5):
    """A wall plate between a and b (on the casing's face), z0..z1, beaten out a little
    between its edges so each plate takes the light on its own curve."""
    t = (b - a).normalized()
    nrm = Vector((t.y, -t.x, 0))

    def build(bm):
        rows = []
        for j in range(m + 1):
            v = j / m
            row = []
            for k in range(n + 1):
                u = k / n
                p = a + (b - a) * u + nrm * BEAT * math.sin(math.pi * u) * math.sin(math.pi * v)
                row.append(bm.verts.new((p.x, p.y, z0 + (z1 - z0) * v)))
            rows.append(row)
        for r0, r1 in zip(rows, rows[1:]):
            for k in range(n):
                bm.faces.new((r0[k], r0[k + 1], r1[k + 1], r1[k]))
    o = mesh_object("wallplate", build, mat, "static", bevel=0.0, smooth=True)
    sol = o.modifiers.new("solid", "SOLIDIFY")
    sol.thickness = 0.05
    sol.offset = -1.0
    return o


# the walls in plates, three courses, each course's joints staggered against the one below;
# one plate replaced in fresher paint (the upper course, the south face's west plate)
SPLITS = {0: (0.0, 1 / 3, 2 / 3, 1.0), 1: (0.0, 1 / 6, 1 / 2, 5 / 6, 1.0), 2: (0.0, 1 / 3, 2 / 3, 1.0)}
SEAMS = []                                      # (point on the face, normal, z0, z1): welds and rivets
for i, (a, b, t, n) in enumerate(edges(outline())):
    for c, (z0, z1) in enumerate(zip(band_z, band_z[1:])):
        cuts = SPLITS[c] if i % 2 else (0.0, 1.0)            # a corner cut: one plate a course
        for k, (f0, f1) in enumerate(zip(cuts, cuts[1:])):
            mat = "collar_low" if c == 0 else "collar"
            if i == 1 and c == 2 and k == 0:
                mat = "green_alt"
            wall_plate(a + (b - a) * f0, a + (b - a) * f1, z0, z1, mat)
        for f in cuts[1:-1]:
            SEAMS.append((a + (b - a) * f, n, z0, z1))
for p, n, z0, z1 in SEAMS:
    ang = math.atan2(n.y, n.x)
    box(tuple(p + n * 0.003 + Vector((0, 0, (z0 + z1) / 2))), (0.016, 0.016, z1 - z0 - 0.04), "seam",
        rot=(0, 0, ang), bevel=0.004)
    t = Vector((-n.y, n.x, 0))
    k = max(2, round((z1 - z0) / 0.07))
    for j in range(k):
        rivet(tuple(p + n * 0.004 + t * 0.024 + Vector((0, 0, z0 + 0.04 + (z1 - z0 - 0.08) * j / (k - 1)))), 0.009,
              rot=(0, math.pi / 2, ang))

# the course bands: flat straps round the casing, riveted top and bottom, worn bright in
# broken stretches on their top edges along the front
for zb in BANDS:
    ring_outline(zb, 0.05, 0.022, -0.01, "rail")
    for p, t, n, i in along(outline_off(0.022), 0.06, ends=0.07):
        for dz in (-0.015, 0.015):
            rivet((p.x, p.y, zb + dz), 0.0095, "head", rot=(0, math.pi / 2, math.atan2(n.y, n.x)))
    _rb = _random.Random(int(zb * 100))
    for p, t, n, i in along(outline_off(0.02), 0.06, ends=0.04):
        if _rb.random() < 0.5:
            L_ = 0.025 + 0.03 * _rb.random()
            box(tuple(p + Vector((0, 0, zb + 0.025))), (L_, 0.006, 0.006), "polish", rot=(0, 0, math.atan2(t.y, t.x)),
                bevel=0.0)
ring_outline(WZ0 + 0.012, 0.024, 0.012, -0.01, "seam", name="footweld")          # the ground joint

# the lid's bolting flange: an angle round the walls' top, bolted to the lid's edge
ring_outline(WT + 0.012, 0.03, 0.032, -0.01, "rail", name="topflange")
for p, t, n, i in along(outline_off(0.016), 0.075, ends=0.05):
    bolt((p.x, p.y, LZ0 + 0.004), 0.013, 0.012, "head")
# its outer top edge worn bright in broken stretches all round, as the lid's edge is where it
# is stood on and struck
_rnd = _random.Random(7)
for p, t, n, i in along(outline_off(0.03), 0.07, ends=0.03):
    if _rnd.random() < 0.55:
        L_ = 0.03 + 0.03 * _rnd.random()
        box(tuple(p + Vector((0, 0, WT + 0.027))), (L_ if abs(t.x) > 0.5 else 0.006, L_ if abs(t.y) > 0.5 else 0.006,
                                                    0.005), "polish", rot=(0, 0, 0) if i % 2 else
            (0, 0, math.atan2(t.y, t.x)), bevel=0.0)

# bolted angle up every corner: one heavy plate bent over each corner cut, wrapping onto
# both walls, bolted through its wraps and down the middle of the cut, its edges worn bright
E8 = edges(outline())
WRAP, TH = 0.05, 0.016


def _mit(n1, n2):
    return (n1 + n2) / (1 + n1.dot(n2))


for i in range(0, 8, 2):
    A, B, t, n = E8[i]
    tp, np_ = E8[i - 1][2], E8[i - 1][3]
    tn, nn = E8[(i + 1) % 8][2], E8[(i + 1) % 8][3]
    p0, p3 = A - tp * WRAP, B + tn * WRAP
    prof = [p0, A, B, p3, p3 + nn * TH, B + _mit(n, nn) * TH, A + _mit(np_, n) * TH, p0 + np_ * TH]
    stack([([(p.x, p.y) for p in prof], WZ0), ([(p.x, p.y) for p in prof], WT + 0.026)], "corner", bevel=0.004,
          name="corner")
    for z in (0.21, 0.29, 0.42, 0.49, 0.63, 0.7):
        for c, nrm in ((A - tp * WRAP * 0.5, np_), (B + tn * WRAP * 0.5, nn), ((A + B) / 2, n)):
            if nrm is n and z not in (0.21, 0.42, 0.63):
                continue
            bolt(tuple(c + nrm * (TH + 0.003) + Vector((0, 0, z))), 0.011, 0.01, "head",
                 rot=(0, math.pi / 2, math.atan2(nrm.y, nrm.x)))
    # its two bends knocked bright in broken stretches
    for c, (z0, z1) in ((A + _mit(np_, n) * (TH + 0.001), (0.25, 0.34)), (A + _mit(np_, n) * (TH + 0.001), (0.55, 0.6)),
                        (B + _mit(n, nn) * (TH + 0.001), (0.36, 0.44)), (B + _mit(n, nn) * (TH + 0.001), (0.62, 0.7))):
        box(tuple(c + Vector((0, 0, (z0 + z1) / 2))), (0.007, 0.007, z1 - z0), "polish", bevel=0.0)

# the lid: flat, in three plates lapped and riveted north-south, its edge bolted down to the
# top flange; the middle plate, under the wellhead, a shade darker
LID = outline_off(0.025)
LID_CUTS = (CW - 0.025, -0.18, 0.195, CE + 0.025)


def clip_x(poly, x0, x1):
    """The part of a closed outline between x0 and x1."""
    def clip(pts, keep, xc):
        out = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            if keep(a):
                out.append(a)
            if keep(a) != keep(b):
                out.append((xc, a[1] + (b[1] - a[1]) * (xc - a[0]) / (b[0] - a[0])))
        return out
    return clip(clip(poly, lambda p: p[0] >= x0 - 1e-9, x0), lambda p: p[0] <= x1 + 1e-9, x1)


def lid_plate(pts, z, mat):
    def build(bm):
        bm.faces.new([bm.verts.new((x, y, z)) for x, y in pts])
    o = mesh_object("lidplate", build, mat, "static", bevel=0.0, recalc=False)
    sol = o.modifiers.new("solid", "SOLIDIFY")
    sol.thickness = 0.03
    sol.offset = -1.0
    return o


# (round 8) not machined true: each plate a hair off level and off square, the east one a
# later replacement in a different primer, sitting a little proud; the west one, where the
# crew climb up, worn hardest
LID_TRIM = (("lid_worn", (0.012, -0.016, 0.004), 0.0), ("lidtop", (-0.01, 0.006, -0.003), 0.001),
            ("lid_new", (0.014, 0.018, 0.007), 0.004))
for k, (x0, x1) in enumerate(zip(LID_CUTS, LID_CUTS[1:])):
    mat_, (rx, ry, rz), dz = LID_TRIM[k]
    pts_ = clip_x(LID, x0 + (0.002 if k == 2 else 0), x1)
    cx_ = sum(p[0] for p in pts_) / len(pts_)
    cy_ = sum(p[1] for p in pts_) / len(pts_)
    o_ = lid_plate([(p[0] - cx_, p[1] - cy_) for p in pts_], 0.0, mat_)
    o_.location = (cx_, cy_, LZ0 + dz)
    o_.rotation_euler = (rx, ry, rz)
for xc in LID_CUTS[1:-1]:                                  # the laps: a raised strip, riveted both sides
    ys = [p[1] for p in clip_x(LID, xc - 1e-3, xc + 1e-3)]
    y0, y1 = min(ys) + 0.02, max(ys) - 0.02
    box((xc, (y0 + y1) / 2, LZ0 + 0.004), (0.034, y1 - y0, 0.008), "lid", bevel=0.003)
    for ya, yb in ((y0 + 0.05, y0 + 0.16), (y0 + 0.3, y0 + 0.38), (y1 - 0.2, y1 - 0.08)):
        box((xc - 0.017, (ya + yb) / 2, LZ0 + 0.008), (0.005, yb - ya, 0.004), "polish", bevel=0.0)   # its edge worn
    k = round((y1 - y0) / 0.07)
    for j in range(k):
        for sx in (-1, 1):
            rivet((xc + sx * 0.01, y0 + 0.035 + (y1 - y0 - 0.07) * j / (k - 1), LZ0 + 0.009), 0.0075, "head")
for x0, x1 in ((-0.42, -0.3), (-0.12, -0.02), (0.3, 0.42)):     # the lid's front edge knocked bright, broken
    box(((x0 + x1) / 2, CS - 0.025 + 0.004, LZ0 + 0.001), (x1 - x0, 0.007, 0.004), "polish", bevel=0.0)


def lid_frame(x, y):
    """Where a part sits flat on the lid at (x, y): its height and the lid's tilt there."""
    z = lid_z(x, y)
    s = math.atan((LZ1 - LZ0) / L_IN)
    return z, (0, 0, 0)                                # (flat since round 7)
    dx, dy = HX + 0.025 - abs(x), HY + 0.025 - abs(y)
    if min(dx, dy) >= L_IN:
        return z, (0, 0, 0)
    if dy < dx:                                       # on the north or south hip: tilted about x
        return z, ((s if y < 0 else -s), 0, 0)
    return z, (0, (-s if x < 0 else s), 0)


# two inspection covers: a raised plate bolted round its edge, a lifting handle
for cx, cy, w, h in ((-0.1, -0.385, 0.2, 0.11), (-0.42, -0.06, 0.11, 0.2)):
    z, rot = lid_frame(cx, cy)
    cv = empty("cover", loc=(cx, cy, z), rot=rot)
    box((0, 0, 0.009), (w, h, 0.018), "lid", bevel=0.004, parent=cv)
    for sx in (-1, 1):
        for k in range(4):
            f = -0.5 + (k + 0.5) / 4
            bolt((sx * (w / 2 - 0.016), f * (h - 0.03), 0.021), 0.009, 0.008, parent=cv)
            bolt((f * (w - 0.03), sx * (h / 2 - 0.016), 0.021), 0.009, 0.008, parent=cv)
    hl = (w * 0.45, 0) if w > h else (0, h * 0.45)
    for s_ in (-1, 1):
        box((s_ * hl[0] * 0.5, s_ * hl[1] * 0.5, 0.032), (0.012, 0.012, 0.026), "steel", bevel=0.002, parent=cv)
    box((0, 0, 0.046), (hl[0] + 0.012, hl[1] + 0.012, 0.01), "polish", bevel=0.002, parent=cv)

# the wellhead: ONE round boss, bolted down through its foot flange and its cover, a hex plug
# and a vent cock in the cover, its stencilled number on its side
BOSS_TOP = BOSS_TOP_Z
bx_, by_ = BOSS_C.x, BOSS_C.y
cyl((bx_, by_, (BOSS_Z0 + BOSS_TOP) / 2), BOSS_R, BOSS_TOP - BOSS_Z0, "boss", verts=72, bevel=0.01)
ring((bx_, by_, BOSS_Z0 + 0.013), BOSS_R + 0.04, BOSS_R - 0.005, 0.026, "rail", verts=72, bevel=0.005)  # foot flange
for k in range(12):
    t = 360 * (k + 0.5) / 12
    p = Vector(polar(BOSS_R + 0.022, t, BOSS_Z0 + 0.031)) + BOSS_C
    bolt(tuple(p), 0.014, 0.013)
ring((bx_, by_, BOSS_TOP + 0.008), BOSS_R + 0.022, BOSS_R - 0.03, 0.02, "rail", verts=72, bevel=0.005)   # cover rim
cyl((bx_, by_, BOSS_TOP + 0.006), BOSS_R - 0.028, 0.012, "captop", verts=72, bevel=0.003)               # the cover
for k in range(10):
    t = 360 * (k + 0.5) / 10
    bolt(tuple(Vector(polar(BOSS_R - 0.004, t, BOSS_TOP + 0.022)) + BOSS_C), 0.012, 0.011)
for a0, a1 in ((215, 240), (290, 310)):                    # the cover rim worn bright, broken
    arc_band(BOSS_R + 0.023, BOSS_R + 0.004, BOSS_TOP + 0.018, 0.006, a0, a1, "polish", centre=(bx_, by_))
ring((bx_, by_, BOSS_TOP + 0.022), 0.065, 0.04, 0.022, "rail", verts=40, bevel=0.004)   # (its centre: the hose, 9.)
cyl((bx_ + 0.07, by_ + 0.05, BOSS_TOP + 0.03), 0.016, 0.036, "steel", verts=16, bevel=0.003)              # vent cock
box((bx_ + 0.07, by_ + 0.05 + 0.02, BOSS_TOP + 0.05), (0.008, 0.045, 0.008), "steel", bevel=0.0)

# two lifting lugs on the lid, on its north-west and south-east, each upright in its
# diagonal's plane so it draws at the camera's angle (never tilted to face the camera)
for (lx, ly), a in (((-0.44, 0.42), 135), ((0.655, -0.47), -45)):
    t = math.radians(a)
    z, rot = lid_frame(lx, ly)
    box((lx, ly, z + 0.01), (0.09, 0.07, 0.024), "steel", rot=(0, 0, t), bevel=0.006)
    lug = empty("lug", loc=(lx, ly, z + 0.05), rot=(math.pi / 2, 0, t))
    box((0, -0.01, 0), (0.08, 0.045, 0.024), "steel", bevel=0.008, parent=lug)
    torus((0, 0.028, 0), 0.03, 0.011, "rail", parent=lug, seg=24)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.03, minor_radius=0.0115, location=(0, 0.028, 0),
                                     major_segments=24, minor_segments=8)
    _top = bpy.context.active_object
    _bm = bmesh.new()
    _bm.from_mesh(_top.data)
    bmesh.ops.delete(_bm, geom=[v for v in _bm.verts if v.co.y < 0.017], context="VERTS")   # (local to the torus)
    _bm.to_mesh(_top.data)
    _bm.free()
    _finish(_top, "polish", "static", bevel=0, smooth=True, parent=lug)

# the maker's plate: brass, riveted to the south face's upper course
MP = empty("makers", loc=(0.0, -HY - BEAT - 0.006, 0.65), rot=(math.pi / 2, 0, 0))
box((0, 0, 0), (0.15, 0.09, 0.01), "brass", bevel=0.003, parent=MP)
for sx in (-1, 1):
    for sy in (-1, 1):
        rivet((sx * 0.06, sy * 0.032, 0.006), 0.008, parent=MP)
box((0, 0.012, 0.006), (0.1, 0.012, 0.003), "patch", bevel=0.0, parent=MP)          # its stamped name
box((0, -0.014, 0.006), (0.075, 0.008, 0.003), "patch", bevel=0.0, parent=MP)

# ---------------------------------------------------------------- 4. the copper straps

def copper_strap(sx, sy):
    """A wide copper strap from the anchor's block up onto a lug on the casing's corner
    angle, on the diagonal: the casing clamped down. Ribbed across like braid."""
    d = Vector((sx, sy, 0)).normalized()
    a_, b_, _, _ = E8[{(-1, -1): 0, (1, -1): 2, (1, 1): 4, (-1, 1): 6}[(sx, sy)]]
    cut = d.dot((a_ + b_) / 2)                                      # the corner cut's middle, along the diagonal
    p0 = d * (AB * SQ2 - 0.17) + Vector((0, 0, 0.187))              # on the block's inner shoulder
    p1 = d * (cut + 0.076) + Vector((0, 0, 0.255))                  # on the lug
    v = p1 - p0
    rot = facing(v)
    box(tuple((p0 + p1) / 2), (0.1, 0.014, v.length + 0.03), "copper", rot=rot, bevel=0.004)
    n = 4
    for k in range(n):
        q = p0 + v * ((k + 0.5) / n) + Vector((0, 0, 0.01))
        box(tuple(q), (0.102, 0.008, 0.012), "copper", rot=rot, bevel=0.002)
    bolt(tuple(p0 + Vector((0, 0, 0.012))), 0.018, 0.016, "steel")
    t = math.atan2(d.y, d.x)
    box(tuple(d * (cut + TH + 0.036) + Vector((0, 0, 0.245))), (0.07, 0.12, 0.08), "anchor", rot=(0, 0, t), bevel=0.01)
    bolt(tuple(p1 + Vector((0, 0, 0.016))), 0.018, 0.016, "steel")


# two, on the south-east and north-west: on the other diagonal each would run through the
# north or the south riser's stand (round 7's clash check: both did in round 6)
for sx, sy in ((1, -1), (-1, 1)):
    copper_strap(sx, sy)

# ---------------------------------------------------------------- 5. the burst disc

# on the lid's east hip, north of east (spec 3.2: the north-east shoulder): a flanged nozzle
# up off the lid, the brass holder and its bulging disc on it, level, its relief line (8.)
# off the holder's side
BD_X, BD_Y = 0.40, 0.20
BD_Z = lid_z(BD_X, BD_Y)
place(Vector((BD_X, BD_Y, BD_Z - 0.01)), Vector((BD_X, BD_Y, BD_Z + 0.012)), 0.07, 0.07, "rail", "static")
place(Vector((BD_X, BD_Y, BD_Z)), Vector((BD_X, BD_Y, BD_Z + 0.07)), 0.045, 0.045, "steel", "static")
BD_H = BD_Z + 0.07                                       # the holder's foot
cyl((BD_X, BD_Y, BD_H + 0.012), 0.08, 0.024, "steel", verts=40, bevel=0.004)                 # its seat flange
cyl((BD_X, BD_Y, BD_H + 0.04), 0.068, 0.034, "brass", verts=40, bevel=0.006)                 # the holder
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.056, location=(BD_X, BD_Y, BD_H + 0.055), segments=32, ring_count=12)
dome = bpy.context.active_object
dome.scale.z = 0.35
bpy.ops.object.transform_apply(scale=True)
_finish(dome, "brass", "static", bevel=0, smooth=True)                                       # the disc, bulging
for k in range(6):
    u = 2 * math.pi * (k + 0.5) / 6
    bolt((BD_X + 0.072 * math.cos(u), BD_Y + 0.072 * math.sin(u), BD_H + 0.027), 0.01, 0.009)
cyl((BD_X, BD_Y, BD_H + 0.075), 0.012, 0.01, "polish", verts=12, bevel=0.0)                  # its telltale pin


# ---------------------------------------------------------------- 7. the riser, per direction

# One riser design in every direction (round 2): a stand rising off the plinth (round 7;
# the round collar's apron before it) through a flanged foot, a gate valve on the stand with its handwheel upright, a cast
# elbow, a horizontal run to the connection with a flanged joint and, where the run is
# long, a support bracket down to the plate, a short reducer, and the flange collar at the
# footprint's edge. The pipe is the furnace's loop pipe in scale; only the mouth's collar
# is vanilla's size, because a vanilla pipe has to meet it.
H = 0.47                              # the run's axis height: the mouth's collar clears the anchors' feet
R_PIPE = 0.08                         # the riser's pipe (round 11: up from 0.065, 10 px; the north and
                                      # south stands' foot flanges, r 0.098, set the most it can be)
R_JOINT = R_PIPE + 0.036              # a bolted flange on it (the furnace's: pipe + 0.036)
COLLAR_T = 0.032
# the mouth's flange collar and its open bore, sized to the vanilla flange it meets
# (measure.py measures both): east and west 0.34, which draws 49 px tall against vanilla's
# 50; north and south 0.26 with a bolting lug either side out to 0.40, which draws 51 px wide
# against vanilla's joint ring of 51, and short enough that the south mouth stays on the
# footprint (its lowest row on the tile edge, where vanilla's ring ends)
R_COLLAR = {"north": 0.26, "east": 0.34, "south": 0.26, "west": 0.34}
LUG_R = 0.40
VAN_NS = 9.5 / 64                     # vanilla's joint ring: centred 9.5 px past the tile edge
VAN_EW = 2 / 64                       # vanilla's horizontal tube: about 2 px above its tile's centre
EW_FACE = 1.0                         # the east and west collars' faces: on the edge (inside it, a 1 px gap)
# the mouth (its collar's middle) and the way the run points, per direction
MOUTH = {
    "north": dict(at=Vector((0.5, 1 + VAN_NS - H / 2, H)), out=Vector((0, 1, 0))),
    "east": dict(at=Vector((EW_FACE - COLLAR_T / 2, -0.5 + VAN_EW - H / 2, H)), out=Vector((1, 0, 0))),
    "south": dict(at=Vector((-0.5, -1 + VAN_NS - H / 2, H)), out=Vector((0, -1, 0))),
    "west": dict(at=Vector((-EW_FACE + COLLAR_T / 2, 0.5 + VAN_EW - H / 2, H)), out=Vector((-1, 0, 0))),
}
# where each stand rises (chosen in rounds 2 and 3 against the round collar, and kept: the
# casing of round 7 is sized to clear them): on the run's line, clear of the anchors' blocks (north and south are each other turned half round; east sits where
# vanilla's tube line puts it, over the south-east anchor). The west run's line crosses the
# collar's west flank, where a stand would stand in its shade and behind it, so the west
# stand rises off the apron's south-west, in view, and its run turns north along the flank
# and then west to the connection: the same assembly with one more elbow (round 3)
STAND = {"north": (0.5, 0.67), "east": (0.30, None), "south": (-0.5, -0.67), "west": (-0.733, -0.267)}
# a bracket under the long runs: where, and along which way the pipe runs there
SUPPORT = {"east": ((0.52, None), (1, 0)), "south": ((-0.5, -0.80), (0, -1)), "west": ((-0.733, 0.15), (0, 1))}
VALVE_Z = 0.3                         # the gate valve's middle, on the stand
# the handwheel's stem, toward the camera and clear of the anchors in each direction, so the
# wheel stands upright in its own plane and draws as an ellipse at the lifting eyes' angle
STEM = {"north": Vector((-1, -1, 0)).normalized(), "east": Vector((-1, -1, 0)).normalized(),
        "south": Vector((1, -1, 0)).normalized(), "west": Vector((-1, -1, 0)).normalized()}
R_WHEEL = 0.075                       # the handwheels (round 3: larger, a bright worn rim)
R_HOLE = R_PIPE - 0.012               # the mouth's opening: the pipe's own bore, in a flange face
assert H - max(R_COLLAR.values()) > 0.11 + 0.01, "the mouth's flange collar would touch an anchor's foot"
assert H - R_PIPE > A_TOP + 0.05, "the run would touch an anchor's bolt"


def joint(at, axis, group, n=8):
    """A bolted flange pair across the pipe at `at`, square to axis (the furnace's flange)."""
    a = axis.normalized()
    for o in (-0.011, 0.011):
        place(at + a * (o - 0.009), at + a * (o + 0.009), R_JOINT, R_JOINT, "steel", group, bevel=0.003)
    q = a.to_track_quat("Z", "Y" if abs(a.z) < 0.9 else "X")
    for k in range(n):
        u = 2 * math.pi * (k + 0.5) / n
        p = at + q @ Vector(((R_PIPE + 0.022) * math.cos(u), (R_PIPE + 0.022) * math.sin(u), 0))
        place(p - a * 0.029, p + a * 0.029, 0.009, 0.009, "head", group, verts=6, bevel=0.0)


def weld(at, axis, group, r=R_PIPE):
    torus(tuple(at), r + 0.001, 0.007, "seam", group, rot=facing(axis), seg=32)


def riser(d):
    """The riser facing d: its own objects in group riser-<d>."""
    g = f"riser-{d}"
    at, out = MOUTH[d]["at"], MOUTH[d]["out"]
    side = Vector((-out.y, out.x, 0))
    sx, sy = STAND[d]
    base = Vector((sx, at.y if sy is None else sy, 0))       # the stand's foot
    zb = ground_z(base.x, base.y)
    up = Vector((0, 0, 1))
    # the stand's foot: a flange bolted to the plinth, a weld boss, the pipe rising off it
    # (round 7: r 0.098, from 0.105, and seated on the ground rather than sunk into it -- the
    # north and south ones stood 0.005 into an anchor's foot)
    place(base + up * zb, base + up * (zb + 0.024), 0.098, 0.098, "steel", g, bevel=0.004)
    bolt_ring(base + up * (zb + 0.028), up, 0.089, 8, 0.009, g, phase=0.5)
    place(base + up * (zb + 0.024), base + up * (zb + 0.05), R_PIPE + 0.012, R_PIPE + 0.012, "pipe", g)
    weld(base + up * (zb + 0.05), up, g)
    # the gate valve: a squat body on the stand, flanged above and below, its bonnet and stem
    # out toward the camera and the handwheel upright on the stem's end
    stem = STEM[d]
    vz = Vector((base.x, base.y, VALVE_Z))
    joint(vz - up * 0.07, up, g)
    joint(vz + up * 0.07, up, g)
    place(vz - up * 0.055, vz + up * 0.055, R_PIPE + 0.028, R_PIPE + 0.028, "valve", g, bevel=0.008)
    place(vz, vz + stem * 0.1, 0.035, 0.03, "valve", g, bevel=0.005)                      # bonnet
    place(vz + stem * 0.1, vz + stem * 0.135, 0.022, 0.022, "steel", g, bevel=0.003)       # gland
    place(vz + stem * 0.13, vz + stem * 0.2, 0.007, 0.007, "polish", g, verts=12, bevel=0.0)    # stem
    whl = empty(f"wheel-{d}", loc=tuple(vz + stem * 0.195), rot=facing(stem))
    torus((0, 0, 0), R_WHEEL, 0.013, "polish", g, parent=whl, seg=40)                    # the rim, worn bright
    for k in range(4):
        t = math.radians(45 + k * 90)
        box((R_WHEEL / 2 * math.cos(t), R_WHEEL / 2 * math.sin(t), 0), (R_WHEEL, 0.012, 0.009), "valve", g,
            rot=(0, 0, t), bevel=0.0, parent=whl)                                          # its spokes
    cyl((0, 0, 0), 0.018, 0.02, "steel", g, verts=6, bevel=0.0, parent=whl)                 # its nut
    # the run: up the stand, through a welded elbow, along the run's line (on the west, round
    # the collar's flank first) to the mouth's neck
    corner = Vector((base.x, base.y, H))
    m0 = at - out * (COLLAR_T / 2 + 0.05)                    # the neck's start, behind the collar
    path = [vz + up * 0.09, corner]
    if d == "west":
        path.append(Vector((base.x, at.y, H)))               # the turn west, onto vanilla's tube line
    path.append(m0)
    pipe([base + up * (zb + 0.05), vz - up * 0.09], R_PIPE, "pipe", group=g, bend=0.0)
    pipe(path, R_PIPE, "pipe", group=g, bend=0.1)
    # each elbow welded in at both ends
    for i in range(1, len(path) - 1):
        for nb in (path[i - 1], path[i + 1]):
            v = (nb - path[i]).normalized()
            weld(path[i] + v * 0.1, v, g)
    # a flanged joint on the longest straight leg
    legs = [(path[i], path[i + 1]) for i in range(1, len(path) - 1)]
    p0, p1 = max(legs, key=lambda ab: (ab[1] - ab[0]).length)
    if (p1 - p0).length > 0.3:
        joint(p0 + (p1 - p0) * 0.5, (p1 - p0).normalized(), g)
    # a support bracket under a long run: a post off the plate, a saddle and a strap
    if d in SUPPORT:
        (px, py), (ux, uy) = SUPPORT[d]
        p = Vector((px, at.y if py is None else py, 0))
        lv = Vector((ux, uy, 0))
        zp = ground_z(p.x, p.y)
        top = H - R_PIPE - 0.012
        ang = math.atan2(lv.y, lv.x)
        box(tuple(p + up * (zp + 0.0125)), (0.11, 0.09, 0.024), "rail", g, rot=(0, 0, ang), bevel=0.004)
        for s_ in (-1, 1):
            bolt(tuple(p + Vector((-lv.y, lv.x, 0)) * s_ * 0.035 + up * (zp + 0.028)), 0.011, 0.01, group=g)
        box(tuple(p + up * ((zp + top) / 2)), (0.03, 0.03, top - zp), "rail", g, bevel=0.003)
        box(tuple(p + up * (top + 0.006)), (0.05, 0.1, 0.012), "rail", g, rot=(0, 0, ang), bevel=0.003)
        place(Vector((p.x, p.y, H)) - lv * 0.012, Vector((p.x, p.y, H)) + lv * 0.012, R_PIPE + 0.01,
              R_PIPE + 0.01, "rail", g, bevel=0.003)                                        # its strap
    # the mouth: the pipe welded into a neck boss on the back of the flange collar, and the
    # collar's face a flange around the pipe's own bore (round 3: a flanged pipe end, not a hole)
    face = at + out * COLLAR_T / 2
    rc = R_COLLAR[d]
    weld(m0, out, g)
    place(m0, at - out * COLLAR_T / 2, R_PIPE + 0.022, R_PIPE + 0.03, "worn", g)            # the neck boss
    collar = ring(tuple(at), rc, R_HOLE, COLLAR_T, "worn", g, verts=64, bevel=0.006, rot=facing(out))
    PARTS.setdefault(f"mouth-{d}", []).append(collar)
    # (round 7) the flange collar casts no shadow, in the plate or the shadow sheet: a disc
    # of vanilla's joint size, standing on the footprint's edge, threw a hard black oval
    # past the east mouth (a hole, Liam) and onto the plate inside the west one
    if d in ("north", "south"):
        # the bolting lugs, either side, level with the axis
        for sgn in (-1, 1):
            c = at + side * sgn * (rc + LUG_R - 0.02) / 2
            lug = box(tuple(c), (abs(side.x) * (LUG_R - rc + 0.02) + abs(out.x) * COLLAR_T,
                                 abs(side.y) * (LUG_R - rc + 0.02) + abs(out.y) * COLLAR_T, 0.1), "steel", g,
                      bevel=0.006)
            PARTS[f"mouth-{d}"].append(lug)
            bolt(tuple(at - out * (COLLAR_T / 2 + 0.006) + side * sgn * (LUG_R - 0.035)), 0.015, 0.012, "steel", g,
                 rot=facing(-out))
    # its raised face round the bore, machined, and the bore itself, dark a short way in
    ring(tuple(face + out * 0.002), R_PIPE + 0.05, R_HOLE, 0.006, "rail", g, verts=48, bevel=0.002, rot=facing(out))
    place(face - out * 0.12, face + out * 0.004, R_HOLE + 0.001, R_HOLE + 0.001, "bore", g, bevel=0.0)
    bolt_ring(at - out * (COLLAR_T / 2 + 0.006), -out, rc - 0.03, 10, 0.014, g, phase=0.5)
    # the face worn bright only in two short stretches, between the raised face and the rim
    q = out.to_track_quat("Z", "Y")
    for a0, a1 in ((200, 235), (300, 320)):
        rw = (rc + R_PIPE + 0.05) / 2
        pts = [face - out * 0.002 + q @ Vector((rw * math.cos(math.radians(a0 + (a1 - a0) * k / 8)),
                                                rw * math.sin(math.radians(a0 + (a1 - a0) * k / 8)), 0))
               for k in range(9)]
        pipe(pts, 0.006, "polish", group=g, bend=0.0)


for d in DIRS:
    riser(d)
    for o in PARTS[f"mouth-{d}"]:
        o.visible_shadow = False              # (round 7: see the collar, above)

# ---------------------------------------------------------------- 8. the pipework and the sight glass

# Round 7: orthogonal pipework, as vanilla's chemical plant and oil refinery carry it --
# straight runs up the casing's faces and across its lid, square elbows, no ring mains. All
# of it is fixed, the same objects in every direction, and clear of every direction's riser
# (--check measures it). Everything rests on something: wall clips, lid stand-offs, saddles.
#
# Round 11 (Liam, after signing off round 10: "the pipes and hoses on the gas pump need to be
# bulkier -- see the factorio sprites"): every bore measured against vanilla's at the same
# 64 px a tile (base/graphics/entity: chemical plant 17-22 px across its pipes, pump and
# offshore pump hoses 18-21 px with 24-28 px cuffs, pumpjack 6-9 px on its small lines and
# 12-16 on its large, flanges 2-4 px proud and 3-4 px deep). Ours were 2-4 px. Now three
# bores: the main line (D1 and the header) 0.095 a side, 12 px; the sight glass 0.12, 15 px,
# in flanges 20 px across; small bore (E1, the bypass, the relief line, the vent stack) 0.04
# to 0.075, 5-10 px. Fewer, fatter runs: the doubled pair (D1, D2) is one main, M3 and W1
# are gone, and the bypass and the drain moved onto D1:
#
#   - D1, the main: up out of the plinth on a bolted foot in front of the south face (a
#     drain cock on the foot), a gate valve with a bypass loop round it (two tees, a loop out
#     to the east, its own small gate), clipped to the face, over the lid's edge, east south
#     of the wellhead, and north beside the compressor housing to the header's east end;
#   - the header: west from there along the lid's north half, the sight glass inline in it
#     between two heavy flanges, and up at its west end into the vent stack;
#   - E1, the east crossing: up the east face from its valve pad into the compressor
#     housing's east face;
#   - the burst disc's relief line: off its nozzle, east over the lid's edge, down the east
#     face on clips, out over the plate and down into a vent cap.
FACE_S = -HY                                    # the south face
CH_X0, CH_X1, CH_Y0, CH_Y1 = 0.33, 0.60, -0.40, 0.08   # (round 10) the compressor housing's foot on the lid (9.);
                                                # (round 12) its west face in from 0.30, for D1's fatter north run
CH_TOP, CH_B = 1.06, 0.035                         # its roof, and how far its walls lean in (9.)
HZ = 0.97                                       # the lid runs' axes (round 11: up from 0.875; round 12: 0.95 -> 0.97)
H_Y, H_R = 0.30, 0.12                           # the header: its line and bore (round 11: 0.032 -> 0.095; round 12: 0.12)
D1_X, D1_R = -0.17, 0.125                       # D1: up the south face, the main (round 12: 16 px)
D1_OFF = 0.175                                  # its axis off the face: clear of the top flange
D1_Y = FACE_S - D1_OFF
D1_EY, D1_NX = -0.34, 0.19                      # its east run's line (south of the wellhead), its north run's
E1_Y, E1_R, E1_X = -0.01, 0.085, 0.79
RL_R, RL_X = 0.05, 0.77
ZL = 0.19                                       # the crossings' axes, over the plinth
CLIP_Z = (0.45, 0.655)                          # wall clips: clear of the course bands and the top flange
UP = Vector((0, 0, 1))
NORTH, SOUTH, EAST, WEST = Vector((0, 1, 0)), Vector((0, -1, 0)), Vector((1, 0, 0)), Vector((-1, 0, 0))


def flange_dims(r):
    """A flange on a pipe of radius r, vanilla's proportions: (proud, each plate's thickness,
    the gap between a pair) -- 2-4 px proud and a pair 3-4 px deep on a main."""
    return max(0.024, 0.34 * r), max(0.007, 0.18 * r), max(0.004, 0.05 * r)


def run(pts, r, mat="line", welds=True):
    """A rigid run through pts, each corner a short square elbow welded in at both ends."""
    pts = [Vector(p) for p in pts]
    e = max(0.03, 1.5 * r)
    pipe(pts, r, mat, bend=e)
    if welds:
        for i in range(1, len(pts) - 1):
            for nb in (pts[i - 1], pts[i + 1]):
                v = (nb - pts[i]).normalized()
                torus(tuple(pts[i] + v * e), r + 0.001, max(0.005, 0.07 * r), "seam", rot=facing(v), seg=32)


def tee(p, r, mat="line"):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=tuple(p), segments=32, ring_count=16)
    _finish(bpy.context.active_object, mat, "static", bevel=0, smooth=True)


def flange_pair(at, axis, r, group="static", n=None):
    """A bolted flange pair across a pipe of radius r at `at`, square to axis: heavy, as
    vanilla's are, its bolts standing proud of both plates."""
    a = axis.normalized()
    pr, t, gap = flange_dims(r)
    n = n or (6 if r < 0.05 else 8)
    for s_ in (-1, 1):
        o = s_ * (gap + t) / 2
        place(at + a * (o - t / 2), at + a * (o + t / 2), r + pr, r + pr, "steel", group, bevel=min(0.004, t / 3))
    q = a.to_track_quat("Z", "Y" if abs(a.z) < 0.9 else "X")
    br = max(0.006, 0.075 * r)
    for k in range(n):
        u = 2 * math.pi * (k + 0.5) / n
        p = at + q @ Vector(((r + pr * 0.6) * math.cos(u), (r + pr * 0.6) * math.sin(u), 0))
        place(p - a * (t + gap / 2 + 0.008), p + a * (t + gap / 2 + 0.008), br, br, "head", group, verts=6, bevel=0.0)


def blind(at, axis, r):
    """A blind flange on a pipe's end at `at`, facing along axis."""
    a = axis.normalized()
    pr, t, gap = flange_dims(r)
    place(at - a * 0.004, at + a * t, r + pr, r + pr, "steel", "static", bevel=0.003)
    place(at + a * t, at + a * (t + 0.012), r + pr * 0.5, r + pr * 0.5, "rail", "static", bevel=0.003)
    bolt_ring(at + a * t, a, r + pr * 0.6, 8, max(0.007, 0.075 * r), "static", phase=0.5, h=0.01)


def cock(at, direction, group="static", k=1.0):
    """A small drain or vent cock: a stub, a square plug and a short lever."""
    d = direction.normalized()
    place(at, at + d * 0.035 * k, 0.011 * k, 0.011 * k, "brass", group, verts=12, bevel=0.0)
    box(tuple(at + d * 0.04 * k), (0.02 * k, 0.02 * k, 0.02 * k), "brass", group, rot=facing(d), bevel=0.003)
    side = d.cross(UP) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    place(at + d * 0.04 * k, at + d * 0.04 * k + side.normalized() * 0.05 * k, 0.005 * k, 0.005 * k, "steel", group,
          verts=8, bevel=0.0)


def wheel(at, stem, r, tube=0.011):
    """A handwheel upright on a horizontal stem: in the stem's plane, never camera-facing."""
    w = empty("handwheel", loc=tuple(at), rot=facing(stem))
    torus((0, 0, 0), r, tube, "polish", parent=w, seg=32)                    # the rim, worn bright by hands
    for k in range(4):
        t = math.radians(45 + k * 90)
        box((r / 2 * math.cos(t), r / 2 * math.sin(t), 0), (r, 0.01, 0.008), "valve", rot=(0, 0, t), bevel=0.0,
            parent=w)
    cyl((0, 0, 0), 0.015, 0.016, "steel", verts=6, bevel=0.0, parent=w)


def gate(p, axis, r, stem, wr=0.04):
    """A flanged gate valve on a line at p, its bonnet out along a horizontal stem and the
    handwheel upright on the stem's end. Returns how far it reaches along the line."""
    a = axis.normalized()
    pr, t, gap = flange_dims(r)
    half = max(0.03, 0.45 * r)
    place(p - a * half, p + a * half, r * 1.3 + 0.006, r * 1.3 + 0.006, "valve", "static", bevel=0.006)
    reach = half + gap / 2 + t
    for s_ in (-1, 1):
        flange_pair(p + a * s_ * reach, a, r)
    bl = max(0.055, 0.7 * r) + r * 1.3
    place(p, p + stem * bl, r * 0.75 + 0.004, r * 0.6 + 0.002, "valve", "static", bevel=0.004)          # bonnet
    place(p + stem * bl, p + stem * (bl + 0.016), r * 0.55 + 0.004, r * 0.55 + 0.004, "steel", "static",
          bevel=0.002)                                                                                # gland
    place(p + stem * (bl + 0.016), p + stem * (bl + 0.05), 0.007, 0.007, "polish", "static", verts=10, bevel=0.0)
    wheel(p + stem * (bl + 0.045), stem, wr)
    return reach + gap / 2 + t


def wall_clip(c, nrm, r, axis=UP):
    """A stand-off from a casing face (normal nrm) to a pipe at c: a pad welded to the plate,
    an arm, and a strap round the pipe."""
    ang = math.atan2(nrm.y, nrm.x)
    d = (c - Vector((0, 0, c.z))).dot(nrm)                          # the pipe's axis off the origin
    face = c - nrm * (d - wall_d(nrm))                              # the point on the face behind it
    box(tuple(face + nrm * 0.008), (0.022, max(0.055, 1.2 * r), max(0.045, 0.9 * r)), "rail", rot=(0, 0, ang),
        bevel=0.004)
    a0, a1 = face + nrm * 0.016, c - nrm * (r + 0.004)
    if (a1 - a0).dot(nrm) > 0.004:
        box(tuple((a0 + a1) / 2), ((a1 - a0).length, max(0.018, 0.4 * r), max(0.013, 0.3 * r)), "rail",
            rot=(0, 0, ang), bevel=0.003)
    sl = max(0.01, 0.16 * r)
    place(c - axis * sl, c + axis * sl, r + 0.01, r + 0.01, "rail", "static", bevel=0.003)
    bolt(tuple(face + nrm * 0.02 + Vector((0, 0, 0.3 * max(0.045, 0.9 * r)))), 0.009, 0.008, rot=(0, math.pi / 2, ang))


def wall_d(nrm):
    """How far the casing's face with normal nrm lies from its centre (plus a plate's bulge)."""
    return {(1, 0): CE, (-1, 0): -CW, (0, 1): CN, (0, -1): -CS}[(round(nrm.x), round(nrm.y))] + 0.004


def lid_stand(c, r, axis):
    """A stand-off from the lid up to a run at c: a foot welded to the lid, a post, a saddle
    and a strap."""
    z0 = lid_z(c.x, c.y)
    top = c.z - r - 0.004
    ang = math.atan2(axis.y, axis.x)
    box((c.x, c.y, z0 + 0.005), (max(0.06, 1.1 * r), max(0.06, 1.3 * r), 0.012), "rail", rot=(0, 0, ang),
        bevel=0.003)
    box((c.x, c.y, (z0 + top) / 2), (max(0.022, 0.35 * r), max(0.04, 1.1 * r), top - z0), "rail", rot=(0, 0, ang),
        bevel=0.003)
    sl = max(0.01, 0.16 * r)
    place(c - axis * sl, c + axis * sl, r + 0.01, r + 0.01, "rail", "static", bevel=0.003)


def valve_pad(c, r, top):
    """A bolted valve pad on the plate or the plinth, where a line comes up out of the
    ground: a block, a flanged valve body up to `top`, a cock on its side."""
    g0 = ground_z(c.x, c.y)
    w = max(0.1, 2 * r)
    box((c.x, c.y, g0 + 0.025), (w, w, 0.05), "anchor", bevel=0.008)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bolt((c.x + sx * (w / 2 - 0.014), c.y + sy * (w / 2 - 0.014), g0 + 0.052), 0.009, 0.008, "head")
    place(Vector((c.x, c.y, g0 + 0.05)), Vector((c.x, c.y, top)), r * 1.25 + 0.008, r * 1.25 + 0.008, "valve", "static",
          bevel=0.005)
    flange_pair(Vector((c.x, c.y, top)), UP, r)


# -- D1, the main: off the plinth in front of the south face, up past its gate and bypass,
#    over the lid's edge, east south of the wellhead, north beside the compressor housing
D1_FOOT = Vector((D1_X, D1_Y, PL_T))
pr_, t_, g_ = flange_dims(D1_R)
place(D1_FOOT, D1_FOOT + UP * 0.03, D1_R + pr_ + 0.012, D1_R + pr_ + 0.012, "steel", "static", bevel=0.005)  # its foot
bolt_ring(D1_FOOT + UP * 0.034, UP, D1_R + pr_ * 0.6 + 0.006, 8, 0.012, "static", phase=0.5)
place(D1_FOOT + UP * 0.03, D1_FOOT + UP * 0.07, D1_R + 0.014, D1_R + 0.012, "line", "static")              # weld boss
cock(Vector((D1_X, D1_Y - D1_R - 0.012, PL_T + 0.05)), SOUTH, k=1.4)                                     # its drain cock
D1_C1 = Vector((D1_NX, D1_EY, HZ))
D1_END = Vector((D1_NX, H_Y, HZ))
run([D1_FOOT + UP * 0.07, Vector((D1_X, D1_Y, HZ)), Vector((D1_X, D1_EY, HZ)), D1_C1, D1_END], D1_R, mat="line_green")
tee(D1_END, D1_R + 0.006, "line_green")                     # its cast elbow into the header, a boss for hose 1
GATE_Z = 0.50
gate(Vector((D1_X, D1_Y, GATE_Z)), UP, D1_R, SOUTH, wr=0.08)
# the bypass: set-on branches below and above the gate (round 12: no tees, the main's too fat
# for three on the face), a loop out to the east along the face, its own small gate valve
BY_X, BY_R = D1_X + 0.2, 0.055
BY_Z = (0.30, 0.70)
run([Vector((D1_X, D1_Y, BY_Z[0])), Vector((BY_X, D1_Y, BY_Z[0])), Vector((BY_X, D1_Y, BY_Z[1])),
     Vector((D1_X, D1_Y, BY_Z[1]))], BY_R)
for z in BY_Z:
    torus((D1_X + D1_R - 0.004, D1_Y, z), BY_R + 0.002, 0.008, "seam", rot=facing(EAST), seg=24)  # welded on
gate(Vector((BY_X, D1_Y, GATE_Z)), UP, BY_R, SOUTH, wr=0.05)
# on the lid: a stand under the east run and one under the north run
lid_stand(Vector((0.07, D1_EY, HZ)), D1_R, EAST)
lid_stand(Vector((D1_NX, 0.12, HZ)), D1_R, NORTH)
# the pressure gauge on a tee on D1's east run: a siphon, a brass case, its dial level (a level
# circle reads at this camera)
GX = -0.03
tee(Vector((GX, D1_EY, HZ)), D1_R + 0.008, "line_green")
gb_ = Vector((GX, D1_EY, HZ + D1_R))
place(gb_, gb_ + Vector((0, 0, 0.03)), 0.014, 0.014, "brass_g", "static", verts=12, bevel=0.0)
torus(tuple(gb_ + Vector((0, 0, 0.045))), 0.02, 0.007, "brass_g", rot=(math.pi / 2, 0, 0), seg=16)
gc = gb_ + Vector((0, 0, 0.09))
place(gb_ + Vector((0, 0, 0.06)), gc - Vector((0, 0, 0.014)), 0.012, 0.012, "brass_g", "static", verts=12, bevel=0.0)
# (the gas-pump-animation task, a2: Liam, "the gauge face may grow a little") the case 0.075 -> 0.09,
# the dial 0.061 -> 0.075, so the needle's kick reads at 1x
G_R = 0.09
cyl(tuple(gc), G_R, 0.032, "brass_g", verts=40, bevel=0.007)                                           # case
ring(tuple(gc + Vector((0, 0, 0.019))), G_R + 0.001, G_R - 0.015, 0.012, "brass_g", verts=40, bevel=0.002)   # bezel
cyl(tuple(gc + Vector((0, 0, 0.0165))), G_R - 0.014, 0.002, "dial", verts=40, bevel=0.0)                 # dial
# the needle (the gas-pump-animation task): on a pivot at the dial's centre, so it kicks on each
# stroke (10.); at rest exactly where round 13 drew it, 0.7 rad, its middle 0.014 east and 0.01
# north of the centre
NEEDLE_REST = 0.7
NEEDLE = empty("needle-pivot", loc=tuple(gc + Vector((0, 0, 0.019))), rot=(0, 0, NEEDLE_REST))
# (a2) longer and bolder on the grown dial: 0.062 long, its tip 0.053 out, 0.011 wide; a dark hub
box((0.022, 0, 0), (0.062, 0.011, 0.002), "bore", group="needle", bevel=0.0, parent=NEEDLE)  # needle
cyl((0, 0, 0.001), 0.009, 0.003, "bore", group="needle", verts=12, bevel=0.0, parent=NEEDLE)  # its hub

# -- the header, west from D1's elbow along the lid's north half: the sight glass inline, then
#    up at its west end into the vent stack
SG_X0, SG_X1, SG_R = -0.28, 0.02, 0.14          # the glass tube's ends and radius: 0.30 long (round 12: r 0.12 -> 0.14)
SG_FL, SG_FR = 0.034, 0.18                      # its end flanges: thickness, radius
HX0 = -0.47                                     # the header's west end: its elbow up into the vent stack
place(Vector((SG_X1 + SG_FL, H_Y, HZ)), D1_END, H_R, H_R, "line_green", "static")
VS_TOP = 1.29
run([Vector((SG_X0 - SG_FL, H_Y, HZ)), Vector((HX0, H_Y, HZ)), Vector((HX0, H_Y, 1.14))], H_R, mat="line_green")
for x0 in (SG_X0 - SG_FL, SG_X1 + SG_FL):
    weld(Vector((x0 + (-0.004 if x0 < 0 else 0.004), H_Y, HZ)), EAST, "static", r=H_R)

# -- the sight glass (round 9: inline, Liam -- the standing column read as a status lamp; round
#    11: twice the bore; round 12: "hard to tell from the vent grille beside it" -- a bright worn
#    frame round a bluer glass, the front tie-rods gone so no bars cross it, one long glint):
#    a glass tube in the header's own axis between two heavy bolted flanges, two tie-rods
#    behind it; dark empty glass in the plate, its contents (partly filled) the light pass's
SG_A, SG_B = Vector((SG_X0, H_Y, HZ)), Vector((SG_X1, H_Y, HZ))
glass = place(SG_A, SG_B, SG_R, SG_R, "glass", "glass", verts=64, bevel=0.0)
for x0 in (SG_X0 - SG_FL, SG_X1):
    place(Vector((x0, H_Y, HZ)), Vector((x0 + SG_FL, H_Y, HZ)), SG_FR, SG_FR, "worn", "static", verts=64, bevel=0.008)
    inner = SG_X1 if x0 == SG_X1 else SG_X0
    place(Vector((inner - 0.005, H_Y, HZ)), Vector((inner + 0.005, H_Y, HZ)), SG_R + 0.012, SG_R + 0.012, "seam",
          "static", verts=64, bevel=0.0)                                      # its gasket at the glass
    xb = x0 + SG_FL / 2
    for k in range(8):
        u = 2 * math.pi * (k + 0.5) / 8
        p = Vector((xb, H_Y + 0.162 * math.cos(u), HZ + 0.162 * math.sin(u)))
        place(p - EAST * (SG_FL / 2 + 0.01), p + EAST * (SG_FL / 2 + 0.01), 0.012, 0.012, "steel", "static", verts=6,
              bevel=0.0)                                                      # its bolts
# the tie-rods: two, behind the glass from the camera, nutted
for th in (40, 320):
    t_ = math.radians(th)
    o_ = Vector((0, (SG_R + 0.018) * math.cos(t_), (SG_R + 0.018) * math.sin(t_)))
    place(SG_A + o_ - EAST * (SG_FL + 0.014), SG_B + o_ + EAST * (SG_FL + 0.014), 0.008, 0.008, "polish", "static",
          verts=10, bevel=0.0)
    for x_ in (SG_X0 - SG_FL - 0.008, SG_X1 + SG_FL + 0.008):
        cyl((x_, H_Y + o_.y, HZ + o_.z), 0.014, 0.014, "steel", verts=6, rot=(0, math.pi / 2, 0), bevel=0.0)
# the glint: a pale highlight along the tube's top edge, toward the camera
t_ = math.radians(100)
o_ = Vector((0, (SG_R + 0.0005) * math.cos(t_), (SG_R + 0.0005) * math.sin(t_)))
place(SG_A + o_ + EAST * 0.02, SG_B + o_ - EAST * 0.02, 0.011, 0.011, "glint", "static", verts=10, bevel=0.0)
# stands under both flanges, off the lid
for x_ in (SG_X0 - SG_FL / 2, SG_X1 + SG_FL / 2):
    z0 = lid_z(x_, H_Y)
    box((x_, H_Y, (z0 + HZ - SG_FR) / 2 + 0.002), (0.028, 0.09, HZ - SG_FR - z0 + 0.004), "rail", bevel=0.002)
    box((x_, H_Y, z0 + 0.005), (0.06, 0.12, 0.012), "rail", bevel=0.002)
# its contents: drawn only in the light pass, the engine tints them by the vent's gas. Partly
# filled: the liquid below a level 0.6 of the radius under the axis (from this camera about
# two thirds of the window, dark empty glass above it), inside the glass, so the
# layer never leaves it -- a flat surface (its meniscus bright along the front), the body under
# it, a darker band low down, bubbles
FILL_R, FILL_H = SG_R - 0.01, -0.6
assert abs(FILL_R - FILL_R_) < 1e-9 and H_Y == H_Y_FILL and HZ == HZ_FILL, "the fill material's constants are stale"


def _fill_mesh(bm, level=FILL_H):
    n = 48
    a0 = math.asin(level)                                      # where the level meets the wall
    angs = [a0 - (math.pi + 2 * a0) * k / n for k in range(n + 1)]   # round under, from front to back
    sec = [(FILL_R * math.cos(a), FILL_R * math.sin(a)) for a in angs]
    rows = [[bm.verts.new((x, H_Y - c, HZ + z)) for c, z in sec] for x in (SG_X0 + 0.008, SG_X1 - 0.008)]
    for i in range(n):
        bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
    bm.faces.new((rows[0][-1], rows[0][0], rows[1][0], rows[1][-1]))        # the surface
    bm.faces.new(list(reversed(rows[0])))
    bm.faces.new(rows[1])


fill = mesh_object("fill", _fill_mesh, "fill", "glass-fill", bevel=0.0)

# (the gas-pump-animation task) the gas moves: the glass layer is FRAMES frames on the crank's
# loop (10.). Its level lifts with each discharge -- FILL_LIFT of the radius at the needle's
# peak, back to round 13's level by the loop's end -- and bubbles drift west along its surface
# (the only face of the contents this camera sees: the body's near side faces away from it),
# BUB_REPEAT copies of one set along the glass, each moving one copy's length a loop, so the
# loop closes on itself; each bubble shrinks to nothing within BUB_FADE of the glass's ends,
# so none pops in or out, and none reaches the flanges. Neutral white, as the contents are.
FILL_LIFT = 0.16
FILL_X0, FILL_X1 = SG_X0 + 0.008, SG_X1 - 0.008
BUB_REPEAT, BUB_FADE = 2, 0.035
_rb_ = _random.Random(29)
BUBBLES = [(_rb_.random(), _rb_.uniform(-0.07, 0.07), _rb_.uniform(0.009, 0.016)) for _ in range(7)]
M["bubble"] = bpy.data.materials.new("bubble")
M["bubble"].use_nodes = True
_bb = M["bubble"].node_tree.nodes["Principled BSDF"]
_bb.inputs["Base Color"].default_value = (0, 0, 0, 1)
_bb.inputs["Emission Color"].default_value = (1, 1, 1, 1)
_bb.inputs["Emission Strength"].default_value = float(os.environ.get("BUBBLE_K", "0.95"))
BUB_OBJS = []
for _ in range(BUB_REPEAT * len(BUBBLES)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=12, ring_count=6)
    BUB_OBJS.append(_finish(bpy.context.active_object, "bubble", "glass-fill", bevel=0, smooth=True))


def fill_level(f):
    return FILL_H + FILL_LIFT * kick(f)


def pose_glass(f):
    """The contents in frame f: the level, and every bubble on the surface."""
    lv = fill_level(f)
    bm = bmesh.new()
    _fill_mesh(bm, lv)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(fill.data)
    bm.free()
    zs = HZ + lv * FILL_R
    span = (FILL_X1 - FILL_X0) / BUB_REPEAT
    half = FILL_R * math.sqrt(1 - lv * lv) - 0.02            # stay on the surface, off the wall
    for k, o in enumerate(BUB_OBJS):
        u, dy, r = BUBBLES[k % len(BUBBLES)]
        x = FILL_X1 - (k // len(BUBBLES) + (u + f / FRAMES) % 1.0) * span
        edge = min(x - FILL_X0, FILL_X1 - x) / BUB_FADE
        r *= max(0.0, min(1.0, edge)) ** 0.5 if edge > 0 else 0.0
        r = r if r >= 0.002 else 0.0                       # gone, not a speck (setup() owns hide_render)
        o.location = (x, H_Y + max(-half, min(half, dy)), zs)
        o.scale = (r, r, r * 0.55)
    bpy.context.view_layer.update()

# -- E1: the east crossing, up the east face from its valve pad, west over the lid's edge into
#    the compressor housing's east face (round 10)
PAD_E = Vector((E1_X, E1_Y, PT))
valve_pad(PAD_E, E1_R, ZL)
# (round 12) rigid up the face to a flange, then hose 1 (9.) up over the lid's edge onto the
# housing's roof: the rigid lid run is gone, so the lid's east plate shows
E1_TOP = 0.84
run([Vector((E1_X, E1_Y, ZL)), Vector((E1_X, E1_Y, E1_TOP))], E1_R)
for z in CLIP_Z:
    wall_clip(Vector((E1_X, E1_Y, z)), EAST, E1_R)
flange_pair(Vector((E1_X, E1_Y, E1_TOP - 0.02)), UP, E1_R)

# -- the burst disc's relief line (round 11: off a tee in its nozzle, the holder too shallow
#    for the bore): east over the lid's edge, down the east face on clips, out over the plate
#    and down into a vent cap
RLZ0 = BD_Z + 0.048
tee(Vector((BD_X, BD_Y, RLZ0)), 0.048)
RLZ = 0.25
run([Vector((BD_X, BD_Y, RLZ0)), Vector((RL_X, BD_Y, RLZ0)), Vector((RL_X, BD_Y, RLZ)), Vector((0.85, BD_Y, RLZ)),
     Vector((0.85, BD_Y, 0.19))], RL_R)
place(Vector((0.85, BD_Y, 0.19)), Vector((0.85, BD_Y, 0.165)), 0.06, 0.06, "steel", "static", bevel=0.004)  # the vent cap
for z in CLIP_Z:
    wall_clip(Vector((RL_X, BD_Y, z)), EAST, RL_R)
flange_pair(Vector((RL_X, BD_Y, 0.56)), UP, RL_R)                                                # a union

# (round 9: the old standing gauge glass is gone: the sight glass is inline in the header, above)


# ---------------------------------------------------------------- 9. hoses, wiring, and use (round 8)

# Round 8 (Liam, beside vanilla: "we need to add more wiring and hoses and things ... these look
# too well machined"). Vanilla's pumpjack, chemical plant, big mining drill and electromagnetic
# plant all carry a loose layer over their machined parts: ribbed rubber hoses in slack curves
# with crimped ends, thin coloured cables zip-tied in bundles and looping over edges, boxes bolted
# on afterwards. Here, the same, all of it fixed (the same in every direction), resting on
# something, and clear of every direction's riser (--check tests it, and tests each piece
# against everything fixed):
#
#   - hose 1: off a nipple on the header's east end (where D2 turns into it), up and over the
#     lid's north-east corner, slack, and down onto a new valve pad on the plinth's east side;
#   - hose 2: the wellhead's flexible connection -- off a nipple in the wellhead's cover, arched
#     up and over onto a nipple on the header's top (the rigid nozzle is gone);
#   - a junction box on a welded bracket on the lid's south-west, skewed, its cable glands;
#   - cable 1 (olive): from it, across the lid and looped over its south edge into a pressure
#     switch clamped to M3 on the south face;
#   - cable 2 (a black and a dull red, zip-tied): from it, north up the lid's west plate on clip
#     saddles and east along the header's north side to a gauge transmitter on the header;
#   - cable 3 (grey): from it, east under the mains on clip saddles, a jog round the lifting lug,
#     looped over the lid's east edge into an instrument box on a welded retrofit bracket on
#     the east face;
#   - less machined: a bolted patch on the lid, oil and grime stains on the plinth under the
#     valves and pads (the plates' trim, the D2 jog and the worn and new lid plates are in 3. and 8.).

def _bez(p0, h0, h1, p1, n=60):
    return [p0 * (1 - t) ** 3 + h0 * 3 * (1 - t) ** 2 * t + h1 * 3 * (1 - t) * t * t + p1 * t ** 3
            for t in (k / n for k in range(n + 1))]


def _catmull(pts, n=10):
    """A smooth curve through pts (uniform Catmull-Rom)."""
    pts = [Vector(p) for p in pts]
    ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1])
    return out


def _resample(pts, step):
    pts = [Vector(p) for p in pts]
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + (b - a).length)
    n = max(2, int(L[-1] / step) + 1)
    out, j = [], 0
    for k in range(n + 1):
        s_ = L[-1] * k / n
        while j < len(L) - 2 and L[j + 1] < s_:
            j += 1
        f = (s_ - L[j]) / max(1e-9, L[j + 1] - L[j])
        out.append(pts[j].lerp(pts[j + 1], f))
    return out, L[-1]


def sweep(pts, r, mat, asm, rib=0.0, pitch=0.018, nseg=10, name="sweep"):
    """A tube along pts (dense), its radius rippled by `rib` every `pitch` (a corrugated hose)."""
    pts, length = _resample(pts, pitch / 4 if rib else 0.01)
    n = len(pts)
    tans = [(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(n)]
    ref = Vector((0, 0, 1)) if abs(tans[0].z) < 0.9 else Vector((1, 0, 0))
    nrm = (ref - tans[0] * ref.dot(tans[0])).normalized()
    frames = []
    for i in range(n):
        nrm = (nrm - tans[i] * nrm.dot(tans[i])).normalized()
        frames.append((nrm, tans[i].cross(nrm)))

    def build(bm):
        rings = []
        for i, (p, (u, v)) in enumerate(zip(pts, frames)):
            s_ = length * i / (n - 1)
            rr = r * (1 - rib * (0.5 + 0.5 * math.cos(2 * math.pi * s_ / pitch))) if rib else r
            rings.append([bm.verts.new(p + (u * math.cos(2 * math.pi * k / nseg) + v * math.sin(2 * math.pi * k / nseg)) * rr)
                          for k in range(nseg)])
        for a, b in zip(rings, rings[1:]):
            for k in range(nseg):
                bm.faces.new((a[k], a[(k + 1) % nseg], b[(k + 1) % nseg], b[k]))
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    o = mesh_object(name, build, mat, "static", bevel=0.0, smooth=True)
    o["asm"] = asm
    return o


def tag(asm, objs_before):
    """Tag every part built since objs_before as belonging to asm (--check's pairs)."""
    for o in PARTS["static"][objs_before:]:
        if "asm" not in o:
            o["asm"] = asm


def crimp_end(p, d, r, asm):
    """A hose's crimped end: a hexagonal crimped ferrule and its swivel nut, along d (out of
    the hose into the fitting)."""
    d = d.normalized()
    n0 = len(PARTS["static"])
    L = max(0.042, 1.1 * r)                                   # (round 11) a cuff as long as the hose is fat
    place(p - d * L, p, r * 1.3, r * 1.3, "steel", "static", verts=12, bevel=0.004)             # ferrule, crimped
    for f in (0.3, 0.7):                                                                        # its crimp grooves
        place(p - d * (L * f + 0.005), p - d * (L * f - 0.005), r * 1.22, r * 1.22, "seam", "static", verts=12,
              bevel=0.0)
    place(p - d * (L + 0.006), p - d * L, r * 1.12, r * 1.12, "head", "static", verts=12, bevel=0.0)   # its bright lip
    place(p, p + d * max(0.018, 0.4 * r), r * 1.45, r * 1.45, "steel", "static", verts=6, bevel=0.003)  # the nut
    tag(asm, n0)


def nipple(p, d, r, asm, length=0.06, flange_at=0.022):
    length, flange_at = max(length, 1.6 * r), max(flange_at, 0.6 * r)
    """A short pipe nipple from p along d, flanged flange_at along it; returns its end."""
    d = d.normalized()
    n0 = len(PARTS["static"])
    place(p, p + d * length, r, r, "line", "static")
    flange_pair(p + d * flange_at, d, r)
    tag(asm, n0)
    return p + d * length


HOSE_RIB, HOSE_PITCH = 0.1, 0.05     # (round 11) corrugations 3 px apart, as vanilla's pump hoses are 3-5


def hose(p0, d0, p1, d1, r, slack, asm, n=80):
    """A flexible hose from a fitting at p0 (leaving along d0) to one at p1 (arriving along d1):
    a cubic through slack handles, crimped at both ends, corrugated."""
    h0, h1 = p0 + d0.normalized() * slack, p1 - d1.normalized() * slack
    pts = _bez(p0, h0, h1, p1, n)
    sweep(pts, r, "hose", asm, rib=HOSE_RIB, pitch=HOSE_PITCH, nseg=20, name=asm)
    crimp_end(p0, -d0, r, asm)
    crimp_end(p1, d1, r, asm)


# -- hose 1: the east crossing's flexible end, from E1's flange up over the lid's east edge
#    onto the compressor housing's roof, its suction (round 12: no longer off the header
#    over the lid's north-east corner to a pad on the plinth, where it crossed the north riser's
#    neck in the north view and shaded the lid)
H1_R = 0.085
h1a = nipple(Vector((E1_X, E1_Y, E1_TOP - 0.01)), UP, 0.055, "hose1", length=0.09, flange_at=0.045)
H1_IN = Vector((0.52, -0.13, CH_TOP + 0.022))
h1b = nipple(H1_IN, UP, 0.05, "hose1", length=0.08, flange_at=0.035)
hose(h1a + UP * 0.03, UP, h1b + UP * 0.03, -UP, H1_R, 0.2, "hose1")

# -- hose 2: the wellhead's flexible connection, its cover's centre -> a tee on D1's north run,
#    east of it (round 11: off M3, which is gone; never across the sight glass from the camera)
H2_R = 0.052
w0 = nipple(Vector((BOSS_C.x, BOSS_C.y, BOSS_TOP + 0.012)), UP, 0.045, "hose2", length=0.07, flange_at=0.048)
tee(Vector((D1_NX, -0.06, HZ)), D1_R + 0.004, "line_green")
w1 = nipple(Vector((D1_NX, -0.06, HZ + D1_R)), UP, 0.045, "hose2", length=0.1)
hose(w0 + UP * 0.02, UP, w1 + UP * 0.03, -UP, H2_R, 0.2, "hose2")

# -- the junction box: on a welded bracket on the lid, skewed a few degrees, glands on its sides
JB = Vector((-0.42, -0.27, LZ0))
JB_ROT = math.radians(6)
n0 = len(PARTS["static"])
jb = empty("junction-box", loc=tuple(JB), rot=(0, 0, JB_ROT))
box((0, 0, 0.006), (0.13, 0.1, 0.012), "rail", bevel=0.003, parent=jb)                       # its bracket plate
for sx in (-1, 1):
    box((sx * 0.066, 0, 0.008), (0.008, 0.08, 0.008), "seam", bevel=0.002, parent=jb)         # welded to the lid
box((0, 0, 0.047), (0.1, 0.08, 0.07), "jbox", bevel=0.006, parent=jb)                          # the box
box((0, 0, 0.083), (0.104, 0.084, 0.006), "jbox", bevel=0.002, parent=jb)                      # its lid
for sx in (-1, 1):
    for sy in (-1, 1):
        bolt((sx * 0.042, sy * 0.032, 0.087), 0.006, 0.005, "head", parent=jb)
box((0.0, -0.041, 0.055), (0.05, 0.003, 0.02), "dial", bevel=0.0, parent=jb)                  # its label
tag("jb", n0)


def jb_point(lx, ly, lz):
    c, s_ = math.cos(JB_ROT), math.sin(JB_ROT)
    return JB + Vector((lx * c - ly * s_, lx * s_ + ly * c, lz))


def gland(p, d, asm, r=0.011):
    """A cable gland: a hex body and a domed cap, along d."""
    d = d.normalized()
    n0 = len(PARTS["static"])
    place(p, p + d * 0.01, r * 1.3, r * 1.3, "brass", "static", verts=6, bevel=0.001)
    place(p + d * 0.01, p + d * 0.02, r * 1.05, r * 0.75, "jgland", "static", verts=16, bevel=0.001)
    tag(asm, n0)
    return p + d * 0.02


def jb_dir(lx, ly):
    c, s_ = math.cos(JB_ROT), math.sin(JB_ROT)
    return Vector((lx * c - ly * s_, lx * s_ + ly * c, 0))


g1 = gland(jb_point(0.025, -0.04, 0.04), jb_dir(0, -1), "jb")       # south: a spare (round 12: cable 1 gone)
g2 = gland(jb_point(-0.03, 0.04, 0.04), jb_dir(0, 1), "jb", r=0.014)  # north: cable 2's bundle
g3 = gland(jb_point(0.05, -0.012, 0.035), jb_dir(1, 0), "jb")        # east: cable 3


def clip_saddle(p, r, asm):
    """A small saddle clip on the lid holding a cable (or a bundle) off it at p."""
    z0 = lid_z(p.x, p.y) + 0.004                                        # (the plates sit a hair proud here and there)
    top = p.z - r
    n0 = len(PARTS["static"])
    box((p.x, p.y, (z0 + top) / 2), (0.014, 0.018, max(0.002, top - z0)), "rail", bevel=0.001)
    box((p.x, p.y, p.z + r + 0.002), (0.012, 0.016, 0.004), "rail", bevel=0.001)
    tag(asm, n0)


def tie(p, d, r, asm):
    """A nylon zip tie round a bundle at p."""
    o = torus(tuple(p), r + 0.002, 0.0028, "tie", rot=facing(d), seg=14)
    o["asm"] = asm


def cable(pts, r, mat, asm, n=10):
    return sweep(_catmull(pts, n), r, mat, asm, nseg=8, name=asm)


CR = 0.0095                                     # a cable
CZ = LZ0 + 0.026                                # cables on clip saddles over the lid

# (round 12: the pressure switch and its cable are gone -- D1's face is full with the fatter main
# and its bypass; the gauge on D1's east run reads the pressure)

# -- the gauge transmitter, on a nipple standing on the sight glass's west flange
TX = Vector((SG_X0 - SG_FL / 2, H_Y + 0.02, HZ + SG_FR + 0.05))   # (round 12: on the west flange, clear of hose 1)
n0 = len(PARTS["static"])
place(Vector((TX.x, H_Y + 0.02, HZ + SG_FR - 0.008)), Vector((TX.x, H_Y + 0.02, TX.z - 0.03)), 0.014, 0.014, "line",
      "static")
box(tuple(TX), (0.05, 0.05, 0.06), "instr", bevel=0.006)
cyl(tuple(TX + Vector((0, 0, 0.033))), 0.018, 0.006, "jbox", verts=20, bevel=0.002)
tag("tx", n0)
gt_ = gland(TX + Vector((0, 0.025, 0)), NORTH, "tx", r=0.011)

# -- cable 2: a bundle of two, junction box -> north up the west plate -> east along the lid's
#    north margin, behind the header -> up into the transmitter's back; zip-tied, on clip saddles
CY2 = 0.49
B2 = [g2, g2 + Vector((0, 0.03, -0.01)), Vector((-0.5, -0.18, CZ + 0.002)), Vector((-0.52, 0.0, CZ)),
      Vector((-0.525, 0.2, CZ + 0.001)), Vector((-0.525, 0.43, CZ)), Vector((-0.47, CY2, CZ + 0.002)),
      Vector((-0.38, CY2, CZ + 0.002)), Vector((TX.x - 0.02, CY2, CZ + 0.01)), Vector((TX.x, 0.515, CZ + 0.06)), Vector((TX.x, 0.52, 1.0)),
      Vector((TX.x, 0.45, TX.z - 0.03)), gt_ + Vector((0, 0.03, 0)), gt_]
path2 = _catmull(B2, 10)
for sgn, mat in ((1, "cable_black"), (-1, "cable_red")):
    pts_ = []
    for i, p in enumerate(path2):
        t = (path2[min(i + 1, len(path2) - 1)] - path2[max(i - 1, 0)]).normalized()
        side = t.cross(UP)
        side = side.normalized() if side.length > 1e-3 else Vector((1, 0, 0))
        k = min(1.0, i / 6, (len(path2) - 1 - i) / 6)                    # together into each gland
        pts_.append(p + side * sgn * 0.0068 * k)
    sweep(pts_, 0.0062, mat, "c2", nseg=8, name="c2")
for p in (Vector((-0.505, -0.12, CZ)), Vector((-0.523, 0.1, CZ)), Vector((-0.42, CY2, CZ))):
    clip_saddle(p, 0.013, "c2")
for i in range(8, len(path2) - 8, 9):
    p = path2[i]
    tie(p, (path2[i + 1] - path2[i - 1]), 0.0125, "c2")

# -- cable 3 (round 10): junction box -> south-east under D1 -> east along the lid's south
#    edge, outside the band (round 12) -> up into a gland low in the compressor housing's south
#    face: its motor's supply
CY3 = -0.505
gi = gland(Vector((0.37, CH_Y0 + CH_B * (0.84 - LZ0 - 0.02) / (CH_TOP - LZ0 - 0.02) - 0.002, 0.84)), SOUTH, "c3",
           r=0.012)
cable([g3, g3 + Vector((0.025, -0.004, -0.012)), Vector((-0.30, -0.38, CZ)), Vector((-0.26, CY3, CZ + 0.002)),
       Vector((0.05, CY3, CZ)), Vector((0.28, CY3, CZ + 0.002)), Vector((0.35, gi.y - 0.04, gi.z - 0.025)), gi],
      CR, "cable_grey", "c3")
for p in (Vector((-0.08, CY3, CZ)), Vector((0.18, CY3, CZ))):
    clip_saddle(p, CR, "c3")

# -- hose 3: off the east crossing's valve pad, slack across the plinth to a drain pot
HP3 = Vector((0.775, -0.43, PL_T))                   # (round 10: out past the grown east face)
R3 = 0.055                                           # (round 11: 0.022 -> 0.055)
n0 = len(PARTS["static"])
cyl((HP3.x, HP3.y, PL_T + 0.045), 0.065, 0.09, "valve", verts=32, bevel=0.008)               # the pot
cyl((HP3.x, HP3.y, PL_T + 0.094), 0.07, 0.01, "rail", verts=32, bevel=0.003)                 # its lid
for k in range(6):
    a_ = math.pi / 3 * k + 0.4
    bolt((HP3.x + 0.056 * math.cos(a_), HP3.y + 0.056 * math.sin(a_), PL_T + 0.1), 0.008, 0.007, "head")
tag("hose3", n0)
PE_R = E1_R * 1.25 + 0.008                           # the pad's valve body
p3a = nipple(Vector((PAD_E.x + 0.012, PAD_E.y - PE_R + 0.004, ZL - 0.06)), SOUTH, 0.04, "hose3", length=0.07, flange_at=0.03)
p3b = nipple(Vector((HP3.x, HP3.y, PL_T + 0.099)), UP, 0.04, "hose3", length=0.065, flange_at=0.03)
q0, q1 = p3a + SOUTH * 0.03, p3b + UP * 0.03
pts3 = _catmull([q0, q0 + SOUTH * 0.05 + Vector((0, 0, -0.03)), Vector((0.81, -0.30, PL_T + R3 + 0.004)),
                 Vector((0.80, -0.34, PL_T + R3 + 0.03)), q1 + UP * 0.09, q1], 12)
sweep(pts3, R3, "hose", "hose3", rib=HOSE_RIB, pitch=HOSE_PITCH, nseg=16, name="hose3")
crimp_end(q0, -SOUTH, R3, "hose3")
crimp_end(q1, -UP, R3, "hose3")

# -- the vent stack (round 8, FFF #350: the casing's top edge was a straight line): the header
#    turned up at its west end (round 11: no longer out of W1, which is gone), flanged, reduced,
#    its rain cap standing above the casing so the outline is not a box; stayed to the lid
VS = Vector((HX0, H_Y, 0.0))
VS_R = 0.075
n0 = len(PARTS["static"])
weld(Vector((VS.x, VS.y, 1.138)), UP, "static", r=H_R)          # (round 12: no flange, the glass's is beside it)
place(Vector((VS.x, VS.y, 1.138)), Vector((VS.x, VS.y, 1.18)), H_R, VS_R, "line", "static")      # the reducer
place(Vector((VS.x, VS.y, 1.18)), Vector((VS.x, VS.y, VS_TOP)), VS_R, VS_R, "line", "static")   # the stack
cone((VS.x, VS.y, VS_TOP + 0.04), 0.115, 0.02, 0.055, "rail", verts=32)                           # its rain cap
for k in range(3):
    a_ = 2 * math.pi * k / 3 + 0.3
    place(Vector((VS.x + 0.05 * math.cos(a_), VS.y + 0.05 * math.sin(a_), VS_TOP - 0.01)),
          Vector((VS.x + 0.09 * math.cos(a_), VS.y + 0.09 * math.sin(a_), VS_TOP + 0.017)), 0.007, 0.007, "steel",
          "static", verts=6, bevel=0.0)                                                     # the cap's legs
# its stay: a strap round it, a flat bar down to a foot welded on the lid, south-east of it
place(Vector((VS.x, VS.y, 1.04)), Vector((VS.x, VS.y, 1.065)), H_R + 0.01, H_R + 0.01, "rail", "static", bevel=0.003)
p_top, p_foot = Vector((VS.x + 0.04, VS.y - 0.11, 1.05)), Vector((-0.41, 0.10, LZ0 + 0.005))
v_ = p_foot - p_top
box(tuple((p_top + p_foot) / 2), (0.022, 0.008, v_.length), "rail", rot=facing(v_), bevel=0.001)
box(tuple(p_foot), (0.05, 0.04, 0.012), "rail", bevel=0.002)
tag("stack", n0)

# -- the compressor housing (round 10, Liam: "more bulky"; FFF #350): a battered box standing
#    on the lid's east plate beside the wellhead, up to z 1.08 -- mass up off the ground and a
#    stepped top, the casing's lid at 0.78 and this above it. Louvres in its south face, a
#    brass motor plate, its roof bolted down with a breather on it; E1 comes into its east
#    face, cable 3 into its west face
n0 = len(PARTS["static"])
_foot = [(CH_X0, CH_Y0 + 0.05), (CH_X0 + 0.05, CH_Y0), (CH_X1 - 0.05, CH_Y0), (CH_X1, CH_Y0 + 0.05),
         (CH_X1, CH_Y1 - 0.05), (CH_X1 - 0.05, CH_Y1), (CH_X0 + 0.05, CH_Y1), (CH_X0, CH_Y1 - 0.05)]
stack([(offset_poly(_foot, -0.012), LZ0), (offset_poly(_foot, -0.012), LZ0 + 0.02),
       (_foot, LZ0 + 0.02), (offset_poly(_foot, CH_B), CH_TOP)], "housing", bevel=0.006, name="housing")
stack([(offset_poly(_foot, CH_B - 0.012), CH_TOP), (offset_poly(_foot, CH_B - 0.012), CH_TOP + 0.022)], "lid",
      bevel=0.005, name="housing-roof")
for p, t, n, i in along(offset_poly(_foot, -0.004), 0.07, ends=0.03):
    bolt((p.x, p.y, LZ0 + 0.024), 0.009, 0.008, "head")                       # its foot, bolted down
for p, t, n, i in along(offset_poly(_foot, CH_B + 0.006), 0.07, ends=0.03):
    bolt((p.x, p.y, CH_TOP + 0.025), 0.009, 0.008, "head")                    # its roof, bolted down


def _on_south(x, z, out=0.0):
    """A point on the housing's leaning south face at (x, z), `out` proud of it."""
    f = (z - (LZ0 + 0.02)) / (CH_TOP - LZ0 - 0.02)
    return Vector((x, CH_Y0 + CH_B * f - out, z))


lean = math.atan(CH_B / (CH_TOP - LZ0 - 0.02))
for k in range(5):                                                            # the louvres
    z = 0.875 + 0.032 * k
    box(tuple(_on_south(0.47, z, 0.006)), (0.2, 0.008, 0.024), "valve", rot=(-0.6 + lean, 0, 0), bevel=0.001)
box(tuple(_on_south(0.47, 0.94, 0.002)), (0.23, 0.004, 0.18), "rail", rot=(lean, 0, 0), bevel=0.002)  # their frame
MP2 = empty("motor-plate", loc=tuple(_on_south(0.36, 0.95, 0.004)), rot=(math.pi / 2 + lean, 0, 0))
box((0, 0, 0), (0.05, 0.04, 0.006), "brass", bevel=0.002, parent=MP2)
# its roof: a breather stub with a rain cap, and a lifting eye
# (the gas-pump-animation task, a2: Liam, option 2) the breather moved from the roof's south-east
# (0.54, -0.31), under the flywheel, to its north-west corner, clear of hose 1's cuff
BREATHER = (0.40, 0.0)
place(Vector((*BREATHER, CH_TOP + 0.02)), Vector((*BREATHER, CH_TOP + 0.1)), 0.02, 0.02, "line", "static")
cone((*BREATHER, CH_TOP + 0.115), 0.045, 0.01, 0.03, "rail", verts=20)
box((0.40, -0.2, CH_TOP + 0.035), (0.05, 0.03, 0.02), "steel", bevel=0.004)
torus((0.40, -0.2, CH_TOP + 0.062), 0.02, 0.008, "polish", rot=(math.pi / 2, 0, 0), seg=20)
tag("housing", n0)

# ---------------------------------------------------------------- 10. the pumping animation
#
# The gas-pump-animation task (Liam, 2026-10-10: ideas 1, 2 and 3; then option 2, "make the
# crank read boldly at 1x"): the compressor is seen to run. A big flywheel (radius 0.28, 36 px
# across at 1x) stands on the housing's roof, upright and facing the camera (a wheel across the
# view reads as a full-width ellipse; one along it would be seen edge on), overhung on its shaft
# from a pedestal behind it, its rim clear over D1's north run to the west and the lid's edge to
# the east. A crank pin on its face drives a heavy connecting rod east into an open-ended trunk
# cylinder; rod and cylinder lie in front of the wheel, on an engine bed that stands on a leg on
# the roof's south edge and a post welded to the lid's east margin. The breather moved to the
# roof's north-west corner to make room (above); the lifting eye and hose 1 stay (--collide checks
# every moving part in every frame, --check every new fixed part). a1 (the first round: a 0.14
# wheel between the breather and hose 1) is crust_tap-a1.py.
#
# One revolution a loop, at constant speed, FRAMES frames. Frame 0 is the piston at the crank
# end of its stroke (the pin due west), so the first half of the loop is the compression
# stroke (the piston running east to the cylinder's head) and the second the return. The
# gauge's needle kicks on each stroke: still for the first third of the compression, up fast
# as the pressure peaks at the stroke's end, easing back to rest by the loop's end. The sight
# glass's gas (the glass layer) runs on the same loop: its level lifts with the discharge and
# bubbles drift west along it.
#
# Moving parts: the flywheel and its pin ("crank"), the rod ("rod"), the piston ("piston":
# inside the cylinder, seen only through its open mouth, and rendered alone for the slide
# check, contract `track`) and the needle ("needle"). Everything else here is fixed, in the
# plate.
FRAMES = int(os.environ.get("FRAMES", "24"))
LOOP_S = 1.0                                     # seconds a stroke (the task: about 1 s)
CK = Vector((0.415, -0.30, 1.41))                 # the crankshaft's centre: its axis along y
WR, WT = 0.28, 0.03                              # the flywheel's radius and thickness
THROW, ROD_L = 0.09, 0.40                        # the crank's throw, the rod's length (centres)
ROD_Y, ROD_Z = 0.03, 0.04                        # the rod's section: about 3 px on the screen
LY = -0.405                                      # the rod's, the piston's and the cylinder's line (y)
CYL_X0, CYL_X1, CYL_R, BORE_R = 0.675, 0.955, 0.07, 0.058   # the cylinder: its open mouth, its head end, radii
ROOF_Z = LZ0 + 0.302                             # the housing's roof plate's top
NEEDLE_KICK = 2.0                                # rad, clockwise from above: the needle's kick (a1: 1.1)


def crank_angle(f):
    """The pin's angle from due east, about -y (east -> up): due west in frame 0."""
    return math.pi + 2 * math.pi * (f % FRAMES) / FRAMES


def pin_at(f):
    a = crank_angle(f)
    return Vector((CK.x + THROW * math.cos(a), LY, CK.z + THROW * math.sin(a)))


def piston_x(f):
    """The wrist pin's x: the slider-crank, exactly."""
    a = crank_angle(f)
    return CK.x + THROW * math.cos(a) + math.sqrt(ROD_L ** 2 - (THROW * math.sin(a)) ** 2)


def kick(f):
    """The needle's lift, 0 at rest to 1 at the peak: still for the first third of the
    compression stroke, up as t^2 to the stroke's end, back by a half cosine to rest at the
    loop's end, so the loop closes with no step."""
    t = (f % FRAMES) / FRAMES
    if t < 1 / 6:
        return 0.0
    if t <= 0.5:
        return ((t - 1 / 6) / (1 / 3)) ** 2
    return 0.5 * (1 + math.cos(math.pi * (t - 0.5) / 0.5))


# the slide's declared curve (contract): the piston's offset from frame 0, x only
PATH = [[round(piston_x(f) - piston_x(0), 6), 0.0, 0.0] for f in range(FRAMES)]

n0 = len(PARTS["static"])
# -- the fixed parts: the pedestal behind the wheel and the shaft out of it
PED_Y0, PED_Y1 = -0.272, -0.236                  # the pedestal's faces: between the wheel and the lifting eye
box((CK.x, (PED_Y0 + PED_Y1) / 2, (ROOF_Z + CK.z) / 2), (0.056, PED_Y1 - PED_Y0, CK.z - ROOF_Z), "rail", bevel=0.004)
box((CK.x, (PED_Y0 + PED_Y1) / 2, ROOF_Z + 0.004), (0.064, 0.05, 0.008), "rail", bevel=0.002)    # its foot,
for sy in (PED_Y0 - 0.004, PED_Y1 + 0.004):                                     # inside the roof's edge bolts
    for sx in (-1, 1):
        bolt((CK.x + sx * 0.02, sy, ROOF_Z + 0.011), 0.006, 0.005, "head")
place(Vector((CK.x, PED_Y0 - 0.004, CK.z)), Vector((CK.x, PED_Y1 + 0.004, CK.z)), 0.045, 0.045, "steel", "static",
      verts=24, bevel=0.003)                                                    # its bearing housing
place(Vector((CK.x, PED_Y1, CK.z)), Vector((CK.x, -0.285 + 0.002, CK.z)), 0.022, 0.022, "polish", "static",
      verts=16, bevel=0.0)                                                      # the shaft, to the wheel's hub
# -- the cylinder: a barrel with cooling ribs, a bolted head at its east end, open at its west (a
#    trunk piston: the rod works straight into it)
CYL_A, CYL_B = Vector((CYL_X0, LY, CK.z)), Vector((CYL_X1, LY, CK.z))
ring(tuple((CYL_A + CYL_B) / 2), CYL_R, BORE_R + 0.0012, CYL_X1 - CYL_X0, "line_green", rot=(0, math.pi / 2, 0),
     verts=40, bevel=0.003)                                                     # the barrel
ring(tuple((CYL_A + CYL_B) / 2), BORE_R + 0.0011, BORE_R, CYL_X1 - CYL_X0 - 0.002, "bore", rot=(0, math.pi / 2, 0),
     verts=40, bevel=0.0)                                                       # its bore, dark, seen at the mouth
for k in range(4):                                                              # cooling ribs
    x_ = CYL_X0 + 0.09 + 0.045 * k
    ring((x_, LY, CK.z), CYL_R + 0.012, CYL_R - 0.002, 0.012, "rail", rot=(0, math.pi / 2, 0), verts=40, bevel=0.002)
ring(tuple(CYL_A + EAST * 0.008), CYL_R + 0.012, BORE_R + 0.001, 0.016, "worn", rot=(0, math.pi / 2, 0), verts=40,
     bevel=0.003)                                                               # the mouth's lip, worn bright
place(Vector((CYL_X1 - 0.002, LY, CK.z)), Vector((CYL_X1 + 0.022, LY, CK.z)), CYL_R + 0.018, CYL_R + 0.018, "steel",
      "static", verts=40, bevel=0.005)                                          # the head
bolt_ring(Vector((CYL_X1 + 0.022, LY, CK.z)), EAST, CYL_R + 0.008, 8, 0.007, "static", mat="head", h=0.006)
cyl((CYL_X1 + 0.006, LY, CK.z + CYL_R + 0.03), 0.011, 0.04, "brass_g", verts=12, bevel=0.0)   # a cock on the head
# -- the engine bed: a channel under the rod and the cylinder, out of the rod's sweep (its west end
#    clear of the big end), on a leg standing on the roof's south edge and a post welded to the
#    lid's east margin; two saddles and straps carry the cylinder on it
BED_X0, BED_X1, BED_Z = 0.515, CYL_X1 - 0.02, 1.29                            # its ends, its top
BED_Y0, BED_Y1 = LY - 0.045, -0.322
box(((BED_X0 + BED_X1) / 2, (BED_Y0 + BED_Y1) / 2, BED_Z - 0.01), (BED_X1 - BED_X0, BED_Y1 - BED_Y0, 0.02), "rail",
    bevel=0.003)
LEG_X = 0.535
box((LEG_X, -0.335, (ROOF_Z + BED_Z - 0.02) / 2), (0.04, 0.026, BED_Z - 0.02 - ROOF_Z), "rail", bevel=0.003)
POST_X = 0.625                                    # between the housing's foot bolts and the lid's edge bolts
box((POST_X, -0.335, (LZ0 + BED_Z - 0.02) / 2), (0.02, 0.03, BED_Z - 0.02 - LZ0), "rail", bevel=0.003)
box((POST_X, -0.335, LZ0 + 0.003), (0.022, 0.032, 0.006), "seam", bevel=0.002)          # its weld
for x_ in (CYL_X0 + 0.06, CYL_X1 - 0.05):                                       # saddles and straps
    box((x_, LY, (BED_Z + CK.z - CYL_R) / 2 + 0.002), (0.03, 0.07, CK.z - CYL_R - BED_Z + 0.004), "rail",
        bevel=0.002)
    ring((x_ + 0.022, LY, CK.z), CYL_R + 0.007, CYL_R - 0.001, 0.014, "steel", rot=(0, math.pi / 2, 0), verts=40,
         bevel=0.002)
g0, g1 = Vector((POST_X + 0.01, -0.335, BED_Z - 0.17)), Vector((BED_X1 - 0.03, -0.335, BED_Z - 0.022))
v_ = g1 - g0
box(tuple((g0 + g1) / 2), (0.016, 0.01, v_.length), "rail", rot=facing(v_), bevel=0.001)       # the gusset
tag("crank-fixed", n0)

# -- the moving parts
CRANK = empty("crank", loc=tuple(CK))                                           # turns about y
WY_L = -0.30 - CK.y                                                             # the wheel's mid-plane, local
ring((0, WY_L, 0), WR, WR - 0.045, WT, "steel", group="crank", parent=CRANK, rot=(math.pi / 2, 0, 0), verts=96,
     bevel=0.005)                                                               # the rim
ring((0, WY_L - WT / 2 - 0.001, 0), WR - 0.003, WR - 0.02, 0.004, "wheel", group="crank", parent=CRANK,
     rot=(math.pi / 2, 0, 0), verts=96, bevel=0.0)                              # its front edge, worn bright
cyl((0, WY_L, 0), 0.05, WT + 0.016, "steel", group="crank", parent=CRANK, rot=(math.pi / 2, 0, 0), verts=32)  # the hub
for k in range(5):                                                              # five spokes: a frame's step
    a = 2 * math.pi * (k + 0.5) / 5                                             # (15 degrees) never matches theirs
    rr = (0.05 + WR - 0.04) / 2
    box((rr * math.cos(a), WY_L, rr * math.sin(a)), (WR - 0.09, 0.016, 0.026), "rail", group="crank", parent=CRANK,
        rot=(0, -a, 0), bevel=0.003)
# the counterweight, opposite the pin: a heavy segment in ochre paint, as moving machinery is
# painted, so the turn reads at 1x as a light mass and a bright pin swapping round the dark wheel
M["cweight"] = layered("cweight", "#CCA845", metal="#C4BEB2", paint_metal=0.05, paint_rough=0.6, wear=0.45,
                       rust=0.25, rust_tint=WET_RUST, dust=0.15, grime=0.35, jitter=0.08)
CW_A, CW_R0, CW_R1 = 0.85, 0.06, WR - 0.045          # its half-angle, its inner and outer radii


def _cweight(bm):
    n = 24
    angs = [math.pi - CW_A + 2 * CW_A * i / n for i in range(n + 1)]
    rows = []
    for y_ in (WY_L - WT / 2 + 0.001, WY_L + WT / 2 - 0.003):
        rows.append([bm.verts.new((r * math.cos(t), y_, r * math.sin(t))) for t in angs for r in (CW_R0, CW_R1)])
    for i in range(n):
        q = [2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2]                          # the segment's faces, front and back
        bm.faces.new([rows[0][k] for k in q])
        bm.faces.new([rows[1][k] for k in reversed(q)])
        for k0, k1 in ((2 * i, 2 * i + 2), (2 * i + 1, 2 * i + 3)):           # its inner and outer edges
            bm.faces.new((rows[0][k0], rows[0][k1], rows[1][k1], rows[1][k0]))
    for k0, k1 in ((0, 1), (2 * n, 2 * n + 1)):                                # its ends
        bm.faces.new((rows[0][k0], rows[0][k1], rows[1][k1], rows[1][k0]))


mesh_object("counterweight", _cweight, "cweight", "crank", bevel=0.005, parent=CRANK)
# the crank pin on the wheel's front face, at the throw (local east: the crank turns it), on a boss
place(Vector((THROW, WY_L - WT / 2 + 0.002, 0)), Vector((THROW, WY_L - WT / 2 - 0.012, 0)), 0.04, 0.04, "steel",
      "crank", verts=24, bevel=0.003)
PARTS["crank"][-1].parent = CRANK
place(Vector((THROW, WY_L - WT / 2 - 0.01, 0)), Vector((THROW, LY - CK.y - ROD_Y / 2 - 0.012, 0)), 0.018, 0.018,
      "polish", "crank", verts=16, bevel=0.002)
PARTS["crank"][-1].parent = CRANK
# the connecting rod: built along local +x, its big end at the origin (on the pin), its small
# end ROD_L east; turned about y each frame. Heavy: 0.03 deep and 0.04 high, about 3 px on the
# screen, a polished shank between a bolted big end and a small end
ROD = empty("rod", loc=(0, 0, 0))
box((ROD_L / 2, 0, 0), (ROD_L - 0.06, ROD_Y, ROD_Z), "polish", group="rod", parent=ROD, bevel=0.004)
cyl((0, 0, 0), 0.042, ROD_Y + 0.008, "steel", group="rod", parent=ROD, rot=(math.pi / 2, 0, 0), verts=24,
    bevel=0.004)                                                                # big end
box((0.0, 0, 0), (0.1, ROD_Y + 0.004, 0.022), "steel", group="rod", parent=ROD, bevel=0.003)    # its cap
for sx in (-1, 1):
    bolt((sx * 0.044, -(ROD_Y + 0.008) / 2 - 0.002, 0), 0.008, 0.006, "head", group="rod", parent=ROD,
         rot=(math.pi / 2, 0, 0))
cyl((ROD_L, 0, 0), 0.026, ROD_Y, "steel", group="rod", parent=ROD, rot=(math.pi / 2, 0, 0), verts=20, bevel=0.003)
# the piston: inside the cylinder, its crown east; the tracked part
PISTON = empty("piston", loc=(piston_x(0), LY, CK.z))
place(Vector((-0.035, 0, 0)), Vector((0.045, 0, 0)), BORE_R - 0.002, BORE_R - 0.002, "steel", "piston", verts=32,
      bevel=0.003)
PARTS["piston"][-1].parent = PISTON
for x_ in (0.025, 0.037):
    place(Vector((x_ - 0.003, 0, 0)), Vector((x_ + 0.003, 0, 0)), BORE_R - 0.0015, BORE_R - 0.0015, "bore", "piston",
          verts=32, bevel=0.0)
    PARTS["piston"][-1].parent = PISTON                                         # its rings


def pose(f):
    """Put every moving part where frame f has it."""
    a = crank_angle(f)
    CRANK.rotation_euler = (0, -a, 0)                      # the pin, built due east, to angle a
    p, w = pin_at(f), Vector((piston_x(f), LY, CK.z))
    ROD.location = p
    ROD.rotation_euler = (0, -math.atan2(w.z - p.z, w.x - p.x), 0)       # local +x onto the wrist pin
    PISTON.location = w
    NEEDLE.rotation_euler = (0, 0, NEEDLE_REST - NEEDLE_KICK * kick(f))
    bpy.context.view_layer.update()


MOVING = ("crank", "rod", "piston", "needle")

# -- a bolted patch on the lid's north-east, older steel than the plate round it
n0 = len(PARTS["static"])
pz, prot = LZ0 + 0.006, (0, 0, math.radians(-3))
pt = empty("lid-patch", loc=(0.37, 0.375, pz), rot=prot)
box((0, 0, 0.003), (0.11, 0.085, 0.006), "patch", bevel=0.002, parent=pt)
for sx in (-1, 1):
    for sy in (-1, 1):
        rivet((sx * 0.044, sy * 0.032, 0.007), 0.007, "head", parent=pt)
tag("patch", n0)

# -- oil and grime on the plinth, under the valves and the pads: irregular dark stains, a
#    little glossy
_rs = _random.Random(11)


def stain(cx, cy, r, z):
    def build(bm):
        n = 18
        ph = [_rs.random() * 6.28 for _ in range(3)]
        vs = []
        for k in range(n):
            a = 2 * math.pi * k / n
            rr = r * (1 + 0.28 * math.sin(2 * a + ph[0]) + 0.18 * math.sin(3 * a + ph[1]) + 0.1 * math.sin(5 * a + ph[2]))
            vs.append(bm.verts.new((cx + rr * math.cos(a), cy + rr * 0.8 * math.sin(a), z)))
        bm.faces.new(vs)
    o = mesh_object("stain", build, "oil", "static", bevel=0.0, recalc=False)
    o["asm"] = "stain"


# (round 10) grit drifted against the plinth's east edge, on the plate, in the shadow of the
# grown casing, the housing and the east face's pipes: so that shadow reads as shaded ground
def _grit(bm):
    pts = []
    n = 24
    for k in range(n + 1):
        y = -0.56 + 1.1 * k / n
        pts.append((0.86 + 0.055 + 0.012 * math.sin(7.0 * y) + 0.008 * math.sin(19.0 * y), y))
    vs = [bm.verts.new((0.858, -0.56, PT + 0.0011))] + [bm.verts.new((x, y, PT + 0.0011)) for x, y in pts] + \
         [bm.verts.new((0.858, 0.54, PT + 0.0011))]
    bm.faces.new(vs)


_g = mesh_object("grit", _grit, "grit", "static", bevel=0.0, recalc=False)
_g["asm"] = "stain"
for cx, cy, r in ((0.78, 0.49, 0.07), (0.79, -0.06, 0.05), (-0.79, 0.31, 0.07), (-0.2, -0.8, 0.045),
                  (0.07, -0.64, 0.05), (-0.78, -0.05, 0.05), (-0.8, 0.44, 0.04)):   # (round 13: two on the west strip)
    stain(cx, cy, r, ground_z(cx, cy) + 0.0012)

# ---------------------------------------------------------------- passes

SUN = rig.sun()
# The shadows lifted, as the vacuum furnace's and the drop crusher's are: the rig's warm
# fill raised, so the collar's foot and the anchors' shaded sides stay coloured, not black.
# (round 12, Liam: "a bit brighter ... lifted shadow side") 0.26 -> 0.30 for this building
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = float(os.environ.get("FILL", "0.28"))   # the rig: 0.14
SHADOW_SUN_DEG = float(os.environ.get("SHADOW_SUN_DEG", "14"))
GROUND = rig.ground_catcher()
GROUND.parent = ROOT
BOUNCE = rig.bounce_ground()

if "--check" in argv:
    # Every riser against everything fixed: a real intersection test on the evaluated meshes
    # (bevels, solidify and curves applied), in world space, each pair prefiltered by its
    # bounds. The stands' feet on the base plate and the supports' bases on it are meant to
    # touch; everything else reported is a clash.
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()
    CENTRES = {}

    def tree(o):
        e = o.evaluated_get(dg)
        me = e.to_mesh()
        mw = e.matrix_world
        vs = [mw @ v.co for v in me.vertices]
        if not vs:
            e.to_mesh_clear()
            return None, Vector((9, 9, 9)), Vector((-9, -9, -9))
        polys = [p.vertices[:] for p in me.polygons]
        t = BVHTree.FromPolygons(vs, polys)
        CENTRES[t] = [sum((vs[i] for i in pv), Vector()) / len(pv) for pv in polys]
        lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
        hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
        e.to_mesh_clear()
        return t, lo, hi

    fixed = [(o, *tree(o)) for g, objs in PARTS.items() if g in ("static", "glass") for o in objs
             if o.type in ("MESH", "CURVE")]
    print("CHECK empty fixed parts at lines", sorted({o.get("line") for o, t, lo, hi in fixed if t is None}))
    fixed = [x for x in fixed if x[1] is not None]
    report = {}
    for d in DIRS:
        hits = set()
        for o in PARTS[f"riser-{d}"]:
            if o.type not in ("MESH", "CURVE"):
                continue
            t, lo, hi = tree(o)
            if t is None:
                continue
            for p, tp, plo, phi in fixed:
                if any(hi[i] < plo[i] - 1e-4 or lo[i] > phi[i] + 1e-4 for i in range(3)):
                    continue
                if t.overlap(tp):
                    hits.add((o.get("line"), p.get("line"), p.name))
        report[d] = sorted(hits, key=str)
    # (round 8) each part of the loose layer against everything fixed but its own assembly
    layer = [x for x in fixed if x[0].get("asm")]
    rest = {}
    for o, t, lo, hi in layer:
        for p, tp, plo, phi in fixed:
            if p is o or p.get("asm") == o.get("asm"):
                continue
            if any(hi[i] < plo[i] - 1e-4 or lo[i] > phi[i] + 1e-4 for i in range(3)):
                continue
            ov = t.overlap(tp)
            if ov:
                key = tuple(sorted(((o.get("asm"), o.get("line")), (p.get("asm") or "-", p.get("line")))))
                c = CENTRES[tp][ov[0][1]]                         # (where, on the other part)
                rest[key] = (round(c.x, 3), round(c.y * math.sin(math.radians(60)), 3), round(c.z, 3))
    print(f"CHECK layer: {len(rest)} contact pairs")
    for k in sorted(rest, key=str):
        print("CHECK   ", k[0], "x", k[1], "at", rest[k])
    for d, hits in report.items():
        print(f"CHECK riser-{d}: {len(hits)} clashes")
        for h in hits:
            print("CHECK   riser line", h[0], "vs fixed line", h[1], h[2])
    sys.exit(0)

if "--blend" in argv:                    # debugging: the scene as built, not rendered
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "scene.blend"))
    sys.exit(0)


def setup(visible=(), ground=False, only=None, holdouts=(), catchers=()):
    for g, objs in PARTS.items():
        if g.startswith("mouth-"):
            continue                      # a view of the riser groups' collars, not a group of its own
        for o in objs:
            o.hide_render = g not in visible and g not in holdouts and g not in catchers
            o.is_holdout = g in holdouts
            o.is_shadow_catcher = g in catchers
            o.visible_camera = True
    if only is not None:
        for g, objs in PARTS.items():
            for o in objs:
                o.hide_render = o not in only
    GROUND.hide_render = not ground
    BOUNCE.hide_render = ground


if ICON:
    sc.cycles.samples = 128
    # An icon is not a sprite on the rig: its fill is lifted so the collar's own shadow does
    # not swallow the riser
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    # a three-quarter view (round 3): the tap turned so its riser comes toward the camera on a
    # diagonal, stand, valve and mouth in view
    ICON_DIR, ICON_TURN = (os.environ.get("ICON_DIR", "south"), float(os.environ.get("ICON_TURN", "25")))
    ROOT.rotation_euler.z = math.radians(ICON_TURN)
    # cropped close on the collar's front and the riser coming toward the camera, the plate's
    # far corners let go: 1.5 tiles across, centred 0.48 below the origin
    # (round 7: 2.2 tiles centred 0.2 below, so the square casing reads whole at 32 px)
    span = float(os.environ.get("ICON_SPAN", "2.2"))
    k = 1024 / span
    cx, cy = float(os.environ.get("ICON_CX", "0.0")), float(os.environ.get("ICON_CY", "-0.2"))
    rig.camera(1024, 1024, centre_px=(512 - k * cx, 512 + k * cy), ss=1).data.ortho_scale = span
    pose(0)
    setup(visible=("static", "glass", f"riser-{ICON_DIR}") + MOVING)
    # the riser's steel a step paler in the icon only, so the pipe separates from the dark
    # collar at 32 px (the sprites keep the mid-value pipe)
    pale = layered("pipe-icon", "#A49C90", metal="#D8D0C2", paint_metal=0.3, paint_rough=0.45, wear=0.45,
                   rust=0.3, rust_tint=WARM_RUST, dust=0.1, grime=0.4, jitter=0.08)
    for o in PARTS[f"riser-{ICON_DIR}"]:
        if o.data.materials and o.data.materials[0] in (M["pipe"], M["valve"], M["steel"]):
            o.data.materials[0] = pale
    rig.render(f"{OUT_DIR}/icon.png")
    sys.exit(0)

# the animations (10.): the moving parts' layer, a slide held to the piston's curve (the
# piston alone, rendered as pump-piston-NN, is what pack.py measures: the layer's own centroid
# is the wheel's and the needle's as well); and the glass's contents, a light layer the
# engine tints, moving in place
DECL["passes"] = [p for p in DECL["passes"] if p["kind"] != "light"] + [dict(name="still", kind="still")]
DECL["animations"] = [dict(name="pump", frames=FRAMES, motion="slide", path=PATH, track="piston",
                           turns=False),             # the turntable never turns: only the riser changes
                      dict(name="sight-glass", frames=FRAMES, motion="flow", kind="light")]
STATIC_G = ("static", "glass")


def pin_textures():
    """materials.layered samples world position, so a turning wheel would slide under its own
    rust: each moving part gets its own copy of its material, the position taken from the part's
    own coordinates carried to where it stands in frame 0 -- the same pattern there, riding with
    it after."""
    for g in MOVING:
        for o in PARTS[g]:
            if not o.data.materials:
                continue
            m = o.data.materials[0].copy()
            t = m.node_tree
            geos = [nd for nd in t.nodes if nd.bl_idname == "ShaderNodeNewGeometry"]
            if not geos:
                continue
            tc, mp = t.nodes.new("ShaderNodeTexCoord"), t.nodes.new("ShaderNodeMapping")
            loc, rot, sca = o.matrix_world.decompose()
            mp.inputs["Location"].default_value = loc
            mp.inputs["Rotation"].default_value = rot.to_euler()
            mp.inputs["Scale"].default_value = sca
            t.links.new(tc.outputs["Object"], mp.inputs["Vector"])
            for nd in geos:
                for lk in list(nd.outputs["Position"].links):
                    t.links.new(mp.outputs["Vector"], lk.to_socket)
            o.data.materials[0] = m


def window(x0, x1, y0, y1):
    """Render only a window of the canvas: screen tiles from the origin, x right, y down."""
    cw, ch = CANVAS
    sc.render.use_border, sc.render.use_crop_to_border = True, False
    sc.render.border_min_x = (cw / 2 + x0 * rig.PX_PER_TILE) / cw
    sc.render.border_max_x = (cw / 2 + x1 * rig.PX_PER_TILE) / cw
    sc.render.border_max_y = 1 - (ch / 2 + y0 * rig.PX_PER_TILE) / ch
    sc.render.border_min_y = 1 - (ch / 2 + y1 * rig.PX_PER_TILE) / ch


PUMP_WIN = (-0.25, 1.2, -0.75, 0.15)      # the gauge to the wheel's shadow east; the wheel's top to the roof's foot
GLASS_WIN = (-0.4, 0.15, -1.05, -0.5)    # the glass and its flanges

pose(0)
pose_glass(0)
pin_textures()

if "--collide" in argv:
    # Every moving part, in every frame, against everything fixed: a real intersection test on the
    # evaluated meshes in world space. The rod in the cylinder's bore and on the crank pin, the
    # pin in the wheel, the hub on its shaft and the needle on its dial are meant.
    from mathutils.bvhtree import BVHTree

    def tree(objs):
        dg = bpy.context.evaluated_depsgraph_get()
        verts, polys, owner = [], [], []
        for o in objs:
            if o.type not in ("MESH", "CURVE"):
                continue
            ev = o.evaluated_get(dg)
            me = ev.to_mesh()
            mw = ev.matrix_world
            base = len(verts)
            verts.extend(mw @ v.co for v in me.vertices)
            for pl in me.polygons:
                polys.append([base + i for i in pl.vertices])
                owner.append(o)
            ev.to_mesh_clear()
        return BVHTree.FromPolygons(verts, polys), owner
    fixed, f_own = tree([o for g in ("static", "glass") for o in PARTS[g]])
    clashes = {}
    for f in range(FRAMES):
        pose(f)
        for g in MOVING:
            mv, m_own = tree(PARTS[g])
            for i, j in fixed.overlap(mv):
                clashes.setdefault((g, f_own[i].get("line"), f_own[i].name), set()).add(f)
    for (g, line, name), fs in sorted(clashes.items(), key=str):
        print(f"COLLIDE {g} x fixed line {line} {name}: frames {sorted(fs)}")
    print(f"COLLIDE clashes {len(clashes)}")
    sys.exit(0)

contract.declare(OUT_DIR, canvas=CANVAS, **DECL)
rig.camera(*CANVAS)
with open(os.path.join(OUT_DIR, "pump.json"), "w") as _f:          # for measure_animation.py
    json.dump(dict(frames=FRAMES, loop_s=LOOP_S, kick=[kick(f) for f in range(FRAMES)],
                   level=[fill_level(f) for f in range(FRAMES)], path=PATH, needle_kick=NEEDLE_KICK,
                   throw=THROW, needle_len=0.053,
                   pump_window=PUMP_WIN, glass_window=GLASS_WIN), _f, indent=1)
PUMP, GLASSA = DECL["animations"]

for d in DIRS:
    def path(stem, d=d):
        return f"{OUT_DIR}/{contract.named(stem, d)}.png"
    riser = f"riser-{d}"
    sc.render.use_border = False
    pose(0)
    pose_glass(0)
    setup(visible=STATIC_G + (riser,))
    rig.render(path("idle"))
    # the stopped machine in one render, every moving part at frame 0: the frame-0 check's reference
    setup(visible=STATIC_G + (riser,) + MOVING)
    rig.render(path("still"))
    if IDLE:
        for f in [int(v) for v in os.environ.get("POSES", "").split(",") if v]:   # iterating: other frames
            pose(f)
            rig.render(f"{OUT_DIR}/pose-{f:02d}-{d}.png")
        if os.environ.get("POSES"):
            break                                  # one direction is enough to look at a pose
        continue
    setup(visible=STATIC_G + (riser,) + MOVING, ground=True)
    for o in [o for objs in PARTS.values() for o in objs]:
        o.visible_camera = False
    # Round 7: the cast shadow soft, as a sun shadow reads at this size (the rig's 5 degree
    # sun drew the east mouth's flange as a hard black oval past the footprint, a hole); the
    # flange collar itself casts none (7.)
    SUN.data.angle = math.radians(SHADOW_SUN_DEG)
    rig.render(path("shadow"))
    SUN.data.angle = math.radians(5.0)
    for o in [o for objs in PARTS.values() for o in objs]:
        o.visible_camera = True
    # not packed: the mouth's collar alone, for the registration check (measure.py), and
    # the riser alone, for the check that the four plates agree where it does not reach
    setup(only=PARTS[f"mouth-{d}"])
    rig.render(f"{OUT_DIR}/diag-mouth-{d}.png")
    setup(visible=(riser,))
    rig.render(f"{OUT_DIR}/diag-riser-{d}.png")
    # not packed: the glass alone as the plate shows it, for the check that the light layer
    # never leaves the glass (measure.py)
    setup(visible=("glass",), holdouts=("static", riser))
    rig.render(f"{OUT_DIR}/diag-glass-{d}.png")

    # the sight glass's contents, a frame at a time, everything in front of them cut out (the
    # cage's rods among it), the glass itself left out -- it is what they are seen through
    window(*GLASS_WIN)
    for f in range(FRAMES):
        pose_glass(f)
        setup(visible=("glass-fill",), holdouts=("static", riser) + MOVING)
        rig.render(path(contract.frame(GLASSA["name"], f)))
    pose_glass(0)
    # the moving parts, their shadows caught on the plate under them; only the window round
    # the roof and the gauge changes, so only it is rendered
    window(*PUMP_WIN)
    for f in range(FRAMES):
        pose(f)
        setup(visible=MOVING, catchers=STATIC_G + (riser,))
        rig.render(path(contract.frame(PUMP["name"], f)))
    # the tracked part (contract: track): the piston alone, whole -- inside its cylinder in the
    # layer -- measured by pack.py's slide check and never packed
    for f in range(FRAMES):
        pose(f)
        setup(visible=("piston",))
        rig.render(f"{OUT_DIR}/{contract.track_frame(PUMP['name'], PUMP['track'], f, d)}.png")
    pose(0)
    sc.render.use_border = False

if not IDLE:
    # the collar with no riser at all: what each plate is, away from its riser
    setup(visible=STATIC_G)
    rig.render(f"{OUT_DIR}/diag-bare.png")
