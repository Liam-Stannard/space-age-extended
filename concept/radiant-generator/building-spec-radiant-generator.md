# Factorio Building — Art & Implementation Specification

**Radiant Generator.** The concept is signed off: the Carousel Foundry, options
round 7 (`options/round-7/1-the-carousel-foundry.png`), Liam, 2026-10-19:
"Sign off". This document describes that machine for the shipping model in
`concept/radiant-generator/model/`. Gameplay numbers are read off
`prototypes/corridor.lua` on master; where they disagree with this document,
the code is right, and §20 lists what was decided and what the wiring must change.

The old art is a steam engine's on a 3×5 chassis. The new building is a 5×5
power plant in which you watch the cell go from the hood to the wire.

---

# 0. Generation Contract

| # | Stage | Gate | State |
| - | ----- | ---- | ----- |
| 1 | Options | Liam picks | **done: round 6, the Carousel Foundry, 2026-10-12** |
| 2 | Refine | Liam signs off the concept | **done: round 7, 2026-10-19** |
| 3 | Spec | Wording agreed and written | this document |
| 4 | Model | Liam signs off the model | next: `radiant-generator-model` |
| 5 | Wiring | Liam signs off in game | after 4 |

**Where it is made.** Blender, through `tools/blender/render.sh --ports --icon`, in
`concept/radiant-generator/model/`, starting from the round-7 scripts
(`r7_carousel_foundry.py`, `r7_kit.py`). `--ports` stays so the contract
confirms the building has no ports. The light goes through
`tools/blender/radiant.py` (§3.3). Every new render takes the pipeline's
defaults: highlights rolled off above 236 to a top of 244, never on a light
pass; glow layers cropped to 99.9 % of their light. Measures through
`factorio-art-measure` only.

---

# 1. Building Overview

**Building Name:** `Radiant Generator`
**Internal Prototype Name:** `sae-radiant-generator`

**Building Type:** `burner-generator`, written out field by field (the steam
engine's field set), not copied from vanilla's hidden one.

**Purpose:** Stage 1 of the radiant power line (`design/08-core-power.md`): it
burns radiant cells, 500 MJ a cell, fifty seconds each at 10 MW, and hands back
a spent cell. Radiant fuel has its own `fuel_category`, so nothing else will
burn it, and this generator burns nothing else. The stage-4 Radiant Reactor,
40 MW with a neighbour bonus, must outclass it; this building leaves it the
spire, the arcs and the tiling.

**Locale:** *"Ten megawatts from the only fuel out here. Nothing else will take
that fuel, and it will take nothing else."* / *"Ten megawatts from radiant
cells, fifty seconds a cell, and each one handed back spent."* The `.cfg`
changes at wiring.

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | **5×5** (Liam, 2026-10-11: "i think the generator should be 5x5"): `collision_box {{-2.2,-2.2},{2.2,2.2}}`, `selection_box {{-2.5,-2.5},{2.5,2.5}}`, the nuclear reactor's. The prototype is still 3×5 until wiring |
| Directions | one picture for all four (§5) |
| Output | 10 MW, electric, `primary-output` |
| Fuel | `sae-radiant` only; 2 fuel slots; 1 burnt-result slot, which takes the spent cell (`sae-spent-cell`) |
| Surface conditions | pressure ≤ 9: the Core and space platforms |
| Stack size / weight | 10 / 40 kg |
| Recipe | 20 processing unit, 20 low-density structure, 40 steel plate |

**No emissions.** The burner sets no `emissions_per_minute` and the fuel's
`fuel_emissions_multiplier` is 0, so nothing is vented. **A spent cell does come
out**, and the art shows where: the chute to the lead bin.

---

# 3. Visual Design

## 3.1 Design Concept

A **cell-fed power plant on a 5×5**, one chain from cell to wire that the player
can follow. Cells go in through two charging ports on the carousel's lead
loading hood, the two fuel slots. The great turntable, the west half of the
building, carries them round. The collector head reads each cell's charge as it
passes. At the pick pocket a twin-hoist crane takes the fresh cell and leaves
the spent one, runs east and swaps them in the lead crucible's served well. In
the crucible the cells stand between copper collector plates, the plate rack;
thermionic tubes on its east flank turn its heat to current. Plates and tubes
feed the DC bus to the switchgear; the rotary converter makes AC, the
transformer steps it up, armoured trunks take it out at the south-west. Spent
cells leave the hood by a chute into a lead bin. A coolant pump, a radiator and
an expansion tank cool the crucible jacket and the tube caps.

**The anti-read.** It must not read as a steam engine: no pistons, connecting
rods, crank or flywheel, no boiler, chimney or exhaust, no steam, smoke or fire,
no orange heat. A turning rotor or converter is fine. This is the art's choice;
the Core's thin atmosphere would allow fire, so the reason is the read, not the
air. It must also not look like the Siderane turbine or the Reaction Plant.

## 3.2 Key Visual Features

* The **carousel**: a lead-clad, banded drum carrying an indexing turntable of
  eight lead-capped cell pockets, its loading hood with two charging ports, a
  geared drive motor whose pinion turns the ring gear.
* The **collector head** over the pocket before the pick, with a bolted
  bullseye port.
* The **twin-hoist crane**, ochre, on rails on the north shield housing and on
  posts along the crucible's south face.
* The **lead crucible** holding the plate rack, seen through a glazed slot, and
  the served well with a lid that lifts while the crane works it.
* **Five thermionic tubes** on the crucible's east flank: glass, a lit emitter
  low in each, finned copper collector caps.
* The **rotary converter** along the south: open commutator, brush gear,
  coupling, AC machine, exciter.
* The **switchgear** and the DC bus tray in the south-east; the **transformer**
  and armoured **trunks** in the south-west.
* **Cooling**: the pump and hoses, the radiator on the north shield housing, the
  expansion tank in the north-east corner.
* **Clutter**: gas bottles, valves, barrels, ladders, a cable tray, stains.

### Signature Feature

The crane's cell swap: a fresh cell lifted from the carousel and lowered into
the crucible while the spent one comes back. It is the cell-to-wire chain made
visible, and the one motion a player stops to watch.

## 3.3 Colour Palette

(base colours from `r7_kit.py`, worn by `worn_paint()` as the Reaction Plant's
finish)

| Role | Hex | Where |
| ---- | --- | ----- |
| Lead (holds the isotope) | `#6A6258`, new lead `#7A7266` | carousel drum and table, crucible, loading hood, bin |
| Grey paint | `#6E6A62` | shield housing, radiator, tank, AC machine, cabinet |
| Teal paint, the radiant family's roofs | `#3E6462` | housing roof, tank top |
| Ochre paint | `#9C7426` | crane, ladders |
| Weathered green | `#4E6034` | motors, switchgear cabinet |
| Cream paint | `#ACA084` | transformer, exciter |
| Oxide red | `#6E2C1E` | pump |
| Dark steel | `#3E3934` | decks, frames, foot rings |
| Copper | `#94592C` | collector plates, tube caps, bus |
| The isotope's light | `#1F63FF` → `#73ADFF`, through `tools/blender/radiant.py` | port, slot, tubes, well |

**The light is one light in four openings**: the bullseye port, the plate-rack
slot, the tube emitters and the well's mouth. Each is a bright core grading to
deep blue at the rim, seen through glass with a thin highlight and a dark bezel,
with the plates, cells and tube grids dark against it. No moving pattern inside
any opening; only its strength moves (§6). `radiant.py` with its disc, slot and
tube shapes, flicker 0, round 7's strength curves in place of its pulse. Blue
share 0.7 % of the building at round 7. **Orange** is kept for copper and paint;
nothing glows orange.

---

# 4. Factorio Visual Style

Vanilla clutter, FFF #146 contrast, FFF #350 outline, readable at 1x. **A
building, not a deck**: footprint cover 94 % and no flat base; the corners
broken by equipment, unevenly (round 7: NW 71.9 %, NE 96.1 %, SW 88.1 %,
SE 63.7 %). **Rise** 0.47 tiles above the north edge, under the fusion
reactor's 0.66. **Finish**: the Reaction Plant model's, tonal p50 ~75–81, p95
in vanilla's range. Compared beside vanilla's steam engine, steam turbine and
fusion generator, the Reaction Plant and the Siderane turbine.

---

# 5. Building Orientation

**One picture for all four directions.** The generator has no fluid box and no
facing port, and `Animation4Way` loaded as a single animation applies to every
direction. The model declares `directions="one"`. No pipe sheets: the
turning-ports rule applies only to a model with ports.

---

---

# 8. Connections

| Connection | Where | Shown as |
| ---------- | ----- | -------- |
| Fuel in | any adjacent tile, by inserter | the two charging ports on the loading hood |
| Spent cell out | any adjacent tile, by inserter | the chute and the lead bin, west face |
| Electric out | no connector; poles reach it | the armoured trunks, south-west |
| Fluids | none | no pipe flange anywhere |

The hood and the bin are honest decoration, as a furnace's are: they say where
the cell goes and comes out without constraining where an inserter stands.
Every pipe and hose on the building is its own coolant plumbing, not a
connection.

---

---

# 6. Sprite Assets Required

| Slot | What it is |
| ---- | ---------- |
| `animation` | the working loop, 32 frames: the plate, the moving parts, the glow |
| `idle_animation` | chosen by Liam after the spike (below) |
| Shadow | a layer of each |
| Remnants | the machine's own wreck, rendered at the model stage, as the Siderane turbine's |

**The loop: 32 frames, one crane cycle** (from `r7_sheets.py`):
frames 0–4 hoist A takes the fresh cell; 4–10 hoist B sets the spent cell in
the pocket; 10–16 the bridge runs to the crucible; 16–26 B takes the spent cell
from the well and A sets the fresh one; 26–32 the bridge runs back. The
carousel indexes one pocket in frames 11–20 and its drive pinion turns with it.
The well's lid is up in frames 15–27. **Pace:** round 7's signed-off 1x GIF,
70 ms a frame; the model task sets `animation_speed` to match it. That is the
reference pace: the prototype's `perceived_performance` stays, so the engine
speeds the loop up and slows it with output. The commutator, the couplings and the
gauge needles turn; the status lamps light. The commutator turns half a turn a
loop.

**The light (glow layer):** tubes swell in turn along the row, twice a loop,
70–100 %; the bullseye port holds steady and dims to 50 % while the table
indexes; the slot breathes ±8 %; the well's mouth rises over three frames as
its lid lifts (hoist B covers it at this camera).

**Flicker, as signed off**: the commutator has 8 dark copper bars; the ring
gear half round 6's teeth; no hazard ticks on the bridge. Strobe 5.6 % at 1x,
moving share 31.6 %. The model's strobe must be ≤ 5.6 %.

**Idle: test first, then Liam chooses.** The API says `idle_animation` plays
while the generator is inactive and must have the same frame count as
`animation`. What the engine shows is not yet known, so a spike at the
model/wiring stage finds what it draws with no fuel, and when fuelled with no
demand. Liam chooses the idle look after; this spec does not set it.

---

# 7. Layer Structure

| Layer | Draw as | Animated |
| ----- | ------- | -------- |
| Plate: everything that does not move, openings dark | normal | no |
| Shadow | `draw_as_shadow` | no |
| Moving parts: carousel table, crane, well lid, commutator, couplings, pinion, gauges | normal | 32 frames |
| The isotope's light | `draw_as_glow`, from `radiant.py` | 32 frames, strength only |
| Status lamps | as the model packs them | on while working |

**The light is rendered apart from the lit glass in the plate**, with
everything in front of it held out, so the plates, cells and grids cut it
exactly. Nothing but the isotope's four openings is in the glow layer.

---

# 12. Image Processing

`tools/blender/render.sh <model> <out> --ports --icon` renders, packs and
checks every layer; `--ports` confirms there are no ports. Highlights rolled
off above 236 to 244 (not light passes); glow cropped to 99.9 % of its light;
leave about a tile of canvas round every radiant opening so the glow's tail is
whole (`radiant.py`). Measured with `factorio-art-measure`.

---

# 13. Sprite Dimensions

64 source px a tile, scale 0.5. Footprint 5×5. The canvas, frame size and
shift are read off the packed sheets at the model stage and written here then.

---

# 14. File Structure

`concept/radiant-generator/model/`: the model script and its renders.
`graphics/entity/radiant-generator/`: the sheets as `pack.py` names them;
the old `base-vertical*`, `base-horizontal*`, `glow-*` files removed at wiring.
`graphics/icons/radiant-generator.png` from `--icon`.

---

# 15. Factorio Prototype

```lua
gen.animation      = { layers = { plate, shadow, moving parts, glow } }  -- one for all directions
gen.idle_animation = -- chosen after the spike (§6); same frame count
```

Changes at wiring: the 5×5 boxes, `idle_animation`, its own remnants for
`corpse`, and a death explosion like the Siderane turbine's: fireball and
sparks, no smoke. **Working sound:** its own, designed in the model task; the
steam engine's goes.

---

# 17. Visual QA Checklist

- [ ] Reads as a cell-fed generator; no steam-engine part (§3.1)
- [ ] The chain can be followed: hood, carousel, crane, crucible, tubes, converter, transformer, trunks
- [ ] Cover ≥ 92 %, corners broken, rise ≤ 0.66, measured
- [ ] Light only in the four openings; blue share near round 7's 0.7 %
- [ ] Strobe no higher than round 7's 5.6 % at 1x
- [ ] Idle as Liam chose after the spike (§6)
- [ ] Tonal p50 ~75–81, no clipped pixels
- [ ] In game: sits on its 5×5, selection box matches, reads on the Core and a platform, fuelled and unfuelled

---

# 18. Final Asset Checklist

- [ ] Model signed off by Liam
- [ ] Sheets packed by `render.sh --ports --icon`; §13 filled in from them
- [ ] Its own working sound, from the model task
- [ ] Prototype: 5×5 boxes, `animation` and `idle_animation`, remnants, death explosion
- [ ] `./tools/check-data-stage.sh` passes
- [ ] Client test, fuelled and unfuelled; Liam signs off in game

# 19. Design Notes / Iteration History

| Round | Asset | What came back | Verdict | Fix asked for |
| ----- | ----- | -------------- | ------- | ------------- |
| 1 | sheet | The machine landed first time and the anti-read held completely — radiator fin banks dominate the silhouette, the shielded throat shows light only through its slots, and there is no piston, flywheel, boiler, chimney, exhaust, steam, smoke or warm colour anywhere. Fuel hopper carries exactly two loading ports, matching `fuel_inventory_size = 2`. Palette strip carries the §3.3 hexes. **But the VERTICAL and HORIZONTAL hero panels showed the same orientation**, so the sheet did not actually show the two directions §5 needs — the same turntable-versus-rotation trap the Vent Pump spec warns about. | **Machine accepted; direction panels rejected** | Two fixes: (1) HORIZONTAL must be the same machine rotated a quarter turn on the ground under a fixed camera, long axis running across the screen rather than up it; (2) the sheet titled itself RADIANT POWER SOURCE, should be RADIANT GENERATOR. |
| 2 | sheet | Both fixes landed. VERTICAL is now tall and narrow with the trough running away from the viewer, HORIZONTAL is wide and short with it running across — the same machine under the same camera, rotated a quarter turn, which is what §5 needs. Title corrected. The building itself came back unchanged. | **Accepted — `concept/v2-sheet.png` is the locked design** | None. |
| Options 1 | five options | Liam: "Look at the nuclear and fusion reactors for inspiration, the radiant reactor options seem a little boring and flat in comparison, we need opportunity for some impressive animations." | none picked | a showpiece |
| Options 2 | five animated options | Liam: "I like both the gyre and the arc spire, i think the generator should be 5x5." | A and C combined | 5×5 |
| Options 3 | three combinations | Liam: "the reactor needs to look bulkier still. A reactor needs cooling etc. See the current factorio reactors." | reworked | bulk, cooling |
| Options 4 | three, bulked | the Gyre Spire chosen, 2026-10-11 | then set aside | — |
| Options 5 | ten generators | Liam: "As this is supposed to be a generator and not a reactor i think we rethink the model. It still should contain animated parts and be up to the core mods standard. Create 10 suggestions. They can be up to 5x5." Then: "For the generator combine features of 3, 4 and 7 but make them a lot bulkier. Not much ground should be visible on the area it covers as its a building." | 3, 4, 7 combined | — |
| Options 6 | three combinations | Liam: "use one but the blue textures look out of place and could be improved." | the Carousel Foundry, 2026-10-12 | the blue |
| Options 7 | the Carousel Foundry refined | cover 94 %, rise 0.47, blue 0.7 %, strobe 5.6 % | Liam: "Sign off", 2026-10-19 | none |
| Spec | rewrite | the Carousel Foundry described for the model | Liam: "Agreed to all the drafts", 2026-10-20 | none |

# 20. Decisions

1. Footprint: "5×5, reactor boxes" (collision ±2.2, selection ±2.5).
2. Light: "radiant.py, no flicker" (flicker 0, round 7's strength curves).
3. Idle: "Test first, then ask": a spike finds what the engine shows with no
   fuel and fuelled with no demand; Liam chooses the idle look after.
4. Commutator: "Half a turn" per loop.
5. Strobe: "≤ 5.6 %".
6. Wreck: "Own wreck, like turbine": own remnants; fireball and sparks, no smoke.
7. Sound: "Sound: in model task".
8. Locale: "Text: reword now" (§1 Locale above).
9. Render: "Keep --ports".
10. Animation speed: "Match the 1x GIF" (set in the model task to round 7's
    signed-off pace, 70 ms a frame).
11. Descriptions: "Cut entity's last line" (the entity description ends
    "…each one handed back spent."; the item description is unchanged).
12. Pace under load: "Engine varies it" (the prototype's `perceived_performance`
    stays; the GIF's pace is the reference pace).
