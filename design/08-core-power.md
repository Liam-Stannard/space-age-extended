# The Core's power — the radiant cycle

**Status:** stage 1 and the turbine are in the mod; stages 2 to 4 are designed,
not built. Every number is a first guess, never played.

The Core's power is one loop in four stages, built from two of its own fluids:
radiant solution and hydrogen.

## 1. The two fluids

Radiant solution carries the energy. Hydrogen strips it out and leaves it as
solid fuel. So enriching the solution gives more fuel, and enriching the
hydrogen would not. Where each comes from is in `04-the-core.md`.

## 2. The first power

The first power is the hydrogen turbine: 1.8 MW each, about one to a fresh vent
before mining productivity research. It needs no power to make power, so it is
also how a blacked-out grid restarts. When radiant power browns out, the
reaction plants stop, then the fuel, then the generators, and only the turbine
can start them again.

## 3. The cycle

**Stage 1, the basic reaction.** The Reaction Plant turns 100 radiant solution
and 100 hydrogen into 1 radiant fuel. The radiant generator burns it at 10 MW,
50 seconds a fuel. Each burnt fuel leaves a spent cell, which stage 3 recycles.
Helium-3 is not used for power.

**Stage 2, solution enrichment.** The isotope centrifuge turns 200 radiant
solution into 100 enriched solution. 100 enriched solution and 100 hydrogen make
3 radiant fuel. So the same solution gives 3 fuel instead of 2, and 100 hydrogen
gives 3 instead of 1.

**Stage 3, cell reprocessing.** 4 spent cells and 50 hydrogen make 100 spent
solution, which splits into 80 stripped solution and 2 radiant sludge. 80
stripped solution makes 40 radiant solution. That gives back 10 solution per
spent cell, about a tenth of what it used. It is the first stage that runs
backwards, so the line becomes a loop.

**Stage 4, fuel enrichment.** 5 radiant fuel and 2 radiant sludge make 1
enriched radiant fuel. Only the radiant reactor burns it: 40 MW, more with
neighbours. The sludge comes from stage 3, so stage 4 can't run unless stage 3
does.

Where the stages sit in the tech tree: `09-core-tech-tree.md`.
