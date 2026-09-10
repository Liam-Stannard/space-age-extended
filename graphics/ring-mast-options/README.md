# Ignition Ring Mast — five options

Five designs to be **compared, not refined**. Nothing here is adopted; when one
is picked the rest of this directory goes.

| Option | One line | What moves |
| ------ | -------- | ---------- |
| **A — the Braced Post** | §3.2 as written: a wide braced base tapering to a short capped emitter, with the charge band at the waist | a band, ~65 % of the box |
| **B — the Lying Coil** | The whole machine is a horizontal banded drum on cradles — nothing is vertical at all | a drum's length, ~90 % |
| **C — the Bell** | A squat closed dome over a charge ring at floor level, so the light is under the mass rather than in it | a ring, ~85 % |
| **D — the Flat Torus** | The charge band is a torus lying flat and the emitter is a stud in its middle | a torus, ~85 % |
| **E — the Plate Stack** | A low stack of insulator discs with the charge climbing the gaps between them | the gaps, ~70 % |

**A is carried as a fair comparison, not as the favourite.**

## The constraint that outranks everything

**The anti-read is the Arc Mast**, and §3.1 calls it the most important line in
the brief. *No cage. No open electrode. No upward-reaching structure. Nothing at
the top that looks like it wants to be struck.*

The two buildings stand on the same planet, both are called masts, and one of
them exists to be hit by lightning while the other exists to be charged from a
pipe. A player who mistakes them will build the wrong one under a storm. **Four
of the five options here refuse to have a top at all** — they put the machine's
whole read at or below the waist, which is the surest way to make the mistake
impossible.

## The rest of the constraints, agreed before drawing

1. **3 × 3, no sideways overhang**, and tall — so the tall-building clause
   applies: it leans slightly away from the camera and its shadow gets its own
   canvas.
2. **Tier 4 — the goal.** Exotic, barely reading as machinery: monolithic
   surfaces, **no seams and no fasteners anywhere**, contained light doing the
   work. This is the opposite instruction from the Drop Crusher's, and the two
   must not look like the same era. If a sheet comes back riveted, it is wrong
   however handsome it is.
3. **The charge band pulses and the emitter does not.** §3.2's signature: light
   climbs the band, holds, and dies over the four-second craft, and the top stays
   dark throughout. That is the single clearest way to say *this is not the thing
   lightning hits*.
4. **Warm white, not violet and not green.** Violet is the Coil Separator's
   field, green is the radiant family. The Array's own firing is the only other
   warm white in the mod, and these two **should** look related — they are one
   installation.
5. **It never draws what it makes.** The ignition charge is an item and it
   spoils; no charge is visible anywhere on the plate.

## The one fluid connection

**Helium-3 enters the south face, on the centre tile, facing straight out** —
`position [0, 1]`, `direction south`, volume 400. One connection and no others.

Every prompt carries the template's §8 rule in full: the flange sits **square to
the edge it is on and points straight out of it**, axis-aligned, never diagonal,
never out of a corner, and it stops flush at the edge of the footprint. A
connector angled across a shoulder is one the player can never join cleanly,
however good it looks — which is exactly the mistake the Vent Pump's §19 records
having made once already.

The inlet is **bare machine metal**. It carries something cryogenic, and an
earlier draft of these prompts frosted it for that reason — which was wrong twice
over. The engine stamps its own neutral cover on an unconnected port, so a rimed
stub ends up with a grey flange sitting in it; and a fluid box is a socket, not a
fluid. See the template's convention 5. The inlet reads by *position* alone:
south face, centre tile, square to the edge.

## The lights, and there are two

This building has both a **charge light** — warm white, inside the band, animated
— and a **status lamp**, white and engine-tinted. They must never be confused, so
every prompt puts them apart: the charge light is *contained inside* the band and
the status lens is a small hard point on the mass, well clear of it.

As everywhere else in this mod: the status lens is painted **white** in the hero
view, the top-down, the details and the silhouette, and coloured **only** inside
the three-state row. A colour baked into the plate is that colour in every state
for ever.

## The animation gate

Each option is measured for how much of its own box moves, against vanilla's
three-tile machines at 72 %, 101 % and 113 %. This building has an unusually good
claim to a large one: its signature *is* light travelling, light costs no
geometry, and a band round the waist of a 3 × 3 is most of the building's width by
construction. **Every option here is above 65 %**, which is not true of any other
round in this repo.

## What to attach, every time

| Attachment | Why | Order |
| ---------- | --- | ----- |
| `assembling-machine-3` | The house camera | first |
| `electromagnetic-plant` | Coils, windings and heavy cable runs treated as a subject in their own right, and the nearest vanilla machine to this tier | second |
| `ignition-array/concept/adopted/R-sheet.png` | **This building's assigned reference**, and here it is a *design* reference rather than a format one: the ring and the thing it rings are one installation and should read that way | last |

**Note the exception.** `graphics/TODO.md` warns that the format example is the
most dangerous attachment on the list, after a Drop Crusher generation came back
as the Ignition Array. On this building that bleed is *less* dangerous, because
the Array is genuinely its sibling — but the prompts still say the machine in it
is a different building, because a 3 × 3 charging post must not come back as a
9 × 9 silo.

## How these get judged

**By measurement first** — `check-sheet-style.py`, with the usual caveat that its
*aspect* and `base_flatness` columns do not work.

**Then by the anti-read.** Every sheet carries a silhouette panel, and on this
building the silhouette has one job: to look nothing like the Arc Mast's. If a
flat black shape of the option could be mistaken for a cage on a leg, it is
disqualified regardless of how it measures.

---

## Two things in the brief raised rather than quietly resolved

**1. §3.2's "helium inlet entering the charge band horizontally" fights §8.**
The band is at the waist and the connection is at ground level on a tile edge —
a pipe cannot enter the waist *and* stop flush at the footprint edge unless it
runs down the outside. Every prompt here routes it **up the face from the edge to
the band**, which satisfies both. The brief should say so.

**2. Nothing in the brief says what the machine looks like when it is NOT
charging**, and this building will spend most of its life idle: the charge spoils,
so a player runs it in bursts. Every prompt therefore asks for the idle state
explicitly in the three-state row — band dark, emitter dark, status lens out —
because a building whose entire read is a pulse needs to be legible without it.

## The round as rendered — 2026-09-10

All five sheets are in `graphics/entity/ring-mast/concept/options/`. Read them
with these known deviations in hand rather than judging the sheets cold:

- **B, the Lying Coil, did not draw its brief.** The drum came back standing on
  end, not lying across the footprint, which makes B the *tallest* of the five
  and breaks the one rule this whole round exists to serve: nothing vertical,
  nothing that looks like it wants to be struck. Judge B on its banding and its
  cradles, not on its silhouette — or drop it.
- **A, B and C were generated before the bare-connection rule** and all three
  drew a frost-jacketed inlet. D and E came back with a bare metal stub, which
  is what the plate should carry. This is a master-plate fix, not a reason to
  prefer D or E.
- **D, the Flat Torus, answers the anti-read most completely**: nothing rises,
  the stud is plainly a cap, and the light travels round a ring rather than
  climbing a shaft. E is the same argument in steps.

## Adopted: A, the Braced Post — with the inlet corrected

Locked 2026-09-10. The sheet is `graphics/entity/ring-mast/concept/adopted/A-sheet.png`;
the round survives as `concept/round-1-contact-sheet.png`.

**One correction carries into the master plate.** A was generated before the
bare-connection rule and drew its helium inlet frost-jacketed and pale blue. The
inlet is **bare machine metal** — see the template's convention 5, and D and E of
this round for what it should look like. Nothing else about A changes.
