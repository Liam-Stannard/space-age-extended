---
name: factorio-task
description: Turn a request for this mod into a task file in .claude/tasks/ that can be implemented without guessing. Researches the topic from the mod, vanilla and the knowledge base first, separates verified facts from assumptions, and questions Liam until every ambiguity is resolved; only then writes the file. Use whenever new work needs a task file, or an amendment to one.
argument-hint: <the request, in Liam's words>
---

Request: $ARGUMENTS

The task file is the contract the agents work to. An agent that meets an
ambiguity guesses; every guess this project has paid for (a weak join
test, a square deck, a frame-0 sound, wording nobody agreed) started as
an unasked question. So this skill does not write the file until nothing
in it is a guess.

## 1. Research before asking
Never ask Liam what the files can answer. Read, in this order, and note
each fact with its source (file and line, or measured):
1. `knowledge/` beside this file: engine facts, the pipeline, the art
   standards and the process, each already verified.
2. `claude.md`, `TODO.md`, and the parts of `design/` the request touches.
3. The building or system's own files: `concept/<building>/` (spec,
   sheets, the latest round's report in the task file), the prototype in
   `prototypes/`, its graphics in `graphics/`.
4. Earlier task files in `.claude/tasks/` on the same subject: what was
   decided, by whom, in which amendment.
5. Vanilla's data (`/home/liam-stannard/.steam/steam/steamapps/common/Factorio/data`)
   and the local docs (`doc-html/`) for any engine behaviour the task
   relies on. If the docs do not settle it, it becomes a spike criterion,
   never an assumption.

## 2. The ledger
Build, in the reply, a ledger of everything the task depends on:
- **Verified:** fact, source.
- **Decided by Liam:** decision, his words, date.
- **Unknown:** what is not known and why it matters to the task.
- **Assumed:** must be empty before the file is written.

## 3. Question until it is unambiguous
Check every section of the task against this list; each gap is a
question, asked with AskUserQuestion (at most four at a time, the
recommended option first, each option saying what it changes):
- **Outcome:** what is true when it is done, that a tester can check?
- **Scope:** which files may change; which must not; what is deferred?
- **Look** (art tasks): references to measure against, the bars
  (coverage, rise, light, finish), what may glow, what moves and why.
- **Gameplay:** footprint, ports and their faces, rotation, recipes,
  numbers. Which are fixed, which open?
- **Engine:** every engine behaviour relied on is in the ledger as
  verified, or a spike criterion.
- **Gates:** where the work stops for Liam (pick, sign-off, wording).
- **Pass criteria:** each names the check and the result that passes,
  strong enough to catch the failure it exists for (a join test that
  checks the full pipe width, not the centreline).
- **Words:** any `.md`, spec or TODO wording is proposed, never written.
- **Conflicts:** anything in the request that contradicts a spec, a rule
  or an earlier decision is put to Liam, quoting both.
Ask again after each answer until the list has no gaps. Do not fill a gap
with a default unless Liam says to use the default.

## 4. Split into tickets
A task is delivered as tickets. A ticket is one clear piece of work that
one agent can finish in one run and that can be signed off on its own.
Split until each ticket passes these tests:
- one role does it (artist, coder, tester, or Liam for a decision);
- its inputs exist before it starts (earlier tickets, named files);
- its output is named: files and paths, or a decision recorded;
- every acceptance criterion is checkable by someone other than its
  author, with the check and the passing result stated;
- it says who signs it off: the code-reviewer, the tester, or Liam.
Typical split for a building: research or study → options → Liam picks →
refine → spec wording → Liam agrees → model → Liam signs off → wiring →
test → Liam signs off in game → ship. Decisions are tickets owned by
Liam, so the gates are visible.

Each ticket, in the task file's **Tickets** section:

    ### T<nn>: <one line>
    Owner: artist | coder | code-reviewer | tester | Liam
    Depends on: T<nn>, ... | none
    Status: open | in progress | done | signed off | blocked (<why>)
    Inputs: <files, decisions, earlier tickets' outputs>
    Do: <what to do, in a few lines; what not to do>
    Output: <exact files and paths, or the decision to record>
    Acceptance criteria:
      1. <check> -> <passing result>
    Sign-off: <who>, on <what evidence>
    Out of scope: <deferred to which ticket>

Tickets with no dependency on each other may run at once, at most three
agents at a time. Each finished ticket ends with a work-in-progress
commit on the branch, so a usage limit or a reboot never loses it, and
its Status is updated in the file.

## 5. Draft, agree, write
Draft the file in the reply, in the `pm` skill's shape (Goal, Scope, Out
of scope, Art, Pass criteria), with a **Decisions** section quoting
Liam's answers and a **Sources** section listing the ledger's verified
facts. When Liam agrees, write it to `.claude/tasks/<branch>.md` (or the
amendment at the end of the existing file), create the branch and
worktree from master, and hand over to `factorio-brief`.

## 6. Keep the knowledge base true
When the work proves or disproves an engine fact, a pipeline limit or a
standard, propose the line to add to or change in `knowledge/` (rule 8:
wording agreed first). Each entry carries its source and date.
