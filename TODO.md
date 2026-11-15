# TODO

Every outstanding task, and nowhere else. Remove an entry once it is done.

## Play

- **Play the landing.** This decides the rest, and the landing is small enough
  for one sitting: from the first boulder to Radiant power (see
  09-core-tech-tree.md).
  The open questions: whether hydrogen or the pool binds first, and whether the
  landing reads as a start or as a stop. Then tune ore richness, vent decline
  and the precipitation ratios against it — all calculated, never played.

## The rework

- **Decide what the kamacite vent is for.** Molten kamacite has no consumer,
  and the Vent Pump exists only to trigger Radiant power while the line that
  used it is gone. Gravity settling (in git history, old 04 §8) is the
  candidate on file.
- **Fines need their advanced use.** Metal carbonyl
  (in git history, old 06 T3) is the chosen later sink for
  kamacite fines, beside fines smelting. It lands with the next tier of the
  Core's tree.
- **Decide how the game ends.** Vanilla victory is off in `control.lua` and
  nothing replaces it, so a playthrough never ends.
- **Re-plan stages 2–4 of the radiant cycle against what exists.** They name
  geodynamic technologies and machines that were cut. The spent-cell and steam
  decisions under Power wait on this.
- **Decide what happens to the cut buildings' art.** `graphics/` still holds
  signed-off art for nine buildings that no longer exist — Bed Tender, Ignition
  Array, Dross Classifier, Sealed Roboport, Whisker Plant, Coil Separator,
  Whisker Comber, Helium Concentrator, Ring Mast — plus their item icons and the
  whisker-bed terrain. Keep them for buildings that may return, or move them to
  `concept/<building>/`; git keeps them either way.
- **Rename "melt" to the kamacite vent in the docs.** "Melt" in `design/`,
  once the docs are rewritten for the rework.
- **Rename siderane to hydrogen.** 04 now says hydrogen (Liam, 2026-11-14).
  Rename the fluid, its vent and its turbine in the mod and in every
  document. It replaces the old "crust gas to siderane" rename entry. With
  it, look at the vacuum names (Vacuum sintering, the Vacuum Furnace), which
  pressure 200 no longer fits.
- **Decide the Vacuum Furnace's job.** In the code it runs only `smelting`,
  so on the Core it is a slower, hungrier electric furnace, and three
  tooltips claim work it does not have (T09 gameplay review,
  evidence/gameplay-audit/T09/vacuum-furnace.md concern 1: (a) lock fines smelting to it, (b) base
  productivity, (c) delete it, (d) rewrite the spec). Then fix the
  tooltips and the unused flux box to match.
- **Holmium oxide's productivity.** With productivity modules the oxide
  route gives +56% to +110% holmium, not +20%. Decide whether to drop
  productivity on `sae-holmium-oxide` (T09 gameplay review,
  evidence/gameplay-audit/T09/vulcanus-fulgora.md concern 4).
- **The magnetite round after railgun damage 2.** Give it a lasting
  advantage, or call it a bridge in the doc (T09 gameplay review,
  evidence/gameplay-audit/T09/vulcanus-fulgora.md concern 3).

## Building art in Blender

Stages: see the factorio-building-round skill.

- **The Vulcanus ↔ Fulgora tree wears stand-in art**: the induction
  foundry, ozone collector and magnetic collector are tinted vanilla
  buildings; the magnetic chunk is the metallic chunk with a blue rim;
  obsidian, the tree's items and its eleven technologies wear tinted
  vanilla icons. Concepts in progress (`vf-tree-concepts`).

## Blender pipeline

- **The contract does not compare a model's declared ports with the
  prototype's pipe connections**, so a picture drawn at a connection it
  was not rendered for goes unseen (the Reaction Plant, 2026-10-20).
- **The sound labeller can invent a label when two sounds start on the
  same onset** (`tools/client/audio/analyse.py`). It fails the run
  rather than passing it; no building cues two sounds on one frame yet.

## Power

- **Decide what happens to spent cells on space platforms.** The Radiant
  Generator can be built on space platforms and gives back spent cells (see
  its spec), so every platform accumulates cells nothing reprocesses. Ship them down, or give platforms a
  void (`auto_recycle = false` in `prototypes/core/items.lua` keeps it open).
- **Decide whether the reactor may make steam.** A `reactor`'s output path is
  heat → exchanger → steam → turbine, which brings steam back at the top of a
  ladder that removed it everywhere else. Accept it in the reactor room, or
  find the reactor another output.

## Trees

- **Five trees are still to design, one per planet**: Nauvis, Vulcanus, Fulgora, Gleba and Aquilo (see `design/00-vision.md`). Each starts from `templates/tree-spec-template.md`. The capstone stubs in `prototypes/core/endgame.lua` still carry the old pair products and craft from one iron plate. Reworking the two pair specs is the Design entry "Trees extend one planet each, not pairs".

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
- **Two power buildings need specs before art**, both for stages the rework
  is re-planning: `concept/isotope-centrifuge/` and `concept/radiant-reactor/`
  do not exist yet; both come from `templates/building-spec-template.md`.
- **Paint accent still to assign** (standards.md, Finish): Gas Pump.
- **The radiant pool's shore steps on the tile grid.** The edge between
  the open surface and the glowing shore follows tile-aligned steps
  (seen on 2.1.22; Liam signed the pool off and asked for this to be
  logged).
- **The Reaction Plant has no sound of its own.** Its press accent is
  a vanilla stand-in (`landfill-inventory-move`) and its bed is the
  chemical plant's; it needs a design and rounds, as the crusher had.
- **The Vent Pump has no sound.** It is silent: the pumpjack's sounds it
  inherited are stripped and nothing replaces them. It needs a sound cued to
  its charges, with a design and rounds, as the crusher had.
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
- **Raise the Core's pressure to 200.** 04 now says 200 (Liam, 2026-11-14).
  The planet changes, and every pressure limit has to move with it. The
  Core-only limits move from 1-9 to 1-299: the Reaction Plant and the radiant
  precipitation recipe. The 'pressure 9 or less' limits (the Core and
  platforms) move to 299 or less: the Radiant Generator and the Vacuum
  Furnace. The Hydrogen Turbine is 9 or less today and must become Core-only,
  1-299. What will then work there: see 04-the-core.md, Surface properties.
- **Decide whether the Core has carbon.** 04 no longer says what the Core
  lacks (Liam, 2026-11-14: "remove this for now"). Carbon is up for review;
  copper, water and organics are not yet decided either.
- **The Core needs its own fallback ground tiles.** Without Alien
  Biomes it borrows Aquilo's snow (map-gen-fallback); our own
  tiles are for later (Liam, 2026-10-19).
- **Reference tables cut from 01-principles.md.** The platform placement list, the immovable fluids and the planet properties table came out in the principles refactor (2026-11-13). Decide where they live, and re-verify them against 2.1.24.
- **Trees extend one planet each, not pairs.** The principles changed on 2026-11-13. The two built cross-planet trees (Vulcanus ↔ Fulgora, Fulgora ↔ Aquilo) need reworking to match. A task file comes first.

## Repository

- **`changelog.txt` is empty.** Write a 0.3.x entry covering the reset, the cut
  back to the landing, stage 1 of the radiant cycle and the Blender pipeline.
- **Hook: deletes that still pass (agent-setup-followup T05 review,
  2026-11-13).** `unlink`, `rm` fed by `xargs` (piped, `-0`, `-a <file>`),
  `sh -c 'rm ...'` and `busybox rm` are not checked against the scratch rule; a
  task file comes first.
