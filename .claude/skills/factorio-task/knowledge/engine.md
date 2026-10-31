# Engine facts (Factorio 2.1.21-2.1.23), verified in this project

Each line: the fact, then how it was verified and when.

## Animation and sound
- Crafting machines play `animation_speed × crafting_speed × animation_progress`;
  `animation_progress` defaults to 0.5. Mining drills use 1. (Measured
  in a client, 2026-10-09.)
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

## Neighbour bonus
- `neighbour_bonus` exists only on `reactor` entities, which output heat,
  not electricity. Not yet spiked with a custom fuel category.

## Map generation
- Tiles repeat per tile; a sheet cannot carry a depth gradient across a
  pool. Depth needs a second tile placed by map-gen. (2026-10-14.)
- Without Alien Biomes, the Core's ground falls back to Vulcanus's
  volcanic tiles, whose expressions step in straight lines on the Core.
  (2026-10-12.)
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
  ms/tick. (V↔F T02 (a).)
- Fulgora's lightning falls only at night: its daytime multiplier is 0. A
  collector in a storm took about one strike every 14 s. (V↔F T02 (a).)
- An asteroid collector's catch area is a square, half-side
  `collection_radius`, centred `collection_box_offset` tiles ahead (5 in
  vanilla). No prototype field limits which chunks it takes. Filters are a
  runtime whitelist: `filter_slot_count` is 0 on a fresh collector and grows as
  filters are set, `get_filter` returns the prototype, not its name, and
  circuit 'set filters' overwrites them with no event. Turning that circuit
  mode off clears them. (V↔F T02 (c).)
- Asteroid chunks stack to 1. (V↔F T02 (c).)
- An entity with no item that places it can't have a ghost. (V↔F T02 (c).)
- A collector's catch area grows by `QualityPrototype.asteroid_collector_collection_radius_bonus` per quality (by default the quality level: +1 for uncommon … +5 for legendary). A fast chunk can't be caught by an arm at rest, but an arm already out chasing slower chunks can catch it, so chunk speed tilts which collector catches what, but can't lock any out. (V↔F T02e, 2026-10-31.)

## Recipes
- `allow_productivity = false` keeps productivity modules out but doesn't stop a machine's built-in productivity (the foundry's +50 %). To give a recipe none at all, also set `maximum_productivity = 0`. (V↔F T05a, measured in a client, 2026-10-31.)
- A recipe's surface conditions are checked when a player picks it (or a blueprint is built), not while the machine crafts. A recipe set by script crafts off its planet. Vanilla's lightning collector and foundry recipes behave the same. The 2.1.24 runtime docs word it as 'required to craft'. (V↔F T07a, 2026-10-31.)

## Fluids
- A fluid's `max_temperature` defaults to its `default_temperature`, so
  vanilla sulfuric acid (25°, no max) can't be heated without raising it. A
  recipe can require a temperature (`minimum_temperature` on a fluid
  ingredient) and set one (`temperature` on a fluid product). Vanilla's
  generated empty-barrel recipe sets no temperature, so a barrelled fluid comes
  back at its default. (V↔F T01 research, base/prototypes/fluid.lua and
  base/data-updates.lua, 2026-10-30.)

## Running a client on this machine
- `xvfb-run` alone leaves WAYLAND_DISPLAY set: the client opens
  full-screen on Liam's desktop. Use
  `env -u WAYLAND_DISPLAY SDL_VIDEO_DRIVER=x11 xvfb-run -a`.
- PULSE_SINK alone does not stop audio reaching the speakers; use
  `--disable-audio`, or a null sink set as the default sink.
- One client at a time; a second client's Steam connect can reach the
  first.
- The data-stage check never opens an image; sprite errors need a real
  client load to `Sprites loaded`.
