# Option A — the Shaker Deck

**One line.** A stepped armoured housing riding on compressed leaf springs, with an eccentric flywheel spinning at its high end.

## The idea

The screens are inside; the *shake* is outside. Three descending planes in
the roofline say there is a cascade under them, four compressed leaf springs and
one spinning eccentric say the whole body is moving, and neither of those reads
needs the machine to be open.

This is the v1 draft's direction, carried forward as a fair comparison rather
than as the favourite. It is the most conventional answer here, and if one of the
other four does not beat it, that is worth knowing.

## Why it suits this machine

Vibration is the mechanism, and vibration is the one process that survives
enclosure completely: springs and an offset flywheel are legible from any angle,
where an open mesh tray would just be an empty tray. The stepped roofline is the
recipe -- coarse at the top, fine at the bottom -- drawn on the outside of the
machine.

Tier 0-1 wants exposed mechanism, and this design has exactly two: the springs
and the drive. Everything else is a machined shell.

## What it risks

**It is a box with things on it.** The silhouette from directly above is a
rectangle, and the stepped roofline is the only thing separating it from the
Vacuum Furnace, the Drop Crusher and every other low grey machine on the Core.

**The slope invites a corner-on drawing.** The template records this happening to
this very building: a directional form makes a generator want to turn the machine
to show the slope off. The prompt puts the slope in the ROOF and keeps the walls
upright, which leaves nothing to turn.

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
Dross Classifier -- option A, the Shaker Deck.
A low three-by-three vibrating classifier: a sealed stepped housing riding on
leaf springs, with an eccentric drive at one end.

== FORM ==
- A heavy machined housing filling the 3x3 footprint, its ROOF stepping down in
  three distinct planes from the drive end to the discharge end. The walls stay
  vertical and square; only the roof slopes.
- Four compressed leaf-spring stacks, one at each corner, visibly bearing the
  whole body's weight and visibly loaded
- A small offset flywheel drive in a guarded housing at the high end, with a
  belt cover and a counterweight boss
- Two shallow discharge bins built into the housing at the low end, on opposite
  faces, both drawn EMPTY and closed
- Inspection hatches with bolt rings on each roof plane, and a grab rail

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

== PANELS ==
- A large hero view of the whole building
- A silhouette panel: the same building as a flat black shape on grey, to prove
  it is readable with no detail at all
- A top-down view from directly overhead, WITHOUT grid lines drawn on it
- Two close-up detail panels: one corner's leaf-spring stack under load; and the eccentric drive with its belt cover off
- A two-frame state pair: the housing at both ends of its shake, the whole body displaced a few centimetres between the two frames
- A palette strip of six colour swatches

== OUTPUT ==
One landscape concept sheet, 3:2, labelled panels on a dark charcoal background,
in the style of a game art bible page. Title the sheet DROSS CLASSIFIER -- SHAKER DECK -- use exactly
that name, do not invent a generic descriptive title. Panel labels only; no
other text anywhere on the sheet.
```

## Round 1 — what came back

`graphics/entity/dross-classifier/concept/options/A-sheet.png`, generated 2026-09-08 from the prompt above with the four attachments named
in the README.

**Measured:** luminance **61.4**, saturation **0.150**, edge density **0.122**.
Band from the four vanilla references: luminance 63.2-90.4, saturation 0.230-0.490, edge density 0.144-0.261. The *aspect* column `check-sheet-style.py` prints is meaningless on a whole sheet -- it measures the sheet's panel bounds, not the building -- so its "perspective low" verdict is ignored here, as `array-options/README.md` says it must be.

**What landed.** The three descending roof planes, the four corner spring
stacks, the guarded drive with its belt cover, bolt rings on every plane. Square
to the grid, roof-dominant, the base reads as a square. The silhouette panel is
an honest lumpy rectangle -- which is the finding, not a complaint.

**What to weigh.** It is the safest of the five and the least distinctive: at a
glance it is a box with a stepped lid, and the Vacuum Furnace and Drop Crusher
are also boxes. The roof steps read more as an arched ribbed cover than as three
flat planes.
