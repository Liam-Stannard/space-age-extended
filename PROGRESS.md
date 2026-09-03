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
     `heat_buffer` is the temperature (100°/s at full draw since the
     playtest-feedback round below; 10°/s as merged) and its
     `connections` are the real heat-pipe interface — the old bespoke
     heat-interface entity is gone. A hidden `electric-energy-interface`
     injects the curve-computed power (`render_no_power_icon = false`);
     a hidden 2-slot filtered container holds Ice, reached via an
     "Insert Ice" button on a small `player.gui.relative` panel anchored
     to the reactor's own native window. `scale_energy_usage = false`
     keeps fuel rate independent of heat; an idle guard in
     `step_generator` paused the reactor (`disabled_by_script`) when the
     grid drew <5% of full output (removed in the playtest-feedback round
     below — it's a thermal reaction, it shouldn't idle). Footprint 4x4.

  Two engine facts learned the hard way, both now commented at the site:
  `LuaEntity.active` is read-only (use `disabled_by_script`), and
  `LuaEntity.power_production` is **joules per tick**, not watts — the
  original spike wrote watts (60x too much), masked from the grid only by
  the prototype's `output_flow_limit`.

  Verified headlessly (see workflow below): real ignition/`no_fuel`
  status, 200s burn (to the MJ), 10.0°/s heating (at the then-400kJ
  `specific_heat`), Ice cooling to the degree, the since-removed idle
  guard's steady idle (fuel byte-identical across samples) and resume on
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

- **Playtest feedback round 1** (branch `thermionic-playtest-feedback`,
  not yet merged). First user playtest of the reactor form. Changes:
  1. **Heats up much faster** — `specific_heat` 400kJ→40kJ, i.e. 100°/s
     at the 4MW draw: 6s cold→600 (top of optimal band), 8s→800
     (overheat). Ice caps at 2 × 40° = 80°/s, so under full load Ice only
     slows the climb (net +20°/s, ~40s to overheat, 100-Ice tank lasts
     50s at the cap) and can never hold the band by itself; the heat-pipe
     channel (10MW, 2.5× input; each vanilla heat pipe adds 1MJ of
     thermal mass, 25× the generator's buffer) is the only avenue that
     can. Feedback verbatim: "it should heat up a lot faster — so the
     thermal block is useful"; at 400kJ Ice trivially held it and pipes
     were pointless.
  2. **Idle guard removed.** Feedback: "it shouldn't idle when there is
     no power draw, this is a thermal reaction." `step_generator` no
     longer measures demand or toggles `disabled_by_script`/
     `custom_status`; it just reads the burner for fuel and writes the
     curve's output. The power interface's `buffer_capacity` (only there
     for the demand measurement) and the `status-idle` locale string are
     gone; design doc §9.1/§9.3/§16 no longer claim "no idle waste".
  3. **Animations play.** The entity only had vanilla's static
     body/pipes sprites; it now has the reactor-type animated fields —
     `heat_lower_layer_picture`, `heat_buffer.heat_picture`,
     `minimum_glow_temperature = 350`, `working_light_picture`, the
     burner's `light_flicker`, and all four connection-patch sheets —
     with vanilla's base-internal `apply_heat_pipe_glow` output inlined
     (tinted layer + `draw_as_light` copy). Vanilla's 12-column patch
     sheets can't serve 16 connections (`variation_count` must be ≥
     `#connections`), so `tools/generate-thermionic-graphics.py` builds
     16-column sheets from them into
     `graphics/entity/thermionic-generator/` (committed). Heat
     connections moved from the collision-box edge (±2) to the edge
     tiles' centres (±1.5), matching every vanilla precedent and the
     once-verified 3x3 layout.
  4. **Magma glow, not uranium green.** Vanilla's working-light sprite
     has green baked into its pixels, so the generator script also
     writes `lights-mask.png` (neutral luminance, L = max(R,G,B), A =
     255) and the reactor tints it via `use_fuel_glow_color` from
     Magmatic Core's new `fuel_glow_color = {1, 0.45, 0.1}` (same value
     on `default_fuel_glow_color` and the reactor's new `light`).

  Engine-verified (data stage, then a headless RCON run by the round's
  tester — the lock was free): heating measured at exactly 100.0°/s
  (615° at 6.15s, 801.7° at 8.02s); fuel burned continuously at 4.000MW
  with nothing drawing power (idle guard confirmed gone); Ice consumed at
  exactly 2 per interval for a net +20°/s climb under full load; and all
  16 tile-centre heat-pipe connections conducted while pipes on the four
  diagonal corner tiles (which touch no connection) stayed at ambient.
  The round's reviewer never ran (session rate limit); the diff was
  reviewed by hand afterwards instead. Still needs in-client eyes:
  whether a heat-pipe block actually *holds* the optimal band at 100°/s
  (only the rate and the connections were measured, not a full network's
  equilibrium), and how the glow/working-light animation actually looks
  (`check-data-stage.sh` parses prototypes, it doesn't render — including
  whether the heat glow reads dim in the 400–600 band, since
  `max_temperature` is 2000 vs vanilla's 1000).

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

- **Playtest + merge** of `thermionic-playtest-feedback` (the round
  above), then delete the branch (see git flow above). The design doc is
  already in sync with it.
- **Trees 2+** — see the parked brainstorm in Claude's memory
  (`project_space_age_extended_future_trees`) and framework.md §4.2's
  open slots.

## To resume

Say "start phase 3" (or 4). Everything needed — design doc, framework doc,
this file, the plan file, and the verified local Factorio 2.1.17 install
at `~/.steam/debian-installation/steamapps/common/Factorio` — is already
in place.
