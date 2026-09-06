# Factorio Building — Art & Implementation Specification

**Drop Crusher.** First draft — a brief, enough to commission and judge a concept
sheet. Not a specification: §6, §12 and §13 stay open until a sheet is approved
and a canonical plate has been measured.

**This building is forced, not optional.** Vanilla's `crusher` carries
`surface_conditions` of `gravity` min 0 **max 0** — it is space-only
(`space-age/prototypes/entity/entities.lua:841`). Beneficiation on the Core's
surface cannot exist without a new crusher, so this is the first thing the
production tree needs and the first thing that should be built.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **draft — `concept/v9-sheet.png`**, variant B, not yet locked |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3 | blocked on 0 being locked |
| 5 | Working animation | portrait 2:3 | The drop loop reads as a drop | blocked on 1 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

---

# 1. Building Overview

**Building Name:** `Drop Crusher`
**Internal Prototype Name:** `sae-drop-crusher`

**Building Type:** `assembling-machine` with its own crafting category. Not a
copy of vanilla's crusher: that one is a rotating mill built for zero g, and this
one is its opposite.

**Purpose:** Breaks kamacite ore into **crushed kamacite** and **fines**, the two
streams the whole production tree stands on. It does it by lifting the charge and
dropping it, because at 50 g a fall does the work a motor would have to do
anywhere else.

**Why it matters:** it is the gate on T1, and T1 is what makes plate smelting
load-bearing rather than skippable. It is also the cheapest possible statement of
the Core's physics — the same gravity that settles the melt breaks the ore.

**Locale:** *"Lifts the ore and lets the planet do the rest."* / *"At fifty
gravities a drop is cheaper than a mill. Two streams out: the coarse fraction to
be smelted, the fines to the carbonyl line."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 3×3 (`collision_box {-1.4,-1.4},{1.4,1.4}`) |
| Directions | 1 |
| Crafting category | `sae-crushing` — its own, so the space crusher can never run it |
| Energy | **Low: 200 kW.** The fall is free; the lift is not |
| Surface conditions | `gravity` ≥ 45 — the Core's surface alone |
| Module slots | 2 |

**The recipe, first pass:** 2 kamacite ore → 3 crushed kamacite + 1 kamacite
fines, 2 s.

**Plate smelting must be re-sourced onto crushed kamacite** at the same time this
lands, or T1 remains skippable and this building is decoration.
`recipes.lua:sae-kamacite-smelting` currently takes raw ore; it should take
crushed.

### Why it is not a reskin

Vanilla's crusher spins and is locked to zero g. This one drops and is locked to
high g. The two cannot be built in the same place, they cannot run each other's
recipes, and each is the wrong machine on the other's world — which is what a
Core variant should mean.

---

# 3. Visual Design

## 3.1 Design Concept

**A sealed hammer.** *(Silhouette locked to variant B, `concept/variants-v4.png`.)*
A **tall armoured cylinder** ringed by external buttresses, with the forged
weight's crown seated in a collar at the centre of its flat roof. The crushing
chamber, the anvil bed and the whole stroke are **inside**; what the player sees
from outside is the crown riding up clear of its collar and slamming back down
flush.

**The collar is a datum, and that is what makes the stroke legible.** A crown
that merely bobs inside a recess reads as nothing; a crown that lifts *clear* of
a hard horizontal ring and returns to sit flush against it gives the eye a fixed
line to measure against. At the top of the stroke the crown stands proud of the
collar by most of its own height; at impact it is seated, and the collar's rim is
unbroken.

**Why enclosed, and this is the load-bearing decision.** The ore is never drawn
(§8), so an open frame would surround a permanently empty anvil bed and read as a
machine doing nothing. Vanilla's crusher is a sealed housing with its rollers in a
recessed bay for exactly this reason. Enclosing it also buys mass: a box reads
heavier than a frame, which suits the one machine on the planet whose argument is
weight.

**The anti-read is a jaw crusher.** No opposed plates, no visible gnashing, no
conveyor gullet. And the second anti-read is a **silo or a tank** — the tower and
the moving crown are what stop it reading as storage.

## 3.2 Key Visual Features

* A **tall armoured cylinder**, its wall slightly tapered, standing on a square
  base plate that fills the 3×3.
* **External buttresses** ringing the cylinder, standing proud of its wall and
  running from the base plate to just under the roof.
* A **collar** at the centre of the flat roof, a hard machined ring, with the
  weight's chamfered crown seated in it.
* A **drop weight** — a forged mass that climbs the posts and releases. It must
  read as *dense*, which is not the same as plain: a compact trapezoidal block,
  wider at its striking face than at its crown, with heavily chamfered edges that
  catch the light, a scarred and burnished striking face underneath, four guide
  shoes visibly wrapping the posts, and lifting lugs on its top face. It is
  distinctly **smaller than the gap it rides in** — a weight that fills the frame
  reads as a container.
* An **armoured inspection hatch** with locking dogs on the front face — the only
  way to the anvil bed, which is never seen in normal operation.
* **No output port of any sort.** This is an `assembling-machine`: inserters take
  from any adjacent tile, so a chute would promise something the entity cannot
  keep — see the template's §8 rule 3.

### Signature Feature

**The crown that rises and falls.** The stroke is the entire read, and it happens
in silhouette above the roofline where nothing can obscure it. A player should be
able to tell a running crusher from a stopped one across the base.

**There is no second feature, and that is deliberate.** Three rounds were spent
arguing about the size and placement of two discharge chutes before the simpler
truth surfaced: an assembling machine has one output inventory and no output
position, so it should never have had chutes at all. The stroke carries the whole
read on its own.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Frame and posts | `#4A463F` → `#6E685C` | the structure |
| Drop weight | `#2E2C29` body, chamfers up to `#6A6660` | the falling mass |
| Anvil bed | `#9A948A` | struck surface, palest thing on the machine |
| Hazard banding | `#C8A23A` | the drop zone's floor edge only |
| Ore and fines | `#7A6A55` / `#A89A82` | the two chutes, coarse and fine |

**No glow.** Nothing here is hot. The one bright note is the anvil, and it is
bright because it is polished by impact.

**The weight must not be flat black.** The first three sheets drew it as an
unadorned near-black box, because that is what §3.2 asked for, and it read as a
hole in the picture rather than a mass of steel. Dark, yes — but with a real
value range across its chamfers, so the eye reads forged metal. *Unadorned* was
the wrong word: it should carry no **machinery**, no panel lines, hatches or
bolts, while carrying all the **forging** it likes.

---

# 4. Factorio Visual Style

3×3 but tall, so the tall-building clause applies: the frame leans slightly away
from the camera and the shadow needs its own canvas (Appendix C). Style reference
to attach: the **crusher**, cropped and upscaled, with the standing disclaimer
that it is a reference for material and finish, not for shape — this machine's
shape is its argument.

---

# 5. Building Orientation

* [x] North only

**Direction count:** `1`. A vertical drop looks the same from every side, and the
chutes accept inserters from any tile.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Ore in | any adjacent tile | inserters, unconstrained |
| Crushed / fines out | any adjacent tile | two products, one output inventory |
| Electric | no visible connector | poles reach it wirelessly |
| Fluids | none | no fluid box anywhere; no pipe flange in the art |

The chutes are **honest decoration** in the way a vanilla furnace's hopper is:
they tell the player where the two streams conceptually go without constraining
where an inserter may stand.

---

# 11. Generation Requirements

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio
Space Age industrial machine. PROJECTION RULE, which overrides everything else
and applies to every panel: draw the building SQUARE-ON to the tile grid
exactly as Factorio draws its own sprites -- the front face parallel to the
bottom edge of the panel, the side faces parallel to the left and right edges.
Do NOT rotate the building so a corner points at the viewer, and do not draw
it three-quarter or isometric. The machine is a sealed 3x3 impact crusher: a
tall armoured cylinder with a slightly tapered wall, standing on a square base
plate that fills the footprint, ringed by external buttresses that stand proud
of the wall and run from the base plate to just under the roof. Its roof is
flat, with a hard machined collar at the centre in which the forged drop
weight's chamfered crown is seated. An armoured inspection hatch with radial
locking dogs sits on the front face. PORT RULE: this machine holds its output
in an inventory until an inserter takes it, so it has NO output chute, spout,
boom, bin, tray or opening of any kind -- draw none at all. Its side and rear
faces are plain armour, broken only by armour ribs, small louvred vents and
bolt lines. Dark grey-brown armour, pale machined collar, dark forged crown,
small yellow hazard banding at the base only. No open frame, no exposed anvil,
no jaw plates, no conveyor, no silo or tank read, no glow, no flame, no smoke.
Panels: main view, front elevation, side elevation, an in-game icon, a 3x3
tile grid top view, a detail of the roof collar with the crown seated in it, a
detail of the inspection hatch, a layer breakdown row separating shadow, base
plate, cylinder body, buttresses, roof collar and drop weight, a colour
palette row, and an animation row of four key frames showing the crown
standing proud of the collar by most of its own height at the top of the
stroke, descending, and finally seated flush so the collar rim is unbroken.
Draw no loose material anywhere. Nothing may extend past the 3x3 tile
footprint. Draw no logos, wordmarks or watermarks anywhere -- in particular no
Factorio or Space Age logo. Title the sheet DROP CRUSHER.
```

---

# 15. Factorio Prototype — sketch

```lua
{
  type = "assembling-machine",
  name = "sae-drop-crusher",
  crafting_categories = { "sae-crushing" },
  crafting_speed = 1,
  energy_usage = "200kW",
  energy_source = { type = "electric", usage_priority = "secondary-input" },
  surface_conditions = { { property = "gravity", min = 45 } },
  module_slots = 2
}
```

---

# 16. Icon

The carriage mid-fall between two posts, with the anvil beneath. Must read at
32 px as *"something heavy dropping"* — the two chutes are too fine to survive at
that size and should not be attempted.

---

# 20. Open questions

- **One recipe or two?** The brief assumes one recipe with two products. An
  alternative is two recipes — a coarse crush and a fine grind — letting the
  player choose the ratio. That is a branch rather than a formality and would
  suit `06-core-production-tree.md`'s own rule that every tier must branch, loop
  or converge. Worth deciding before the art is commissioned, since it changes
  whether the two chutes are simultaneous or alternate.
- **Do the fines have a home yet?** They feed the carbonyl line (T3), which does
  not exist. Until it does, fines are a dead-end item and the split is
  cosmetic — so either land T3 alongside this, or give fines a stopgap use.


---

# 19. Design Notes / Iteration History

### Version 1 — `concept/v1-sheet.png`

Layout, panel set and silhouette right first time. Attaching a vanilla crusher
frame as a style reference and an approved sheet from another building as a
format example did the work Appendix B says they do: the panel structure, the
labelled information table and the colour-swatch row all arrived without being
described.

Four things were wrong, all of them in the machine rather than the sheet:

1. **Copper hydraulic pipes and cables all over the frame**, and copper in the
   palette. §8 says this building has **no fluid box and no pipe flange
   anywhere** — the art was promising a connection the prototype does not have.
2. **The carriage read as a detailed equipment box** with panel lines, bolts and
   a hatch. §3.2 asks for an unadorned slab: it is a dead weight, not a machine.
3. **Too squat.** §4 invokes the tall-building clause and the drop distance is
   the mechanic; the posts were barely taller than the base.
4. **Raised and dropped were nearly identical** in the key frames, so the
   signature stroke did not read.

### Version 2 — `concept/v2-sheet.png` — **draft, not locked**

All nine buildings are being drafted first and locked together at the end, so
nothing here is approved yet and Appendix C's *"once a design is locked, stop
prompting"* rule has not started applying.

All four fixes took, in one round, written to Appendix A's shape: keep-list
first, then numbered fixes each naming what it currently reads as and what it
must read as.

- Every pipe, hose and cable gone; copper gone from the palette; the breakdown
  row's **PIPES & DETAIL** layer replaced with **GUIDE RAILS**.
- The carriage is now a plain near-black block, `#1F1F1F`, darker than anything
  else on the machine and labelled *"plain weight block"*.
- The posts are roughly twice the base height. It reads as tall, and the drop
  reads as long.
- Raised sits at the top of the posts, dropped sits hard on the bed.

Verified new rather than re-encoded by byte size (2,091,348 against v1's
2,187,107) and by `ImageChops.difference`, per Appendix B.

**Palette as drawn**, which supersedes §3.3's first guess:

| Role | Sheet | §3.3 asked for | Note |
| ---- | ----- | -------------- | ---- |
| Dark metal | `#3B3A36` | `#4A463F` | Slightly darker; in family |
| Secondary metal | `#5E5B55` | `#6E685C` | Slightly darker; in family |
| Anvil stone | `#B7B6AF` | `#9A948A` | **Lighter, and better** — §3.3 wants it the palest thing on the machine |
| Carriage block | `#1F1F1F` | `#2E2C29` | **Darker, and better** — §3.2 wants it darker than everything |
| Hazard yellow | `#D1A620` | `#C8A23A` | Effectively the same |
| Dust grey | `#787B71` | `#7A6A55` | Greyer than the brown asked for; left alone at concept stage, since Appendix C measures colour off the plate rather than eyeballing the sheet |

**One thing settled by the art, for §5 and the plate stage:** the canonical view
draws the carriage **raised**, so the idle plate is the raised position and the
drop is the working animation. That is the right way round — a machine at rest
should be holding its weight up, not sitting on its own anvil.

**Still open, and unchanged:** §20's two questions. One recipe or two, and
whether the fines have a consumer yet.


### Versions 3 to 5 — the redraw

**v3** applied the I/O conventions: chutes empty, nothing on the ground, inside
the grid. **v4** split the chutes onto opposite faces, after both were found
sitting side by side in a single tile of the 3×3 — which read as one output and
left nowhere for a second belt.

**v5 fixed the weight, and the fault was in this document.** §3.2 said
*"an unadorned slab"* and §3.3 pinned it near-black, so three sheets running drew
a featureless black box that read as a hole in the picture rather than a mass of
steel. *Unadorned* was the wrong word. It should carry no **machinery** — no
panel lines, hatches or bolts — while carrying all the **forging** it likes:

- a compact trapezoidal mass, wider at the striking face than at the crown,
- heavily chamfered edges that catch the light,
- a scarred, burnished striking face underneath,
- four guide shoes visibly wrapping the posts, and lifting lugs on top,
- **distinctly smaller than the gap it rides in** — a weight that fills the frame
  reads as a container, not a hammer.

§3.2 and §3.3 are corrected to match, and the weight now has its own detail panel
on the sheet.


### Version 6 — enclosed, and this is the shape to keep

Liam's call, and it is the better design for a reason that generalises: **the ore
is never drawn, so an open frame surrounds a permanently empty anvil bed and the
machine reads as idle even while it runs.** That is precisely why vanilla's
crusher is a sealed housing with its rollers in a recessed bay, and it is now
recorded in the template's §8 as the corollary to *never draw the product*.

What the enclosure bought, beyond fixing that:

- **Mass.** A box reads heavier than a frame, which suits the one machine on the
  planet whose whole argument is weight. The open version never looked heavy no
  matter what was done to the weight itself.
- **A better animation.** The weight's crown emerging from a gland on the tower
  gives the stroke a silhouette read above the roofline, where nothing can
  obscure it — legible across the base, and four key frames now show the crown
  sinking away into the tower.
- **A distinctive silhouette.** Enclosed with a central tower, it no longer shares
  a family read with the Ballast Drill, which was the other standing complaint.

The anvil bed is now behind an armoured inspection hatch and is never seen in
normal operation, which is the honest arrangement: it was only ever drawn to be
looked at, and it was always empty.


### Version 7 — variant B, built out

Liam chose **variant B**, the tall buttressed cylinder, off
`concept/variants-v4.png`. The full sheet is `concept/v7-sheet.png`.

**The one concern raised at selection, and how it was answered.** B's crown sits
in a collar on the roof rather than on top of a tower, so the stroke risked being
the least legible of the three. The fix is to make the collar a **datum**: the
crown lifts *clear* of the ring by most of its own height at the top of the
stroke and returns to sit flush, leaving the rim unbroken. A crown bobbing inside
a recess reads as nothing; a crown measured against a hard horizontal line reads
at a glance. The four key frames on the sheet are drawn to that.

**Palette as drawn**, superseding §3.3 again:

| Role | Sheet | Note |
| ---- | ----- | ---- |
| Primary armour | `#3A3632` | Darker than §3.3's `#4A463F` |
| Secondary armour | `#64605A` | |
| Machined collar | `#A7A7A2` | The palest thing on the machine, correctly |
| Drop weight | `#212121` | Near-black again, but now faceted, so it reads as forged rather than as a hole |
| Warm metal | `#7C7364` | |
| Hazard yellow | `#D4A017` | |
| Rust accent | `#7B4B2A` | Not in §3.3; sparingly used and worth keeping |

**What the sheet gets right that earlier ones did not:** four true elevations
(south, east, north) all square-on, a top view sitting inside the 3×3 with the
buttresses reading as the footprint's corners, no output port anywhere, and a
layer breakdown that separates cleanly into shadow, base plate, cylinder body,
buttresses, roof collar and drop weight — which is close to how the prototype
will actually be layered.


### Version 8 — the camera fixed, and the prompt restructured

Two faults in v7, both Liam's catch.

**The camera was wrong, and my own rule caused it.** Rule zero said "square-on to
the tile grid", which fixed the corner-on rotation but was read as *flat-on*: v7
is an architectural front elevation with almost no roof. Factorio looks steeply
**down** — mostly roof, shallow near face — and the roof is where the collar, the
hatches and the vents live. The template's rule zero now names both halves,
rotation *and* elevation, and says what each looks like when missed.

**The prompt had grown to 2,505 characters of competing prose** and rules kept
falling out of it — ports from one generation, palette from another, camera from
this one. Rewritten as **1,751 characters of labelled sections** — CAMERA,
BUILDING, FORM, COLOUR, RULES, PANELS, OUTPUT — it produced a better sheet in a
single pass. The palette came back hit exactly, hex for hex, and the rules were
echoed onto the sheet as a notes panel, which no prose version ever managed. The
skeleton is now in the template's Appendix B.


### Version 9 — one view, one camera

v8's main view was right and its three "elevations" were wrong: drawn flatter and
more side-on than the main view, they read as architectural elevations. **Factorio
has rotations, not elevations** — north, east, south and west are the same camera
with the building turned underneath it, and the engine never produces a flat
side-on view at all. A sheet that draws one is describing something the game
cannot show.

This entity has **one** direction, and that is the engine's decision rather than
a preference: a square assembling machine with no fluid box cannot be rotated.
So v9 draws the machine **once**, large, and spends the reclaimed space on the
icon, the top view, the two details, the layer breakdown, the palette and the
four animation frames.
