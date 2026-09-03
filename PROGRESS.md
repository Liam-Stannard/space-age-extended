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
  `sae-thermionic-power`), on branch `thermionic-reactor-rework`, not yet
  merged. Went through three architectures in one day:
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

## Not started yet

- **Design doc sync.** `design/vulcanus-fulgora.md` §9.2/§9.4 still
  describe the abstract-temperature model, the old heat-interface entity,
  and the 20s-to-floor timing; §16 lists several questions this branch
  answered (calcite burden, foil value, holmium yield, acid loop runs at
  3x surplus). Update once the branch is playtested and merged.
- **Playtest + merge** of `thermionic-reactor-rework`, then delete the
  branch (see git flow above).
- **Trees 2+** — see the parked brainstorm in Claude's memory
  (`project_space_age_extended_future_trees`) and framework.md §4.2's
  open slots.

## To resume

Say "start phase 3" (or 4). Everything needed — design doc, framework doc,
this file, the plan file, and the verified local Factorio 2.1.17 install
at `~/.steam/debian-installation/steamapps/common/Factorio` — is already
in place.
