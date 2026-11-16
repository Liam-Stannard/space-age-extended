---
name: factorio-standing-rules
description: The rules every agent working on this mod keeps, whatever its role - writing, committing, scratch, waiting, processes, game clients, Blender, asking, and the report Liam reads. Preloaded into every agent; read it before any work on a ticket.
---

These rules hold for every ticket and every role. A brief or ticket may
narrow them, never loosen them. The hook
(`.claude/hooks/no-ghost-waits.py`) enforces the ones marked (hook).

## Writing
- Write only where your brief says: a folder, never "anywhere".
- No `.md` file is changed except as `DOCUMENTATION-LANGUAGE.md` §8 says; put the proposed wording in your report. The project-manager may write
  its task file's Status lines, a working note `DOCUMENTATION-LANGUAGE.md` §8.1 allows. Only the
  questions-clerk writes `.claude/tasks/QUESTIONS.md`, the other one,
  with its locked commands.
- What may go in `graphics/`: claude.md rule 2.
- No migrations before 1.0 (Liam).
- Sound: vanilla references plus scripted files only.

## Git
- Workers (artist, coder, code-reviewer, tester) never commit, merge,
  push, stash or switch branch.
- The project-manager, or the orchestrator, makes a work-in-progress
  commit when a ticket is done, on the task's branch.
- Commit, merge and push: see factorio-ship.

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
  directory; one Factorio at a time (see factorio-client-test).
- `tools/check-data-stage.sh` exiting 3 means the lock was held: the
  data stage was not checked, which is NOT RUN, not FAIL.

## Judging and asking
- Nothing is PASS that was not run and seen to pass. Never sign off
  art or sound: Liam judges the look.
- Never settle an unknown with a default. Anything the ticket, the task
  file and the files do not settle is a question, asked as **Asking
  Liam** says. A subagent, or anyone while Liam is away, has the
  questions-clerk add it to `.claude/tasks/QUESTIONS.md`, naming the
  ticket it pauses, takes the Q<n> the clerk returns, pauses that ticket
  and moves to the next. The clerk records Liam's answers there, in his
  own words.
- When Liam's own sources disagree, the more specific one wins: his
  decision on the subject, then the subject's own tree or building
  spec, then the general design docs (`design/01-principles.md`). At the same level, the newer one wins.
  Report the line that loses as `DOCUMENTATION-LANGUAGE.md` §4 says, not as a FAIL. On what
  the game does, the mod's dump and the knowledge base win over any
  text.
- **Asking Liam.** Word each question as `DOCUMENTATION-LANGUAGE.md` §3 says. In the main session with Liam present,
  ask with AskUserQuestion; a subagent, or anyone while Liam is away,
  sends it to the questions-clerk.

## The report
- Word the report as `DOCUMENTATION-LANGUAGE.md` §2 and §6 say.
- Art: a crops sheet at 2x of every cable, hose and pipe run's ends and
  anything that crosses another part, with each clip found and fixed.
- What is left running (nothing should be), and anything left for
  Liam.
