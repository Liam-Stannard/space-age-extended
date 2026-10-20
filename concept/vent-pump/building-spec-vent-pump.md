# Factorio Building — Art & Implementation Specification

**Vent Pump.** Filled from `building-spec-template.md`. Every gameplay number here is the implemented value read off `prototypes/core/entities.lua` and the vanilla prototypes it deep-copies. The art sections describe the signed-off concept: the **Gas Lift Tower**, round 5, variant (a) "Warmer paints" (Liam, 2026-10-20). The shipping model is built from `concept/vent-pump/options/round-5/vpb5_08_gas_lift_tower.py --variant a`.

**The central art decision — see §3.1.** A pumpjack is a beam pump. The Vent Pump is a **gas lift**: helium-3 is blown into the melt at the foot of a tower, and its bubbles carry the melt up. The building shows that happen, in glass.

---

**Amended 2026-10-09 (Liam): melt only.** Helium-3 is now drawn by the Gas
Pump (`concept/crust-tap/building-spec-crust-tap.md`, §A), with every other gas.
The Vent Pump keeps the melt vent and nothing else: its `resource_categories`
stays `{ "sae-vent" }`, which now holds only `sae-melt-vent`, while the gas vents
move to `sae-gas`. Its input fluid box, the helium it burns to draw melt, and
everything else in this spec are unchanged. Where it says the Vent Pump draws
helium or stands on a gas vent, read the Gas Pump.

**Amended 2026-10-20 (Liam): the Gas Lift Tower.** Round 1's model and the ChatGPT plates are set aside. From twenty ideas Liam picked eight (round 2), then "Gas lift tower - now we can review the textures" (round 4), then "(a) Warmer paints" (round 5). His other rulings:
- "The pump should include no frost/cold as part of the model, this would be from animations/effects."
- The helium seen in glass, mix "A: violet, pink pulse per stroke". The helium glow is allowed beside the melt's orange.
- Clipping: "Fix both in the model" (melt crest `#F89A50`, satin bare steel), then "Accept, add to the shared rig" for the highlight roll-off (§11).
- Rise: "Accept 0.77" — the bar for this building is the foundry's 0.78, not the pumpjack's 0.47.
- South join: "Fix in the model" — widen the south helium nozzle or carry the footing under it, so measure.py's join gate passes.
- Strobe 0.27–0.29 % on the moving parts: noted, not raised.
- Lamps: "Two lenses, two states": one green while working, one amber when the input fluid is missing.
- Boil-off wisp: "Put it on the tower"; "Artist proposes spot": two or three spots shown at the model stage, only while working.
- Effects: "Add effects"; "Artist proposes": options shown at the model stage, Liam picks.
- Loop speed: "Model stage proposes": the artist proposes it from the 1x GIF, Liam picks at model sign-off.

**What the model must keep** (round 5, variant (a), measure.py):

| Measure | Round 5 (a) | Bar |
| --- | --- | --- |
| Footprint coverage | 95.9 % | ≥ 92 % |
| Rise above the north edge | 0.77 tiles | ≤ 0.78 (foundry) |
| Tonal, plate / still | p50 79 / 77, p95 170 / 169 | p50 ~75–81, p95 in vanilla's range |
| White and clipped px, whole frame | 0 | 0 |
| Helium glow peak, 1x | 122 | 87–171 |
| Pale cyan and frost px | 0 | 0 |
| Strobe | 0.29 % | noted |
| North join | pass | pass |
| South join | fail: 7 of 39 columns, up to 6 px | pass |

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
{ "sae-vent" }`). No `surface_conditions` — see §1. `fast_replaceable_group`
and `next_upgrade` are both cleared, so it never fast-replaces a pumpjack and
never offers an upgrade path.

**Rotation:**
`4-way.` One helium-3 input on the south face and one molten kamacite output on the north face, both on the centre tile, turning with the building as a pair. See §5 and §8.

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

**Primary Visual Theme:** **A gas-lift tower.** A tall, narrow iron shaft over the vent with a glass riser down its south face, a head tank on top, and the plant that serves it packed round its foot. Not a beam pump. It glows with the melt it carries, the helium in its sight glass, and its two status lenses, and nothing else.

**Overall Appearance:** The tower stands over the vent on a refractory footing, just north of centre. Its kit fills the rest of the footprint, each unit on its own footing, with no deck: the helium inlet, stop valve, flow meter and sight glass (south); the recovery compressor (south-east); the recovery receiver (south-west); the switchgear (east); the control house (north-east); the lagged downcomer and the skimmings bin (north-west); two gas bottles and a tool chest (west); a ladder up the tower's west side.

**Silhouette:** The head tank rises above the north edge; the units break each corner at different heights (FFF #350). From altitude the read is *"a glass tower full of melt, fed from below"*.

**Visual Complexity:** `Medium-high.` Clutter and hoses after vanilla, readable at 1x.

**Visual Age:** `Advanced, and used.` Paint per unit, worn paint, rust only where it forms, in vanilla's warmth and saturation (the Reaction Plant model's finish).

---

## 3.2 Key Visual Features

The building should contain:

* The **tower shaft**, iron, banded every 0.42 of its height, with a slot down its south face.
* The **glass riser** in that slot: orange melt with helium bubbles climbing it.
* The **head tank** on the tower top, where the helium breaks out of the melt, with a melt window and a **float chamber** whose lever rocks.
* The **helium line**: in at the south nozzle, through the stop valve and the turning **flow meter**, past a tee and a gauge, through the **sight glass**, down to the **sparger ring** round the tower's foot. Bare steel at the intake; the line lagged grey-violet with ID bands.
* The **recovery loop**: down the tower's east side to the **compressor** (its coupling turning), west over the inlet to the **receiver**, back into the line at the tee.
* The **lagged downcomer** carrying the melt from the head tank down to the north nozzle.

### Signature Feature

**The helium seen at work.** Violet helium in its sight glass drops and flushes pink at each charge, and its bubbles carry the orange melt up the glass riser. The player watches the scarce vent pay for the rich one.

---

## 3.3 Colour Palette

Variant (a), "Warmer paints" (`vpb5_kit.py`). A paint or metal per unit.

**Iron:** the tower `#6A5642`; the head tank `#523F33`.

**Unit paints:** oxide red `#963220` (compressor, skimmings bin); ochre `#BC8624` (ladder, a gas bottle); green `#5C7A2C` (meter transmitter, compressor motor, a gas bottle); cream `#C0A676` (control house); grey `#86704C` (receiver, injection controller, switchgear).

**Metal:** bare steel and nickel bands, satin, so no glint reaches white. The brightest paints are a step down (`CAPS` in `vpb5_kit.py`).

**Helium line:** grey-violet lagging, ID bands `#84769A`. No frost, rime, ice or cold colour anywhere in the model.

**Molten kamacite:** `#D96B29` → crest `#F89A50`, only where melt is seen: the glass riser and the head-tank window.

**Helium glow:** mix A, violet with a peach-pink flush at each charge, in the sight glass only, while working only. Peak 122 at 1x.

**Status lenses:** two, lit, drawn as lights: the control house's (north-east) green while working; the switchgear's (east) amber when the input fluid is missing (Liam, "Two lenses, two states", "House green, gear amber", "Light").

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

**The camera is the shared rig's** (`tools/blender/`), not a prompt.

### Style Reference Buildings

1. `Pumpjack` (base) — the same 3×3 over a fluid resource; the comparison on every sheet.
2. `Chemical plant` (base) — a 3×3 built up in height, clutter and pipes.
3. `Foundry` (Space Age) — molten metal seen in the building, and the rise bar (0.78).

The cryogenic plant is no longer a reference: no frost is modelled.

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

**How the four directions differ.** The whole machine is turned a quarter turn under the one fixed camera, as round 5's sheets show it. The fluid boxes turn with it, so helium enters the face opposite the melt's outlet in every direction. Each direction is its own render.

---

# 6. Sprite Assets Required

## 6.1 Main Building

Four directions, each a whole render (§5). Layers as `tools/blender/render.sh --ports --icon` packs them: the plate, its shadow, the working loop, the glow, the pipe pictures and the icon.

---

## 6.2 Animation Layers

**What moves, in a 24-frame loop with two helium charges a loop:**
* bubbles climbing the glass riser, faster in each charge;
* the melt flowing in the riser and the head-tank window;
* the sight glass: the level drops and flushes pink at each charge, then refills;
* the flow meter turning, racing in each charge;
* the line gauge swinging with each charge;
* the float lever rocking, once a charge;
* the compressor's coupling turning;
* the receiver's gauge swinging.

Idle: everything still, no glow. Moving share 2.67 %; strobe 0.29 %, noted (Liam).

**The lift itself has no moving parts.** The motion is the helium's kit doing its job. Nothing nods or strokes.

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

**Shadow:** from the model, cast down-right; fixed, as the Core has `day-night-cycle = 0`.

**Structure:** one model; no base plate. Four directions.

**Working:** the 24-frame loop (§6.2), four directions.

**Glow:** two lights, kept apart: the melt's orange in the riser and the head-tank window, and the helium's violet-to-pink in the sight glass, working only.

**Lighting:** the two status lenses, drawn as lights (never rolled off): the control house's green while working, the switchgear's amber when the input fluid is missing. What the engine can trigger the amber from is checked by a spike at the model stage; if it cannot, back to Liam ("Check engine first").

**Effects:** any cold shown comes from effects, never the model (Liam). A boil-off wisp on the tower, only while working; the artist shows two or three spots, and its look, at the model stage and Liam picks. Other effects as §10.

---

# 8. Input / Output Visualisation

**Both fluid boxes are declared by this mod, not inherited.** What the pumpjack
and the mining drill hand down is unusable, and §18 records why.

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

* The **intake** (south) is bare steel and turns at once into the grey-violet helium line, through valve and meter.
* The **outlet** (north) is the end of the lagged downcomer, fed from the head tank high on the tower.
* They sit on **opposite faces**, and the two colours (violet, orange) are a second cue.

Each face's flange stands at the edge on assembler 3's pipe axis (z 0.42). The pipe pictures are the model's own, in assembler 3's outline, in its own metal; the pipe covers are vanilla's. Every join passes measure.py's no-gap rule; the south nozzle is fixed in the model (Liam, "Fix in the model").

---

# 9. Working Animation

## Animation Concept

Two helium charges a loop. Each charge is let in, and the melt answers: bubbles climb faster, the level in the head tank lifts.

### Sequence

1. Idle: everything still, no glow.
2. Charge: the meter races, the line gauge swings, the sight glass drops and flushes pink.
3. The bubbles in the riser climb faster; the float lever rocks.
4. Between charges: the glass refills and fades back to violet; the bubbles slow but keep climbing.
5. The second charge, the same; the loop repeats.
6. On stop, the engine's own fade back to (1).

**Frame Count:** `24`

**FPS / Loop Duration:** proposed at the model stage from the 1x GIF; Liam picks at model sign-off.

The loop is seamless: its wrap is within the frame-to-frame steps (measure.py).

---

# 10. Effects

## Working Effects

* [x] Glow (melt, helium glass, status lenses)
* [x] Moving fluids
* [x] Other: a boil-off wisp on the tower, only while working

### Effect Description

While working: the melt moves in the riser and the head-tank window; the helium glass drops and flushes at each charge; a boil-off wisp lifts from the tower.

**The effects are proposed at the model stage.** The artist shows the wisp at two or three spots, each with its proposed look, and effect options beside it; nothing is ruled out (Liam, "Nothing ruled out"). Liam picks.

---

# 11. Image Processing

The model goes through `tools/blender/render.sh --ports --icon` on the GPU; every layer is packed by `pack.py`. The highlight roll-off is on by default (knee 236, top 244) and never on light passes. `--collide` over every frame: 0 clashes.

---

# 12. Sprite Dimensions — measured

**These are the ChatGPT plates now in `graphics/`.** The model's own sizes and shifts replace them at wiring, measured off the packed sheets.

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

# 13. File Structure

Set at wiring by what `pack.py` writes into `graphics/entity/vent-pump/`. The model, its script and its renders live in `concept/vent-pump/model/`.

---

# 14. Factorio Prototype

**Prototype Type:**
`mining-drill`

**Prototype Name:**
`sae-vent-pump`

### Graphics

The graphics are written at wiring, against `pack.py`'s sheets; `prototypes/core/entities.lua` is the record until then.

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
Two status lenses, drawn as lights: the control house's green while working, the switchgear's amber when the input fluid is missing (its trigger checked at the model stage).

Fluid Boxes:
input_fluid_box  — helium-3, volume 200, one connection at [0,1] facing south.
output_fluid_box — molten kamacite, volume 1000, one connection at [0,-1] facing north.
Both turn with the entity.

Circuit Connections:
Inherited from the pumpjack (circuit_connector_definitions["pumpjack"]). The
connector sprite sits on the base plate and must not be occluded by the new
tower — check this before the art is signed off.
```

---

# 15. Icon

**Icon Required:** ✓ · **Icon Size:** `64×64`

**To be redone from the model** (`render.sh --icon`). The current icon is cut from the ChatGPT north plate.

---

# 16. Visual QA Checklist

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

* [ ] No frost, rime or cold colour in the model
* [ ] The helium violet and the melt orange read apart
* [ ] The outlet cannot be mistaken for the intake
* [ ] Both pipe joins pass measure.py's no-gap rule
* [ ] The circuit connector is not occluded by the tower
* [ ] The control house's green lens lights only while working; the switchgear's amber only when the input fluid is missing
* [ ] The boil-off wisp shows only while working
* [ ] It does not read as a pumpjack, the generator or the Reaction Plant

---

# 17. Final Asset Checklist

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

# 18. Design Notes / Iteration History

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


### 2026-10-20 — the Gas Lift Tower signed off

Round 1's Blender model read as a square deck with a small stack and was set aside. Rounds 2–5 (`concept/vent-pump/options/`): twenty ideas, eight picked; the helium seen at work and every pipe going somewhere (round 3); the helium in glass, mix A (round 4); the Gas Lift Tower in three surfacings (round 5). Liam signed off variant (a) on 2026-10-20 (see the amendment at the top). The ChatGPT prompts (the old §11, and the icon prompt in the old §16) were deleted the same day, and §12–§19 renumbered.

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
  anything resting on a surface. Both come off in processing (§11), but if the
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

**Superseded 2026-10-20** by the Gas Lift Tower; the plates below `concept/v2-sheet.png` describe the art now in `graphics/`.

The concept sheet is approved and the design is locked. What remains is the
production pipeline of template Appendix C — canonical plate, idle plate, the
four directional frames derived from it, glow by differencing, then the sprite
canvas. **Stop prompting for the design now**: every later image is an edit of
`concept/v2-sheet.png`, never a fresh generation.
