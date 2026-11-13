---
name: factorio-brief
description: Write the prompt for an artist, coder, code-reviewer, factorio-gameplay-expert, tester, analyst or project-manager agent working on this mod, from one ticket of a task file - what the ticket is, where the agent works and from which base commit, and what it must leave alone. The standing rules come from the factorio-standing-rules skill every agent preloads. Use before launching or resuming any agent.
argument-hint: <task file> <ticket T<nn>>
---

Write the brief for one ticket of a task (`.claude/tasks/<name>.md`,
ticket `T<nn>`), for the ticket's owner. One brief, one ticket: never
brief an agent with a whole task. Return the brief, launch the agent
with it, add its line to `.claude/tasks/RUNNING`, and set the ticket's
Status to "in progress". When the ticket is done its sign-off owner
checks it; only then is it "signed off" and the next ticket briefed.

## 1. What the brief names
- The task file's absolute path and the ticket, quoted whole (header,
  Do, Output, Acceptance, Sign-off).
- The worktree and branch, as absolute paths
  (`/home/lstan/data/git/space-age-extended/.claude/worktrees/<branch>`).
- The base commit: the commit the ticket started from. A resumed
  ticket keeps that base after its own work-in-progress commits, so a
  review from it still covers all of the ticket's work.
- Where the role may write (a folder, never "anywhere") and what it
  must not touch.
- What to read first: the building's spec, the previous round's folder,
  the latest signed-off model as the finish standard.
- The other agents running (from `RUNNING`) and their worktrees, and
  whether a render slot is free.
- For a project-manager: the attribution lines its commits end with.
- For a factorio-gameplay-expert: the dumps to measure (the knowledge
  base's, and where to keep the mod's), the decisions of Liam's the
  change rests on, and the vanilla buildings or items it is meant to sit
  beside.

## 2. The standing rules
Every agent preloads factorio-standing-rules; the brief does not
restate it. The brief adds only what this ticket narrows (one folder,
no client, no render while two run).

## 3. What the report must contain
What the standing rules ask, answered in the ticket's own numbering;
on a re-run, each earlier finding marked resolved or not.

## 4. Resuming
Resume an agent only to fix its own ticket after a review; brief every
new ticket to a fresh agent. To continue one, `SendMessage` it with
what changed since it stopped (commits made, files moved, scratch
emptied), what to do now, and the base commit, unchanged.
