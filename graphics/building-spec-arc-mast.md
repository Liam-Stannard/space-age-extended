# Factorio Building — Art & Implementation Specification

**Arc Mast.** Filled from `building-spec-template.md`. Every gameplay number
here is the implemented value read off `prototypes/core/storms.lua`,
`prototypes/core/planet.lua` and the vanilla prototypes they deep-copy, not a
proposal. The art sections *are* proposals: the building currently wears
vanilla's lightning collector unmodified, and this document exists to
commission a replacement.

**The central art decision — see §3.1.** Fulgora's lightning collector is a
slender tuning-fork antenna: light, tall, delicate, built to sip a strike that
arrives every ten seconds. The Arc Mast stands under a strike **nine times
rarer and six times heavier**, on a world at **gravity 50**, and its job is to
*take the hit so nothing else does* and hold 4000 MJ afterwards. It should read
as a **grounded sacrificial anvil** — a squat, over-braced, deeply earthed
lightning terminal with a burnt-away tip and a storage drum bigger than its
head — not as a recoloured antenna.

---

# 0. Generation Contract

**Where generation happens:** the browser (ChatGPT's image tool), signed in as
the user. `tools/generate-building-art.py` reads the same §11 blocks and stays
the fallback, but the OpenAI account it uses has no credits, so the browser is
the live route. See template Appendix B for what the composer does to a prompt.

| # | Asset | Canvas | Gate | State |
| - | ----- | ------ | ---- | ----- |
| 1 | Master concept | portrait 2:3 | Silhouette approved against §3.1 and §17 | **round 2, not yet passed** |
| 2 | Main structure (unlit) | portrait 2:3 | Same machine, nothing lit | blocked on 1 |
| 3 | Directional frames | — | n/a — one direction, see §5 | n/a |
| 4 | Glow plates | portrait 2:3 | Aligns with stage 2 geometry | blocked on 1 |
| 5 | Effects plate | portrait 2:3 | Reads at one tile | blocked on 1 |
| 6 | Icon | square | Legible at 32 px | not started |

Stage 2 is deliberately not generated in round one: it is the master prompt
plus "nothing lit", and re-approving the master would throw it away.

## 1. Building Overview

**Building Name:**
`Arc Mast`

**Internal Prototype Name:**
`sae-arc-mast`

**Building Type:**
`lightning-attractor`, deep-copied from `lightning-collector`. The entity type
is load-bearing twice over: it is the only type the planet's
`lightning_properties.priority_rules` can name, and it is the only one that
converts a strike into an `electric` energy source. `sae-arc-mast` carries a
`priority_bonus` of 10000 on the Core, so a mast outbids every other structure
on the surface for the strike — which is the whole safety mechanic.

**Planet / Environment:**
`The Core.` Not gated by `surface_conditions` — it is gated by there being
nothing to catch anywhere else. Arc storms exist only where
`lightning_properties` is declared, and the Core is the only surface in the mod
that declares them. A mast on Nauvis would build, sit at zero, and drain 100 kW
forever.

**Purpose:**
Catches an arc strike and **banks it as electricity**. The hazard and the power
supply are the same event: 600 damage and 4000 MJ arriving once per chunk every
ninety seconds, of which the mast keeps **35%** — 1400 MJ per strike — into a
4000 MJ buffer. Sited for cover first and power second.

**Technology Unlock:**
`Arc Masts` (`sae-arc-masts`, tier 0 — see `design/04-the-core.md` §6).
Prerequisite `sae-core-survey`; 200 units of the seven vanilla packs at 60 s,
since no geodynamic pack can exist before the surface has power.

---

## 2. Gameplay Dimensions

Inherited from `lightning-collector` unless stated.

**Tile Size:**
`2×2` selection over a `1.4×1.4` collision — but see §13: the *sprite* is
roughly `3.5×7` tiles, because most of this building is drawn above its
footprint.

**Collision Box:**
`[-0.7, -0.7] → [0.7, 0.7]`

**Selection Box:**
`[-1, -1] → [1, 1]`

**Placement Restrictions:**
None. No `surface_conditions`, no resource requirement, no terrain
restriction. `fast_replaceable_group` and `next_upgrade` are both cleared, so
it never fast-replaces a lightning collector and offers no upgrade path.

**Rotation:**
`None.` `lightning-attractor` has no direction — the entity cannot be rotated
in the world, and the prototype has no per-direction sprite slot to fill. **One
frame, one orientation, for the life of the building.** This is the single
biggest difference from `building-spec-vent-pump.md`, and it removes the whole
class of four-frame consistency problems from generation.

**Crafting Speed:**
n/a. The relevant rates are `efficiency = 0.35` (vanilla 0.4) and
`range_elongation = 20` (vanilla 25) — it catches less of what it takes, and
reaches less far, because out here a strike is an event rather than weather.

**Energy Consumption:**
`100 kW` standby drain (vanilla 2.5 MJ). Strikes are nine times rarer, so
standby loss between them is what decides whether a mast is worth building; the
lower drain is the compensation.

**Energy Type:**
`electric`, `usage_priority = "primary-output"`. Buffer 4000 MJ, output flow
limit 40 MW. Power leaves through the electric network only — a mast is **not**
a pole and has no wire connectors of its own, so it has to stand inside some
pole's supply area to deliver anything.

**Health and resistances:**
`max_health = 200`, fire 90%, electric 100% (inherited). It is immune to the
thing that hits it, which is the point.

**Recipe:**
30 kamacite plate · 5 welded plate · 10 processing unit · 5 accumulator, 10 s.
`stack_size = 10`, `weight = 40000` — 25 to a rocket.

---

# 3. Visual Design

## 3.1 Design Concept

**Primary Visual Theme:**
**Grounded sacrificial anvil.** A deliberately over-built lightning terminal:
mass low, tip burnt, everything bolted to the crust. Heavy electrical
infrastructure, not an antenna, and explicitly **not** a weapon — nothing here
points at anything or tracks a target.

**Overall Appearance:**
A wide splayed grounding skirt bolted flat into bare metal, carrying a short,
thick, three-sided braced column that tapers as it rises. Two-thirds of the way
up, a stack of ribbed ceramic insulators separates the column from a stubby
**sacrificial tip** — a pitted, cratered, part-ablated tungsten spike clamped in
a replaceable collar. At the base, hugging the skirt, sits an armoured
horizontal **surge drum**, ribbed for cooling, visibly the heaviest single
component on the building.

Proportions are the message. Fulgora's collector is a slender thing with a big
head; this is a big base with a small, damaged head. At gravity 50 nothing
slender stands up, and nothing that took 600 damage a minute ago looks new.

**Silhouette:**
A broad triangular base narrowing into a short braced column, ending in a blunt
notched spike — not a fork, not a dish, not a barrel. Read from altitude:
*"something earthed, and something stored."* The surge drum breaks the tower
outline at the bottom-left so the shape is asymmetric and recognisable in a row
of other buildings.

**Visual Complexity:**
`Medium.` The base carries the detail; the column stays plain so the tip reads
cleanly against the sky when a strike lands on it.

**Visual Age:**
`Advanced.` Machined, purposeful, unglamorous. Not experimental — this is the
first structure the player builds on the Core after the vent pump, and it
should look like proven kit that has already been hit a hundred times.

---

## 3.2 Key Visual Features

The building should contain:

* A **splayed grounding skirt** — a wide, low, bolted anchor plate with four
  radial earthing straps driven into the crust and visible scorch fanning out
  from where they enter the ground.
* A **short braced column** — a heavy three-sided lattice with an armoured buss
  bar running up its centre, cross-braced hard at two heights.
* A **ceramic insulator stack** — four or five ribbed pale ceramic discs
  separating the tip assembly from the column, the one obviously non-metal
  element on the building.
* A **sacrificial tip** — a blunt tungsten spike, pitted and cratered, its
  upper third discoloured to straw and blue-grey from repeated ablation, held
  in a bolted collar that reads as replaceable.
* An **armoured surge drum** at the base — a ribbed horizontal cylinder with
  cast end caps and a single small steady green lamp, the visual weight that
  says the strike is being kept rather than dumped.

### Signature Feature

**The tip is damaged and the base is enormous.** Every other lightning
structure in the game gets thinner and more elegant as it rises; this one gets
smaller and *worse*. The burnt spike over a massive earthed drum is the whole
mechanic in one silhouette — you stood in the way, you got paid for it, and the
thing that pays you is also eating the building.

---

## 3.3 Colour Palette

Metal hexes match `building-spec-vent-pump.md` so the Core's buildings read as
one set. The arc hex is **not** a free choice: `sae-arc` is vanilla's
`lightning` prototype with only its damage and energy changed, so the strike
itself arrives in vanilla's colours and anything the mast glows must sit
alongside them without clashing.

**Primary:**
Dark iron-nickel grey-brown machined casing, `#4A463F` → `#6E685C`. Faintly
warm, slightly oxidised — meteoric iron, not blue steel.

**Secondary:**
Pale nickel-white machined bands and flange faces, `#B9B4A8`, used on the skirt
bolt rings and the drum end caps to break up the mass.

**Metal:**
Warm dark steel, desaturated, so the arc colour is the only saturated thing on
the building.

**Ceramic:**
Pale vitreous sand `#C9C0AC` with cooler grey shadow between the ribs. The
insulator stack should be the lightest value on the building and the first
thing the eye finds after the tip.

**Accent — the arc:**
Violet-white, `#C9B6FF` ramping to `#FFFFFF` at the core of a filament, matched
to vanilla lightning. Confined to the tip, the top two insulator ribs, and the
buss bar seam.

**Accent — the tip metal:**
Ablation discolouration only: straw `#C2A05B` through blue-grey `#7C8794` on
the upper third of the spike. This is temper colour on tungsten, **not** heat
glow — the tip is cold between strikes and must not be lit.

**Working Glow:**
Violet-white `#C9B6FF` at the tip and along the buss bar during charge and
discharge only. **Nothing on this building glows at rest.** The buffer level is
not visible to the engine (see §6.1), so a permanent glow would be a lie the
player learns to ignore.

**Warning / Status Lights:**
One small steady green lamp on the surge drum, decorative — the prototype gives
no hook for a state-driven indicator, and a lamp that never changes is honest
only if it never claims to mean anything. No red, no amber, no blinking.

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

**Note on the perspective line above — and it is different from the vent
pump's.** Factorio's camera sits roughly 60° above the horizon, so a *flat*
building shows mostly its roof. A **tall** one does not: vanilla cheats,
drawing anything above about two tiles progressively closer to elevation view
so it leans toward the viewer, which is why the lightning collector, the big
electric pole and the rocket silo all show their sides rather than their tops.
The Arc Mast is a tall object and gets the same treatment — **base seen from
above at ~60°, column and tip seen almost from the side** — with the whole
thing effectively orthographic. Asking a generator for "45° isometric" produces
a different game; asking for "a photo of a tower" produces a vanishing point.
§11 says this the long way round rather than naming an angle.

### Style Reference Buildings

1. `Lightning collector` (Space Age)
2. `Substation` (base)
3. `Accumulator` (base)

**Reason for references:**
Take from the **lightning collector** only its *envelope* — the height, the
drawing box, and the trick of leaning a tall object toward the camera. Take
none of its design: the tuning-fork head, the slenderness and the pale enamel
all belong to Fulgora and are exactly what makes the current placeholder wrong
here. Take from the **substation** the ceramic insulator stacks, the bolted
armoured base and the sense of a live node in a grid. Take from the
**accumulator** the squat, ribbed, heavy read of stored energy — the surge drum
should look like it belongs to the same family as the accumulators the player
must build alongside it.

---

# 5. Building Orientation

## Required Directions

* [x] North
* [ ] East
* [ ] South
* [ ] West

**Direction count:**
`1`

`lightning-attractor` has no direction. The entity cannot be rotated, the
prototype has one `picture` slot, and the game will draw that single image
whichever way the player faces when they place it. There is no four-frame
consistency problem to solve here — **do not generate east, south and west
frames**, and do not accept a generator's offer of a turntable.

The consequence for the art is that the one frame has to carry everything: the
skirt, the drum and the tip all have to read from a single fixed view, and no
component may be hidden behind another on the assumption that another frame
will show it.

---

# 6. Sprite Assets Required

## 6.1 Main Building

| Asset         | Required | Frames | Directions |
| ------------- | -------: | -----: | ---------: |
| Main building |        ✓ |    `1` |        `1` |
| Shadow        |        ✓ |    `1` |        `1` |
| Idle state    |        ✓ |    `1` |        `1` |
| Working state |      `✓` |`19 + 24` |      `1` |

`lightning-attractor` exposes exactly three visual slots through
`chargable_graphics`: a static `picture`, a `charge_animation` played once when
a strike is caught (`charge_cooldown = 30`), and a `discharge_animation` played
once when the buffer is drawn down (`discharge_cooldown = 60`). Frame counts
match vanilla's — 19 and 24 — so the inherited cooldowns stay correct.

**There is no charge-level visual, and there cannot be one.** The engine gives
no way to vary the sprite with buffer contents on this prototype. A mast
holding 4000 MJ looks identical to an empty one, which is why §3.3 forbids a
resting glow: the only honest states are *just hit* and *being drained*.

---

## 6.2 Animation Layers

| Layer          | Required | Animated | Frames |
| -------------- | -------: | -------: | -----: |
| Main structure |        ✓ |       No |      1 |
| Machinery      |      `—` |      `—` |    `—` |
| Pistons        |      `—` |      `—` |    `—` |
| Belts          |      `—` |      `—` |    `—` |
| Fans           |      `—` |      `—` |    `—` |
| Lights         |      `—` |      `—` |    `—` |
| Glow           |      `✓` |      `✓` | `19 + 24` |
| Steam          |      `—` |      `—` |    `—` |

**Animation FPS:**
Vanilla's `animation_speed` on both sequences, unchanged. The charge burst runs
inside its 30-tick cooldown and the discharge inside its 60.

**Animation Loop:**
`No` — both are one-shot, triggered by the engine. `charge_animation_is_looped
= false`.

**Nothing on this building moves mechanically.** No fans, no pistons, no
rotation, no vents. Every animated pixel is additive light drawn as glow. If
the art shows a moving part, the mechanic has been misread — the mast is a lump
of earthed metal and the only thing that happens to it is electricity.

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
Cast down-right, matching every vanilla building, drawn as a separate
`draw_as_shadow` sheet. The Core has `day-night-cycle = 0` and a sky that never
moves, so this shadow is fixed forever. A 7-tile tower throws a long one: it
should fall well outside the collision box and taper, and it must **not** be
baked into the colour layer.

**Base:**
Grounding skirt, bolt rings, earthing straps and the scorch fan around them.

**Main Structure:**
The braced column, the buss bar, the insulator stack and the tip collar.

**Static Machinery:**
The surge drum, its end caps, its cable run into the skirt, and the green lamp.

**Pipes:**
None. Nothing fluid touches this building.

**Working Machinery:**
None — see §6.2. The slot stays empty deliberately.

**Lighting:**
None. The green lamp is painted into the static layer, not drawn as a light.

**Glow:**
Two additive one-shot sheets. *Charge*: filaments crawling down from the tip
along the buss bar into the drum, 19 frames, bright at frame 1 and gone by 19.
*Discharge*: a lower, duller pulse travelling up out of the drum and dispersing
at the insulators, 24 frames, never as bright as charge.

**Effects:**
A faint corona haze at the tip immediately after a strike, and dust lifted off
the skirt. **No smoke, no flame, no steam** — pressure 5, nothing burns.

---

# 8. Input / Output Visualisation

## Item Inputs

| Input | Location | Direction |
| ----- | -------- | --------- |
| None  | —        | —         |

## Item Outputs

| Output | Location | Direction |
| ------ | -------- | --------- |
| None   | —        | —         |

No inserter ever touches this building.

## Fluid Inputs / Outputs

None, either way.

## Energy

| Flow | Location | Connection Type |
| ---- | -------- | --------------- |
| In — the strike | `[0, -4.8]` — the tip | `lightning_strike_offset` |
| Out — 40 MW | anywhere in a pole's supply area | electric network |

### Visual Requirement

**`lightning_strike_offset = {0, -4.8}` is the hardest constraint in this
document.** The engine draws every arc terminating at a point 4.8 tiles above
the entity's origin, regardless of what the sprite looks like. If the painted
tip does not sit at that height, arcs will visibly strike empty air above the
mast or bury themselves in its column — and this happens once every ninety
seconds per chunk, in front of the player, lit up. §13 turns 4.8 tiles into a
pixel row on the canvas; the tip goes there.

The output is invisible by definition, so the art has to imply it instead: the
cable run from the drum into the skirt, and the drum's own bulk, are what tell
the player this building is part of the grid rather than a rod.

---

# 9. Working Animation

## Animation Concept

Two separate one-shot events, ninety seconds apart, with nothing in between.
The building is inert almost all of the time and that is correct — the drama is
the strike, and anything idling continuously would compete with it.

### Sequence — charge (19 frames, one shot)

1. Inert: no glow anywhere, tip cold, drum dark.
2. Frame 1: the whole tip flares violet-white as the arc lands.
3. Filaments race **down** the buss bar and the outer bracing, forking once.
4. The insulator ribs light from the top down as the charge passes them.
5. The drum seams brighten as the charge arrives and settles.
6. Everything falls away to nothing by frame 19; the tip is last to fade.

### Sequence — discharge (24 frames, one shot)

1. Inert.
2. A dull violet pulse rises out of the drum seams.
3. It travels **up** the buss bar — the opposite direction to charge, and about
   half the brightness.
4. It disperses at the insulator stack without ever reaching the tip.
5. Fades to nothing by frame 24.

**Frame Count:** `19` (charge) · `24` (discharge)

**Loop Duration:** n/a — both are one-shot, engine-triggered.

Direction is the whole reading: **down is energy arriving, up is energy
leaving.** A player watching a mast should be able to tell which is happening
without looking at the power graph.

---

# 10. Effects

## Working Effects

* [x] Glow
* [ ] Steam
* [ ] Smoke
* [ ] Sparks
* [ ] Flames
* [x] Electrical arcs
* [ ] Moving fluids
* [x] Other: `corona haze at the tip, dust lifted off the skirt`

### Effect Description

For roughly half a second after a strike: a faint violet corona clinging to the
tip and the top insulator, and a low ring of dust lifting off the skirt and
settling. Nothing else, ever.

**No flame, no smoke, no exhaust.** Pressure 5 is the Core's defining number
and it means nothing on the planet burns — the same rule that refuses boilers
and furnaces here. **No sparks** either: showers of orange sparks read as
grinding metal or combustion, and this is a clean high-voltage event.

---

# 11. DALL·E Generation Requirements

Generate at the largest size the tool supports. **Portrait, not square, for
everything except the icon** — this building is twice as tall as it is wide and
a square canvas wastes half its resolution on empty sky. `--size 1024x1536` for
the master, structure, glow and effects plates; `--size 1024x1024` for the
icon. Transparent background where supported, otherwise flat magenta `#FF00FF`
for keying — the colour appears nowhere on the building.

## Master Concept Prompt

```text
A Factorio Space Age industrial building sprite: a heavy grounded lightning
terminal, standing alone, drawn as a game asset with no perspective vanishing
point.

Camera: the base of the machine is seen from a steep angle above, so the upper
faces of its base plates and the top of its drum are clearly visible, while the
tower above the base leans toward the viewer so its sides show rather than its
top — the way tall structures are drawn in a top-down game. Not a side-on
elevation.

Structure, bottom to top. A wide splayed grounding skirt of bolted armour
plate, anchored flat, with four braided copper earthing straps at its corners
driven into bare metallic ground and faint dark scorch fanning out across the
ground where they enter. Rising from it, a short thick braced lattice column
with nearly parallel sides and only a slight taper, cross-braced twice, with an
armoured copper buss bar up its centre. Hugging the skirt at one side only, an
armoured ribbed horizontal cylinder with cast end caps, one small green lamp,
and a cable run into the skirt. Two thirds of the way up the column, a stack of
four ribbed pale ceramic insulator discs. Above them, clamped in a bolted
collar, a blunt sacrificial electrode stub: short, thick and slab-sided,
roughly as wide as it is tall, with a flat cratered chewed-off top like a
worn anvil or a burnt-out welding electrode, its upper part discoloured to
straw yellow and blue-grey from repeated burning.

Proportion: the whole object is twice as tall as it is wide. The base is
massive, the blunt tip occupies only the top eighth of the height, and the
machine is deliberately bottom-heavy — over-built, squatting under high
gravity.

Materials: dark iron-nickel grey-brown machined metal, #4A463F to #6E685C, kept
dark and warm rather than pale — much less orange rust than a weathered-steel
default, with pale nickel-white #B9B4A8 confined to the bolt rings and drum end
caps, and pale sand #C9C0AC ceramic. Metal dust, scuffing and old scorch marks.

State: cold and unlit. No glow, no light, no electricity visible anywhere,
including the lamp.

It must read as earthed electrical infrastructure, not as a rocket, a missile
or an antenna: nothing tapers to a point, no nose cone, no dish, no tuning
fork, no twin prongs, no barrel, no muzzle, nothing aimed, no launch stand, no
rotating parts, no fire, no smoke, no exhaust, no snow.

Painted semi-realistic industrial game art, strong readable silhouette, three
and a half tiles wide and seven tiles tall, fully transparent background, no
text, no logos, no characters, no UI, no ground texture, no background scenery,
no baked drop shadow.
```

---

## Directional Prompts

### North

```text
Not required — the entity has no direction. See §5.
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
[Master prompt] This is the static base layer: the complete building, cold and
inert, with absolutely nothing lit. No violet, no white filaments, no corona,
no glow in the ceramic, no light in the green lamp. Every surface reads by
shape and material alone. Nothing in frame but the machine.
```

### Working Machinery

```text
Not required — this building has no moving parts. See §6.2.
```

### Glow / Lighting

```text
Two separate additive glow plates on a fully transparent background, for
additive blending over the static structure, with no machine and no metal drawn
— only the light itself, positioned as it would fall on a tall narrow tower
about three and a half tiles wide and seven tall.

Plate one, charge: violet-white #C9B6FF filaments brightening to pure white at
their cores, flaring at the blunt tip near the top of the frame and forking
downward along a central vertical buss line and its outer bracing, brightest at
the top, reaching a ribbed horizontal drum shape at the bottom left.

Plate two, discharge: a duller, lower violet #A48CE0 pulse rising out of that
same drum shape at the bottom left and travelling a short way up the central
line, dispersing before it reaches the ceramic stack, never touching the tip,
at roughly half the brightness of plate one.

No sparks, no orange, no lens flare, no starburst, no text.
```

### Effects

```text
A faint high-voltage corona on a fully transparent background, with nothing
else in frame: a thin violet-white haze clinging to the shape of a blunt
pitted spike and the ribbed disc immediately below it, plus a few short
crawling filaments no longer than the spike itself, and a low thin ring of pale
grey dust lifting and settling near the bottom of the frame. Thin and sparse in
near-vacuum. No smoke, no fire, no steam, no sparks, no particles leaving the
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
* [ ] Generate directional sprites — **skip, one direction**
* [ ] Generate animation frames
* [ ] Generate spritesheets
* [ ] Optimise PNGs

**The tall sprite makes the crop different from the vent pump's.** The horizontal
crop is centred on the column, but the *vertical* crop is fixed by §8: the tip
lands on a specific pixel row and everything else follows from it. Crop the top
first, to that row, and let the bottom fall where it falls.

Generators attach a ground plane and a baked shadow to anything that looks like
it stands on the floor, and both have to come off before the crop. The baked
shadow is not reusable — Factorio wants it as a separate `draw_as_shadow`
sheet, and one left in the colour layer doubles against the engine's own.

The two glow plates arrive as stills and are **animated by us**, not by the
generator: 19 charge frames and 24 discharge frames are derived from the plates
by masking along the buss line, which is why §11 asks for the light shaped to
the tower rather than for a sequence.

---

# 13. Sprite Dimensions

**Tile Size:**
`32` px in-game. Source art is drawn at `scale = 0.5`, so **64 source pixels
per tile**.

**Building Width:**
`3.5` tiles → `112` in-game px → `224` source px

**Building Height:**
`7.0` tiles → `224` in-game px → `448` source px

**Sprite Width:**
`224` px (source)

**Sprite Height:**
`448` px (source)

**Shift:**
`util.by_pixel(0, -68)` — in-game pixels, applied to the sprite centre.

**Where the tip goes.** With that shift, the canvas spans −180 to +44 in-game
px around the origin. The strike point is `-4.8` tiles = `-153.6` in-game px,
which is **26.4 in-game px — 53 source px — below the top edge of the canvas**.
The centre of the tungsten tip must land on that row, ±4 source px. The
headroom above it is not waste: it is where the corona and the top of the
charge flare live.

**Spritesheet Width:**
`1536` px — charge and discharge alike, 8 frames per row at 192 px

**Spritesheet Height:**
`1440` px — 3 rows of 480 px

**Frame Count:**
`1` (picture) · `1` (shadow) · `19` (charge) · `24` (discharge)

**Line Length:**
`8` for both animations. 19 frames fill 8+8+3; 24 fill 8+8+8.

The glow frames are 192×480 rather than 224×448: narrower, because light only
happens on the column, and taller, because the corona extends past the tip.

---

# 14. File Structure

```text
graphics/
└── entity/
    └── arc-mast/
        ├── concept/                  generated concepts, not shipped
        │   ├── v1-master.png
        │   ├── v1-layer-structure.png
        │   ├── v1-layer-glow.png
        │   ├── v1-layer-effects.png
        │   └── v1-icon.png
        ├── arc-mast.png              224×448, the static picture
        ├── arc-mast-shadow.png       224×448, draw_as_shadow
        ├── arc-mast-charge.png       1536×1440, 19 frames
        └── arc-mast-discharge.png    1536×1440, 24 frames
```

No directional files. No working-machinery file. The icon lives with the other
icons, not here.

---

# 15. Factorio Prototype

**Prototype Type:**
`lightning-attractor`

**Prototype Name:**
`sae-arc-mast`

### Graphics

Replaces the inherited `chargable_graphics` in `prototypes/core/storms.lua`.

```lua
mast.chargable_graphics =
{
  picture =
  {
    layers =
    {
      {
        filename = "__space-age-extended__/graphics/entity/arc-mast/arc-mast.png",
        priority = "high",
        width = 224,
        height = 448,
        shift = util.by_pixel(0, -68),
        scale = 0.5
      },
      {
        filename = "__space-age-extended__/graphics/entity/arc-mast/arc-mast-shadow.png",
        priority = "high",
        draw_as_shadow = true,
        width = 224,
        height = 448,
        shift = util.by_pixel(0, -68),
        scale = 0.5
      }
    }
  },
  charge_animation =
  {
    layers =
    {
      {
        filename = "__space-age-extended__/graphics/entity/arc-mast/arc-mast-charge.png",
        priority = "high",
        blend_mode = "additive",
        draw_as_glow = true,
        width = 192,
        height = 480,
        frame_count = 19,
        line_length = 8,
        shift = util.by_pixel(0, -76),
        scale = 0.5
      }
    }
  },
  charge_animation_is_looped = false,
  charge_cooldown = 30,
  discharge_animation =
  {
    layers =
    {
      {
        filename = "__space-age-extended__/graphics/entity/arc-mast/arc-mast-discharge.png",
        priority = "high",
        blend_mode = "additive",
        draw_as_glow = true,
        width = 192,
        height = 480,
        frame_count = 24,
        line_length = 8,
        shift = util.by_pixel(0, -76),
        scale = 0.5
      }
    }
  },
  discharge_cooldown = 60
}
```

### Other Visual Properties

```text
Animation:
Two one-shot sequences only; no idle animation exists on this prototype.

Shadow:
Separate draw_as_shadow layer inside picture. Down-right, long, tapering.

Working Visualisation:
Not applicable to lightning-attractor. Charge and discharge are the whole of it.

Lights:
None. drawing_box_vertical_extension = 4.5 and lightning_strike_offset =
{0, -4.8} are both inherited and must not change -- the art is fitted to them,
not the other way round.

Fluid Boxes:
None.

Circuit Connections:
None. Not a pole; must stand inside a pole's supply area to deliver power.

Remnants:
Still lightning-collector-remnants, inherited. Out of scope here, and wrong
once this art lands -- a follow-up.
```

---

# 16. Icon

**Icon Required:** ✓

**Icon Size:**
`64×64`

**Icon Concept:**
The bottom-heavy silhouette, compressed. A wide dark skirt, a short braced
column, the pale ceramic stack, and the pitted tip — with one violet filament
on the tip so the icon reads as *lightning* rather than as *pylon* at 32 px.
The surge drum is dropped: at icon size it muddies the base into a blob.
Vertical composition inside a square frame, filling the height.

### Icon Prompt

```text
Factorio "Space Age" item icon. A small rendered industrial object on a
workbench: a heavy grounded lightning terminal, bottom-heavy, with a wide
bolted dark metal base skirt, a short three-sided braced column, a stack of
four pale sand-coloured ceramic insulator discs, and a blunt pitted tungsten
spike on top whose upper third is discoloured straw and blue-grey. One short
violet-white electrical filament crawls across the spike. Dark iron-nickel
grey-brown metal, #4A463F to #6E685C, with pale nickel-white bolt rings.

Semi-realistic sci-fi industrial painting, not flat, not cartoon, not
photo-real. Three-quarter view, slightly above, soft single-direction lighting
from the upper left, visible specular highlight, subtle ambient occlusion,
gentle drop shadow behind the object. Vertical object filling roughly 85% of
the frame height, centred, even padding. Bold simple silhouette that still
reads at very small size. Fully transparent background, square canvas, no
ground or platform under the object, no text, no logos, no watermark, no
border, no scene or background elements.
```

The icon should remain recognisable at Factorio's normal inventory/UI scale.

---

# 17. Visual QA Checklist

### Building

* [ ] Correct tile size — 2×2 footprint under a 3.5×7 sprite
* [ ] Correct perspective — base from above, tower leaning toward the camera
* [ ] Correct scale
* [ ] Clear silhouette
* [ ] Looks like Factorio
* [ ] Matches intended planet — bare metal, no vegetation, no snow, no rust-red
* [ ] Inputs are visually understandable — the tip is obviously where it is hit
* [ ] Outputs are visually understandable — the drum and its cable read as grid

### Generated-art defects

* [ ] Does not read as a rocket, a missile or anything on a launch stand
* [ ] No baked drop shadow in the colour layer
* [ ] No ground plane or scenery
* [ ] Background is transparent or cleanly keyable
* [ ] Palette is dark and warm, not pale and rust-orange
* [ ] Nothing glows — the static picture is entirely unlit

### Directions

* [x] North
* [x] East — n/a, no direction
* [x] South — n/a
* [x] West — n/a
* [x] All directions represent the same building — trivially

### Animation

* [ ] Charge reads as energy arriving, travelling **down**
* [ ] Discharge reads as energy leaving, travelling **up**, and is dimmer
* [ ] Neither sequence loops
* [ ] Static components remain static
* [ ] Glow aligns with the buss bar and the tip in the static layer

### In-Game

* [ ] **Arcs terminate on the painted tip, not above or inside it**
* [ ] Shadow aligns with the building and does not double
* [ ] Building doesn't overlap neighbouring entities incorrectly
* [ ] Building is recognisable in a row of masts
* [ ] Not confusable with a substation or an accumulator at a glance
* [ ] Performance is acceptable

---

# 18. Final Asset Checklist

```text
[ ] Master concept
[x] North sprite      -- single direction; the master is the sprite
[x] East sprite       -- n/a
[x] South sprite      -- n/a
[x] West sprite       -- n/a

[ ] Shadow
[ ] Static picture
[ ] Charge animation      (19 frames)
[ ] Discharge animation   (24 frames)
[x] Working machinery layer -- n/a, no moving parts
[x] Lighting layer          -- n/a, painted lamp only
[ ] Effects layer

[ ] Icon
[ ] Spritesheets
[ ] Factorio prototype
[ ] In-game test
```

---

# 19. Design Notes / Iteration History

Generated in the browser against ChatGPT's image tool, portrait 2:3, master
concept prompt only. Both rounds are the same conversation, so round 2 had
round 1 in context.

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| 1 | master | Splayed skirt, braided corner straps, braced lattice with copper buss bar, ceramic disc stack, ribbed drum with green lamp — every named component present. But the column tapered hard into a **conical nose cone**: a V-2 on a launch stand. | **Reject** | Keep-list, then six numbered fixes: blunt slab-sided electrode stub instead of the cone; near-parallel column sides; 1:2 proportion with the stack two-thirds up and the tip in the top eighth; base seen from above, not side-on; darker warmer palette with less rust; transparent background, no baked shadow. |
| 2 | master | Nose cone gone — the top is now a blunt cratered stub, and the silhouette no longer reads as a rocket. Taper reduced. Skirt, straps, buss bar, ceramic stack, drum and lamp all carried over intact. **Background is genuinely transparent** (1024×1536 RGBA). | **Reject, but close** — the silhouette is approved in principle | Still outstanding: the palette is pale, silvery and bleached where it should be dark warm iron; the base is drawn too close to side-on; the column still tapers more than asked. |
| 3 | master | `[pending]` | — | Palette pushed hard toward dark warm cast iron, the column taper given a numeric floor (top width ≥ ¾ of bottom width), and the camera restated as a visible consequence. |

Concepts are in `graphics/entity/arc-mast/concept/`: `v1-master.png`
(966×1628) and `v2-master.png` (1024×1536), both RGBA with a genuinely
transparent background. Signed image URLs cannot be read out of the page, so
they were downloaded through the browser's own control rather than fetched.

### Version 1

The generator draws what it is *shown*, not what it is *told not to be*. Round
1 named every component correctly and still produced a rocket, because a
tapering tower with something on top **is** a rocket unless the anti-read is
stated as a read: "must not look like a missile" works where "no nose cone"
does not. The master prompt in §11 was rewritten to lead with the anti-read and
to state proportion as a ratio.

### Version 2

Three defects survived the refinement and are the ones to attack next, in this
order:

1. **Camera.** Two rounds have produced a side-on elevation. The fix is to
   demand a specific visible consequence rather than an angle — *the top faces
   of the skirt plates and the top of the drum must be visible* — which is now
   in the master prompt.
2. **Palette.** "Dark iron-nickel grey-brown" with hexes is not winning against
   the model's weathered-steel default. The prompt now says what to *reduce*,
   not only what to use.
3. **Ground marks.** Transparency was honoured — the plate is RGBA and the
   background is empty, so no keying is needed. What is left is ambiguous: the
   dark marks under the skirt feet read as much like a baked drop shadow as
   like the scorch that was asked for. They have to be separated in processing
   (§12), because Factorio draws its own shadow and a doubled one is obvious.

### Final

`[Not reached — the master concept has not passed its gate.]`
