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

> ## The design changed after this spec was written
>
> **The Array is the Suspended Core** — option R, chosen 2026-09-08 from twenty
> concepts across four sets. A colossal sphere held off the ground inside a
> heavy frame, with clear air underneath it. The decision record is
> `concept/ignition-array/options/R-suspended-core.md`; the locked panels are at
> `concept/ignition-array/adopted/`.
>
> **§0, §6, §9, §12, §13, §14, §15, §16, §17 and §18 describe what ships** and
> have been rewritten against it and against measurements of the shipped plates.
>
> **§3, §7, §10 and §11 still describe the earlier deck-and-iris design**
> and its concept prompts. They are kept as the record of a rejected building —
> the octagonal deck, the closed iris and the cradle ring are not what stands on
> the Core. Read them as history, and do not commission art from §11.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **passed — `concept/adopted/R-sheet.png`, option R, chosen against nineteen others** |
| 1 | Canonical view | landscape | Silhouette approved against §17 | **passed — `concept/adopted/R-hero.png`, with its own silhouette panel** |
| 2 | Idle plate (unlit) | landscape | Same machine, nothing lit | **passed — `array-render.png`, generated as an *edit* of the locked hero, transparent, so nothing had to be keyed** |
| 3 | Directional frames | — | n/a — no rotation, see §5 | n/a |
| 4 | Glow plates | — | Differenced against stage 2 | **passed — `R-charge-100.png` minus `R-charge-000.png`; the artist's own light, not a painted ellipse** |
| 5 | Effects plate | — | Deferred — engine effects, see §10 | n/a — the discharge is `column*.png`, drawn by `tools/build-array-column.py` |
| 6 | Icon | square | Legible at 16 px | **passed — keyed off `array-render.png`, so the icon is the building** |

Every shipped plate is cut from stage 2 by `tools/build-ignition-array.py`. No
plate is drawn from scratch and no stage was re-prompted after the lock: the
rule that cost the Arc Mast and the Bed Tender their extra rounds — *edit the
approved image, do not ask again* — held for the whole of this building.

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

| Slot | Frames | What ships |
| ---- | -----: | ---------- |
| `base_day_sprite` | 1 | **Replaced** — `base.png`, the machine itself, unlit. |
| `shadow_sprite` | 1 | **Replaced** — `base-shadow.png`, sheared out of the plate's own alpha. |
| `rocket_glow_overlay_sprite` | 1 | **Replaced** — `charge-glow.png`, the deck lit by what leaves it. |
| `door_back_sprite` / `door_front_sprite` | 1 each | **Removed — set to `nil`.** Both are optional, proved on a live 2.1.17 server rather than assumed: a silo with both nil ran the whole launch in lockstep with a vanilla silo beside it. The Suspended Core has no deck to open. |
| `hole_sprite` / `hole_light_sprite` | 1 each | **Emptied.** There is no shaft: the ground is already visible under the sphere. |
| `red_lights_back_sprites` / `red_lights_front_sprites` | 1 each | **Not used.** They are a blink cycle driven by `light_blinking_speed` and `times_to_blink`, not a counter, so they cannot show a fill state — probed on a live server. The charge is drawn from `control.lua` instead. |
| `rocket_shadow_overlay_sprite` | 1 | **Emptied** — nothing sits on the pad to cast it. |
| `graphics_set.working_visualisations` — `crafting`, `crafting-light`, `filter`, `engine`, `steam-1`, `steam-2` | 32–64 each | **All suppressed**, and none replaced. An engine and two steam plumes at pressure 5 are a lie; and a working visualisation cannot hold cumulative state anyway, which is what this machine needs to show. See §9. |
| `robot_door` | — | **Emptied** — a silo roboport hatch that our building does not draw. |
| `working_sound.sound_accents` | — | **Removed.** Four welder accents keyed by name to frames of `crafting`; with that visualisation gone they are a hard load error, not just a wrong noise. |
| `*_frozen` sprites (5) | — | **Emptied** — an iced rocket silo over a machine pressure-locked to the Core, which can never freeze. |
| The rocket (`rocket-silo-rocket`) | many | **Replaced as an entity** — `sae-ignition-discharge`, see below. |

**The charge is not in this table**, because it is not a prototype slot at all —
it is `control.lua` and `LuaRendering`. See §9, which is where the three routes
that do not work are recorded.

**Engine limits worth stating here:**

**The rocket was a real problem and this document did not pretend otherwise.**
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

So the Array got **its own rocket entity that is not a rocket**, and it is
built: `sae-ignition-discharge`, a `rocket-silo-rocket` copy with its shadow,
both flames and all five smoke plumes emptied, its explosion and its three
takeoff roars removed, and three slots replaced with the light column that
`tools/build-array-column.py` draws.

```lua
array.rocket_entity = "sae-ignition-discharge"
```

**Two inherited numbers were wrong, and rendering found them where reasoning had
not.** `rocket_initial_offset` is vanilla's `{ 0, 3.5 }` — a rocket starts low
on the pad, three and a half tiles south of the origin — which put the column
eleven tiles south of the building as a bright smear on the ground; it is
`{ 0, 0 }`. And `rocket_visible_distance_from_center = 0`, on the reasoning that
a column standing in the machine should be visible, left the parked discharge
lit in the open indefinitely, because the Array reaches
`waiting_to_launch_rocket` and stays there. Held at `1.0`, the column appears as
it leaves and not before.

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

*Rewritten against what ships. The sequence this section used to describe — light
pulsing inward along four cable trunks, cradle lamps latching one per segment —
belonged to the deck design and to a 32-frame sheet that was actually built
before the design was replaced. It is in §19.*

## Animation Concept

**Two things, and they are not the same event.** The **charge** is cumulative and
continuous: it climbs the sphere over the whole hundred-segment build. The
**ignition** is one-shot and engine-driven.

**The charge is not a prototype slot, and that is the finding worth keeping.**
Three routes were probed on a live 2.1.17 server rather than reasoned about:

* `red_lights_back_sprites` / `red_lights_front_sprites` are a **blink cycle**,
  driven by `light_blinking_speed` and `times_to_blink`. They are not a counter
  and cannot show a level.
* A `working_visualisation` plays *while the machine crafts*. It has no access to
  how much has been built.
* `LuaEntity` in 2.1.17 has no `disabled_working_visualisations`, so named
  visualisations cannot be switched per entity from script either.

So the charge is drawn by `control.lua` with `LuaRendering`, off
`(rocket_parts + crafting_progress) / rocket_parts_required` — a smooth 0–1
across the whole build rather than a hundred steps, because `crafting_progress`
is the segment currently in flight. One `draw_sprite` of `charge-glow.png` whose
alpha *is* the charge, and one `draw_light` whose intensity is
`0.15 + 0.55 × charge`. Below 0.001 both are destroyed rather than faded, so a
dormant Array costs the renderer nothing and **nothing glows at rest**.

The Arrays are held in a registry keyed by unit number, maintained on build and
destroy events; a whole-surface `find_entities_filtered` once a second to track a
handful of endgame buildings is work the map does not need to do. It is updated
every 20 ticks — three times a second, which is plenty for a ramp.

### Sequence

1. **Idle** — nothing drawn. No glow, no light, no working visualisation.
2. **Charging** — the sphere's bands fill with violet as segments accumulate,
   and the machine casts a violet light that brightens with them.
3. **Full** — the whole shell lit, the gap beneath it glowing. This is the state
   the concept sheet's 100% frame draws, and it is what "loaded" looks like.
4. **Ignition** — `charge-glow.png` again as `rocket_glow_overlay_sprite`, the
   same plate at the same shift, floods the machine additively; the light column
   rises; the game ends. It does not return to idle.

**Frame Count:** none on the building — the charge is one plate whose alpha
ramps, and there is nothing to step. The discharge's flicker is 8 frames.

**Verified on the rig:** charge reported 0.25 / 0.50 / 0.75 / 0.99 with the
glow's alpha and the light's intensity tracking it, nothing drawn at all at rest,
then `doors_opening` → `rocket_rising` → `rocket_ready` with no door sprites to
open, `launch_rocket` returning true, and the ignition firing.

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

* [x] Remove background — n/a, the production render came back on real
      transparency rather than a checkerboard, so nothing had to be keyed. This
      is the one thing the Suspended Core got for free: R's own review said the
      concept sheet **could not** be keyed, because the building's darks overlap
      the charcoal it was drawn on.
* [x] Remove unwanted shadows/background objects — none present
* [x] Crop to building — `solid()` at alpha 40, then `getbbox()`
* [x] Correct perspective — see the note below; not fully solved
* [x] Match Factorio scale — 576 px of drawn machine, 9.000 tiles exactly
* [x] Convert to appropriate resolution — LANCZOS to the target width
* [x] Align to tile grid — centred to 0.0 px on both axes
* [x] Separate layers — plate, shadow and charge glow
* [x] Generate directional sprites — **skip, one direction**
* [x] Generate animation frames — none on the building; the discharge's flicker
      is 8 frames of `column-flame.png`
* [x] Generate spritesheets — n/a, single plates
* [x] Optimise PNGs

Everything above is `tools/build-ignition-array.py`, which is the only thing
allowed to write the shipped plates. Run it with `--check` to measure without
writing.

**Three jobs are specific to this building.**

**The alpha has to be snapped.** Re-encoding left the body at alpha 252–253.
Left alone, that is a building the ground shows faintly through, on every pixel,
for ever. Anything at 240 or over is forced to 255.

**The plate needs a transparent rim.** A render cropped to its own content puts
opaque pixels on all four canvas edges, which fails Appendix C's check 2 — the
one the arc mast still fails. Four pixels a side, at scale 0.5, is 0.0625 tiles
of empty canvas: it changes nothing on screen, and the drawn machine stays 576
px, still 9.000 tiles, still centred. The shadow needs twelve, because a 3 px
Gaussian carries about nine pixels past its mask.

**The glow is differenced, not painted.** `R-charge-100.png` minus
`R-charge-000.png` is exactly the light the artist put on the machine, because
the two frames are the same render with the power on and off. The two panels are
cropped to their own panel bounds, so they are registered on the *building*
before subtracting.

**What is not solved: the camera.** The render is 0.911 wider than tall, so at
nine tiles wide it is 8.20 tiles high and under-fills its own footprint by 0.80.
That is a camera artefact — Factorio draws buildings mostly roof, and this render
is more front-on than that — and fixing it means a re-render at a steeper camera,
not a different number. The slack is split 0.40 a side rather than parked at one
end; see §13.

---

# 13. Sprite Dimensions

**Measured off the shipped plates, not targeted.** Template §13 exists because
guessing these numbers cost the Arc Mast three rounds.

**Tile Size:** `32` px in-game · **Scale:** `0.5` → `64` source px per tile

**Building Width:** `9` tiles → `576` source px of drawn machine — the footprint
exactly, overhanging on neither side

**Building Height:** `8.203` tiles → `525` source px. Short of the 9-tile box by
`0.797` tiles, split `0.40` a side.

| Plate | Canvas | Drawn content | Shift | Scale |
| ----- | ------ | ------------- | ----- | ----- |
| `base.png` | 584 × 533 | 576 × 525 → 9.000 × 8.203 tiles | `{ 0.0, 0.0 }` | 0.5 |
| `base-shadow.png` | 655 × 557 | 594 × 538, the plate's own alpha sheared and blurred | `{ 0.36719, 0.0 }` | 0.5 |
| `charge-glow.png` | 584 × 533 | same canvas as the base, pixel for pixel | `{ 0.0, 0.0 }` | 0.5 |
| `column.png` | 208 × 512 | the discharge, drawn foot-down | `{ 0.0, -4.0 }` | 0.5 |
| `column-glare.png` | 384 × 384 | on the foot | `{ 0.0, 0.0 }` | 0.5 |
| `column-flame.png` | 1856 × 232 | 8 frames of 232 × 232, line length 8 | `{ 0.0, 0.0 }` | 0.5 |

**Checked against Appendix C, all four checks:**

1. **Centred** — content centre equals canvas centre to `0.0` px on both axes.
2. **Not clipped** — alpha is `0` down both edge columns and along both edge
   rows, on the base, the shadow and the glow.
3. **Fits the box** — visible half-width `288` px × `0.5` ÷ `32` = **4.50
   tiles**, against a 9×9 selection box's 4.5.
4. **Declared equals actual** — the four `width`/`height` pairs in
   `prototypes/core/endgame.lua` are the files' own sizes, and
   `column-flame.png` holds its 8 frames at line length 8 (1856 = 8 × 232).

**Two shifts that are solved rather than typed.** The base's is `{ 0, 0 }`
because the plate is *shorter* than its footprint: vanilla parks a silo's bottom
edge past the south edge, which works when the art is larger than the box and
here would dump all 0.80 tiles of slack at the north — 1.19 tiles of empty box
above the machine and 0.39 poking out below it. The shadow's is
`(Ws − Wb − 2·bleed) / 2` tiles, solved from where the base's own pixel (0, 0)
sits inside the sheared canvas, not assumed.

**The shadow's lean is vanilla's.** Its silo shadow is 656 px wide against a 628
px base and sits 0.5625 tiles east, so it leans about 0.78 tiles over a
9.56-tile height: a shear of **0.0817**. An early pass used 0.55, which throws
this building's shadow four and a half tiles east and reads as a separate object
lying on the ground beside it.

**Body luminance 68.5, saturation 0.353**, measured over the plate's opaque
pixels — inside §3.3's band and inside the four vanilla style references
(`tools/check-sheet-style.py` measured the adopted sheet at luminance 65.3,
saturation 0.262, detail density 0.185, base flatness 0.904).

**Frame Count:** `1` base · `1` shadow · `1` charge glow · `8` discharge flicker

---

# 14. File Structure

```text
graphics/
├── icons/
│   └── ignition-array.png      keyed off array-render.png, so the icon is the building
└── entity/
    └── ignition-array/
        ├── concept/
        │   ├── adopted/        option R: sheet, hero, top-down, five charge frames, discharge
        │   └── …               the rejected deck-and-iris rounds, kept as the record
        ├── array-render.png    the production render: unlit, transparent, an EDIT of the hero
        ├── base.png            the machine, unlit
        ├── base-shadow.png     draw_as_shadow, sheared from base.png's alpha
        ├── charge-glow.png     100% minus 0%, additive — the charge and the ignition
        ├── column.png          the discharge, a column of light
        ├── column-glare.png    its glare at the foot
        └── column-flame.png    8-frame flicker at the foot
```

Eight files against the ten this section used to list, and the difference is the
design: there are no iris halves, no shaft, no shaft light and no cradle lamps,
because the Suspended Core has no deck to put them in. The principle is
unchanged and stronger for it — `array-render.png` carries the whole machine,
and **every other file here is cut or derived from it**, so nothing can drift out
of register with anything else.

Two tools own this directory: `tools/build-ignition-array.py` for the three
building plates, `tools/build-array-column.py` for the three discharge plates.

---

# 15. Factorio Prototype

**Prototype Type:** `rocket-silo` · **Prototype Name:** `sae-ignition-array`

All of it is in `prototypes/core/endgame.lua`; this is what is wired, not a
proposal.

### Graphics

```lua
local IA = "__space-age-extended__/graphics/entity/ignition-array/"

array.graphics_set = { working_visualisations = {} }   -- all six suppressed, §6.1
array.base_day_sprite   = { filename = IA .. "base.png",
                            width = 584, height = 533, shift = { 0.0, 0.0 }, scale = 0.5 }
array.shadow_sprite     = { filename = IA .. "base-shadow.png", draw_as_shadow = true,
                            width = 655, height = 557, shift = { 0.36719, 0.0 }, scale = 0.5 }
array.base_front_sprite = util.empty_sprite()
array.base_night_sprite = nil
array.door_back_sprite  = nil   -- optional, proved on a live server
array.door_front_sprite = nil
array.hole_sprite       = util.empty_sprite()
array.hole_light_sprite = util.empty_sprite()
array.rocket_shadow_overlay_sprite = util.empty_sprite()
array.rocket_glow_overlay_sprite = { filename = IA .. "charge-glow.png",
                            blend_mode = "additive", draw_as_glow = true,
                            width = 584, height = 533, shift = { 0.0, 0.0 }, scale = 0.5 }
array.rocket_entity = "sae-ignition-discharge"
```

### Other Visual Properties

```text
Animation:
None on the building. The machine is one plate; everything that moves on it is
either drawn by control.lua or is the engine's own launch sequence.

Shadow:
Derived from the plate's alpha at vanilla's own shear, 0.0817. Fixed: the Core's
sky never moves.

Working Visualisation:
None. All six of vanilla's are suppressed and none is replaced -- see §9. A
working visualisation cannot hold cumulative state, which is the only thing this
machine needs to show.

The charge:
control.lua draws it. `sae-ignition-charge-glow` is charge-glow.png declared as a
sprite prototype, because LuaRendering needs a name and cannot be handed a
filename. It is the same plate at the same shift as rocket_glow_overlay_sprite,
so the glow the player watches climb is pixel for pixel the glow that floods the
machine when it fires.

Lights:
One rendering.draw_light per charging Array, utility/light_medium, violet
(0.62, 0.48, 1.0), intensity 0.15 + 0.55 x charge. Destroyed rather than faded to
zero at rest, so a dormant Array costs the renderer nothing.

Fluid Boxes:
None.

Circuit Connections:
Inherited from rocket-silo -- ordinary modding, not a leftover.

The rocket:
sae-ignition-discharge, a rocket-silo-rocket copy emptied of every sprite, flame,
plume and roar, with column.png, column-glare.png and column-flame.png in the
three slots that are left. See §6.1 for the two offsets that had to be measured.
```

---

# 16. Icon

**Icon Required:** ✓ · **Icon Size:** `64×64`, shipped as vanilla ships one — a
`120×64` mipmap strip, four levels

**What ships.** `tools/key-icons.py graphics/icons
graphics/entity/ignition-array/array-render.png:ignition-array` — the icon is
the production render itself, cropped, squared and downsampled, exactly as every
other building icon in this mod is derived from its own plate. The render
already carries real alpha, so no keying was needed and nothing was re-prompted.

**Judged at 16 px, not by eye at 64.** At the size the player actually sees it in
a full inventory it reads as a heavy arch with a bright gap beneath it — which is
this design's own silhouette, the daylight under the sphere, and it is the one
shape nothing else in the mod has. It occupies 63% of the icon field.

**The icon concept below is the rejected design's** and is kept with §3. There is
no icon prompt any more: an icon derived from the shipped plate cannot disagree
with the building, and a generated one can.

**Icon Concept (rejected design, for the record):**
The radial read, compressed: a dark octagonal deck, the bright cradle ring, and
the closed iris at the centre with one violet seam. The cable trunks are
dropped — at icon size four diagonals turn the silhouette into a star and lose
the octagon.

---

# 17. Visual QA Checklist

Measured, not looked at. Every box here was ticked by a number.

### Building

* [x] Correct tile size — 9.000 tiles wide on a 9×9 footprint, nothing spills
      sideways
* [x] Correct perspective — square to the grid, base flatness 0.904 where two
      rejected options were drawn corner-on. **One reservation:** the render is
      more front-on than Factorio's mostly-roof camera, which is why it is 0.80
      tiles short vertically. See §12.
* [x] Correct scale — human-scale cues (walkways, ladders, handrails) are on the
      towers, so the mass reads as enormous rather than as a small object drawn
      large
* [x] Clear silhouette — the sheet carries its own silhouette panel, and the
      icon at 16 px is the same shape
* [x] Looks like Factorio — luminance 65.3, saturation 0.262, detail density
      0.185, all three inside the bands taken off four vanilla references
* [x] Matches intended planet — bare metal, no vegetation, no snow, nothing that
      burns
* [x] Inputs are visually understandable — the base slab is approachable on all
      four edges
* [x] Outputs are visually understandable — n/a, nothing leaves
* [x] **Does not read as** a rocket launch pad, a nuclear reactor or a radar —
      no rocket read was the constraint that eliminated most of the twenty
      options
* [x] Fill state is readable — the charge climbs the sphere's bands, and it is
      the whole reason this option won

### Directions

* [x] North · [x] East n/a · [x] South n/a · [x] West n/a
* [x] All directions represent the same building — trivially

### Animation

* [x] The charge is continuous, not stepped — `(rocket_parts +
      crafting_progress) / rocket_parts_required`, a smooth 0–1 across the whole
      build rather than a hundred clicks
* [x] The glow registers exactly with the base plate — same canvas, same shift,
      cut by the same tool
* [x] Nothing glows at rest — the drawn objects are destroyed below 0.001, not
      faded
* [x] Static components remain static
* [x] No steam, no engine, no turbine anywhere — all six vanilla visualisations
      suppressed

### Generated-art defects

* [x] Alpha measured clear rather than judged from a preview — alpha 0 on all
      four canvas edges of all three plates
* [x] Palette measured — body luminance 68.5, saturation 0.353 over the plate's
      opaque pixels
* [x] No baked drop shadow, no ground plane — the shadow is a separate plate
      derived from the alpha
* [x] Nothing glows on the base plate — the production render is the *unlit*
      machine; the hero panel is effectively 25% charged and was not used

### In-Game

* [x] Shadow aligns and does not double — one shadow plate, and vanilla's
      `*_frozen` art emptied so nothing draws twice
* [x] The launch sequence does not show a vanilla rocket — `sae-ignition-
      discharge`, run end to end on a headless 2.1.17 server
* [x] The charge tracks the build — reported 0.25 / 0.50 / 0.75 / 0.99 on the
      rig, with the glow's alpha and the light's intensity following it
* [x] The win condition is reachable — the silo GUI's **Launch** button is
      present and enables at 100%, checked in a real client, not inferred
* [x] Performance acceptable — no 64-frame sheet ships at all; the building is
      three plates and one drawn sprite per Array
* [ ] Inserters reach the deck edge correctly — not tested; the Array has a fixed
      recipe and is fed by belt or bot in practice, but nobody has put an inserter
      against it
* [ ] Recognisable at map zoom — not measured

---

# 18. Final Asset Checklist

```text
[x] Concept sheet            concept/adopted/R-sheet.png, option R of twenty
[x] Master concept / canonical view   concept/adopted/R-hero.png
[x] Directional sprites      n/a, one direction
[x] Idle / static picture    base.png
[x] Shadow                   base-shadow.png
[x] Charge glow              charge-glow.png, differenced 100% - 0%
[x] Charge display           control.lua, LuaRendering, sprite + light
[x] Discharge                column.png, column-glare.png, column-flame.png
[x] Ignition entity          sae-ignition-discharge
[x] Suppressed slots         doors nil, hole/hole-light/robot-door/frozen emptied
[x] Icon                     keyed off array-render.png
[x] Factorio prototype       prototypes/core/endgame.lua
[x] In-game test             headless 2.1.17: placed, charged, launched, ended;
                             and the Launch button seen in a real client
```

---

# 19. Design Notes / Iteration History

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| 1 | sheet | Everything requested, and the anti-read held first time: octagonal deck, closed iris with radiating seams, ring of pale-blue segments, four converging copper trunks, capacitor banks, bolt rings. **Camera is correct — flat and roof-dominant**, which the nuclear-reactor reference clearly earned. Layer breakdown matches §7. Animation frames travel **inward**. Palette strip carries the exact §3.3 hexes and the art matches them. Information panel accurate. | **Accept as the design language** | Four corrections before the canonical view: (1) it drew NORTH/EAST/SOUTH/WEST panels, but §5 says one direction — replace with CANONICAL / ALTERNATE / TOP VIEW; (2) the cable trunks overhang the 9×9 grid in the top-down panel and need checking against the footprint; (3) the cradles read as capsules lying flat around the ring rather than tilted nose-down toward the centre; (4) the iris reads as a smooth scored disc rather than eight overlapping leaves. |
| 2 | sheet | All four round-1 corrections landed in one pass. The direction panels are gone, replaced by CANONICAL / ALTERNATE / TOP VIEW as asked. The iris is now unmistakably **eight overlapping armoured leaves** with individual thickness and lap shadows, not a scored disc. The cradles hold their segments **angled nose-down toward the centre**, and the close-up panel captions it. The tile-grid panel shows the whole building, trunks included, inside the 9×9. Layer breakdown, animation frames and palette all correct. | **Accepted — `concept/v2-sheet.png` is the locked design** | None to the design. One cosmetic note: the generator added a *Factorio Space Age* wordmark in the bottom-right corner of the sheet, which was not asked for and is not part of any asset. Harmless on an internal document; remove it before the sheet is shown anywhere outside the repo, and do not carry it into a plate. |
**Round 3 — the design was replaced, not refined.** Rounds 1 and 2 above locked
the octagonal deck, and a v3 was then taken as far as cut iris blades, a drawn
shaft, a 32-frame assembly glow and a screenshot rig to check them on. It was
put aside anyway: the Array is the last building in the game and it had been
drawn as another machine. Twenty concepts across four sets followed —
`concept/ignition-array/options/README.md` records what each set cost — and **option R,
the Suspended Core, was adopted on 2026-09-08**.

What the four sets taught, in one line each: tier zero is riveted and rusted and
that is the landing-day machines; tier four overshoots into generic science
fiction and measured at half vanilla's chroma; the register that works is
advanced fabrication with Factorio's mechanical density still on it; and
spectacle is a *height* decision, not a detail one.

**The cosmetic note from round 2 is closed by the replacement.** The *Factorio
Space Age* wordmark the generator added unasked lives on `concept/v2-sheet.png`,
which is a rejected sheet in the concept folder. No shipped asset was ever cut
from it.

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
