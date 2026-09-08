# Option J — the Containment Well

**One line.** A shallow seamless bowl around a well, with a ring suspended above it held by nothing visible. 9x9 tiles.

*The tier-4 counterpart of option E, the Crust Anchor.*

## The idea

The most exotic option in either set, and the only one where the charge
changes the building's *shape* rather than its colour. A suspended ring is the
clearest possible statement of "field effects" and "machinery implied rather than
shown": the mechanism is invisible and its effect is not.

It is also the only design that cannot be misread as belonging to an earlier
tier, because nothing at an earlier tier could hold something in the air.

## Why it suits the Core

The Array is **tier 4** in `building-spec-template.md`'s ladder — "exotic; barely
reads as machinery: field effects, superconducting elements, monolithic surfaces
with no seams at all, contained light doing the work". Options A–E were written
in tier-0 vocabulary — riveted, bolted, rust in the seams — which is what the
landing-day machines look like, not the last building in the game.

The register is the point of this option, not a coat of paint on the previous
one. A player should be able to read their own progress off the factory floor,
and the Drop Crusher's exposed gears only land as *early* if the endgame has
nothing exposed at all.

Everything the Core demands still holds: a dead dynamo rather than a rocket,
nothing that burns, massive under gravity 50, cold because it is superconducting.

## The charge display

The ring rises and lights. Two channels at once -- position and
brightness -- so the fill is readable even at a glance and even in silhouette.

The risk is engine-side rather than artistic: the ring has to be a separate drawn
sprite whose offset is animated, which is more `LuaRendering` work than any other
option, and a hovering object needs its shadow handled or it will look pasted on.

## Cost and risk

Tier 4 is *cheaper* to draw than tier 0, not dearer — fewer parts, fewer
fasteners, fewer greebles — but less forgiving, because a seamless form has
nothing to hide behind and every proportion shows.

## Concept Sheet Prompt

```text
FACTORIO SPACE AGE BUILDING -- CONCEPT SHEET

== CAMERA ==
Match the attached vanilla sprites exactly: steeply down from above, MOSTLY ROOF
with only a shallow near face. Square to the tile grid. Not rotated corner-on.
Not a flat front elevation.
The four attached sprites are style references only: match the camera, rendering,
finish and level of detail; do NOT copy the design, shape, colours or components.

== BUILDING ==
Ignition Array - option J, Containment Well.
A shallow seamless bowl around a well, with a ring suspended above
it held by nothing visible. 9x9 tiles.

== FORM ==
- A shallow bowl of dark composite set into the ground, filling the footprint
- A well at its centre, open, dark, the ground visible falling away
- A single slender ring hovering above the bowl, level, with no supports,
  no struts and no cables of any kind
- The gap between ring and bowl is clearly empty
- The bowl's inner face is smooth and unbroken, chamfered at the rim
- No legs, no anchors, no fasteners, no pipework

== COLOUR ==
- Shell: #2E3138 to #4A4F58, dark composite, matte, seamless
- Pale composite: #C9CBD0, on chamfers and inlays only
- Cryogenic jacket: #A8B6C2, cold pale blue-grey
- Contained light: violet-white #C9B6FF ramping to #FFFFFF, in the charge frames
- Almost no copper and NO rust. This building is later in the tech tree than
  anything around it and its surfaces have never been improvised or repaired.

== RULES ==
- TIER 4, THE LAST BUILDING IN THE GAME. Exotic, quiet, sealed. It should barely
  read as machinery. Seamless monolithic surfaces, chamfered forms, superconducting
  elements, contained light doing the work, machinery implied rather than shown.
- NO rivets, NO bolts, NO weld seams, NO rust, NO exposed fasteners, NO lattice
  framework, NO exposed gears, pipes, cables or linkages on primary faces.
- Still Factorio, not generic science fiction: physical, weighty, industrial,
  grounded. Futuristic through material and finish, not through neon strip
  lighting, holograms, decals or glowing panel lines everywhere.
- Airless metallic world, gravity 50: massive and low. Nothing is delicate.
- Nothing burns here. No flame, no exhaust, no steam, no smoke, no fire, anywhere.
- Nothing glows at rest. Violet appears only in the charge frames.
- The building sits inside a 9x9 tile square with no part crossing the edge.
- Must read as a ring held in the air by the machine below it, not as a ring
  on a stand, not as a portal or gateway, and not as decoration.

== PANELS ==
- A large hero view of the building
- A tile-grid panel from directly overhead on a 9x9 tile grid, the building
  inside the grid with no part crossing the edge
- Three close-up detail panels: the gap between the hovering ring and the bowl beneath it; the rim of
the well; the chamfered outer edge of the bowl
- A row of five charge key frames labelled 0%, 25%, 50%, 75%, 100%, showing
  the hovering ring lighting from within and rising slightly higher above
the bowl as charge climbs, dark and low at 0%, bright violet and at its highest
at 100%
- A layer breakdown row: shadow, bare shell, charge overlay, discharge
- A palette strip of eight colour swatches

== OUTPUT ==
One landscape concept sheet, 3:2, labelled panels on a dark charcoal background,
in the style of a game art bible page. Panel labels only; no other text.
```
