# Factorio Building — Art & Implementation Specification

**Drop Crusher.** First draft — a brief, enough to commission and judge a concept
sheet. Not a specification: §6, §12 and §13 stay open until a sheet is approved
and a canonical plate has been measured.

**This building is forced, not optional.** Vanilla's `crusher` carries
`surface_conditions` of `gravity` min 0 **max 0** — it is space-only
(`space-age/prototypes/entity/entities.lua:841`). Beneficiation on the Core's
surface cannot exist without a new crusher, so this is the first thing the
production tree needs and the first thing that should be built.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **passed — `concept/v2-sheet.png`** |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3 | **ready** |
| 5 | Working animation | portrait 2:3 | The drop loop reads as a drop | blocked on 1 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

---

# 1. Building Overview

**Building Name:** `Drop Crusher`
**Internal Prototype Name:** `sae-drop-crusher`

**Building Type:** `assembling-machine` with its own crafting category. Not a
copy of vanilla's crusher: that one is a rotating mill built for zero g, and this
one is its opposite.

**Purpose:** Breaks kamacite ore into **crushed kamacite** and **fines**, the two
streams the whole production tree stands on. It does it by lifting the charge and
dropping it, because at 50 g a fall does the work a motor would have to do
anywhere else.

**Why it matters:** it is the gate on T1, and T1 is what makes plate smelting
load-bearing rather than skippable. It is also the cheapest possible statement of
the Core's physics — the same gravity that settles the melt breaks the ore.

**Locale:** *"Lifts the ore and lets the planet do the rest."* / *"At fifty
gravities a drop is cheaper than a mill. Two streams out: the coarse fraction to
be smelted, the fines to the carbonyl line."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 3×3 (`collision_box {-1.4,-1.4},{1.4,1.4}`) |
| Directions | 1 |
| Crafting category | `sae-crushing` — its own, so the space crusher can never run it |
| Energy | **Low: 200 kW.** The fall is free; the lift is not |
| Surface conditions | `gravity` ≥ 45 — the Core's surface alone |
| Module slots | 2 |

**The recipe, first pass:** 2 kamacite ore → 3 crushed kamacite + 1 kamacite
fines, 2 s.

**Plate smelting must be re-sourced onto crushed kamacite** at the same time this
lands, or T1 remains skippable and this building is decoration.
`recipes.lua:sae-kamacite-smelting` currently takes raw ore; it should take
crushed.

### Why it is not a reskin

Vanilla's crusher spins and is locked to zero g. This one drops and is locked to
high g. The two cannot be built in the same place, they cannot run each other's
recipes, and each is the wrong machine on the other's world — which is what a
Core variant should mean.

---

# 3. Visual Design

## 3.1 Design Concept

A shaft with a hammer at the top of it. The building is mostly **empty vertical
space**: a heavy frame, a lifting carriage that climbs it, and a hardened anvil
bed at the bottom where the ore lands.

**The anti-read is a jaw crusher.** No opposed plates, no visible gnashing, no
conveyor gullet. Everything about this machine is vertical and it should look
like it works in one direction only: down.

## 3.2 Key Visual Features

* A **four-post frame**, tall relative to the footprint, open on all sides so the
  drop is visible.
* A **lifting carriage** — a dark mass that climbs the posts and releases.
* An **anvil bed** at the base, scarred and pale where it has been struck.
* Two **discharge chutes** at the base, deliberately different sizes: coarse to
  one side, fines to the other.

### Signature Feature

**The two chutes.** They are the recipe made visible — one building, two output
streams — and they are what the player will look for when they are trying to
remember which machine splits the ore.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Frame and posts | `#4A463F` → `#6E685C` | the structure |
| Lifting carriage | `#2E2C29` | the falling mass |
| Anvil bed | `#9A948A` | struck surface, palest thing on the machine |
| Hazard banding | `#C8A23A` | the drop zone's floor edge only |
| Ore and fines | `#7A6A55` / `#A89A82` | the two chutes, coarse and fine |

**No glow.** Nothing here is hot. The one bright note is the anvil, and it is
bright because it is polished by impact.

---

# 4. Factorio Visual Style

3×3 but tall, so the tall-building clause applies: the frame leans slightly away
from the camera and the shadow needs its own canvas (Appendix C). Style reference
to attach: the **crusher**, cropped and upscaled, with the standing disclaimer
that it is a reference for material and finish, not for shape — this machine's
shape is its argument.

---

# 5. Building Orientation

* [x] North only

**Direction count:** `1`. A vertical drop looks the same from every side, and the
chutes accept inserters from any tile.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Ore in | any adjacent tile | inserters, unconstrained |
| Crushed / fines out | any adjacent tile | two products, one output inventory |
| Electric | no visible connector | poles reach it wirelessly |
| Fluids | none | no fluid box anywhere; no pipe flange in the art |

The chutes are **honest decoration** in the way a vanilla furnace's hopper is:
they tell the player where the two streams conceptually go without constraining
where an inserter may stand.

---

# 11. Generation Requirements

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio Space
Age industrial machine, every panel drawn from the game's characteristic
45-degree top-down perspective. The machine is a tall open three-by-three drop
crusher standing on an airless metallic world. Four heavy vertical posts form an
open frame. A dark heavy lifting carriage rides the posts. A pale scarred anvil
bed sits at the base. Two discharge chutes leave the base at different sizes, one
coarse and one fine. Dark grey-brown armour, charcoal carriage, pale grey struck
anvil, small yellow hazard banding on the floor edge only. Grey-brown ore dust.
No opposed jaw plates, no gnashing mechanism, no glow, no flame, no smoke.
Panels: main view, front elevation, side elevation, a detail of the anvil bed and
the two chutes, and the carriage shown raised and dropped.
```

---

# 15. Factorio Prototype — sketch

```lua
{
  type = "assembling-machine",
  name = "sae-drop-crusher",
  crafting_categories = { "sae-crushing" },
  crafting_speed = 1,
  energy_usage = "200kW",
  energy_source = { type = "electric", usage_priority = "secondary-input" },
  surface_conditions = { { property = "gravity", min = 45 } },
  module_slots = 2
}
```

---

# 16. Icon

The carriage mid-fall between two posts, with the anvil beneath. Must read at
32 px as *"something heavy dropping"* — the two chutes are too fine to survive at
that size and should not be attempted.

---

# 20. Open questions

- **One recipe or two?** The brief assumes one recipe with two products. An
  alternative is two recipes — a coarse crush and a fine grind — letting the
  player choose the ratio. That is a branch rather than a formality and would
  suit `06-core-production-tree.md`'s own rule that every tier must branch, loop
  or converge. Worth deciding before the art is commissioned, since it changes
  whether the two chutes are simultaneous or alternate.
- **Do the fines have a home yet?** They feed the carbonyl line (T3), which does
  not exist. Until it does, fines are a dead-end item and the split is
  cosmetic — so either land T3 alongside this, or give fines a stopgap use.


---

# 19. Design Notes / Iteration History

### Version 1 — `concept/v1-sheet.png`

Layout, panel set and silhouette right first time. Attaching a vanilla crusher
frame as a style reference and an approved sheet from another building as a
format example did the work Appendix B says they do: the panel structure, the
labelled information table and the colour-swatch row all arrived without being
described.

Four things were wrong, all of them in the machine rather than the sheet:

1. **Copper hydraulic pipes and cables all over the frame**, and copper in the
   palette. §8 says this building has **no fluid box and no pipe flange
   anywhere** — the art was promising a connection the prototype does not have.
2. **The carriage read as a detailed equipment box** with panel lines, bolts and
   a hatch. §3.2 asks for an unadorned slab: it is a dead weight, not a machine.
3. **Too squat.** §4 invokes the tall-building clause and the drop distance is
   the mechanic; the posts were barely taller than the base.
4. **Raised and dropped were nearly identical** in the key frames, so the
   signature stroke did not read.

### Version 2 — `concept/v2-sheet.png` — **approved, design locked**

All four fixes took, in one round, written to Appendix A's shape: keep-list
first, then numbered fixes each naming what it currently reads as and what it
must read as.

- Every pipe, hose and cable gone; copper gone from the palette; the breakdown
  row's **PIPES & DETAIL** layer replaced with **GUIDE RAILS**.
- The carriage is now a plain near-black block, `#1F1F1F`, darker than anything
  else on the machine and labelled *"plain weight block"*.
- The posts are roughly twice the base height. It reads as tall, and the drop
  reads as long.
- Raised sits at the top of the posts, dropped sits hard on the bed.

Verified new rather than re-encoded by byte size (2,091,348 against v1's
2,187,107) and by `ImageChops.difference`, per Appendix B.

**Palette as drawn**, which supersedes §3.3's first guess:

| Role | Sheet | §3.3 asked for | Note |
| ---- | ----- | -------------- | ---- |
| Dark metal | `#3B3A36` | `#4A463F` | Slightly darker; in family |
| Secondary metal | `#5E5B55` | `#6E685C` | Slightly darker; in family |
| Anvil stone | `#B7B6AF` | `#9A948A` | **Lighter, and better** — §3.3 wants it the palest thing on the machine |
| Carriage block | `#1F1F1F` | `#2E2C29` | **Darker, and better** — §3.2 wants it darker than everything |
| Hazard yellow | `#D1A620` | `#C8A23A` | Effectively the same |
| Dust grey | `#787B71` | `#7A6A55` | Greyer than the brown asked for; left alone at concept stage, since Appendix C measures colour off the plate rather than eyeballing the sheet |

**One thing settled by the art, for §5 and the plate stage:** the canonical view
draws the carriage **raised**, so the idle plate is the raised position and the
drop is the working animation. That is the right way round — a machine at rest
should be holding its weight up, not sitting on its own anvil.

**Still open, and unchanged:** §20's two questions. One recipe or two, and
whether the fines have a consumer yet.
