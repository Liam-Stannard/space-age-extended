# Vent Pump — building spec

Vent Pump. Lifts molten kamacite out of a kamacite vent with helium-3.

---

# 1. Facts

- **Name:** Vent Pump
- **What it does:** draws molten kamacite from a kamacite vent. Each operation
  uses helium-3.
- **Size and directions:** 3 × 3, 4 directions.
- **Where it can be built:** on a kamacite vent. It has no surface limit of its
  own, but kamacite vents are found only on the Core.
- **Power:** 90 kW electric.
- **Inputs and outputs:** helium-3 in on the south face; molten kamacite out on
  the north face. Nothing uses molten kamacite yet (TODO, "Decide what the
  kamacite vent is for").
- **Speed:** mining speed 1, one operation a second. Each operation uses 10
  helium-3; how much molten kamacite it gives depends on the vent
  (`design/04-the-core.md`). 2 module slots.
- **Cost:** 10 steel plate, 5 electric engine units, 5 processing units, 10
  pipe; 5 s.
- **Weight:** 20 kg, stack of 20.
- **Unlocked by:** Vent tapping.
- **Art:** signed off (2026-10-21); the fittings and wire-post mount signed off
  2026-10-27.
- **Remnants and explosion:** TODO.

---

# 3. Visual Design

## 3.1 Design Concept

A gas-lift tower. Helium-3 is blown into the molten kamacite at the foot of a
tall iron tower, and its bubbles carry the molten kamacite up a glass riser.
From far off it reads as a glass tower full of molten kamacite, fed from below.
It is not a beam pump and must not read as a pumpjack: the lift has no moving
parts, and nothing nods or strokes. What moves is the helium's kit.

## 3.2 Key Visual Features

* The **tower**: a tall, narrow iron shaft over the vent, just north of centre,
  on a refractory footing. It is banded every 0.42 of its height, with a ladder
  up its west side. A slot down its south face holds the **glass riser**:
  orange molten kamacite with helium bubbles climbing it.
* The **head tank** on top, rising above the north edge, where the helium
  breaks out. It has a window onto the molten kamacite and a **float chamber**
  whose lever rocks. A lagged **downcomer** carries the molten kamacite down to
  the north outlet.
* The **helium line**: in at the south nozzle, through the stop valve and the
  turning **flow meter**, past a tee and a gauge, through the **sight glass**,
  down to the **sparger ring** round the tower's foot.
* The **recovery loop**: down the tower's east side to the **compressor**
  (south-east), its coupling turning; west over the inlet to the **receiver**
  (south-west); back into the line at the tee.
* The **units round the foot**, each on its own footing, with no deck. Facing
  north: the control house (north-east), the switchgear (east), the skimmings
  bin (north-west), two gas bottles and a tool chest (west). They break each
  corner at different heights.

### Signature Feature

The helium seen at work. Violet helium in the sight glass drops and flushes
pink at each charge, and its bubbles carry the orange molten kamacite up the
glass riser.

## 3.3 Colour Palette

Finished to the bars in standards.md (Finish).

| Role | Hex | Where |
| ---- | --- | ----- |
| Iron | `#6A5642` | the tower |
| Dark iron | `#523F33` | the head tank |
| Oxide red | `#963220` | compressor, skimmings bin |
| Ochre | `#BC8624` | ladder, a gas bottle |
| Green | `#5C7A2C` | meter transmitter, compressor motor, a gas bottle |
| Cream | `#C0A676` | control house |
| Grey | `#86704C` | receiver, injection controller, switchgear |
| Bare steel and nickel | satin | bands and the helium intake; no glint reaches white |
| Helium line | grey-violet, bands `#84769A` | the lagged helium line and its ID bands |
| Molten kamacite (glow) | `#D96B29` → crest `#F89A50` | the glass riser and the head-tank window, while working |
| Helium (glow) | violet `#9C86CC`, flushing peach-pink `#F2A296` | the sight glass only, while working; the flush at each charge |
| Green lens (glow and halo) | `#46F05A` | the control house; lit while working, and in low power |
| Amber lens (glow and halo) | `#FF9A12` | the switchgear; lit only when the helium is missing |
| Embers (glow) | molten kamacite's orange | sparks off the skimmings bin, while working |
| Ground light | `#FF7A2E` | round the tower's foot, in the dark, while working |

Each lens is a glow, seen by day and by night, with the game's own small light
as a halo in the dark. Each lens has its own colour; unlit, it is the plate's
dark glass. The brightest paints are held a step down so none clips.

---

# 4. Factorio Visual Style

* **Pumpjack:** the same 3 × 3 over a fluid resource, for scale.
* **Chemical plant:** a 3 × 3 built up in height, with clutter and pipes; and
  four directions, each its own arrangement.
  * In every direction the tower, its riser, the head tank with its window and
    float chamber, the ladder and the sparger ring face the camera.
  * The plumbing and the units turn with the connections. The sight glass, the
    meter's dial, the two gauges and the receiver's plate face the camera
    wherever they stand.
  * Facing south, the sight glass stands east of the tower and the tool chest
    takes its place.
  * West is east mirrored; the tower is not.
* **Foundry:** molten metal seen inside the building, and its height: the tower
  rises at most 0.78 tiles above the north edge.

---

# 8. Connections

* **Helium-3 in:** the middle of the south face, {0, 1}.
* **Molten kamacite out:** the middle of the north face, {0, −1}.
* Both turn with the machine and always sit on opposite faces. The outlet is
  north {0, −1}, east {1, 0}, south {0, 1}, west {−1, 0}; the inlet is the face
  opposite.
* Each is a flanged fitting set into the wall, square to the edge, at
  assembler 3's pipe height (z 0.42). The pipe picture is only the fitting's
  open mouth past the edge. Unconnected, vanilla's pipe cover sits over the
  mouth. A north mouth is drawn behind the building.
* The two read apart: the intake is bare steel turning at once into the
  grey-violet helium line; the outlet is the end of the lagged downcomer from
  the head tank. The violet and the orange are a second cue.
* **Wire post:** on the control house. Facing north, on a bolted pad at the
  front of its roof; in the other three, on a shelf on the wall that faces the
  camera.
* No item connections.

---

# 9. Working Animation

24 entries at animation speed 0.2: a 120-tick loop with two charges, one charge
an operation.

| # | Step | Entries | Ticks | What moves | Ease | Accent |
|---|---|---|---|---|---|---|
| 1 | Between | 1 | 5 | as step 3 | even | — |
| 2 | First charge | 2–9 | 40 | the meter races; the line gauge swings; the sight glass drops and flushes pink; the riser's bubbles climb faster; the float lever rocks; the coupling turns; the receiver's gauge swings | eased | entry 2: cold breath off the stop valve, purge puff off the float chamber; no sound |
| 3 | Between | 10–13 | 20 | the sight glass refills and fades to violet; the bubbles slow but keep climbing; the coupling turns | even | — |
| 4 | Second charge | 14–21 | 40 | as step 2 | eased | entry 14: as step 2 |
| 5 | Between | 22–24 | 15 | as step 3 | even | — |

Idle, everything is still and nothing is lit, except the amber lens when the
helium is missing. An unpowered, dry pump shows no lens.

The effects, each only while working and faded out on stop:

* **Wisp:** a fume lit by the molten kamacite, off the head tank's gas
  offtake. Its own loop of 32 entries at speed 0.25, drawn over the building.
* **Embers:** sparks rising off the slag in the skimmings bin. 48 entries at
  speed 0.4, two to each machine entry, in step with the loop. Any part nearer
  the camera hides them.
* **Ground light:** the molten kamacite's orange on the ground round the
  tower's foot, radius 2.5 tiles. Seen only in the dark.
* **Cold breath:** off the stop valve at each charge. None facing south, where
  the valve stands behind the tower.
* **Purge puff:** a violet-grey puff off the float chamber's cap at each charge.

---

# 14. Icon

Rendered from the model: the tower facing north, working. Nothing is dropped
at small sizes.
