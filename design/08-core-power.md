# The Core's power — the radiant cycle

**Status:** stage 1 and the turbine are in the mod; stage 2 is designed, not
built. Every number is a first guess, never played.

The Core's power is one loop in two stages, built from two of its own fluids:
radiant solution and hydrogen.

## 1. The two fluids

Radiant solution carries the energy. Hydrogen strips it out and leaves it as
solid fuel. So enriching the solution gives more fuel, and enriching the
hydrogen would not. Where each comes from is in `04-the-core.md`.

## 2. The first power

The first power is the hydrogen turbine (its output is in its spec), about one
to a fresh vent before mining productivity research. It needs no power to make power, so it is
also how a blacked-out grid restarts. When radiant power browns out, the
chemical plants stop, then the fuel, then the generators, and only the turbine
can start them again.

## 3. The cycle

**Stage 1, the basic reaction.** A chemical plant turns 100 radiant solution
and 100 hydrogen into 1 radiant fuel in 20 s. The radiant generator burns it (its output
and burn time are in its spec). Each burnt fuel leaves a spent cell, which stage
2 recycles.
Helium-3 is not used for power.

**Stage 2, cell reprocessing.** 4 spent cells and 50 hydrogen make 100 spent
solution, which splits into 80 stripped solution and 2 radiant sludge. 80
stripped solution makes 40 radiant solution. That gives back 10 solution per
spent cell, about a tenth of what it used. It runs backwards, so the line
becomes a loop.

Where the stages sit in the tech tree: `09-core-tech-tree.md`.
