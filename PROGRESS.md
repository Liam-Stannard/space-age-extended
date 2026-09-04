# Implementation Progress

Status snapshot for resuming work on the Vulcanus ↔ Fulgora tree. The full
implementation plan (phasing, engine facts, technical approach) lives at
`~/.claude/plans/generic-floating-waterfall.md` on this machine — this file
is the shorter "where things stand" companion to that, kept in the repo so
it survives independently of local Claude state.

## Done (on `master`, pushed to GitHub)

- **Phase 0 — Scaffolding.** Mod skeleton (`data.lua`, `prototypes/`,
  `locale/en/strings.cfg`, `migrations/`), `.luacheckrc`, GitHub Actions
  lint workflow, `tools/check-data-stage.sh` (local smoke test that runs
  the mod's data stage through the real Factorio 2.1 engine via
  `--dump-data`).
- **Phase 1 — Refining chain** (design doc §1–6). Scrap Remelting →
  Ferrous/Non-Ferrous Separation → Ferrous Refinement (→ vanilla
  `molten-iron`) / Non-Ferrous Separation (→ vanilla `molten-copper` +
  Holmium-rich Residue) → Holmium Extraction (→ vanilla `holmium-ore`),
  plus Copper Foil. Two technologies: `sae-metallurgical-recovery`,
  `sae-advanced-material-recovery`. User-playtested, confirmed working.
- **Phase 2 — Electronics alt-recipes** (design doc §7). Electromagnetic
  Electronic/Advanced/Processing Unit alt-recipes on the EM Plant, each
  outputting the literal vanilla item. Two technologies:
  `sae-electromagnetic-metallurgy`, `sae-integrated-electronics`.
  Data-stage + 60-tick benchmark verified; not yet user-playtested.

- **Phase 3 — Capstone** (design doc §8; Tech 5 `sae-resonant-electromagnetics`),
  on branch `phase-3-capstone`, not yet merged to `master`. Catalyst Rod,
  Resonant Circuit (+ Depleted Catalyst Rod + Contaminated Sulfuric Acid
  byproducts), Purify Contaminated Sulfuric Acid, Magmatic Core (Vulcanus
  side — Lava + Tungsten + Catalyst Rod), Depleted Catalyst Rod
  reprocessing (feeds back into Holmium Extraction), Thermionic Assembly.
  5 new items, 1 new fluid, 6 new recipes. One technology,
  `sae-resonant-electromagnetics`, requiring both
  `sae-electromagnetic-metallurgy` and `sae-integrated-electronics`.
  Data-stage verified; not yet user-playtested.

One real bug found and fixed along the way: the mod's internal `name` in
`info.json` didn't match the `__space-age-extended__` prefix already used
in every graphics path, so it failed to load. Renamed the mod (and its
title) to **`space-age-extended`** — this also better reflects
`design/framework.md`'s intent of one mod eventually holding multiple
cross-planet trees, not just this one. The mods-folder symlink at
`~/.factorio/mods/space-age-extended` and `tools/check-data-stage.sh`
both already reflect the current name.

## Verification workflow (established, keep using it)

```
./tools/check-data-stage.sh   # data-stage load against the real engine
```

Plus, per phase, an in-engine `--create` + `--benchmark --benchmark-ticks 60`
smoke test (see git log for the exact throwaway-scratch-dir invocation used
each time), and a manual in-game playtest using console commands to
fast-research, e.g.:

```
/c game.player.force.technologies['sae-metallurgical-recovery'].researched = true
/c game.player.cheat_mode = true
```

Git flow used so far: one branch per phase, commit, verify, merge
fast-forward into `master`, push, delete the branch.

- **Phase 4 — Thermionic Generator** (design doc §9; Tech 6
  `sae-thermionic-power`), merged to `master` (`cdcd0be`, docs `5ba70b5`).
  Went through three architectures in one day:
  1. `electric-energy-interface` + hidden filtered-container hopper
     (original spike). Playtest: fuel read as a chest slot, not fuel.
  2. Hidden `furnace` with an unreachable recipe category as a fake fuel
     slot. Playtest: engine never ignites fuel it doesn't drain itself, so
     status/tooltip/gauge all misreported ("stuck red icon").
  3. **Current:** the visible generator *is* a real `reactor`. Engine
     genuinely burns Magmatic Core (custom `sae-thermionic-fuel` category,
     800MJ = 200s/core, matching the uranium fuel cell); its own
     `heat_buffer` is the temperature (10°/s at full draw) and its
     `connections` are the real heat-pipe interface — the old bespoke
     heat-interface entity is gone. A hidden `electric-energy-interface`
     injects the curve-computed power (`render_no_power_icon = false`);
     a hidden 2-slot filtered container holds Ice, reached via an
     "Insert Ice" button on a small `player.gui.relative` panel anchored
     to the reactor's own native window. `scale_energy_usage = false`
     keeps fuel rate independent of heat; an idle guard in
     `step_generator` pauses the reactor (`disabled_by_script`) when the
     grid draws <5% of full output, restoring §9.1's "no idle waste".
     Footprint 4x4.

  Two engine facts learned the hard way, both now commented at the site:
  `LuaEntity.active` is read-only (use `disabled_by_script`), and
  `LuaEntity.power_production` is **joules per tick**, not watts — the
  original spike wrote watts (60x too much), masked from the grid only by
  the prototype's `output_flow_limit`.

  Verified headlessly (see workflow below): real ignition/`no_fuel`
  status, 200s burn (to the MJ), 10.0°/s heating, Ice cooling to the
  degree, steady idle (fuel byte-identical across samples) and resume on
  a 300kW load, teardown. **Not yet user-playtested** in this form — the
  relative-GUI panel and the rescaled 16-point heat-pipe connection
  layout for the 4x4 footprint need in-client eyes.

- **Balance pass** (same branch), against vanilla numbers from the
  installed engine: Copper Foil 10→1 per craft (was a ~10x copper
  discount; now value-neutral per §7.1), Scrap Remelting 50→100 molten
  scrap and calcite 10→2 (was ~5x below recycling on iron), non-ferrous
  split 95/5→90/10 (holmium trickle was *below* recycling's 1%),
  `specific_heat` 80kJ→400kJ (16s→80s to overheat; holding needs
  0.25 Ice/s not 1.25), coolant tank 1→2 slots.

## Headless RCON verification (how this was actually tested)

`tools/check-data-stage.sh` only covers the data stage. Runtime logic was
verified with a headless server driven over RCON — no client needed, but
two gotchas: `~/.factorio/.lock` means the real client must be closed,
and with no client connected the server free-runs far faster than
real-time, so **always measure against `game.tick` deltas, never
wall-clock `sleep`**. Rig: symlink the repo into a scratch `mods/` dir
with a `mod-list.json`, `factorio --create fresh.zip --mod-directory
mods`, then `--start-server fresh.zip --rcon-port N --rcon-password X
--server-settings settings.json` (with `allow_commands: "true"`) and a
20-line Source-RCON Python client sending `/c ... rcon.print(...)`.
Setup per run: `force.create_space_platform{starter_pack=...}`,
`apply_starter_pack()`, `create_entity` on `platform-1` with
`raise_built=true`. Note `create_entity` fires `script_raised_built`, so
`on_generator_built` runs; the first RCON call after startup tends to
return blank — send a warm-up.

## Phase 4 rebuilt: the Quench Turbine (branch `quench-turbine`)

The Thermionic Generator is **gone**, replaced by the Quench Turbine. The
reason is worth keeping: a `reactor`'s heat buffer feeds every consumer on its
network, so vanilla heat exchangers plus steam turbines would have converted
the generator's waste heat into roughly as much electricity again, making its
own output irrelevant. The only native fix was to hold the whole network below
the heat exchanger's 500-degree `min_working_temperature` — which works, but
leaves the temperature scale fighting the efficiency curve and still needs a
script to remove heat at all.

The replacement reaches the same design goal — output per shipped Magmatic
Core is a decision the player tunes — with **no heat network, no hidden
entities and no runtime script**. `control.lua` is now empty and `scripts/` is
deleted, along with the reactor, its hidden power interface, its hidden
coolant container, the custom GUI and the `sae-thermionic-fuel` category.

Magmatic Core stopped being a fuel and became an ingredient. A quench recipe
on an ordinary chemical plant turns one core plus Ice into Quench Vapour at a
temperature the recipe fixes; the Quench Turbine is a plain `generator` and
clips vapour above 315°C. A recipe making a little very hot vapour throws most
of the core away; one making a lot at exactly the cap wastes nothing. That
difference is the tech ladder, enforced by the engine rather than by script.

- **Lean Quench** (with `sae-thermionic-power`): 90MJ/core, 9MW per plant.
- **Cryogenic Quench** (new `sae-cryogenic-quenching`, needs vanilla
  `cryogenic-plant` **and** Fluoroketone): 600MJ/core, 60MW per plant.
- **Radiative Fluoroketone Cooling**: vacuum-only chemical-plant recipe
  closing the Fluoroketone loop in space, since a cryogenic plant cannot be
  built on a platform. Fluoroketone is an initial fill, not an import.
- Tier 3 deliberately deferred to the endgame design (a corridor-gated
  asteroid resource).

Migration: a JSON rename handles stockpiled items and set recipes; a two-line
Lua migration re-runs technology effects. Generators already *placed* cannot
be recovered — the engine removes them before migrations run.

### Verified over headless RCON (rig above)

| Check | Result |
|---|---|
| Turbine at the 315°C cap | 18.000 MW |
| Vapour at 900°C | 18.000 MW — clipped, not 53 MW |
| Vapour at 200°C | 11.100 MW — linear, so the clip is real |
| No electrical demand | 0 MW, no vapour consumed (no idle burn) |
| ~3 MW demand | 3.000 MW, 1.97 vapour/s of the 12/s maximum |
| Lean / Cryogenic Quench | 60 / 400 vapour per core |
| Radiative cooling | hot Fluoroketone → cold, on a platform |
| Technology gating | tier-2 recipes disabled until researched |
| Placement | builds on a platform, refused on Nauvis |

**Engine fact learned, worth not re-discovering:** recipe `surface_conditions`
are a *player-facing selection filter*, not a runtime crafting block. A recipe
forced onto a wrong-surface machine by script or console crafts happily. This
was confirmed against vanilla's own gravity-0 `space-science-pack`, which
behaves the same way on Nauvis. The vacuum-only radiative recipe is correct as
written — do not "fix" it.

**Art:** the turbine's sheets and icon are this mod's own, built from
vanilla's steam turbine by `tools/recolour-turbine.py`. Not a `tint` on
vanilla's files -- a tint multiplies, and vanilla's turbine is already brass
and rust (saturated pixels at hue 15-45 degrees, ~16% of the opaque area), so
tinting it warm changed almost nothing and muddied the greys. The script
rotates just those accents to a cryogenic teal at their original lightness and
leaves neutral metal alone, so all of vanilla's shading survives. Teal because
the building is the *cold* half of the mechanic; orange would have been
indistinguishable from the source sprite. Shadows are copied unrecoloured.

The Quench Vapour icon is built by `tools/derive-vapour-icon.py`, which
gradient-maps an existing drop (hue rotation can't colour a source that has no
saturation). Two false starts worth not repeating: vanilla's steam icon is a
lumpy cloud that reads as popcorn once warmed, and at 46% frame coverage it
was chunkier than the set's 31-35%; and a warm amber vapour measured at hue
0-20, colliding with molten non-ferrous, while pale gold collided with
contaminated acid. Teal is the set's one free hue, and it pairs the fluid with
its machine. The fluid's base_color/flow_color were changed to match.

**Still owed:** a client playtest -- nothing here has been played.

## Balance pass (branch `balance-pass`)

A review against the installed game's own numbers found three problems, all
fixed here. The measurements are in `design/vulcanus-fulgora.md` §9.4.

1. **Magmatic Core shipped 10,000 per rocket.** Its weight was never set, and
   the engine's derived default came out at 100 because the recipe is mostly
   Lava and fluids weigh nothing. A rocket of cores was worth 6TJ at the
   cryogenic quench -- three times a rocket of fusion power cells and
   seventy-five times a rocket of uranium fuel cells. Shipping was effectively
   free, which defeats framework.md §2.1 entirely. Now an explicit 1000, so a
   rocket is 90GJ lean / 600GJ cryogenic. Catalyst Rod, its spent form and
   Copper Foil are 2000 for the same reason -- left derived, the rod loop cost
   twenty times moving the cores it exists to produce.

2. **The radiative recipe was buffing vanilla fusion.** Vanilla deliberately
   has no way to re-cool Fluoroketone in space: its cooling recipe is
   `cryogenics`-only and a cryogenic plant needs pressure >= 10, which is why
   vanilla fusion platforms ship coolant in barrels. The mod's vacuum-only
   recipe had made it the only in-space source of `fluoroketone-cold`, i.e. it
   silently removed vanilla fusion's coolant logistics for anyone running the
   mod. The loop now runs on two mod fluids, Quench Coolant and Spent Quench
   Coolant, made on Aquilo from Fluoroketone. Vanilla's economy is untouched
   and Aquilo is still the gate. Two fluids rather than one at two
   temperatures because barrels do not preserve temperature -- a single
   coolant could be barrelled hot and emptied cold, laundering the radiator
   step away.

3. **The tier ladder inverted on floor space.** At 10 radiators per quench
   plant the cryogenic tier was 80 tiles for 60MW (0.71 MW/tile), *less*
   space-efficient than the lean tier it upgrades from (0.86) -- backwards, on
   a platform, where floor space is the scarcest thing there is. Radiative
   cooling now processes 40 per craft instead of 10: 2.5 radiators per quench
   plant, 50 tiles, 1.17 MW/tile, ahead of lean and still behind fusion's 1.36.

Also worth keeping: **the turbine's real advantage over nuclear is ice, not
density.** Nuclear on a platform must melt ice into water for its exchangers,
about 0.52 ice/s per MW and some twenty chemical plants of ice-melting per
reactor; the cryogenic quench needs 0.067. That, plus no idle burn, is the
honest case for the building.

Verified over RCON: weights (1000 per rocket for cores, 500 for rods), the
cryogenic quench producing 400 vapour + 100 spent coolant per core, radiative
cooling returning 4 cold/s for a 2.5:1 ratio, and vanilla still having no
in-space Fluoroketone cooling recipe.

## Not started yet

- **Playtest** the Quench Turbine. Nothing in it or the balance pass has been
  played; every number is engine-measured, none is play-tested.
- **`thermionic-playtest-feedback` is kept, deliberately not merged.** It
  refines the Thermionic Generator this work deletes; kept so the old design
  can be revisited if the Quench Turbine does not survive playtesting.
- **Trees 2+** — see the parked brainstorm in Claude's memory
  (`project_space_age_extended_future_trees`) and framework.md §4.2's
  open slots.

## To resume

Say "playtest the quench turbine". Everything needed — design doc, framework doc,
this file, the plan file, and the verified local Factorio 2.1.17 install
at `~/.steam/debian-installation/steamapps/common/Factorio` — is already
in place.
