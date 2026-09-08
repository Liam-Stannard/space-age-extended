# Option F — the Field Ring

**One line.** A seamless monolithic ring around an open bore, with a containment gap where a coil should be and nothing visible inside it. 9x9 tiles.

*The tier-4 counterpart of option A, the Coil Ring.*

## The idea

Option A's geometry with option A's fabrication removed. The ring is cast
whole. The hundred field coil segments are not visible as a hundred objects: they
are a single continuous field held in a gap, and what fills is the gap.

This is the version that actually answers the tier: a player who has been staring
at riveted plate for forty hours arrives at a thing with no fasteners on it at
all, and the difference reads instantly.

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

Light in the gap, running round it. Because the gap is continuous the
fill is continuous, so `crafting_progress` maps onto it exactly with no stepping
and no hundred discrete lamps to draw.

The shell never lights. Only the gap does, which is what "contained light doing
the work" means and what separates this from a building with glowing panel lines.

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
Ignition Array - option F, Field Ring.
A seamless monolithic ring around an open bore, with a containment
gap where a coil should be and nothing visible inside it. 9x9 tiles.

== FORM ==
- A single unbroken torus of dark composite, wider than tall, sitting low
- An open bore straight down through the centre, background visible through it
- The bore is roughly two thirds of the building's width
- A narrow containment gap running the whole way round the inner face, with
  nothing solid inside it -- the coil is a field, not an object
- Chamfered pale composite inlays where the ring meets the ground
- No fasteners, no seams, no pipework anywhere on the shell

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
- Must read as one solid object that was cast whole, not as parts assembled.
  Not a rocket silo, and not a ring of separate machines.

== PANELS ==
- A large hero view of the building
- A tile-grid panel from directly overhead on a 9x9 tile grid, the building
  inside the grid with no part crossing the edge
- Three close-up detail panels: the containment gap seen close, empty and dark; the chamfered inlay
where the shell meets the ground; the lip of the bore
- A row of five charge key frames labelled 0%, 25%, 50%, 75%, 100%, showing
  light appearing inside the containment gap and travelling round it,
faint at 25%, a continuous ring of contained violet light at 100% - the light is
inside the gap, the shell itself never glows
- A layer breakdown row: shadow, bare shell, charge overlay, discharge
- A palette strip of eight colour swatches

== OUTPUT ==
One landscape concept sheet, 3:2, labelled panels on a dark charcoal background,
in the style of a game art bible page. Panel labels only; no other text.
```
