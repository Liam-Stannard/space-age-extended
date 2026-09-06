# Factorio Building — Art & Implementation Specification

**Dross Classifier.** First draft — a brief, enough to commission and judge a
concept sheet. Not a specification: §6, §12 and §13 stay open until a sheet is
approved and a canonical plate has been measured.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **draft — `concept/v1-sheet.png`**, not locked |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3 | blocked on 0 |
| 5 | Working animation | portrait 2:3 | The sort loop reads as sorting | blocked on 1 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

---

# 1. Building Overview

**Building Name:** `Dross Classifier`
**Internal Prototype Name:** `sae-dross-classifier`

**Building Type:** `assembling-machine`.

**Purpose:** Sorts settling dross by particle size into **bed-grade dross**,
which is the ground the whisker beds are laid on, and **recovered fines**, which
go to the carbonyl line. It uses the same thing the settler uses — weight — but
applied to a solid.

**Why it matters:** dross is currently the mod's only genuine byproduct and it
has two outlets that are both terminal (bed tiles, and resettling back into
melt). Neither teaches anything. Classifying it makes the byproduct a **feedstock
with a choice attached**, and it gives the whisker farm a supply chain instead of
a hand recipe.

**Locale:** *"Sorts the leavings by weight, because weight is what this planet
has."* / *"Coarse dross makes ground for the beds; the fines go to the carbonyl
line. Nothing here is waste for long."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 3×3 (`collision_box {-1.4,-1.4},{1.4,1.4}`) |
| Directions | 1 |
| Crafting category | `sae-classification` |
| Energy | **Low: 150 kW.** The sort is gravity; the shake is not |
| Surface conditions | `gravity` ≥ 45 — the Core's surface alone |
| Module slots | 2 |

**The recipe, first pass:** 10 dross → 6 bed-grade dross + 3 kamacite fines, 5 s.
A tenth is lost, so classifying is not free and stockpiling raw dross stays a
legitimate choice.

### Why it is not a reskin

It shares the Ballast Drill's and the Drop Crusher's argument — gravity doing
mechanical work — but applies it to separation rather than to extraction or
breaking. Together the three read as a **family of machines that all lean on the
same planetary fact**, which is worth more than three unrelated ideas. Nothing in
vanilla sorts a solid by density.

---

# 3. Visual Design

## 3.1 Design Concept

**An enclosed deck that shakes.** The screens are *inside* a sloped armoured
housing; what the player sees is the housing riding on visible leaf springs with
an eccentric drive turning at one end. The dross is never drawn (§8), so open
trays would be three empty mesh decks on show at all times — see the template's
§8 corollary and the Drop Crusher's §19.

**The whole machine's read is that it is shaking**, and that survives enclosure
perfectly: springs and a spinning eccentric on the outside say *vibration* far
more clearly than an empty tray does.

**The anti-read is a splitter.** This is not a belt device and must not borrow a
splitter's flat, low, symmetrical read. **The second anti-read is a plain crate** —
the sloped roofline, the springs and the drive are what stop it reading as a
box.

## 3.2 Key Visual Features

* A **sloped armoured housing**, its roofline visibly descending from the drive
  end to the discharge end, so the cascade inside is legible from the outside.
* **Leaf springs** at all four corners, drawn compressed.
* An **eccentric drive** — a small offset flywheel at the high end.
* **No output port.** An `assembling-machine` waits for an inserter, which may
  stand anywhere — see the template's §8 rule 3.

### Signature Feature

**The stepped profile, read from the side.** Three descending planes is a
silhouette nothing else in the mod has, and it is legible even at the 45-degree
camera where flat machines all look alike.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Frame and bins | `#4A463F` → `#6E685C` | the structure |
| Tray decks | `#8A8580` | the three planes |
| Springs and drive | `#3B3B40` | corners and high end |
| Coarse dross | `#7A6A55` | upper trays, shallow bin |
| Fine dross | `#A89A82` | lower tray, deep bin |

**No glow.** Dross is cold by the time it gets here — it is what settled *out*.

---

# 4. Factorio Visual Style

## Technology tier and visual register

**Tier 0–1.** Mostly mechanical but deliberately built: exposed leaf springs and eccentric drive, but a machined housing rather than a knocked-together frame.

See the template's *"Technology tier sets the visual register"* — the player
should be able to read their progress off the factory floor without opening the
tech tree, so this building's surface treatment is set by where it sits on
`04-the-core.md` §6's ladder, not by taste.



3×3 and low, so the camera shows mostly deck. That suits this building: the three
trays *are* the deck, so the most-visible surface is also the most informative
one. Style reference to attach: the **crusher**, cropped and upscaled, for
material and finish.

---

# 5. Building Orientation

* [x] North only

**Direction count:** `1` — **and this is the engine's decision, not a design
choice.** `CraftingMachinePrototype` refuses to rotate a crafting machine unless
it has a fluid box, a heat or fluid energy source, or a non-square collision box.
This is a square 3×3 assembling machine with no fluid box, so it **cannot** be
rotated whatever the art implies.

That matters here more than on the other machines, because the housing's sloped
roofline is directional by nature — it descends from the drive end to the
discharge end. A player cannot turn it to suit their layout, so **the slope must
read well from every approach**, and the drive end should be the near face in the
one orientation that exists.

*(This spec previously said four directions, which was wrong.)*

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Dross in | any adjacent tile | inserters, unconstrained |
| Bed-grade / fines out | any adjacent tile | two products, one output inventory |
| Electric | no visible connector | poles reach it wirelessly |
| Fluids | none | no fluid box; no pipe flange in the art |

The bins are honest decoration, as the Drop Crusher's chutes are. They say which
end is downhill; they do not constrain inserters.

---

# 11. Generation Requirements

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio
Space Age industrial machine, every panel drawn from the game's characteristic
45-degree top-down perspective. The machine is a low three-by-three vibrating
classifier standing on an airless metallic world. Three shallow empty stepped
trays descend across the footprint, each with a visibly finer mesh than the
one above. The whole deck rides on compressed leaf springs at four corners. A
small offset flywheel drive sits at the high end. Two empty discharge lips of
different widths leave the machine on opposite sides -- one on the left face
and one on the right face -- so they sit on clearly separate tiles of the
footprint and never side by side. Dark grey-brown frame, pale grey tray decks,
charcoal springs. No belts, no conveyor, no collection bins, no glow, no
flame, no smoke. Panels: main view, side elevation showing the three
descending planes clearly, top-down view, a detail of the springs and the
eccentric drive, and the deck shown at both ends of its shake. Title the sheet
DROSS CLASSIFIER. Draw no loose material anywhere: no ore, powder, fibre,
grit, debris or product on the ground, in bins, at chutes, on trays or
spilling from the machine. Factorio machines never show what they make, so
every chute, port, bin and tray is drawn as empty machinery. Every pipe
connection must run down to ground level and stop flush at the edge of the
tile footprint; no pipe may end in mid-air and none may leave the top of the
building. Nothing may extend past the tile footprint, pipework included, and
the tile-grid panel must show the whole machine inside the grid with no
overhang.
```

---

# 15. Factorio Prototype — sketch

```lua
{
  type = "assembling-machine",
  name = "sae-dross-classifier",
  crafting_categories = { "sae-classification" },
  crafting_speed = 1,
  energy_usage = "150kW",
  energy_source = { type = "electric", usage_priority = "secondary-input" },
  surface_conditions = { { property = "gravity", min = 45 } },
  module_slots = 2
}
```

---

# 16. Icon

The three stepped trays seen from the side, coarse grit on top and pale powder
below. Must read at 32 px as *"three descending steps"* — the springs and drive
will not survive and should not be attempted.

---

# 20. Open questions

- **It must not be a second phosphorus source.** Settled here and in the Coil
  Separator's §20: **schreibersite comes from the separator only.** If the
  classifier also yielded it, neither source would gate the flux and T1 would
  stop mattering. The classifier's second stream is fines, which the carbonyl
  line consumes.
- **Two fines sources is fine; two phosphorus sources is not.** The Drop Crusher
  also makes fines, deliberately — a byproduct with two producers and one hungry
  consumer is a healthy shape, and it means the carbonyl line does not stall when
  ore runs short.
- **Does bed-grade dross replace raw dross in the whisker bed recipe?** It
  should, or classifying is optional and the building is decoration. That is a
  one-line change to `recipes.lua:sae-whisker-bed`, and it should land in the
  same commit.
