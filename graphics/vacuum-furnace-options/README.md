# Vacuum Furnace — five options

Five designs to be **compared, not refined**. That is the method the Ignition
Array arrived at after four sets and twenty concepts: refining one idea makes it
a better version of itself and never tells you whether it was the right idea.

Each option is a page with its own prompt. Nothing here is adopted; when one is
picked, the rest of this directory goes, the way `array-options/` lost nineteen
pages the day option R was chosen.

| Option | One line |
| ------ | -------- |
| **A — the Pot** | A squat welded drum with one big clamped roof hatch and radiator loops on two flanks |
| **B — the Retort Bank** | Three sealed tubes lying side by side in a cradle under one common radiator manifold |
| **C — the Bell** | A heavy lifting bell standing over a fixed hearth base: the state is the seal, not the light |
| **D — the Radiator Block** | Nine tenths radiator and one tenth furnace — the heat has nowhere to go, so draw where it goes |
| **E — the Clamshell** | Two half-shells drawn together by a row of external draw bolts down a raised centre seam |

## The constraints, agreed before drawing

1. **It fits 3 x 3 with no sideways overhang.** Height above the footprint is
   fine and Factorio does it everywhere; width is not, and a plate that
   overhangs makes a row of machines interleave. The Arc Mast is the standing
   lesson at 3.14 tiles on a 3-tile pitch.
2. **It suits the Core and what the Core makes** — airless, gravity 50, nothing
   burns, nothing rusts in air that is not there, and the palette is the mod's
   own warm iron-nickel.
3. **It reads as itself at a glance**, beside the other low grey 3 x 3 machines
   on the same factory floor. This is the constraint doing the most work here.
   The Dross Classifier is locked as a stepped low box; the Drop Crusher is a
   box; this building's own spec calls it *"a squat welded drum"*. Its adopted
   sibling's page already names the risk in as many words — *"at a glance it is a
   box with a stepped lid, and the Vacuum Furnace and Drop Crusher are also
   boxes."* Three of the five options here deliberately stop being one.
4. **It never draws what it makes.** No vanilla machine paints its product into
   its own plate, so every port, hatch and mouth on these sheets is drawn empty.
   For this building the rule is nearly the whole design: **the read is
   *sealed***, so there is no throat, no door and no visible fire, and the outside
   has to carry everything.
5. **It carries its tier.** **Tier 0–1**: welded shell with visible seams,
   bolted plate, cast housings, honest wear — but built rather than improvised,
   with a properly machined hatch and a real status lamp. Not sealed-and-seamless;
   that register belongs to the Coil Separator and the Concentrator.
6. **It has three states and a still frame has to tell them apart.** RUNNING,
   BLOCKED and IDLE, with two lights that must never be confused: the orange
   sight port, and a small white lamp the engine tints. Every option puts them in
   different places on purpose.

## The one fluid connection

The flux inlet is the building's only pipe, and the template's §8 rule 2 applies
to it in full: **it lands on a tile edge, at ground level, axis-aligned, never
diagonal, never leaving the roof, never stopping in mid-air**, and the flange is
drawn into the building's own art the way the foundry does it.

**Smelting takes no flux; sintering does**, so §8 asks for a flange that looks
unremarkable with nothing plumbed to it. That is a real design instruction and
every prompt carries it: the flange is small, low and quiet, not a feature.

**§5 fixes the building at one direction**, and says so as a choice rather than a
constraint — the flux fluid box means the engine *would* allow rotation, and it
is pinned so the hatch, lamp and sight port stay in a fixed relationship. So
these prompts ask for **one machine, once**: no rotation row, and the space goes
to the three-state row instead.

## What to attach, every time

| Attachment | Why |
| ---------- | --- |
| `assembling-machine-3` | The house camera — the most-seen machine in the game, and the one a player's eye is calibrated to |
| `foundry` | A big Space Age machine at the current art standard: finish and detail density. It is also the pattern this building's flux flange copies |
| **`cryogenic-plant`** | This building's own style reference, per the reference plan in `graphics/TODO.md`. Every one of the nine gets a different one, so the set does not come back looking like one machine drawn nine times |
| **`ignition-array/concept/adopted/R-sheet.png`** | Format example: our own approved sheet, for panel layout only. Say in the prompt that the machine in it is a different building |

`tools/extract-style-references.py` cuts the vanilla ones from their real layers
at their real shifts, so what goes over is the machine as the engine assembles
it. They are Wube's art: extract to a scratch directory, attach, discard, never
commit.

**Done: `cryogenic-plant` is now in that tool's `REFERENCES` table**, composited
from its main plate and its glass layer at their real shifts (380 × 396 and
274 × 228), read off a data-raw dump rather than guessed. Cut it with
`tools/extract-style-references.py --only assembling-machine-3,foundry,cryogenic-plant`.

**And one warning that goes with that reference.** The cryogenic plant is a pale,
late-game, jacketed machine and this one is dark and tier 0–1. It is attached for
**camera, finish and detail density only** — the standing disclaimer has to be in
the prompt, and it is, because a pale jacketed furnace would be the wrong tier
before it was anything else.

**The format example is the adopted Array sheet, not `ignition-array/concept/v2-sheet.png`.**
`graphics/TODO.md`'s reference plan names the v2 sheet; that sheet is rejected and
carries a generator-added wordmark, and attaching it would invite one back. The
plan's row should be corrected to point at `concept/adopted/R-sheet.png`.

## How these get judged

**By measurement first.** `tools/check-sheet-style.py` scores a sheet against
four vanilla references for luminance, saturation and detail density, and it
earned its keep on the Array — it caught a whole set sitting at half vanilla's
chroma before anyone had to argue about it.

**Two of its numbers do not work** and should not be quoted: the *aspect* column
reads the sheet's panel bounds rather than the building, and `base_flatness`
scored a plainly diamond-shaped base at 1.000. Corner-on drawing is still found
by eye.

**One number needs reading carefully on this building.** §3.3 asks for a body
*darker than the mod's usual chassis*, and luminance is measured against a
vanilla band whose floor is 63.2. A dark furnace that measures low is doing what
its spec asked; a dark furnace that measures low **and** flat is not. Judge
saturation and edge density first here, and treat luminance as the one metric
this building is allowed to argue with.

**Then by silhouette.** Every sheet carries a silhouette panel for exactly this:
if the option is not identifiable as a flat black shape, it will not be
identifiable at map zoom either.

**The tile-grid panel is deliberately absent.** Every concept sheet in this repo
has drawn a grid that does not line up with the building on it, because a
generator has no idea where the tile edges are. These prompts ask for a plain
top-down view instead, and the footprint is measured on the real plate later with
`tools/check-footprint.py`.

**And the copper is not rationed.** All fifteen sheets in the last round came back
under vanilla's saturation floor of 0.230, the worst at 0.136, because every
prompt confined copper to one place. The adopted Array prompt says copper and
brass are *"VISIBLE and used freely on bus runs, joints and fittings"* and
measures 0.262. Appendix B item 3a is the write-up. Every prompt here says the
same thing — which matters more on this building than on any other in the round,
because §3.3's whole palette is dark grey with one orange dot in it.

---

## Four things in the spec raised rather than quietly resolved

**1. §8 says the flux flange is on "one flank" and never says which.** A 3 x 3
building has four faces and each face has three tiles; the prototype has to
declare one of them. This round pins it to the **east face, centre tile**, on all
five options, so the sheets are comparable and so the fault lamp and sight port
can be placed relative to something fixed. That is a convention adopted for the
round, not a decision taken on the spec's behalf — but note what happens if it is
left open: **the art will pin it, and then the art becomes the spec.** §8 should
name the face before stage 1.

**2. §11's three-state row and §20's last bullet disagree about the sight port.**
The row says BLOCKED is *"the sight port dark and the lamp glowing amber"*. §20
says the latch *"argues for the sight port being visible even when idle-but-blocked,
so a latched machine does not read as a working one"* — which, read literally, is
the opposite instruction, and read charitably is the same worry expressed
backwards. These prompts follow **§11**: port dark when blocked, amber lamp lit.
Two reasons. §3.3 says the heat-glow budget is one circle and that orange anywhere
else means the seal is a lie; and a lit port on a latched machine is precisely the
false "it's working" read §20 is anxious about. **§20's bullet should be rewritten
or struck**, because as it stands one of the two is wrong and a generator handed
both will split the difference.

**3. §3.3 has no copper in it at all.** Seven rows, none of them a warm metal.
A building drawn to exactly that palette will measure below vanilla's saturation
floor by arithmetic — that is the finding from fifteen sheets, not a matter of
taste. These prompts add copper and brass on bus runs, hatch furniture, dog
threads, flange faces and radiator fittings, and **§3.3 should gain a row saying
so**. The one discipline that comes with it: copper is a *material* and never
glows, so it can never be mistaken for the sight port.

**4. The fault lamp is painted white and coloured by the engine, and the concept
sheet has to lie about that on purpose.** §3.2 is emphatic: the lens is drawn
once in white with `apply_tint = "status"` and `always_draw = true`, and the
engine tints it. But the sheet's whole job is to prove the three states are
legible, which means drawing the lamp amber in one panel and pale blue in
another. Every prompt here says explicitly that **the lens is white in the hero
view and on the plate, and coloured only inside the three-state row**. Without
that line the sheet teaches the wrong thing to whoever cuts the plate from it.

## The anti-read

**§3.1 names it: vanilla's electric furnace** — an open-fronted box with a
visible glowing throat. Every part of that is wrong here, and §4 says plainly
**do not attach it**. That is followed: it is not in the attachment list, and the
forbidden-reads clause names it in words instead.

The second anti-read is not in the spec and should be: **the Dross Classifier**,
locked on 2026-09-08 as a low stepped grey box on this same factory floor. Its own
adopted page flags the collision. Options B, C, D and E each move somewhere that
building cannot follow — parallel tubes, a bell on a base, a fin block, and a
bolted spine.
