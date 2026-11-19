# Engine facts (Factorio 2.1.21-2.1.24), verified in this project

Each line is worded as `DOCUMENTATION-LANGUAGE.md` §7.1 says.

## Animation and sound
- Crafting machines play `animation_speed × crafting_speed × animation_progress`
  (measured in a client on the Core, 2026-10-10, one screenshot a tick for 720
  ticks: a comment in `prototypes/core/machines.lua` at 677b1ea).
  `animation_progress` defaults to 0.5, and to 1 for mining drills
  (prototype-api.json, CraftingMachineGraphicsSet and MiningDrillGraphicsSet;
  2.1.24, read 2026-11-18).
- A crafting machine's animation is not reset at the start of a craft; it
  freezes when the machine stops and resumes from that frame. A placed
  machine starts on a random frame. So motion can be rate-locked to crafts,
  never phase-locked. (Drop Crusher, client, 2026-10-11.)
- `idle_animation` must have the same frame count as `animation`
  (docs WorkingVisualisations; the engine errors otherwise). It draws when
  the machine is not working, except unpowered with a recipe and input,
  where the main animation freezes. (Client, 2026-10-11.)
- A `sound_accents` entry on frame 0 never fires: 0 is the unset value.
  Use frame 1 or later; `derive.working_sound` refuses 0. (Recorded in a
  client, 2026-10-11.)
- Accent frames count from 0 on the animation they name, and with a
  `frame_sequence` they count its entries, not sprite frames. (Reaction
  Plant T04, measured again with sound in T10, 2026-10-29.)
- A generator (`GeneratorPrototype`) draws `pictures` (north/east, each
  animation + frozen_patch): no `working_visualisations`, no
  status-tinted lamp. Its animation speed scales with output through
  `perceived_performance`. (Docs and client, Siderane turbine, 2026-10-11.)
- A `burner-generator` draws only `animation` and `idle_animation`; glow
  goes in as `draw_as_glow` layers; brightness cannot scale with load,
  only speed. (Docs, 2026-10-11.)
- `two_direction_only` generators collapse south to north and west to
  east. (Client, 2026-10-11.)
- A mining drill's animation is not sped up by its `mining_speed` (Ballast
  Drill, seen in a client on the Core, 2026-10-10: a comment in
  `prototypes/core/machines.lua` at 677b1ea, removed in 65db6bc).

## Neighbour bonus
- `neighbour_bonus` is a property of `ReactorPrototype`, whose reactors output
  heat, and of `FusionReactorPrototype`, whose reactors output a fluid
  (prototype-api.json; 2.1.24, read 2026-11-18). A reactor whose burner takes
  only `sae-radiant` fuel gets the full bonus, as a vanilla uranium bank does
  (a spike against the engine, 2026-09-17; its one record is
  `design/production-line-plan.md` at 35e77fb, a file since removed).

## Map generation
- Tiles repeat per tile, so a sheet cannot carry a depth gradient across a
  pool (one source: the header of `concept/radiant-look-pool-icons/pool_look_b.py`,
  2026-10-14).
- A vanilla planet's tile expressions do not carry over to another surface:
  they read that surface's own inputs, so a tile used elsewhere needs
  expressions of its own.
  - Vulcanus's ash tiles read `vulcanus_ashlands_biome`, `aux` and `moisture`
    (knowledge-base/2.1.24/data/space-age/prototypes/tile/tiles-vulcanus.lua:316-333).
    The Core's `aux` and `moisture` vary far more slowly than Vulcanus's, so
    there the tiles' edges stepped in straight lines (seen 2026-10-12; the
    cause found by the map-gen-fallback task's spike T01, 2026-10-20).
  - Aquilo's snow expressions add the surface's elevation
    (knowledge-base/2.1.24/data/space-age/prototypes/planet/planet-aquilo-map-gen.lua:332,
    :337, :342). On the Core each snow tile's expression came out far higher
    than those of the pool, shore and glow tiles, so all three vanished
    (`prototypes/core/map-gen.lua:85-89`, 2026-10-20).
- A resource added to a vanilla planet's map gen reaches new games only. A
  save's existing surface keeps its stored map gen settings, so even new
  chunks get none, until a script adds the autoplace entries to that surface
  (on_configuration_changed). Explored ground never gets them. (V↔F T02 (b),
  2026-10-30.)

## Surfaces, lights and placement (2.1.23, 2026-10-21)
- `day-night-cycle = 0` freezes a surface at noon (always_day, darkness
  0); above 0 the engine runs the cycle and the value reaches existing
  saves. Dusk, evening, morning and dawn are runtime settings (control
  stage). Source: core-sky T01/T05.
- A LightDefinition and a `draw_as_light` layer show only in the dark;
  `draw_as_glow` shows by day and night. LightDefinition `size` is a
  radius in tiles. Source: vent-pump T07b, vents T02, doc-html
  LightDefinition.
- Resources sit on tile centres; an even-sized building centres on a
  tile corner, so a 2x2 pump sits half a tile off its vent. Odd-sized
  pumps (the pumpjack's 3x3, reach 0.49) sit centred. Source:
  gas-pump-3x3 T01.
- A player cannot build any drill over a resource that needs a fluid
  until the force has `mining_with_fluid`, which only Uranium mining
  grants. Source: vent-pump-hand-build T01.
- A mining drill draws `graphics_set` dry and `wet_mining_graphics_set`
  on a resource that needs a fluid (vanilla's drills show their pipe
  fittings only wet). Source: big-mining-drill.lua:627-628.
- A burner generator with no fuel and one fuelled with no demand draw
  the same: `idle_animation` alone (or the frozen animation if none);
  an idle with the animation's frame count holds the frame it stopped
  on; a one-frame idle needs `repeat_count`. Speed follows output, with
  `perceived_performance.minimum` as the floor. Source:
  radiant-generator T08b.
- A corpse may carry a `draw_as_glow` layer (vanilla's demolisher
  fissure scorch mark). Source: radiant-generator T08e.

## Lightning and asteroid collectors (2.1.24, 2026-10-30)
- No trigger effect adds fluid, and a lightning attractor has no fluid box. To
  make a fluid per strike: a script effect in the lightning's
  `attractor_hit_effect`, under `target_effects`, raises
  `on_script_trigger_effect` with the attractor hit as `target_entity`; under
  `source_effects` it gives only the lightning. It fires for every attractor,
  including ruins and vanilla rods. Cost with 50 collectors: 0.0003–0.006
  ms/tick (V↔F T02 (a), 2026-10-30; in the main checkout's `evidence/vf-t02/`:
  the benchmark script `probe-mods/bench.sh`, the launcher's run record
  `client-20261030-221332-1263405/run.json`, and the figures in
  `summary.txt`).
- Fulgora's lightning falls only at night: its daytime multiplier is 0. A
  collector in a storm took about one strike every 14 s: 216 strikes on 50
  collectors in 3600 ticks (V↔F T02 (a), 2026-10-30, the same run:
  `evidence/vf-t02/summary.txt`).
- An asteroid collector's catch area is a square, half-side
  `collection_radius`, centred `collection_box_offset` tiles ahead (5 in
  vanilla). No prototype field limits which chunks it takes. Filters are a
  runtime whitelist: `filter_slot_count` is 0 on a fresh collector and grows as
  filters are set, `get_filter` returns the prototype, not its name, and
  circuit 'set filters' overwrites them with no event. Turning that circuit
  mode off clears them. (V↔F T02 (c).)
- Asteroid chunks stack to 1. (V↔F T02 (c).)
- An entity with no item that places it can't have a ghost. (V↔F T02 (c).)
- A collector's catch area grows by `QualityPrototype.asteroid_collector_collection_radius_bonus` per quality (by default the quality level: +1 for uncommon … +5 for legendary). An arm at rest can't catch a fast chunk. An arm already out, chasing slower chunks, can. So chunk speed changes which collector catches what, but no collector is locked out. (V↔F T02e, 2026-10-31.)

## Recipes
- `allow_productivity = false` keeps productivity modules out but doesn't stop a machine's built-in productivity (the foundry's +50 %). To give a recipe none at all, also set `maximum_productivity = 0`. (V↔F T05a, measured in a client, 2026-10-31.)
- A recipe's surface conditions are checked when a player picks it (or a blueprint is built), not while the machine crafts. A recipe set by script crafts off its planet. Vanilla's lightning collector and foundry recipes behave the same. The 2.1.24 runtime docs word it as 'required to craft'. (V↔F T07a, 2026-10-31.)

## Technologies
- A `craft-item` research trigger counts what a machine crafts, including a
  recipe's second result: a Heavy crusher's fines fired Vent tapping's trigger
  (design/09-core-tech-tree.md) once its count was reached, with nothing else
  making fines (core-vanilla-machines T01, in a client, 2026-11-16:
  `tools/client/launch.sh` with the probe mod; the probe, the launcher's
  record and the result in the main checkout's
  `evidence/core-vanilla-machines/T01/tester/`).

## Fluids
- A fluid's `max_temperature` defaults to its `default_temperature`, so
  vanilla sulfuric acid (25°, no max) can't be heated without raising it. A
  recipe can require a temperature (`minimum_temperature` on a fluid
  ingredient) and set one (`temperature` on a fluid product). Vanilla's
  generated empty-barrel recipe sets no temperature, so a barrelled fluid comes
  back at its default. (V↔F T01 research, base/prototypes/fluid.lua and
  base/data-updates.lua, 2026-10-30.)

## Running a client on this machine
- `xvfb-run` alone leaves WAYLAND_DISPLAY set, and the client then opens
  full-screen on Liam's desktop (seen twice: the crust-tap spike, 2026-10-02,
  and an icons-wiring test, 2026-10-11).
- PULSE_SINK alone does not stop a client's sound reaching the speakers:
  Factorio's own PipeWire output still reached them (one report: a tester's
  first client run, 2026-10-11).
- A second client's Steam connect may reach the first: a client once got a
  join and a quit it did not send, probably from another agent's client (one
  report, 2026-10-11; the cause is not confirmed).
- The data-stage check opens no image. The data stage never opens one (one
  source: `tools/check-data-stage.sh`, its note at line 121, 2026-09-04). The
  two image checks the script runs only test that the files they name exist
  (`tools/check-graphics.sh`, `tools/check-dumped-graphics.py`, read
  2026-11-19).
  - One source says an animation whose layers disagree on frame count passes
    the check and fails only when sprites load. The Drop Crusher's stroke was
    checked by a client load to `Sprites loaded`, with no error
    (`graphics/building-spec-drop-crusher.md` at bc0f1b4, 2026-09-10; the
    paragraph was cut in 46aa931).

## Sprites and rotation
- A crafting machine cannot be rotated unless it has a fluid box, a heat
  energy source, a fluid energy source, or a non-square collision box; one
  with a non-square collision box can be rotated only before it is placed
  (prototype-api.json, `CraftingMachinePrototype`; 2.1.24, read 2026-11-18).
- `util.by_pixel(x, y)` = `{x/32, y/32}`, x and y in game pixels, whatever the
  sprite's scale: it takes no scale (knowledge-base/2.1.24/data/core/lualib/util.lua:174-176,
  read 2026-11-18). Sprite size in tiles = source pixels × scale / 32 (one
  source: a note added to the building-spec template in ef47a72, 2026-09-05,
  and moved here on 2026-11-15).
