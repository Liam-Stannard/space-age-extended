# Factorio Building — Art & Implementation Specification

**Whisker Comber.** First draft — a brief, enough to commission and judge a
concept sheet. Not a specification: §6, §12 and §13 stay open until a sheet is
approved and a canonical plate has been measured.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **draft — `concept/v1-sheet.png`**, not locked |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3 | blocked on 0 |
| 5 | Working animation | portrait 2:3 | The comb stroke loops seamlessly | blocked on 1 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

---

# 1. Building Overview

**Building Name:** `Whisker Comber`
**Internal Prototype Name:** `sae-whisker-comber`

**Building Type:** `assembling-machine`.

**Purpose:** Turns a harvest of loose kamacite whiskers into either **whisker
tow** — combed into one direction, strong in tension, the feedstock for composite
— or **whisker felt**, matted and unaligned, which is cheap thermal insulation.
Two recipes, one machine, and the player chooses the split.

**Why it matters:** the farm currently has one output and therefore no decisions.
Single-crystal fibres really are absurdly strong along their axis and useless
across it, so alignment is a genuine process step rather than an invented one —
and two grades from one crop is what turns a field into a factory. The answer to
*"how much of this harvest is worth combing?"* changes as the base grows, which is
the only kind of number a player enjoys revisiting.

**Locale:** *"Strength runs one way in a whisker. This is what points them all the
same way."* / *"Combed into tow, or matted into felt. The comb is slow and the
mat is not, and which you want depends on what your line is short of."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 3×3 (`collision_box {-1.4,-1.4},{1.4,1.4}`) |
| Directions | 1 |
| Crafting category | `sae-fibre` |
| Energy | 400 kW, electric |
| Surface conditions | `pressure` ≤ 9 — the Core and platforms |
| Module slots | 3 |

**The two recipes, first pass:**

| Recipe | In | Out | Time |
| ------ | -- | --- | ---- |
| Combing | 8 kamacite whiskers | 1 whisker tow | 12 s |
| Matting | 4 kamacite whiskers | 1 whisker felt | 3 s |

Combing is deliberately four times slower per whisker. Tow is what the composite
line needs and felt is what the cryostat needs, so neither is the "correct"
answer — but a player who combs everything will find their cryogenics starved,
and a player who mats everything will never build a frame.

### Why it is not a reskin

Nothing in vanilla splits one harvest into a quality-graded pair where both
grades have real consumers. Gleba's fruit yields fixed products; this is the
player deciding the ratio, every hour, against whatever their line is short of.

---

# 3. Visual Design

## 3.1 Design Concept

A carding machine for metal. Two counter-rotating **comb drums**, their surfaces
covered in fine needles, with a loose mass of whiskers going in one side and a
neat aligned sliver leaving the other.

**The anti-read is a textile mill.** The reference is real carding machinery, but
the material here is metal, the environment is vacuum, and the machine should
look like it is handling something that would cut you: guarded, heavy, with the
drums recessed rather than open.

## 3.2 Key Visual Features

* **Two comb drums** side by side, needled surfaces catching the light, recessed
  below a guard rail.
* An **infeed tray** at one end holding a loose grey tangle.
* An **outfeed nip** at the other, where the aligned sliver emerges as a bright
  ordered ribbon.
* A **guard hood** that is clearly removable and clearly necessary.

### Signature Feature

**The before-and-after across the machine's length.** Tangle at one end, ordered
ribbon at the other, and the transition visible in between. It is the recipe
drawn on the building, and it is what makes the comber legible next to the
classifier, which is also a low grey box that sorts things.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Chassis and hood | `#4A463F` → `#6E685C` | the mass of the building |
| Comb drums | `#8A8580` | the two cylinders |
| Needle glints | `#D8D4CC` | drum surfaces, sparingly |
| Loose whiskers | `#9A9488` | infeed tray, disordered |
| Aligned tow | `#C8C4BC` | outfeed, brighter and ordered |

**The aligned material is brighter than the loose material.** That is physically
true — aligned fibres catch light coherently — and it is the whole visual gag.

---

# 4. Factorio Visual Style

3×3 and low, mostly roof and hood from the camera, so the two drums have to be
visible *through* the guard rather than hidden by it. Style reference to attach:
the **biochamber**, cropped and upscaled, for the organic-process-in-an-
industrial-shell read.

---

# 5. Building Orientation

* [x] North only

**Direction count:** `1`. The infeed-to-outfeed axis is fixed and the inserters
do not care which end they stand at.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Whiskers in | any adjacent tile | inserters, unconstrained |
| Tow / felt out | any adjacent tile | one output inventory |
| Electric | no visible connector | poles reach it wirelessly |
| Fluids | none | no fluid box; no pipe flange in the art |

---

# 11. Generation Requirements

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio
Space Age industrial machine, every panel drawn from the game's characteristic
45-degree top-down perspective. The machine is a low three-by-three metal-
fibre carding machine standing on an airless metallic world. Two pale grey
needled comb drums lie side by side, recessed beneath a heavy guard hood and
rail, and the needles are the machine's most distinctive feature. At one end a
deep empty hopper mouth opens upward; at the other a pair of polished nip
rollers sits in an empty outfeed slot. Dark grey-brown chassis and hood, pale
grey drums with fine bright needle glints. No textile-mill wooden framing, no
belts, no glow, no flame, no smoke. Panels: main view, side elevation showing
the hopper mouth at one end and the nip rollers at the other, top-down view, a
close detail of the needled drum surface and the guard rail, and the drums
shown at two points in their rotation. Title the sheet WHISKER COMBER. Draw no
loose material anywhere: no ore, powder, fibre, grit, debris or product on the
ground, in bins, at chutes, on trays or spilling from the machine. Factorio
machines never show what they make, so every chute, port, bin and tray is
drawn as empty machinery. Every pipe connection must run down to ground level
and stop flush at the edge of the tile footprint; no pipe may end in mid-air
and none may leave the top of the building. Nothing may extend past the tile
footprint, pipework included, and the tile-grid panel must show the whole
machine inside the grid with no overhang.
```

---

# 15. Factorio Prototype — sketch

```lua
{
  type = "assembling-machine",
  name = "sae-whisker-comber",
  crafting_categories = { "sae-fibre" },
  crafting_speed = 1,
  energy_usage = "400kW",
  energy_source = { type = "electric", usage_priority = "secondary-input" },
  surface_conditions = { { property = "pressure", max = 9 } },
  module_slots = 3
}
```

---

# 16. Icon

A bundle of aligned fibres against a tangle, split down the middle of the frame.
Must read at 32 px as *"messy on one side, neat on the other"*; the drums will not
survive and should not be attempted.

---

# 20. Open questions

- **Should felt come out of combing as a byproduct instead of its own recipe?**
  A single recipe yielding tow plus a little felt is simpler and removes the
  choice. The choice is the point, so: two recipes. Recorded here so it is not
  quietly simplified later.
- **Both consumers must exist before this is worth building.** Tow feeds whisker
  prepreg (T5) and felt feeds the cryostat core (T6), and neither tier is built.
  Landing the comber alone gives the player two items with nowhere to go.
- **`allowed_effects`.** Speed modules on combing would undercut
  `04-the-core.md` §7's rule that the answer to "faster" is more floor. The farm
  itself is already area-limited, so the comber is arguably the one place speed
  is legitimate — but it should be a decision, not an oversight.
