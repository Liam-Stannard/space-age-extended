# The pipeline, as it is (2026-10-20)

- **Repo:** master is checked out in `.claude/worktrees/master-merge`;
  `~/.factorio/mods/space-age-extended` links to it. Every task has its own
  branch and worktree under `.claude/worktrees/`; nothing is committed on
  master directly (claude.md rule 7).
- **Blender:** blender.org 5.0.1 at
  `/home/liam-stannard/opt/blender-5.0.1-linux-x64/blender`, GPU (OptiX,
  RTX 5080) by default via `SAE_BLENDER_DEVICE`; `/usr/bin/blender` has no
  GPU. `tools/blender/render.sh` writes `<out>/render.done`.
- **Packing:** `tools/blender/pack.py` crops per declared layer, checks
  centre offset, edge alpha, half width, glow white pixels, frame 0 against
  the still, motion paths; refuses an empty layer. Contract flags: cycle,
  working, flow, light, turns. Animated glows (kind "glow"),
  `frame_sequence` or `hold` in render.json, the footprint cut and
  `--collide` in render.sh are all in. Slides are measured from frame 0;
  still glows are cropped to 99.9 % of their light; highlights are rolled
  off above 236 to under 245, never on light passes (`rolloff: false` opts
  out); ports are checked for every face they reach (`ports_turn`).
- **Same render:** two renders of one model are the same render when
  `tools/blender/same_render.py <out-a> <out-b>` passes: compared in
  premultiplied colour, every pixel within 3 levels, under 2 % of a
  sheet's visible pixels differing, alpha flips only where the colour is
  3 or less, meta.json equal but for the light stats (core/halo 0.1,
  peak 1) and the roll-off counts (within 1 % of the larger, or 1). It is
  per device: a GPU and a CPU render of one model fail it.
  `test/test_repeatable.py` renders the box and radiant box twice on the
  GPU and holds them to it.
- **Icons:** `tools/blender/icon_rig.py`, `icon_post.py`,
  `render-icons.sh`, `tools/key-icons.py --mips`; technology icons
  `tech_rig.py`, 480×256 strips.
- **Audio:** `tools/audio/` (sfx.py, loudness.py, review.py), venv at
  `tools/audio/.venv` (git-ignored); `derive.working_sound` in
  `prototypes/derive.lua`.
- **Data stage:** `tools/check-data-stage.sh` (data, graphics, layout,
  dumped graphics, recipes, tech reachability). luacheck is not installed
  locally; CI runs it. It takes launch.sh's lock.
- **Agents:** artist, coder, code-reviewer, tester, project-manager
  (`.claude/agents/`); the `no-ghost-waits` hook blocks unbounded or
  duplicate waits and deletes of scratch roots.
- **Sending files:** images over 8000 px on the longer side cannot be sent
  to Liam; send a top-section copy.
