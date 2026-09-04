# Implementation Plan

What gets built, in what order, and how each phase is proved. Written to be
executed top to bottom; every phase ends in something verifiable rather than
something merely written.

The design is settled for the Core and the corridor. **The five trees are not
designed yet**, so this plan is arranged so that nothing waits on them until the
last possible moment.

---

## 0 · Ground rules

**Prototype-first.** Everything in this design is prototype work except the
victory trigger. `control.lua` should hold only: disabling vanilla's victory at
init (`set_no_victory`), and firing ours when the Ignition Array launches.
Anything else that reaches for a script is a signal the design took a wrong turn.

**Verify each phase before starting the next.** Two harnesses, both proven:
`tools/check-data-stage.sh` for loading, and the headless RCON rig
([spikes.md](spikes.md#the-rig)) for behaviour. Every phase below names what to
assert.

**Stub the capstones early.** The Core's chain consumes five capstone products
that will not exist for months. Define them as plain placeholder items from the
start — craftable from nothing, flagged as temporary — so the entire endgame is
testable long before any tree is built. Replacing a placeholder with a real
chain later is a recipe change and a migration, not a redesign.

**Dependencies.** `base` and `space-age`, required. A terrain pack such as Alien
Biomes should be an **optional** dependency used for tiles and decoratives if
present, with recoloured vanilla tiles as the fallback — the mod must load and
play without it, and the fallback path needs testing, not assuming.

---

## Phase 0 — Reset the repository

The repo still contains the previous Vulcanus ↔ Fulgora implementation — six
technologies, the quench turbine, its recipes and art — built to a design that no
longer exists.

- Remove `prototypes/*.lua` contents, the turbine's graphics, and its migrations.
- Rewrite `info.json`: the description still advertises the old chain.
- Keep `tools/check-data-stage.sh`, the art-derivation scripts, `.luacheckrc`
  and the CI lint workflow — all still useful.
- Keep the git history; nothing needs deleting from it.

**Done when:** the mod loads clean and adds nothing.

## Phase 1 — The Core as a place

The planet, and only the planet.

- `planet` prototype: pressure 5, gravity 50, magnetic-field 0, solar-power 0.
- Its own **map generation**: three tiles (kamacite plain, frost crust, slag
  flat), metallic ridges as cliffs, no water anywhere.
- Resources placed but inert: **kamacite ore** in very rich, widely spaced,
  finite patches; **melt vents** scarce; **gas vents** scarcer.
- **The landing site is a designed guarantee**: a starting ore patch and one melt
  vent within reach. Without it the foothold is impossible before the corridor
  runs at volume.
- **Core Discovery** technology — `unlock-space-location`, prerequisite
  promethium science. Measured in S1: without it the planet is unreachable.
- The space connection from the Shattered Planet.

**Assert:** surface generates; properties read 5 / 50 / 0 / 0; the placement
table from [spikes S1](spikes.md#results-so-far) still holds; a platform paths,
flies and docks; the starting area contains both a patch and a vent.

## Phase 2 — The local chain

The Core's own industry, all four mechanics, no capstones involved.

| Piece | Notes |
|---|---|
| Fluids | molten kamacite, helium-3 — both `auto_barrel = false` |
| Vent pump | drill with **both** fluid boxes; the vent's `minable.required_fluid` is helium-3 (proven in S4) |
| Kamacite plate | ore, smelted |
| **Gravity settling** | two recipe variants — metal-heavy and steam-heavy — both `surface_conditions` gravity ≥ 45 |
| Casting | settled melt → cast ingot |
| **Orbital homogenisation** | cast ingot → homogenised ingot, gravity 0 |
| **Whisker beds** | mod tile, `plant` with `growth_ticks`, and the **bed tender** that plants and harvests (pressure 1–9) |
| **Cold welding** | recipe at pressure ≤ 9, long duration, negligible machine power |
| Dross | the settling byproduct — needs two outlets, per the principles |

**Assert:** the pump stalls at `missing_required_fluid` and works when supplied;
settling is unavailable on Vulcanus (gravity 40) and available on the Core;
homogenisation is available only in orbit; a bed grows and is harvested by the
tender; welding runs at pressure 5 and 0 but not on a planet.

## Phase 3 — Arc storms

`lightning` and `lightning-attractor`, tuned deliberately against Fulgora:
rarer, far more damaging, banking a much larger charge per strike. Unprotected
buildings take real damage, so attractors are sited for coverage first and power
second.

**Assert:** strikes occur at the intended rate, damage unprotected buildings, and
charge an attractor's buffer. Rate and damage need in-client eyes, not just RCON.

## Phase 4 — The endgame structures

- **Ignition Array** — `rocket-silo`-derived, pressure 1–9, 100 parts, ~50 MW
  active.
- **Field Coil Segment** — its part, built only from the two end products.
- **Sealed roboport** — pressure 1–9 (proven in S2).
- **`control.lua`** — `set_no_victory` at init; `on_rocket_launched` from the
  Array calls `game.set_game_state{game_finished = true, player_won = true,
  can_continue = true}`.

**Assert:** the Array places only on the Core; consumes segments; fires; victory
triggers once and only once; vanilla's Edge victory no longer fires.

## Phase 5 — The sixth tech tree

Fifteen technologies in five tiers, and the **geodynamic science pack**
(`field conductor + reinforced frame + helium-3`, locked to pressure 1–9).

The five integration recipes are written against the **stubbed** capstone
products, so the whole tree is playable before a single tree exists. The two
middle stages — five intermediates, two end products — land here.

**Assert:** the pack cannot be crafted off the Core; research gates each stage;
the tree completes end to end using stubs.

## Phase 6 — The corridor

- The new asteroid, its **infected** variant, the infected chunk — remembering a
  chunk needs **both** an `asteroid-chunk` prototype **and** an item of the same
  name (S3).
- The **seed missile**: a projectile action combining `damage` with
  `create-entity` (conversion proven in S3).
- The **power material** and the generator that burns it.
- Asteroid spawn definitions along the route, keeping the far field otherwise
  barren — no metallic, carbonic or oxide chunks out there.

**Assert:** conversion works in flight; **and finish S3's open half in a client**
— that chunks from a seeded rock reach a collector. The script-damage harness
could not observe it, and the vanilla control failed identically, so this is the
one thing that must be watched by a person.

## Phase 7 — The trees

Blocked on design. Each tree replaces one stubbed capstone with a real chain, and
each is played before the next is designed.

## Phase 8 — Finishing

Balance against measured vanilla numbers; item weights set explicitly, never
derived; migrations for every rename; art passes.

---

## Order, and what can run in parallel

**1 → 2 → 4 → 5** is the spine: a place, an industry, a goal, a tech tree. Phase
3 and Phase 6 are independent of it and can be built whenever. Phase 7 waits on
design, and Phase 8 waits on play.

The point of stubbing the capstones is that **the entire endgame is playable at
the end of Phase 5** — long before the trees exist. That is the earliest possible
moment to discover the Core is boring, which is the thing worth finding out
first.

## What could still invalidate work

| Risk | Where it bites | Mitigation |
|---|---|---|
| Chunk collection does not work as designed | Phase 6 | Finish S3 in a client before building the rest of the corridor |
| The Core plays as tedious rather than austere | Phase 2 | Stubs make it playable at Phase 5; be willing to change the mechanics then |
| The bed tender is a chore | Phase 2 | Watch it in play; growth is meant to cost land, not attention |
| A tree cannot find an honest anchor | Phase 7 | The reserve pair, Vulcanus ↔ Aquilo, exists for exactly this |
