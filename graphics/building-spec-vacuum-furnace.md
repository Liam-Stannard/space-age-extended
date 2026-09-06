# Factorio Building — Art & Implementation Specification

**Vacuum Furnace.** First draft — a brief, enough to commission and judge a
concept sheet. Not a specification: §6, §12 and §13 stay open until a sheet is
approved and a canonical plate has been measured.

**This building has to justify itself harder than the others in the set,**
because "a furnace, but sealed" is a reskin of the electric furnace unless it is
given work nothing else can do. §2 is where that happens; if the exclusive work
is ever removed, delete the building rather than shipping it.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | not started |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3 | blocked on 0 |
| 2 | Idle plate (unlit) | portrait 2:3 | Same machine, cold | blocked on 1 |
| 4 | Glow plate | portrait 2:3 | Differenced against stage 2 | blocked on 2 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

---

# 1. Building Overview

**Building Name:** `Vacuum Furnace`
**Internal Prototype Name:** `sae-vacuum-furnace`

**Building Type:** `furnace`. Deliberately not an assembling machine: a furnace
**chooses its recipe from what is inserted**
(`auxiliary/furnace-recipe-selection.html`), so one building serves the whole
smelting and sintering line without the player setting a recipe on each.

**Purpose:** The Core's only smelter, and the only machine in the game that can
process **kamacite fines**. An open furnace loses powder; a sealed one does not,
and on a world with no atmosphere sealing is free.

**Why it matters:** it is the one place the pressure-5 rule pays the player back
instead of taking something away. Everywhere else, vacuum is a list of buildings
that are refused. Here it is the reason a whole material stream exists.

**Locale:** *"Nothing escapes a furnace with no air in it."* / *"Smelts what an
open furnace would lose. On a world with no atmosphere, a sealed crucible costs
nothing to seal."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 3×3 (`collision_box {-1.4,-1.4},{1.4,1.4}`) |
| Directions | 1 |
| Crafting categories | `smelting` **and** `sae-sintering` |
| `source_inventory_size` | 1 (the prototype maximum) |
| Energy | 1.2 MW, electric |
| Surface conditions | `pressure` ≤ 9 — the Core and platforms |
| Module slots | 2 |

### The exclusive work — the reason it exists

1. **Kamacite fines.** The Drop Crusher's second stream can only be smelted here.
   Nothing else in the game accepts the item.
2. **Sintering.** Carbonyl powder pressed into a sintered preform is a
   `sae-sintering` recipe, and this is the only machine carrying that category.

Both are powder processes, and both are impossible in an open furnace for the
same real reason. That is one argument doing two jobs, which is what makes it an
argument rather than an excuse.

### Why it is not a reskin

The electric furnace can be carried here and will smelt plate perfectly well.
This building does not replace it — it does the two things the electric furnace
**cannot**, and picks its own recipe while doing them. If a player never builds
one, they never see the fines line or the carbonyl line, and both are tiers of
the production tree.

---

# 3. Visual Design

## 3.1 Design Concept

A pressure vessel that is holding nothing in. The read is **sealed** — a squat
welded drum with no door, no chimney, no visible fire, and a single heavy clamped
hatch on the roof that is the only way anything gets in or out.

**The anti-read is the electric furnace.** Vanilla's is an open-fronted box with
a visible glowing throat, and every part of that is wrong here: an open front on
a sealed machine is a contradiction the player will notice.

## 3.2 Key Visual Features

* A **welded drum** body, seams visible, deliberately without panel lines — it is
  one piece, because a seam is a leak.
* A **clamped roof hatch**, heavy, with radial dogs around its rim.
* **Radiator loops** on two flanks — the heat has nowhere to go but a radiator,
  since there is no air to carry it.
* A **sight port**, small and thick, the only place any glow escapes.

### Signature Feature

**The sight port.** One small deep-set circle of orange in an otherwise cold dark
building. It is how the player tells a running furnace from an idle one at a
glance, and it is the entire lighting budget.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Drum body | `#3E3B36` → `#5E584E` | the mass; darker than the mod's usual chassis |
| Hatch and dogs | `#8A8580` | roof only |
| Radiator loops | `#6E685C` | two flanks |
| Sight port glow | `#E8A24A` → `#FFD9A0` | the port, and nothing else |
| Weld seams | `#7A7268` | fine lines on the drum |

**The glow budget is one circle.** If orange appears anywhere else on this
building the seal is a lie.

---

# 4. Factorio Visual Style

3×3 and squat, so the camera shows a great deal of roof — which is why the hatch
is the roof's feature and has to carry the read from above. Style reference to
attach: the **foundry**, cropped and upscaled, for weight and finish. **Do not
attach the electric furnace**; it is the anti-read.

---

# 5. Building Orientation

* [x] North only

**Direction count:** `1`.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Item in | any adjacent tile | `source_inventory_size = 1` |
| Item out | any adjacent tile | `result_inventory_size = 1` |
| Electric | no visible connector | poles reach it wirelessly |
| Fluids | none | no fluid box; no pipe flange in the art |

**A furnace with one input slot cannot be fed a mixed belt safely.** Nothing in
the prototype prevents it, but a player who feeds fines and ore onto one belt
will watch the machine flip recipes. That is vanilla smelting's own behaviour and
needs no fix, but the locale should not encourage it.

---

# 11. Generation Requirements

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio Space
Age industrial furnace, every panel drawn from the game's characteristic
45-degree top-down perspective. The machine is a squat sealed three-by-three
welded drum standing on an airless metallic world. No door and no chimney. A
heavy clamped circular hatch with radial locking dogs sits on the roof. Radiator
loops run along two flanks. One small deep-set thick sight port glows warm
orange; no other part of the machine glows. Very dark grey-brown welded body with
fine visible weld seams, pale grey hatch and dogs. No open furnace mouth, no
flame, no smoke, no chimney, no visible fire. Panels: main view, top-down view
emphasising the roof hatch, side elevation, a detail of the hatch dogs and the
sight port, and a lit/unlit pair.
```

---

# 15. Factorio Prototype — sketch

```lua
{
  type = "furnace",
  name = "sae-vacuum-furnace",
  crafting_categories = { "smelting", "sae-sintering" },
  crafting_speed = 1,
  source_inventory_size = 1,
  result_inventory_size = 1,
  energy_usage = "1200kW",
  energy_source = { type = "electric", usage_priority = "secondary-input" },
  surface_conditions = { { property = "pressure", max = 9 } },
  module_slots = 2
}
```

---

# 16. Icon

The drum seen slightly from above, hatch on top, one orange sight port. Must read
at 32 px as *"a sealed pot"*. The weld seams and radiator loops will not survive
and should not be attempted.

---

# 20. Open questions

- **Does it also take `sae-degassing` or `sae-crushing`?** No, and it should not
  be allowed to drift that way. A furnace that accumulates categories becomes the
  one machine that does everything, and the point of the Core's buildings is that
  each says something.
- **Furnace recipe selection needs one item ingredient.** Any sintering recipe
  that wants powder *and* flux breaks auto-selection — it would have to be one
  item plus one fluid. If sintering genuinely needs two solids, this must become
  an assembling machine and the "picks its own recipe" argument is lost. **Settle
  the sintering recipe's shape before commissioning art.**
