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
| 1 | Master concept | `[portrait 2:3 / square]` | Silhouette approved against §3.1 and §17 |
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

* [ ] Factorio top-down perspective — **see the camera note below**
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

**Rule — never write "45°" or "isometric" in a prompt.** Both produce a
different game. Factorio's camera sits roughly 60° above the horizon and is
effectively orthographic, and prompts must describe that the long way round:

* **A flat building** (under ~2 tiles tall) shows mostly its roof, a shallow
  slice of its near face, and no far face at all.
* **A tall building** is drawn leaning toward the viewer so its *sides* show —
  the same cheat vanilla uses for the lightning collector, the big electric
  pole and the rocket silo. Its **base** is still seen from above: the top
  faces of its base plates are visible. Say both halves, or the generator
  returns a flat side-on elevation.

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

**Rule — do not ask a generator for animation frames.** Ask for stills shaped
to the geometry, and derive frames from them in processing. A generator asked
for "32 frames" returns one image, or 32 unrelated ones.

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

### Effects this building must never show, and why

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
        ├── [building-name].png
        ├── [building-name]-shadow.png
        └── [additional assets as §6 requires]
```

**Fill rule:** list only files this building actually needs. The template's
four directional filenames are not a requirement.

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

* [ ] Engine-drawn effects land where the art says they should
* [ ] Shadow aligns and does not double
* [ ] Inserters and pipes align correctly
* [ ] Doesn't overlap neighbours incorrectly
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
2. **Camera.** Described, never named as an angle — see §4. Both halves for a
   tall building: base from above, upper structure leaning toward the viewer.
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
* **Expect transparency to be ignored.** Ask anyway, then key.
* Save concepts to `graphics/entity/<building>/concept/<tag>-<slug>.png` by
  hand, matching the names `tools/generate-building-art.py` would have used, so
  both routes leave the same trail.
