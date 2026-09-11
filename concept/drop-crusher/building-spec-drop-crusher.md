# Factorio Building — Art & Implementation Specification

**Drop Crusher.** The design is locked: **option A, the Sealed Hammer**, chosen
2026-09-09 from a five-option round drawn against itself. The decision record is
`drop-crusher-options/`, the sheet is `concept/adopted/A-sheet.png`, and the four
rejected designs are gone, and the plate is cut, measured and in the engine —
see §13. What is left is the stroke: the crown does not move yet, and §9 records
exactly what that needs.

**This building is forced, not optional.** Vanilla's `crusher` carries
`surface_conditions` of `gravity` min 0 **max 0** — it is space-only
(`space-age/prototypes/entity/entities.lua:841`). Beneficiation on the Core's
surface cannot exist without a new crusher, so this is the first thing the
production tree needs and the first thing that should be built.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **draft — `concept/v10-sheet.png`**, variant B, not yet locked |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3 | blocked on 0 being locked |
| 5 | Working animation | — | The drop loop reads as a drop | **built** — derived from the plate by Animatorio, not generated; see §9 |
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

**A sealed hammer.** *(Locked to `concept/adopted/A-sheet.png`, the Sealed Hammer,
2026-09-09. The earlier "variant B of `concept/variants-v4.png`" lock was a
refinement of one idea; this one was drawn against a sibling.)*
A **tall armoured cylinder** ringed by external buttresses, with the forged
weight's crown seated in a collar at the centre of its flat roof. The crushing
chamber, the anvil bed and the whole stroke are **inside**; what the player sees
from outside is the crown riding up clear of its collar and slamming back down
flush.

**The weight is lifted, not levitated.** A crown that simply rises out of a ring
with nothing touching it reads as floating. The roof therefore carries the
mechanism that does the work: geared drums winding the weight up a rack cut into
its shank, and a trip pawl that kicks clear to drop it. This is how a real board
drop hammer behaves — wound up, then released — and it puts moving machinery on
the surface the camera shows most of, which the roof previously lacked entirely.

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
* **Lift gear on the roof**, flanking the collar: a pair of heavy toothed gears
  meshing with a **vertical rack** cut into the weight's shank, driven by a
  compact geared motor housing on one side.
* A **trip pawl** — a stout sprung lever beside one gear that visibly engages the
  rack and kicks clear to release the weight.
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
| Hazard banding | `#C8A23A` | the base plate edge only |
| Lift gear | `#8A857C` | gears, rack, pawl and collar — brighter than the armour, so the mechanism reads as a separate assembly |
| Lamp lens | `#FFFFFF` | painted white; the engine tints it via `status_colors` |
| Copper and brass | `#8A5A32` → `#C88A4A` | bus runs, gear furniture, bearing caps, bolt lines |

*The "ore and fines" row is gone with the chutes it described.* **The copper row
is not decoration and is worth defending:** a building drawn to the four grey
rows above measures below vanilla's saturation floor by arithmetic — fifteen
sheets in an earlier round proved it, the worst at 0.136. The adopted sheet says
copper is used freely and measures **0.264**, inside the band. The discipline
that comes with it: copper is a *material* and never glows, so it can never be
mistaken for the lamp.

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

## Technology tier and visual register

**Tier 0 — Foothold.** Crude and mechanical: riveted plate, cast housings, exposed gears, rack and pawl, weld seams, hazard tape, honest wear. **Its visible gearing is correct because of its tier and must not be modernised** — it is the baseline the endgame is measured against.

See the template's *"Technology tier sets the visual register"* — the player
should be able to read their progress off the factory floor without opening the
tech tree, so this building's surface treatment is set by where it sits on
`04-the-core.md` §6's ladder, not by taste.



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

**There are no chutes, and this line used to say there were.** §3.2 settled it —
an `assembling-machine` has one output inventory and no output *position*, so a
chute promises the player something the entity cannot keep, and the adopted sheet
draws none. The old text here described them as "honest decoration in the way a
vanilla furnace's hopper is"; a vanilla furnace's hopper is an *input* read, and
this building's inputs are unconstrained too. Struck rather than reconciled.

---

# 11. Generation Requirements

## Concept Sheet Prompt

**Stage 0 is done and the prompt that produced the adopted sheet lives with it**,
at `drop-crusher-options/A-sealed-hammer.md`. It is not copied here, because two
copies of a prompt is two copies to drift — the same reason
`tools/generate-building-art.py` reads prompts out of the markdown rather than
keeping its own.

The prompt that used to sit here is superseded. It described the machine before
the five-option round and before the status lamp existed, and it asked for a
`3x3 tile grid top view` — a panel this project has stopped requesting, because
a generator has no idea where the tile edges are and drew a grid that never lined
up. Footprint is measured on the real plate with `tools/check-footprint.py`.

## Master Concept Prompt

Stage 1. **Attach `concept/adopted/A-sheet.png` and nothing else** — this is the
same machine as the sheet's hero view, not a new design, and any second reference
invites a second building (see the art backlog (now `TODO.md`)'s warning).

**The crown is SEATED.** This plate is frame 0 of the stroke and the thing the
animation is cut from; a crown drawn half-raised would bake a mid-stroke position
into the still machine.

```text
FACTORIO SPACE AGE BUILDING SPRITE -- MASTER PLATE

Redraw the machine in the ATTACHED SHEET's hero view as a single clean game
sprite. Same building, same design, same camera. Do not redesign it, do not
add or remove parts, and do not draw any panels, labels, text, borders or
background furniture.

== WHAT IT IS ==
The Drop Crusher: a sealed 3x3 impact crusher on an airless metal world. A tall
armoured cylinder with a slightly tapered wall on a square riveted base plate,
ringed by external buttresses. A hard machined collar at the centre of its flat
roof with the forged drop weight's chamfered crown SEATED FLUSH in it. Heavy
toothed lift gears flanking the collar, meshing a vertical rack cut into the
weight's shank, with a compact geared motor housing to one side and a sprung
trip pawl engaging the rack. An armoured inspection hatch with radial locking
dogs on the front face. Riveted seams, bolt lines, lifting lugs, cable cleats.

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
- THE CROWN IS SEATED FLUSH in its collar and the collar's rim is UNBROKEN
- The LAMP LENS is PAINTED WHITE -- a plain white lens, not lit, not coloured,
  not glowing. The engine colours it in game
- NOTHING IS HOT AND NOTHING GLOWS. No warm light anywhere on the machine
- No output chute, spout, bin, tray or opening of any kind
- No pipes, no flange, no hose, no fluid connection anywhere
- No loose ore, powder, grit, dust or debris anywhere
- Nothing extends sideways past the square base plate
- No text, no labels, no logos, no wordmarks, no watermarks

== OUTPUT ==
One square image, the machine alone on transparency, sharp and clean at full
resolution, in the rendering and finish of the attached sheet.
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
  module_slots = 2,
  -- Shipped 2026-09-10; see prototypes/core/machines.lua for the real thing and
  -- §13 for where every number came from.
  graphics_set =
  {
    animation = { layers = { base.png 200x206 shift {0,-0.03125},
                             base-shadow.png 358x217 draw_as_shadow
                                             shift {1.23438,0.05469} } },
    working_visualisations =
    {
      { always_draw = true, apply_tint = "status",
        animation = { status-lamp.png 200x206, draw_as_glow = true } }
    }
  }
}
```

---

# 16. Icon

**Done 2026-09-10 — `graphics/icons/drop-crusher.png`, derived from the master
render rather than generated separately (§13).** The instruction below stands as
the record of what was asked for and why.

**Redraw from the adopted sheet; the old text here described a building that no
longer exists.** It asked for "the carriage mid-fall between two posts, with the
anvil beneath" — the open-frame design that versions 3 to 6 replaced, with an
anvil this machine has sealed inside it and posts it does not have.

The icon should be the **crown standing proud of its collar**, cropped tight, on
the buttressed roofline. Must read at 32 px as *"something heavy about to
drop"* — the lift gear, the pawl and the hazard banding are all too fine to
survive at that size and should not be attempted.

---

# 20. Open questions

**Both of the questions this section used to ask are now closed by the code, and
neither affects the art.**

- ~~**One recipe or two?**~~ **One**, with two products, as implemented:
  `sae-crushing` takes 2 kamacite ore to 3 crushed kamacite and 1 fines. The
  question mattered because it decided "whether the two chutes are simultaneous
  or alternate" — and there are no chutes (§8), so it no longer touches the
  plate. A coarse/fine split remains available as a branch if T1 ever wants one.
- ~~**Do the fines have a home yet?**~~ **Yes, two.** `sae-fines-smelting` takes
  4 fines to a kamacite plate, and `sae-metal-carbonyl` takes 4 more into the
  carbonyl line. T3 exists.

Still open, and this one is new: **the moving part is about a third of the box**,
against 72–113 % on the three vanilla machines it stands beside. See the adopted
option's page — it is the first thing stage 1 should push on.


---

# 19. Design Notes / Iteration History

### Round 11 — five options, and the first comparison this building ever had

**Versions 1 to 10 are all the same idea.** That is the finding, and it took
until now to say it: ten sheets of refinement, each a better version of its
predecessor, and not one of them ever asked whether a sealed vertical hammer was
the right answer. `drop-crusher-options/README.md` opens with the method the
Ignition Array arrived at after four sets and twenty concepts — *compare, do not
refine* — and this building had never been through it.

Five designs were written against each other: the Sealed Hammer (the incumbent,
carried as a fair comparison), the Twin Tower, the Beam Engine, the Ratchet Crown
and the Skip Tower. Two were drawn. **A won**, and it is the incumbent — which is
worth knowing, and is exactly the thing ten rounds of refinement could not have
told anyone.

**What the round added to the brief:**

- **A status lamp**, which this building never had. §3.3 says nothing here is
  hot, so the Drop Crusher is the one machine in the set where a single white
  lens carries the whole idle/running/blocked read with no warm light to help it.
- **The animation gate, applied before the plate exists.** Each option was
  measured for how much of its own box moves. The adopted design is the weakest
  of the five at ~33 %, against 72–113 % on the vanilla machines it stands
  beside — see §20.
- **Copper, unrationed.** The palette had no warm metal in it at all and would
  have measured below vanilla's saturation floor by arithmetic.

**And it found two contradictions in this document**, both now struck rather than
reconciled: §8 still promised chutes that §3.2 had already argued away, and §16's
icon described the open-frame design that versions 3 to 6 replaced.


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


### Version 10 — the weight is lifted, not levitated

Liam's catch on the animation: the weight rose out of its collar with nothing
touching it, so it read as floating rather than as being hauled up and dropped.

The roof now carries the mechanism that does the work — a pair of heavy toothed
gears meshing with a rack cut into the weight's shank, a geared motor housing at
one side, and a sprung trip pawl that engages the rack and kicks clear to
release. That is how a board drop hammer actually behaves: wound up, then let go.

**It also fixes something the sheet had not solved.** The roof is the surface
this camera shows most of, and until now it held only a collar and a blank
weight. Putting the lift gear there gives the most-visible face of the building
something mechanical to look at, and it is the reason v10 reads as a machine
rather than as a lid.

The four frames now describe a cycle rather than a position: seated with the pawl
engaged, gears turning and the weight climbing the rack, at the top with the pawl
kicking clear, fallen with the gears freewheeling.

New palette entry, `#8A857C` for the gear, rack and pawl — deliberately brighter
than the armour so the mechanism reads as a separate assembly rather than as more
shell.


---

# 9. Working Animation — what the engine will and will not do

**Yes, the gears will turn in game.** `WorkingVisualisations.animation` on a
crafting machine plays while the machine is crafting, so the gears, the rack and
the pawl are all just authored frames. Three constraints shape how they have to
be drawn.

**1. It loops; it cannot fire once per craft.** An assembling machine has no
"play this once when a craft completes" hook — the animation runs continuously
while working and stops when it stops. So **one drop does not equal one item**,
and the animation must not imply that it does. Draw it as a *rhythm* — a hammer
that keeps hammering for as long as the machine is running — rather than as a
discrete event. Vanilla assemblers work the same way and nobody notices.

**2. Playback speed scales with crafting speed.** `constant_speed` defaults to
false, so the animation is *adjusted to the machine speed*: modules and beacons
will make the gears spin and the hammer fall faster. That is the right behaviour
here and should be left alone — a sped-up drop hammer reads as a machine working
harder. Set `constant_speed = true` only if the fall ever looks silly at speed.

**3. The fall has to be faked in the frame spacing.** Frames play at a constant
rate, so a weight that falls at a constant rate looks like it is being *lowered*.
The acceleration must be baked into **frame spacing**: many frames through the
slow wind-up, progressively fewer through the fall, and a hard stop at the
bottom. Budget roughly two thirds of the frame count to the rise and the pawl
trip, and the last third to the fall and impact.

**One authoring gotcha, from the prototype docs:** `idle_animation` **must have
the same frame count as `animation`**. So a 24-frame working animation cannot
pair with a 1-frame idle — the idle would have to be 24 frames of the machine
sitting still, weight seated and pawl engaged. Budget for it, or omit
`idle_animation` entirely and let the machine simply stop on a frame.

### Where this stands — the stroke, and what measuring it overturned

**Shipped 2026-09-10:** the master plate, its cast shadow, the status lamp and
the icon, all wired in `prototypes/core/machines.lua`. The building no longer
wears `assembling-machine-3`'s sprites and no longer appears in the data stage's
placeholder report.

**Shipped 2026-09-10, second pass: the stroke moves.** It came out of
[Animatorio](https://github.com/Onoulade/Animatorio), a sprite-sheet generator
for exactly this — declare a moving region in JSON and it renders the frames.
The asset is `stroke.json` beside the plate; the cut is
`tools/build-animatorio-layers.py`. **Three of the four things this section
predicted turned out to be wrong**, and the corrections are worth more than the
result:

1. **"It can only travel upward" — it cannot travel upward at all.** The crown is
   the *topmost thing on the plate*: its first opaque row is **7**, against a
   canvas rim that has to stay clear to row 4. Two pixels of headroom. Rising is
   not available at this canvas size, and no mask recovers it. The plate is the
   **top** of the stroke and the frames fall from it — the exact opposite of what
   this section assumed.
2. **"Sliding it down would draw it over the collar's front rim" — only if you
   let it.** A fixed clip window ending on row 50, the rim's top edge, means
   nothing below the rim can be touched, so the shank slides *behind* it. In
   Animatorio that is one field (`mask_polygon`); the shaped case is a
   `source_occluder` layer. The occlusion was never the hard part.
3. **"The vacated region is not roof, it is shank" — the shank is already
   drawn.** Look at the plate at 8×: below the crown is a full shank, rows 31 to
   50, with the **rack cut into it**, running down into the collar throat. So the
   crown and the shank travel as one rigid part, and the rack's rungs pay out of
   the collar as the weight is hoisted. That travelling rack turned out to sell
   the stroke better than the crown does.

What was *right* is point 1's premise — a rectangular cut takes collar pixels —
and the frame-spacing rule above, which is the one thing the tool could not do.

**The tool's one real gap, and the way round it.** Animatorio's `piston` offers
`sine` or `triangle`, both symmetric: the fall takes as long as the rise, which
is precisely the "looks like it is being *lowered*" failure this section warns
about. Its phase-to-displacement map is `t = 0.5 − 0.5·cos(2πp)`, monotonic on
`p ∈ [0, ½]`, so it inverts — pick the displacement per frame, solve back for the
phase, ask the tool for *that* frame. Nothing is patched. The loop is **16 frames
of constant-speed geared rise and 8 of a fall whose distance goes as t²**, which
is this section's two-thirds/one-third, and the last increment of the fall is the
largest, which is the hard stop at impact.

**Frame 0 is `base.png`, byte for byte** — asserted by the tool, not hoped for.
The handler returns without touching the frame at zero displacement, and the loop
is ordered to start at the top of the stroke so that it does. This is what
answers §9's `idle_animation` gotcha above: there is no idle animation, the
machine stops on a frame, and the frame it stops on is the approved still.

**Drawn the way the biochamber is.** Not 24 copies of a 200 × 206 plate: a static
housing with a 48 × 54 window punched out and 24 frames of that window over the
hole — `space-age/prototypes/entity/biochamber-pictures.lua` does the same with
`frame_count = 1, repeat_count = 64`. **103,408 px of atlas against 988,800**,
and the tool reassembles every frame from the two layers and requires it to match
Animatorio's own composite exactly before it will write anything.

**The share of the box, and it is not good.** Measured, against the 72 %, 101 %
and 113 % of the three vanilla machines this stands beside:

| | |
| --- | --- |
| Moving part | 34 × 46 px in a 192 × 196 machine |
| Share of the machine's width | **17.7 %** |
| Swept box, with the 14 px travel | 34 × 60 px — 30.6 % of its height |
| Pixels that ever change | **4.6 %** of the drawn machine |

That is the Dross Classifier's problem again, and better only in degree — its
drum was 5.2 %. §3.2 asks this stroke to "carry the whole read" and be legible
"across the base", and at 17.7 % of the width it will not be. **The cause is
upstream of the animation**: §3.2 describes a weight that *climbs the posts*
above the roofline, and the plate drew a sealed cylinder with a cap standing
proud of a collar. Nothing downstream of the master plate can enlarge it — the
options are to accept a subtle stroke or to re-cut the plate, and that is a
decision for §20, not for this section.

**What was left out, deliberately.** The two lift gears flanking the collar are
large enough to change the share materially, and Animatorio has `mechanical_gear`
for them — but a rack-driven gear has to *reverse with the stroke*, and that
layer only spins continuously. It would be turning while the crown sits at the
top. The cast shadow is also still one frame; the crown's shadow is a small part
of a plate nearly twice the machine's width, and cutting it apart is a second
mask for something no player looks at.

---

# 13. Sprite Dimensions — measured

Every number here was measured off the cut plate, not chosen.

| | |
| --- | --- |
| Master render | `concept/master-v1.png`, 1254 × 1254, transparent, trimmed to 1154 × 1175 |
| Colour plate | `base.png`, **200 × 206**, `scale = 0.5` |
| Drawn machine | **192 × 196 px** at (4, 5) — **exactly 3.000 tiles wide**, 3.06 tall |
| Rim | 4 px left and right, 5 px top and bottom; **alpha zero on all four edge rows**, checked |
| Colour shift | **{ 0, −0.03125 }** |
| Shadow plate | `base-shadow.png`, **358 × 217**, `draw_as_shadow` |
| Shadow shift | **{ 1.23438, 0.05469 }** |
| Status lamp | `status-lamp.png`, 200 × 206 — the plate's own canvas, so it registers by construction. Lens at (93, 81)–(105, 92) |
| Icon | `graphics/icons/drop-crusher.png`, 120 × 64 mipmap strip |
| Stroke housing | `stroke-housing.png`, **200 × 206** — the plate with the window cut out. Same canvas, same `scale` and `shift` as `base.png`, so it needs no numbers of its own |
| Stroke frames | `stroke.png`, **288 × 216** — 24 frames of 48 × 54, `line_length = 6` |
| Stroke window | **(79, 0)–(127, 54)** on the plate |
| Stroke shift | **{ 0.046875, −1.21875 }** |

**The stroke layer's shift is arithmetic, not a fit.** The window's centre is
(103, 27) on a canvas whose centre is (100, 103) — 3 source px right and 76 up.
At `scale = 0.5` there are 64 source px to the tile, giving 3/64 = 0.046875 and
−76/64 = −1.1875, and the plate's own −0.03125 adds to the second to make
−1.21875. Every one of those is an exact sixty-fourth; none was rounded to get
there, which is the test that the window was placed on whole pixels.

**The window must be even in both axes** or its centre lands on half an in-game
pixel at `scale = 0.5`. `tools/build-animatorio-layers.py` refuses an odd one.

**Verified in the engine, not just in the tool.** A layered animation whose
layers disagree on frame count is a *sprite*-stage failure, and the data stage
never opens an image — `tools/check-data-stage.sh` passes a mod that cannot draw.
Loaded the client under a virtual framebuffer instead: **`Sprites loaded` at
22.4 s, `Factorio initialised`, no error lines.**

**The shift is measured rather than centred, and this is the part worth keeping.**
The building is taller than it is deep, so the drawn 3 × 3 box is bottom-aligned
inside the content: it occupies rows 9–201 of a plate whose canvas centre is row
103, putting the footprint's centre 2 source px low. Two source px is one in-game
px at `scale = 0.5`, which is `1/32` of a tile — hence −0.03125. Centring the
plate instead would have put the building one screen pixel deep into its own
southern tile.

`tools/check-footprint.py base.png --tiles 3` reports 0.00 tiles of overhang left
and right and passes.

**The icon is derived, not drawn.** It is the crown-and-collar region of the
master render, masked to the collar disc plus the crown, run through
`tools/key-icons.py`. That follows §16's instruction — "the crown standing proud
of its collar, cropped tight" — and follows this project's habit of deriving a
layer from an approved plate rather than commissioning a second render that can
disagree with the first.
