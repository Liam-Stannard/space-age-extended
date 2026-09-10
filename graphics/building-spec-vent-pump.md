# Factorio Building — Art & Implementation Specification

**Vent Pump.** Filled from `building-spec-template.md`. Every gameplay number
here is the implemented value read off `prototypes/core/entities.lua` and the
vanilla prototypes it deep-copies, not a proposal. The art sections *are*
proposals: the building currently wears vanilla's pumpjack unmodified, and this
document exists to commission a replacement.

**The central art decision — see §3.1.** A pumpjack is a *beam pump*: a
counterweighted horsehead nodding over an open sucker rod, lifting cold crude
by suction. The Vent Pump does none of that. It draws 1200 °C molten metal out
of a sealed hole by injecting cryogenic helium-3 — which is **gas lift**, a real
and completely different piece of machinery, with no reciprocating parts and
nothing open to the sky. The replacement art should be a **gas-lift wellhead**,
not a recoloured nodding donkey.

---

## 1. Building Overview

**Building Name:**
`Vent Pump`

**Internal Prototype Name:**
`sae-vent-pump`

**Building Type:**
`mining-drill`, deep-copied from `pumpjack` with an `input_fluid_box` added
from `electric-mining-drill`. The entity type is load-bearing: only
`mining-drill` supports `minable.required_fluid` on the resource *and* an
output fluid box, which is what makes helium-3 throttle the melt without a
line of control-stage script. When the helium runs out the engine raises
`missing_required_fluid` on its own — a failure the player can read off the
building.

**Planet / Environment:**
`The Core.` Not gated by a placement rule of its own — it is gated by having
somewhere to place it. `sae-melt-vent` exists on no other surface, and helium-3
is `auto_barrel = false` so it cannot be imported. A Vent Pump on Nauvis would
build and then sit idle forever.

**Purpose:**
Draws **molten kamacite** from a melt vent. Consumes **10 helium-3 per mining
operation** to do it (`minable.required_fluid`), so the Core's rare vent
throttles its rich one and the two vent types are a single coupled siting
problem. This is the first machine the player builds on the Core and the head
of every chain on the planet.

**Technology Unlock:**
`Core Survey` (tier 0 — see `design/04-the-core.md` §6). Researched on vanilla
packs, since no geodynamic pack can exist before this building runs.

---

## 2. Gameplay Dimensions

Inherited from `pumpjack` unless stated.

**Tile Size:**
`3×3`

**Collision Box:**
`[-1.2, -1.2] → [1.2, 1.2]`

**Selection Box:**
`[-1.5, -1.5] → [1.5, 1.5]`

**Placement Restrictions:**
Requires a `sae-melt-vent` resource under it (`resource_categories =
{"basic-fluid"}`). No `surface_conditions` — see §1. `fast_replaceable_group`
and `next_upgrade` are both cleared, so it never fast-replaces a pumpjack and
never offers an upgrade path.

**Rotation:**
`4-way.` **The output pipe moves to a different corner in each direction** and
the three input pipes rotate with the body. This is the most important art
constraint in this document; see §5 and §8.

**Crafting Speed:**
n/a. `mining_speed = 1`, against `sae-melt-vent`'s `minable.mining_time = 1`
and a yield of 10 molten kamacite, declining with depletion the way crude oil
does.

**Energy Consumption:**
`90 kW` while working. Deliberately unchanged from the pumpjack: the machine's
real cost is the helium, not the electricity, and raising the draw would blunt
that.

**Energy Type:**
`electric` (input, secondary priority). `module_slots = 2`.

---

# 3. Visual Design

## 3.1 Design Concept

**Primary Visual Theme:**
**Sealed cryogenic gas-lift wellhead.** Heavy, squat, pressure-tight
extraction plumbing bolted to bare metal. Explicitly **not** a beam pump, and
explicitly **not** a furnace: nothing burns anywhere on the Core, so the
building may glow with the melt it carries but must never look like it is
combusting anything.

**Overall Appearance:**
A low, wide armoured base plate anchored into the crust, carrying a stepped
stack of valve bodies over the vent bore — a christmas tree. Two thick pipes
meet the stack from opposite characters: a **frost-jacketed helium-3 injection
line** entering low and cold, and a **glowing production riser** leaving high
and hot, elbowing out to the pipe connection. The whole thing is bolted,
gasketed and closed; there is no open shaft, no exposed rod, no moving arm.

**Silhouette:**
A blocky square base with one asymmetric stepped tower offset over the bore,
and one thick pipe running low into it and one thick pipe leaving high out of
it. From altitude the read is *"valve stack, in and out"* — instantly not a
drill, instantly not an assembler, and it tells the player which way the
building faces from the pipe geometry alone.

**Visual Complexity:**
`Medium.` The Core's opening hours are wide belt-and-rail sprawl, and vents
come in clusters, so ten of these will be on screen at once beside settling
vessels and arc masts. One clear focal point — the stack — with the plumbing
subordinate to it.

**Visual Age:**
`Advanced.` This is the last planet in the game and everything here was
shipped in by rocket. Precise, plated, deliberately engineered — but working
machinery covered in condensation and metal dust, not a laboratory instrument.

---

## 3.2 Key Visual Features

The building should contain:

* A **stepped valve stack** (christmas tree) rising off-centre over the bore,
  three or four bodies tall, with flanged joints and hand-wheel valve caps.
* A **frost-jacketed injection line** entering low: a ribbed cryogenic pipe in
  a pale insulating sleeve, rimed white-blue, with a visible frost bloom where
  it meets the warm stack.
* A **production riser** leaving high: a thick, unlagged, heat-stained pipe
  carrying melt, dull orange at the seams, with heat-shimmer discolouration on
  the metal around it.
* A **heavy anchored base plate** with bolt rings and a raised gasketed collar
  around the bore, keeping the crust sealed.
* **A sight port on the riser** — a small armoured window through which moving
  melt is visible. This is the working tell and the one animated element.

### Signature Feature

**Cold and hot on the same machine, touching.** One frosted pipe going in, one
glowing pipe coming out, meeting at a single valve stack. No other building in
the mod or in vanilla puts rime and molten metal within a tile of each other,
and it renders the Core's central coupling — the rare vent paying for the rich
one — as something the player can see rather than read.

---

## 3.3 Colour Palette

Hexes are taken from the fluid prototypes in `prototypes/core/fluids.lua`, so
the building matches the fluids it moves wherever they appear in the UI.

**Primary:**
Dark iron-nickel grey-brown machined casing, `#4A463F` → `#6E685C`. Kamacite is
meteoric iron-nickel; the metal should look faintly warm and slightly oxidised,
not blue-steel.

**Secondary:**
Pale nickel-white machined bands and flange faces, `#B9B4A8`. Used sparingly,
to break the stack into readable steps.

**Metal:**
Warm dark steel. Deliberately desaturated so both accent colours read as
*material being carried* rather than as paint.

**Accent — injection side:**
Helium-3 cyan, `#8CC7E5` base ramping to `#C7E5FF` at the frost highlights.
Confined to the injection line, its collar, and its status lamp.

**Accent — production side:**
Molten kamacite orange, `#D96B29` base ramping to `#FF9E52` at the hottest
seams. Confined to the riser, the sight port and the seam lines near it.

**Working Glow:**
Warm orange `#FF9E52` at the sight port and riser seams, low and pulsing.
Separately, a faint cold `#C7E5FF` bloom at the injection collar. **The two
glows must never bleed into each other** — the gap between them is the whole
idea.

**Warning / Status Lights:**
One small amber lamp on the stack for `missing_required_fluid` — no helium, no
melt. It is the failure the player will hit most often, so it gets the only
indicator on the building.

---

# 4. Factorio Visual Style

The building should visually fit alongside the vanilla Factorio / Space Age graphics.

### Required characteristics

* [x] 45° top-down Factorio perspective
* [x] Strong readable silhouette
* [x] Appropriate visual scale
* [x] Industrial construction
* [x] Clear separation between major components
* [x] Subtle wear and grime
* [x] No photorealism
* [x] No text
* [x] No logos
* [x] No characters
* [x] No UI elements
* [x] No unrelated background objects

**Note on the perspective line above.** The template says "45°", and that is
the wrong number to hand an image generator: asked for 45° it produces a clean
isometric three-quarter view, which reads as a different game. Factorio's
camera sits roughly **60° above the horizon** — the player sees mostly the roof
of a building, a shallow slice of its north face, and no south face at all,
with the vanishing point far enough away to be effectively orthographic.
Prompts in §11 say this the long way round rather than naming an angle.

### Style Reference Buildings

1. `Pumpjack` (base)
2. `Cryogenic plant` (Space Age)
3. `Foundry` (Space Age)

**Reason for references:**
Take the **footprint, base plate and anchoring** from the pumpjack — it is the
same 3×3 over a fluid resource and its base is already proven to read at this
size. Take **nothing else** from it: the horsehead, the counterweight and the
rocking motion are all wrong for gas lift, and the recolour's whole problem is
that it still reads as an oil derrick on a planet with no oil. Take the
**frost, insulation sleeves and pale cryogenic plumbing** from the cryogenic
plant, which is the correct treatment for the helium line. Take the **heavy
flanged construction and the way molten material glows through seams** from the
foundry, which is the only vanilla building that already carries molten metal
in pipes.

---

# 5. Building Orientation

## Required Directions

* [x] North
* [x] East
* [x] South
* [x] West

**Direction count:**
`4`

All directions must represent the **same physical building**.

The following must remain consistent:

* Overall dimensions
* Building height
* Major machinery
* Pipes
* Windows
* Vents
* Platforms
* Decorative elements
* Colour scheme
* Material construction

Only the viewing direction should change.

**How the four directions actually differ.** The pumpjack solves this cheaply
and the Vent Pump inherits the solution: the base is **one sheet of four
frames**, one per direction, and the entity is *not* re-rendered from four
camera angles — the camera never moves in Factorio. Each frame is the same
machine with its **plumbing rotated a quarter turn** on the base plate. The
stack, the base, the bolt rings and the lighting are identical in all four; the
injection line, the riser and the output elbow move around the stack.

This matters for generation: **do not ask for four viewpoints.** Ask for four
arrangements, seen from the one fixed camera. Generators reliably get this
wrong and will hand back a rotating turntable, which is unusable.

---

# 6. Sprite Assets Required

## 6.1 Main Building

| Asset         | Required | Frames | Directions |
| ------------- | -------: | -----: | ---------: |
| Main building |        ✓ |    `1` |      `4` |
| Shadow        |        ✓ |    `1` |      `4` |
| Working glow  |        ✓ |   `16` |      `4` |

**This table used to say the working layer needed one direction, "because the
sight port and flow disc sit on the stack, which does not rotate".** The sight
port is on the **riser**, and the riser is the fluid box — it is the one part of
this building that *must* rotate. Measured off the cut plates, the port's glow
sits at top-centre in north, right in east, bottom in south and left in west. It
is four directions.

**And sixteen frames, not thirty-two.** The port is 9 × 16 screen pixels in the
north view and 12–13 tall in the others, so a rising level has at most sixteen
distinct pictures in it. Thirty-two frames would be sixteen images and sixteen
duplicates — the same arithmetic that cut the Dross Classifier's shake from
sixty-four frames to twelve.

---

## 6.2 Animation Layers

| Layer          | Required | Animated | Frames |
| -------------- | -------: | -------: | -----: |
| Main structure |        ✓ |       No |      1 |
| Machinery      |      `✓` |      `✓` |   `32` |
| Pistons        |      `—` |      `—` |    `—` |
| Belts          |      `—` |      `—` |    `—` |
| Fans           |      `—` |      `—` |    `—` |
| Glow           |      `✓` |      `✓` |   `16` |
| Steam          |      `—` |      `—` |    `—` |

**Animation FPS:**
`animation_speed = 0.25` — a sixteen-frame loop in a little over one second,
which is the same pace the 32-frame figure was aiming for and half the frames.

**The steam row is struck.** §5 of this document and the planet brief both say
there is no air here: no flame, no exhaust, no smoke, no steam plume. A steam
layer was in this table by inheritance from a wellhead on a world that has an
atmosphere.

**And the moving part is small — knowingly.** At 16.7 % of the building's own
box it is well under vanilla's 72–113 % band, and the plate is cut, so it cannot
grow. It is built anyway because it costs sixteen tiny derived sprites and gives
the building a running-versus-stopped tell it otherwise has none of; it is not
built under any illusion that it carries the read at play zoom. `04-the-core.md`
§26 is the standing warning, and this is the exception taken with its eyes open.

**Animation Loop:**
`Yes` — seamless. Nothing on this building has a stroke or a cycle start; it is
continuous flow, and a visible seam would read as a stutter.

**No pistons, no fans, no belts, deliberately.** Gas lift has no moving parts
below the wellhead. If the art shows something reciprocating, the mechanic has
been misread.

---

# 7. Layer Structure

```text
Building
│
├── Shadow
│
├── Base
│
├── Main Structure
│
├── Static Machinery
│
├── Pipes
│
├── Working Machinery
│
├── Lighting
│
├── Glow
│
└── Effects
```

### Layer Notes

**Shadow:**
Cast down-right, matching every vanilla building. The Core has
`day-night-cycle = 0` and a sky that does not move, so the shadow is fixed
forever — worth getting right once. The stack throws the long shadow; the base
plate throws almost none.

**Base:**
The anchored plate, bolt ring, gasketed bore collar, and the ground scarring
around it. Four frames, one per direction, drawn always.

**Main Structure:**
The valve stack itself, its flanges and hand-wheels. Identical in all four
directions.

**Static Machinery:**
Choke body, injection collar, riser elbow, the armoured sight port housing.
Rotates with direction.

**Working Machinery:**
Contents of the sight port only — melt moving past the window, and a small
flow-meter disc turning in the injection line. 32 frames, one direction.

**Lighting:**
The amber `missing_required_fluid` lamp. Drawn as a light, so it reads at
night — though the Core has no night, so this is really about local darkness
under a roof of other buildings.

**Glow:**
Two separate additive sheets that must not be merged: warm `#FF9E52` at the
riser seams and sight port, cold `#C7E5FF` at the injection collar. Merging
them into one sheet makes the middle of the building an unreadable brown.

**Effects:**
A faint cold vapour wisp lifting off the injection collar, rising a tile at
most and fading. **Not steam, not smoke, not exhaust** — a cryogenic boil-off
wisp, thin and blue-white. At pressure 5 it should look like it barely holds
together before it disperses.

---

# 8. Input / Output Visualisation

**Both fluid boxes are declared by this mod, not inherited.** What the pumpjack
and the mining drill hand down is unusable, and §19 records why.

```
north-facing:   . O .      O = molten kamacite out, faces north
                .   .
                . I .      I = helium-3 in, faces south
```

| Fluid | Position (facing north) | Faces | Volume |
| ----- | ----------------------- | ----- | -----: |
| `sae-molten-kamacite` | `[0, -1]` — centre of the north edge | north | 1000 |
| `sae-helium-3` | `[0, 1]` — centre of the south edge | south | 200 |

One in, one out, on opposite faces, both on the centre tile of their edge. Fluid
runs straight through the building, and the whole arrangement rotates with the
entity as a rigid pair.

### Pipes only join in straight lines

This is the rule the art has to be drawn against, and it is easy to get wrong.
A pipe connection has a **tile** and a **facing**, and the pipe that meets it
runs axis-aligned out of that tile's edge. There is no such thing as a diagonal
hookup. Two consequences:

* **Every flange must sit square to the edge it is on** and point straight out
  of it. A connector angled across a corner is one the player can never join
  cleanly, however good it looks.
* **A connection on a corner *tile* is still not diagonal.** The pumpjack's
  inherited output sat on tile `[1, -1]` and faced *north* — it left through the
  top edge at the right-hand tile. Reading that as "diagonally out from the
  shoulder" is what produced the elbow in `concept/v3-sheet.png`, and it was
  wrong. We no longer use a corner tile at all, but the distinction matters
  anywhere else it comes up.

## Item Inputs / Outputs

| | Location | Direction |
| --- | -------- | --------- |
| None | — | — |

Nothing solid enters or leaves. No inserter ever touches this building.

### Visual Requirement

Two connectors, and they must not be confusable — the player is threading two
different fluids into one 3×3 building and reversing them is the likeliest
mistake on the planet.

* The **intake** is pale, ribbed, insulated and rimed with frost: obviously
  cryogenic, obviously the cold side.
* The **riser** is bare, dark, heat-stained metal, sitting higher on the stack
  and glowing faintly at its flange, with the armoured sight window on it.
* They sit on **opposite faces**, which is a second, redundant cue on top of
  frost-versus-heat.

Both flanges are modelled into the plate, square to their edge — see the
foundry's `enable_working_visualisations` pattern in the briefs' §8.

---

# 9. Working Animation

## Animation Concept

Continuous flow, not a stroke. Helium goes down cold, melt comes up hot, and
the building's only job is to look like it is *moving fluid steadily* rather
than *cycling*. The player reads "working" from glow and flow, never from an
arm going up and down.

### Sequence

1. Idle: stack dark, sight port black, frost static, no glow, amber lamp lit if
   helium is missing.
2. Injection begins: a cold bloom brightens at the injection collar and the
   flow-meter disc starts to turn.
3. Melt arrives: the riser seams warm from `#D96B29` up toward `#FF9E52`,
   travelling **upward from the bore to the elbow** over several frames.
4. Steady state: melt visibly moving past the sight port, glow pulsing gently
   around the peak, boil-off wisp lifting from the collar.
5. Steady state continues — there is no completion event, the loop simply
   repeats.
6. On stop, everything fades back to (1) over the engine's own fade, not a
   scripted sequence.

**Frame Count:** `32`

**FPS:** `animation_speed = 0.4` → ~24 animation frames per second

**Loop Duration:** `~1.33` seconds

The upward travel in step 3 must divide evenly into the loop so it reads as
continuous flow rather than a repeating pulse train — two full travels per
32-frame loop is the target.

---

# 10. Effects

## Working Effects

* [x] Glow
* [ ] Steam
* [ ] Smoke
* [ ] Sparks
* [ ] Flames
* [ ] Electrical arcs
* [x] Moving fluids
* [x] Other: `cryogenic boil-off wisp at the injection collar`

### Effect Description

While working: the sight port shows melt moving; the riser seams glow warm and
pulse; the injection collar carries a faint cold bloom and lifts a thin
blue-white boil-off wisp about one tile before dispersing.

**No flame, no smoke, no exhaust plume, ever.** Pressure 5 is the Core's
defining number and it means nothing on the planet burns. A single lick of
flame on this building contradicts the reason boilers and furnaces are refused
here, and a player who sees one will reasonably conclude the mod is
inconsistent.

**No steam either**, despite the melt being at 1200 °C. Steam on the Core comes
from the settling recipes, in a different building; putting a plume on this one
blurs the split that the whole surface economy turns on.

---

# 11. DALL·E Generation Requirements

Generate square, at the largest size the tool supports (1024×1024 or better);
we downscale ourselves. Transparent background if the tool supports it,
otherwise flat magenta `#FF00FF` for keying — the colour appears nowhere on the
building.

## Master Concept Prompt

```text
A Factorio Space Age industrial building sprite: a sealed cryogenic gas-lift
wellhead, seen from a fixed high camera about sixty degrees above the horizon,
so mostly the top of the machine is visible with a shallow slice of its near
face and no far face at all, drawn almost orthographically like a game asset
rather than in perspective.

A low heavy armoured base plate, bolted and anchored into bare metallic ground,
carries an off-centre stepped stack of flanged valve bodies with hand-wheel
caps over a gasketed bore collar. One thick ribbed pipe in a pale insulating
sleeve enters the stack low from one side, rimed with white-blue frost that
blooms where cold meets warm metal. A second thick unlagged pipe leaves the
stack high on the opposite side, bare heat-stained metal glowing dull orange at
its seams, elbowing away to a flanged connection. A small armoured sight window
on that hot riser shows molten metal inside.

Dark iron-nickel grey-brown machined casing with pale nickel-white flange
bands. Cold cyan #8CC7E5 confined to the frosted intake side, molten orange
#D96B29 confined to the hot riser side, with clean dark metal between them so
the two never blend. Subtle wear, metal dust and condensation.

It must read as sealed pressure plumbing moving fluid, not as an oil derrick:
no nodding beam, no horsehead, no counterweight, no exposed rod, no derrick
tower, no flame, no fire, no smoke, no exhaust plume. Painted semi-realistic
industrial game art, strong readable silhouette, square footprint roughly three
tiles across, fully transparent background, no text, no logos, no characters,
no UI, no ground texture, no background scenery.
```

---

## Directional Prompts

**The four prompts that used to sit here were wrong and have been replaced.**
They asked for the intake "from the left edge", the riser "elbowed out to the
top-right corner", and "two capped, unused intake stubs" — which is the v3
design that §8 argues against in as many words: the corner-tile output was read
as a diagonal hookup, the elbow was the result, and the prototype now declares
one connection in and one out on opposite **centre** tiles with no stubs at all.
Following them would have produced art the player cannot plumb.

**One strip, four arrangements, one camera.** Generated together so they are
unmistakably four rotations of one machine, then split by
`tools/cut-rotation-strip.py --tiles 3`, which scales and centres every view on
its **base square** rather than on its content — otherwise the view whose pipes
stick out furthest is drawn smallest and sits off its own tile.

### Round 1 — the strip, and what it took

**Generated 2026-09-10 from the prompt below**, attached to
`concept/v4-sheet.png`, and cut with
`tools/cut-rotation-strip.py --tiles 3`. Kept at
`concept/rotation-strip-v2.png`.

**The first attempt returned the reference sheet itself, essentially
unchanged.** The sheet already carries four sprites in a row across its top, so
"draw four sprites in a row" read as "return this". The `DO NOT RETURN THE
ATTACHED IMAGE` block that opens the prompt is the answer, and the strip came
back correct with it in place. Two attempts in between died on ChatGPT's own
"Something went wrong" — server-side, and not worth reading anything into.

**Checked against the prototype rather than trusted**, because on this building
the pipes *are* the fluid boxes: north puts the riser out of the top edge and the
intake out of the bottom, which is output `{0,-1}` facing north and input
`{0,1}` facing south; east, south and west rotate the pair rigidly, exactly as
the entity does. Both pipes sit on the centre line of their edge, square to it,
with the flange passing through the connection tile. Rendered over a real grid
with the declared connections marked, which is the only way to see it.

### Rotation strip

```text
FACTORIO SPACE AGE BUILDING SPRITE -- FOUR-DIRECTION STRIP

== DO NOT RETURN THE ATTACHED IMAGE ==
The attachment is a REFERENCE for the machine's design only. Produce a NEW
image. Do not reproduce it, do not copy its layout, and do not return it with
changes. The attachment is a design document with a title, captions, detail
insets, an icon panel, a tile grid, a layer breakdown and a palette strip: the
output has NONE of those. The output is four machine sprites on an empty
transparent background and NOTHING else -- no title, no text, no captions, no
panel boxes, no borders, no palette, no insets, no icon, no grid.

Draw the machine from the attachment as four game sprites in ONE horizontal row,
evenly spaced, with clear empty space between them. Same building, same design,
same camera, same size and same lighting in all four. This is ONE machine drawn
four times with its plumbing moved, NOT four camera angles and NOT a turntable.

== THE MACHINE ==
The Vent Pump: a sealed cryogenic gas-lift wellhead on an airless metal world.
A heavy octagonal armoured base plate filling a 3x3 footprint, with a sealed
valve stack and hand wheel over the bore collar at its centre. Two connections
and no others:
  - a HOT RISER: bare dark heat-stained metal, standing higher than the stack,
    with an armoured sight port glowing orange, and a bolted flange at its mouth
  - a FROSTED INTAKE: pale, ribbed, insulated pipe heavily rimed with white
    frost, lower and squatter than the riser, with a bolted flange at its mouth

== THE FOUR ARRANGEMENTS, IN THIS ORDER ==
Left to right, and the riser and the intake are ALWAYS on OPPOSITE faces:
  1. NORTH -- riser out of the TOP edge,    intake out of the BOTTOM edge
  2. EAST  -- riser out of the RIGHT edge,  intake out of the LEFT edge
  3. SOUTH -- riser out of the BOTTOM edge, intake out of the TOP edge
  4. WEST  -- riser out of the LEFT edge,   intake out of the RIGHT edge

== HOW THE PIPES MUST SIT -- THIS IS THE PART THAT MATTERS ==
- Each pipe leaves from the CENTRE of its edge, on the middle tile of that edge,
  square to the edge and pointing STRAIGHT out of it along the axis
- NEVER diagonal, never out of a corner, never elbowed across a shoulder
- The riser and the intake are on the SAME straight line through the machine
- Each flange stops flush at the edge of the base plate. It does not float clear
  of the building and it does not stop short inside it
- NO other pipes, stubs, caps, blanks or spare ports anywhere. There are exactly
  two connections on this building

== CAMERA ==
Looking steeply down from above, MOSTLY ROOF with only a shallow near face
visible, square to the tile grid, identical in all four. The base plate reads as
a SQUARE footprint, never a diamond. Not rotated corner-on. The camera does NOT
move between the four -- only the plumbing does.

== HARD REQUIREMENTS ==
- FULLY TRANSPARENT BACKGROUND. No ground, no floor, no cast shadow, no panel
  borders, no labels, no text, no grid, no backdrop
- The four machines are the same size and sit on the same horizontal line
- The ONLY light is the riser's orange sight port and the faint heat at its
  flange. The frost is pale blue-white and does NOT glow
- No flame, no exhaust, no smoke, no steam plume, no dust: there is no air here
- No loose material anywhere
- Nothing extends past the base plate except the two pipes

== OUTPUT ==
One wide image, four sprites in a row on transparency, sharp and clean at full
resolution, in the rendering and finish of the attached sheet.
```

---

## Layer Prompts

### Main Structure

```text
[Master prompt] Static structure only: base plate, bolt rings, bore collar,
valve stack, flanges, hand-wheels, pipework, insulation and frost. Everything
cold and unlit — no orange glow anywhere, no light in the sight window, which
is dark and empty. Nothing that moves.
```

### Working Machinery

```text
Only the contents of a small armoured sight window, on a fully transparent
background, viewed from the same fixed high camera: molten orange metal
flowing steadily upward past the inside of the window, plus a small toothed
flow-meter disc turning in a separate circular port. Thirty-two frames in which
the flow travels the height of the window exactly twice, so the sequence loops
seamlessly with no visible seam. Nothing else in frame.
```

### Glow / Lighting

```text
Two separate glow plates on a fully transparent background, for additive
blending, with nothing else in frame.

Plate one: a warm orange #FF9E52 glow shaped to the seam lines of a vertical
pipe and to a small rectangular sight window, brightest at the window, falling
off within a few pixels of the seams.

Plate two: a faint cold #C7E5FF bloom shaped to a circular pipe collar, plus a
single small amber indicator lamp glow, both soft and low intensity.
```

### Effects

```text
A thin cryogenic boil-off wisp on a fully transparent background: pale
blue-white vapour lifting from a circular pipe collar, rising a short distance
and dispersing into nothing, thin and wispy in near-vacuum rather than a dense
plume. No smoke, no fire, no steam cloud, no snow, no particles leaving the
shape.
```

---

# 12. Image Processing

Generated artwork must be processed before being used by Factorio.

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

**Order matters, and the first three are the expensive ones.** Generators
attach a ground plane and a baked shadow to anything that looks like it stands
on the floor, and both have to come off before the sprite is cropped or the
crop lands in the wrong place. The baked shadow is not reusable — Factorio
needs the shadow as a separate `draw_as_shadow` sheet, and a shadow left in the
colour layer will double up against the engine's own.

---

# 13. Sprite Dimensions — measured

**This section used to say frame geometry was "taken verbatim from the
pumpjack", so the inherited shifts would stay correct.** That was a plan, not a
measurement, and it did not survive contact: the plates are cut from our own
strip, every canvas is a different size, and each shift is measured off its own
base plate. The pumpjack's numbers are gone from the prototype along with its
sprites. Sprites are authored at 2× and drawn at `scale = 0.5`.

| Direction | Colour plate | Shift | Shadow | Shadow shift | Base measured |
| --------- | ------------ | ----- | ------ | ------------ | ------------: |
| north | `base-north.png` 203 × 281 | `{ 0.00781, −0.23438 }` | 441 × 301 | `{ 1.71094, −0.23438 }` | **3.000** tiles |
| east  | `base-east.png` 248 × 198  | `{ 0, −0.02344 }` | 420 × 218 | `{ 1.18750, −0.02344 }` | 2.969 tiles |
| south | `base-south.png` 202 × 265 | `{ −0.00781, −0.14844 }` | 427 × 285 | `{ 1.59375, −0.14844 }` | 2.984 tiles |
| west  | `base-west.png` 247 × 198  | `{ −0.01562, −0.02344 }` | 419 × 218 | `{ 1.17188, −0.02344 }` | 2.953 tiles |

**Every number is measured off the base plate, never off the content.** The
pipes reach further in some views than others — that is the whole point of them —
so centring on content slides the machine off its own tile in exactly the views
whose plumbing overhangs most. The scale is set once, from the north view's base
square fitted to 3.000 tiles, and used for all four; the other three land at
2.953–2.984, all *under* the footprint, which is the safe side to miss on. A base
wider than its footprint interleaves with its neighbours, and the Arc Mast at
3.14 tiles is the standing lesson.

**The y shifts differ by axis and that is not an error.** A riser leaving through
the top edge is drawn standing up, so it adds height above the base and pushes
the base low in its canvas: north needs a quarter tile of lift where east and
west need almost none.

### The working glow

| Direction | Sheet | Frame | Shift | Glass measured |
| --------- | ----- | ----- | ----- | -------------: |
| north | `port-north.png` 168 × 70 | 21 × 35 | `{ −0.05469, −1.70313 }` | 12 × 29 px |
| east  | `port-east.png` 192 × 56  | 24 × 28 | `{ 1.39062, −0.35156 }` | 16 × 12 px |
| south | `port-south.png` 184 × 58 | 23 × 29 | `{ −0.07812, 1.02344 }` | 11 × 27 px |
| west  | `port-west.png` 208 × 56  | 26 × 28 | `{ −1.32031, −0.35156 }` | 16 × 13 px |

16 frames, `line_length` 8, `animation_speed = 0.25`, `draw_as_glow`, no
`always_draw` — so it is drawn only while the pump is working. Each shift is the
port crop's own offset plus its plate's, both measured. Built by
`tools/build-fill-frames.py`, which is new and exists because
`build-glow-frames.py`'s two modes are one-shot charge and discharge built round
an envelope that starts and ends dark; a level in a sight glass loops and never
goes out.

**The plate keeps its glow and this sheet adds to it.** The first attempt split
the port into an unlit base and a separate glow the way the rest of the mod does
it, and it does not work here: `split-glow.py` wants emissive parts that are
strongly chromatic against near-neutral iron-nickel, and this riser is copper.
Every threshold that saved the port took half the riser with it — measured, 1157
"hot" pixels across a 179 × 226 box when the port is 18 × 32. A brightening over
a lit plate is also the truer reading, since a wellhead full of melt is warm
whether or not it is pumping.

**`tools/check-footprint.py` reports 0.39 tiles of overhang on east and west, and
that is the tool measuring the wrong thing.** It fits the declared box to the
*visible* bounds, and in those two views the visible bounds include the pipes,
which are supposed to hang over the edge and reach the next tile. The base is
what has to fit, and it does.

## The numbers this section used to carry

**Tile Size:**
`64` px authored / `32` px drawn

**Building Width:**
`~192` px drawn — the 3×3 footprint

**Building Height:**
`~192` px drawn, plus the stack overhanging upward

**Sprite Width:**
`261` px (base frame), `206` px (animation frame)

**Sprite Height:**
`273` px (base frame), `172` px (animation frame)

**Spritesheet Width:**
`1044` px base (4 frames × 261) · `1648` px animation (8 per row × 206)

**Spritesheet Height:**
`273` px base (1 row) · `688` px animation (4 rows × 172)

**Frame Count:**
`4` base (one per direction) · `32` animation

**Line Length:**
`4` base · `8` animation

Shadow sheets match their colour sheets frame for frame. The base sprite is
wider than the 3×3 collision box on purpose — the pumpjack's is too — so the
plate and its ground scarring can overhang the footprint the way every vanilla
building's does.

---

# 14. File Structure

```text
graphics/
└── entity/
    └── vent-pump/
        ├── vent-pump-base.png            (4 frames, one per direction)
        ├── vent-pump-base-shadow.png     (4 frames, draw_as_shadow)
        ├── vent-pump-working.png         (32 frames, sight port + flow disc)
        ├── vent-pump-glow-hot.png        (32 frames, additive)
        ├── vent-pump-glow-cold.png       (32 frames, additive)
        └── vent-pump-lamp.png            (1 frame, amber status light)
```

Concept art from the generation pass lives alongside, in
`graphics/entity/vent-pump/concept/`, and is kept: it is what the four
directional frames have to stay faithful to.

---

# 15. Factorio Prototype

**Prototype Type:**
`mining-drill`

**Prototype Name:**
`sae-vent-pump`

### Graphics

```lua
-- Replaces the inherited pumpjack graphics_set in prototypes/core/entities.lua.
-- The base is drawn always, as a 4-frame directional working visualisation,
-- exactly as the pumpjack draws its own base beneath the horsehead.
local vp = "__space-age-extended__/graphics/entity/vent-pump/"

local base_sheets = {
  { filename = vp .. "vent-pump-base.png",
    priority = "extra-high", width = 261, height = 273,
    shift = util.by_pixel(-2.25, -4.75), scale = 0.5 },
  { filename = vp .. "vent-pump-base-shadow.png",
    width = 261, height = 273, scale = 0.5,
    draw_as_shadow = true, shift = util.by_pixel(-2, -5) }
}

local base_visualisation = { always_draw = true, secondary_draw_order = -1 }
for i, dir in ipairs({ "north_animation", "east_animation",
                       "south_animation", "west_animation" }) do
  local layers = {}
  for _, sheet in pairs(base_sheets) do
    sheet = table.deepcopy(sheet)
    sheet.x = sheet.width * (i - 1)
    table.insert(layers, sheet)
  end
  base_visualisation[dir] = { layers = layers }
end

pump.graphics_set = {
  animation = {
    north = { layers = {
      { filename = vp .. "vent-pump-working.png",
        priority = "high", animation_speed = 0.4, scale = 0.5,
        line_length = 8, width = 206, height = 172, frame_count = 32,
        shift = util.by_pixel(-4.5, -29) }
    } }
  },
  working_visualisations = {
    base_visualisation,
    { animation = { filename = vp .. "vent-pump-glow-hot.png",
        draw_as_glow = true, blend_mode = "additive",
        animation_speed = 0.4, scale = 0.5, line_length = 8,
        width = 206, height = 172, frame_count = 32,
        shift = util.by_pixel(-4.5, -29) } },
    { animation = { filename = vp .. "vent-pump-glow-cold.png",
        draw_as_glow = true, blend_mode = "additive",
        animation_speed = 0.4, scale = 0.5, line_length = 8,
        width = 206, height = 172, frame_count = 32,
        shift = util.by_pixel(-4.5, -29) } }
  }
}
pump.graphics_set_flipped = nil
```

`graphics_set_flipped` must be cleared, not inherited. The pumpjack ships a
mirrored variant so its horsehead can nod the other way; this building has no
handed part, and leaving the inherited flipped set in place would point at
pumpjack files that no longer describe the entity.

### Other Visual Properties

```text
Animation:
32 frames, animation_speed 0.4, single direction, seamless loop. Sight port
contents and flow-meter disc only.

Shadow:
Separate draw_as_shadow sheet, 4 frames, matching the base frame for frame.
Cast down-right. The Core has day-night-cycle 0, so it never moves.

Working Visualisation:
Base (always_draw, 4 directions, static) + hot glow (additive) + cold glow
(additive). Three entries, in that order.

Lights:
One amber lamp for missing_required_fluid. Small, on the stack.

Fluid Boxes:
input_fluid_box  — helium-3, volume 200, three connections at [-1,0] W,
                   [1,0] E, [0,1] S; rotate with the entity.
output_fluid_box — molten kamacite, corner connection whose position changes
                   per direction: N [1,-1], E [1,1], S [-1,1], W [-1,-1].

Circuit Connections:
Inherited from the pumpjack (circuit_connector_definitions["pumpjack"]). The
connector sprite sits on the base plate and must not be occluded by the new
stack — check this before the art is signed off.
```

---

# 16. Icon

**Done 2026-09-10 — `graphics/icons/vent-pump.png`, derived from the north plate
rather than generated separately**, so it cannot disagree with the building it is
an icon for. The whole machine, riser and frosted intake included: both survive
at 32 px, and they are what makes it unmistakably this building rather than
another grey box. What follows is the record of what was asked for.


**Icon Required:** ✓

**Icon Size:**
`64×64`

**Icon Concept:**
The valve stack alone, seen straight on, with one frosted pale-blue pipe
entering low from the left and one glowing orange pipe leaving high to the
right. Drop the base plate entirely — at 32 px it is a grey smudge that eats
the silhouette. The read at inventory size is a dark stepped tower with one
cold end and one hot end, which is the same read as the building.

### Icon Prompt

```text
Factorio "Space Age" item icon. A small sealed wellhead valve stack: three
stacked flanged valve bodies in dark iron-nickel grey-brown metal with pale
nickel-white flange bands and hand-wheel caps. A ribbed, frost-rimed pale blue
insulated pipe enters low from the left; a bare heat-stained pipe glowing dull
orange leaves high to the right. Cold cyan #8CC7E5 on the left, molten orange
#D96B29 on the right, dark clean metal between them.

Rendered in a semi-realistic sci-fi industrial style — not flat, not cartoon,
not photo-real. Three-quarter, slightly top-down perspective, as if resting on
a workbench. Soft single-direction studio lighting from the upper-left, visible
specular highlight, subtle ambient occlusion where surfaces meet, gentle drop
shadow beneath the object. The object fills roughly 75–85% of the frame,
centred, with even padding on all sides. Bold simple silhouette that still
reads at 32 pixels. Background fully transparent. No text, no logos, no
watermark, no border, no frame, no ground or platform under the object, no
scene or background elements. Square canvas.
```

The icon should remain recognisable at Factorio's normal inventory/UI scale.

---

# 17. Visual QA Checklist

### Building

* [ ] Correct tile size
* [ ] Correct perspective
* [ ] Correct scale
* [ ] Clear silhouette
* [ ] Looks like Factorio
* [ ] Matches intended planet
* [ ] Inputs are visually understandable
* [ ] Outputs are visually understandable

### Directions

* [ ] North
* [ ] East
* [ ] South
* [ ] West
* [ ] All directions represent the same building

### Animation

* [ ] Working animation is readable
* [ ] Animation loops correctly
* [ ] No parts change shape unexpectedly
* [ ] Static components remain static
* [ ] Effects align correctly

### In-Game

* [ ] Shadow aligns with building
* [ ] Inserters align correctly
* [ ] Pipes align correctly
* [ ] Building doesn't overlap neighbouring entities incorrectly
* [ ] Building is recognisable when surrounded by other machines
* [ ] Performance is acceptable

### Mod-specific

* [ ] Nothing on the building looks like it is burning
* [ ] The cold accent and the hot accent do not blend into each other
* [ ] The output elbow cannot be mistaken for an input stub
* [ ] The circuit connector is not occluded by the stack
* [ ] It does not read as a pumpjack

---

# 18. Final Asset Checklist

```text
[ ] Master concept
[ ] North sprite
[ ] East sprite
[ ] South sprite
[ ] West sprite

[ ] Shadow
[ ] Idle animation
[ ] Working animation
[ ] Working machinery layer
[ ] Lighting layer
[ ] Effects layer

[ ] Icon
[ ] Spritesheets
[ ] Factorio prototype
[ ] In-game test
```

---

# 19. Design Notes / Iteration History

### 2026-09-10 — the plates, and a prompt that described the wrong building

**The four directional prompts in §11 were wrong and had to be replaced before
anything could be generated.** They asked for the intake "from the left edge",
the riser "elbowed out to the top-right corner", and "two capped, unused intake
stubs" — the v3 design, which §8 of this same document argues against in as many
words. The prototype had already moved to one connection in and one out on
opposite centre tiles with no stubs; the prompts had not moved with it. Following
them would have produced art the player cannot plumb.

They are replaced by a single rotation-strip prompt that matches §8, and the
strip was cut with `tools/cut-rotation-strip.py --tiles 3` — which is
`cut-crust-tap.py` generalised, this building being its second user.

**Its base detector had to be rewritten for this building, and the failure is
worth recording.** It kept columns taller than a share of the tallest column,
which works only while the protruding part is short. This machine's pipes are as
tall as the base in the north and south views — they leave through the top and
bottom edges, straight at the camera — so they raised the threshold and pushed
the real base columns below it. In east and west the same pipes leave sideways,
are short, and dragged the measured base *wider* instead. Four bases that are
really 408, 401, 408 and 401 px measured as 388, 401, 395 and 401.

A row is a better witness than a column: the base is the widest thing on most
rows, and the pipes only widen the rows they actually cross, so the median row is
the base whichever way the plumbing points. With that, the four cut to 3.000,
2.969, 2.984 and 2.953 tiles instead of 3.016, 3.094, 3.047 and 3.094 — from
overhanging on two views to under-running on three.

**One consequence outside this building:** the new measurement moves the Crust
Tap's plates by about a pixel. Those are shipped, declared in
`prototypes/core/crust-tap.lua` and verified against that building's own §13, so
they are deliberately not re-cut. The tool says so at the top.


### Version 0 — inherited pumpjack (current, in repo)

`prototypes/core/entities.lua` deep-copies `pumpjack` and changes no graphics
at all, so the building in game today *is* an oil derrick, horsehead and all,
standing on a planet that has never had a drop of oil. It was the right
placeholder — it made the entity type and the `required_fluid` coupling
testable without any art — and it is the thing this document exists to replace.

### Version 1 — gas-lift wellhead (this document)

The concept, the palette, the layer split and the prompts in §11 and §16 are
written; `tools/generate-building-art.py` reads them straight out of this file,
so there is no second copy to keep in step.

**The API route is dead and the browser route is the one that works.** The
first generation pass was attempted through the OpenAI API and refused — the
account authenticates but has a zero credit balance (`insufficient_quota` /
`credit_balance_exhausted`, on text calls as well as image calls). Everything
since has gone through ChatGPT in the browser; see template Appendix B.

### Round log

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| 1 | sheet | `concept/v1-sheet.png`. The machine is right and the anti-read held completely — sealed valve stack, frost-jacketed injection line, glowing sight port, heavy anchored base plate, and not a trace of derrick, horsehead, beam or flame. Palette obeys the split: cyan confined to the cold side, orange to the hot side, clean metal between. **But the four direction panels are a turntable** — four camera angles of the machine rotating in front of the viewer, which is exactly what §5 says must not be asked for and which is unusable as sprite reference. | **Machine accepted; direction panels rejected** | Redraw NORTH / EAST / SOUTH / WEST as four *plumbing arrangements* under one fixed camera: identical base, stack, bolt rings, lighting and shadow in all four, with only the intake and riser attachment points moving a quarter turn between them. |
| 2 | sheet | `concept/v2-sheet.png`. **The turntable is gone.** All four panels now share one fixed camera: identical base plate, identical valve stack, identical lighting and shadow, with only the intake and riser attachment points moving a quarter turn between them — which is exactly the four *arrangements* §5 asks for, and is usable as sprite reference. The captions state the coupling correctly (intake from north, hot output to south, and so on round). Machine, palette split and anti-read all carried over unchanged. Layer breakdown matches §7 and the sight-port fill runs 0 to 100 per cent. | **Accepted — `concept/v2-sheet.png` is the locked design** | None. |
| 3 | sheet | `concept/v3-sheet.png`. Drawn against the *inherited* fluid boxes — three edge-midpoint intakes and a rotating corner output. NORTH came back correct; EAST, SOUTH and WEST kept a fixed intake arrangement and moved only the riser, so an intake sat on the edge that had to stay clean and two panels had four intakes instead of three. The corner riser was also drawn as an elbow reaching **diagonally** past the shoulder, which is not a thing that exists: a connection on a corner *tile* still faces straight out through an edge. | **Rejected, and the design changed under it** | Superseded by the fluid-box replacement below. |
| 4 | sheet | `concept/v4-sheet.png`. Drawn against the replaced fluid boxes: **one intake, one riser, opposite faces, both on the centre tile of their edge, both square to it.** All four rotations correct and captioned; the tile-grid panel draws the straight line through the machine. Anti-read holds. | **Accepted — `concept/v4-sheet.png` is the locked design** | None. |

Two things to expect on the first real pass, and to check for before spending
another generation on refinement:

* **The camera.** Image models default to a clean isometric three-quarter view
  and will need pushing toward Factorio's flatter, higher angle. §4 explains why
  the template's "45°" was not used in the prompts.
* **The base plate.** Generators attach a ground plane and a baked shadow to
  anything resting on a surface. Both come off in processing (§12), but if the
  building is generated *sitting in a hole* rather than *bolted to a flat
  surface*, the crop has nothing clean to work with and the prompt needs the
  fix, not the image.

### The fluid boxes were replaced, and why

Three rounds of art were spent trying to serve the inherited plumbing before it
became clear the plumbing was the problem. The pumpjack contributes an output on
a **corner tile that walks around the four corners** as the building rotates; the
electric mining drill contributes **three** inputs at edge midpoints. Seven
possible hookups on a 3×3, of which a player uses two — and no arrangement of art
makes the other five look intended rather than broken.

`prototypes/core/entities.lua` now declares both boxes: one in, one out, opposite
faces, centre tile, facing straight out. The building is simpler, the art is
honest, and the fluid path reads as the single straight line the pipes in front
of it will actually form.

### Final

The concept sheet is approved and the design is locked. What remains is the
production pipeline of template Appendix C — canonical plate, idle plate, the
four directional frames derived from it, glow by differencing, then the sprite
canvas. **Stop prompting for the design now**: every later image is an edit of
`concept/v2-sheet.png`, never a fresh generation.
