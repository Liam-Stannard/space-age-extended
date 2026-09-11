# The Corridor

The route from the Solar System Edge to [the Core](04-the-core.md), **flown on
space platforms**. It is where the mod's cargo travels, where its one shared
mechanic lives, and the only place the player meets the far field.

---

## 1. What vanilla leaves out there

- **Past the midpoint of the Shattered Planet route the useful chunks stop.**
  Metallic, carbonic and oxide die away and promethium replaces them.
- **Promethium is inert.** It has no crushing recipe at all — the only entry
  vanilla gives it returns 25% of the chunk and nothing else.
- **Damage scales with speed**, so the corridor cannot be outrun.
- The Shattered Planet is not a destination; you travel toward it and turn back.

The mod does not undo any of that. It adds **one** new asteroid type and leaves
the barrenness intact — in particular, **no metallic, carbonic or oxide chunks
that far out**. Carbon, ice and ore remain freight from the inner system, which
is what keeps the corridor carrying something every hour of the endgame.

## 2. Seeding the field

The corridor's own mechanic. ([mechanics.md](mechanics.md) will carry the
full description once the mechanics are settled.)

**Same rock, two harvests.**

| Do this | Get |
|---|---|
| Shoot it plainly | The corridor's **power material** |
| Fire a **bio missile** into it first, then harvest | **Organics** — the only living material out there |

The infected asteroid is a crop rather than a mineral. Using the wrong weapon
destroys the rock and yields nothing, because our asteroid's dying effect is
terminal — the field punishes reflexes and rewards intent.

**The payload is seed stock**, the Gleba ↔ Aquilo capstone chain's frozen
culture. So the corridor's biology traces to a planet that cannot be relocated,
and the tree that makes insurance also makes ammunition.

**Why it is shaped this way:** it inverts the logistics. Instead of hauling bulk
organics two million kilometres, you ship light seed and grow heavy cargo where
it is needed.

## 3. Power out there

**Provisional.** What is built, and may yet change: the corridor's one new
asteroid is the **radiant asteroid**, whose chunk crushes to **radiant fuel**,
a fuel in its own category that only the **radiant generator** burns
(`prototypes/corridor.lua`). The generator carries a pressure ≤ 9 condition,
so it works on platforms and on the Core and nowhere else. None of it has been
played, and the names and numbers are first guesses.


## 4. Still open

- **How long the route is**, and whether it is one connection or several hops.
- **Whether parked depots are part of the design**, or the corridor is flown
  end to end.
- **Whether the radiant chain above is the answer**, or a placeholder for one.
- **The ammunition economy** — seeding costs missiles, harvesting costs ordinary
  ammunition, and both are freight until the field itself supplies them.
- **The spike**: whether a projectile can destroy an asteroid and create another
  in one trigger, and whether collectors gather the resulting chunks.
