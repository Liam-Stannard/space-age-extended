# Factorio Building — Art & Implementation Specification

**Ballast Drill.** First draft — a brief, enough to commission and judge a
concept sheet. Not a specification: §6, §12 and §13 stay open until a sheet is
approved and a canonical plate has been measured.

Named for what makes it work rather than for where it stands: the Core's own
drill, but "Core Drill" reads as a drill *for* cores, and every other building
here already says Core in its description.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | Whole design approved in one review | **draft — `concept/v1-sheet.png`**, not locked |
| 1 | Canonical view | portrait 2:3 | Silhouette approved against §3 | blocked on 0 |
| 3 | Directional frames | portrait 2:3 | **Four are needed** — see §5 | blocked on 1 |
| 5 | Working animation | portrait 2:3 | Loops without a visible seam | blocked on 3 |
| 6 | Icon | square | Legible at 32 px | blocked on 1 |

---

# 1. Building Overview

**Building Name:** `Ballast Drill`
**Internal Prototype Name:** `sae-ballast-drill`

**Building Type:** `mining-drill`, built fresh against vanilla's
`big-mining-drill` as the reference for proportions and for
`resource_drain_rate_percent`.

**Purpose:** Works kamacite ore **without wasting it.** Slower than an electric
mining drill and far hungrier for power, but it takes half as much out of the
patch for every ore it delivers.

**Why it matters:** kamacite patches *genuinely run out* (`decisions.md` D12) and
nothing else in the mod cares. This is the only building in the game whose
argument is "spend electricity to make a finite thing last", and on a planet
whose central tension is already electricity, that lands the trade in exactly the
right place.

**Locale:** *"Leans on the ore rather than tearing at it."* / *"Half the drain
for every ore delivered, at twice the power and two thirds the speed. The patch
is not coming back; the electricity is."*

---

# 2. Gameplay Dimensions

| | |
| --- | --- |
| Tile footprint | 5×5, matching the big mining drill |
| Directions | 4 |
| Resource categories | `basic-solid` |
| `mining_speed` | ~0.65 of the electric drill's, per ore |
| `resource_drain_rate_percent` | **50** — vanilla precedent: `big-mining-drill.lua:568` |
| Energy | 900 kW, electric, `secondary-input` |
| Surface conditions | `gravity` ≥ 45 — the Core alone |
| Module slots | 4 |

### Why it is not a reskin

`resource_drain_rate_percent` is the whole building. It is the one mining-drill
field that changes what a patch is *worth* rather than how fast it empties, and
vanilla uses it exactly once. Here it turns ore siting into a decision with a
cost attached, on the one planet where ore is finite by design.

**The gravity condition is the fiction and the balance in one line.** At 50 g the
drill can press down with its own mass instead of hammering, which is why it
wastes less — and it means the building cannot be carried to a world where ore is
effectively infinite and used as a straight upgrade.

---

# 3. Visual Design

## 3.1 Design Concept

A press, not a hammer. The machine's read is **weight brought to bear**: a broad
low chassis with a heavy ballast block riding above the cutting head, and legs
splayed wide enough that it is obviously bracing rather than standing.

**The anti-read is a derrick.** No tower, no headframe, no rotating superstructure.
Everything about this machine is low and wide, because its argument is mass.

## 3.2 Key Visual Features

* A **ballast block** — the tallest element, an unadorned slab of metal riding on
  four visible guide rails above the head.
* **Splayed bracing legs** at the four corners, each with a broad foot pad.
* A **cutting head** under the block, mostly hidden, seen only as a rim of
  disturbed ground.
* An **output boom** on one side, short and stubby.

### Signature Feature

**The ballast block descends and rises on the working loop** — a slow, heavy,
one-second stroke rather than a spin. It is the animation that says *this machine
is using gravity*, and it is the reason the building reads at a glance.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Chassis and legs | `#4A463F` → `#6E685C` | the mass of the building |
| Ballast block | `#2E2C29` | the slab, deliberately darker than everything |
| Guide rails | `#8A8580` | four verticals |
| Hazard banding | `#C8A23A` | leg feet only, sparingly |
| Ore dust | `#7A6A55` | ground disturbance under the head |

**No glow at all.** Nothing on this machine is hot or energised; it is a weight
on a rail. A drill that glows would read as a smelter.

---

# 4. Factorio Visual Style

## Technology tier and visual register

**Tier 0 — Foothold.** Crude and mechanical: bolted plate, cast legs, exposed guide rails, visible wear on the cutting head. A landing-day machine.

See the template's *"Technology tier sets the visual register"* — the player
should be able to read their progress off the factory floor without opening the
tech tree, so this building's surface treatment is set by where it sits on
`04-the-core.md` §6's ladder, not by taste.



5×5 and low, so the camera shows a great deal of roof and very little face — the
ballast block and the four rails carry the whole silhouette. Style reference to
attach: the **big mining drill**, cropped and upscaled, with the standing
disclaimer.

---


# 5. Building Orientation

* [x] North · [x] East · [x] South · [x] West

**Direction count:** `4`. The output boom points a different way in each, and a
drill whose boom does not match its belt is the single most confusing thing a
mining building can do.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| Ore out | `vector_to_place_result` `{ 0, −2.85 }` — the **north** face, centred | must match the boom tip in all four directions |
| Mining fluid in | four connections, vanilla's big-mining-drill layout | **declared, and nothing uses them yet** |
| Electric | no visible connector | poles reach it wirelessly |
| Items in | none | no inserter feeds this building |

```
          . . O . .        O = ore out, north face, centre
          . . . . .        W = fluid in, west face, one tile north of centre
      W . . . . . . E      E = fluid in, east face, one tile north of centre
          . . . . .        S = fluid in, south face, either side of centre
          . S . S .
```

**`vector_to_place_result` is the one number that cannot be guessed.** It has to
be measured off each directional plate so the ore appears at the boom's tip and
not through the chassis.

**This table used to say "Fluids: none; no `input_fluid_box`; this drill takes no
reagent".** That was true of the mechanic and wrong about the prototype, which
inherited four connections from the big mining drill all along. They were briefly
cleared and are now kept deliberately: **a mining fluid for this drill is wanted
later, and the layout has to be settled before the plate is cut.** A flange added
to a finished plate is a repaint of all four directions.

**The layout is vanilla's, verbatim**, and that is the reason to use it — a player
who has plumbed a big mining drill has already learned this one. North takes no
connection, because north is where the ore comes out.

**The plate draws none of them.** Vanilla's own drills carry no plumbing in their
art at all — the big mining drill's north sprite is a gantry and two ladders and
nothing else. The fitting is the fluid box's `pipe_covers`, and the engine stamps
it at whichever connections are live; **on an ore that needs no fluid it draws
nothing.**

That is what makes keeping the box free. Today the covers never appear. The day a
recipe asks for a fluid, the flanges appear by themselves, in the right places,
in all four directions, and no plate is repainted — which is the whole reason to
settle the layout now and draw nothing.

So: **no flange, no stub, no hose, no valve, no capped port anywhere on the
art.** Painting them in would put four visible sockets on a machine with no use
for them.

---

# 11. Generation Requirements

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio
Space Age mining machine, every panel drawn from the game's characteristic
45-degree top-down perspective. The machine is a broad low wide five-by-five
ore press standing on an airless metallic world, much wider than it is tall.
Four splayed bracing legs with wide foot pads reach out to the corners. A
heavy dark unadorned ballast slab rides above the centre on four short pale
vertical guide rails. Directly beneath the slab, a toothed circular cutting
head is set into the ground and mostly hidden, with only its rim showing. A
short stubby empty output boom projects from one side. Dark grey-brown armour,
charcoal ballast, pale grey rails, small yellow hazard banding on the foot
pads only. No tower, no derrick, no headframe, no glow, no flame, no smoke.
Panels: main view, front elevation, side elevation, a detail of the cutting
head beneath the raised slab, and the slab shown at the top and bottom of its
stroke. Title the sheet BALLAST DRILL. Draw no loose material anywhere: no
ore, powder, fibre, grit, debris or product on the ground, in bins, at chutes,
on trays or spilling from the machine. Factorio machines never show what they
make, so every chute, port, bin and tray is drawn as empty machinery. Every
pipe connection must run down to ground level and stop flush at the edge of
the tile footprint; no pipe may end in mid-air and none may leave the top of
the building. Nothing may extend past the tile footprint, pipework included,
and the tile-grid panel must show the whole machine inside the grid with no
overhang.
```

---


## Master Concept Prompt

Stage 1. **Attach `graphics/entity/ballast-drill/concept/adopted/B-sheet.png` and
nothing else** — same machine as the sheet's hero view, not a new design.

**The ring is RAISED.** This plate is the top of the press stroke and the frame
the animation is cut from; a ring drawn seated would bake the bottom of the
stroke into the still machine.

**The output is rebuilt.** The adopted sheet drew an upright boom. It becomes a
low drag-chain chute set into the north face — measured off vanilla, with the
numbers in `ballast-drill-options/README.md`.

```text
FACTORIO SPACE AGE BUILDING SPRITE -- MASTER PLATE

Redraw the machine in the ATTACHED SHEET's hero view as a single clean game
sprite. Same building, same design, same camera. Do not redesign it, do not
add or remove parts except where this brief says so, and do not draw any
panels, labels, text, borders or background furniture.

== WHAT IT IS ==
The Ballast Drill: a 5x5 mining machine on an airless metal world at fifty
gravities. It does not hammer and it does not spin -- it brings weight to bear.
A low riveted deck fills the footprint. A short capped central column rises from
its middle, blunt and closed. A heavy cast BALLAST RING, an annulus almost the
full width of the machine, rides around that column with deep chamfers and cast
webs across its top face. Three guide columns spaced round the ring, each with a
visible shoe wrapping it. A hammered landing shoulder at the base for the ring to
seat on. Compact geared winch housings at two of the three columns, gears
exposed. Riveted seams, bolt lines, lifting lugs, cable cleats, honest wear.

== THE OUTPUT, WHICH IS THE ONE CHANGE FROM THE SHEET ==
The attached sheet drew a tall upright boom. REPLACE IT. This machine gets a
SHORT DRAG-CHAIN SCRAPER CONVEYOR SET INTO THE NORTH FACE at ground level:
sloping down and forward out of the deck, a chain-and-flight bed running in a
guarded channel, a small drive sprocket at its head. It is BUILT INTO the
machine, not bolted on top of it. Its mouth is FLUSH WITH THE NORTH TILE EDGE.
NOTHING about it rises above the roofline and NOTHING overhangs the footprint.
It is drawn EMPTY -- the ore is placed by the engine in front of the mouth and is
never painted into the sprite.

== CAMERA ==
Looking steeply down from above, MOSTLY ROOF with only a shallow near face
visible, square to the tile grid: the near face parallel to the bottom edge of
the frame, the side faces parallel to the left and right edges. The square deck
reads as a SQUARE, never a diamond. Not rotated corner-on, not a front
elevation. Match the attached sheet's hero view exactly.

== HARD REQUIREMENTS ==
- ONE machine, centred, filling the frame, nothing else in the image
- FULLY TRANSPARENT BACKGROUND. No ground, no floor, no shadow on the ground,
  no grid, no vignette, no backdrop of any kind
- THE BALLAST RING IS RAISED, clear of the landing shoulder, at the top of its
  travel, with the guide columns visible beneath it
- DRAW NO FLUID FITTINGS AT ALL: no flange, no pipe stub, no hose, no valve, no
  manifold, no capped port, anywhere on the machine. Vanilla's own drills carry
  no plumbing in their art; the engine stamps the fitting at whichever
  connections are live, and draws nothing on an ore that needs no fluid
- THE LAMP LENS is PAINTED WHITE -- a plain white lens, not lit, not coloured,
  not glowing. The engine colours it in game
- NOTHING IS HOT AND NOTHING GLOWS anywhere on the machine
- The cutting head is PART OF THE MACHINE: a shrouded rim under the deck. No
  disturbed earth, no crater, no spoil ring, no ground texture
- No loose ore, rock, spoil, powder, grit, dust or debris anywhere
- Nothing extends sideways past the 5x5 deck, the chute included
- No tower, no headframe, no mast, nothing reaching upward
- No text, no labels, no logos, no wordmarks, no watermarks

== OUTPUT ==
One square image, the machine alone on transparency, sharp and clean at full
resolution, in the rendering and finish of the attached sheet.
```

# 15. Factorio Prototype — sketch

```lua
{
  type = "mining-drill",
  name = "sae-ballast-drill",
  resource_categories = { "basic-solid" },
  mining_speed = 0.65,
  resource_drain_rate_percent = 50,   -- big-mining-drill.lua:568 is the precedent
  energy_usage = "900kW",
  energy_source = { type = "electric", usage_priority = "secondary-input" },
  surface_conditions = { { property = "gravity", min = 45 } },
  module_slots = 4,
  vector_to_place_result = { --[[ measured per direction; see §8 ]] }
}
```

---

# 16. Icon

The ballast block on its rails, seen square on, with the cutting head as a dark
rim beneath. Must read at 32 px as *"a weight on a drill"* — if it reads as a
plain drill, the icon has failed, because the weight is the entire building.

---

# 20. Open questions

- **Does it replace the electric drill or sit beside it?** The brief assumes
  beside: the vanilla drill stays available and stays faster, so the choice is
  live on every patch. If playtesting shows nobody ever builds the fast one, the
  fix is to widen the speed gap, not to remove the option.
- **Interaction with mining productivity.** `uses_force_mining_productivity_bonus`
  is on by default, and productivity already reduces effective drain. Check the
  two do not stack into an ore patch that is functionally infinite.
