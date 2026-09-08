# Option E — the Spiral Rake

**One line.** A closed settling box with a single inclined rake leg climbing out of it, screwing the coarse fraction up and out.

## The idea

A rake classifier: the body is a low closed settling box, and one inclined
armoured leg rises out of it at a shallow angle, carrying an auger that walks the
heavy fraction up the slope while the fines stay behind. One diagonal against one
box -- an L, which is a silhouette the Core does not have anywhere.

The auger is inside its own casing. What shows is the leg, its drive head at the
top, and the closed discharge boot under it.

## Why it suits this machine

The two products leave in two physically different ways -- one is walked up
and out, one stays down -- which is the recipe made visible without drawing a
single grain of anything.

It is also the cheapest of the five to animate later: one rotating drive head at
the top of the leg, and nothing else on the building has to move.

## What it risks

**The inclined leg is a corner-on trap.** A diagonal element is exactly
what makes a generator want to rotate the whole machine, and the template records
this building doing that once already. The prompt fixes the leg parallel to one
face and says so twice.

**It can read as a conveyor**, which is a belt device, and the spec's first
anti-read is a splitter. The armoured closed casing, with no belt visible
anywhere and a screw drive head rather than a pulley, is the defence.

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

== BUILDING ==
Dross Classifier -- option E, the Spiral Rake.
A three-by-three classifier: a low closed settling box with one inclined armoured
screw leg climbing out of it.

== FORM ==
- A low closed box occupying most of the footprint, machined, with bolt rings, a
  bolted inspection door and a sealed lid
- One INCLINED ARMOURED LEG rising from the box at about thirty degrees. Its
  axis is parallel to one face of the square base and rises straight out over
  that face -- never diagonally across the corner of the footprint
- The leg is a closed tube casing, not an open trough and not a belt: a screw
  drive head in a guarded housing caps its top end
- Under the leg's head, a closed EMPTY discharge boot with a hinged flap
- A second closed outlet low on the opposite face of the box, drawn shut
- The leg is braced back to the box roof by two struts, and the whole assembly
  stays inside the 3x3 square in plan

== COLOUR ==
- Frame and housing: #4A463F to #6E685C, warm low-value iron-nickel
- Screen decks and mesh: #8A8580, pale grey, on the sorting surfaces only
- Springs, drive and mechanism: #3B3B40, near-black steel
- Pale nickel-white: #B9B4A8, on chamfers, covers and end caps
- Copper and brass: #8A5A32, used sparingly on the drive end only
- WARM, not cold. The attached sprites are brown-grey with copper in them.

== RULES ==
- REGISTER: TIER 0-1, the landing-day machines, but deliberately built. Mostly mechanical: cast housings, bolted plate, one or two exposed mechanisms, weld seams, honest wear. Machined enough to look built rather than knocked together, but nothing sealed, nothing seamless, no indicator lamps, no light used as a material.
- Draw NO loose material anywhere: no ore, powder, grit, fibre, debris or
  product on the ground, in bins, at chutes, in trays, or spilling from the
  machine. Factorio machines never show what they make, so every chute, port,
  bin, tray and mouth is drawn as EMPTY machinery.
- The working chamber is enclosed. An open frame around an empty bed advertises
  that emptiness on every tick and the machine reads as idle while it runs.
- NO output port and no output chute aimed at a tile: this machine holds its
  products until an inserter takes them, and the inserter may stand on any
  adjacent tile. Vanilla's assembling machines draw no output port at all.
- Nothing extends sideways past the 3x3 footprint. Height above it is fine;
  width is not.
- No pipe flanges and no fluid connections: this machine has no fluid box. No
  visible electrical connector either -- power arrives from a pole off-frame.
- Airless metallic world, gravity 50: nothing burns and nothing blows about.
  No flame, no exhaust, no steam, no smoke, no fire, no dust cloud, anywhere.
- NOTHING GLOWS. Dross is what settled out; it is cold by the time it
  reaches this machine. No lit panels, no emissive anything.
- Not generic science fiction: no neon strip lighting, no holograms, no decals,
  no hazard chevrons used as decoration.
- FORBIDDEN READS: it must not read as a belt splitter -- not flat, not low, not
  symmetrical about both axes -- and it must not read as a plain crate or
  a shipping container. It is a machine that visibly MOVES.
  It must NOT read as a conveyor or a belt: no belt, no pulleys, no rollers, no
  open trough of material. It must not read as an artillery piece or anything
  aimed: the leg is short, thick, obviously a casing, and it ends in a drive
  head and a discharge boot rather than a mouth.

== PANELS ==
- A large hero view of the whole building
- A silhouette panel: the same building as a flat black shape on grey, to prove
  it is readable with no detail at all
- A top-down view from directly overhead, WITHOUT grid lines drawn on it
- Two close-up detail panels: the screw drive head and its guarded housing at the top of the leg; and where the leg meets the settling box, with its bracing struts
- A two-frame state pair: the drive head at two points in its rotation
- A palette strip of six colour swatches

== OUTPUT ==
One landscape concept sheet, 3:2, labelled panels on a dark charcoal background,
in the style of a game art bible page. Title the sheet DROSS CLASSIFIER -- SPIRAL RAKE -- use exactly
that name, do not invent a generic descriptive title. Panel labels only; no
other text anywhere on the sheet.
```

## Round 1 — what came back

`graphics/entity/dross-classifier/concept/options/E-sheet.png`, generated 2026-09-08 from the prompt above with the four attachments named
in the README.

**Measured:** luminance **63.3**, saturation **0.200**, edge density **0.127**.
Band from the four vanilla references: luminance 63.2-90.4, saturation 0.230-0.490, edge density 0.144-0.261. The *aspect* column `check-sheet-style.py` prints is meaningless on a whole sheet -- it measures the sheet's panel bounds, not the building -- so its "perspective low" verdict is ignored here, as `array-options/README.md` says it must be.

**What landed.** The closed settling box, the armoured leg with its screw drive
head, the bracing struts, the discharge boot. The L-shape is unmistakable in the
silhouette panel and nothing else in the mod has it.

**What to weigh.** The leg rises toward the viewer rather than straight out over
one face, so the machine reads as turned a few degrees even though the base is
square -- the same pull that turned option C, arriving in a milder form. And the
leg is drawn long enough that a plate cut from this would need checking against
the 3x3 footprint before anything else.
