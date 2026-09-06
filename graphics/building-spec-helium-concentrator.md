# Factorio Building — Art & Implementation Specification

**Helium Concentrator.** First draft — a brief, enough to commission and judge a
concept sheet, in the manner of the four specs that began that way. It is **not**
a specification: §6, §12 and §13 stay open until a sheet is approved and a
canonical plate has been measured.

**Agreed, unbuilt.** The building is approved; the recipe economy under it is
not settled — see §20, which is load-bearing for this one more than for any
other building in the set.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **draft — `concept/v1-sheet.png`**, not locked |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3 | blocked on 0 |
| 2 | Idle plate (unlit) | portrait 2:3 | Same machine, nothing lit | blocked on 1 |
| 4 | Glow plate | portrait 2:3 | Differenced against stage 2 | blocked on 2 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

### Where generation happens

Browser — ChatGPT's image tool. Template Appendices B and C apply in full.

---

# 1. Building Overview

**Building Name:** `Helium Concentrator`
**Internal Prototype Name:** `sae-helium-concentrator`

**Building Type:** `assembling-machine`, built fresh rather than deep-copied.
Its fluid box count is the reason: one fluid in and two out, which no vanilla
assembler carries.

**Purpose:** Strips primordial helium-3 out of molten kamacite. The gas has been
trapped in the interior since the planet formed, so the melt carries it — and
that gives the Core a second, expensive helium source that is **paid for in
melt** rather than found on the map.

**Why it matters:** it turns the melt's two-way split into a three-way one.
Metal, power, or gas: every casting decision now also competes with the rarest
resource on the planet, and the vents stop being the only answer to a helium
shortage.

**Locale:** *"Pulls the planet's oldest gas out of its newest metal."* /
*"Molten kamacite still holds the helium it trapped when the world formed.
Boiling it out costs melt that would have been metal — which is the trade."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 3×3 (`collision_box {-1.4,-1.4},{1.4,1.4}`) |
| Directions | 1 (no rotation; fluid boxes on fixed faces) |
| Crafting category | `sae-degassing` — its own, so nothing else can run the recipe |
| Energy | **Heavy: 1.5 MW.** The cost of the trade is electricity |
| Surface conditions | `pressure` ≤ 9 — the Core and platforms |
| Module slots | 3, all effects allowed |
| Fluid boxes | 1 in (molten kamacite), 2 out (helium-3, settled melt) |

**The recipe, first pass:** 100 molten kamacite → 10 helium-3 + 40 settled melt,
20 s. Deliberately worse than gravity settling at making melt *and* far worse
than a gas vent at making helium. It is the bad trade you take when one of the
two is the thing you have run out of.

### Why it is not a reskin

Nothing in vanilla converts one resource into a scarcer one at a punitive rate.
The chemical plant is the closest shape and it is a straight conversion; this is
a **relief valve on a hard cap**, and the whole design of the Core rests on that
cap (`decisions.md` D12).

---

# 3. Visual Design

## 3.1 Design Concept

A cold machine wrapped around a hot pipe. Molten kamacite enters at the base,
and the building's entire mass exists to hold it still long enough for gas to
come out of solution: a tall, ribbed separation drum with a narrow gas riser
climbing one side and a heavy return line leaving at the bottom.

**The anti-read is a distillation column.** This is not a refinery tower and must
not borrow one's silhouette — no fractionating trays, no ladder cage running the
full height, no flare. It is squat and dense, because it stands on the heaviest
world in the game.

## 3.2 Key Visual Features

* A **separation drum** two thirds of the height, ribbed horizontally.
* A **gas riser** — a slim, pale, frost-jacketed pipe climbing one flank and
  leaving at the top. It is the only cold thing on the building.
* A **melt return** — a heavy, dark, insulated line leaving low on the opposite
  flank.
* **Frost** where the riser meets the drum, and nowhere else.

### Signature Feature

**The temperature split, read in one glance:** orange at the bottom, frost at the
top, and a hard line between them at the drum's waist. A player should be able to
tell what this machine does without reading its name.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Drum body | `#4A463F` → `#6E685C` | the mass of the building |
| Melt lines and base | `#7A4A28` → `#C86A2E` | lower third only |
| Gas riser and frost | `#BFD8E8` → `#EAF4FA` | riser and drum waist |
| Shielding collars | `#3B3B40` | clamps at both ports |

The pale blue is the helium-3 fluid icon's own hue. **No green anywhere** —
green is radiant fuel's family, and this gas is not that.

---

# 4. Factorio Visual Style

3×3 and mid-height, so the camera shows roof, a shallow near face and one flank.
Name the camera exactly — *"the game's characteristic 45-degree top-down
perspective"*. Style reference to attach: the **chemical plant**, cropped and
upscaled, with the standing disclaimer.

---

# 5. Building Orientation

* [x] North only

**Direction count:** `1`. The fluid boxes name fixed faces, so the building never
rotates. One plate, one glow sheet.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Molten kamacite in | south face, centre | modelled flange, `pipe_picture` emptied |
| Helium-3 out | north face, high | the riser's own outlet |
| Settled melt out | west face, low | the heavy return |
| Electric | no visible connector | poles reach it wirelessly |

Follow the foundry's pattern: `pipe_picture = util.empty_sprite()`,
`always_draw_covers = false`, and the flange drawn into the building's own plate
at exactly the tile each fluid box names. Three ports on three different faces is
the geometry to get right at concept stage, not later.

---

# 11. Generation Requirements

**Canvas:** portrait 2:3 for plates, landscape 3:2 for the sheet.

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio Space
Age building, every panel drawn from the game's characteristic 45-degree
top-down perspective. The building is a squat three-by-three industrial gas
separator standing on an airless metallic world. A heavy ribbed separation drum
fills most of the height. A slim frost-jacketed pale-blue gas riser climbs the
left flank and exits at the top. A dark insulated melt return line leaves low on
the right. Hot orange metal glows in the lower third only; pale frost-blue
appears only at the drum's waist and on the riser. Dark grey-brown armour,
charcoal shielding collars. No smoke, no flame, no fractionating tower, no
ladder cage. Panels: main view, front elevation, side elevation, a detail of the
riser-to-drum junction, and a lit/unlit pair.
```

---

# 15. Factorio Prototype — sketch

```lua
{
  type = "assembling-machine",
  name = "sae-helium-concentrator",
  crafting_categories = { "sae-degassing" },
  crafting_speed = 1,
  energy_usage = "1500kW",
  energy_source = { type = "electric", usage_priority = "secondary-input" },
  surface_conditions = { { property = "pressure", max = 9 } },
  module_slots = 3,
  fluid_boxes = { --[[ 1 in, 2 out; see §8 for faces ]] }
}
```

---

# 16. Icon

The drum in silhouette with the frost line across its waist and one pale bubble
rising. Must read at 32 px as *"gas coming off metal"*, not as a tank.

---

# 20. Decisions and open questions

**Settled: helium-3 is a price, not a cap** — `decisions.md` R8. The concentrator
exists, and D12's hard wall becomes an exchange rate. The three options this
section previously offered are closed; option 3 was taken.

**The price is denominated in power, not melt.** That is the load-bearing half of
the decision. Electricity is already the Core's central competition — every
megawatt the Array draws is melt that was not cast — so a helium shortage now
resolves into a power decision rather than a new one. Tune `energy_usage` first
and the melt ratio second.

Still open, and all of it is tuning rather than design:

- **How expensive, in watts.** The 1.5 MW in §2 is a first guess and it is the
  single most important number on this building. Too cheap and gas-vent siting
  stops mattering from the first hour; too dear and the relief valve is decorative.
- **When it unlocks.** Late. R8's mitigation for the lost constraint is unlock
  order, not arithmetic: the hard cap has to have taught its lesson before the way
  around it is offered. Tier 3 of the ladder at the earliest, and it should not be
  in the foothold tier under any circumstances.
- **Whether the melt output is worth having at all.** §2 returns 40 settled melt
  alongside the gas. If that makes the concentrator a competitive *melt* source as
  well, it is doing two jobs and should lose one — drop the melt return to dross,
  or to nothing.
- **Does it need a surface condition at all?** `pressure ≤ 9` is written in §2 out
  of habit. Molten kamacite is unbarrelable and exists nowhere else, so the recipe
  is already Core-locked by its ingredient. The condition is harmless but it is
  not doing any work, and `01-principles.md` is clear that manufacture alone is
  never a crossing.
