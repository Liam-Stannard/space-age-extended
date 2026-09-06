# Factorio Building — Art & Implementation Specification

**Crust Tap.** First draft — a brief, enough to commission and judge a concept
sheet. Not a specification: §6, §12 and §13 stay open until a sheet is approved
and a canonical plate has been measured.

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
| Scorched ground | `#2E2A26` | tight ring at the base |

**Dull orange, not bright, and only at ground level.** This is conducted heat
through metal, not a flame. The frost must be close enough to the seam that both
are legible in the same glance — that adjacency *is* the signature.

---

# 4. Factorio Visual Style

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
| `sae-crust-gas` out | the riser's tip, per `fluid_source_offset` | must match the art in all four directions |
| Electric | none | the tap draws no power |
| Items | none | no inserter ever touches this building |

`fluid_source_offset` has to be measured off each directional plate, exactly as
the Ballast Drill's `vector_to_place_result` does. A riser drawn on one face and
declared on another is the same class of defect as the arc mast's first
`lightning_strike_offset`.

---

# 11. Generation Requirements

## Concept Sheet Prompt

```text
A single landscape concept-art and asset-breakdown sheet for one Factorio
Space Age industrial wellhead, every panel drawn from the game's
characteristic 45-degree top-down perspective. The machine is a low squat two-
by-two armoured collar clamped over a bore in dark metallic ground on an
airless world, and the entire machine including its pipework fits inside the
two-by-two footprint. Heavy ground anchors bolt it down. A short pale pipe
rises from the collar, turns, and comes straight back down to a flange flush
with the ground at the edge of the footprint; it is visibly narrowed at a
choke, and beyond the choke it carries a pale blue frost jacket. A small
bulging yellow burst disc sits on the collar's shoulder. A thin dull orange
line of conducted heat glows in the joint where the collar meets the ground,
and nowhere else on the machine. Very dark grey-brown armour, pale grey pipe.
No water, no impeller, no open frame, no lava, no flame, no smoke, no bright
fire. Panels: main view, top-down view showing the pipe flange at the
footprint edge, side elevation, a detail of the collar seam and the frosted
pipe together, and a lit/unlit pair. Title the sheet CRUST TAP. Draw no loose
material anywhere: no ore, powder, fibre, grit, debris or product on the
ground, in bins, at chutes, on trays or spilling from the machine. Factorio
machines never show what they make, so every chute, port, bin and tray is
drawn as empty machinery. Every pipe connection must run down to ground level
and stop flush at the edge of the tile footprint; no pipe may end in mid-air
and none may leave the top of the building. Nothing may extend past the tile
footprint, pipework included, and the tile-grid panel must show the whole
machine inside the grid with no overhang.
```

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
