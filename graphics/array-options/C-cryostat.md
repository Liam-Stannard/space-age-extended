# Option C — the Cryostat

**One line.** One enormous insulated vessel, white with frost, holding a
superconducting magnet at temperature — and the frost burns off as it charges.

## The idea

Every other option is a frame with parts on it. This one is a single object: a
dewar. The superconducting coil is *inside*, invisible, and what the player sees
is the lagging, the cryo lines, the relief valves and the rime. It is the only
option whose form comes from the coolant chain rather than from the coil.

Visually it is the odd one out on purpose. The Core is grey-brown rust from
horizon to horizon; a white building at the end of it would be the most striking
thing on the planet.

## Why it suits the Core

The chain already ends in `sae-coolant-loop`, `sae-cold-cryogen` and
`sae-cryoprotectant` — the mod spends a whole production line getting something
cold, and nothing in the built world currently shows it. A superconductor needs
to be cold, the Core has no atmosphere to insulate against, and a vacuum world
is exactly where you would put a bare cryostat.

Nothing burns here, and this is the only option that could not possibly be
mistaken for something that does.

## Massing and palette

A single fat drum, wider than tall, banded with lagging and strapping, standing
on a low anchored plinth. Cryo lines and relief stacks around the base. Pale
grey-white lagging, frost and rime, pale blue shadow in the ice, with the steel
of the plinth and the pipework as the only warm-grey. Heavy frost skirt where it
meets the ground.

## The charge display

**The rime burns off.** At 0% the vessel is buried in frost, opaque white, and
the coil is invisible. As charge climbs the frost recedes in a band from the
base upward, revealing violet light from the windings *through* the vessel's
inspection slots — so the display is a material changing state rather than lamps
switching on.

At 100% the drum is clear of ice and lit violet from within, and the frost skirt
on the ground has retreated to a ring.

## Plates

`base` (frosted, unlit), `charge-overlay` (clear vessel with lit windings,
revealed by a rising mask), `shadow`. Three — but the overlay is a *different
render of the same object*, not a lit copy of the base, which is more art than
the others need.

## Cost and risk

The most expensive: two full renders that have to register pixel-for-pixel, and
generators are poor at producing the same object twice. Also the biggest
departure — a white building may read as belonging to a different mod, and there
is no bore, so the rocket has nowhere obvious to rise from.

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
Ignition Array - option C, Cryostat.
One enormous insulated cryogenic vessel holding a superconducting
magnet, standing on a low anchored plinth. 9x9 tiles.

== FORM ==
- One fat drum lying horizontally, wider than it is tall, filling the footprint
- Wrapped in banded thermal lagging with steel strapping over it
- Standing on a low, thick, anchored plinth
- Thick cryogenic pipework and relief stacks around its base
- Inspection hatches along its flank
- The whole vessel caked in heavy white frost and rime, pale blue in the shadows
- A skirt of frost spreading onto the ground where it stands

== COLOUR ==
- Lagging: #C6C8C6 to #E4E7EA, frosted pale grey-white, the body of the building
- Ice and rime: #DCE6EE with #9FB3C4 in the shadows, pale blue
- Plinth and pipework: #4A463F to #6E685C, warm dark iron-nickel
- Copper: #8A5A32, confined to fittings
- Charge: violet-white #C9B6FF ramping to #FFFFFF, in the charge frames only
- This is the one option that is pale on purpose. The vessel is white; the steel
  it stands on is not.

== RULES ==
- Airless metallic world, gravity 50: squat, thick, anchored. Nothing cantilevers,
  nothing is delicate, nothing is slender.
- Nothing burns here. No flame, no exhaust, no steam, no smoke, no fire, anywhere
  on the sheet, in any panel.
- Superconducting, therefore cold. Frost and rime are correct; glowing hot metal
  is wrong.
- Nothing glows at rest. Violet appears only in the charge frames.
- The building sits inside a 9x9 tile square with no part crossing the edge.
- Must read as a cryogenic dewar, not a fuel tank, boiler or silo: no burner,
  no firebox, no chimney, no flue, nothing that could combust.

== PANELS ==
- A large hero view of the building
- A tile-grid panel from directly overhead on a 9x9 tile grid, the building
  inside the grid with no part crossing the edge
- Three close-up detail panels: the banded lagging and steel strapping on the flank; an inspection hatch
with frost around its rim; the cryogenic pipework and relief stacks at the base
- A row of five charge key frames labelled 0%, 25%, 50%, 75%, 100%, showing
  the white frost receding down the vessel from the top, uncovering
inspection slots that glow violet from the windings inside, until at 100% the
drum is clear of ice and lit from within
- A layer breakdown row: shadow, bare metal, charge overlay, discharge
- A palette strip of eight colour swatches

== OUTPUT ==
One landscape concept sheet, 3:2, labelled panels on a dark charcoal background,
in the style of a game art bible page. Panel labels only; no other text.
```
