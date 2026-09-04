# Factorio Building — Art & Implementation Specification

**Quench Turbine.** Filled from `building-spec-template.md`. Every gameplay
number here is the implemented, engine-verified value (see
`design/vulcanus-fulgora.md` §9.6), not a proposal. The art sections *are*
proposals: the building currently wears vanilla's steam turbine recoloured, and
this document exists to commission a replacement.

**Open naming question — see §19 before writing any filename.** The technology
that unlocks this building is still called Thermionic Power and its ingredient
is still the Thermionic Assembly, both inherited from a reactor design that no
longer exists. One of the three names should move.

---

## 1. Building Overview

**Building Name:**
`Quench Turbine`

**Internal Prototype Name:**
`sae-quench-turbine`

**Building Type:**
`generator` — the engine computes output from fluid flow, heat capacity and
temperature, and clips anything above `maximum_temperature`. That clipping is
the mod's central mechanic, so the entity type is load-bearing and must not be
swapped for a scripted machine.

**Planet / Environment:**
`Space platforms only.` Gated by a real physical surface property
(`pressure = 0`), the same gate vanilla uses for the thruster — never by a
planet-name rule.

**Purpose:**
Converts Quench Vapour into electricity. The vapour is made on the same
platform by a quench recipe that combines a Magmatic Core shipped from Vulcanus
with locally caught Ice. Because the turbine cannot use vapour hotter than
315°C, the recipe tier the player has unlocked — not the item — decides how much
electricity one core is worth: 90 MJ on the lean quench, 600 MJ on the
cryogenic quench.

**Technology Unlock:**
`sae-thermionic-power` (see the naming question in §19)

---

## 2. Gameplay Dimensions

**Tile Size:**
`3×5` when facing north, `5×3` when facing east.

**Collision Box:**
`[-1.25, -2.35] → [1.25, 2.35]`

**Selection Box:**
`[-1.5, -2.5] → [1.5, 2.5]`

**Placement Restrictions:**
Space platforms only, via `surface_conditions = { property = "pressure", min = 0, max = 0 }`.
Verified in-engine: builds on a platform, refused on Nauvis.

**Rotation:**
`2-way.` `two_direction_only = true` — vertical and horizontal only, exactly
like vanilla's steam turbine. **This is the single most important art
constraint in this document; see §5.**

**Crafting Speed:**
n/a — not a crafting machine.

**Energy Consumption:**
None. It is a producer: **18.000 MW** at the temperature cap, measured, not
derived. Output is linear in vapour temperature below the cap (11.100 MW at
200°C) and hard-clipped above it (18.000 MW at 900°C, not 53).

**Energy Type:**
Consumes `fluid` (Quench Vapour), produces `electric` on
`secondary-output` priority. It draws vapour only on demand, so a platform
parked at a waypoint consumes no cores at all — measured at 0 MW and zero
consumption with no load, and 3.000 MW against a 3 MW load.

---

# 3. Visual Design

## 3.1 Design Concept

**Primary Visual Theme:**
Cryogenic turbomachinery. Precision-machined, cold, sealed. Explicitly **not**
heavy industry and **not** a boiler — the heat all happens in the chemical plant
next door, and this machine's job is to be the cold end of that process.

**Overall Appearance:**
A long, low, sealed turbine housing lying along its axis, with a bladed rotor
visible through a circular inspection port at one end and heavy flanged
pipework entering at both ends. Ribbed or finned casing along the barrel.
Everything should look bolted down and pressure-tight, as befits a machine that
runs in vacuum.

**Silhouette:**
An elongated cylinder with one distinctly larger circular housing at the intake
end — the shape reads as "turbine" instantly and as "not a chemical plant" at
any zoom. The long axis must be unmistakable so a player can tell its rotation
at a glance.

**Visual Complexity:**
`Medium.` Detailed casing and pipework, but a single clear focal point. It will
sit in rows of three or more beside a chemical plant and a radiator field, so it
must not compete for attention.

**Visual Age:**
`Advanced.` Post-Aquilo engineering, cleaner and more precise than Nauvis-era
machinery, but not alien or experimental.

---

## 3.2 Key Visual Features

The building should contain:

* A bladed turbine rotor visible through a circular port, which is the one part
  that animates.
* Heavy flanged fluid connections at both ends of the long axis, matching the
  two pipe connections in §8.
* A ribbed or finned pressure casing along the barrel.
* Frost or condensation gathering on the intake end, falling off toward the
  exhaust end — the visual tell that this is the cold machine.
* Recessed inspection panels and bolt lines that read as "sealed for vacuum".

### Signature Feature

**The frosted intake and the exposed rotor, together.** A viewer should be able
to tell which end the vapour enters from the frost alone, and should see the
rotor spinning when the platform is drawing power. Nothing else in the mod's
buildings has either cue.

---

## 3.3 Colour Palette

The current recolour is authoritative — the new art should match it, so the
building does not change identity when the art is replaced.

**Primary:**
Dark grey-green machined metal casing.

**Secondary:**
Cyan-teal painted panels and pipe collars, hue ≈ 182°.

**Metal:**
Cool steel, deliberately desaturated so the teal reads as paint on metal rather
than as glowing material.

**Accent:**
Teal, ramping roughly `#0E7482` in shadow → `#26AAB6` midtone → `#ACEEF0`
highlight.

**Working Glow:**
Pale cyan-white, low intensity. It is a cold machine; it should never glow
orange or look like it is burning anything.

**Warning / Status Lights:**
A small amber lamp for "no vapour". This is the only warm colour permitted
anywhere on the building.

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

### Style Reference Buildings

1. `Steam turbine` (base)
2. `Fusion generator` (Space Age)
3. `Cryogenic plant` (Space Age)

**Reason for references:**
Take the **proportions and the rotor-through-a-port motif** from the steam
turbine — it is the same footprint and the same two-direction rotation, so its
silhouette is already proven to read at this size. Take the **sealed, precise,
plated construction** from the fusion generator, which is the correct era. Take
the **cold palette and frost treatment** from the cryogenic plant. Take nothing
from the steam turbine's colour: the whole point of the recolour was that it
must not read as a vanilla steam turbine sitting on a platform.

---

# 5. Building Orientation

## Required Directions

* [x] North
* [x] East
* [ ] South — **not required**
* [ ] West — **not required**

**Direction count:**
`2.` The prototype sets `two_direction_only = true`, so the engine only ever
draws the north (vertical, `-V`) and east (horizontal, `-H`) sheets. Producing
south and west art would be wasted work and would silently go unused.

This is a deviation from the template's default, and it is deliberate. The
generic four-direction checklist in the template does not apply to this
building.

All directions must represent the **same physical building**.

The following must remain consistent between the vertical and horizontal
sheets:

* Overall dimensions (3×5 becomes 5×3; the building does not change size)
* Building height
* Major machinery — the rotor is at the same physical end of the machine
* Pipes — both connections stay on the long axis
* Windows
* Vents
* Platforms
* Decorative elements
* Colour scheme
* Material construction

Only the viewing direction should change.

---

# 6. Sprite Assets Required

## 6.1 Main Building

| Asset         | Required | Frames | Directions |
| ------------- | -------: | -----: | ---------: |
| Main building |        ✓ |    `8` |      `2` |
| Shadow        |        ✓ |    `8` |      `2` |
| Idle state    |        ✓ |    `1` |      `2` |
| Working state |      `✓` |    `8` |      `2` |

Idle and working are the same sheet: the engine advances the animation only
while the turbine is producing, so frame 1 is the idle pose. No separate idle
asset is needed.

---

## 6.2 Animation Layers

| Layer          | Required | Animated | Frames |
| -------------- | -------: | -------: | -----: |
| Main structure |        ✓ |       No |      1 |
| Machinery      |      `✓` |      `✓` |    `8` |
| Pistons        |      `—` |      `—` |    `—` |
| Belts          |      `—` |      `—` |    `—` |
| Fans           |      `✓` |      `✓` |    `8` |
| Lights         |      `✓` |      `—` |    `1` |
| Glow           |      `✓` |      `—` |    `1` |
| Steam          |      `—` |      `—` |    `—` |

"Machinery" and "Fans" are the same object here: the turbine rotor. No steam
layer — the machine is sealed and running in vacuum, and vanilla's steam
turbine's exhaust plume was deliberately dropped for exactly that reason.

**Animation FPS:**
`30` (vanilla steam turbine's rate; the rotor should look fast, not stately)

**Animation Loop:**
`Yes`

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
Separate greyscale alpha sheet, offset down-right to match vanilla's sun angle.
Must not include the rotor's motion — a static silhouette across all 8 frames.

**Base:**
The mounting feet and the footprint the building sits on. No platform-floor
decoration; the platform tile shows through.

**Main Structure:**
The casing barrel, end housings, flanges and bolt detail. Static, one frame,
and the bulk of the pixels.

**Static Machinery:**
Pipework, valves, the inspection port ring, cable runs. Static.

**Working Machinery:**
The rotor blades only, 8 frames. Nothing else may move — see §17.

**Lighting:**
The amber "no vapour" status lamp, drawn as a separate low-opacity layer so it
can be shown independently of the working state.

**Effects:**
Frost/condensation on the intake end. Static, part of the main structure's
paint rather than a live effect.

---

# 8. Input / Output Visualisation

## Item Inputs

None. The turbine takes no items — no fuel slot, no module slots, no inserter
interaction at all. **Art must not show a fuel hatch, hopper or inserter pad**,
which would tell the player something untrue about how it is supplied.

## Item Outputs

None.

## Fluid Inputs

| Fluid           | Location                          | Connection Type |
| --------------- | --------------------------------- | ---------------- |
| `Quench Vapour` | `{0, -2}` north end, and `{0, 2}` south end | `input-output` pipe connection, filtered to `sae-quench-vapour`, minimum temperature 100°C |

Both connections are inputs; the turbine has no output fluid. Volume 200. Having
a connection at each end lets turbines be chained in a line off one vapour
header, which is how they will actually be built — the art must make both ends
look equally like a connection point.

## Fluid Outputs

None. Electricity leaves through the electric network, so the building needs to
read as connected to power poles, not as plumbed to an output.

### Visual Requirement

Input/output points should be visually obvious without making the building
excessively cluttered.

---

# 9. Working Animation

## Animation Concept

The rotor spins up and holds. There is no cycle, no batch, and no product — the
turbine either has vapour and demand or it does not, so the animation is a
simple continuous loop rather than a process with a beginning and an end. The
engine ties playback speed to output, so a turbine running at partial load
visibly turns more slowly, which is a free and genuinely useful readout.

### Sequence

1. Idle: rotor stationary, frost visible, status lamp amber.
2. Vapour arrives and the grid draws: lamp goes out, rotor begins to turn.
3. Rotor reaches full speed; blade blur becomes continuous.
4. Held indefinitely while producing — this is the state players will see 99% of
   the time.
5. Demand falls: rotor slows proportionally, driven by the engine, not by
   separate frames.
6. Vapour exhausted: rotor coasts to a stop, lamp returns to amber.

**Frame Count:** `8`

**FPS:** `30`

**Loop Duration:** `0.27 seconds` per revolution at full output

---

# 10. Effects

## Working Effects

* [x] Glow — faint cyan rim light on the rotor port only
* [ ] Steam
* [ ] Smoke
* [ ] Sparks
* [ ] Flames
* [ ] Electrical arcs
* [x] Moving fluids — optional, a subtle flicker in a sight glass on the intake
* [x] Other: `frost that does not animate`

### Effect Description

While running, the rotor turns and the port emits a faint cold rim light.
Nothing is vented, nothing is emitted into the surrounding tiles, and no
particle effect leaves the building's own footprint. This is a sealed machine in
vacuum, and vanilla's steam-turbine exhaust plume was explicitly removed from
the current prototype for that reason. Adding an emission back would be a
correctness regression, not a flourish.

---

# 11. DALL·E Generation Requirements

## Master Concept Prompt

```text
A Factorio Space Age industrial building sprite, 45-degree top-down
perspective: a long sealed cryogenic turbine lying horizontally, with a bladed
turbine rotor visible through a circular inspection port at one end, heavy
flanged pipe connections at both ends of its long axis, and a ribbed pressure
casing along the barrel. Painted in cyan-teal panels over dark grey-green
machined metal, with cool steel fittings and pale frost gathering on the intake
end. It should read as precise, sealed, cryogenic turbomachinery, not as a
furnace or boiler: no flame, no orange glow, no exhaust plume. Subtle wear and
grime. Painted semi-realistic industrial game art, strong readable silhouette,
transparent background, no text, no logos, no characters, no UI, no background
scenery.
```

---

## Directional Prompts

### North

```text
[Master prompt] Oriented vertically, long axis running from the top of the
frame to the bottom, rotor housing at the top end, pipe flanges at top and
bottom. Sprite proportions 3 tiles wide by 5 tiles tall.
```

### East

```text
[Master prompt] Oriented horizontally, long axis running from the left of the
frame to the right, rotor housing at the right end, pipe flanges at left and
right. Sprite proportions 5 tiles wide by 3 tiles tall. Same machine as the
vertical view, same size, same fittings, only the viewing direction changes.
```

### South

```text
Not required -- two_direction_only. Do not generate.
```

### West

```text
Not required -- two_direction_only. Do not generate.
```

---

## Layer Prompts

### Main Structure

```text
[Master prompt] Static structure only: casing, end housings, flanges, bolts,
pipework and frost. The rotor port is present but empty -- no blades. Nothing
that moves.
```

### Working Machinery

```text
Only a bladed turbine rotor disc on a transparent background, viewed at the
same 45-degree top-down angle, sized to sit inside a circular inspection port.
Eight frames showing the rotor at successive rotations of 45 degrees over one
eighth of a turn each, so the sequence loops seamlessly. Cool steel blades with
a faint cyan rim light. Nothing else in frame.
```

### Glow / Lighting

```text
A faint cold cyan rim-light glow shaped to a circular turbine inspection port,
on a fully transparent background, for additive blending. Plus a small amber
indicator lamp glow, separately placed. No other content.
```

### Effects

```text
Pale frost and condensation crystals on a transparent background, shaped to
gather along one end of a cylindrical machine casing. Cold blue-white, subtle,
no snow, no particles leaving the shape.
```

---

# 12. Image Processing

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

Two notes from the icon work already done in this repo, which apply here too and
have already cost time once each. Background-removal tools tend to return
**premultiplied alpha**, which Factorio renders dark and washed out — divide the
coverage back out (`tools/derive-fluid-icons.py` and `tools/key-icons.py` both
handle this). And generators that fake transparency with a painted checkerboard
need keying, not a straight alpha read; `tools/key-icons.py` does that.

---

# 13. Sprite Dimensions

Current sheets, which a replacement must match exactly or the prototype's
`width`/`height`/`shift` values in `prototypes/entity.lua` must be updated in
the same commit.

**Tile Size:**
`64 px` at `scale = 0.5` (sprites are authored at 2× and drawn at half size,
vanilla's convention)

**Building Width:**
`217 px` vertical frame / `320 px` horizontal frame

**Building Height:**
`374 px` vertical frame / `245 px` horizontal frame

**Sprite Width:**
`217` (V), `320` (H)

**Sprite Height:**
`374` (V), `245` (H)

**Spritesheet Width:**
`868` (V), `1280` (H)

**Spritesheet Height:**
`748` (V), `490` (H)

**Frame Count:**
`8`

**Line Length:**
`4` — an 8-frame sheet laid out as a 4×2 grid. Verified: both sheets divide
exactly into this grid.

Shadow sheets: `302×260` per frame (V, sheet `1208×520`) and `435×150` per frame
(H, sheet `1740×300`), same 4×2 grid.

Shifts currently applied, in tiles: V body `{0.148438, 0}`, V shadow
`{1.234375, 0.765625}`, H body `{0, -0.085938}`, H shadow `{0.890625, 0.5625}`.

---

# 14. File Structure

```text
graphics/
└── entity/
    └── quench-turbine/
        ├── quench-turbine-V.png            -- north, 8 frames, 4x2
        ├── quench-turbine-V-shadow.png     -- north shadow, 8 frames, 4x2
        ├── quench-turbine-H.png            -- east, 8 frames, 4x2
        └── quench-turbine-H-shadow.png     -- east shadow, 8 frames, 4x2
```

This is the layout already in the repo and already referenced by
`prototypes/entity.lua`. The template's generic north/east/south/west file list
does not apply — this building has two directions, and vanilla's `-V`/`-H`
suffix convention is what the existing prototype expects.

If the glow and status lamp are separated out as their own layers, add
`quench-turbine-V-glow.png` and `quench-turbine-H-glow.png` alongside.

---

# 15. Factorio Prototype

**Prototype Type:**
`generator`

**Prototype Name:**
`sae-quench-turbine`

### Graphics

The implemented block, in `prototypes/entity.lua`. A `generator` uses
`pictures`, not `graphics_set`.

```lua
pictures = {
  north = { animation = { layers = {
    { filename = ".../quench-turbine-V.png",
      width = 217, height = 374, frame_count = 8, line_length = 4,
      shift = { 0.148438, 0.0 }, run_mode = "backward", scale = 0.5 },
    { filename = ".../quench-turbine-V-shadow.png",
      width = 302, height = 260, repeat_count = 8, line_length = 1,
      draw_as_shadow = true, shift = { 1.234375, 0.765625 },
      run_mode = "backward", scale = 0.5 },
  } } },
  east = { animation = { layers = {
    { filename = ".../quench-turbine-H.png",
      width = 320, height = 245, frame_count = 8, line_length = 4,
      shift = { 0.0, -0.085938 }, run_mode = "backward", scale = 0.5 },
    { filename = ".../quench-turbine-H-shadow.png",
      width = 435, height = 150, repeat_count = 8, line_length = 1,
      draw_as_shadow = true, shift = { 0.890625, 0.5625 },
      run_mode = "backward", scale = 0.5 },
  } } },
},
```

### Other Visual Properties

```text
Animation:
8 frames, line_length 4, run_mode = "backward". Playback speed is driven by the
engine from actual output, so a partially loaded turbine visibly turns slower.

Shadow:
Separate layer, draw_as_shadow = true, repeat_count = 8 so one silhouette is
held across the body's 8 frames.

Working Visualisation:
None declared. A generator animates whenever it produces; there is no separate
working_visualisations block to maintain.

Lights:
None declared yet. The amber "no vapour" status lamp in §3.3 and §7 is a
proposal, not an implemented feature -- adding it means a new light layer.

Fluid Boxes:
One input box, volume 200, filter "sae-quench-vapour", minimum_temperature 100,
two input-output pipe connections at {0, -2} and {0, 2}.

Circuit Connections:
None. Not wired, by design.
```

---

# 16. Icon

**Icon Required:** ✓

**Icon Size:**
`64×64`, delivered as a `120×64` four-level mipmap strip (64/32/16/8 packed
left to right), matching every other icon in this mod and vanilla's own
convention. `icon_mipmaps = 4`.

**Icon Concept:**
The turbine seen three-quarter on, foreshortened so the rotor port is the
dominant element. At 16 px the read must be "a bladed disc in a teal machine" —
the barrel and pipework can dissolve entirely.

### Icon Prompt

```text
A Factorio-style item icon of a compact cryogenic turbine module, three-quarter
view, lit from the upper left: a bladed turbine rotor visible through a
circular housing opening, heavy pipework and flanges around it, painted in
cyan-teal accents over dark grey-green metal, with pale frost on the intake
side. It must read as a precision cryogenic turbine, cold and machined, not as
a furnace or boiler -- no flame, no orange glow. Object fills about 80% of a
square frame, centred, transparent background, soft drop shadow, no text, no
logos, no background scenery.
```

The icon should remain recognisable at Factorio's normal inventory/UI scale.

---

# 17. Visual QA Checklist

### Building

* [ ] Correct tile size (3×5 vertical, 5×3 horizontal)
* [ ] Correct perspective
* [ ] Correct scale
* [ ] Clear silhouette
* [ ] Looks like Factorio
* [ ] Reads as a space-platform machine, not a planet-surface one
* [ ] Both pipe ends are visually obvious as connection points
* [ ] No fuel hatch, hopper or inserter pad anywhere on the model

### Directions

* [ ] North (vertical)
* [ ] East (horizontal)
* [ ] ~~South~~ — not used, `two_direction_only`
* [ ] ~~West~~ — not used, `two_direction_only`
* [ ] Both directions represent the same building at the same size

### Animation

* [ ] Working animation is readable
* [ ] Animation loops correctly (frame 8 → frame 1 seamless)
* [ ] No parts change shape unexpectedly
* [ ] Only the rotor moves — casing, pipes, frost and flanges are pixel-identical across all 8 frames
* [ ] Rotor is visibly slower at partial load
* [ ] Effects align correctly

### In-Game

* [ ] Shadow aligns with building
* [ ] ~~Inserters align correctly~~ — n/a, no item interaction
* [ ] Pipes align correctly at both `{0, -2}` and `{0, 2}`
* [ ] Building doesn't overlap neighbouring entities incorrectly
* [ ] Recognisable in a row of three turbines beside a chemical plant
* [ ] Does not read as a vanilla steam turbine at a glance
* [ ] Performance is acceptable

---

# 18. Final Asset Checklist

```text
[ ] Master concept
[ ] North sprite (V, 8 frames, 4x2)
[ ] East sprite (H, 8 frames, 4x2)
[x] South sprite -- N/A, two_direction_only
[x] West sprite  -- N/A, two_direction_only

[ ] Shadow (V and H)
[ ] Idle pose (frame 1 of the working sheet)
[ ] Working animation
[ ] Working machinery layer (rotor only)
[ ] Lighting layer (status lamp)
[ ] Effects layer (frost)

[ ] Icon (120x64 mipmap strip)
[ ] Spritesheets
[x] Factorio prototype -- implemented and engine-verified
[ ] In-game test
```

---

# 19. Design Notes / Iteration History

### Version 1 — Thermionic Generator (abandoned)

A `reactor`-type entity with a scripted temperature/efficiency curve, two hidden
paired entities and a custom GUI, wearing vanilla's nuclear reactor sprites with
a magma-orange working glow. Abandoned because it could not survive vanilla's
heat network: a reactor's heat buffer feeds every consumer attached to it, so
heat exchangers and steam turbines would have converted its waste heat into
roughly as much electricity again, making its own output irrelevant.

### Version 2 — Quench Turbine, derived art (current)

Rebuilt as a plain `generator`, which reaches the same design goal with no heat
network, no hidden entities and no runtime script at all. The art is vanilla's
steam turbine recoloured by `tools/recolour-turbine.py`: a hue rotation of the
warm accent pixels to teal at their original lightness, so vanilla's shading
survives and only the colour changes. Teal was chosen because this is the cold
half of the mechanic, and because the source sprite is already brass and orange
— a warm tint changed almost nothing.

That recolour is good enough to play with. It is still vanilla's steam turbine
underneath, which is what this document exists to replace.

### Final — open questions before art is commissioned

**1. The naming is inconsistent, and this should be settled first.** The
building is the Quench Turbine, but the technology that unlocks it is
`sae-thermionic-power` ("Thermionic Power") and its crafting ingredient is the
`Thermionic Assembly` — both inherited from the abandoned reactor, and neither
now describes anything the building does. A thermionic device emits electrons
from a hot surface; this one expands a vapour through a rotor. Three ways out:

* **Rename the technology** to something like Quench Power or Vapour Power, and
  keep the building and the assembly as they are. Cheapest: one technology name,
  its locale strings and a migration entry. The Thermionic Assembly survives as
  a deliberately generic capstone item, which `design/vulcanus-fulgora.md` §8.5
  already says it is meant to be.
* **Rename the building** to Thermionic Turbine, making the whole branch
  consistent with the existing technology and assembly names. Touches the
  prototype name, the entity, item and recipe locale, the graphics directory,
  every doc reference and this file.
* **Leave it.** Defensible only if the Thermionic Assembly is read as the
  brand of the whole tree rather than a description of the mechanism.

Recommended: rename the technology. It is the smallest change, and it leaves
the two player-facing nouns — Quench Turbine and Quench Vapour — matching each
other, which is what a player actually reads while building.

**2. The status lamp does not exist yet.** §3.3, §7 and §18 specify an amber
"no vapour" indicator. Nothing in the prototype declares a light. Adding it is a
small prototype change but it must be decided before the art is drawn, because
the lamp needs a physical place on the casing.

**3. Nothing here has been playtested.** Every gameplay number in §2 is
engine-measured over RCON, but no human has yet built one of these in a client
and looked at it. The art should not be commissioned until someone has, in case
the footprint or the pipe placement turns out to be wrong in practice.
