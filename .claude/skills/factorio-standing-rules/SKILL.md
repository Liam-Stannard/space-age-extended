---
name: factorio-standing-rules
description: The rules every agent working on this mod keeps, whatever its role - writing, committing, scratch, waiting, processes, game clients, Blender, asking, and the report Liam reads. Preloaded into every agent; read it before any work on a ticket.
---

These rules hold for every ticket and every role. A brief or ticket may
narrow them, never loosen them. The hook
(`.claude/hooks/no-ghost-waits.py`) enforces the ones marked (hook).

## Writing
- Write only where your brief says: a folder, never "anywhere".
- No `.md` file, `design/`, `templates/` or `TODO.md` is written, added
  to or reworded without Liam's agreement first (claude.md rule 8); put
  the proposed wording in your report. The project-manager may write
  the working notes rule 8 allows: its task file's Status lines and
  QUESTIONS.md.
- Only signed-off or placeholder art goes in `graphics/`; nothing in
  `concept/` ships (claude.md rule 3).
- No migrations before 1.0 (Liam).
- Sound: vanilla references plus scripted files only.

## Git
- Workers (artist, coder, code-reviewer, tester) never commit, merge,
  push, stash or switch branch.
- The project-manager, or the orchestrator, makes a work-in-progress
  commit when a ticket is done, on the task's branch.
- Merge only on Liam's own words naming the branch, relayed verbatim;
  push only when Liam says push. Commit, merge and push are three
  separate permissions (factorio-ship).

## Scratch
- Yours is `<session scratchpad>/<role>/<ticket>/`, e.g.
  `.../scratchpad/coder/agent-setup-T04/`. Delete only inside it
  (hook). Evidence your report names is kept; the rest goes when you
  finish.
- Evidence Liam or a tester must keep goes to
  `<worktree>/evidence/<task>/` (git-ignored).

## Waiting and processes
- No polling loops: no `while` or `until` with `sleep` (hook). Start a
  long job (a render, a client, a server) with the Bash tool's
  `run_in_background`; you are told when it exits. To wait on a job
  you did not start: `timeout <seconds> tail --pid=<pid> -f /dev/null`,
  at most 3600 s. `tools/blender/render.sh` writes
  `<out-dir>/render.done` when it ends.
- Stop every process you started, by PID, before you report. Never
  `pkill` or `killall` (hook).
- At most eight worker agents run on this machine at once; a
  project-manager does not count. At most two Blender renders run at
  any time, whoever starts them, since rendering is CPU-heavy (Liam,
  2026-11-11: "increase limit of agents to 8 but only 2 artists";
  "Two renders at once"). The shared roster,
  `.claude/tasks/RUNNING`, counts both. Your brief names the others and
  their worktrees: leave them alone.

## Blender
- blender.org's build, the one `tools/paths.conf` names (BLENDER), on
  the GPU, through `tools/blender/render.sh`.
- Prove a change on one take before rendering the rest.

## Game clients
- Every Factorio client goes through `tools/client/launch.sh`, via
  factorio-client-test (hook): no Wayland, a private Xvfb,
  `--disable-audio` unless the test is about sound, a scratch mod
  directory. One Factorio runs at a time; the launcher's lock refuses a
  second.
- `tools/check-data-stage.sh` exiting 3 means the lock was held: the
  data stage was not checked, which is NOT RUN, not FAIL.

## Judging and asking
- Nothing is PASS that was not run and seen to pass. Never sign off
  art or sound: Liam judges the look.
- Never settle an unknown with a default. Anything the ticket, the task
  file and the files do not settle is a question: options, what each
  changes, a recommendation first. In the main session with Liam
  present, ask with AskUserQuestion (at most four at once); a subagent,
  or anyone while Liam is away, puts it in
  `.claude/tasks/QUESTIONS.md` as Q<n> naming the ticket it pauses,
  pauses that ticket and moves to the next.
- Any image a question refers to is sent with it, first.

## The report
- Each acceptance criterion: PASS, FAIL or NOT RUN, with the command
  and the evidence.
- Absolute paths only, for every file named.
- Liam reviews on his phone: every image, GIF and sheet he should see
  is named by absolute path beside the question or finding it belongs
  to, each under 8000 px on its longer side (or a top-section copy
  that is).
- Art: a crops sheet at 2x of every cable, hose and pipe run's ends and
  anything that crosses another part, with each clip found and fixed.
- Proposed wording for any `.md` file, spec or TODO entry, marked as a
  proposal.
- What is left running (nothing should be), and anything left for
  Liam.
