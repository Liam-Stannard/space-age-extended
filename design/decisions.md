# Decisions

Design reversals and open calls, recorded once so the specification documents can
state what is true instead of arguing with their own earlier drafts.

Anything settled here should read as fact in the other documents. Anything open
is a question for the next person to touch that area.

---

## Settled

**D1 — The mod may require its own content for its own destination.**
An earlier draft made every tree skippable by giving each corridor hazard two
answers from different pairs. That is reversed: redundancy is exactly what makes
a tree skippable, and there is no reason the mod's endgame should be reachable
without the mod. One hazard, one answer, on the mandatory path only. The line is
the vanilla win condition, which is untouched.
*Cost accepted:* five single points of failure, which is why the mandatory set is
capped at five and why they are played first.

**D2 — Gating is by traversal, not by an ingredient list.**
A final technology consuming one capstone per tree is a checklist the player
grinds. Each band removes a class of resource instead, and arrival is the gate.
Capstones still matter, as the materials the corridor consumes.

**D3 — Hazards are written as removed resources, not as named products.**
This is what lets a tree be demoted and its band re-assigned if it plays badly,
while keeping each band's failure legible. "Ammunition economy fails" is a
hazard; "you lack a Deflector Field" is not.

**D4 — Power is one tree, and it owns its coolant loop.**
An earlier draft split the Power band between tree 1 and a second tree's "thermal
bus" stage, which would have given one tree two subsystems and two new buildings.
The loop is a fluid circuit built from existing buildings — Quench Coolant, its
spent form, and radiative cooling on ordinary chemical plants — so tree 1 can own
it without breaching the one-building rule. Heat itself is introduced by asteroid
processing, not by the generator.

**D5 — The Quench Turbine exposes no usable waste heat.**
It was once a `reactor` with a real heat-pipe interface. Vanilla heat exchangers
and steam turbines then converted its rejected heat into roughly as much
electricity again, relieving Power twice over. It now has no heat network at all.
Any future capability wanting heat as an input must introduce it.

**D6 — Magmatic Core is an ingredient, not a fuel.**
The generator went through three architectures (a power interface with a hidden
hopper; a hidden furnace as a fake fuel slot; a real reactor). The current design
is a plain `generator` fed by a quench recipe whose output temperature the recipe
fixes, and which the turbine clips. The tier ladder is enforced by the engine
rather than by script, and `control.lua` is empty.

**D7 — No new in-space cooling for vanilla Fluoroketone.**
The platform loop runs on mod fluids specifically so that vanilla fusion's
coolant logistics stay exactly as vanilla designed them.

**D8 — No Bulk Crusher.**
Folding the platform's existing crushing chain into one better building is
precisely the redundant building tier the principles forbid. Floor space on the
corridor gets answered by the mandatory capabilities being compact, not by an
upgraded crusher.

**D9 — Band 4's hazard is the failure of every vanilla power source in turn**,
not "waste heat." Solar is dead out there; nuclear's exchangers starve once oxide
capture stops supplying water; fusion coolant cannot be re-cooled in vacuum. The
quench chain is the one with a closed loop. This replaces an earlier hazard that
cited generation heat the mod does not produce.

---

## Open

**O1 — Where is Gleba?**
It appears in no mandatory tree, while the mod's own advice says the next tree
should use an anchor unlike tree 1's — and spoilage is the most distinct anchor
in the game. Thrust is the one unassigned pair. Either Gleba takes it, or the mod
accepts that its most interesting anchor is optional content. Decide when tree 2
is chosen.

**O2 — Provisional pairs.**
Structure→Vulcanus↔Aquilo, Asteroid processing→Fulgora↔Aquilo, and
Defence→Nauvis↔Fulgora are sketches, not commitments. Each is confirmed only when
its anchor survives the checklist. The subsystem claims are firm regardless.

**O3 — Tier 1 quench cost.**
90 MJ per core is sized for one turbine, not a platform: 100 MW would need ~11
chemical plants and 67 cores a minute. Whether that reads as *expensive* or
*impossible* is the first thing M0 should answer. If it is impossible, raise tier
1 toward 150 MJ — the ~1:6.7 ratio between tiers is the thing to preserve, not
the absolute number.

**O4 — Is the corridor moddable at all?**
Unverified, and two documents depend on it. See [roadmap M1](06-roadmap.md).

**O5 — Tier 3 quench.**
Deliberately deferred to a corridor-gated asteroid resource, which cannot be
specified until the corridor exists.
