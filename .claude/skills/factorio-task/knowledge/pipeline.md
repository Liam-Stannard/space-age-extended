# The pipeline, as it is

- **Repo:** master is checked out in `.claude/worktrees/master-merge`;
  `~/.factorio/mods/space-age-extended` links to it. Each task's branch
  (claude.md rule 6) has its worktree under `.claude/worktrees/`.
  (2026-11-16.)
- **Blender:** blender.org 5.0.1 (`tools/paths.conf`, 2026-11-18). Which build
  to use, rendering on the GPU through `render.sh`, and `render.done`: see the
  standing rules (factorio-standing-rules, "Blender" and "Waiting and
  processes"). `SAE_BLENDER_DEVICE` chooses GPU or CPU, and unset means GPU; a
  GPU render uses Cycles on OptiX, or CUDA if Blender finds no OptiX device
  (`tools/blender/render.sh`, its notes; 2026-11-18). The card is an RTX 5080
  (`nvidia-smi -L`, 2026-11-18).
- **Packing:** `tools/blender/pack.py` crops per declared layer, checks
  centre offset, edge alpha, half width, glow white pixels, frame 0 against
  the still, motion paths; refuses an empty layer. Contract flags: cycle,
  working, flow, light, turns. Animated glows (kind "glow"),
  `frame_sequence` or `hold` in render.json, the footprint cut and
  `--collide` in render.sh are all in. Slides are measured from frame 0;
  still glows are cropped to 99.9 % of their light; highlights are rolled off
  above 236, to meet the "No white" bar in `standards.md` (`rolloff: false`
  opts out); ports are checked for every face they reach (`ports_turn`).
  (2026-10-20.)
- **Same render:** two renders of one model are the same render when
  `tools/blender/same_render.py <out-a> <out-b>` passes: compared in
  premultiplied colour, every pixel within 3 levels, under 2 % of a
  sheet's visible pixels differing, alpha flips only where the colour is
  3 or less, meta.json equal but for the light stats (core/halo 0.1,
  peak 1) and the roll-off counts (within 1 % of the larger, or 1). It is
  per device: a GPU and a CPU render of one model fail it.
  `tools/blender/test/test_repeatable.py` renders the box and radiant box
  twice on the GPU and holds them to it. (2026-11-15.)
- **Icons:** `tools/blender/icon_rig.py`, `icon_post.py`,
  `render-icons.sh`, `tools/key-icons.py --mips`; technology icons
  `tech_rig.py`, 480×256 strips. (2026-10-14.)
- **Audio:** `tools/audio/` (sfx.py, loudness.py, review.py), venv at
  `tools/audio/.venv` (git-ignored); `derive.working_sound` in
  `prototypes/derive.lua`. (2026-10-14.)
- **Data stage:** `tools/check-data-stage.sh` (data, graphics, layout,
  dumped graphics, recipes, tech reachability). It takes launch.sh's lock.
  (2026-11-11.)
  **Lint:** `luacheck .` (1.2.0 on Lua 5.4, in ~/.luarocks/bin, which
  `env.PATH` in `.claude/settings.json` puts on every session's PATH,
  2026-11-13); CI runs the same .luacheckrc.
- **Gameplay:** `tools/gameplay/graph.py <dump>` (raw cost, research, loops,
  weight, compare); `tools/check-data-stage.sh --keep-dump <path>` keeps the
  mod's dump (2026-11-13). Its weights matched the engine's on every vanilla
  item, and on every item of the mod as it was on 2026-11-13 (the
  factorio-gameplay-expert task's T04: c6-compare-r2.out in the main
  checkout's `evidence/factorio-gameplay-expert/T04/`).
- **Game knowledge base:** `tools/build-knowledge-base.sh` builds
  `knowledge-base/<version>/` in the main checkout (git-ignored): the runtime
  and prototype API JSON, the `--dump-data` prototype dump and the six game
  mods' prototype Lua, with a MANIFEST of sums.
  `tools/client/launch.sh --version` prints the installed version.
  (2026-11-11.)
- **Agents:** their files are in `.claude/agents/`, each preloading the
  `factorio-standing-rules` skill. The `no-ghost-waits` hook blocks sleep
  loops, deletes above a scratch ticket folder, `pkill`, `killall` and killing
  by name, and running Factorio outside `tools/client/launch.sh`.
  (2026-11-16.)
- **Questions:** who writes `.claude/tasks/QUESTIONS.md` is in the standing
  rules; how, with its commands and its lock, is in
  `.claude/agents/questions-clerk.md`.
- **Sending files:** the image size limit is in `DOCUMENTATION-LANGUAGE.md`
  §2.3.
