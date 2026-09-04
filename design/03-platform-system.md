# The Platform System

Space platforms are the one context every player shares, and the part of Space
Age least served by planetary technology. Each tree terminates there, and the
accumulated capabilities are what make [the corridor](04-corridor.md) passable.

---

## 1. One subsystem per tree

| Subsystem | What it covers | Claimed by |
|---|---|---|
| **Power** | Electricity generation aboard a platform | Tree 1 — Quench Turbine |
| **Structure** | Hull integrity and what a platform can survive | Tree 2 |
| **Asteroid processing** | How a platform captures, sorts and refines chunks | Tree 3 |
| **Thrust** | Engine output, propellant, manoeuvrability | Tree 4 |
| **Defence** | Weapons, shielding, damage mitigation | Tree 5 |

**Cargo and logistics is deliberately not a tree slot.** The corridor's supply
chain is built from mechanics vanilla already provides — platform-to-platform
transfer at non-planet locations, and reduced asteroid damage while stationary.
Nothing there needs a capstone chain, and inventing one would replace a real
logistics problem with a purchased solution.

Two trees must never claim the same subsystem. The point of the pattern is one
coherent platform upgrade per tree, not a pile of competing generators.

## 2. The five shared resources

Capabilities are bound into a system by competing for and feeding the same five
things:

**electricity · heat · ice · weight · consumables**

Adding any capability changes the arithmetic of the others. Rules for a new one:

1. Draw on at least one shared resource, and feed at least one other capability.
2. No flat multipliers — a multiplier cannot be traded against anything.
3. Degrade, don't destroy.
4. **Every capability must have a wrong platform to install it on.** If there is
   no platform where installing it is a mistake, it is not a decision.
5. **Never relieve two of the five at once.** A capability that solves both power
   and weight removes the tension the system is made of.

## 3. Power is the exchange rate

A platform runs one generator type, so the Quench Turbine's numbers price every
other capability's electricity draw. Its tuning cannot be finalised in isolation;
it gets re-checked as each new capability lands.

Its shape, in one paragraph: Magmatic Core plus Ice quenches into a vapour whose
*temperature is fixed by the recipe*, and the turbine clips everything above its
cap. A recipe that makes a little very hot vapour throws most of the core away; a
recipe that makes a lot at exactly the cap wastes nothing. That gap is the
technology ladder, enforced by the engine rather than by script. Full numbers in
the [tree spec](trees/vulcanus-fulgora.md).

Its two real advantages over vanilla nuclear are **no idle burn** — a parked
platform consumes nothing — and **ice**, needing roughly an eighth of what
nuclear's exchangers demand. Not density; the honest comparison on floor space
puts it between nuclear and fusion.

## 4. Heat

**The turbine deliberately exposes no usable waste heat and has no heat network
at all.** An earlier design made it a `reactor` with a real heat-pipe interface;
vanilla heat exchangers and steam turbines then converted its rejected heat back
into roughly as much electricity again, relieving Power twice over and breaking
rule 5.

So heat is not a baseline the platform provides. It is introduced by whichever
capability needs it — currently asteroid processing, whose refining runs hot —
and rejected by the **coolant loop**: the Quench Coolant / Spent Quench Coolant
pair, made on Aquilo, radiated back to cold in vacuum on ordinary chemical
plants. That loop is a fluid circuit built from existing buildings, not a new
machine, which is why Power can own it without breaking the one-building rule.

The same loop, run backwards, is how the Core is eventually powered — see
[the Core](05-the-core.md).

## 5. Ice

Ice is the quietest of the five and the most contested. The turbine needs it, the
refinery needs it, and out past the midpoint there are no oxide asteroids to
catch. Any capability that consumes ice is making a claim on the same asteroid
capture rate as the platform's power supply, and should be priced knowing that.

---

Next: what all this is for — [the corridor](04-corridor.md).
