# TODO

Every outstanding task, and nowhere else. Remove an entry once it is done.

## Play

- **Play the landing.** This decides the rest, and the landing is small enough
  for one sitting: boulder → Crust Tap → survey → Vent Pump → Radiant power.
  The open questions: whether crust gas or the pool binds first, and whether the
  landing reads as a start or as a stop. Then tune ore richness, vent decline
  and the precipitation ratios against it — all calculated, never played.

## The rework

- **Decide what the kamacite vent is for.** Molten kamacite has no consumer,
  and the Vent Pump exists only to trigger Radiant power while the line that
  used it is gone. Gravity settling (`design/04-the-core.md` §8) is the
  candidate on file.
- **Decide how the game ends.** Vanilla victory is off in `control.lua` and
  nothing replaces it, so a playthrough never ends.
- **Re-plan stages 2–4 of the radiant cycle against what exists.** They name
  geodynamic technologies and machines that were cut
  (`design/production-line-plan.md` says so). The spent-cell and steam
  decisions under Power wait on this.
- **Decide what happens to the cut buildings' art.** `graphics/` still holds
  signed-off art for nine buildings that no longer exist — Bed Tender, Ignition
  Array, Dross Classifier, Sealed Roboport, Whisker Plant, Coil Separator,
  Whisker Comber, Helium Concentrator, Ring Mast — plus their item icons and the
  whisker-bed terrain. Keep them for buildings that may return, or move them to
  `concept/<building>/`; git keeps them either way.
- **Rename the melt vent to the kamacite vent.** The four player-facing
  strings, `sae-melt-vent` → `sae-kamacite-vent` with a migration, and "melt"
  in `design/` once the docs are rewritten for the rework.

## Building art in Blender

Each building is modelled through `tools/blender/` from its spec, signed off by
Liam, then wired in. Task specs are in `.claude/tasks/` (local).

- **Vacuum Furnace** — redesigned 2026-10-02 to take one rotatable fluid input;
  finished model in progress (`vacuum-furnace-model`), then wiring: rotatable
  fluid box, rendered pipe pictures, `status_colors` per §3.1's fault-lamp table.
- **Drop Crusher** — model (`drop-crusher-model`), then wiring.
- **Crust Tap** — model (`crust-tap-model`), then wiring once the engine test
  says whether `fluid_animation` can carry the working-only frost and seam.
- **Radiant Generator** — model (`radiant-generator-model`), then wiring with
  an `idle_animation`, so a fuelless generator stops glowing.
- **Ballast Drill** — model (`ballast-drill-model`), then wiring: one plate,
  a vanilla-style chute and ore particles per direction. Replaces the stroke
  art committed without sign-off (`ballast-drill/stroke*`).
- **Reaction Plant, again** — re-modelled to template rules 6 and 7: no
  gutter base, rendered pipe pictures, vanilla covers.
- **The Drop Crusher, Ballast Drill and Vacuum Furnace lamps have no
  `status_colors`**, so they likely draw dark, as the reaction plant's did.
  Each wiring task sets them.

## Blender pipeline

- **Renders are not repeatable to the byte.** A fresh reaction plant render
  in `blender-pipeline-review` differed from `graphics/` and was not looked
  into; until it is, every "matches what shipped" check needs a tolerance.
- **The contract does not check that a model turning its ports has a fitting
  sheet for every face they turn to** (`tools/blender/contract.py`).
- **The slide check averages before it measures**, so one frame up to about
  1.33 px off its curve still passes the 1 px limit (`tools/blender/pack.py`).

## Power

- **Decide what happens to spent cells on space platforms.** The Radiant
  Generator places at pressure ≤ 9 and emits spent cells, so every platform
  accumulates cells nothing reprocesses. Ship them down, or give platforms a
  void (`auto_recycle = false` in `prototypes/core/items.lua` keeps it open).
- **Decide whether the reactor may make steam.** A `reactor`'s output path is
  heat → exchanger → steam → turbine, which brings steam back at the top of a
  ladder that removed it everywhere else. Accept it in the reactor room, or
  find the reactor another output.

## Trees

- **Four capstones are stubs.** Magnetar alloy, cultured alloy, bio-polymer
  and cryoprotectant each craft from one iron plate
  (`prototypes/core/endgame.lua`). Each needs a real tree — an anchor, a chain
  on each world, a capstone building and 3–10 technologies — with
  [Fulgora ↔ Aquilo](design/trees/fulgora-aquilo.md) as the worked example.

## Art

- **The Crust Turbine and the crust vent tile still wear vanilla art**
  (`derive.placeholder_art` in `prototypes/core/crust-tap.lua`). The data stage
  lists every survivor at the end of each load.
- **The Crust Tap has no scorched-ground layer**, which its spec (§3.3) asks
  for as its own layer, the way vanilla does `mining_drill_scorch_mark`.
- **The space connection** `sae-shattered-planet-core` has no icon of its own,
  and the radiant asteroid wears its chunk's icon.
- **The planet has no procession sets or ambient sounds** (`planet.lua`):
  vanilla planets carry `planet_procession_set`, `platform_procession_set`,
  `procession_graphic_catalogue` and `persistent_ambient_sounds`. Needs art
  and audio before it can be filled.
- **The vents wear crude oil's sheet and sounds**, and the ore iron ore's
  sheet. A vent art plan was proposed in session (2026-09-11) and awaits
  agreement; once agreed, the specs go in `concept/kamacite-vent/` and
  `concept/gas-vent/`.
- **Six technologies wear vanilla icons:** Crust tapping, Core survey and
  Radiant power wear Aquilo's, and the three Fulgora ↔ Aquilo technologies
  wear the cryogenic science pack's. The data-stage placeholder report lists
  them.
- **Two power buildings need specs before art**, both for stages the rework
  is re-planning: `concept/isotope-centrifuge/` and `concept/radiant-reactor/`
  do not exist yet; both come from `templates/building-spec-template.md`.
- **Paint accents still to assign** (template Appendix B): Drop Crusher,
  Ballast Drill, Vacuum Furnace, Crust Tap.

## Design

- **The Core has no threat.** The arc storms went with the power rework, and
  they were the planet's only hazard. It needs a replacement: something that
  threatens the factory or the player, that is not a fourth spoil-timer
  mechanic, and that must not quietly become a power source again.
  `design/ideas.md` I1 (radiation and decontamination) is the one researched
  candidate on file.
- **`04-the-core.md` §1 still describes the arc storm as the Core's hazard.**
  "Life and hazard" needs wording that says the planet has no threat yet.
  Wording to be agreed before `design/` is touched.
- **The design still says the Core has no surface fluid.** The radiant pool,
  its shore and its solution are in the mod, and 04 §2, 03 §3 and the "no
  coastline" line need wording that says what the pool is and why it is not a
  coastline. Wording to be agreed before `design/` is touched.
- **Five building specs describe a building that is not being built.** The
  Radiant Generator's (no burnt-result slot; art "blocked"), the Crust Tap's
  (gas only), the Ballast Drill's (a ballast block, not the Ring Press), the
  Drop Crusher's (the Animatorio stroke) and the Vacuum Furnace's (sintering).
  Wording to be agreed.

## Repository

- **`changelog.txt` is empty.** Write a 0.3.x entry covering the reset, the cut
  back to the landing, stage 1 of the radiant cycle and the Blender pipeline.
