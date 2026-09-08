# Dross Classifier — five options

Five designs to be **compared, not refined**. That is the method the Ignition
Array arrived at after four sets and twenty concepts: refining one idea makes it
a better version of itself and never tells you whether it was the right idea.

Each option is a page with its own prompt. Nothing here is adopted; when one is
picked, the rest of this directory goes, the way `array-options/` lost nineteen
pages the day option R was chosen.

| Option | One line |
| ------ | -------- |
| **A — the Shaker Deck** | A stepped armoured housing on compressed leaf springs, with an eccentric flywheel at its high end |
| **B — the Trommel** | A screen drum lying across the footprint in a roller cradle, turned by a ring gear |
| **C — the Rocker Beam** | The whole housing see-saws on a central trunnion, driven by a swinging counterweight |
| **D — the Cascade Tower** | A tall tower with a bucket-elevator leg: lift once, then let it fall through decks |
| **E — the Spiral Rake** | A closed settling box with one inclined screw leg walking the coarse fraction out |

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
   here: the Ballast Drill, the Drop Crusher and this machine all lean on
   the same planetary fact — gravity doing mechanical work — and the spec wants
   them to read as a *family*. Three identical grey boxes are not a family, they
   are a repetition, so three of the five options deliberately leave the box
   behind.
4. **It never draws what it makes.** No vanilla machine paints its product into
   its own plate, so every chute, tray, bin and mouth on these sheets is drawn
   empty — and that is *why* each option encloses its working chamber. An open
   frame around an empty bed advertises that emptiness on every tick and the
   machine reads as idle while it runs.
5. **It carries its tier.** **Tier 0-1**, the landing-day machines but deliberately built: cast
   housings, bolted plate, one or two exposed mechanisms, honest wear. Nothing
   sealed, nothing seamless, no indicator lamps. The Drop Crusher's exposed gears
   are correct *because* it is tier zero, and this machine sits just above it.

## What to attach, every time

| Attachment | Why |
| ---------- | --- |
| `assembling-machine-3` | The house camera — the most-seen machine in the game, and the one a player's eye is calibrated to |
| `foundry` | A big Space Age machine at the current art standard: finish and detail density |
| **`centrifuge`** | This building's own style reference. Every one of the nine gets a different one, so the set does not come back looking like one machine drawn nine times |
| **`bed-tender/concept/v2-sheet.png`** | Format example: our own approved sheet, for panel layout only. Say in the prompt that the machine in it is a different building |

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

## The one thing every option has to solve

**The v1 sheet came back corner-on**, and the template records why: this building
is directional by nature — it has a high end and a low end — and a generator
turns a directional machine to show the slope off. The fix is in every prompt
here: **the slope goes in the roof and the walls stay upright**, so there is
nothing to turn. Options C and E carry the same risk in a different form, a
rocking body and an inclined leg, and both prompts pin the axis parallel to a
face and say so twice.

## What is not settled

**Whether the two discharge bins should be on opposite faces at all.** The
template's §8 rule 3 says an assembling machine draws no output port, because the
inserter may stand anywhere — and the v1 prompt asked for two chutes on opposite
faces regardless, which is a promise the entity cannot keep. Every option here
draws its bins as closed decoration built into the housing rather than as ports
aimed at tiles. If that reads as coy in the sheets, the honest fix is to drop the
bins entirely rather than to aim them.
