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

## Technology tier and visual register

**Tier 3.** Advanced and quiet: cryogenic jacketing, smooth shells, machinery implied rather than shown. Gated late by §20, and should look it.

See the template's *"Technology tier sets the visual register"* — the player
should be able to read their progress off the factory floor without opening the
tech tree, so this building's surface treatment is set by where it sits on
`04-the-core.md` §6's ladder, not by taste.



3×3 and mid-height, so the camera shows roof, a shallow near face and one flank.
Name the camera exactly — *"the game's characteristic 45-degree top-down
perspective"*. Style reference to attach: the **chemical plant**, cropped and
upscaled, with the standing disclaimer.

---

# 5. Building Orientation

* [x] North only

**Direction count:** `1` — **a choice, not a constraint.** This machine has fluid
boxes, so the engine *would* let it rotate. It is fixed at one direction because
its three flanges are on three named faces (§8) and rotating it would move all
three at once, which is more confusion than convenience. Revisit if playtesting
shows people fighting the pipe runs.. The fluid boxes name fixed faces, so the building never
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
A single landscape concept-art and asset-breakdown sheet for one Factorio
Space Age building, every panel drawn from the game's characteristic 45-degree
top-down perspective. The building is a squat three-by-three industrial gas
separator standing on an airless metallic world. A heavy ribbed separation
drum fills most of the height. Exactly three pipe flanges meet the ground at
the edge of the footprint, one on each of three different sides: a wide dark
inlet flange on the near side, a slim frost-jacketed pale-blue gas flange on
the left, and a heavy insulated dark flange on the right. Each pipe runs from
the drum down to its flange and stops there. Hot orange metal glows in the
lower third of the drum only; pale frost-blue appears only at the drum's waist
and on the gas pipe. Dark grey-brown armour, charcoal shielding collars. No
smoke, no flame, no fractionating tower, no ladder cage. Panels: main view,
front elevation, side elevation, a top-down view showing all three ground
flanges at the footprint edge, and a lit/unlit pair. Title the sheet HELIUM
CONCENTRATOR. Draw no loose material anywhere: no ore, powder, fibre, grit,
debris or product on the ground, in bins, at chutes, on trays or spilling from
the machine. Factorio machines never show what they make, so every chute,
port, bin and tray is drawn as empty machinery. Every pipe connection must run
down to ground level and stop flush at the edge of the tile footprint; no pipe
may end in mid-air and none may leave the top of the building. Nothing may
extend past the tile footprint, pipework included, and the tile-grid panel
must show the whole machine inside the grid with no overhang.
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

---

# 13. Sprite Dimensions

**Measured off the shipped plates.**

| Plate | Canvas | Drawn content | Shift | Scale |
| ----- | ------ | ------------- | ----- | ----- |
| `base.png` | 200 × 201 | 192 × 193 → **3.000 × 3.016 tiles** | `{ 0, 0 }` | 0.5 |
| `base-shadow.png` | 355 × 212 | sheared off the plate's own alpha | `{ 1.21094, 0.08594 }` | 0.5 |
| `skirt-glow.png` | 200 × 201 | the hot vessel's skirt joints, differenced | `{ 0, 0 }` | 0.5 |

Centred to **0.0 px**, alpha `0` on all four edges of every plate, three in a row
claim **0 px twice**, `check-footprint.py --tiles 3` passes with 0.02 tiles of
height above the box.

### Compared against vanilla

| | tiles | aspect | luminance | edge density |
| --- | ---: | ---: | ---: | ---: |
| vanilla chemical plant | 3.188 × 4.563 | 1:1.43 | — | **0.164** |
| **ours** | **3.000 × 3.016** | **1:1.00** | 67 | **0.262** |

**The density problem the option page warned about is solved, and by more than
the target.** The concept sheet measured 0.108 — the least detailed of its round
— and the cut plate measures **0.262 against vanilla's chemical plant at
0.164**. One instruction did it: *more hardware, without changing the shapes.*
Gauge faces, jacket seams, ladder cleats, cable runs, valve blocks, bolt rings.

**The vanilla comparison also shows why the sheet number was misleading.** A
concept sheet is mostly charcoal page; a plate is all building.

---

# 21. What stage 1 found

**The prototype declared both outputs on the north face.** Its own §8 says
helium-3 leaves north on the riser and the settled melt leaves **west, low**, and
the adopted plate draws exactly that. Fixed, and verified against the engine's own
dump rather than the Lua: `input dir=8 (south)`, `output dir=0 (north)`,
`output dir=12 (west)` — three ports on three faces.

**All three fluid boxes now follow the foundry's pattern**: `pipe_picture`
emptied and `always_draw_covers = false`, because the flange belongs to the
building's own plate and a generic engine stub drawn over it is a second flange
in the wrong place. The Vacuum Furnace's box was given the same treatment in the
same pass.

**Three pipe stubs, drawn to mate.** The Crust Tap's three rounds bought a rule
and it was applied here first time: each connection ends in an open, full-diameter
pipe mouth at ground level, flush with the middle of its tile edge. The
pump-and-pipe reference went over with the prompt.
