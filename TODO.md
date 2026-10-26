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
- **Fines need their advanced use.** Metal carbonyl
  (`design/06-core-production-tree.md` T3) is the chosen later sink for
  kamacite fines, beside fines smelting. It lands with the next tier of the
  Core's tree.
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
- **Rename "melt" to the kamacite vent in the docs.** "Melt" in `design/`,
  once the docs are rewritten for the rework.
- **Rename crust gas to siderane in the docs.** The player-facing names
  changed on 2026-10-09 (siderane, the Siderane wellhead, turbine, vent and
  extraction); `design/` and the other specs still say "crust gas", "crust
  tap" and "crust turbine" about 50 times. Rewrite them with the rework.
  Internal names (`sae-crust-*`) stay. With it, `design/08-core-power.md`
  lines 18 and 24–27: radiant solution is drawn by a vanilla offshore pump
  at the pool, and siderane by the Gas Pump, not one tap drawing both.

## Building art in Blender

Each building is modelled through `tools/blender/` from its spec, signed off by
Liam, then wired in. Task specs are in `.claude/tasks/` (local).

- **Radiant Generator** — concept signed off (the Carousel Foundry,
  round 7); spec wording, then the model, then wiring with an
  `idle_animation`, so a fuelless generator stops glowing.
- **Reaction Plant** — re-modelled in four directions so its pipes
  follow the flow and every connection has a fitting (Liam,
  2026-10-20), then re-wired (`reaction-plant-wiring`).

## Blender pipeline

- **The contract does not compare a model's declared ports with the
  prototype's pipe connections**, so a picture drawn at a connection it
  was not rendered for goes unseen (the Reaction Plant, 2026-10-20).
- **The sound labeller can invent a label when two sounds start on the
  same onset** (`tools/client/audio/analyse.py`). It fails the run
  rather than passing it; no building cues two sounds on one frame yet.

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

- **The planet has no procession sets or ambient sounds** (`planet.lua`):
  vanilla planets carry `planet_procession_set`, `platform_procession_set`,
  `procession_graphic_catalogue` and `persistent_ambient_sounds`. Needs art
  and audio before it can be filled.
- **The vents and the kamacite ore wear vanilla art**: the vents crude
  oil's sheet, with no motion or working sound; the ore iron ore's sheet.
  One shared vent form with a feature of its own per vent, coloured to
  show each resource, drawn in Blender; a spec per resource
  (`concept/kamacite-vent/`, `gas-vent/`, `siderane-vent/`,
  `kamacite-ore/`) and one shared note; then an options round (Liam,
  2026-10-20).
- **Two technologies wear vanilla icons:** Vent tapping and Radiant
  power still wear Aquilo's; each waits for its building's model (the
  Vent Pump, the Radiant Generator). The data-stage placeholder report
  lists them.
- **Two power buildings need specs before art**, both for stages the rework
  is re-planning: `concept/isotope-centrifuge/` and `concept/radiant-reactor/`
  do not exist yet; both come from `templates/building-spec-template.md`.
- **The Reaction Plant's sight slots still glow green-white**; the
  whole radiant family is the solution's blue (`#1F63FF` → `#73ADFF`,
  Liam 2026-10-10). They go blue with its four-way model
  (`reaction-plant-wiring`).
- **Paint accents still to assign** (template Appendix B): Drop Crusher,
  Ballast Drill, Vacuum Furnace, Crust Tap.
- **The radiant pool's shore steps on the tile grid.** The edge between
  the open surface and the glowing shore follows tile-aligned steps
  (seen on 2.1.22; Liam signed the pool off and asked for this to be
  logged).
- **The Reaction Plant has no sound of its own.** Its press accent is
  a vanilla stand-in (`landfill-inventory-move`) and its bed is the
  chemical plant's; it needs a design and rounds, as the crusher had.
- **The Ballast Drill's sounds want the crusher's treatment**: softer
  attacks, less high end, heavier, grouped like vanilla's (Liam,
  2026-10-20: "Crusher first").

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
- **The Core needs its own fallback ground tiles.** Without Alien
  Biomes it borrows Aquilo's snow and ice (map-gen-fallback); our own
  tiles are for later (Liam, 2026-10-19).
- **Five building specs describe a building that is not being built.** The
  Radiant Generator's (no burnt-result slot; art "blocked"), the Crust Tap's
  (gas only), the Ballast Drill's (a ballast block, not the Ring Press), the
  Drop Crusher's (the Animatorio stroke) and the Vacuum Furnace's (sintering).
  Wording to be agreed.

## Repository

- **`changelog.txt` is empty.** Write a 0.3.x entry covering the reset, the cut
  back to the landing, stage 1 of the radiant cycle and the Blender pipeline.
