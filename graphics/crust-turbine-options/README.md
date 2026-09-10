# Crust Turbine — five options

Five designs to be **compared, not refined**. Nothing here is adopted; when one
is picked the rest of this directory goes.

Its brief is new — `graphics/building-spec-crust-turbine.md`, written 2026-09-10,
because until then this building lived inside the Crust Tap's spec as "a
companion generator". That was fine while it was one line of Lua and a problem
the moment anyone had to draw it.

| Option | One line | What moves |
| ------ | -------- | ---------- |
| **A — the Let-Down** | §3.2 as written: a long low body with a frosted expansion housing at one end and a generator can at the other | a rotor face, ~25 % |
| **B — the Frost Barrel** | One fat insulated barrel between two flanges, frost blooming along it, and nothing visible moving at all | **nothing** |
| **C — the Twin Rotor** | Two rotor faces side by side down the body, counter-turning behind open grilles | two faces, ~50 % |
| **D — the Cascade** | Four expansion stages in a row, each smaller and frostier than the last, so the pressure drop is the building | a stage-by-stage frost, ~85 % |
| **E — the Collared Pair** | Built to echo the tap's Bolted Collar so the two read as one installation | a rotor face, ~25 % |

## The constraint that does the most work

**It must not look like a steam turbine — and the reason is not the obvious
one.** Yes, this building currently wears vanilla's steam-turbine sprites and the
whole point is to stop. But the sharp problem is that **the player builds real
steam turbines on this planet too**: the melt-and-steam line in `04-the-core.md`
§2 runs 500 °C steam into vanilla turbines, on the same factory floor, fed by a
pipe that looks like this one's.

Two turbines, two different fluids, and reversing them is a mistake the player
can actually make. So the separation has to be visible at a glance, and the brief
gives it: **this machine is cold**. The tap sells *pressure, not heat*; gas
expands, the energy is in the difference, and nothing burns. Frost where the
other is hot, no lagging, no insulation blankets, no heat stain, and **no glow of
any kind anywhere on the building**.

## The rest of the constraints

1. **2 × 5, and it is the flattest thing in the set.** Long and low along its
   axis. No overhang on either side.
2. **Tier 0 — Foothold**, the same register as the Drop Crusher and the Ballast
   Drill: riveted plate, cast housings, bolted flanges, weld seams, honest wear.
   It is priced in freight — 20 steel plate, 10 pipe, 20 iron gear wheels — and it
   should look like something that came off a cargo pod.
3. **Two orientations, not four.** A `generator` draws `horizontal_animation` and
   `vertical_animation`; both connections are on the long axis, so a quarter turn
   is the only rotation that means anything.
4. **It never draws what it makes.** No arcs, no sparks, no crackle, nothing at
   the terminal box.
5. **Small on purpose.** 1.8 MW, roughly one turbine per tap. A player who tiles
   fifty of these should still find the melt line the better answer by a wide
   margin, and the art should not oversell it — this is a foothold, not a power
   station.

## The two fluid connections

**One at each end of the long axis, and they are identical** — `[0, 2]` and
`[0, −2]`, both `input-output`, both filtered to crust gas. Gas passes straight
through, so turbines chain end to end exactly as steam turbines do.

**The art has to make the chaining obvious**, because a player who cannot see it
will put a pipe between every pair and wonder why the row looks wrong. Identical
flanges at both ends is the cheapest way to say it, and every prompt here insists
on it.

Each flange sits **square to the end it is on and points straight out of it**,
axis-aligned, stopping flush at the middle of that tile edge. There is no
diagonal hookup on a Factorio pipe — the Vent Pump's §19 records what believing
otherwise cost.

**And the flanges stay bare metal.** Frost is this building's signature, so the
temptation is to run it all the way out to the ends — but a connection carries no
frost, heat or tint at all (template convention 5). The engine stamps its own
neutral cover on an unconnected port, and rime under a grey flange reads as a
mistake. The frost belongs on the body, a tile back from the edge.

## The lights

**One white lens, engine-tinted**, and on this building it is the *only* light,
because §3.3 forbids every other kind. A cold machine with a status lamp is a
strong, simple read.

Painted **white** in the hero view, the top-down, the details and the silhouette;
coloured **only** inside the three-state row.

## The animation gate, and why this round is allowed to fail it

Every option here is measured against vanilla's 72–113 %, and **four of the five
are well under it**. That is not carelessness; it is what a 2 × 5 pressure
let-down honestly has. A rotor face is a disc at one end of a long body, and the
building's actual signature — frost — is a *state*, not a motion, and §9 is
explicit that animating it as a cycle would read as the machine stopping and
starting.

**Option B takes the other honest answer and moves nothing at all**, and option D
tries to make the pressure drop itself the animated element. Between them the
round tests whether this building should move.

## What to attach, every time

| Attachment | Why | Order |
| ---------- | --- | ----- |
| `assembling-machine-3` | The house camera | first |
| `steam-turbine` | The building this must **not** be, attached for finish and scale only. The forbidden-reads clause names it in words as well | second |
| `crust-tap/concept/adopted/A-sheet.png` | Its sibling — these two are commissioned as a set and stand next to each other on the ground | last |

Cut the vanilla ones with `tools/extract-style-references.py`. They are Wube's
art: scratch only, never committed.

## How these get judged

**By measurement first**, with the usual caveat about `check-sheet-style.py`'s
*aspect* and `base_flatness` columns.

**Then by the pairing.** Put each sheet beside `crust-tap/concept/adopted/A-sheet.png`.
These two buildings are always built together and always stand together, and the
round is partly asking which of the five looks like it arrived in the same crate.

**And then by the confusion test**, which is this building's own: put the
silhouette beside a vanilla steam turbine. If you have to look twice, the option
has failed the one thing it exists to get right.

## The round as rendered — 2026-09-10

All five sheets are in `graphics/entity/crust-turbine/concept/options/`.

- **Every one of them is drawn nearer side-on than Factorio's projection.** This
  is the defect `TODO.md` says to expect on every remaining building; measure the
  trimmed aspect against a real 2×5 vanilla plate before cutting anything, and
  fix it with a regenerate carrying a vanilla sprite as camera reference.
- **The frost reached the end flanges in A, B, D and E**, despite the brief
  saying in as many words that it must not. The rule is right and the generator
  ignored it; strip the rime off the flange faces at master-plate stage.
- **C, the Twin Rotor, risks reading as an air cooler** — two round grilles side
  by side on a roof is a fan bank before it is a turbine. That is a different
  wrong answer from the steam-turbine anti-read, but it is still a wrong answer.
- **B and D both kept their promise to show no mechanism at all**, which makes
  them the honest options for a machine whose signature is a state, not a motion.
