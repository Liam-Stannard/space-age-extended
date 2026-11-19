---
name: factorio-spec-wording
description: Change a building spec, design doc, template, TODO entry or any other .md file in this mod the agreed way - a numbered draft, Liam's answers, then exactly the agreed text written. Use whenever wording in a .md file has to change.
argument-hint: <file> [what changed]
---

How a `.md` file is changed: `DOCUMENTATION-LANGUAGE.md` §8.

## 1. Draft
Read the file and what changed (the task file, Liam's decisions, the
latest sheets). The docs-moderator writes the draft, as `.claude/agents/docs-moderator.md` (Draft) and `DOCUMENTATION-LANGUAGE.md` §8.3 say. A second docs-moderator checks it before Liam sees it.
Send the draft file to Liam and summarise it in the reply. Put the open
questions to him as the standing rules' **Asking Liam** says.

## 2. Agree
Wait for Liam's answers. What his agreement covers is in
`DOCUMENTATION-LANGUAGE.md` §8.4. Apply any changes he asks for, and
send the draft again if they are more than a line.

## 3. Write
The docs-moderator writes the agreed text, as `DOCUMENTATION-LANGUAGE.md` §8.5 says.

## 4. Record
(§8.6) The commit goes
through `factorio-ship`.
