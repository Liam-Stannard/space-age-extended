# Factorio Building — Art & Implementation Specification

**Whisker Comber.** The design is locked: **option C, the Spinner**, chosen
2026-09-08 from five drawn against each other. The decision record is
`whisker-comber-options/`, the sheet is `concept/adopted/C-sheet.png`, and the
four rejected designs are gone. §6, §12 and §13 stay open until a canonical plate
exists and has been measured.

**The adopted design changed what this building looks like.** It is no longer a
low casing with two needled drums lying in it: it is a squat vertical drum that
aligns fibre by spinning it. §3 and §16 are rewritten against that; §1, §2, §8
and §20 are unchanged, because none of them was ever about the art.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **passed — `concept/adopted/C-sheet.png`**, option C of five |
| 1 | Canonical view | square | Silhouette approved against §3, **and clearly not the Sealed Roboport's dome** | **passed — `concept/plate-r1.png`**, an edit of the adopted hero, one round |
| 2 | Idle plate (unlit) | — | Same machine, nothing lit | **passed — it is the same plate; nothing on this machine is ever lit** |
| 5 | Working animation | portrait 2:3 | The comb stroke loops seamlessly | blocked on 1 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

---

# 1. Building Overview

**Building Name:** `Whisker Comber`
**Internal Prototype Name:** `sae-whisker-comber`

**Building Type:** `assembling-machine`.

**Purpose:** Turns a harvest of loose kamacite whiskers into either **whisker
tow** — combed into one direction, strong in tension, the feedstock for composite
— or **whisker felt**, matted and unaligned, which is cheap thermal insulation.
Two recipes, one machine, and the player chooses the split.

**Why it matters:** the farm currently has one output and therefore no decisions.
Single-crystal fibres really are absurdly strong along their axis and useless
across it, so alignment is a genuine process step rather than an invented one —
and two grades from one crop is what turns a field into a factory. The answer to
*"how much of this harvest is worth combing?"* changes as the base grows, which is
the only kind of number a player enjoys revisiting.

**Locale:** *"Strength runs one way in a whisker. This is what points them all the
same way."* / *"Combed into tow, or matted into felt. The comb is slow and the
mat is not, and which you want depends on what your line is short of."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 3×3 (`collision_box {-1.4,-1.4},{1.4,1.4}`) |
| Directions | 1 |
| Crafting category | `sae-fibre` |
| Energy | 400 kW, electric |
| Surface conditions | `pressure` ≤ 9 — the Core and platforms |
| Module slots | 3 |

**The two recipes, first pass:**

| Recipe | In | Out | Time |
| ------ | -- | --- | ---- |
| Combing | 8 kamacite whiskers | 1 whisker tow | 12 s |
| Matting | 4 kamacite whiskers | 1 whisker felt | 3 s |

Combing is deliberately four times slower per whisker. Tow is what the composite
line needs and felt is what the cryostat needs, so neither is the "correct"
answer — but a player who combs everything will find their cryogenics starved,
and a player who mats everything will never build a frame.

### Why it is not a reskin

Nothing in vanilla splits one harvest into a quality-graded pair where both
grades have real consumers. Gleba's fruit yields fixed products; this is the
player deciding the ratio, every hour, against whatever their line is short of.

---

# 3. Visual Design

## 3.1 Design Concept

**A squat vertical drum that spins fibre into line.** The machine stands rather
than lies: a heavy machined shell about as tall as it is wide, a domed lid held
by a ring of toggle dogs, a ring of balance bosses round the waist, a louvred
drive skirt at the base, and a small arched draw-off guide standing over one edge
of the lid. Inside, a spinning head throws the material against the wall and it
comes off aligned; none of that is visible, and none of it needs to be.

**Why standing, and not another low box.** The spec's own problem, stated below
in §3.2, is that this machine sorts things next to a machine that sorts things —
the Dross Classifier is also a low grey 3×3. A standing drum separates from it at
any zoom, in any direction, with no detail at all. A vertical axis is also the
honest answer to gravity 50: it is the one axis where the Core's gravity is not
fighting the bearings.

**The anti-read is a textile mill**: no wooden framing, no spindles, no bobbins,
no thread, nothing that belongs in one. **The second anti-read is now the Sealed
Roboport**, which is a smooth dome already standing on the Core. This machine is
squat, bolted and industrial where that one is smooth — and that difference is
carried entirely by hardware, so every piece of it matters.

## 3.2 Key Visual Features

* A **squat drum** on the 3×3, machined shell, low skirt where it meets ground.
* A **domed lid** held by a ring of toggle dogs, lifting eye at the crown —
  bolted and squat, never smooth and seamless.
* A ring of **balance bosses** round the waist, evenly spaced. This is the detail
  that says the thing spins, and it is what a round shell needs to stop reading
  as a tank.
* A **louvred drive skirt** at the base, with a cable entry.
* A **draw-off guide** over one edge of the lid: two polished rollers in a small
  arch, drawn empty. It is not a port and must never be aimed at a tile.
* **No output port.** An `assembling-machine` waits for an inserter, which may
  stand anywhere — see the template's §8 rule 3.

### Signature Feature

**The standing silhouette.** A round body among low boxes, and the only round
building in the Core's machine set.

**What was given up to get it**, recorded so it is not rediscovered as a
surprise: the previous design's signature was the *before-and-after* along the
machine's length — tangle in, ordered ribbon out — which was the recipe drawn on
the building. A vertical drum has no length to read along, and the two recipes
(comb into tow, mat into felt) are not visible on this machine at all. Option E
of the round was the design that showed them, and it was not picked. If the
choice has to become visible later it belongs in a `working_visualisation`, which
only plays while the machine is crafting.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Chassis and shell | `#4A463F` → `#6E685C` | the drum |
| Working parts | `#8A8580` | draw-off rollers, visible mechanism |
| Needle glints | `#D8D4CC` | needled surfaces only, sparingly |
| Pale nickel-white | `#B9B4A8` | lid ring, chamfers, guards, end caps |
| Copper and brass | `#8A5A32` | drive skirt, bearing caps, lid furniture |

**Two measurements to fix at stage 1, both from the adopted sheet.** It came back
at **saturation 0.180** against vanilla's 0.230 floor, and at **edge density
0.114** against a floor of 0.144 — the least detailed sheet of the fifteen drawn
that day. A round shell gives the eye less to hold, which is exactly why vanilla
covers its round machines in hardware. More instrumentation, more panel breaks,
more fittings on the skirt; and let the copper out, which fixes both numbers at
once.

# 4. Factorio Visual Style

## Technology tier and visual register

**Tier 1–2.** Precision plant: machined casing, guarded mechanism, few visible fasteners on the primary faces. The needled drums inside are the only crude thing about it.

See the template's *"Technology tier sets the visual register"* — the player
should be able to read their progress off the factory floor without opening the
tech tree, so this building's surface treatment is set by where it sits on
`04-the-core.md` §6's ladder, not by taste.



3×3 and standing, about as tall as it is wide, so the camera shows the lid and a
shallow band of shell. The lid is therefore the most-visible surface and has to
carry hardware. Style references: the **recycler** for a guarded precision
machine, plus the standard assembling machine 3 and foundry.

---

# 5. Building Orientation

* [x] North only

**Direction count:** `1`. The infeed-to-outfeed axis is fixed and the inserters
do not care which end they stand at.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Whiskers in | any adjacent tile | inserters, unconstrained |
| Tow / felt out | any adjacent tile | one output inventory |
| Electric | no visible connector | poles reach it wirelessly |
| Fluids | none | no fluid box; no pipe flange in the art |

---

# 11. Generation Requirements

**The concept prompt lives with the design it drew:**
`whisker-comber-options/C-spinner-drum.md`.

**Do not re-prompt this design.** Appendix C's rule applies: crop the approved
view out of the sheet, attach it, and give a numbered list of permitted changes.

**Two changes are permitted at stage 1**, from the option page's production
notes:

1. **More hardware and more copper** — instrumentation, panel breaks, skirt
   fittings. §3.3 carries the two measurements that demand it.
2. **Everything that separates this from the Sealed Roboport must survive**: the
   toggle dogs, the lifting eye, the balance-boss ring, the louvred skirt. If a
   round smooths any of them away, it is a failed round however good it looks.

---

# 13. Sprite Dimensions

**Measured off the shipped plates, not targeted.**

**Tile Size:** `32` px in-game · **Scale:** `0.5` → `64` source px per tile

| Plate | Canvas | Drawn content | Shift | Scale |
| ----- | ------ | ------------- | ----- | ----- |
| `base.png` | 200 × 225 | 192 × 217 → **3.000 × 3.391 tiles** | `{ 0, −0.19531 }` | 0.5 |
| `base-shadow.png` | 374 × 236 | sheared off the plate's own alpha | `{ 1.35938, −0.10938 }` | 0.5 |

**Checked against the template's Appendix C, all four checks:** centred to
**0.0 px**; alpha `0` on all four edges of both plates; `check-footprint.py
--tiles 3` passes with the drawn machine 3.000 tiles wide and 3.39 tall ("above
the box: 0.39 — expected on a tall building"); declared sizes equal the files'.

**Three in a row at the real 3-tile pitch claim 0 px twice**, at alpha > 1 and at
alpha > 80.

**Camera:** trimmed aspect **1:1.13**, inside vanilla's 1.00–1.31 range.

**Body metal `#57422F`, luminance 69, warmth R−B +40** — inside the
`#4A463F`–`#6E685C` band, and the warmest plate of the three cut this round,
which is the copper §3.3 asked for after the concept measured 0.180.

---

# 15. Factorio Prototype — sketch

```lua
{
  type = "assembling-machine",
  name = "sae-whisker-comber",
  crafting_categories = { "sae-fibre" },
  crafting_speed = 1,
  energy_usage = "400kW",
  energy_source = { type = "electric", usage_priority = "secondary-input" },
  surface_conditions = { { property = "pressure", max = 9 } },
  module_slots = 3
}
```

---

# 16. Icon

**The standing drum, its dogged lid and the draw-off arch.** Must read at 16 px
as *"a squat round machine with something over its lid"* — the balance bosses and
the louvres will not survive that size and should not be attempted; the
silhouette and the arch must.

*(The previous icon concept — aligned fibres against a tangle — drew the product,
which the template's §8 rule 1 forbids on the building and which is a poor idea
on an icon for the same reason: it promises a read the machine never shows.)*

### The Sealed Roboport problem, measured

**At 16 px this icon and the Sealed Roboport's overlap at IoU 0.85.** Both are
round brown masses at that size, and the toggle dogs, balance bosses and louvred
skirt that separate them on the plate are all below one pixel. The risk the
option page named has landed exactly where it was pointed.

**Two things still separate them in play, and neither is the icon.** The Roboport
is a 4-tile building against this one's 3, so they differ by a third in width
wherever they stand together; and this plate is the warmer of the two by
measurement (R−B +40).

**What would fix the icon is a plate change, and that is a design decision rather
than a processing one** — raising the draw-off arch clear of the dome so the
outline gains a notch, which is the one part of this machine that is not
rotationally symmetrical. It is *not* taken here, because the design is locked and
Appendix C's rule is that a locked design stops being re-prompted. Recorded for
Liam: accept the collision at icon size, or spend one plate round on the
silhouette.

---

# 19. Design Notes / Iteration History

**Round 1, 2026-09-08 — five options, compared rather than refined.** A Carding
Casing, B Travelling Gill, C Spinner, D Mill Stack, E Two-Lane Machine; one
generation each, no refinements, a fresh conversation per option. **C was
chosen.**

**The set's real finding was not about any one option.** With the material
correctly undrawn, three of the five read as machines *waiting* rather than
working — B's empty roof slot most of all. That is the sharpest form of the
conflict between this spec's old §3.2, which wanted the fibre's before-and-after
drawn on the building, and the template's §8 rule 1, which forbids drawing the
product at all. The honest resolution is a `working_visualisation`: the engine
draws it only while the machine crafts, so it stops when the machine does.

**The runner-up is recorded on purpose.** A, the Carding Casing, was the
best-measured sheet of the fifteen — the only one in this set inside vanilla's
detail band — and it is the fallback if the Spinner cannot be kept clear of the
Sealed Roboport's dome.

---

# 20. Open questions

- **Should felt come out of combing as a byproduct instead of its own recipe?**
  A single recipe yielding tow plus a little felt is simpler and removes the
  choice. The choice is the point, so: two recipes. Recorded here so it is not
  quietly simplified later.
- **Both consumers must exist before this is worth building.** Tow feeds whisker
  prepreg (T5) and felt feeds the cryostat core (T6), and neither tier is built.
  Landing the comber alone gives the player two items with nowhere to go.
- **`allowed_effects`.** Speed modules on combing would undercut
  `04-the-core.md` §7's rule that the answer to "faster" is more floor. The farm
  itself is already area-limited, so the comber is arguably the one place speed
  is legitimate — but it should be a decision, not an oversight.

---

# 22. What stage 1 found

**One round, no refinements.** The plate is an edit of the adopted hero with two
changes permitted: more hardware, because the concept measured **0.114** edge
density against vanilla's 0.144 floor and a round shell gives the eye less to
hold; and copper let out, because it measured **0.180** saturation against a
floor of 0.230. Both landed — the plate carries gauges, an inspection port, a
junction box, more skirt fittings and bolt rings, and it measures warmth **+40**.

**The dome held its ground.** It came back squat and bolted rather than smooth,
which was the condition the option page set: everything separating it from the
Sealed Roboport had to survive. On the plate it did. At icon size it did not —
see §16.

---

# 25. The accent, and why a cold machine needs paint

**This machine makes no light, so it had nothing to be told apart by.** Measured
across ten of our icons: they sat in a nine-degree hue band at a mean pairwise
RGB distance of 13.2, where vanilla's six production icons span 27°–98° at 32.6.
The Core's palette is one warm iron-nickel body plus copper, and the only things
that break it are emissive — heat, frost, a field, a charge.

**So the accent is paint:** service blue `#2E5A8C`, on the shoulder band, the lid's toggle dogs and the drive skirt's access panel. Blue is the colour a guarded machine's service furniture carries, and these are the parts a person touches on a machine handling something that would cut you. Paint is reflective, chipped and worn;
it never glows, and it is not a status light.

**Measured after the repaint:** the icon now carries **7 blue** distinct-hue pixels
at 16 px out of about 150 lit, where it carried none. That is the number that
matters — an accent has to be an *area* to survive to icon size, which a lit port
or a rime band does not.

See the template's *"Every machine gets an accent"* note for the rule and the
assignment table.
