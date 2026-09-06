# Spikes

Engine assumptions the design now rests on, none of them proven. Each is cheap to
test and expensive to be wrong about — three separate claims in this design have
already turned out false when measured, so nothing here is taken on trust.

**Run them in this order.** They are sorted by blast radius: the first can void
two documents, the last only changes a recipe.

---

## The rig

Both harnesses already exist and are known to work.

**Data stage** — `factorio --dump-data --mod-directory <scratch>/mods` writes
`~/.factorio/script-output/data-raw-dump.json`. Enough to prove a prototype
*loads*, and to read back what the engine made of it.

**Runtime** — a headless server driven over RCON:

```
factorio --create fresh.zip --mod-directory <scratch>/mods
sleep 600 | factorio --start-server fresh.zip --mod-directory <scratch>/mods \
  --port 34198 --rcon-port 27016 --rcon-password x \
  --server-settings settings.json      # allow_commands: "true"
```

Then a short Source-RCON client sending `/c ... rcon.print(...)`. Two gotchas
learned the hard way: the server closes on stdin EOF, hence the `sleep` pipe; and
with no client attached it free-runs far faster than real time, so **measure
against `game.tick` deltas, never wall-clock sleeps**.

---

## Results so far

| Spike | Status |
|---|---|
| S1 — is the Core buildable? | **PASS**, with one required addition |
| S2 — do the Core's conditions behave? | **PASS** on placement, growth and the sealed roboport; one gap found |
| S3 — does seeding work? | **PARTIAL** — the conversion works; the harvest half is unproven by this harness |
| S4 — can a vent require an input fluid? | **PASS** |
| S9 — do arc storms need night? | **FAIL, then fixed** — `day-night-cycle = 0` has no night, so no lightning at all |
| S10 — crust tap: pump on land, generator burning a fluid | **PASS on both**, but the pump needs a fluid-bearing *tile*, which makes the tap sited |
| S11 — does a spoiling ingredient survive a rocket silo? | **PASS** — it ticks, it vanishes cleanly, and it cannot rot mid-craft |
| S12 — can a furnace select on one item + one fluid? | **PASS**, but the fluid must reach the machine before it will accept the solid |
| S13 — can a furnace carry a status-tinted lamp? | **PASS at the data stage** — loaded and retained; rendering still wants an eye on it |

### S1 — PASS

Measured on a headless server with a scratch mod defining the planet and a
connection from the Shattered Planet:

- The planet loads, `create_surface()` generates ground, and the surface reports
  **pressure 5, gravity 50, solar-power 0** exactly as specified.
- Placement on it matches the design precisely: chests, inserters, rails,
  assemblers, foundries, electromagnetic plants, cryogenic plants, biochambers,
  recyclers, nuclear reactors, drills, the rocket silo and the cargo landing pad
  all place; **boilers, furnaces, heating towers, roboports, burner inserters,
  agricultural towers and biolabs are all refused.** Lightning rods are refused
  too, since the magnetic field is 0.
- The space connection resolves, a platform paths to it, departs under thruster
  power, and **arrives**: `state = waiting_at_station, location = sae-core`.

**The required addition: the Core needs a discovery technology.** A platform
reports `no_path` to our planet until the force has explicitly unlocked the
location. `research_all_technologies()` does not do it, because no technology
references our planet — vanilla gates each of its worlds behind a
`planet-discovery-*` technology with an `unlock-space-location` effect, and ours
needs the same. Without it the Core is unreachable however well-formed the
connection is.

*Also learned:* the Shattered Planet is a perfectly good waypoint — connections
from it path fine, so the corridor can genuinely start where vanilla's route
gives out.

### S2 — PASS, with a gap

- A **mod tile** places on the Core, and a **mod `plant`** placed on it grows to
  maturity on schedule and yields its harvest products when mined. Whisker
  growth is buildable exactly as designed.
- A **sealed roboport** with `surface_conditions` pressure 1–9 places on the
  Core and is **refused on Aquilo and on a space platform**, while the vanilla
  roboport is refused on the Core. The mid-tree bot unlock works, and it competes
  with nothing.

**The gap: there is no harvester.** The vanilla agricultural tower is refused on
the Core (it needs pressure 1000–2000), so whiskers can only be gathered by hand
unless the mod supplies **its own harvesting tower** with the Core's conditions.
That is a second new building on the Core, and it needs to be justified or
designed into an existing one.

*Not re-tested:* whether recipe `surface_conditions` block crafting at runtime.
Earlier work established they are a player-facing selection filter rather than a
runtime block, which is sufficient — players do not set recipes by script.

### S3 — PARTIAL

**The conversion works, and it is the novel half.** A projectile whose action
combines `damage` with `create-entity` destroyed a mod asteroid and left an
infected one in its place, in a single shot, with no script. The design's central
claim holds: you can seed a rock in flight.

**The harvest half is not proven, and the harness is why.** Destroying the
infected asteroid produced no chunk this test could see, and neither did the
**control** — a *vanilla* small asteroid, destroyed the same way beside a powered
collector, also yielded nothing observable. When the control fails, the
experiment says nothing about the mod. This needs an in-client test, or a rig
that shoots asteroids with a real turret rather than applying script damage.

Four things learned along the way, all of which would have cost hours later:

- **A chunk needs two prototypes.** Vanilla defines both an `asteroid-chunk`
  *and* an `item` of the same name; copying only the former gives a chunk with no
  item form. `prototypes.entity["metallic-asteroid-chunk"]` is `nil` — chunks are
  not entities, which is also why `find_entities_filtered` cannot see them.
- **`create-asteroid-chunk` is a first-class trigger effect**, and it is what
  vanilla's small asteroids use to yield chunks. The seeding design uses exactly
  the machinery the game already has.
- **Asteroids spawned on platform tiles are destroyed instantly.** They only
  survive in empty space beyond the foundation — which is where they naturally
  are, but it invalidates a naive test.
- **Asteroids only persist while the platform is travelling.** On a stationary
  platform they vanish within a second, so any asteroid test has to be run under
  way.

### S4 — PASS

**A fluid resource can require an input fluid, and a drill can hold both fluid
boxes.** Measured on the Core with a vent resource carrying
`minable.required_fluid` and a pumpjack-derived drill given the electric mining
drill's `input_fluid_box`:

| State | Result |
|---|---|
| No helium-3 supplied | status **`missing_required_fluid`** — the engine refuses to draw |
| Helium-3 inserted | status **`working`**, molten kamacite accumulating (279 → 349 over five seconds), helium consumed as it goes |
| Helium drained again | status returns to **`missing_required_fluid`** and output stops |

So helium-3 gating the melt draw works exactly as designed — the rare resource
throttles the abundant one — and the engine even provides a dedicated,
player-legible status for the failure. No fallback needed.

### Engine change worth knowing

**Recipes in 2.1 use `categories = {...}`, not `category = "..."`.** The data
stage refuses the old form outright: *"In RecipePrototype, `category` and
`additional_categories` got merged into `categories` table."*

---

## S1 — Is the Core buildable at all?

**The claim.** A landable planet can be added past the Shattered Planet, with its
own orbit and a space connection reaching it.

**Test.** A scratch mod defining a `planet` with our surface properties
(pressure 5, gravity 50, magnetic-field 0, solar-power 0) and a `space-connection`
from `shattered-planet`. Over RCON: `game.planets["<core>"].create_surface()`,
force-generate chunks, place an entity, and confirm a platform can be given the
route.

**Pass:** the surface generates, entities place, and the connection appears as a
navigable destination.

**If it fails:** [the corridor](03-corridor.md) and [the Core](04-the-core.md)
are both void, and the mod becomes five trees plus a shared endgame that has to
live somewhere else. Better to learn this in a day than after four trees.

## S2 — Do the Core's conditions behave?

**The claims.** Four separate ones, all cheap to check together:

| Claim | Test |
|---|---|
| A recipe with `surface_conditions` gravity ≥ 45 is available on the Core and nowhere else | Check availability on the Core, Vulcanus (40) and a platform |
| A `plant` with a mod tile restriction grows at pressure 5 | Place the tile, plant, advance ticks, harvest |
| A roboport with `surface_conditions` pressure 1–9 places on the Core and refuses everywhere else | `can_place_entity` on the Core, Aquilo (300) and a platform (0) |
| Personal roboports work at pressure 5 | Equip and build a ghost |

**Pass:** all four behave as the surface-condition tables predict.

**If it fails:** the Core's austerity has to be enforced some other way, and the
sealed roboport — the mid-tree milestone — may not be possible.

## S3 — Does seeding work?

**The claim.** A projectile's action can destroy an asteroid *and* place a
different asteroid in its position, and collectors will gather the chunks that
one yields.

**Test.** Define a mod asteroid with a terminal `dying_trigger_effect`, an
infected variant whose dying effect creates a mod chunk, and a projectile whose
action combines `damage` with `create-entity`. On a platform over RCON: spawn the
asteroid, fire the projectile at it, confirm the infected entity exists and the
original is gone; destroy the infected one and confirm chunks appear and a
collector picks them up.

**Pass:** one shot converts the rock, and the chunks enter a collector.

**If it fails:** the corridor's mechanic needs another shape — most likely the
infection becomes a *chunk* transformation done in a crusher rather than an
entity transformation done in flight, which is less interesting but entirely
native.

## S4 — Can a vent require an input fluid?

**The claim.** A fluid resource can carry `minable.required_fluid`, and a drill
can hold both an input and an output fluid box, so drawing molten kamacite can
cost helium-3.

**Why it is doubtful.** Vanilla uses `required_fluid` only on uranium ore, a
*solid*. Every vanilla fluid resource — crude oil, lithium brine, the acid geyser,
the fluorine vent — is drawn with no input at all.

**Test.** Define the resource and a mining drill with both fluid boxes; place it
on a patch; confirm it stalls without helium-3 and produces with it.

**If it fails:** gate the melt somewhere else — most simply, the settling recipes
consume helium-3 rather than the vent doing so. The design intent survives; only
the location of the cost moves.

## S5 — Confirmations, not discoveries

Quick checks on things the data already implies. Ten minutes each, worth doing
before building on them.

- **`spoil_result` may point at a better item** — maturation depends on it.
  Nothing in the format requires a downgrade, and vanilla's own bacteria spoil
  *into ore*, so this is close to proven already.
- **A recipe can output steam at 500 °C into ordinary turbines** — vanilla's
  `acid-neutralisation` already does exactly this.
- **A machine can be powered by a custom fuel category** — the biochamber burns
  nutrients, which is the same shape.
- **An item's `weight` overrides the derived value** — verified previously, and
  the reason capstone freight cost is a decision rather than an accident.

---

## What to do with the results

Every spike either confirms a line in the design documents or forces a specific,
already-identified fallback. Record each outcome in
[decisions.md](decisions.md) — including the ones that pass, since "we checked
this" is worth as much as "we changed this."

---

## S9 — Arc storms need night, and `day-night-cycle = 0` has none

**Measured after the Core shipped with no working lightning at all.**

A mast on the Core caught nothing: 729 chunks, 7018 ticks, zero strikes, while
vanilla Fulgora in the same rig produced 35 sightings over 5171 ticks. The
prototype data was not at fault — the dumped `lightning_properties` are present
and correct on both planets.

Lightning is generated **only while a surface is dark**:

| `day-night-cycle` | darkness | result |
| ----------------- | -------- | ------ |
| `0` | 0.00, always | zero strikes in 7018 ticks |
| `216000`, sampled in daylight | 0.00 | zero strikes in 8864 ticks |
| `216000`, forced to `daytime = 0.5` | 0.85 | charged in **370 ticks** |
| `10800`, night comes round quickly | varies | charged in 4063 ticks |

A cycle of 0 means there is never any night, so the Core's only power source and
its only hazard were both silently dead.

**The fix.** The planet declares a long cycle so night is reachable, and
`control.lua` pins the Core at `daytime = 0.5` with `freeze_daytime = true` when
the surface is created. The design's "sky that does not move" survives intact —
it simply never moves off night, which suits a world with `solar-power = 0`.

Verified on a fresh save with no console intervention: darkness 0.85, frozen,
mast at 1399 MJ within 1108 ticks — exactly 35% of a 4000 MJ strike, matching
`efficiency = 0.35`.

**Also worth knowing:** a hand-spawned lightning entity does *not* charge a
mast. `create_entity{name = "sae-arc", position = ...}` with no `target` strikes
the ground and nothing else, because attraction is decided when the lightning is
created, not by proximity afterwards. Pass `target = <the mast>` to test by hand.


---

## S10 — The crust tap: an offshore pump on land, and a generator that burns a fluid

**Both halves needed, and one of them changed the design.**

### The pump builds on open ground — and produces nothing

Vanilla's offshore pump carries two `tile_buildability_rules`: one requiring a
ground tile under the centre, one requiring **water** in the tiles ahead. Drop the
second and the entity places on bare ground on the Core: `can_place_entity` true,
`create_entity` true.

It then yields nothing at all, while reporting itself perfectly healthy:

| Probe | Result |
| ----- | ------ |
| `entity.status` | **`working`** |
| `get_fluid_contents()` | empty |
| `get_fluid_source_fluid()` | `nil` |

**An offshore pump takes its fluid from `TilePrototype::fluid` on the tile beneath
it, not from its own fluid box filter.** Vanilla's water tiles declare
`fluid = "water"` (`base/prototypes/tile/tiles.lua:962` and after); a tile that
declares nothing is a pump that pumps nothing. This is the same shape of silent
failure as S9 — a correct-looking prototype, a machine reporting "working", and
no output — and it would have survived every check the repo currently runs.

Given a tile that declares the fluid, it works immediately: `get_fluid_source_fluid`
returns the gas and a connected pipe fills to its full 100 units.

**Consequence for the design: the Crust Tap is sited, not placeable anywhere.**
It needs a vent tile of its own, which means a tile prototype, an autoplace entry
in `map-gen.lua`, and tile art. That makes it a **fourth sited resource**
alongside ore, melt vents and gas vents — arguably better than the brief assumed,
since power becomes a place you go rather than a thing you tile, but it is a
larger build than "an offshore pump with the water rule removed".

### `burns_fluid = true` works, and temperature genuinely stops mattering

A `generator` with `burns_fluid = true`, fed a fluid at **25 °C** carrying
`fuel_value = "200kJ"`, produced **30,000 J/tick — exactly 1.80 MW**, its declared
`max_power_output`, under a 2 MW load. Status `working`, fluid consumed.

That is the whole reason to prefer a gas over steam: vanilla `steam` sits at
`default_temperature = 15` and an offshore pump has no field to raise it, so a
temperature-based generator on a tapped fluid would have produced nothing.

**One gotcha:** `maximum_temperature` is **mandatory on a `generator` even when
`burns_fluid` is true**. Omitting it fails the data stage outright —
`Key "maximum_temperature" not found in property tree`. It is unused for power in
this mode, but it has to be there.

### Also learned — the rig itself

**`LuaEntity.fluidbox` no longer exists in 2.1.** It is replaced by
`get_fluid_contents()`, `get_fluid(index)`, `get_fluid_source_fluid()` and
friends. Any spike script carried over from an older note will fail with
*"LuaEntity doesn't contain key fluidbox"*.

Two more, for whoever drives the rig next: a headless server **pauses when no
player is connected** unless `auto_pause` is `false` in the server settings — with
it left on, `game.tick` advances one tick per RCON call and every measurement is
meaningless. And a rocket silo's ingredient inventory is
`defines.inventory.crafter_input`, not `assembling_machine_input`, which does not
exist.

---

## S11 — Does a spoiling ingredient survive a rocket silo? — PASS

The Ignition Ring Mast's whole mechanic rests on it: charges carry a ten-second
`spoil_ticks` and no `spoil_result`, so a mast too far from the Array delivers
nothing. Two things had to be true.

**Spoilage does tick inside a rocket silo's input inventory.** Five charges
inserted with the segment's other ingredients; after ~750 ticks against a 600-tick
timer, the two consumed by crafting were gone and **the remaining three had simply
vanished**. An item with no `spoil_result` does exactly what the design wants:
ceases to exist, quietly, wherever it is.

The Array does **not** jam on this. It keeps building parts for as long as a fresh
charge is present, and loses only the charges that sat too long — which is the
mechanic, not a failure of it.

**A charge cannot rot mid-craft and take the coil assembly with it.** This was the
real worry in the brief, and it is unfounded: **ingredients are consumed at craft
start.** A charge inserted at `spoil_percent = 0.98` — about a fifth of a second
of life left, against an eight-second craft — still produced a rocket part
(`rocket_parts` 3 → 4). Once a craft begins, the ingredients are already inside
it.

**So the ring mast works as specified, and §20's second open question is closed.**

---

## S12 — Can a `furnace` auto-select a recipe from one item *and* one fluid? — PASS, with a catch

`auxiliary/furnace-recipe-selection.html` says recipes with *"one fluid and one
item ingredient"* are selectable. Nothing in the game does it: there are exactly
three furnaces — stone, steel and electric — and **none has a fluid box**. So it
was documented and unproven, which after S10 is not a category to build on.

### It works, and it disambiguates properly

A `furnace` deep-copied from the electric furnace, given `fluid_boxes` and a
crafting category holding two recipes that share one fluid and differ only in
their item:

| Fed | Produced |
| --- | -------- |
| powder-**a** + flux | `spike-preform-a` ×20 |
| powder-**b** + flux | `spike-preform-b` ×5 |

So selection is genuinely by the item, not "the first recipe in the category".
The data stage accepts `fluid_boxes` on a furnace without complaint.

### The catch: the fluid has to arrive first

**A furnace with a fluid ingredient will not accept its solid ingredient until
the fluid is already in the machine.** Measured, with the input inventory empty
each time:

| Furnace state | `insert{spike-powder-b, 5}` returns |
| ------------- | ----------------------------------- |
| No fluid in the machine | **0** — refused outright |
| 100 flux in the machine | **5** — accepted, crafted, correct product |

The engine cannot select a recipe it has no fluid for, and it will not hold an
item for a recipe it cannot select.

**The vanilla control behaves differently**, which is what makes this a real
finding rather than an artefact: an electric furnace that has just smelted iron
accepts copper ore unconditionally — `insert` returned 5 — because its recipes
have no fluid to be missing.

It self-heals: the moment fluid arrives, solids are accepted again. But two
consequences are worth designing around.

- **On first build, pipe before you belt.** A player who runs the solid line in
  first will watch inserters refuse to load a machine that looks perfectly
  healthy.
- **A dry fluid line plus an empty input latches the machine shut** until the
  fluid comes back. Recoverable, and invisible while it is happening.

### Also learned

`RecipePrototype::category` and `additional_categories` **no longer exist** — they
were merged into `categories`, and the data stage names the replacement in its
error, which is the friendliest failure in this whole set of spikes.

And `defines.inventory.furnace_source` is gone: a furnace's ingredient inventory
is `crafter_input`, the same one a rocket silo uses (S10).


---

## S13 — Can a `furnace` carry a status-tinted fault lamp? — PASS at the data stage

S12 left the Vacuum Furnace able to latch shut invisibly: with no flux it refuses
powder outright, so the input slot stays empty and the fault reads as an upstream
belt problem. The building had one lit state — a heat glow — and no way to say
*why* it was dark.

The engine has a mechanism for exactly this, and it is not new: a
`working_visualisation` with `apply_tint = "status"` and `always_draw = true`,
coloured by `WorkingVisualisations::status_colors`. Vanilla drives the electric
mining drill's status LEDs with it (`base/prototypes/entity/mining-drill.lua:161`
and `179`).

**But vanilla uses it only on mining drills.** The documentation says
`apply_tint` is *"Used by CraftingMachinePrototype ("status" and
"visual-state-color" only) and MiningDrillPrototype"*, and after S10 and S12 that
is exactly the shape of claim worth checking rather than trusting.

Applied to a `furnace` with all eight `status_colors` keys set, the data stage
loads without complaint and the dump retains both:

```
status_colors kept: {"no_power":[0,0,0,0], "working":[0,0,0,0], "low_power":[...],
                     "idle":[...], "insufficient_input":[...], "full_output":[...],
                     "disabled":[...]}
working_visualisations: 5, one with apply_tint = status, always_draw = true
```

**The available statuses are fixed and short:** `no_power`, `low_power`, `idle`,
`working`, `disabled`, `insufficient_input`, `full_output`, `no_minable_resources`.
`insufficient_input` is the one that covers a missing fluid ingredient, which is
what the latch is.

**`always_draw = true` is mandatory.** Vanilla's own comment is explicit: without
it, the `no_power`, `idle`, `disabled`, `insufficient_input` and `full_output`
layers are never drawn at all — the visualisation only appears while working,
which is the opposite of what a fault lamp is for.

**What this does not prove.** The dump shows the properties *loaded and retained*
on a furnace; it does not show the renderer applying the tint. That needs a
client, and it is a ten-second check rather than a spike: build one, cut its
flux, look at the lamp.

**It generalises.** Nothing in this mod uses status colours anywhere, and every
machine in it can stall for a reason the player cannot see. This is the cheapest
legibility win available to the whole set of nine buildings.
