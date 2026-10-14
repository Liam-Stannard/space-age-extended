# Engine facts (Factorio 2.1.21), verified in this project

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
- Accent frames count from 0 on the animation they name. Whether they
  count `frame_sequence` entries or sprite frames is not yet verified.
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
