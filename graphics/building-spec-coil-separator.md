# Factorio Building — Art & Implementation Specification

**Coil Separator.** First draft — a brief, enough to commission and judge a
concept sheet. Not a specification: §6, §12 and §13 stay open until a sheet is
approved and a canonical plate has been measured.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **draft — `concept/v1-sheet.png`**, not locked |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3 | blocked on 0 |
| 2 | Idle plate (unlit) | portrait 2:3 | Same machine, field dead | blocked on 1 |
| 4 | Glow plate | portrait 2:3 | Differenced against stage 2 | blocked on 2 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

---

# 1. Building Overview

**Building Name:** `Coil Separator`
**Internal Prototype Name:** `sae-coil-separator`

**Building Type:** `assembling-machine`, built fresh.

**Purpose:** Magnetic beneficiation on a world with no magnetic field. It pulls
**schreibersite concentrate** — the Core's only phosphorus — out of crushed
kamacite, using a field it generates itself from a coil the player has already
learned to build.

**Why it matters:** it is the payoff of the mod's best joke. `magnetic-field = 0`
refuses the electromagnetic plant as a *manufactured* item, so the first
separation on the Core has to be done in an imported plant — the dead dynamo felt
as a supply problem, hours before the Ignition Array explains it. This building
is how the player stops importing: they build the field themselves, out of the
same coil the endgame is made of.

**Locale:** *"Makes its own field, because the planet has none to lend."* /
*"Separates by magnetism where there is no magnetism. The coil inside it is the
same one the Array is built from, which is the point."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 3×3 (`collision_box {-1.4,-1.4},{1.4,1.4}`) |
| Directions | 1 |
| Crafting category | `sae-separation` |
| Energy | **Very heavy: 2.5 MW.** Generating a field from nothing is the cost |
| Surface conditions | `pressure` ≤ 9 — the Core and platforms |
| Module slots | 3 |
| Recipe to build it | includes **1 coil assembly** — see below |

**Its own recipe is the mechanic.** Building a Coil Separator costs a coil
assembly, which is two stages below the Field Coil Segment. The player spends
endgame material to make more endgame material, which is
`06-core-production-tree.md`'s *"using the thing you are building to build more of
it"*, made literal rather than described.

### Why it is not a reskin

The electromagnetic plant is manufactured under a magnetic-field condition and
placed anywhere. This is the inverse: manufactured anywhere, placed only where
there is no field to borrow, and priced in the mod's own endgame currency. It is
also the only building in the game whose ingredient list is an argument.

---

# 3. Visual Design

## 3.1 Design Concept

A machine built around a hole. The centre of the building is an open **coil
throat** — a heavy toroidal winding on its side, with the ore stream passing
through it — and everything else is the apparatus needed to keep that throat fed
and cooled.

**The anti-read is the electromagnetic plant.** Vanilla's is a clean lab-white
box with a violet field effect, and copying it would say "you imported this".
This machine is heavy, dark and visibly strained: the field is expensive here.

## 3.2 Key Visual Features

* A **coil throat** — the signature. A thick copper-brown toroid mounted
  vertically, its aperture facing the camera, with the ore path running through.
* **Two splitter chutes** below the throat, angled apart, where the stream
  divides.
* **Bus bars** — heavy flat conductors entering the throat from both flanks,
  visibly overbuilt.
* **Cooling fins** on the throat's outer face.

### Signature Feature

**The throat's field glow, seen only through the aperture.** A cold blue-violet
that lives strictly inside the ring and never spills onto the chassis. Fulgora's
lightning and this are the only violet in the mod's palette and they should not
be confused — this one is steady, not flickering.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Chassis | `#4A463F` → `#6E685C` | the mass of the building |
| Coil windings | `#8A5A32` → `#C88A4A` | the toroid only |
| Bus bars | `#8A8580` | flanks |
| Field glow | `#6A5AC8` → `#B0A8F0` | inside the aperture only |
| Concentrate | `#7A7060` | the chutes |

---

# 4. Factorio Visual Style

3×3 and mid-height. The throat's aperture must survive the 45-degree camera — an
opening drawn as a perfect circle will read as an ellipse and lose its centre, so
it should be drawn already foreshortened. Style reference to attach: the
**foundry**, cropped and upscaled, for weight and finish. **Do not attach the
electromagnetic plant**; it is the anti-read.

---

# 5. Building Orientation

* [x] North only

**Direction count:** `1`.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Crushed kamacite in | any adjacent tile | inserters, unconstrained |
| Concentrate / tailings out | any adjacent tile | one output inventory |
| Electric | no visible connector | poles reach it wirelessly |
| Fluids | none | no fluid box; no pipe flange in the art |

---

# 11. Generation Requirements

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio
Space Age industrial machine, every panel drawn from the game's characteristic
45-degree top-down perspective. The machine is a heavy dark three-by-three
magnetic separator standing on an airless metallic world. Its centre is a
thick copper-brown toroidal coil mounted vertically with an open aperture
facing the viewer. Heavy flat pale-grey bus bars enter the coil from both
flanks. Cooling fins on the coil's outer face. Two empty angled splitter
chutes of different widths leave the base below the coil. A steady cold blue-
violet glow appears only inside the aperture and never on the chassis. Dark
grey-brown armour. No white laboratory panels, no flickering electricity, no
arcs, no smoke, no flame. Panels: main view, front elevation, side elevation,
a detail of the empty coil throat and the two chute mouths, and a lit/unlit
pair. Title the sheet COIL SEPARATOR. Draw no loose material anywhere: no ore,
powder, fibre, grit, debris or product on the ground, in bins, at chutes, on
trays or spilling from the machine. Factorio machines never show what they
make, so every chute, port, bin and tray is drawn as empty machinery. Every
pipe connection must run down to ground level and stop flush at the edge of
the tile footprint; no pipe may end in mid-air and none may leave the top of
the building. Nothing may extend past the tile footprint, pipework included,
and the tile-grid panel must show the whole machine inside the grid with no
overhang.
```

---

# 15. Factorio Prototype — sketch

```lua
{
  type = "assembling-machine",
  name = "sae-coil-separator",
  crafting_categories = { "sae-separation" },
  crafting_speed = 1,
  energy_usage = "2500kW",
  energy_source = { type = "electric", usage_priority = "secondary-input" },
  surface_conditions = { { property = "pressure", max = 9 } },
  module_slots = 3
}
```

---

# 16. Icon

The toroid seen square on, aperture open, with the violet field inside it and the
ore stream splitting below. Must read at 32 px as *"a ring with something passing
through"*.

---

# 20. Open questions

- **Phosphorus must have exactly one source.** `06-core-production-tree.md` T1
  gives schreibersite to magnetic separation of crushed kamacite. The **Dross
  Classifier** brief could also plausibly yield it. If both do, neither is
  scarce and the flux stops gating anything. Decided here: **schreibersite comes
  from this building only**; the classifier recovers fines instead.
- **When does it unlock?** It must land *after* the imported electromagnetic
  plant has been the only option for a real stretch of play, or the joke never
  fires. Tier 3 of the ladder at the earliest.
- **Does it need the imported plant to exist at all?** If the first separation
  recipe runs in an electromagnetic plant and the second in this, the two need
  different recipes or different categories, or the player will simply wait.
