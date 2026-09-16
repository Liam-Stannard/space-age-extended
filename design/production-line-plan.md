# The radiant cycle — build plan

How `08-core-power.md` gets built: four stages, each on its own branch, each
with the files it touches and the check that says it is done. Read 08 first;
this document says nothing about *why*.

## Before any stage

**Run the data stage on the branch as it stands.** Six commits sit between the
trigger-tech change and here — a fluid rename touching two tiles, a planet
property removed, ten trigger technologies — and none has been loaded against
the engine. Building the cycle on top of an unverified branch means the first
error could belong to any of seven commits. `tools/check-data-stage.sh`
locally, fix what it finds, merge to `master`, delete the branch. Then each
stage below gets its own.

**One spike, data stage, cheap.** Stage 4's reward rests on `neighbour_bonus`
working with a fuel category that is not uranium's. It has been assumed since
the reactor was first proposed and never checked. A `reactor` with
`fuel_categories = { "sae-radiant" }` in a 2×2, and a look at the bonus in its
GUI.

**Every crafter here is an `assembling-machine`.** There is no centrifuge
prototype in the engine: vanilla's centrifuge, chemical plant, foundry and
electromagnetic plant are all instances of one type, and `crafter()` in
`machines.lua` derives from whichever instance is the fairest starting
silhouette. The second argument decides only the placeholder sprite, the
sounds and the default fluid boxes; `crafter()` overrides everything else. So
both new crafters derive from the chemical plant — the Helium Concentrator
already does, and it is the one 3×3 in vanilla whose art draws the ports its
fluid boxes connect to.

---

## Stage 1 — Radiant power

*Branch: `core-radiant-power`*

**Two things 08 does not say.** `sae-radiant-generator` has
`burnt_inventory_size = 0` and `sae-radiant-fuel` has no `burnt_result`, so a
spent cell cannot exist until both change. And the generator places on space
platforms (pressure ≤ 9): once it emits spent cells, platforms accumulate them
with nothing to do until stage 3. Either they ship down, or platforms get a
void. Decide before this ships.

| File | Change |
|---|---|
| `machines.lua` | **Reaction plant** — `crafter("sae-reaction-plant", "chemical-plant", …)` on a new private category `sae-reaction`, the Helium Concentrator's fluid-box layout as the precedent: two in, the item out the inserter side. `derive.placeholder_art` until it has a spec. Core-only. |
| `machines.lua` | `sae-reaction` added to the category list at the top of the file. |
| `corridor.lua` | `burnt_inventory_size = 1` on the generator. `burnt_result = "sae-spent-cell"` on the fuel. |
| `corridor.lua` | `sae-radiant-precipitation` **becomes stage 1**: `100 radiant solution + 100 crust gas → 1 radiant fuel`, category `sae-reaction`. Helium-3 leaves the recipe. The name stays — a rename costs a migration for nothing. |
| `items.lua` | **Spent cell** — the depleted-cell pattern: no fuel value, `stack_size = 50`, fuel-cell sounds. |
| `technology.lua` | `landfall("sae-radiant-power", { "sae-core-survey" }, …)` unlocking the plant, the recipe and the generator. Trigger `craft-item sae-vent-pump` — the first machine on the planet that runs continuously and that everything downstream waits on. It obeys the invariant: the pump is Core survey's. |
| `technology.lua` | The generator comes off `sae-corridor-seeding`; precipitation comes off `sae-orbital-lift`. Neither is left empty. |
| `groups.lua`, `locale/en/strings.cfg` | Ordering entries and strings for the plant, the category, the technology and the spent cell. |
| `migrations/space-age-extended-0.3.2.lua` | `reset_technology_effects`, idempotent as before. |

**Done when** `tools/check-tech-reachability.py` is green — it is the tool that
catches a burner unlocked without its fuel — and a save on the Core runs a
generator on locally made cells with no helium consumed.

**Play it before stage 2.** The ratios in 08 are first guesses, and whether
crust gas or the pool binds first is the question every later stage's numbers
depend on.

---

## Stage 2 — Solution enrichment

*Branch: `core-solution-enrichment`*

| File | Change |
|---|---|
| `machines.lua` | **Isotope centrifuge** — `crafter("sae-isotope-centrifuge", "chemical-plant", …)`, category `sae-enrichment`, the chemical plant's boxes passed in. Placeholder art. Core-only. Note the behaviour `crafter()` sets when boxes are passed: `fluid_boxes_off_when_no_fluid_recipe = true`, so the building shows its pipes while running a fluid recipe and none while running stage 4's all-solid one. That is vanilla's chemical-plant behaviour, and here it reads as intended. |
| `fluids.lua` | **Enriched solution** — the solution's colours pushed brighter, `auto_barrel = false` like every Core fluid. |
| `recipes.lua` | `200 radiant solution → 100 enriched solution` in the centrifuge. `100 enriched solution + 100 crust gas → 3 radiant fuel` in the reaction plant — a second recipe on that machine, so the plant now auto-selects between two. Confirm that is wanted, or lock it. |
| `technology.lua` | `geodynamic("sae-solution-enrichment", { "sae-radiant-power", "sae-geodynamic-science" }, 150, …)`. The first geodynamic technology on the power line; 150 to match the integrations it sits beside. |
| `groups.lua`, `strings.cfg`, migration | As stage 1. |

**Done when** a reaction plant fed enriched solution makes three cells a craft,
and `tools/check-recipes.py` confirms every recipe in `sae-enrichment` fits the
centrifuge's boxes — that tool exists because a recipe with more fluids than its
machine has boxes "is accepted silently and then never runs".

---

## Stage 3 — Cell reprocessing

*Branch: `core-cell-reprocessing`. Nothing new to build: this is where the two
machines earn their second job.*

| File | Change |
|---|---|
| `fluids.lua` | **Spent solution**, **stripped solution**. Two fluids for one stage — 08 §7 already calls it the heaviest cost in the design. If it is too many, collapse scrub and settle into one step *here*, before locale strings exist for both. |
| `items.lua` | **Radiant sludge** — an intermediate with no fuel value. It is a reagent, not waste. |
| `recipes.lua` | Dissolve `4 spent cells + 50 crust gas → 100 spent solution` in the reaction plant (item and fluid in, fluid out — the chemical-plant shape). Scrub `100 spent → 80 stripped + 2 sludge` and settle `80 stripped → 40 radiant solution`, both in the centrifuge. |
| `technology.lua` | `geodynamic("sae-cell-reprocessing", { "sae-solution-enrichment" }, 300, …)`. |
| `groups.lua`, `strings.cfg`, migration | As stage 1. |

**The thing to check is the loop, not the recipes.** Spent cells leave the
generator, travel by belt, and come back as solution — the first return leg on
the planet. It is also where stage 1's platform question gets its answer: if
platforms cannot reprocess, their cells come down.

**Done when** a closed loop runs — generators feeding a dissolver feeding a
centrifuge feeding the shore's solution line — and solution consumption per
cell drops by the ~40% the design claims.

---

## Stage 4 — Radiant reactors

*Branch: `core-radiant-reactors`. Needs the neighbour-bonus spike.*

| File | Change |
|---|---|
| `corridor.lua` | New fuel category `sae-radiant-enriched`. |
| `items.lua` | **Enriched radiant fuel** — `fuel_category = "sae-radiant-enriched"`, fuel value set so a 40 MW reactor burns one on a reasonable cadence. Its `burnt_result` is the **same spent cell** as stage 1's: one return path keeps stage 3 the single place cells come back. |
| `recipes.lua` | `5 radiant fuel + 2 radiant sludge → 1 enriched radiant fuel` in the centrifuge. **This is what makes stage 4 unreachable without stage 3 running** — give sludge no other source. |
| `power.lua` *(new)* | **Radiant reactor** — `derive.from("reactor", "nuclear-reactor", …)`, `fuel_categories = { "sae-radiant-enriched" }`, `neighbour_bonus` as the spike found it, heat pipes vanilla's. |
| `technology.lua` | `geodynamic("sae-radiant-reactors", { "sae-cell-reprocessing" }, 600, …)` — priced with Field coils, its peer. |
| `groups.lua`, `strings.cfg`, migration | As stage 1. |

**The wrinkle to rule on before building.** A reactor's output path is heat →
exchanger → steam → turbine. `04-the-core.md` §1 says the heat exchanger and
steam turbine work unchanged at pressure 5, so it *runs* — but it brings steam
back onto the planet at the top of a ladder that removed it everywhere else.
Either that is accepted as the one place, or the reactor drives something other
than an exchanger. Decide first; it changes what stage 4 is.

**Done when** a 2×2 bank shows the neighbour bonus in the reactor GUI, and
nothing but a reactor will accept an enriched cell.

---

## Order

```
data stage on the current branch → merge → the neighbour-bonus spike
  → stage 1 → play it → stage 2 → stage 3 → stage 4
```

Stage 1 is the only stage with no unknowns beyond the platform question, and
it restores the planet's power — the storm removal took ~2.3 MW a mast away and
put nothing back. Everything after it waits on what stage 1 teaches.

## Not decided

- **Spent cells on platforms** — ship down, or void. Blocks stage 1.
- **Steam at the top of the ladder** — accept it in the reactor room, or find
  the reactor another output. Blocks stage 4.
- **Three building specs before art**, per `claude.md` §3 —
  `concept/reaction-plant/`, `concept/isotope-centrifuge/`,
  `concept/radiant-reactor/`, from the template. Placeholder art ships without
  them, as every Core machine did.
