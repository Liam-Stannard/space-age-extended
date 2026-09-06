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
`04-the-core.md`, `mechanics.md` or `decisions.md` are not, until it is agreed.

## How this differs from the neighbouring documents

| Document | Holds | Status of what is in it |
|---|---|---|
| [decisions.md](decisions.md) | What was settled, and what it replaced | **Binding** |
| [mechanics.md](mechanics.md) § Considered and cut | Mechanics that were designed and rejected | **Rejected**, recorded so they are not re-proposed |
| **ideas.md** (this) | Proposals nobody has ruled on | **Unjudged** — not approved, not rejected |

An entry leaves this file in one of three directions: agreed and moved into the
design proper, rejected and moved to `mechanics.md`'s cut table with a reason, or
deleted because it stopped being interesting. It never leaves by being built.

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
(`decisions.md` D12). Decontamination throughput then equals the helium rate,
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
- **The only hazard.** There are no living enemies by design (`decisions.md`
  D11). Radiation threatens throughput, not the player; remove the storms and the
  Core holds no danger of any kind.
- **Two trees' endgame payoff.** `mechanics.md` sells surge production
  (Vulcanus ↔ Fulgora) as *"the Core's arc storms are the same problem without
  the lightning-rod tutorial"*, and `trees/fulgora-aquilo.md` §5 justifies the
  superconducting store with *"arc storms are episodic and a mast loses what it
  caught."* Both rationales die with the storms.
- **The mod's most finished asset.** The Arc Mast is the only building with
  measured plates, glow sheets, an icon, a filled §13 and four in-game geometry
  fixes behind it. The chamber would need that pipeline run again from a blank
  spec, and `graphics/TODO.md` already lists building sprites as the largest
  outstanding cost in the mod.

Deleting the storms is mechanically easy — `prototypes/core/storms.lua`,
`planet.lua`'s `lightning_properties` and long day-night cycle, the
midnight-freeze hack in `control.lua` (a genuine simplification), plus
`technology.lua:111`, `endgame.lua:391`, six locale strings and six design
documents. It is the design debt rather than the code that is expensive.

### The objection that has nothing to do with lightning

`mechanics.md` closes with a rule written for exactly this situation: three of
the four cut mechanics leaned on the spoil timer, and *"whatever replaces them
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
