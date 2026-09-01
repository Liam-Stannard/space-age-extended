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

## Not started yet

- **Phase 3 — Capstone** (design doc §8; Tech 5 `sae-resonant-electromagnetics`).
  Catalyst Rod, Resonant Circuit (+ Depleted Catalyst Rod + Contaminated
  Sulfuric Acid byproducts), Purify Contaminated Sulfuric Acid, Magmatic
  Core (Vulcanus side — Lava + Tungsten + Catalyst Rod), Depleted Catalyst
  Rod reprocessing (feeds back into Holmium Extraction), Thermionic
  Assembly. Testable state per the plan: simulate shipping via console
  item-insertion between a Vulcanus and Fulgora surface rather than real
  rockets.
- **Phase 4 — Thermionic Generator** (design doc §9; Tech 6
  `sae-thermionic-power`). The hard one — needs real `control.lua` runtime
  logic since no stock Factorio entity type gives a self-heating,
  coolant-driven efficiency curve with electricity-only output for free
  (confirmed by reading the actual `fusion-generator`/`reactor`/`generator`
  prototypes in the installed engine). The plan calls for a time-boxed
  technical spike first — default approach: a visible
  `electric-energy-interface` (script sets `.power_production` per tick)
  paired with a hidden 2-slot `container` fuel/coolant hopper, linked via
  `unit_number` in `storage`. Fallback: `burner-generator` with Magmatic
  Core as a custom fuel category. See the plan file for full detail.

## To resume

Say "start phase 3" (or 4). Everything needed — design doc, framework doc,
this file, the plan file, and the verified local Factorio 2.1.17 install
at `~/.steam/debian-installation/steamapps/common/Factorio` — is already
in place.
