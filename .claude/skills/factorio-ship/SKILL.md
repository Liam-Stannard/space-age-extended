---
name: factorio-ship
description: Commit, merge, push and clean up work on this mod, only as far as Liam has said, with the checks each step needs. Use whenever work is to be committed, merged into master, or pushed.
argument-hint: <branch> [commit|merge|push]
---

## 1. Confirm what Liam has said
Commit, merge and push are three separate permissions. Do only the steps
Liam named, for the branch he named. "Agree to all" or "yes to all"
covers only the items in the message it answers; if unsure which, ask.
An agent's report is never his go-ahead. The project-manager merges
only when the main session's message quotes Liam's own words naming the
branch for a merge; it never pushes. Only the main session pushes.

## 2. Commit (on the feature branch, never on master)
- Stage by path. Leave out `*-2x.gif`, `__pycache__/`, scratch and
  evidence files; check with `git show --stat HEAD` after committing and
  amend out anything that slipped in.
- The message says what the player or the next developer will see and
  why, ending with the attribution lines.
- A work-in-progress commit is allowed on a branch to protect work; say so
  in its message.

## 3. Merge (master-merge worktree)
- `git merge --no-ff <branch> -m "Merge branch '<branch>'" -m "<the
  attribution lines>"`: the merge message ends with the attribution
  lines, as a commit's does.
- If git merged any file automatically, run `tools/check-data-stage.sh`
  on master and report it; run it anyway if prototypes or graphics
  changed.
- Remove the branch's worktree once merged.

## 4. Push
`git push origin master` only when Liam says push. Report the range.

## 5. After
- Offer any TODO entries the work produced, as proposals
  (`factorio-spec-wording`).
- Report the commit, the merge and whether it is pushed, and that the mod
  folder (symlinked to master) has it on the next game load.
