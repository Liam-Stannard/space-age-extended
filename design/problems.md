# The Problem Catalogue

Twenty problems, drawn from an end-to-end vanilla Space Age playthrough and read
forward into the endgame.

**This is source material, not the selection list.** The mod creates its own
problems through [new mechanics](mechanics.md) rather than borrowing these — but
a mechanic that resonates with real friction the player already feels will land
better than one invented in a vacuum. Read this when judging whether a candidate
mechanic is about something.

A problem is listed only if vanilla leaves it unsolved or solves it expensively.
Each entry names where the player meets it, why the vanilla answer is incomplete,
and what it becomes on the way to the Core.

---

## Leaving Nauvis

**1. Every shipment costs a rocket, forever.**
Rocket parts are processing units, low density structures and rocket fuel, burnt
per launch. A one-off delivery is fine; a chain that ships *continuously* pays
this tax for the rest of the game.
*Endgame:* a supply line of corridor depots is continuous shipping by definition.

**2. A platform has to feed itself.**
Thruster fuel, oxidiser and ammunition all come from what the platform catches en
route. Stop catching and the ship stops.
*Endgame:* past the midpoint there is nothing to catch.

**3. The route decides what you get.**
Metallic, carbonic and oxide chunks arrive in whatever ratio the route gives.
Reprocessing converts between them at a loss — 40% chance of keeping what you
had, 20% each for the two alternatives.
*Endgame:* the far field offers one chunk type, and it converts to nothing.

**4. Every platform tile was launched.**
Foundation is rocket cargo. A chain that needs twenty buildings does not fit on
anything a player is willing to pay for.
*Endgame:* depots need to be compact enough to be worth parking.

**5. Space refuses most of your buildings.**
Measured at pressure 0: no boiler, no stone or steel furnace, no heating tower,
no roboport, no chest of any kind, no rocket silo, no biolab, no agricultural
tower. A platform is not a small factory — several standard approaches simply do
not exist there.
*Endgame:* every corridor structure inherits this.

**6. Several factories, no way to see them.**
After the second planet the player is running parallel bases with no
interplanetary information or control — no signals between worlds, no way to know
a remote base has stalled until a delivery fails to arrive.
*Endgame:* a corridor is the most remote base of all.

## Vulcanus

**7. There is no water.**
An entire branch of vanilla chemistry has no feedstock. Everything is re-derived
through lava, calcite and acid geysers.
*Endgame:* the Core has no fluids at all, so this is the rehearsal.

**8. The molten metals cannot leave.**
`lava`, `molten-iron` and `molten-copper` have no barrel. Vulcanus can only
export value that has already been embodied in a solid.
*Endgame:* whatever the Core receives must survive the same constraint.

**9. Calcite gates everything, and only exists here.**
Every lava process needs it, and no other world has a grain of it.

## Fulgora

**10. The outputs are chosen for you.**
Scrap yields a fixed spread: holmium in a trickle, iron and concrete and
batteries in a flood. Scaling the thing you want means drowning in the things you
do not.
*Endgame:* the corridor's only material yields whatever it yields.

**11. Power arrives as spikes.**
Lightning is capture and storage rather than generation, and the islands cap how
much of either fits.

**12. Nothing here ever lived.**
No soil, no organics, no fresh water — the one world that cannot grow anything.

## Gleba

**13. Everything is on a clock.**
Yumako mash 3 minutes, jelly 4, nutrients 5, pentapod eggs 15, biter eggs 30,
fruit 60, bioflux 120 — and **transit does not pause any of it**. A rocket is not
a fridge.
*Endgame:* the longest journey in the game, carrying things that expire.

**14. A stalled Gleba base cannot restart itself.**
Nutrients are needed to make nutrients. Lose the loop and you are hand-feeding it
back to life.
*Endgame:* a depot that stalls is weeks of travel away.

**15. There are no ore veins.**
Metal comes from bacteria that spoil into ore — the only world where mining is a
biological process on a timer.

**16. Production has a military cost.**
Spores draw pentapods, so expanding output expands the front line. It is the only
world where building more makes the game harder immediately.
*Endgame:* the field past the Edge is the same bargain at a larger scale.

## Aquilo

**17. Heat is a second logistics network.**
Everything freezes without it, heating towers burn imported fuel, and the pipes
have to reach every building before any of them work.
*Endgame:* the Core is frozen over a hot interior — the same problem inverted.

**18. Solar reads 1.**
Against 400 on Vulcanus and 100 on Nauvis. Power on Aquilo requires a whole chain
standing up before it produces a single watt.

**19. Aquilo's chemistry cannot leave.**
`ammonia`, `ammoniacal-solution`, `fluorine` and `lithium-brine` have no barrel.
A fusion cell is 5 lithium plate + 1 holmium plate + **100 ammonia**, so cells
can only be made there and freighted out.
*Endgame:* powering the corridor means hauling Aquilo's output the whole way.

**20. The field past the Edge is inert.**
Promethium chunks have **no crushing recipe** — the only entry vanilla gives them
returns 25% of the chunk and nothing else. Damage scales with speed, so it cannot
be outrun, and promethium science runs against a 30-minute egg clock.
*Endgame:* this is the wall the whole mod is built to get past.

---

## Reference: what each world lacks

| World | Has | Lacks entirely |
|---|---|---|
| Vulcanus | lava, tungsten, calcite, coal, acid geysers | water, biology, electronics feedstock |
| Fulgora | scrap, and everything out of it | soil, biology, ore veins, fresh water |
| Gleba | plants, stone, water, ore-bearing bacteria | ore veins, oil, metal of its own |
| Aquilo | crude oil, fluorine, lithium brine, ammonia, ice | solids of nearly every kind, warmth, light |

The sharpest row-pair is Fulgora and Gleba: **the world with no soil against the
world with no ore.**

## Power is not one of the five

Vanilla covers power to the Edge — solar 400 on Vulcanus, lightning on Fulgora,
fusion for Aquilo. It only becomes hard past the Edge, where there is no sun and
nothing burns, and problem 19 shows why the vanilla answer does not travel:
fusion cells are made on Aquilo or not at all.

So power is solved **on the way to the Core**, by a new asteroid type in the far
field — a material vanilla has no use for, yielding fuel for a generator that
runs where nothing else does. Corridor content, not a tree capstone. It also
gives whichever tree handles local refining a second life out there, since that
building is the natural owner of the process that makes the new chunk burnable.
