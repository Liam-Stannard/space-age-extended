# Factorio Building — Art & Implementation Specification

**Template v2.** Copy to `building-spec-<name>.md` and fill it in *before*
commissioning art. v1 was a set of blanks; this version is opinionated, because
blanks turned out to be where the failures came from. Everything marked
**Rule** below was learned from a generation round that went wrong, and is
written down so it goes wrong once rather than every time.

Specs written against v1 (`building-spec-vent-pump.md`) remain valid — v2 only
adds §0, the Fill rules, and the appendices, and renumbers nothing.

## How to use this document

1. **Fill §1–§10 from the implemented prototype, not from your intentions.**
   Every gameplay number is read off the Lua and off the vanilla prototype it
   deep-copies. If a number here disagrees with the code, the code is right and
   this document is stale. The *art* sections are proposals; the gameplay
   sections are records.
2. **Fill §11 last.** A prompt written before §3, §5 and §8 are settled will
   produce a building that cannot be implemented.
3. **Then run §0.** Generate in the order given, gate by gate.
4. **Log every round in §19.** A spec whose iteration history is empty after a
   generation round is an incomplete spec.

## Machine contract — do not break these

`tools/generate-building-art.py` reads prompts straight out of this document,
so the *formatting* of §11 and §16 is an interface:

* Prompts live in fenced ` ```text ` blocks, the first one after each known
  heading.
* The headings it looks for are exactly: `## Concept Sheet Prompt`,
  `## Master Concept Prompt`,
  `### North`, `### East`, `### South`, `### West`, `### Main Structure`,
  `### Working Machinery`, `### Glow / Lighting`, `### Effects`,
  `### Icon Prompt`. Do not rename or re-level them.
* A block whose text begins `Not required` or `Do not generate` is skipped.
  Use that instead of deleting a heading.
* `[Master prompt]` at the start of a block splices the master in ahead of it.

---

# 0. Generation Contract

**Fill rule:** tick nothing here until the gate above it has actually passed.

Generate in this order. Each stage is a gate: a failure at stage *n* is fixed
before stage *n+1* is attempted, because every later asset inherits the
silhouette agreed at stage 1.

| # | Asset | Canvas | Gate before moving on |
| - | ----- | ------ | --------------------- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review — see below |
| 1 | Canonical view | `[portrait 2:3 / square]` | Silhouette approved against §3.1 and §17 |
| 2 | Main structure (unlit) | same | Same machine as stage 1, nothing lit |
| 3 | Directional frames | same | Only if §5 says >1 direction. One machine, rotated fittings |
| 4 | Glow plates | same | Aligns with stage 2 geometry |
| 5 | Effects plate | same | Reads at 1 tile, nothing leaves the shape |
| 6 | Icon | square | Legible at 32 px |

**Stage 0 is the cheapest review in the process.** One landscape image laid out
as a concept sheet — four directional views, the icon, a tile-grid top view,
close-ups, a layer breakdown, animation key frames, effects plates and a
palette strip, all in one frame. It is a *design* artifact, not production art:
it may carry labels and text, its layer thumbnails are illustrative rather than
usable, and nothing on it is at sprite resolution. What it buys is consistency
— every panel is drawn by one pass, so the four directions agree with each
other and with the icon before a single production plate exists, and colour
drift shows up against the palette strip immediately.

Approve the sheet before stage 1. A silhouette argument is far cheaper here
than four rounds into the directional frames.

**Stage 1 is the canonical source, and it is a sprite, not a picture.** No
labels, no sheet layout, no grid, no icon, no close-ups — just the machine,
isolated on transparency, at the highest resolution available. Every production
asset afterwards derives from *this file* by editing, not from the prompt by
re-generating. The concept sheet is reference only; nothing on it ships.

**Rule — one gate at a time.** Do not generate the layer plates from an
unapproved master. Every plate is drawn to fit geometry that the master
defines, and re-approving the master later invalidates all of them.

**Rule — stage 2 is not free.** It is the master prompt plus "nothing lit", so
skip it in round one and generate it only once the master is approved.

### Where generation happens

`[Browser (ChatGPT / image tool) / tools/generate-building-art.py]`

Both routes read the same §11 prompts. See Appendix B before using the browser
route — the composer imposes constraints the API does not.

### Round log

Record every round in §19. A round is: generate → review against §17 → write
the refinement → regenerate. Not "generate until it looks nice".

---

# 1. Building Overview

**Fill rule:** name the prototype type *and why that type* — the type is
usually load-bearing for a mechanic, and the art must not contradict it.

**Building Name:**
`[Name]`

**Internal Prototype Name:**
`[prototype-name]`

**Building Type:**
`[assembling-machine / furnace / mining-drill / lightning-attractor / etc.]`
`[— deep-copied from what, and what the type buys the mechanic]`

**Planet / Environment:**
`[Nauvis / Vulcanus / Fulgora / Gleba / Aquilo / custom]`
`[— and what actually gates it there: surface conditions, a resource, or
nothing but the absence of anywhere else to put it]`

**Purpose:**
`[What it does, in the terms the player experiences]`

**Technology Unlock:**
`[Technology, tier, prerequisites, and what it is researched on]`

**Recipe:**
`[Ingredients and craft time]`

---

# 2. Gameplay Dimensions

**Fill rule:** read every line off the prototype. Mark anything inherited as
inherited. If the sprite is bigger than the footprint — a tall building — say
so here and not only in §13.

**Tile Size:**
`[e.g. 3×3 — and the sprite's size, if different]`

**Collision Box:**
`[x1, y1] → [x2, y2]`

**Selection Box:**
`[x1, y1] → [x2, y2]`

**Placement Restrictions:**
`[Surface conditions / resource category / none — and whether fast_replaceable_group
and next_upgrade are cleared]`

**Rotation:**
`[4-way / 8-way / none — and what physically moves between directions]`

**Crafting Speed:**
`[value, or the equivalent rate for this entity type]`

**Energy Consumption:**
`[working draw, and standby drain]`

**Energy Type:**
`[electric / fluid / heat / lightning]`

**Health and resistances:**
`[max_health, resistances]`

---

# 3. Visual Design

## 3.1 Design Concept

**Fill rule:** this section exists to stop the building being a recolour. If it
is currently wearing a vanilla building's art, state plainly **what that
vanilla machine actually is** and **why this one is not that** — that sentence
is the brief.

**The wrong machine it must not be:**
`[The vanilla art it currently wears, or the obvious lazy read, and why it is wrong]`

**Primary Visual Theme:**
`[Heavy industry / cryogenic / high-voltage / recycling / etc.]`

**Overall Appearance:**
`[Shape and construction, described bottom to top in the order a prompt will
need them]`

**Silhouette:**
`[What makes it recognisable at map zoom, and what it must never be confused with]`

**Visual Complexity:**
`[Low / Medium / High — and where the detail is concentrated]`

**Visual Age:**
`[Primitive / Industrial / Advanced / Experimental]`

---

## 3.2 Key Visual Features

**Fill rule:** five features, each one a thing a generator can draw. "Looks
industrial" is not a feature; "four braided copper earthing straps at the skirt
corners" is.

* `[Feature 1]`
* `[Feature 2]`
* `[Feature 3]`
* `[Feature 4]`
* `[Feature 5]`

### Signature Feature

`[The one feature that makes it immediately recognisable — ideally the one that
renders a mechanic visible rather than decorating the box.]`

---

## 3.3 Colour Palette

**Fill rule:** hexes, not adjectives, and say where each colour is *confined*.
Take fluid and item colours from the prototypes so the building matches its own
UI. Where a colour is fixed by something vanilla (a lightning prototype, a
fluid tint), say so — it is not a free choice.

**Primary:**
`[hex range / material]`

**Secondary:**
`[hex / material]`

**Metal:**
`[warm or cold, and how desaturated]`

**Accent:**
`[hex, and what it is confined to]`

**Working Glow:**
`[hex, where, and whether anything glows at rest]`

**Warning / Status Lights:**
`[hex, what state drives it, or "decorative — the prototype offers no hook"]`

**Rule — every accent is confined.** State the gap between accents. Two
saturated colours allowed to meet make an unreadable middle, and generators
will blend them unless told not to.

---

# 4. Factorio Visual Style

### Required characteristics

* [ ] 45-degree top-down Factorio perspective — **named in the prompt, see below**
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

**Rule — name the angle, in these words: "the game's characteristic 45-degree
top-down perspective".** Say it early, in the first or second sentence.

This is measured, not stylistic. Prompts that named the angle that way produced
correct Factorio camera on the first attempt; prompts that avoided naming it and
described the geometry instead — "a fixed camera high above the horizon", "drawn
leaning toward the viewer" — produced flat side-on elevations three rounds
running, on a building whose whole silhouette depends on the camera. The phrase
is what these models associate with Factorio's look, and no amount of careful
description substitutes for it.

Two notes that do not change the rule:

* **"45-degree top-down" is a prompt token, not a measurement.** Factorio's
  camera actually sits nearer 60° above the horizon and is effectively
  orthographic. Use the true geometry when judging a result in §17; use the
  phrase when asking for one.
* **A tall building still needs one added clause.** Vanilla draws anything much
  above two tiles leaning toward the viewer so its sides show, while its base
  stays seen from above — the cheat used for the lightning collector, the big
  electric pole and the rocket silo. Name the angle *and* add that, rather than
  substituting the description for the angle. Never write "isometric": that one
  really does produce a different game.

### Style Reference Buildings

1. `[Building]`
2. `[Building]`
3. `[Building]`

**Reason for references:**
`[What to take from each — and, for any reference this building currently wears
as a recolour, what to take *nothing* of.]`

---

# 5. Building Orientation

**Fill rule:** get the direction count from the prototype, not from the
template's four checkboxes. Several entity types have no direction at all, and
generating four frames for one of them is pure waste.

## Required Directions

* [ ] North
* [ ] East
* [ ] South
* [ ] West

**Direction count:**
`[1 / 4 / 8]`

**What actually differs between directions:**
`[Which fittings move, and what stays identical]`

**Rule — four arrangements, not four viewpoints.** The camera never moves in
Factorio. Ask for the same machine with its fittings rotated on a fixed camera.
A generator offered "four directions" returns a turntable, which is unusable.

**Rule — approve the first frame before generating the rest.** Rotate the
approved image; do not re-generate from the prompt three more times.

---

# 6. Sprite Assets Required

## 6.1 Main Building

| Asset         | Required | Frames | Directions |
| ------------- | -------: | -----: | ---------: |
| Main building |        ✓ |  `[x]` |    `[1/4/8]` |
| Shadow        |        ✓ |  `[x]` |    `[1/4/8]` |
| Idle state    |        ✓ |  `[x]` |    `[1/4/8]` |
| Working state |  `[✓/—]` |  `[x]` |    `[1/4/8]` |

**Fill rule:** list only the slots this prototype actually exposes. Naming a
slot the entity type does not have produces art nobody can wire up.

**Idle is authored, not assumed.** A generator draws every machine at full
tilt — furnace glowing, metal pouring, everything lit. The idle plate is made by
*taking that light away*: dark interior, no pouring, no sparks, no steam,
machinery stopped. The contrast between idle and working is most of what makes
working read at all, so a bright idle throws away the animation's whole effect.

**Engine limits worth stating here:**
`[Anything the prototype cannot show — buffer levels, per-direction animation,
state-driven lights. Say it plainly; the art then compensates honestly instead
of implying a state the player can never see.]`

---

## 6.2 Animation Layers

| Layer          | Required | Animated | Frames |
| -------------- | -------: | -------: | -----: |
| Main structure |        ✓ |       No |      1 |
| Machinery      |  `[✓/—]` |  `[✓/—]` |  `[x]` |
| Pistons        |  `[✓/—]` |  `[✓/—]` |  `[x]` |
| Belts          |  `[✓/—]` |  `[✓/—]` |  `[x]` |
| Fans           |  `[✓/—]` |  `[✓/—]` |  `[x]` |
| Lights         |  `[✓/—]` |  `[✓/—]` |  `[x]` |
| Glow           |  `[✓/—]` |  `[✓/—]` |  `[x]` |
| Steam          |  `[✓/—]` |  `[✓/—]` |  `[x]` |

**Animation FPS:** `[value]`

**Animation Loop:** `[Yes / No / one-shot, engine-triggered]`

**What must NOT move:**
`[List it. If the mechanic has no reciprocating parts, a generator drawing a
piston has misread the machine, and so will every reviewer afterwards.]`

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
├── Working Machinery
├── Lighting
├── Glow
└── Effects
```

### Layer Notes

**Fill rule:** write `None — [why]` for layers this building does not have.
An empty heading reads as an oversight; a refusal reads as a decision.

**Shadow:** `[Direction, length, and whether the planet's day-night cycle ever
moves it]`

**Base:** `[Description]`

**Main Structure:** `[Description]`

**Static Machinery:** `[Description]`

**Pipes:** `[Description or None]`

**Working Machinery:** `[Description or None]`

**Lighting:** `[Description or None]`

**Glow:** `[Description — and whether plates may be merged]`

**Effects:** `[Description or None]`

---

# 8. Input / Output Visualisation

**Fill rule:** read the fluid boxes and connection points off the prototype and
list every position, including the ones a player will rarely use. Art that
hides an existing connection point is a bug report waiting to happen.

### Rule zero: the building is drawn square-on to the tile grid

**Checked against the electric mining drill in all four directions.** Factorio's
camera is a slightly-tilted top-down, and the tile grid is aligned with the
screen: north is up, east is right. So every vanilla sprite presents the building
**face-on** — its front face parallel to the bottom of the frame, its side faces
parallel to the left and right edges. The drill's output spout leaves a face at
right angles and points **straight down the screen**.

**A building drawn rotated, with a corner toward the viewer, is in the wrong
projection**, and it takes every port with it: from a corner-on box, every face
points diagonally, so every chute, flange and boom exits on a diagonal and aims
at no tile at all. Belts and inserters are axis-aligned; a diagonal port is
pointing at nothing.

This is easy to get wrong because a three-quarter corner view is what concept art
*normally* looks like, and a generator will default to it every time unless told
otherwise. Say it explicitly in every prompt:

> Draw the building square-on to the tile grid, as Factorio draws its own
> sprites: the front face parallel to the bottom edge of the panel, the side
> faces parallel to the left and right edges. Do not rotate it so a corner points
> at the viewer. Every chute, port and pipe leaves a face at right angles to it,
> pointing straight up, down, left or right in the image — never diagonally out
> of a corner.

### Three conventions vanilla never breaks

Checked against the real sprites, not remembered. Every one of these is easy to
break at concept stage and expensive to unpick afterwards.

**1. Never draw the product.** No vanilla machine paints the thing it makes into
its own plate. The space crusher is enclosed and shows nothing; the foundry and
the chemical plant show pipework and no material at all. The apparent exception
proves it: the big mining drill has an `output` layer, and that layer is an
*animated chute mechanism* — the ore itself is placed by the engine at
`vector_to_place_result`, as a real item entity.

So **draw the chute, never what comes out of it.** A machine with product heaped
at its feet is wrong twice over: the pile is a lie the moment the belt backs up
or the machine idles, and it is drawn on tiles the entity does not own.

**The corollary: enclose the working chamber.** This is *why* vanilla's crusher
is a sealed housing with its rollers in a recessed bay. If a machine cannot show
what it is working on, then an open frame around an empty bed, an empty tray or
an empty throat advertises that emptiness on every tick, and the machine reads as
idle even while it runs. Put the process inside a housing, and let the outside
carry the read instead — a shaft head that rises, a hatch, a window, a moving arm.
An open machine is only right when the thing moving in the open is *machinery*.

**2. Every connection lands on a tile edge, at ground level.** A pipe that leaves
the top of a building, or stops in mid-air, connects to nothing — the engine puts
fluid connections on the tile boundary the prototype names, and a player's pipe
arrives there and nowhere else. A riser is fine as long as it comes back down and
terminates at the edge.

**3. Two ports means two tiles.** Where a machine has two output ports — a coarse
and a fine chute, two splitter mouths, two discharge lips — they must sit on
**separate tiles of the footprint**, ideally on different faces. Drawn side by
side inside one tile they read as a single output, which throws away the reason
there are two of them, and a player cannot see where to put the second belt.
The engine does not care: an assembling machine has one output inventory and an
inserter may stand anywhere. The *player* cares, and the art is the only thing
telling them.

**And the ports must differ in size, not just in position.** Two identical mouths
read as a decorative symmetric pair; one wide and one narrow reads as *coarse and
fine*, which is the recipe. State it as its own hard rule when prompting, with
the faces named — buried inside a longer clause it is quietly dropped, which cost
a full regeneration of the Drop Crusher's variants sheet.

**4. Nothing crosses the collision box** — not the machine, not a pipe run, and
not spilled material or ground scatter. The Arc Mast is the standing lesson: at
3.14 tiles on a 3-tile pitch, a row of them interleaved, and the fix was to cut
the plate to exactly 3.00. Ground decals are the one legitimate exception, and
they belong in their own layer rather than baked into the base plate — vanilla
does this with `mining_drill_scorch_mark`.

## Item Inputs

| Input    | Location      | Direction   |
| -------- | ------------- | ----------- |
| `[item]` | `[tile/side]` | `[N/E/S/W]` |

## Item Outputs

| Output   | Location      | Direction   |
| -------- | ------------- | ----------- |
| `[item]` | `[tile/side]` | `[N/E/S/W]` |

## Fluid Inputs / Outputs

| Fluid     | Location     | Connection Type     |
| --------- | ------------ | ------------------- |
| `[fluid]` | `[location]` | `[pipe connection]` |

## Energy

| Flow | Location | Connection Type |
| ---- | -------- | --------------- |
| `[in / out]` | `[where]` | `[network / heat pipe / strike offset]` |

### Hard geometric constraints

`[Any offset the engine draws to regardless of the art —
lightning_strike_offset, heat connection points, rocket launch position. Convert
each one into a pixel row or column in §13. This is the class of error that is
invisible in the concept and glaring in game.]`

### Visual Requirement

`[How the player tells inputs from outputs at a glance, and what the most
likely mistake is.]`

---

# 9. Working Animation

## Animation Concept

`[What physically happens when it runs — and whether it is a cycle or a
continuous flow. They read completely differently and the wrong one makes the
mechanic unreadable.]`

### Sequence

1. `[Idle]`
2. `[Begins]`
3. `[Major movement]`
4. `[Processing]`
5. `[Completion]`
6. `[Return to idle]`

**Frame Count:** `[x]` · **FPS:** `[x]` · **Loop Duration:** `[x] s`

**Rule — generate animation components, not whole buildings.** Never ask for N
complete frames: the geometry drifts between them and the building visibly
changes shape as it animates. Keep the approved base plate fixed and generate
or edit **only the moving area** — the molten channel, the flowing fluid, the
light travelling down a bus bar — then composite those over the static base in
processing.

**Rule — decide what moves before generating anything.** Write the mechanical
cycle out first (conveyor advances → ram cycles → chamber churns → outlet
pulses). Prefer a *continuous* cycle over one that visibly completes a recipe:
crafting time varies with recipe and modules, so an animation that depicts
completion will desynchronise from what the machine is actually doing.

---

# 10. Effects

## Working Effects

* [ ] Glow
* [ ] Steam
* [ ] Smoke
* [ ] Sparks
* [ ] Flames
* [ ] Electrical arcs
* [ ] Moving fluids
* [ ] Other: `[description]`

### Effect Description

`[Exactly what is visible while operating.]`

### Prohibited effects, and why

`[Name them and give the reason from the design, not just the ban. "No flame —
pressure 5 means nothing burns here" survives a generator's creative instincts;
"no flame" alone does not.]`

---

# 11. DALL·E Generation Requirements

**Fill rule:** every prompt below follows the anatomy in Appendix A, in that
order, and ends with the standard tail. Prompts are the only part of this
document a machine reads verbatim — write them as instructions to a
literal-minded stranger, not as prose about the building.

**Canvas:** `[portrait 2:3 for tall buildings, square for flat ones and icons]`
— generate at the largest size available; we downscale. Transparent background
where supported, otherwise flat magenta `#FF00FF`, chosen because it appears
nowhere on the building.

## Concept Sheet Prompt

One landscape image, generated first. Unlike every other prompt in this
document, this one **may ask for text and labels** — it is a design sheet, not
a sprite. Name the panels explicitly or the generator returns a single hero
render.

```text
[Prompt goes here — name every panel: directional views, in-game icon, tile
grid top view, close-up details, layer breakdown, working animation key
frames, effects layers, building information, palette strip.]
```

---

## Master Concept Prompt

```text
[Prompt goes here]
```

---

## Directional Prompts

Only if §5 says more than one direction. Otherwise write `Not required — see
§5.` in each block; the generator script skips those and the headings stay put.

### North

```text
[Prompt]
```

### East

```text
[Prompt]
```

### South

```text
[Prompt]
```

### West

```text
[Prompt]
```

---

## Layer Prompts

### Main Structure

```text
[Master prompt] [what to strip: everything unlit, nothing glowing]
```

### Working Machinery

```text
[Prompt, or "Not required — see §6.2"]
```

### Glow / Lighting

```text
[Glow plates only, on transparent, with no metal drawn]
```

### Effects

```text
[Effect only, on transparent, nothing else in frame]
```

---

# 12. Image Processing

### Processing Checklist

* [ ] Remove background
* [ ] Remove unwanted shadows/background objects
* [ ] Crop to building
* [ ] Correct perspective
* [ ] Match Factorio scale
* [ ] Convert to appropriate resolution
* [ ] Align to tile grid
* [ ] Separate layers
* [ ] Generate directional sprites
* [ ] Generate animation frames
* [ ] Generate spritesheets
* [ ] Optimise PNGs

**Rule — the first three are the expensive ones, and their order matters.**
Generators attach a ground plane and a baked drop shadow to anything that looks
like it stands on the floor, whatever the prompt says. Both come off before the
crop, or the crop lands in the wrong place. The baked shadow is never reusable:
Factorio wants a separate `draw_as_shadow` sheet, and one left in the colour
layer doubles against the engine's own.

**Rule — the crop is driven by §8's hard constraints, not by the artwork.**
Where an engine offset fixes a pixel row, crop to that row first and let the
rest fall where it falls.

---

# 13. Sprite Dimensions

**Fill rule:** give source pixels *and* the in-game equivalent, and state the
scale. Turn every §8 hard constraint into a pixel coordinate here, with a
tolerance.

**Rule — derive these from the finished art, not from the footprint.** Canvas
size and `shift` are measurements of the approved plate, taken after it exists;
guessing them from the nominal tile size produces a sprite that is the wrong
size on the ground, and the error is invisible until it is in game. Fill this
section provisionally if you must, mark it so, and re-measure once stage 1
passes.

**The exception is anything the engine pins.** Where a prototype draws to a
fixed offset — `lightning_strike_offset`, heat connection points, a launch
position — that coordinate is a constraint the art must satisfy, not a
measurement to take afterwards. Derive everything else; pin those.

### The arithmetic everything else rests on

Get these three wrong and every number in this section is wrong, invisibly.

```text
tiles          = source_px * scale / 32          NOT / 64
util.by_pixel  = {x/32, y/32}, always in-game px, whatever the sprite's scale
```

`scale = 0.5` does mean 64 source px per tile — but the formula is
`* scale / 32`, and reaching for `/ 64` instead makes the building half the size
you think it is. On a scale-0.5 plate, `by_pixel(0, -60)` is a shift of 120
*source* pixels.

**Fit the art to the box by making the numbers equal, not close.** The visible
half-width in tiles must *equal* the selection box's half-width. The arc mast
sat at 3.14 tiles against a 3.00 tile box and the 0.14 tiles of overlap was
plainly visible in game — a quarter of a foot pad, two of them interleaving.
Vanilla tolerates 0.25 tiles on its lightning collector only because the
overhang there is a soft tapering skirt; hard bolted geometry has no such
slack. Cut the plate so the number is exact, then check it:

```python
half = max(abs(bb[0] - W/2), abs(bb[2] - W/2))   # bb = visible bbox, W = canvas
assert half * scale / 32 == selection_box_half_width
```

**Anchor `shift` on the ground-contact plate, never on the tip.** Anchoring on
the tip fixes the top of the building and lets the bottom fall wherever it
lands; the arc mast floated two thirds of a tile above its own footprint, with
its selection box drawn in bare ground beneath it. Measure the rows the base
plate occupies, take their centre, and put that on the origin. Vanilla's
collector sits its plate centre at `-0.133` tiles, which is a good target.

**Anything the engine pins is downstream of the plate, not fixed.** The note
above says pinned coordinates are a constraint the art must satisfy — true when
you are *commissioning* art, but once the plate exists the pin has to be
re-derived from it, and re-derived again every time the plate is re-cut.
`lightning_strike_offset` moved twice on the arc mast for exactly this reason.
Write the derivation down next to the number.

**Tile Size:** `[32] px in-game` · **Scale:** `[0.5]` → `[64] source px per tile`

**Building Width:** `[x] tiles → [x] in-game px → [x] source px`

**Building Height:** `[x] tiles → [x] in-game px → [x] source px`

**Sprite Width / Height:** `[x] × [x]` source px

**Shift:** `util.by_pixel([x], [y])`

**Fixed points:**
`[e.g. "the tip must land 53 source px below the top edge, ±4"]`

**Spritesheet Width / Height:** `[x] × [x]` px

**Frame Count:** `[x]` · **Line Length:** `[x]`

---

# 14. File Structure

```text
graphics/
└── entity/
    └── [building-name]/
        ├── concept/                   generated concepts, not shipped
        │   └── [tag]-[slug].png
        ├── base.png                   almost the whole machine, static, unlit
        ├── shadow.png                 draw_as_shadow
        ├── working.png                only the parts that move
        └── glow.png                   only the emissive light
```

**Fill rule:** four plates is the practical shipped set for most buildings, and
§7's nine-part tree describes *content*, not files — several of its entries live
inside `base.png`. Add directional variants only where §5 says the entity
rotates, and add frames only where §6 says an animation exists.

**Smoke, steam and particles are usually engine effects, not sprites.**
Factorio can emit them from the prototype, so baking them into a plate costs
resolution and freezes something the engine would otherwise vary. Bake an
effect only when it has to align exactly with painted geometry.

---

# 15. Factorio Prototype

**Prototype Type:** `[type]`

**Prototype Name:** `[name]`

### Graphics

```lua
-- The real table, written so it can be pasted into the prototype file.
```

### Other Visual Properties

```text
Animation:
Shadow:
Working Visualisation:
Lights:
Fluid Boxes:
Circuit Connections:
Remnants:
```

**Fill rule:** name anything still inherited from the vanilla original and
therefore now wrong — remnants and corpses are the usual ones — as an explicit
follow-up rather than leaving it silent.

---

# 16. Icon

**Icon Required:** ✓ · **Icon Size:** `64×64`

**Icon Concept:**
`[The simplified read — and what gets dropped. An icon is not the sprite
scaled down; detail that survives at 224 px turns to mud at 32.]`

### Icon Prompt

```text
[Prompt]
```

---

# 17. Visual QA Checklist

**Fill rule:** add a line for every anti-read named in §3.1 and every hard
constraint in §8. A generic checklist passes everything.

### Building

* [ ] Correct tile size
* [ ] Correct perspective — base from above, tall parts leaning toward camera
* [ ] Correct scale
* [ ] Clear silhouette
* [ ] Looks like Factorio
* [ ] Matches intended planet
* [ ] Inputs are visually understandable
* [ ] Outputs are visually understandable
* [ ] **Does not read as** `[the anti-read from §3.1]`

### Directions

* [ ] North · [ ] East · [ ] South · [ ] West
* [ ] All directions represent the same building

### Animation

* [ ] Working animation is readable
* [ ] Animation loops correctly, or fires once as intended
* [ ] No parts change shape unexpectedly
* [ ] Static components remain static
* [ ] Effects align correctly

### Generated-art defects

* [ ] No baked drop shadow in the colour layer
* [ ] No ground plane or scenery
* [ ] Background is transparent or cleanly keyable
* [ ] Palette matches §3.3 rather than drifting pale and rust-orange
* [ ] Nothing glows that §3.3 says is unlit

### In-Game

Place **at least three in a row.** One building hides every spacing defect
there is.

* [ ] Engine-drawn effects land where the art says they should
* [ ] Shadow aligns, does not double, and is *visible* — brighten the screenshot
      and confirm it is actually there
* [ ] Inserters and pipes align correctly
* [ ] Neighbours do not overlap — measured, not judged: see Appendix C
* [ ] The building sits on its tile, not above it — the selection box should not
      be drawn in bare ground below the machine
* [ ] Recognisable among other machines
* [ ] Performance is acceptable

---

# 18. Final Asset Checklist

```text
[ ] Master concept
[ ] Directional sprites   (or n/a — one direction)
[ ] Shadow
[ ] Idle / static picture
[ ] Working animation
[ ] Glow layer
[ ] Effects layer
[ ] Icon
[ ] Spritesheets
[ ] Factorio prototype
[ ] In-game test
```

---

# 19. Design Notes / Iteration History

**Fill rule:** one entry per generation round, written *when it happens*.
Record what came back and what was asked for next, because the same generator
makes the same mistakes on the next building and this is where that gets
cheaper.

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| `1` | `[slug]` | `[what it actually was]` | `[reject / accept]` | `[the refinement]` |

### Version 1

`[Notes]`

### Version 2

`[Changes made]`

### Final

`[Final design decisions]`

---

# Appendix A — Prompt anatomy

Every prompt in §11 is written in this order. The order is not cosmetic:
generators weight early text more heavily, and a constraint that arrives after
three sentences of description gets outvoted by the description.

1. **Subject, in one clause.** What the object *is*, in the plainest words.
2. **Camera, named.** "Viewed from the game's characteristic 45-degree top-down
   perspective" — the exact phrase, early. For a tall building add the leaning
   clause after it; do not replace it with the clause. See §4.
3. **Structure, bottom to top.** In physical order, each component with its
   position relative to the last. Generators lose track of "and also" lists;
   they follow a climb.
4. **Proportion, stated as a ratio.** "Twice as tall as it is wide", "the tip
   occupies the top eighth". Adjectives like "squat" do nothing.
5. **Materials and palette, with hexes.** Plus what to *reduce* — pale and
   rust-orange are the default drift, and must be argued down explicitly.
6. **State.** Lit or unlit, working or idle, and what must not glow.
7. **Negative reads — the important part.** Name the wrong object the shape
   could collapse into, not just the features to omit: *"must read as earthed
   infrastructure, not a rocket: no nose cone, nothing tapering to a point,
   nothing aimed."* A list of banned parts does not prevent a banned silhouette.
8. **Standard tail**, verbatim:

```text
Painted semi-realistic industrial game art, strong readable silhouette,
[N] tiles wide and [M] tiles tall, fully transparent background, no text,
no logos, no characters, no UI, no ground texture, no background scenery,
no baked drop shadow.
```

### Writing a refinement

Proven shape, in this order:

1. **The keep-list first.** Name every element that survives, explicitly. A
   refinement that opens with a complaint gets a redesign, and the parts that
   worked are lost.
2. **Numbered fixes, one change each.** Numbering them makes them survivable
   as a list; bundling two changes into one sentence loses the second.
3. **For each fix: what it currently reads as, then what it must read as.**
   "It reads as a rocket on a launch stand; the top must be a blunt electrode
   stub" beats "make the top blunter".
4. **Re-state the canvas and background rules.** They are dropped on almost
   every regeneration.

---

# Appendix B — Browser generation

When generating through a chat UI rather than the API:

* **Flatten the prompt to a single paragraph.** A newline sends the message.
  Replace the line breaks with spaces; the prompt is unchanged otherwise.
* **Avoid characters the composer eats.** Em dashes and smart quotes survive;
  markdown fences do not — paste the prompt body, not the fence.
* **Ask for portrait explicitly** (`portrait, 2:3`). Chat UIs default to
  square and will silently crop a tall building to fit.
* **Refine in the same conversation** so the previous image is context, but say
  *"regenerate"* rather than *"edit"* when the silhouette itself is wrong — an
  edit preserves the very shape being rejected.
* **Never judge a plate by looking at it in a viewer.** A transparent PNG is
  composited onto whatever background the viewer uses, so the metal's apparent
  value moves with it and a dark preview makes ordinary highlights read as
  "silvery" or "bleached". Measured over five rounds on one building, eyeballing
  produced two confident and completely wrong findings — a lost alpha channel
  that was never lost, and a pale palette that was in fact already below its
  target floor, which three refinements then drove darker still. Run
  `tools/process-building-art.py <plate> --report` and refine against the
  numbers: alpha split, trimmed aspect, body-metal luminance.
* Save concepts to `graphics/entity/<building>/concept/<tag>-<slug>.png` by
  hand, matching the names `tools/generate-building-art.py` would have used, so
  both routes leave the same trail.

### Driving the composer, which is fiddly

Three mechanical things cost time every session until they are written down.

* **Typing into a freshly-loaded page silently does nothing.** Click the
  composer, type a one-word probe, and read `#prompt-textarea`'s `innerText`
  back before committing the real prompt. On a page that has just navigated or
  just taken an upload, the first click-and-type lands nowhere and the composer
  stays empty — and the send button is enabled either way, so nothing complains.
* **Do not click the send arrow by screen position.** Attaching files and typing
  a long prompt both grow the composer, and the arrow moves down with it; a
  click at the old coordinates lands inside the textarea. Click the button
  through the DOM (`button[data-testid="send-button"]`), and gate it on the text
  actually being there.
* **Poll for the image, not for the stop button, and identify it by bytes.**
  Several `img` elements share the same rendered image, a lazily-attached
  thumbnail can be the newest node while being an *older* picture, and an edit
  that changed nothing comes back re-encoded — different file size, identical
  pixels. Fetch each candidate as a blob, compare sizes to find the one you have
  not seen, and if the result matters, `ImageChops.difference` it against the
  input before believing it is new. The store's "make the ring glow" edit was
  caught this way: zero difference on every channel.

### Four things that moved the needle more than prompt wording

Measured across roughly a dozen rounds on one building:

1. **Name the camera angle** — see §4. Worth more than any other single word.
2. **Attach a real vanilla sprite as a style reference.** Pull one out of the
   game's own `data/base/graphics/entity/…`, crop a single frame, upscale it,
   and say: *match the camera, rendering, finish and level of detail; do NOT
   copy the design, shape, colours or components.* The disclaimer is load-
   bearing. Pick a reference the building is not trying to avoid resembling —
   using the very machine named in §3.1's anti-read would pull the design
   straight back toward it.
3. **Attach an example of the deliverable format.** A finished sheet for a
   *different* building produced a correctly laid-out sheet in one attempt,
   including panel structure and an information table that several rounds of
   describing in words had failed to get.
4. **Start a new conversation when the context is polluted.** A thread carrying
   earlier corrections — including wrong ones — keeps honouring them. A clean
   session with the corrected prompt behaves noticeably better.

### Once the design is locked, stop prompting

This is the single most important rule in this document. A generator asked to
draw the same machine again will re-interpret it every time, and the drift is
invisible until two frames are compared side by side. A component count that
survived nine rounds of being *told* "exactly four" was fixed in one round of
being *shown* the image and told to edit it.

So: crop the approved view out of whatever it lives in, attach it as the
source, and give an explicit, numbered list of exactly which changes are
permitted. Words specify a design; only the image preserves it.


---

# Appendix C — The production pipeline

Concept art is not a sprite. Everything below is mechanical, scripted, and
repeatable; none of it should be asked of an image generator.

### The tools

| Tool | What it does |
| ---- | ------------ |
| `tools/generate-building-art.py` | Reads §11/§16 prompts out of a spec. `--list` / `--dry-run` to get prompt text for the browser route. |
| `tools/process-building-art.py` | `--report` measures a plate; `--dekey` restores alpha; otherwise trims, scales, places on the sprite canvas and derives a shadow. |
| `tools/derive-glow.py` | Subtracts an unlit plate from its lit twin to recover the additive glow layer. |
| `tools/build-glow-frames.py` | Builds animation spritesheets from one glow plate with a travelling mask. |

### Measure every plate before judging it

```
tools/process-building-art.py <plate> --report
```

Prints alpha split, trimmed aspect and body-metal luminance against the §3.3
range. **Never judge a transparent plate by looking at it** — the viewer
composites it onto its own background, so the metal's apparent value moves with
the backdrop and ordinary highlights read as "silvery". Eyeballing produced two
confident, completely wrong findings on one building: a lost alpha channel that
was never lost, and a "pale" palette that was already below its target floor,
which three refinements then drove darker still.

### The checkerboard export trap

ChatGPT's image editor exports edited images **flattened onto its transparency
checkerboard**, so a download arrives 100% opaque with the pattern baked in even
though the editor shows it as transparent. `--dekey` recovers the alpha: a
border-seeded flood fill over bright neutral greys. It cannot punch through
light-but-chromatic parts (cream ceramics, warm metal) because those are not
neutral. Re-running it on an already-cleared plate works — cleared pixels are
treated as passable.

### Glow: difference, never draw

Do not ask for "just the light on transparency" — the generator invents
geometry that will not line up with the base plate. Instead:

1. Approve the unlit plate.
2. Attach it and ask for **the same image, lit**, with the machine unchanged.
3. `tools/derive-glow.py --lit <lit> --unlit <unlit>` — the placement is
   measured off the **unlit** plate and applied to both, then they are
   subtracted. The difference *is* the light.

**Trim on what you can see, not on `getbbox()`.** A generator leaves fringe:
`v11-idle.png` had 95 columns down one side holding a single speck above alpha
20 and nothing else. Cropping to the raw alpha box squeezed the building into
814/909 of its canvas, off-centre and clipped flat at the edge. Require a row or
column to carry a handful of pixels above a real alpha before it counts as
content — `solid_bbox()` in both art tools — and then check the two things that
follow: **the visible content is centred in its canvas, and the alpha is zero at
all four edges.** Neither shows up in a viewer; both are one line to measure.

**Registration is the thing to check, and "same canvas" does not give it to
you.** The tool used to trim each plate to its own alpha bounding box; a lit
render blooms past the metal, so its box is bigger, and the two ended up on
different scales and different centres. Every frame of the arc mast's two
sheets shipped 6 px right and 8 px above the plate. If you touch this tool,
verify it the cheap way: put the unlit plate through the same path and diff the
result against the shipped colour plate. The alpha bounding boxes must match
exactly.

### Animation: mask, never generate

Frames come from one glow plate and a travelling gradient. A mask cannot drift;
nineteen separate generations will. Direction carries meaning — light moving
*down* reads as energy arriving, *up* as energy leaving — so it is worth making
the two sequences differ in direction and brightness rather than only in speed.

### A tall building's shadow needs its own canvas

Factorio wants the shadow as its own `draw_as_shadow` sheet, and a tall
building's shadow does not fit inside its colour plate's width. Give it a wider
canvas, anchor it left, and offset it right by half the extra width in `shift`.

**A synthesised shadow is a projection, not a squash.** A pixel `up` rows above
the object's foot lands `up*kx` to the right and `up*ky` *further up the
screen*, on the foot's own row — discard the source row entirely. Keeping it
only squashes the silhouette and leaves the building standing in its own
shadow. `kx 0.79, ky 0.25`, measured off vanilla's lightning collector, put the
arc mast's shadow at 5.98 × 1.45 tiles against vanilla's 6.36 × 1.53.

**Check the alpha before believing the shadow exists.** The first arc-mast
plate rendered at a peak alpha of 94 and was simply invisible in game, because
the tool composited it over a transparent canvas through its own alpha —
squaring it — and then scaled against 255 rather than the plate's actual peak.
A shadow you cannot see in a brightened screenshot is not a subtle shadow.

It is still synthesised rather than hand-authored, which remains the ceiling on
how good it gets.

### Measure the camera before anything else

Every concept sheet this mod has commissioned is drawn at a **shallower camera
than Factorio's projection**, and no amount of looking at the plate says so. The
tell is one number `--report` already prints: the **aspect of the trimmed
content**, measured against a real vanilla building of the same footprint and
roughly the same shape.

| Vanilla plate | Footprint | Content | Aspect |
| ------------- | --------- | ------- | ------ |
| `assembling-machine-1-base.png` | 3×3, boxy | 188 × 180 px | 1 : 0.96 |
| `storage-tank.png` (frame 0) | 3×3, **round** | 199 × 218 px | 1 : 1.10 |
| `accumulator.png` | 2×2, tall box | 130 × 186 px | 1 : 1.43 |

**Why it is never much below 1 : 1.** Factorio's ground is drawn as a true
top-down square grid — a tile is a 32 × 32 square, not a diamond, and not
foreshortened. So a building's base spans its footprint *equally in both axes*:
a round drum two tiles across stands on a base drawn as a full circle two tiles
wide **and** two tiles deep. The 45-degree look comes from buildings showing
their sides, not from a tilted ground plane. A plate wider than it is tall is
therefore a building that does not cover its own footprint, and it shows up in
game as bare ground between neighbours — which vanilla never has.

The cheap way to see it: render the cut plate in a grid at the real tile pitch,
in **both** axes. Nine vanilla accumulators at a 2-tile pitch overlap heavily
front to back with no ground showing; the store's first plate, at 1 : 0.94, left
a clear gap in every row.

The fix is a **regenerate, not an edit**: an edit preserves the silhouette being
rejected. Attach a real vanilla sprite as a camera reference under the standing
"do not copy the design" clause — but **not one the design's anti-read names**;
a storage tank is the right camera for a round drum and exactly the wrong thing
to show a generator drawing a cryostat that must not read as a fluid tank.
State the target as a number, not an adjective, and give it in pixels: *if it is
1000 px wide the finished object must be about 1100 px tall.*

**And when the correction does not take, start a new conversation.** The store's
third round was asked to regenerate unlit and came back lit, at the same wrong
camera, because the thread above it contained "the lighting on that last one is
exactly right and I want it kept". A thread honours its own history over the
instruction in front of it — Appendix B says this and it costs a round every
time it is forgotten.

### Four measurements before a plate is wired

Every arc-mast defect passed the data-stage load, `--report`, `check-graphics.sh`
and a careful look at the PNG. All four were geometry, and geometry is not
visible in a viewer. These take a minute and would have caught all of them.

```python
from PIL import Image
im = Image.open(plate).convert("RGBA"); a = im.getchannel("A"); W, H = im.size
bb = a.point(lambda v: 255 if v > 20 else 0).getbbox()      # visible content

# 1. centred?  content centre must equal canvas centre
(bb[0] + bb[2]) / 2 == W / 2

# 2. clipped?  alpha must be 0 down both edge columns and along both edge rows
max(a.getpixel((0, y))     for y in range(H)) == 0
max(a.getpixel((W - 1, y)) for y in range(H)) == 0

# 3. fits the box?  visible half-width in tiles == selection box half-width
max(abs(bb[0] - W/2), abs(bb[2] - W/2)) * scale / 32

# 4. declared == actual?  and does the sheet hold its frames?
im.size == (declared_w * cols, declared_h * rows)
frame_count <= cols * rows  and  line_length <= cols
```

`process-building-art.py --bottom-margin` exists so check 2 can actually pass:
without it the art lands flush on the canvas floor and the bottom row is never
zero. The arc mast shipped that way and measures `B255` to this day.

Check 2 is the one nobody thinks of. A plate hard against its canvas edge has no
antialiased rim — it ends on a razor line mid-geometry — and it is also the
symptom that says the *trim* is wrong, which is what pushes the building
off-centre in the first place.

`check-graphics.sh` covers none of this; it only proves the files exist.

### Measuring overlap, rather than arguing about it

Render N neighbours at the real pitch and count opaque pixels claimed by two
buildings at once:

```python
overlap = sum(1 for y in ... for x in ... if mask_a[x, y] and mask_b[x, y])
```

A correct fit gives a **1–2 px seam at low alpha that vanishes above ~alpha 80**
— that is two antialiased edges meeting. Real overlap is tens of pixels wide and
survives any threshold. Run the same measurement on the vanilla building yours
is modelled on and compare: the arc mast finished at a 2 px seam against
vanilla's collector's 32 px, which is the evidence that ended the argument.

### Verifying without closing the game

`--dump-data` and the headless rig both take `~/.factorio/.lock`, so neither runs
while a client is open. Point Factorio at a scratch user-data directory instead
and it will not contend at all:

```ini
# scratch/config.ini
[path]
read-data=__PATH__executable__/../../data
write-data=/path/to/scratch/data
```

`factorio --dump-data --config scratch/config.ini --mod-directory scratch/mods`
then writes its dump to `scratch/data/script-output/`. The same flag works for
`--create` and `--start-server`. Do not kill a running client to free the lock.

### Then, and only then

Wire the prototype, run `tools/check-data-stage.sh` (which also runs the
graphics and recipe checks), and take it into a client. Everything up to that
point can be verified locally; the in-game pass — scale on the ground, selection
box, engine-drawn effects landing where the art says, shadow against
neighbours — cannot.

**Record it, and measure the recording — then do it again after the fix.** The
arc mast passed every local check and still shipped four geometry defects, all
of them found by pulling frames out of a screen capture. The fix for the worst
of them was itself incomplete, and only a second screenshot showed it: the box
had been grown to fit the art, but the art was 3.14 tiles against a 3 tile box
and still overlapped. Sizing art to a box means making the number *equal*, not
close.

**The selection brackets are the ruler.** They are a known number of tiles wide,
so measuring them in a frame gives screen-pixels-per-tile, and every claim about
sprite size, overlap and shift follows from that one number. Place at least
three of the building in a row — one hides overlap entirely.

**Do not assert a geometry number you have not computed.** Two of the four
arc-mast diagnoses were wrong the first time round and both were confident:
"the plates just touch at a 3 tile pitch" was arithmetic never actually done —
3.14 on a pitch of 3 overlaps — and the invisible shadow was blamed on the blur
when the real cause was compositing the plate through its own alpha, squaring
155 into 94. Both would have been caught by rendering the thing and measuring
it, which is a minute's work. If a claim about size, position or overlap has not
come out of a measurement, write it as a question instead.
