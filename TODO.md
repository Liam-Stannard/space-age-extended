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
- **Storm rate and damage.** No natural strike was ever observed headlessly, so
  600 damage per strike every ninety seconds (`prototypes/core/storms.lua`) is
  still an assertion.

## Art

- **The Crust Turbine and the crust vent tile still wear vanilla art**
  (`derive.placeholder_art` in `prototypes/core/crust-tap.lua`). The data stage
  lists every survivor at the end of each load.
- **Arc Mast plate:** `graphics/entity/arc-mast/base.png` has alpha 255 along
  its bottom row. Recut it with `process-building-art.py --bottom-margin`.
- **Arc Mast icon:** `graphics/icons/arc-mast.png` is a bare 64×64, the only
  icon in the mod that is not a 120×64 mipmap strip.
- **The space connection** `sae-shattered-planet-core` has no icon of its own,
  and the two asteroids wear their chunks' icons.
- **The Core has no cliff of its own.** `map-gen.lua` states Nauvis's cliff
  explicitly; the design's metallic ridges need a `cliff` prototype and art.
- **The planet has no procession sets or ambient sounds** (`planet.lua`):
  vanilla planets carry `planet_procession_set`, `platform_procession_set`,
  `procession_graphic_catalogue` and `persistent_ambient_sounds`. Needs art
  and audio before it can be filled.
- **The vents wear crude oil's sheet and sounds**, and the ore iron ore's sheet.
- **Twenty technologies wear vanilla icons** — every Core technology except
  Core Discovery, Gravity Settling, Whisker Beds and Field Coils wears
  Aquilo's, and the three Fulgora ↔ Aquilo technologies wear the cryogenic
  science pack's. The data-stage placeholder report lists them by name.
- **Paint accents still to assign** (template Appendix B): Drop Crusher, Ballast
  Drill, Vacuum Furnace, Helium Concentrator, Crust Tap, Ring Mast, Bed Tender,
  Sealed Roboport. The Roboport's lamps and the Bed Tender's bin are derived
  against their own plates, so repainting either means re-deriving those too.

## Core terrain (`core-terrain` branch)

- **Choose the palette.** `frosted-iron` was built from the renders of the
  other four and is the first to give the brief's read — grey metal ground
  (66–72% mineral dirt over two seeds), pale frost in patches (2–12%), heat only
  along thin seams (1.2%, both seeds), grey and black rock scatter and craters,
  no Vulcanus or Fulgora props. Renders: `concept/planet-core/terrain/frosted-iron/`.
  `struck-nickel` is still the one `map-gen.lua` selects; switching is a
  one-word design decision. Still unseen: a heat seam close up, and a full
  playthrough's worth of ground.
- **Frost varies a lot by seed** (2% against 12% over 256 chunks) because the
  temperature noise is region-scale. Acceptable or not is a play question.
- **The kamacite boulder is a drill-free ore route.** 25 ore by hand, about two
  a chunk, finite. 04 §2 says only the Ballast Drill works kamacite; if the
  boulder stays, that section owes a sentence (design change — needs agreement).
- **Decorative scatter is Vulcanus's and Fulgora's.** The pattern match lets in
  the volcanic rocks, craters, Fulgora rocks and the three sulfur rock
  decoratives (~400 per chunk in total). Alien Biomes' coloured rocks are
  enabled but never place. Decide whether sulfur belongs, and whether the
  density is right, by eye.

## Repository layout

- **Untracked art in `graphics/entity/` awaiting a sign-off decision:**
  `ballast-drill/stroke.png`, `stroke-housing.png`, `stroke.json` (wired by the
  uncommitted `machines.lua` diff), `dross-classifier/base-animation.png` and
  `ignition-array/base-animation.png`. Only signed-off or placeholder art lives
  in `graphics/`; anything not signed off moves to `concept/<building>/`.
- **`changelog.txt` is empty** (the working tree deleted its contents). Restore
  from HEAD or write a 0.3.x entry for the reset.

