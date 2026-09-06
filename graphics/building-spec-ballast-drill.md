# Factorio Building — Art & Implementation Specification

**Ballast Drill.** First draft — a brief, enough to commission and judge a
concept sheet. Not a specification: §6, §12 and §13 stay open until a sheet is
approved and a canonical plate has been measured.

Named for what makes it work rather than for where it stands: the Core's own
drill, but "Core Drill" reads as a drill *for* cores, and every other building
here already says Core in its description.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **draft — `concept/v1-sheet.png`**, not locked |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3 | blocked on 0 |
| 3 | Directional frames | portrait 2:3 | **Four are needed** — see §5 | blocked on 1 |
| 5 | Working animation | portrait 2:3 | Loops without a visible seam | blocked on 3 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

---

# 1. Building Overview

**Building Name:** `Ballast Drill`
**Internal Prototype Name:** `sae-ballast-drill`

**Building Type:** `mining-drill`, built fresh against vanilla's
`big-mining-drill` as the reference for proportions and for
`resource_drain_rate_percent`.

**Purpose:** Works kamacite ore **without wasting it.** Slower than an electric
mining drill and far hungrier for power, but it takes half as much out of the
patch for every ore it delivers.

**Why it matters:** kamacite patches *genuinely run out* (`decisions.md` D12) and
nothing else in the mod cares. This is the only building in the game whose
argument is "spend electricity to make a finite thing last", and on a planet
whose central tension is already electricity, that lands the trade in exactly the
right place.

**Locale:** *"Leans on the ore rather than tearing at it."* / *"Half the drain
for every ore delivered, at twice the power and two thirds the speed. The patch
is not coming back; the electricity is."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 5×5, matching the big mining drill |
| Directions | 4 |
| Resource categories | `basic-solid` |
| `mining_speed` | ~0.65 of the electric drill's, per ore |
| `resource_drain_rate_percent` | **50** — vanilla precedent: `big-mining-drill.lua:568` |
| Energy | 900 kW, electric, `secondary-input` |
| Surface conditions | `gravity` ≥ 45 — the Core alone |
| Module slots | 4 |

### Why it is not a reskin

`resource_drain_rate_percent` is the whole building. It is the one mining-drill
field that changes what a patch is *worth* rather than how fast it empties, and
vanilla uses it exactly once. Here it turns ore siting into a decision with a
cost attached, on the one planet where ore is finite by design.

**The gravity condition is the fiction and the balance in one line.** At 50 g the
drill can press down with its own mass instead of hammering, which is why it
wastes less — and it means the building cannot be carried to a world where ore is
effectively infinite and used as a straight upgrade.

---

# 3. Visual Design

## 3.1 Design Concept

A press, not a hammer. The machine's read is **weight brought to bear**: a broad
low chassis with a heavy ballast block riding above the cutting head, and legs
splayed wide enough that it is obviously bracing rather than standing.

**The anti-read is a derrick.** No tower, no headframe, no rotating superstructure.
Everything about this machine is low and wide, because its argument is mass.

## 3.2 Key Visual Features

* A **ballast block** — the tallest element, an unadorned slab of metal riding on
  four visible guide rails above the head.
* **Splayed bracing legs** at the four corners, each with a broad foot pad.
* A **cutting head** under the block, mostly hidden, seen only as a rim of
  disturbed ground.
* An **output boom** on one side, short and stubby.

### Signature Feature

**The ballast block descends and rises on the working loop** — a slow, heavy,
one-second stroke rather than a spin. It is the animation that says *this machine
is using gravity*, and it is the reason the building reads at a glance.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Chassis and legs | `#4A463F` → `#6E685C` | the mass of the building |
| Ballast block | `#2E2C29` | the slab, deliberately darker than everything |
| Guide rails | `#8A8580` | four verticals |
| Hazard banding | `#C8A23A` | leg feet only, sparingly |
| Ore dust | `#7A6A55` | ground disturbance under the head |

**No glow at all.** Nothing on this machine is hot or energised; it is a weight
on a rail. A drill that glows would read as a smelter.

---

# 4. Factorio Visual Style

## Technology tier and visual register

**Tier 0 — Foothold.** Crude and mechanical: bolted plate, cast legs, exposed guide rails, visible wear on the cutting head. A landing-day machine.

See the template's *"Technology tier sets the visual register"* — the player
should be able to read their progress off the factory floor without opening the
tech tree, so this building's surface treatment is set by where it sits on
`04-the-core.md` §6's ladder, not by taste.



5×5 and low, so the camera shows a great deal of roof and very little face — the
ballast block and the four rails carry the whole silhouette. Style reference to
attach: the **big mining drill**, cropped and upscaled, with the standing
disclaimer.

---

# 5. Building Orientation

* [x] North · [x] East · [x] South · [x] West

**Direction count:** `4`. The output boom points a different way in each, and a
drill whose boom does not match its belt is the single most confusing thing a
mining building can do.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Ore out | the boom tip, per `vector_to_place_result` | must match the art in all four directions |
| Electric | no visible connector | poles reach it wirelessly |
| Fluids | none | no `input_fluid_box`; this drill takes no reagent |

**`vector_to_place_result` is the one number that cannot be guessed.** It has to
be measured off each directional plate so the ore appears at the boom's tip and
not through the chassis.

---

# 11. Generation Requirements

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio
Space Age mining machine, every panel drawn from the game's characteristic
45-degree top-down perspective. The machine is a broad low wide five-by-five
ore press standing on an airless metallic world, much wider than it is tall.
Four splayed bracing legs with wide foot pads reach out to the corners. A
heavy dark unadorned ballast slab rides above the centre on four short pale
vertical guide rails. Directly beneath the slab, a toothed circular cutting
head is set into the ground and mostly hidden, with only its rim showing. A
short stubby empty output boom projects from one side. Dark grey-brown armour,
charcoal ballast, pale grey rails, small yellow hazard banding on the foot
pads only. No tower, no derrick, no headframe, no glow, no flame, no smoke.
Panels: main view, front elevation, side elevation, a detail of the cutting
head beneath the raised slab, and the slab shown at the top and bottom of its
stroke. Title the sheet BALLAST DRILL. Draw no loose material anywhere: no
ore, powder, fibre, grit, debris or product on the ground, in bins, at chutes,
on trays or spilling from the machine. Factorio machines never show what they
make, so every chute, port, bin and tray is drawn as empty machinery. Every
pipe connection must run down to ground level and stop flush at the edge of
the tile footprint; no pipe may end in mid-air and none may leave the top of
the building. Nothing may extend past the tile footprint, pipework included,
and the tile-grid panel must show the whole machine inside the grid with no
overhang.
```

---

# 15. Factorio Prototype — sketch

```lua
{
  type = "mining-drill",
  name = "sae-ballast-drill",
  resource_categories = { "basic-solid" },
  mining_speed = 0.65,
  resource_drain_rate_percent = 50,   -- big-mining-drill.lua:568 is the precedent
  energy_usage = "900kW",
  energy_source = { type = "electric", usage_priority = "secondary-input" },
  surface_conditions = { { property = "gravity", min = 45 } },
  module_slots = 4,
  vector_to_place_result = { --[[ measured per direction; see §8 ]] }
}
```

---

# 16. Icon

The ballast block on its rails, seen square on, with the cutting head as a dark
rim beneath. Must read at 32 px as *"a weight on a drill"* — if it reads as a
plain drill, the icon has failed, because the weight is the entire building.

---

# 20. Open questions

- **Does it replace the electric drill or sit beside it?** The brief assumes
  beside: the vanilla drill stays available and stays faster, so the choice is
  live on every patch. If playtesting shows nobody ever builds the fast one, the
  fix is to widen the speed gap, not to remove the option.
- **Interaction with mining productivity.** `uses_force_mining_productivity_bonus`
  is on by default, and productivity already reduces effective drain. Check the
  two do not stack into an ore patch that is functionally infinite.
