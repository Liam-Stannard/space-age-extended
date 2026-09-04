# Roadmap

The mod is currently **one built tree, one played phase, and five documents.**
The roadmap's job is to stop that ratio getting worse.

Every milestone below has an exit criterion and a kill criterion, because a
design that cannot be falsified by playing it is not a design.

---

## Where things stand

Separating measured fact from assertion, since everything downstream depends on
which is which.

| | Status |
|---|---|
| Tree 1, phases 1–4 | Implemented; verified against the real engine over headless RCON |
| Tree 1, phase 1 | The only part a human has actually played |
| Quench Turbine + balance pass | Every number engine-measured, **none played** |
| Trees 2–5 | Subsystems firm, pairs provisional, no anchors worked out |
| The corridor | Designed on paper |
| The Core | Designed on paper, atop an unverified engine assumption |

---

## M0 — Play what exists  *(next; blocks everything)*

Playtest tree 1 end to end in a client: the refining chain at real Fulgora scrap
rates, the circuit alt-recipes against the vanilla chain, the capstone loop, and
a platform running on quench power across both tiers.

- **Exit:** the tree is enjoyable without console commands; tier 1 quench reads as
  expensive rather than impossible; the catalyst rod round-trip sustains itself.
- **Kill:** if the shipping loop is tedious at scale, the *pattern* is wrong
  rather than the tuning — and four more trees built to it would inherit the same
  problem. Stop and rework the pattern before tree 2.
- **Why it is first:** every other document assumes this tree is good. Nothing has
  tested that.

## M1 — The moddability spike  *(cheap; run alongside M0)*

Verify in the engine, not in documentation, that the corridor can exist: a
location past the Shattered Planet, a custom asteroid distribution along its
connection, distance-scaled damage, and a landable surface at the end.

- **Exit:** a throwaway mod that flies a platform out there and lands it.
- **Kill:** if it is not moddable, [04](04-corridor.md) and [05](05-the-core.md)
  are void, and the mod becomes five trees and a platform capability set — a
  smaller but entirely coherent product. Far better to learn that now than after
  tree 4.

## M2 — Tree 2, chosen to break the mould

Pick the pair whose anchor is *least* like tree 1's bulk-mineral-and-bulk-fluid
shape, and run it through the [checklist](01-principles.md#the-checklist) before
any recipe number exists.

- **Exit:** it passes the checklist on paper, then ships and is played to the M0
  bar.
- **Kill:** if the checklist can only be satisfied by inventing a placement rule,
  the pair is wrong. Try another rather than bending the shipping principle.
- **Hard constraint:** tree 2 is played before tree 3 starts. The failure this
  roadmap exists to prevent is four unplayed trees.

## M3 — Trees 3–5

Same bar, one at a time. As each capability lands, re-check it against the others
for interaction, and re-tune the Quench Turbine, since it prices everyone's
electricity.

- **Exit:** five capabilities on one platform, competing for electricity, heat,
  ice, weight and consumables in a way the player has to solve.
- **Kill:** any mandatory tree that plays as a chore gets demoted to the optional
  tier and its band re-assigned.

## M4 — The corridor

Bands, distances, hazard tuning, forward depots — built only once the
capabilities it gates on are known quantities rather than sketches.

- **Exit:** a platform dies at each band for exactly one diagnosable reason, and
  one depot hop is a satisfying build rather than a chore.
- **Tune from one measured hop**, not from lore. Distance is the whole balance
  problem.

## M5 — The Core, stage one

Land with nothing that works; survive on imported ice and cores; escape by
reversing the coolant loop into the thermal gradient.

- **Exit:** the moment the gradient tap comes online is the best moment in the
  mod.
- Stages two and three — the Dynamo, the launch loop — are planned separately,
  after stage one plays.

---

## The critical path

**M0 → M2 → M3 → M4 → M5.** Two things shorten it:

- **M1 runs in parallel and is cheap.** It can invalidate two documents in a day.
  Do it now, not last.
- **Every tree ships as playable content.** A tree is a regional loop plus a
  platform capability, worth playing before the corridor exists. The mod should
  never be in a state where the only reason to play it is a destination that
  isn't built.

What genuinely cannot be parallelised: band order is forced, since Thrust and
Power both feed on Asteroid processing's residue.

## Risk register

| Risk | Why it bites | Mitigation |
|---|---|---|
| Five single points of failure | No escape hatch: one tedious tree blocks the destination | Play each tree before starting the next; keep the band swap possible |
| Corridor not moddable | Two documents become void | M1, now |
| Content bunched behind Aquilo | Three mandatory trees plus the corridor land where most players stop | Treat "earlier is better" as a real criterion when assigning pairs |
| Scope of the Core | A planet, a megaproject, an export mechanic and a decay system, on an unplayed mod | Stage one is the deliverable; the rest are sequels |
| Design outrunning evidence | Five documents, one played phase | These exit criteria |

## What "done" means

A player who ignored the mod finishes Space Age exactly as before. A player who
built it has a corridor running in both directions that only stays solved while
they keep solving it.
