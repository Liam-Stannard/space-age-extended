%s

> ## ADOPTED — this is the Crust Tap
>
> Chosen 2026-09-09 by Liam from five options drawn against each other, after the
> whole set was regenerated twice for the pipe connection. The sheet is locked at
> `concept/crust-tap/adopted/A-sheet.png`. Every other option in
> this directory is rejected and its page has been deleted; the README keeps the
> record of what the five were, what the round measured, and what the two
> regenerations cost.

### Why it won

**It is the wellhead.** A thick armoured collar clamped over a capped bore with
four ground anchors pulling it down — every feature on it exists to hold
something back, which is this building's whole argument. Nothing has to be
explained.

The other four each traded that away for a shape: a wedge sealed by its own
weight (B), a cross-yoke that reads as an X from the map (C), a screwed stuffing
box (D), or a plate pressed almost flat (E). Every one of them is a more
distinctive silhouette, and every one of them says *pressure* less directly.

**It also survived the regeneration best.** The riser leaves square through the
middle of an edge, drops to ground level and ends in an open full-diameter mouth
behind a flange collar — and the rotations move it face to face without the
collar itself changing, which is exactly what four directional plates need.

### What to fix in production, found on review

1. **Detail density, 0.099 against a floor of 0.144.** Two tiles is a quarter of
   a 3×3's canvas and the pipe stub that fixed the connection replaced fussier
   geometry. Stage 1 must load the collar: bolt rings, cleats, tag plates, grease
   nipples, lock wire, chipped cast edges, weld spatter. This is the single most
   important thing about that round.
2. **Luminance 50.6 against a floor of 63.2**, and that is §3.3's doing rather
   than the render's — the spec deliberately sets a tier-0 body darker than the
   mod's usual chassis. **Not fixed here**: it is a decision about the whole tier,
   recorded in the spec's §21 for Liam.
3. **Four plates, and the riser is the fluid box.** Every rotation must be drawn,
   not rotated in software, and `fluid_source_offset` measured off each one. A
   riser drawn on one face and declared on another is the arc mast's
   `lightning_strike_offset` defect wearing different clothes.
4. **The scorched ring in §3.3 must not be baked into the plate.** Ground scatter
   belongs in its own layer — vanilla does this with `mining_drill_scorch_mark` —
   and at 2×2 a ring drawn on the plate would cross the collision box.


**One line.** A low armoured collar clamped over the bore by four heavy ground anchors, with a choked riser leaving one side.

## The idea

§3.1 drawn exactly as written. A squat armoured **collar** — a thick cast ring
with a capped centre — sits over the bore and fills most of the 2 x 2. Four heavy
**ground anchors** at the corners pin it down: bolt plates driven into the crust
with visible washer stacks and tie rods, so the machine is plainly being *held*.
A small bulging **burst disc** sits on the collar's shoulder. On one side a
**riser** leaves the collar, narrows sharply at a **choke**, turns horizontal, and
comes back down to the tile edge; rime stands on it downstream of the choke.

A thin dull orange line of conducted heat glows in the joint where the collar
meets the ground, a few pixels below the rime.

This is the conventional answer, carried as a fair comparison rather than as the
favourite. If none of the other four beats it, that is worth knowing.

## Why it suits this machine

**The anchors are the argument.** §3.1 says every feature exists to contain
pressure, and bolts driven into the ground are the plainest way to say a thing is
trying to lift. Nothing else in the mod's set is anchored down, so it also reads
as specific rather than generic.

**The adjacency lands easily.** The collar's ground joint and the riser's choke
are naturally close together on this shape, which is what §3.3 asks for — hot
seam and cold rime legible in one glance, a few pixels apart.

**And it rotates cleanly.** A ring with a riser on one side is the ideal
four-direction object: the collar is rotationally symmetric, so only the riser
moves, and the other three frames are the first one with a pipe in a different
place. That is exactly the "four arrangements, not four viewpoints" the template
asks for.

## What it risks

**A ring with a pipe is a manhole with a pipe.** At 2 x 2 and very low, the
silhouette is a squashed circle in a square, and there is not much of it. The
anchors and the riser are the only things giving the shape any character, and
anchors are the first detail to be lost at map zoom.

**It is the option closest to the offshore pump.** Not in its parts — there is no
frame and no impeller — but in its *layout*: a low body with pipework leaving one
side is the pump's arrangement, and the pump is the named anti-read.

**The choke is small and it is load-bearing.** §3.2 makes the riser *"visibly
narrower at the throat than at either end"* the thing that says pressure. On a
2 x 2 plate that narrowing is a few pixels wide, and if the sheet comes back with
a constant-diameter pipe, the design has lost its explanation.

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
Crust Tap -- option A, the Bolted Collar.
A very low two-by-two armoured wellhead clamped over a bore in an airless
metallic world, with one choked riser leaving a side.

== FORM ==
- A squat armoured COLLAR filling most of the 2x2 footprint: a thick cast ring
  standing about a third of a tile tall, its centre CAPPED by a bolted plate.
  Nothing can be seen down it.
- FOUR heavy GROUND ANCHORS at the corners: bolt plates driven into the crust,
  washer stacks, tie rods, visibly holding the collar down against something
  trying to lift it
- A small bulging BURST DISC on the collar's shoulder -- a thin domed plate in a
  ring of small bolts, plainly a safety afterthought added to a finished machine
- One RISER leaving one side of the collar: it rises a little, narrows sharply at
  a CHOKE -- visibly thinner at the throat than at either end -- turns horizontal,
  and comes straight back DOWN to terminate at the middle of that tile edge, at
  ground level
- RIME standing on the riser DOWNSTREAM of the choke only
- A thin DULL ORANGE LINE of conducted heat in the joint where the collar meets
  the ground, a few pixels below the rime
- Cast lugs, bolt rings, weld seams and honest wear all over the collar

== COLOUR ==
- Collar and anchors: #3E3B36 to #5E584E, dark warm iron-nickel, cast and bolted
- Riser body: #8A8580, pale grey, the single pipe
- Rime: #BFD8E8 to #EAF4FA, on the riser downstream of the choke ONLY
- Seam heat: #C8541E to #E8A24A, in the ground joint ONLY, dull and narrow
- Burst disc: #C8A23A, one small plate
- Copper and brass: #8A5A32 to #C88A4A, VISIBLE and used freely on fittings,
  bolt threads, gland nuts, tie-rod ends and earthing straps at the anchors.
  This is what keeps the building warm. Do not ration it.
- WARM dark metal, one COLD pipe and one DULL HOT seam. The collar must not
  drift blue.

== RULES ==
- REGISTER: TIER 0, the Foothold -- the first thing built on this planet, made on site from what was to hand. Crude and mechanical: riveted and bolted plate, cast housings, ground anchors, weld seams, honest wear, a burst disc that is plainly an afterthought. Nothing sealed, nothing seamless, no chamfered composite shells, no cryogenic jacketing, no indicator lamps, no light used as a material.
- Draw NO loose material anywhere, and NOTHING ESCAPING: no gas plume, no jet, no
  vapour, no wisp, no haze, no spray. This building's whole argument is that it is
  HOLDING SOMETHING BACK, and a visible leak is the design contradicting itself.
- THE BORE IS CAPPED. No shaft, no hole, no opening, no visible interior, no far
  inner wall, nothing to look down.
- ONE FLUID CONNECTION: the riser's tip. It comes down to GROUND LEVEL and stops
  flush at the middle of a tile edge, square to that face. Axis-aligned, never
  diagonal. It does not leave the roof, it does not stop in mid-air and it does
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
  the thin dull orange line of CONDUCTED HEAT in the ground joint. It is dull,
  narrow, at ground level only, and it is heat through metal -- never a flame,
  never molten anything, never bright.
- THE RIME IS COLD AND CLOSE. Pale frost forms on the BARE PIPE downstream of the
  choke, because gas that expands gets cold. It is rime on metal, not a
  manufactured jacket or a fitted sleeve. It sits within a few pixels of the hot
  ground seam: that ADJACENCY is the signature and both must be legible in one
  glance.
- Not generic science fiction: no neon strip lighting, no holograms, no decals,
  no hazard chevrons used as decoration.
- FORBIDDEN READS: it must NOT read as vanilla's offshore pump -- no water
  anywhere, no impeller, no rotor, no light open frame, nothing that looks like
  it could be lifted by hand. It must NOT read as a lava tap, a magma vent or a
  volcano cap: nothing molten, nothing pouring, nothing bright, and no orange
  above ground level. And it must not read as a manhole cover or a drain: the
  anchors, the burst disc and the choked riser are what make it a machine.

== PANELS ==
- A large hero view of the whole building
- A silhouette panel: the same building as a flat black shape on grey, to prove
  it is readable with no detail at all
- A top-down view from directly overhead, WITHOUT grid lines drawn on it
- A FOUR-ROTATION ROW labelled N, E, S, W: the SAME camera in all four frames with the building turned underneath it, the riser leaving a different face in each. Never a front or a side elevation. Everything except the riser is identical in all four.
- One close-up detail panel: the choke and the collar's ground joint together -- the pipe narrowing at the throat, rime standing on it beyond, and the dull orange seam a few pixels below
- A two-frame state pair: dormant and venting -- the ground seam dark and the riser bare, then the seam a dull orange line and rime standing on the riser beyond the choke. Nothing escapes in either frame.
- A palette strip of six colour swatches

== OUTPUT ==
One landscape concept sheet, 3:2, labelled panels on a dark charcoal background,
in the style of a game art bible page. Title the sheet CRUST TAP -- BOLTED COLLAR -- use exactly
that name, do not invent a generic descriptive title. Panel labels only; no
other text anywhere on the sheet.
```

## Round 1 — what came back

`concept/crust-tap/options/A-sheet.png`, generated 2026-09-09 from the prompt above with the four attachments named
in the README. One generation, no refinements.

**Measured:** luminance **50.9**, saturation **0.229**, edge density **0.112**.
Band from the four vanilla references: luminance 63.2-90.4, saturation 0.230-0.490, edge density 0.144-0.261. The *aspect* column and its "perspective low" verdict are ignored, as they are on every sheet in this repo: they measure the panel bounds, not the building.

**What landed.** The four-rotation row came back as rotations rather than
elevations — the same camera with the building turned under it and the riser
moving face to face — which is the thing this building had to prove. Anchors,
burst disc, choke and the rime-above-a-hot-seam adjacency are all present.

**What to weigh.** Darkest of the five and the least distinctive from above: a
ring on a square. The rotations are its best argument.

## Round 2 — regenerated, because the pipe could not be connected to

`concept/crust-tap/options/A-sheet.png`, generated 2026-09-09. **This
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

**Measured:** luminance **50.6**, saturation **0.211**, edge density **0.099**.

**The connection is right now.** The riser leaves square through the middle of
the near edge, drops to ground level and ends in an open, full-diameter pipe
mouth behind a flange collar — and the connection panel draws an ordinary pipe
butted onto it. The four rotations move the riser face to face and every one of
them is perpendicular.
