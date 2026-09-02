# The Endgame Destination

A final planet reached by surviving the corridor vanilla makes unsurvivable, gated on the accumulated platform capabilities from every tree. This is the endgame the [overall mod design framework](framework.md) points to from its §4.4 — see that document for the platform-capability pattern and the mandatory-five rule this document applies. What the capstones are spent on once a player actually arrives is in [design/core.md](core.md).

---

## 1. What vanilla actually does out there

Worth being exact, because the design falls out of it almost entirely.

- **The win condition is the Solar System Edge**, 100,000 km out. Everything past it is post-game.
- **The Shattered Planet is not a destination.** It does not exist as a planet any more. You travel *toward* it, achievements fire at 10,000 / 30,000 / 60,000 km, and eventually you turn back, get stranded, or die. The nominal distance is on the order of two million kilometres.
- **Roughly halfway out, the useful asteroids stop.** Metallic, carbonic and oxide chunks die away almost entirely and are replaced by promethium chunks, which yield nothing usable. A flying factory stops being able to feed itself.
- **Speed is punished.** The further out you go, the more damage you take, and going faster shreds you. You cannot outrun the corridor.
- **Promethium science needs biter eggs**, which spoil in thirty minutes, so every run is already fighting a clock.

The community reaction to this is instructive: players call it disappointing that a thing named "planet" cannot be visited.

**That is the hook.** The mod's endgame should not invent new geography. It should finish the sentence vanilla left hanging — the Shattered Planet has a **core**, the intact iron-nickel heart of the destroyed world, and it is still out there past the point where every vanilla platform turns around.

---

## 2. Why the accumulated capabilities are genuinely required

The design rule: **gate on qualitative impossibilities, not on quantity.** Anything gated on volume will be brute-forced with more railguns and a bigger hold. Every hazard below defeats a vanilla answer in kind, not in scale.

| Hazard | Why vanilla cannot answer it | Tree required |
|---|---|---|
| No usable chunks past the midpoint | Platforms are flying factories; out there the feedstock is promethium, which crushes into nothing. Carrying everything caps range at cargo capacity | **Asteroid processing** — orbital lixiviation makes promethium yield fuel, oxidiser and ammunition |
| Damage scales with speed | You cannot go fast, so the journey takes an enormous time, which multiplies every consumption rate | **Structure** — ablative hull raises the safe speed ceiling |
| A raised ceiling is useless without power to exploit it | Chemical thrust needs oxidiser you can no longer make | **Thrust** — electric propulsion, fed by the residue from lixiviation |
| Solar is nil; nuclear is heavy and weight costs speed | Power density per tonne becomes the constraint over a two-million-kilometre run | **Power** — the Thermionic Generator, tree 1's claim, becomes literally load-bearing |
| Promethium asteroids arrive in overwhelming volume | Ammunition consumption exceeds what any hold can carry | **Defence** — and the ammunition is made from the asteroids themselves |

Nothing being resupplied from a planet isn't its own hazard-tree row: it's answered by mechanics vanilla already has (platform-to-platform transfer at non-planet locations, reduced damage while stationary — §3), not by a new capstone chain. That is what makes the forward-depot corridor possible in the first place, but it doesn't count toward the mandatory five below.

Two of these interlock rather than stacking: the structure capability raises the speed ceiling and the thrust capability uses it, and neither alone shortens the journey — thrust is fed by the residue from asteroid processing's lixiviation, so it only comes online once that chain is already running. That is the shape §4.4 asks for — several capabilities required *simultaneously*, in a specific order, rather than a checklist.

**One hazard, one answer.** An earlier draft gave every hazard two answers from different pairs so that no tree became mandatory. That is now reversed: redundancy is precisely what makes a tree skippable, and the mod's own endgame is allowed to require the mod's own content. Each hazard on the corridor has exactly one solution, from exactly one tree.

The mandatory set is **five, and named**: Structure, Asteroid processing, Thrust, Power, and Defence — one tree each, one band each (§2a). Every mandatory tree is a single point of failure — if it is tedious it blocks the endgame rather than being skipped — so the remaining trees make the corridor *cheaper* rather than *possible*, and the five must be the first ones playtested.

The elegant part is the loop it creates. The corridor's defining feature is that the only thing out there is useless. The mod's answer is to make that thing the fuel, the ammunition and the propellant. You survive the promethium field by eating it.

---

## 2a. The bands — gating by traversal, not by recipe

A final technology consuming one capstone from each tree is a checklist: the player reads the tooltip, sees what is missing, and grinds it. The corridor should teach its own requirements instead, by killing platforms in specific, legible ways at specific distances. Each band removes one crutch that vanilla players rely on, and exactly one tree restores it.

| Band | What stops working | The only answer |
|---|---|---|
| **1 — past the Edge** | Impact rate outruns bot repair; hulls lose structure faster than they can be patched | **Ablative hull** (V↔A) — Structure |
| **2 — the midpoint** | Usable chunks vanish; the flying factory starves | **Electrode Array** (F↔A) — Asteroid processing |
| **3 — post-midpoint** | A raised speed ceiling is useless if exploiting it means burning chemical oxidiser you can no longer resupply | **Electric propulsion** (pair TBD), fed by the residue lixiviation already leaves behind — Thrust |
| **4 — deep field** | Solar is dead, and refining heat compounds on top of generation heat | **Thermionic Generator + Thermal Bus** (tree 1, and V↔A's second stage) — Power |
| **5 — dense field** | Chaff density exceeds any ammunition economy a hold can carry | **Deflector Field** (N↔F), with the rail battery for what the field cannot stop — Defence |
| **6 — duration** | The run is now long enough that the egg clock, floor space and the ice contest each bite | **Cryostat, Growth Chamber, Enriched Oxidiser** — the cheapening tier; **Bulk Crusher** answers floor space specifically, folding the platform's existing asteroid-crushing chain into one building so the mandatory trees' own new mechanics have room to be built |

Bands 1 to 5 are the mandatory path, one band per mandatory tree — Structure, Asteroid processing, Thrust, Power, Defence, in that order, because Thrust's fuel is a byproduct of Asteroid processing and can't come online before it. Band 6 is where the optional trees live: a player who has skipped them can still finish, but the run is longer, tighter and more expensive.

Each band must kill in one identifiable way. A platform that dies at the midpoint should run out of ammunition and propellant with a full power grid and an intact hull — so the player learns *feedstock*, not "the corridor is hard."

---

## 3. The corridor, not the ship

This is the actual new gameplay, and 2.1 is what makes it possible.

Platforms can now transfer items to each other at non-planet locations, explicitly including the solar system edge, and stationary platforms take significantly less asteroid damage. Together those make **parked forward depots** viable for the first time.

So the endgame is not a hero ship. It is a **supply corridor**: a chain of stationary refinery-depots at intervals along the route, each processing local promethium into consumables, each defended, each powered, feeding the expedition platforms that run between them. Building it is a logistics problem at a scale nothing else in the game demands. Maintaining it is the endgame.

That also solves the Magmatic Core problem — a generator fuelled from Vulcanus cannot be resupplied two million kilometres out, unless there is a chain to carry it. The depot network is what makes tree 1's fuel line reach.

---

## 4. The Core

What is actually there matters less than what is *not*.

The Core is a stripped planetary remnant: metal, vacuum, and nothing else. No water, no atmosphere, no oil, no biology, no lava, no lightning. It is **the first planet in the game that cannot be bootstrapped.** Every other world in Space Age gives you something to start with; this one gives you nothing but ore and a place to stand. Everything — power, fluids, machines, the first inserter — comes down the corridor you spent the endgame building.

That inverts the arrival pattern the player has performed four times already, and it makes the corridor the point rather than the ceremony.

Its exclusive resource should exist to feed the final technology and infinite research, not to seed a new economy. The mod should not add a sixth planetary tech tree here.

---

## 5. The final technology

Researched on the Core, and the gate is **arrival itself**. A player standing on the Core has necessarily built the ablative hull, the refinery, electric propulsion, the power and cooling chain, and the deflector, because nothing else survives the bands. There is no need to re-check that with an ingredient list, and doing so would convert a journey into an inventory audit.

The capstone items still matter, but as the *materials* the corridor consumes rather than as tokens the technology demands. That is why [the framework](framework.md#43-capstone-shippability-requirement) required capstones to be clean, stable and freely shippable — not so a final recipe could tally them, but so they could be freighted down a supply line two million kilometres long.

The one thing worth keeping from the two-layer idea: research on the Core should require something that **only exists on the Core**, so the technology cannot be completed in Nauvis orbit by a player who merely visited once. Arrival is the gate; staying is the cost.

For what it unlocks, the honest options are a genuine ending, or an infinite research fed by the Core that keeps the corridor economically alive. The second fits Factorio better — vanilla's post-game is infinite research, and an ending that switches the corridor off wastes the most interesting thing the mod built.

---

## 6. Risks

**Do not devalue vanilla's promethium.** Making promethium chunks yield usable material also makes ordinary Shattered Planet science runs easier. Restrict the lixiviation output to corridor consumables — propellant, oxidiser, ammunition — rather than anything exportable, or price it so poorly that it is only worth doing where nothing else exists.

**Do not move the win condition.** The Solar System Edge stays the game's ending. This is post-post-game, strictly additive, and a player who ignores the mod entirely still finishes Space Age normally. The mod may require its own content for its own destination; it may never touch a vanilla objective.

**Every mandatory tree is now a single point of failure.** Under the revised §2.4 there is no escape hatch: a tree that turns out to be tedious blocks the endgame rather than being skipped. Three consequences. Keep the mandatory set at five. Playtest those five before building any optional depth. And if one of them proves unfun in play, demote it to band 6 and promote a band 6 tree in its place — that swap must stay possible, so no band's hazard should be written so specifically that only one conceivable tree could ever answer it.

**Legibility is a hard requirement, not polish.** Gating by traversal only works if the player can diagnose their own death. If a platform can fail at the midpoint for three overlapping reasons at once, the corridor stops teaching and starts feeling arbitrary. Each band needs one dominant failure, tuned so it bites well before the next band's hazard is in range.

**Distance tuning is the whole balance problem.** Two million kilometres at a punished speed is an enormous real-time commitment. The corridor needs to be long enough that the depot chain is mandatory and short enough that a run is not an afternoon. That number should be set by playtesting one depot hop first, not by lore.

**Check whether the route is moddable at all.** Adding a location past the Shattered Planet, with its own asteroid distribution and a landable surface, is the single largest technical assumption in this document. Verify it before designing anything else in this file.
