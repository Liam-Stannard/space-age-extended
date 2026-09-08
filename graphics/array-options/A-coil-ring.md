# Option A — the Coil Ring

**One line.** A squat armoured ring of field coil segments laid end to end
around a wide open bore, and the segments light as you build them.

## The idea

The Array's charge *is* a hundred `sae-field-coil-segment`s. Every other option
has to invent somewhere to display that number; this one puts the segments
themselves on the outside of the building and lets the player watch the ring
close. The thing you are manufacturing and the thing you are looking at are the
same object, which is the strongest link between mechanic and art available
here.

The bore is wide — most of the footprint — because the machine is a winding
around a hole, not a box with a hole in it. The current has to go somewhere, and
the somewhere is straight down.

## Why it suits the Core

A ring of superconducting coils around a vertical shaft is, physically, how you
would drive a current into a planet's crust to restart a dynamo. The fiction and
the silhouette agree without either being bent. Squat and heavily braced for
gravity 50; rimed rather than hot; no plume anywhere.

## Massing and palette

Octagonal, wider than tall, sitting low. Weathered kamacite plate and welded
seams, rust in the water-traps, copper busbars running between segments. Frost
collecting on the coil housings and nowhere else, which is the one cue that
these are cold and everything around them is not.

## The charge display

**Segment by segment, around the ring.** At 0% every coil housing is dark
metal. Each completed segment lights one housing violet, and it stays lit. The
ring closes clockwise, so the player reads position as progress from across the
screen — a gauge with a hundred divisions that is also the building.

`crafting_progress` fades the *next* housing in, so it breathes between
segments instead of stepping.

At 100% the whole ring is lit and the bore is still dark. Ignition is then the
only moment the shaft lights, which is worth saving.

## Plates

`base` (unlit ring), `charge-overlay` (all housings lit, drawn at ramping alpha
per housing), `hole` (the shaft), `shadow`. Four, and the overlay is cut from
the base by the same tooling that already exists.

## Cost and risk

Cheapest of the five: r4 is already most of this building, so it is a re-cut
plus one overlay rather than a fresh design. The risk is that it is the safe
answer — it is the shape we have been drawing for three versions, and picking it
means the comparison changed nothing.

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
Ignition Array - option A, Coil Ring.
A squat octagonal machine ring with a wide open shaft straight down
through its middle. 9x9 tiles.

== FORM ==
- Outer silhouette an octagon, wider than it is tall, sitting low
- A shaft straight through the centre, open, the background visible through it
- The shaft is roughly two thirds of the building's width
- A continuous chain of superconducting coil housings laid end to end around the
  ring: thick cylindrical windings in armoured cradles
- Copper busbars linking each housing to the next
- Frost and rime collecting on the coil housings and nowhere else
- A bolted armoured collar at the lip of the shaft

== COLOUR ==
- Body casing: #4A463F to #6E685C, warm low-value iron-nickel, old dark cast iron
- Pale nickel-white: #B9B4A8, confined to bolt rings and end caps
- Ceramic: #C9C0AC, the lightest value on the building
- Copper: #8A5A32, confined to busbars and straps
- Charge: violet-white #C9B6FF ramping to #FFFFFF, in the charge frames only
- NOT pale galvanised or bleached weathered steel. That is the default drift and
  it must be argued down. Warm dark desaturated steel, so violet is the only
  saturated colour on the sheet.

== RULES ==
- Airless metallic world, gravity 50: squat, thick, anchored. Nothing cantilevers,
  nothing is delicate, nothing is slender.
- Nothing burns here. No flame, no exhaust, no steam, no smoke, no fire, anywhere
  on the sheet, in any panel.
- Superconducting, therefore cold. Frost and rime are correct; glowing hot metal
  is wrong.
- Nothing glows at rest. Violet appears only in the charge frames.
- The building sits inside a 9x9 tile square with no part crossing the edge.
- Must read as a winding around a bore, not a rocket silo: no launch clamps,
  no gantry, no blast doors, nothing aimed upward.

== PANELS ==
- A large hero view of the building
- A tile-grid panel from directly overhead on a 9x9 tile grid, the building
  inside the grid with no part crossing the edge
- Three close-up detail panels: one coil housing in its armoured cradle with frost on it; the copper
busbar joint between two housings; the bolted collar at the lip of the shaft
- A row of five charge key frames labelled 0%, 25%, 50%, 75%, 100%, showing
  the coil housings lighting violet one at a time around the ring, so the
lit arc grows clockwise and the ring is fully lit only at 100%
- A layer breakdown row: shadow, bare metal, charge overlay, discharge
- A palette strip of eight colour swatches

== OUTPUT ==
One landscape concept sheet, 3:2, labelled panels on a dark charcoal background,
in the style of a game art bible page. Panel labels only; no other text.
```
