# Factorio Building — Art & Implementation Specification

**Coil Separator.** The design is locked: **option D, the Cold Plant**, chosen
2026-09-08 from five drawn against each other. The decision record is
`coil-separator-options/`, the sheet is `concept/adopted/D-sheet.png`, and the
four rejected designs are gone. §6, §12 and §13 stay open until a canonical plate
exists and has been measured.

**The adopted design changed what this building looks like.** It is no longer a
machine built around an open coil throat: the coil is *buried*, and what stands
on the tile is the refrigeration plant a magnet needs on a world with no field to
borrow. §3 and §16 are rewritten against that; §1, §2, §8 and §20 are unchanged,
because none of them was ever about the art.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **passed — `concept/adopted/D-sheet.png`**, option D of five |
| 1 | Canonical view | square | Silhouette approved against §3, **and the base slot unmistakable** | **passed — `concept/plate-r1-lit.png`**, an edit of the adopted hero, one round |
| 2 | Idle plate (unlit) | square | Same machine, field dead | **passed — `concept/plate-r1-unlit.png`**, an edit of the lit plate, so the two register |
| 4 | Glow plate | — | Differenced against stage 2 | **passed — `slot-glow.png`**, lit minus unlit: 2.3% of the canvas, and it is the slot |
| 6 | Icon | square | Legible at 16 px | **passed — keyed off the lit plate**, so the slot survives at icon size |

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

**Nine tenths cooling plant, one tenth magnet.** A fat jacketed vessel stands
off-centre on the tile with a finned condenser stack beside it, lagged trunking
looping between them, frost collars and relief valves on the crown. The coil is
inside the vessel and the player never sees it. All that shows of the separation
itself is a narrow horizontal **slot at the base of the vessel**, with cold light
standing in it.

**The joke is the proportion**: a machine this big, to make a field that small.
It is the only design of the five that explains the 2.5 MW on the tooltip, and
the tooltip is the building's whole argument.

**The anti-read is still the electromagnetic plant.** Vanilla's is a clean
lab-white box with a violet field playing over it, and copying it would say "you
imported this". **The second anti-read is now vanilla's cryogenic plant**, which
this design is much closer to than the rejected coil-throat one was: a vessel and
a condenser stack could be any cold process. The slot is what separates them, and
it has to carry that weight.

## 3.2 Key Visual Features

* A **jacketed vessel**, pale cryogenic jacketing over a dark shell, banded with
  frost collars, capped with a domed head.
* A **condenser stack** beside it — a close-packed fin bank in a heavy frame,
  about two thirds the vessel's height.
* **Lagged trunking** looping between the two, thick, flanged, staying inside
  the footprint. It connects the machine to *itself*: there is no pipe to the
  outside world, because there is no fluid box.
* **No visible coil at all.** This is the design decision, not an omission.
* **No output port.** An `assembling-machine` waits for an inserter, which may
  stand anywhere — see the template's §8 rule 3.

### Signature Feature

**The slot at the base of the vessel.** One narrow horizontal opening, the only
opening in the machine, with a steady cold blue-violet standing in it. Everything
else on the building is apparatus for keeping that slot cold.

It is also the risk: the adopted sheet reads as a *plant* first and a separator
second, and the slot is the only thing arguing otherwise. Stage 1 must draw it
wider and brighter than the concept does, and it must be the first thing the eye
finds.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Chassis and vessel shell | `#4A463F` → `#6E685C` | the mass of the building |
| Cryogenic jacketing, frost collars | `#B9B4A8` | the vessel, the collars |
| Bus bars and conductors | `#8A8580` | flanks |
| Copper and brass | `#8A5A32` → `#C88A4A` | trunking flanges, terminal blocks, condenser fittings |
| Field glow | `#6A5AC8` → `#B0A8F0` | inside the base slot only |

**The copper line is a correction, not a preference.** The adopted sheet measured
saturation **0.136** — the least saturated of the fifteen drawn this round, and
well under vanilla's 0.230 floor — because the design has almost no copper in it
by construction. It has to come back somewhere honest, and flanged joints,
terminal blocks and condenser fittings are where a real cold plant carries it.

# 4. Factorio Visual Style

## Technology tier and visual register

**Tier 3.** Advanced and sealed: seamless chassis, chamfered forms, no visible fasteners on the primary faces, and the field itself doing the visible work. It is built *from* a coil assembly, so it should look like it.

See the template's *"Technology tier sets the visual register"* — the player
should be able to read their progress off the factory floor without opening the
tech tree, so this building's surface treatment is set by where it sits on
`04-the-core.md` §6's ladder, not by taste.



3×3 and mid-height, with the vessel's domed head the tallest thing on it. Style
references: the **nuclear reactor** for heavy contained power, plus the standard
assembling machine 3 and foundry. **Do not attach the electromagnetic plant** —
it is the anti-read, and attaching it unlabelled pulls the design back toward the
thing this building exists to not be.

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

**The concept prompt lives with the design it drew:**
`coil-separator-options/D-cold-plant.md`.

**Do not re-prompt this design.** Appendix C's rule applies: crop the approved
view out of the sheet, attach it, and give a numbered list of permitted changes.

**Three changes are permitted at stage 1**, from the option page's production
notes:

1. **The base slot, wider and brighter** — it must be the first thing the eye
   finds, and it must be unmistakable at normal zoom.
2. **More copper** — trunking flanges, terminal blocks, condenser fittings. See
   §3.3 for the measurement that demands it.
3. **Nothing else.** In particular the vessel-and-stack composition is the design
   and must not drift.

**One check before locking stage 1, and it needs the game rather than an
opinion:** photograph this building beside vanilla's cryogenic plant on the same
ground at the same zoom. That is the anti-read §3.1 names, and a screenshot is
the only way to know.

---

# 13. Sprite Dimensions

**Measured off the shipped plates, not targeted.**

**Tile Size:** `32` px in-game · **Scale:** `0.5` → `64` source px per tile

| Plate | Canvas | Drawn content | Shift | Scale |
| ----- | ------ | ------------- | ----- | ----- |
| `base.png` | 200 × 216 | 192 × 208 → **3.000 × 3.250 tiles** | `{ 0, −0.125 }` | 0.5 |
| `base-shadow.png` | 367 × 227 | sheared off the plate's own alpha | `{ 1.30469, −0.03906 }` | 0.5 |
| `slot-glow.png` | 200 × 216 | the difference, registered on the base by construction | `{ 0, −0.125 }` | 0.5 |

**The shift is solved, not chosen.** The machine is 3.25 tiles tall on a 3-tile
box, so it rises a quarter tile above its footprint — which is what Factorio does
everywhere, and is not the sideways overhang that makes a row of machines
interleave. Putting its *foot* on the tile rather than its middle means the plate
moves up an eighth of a tile: `−0.125`.

**Checked against the template's Appendix C, all four checks:**

1. **Centred** — content centre equals canvas centre to **0.0 px**.
2. **Not clipped** — alpha `0` down both edge columns and along both edge rows,
   on all three plates.
3. **Fits the box** — `check-footprint.py --tiles 3` reports **0.00 tiles**
   overhang left and right, 3.25 tiles tall, "expected on a tall building".
4. **Declared equals actual** — every `width`/`height` pair in
   `prototypes/core/machines.lua` is the file's own size.

**Three in a row at the real 3-tile pitch claim 0 px twice**, at alpha > 1 and at
alpha > 80.

**Camera:** trimmed aspect **1:1.08**, inside vanilla's own range of 1.00
(rocket silo) to 1.31 (electromagnetic plant) and appropriate for a machine whose
vessel stands above its base.

**Body metal `#655344`, luminance 86, warmth R−B +33** — inside the
`#4A463F`–`#6E685C` band, and the warmth is the copper §3.3 demanded after the
concept measured 0.136 saturation.

**The glow is 2.3% of the canvas.** That is the containment rule, measured: the
light is in the slot and nowhere else.

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

**The vessel, the condenser stack beside it, and the lit slot at the base.** Must
read at 16 px as *"a fat cold tank with a bright line under it"* — the stack and
the trunking will not survive that size and should not be attempted; the vessel's
silhouette and the slot must.

*(The previous icon concept — a toroid seen square-on with the ore stream
splitting below — belonged to the rejected coil-throat design.)*

---

# 19. Design Notes / Iteration History

**Round 1, 2026-09-08 — five options, compared rather than refined.** A the
Throat, B Split Poles, C Magnet Drum, D Cold Plant, E Quadrupole; one generation
each, no refinements, a fresh conversation per option. **D was chosen.**

**This was the strongest of the three sets drawn that day.** All five held the
containment rule — the violet stayed inside the aperture, the slot, the arc line,
the base slot and the shaft respectively, and never touched the chassis — and
none of them read as vanilla's electromagnetic plant.

**The runner-up is recorded on purpose.** E, the Quadrupole, was the only sheet
of the fifteen whose detail density cleared vanilla's floor (0.148 against
0.144), and the only one whose signature feature sat on the *roof*, which is
where Factorio's camera looks. If D cannot be kept clear of vanilla's cryogenic
plant at stage 1, E is where to go.

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

---

# 21. What stage 1 found in the prototype

**A hard load error, and it was not this building's fault alone.** Replacing the
graphics set on a machine derived from the electromagnetic plant produces:

```
Error while loading entity prototype "sae-coil-separator" (assembling-machine):
Working visualisation "warm-up" doesn't exist
```

Vanilla's plant gates its audio on named animations — `sound_accents` carry
`play_for_working_visualisation`, and `main_sounds` carry
`play_for_working_visualisations`. Both name the vanilla set. The moment our
plate replaces it, all of them point at animations that are gone.

**Fixed in `prototypes/derive.lua`, not here**, as `derive.own_graphics`: it
assigns the new graphics set and strips every sound cued to a working
visualisation. This is the same failure the Ignition Array hit with the rocket
silo's welder accents and had fixed by hand; it is not a one-off but what happens
to *every* building in `machines.lua` on the day its plate arrives, so it belongs
in the shared file.

**The half that is easy to miss** is `main_sounds`. Clearing only the accents
leaves the error exactly where it was, because the warm-up, loop and cool-down
are each gated too.

**The Separator's hum is therefore chosen rather than inherited**: the cryogenic
plant's ambient loop, which is ungated and is the right noise for a building that
is nine tenths refrigeration. Its smoke-puff accents are left behind — nothing
puffs on a world with no atmosphere.
