# Factorio Building — Art & Implementation Specification

**Sealed Roboport.** Began as a brief — enough to commission and judge a concept
sheet — and was filled out into a specification once that sheet was approved and
the connection review of §8 had rebuilt the design around what the engine
actually draws. Every gameplay number is read off `prototypes/core/endgame.lua`
and the vanilla `roboport` it deep-copies.

**Read §8 before anything else.** This building's design was wrong in its first
round for a reason that had nothing to do with how it looked, and §8 is where
that is recorded.

§13 is the one section still open: its numbers are measured off the canonical
plate, and that plate does not exist yet.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **passed — `concept/v2-sheet.png`** |
| 1 | Canonical view | square | Silhouette approved against §3 | blocked on 0 |
| 2 | Idle plate (unlit) | square | Same machine, nothing lit | blocked on 1 |
| 3 | Directional frames | — | n/a — no rotation, see §5 | n/a |
| 4 | Glow plates | square | Differenced against stage 2 | blocked on 2 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

### Where generation happens

Browser — ChatGPT's image tool. Template Appendices B and C apply in full.

### Round log

See §19.

---

# 1. Building Overview

**Building Name:** `Sealed Roboport`
**Internal Prototype Name:** `sae-sealed-roboport`

**Building Type:** `roboport`, deep-copied from vanilla's. Restricted to
`surface_conditions = { pressure 1–9 }`, which is the Core and nowhere else in
the game: not a platform (0), not any vanilla world (Aquilo is the lowest at
300). It competes with nothing, which is why a second roboport is not a second
tier.

**Purpose:** Bots have been possible since the player landed; a *network* has
not. This is the building that turns the Core from hand-carried to logistically
served, and it is gated behind the Core's own chain — it costs cold-welded
plate, kamacite plate, processing units and two coolant loops.

**Locale:** *"Holds its own air so the bots inside it work at all."* /
*"A roboport that holds its own atmosphere. It works here, and nowhere else in
the system."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 4×4 (`collision_box {-1.7,-1.7},{1.7,1.7}`, inherited) |
| Directions | 1 — `roboport` has no rotation |
| Energy | 150 kW, electric |
| Surface conditions | pressure 1–9 |
| Stack size / weight | 10 / 40000 |
| Recipe | 20 cold-welded plate, 30 kamacite plate, 20 processing unit, 2 coolant loop |

---

# 3. Visual Design

## 3.1 Design Concept

The whole idea is in the first word. A vanilla roboport is **open**: a squat
open-topped drum with four exposed charging pads on its rim and bots landing on
them in the air. On the Core there is no air, so an open roboport is a
contradiction the player can see. This one is **sealed** — a pressure vessel
with the network happening inside it.

So the bots do not land on the outside. They pass through a **single airlock
hatch** on one face, and everything the vanilla building does in the open this
one does behind armour. What the player reads from outside is: a pressurised
drum, a hatch, and the evidence that something is pressurised — ribbing, seals,
an equalisation stack venting a puff that instantly freezes.

**The anti-read:** it must not read as a vanilla roboport recoloured. If the
sheet comes back with exposed charging pads on the rim, the design has failed
regardless of how good the metal looks.

## 3.2 Key Visual Features

* A heavy cylindrical pressure drum, wider than it is tall, on a square deck
  that fills the 4×4 footprint.
* A **domed armoured lid**, ribbed radially, bolted down with a visible ring of
  heavy fasteners — the seal is the signature.
* One **airlock hatch** set into the drum wall on the south face: a small
  rectangular double-door with a lit amber frame and a short landing shelf
  outside it. This is the only opening.
* A **pressure equalisation stack** at one rear corner — a short vertical pipe
  with a relief valve and a frost collar, the one place gas is allowed out.
* A ring of small **status lamps** around the base of the dome, the network's
  activity read.
* **Four recessed charging docks** at the `charging_offsets` of §8 — sockets cut
  into the deck, not pads on it.
* A **central iris aperture** in the dome's crown, over the axis, where robots
  enter and leave. See §8.

### Signature Feature

The bolted seal ring around the dome. It is the one component that says
"pressurised" from directly overhead at one tile, which is the only view that
matters.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Deck and drum body | `#4A463F` → `#6E685C` | the mass of the building |
| Bolt rings, seal ring, fasteners | `#B9B4A8` | dome ring, hatch frame |
| Hatch light and status lamps | `#E8A33A` | airlock frame, base ring |
| Frost / pressure evidence | `#C8DCE4` | equalisation stack collar |
| Warning stripe | `#8A5A32` | one short hazard band by the hatch |

Robot-network blue is deliberately absent. Vanilla owns it, and borrowing it
would pull the design back toward the building this one is avoiding.

---

# 4. Factorio Visual Style

The **flat camera case**: a 4×4 building barely two tiles tall, so the camera
shows mostly its lid, a shallow slice of its near face and no far face at all.
The Arc Mast's "leaning toward the viewer" clause does not apply and will tilt
the drum into a wall if it is used.

**Style reference to attach:** a vanilla sprite the design is *not* trying to
avoid resembling — the nuclear reactor or the accumulator, cropped to one
frame and upscaled, with the standing disclaimer: match the camera, rendering,
finish and level of detail; do **not** copy the design, shape, colours or
components. Do not attach the vanilla roboport; it is the anti-read.

---

# 5. Building Orientation

* [x] North
* [ ] East · South · West

**Direction count:** `1`. `roboport` has no direction and cannot be rotated.
The airlock hatch therefore always faces the same way, which is fine — it is a
building the player walks up to, not one they orient.

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
| Robot charging | `{-1.5, -1}` `{1.5, -1}` `{1.5, 1}` `{-1.5, 1}` | `roboport.charging_offsets` |
| Robot docking | `{0, 0}` — the centre | `roboport.stationing_offset` |
| Items in | any adjacent tile | inserters, unconstrained |
| Fluids | none | — |

**This is a direct conflict with §3.1 and it has to be resolved before a plate
is drawn.** The design's whole anti-read is "no open charging pads", but the
engine draws a charging robot, with its beam, at each of those four offsets
regardless of what the art shows — four robots hovering and sparking over blank
armoured drum. Robots also enter and leave at the **centre**, not at the airlock
hatch the design gives them.

**Resolved in the art, not the prototype.** The offsets are sensible positions
for a 4×4 and there was nothing to gain by moving them, so §3.2 gains two
components and the anti-read is tightened rather than weakened:

* **Four recessed charging docks**, one at each of the four offsets — a shallow
  socket cut into the armoured deck with a sprung clamp, two contact rails and an
  amber indicator. A socket is still sealed; a pad standing proud of the deck is
  not. This is now the wording the prompt uses, and "no open charging pads" stays
  exactly as strong an anti-read as before.
* **A central iris aperture** in the top of the dome, over the drum's axis, where
  robots come and go — because `stationing_offset` is `{0, 0}` and they will
  appear there whatever the art does. Closed when idle, and nothing may overlap
  it.

That leaves the building with two distinct routes, which is a better design than
the one it replaces: the airlock hatch on the wall is the **materials** route and
the iris on the roof is the **robot** route. Recorded in `concept/v2-sheet.png`.

# 11. Generation Requirements

**Canvas:** square for the plates, landscape 3:2 for the sheet. Generate at the
largest size available.

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio Space
Age building, every panel drawn from the game's characteristic 45-degree
top-down perspective, laid out as labelled panels on a dark charcoal
background, in the style of a game art bible page.

Panels: a large hero view of the building; an in-game icon panel showing it
simplified to a 64x64 item icon; a tile-grid panel showing it from directly
overhead on a 4x4 tile grid; three close-up detail panels showing the bolted
seal ring around the dome, the airlock hatch with its landing shelf, and the
pressure equalisation stack with its frost collar; a layer breakdown row showing
shadow, deck, drum, dome and lamps separated; a row of four animation key frames
showing the airlock hatch opening and its amber frame lighting; and a palette
strip of eight swatches.

The building in every panel is the same machine: a heavy sealed cylindrical
pressure drum, wider than it is tall, standing on a square armoured deck that
fills a four by four tile footprint. Its top is a domed armoured lid ribbed
radially and bolted down with a prominent ring of heavy fasteners. One small
rectangular double-door airlock hatch is set into the drum wall on the near
face, with a lit amber frame and a short landing shelf outside it; it is the
only opening anywhere on the building. A short vertical pressure equalisation
stack with a relief valve and a pale frost collar stands at one rear corner. A
ring of small amber status lamps runs around the base of the dome.

Dark iron-nickel grey-brown metal, #4A463F to #6E685C, pale nickel-white
#B9B4A8 bolt rings and seal ring, amber #E8A33A for the hatch frame and status
lamps, pale frost #C8DCE4 only at the equalisation stack, and one short
copper-brown #8A5A32 hazard band beside the hatch.

It must read as a sealed pressure vessel that holds its own atmosphere, never
as an ordinary open robot hangar: no open charging pads on the rim, no exposed
landing bays, no bots visible outside the building, no open tops, nothing blue.
Panel labels and small caption text are wanted on this sheet. Painted
semi-realistic industrial game art. No characters, no photorealism.
```

---

---

# 6. Sprite Assets Required

`roboport` exposes six art slots and a light, and the mapping onto this design is
unusually clean — every vanilla slot has an honest equivalent here.

| Slot | Frames | Plan |
| ---- | -----: | ---- |
| `base` | 1 | **Replace** — deck, drum, insulation banding, dome, seal ring, hatch, equalisation stack, and the four dock recesses **unlit**. This is the building. |
| `base_patch` | 1 | **Replace** — the ground patch under the deck. Also carries the derived shadow; see §7. |
| `base_animation` | n | **Replace** — the ring of amber status lamps at the base of the dome, idling. |
| `door_animation_up` | n | **Replace as the back half of the central iris.** |
| `door_animation_down` | n | **Replace as the front half of the central iris.** |
| `recharging_animation` | n | **Replace** — the contact arc inside a dock, drawn once per occupied `charging_offset`. |
| `recharging_light` | — | **Retint.** Vanilla's is blue (`{0.5, 0.5, 1}`); ours is amber to match §3.3. One-line change, no art. |

**The doors become the iris, and that is the whole trick.** Vanilla's roboport
opens a pair of sliding doors on its roof; the two halves are separate slots so
robots can be drawn between them. An iris of overlapping leaves splits the same
way — back leaves in `door_animation_up`, front leaves in `door_animation_down` —
so the engine's existing layering does the work and no control-stage code is
needed. The Ignition Array's spec uses the same split for its iris (§6.1 there),
which means the two buildings can share a method even though nothing else about
them matches.

---

# 7. Layer Structure

| # | Layer | Draw as | Animated | Notes |
| - | ----- | ------- | -------: | ----- |
| 1 | Ground patch + shadow | `base_patch`, shadow sub-layer `draw_as_shadow` | no | Derived. |
| 2 | Deck, drum, dome | `base` | no | Includes the four dock recesses and the iris collar, all **unlit**. |
| 3 | Iris back leaves | `door_animation_up` | yes | Closed on frame 0. |
| 4 | Iris front leaves | `door_animation_down` | yes | Closed on frame 0. |
| 5 | Status lamps | `base_animation`, `draw_as_glow` | yes | The amber ring at the dome base. |
| 6 | Dock contact arc | `recharging_animation`, `draw_as_glow` | yes | Drawn per occupied dock, not once per building. |

### Layer Notes

**Every dock recess is modelled in layer 2**, empty and unlit, and layer 6 adds
only the arc. The recess must therefore be drawn in the plate at all four
offsets even though nothing occupies it most of the time — a socket with nothing
in it still has to look like a socket.

**The iris is closed in the base plate too.** Layers 3 and 4 replace it when they
draw, so the crown of the dome carries a closed iris in `base` and the animation
takes over on top. That way a roboport with no robots moving still reads sealed.

---

# 12. Image Processing

### Processing Checklist

1. `tools/process-building-art.py <plate> --report` first, always.
2. `--dekey` if the export came back flattened onto a checkerboard.
3. Cut the colour plate to the §13 canvas.
4. Derive the shadow; it is a placeholder, per Appendix C.
5. **Derive the lamps and the arc by differencing**, not by drawing: approve the
   unlit plate, ask for the same image with the lamps lit and a dock arcing,
   `tools/derive-glow.py --lit <lit> --unlit <unlit>`.
6. **The iris is a mask job, not a generation job.** Cut the closed iris out of
   the approved plate once, then rotate the leaves programmatically for the open
   frames. Eight leaves rotating about one centre is exactly the case where a
   generator drifts and a transform cannot.

---

# 13. Sprite Dimensions

**Not yet measurable** — derived from the canonical plate, which does not exist.
Fixed in advance:

**Tile Size:** `32` px in-game · **Scale:** `0.5` → `64` source px per tile

**Footprint:** 4×4 tiles. `collision_box` `{{-1.7,-1.7},{1.7,1.7}}`,
`selection_box` `{{-2,-2},{2,2}}`, both inherited.

**Width, load-bearing:** the deck must span **exactly 4.00 tiles** — `256`
source px at scale 0.5 — so a row of roboports tiles cleanly. Side margins sit
outside that and are not part of the number.

**Height:** low-profile; the dome's crown should land around 1.5 tiles above the
deck. Measure it.

**Dock positions are the second load-bearing number.** The four recesses must
land on `{-1.5,-1}`, `{1.5,-1}`, `{1.5,1}`, `{-1.5,1}` in tile space — at scale
0.5 that is ±96 and ±64 source px from the plate's centre. Get this wrong and the
engine parks robots beside the sockets instead of in them. Check it on the cut
plate, not on the concept sheet.

**Shift:** anchor on the **deck**, not the dome.

---

# 14. File Structure

```
graphics/entity/sealed-roboport/
    base.png              colour plate, unlit, iris closed
    base-patch.png        ground patch
    shadow.png            derived
    lamps.png             status lamp animation, additive
    iris-back.png         door_animation_up
    iris-front.png        door_animation_down
    dock-arc.png          recharging_animation, additive
    concept/              v1-sheet.png, v2-sheet.png
graphics/icons/
    sealed-roboport.png   64 px mipmap strip, derived from base.png
```

---

# 15. Factorio Prototype

### Graphics

```lua
local ART = "__space-age-extended__/graphics/entity/sealed-roboport/"
port.base                = { layers = { <base.png>, <shadow.png draw_as_shadow> } }
port.base_patch          = <base-patch.png>
port.base_animation      = <lamps.png, draw_as_glow>
port.door_animation_up   = <iris-back.png>
port.door_animation_down = <iris-front.png>
port.recharging_animation = <dock-arc.png, draw_as_glow>
port.recharging_light    = { intensity = 0.2, size = 3, color = { 0.91, 0.64, 0.23 } }
```

The light colour is the §3.3 amber `#E8A33A` in normalised floats. Everything
else — `logistics_radius`, `construction_radius`, `charging_energy`, the slot
counts, `charge_approach_distance` — stays inherited and is not art's business.

### Other Visual Properties

`draw_logistic_radius_visualization` and `draw_construction_radius_visualization`
stay `true`. `radar_visualisation_color` stays vanilla's blue: it is a map-view
colour, not a building colour, and consistency with other roboports on the map is
worth more there than palette purity.

---

# 17. Visual QA Checklist

### Building

- [ ] Reads as a sealed pressure vessel, not an open robot hangar
- [ ] No pad stands proud of the deck anywhere
- [ ] Bolted seal ring legible from directly overhead at one tile
- [ ] Nothing blue on the building
- [ ] Body metal luminance inside the §3.3 range, **measured**

### Connections — the section this design was rebuilt around

- [ ] Four dock recesses land on the `charging_offsets` of §8, checked on the cut plate
- [ ] A robot drawn in a dock sits **in** the recess, not beside or on top of it
- [ ] The central iris is centred on `{0, 0}` and nothing overlaps it
- [ ] The airlock hatch reads as the materials route, distinct from the docks

### Animation

- [ ] Iris opens and closes about its own centre with no drift
- [ ] Back and front leaves layer correctly with a robot passing between them
- [ ] Lamps idle without implying the building is working
- [ ] Dock arc appears only at occupied docks

### In-Game

- [ ] Two roboports side by side touch and do not overlap
- [ ] Sits on its footprint
- [ ] Robots entering and leaving read as going through the iris

---

# 18. Final Asset Checklist

- [ ] `base.png`, `base-patch.png`, `shadow.png`
- [ ] `lamps.png`, `iris-back.png`, `iris-front.png`, `dock-arc.png`
- [ ] Icon derived from the plate
- [ ] §13 filled in with **measured** numbers, dock offsets verified
- [ ] `recharging_light` retinted amber
- [ ] Prototype wired; `./tools/check-data-stage.sh` passes
- [ ] Verified in a client with robots actually charging

# 19. Design Notes / Iteration History

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| 1 | sheet | **Accepted first round.** The anti-read held: a sealed pressure drum with a bolted dome seal ring, one amber airlock hatch with a landing shelf as the only opening, an equalisation stack with a frost collar, and a ring of status lamps — nothing resembling a vanilla roboport's open charging pads, no visible robots, no blue anywhere. Layer breakdown matches §3.2, the 4×4 grid panel contains the whole building, and the palette strip carries the exact §3.3 hexes. | **Accepted — `concept/v1-sheet.png` is the locked design** | None. |
| 2 | sheet | Redrawn against §8 after the connection review. **All three engine facts are now honoured**: four recessed charging docks straddling the drum at the `charging_offsets`, a central armoured iris over the axis where `stationing_offset` puts robots, and the airlock hatch demoted to the materials route. The docks read as sockets cut into the deck, with clamp and contact rails, so the "no open charging pads" anti-read survives intact — the detail panel shows a robot settled into one. Iris animation runs 0 to 100 per cent. Palette and layer breakdown correct. | **Accepted — `concept/v2-sheet.png` is the locked design** | None. |

### The conflict made the design better

Worth recording, because the first instinct was to treat the engine as an
obstacle. v1 had one opening and a contradiction; v2 has **two routes that mean
different things** — robots through the iris on the roof, materials through the
hatch on the wall — and that is a clearer building than the one the review broke.
The engine's four charging points and centre docking were not arbitrary; they
were a 4×4 layout someone had already thought about.
