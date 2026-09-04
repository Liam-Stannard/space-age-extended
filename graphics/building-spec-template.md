# Factorio Building — Art & Implementation Specification

## 1. Building Overview

**Building Name:**
`[Name]`

**Internal Prototype Name:**
`[prototype-name]`

**Building Type:**
`[assembling-machine / furnace / chemical-plant / reactor / custom entity / etc.]`

**Planet / Environment:**
`[Nauvis / Vulcanus / Fulgora / Gleba / Aquilo / custom]`

**Purpose:**
`[Short description of what the building does]`

**Technology Unlock:**
`[Technology that unlocks the building]`

---

## 2. Gameplay Dimensions

**Tile Size:**
`[e.g. 3×3 / 5×5 / 7×7]`

**Collision Box:**
`[x1, y1] → [x2, y2]`

**Selection Box:**
`[x1, y1] → [x2, y2]`

**Placement Restrictions:**
`[None / specific planet / specific terrain / etc.]`

**Rotation:**
`[4-way / 8-way / none]`

**Crafting Speed:**
`[value]`

**Energy Consumption:**
`[value]`

**Energy Type:**
`[electric / fluid / heat / etc.]`

---

# 3. Visual Design

## 3.1 Design Concept

**Primary Visual Theme:**
`[Heavy industry / advanced technology / alien / recycling / nuclear / etc.]`

**Overall Appearance:**
`[Describe the building's overall shape and construction]`

**Silhouette:**
`[What should make the building recognisable from a distance?]`

**Visual Complexity:**
`[Low / Medium / High]`

**Visual Age:**
`[Primitive / Industrial / Advanced / Experimental]`

---

## 3.2 Key Visual Features

The building should contain:

* `[Feature 1]`
* `[Feature 2]`
* `[Feature 3]`
* `[Feature 4]`
* `[Feature 5]`

### Signature Feature

`[The single visual feature that makes this building immediately recognisable.]`

---

## 3.3 Colour Palette

**Primary:**
`[colour / material]`

**Secondary:**
`[colour / material]`

**Metal:**
`[steel / copper / dark metal / etc.]`

**Accent:**
`[colour]`

**Working Glow:**
`[colour]`

**Warning / Status Lights:**
`[colour]`

---

# 4. Factorio Visual Style

The building should visually fit alongside the vanilla Factorio / Space Age graphics.

### Required characteristics

* [ ] 45° top-down Factorio perspective
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

### Style Reference Buildings

Use these Factorio buildings as visual references:

1. `[Building]`
2. `[Building]`
3. `[Building]`

**Reason for references:**
`[Explain what should be taken from each reference.]`

---

# 5. Building Orientation

## Required Directions

* [ ] North
* [ ] East
* [ ] South
* [ ] West

**Direction count:**
`[4 / 8]`

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

---

# 6. Sprite Assets Required

## 6.1 Main Building

| Asset         | Required | Frames | Directions |
| ------------- | -------: | -----: | ---------: |
| Main building |        ✓ |  `[x]` |    `[4/8]` |
| Shadow        |        ✓ |  `[x]` |    `[4/8]` |
| Idle state    |        ✓ |  `[x]` |    `[4/8]` |
| Working state |  `[✓/—]` |  `[x]` |    `[4/8]` |

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

**Animation FPS:**
`[value]`

**Animation Loop:**
`[Yes / No]`

---

# 7. Layer Structure

The building should be separated into layers wherever practical.

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
`[Description]`

**Base:**
`[Description]`

**Main Structure:**
`[Description]`

**Static Machinery:**
`[Description]`

**Working Machinery:**
`[Description]`

**Lighting:**
`[Description]`

**Effects:**
`[Description]`

---

# 8. Input / Output Visualisation

The physical locations of inputs and outputs must be defined before artwork is produced.

## Item Inputs

| Input    | Location      | Direction   |
| -------- | ------------- | ----------- |
| `[item]` | `[tile/side]` | `[N/E/S/W]` |
| `[item]` | `[tile/side]` | `[N/E/S/W]` |

## Item Outputs

| Output   | Location      | Direction   |
| -------- | ------------- | ----------- |
| `[item]` | `[tile/side]` | `[N/E/S/W]` |

## Fluid Inputs

| Fluid     | Location     | Connection Type     |
| --------- | ------------ | ------------------- |
| `[fluid]` | `[location]` | `[pipe connection]` |

## Fluid Outputs

| Fluid     | Location     | Connection Type     |
| --------- | ------------ | ------------------- |
| `[fluid]` | `[location]` | `[pipe connection]` |

### Visual Requirement

Input/output points should be visually obvious without making the building excessively cluttered.

---

# 9. Working Animation

## Animation Concept

`[Describe what physically happens when the building is operating.]`

### Sequence

1. `[Initial state]`
2. `[Machine begins operation]`
3. `[Major mechanical movement]`
4. `[Processing effect]`
5. `[Completion]`
6. `[Return to idle]`

**Frame Count:** `[x]`

**FPS:** `[x]`

**Loop Duration:** `[x] seconds`

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

`[Describe exactly what should be visible while operating.]`

---

# 11. DALL·E Generation Requirements

## Master Concept Prompt

```text
[Prompt goes here]
```

---

## Directional Prompts

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
[Prompt]
```

### Working Machinery

```text
[Prompt]
```

### Glow / Lighting

```text
[Prompt]
```

### Effects

```text
[Prompt]
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

---

# 13. Sprite Dimensions

**Tile Size:**
`[32 / 64 / other] px`

**Building Width:**
`[x] px`

**Building Height:**
`[x] px`

**Sprite Width:**
`[x] px`

**Sprite Height:**
`[x] px`

**Spritesheet Width:**
`[x] px`

**Spritesheet Height:**
`[x] px`

**Frame Count:**
`[x]`

**Line Length:**
`[x]`

---

# 14. File Structure

```text
graphics/
└── entity/
    └── [building-name]/
        ├── [building-name].png
        ├── [building-name]-shadow.png
        ├── [building-name]-idle.png
        ├── [building-name]-working.png
        ├── [building-name]-glow.png
        ├── [building-name]-north.png
        ├── [building-name]-east.png
        ├── [building-name]-south.png
        └── [building-name]-west.png
```

Additional animation assets should be added where required.

---

# 15. Factorio Prototype

**Prototype Type:**
`[assembling-machine / furnace / etc.]`

**Prototype Name:**
`[name]`

### Graphics

```lua
graphics_set = {
    -- Generated implementation goes here
}
```

### Other Visual Properties

```text
Animation:
[details]

Shadow:
[details]

Working Visualisation:
[details]

Lights:
[details]

Fluid Boxes:
[details]

Circuit Connections:
[details]
```

---

# 16. Icon

**Icon Required:** ✓

**Icon Size:**
`64×64`

**Icon Concept:**
`[Describe the simplified representation of the building.]`

### Icon Prompt

```text
[Prompt]
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

### Version 1

`[Notes]`

### Version 2

`[Changes made]`

### Final

`[Final design decisions]`
