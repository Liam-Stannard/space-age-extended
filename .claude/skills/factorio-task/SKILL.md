---
name: factorio-task
description: Turn a request for this mod into a task file in .claude/tasks/ that can be implemented without guessing. Researches the topic from the mod, vanilla and the knowledge base first (or has the analyst do it), separates verified facts from assumptions, and questions Liam until every ambiguity is resolved; only then writes the file. Run by the project-manager or the main session. Use whenever new work needs a task file, or an amendment to one.
argument-hint: <the request, in Liam's words>
---

Request: $ARGUMENTS

The task file is the contract the agents work to. An agent that meets an
ambiguity guesses; every guess this project has paid for (a weak join
test, a square deck, a frame-0 sound, wording nobody agreed) started as
an unasked question. So this skill does not write the file until nothing
in it is a guess.

## 0. Which path, and who asks
- **Full path:** anything with art, a gameplay change, an engine
  behaviour relied on, or more than one ticket: §1-§6.
- **Light path:** one coder ticket, no art, no gameplay change (a tool
  fix, a check, a message). Skip the ledger and §3's list: draft Goal,
  Scope, Pass criteria and the one ticket, ask what they leave open,
  then §5.
- **Who asks:** the main session asks with AskUserQuestion. The
  project-manager cannot: it puts each question in
  `.claude/tasks/QUESTIONS.md` and returns the draft in its report.
  Nothing is written until Liam's agreement comes back, quoted.

## 1. Research before asking
Never ask Liam what the files can answer. The analyst agent may do this
research: brief it with the request and what must be settled; it returns
facts with sources and the unknowns, no opinions. Read, in this order,
and note each fact with its source (file and line, or measured):
1. `knowledge/` beside this file: engine facts, the pipeline and the art
   standards, each already verified.
2. `claude.md`, `TODO.md`, and the parts of `design/` the request touches.
3. The building or system's own files: `concept/<building>/` (spec,
   sheets, the latest round's report in the task file), the prototype in
   `prototypes/`, its graphics in `graphics/`.
4. Earlier task files in `.claude/tasks/` on the same subject: what was
   decided, by whom, in which amendment.
5. Vanilla's data (`<FACTORIO_ROOT>/data`, the root `tools/paths.conf` names)
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
question (at most four at a time, the recommended option first, each
option saying what it changes):
- **Outcome:** what is true when it is done, that a tester can check?
- **Scope:** which files may change; which must not; what is deferred?
- **Look** (art tasks): the references to measure against and which of
  standards.md's bars apply; what may glow, what moves and why.
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
A ticket is one piece of work one agent finishes in one run and that
can be signed off on its own. Split until each ticket has one owner,
inputs that exist before it starts, a named output, acceptance criteria
someone other than its author can check, and a sign-off owner.
Typical split for a building: study → options → Liam picks → refine →
spec wording → Liam agrees → model → Liam signs off → wiring → test →
Liam signs off in game → ship. Decisions are tickets owned by Liam, so
the gates are visible.

    ### T<nn>: <one line>
    <owner> · <depends on: T<nn>, ... | none> · <status>
    Do: <what to do, in a few lines; what not to do>
    Output: <exact files and paths, or the decision to record>
    Acceptance: 1. <check> -> <passing result>
    Sign-off: <who>, on <what evidence>

Owner: artist, coder, code-reviewer, tester, analyst, orchestrator or
Liam. Status: open, in progress, done, signed off, blocked (<why>), or
waiting on Liam: Q<n>. Tickets with no dependency on each other may run
at once, within the standing rules' limits. Each signed-off ticket ends
with a work-in-progress commit on the branch, and its Status is updated
in the file.

## 5. Draft, agree, write
Draft the file in the reply (or, run by the project-manager, in its
report), in this shape:

    # Task: <one line>
    Branch: <lowercase-with-hyphens, named for the work>

    ## Goal
    What is true when this is done, in two or three sentences.
    ## Scope
    The files and areas that may change.
    ## Out of scope
    What must be left alone, and what is deferred.
    ## Art
    `none`, or which entity needs art; the coder wires
    `derive.placeholder_art` so the task passes without it; whether the
    building's spec in `concept/<building>/` is agreed.
    ## Decisions
    Liam's answers, quoted and dated.
    ## Sources
    The ledger's verified facts.
    ## Pass criteria
    Numbered, each the check and the result that passes. Every task
    carries: `luacheck .` reports nothing; `tools/check-data-stage.sh`
    passes; if anything under `graphics/` or any sprite or animation
    definition changed, the client loads to `Sprites loaded` with no
    error. Behaviour is a check over RCON with the expected answer, or
    an explicit "needs a client".
    ## Tickets

The light path's file is Goal, Scope, Pass criteria and its ticket.
When Liam agrees, write it to `.claude/tasks/<branch>.md` (or the
amendment at the end of the existing file) and create the branch and
worktree from master. Run by the project-manager, go on to the tickets.
In the main session, launch the project-manager in the background on
the agreed file.

## 6. Keep the knowledge base true
When the work proves or disproves an engine fact, a pipeline limit or a
standard, propose the line to add to or change in `knowledge/` (rule 8:
wording agreed first); the analyst may draft it. Each entry carries its
source and date.
