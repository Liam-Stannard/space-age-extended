---
name: factorio-spec-wording
description: Change a building spec, design doc, template, TODO entry or any other .md file in this mod the agreed way - a numbered draft, Liam's answers, then exactly the agreed text written. Use whenever wording in a .md file has to change.
argument-hint: <file> [what changed]
---

claude.md rule 8: no `.md` file is written, added to or reworded without
Liam's explicit agreement first.

## 1. Draft
Read the file and what changed (the task file, Liam's decisions, the
latest sheets). Write the draft to the session scratchpad, not the repo:
- per section that changes: the heading, the current text quoted briefly,
  the proposed replacement in the file's own voice;
- the sections that stay;
- numbered open questions, each with a recommendation.
Send the draft file to Liam and summarise it in the reply.

## 2. Agree
Wait for Liam's answer. "Agreed" covers the draft and the recommended
answers as sent; anything else, apply his changes and re-send if they are
more than a line.

## 3. Write
Write exactly the agreed text. Do not add sentences, figures or
rationale that were not in the agreed draft. If writing needs any wording
not agreed (a joining phrase, a corrected figure), list each addition,
quoted, and get it agreed before committing; remove any he does not agree.

## 4. Record
Add a dated history line where the file keeps one. The commit goes
through `factorio-ship`.
