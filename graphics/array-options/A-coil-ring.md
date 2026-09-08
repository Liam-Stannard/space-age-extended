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
A single landscape concept-art and asset-breakdown sheet for one Factorio Space Age building, every panel drawn from the game's characteristic 45-degree top-down perspective, laid out as labelled panels on a dark charcoal background, in the style of a game art bible page.

Panels, left to right and top to bottom. A large hero view of the building. A tile-grid panel showing it from directly overhead on a 9x9 tile grid, sitting inside the grid with no part crossing the edge. Three close-up detail panels: one coil housing in its armoured cradle with frost on it, the copper busbar joint between two housings, and the bolted collar at the lip of the shaft. A row of five charge key frames labelled 0%, 25%, 50%, 75% and 100%, showing the coil housings lighting violet one at a time around the ring, so the lit arc grows clockwise and the ring is fully lit only at 100%. A layer breakdown row showing the same building separated into shadow, bare metal, charge overlay and discharge. A palette strip of eight colour swatches.

The building in every panel is the same machine: a squat, heavy, octagonal machine ring with a wide open shaft straight down through its middle, and a continuous chain of superconducting coil housings laid end to end around the ring - thick cylindrical windings in armoured cradles, copper busbars linking one to the next, frost and rime collecting on the housings.

It stands on an airless metallic world under crushing gravity, so it is squat, thick and anchored, and nothing about it is delicate. Weathered iron-nickel plate, grey-brown, rust in the seams. Violet is the only saturated colour on the sheet and it appears only in the charge frames. No flame, no exhaust, no steam, no smoke and no fire anywhere on the sheet.
```
