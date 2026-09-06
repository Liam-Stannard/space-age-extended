# Factorio Building — Art & Implementation Specification

**Ignition Ring Mast.** First draft — a brief, enough to commission and judge a
concept sheet. Not a specification: §6, §12 and §13 stay open until a sheet is
approved and a canonical plate has been measured.

**This building carries a mechanic, not just a job.** It is how helium-3 comes to
throttle the endgame without the Ignition Array needing a fluid box — the
problem H4 was raised to solve and could not, since no vanilla rocket silo has
one and the launch UI's behaviour with a fluid ingredient is unknown. The ring
mast routes around it entirely: the mast takes the fluid, and the Array takes the
mast's output as an item.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | not started |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3, **and against the Arc Mast** | blocked on 0 |
| 2 | Idle plate (unlit) | portrait 2:3 | Same machine, unenergised | blocked on 1 |
| 4 | Charge glow sheet | portrait 2:3 | Differenced against stage 2 | blocked on 2 |
| 6 | Icon | square | Legible at 32 px, and not confusable with the Arc Mast's | blocked on 1 |

---

# 1. Building Overview

**Building Name:** `Ignition Ring Mast`
**Internal Prototype Name:** `sae-ring-mast`

**Building Type:** `assembling-machine` with a `fixed_recipe`. It is a mast in
fiction and a machine in the engine, and the spec should not pretend otherwise.

**Purpose:** Charges **ignition charge** from helium-3 and a great deal of
electricity. The Field Coil Segment recipe — the Ignition Array's `fixed_recipe`
— consumes one, so no segment is ever built without a ring of these running.

**Why it matters:** it makes the last hour of the mod a **site** rather than a
building. Vanilla's rocket silo is a thing you place; the Array becomes a thing
you *lay out*, surrounded by masts that have to be close enough to deliver.

**Locale:** *"Stands in the ring and holds the charge until the Array asks for
it."* / *"Helium-3 and a great deal of current, held for a few seconds at a time.
It has to stand close: what it makes does not travel."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 3×3 (`collision_box {-1.4,-1.4},{1.4,1.4}`) |
| Directions | 1 |
| Crafting category | `sae-ignition-charge` — its own |
| `fixed_recipe` | `sae-ignition-charge` |
| Energy | **12 MW.** It is meant to hurt |
| Surface conditions | `pressure` 1–9 — the Core alone, as the Array is |
| Module slots | 0, `allowed_effects = {}` |
| Fluid boxes | 1 in (helium-3) |

**The recipe, first pass:** 25 helium-3 + 12 MW for 4 s → 1 ignition charge.

### The ring is geometry, not a rule

Nothing in the engine can require a building to be *near* another one. The mast
does it with a timer instead: **ignition charge carries a very short
`spoil_ticks`** — on the order of ten seconds — and no `spoil_result`, so it
simply ceases to exist. Belt travel is real time, so a mast more than a few
seconds of belt from the Array delivers nothing.

That is the whole mechanic, and it is pure data. It reuses the engine's spoilage
timer, which the mod already leans on three times, and it needs no control-stage
script.

### Why it is not a reskin of the Arc Mast

They are opposites and the art has to say so. The Arc Mast **catches** something
episodic and banks it; this **spends** something continuously and cannot store it
at all. One is a receiver with a cage at the top; this is an emitter with its
mass at the bottom. If a player ever confuses the two silhouettes at a glance,
this design has failed — see §3.1's anti-read, which is unusually specific for
that reason.

---

# 3. Visual Design

## 3.1 Design Concept

A charged post, braced against its own discharge. Low and wide at the base,
tapering to a short capped emitter — the inverse of the Arc Mast's tall open cage
on a narrow leg.

**The anti-read is the Arc Mast**, and it is the most important line in this
brief. No cage. No open electrode. No upward-reaching structure. Nothing at the
top that looks like it wants to be struck. This machine's business is at its
waist, where the helium enters, and its top is closed.

## 3.2 Key Visual Features

* A **wide braced base** — four heavy buttresses, obviously resisting something.
* A **charge band** at waist height: a thick ring of banded coils around the
  shaft, the widest part of the machine.
* A **short capped emitter** at the top, closed and blunt.
* A **helium inlet** entering the charge band horizontally, frost-jacketed.

### Signature Feature

**The charge band pulses and the emitter does not.** Light climbs the band, holds,
and dies, over the four-second craft. The top stays dark throughout — which is the
single clearest way to say *this is not the thing lightning hits*.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Base and buttresses | `#4A463F` → `#6E685C` | the mass of the building |
| Charge band coils | `#8A5A32` → `#C88A4A` | waist only |
| Emitter cap | `#3B3B40` | the closed top |
| Charge light | `#F0E0A8` → `#FFF8E0` | inside the band only |
| Helium inlet frost | `#BFD8E8` | the inlet, small |

**Warm white, not violet and not green.** Violet belongs to the Coil Separator's
field and green to the radiant family; the Array's own firing is the only other
warm-white light in the mod, and these two *should* look related.

---

# 4. Factorio Visual Style

3×3 and tall, so the tall-building clause applies: it leans slightly away from
the camera and its shadow needs its own canvas (Appendix C). Style reference to
attach: the **Ignition Array's own approved deck plate**, so the ring and the
thing it rings read as one installation.

---

# 5. Building Orientation

* [x] North only

**Direction count:** `1`. A ring of masts around a silo will be placed at every
angle, and a machine with a visible "front" would look wrong in three quarters of
those positions. Radial symmetry is the requirement, not a simplification.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Helium-3 in | the charge band, one face | modelled flange, `pipe_picture` emptied |
| Ignition charge out | any adjacent tile | inserters, unconstrained |
| Electric | no visible connector | poles reach it wirelessly |

The building is radially symmetric but its fluid box is not, so the inlet flange
is the one asymmetry in the plate. It has to be drawn at exactly the tile the
fluid box names.

---

# 11. Generation Requirements

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio Space
Age industrial machine, every panel drawn from the game's characteristic
45-degree top-down perspective. The machine is a tall radially symmetric
three-by-three charging post standing on an airless metallic world. Four heavy
buttresses splay from a wide base. At waist height a thick banded ring of
copper-brown coils forms the widest part of the machine. Above it the shaft
tapers to a short blunt closed charcoal cap. A small frost-jacketed pale-blue
pipe enters the coil band horizontally. Warm white light glows from inside the
coil band only; the top of the machine is completely dark. Dark grey-brown
armour. No cage, no open electrode, no lightning rod, no upward-reaching mast, no
antenna, no arcs, no smoke, no flame. Panels: main view, front elevation, side
elevation, a detail of the coil band and its frosted inlet, and the band shown
unlit and fully charged.
```

---

# 15. Factorio Prototype — sketch

```lua
{
  type = "assembling-machine",
  name = "sae-ring-mast",
  crafting_categories = { "sae-ignition-charge" },
  fixed_recipe = "sae-ignition-charge",
  crafting_speed = 1,
  energy_usage = "12MW",
  energy_source = { type = "electric", usage_priority = "secondary-input" },
  surface_conditions = { { property = "pressure", min = 1, max = 9 } },
  module_slots = 0,
  allowed_effects = {},
  fluid_boxes = { --[[ 1 in, helium-3; see §8 ]] }
}
```

And the item that makes the ring a ring:

```lua
{
  type = "item",
  name = "sae-ignition-charge",
  stack_size = 10,
  spoil_ticks = 60 * 10   -- ten seconds; no spoil_result, so it simply goes
}
```

---

# 16. Icon

The coil band seen square on, glowing, with the blunt cap above and the buttressed
base below. Must read at 32 px as *"a charged collar"* — and must be
distinguishable from the Arc Mast's icon at that size, which is the harder
requirement.

---

# 20. Open questions

- **Does spoilage tick inside a rocket silo's input inventory?** The mechanic
  depends on it *not* mattering — the Array should consume charges promptly — but
  if charges rot in the silo faster than segments are built, the Array will jam on
  an ingredient that keeps vanishing. **This is the spike to run before anything
  is drawn.** It is cheap: one silo, one spoiling item, watch the slot.
- **What happens to a part-built segment when the charge is gone?** Vanilla holds
  ingredients in the crafting machine mid-craft. If a charge spoils *during* the
  8-second segment craft, the craft may fail and lose the coil assembly with it —
  which would be an appalling way to lose an hour of production. Either the charge
  must outlive the craft comfortably, or the segment recipe needs its time cut.
- **How many masts, and does the number matter?** The brief makes throughput the
  only constraint, so the "ring" is however many masts keep up. If the ring should
  be a *specific* shape, that needs a different mechanic and probably a script —
  and would be worth its own entry in `design/ideas.md` rather than being smuggled
  in here.
- **It is blocked behind I1.** If radiation ever replaces the arc storms, this
  building's whole visual argument — *"the mast that is not the other mast"* —
  loses its counterpart, and §3.1 would need rewriting rather than reusing.
