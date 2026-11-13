# Gameplay facts (Factorio 2.1.24), verified in this project, 2026-11-13

Each line: the fact, then its source and date. Lua paths are under
knowledge-base/2.1.24/data/; "dump" is knowledge-base/2.1.24/data-raw-dump.json.
"Computed" means worked by hand from the docs, not read from the engine;
"graph.py" is tools/gameplay/graph.py on the dump.

## Science packs
- Packs and where they can be made: automation, logistic, military,
  chemical, production, utility anywhere, in assembling machines; space on
  a platform (gravity 0); metallurgic on Vulcanus (pressure 4000, foundry);
  agricultural on Gleba (pressure 2000, biochamber); electromagnetic on
  Fulgora (magnetic field 99, EM plant); cryogenic on Aquilo (pressure 300,
  cryogenic plant); promethium on a platform (gravity 0, cryogenic plant).
  The solar system edge and shattered planet are space locations with no
  surface; no pack is made there. (Recipe surface_conditions against planet surface_properties, dump;
  space-age/prototypes/recipe.lua:750-853, :2764; space-age/prototypes/planet/planet.lua:708, :724;
  2.1.24, 2026-11-13.)
- Recipes: automation 5 s, copper plate + gear -> 1; logistic 6 s,
  inserter + belt -> 1; military 10 s, piercing magazine + grenade + 2
  walls -> 2; chemical 24 s, 2 engines + 3 red circuits + sulfur -> 2;
  production 21 s, electric furnace + prod module + 30 rail -> 3; utility
  21 s, 3 LDS + 2 blue circuits + robot frame -> 3. (base/prototypes/recipe.lua:1002,
  :1020, :1982, :1963, :2001, :2020; 2.1.24, 2026-11-13.)
- Space 15 s, 2 iron plate + carbon + ice -> 5; metallurgic 10 s, 3
  tungsten carbide + 2 tungsten plate + 200 molten copper -> 1;
  agricultural 4 s, bioflux + pentapod egg -> 1; electromagnetic 10 s,
  supercapacitor + accumulator + 25 electrolyte + 25 holmium solution -> 1;
  cryogenic 20 s, 3 ice + lithium plate + 6 cold fluoroketone -> 1 + 3 hot
  fluoroketone; promethium 5 s, 25 promethium chunks + quantum processor +
  10 biter eggs -> 10. (space-age/prototypes/recipe.lua:750, :777, :800,
  :829, :853, :2764; 2.1.24, 2026-11-13.)
- Every pack recipe allows productivity. Agricultural packs spoil in 1 h
  (216000 ticks) to spoilage. (dump; 2.1.24, 2026-11-13.)
- Raw cost per pack, by `tools/gameplay/graph.py <dump> --section cost`
  (the engine's first-picked recipe, recycling and barrelling left out,
  by-products not credited, no productivity; raws are mining results,
  plants, trees, asteroid chunks and tile fluids): automation 2 iron ore,
  1 copper ore; logistic 5.5 iron, 1.5 copper; military 10 stone, 5.75
  iron, 5 coal, 0.5 copper; chemical 83.33 crude oil, 12 iron, 7.5
  copper, 7.5 water, 1.5 coal; metallurgic 440 lava, 30 sulfuric acid, 14
  tungsten ore, 3 carbon, 0.88 calcite; agricultural 300 spoilage, 60
  water, 1.875 yumako, 0.75 jellynut. (graph.py, T02 2444679; 2.1.24,
  2026-11-13.)
- By that order petroleum gas comes from basic oil processing and light
  oil from advanced oil processing (their `order` strings sort before the
  cracking recipes'). Ice is costed from ammoniacal-solution separation, a
  no-decomposition recipe (marked `*`); holmium ore has no route outside
  scrap recycling. (graph.py; T04 evidence c7-routes-r2.out; 2.1.24,
  2026-11-13.)

## Planets and their order
- Vulcanus, Gleba and Fulgora are each discovered by a 1000 x (red, green,
  blue, space) technology after space-platform-thruster; Gleba also needs
  landfill, Fulgora electric-energy-accumulators. None needs another
  planet. (space-age/prototypes/technology.lua:367, :399, :431; 2.1.24,
  2026-11-13.)
- planet-discovery-aquilo costs 3000 x nine packs, including metallurgic,
  agricultural and electromagnetic, so it needs all three inner planets.
  (space-age/prototypes/technology.lua:467, :495-498; 2.1.24, 2026-11-13.)
- stellar-discovery-solar-system-edge (fusion-reactor, railgun) adds
  cryogenic; the promethium-science-pack technology (biter-egg-handling,
  the edge) unlocks the shattered planet. (space-age/prototypes/technology.lua:2003,
  :2038; 2.1.24, 2026-11-13.)
- Each planet's pack technology is a craft trigger behind that planet's
  discovery: tungsten plate, 100 bioflux, supercapacitor, cryogenic plant.
  (space-age/prototypes/technology.lua:838, :1144, :1556, :1875; 2.1.24,
  2026-11-13.)
- Routes: Nauvis to Vulcanus, Gleba, Fulgora 15000; Vulcanus-Gleba and
  Gleba-Fulgora 15000; Gleba and Fulgora to Aquilo 30000; Aquilo to the
  edge 100000; the edge to the shattered planet 4000000.
  (space-age/prototypes/planet/planet.lua:743-823; 2.1.24, 2026-11-13.)

## Technologies
- 277 technologies; 32 are triggers with no packs. Roots: steam-power,
  electronics. Depth (edges on the longest prerequisite chain): inner
  discoveries 19, Aquilo 28, edge 34, research-productivity 36 (the
  deepest). (dump, analyst T01 run_all.py; 2.1.24, 2026-11-13.)
- Technologies needing each pack (count; unit count range; depth range):
  automation 245, 10-5000, 2-36; logistic 230, 20-5000, 3-36; military
  79, 50-5000, 5-36; chemical 170, 50-5000, 10-36; production 50,
  50-5000, 12-36; utility 73, 100-5000, 15-36; space 73, 50-5000,
  18-36; metallurgic 23, 500-5000, 25-36; agricultural 34, 50-5000,
  26-36; electromagnetic 25, 500-5000, 24-36; cryogenic 12, 500-5000,
  32-36; promethium 1 (research-productivity). Ranges leave out the
  count_formula (infinite) ones. (dump, analyst T01 run_all.py; 2.1.24,
  2026-11-13.)

## Weight and stacks
- Weights use `default_rocket_lift_weight` = 1 000 000 (1 t); the
  default item weight is 100. A rocket's cargo uses the silo's
  `lift_weight` (default 1 000 000): with the constant at 2e6 and the
  silo at 4e6, weights followed the constant and a rocket took 4000 iron
  plates. (core/prototypes/utility-constants.lua:555-556; spike load,
  T04 evidence spike-*.out; 2.1.24, measured in game 2026-11-13.)
- The engine stores a weight rounded down to a 1/65536 step, and rounds
  item-weight.html's intermediate result down to a whole number first:
  processing unit 3333.3333282, artillery wagon 531666. (T04, every item
  of vanilla and the mod read in game, c6-compare-r2.out; 2.1.24,
  2026-11-13.)
- Which recipe weighs an item, measured: not hidden and allowing
  decomposition; then named as the item; then not using the item as a
  catalyst; then subgroup, order, and recipe name. Category and
  hand-craftability made no difference, against item-weight.html. An item
  met again inside its own recipe chain takes the default weight for
  that use only, and is weighed properly later. (T04 spike load,
  spike-compare.out, spike-loopsim.out; 2.1.24, 2026-11-13.)
- Every science pack weighs 1 kg (1000) and stacks to 200: 1000 per
  rocket. Space packs stack to 200 in Space Age, 2000 in base.
  (base/prototypes/item.lua:694-695, space-age/base-data-updates.lua:826;
  2.1.24, 2026-11-13.)
- Set weights (stack): copper cable 250 (200), plastic 500 (100),
  sulfur 1000 (50), engine 2500 (50), LDS 5000 (50), rocket fuel 10000
  (20), tungsten plate 4000 (50), tungsten carbide 2000 (50), holmium
  plate 1000 (100), supercapacitor 2000 (100), carbon fiber 2000 (100),
  bioflux 1000 (100), lithium plate 2000 (100), quantum processor 5000
  (100), ores 2000 (50). (base/ and space-age/prototypes/item.lua, dump;
  2.1.24, 2026-11-13.)
- Computed weights (stack): iron, copper plate and gear 1000 (100);
  steel 2500 (100); electronic circuit 500 (200, the doc's example);
  advanced circuit 1000 (200); processing unit 3333.33 (100), 300 per
  rocket; battery 2500 (200); superconductor 1000 (200); electric engine
  2500 (50); flying robot frame 6666.67 (50). The engine gives the same,
  to the 1/65536 step. (doc-html/auxiliary/item-weight.html, dump; T04
  in game; 2.1.24, 2026-11-13.)

## Recycling
- A recycler returns 25 % of each item ingredient (fractions as
  extra_count_fraction), no fluids, in 1/16 of the recipe's time; an item
  with no recipe returns itself at 25 %. It runs at speed 0.5 with 4
  slots and takes no productivity. (recycler/recycling.lua:105-123,
  :263-264; recycler/data.lua:141-158; 2.1.24, 2026-11-13.)

## Productivity
- A recipe's productivity is capped at +300 % (maximum_productivity
  default 3); no vanilla recipe changes it. (prototype-api.json, dump;
  2.1.24, 2026-11-13.)
- Infinite recipe-productivity researches, +10 % a level: asteroid
  crushing, processing unit, steel, LDS, plastic, rocket fuel (each
  1.5^L x 1000), scrap recycling (1.5^L x 500), rocket part (1.5^L x 2000).
  Mining productivity +10 % a level; research productivity +10 % lab
  productivity, 1.2^L x 1000, all 12 packs. (space-age/prototypes/technology.lua:2108-2404,
  base/prototypes/technology.lua:5224-5273; 2.1.24, 2026-11-13.)
- Productivity modules give +4, +6, +10 %. (dump; 2.1.24, 2026-11-13.)

## Quality
- Qualities: normal 0, uncommon 1, rare 2, epic 3, legendary 5; each step
  up has next_probability 1 and a 10 % chain chance. (quality/prototypes/quality.lua,
  base/prototypes/categories/quality.lua; 2.1.24, 2026-11-13.)
- Quality modules give +1, +2, +2.5 % quality, each -5 % speed; speed
  modules give -1, -1.5, -2.5 %. (quality/prototypes/item.lua:20-54,
  base/prototypes/item.lua:2556-2604; 2.1.24, 2026-11-13.)
- A module's effect scales by 1 + 0.3 x its quality level, so a
  legendary tier-3 quality module gives 6.25 %. Computed from the doc
  defaults. (prototype-api.json QualityPrototype; 2.1.24, 2026-11-13.)

## Difficulty
- DifficultySettings has two settings only: technology_price_multiplier
  (default 1, 0.001-100000) and spoil_time_modifier (default 1,
  0.01-100). The marathon presets set the price multiplier to 4.
  (runtime-api.json, prototype-api.json, base/prototypes/map-gen-presets.lua:38-41;
  2.1.24, 2026-11-13.)
