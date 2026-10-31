# Vulcanus ↔ Fulgora: a magnet from glass and storms

**Agreed by Liam 2026-10-30.**

| | |
|---|---|
| Available after | Vulcanus and Fulgora (metallurgic and electromagnetic science) |
| Mechanic | Surge supply |
| Capstone product | Magnetar alloy |
| Capstone building | Magnetic collector |
| Endgame role | **Today:** magnetar alloy's only use is the magnetic collector ("Collector only for now"). **Planned:** the field coil's magnetic core, through the Core's magnetic core billet, whose recipe is not in the code yet. **On the way to the Core:** magnetite rounds, the one railgun round that kills a huge promethium asteroid in a single hit. |

---

## 1. The pairing

**Vulcanus contributes** obsidian, which is found nowhere else, and lava, which
gives molten iron and heat for nothing but the foundry's time.

**Fulgora contributes** ozone, which comes only with lightning and has no barrel,
and electrolyte, which has no barrel either. Its magnetic field (99) is also the
only one strong enough for the electromagnetic plant's own recipe.

Vulcanus can make clean iron but no magnet. Fulgora can make the magnet's coil
and its holmium, but has no iron to cast them in. The magnet needs both.

## 2. The crossing

| Leg | Carries | Forced because |
|---|---|---|
| Fulgora → Vulcanus | **superconducting coil** | the usual leg, not a forced one: electrolyte has no barrel, but holmium ore ships, so the coil can also be wound on Vulcanus |
| Fulgora → Vulcanus | **holmium oxide** | **ozone** has no barrel, and only lightning makes it |
| Vulcanus → Fulgora | nothing that runs | see below |

**The forced leg is the oxide.** Ozone has no barrel and only lightning makes it, so holmium oxide is made only on Fulgora, and the tree can't be finished without both planets.

**Why the coil and the oxide go to Vulcanus, not flux to Fulgora.** Obsidian flux
ships fine, so the meeting point is a choice. Vulcanus wins it: lava gives molten
iron for free, while Fulgora has no iron ore and would have to import it. The
player can see that in the recipes. The oxide's lock is a fluid with no barrel; the coil's is only cost. The meeting point is cheapest on Vulcanus, not forbidden elsewhere.

**Nothing has to go back.** This tree is one-way for running material, on
purpose. Vulcanus's answer to "what do you give back" is the capstone itself:
only it can cast and charge the field core, and the magnetar alloy goes on to
platforms, not to Fulgora. Obsidian glass is used once in each induction
foundry, built on Vulcanus, so it doesn't cross either.

## 3. The mechanic: surge supply

**Ozone arrives only when lightning strikes an ozone collector.** Each strike adds
a fixed amount of ozone to the collector. Between strikes it adds nothing. A
storm is a burst; a calm is a drought.

**Ozone has no barrel.** It can be piped and tanked, but it can't leave Fulgora.

**The steps that drink it run all the time.** Holmium oxide and oxide
superconductor take ozone every craft. So the player buffers it: collectors fill
tanks during a storm, and the tanks feed the plants through the calm. The
problem to design is how many collectors and how much tank it takes to never
stop, and what to let stall when it runs short.

**Which buildings drink it:** the chemical plant (holmium oxide) and the
electromagnetic plant (oxide superconductor). Nothing on Vulcanus uses ozone.

## 4. The chain

```
Vulcanus                                         Fulgora
  obsidian (ore)        sulfuric acid + lava       lightning strike
    │ furnace              │ foundry                 │ ozone collector
  obsidian glass ──┬── superheated acid (500°)     ozone (no barrel) ──┐
    │              │ chemical plant                  │ chemical plant   │
    │            obsidian flux                     holmium solution + ozone
    │              ├─> molten iron from lava (+20%)  │
    │              ├─> fluxed steel ──> slag aggregate ─┐   holmium oxide ──┼──> holmium plate (+20%)
    │              │                    ├─> slag concrete│     │              │ EM plant
    │              │                    └─> stone brick  │     │            oxide superconductor
    │              └─> refined molten iron ──> slag      │     │              │ EM plant (+ electrolyte)
    │                       │                            │     │            superconducting coil
    │                       │   <── holmium oxide ───────┼─────┘              │
    │                       │   <── superconducting coil ┼────────────────────┘
    │                       ▼                            │
    └── (build) ──> induction foundry (on Vulcanus) <────┘ slag, flux, acid, oxide
                      molten holmium iron                   also feed its 5 induction casts
                            │ + superconducting coil
                      field core
                            │ charged
                      magnetar alloy ──> magnetic collector   the capstone building
                            └ ─ ─ ─ ─ ─> magnetic core billet the Core, later
```

## 5. The capstone building: the magnetic collector

An asteroid collector with a magnetar alloy arm and coil. It works only on
platforms, like the vanilla collector.

**Better:**
- **Reach:** collection radius 15 tiles, twice the vanilla 7.5.
- **Arms:** arm and turn speed 0.55, against 0.2. Fast enough to catch the magnetic chunk, which vanilla arms at rest can't.

**Worse:**
- **Power:** four times the energy per arm move (4 kJ, against 1 kJ).
- **Cost:** ten magnetar alloy a collector, the most expensive thing in the tree.

It takes every chunk type, and no filter is set on it or on vanilla's collector.

**The magnetic chunk:** a new chunk that flies only on the new direct Vulcanus ↔ Fulgora route, fast (speed 0.25). Magnetic collectors catch most of them (about 70–90 % in the T02e test), vanilla collectors only a few (0–16 %). It's a strong tilt, not a lock.

**The choice:** a magnetic collector reaches further and catches the magnetic chunk, but it costs four times the power and a share of the capstone. A platform that doesn't fly the Vulcanus ↔ Fulgora route, or is short of power, is better off with vanilla's.

**Across the game:**
1. **Mid-game:** more iron per platform from the same edge, for a player who
   never goes near the Core.
2. **Getting to the Core:** a corridor platform catches more metal at speed.
3. **On the Core:** it is a platform building, so it serves the ships that
   supply the Core, not the surface.
4. **Getting to the Core, again:** magnetic chunks crush into magnetite, and magnetite makes the magnetite round (tech 11), for the promethium belt.

## 6. Technologies

Eleven, ten in the tree and one after the railgun. The Vulcanus path uses metallurgic science, the Fulgora path electromagnetic
science, and the two shared steps use both. Each also uses the packs those packs
need: automation, logistic, chemical and space.

Both openers require **both** planets' science packs, so the tree opens only when
both vanilla trees are done (principle 7). After that, each path needs only its
own planet's pack.

| # | Technology | Unlocks | Prerequisites | Packs | Count × time |
|---|---|---|---|---|---|
| 1 | **Obsidian mining** | obsidian glass. (Obsidian itself is on new map ground once the mod loads, mined by any drill) | metallurgic science pack, electromagnetic science pack | a, l, c, s, **M** | 200 × 60 s |
| 2 | **Obsidian flux** | **superheated sulfuric acid** (the heating recipe); obsidian flux; molten iron from lava with flux | Obsidian mining | a, l, c, s, **M** | 300 × 60 s |
| 3 | **Fluxed steel** | fluxed steel casting; slag concrete; slag brick | Obsidian flux | a, l, c, s, **M** | 400 × 60 s |
| 4 | **Refined molten iron** | refined molten iron | Fluxed steel | a, l, c, s, **M** | 500 × 60 s |
| 5 | **Ozone capture** | ozone collector (and with it, ozone) | electromagnetic science pack, metallurgic science pack, lightning collector | a, l, c, s, **E** | 200 × 60 s |
| 6 | **Holmium oxide** | holmium oxide; holmium plate from oxide | Ozone capture | a, l, c, s, **E** | 300 × 60 s |
| 7 | **Oxide superconductor** | superconductor from holmium oxide | Holmium oxide | a, l, c, s, **E** | 400 × 60 s |
| 8 | **Superconducting coil** | superconducting coil | Oxide superconductor | a, l, c, s, **E** | 500 × 60 s |
| 9 | **Induction foundry** (convergence) | induction foundry; molten holmium iron; field core; the five induction casts | Refined molten iron, Superconducting coil | a, l, c, s, **M, E** | 750 × 60 s |
| 10 | **Magnetar alloy** (capstone, essential) | magnetar alloy; magnetic collector | Induction foundry | a, l, c, s, **M, E** | 1000 × 60 s |
| 11 | **Magnetite rounds** (after Aquilo) | magnetic chunk crushing; magnetite round | Magnetar alloy, railgun | the railgun's ten packs | 1000 × 60 s |

a = automation, l = logistic, c = chemical, s = space, M = metallurgic,
E = electromagnetic.

**Total:** 4,550 units across the ten tree techs, and 1,000 for Magnetite rounds.

Magnetite rounds is the one tech outside the estimated 3–10: it waits for the railgun, which waits for Aquilo, so magnetite can be collected long before it's used.

**Against vanilla:**

| Vanilla tech | Packs | Count × time |
|---|---|---|
| Asteroid reprocessing | a, l, c, s, M | 500 × 60 s |
| Turbo transport belt | a, l, c, p, s, M | 500 × 60 s |
| Lightning collector | a, l, c, s, E | 1000 × 60 s |
| Rail support foundations | a, l, c, p, u, s, M, E | 2000 × 30 s |
| Fulgora ↔ Aquilo's three techs (ours) | eight packs | 300, 400, 600 × 60 s |

Our steps start below asteroid reprocessing and end at the lightning
collector's cost. They use fewer packs than Fulgora ↔ Aquilo, so they cost more
units for a similar effort.

## 7. Recipes

**New items:** obsidian, obsidian glass, obsidian flux, slag aggregate, holmium
oxide, **superconducting coil**, field core, magnetar alloy (the stub's item,
made for real), the ozone collector, the induction foundry and the magnetic
collector.

**New fluids, all with no barrel:** ozone, refined molten iron, molten holmium
iron.

**One vanilla fluid changed:** sulfuric acid's max_temperature goes from its
default (25, the same as its default_temperature) to **500**, so it can be
heated. Nothing else about it changes.

**Machines:** furnace, assembler, foundry (metallurgy), chemical plant
(chemistry), electromagnetic plant (electromagnetics), induction foundry
(induction: a new category only it crafts).

### Step 1: Obsidian mining

| Recipe | Inputs | Outputs | Time | Machine | Where |
|---|---|---|---|---|---|
| **Obsidian glass** | 2 obsidian | 1 obsidian glass | 3.2 s | furnace | anywhere; obsidian is only on Vulcanus |
| *vanilla stone brick* | *2 stone* | *1 stone brick* | *3.2 s* | *furnace* | |

Glass is smelted like brick. Its uses are the flux (step 2) and the induction
foundry's recipe.

### Step 2: Obsidian flux

| Recipe | Inputs | Outputs | Time | Machine | Where |
|---|---|---|---|---|---|
| **Superheated sulfuric acid** | 100 sulfuric acid, 20 lava | 100 sulfuric acid **at 500°** | 4 s | foundry | Vulcanus (lava) |
| **Obsidian flux** | 1 obsidian glass, 10 sulfuric acid **at 500° or more** | 2 obsidian flux | 1 s | chemical plant | Vulcanus (hot acid) |
| **Molten iron from lava (flux)** | 500 lava, 1 obsidian flux | **300** molten iron, 10 stone | 16 s | foundry | Vulcanus (lava) |
| *vanilla molten iron from lava* | *500 lava, 1 calcite* | *250 molten iron, 10 stone* | *16 s* | *foundry* | |

**Lava heats the acid.** Lava is 1500°, so it is the planet's heat. The heating
recipe has **no productivity**. The foundry's built-in +50% would otherwise turn
100 acid into 150.

**The acid fields** (prototype-api.json, checked):
- the heating recipe's product uses FluidProductPrototype's `temperature = 500`;
- the flux recipe's ingredient uses FluidIngredientPrototype's
  `minimum_temperature = 500`;
- FluidPrototype's `max_temperature` defaults to `default_temperature`, which is
  why the change above is needed.

**Hot acid stays on Vulcanus.** The vanilla empty-barrel recipe gives the fluid
back with no temperature set (base/data-updates.lua), so a barrel brings
acid back at 25°. Only lava makes it hot again.

**Keep hot and cold lines apart.** Hot and cold acid mixed in one pipe average
their temperatures. A heater's output joined to the geyser line drops below 500°
and the flux plants stop. For now the player keeps the two lines apart
("We will try keeps lines apart for now"); see section 11.

**What flux costs:** 1 flux is half a glass (1 obsidian) and 5 hot acid (5 acid
and 1 lava). The molten iron recipe gives 20% more molten iron per foundry for
one flux a craft. Calcite still makes molten copper, so it stays as valuable as
it was.

**Acid per flux plant:** 10 acid a second, so 600 a minute. One heating foundry
(speed 4) gives 100 acid a second, enough for ten flux plants.

### Step 3: Fluxed steel (and obsidian slag)

| Recipe | Inputs | Outputs | Time | Machine | Where |
|---|---|---|---|---|---|
| **Fluxed steel** | 40 molten iron, 1 obsidian flux | 2 steel plate, 1 slag aggregate | 6.4 s | foundry | wherever there is molten iron |
| *vanilla casting steel (×2)* | *60 molten iron* | *2 steel plate* | *6.4 s* | *foundry* | |
| **Slag concrete** | 20 molten iron, 100 water, 5 slag aggregate | 10 concrete | 10 s | foundry | |
| *vanilla concrete from molten iron* | *20 molten iron, 100 water, 5 stone brick* | *10 concrete* | *10 s* | *foundry* | |
| **Slag brick** | 2 slag aggregate | 1 stone brick | 3.2 s | furnace | |
| *vanilla stone brick* | *2 stone* | *1 stone brick* | *3.2 s* | *furnace* | |

A third less iron per steel. The glass carries the impurities away as slag.
**Slag aggregate has outlets in two buildings** (principle 6): concrete and
stone brick here, and two induction casts later (section 8). None is mandatory, and none voids it.

Vanilla's steel plate productivity research boosts fluxed steel too.

### Step 4: Refined molten iron

| Recipe | Inputs | Outputs | Time | Machine | Where |
|---|---|---|---|---|---|
| **Refined molten iron** | 100 molten iron, 2 obsidian flux | 80 refined molten iron, 1 slag aggregate | 4 s | foundry | wherever there is molten iron |

Refined molten iron has **no barrel**, like molten iron. It loses a fifth of
the iron to slag. Its only use is the convergence.

### Step 5: Ozone capture

| Recipe | Inputs | Outputs | Time | Machine | Where |
|---|---|---|---|---|---|
| **Ozone collector** | 1 lightning rod, 4 supercapacitor, 1 storage tank, 40 electrolyte | 1 ozone collector | 5 s | EM plant | magnetic field 99 (Fulgora) |
| *vanilla lightning collector* | *1 lightning rod, 8 supercapacitor, 1 accumulator, 80 electrolyte* | *1 lightning collector* | *5 s* | *EM plant* | *magnetic field 99* |

**Ozone** is a fluid with **no barrel**. It has no recipe: only strikes make it
(section 9).

### Step 6: Holmium oxide

| Recipe | Inputs | Outputs | Time | Machine | Where |
|---|---|---|---|---|---|
| **Holmium oxide** | 100 holmium solution, 50 ozone | 6 holmium oxide | 5 s | chemical plant | Fulgora (ozone and holmium solution have no barrel) |
| **Holmium plate from oxide** | 1 holmium oxide | 1 holmium plate | 1 s | foundry | anywhere |
| *vanilla holmium plate (×5)* | *100 holmium solution* | *5 holmium plate* | *5 s* | *foundry or assembler* | |

Six plates per 100 solution, not five: 20% more holmium, paid for in ozone.
That is the most the tree adds to holmium, so holmium stays scarce
(principle 5).

### Step 7: Oxide superconductor

| Recipe | Inputs | Outputs | Time | Machine | Where |
|---|---|---|---|---|---|
| **Oxide superconductor** | 1 holmium oxide, 1 copper plate, 1 plastic bar, 20 ozone | 2 superconductor | 5 s | EM plant | Fulgora (ozone) |
| *vanilla superconductor* | *1 holmium plate, 1 copper plate, 1 plastic bar, 5 light oil* | *2 superconductor* | *5 s* | *EM plant* | |

It makes the vanilla superconductor. It is cheaper because the oxide is cheaper
than the plate and no light oil is needed. The ozone is the price: it stops when
the tanks run dry.

### Step 8: Superconducting coil

| Recipe | Inputs | Outputs | Time | Machine | Where |
|---|---|---|---|---|---|
| **Superconducting coil** | 4 superconductor, 2 steel plate, 10 electrolyte | 1 superconducting coil | 10 s | EM plant | Fulgora (electrolyte has no barrel) |
| *vanilla supercapacitor* | *2 holmium plate, 2 superconductor, 4 electronic circuit, 1 battery, 10 electrolyte* | *1 supercapacitor* | *10 s* | *EM plant* | |

The coil is an item and ships. Stack 50.

### Step 9: Induction foundry (convergence)

| Recipe | Inputs | Outputs | Time | Machine | Where |
|---|---|---|---|---|---|
| **Induction foundry** | 1 foundry, 10 superconducting coil, 20 obsidian glass, 20 tungsten plate | 1 induction foundry | 20 s | assembler | pressure 4000 (as the foundry's recipe) |
| *vanilla foundry* | *50 tungsten carbide, 50 steel, 30 electronic circuit, 20 refined concrete, 20 lubricant* | *1 foundry* | *10 s* | *assembler* | *pressure 4000* |
| **Molten holmium iron** | 100 refined molten iron, 2 holmium oxide | 100 molten holmium iron | 4 s | induction foundry | wherever refined molten iron is |
| **Field core** | 1 superconducting coil, 50 molten holmium iron | 1 field core | 10 s | induction foundry | |

**Molten holmium iron** has **no barrel**. The holmium oxide is fluxed into the
refined iron and held in the foundry's field. The **field core** is that fluid
cast around a coil: a coil in an iron body, ready to charge.

The same tech unlocks the **five induction casts** (section 8).

### Step 10: Magnetar alloy (capstone)

| Recipe | Inputs | Outputs | Time | Machine | Where |
|---|---|---|---|---|---|
| **Magnetar alloy** | 1 field core | 1 magnetar alloy | 20 s | induction foundry | |
| **Magnetic collector** | 1 asteroid collector, 10 magnetar alloy, 2 superconducting coil | 1 magnetic collector | 10 s | assembler | |
| *vanilla asteroid collector* | *20 low density structure, 8 electric engine unit, 5 processing unit* | *1 asteroid collector* | *10 s* | *assembler* | |

Charging is time in the field, nothing else. The **stub recipe goes**. The item
keeps its name (sae-magnetar-alloy), so saves keep what they hold.
**Weight: 2 kg**, the stub's and the superconducting winding's.

### What one magnetar alloy costs

Before productivity:
- 1 field core: 1 coil and 50 molten holmium iron.
- 1 coil: 4 superconductor (2 holmium oxide, 40 ozone), 2 steel, 10 electrolyte.
- 50 molten holmium iron: 1 holmium oxide and 50 refined molten iron.
- So: 3 holmium oxide (50 holmium solution, which is 1 holmium ore), 65 ozone,
  and about 100 molten iron.
- That is under one strike of ozone (section 9). The pressure is the steady
  ozone draw, not the cost of one alloy.

### Step 11: Magnetite rounds

| Recipe | Ingredients | Result | Time | Made in |
|---|---|---|---|---|
| **Magnetic chunk crushing** | 1 magnetic asteroid chunk | 10 magnetite (chunk returned as in metallic crushing) | 2 s | crusher |
| **Magnetite round** | 5 magnetite, 2 superconducting coil, 5 steel plate, 2 explosives | 1 magnetite round | 30 s | assembler |
| *vanilla railgun ammo* | *5 steel plate, 10 copper cable, 2 explosives* | *1 railgun ammo* | *25 s* | *assembler* |

**Against vanilla's round:** 15,000 damage against 10,000, but it fires 1.5× slower (every 4.25 s, against 2.8 s). Both are railgun ammo, so vanilla's railgun research boosts both alike.

| Target | Health | Vanilla round | Magnetite round |
|---|---|---|---|
| Big or huge, metallic, carbonic, oxide | 2,000–5,000 | 1 shot, 2.8 s a kill | 1 shot, 4.25 s a kill |
| Huge promethium | 10,000 | 2 shots, 5.7 s a kill | **1 shot, 4.25 s a kill** |

So it's slower against everything except the biggest promethium asteroids, and costs more.

## 8. Buildings

All three use **tinted vanilla** as stand-in art (derive.placeholder_art): the
nearest vanilla building, with its own tint. Real art is a separate task for
each.

### Ozone collector (from the lightning collector)

| | Ozone collector | Lightning collector |
|---|---|---|
| Size | 2×2 | 2×2 |
| Attracts strikes | yes, range elongation 15 (the rod's) | yes, 25 |
| Power from a strike | **none** (efficiency 0) | 40% (400 MJ of 1000 MJ) |
| What a strike gives | **100 ozone** | 400 MJ |
| Holds | 1,000 ozone (ten strikes) | 1,000 MJ |
| Output | one pipe connection, through a wall fitting | electric |
| Stand-in tint | pale blue | — |

**The trade-off:** every strike it takes is a strike no collector turns into
power. Storm spots are shared between power and ozone. How the strike becomes
ozone (prototypes only, or a small script) is T02's test (a).

### Induction foundry (from the foundry)

Liam: "It shouldn't do vanilla recipes but offer alternative recipes for the
cost of an extra ingredient with a slight bump in speed and/or productivity";
the extra ingredient is chosen "Per recipe"; the recipes are "The core casts".

| | Induction foundry | Foundry |
|---|---|---|
| Size | 5×5 | 5×5 |
| Crafts | **induction only**: the three field recipes and five induction casts. No vanilla recipe | metallurgy, crafting with fluid |
| Speed | 4 | 4 |
| Built-in productivity | +50% | +50% |
| Modules | 4 | 4 |
| Power | **4 MW** | 2.5 MW |
| Stand-in tint | cold blue-violet | — |

**The machine is the foundry's equal.** Every gain is in the recipe, paid for by
its extra ingredient. Then the gain is the same with or without modules, and the
player can read it straight off the recipe.

**Never strictly better:**
- it can't run vanilla's recipes, so without the extra ingredient it makes
  nothing;
- with it, it uses 60% more power for a 10–18% gain. That is 1.36 to 1.45 times
  the power per unit made (1.6 ÷ 1.18 to 1.6 ÷ 1.10);
- the vanilla foundry keeps the tree's own flux routes (molten iron with flux,
  fluxed steel).

**Gain is sized to what the extra costs:**
- slag aggregate, a byproduct: **+10%**;
- obsidian flux or hot acid, made on Vulcanus: **+17–18%**.

#### The five induction casts

These are five of the vanilla foundry's core casts (space-age/prototypes/recipe.lua). Molten iron from lava and steel are left out, because the tree already has its own (Liam: "Just drop them").
Item extras come in batches of the vanilla recipe, so one extra item goes into
each craft.

| Cast | Vanilla recipe | Induction recipe | Extra, and why it fits |
|---|---|---|---|
| Molten copper from lava | 500 lava, 1 calcite → 250 molten copper, 15 stone; 16 s | 500 lava, 1 calcite, **20 hot acid** → **275** molten copper, 15 stone; **15 s** | Hot sulfuric acid leaches copper out of the rock, as real copper works do |
| Iron plate (×5) | 100 molten iron → 10 iron plate; 16 s | 100 molten iron, **1 obsidian flux** → **11** iron plate; **15 s** | Flux skims the cast clean |
| Copper plate (×5) | 100 molten copper → 10 copper plate; 16 s | 100 molten copper, **10 hot acid** → **11** copper plate; **15 s** | Acid pickles the oxide skin off |
| Iron gear wheel (×10) | 100 molten iron → 10 gear; 10 s | 100 molten iron, **1 slag aggregate** → **11** gear; 10 s | Crushed slag as mould sand |
| Copper cable (×15) | 75 molten copper → 30 cable; 15 s | 75 molten copper, **1 obsidian flux** → **33** cable; **14 s** | Flux in the melt means fewer breaks in the draw |

"Hot acid" is sulfuric acid at 500° or more. Vanilla's recipes themselves are
1-craft (20 molten iron → 2 plates in 3.2 s, and so on). The batches above are
the same figures multiplied, for comparison.

#### The numbers, per building per minute

**The arithmetic:** both machines run at speed 4 with +50% built-in
productivity and no modules. So output a minute = output a craft × (60 ÷ time)
× 4 × 1.5 = output × 360 ÷ time. Extra used a minute = extra a craft × (60 ÷
time) × 4. Productivity doesn't raise what goes in.

| Cast | Vanilla foundry | Induction foundry | Gain | Extra used a minute | Extra, traced back |
|---|---|---|---|---|---|
| Molten copper from lava | **5,625** | 275 × 360 ÷ 15 = **6,600** | **+17%** | 320 hot acid | 320 acid, 64 lava |
| Iron plate | 10 × 360 ÷ 16 = **225** | 11 × 360 ÷ 15 = **264** | **+17%** | 16 obsidian flux | 16 obsidian, 80 hot acid |
| Copper plate | **225** | **264** | **+17%** | 160 hot acid | 160 acid, 32 lava |
| Iron gear wheel | 10 × 360 ÷ 10 = **360** | 11 × 360 ÷ 10 = **396** | **+10%** | 24 slag aggregate | a byproduct |
| Copper cable | 30 × 360 ÷ 15 = **720** | 33 × 360 ÷ 14 = **849** | **+18%** | 17.1 obsidian flux | 17.1 obsidian, 86 hot acid |

**Beside the tree's vanilla-foundry routes:** the tree's own molten iron with flux and fluxed steel stay in the vanilla foundry. The induction foundry has no version of either.

**Slag balance:** one fluxed steel foundry makes 1 × 60 ÷ 6.4 × 4 × 1.5 = 56
slag aggregate a minute (slag is a product, so
productivity counts). That covers about two induction gear foundries (24 a
minute each).

#### The three field recipes

They keep the times in section 7, now at speed 4. **Molten holmium iron** takes
the built-in +50% like any cast. **Field core and magnetar alloy take no
productivity**, so one coil always makes one alloy and the capstone costs what
section 7 says (question 15).

### Magnetic collector (from the asteroid collector)

| | Magnetic collector | Asteroid collector |
|---|---|---|
| Size | 3×3 | 3×3 |
| Collection radius | **15** | 7.5 |
| Arm speed | **0.55** | 0.2 |
| Arm turn speed cap | 0.55 | 0.2 |
| Energy per arm move | **4 kJ (slow 1.2 kJ)** | 1 kJ (slow 300 J) |
| Chunks | **any, no filter** | any; filter optional |
| Where | platforms only (pressure 0) | platforms only |
| Quality scaling | as vanilla | — |
| Stand-in tint | dark iron-grey | — |

**What differs:** reach and arm speed, against four times the power and the magnetar alloy cost. No filter is used (Liam: "We shouldn't alter the filter of either collector"). T02e measured the catch rates.

## 9. Resources

### Obsidian, on Vulcanus

An ore of fast-cooled volcanic glass, in the **basalt lowlands near the lava**,
so it is semi-real and fits the planet. Mined by any drill, with no fluid.

| | Obsidian | Tungsten ore | Calcite |
|---|---|---|---|
| Biome | basalts | basalts | mountains |
| Spot count per region | **10** | 15 | 12 |
| Region size | 400 + 400 / frequency (non-metal) | 500 + 500 / frequency | 400 + 400 / frequency |
| Patch radius | **25** × size | 25 × size | 25 × size |
| Richness | **15,000** × richness / size | 10,000 | 24,000 |
| Mining time | 1 | 5 | 1 |
| Starting-area patch | **none** | yes | yes |
| Map sliders | its own (frequency, size, richness) | own | own |

Smaller and fewer patches than tungsten, but richer, because each craft needs
little (one obsidian per 300 molten iron). There is no starting patch: the
starting area is long generated, and "New ground only" means it appears in
chunks generated after the mod loads. T02's test (b) counts patches over five
seeds.

### Ozone, on Fulgora

| | Proposal |
|---|---|
| Per strike on an ozone collector | **100 ozone** |
| Collector holds | 1,000 (ten strikes) |
| Barrel | none |

**What the plants drink, at full speed:**
- one chemical plant on holmium oxide: 50 ozone every 5 s, so **600 a minute**;
- one EM plant on oxide superconductor (speed 2): 20 ozone every 2.5 s, so
  **480 a minute**.
- So a plant needs about five or six strikes a minute, averaged over storm and
  calm. How many strikes a collector takes in a storm is measured in T02 (a),
  and ozone per strike is set from that.

### Sulfuric acid, on Vulcanus (vanilla)

From the geysers, as now. The only change is that it can be heated to 500°.

### Magnetic chunks, on the Vulcanus ↔ Fulgora route

A new direct route between Vulcanus and Fulgora, 15,000 km. Its ordinary asteroids blend Nauvis–Vulcanus's mix at the Vulcanus end with Nauvis–Fulgora's at the Fulgora end. The magnetic chunk flies only here, at speed 0.25 (probability 0.0015 per spawn point). There are no big or huge magnetic asteroids, only chunks.

## 10. Verified

- **Molten iron, holmium solution and electrolyte have no barrel** (vanilla
  auto_barrel = false). Ozone, refined molten iron and molten holmium iron will
  be made the same way.
- **The EM plant's own recipe and the lightning collector's recipe need magnetic
  field 99**; the foundry's recipe needs pressure 4000. The new buildings copy
  these.
- **Sulfuric acid** (base/prototypes/fluid.lua) has default_temperature 25 and
  no max_temperature. FluidPrototype's max_temperature defaults to
  default_temperature, so today it can't be heated. Lava is 1500°.
- **Temperature fields exist** (prototype-api.json):
  - FluidIngredientPrototype has `temperature`, `minimum_temperature` and
    `maximum_temperature`;
  - FluidProductPrototype has `temperature`.
- **Barrels drop the temperature:** vanilla's generated empty-barrel recipe sets
  no temperature on its fluid result (base/data-updates.lua).
- **The vanilla foundry** is speed 4, 2.5 MW, 4 modules, +50% built-in
  productivity. The five casts it has an induction version of are in section 8's table.
- **The asteroid collector** reaches 7.5 tiles, arm speed 0.2. It has no
  prototype field limiting which chunks it takes. Filters are runtime only
  (LuaEntity.set_filter).
- **Lightning** carries 1000 MJ. A collector keeps 40%, a rod 20%. Fulgora
  strikes about once per chunk per 10 s while it storms. The attractor has
  strike and hit trigger effects.
- **Vulcanus's resources** use spot noise per biome: tungsten (15 spots, 10,000
  richness, basalts), calcite (12, 24,000, mountains), coal (12, 18,000,
  ashlands).
- **Vanilla figures** in sections 6 to 8 are from the installed Space Age
  data (recipe.lua, technology.lua, entities.lua, planet-vulcanus-map-gen.lua).

## 11. Still open

**T02 must settle:**
- **(a) Ozone per strike:** whether a strike can add ozone with prototypes alone
  or needs a small script, how many strikes a collector takes in a storm, and
  the UPS cost with 50 collectors. Then the 100 per strike is set.
- **(b) Obsidian autoplace:** patch counts over five seeds of new Vulcanus
  ground, and that an old save gets them only in new chunks, without errors.

**Also open:**
- **Hot and cold acid in one pipe.** They average. "For now" the player keeps
  the lines apart. Whether that is a fair puzzle or a trap is to watch in play.
  If it is a trap, a later fix is a separate fluid. That is not designed here.
- **The heating recipe's time** (4 s). It sets how many heaters a flux line
  needs, and nothing else.
- **Numbers.** Every ratio here is a first guess. Balance playtesting is a later
  task.
- **Ozone's rhythm.** Whether buffering through a calm is a puzzle or a chore is
  the thing to watch first.
- **The Core's use.** Magnetar alloy has one use today, the magnetic collector.
  The magnetic core billet comes when the Core's recipes return.

## 12. Decided (Liam, 2026-10-30)

1. **Ozone per strike:** 100, with 1,000 held per collector, then set from
   T02 (a). "Yes, recommended."
2. **The crossing is one-way:** coil and oxide go to Vulcanus, and nothing
   comes back. "Yes, recommended."
3. **The convergence's location is left open.** No lock ties the induction
   foundry to Vulcanus; lava makes it the cheap place. "Yes, recommended."
4. **Oxide superconductor makes the vanilla superconductor.** "Yes,
   recommended."
5. **The induction foundry** runs no vanilla recipe. It offers alternatives of
   the core casts, each for an extra ingredient, with a slight gain. "It
   shouldn't do vanilla recipes but offer alternative recipes for the cost of
   an extra ingredient with a slight bump in speed and/or productivity, we'd
   need to run the numbers"; "Per recipe"; "The core casts". Principle 3
   changes to allow it: "Change the principle" (design/01-principles.md).
6. **The ozone collector gives no power.** "Yes, recommended."
7. **Refined molten iron** has no use before the convergence. "Yes,
   recommended."
8. **Magnetar alloy weighs 2 kg.** "Yes, recommended."
9. **The slag item is "Slag aggregate"**, unlocked by Fluxed steel. "Yes,
   recommended."
10. **Obsidian flux is made from glass and superheated sulfuric acid.** "flux
    should be from glass and a fluid found on vulcanus"; "What about super
    heated sulfuric acid"; "Lava heats it"; "We will try keeps lines apart for
    now".
11. **The packs:** each path on its own planet's pack; both openers need both
    planets' science packs. "Yes, recommended."
12. **Obsidian patches:** 10 spots, radius 20, richness 15,000, in the basalts,
    with no starting patch, then adjusted from T02 (b). "Yes, recommended."
    After T04's seed counts (two of five seeds thin): radius 25. "Bigger
    patches."
13. **Tech costs:** 200 to 500 a path step, 750 and 1000, all at 60 s.
    "Yes, recommended."
14. **The endgame role:** "Collector only for now."

15. **Productivity in the field recipes:** molten holmium iron takes the +50%;
    field core and magnetar alloy take none, so one coil makes one alloy.
    "Yes, all three."
16. **Sulfuric acid's max_temperature is raised to 500**, the tree's one touch
    to a vanilla prototype; cold acid behaves as before. "Yes, all three."
17. **The induction foundry at 4 MW**, with gains of 10% for slag and 17–18% for
    flux and acid, as first guesses. "Yes, all three."
18. **No induction cast crosses the tree's own recipes:** "Check the new
    induction recipes against the recipes introduced in the tree. None should
    cross over" → molten iron from lava and steel are dropped: "Just drop them".

**2026-10-31:**

19. **The magnetic collector:** "Accept tilt"; arm and turn speed 0.55, reach 15; no filter, it takes every chunk; its downside "Much more power + cost" (4× energy per arm move).
20. **A new direct Vulcanus ↔ Fulgora route,** 15,000 km, its mix "Blend Nauvis–Vulcanus + Nauvis–Fulgora"; UPS "Accept".
21. **The chunk makes magnetite:** "Magnetite but it needs a use"; "A new type of ammo"; "Railgun ammo"; "Needs to be compared against railguns anmo"; more damage, costs more; "Fire rate should be slower so the rounds are intended for high health targets only" ("1.5× slower"); 10 magnetite a chunk; "11th tech after railgun".
22. **Tree size:** "Change from limit to estimate"; "'Estimated 3–10'".
23. **Fluxed steel takes vanilla's steel productivity research:** "Add to vanilla tech".
24. **Planet locks behave as vanilla's; obsidian distance judged in play; the coil is the usual leg, the oxide the forced one:** "Accept all three".
