# Factorio Building — Art & Implementation Specification

**Vacuum Furnace.** First draft — a brief, enough to commission and judge a
concept sheet. Not a specification: §6, §12 and §13 stay open until a sheet is
approved and a canonical plate has been measured.

**This building has to justify itself harder than the others in the set,**
because "a furnace, but sealed" is a reskin of the electric furnace unless it is
given work nothing else can do. §2 is where that happens; if the exclusive work
is ever removed, delete the building rather than shipping it.

**Settled 2026-09-06: it stays a `furnace`, and phosphide flux becomes a fluid.**
Spike S12 proved a furnace can auto-select on one item plus one fluid, so
sintering keeps its flux without costing the machine its defining trick. The
consequence outside this document is that `06-core-production-tree.md` T2's flux
is a fluid now — piped, never belted or chested.

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
| Fluid boxes | 1 in — **phosphide flux**, used by the sintering recipes only |
| Energy | 1.2 MW, electric |
| Surface conditions | `pressure` ≤ 9 — the Core and platforms |
| Module slots | 2 |

**The flux box wants a generous volume.** S12 found that a furnace with a fluid
ingredient refuses its *solid* ingredient outright until the fluid is already in
the machine. A large buffer against a small per-craft draw makes that latch rare
after first build; it does not remove it, and §3.2's status lamp is what makes it
legible when it happens.

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
* A **sight port**, small and thick, the only place any *heat* glow escapes.
* A **fault lamp** on the hatch rim — a small neutral-white lens the engine
  tints. See below; it is drawn white and coloured at runtime, never painted.
* A **flux inlet** on one flank, frost-jacketed, small.

### Signature Feature

**The sight port.** One small deep-set circle of orange in an otherwise cold dark
building. It is how the player tells a running furnace from an idle one at a
glance, and it is the entire *heat* lighting budget.

### The fault lamp — and the problem it exists to solve

S12's latch is invisible without it. A furnace with no flux **refuses to accept
powder at all**, so its input slot stays empty and the fault reads as an upstream
belt problem rather than a machine problem — the player stares at a healthy-looking
furnace that inserters will not load.

The engine solves this directly, and vanilla proves the pattern on the electric
mining drill (`base/prototypes/entity/mining-drill.lua:161` and `179`): a
`working_visualisation` with `apply_tint = "status"` and **`always_draw = true`**,
plus `status_colors` on the graphics set. The lamp is drawn once, in white, and
the engine colours it per machine status.

**The lamp is a *fault* lamp, not a status lamp**, and that is what keeps §3.2's
"one lit state" honest:

| Status | Colour | Reads as |
| ------ | ------ | -------- |
| `working` | **clear** — invisible | The sight port already says this |
| `insufficient_input` | amber | **The latch.** No flux, or no powder |
| `full_output` | pale blue | Nothing is taking the preforms |
| `idle`, `disabled` | dim grey | Off, on purpose |
| `no_power`, `low_power` | clear / amber | The grid, not the machine |

So the building has exactly one lit state when it is well — the orange port — and
lights a second, differently coloured, differently placed lamp only when something
is wrong. `always_draw = true` is **mandatory**: vanilla's own comment says the
non-working states will not draw without it.

**The lamp sprite is not concept-art work.** It is a small white lens drawn once,
at 32 px, `draw_as_glow`. It should be on the *hatch rim* rather than beside the
sight port, so the two lights are never confused at a glance.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Drum body | `#3E3B36` → `#5E584E` | the mass; darker than the mod's usual chassis |
| Hatch and dogs | `#8A8580` | roof only |
| Radiator loops | `#6E685C` | two flanks |
| Sight port glow | `#E8A24A` → `#FFD9A0` | the port, and nothing else |
| Fault lamp lens | `#FFFFFF` | hatch rim — **painted white, tinted by the engine** |
| Flux inlet frost | `#BFD8E8` | one flank, small |
| Weld seams | `#7A7268` | fine lines on the drum |

**The heat-glow budget is one circle.** If orange appears anywhere else on this
building the seal is a lie — and the fault lamp is not an exception to that, since
it is painted white and only the engine ever makes it amber.

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
| Phosphide flux in | one flank, modelled flange | `pipe_picture` emptied, foundry pattern |
| Electric | no visible connector | poles reach it wirelessly |

**A furnace with one input slot cannot be fed a mixed belt safely.** Nothing in
the prototype prevents it, but a player who feeds fines and ore onto one belt
will watch the machine flip recipes. That is vanilla smelting's own behaviour and
needs no fix, but the locale should not encourage it.

**Smelting takes no flux; sintering does.** So the same machine runs with its
pipe connected or not, depending on which job it is doing — and the flange has to
look unremarkable when nothing is plumbed to it.

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
  module_slots = 2,
  fluid_boxes = { --[[ 1 in, phosphide flux, generous volume; see §2 ]] },
  graphics_set =
  {
    status_colors =
    {
      working            = { 0, 0, 0, 0 },        -- the sight port says this
      insufficient_input = { 1, 0.65, 0.15, 1 },  -- the latch
      full_output        = { 0.4, 0.7, 1, 1 },
      idle               = { 0.3, 0.3, 0.35, 1 },
      disabled           = { 0.3, 0.3, 0.35, 1 },
      no_power           = { 0, 0, 0, 0 }
    },
    working_visualisations =
    {
      { --[[ the sight port glow, working only ]] },
      {
        apply_tint = "status",
        always_draw = true,      -- mandatory, or the fault states never draw
        animation = { --[[ the white lens, 32px, draw_as_glow ]] }
      }
    }
  }
}
```

**Verified at the data stage (S13):** the engine loads and retains both
`status_colors` and `apply_tint = "status"` on a `furnace`, not only on the mining
drills vanilla uses them on.

---

# 16. Icon

The drum seen slightly from above, hatch on top, one orange sight port. Must read
at 32 px as *"a sealed pot"*. The weld seams and radiator loops will not survive
and should not be attempted.

---

# 20. Decisions and open questions

**Settled: it stays a `furnace`, and phosphide flux becomes a fluid.** S12 proved
the item-plus-fluid selection path; §2 and §8 are written to it. The knock-on is
in `06-core-production-tree.md` T2, where flux stops being an item.

**Settled: the latch gets a fault lamp**, not a redesign — §3.2. The engine's
`apply_tint = "status"` does it, vanilla does it on the drills, and S13 confirmed
a furnace loads it.

- **Does it also take `sae-degassing` or `sae-crushing`?** No, and it should not
  be allowed to drift that way. A furnace that accumulates categories becomes the
  one machine that does everything, and the point of the Core's buildings is that
  each says something.
- **The lamp is proven to load, not proven to render.** S13 read it back out of
  the data dump; whether the renderer applies the tint on a furnace as it does on
  a drill needs eyes on a client. It is the cheapest possible check — build one,
  cut its flux, look at it — and it should happen the first time anyone plays this
  building rather than being spiked on its own.
- **Flux as a fluid costs the player a storage option.** It can no longer be
  belted or chested, only piped and tanked. That is the price of keeping
  auto-selection, and it is worth re-examining if the sintering line ever turns
  out to want flux in more than two or three places.
- ~~**Furnace recipe selection needs one item ingredient**~~ — **spiked (S12),
  and the furnace path is viable.** A furnace *does* accept `fluid_boxes` and
  *does* auto-select from one item plus one fluid, disambiguating correctly by the
  item: powder-a made preform-a, powder-b made preform-b, from the same shared
  fluid.

  **The decision this leaves is about phosphide flux, not about this building.**

  | Option | What it costs | Status |
  | ------ | ------------- | ------ |
  | **Furnace, flux becomes a fluid** | T2's flux recipe changes; flux can no longer be belted or chested, only piped | Proven in S12 |
  | **Assembling machine, flux stays an item** | Loses auto-selection; the player sets a recipe per machine | Proven a thousand times over |

  Leaning furnace: auto-selection is worth real money on a machine meant to handle
  several powders, a molten flux is not a strange thing for something whose job is
  to wet a powder, and piping it adds a routing problem to a line that is otherwise
  all belts.

- **If it stays a furnace, §3 must account for S12's ordering catch.** A furnace
  with a fluid ingredient **will not accept its solid until the fluid is already
  in the machine** — `insert` returns 0 with the fluid box empty, and 5 with it
  full. A vanilla furnace accepts a new item unconditionally, so this is specific
  to the fluid path. Two consequences: on first build the player must pipe before
  they belt, and a dry flux line plus an empty input latches the machine shut until
  flux returns. It self-heals, and it is invisible while it is happening.

  That argues for the **sight port being visible even when idle-but-blocked**, so a
  latched machine does not read as a working one. Worth settling before the glow
  plate is drawn, since §3.2 currently gives the building exactly one lit state.
