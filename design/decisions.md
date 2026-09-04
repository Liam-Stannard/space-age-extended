# Decisions

What was settled, what it replaced, and why — recorded once so the design
documents can state what is true instead of arguing with earlier drafts.

A decision listed here should read as fact everywhere else. Anything still open
lives at the foot of the document that owns it.

---

## Scope and shape

**D1 — The mod is five cross-planet trees plus a shared endgame.**
Each pair of planets gets a small tree (4–10 technologies) ending in a capstone
that unlocks a product and a building. The five capstones feed one production
line on the Core, which is where the game is won.

**D2 — Nauvis is not part of the mod.**
It is the world the player already knows inside out, and a chain that starts
there is a chain about iron plates. The mod lives among Vulcanus, Fulgora, Gleba
and Aquilo, which gives six possible pairs; five get trees.
*Cost accepted:* the mod now begins later — there is no tree available on a
player's first trip out, so the first one has to be worth the wait.

**D3 — The five pairs are V↔F, V↔G, F↔G, F↔A, G↔A.**
Vulcanus ↔ Aquilo is the reserve. Heat against cold is the strongest unused
theme, but taking it would have put three of five trees behind Aquilo and emptied
the mid-game. With four worlds and five pairs the even loop is unavailable, so
Fulgora and Gleba each appear three times — watch that Fulgora does not end up
doing the same job in all three.

**D4 — A tree opens when both its planets' vanilla trees are complete.**
Nothing else gates it. The mod never puts vanilla content behind mod content.

**D5 — The win condition moves to the Core, and it is won on completion.**
Not on arrival. Vanilla's Solar System Edge victory is disabled through
`space_finish_script`'s `set_no_victory`, and the mod calls
`game.set_game_state` itself when the Ignition Array fires. This is the only
change the mod makes to vanilla.

## The trees

**D6 — Every tree teaches exactly one new mechanic, and the mechanic is the
problem.**
The mod creates its own problems rather than borrowing vanilla's. A tree with no
mechanic is a set of recipes; a tree with three is a mod of its own.

**D7 — The mechanics are surge production (V↔F), maturation (V↔G), the living
line (F↔G), the cold loop (F↔A) and seed stock (G↔A)**, with **seeding the
field** on the corridor. Two rest on the spoil timer and four do not.

**D8 — The capstones are the five parts of a field coil.**
A coil has a conductor, a magnetic core, insulation, a coolant and a frame; there
are five trees, so each supplies one. Every capstone is therefore visibly *in*
the thing being built, and each is integrated through a different local input so
the five integration technologies are five problems rather than one repeated.

**D9 — Power is not a tree's problem.**
Vanilla covers it to the Edge — solar 400 on Vulcanus, lightning on Fulgora,
fusion for Aquilo. It only becomes hard past the Edge, and the corridor answers
it there with the new asteroid's power material.

## The Core

**D10 — Pressure 5, gravity 50, magnetic-field 0, solar-power 0.**
Pressure 5 is the load-bearing number: the rocket silo works (≥1) while boilers,
furnaces, heating towers, roboports and burner inserters do not (≥10). Nothing
burns, and there is no bot network until one is earned. Gravity 50 clears every
gravity threshold and makes the Core the densest body in the game.

**D11 — No living enemies; the hazard is arc storms**, caught by attractors that
bank the strike as power. The thing that damages you is the thing that runs you.

**D12 — Three sited resources: kamacite ore, melt vents, gas vents.**
Ore is rich, scattered and finite, so the base spreads and rails matter. Melt
vents yield unbarrelable molten kamacite at a declining rate. Gas vents yield
helium-3 — rare, precious, and required to draw melt, so the scarce resource
throttles the abundant one.

**D13 — No carbon, no water, no organics on the Core, ever.**
The vents give it an industry, not independence. This is what keeps the corridor
running after the megaproject is built.

**D14 — The Core's own mechanics are gravity settling, orbital homogenisation,
cold welding and whisker growth.**
Weight, vacuum, time and the absence of gravity doing the work that heat and
electricity do everywhere else. Settling and homogenisation are opposites, which
is what makes the surface/orbit round trip physically motivated rather than a
logistics rule.

**D15 — The Core has the sixth tech tree, and its own science pack.**
Geodynamic science is crafted from the same intermediates the end products need,
so research and construction draw on one supply: every pack burned is a Field
Coil Segment delayed. The pack is locked to pressure 1–9, does not mature, and
takes two fixed intermediates — the field conductor and the reinforced frame — so
research opens once F↔A and V↔G are delivering while the segment still needs all
five.

## Reversals

Recorded so they are not re-proposed as new ideas.

**R1 — Power moved off the trees and onto the corridor.**
It was Vulcanus ↔ Fulgora's reserved problem. Vanilla solves power well until the
sun stops, so a power capstone in the mid-game would have been solving a problem
the player does not have.

**R2 — The Core has no heat network.**
An earlier draft gave it Aquilo's mechanic: a frozen crust, `heating_energy` on
every building, heat piped from the vents. Rejected as a reprise. Melt still
splits between metal and power, but as a choice between two settling recipes, one
yielding more melt and a little steam and the other less melt and a great deal at
500 °C.

**R3 — Maturation moved from the Core to the corridor.**
It was written as the Core's central process. The Core has its own time-based
mechanic in whisker growth, and two "wait for the material" processes in one
place would blur. Maturation is a warehouse that ages; growth is a field you
harvest.

**R4 — Four mechanics were designed and cut**: charge (energy as decaying cargo),
substrate (manufactured ground for off-world crops), launch (a superconducting
silo re-pricing freight — which could never have worked platform-to-platform
anyway, since the silo prototype requires gravity), and suspension (perishables
held indefinitely in coolant).

**R5 — Synthetic graphite was dropped as a capstone.**
Carbon is available from carbonic chunks on any platform, so no tree should claim
a job the player can do by parking a crusher. Whether carbon can be caught in the
Core's *orbit* is a separate dial, and it is set to no — the far field stays
barren.

**R6 — The obsolete platform-system document was deleted.**
It described a design in which each capstone was a space-platform capability.
Capstones are coil parts now, and the platform content lives in the corridor and
the Core's orbital half.

## Verified engine facts behind these decisions

Measured, not assumed — three earlier claims in this design were wrong until
checked.

- **Placement is gated by surface conditions.** At pressure 0 the game refuses
  boilers, furnaces, heating towers, roboports, every chest, the rocket silo, the
  biolab and the agricultural tower; the chemical plant, assembler, foundry,
  electromagnetic plant, biochamber, recycler and cryogenic plant all place fine.
  It separates planets too: the biolab is Nauvis-only at pressure exactly 1000,
  the agricultural tower Nauvis-and-Gleba at 1000–2000.
- **Recipe conditions and entity conditions are different locks.** Most big
  machines are *manufactured* under a condition and placed anywhere — so
  manufacture alone is never a crossing.
- **Nine fluids have no barrel**, so they can never leave their world:
  `lava`, `molten-iron`, `molten-copper`, `holmium-solution`, `electrolyte`,
  `ammonia`, `ammoniacal-solution`, `fluorine`, `lithium-brine`.
- **Promethium has no crushing recipe** — the far field is inert by design.
- **A fusion cell needs 100 ammonia**, which has no barrel, so cells are made on
  Aquilo or nowhere.
- **Victory is moveable**: `space-finish-script.lua` fires on a platform reaching
  `victory_location`, and exposes `set_victory_location` and `set_no_victory`.
- **Asteroids create entities when they die** (`dying_trigger_effect`), which is
  the pattern the seeding mechanic uses.
- **Item weight defaults to 100 against a 1,000,000 rocket lift**, so freight
  cost is derived unless set deliberately.
