# The Core

Arrival is the gate, not the ending. [The corridor](04-corridor.md) covers
getting here; this document covers what is here, which is where the capstones
stop being components and become materials.

---

## 1. What it is, and what it must not become

The Core is the stripped metallic heart of the Shattered Planet. What matters
about it is what is *absent*.

- **No fluids at all.** No water, no oil, no lava, no ice. Nothing needing steam,
  cooling water or wet chemistry works out of the box.
- **No oxygen, so nothing burns.** Boilers, burner drills, heating towers and
  every combustion recipe are dead on arrival. This is the sharpest constraint on
  the Core, and it is physically honest.
- **The largest thermal gradient in the game.** A frozen surface over a still-hot
  metallic interior. The mod opened on a heat-driven generator and ends on a body
  that is one enormous heat engine waiting to be tapped.
- **Absurd metal density and nothing else.** The richest ore body in the system
  and the poorest of everything else.

Three things it must not become:

**Not a sixth planetary tech tree.** No new science pack, no local material
economy, no new building family. Every machine that works here was designed
somewhere else by a tree the player already built.

**Not a place you retire to.** Infinite metal plus local power tempts a player to
relocate the whole factory. The absence of fluids, combustion and biology has to
be enforced hard enough that the Core is always a place you *supply*.

**Not a construction site that finishes.** A megaproject completed once kills
every supply line that built it, and the mod's ethos is loops that keep running.

## 2. Stage one — Foothold

Land with nothing that works. This stage alone is a complete and satisfying
ending if the rest is never built, and it should be designed so that stopping
here is not a truncation.

**The crisis is ice.** The only generator that runs here is the Quench Turbine,
and quenching needs Magmatic Core *and* Ice — neither of which exists on the
Core. Both must be freighted the entire length of the corridor, and ice is bulky,
so the opening hours are a supply crisis rather than a base-building exercise.
That is deliberate: it makes the player feel the corridor's length as a
throughput number rather than a travel time.

**The escape is to run the coolant loop backwards.** The same fluid circuit that
rejects heat into space on a platform will instead carry heat *out of the ground*
and into generators. The mod's cooling technology becomes the Core's power
source, and the moment it lands the corridor stops carrying fuel.

That single reversal is the stage-one objective, and it should be the first
genuinely satisfying moment on the surface.

## 3. Stage two — The Dynamo

The Core is a dead iron-nickel body that once had a magnetic field. Restarting it
is the mod's megaproject: a multi-segment structure, closer to a rocket silo than
a research lab, where **each segment consumes a different tree's output in
volume**.

That is the design point. The Dynamo cannot be built by running one supply line
hard; its mandatory segments require the five trees' chains operating
simultaneously, at sustained rate, down a route that eats platforms. Every
logistics lesson in the mod is examined at once.

Each capability earns a ground role, and the toolkit built for space turns out to
be the colonisation toolkit:

| From | Ground role | Tier |
|---|---|---|
| **Asteroid processing** — Electrode Array | With no water and no acid, electrolytic separation is the only way to refine Core ore. The refinery transfers to the ground wholesale | Mandatory |
| **Power** — Thermionic Assembly, and the coolant loop | Taps the gradient, and cools the Dynamo itself | Mandatory |
| **Structure** — ablative composite | Every structure on a surface that swings between the two extremes | Mandatory |
| **Defence** — deflector field | Ground defence against magnetic storms and the ejecta the restart itself throws | Mandatory |
| **Thrust** | *No segment.* Its contribution is entirely to traversal; it has nothing to spend on the ground | — |
| **Optional tier** — cryogenics, organics, oxidiser | Superconducting windings need cold; anything organic arrives frozen or not at all; an airless world has no oxidiser but the imported kind | Optional |

Mandatory segments gate whether the Dynamo fires at all. Optional segments do
not: missing one leaves it running, just slower to build, more failure-prone, or
throttled in output.

**The failure mode matters.** A half-built Dynamo is a large, expensive, visibly
incomplete *thing*, not a locked recipe. The player should be able to stand in it
and see which segment is starving — and for an optional segment, starving should
read as throttled, not as a wall.

## 4. Stage three — The reversal

The Dynamo does not fire a weapon or open a portal. It drives a **magnetic launch
loop**: a planetary-scale accelerator that throws Core material to any
destination in the system without rockets.

The flow reverses. For the whole mod the corridor has been a cost, everything
travelling outward at enormous expense. Now the Core becomes the richest supplier
in the system and the traffic starts coming home. The exported material feeds
infinite research back on the inner planets, so the post-game loop lives at both
ends of the corridor rather than only at the far one.

That is the right shape for a Factorio endgame: the reward for solving a
logistics problem is a better logistics problem.

**It must not trivialise rockets.** The loop exports *Core* material
specifically. If it becomes a general free cargo route between planets, it
deletes the logistics economy the entire mod is built on.

## 5. Why the corridor stays alive

Two ongoing demands, both drawn from existing mechanics rather than invented:

- **The field decays.** The Dynamo needs continuous power and continuous
  replacement of its superconducting windings, so cryogenics and holmium keep
  flowing outward forever.
- **The launch loop wears.** It is a rail at planetary scale, so it consumes
  ablative material exactly as platform armour does; the Structure chain never
  switches off.

The endgame state is not "the Core is finished." It is a corridor running in both
directions permanently — the same answer tree 1 reached with its own consumable
fuel line, applied at the largest scale the mod has.

## 6. Risks

**Scope.** A landable surface, a megaproject, an export mechanic and a decay
system is a large amount of content for a mod whose first tree is not yet played.
Stage one is the deliverable; stages two and three are sequels.

**Ejecta and storms need a real answer.** If ground hazards are chip damage, the
deflector's ground role is decorative. If they are severe, the player must be
able to see them coming and build against them — the same degrade-don't-destroy
rule that governs everything else.

**Everything here rests on the moddability spike.** If a landable surface past
the Shattered Planet is not possible, this document is void and the mod is five
trees and a platform capability set — a smaller but entirely coherent product.
