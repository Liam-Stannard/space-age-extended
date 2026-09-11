# Helium Concentrator — five options

Five designs to be **compared, not refined**. That is the method the Ignition
Array arrived at after four sets and twenty concepts: refining one idea makes it
a better version of itself and never tells you whether it was the right idea.

Each option is a page with its own prompt. Nothing here is adopted; when one is
picked, the rest of this directory goes, the way `array-options/` lost nineteen
pages the day option R was chosen.

| Option | One line |
| ------ | -------- |
| **A — the Waist** | One fat sealed drum with a machined belt at mid-height: hot below it, frosted above it |
| **B — the Cold Cap** | A wide low holding pan carrying a small frost-jacketed condenser bell — nine tenths hot mass, one tenth cold |
| **C — the Twin Bottles** | Two unequal vessels side by side, one hot and one frosted, bridged at the waist |
| **D — the Coil Trap** | A helical exchanger wound round a central core, warm at its foot and frosted at its crown |
| **E — the Sunken Well** | Almost no height: a machined roof deck with a frost-ringed capped well in it, the heat showing at the skirt |

## The constraints, agreed before drawing

1. **It fits 3 x 3 with no sideways overhang.** Height above the footprint is
   fine and Factorio does it everywhere; width is not, and a plate that
   overhangs makes a row of machines interleave. The Arc Mast is the standing
   lesson at 3.14 tiles on a 3-tile pitch.
2. **It suits the Core and what the Core makes** — airless, gravity 50, nothing
   burns, nothing rusts in air that is not there, and the palette is the mod's
   own warm iron-nickel.
3. **It reads as itself at a glance.** This building sits at **tier 3** on a
   floor that is mostly tier 0, and the player should be able to read that off
   the factory floor without opening the tech tree. It also stands beside the
   Coil Separator, which is the *other* tier 3 machine in the set and is already
   locked as a jacketed vessel with a condenser stack. Frost and jacketing are
   now spoken for; whatever is picked here has to be separable from that.
4. **It never draws what it makes.** No vanilla machine paints its product into
   its own plate, so every port, flange and mouth on these sheets is drawn
   empty — and that is *why* each option encloses its working chamber. This
   building's whole job is to hold molten metal still, and a visibly open melt
   surface is a lie the moment the machine idles.
5. **It carries its tier.** **Tier 3**, the Core's own goods: seamless welded
   shells, chamfered forms, cryogenic jacketing where it is earned, machinery
   implied rather than shown. But it is heavy and short, because it stands on the
   heaviest world in the game — §3.1 says *squat and dense* in as many words.
6. **The two-temperature split is the signature, and it is a split, not a
   gradient.** Emissive orange in the lower third, frost at the waist, and a hard
   line between them. Every option puts that line somewhere different; that is
   most of what the five are testing.

## The three fluid connections, which are the geometry to get right

This is the first building in the round with fluid boxes, so the template's §8
rule 2 bites: **every connection lands on a tile edge, at ground level,
axis-aligned, never diagonal, never leaving the roof, never stopping in mid-air**,
and vanilla puts the connector in the building's own art rather than letting the
engine draw a cover.

| Fluid | Face | In the prompts as |
| ----- | ---- | ----------------- |
| Molten kamacite **in** | south, centre | a wide dark flange at ground level on the near face |
| Helium-3 **out** | north, centre | the riser's outlet, brought back down to ground level |
| Settled melt **out** | west, centre | a heavy insulated line at ground level on the left face |

**§5 fixes the building at one direction**, and says so as a choice rather than a
constraint: the engine would let a machine with fluid boxes rotate, and this one
is pinned because rotating it would move all three flanges at once. So these
prompts ask for **one machine, once** — no rotation row — and spend the space on
detail and the state pair instead.

## What to attach, every time

| Attachment | Why |
| ---------- | --- |
| `assembling-machine-3` | The house camera — the most-seen machine in the game, and the one a player's eye is calibrated to |
| `foundry` | A big Space Age machine at the current art standard: finish and detail density. It is also the pattern this building's flanges copy |
| **`chemical-plant`** | This building's own style reference, per the reference plan in the art backlog (now `TODO.md`). Every one of the nine gets a different one, so the set does not come back looking like one machine drawn nine times |
| **`vent-pump/concept/v4-sheet.png`** | Format example: our own approved sheet, for panel layout only. Say in the prompt that the machine in it is a different building |

`tools/extract-style-references.py` cuts the vanilla ones from their real layers
at their real shifts, so what goes over is the machine as the engine assembles
it. They are Wube's art: extract to a scratch directory, attach, discard, never
commit.

**Done: `chemical-plant` is now in that tool's `REFERENCES` table**, cut from the
entity's own north base layer at its real size and shift (204 × 292, shift
0.03125, −0.28125) read off a data-raw dump rather than guessed. Cut it with
`tools/extract-style-references.py --only assembling-machine-3,foundry,chemical-plant`.

## How these get judged

**By measurement first.** `tools/check-sheet-style.py` scores a sheet against
four vanilla references for luminance, saturation and detail density, and it
earned its keep on the Array — it caught a whole set sitting at half vanilla's
chroma before anyone had to argue about it.

**Two of its numbers do not work** and should not be quoted: the *aspect* column
reads the sheet's panel bounds rather than the building, and `base_flatness`
scored a plainly diamond-shaped base at 1.000. Corner-on drawing is still found
by eye.

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
same thing.

---

## Four things in the spec raised rather than quietly resolved

**1. §8 puts the helium-3 outlet on the "north face, high", and §3.2 has the
riser "leaving at the top". The template forbids both.** §8's rule 2 is explicit:
a pipe that leaves the top of a building, or stops in mid-air, connects to
nothing — the engine puts the connection on the tile boundary the prototype
names, and a player's pipe arrives there and nowhere else. The same rule allows
the fix: *"a riser is fine as long as it comes back down and terminates at the
edge."* So every prompt here climbs the riser up the flank for the read and then
brings it down to ground level at the north tile edge. **The spec's §3.2 and §8
should be corrected to say so**; as written they describe a connection the engine
cannot make.

**2. §8 names three faces and no tiles.** A 3-wide face has three tiles on it, and
which one the flange sits on is a number the prototype has to declare. This round
pins all three to the **centre tile of their face**, so the five options are
comparable and so the sheets can be judged against one geometry. That is a
convention adopted for the round, not a decision taken on the spec's behalf — if
the real fluid boxes end up offset, whichever option wins gets its flange moved at
stage 1, which is cheap.

**3. §3.3 has no copper in it at all.** Its four rows are body, melt, frost and
shielding collars, and a building drawn to exactly that palette will measure below
vanilla's saturation floor by arithmetic — that is the finding from fifteen sheets,
not a matter of taste. These prompts add copper and brass on bus runs, joints,
flange faces and fittings, and **§3.3 should gain a row saying so**.

There is a real tension underneath that, and it is worth naming rather than
hiding: the two-temperature read wants orange **confined to the lower third**, and
copper is orange. The prompts resolve it by separating material from light —
copper and brass are a *material* and never glow, and the only emissive orange on
the building is melt heat below the waist line. If a sheet comes back with a warm
haze over the whole machine, that separation failed and it is the first thing to
check.

**4. "Hot" cannot mean fire here.** The Core is airless at pressure 5; nothing
burns and nothing exhausts. The heat in the lower third is **incandescent metal
seen through slots and joints, and conducted heat in seams** — dull, contained,
and coming from inside. Every prompt says so, because a generator asked for a hot
lower third will draw a furnace flame unless told what hot is made of.

## The anti-read, and why three of the five leave the drum behind

**§3.1 names it: a distillation column.** No fractionating trays, no full-height
ladder cage, no flare. That is easy to state and hard to avoid, because a tall
ribbed drum with a pipe climbing its flank *is* the silhouette of a refinery
tower, and option A is exactly that shape drawn short.

The second anti-read is not in the spec and should be: **the Coil Separator**,
which was locked on 2026-09-08 as a jacketed vessel with a condenser stack and
frost collars. It is the other tier 3 machine on the same floor and it already
owns "pale jacketing on a dark shell". Options B, D and E each move the read
somewhere that building cannot follow — proportion, a helix, and the roof.

---

## Round 1 measured, all five

| Option | Luminance | Saturation | Edge density |
| ------ | --------: | ---------: | -----------: |
| A — the Waist | 70.1 | 0.145 | 0.119 |
| B — the Cold Cap | 73.7 | **0.173** | 0.136 |
| C — Twin Bottles | 65.4 | 0.143 | 0.108 |
| D — the Coil Trap | 69.9 | 0.153 | 0.113 |
| E — the Sunken Well | 72.1 | 0.154 | 0.133 |
| **vanilla band** | 63.2–90.4 | 0.230–0.490 | 0.144–0.261 |

The sheets are at `concept/helium-concentrator/options/`, and
`concept/five-options-contact-sheet.png` holds all five at reduced size.

**This set is the one that stayed under the saturation floor**, and the reason
is the design rather than the prompt: the palette is a dark shell, pale frost and
one dull orange, and frost is the least saturated thing a building can wear. The
Cold Cap gets closest at 0.173 because it has the most bare metal showing.

**Two options are under vanilla's detail floor by a distance** — Twin Bottles at
0.108 and the Coil Trap at 0.113 — because both are made of smooth curved
vessels. That is the Whisker Comber's round-shell problem again, and it is fixable
at stage 1 with instrumentation rather than by changing the design.

**Every option held the hard temperature line.** Nothing warm appears above the
belt, the bell's skirt, the cross-over clamp, the boundary collar or the deck.
That was the rule most likely to be lost to a gradient, and it survived five
times out of five.

### The copper instruction worked, and it is measurable

The previous round put every one of its fifteen sheets under vanilla's
saturation floor, because each prompt confined copper to one place. These prompts
say copper and brass are visible and used freely, and **six of this round's
fifteen sheets are now inside the band** — where none of the last round's were.
The Vacuum Furnace's Radiator Block measures **0.270**, against a previous-round
worst of 0.136. Appendix B item 3a earned its place.

---

## CHOSEN — option C, the Twin Bottles

Picked by Liam on 2026-09-09. Its page is the only one left in this directory;
the other four are deleted, and so are their full-size sheets. What survives of
the round is this README, the winner's page with its production notes, and
`concept/helium-concentrator/five-options-contact-sheet.png`, which holds all five
at reduced size.

The adopted sheet is `concept/helium-concentrator/adopted/C-sheet.png`.

**Chosen because it draws the temperature split on the pipe**, at a clamp
halfway along a lagged cross-over, rather than on a shell where it has to be
inferred. Two unequal vessels also give it a plan silhouette no other 3 x 3 on
the Core has: every one of them is a single mass.

**What the round cost, and what it bought.** Five generations, no refinements.
The set's finding was that this building's palette fights the measurement: dark
shell, pale frost and one dull orange put all five under the saturation floor, and
the two smooth-vessel designs under the detail floor as well. The runner-up worth
recording is **B, the Cold Cap** — the best-measured sheet of this set at 0.173
and 0.136, and the only one whose top-down view is instantly distinguishable —
which is where to go if the Twin Bottles cannot be made dense enough at stage 1.
