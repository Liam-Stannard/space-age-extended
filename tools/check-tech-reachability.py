#!/usr/bin/env python3
"""Can the player actually build what each technology unlocks?

The other checks in this directory answer whether the mod *loads*.
`check-data-stage.sh` proves the data stage accepts every prototype;
`check-graphics.sh` and `check-dumped-graphics.py` prove every asset path
resolves. None of them has any opinion about whether the game can be played.

This one walks the technology tree and asks, for every technology, with only its
transitive prerequisites researched: is each recipe it unlocks actually
craftable? Every ingredient obtainable, and a machine of its category buildable?

**It was written because the answer was no.** Plate smelting had been re-sourced
onto crushed kamacite so that beneficiation could not be skipped -- correct, and
one line -- but crushing runs only in the Drop Crusher, crushed kamacite and
fines are the only two routes to a kamacite plate, and the Drop Crusher cost 40
kamacite plate. The first crusher could never be built. Nothing else in the game
makes kamacite plate, so it could not be imported either, and every one of the
Core's technologies unlocked recipes that were unreachable. The mod loaded, it
passed every check in the repo, and it could not be played past the landing pad.

Thirty failures on the first run, of which that was one.

What counts as obtainable:

  * anything mined from a resource, grown as a plant, or caught as an asteroid
    chunk -- but only where a machine that works that `resource_category` can
    itself be built, which is what catches a drill priced in its own ore;
  * anything a *vanilla* recipe makes, because the Core is reached by rocket and
    the corridor can carry it. The mod's own items get no such pass;
  * anything an already-unlocked recipe makes, transitively, provided a machine
    for its category exists and is buildable.

Surface conditions are deliberately ignored. A recipe locked to gravity 0 is
made in orbit and flown down, which is the endgame's whole shape -- so "can this
be obtained" is a question about the solar system, not about one surface.

Usage: tools/check-tech-reachability.py <data-raw-dump.json>

Get the dump from tools/check-data-stage.sh, or with:
  factorio --dump-data --config <cfg> --mod-directory <dir>
"""

import collections
import json
import sys

MACHINE_TYPES = ("assembling-machine", "furnace", "rocket-silo")
MINING_TYPES = ("mining-drill",)
# Categories a player can craft in their own hands, so a recipe in one needs no
# machine at all. A fluid anywhere in the recipe rules that out, which is how
# vanilla stops anyone hand-making a processing unit.
HAND_CRAFTABLE = ("crafting", "basic-crafting", "advanced-crafting",
                  "crafting-with-fluid")


def ingredients(recipe):
    out = []
    for i in recipe.get("ingredients") or []:
        if isinstance(i, dict):
            out.append((i.get("type", "item"), i["name"]))
        else:
            out.append(("item", i[0]))
    return out


def results(proto):
    """Results of a recipe or a `minable`, in both spellings the engine accepts."""
    out = []
    for r in proto.get("results") or []:
        if isinstance(r, dict):
            out.append((r.get("type", "item"), r["name"]))
        else:
            out.append(("item", r[0]))
    if proto.get("result"):                    # singular, still used by resources
        out.append(("item", proto["result"]))
    return out


def categories(recipe):
    if recipe.get("categories"):
        return recipe["categories"]
    return [recipe["category"]] if recipe.get("category") else ["crafting"]


class Model:
    def __init__(self, dump, prefix):
        self.d = dump
        self.prefix = prefix
        self.recipes = dump["recipe"]
        self.techs = dump["technology"]
        self.fluids = set(dump.get("fluid", {}))

        self.unlocked_by = collections.defaultdict(list)
        for name, tech in self.techs.items():
            for effect in tech.get("effects") or []:
                if effect.get("type") == "unlock-recipe":
                    self.unlocked_by[effect["recipe"]].append(name)

        self.by_category = collections.defaultdict(list)
        for mtype in MACHINE_TYPES:
            for name, machine in (dump.get(mtype) or {}).items():
                for cat in machine.get("crafting_categories") or []:
                    self.by_category[cat].append(name)

        # Which drill works which resource category, so a resource is only raw
        # if something that can work it can be built.
        self.drills_for = collections.defaultdict(list)
        for mtype in MINING_TYPES:
            for name, drill in (dump.get(mtype) or {}).items():
                for cat in drill.get("resource_categories") or []:
                    self.drills_for[cat].append(name)

        self.placers = collections.defaultdict(list)
        for name, item in dump.get("item", {}).items():
            if item.get("place_result"):
                self.placers[item["place_result"]].append(name)

        self.free = self._importable()
        self.mined = self._mined()

    def _kind(self, name):
        return "fluid" if name in self.fluids else "item"

    def _importable(self):
        """Everything the corridor can carry: all of vanilla."""
        free = set()
        for name in self.d.get("item", {}):
            if not name.startswith(self.prefix):
                free.add(("item", name))
        for name in self.fluids:
            if not name.startswith(self.prefix):
                free.add(("fluid", name))
        return free

    def _mined(self):
        """(thing, the drills that could yield it) for everything in the ground."""
        out = collections.defaultdict(set)
        for name, res in (self.d.get("resource") or {}).items():
            drills = self.drills_for.get(res.get("category"), [])
            for _, thing in results(res.get("minable") or {}):
                out[(self._kind(thing), thing)].update(drills)
        # Plants are harvested and asteroid chunks are caught; neither needs a
        # drill, so both are raw outright.
        for src in ("plant", "asteroid-chunk"):
            for name, e in (self.d.get(src) or {}).items():
                if src == "asteroid-chunk":
                    out[("item", name)] = None
                for _, thing in results(e.get("minable") or {}):
                    out[(self._kind(thing), thing)] = None
        for name, tile in (self.d.get("tile") or {}).items():
            if tile.get("fluid"):
                out[("fluid", tile["fluid"])] = None
        return out

    def buildable(self, entity, have):
        return any(("item", p) in have for p in self.placers.get(entity, []))

    def machine_ok(self, recipe, have):
        cats = categories(recipe)
        if any(c in HAND_CRAFTABLE for c in cats):
            fluid = any(t == "fluid" for t, _ in
                        ingredients(recipe) + results(recipe))
            if not fluid:
                return True, None
        for cat in cats:
            for machine in self.by_category.get(cat, []):
                if self.buildable(machine, have):
                    return True, None
        candidates = [m for c in cats for m in self.by_category.get(c, [])]
        if not candidates:
            return False, "no machine anywhere has category %s" % ", ".join(cats)
        return False, "no buildable machine for %s (needs one of: %s)" % (
            ", ".join(cats), ", ".join(sorted(set(candidates))))

    def closure(self, enabled):
        """Everything obtainable with this recipe set, to a fixed point."""
        have = set(self.free)
        changed = True
        while changed:
            changed = False
            for thing, drills in self.mined.items():
                if thing in have:
                    continue
                if drills is None or any(self.buildable(d, have) for d in drills):
                    have.add(thing)
                    changed = True
            for name in enabled:
                recipe = self.recipes.get(name)
                if not recipe:
                    continue
                if not all(i in have for i in ingredients(recipe)):
                    continue
                if not self.machine_ok(recipe, have)[0]:
                    continue
                for thing in results(recipe):
                    if thing not in have:
                        have.add(thing)
                        changed = True
        return have

    def prerequisites(self, name, seen=None):
        seen = seen if seen is not None else set()
        for p in self.techs.get(name, {}).get("prerequisites") or []:
            if p not in seen:
                seen.add(p)
                self.prerequisites(p, seen)
        return seen

    def depth(self, name, memo={}):
        if name in memo:
            return memo[name]
        prereqs = self.techs.get(name, {}).get("prerequisites") or []
        memo[name] = 0 if not prereqs else 1 + max(self.depth(p) for p in prereqs)
        return memo[name]


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: check-tech-reachability.py <data-raw-dump.json>")
    prefix = sys.argv[2] if len(sys.argv) > 2 else "sae-"
    with open(sys.argv[1]) as fh:
        dump = json.load(fh)
    m = Model(dump, prefix)

    ours = [t for t in m.techs if t.startswith(prefix)]
    problems = []
    for tech in sorted(ours, key=lambda t: (m.depth(t), t)):
        available = m.prerequisites(tech) | {tech}
        enabled = {r for r in m.recipes if not r.startswith(prefix)}
        enabled |= {r for r, ts in m.unlocked_by.items()
                    if any(t in available for t in ts)}
        enabled |= {r for r, v in m.recipes.items()
                    if r.startswith(prefix) and v.get("enabled", True)}
        have = m.closure(enabled)

        for name in sorted(r for r, ts in m.unlocked_by.items() if tech in ts):
            recipe = m.recipes.get(name)
            if not recipe:
                continue
            missing = [n for t, n in ingredients(recipe) if (t, n) not in have]
            ok, note = m.machine_ok(recipe, have)
            if missing or not ok:
                problems.append((tech, name, missing, None if ok else note))

    if problems:
        print("Tech reachability FAILED: %d recipes cannot be crafted when the "
              "technology that unlocks them completes." % len(problems),
              file=sys.stderr)
        for tech, recipe, missing, note in problems:
            print("  %s -> %s" % (tech, recipe), file=sys.stderr)
            if missing:
                print("      cannot obtain: %s" % ", ".join(missing),
                      file=sys.stderr)
            if note:
                print("      %s" % note, file=sys.stderr)
        return 1

    print("Tech reachability OK -- every recipe each of the %d %s technologies "
          "unlocks can be crafted when that technology completes." %
          (len(ours), prefix.rstrip("-")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
