# Factorio Building — Art & Implementation Specification

**Crust Tap.** The design is locked: **option A, the Bolted Collar**, chosen
2026-09-09 from five drawn against each other and regenerated twice for the pipe
connection. The decision record is `crust-tap-options/`, the sheet is
`concept/adopted/A-sheet.png`, and the four rejected designs are gone. §6, §12
and §13 stay open until a canonical plate exists and has been measured.

**This brief covers two prototypes**, and that is a design decision rather than
an accident — see §2. The tap raises a gas; a companion turbine burns it. The tap
sells **pressure, not heat**, and that single choice is what keeps it simple.

---

# 0. Generation Contract

| # | Asset | Canvas | Gate before moving on | State |
| - | ----- | ------ | --------------------- | ----- |
| 0 | Concept sheet | landscape 3:2 | **Both** prototypes approved in one review | **draft — `concept/v1-sheet.png`**, not locked |
| 1 | Canonical view — tap | portrait 2:3 | Silhouette approved against §3 | blocked on 0 |
| 1b | Canonical view — turbine | landscape | May be derived; see §20 | blocked on 0 |
| 4 | Glow / frost plate — tap | portrait 2:3 | Differenced against the unlit plate | blocked on 1 |
| 6 | Icons | square | Both legible at 32 px | blocked on 1 |

---

# 1. Building Overview

**Building Name:** `Crust Tap`
**Internal Prototype Name:** `sae-crust-tap`

**Building Type:** `offshore-pump`. Chosen for one reason: an offshore pump is
the only prototype in the game that **produces a fluid from nothing**, which is
exactly what a bore into a still-pressurised planetary interior should do.

**Purpose:** The Core's landing-day power. A tap sunk into the crust vents
**crust gas** — its own high-pressure gas, held down there since the world
formed — and a companion turbine burns it for a modest, permanent trickle of
electricity.

**Why it matters:** it closes the only genuine hole in the Core's opening hours.
Solar is `0`, nothing burns at pressure 5, the melt line needs helium and machines
the player has not built yet, and arc storms are episodic. Everything else on this
planet requires a factory to already exist. This does not.

**The surface reads 5 and the interior does not.** That pressure gradient is the
building's whole argument, and it is the one physical fact about the Core that
nothing else in the mod spends.

**Locale:** *"The inside of this planet is still under pressure. This is the hole
you let it out of."* / *"Not much power, and it will never be much. But it is
there the hour you land, and it does not care whether the sky is doing
anything."*

---

# 2. Gameplay Dimensions

## The tap

| | |
| --- | --- |
| Tile footprint | 2×2 |
| Directions | 4 (the outlet faces a different way in each) |
| Output | `sae-crust-gas`, ~30/s |
| Energy | none — an offshore pump needs no power to run |
| Surface conditions | `gravity` ≥ 45 — the Core's surface alone |
| Placement | **on a crust vent tile only** — see below |

## The companion turbine

| | |
| --- | --- |
| Prototype | `generator`, `sae-crust-turbine` |
| `burns_fluid` | **`true`** |
| Fluid box filter | `sae-crust-gas` only |
| Output | ~1.8 MW per turbine |
| Surface conditions | `pressure` ≤ 9 |

**Roughly one turbine per tap, and about 1.8 MW for the pair.** That is deliberate
and it should stay small: a foothold, not a power strategy. A player who tiles
fifty taps should still find the melt-and-steam line the better answer by a wide
margin, or the Core's central tension is undercut by its own tutorial.

### The tap is sited — measured, not assumed

**Spike S10 changed this brief.** An offshore pump draws its fluid from
`TilePrototype::fluid` on the tile beneath it, **not** from its own fluid box
filter. Placed on bare ground it builds happily, reports `status = working`, and
produces nothing at all — `get_fluid_source_fluid()` returns `nil`. That is the
same silent failure as S9 and it would pass every check in the repo.

So the tap needs a **crust vent tile** carrying `fluid = "sae-crust-gas"`, and
`tile_buildability_rules` requiring it. Which makes the Crust Tap a **fourth
sited resource** beside ore, melt vents and gas vents, rather than a building the
player tiles at will.

That is a better design than the first draft assumed — power becomes a place you
go rather than a thing you spam, and the cap is enforced by the map instead of by
a tuning number — but it is a **larger build**: a tile prototype, an autoplace
entry in `prototypes/core/map-gen.lua`, and tile art on top of the building's own.
`tools/build-whisker-bed-tile.py` and the whisker bed are the precedent for the
tile half.

### Pressure, not heat — and why that is the whole simplification

A `generator` with **`burns_fluid = true`** takes its power from the fluid's
`fuel_value` and ignores temperature entirely. So `sae-crust-gas` carries a
`fuel_value` and can sit at any temperature at all, and the tap never has to
declare one.

**Measured in S10:** a turbine burning gas at 25 °C with `fuel_value = "200kJ"`
produced **30,000 J/tick — exactly 1.80 MW**, its declared `max_power_output`,
under load. Temperature genuinely does not enter into it.

**One gotcha, also from S10:** `maximum_temperature` is **mandatory on a
`generator` even when `burns_fluid` is true**. Leaving it out fails the data stage
outright with `Key "maximum_temperature" not found in property tree`. It does no
work in this mode; it still has to be declared.

That matters because the obvious alternative is a trap. Vanilla `steam` has
`default_temperature = 15` (`base/prototypes/fluid.lua:42`) and an offshore pump
has **no field to set an output temperature** — it emits its fluid at that fluid's
default. A tap plumbed to vanilla steam would therefore produce cold steam and
**no power at all**, while loading, dumping and reporting perfectly normally: the
same shape of silent failure that `day-night-cycle = 0` caused for the arc storms
in spike S9.

Space Age already ships fluids whose energy is a fuel value rather than a
temperature — `thruster-fuel` and `thruster-oxidizer` both carry
`fuel_value = "50kJ"` at `default_temperature = 25`
(`space-age/prototypes/fluid.lua:133,145`) — so the pattern is established, even
though those two are burned by a `thruster` rather than a generator.

### Why it is not a reskin

An offshore pump that is not on water, vents a gas, and is gated to the heaviest
world in the game is not a water pump. More to the point: nothing else in Space
Age gives a planet a **free, sited, permanently modest** power floor. Every
vanilla world's opening power is either burned or shone on.

---

# 3. Visual Design

## 3.1 Design Concept

A wellhead holding something back. The building is a **capped bore** — a squat
armoured collar clamped over a hole in the crust — and every feature on it exists
to contain pressure: heavy ground anchors, a thick collar, and a single choked
riser leaving one side.

**This is the adopted design and it beat four alternatives**: a driven wedge, a
cross-yoke, a screwed gland stack and a flush plate. It won because it is the
most direct statement of the building's argument, not the most distinctive
shape — see `crust-tap-options/README.md`.

**The anti-read is the offshore pump.** Vanilla's is a light open frame standing
in water with a visible impeller, and every part of that is wrong: there is no
water, no impeller, and nothing about this should look light.

**The second anti-read is a lava tap.** This is not a hot-fluid building. The heat
is underground and stays there; what comes out is cold, because gas that expands
does.

## 3.2 Key Visual Features

* An **armoured collar**, low and heavy, clamped down with visible ground anchors
  — this thing is holding something in.
* A **choked riser** leaving one side and turning horizontal, visibly narrower at
  the throat than at either end.
* A **burst disc** — a small bulging plate on the collar's shoulder, the honest
  admission that this could go wrong.
* **Frost** on the riser downstream of the choke, and a **thin dull heat line** in
  the ground joint beneath the collar.

### Signature Feature

**The two-temperature read: hot underneath, cold coming out.** A dull orange seam
where the collar meets the ground and a pale frost jacket a few pixels away on the
riser. It is physically exactly right — gas cools as it expands — and it is a
silhouette-level cue no other building in the mod has. It also says *pressure*
rather than *heat* in one glance, which is the whole point of the building.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| Collar and anchors | `#3E3B36` → `#5E584E` | the mass of the building |
| Riser body | `#8A8580` | the single pipe |
| Frost jacket | `#BFD8E8` → `#EAF4FA` | riser, downstream of the choke only |
| Seam heat | `#C8541E` → `#E8A24A` | ground joint only, dull |
| Burst disc | `#C8A23A` | one small plate |
| Scorched ground | `#2E2A26` | tight ring at the base — **its own layer, never the plate** |

**The scorched ring is ground scatter and belongs in its own layer**, the way
vanilla does it with `mining_drill_scorch_mark`. Baked into a 2×2 plate it would
cross the collision box, which is the template's §8 rule 4. The concept sheets
draw no ground at all, deliberately.

**Dull orange, not bright, and only at ground level.** This is conducted heat
through metal, not a flame. The frost must be close enough to the seam that both
are legible in the same glance — that adjacency *is* the signature.

---

# 4. Factorio Visual Style

## Technology tier and visual register

**Tier 0 — Foothold.** Crude and mechanical: heavy bolted collar, ground anchors, a burst disc that is plainly a safety afterthought. The first thing built on the planet.

See the template's *"Technology tier sets the visual register"* — the player
should be able to read their progress off the factory floor without opening the
tech tree, so this building's surface treatment is set by where it sits on
`04-the-core.md` §6's ladder, not by taste.



2×2 and very low, so the camera sees almost entirely roof and the ring of scorched
ground. That is the right emphasis: the interesting thing about this building is
where it is, not how tall it is. Style reference to attach: the **pumpjack**,
cropped and upscaled, for the wellhead read. **Do not attach the offshore pump.**

---

# 5. Building Orientation

* [x] North · [x] East · [x] South · [x] West

**Direction count:** `4`. The riser is the fluid box, and a riser pointing the
wrong way is the fluid box in the wrong place.

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| `sae-crust-gas` out | the riser's tip, at `fluid_box.pipe_connections` | must match the art in all four directions |
| Electric | none | the tap draws no power |
| Items | none | no inserter ever touches this building |

**A correction, checked against vanilla's own offshore pump rather than
remembered.** This table used to say the gas leaves at `fluid_source_offset`. It
does not: on an `offshore-pump` that field is where the pump *draws from*
(vanilla's is `{0, -1}`), while the player's pipe attaches at
`fluid_box.pipe_connections`. The riser's tip is a **pipe connection**, and it is
that field the art has to agree with.

Either way the number has to be measured off each directional plate, exactly as
the Ballast Drill's `vector_to_place_result` does. A riser drawn on one face and
declared on another is the same class of defect as the arc mast's first
`lightning_strike_offset`.

**And the connection has to be drawn as something a pipe can join.** Three
generations were spent learning this: a riser aimed between two edges connects to
no tile at all, and a riser that ends in a nozzle or a cap connects to nothing
even when the angle is right. The adopted sheet ends in an open, full-diameter
pipe mouth behind a flange collar, flush with the middle of a tile edge — the
same thing vanilla's pump does — and carries a panel with an ordinary pipe butted
onto it.

---

# 11. Generation Requirements

**The concept prompt lives with the design it drew:**
`crust-tap-options/A-bolted-collar.md`, in the form that finally worked — with
the geometry diagram and the pump-and-pipe connection reference both named.

**Do not re-prompt this design.** Appendix C's rule applies: crop the approved
view out of the sheet, attach it, and give a numbered list of permitted changes.

**Two changes are permitted at stage 1**, from the option page's production
notes:

1. **Much more hardware on the collar** — bolt rings, cleats, tag plates, grease
   nipples, lock wire, chipped cast edges, weld spatter. It measured 0.099 edge
   density against vanilla's 0.144 floor, and a 2×2 has a quarter of a 3×3's
   canvas to work with.
2. **Nothing else.** The collar, the four anchors, the burst disc, the choked
   riser and its open pipe mouth are the design.

**Four plates, drawn not rotated**, and `fluid_box.pipe_connections` measured off
each one — see §8.

---

# 15. Factorio Prototype — sketch

```lua
{
  type = "offshore-pump",
  name = "sae-crust-tap",
  pumping_speed = 30,
  fluid_box = { filter = "sae-crust-gas", --[[ ... ]] },
  fluid_source_offset = { --[[ measured per direction; see §8 ]] },
  surface_conditions = { { property = "gravity", min = 45 } }
  -- NOTE: vanilla's offshore pump restricts placement through
  -- `tile_buildability_rules` and `collision_mask` on the entity, not through
  -- any offshore-pump field. Both must be cleared here, or the tap will only
  -- build next to water that does not exist.
}
```

The gas carries its energy as a fuel value, so temperature never enters into it:

```lua
{
  type = "fluid",
  name = "sae-crust-gas",
  default_temperature = 25,
  fuel_value = "200kJ",       -- thruster-fuel is 50kJ, for scale
  gas_temperature = 0,        -- always drawn with the gas-flow animation
  auto_barrel = false         -- it can never leave the Core
}
```

And the turbine burns it rather than reading its temperature:

```lua
{
  type = "generator",
  name = "sae-crust-turbine",
  burns_fluid = true,
  destroy_non_fuel_fluid = false,
  scale_fluid_usage = true,
  max_power_output = "1800kW",
  fluid_box = { filter = "sae-crust-gas", --[[ ... ]] },
  surface_conditions = { { property = "pressure", max = 9 } }
}
```

---

# 16. Icon

The collar seen from slightly above, riser leaving one side with its frost band,
and the seam line beneath. Must read at 32 px as *"a capped hole under
pressure"*. The burst disc will not survive at that size and should not be
attempted.

---

# 20. Open questions

- **`auto_barrel = false` is not optional.** Crust gas must never leave the Core,
  or a player barrels a landing-day power source and ships it to Nauvis. It joins
  molten kamacite on the unbarrelable list for the same reason.
- ~~**`burns_fluid = true` has no vanilla user**~~ — **proven in S10.** 1.80 MW
  from a 25 °C gas, exactly as declared.
- ~~**Placement on open ground needs the same test**~~ — **tested in S10, and it
  changed the design.** The pump builds on open ground and yields nothing; it
  needs a fluid-bearing tile. See §2.
- **Still open: how many vents, and how scattered.** Now that the tap is sited,
  its cap is a map-gen number rather than a balance number, and it wants the same
  treatment `resources.lua` gives the other three. All of them are in the starting
  area deliberately; a landing-day power source has to be.
- **Still open: the vent tile's art.** It is a second art job inside this brief,
  and `graphics/TODO.md` already records the whisker bed tile as an outstanding
  mismatch for exactly this reason — a tile cloned from stone path reads as a
  concrete pad.
- **Turbine art may be derived rather than generated.** `tools/recolour-turbine.py`
  already exists — written for the superseded Quench Turbine — and recolours
  vanilla's steam turbine. Reusing it would make the companion turbine nearly
  free, which is the argument for accepting a second prototype at all.
- **It must not obsolete the arc masts.** If storms survive I1, a tap that is
  merely *steadier* than a mast will win on convenience. Keeping the tap small and
  strictly capped is what preserves both.
- **Does the gas want a second use?** A high-pressure inert gas is a plausible
  atmosphere for sealed processes, which `04-the-core.md` §2 currently gives to
  helium-3. Left alone for now — helium is the scarce one and should stay the
  interesting one — but recorded so it is a decision rather than an oversight.

---

# 21. Open, and it is a tier decision rather than a building one

**Every one of this building's five concepts measured under vanilla's luminance
floor** — 49.8 to 57.9 against 63.2 — and the cause is §3.3, which sets the body
at `#3E3B36`–`#5E584E` because this is tier 0 and half buried. That is darker
than the mod's usual `#4A463F`–`#6E685C` chassis on purpose.

Two honest options, and neither is a stage-1 prompt's business:

* **Accept it.** The Crust Tap is the darkest thing on the Core, which suits a
  machine that is mostly underground on a planet at permanent midnight.
* **Lift the tier-0 range** by a few points, here and on every other tier-0
  building, so the whole landing-day set sits inside vanilla's band.

Recorded for Liam. Whichever way it goes, it should be decided once for the tier
rather than per building.

---

# 22. Design notes / iteration history

**Round 1, 2026-09-09 — five options.** The Bolted Collar, the Wedge Cap, the
Yoke, the Gland Stack, the Flush Plate. One generation each.

**Rounds 2 and 3 — the whole set regenerated, twice, for the connection.** Round
1 drew every riser heading toward a *corner* of the footprint. Round 2 fixed the
angle with a flat geometry diagram — the 2×2 square, its four edge midpoints
marked, an arrow leaving one, crosses on the diagonals — and produced risers that
were square and still ended in nozzles and bulbs. Round 3 added a vanilla **pump
with vanilla pipes butted onto it**, captioned as the connection to copy and
nothing else, and every sheet came back with an open full-diameter mouth and a
panel proving a pipe mates with it.

**The rule that came out of it, and it is not written anywhere else:** *a fluid
connection is not drawn until a pipe can be drawn butted onto it.* Both failures
looked fine in isolation. Both were only visible against the thing that has to
mate with them.
