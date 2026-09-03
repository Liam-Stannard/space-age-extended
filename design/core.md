# The Core: What You Do When You Get There

Arrival is the gate, not the ending. This document covers the content on the surface, which is where the capstone items are actually spent. It picks up where [the endgame design document](endgame.md) leaves off — see that document for the corridor, the bands, and why the mandatory five trees are the ones that get a player here at all.

---

## 1. What the Core is, and what it must not become

**Not a sixth planetary tech tree.** The Core adds no new science pack, no new local material economy, no new building family. Every machine that works there was designed somewhere else, by a tree the player already built.

**A construction site, not a factory.** The Core is where the mod's capstones stop being components and become *materials*, consumed in bulk over many deliveries. The gameplay is sustained logistics at extreme range, which is the thing the whole mod has been teaching.

**The one hard rule: nothing can be made locally at first.** Not power, not fluids, not a single burner drill. Everything arrives down the corridor until the player earns local production, and earning it is stage one.

### The physics that make it distinctive

- **No fluids at all.** No water, no oil, no lava, no ice. Nothing that needs steam, cooling water or chemistry works out of the box.
- **No oxygen, so nothing burns.** Boilers, burner drills, heating towers and every combustion recipe are dead on arrival. This is the sharpest single constraint on the Core and it is physically honest.
- **The largest thermal gradient in the game.** A frozen surface over a still-hot metallic interior. The mod opened with a heat-driven generator; it ends on a body that is one enormous heat engine waiting to be tapped.
- **Absurd metal density and nothing else.** The Core is the richest ore body in the system and the poorest of everything else.

---

## 2. Stage one — Foothold

Land with nothing that works.

The first problem is power. Solar is dead this far out, combustion is impossible, and the only running generator is the Thermionic, burning Magmatic Core freighted the entire length of the corridor. That is deliberately unsustainable: it makes the opening hours of the Core a supply crisis rather than a base-building exercise.

The escape is to **run the Thermal Bus backwards.** The same fluoroketone loop that rejects heat into space on a platform will instead carry heat *out of the ground* and into generators. The mod's cooling technology becomes the Core's power source, and the moment it lands the corridor stops carrying fuel.

That single reversal is the stage-one objective and should be the first genuinely satisfying moment on the surface.

**Capstones spent:** Thermal-Shock Composite for anything built on the surface; Thermal Bus for the ground loop; Quench Turbines to bridge the gap.

---

## 3. Stage two — The Dynamo

The Core is a dead iron-nickel body that once had a magnetic field. Restarting it is the mod's megaproject.

Mechanically it is a multi-segment structure, closer to a rocket silo than to a research lab, where **each segment consumes a different tree's capstone in volume**. That is the design point: the Dynamo cannot be built by running one supply line hard. Its mandatory-tier segments require the mandatory five trees' chains operating simultaneously, at sustained rate, down a route that eats platforms. Every logistics lesson in the mod is examined at once.

Each capstone earns a ground role, and the toolkit built for space turns out to be the colonisation toolkit:

| Capstone | What it does on the Core | Tier |
|---|---|---|
| **Electrode Array** | With no water and no acid, electrolytic separation is the *only* way to refine Core ore. The refinery technology transfers to the ground wholesale | Mandatory (Asteroid processing) |
| **Thermal Bus** | Taps the gradient; also the Dynamo's own cooling | Mandatory (Power) |
| **Thermal-Shock Composite** | Every structure on a surface that swings between the two extremes | Mandatory (Structure) |
| **Deflector Field** | Ground defence against magnetic storms and ejecta thrown by the restart itself | Mandatory (Defence) |
| **Capacitor Rail Battery** | Scales up — the same technology, at planetary size, becomes stage three | Mandatory (Defence) |
| **Cryostat** | Superconducting windings need cold, and anything organic arrives frozen or not at all | Optional — cheapening tier |
| **Enriched Oxidiser** | The only oxidiser on an airless world, so any process that needs one runs on imports | Optional — cheapening tier |
| **Growth Chamber** | The sole source of organic material anywhere on the Core | Optional — cheapening tier |

The mandatory-tier segments gate whether the Dynamo can fire at all — this is where the mandatory five's [corridor bands](endgame.md#2a-the-bands--gating-by-traversal-not-by-recipe) land as ground infrastructure. The optional-tier segments don't block ignition; missing one leaves the Dynamo running, just slower to build, more failure-prone, or throttled in output. (Thrust has no Dynamo segment — its contribution is entirely to traversal, not construction, so it has nothing to spend on the ground.)

**The failure mode matters.** A half-built Dynamo should be a large, expensive, visibly incomplete thing, not a locked recipe. The player should be able to stand in it and see which segment is starving — and for an optional segment, "starving" should read as throttled, not as a wall.

---

## 4. Stage three — The reversal

The Dynamo does not fire a weapon or open a portal. It drives a **magnetic launch loop**: a planetary-scale accelerator, built from the rail battery's technology, that throws Core material to any destination in the system without rockets.

The flow reverses. For the whole mod the corridor has been a cost — everything travelling outward at enormous expense. The Dynamo turns the Core into the richest supplier in the system, and the traffic starts coming home.

That is the right shape for a Factorio endgame: the reward for solving a logistics problem is a much better logistics problem. The exported material is what feeds infinite research back on the inner planets, so the post-game loop lives at both ends of the corridor rather than only at the far one.

---

## 5. Why the corridor stays alive

A megaproject that is finished once kills every supply line that built it, and the mod's whole ethos is loops that keep running.

Two ongoing demands, both drawn from existing mechanics rather than invented:

- **The field decays.** The Dynamo needs continuous power and continuous replacement of its superconducting windings, which means cryogenics and holmium keep flowing outward forever.
- **The launch loop wears.** It is a rail at planetary scale, so it consumes ablative material exactly as platform armour does — the Vulcanus ↔ Aquilo chain never switches off.

So the endgame state is not "the Core is finished." It is a corridor running in both directions permanently, which is the same answer tree 1 reached with the Magmatic Core, applied at the largest scale the mod has.

---

## 6. Risks

**Scope.** A landable surface, a megaproject, an export mechanic and a decay system is a large amount of content for a mod whose first tree is not yet playtested. Stage one alone — land, survive on imported power, tap the gradient — is a complete and satisfying ending if the rest never gets built. Design it so that stopping there is not a truncation.

**Do not let the Core become a better Nauvis.** Infinite metal plus local power is a temptation to relocate the whole factory. The absence of fluids, combustion and biology has to be enforced hard enough that the Core is always a place you supply, never a place you retire to.

**The launch loop must not trivialise rockets.** It should export *Core* material specifically, not act as a general free cargo route between planets. If it becomes a rocket replacement, it deletes the logistics economy the entire mod is built on.

**Ejecta and storms need a real answer, not a nuisance tax.** If ground hazards are only chip damage, the Deflector's ground role is decorative. If they are severe, the player needs to be able to see them coming and build against them — the same degrade-don't-destroy rule that governs everything else.
