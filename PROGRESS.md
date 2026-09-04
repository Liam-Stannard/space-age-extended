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
smoke test in a throwaway scratch dir. The invocation, written down once so it
stops being rediscovered — `$B` is any scratch dir holding `mods/`
(a symlink to the repo plus a `mod-list.json`) and `cfg/config.ini` with its
own `write-data`:

```
factorio --create    $B/bench.zip --config $B/cfg/config.ini --mod-directory $B/mods
factorio --benchmark $B/bench.zip --benchmark-ticks 60 \
         --config $B/cfg/config.ini --mod-directory $B/mods
```

Give it its **own** `--config`/`write-data`. Another agent session's headless
server may be holding `~/.factorio/.lock`, and anything using the default
write-data then dies with "Is another instance already running?" — including
`tools/check-data-stage.sh`, which takes a binary path as `$1`, so a two-line
wrapper that `exec`s the real binary with `--config` appended gets it past the
lock without editing the script. Never `pkill` on a bare `factorio` pattern.

And a manual in-game playtest using console commands to fast-research, e.g.:

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

    Re-measured later on the isolated rig geometry (below): `big` is **not**
    deterministic either. Three runs gave 5 / 10 / 10 charges, plate 200/200
    throughout, 0–1 tiles lost; `huge` gave 10 / 10 / (plate destroyed), 1 /
    13 / 28 tiles. Read the metallic `big` row as **5–10, RNG**, not 5.
  - **Per-class ladder, PROMETHIUM** — the companion to the table above, and
    the one that matters, since the promethium route is the corridor this
    capability exists for. Promethium asteroids carry **double `max_health`
    and double `damage_per_hp` with identical resistances**
    (`space-age/prototypes/entity/asteroid.lua:140-162`; health
    200 / 800 / 4000 / 10000 for small/medium/big/huge), so the metallic
    ladder does not describe them. Entity names `<class>-promethium-asteroid`,
    verified against `prototypes.entity` on the running server. Same plate,
    same rig, same `range_mode` and `turn_range`.

    **The computed prediction — `big` = 2 charges, `huge` = 6 — is exactly
    right, and is the wrong number to plan with.** It is confirmed as the
    cost of killing the *parent rock* and nothing else: a `huge` engaged in
    isolation reads `damage_dealt = 10800` = 6 × ((5000−3000)×0.9), a `big`
    5400 = 2 × ((5000−2000)×0.9), both exact. What an *encounter* costs is
    dominated by the **cascade**: every dying asteroid above `small` spawns
    exactly three of the next size down (`asteroid.lua:255-278` — a
    three-entry `offsets` list with a random `offset_deviation` of
    ± collision_radius/2), and the plate shoots those too. Measured
    per-encounter cost is **4–5× the parent cost** for `big` and up to **8×**
    for `huge`.

    Lone 10-charge plate, steel-chest witness one tile behind:

    | class  | runs | charges spent            | plate after                            | witness                  | tiles lost      |
    |--------|------|--------------------------|----------------------------------------|--------------------------|-----------------|
    | small  | 2    | 1, 1                     | 200/200 ×2                             | 350/350 ×2               | 0, 0            |
    | medium | 3    | 4, 4, 4                  | 200/200 ×3                             | 350/350 ×3               | 0, 0, 0         |
    | big    | 5    | 8, 9, 10, 10, magazine emptied | 200/200 ×3, **50/200** ×1, **DESTROYED** ×1 | 350/350 ×4, DESTROYED ×1 | 0, 0, 2, 3, 4   |
    | huge   | 5    | 6, 6, 10, 10, magazine emptied | 200/200 ×4, **DESTROYED** ×1           | 350/350 ×5               | 0, 0, 1, 2, 7   |

    Continuous rim on the same hull, **1×1-ERA** (78 plates × 10 charges =
    780 loaded), same single inbound rock. These are not the shipped entity's
    numbers — the 3×2 rim stands 24 plates and its own figures are in the
    footprint write-up below:

    | class  | runs | charges spent (whole rim) | plates lost | plates damaged | tiles lost |
    |--------|------|---------------------------|-------------|----------------|------------|
    | medium | 2    | 4, 4                      | 0/78        | 0              | 0          |
    | big    | 3    | 10, 13, 14                | 0/78        | 0              | 0          |
    | huge   | 3    | 24, 34, 48                | 0/78        | 0              | 0          |

    **A rim is not a more expensive lone plate; it is a different outcome.**
    Eight loaded rim runs across three classes lost zero plates, took zero
    plate damage and lost zero foundation tiles, including against `huge`.
    The lone plate leaked in 6 of 10 `big`/`huge` runs and was destroyed in 2
    of them. The rim spends more charges precisely *because* it catches the
    cascade the lone plate lets past.

    Empty-plate control, same rocks, 0 charges:

    | class  | plate      | witness   | hull                                                        |
    |--------|------------|-----------|-------------------------------------------------------------|
    | small  | DESTROYED  | 350/350   | 0 tiles                                                     |
    | medium | DESTROYED  | DESTROYED | 4 tiles                                                     |
    | big    | DESTROYED  | DESTROYED | 30 tiles by t+700, 90 by t+1300, rock still alive at 1672/4000 |
    | huge   | DESTROYED  | DESTROYED | 63 tiles by t+700, then **the whole platform**: see below   |
    | big, unloaded rim  | 5 of 78 destroyed | — | 90 tiles                                  |
    | huge, unloaded rim | 10 of 78 destroyed | — | the entire 620-tile half                 |

    Note the first row. **A promethium `small` — the cheapest rock in the
    game out there — destroys a 200 HP plate outright**, while leaving a
    350 HP steel chest one tile behind it untouched. The plate has no
    survivability margin at all on this route.

    **Every plate health figure in this section was taken against the 200 hp
    prototype**, which is what these runs were measured on. The plate now
    ships at 400, and the contact damage behind these deaths has since been
    measured exactly (promethium `small` 200, `medium` 1280, `big` 9550) —
    see "Numbers pass" below. Nothing else in these tables changes: the
    charge counts, tile losses and the rim-vs-lone conclusion all stand.

    Two rig facts learned paying for these numbers, both now commented in
    the scenario files:
    - **A rampaging asteroid can delete the whole platform's foundation in
      one step.** Once enough hull is eaten that the remainder stops being
      connected to the hub, every foundation tile goes at once — both test
      columns simultaneously read 0 tiles and everything destroyed. That is
      indistinguishable from "the subject failed catastrophically" unless
      the platform-wide tile count is sampled too, which the measure
      scenario now does.
    - **A `huge` promethium asteroid can hard-spin the server**: 100% CPU,
      `game.tick` frozen, every RCON call timing out, no error logged, no
      recovery. Seen three times, always on huge-promethium. Mitigated by
      short exposure windows (700 + 600 ticks rather than 900 + 900) and by
      culling the control side between samples; not eliminated. **But short
      windows are not free**: the 700 + 600 window truncated the parity-gap
      runs (§3 of the footprint write-up), and the 27-run long-window re-run —
      polling to quiescence, out to dt 11560, 43 minutes of wall clock — never
      hard-spun once. Cull and poll rather than cutting the window short.
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
    The prototype value is the guaranteed minimum stock, not the stock —
    **except where the floor equals the inventory's capacity**, as it does on
    the shipped plate (20 == 1 slot × stack 20). There is then no headroom to
    overshoot into, and the settle point is the floor for every force at every
    research level; see T14 below.
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
- **An entity with no item that places it cannot be ghosted.**
  `create_entity{name = "entity-ghost", inner_name = X}` fails outright with
  *"X can not be part a entity ghost"* unless some item has
  `place_result = X`. Inside a `pcall` that reads as "the ghost oracle said
  no" and silently zeroes the revive column of a placement matrix in every
  cell. Give throwaway spike prototypes a throwaway placing item.
- **`LuaWireConnector`'s methods take a dot, not a colon.**
  `a:connect_to(b, ...)` passes the connector itself as the target, so the
  wire is never made — and every circuit measurement after it reads an
  unconnected network without erroring. Spell it `a.connect_to(b, ...)`.
- **An inserter's `drop_target` is nil on the tick it is created** and only
  resolves once the game has stepped. Census it from a measurement step, not
  from the setup step, or a feedability count comes out 0/76.
- **A concentric belt ring cannot feed the corner of any footprint.** The
  corner tile of ring *k* is diagonal to the corner tile of ring *k+1*, so
  the inserter that would serve a corner plate has no belt orthogonally
  behind it. That is a property of concentric squares, not of the plate —
  measure corner questions against "does a tile an inserter can stand on
  exist at all", not against one belt layout.
- **A 3600-tick exposure flight is not a damage instrument.** On a
  Nauvis→Vulcanus leg at speed 0.54 a plated rim was not touched at all in
  any of four conditions. If the question is "does X leak", aim an asteroid
  at X and keep an instrument check (a condition that *must* leak) in the
  run, or a flawless result means nothing.
- **A fixed post-spawn window is not a measurement; poll to quiescence.** A
  promethium cascade freezes the measured state anywhere from dt 256 to dt
  1985 and leaves the near field busy out to dt 9698, so a fixed 1300-tick
  window truncates some runs and not others and the truncation is invisible in
  the output. Poll until nothing in a ±40 near-field box (charges, tiles,
  plates, witness) has changed and no asteroid is left in the box, held for
  ~1200 ticks under a hard cap, and report the settle tick. Scope the test to
  the near field: fragments that miss keep flying at full hp far off the
  platform (one at (46, −62) at dt 9300) and can never come back, so a
  surface-wide wait never terminates.
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

### Reactive Edge Plating (branch `reactive-edge-plating-finish`, unmerged, ahead of `master`)

Everything mechanical is now settled and measured. What is left is one art
package, one real ingredient chain, a reference rim pattern — which now has a
measured constraint on it, the cascade-failure finding below — and a
playtest.

- [ ] **Client playtest.** Three things headless testing cannot answer:
      whether the four stand-in facings read as different in a client,
      whether rotate-to-face-void placement is comfortable (vanilla asks the
      same of the asteroid collector), and whether a 3×2 panel is pleasant to
      lay along a rim by hand as opposed to by blueprint.
- [ ] **A reference rim pattern is still owed.** The 3×2 footprint solved
      *feedability* — every plate on a square rim has a tile an inserter can
      stand on, at every size tested — but nobody has yet written down the
      belt/inserter layout a player should copy. Two hard constraints on it:
      it **must not be a closed belt loop** (a saturated loop deadlocked for
      20,000 ticks with 44 plates dry), and every footprint's corner-owning
      plate needs one deliberate tile (a spur, a buffer chest, or a chamfer).
      **The earlier chamfer guidance is superseded**: chamfering the hull is
      now *optional advice* for tidying a corner, not the answer to corner
      feeding — the footprint is.
- [ ] **Cascade failure: a damaged rim has to be repaired before the next
      `huge` encounter.** This is measured, not predicted, and it is new. One
      lost 3×2 plate opens a hole of **exactly 6 tiles** (2 deep × 3 wide), and
      a 6-tile hole leaked in **4 of 10** aimed promethium `huge` runs — losing
      2, 8, 20 and 32 foundation tiles, **destroying further plates in two of
      them** (1 and 2), and damaging the witness behind the gap in two. So the
      first plate lost materially raises the odds of losing the next: rim
      damage compounds. Nothing repairs it automatically — **there are no
      construction robots on a platform** (`roboport` sits behind
      `surface_conditions` pressure ≥ 10 and platforms are pressure 0, noted on
      `automated_ammo_count` in `prototypes/entity.lua`), so a player has to
      notice and act, which is exactly what the circuit-network `read_ammo`
      interface exists to support. **This changes no shipped number and does
      not re-open the footprint decision** (3×2 stands on corner feedability).
      It is an input to the two items above: the **reference rim pattern**
      should make a lost plate easy to see and easy to replace, and should
      probably carry a documented missing-plate / low-charge alert wiring; and
      the **client playtest** should include flying a rim that has already lost
      a plate. Measurement in §3 of the footprint write-up below.
- [ ] **Replace the provisional recipe and technology** with the real
      Thermal-Shock Composite chain and its gating (the `explosives`
      prerequisite goes away with them). This is the one deliberate
      provisional seam in the capability and is marked
      `TODO(thermal-shock-composite)` in `prototypes/recipe.lua`. It is
      blocked on tree 2 building the chain; **do not substitute a different
      real ingredient in the meantime.**
- [ ] **Real art**: the entity sprite with folded/preparing/attacking states,
      plus the three new icons in `graphics/icon-prompts.md`. Nothing numeric
      depends on it.
- [ ] **Merge decision.** Rebased onto current master and purely additive, but
      not merged and not pushed.
- [x] **Measure the promethium ladder.** Done — table above. The computed
      2-for-`big` / 6-for-`huge` figures are confirmed exactly as *parent-kill*
      costs and are 4–8× too low as *encounter* costs, because the cascade
      dominates: lone plate `big` 8–10, `huge` 6–10 (both magazine-capped);
      continuous rim `big` 10–14, `huge` 24–48. **Those rim figures are the
      1×1-era measurement**, taken on a 78-plate rim before the footprint was
      settled; the shipped 3×2 rim's figures are `big` a deterministic 14 and
      `huge` a non-deterministic **22–40 on a continuous rim** (6–46 across
      every gap condition measured), below.
- [x] **Footprint settled at 3 wide × 2 deep.** Measured against 1x1 and 2x2
      built as real prototypes side by side — full write-up below.
- [x] **Corner feeding.** Solved by the footprint, not by asking the player to
      chamfer: at 3x2 every plate on a square rim has a tile an inserter can
      stand on, at every platform size tested (0 unreachable, 24/24 and 48/48
      simultaneously matchable at 20×20 and 40×40).
- [x] **Numbers pass done** — `max_health`, `resistances`, `cooldown`, the
      ammo triple (`inventory_size` / charge `stack_size` /
      `automated_ammo_count`), both stack sizes, `mining_time`, the charge's
      damage and the rest are each measured or anchored in a one-line note in
      the prototype. Write-up below; data stage clean, 60-tick benchmark
      recorded.
- [x] **The plate's own survivability is decided: the rim is the answer.**
      Contact damage was measured directly (promethium `small` 200, `medium`
      1280, `big` 9550), so nothing above `small` is survivable at any sane hit
      point total and HP cannot be the answer to a leak. `max_health` goes
      200 → 400 only to get off the knife edge where the cheapest rock on the
      route was a guaranteed plate kill; `resistances` stays unset on purpose,
      even though `impact` resistance was measured to work, because absorbing
      impacts is another tree's payoff.
- [x] **The perimeter table is recomputed for 3×2**, with the 40×40 plate
      count measured rather than divided out (48, not 156/3 = 52). "Doubling
      the ship halves the relative cost of armouring it" still holds, and at
      3×2 it holds exactly.
- [x] **Circuit connector** added — a per-direction vector, `read_ammo`
      verified in all four rotations. (**`heating_energy`** is no longer open
      either: unset/0W is correct by construction for a vacuum-only entity —
      see the engine-facts list.)
- [x] **Target priority list works, including from the circuit network.** So
      "ignore small chunks and leave them to the collectors" is an
      automatable decision, not a flat income penalty for plating a mining
      platform. Details below. No `control.lua` change; none was needed.
- [x] **`control.lua` and `scripts/` untouched.** The whole capability is
      data-stage, and nothing in the numbers pass needed script.

#### Footprint: measured, and why it is 3×2

1x1, 2x2 and 3x2 were built as real prototypes on the same platform and
measured side by side. Every number below is from the running engine.

**1. Corner feedability — the measurement that decided it.** Asked
topology-independently, so no cleverer belt layout can argue it away: for
every plate on a fully built rim, does *any* orthogonally adjacent tile exist
that is on the platform and is not itself under a plate (an inserter cannot
stand diagonally), and can all the plates be satisfied *at once* (maximum
bipartite matching between plates and free adjacent tiles)?

| | 1x1 | 2x2 | 3x2 |
|---|---|---|---|
| Unfeedable by **any** layout | **4** (every size) | **1–4** (size-dependent) | **0** (every size) |
| Feedable simultaneously, 20×20 | 68/76 | 32/36 | **24/24** |
| …at sizes 10 / 21 / 22 / 31 | 28/36, 72/80, 76/84, 112/120 | 12/16, 35/36, 36/40, 55/56 | **8/8, 24/24, 24/24, 36/36** |

At 1x1 the outermost corner tile's four orthogonal neighbours are all void or
plate, so it can never be loaded; its two neighbours then contend for the one
diagonal-interior tile, so three plates per corner go dry in a real build.
At 2x2 the corner block is boxed in by the perpendicular band. At 3x2 the
third tile reaches past that band. **The 12-of-76 figure measured earlier is
confirmed as what a concrete belt ring realises; 8-of-76 is the floor no
layout can beat.**

A naive concentric belt+inserter ring realises 63/76 (1x1), 32/36 (2x2) and
20/24 (3x2) — every footprint's corner-owning plate needs one deliberate tile
(a spur, a buffer chest, or a chamfer), because the corner tile of ring *k* is
diagonal to the corner tile of ring *k+1* whatever the plate looks like. The
difference is that at 3x2 that tile exists and at 1x1 four of them cannot.
Adding corner bump-outs to the ring does **not** help at d=1 — it costs more
inserter-ring tiles than it buys (1x1 went 13 → 17 unfed).

**2. Floor and entity count**, measured on the real build, 20×20 rim:

| | 1x1 | 2x2 | 3x2 |
|---|---|---|---|
| Rings of floor (plate + inserter + belt) | 3 | 4 | 4 |
| Plates on a 20×20 rim | 76 | 36 | **24** |
| Inserters built | 63 | 55 | 55 |
| Plates per 12 rim tiles | 12 | 6 | 4 |
| Rim quantised in | 1 | 2 | 3 |
| Hole opened by one lost plate | 1 tile | 4 tiles | 6 tiles |
| Charges standing, 20×20 rim @ 20/plate | 1520 | 720 | **480** |

The predicted table was right on rings, plates and quantisation; it was wrong
about the hole one lost plate opens — for a 2-deep plate the hole is the whole
2×w block (4 and 6 tiles), not w. And the standing-charge figures are 720 and
480 exactly, not "~760" and "~500".

**3. A 2-tile parity gap is covered; a 6-tile gap is not.** Quantising in 3s
leaves up to 2 tiles over on an arbitrary edge, so 2 is the gap size the
footprint actually creates. Measured by aiming one promethium asteroid at the
centre of a deliberate hole in the north band of a fully plated 20×20, with a
steel-chest witness one tile behind the hole.

**The measurement was re-run properly, and the earlier figures are
superseded.** The old runs used a fixed 700 + 600 tick window. The measured
state actually freezes anywhere from dt 256 to dt 1985 and the near field only
goes quiet between dt 1187 and dt 9698 — so **that window truncated some runs
and not others**. The re-run polls to quiescence instead: zero asteroids left
inside a **±40 near-field box** *and* no change in the measured state
(charges, tiles, plates, witness), held for 1200 ticks, under a hard cap.
27 runs, promethium `huge`:

| north band | runs | charges (range, median) | leaked | plates destroyed / damaged | witness |
|---|---|---|---|---|---|
| continuous (gap 0) | 4 | 22–40, median 31 | **0/4** | 0 / 0 | 350/350 ×4 |
| 2-tile hole | 10 | 15–46, median 34 | **0/10** | 0 / 1 scratched | 350/350 ×10 |
| 6-tile hole | 10 | 6–43, median 27 | **4/10** — 2, 8, 20, 32 tiles | **1 and 2 destroyed**, in two separate runs | 290/350 in two runs |
| gap 18 — instrument check | 3 | 360, deterministic | **3/3** — 400 tiles | **all 18 destroyed** | DESTROYED ×3 |

Every run settled well inside the cap — ticks to quiescence ranged
**1187–9698**, i.e. 1–7× the old window, and the longest run was confirmed
quiet out to dt 11560. The server never hard-spun across the whole 43-minute
session.

(The ±40 scope is load-bearing, not a convenience: fragments that *miss* keep
flying and are still at full hp thousands of ticks later far off the platform —
one sat at (46, −62) at dt 9300. The platform is parked at speed 0 so they
cannot come back, but waiting on the surface-wide count never terminates.)

**Fixing the window did not rescue the old claim; it made it worse.** The
earlier single leaked 6-tile run was not a fluke to be explained away by a
short window — it was a sample from a real failure mode, and the long window
shows the worst case is worse than what had been recorded: 32 tiles and a
destroyed plate, against the 6 tiles logged before.

**A 2-tile gap is covered: 0/10 leaked.** Neighbouring plates do cover a
2-tile hole, and 2 tiles is the only gap a 3-wide plate produces when a rim is
quantised. **So the parity-gap argument survives for the gaps the footprint
actually creates** — and only for those.

**A 6-tile gap is not covered: 4/10 leaked.** "Gaps up to 6 tiles do not leak"
holds **only for `big`**, which is deterministic at 14 charges across three or
more runs at each of gap 0, 2 and 6 and never let a tile past. For `huge` it is
false, and it must not be restated.

**`huge` is genuinely non-deterministic, and the residual variance is in cost,
not outcome.** Charge spend is a wide overlapping distribution at every gap
size (22–40, 15–46, 6–43) and the gap-size signal in the charge column is nil —
gap 6 has the *lowest* median precisely because a leaking rock is one that is
not being shot at. So `huge` still must not be quoted as a point value: for
the shipped 3×2 rim it is roughly **6–46 charges, median ~30**, and the old
"20–41" is superseded.

**The instrument check is sound, and now deterministic.** With the north band
removed entirely (gap 18) the same `huge` promethium is a total loss — 360
charges, all 400 foundation tiles, all 18 remaining plates, witness destroyed —
identical to the tick across three runs. The rig can definitely see a leak, so
the clean gap-0 and gap-2 results mean something.

**Where this bites elsewhere in this document:** the survivability decision's
"no plate has been destroyed, or even damaged, in any loaded rim run" now needs
the word *continuous* doing real work. It holds at gap 0, and at gap 2 with one
plate scratched; behind a **6-tile** gap two runs lost plates outright. That
paragraph has been corrected to say so.

**The design consequence, and it is the one that matters: one lost 3×2 plate
opens a hole of exactly 6 tiles** (2 deep × 3 wide — the "hole one lost plate
opens" row in §2). The gap size that leaks about 40% of the time against `huge`
is therefore precisely the gap a plate loss creates, and two of those leaking
runs destroyed further plates. **Losing one plate materially raises the chance
of losing more: rim damage compounds.** Written up as a design input in the
outstanding-work list above.

**This does not re-open the footprint decision.** 3×2 stands on corner
feedability — 0 unfeedable against a hard floor of 4 structurally impossible
for 1×1, independently reconfirmed at six platform sizes — not on gap
coverage. And no shipped number moves on this result. What it changes is what
may be claimed for a *damaged* rim.

The 3600-tick exposure flight could **not** answer this: on a Nauvis→Vulcanus
leg at speed 0.54, none of 1x1 / 2x2 / 3x2 was touched at all (0 tiles lost,
0 charges spent for 1x1 and 2x2), and the only condition that lost anything
was the unplated control — which lost the *entire platform*. Aiming the rock
is the only way to get a signal out of this question.

**4. Corner arc coverage — no hole.** Swept single asteroids through the void
off the NW corner on a 1-tile grid and recorded which plate fired. The
corner's western approach is engaged by the neighbouring **west**-facing
plate, the northern approach by the **north**-facing one, and their coverage
overlaps; nothing inside range went unengaged. (One artefact worth knowing:
probes spawned 0.5 tiles off the hull are already in contact and destroy
themselves against the foundation before any turret reacts — that column of
the map is not a coverage hole.)

**5. Placement still admits exactly one facing per position.** The 44-cell
matrix was rebuilt for the rotated footprint (rotation swaps 3×2 to 2×3, so
every cell needs its own computed centre) and comes out a perfect diagonal
under all three valid oracles — `can_place_entity` with `manual`,
`can_place_entity` with `blueprint_ghost`, and reviving a real `entity-ghost`
— with `create_entity` disagreeing in every refused cell, as always. Corners
admit both outward facings but only the **one** lateral offset that sits flush
inside the platform; the other two would hang the plate off the edge. That is
the pinwheel a rim wants, and it falls out of the rules rather than having to
be taught. The same matrix was measured for 1x1 and 2x2, so the diagonal is a
property of the rules, not of this footprint.

**Input to the numbers pass.** A 20×20 rim now stands 24 plates, not 76. At
`automated_ammo_count = 10` that is a guaranteed 240 charges standing (480 at
a 20-charge fill), against 760/1520 before. The measured encounter costs are
unchanged — a rim spends 4 charges on a promethium `medium`, 14 on a `big` and
22–40 on a `huge` (continuous rim, not reproducible) — so at a floor of 10 a
20×20 rim's 240 standing charges are about 17 `big` encounters or 6–10 `huge`
ones, where at 1x1 it was three times that.
That is the number the numbers pass has to be comfortable with; the levers are
`inventory_size`, the charge's stack size, and the per-charge damage, not the
footprint. **Answered below** — `automated_ammo_count` went to 20, which puts
the guaranteed standing buffer back at 480.

#### Circuit control (both verified over RCON)

**`read_ammo`.** Four plates, one per rim face in the one rotation the
buildability rules allow there, loaded with 3/5/7/9 charges and each wired to
its own red network. Every network read back exactly its own plate's count, in
every rotation. Prototype-side this needed only `circuit_connector` and
`circuit_wire_max_distance`.

**The connector must have exactly 4 entries**, and the engine enforces it in
both directions: throwaway clones carrying 1 and 8 entries were each refused
at load with `In circuit connector definitions expected table of 4 elements
but N were given`. `prototype-api.json` states the rule (8 for
building-direction-8-way, 16 for 16-way, **4 for `turret_base_has_direction`**,
else 1) and vanilla's railgun turret supplies 8 only because it is an 8-way
building — copying its list would not have loaded. The helpers come from
`core/lualib/circuit-connector-sprites.lua`, which is on every mod's
data-stage Lua path, so the plain `require("circuit-connector-sprites")` that
vanilla's own `turrets.lua` opens with is the correct spelling — no
`__core__.` prefix. It defines `circuit_connector_definitions`,
`universal_connector_template` and `default_circuit_wire_max_distance` (= 9).

**Target priority list — POSITIVE, all three ways.** A plate holding 20
charges, one `small` and one `medium` metallic asteroid probed in turn on the
`enemy` force, with a vanilla gun turret as the control:

| configuration | `small` | `medium` |
|---|---|---|
| defaults | engaged, killed | engaged, killed |
| entity-side (`set_priority_target` + `ignore_unprioritised_targets`) | **ignored**, 0 damage | engaged |
| circuit-gated, condition satisfied | **ignored**, 0 damage | engaged |
| circuit-gated, condition *not* satisfied | engaged, killed | engaged, killed |
| list read from the wire (`set_priority_list`) | **ignored**, 0 damage | engaged |

So the acceptance criterion is met: flipping the one signal the condition
tests switches a rim between ignoring `small` and engaging it, live. Which
half is which:

- **Prototype-side:** only the circuit connector, and only for the two
  circuit-driven variants. The entity-side variant needs nothing at all.
- **Player-side:** `LuaEntity.set_priority_target` /
  `ignore_unprioritised_targets`, and on the control behaviour
  `set_ignore_unlisted_targets` + `ignore_unlisted_targets_condition`, or
  `set_priority_list = true` with the wanted target named by an **entity-type
  signal** on the network. All of it is the vanilla turret GUI.

This matters because `asteroid-collector` has `collection_radius = 7.5`, so a
plate firing at contact range kills chunks well inside the radius of any
collector behind it. Plating a mining platform's rim used to be a flat cut in
income; it is now a decision the player can automate.

#### Numbers pass: every number measured or anchored

Done on top of the 3×2 footprint. Every number on the entity and the charge
is now either measured on the running engine or carries a one-line note in the
prototype saying what it is anchored to. The only things left provisional in
this capability are the **art** and the **recipe + technology**, and the second
is deliberate: their real ingredient is Thermal-Shock Composite, which does not
exist yet, and the seam is marked `TODO(thermal-shock-composite)` at the head
of the Reactive Edge Plating block in `prototypes/recipe.lua`.

| number | was | now | anchored to |
|---|---|---|---|
| `max_health` | 200 | **400** | vanilla gun-turret's own 400; survives exactly one leaked promethium `small` (measured 200 damage) and nothing above it |
| `resistances` | none | **none, deliberately** | measured: contact damage is `impact` and resistances *do* apply — not taken, because absorbing impacts is another tree's payoff |
| `cooldown` | 15 (placeholder) | **15** | measured not to be binding; all firing is done by dt 1985 at the latest (27 long-window runs), and 130 shots fit inside that |
| `inventory_size` | 1 | **1** | capacity == the charge's stack size, one number; every vanilla ammo turret uses 1 |
| charge `stack_size` | 20 | **20** | 2× the worst measured single-plate drain (10, magazine-capped); 200 kg/stack keeps resupply a visible commitment |
| `automated_ammo_count` | 10 | **20** | == capacity, so the guaranteed stock *is* the capacity at any research level; twice the (lower-bound) worst single-plate drain, so headroom against one encounter rather than a proof; railgun turret's own floor==capacity arrangement |
| `minable.mining_time` | 0.2 | **0.2** | asteroid-collector's 0.2, the other rim-line entity, not gun-turret's 0.5 |
| charge damage | 5000 physical | **5000 physical** | the ladder window: D ≥ 4223 one-shots a metallic `big`, D ≥ 8556 would one-shot a `huge` |
| plate item `stack_size` | 50 | **50** | gun-turret's item stack; one stack lays a 20×20 rim twice or a 40×40 once |
| `weight` (both) | — | unchanged | rocket cargo only; measured to contribute nothing to platform mass |

**T13 — contact damage, measured directly.** The survivability call could not
be made from "the 200 hp plate died", which only bounds the damage from below.
So the plate was rebuilt with `max_health = 1000000`, which makes it *survive*
the contact, and the health delta then **is** the damage. Empty plate (0
charges, so it never shoots and the rock always lands), one promethium
asteroid on the `enemy` force spawned 11 tiles out, steel-chest witness one
tile behind, vanilla gun-turret control on the same foundation:

| promethium class | damage to the plate | witness | tiles |
|---|---|---|---|
| small | **200** | 350/350 | 0 |
| medium | **1280** | 350/350 | 0 |
| big | **9550** | 350/350 | 1 |

`huge` was not run: a huge promethium asteroid is the one that hard-spins the
server, and the three rows above already settle the question.

**T13b — the damage type.** A second probe carried a *fingerprint* resistance
set — a distinct percent for every damage type, so whichever one applies is
named by the ratio that survives (physical 90 → 20, impact 50 → 100, explosion
25 → 150, laser 75 → 50, fire 10 → 180, acid 60 → 80, poison 80 → 40, electric
40 → 120). The promethium `small` that deals 200 unresisted dealt exactly
**100**. So asteroid contact damage is **`impact`**, and resistances *do*
apply to it.

**The survivability decision: the rim is the answer.** Those numbers make it
one-sided rather than a judgement call. A `medium` is 3.2× a 400 hp plate and
a `big` 24×, so no sane hit point total survives a leak of anything above
`small`; HP cannot be the answer. A **continuous** rim is: across the 1×1-era
runs, the 3×2 gap-0 runs and all ten 3×2 2-tile-gap runs, **no plate has ever
been destroyed, and exactly one was damaged** — scratched, in one `huge`
2-tile-gap run. That is why **the plate is specified only as a continuous
rim**, and it is the whole of the claim: behind a **6-tile** gap the long-window
re-run destroyed plates in 2 of 10 `huge` runs and lost up to 32 foundation
tiles, so a rim with a hole in it is not covered by this sentence. See §3 of
the footprint write-up, and the cascade-failure item in the outstanding-work
list.

400 is taken anyway, for one reason that is not "buy survivability": the old
200 sat *exactly* on the measured `small` figure, so the cheapest rock on the
promethium route was a guaranteed plate kill and a rim that ran dry deleted
itself to gravel. At 400 a dry plate eats one `small` and survives at 200/400,
so the rim degrades gradually and visibly instead of vanishing. It is
turret-grade (gun-turret 400), not armour-grade (railgun turret 4000, rocket
turret 1500).

**`resistances` stays unset as a decision.** An `impact` resistance is a real,
measured, available lever — and it is exactly the thing this capability must
not do. A percent impact resistance is literally "absorbs impacts", scaling
with the size of the rock; that is the hull-armour / deflector answer another
tree owes. Leaving it unset keeps the failure economy two-tiered: cheap charges
consumed **per impact**, expensive plates consumed **per failure**.

**T14 — the ammo triple behaves.** With the shipped numbers, a fast inserter
fed from a full chest settles the plate at **exactly 20** and stops, with
nothing stranded in the inserter's hand — floor == capacity does not jam.
Vanilla gun-turret on an identical rig settled at 10 in the same run, so the
rig is sound. (Rig gotcha found here and worth keeping: an inserter's
`direction` is the side it **picks up** from, not the side it drops to.)

That first run used a **fast** inserter at bonus 0, i.e. hand size 1 — the one
case where an overshoot is impossible, so it did not actually test the claim.
Closed by a second run at **`inserter_stack_size_bonus = 6`**: the plate
pinned at `charges = 20` with `inserter_held = 1`, the leftover charge of the
hand stranded in the inserter, while the vanilla gun-turret control on the
same rig went 10 → 14 as the ladder predicts. So floor == capacity holds under
a full hand: the inserter stops at capacity and simply keeps the remainder,
and no research level moves this plate's stock off 20.

#### The perimeter table, recomputed for 3×2

Plate counts are **measured** on the rig (`t7g-reach.lua` at
`storage.fp_side = 20` and `= 40`), not divided out of the perimeter — the
naive 156/3 = 52 for a 40×40 is wrong, the real count is 48. The rule the
engine actually realises is 4 × ⌊(side − 2)/3⌋.

| Platform | Tiles | Rim tiles | Rim as % | Plates (measured) | Plated band | Fully-plated rim cost |
|---|---|---|---|---|---|---|
| 20 × 20 | 400 | 76 | 19% | **24** | 144 tiles (36%) | 48 composite, 120 tungsten plate, 240 steel |
| 40 × 40 | 1600 | 156 | 10% | **48** | 288 tiles (18%) | 96 composite, 240 tungsten plate, 480 steel |

Costed at the provisional plate recipe the old table used (2 Thermal-Shock
Composite + 5 tungsten plate + 10 steel). The composite line is *not* in the
shipped recipe — that is the marked seam. Against the old 1×1 table the same
rims cost 152/380/760 and 312/780/1560, so **3×2 cuts the build cost of
armouring a rim to just under a third**, on top of cutting the inserter count.

Both rims are feedable with no unfeedable plate at either size (0 unreachable,
24/24 and 48/48 simultaneously matchable). The 20×20 quantises exactly; the
40×40 leaves a 2-tile parity gap per band (16 tiles in all). **A 2-tile gap is
covered**: it never leaked in ten long-window promethium `huge` runs, nor at
`big`. (A 6-tile gap — the hole one lost plate opens — is a different matter
and does leak; see §3 of the footprint write-up above.)

**"Doubling the ship halves the relative cost" still holds, and now exactly.**
Plates per platform tile: 24/400 = **0.060** at 20×20, 48/1600 = **0.030** at
40×40 — a clean factor of two, where the 1×1 footprint gave 0.190 → 0.0975, a
factor of 1.95. Perimeter scales with circumference and production with area,
so compact-and-large stays cheap to armour and long-and-thin stays ruinous;
3×2 does not blunt that argument, it sharpens it.

**Standing buffer.** With `automated_ammo_count = 20` == capacity, every plate
on a fed rim is guaranteed 20 charges. Against the measured burn rate of **50
charges / 3600 ticks = 0.83 charges/s** under moderate exposure:

| Platform | Plates | Guaranteed standing charges | Seconds of measured burn | Encounters covered |
|---|---|---|---|---|
| 20 × 20 | 24 | **480** | **578 s** (9 min 38 s) | ~120 `medium`, **34** `big`, 12–21 `huge` |
| 40 × 40 | 48 | **960** | **1157 s** (19 min 17 s) | ~240 `medium`, **68** `big`, 24–43 `huge` |

(Encounter costs are the measured rim-wide promethium figures: `medium` 4,
`big` a deterministic 14, `huge` 22–40 on a continuous rim and not
reproducible — the `huge` column is a spread, not a tolerance. A single `big`
encounter takes 14 of the 480, leaving 466. A 40×40 also presents more rim to be hit, so its extra
seconds are not a free doubling of endurance.) At the old floor of 10 the
20×20 stood 240 charges = 289 s, which is where "a supply hiccup empties it
three times faster than the 1×1 rim did" came from; 20 puts it back.

**Data stage and benchmark.** `./tools/check-data-stage.sh` clean. In-engine
60-tick benchmark on a fresh save with the mod loaded, run twice: **60 updates
in 8.4–9.9 ms — avg 0.14–0.17 ms, min ~0.10 ms, max 0.29–0.32 ms** (Factorio
2.1.17, throwaway scratch dir with its own `--config`/`write-data`). The
spread between runs is ordinary timing noise; it is recorded as a range
because a single figure would not reproduce.

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
- [ ] **Replace the provisional recipe and technology** on the plating branch
      with the real chain and its gating (the `explosives` prerequisite goes
      away with them). Same item as the plating list above, seen from this
      side: the plating branch is finished apart from art and this seam, and
      the seam is blocked on Thermal-Shock Composite existing.
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
