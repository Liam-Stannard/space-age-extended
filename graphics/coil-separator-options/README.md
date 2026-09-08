# Coil Separator — five options

Five designs to be **compared, not refined**. That is the method the Ignition
Array arrived at after four sets and twenty concepts: refining one idea makes it
a better version of itself and never tells you whether it was the right idea.

Each option is a page with its own prompt. Nothing here is adopted; when one is
picked, the rest of this directory goes, the way `array-options/` lost nineteen
pages the day option R was chosen.

| Option | One line |
| ------ | -------- |
| **A — the Throat** | A copper toroid stood on edge, aperture to the camera, the field burning inside the ring |
| **B — the Split Poles** | Two shaped pole shoes facing each other across a narrow slot, the field standing in the gap |
| **C — the Magnet Drum** | A sealed drum turning behind a hood, the field a thin bright line along the scraper |
| **D — the Cold Plant** | Nine tenths refrigeration and one tenth magnet: the cost of the field, drawn instead of the field |
| **E — the Quadrupole** | A monolith with four corner coil bosses and a square shaft down through the middle |

## The constraints, agreed before drawing

1. **It fits 3 x 3 with no sideways overhang.** Height above the footprint is
   fine and Factorio does it everywhere; width is not, and a plate that
   overhangs makes a row of machines interleave. The Arc Mast is the standing
   lesson at 3.14 tiles on a 3-tile pitch.
2. **It suits the Core and what the Core makes** — airless, gravity 50, nothing
   burns, nothing rusts in air that is not there, and the palette is the mod's
   own warm iron-nickel.
3. **It reads as itself at a glance**, beside the other low grey 3 x 3 machines
   on the same factory floor. This is the constraint that does the most work
   here: this machine sits at tier 3 on a floor that is mostly tier 0, and
   the player should be able to read that off the factory floor without opening
   the tech tree. It is the *most advanced-looking* of the three buildings in
   this round, and it should not be confusable with either of them.
4. **It never draws what it makes.** No vanilla machine paints its product into
   its own plate, so every chute, tray, bin and mouth on these sheets is drawn
   empty — and that is *why* each option encloses its working chamber. An open
   frame around an empty bed advertises that emptiness on every tick and the
   machine reads as idle while it runs.
5. **It carries its tier.** **Tier 3**, the Core's own goods: sealed, chamfered, seamless where it
   can be, cryogenic jacketing where it is earned, light used as a material. But
   heavy and visibly strained — this machine makes a magnetic field on a world
   with none, and 2.5 MW should look like it costs something.

## What to attach, every time

| Attachment | Why |
| ---------- | --- |
| `assembling-machine-3` | The house camera — the most-seen machine in the game, and the one a player's eye is calibrated to |
| `foundry` | A big Space Age machine at the current art standard: finish and detail density |
| **`nuclear-reactor`** | This building's own style reference. Every one of the nine gets a different one, so the set does not come back looking like one machine drawn nine times |
| **`superconducting-store/concept/v1-sheet.png`** | Format example: our own approved sheet, for panel layout only. Say in the prompt that the machine in it is a different building |

`tools/extract-style-references.py` cuts the vanilla ones from their real layers
at their real shifts, so what goes over is the machine as the engine assembles
it. They are Wube's art: extract to a scratch directory, attach, discard, never
commit.

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

## The anti-read, which is the whole point of the building

**Vanilla's electromagnetic plant is the machine this one exists to replace.**
It is a clean lab-white box with a violet field playing over it, and the fiction
is that the player has been *importing* it because the Core has no magnetic field
to manufacture one in. So this building must look like the heavier, darker, older
answer they built themselves.

That is why **the electromagnetic plant is not attached** to any of these
prompts, even though Appendix B normally wants it in the standard four: attaching
the anti-read unlabelled pulls the design back toward the thing the building
exists to not be. The nuclear reactor covers the same ground — heavy, dark,
contained power — without the pull.

## The rule every option shares

**The glow is contained.** A steady cold blue-violet, inside the named aperture
and nowhere else: not on the chassis, not as a rim light, not as a haze. Fulgora's
lightning and this are the only violet in the mod's palette and they must not be
confused — that one flickers, this one does not.

Option D is the deliberate test of that rule: it hides the coil completely and
shows one lit slot at the base of a refrigeration plant. If a sheet can carry the
read with that little light, the rule is safe everywhere else.

---

## Round 1 measured, all five

| Option | Sheet | Luminance | Saturation | Edge density |
| ------ | ----- | --------: | ---------: | -----------: |
| A — the Throat | `options/A-sheet.png` | 64.0 | 0.189 | 0.129 |
| B — Split Poles | `options/B-sheet.png` | 70.3 | 0.218 | 0.141 |
| C — Magnet Drum | `options/C-sheet.png` | 69.8 | 0.188 | 0.142 |
| D — Cold Plant | `options/D-sheet.png` | 70.2 | 0.136 | 0.129 |
| E — Quadrupole | `options/E-sheet.png` | 65.0 | 0.208 | 0.148 |
| **vanilla band** | | 63.2–90.4 | 0.230–0.490 | 0.144–0.261 |

**The sheets are at `graphics/entity/coil-separator/concept/options/`.**

**This is the strongest of the three sets.** All five hold the containment rule —
the violet stays inside the aperture, the slot, the arc, the base slot and the
shaft respectively, and never touches the chassis — and none of them reads as
vanilla's electromagnetic plant. Option E is the only sheet in the whole round
whose detail density clears vanilla's floor; option D is the least saturated
sheet of the fifteen, which is what happens to a design with no copper in it.

**One finding runs across all fifteen sheets in this round, not just these
five: every one of them is under vanilla's saturation floor.** The measurement is
like-for-like — the adopted Ignition Array sheet scores 0.262 the same way, on
the same kind of charcoal page — so this is real and not an artefact of the
background.

The cause is in the prompts, and it is worth fixing before the next round rather
than arguing about taste. These prompts confine copper to one place each
(*"the drive end only"*, *"the coil itself"*). Option R's prompt, the one that
was adopted, said the opposite: copper and brass **"VISIBLE and used freely on
bus runs, joints and fittings. This is what keeps the building warm."** Set 2 of
the Array's concepts failed the same way at 0.10–0.12, and the fix that worked
was putting the warmth and the mechanical density back while keeping the
advanced fabrication.

Whichever option is picked here, its stage-1 prompt should let the copper out.
