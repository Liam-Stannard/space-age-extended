#!/usr/bin/env python3
"""Gameplay figures from a data-raw dump: raw cost, research, loops, weight, comparison.

  python3 tools/gameplay/graph.py <data-raw-dump.json> [options]

The dump is a `factorio --dump-data` output: the knowledge base's
(knowledge-base/2.1.24/data-raw-dump.json, vanilla only) or the mod's, kept by
`tools/check-data-stage.sh --keep-dump <path>`. Standard library only. 2.1.24
recipes carry `categories` (a list); an old `category` is read as a one-item list.

Sections (all by default; --section picks some):

  cost     Raw cost of one unit of each item and fluid, down to the minable results
           of resources, plants, trees and fish, asteroid chunks and tile fluids
           (what an offshore pump takes from a tile), and the total crafting time
           at crafting speed 1. Each leaf names its kind; a leaf with no source is
           `no-route`, `loop`, or with --planet `import`.
           Route-able recipes: not hidden, not a parameter, no `recycling`
           category (the recycler's hidden `*-recycling` recipes, and
           scrap-recycling, which is not hidden), no barrelling (a filled barrel,
           subgroup `barrel`, as ingredient or product). They come in tiers, each
           in the weight ordering (below): tier 0 weight-eligible; tier 1 with
           allow_decomposition false (marked `*`); tier 2, with --planet only, the
           `recycling` recipes (marked `recycling`), since Fulgora has iron plate
           and holmium ore only that way.
           Without --planet the route is the engine's pick for the item's weight:
           the first tier-0 recipe that does not loop (need a good already being
           costed above it), whether or not it resolves to raws; with no tier-0
           recipe, the first tier-1 recipe that resolves, else the first that does
           not loop. Fluids, which the engine does not weigh, take the same
           ordering. --recipe <name> makes that recipe the route for every good it
           makes. A recipe with the good among its ingredients (a catalyst:
           kovarex, fish breeding, pentapod eggs) counts its net output, and is a
           candidate only when that is above 0. A recipe's whole cost is charged
           to the good being costed: by-products are credited nothing.
           Productivity is not applied to cost; neither are spoil results (iron
           bacteria spoiling to ore) nor burnt results, which no recipe names.
           Without --planet, raws come from every planet, so each raw found on
           only some places (the planets, and space-platform for asteroid chunks;
           by the same autoplace settings and tiles as --planet) is marked with
           them, e.g. `heavy-oil(f) 75 [raw: fulgora]`: a cost leaning on another
           planet shows.
           Every other tier-0 and tier-1 route (with --planet, also each recycling
           route that resolves) is listed beside the chosen one, with its own
           cost, its ingredients by their own routes; flags: no-decomposition,
           recycling, surface (fails --planet's surface), catalyst.
           --planet <name> (a planet, or `space-platform`): raws are what that
           planet autoplaces (resources, plants, trees, fish by entity or
           autoplace control; tile fluids by tile), or for space-platform the
           asteroid chunks; candidates are recipes whose surface_conditions it
           meets (missing properties at their surface-property default), in the
           same tiers and weight ordering. No weighting between resources. A good
           the planet makes from its own raws takes the first candidate whose
           ingredients it makes there and that resolves to its raws, ordered by
           the recycling steps beneath the recipe (fewest first), then tier, then
           weight order: recycling is a last resort, beneath a route as at the
           good, so Fulgora's iron plate is gear recycling (10 scrap), not
           smelting ore recycled from concrete (666), and Vulcanus's is casting
           (20 lava). A good it cannot make wholly from its raws, but can by a
           tier-0 or tier-1 recipe with at least one ingredient made there, takes
           the first such recipe in the same order (fewest recycling steps
           beneath, an import counting none, then tier, then weight order);
           anything else is an `import` leaf.
           (PlanetCoster.)
  tech     Per technology: depth (the longest prerequisite chain; no prerequisites
           is 0), science tier (its packs), research cost (count x packs, unit
           time, count x time); count_formula is evaluated at --level, or at the
           technology's own level (a trailing `-<n>` in its name, else 1); the
           formula reader takes numbers, L or l, + - * / ^ and parentheses, and a
           formula it cannot read or evaluate leaves the row's count empty with
           `formula_error`. Trigger technologies show their trigger instead.
  loops    Recipe loops, recycling and barrelling included, up to --loop-length
           recipes (default 3), whose yield is 1 or more at maximum productivity,
           with the productivity researches that act on their recipes. The model:
           an edge from ingredient I to product P of recipe R has yield
           expected_out(P, prod) / amount(I), where expected_out is
           probability x (amount + extra_count_fraction + prod x (amount -
           ignored_by_productivity + extra_count_fraction)) and probability is
           independent_probability x (shared_probability.max - min). prod is R's
           maximum_productivity if R allows productivity, or if an infinite
           change-recipe-productivity research names R (vanilla's
           scrap-recycling-productivity names a recipe without
           allow_productivity); a finite research gives at most the sum of its
           changes; otherwise 0. Each edge takes the best recipe between its two
           goods (by that edge's yield). A loop's yield is then found by charging
           every loop good (charge_loop): the steps run the crafts that carry one
           unit of the first good round, each loop good is charged all that any
           step takes of it, as main or side ingredient, and credited all any step
           makes of it. The yield is the first good's made/taken ratio (the goods
           in between balance at 1 unless a side ingredient or by-product moves
           them), and a loop is flagged only when it is 1 or more and no loop
           good's ratio is below 1 (`balance`; `lowest` names the lowest): at those
           crafts no loop good runs down. That is sound (a flagged loop holds) but
           not exhaustive: a loop that holds only at other crafts, or whose start
           good would give another yield, is not searched for. The loop's first
           good is its lowest by (type, name). Ingredients that are not loop goods
           are taken as free: the question is whether the loop's own goods
           multiply. A loop whose edges each use another recipe is not tried.
           Every flagged loop is listed, each marked `gain` (above 1) or
           `break-even` (1), and `catalyst` when it is one recipe making a good it
           takes, with `break_even_productivity`: the bonus, given equally to every
           step that can have productivity (the others at 0), at which the loop
           just holds: `0%` when it holds without, which is every loop no step of
           which can have productivity; `n/a` only for a loop that does not hold
           at 0 and no step of which can (break_even_productivity). The table
           title says what the yield assumes. Recycling's results are as the dump
           has them (the recycler's 25% is already in their amounts). Yields of
           1 +- 1e-9 count as 1 (break-even; vanilla's 300% cap against 25%
           recycling lands exactly there). Limits: quality is not modelled (a loop
           that upcycles quality shows only its normal-quality yield); a machine's
           own base productivity is not separated from the cap, which bounds it;
           loops longer than --loop-length are not found.
  weight   Item weight by doc-html/auxiliary/item-weight.html (2.1.24), with the
           branch it took, and items per rocket. Fluid ingredients weigh 100 per
           unit, as the page says. Where the page is silent or wrong, the rules
           below were measured in the engine (T04, 2026-11-13: every item's
           prototypes.item[...].weight over RCON for vanilla, the mod and a spike
           mod built to tell the cases apart; graph.py matches all 1073 rows):
           - The page's "rocket_lift_weight" is utility-constants'
             default_rocket_lift_weight in the weight formula (the spike set it
             to 2e6 and the silo to 4e6; weights followed the constant).
           - Items per rocket follow the rocket silo's lift_weight (default
             1000000), floor(lift_weight / weight); one figure per silo when
             silos differ.
           - Every weight, explicit ones included, is stored rounded down to a
             1/65536 step (fixed_weight); the intermediate branch's result is
             first rounded down to a whole number. The stored value is what feeds
             later weights; feeding the unrounded one gives the same 1073 rows,
             so the data does not settle which.
           - Loops: see the ordering note below.
  compare  With --compare <name> (a technology, else an item or fluid;
           `tech:`, `item:` or `fluid:` before the name picks one when it is
           more than one; a bare item-and-fluid name is the item): it beside the vanilla
           ones at the same science tier (exactly its pack set); when there are
           none, the vanilla tiers one pack away (one added or removed). Vanilla
           is every name in --vanilla <dump>; by default the knowledge base's
           dump, knowledge-base/2.1.24/data-raw-dump.json under this checkout's
           root or, since it is git-ignored and a worktree has none, under the
           main checkout's (the parent of `git rev-parse --git-common-dir`);
           with `--vanilla prefix`, or no such dump, every name not starting with
           `sae-`. The report names which. An item's
           tier is that of the shallowest technology unlocking its route recipe
           (`start` when the recipe is enabled from the start). Without
           --compare: one row per tier, vanilla only.

Weight recipe ordering: hidden recipes and those with allow_decomposition false
are skipped (the page); then, preferring each in turn: the recipe's name is the
item's; the item is not among its ingredients (not a catalyst) (both the page's);
then subgroup (group order, group name, subgroup order, subgroup name), the
recipe's order (else its main product's), and the recipe name. This departs from
the page, and was set by measurement, not taken from it: the page's "can be used
as an intermediate while hand-crafting" step and its category step were not seen
to act. Among recipes of equal subgroup and order the engine took the
alphabetically first name in all six spike cases, over category name, category
order and definition order, and over a crafting-category recipe (a chemistry one
with the earlier name won); hide_from_player_crafting made no difference. The
same ordering ranks routes in the cost section. Subgroup and order themselves were
not varied in the spike: they stand as the page has them.
Loops, also measured: when an item's recipe meets an item already being weighed,
that item takes the default weight for that one use only, nothing stored, and is
weighed properly when next asked for (the spike's t04-loop-b and -c: 1275.51, not
100); the item above it records it in `loop_defaults`. An item that still meets a
loop when weighed from the top (its only recipe takes itself) keeps the page's
default, branch `loop`; no engine row so far has been such a case. Items are weighed in
ITEM_TYPES order, each type in the dump's (definition) order; only that order with
this rule gave the engine's spike values.

Options: --json for JSON instead of text tables; --item <name> and --tech <name>
(repeatable) to narrow cost, weight and tech to those names. An item and a fluid
may share a name: a bare --item name means both, `item:<name>` or `fluid:<name>`
one.

Exits 0 with the report; 1 when a name given in an option is not in the dump, or
the dump or the --vanilla dump cannot be read; 2 on bad usage.
"""
import argparse
import json
import math
import os
import re
import statistics
import subprocess
import sys

ITEM_TYPES = (  # ItemPrototype and its descendants, prototype-api.json 2.1.24
    "item", "ammo", "capsule", "gun", "item-with-entity-data", "item-with-label",
    "item-with-inventory", "blueprint-book", "item-with-tags", "selection-tool",
    "blueprint", "copy-paste-tool", "deconstruction-item", "spidertron-remote",
    "upgrade-item", "module", "rail-planner", "space-platform-starter-pack", "tool",
    "armor", "repair-tool",
)
MOD_PREFIX = "sae-"
FLUID_INGREDIENT_WEIGHT = 100        # item-weight.html: fluid_ingredient_amount * 100
DEFAULT_ITEM_WEIGHT = 100            # UtilityConstants, when the dump lacks it
DEFAULT_LIFT_WEIGHT = 1000000        # UtilityConstants.default_rocket_lift_weight in 2.1.24
KB_DUMP = os.path.join("knowledge-base", "2.1.24", "data-raw-dump.json")   # under a repo root
EPS = 1e-9
SECTIONS = ("cost", "tech", "loops", "weight", "compare")
RAW_KINDS = ("resource", "plant", "tree", "fish", "asteroid-chunk", "tile-fluid")


def as_list(v):
    """The dump writes an empty Lua table as {}; a list stays a list."""
    if isinstance(v, list):
        return v
    return []


# ---------------------------------------------------------------- the dump

class Recipe:
    def __init__(self, name, p):
        self.name = name
        self.categories = as_list(p.get("categories")) or (
            [p["category"]] if p.get("category") else ["crafting"])
        self.energy = float(p.get("energy_required", 0.5))
        self.ingredients = [(i.get("type", "item"), i["name"], float(i["amount"]))
                            for i in as_list(p.get("ingredients"))]
        self.results = as_list(p.get("results"))
        self.hidden = bool(p.get("hidden", False))
        self.parameter = bool(p.get("parameter", False))
        self.allow_decomposition = p.get("allow_decomposition", True)
        self.allow_productivity = bool(p.get("allow_productivity", False))
        self.allow_as_intermediate = p.get("allow_as_intermediate", True)
        self.max_prod = float(p.get("maximum_productivity", 3.0))
        self.enabled = p.get("enabled", True)
        self.subgroup = p.get("subgroup")
        self.order = p.get("order")
        self.main_product = p.get("main_product")
        self.surface_conditions = as_list(p.get("surface_conditions"))

    def ingredient_names(self):
        return {n for _t, n, _a in self.ingredients}

    def products(self):
        return [(r.get("type", "item"), r["name"]) for r in self.results]


def product_expected(r, prod=0.0):
    """Expected count of one result entry per craft, at productivity `prod`."""
    if "amount" in r:
        amount = float(r["amount"])
    else:
        lo = float(r.get("amount_min", 0))
        amount = (lo + max(float(r.get("amount_max", lo)), lo)) / 2
    extra = float(r.get("extra_count_fraction", 0))
    ignored = float(r.get("ignored_by_productivity", r.get("ignored_by_stats", 0)))
    shared = r.get("shared_probability") or {}
    p = float(r.get("independent_probability", 1)) * (
        float(shared.get("max", 1)) - float(shared.get("min", 0)))
    return p * (amount + extra + prod * (max(0.0, amount - ignored) + extra))


class Dump:
    def __init__(self, raw):
        self.raw = raw
        self.items = {}
        for t in ITEM_TYPES:
            for n, p in (raw.get(t) or {}).items():
                self.items.setdefault(n, p)
        self.fluids = dict(raw.get("fluid") or {})
        self.recipes = {n: Recipe(n, p) for n, p in (raw.get("recipe") or {}).items()}
        self.techs = dict(raw.get("technology") or {})
        self.groups = raw.get("item-group") or {}
        self.subgroups = raw.get("item-subgroup") or {}
        uc = (raw.get("utility-constants") or {}).get("default") or {}
        self.default_weight = float(uc.get("default_item_weight", DEFAULT_ITEM_WEIGHT))
        self.lift = float(uc.get("default_rocket_lift_weight", DEFAULT_LIFT_WEIGHT))
        # Rocket cargo is the silo's lift_weight (default 1000000), not the constant
        self.silo_lifts = {n: float(p.get("lift_weight", DEFAULT_LIFT_WEIGHT))
                           for n, p in (raw.get("rocket-silo") or {}).items()}
        self.by_product = {}
        for r in self.recipes.values():
            if r.parameter:
                continue
            for key in dict.fromkeys(r.products()):
                self.by_product.setdefault(key, []).append(r)
        self.unlocked_by = {}
        self.prod_research = {}
        for tn, t in self.techs.items():
            for e in as_list(t.get("effects")):
                if e.get("type") == "unlock-recipe":
                    self.unlocked_by.setdefault(e.get("recipe"), []).append(tn)
                elif e.get("type") == "change-recipe-productivity":
                    self.prod_research.setdefault(e.get("recipe"), []).append(
                        (tn, float(e.get("change", 0))))

    # -- what kind of thing a name is
    def goods(self, name):
        """[(type, name)] a name stands for: `item:<n>` or `fluid:<n>` the one, a
        bare name every one there is (an item and a fluid may share a name)."""
        for prefix, typ in (("item:", "item"), ("fluid:", "fluid")):
            if name.startswith(prefix):
                n = name[len(prefix):]
                return [(typ, n)] if n in (self.items if typ == "item" else self.fluids) else []
        return ([("item", name)] if name in self.items else []) + (
            [("fluid", name)] if name in self.fluids else [])

    def proto(self, typ, name):
        return (self.fluids if typ == "fluid" else self.items).get(name) or {}

    def is_barrelling(self, r):
        for typ, name in [(t, n) for t, n, _a in r.ingredients] + r.products():
            if typ == "item" and self.items.get(name, {}).get("subgroup") == "barrel":
                return True
        return False

    def routable(self, r):
        return not (r.hidden or r.parameter or "recycling" in r.categories
                    or self.is_barrelling(r))

    # -- the weight page's recipe ordering
    def main_product_proto(self, r):
        if r.main_product:
            for typ, name in r.products():
                if name == r.main_product:
                    return self.proto(typ, name)
            return {}
        if r.main_product is None and len(r.results) == 1:
            typ, name = r.products()[0]
            return self.proto(typ, name)
        return {}

    def recipe_sort_key(self, r, item):
        """The weight ordering as measured (see the header): name, catalyst,
        subgroup, order, recipe name."""
        mp = self.main_product_proto(r)
        sg = r.subgroup or mp.get("subgroup") or "other"
        sgp = self.subgroups.get(sg) or {}
        grp = sgp.get("group") or ""
        grp_order = (self.groups.get(grp) or {}).get("order") or ""
        order = r.order if r.order is not None else (mp.get("order") or "")
        return (r.name != item, item in r.ingredient_names(),
                (grp_order, grp, sgp.get("order") or "", sg), order, r.name)

    def weight_recipes(self, item):
        rs = [r for r in self.by_product.get(("item", item), [])
              if not r.hidden and r.allow_decomposition]
        return sorted(rs, key=lambda r: self.recipe_sort_key(r, item))


# ---------------------------------------------------------------- weight

WEIGHT_STEP = 65536      # the engine keeps weights in 1/65536 steps, rounded down


def fixed_weight(x):
    """A weight as the engine stores it: rounded down to a 1/65536 step."""
    return math.floor(x * WEIGHT_STEP) / WEIGHT_STEP


def rocket_capacity(D, w):
    """{silo: items of weight w one rocket lifts}: floor(silo lift_weight / w)."""
    return {n: (math.floor(lift / w) if w > 0 else None) for n, lift in D.silo_lifts.items()}


def per_rocket(D, w):
    """Items per rocket: one figure when every silo lifts the same (or there is no
    silo: the default 1000000), else {silo: figure}."""
    cap = rocket_capacity(D, w)
    figures = set(cap.values())
    if len(figures) <= 1:
        return figures.pop() if figures else (math.floor(DEFAULT_LIFT_WEIGHT / w) if w > 0
                                              else None)
    return cap


def compute_weights(D):
    """{item: {weight, branch, recipe, loop_defaults}} by item-weight.html, with the
    engine's rounding and loop handling as measured (see the header)."""
    out = {}
    busy = set()
    sys.setrecursionlimit(max(10000, sys.getrecursionlimit()))

    def put(name, w, branch, recipe=None, loops=()):
        w = fixed_weight(w)
        out[name] = {"weight": w, "branch": branch, "recipe": recipe,
                     "loop_defaults": list(loops)}
        return w

    def weigh(name):
        """name's weight. When name's recipe meets an item already being weighed (a
        loop), the default weight for this one use, nothing stored: name is weighed
        again, properly, when next asked for."""
        if name in out:
            return out[name]["weight"]
        p = D.items.get(name, {})
        if "weight" in p:
            return put(name, float(p["weight"]), "explicit")
        flags = set(as_list(p.get("flags")))
        if {"only-in-cursor", "spawnable"} <= flags:
            return put(name, 0.0, "cursor-spawnable")
        rs = D.weight_recipes(name)
        if not rs:
            return put(name, D.default_weight, "no-recipe")
        r = rs[0]
        busy.add(name)
        recipe_weight = 0.0
        loops = []
        for typ, ing, amount in r.ingredients:
            if typ == "fluid":
                recipe_weight += amount * FLUID_INGREDIENT_WEIGHT
                continue
            if ing in busy:
                busy.discard(name)
                return D.default_weight
            recipe_weight += weigh(ing) * amount
            if ing not in out:
                loops.append(ing)    # it met a loop: weighed at the default for this use
        busy.discard(name)
        if recipe_weight == 0:
            return put(name, D.default_weight, "zero-recipe-weight", r.name, loops)
        count = sum(product_expected(x) for x in r.results if x.get("type", "item") == "item")
        if count == 0:
            return put(name, D.default_weight, "zero-product-count", r.name, loops)
        coef = float(p.get("ingredient_to_weight_coefficient", 0.5))
        stack = float(p.get("stack_size", 1)) or 1.0
        inter = recipe_weight / count * coef
        if not r.allow_productivity:
            simple = D.lift / stack
            if simple >= inter:
                return put(name, simple, "stack-size", r.name, loops)
        stacks = D.lift / inter / stack
        if stacks <= 1:
            return put(name, math.floor(inter), "intermediate", r.name, loops)
        return put(name, D.lift / math.floor(stacks) / stack, "floor", r.name, loops)

    for n in D.items:
        weigh(n)
        if n not in out:
            # weighed from the top and still meeting a loop (its recipe takes
            # itself): no later use to weigh it again, so the page's default stands
            rs = D.weight_recipes(n)
            put(n, D.default_weight, "loop", rs[0].name if rs else None)
    return out


# ---------------------------------------------------------------- raw cost

def entity_results(p):
    m = p.get("minable") or {}
    if m.get("results"):
        return [(r.get("type", "item"), r["name"]) for r in as_list(m["results"])]
    if m.get("result"):
        return [("item", m["result"])]
    return []


def raw_sources(D, planet=None):
    """{(type, name): kind} of raw goods, everywhere or on one planet / space-platform."""
    raws = {}
    controls = set()
    ents = tiles = None
    if planet is not None and planet != "space-platform":
        mg = (D.raw["planet"][planet].get("map_gen_settings") or {})
        controls = set((mg.get("autoplace_controls") or {}).keys())
        aps = mg.get("autoplace_settings") or {}
        ents = set(((aps.get("entity") or {}).get("settings") or {}).keys())
        tiles = set(((aps.get("tile") or {}).get("settings") or {}).keys())

    def placed(name, p, names):
        if planet is None:
            return True
        if planet == "space-platform":
            return False
        ctl = (p.get("autoplace") or {}).get("control")
        return name in names or (ctl is not None and ctl in controls)

    for typ, kind in (("resource", "resource"), ("plant", "plant"), ("tree", "tree"),
                      ("fish", "fish")):
        for n, p in (D.raw.get(typ) or {}).items():
            if placed(n, p, ents or set()):
                for key in entity_results(p):
                    raws.setdefault(key, kind)
    for n, p in (D.raw.get("tile") or {}).items():
        if p.get("fluid") and placed(n, p, tiles or set()):
            raws.setdefault(("fluid", p["fluid"]), "tile-fluid")
    if planet is None or planet == "space-platform":
        for p in (D.raw.get("asteroid-chunk") or {}).values():
            for key in entity_results(p):
                raws.setdefault(key, "asteroid-chunk")
    return raws


def locations(D):
    """The places --planet takes: every planet, then space-platform."""
    return list(D.raw.get("planet") or {}) + ["space-platform"]


def raw_locations(D):
    """{(type, name): [places]} where each raw good is found, by raw_sources."""
    where = {}
    for place in locations(D):
        for key in raw_sources(D, place):
            where.setdefault(key, []).append(place)
    return where


def surface_properties(D, planet):
    defaults = {n: p.get("default_value", 0)
                for n, p in (D.raw.get("surface-property") or {}).items()}
    if planet is None:
        return None
    if planet == "space-platform":
        props = ((D.raw.get("surface") or {}).get("space-platform") or {}).get("surface_properties")
    else:
        props = D.raw["planet"][planet].get("surface_properties")
    defaults.update(props or {})
    return defaults


def surface_ok(r, props):
    if props is None:
        return True
    for c in r.surface_conditions:
        v = props.get(c.get("property"), 0)
        if v < c.get("min", -math.inf) or v > c.get("max", math.inf):
            return False
    return True


class Coster:
    """Raw cost by route, without --planet: the weight's pick.

    Candidates for a good come in tiers, each in the weight ordering: 0,
    route-able and weight-eligible; 1, route-able with allow_decomposition false
    (note `*`); 2, with --planet only, the `recycling`-category recipes (note
    `recycling`). The route is the first tier-0 candidate that does
    not loop, whether or not it resolves to raws; with none, the first tier-1
    candidate that resolves, else the first that does not loop. A recipe with the
    good among its ingredients (a catalyst) counts its net output, and is used
    only when that is above 0."""

    def __init__(self, D, planet=None, overrides=()):
        self.D = D
        self.planet = planet
        self.raws = raw_sources(D, planet)
        self.props = surface_properties(D, planet)
        self.overrides = {}
        for rn in overrides:
            for key in D.recipes[rn].products():
                self.overrides[key] = D.recipes[rn]
        self.memo = {}
        self.leaf_note = {}
        self.raw_where = raw_locations(D) if planet is None else None
        self.places = locations(D)

    def tier(self, r):
        if self.D.routable(r):
            return 0 if r.allow_decomposition else 1
        if (self.planet is not None and not r.parameter
                and "recycling" in r.categories and not self.D.is_barrelling(r)):
            return 2
        return None

    def candidates(self, key, tiers=(0, 1, 2)):
        """[(tier, recipe)] making `key` (net of any catalyst), by tier, each tier in
        weight order."""
        D = self.D
        rs = [(self.tier(r), r) for r in D.by_product.get(key, [])]
        rs = [(t, r) for t, r in rs if t in tiers and self.net_count(r, key) > 0]
        return sorted(rs, key=lambda tr: (tr[0], D.recipe_sort_key(tr[1], key[1])))

    def usable(self, r):
        return surface_ok(r, self.props)

    def listed(self, tier, _r, _key):
        """Whether report() lists this candidate beside the route."""
        return tier in (0, 1)

    def out_count(self, r, key):
        return sum(product_expected(x) for x in r.results
                   if (x.get("type", "item"), x["name"]) == key)

    def net_count(self, r, key):
        return self.out_count(r, key) - sum(a for t, n, a in r.ingredients if (t, n) == key)

    def via(self, key, r, stack):
        """Cost of one `key` by recipe r: (raw {key: amount}, time, clean)."""
        n = self.net_count(r, key)
        raw, time, clean = {}, r.energy / n, True
        for t, name, amount in r.ingredients:
            if (t, name) == key:
                continue
            sub = self.unit((t, name), stack + (key,))
            clean = clean and sub["clean"]
            for k, v in sub["raw"].items():
                raw[k] = raw.get(k, 0.0) + v * amount / n
            time += sub["time"] * amount / n
        return raw, time, clean

    def resolved(self, raw):
        return all(k in self.raws for k in raw)

    def leaf(self, key, note, clean):
        self.leaf_note[key] = note
        return {"raw": {key: 1.0}, "time": 0.0, "recipe": None, "note": note, "clean": clean}

    def unit(self, key, stack=()):
        """Cost of one `key` with `stack` (the goods being costed above it).

        clean is False when the result depends on the stack (a recipe passed over
        for needing a good on it); only clean results are memoised."""
        if key in self.memo:
            return self.memo[key]
        if key in self.raws and key not in self.overrides:
            res = {"raw": {key: 1.0}, "time": 0.0, "recipe": None,
                   "note": self.raws[key], "clean": True}
            self.memo[key] = res
            return res
        if key in stack:
            return self.leaf(key, "loop", False)
        if key in self.overrides:
            raw, time, clean = self.via(key, self.overrides[key], stack)
            res = {"raw": raw, "time": time, "recipe": self.overrides[key].name,
                   "note": "--recipe", "clean": clean}
        else:
            res = self._route(key, stack)
        if res["clean"]:
            self.memo[key] = res
        return res

    def _route(self, key, stack):
        clean = True
        looped = False
        fallback = None
        for tier, r in self.candidates(key, tiers=(0, 1)):
            needs = {(t, n) for t, n, _a in r.ingredients} - {key}
            if needs & set(stack):
                looped = True
                clean = False
                continue
            raw, time, sub_clean = self.via(key, r, stack)
            clean = clean and sub_clean
            res = {"raw": raw, "time": time, "recipe": r.name,
                   "note": ("", "*")[tier], "clean": clean}
            if tier == 0 or self.resolved(raw):
                return res
            if fallback is None:
                fallback = res
        if fallback is not None:
            fallback["clean"] = clean
            return fallback
        return self.leaf(key, "loop" if looped else "no-route", clean)

    def report(self, key):
        u = self.unit(key)
        others = []
        for tier, r in self.candidates(key):
            if r.name == u["recipe"] or not self.listed(tier, r, key):
                continue
            flags = []
            if tier == 2:
                flags.append("recycling")
            elif not r.allow_decomposition:
                flags.append("no-decomposition")
            if not self.usable(r):
                flags.append("surface")
            if key in {(t, n) for t, n, _a in r.ingredients}:
                flags.append("catalyst")
            raw, time, _clean = self.via(key, r, ())
            if tier == 2 and not self.resolved(raw):
                continue   # a recycling route that does not resolve is not a route
            others.append({"recipe": r.name, "flags": flags, "raw": raw, "time": time})
        return {"name": key[1], "type": key[0], "recipe": u["recipe"], "note": u["note"],
                "raw": self.raw_rows(u["raw"]), "time": u["time"],
                "other_routes": [dict(o, raw=self.raw_rows(o["raw"])) for o in others]}

    def raw_rows(self, raw):
        """[{type, name, amount, kind[, found_on]}], largest first; kind is the raw
        source, or why the good is a leaf without one (no-route, loop, import).
        Without --planet a raw found on only some places (planets, space-platform)
        names them in found_on ([] for one autoplaced nowhere)."""
        rows = []
        for (t, n), v in sorted(raw.items(), key=lambda kv: (-kv[1], kv[0])):
            row = {"type": t, "name": n, "amount": v,
                   "kind": self.raws.get((t, n)) or self.leaf_note.get((t, n), "loop")}
            if self.raw_where is not None and (t, n) in self.raws:
                where = self.raw_where.get((t, n), [])
                if len(where) < len(self.places):
                    row["found_on"] = where
            rows.append(row)
        return rows


class PlanetCoster(Coster):
    """Raw cost on one planet (or space-platform), by the same tiers and weight
    ordering as the default route, among recipes whose surface_conditions the
    planet meets. No weighting between resources.

    A good the planet makes from its own raws (a fixpoint over those recipes,
    recycling included) takes, among the candidates whose ingredients it makes
    there, the first that resolves to the planet's raws, in the order: fewest
    recycling steps beneath the recipe (`rec_depth` of its deepest ingredient:
    0 for a raw, a recipe's own depth is its deepest ingredient's plus 1 if it
    is recycling, a good's the least of its recipes'), then tier (recycling, tier
    2, after tiers 0 and 1), then weight order; failing all, the first that does
    not loop. So recycling is a last resort twice over: beneath a route, and at
    the good. A good it cannot make wholly from its raws, but can by a
    tier-0 or tier-1 recipe with at least one ingredient it makes (in turn), takes
    the first such recipe in the same order (an import counts no recycling steps),
    its other ingredients costed by the same rules. Any
    other good is an `import` leaf."""

    def __init__(self, D, planet, overrides=()):
        super().__init__(D, planet, overrides)
        self.producible = self._producible()
        self.rec_depth = self._rec_depth()
        self.partly = self._partly_local()

    def _rec_depth(self):
        """{good: fewest nested recycling steps it needs}, over the producible goods."""
        depth = {k: 0 for k in self.raws}
        rs = [r for r in self.D.recipes.values()
              if (self.tier(r) is not None or r in self.overrides.values()) and self.usable(r)]
        changed = True
        while changed:
            changed = False
            for r in rs:
                ins = [(t, n) for t, n, _a in r.ingredients]
                if not all(k in depth for k in ins):
                    continue
                d = max((depth[k] for k in ins), default=0) + (1 if self.tier(r) == 2 else 0)
                for key in r.products():
                    if self.net_count(r, key) > 0 and d < depth.get(key, d + 1):
                        depth[key] = d
                        changed = True
        return depth

    def beneath(self, r, key):
        return max((self.rec_depth.get((t, n), 0) for t, n, _a in r.ingredients
                    if (t, n) != key), default=0)

    def _producible(self):
        have = set(self.raws)
        rs = [r for r in self.D.recipes.values()
              if (self.tier(r) is not None or r in self.overrides.values()) and self.usable(r)]
        changed = True
        while changed:
            changed = False
            for r in rs:
                if all((t, n) in have for t, n, _a in r.ingredients):
                    for key in r.products():
                        if key not in have and self.net_count(r, key) > 0:
                            have.add(key)
                            changed = True
        return have

    def _partly_local(self):
        made = set(self.producible)
        changed = True
        while changed:
            changed = False
            for key in self.D.by_product:
                if key in made:
                    continue
                for _tier, r in self.candidates(key, tiers=(0, 1)):
                    if self.usable(r) and any((t, n) in made for t, n, _a in r.ingredients
                                              if (t, n) != key):
                        made.add(key)
                        changed = True
                        break
        return made

    def makes_all(self, r, key):
        return self.usable(r) and all((t, n) in self.producible
                                      for t, n, _a in r.ingredients if (t, n) != key)

    def listed(self, tier, r, key):
        return tier in (0, 1) or (tier == 2 and self.makes_all(r, key))

    def _route(self, key, stack):
        clean = True
        looped = False
        fallback = None
        if key in self.producible:
            cands = [(self.beneath(r, key), i, tier, r)
                     for i, (tier, r) in enumerate(self.candidates(key)) if self.makes_all(r, key)]
            for _d, _i, tier, r in sorted(cands, key=lambda c: c[:2]):
                if ({(t, n) for t, n, _a in r.ingredients} - {key}) & set(stack):
                    looped = True
                    clean = False
                    continue
                raw, time, sub_clean = self.via(key, r, stack)
                clean = clean and sub_clean
                res = {"raw": raw, "time": time, "recipe": r.name,
                       "note": ("", "*", "recycling")[tier], "clean": clean}
                if self.resolved(raw):
                    return res
                if fallback is None:
                    fallback = res
            if fallback is not None:
                fallback["clean"] = clean
                return fallback
            return self.leaf(key, "loop" if looped else "no-route", clean)
        if key in self.partly:
            cands = [(self.beneath(r, key), i, tier, r)
                     for i, (tier, r) in enumerate(self.candidates(key, tiers=(0, 1)))]
            for _d, _i, tier, r in sorted(cands, key=lambda c: c[:2]):
                needs = {(t, n) for t, n, _a in r.ingredients} - {key}
                if not self.usable(r) or not needs & self.partly:
                    continue
                if needs & set(stack):
                    looped = True
                    clean = False
                    continue
                raw, time, sub_clean = self.via(key, r, stack)
                return {"raw": raw, "time": time, "recipe": r.name,
                        "note": ("", "*")[tier], "clean": clean and sub_clean}
            return self.leaf(key, "loop" if looped else "import", clean)
        return self.leaf(key, "import", True)


# ---------------------------------------------------------------- technology

_TOKEN = re.compile(r"\s*(?:(\d+(?:\.\d*)?|\.\d+)|([A-Za-z_]+)|(.))")


def eval_formula(text, level):
    """A count_formula (MathExpression): numbers, L or l, + - * / ^, parentheses."""
    toks = []
    for num, word, op in _TOKEN.findall(text):
        if num:
            toks.append(("n", float(num)))
        elif word:
            if word not in ("L", "l"):
                raise ValueError(f"unknown name {word!r} in {text!r}")
            toks.append(("n", float(level)))
        elif op.strip():
            toks.append(("o", op))
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else ("e", None)

    def take():
        t = peek()
        pos[0] += 1
        return t

    def expr():
        v = term()
        while peek() in (("o", "+"), ("o", "-")):
            v = v + term() if take()[1] == "+" else v - term()
        return v

    def term():
        v = unary()
        while peek() in (("o", "*"), ("o", "/")):
            v = v * unary() if take()[1] == "*" else v / unary()
        return v

    def unary():
        if peek() == ("o", "-"):
            take()
            return -unary()
        if peek() == ("o", "+"):
            take()
            return unary()
        return power()

    def power():
        base = atom()
        if peek() == ("o", "^"):
            take()
            return base ** unary()
        return base

    def atom():
        t = take()
        if t[0] == "n":
            return t[1]
        if t == ("o", "("):
            v = expr()
            if take() != ("o", ")"):
                raise ValueError(f"unbalanced parentheses in {text!r}")
            return v
        raise ValueError(f"unexpected {t[1]!r} in {text!r}")

    v = expr()
    if pos[0] != len(toks):
        raise ValueError(f"trailing input in {text!r}")
    if isinstance(v, complex):
        raise ValueError(f"{text!r} is not a real number at L={level}")
    return v


def tech_level(name):
    m = re.search(r"-(\d+)$", name)
    return int(m.group(1)) if m else 1


def tech_depths(D):
    depth = {}

    def walk(n, seen):
        if n in depth:
            return depth[n]
        if n in seen or n not in D.techs:
            return 0
        pre = as_list(D.techs[n].get("prerequisites"))
        d = 0 if not pre else 1 + max(walk(p, seen | {n}) for p in pre)
        depth[n] = d
        return d

    for n in D.techs:
        walk(n, frozenset())
    return depth


def pack_order(D, name):
    p = D.items.get(name, {})
    return (p.get("order") or "", name)


def tier_of_tech(D, t):
    unit = t.get("unit")
    if not unit:
        return ("trigger",)
    packs = [i[0] if isinstance(i, list) else i.get("name")
             for i in as_list(unit.get("ingredients"))]
    return tuple(sorted(packs, key=lambda n: pack_order(D, n)))


def tier_label(tier):
    return "+".join(p[:-len("-science-pack")] if p.endswith("-science-pack") else p
                    for p in tier) or "-"


def tech_row(D, name, depths, level=None):
    t = D.techs[name]
    row = {"name": name, "depth": depths.get(name, 0), "tier": list(tier_of_tech(D, t)),
           "prerequisites": as_list(t.get("prerequisites")), "max_level": t.get("max_level")}
    unit = t.get("unit")
    if not unit:
        trig = t.get("research_trigger") or {}
        row.update({"trigger": dict(trig), "count": None, "unit_time": None,
                    "packs": {}, "total_time": None, "level": None})
        return row
    lvl = level if level is not None else tech_level(name)
    unit_time = float(unit.get("time", 0))
    row.update({"trigger": None, "unit_time": unit_time, "level": lvl})
    if "count_formula" in unit:
        row["count_formula"] = unit["count_formula"]
        try:
            count = eval_formula(unit["count_formula"], lvl)
        except (ValueError, ZeroDivisionError, OverflowError) as e:
            # A formula this parser does not read, or one that does not evaluate
            # at this level: the row says so, the report goes on.
            row.update({"count": None, "packs": {}, "total_time": None,
                        "formula_error": str(e)})
            return row
    else:
        count = float(unit.get("count", 0))
    packs = {}
    for i in as_list(unit.get("ingredients")):
        pn, amt = (i[0], i[1]) if isinstance(i, list) else (i.get("name"), i.get("amount"))
        packs[pn] = count * float(amt)
    row.update({"count": count, "packs": packs, "total_time": count * unit_time})
    return row


# ---------------------------------------------------------------- loops

def reachable_productivity(D, r):
    if r.allow_productivity:
        return r.max_prod
    total = 0.0
    for tn, change in D.prod_research.get(r.name, []):
        t = D.techs.get(tn, {})
        if t.get("max_level") == "infinite":
            return r.max_prod
        lv = tech_level(tn)
        levels = (int(t["max_level"]) - lv + 1) if isinstance(t.get("max_level"), int) else 1
        total += change * max(levels, 1)
    return min(r.max_prod, total)


def recipe_flows(D, r, prod=None):
    """({good: amount in}, {good: expected out}, prod), at productivity `prod`, by
    default r's reachable productivity."""
    if prod is None:
        prod = reachable_productivity(D, r)
    ins, outs = {}, {}
    for t, n, a in r.ingredients:
        ins[(t, n)] = ins.get((t, n), 0.0) + a
    for x in r.results:
        key = (x.get("type", "item"), x["name"])
        outs[key] = outs.get(key, 0.0) + product_expected(x, prod)
    return ins, outs, prod


def charge_loop(path, flows):
    """Balance of a loop: path[i] -> path[i+1] by flows[i] = (ins, outs).

    Step i runs x_i crafts, enough to take what the step before passed on (one
    unit of path[0] to start): x_i = carried / ins_i[path[i]], carried =
    outs_i[path[i+1]] x x_i. Every loop good is then charged all that any step
    takes of it, main ingredient or side, and credited all any step makes of it.
    The goods in between balance at 1 unless a side ingredient or by-product moves
    them; path[0]'s ratio is the loop's yield.
    Returns ({good: made / taken}, path[0]'s ratio, the good with the lowest)."""
    x, carried = [], 1.0
    for i, u in enumerate(path):
        ins, outs = flows[i]
        x.append(carried / ins[u])
        carried = outs.get(path[(i + 1) % len(path)], 0.0) * x[-1]
    ratio = {}
    for g in dict.fromkeys(path):
        made = sum(xi * outs.get(g, 0.0) for xi, (_ins, outs) in zip(x, flows))
        taken = sum(xi * ins.get(g, 0.0) for xi, (ins, _outs) in zip(x, flows))
        ratio[g] = made / taken
    low = min(ratio, key=lambda g: (ratio[g], path.index(g)))
    return ratio, ratio[path[0]], low


def break_even_productivity(D, path, step_recipes):
    """The productivity bonus at which the loop just holds (charge_loop: yield 1 or
    more, no loop good below 1), given equally to every step whose recipe can have
    productivity (reachable_productivity above 0: allow_productivity, or a
    research), the other steps at 0. 0 when it holds without (whether or not
    any step can have productivity); None only when it does not and no step can
    (find_loops lists only loops that hold at maximum productivity, so that is
    None for them only if their caps are all 0). Found by bisection to 1e-6,
    from 0 to the largest cap of its steps."""
    rs = [D.recipes[rn] for rn in step_recipes]
    can = [reachable_productivity(D, r) > 0 for r in rs]

    def holds(p):
        ratio, total, low = charge_loop(path, [recipe_flows(D, r, p if c else 0.0)[:2]
                                               for r, c in zip(rs, can)])
        return total >= 1 - EPS and ratio[low] >= 1 - EPS

    if holds(0.0):
        return 0.0
    if not any(can):
        return None
    hi = max(reachable_productivity(D, r) for r, c in zip(rs, can) if c)
    if not holds(hi):
        return None
    lo = 0.0
    while hi - lo > 1e-6:
        mid = (lo + hi) / 2
        if holds(mid):
            hi = mid
        else:
            lo = mid
    return hi


def find_loops(D, max_len=3):
    best = {}   # (u, v) -> (edge yield, recipe, prod)
    flows = {}  # recipe -> (ins, outs)
    for r in D.recipes.values():
        if r.parameter or not r.ingredients:
            continue
        ins, outs, prod = recipe_flows(D, r)
        flows[r.name] = (ins, outs)
        for u, a in ins.items():
            if a <= 0:
                continue
            for v, o in outs.items():
                y = o / a
                if y > 0 and ((u, v) not in best or y > best[(u, v)][0]):
                    best[(u, v)] = (y, r.name, prod)
    nodes = sorted({u for u, _v in best} | {v for _u, v in best})
    index = {n: i for i, n in enumerate(nodes)}
    adj = {}
    for (u, v) in best:
        adj.setdefault(u, []).append(v)
    cycles = []

    def dfs(start, path):
        for v in adj.get(path[-1], []):
            if v == start:
                cycles.append(list(path))
            elif index[v] > index[start] and v not in path and len(path) < max_len:
                dfs(start, path + [v])

    for s in nodes:
        dfs(s, [s])
    rows = []
    for path in cycles:
        edges = [best[(u, path[(i + 1) % len(path)])] for i, u in enumerate(path)]
        ratio, total, low = charge_loop(path, [flows[rn] for _y, rn, _p in edges])
        if total < 1 - EPS or ratio[low] < 1 - EPS:
            continue
        steps = []
        for i, (u, (ey, rn, prod)) in enumerate(zip(path, edges)):
            v = path[(i + 1) % len(path)]
            steps.append({"from": u[1], "from_type": u[0], "to": v[1], "to_type": v[0],
                          "recipe": rn, "max_productivity": prod, "yield": ey})
        recipes = list(dict.fromkeys(s["recipe"] for s in steps))
        research = sorted({tn for rn in recipes for tn, _c in D.prod_research.get(rn, [])})
        rows.append({"goods": [u[1] for u in path], "recipes": recipes, "steps": steps,
                     "yield": total, "lowest": low[1],
                     "balance": {g[1]: v for g, v in ratio.items()},
                     "kind": "gain" if total > 1 + EPS else "break-even",
                     "catalyst": len(path) == 1, "productivity_research": research,
                     "break_even_productivity": break_even_productivity(
                         D, path, [s["recipe"] for s in steps])})
    rows.sort(key=lambda r: (-round(r["yield"], 9), len(r["goods"]), r["goods"]))
    return rows


# ---------------------------------------------------------------- comparison

def item_tier(D, coster, depths, key):
    u = coster.unit(key)
    if u["recipe"] is None:
        return ("raw",) if u["note"] in RAW_KINDS else ("-",)
    r = D.recipes[u["recipe"]]
    techs = D.unlocked_by.get(r.name, [])
    if r.enabled is not False and not techs:
        return ("start",)
    if not techs:
        return ("-",)
    best = min(techs, key=lambda t: (depths.get(t, 0), t))
    return tier_of_tech(D, D.techs[best])


def raw_totals(raw):
    """(raw item units, raw fluid units) of a unit() raw map."""
    items = sum(v for (t, _n), v in raw.items() if t == "item")
    fluids = sum(v for (t, _n), v in raw.items() if t == "fluid")
    return items, fluids


def spread(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return {"n": len(vals), "min": min(vals), "median": statistics.median(vals), "max": max(vals)}


def per_rocket_least(D, w):
    """The smallest per-rocket figure over the silos, for comparing items."""
    pr = per_rocket(D, w) if w else None
    return min(v for v in pr.values() if v is not None) if isinstance(pr, dict) else pr


def item_compare_row(D, coster, weights, depths, key):
    u = coster.unit(key)
    ri, rf = raw_totals(u["raw"])
    item = key[0] == "item"
    w = weights.get(key[1], {}).get("weight") if item else None
    return {"name": key[1], "type": key[0], "tier": list(item_tier(D, coster, depths, key)),
            "recipe": u["recipe"], "raw_items": ri, "raw_fluids": rf, "time": u["time"],
            "weight": w, "stack_size": D.items[key[1]].get("stack_size") if item else None,
            "per_rocket": per_rocket_least(D, w)}


def split_compare(D, name):
    """('tech', name) or ('good', name) for --compare: a technology when the name
    is one, unless prefixed `item:` or `fluid:` (kept, for Dump.goods); `tech:`
    forces a technology. A bare name that is both an item and a fluid is the item."""
    if name.startswith("tech:"):
        return "tech", name[len("tech:"):]
    if name.startswith(("item:", "fluid:")):
        return "good", name
    return ("tech" if name in D.techs else "good"), name


def compare(D, coster, weights, depths, name, vanilla, level):
    def is_vanilla(n):
        return n in vanilla if vanilla is not None else not n.startswith(MOD_PREFIX)

    if name is None:
        tiers = {}
        for tn, t in D.techs.items():
            if is_vanilla(tn) and not D.techs[tn].get("hidden"):
                tiers.setdefault(tier_of_tech(D, t), []).append(tech_row(D, tn, depths, level))
        items = {}
        for n, p in D.items.items():
            if is_vanilla(n) and not p.get("hidden") and not p.get("parameter"):
                items.setdefault(item_tier(D, coster, depths, ("item", n)), []).append(
                    item_compare_row(D, coster, weights, depths, ("item", n)))
        rows = []
        for tier in sorted(set(tiers) | set(items), key=lambda k: (len(k), k)):
            trs, irs = tiers.get(tier, []), items.get(tier, [])
            rows.append({"tier": list(tier), "techs": len(trs),
                         "depth": spread([r["depth"] for r in trs]),
                         "count": spread([r["count"] for r in trs]),
                         "total_time": spread([r["total_time"] for r in trs]),
                         "items": len(irs), "raw_items": spread([r["raw_items"] for r in irs])})
        return {"subject": None, "tiers": rows}
    kind, name = split_compare(D, name)
    if kind == "tech":
        me = tech_row(D, name, depths, level)
        cols = ("depth", "count", "unit_time", "total_time")
        groups = {}
        for tn, t in D.techs.items():
            if tn != name and is_vanilla(tn) and not t.get("hidden"):
                groups.setdefault(tier_of_tech(D, t), []).append(tech_row(D, tn, depths, level))
        order = (lambda r: (r["depth"], r["name"]))
        return dict(peer_report(me, groups, cols, order), kind="technology")
    key = D.goods(name)[0]
    me = item_compare_row(D, coster, weights, depths, key)
    groups = {}
    for n, p in D.items.items():
        if ("item", n) == key or not is_vanilla(n) or p.get("hidden") or p.get("parameter"):
            continue
        groups.setdefault(item_tier(D, coster, depths, ("item", n)), []).append(
            item_compare_row(D, coster, weights, depths, ("item", n)))
    cols = ("raw_items", "raw_fluids", "time", "weight", "per_rocket")
    return dict(peer_report(me, groups, cols, lambda r: (r["raw_items"], r["name"])),
                kind="item")


SPECIAL_TIERS = {("trigger",), ("start",), ("raw",), ("-",)}


def peer_report(me, groups, cols, order):
    """The subject beside the vanilla rows at exactly its tier (its pack set), or,
    when there are none, the vanilla tiers one pack away (one added or removed)."""
    tier = tuple(me["tier"])
    peers = sorted(groups.get(tier, []), key=order)
    out = {"subject": me, "peers": peers,
           "summary": {k: spread([p[k] for p in peers]) for k in cols}, "near_tiers": []}
    if peers or tier in SPECIAL_TIERS:
        return out
    mine = set(tier)
    for other, rows in sorted(groups.items(), key=lambda kv: (len(kv[0]), kv[0])):
        if other in SPECIAL_TIERS or len(mine ^ set(other)) != 1:
            continue
        (pack,) = mine ^ set(other)
        out["near_tiers"].append({
            "tier": list(other), "change": ("+" if pack in other else "-") + pack,
            "peers": [r["name"] for r in sorted(rows, key=order)],
            "summary": {k: spread([r[k] for r in rows]) for k in cols}})
    return out


# ---------------------------------------------------------------- output

def fmt(v):
    if v is None:
        return "-"
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
        return f"{v:.4g}" if abs(v) < 1e5 else f"{v:.6g}"
    return str(v)


def fmt_rocket(v):
    if isinstance(v, dict):
        return ", ".join(f"{silo} {fmt(n)}" for silo, n in v.items())
    return fmt(v)


def raw_text(rows):
    if rows is None:
        return "-"
    def note(r):
        if r["kind"] not in RAW_KINDS:
            return f" [{r['kind']}]"
        if "found_on" in r:
            return f" [raw: {', '.join(r['found_on']) or 'autoplaced nowhere'}]"
        return ""
    return ", ".join(f"{r['name']}{'(f)' if r['type'] == 'fluid' else ''} {fmt(r['amount'])}"
                     + note(r) for r in rows)


def table(title, head, rows):
    lines = [f"== {title} ({len(rows)} rows)"]
    if not rows:
        lines.append("(none)")
        return lines
    widths = [len(h) for h in head]
    for r in rows:
        for i, c in enumerate(r[:-1]):
            widths[i] = min(max(widths[i], len(c)), 48)
    def line(cells):
        return "  ".join(c.ljust(widths[i]) if i < len(cells) - 1 else c
                         for i, c in enumerate(cells)).rstrip()
    lines.append(line(head))
    lines.extend(line(r) for r in rows)
    return lines


def spread_text(s):
    if not s:
        return "-"
    return f"{fmt(s['min'])}/{fmt(s['median'])}/{fmt(s['max'])}"


def text_report(rep):
    out = [f"dump: {rep['dump']}  planet: {rep['planet'] or 'all'}  "
           f"recipe overrides: {', '.join(rep['recipe_overrides']) or 'none'}"]
    if "compare" in rep["sections"]:
        out.append(f"vanilla: {rep['vanilla']}")
    s = rep["sections"]
    if "cost" in s:
        rows = []
        for c in s["cost"]:
            route = (c["recipe"] or f"({c['note']})") + (
                f" {c['note']}" if c["recipe"] and c["note"] else "")
            rows.append([c["name"] + ("(f)" if c["type"] == "fluid" else ""), route,
                         fmt(c["time"]), raw_text(c["raw"])])
            for o in c["other_routes"]:
                flags = f" [{','.join(o['flags'])}]" if o["flags"] else ""
                rows.append(["", "  or " + o["recipe"] + flags, fmt(o["time"]),
                             raw_text(o["raw"])])
        out += table("raw cost per unit (time: s at crafting speed 1; (f) fluid; "
                     "* not weight-eligible)", ["good", "route", "time", "raw"], rows)
    if "tech" in s:
        rows = []
        for t in s["tech"]:
            if t["trigger"] is not None:
                cost = "trigger " + ", ".join(f"{k}={v}" for k, v in t["trigger"].items()
                                              if k != "type") + f" ({t['trigger'].get('type')})"
            else:
                formula = t.get("count_formula")
                cost = (f"{fmt(t['count'])} x {fmt(t['unit_time'])}s = {fmt(t['total_time'])}s"
                        + (f" (L={t['level']}: {formula})" if formula else ""))
                if t.get("formula_error"):
                    cost = (f"count_formula {formula!r} not evaluated at L={t['level']}: "
                            f"{t['formula_error']}")
            rows.append([t["name"], str(t["depth"]), tier_label(t["tier"]), cost])
        out += [""] + table("technology (depth: longest prerequisite chain)",
                            ["technology", "depth", "tier", "cost (count x unit time)"], rows)
    if "loops" in s:
        rows = []
        for lp in s["loops"]:
            chain = " -> ".join(f"{st['from']} [{st['recipe']} {fmt(st['yield'])}]"
                                for st in lp["steps"]) + f" -> {lp['goods'][0]}"
            bep = lp["break_even_productivity"]
            rows.append([f"{lp['yield']:.6g}", "n/a" if bep is None else f"{bep * 100:.0f}%",
                         lp["kind"] + (" (catalyst)" if lp["catalyst"] else ""),
                         lp["lowest"], ", ".join(lp["productivity_research"]) or "-", chain])
        out += [""] + table(f"recipe loops with yield >= 1, up to {rep['loop_length']} recipes: "
                            "yield at each recipe's maximum_productivity, every loop good "
                            "charged, other ingredients free; break-even: the productivity "
                            "bonus, on every step that can have it, at which the loop holds "
                            "([recipe edge yield])",
                            ["yield", "break-even", "kind", "lowest good",
                             "productivity research", "loop"], rows)
    if "weight" in s:
        rows = [[w["name"], fmt(w["weight"]),
                 w["branch"] + (f" (loop default: {', '.join(w['loop_defaults'])})"
                                if w.get("loop_defaults") else ""), w["recipe"] or "-",
                 fmt(w["stack_size"]), fmt_rocket(w["per_rocket"])] for w in s["weight"]]
        silos = ", ".join(f"{n} {fmt(v)}" for n, v in rep["silo_lift_weights"].items()) or "none"
        out += [""] + table(f"item weight (weight formula's lift: default_rocket_lift_weight "
                            f"{fmt(rep['lift_weight'])}; per rocket: silo lift_weight, {silos})",
                            ["item", "weight", "branch", "recipe", "stack", "per rocket"], rows)
    if "compare" in s:
        c = s["compare"]
        out.append("")
        if c["subject"] is None:
            rows = [[tier_label(t["tier"]), str(t["techs"]), spread_text(t["depth"]),
                     spread_text(t["count"]), spread_text(t["total_time"]), str(t["items"]),
                     spread_text(t["raw_items"])] for t in c["tiers"]]
            out += table("vanilla technologies and items by science tier (min/median/max)",
                         ["tier", "techs", "depth", "count", "count x time (s)", "items",
                          "raw item units"], rows)
        else:
            tech = c["kind"] == "technology"
            cols = (("depth", "count", "unit_time", "total_time") if tech else
                    ("raw_items", "raw_fluids", "time", "weight", "per_rocket"))
            what = "technologies" if tech else "items"
            me = c["subject"]
            mark = "(f)" if me.get("type") == "fluid" else ""
            rows = [[me["name"] + mark + " (subject)"] + [fmt(me[k]) for k in cols]]
            rows.append(["vanilla min/median/max"] + [spread_text(c["summary"][k]) for k in cols])
            rows += [[p["name"]] + [fmt(p[k]) for k in cols] for p in c["peers"]]
            out += table(f"{me['name']} beside vanilla {what} at tier {tier_label(me['tier'])}",
                         ["technology" if tech else "item"] + list(cols), rows)
            if not c["peers"]:
                out.append(f"no vanilla {'technology' if tech else 'item'} has exactly this pack"
                           " set; the vanilla tiers one pack away:")
                near = [[t["change"], str(len(t["peers"]))]
                        + [spread_text(t["summary"][k]) for k in cols] + [tier_label(t["tier"])]
                        for t in c["near_tiers"]]
                out += table("tiers one pack away (min/median/max)",
                             ["pack", "n"] + list(cols) + ["tier"], near)
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- main

def load_dump(path):
    """A Dump from a data-raw-dump.json; OSError or ValueError (bad JSON) if not."""
    with open(path, encoding="utf-8") as f:
        return Dump(json.load(f))


def kb_dump_under(root):
    """The knowledge base's vanilla dump under a repo root, or None."""
    path = os.path.join(root, KB_DUMP)
    return path if os.path.isfile(path) else None


def default_vanilla_dump():
    """The KB dump for --vanilla's default. It is git-ignored, so a worktree has
    none: look under this checkout's root (two up from this file), then under the
    main checkout's, which is the parent of `git rev-parse --git-common-dir`."""
    here = os.path.dirname(os.path.abspath(__file__))
    roots = [os.path.dirname(os.path.dirname(here))]
    try:
        common = subprocess.run(
            ["git", "-C", here, "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, timeout=10, check=True).stdout.strip()
        roots.append(os.path.dirname(common))
    except (OSError, subprocess.SubprocessError):
        pass
    for root in roots:
        path = kb_dump_under(root)
        if path:
            return path
    return None


def build(D, args, vanilla=None):
    coster = (PlanetCoster(D, args.planet, args.recipe) if args.planet
              else Coster(D, None, args.recipe))
    rep = {"dump": args.dump, "planet": args.planet, "recipe_overrides": list(args.recipe),
           "lift_weight": D.lift, "silo_lift_weights": D.silo_lifts,
           "default_item_weight": D.default_weight,
           "loop_length": args.loop_length,
           "vanilla": getattr(args, "vanilla_source", f"names not starting with {MOD_PREFIX}"),
           "sections": {}}
    sections = args.section or list(SECTIONS)
    weights = compute_weights(D) if ("weight" in sections or "compare" in sections) else {}
    depths = tech_depths(D)
    if "cost" in sections:
        keys = ([k for n in args.item for k in D.goods(n)] if args.item else
                [("item", n) for n, p in D.items.items() if not p.get("parameter")]
                + [("fluid", n) for n, p in D.fluids.items() if not p.get("parameter")])
        rep["sections"]["cost"] = [coster.report(k) for k in dict.fromkeys(keys)]
    if "tech" in sections:
        names = args.tech or list(D.techs)
        rep["sections"]["tech"] = [tech_row(D, n, depths, args.level) for n in names]
    if "loops" in sections:
        rep["sections"]["loops"] = find_loops(D, args.loop_length)
    if "weight" in sections:
        names = ([k[1] for n in args.item for k in D.goods(n) if k[0] == "item"]
                 if args.item else list(D.items))
        rows = []
        for n in dict.fromkeys(names):
            w = weights[n]
            rows.append({"name": n, "weight": w["weight"], "branch": w["branch"],
                         "recipe": w["recipe"], "stack_size": D.items[n].get("stack_size"),
                         "per_rocket": per_rocket(D, w["weight"]),
                         "loop_defaults": w["loop_defaults"]})
        rep["sections"]["weight"] = rows
    if "compare" in sections:
        rep["sections"]["compare"] = compare(D, coster, weights, depths, args.compare,
                                             vanilla, args.level)
    return rep


def parse_args(argv):
    ap = argparse.ArgumentParser(
        prog="graph.py", description="Gameplay figures from a data-raw dump (see the header).")
    ap.add_argument("dump", help="path to data-raw-dump.json")
    ap.add_argument("--json", action="store_true", help="JSON instead of text tables")
    ap.add_argument("--section", action="append", choices=SECTIONS,
                    help="report only this section (repeatable; default all)")
    ap.add_argument("--item", action="append", default=[],
                    help="narrow cost and weight to this item or fluid (repeatable; "
                    "item:NAME or fluid:NAME when it is both)")
    ap.add_argument("--tech", action="append", default=[],
                    help="narrow tech to this technology (repeatable)")
    ap.add_argument("--recipe", action="append", default=[],
                    help="use this recipe as the route for what it makes (repeatable)")
    ap.add_argument("--planet", help="cost with only this planet's raws and surface "
                    "(a planet, or space-platform)")
    ap.add_argument("--level", type=int, help="level for count_formula (default: each "
                    "technology's own)")
    ap.add_argument("--compare", metavar="NAME", help="an item or technology to set beside "
                    "vanilla's at its science tier (item:NAME or tech:NAME when it is both)")
    ap.add_argument("--vanilla", metavar="DUMP|prefix",
                    help="what is vanilla for compare: every name in this dump (default: the "
                    "knowledge base's, found from the repo root); `prefix`, or no KB dump: every "
                    "name not starting with sae-")
    ap.add_argument("--loop-length", type=int, default=3,
                    help="longest loop searched, in recipes (default 3)")
    args = ap.parse_args(argv)
    if args.loop_length < 1:
        ap.error("--loop-length must be at least 1")
    return args


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        D = load_dump(args.dump)
    except (OSError, ValueError) as e:
        print(f"graph.py: cannot read the dump {args.dump!r}: {e}", file=sys.stderr)
        return 1
    errors = []
    for n in args.item:
        if not D.goods(n):
            errors.append(f"no item or fluid {n!r}")
    errors += [f"no technology {n!r}" for n in args.tech if n not in D.techs]
    errors += [f"no recipe {n!r}" for n in args.recipe if n not in D.recipes]
    planets = D.raw.get("planet") or {}
    if args.planet and args.planet != "space-platform" and args.planet not in planets:
        errors.append(f"no planet {args.planet!r} (planets: "
                      f"{', '.join(D.raw.get('planet') or {})}, or space-platform)")
    if args.compare:
        kind, name = split_compare(D, args.compare)
        if (kind == "tech" and name not in D.techs) or (kind == "good" and not D.goods(name)):
            errors.append(f"no {'technology' if kind == 'tech' else 'item or fluid'} {name!r}")
    if errors:
        print("graph.py: " + "; ".join(errors), file=sys.stderr)
        return 1
    vanilla = None
    args.vanilla_source = f"names not starting with {MOD_PREFIX}"
    if "compare" in (args.section or SECTIONS) and args.vanilla != "prefix":
        path = args.vanilla or default_vanilla_dump()
        if path:
            try:
                V = load_dump(path)
            except (OSError, ValueError) as e:
                print(f"graph.py: cannot read the --vanilla dump {path!r}: {e}", file=sys.stderr)
                return 1
            vanilla = set(V.items) | set(V.fluids) | set(V.techs)
            args.vanilla_source = path
    rep = build(D, args, vanilla)
    if args.json:
        json.dump(rep, sys.stdout, indent=1, sort_keys=False)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(text_report(rep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
