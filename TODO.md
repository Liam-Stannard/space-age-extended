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
- **The Core's cliff, boulder and shards are vanilla shapes in the Core's
  material** — `sae-cliff-core` is Fulgora's twenty seamed orientations
  rebuilt in slate by `tools/build-core-cliff.py`; the boulder and the three
  shard decoratives are vanilla's rocks rebuilt by `tools/build-core-rocks.py`.
  Shape is still borrowed; the material is ours. Drawing the Core's own rock
  shapes is a concept-sheet job (`concept/core-boulder/`), and a cliff of its
  own is the most demanding terrain asset in the game — weeks, not days.
- **The planet has no procession sets or ambient sounds** (`planet.lua`):
  vanilla planets carry `planet_procession_set`, `platform_procession_set`,
  `procession_graphic_catalogue` and `persistent_ambient_sounds`. Needs art
  and audio before it can be filled.
- **The vents wear crude oil's sheet and sounds**, and the ore iron ore's sheet.
- **`core-crust` is the working palette** — white crust, arc-blue lit cell
  joints, slate cliff, slate boulder and shards, craters only; two-scale
  elevation with a 28-step cliff interval. Renders in
  `concept/planet-core/terrain/core-crust/`. Joints are still wide (24% of
  ground) and the crust vent's stone-path placeholder is now the loudest
  thing on it.
- **Twenty technologies wear vanilla icons** — every Core technology except
  Core Discovery, Gravity Settling, Whisker Beds and Field Coils wears
  Aquilo's, and the three Fulgora ↔ Aquilo technologies wear the cryogenic
  science pack's. The data-stage placeholder report lists them by name.
- **Paint accents still to assign** (template Appendix B): Drop Crusher, Ballast
  Drill, Vacuum Furnace, Helium Concentrator, Crust Tap, Ring Mast, Bed Tender,
  Sealed Roboport. The Roboport's lamps and the Bed Tender's bin are derived
  against their own plates, so repainting either means re-deriving those too.

## Core terrain (`core-terrain` branch)

- **Five palettes without grey were rendered for the choice** — `tempered-steel`,
  `rust-iron`, `slag-flats`, `meteorite-face`, `dead-dynamo` — in
  `concept/planet-core/terrain/`, contact sheet `five-without-grey-…`. First
  cuts, one seed each; whichever is chosen gets the same two-seed tuning pass
  `scoured-nickel` had. Note `tempered-steel` placed no violet or purple on its
  seed (aux never reached their 0.85+ windows) and came out tan and brown.
- **Ten more palettes, no two sharing a body colour**, rendered one seed each:
  beige-regolith, cream-flats, violet-bloom, deep-purple, mauve-dust,
  straw-tan, green-heat (Alien Biomes' green heat tiles as ground), and three
  on Space Age's own tiles with no pack needed — red-desert (Nauvis),
  fulgoran-dust (Fulgora), basalt-soil (Vulcanus). Contact sheet
  `concept/planet-core/terrain/ten-more-…`; each has its tile shares in
  `v1-tiles.txt`. tempered-steel was retuned to reach its violet.
- **Choose the palette.** `scoured-nickel` was the grey recommendation: built from
  the renders of the other five, it drops frost entirely (the Core has no water
  to freeze) and gives the brief's read from what the planet does have — dark
  grey-to-black metal ground (two seeds: 71% black / 60% grey), plates of bare
  pale nickel where the crust is scoured (8–14%), thin dark seams along the
  fractures (~1.7%), craters, grey and black rock scatter, dark boulders.
  Renders: `concept/planet-core/terrain/scoured-nickel/`. `frosted-iron` is
  kept as the frost-on-metal alternative. `struck-nickel` is still the one
  `map-gen.lua` selects; switching is a one-word design decision.
- **The crust's lit cracks exist now** — `sae-crust-glow` (ember) and
  `sae-crust-glow-arc` (blue), placed along the palette's cell joints; both
  glow at night. They are Vulcanus's hot-crack sheets, the arc one hue-rotated
  by `tools/build-crust-glow-tile.py` — the whisker bed's approach, vanilla
  geometry with the material changed. Their own art is still owed if the
  Core should not share Vulcanus's crack texture. The `wb-cells-glow` and
  `wb-cells-arc` renders are in `concept/planet-core/terrain/white-and-blue/
  cells-glow/`; joint width (22% of ground) and glow cut still want tuning.
- **The heat seams on the other palettes do not glow.** Alien Biomes' heat tiles carry no light, so at
  night a fracture is a black line (`v3-seam-night.png`). Heat showing through
  the crust — the brief's third read — needs the Core's own lit tile, like the
  crust vent's. Until then the seams are dark fractures with pale rims.
## Repository layout

- **Untracked art in `graphics/entity/` awaiting a sign-off decision:**
  `ballast-drill/stroke.png`, `stroke-housing.png`, `stroke.json` (wired by the
  uncommitted `machines.lua` diff), `dross-classifier/base-animation.png` and
  `ignition-array/base-animation.png`. Only signed-off or placeholder art lives
  in `graphics/`; anything not signed off moves to `concept/<building>/`.
- **`changelog.txt` is empty** (the working tree deleted its contents). Restore
  from HEAD or write a 0.3.x entry for the reset.

