# Factorio Building — Art & Implementation Specification

**Bed Tender.** Began as a brief and was filled out into a specification once its
concept sheet was approved and §8's connection review was done. Every gameplay
number is read off `prototypes/core/entities.lua` and the vanilla
`agricultural-tower` it deep-copies.

**Only the hub is in scope.** The crane is a separate prototype — §6 — and until
it is authored this building ships as a custom hub under an inherited arm.

Written after the fact: a concept sheet (`concept/v1-sheet.png`) was
commissioned for this building before any document existed for it, which is the
one thing the template's process rule forbids. This brief records the design
that sheet established, plus the two engine facts the sheet got wrong because
nobody had written them down.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **passed — `concept/v2-sheet.png`** |
| 1 | Canonical view | square | Silhouette approved against §3 | **passed — `concept/v4-hub.png`** |
| 2 | Idle plate (unlit) | square | Same machine, nothing lit | **passed — the same plate; this building has no lit state, so stages 1 and 2 are one asset** |
| 3 | Directional frames | — | **n/a — no rotation, see §5** | n/a |
| 4 | Crane asset | — | **Its own prototype, see §6** | separate |
| 6 | Icon | square | Legible at 32 px | **passed — `graphics/icons/bed-tender.png`, derived from the plate** |

### Where generation happens

Browser — ChatGPT's image tool. Template Appendices B and C apply in full.

### Round log

See §19.

---

# 1. Building Overview

**Building Name:** `Bed Tender`
**Internal Prototype Name:** `sae-bed-tender`

**Building Type:** `agricultural-tower`, deep-copied from Space Age's. The
vanilla tower needs pressure 1000–2000 and is refused on the Core, so without
this the whisker beds would be hand-worked forever.

**Purpose:** Plants seed plates on whisker beds and harvests whatever has
finished growing. It is the machine that turns the Core's farm from a chore into
a factory.

**Locale:** *"Sows and reaps, in a place where nothing was ever supposed to
grow."* / *"Works only where the air is thin enough that nothing else does."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 3×3 (`collision_box {-1.2,-1.2},{1.2,1.2}`, inherited) |
| Planting radius | 3 tiles (inherited `radius`) |
| Directions | 1 — `agricultural-tower` has no rotation |
| Input inventory | 3 slots |
| Crane energy | 100 kW while working |
| Recipe | 20 kamacite plate, plus the rest of the inherited chain |

---

# 3. Visual Design

## 3.1 Design Concept

Cold precision agriculture, in metal. A vanilla agricultural tower is a
*greenhouse-adjacent* machine — it belongs to a world with air, weather and
soil. This one works in near-vacuum on a metallic crust, so nothing about it
should suggest growing conditions: no glass, no misting, no green.

The design is a **slewing gantry on an armoured hub**: an octagonal drum that
sits in the 3×3, a slewing ring on top of it, and a long counterweighted arm
that reaches out over the beds. The arm is the whole read — it is what says
"this machine tends ground it is not standing on".

**The anti-read:** it must not look like it grows anything itself. No planter
boxes on the building, no glass, no green foliage, no water. What it holds is a
magazine of *seed plates* and a bin of *harvested crystal*, and both are
obviously metal.

## 3.2 Key Visual Features

* An **armoured octagonal hub** filling the 3×3, low and heavy.
* A **slewing ring** on top — a visible toothed bearing race the arm turns on.
* A **long counterweighted gantry arm** reaching well past the hub, with a
  gripper tool head hanging from its outer end.
* A **seed plate magazine** on one flank: a stepped rack of thin plates, edge
  on, clearly a stack of stock waiting to be planted.
* A **collection bin** on the opposite flank, open-topped, with harvested
  silver-white crystal visible in it.

### Signature Feature

The slewing ring plus arm. At 3×3 the hub alone would read as any other drum;
the arm sweeping past the footprint is what makes it legible in one glance.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Hub and arm body | `#4A463F` → `#6E685C` | the mass of the building |
| Slewing ring, bolt rings | `#B9B4A8` | bearing race, joints |
| Hazard/marker banding | `#7A6A41` | arm edges, gripper head |
| Harvested crystal | `#D6DAE0` → `#FFFFFF` | collection bin only |
| Bed ground | `#5A5248` | ground panels, magazine plates |

No green anywhere, and no glow — this machine has no lit state.

---

# 4. Factorio Visual Style

The flat camera case for the hub, but the arm has real height and reach, so the
plate is wider than the footprint. Name the camera exactly and do not add the
tall building's leaning clause.

---

# 5. Building Orientation

* [x] North
* [ ] East · South · West

**Direction count:** `1`. `agricultural-tower` has no direction and cannot be
rotated. **The v1 sheet drew NORTH / EAST / SOUTH / WEST panels and that is
wrong** — it produced four camera angles of an unrotatable building, which is
the turntable failure the Vent Pump spec §5 warns about. What varies is not
direction but **arm sweep position**, and that belongs in the animation row.

---

# 6. Sprite Assets Required

**The crane is a separate prototype, and this is the scoping fact that was
missing.** `agricultural-tower` carries a `crane` field pointing at
`__space-age__/prototypes/entity/agricultural-tower-crane`, which defines the
arm, its joints, its grip and their animations as a structure in its own right —
it is not part of `graphics_set` and cannot be replaced by editing the building
plate.

So the work splits in two, and only the first half is a normal building plate:

| Asset | Plan |
| ----- | ---- |
| Hub, slewing ring, magazine, bin, shadow | **Replace** — one plate, one direction, by the normal §12 pipeline. |
| The crane (arm, joints, grip, its animations) | **Separate asset with its own pass.** Ship the hub first. |

Until the crane is authored it stays inherited, which means a vanilla arm on a
custom hub — visibly mismatched, but functional and honest as an intermediate
state.

---

---

# 8. Connections

**What the engine will draw whatever the art does.** Vanilla never butts a
generic pipe or effect against a flat wall — the connector is modelled into the
building's own plate and the engine only reveals it. The foundry is the
reference: `pipe_picture = util.empty_sprite()`, `always_draw_covers = false`,
and `enable_working_visualisations = { "input-pipe" }`, so the flange lives in
the building's graphics set at exactly the tile the fluid box names.

| Connection | Where | Inherited from |
| ---------- | ----- | -------------- |
| Crane pivot | `{0.5, -0.55, 4.6}` | `agricultural-tower-crane.origin` |
| Items in / out | any adjacent tile | inserters, unconstrained |
| Planting reach | radius 3, beyond the 3×3 footprint | `agricultural-tower.radius` |
| Fluids | none | — |

**The crane pivot is not the centre of the building.** `origin` is half a tile
east, just over half a tile north, and **4.6 units up** — so while the crane
stays inherited (§6 says it must, until it is authored), the arm swings from a
point the concept sheet has no bearing at. `concept/v2-sheet.png` puts the
slewing ring dead centre on the hub.

**Resolved in the prototype, not the art.** `prototypes/core/entities.lua` now
sets `tender.crane.origin = { 0, 0, 4.6 }`, moving the pivot to the middle of the
building where the sheet draws the bearing. The height is unchanged.

The alternative was drawing the ring half a tile off-centre to chase vanilla's
asymmetry, which would have made every later plate carry an offset that exists
for no reason of ours. Vanilla's tower is not symmetrical; this one is.

Safe against reach: the crane's extendable segments run to 4.5 and 4.0 against a
planting radius of 3, so half a tile of recentring is well inside what the arm
already covers. Worth confirming in a client when the hub plate lands — a
visibly short arm at the edge of the radius would be the symptom.

Item routing is unconstrained, so the seed magazine and collection bin of §3.2
are honest decoration in the same way a vanilla furnace's are.

# 11. Generation Requirements

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio Space
Age building, titled BED TENDER, every panel drawn from the game's
characteristic 45-degree top-down perspective, laid out as labelled panels on a
dark charcoal background, in the style of a game art bible page.

Panels: a large hero view labelled CANONICAL; a second large view labelled ARM
EXTENDED showing the same machine with its gantry arm reached out over the
ground; an in-game icon panel showing it simplified to a 64x64 item icon; a
tile-grid panel showing it from directly overhead on a 3x3 tile grid with a
dashed circle marking the arm's three-tile reach beyond the footprint; three
close-up detail panels showing the seed plate magazine, the gripper tool head,
and the collection bin with harvested crystal in it; a layer breakdown row
showing shadow, hub, slewing ring, arm and crystal separated; a row of five
animation key frames showing one work cycle — idle, sweep out, position, plant a
seed plate, lift a harvest; and a palette strip of eight swatches.

Do not draw north, east, south and west panels: this building cannot be rotated
in game, and the only thing that varies between frames is where the arm is
pointing.

The building in every panel is the same machine: a low armoured octagonal hub
filling a three by three tile footprint, with a visible toothed slewing bearing
ring on top of it. A long counterweighted gantry arm turns on that ring and
reaches well past the hub, with a gripper tool head hanging from its outer end.
A stepped rack of thin seed plates, stacked edge on, sits on one flank; an
open-topped collection bin with silver-white crystal spikes in it sits on the
opposite flank.

Dark iron-nickel grey-brown metal, #4A463F to #6E685C, pale nickel-white
#B9B4A8 slewing ring and bolt rings, dull ochre #7A6A41 banding on the arm and
gripper, silver-white #D6DAE0 to #FFFFFF crystal in the collection bin only, and
brown-grey #5A5248 for the bed ground and the stacked plates.

It must read as a machine that tends ground it is not standing on, and it must
not read as something that grows anything itself: no glass, no greenhouse
panels, no green foliage, no water, no mist, no planter boxes on the building.
Nothing on this machine is lit or glowing. Panel labels and small caption text
are wanted, but no brand logos or wordmarks of any kind. Painted semi-realistic
industrial game art. No characters, no photorealism.
```

---

---

# 7. Layer Structure

Only the hub is in scope; the crane is a separate prototype and §6 says why.

| # | Layer | Draw as | Animated | Notes |
| - | ----- | ------- | -------: | ----- |
| 1 | Shadow | `draw_as_shadow = true` | no | Derived. Hub only — the arm casts its own. |
| 2 | Hub | `graphics_set.animation` | no | Deck, octagonal drum, slewing bearing ring, seed magazine, collection bin. |
| 3 | Bin contents | `working_visualisations` | no | The silver crystal in the collection bin, so a full bin differs from an empty one. |

### Layer Notes

**Nothing on this building glows**, so there is no additive layer and no
`derive-glow.py` step. It is the only building in the mod with no lit state,
which makes it the cheapest plate to cut and a sensible one to do early.

**The slewing ring must be drawn as a real bearing race** — a toothed ring with
its own depth and shadow — because the inherited crane arm is drawn on top of it
by a separate prototype and the join has to survive that. See §8: the pivot is
now centred to sit on this ring.

---

# 12. Image Processing

### Processing Checklist

1. `--report` before judging.
2. `--dekey` if needed.
3. Cut the hub plate to the §13 canvas.
4. Derive the shadow.
5. No glow step.

**Check the plate against the inherited arm before calling it done.** Cut the
hub, wire it, and look at it in a client with the crane moving. The arm is not
ours yet, and the only way to know the bearing lines up is to watch it turn.

---

# 13. Sprite Dimensions

**Measured off `concept/v4-hub.png` after cutting.** The numbers below are what
the shipped plates actually are, not what was intended.

**Tile Size:** `32` px in-game · **Scale:** `0.5` → `64` source px per tile

| | Canvas | Visible content | Shift |
| --- | --- | --- | --- |
| `base.png` | 224 × 189 | 192 × 161 px at rows 16–177, centred | `{ 0, 0.21094 }` — `by_pixel(0, 6.75)` |
| `base-shadow.png` | 363 × 189 | 241 × 49 px | `{ 1.08594, 0.21094 }` |
| `bin.png` | 224 × 189 | 41 × 57 px, over the bin opening | `{ 0, 0.21094 }` |

All three share the colour plate's canvas origin, so registration is exact by
construction rather than by alignment.

**Why the shift is positive.** A tall building's art reaches up and takes a
negative shift; this one is low and is nearly all footprint, so its plate hangs
slightly *below* the origin. `by_pixel(0, 6.75)` puts the front skirt on the
footprint's near edge at +1.5 tiles. Vanilla anchors its own low plates the same
way — `assembling-machine-1-base` is `by_pixel(0, 4)`.

**The camera, which is the thing that nearly shipped wrong.** See §19 round 3.
The measurable test: a vanilla 3×3 building's plate is close to square —
`assembling-machine-1-base.png` measures 188 × 180 px, **aspect 1 : 0.96**. The
first plate came back at 1 : 0.61, a pancake, and no amount of looking at it in
a viewer said so. The shipped plate is 1 : 0.84.

**Verified before wiring**, by the four measurements in the template's Appendix C:
centred to 0.0 px; alpha zero along all four edges; visible span **3.000 tiles**
exactly; peak alpha 255 on the colour plate and 155 on the shadow. Three tenders
rendered at a 3-tile pitch overlap by **90 px at alpha > 1 and 0 px above alpha
80** — two antialiased edges meeting, which is the signature of a correct fit.

**Footprint:** 3×3 tiles. `collision_box` `{{-1.2,-1.2},{1.2,1.2}}`,
`selection_box` `{{-1.5,-1.5},{1.5,1.5}}`, inherited.

**Width, load-bearing:** the hub must span **exactly 3.00 tiles** — `192` source
px at scale 0.5. **It does: measured 192 px.**

**The bearing centre is the second load-bearing number.** With `crane.origin` now
`{0, 0, 4.6}` the arm pivots on the plate's centre, so the ring's centre must
land exactly there. The plate's content is centred on the canvas to 0.0 px and
the ring is drawn centred in it, so this holds by construction — but it is a
claim about *drawn* geometry, not canvas geometry, and only a client with the
arm turning can settle it. Still open.

**`drawing_box_vertical_extension = 2.5`** is inherited and must stay: the arm
reaches well above the hub, and without the extension the engine culls it.

**Shift:** anchor on the deck.

---

# 14. File Structure

```
graphics/entity/bed-tender/
    base.png      colour plate, hub only
    shadow.png    derived
    bin.png       collection bin contents, working visualisation
    concept/      v1-sheet.png, v2-sheet.png
graphics/icons/
    bed-tender.png   64 px mipmap strip, derived from base.png
```

No crane files. When the crane is authored it gets its own directory and its own
section, because it is its own prototype.

---

# 15. Factorio Prototype

### Graphics

```lua
local ART = "__space-age-extended__/graphics/entity/bed-tender/"
tender.graphics_set.animation =
{
  layers = { <base.png>, <shadow.png draw_as_shadow> }
}
tender.graphics_set.working_visualisations = { <bin.png> }
tender.graphics_set.water_reflection = nil
```

`tender.crane` stays inherited apart from the recentred `origin` already set in
`prototypes/core/entities.lua`.

### Other Visual Properties

`circuit_connector = circuit_connector_definitions["agricultural-tower"]` is
inherited and places a small wire-connection sprite at an offset chosen for
vanilla's asymmetric tower. **Check where it lands on the symmetric hub** when
the plate is wired; if it sits somewhere silly, the definition can be swapped for
another entry in `circuit_connector_definitions` rather than redrawn.

`radius_visualisation_picture` stays vanilla's — it is a placement overlay, not
part of the building.

---

# 17. Visual QA Checklist

### Building

- [ ] Reads as a machine that tends ground it is not standing on — **cannot be
      judged until the crane is authored; the hub alone does not carry it**
- [x] Nothing suggests it grows anything itself — no glass, no green, no water
- [x] Slewing ring reads as a real bearing race, with depth
- [x] Seed magazine and collection bin are distinguishable at a glance
- [x] Nothing on the building is lit
- [x] Body metal luminance inside the §3.3 range, **measured** — `#5E554C`, 86

### Connections

- [x] Bearing ring centre lands on `{0, 0}`, checked on the cut plate — content
      centred to 0.0 px, ring drawn centred within it
- [ ] The inherited arm turns on the drawn ring — **verified in a client, moving**
- [ ] Circuit connector sprite lands somewhere sensible on the hub

### In-Game

- [x] Two tenders side by side touch and do not overlap — measured at a 3-tile
      pitch: 90 px overlapping at alpha > 1, **0 px above alpha 80**
- [ ] Sits on its footprint
- [ ] Arm is not culled at full extension — `drawing_box_vertical_extension` intact
- [ ] Hub and inherited arm do not read as two different art styles glued together
      (they will, somewhat; the question is whether it is tolerable until the
      crane is authored)

---

# 18. Final Asset Checklist

- [x] `base.png` cut and measured — 224 × 189, content 192 × 161
- [x] `base-shadow.png` derived — 363 × 189 (the file is `base-shadow.png`, not
      `shadow.png`; §14 predates the tool's naming)
- [x] `bin.png` working visualisation
- [x] Icon derived from the plate — no collision at 16 px against the 32 icons
      already locked (closest 30.4, against the set's own floor of 30.2)
- [x] §13 filled in with **measured** numbers; bearing centre still open on the
      one part only a client can answer
- [x] Prototype wired
- [x] `./tools/check-data-stage.sh` passes
- [ ] Verified in a client with the crane actually working

# 19. Design Notes / Iteration History

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| 1 | sheet | Commissioned before this document existed. The design itself is good and is what §3 now records: armoured octagonal hub, slewing ring, counterweighted arm, seed plate magazine, gripper head, crystal collection bin, and a five-frame work cycle. Palette is right and nothing glows. **Two engine facts were wrong because nobody had written them down**: it drew NORTH / EAST / SOUTH / WEST panels for a building that cannot be rotated, and it treated the arm as part of the building plate when the crane is a separate prototype (§6). | **Design accepted; sheet structure rejected** | Replace the direction panels with CANONICAL and ARM EXTENDED, add the reach circle to the tile-grid panel, and keep the arm as its own layer in the breakdown. |
| 2 | sheet | Both structural fixes landed. The direction panels are gone, replaced by CANONICAL and ARM EXTENDED — the same unrotatable machine with the arm at rest and reached out. The tile-grid panel now carries the dashed three-tile reach circle around the 3×3 footprint. **The arm appears as its own layer in the breakdown**, separate from the hub, which is what §6 needs given the crane is its own prototype. Five-frame work cycle reads correctly: idle, sweep out, position, plant, lift. Nothing glows, nothing is green, no glass anywhere. | **Accepted — `concept/v2-sheet.png` is the locked design** | None. |
| 3 | plate | The approved CANONICAL panel was cropped out of `v2-sheet.png`, attached, and the arm asked away so the slewing ring could be drawn complete underneath. The arm came off cleanly and the ring came back whole. **The camera was wrong and nothing about looking at it said so**: measured, the machine came back 3.00 tiles wide by 1.84 deep, aspect **1 : 0.61**, a pancake. A vanilla 3×3 plate — `assembling-machine-1-base.png`, 188 × 180 px — is **1 : 0.96**. The report passed it: transparency ok, palette in range, body metal luminance 83. Palette and alpha checks cannot see projection. | **Rejected on camera; design accepted** | Regenerate rather than edit — an edit preserves the silhouette being rejected — with a real vanilla 3×3 sprite attached as a camera reference under the usual "do not copy the design" clause, and the target stated as a number: as deep front to back as it is wide. |
| 4 | plate | Aspect **1 : 0.84**, up from 1 : 0.61. The octagonal deck now reads as an octagon covering ground rather than an ellipse pasted on a box, and the slewing ring sits on the deck at the same angle instead of floating flat on it. Design unchanged: magazine left, crystal bin right, corner bollards, no arm, nothing lit. Body metal `#5E554C`, luminance 86, inside §3.3. | **Accepted — `concept/v4-hub.png` is the plate** | None. Cut at 224 × 189 with 192 px of visible content; crystal split into `bin.png`; icon derived; prototype wired. |

### What this building cost, in one line

The concept sheets are drawn at a shallower camera than Factorio's projection,
and **the aspect ratio of the trimmed content is the cheapest way to see it**.
Measure the plate against a real vanilla building of the same footprint before
anything else: `aspect` is already in `--report` output, and 1 : 0.61 against a
1 : 0.96 target is not a judgement call. Every remaining building in this mod is
cut from a sheet drawn the same way, so expect the same round on each.

---

# 20. The crane, and what it actually costs

Section 6 says the crane is a separate prototype and cannot be replaced by
editing the hub plate. That is still true. What was *wrong* — asserted in this
session and corrected the same session — is the claim that authoring one needs
64 hand-drawn angles per part and is therefore out of reach.

**The engine does the rotation.** Every one of the 128 frames in
`agricultural-tower-crane-5` is drawn with the arm segment *vertical*; the crane
parts carry `rotated_sprite` with `direction_count = 128`, and the engine
selects and orients them. The frames are not 128 poses. They are one pose seen
from 128 camera azimuths, and what varies is shading and self-occlusion.

Measured, frame 0 against the others:

| vs frame 0 | silhouette differs | colour differs |
| ---------- | -----------------: | -------------: |
| 1 | 2.7% | 4.7% |
| 16 | 18.1% | 36.5% |
| 32 | 25.9% | 39.2% |
| 63 | 6.1% | 31.5% |

So a bespoke crane needs **one canonical vertical image per part**, replicated
across that part's direction count. The arm then swings correctly, because the
engine is doing the swinging; what it loses is the up-to-26% of outline and up
to 47% of colour that should shift as the camera comes round. At 33 in-game px
across, that is a small and honest loss.

Six generations would do it: hub, inner arm, inner joint, central arm, central
joint, and outer arm with gripper. Until then the recoloured vanilla arm stands,
which is right in material and wrong in movement.

**The general lesson, which is the template's:** do not assert what an asset
costs before opening it. "Sixty-four angles per part" was inferred from a frame
count and would have closed off a tractable job. One look at the frames, and one
measurement across them, said otherwise.
