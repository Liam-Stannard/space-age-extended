# Factorio Building — Art & Implementation Specification

**Crust Tap**, now the **Gas Pump**. The design is the **Flywheel Compressor**, take 2 of the 3×3 round, refined and signed off by Liam on 2026-10-21. The decision record is `concept/crust-tap/options/round-3x3/` and `round-3x3-refine/`; the Bolted Collar it replaces is recorded in §22. §13 stays open until the model's sheets exist.

**This brief covers two prototypes**, and that is a design decision rather than
an accident — see §2. The tap raises a gas; a companion turbine burns it. The tap
sells **pressure, not heat**, and that single choice is what keeps it simple.

---

**Amended 2026-10-09 (Liam): this building is now the Gas Pump.** One generic
pump for every gas on the Core, drawing from vent *resources* that deplete as
crude oil does. The amendment below replaces what it names; where the older
sections still describe an offshore pump on a vent tile, the amendment wins. Rewritten in place 2026-10-21 (Liam) for the 3×3 pump; §22 records what changed.

---

# A. Amendment, 2026-10-09 — the Gas Pump

Liam took the defaults below as drafted, and on reviewing the built pump set
the rate to one turbine's worth and thinned the vents.

## A.1 What changes, and why

The Core has two gases, and until now two machines drew them: siderane came up
through an `offshore-pump` standing on a vent **tile**, and helium-3 through the
Vent Pump, a `mining-drill` on a vent **resource**. A tile holds no amount, so
siderane could never run down; helium did, because depletion belongs to the
resource and not to the machine, as an oil field's does to the field and not to
the pumpjack.

Liam's call: **one Gas Pump for every gas, and siderane depletes like oil.** So
the Gas Pump is a `mining-drill`, as the pumpjack is, and every gas vent is a
resource carrying its own yield:

| Vent | Resource | Yields | Drawn by |
| ---- | -------- | ------ | -------- |
| Siderane vent | `sae-crust-vent`, **now a resource, no longer a tile** | siderane | **Gas Pump** |
| Helium-3 vent | `sae-gas-vent` | helium-3 | **Gas Pump** (was the Vent Pump) |
| Melt vent | `sae-melt-vent` | molten kamacite, for 10 helium-3 a cycle | Vent Pump, **melt only** |

The gas vents share a new resource category, `sae-gas`; the melt vent keeps
`sae-vent`. The Gas Pump takes `sae-gas` only and the Vent Pump `sae-vent` only,
so neither can stand on the other's vent. A future gas costs a resource and a
fluid, and no new machine.

## A.2 Section 1 — overview, replaced

**Building Name:** `Gas Pump` (was the Siderane wellhead, and before that the Crust Tap)
**Internal Prototype Name:** `sae-gas-pump`. The entity changes
type, from `offshore-pump` to `mining-drill`, and an entity cannot change type
under its old name in a save: placed taps are removed on load whatever the name.
So it takes a new name, and a migration carries the `sae-crust-tap` *item* (and
its recipe) over, so nothing in an inventory is lost.

**Building Type:** `mining-drill`, from `pumpjack`, with an output fluid box and no
input. The engine's resource machinery is what makes the yield deplete and the
pump report `no_minable_resources`, with no script.

**Purpose:** unchanged at heart, and still the Core's landing-day power: the Gas
Pump on a siderane vent feeds the Siderane turbine. It also draws helium-3, the
gas that throttles the melt line, so it is the first machine of two chains.

**Energy:** **none — a `void` energy source.** **[confirm by test]** The landing
has no power until this pump runs, so it must not need any; the offshore pump it
replaces needed none either. A `void` source on a `mining-drill` is expected to
work but has not been measured on this engine, and it is the first thing the
prototype task tests.

## A.3 Section 2 — the tap's table, replaced

| | |
| --- | --- |
| Tile footprint | **3×3**, the pumpjack's boxes (collision ±1.2, selection ±1.5), reaching 0.49 for its vent, so it always stands centred on it |
| Directions | 4: the whole machine turns, and the outlet with it (§5) |
| Output | the vent's gas: siderane or helium-3 |
| Rate | **9/s** on a fresh siderane vent — one turbine's burn, 1.8 MW — falling with depletion |
| Energy | none (`void`) — see A.2 |
| Surface conditions | `gravity` ≥ 45, unchanged |
| Placement | on a gas vent resource; nowhere else |
| Recipe | set by Liam (T10) |

**Depletion, as crude oil's.** Each gas vent is `infinite = true` with a
`normal` yield, a `minimum` floor and an `infinite_depletion_amount`, so a vent
slows as it is drawn and never quite stops. Siderane's numbers:

* `normal` sized so a fresh vent drives about one turbine's worth, ~1.8 MW, as
  the old tap did;
* `minimum` at **20%**, crude oil's own ratio, so an old vent still turns a
  turbine at a fifth of its speed — the landing's power fades into a trickle
  rather than going dark, and the player has a reason to move on to the melt
  line;
* depletion per cycle in line with helium's `infinite_depletion_amount = 10`.

**The vents are thin**, as crude oil's are: a starting area holds a handful of
siderane vents, not a field of them, so the landing's power stays a foothold.
The first build, at the other vents' density, put 13 in one starting patch —
forty-odd turbines' worth.

**The starting field is placed by hand** (Liam, 2026-10-09): four vents in a
fixed pattern about 48 tiles out, rotated per map toward dry ground, any that
would land in the radiant pool dropped. A probability draw cannot promise a
handful: over twelve seeds it gave anywhere from none to twelve, once put the
patch 85 tiles out and once drowned it. Beyond 150 tiles the vents are thinned
as crude oil's are. The cost is accepted: the start always holds four, the
pattern is the same on every map but turned, and the frequency slider does not
move it. Siderane takes the ground first where vents overlap other resources, and
a kamacite boulder can occasionally sit on a starting vent — mining it is the
landing's first act anyway.

**The cap moves from the map to the map *and* the yield.** It was "how many vent
tiles exist"; it becomes "how many vents, and how rich", which is the treatment
`resources.lua` already gives every other vent.

**Vent size: crude oil's.** A 2×2 pump cannot sit centred on its vent: the engine puts every resource on a tile centre and a 2×2 machine's centre on a tile corner, so the pump stood half a tile off its vent in any of four quadrants (Liam: *"The offsetting of the pump needs to be fixed"*; the fix *"Gas Pump to 3x3 (vanilla's way)"*). So the pump is 3×3 over a small vent, as the pumpjack is over crude oil, and both gas vents take **crude oil's real boxes** (Liam: *"Crude oil's real boxes"*): collision ±1.4, selection ±0.5. A 3×3 pump with a 0.49 reach was centred on its vent every time, by hand and by script (T01).

**The starting fields at that size.** The siderane field keeps its four. Helium-3's starting patch, which gave 4 to 7 vents at ±1.4 against 9 to 13 before, is **retuned to about eleven** (Liam: *"Retune to about 11"*): the gas patch's radius in `map-gen.lua`, 3.5 for the 2×2 vent, is re-measured over 30 seeds and the seed harness's reference re-recorded with a note.

## A.4 What the older sections lose, and keep

**Lost, and recorded so the lessons are not:**

* "The tap is sited — measured, not assumed" (§2): the vent tile, its
  collision layer, its `tile_buildability_rules`, and the planet's tile
  whitelist entry in `map-gen.lua` all go. The siderane vent becomes an ordinary
  resource with an autoplace control, as the other vents are.
* The offshore pump's traps in §8 and §24 (`fluid_source_offset` drawing from a
  tile corner and producing nothing, the pump with no buffer). A mining drill has
  neither.
* The vent tile's art (§20) is replaced by a resource sprite, as crude oil's and
  the other vents' are.

**Kept:** pressure, not heat (§2) and every S10 finding about `burns_fluid` — those are the turbine's, and the turbine is unchanged; `auto_barrel = false`; the four directions, though the whole machine now turns (§5).

**To prove again on the rig**, since the pump is new: a Gas Pump on a fresh
siderane vent, piped to a turbine under load, produces the declared 1.8 MW; on
a vent at its floor, a fifth of it; on a helium vent it yields helium; it builds
on neither the melt vent nor bare ground; and it runs with no power connected.

## A.5 Section 15 — the prototype sketch, replaced for the pump

```lua
{
  type = "mining-drill",
  name = "sae-gas-pump",
  -- from pumpjack, with its boxes and its reach: always centred on the vent
  resource_categories = { "sae-gas" },
  collision_box = { { -1.2, -1.2 }, { 1.2, 1.2 } },
  selection_box = { { -1.5, -1.5 }, { 1.5, 1.5 } },
  resource_searching_radius = 0.49,
  mining_speed = 1,
  energy_source = { type = "void" },        -- landing day: no grid yet
  max_health = 200,                          -- the pumpjack's, with its wreck and explosion
  corpse = "pumpjack-remnants",
  dying_explosion = "pumpjack-explosion",
  output_fluid_box = { volume = 1000, pipe_connections = {
    { flow_direction = "output", direction = defines.direction.north, position = { 0, -1 } }
  } },
  surface_conditions = { { property = "gravity", min = 45 } }
}
-- and each gas vent:
{
  type = "resource", name = "sae-crust-vent", category = "sae-gas",
  infinite = true, minimum = --[[ 20% of normal ]], normal = --[[ ~1 turbine ]],
  infinite_depletion_amount = 10,
  minable = { mining_time = 1, results = { { type = "fluid", name = "sae-crust-gas", amount = 9 } } },
  collision_box = { { -1.4, -1.4 }, { 1.4, 1.4 } },   -- crude oil's
  selection_box = { { -0.5, -0.5 }, { 0.5, 0.5 } }
}
-- the helium-3 vent's sight-glass tint and map colour, #B6A6C8:
mining_visualisation_tint = { r = 0.714, g = 0.651, b = 0.784 }
map_color = { r = 0.714, g = 0.651, b = 0.784 }
```

## A.6 Names

| Player-facing | Internal |
| ------------- | -------- |
| Gas Pump | `sae-gas-pump` (new; `sae-crust-tap` migrated) |
| Siderane vent | `sae-crust-vent` (now a resource) |
| Helium-3 vent, was "Gas vent" | `sae-gas-vent` |
| Siderane turbine, siderane, Siderane extraction | unchanged |

"Gas vent" for helium's vent stops making sense once there are two gas vents, so
it takes its gas's name, as the siderane vent does.

## A.7 The working animation (Liam, 2026-10-10; 3×3, 2026-10-21)

While pumping, the flywheel turns once a loop; both crossheads and their rods go out and back once, opposed, moving apart and together; the power cylinders' rockers nod; the lubricator works off the flywheel hub; the gauge board's three needles kick on the strokes; and gas drifts in the sight glass, tinted by the vent. One loop of 24 frames, **one turn a second** (Liam: *"One turn a second"*), the same loop for every gas. Idle, everything stops where it is and the glass shows empty, as vanilla's pumpjack stops mid-nod.

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

**Building Name:** `Siderane Wellhead` (was `Crust Tap`)
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

**An oilfield integral engine-compressor**, the 2×2 Gas Pump's idea — a flywheel and crank driving a compressor, a gauge kicking, gas in a sight glass, its green casing — grown to 3×3 (Liam, T03: *"2 Flywheel Compressor"*). One crankcase carries two upright power cylinders and two horizontal compressor cylinders, opposed, their rods and crossheads seen sliding in open distance pieces; a big flywheel on the crankshaft's south end.

**The chain, which the eye can follow:** the vent under the wellhead; a tall suction scrubber over it, the liquid knocked out; suction lines over the top to both compressor cylinders; their discharges up each side, the east one through the sight glass; into the discharge bottle along the north face; out of the bottle's north side at the connection's size, to the outlet.

**The gas engine** (Liam: *"Keep the gas engine"*): the power cylinders burn a slip of the vent's own gas, fed by a tan hose from the scrubber's head through a yellow regulator to their gas rail. **It is art only** (Liam: *"Art only"*): the pump's energy source stays `void` and its rate 9/s.

**The anti-read is still the offshore pump**, and it is not a hot-fluid building: the gas comes up cold.

## 3.2 Key Visual Features

* The **flywheel**, its web cast solid in the casing's green with the spokes only a little proud, and a **yellow balance weight** bolted between two spokes.
* The **opposed compressor cylinders**, crossheads in bare steel on an oil-dark guide floor, a yellow slipper on each.
* The **suction scrubber** standing over the vent, the tallest thing on the machine.
* A **lubricator** driven off the flywheel hub by a short rod (Liam: *"Add a lubricator"*); the artist places it (Liam: *"Artist places it"*).
* The kit: the **gauge board** (west, three needles), the **sight glass** run (east), the lube tank and panel (north-east), spare cylinder liners, crated.

### Signature Feature

**The flywheel and its yellow weight** (Liam: *"Flywheel + yellow weight"*): one bold mark a turn, so the turn reads at 1x and a player sees the pump working from across the landing. The refine made it so: the moving share went from 3.69 % to 4.49 %.

## 3.3 Colour Palette

**Signature finish (Liam, 2026-10-09).** Every Core building shares one base — dark
steel, the shared rust, dust and ground dirt — so they read as one planet's machines.
Each also carries one material of its own on its main surfaces, so a player tells them
apart by colour before shape, as vanilla's electric furnace, assembler and foundry
are told apart. Within the building, variation comes from replacement panels in a
slightly different shade, small stencilled markings, and rust that differs by place:
dry orange on tops, dark wet streaks below fittings.

**This building's: the Vent Pump's finish** (Liam: *"Vent Pump finish"*), its kit's variant (a), *"warmer paints"*, used whole. **An exception to the rule above:** the two pumps share one finish, and are told apart by shape and by what moves.

| Role | Hex | Where |
| ---- | --- | ----- |
| Green | `#5C7A2C` | casing, cylinders, flywheel web |
| Yellow | `#A8841E` at most | balance weight, crosshead slippers, regulator |
| Cream | `#C0A676` | lube tank, gauge board |
| Grey | `#86704C` | discharge bottle, panel |
| Siderane in the glass | `#A8D929` | the siderane vent's `mining_visualisation_tint` |
| Helium-3 in the glass | `#B6A6C8` | the Vent Pump's paler bubble and band violet (Liam: *"Violet, like the Vent Pump"*, then *"#B6A6C8"*); also the helium-3 vent's map colour (Liam: *"Also the vent's map colour"*). Helium-3's own fluid colours do not change |

**The gas is paint, never light: nothing on this building glows.** Idle, the glass shows empty.

---

# 4. Factorio Visual Style

## Technology tier and visual register

**Tier 0 — Foothold.** Crude and mechanical: castings, bolted heads, open crossheads and hoses. The first thing built on the planet.

See the template's *"Technology tier sets the visual register"* — the player
should be able to read their progress off the factory floor without opening the
tech tree, so this building's surface treatment is set by where it sits on
`04-the-core.md` §6's ladder, not by taste.



3×3 and low — the scrubber its tallest part, 0.34 tiles over the north edge against the pumpjack's 0.47 — and it covers 92.9 % of its footprint against the pumpjack's open 73.0 %. Style reference: the **pumpjack**, for the oilfield read and the camera. **Do not attach the offshore pump.**

---

# 5. Building Orientation

* [x] North · [x] East · [x] South · [x] West

**Direction count:** `4`. **The whole machine turns** (Liam: *"Whole machine turns"*): four drawings, each the whole machine turned a quarter, not the pumpjack's split, where the moving part is drawn once and only the base under it turns. The outlet is the fluid box, and it turns with the machine (§24).

---

# 8. Connections

| Connection | Where | Notes |
| ---------- | ----- | ----- |
| the vent's gas out | the outlet off the discharge bottle, middle of the north face, `output_fluid_box.pipe_connections` | must match the art in all four drawings, measured by the no-gap rule |
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

**The model is built from the signed-off concept script**, `concept/crust-tap/options/round-3x3-refine/gp_2_flywheel_compressor.py`, in the Vent Pump's kit. Changes from the concept, each from Liam: the lubricator off the flywheel hub; helium-3 at `#B6A6C8` (the concept still renders `#9C86CC`); four drawings, the whole machine turned. Then the icon (§16).

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

**Rendered from the model** (Liam: *"icon from the model"*), at T08: the machine from the house camera, the flywheel and its yellow weight the thing that must read at 32 px.

---

# 20. Open questions

**Renamed 2026-10-09 (Liam): crust gas is now siderane.** An invented gas of
the Core's own, named to sound like a real one: Greek *sideros*, iron, as in
the siderite meteorites, with the *-ane* of a fuel that burns. The player-facing
set is siderane, the siderane vent, the Siderane wellhead, the Siderane turbine
and Siderane extraction. Only the locale changed; every internal name
(`sae-crust-*`) stays, because renaming those costs a migration for nothing.
Where this spec still says "crust gas", read siderane.

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
  and the art backlog (now `TODO.md`) already records the whisker bed tile as an outstanding
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

**Round 3×3, 2026-10-21 — the pump made 3×3, and the spec rewritten in place.** A 2×2 pump sat half a tile off its vent, so the pump became 3×3 over crude oil's boxes. Three takes: the Gas Jack, the Flywheel Compressor, the Gas Bell. Liam picked take 2, *"Whole machine turns"*; the refine made its motion read at 1x (3.69 % moving to 4.49 %); he signed off the concept with a lubricator off the flywheel hub, the yellow weight and helium-3 in `#B6A6C8`. Replaced in this rewrite: the Bolted Collar's design, palette, signature, prompt, icon and plates (§3, §4, §11, §13, §16), the 2×2 boxes and the 2×2 model (A.3, A.4, A.5, A.7), and §24's tile-centre table. Earlier rounds are recorded above.

---

# 13. Sprite Dimensions

**Four drawings of the whole machine, one per direction**, from the model at 64 px a tile. Their sizes, shifts and frame counts are copied from the model's `sheets/meta.json` when it exists (T08); none is measured off a sheet or typed. The concept, one direction, measured beside the pumpjack (T04, `measures.json`):

| Measure | Concept | Pumpjack |
| --- | --- | --- |
| Footprint coverage | 92.9 % (bar ≥ 92 %) | 73.0 % |
| Rise above the north edge | 0.34 tiles | 0.47 |
| Tonal, plate p50 / p95 | 78 / 157 | 38 / 138 |
| Black | 13.3 % | 18.2 % |
| White and clipped px | 0 | — |
| Moving share / strobe | 4.49 % / 0.34 % | — |
| Join, north | pass, 0 gap columns | — |

The model is measured in all four directions, with the lubricator.

---

# 24. What stage 1 found — and it was a defect in my own diagram

**On a 2×2 footprint the middle of a face is not a connection point.** It is the
seam between two tiles, and nothing connects there. The prototype has always
declared the connection at `{ 0.5, −0.5 }` — a **tile centre** — while the
geometry diagram used through three concept rounds told the generator to leave
"through the middle of that edge". On an odd footprint those are the same place;
on an even one they are half a tile apart.

The first four plates were drawn to the diagram and were therefore half a tile
out. They were re-rendered against a corrected diagram — four tiles with their
centres marked, a cross over the middle of the face.

**On a 3×3 the middle of a face is a tile centre**, so the outlet sits there and the half-tile correction no longer applies:

| Direction | Connection |
| --------- | ---------- |
| north | `{ 0, −1 }` |
| east | `{ 1, 0 }` |
| south | `{ 0, 1 }` |
| west | `{ −1, 0 }` |

The lesson stands: art and prototype are read against each other, connection by connection, in every drawing.
