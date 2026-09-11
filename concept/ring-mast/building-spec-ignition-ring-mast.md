# Factorio Building — Art & Implementation Specification

**Ignition Ring Mast.** First draft — a brief, enough to commission and judge a
concept sheet. Not a specification: §6, §12 and §13 stay open until a sheet is
approved and a canonical plate has been measured.

**This building carries a mechanic, not just a job.** It is how helium-3 comes to
throttle the endgame without the Ignition Array needing a fluid box — the
problem H4 was raised to solve and could not, since no vanilla rocket silo has
one and the launch UI's behaviour with a fluid ingredient is unknown. The ring
mast routes around it entirely: the mast takes the fluid, and the Array takes the
mast's output as an item.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **draft — `concept/v1-sheet.png`**, not locked |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3, **and against the Arc Mast** | blocked on 0 |
| 2 | Idle plate (unlit) | portrait 2:3 | Same machine, unenergised | blocked on 1 |
| 4 | Charge glow sheet | portrait 2:3 | Differenced against stage 2 | blocked on 2 |
| 6 | Icon | square | Legible at 32 px, and not confusable with the Arc Mast's | blocked on 1 |

---

# 1. Building Overview

**Building Name:** `Ignition Ring Mast`
**Internal Prototype Name:** `sae-ring-mast`

**Building Type:** `assembling-machine` with a `fixed_recipe`. It is a mast in
fiction and a machine in the engine, and the spec should not pretend otherwise.

**Purpose:** Charges **ignition charge** from helium-3 and a great deal of
electricity. The Field Coil Segment recipe — the Ignition Array's `fixed_recipe`
— consumes one, so no segment is ever built without a ring of these running.

**Why it matters:** it makes the last hour of the mod a **site** rather than a
building. Vanilla's rocket silo is a thing you place; the Array becomes a thing
you *lay out*, surrounded by masts that have to be close enough to deliver.

**Locale:** *"Stands in the ring and holds the charge until the Array asks for
it."* / *"Helium-3 and a great deal of current, held for a few seconds at a time.
It has to stand close: what it makes does not travel."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 3×3 (`collision_box {-1.4,-1.4},{1.4,1.4}`) |
| Directions | 1 |
| Crafting category | `sae-ignition-charge` — its own |
| `fixed_recipe` | `sae-ignition-charge` |
| Energy | **12 MW.** It is meant to hurt |
| Surface conditions | `pressure` 1–9 — the Core alone, as the Array is |
| Module slots | 0, `allowed_effects = {}` |
| Fluid boxes | 1 in (helium-3) |

**The recipe, first pass:** 25 helium-3 + 12 MW for 4 s → 1 ignition charge.

### The ring is geometry, not a rule

**Agreed 2026-09-06.** The mechanic below is settled; what remains open in §20 is
whether the engine behaves as it assumes, not whether the design is wanted.

Nothing in the engine can require a building to be *near* another one. The mast
does it with a timer instead: **ignition charge carries a very short
`spoil_ticks`** — on the order of ten seconds — and no `spoil_result`, so it
simply ceases to exist. Belt travel is real time, so a mast more than a few
seconds of belt from the Array delivers nothing.

That is the whole mechanic, and it is pure data. It reuses the engine's spoilage
timer, which the mod already leans on three times, and it needs no control-stage
script.

### Why it is not a reskin of the Arc Mast

They are opposites and the art has to say so. The Arc Mast **catches** something
episodic and banks it; this **spends** something continuously and cannot store it
at all. One is a receiver with a cage at the top; this is an emitter with its
mass at the bottom. If a player ever confuses the two silhouettes at a glance,
this design has failed — see §3.1's anti-read, which is unusually specific for
that reason.

---

# 3. Visual Design

## 3.1 Design Concept

A charged post, braced against its own discharge. Low and wide at the base,
tapering to a short capped emitter — the inverse of the Arc Mast's tall open cage
on a narrow leg.

**The anti-read is the Arc Mast**, and it is the most important line in this
brief. No cage. No open electrode. No upward-reaching structure. Nothing at the
top that looks like it wants to be struck. This machine's business is at its
waist, where the helium enters, and its top is closed.

## 3.2 Key Visual Features

* A **wide braced base** — four heavy buttresses, obviously resisting something.
* A **charge band** at waist height: a thick ring of banded coils around the
  shaft, the widest part of the machine.
* A **short capped emitter** at the top, closed and blunt.
* A **helium inlet** entering the charge band horizontally, bare machine metal
  — see the template's convention 5: connections carry no frost, heat or tint.

### Signature Feature

**The charge band pulses and the emitter does not.** Light climbs the band, holds,
and dies, over the four-second craft. The top stays dark throughout — which is the
single clearest way to say *this is not the thing lightning hits*.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Base and buttresses | `#4A463F` → `#6E685C` | the mass of the building |
| Charge band coils | `#8A5A32` → `#C88A4A` | waist only |
| Emitter cap | `#3B3B40` | the closed top |
| Charge light | `#F0E0A8` → `#FFF8E0` | inside the band only |

**Warm white, not violet and not green.** Violet belongs to the Coil Separator's
field and green to the radiant family; the Array's own firing is the only other
warm-white light in the mod, and these two *should* look related.

---

# 4. Factorio Visual Style

## Technology tier and visual register

**Tier 4 — The goal.** Exotic, barely reading as machinery: a monolithic surface with no seams at all, no fasteners anywhere, and contained light doing the work. It stands beside the Ignition Array and must not look like it came from the same era as the Drop Crusher.

See the template's *"Technology tier sets the visual register"* — the player
should be able to read their progress off the factory floor without opening the
tech tree, so this building's surface treatment is set by where it sits on
`04-the-core.md` §6's ladder, not by taste.



3×3 and tall, so the tall-building clause applies: it leans slightly away from
the camera and its shadow needs its own canvas (Appendix C). Style reference to
attach: the **Ignition Array's own approved deck plate**, so the ring and the
thing it rings read as one installation.

---

# 5. Building Orientation

* [x] North only

**Direction count:** `1` — **a choice, and the right one.** The helium fluid box
would permit rotation, but a ring of masts around the Array will be placed at
every angle, and a machine with a visible "front" would look wrong in three
quarters of those positions. Radial symmetry is the requirement (§5), so the
single asymmetry — the inlet flange — is the only thing that has to be sited
carefully.. A ring of masts around a silo will be placed at every
angle, and a machine with a visible "front" would look wrong in three quarters of
those positions. Radial symmetry is the requirement, not a simplification.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Helium-3 in | the charge band, one face | modelled flange, `pipe_picture` emptied |
| Ignition charge out | any adjacent tile | inserters, unconstrained |
| Electric | no visible connector | poles reach it wirelessly |

The building is radially symmetric but its fluid box is not, so the inlet flange
is the one asymmetry in the plate. It has to be drawn at exactly the tile the
fluid box names.

---

# 11. Generation Requirements

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio
Space Age industrial machine, every panel drawn from the game's characteristic
45-degree top-down perspective. The machine is a tall radially symmetric
three-by-three charging post standing on an airless metallic world. Four heavy
buttresses splay from a wide base. At waist height a thick banded ring of
copper-brown coils forms the widest part of the machine. Above it the shaft
tapers to a short blunt closed charcoal cap. A slim bare metal pipe leaves the
coil band, runs down the outside of one buttress, and stops at
a flange flush with the ground at the edge of the footprint. Warm white light
glows from inside the coil band only; the top of the machine is completely
dark. Dark grey-brown armour. No cage, no open electrode, no lightning rod, no
upward-reaching mast, no antenna, no arcs, no smoke, no flame. Panels: main
view, front elevation, side elevation, a detail of the coil band with the
bare pipe running down to its ground flange, and the band shown unlit and
fully charged. Title the sheet IGNITION RING MAST. Draw no loose material
anywhere: no ore, powder, fibre, grit, debris or product on the ground, in
bins, at chutes, on trays or spilling from the machine. Factorio machines
never show what they make, so every chute, port, bin and tray is drawn as
empty machinery. Every pipe connection must run down to ground level and stop
flush at the edge of the tile footprint; no pipe may end in mid-air and none
may leave the top of the building. Nothing may extend past the tile footprint,
pipework included, and the tile-grid panel must show the whole machine inside
the grid with no overhang.
```

---


## Master Concept Prompt

Stage 1. **Attach `concept/ring-mast/adopted/A-sheet.png` and
nothing else** — this is the same machine as the sheet's hero view, not a new
design, and any second reference invites a second building (see
the art backlog (now `TODO.md`)'s warning).

**The band is UNLIT.** This plate is the machine the glow layer is derived from,
so a band drawn part-charged would bake a mid-cycle state into the still.

**The inlet is BARE.** The adopted sheet drew it frost-jacketed; that was
generated before the template's convention 5 and is the one thing this render
changes.

```text
FACTORIO SPACE AGE BUILDING SPRITE -- MASTER PLATE

Redraw the machine in the ATTACHED SHEET's hero view as a single clean game
sprite. Same building, same design, same camera. Do not redesign it, do not
add or remove parts, and do not draw any panels, labels, text, borders or
background furniture.

== WHAT IT IS ==
The Ignition Ring Mast: a 3x3 charging post on an airless metal world. A wide
braced base with four heavy buttresses splaying to the corners. At waist height
a thick banded ring of close-wound copper-brown coils, the widest part of the
machine. Above it the shaft tapers to a short blunt CLOSED charcoal cap. A slim
pipe leaves the coil band, runs down the outside of one buttress, and stops at a
flange flush with the ground at the middle of the SOUTH tile edge. A small round
white status lens on the base, clear of the band.

== CAMERA ==
Looking steeply down from above, MOSTLY ROOF with only a shallow near face
visible, square to the tile grid: the near face parallel to the bottom edge of
the frame, the side faces parallel to the left and right edges. The square base
reads as a SQUARE, never a diamond. Not rotated corner-on, not a front
elevation. Match the attached sheet's hero view exactly.

== HARD REQUIREMENTS ==
- ONE machine, centred, filling the frame, nothing else in the image
- FULLY TRANSPARENT BACKGROUND. No ground, no floor, no shadow on the ground,
  no grid, no vignette, no backdrop of any kind
- THE CHARGE BAND IS UNLIT. Copper and brass as MATERIAL, dark, no glow at all.
  The lit version is derived from this plate, not drawn into it
- THE TOP IS CLOSED, BLUNT AND DARK. No cage, no electrode, no antenna, no rod,
  no finial, nothing reaching upward, nothing lit
- THE HELIUM INLET IS BARE MACHINE METAL. No frost, no rime, no ice, no pale
  blue, no lagging, no colour treatment of any kind on the pipe or its flange.
  It is the same metal as the machine
- The inlet is AXIS-ALIGNED on the SOUTH face, centre tile, stopping flush at
  the middle of that tile edge at GROUND LEVEL. Never diagonal, never out of a
  corner, never floating clear
- The STATUS LENS is PAINTED WHITE -- a plain white lens, not lit, not coloured,
  not glowing. The engine colours it in game
- NOTHING IS HOT AND NOTHING GLOWS anywhere on the machine
- No output chute, spout, bin, tray or opening of any kind
- No loose material, no charge, no cell, no canister, no cargo anywhere
- Nothing extends sideways past the square base
- No text, no labels, no logos, no wordmarks, no watermarks

== OUTPUT ==
One square image, the machine alone on transparency, sharp and clean at full
resolution, in the rendering and finish of the attached sheet.
```

# 15. Factorio Prototype — sketch

```lua
{
  type = "assembling-machine",
  name = "sae-ring-mast",
  crafting_categories = { "sae-ignition-charge" },
  fixed_recipe = "sae-ignition-charge",
  crafting_speed = 1,
  energy_usage = "12MW",
  energy_source = { type = "electric", usage_priority = "secondary-input" },
  surface_conditions = { { property = "pressure", min = 1, max = 9 } },
  module_slots = 0,
  allowed_effects = {},
  fluid_boxes = { --[[ 1 in, helium-3; see §8 ]] }
}
```

And the item that makes the ring a ring:

```lua
{
  type = "item",
  name = "sae-ignition-charge",
  stack_size = 10,
  spoil_ticks = 60 * 10   -- ten seconds; no spoil_result, so it simply goes
}
```

---

# 13. Sprite Dimensions — measured

Every number here was measured off the cut plate, not chosen.

| | |
| --- | --- |
| Master render | `concept/master-v1.png`, 1254 × 1254, transparent, trimmed to 1184 × 1115, aspect **1:0.94** against a vanilla 3×3's 1:0.96 |
| Colour plate | `base.png`, **200 × 191**, `scale = 0.5` |
| Drawn machine | **192 × 181 px** at (4, 5) — **exactly 3.000 tiles wide**, 2.83 tall |
| Rim | 4 px left and right, 5 px top and bottom; alpha zero on all four edge rows |
| Colour shift | **{ 0, +0.08594 }** |
| Shadow plate | `base-shadow.png`, **346 × 202**, `draw_as_shadow` |
| Shadow shift | **{ 1.14062, 0.17188 }** |
| Status lamp | `status-lamp.png`, 200 × 191 — the plate's own canvas. Lens at (62, 132)–(70, 141) |
| Icon | `graphics/icons/ring-mast.png`, 120 × 64 mipmap strip, from `icons/masters/ring-mast.png` |

**The shift is positive, and that is the interesting part.** The Drop Crusher is
taller than its footprint and needed pulling *up*; this building is **shorter**
than its footprint — 2.83 tiles of drawn height on a 3 tile box — so the
bottom-aligned box puts the footprint's centre 5.5 source px *above* the canvas
centre, and the plate is pushed **down** by 2.75 in-game px.

Vanilla agrees. `assembling-machine-3` is the other squat 3×3 and ships
196 × 192 at `by_pixel(-0.5, 2.5)` — **+0.078 tiles** against our +0.086.

**This is also what exposed a bug in `tools/check-footprint.py`.** It took the
tile pitch from the *narrower* visible axis, on the reasoning that a building
overhangs vertically and never horizontally — true of a tall building, false of a
squat one. On this plate it read the height as the footprint, inferred a 60.3 px
pitch instead of 64, and reported a plate cut to exactly 3.000 tiles as
overhanging 0.09 each side. It now takes the pitch from the width, and accepts a
rectangular footprint (`--tiles 2 5`) for the Crust Turbine.

**The icon is derived, not drawn, and it is unlit.** §16 asks for the coil band
*glowing*; the plate's band is unlit because the charge glow will be derived from
it, and an icon promising a light the entity cannot yet show would be a lie for
as long as that layer takes. The 32 px read and the Arc Mast test — §16's harder
requirement — are both met without it: a fat banded copper drum against a thin
lattice tower. Revisit when the charge animation is cut.

---

# 16. Icon

The coil band seen square on, glowing, with the blunt cap above and the buttressed
base below. Must read at 32 px as *"a charged collar"* — and must be
distinguishable from the Arc Mast's icon at that size, which is the harder
requirement.

---

# 20. Open questions

- ~~**Does spoilage tick inside a rocket silo's input inventory?**~~ **Answered
  by spike S11: yes, and cleanly.** Charges with no `spoil_result` simply vanish
  where they stand, and the Array does not jam — it keeps building parts for as
  long as a fresh charge is present, and loses only the ones that sat too long.
  That is the mechanic working, not failing.
- ~~**What happens to a part-built segment when the charge is gone?**~~ **Not a
  risk — S11 disproved it.** Ingredients are consumed at craft *start*: a charge
  inserted at `spoil_percent = 0.98`, about a fifth of a second from death against
  an eight-second craft, still produced a rocket part. Nothing can rot mid-craft
  and take a coil assembly with it.
- **How many masts, and does the number matter?** The brief makes throughput the
  only constraint, so the "ring" is however many masts keep up. If the ring should
  be a *specific* shape, that needs a different mechanic and probably a script —
  and would be worth its own entry in `design/ideas.md` rather than being smuggled
  in here.
- **It is blocked behind I1.** If radiation ever replaces the arc storms, this
  building's whole visual argument — *"the mast that is not the other mast"* —
  loses its counterpart, and §3.1 would need rewriting rather than reusing.
