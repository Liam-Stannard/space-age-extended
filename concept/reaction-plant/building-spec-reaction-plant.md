# Factorio Building — Art & Implementation Specification

**Reaction plant.** A brief, enough to commission and judge a concept sheet, in
the manner of the Helium Concentrator's. It is **not** a specification: §6.1,
§12 and §13 stay open until a sheet is approved and a canonical plate has been
measured.

**Agreed wording, four decisions taken.** Liam settled the orientation, the
accent, the output box and the accent's placement on **2026-09-17** (§5,
Appendix B, §8). The gameplay sections (§1, §2, §8, §13) are *records* read off
`prototypes/core/machines.lua` **on master** — commits `5fe54fc`, `a28f572` and
`1fc943b`, merged as `19f7176`. If a number here disagrees with the code, the
code is right and this document is stale. The art sections are proposals.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **four rounds generated; `v4-sheet.png` is the best and is one measurement short — the gutter sockets are 0.41–0.53 tiles against 0.80. See §17** |
| 1 | Canonical view | square | Silhouette approved against §3 and §15; **no flange painted anywhere** | blocked on 0 |
| 2 | Idle plate (unlit) | square | Same machine, nothing lit | blocked on 1 |
| 3 | Directional frames | — | **n/a — §5.** One plate; the engine rotates the ports, measured | — |
| 4 | Glow plate | square | Differenced against stage 2 (Appendix C) | blocked on 2 |
| 5 | Working animation | square, 12-frame sheet | The coupling reads as turning, and frame 0 equals the plate byte for byte | blocked on 2 |
| 6 | Icon | square | Legible at 32 px, and the teal survives at 16 px as an area | blocked on 1 |

### Where generation happens

Browser — ChatGPT's image tool, `tools/generate-building-art.py <spec> --list`
for the prompt text. Template Appendices B and C apply in full. Concepts go to
`concept/reaction-plant/<tag>-<slug>.png`; nothing enters `graphics/` without
sign-off. Stage 5 is built with `tools/build-animatorio-layers.py` against the
Animatorio checkout (`~/git/Animatorio`, or `$ANIMATORIO`), which punches the
window out of a one-frame housing and verifies every recomposited frame against
Animatorio's own.

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
`advanced-circuit`, 8 s — the Helium Concentrator's price, for the reason the
code gives: a 3×3 shell with fluid ports on it, built of plate, pipe and enough
circuitry to meter what goes through.

**Locale (already written, `locale/en/strings.cfg`):**
*"Precipitates the pool's isotope into cells. It will take no other work, and
nothing else will take this."* /
*"Solution in one port, vent gas in the other, and a cell out on the belt. The
planet's whole power supply runs through it."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| **Tile Size** | 3×3. Sprite target 3.00 tiles wide and not less than 3.00 tall — §11 |
| **Collision Box** | `{-1.4,-1.4} → {1.4,1.4}` (`BOX_3x3`; the vanilla chemical plant's 1.2 is overridden) |
| **Selection Box** | `{-1.5,-1.5} → {1.5,1.5}` (`SEL_3x3`) |
| **Placement Restrictions** | `pressure` min 1, max 9 — the Core's surface only. `fast_replaceable_group` and `next_upgrade` cleared by `derive.from` |
| **Rotation** | **4-way, always, including with no recipe set.** No `not-rotatable` flag. The ports turn with the entity: the two inputs sit on the faced side and the output opposite. Measured in all four directions on 2.1.19 |
| **Crafting Category** | `sae-reaction` — private both ways: a vanilla chemical plant cannot make the Core's fuel, and this plant cannot run chemistry |
| **Crafting Speed** | 1 (`crafter` default) |
| **Energy Consumption** | **1500 kW working.** Standby is the chemical plant's inherited `drain`; re-read off a dump before this line is treated as a record |
| **Energy Type** | electric, `secondary-input`. No visible connector |
| **Module slots** | 3, all effects allowed |
| **Health and resistances** | `max_health = 300`, **no resistances** — both inherited from the vanilla chemical plant, which declares none |
| **Fluid Connectors** | **2 in, 1 out**, `volume 1000` each. North `{-1,-1}` and `{1,-1}`, south `{0,1}`. Full table in §8 |
| **Hatch Connectors** | None — this entity type has no such concept |

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
| **No recipe set** | **all three boxes and all three stubs.** It keeps whatever direction it is given, and a pipe laid against the output face joins |
| **`sae-radiant-precipitation`** | **the two input boxes only** — the recipe's products are solid, so the engine drops the output box whatever the flag says. No output stub. Still rotates |
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

**The wrong machine it must not be:** **vanilla's chemical plant**, whose sprites
it is wearing right now (`derive.placeholder_art(p, "wears chemical-plant's
sprites until its plate exists")`). Two chimneys over a low shed with four
painted flanges is the lazy read, and it is wrong three ways: there is no air
here so there is no exhaust; the ports are the engine's and must not be painted
anywhere; and the chemical plant is a *tidy* machine where this one is hour-one
kit.

**The second wrong machine, and the nearer danger:** **our own Helium
Concentrator.** Both are 3×3 chemical-plant derivatives built round a drum, both
sit on the Core, and without deliberate separation the player gets two machines
they cannot tell apart. Four axes, all four in the prompt:

| | Helium Concentrator | Reaction plant |
| --- | --- | --- |
| Proportion | tall; the drum is two thirds of the height | **squat — the drum is wider than it is tall** |
| Tier / finish | 3: smooth, sealed, cryogenic jacketing | **0: riveted, bolted, cast, mechanism showing** |
| Colour | hot orange below, frost above, split at the waist | **radiant green-white in three low sight slots, teal paint on the roof, nothing else** |
| Feature | a frost-jacketed gas riser leaving the top | **an exposed agitator drive turning on the crown** |
| Ports | painted into its own plate, three faces, fixed | **drawn by the engine, and they move when you turn it** |

**Primary Visual Theme:** heavy industry improvised on site — a shielded batch
reactor bolted together out of plate.

**Overall Appearance,** bottom to top in the order a prompt needs:

1. A **continuous bolted service gutter** running right round the machine at the
   very edge of the 3×3 footprint: a shallow channel of riveted plate, identical
   on all four sides, with short capped stubs at regular intervals and **no
   feature that names one face over another**. This is where the engine's pipe
   stubs land, and its uniformity is a hard requirement — §8.
2. A low **skirt of riveted plate** rising off the gutter, with hazard tape worn
   off the corners.
3. The **precipitation drum**: a squat cylinder filling most of the 3×3, **wider
   than it is tall**, its shell carried in three heavy **lead shield bands**
   strapped round it and bolted at visible lugs. Three narrow horizontal **sight
   slots** low on the near shoulder, and the only light on the machine behind
   them.
4. On the crown, an **exposed agitator drive**: a cast motor block, an open gear
   train, and between them a **free-turning spider coupling** with a clear gap
   all the way round it. This is the moving part, and §6.2 is why it is drawn
   free. Its **guard is painted teal**, and it is one of only two teal things on
   the building.
5. Off to one side of the roof, service furniture that does not have to be
   symmetric: a **teal inspection-hatch cover**, a cable trunk down to the skirt,
   a gauge cluster, ladder cleats.

**Silhouette:** a squat banded drum with one small piece of open machinery
turning on top of it. At map zoom it is a low dark disc inside a square gutter —
exactly what the Helium Concentrator is not, and never to be confused with it or
with a storage tank.

**Visual Complexity:** Medium-high, concentrated in the shield bands, their lugs
and the drive head. The gutter is deliberately plain.

**Visual Age:** **Primitive/Industrial — tier 0.** Riveted and bolted plate, cast
housings, exposed gears, weld seams, hazard tape, wear and rust staining. Nothing
flush, nothing seamless, no indicator lamps other than the one the engine tints.

## 3.2 Key Visual Features

* **Three lead shield bands** strapped round the drum, each bolted through a
  raised lug, plainly a duller and cooler metal than the shell.
* **Three narrow sight slots** low on the drum's near shoulder, radiant
  green-white showing through them and nowhere else.
* **An exposed spider coupling** turning between a cast motor block and the
  drum's crown bearing, drawn free with a visible gap all round.
* **A continuous bolted service gutter** at the footprint edge, identical on all
  four sides and carrying no paint at all.
* **Teal paint on the roof only** — the drive guard and the inspection-hatch
  cover, two solid areas and nothing else.

### Signature Feature

**The banded drum with its drive turning on top.** It renders the mechanic — a
sealed batch vessel that has to be stirred, shielded because what comes out of it
is hot in the other sense — and it is the one part legible at one tile.

## 3.3 Colour Palette

| Role | Hex | Confined to |
| ---- | --- | ----------- |
| Drum shell and skirt | `#4A463F` → `#6E685C` | the mass of the building |
| Lead shield bands | `#5A5A60` → `#7A7A80`, cooler and duller than the shell | the three bands and their lugs only |
| Shielding collars, bearing housing | `#3B3B40` | crown bearing, motor block |
| Copper and brass | `#8A5A32` → `#C88A4A` | **used freely** on the cable trunk, the gutter's joints, fittings and lugs. This is what keeps the building warm; rationing it is how a plate lands under vanilla's saturation floor (template Appendix B, note 3a) |
| Radiant light | `#A8E8C0` → `#E8FFF0` | **the three sight slots only.** The same green-white as the radiant fuel icon, the radiant chunk and the radiant generator's throat — one family |
| **Paint accent** | **works teal `#2A7F7A`** | **the roof only: the drive guard and the inspection-hatch cover.** Nothing at the footprint edge, nothing on the gutter, nothing on the skirt |
| Status lamp | engine-tinted | one lens on the roof, `apply_tint = "status"` |

**No orange anywhere** — orange is heat and nothing here is hot. **No frost, no
pale blue** — that is the Concentrator's and the Crust Tap's. **No red, no
magenta** — see the accent note.

**Teal is roof-only, decided 2026-09-17, and it is a rule about the edge as much
as about the roof.** Paint at the footprint edge would sit where the engine
stamps its own stubs and grey covers, so a painted gutter corner would be
half-covered by engine hardware in some directions and not in others — and the
gutter's whole job is to look the same on every side (§8). The accent goes on the
two service surfaces a person actually opens, both of them on the roof, and the
gutter carries copper and bare metal only.

**Every accent is confined, and here the gap has to be argued in *value*, not
only in hue.** Teal `#2A7F7A` is hue 176°, saturation 0.67, **value 0.50**. The
radiant light `#A8E8C0` is hue 142° at **value 0.91**. Thirty-four degrees of hue
is not much, so what separates them is that one is a dark matte paint and the
other is a bright emissive light, and they are at opposite ends of the machine:
**paint on the roof, light low on the drum's near shoulder**, with the whole
height of the drum between. They must never be adjacent, never overlap, and the
teal must never be given a bloom or a rim of light — a lit teal edge would read
as a cold version of the process light and collapse the distinction the palette
rests on.

Copper sits on the skirt and gutter and is 165 RGB units from the teal, so that
pair needs no special handling; the nearest thing to the teal on the whole
building is the shell itself at 78, which is what makes a teal guard read as a
patch rather than as a shadow.

**`#2A7F7A` is the paint, not what the plate measures.** Chipped, dusted and in
full sun on the roof, it renders at about `#54736B` (hue 165°, saturation 0.26,
value 0.45), measured off the Blender plate on 2026-10-01. That is within 0.02 of
the teal on `v2-sheet.png`'s main view (`#4D6D66`), so the weathering is the
concept's, not a drift from it. On the plate the teal sits 24 RGB units from the
lead bands, so there it is held apart by hue, as the only blue-green on the
building, not by distance. Every measurement above is taken on the clean paint,
and the icon keeps it: the icon render paints the two teal surfaces without wear
or dust, so the 16 px area carries `#2A7F7A`'s saturation.

---

# 4. Factorio Visual Style

### Required characteristics

* [ ] 45-degree top-down Factorio perspective — named in the prompt, in those words
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

**The angle clause.** 3×3 and **low** — a squat drum under two tiles. Name the
camera exactly: *"the game's characteristic 45-degree top-down perspective"*, and
**do not add the tall building's leaning clause**. Mostly roof, a shallow near
face, the square gutter reading as a **square and never as a diamond**.

### Technology tier and visual register

**Tier 0 — foothold.** `sae-radiant-power` hangs directly off Core Survey on a
craft-item trigger, so this is among the first four or five machines a player
builds. Riveted and bolted plate, cast housings, an exposed gear train, weld
seams, hazard tape, rust staining, visible wear. **Do not tidy it up**, and do not
let "handles a radioactive isotope" pull it toward tier-3 sealed plant: the
shielding here is lead sheet strapped on with bands and bolted, which is what a
foothold crew would actually do. It is also the clearest separator from the
Helium Concentrator, which is tier 3 and should look it.

### Style Reference Buildings

1. `assembling-machine-3` — the house camera, **and the port convention**: its
   fluid stubs are the engine's, drawn at the tile edge over a plate that paints
   no flange. Exactly this building's arrangement, and the reference to lean on
   hardest.
2. `foundry` — a big Space Age machine at the current standard: the finish and
   detail density to match.
3. `chemical-plant` — **camera reference only.** It is §3.1's anti-read: take the
   camera and the sense of scale, and nothing of the design — not the chimneys,
   not the red-and-white paint, and not the painted flanges.

**Reason for references:** attach all four of
`tools/extract-style-references.py`'s set under the standing disclaimer (*match
the camera, rendering, finish and level of detail; do NOT copy the design, shape,
colours or components*), with the chemical plant labelled as above.
`electromagnetic-plant` and `rocket-silo` come in the same set and bracket the
camera range; this building sits at the flat end of it. Also attach **our own
Helium Concentrator plate** as a projection example — its front edge is parallel
to the bottom of the frame — telling the generator to copy its projection exactly
and nothing else about it.

---

# 5. Building Orientation

## Required Directions

* [x] North · [x] East · [x] South · [x] West — **the entity rotates, and keeps rotating**
* [ ] but **one plate is drawn**, not four

**Direction count:** `4` in the prototype, `1` in the artwork. **Settled by Liam,
2026-09-17:** the fluid ports rotate with the entity and the building itself does
not turn. No `not-rotatable` flag; the code carries none, and
`fluid_boxes_off_when_no_fluid_recipe = false` exists precisely so that a plant
with no recipe still has boxes to rotate (§2).

**What actually differs between directions: nothing in the sprite.** Only the
engine's own pipe stubs and covers move, because `pipe_picture` is vanilla's
`assembler2pipepictures` rather than an empty sprite. **Measured on 2.1.19 in all
four directions**: the two inputs sit on the faced side and the output opposite.
So the one-plate answer is verified behaviour, not an inference from the
prototype.

**The consequence, and it is the biggest single art constraint on this
building:** the plate cannot carry any feature that names a face. Nothing in the
still art has a facing, so there is nothing to draw four times — which is
precisely what buys a rotatable machine for one plate instead of the Crust Tap's
four.

**And nothing in the design may quietly re-introduce a facing.** A porch, a
loading bay, a stepped-down deck, an asymmetric skirt or a run of pipework at one
edge would each make three of the four rotations look wrong. The gutter in §3.1
exists to prevent exactly that, and it is why the teal is on the roof rather than
at the corners. Roof furniture is exempt: it stays put under rotation and reads
fine from any side, as vanilla's own assemblers show.

---

# 6. Sprite Assets Required

## 6.1 Slots

| Asset         | Required | Directions |
| ------------- | -------: | ---------: |
| Main building |        ✓ |          1 |
| Shadow        |        ✓ |          1 |
| Idle state    |        ✓ |          1 |
| Working state |        ✓ |          1 |

**Idle is authored, not assumed.** The idle plate is this machine with the sight
slots **dark**, the coupling stopped, and the status lamp the only thing the
engine tints. A generator returns everything lit; the idle plate is made by taking
the light away, and that contrast is most of what makes the working state read.

**Engine limits worth stating.** The prototype cannot show buffer levels, which
port is carrying which fluid, or how far through a batch it is. The sight slots
therefore glow at a constant brightness while crafting and are dark otherwise —
never drawn as a rising level, because no hook would drive one. The status lamp is
the only state the engine will tint.

**And the plate has to read correctly in two port states, which are the two a
player meets** (§2, measured on 2.1.19):

| State | What the engine draws |
| --- | --- |
| No recipe set — a plant just placed | **all three stubs**, on whichever direction it was given |
| `sae-radiant-precipitation` | **two input stubs on the faced side, and no output stub** |
| A future stage-3 fluid recipe | all three again |

**There is no state in normal play where the machine stands with no stubs at
all.** That is the practical effect of `fluid_boxes_off_when_no_fluid_recipe =
false`, and it removes a worry the earlier drafts of this document carried. What
it does *not* remove is the uniform gutter: stubs still appear and disappear
between the two-stub and three-stub states, and they still move when the machine
is turned, so no tile edge may be drawn as special.

## 6.2 Animation Layers — what moves, decided here

| Layer          | Required | Animated | Frames |
| -------------- | -------: | -------: | -----: |
| Main structure |        ✓ |       No |      1 |
| Machinery      |        ✓ |        ✓ |   **12** |
| Pistons        |        — |        — |      — |
| Belts          |        — |        — |      — |
| Fans           |        — |        — |      — |
| Glow           |        ✓ |       No |      1 |
| Steam          |        — |        — |      — |

**What moves: the spider coupling on the crown, and nothing else.** It passes the
separability test, which is the only test: in the still it is drawn **free**, with
a visible gap all the way round and nothing bridging it to the motor block or the
crown bearing — no spokes, no hose, no bracket, no cable across that gap. Behind
it, the crown bearing plate and the drum roof are drawn **complete**, because that
is what the coupling uncovers as it turns. A sheet that comes back with the
coupling welded to its housing — the Ballast Drill's failure — is a reject at
stage 0, not a fix at stage 5.

**Its size is not a consideration.** The share-of-box gate was withdrawn on
2026-09-10 and must not be reintroduced. The only question asked here is whether
the part could be lifted out of the picture.

**It is also the one moving part that survives rotation:** a coupling on the crown
has no facing, so it needs drawing once. A moving part at an edge would have
needed four sheets.

**Twelve frames, not thirty-two.** Six-fold symmetry means 60° is the whole loop:
twelve frames at 5°. More is duplicates — the arithmetic that cut the Dross
Classifier's shake to twelve.

**The steam row is struck.** No air here: no flame, no exhaust, no smoke, no steam
plume, ever.

**No pistons, no belts, no fans, deliberately.** A batch precipitator has no
stroke and no cycle start, so the loop is seamless; a visible seam would read as a
stutter.

**The glow is not animated.** One static glow plate drawn only while crafting via
`working_visualisation`, so the engine gives the running-versus-stopped tell and
the art never implies a state it cannot know.

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

**Shadow:** cast to the lower right, synthesised off the plate's own alpha with
`kx 0.79, ky 0.25` (Appendix C). The Core has no day-night cycle to move it. A
squat building's shadow sits close to its plate, so it needs far less extra canvas
than the Arc Mast did — but it still gets its own `draw_as_shadow` sheet, never one
baked into the colour layer.

**Base:** the bolted service gutter and the riveted skirt. This is the
ground-contact plate and it is what `shift` is anchored on.

**Main Structure:** the drum, its three lead bands and their lugs, the sight-slot
housings, the roof furniture.

**Static Machinery:** the motor block, the fixed half of the gear train, the crown
bearing, the gauge cluster, the cable trunk.

**Pipes:** **None — deliberately.** Every port on this building is drawn by the
engine (§8). The plate draws no flange, no stub and no pipe run at any of the three
port tiles, nor anywhere else at the footprint edge.

**Lighting:** one status-lamp lens on the roof, cut white from the plate's own
canvas so it registers by construction, `apply_tint = "status"`, `always_draw =
true` — the Ring Mast's pattern, `always_draw` because a lamp that only appears
while working cannot report that the machine has stopped, which is the one thing it
exists to say.

**Glow:** the three sight slots, recovered by difference from a lit twin of the
approved unlit plate (`tools/derive-glow.py`), never drawn on transparency. It may
**not** be merged into the base: it is the working-versus-idle read. **The teal is
not in this layer and must not appear in it at all** — paint never glows.

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

Read straight off `machines.lua` on master. Positions are tiles from the entity
centre on a 3×3, given for direction north; all three turn with the building.

| Fluid box | `production_type` | `direction` | `position` | Which tile edge | volume |
| --- | --- | --- | --- | --- | --- |
| input 1 | `input` | north | `{-1, -1}` | north face, left (west) column | 1000 |
| input 2 | `input` | north | `{ 1, -1}` | north face, right (east) column | 1000 |
| output | `output` | south | `{ 0,  1}` | south face, centre column | 1000 |

All three: `pipe_picture = assembler_pictures.assembler2pipepictures`,
`pipe_covers = derive.pipe_covers()`, `always_draw_covers = false`,
`secondary_draw_orders = { north = -1 }`. The entity sets
`fluid_boxes_off_when_no_fluid_recipe = false` (§2).

## Energy

| Flow | Location | Connection Type |
| ---- | -------- | --------------- |
| in | no visible connector | electric network, `secondary-input`, 1500 kW |

### Hard geometric constraints

Seven, and six are the ports. Every one can be got wrong at stage 0 and is
expensive afterwards.

1. **The plate draws no flange, stub or pipe at any tile edge.** `pipe_picture` is
   vanilla's assembler fitting, so the engine stamps its own stub at each exposed
   port and `pipe_covers` caps an unconnected one with a neutral grey cap on top
   of whatever the plate drew there. Anything painted at an edge is a second
   flange in the wrong place. **This is the exact inverse of the Helium
   Concentrator's spec**, whose three flanges are painted into its plate because
   its `pipe_picture` is emptied, and copying that precedent here is the single
   most likely error.
2. **The placeholder is expected to look wrong, and that is not a bug to file.**
   The chemical-plant sprites this machine wears paint flanges of their own at two
   north and two south positions, so today the engine's north stubs sit on top of
   those painted flanges, and the south stub — drawn whenever the plant has no
   recipe set — stands on solid body between the placeholder's painted southern
   pair. That is a stand-in artefact. **The real plate paints none**, and the way
   to tell the design is right is that this artefact becomes impossible.
3. **No tile edge may be drawn as special**, because the ports move — measured in
   all four directions. A machine that looks purpose-built at two adjacent tiles
   looks wrong the moment it is built facing east. Hence the continuous, identical
   gutter: **the plate must be drawable with a stub at any of the twelve edge tiles
   and look right.** It is also why no paint goes at the edge (§3.3).
4. **The plate must read with two stubs and with three** — §6.1's table. The
   no-stub case has gone away with
   `fluid_boxes_off_when_no_fluid_recipe = false`, so the gutter no longer has to
   carry the machine on its own; but stubs still appear, disappear and move, so it
   must not look like a socket rail waiting to be filled either.
5. **North stubs are drawn behind the machine.** `secondary_draw_orders = { north
   = -1 }` — so the drum and skirt must stand back far enough from the edge that a
   stub drawn behind them still reads. This applies to whichever face is north at
   the time, which is another reason the gutter is uniform.
6. **Nothing on the plate may name which port takes which fluid.** Box assignment
   follows the recipe's ingredient order: under `sae-radiant-precipitation` the
   left input takes solution and the right takes gas, and under stage 3's dissolve
   (`4 spent cells + 50 crust gas`) the first fluid is the gas and the assignment
   swaps. A fluid box is a socket, not a fluid. The same rule forbids any tint,
   frost, stain, glow or fluid-coloured marking on or within half a tile of any
   edge tile — the building's signature lives on the drum, a tile back from every
   edge.
7. **Nothing crosses the collision box.** 3×3 at `±1.4`; the plate cut to **exactly
   3.000 tiles** wide. The Arc Mast's 3.14 on a 3-tile pitch is the standing lesson,
   and this is a machine players build in rows.

### Port size and style — the standing rule

**Wherever a fluid port is required, it matches the size and style of the chemical
plant's** (Liam, 2026-09-17). That is the house standard for a Core machine's
plumbing, and it is what a player's eye is already calibrated to.

On *this* building no port is painted, so the rule binds in two places rather than
one:

* **The space a port occupies is reserved at that size.** The engine stamps
  vanilla's assembler-2 fitting here, and it is the same size class as the chemical
  plant's own ports — measured off the vanilla sheets, the north stub is
  **52 × 20 source px at scale 0.5**, so about **0.8 tiles wide and 0.3 tiles
  deep**. Nothing on the plate may crowd that rectangle at any of the twelve edge
  tiles.
* **The gutter's own capped stubs are drawn to the same size and style**, so an
  engine-drawn port sits among them as one of the family rather than as a foreign
  object bolted on.

A port drawn smaller than the chemical plant's reads as a hose and a player will
not believe a pipe meets it; drawn larger, it swallows the engine's fitting and the
grey cover sits inside a mouth two sizes too big.

### Visual Requirement

The player tells inputs from outputs by the engine's stubs and the recipe tooltip,
not by the art, and the art must not pretend otherwise. **The most likely mistake
is an output chute**: a solid does come out of this machine, which makes a chute
feel natural, and it is exactly the promise the entity cannot keep — the cell comes
out wherever the inserter is, and a crafting machine has one output inventory
however many products a recipe lists. The second most likely is painting a flange
at two north tiles because the chemical plant reference has them painted.

---

# 9. Image Generation Prompts

**Canvas:** square for the plates and the icon, landscape 3:2 for the concept
sheet. Generate at the largest size available; we downscale. Transparent background
where supported, otherwise flat magenta `#FF00FF` — which is safe on this building,
because with the accent settled as teal there is no magenta anywhere on it.

## Concept Sheet Prompt

```text
FACTORIO SPACE AGE BUILDING -- CONCEPT SHEET

== CAMERA ==
Match the attached vanilla sprites exactly: the game's characteristic
45-degree top-down perspective, steeply down from above, MOSTLY ROOF with
only a shallow near face. Square to the tile grid: the square base must read
as a SQUARE, never as a diamond. Not rotated corner-on. Not a flat front
elevation. This building is low, so do NOT lean it toward the viewer.

== BUILDING ==
REACTION PLANT. Three tiles by three tiles, squat. A shielded batch reactor
that takes two fluids and precipitates a solid fuel cell out of them. It is
one of the very first machines a crew builds on this world, made on site out
of plate, and it should look it.

== FORM ==
- A continuous bolted service gutter runs right round the very edge of the
  three-by-three footprint: a shallow riveted channel, IDENTICAL on all four
  sides, with short capped stubs at regular intervals. Those capped stubs are
  the size and style of a vanilla chemical plant's fluid ports -- about
  four fifths of a tile across -- and no side of this machine is different
  from any other side.
- Above it a low riveted skirt, hazard tape worn off the corners.
- The mass of the building is a squat precipitation drum, WIDER THAN IT IS
  TALL, filling most of the footprint.
- Three heavy lead shield bands are strapped round the drum and bolted at
  raised lugs. The bands are a duller, cooler metal than the shell.
- Three narrow horizontal sight slots low on the drum's near shoulder, with
  cool green-white light showing through them and nowhere else.
- On the crown, an exposed agitator drive: a cast motor block, an open gear
  train, and between them a free-turning spider coupling. The coupling is
  drawn FREE, with a clear visible gap all the way round it and nothing
  bridging it to the motor or to the bearing beneath it.
- To one side of the roof: an inspection hatch cover, a cable trunk down to
  the skirt, a gauge cluster, ladder cleats.

== FINISH ==
Riveted and bolted plate, cast housings, exposed gears, weld seams, visible
wear and rust staining. Nothing flush, nothing seamless, no sealed composite
shells. Copper and brass are VISIBLE and used freely on the cable trunk, the
gutter joints and the lugs. This is what keeps the building warm.

== COLOUR ==
- Drum shell and skirt: #4A463F to #6E685C
- Lead shield bands: #5A5A60 to #7A7A80, duller and cooler than the shell
- Collars and bearing housing: #3B3B40
- Copper and brass, used freely: #8A5A32 to #C88A4A
- Radiant light, sight slots ONLY: #A8E8C0 to #E8FFF0
- Paint, on the drive guard and the inspection hatch cover and NOWHERE else:
  works teal #2A7F7A, a dark matte reflective paint, chipped and worn. Both
  painted parts are on the ROOF. It NEVER glows and has no bloom or rim light.
- The gutter, the skirt and every edge of the footprint carry NO paint at all:
  bare metal and copper only.
Reduce pale grey and rust-orange drift. No orange glow. No pale blue, no
frost, no ice. The teal paint is high on the machine and the green-white
light is low on the drum, with the whole height of the drum between them:
the paint is dark and matte, the light is bright and emissive, and they must
never touch.

== RULES ==
- Draw NO pipe, flange, stub, chute or port anywhere at the edge of the
  footprint, and no pipework running down the outside of the machine to reach
  it. The game draws its own pipe fittings; a painted one is a second fitting
  in the wrong place. The gutter must look finished with nothing attached to
  it.
- The gutter's own small capped stubs are the ONLY port-like shapes on the
  machine, and they are drawn at the size and in the style of a vanilla
  chemical plant's fluid ports -- about four fifths of a tile across -- so
  that the game's own fitting sits among them as one of the family.
- No output chute and no product anywhere: no cells, ore, powder, grit or
  debris on the ground, in bins, at chutes, on trays or spilling from the
  machine.
- No side of the machine may be a front: no porch, no loading bay, no stepped
  deck, no asymmetric skirt, no pipework at any one edge, and no paint at any
  edge.
- Nothing extends past the three-by-three footprint, and the machine sits
  squarely inside it.
- Must read as a squat shielded batch reactor, NOT as a chemical plant: no
  chimneys, no exhaust stacks, no smoke, no flame, no red-and-white paint,
  no painted flanges. And NOT as a tall ribbed separation drum with a riser.

== PANELS ==
Main view - a top view showing the square footprint and the plain uniform
gutter on all four sides - a close-up of the drive head showing the gap all
round the coupling - a close-up of a shield band and its bolted lug - a
lit/unlit pair - a layer breakdown - the in-game icon - a palette strip.

== OUTPUT ==
Title the sheet REACTION PLANT. Landscape, 3:2.
```

---

## Master Concept Prompt

```text
A squat shielded batch reactor for a factory-building game, three tiles by
three tiles, viewed from the game's characteristic 45-degree top-down
perspective: steeply down from above, mostly roof with only a shallow near
face, square to the tile grid so its square base reads as a SQUARE and never
as a diamond. It is low, so it is not leaned toward the viewer.

Bottom to top: a continuous bolted service gutter runs round the very edge of
the square footprint, a shallow riveted channel identical on all four sides
with short capped stubs at regular intervals; above it a low riveted skirt
with hazard tape worn off the corners; then the mass of the machine, a squat
precipitation drum wider than it is tall, filling most of the footprint,
carried in three heavy lead shield bands strapped round it and bolted at
raised lugs; three narrow horizontal sight slots low on the drum's near
shoulder; and on the crown an exposed agitator drive -- a cast motor block, an
open gear train, and between them a free-turning spider coupling drawn with a
clear visible gap all the way round it and nothing bridging it to the motor or
to the bearing beneath. To one side of the roof, an inspection hatch cover, a
cable trunk running down to the skirt, a gauge cluster and ladder cleats.

Proportion: the drum is about twice as wide as it is tall, and the whole
machine is no taller than it is wide.

Riveted and bolted plate, cast housings, exposed gears, weld seams, rust
staining and visible wear; nothing flush or seamless. Drum shell and skirt
#4A463F to #6E685C; lead bands #5A5A60 to #7A7A80, duller and cooler than the
shell; collars and bearing housing #3B3B40; copper and brass visible and used
freely on the cable trunk, gutter joints and lugs, #8A5A32 to #C88A4A; dark
matte chipped teal paint #2A7F7A on the drive guard and the inspection hatch
cover, both on the roof, and on nothing else -- the gutter, the skirt and every
edge of the footprint carry no paint at all. Reduce pale grey and rust-orange
drift.

State: running. Cool green-white light #A8E8C0 to #E8FFF0 shows through the
three sight slots and NOWHERE else. Nothing else on the machine glows -- not
the teal paint, which is matte and has no bloom and no rim light, not the
copper, not the gutter, not any edge of the footprint. The paint sits high on
the machine and the light sits low on the drum, and they do not touch.

Draw no pipe, flange, stub, chute or port anywhere at the edge of the
footprint, no pipework running down the outside of the machine to reach it, and
no product anywhere. The gutter's own small capped stubs are the only port-like
shapes on the machine and are drawn at the size and in the style of a vanilla
chemical plant's fluid ports, about four fifths of a tile across. No side of the
machine is a front. Must
read as a squat shielded batch reactor, not as a chemical plant: no chimneys,
no exhaust stacks, no smoke, no flame, no red-and-white paint, no painted
flanges; and not as a tall ribbed separation drum with a riser, and not as a
storage tank.

Painted semi-realistic industrial game art, strong readable silhouette,
3 tiles wide and 3 tiles tall, fully transparent background, no text,
no logos, no characters, no UI, no ground texture, no background scenery,
no baked drop shadow.
```

---

## Directional Prompts

### North

```text
Not required — see §5. One plate; the engine rotates the ports.
```

### East

```text
Not required — see §5.
```

### South

```text
Not required — see §5.
```

### West

```text
Not required — see §5.
```

---

## Layer Prompts

### Main Structure

```text
[Master prompt] State: STOPPED and completely unlit. The three sight slots are
dark, closed and cold -- no green, no white, no bloom, no light spill on the
shell around them. Nothing anywhere on the machine emits light, and the teal
paint on the drive guard and the inspection hatch cover is matte and unlit as
before. Everything else about the machine is unchanged: same shapes, same
components, same materials, same colours, same camera, same position in frame.
```

### Glow / Lighting

```text
The attached image is the approved unlit plate of this machine. Return the
SAME image, pixel for pixel identical in shape, position, scale, camera,
components and materials, with one change only: the three sight slots low on
the drum's near shoulder are lit from inside with cool green-white light,
#A8E8C0 to #E8FFF0, with a short soft bloom on the shell immediately around
each slot. Nothing else lights up: not the teal paint on the roof, which stays
matte with no bloom and no rim light, not the copper, not the gutter, not the
drive head, not any edge of the footprint. Do not redraw, redesign, recolour,
move or re-scale the machine. Fully transparent background, no text, no ground
texture, no baked drop shadow.
```

---

# 10. Image Processing

### Processing Checklist

* [ ] Remove background
* [ ] Remove unwanted shadows/background objects
* [ ] Crop to building
* [ ] Correct perspective
* [ ] Match Factorio scale
* [ ] Convert to appropriate resolution
* [ ] Align to tile grid
* [ ] Separate layers
* [ ] Generate directional sprites — **n/a, §5**
* [ ] Generate spritesheets
* [ ] Optimise PNGs

The crop is driven by §8, and §8's driver is the gutter: **the outer edge of the
drawn gutter is the 3.000-tile line**, and the plate is cut to it. Everything else
falls where it falls. `--bottom-margin` so alpha is zero on all four edges.

---

# 11. Sprite Dimensions

**Provisional — no plate exists. Re-measure every line once stage 1 passes.** These
are commissioning targets, not measurements.

**Tile Size:** `32` px in-game · **Scale:** `0.5` → `64` source px per tile

| | tiles | in-game px | source px |
| --- | --- | --- | --- |
| **Building width** | 3.000 exactly | 96 | **192** |
| **Building height** | 3.00–3.20 (target) | 96–102 | 192–205 |

**Sprite Width / Height:** `200 × 201` source px provisional — the Helium
Concentrator's cut canvas, 4 px of clear margin each side of a 192 px building,
which satisfies the alpha-zero-at-every-edge check.

**Shift:** `util.by_pixel(0, 0)` provisional, anchored on the **gutter**, which is
the ground-contact plate — not on the drum's crown. Re-derive from the measured
rows the gutter occupies.

**Aspect target: not below 1 : 1.00.** Vanilla's `assembling-machine-1-base.png` is
188 × 180 at 1 : 0.96 and its storage tank is 1 : 1.10; a plate wider than it is
tall leaves bare ground between neighbours. A squat drum is exactly the shape that
comes back too wide, so this is the first number to read off `--report`.

**Fixed points:** the outer edge of the gutter must land on the 192-px width line,
±0 — cut, not persuaded. **No engine-pinned pixel coordinate on this building**: it
has no `lightning_strike_offset`, no heat connections and no
`vector_to_place_result`, and because the ports are the engine's there is no flange
position for the art to hit either. The port tiles constrain what the plate must
*not* contain, not where anything must land.

**Spritesheet Width / Height:** working animation 12 frames of 200 × 201 at
`line_length = 6` → **1200 × 402** px. Glow: one frame, 200 × 201. Status lamp: one
frame, 200 × 201. Shadow: its own canvas, wider than the plate, anchored left with
half the extra width added back in `shift`; ~260 × 210 expected for a building this
low, to be measured.

**Density target:** edge density at or above vanilla's chemical plant, **0.164**.
The Helium Concentrator's cut plate reached 0.262 on one instruction — *more
hardware, without changing the shapes* — held in reserve here. Measure a cut plate,
never the sheet (Appendix B, 3a-i).

---

# 12. File Structure

```text
├── concept/
│   └── reaction-plant/
│       ├── building-spec-reaction-plant.md
│       └── [tag]-[slug].png              every generated concept, round by round
└── graphics/
    └── entity/
        └── reaction-plant/
            ├── base.png                  the machine, static, unlit
            ├── base-shadow.png           draw_as_shadow
            ├── drive.png                 12-frame coupling sheet (housing window)
            ├── slots-glow.png            the sight slots, differenced
            └── status-lamp.png           white lens, engine-tinted
```

Nothing moves to `graphics/` without sign-off. Smoke and particles are not sprites
here and are not wanted at all — there is no atmosphere.

---

# 13. Factorio Prototype

**Prototype Type:** `assembling-machine` · **Prototype Name:** `sae-reaction-plant`

### Graphics

```lua
-- Provisional. Canvas and shift are re-measured off the approved plate, and the
-- set is attached with derive.own_graphics so the vanilla audio cues that name
-- the vanilla animations go with the art they were cued to.
graphics_set =
{
  animation =
  {
    layers =
    {
      { filename = RP .. "base.png",        width = 200, height = 201, frame_count = 1, shift = { 0, 0 }, scale = 0.5 },
      { filename = RP .. "base-shadow.png", width = 260, height = 210, frame_count = 1, shift = { 0, 0 },
        draw_as_shadow = true, scale = 0.5 }
    }
  },
  working_visualisations =
  {
    -- The coupling. Housing window punched by tools/build-animatorio-layers.py;
    -- frame 0 must equal the plate byte for byte.
    {
      animation =
      {
        filename = RP .. "drive.png", width = 200, height = 201,
        frame_count = 12, line_length = 6, animation_speed = 0.4,
        shift = { 0, 0 }, scale = 0.5
      }
    },
    -- The sight slots. Drawn only while crafting, which is the whole tell.
    {
      animation =
      {
        filename = RP .. "slots-glow.png", width = 200, height = 201,
        frame_count = 1, draw_as_glow = true, shift = { 0, 0 }, scale = 0.5
      }
    },
    -- The status lamp. always_draw, because a lamp that vanishes when the
    -- machine stops cannot report that the machine has stopped.
    {
      always_draw = true, apply_tint = "status",
      animation =
      {
        filename = RP .. "status-lamp.png", width = 200, height = 201,
        frame_count = 1, draw_as_glow = true, shift = { 0, 0 }, scale = 0.5
      }
    }
  }
}
```

**No `flags` line, and no `not-rotatable`.** Settled 2026-09-17. If one ever
appears here, this spec is wrong and §5 has to be re-opened before it goes in.

### Other Visual Properties

```text
Graphics set:          to be written; the table above, once measured, via derive.own_graphics
Shadow:                own draw_as_shadow layer, synthesised kx 0.79 ky 0.25
Working Visualisation: coupling (12f) + slots glow (1f) + status lamp (1f)
Lights:                none beyond the glow layer
Fluid Boxes:           2 in (north, {-1,-1} and {1,-1}) + 1 out (south, {0,1}),
                       volume 1000 each; pipe_picture =
                       assembler_pictures.assembler2pipepictures,
                       pipe_covers = derive.pipe_covers(),
                       always_draw_covers = false,
                       secondary_draw_orders = { north = -1 },
                       fluid_boxes_off_when_no_fluid_recipe = FALSE, this plant alone
Circuit Connections:   inherited from chemical-plant
Remnants:              the chemical plant's, reused on purpose -- see below
```

**What is inherited, and why none of it is a follow-up.** `derive.lua` states the
policy: it clears the classes of inherited field that were invisible in the Lua and
wrong in a dump, and it deliberately leaves alone *"the stuff that is legitimate to
reuse: open/close and working sounds, corpses and explosions. Reusing vanilla audio
is ordinary modding."* So `corpse = "chemical-plant-remnants"` and `dying_explosion
= "chemical-plant-explosion"` stay.

The sound problem that used to be a follow-up is handled by the tool rather than by
this document: `derive.own_graphics` strips `working_sound.sound_accents` and any
`main_sounds` gated on a named vanilla working visualisation at the moment the new
`graphics_set` is attached, because a gated sound cannot survive the art it was cued
to. **Nothing here is owed to the coder on that front** — it happens automatically
the day this building's plate lands.

The `icon` is still the chemical plant's, taken via `entity_icon()`; the item
follows the entity by design, so the two can never disagree. It changes when §14
ships.

---

# 14. Icon

**Icon Required:** ✓ · **Icon Size:** `64×64`, cut to a 120×64 mipmap strip by
`tools/key-icons.py`.

**Icon Concept:** the banded drum, head-on, with **one** shield band and its bolted
lug, **one** green-white sight slot, and the **teal drive guard** as a visible patch
on top. Everything else is dropped: the gutter, the gear train, the cable trunk, the
gauges, the second and third bands. Key it off the **lit** plate so the green-white
is in the icon.

**Bring the inspection-hatch cover in if the guard alone is not enough.** It is the
only other teal surface on the building, it is on the roof and therefore visible at
this angle, and it is the honest way to make the accent an area — see the count
below.

### Why teal carries the icon, measured

Our ten building icons sit in a **nine-degree hue band**, mean pairwise RGB distance
**13.2**, closest pair **1.6** apart; vanilla's six production icons span **27°–98°**
at **32.6**. The cause is that the Core's palette is one warm iron-nickel body plus
copper, and the only things that break it are emissive. So the icon is separated by
a painted **area**, not by silhouette — our icons overlap at a mean IoU of 0.83 and
vanilla's own at 0.75, so silhouette is not the lever.

Works teal `#2A7F7A` is hue **176°**, saturation 0.67, value 0.50. Measured against
everything already spoken for:

| Against | Hue gap | RGB distance |
| --- | ---: | ---: |
| Service blue `#2E5A8C` (Whisker Comber) — **its nearest neighbour** | 36° | **41.3** |
| Signal yellow `#C8A23A` (Dross Classifier) | 132° | 174.0 |
| Radiant green-white `#A8E8C0` (this machine's own light) | 34° | 178.3 |
| Frost `#B8C4C8` (Concentrator, Crust Tap) | 19° | 176.1 |
| Violet `#6A5AC8` (field) | 73° | 107.5 |
| Heat `#D96B29` / copper `#C88A4A` | 154° / 146° | 193.9 / 165.5 |

**The number that matters is 41.3 against the closest existing accent**, which is
above vanilla's own mean pairwise separation of 32.6 and more than three times our
current mean of 13.2. Teal is a genuine widening of the band, not a shuffle inside
it.

### What roof-only paint does to the count, honestly

The template's measurement is distinct-hue pixels at 16 px, out of roughly 150 lit.
The painted machines score **11** (Dross Classifier) and **7** (Whisker Comber); the
light-only machines score **0–1**.

**Those two both spread their paint over three places.** The Dross Classifier's
yellow is on the eccentric-drive guard, the four spring caps *and* the drive-end
rail; the Whisker Comber's blue is on the hood band, the lid dogs and the drive
skirt's access panel. This building's teal is now on **two** surfaces, both on the
roof, and only one of them — the drive guard — was in the icon concept before this
decision. So the earlier draft's "target 7–11" was written against a larger painted
area than the building now has, and repeating it would be quoting a number for a
machine that no longer exists.

**The honest expectation is 5–8, and the target is ≥ 7.** The guard alone, drawn as
a solid cap on the drive head, is a smaller area than any of the two precedents'
three-part schemes. Two things recover it, both in the prompt above: draw the guard
as a **solid cap covering the whole drive head**, not an outline or a rim; and, if
the count still falls short, **bring the inspection-hatch cover into the icon** as a
second teal area rather than enlarging the guard past what the plate shows.

**Measure it rather than judging it.** If the finished icon counts **below 5**, the
teal has become a point and the icon goes back a round — that is the failure mode
this whole argument exists to catch, and it is not visible by looking.

### Icon Prompt

```text
A game inventory icon, square, on a fully transparent background: a squat
riveted metal drum seen from slightly above and in front, wider than it is
tall, with one heavy lead shield band strapped round its middle and bolted at
a raised lug. One narrow horizontal sight slot low on the drum glows cool
green-white, #A8E8C0 to #E8FFF0. On top of the drum, a small cast drive head
whose guard is painted a chipped reflective dark teal, #2A7F7A -- the paint is
a solid cap covering the whole guard, not a thin line and not an outline, it is
matte and it does not glow. Beside it on the roof, a small teal inspection
hatch cover in the same paint. Keep all the teal on top and the green-white
slot low, with plain dark metal between them so they never touch, and no paint
anywhere at the base of the machine. Drum body #4A463F to #6E685C, band
#5A5A60 to #7A7A80, a little visible copper #C88A4A at the lug. Bold, simple,
high contrast, readable at 32 pixels: no pipes, no flanges, no gutter, no
gears, no gauges, no cables, no product. Painted semi-realistic industrial game
art, fully transparent background, no text, no logos, no characters, no UI, no
ground texture, no background scenery, no baked drop shadow.
```

---

# 15. Visual QA Checklist

### Building

* [ ] Correct tile size — 3.000 tiles wide, measured, not judged
* [ ] Correct perspective — mostly roof, shallow near face, **not** leaned toward the viewer
* [ ] Square base reads as a square, not a diamond
* [ ] Correct scale
* [ ] Clear silhouette
* [ ] Looks like Factorio
* [ ] Matches the Core
* [ ] Inputs are visually understandable — by the engine's stubs, not by the plate
* [ ] Outputs are visually understandable — there is no output port to understand
* [ ] **Does not read as** the vanilla chemical plant — no chimneys, no exhaust, no red-and-white, no painted flanges
* [ ] **Does not read as** the Helium Concentrator — squat not tall, riveted not sealed, teal-and-green-white not frost-and-orange
* [ ] **Does not read as** a storage tank
* [ ] Tier 0 finish: rivets, bolts, cast housings, weld seams, wear. Nothing flush or seamless
* [ ] **No face is a front** — no porch, loading bay, stepped deck, asymmetric skirt, edge pipework or edge paint

### Ports — every line comes from §8

* [ ] **No flange, stub, pipe or chute drawn anywhere at the footprint edge**, and no pipework running down the outside of the machine to reach one
* [ ] The gutter's capped stubs are the **size and style of the chemical plant's fluid ports** — about 0.8 tiles across, matching the 52 × 20 source px fitting the engine stamps
* [ ] The rectangle each engine stub occupies is clear at every edge tile
* [ ] The gutter is identical on all four sides
* [ ] The plate reads correctly with **two stubs and with three** (§6.1)
* [ ] The drum and skirt stand back far enough for a north stub, drawn *behind* them, to read
* [ ] Nothing names which port takes which fluid
* [ ] No output chute, and no cell or product drawn anywhere
* [ ] No tint, stain or glow on or within half a tile of any edge tile

### Accent and glow

* [ ] The teal is on the **roof only**: drive guard and inspection-hatch cover, and nothing at the gutter, the skirt or any edge
* [ ] Each teal surface is an **area** — a solid cap or panel, not a line or an outline
* [ ] The teal does not glow, has no bloom and no rim light, and is absent from the glow layer entirely
* [ ] Teal and green-white are not adjacent anywhere, on the plate or in the icon
* [ ] The icon's teal scores **≥ 7 distinct-hue pixels at 16 px**, counted, and never below 5

### Directions

* [ ] North · [ ] East · [ ] South · [ ] West — one plate serves all four; the engine moves the ports
* [ ] All directions represent the same building

### Generated-art defects

* [ ] No baked drop shadow in the colour layer
* [ ] No ground plane or scenery
* [ ] Background is transparent or cleanly keyable
* [ ] Palette matches §3.3 rather than drifting pale and rust-orange; measured with `--report`, not eyeballed
* [ ] Nothing glows that §3.3 says is unlit

### In-Game

Place **at least three in a row**, set one to precipitation, leave one with no
recipe, and rotate one.

* [x] **The ports turn with the entity in all four directions, inputs on the faced side and output opposite** — measured on 2.1.19 by the coder, the reviewer and the tester
* [x] **With no recipe the plant carries all three boxes, keeps its direction, and a pipe at the output joins; with `sae-radiant-precipitation` the engine keeps the two inputs only and drops the output** — measured on 2.1.19
* [ ] The engine's stubs land on the gutter and look like they belong, in all four directions — **not checked; needs the real plate**
* [ ] An unconnected port's grey cover does not sit on top of painted geometry — trivially true once the plate paints nothing, but unchecked
* [ ] Shadow aligns, does not double, and is *visible* — brighten the screenshot and confirm it is actually there
* [ ] Inserters take the cell from any adjacent tile without the art implying one
* [ ] Neighbours do not overlap — measured, not judged: see Appendix C
* [ ] The building sits on its tile, not above it
* [ ] Recognisable beside the Helium Concentrator specifically
* [ ] Performance is acceptable

**Known and expected until the real plate lands:** the placeholder chemical-plant
sprites paint their own flanges, so the engine's north stubs sit on top of painted
flanges and the no-recipe south stub stands on solid body between the placeholder's
painted southern pair. Stand-in artefact, not a defect, and not to be filed (§8.2).

---

# 16. Final Asset Checklist

```text
[ ] Concept sheet
[ ] Master concept
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

### Final — the wording agreed, 2026-09-17

Two further changes on the same day. **The teal is roof-only** — drive guard and
inspection-hatch cover, nothing at the gutter or any edge — because paint at the
footprint edge would sit under the engine's own stubs and covers and would break the
gutter's sameness on four sides; §14's icon expectation was re-stated downward to
match the smaller area rather than quoting the old figure. And
**`fluid_boxes_off_when_no_fluid_recipe` is false on this plant alone**, so a plant
with no recipe keeps its boxes and can be turned: the no-recipe state now shows all
three stubs rather than none, measured on 2.1.19 by the coder, the reviewer and the
tester.

**The lesson worth keeping:** `pipe_picture` decides who draws the port, and it
decides half the art brief with it. Read it before writing §7 and §8, on every
building — twice now it has been the difference between a plate that paints flanges
and one that must not.
