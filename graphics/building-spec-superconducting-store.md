# Factorio Building — Art & Implementation Specification

**Superconducting Store.** Began as a brief — enough to commission and judge a
concept sheet — and was filled out into a specification once that sheet was
approved and the connection review of §8 was done. Every gameplay number is read
off `prototypes/trees/fulgora-aquilo.lua` and the vanilla `accumulator` it deep-
copies. §13 is the one section still open, because its numbers are measured off
the canonical plate and that plate does not exist yet.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **passed — `concept/v1-sheet.png`** |
| 1 | Canonical view | square | Silhouette approved against §3 | blocked on 0 |
| 2 | Idle plate (unlit) | square | Same machine, nothing lit | blocked on 1 |
| 3 | Directional frames | — | n/a — no rotation, see §5 | n/a |
| 4 | Charge frames | square | **Five states**, see §9 | blocked on 2 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

### Where generation happens

Browser — ChatGPT's image tool. Template Appendices B and C apply in full.

### Round log

See §19.

---

# 1. Building Overview

**Building Name:** `Superconducting Store`
**Internal Prototype Name:** `sae-superconducting-store`

**Building Type:** `accumulator`, deep-copied from vanilla's.

**Purpose:** The Fulgora ↔ Aquilo capstone building, and the first tree's
payoff. A world of spikes — Fulgora's lightning when it is earned, the Core's
arc storms at the end — has always wanted somewhere to put a surge that arrives
faster than anything can spend it. Half a gigajoule, and it will take twenty
megawatts at once: **twenty times a vanilla accumulator's capacity and four
times its input limit.** That ratio is the design, and the art has to carry it.

**Locale:** *"Somewhere to put a surge that arrives faster than anything can
spend it."* / *"Half a gigajoule, and it will take twenty megawatts at once.
Built for a sky that pays in lumps."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 2×2 (inherited from `accumulator`) |
| Directions | 1 — `accumulator` has no rotation |
| Buffer | 500 MJ (vanilla: 5 MJ) |
| Input / output flow limit | 20 MW / 20 MW (vanilla: 5 MW / 5 MW) |
| Usage priority | tertiary |
| Stack size / weight | 20 / 20000 |
| Recipe | 10 superconducting winding, 2 accumulator, 20 steel plate |

**Two tiles is the constraint that shapes everything.** This building holds a
hundred times a vanilla accumulator's energy in the same 2×2 the player already
knows, so the art has one job: look far too dense for its footprint.

---

# 3. Visual Design

## 3.1 Design Concept

A vanilla accumulator is a **box with a light on it** — a flat-topped cabinet
with a glowing panel that brightens as it charges. That is a battery. This is
not a battery; it is a **superconducting ring**, and what stores the energy is
a current going round and round in a loop that never loses anything, held cold
enough that it doesn't stop.

So the building is a **cryostat**: a squat armoured cylinder, heavily insulated,
with the storage ring buried inside it and cold plumbing wrapped around the
outside. The player should be able to see that the expensive part is the
*cooling*, not the vessel — because that is what the recipe says, ten
superconducting windings and a chain that runs back to Aquilo.

**The anti-read:** it must not read as a vanilla accumulator with a different
paint job — no flat cabinet, no big glowing rectangular panel on the front. And
it must not read as a fluid tank either; a plain drum with pipes is the shape
this design will collapse into if the ring is not visible.

## 3.2 Key Visual Features

* A squat, heavily armoured **cylindrical cryostat** filling the 2×2 footprint,
  banded with insulation wrap rather than plain plate.
* The **storage ring**, visible as a continuous circular channel around the
  vessel's upper third — a recessed toroidal groove, and the one place light
  appears. It goes all the way round: a ring the eye can follow, not a gauge.
* **Cold plumbing** — two frost-jacketed feed lines entering at opposite sides
  and disappearing into the vessel wall, with condensation collars where they
  enter.
* A **heavy terminal block** at one side where the busbars leave, deliberately
  oversized for a 2×2 building, with thick armoured cabling.
* **Frost** gathering on the lower third and nowhere else, because the top runs
  warmer.

### Signature Feature

The continuous glowing ring. It is legible from directly overhead at 2×2, it
distinguishes the building from every box in the game, and it gives the charge
animation somewhere to happen — the light travels *around* the ring rather than
filling a bar.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Armour and insulation wrap | `#4A463F` → `#6E685C` | vessel body |
| Bolt rings and collars | `#B9B4A8` | banding, pipe entries |
| Ring light, charged | `#9FC4E8` → `#E8F4FF` | the toroidal channel only |
| Cold plumbing and frost | `#B8D8E8` | feed lines, lower third |
| Busbar terminations | `#8A5A32` | terminal block |

The ring light is the same blue-white as the superconducting winding and the
field conductor icons, which is deliberate: the winding, the store built from it
and the conductor it becomes should read as one material.

---

# 4. Factorio Visual Style

The **flat camera case** — 2×2 and squat, so mostly lid and a shallow near
face. At two tiles the whole building is about the size of a single detail panel
on the Ignition Array's sheet, so detail density must be tuned down: three or
four legible components, not a dozen.

**Style reference to attach:** the vanilla nuclear reactor or a chemical plant,
cropped to one frame and upscaled, with the standing disclaimer. **Do not attach
the vanilla accumulator**; it is the anti-read.

---

# 5. Building Orientation

* [x] North
* [ ] East · South · West

**Direction count:** `1`. `accumulator` has no direction. The design is radial,
which suits that.

---

# 9. Working Animation

The charge state is the one thing this building animates, and it is derived,
not generated — the glow plate is differenced out of a lit plate against the
unlit one and then masked, exactly as in template Appendix C. Five states are
wanted, `0%` through `100%`, and the light **travels around the ring** rather
than filling it like a bar: at 20% a short arc glows, at 100% the ring is
continuous and brightest.

Direction carries meaning here. Light running *around* the ring reads as a
current circulating, which is what a superconducting store physically is.

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
| Electric | no visible connector — poles reach it wirelessly | `energy_source` |
| Charge / discharge overlay | drawn over the base | `accumulator.chargable_graphics` |
| Items / fluids | none | — |

No pipes and no inserters, so the plate is free of hard geometry. The trap here
is different: the prototype deep-copies `accumulator`, which carries
`chargable_graphics.charge_animation` and `discharge_animation` — sprite layers
drawn **on top of** the base and shaped for vanilla's flat-fronted box.

**Resolved in the prototype.** `charge_animation`, `discharge_animation` and both
cooldowns are now cleared in `prototypes/trees/fulgora-aquilo.lua`, so no
vanilla-shaped panel glow can land on the cryostat drum.

Cleared rather than left alone deliberately: the failure only appears at the
moment the plate lands, when whoever sets `chargable_graphics.picture` would have
to remember that the overlays are a coupled set. Clearing them now makes the
requirement impossible to miss and costs only the placeholder's charge glow on a
building nobody has played with.

**What has to go back:** the five ring states of §9, as `charge_animation`, with
the light travelling around the channel rather than filling a bar. Until then the
store has no charge feedback at all, which is honest — it has no ring either.

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
overhead on a 2x2 tile grid; three close-up detail panels showing the recessed
toroidal ring channel, a frost-jacketed feed line entering the vessel wall, and
the busbar terminal block; a layer breakdown row showing shadow, vessel, ring
channel, plumbing and glow separated; a row of five animation key frames labelled
0, 25, 50, 75 and 100 per cent, in which a band of light travels progressively
further around the ring channel until it closes into a continuous circle; and a
palette strip of eight swatches.

The building in every panel is the same machine: a squat, heavily armoured
cylindrical cryostat filling a two by two tile footprint, wider than it is tall,
banded with insulation wrap rather than plain plate. Around its upper third runs
a continuous recessed circular channel, unbroken all the way round, and this
channel is the only place light appears on the building. Two frost-jacketed feed
pipes enter the vessel wall at opposite sides, each with a pale condensation
collar where it meets the armour. A heavy busbar terminal block, deliberately
oversized for so small a building, sits at one side with thick armoured cabling
leaving it. Frost gathers on the lower third of the vessel and nowhere else.

Dark iron-nickel grey-brown metal, #4A463F to #6E685C, pale nickel-white
#B9B4A8 banding and collars, blue-white #9FC4E8 to #E8F4FF confined entirely to
the ring channel, pale frost #B8D8E8 on the plumbing and the lower vessel, and
copper-brown #8A5A32 busbar terminations.

It must read as an insulated superconducting ring store, never as an ordinary
battery cabinet and never as a fluid tank: no flat-topped box, no large glowing
rectangular panel on any face, no charge bar, no plain drum with pipes on it,
nothing that looks like a storage tank. Keep the detail count low — this is a
two tile building and only three or four components should be legible. Panel
labels and small caption text are wanted on this sheet. Painted semi-realistic
industrial game art. No characters, no photorealism.
```

---

---

# 6. Sprite Assets Required

`accumulator` has a small art surface, which is the main reason this building is
a good one to cut first.

| Slot | Frames | Plan |
| ---- | -----: | ---- |
| `chargable_graphics.picture` | 1 | **Replace** — the cryostat: deck, drum, insulation banding, ring channel unlit, plumbing, busbar block. This is the building. |
| `chargable_graphics.charge_animation` | 5+ | **Replace, derived** — the ring channel lit, by the §12 method. Currently `nil`; see §8. |
| `chargable_graphics.discharge_animation` | 5+ | **Replace, derived** — same plate, run the other way. Currently `nil`. |
| `chargable_graphics.charge_cooldown` / `discharge_cooldown` | — | Restore with the animations. Vanilla uses 30 and 60. |
| `water_reflection` | 1 | **Suppress.** No water tile can ever place on the Core (`planet.lua` guarantees it via the elevation expression), so the reflection is dead weight. Set to `nil`. |
| Shadow | 1 | **Derive** from the colour plate by the §12 method. |

There is no separate shadow slot on `accumulator`; the shadow is a layer inside
`picture`. That matters for §12 — the plate is built as a two-layer sprite, not
as two prototype fields.

---

# 7. Layer Structure

| # | Layer | Draw as | Animated | Notes |
| - | ----- | ------- | -------: | ----- |
| 1 | Shadow | `draw_as_shadow = true` | no | Derived, not drawn. Wider canvas than the colour layer; see §13. |
| 2 | Cryostat body | normal | no | Deck, drum, insulation banding, plumbing, busbar block, frost. The ring channel is present but **dark**. |
| 3 | Ring glow | `draw_as_glow = true`, additive | yes | The travelling band of light in the channel, and nothing else. |

### Layer Notes

**The ring channel must be modelled in layer 2 and lit in layer 3.** Cutting the
channel only into the glow layer is the mistake the template warns about in
Appendix C: a glow invented separately from the base never registers against it.
Layer 2 carries the recess, its shadow and its rim; layer 3 carries only the
light that sits inside it.

**Nothing else on the building is emissive.** The frost is not lit, the busbar is
not lit, and there are no status lamps. One light, one meaning.

---

# 12. Image Processing

### Processing Checklist

1. **Measure before judging.** `tools/process-building-art.py <plate> --report`.
   Never eyeball a transparent plate — see the template's Appendix C.
2. **De-key if needed.** An edited export arrives flattened onto the editor's
   checkerboard; `--dekey` restores alpha.
3. **Cut the colour plate.** Trim, scale and place on the sprite canvas with
   `--width`/`--height`/`--top-margin`, using the numbers §13 records once the
   canonical plate exists.
4. **Derive the shadow** — the tool does this from the colour plate. It is a
   placeholder by construction, not a true cast shadow; see Appendix C.
5. **Derive the glow.** Approve the unlit plate, then ask for *the same image with
   the ring lit*, unchanged in every other respect, and run
   `tools/derive-glow.py --lit <lit> --unlit <unlit>`. The difference **is** the
   light, so it registers by construction.
6. **Build the charge frames.** `tools/build-glow-frames.py --glow <plate>` with a
   travelling mask. The mask runs **around** the ring; it does not fill a bar.
   Five states at minimum, per §9.
7. **Never draw a frame by hand.** Nineteen separate generations drift; a mask
   cannot.

---

# 13. Sprite Dimensions

**Not yet measurable.** These numbers are derived from the approved canonical
plate, and there isn't one. What is fixed in advance:

**Tile Size:** `32` px in-game · **Scale:** `0.5` → `64` source px per tile

**Footprint:** 2×2 tiles. `collision_box` is `{{-0.9,-0.9},{0.9,0.9}}` and
`selection_box` `{{-1,-1},{1,1}}`, both inherited.

**Width, load-bearing:** the drum must span **exactly 2.00 tiles** at scale 0.5,
which is `128` source px, so that a row of stores touches and never overlaps.
The plate is wider than that only by its side margins.

**Height:** the building is squat — §4 says wider than it is tall — so expect
roughly 1.2 to 1.4 tiles of visible height above the deck. Measure it; do not
assume it.

**Shift:** anchor on the **deck**, which is the part that touches the tile, not
on the top of the dome. The arc-mast spec's §13 records what anchoring on the
tip costs: the whole building floated two thirds of a tile above its own
footprint. Measure the deck's row span in the cut plate and match its centre to
the origin.

---

# 14. File Structure

```
graphics/entity/superconducting-store/
    base.png            colour plate, unlit
    shadow.png          derived
    charge.png          glow spritesheet, ring filling
    discharge.png       glow spritesheet, ring emptying
    concept/            v1-sheet.png and any later rounds
graphics/icons/
    superconducting-store.png    64 px mipmap strip, derived from base.png
```

Matches the arc-mast's layout exactly, so `tools/` needs no new paths.

---

# 15. Factorio Prototype

### Graphics

```lua
local ART = "__space-age-extended__/graphics/entity/superconducting-store/"
store.chargable_graphics =
{
  picture =
  {
    layers =
    {
      { filename = ART .. "base.png",   width = W, height = H, shift = SHIFT, scale = 0.5 },
      { filename = ART .. "shadow.png", width = SW, height = SH, shift = SSHIFT,
        scale = 0.5, draw_as_shadow = true }
    }
  },
  charge_animation    = <charge.png sheet>,
  charge_cooldown     = 30,
  discharge_animation = <discharge.png sheet>,
  discharge_cooldown  = 60
}
store.water_reflection = nil
```

`W`, `H` and `SHIFT` come from §13 once the plate is cut. **Set the animations in
the same commit as `picture`** — §8 explains why they are currently `nil`, and
leaving them out again would reintroduce exactly the bug that clearing them was
meant to prevent.

### Other Visual Properties

Unchanged from the inherited prototype: `circuit_connector`,
`circuit_wire_max_distance`, `impact_category`, the open/close sounds. There is
no working sound on an accumulator and none should be added — this building is
silent, which suits a superconducting loop with no moving parts.

---

# 17. Visual QA Checklist

### Building

- [ ] Reads as an insulated ring store, not a battery cabinet and not a tank
- [ ] The ring channel is continuous and unbroken all the way round
- [ ] Frost on the lower third only
- [ ] Busbar block reads as oversized for a 2×2
- [ ] Three or four legible components, no more — §4
- [ ] Body metal luminance inside the §3.3 range, **measured** not eyeballed

### Animation

- [ ] Light travels **around** the ring; it does not fill like a bar
- [ ] 0% is fully dark; 100% closes into a continuous circle
- [ ] Glow registers exactly on the channel modelled in layer 2
- [ ] Discharge is distinguishable from charge by direction, not only by speed

### In-Game

- [ ] Two stores side by side touch and do not overlap
- [ ] Sits on its footprint — not floating, not sunk
- [ ] Selection box matches the visible building
- [ ] Shadow falls consistently with neighbouring buildings
- [ ] Charge state is readable at default zoom, which is the only zoom that matters

---

# 18. Final Asset Checklist

- [ ] `base.png` cut, measured, alpha verified
- [ ] `shadow.png` derived
- [ ] `charge.png` / `discharge.png` built from a masked glow plate
- [ ] `superconducting-store.png` icon derived from the plate
- [ ] §13 filled in with **measured** numbers
- [ ] Prototype wired, including the animations
- [ ] `./tools/check-data-stage.sh` passes
- [ ] Verified in a client at default zoom

# 19. Design Notes / Iteration History

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| 1 | sheet | **Accepted first round.** The anti-read held: a squat insulated cryostat with a continuous recessed ring channel as the only lit feature, frost-jacketed feed pipes with condensation collars, and an oversized busbar block — no flat-topped cabinet, no glowing panel, no charge bar, nothing tank-like. Detail count stayed low, which was the hard part at 2×2. **The charge animation is exactly the §9 behaviour**: the light travels progressively around the ring at 0/25/50/75/100 per cent and closes into a continuous circle, rather than filling like a bar. Palette strip carries the §3.3 hexes. | **Accepted — `concept/v1-sheet.png` is the locked design** | None. |
