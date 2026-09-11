# Implementation Plan

What gets built, in what order, and how each phase is proved. Written to be
executed top to bottom; every phase ends in something verifiable rather than
something merely written.

The design is settled for the Core and the corridor. **The five trees are not
designed yet**, so this plan is arranged so that nothing waits on them until the
last possible moment.

---

## 0 · Ground rules

**Verify each phase before starting the next.** Two harnesses, both proven:
`tools/check-data-stage.sh` for loading, and the headless RCON rig
(`tools/rcon.py`) for behaviour. Every phase below names what to
assert.

**Dependencies.** `base` and `space-age`, required. A terrain pack such as Alien
Biomes should be an **optional** dependency used for tiles and decoratives if
present, with recoloured vanilla tiles as the fallback — the mod must load and
play without it, and the fallback path needs testing, not assuming.

---

## Phase 1 — The Core as a place

The planet, and only the planet.

## Phase 2 — The local chain

The Core's own industry, all four mechanics, no capstones involved.


## Phase 3 — The endgame structures


## Phase 4 — The sixth tech tree

Twenty-one technologies across five tiers, and the **geodynamic science
pack**, locked to pressure 1–9.

The five integration recipes are written against the **stubbed** capstone
products, so the whole tree is playable before a single tree exists. The two
middle stages — five intermediates, two end products — land here.

**Assert:** the pack cannot be crafted off the Core; research gates each stage;
the tree completes end to end using stubs.

## Phase 5 — The corridor

- The new asteroid, its **infected** variant, the infected chunk — remembering a
  chunk needs **both** an `asteroid-chunk` prototype **and** an item of the same
  name (S3).
- The **seed missile**: a projectile action combining `damage` with
  `create-entity` (conversion proven in S3).
- The **power material** and the generator that burns it.
- Asteroid spawn definitions along the route, keeping the far field otherwise
  barren — no metallic, carbonic or oxide chunks out there.

## Phase 7 — The trees

Blocked on design. Each tree replaces one stubbed capstone with a real chain, and
each is played before the next is designed.

## Phase 8 — Finishing

Balance against measured vanilla numbers; item weights set explicitly, never
derived; migrations for every rename; art passes.

