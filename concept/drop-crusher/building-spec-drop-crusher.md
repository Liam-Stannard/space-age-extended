# Drop Crusher — building spec

Drop Crusher. Lifts a heavy weight and drops it on kamacite ore.

---

# 1. Facts

- **Name:** Drop Crusher
- **What it does:** crushes kamacite ore into crushed kamacite and kamacite
  fines. It is the only machine that does.
- **Size and directions:** 3 × 3, 1 direction. It cannot be rotated: it is
  square, runs on electricity and has no fluid box.
- **Where it can be built:** where gravity is 45 or more, so only the Core.
- **Power:** 200 kW electric.
- **Inputs and outputs:** one item slot in, one out, by inserter from any side.
  Its recipe: `06-core-production-tree.md`, Crushing.
- **Speed:** crafting speed 1; 2 module slots.
- **Cost:** 40 steel plate, 30 iron gear wheels, 10 advanced circuits; 6 s.
- **Weight:** 40 kg, stack of 20.
- **Unlocked by:** Gravity crushing.
- **Art:** signed off (2026-10-09).
- **Remnants and explosion:** TODO.

---

# 3. Visual Design

## 3.1 Design Concept

A sealed drop hammer: a tall armoured cylinder with the crushing chamber
inside. The player sees only the weight's crown, wound up out of a collar on the
roof by gears and a pawl, and dropped back into it. It must not be mistaken for
a jaw crusher, a silo or a tank.

## 3.2 Key Visual Features

* A **tall armoured cylinder** in red-oxide primer, slightly tapered, on a
  square base plate, with **four buttresses** on the diagonals.
* The **collar**: a hard machined ring at the centre of the flat roof. The
  crown lifts clear of it by most of its own height, and lands seated flush
  with the rim unbroken.
* The **lift gear**: two upright toothed gears east and west of the collar,
  meshing racks cut into the weight's shank, each driven by a geared motor at
  the roof's edge. A sprung **trip pawl** rides a ratchet on the shank and kicks
  clear to drop it.
* The **drop weight**: an octagonal forged crown on its shank. Dense and dark,
  but not flat black: chamfered edges catch the light. It carries forging, never
  machinery: no panel lines, hatches or bolts. It is smaller than the opening it
  rides in.
* An **armoured inspection hatch** with eight locking dogs on the south face,
  and a **caged status lamp** on the roof's kerb at the south-east, where
  nothing that moves passes in front of it.

No output chute or port, no pipe and no flange anywhere. The ore, the anvil bed
and the products are never drawn.

### Signature Feature

The crown that rises and falls. It moves in silhouette above the roofline, so a
player can tell a running crusher from a stopped one across the base.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Red-oxide primer | `#6E2E22` → `#8A3E2C` | the painted area: the cylinder's armour, the buttresses and the hatch |
| Bare steel | `#9C968C` | where the machine is struck or worked: the buttress edges, the hatch round its dogs, the collar, the deck round the gears |
| Steel structure | `#4A463F` → `#6E685C` | base plate and roof deck |
| Lift gear | `#8A857C` | gears, racks, pawl and collar, brighter than the armour |
| Polished steel | `#A8A296` | the collar's rim, polished by the landing; the palest part |
| Drop weight | `#4C4842` body, bevels up to `#D2CCC2` | the crown and shank |
| Hazard banding | `#C8A23A` | the base plate's edge only |
| Copper and brass | `#8A5A32` → `#C88A4A` | bands, bus runs, gear furniture, bearing caps, bolt lines; never glows |
| Status lamp | `#FFFFFF` | the lens, painted white; the engine tints it |

The primer is painted once and battered since. The deck, the gears and the
weight keep their bare metal. Replacement panels are a slightly different shade,
with small stencilled markings. Rust is dry orange on tops and dark wet streaks
below fittings.

Nothing is hot. The one glow is the status lamp: green working; yellow blocked,
disabled or short of power; red idle or out of ore; dark with no power.

---

# 4. Factorio Visual Style

Tier 0, the foothold: riveted plate, cast housings, exposed gears, rack and
pawl, weld seams, hazard tape and honest wear. The visible gearing must not be
modernised. Style reference: vanilla's crusher, for material and finish only,
not shape.

---

# 8. Connections

None that show. Inserters load and unload it from any side; both products leave
from one output. Power poles reach it with no visible connector. It has no
fluid connection.

---

# 9. Working Animation

One loop is 60 entries, 240 ticks: one craft at crafting speed 1. Entry 0 is
the rest pose: the weight 61 % up its travel, held by the pawl.

| # | Step | Entries | Ticks | What moves | Ease | Accent |
|---|---|---|---|---|---|---|
| 1 | Wind-up, upper half | 0–12 | 52 | the crown climbs; the gears turn; the pawl ticks over the teeth | even, slowing over the last 4 | 6 pawl click |
| 2 | Top hold | 13–19 | 28 | nothing; the pawl holds the crown | hold | — |
| 3 | Trip | 20–21 | 8 | the pawl kicks clear | snap | 20 trip |
| 4 | Fall | 22–27 | 24 | the crown drops; the gears spin back | faster every entry | — |
| 5 | Land | 28 | 4 | the crown lands seated; the gears stop dead | hard stop | 28 drop |
| 6 | Seated hold | 29–41 | 52 | the pawl drops back onto the rack on 36–37 | hold | — |
| 7 | Wind-up, lower half | 42–59 | 72 | the crown leaves the seat | slow in over 4, then even | 50 and 58 pawl clicks |

The gears stay meshed with the racks throughout. Modules speed the loop up.
When it stops, the crusher rests cocked; with no power and work loaded, it
freezes where it stopped.

Sound: a low motor hum under the loop. The pawl clicks are heavy and low, the
trip a rounded steel clack, the drop a heavy iron impact with rock breaking and
no grit. At most three crushers sound at once, and no more than two of any one
accent.

---

# 14. Icon

The crown standing proud of its collar on the buttressed roofline, cropped
tight. The lift gear, pawl and hazard banding are dropped at small sizes.
