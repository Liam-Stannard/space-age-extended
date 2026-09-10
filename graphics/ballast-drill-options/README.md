# Ballast Drill — five options

Five designs to be **compared, not refined** — the method the Ignition Array
arrived at after four sets and twenty concepts, and the one the Drop Crusher's
round proved on a building that had spent ten versions refining a single idea.

Nothing here is adopted. When one is picked the rest of this directory goes.

| Option | One line | What moves |
| ------ | -------- | ---------- |
| **A — the Ballast Block** | §3.2 as written: an unadorned slab riding four guide rails above the head, on splayed legs | a slab, ~60 % of the box |
| **B — the Ring Press** | The mass is a torus: an annular ballast ring descending around a central column | a ring, ~80 % |
| **C — the Screw Jack** | Four massive corner screws wind a platen down onto the head and let it go | a platen and four screws, ~70 % |
| **D — the Sled** | No legs and no stroke — the chassis *is* the ballast, and the machine is deliberately still | **nothing** |
| **E — the Slug Magazine** | A carousel on the roof drops ballast slugs onto the head one at a time | a drum, ~60 % |

**A is carried as a fair comparison, not as the favourite.** It is what §3.2
currently describes, and if none of the other four beats it that is worth
knowing.

## The constraints, agreed before drawing

1. **5 × 5 with no sideways overhang.** This is the largest footprint in the set
   after the Ignition Array, and the Arc Mast at 3.14 tiles on a 3-tile pitch is
   the standing lesson about what overhang costs.
2. **Tier 0 — Foothold, crude and mechanical.** Riveted plate, cast housings,
   exposed gears and screws, weld seams, hazard tape, honest wear. It is priced
   in freight (see below), which puts it on the landing-day shelf beside the Drop
   Crusher.
3. **The anti-read is a derrick.** No tower, no headframe, no rotating
   superstructure, nothing reaching up. Everything about this machine is low and
   wide, because its argument is mass.
4. **It never draws what it makes.** No ore, no spoil, no dust, no debris — not
   on the ground, not at the boom, not under the head. It is a mining machine and
   it must still be drawn empty.
5. **It reads as itself beside the other Core machines.** The Drop Crusher is a
   buttressed cylinder, the Vacuum Furnace a welded drum, the Whisker Comber a
   standing drum. None of those is 5 × 5, which helps — but three of the five
   options here deliberately avoid being another vertical mass on a square base.

## Four engine facts that are not style opinions

**Four fluid flanges, drawn now, for a fluid that does not exist yet.**

The drill inherits four input fluid connections from the big mining drill, and
today every one of them is unreachable — kamacite's `minable` carries no
`required_fluid`, so they accept nothing. **They are kept deliberately.** A mining
fluid for this drill is wanted later, and the layout has to be settled *before*
the plate is cut: a flange added to a finished plate is a repaint of all four
directions, and the Vent Pump is the standing proof of how expensive rearranging
plumbing after the fact is.

The layout is **vanilla's, verbatim**, which is the point — a player who has
plumbed a big mining drill has already learned this one:

```
          . . O . .        O = ore out, north face, centre
          . . . . .        W = fluid in, west face, one tile north of centre
      W . . . . . . E      E = fluid in, east face, one tile north of centre
          . . . . .        S = fluid in, south face, either side of centre
          . S . S .
```

**North takes no connection**, because north is where the ore comes out.

**And the plate draws none of them.** That is the part that matters for this
round, and it is vanilla's own answer: the big mining drill's sprite has **no
plumbing on it whatsoever** — checked, its north plate is a gantry and two
ladders. The fitting is the fluid box's `pipe_covers`, and the *engine* stamps it
at whichever connections are live. **On an ore that needs no fluid it draws
nothing at all.**

So keeping the box costs the art nothing. Today the covers never appear, because
kamacite asks for no fluid. The day a recipe does ask, the flanges appear by
themselves, in the right places, in all four directions, and not one plate is
repainted.

Every prompt therefore says **draw no fluid fittings at all** — no flange, no
stub, no hose, no valve, no capped port. Painting them in would put four visible
sockets on a machine that has no use for them, which is the Vent Pump's §19
complaint exactly. The connection panel marks the four points with a *symbol*, to
prove the plate leaves those tile edges clear.

**The ore leaves at `vector_to_place_result = [0, −2.85]`** — the north face,
centred, just outside the footprint. That is a real output *position*, unlike the
Drop Crusher's, so this building **does** get a boom, and it points north on the
north-facing frame. Draw it short and stubby, and draw it **empty**.

**Four directions.** A mining drill rotates, and the boom rotates with it. That is
four plates, and per the Vent Pump's §5: **do not ask for four viewpoints**, ask
for four arrangements from one fixed camera, or a generator returns a turntable.

**Nothing else on this planet can work kamacite.** The ore carries its own
`resource-category`, so the Ballast Drill is not one option among drills, it is
the only one — which is why it is priced in freight like the Drop Crusher, and
why it can afford to look like the specialist it is.

## The lights

**One white lens, engine-tinted**, `apply_tint = "status"` with
`always_draw = true`, as on the Vacuum Furnace and the Drop Crusher. A drill that
has run its patch out, or lost power, or has nowhere to put its ore, stops for
reasons the player cannot otherwise see — and this machine halves the patch it
works, so *"no minable resources"* is a state it will reach and should announce.

Every prompt carries the same two-part instruction: the lens is **white** in the
hero view, the top-down, the details and the silhouette, and coloured **only**
inside the three-state row.

## The animation gate, applied before the plate exists

Each option is measured for how much of its own box moves, against vanilla's
three-tile crafting machines at 72 %, 101 % and 113 %, and against the Dross
Classifier's rejected 5.2 % drum. On a 5 × 5 the box is 160 screen px, so a
moving part has further to go to look like anything.

**Option D moves nothing, deliberately.** The template's §6.2 offers exactly that
— *"the honest answers are to redesign the moving part larger or to decide the
machine is still and say so here"* — and a machine whose whole argument is dead
weight has a real claim to it. It is in the round to be argued with.

## What to attach, every time

| Attachment | Why | Order |
| ---------- | --- | ----- |
| `assembling-machine-3` | The house camera, the machine a player's eye is calibrated to | first |
| `big-mining-drill` | This building's assigned style reference in `graphics/TODO.md`, and the drill it derives from — for finish and for the *scale* of a large drill | second |
| *(no format example)* | See the warning in `graphics/TODO.md`: the Drop Crusher's round had one generation come back as the Ignition Array, the building in its format sheet | — |

Cut the vanilla ones with `tools/extract-style-references.py --only
assembling-machine-3,big-mining-drill`. They are Wube's art: extract to a scratch
directory, attach, discard, never commit.

## How these get judged

**By measurement first** — `tools/check-sheet-style.py` for luminance,
saturation and edge density against the vanilla band. Two of its numbers do not
work and should not be quoted: *aspect* reads the sheet's panel bounds rather
than the building, and `base_flatness` once scored a plainly diamond-shaped base
at 1.000.

**Then by silhouette**, and on a 5 × 5 that matters more than usual: this is the
biggest thing on the Core's factory floor after the Array, so its shape is what a
player navigates by.

**And the copper is not rationed.** Fifteen sheets in an earlier round all came
back under vanilla's saturation floor because every prompt confined copper to one
place. Every prompt here says it is used freely.

---

## Two things in the brief raised rather than quietly resolved

**1. §3.2 asks for "a cutting head under the block, mostly hidden, seen only as a
rim of disturbed ground".** Disturbed ground is *terrain*, and a building sprite
cannot draw it — the plate is transparent everywhere the building is not, and
whatever tile the drill stands on shows through. Every prompt here asks for the
head as a **shrouded rim on the machine**, not as a mark on the floor. §3.2 should
be reworded.

**2. §3.2's "output boom on one side" needs to name the side, and it is north.**
`vector_to_place_result` is `[0, −2.85]`: centred on the north face. A boom drawn
on a flank would be a boom the ore does not come out of. This round pins it, and
the brief should say so before stage 1.

## The round as rendered — 2026-09-10

All five sheets are in `graphics/entity/ballast-drill/concept/options/`.

- **The fluid rule held.** No option drew a flange, stub or hose anywhere. A, C,
  D and E all marked the four connection points with a symbol on their own
  panel, which is exactly the check that panel exists for.
- **The output boom came back tall in A, C, D and E** — an upright chute rising
  above the roofline rather than a stubby spout reaching past the north edge.
  That is a real conflict with the anti-derrick rule, and it costs every one of
  them some of the low-and-wide read. It is a master-plate fix.
- **D, the Sled, is nearly featureless in silhouette**, which is the price of
  its no-moving-parts argument. Decide whether that reads as *heavy* or as
  *unfinished* before adopting it.

## Adopted: B, the Ring Press — with the output corrected

Locked 2026-09-10. The sheet is `graphics/entity/ballast-drill/concept/adopted/B-sheet.png`;
the round survives as `concept/round-1-contact-sheet.png`.

**One correction carries into the master plate: the output must be built the way
vanilla's drills build theirs.** B drew an upright boom rising above the
roofline. Vanilla does not do that, and the reason is geometric rather than
stylistic.

Measured off the real sprite, not remembered. The big mining drill is 5×5 —
`selection_box` `{{-2.5,-2.5},{2.5,2.5}}`, the same footprint as ours — and its
`vector_to_place_result` is `{0, -2.85}`: ore is placed 0.35 tiles **past** the
north edge. Its output layer, `big-mining-drill-N-output.png`, is a 128×88
six-frame sprite shifted `by_pixel(-2, -66.5)` — that is −2.08 tiles, so the
chute spans roughly −2.42 to −1.73 and sits **inside** the footprint with its
mouth flush to the north edge.

What it draws is a **short drag-chain scraper conveyor set into the north face at
ground level**, sloping down and forward, with a small drive sprocket at its
head. Low, built in, overhanging nothing. The ore itself is a real item entity
the engine places in front of the mouth — the plate draws the chute and never
what comes out of it, which is convention 1.

So: replace B's upright boom with that. A low built-in chain chute on the north
face, mouth flush with the tile edge, nothing above the roofline, nothing past
the footprint, and drawn empty.
