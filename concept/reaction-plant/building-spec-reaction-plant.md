# Factorio Building — Art & Implementation Specification

**Reaction plant.**

**Rendered from a model, design chosen.** Liam chose F, the Circulator, at 5×5
on **2026-10-11**, its finish over rounds 3–5 (*"The colours are good"*) and six
motions (*"All of the animations look good"*), and signed it off the same day
(*"Sign off the reaction plant."*). Liam then reversed the one plate
(2026-10-20): the building turns with its ports, one model drawn in four
directions. Form 1, the casing, was picked on 2026-10-21 (*"1 Casing"*), and the
four-way model with its ports was signed off on **2026-10-28** (*"Sign off pump
and plant"*). The four plates, glow, lamps and icon are rendered from that model
through `tools/blender/`. There is no master plate, and nothing is generated.

§1, §2, §8 and §13 are records of `prototypes/core/machines.lua`; where they
disagree with the code, the code is right. Until the 5×5 is wired, the code is
still the 3×3 and the 5×5 numbers below are what the wiring task writes into it.

---

# 0. Generation Contract

| # | Asset | Gate before moving on | State |
| - | ----- | --------------------- | ----- |
| 0 | Options and concept | Liam picks | **done: F, round 5** |
| 1 | Model, four directions | `--collide` 0 and `--clash` 0; pack checks; cover ≥ 92 % in every direction | **signed off 2026-10-28** (cover 95.4 / 94.3 / 95.2 / 94.0 %, N/E/S/W) |
| 2 | Connections | vanilla's pipe joins (no gap) at all 3 stubs in all 4 directions, 12/12; nothing of vanilla's pipe or cover laps over the body | **12/12** |
| 3 | Plates, shadows | p50 ~75–81, p95 into vanilla's | p50 81 / 78 / 81 / 74; west *"A: as built"* |
| 4 | Legs glow | differenced; blue only in the legs | open |
| 5 | Animation layers | the plate equals every layer's frame 0 | open |
| 6 | Icon | §14 | open |

### Where generation happens

`RP_FORM=casing RP_DIRECTION=<north|east|south|west> BLENDER=<blender> tools/blender/render.sh <the model> <scratch>`,
one run per direction, on the GPU. No `--ports`: the model has no pipe pictures.
Every size and shift in §11 and §13 is copied from each direction's `meta.json`.
Nothing enters `graphics/` without sign-off.
The icon is re-rendered from the casing model in T09 and shown to Liam before it is set (Liam, 2026-10-28: *"Re-render"*).

### Round log

Every round is in §17.

---

# 1. Building Overview

**Building Name:** `Reaction plant`

**Internal Prototype Name:** `sae-reaction-plant`

**Building Type:** `assembling-machine`, deep-copied from **`chemical-plant`**
via `derive.from` (`crafter()` in `machines.lua`). The type is load-bearing
twice: a crafting machine holds its product in an inventory until an inserter
takes it, so the art draws **no output chute** (§8); and a crafting machine with
fluid boxes **rotates**, so the building can be drawn turning with its ports
(§5). `derive.from` clears `next_upgrade`,
`fast_replaceable_group`, `factoriopedia_simulation`, the frozen patches and the
water reflection.

**Planet / Environment:** the **Core**, and only its surface.
`surface_conditions = { pressure min 1, max 9 }` (`CORE_ONLY`) — not `CORE`, so
unlike the Helium Concentrator it cannot be built on a platform. What gates it
there is the two fluids: radiant solution off the pool's shore and crust gas off
a vent, both drawn by a Crust Tap, neither barrelable, neither existing anywhere
else.

**Purpose:** Stage 1 of the radiant cycle, and the Core's entire power supply.
Two fluids go in and a solid comes out: the crust gas strips the corridor's
isotope out of the solution and drops it as a cell, which burns in the radiant
generator at 10 MW.

**Why it matters:** it is the machine the black start exists *for*. A grid that
browns out stops its reaction plants, which stops the fuel, which stops the
generators; a crust turbine on a vent is the only way back (`08-core-power.md`
§3). The planet's whole power supply passes through this one building, and it
should look like it carries that.

**Technology Unlock:** `sae-radiant-power`, a **trigger technology** whose only
prerequisite is `sae-core-survey`, fired by crafting a `sae-vent-pump`. It
carries the plant, the recipe and the generator together, because none is worth
anything alone. **Tier 0, the foothold tier** (`08-core-power.md` §6). This is
the register-setting fact for §4.

**Recipe (to build one):** 60 × `sae-kamacite-plate`, 30 × `pipe`, 20 × `advanced-circuit`, 10 s (Liam, 2026-10-20: *"×1.5: 60/30/20, 10 s"*).

**Throughput:** unchanged at 5×5 — one cell per 20 s at crafting speed 1 (Liam,
2026-10-11). The bigger footprint buys the art room, not more output.

**Locale (already written, `locale/en/strings.cfg`):**
*"Precipitates the pool's isotope into cells. It will take no other work, and
nothing else will take this."* /
*"Solution in one port, vent gas in the other, and a cell out on the belt. The
planet's whole power supply runs through it."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| **Tile Size** | **5×5** (Liam, 2026-10-11: *"Make the reaction plant 5x5 so any tall parts can mostly remain inside the grid as per the FFF."*). The mass rises 0.64 / 0.81 / 0.53 / 0.73 tile above the north edge, facing N/E/S/W (the oil refinery's 0.97). The art is cut to exactly 5.000 tiles wide — §11 |
| **Collision Box** | `{-2.4,-2.4} → {2.4,2.4}` |
| **Selection Box** | `{-2.5,-2.5} → {2.5,2.5}` |
| **Placement Restrictions** | `pressure` min 1, max 9 — the Core's surface only. `fast_replaceable_group` and `next_upgrade` cleared by `derive.from` |
| **Rotation** | **4-way, always, including with no recipe set.** No `not-rotatable` flag. The ports turn with the entity: the two inputs sit on the faced side and the output opposite. Measured in all four directions on 2.1.19 (at 3×3) |
| **Crafting Category** | `sae-reaction` — private both ways: a vanilla chemical plant cannot make the Core's fuel, and this plant cannot run chemistry |
| **Crafting Speed** | 1 (`crafter` default) |
| **Energy Consumption** | **1500 kW working.** Standby is the chemical plant's inherited `drain`; re-read off a dump before this line is treated as a record |
| **Energy Type** | electric, `secondary-input`. No visible connector |
| **Module slots** | 3, all effects allowed |
| **Health and resistances** | **`max_health = 350`, the oil refinery's** (Liam, 2026-10-11; the 3×3 inherited the chemical plant's 300). No resistances |
| **Fluid Connectors** | **2 in, 1 out**, `volume 1000` each. North `{-1,-2}` and `{1,-2}`, south `{0,2}`. Full table in §8 |
| **Hatch Connectors** | None — this entity type has no such concept |

**Existing saves.** Plants placed at 3×3 will overlap their neighbours once the
entity is 5×5. Accepted: no migrations before 1.0 (Liam, 2026-10-11).

**The recipe it runs:** `sae-radiant-precipitation`, category `sae-reaction`,
20 s, `100 sae-radiant-solution + 100 sae-crust-gas → 1 sae-radiant-fuel`,
surface-gated `pressure 1–9`, `enabled = false` until `sae-radiant-power`. The
cell holds 500 MJ and burns for about fifty seconds in a 10 MW generator.

### `fluid_boxes_off_when_no_fluid_recipe = false`, on this plant alone

`crafter()` sets that flag on every machine it hands boxes to; this one turns it
off again on the next line, and the reason is rotation. With the flag true the
engine gives a machine with no recipe **no fluid boxes at all**, and an entity
with no fluid boxes has nothing to rotate — a freshly placed plant, before its
recipe is chosen, took a direction and snapped straight back to north. Vanilla
agrees about which machines want the flag: the chemical plant, which this one is
shaped after, does not set it.

**What that buys, and what it does not.** It governs the no-recipe case and only
that. Measured on 2.1.19 by the coder, the reviewer and the tester:

| State | What the engine exposes |
| --- | --- |
| **No recipe set** | **all three boxes, so all three stubs take a pipe or a cover.** It keeps whatever direction it is given, and a pipe laid against the output face joins |
| **`sae-radiant-precipitation`** | **the two input boxes only** — the recipe's products are solid, so the engine drops the output box whatever the flag says. No output picture. Still rotates |
| **A future stage-3 fluid recipe** | all three again |

No flag turns the middle row off: it is how the engine handles a crafting
machine's fluid boxes, and a vanilla chemical plant on a recipe whose products
are solid behaves identically.

**The output box is declared now rather than with stage 3's recipe.** A fluid
box is a property of the prototype and not of a recipe, so adding one later would
change the entity's geometry under every plant already standing and every
blueprint holding one: the south face would turn from wall into port, and a
layout that had run belts across it would have to be redrawn. Declared now, that
face is spoken for, and the day stage 3's dissolve recipe is set on a plant the
port comes alive on a line the player already left room for.

### Why it is not a reskin

Vanilla's chemical plant is a two-in two-out fluid converter whose whole
character is two red-and-white chimneys over a low shed, with its ports painted
into its plate. This machine takes two fluids and makes a **solid**, on a private
category, with **engine-drawn ports that move when you rotate it** and a third
port that is dormant under the only recipe it can currently run. Nothing burns
here, so there is nothing for a chimney to be. All of that is visible, and the
art has to carry it.

---

# 3. Visual Design

## 3.1 Design Concept

**What it must not read as:**

* **vanilla's chemical plant** — two chimneys over a shed;
* **the oil refinery, its 5×5 neighbour** — no towers, no flare stacks, nothing
  burns;
* **a storage tank;**
* **any plume** — the condenser drips, it never steams.

**Primary Visual Theme:** *a thermosiphon you watch go round: hour-one plant
piled onto one site.*

**Overall Appearance:** one riveted **housing**, 0.85 tile tall over the whole
footprint, in a putty grey. The vessels stand up through its roof in bolted
collars: the tall lead-clad **reactor**, its two fat strapped **glass legs** (a
**riser**, where the blue climbs with bright bubbles, and a **downcomer**, where
it falls with dark flecks), the condenser and the settling pot. The rest of the
kit stands on the roof. An exposed **agitator drive** sits on the reactor head:
shaft, a big five-spoked pulley, a laced belt and the motor's pulley.

**The flow reads through the building.** Each connection meets a low stub in the
housing, as vanilla's chemical plant's do: vanilla's pipe joins it, or vanilla's
cover sits on it. The unit that uses it stands on the roof straight over
it, joined by a riser with a visible reducer: the feed drum over the solution's,
the compressor's bottle (on legs) over the gas's, and the receiver over the
output's.

The two front corners are broken by the units on the ground in them: the
**filter press** on its lead-lined **drop box** (south-west) and the pump house
(south-east).

**Every hose and cable lands in a port:** a bolted nozzle, a reducer adaptor on
a tank's own nozzle, a saddle clamp on a glass leg, or a gland. The compressor's
own discharge stack is the only run end with none.

**Silhouette:** one building with broken front corners and the vessels rising
out of it. Cover 94.0–95.4 % of the footprint.

**Visual Age:** **Primitive/Industrial — tier 0.** Hoses, cables and clutter, a
crew's kit piled together, not one machined casting.

## 3.2 Key Visual Features

* **Two glass legs with the solution moving in them**, the only blue but the solution's sight glass.
* **The agitator drive** on the reactor head.
* **The filter press and its drop box.**
* **Lead** on the vessels the solution lives in.
* **A paint per unit.**
* **A low stub at each connection**, as vanilla's, its user standing over it.
* **A sight glass on each input line**, showing the fluid in it.
* **The casing.**

### Signature Feature

**The glass loop, the blue going round**, legible at one tile.

**Signature finish:** weathered lead, one material among several.

## 3.3 Colour Palette

Teal is dropped.

| Material | Colour | Where |
| -------- | ------ | ----- |
| Lead | `#66625C` → `#86807A`, bloom `#B4A486` → `#D8CAA6` | reactor, settling pot, drop box, leg caps, alternate filter leaves |
| Oxide red | `#6E2C1E` | scrubber, sampling cabinet |
| Ochre | `#9C7426` | feed drum, ladder |
| Weathered green | `#4E6034` | receiver, motors, press ram |
| Cream | `#ACA084` | pump house, make-up pot, filter leaves |
| Grey | `#6E6A62` | exchanger, instrument house |
| Casing | `#8E8572`, grey trim | the housing |
| Dark steel | `#3E3934` | skids, saddles, frames, headers, the stubs |
| Bare steel | `#A8A090` | pipes, flanges, straps |
| Copper / brass | `#94592C` / `#9A7438` | condenser / gauges, nuts |
| Hoses / lagging | `#5E4636`, `#38302A` / `#9A8A68` | |
| Accents | `#A8301E`, `#D0A428` | handwheels, marking rings |
| Filter cake | `#8C8476` | the cake, only in motion (§6.2) |
| Radiant light | `#1F63FF` → `#73ADFF` | **the two legs only** (1.1–2.0 % of the plate, by direction) |

**The blue rule:** blue is in the legs and nowhere else — no blue cable, paint
or lamp — except the solution's sight glass, which shows the solution in its line (§8 constraint 3). Idle, the legs are a still dark navy.

**The paint rule:** paint keeps its colour and wears locally: chips at the
edges, rust only in seams, round bolts, at the foot and down from the bands; a
dirt film, wiped patches, oil at the feet.

**Lends the generator:** the lead and its bloom, and the paint-per-unit rule.

---

# 4. Factorio Visual Style

### Required characteristics

* [ ] 45-degree top-down Factorio perspective
* [ ] Strong readable silhouette
* [ ] Appropriate visual scale
* [ ] Industrial construction
* [ ] Clear separation between major components
* [ ] Subtle wear and grime
* [ ] No photorealism
* [ ] No text
* [ ] No logos
* [ ] No characters
* [ ] No UI elements
* [ ] No unrelated background objects

**The angle.** 5×5 and tall in the back corners; mostly roof, the near faces
shallow; nothing leans. The camera is `tools/blender/rig.py`'s, calibrated once.

### Technology tier and visual register

**Tier 0 — foothold.** `sae-radiant-power` hangs directly off Core Survey on a
craft-item trigger, so this is among the first four or five machines a player
builds. Hoses, lagging, bolted plate, strapped glass, visible wear. **Do not
tidy it up**, and do not let "handles a radioactive isotope" pull it toward
tier-3 sealed plant: the shielding here is lead sheet riveted on, which is what a
foothold crew would actually do.

### Style Reference Buildings

1. `oil-refinery` and `chemical-plant` — massing, hoses, the fluid window.
2. `chemical-plant`, `oil-refinery`, `cryogenic-plant`, `foundry`: how a pipe meets the casing (the stubs).
3. `pumpjack`, `storage-tank` — surfaces and wear.
4. `foundry`, `electromagnetic-plant` — colour.

---

# 5. Building Orientation

## Required Directions

* [x] North · [x] East · [x] South · [x] West: **the building turns with its ports, one model drawn in four directions**

**Direction count:** `4` in the prototype and `4` in the artwork. **Reversed by
Liam, 2026-10-20**, the 2026-09-17 one plate: *"The model should be adjusted so
the pipe connections make sense and follow the flow of the fluid/gas through the
model. We could draw a model for each rotation rotate like factorio does for some
of the vanilla models"*.

One model, with the camera and sun fixed, is turned on its turntable to face
each direction, as vanilla's chemical plant and oil refinery are. Each direction
is its own render with its own plate, shadow, glow, lamps and moving layers
(§6.2). The connections are fixed (Liam, 2026-10-20): the solution's at
`{-1,-2}`, the gas's at `{1,-2}` and the output at `{0,2}`, facing north, all
turning with the building.

**Ports hidden in one direction are accepted, as in vanilla** (Q21, 2026-10-27).
Facing north, the west leg's feed and gas saddles, the side-nozzle spool and the
cabinet's north gland are hidden. Each of them shows in another direction.

**Hazard tape on the drop box's south face is allowed** (Liam, 2026-10-11): it
names no port.

---

# 6. Sprite Assets Required

## 6.1 Slots

| Asset         | Required | Directions |
| ------------- | -------: | ---------: |
| Main building |        ✓ |          4 |
| Shadow        |        ✓ |          4 |
| Idle state    |        ✓ |          4 |
| Working state |        ✓ |          4 |

**Idle:** frame 0 of every layer, the legs unlit dark navy, the press closed,
the two status lamps tinted by the engine.

**Working:** the legs glow at constant strength while crafting. The press keeps
a once-per-craft rhythm but is not a progress readout.

**Engine limits worth stating.** The prototype cannot show buffer levels, which
port is carrying which fluid, or how far through a batch it is. The legs
therefore circulate and glow at one strength while crafting and stand dark
otherwise — never drawn as a rising level, because no hook would drive one.

**The plate has to read correctly in two port states, which are the two a
player meets** (§2, measured on 2.1.19):

| State | What the engine draws at the plate's stubs |
| --- | --- |
| No recipe set | three boxes; vanilla's cover on each unconnected stub |
| `sae-radiant-precipitation` | the two input boxes only; **no box at the output, so no cover on its stub** |
| A future stage-3 fluid recipe | all three again |

## 6.2 Animation Layers — what moves, decided here

| Layer          | Required | Animated | Frames |
| -------------- | -------: | -------: | -----: |
| Main structure |        ✓ |       No |      1 |
| Machinery      |        ✓ |        ✓ | 24, the press 16 |
| Pistons        |        ✓ |        ✓ | 16 (the filter press) |
| Belts          |        ✓ |        ✓ | 24 (the agitator drive) |
| Fans           |        — |        — |      — |
| Glow           |        ✓ |        ✓ | 24 (the legs) |
| Steam          |        — |        — |      — |

**Six motions** (Liam, 2026-10-11: *"All of the animations look good"*), as
fixed in `options/animation/` (`6-all-fixed.gif`):

* **Legs:** 24 f; the bands rise two wavelengths a loop in the riser and fall in
  the downcomer; bubbles up, flecks down, each wrapping. A loop is ~1.7 s at
  14 fps. Carries the glow.
* **Agitator drive** (replaces the head coupling): 24 f; the big pulley turns
  144° a loop, the motor's small one a full turn.
* **Compressor, dosing-pump and pump couplings:** 60° a loop.
* **Filter press:** 16 frames once per craft. The head and the tail stand stay bolted down; the press **opens west** — the leaf pack, five thin leaves, backs off **0.18 tile** along the rails towards the tail stand. Frames 1–4 it opens, 5 the cake hangs, 6–9 it peels away from its
  leaf and falls, **10 it lands in the drop box (the sound accent; never
  frame 0)**, 11–15 the press closes, then it holds. The cake is toned down to a
  grey-buff `#8C8476`: filter cake, not a cell. It falls into a dark chute mouth
  in the drop box's lid.
* **Gauge needles:** 24 f, on **double-size dials on stems**: the reactor's two
  and the scrubber's.
* **Condenser drip:** 24 f; beads run down the copper, and two drops a loop fall
  from a drain cock on its **south-east flank, inside the footprint**, onto a wet
  patch. No steam.

**Layers per direction.** A layer the camera never sees in a direction has no
sheet there. Its parts stand in that direction's plate at frame 0.

| Facing | Moving layers |
| --- | --- |
| North | legs, drive, the three couplings, press, the three gauges, drip |
| East | as north, without the dosing-pump coupling |
| South | legs, drive, compressor and pump couplings, press |
| West | legs, drive, dosing-pump coupling, press |

**Moving share: 5.17 / 3.54 / 3.96 / 4.63 %**, N/E/S/W (chemical plant 5.2 %, refinery 15.9 %).
Each part is its own cropped sheet.

**The press, in the engine.** Once per craft, **rate-locked, not
phase-locked**: the engine does not reset the animation at a craft's start, so
the press runs once in every craft's worth of animation without being tied to
when a craft begins. The press is its own `working_visualisation`, always drawn (Liam, 2026-10-20: *"Own working visualisation"*): a 140-entry `frame_sequence` at 7/60, 1200 ticks, one craft. The engine never draws `idle_animation` here, so a stopped plant shows the press where it stopped (*"Accept frozen-open"*). The cake lands on press frame 10. The accent counts sequence entries from 0 and sits on entry 21 (measured in T04).

**The steam row is struck.** Nothing burns in this plant: no flame, no exhaust, no smoke, no steam plume, ever. The Core's thin atmosphere would allow them; the design has none.

**No fans, deliberately.** Nothing in this plant needs air moved.

---

# 7. Layer Structure

```text
Building
│
├── Shadow
├── Base
├── Main Structure
├── Static Machinery
├── Pipes
├── Lighting
└── Glow
```

### Layer Notes

**Shadow:** its own `draw_as_shadow` sheet off the model, never baked into the
colour layer.

**Base, Main Structure, Static Machinery:** one plate per direction, rendered.
The housing fills the footprint, and there is no flat base under it (template
rule 7). Every moving part of §6.2 is rendered out of it as its own cropped
sheet, and each plate equals its own direction's frame 0.

**Pipes:** none drawn by the engine. Each connection's low stub is modelled into
every direction's plate and casts and takes its own shadows. The engine draws
vanilla's pipe joined to it, or vanilla's cover on it when unconnected.

**Sight glasses:** two, one per input line, one white sheet a direction each,
ordinary paint (not glow), tinted by the recipe (§8).

**Lighting:** **two status lamps**, one sheet per direction, on the pump house and the instrument house,
cut white and tinted by the engine, `apply_tint = "status"`, `always_draw = true`.

**Glow:** **the legs only**, differenced from a lit and an unlit render of the
same scene. It may not be merged into the base: it is the working-versus-idle
read.

---

# 8. Input / Output Visualisation

## Item Inputs

| Input    | Location      | Direction   |
| -------- | ------------- | ----------- |
| `sae-radiant-fuel` (spent cells, stage 3, not yet implemented) | inserter, any adjacent tile | any |

## Item Outputs

| Output   | Location      | Direction   |
| -------- | ------------- | ----------- |
| `sae-radiant-fuel` | **no port** — a crafting machine holds its product until an inserter takes it, from any adjacent tile | any |

## Fluid Inputs / Outputs

Positions are tiles from the entity centre on a 5×5, given for direction north;
all three turn with the building.

| Fluid box | `production_type` | `direction` | `position` | Which tile edge | volume |
| --- | --- | --- | --- | --- | --- |
| input 1 | `input` | north | `{-1, -2}` | north face, west of centre | 1000 |
| input 2 | `input` | north | `{ 1, -2}` | north face, east of centre | 1000 |
| output | `output` | south | `{ 0,  2}` | south face, centre column | 1000 |

All three: no `pipe_picture`; the stub is in the plate. `pipe_covers =
derive.pipe_covers()`, `always_draw_covers = false`, `secondary_draw_orders = {
north = -1 }`. The entity sets `fluid_boxes_off_when_no_fluid_recipe = false`
(§2).

## Energy

| Flow | Location | Connection Type |
| ---- | -------- | --------------- |
| in | no visible connector | electric network, `secondary-input`, 1500 kW |

## Circuit connector

The model carries a terminal box with its cable gland on the wall facing the
camera, one per direction. The engine's connector sprite is drawn over it (model
tiles, x east, y north, facing north before turning):

| Facing | Socket | Model position |
| --- | --- | --- |
| North | the housing's south wall | `(0.85, -2.328, 0.5)` |
| East | the housing's east wall | `(2.428, -0.95, 0.5)` |
| South | the housing's north wall | `(0.0, 2.328, 0.5)` |
| West | the housing's west wall | `(-2.428, 0.6, 0.5)` |

The prototype positions come from the render.

### Hard geometric constraints

1. **Each connection meets a low stub in the housing; vanilla's pipe joins it
   with no gap at all 12 connections, measured, and nothing of vanilla's pipe or
   cover laps over the body's top.**
2. **North covers are drawn behind** (`secondary_draw_orders = { north = -1 }`).
3. **No marking names a fluid; a sight glass shows it.** Box assignment follows the recipe's ingredient
   order: under `sae-radiant-precipitation` the west input takes solution and the
   east takes gas, and under stage 3's dissolve (`4 spent cells + 50 crust gas`)
   the first fluid is the gas and the assignment swaps. A fluid box is a socket,
   not a fluid. Each input line carries a sight glass, drawn white and tinted by
   the recipe (`crafting_machine_tint`: primary is the first fluid's colour,
   secondary the second's), so it shows whatever fluid is in that line; a
   mirrored plant draws `graphics_set_flipped` with the two tints swapped (Liam,
   2026-10-28: *"Adopt"*, *"Sight glass"*). Hazard tape on the drop box's south
   face names no port and is allowed (§5).
4. **The blue sits more than a tile from every edge.**
5. **Nothing crosses ±2.5** (the selection box), and the art is cut to **exactly 5.000 tiles** wide.
   This is a machine players build in rows.
6. **The press's cake is only ever drawn in motion, into a closed box.**

### Visual Requirement

The player tells inputs from outputs by the stubs modelled into each direction's plate and the recipe
tooltip, not by the art, and the art must not pretend otherwise. **The most
likely mistake is an output chute**: a solid does come out of this machine, and
the cell comes out wherever the inserter is. The drop box is not a chute: the
cake falls into it and is never seen leaving.

---

# 9. Image Generation Prompts

Not used: every asset is rendered from the model (§0). The headings stay because
`tools/generate-building-art.py` reads them.

## Concept Sheet Prompt

```text
Not required — rendered from the model. See §0.
```

---

## Master Concept Prompt

```text
Not required — rendered from the model. See §0.
```

---

## Directional Prompts

### North

```text
Not required — rendered from the model. Four directions from one model; see §5.
```

### East

```text
Not required — rendered from the model. See §5.
```

### South

```text
Not required — rendered from the model. See §5.
```

### West

```text
Not required — rendered from the model. See §5.
```

---

## Layer Prompts

### Main Structure

```text
Not required — rendered from the model. See §0.
```

### Glow / Lighting

```text
Not required — rendered from the model; the legs' glow is differenced. See §7.
```

---

# 10. Image Processing

`pack.py`'s checks, run by `render.sh`: the template's Appendix C must hold
exactly (`centre_offset_px 0`, `edge_alpha_max 0`, **`half_width_tiles 2.5`**),
and `glow_white_px` stays at 0.

---

# 11. Sprite Dimensions

Every size and shift is computed by the packer and
copied from its `meta.json`, never measured off a sheet.

**Tile Size:** `32` px in-game · **Scale:** `0.5` → `64` source px per tile

| | tiles | in-game px | source px |
| --- | --- | --- | --- |
| **Building width** | 5.000 exactly | 160 | **320** |

**Per direction.** Each direction has its own sizes and shifts, copied from that
direction's `meta.json`. **Rise:** 0.64 / 0.81 / 0.53 / 0.73 tile, N/E/S/W,
against the refinery's 0.97.

| Sheet | Frames | North | East | South | West |
| --- | ---: | --- | --- | --- | --- |
| `base` | 1 | 327×367 @ (-0.00781, -0.32031) | 327×381 @ (-0.00781, -0.39844) | 327×357 @ (+0.00781, -0.30469) | 327×375 @ (+0.00781, -0.35156) |
| `shadow` | 1 | 360×329 @ (+0.3125, -0.05469) | 353×344 @ (+0.25781, -0.09375) | 365×329 @ (+0.35156, -0.07031) | 345×335 @ (+0.22656, -0.02344) |
| `legs-glow` | 1 | 188×57 @ (-0.01562, +0.13281) | 34×210 @ (-0.73438, -0.59375) | 188×56 @ (-0.01562, -1.3125) | 34×207 @ (+0.70312, -0.57031) |
| `status-lamp` | 1 | 14×216 @ (+2.29688, +0.17188) | 189×41 @ (-0.82031, +1.64844) | 13×164 @ (-2.28906, -1.46875) | 189×25 @ (+0.82031, -2.94531) |
| `sight-glass-1` | 1 | 16×19 @ (-1.17188, -1.17969) | 14×7 @ (+2.0, -0.47656) | 91×104 @ (+0.58594, +0.75) | 19×18 @ (-0.63281, +0.65625) |
| `sight-glass-2` | 1 | 15×23 @ (+1.53906, -2.05469) | 18×14 @ (+0.9375, +0.46875) | 14×15 @ (-1.53125, -0.16406) | 21×19 @ (-0.96094, -2.61719) |
| `legs` | 24 | 189×61 @ (-0.02344, +0.11719) | 35×213 @ (-0.74219, -0.60156) | 189×60 @ (-0.02344, -1.32812) | 35×210 @ (+0.69531, -0.57812) |
| `drive` | 24 | 64×60 @ (-0.0625, -2.10938) | 59×65 @ (+0.25781, -1.91406) | 64×61 @ (+0.0625, -1.60156) | 59×65 @ (-0.25781, -1.78906) |
| `coupling-compressor` | 24 | 7×20 @ (+1.94531, -2.375) | 16×6 @ (+1.75, +1.25) | 7×20 @ (-1.94531, +1.125) | — |
| `coupling-dosing` | 24 | 7×15 @ (-0.44531, +0.42969) | — | — | 6×4 @ (+1.03125, -0.17188) |
| `coupling-pump` | 24 | 10×18 @ (+2.03125, +1.375) | 17×10 @ (-1.94531, +1.42188) | 10×19 @ (-2.03125, -2.50781) | — |
| `press` | 16 | 81×92 @ (-1.88281, +1.73438) | 61×93 @ (-1.99219, -2.22656) | 81×94 @ (+1.88281, -2.26562) | 61×114 @ (+1.99219, +1.5) |
| `gauge-reactor-upper` | 24 | 10×5 @ (+0.03125, -0.10156) | 5×11 @ (-0.75781, -0.82031) | — | — |
| `gauge-reactor-lower` | 24 | 10×7 @ (-0.17188, +0.24219) | 4×10 @ (-0.76562, -0.67188) | — | — |
| `gauge-scrubber` | 24 | 8×7 @ (-1.5, -2.02344) | 6×8 @ (+1.29688, -2.23438) | — | — |
| `drip` | 24 | 23×36 @ (+2.21094, -0.03125) | 37×33 @ (-0.44531, +1.66406) | — | — |

East and west reach one faint pixel (alpha 29 or less) past the 5-tile edge, as at sign-off (Liam, 2026-10-28: *"Accept, note in spec"*).

---

# 12. File Structure

```text
├── concept/
│   └── reaction-plant/
│       ├── building-spec-reaction-plant.md
│       ├── model/                        the model, rendered by tools/blender/
│       └── options/                      rounds 1-5 and the animation previews
└── graphics/
    └── entity/
        └── reaction-plant/
            ├── north/ east/ south/ west/   one folder a direction, each with:
            │   ├── base.png  shadow.png  legs.png  legs-glow.png  status-lamp.png  sight-glass-1.png  sight-glass-2.png
            │   └── the moving layers seen in that direction (§6.2)
```

Nothing moves to `graphics/` without sign-off. Smoke and particles are not
wanted at all: nothing here burns or vents.

---

# 13. Factorio Prototype

**Prototype Type:** `assembling-machine` · **Prototype Name:** `sae-reaction-plant`

### Graphics

```text
From each direction's packed meta.json, via derive.own_graphics:
  animation              north/east/south/west_animation: each direction's
                         plate, shadow and the moving layers seen in it (§6.2)
  working_visualisations each with north/east/south/west_animation: the press;
                         the legs and their glow; the two status lamps
                         (always_draw, apply_tint "status"); the two sight
                         glasses (always_draw, apply_recipe_tint primary /
                         secondary)
  circuit_connector      one per direction, at the model's socket (§8)
  graphics_set_flipped   the same set with the two glasses' tints swapped (§8)
  recipe_not_set_tint    neutral grey, 0.5
```

**No `flags` line, and no `not-rotatable`.** Settled 2026-09-17.

### Other Visual Properties

```text
Collision / selection: {-2.4,-2.4} -> {2.4,2.4} / {-2.5,-2.5} -> {2.5,2.5}
Max health:            350, the oil refinery's
Shadow:                own draw_as_shadow layer off the model
Lights:                none beyond the glow layer
Fluid Boxes:           2 in (north, {-1,-2} and {1,-2}) + 1 out (south, {0,2}),
                       volume 1000 each; no pipe_picture,
                       pipe_covers = derive.pipe_covers(),
                       always_draw_covers = false,
                       secondary_draw_orders = { north = -1 },
                       fluid_boxes_off_when_no_fluid_recipe = FALSE, this plant alone
Circuit Connections:   one per direction, from the model (§8)
Remnants:              oil-refinery-remnants, oil-refinery-explosion
```

| Facing | Socket | `main_offset` (screen tiles) | ground under it (tiles) |
| --- | --- | --- | --- |
| North | the housing's south wall | `{0.85, 2.078}` | `{0.85, 2.328}` |
| East | the housing's east wall | `{-0.95, 2.178}` | `{-0.95, 2.428}` |
| South | the housing's north wall | `{0.0, 2.078}` | `{0.0, 2.328}` |
| West | the housing's west wall | `{-0.6, 2.178}` | `{-0.6, 2.428}` |

Connector sprite: vanilla's variation 18 (Liam, 2026-10-28: *"18, face-on"*).

**Remnants and explosion: the oil refinery's for now** (Liam, 2026-10-11), the
5×5 vanilla machine they fit. Our own remnants are a TODO.

**The sound accent is ours.** `derive.own_graphics` strips the inherited
`sound_accents` when the new `graphics_set` is attached, because a gated sound
cannot survive the art it was cued to; the press's accent is set on the press's sequence entry 21 after that.

Alt-mode icon: twice the size (Liam, 2026-10-20: *"Double, like the refinery"*), at the centre, `{0, 0}`, one place for all four directions (Liam, 2026-10-28: *"Centre"*).

The `icon` is taken via `entity_icon()`; the item follows the entity by design,
so the two can never disagree.

---

# 14. Icon

**Icon Required:** ✓ · **Icon Size:** `64×64`, cut to a 120×64 mipmap strip by
`tools/key-icons.py`.

**Icon Concept:** rendered with `--icon`: **the lead reactor and its two lit
legs** (Liam, 2026-10-11). Legible at 32 px.
The icon is re-rendered from the casing model in T09 and shown to Liam before it is set (Liam, 2026-10-28: *"Re-render"*).

### Icon Prompt

```text
Not required — rendered from the model with --icon. See §14.
```

---

# 15. Visual QA Checklist

### Building

* [ ] Correct tile size — 5.000 tiles wide, measured, not judged
* [ ] Correct perspective — mostly roof, shallow near faces, nothing leans
* [ ] Correct scale
* [ ] Clear silhouette — one building, front corners broken, vessels rising out of it
* [ ] Looks like Factorio
* [ ] Matches the Core
* [ ] Inputs are visually understandable — each input's run reads from its stub to the unit that uses it
* [ ] Outputs are visually understandable — there is no output port to understand
* [ ] **Does not read as** the vanilla chemical plant — no chimneys, no exhaust, no red-and-white
* [ ] **Does not read as** the oil refinery — no towers, no flare stacks, nothing burns
* [ ] **Does not read as** a storage tank
* [ ] **No plume** — the condenser drips, it never steams
* [ ] Tier 0 finish: hoses, lagging, bolted plate, wear. A paint per unit, worn locally
* [ ] Every hose and cable end lands in a port; clipping checked by eye

### Ports — every line comes from §8

* [ ] Joins pass (no gap) at all 12 connections
* [ ] Each stub sits low in the housing, as vanilla's
* [ ] The plate reads correctly with **two boxes and with three, in every direction** (§6.1)
* [ ] A north cover, drawn *behind*, still reads
* [ ] Nothing names which port takes which fluid
* [ ] No output chute; the cake is only drawn in motion, into a closed box
* [ ] Nothing crosses ±2.5

### Blue and glow

* [ ] **No blue outside the legs and the solution's sight glass** — no blue cable, paint or lamp
* [ ] The blue sits more than a tile from every edge
* [ ] The glow layer is the legs only, and `glow_white_px` is 0
* [ ] Idle, the legs are a still dark navy

### Animation

* [ ] The plate equals every layer's frame 0
* [ ] **The press's accent is off frame 0** — the cake lands on press frame 10
* [ ] The press runs once per craft and holds where it stopped
* [ ] Nothing moving clashes (`--collide`, every frame)

### Directions

* [ ] North · [ ] East · [ ] South · [ ] West: the building turns with its ports; measured in each
* [ ] All directions represent the same building
* [ ] The circuit connector sits on the model's socket in every direction

### Rendered-art defects

* [ ] No baked drop shadow in the colour layer
* [ ] No ground plane or scenery
* [ ] `tonal.py`: p50 ~75–81, p95 into vanilla's
* [ ] Nothing glows that §3.3 says is unlit

### In-Game

Place **at least three in a row**, set one to precipitation, leave one with no
recipe, and rotate one.

* [x] **The ports turn with the entity in all four directions, inputs on the faced side and output opposite** — measured on 2.1.19 by the coder, the reviewer and the tester (at 3×3)
* [x] **With no recipe the plant carries all three boxes, keeps its direction, and a pipe at the output joins; with `sae-radiant-precipitation` the engine keeps the two inputs only and drops the output** — measured on 2.1.19 (at 3×3)
* [ ] Pipes join each stub, in all four directions
* [ ] With `sae-radiant-precipitation`, the output stub with no box looks right
* [ ] An unconnected port's cover sits right
* [ ] Each sight glass shows its line's fluid, in four directions, normal and mirrored
* [ ] Shadow aligns, does not double, and is *visible* — brighten the screenshot and confirm it is actually there
* [ ] Inserters take the cell from any adjacent tile without the art implying one
* [ ] Neighbours do not overlap — measured, not judged: see Appendix C
* [ ] The building sits on its tile, not above it
* [ ] The press runs once per craft, its accent sounds as the cake lands, and it holds where it stopped
* [ ] Performance is acceptable

---

# 16. Final Asset Checklist

```text
[ ] Model
[ ] Stubs (in the plates)
[ ] Directional sprites   (four, §5)
[ ] Shadow
[ ] Idle / static picture
[ ] Working state
[ ] Glow layer
[ ] Icon
[ ] Spritesheets
[ ] Factorio prototype
[ ] In-game test
```

---

# 17. Design Notes / Iteration History

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| `1` | `v1-sheet.png` | A complete, well-laid-out sheet: squat banded drum, uniform gutter, three lit slots, teal on the motor block and hatch, tier-0 riveted finish, eight panels and a palette strip | **reject** — five faults | 1. Strip the copper pipework that runs down the outside of the drum and lands on the gutter: nothing may reach the footprint edge. 2. Turn the machine square-on — the base's front edge parallel to the bottom of the frame, not corner-on. 3. Draw the coupling FREE: a gap all round, nothing meshing with it. 4. Add the missing top-view panel. 5. Remove the Factorio wordmark |
| `2` | `v2-sheet.png` | All five fixes taken: no pipework anywhere near the edge, the base square-on, the coupling free in a recessed bay with the shaft visible beneath it, a top-view panel added, the wordmark gone | **reject** — two faults left | 1. The gutter's sockets read as small brass bolts; they must be blanked-off fluid sockets at the **size and style of a chemical plant's ports**, about 0.8 tiles across, three per side, twelve in all. 2. The three shield bands have flattened into stacked rings — bring them back as distinct lead bands on bolted lugs |
| `3` | `v3-sheet.png` | Both fixes taken, nothing else disturbed: capped sockets with bolted collars set three to a side all the way round, and three distinct lead bands with lugs and plain riveted shell between them | **reject** — accepted in error, then withdrawn on measurement. Liam: *"I dont see the pipe ports."* Measured, the sockets are **0.27 tiles** in the main view and **0.43** in the top view against the 0.80 the rule asks, they are blank lids with no bore, and the two panels disagree. The first verdict was eyeballed, which is the claim Appendix C says not to make | Double the sockets to 0.80 tiles, give each one an open mouth inside its collar, and draw them the same size in every panel |
| `4` | `v4-sheet.png` | The mouths are fixed — dark open bores inside raised bolted collars, three to a side, twelve in all, consistent between panels — and nothing else moved | **reject, narrowly** — one number still short | Measured on the main view at 171.0 px/tile: near-edge sockets **0.50–0.53 tiles**, side-edge sockets **0.41–0.42**, against a target of **0.80** (139 px on this sheet). "Roughly double" was taken literally and landed at about 60% of target. Next ask states it as a span: the three sockets on a side must together cover about four fifths of that whole side |
| `R1` | `options/` | The redesign's first options, A–D at 3×3 | Liam asked for 5×5 | Five new options at 5×5 |
| `R2` | `options/round-2/` | Five options at 5×5 | **F, the Circulator, chosen** | Textures |
| `R3` | `options/round-3/` | F textured | **reject** | The front pipe, and texturing to the base game |
| `R4` | `options/round-4/` | Real pipe pictures in assembler 3's shape; a broken silhouette; vanilla's surfaces studied | **model approved** | Colour and detail |
| `R5` | `options/round-5/` | A paint per unit, rust confined, details | **accepted** — *"The colours are good."* | The animation previews |
| `A1` | `options/animation/` | Six motion previews | **accepted, one fault** — the vent condenser clips | Fix every clash; re-render "all together" |
| `A2` | `options/animation/6-all-fixed.gif` | The clashes fixed | **signed off** | — |
| `T06` | `model/four-way/` | The model in four directions, a fitting at each connection | flow did not read | the runs visible to their users |
| `T06b–d` | `model/four-way/`, `t06d/` | Flow traced; hose and pipe scale; fat-hose variant | thin hoses, visibly fastened | new layouts |
| `T06e` | `options/round-layout/` | Takes A–D | *"more like a building"* | three forms |
| `T06g` | `options/round-forms/` | Casing, frame, rotunda | **1, the casing** | refine |
| `T06h` | `options/round-forms-refine/` | Kit restored, tone lifted | *"A: as built"* | ports |
| `T06i` | `options/round-ports/` | Every run end in a port, 42 of 42 | **signed off 2026-10-28** | — |

### Version 1

Spec drafted against three fluid boxes and `assembler2pipepictures`: the engine
draws every port, so the plate draws none, the footprint edge is a uniform bolted
gutter, and one direction-neutral plate covers all four rotations. Accent proposed
as contamination magenta.

### Version 2

The code briefly carried two input boxes and an emptied `pipe_picture`, which
inverted the brief — the flanges would have been ours to paint, and orientation
became a fork. Written, then overtaken when the code was returned to the agreed
arrangement.

### Version 3

Liam settled three things on 2026-09-17: the ports rotate with the entity and the
building does not turn, so one direction-neutral plate and no `not-rotatable`; the
accent is **works teal `#2A7F7A`**; and stage 3's output box is **declared now**, so
the south face is spoken for in blueprints stamped today.

**The wording agreed, 2026-09-17.** Two further changes on the same day. **The
teal is roof-only** — drive guard and inspection-hatch cover, nothing at the
gutter or any edge. And **`fluid_boxes_off_when_no_fluid_recipe` is false on this
plant alone**, so a plant with no recipe keeps its boxes and can be turned: the
no-recipe state shows all three stubs rather than none, measured on 2.1.19 by the
coder, the reviewer and the tester.

**The lesson worth keeping:** `pipe_picture` decides who draws the port, and it
decides half the art brief with it. Read it before writing §7 and §8, on every
building.

The 3×3 banded drum was then modelled in Blender and wired, signed off
2026-10-01. Version 4 replaces it.

### Version 4 — the redesign

All on **2026-10-11**.

**Why.** Liam on the 3×3 model: *"The reaction plant looks like a plate with a
dome on top, i think we redo the model completely. Look at the oil refinery and
chemical plant for inspiration. We want bulky hoses, a glass view port for the
fluids and asymmetrical design."* The banded drum and its spider coupling were
dropped.

**Round 1.** A study of the oil refinery and the chemical plant, then four
options at 3×3, A–D, each with a glass view port. Liam: *"Make the reaction
plant 5x5 so any tall parts can mostly remain inside the grid as per the FFF."*

**Round 2.** Five new options at 5×5, tall parts inside the grid. Liam: *"The
circulator is good but the textures need work."* F, the Circulator, chosen.

**Round 3.** F textured to vanilla's level. Liam: *"the pipe at the front
doesn't look right, the texturing also doesn't fit basegame factorio."*

**Round 4.** The real pipe pictures for every port, in assembler 3's shape and
our own metal; vanilla's surfaces studied and matched; the silhouette broken
(FFF #350). Liam: *"the model is good but the textures could be improved,
everything is the same, add some colour and more details to break up the rust
texture."* The model was approved as it stood.

**Round 5.** A paint per unit, measured on vanilla's machines; rust confined to
where it forms; seams, rivets, gauges, handwheels, wiped patches, oil stains.
Liam: *"The colours are good."*

**The animation previews.** Liam: *"Could you show me what these animations
would look like."* Six previews on round 5's model: the legs and couplings, the
filter press, the gauge needles, the agitator drive, the vent condenser, and all
together. Liam: *"All of the animations look good, a small problem is the vent
pump clips."* All six kept, the agitator drive replacing the head coupling.

**The clip fixes.** `--collide` over the whole model and every frame. The
condenser's drain cock moved from the east flank, where it reached past the
footprint, to the south-east flank inside it; the exchanger shortened clear of
the condenser and the scrubber; the couplings centred in their gaps; the belt's
lacing clips laid along the belt; the press made to open west, its head bolted
down and the leaf pack and tail standing back 0.18 tile, where it had backed
east into the filtrate receiver; the cake toned down to `#8C8476`; the gauges
made double-size dials on stems. Moving share 8.5 %.

**Signed off.** Liam: *"Sign off the reaction plant."* The design is F at 5×5:
round 5's model and colours with the animation set as fixed.

**The spec.** Liam agreed this wording and the recommended answers: *"Agree to
all."* One cell per 20 s; health 350 and a build cost raised toward the
refinery's; the refinery's remnants and explosion for now; the art cut to
5.000 tiles; the press once per craft, rate-locked, closed when idle, its accent
on frame 10; the icon the reactor and its two lit legs; the south pipe picture
dark steel; hazard tape on the drop box allowed; two status lamps; old 3×3 saves
left to overlap, no migrations before 1.0. The sprite brief beside this spec is
retired, superseded by the model (§0).

### Version 5 — four directions

**Why.** Liam, 2026-10-20, on the engine's pipe pictures over the one plate:
*"The model should be adjusted so the pipe connections make sense and follow the
flow of the fluid/gas through the model. We could draw a model for each rotation
rotate like factorio does for some of the vanilla models"*; the connector: *"All
of them - the model should cater for them"*. This reverses the one plate of
Version 3.

**Flow, then layout.** *"The pipe connections should allow the liquid to flow
through the building or out of the building as you expect."* On the runs: *"it
wouldn't make sense to suddenly half the diameter of the pipe"*. Hoses: *"Thin,
when hoses connect to something they need to look like they're structurally
connected"*. On the layouts: *"it would help if it looked more like a building
than some tanks on the ground"*; connections *"Should enter the building's
wall"*.

**The casing.** *"1 Casing"*; the left-out kit *"Restore in refine"*; tone *"A: as
built"*. Then: *"The hoses on thr reaction plant don't have appropriate ports,
they look like they lead to nowhere"*. Every run end now lands in a port. Q21 was
answered A on all four: kit as built, saddles kept, ports hidden in one direction
accepted, gland as is.

**Signed off, 2026-10-28.** *"Sign off pump and plant"*. Joins 12/12, collide 0,
clash 0, cover 94.0–95.4 %.

**Connections like vanilla's, and sight glasses, 2026-10-28/29.** *"For the reaction plant make the pipe connections like vanillas"*, *"Like the Gas Pump fix"*: the wall fittings became low stubs, signed off *"Sign off"*. A sight glass on each input line, tinted by the recipe and swapped when mirrored (*"Adopt"*, *"Sight glass"*; a second glass facing east, *"Add a second glass"*).
