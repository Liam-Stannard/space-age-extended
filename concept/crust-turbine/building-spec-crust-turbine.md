# Hydrogen Turbine — building spec

Hydrogen Turbine. The Core's first power: it burns hydrogen from a Gas Pump.

---

# 1. Facts

- **Name:** Hydrogen Turbine
- **What it does:** burns hydrogen to make electricity.
- **Size and directions:** 3 × 5, 2 directions.
- **Where it can be built:** pressure 9 or less, so today the Core and
  platforms; it must become Core-only (TODO, pressure 200).
- **Power:** makes up to 1.8 MW.
- **Inputs and outputs:** hydrogen only, 9 a second, through a connection at
  each end; turbines chain end to end.
- **Speed:** full output at 9 hydrogen a second.
- **Cost:** 20 steel plate, 10 pipe, 20 iron gear wheels; 6 s.
- **Weight:** 40 kg, stack of 20.
- **Unlocked by:** Hydrogen extraction.
- **Art:** being redone.
- **Remnants and explosion:** Complete.

---

# 3. Visual Design

## 3.1 Design Concept

It burns hydrogen and should look it: a hot machine, with flame or glow where it
burns.

## 3.2 Key Visual Features

* A **long low body** on the 3 × 5, filling its depth: heavy collars, a deep
  burner housing, a generator can as wide as the collars, with lagged runs, a
  cable tray, a terminal box and braces round them.
* A **burner stage** at one end, where the hydrogen burns, with a flame or glow,
  and a high and a low pressure gauge either side of it.
* An **inline rotor casing** down the middle, smooth and pressure-rated.
* **Two flanges, one at each end**, identical, because gas passes straight
  through and turbines chain end to end.
* A **generator can** at the far end from the burner stage, plainly electrical.

### Signature Feature

**Porcelain on the machine that makes the power.** Three glazed bushings on the
generator can, copper bus down from them to the terminal box, and a gauge pair
reading the pressure across the burner stage: the output is plainly electricity.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Body and casing | `#4A463F` → `#6E685C` | the mass of the building |
| Generator can | `#5A5047` | the electrical end |
| Flanges and fittings | `#8A857C` | both ends |
| Copper and brass | `#8A5A32` → `#C88A4A` | bus runs, terminal box, flange faces |
| Porcelain | `#B4AA94` | the three bushings only |
| Lagging | `#5E584C` | the balance line |
| Burner glow | pale blue, set in the art round | the burner stage only |

One glow, at the burner stage. The status lens is the only other light.

---

# 4. Factorio Visual Style

Tier 0, the foothold: riveted plate, cast housings, bolted flanges, weld seams
and honest wear, like the Drop Crusher and the Ballast Drill. Style reference:
vanilla's steam turbine, for finish and scale only.

---

# 8. Connections

The two end flanges are identical. Each sits square to its end and stops flush
at the middle of the tile edge, so a row plainly chains. No electric connector
shows, and no inserter ever touches it.

---

# 9. Working Animation

A rotor turning behind a grille, and the burner's glow while it runs.
