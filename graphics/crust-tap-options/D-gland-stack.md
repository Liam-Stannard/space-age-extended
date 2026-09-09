# Option D — the Gland Stack

**One line.** A stack of stepped screwed gland rings tightened down on the bore, like a stuffing box the size of a building.

## The idea

Draw the seal as a *thread*. Four cast rings of decreasing diameter stack over the
bore — the widest at the ground, the smallest at the top — each one a **screwed
gland ring** with wrench flats around its rim, separated from the next by a ring
of **jack bolts**. The whole thing is a stuffing box: something screwed down on a
hole until it stops leaking, then screwed down further.

The crown is a small capped disc with a **burst disc** beside it. The **riser**
leaves the second ring from the ground, chokes as it turns outward, and steps down
to the tile edge.

From above it is a set of concentric circles with flats on them, stepping smaller
as they rise. That is the silhouette: a ziggurat of nuts.

## Why it suits this machine

**A thread is the most legible "tightened" in industrial design.** Anchors say
*held down*; bolts say *fastened*; wrench flats and jack bolts say *someone
torqued this, and can torque it again*. On a machine whose whole read is
containment, that is the most specific vocabulary available, and none of the other
four uses it.

**It gives the two-temperature read a ladder to sit on.** The ground seam is at
the widest ring's foot, and the riser leaves one ring up — so hot and cold end up
vertically stacked a few pixels apart, which is exactly the adjacency §3.3 asks
for, drawn as a step rather than a gap.

**And it is dense.** Four rings of wrench flats, three rings of jack bolts and a
capped crown is a lot of edge in a 2 x 2. Detail density is the metric the last
round failed hardest — the Whisker Comber measured 0.114 against vanilla's 0.144
floor — and this is the option most likely to clear it.

## What it risks

**It is a stack of nuts, and a stack of nuts is a bolt.** At map zoom, concentric
stepped circles read as a fastener, a valve handwheel or a hydrant — all of them
things you would find *on* a machine rather than things that *are* one. The riser
and the burst disc are the only parts that say building.

**Concentric circles also read as a target**, which is the sort of thing a
generator will happily make graphic and symmetrical. It must stay a cast object
with wear on it, not a diagram.

**It is the tallest of the five for its footprint**, and §4 is explicit that this
building is *"2 x 2 and very low"* because *"the interesting thing about this
building is where it is, not how tall it is."* Four stacked rings fights that.
Keeping the whole stack under half a tile is what stops it becoming a bollard, and
it is the first thing to check on the sheet.

## Concept Sheet Prompt

```text
FACTORIO SPACE AGE BUILDING -- CONCEPT SHEET

== CAMERA ==
Match the attached vanilla sprites exactly: looking steeply down from above,
MOSTLY ROOF with only a shallow near face visible. Square to the tile grid --
the near face parallel to the bottom edge of the frame, the side faces parallel
to the left and right edges. The square base must read as a SQUARE, never as a
diamond or a rhombus. Not rotated corner-on. Not a flat front elevation.
The attached vanilla sprites are STYLE references only: match the camera,
rendering, finish, LEVEL OF DETAIL and COLOUR TEMPERATURE; do NOT copy the
design, shape or components. The attached sheet of our own is a FORMAT reference
only: match its panel layout and information panels. The machine in it is a
different building of ours and this one must look like nothing else.

== THE RISER'S ALIGNMENT -- READ THE ATTACHED DIAGRAM ==
One attachment is a flat GEOMETRY DIAGRAM of this building's 2x2 footprint seen
from directly above: a black square with its four face midpoints marked, a green
arrow leaving one of them, and red crosses over all four diagonals. It is a
geometry reference ONLY -- do not copy its flat colours, its lines, its arrows or
its text into the sheet.

What it says is the hardest rule on this building. THE RISER LEAVES AT NINETY
DEGREES TO ONE EDGE OF THE SQUARE BASE, THROUGH THE MIDDLE OF THAT EDGE. Its
centreline runs parallel to the other two edges of the base. It NEVER points at a
corner, NEVER leaves on a diagonal, and NEVER runs at an angle between two edges.
The base's four edges must stay straight and legible so that alignment can be
judged at a glance.

This is not a stylistic preference. In game a pipe connection lands on the tile
boundary the prototype names, and a player's pipe arrives there and nowhere else,
so a riser aimed between two edges is aimed at no tile at all. The first round of
this building failed on exactly this point -- every one of the five drew the
riser heading toward a corner -- which is why the diagram is attached.

== THE PIPE CONNECTION -- IT MUST ACTUALLY CONNECT ==
The other attachment is a vanilla PUMP with vanilla PIPES butted onto it. Copy
the CONNECTION from it and nothing else -- not the machine, not its shape, not
its colours.

The riser's last section IS A PIPE. It is a straight, open-ended, cylindrical
pipe stub of THE SAME DIAMETER as the vanilla pipe in that image, running
horizontally at ground level, its open mouth flush with the middle of the tile
edge and square to it, so that a pipe placed on the next tile meets it END TO
END and the two read as one run.

It does NOT end in a cap, a plug, a nozzle, a gland, a bulb, a taper, a cone or a
closed face. It does not narrow at the mouth. It does not stop short of the edge
and it does not overshoot it. A flange collar just behind the mouth is right and
vanilla does exactly that; the mouth itself stays open and full width.

== BUILDING ==
Crust Tap -- option D, the Gland Stack.
A very low two-by-two wellhead built as a stuffing box: four stepped screwed
gland rings tightened down over the bore.

== FORM ==
- FOUR cast GLAND RINGS stacked over the bore, decreasing in diameter as they
  rise: the widest fills most of the 2x2 footprint at ground level, the smallest
  is about a third of that at the top. The whole stack stands UNDER HALF A TILE
  tall -- this is a low building.
- Each ring carries WRENCH FLATS around its rim -- it is a thing that was screwed
  down and can be screwed down again
- Between each pair of rings, a ring of JACK BOLTS with lock nuts, visibly loaded
- The CROWN is a small capped disc with a bolt ring. Nothing can be seen down it.
- A small bulging BURST DISC beside the crown -- a thin domed plate in a ring of
  small bolts, plainly a safety afterthought
- One RISER leaving the SECOND RING from the ground: it turns outward, narrows
  sharply at a CHOKE -- visibly thinner at the throat than at either end -- steps
  down, and terminates at the middle of one tile edge, at ground level
- RIME standing on the riser DOWNSTREAM of the choke only
- A thin DULL ORANGE LINE of conducted heat in the joint where the widest ring
  meets the ground, a few pixels below the rime
- Cast texture, weld seams, peened threads and honest wear on every ring

== COLOUR ==
- Gland rings: #3E3B36 to #5E584E, dark warm iron-nickel, cast, worn at the
  wrench flats
- Riser body: #8A8580, pale grey, the single pipe
- Rime: #BFD8E8 to #EAF4FA, on the riser downstream of the choke ONLY
- Seam heat: #C8541E to #E8A24A, in the ground joint ONLY, dull and narrow
- Burst disc: #C8A23A, one small plate
- Copper and brass: #8A5A32 to #C88A4A, VISIBLE and used freely on the jack-bolt
  heads, gland nuts, thread collars, the riser's fittings and earthing straps.
  This is what keeps the building warm. Do not ration it.
- WARM dark metal, one COLD pipe and one DULL HOT seam. The rings must not drift
  blue.

== RULES ==
- REGISTER: TIER 0, the Foothold -- the first thing built on this planet, made on site from what was to hand. Crude and mechanical: cast housings, exposed screw threads, jack bolts, weld seams, honest wear, a burst disc that is plainly an afterthought. Nothing sealed, nothing seamless, no chamfered composite shells, no cryogenic jacketing, no indicator lamps, no light used as a material.
- Draw NO loose material anywhere, and NOTHING ESCAPING: no gas plume, no jet, no
  vapour, no wisp, no haze, no spray. This building's whole argument is that it is
  HOLDING SOMETHING BACK, and a visible leak is the design contradicting itself.
- THE BORE IS CAPPED. No shaft, no hole, no opening, no visible interior, no far
  inner wall, nothing to look down.
- IT IS LOW. The whole stack stays under half a tile tall; this building's
  interest is where it is, not how tall it is.
- ONE FLUID CONNECTION: the riser's tip. It steps down to GROUND LEVEL and stops
  flush at the middle of a tile edge, square to that face. Axis-aligned, never
  diagonal. It does not leave the crown, it does not stop in mid-air and it does
  not cross the edge of the footprint. It is drawn into the building's own art.
- NO item ports of any kind, no chutes, no bins, no hatches aimed at a tile: no
  inserter ever touches this machine. NO electrical connector and no cables
  either -- this machine draws no power at all.
- Nothing extends sideways past the 2x2 footprint, riser included. Two tiles is
  small and the riser is what will cross the line; keep it inside.
- NO GROUND IS DRAWN: no scorch ring, no ground plane, no gravel, no rock, no
  scenery, no baked drop shadow. The machine is drawn on its own.
- Airless metallic world, gravity 50: nothing burns and nothing blows about.
  No flame, no exhaust, no steam, no smoke, no fire, no dust cloud, anywhere.
- THE HEAT IS UNDERGROUND AND STAYS THERE. The only warm thing on the machine is
  the thin dull orange line of CONDUCTED HEAT in the ground joint at the widest
  ring's foot. It is dull, narrow, at ground level only, and it is heat through
  metal -- never a flame, never molten anything, never bright.
- THE RIME IS COLD AND CLOSE. Pale frost forms on the BARE PIPE downstream of the
  choke, because gas that expands gets cold. It is rime on metal, not a
  manufactured jacket or a fitted sleeve. It sits one ring above the hot ground
  seam and a few pixels from it: that ADJACENCY is the signature and both must be
  legible in one glance.
- IT IS A CAST OBJECT, NOT A DIAGRAM. The rings are worn, chipped and unevenly
  seated; they are not perfect concentric graphics.
- Not generic science fiction: no neon strip lighting, no holograms, no decals,
  no hazard chevrons used as decoration.
- FORBIDDEN READS: it must NOT read as vanilla's offshore pump -- no water
  anywhere, no impeller, no rotor, no light open frame, nothing that looks like
  it could be lifted by hand. It must NOT read as a lava tap, a magma vent or a
  volcano cap: nothing molten, nothing pouring, nothing bright, and no orange
  above ground level. And it must NOT read as a giant bolt head, a valve
  handwheel, a fire hydrant or a target: it is a building on the ground, and the
  riser, the burst disc and the ground seam are what say so.

== PANELS ==
- A large hero view of the whole building
- A silhouette panel: the same building as a flat black shape on grey, to prove
  it is readable with no detail at all
- A top-down view from directly overhead, WITHOUT grid lines drawn on it
- A FOUR-ROTATION ROW labelled N, E, S, W: the SAME camera in all four frames with the building turned underneath it, the riser leaving toward a different face in each. Never a front or a side elevation. Everything except the riser is identical in all four.
- One close-up detail panel: two gland rings with the jack bolts between them, the riser leaving the second ring at its choke with rime beyond it, and the dull orange ground seam a few pixels below
- A two-frame state pair: dormant and venting -- the ground seam dark and the riser bare, then the seam a dull orange line and rime standing on the riser beyond the choke. Nothing escapes in either frame.
- A palette strip of six colour swatches

== OUTPUT ==
One landscape concept sheet, 3:2, labelled panels on a dark charcoal background,
in the style of a game art bible page. Title the sheet CRUST TAP -- GLAND STACK -- use exactly
that name, do not invent a generic descriptive title. Panel labels only; no
other text anywhere on the sheet.
```

## Round 1 — what came back

`graphics/entity/crust-tap/concept/options/D-sheet.png`, generated 2026-09-09 from the prompt above with the four attachments named
in the README. One generation, no refinements.

**Measured:** luminance **53.0**, saturation **0.207**, edge density **0.084**.
Band from the four vanilla references: luminance 63.2-90.4, saturation 0.230-0.490, edge density 0.144-0.261. The *aspect* column and its "perspective low" verdict are ignored, as they are on every sheet in this repo: they measure the panel bounds, not the building.

**What landed.** Four stepped rings with wrench flats and jack bolts, under half
a tile tall, with the riser leaving the second ring at its choke.

**What to weigh.** **The only sheet of the thirty drawn across both rounds that
the checker flags as `detail low`** — 0.084 against a floor of 0.144. Concentric
rings are a shape with very little edge in them, and at 2 x 2 there is not much
canvas to add any. That is a real finding about the design, not about this
render.

## Round 2 — regenerated, because the pipe could not be connected to

`graphics/entity/crust-tap/concept/options/D-sheet.png`, generated 2026-09-09. **This
sheet replaces round 1's**, whose numbers above are superseded.

**Two defects, both Liam's, both about the same thing.** Round 1 drew every riser
heading toward a *corner* of the footprint — in game a fluid connection lands on
the tile boundary the prototype names, so a pipe aimed between two edges is aimed
at no tile at all. The first re-prompt fixed the angle and produced risers that
ended in nozzles and bulbs: square, and still impossible to plumb.

**What fixed it was two attachments rather than more words**, which is Appendix
B's own lesson about geometry. A flat diagram of the 2 x 2 footprint with the
four edge midpoints marked, a green arrow leaving one and red crosses on the
diagonals; and a vanilla **pump with vanilla pipes butted onto it**, captioned as
the connection to copy and nothing else. Three rounds of prose had not landed it;
one picture of the mating did.

**Measured:** luminance **54.6**, saturation **0.189**, edge density **0.098**.

**The connection is right now** — the riser leaves the second ring, steps down,
chokes, widens back and ends in an open mouth at the edge midpoint.

**The extra hardware helped.** Round 1 measured 0.084 and was the only sheet the
checker flagged; asking for grease nipples, lock wire, tag plates and chipped
edges took it to 0.098 and cleared the flag. Still under the floor, and still the
least dense idea in the set.
