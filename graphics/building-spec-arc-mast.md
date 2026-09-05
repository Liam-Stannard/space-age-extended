# Factorio Building — Art & Implementation Specification

**Arc Mast.** Filled from `building-spec-template.md` (v2), section for section.
Every gameplay number is the implemented value read off
`prototypes/core/storms.lua`, `prototypes/core/planet.lua` and the vanilla
prototypes they deep-copy. The art sections are proposals.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on |
| - | ----- | ------ | --------------------- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **passed — round 9 master sheet is the locked design** |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3.1 and §17 | **passed — `concept/v10-canonical.png`** |
| 2 | Idle plate (unlit) | portrait 2:3 | Same machine as stage 1, nothing lit | **passed — `concept/v11-idle.png`, lamp measured dark** |
| 3 | Directional frames | — | n/a — one direction, see §5 | n/a |
| 4 | Glow plates | portrait 2:3 | Aligns with stage 2 geometry | **passed — derived by differencing, so registration is exact** |
| 5 | Effects plate | portrait 2:3 | Reads at one tile | **deferred** — corona and dust are better as engine effects; not needed for the first in-game test |
| 6 | Icon | square | Legible at 32 px | **passed — derived from the approved plate, `graphics/icons/arc-mast.png`** |

Stage 1 was run before stage 0 existed in the template. The concept sheet is
still worth generating: it is the cheapest way to check the icon, the tile-grid
read and the layer split against a silhouette that is nearly settled.

### Where generation happens

Browser — ChatGPT's image tool, signed in. `tools/generate-building-art.py`
reads the same §11 blocks and remains the fallback, but its OpenAI account has
no credits. See template Appendix B.

### Round log

Three rounds so far, all stage 1. Recorded in §19.

---

# 1. Building Overview

**Building Name:**
`Arc Mast`

**Internal Prototype Name:**
`sae-arc-mast`

**Building Type:**
`lightning-attractor`, deep-copied from `lightning-collector`. The type is
load-bearing twice: it is the only type the planet's
`lightning_properties.priority_rules` can name, and the only one that turns a
strike into an `electric` energy source. `sae-arc-mast` carries a
`priority_bonus` of 10000 on the Core, so a mast outbids every other structure
for the strike — which is the whole safety mechanic.

**Planet / Environment:**
`The Core.` No `surface_conditions`; it is gated by there being nothing to
catch anywhere else. Arc storms exist only where `lightning_properties` is
declared, and the Core is the only surface that declares them. A mast on Nauvis
would build, sit at zero, and drain 100 kW forever.

**Purpose:**
Catches an arc strike and banks it as electricity. The hazard and the power
supply are one event: 600 damage and 4000 MJ per chunk every ninety seconds, of
which the mast keeps 35% — 1400 MJ — into a 4000 MJ buffer. Sited for cover
first and power second.

**Technology Unlock:**
`Arc Masts` (`sae-arc-masts`), tier 0, prerequisite `sae-core-survey`.
Researched on 200 units of the seven vanilla packs at 60 s, since no geodynamic
pack can exist before the surface has power.

**Recipe:**
30 kamacite plate · 5 welded plate · 10 processing unit · 5 accumulator, 10 s.
`stack_size = 10`, `weight = 40000` — 25 to a rocket.

---

# 2. Gameplay Dimensions

**Tile Size:**
`3×3` selection over a `2.8×2.8` collision. Most of this building is still
drawn above its footprint — the sprite is `3.5 × 5.4` tiles — but the *base
plate* is 3.14 tiles across, and it has to fit between neighbours. See §13.

**Collision Box:**
`[-1.4, -1.4] → [1.4, 1.4]`

**Selection Box:**
`[-1.5, -1.5] → [1.5, 1.5]`

**Why not the collector's 2×2, which this prototype deep-copies.** Because the
art does not fit it. Vanilla's collector is 144 source px at its widest — 2.25
tiles on a 2 tile pitch, a quarter tile of sloped leg overhanging, which reads
fine. Ours is 201 px, 3.14 tiles, and in the first in-game test a row of masts
overlapped by more than a whole tile: each base plate visibly ate its
neighbour's. The mast is meant to be a bigger machine than Fulgora's collector,
so the box grew to meet the art rather than the art shrinking to meet the box.
At a 3 tile pitch the plates just touch. Measured in-engine: the mast reports
`tile_width 3`, three masts place at a 3 tile pitch, and a second mast 2 tiles
from the first is refused.

**Placement Restrictions:**
None — no surface conditions, no resource requirement, no terrain restriction.
`fast_replaceable_group` and `next_upgrade` are both cleared, so it never
fast-replaces a lightning collector and offers no upgrade path.

**Rotation:**
`None.` `lightning-attractor` has no direction: the entity cannot be rotated and
the prototype has no per-direction sprite slot. Nothing moves between
directions because there are none.

**Crafting Speed:**
n/a for this entity type. The equivalent rates are `efficiency = 0.35` (vanilla
0.4) and `range_elongation = 20` (vanilla 25).

**Energy Consumption:**
Working: none — it is a source, not a load. Standby drain `100 kW` (vanilla
2.5 MJ). Output flow limit 40 MW, buffer 4000 MJ.

**Energy Type:**
`electric`, `usage_priority = "primary-output"`. Not a pole: it must stand
inside some pole's supply area to deliver anything.

**Health and resistances:**
`max_health = 200`; fire 90%, electric 100% (both inherited). It is immune to
the thing that hits it, which is the point.

---

# 3. Visual Design

## 3.1 Design Concept

**The wrong machine it must not be:**
It currently wears **Fulgora's lightning collector** unmodified — a slender
tuning-fork antenna, light and delicate, built to sip a strike arriving every
ten seconds. The Arc Mast stands under a strike nine times rarer and six times
heavier, at gravity 50, and its job is to take the hit so nothing else does and
then hold 4000 MJ. Nothing about the collector's proportions, slenderness or
pale enamel survives that brief. Second anti-read, learned the hard way in
generation: a tapering tower with something on top reads as a **rocket on a
launch stand**, and must not.

**Primary Visual Theme:**
Grounded sacrificial anvil. Heavy electrical infrastructure: mass low, tip
burnt, everything bolted to the crust.

**Overall Appearance:**
Bottom to top — a wide splayed grounding skirt bolted flat into bare metal with
four braided earthing straps at its corners; a short, thick, braced lattice
column with nearly parallel sides and an armoured copper buss bar up its
centre; an armoured ribbed horizontal surge drum hugging the skirt on one side
only, cabled in, carrying one small green lamp; two thirds of the way up, a
stack of four ribbed pale ceramic insulator discs; above them, in a bolted
collar, a blunt sacrificial electrode stub.

**Silhouette:**
A broad triangular base narrowing into a short braced column, ending in a blunt
notched stub — not a fork, not a dish, not a cone. From altitude the read is
*"something earthed, and something stored."* The drum breaks the outline at one
side so the shape is asymmetric. It must never be confused with a substation,
an accumulator, or anything aimed.

**Visual Complexity:**
`Medium` — detail concentrated in the base and the drum; the column stays plain
so the tip reads cleanly against the sky when a strike lands on it.

**Visual Age:**
`Advanced.` Machined, purposeful, unglamorous. Proven kit that has already been
hit a hundred times.

---

## 3.2 Key Visual Features

The building should contain:

* A **splayed grounding skirt** — wide, low, bolted anchor plate with four
  radial braided earthing straps driven into the crust, and faint dark scorch
  fanning out across the ground where they enter.
* A **short braced column** — heavy lattice, cross-braced twice, sides nearly
  parallel (top width at least three quarters of bottom width), with an
  armoured copper buss bar up its centre.
* A **ceramic insulator stack** — four ribbed pale ceramic discs, the one
  obviously non-metal element on the building.
* A **sacrificial tip** — a blunt, slab-sided electrode stub roughly as wide as
  it is tall, flat and cratered on top, discoloured straw and blue-grey from
  repeated ablation, in a bolted collar that reads as replaceable.
* An **armoured surge drum** — ribbed horizontal cylinder with cast end caps,
  one small green lamp, cabled into the skirt, and visibly the heaviest single
  component.

### Signature Feature

**The tip is damaged and the base is enormous.** Every other lightning
structure in the game gets thinner and more elegant as it rises; this one gets
smaller and *worse*. A burnt stub over a massive earthed drum is the mechanic in
one silhouette — you stood in the way, you got paid for it, and the thing that
pays you is also eating the building.

---

## 3.3 Colour Palette

**Primary:**
Dark iron-nickel grey-brown machined casing, `#4A463F` → `#6E685C`. Warm and
low-value, closer to old dark cast iron than to steel. Matches
`building-spec-vent-pump.md` so the Core's buildings read as one set.

**Secondary:**
Pale nickel-white `#B9B4A8`, confined to the skirt bolt rings and the drum end
caps.

**Metal:**
Warm dark steel, desaturated, so the arc colour is the only saturated thing on
the building. Explicitly **not** pale galvanised or bleached weathered steel —
that is the generator's default and it has to be argued down every round.

**Accent:**
Ceramic pale vitreous sand `#C9C0AC`, the lightest value on the building.
Copper `#8A5A32` confined to the buss bar and the earthing straps. Tip ablation
discolouration straw `#C2A05B` through blue-grey `#7C8794`, on the upper part of
the stub only — this is temper colour, not heat glow, and must not be lit.

**Working Glow:**
Violet-white `#C9B6FF` ramping to `#FFFFFF`, at the tip, the top two insulator
ribs and the buss bar seam, during charge and discharge only. **Nothing glows at
rest.** Not a free choice: `sae-arc` is vanilla's `lightning` with only damage
and energy changed, so the strike arrives in vanilla's colours and the mast's
glow has to sit alongside them.

**Warning / Status Lights:**
One small steady green lamp on the surge drum — decorative, because the
prototype offers no hook for a state-driven indicator. A lamp that never
changes is honest only if it never claims to mean anything. No red, no amber,
no blinking.

---

# 4. Factorio Visual Style

### Required characteristics

* [x] Factorio top-down perspective
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

**Name the angle.** Every prompt in §11 says *"the game's characteristic
45-degree top-down perspective"*, early and in those words. Rounds 1–3 avoided
the phrase and described the geometry instead, and all three came back as flat
side-on elevations; the phrase is what the model associates with Factorio's
camera. Because this is a **tall** building, one clause is added after it — base
seen from above with the upper faces of the skirt plates and the top of the drum
visible, column and tip leaning toward the viewer — rather than in place of it.

### Style Reference Buildings

1. `Lightning collector` (Space Age)
2. `Substation` (base)
3. `Accumulator` (base)

**Reason for references:**
Take from the **lightning collector** only its envelope — the height, the
drawing box, and the trick of leaning a tall object toward the camera. Take
**nothing** of its design: the tuning-fork head, the slenderness and the pale
enamel belong to Fulgora and are exactly what makes the placeholder wrong here.
Take from the **substation** the ceramic insulator stacks, the bolted armoured
base and the sense of a live node in a grid. Take from the **accumulator** the
squat, ribbed, heavy read of stored energy — the surge drum should look like it
belongs to the same family as the accumulators the player must build alongside
it.

---

# 5. Building Orientation

## Required Directions

* [x] North
* [ ] East
* [ ] South
* [ ] West

**Direction count:**
`1`

**What actually differs between directions:**
Nothing — there are none. `lightning-attractor` has one `picture` slot and the
game draws it whichever way the player faces when placing. Do not generate
east, south and west frames, and do not accept a generator's offer of a
turntable.

The consequence for the art is that one frame carries everything: skirt, drum
and tip must all read from a single fixed view, and no component may be hidden
behind another on the assumption that another frame will show it.

---

# 6. Sprite Assets Required

## 6.1 Main Building

| Asset         | Required | Frames | Directions |
| ------------- | -------: | -----: | ---------: |
| Main building |        ✓ |    `1` |        `1` |
| Shadow        |        ✓ |    `1` |        `1` |
| Idle state    |        ✓ |    `1` |        `1` |
| Working state |      `✓` | `19 + 24` |     `1` |

**Engine limits worth stating here:**
`lightning-attractor` exposes exactly three visual slots through
`chargable_graphics`: a static `picture`, a `charge_animation` played once when
a strike is caught (`charge_cooldown = 30`), and a `discharge_animation` played
once when the buffer is drawn down (`discharge_cooldown = 60`). **There is no
charge-level visual and there cannot be one** — a mast holding 4000 MJ looks
identical to an empty one. That is why §3.3 forbids a resting glow: the only
honest states are *just hit* and *being drained*.

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
Vanilla's `animation_speed` on both sequences, unchanged — the charge burst runs
inside its 30-tick cooldown, the discharge inside its 60.

**Animation Loop:**
`No` — both are one-shot, engine-triggered. `charge_animation_is_looped = false`.

**What must NOT move:**
Everything. No fans, no pistons, no rotation, no vents, no reciprocating parts.
Every animated pixel is additive light drawn as glow. The mast is a lump of
earthed metal and the only thing that happens to it is electricity; art showing
a moving part has misread the machine.

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

**Shadow:**
Cast down-right, drawn as a separate `draw_as_shadow` sheet. The Core has
`day-night-cycle = 0` and a sky that never moves, so this shadow is fixed
forever. A 7-tile tower throws a long one: it should fall well outside the
collision box and taper, and must never be baked into the colour layer.

**Base:**
Grounding skirt, bolt rings, earthing straps and the scorch fan around them.

**Main Structure:**
The braced column, the buss bar, the insulator stack and the tip collar.

**Static Machinery:**
The surge drum, its end caps, its cable run into the skirt, and the green lamp.

**Pipes:**
None — nothing fluid touches this building.

**Working Machinery:**
None — see §6.2. The slot stays empty deliberately.

**Lighting:**
None — the green lamp is painted into the static layer, not drawn as a light.

**Glow:**
Two additive one-shot sheets, never merged. *Charge*: filaments crawling down
from the tip along the buss bar into the drum, 19 frames, bright at frame 1 and
gone by 19. *Discharge*: a lower, duller pulse travelling up out of the drum and
dispersing at the insulators, 24 frames, never as bright as charge.

**Effects:**
A faint corona haze at the tip immediately after a strike, and dust lifted off
the skirt. No smoke, no flame, no steam — pressure 5, nothing burns.

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

| Fluid | Location | Connection Type |
| ----- | -------- | --------------- |
| None  | —        | —               |

## Energy

| Flow | Location | Connection Type |
| ---- | -------- | --------------- |
| In — the strike | `[0, -4.14375]` — the electrode | `lightning_strike_offset` |
| Out — up to 40 MW | anywhere inside a pole's supply area | electric network |

### Hard geometric constraints

**`lightning_strike_offset = {0, -4.14375}`.** The engine draws every arc
terminating that many tiles above the entity origin regardless of what the
sprite looks like. If the painted tip is not at that height, arcs strike empty
air or bury themselves in the column — once every ninety seconds per chunk, in
front of the player, lit up. §13 converts this to a pixel row.

This is **no longer the inherited `-4.8`.** It moved with the plate: the shift
came down by 0.65625 tiles (see §13), so the strike row came down by exactly
the same amount. The two numbers are locked together and neither can be changed
alone.

`drawing_box_vertical_extension = 4.5` is inherited and must not change; the art
is fitted to it, not the other way round.

### Visual Requirement

The output is invisible by definition, so the art implies it: the cable run
from the drum into the skirt, and the drum's own bulk, are what tell the player
this is part of the grid rather than a rod. The input needs no signposting — the
engine draws a lightning bolt onto it.

---

# 9. Working Animation

## Animation Concept

Two separate one-shot events, ninety seconds apart, with nothing in between.
The building is inert almost all the time and that is correct — the drama is the
strike, and anything idling continuously would compete with it. **Not a cycle:**
direction is the whole reading, down is energy arriving and up is energy
leaving.

### Sequence

1. Inert — no glow anywhere, tip cold, drum dark.
2. Charge frame 1 — the whole tip flares violet-white as the arc lands.
3. Filaments race **down** the buss bar and the outer bracing, forking once;
   the insulator ribs light from the top down as the charge passes them.
4. The drum seams brighten as the charge arrives and settles.
5. Charge falls away to nothing by frame 19, the tip last to fade. Separately,
   on discharge, a dull violet pulse rises **up** out of the drum at half the
   brightness and disperses at the insulator stack without reaching the tip.
6. Return to inert. There is no completion event and no loop.

**Frame Count:** `19` (charge) · `24` (discharge)

**FPS:** vanilla `animation_speed`, unchanged

**Loop Duration:** n/a — one-shot, engine-triggered

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

### Prohibited effects, and why

**No flame, no smoke, no exhaust.** Pressure 5 is the Core's defining number and
it means nothing on the planet burns — the same rule that refuses boilers,
furnaces and heating towers here. One lick of flame contradicts the reason those
buildings are banned, and a player who sees it will reasonably conclude the mod
is inconsistent.

**No sparks.** Showers of orange sparks read as grinding metal or combustion.
This is a clean high-voltage event and the colour budget belongs to the arc.

**No steam.** Steam on the Core comes from the settling recipes in a different
building; putting a plume here blurs the split the surface economy turns on.

---

# 11. DALL·E Generation Requirements

**Canvas:** portrait 2:3 for the master and every layer plate — this building is
twice as tall as it is wide and a square canvas wastes half the resolution on
sky. Landscape 3:2 for the concept sheet, square for the icon. Generate at the
largest size available; we downscale. Transparent background is requested and,
measured over three rounds, is honoured.

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio Space
Age building, every panel drawn from the game's characteristic 45-degree
top-down perspective, laid out as labelled panels on a dark charcoal
background, in the style of a game art bible page.

Panels, left to right and top to bottom. A large hero view of the building. An
in-game icon panel showing the same building simplified to a 64x64 item icon. A
tile-grid panel showing it from directly overhead on a 2x2 tile grid. Three
close-up detail panels: the burnt electrode tip in its bolted collar, the
ceramic insulator stack, and the surge drum with its cable run. A layer
breakdown row showing the same building separated into shadow, base, structure,
static machinery, glow and effects. A row of animation key frames showing a
violet-white charge travelling down the tower from tip to drum. A small effects
panel showing a corona haze and a dust ring as separate plates. A palette strip
of eight colour swatches.

The building in every panel is the same machine: a heavy grounded lightning
terminal, bottom-heavy, with a wide splayed bolted grounding skirt with four
braided copper earthing straps, a short thick braced lattice column with nearly
parallel sides and a copper buss bar up its centre, an armoured ribbed
horizontal drum with cast end caps and one small green lamp at the base, a
stack of four ribbed pale ceramic insulator discs two thirds of the way up, and
a blunt cratered sacrificial electrode stub on top in a bolted collar. Dark
iron-nickel grey-brown metal, #4A463F to #6E685C, pale sand ceramic, violet
white #C9B6FF only in the animation and glow panels.

It must read as earthed electrical infrastructure, never as a rocket or a
missile: nothing tapers to a point, no nose cone, nothing aimed. Panel labels
and small caption text are wanted on this sheet. Painted semi-realistic
industrial game art. No characters, no photorealism.
```

---

## Master Concept Prompt

```text
Factorio Space Age industrial building sprite art, viewed from the game's
characteristic 45-degree top-down perspective: a heavy grounded lightning
terminal, standing alone, drawn as a game asset with no perspective vanishing
point.

Because the building is tall, it gets the treatment vanilla gives the lightning
collector and the big electric pole: the base is seen from above, so the upper
faces of its skirt plates and the top of its drum are clearly visible, while the
column and tip above it lean toward the viewer so their sides show. Not a
side-on elevation, and not isometric.

Structure, bottom to top. A wide splayed grounding skirt of bolted armour
plate, anchored flat, with four braided copper earthing straps at its corners
driven into bare metallic ground and faint dark scorch fanning out across the
ground where they enter. Rising from it, a short thick braced lattice column
with nearly parallel sides and only a slight taper — the width at the top of the
column must be at least three quarters of its width at the bottom, so it reads
as a column and not as a pylon or a derrick. Cross-braced twice, with an
armoured copper buss bar up its centre. Hugging the skirt at one side only, an
armoured ribbed horizontal cylinder with cast end caps, one small green lamp,
and a cable run into the skirt. Two thirds of the way up the column, a stack of
four ribbed pale ceramic insulator discs. Above them, clamped in a bolted
collar, a blunt sacrificial electrode stub: short, thick and slab-sided,
roughly as wide as it is tall, with a flat cratered chewed-off top like a worn
anvil or a burnt-out welding electrode, its upper part discoloured to straw
yellow and blue-grey from repeated burning.

Proportion: the whole object is twice as tall as it is wide. The base is
massive, the blunt tip occupies only the top eighth of the height, and the
machine is deliberately bottom-heavy — over-built, squatting under high gravity.

Materials: iron-nickel grey-brown machined metal in a mid-dark value, the body
of the metal reading around #554E45 and staying inside the range #4A463F to
#6E685C — do not go darker than #4A463F, and do not push it toward black or
toward heavy brown; it should read as machined iron in daylight, not as a
silhouette. Pale nickel-white #B9B4A8 confined to the bolt rings and drum end
caps only, pale sand #C9C0AC ceramic. Metal dust, scuffing and old scorch
marks, but restrained — no heavy orange rust.

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
else in frame: a thin violet-white haze clinging to the shape of a blunt pitted
stub and the ribbed disc immediately below it, plus a few short crawling
filaments no longer than the stub itself, and a low thin ring of pale grey dust
lifting and settling near the bottom of the frame. Thin and sparse in
near-vacuum. No smoke, no fire, no steam, no sparks, no particles leaving the
shape.
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
* [ ] Generate directional sprites — **skip, one direction**
* [ ] Generate animation frames
* [ ] Generate spritesheets
* [ ] Optimise PNGs

Measured over three rounds: transparency **is** honoured, so there is no
background to key and step one is free. What arrives uninvited is ground
contact — dark marks under the skirt feet that are half the scorch that was
asked for and half a baked drop shadow. Separate them before the crop; the
shadow half is not reusable, because Factorio wants a separate `draw_as_shadow`
sheet and one left in the colour layer doubles against the engine's own.

The vertical crop is fixed by §8, not by the artwork: crop the top to the tip
row first and let the bottom fall where it falls.

The two glow plates arrive as stills and are animated by us — 19 charge frames
and 24 discharge frames derived by masking along the buss line, which is why
§11 asks for light shaped to the tower rather than for a sequence.

---

# 13. Sprite Dimensions

**Measured off `concept/v10-canonical.png`**, not guessed. The approved plate
trims to 961×1480, an aspect of 1:1.54, and at 3.5 tiles wide that makes the
machine **3.5 × 5.4 tiles**, not the 3.5 × 7 this section previously claimed.
The 1:2 target was my own invention, extrapolated from a nominal footprint, and
three rounds were spent chasing it.

**And the art turns out to satisfy the engine pin on its own.** With the object
5.4 tiles tall and its tip on the `-4.8` strike row, its base sits 0.59 tiles
below the origin and the sprite centre lands at `by_pixel(0, -67)` — within a
pixel of the value guessed earlier, but now derived rather than asserted. The
proportion never needed forcing.

**Tile Size:** `32` px in-game · **Scale:** `0.5` → `64` source px per tile

**Building Width:** `3.5` tiles → `112` in-game px → `224` source px

**Building Height:** `5.45` tiles → `175` in-game px → `349` source px

**Sprite Width / Height:** `224 × 365` source px — the object is 224 × 349 with
16 source px of headroom above the tip, which is where the corona and the top
of the charge flare live.

**Shift:** `util.by_pixel(0, -60)`.

**This was `-81` and it was wrong.** `-81` was derived from the tip, and the tip
is the one landmark that cannot anchor a sprite: it fixed the top of the
building and let the bottom fall where it liked. In game the whole mast floated
two thirds of a tile above its own footprint, standing on nothing, with the
selection box drawn in bare ground beneath it.

**Anchor on the base plate instead**, which is the part that touches the tile.
Measured off `base.png`: the plate spans source rows 225–363, so its centre sits
55.8 in-game px below the canvas centre. Vanilla's collector puts its own plate
centre at `-0.133` tiles from the origin; matching that gives
`shift = -60 in-game px = -1.875 tiles`. The whole plate came down 0.65625 tiles.

**The strike row moves with it.** With the shift at `-60`, the electrode cage
spans `-4.43` to `-3.79` tiles from the origin, so the strike belongs at
`-4.14375` — vanilla's `-4.8` plus the same 0.65625 the plate moved. See §12.

**Spritesheet Width / Height:** `1792 × 1095` px, for charge and discharge alike

**Frame Count:** `1` picture · `1` shadow · `19` charge · `24` discharge

**Line Length:** `8` — 19 frames fill 8+8+3, 24 fill 8+8+8

Glow frames are `224 × 365` — the same canvas as `base.png`, deliberately. An
earlier plan gave them their own tighter canvas; sharing one is what makes the
registration checkable, since any offset between a glow frame and the plate is
then a straight pixel comparison. See §19, "The registration bug".

---

# 14. File Structure

```text
graphics/
├── icons/
│   └── arc-mast.png            64×64, derived from base.png
└── entity/
    └── arc-mast/
        ├── concept/            generated concepts, not shipped
        ├── base.png            224×365, the whole machine, unlit
        ├── shadow.png          512×365, draw_as_shadow, its own wider canvas
        ├── charge.png          1792×1095, 19 frames, additive glow
        └── discharge.png       1792×1095, 24 frames, additive glow
```

Four plates and no `working.png`: this building has no moving parts, so its
entire animation is emissive light and the two glow sheets *are* the working
layers. **The shadow gets its own canvas** — a five-tile tower's shadow does not
fit inside a 224 px plate, so it is 512 px wide, anchored left, and offset right
by half the extra width (`shift = {2.25, -1.875}`). It needs no *extra rows*:
the shadow lies flat and leans up and to the right, away from the camera, so it
never reaches below the plate's own bottom edge.

# 15. Factorio Prototype

**Prototype Type:** `lightning-attractor`

**Prototype Name:** `sae-arc-mast`

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
        filename = "__space-age-extended__/graphics/entity/arc-mast/base.png",
        priority = "high",
        width = 224,
        height = 365,
        shift = util.by_pixel(0, -60),
        scale = 0.5
      },
      {
        filename = "__space-age-extended__/graphics/entity/arc-mast/shadow.png",
        priority = "high",
        draw_as_shadow = true,
        width = 512,
        height = 365,
        shift = util.by_pixel(72, -60),
        scale = 0.5
      }
    }
  },
  charge_animation =
  {
    layers =
    {
      {
        filename = "__space-age-extended__/graphics/entity/arc-mast/charge.png",
        priority = "high",
        blend_mode = "additive",
        draw_as_glow = true,
        width = 224,
        height = 365,
        frame_count = 19,
        line_length = 8,
        shift = util.by_pixel(0, -60),
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
        filename = "__space-age-extended__/graphics/entity/arc-mast/discharge.png",
        priority = "high",
        blend_mode = "additive",
        draw_as_glow = true,
        width = 224,
        height = 365,
        frame_count = 24,
        line_length = 8,
        shift = util.by_pixel(0, -60),
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
Separate draw_as_shadow layer inside picture. Up-right, long, tapering, lying
flat on the ground -- 5.98 x 1.45 tiles against vanilla's 6.36 x 1.53.

Working Visualisation:
Not applicable to lightning-attractor. Charge and discharge are the whole of it.

Lights:
None. drawing_box_vertical_extension = 4.5 is inherited and must not change.
lightning_strike_offset is NOT inherited any more: it is {0, -4.14375}, and it
is tied to the picture shift. Move one and you move the other. See §12.

Fluid Boxes:
None.

Circuit Connections:
None. Not a pole; must stand inside a pole's supply area to deliver power.

Remnants:
Still lightning-collector-remnants, inherited, and wrong once this art lands.
Explicit follow-up, out of scope here.
```

---

# 16. Icon

**Icon Required:** ✓ · **Icon Size:** `64×64`

**Icon Concept:**
The bottom-heavy silhouette, compressed: a wide dark skirt, a short braced
column, the pale ceramic stack, and the blunt cratered stub, with one violet
filament on the stub so it reads as *lightning* rather than *pylon* at 32 px.
**The surge drum is dropped** — at icon size it muddies the base into a blob.
Vertical composition inside a square frame, filling the height.

### Icon Prompt

```text
Factorio "Space Age" item icon. A small rendered industrial object on a
workbench: a heavy grounded lightning terminal, bottom-heavy, with a wide
bolted dark metal base skirt, a short three-sided braced column, a stack of
four pale sand-coloured ceramic insulator discs, and a blunt cratered electrode
stub on top whose upper part is discoloured straw and blue-grey. One short
violet-white electrical filament crawls across the stub. Dark iron-nickel
grey-brown metal, #4A463F to #6E685C, kept dark and warm rather than pale, with
pale nickel-white bolt rings.

Semi-realistic sci-fi industrial painting, not flat, not cartoon, not
photo-real. Three-quarter view from slightly above, close to the game's
characteristic 45-degree top-down perspective but tipped a little more toward
the viewer the way vanilla item icons are, soft single-direction lighting
from the upper left, visible specular highlight, subtle ambient occlusion,
gentle drop shadow behind the object. Vertical object filling roughly 85% of
the frame height, centred, even padding. Bold simple silhouette that still
reads at very small size. Fully transparent background, square canvas, no
ground or platform under the object, no text, no logos, no watermark, no
border, no scene or background elements.
```

---

# 17. Visual QA Checklist

### Building

* [x] Correct tile size — 3×3 footprint under a 3.5×5.4 sprite; verified in-engine, and a row of masts no longer overlaps
* [ ] Correct perspective — 45-degree top-down read; base from above, column and tip leaning toward camera
* [ ] Correct scale
* [ ] Clear silhouette
* [ ] Looks like Factorio
* [ ] Matches intended planet — bare metal, no vegetation, no snow, no rust-red
* [ ] Inputs are visually understandable — the tip is obviously where it is hit
* [ ] Outputs are visually understandable — the drum and its cable read as grid
* [ ] **Does not read as** a rocket, a missile, a launch stand, or Fulgora's
      slender tuning-fork collector

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

### Generated-art defects

* [ ] No baked drop shadow in the colour layer — scorch and shadow separated
* [ ] No ground plane or scenery
* [ ] Alpha channel measured clear — never judged from a preview
* [ ] Palette measured inside `#4A463F`–`#6E685C` — by `--report`, not by eye
* [ ] Nothing glows — the static picture is entirely unlit
* [ ] Column taper within limit — top width ≥ ¾ of bottom width

### In-Game

* [ ] **Arcs terminate on the painted tip, not above or inside it**
* [ ] Shadow aligns with the building and does not double
* [ ] Inserters and pipes align correctly — n/a, neither touches this building
* [ ] Building doesn't overlap neighbouring entities incorrectly
* [ ] Building is recognisable in a row of masts
* [ ] Not confusable with a substation or an accumulator at a glance
* [ ] Performance is acceptable

---

# 18. Final Asset Checklist

```text
[x] Concept sheet          concept/v4-sheet.png, concept/v9-master-sheet.png
[x] Master concept         concept/v10-canonical.png -- the locked design
[x] Directional sprites    n/a, one direction
[x] Shadow                 derived; cast projection, see below
[x] Idle / static picture  base.png
[x] Working animation      charge.png (19), discharge.png (24)
[x] Glow layer             same two sheets; this building's animation IS glow
[ ] Effects layer          deferred -- better as engine effects
[x] Icon                   graphics/icons/arc-mast.png
[x] Spritesheets           built by tools/build-glow-frames.py
[x] Factorio prototype     prototypes/core/storms.lua
[x] In-game test           first pass done; four defects found and fixed, see below
```

**The shadow is still synthesised** from the colour plate's own alpha rather
than hand-authored, but it is now an actual ground projection: 5.98 × 1.45
tiles against vanilla's 6.36 × 1.53, leaning up and to the right, anchored at
the foot. The first version did not reach the screen at all — see §19.

# 19. Design Notes / Iteration History

## The first in-game test

Everything up to here passed a data-stage load and a file-by-file inspection,
and all four of the defects below still shipped. They were found by putting
three masts on the ground, recording it, and measuring the frames — the entity
geometry against the selection brackets, the sprite plates against each other.
None of them are visible in a PNG viewer.

**1. The sprite was 3.14 tiles wide on a 2 tile pitch.** A row of masts
overlapped by more than a tile. Fixed by growing the box, not shrinking the art
— §2 has the reasoning and the in-engine verification.

**2. The glow sheets sat 6 px right and 8 px above the plate.** See "The
registration bug" below.

**3. The plate floated 0.66 tiles above its own footprint,** because the shift
was anchored on the tip rather than the base plate. See §13.

**4. The shadow never rendered.** Two faults, stacked. `shadow()` in
`tools/process-building-art.py` stamped each pixel at `y + up*ky`, keeping the
source row and only *adding* the projection — a mild squash rather than a
ground cast, 4.1 tiles of standing shadow. And the plate was composited over a
transparent canvas *through its own alpha*, which squares it: the 155 the tool
asked for arrived as `155² / 255 = 94`, invisible against Core basalt. Both are
fixed; the projection now matches vanilla's proportions.

**The lesson is the one already written at the end of §19: measure the plate,
do not look at it.** It now extends past the plate to the running game. A
screen recording plus the selection brackets as a ruler is enough — the
brackets are a known 2 or 3 tiles, which calibrates pixels to tiles, and every
other geometry claim follows from that.

## The registration bug

`tools/derive-glow.py` builds the glow by subtracting the unlit plate from the
lit one, and its docstring claimed the result registers "by construction"
because both are normalised onto the same canvas. Same canvas is not the same
transform. Each plate was trimmed to *its own* alpha bounding box first, and
the lit render blooms past the metal:

```text
v11-idle.png   (unlit)  trims to 909 × 1415, x from 106
v12-charge.png (lit)    trims to 947 × 1450, x from  68
```

Different box, so a different scale (2.5% apart) and a different horizontal
centring. Every glow frame in both sheets inherited the same 6 px right, 8 px
up offset, because `build-glow-frames.py` masks one plate and so reproduces its
error identically in all 43 frames.

The fix is to measure the placement **once, off the unlit plate**, and apply
those same numbers to both. Confirmed by putting the unlit plate through the
new path and diffing against the shipped `base.png`: identical alpha bounding
box, 78 mismatched pixels out of 31,506, all of them antialiased edge.

One thing fell out of it. Scaling the whole lit render, rather than its crop,
preserves light that blooms past the silhouette — but `v12-charge.png` is
*clipped* by its own canvas top, so that corona arrived as a flat bright cap
above the electrode. The glow is now masked to the unlit plate's alpha, dilated
2 px and softened, so light only lands where the building is.

Generated in the browser against ChatGPT's image tool, portrait 2:3, master
concept prompt only. All three rounds share one conversation, so each had the
previous images in context. Concepts are in
`graphics/entity/arc-mast/concept/`: `v1-master.png` (966×1628),
`v2-master.png` and `v3-master.png` (both 1024×1536), all RGBA with genuinely
transparent backgrounds.

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| 1 | master | Splayed skirt, braided corner straps, braced lattice with copper buss bar, ceramic disc stack, ribbed drum with green lamp — every named component present. But the column tapered hard into a **conical nose cone**: a V-2 on a launch stand. | **Reject** | Keep-list, then six numbered fixes: blunt slab-sided electrode stub instead of the cone; near-parallel column sides; 1:2 proportion with the stack two thirds up and the tip in the top eighth; base seen from above, not side-on; darker warmer palette with less rust; transparent background, no baked shadow. |
| 2 | master | Nose cone gone — the top is a blunt cratered stub and the silhouette no longer reads as a rocket. Taper reduced. Every kept component carried over intact. Background genuinely transparent. | **Reject, but close** — silhouette approved in principle | Palette still pale, silvery and bleached where it should be dark warm iron; base still drawn too close to side-on; column still tapering more than asked. |
| 3 | master | Camera fixed — the base genuinely reads from above. Tip, stack, drum, straps and buss bar stable across rounds 2 and 3. Measured: alpha 60% clear, body metal `#45382D`, aspect 1:1.51. | **Reject** — on proportion and disc count only | Full object with headroom, no crop, 1:2. Four discs, counted. Column taper to the ¾ rule. **The palette instruction sent with this round was wrong** — see below. |
| 5 | master | Sent with a wrong palette instruction (see below); judged on geometry only. Aspect still ~1:1.5. | **Reject** | — |
| 6 | master | Measured: alpha 67% clear, body metal `#594C40` luminance 78 — **back inside the palette range** for the first time since round 1 — aspect 1:1.57. First round to name the camera angle, and the base finally reads from above. | **Reject** — aspect and taper | Restart clean. |
| 7 | master | **New ChatGPT session**, with vanilla's `substation.png` attached as a style-and-camera reference ("match the rendering, not the design"). Noticeably taller and narrower; drum repositioned. | **Progress** | Restart at phase 1 with the design sheet attached. |
| 8 | master | Phase-1 restart: our own approved sheet attached as the locked design. Taller again. | **Progress** | Ask for the deliverable in the example's format. |
| 9 | master sheet | With the Scrap Reclamation Plant sheet attached as a format-and-quality example: a full **Arc Mast master sheet** — title bar, CANONICAL / ALTERNATE ANGLE / TOP VIEW panels, in-game icon, three close-ups (electrode tip, ceramic insulators, surge drum) and a building information panel carrying the real data. Camera correct, palette in range, top view reads the 2×2 footprint. | **Best result so far — the design is now locked** | Two defects survive: the canonical view still draws six or seven ceramic discs while its own close-up is captioned "×4", and the column still tapers past the ¾ rule. |
| 10 | canonical | **The fix.** The CANONICAL panel was cropped out of the round 9 sheet locally and attached as the source, with instructions to *edit* it rather than regenerate: preserve every component, two changes permitted. Result: **exactly four ceramic discs**, taper reduced, and every other feature carried over intact — skirt, four braided straps, buss bar, drum, cable run, bolted collar, cratered stub. Measured: 66% clear alpha, body metal `#57483B` luminance 74 (in range), aspect 1:1.54. | **Accept as the canonical base sprite** | Only the green lamp is still lit and needs darkening for the true idle plate. |
| 4 | sheet | Every requested panel present and coherent: hero, 64×64 icon, 2×2 top view, three detail close-ups, a six-part layer breakdown matching §7 exactly, six animation key frames, two effects plates labelled additive and multiply, and an eight-swatch palette strip. **The charge animation travels down, tip to drum, as §9 requires** — the sheet understood the mechanic. | **Accept as a design sheet** — this is the design language, approved | Four corrections before the sheet is reissued: palette still reads sandy tan rather than dark iron `#4A463F`–`#6E685C`, and the swatch strip proves it; the caption says four ceramic discs while the art draws six or seven; the discharge sequence (energy leaving, travelling **up**, dimmer) is missing entirely; the column still tapers past the ¾ rule. |

### Version 1

The generator draws what it is *shown*, not what it is *told not to be*. Round
1 named every component correctly and still produced a rocket, because a
tapering tower with something on top **is** a rocket unless the anti-read is
stated as a read: "must not look like a missile" works where "no nose cone"
does not. The master prompt now leads with the anti-read and states proportion
as a ratio.

### Version 2

Three defects survived the first refinement, and the fixes for each are now
standing rules in the template:

1. **Camera.** Two rounds produced a side-on elevation. Demanding a visible
   consequence — *the top faces of the skirt plates and the top of the drum
   must be visible* — works where naming an angle does not.
2. **Palette.** Hexes alone lose to the model's weathered-steel default. The
   prompt now says what to *reduce*, and names the wrong result explicitly
   ("not pale, not silvery, not bleached").
3. **Taper.** "Slight taper" is not measurable. It is now a number: top width
   at least three quarters of bottom width.

**Measure the plate; do not look at it.** Two findings recorded here after
rounds 2 and 3 were wrong, and both came from eyeballing a transparent PNG in a
viewer that composited it onto its own dark background:

* *"Transparency was lost in round 3."* It was not. Every round has been RGBA
  with clear corners — v1 71% clear, v2 63%, v3 60%. The "painted dark vignette"
  was the preview's own backdrop.
* *"The palette is pale, silvery and bleached."* The opposite. Measured body
  metal is `#514840` (v1), `#493D32` (v2), `#45382D` (v3), against a target
  range of `#4A463F`–`#6E685C`. Round 1 sat inside the range; rounds 2 and 3
  are **below its dark floor**, and the instruction to darken further — sent
  three times — drove it there. The specular highlights and pale bolt rings
  read as "silvery" against a dark preview and misled every judgement.

`tools/process-building-art.py --report` now prints alpha split, trimmed
aspect and body-metal luminance against the §3.3 range, and warns when the
metal is past the floor. Run it before writing a refinement.

**What is actually outstanding**, measured rather than eyeballed: aspect is
1:1.46–1.51 against a 1:2 target, the ceramic stack draws six or seven discs
instead of four, and the column taper is past the ¾ rule.

### The consistency fix

The disc count survived nine rounds of being told, in words, to draw four. It
was fixed in one round by **cropping the approved view out of the sheet and
attaching it as the source**, with the instruction to edit that image rather
than generate a new one, and an explicit list of exactly two permitted changes.

That is the general rule, and it is now the reason stage 1 exists: once a design
is locked, every later image is an **edit of the approved file**, never a fresh
generation from the prompt. Words specify a design; only the image preserves
it. A generator asked to draw the same machine again will re-interpret it every
time, and the drift is invisible until you compare two frames side by side.

### What actually moved the needle

Nine rounds in, three changes did more than any amount of prompt rewriting:

1. **Naming the camera angle** — see below.
2. **Attaching a real vanilla sprite** (`substation.png`, extracted from the
   game's own files) as a style reference, with an explicit "match the
   rendering, the finish and the camera; do **not** copy the design" clause.
   The clause matters: showing the model the building we are trying *not* to
   resemble would have pulled the design toward it.
3. **Attaching an example of the deliverable format** — a finished master sheet
   for a different building — which produced a correctly laid-out Arc Mast
   sheet in one attempt, including panels and an information table that took
   several rounds to describe in words.

And one thing that helped before any of those: **starting a new conversation.**
Rounds 1–6 shared a context containing two of my own incorrect palette
corrections, and the model kept honouring them. A clean session with the
corrected prompt behaved noticeably better.

### The camera phrasing, corrected

The template originally forbade naming an angle, on the theory that "45°" makes
a generator produce clean isometric. That was wrong, and this building is the
evidence: rounds 1–3 described the camera at length without naming it and
returned side-on elevations every time, while the Scrap Reclamation Plant prompt
— which simply said *"the game's characteristic 45-degree top-down
perspective"* — got the camera right first time. Every prompt in §11 now names
the angle in those words, with the tall-building clause added after it rather
than substituted for it. "Isometric" stays banned; that one does produce a
different game.

### Process changes taken from the Scrap Reclamation Plant plan

A parallel plan written for a different building (a 5×5 scrap plant) was
reviewed against this one. It agreed with §0 and §5 on the important calls —
one canonical view first, directions produced by *editing* that file rather
than re-generating, animation components rather than whole frames, icon last —
and corrected the template on two:

1. **The shipped file set is four plates**, not nine. §7's tree describes
   content; most of it lives inside `base.png`. §14 now says so, and smoke and
   steam are engine effects rather than baked pixels.
2. **Canvas size and shift are measured from the approved art**, not guessed
   from the nominal footprint. §13 is now marked provisional — with the
   exception of the pinned tip row, which is an engine constraint the art must
   satisfy rather than a measurement to take later.

It also names a step this spec had left implicit: **idle is authored by taking
the light away.** For the Arc Mast that is already the rule (§3.3 forbids a
resting glow) but for the general case it is now in the template.

### Final

`[Not reached.]` The stage 0 sheet has settled the design language and the
layer split; what is left is a palette that has resisted three rounds of
correction, a disc count the generator will not hold, and a taper that needs
policing. Next round: reissue the sheet with those four fixes, then take the
approved hero from it into stage 1 rather than re-prompting the master from
scratch.

**On the sheet's own hero panel.** It is drawn three-quarter, closer to
isometric than to Factorio's camera. That is fine for a design sheet and must
not be inherited by the production plates — §4's camera rule still governs
stage 1 onward. The sheet also titles the building "Lightning Terminal"; the
name is `Arc Mast`, and the next sheet should say so, since this one carries
text.
