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
A single landscape concept-art and asset-breakdown sheet for one Factorio Space Age building, every panel drawn from the game's characteristic 45-degree top-down perspective, laid out as labelled panels on a dark charcoal background, in the style of a game art bible page.

Panels, left to right and top to bottom. A large hero view of the building. A tile-grid panel showing it from directly overhead on a 9x9 tile grid, sitting inside the grid with no part crossing the edge. Three close-up detail panels: the banded thermal lagging and steel strapping on the vessel's flank, an inspection hatch with frost around its rim, and the cryogenic pipework and relief stacks at the base. A row of five charge key frames labelled 0%, 25%, 50%, 75% and 100%, showing the white frost receding down the vessel from the top as it charges, uncovering inspection slots that glow violet from the windings inside, until at 100% the drum is clear of ice and lit from within. A layer breakdown row showing the same building separated into shadow, bare metal, charge overlay and discharge. A palette strip of eight colour swatches.

The building in every panel is the same machine: one enormous insulated cryogenic vessel - a fat horizontal drum, wider than it is tall, wrapped in banded thermal lagging and steel strapping, standing on a low anchored plinth, with thick cryogenic pipework and relief stacks around its base, the whole vessel caked in heavy white frost and rime, pale blue in the shadows.

It stands on an airless metallic world under crushing gravity, so it is squat, thick and anchored, and nothing about it is delicate. Weathered iron-nickel plate, grey-brown, rust in the seams. Violet is the only saturated colour on the sheet and it appears only in the charge frames. No flame, no exhaust, no steam, no smoke and no fire anywhere on the sheet.
```
