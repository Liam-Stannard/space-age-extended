# Factorio Building — Art & Implementation Specification

**Ignition Array.** Filled from `building-spec-template.md` (v2), section for
section. Every gameplay number is read off `prototypes/core/endgame.lua`,
`prototypes/core/technology.lua`, `control.lua` and vanilla's `rocket-silo`.
The art sections are proposals.

**Read §6.1 before commissioning anything.** The rocket silo has the largest
art surface of any prototype in the game — sixteen sprite and animation slots,
several of them 64-frame sheets — and a full custom set is not a realistic
target. §6.1 scopes it down to the slots that carry the read, and says plainly
what stays inherited.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **passed — `concept/v2-sheet.png`, all four round-1 corrections applied** |
| 1 | Canonical view | square | Silhouette approved against §3.1 and §17 | blocked on 0 |
| 2 | Idle plate (unlit) | square | Same machine, nothing lit | blocked on 1 |
| 3 | Directional frames | — | n/a — no rotation, see §5 | n/a |
| 4 | Glow plates | square | Differenced against stage 2 | blocked on 2 |
| 5 | Effects plate | square | Deferred — engine effects, see §10 | — |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

**Square, not portrait.** Unlike the Arc Mast this is a wide, squat, ground-
hugging building — 9×9 tiles with almost nothing above two tiles tall. Its
canvas is roughly square and its camera problem is the *flat* case in §4, not
the tall one.

### Where generation happens

Browser — ChatGPT's image tool. See template Appendices B and C; in particular,
attach a real vanilla sprite as a style reference and an example sheet as a
format reference, and once the design is locked **edit the approved file rather
than re-prompting**.

### Round log

Two rounds, both stage 0. Recorded in §19.

---

# 1. Building Overview

**Building Name:**
`Ignition Array`

**Internal Prototype Name:**
`sae-ignition-array`

**Building Type:**
`rocket-silo`, deep-copied from `rocket-silo`. The type is chosen so the
building behaves the way the player already understands one: it accumulates
parts, shows its progress on a gauge, and fires once. It is also the only
prototype that offers a "assemble N of a thing, then trigger an irreversible
event" loop without a line of control-stage script — `control.lua` only listens
for `on_rocket_launch_ordered` and calls `game.set_game_state`.

**Planet / Environment:**
`The Core.` `surface_conditions = pressure 1–9`, which is the Core and nowhere
else in the game — not a platform (0), not any vanilla world (Aquilo is lowest
at 300).

**Purpose:**
**The win condition.** It accumulates **100 Field Coil Segments**
(`fixed_recipe = "sae-field-coil-segment"`, `rocket_parts_required = 100`),
buries them in the crust and fires them at once, restarting the dead dynamo.
`launch_to_space_platforms = false`: this is an ignition, not a delivery.

**Technology Unlock:**
`Ignition Array` (`sae-ignition-array`), tier 4, prerequisite
`sae-field-coils`. **1200 geodynamic science packs** at 60 s — the most
expensive technology in the mod, and the last.

**Recipe:**
200 welded plate · 500 kamacite plate · 10 coil assembly · 200 processing unit ·
**4 arc masts**, 120 s. `stack_size = 1`, `weight = 500000`.

---

# 2. Gameplay Dimensions

Inherited from `rocket-silo` unless stated.

**Tile Size:**
`9×9`

**Collision Box:**
`[-4.42, -4.20] → [4.42, 4.20]`

**Selection Box:**
`[-4.5, -4.5] → [4.5, 4.5]`

**Placement Restrictions:**
`surface_conditions = { pressure 1–9 }`. `fast_replaceable_group` and
`next_upgrade` cleared, so it never fast-replaces a rocket silo.

**Rotation:**
`None.` `rocket-silo` has no direction. One orientation, for the life of the
building.

**Crafting Speed:**
`crafting_categories = { "sae-ignition" }`, `fixed_recipe =
"sae-field-coil-segment"`. The player cannot choose what it makes.

**Energy Consumption:**
`2 MW` idle (vanilla 250 kW) · **`50 MW` active** (vanilla 3.99 MW). An order
of magnitude past vanilla, deliberately: every megawatt the array draws is melt
that was not cast into the segments it also needs. This number *is* the
endgame's central tension, and the art should look like it eats a grid.

**Energy Type:**
`electric`.

**Health and resistances:**
Inherited. `minable = { mining_time = 5 }` — five seconds to pick up, the
slowest in the mod.

---

# 3. Visual Design

## 3.1 Design Concept

**The wrong machine it must not be:**
It currently wears **vanilla's rocket silo** unmodified, and that art is wrong
in the most specific way possible: a rocket silo is a building whose entire
visual language is *something leaving*. Blast doors that split and slide, a
gantry, a rocket standing in a hole, exhaust, a launch. The Ignition Array
sends nothing anywhere. It buries a hundred coil segments **downward** into the
crust and fires them at once, and the thing that comes out is a restarted
magnetic field, not a vehicle. The anti-read is therefore unusually strong:
**it must not look like anything is going to take off.** No gantry, no rocket,
no nose cone, no exhaust bell, no launch clamps, no countdown lights.

**Primary Visual Theme:**
**A buried coil array, seen from directly above.** Heavy circular electrical
emplacement: a ring of segment cradles around a capped central shaft, cable
trunks converging inward, everything anchored flat and pointing down.

**Overall Appearance:**
A wide, low, octagonal armoured deck flush with the crust, filling almost the
whole 9×9 footprint. At its centre a **capped shaft** — a heavy iris of
overlapping segments, closed. Around the shaft, a ring of **segment cradles**:
short angled racks, each holding one field coil segment nose-down toward the
shaft, so a full array reads as loaded and an empty one as waiting. Four
**cable trunks** enter the deck at the diagonals from outside the footprint,
thick, armoured, converging on the shaft. Between the cradles, low **capacitor
banks** and a bank of **coolant loops** in pale insulating sleeves.

**Silhouette:**
A wide dark octagon with a bright ring and a closed eye at the centre. From
altitude it reads as *"a lid over something"* — the only round building on the
Core and the only one whose detail runs in a circle rather than a line. It must
never read as a launch pad, and must not be confusable with a nuclear reactor
(square, hot) or a radar (thin, tall, rotating).

**Visual Complexity:**
`High` — this is the last building the player builds and the most expensive
thing in the mod; it should reward being looked at closely. Detail concentrates
in the cradle ring and the iris.

**Visual Age:**
`Experimental.` Everything else on the Core is proven kit. This is a one-shot
machine that has never been fired, and should look slightly over-instrumented
and slightly provisional — braced, cabled, monitored.

---

## 3.2 Key Visual Features

The building should contain:

* A **closed iris cap** over the central shaft: eight heavy overlapping
  armoured leaves, dark, with a hairline seam pattern radiating from the
  centre. This is the one thing the whole building is arranged around.
* A **ring of segment cradles** — short angled racks around the iris, each
  holding one pale-blue field coil segment tilted nose-down toward the centre.
* **Four armoured cable trunks** entering at the diagonals and converging on
  the shaft, thick enough to read at map zoom as *this building eats power*.
* **Capacitor banks** between the cradles: low ribbed cylinders lying flat, in
  pairs, cabled into the ring.
* An **octagonal anchored deck** with heavy bolt rings, walkway grating between
  the equipment, and dark scorch already present around the iris seam.

### Signature Feature

**Everything points down and inward.** Every cradle is tilted toward the
centre, every cable runs to the shaft, and the middle is a closed lid. No other
building in the game arranges itself around a hole it intends to fire into. It
is the visual opposite of a rocket silo, which arranges itself around a hole
something intends to leave through.

---

## 3.3 Colour Palette

**Primary:**
Dark iron-nickel grey-brown machined casing, `#4A463F` → `#6E685C`, matching
`building-spec-arc-mast.md` and `building-spec-vent-pump.md` so the Core's
buildings read as one set.

**Secondary:**
Pale nickel-white `#B9B4A8` on bolt rings, deck edging and cradle frames.

**Metal:**
Warm dark steel, desaturated. The array is the largest dark mass on the
planet's surface; it should sit heavy and let the accents do the talking.

**Accent — the segments:**
Field-coil pale blue `#8FA8D8`, on the coil segments in their cradles and on
the coolant sleeves. Cool and inert. This is the only cool colour on the
building and it marks *the thing being consumed*.

**Accent — copper:**
`#8A5A32`, confined to the cable trunk terminations and the busbars on the
capacitor banks, tying the array to the Arc Mast's copper.

**Working Glow:**
Violet-white `#C9B6FF` → `#FFFFFF`, at the iris seams and along the cable
trunks while the array is assembling segments. **Not a free choice:** it must
match `sae-arc`, which is vanilla's `lightning` unmodified, because the arc
masts that power this thing are in frame beside it. Nothing glows at rest.

**Warning / Status Lights:**
Amber `#FFB13B` on the cradle ring — and unlike the Arc Mast these are real:
the rocket-silo prototype has `red_lights_back_sprites` and
`red_lights_front_sprites`, which the engine drives from launch state. One
lamp per cradle, so a filling array visibly fills.

---

# 4. Factorio Visual Style

### Required characteristics

* [x] 45-degree top-down Factorio perspective — **named in the prompt**
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

**This is the *flat* camera case, not the tall one.** Nothing on this building
rises much above two tiles, so it shows mostly its **roof**, a shallow slice of
its near face, and no far face at all. Do not add the Arc Mast's "leaning
toward the viewer" clause — that is for towers, and using it here will tilt a
9×9 deck into a wall.

### Style Reference Buildings

1. `Nuclear reactor` (base)
2. `Rocket silo` (base)
3. `Electromagnetic plant` (Space Age)

**Reason for references:**
Take from the **nuclear reactor** the read of a large, heavy, flat, dangerous
installation that fills its footprint and is clearly one machine rather than a
compound. Take from the **rocket silo** only its **scale and deck construction**
— how a 9×9 building carries walkways, railings and bolt rings without becoming
noise — and **nothing** of its doors, gantry or rocket, which are exactly the
anti-read in §3.1. Take from the **electromagnetic plant** the treatment of
coils, windings and heavy cable runs as a visual subject in their own right.

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
Nothing — `rocket-silo` has no direction and cannot be rotated. One frame
carries everything, and because the design is radial that is a natural fit.

---

# 6. Sprite Assets Required

## 6.1 Main Building

**This is the scoping decision, and it is the most important section here.**
Vanilla's rocket silo uses sixteen art slots, several of them 64-frame sheets
totalling millions of pixels. Replacing all of it is not a realistic target for
generated art. The slots below are split into what we **replace** — everything
that carries the "buried coil array, not launch pad" read — and what we
**inherit or suppress**.

| Slot | Frames | Plan |
| ---- | -----: | ---- |
| `base_day_sprite` | 1 | **Replace** — the deck, ring, cradles, iris. This is the building. |
| `shadow_sprite` | 1 | **Replace** — derived from the base plate. |
| `door_back_sprite` | 1 | **Replace** — as the *back half of the iris*, not a sliding blast door. |
| `door_front_sprite` | 1 | **Replace** — front half of the iris. |
| `hole_sprite` | 1 | **Replace** — the open shaft under the iris: dark, deep, lined. |
| `hole_light_sprite` | 1 | **Replace** — violet light rising out of the open shaft. |
| `red_lights_back_sprites` / `red_lights_front_sprites` | 1 each | **Replace** — the amber cradle lamps of §3.3. |
| `crafting` working visualisation | 64 | **Replace, derived** — glow only, by the §12 method. |
| `crafting-light` | 64 | **Replace, derived** — same plate, additive. |
| `filter`, `engine`, `steam-1`, `steam-2`, `turbine` | 32–64 each | **Suppress.** All four are launch-pad furniture — extractor fans, engine bells, steam venting. Nothing on the Core vents steam (§10), and there is no engine. Set to empty. |
| `arm_01/02/03` animations | — | **Not used** by the vanilla silo prototype; nothing to do. |
| The rocket itself (`rocket-silo-rocket`) | many | **Replace the entity, not just the art** — see below. |

**Engine limits worth stating here:**

**The rocket is a real problem and this document should not pretend otherwise.**
`rocket-silo` spawns a `rocket-silo-rocket` entity and plays a launch sequence.
`launch_to_space_platforms = false` stops it *going* anywhere, but the engine
still has a rocket rise out of the building — which on a world where the whole
point is that nothing leaves would be the single most contradictory frame in
the mod.

**The fix is available, and checked against the engine's own prototypes.** The
silo carries `rocket_entity = "rocket-silo-rocket"` as a settable field, and
`rocket-silo-rocket` is a prototype type in its own right with `rocket_sprite`,
`rocket_shadow_sprite`, `rocket_glare_overlay_sprite` and its own
`rising_speed`, `engine_starting_speed` and `flying_speed`.

So the Array gets **its own rocket entity that is not a rocket**:

```lua
local column = table.deepcopy(data.raw["rocket-silo-rocket"]["rocket-silo-rocket"])
column.name = "sae-ignition-column"
-- art: a column of violet-white light rising and dispersing, not a vehicle
array.rocket_entity = "sae-ignition-column"
```

What the player sees at ignition is the iris opening and **a column of light
going up out of the shaft** — the restarted field lighting, which is exactly
what the fiction says happens. The engine still has its entity and its launch
sequence; only the art changes. `rising_speed` and `engine_starting_speed`
should be raised so the column goes up fast rather than lumbering like a
vehicle, and `flying_speed` is irrelevant because
`launch_to_space_platforms = false` means it is going nowhere.

**This is a separate asset with its own spec section, not part of the building
plate.** Ship the building first; the column is the next piece after it.

---

## 6.2 Animation Layers

| Layer          | Required | Animated | Frames |
| -------------- | -------: | -------: | -----: |
| Main structure |        ✓ |       No |      1 |
| Machinery      |      `—` |      `—` |    `—` |
| Pistons        |      `—` |      `—` |    `—` |
| Belts          |      `—` |      `—` |    `—` |
| Fans           |      `—` |      `—` |    `—` |
| Lights         |      `✓` |      `✓` |  engine-driven |
| Glow           |      `✓` |      `✓` |   `64` |
| Steam          |      `—` |      `—` |    `—` |

**Animation FPS:**
`animation_speed = 0.65`, inherited, so the derived glow sheet drops straight
into the vanilla timing.

**Animation Loop:**
`Yes` for the crafting glow — it runs continuously while segments are being
assembled. The launch sequence is one-shot and engine-driven.

**What must NOT move:**
The deck, the cradles, the cable trunks and the capacitor banks are all static.
**No fans, no turbine, no steam, no engine.** Every one of those is inherited
launch-pad furniture and every one of them is suppressed in §6.1. The only
things that move are light, the iris, and the cradle lamps.

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

**Shadow:** Derived from the base plate. A flat 9×9 building throws a short,
wide shadow — unlike the Arc Mast this one *does* fit beside its own plate, so
it needs no oversized canvas. The Core's sky never moves, so it is fixed.

**Base:** The octagonal deck, bolt rings, grating and ground scorch. Almost the
whole machine lives here — see the four-plate rule in §14.

**Main Structure:** Cradle ring, capacitor banks, cable trunks, iris housing.

**Static Machinery:** The coil segments sitting in their cradles.

**Pipes:** None. Coolant sleeves are painted into the base, not plumbed —
nothing fluid connects to this building.

**Working Machinery:** The iris leaves, as `door_back` / `door_front`.

**Lighting:** The amber cradle lamps, driven by the engine's red-lights slots.

**Glow:** Violet-white at the iris seams and along the cable trunks, plus the
light rising from the open shaft. Derived, never drawn — see §12.

**Effects:** None baked. See §10.

---

# 8. Input / Output Visualisation

**Reviewed against the engine, 2026-09-05: nothing to reconcile.** A
`rocket-silo` takes its parts from any tile touching the footprint and has no
fluid box, so the 9×9 deck carries no hard connection geometry and the art is
free of pipe flanges and port positions. The cradles and trunks are structure,
not connections.

The one thing that *is* positional is the shaft: `rocket_entity` rises from the
centre, so whatever the iris becomes must open on the centre and nothing may
occlude it. See §6.1 for the `sae-ignition-column` replacement.


## Item Inputs

| Input | Location | Direction |
| ----- | -------- | --------- |
| `sae-field-coil-segment` ingredients | any edge of the 9×9 | inserter or bot |

The array assembles its own segments from a fixed recipe, so what actually
arrives is that recipe's ingredients, on belts or by bot, at any edge.

## Item Outputs

| Output | Location | Direction |
| ------ | -------- | --------- |
| None   | —        | —         |

Nothing ever comes out. It is the end of every chain in the mod.

## Fluid Inputs / Outputs

| Fluid | Location | Connection Type |
| ----- | -------- | --------------- |
| None  | —        | —               |

## Energy

| Flow | Location | Connection Type |
| ---- | -------- | --------------- |
| In — 50 MW active | anywhere in a pole's supply area | electric network |

### Hard geometric constraints

None of the Arc Mast's kind — no engine-drawn offset has to land on a painted
feature. The constraints here are the **inherited sprite geometry**: the
replacement plates must match vanilla's shifts and sizes closely enough that
`door_back`, `door_front`, `hole` and `hole_light` still line up with the base,
because those four are drawn as separate layers at fixed offsets. Measure them
off `data/base/prototypes/entity/entities.lua` before building the plates, and
record them in §13.

### Visual Requirement

The player needs to read **how full the array is** at a glance — that is the
whole endgame loop. The cradle ring and its lamps carry that: empty cradles
read dark and bare, full ones carry a pale blue segment and a lit lamp.

---

# 9. Working Animation

## Animation Concept

Two things, and they are not the same event. **Assembly** is continuous: while
the array is building segments, light pulses inward along the cable trunks and
the iris seams breathe. **Ignition** is one-shot and engine-driven: the iris
opens, the shaft lights, and the field goes up.

Prefer the continuous read for assembly. Crafting time varies, so an animation
that depicts *completing a segment* will desynchronise from what the machine is
doing; light travelling inward does not.

### Sequence

1. Idle — deck dark, iris closed, cradle lamps dark, nothing lit.
2. Assembly begins — violet pulses travel **inward** along the four cable
   trunks toward the shaft.
3. The iris seams take up the light and glow faintly, in time with the pulses.
4. A segment completes — one more cradle lamp lights and stays lit. This is the
   only cumulative state on the building.
5. Full — all cradle lamps lit, the ring reading unmistakably loaded.
6. Ignition — the iris opens, the shaft floods with violet-white light, and the
   sequence does not return to idle.

**Frame Count:** `64` (crafting glow, inherited) · iris and lights engine-driven

**FPS:** `animation_speed = 0.65`, inherited

**Loop Duration:** ~1.6 s for the assembly glow

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
* [x] Other: `light rising from the open shaft at ignition`

### Effect Description

While assembling: violet pulses inward along the cable trunks, iris seams
glowing faintly. At ignition: the shaft floods with light.

### Prohibited effects, and why

**No steam, and this one is inherited rather than invented.** Vanilla's silo
ships two 64-frame steam sheets and a turbine, and they are suppressed in §6.1.
Pressure 5 is the Core's defining number: nothing burns and nothing vents. A
steam plume here contradicts the rule that refuses boilers and furnaces on the
planet.

**No engine exhaust, no flame, no smoke.** All launch-pad furniture, all wrong
for a machine that fires downward.

**No sparks.** Same reason as the Arc Mast: sparks read as combustion or
grinding, and the colour budget belongs to the field.

---

# 11. DALL·E Generation Requirements

**Canvas:** square for everything — the building is 9×9 and its plate is
roughly square. Generate at the largest size available. Transparent background;
measured over a dozen rounds on the Arc Mast, it is honoured.

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio Space
Age building, every panel drawn from the game's characteristic 45-degree
top-down perspective, laid out as labelled panels on a dark charcoal
background, in the style of a game art bible page.

Panels: a large hero view of the building; an in-game icon panel showing it
simplified to a 64x64 item icon; a tile-grid panel showing it from directly
overhead on a 9x9 tile grid; three close-up detail panels showing the closed
central iris, one segment cradle holding a pale blue coil segment, and a cable
trunk termination; a layer breakdown row showing shadow, deck, cradle ring,
iris and glow separated; a row of animation key frames showing violet light
pulsing inward along the cable trunks; and a palette strip of eight swatches.

The building in every panel is the same machine: a wide, low, octagonal
armoured deck lying flush with bare metallic ground, filling a nine by nine
tile footprint. At its centre a closed iris cap of eight heavy overlapping
armoured leaves. Around the iris, a ring of short angled cradles, each holding
one pale blue coil segment tilted nose-down toward the centre. Four thick
armoured cable trunks enter at the diagonals and converge on the shaft. Low
ribbed capacitor banks lie flat between the cradles, and walkway grating runs
between the equipment. Dark iron-nickel grey-brown metal, #4A463F to #6E685C,
pale nickel-white #B9B4A8 bolt rings, pale blue #8FA8D8 coil segments, copper
#8A5A32 cable terminations, violet-white #C9B6FF only in the animation and glow
panels.

It must read as a heavy buried electrical installation that fires downward into
the ground, never as a rocket launch pad: no rocket, no nose cone, no gantry,
no exhaust bell, no launch clamps, no blast doors sliding apart, nothing
pointing at the sky. Panel labels and small caption text are wanted on this
sheet. Painted semi-realistic industrial game art. No characters, no
photorealism.
```

---

## Master Concept Prompt

```text
Factorio Space Age industrial building sprite art, viewed from the game's
characteristic 45-degree top-down perspective: a heavy buried coil array,
standing alone, drawn as a game asset with no perspective vanishing point.

The building is wide and flat rather than tall, so the camera shows mostly its
roof and deck, a shallow slice of its near face, and no far face at all. It is
not seen from the side and it is not isometric.

A wide octagonal armoured deck lies flush with bare metallic ground and fills a
nine by nine tile footprint. At its centre, a closed iris cap made of eight
heavy overlapping armoured leaves, dark, with hairline seams radiating from the
middle. Around the iris runs a ring of short angled cradles, each holding one
pale blue coil segment tilted nose-down toward the centre, so the ring reads as
loaded. Four thick armoured cable trunks enter the deck at the diagonals from
outside the footprint and converge on the central shaft. Low ribbed capacitor
banks lie flat between the cradles in pairs, cabled into the ring, and walkway
grating runs between the equipment. Heavy bolt rings edge the deck, and there
is old dark scorch around the iris seam.

Everything on this machine points down and inward: every cradle tilts toward
the centre, every cable runs to the shaft, and the middle is a closed lid.

Materials: dark iron-nickel grey-brown machined metal in a mid-dark value, the
body of the metal reading around #554E45 and staying inside the range #4A463F
to #6E685C. Pale nickel-white #B9B4A8 confined to bolt rings, deck edging and
cradle frames; pale blue #8FA8D8 on the coil segments only; copper #8A5A32 only
at the cable terminations. Metal dust, scuffing and restrained wear.

State: cold and unlit. No glow, no light, no electricity visible anywhere, and
the status lamps dark.

It must read as a heavy electrical installation that fires downward into the
ground, and never as a rocket launch pad or anything preparing to take off: no
rocket, no nose cone, no gantry, no exhaust bell, no engine, no launch clamps,
no blast doors sliding apart, no countdown lights, nothing pointing at the sky,
no fire, no smoke, no exhaust, no steam.

Painted semi-realistic industrial game art, strong readable silhouette, nine
tiles across, fully transparent background with nothing painted behind the
object, no text, no logos, no characters, no UI, no ground texture, no
background scenery, no baked drop shadow.
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
inert, with absolutely nothing lit. No violet, no glow at the iris seams, no
light in the cable trunks, no lit status lamps. Every surface reads by shape
and material alone.
```

### Working Machinery

```text
Not required as a separate generation — the only moving parts are the two iris
halves, which are cut from the approved base plate rather than drawn fresh.
See §6.1 and §12.
```

### Glow / Lighting

```text
Not required as a separate generation. The glow layer is recovered by
differencing a lit version of the approved base plate against the unlit one —
see template Appendix C. Ask for the lit version with this instruction: the
same image, unchanged, with violet-white #C9B6FF light pulsing inward along the
four cable trunks and glowing along the hairline seams of the closed central
iris, and the amber status lamps on the cradle ring lit. Nothing else emits
light.
```

### Effects

```text
Not required — see §10. Nothing is baked; the shaft light at ignition is part
of the hole_light slot, not a particle effect.
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

Run `tools/process-building-art.py <plate> --report` before judging any plate,
and `--dekey` if it came back flattened onto a checkerboard. Both traps are
documented in template Appendix C.

**Three jobs are specific to this building.**

**The iris has to be cut, not drawn.** `door_back_sprite` and
`door_front_sprite` are the two halves of the iris, and they must be *cut out
of the approved base plate* so they register with it exactly — the same
edit-don't-regenerate rule that fixed the Arc Mast. The hole beneath them is
then painted in the gap they leave.

**The glow is differenced**, per Appendix C: lit minus unlit, then
`tools/build-glow-frames.py` for the 64-frame crafting sheet, with the mask
travelling **inward** along the trunks rather than down a column.

**The suppressed slots need empty art, not deletion.** `filter`, `engine`,
`steam-1`, `steam-2` and `turbine` are structural in the vanilla graphics set;
replace them with 1×1 transparent sprites rather than removing the keys, unless
a data-stage check proves the keys are optional.

---

# 13. Sprite Dimensions

**Provisional — nothing here is measured yet.** Per template §13, canvas size
and shift are measurements of the approved plate, taken after it exists. What
follows is the *target* and the inherited geometry the plates must respect.

**Tile Size:** `32` px in-game · **Scale:** `0.5` → `64` source px per tile

**Building Width:** `9` tiles → `288` in-game px → `576` source px

**Building Height:** `9` tiles → `288` in-game px → `576` source px (target;
the deck is flat, so the plate should be close to square)

**Sprite Width / Height:** `[measure after stage 1]`

**Shift:** `[measure after stage 1]`

**Fixed points:**
The inherited layer offsets. Vanilla's plates for reference:
`06-rocket-silo.png` 628×612 (base), `00-rocket-silo-shadow.png` 656×600,
`04-door-back.png` 312×286, `05-door-front.png` 332×300,
`01-rocket-silo-hole.png` 400×270. The replacements do not have to match these
sizes, but the **door and hole plates must sit correctly relative to the base**,
so their shifts are derived together, not separately.

**Spritesheet Width / Height:** `[derive from the 64-frame glow]`

**Frame Count:** `1` base · `1` shadow · `1` each door · `1` hole · `64` glow

**Line Length:** `6`, matching vanilla's crafting sheet

---

# 14. File Structure

```text
graphics/
├── icons/
│   └── ignition-array.png
└── entity/
    └── ignition-array/
        ├── concept/            generated concepts, not shipped
        ├── base.png            the deck, ring, cradles, closed iris, unlit
        ├── shadow.png          draw_as_shadow
        ├── door-back.png       iris, back half — cut from base.png
        ├── door-front.png      iris, front half — cut from base.png
        ├── hole.png            the open shaft
        ├── hole-light.png      light rising from the shaft
        ├── lights-back.png     amber cradle lamps
        ├── lights-front.png    amber cradle lamps
        ├── working.png         64 frames, the assembly glow
        └── empty.png           1×1 transparent, for the suppressed slots
```

More than the four-plate default, because `rocket-silo` demands named slots
rather than a free layer stack. The principle is unchanged: `base.png` carries
almost the whole machine, and everything else is either cut from it or derived
from it.

---

# 15. Factorio Prototype

**Prototype Type:** `rocket-silo`

**Prototype Name:** `sae-ignition-array`

### Graphics

```lua
-- Written against the vanilla graphics_set's slot names; sizes and shifts are
-- filled in from section 13 once stage 1 has passed and been measured.
local ART = "__space-age-extended__/graphics/entity/ignition-array/"
array.graphics_set =
{
  -- base, doors, hole, hole light and the cradle lamps
  -- working_visualisations: the assembly glow only; every launch-pad
  -- visualisation vanilla ships (filter, engine, steam, turbine) is replaced
  -- with an empty sprite -- see section 6.1.
}
```

### Other Visual Properties

```text
Animation:
Assembly glow, 64 frames, animation_speed 0.65 inherited. The iris and the
cradle lamps are engine-driven, not authored as loops.

Shadow:
Derived from the base plate. Flat building, so it fits beside its own plate and
needs no oversized canvas.

Working Visualisation:
One: the assembly glow. All inherited launch-pad visualisations suppressed.

Lights:
red_lights_back_sprites / red_lights_front_sprites, repurposed as the amber
cradle lamps. Engine-driven from launch state, which is what makes a filling
array visibly fill.

Fluid Boxes:
None.

Circuit Connections:
Inherited from rocket-silo.

The rocket:
array.rocket_entity = "sae-ignition-column", a deep copy of rocket-silo-rocket
whose sprites are a rising column of violet-white light rather than a vehicle.
Checked: rocket_entity is settable and rocket-silo-rocket is its own prototype
type with its own sprite and speed fields. Ship the building first; the column
is the next asset after it.
```

---

# 16. Icon

**Icon Required:** ✓ · **Icon Size:** `64×64`

**Icon Concept:**
The radial read, compressed: a dark octagonal deck, the bright cradle ring, and
the closed iris at the centre with one violet seam. The cable trunks are
dropped — at icon size four diagonals turn the silhouette into a star and lose
the octagon. Derived from the approved base plate once it exists, per the
"icon last" rule.

### Icon Prompt

```text
Factorio "Space Age" item icon. A small rendered industrial object on a
workbench: a wide, low, octagonal armoured deck with a ring of short angled
cradles around a closed iris cap at its centre, seen from slightly above. Pale
blue coil segments sit in the cradles; one hairline violet-white seam crosses
the iris. Dark iron-nickel grey-brown metal, #4A463F to #6E685C, with pale
nickel-white bolt rings.

Semi-realistic sci-fi industrial painting, not flat, not cartoon, not
photo-real. Three-quarter view from slightly above, close to the game's
characteristic 45-degree top-down perspective. Soft single-direction lighting
from the upper left, visible specular highlight, subtle ambient occlusion,
gentle drop shadow behind the object. The object fills roughly 85% of the
frame, centred. Bold simple silhouette that still reads at very small size.
Fully transparent background, square canvas, no ground or platform under the
object, no text, no logos, no watermark, no border, no scene elements.
```

---

# 17. Visual QA Checklist

### Building

* [ ] Correct tile size — fills 9×9 without overflowing it
* [ ] Correct perspective — flat case: roof-dominant, no leaning
* [ ] Correct scale
* [ ] Clear silhouette
* [ ] Looks like Factorio
* [ ] Matches intended planet — bare metal, no vegetation, no snow
* [ ] Inputs are visually understandable — edges are approachable by inserters
* [ ] Outputs are visually understandable — n/a, nothing leaves
* [ ] **Does not read as** a rocket launch pad, a nuclear reactor, or a radar
* [ ] Fill state is readable — empty cradles look empty

### Directions

* [x] North · [x] East n/a · [x] South n/a · [x] West n/a
* [x] All directions represent the same building — trivially

### Animation

* [ ] Assembly glow travels **inward**, toward the shaft
* [ ] Iris halves register exactly with the base plate
* [ ] Cradle lamps light cumulatively as segments complete
* [ ] Static components remain static
* [ ] No steam, no engine, no turbine anywhere

### Generated-art defects

* [ ] Alpha measured clear by `--report`, never judged from a preview
* [ ] Palette measured inside `#4A463F`–`#6E685C`
* [ ] No baked drop shadow, no ground plane
* [ ] Nothing glows on the base plate

### In-Game

* [ ] Doors and hole align with the base
* [ ] Inserters reach the deck edge correctly
* [ ] Shadow aligns and does not double
* [ ] The launch sequence does not show a vanilla rocket
* [ ] Recognisable at map zoom as the endgame building
* [ ] Performance acceptable at 9×9 with a 64-frame glow

---

# 18. Final Asset Checklist

```text
[ ] Concept sheet
[ ] Master concept / canonical view
[x] Directional sprites    n/a, one direction
[ ] Shadow
[ ] Idle / static picture
[ ] Iris doors (back, front)
[ ] Hole and hole light
[ ] Cradle lamps
[ ] Assembly glow (64 frames)
[ ] Suppressed-slot empty sprite
[ ] Icon
[ ] Factorio prototype
[ ] Ignition column entity    -- sae-ignition-column, see section 6.1
[ ] In-game test
```

---

# 19. Design Notes / Iteration History

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| 1 | sheet | Everything requested, and the anti-read held first time: octagonal deck, closed iris with radiating seams, ring of pale-blue segments, four converging copper trunks, capacitor banks, bolt rings. **Camera is correct — flat and roof-dominant**, which the nuclear-reactor reference clearly earned. Layer breakdown matches §7. Animation frames travel **inward**. Palette strip carries the exact §3.3 hexes and the art matches them. Information panel accurate. | **Accept as the design language** | Four corrections before the canonical view: (1) it drew NORTH/EAST/SOUTH/WEST panels, but §5 says one direction — replace with CANONICAL / ALTERNATE / TOP VIEW; (2) the cable trunks overhang the 9×9 grid in the top-down panel and need checking against the footprint; (3) the cradles read as capsules lying flat around the ring rather than tilted nose-down toward the centre; (4) the iris reads as a smooth scored disc rather than eight overlapping leaves. |
| 2 | sheet | All four round-1 corrections landed in one pass. The direction panels are gone, replaced by CANONICAL / ALTERNATE / TOP VIEW as asked. The iris is now unmistakably **eight overlapping armoured leaves** with individual thickness and lap shadows, not a scored disc. The cradles hold their segments **angled nose-down toward the centre**, and the close-up panel captions it. The tile-grid panel shows the whole building, trunks included, inside the 9×9. Layer breakdown, animation frames and palette all correct. | **Accepted — `concept/v2-sheet.png` is the locked design** | None to the design. One cosmetic note: the generator added a *Factorio Space Age* wordmark in the bottom-right corner of the sheet, which was not asked for and is not part of any asset. Harmless on an internal document; remove it before the sheet is shown anywhere outside the repo, and do not carry it into a plate. |
### Version 1

Written before any generation, from the implemented prototype and from what the
Arc Mast's dozen rounds taught. Three decisions are already made and should not
be relitigated by whoever runs the first round:

1. **Square canvas and the flat camera case.** This is a 9×9 deck, not a tower.
   The Arc Mast's "leaning toward the viewer" clause is wrong here and will
   tilt the deck into a wall.
2. **The anti-read is unusually strong**, because the inherited art is not
   merely generic but actively contradictory: a rocket silo is a building about
   *leaving*, and this one is about *firing downward*. §3.1 and §11 name that
   explicitly rather than listing banned parts.
3. **Scope before art.** §6.1 splits sixteen inherited slots into replace,
   suppress and unresolved. Commissioning a full silo art set would be weeks of
   generation for slots the player never looks at.

### Version 2

`[Changes made]`

### Final

`[Final design decisions]`
