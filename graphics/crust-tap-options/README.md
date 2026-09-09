# Crust Tap — five options

Five designs to be **compared, not refined**. That is the method the Ignition
Array arrived at after four sets and twenty concepts: refining one idea makes it
a better version of itself and never tells you whether it was the right idea.

Each option is a page with its own prompt. Nothing here is adopted; when one is
picked, the rest of this directory goes, the way `array-options/` lost nineteen
pages the day option R was chosen.

| Option | One line |
| ------ | -------- |
| **A — the Bolted Collar** | A low armoured collar pinned down by ground anchors, with a choked riser leaving one side |
| **B — the Wedge Cap** | A solid cast frustum driven over the bore: no anchors, the mass is the seal |
| **C — the Yoke** | A cast cross-yoke bolted over a small central plug, each arm ending in its own ground anchor |
| **D — the Gland Stack** | A stack of stepped screwed gland rings — a stuffing box, tightened down on a hole |
| **E — the Flush Plate** | Almost nothing above ground: an armoured plate at grade with a raised rim and a low horizontal riser |

## The constraints, agreed before drawing

1. **It fits 2 x 2 with no sideways overhang** — and 2 x 2 is tight. The Arc Mast
   is the standing lesson at 3.14 tiles on a 3-tile pitch; the same 0.14 tiles on
   a 2-tile pitch is a larger fraction of the building. The riser is what will
   cross the line, and every prompt here says so twice.
2. **It suits the Core and what the Core makes** — airless, gravity 50, nothing
   burns, nothing rusts in air that is not there, and the palette is the mod's
   own warm iron-nickel.
3. **It reads as itself at a glance.** This is the first thing built on the
   planet and it stands alone in the landscape rather than in a factory row, so
   the comparison it has to survive is not other machines — it is the *ground*.
   A 2 x 2 object with almost no height has very little silhouette to be
   recognised by, and option E is the deliberate test of how little is enough.
4. **It never draws what it makes.** No gas plume, no vapour, no jet, nothing
   escaping. The building's entire argument is that it is **holding something
   back**, so a visible leak is the design contradicting itself.
5. **It carries its tier.** **Tier 0 — Foothold.** Crude and mechanical: riveted
   and bolted plate, cast housings, ground anchors, weld seams, honest wear, and
   a burst disc that is plainly a safety afterthought. Nothing sealed, nothing
   seamless, no indicator lamps, no light used as a material. This is the
   landing-day register and it should look it beside the Coil Separator.
6. **The two-temperature read is the signature, and it is an *adjacency*.** A
   dull orange seam where the collar meets the ground and pale frost a few pixels
   away on the riser. §3.3 is explicit that the two have to be legible in the same
   glance — *that adjacency is the signature*. Every option puts them within a
   few pixels of each other on purpose.

## Four directions, so the sheet gets a rotation row

**§5 says 4**, and it says why: *"the riser is the fluid box, and a riser pointing
the wrong way is the fluid box in the wrong place."* This is the only building of
the three in this round that rotates.

So these prompts ask for **four rotations, never four elevations.** The template's
§8 is blunt about the difference: Factorio has rotations, not elevations — a
building's N/E/S/W sprites are the *same camera* with the building turned
underneath it, and a sheet that draws a flat side-on architectural view is
describing something the engine cannot produce. Every panel showing the whole
machine uses the one camera in the CAMERA block.

**What differs between the four:** the riser, and only the riser. The collar, the
anchors, the burst disc and the ground seam are identical in all four frames. The
prompts say that too, because a generator handed "four directions" will otherwise
redesign the machine four times.

## What to attach, every time

| Attachment | Why |
| ---------- | --- |
| `assembling-machine-3` | The house camera — the most-seen machine in the game, and the one a player's eye is calibrated to |
| `foundry` | A big Space Age machine at the current art standard: finish and detail density |
| **`pumpjack`** | This building's own style reference, per the reference plan in `graphics/TODO.md`. It is the wellhead read, and it is also a 3 x 3 machine — so take the *finish*, not the scale |
| **`arc-mast/concept/v4-sheet.png`** | Format example: our own approved sheet, for panel layout only. Say in the prompt that the machine in it is a different building |

`tools/extract-style-references.py` cuts the vanilla ones from their real layers
at their real shifts, so what goes over is the machine as the engine assembles
it. They are Wube's art: extract to a scratch directory, attach, discard, never
commit.

**Done: `pumpjack` is now in that tool's `REFERENCES` table**, composited from its
base and horsehead layers at their real shifts (261 × 273 and 206 × 172), read off
a data-raw dump rather than guessed. Cut it with
`tools/extract-style-references.py --only assembling-machine-3,foundry,pumpjack`.

**It is also this building's anti-read**, so the prompt labels it a camera
reference and names what must not be taken from it — Appendix B's rule for
exactly this case.

**§4 says: do not attach the offshore pump.** That is followed — it is the
anti-read, and Appendix B's rule about attaching an anti-read unlabelled is
exactly why. It is named in the forbidden-reads clause in words instead.

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
identifiable at map zoom either. On a 2 x 2 building that is not a formality —
it is the main question this round is asking.

**The tile-grid panel is deliberately absent.** Every concept sheet in this repo
has drawn a grid that does not line up with the building on it, because a
generator has no idea where the tile edges are. These prompts ask for a plain
top-down view instead, and the footprint is measured on the real plate later with
`tools/check-footprint.py --tiles 2`.

**And the copper is not rationed.** All fifteen sheets in the last round came back
under vanilla's saturation floor of 0.230, the worst at 0.136, because every
prompt confined copper to one place. The adopted Array prompt says copper and
brass are *"VISIBLE and used freely on bus runs, joints and fittings"* and
measures 0.262. Appendix B item 3a is the write-up. Every prompt here says the
same thing — and tier 0 gives it somewhere honest to live: brass fittings, bronze
bushes, copper earthing straps at the anchors.

---

## Four things in the spec raised rather than quietly resolved

**1. §8 says the gas leaves "the riser's tip, per `fluid_source_offset`", and
those are two different fields.** Read off vanilla's own prototype
(`base/prototypes/entity/entities.lua`): the offshore pump has
`fluid_source_offset = {0, -1}` **and** a `fluid_box.pipe_connections` entry at
`{position = {0, 0}, direction = south, flow_direction = "output"}`. The offset is
where the pump takes its fluid *from* — one tile out, into the water. The tile a
player's pipe actually attaches to is the pipe connection. So **the riser's tip is
the pipe connection, not `fluid_source_offset`**, and §8 as written would send
whoever implements this to the wrong field.

That matters more than a naming quibble, because §8 itself invokes the right
precedent: *"a riser drawn on one face and declared on another is the same class
of defect as the arc mast's first `lightning_strike_offset`."* Correct — and the
way to avoid it is to measure the **pipe connection** off each directional plate.
These prompts therefore say: the riser's tip terminates at the middle of a tile
edge, at ground level, and it rotates with the building.

**2. §3.3's "scorched ground — tight ring at the base" is ground scatter, and the
template forbids baking it in.** §8 rule 4 says nothing crosses the collision box,
that ground decals are the one legitimate exception, and that they *belong in
their own layer* rather than in the base plate — vanilla does exactly this with
`mining_drill_scorch_mark`. On a 2 x 2 building a ring at the base is very likely
to cross the edge, and §4 already asks the camera to show "the ring of scorched
ground", which would put it inside the plate.

These prompts draw **no ground at all**: no scorch ring, no ground plane, no
scenery. There are two better homes for it and the spec already knows about both —
the **crust vent tile** art, which §20 lists as an outstanding second art job, or
a separate decal layer. **§3.3 and §4 should be amended to say which.**

**3. Frost on a tier 0 building is a register question nobody has answered.**
§3.3 calls it a "frost jacket", and *jacketing* is tier 3's vocabulary — a
manufactured cryogenic component, the thing the Coil Separator is made of. On the
first machine built on the planet it should be **rime**: frost forming on bare
pipe because gas that expands gets cold, a consequence rather than a component.
These prompts say rime, and they say it downstream of the choke only, which also
makes the physics do the work §3.2 wants it to do. **§3.3's row should be
reworded**, because "jacket" will pull a generator toward a pale engineered
sleeve and that is the wrong tier.

**4. §11's existing prompt asks for a "side elevation".** The engine has no such
view, and the template says a sheet that draws one is describing something the
game cannot produce. This round replaces it with a **four-rotation row**, which is
what a 4-direction building actually needs and what §5 has been asking for all
along.

## The two anti-reads, and why three of the five leave the collar behind

**§3.1 names both.** Vanilla's **offshore pump** — a light open frame standing in
water with a visible impeller — and a **lava tap**. The second one is the one that
will keep coming back, because "hole in the ground with orange in it" is the most
obvious drawing of this building and it is wrong: the heat is underground and
stays there, and what comes out is *cold*. The orange is a dull conducted seam at
one joint, and it is small.

Options B, D and E each answer the first anti-read by being solid rather than
framed, which is the cheapest possible defence: a wedge, a screwed gland stack and
a flush plate cannot be mistaken for an open frame in water. Option C deliberately
takes the risk of an open structure, to find out whether "heavy" survives being
"open" — and its page says so.

One note on why C is a **cross** rather than the tripod it wanted to be. Three
buttresses at 120° is the better-looking object and the wrong one: on a square
2 x 2 footprint two of the three legs land on diagonals, and §8's rule zero says
the base must read as a square rather than as a diamond. A cross-yoke whose four
arms run to the four face midpoints stays axis-aligned by construction, which is
the same reasoning that put the Dross Classifier's slope in the roof.

---

## Round 1 measured, all five

| Option | Luminance | Saturation | Edge density |
| ------ | --------: | ---------: | -----------: |
| A — the Bolted Collar | 50.9 | 0.229 | 0.112 |
| B — the Wedge Cap | 57.6 | **0.235** | 0.121 |
| C — the Yoke | 52.7 | 0.213 | 0.097 |
| D — the Gland Stack | 53.0 | 0.207 | **0.084 — flagged `detail low`** |
| E — the Flush Plate | 55.1 | **0.260** | 0.113 |
| **vanilla band** | 63.2–90.4 | 0.230–0.490 | 0.144–0.261 |

The sheets are at `graphics/entity/crust-tap/concept/options/`, and
`concept/five-options-contact-sheet.png` holds all five at reduced size.

**Every option in this set is under vanilla's luminance floor**, between 50.9
and 57.6 against 63.2, and that is a *spec consequence rather than a generation
failure*: §3.3 sets this building's body at `#3E3B36`–`#5E584E`, which is
deliberately darker than the mod's usual chassis because it is tier 0 and half
buried. Two honest options — accept that the Crust Tap is the darkest thing on
the Core, or lift the tier-0 body range by a few points. It is a decision for
Liam, not something to fix quietly in a stage-1 prompt.

**Detail density is the other cost of 2 x 2.** Four of the five are under the
floor and the Gland Stack is the only sheet in thirty that the checker flags
outright. A two-tile building has a quarter of the canvas a 3 x 3 has, and
concentric rings are the least edge-dense shape in the set.

**The four-rotation row came back as rotations on all five** — same camera,
building turned underneath, riser moving face to face — never the elevations the
engine cannot produce.

### The copper instruction worked, and it is measurable

The previous round put every one of its fifteen sheets under vanilla's
saturation floor, because each prompt confined copper to one place. These prompts
say copper and brass are visible and used freely, and **six of this round's
fifteen sheets are now inside the band** — where none of the last round's were.
The Vacuum Furnace's Radiator Block measures **0.270**, against a previous-round
worst of 0.136. Appendix B item 3a earned its place.
