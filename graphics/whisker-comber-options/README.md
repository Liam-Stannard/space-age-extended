# Whisker Comber — five options

Five designs to be **compared, not refined**. That is the method the Ignition
Array arrived at after four sets and twenty concepts: refining one idea makes it
a better version of itself and never tells you whether it was the right idea.

Each option is a page with its own prompt. Nothing here is adopted; when one is
picked, the rest of this directory goes, the way `array-options/` lost nineteen
pages the day option R was chosen.

| Option | One line |
| ------ | -------- |
| **A — the Carding Casing** | Two drum bearing housings bulging from each flank, under a hinged inspection lid |
| **B — the Travelling Gill** | A comb head that walks a slot along the roof, so the working state is a position |
| **C — the Spinner** | A squat vertical drum with a dogged lid: alignment by spinning rather than combing |
| **D — the Mill Stack** | A rolling-mill stand — screw-down caps above a roller stack behind an armoured face |
| **E — the Two-Lane Machine** | Two visibly unequal lanes under one casing, because the recipe is a choice |

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
   here: the spec says it plainly — the comber is *also* a low grey box that
   sorts things, standing next to a classifier that is a low grey box that sorts
   things. Whatever is picked has to survive that comparison, which is why three
   of the five leave the low box behind entirely.
4. **It never draws what it makes.** No vanilla machine paints its product into
   its own plate, so every chute, tray, bin and mouth on these sheets is drawn
   empty — and that is *why* each option encloses its working chamber. An open
   frame around an empty bed advertises that emptiness on every tick and the
   machine reads as idle while it runs.
5. **It carries its tier.** **Tier 1-2**, integration and precision plant: machined casing, flush
   panels, guarded mechanisms, some instrumentation. The needled working parts
   inside are the only crude thing about it, and the material would cut you — so
   it looks guarded.

## What to attach, every time

| Attachment | Why |
| ---------- | --- |
| `assembling-machine-3` | The house camera — the most-seen machine in the game, and the one a player's eye is calibrated to |
| `foundry` | A big Space Age machine at the current art standard: finish and detail density |
| **`recycler`** | This building's own style reference. Every one of the nine gets a different one, so the set does not come back looking like one machine drawn nine times |
| **`sealed-roboport/concept/v2-sheet.png`** | Format example: our own approved sheet, for panel layout only. Say in the prompt that the machine in it is a different building |

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

## A conflict in the spec, raised rather than quietly resolved

**§3.2 wants the before-and-after drawn on the building** — a loose tangle in the
infeed tray, a bright ordered ribbon at the outfeed — and calls it the signature
feature. **The template's §8 rule 1 forbids exactly that:** no vanilla machine
draws the thing it makes, and a tray with material in it is a lie the moment the
belt backs up or the machine idles.

These five options resolve it the template's way — every mouth, tray and slot is
drawn empty — and carry the before-and-after in **machinery** instead: coarse
guarded intake at one end against fine polished rollers at the other (A, D),
a needle bar that is visibly finer than the matting roller beside it (E).

**If that loses too much**, the fix is not to paint fibre into the trays. It is a
`working_visualisation` — the engine will draw a moving layer only while the
machine is crafting, which is the one honest way to show material: it stops when
the machine does. That is a decision for after a design is picked, and it does
not change which design is picked.
