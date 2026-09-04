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
| Idle state    |        ✓ |    `1` |      `4` |
| Working state |        ✓ |   `32` |      `1` |

The base is static and always drawn (`always_draw = true`), exactly as the
pumpjack draws its base under its horsehead. Only the working layer animates,
and it needs **one** direction because the sight port and flow disc sit on the
stack, which does not rotate.

---

## 6.2 Animation Layers

| Layer          | Required | Animated | Frames |
| -------------- | -------: | -------: | -----: |
| Main structure |        ✓ |       No |      1 |
| Machinery      |      `✓` |      `✓` |   `32` |
| Pistons        |      `—` |      `—` |    `—` |
| Belts          |      `—` |      `—` |    `—` |
| Fans           |      `—` |      `—` |    `—` |
| Lights         |      `✓` |      `✓` |   `32` |
| Glow           |      `✓` |      `✓` |   `32` |
| Steam          |      `✓` |      `✓` |   `32` |

**Animation FPS:**
`animation_speed = 0.4` (24 frames of animation per second of game time at 60
UPS, so the 32-frame loop runs in ~1.33 s). Slower than the pumpjack's 0.5.

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

Read off the two inherited fluid boxes. There are **four possible hookups** on
a 3×3 building, and the art has to accommodate all of them.

## Item Inputs

| Input | Location | Direction |
| ----- | -------- | --------- |
| None  | —        | —         |

## Item Outputs

| Output | Location | Direction |
| ------ | -------- | --------- |
| None   | —        | —         |

Nothing solid enters or leaves. No inserter ever touches this building, which
frees all four sides for pipe.

## Fluid Inputs

Inherited from `electric-mining-drill.input_fluid_box`. Single positions, so
they rotate with the entity. Volume 200.

| Fluid     | Location (entity-relative, facing north) | Connection Type |
| --------- | ---------------------------------------- | --------------- |
| `sae-helium-3` | `[-1, 0]` — mid-west edge  | Input pipe connection, facing west |
| `sae-helium-3` | `[1, 0]` — mid-east edge   | Input pipe connection, facing east |
| `sae-helium-3` | `[0, 1]` — mid-south edge  | Input pipe connection, facing south |

## Fluid Outputs

Inherited from `pumpjack.output_fluid_box`. A `positions` array, so the
connection sits at a **different corner in each of the four rotations** —
this is the pumpjack's signature quirk and the reason it is worth rotating.

| Fluid | Location by direction | Connection Type |
| ----- | --------------------- | --------------- |
| `sae-molten-kamacite` | N `[1, -1]` · E `[1, 1]` · S `[-1, 1]` · W `[-1, -1]` | Output pipe connection |

### Visual Requirement

The three input stubs and the one output elbow must be **visually
distinguishable at a glance**, because the player will be threading two
different fluids into the same 3×3 building and getting them backwards is the
most likely mistake on the planet.

* The **three input stubs** are pale, ribbed, insulated, and rimed — obviously
  cryogenic, obviously the same fluid as each other, and obviously not the
  output.
* The **one output elbow** is bare, dark, heat-stained metal, sitting higher on
  the stack, and glowing faintly at its flange. It sits on a **corner**, where
  no input ever sits, so corner-versus-edge is a second, redundant cue.
* Only one input is used in practice. The other two stubs should read as
  **capped and idle** rather than as three live pipes, or the building looks
  like it wants three helium lines.

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

Four arrangements from **one fixed camera**, not four viewpoints. Generate the
north frame first, approve it, then produce the other three by rotating the
plumbing in the approved image rather than re-generating from scratch — that is
the only reliable way to keep one machine across four frames.

### North

```text
[Master prompt] Plumbing arranged for the north-facing frame: the insulated
frosted intake pipe enters the stack from the left edge of the base plate, and
the hot glowing riser elbows out to the top-right corner of the base plate.
Two additional capped, unused intake stubs sit at the right edge and the bottom
edge, clearly sealed and idle.
```

### East

```text
[Master prompt] The same machine, same camera, same size, same fittings, same
lighting. Only the plumbing is rotated a quarter turn clockwise: the frosted
intake enters from the top edge, the hot riser elbows out to the bottom-right
corner, and the two capped idle stubs sit at the bottom edge and the left edge.
```

### South

```text
[Master prompt] The same machine, same camera, same size, same fittings, same
lighting. Plumbing rotated a half turn from the north frame: the frosted intake
enters from the right edge, the hot riser elbows out to the bottom-left corner,
and the two capped idle stubs sit at the left edge and the top edge.
```

### West

```text
[Master prompt] The same machine, same camera, same size, same fittings, same
lighting. Plumbing rotated a quarter turn anticlockwise from the north frame:
the frosted intake enters from the bottom edge, the hot riser elbows out to the
top-left corner, and the two capped idle stubs sit at the top edge and the
right edge.
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

# 13. Sprite Dimensions

Frame geometry is taken **verbatim from the pumpjack**, so the inherited
`shift` values in the graphics set stay correct and the new art drops straight
into the existing prototype. Sprites are authored at 2× and drawn at
`scale = 0.5`.

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

### Version 0 — inherited pumpjack (current, in repo)

`prototypes/core/entities.lua` deep-copies `pumpjack` and changes no graphics
at all, so the building in game today *is* an oil derrick, horsehead and all,
standing on a planet that has never had a drop of oil. It was the right
placeholder — it made the entity type and the `required_fluid` coupling
testable without any art — and it is the thing this document exists to replace.

### Version 1 — gas-lift wellhead (this document)

The concept, the palette, the layer split and the prompts in §11 and §16 are
written and ready to fire; `tools/generate-building-art.py` reads them straight
out of this file, so there is no second copy to keep in step.

**No art has been generated yet.** The generation pass was attempted and the
API refused it — the account authenticates fine but has a zero credit balance
(`insufficient_quota` / `credit_balance_exhausted`, on text calls as well as
image calls). Nothing about the prompts has been tested against a generator, so
every art claim below Version 0 is still a proposal on paper.

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

### Final

`[Open until the four directional frames are approved.]`
