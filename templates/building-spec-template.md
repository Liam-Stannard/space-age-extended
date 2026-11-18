# <Building> — building spec

Copy it to the place claude.md rule 3 gives, and fill it in before
any art. §1 is read from the mod; the rest is the art brief. The art bars are in
`.claude/skills/factorio-task/knowledge/standards.md`, and the stages in the
factorio-building-round skill.

---

# 1. Facts

**Fill rule:** `DOCUMENTATION-LANGUAGE.md` §7.4.

- **Name:**
- **What it does:**
- **Size and directions:**
- **Where it can be built:**
- **Power:** what it uses or makes, or "none".
- **Inputs and outputs:** its slots and connections only.
- **Speed:** crafting speed and module slots.
- **Cost:**
- **Weight:**
- **Unlocked by:**
- **Art:** "placeholder", "signed off (date)", or "being redone".
- **Remnants and explosion:** "Complete", "In Progress" or "TODO".
- **Art files:** `concept/<building>/`.

---

# 3. Visual Design

## 3.1 Design Concept

What the machine is, and what it must not be mistaken for.

## 3.2 Key Visual Features

Its features.

### Signature Feature

The one feature that makes it recognisable, ideally one that shows how it works.

## 3.3 Colour Palette

| Role | Hex | Where |
| ---- | --- | ----- |
| | | |


---

# 4. Factorio Visual Style

The vanilla buildings it takes its finish and scale from, and what it takes
from each.

---

# 8. Connections

Each connection, with its tile and side, read from the prototype. Any hard
offsets, and how its inputs and outputs read.

---

# 9. Working Animation

Fill in before modelling, or write `None — [why]` for a building that does not
move. One row a step:

| # | Step | Entries | Ticks | What moves | Ease | Accent |
|---|---|---|---|---|---|---|
| 1 | [name] | [first–last, from 0] | [ticks] | [parts] | [even / eased / hold / snap] | [entry and sound, or —] |

The steps' entries add up to the loop, with every entry in exactly one step.
Entries count from 0, as the game's frames do (`engine.md`).

---

# 14. Icon

What the icon shows, and what is dropped at small sizes.
