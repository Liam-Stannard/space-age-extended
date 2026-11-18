---
name: factorio-brief
description: Write the prompt for an artist, coder, code-reviewer, factorio-gameplay-expert, questions-clerk, tester, analyst, docs-moderator or project-manager agent working on this mod, from one ticket of a task file - what the ticket is, where the agent works and from which base commit, and what it must leave alone. Use before launching or resuming any agent.
argument-hint: <task file> <ticket T<nn>>
---

Write the brief for one ticket of a task (`.claude/tasks/<name>.md`,
ticket `T<nn>`), for the ticket's owner. One brief, one ticket: never
brief an agent with a whole task. Return the brief, launch the agent
with it as `.claude/agents/project-manager.md` (The limit) says, and set
the ticket's Status to "in progress". When the ticket is done its
sign-off owner checks it; only then is it "signed off". Which tickets
may be briefed while others run: see factorio-task §4.

## 1. What the brief names
- The task file's absolute path and the ticket, quoted whole (header,
  Do, Output, Acceptance, Sign-off).
- The worktree, by absolute path, and its branch.
- The base commit: the commit the ticket started from.
- Where the role may write (a folder, never "anywhere") and what it
  must not touch.
- What to read first: the building's spec, the previous round's folder,
  and the finish reference `.claude/skills/factorio-task/knowledge/standards.md`
  (Finish) names.
- What the standing rules (Waiting and processes) say the brief names,
  and whether a render slot is free.
- For a project-manager: the attribution lines its commits end with.
- For a factorio-gameplay-expert: the mod's shared dump by path and
  sha256, if there is one; the decisions of Liam's the change rests on;
  and the vanilla buildings or items it is meant to sit beside.
- For the questions-clerk: no ticket of its own. Name the job, and what
  `.claude/agents/questions-clerk.md` says that job is given.

## 2. The standing rules
The brief does not restate the standing rules. How a brief may narrow
them is in their opening.

## 3. What the report must contain
As the standing rules' The report says.

## 4. Resuming
Resume an agent only to fix its own ticket after a review; brief every
new ticket to a fresh agent. To continue one, `SendMessage` it with
what changed since it stopped (commits made, files moved, scratch
emptied), what to do now, and the base commit, unchanged.
