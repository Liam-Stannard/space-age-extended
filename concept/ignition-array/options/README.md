# Choosing the Ignition Array

**Decided.** The Array is **option R, the Suspended Core** — see
`R-suspended-core.md`, the only spec left in this directory. The nineteen
rejected options have been deleted; this is the record of how the choice was
made and what it cost, kept because the method transfers to every other building.

## The problem it solved

The Array's shape had never actually been *chosen*. v1, v2 and v3 were one idea
refined three times, not three ideas compared — and refining a shape nobody had
committed to is how that building consumed most of its art budget. Twenty
concepts were drawn across four sets before one was picked.

## The constraints, and how they narrowed

Three, agreed up front: it fits inside 9 × 9 with no overhang, it suits the Core
and what the Core makes, and it shows how charged it is. The third one did the
most work — the Array assembles a hundred field coil segments and the building
had never said so, and "where does a 0-to-1 fill live, and is it legible at
normal zoom" eliminated more designs than taste did.

Height was later allowed above the footprint, the way Factorio draws every tall
building — that is not the sideways overhang that was rejected on the r4 deck.

## What the four sets cost, and what each taught

| Set | Register | Outcome |
| --- | --- | --- |
| A–E | tier 0 — riveted, rusted | wrong register: that is the landing-day machines |
| F–J | tier 4 — seamless, monolithic | overshot into generic science fiction |
| K–O | advanced but still Factorio | right register, measured back inside vanilla's bands |
| P–T | the same, built for spectacle | R chosen from these |

**The tier ladder is real and it is easy to miss in both directions.**
`building-spec-template.md` puts the Array at tier 4, and drawing the last
building in the game in the first building's vocabulary throws away the thing the
ladder exists for. But overshooting is just as wrong: sets F–J measured at
**saturation 0.10–0.12 against vanilla's 0.23–0.49**, roughly half the chroma
floor, and sat at the bottom of vanilla's detail range. Cold, monochrome and
smooth, where Factorio is warm, busy and mechanical.

That was the spec's fault, not the generator's — set 2 asked for a blue-grey
shell and "almost no copper", and got exactly that. Set 3 put the warmth and the
mechanical density back while keeping the advanced *fabrication*, and every
option landed in band.

## What the measurements were worth

`tools/check-sheet-style.py` measures a concept against the four vanilla style
references rather than against an opinion, and saturation, luminance and detail
density all earned their keep — they caught set 2's problem before anyone had to
argue about it.

**Two of its numbers did not.** The *aspect* column is unusable when the hero
crop hits the sheet's own panel bounds, which it usually does, so it reports the
panel's shape rather than the building's. And `base_flatness`, written to catch
corner-on drawing, scored the Driven Column a perfect 1.000 while its base is
plainly a diamond, and flagged the Storm Crown, whose base is merely round. Both
corner-on offenders were found by eye. A metric that reads the *top-down* panel's
outline against the grid would probably work; nothing yet does.

## The prompt method that worked

Sectioned, not prose, per Appendix A — `== CAMERA ==` first, then BUILDING, FORM,
COLOUR with hexes, RULES, PANELS, OUTPUT. The four standing vanilla sprites
attached every time with the "do not copy the design" clause. A fresh chat per
concept, so no design bleeds into the next.

Every sheet carried a **charge sequence** row, and from set 4 a **silhouette**
panel and a **discharge** panel too — so "readable at a glance" and "the ignition
is an event" became things a sheet proves rather than things a spec asserts.
