---
name: factorio-brief
description: Write the prompt for an artist, coder, code-reviewer, tester or project-manager agent working on this mod, from a task file. Adds the standing rules every agent needs (Blender on the GPU, bounded waits, scratch, processes, safe game clients, no commit) so a brief never forgets them. Use before launching or resuming any agent.
argument-hint: <task file> <ticket T<nn>>
---

Write the brief for one ticket of a task (`.claude/tasks/<name>.md`,
ticket `T<nn>`), for the ticket's owner role. One brief, one ticket: never
brief an agent with a whole task. Return the brief text, then launch the
agent with it, and set the ticket's Status to "in progress".

The brief quotes the ticket whole (Inputs, Do, Output, Acceptance
criteria, Sign-off, Out of scope) and the agent's report answers it
criterion by criterion. When the ticket is done, its sign-off owner
checks it: the code-reviewer or tester agent, or Liam; only then is the
Status "signed off" and the next ticket briefed.

## 1. What the brief names
- The task file's absolute path and the section to run, quoted by title.
- The worktree and branch, as absolute paths
  (`/home/liam-stannard/git/space-age-extended/.claude/worktrees/<branch>`).
- Where the role may write (a folder, never "anywhere"), and what it must
  not touch: the spec, `graphics/`, `prototypes/`, `tools/`, `design/` and
  any `.md` file unless the task gives it.
- What to read first: the building's spec, the previous round's folder,
  and the current finish standard (the latest signed-off model).
- Other agents working at the same time, and their worktrees, so it
  leaves them alone.

## 2. The standing rules, in every brief
- **No commit.** The orchestrator commits, on Liam's word.
- **Blender:** blender.org's build at
  `/home/liam-stannard/opt/blender-5.0.1-linux-x64/blender`, on the GPU;
  wait on `render.done` with one bounded wait per job, never a polling
  loop and never two waits on one job.
- **Game clients** (any role that launches Factorio): one client at a time
  on this machine (check `pgrep -af factorio` first, wait bounded if one
  runs); every launch is
  `env -u WAYLAND_DISPLAY SDL_VIDEO_DRIVER=x11 xvfb-run -a ... --disable-audio`
  unless the test is about sound (then a verified null sink as the default
  sink before launch, restored after).
- **Scratch:** its own subfolder of the session scratchpad,
  `.../scratchpad/<role>/<task>/`; never delete outside it; evidence the
  report names is kept, the rest deleted at the end.
- **Processes:** stop everything it started by PID; never `pkill` by
  pattern.
- **Art:** never signs off; Liam judges.

## 3. What the report must contain
For each pass criterion: PASS, FAIL or NOT RUN, with the evidence path.
The absolute path of every image, GIF and sheet Liam should see (each
under 8000 px on its longer side, or a top-section copy that is). Any
wording for a `.md` file, spec or TODO entry as a proposal only. For art:
a crops sheet of every cable, hose and pipe run's ends and of anything that
crosses another part, at 2x, with each clip found and fixed listed. Anything
left for Liam.

## 4. Resuming
Resume an agent only to fix its own ticket after a review; brief every new
ticket to a fresh agent, since the task file and the brief carry what it
needs.

To continue an agent, `SendMessage` it with: what changed since it
stopped (commits made, files moved, scratch emptied), what to do now, and
the same standing rules.
