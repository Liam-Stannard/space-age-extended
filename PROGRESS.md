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

- **Reactive Edge Plating — Phase 0 feasibility spike** (branch
  `reactive-edge-plating`, not merged, no design-doc section yet). A
  perimeter plate that spends one loaded charge to destroy an incoming
  asteroid at contact range: an `ammo-turret` entity plus an `ammo` item,
  a dedicated `ammo-category`, native `tile_buildability_rules` for the
  void-adjacency restriction, placeholder recipes and a temporary
  technology. **Zero control-stage Lua** — `control.lua` and `scripts/` are
  untouched, and that is the spike's headline result.

  Measured on the headless rig below; every number is from a real run.

  - **Placement is fully native.** A 44-cell matrix (each rim face x each
    rotation, plus corners, interior tiles, and one-in-from-rim) comes out
    an exact diagonal: outward-facing rim only, both outward directions on
    a corner, every interior cell rejected in every rotation. Identical
    under `can_place_entity` and under reviving an `entity-ghost`, so
    blueprints obey the same rule as manual placement. No `on_built`
    rejection handler needed.
  - **Inserter loading is tick-for-tick identical to a vanilla gun turret**
    on the same chest+inserter rig: both at 8 after 600 ticks, both at 10
    after 1200.
  - **Ammo-category isolation is total, in both directions and through the
    inserter path.** firearm-magazine and railgun-ammo into a plate insert
    0; a Reactive Charge into a vanilla gun turret inserts 0; an inserter
    beside a gun turret with a chest of 20 charges moved none in 900 ticks.
  - **Loaded vs empty, same tile, same medium asteroid:** loaded → plate
    200/200, witness one tile behind 350/350, 0 tiles lost; empty → plate
    destroyed, 2 foundation tiles lost.
  - **A plated rim saves the platform.** Same route, thrust and tick budget,
    3600 ticks: UNPLATED lost 400 of 400 foundation tiles and all 12
    interior witnesses (gone by dt~2700). PLATED (64 plates, one per
    buildable perimeter tile, 20 charges each) finished 400/400 tiles, 0
    tile damage, 12/12 witnesses at full health, 64/64 plates alive, having
    spent 50 of 1280 charges (3.9%).
  - **Charge consumption is strictly per-impact, never per-second.** Three
    loaded plates with nothing to shoot held 10/10 charges at
    `damage_dealt = 0` across 11,202 ticks, against a liveness witness
    (burner inserter) that moved 147 items in the same window. A plate with
    a NEUTRAL-force asteroid parked half a tile off its hull likewise sat at
    10/10 and `damage_dealt = 0` and was destroyed by it without firing.
  - **Per-class ladder** (loaded 10-charge plate, steel-chest witness one
    tile behind, asteroid on the `enemy` force, `range_mode` and
    `turn_range` as shipped): medium → plate 200/200, witness 350/350, 0
    tiles lost, 4 charges spent. big → 200/200, 350/350, 0 tiles lost, 5
    charges. huge → all 10 charges every run, and **the outcome is not
    deterministic** — the dying cascade's child spread is RNG. Five runs:
    tiles lost 0 / 2 / 2 / 2 / 1, plate health 200 / 150 / 150 / 200 / 200,
    witness 350/350 in all five. A `huge` dies to 3 charges
    ((5000-3000)*0.9 = 1800 x 3 > 5000 hp); the other 7 go on its cascade.
  - **A 0.5 (hemisphere) firing arc costs nothing.** A/B on the same build,
    360 degrees vs 0.5: 3600-tick plated flight 400/400 tiles, 12/12
    witnesses, 64/64 plates in both, 49 charges spent at 360 degrees vs 50
    at 0.5. `huge` x4 at 360 degrees lost 0/1/3/0 tiles against 0/2/2/2/1
    at 0.5 — overlapping spreads, no regression. `medium` identical (4
    charges, 0 tiles); `big` 0 tiles lost either way, but 9 charges at 360
    degrees against 5 at 0.5, because the full circle also spends charges on
    cascade children that have already drifted past the plate.

  Engine facts this spike established, each now commented at its site:

  - **`attack_parameters.range_mode` defaults to `center-to-center`.**
    Vanilla asteroids carry `collision_box = {{-r,-r},{r,r}}` from
    `collision_radiuses = {0.4, 0.5, 1, 2, 4.5}`
    (`space-age/prototypes/entity/asteroid.lua:165-172`, applied at `:492`),
    so under the default a declared `range = 4` is a real standoff of 3.5
    tiles against a small, 3.0 against a medium, 2.0 against a big and
    **-0.5 against a huge** — the rock's hull is already past the turret
    before it may fire, and `prepare_range` (which defaults to `range`)
    means it is still folded at that moment. Chunks are the exception:
    asteroid.lua:492 gives a chunk no collision_box at all, so for a chunk
    the two modes are the same. Anything meant to engage asteroids at a
    stated tile distance needs
    `range_mode = "center-to-bounding-box"` (vanilla precedent: tesla turret
    `space-age/prototypes/entity/turrets.lua:724`, and
    `base/prototypes/entity/flying-robots.lua:773`, `:856`).
  - **`turn_range` defaults to 1 (a full circle)**, and the engine clamps
    anything in (0.5, 1) down to 0.5 — targeting in arcs larger than a half
    circle is not implemented. A turret whose placement already fixes its
    facing therefore has exactly two useful settings: the default full
    circle, or a hemisphere.
  - **`LuaSurface.create_entity` runs no build check and bypasses
    `tile_buildability_rules` entirely.** Measured returning a valid entity
    on interior tiles and on bare void, for the plate *and* for vanilla
    `asteroid-collector` and `thruster`. Any placement test written on
    create_entity is a false pass in every cell. The valid oracles are
    `can_place_entity` and reviving an `entity-ghost`.
  - **`automated_ammo_count` is a FLOOR, not a cap.** An inserter keeps
    swinging until the turret holds at least that many, and a whole hand
    lands in the final swing, so the settle point scales with
    `force.inserter_stack_size_bonus`: bonus 0 settles at 10, bonus 3 at 12,
    bonus 6 at 14 — identically for the plate and for a vanilla gun turret.
    The prototype value is the guaranteed minimum stock, not the stock.
  - **The `empty-space` tile declares `ground_tile = true`** in its own
    collision_mask (`space-age/prototypes/tile/tiles.lua:211-222`), so a
    `tile_buildability_rules` entry with `required_tiles = {layers =
    {ground_tile = true}}` alone happily matches void. It has to be paired
    with `colliding_tiles = {layers = {empty_space = true}}` to mean "real
    foundation" — which is exactly what vanilla's asteroid-collector
    (`space-age/prototypes/entity/entities.lua:691-694`) and thruster
    (`:908-911`) do.
  - **`heating_energy` defaults to 0W**, so an entity that does not declare
    it never freezes — but that only ever matters on a surface whose planet
    sets `entities_require_heating`, and **Aquilo is the only one in the
    game that does** (`space-age/prototypes/planet/planet.lua:680`, the sole
    occurrence in the entire data tree). This is **closed, not an open
    balance edge**: the plate is vacuum-only (`surface_conditions` pressure
    min 0 max 0), Aquilo's surface pressure is 300 (`planet.lua:643`) and a
    platform's is 0 (`space-age/prototypes/surface.lua:12`), so the plate can
    never stand on the one surface where `heating_energy` is read. Unset/0W
    is correct **by construction**. Vanilla's railgun and rocket turrets do
    declare `"50kW"` (`space-age/prototypes/entity/turrets.lua:318`, `:432`)
    precisely because they carry **no `surface_conditions` at all** (verified:
    no `surface_conditions` key anywhere in `base/` or `space-age/`
    `turrets.lua`) and so *are* placeable on Aquilo. The difference is
    placement scope, not an asymmetry to correct.

  Findings that are **design input, not defects** — recorded here for the
  design phase; no fix attempted:

  - **Corners are structurally unfeedable by a belt+inserter rim ring.** A
    full concentric build — 76 plates on ring 0, inserters on ring 1, belt
    on ring 2, power poles on ring 3 — got 63 of 63 inserter-served plates
    to >=10 charges and held them there. But **12 of the 76 rim plates (the
    3 tiles at each of the four corners) have no orthogonal neighbour on the
    belt ring**, so no inserter can ever sit between belt and plate. Corners
    are exactly where a rim is most exposed. Any answer is a design one:
    accept unfed corners, chamfer the platform, use a second logistics
    layer, or change the plate's feeding shape.
  - **A closed belt loop deadlocks — see the stated rule below**, which is
    the one finding here that has to reach players rather than just the
    design phase.
  - **`weight` is permanently off the table for this capability.** Platform
    mass is hub weight + sum of tile weights and nothing else (see the
    engine fact below), so a plate can never be balanced against platform
    speed; its whole cost has to live in the charge supply chain.
  - **No circuit connector**, so a plate's remaining charges are not
    readable on the circuit network and a platform cannot hold at a depot
    until its rim is re-armed. Vanilla gun-turret carries
    `circuit_connector_definitions["gun-turret"]`; this entity carries
    nothing. Prototype-only to close.
  - **The framework.md §4.5.1 interaction is emergent only.** The plate
    draws on the platform's consumable throughput, and what it "feeds" is
    negative and implicit: asteroids a plate destroys are asteroids the
    collectors never harvest. Real, but it falls out of turret targeting on
    its own — nothing in the prototype expresses it and there is no knob to
    tune it with.

  ### Rule: a charge-resupply belt ring must never be closed

  **Rule.** Any rim pattern this mod suggests — blueprint, screenshot,
  tutorial, or wiki page — **must leave the belt ring open by at least one
  tile**. A ring that meets itself is a broken build, not a tidier one.

  **Cause.** A belt advances an item only into free space ahead of it. Close
  the ring and every tile's "ahead" is another occupied tile, so once the
  lane saturates there is nowhere for the front item to go and the whole
  loop stops moving at once. Inserters on the arc that never received
  charges then have nothing to pick up, and — because nothing is moving —
  never will. It is a stable state, not a slow one: it does not clear itself
  given more time, more belt, or more input.

  **Evidence (measured).** The first rim build used a closed loop: one
  saturated lane across all 60 belt tiles, frozen for 20,000 ticks, with 44
  of the rim's plates permanently dry while the belt in front of them was
  visibly full. Deleting a **single** belt tile to open the ring fixed it
  completely — the same build then filled every inserter-served plate to
  >=10 charges and held them there.

  **Symptom, in the words a player will use.** *Full belts, empty plates.*
  The belt looks perfectly healthy — solidly packed with Reactive Charges
  all the way round — while a whole arc of the rim sits at zero and does not
  fire. There is no alert, no red icon and no error; the only visible cue is
  that the belt is not moving. A player who hits this will report that **the
  plating is broken**, because from the outside that is exactly what it
  looks like. Anything shipped with a closed ring will generate that bug
  report.

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

Further rig-level gotchas, all found the hard way while spiking Reactive Edge
Plating. Each of these silently produces a plausible but wrong measurement
rather than an error, so check for them before believing a negative result:

- **`/c` must share a line with the first statement.** A scenario file
  sent as `/c\n<lua>` makes the server parse `c` plus the next word as a
  command name and reply `Unknown command "c local"`. Prefix with `"/c "`
  and `lstrip()` the file.
- **Asteroids must be created on the `enemy` force.** On `neutral` — the
  obvious guess — turrets simply ignore them: a vanilla gun turret with
  10 magazines loaded sat at `damage_dealt = 0` and let the asteroid hit
  it. Turrets only engage forces their own force is `is_enemy()` with,
  and `player` vs `neutral` is false. **Always put a vanilla control
  turret in the rig.**
- **An inserter's `direction` is the side it picks up FROM**, not the
  side it drops on. `direction = north` gives `pickup_position` one tile
  north and `drop_position` one tile south.
- **`automated_ammo_count` is the count an inserter fills a turret up
  to**, not just a logistics-request number — and it is a *floor*, not a
  cap. See the engine-facts list under Reactive Edge Plating above.
- **Not every API method takes a table.** `LuaSpacePlatform::repair_tile`
  and `LuaSurface::set_tiles` take positional args while their neighbours
  don't; `runtime-api.json`'s per-method `format.takes_table` is the
  authority. That file (plus `prototype-api.json`) ships with the install
  at `<factorio>/doc-html/` and is far faster to consult than guessing.
- **`LuaEntityPrototype` has no `max_health`** — read `max_health` off
  the `LuaEntity`.
- **Resolve a platform by scanning `game.surfaces` for a valid
  `.platform`.** `force.get_space_platforms(planet)` stops finding it the
  moment it departs, and the surface is not always `platform-1` (a
  destroyed platform's replacement is `platform-2`, …).
- **Killing the hub deletes the whole platform**, and every later
  measurement then errors on a nil platform. Pin
  `platform.hub.destructible = false` in any rig that lets asteroids
  through, and keep test lanes off `x = 0`.
- **Platform mass is hub weight + Σ tile weight, and nothing else.**
  Entities and their cargo contribute zero; `weight` as a mass
  contribution exists only on `TilePrototype` and
  `SpacePlatformHubPrototype`.
- Asteroids drift at ~0.0197 tiles/tick **even when the platform's own
  speed is 0**, so single-asteroid tests need no thrusters at all. Only
  the S5-style exposure runs need the platform genuinely under way.
- **A platform will not depart until the destination's
  `planet-discovery-*` technology is researched.** Setting a schedule
  without it leaves `platform.state = 5` (`no_path`), `speed` pinned at
  0.00 and every thruster reporting `thrust_not_required` — a flight
  scenario then runs its whole tick budget with zero asteroids spawned and
  reports a flawless result. Research `planet-discovery-vulcanus` (or the
  lot) in setup, and assert `speed > 0` before believing a flight run.
- **Clear asteroids surface-wide between scenarios, not just inside the
  setup's box.** Every setup here wipes a +/-45 tile box; after a flight
  run there are live asteroids well outside it that drift back in
  mid-measurement. Measured cost of skipping it: a `huge` ladder run
  immediately after a flight reported the plate DESTROYED and 58 foundation
  tiles lost, against 0-2 tiles for the same build from a clean surface.
  Destroy `find_entities_filtered{type = "asteroid"}` over the whole
  surface and re-park the platform first.

## Not started yet

- **Playtest** the Quench Turbine, then merge `quench-turbine` into `master`.
- **`thermionic-playtest-feedback` is kept, deliberately not merged.** It
  refines the Thermionic Generator this work deletes; kept so the old design
  can be revisited if the Quench Turbine does not survive playtesting.
- **Strip `icon_mipmaps`, repo-wide, in its own janitorial commit.** The key
  does **not** exist in the Factorio 2.1 prototype API and is silently
  ignored — verified against the shipped `doc-html/prototype-api.json`. It is
  pre-existing at 25 sites across the whole repo, so new code has been
  following it as house style; removing it is a single mechanical pass, not
  something to fold into a feature branch. Recorded here so nobody re-adds it
  or re-discovers it as a review finding.
- **Trees 2+** — see the parked brainstorm in Claude's memory
  (`project_space_age_extended_future_trees`) and framework.md §4.2's
  open slots.

## Outstanding work, as of 2026-09-04

Consolidated across tree 1, this branch, and tree 2's plan
(`~/.claude/plans/vulcanus-aquilo-structure.md`). Ordered by what blocks what.

### Tree 1 — Quench Turbine (on `master`)

- [ ] **Client playtest.** Nothing in the Quench Turbine rework has been played.
      Tooltip legibility of the temperature clipping, and whether the lean tier
      reads as a bridge rather than a solution.
- [ ] **Decide `thermionic-playtest-feedback`.** Kept deliberately, refines a
      design this work deleted. Keep or delete once the turbine is played.
- [ ] **Strip `icon_mipmaps` repo-wide** — dead key, 25 sites, own janitorial
      commit.

### Reactive Edge Plating (branch `reactive-edge-plating`, 11 commits, unmerged)

- [ ] **Client playtest.** Two things headless testing cannot answer: whether
      the four placeholder facings actually read as different in a client, and
      whether rotate-to-face-void placement is comfortable (vanilla asks the
      same of the asteroid collector).
- [ ] **Measure the promethium ladder.** The two-charges-for-`big` and
      six-for-`huge` figures are computed from prototype data, not measured —
      no charge has ever been fired at a promethium asteroid.
- [ ] **Apply the first-pass numbers** from the plan's §13. The prototypes still
      carry spike placeholders (charge = 1 steel + 1 explosives; plate = 10
      steel + 5 tungsten) and no composite appears anywhere yet.
- [ ] **Decide the plate's own survivability** — `max_health = 200` and its
      resistances, once promethium's doubled `damage_per_hp` is measured.
- [ ] **Corner feeding.** Adopt chamfered rims as stated design intent, and
      publish a reference rim pattern. It must not be a closed belt loop (a
      saturated loop deadlocked for 20,000 ticks with 44 plates dry).
- [ ] **Circuit connector** is missing and **`heating_energy`** is unset — both
      recorded in-line as deliberate gaps, neither decided.
- [ ] **Real art**: the entity sprite with folded/preparing/attacking states,
      plus the three new icons in `graphics/icon-prompts.md`.
- [ ] **Merge decision.** Rebased onto current master and purely additive, but
      not merged and not pushed.

### Tree 2 — the rest of the tree (nothing implemented)

- [ ] **Resolve the Thermal Bus contradiction first — it blocks the design doc.**
      `design/endgame.md` §2a band 4 still names "Quench Turbine + **Thermal
      Bus** (tree 1, and V↔A's second stage)", and `design/core.md` §2's
      stage-one reversal ("run the Thermal Bus backwards") both point at a
      mechanic the quench rework deleted. Decide whether V↔A owes a second-stage
      thermal capability at all; the plan's §10 recommends replacing the beat
      with a Geothermal Quench on the Core rather than deleting it.
- [ ] **Write `design/vulcanus-aquilo.md`** — plan Phase 1. Nothing in `design/`
      has been touched yet. Must state the band-5 boundary (consumption stays
      strictly per-impact) as a rule, not a tuning note.
- [ ] **Build the chain** — Molten Basalt, Refractory Panel, Basalt Fibre,
      Fluoride Flux, Spent Flux, Tungsten Halide Pellet, Clad Panel,
      Thermal-Shock Composite, and the five technologies. Plan phases 2–4.
- [ ] **Replace the placeholder recipe and technology** on the plating branch
      with the real chain and its gating (the `explosives` prerequisite goes
      away with them).
- [ ] **Update `design/framework.md` §5.1/§5.2** — Structure is still listed as
      an open slot.

### Housekeeping

- [ ] `.claude/` (agent worktrees) is untracked in the main checkout and should
      be gitignored.

## To resume

Say "playtest the quench turbine". Everything needed — design doc, framework doc,
this file, the plan file, and the verified local Factorio 2.1.17 install
at `~/.steam/debian-installation/steamapps/common/Factorio` — is already
in place.
