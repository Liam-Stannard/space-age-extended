# Factorio Building — Art & Implementation Specification

**Reaction plant.**

**Rendered from a model, design chosen.** Liam chose F, the Circulator, at 5×5
on **2026-10-11**, its finish over rounds 3–5 (*"The colours are good"*) and six
motions (*"All of the animations look good"*), and signed it off the same day
(*"Sign off the reaction plant."*). The plate, pipe pictures, glow and icon are
rendered from `concept/reaction-plant/model/` through `tools/blender/`; there is
no master plate and nothing is generated.

§1, §2, §8 and §13 are records of `prototypes/core/machines.lua`; where they
disagree with the code, the code is right. Until the 5×5 is wired, the code is
still the 3×3 and the 5×5 numbers below are what the wiring task writes into it.

---

# 0. Generation Contract

| # | Asset | Gate before moving on | State |
| - | ----- | --------------------- | ----- |
| 0 | Options and concept | Liam picks | **done: F, round 5** |
| 1 | Model | `--collide` clean; pack checks; cover, corners and rise as the model (85.8 %; NW 96 %, NE 94 %, SW 2 %, SE 4 %; 0.78 tile) | open |
| 2 | Pipe pictures | each face within 1 px of assembler 3's outline | round 5 passes |
| 3 | Plate, shadow, idle | p50 ~75–81, p95 into vanilla's | round 5: p50 75, p95 161 |
| 4 | Legs glow | differenced; blue only in the legs | open |
| 5 | Animation layers | the plate equals every layer's frame 0 | open |
| 6 | Icon | §14 | open |

### Where generation happens

`BLENDER=<blender> tools/blender/render.sh <the model under concept/reaction-plant/model/> <scratch> --ports --icon`,
on the GPU. `render.sh` prints `pack.py`'s checks, and every size and shift in
§11 and §13 is copied from the `meta.json` files it writes. Nothing enters
`graphics/` without sign-off.

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
fluid boxes **rotates**, which is what makes §5's one-plate answer possible
rather than merely cheap. `derive.from` clears `next_upgrade`,
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

**Recipe (to build one):** 40 × `sae-kamacite-plate`, 20 × `pipe`, 15 ×
`advanced-circuit`, 8 s — set for the 3×3 and not yet re-argued for 5×5. **To be
raised toward the refinery's with the wiring task** (Liam, 2026-10-11); no
recipe is fixed here.

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
| **Tile Size** | **5×5** (Liam, 2026-10-11: *"Make the reaction plant 5x5 so any tall parts can mostly remain inside the grid as per the FFF."*). The mass rises 0.78 tile above the north edge (the oil refinery's 0.97). The art is cut to exactly 5.000 tiles wide — §11 |
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
| **No recipe set** | **all three boxes and all three pipe pictures.** It keeps whatever direction it is given, and a pipe laid against the output face joins |
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

**Overall Appearance:** a tall lead-clad **reactor** right of centre. Two fat
strapped **glass legs** stand off its west side: a **riser**, where the blue
climbs with bright bubbles, and a **downcomer**, where it falls with dark
flecks. Fat hoses close the loop into the reactor's shoulder, a cast header at
the foot. An exposed **agitator drive** on the head: shaft, a big five-spoked
pulley, a laced belt and the motor's pulley.

The plant is piled into **three masses**:

1. the reactor with its legs and the compressor;
2. the oxide-red scrubber and the ochre feed drum;
3. the press house, the filtrate receiver and the pump house.

The **filter press** stands on a lead-lined **drop box**. The corners drop out
unevenly (FFF #350): round vessels with ground round them in the north-west and
north-east, bare ground in the south-west and south-east. **Every edge's middle
three tiles meet a wall.**

**Silhouette:** broken and asymmetric, height in the back corners. Cover 85.8 %
of the footprint.

**Visual Age:** **Primitive/Industrial — tier 0.** Hoses, cables and clutter, a
crew's kit piled together, not one machined casting.

## 3.2 Key Visual Features

* **Two glass legs with the solution moving in them**, the only blue.
* **The agitator drive** on the reactor head.
* **The filter press and its drop box.**
* **Lead** on the vessels the solution lives in.
* **A paint per unit.**
* **Our own pipe pictures.**

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
| Dark steel | `#3E3934` | skids, saddles, frames, headers, the four pipe pictures' plates |
| Bare steel | `#A8A090` | pipes, flanges, straps |
| Copper / brass | `#94592C` / `#9A7438` | condenser / gauges, nuts |
| Hoses / lagging | `#5E4636`, `#38302A` / `#9A8A68` | |
| Accents | `#A8301E`, `#D0A428` | handwheels, marking rings |
| Filter cake | `#8C8476` | the cake, only in motion (§6.2) |
| Radiant light | `#1F63FF` → `#73ADFF` | **the two legs only** (3.2 % of the plate) |

**The blue rule:** blue is in the legs and nowhere else — no blue cable, paint
or lamp. Idle, the legs are a still dark navy.

**The paint rule:** paint keeps its colour and wears locally: chips at the
edges, rust only in seams, round bolts, at the foot and down from the bands; a
dirt film, wiped patches, oil at the feet.

**The south pipe picture is neutral dark steel**, like the other three (Liam,
2026-10-11). Round 5 painted its plate the receiver's green; the model changes
that.

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
2. `assembling-machine-3` — the pipe pictures' shape, size and placement.
3. `pumpjack`, `storage-tank` — surfaces and wear.
4. `foundry`, `electromagnetic-plant` — colour.

---

# 5. Building Orientation

## Required Directions

* [x] North · [x] East · [x] South · [x] West — **the entity rotates, and keeps rotating**
* [ ] but **one plate is drawn**, not four

**Direction count:** `4` in the prototype, `1` in the artwork. **Settled by Liam,
2026-09-17:** the fluid ports rotate with the entity and the building itself does
not turn.

**One asymmetric plate serves all four directions.** The mass is off-centre on
purpose and reads in every rotation. What may not exist is a feature that
**names a port**: no painted flange, stub or fluid-coloured marking at an edge.
The engine draws the ports; every edge's middle three tiles meet a wall, so a
picture at any of the twelve positions has something to butt against.

**Hazard tape on the drop box's south face is allowed** (Liam, 2026-10-11): it
names no port.

---

# 6. Sprite Assets Required

## 6.1 Slots

| Asset         | Required | Directions |
| ------------- | -------: | ---------: |
| Main building |        ✓ |          1 |
| Shadow        |        ✓ |          1 |
| Idle state    |        ✓ |          1 |
| Working state |        ✓ |          1 |

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

| State | What the engine draws |
| --- | --- |
| No recipe set — a plant just placed | **all three pipe pictures**, on whichever direction it was given |
| `sae-radiant-precipitation` | **two input pictures on the faced side, and no output picture** |
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
* **Filter press:** 16 frames once per craft. The head stays bolted down; the
  press **opens west** — the leaf pack and tail stand back off **0.18 tile** along
  the rails. Frames 1–4 it opens, 5 the cake hangs, 6–9 it peels away from its
  leaf and falls, **10 it lands in the drop box (the sound accent; never
  frame 0)**, 11–15 the press closes, then it holds. The cake is toned down to a
  grey-buff `#8C8476`: filter cake, not a cell. It falls into a dark chute mouth
  in the drop box's lid.
* **Gauge needles:** 24 f, on **double-size dials on stems**: the reactor's two
  and the scrubber's.
* **Condenser drip:** 24 f; beads run down the copper, and two drops a loop fall
  from a drain cock on its **south-east flank, inside the footprint**, onto a wet
  patch. No steam.

**Moving share, all together: 8.5 %** (chemical plant 5.2 %, refinery 15.9 %).
Each part is its own cropped sheet.

**The press, in the engine.** Once per craft, **rate-locked, not
phase-locked**: the engine does not reset the animation at a craft's start, so
the press runs once in every craft's worth of animation without being tied to
when a craft begins. It **snaps closed when idle** (`idle_animation`). The cake
lands on press frame 10, which carries the sound accent, never frame 0. Two
engine details to verify when wired:

1. the maximum `frame_sequence` length;
2. whether `sound_accents.frame` counts the sequence index or the sprite index.

The alternative is the press as its own `working_visualisation`.

**The steam row is struck.** No air here: no flame, no exhaust, no smoke, no
steam plume, ever.

**No fans, deliberately.** Nothing on a plant without air moves air.

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

**Base, Main Structure, Static Machinery:** one plate, rendered; there is no flat
base under the machine (template rule 7). Every moving part of §6.2 is rendered
out of it as its own cropped sheet, and the plate equals each sheet's frame 0.

**Pipes:** the plant's own pipe pictures, in assembler 3's shape, size and
placement and our own metal, drawn by the engine; vanilla's covers.

**Lighting:** **two status lamps**, on the pump house and the instrument house,
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

All three: the plant's own pipe pictures (§13), `pipe_covers =
derive.pipe_covers()`, `always_draw_covers = false`, `secondary_draw_orders = {
north = -1 }`. The entity sets `fluid_boxes_off_when_no_fluid_recipe = false`
(§2).

## Energy

| Flow | Location | Connection Type |
| ---- | -------- | --------------- |
| in | no visible connector | electric network, `secondary-input`, 1500 kW |

### Hard geometric constraints

1. **The pipe pictures are within 1 px of assembler 3's outline on every face**
   (template rule 6), in our own metal, all four plates neutral dark steel;
   vanilla's covers.
2. **Every edge's middle three tiles meet a wall**, so a picture at any of the
   twelve positions has something to butt against.
3. **North pictures are drawn behind** (`secondary_draw_orders = { north = -1 }`).
   The plate rises 0.17–0.19 tile over the north port tiles; assembler 3's north
   picture stands 0.0–0.31 above the edge.
4. **No marking names a fluid.** Box assignment follows the recipe's ingredient
   order: under `sae-radiant-precipitation` the west input takes solution and the
   east takes gas, and under stage 3's dissolve (`4 spent cells + 50 crust gas`)
   the first fluid is the gas and the assignment swaps. A fluid box is a socket,
   not a fluid. Hazard tape on the drop box's south face names no port and is
   allowed (§5).
5. **The blue sits more than a tile from every edge.**
6. **Nothing crosses ±2.5** (the selection box), and the art is cut to **exactly 5.000 tiles** wide.
   This is a machine players build in rows.
7. **The press's cake is only ever drawn in motion, into a closed box.**

### Visual Requirement

The player tells inputs from outputs by the engine's pipe pictures and the recipe
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
Not required — rendered from the model. One plate; the engine rotates the ports. See §5.
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

**Provisional until packed.** Every size and shift is computed by the packer and
copied from its `meta.json`, never measured off a sheet.

**Tile Size:** `32` px in-game · **Scale:** `0.5` → `64` source px per tile

| | tiles | in-game px | source px |
| --- | --- | --- | --- |
| **Building width** | 5.000 exactly | 160 | **320** |
| **Building height** | ~5.7 (the mass: 5.08 × 5.73 tiles in round 5) | — | — |

**Rise:** 0.78 tile above the north edge (round 5), against the refinery's 0.97.

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
            ├── base.png                  the plate, static
            ├── shadow.png                draw_as_shadow
            ├── legs.png                  24 f, the solution going round
            ├── legs-glow.png             the legs, differenced
            ├── drive.png                 24 f, the agitator drive
            ├── couplings.png             the compressor, dosing-pump and pump couplings
            ├── press.png                 16 f, the filter press
            ├── gauges.png                24 f, the needles
            ├── drip.png                  24 f, the condenser
            ├── status-lamp.png           white lens, engine-tinted
            └── port-*.png                the four pipe pictures
```

Nothing moves to `graphics/` without sign-off. Smoke and particles are not
wanted at all — there is no atmosphere.

---

# 13. Factorio Prototype

**Prototype Type:** `assembling-machine` · **Prototype Name:** `sae-reaction-plant`

### Graphics

```text
To be written by the wiring task, from the packed meta.json, via
derive.own_graphics:
  animation              the plate, the shadow and the moving layers of §6.2,
                         each its own cropped sheet; the press once per craft
                         (§6.2, "The press, in the engine")
  idle_animation         the press closed
  working_visualisations the legs and their glow (only while crafting);
                         the two status lamps (always_draw, apply_tint "status")
  sound accent           on press frame 10, never frame 0
```

**No `flags` line, and no `not-rotatable`.** Settled 2026-09-17.

### Other Visual Properties

```text
Collision / selection: {-2.4,-2.4} -> {2.4,2.4} / {-2.5,-2.5} -> {2.5,2.5}
Max health:            350, the oil refinery's
Shadow:                own draw_as_shadow layer off the model
Lights:                none beyond the glow layer
Fluid Boxes:           2 in (north, {-1,-2} and {1,-2}) + 1 out (south, {0,2}),
                       volume 1000 each; pipe_picture = the plant's own
                       (port-N/E/S/W), pipe_covers = derive.pipe_covers(),
                       always_draw_covers = false,
                       secondary_draw_orders = { north = -1 },
                       fluid_boxes_off_when_no_fluid_recipe = FALSE, this plant alone
Circuit Connections:   inherited from chemical-plant
Remnants:              oil-refinery-remnants, oil-refinery-explosion
```

**Port shifts, from round 5's packed `ports/meta.json`** (re-read from the full
model's pack). Each picture is rendered on the middle tile of its face and
shifted from the tile outside the port:

| Face | Size (px) | Shift |
| --- | --- | --- |
| N | 53 × 22 | `{ 0.00781, 0.34375 }` |
| E | 31 × 71 | `{ -0.72656, 0.05469 }` |
| S | 63 × 69 | `{ -0.00781, -0.77344 }` |
| W | 31 × 72 | `{ 0.72656, 0.01562 }` |

**Remnants and explosion: the oil refinery's for now** (Liam, 2026-10-11), the
5×5 vanilla machine they fit. Our own remnants are a TODO.

**The sound accent is ours.** `derive.own_graphics` strips the inherited
`sound_accents` when the new `graphics_set` is attached, because a gated sound
cannot survive the art it was cued to; the press's accent is set on press frame
10 after that.

The `icon` is taken via `entity_icon()`; the item follows the entity by design,
so the two can never disagree.

---

# 14. Icon

**Icon Required:** ✓ · **Icon Size:** `64×64`, cut to a 120×64 mipmap strip by
`tools/key-icons.py`.

**Icon Concept:** rendered with `--icon`: **the lead reactor and its two lit
legs** (Liam, 2026-10-11). Legible at 32 px.

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
* [ ] Clear silhouette — broken, asymmetric, height in the back corners; corners drop out unevenly
* [ ] Looks like Factorio
* [ ] Matches the Core
* [ ] Inputs are visually understandable — by the engine's pipe pictures, not by the plate
* [ ] Outputs are visually understandable — there is no output port to understand
* [ ] **Does not read as** the vanilla chemical plant — no chimneys, no exhaust, no red-and-white
* [ ] **Does not read as** the oil refinery — no towers, no flare stacks, nothing burns
* [ ] **Does not read as** a storage tank
* [ ] **No plume** — the condenser drips, it never steams
* [ ] Tier 0 finish: hoses, lagging, bolted plate, wear. A paint per unit, worn locally

### Ports — every line comes from §8

* [ ] Each face's pipe picture is **within 1 px of assembler 3's outline**, measured
* [ ] All four pipe pictures' plates are neutral dark steel
* [ ] Every edge's middle three tiles meet a wall
* [ ] The plate reads correctly with **two pipe pictures and with three** (§6.1)
* [ ] A north picture, drawn *behind*, still reads
* [ ] Nothing names which port takes which fluid
* [ ] No output chute; the cake is only drawn in motion, into a closed box
* [ ] Nothing crosses ±2.5

### Blue and glow

* [ ] **No blue outside the legs** — no blue cable, paint or lamp
* [ ] The blue sits more than a tile from every edge
* [ ] The glow layer is the legs only, and `glow_white_px` is 0
* [ ] Idle, the legs are a still dark navy

### Animation

* [ ] The plate equals every layer's frame 0
* [ ] **The press's accent is off frame 0** — the cake lands on press frame 10
* [ ] The press runs once per craft and is closed when idle
* [ ] Nothing moving clashes (`--collide`, every frame)

### Directions

* [ ] North · [ ] East · [ ] South · [ ] West — one plate serves all four; the engine moves the ports
* [ ] All directions represent the same building

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
* [ ] The pipe pictures land on a wall and look like they belong, in all four directions
* [ ] An unconnected port's cover sits right
* [ ] Shadow aligns, does not double, and is *visible* — brighten the screenshot and confirm it is actually there
* [ ] Inserters take the cell from any adjacent tile without the art implying one
* [ ] Neighbours do not overlap — measured, not judged: see Appendix C
* [ ] The building sits on its tile, not above it
* [ ] The press runs once per craft, its accent sounds as the cake lands, and it is closed when idle
* [ ] Performance is acceptable

---

# 16. Final Asset Checklist

```text
[ ] Model
[ ] Pipe pictures
[ ] Directional sprites   (n/a -- one plate, §5)
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
