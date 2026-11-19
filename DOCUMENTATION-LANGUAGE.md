# Documentation language

Every rule for how this project's text is worded. Other files point here and do not repeat these rules. The docs-moderator checks each document change against them.

## 1. Every document

1. Write in short, simple English.
2. Each fact lives in one place. Elsewhere, point to it; do not repeat it.
3. State facts, not opinions. Any claim about the game, the mod or the past names its source, or can be checked. An instruction is not a claim, and passes.
4. A fact that rests on one note, report or comment alone, with no kept record of a test, says so. A measured figure gives the command that measured it, so anyone can re-run it.
5. Write in the file's own voice.
6. Commands and code inside a document are not held to these rules.

## 2. Reports, questions and drafts sent to Liam

1. Commands, figures and file:line references go in a separate evidence file beside the report; commands and code names are as §2.4 says.
2. When a file is named for Liam, name it by its absolute path.
3. Every image, GIF or sheet he must judge is named beside the question or finding it belongs to, is sent to him before the question, and is under 8000 px on its longer side.
4. Quote the rule, principle or text a finding or question is about, in full. No commands or code names: text that holds them is described in plain words, except Liam's own words and a draft's current and proposed wording, which are quoted.

## 3. Questions to Liam

1. One decision per question, asked one at a time.
2. Its context in at most three short lines, besides the text it quotes (§2.4).
3. Each option on one line, saying what it changes.
4. The recommended option first.

## 4. Liam's words

1. Liam's words are quoted exactly as he wrote them, with the date.
2. Where two sources disagree, the line that loses is reported as wording to fix, with both lines quoted, or described where §2.4 says.

## 5. In-game text

1. Descriptions follow vanilla Factorio's style: one or two plain sentences saying what the thing does.
2. A building's text is themed on its name.
3. Leave out figures, since the game lists them, and leave out where it can be built.
4. Never name a resource, fluid or item.
5. A building's item has no text of its own.

## 6. Reports

1. Answer in the ticket's own numbering. On a re-run, mark each earlier finding resolved or not.
2. Each acceptance criterion is PASS, FAIL or NOT RUN, with its evidence, as §2.1 says.
3. Proposed wording for any `.md` file, spec or TODO entry is marked as a proposal.
4. Anything the criteria do not cover is marked as an observation.
5. A code review's findings come most severe first, each with the file and line, one sentence stating the defect, and the input or state that makes it go wrong. Report only what was confirmed by reading or running; mark the rest PLAUSIBLE. Style remarks go last, marked as such.
6. A coder's report gives the files changed, a sentence each; each acceptance criterion and how it is met; anything not done; art needed.
7. Art figures are quoted beside vanilla's, for the bars in standards.md, where §2.1 says; the report names the comparison sheet and states any bar not met.
8. A commit message says what the player or the next developer will see and why, and ends with the attribution lines. A work-in-progress commit says so.

## 7. The shape of documents

1. A knowledge-file line gives the fact, then its source or how it was verified, and the date. A standards line gives Liam's words or the decision, the date, and how it is checked.
2. A task file's Goal says what is true when it is done, in two or three sentences. A ticket's Do takes a few lines. The task file's Decisions give Liam's answers, quoted as §4.1 says.
3. Each design document and tree spec gives its own status.
4. A building spec's facts are plain facts read from the mod, with no comparisons. Its recipes are not in the spec: they are in the line's document (06 or 08). What it does takes one or two sentences; what it is, and must not be mistaken for, two or three lines; its features, up to five, each one a thing the model can show. Every glow is named, with what it shows. The painted area is named too.
5. A technology entry has its own heading, with its description, cost, purpose and dependencies.
6. An idea has a number, a one-line pitch, and four headings: what the game already gives, what it does not, what it would cost, and its status.
7. A principle has a name; the rule, in one sentence that can fail a proposal; why, in two to four lines; then Applies to, Fails when, Concern when, Checked by, Vanilla precedent, Exceptions and Source.

## 8. Drafts and agreement

1. No `.md` file is written, added to or reworded without Liam's explicit agreement first. Propose the wording; write it only once agreed. The exceptions are a task file's ticket Status lines, entries in QUESTIONS.md, his answers recorded there word for word, and an agent's own notes, drafts, reports and digests, where §8.2 lets it create them.
2. No new `.md` file is added to the repo or its worktrees without his permission: that is, a file git tracks, or one it would commit because it is not ignored. Anywhere else, agents may create `.md` files freely: outside the repo, as in the session scratchpad, or in a folder git ignores, such as `evidence/` and `.claude/tasks/`.
3. A draft gives, for each section that changes, its heading, the current text quoted briefly and the replacement; then the sections that stay; then numbered open questions.
4. "Agreed" covers the draft as sent. Each open question needs its own answer.
5. Write exactly the agreed text. Any wording that was not agreed is listed, quoted, and agreed before it is committed.
6. Add a dated history line where the file keeps one.
