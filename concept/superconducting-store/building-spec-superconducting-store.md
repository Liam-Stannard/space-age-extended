# Superconducting Store — building spec

Superconducting Store. Holds 500 MJ of electricity and takes or gives it at up
to 20 MW.

---

# 1. Facts

- **Name:** Superconducting store
- **What it does:** stores electricity, up to 500 MJ, and charges or discharges
  at up to 20 MW.
- **Size and directions:** 2 × 2, 1 direction.
- **Where it can be built:** anywhere, platforms included; it has no surface
  conditions.
- **Power:** stores up to 500 MJ; takes and gives up to 20 MW; tertiary
  priority.
- **Inputs and outputs:** electricity only.
- **Speed:** charges and discharges at up to 20 MW.
- **Cost:** 10 superconducting winding, 2 accumulator, 20 steel plate; 20 s.
- **Weight:** 20 kg, stack of 20.
- **Unlocked by:** Superconducting winding.
- **Art:** signed off (date not recorded).

---

# 3. Visual Design

## 3.1 Design Concept

A cryostat: a squat armoured drum with a superconducting ring buried inside it
and cold plumbing round the outside. The cooling is the expensive part, and it
shows. It must not be mistaken for an accumulator (no flat cabinet, no glowing
front panel, no charge bar) or for a fluid tank (no plain drum with pipes).

## 3.2 Key Visual Features

Three or four parts read at 2 × 2; no more.

* A squat, armoured **cylindrical cryostat**, wider than it is tall, banded
  with insulation wrap. It spans exactly 2 tiles, so a row of stores touches and
  never overlaps.
* The **storage ring**: a recessed channel running unbroken round the upper
  third, with real depth, lips and shadow. It is the only place light appears.
* **Cold plumbing**: two frost-jacketed feed lines entering at opposite sides,
  each with a pale condensation collar where it meets the armour.
* A **heavy busbar terminal block** on one side, oversized for the footprint,
  with thick armoured cabling.
* **Frost** on the lower third only; the top runs warmer.

### Signature Feature

The continuous lit ring. It reads from above at 2 × 2, and the light travels
round it rather than filling a bar, as a current circulates in a loop.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Armour and insulation wrap | `#4A463F` → `#6E685C` | the drum body |
| Bolt rings and collars | `#B9B4A8` | banding, pipe entries |
| Ring light | `#9FC4E8` → `#E8F4FF` | the ring channel only |
| Cold plumbing and frost | `#B8D8E8` | feed lines, lower third |
| Busbar terminations | `#8A5A32` | the terminal block |

The ring light is the superconducting winding's blue-white, so the winding and
the store read as one material.

One glow: the ring light. It is always lit, and a sweep of light runs round it
while the store charges or discharges. Nothing else is lit: not the frost, not
the busbar, and there are no status lamps.

No painted area is chosen yet.

---

# 4. Factorio Visual Style

Style reference: vanilla's nuclear reactor or chemical plant, for finish and
scale. Never the accumulator.

---

# 8. Connections

No pipes and no item connections; the feed lines are art only. Power poles
connect to it by their supply area, so no electric connector shows. Circuit
wires connect to it.

---

# 9. Working Animation

| # | Step | Entries | Ticks | What moves | Ease | Accent |
|---|---|---|---|---|---|---|
| 1 | Charging | charge sheet 1–20 | 20 | an arc of light grows clockwise from the north of the ring until it closes into a full circle | even | — |
| 2 | Discharging | discharge sheet 1–20 | 20 | the same arc, anticlockwise, at a little over half the brightness | even | — |

Charge and discharge are separate sheets, played while power flows in or out,
so the loop is not tied to a craft. The sweep runs on 30 ticks after charging
stops and 60 after discharging stops. The ring is always lit at 90 %
brightness, full or empty, and the sweeps brighten it. No working sound.

---

# 14. Icon

The plate, scaled down: the drum and its busbar block. The ring must read at
small sizes.
