# Ideas

Nothing here is agreed. Nothing in it is built, or moved into a design
document, until Liam agrees it by name. Reading, researching and arguing with an
entry are fine.

An entry leaves this file in one of three ways: agreed and moved into the
design, rejected with its reason written here, or deleted. It never leaves by
being built.

## The entry format

Each idea gets a number, a one-line pitch, and four headings: what the game
already gives, what it doesn't, what it would cost, and its status. Every claim
about the game names its source, so the research never has to be done twice.

---

## I1 — Radiation and decontamination on the Core

*Raised 2026-09-06. Reviewed against the 2.1.17 prototype and runtime API docs
and vanilla's own recipe data.*

**The pitch:** the Core is full of radiation. Some items in the production line
turn into irradiated material after a while. A new building, the
**decontamination chamber**, resets that clock for the cost of a fluid. Only a
few chambers can run at first, so the player chooses which lines may run long
and which must stay short. Not everything irradiates, so it isn't a tax on the
whole factory. Raised as a hazard for the Core, which has none yet.

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
load-bearing for melt draw and decontamination at once, which may be one claim
too many on a single vent.

**Terminal products must stay clean.** If the Core's end products can irradiate, a
player stockpiling them for the endgame watches them rot.
That is the frustration case the pitch is already trying to avoid, and it would
land on the endgame.

### What it would cost

One new building, the decontamination chamber, with its art, and a choice of
which items irradiate.

### Status

Parked until the first playtest. Before anything is built, test whether the game
accepts the same item twice in one recipe's results, with different ages.
