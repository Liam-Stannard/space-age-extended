# TODO

Every outstanding task, and nowhere else. Remove an entry once it is done.

## Play

- **Play the Core end to end.** This decides the rest. The open questions:
  whether the vent → settle → cast loop has enough going on, and whether
  whisker beds read as a farm or as waiting.
- **Then tune against that playtest.** The geodynamic pack's cost, the Ignition
  Array's 100 parts, ore richness and vent decline are all first guesses —
  calculated, never played.

## Trees

- **Four capstones are stubs.** Magnetar alloy, cultured alloy, bio-polymer and
  cryoprotectant each craft from one iron plate (`prototypes/core/endgame.lua`).
  Each needs a real tree — an anchor, a chain on each world, a capstone
  building and 3–10 technologies — with
  [Fulgora ↔ Aquilo](design/trees/fulgora-aquilo.md) as the worked example.

## Power

- **Build the radiant cycle.** `design/08-core-power.md` is the design and
  `design/production-line-plan.md` is the plan: four stages on four branches.
  Nothing of it exists yet — the storms are gone and the planet runs on 1.8 MW
  turbines and a generator researched four technologies too late. Stage 1
  alone puts the power back; build it, play it, and let it set the numbers for
  the other three.
- **Decide what happens to spent cells on space platforms.** The radiant
  generator places at pressure ≤ 9, so once it emits a `burnt_result` every
  platform accumulates cells it cannot reprocess until stage 3. Ship them down,
  or give platforms a void. Blocks stage 1.
- **Decide whether the reactor may make steam.** A `reactor`'s output path is
  heat → exchanger → steam → turbine, which brings steam back at the top of a
  ladder that removed it everywhere else. Accept it in the reactor room, or find
  the reactor another output. Blocks stage 4.
- **Spike: `neighbour_bonus` on a fuel category that is not uranium's.** A
  `reactor` with `fuel_categories = { "sae-radiant" }` in a 2×2, and a look at
  the bonus in its GUI. Assumed since the reactor was first proposed, never
  checked, and stage 4's whole reward rests on it. Data stage.

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
- **Nineteen technologies wear vanilla icons** — every Core technology except
  Core Discovery, Gravity Settling, Whisker Beds and Field Coils wears
  Aquilo's, and the three Fulgora ↔ Aquilo technologies wear the cryogenic
  science pack's. The data-stage placeholder report lists them by name.
- **Three power buildings need specs before art** — `concept/reaction-plant/`,
  `concept/isotope-centrifuge/` and `concept/radiant-reactor/`, from
  `templates/building-spec-template.md`. Each ships in placeholder art until
  then, as every Core machine did. Both crafters derive from the chemical plant
  (`production-line-plan.md` says why), so their placeholders already draw the
  ports their fluid boxes connect to.
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

- **`04-the-core.md` §1 still describes the arc storm as the Core's hazard**,
  in a binding document, and the storms are gone. "Life and hazard" needs
  wording that says the planet has no threat yet and points at the entry above.
  Wording to be agreed before `design/` is touched.

- **The design still says the Core has no surface fluid.** The radiant pool,
  its shore and its solution are in the mod (`prototypes/core/tiles.lua`,
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

