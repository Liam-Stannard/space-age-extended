# Factorio Building — Art & Implementation Specification

**Radiant Generator.** Began as a brief — enough to commission and judge a
concept sheet — and was filled out into a specification once that sheet was
approved. Every gameplay number is read off `prototypes/corridor.lua` and the
vanilla `burner-generator` it deep-copies.

**The inherited art is the problem this document exists to solve.** The
placeholder is literally a steam engine, on a world where nothing burns and
there is no air to carry sound or smoke. §3.1's anti-read is unusually long for
that reason.

§13 is the one section still open: its numbers are measured off the canonical
plates, and those do not exist yet.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **passed — `concept/v2-sheet.png`** |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3 | blocked on 0 |
| 2 | Idle plate (unlit) | portrait 2:3 | Same machine, nothing lit | blocked on 1 |
| 3 | Directional frames | portrait 2:3 | **Two are needed** — see §5 | blocked on 2 |
| 4 | Glow plates | portrait 2:3 | Differenced against stage 2 | blocked on 2 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

### Where generation happens

Browser — ChatGPT's image tool. Template Appendices B and C apply in full.

### Round log

See §19.

---

# 1. Building Overview

**Building Name:** `Radiant Generator`
**Internal Prototype Name:** `sae-radiant-generator`

**Building Type:** `burner-generator`, deep-copied from the base game's hidden
`burner-generator` — which is itself a steam engine's art on a burner chassis.
**That inheritance is the problem this art exists to solve:** the placeholder is
literally a steam engine, and a steam engine is the single most wrong object
that could stand on a vacuum world.

**Purpose:** The one power source that is *made where it is spent*. Radiant fuel
has its own `fuel_category`, so it cannot be shovelled into anything that
already exists, and this generator will take nothing else. Ten megawatts, in
vacuum, from rock crushed out of the corridor.

**Locale:** *"Ten megawatts from the only fuel out here. Nothing else will take
that fuel, and it will take nothing else."* / *"Burns the only fuel out here…
Works in vacuum, which is the point: it is made where it is spent."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 3×5 (`collision_box {-1.35,-2.35},{1.35,2.35}`, inherited) |
| Directions | 2 distinct (N/S share art, E/W share art) |
| Output | 10 MW, electric, `primary-output` |
| Fuel | `sae-radiant` category only; 2 fuel slots, no burnt-result slot |
| Surface conditions | pressure ≤ 9 — the Core and space platforms |
| Stack size / weight | 10 / 40000 |
| Recipe | 20 processing unit, 20 low-density structure, 40 steel plate |

**No emissions and no burnt result.** The `burner` block sets no
`emissions_per_minute` and `burnt_inventory_size = 0`, so nothing is vented and
nothing comes out. The art must not contradict either.

---

# 3. Visual Design

## 3.1 Design Concept

A **radiant** generator, not a combustion one. The fuel does not burn in the
ordinary sense; it is a rock that emits, and the machine's job is to stand
around that emission and collect it. So the building is not an engine — it has
no moving parts the player can see, no reciprocating anything, no exhaust.

It is a **long armoured trough** lying on its 3×5 footprint: a fuel magazine at
one end, a shielded reaction throat down the middle, and a heavy conversion
block at the other end where the cabling leaves. The one thing that moves is
light: a cool green-white glow that lives *inside* the throat and shows only
through narrow shielded slots, because anything that can put out ten megawatts
in vacuum is something you look at through a slot.

**The anti-read, and it is the whole point:** it must not read as a steam
engine. No pistons, no connecting rods, no flywheel, no crankshaft, no boiler
drum, no chimney, no exhaust, no steam, no smoke, no fire, no orange heat. The
placeholder art has every one of those and each is a lie on a vacuum world.

## 3.2 Key Visual Features

* A **long low armoured trough**, running the length of the 5-tile axis, ribbed
  with heavy cooling fins along both flanks — the fins are radiators, and in
  vacuum radiators are the only way heat leaves, so they should be the most
  prominent structure on the building.
* A **fuel magazine** at one end: a squat armoured hopper with a heavy sliding
  lid and two loading ports, matching the two fuel slots.
* A **shielded reaction throat** down the centre: a thick-walled tube with
  three or four narrow horizontal viewing slots, cool green-white light showing
  through them and nowhere else.
* A **conversion block** at the far end — a dense finned mass with heavy
  armoured cable trunks leaving from its base.
* Lead-grey **shielding collars** clamped around the throat at intervals,
  bolted, obviously heavy.

### Signature Feature

The radiator fins. They say "this machine sheds heat with nowhere for the heat
to go", which is the vacuum read, and they hold the silhouette at one tile.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Armour and trough body | `#4A463F` → `#6E685C` | the mass of the building |
| Radiator fins | `#8A8580` | flanks, conversion block |
| Shielding collars | `#3B3B40` | clamps around the throat |
| Radiant light | `#A8E8C0` → `#E8FFF0` | throat slots only |
| Cable terminations | `#8A5A32` | conversion block base |

The radiant green-white is the same hue as the radiant chunk and radiant fuel
icons, and that is deliberate: the fuel, the rock and the machine that burns it
should be recognisably one family. **No orange anywhere** — orange is heat, and
heat is the read this building is avoiding.

---

# 4. Factorio Visual Style

Between the two camera cases: 3×5 on the ground and low, so mostly roof and a
shallow near face, but long enough that the trough's length has to be legible.
Name the camera exactly — "the game's characteristic 45-degree top-down
perspective" — and do not add the tall building's leaning clause.

**Style reference to attach:** a vanilla sprite that is not the anti-read —
the fusion reactor or the nuclear reactor, cropped to one frame and upscaled,
with the standing disclaimer. **Do not attach the steam engine**; it is the
exact object the design is trying to escape.

---

# 5. Building Orientation

* [x] North · [x] East · [x] South · [x] West

**Direction count:** `2`. The inherited prototype maps north/south to one
animation and east/west to the other, so two plates are needed: the trough
running vertically and the trough running horizontally. They are the same
machine rotated, not two designs.

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
| Fuel in | any adjacent tile | inserters, unconstrained |
| Electric out | no visible connector — poles reach it wirelessly | `energy_source` |
| Fluids | none | `burner-generator` has no fluid box |
| Burnt result | none | `burnt_inventory_size = 0` |

**Nothing to reconcile.** A `burner-generator` accepts fuel from any tile
touching its footprint, so the fuel hopper at one end of §3.2 is honest
decoration in exactly the way a vanilla furnace's is — it tells the player where
the fuel conceptually goes without constraining where an inserter may stand.

Two things the art must still not imply: there is **no burnt-result slot**, so
nothing should look like an ash or waste port, and there is **no fluid box**, so
no pipe flange anywhere on the building. Every pipe-like form on this machine is
internal plumbing, not a connection.

# 11. Generation Requirements

**Canvas:** portrait 2:3 for the north plate, landscape for the east plate,
landscape 3:2 for the sheet. Generate at the largest size available.

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio Space
Age building, every panel drawn from the game's characteristic 45-degree
top-down perspective, laid out as labelled panels on a dark charcoal
background, in the style of a game art bible page.

Panels: two large hero views of the building, one labelled VERTICAL and one
labelled HORIZONTAL, the same machine rotated ninety degrees; an in-game icon
panel showing it simplified to a 64x64 item icon; a tile-grid panel showing it
from directly overhead on a 3 by 5 tile grid; three close-up detail panels
showing the fuel magazine with its sliding lid, a shielding collar clamped
around the reaction throat, and a radiator fin bank; a layer breakdown row
showing shadow, trough, fins, shielding and glow separated; a row of four
animation key frames showing the light in the throat slots rising from dark to
full; and a palette strip of eight swatches.

The building in every panel is the same machine: a long low armoured trough
lying flat on the ground and filling a three by five tile footprint, no taller
than about one tile. Heavy cooling radiator fins run in banks along both long
flanks and are the most prominent structure on it. At one end sits a squat
armoured fuel hopper with a heavy sliding lid and two loading ports. Down the
centre runs a thick-walled shielded tube with three narrow horizontal viewing
slots in its side, cool green-white light showing through those slots and
nowhere else on the building. Lead-grey shielding collars are bolted around the
tube at intervals. At the far end is a dense finned conversion block with heavy
armoured cable trunks leaving from its base.

Dark iron-nickel grey-brown metal, #4A463F to #6E685C, pale grey #8A8580
radiator fins, near-black #3B3B40 shielding collars, cool radiant green-white
#A8E8C0 to #E8FFF0 confined entirely to the throat slots, and copper-brown
#8A5A32 cable terminations.

It must read as a sealed radiant power source standing in vacuum, never as a
steam engine or a combustion engine: no pistons, no connecting rods, no
flywheel, no crankshaft, no boiler, no chimney, no exhaust pipe, no steam, no
smoke, no fire, and no orange or red heat anywhere on the building. Panel labels
and small caption text are wanted on this sheet. Painted semi-realistic
industrial game art. No characters, no photorealism.
```

---

---

# 6. Sprite Assets Required

`burner-generator` has the smallest art surface of any building in this mod:
one animation, optionally two.

| Slot | Frames | Directions | Plan |
| ---- | -----: | ---------: | ---- |
| `animation.north` / `.south` | 1 | shared | **Replace** — the trough running away from the viewer. |
| `animation.east` / `.west` | 1 | shared | **Replace** — the same machine turned a quarter turn. |
| `idle_animation` | 1 each | 2 | **Replace** — identical to `animation` but with the throat slots dark. |
| Shadow | 1 each | 2 | **Derive**, as a layer inside each animation. |

**Two plates, not four.** The inherited prototype maps north and south to one
animation and east and west to the other, which is the whole reason §5 asks for
two hero views rather than four.

**`idle_animation` is what makes the fuel state readable.** Without it the
throat glows whether or not the generator has fuel, and a burner with no fuel
looking exactly like one at full output is a lie the player has to open the GUI
to catch. The idle plate is the same pixels with layer 3 omitted.

---

# 7. Layer Structure

| # | Layer | Draw as | Animated | Notes |
| - | ----- | ------- | -------: | ----- |
| 1 | Shadow | `draw_as_shadow = true` | no | Derived. Long, because the building is long. |
| 2 | Trough, fins, hopper, collars, conversion block | normal | no | The whole machine, **throat slots dark**. |
| 3 | Throat glow | `draw_as_glow = true`, additive | yes | The three slots, and nothing else on the building. |

### Layer Notes

**The slots are cut in layer 2 and lit in layer 3.** Layer 2 carries the slot
openings, their depth and their shadowed interior; layer 3 carries only the
green-white light inside them. Derived by differencing, so registration is exact.

**Radiator fins are never emissive.** They shed heat; they do not make it. If
anything but the throat slots ends up in the glow plate, the difference was taken
against the wrong pair of images.

---

# 12. Image Processing

### Processing Checklist

1. `--report` before judging anything.
2. `--dekey` if the export was flattened.
3. Cut **both** direction plates to the §13 canvases. They are different sizes —
   3×5 one way, 5×3 the other — and that is the whole point of having two.
4. Derive the shadow per plate.
5. Derive the glow per plate, by differencing lit against unlit.
6. `idle_animation` is the unlit plate; no extra work.

**Do not derive one direction from the other by rotating it.** The camera does
not rotate, so the east plate is a different drawing of the same object, not the
north plate turned ninety degrees. Rotating it produces a machine lit from the
wrong side, which is the tell that gives away a bad directional set.

---

# 13. Sprite Dimensions

**Not yet measurable.** Fixed in advance:

**Tile Size:** `32` px in-game · **Scale:** `0.5` → `64` source px per tile

**Footprint:** 3×5 tiles. `collision_box` `{{-1.35,-2.35},{1.35,2.35}}`,
`selection_box` `{{-1.5,-2.5},{1.5,2.5}}`, both inherited from the vanilla
`burner-generator`, itself a steam-engine chassis.

**Load-bearing numbers, per direction:**

| Direction | Deck must span | Source px at scale 0.5 |
| --------- | -------------- | ---------------------- |
| North / south | 3.00 tiles wide × 5.00 tall | `192 × 320` |
| East / west | 5.00 tiles wide × 3.00 tall | `320 × 192` |

Get these exactly right or a row of generators will not tile.

**Height above the deck:** low — §3.1 says no taller than about one tile — so the
visible mass sits close to the footprint and the shadow does most of the work of
seating it.

**Shift:** anchor on the trough's base, the part that touches the ground.

---

# 14. File Structure

```
graphics/entity/radiant-generator/
    base-v.png       colour plate, vertical (north/south), throat dark
    base-h.png       colour plate, horizontal (east/west), throat dark
    shadow-v.png     derived
    shadow-h.png     derived
    glow-v.png       throat slots, additive
    glow-h.png       throat slots, additive
    concept/         v1-sheet.png, v2-sheet.png
graphics/icons/
    radiant-generator.png   64 px mipmap strip, derived from base-v.png
```

---

# 15. Factorio Prototype

### Graphics

```lua
local ART = "__space-age-extended__/graphics/entity/radiant-generator/"
local function plate(tag, w, h, shift)
  return { layers = { <base-tag.png>, <shadow-tag.png draw_as_shadow>, <glow-tag.png draw_as_glow> } }
end
gen.animation =
{
  north = plate("v", ...), south = plate("v", ...),
  east  = plate("h", ...), west  = plate("h", ...)
}
gen.idle_animation = -- the same, minus the glow layer
{
  north = idle("v", ...), south = idle("v", ...),
  east  = idle("h", ...), west  = idle("h", ...)
}
```

### Other Visual Properties

`gen.working_sound` is already the steam engine's, inherited deliberately in
`prototypes/corridor.lua`. **That should change with the art**: a steam engine's
reciprocating sound is the audio equivalent of the piston this design spent its
whole anti-read removing. A low continuous hum would match the machine. Out of
scope for the art pass, but worth doing in the same commit.

There is no smoke, no `emissions_per_minute` and no burnt result; §8 covers why
none of them may appear.

---

# 17. Visual QA Checklist

### Building

- [ ] Reads as a sealed radiant source, never as a steam or combustion engine
- [ ] No piston, rod, flywheel, boiler, chimney, exhaust, steam or smoke
- [ ] No orange or red anywhere — heat is the wrong colour on this building
- [ ] Radiator fins are the dominant silhouette feature
- [ ] Fuel hopper shows exactly two loading ports, matching `fuel_inventory_size`
- [ ] Body metal luminance inside the §3.3 range, **measured**

### Directions

- [ ] Vertical and horizontal plates are the same machine, lit identically
- [ ] Neither is a rotation of the other
- [ ] Both tile cleanly against a neighbour of the same orientation

### Animation

- [ ] Light appears only in the throat slots
- [ ] Idle plate is genuinely dark — a fuelless generator must look fuelless
- [ ] Glow registers exactly on the slots modelled in layer 2

### In-Game

- [ ] Sits on its footprint in both orientations
- [ ] Selection box matches the visible building
- [ ] Reads correctly on a space platform as well as on the Core

---

# 18. Final Asset Checklist

- [ ] `base-v.png`, `base-h.png` cut and measured
- [ ] `shadow-v.png`, `shadow-h.png` derived
- [ ] `glow-v.png`, `glow-h.png` derived by differencing
- [ ] Icon derived from `base-v.png`
- [ ] §13 filled in with **measured** numbers for both orientations
- [ ] Prototype wired with `animation` **and** `idle_animation`
- [ ] Working sound reconsidered — see §15
- [ ] `./tools/check-data-stage.sh` passes
- [ ] Verified in a client, fuelled and unfuelled

# 19. Design Notes / Iteration History

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| 1 | sheet | The machine landed first time and the anti-read held completely — radiator fin banks dominate the silhouette, the shielded throat shows light only through its slots, and there is no piston, flywheel, boiler, chimney, exhaust, steam, smoke or warm colour anywhere. Fuel hopper carries exactly two loading ports, matching `fuel_inventory_size = 2`. Palette strip carries the §3.3 hexes. **But the VERTICAL and HORIZONTAL hero panels showed the same orientation**, so the sheet did not actually show the two directions §5 needs — the same turntable-versus-rotation trap the Vent Pump spec warns about. | **Machine accepted; direction panels rejected** | Two fixes: (1) HORIZONTAL must be the same machine rotated a quarter turn on the ground under a fixed camera, long axis running across the screen rather than up it; (2) the sheet titled itself RADIANT POWER SOURCE, should be RADIANT GENERATOR. |
| 2 | sheet | Both fixes landed. VERTICAL is now tall and narrow with the trough running away from the viewer, HORIZONTAL is wide and short with it running across — the same machine under the same camera, rotated a quarter turn, which is what §5 needs. Title corrected. The building itself came back unchanged. | **Accepted — `concept/v2-sheet.png` is the locked design** | None. |
