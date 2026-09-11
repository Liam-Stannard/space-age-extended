# Ideas

**Nothing in this document is approved, and nothing in it is implemented without
Liam saying so explicitly, by name, first.**

That is the whole point of the file. An idea recorded here has been thought
about and often researched against the engine, which makes it look far more
finished than it is — and a plausible-looking design that nobody agreed to is
exactly the kind of thing that quietly ends up in the mod. If a change traces
back to this document and not to a request, it should not have been made.

Reading, researching, costing and arguing with an entry are all fine. Writing
prototypes, deleting existing mechanics, or folding an entry into
`04-the-core.md` or `mechanics.md` are not, until it is agreed.

## How this differs from the neighbouring documents

| Document | Holds | Status of what is in it |
|---|---|---|
| [04-the-core.md](04-the-core.md) and the other numbered documents | The design as agreed | **Binding** |
| [mechanics.md](mechanics.md) | The one new rule each tree teaches | **To be decided** |
| **ideas.md** (this) | Proposals nobody has ruled on | **Unjudged** — not approved, not rejected |

An entry leaves this file in one of three directions: agreed and moved into the
design proper, rejected with the reason recorded here, or deleted because it
stopped being interesting. It never leaves by being built.

## The entry format

Each idea gets a number, a one-line pitch, and four headings: **what the engine
gives free**, **what it does not**, **what it would cost**, and **status**. The
engine sections carry the citation for every claim, because the value of an idea
sitting here for months is that the research does not have to be redone — and an
unsourced engine claim is worse than none.

---

## I1 — Radiation and decontamination on the Core

*Raised 2026-09-06. Reviewed against the 2.1.17 prototype and runtime API docs
and vanilla's own recipe data.*

**The pitch:** the Core is bathed in radiation. Certain items in the production
chain irradiate after a random time between a minimum and a maximum, and become
irradiated material when they do. A new building — the **decontamination
chamber** — is something items pass through, resetting the timer for the cost of
a fluid. The starting patch affords only a few chambers, so the player decides
which lines may run long and which have to be short and efficient. Not
everything can irradiate, so it does not become a tax on the whole factory.

**Raised as a replacement for the arc storms.** Whether it should replace them is
the contested part; the mechanic itself is nearly free.

### What the engine gives free

Most of this is vanilla's spoilage system wearing a different name, and needs no
control-stage script.

| The idea | The feature | Evidence |
|---|---|---|
| Items irradiate after a time | `spoil_ticks` + `spoil_result` pointing at an `sae-irradiated-material` item | Native; the same pair maturation already uses |
| Dose accumulates down a chain | `ItemIngredientPrototype::spoil_weight` — a product inherits its ingredients' spoil percentage | Native; this is how Gleba's chain carries freshness |
| The chamber resets the timer | `ItemProductPrototype::reset_freshness_on_craft = true` on a recipe whose product is its own ingredient | **Vanilla does exactly this** — `space-age/prototypes/recipe.lua:143`, copper bacteria |
| …paid for in a fluid | An ordinary fluid ingredient on that recipe | Native |
| Items *pass through*, whatever they are | Build the chamber as a **`furnace`**, not an assembler: furnaces choose their recipe from what is inserted | `auxiliary/furnace-recipe-selection.html` — *"one fluid and one item ingredient"* recipes are selectable, so one recipe per irradiable item and the chamber picks by itself |
| Not everything irradiates | Give `spoil_ticks` only to the chosen items | Native. **Fluids can never spoil**, so the melt, steam and helium half of the tree is exempt at no cost |
| Route the hottest stack to the chamber first | `spoil_level` plus inserter spoil priority | Native, and free depth |

### What it does not give

**The random timer is not a field.** `spoil_ticks` is a single `uint32`. A
quantised uniform roll is available natively by listing the same item several
times as products with disjoint `shared_probability` ranges and different
`percent_spoiled`:

```lua
results = {
  { type="item", name="X", amount=1, percent_spoiled=0.00, shared_probability={min=0.0,  max=0.25} },
  { type="item", name="X", amount=1, percent_spoiled=0.25, shared_probability={min=0.25, max=0.5}  },
  -- ...
}
```

Vanilla uses `shared_probability` this way for asteroid reprocessing
(`recipe.lua:1041`) and `percent_spoiled` at `recipe.lua:334`, but **never the
same item twice in one result list** — that combination is unproven and is the
spike this idea needs. `LuaItemStack.spoil_tick` is writable at runtime, but no
event fires when a machine produces an item, so scripting it would mean polling
inventories; not worth it. A fixed timer is also arguably the better puzzle:
variance a player cannot plan around is noise rather than a decision.

**"The planet is covered in radiation" is not expressible.** A spoil timer
belongs to the item, not the surface. An irradiable item decays identically on
Nauvis, on a platform and inside a cargo pod. It can be made true *in practice*
by pushing those items' `weight` past `default_rocket_lift_weight` so they
cannot leave — but `04-the-core.md` §4 requires the surface↔orbit lift, so
anything in that loop stays liftable and keeps ticking in orbit, above the
radiation that is supposedly causing it.

**Scarcity has to be a rate, not a stock.** "The starting patch affords only a
few chambers" gates construction, and any stock gate evaporates the moment the
corridor can import the material. Gating the *fluid* survives, and helium-3 is
already the right shape: sited, rare, declining, and already throttling the melt
(`04-the-core.md` §2). Decontamination throughput then equals the helium rate,
which cannot be imported around. The risk runs the other way — helium would be
load-bearing for melt draw, geodynamic science and decontamination at once,
which may be one claim too many on a single vent.

**Terminal products must stay clean.** If a Field Coil Segment can irradiate, a
player stockpiling a hundred of them for the Ignition Array watches them rot.
That is the frustration case the pitch is already trying to avoid, and it would
land on the endgame.

### What it would cost

Adding the mechanic is cheap. *Replacing the arc storms with it* is not, because
storms carry four loads radiation does not reach:

- **Power.** Solar is 0 and nothing burns at pressure 5, so storms are half the
  Core's supply (`04-the-core.md` §1). Without them the surface runs on
  steam-off-the-melt plus the corridor's `sae-radiant-generator`, which does work
  here — `surface_conditions` pressure ≤ 9, 10 MW — so it survives, but landing
  day becomes an import problem.
- **The only hazard.** There are no living enemies by design (`04-the-core.md`
  §1). Radiation threatens throughput, not the player; remove the storms and the
  Core holds no danger of any kind.
- **Two trees' endgame payoff.** Surge production (Vulcanus ↔ Fulgora) was
  sold as *"the Core's arc storms are the same problem without
  the lightning-rod tutorial"*, and `trees/fulgora-aquilo.md` §5 justifies the
  superconducting store with *"arc storms are episodic and a mast loses what it
  caught."* Both rationales die with the storms.
- **The mod's most finished asset.** The Arc Mast is the only building with
  measured plates, glow sheets, an icon, a filled §13 and four in-game geometry
  fixes behind it. The chamber would need that pipeline run again from a blank
  spec, and building sprites are already the largest outstanding cost in the
  mod (`TODO.md`).

Deleting the storms is mechanically easy — `prototypes/core/storms.lua`,
`planet.lua`'s `lightning_properties` and long day-night cycle, the
midnight-freeze hack in `control.lua` (a genuine simplification), plus
`technology.lua:111`, `endgame.lua:391`, six locale strings and six design
documents. It is the design debt rather than the code that is expensive.

### The objection that has nothing to do with lightning

The mechanics work set a rule for exactly this situation: three of the four
cut mechanics leaned on the spoil timer, and *"whatever replaces them
should mostly draw on other parts of the engine … so the five do not all turn
out to be one idea in different clothes."* Maturation, the living line and seed
stock are already three spoil-timer mechanics. Radiation would be the fourth,
sitting on the planet where all of them converge — and the Core would be
carrying a fifth mechanic of its own alongside settling, homogenisation, cold
welding and whisker growth.

### Status

**Parked, pending the first playtest.** The README's own ordering puts play
first, and nothing has been played. Removing the only finished building to add a
fourth spoil-timer mechanic to an untested loop is a bet placed before the cards
are dealt.

If it is taken up, the recommendation on record is: **add it, keep the storms**
— keeping them costs nothing, since they are already built, and it preserves the
power supply, the hazard and both trees' payoffs.

**Open before anything is built:** whether the engine accepts the same item
listed twice in one result list with different `percent_spoiled` and disjoint
`shared_probability`. That is a data-stage spike, and it decides whether the
random timer exists at all.

---

## I2 — A reactor for the Core, on vanilla's nuclear pattern

*Raised 2026-09-10. Researched against this repo's own measurements and against
the vanilla chain as shipped. Claims sourced to a file in this repo were checked;
claims about vanilla's own prototypes are marked **(unverified)** where no
`file:line` was confirmed in the session that wrote this, and each of those is
listed as a spike rather than relied on.*

**The pitch:** replace the Core's three unrelated power sources with **one system
in three stages of rising complexity, ending in a reactor** — built on vanilla's
own nuclear architecture, with helium-3 in place of water and no steam anywhere.
Stages 1 and 2 each teach one half of the stage-3 loop, so the reactor is the
first time both halves run at once rather than the first time either is met.

**Raised because the Core currently has three power systems and no ladder.** The
crust tap is a foothold (`crust-tap.lua`, 1.8 MW, sited), the arc masts are free
average power (`storms.lua`, 0.12 efficiency, ~2.3 MW a mast), and the melt split
is the stated central problem (`04-the-core.md` §2). They do not teach each other
anything, and the mast's efficiency has already been cut from 0.35 to 0.12
because free power was undercutting the split it is supposed to sharpen.

**And because tier 2 as designed is steam turbines**, which is the silhouette
Vulcanus already owns.

### The architecture

Four prototypes, all of them the ones vanilla's nuclear chain uses, with the
working fluids changed:

| Part | Prototype | Vanilla precedent |
|---|---|---|
| **Pile** | `reactor`, burner energy source, custom `fuel-category` | `nuclear-reactor` |
| **Heat pipes** | `heat-pipe` | unchanged |
| **Exchanger** | `boiler`, heat energy source, `mode = "output-to-separate-pipe"` | `heat-exchanger` — water in, steam out |
| **Converter** | `generator` with `maximum_temperature` | `steam-turbine` |

Coolant helium in, hot helium out, watts scaled by how hot it came back. No
water, no steam, no turbine in the loop.

**The earlier rejection of planetary heating does not block this, and the
distinction is worth recording so it is not re-litigated.** That rejected
`heating_energy` on every building plus
`entities_require_heating` on the planet — Aquilo's mechanic, a *world* that
demands heat. Heat pipes inside a power plant are a different thing entirely;
Nauvis has heat pipes and is not Aquilo.

### The ladder

The architecture has two halves — *make heat* and *turn heat into power* — so
each stage teaches one, and stage 3 is where they meet.

| Stage | What is built | What it teaches |
|---|---|---|
| **1 — landing day, no tech** | Crust Tap (built) on a vent tile, feeding a small exchanger and a converter | **The power half.** Coolant in, hot coolant out, and that the return line's temperature *is* the output |
| **2 — tech** | **Ember Kiln** burning a charge cast from settled melt, `burnt_result` a depleted charge, piped by heat pipes into the *same* exchanger and converter | **The fuel half.** A cycle that returns something to reprocess, and heat as a thing you transport |
| **3 — tech** | **The Pile**: both halves at scale, banks of exchangers, neighbour bonus | Only **placement** is new. Optimisation is the right thing to meet last |

Three placements on landing day is exactly Nauvis's first hour — burner drill,
boiler, steam engine — so stage 1 is proportionate rather than demanding.

The melt split lands at stage 2, where the charges are cast: melt becomes plate
*or* charge, which is the same recipe choice `04-the-core.md` §2 already
describes, with the steam taken out of it.

This is the science pack's own argument applied to power. The pack was moved
onto one ingredient per mechanic on the grounds that *"under the old split, cold welding
was first met at the last assembly, which is the worst possible place to learn
it."* A reactor that is the first time a player meets a fuel cycle, a heat
network **and** a coolant loop has the same defect.

### What the engine gives free

| The idea | The feature | Evidence |
|---|---|---|
| A reactor works on the Core at all | `reactor` places at pressure 5 | **Measured on the rig**: nuclear reactors place at pressure 5, while boilers are refused |
| An exchanger works too, despite boilers being refused | The pressure condition lives on the vanilla entity *named* `boiler`, not on the type | `04-the-core.md` §1 lists **heat exchanger and steam turbine** as working unchanged at pressure 5, and states outright that the conditions live on *"those specific vanilla prototypes"* |
| Coolant in, a different fluid out, driven by heat | `boiler` with a heat energy source in `output-to-separate-pipe` mode | Vanilla's heat exchanger is exactly this — water in, steam at 500 out **(unverified)** |
| Power scaled by the coolant's temperature | `generator` + `maximum_temperature` | `crust-tap.lua:270-279` proves the prototype runs on the Core |
| A fuel nothing else will eat | Custom `fuel-category` | Already done in this mod — `sae-radiant` at `corridor.lua:196-213` |
| Spent fuel that reprocesses | `burnt_result` on the fuel item | Vanilla's uranium fuel cell → depleted cell **(unverified)** |
| A power building that only works here | `surface_conditions` on the entity | Already done — `sae-radiant-generator` sets pressure ≤ 9 at `corridor.lua:239` |
| One legible health readout for a bank of exchangers | Pipes average temperature when fluids mix | Native. A starved or unfuelled exchanger passes coolant through cold and drags the shared return line down, so the bus temperature reports the plant's condition |

### What it does not give

**There is no condensate.** The converter consumes the coolant; nothing returns
it cold. The loop is therefore **not conserved** — helium is spent at a rate and
topped up from the vent.

That is not a defect, but it has to be a decision rather than a leak nobody
noticed: it makes **helium throughput the ceiling on power**, which is exactly
the axis the helium-throttle design puts power on. It also means a true closed loop is
unavailable without an `electric-energy-interface` and a control tick, which is
not worth it.

**An exchanger's output temperature is a fixed target**, so it cannot emit
"whatever it picked up". Variation in the return line comes from *mixing* on a
shared bus, not from any one exchanger. That is the mechanic, and it is free —
but it means the interesting behaviour only appears once there are several.

**Output cannot scale inversely with temperature.** "Warm coolant cools worse"
is not expressible; the same play has to be said from the other end, as *a cold
return line pays less*.

**Vanilla reactors do not melt down.** Starved of coolant a reactor simply stops.
An overheat hazard means reading `LuaEntity.temperature` on a control tick and
applying damage — modest script, and optional **(unverified)**.

**The neighbour bonus with a non-uranium `fuel-category` is assumed, not known.**

### What it would cost

**Steam has a second job, and it is not power.** `recipes.lua:674` requires steam
at `minimum_temperature = 500` for the valve processor, and the comment above it
(`recipes.lua:645-651`) puts vacuum electronics on the metal-or-steam split
deliberately, as *"a third claimant beside metal and electricity"*. Taking steam
out of *power* does not take it out of the mod. Either the settling recipes keep
emitting it for electronics alone, or that requirement moves onto hot helium.
**Decide this before anything is built**, because §2's central tension is
currently written in terms of steam.

**Art is the bill.** Three or four new buildings — pile, exchanger, converter and
probably the kiln — against one for a drop-tower ladder.
Building sprites are already the largest outstanding cost in the mod
(`TODO.md`).

**The crust tap survives but loses half its job.** Tap and turbine are 8 cut
plates and the only power chain measured end to end on the rig — exactly
1,800,000 W. The tap becomes stage 1's heat source; **the turbine becomes
redundant.**

**The arc storms are left unresolved.** This ladder carries no hazard of its own
unless the meltdown is built. Keeping the storms as pure weather costs nothing —
they exist, the mast has four measured plates — but it leaves the storms'
rationale, *"the thing that damages you is the thing that runs you"*, holding
only its first half.

**Helium would carry a third load**: melt draw, the science pack's coolant
charge, and now all cooling. This is the same objection I1 raised against
gating decontamination on helium, arriving by a different road.

### The objection that has nothing to do with the Core

**The shape is Nauvis's.** Fuel cell → reactor → heat pipe → exchanger →
generator is a chain the player has already built, and will recognise in ten
seconds.

Four things differ, and the first is the only one that carries real weight:

- **The coolant is the scarce resource.** Water is free and infinite; helium-3 is
  sited, declining, and already throttles melt. Plant size is capped by **vent
  siting rather than by fuel**, which vanilla never poses.
- The fuel is cast from settled melt, so metal-versus-power survives into the
  endgame rather than being replaced by a new ore.
- No steam, no water, no turbine.
- Heat pipes in vacuum have no convective loss, so the Core's could reach further
  than Nauvis's — the same component as a different tool, and a free dial.

Whether *"recognises the pattern, then meets new constraints"* is the virtue
(nothing is taught twice, and the constraints are where the design lives) or the
failure (the Core's power becomes the least surprising thing on it) is the
judgement this entry cannot make for itself. It is the question to rule on.

### Status

**Unjudged.** Nothing here is agreed and no prototype has been touched.

**Three spikes, all cheap, before any of it is depended on:**

1. **Can a `boiler` take a `fluid` energy source** (`burns_fluid`) so stage 1 can
   run on tapped crust gas — or does stage 1 need a small `reactor` of its own?
   Data stage.
2. **Does `neighbour_bonus` work with a custom `fuel-category`**, or is it wired
   to uranium? Data stage.
3. **Is `LuaEntity.temperature` readable on a `reactor` in 2.1**, for the
   meltdown hazard? Runtime, and only if the hazard is wanted. Note that
   `LuaEntity.fluidbox` was already found gone in 2.1 on the rig, so runtime
   assumptions carried over from older notes are not safe here.

**The recommendation on record**, if it is taken up: **build stage 1 and stage 2
first and play them**, before the pile exists. They are the whole teaching
argument, they reuse the crust tap that is already measured, and if the ladder is
not interesting at stage 2 the reactor will not rescue it. The README's own
ordering puts play first, and none of this has been played.

**Keep the arc storms either way.** They cost nothing to keep, they are the only
hazard on the planet, and they hold up two trees' payoffs — the same conclusion
I1 reached about the same buildings, for the same reasons.
