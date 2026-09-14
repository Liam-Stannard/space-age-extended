# TODO

Every outstanding task, and nowhere else. Remove an entry once it is done.

## Play

- **Play the Core end to end.** This decides the rest. The open questions:
  whether the vent → settle → cast loop has enough going on, whether whisker
  beds read as a farm or as waiting, and whether a strike every ninety seconds
  is weather or an annoyance.
- **Then tune against that playtest.** The geodynamic pack's cost, the Ignition
  Array's 100 parts, ore richness and vent decline are all first guesses —
  calculated, never played.

## Trees

- **Four capstones are stubs.** Magnetar alloy, cultured alloy, bio-polymer and
  cryoprotectant each craft from one iron plate (`prototypes/core/endgame.lua`).
  Each needs a real tree — an anchor, a chain on each world, a capstone
  building and 3–10 technologies — with
  [Fulgora ↔ Aquilo](design/trees/fulgora-aquilo.md) as the worked example.

## Checks only a client can make

- **Do chunks from a seeded asteroid reach a collector?** Chunks are not
  entities the search API can see, and the vanilla control failed identically,
  so the headless rig cannot answer it.

## Art

- **The Crust Turbine and the crust vent tile still wear vanilla art**
  (`derive.placeholder_art` in `prototypes/core/crust-tap.lua`). The data stage
  lists every survivor at the end of each load.
- **The space connection** `sae-shattered-planet-core` has no icon of its own,
  and the two asteroids wear their chunks' icons.
- **The planet has no procession sets or ambient sounds** (`planet.lua`):
  vanilla planets carry `planet_procession_set`, `platform_procession_set`,
  `procession_graphic_catalogue` and `persistent_ambient_sounds`. Needs art
  and audio before it can be filled.
- **The vents wear crude oil's sheet and sounds**, and the ore iron ore's sheet.
  A vent art plan was proposed in session (2026-09-11) and awaits agreement;
  once agreed, the specs go in `concept/melt-vent/` and `concept/gas-vent/`
  before any art is commissioned.
- **Twenty technologies wear vanilla icons** — every Core technology except
  Core Discovery, Gravity Settling, Whisker Beds and Field Coils wears
  Aquilo's, and the three Fulgora ↔ Aquilo technologies wear the cryogenic
  science pack's. The data-stage placeholder report lists them by name.
- **Paint accents still to assign** (template Appendix B): Drop Crusher, Ballast
  Drill, Vacuum Furnace, Helium Concentrator, Crust Tap, Ring Mast, Bed Tender,
  Sealed Roboport. The Roboport's lamps and the Bed Tender's bin are derived
  against their own plates, so repainting either means re-deriving those too.

## Design

- **The Core has no threat.** The arc storms went with the power rework — the
  radiant cycle does not need them, and they were the planet's only hazard, so
  the Core is now a world where nothing can go wrong. It needs a replacement:
  something that threatens the factory or the player, that is not a fourth
  spoil-timer mechanic, and that must not quietly become a power source again —
  free power is what forced the mast's efficiency down twice.
  `design/ideas.md` I1 (radiation and decontamination) is the one researched
  candidate on file and was written as a replacement for these storms, so it is
  where this starts rather than a blank page.

- **The design still says the Core has no surface fluid.** The radiant pool,
  its shore and its brine are in the mod (`prototypes/core/tiles.lua`,
  `map-gen.lua`), and 04 §2, 03 §3 and the "no coastline" line need wording
  that says what the pool is and why it is not a coastline. Wording to be
  agreed before `design/` is touched.

## Repository layout

- **Untracked art in `graphics/entity/` awaiting a sign-off decision:**
  `ballast-drill/stroke.png`, `stroke-housing.png`, `stroke.json` (wired by the
  uncommitted `machines.lua` diff), `dross-classifier/base-animation.png` and
  `ignition-array/base-animation.png`. Only signed-off or placeholder art lives
  in `graphics/`; anything not signed off moves to `concept/<building>/`.
- **`changelog.txt` is empty** (the working tree deleted its contents). Restore
  from HEAD or write a 0.3.x entry for the reset.

