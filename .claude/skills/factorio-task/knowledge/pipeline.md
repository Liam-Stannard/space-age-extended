# The pipeline, as it is (2026-10-14)

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
  working, flow, light, turns. Not yet: an animated glow kind (being added
  on `radiant-look`), `frame_sequence` in render.json, a footprint cut,
  `--collide` in render.sh (each model carries its own).
- **Icons:** `tools/blender/icon_rig.py`, `icon_post.py`,
  `render-icons.sh`, `tools/key-icons.py --mips`; technology icons
  `tech_rig.py`, 480×256 strips.
- **Audio:** `tools/audio/` (sfx.py, loudness.py, review.py), venv at
  `tools/audio/.venv` (git-ignored); `derive.working_sound` in
  `prototypes/derive.lua`.
- **Data stage:** `tools/check-data-stage.sh` (data, graphics, layout,
  dumped graphics, recipes, tech reachability). luacheck is not installed
  locally; CI runs it.
- **Agents:** artist, coder, code-reviewer, tester, project-manager
  (`.claude/agents/`); the `no-ghost-waits` hook blocks unbounded or
  duplicate waits and deletes of scratch roots.
- **Sending files:** images over 8000 px on the longer side cannot be sent
  to Liam; send a top-section copy.
