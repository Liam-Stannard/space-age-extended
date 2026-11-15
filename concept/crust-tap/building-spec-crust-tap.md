# Gas Pump — building spec

Gas Pump. Draws gas from a vent: hydrogen or helium-3.

---

# 1. Facts

- **Name:** Gas Pump
- **What it does:** pumps gas from a vent.
- **Size and directions:** 3 × 3, 4 directions.
- **Where it can be built:** on a hydrogen or helium-3 vent, where gravity is
  45 or more, so only the Core.
- **Power:** none.
- **Inputs and outputs:** no input; one gas output on the north face.
- **Speed:** mining speed 1; how much it pumps depends on the vent
  (`design/04-the-core.md`).
- **Cost:** 5 steel plate, 10 iron gear wheels, 5 electronic circuits, 10 pipe;
  5 s.
- **Weight:** 20 kg, stack of 20.
- **Unlocked by:** Hydrogen extraction.
- **Art:** signed off (2026-10-27).
- **Remnants and explosion:** TODO.

---

# 3. Visual Design

## 3.1 Design Concept

An oilfield gas engine and compressor: a flywheel and crank drive two
compressor cylinders, with two engine cylinders, a gauge board and a sight glass
showing the gas. The gas can be followed from the vent, up a scrubber, through
the cylinders and out. The engine is art only: the pump needs no power. It must
not look like vanilla's offshore pump.

## 3.2 Key Visual Features

* The **flywheel**, in the casing's green, with a yellow balance weight between
  two spokes.
* Two opposed **compressor cylinders**, with bare-steel crossheads, each with a
  yellow slipper.
* The **suction scrubber** over the vent, the tallest part.
* A **lubricator** driven off the flywheel hub.
* The **gauge board** (west), the **sight glass** (east), the lube tank and
  panel (north-east) and crated spare liners.

### Signature Feature

The flywheel and its yellow weight: one bold mark a turn, so a player sees the
pump working from across the landing.

## 3.3 Colour Palette

It shares the Vent Pump's finish; the two are told apart by shape and by what
moves.

| Role | Hex | Where |
| ---- | --- | ----- |
| Green | `#5C7A2C` | casing, cylinders, flywheel web |
| Yellow | `#A8841E` at most | balance weight, crosshead slippers, regulator |
| Cream | `#C0A676` | lube tank, gauge board |
| Grey | `#86704C` | discharge bottle, panel |
| Hydrogen in the glass | `#A8D929` | the hydrogen vent's sight-glass tint |
| Helium-3 in the glass | `#B6A6C8` | also the helium-3 vent's map colour |

Nothing glows: the gas in the glass is paint. Idle, the glass shows empty.

---

# 4. Factorio Visual Style

Style reference: vanilla's pumpjack, for the oilfield look and the camera.

---

# 8. Connections

One gas outlet, from the discharge bottle at the middle of the north face. It
turns with the machine: north {0, −1}, east {1, 0}, south {0, 1}, west {−1, 0}.
It ends in an open pipe mouth behind a flange, flush with the tile edge, so a
pipe can join it. No electric or item connections.

---

# 9. Working Animation

| # | Step | Entries | Ticks | What moves | Ease | Accent |
|---|---|---|---|---|---|---|
| 1 | Pumping | 1–24 | 60 | the flywheel turns once; both crossheads go out and back, opposed; the engine rockers nod; the lubricator works; the three gauge needles kick on the strokes; gas drifts in the sight glass, tinted by the vent | even | — |

Idle, everything stops where it is and the glass shows empty.

---

# 14. Icon

Rendered from the model. The flywheel and its yellow weight must read at small
sizes.
