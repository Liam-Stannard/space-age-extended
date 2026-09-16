---
name: pm
description: Run a piece of work through the team. Drafts a task specification with pass criteria, gets it agreed, writes it, branches, then hands it to the project-manager agent, who drives coder, code-reviewer, artist and tester and reports back.
disable-model-invocation: true
argument-hint: [task, or a TODO.md entry to quote]
model: fable
---

You are running the task below through the team. Nothing here overrides
`claude.md`: no `.md` file is written, and nothing goes into `TODO.md` or
`design/`, without Liam agreeing the wording first.

Task: $ARGUMENTS

## 1. Draft the specification, in the reply

Read `TODO.md`, the parts of `design/` the task touches, and the code it will
change. Then propose, in the reply and nowhere else:

- a branch name, lowercase with hyphens, named for the work (claude.md rule 7)
- the specification, in exactly this shape:

    # Task: <one line>
    Branch: <name>

    ## Goal
    What is true when this is done, in two or three sentences.

    ## Scope
    The files and areas the coder may change.

    ## Out of scope
    What the coder must leave alone, and what is deliberately deferred.

    ## Art
    `none`, or: which entity needs art, and that the coder wires
    `derive.placeholder_art` for it so the task passes without the art.
    If the building's spec in `concept/<building>/` is already agreed, say
    so, and the artist may generate against it; otherwise the artist only
    proposes the spec, and generation waits for agreement.

    ## Pass criteria
    Numbered. Each one names the check the tester runs and the result that
    counts as passing. Every task carries at least:
    1. `luacheck .` reports nothing (if luacheck is not installed locally,
       the tester reports NOT RUN and CI decides).
    2. `tools/check-data-stage.sh` passes.
    3. If any file under `graphics/` or any sprite or animation definition
       changed: the client loads to `Sprites loaded` with no error.
    Then the behavioural criteria specific to this task, each stated as
    something a headless server can be asked over RCON, with the expected
    answer, or an explicit "needs a client" that the tester will report as
    NOT RUN.

Stop there and wait. Do not write the file, do not create the branch.

## 2. Once Liam agrees

- Confirm the working tree is clean and on `master`; if not, say so and stop.
- `git switch -c <branch>`.
- Write the agreed spec to `.claude/tasks/<branch>.md` exactly as agreed.
- Launch the `project-manager` agent in the background with the prompt:
  "Run the task specified in `.claude/tasks/<branch>.md`."
- Tell Liam it is running.

## 3. When the project manager reports

Relay the report as it stands: the commit on the feature branch, each pass
criterion with its result, the files changed, anything unresolved, and any
art produced or still needed. If the report proposes `TODO.md` wording,
present it as a proposal. If the project manager stopped with a question,
put the question to Liam and, once answered, resume the same agent with
`SendMessage` so it keeps its context. Then wait: merging is Liam's
decision.

## 4. Once Liam confirms the merge

Resume the same project-manager agent with `SendMessage`: "Liam has
confirmed: merge <branch> into master." It merges, deletes the branch and
reports the merge commit; relay that. If Liam asks for changes instead,
resume the same agent with them and go back to step 3.
