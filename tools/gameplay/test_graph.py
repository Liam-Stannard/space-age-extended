#!/usr/bin/env python3
"""tools/gameplay/graph.py against small fixture dumps, built inline below.

  python3 tools/gameplay/test_graph.py [-v]

Each case is a label, what graph.py gives on a fixture, and what it must give:
raw cost on a fixture with a known answer (and --recipe, --planet, a catalyst);
each branch of the item-weight algorithm (doc-html/auxiliary/item-weight.html,
2.1.24) and each step of its recipe ordering; a loop whose yield at maximum
productivity is above 1 flagged, one below 1 not; technology depth and tier on a
fixture tree, and count_formula; and the command line end to end (--json, every
section non-empty, exit 1 on an unknown name). The fixtures hold only the keys
graph.py reads, in the dump's shapes (`categories` lists, ingredients as tables).
-v prints every case, not only the failures.

Exits 0 when every case comes out as listed, 1 naming those that do not.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True     # no __pycache__ beside the tool
sys.path.insert(0, HERE)
import graph  # noqa: E402  (the module under test, beside this file)

GRAPH = os.path.join(HERE, "graph.py")


# ---------------------------------------------------------------- fixture building

def item(name, stack=100, **kw):
    p = {"type": "item", "name": name, "stack_size": stack, "subgroup": "sg-a", "order": name}
    p.update(kw)
    return p


def recipe(name, ingredients, results, **kw):
    """ingredients/results: [(name, amount)] items, (name, amount, 'fluid'), or a dict
    as the dump has it."""
    def entry(t):
        if isinstance(t, dict):
            return t
        return {"type": t[2] if len(t) > 2 else "item", "name": t[0], "amount": t[1]}
    p = {"type": "recipe", "name": name, "ingredients": [entry(i) for i in ingredients],
         "results": [entry(r) for r in results]}
    p.update(kw)
    return p


def dump(items=(), recipes=(), techs=(), fluids=(), resources=(), extra=None):
    raw = {
        "utility-constants": {"default": {"default_item_weight": 100,
                                          "default_rocket_lift_weight": 1000000}},
        "character": {"character": {"crafting_categories": ["crafting", "hand-crafting"]}},
        "recipe-category": {c: {"name": c} for c in
                            ("crafting", "smelting", "alpha", "beta", "recycling", "chemistry")},
        "item-group": {"g1": {"name": "g1", "order": "a"}, "g2": {"name": "g2", "order": "b"}},
        "item-subgroup": {"sg-a": {"name": "sg-a", "group": "g1", "order": "a"},
                          "sg-b": {"name": "sg-b", "group": "g1", "order": "b"},
                          "sg-late": {"name": "sg-late", "group": "g2", "order": "a"}},
        "item": {p["name"]: p for p in items},
        "fluid": {p["name"]: p for p in fluids},
        "recipe": {p["name"]: p for p in recipes},
        "technology": {p["name"]: p for p in techs},
        "resource": {r: {"name": r, "minable": {"result": r}} for r in resources},
    }
    for k, v in (extra or {}).items():
        raw.setdefault(k, {}).update(v)
    return graph.Dump(raw)


def args_for(dump_path, *argv):
    return graph.parse_args([dump_path, *argv])


# ---------------------------------------------------------------- fixtures

def circuit_dump():
    """iron/copper ore -> plates -> cable -> circuit, as vanilla's numbers.
    Circuit: 1 iron ore + 1.5 copper ore; time 0.5 + 3.2 + 3 x (0.25 + 1.6) = 9.25 s."""
    return dump(
        items=[item("iron-ore", 50), item("copper-ore", 50), item("iron-plate"),
               item("copper-plate"), item("copper-cable", 200), item("electronic-circuit", 200),
               item("egg"), item("food"), item("dual"), item("slag"), item("junk"),
               item("gear"), item("concrete"), item("mix")],
        fluids=[{"name": "lava", "subgroup": "sg-a", "order": "l"},
                {"name": "dual", "subgroup": "sg-a", "order": "d"}],
        resources=["iron-ore", "copper-ore", "food", "junk"],
        recipes=[
            recipe("iron-plate", [("iron-ore", 1)], [("iron-plate", 1)],
                   categories=["smelting"], energy_required=3.2, allow_productivity=True),
            recipe("copper-plate", [("copper-ore", 1)], [("copper-plate", 1)],
                   categories=["smelting"], energy_required=3.2, allow_productivity=True),
            recipe("copper-cable", [("copper-plate", 1)], [("copper-cable", 2)]),
            recipe("electronic-circuit", [("iron-plate", 1), ("copper-cable", 3)],
                   [("electronic-circuit", 1)]),
            recipe("casting-iron", [("lava", 20, "fluid")], [("iron-plate", 2)],
                   categories=["smelting"], energy_required=3.2, allow_decomposition=False,
                   surface_conditions=[{"property": "pressure", "min": 4000, "max": 4000}]),
            recipe("iron-plate-recycling", [("iron-plate", 1)],
                   [("iron-plate", 1)], categories=["recycling"], hidden=True),
            recipe("egg-breeding", [("egg", 2), ("food", 1)], [("egg", 3)],
                   categories=["chemistry"], energy_required=6),
            # only a no-decomposition recipe makes slag
            recipe("slag", [("iron-ore", 1)], [("slag", 1)], allow_decomposition=False),
            # junk (planet `dump`): junk-recycling gives gear and concrete; gear recycles
            # to plate; concrete recycles to ore, which smelts to plate. The ordering
            # alone would take iron-plate (tier 0) via ore from concrete recycling; the
            # fewer recycling steps beneath gear-recycling win instead.
            recipe("junk-recycling", [("junk", 1)],
                   [{"type": "item", "name": "gear", "amount": 1, "independent_probability": 0.2},
                    {"type": "item", "name": "concrete", "amount": 1,
                     "independent_probability": 0.1}],
                   categories=["recycling", "hand-crafting"]),
            recipe("gear", [("iron-plate", 2)], [("gear", 1)], allow_productivity=True),
            recipe("concrete", [("iron-ore", 1)], [("concrete", 10)]),
            recipe("gear-recycling", [("gear", 1)],
                   [{"type": "item", "name": "iron-plate", "amount": 0,
                     "extra_count_fraction": 0.5}], categories=["recycling"], hidden=True),
            recipe("concrete-recycling", [("concrete", 1)],
                   [{"type": "item", "name": "iron-ore", "amount": 0,
                     "extra_count_fraction": 0.025}], categories=["recycling"], hidden=True),
            # mix, on `dump`, needs an import either way (lava, copper plate): aa-mix,
            # first by weight order, takes ore that is 2 recycling steps deep there;
            # ab-mix takes junk itself (0 steps), so Q50's order takes ab-mix.
            recipe("aa-mix", [("iron-ore", 1), ("lava", 1, "fluid")], [("mix", 1)]),
            recipe("ab-mix", [("junk", 1), ("copper-plate", 1)], [("mix", 1)]),
            # an item and a fluid sharing a name
            recipe("dual", [("iron-plate", 2)], [("dual", 1)]),
            recipe("dual-fluid", [("lava", 10, "fluid")], [("dual", 5, "fluid")],
                   categories=["chemistry"]),
        ],
        extra={
            "tile": {"lava": {"name": "lava", "fluid": "lava"}},
            "surface-property": {"pressure": {"name": "pressure", "default_value": 1000}},
            "planet": {
                "home": {"name": "home", "surface_properties": {"pressure": 1000},
                         "map_gen_settings": {"autoplace_settings": {"entity": {"settings": {
                             "iron-ore": {}, "copper-ore": {}, "food": {}}}}}},
                "hot": {"name": "hot", "surface_properties": {"pressure": 4000},
                        "map_gen_settings": {"autoplace_settings": {"tile": {"settings": {
                            "lava": {}}}}}},
                "dump": {"name": "dump", "surface_properties": {"pressure": 1000},
                         "map_gen_settings": {"autoplace_settings": {"entity": {"settings": {
                             "junk": {}}}}}},
            },
        })


def weight_dump():
    lift_items = [
        item("plate", 100, weight=1000),
        item("cable", 200, weight=250),
        item("heavy", 10, weight=1000000),
        item("cursor-thing", 1, flags=["only-in-cursor", "spawnable"]),
        item("orphan", 50),
        item("loop-a", 100), item("loop-b", 100),
        item("from-nothing", 100),
        item("never-made", 100),
        item("circuit", 200, ingredient_to_weight_coefficient=0.28),
        item("crate", 10),
        item("monolith", 10),
        item("brew", 100),
        item("hidden-only", 100),
        item("self-loop", 100),
    ]
    rs = [
        recipe("loop-a", [("loop-b", 1)], [("loop-a", 1)], allow_productivity=True),
        recipe("loop-b", [("loop-a", 1)], [("loop-b", 1)], allow_productivity=True),
        recipe("from-nothing", [], [("from-nothing", 1)]),
        recipe("never-made", [("plate", 1)],
               [{"type": "item", "name": "never-made", "amount": 1, "independent_probability": 0}]),
        recipe("circuit", [("plate", 1), ("cable", 3)], [("circuit", 1)], allow_productivity=True),
        recipe("crate", [("plate", 1)], [("crate", 1)]),
        recipe("monolith", [("heavy", 2)], [("monolith", 1)], allow_productivity=True),
        recipe("brew", [("water", 10, "fluid")], [("brew", 1)], allow_productivity=True),
        recipe("hidden-only", [("plate", 1)], [("hidden-only", 1)], hidden=True),
        recipe("hidden-only-b", [("plate", 1)], [("hidden-only", 1)], allow_decomposition=False),
        recipe("self-loop", [("self-loop", 2), ("plate", 1)], [("self-loop", 3)]),
    ]
    return dump(items=lift_items, recipes=rs, fluids=[{"name": "water"}])


def order_dump():
    """One item per ordering step; recipe `zz-*` would lose on name alone."""
    its = [item(n) for n in ("ing", "named", "cat", "hand", "catorder", "subg", "ord")]
    rs = [
        # 1. the recipe named as the item first, though "aa-named" sorts before it
        recipe("aa-named", [("ing", 1)], [("named", 1)]),
        recipe("named", [("ing", 9)], [("named", 1)], categories=["smelting"]),
        # 2. not a catalyst: aa-cat uses cat itself
        recipe("aa-cat", [("cat", 1), ("ing", 1)], [("cat", 2)]),
        recipe("zz-cat", [("ing", 1)], [("cat", 1)], categories=["smelting"]),
        # 3. hand-craftable intermediate: crafting beats smelting; aa-hand forbids it
        recipe("aa-hand", [("ing", 1)], [("hand", 1)], categories=["smelting"]),
        recipe("ab-hand", [("ing", 1)], [("hand", 1)], allow_as_intermediate=False),
        recipe("zz-hand", [("ing", 1)], [("hand", 1)], categories=["smelting", "crafting"]),
        # 4. category: alpha before beta
        recipe("aa-catorder", [("ing", 1)], [("catorder", 1)], categories=["beta"]),
        recipe("zz-catorder", [("ing", 1)], [("catorder", 1)], categories=["alpha"]),
        # 5. subgroup: group g1 before g2, then subgroup order
        recipe("aa-subg", [("ing", 1)], [("subg", 1)], categories=["alpha"], subgroup="sg-late"),
        recipe("ab-subg", [("ing", 1)], [("subg", 1)], categories=["alpha"], subgroup="sg-b"),
        recipe("zz-subg", [("ing", 1)], [("subg", 1)], categories=["alpha"], subgroup="sg-a"),
        # 6. order; and hidden / no-decomposition recipes never count
        recipe("aa-ord", [("ing", 1)], [("ord", 1)], categories=["alpha"], order="b"),
        recipe("ab-ord", [("ing", 1)], [("ord", 1)], categories=["alpha"], order="a",
               hidden=True),
        recipe("ac-ord", [("ing", 1)], [("ord", 1)], categories=["alpha"], order="a",
               allow_decomposition=False),
        recipe("zz-ord", [("ing", 1)], [("ord", 1)], categories=["alpha"], order="a"),
    ]
    return dump(items=its, recipes=rs)


def loop_dump():
    """x -> y at +300% (4 y per x), y recycles to 0.3 x: yield 1.2, flagged.
    p -> q at +300%, q recycles to 0.2 p: yield 0.8, not.
    s -> t without productivity, t back to s 1:1, but an infinite research on s->t:
    at its cap of 3 the yield is 4.
    c -> sg -> sp -> c, rail-signal style: make-sg takes 1 c and 5 sp (a loop good as
    a side ingredient) for 1 sg; sg recycles to 1.25 sp; sp makes c at +300%. The
    edges multiply to 1 x 1.25 x 4 = 5, but sp runs down: made 1.25, taken 5 + 1.25,
    so 0.2, and the loop is not flagged.
    u -> w -> u 1:1 is break-even; u-catalyst (2 u -> 3 u) a one-recipe gain."""
    its = [item(n) for n in ("x", "y", "p", "q", "s", "t", "c", "sg", "sp", "u", "w")]
    rs = [
        recipe("make-y", [("x", 1)], [("y", 1)], allow_productivity=True),
        recipe("y-recycling", [("y", 1)],
               [{"type": "item", "name": "x", "amount": 0, "extra_count_fraction": 0.3}],
               categories=["recycling"], hidden=True),
        recipe("make-q", [("p", 1)], [("q", 1)], allow_productivity=True),
        recipe("q-recycling", [("q", 1)],
               [{"type": "item", "name": "p", "amount": 0, "extra_count_fraction": 0.2}],
               categories=["recycling"], hidden=True),
        recipe("make-t", [("s", 1)], [("t", 1)]),
        recipe("t-to-s", [("t", 1)], [("s", 1)]),
        recipe("make-sg", [("c", 1), ("sp", 5)], [("sg", 1)]),
        recipe("sg-recycling", [("sg", 1)],
               [{"type": "item", "name": "sp", "amount": 1, "extra_count_fraction": 0.25}],
               categories=["recycling"], hidden=True),
        recipe("make-c", [("sp", 1)], [("c", 1)], allow_productivity=True),
        recipe("u-to-w", [("u", 1)], [("w", 1)]),
        recipe("w-to-u", [("w", 1)], [("u", 1)]),
        recipe("u-catalyst", [("u", 2)], [("u", 3)]),
        # p -> q with no productivity, then q-recycling's 0.2: fails at 0, and no
        # step can have productivity (make-q, at +300%, is the edge find_loops takes)
        recipe("p-to-q-plain", [("p", 1)], [("q", 1)]),
    ]
    techs = [
        {"name": "make-y-productivity", "effects": [
            {"type": "change-recipe-productivity", "recipe": "make-y", "change": 0.1}],
         "unit": {"count_formula": "1.5^L*1000", "ingredients": [["pack-a", 1]], "time": 60},
         "max_level": "infinite"},
        {"name": "make-t-productivity", "effects": [
            {"type": "change-recipe-productivity", "recipe": "make-t", "change": 0.1}],
         "unit": {"count_formula": "1.5^L*1000", "ingredients": [["pack-a", 1]], "time": 60},
         "max_level": "infinite"},
    ]
    return dump(items=its + [item("pack-a")], recipes=rs, techs=techs)


def tech_dump():
    """t-a <- t-b <- t-c; t-d needs t-a and t-c (depth 3); t-trig is a trigger."""
    packs = [item("pack-b", order="b"), item("pack-a", order="a"), item("pack-c", order="c")]
    techs = [
        {"name": "t-a", "unit": {"count": 10, "ingredients": [["pack-a", 1]], "time": 10}},
        {"name": "t-b", "prerequisites": ["t-a"],
         "unit": {"count": 50, "ingredients": [["pack-b", 1], ["pack-a", 1]], "time": 15}},
        {"name": "t-c", "prerequisites": ["t-b"],
         "unit": {"count": 75, "ingredients": [["pack-a", 2], ["pack-b", 1]], "time": 30}},
        {"name": "t-d", "prerequisites": ["t-a", "t-c"],
         "unit": {"count": 100, "ingredients": [["pack-b", 1], ["pack-a", 1]], "time": 60}},
        {"name": "t-trig", "research_trigger": {"type": "craft-item", "item": "pack-a"}},
        {"name": "t-inf-3", "prerequisites": ["t-d"], "max_level": "infinite",
         "unit": {"count_formula": "2^(L-3)*1000", "ingredients": [["pack-a", 1]], "time": 60}},
        {"name": "sae-new", "prerequisites": ["t-d"],
         "unit": {"count": 200, "ingredients": [["pack-a", 1], ["pack-b", 1], ["pack-c", 1]],
                  "time": 60}},
        {"name": "t-odd", "prerequisites": ["t-a"],
         "unit": {"count_formula": "1e3*L", "ingredients": [["pack-a", 1]], "time": 60}},
    ]
    return dump(items=packs, techs=techs)


# ---------------------------------------------------------------- the cases

def near(a, b, tol=1e-9):
    return a is not None and b is not None and abs(a - b) <= tol * max(1.0, abs(b))


def raw_of(res):
    return {k[1]: round(v, 9) for k, v in res["raw"].items()}


def spike_dump():
    """The T04 spike (evidence/.../T04/probe-mod/sae-t04-spike), as its data.lua and
    data-final-fixes.lua build it (inject.py likewise): lift constant 2e6, silo lift
    4e6, iron-plate 1000; items of stack 1, subgroup and order alike for every
    recipe, each recipe 1 craft of its item from 1 or 2 plates (500 or 1000)."""
    cats = [("t04-cat-x", "b"), ("t04-cat-y", "a")]
    items = [("t04-a1", "t04a1"), ("t04-a2", "t04a2"), ("t04-a3", "t04a3"), ("t04-b", "t04b"),
             ("t04-c", "t04c"), ("t04-d", "t04d"), ("t04-loop-a", "t04l-b"),
             ("t04-loop-b", "t04l-a"), ("t04-loop-d", "t04l-d"), ("t04-loop-c", "t04l-c")]
    spec = [("t04-a1-z", "t04-a1", ["chemistry"], 1, False, []),
            ("t04-a1-a", "t04-a1", ["smelting"], 2, False, []),
            ("t04-a2-a", "t04-a2", ["centrifuging"], 1, False, []),
            ("t04-a2-z", "t04-a2", ["oil-processing"], 2, False, []),
            ("t04-a3-a", "t04-a3", ["t04-cat-x"], 1, False, []),
            ("t04-a3-z", "t04-a3", ["t04-cat-y"], 2, False, []),
            ("t04-b-a", "t04-b", ["oil-processing", "advanced-crafting"], 1, False, []),
            ("t04-b-z", "t04-b", ["chemistry"], 2, False, []),
            ("t04-c-a", "t04-c", ["crafting"], 1, True, []),
            ("t04-c-z", "t04-c", ["crafting"], 2, False, []),
            ("t04-d-z", "t04-d", ["crafting"], 1, False, []),
            ("t04-d-a", "t04-d", ["chemistry"], 2, False, []),
            ("t04-loop-a", "t04-loop-a", ["chemistry"], 1, False, ["t04-loop-b"]),
            ("t04-loop-b", "t04-loop-b", ["chemistry"], 2, False, ["t04-loop-a"]),
            ("t04-loop-d", "t04-loop-d", ["chemistry"], 1, False, ["t04-loop-c"]),
            ("t04-loop-c", "t04-loop-c", ["chemistry"], 2, False, ["t04-loop-d"])]
    rs = [recipe(n, [("iron-plate", plates)] + [(x, 1) for x in extra], [(it, 1)],
                 categories=c, energy_required=1, allow_productivity=True,
                 hide_from_player_crafting=hide, subgroup="intermediate-product", order="t04")
          for n, it, c, plates, hide, extra in spec]
    its = [item("iron-plate", 100, weight=1000)] + [
        item(n, 1, subgroup="intermediate-product", order=o) for n, o in items]
    D = dump(items=its, recipes=rs, extra={
        "recipe-category": {n: {"name": n, "order": o} for n, o in cats},
        "item-subgroup": {"intermediate-product": {"name": "intermediate-product",
                                                   "group": "g1", "order": "g"}},
        "rocket-silo": {"rocket-silo": {"name": "rocket-silo", "lift_weight": 4000000}}})
    D.lift = 2000000.0     # data-final-fixes.lua: default_rocket_lift_weight = 2e6
    return D


def spike_cases():
    """The engine's figures for the spike, from evidence/.../T04/spike-engine.tsv and
    spike-rocket.tsv (RCON, 2026-11-13)."""
    D = spike_dump()
    W = graph.compute_weights(D)
    engine = {"t04-a1": 1000.0, "t04-a2": 500.0, "t04-a3": 500.0, "t04-b": 500.0,
              "t04-c": 500.0, "t04-d": 1000.0, "t04-loop-a": 550.05499267578125,
              "t04-loop-b": 1275.5101928710938, "t04-loop-c": 1275.5101928710938,
              "t04-loop-d": 550.05499267578125}
    return [
        ("spike ordering: the earlier recipe name, over category name (a1), category "
         "order (a3), several categories (b), hide_from_player_crafting (c), crafting "
         "against chemistry (d)",
         {n: W[n]["weight"] for n in engine if "loop" not in n},
         {n: v for n, v in engine.items() if "loop" not in n}),
        ("spike loops: definition order a, b, d, c; the default for one use only "
         "(a, d 550.05499267578125; b, c 1275.5101928710938)",
         {n: W[n]["weight"] for n in engine if "loop" in n},
         {n: v for n, v in engine.items() if "loop" in n}),
        ("spike lift: weights by the constant (2e6), cargo by the silo (4e6): "
         "iron-plate 4000 a rocket", graph.per_rocket(D, W["iron-plate"]["weight"]), 4000),
    ]


def rounding_cases():
    """Each against an engine value from the T04 tables (c6-engine-vanilla.tsv)."""
    D = dump(items=[
        item("fishlike", 100, weight=3333.3333333333335),            # raw-fish, explicit
        item("ing3000", 100, weight=3000), item("pu-like", 100, ingredient_to_weight_coefficient=1),
        item("ing466k", 100, weight=466666.6666666667), item("dd-like", 5),
    ], recipes=[
        recipe("pu-like", [("ing3000", 1)], [("pu-like", 1)], allow_productivity=True),
        recipe("dd-like", [("ing466k", 1)], [("dd-like", 1)], allow_productivity=True),
    ])
    W = graph.compute_weights(D)
    return [
        ("rounding: an explicit weight is stored in 1/65536 steps, rounded down "
         "(raw-fish 3333.3333333 -> 3333.3333282470703)", W["fishlike"]["weight"],
         3333.3333282470703),
        ("rounding: the floor branch likewise (processing-unit 1e6/3/100 -> "
         "3333.3333282470703)", (W["pu-like"]["branch"], W["pu-like"]["weight"]),
         ("floor", 3333.3333282470703)),
        ("rounding: the intermediate branch to a whole number (discharge-defense "
         "233333.33 -> 233333)", (W["dd-like"]["branch"], W["dd-like"]["weight"]),
         ("intermediate", 233333.0)),
        ("rounding: fixed_weight(1/3) is a multiple of 1/65536, not above 1/3",
         (graph.fixed_weight(1 / 3) * 65536 == int(graph.fixed_weight(1 / 3) * 65536),
          graph.fixed_weight(1 / 3) <= 1 / 3), (True, True)),
    ]


def silo_cases():
    D = dump(items=[item("x", 100, weight=1000)], extra={"rocket-silo": {
        "rocket-silo": {"name": "rocket-silo"},
        "big-silo": {"name": "big-silo", "lift_weight": 3000000}}})
    same = dump(items=[item("x", 100, weight=1000)], extra={"rocket-silo": {
        "rocket-silo": {"name": "rocket-silo"}, "twin": {"name": "twin"}}})
    none = dump(items=[item("x", 100, weight=1000)])
    return [
        ("silo: silos that differ give one figure each (default lift 1e6 -> 1000; 3e6 -> 3000)",
         graph.per_rocket(D, 1000.0), {"rocket-silo": 1000, "big-silo": 3000}),
        ("silo: silos that agree give one figure", graph.per_rocket(same, 1000.0), 1000),
        ("silo: no silo in the dump: the default lift_weight 1e6", graph.per_rocket(none, 1000.0),
         1000),
        ("silo: weight 0 has no figure", graph.per_rocket(same, 0.0), None),
    ]


def cost_cases():
    D = circuit_dump()
    c = graph.Coster(D)
    out = []
    u = c.unit(("item", "electronic-circuit"))
    out.append(("cost: circuit raw is 1 iron ore + 1.5 copper ore",
                raw_of(u), {"iron-ore": 1.0, "copper-ore": 1.5}))
    out.append(("cost: circuit time is 9.25 s", near(u["time"], 9.25), True))
    out.append(("cost: route is the weight's pick (iron-plate, not casting-iron)",
                c.unit(("item", "iron-plate"))["recipe"], "iron-plate"))
    rep = c.report(("item", "iron-plate"))
    out.append(("cost: other routes list casting-iron (no-decomposition), not the recycling",
                [(o["recipe"], o["flags"]) for o in rep["other_routes"]],
                [("casting-iron", ["no-decomposition"])]))
    out.append(("cost: other route's own cost (lava 10 per plate)",
                {r["name"]: r["amount"] for r in rep["other_routes"][0]["raw"]}, {"lava": 10.0}))
    c2 = graph.Coster(D, None, ["casting-iron"])
    out.append(("cost: --recipe casting-iron costs the circuit in lava",
                raw_of(c2.unit(("item", "electronic-circuit"))),
                {"lava": 10.0, "copper-ore": 1.5}))
    hot = graph.PlanetCoster(D, "hot")
    out.append(("cost: --planet hot (lava, pressure 4000) takes casting-iron",
                (hot.unit(("item", "iron-plate"))["recipe"],
                 raw_of(hot.unit(("item", "iron-plate")))),
                ("casting-iron", {"lava": 10.0})))
    out.append(("cost: --planet hot has no copper: the circuit is partly local, cable imported",
                [(r["name"], r["amount"], r["kind"])
                 for r in hot.report(("item", "electronic-circuit"))["raw"]],
                [("lava", 10.0, "tile-fluid"), ("copper-cable", 3.0, "import")]))
    out.append(("cost: --planet hot: copper cable, nothing of it made there, is an import",
                (hot.unit(("item", "copper-cable"))["recipe"],
                 hot.unit(("item", "copper-cable"))["note"]), (None, "import")))
    home = graph.PlanetCoster(D, "home")
    out.append(("cost: --planet home fails casting-iron's surface condition",
                [(o["recipe"], o["flags"])
                 for o in home.report(("item", "iron-plate"))["other_routes"]],
                [("casting-iron", ["no-decomposition", "surface"])]))
    out.append(("cost: a catalyst recipe counts its net output (1 egg per food)",
                raw_of(c.unit(("item", "egg"))), {"food": 1.0}))
    # Q43.2: a good with only no-decomposition recipes takes the first, marked *
    out.append(("Q43.2: only no-decomposition recipes: the first, marked *",
                (c.unit(("item", "slag"))["recipe"], c.unit(("item", "slag"))["note"]),
                ("slag", "*")))
    # Q43.1: --planet by the ordering, recycling last, imports
    out.append(("Q43.1: --planet hot: tier-0 iron-plate needs ore hot lacks; casting-iron next",
                hot.unit(("item", "iron-plate"))["note"], "*"))
    junk = graph.PlanetCoster(D, "dump")
    plate = junk.report(("item", "iron-plate"))
    out.append(("Q43.1: --planet dump: recycling last resort; gear-recycling (1 step beneath) "
                "before iron-plate (ore by 2)",
                (plate["recipe"], plate["note"], {r["name"]: r["amount"] for r in plate["raw"]}),
                ("gear-recycling", "recycling", {"junk": 10.0})))
    out.append(("Q43.1: ... the planet's other routes listed beside it",
                [(o["recipe"], o["flags"], {r["name"]: r["amount"] for r in o["raw"]})
                 for o in plate["other_routes"]],
                [("iron-plate", [], {"junk": 400.0}),
                 ("casting-iron", ["no-decomposition", "surface"], {"lava": 10.0})]))
    mix = junk.report(("item", "mix"))
    out.append(("Q50: a partly-local good takes the fewest recycling steps beneath first "
                "(ab-mix, 0 steps, over aa-mix, ore 2 steps deep)",
                (mix["recipe"], [(r["name"], r["amount"], r["kind"]) for r in mix["raw"]]),
                ("ab-mix", [("copper-plate", 1.0, "import"), ("junk", 1.0, "resource")])))
    out.append(("Q43.1: --planet home: a recycling route is never taken where another resolves",
                home.unit(("item", "iron-plate"))["recipe"], "iron-plate"))
    out.append(("Q43.1: --planet: no FLUID_PRICE, no cheapest-route relaxation",
                (hasattr(graph, "FLUID_PRICE"), hasattr(graph.PlanetCoster, "_relax")),
                (False, False)))
    # Q43.6: default-mode raws name the planets they come from
    rows = {r["name"]: r.get("found_on") for r in c.report(("item", "electronic-circuit"))["raw"]}
    out.append(("Q43.6: default raws found on only some places name them",
                rows, {"iron-ore": ["home"], "copper-ore": ["home"]}))
    rows = {r["name"]: r.get("found_on") for r in c2.report(("item", "iron-plate"))["raw"]}
    out.append(("Q43.6: ... a tile fluid by the planets whose tiles carry it", rows,
                {"lava": ["hot"]}))
    out.append(("Q43.6: ... shown in text as [raw: <planets>]",
                graph.raw_text(c2.report(("item", "iron-plate"))["raw"]), "lava(f) 10 [raw: hot]"))
    out.append(("Q43.6: ... and not with --planet, where every raw is local",
                ["found_on" in r for r in hot.report(("item", "iron-plate"))["raw"]], [False]))
    return out


def weight_cases():
    W = graph.compute_weights(weight_dump())
    def w(n):
        return (W[n]["branch"], round(W[n]["weight"], 6))
    return [
        ("weight: only-in-cursor + spawnable is 0", w("cursor-thing"), ("cursor-spawnable", 0.0)),
        ("weight: no recipe -> default 100", w("orphan"), ("no-recipe", 100.0)),
        ("weight: recipe loop: loop-a takes loop-b at the default for that use (100 x 0.5)",
         (w("loop-a"), W["loop-a"]["loop_defaults"]), (("floor", 50.0), ["loop-b"])),
        ("weight: ... loop-b is weighed properly afterwards (50 x 0.5), not kept at 100",
         w("loop-b"), ("floor", 25.0)),
        ("weight: an item whose only recipe takes itself keeps the default (branch loop)",
         w("self-loop"), ("loop", 100.0)),
        ("weight: zero recipe weight -> default", w("from-nothing"), ("zero-recipe-weight", 100.0)),
        ("weight: zero product count -> default", w("never-made"), ("zero-product-count", 100.0)),
        ("weight: stack-size branch (no productivity, 1e6/10 >= 500)", w("crate"),
         ("stack-size", 100000.0)),
        ("weight: floor branch, the doc's circuit = 500", w("circuit"), ("floor", 500.0)),
        ("weight: intermediate branch (stacks <= 1)", w("monolith"), ("intermediate", 1000000.0)),
        ("weight: a fluid ingredient weighs 100 a unit (10 x 100 x 0.5)", w("brew"),
         ("floor", 500.0)),
        ("weight: hidden and no-decomposition recipes are skipped", w("hidden-only"),
         ("no-recipe", 100.0)),
        ("weight: an explicit weight stands", w("plate"), ("explicit", 1000.0)),
    ]


def order_cases():
    D = order_dump()
    def first(n):
        return D.weight_recipes(n)[0].name
    return [
        ("order 1: the recipe named as the item", first("named"), "named"),
        ("order 2: not using the item as a catalyst", first("cat"), "zz-cat"),
        ("order 3 (measured): hand-craftability does not act; the earlier name wins",
         first("hand"), "aa-hand"),
        ("order 4 (measured): category does not act; the earlier name wins",
         first("catorder"), "aa-catorder"),
        ("order 5: subgroup (group order, then subgroup order)", first("subg"), "zz-subg"),
        ("order 6: order; hidden and no-decomposition skipped", first("ord"), "zz-ord"),
        ("order: the skipped recipes are not candidates at all",
         [r.name for r in D.weight_recipes("ord")], ["zz-ord", "aa-ord"]),
    ]


def loop_cases():
    D = loop_dump()
    loops = graph.find_loops(D, 3)
    by = {tuple(sorted(lp["goods"])): lp for lp in loops}
    xy = by.get(("x", "y"))
    st = by.get(("s", "t"))
    return [
        ("loops: x -> y -> x at +300% (yield 1.2) is flagged a gain",
         (xy is not None and round(xy["yield"], 9), xy and xy["kind"]), (1.2, "gain")),
        ("loops: ... with the productivity research acting on it",
         xy and xy["productivity_research"], ["make-y-productivity"]),
        ("loops: p -> q -> p (yield 0.8) is not flagged", ("p", "q") in by, False),
        ("loops: break-even productivity, x -> y -> x: 0.3 x (1 + p) = 1, p = 233.33%",
         xy and round(xy["break_even_productivity"], 4), 2.3333),
        ("loops: break-even productivity 0 when the loop holds without (s -> t -> s)",
         st and st["break_even_productivity"], 0.0),
        ("loops: break-even 0 for a loop that holds with no productivity possible "
         "(u -> w -> u, 1:1)",
         (lambda lp: lp and lp["break_even_productivity"])(by.get(("u", "w"))), 0.0),
        ("loops: ... and for a gain with no productivity possible (u-catalyst, 2 -> 3, 1.5)",
         (lambda lp: lp and (round(lp["yield"], 9), lp["break_even_productivity"]))(
             by.get(("u",))), (1.5, 0.0)),
        ("loops: n/a (None) only when the loop fails at 0 and no step can have productivity",
         graph.break_even_productivity(D, [("item", "p"), ("item", "q")],
                                       ["p-to-q-plain", "q-recycling"]), None),
        ("Q43.3: a break-even loop (u -> w -> u, 1:1) is listed, marked break-even",
         (lambda lp: lp and (lp["kind"], lp["catalyst"], round(lp["yield"], 9)))(
             by.get(("u", "w"))),
         ("break-even", False, 1.0)),
        ("Q43.3: a one-recipe loop (u-catalyst, 2 -> 3) is marked catalyst",
         (lambda lp: lp and (lp["kind"], lp["catalyst"], round(lp["yield"], 9)))(by.get(("u",))),
         ("gain", True, 1.5)),
        ("loops: a loop good eaten as a side ingredient is charged: c -> sg -> sp not flagged",
         [lp["goods"] for lp in loops if {"c", "sg", "sp"} & set(lp["goods"])], []),
        ("loops: ... charged, sp is made 1.25 of 6.25 taken (0.2), the lowest good",
         (lambda r: (round(r[0][("item", "sp")], 9), r[2][1]))(graph.charge_loop(
             [("item", "c"), ("item", "sg"), ("item", "sp")],
             [graph.recipe_flows(D, D.recipes[n])[:2]
              for n in ("make-sg", "sg-recycling", "make-c")])), (0.2, "sp")),
        ("loops: research-only productivity reaches the cap (s -> t -> s, yield 4)",
         st is not None and round(st["yield"], 9), 4.0),
        ("loops: a finite research gives only its sum (0.1 x levels 2-4)",
         round(graph.reachable_productivity(dump(
             recipes=[recipe("r", [("a", 1)], [("b", 1)])],
             techs=[{"name": "r-productivity-2", "max_level": 4, "effects": [
                 {"type": "change-recipe-productivity", "recipe": "r", "change": 0.1}]}]),
             graph.Recipe("r", {"ingredients": [], "results": []})), 9),
         0.3),
    ]


def tech_cases():
    D = tech_dump()
    depths = graph.tech_depths(D)
    rows = {n: graph.tech_row(D, n, depths) for n in D.techs}
    return [
        ("tech: depth t-a 0, t-b 1, t-c 2, t-d 3 (the longest chain)",
         [depths[n] for n in ("t-a", "t-b", "t-c", "t-d")], [0, 1, 2, 3]),
        ("tech: tier is the packs, in pack order", rows["t-d"]["tier"], ["pack-a", "pack-b"]),
        ("tech: research cost is count x packs, count x time",
         (rows["t-c"]["packs"], rows["t-c"]["total_time"]),
         ({"pack-a": 150.0, "pack-b": 75.0}, 2250.0)),
        ("tech: a trigger technology has the trigger tier", (rows["t-trig"]["tier"],
                                                              rows["t-trig"]["trigger"]["type"]),
         (["trigger"], "craft-item")),
        ("tech: count_formula at the name's level (t-inf-3: 2^0 x 1000)",
         (rows["t-inf-3"]["level"], rows["t-inf-3"]["count"]), (3, 1000.0)),
        ("tech: count_formula at --level 5 (2^2 x 1000)",
         graph.tech_row(D, "t-inf-3", depths, 5)["count"], 4000.0),
        ("formula: 1000*(L - 2) at 3", graph.eval_formula("1000*(L - 2)", 3), 1000.0),
        ("formula: 1.5^L*1000 at 2", graph.eval_formula("1.5^L*1000", 2), 2250.0),
        ("formula: -(2)+5, 2^3^2, l", (graph.eval_formula("-(2)+5", 1),
                                       graph.eval_formula("2^3^2", 1),
                                       graph.eval_formula("l*2", 4)), (3.0, 512.0, 8.0)),
        ("formula: no level in the name is level 1", graph.tech_level("steel-plate-productivity"),
         1),
        ("tech: a count_formula the reader cannot take leaves the row's count empty, no traceback",
         (rows["t-odd"]["count"], rows["t-odd"]["total_time"],
          "unknown name 'e'" in rows["t-odd"].get("formula_error", "")), (None, None, True)),
    ]


def compare_cases():
    D = tech_dump()
    depths = graph.tech_depths(D)
    c = graph.compare(D, graph.Coster(D), {}, depths, "sae-new", None, None)
    near = [(t["change"], t["tier"], t["peers"]) for t in c["near_tiers"]]
    return [
        ("Q43.4: compare is the exact pack set: sae-new (a+b+c) has no vanilla peers",
         c["peers"], []),
        ("Q43.4: ... so the tiers one pack away are listed (a+b, -pack-c)", near,
         [("-pack-c", ["pack-a", "pack-b"], ["t-b", "t-c", "t-d"])]),
        ("Q43.4: an exact match lists no near tiers",
         graph.compare(D, graph.Coster(D), {}, depths, "t-c", None, None)["near_tiers"], []),
    ]


def vanilla_cases():
    out = []
    with tempfile.TemporaryDirectory() as root:
        out.append(("Q43.5: no KB dump under a root -> None (the sae- prefix rule)",
                    graph.kb_dump_under(root), None))
        path = os.path.join(root, "knowledge-base", "2.1.24", "data-raw-dump.json")
        os.makedirs(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as f:
            f.write("{}")
        out.append(("Q43.5: the KB dump under a root is found", graph.kb_dump_under(root), path))
    found = graph.default_vanilla_dump()
    out.append(("Q43.5: the default, where there is one, is a KB dump under some repo root",
                found is None or found.endswith(graph.KB_DUMP), True))
    return out


def cli_cases():
    out = []
    raw = circuit_dump().raw
    raw["technology"] = tech_dump().raw["technology"]
    raw["item"].update(tech_dump().raw["item"])
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "data-raw-dump.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(raw, f)
        p = subprocess.run([sys.executable, GRAPH, path, "--json", "--vanilla", "prefix"],
                           capture_output=True, text=True)
        ok = p.returncode == 0
        rep = json.loads(p.stdout) if ok else {}
        secs = rep.get("sections", {})
        out.append(("cli: --json exits 0", p.returncode, 0))
        out.append(("cli: every section present and non-empty (loops: the egg catalyst)",
                    sorted(k for k, v in secs.items() if v), sorted(graph.SECTIONS)))
        p = subprocess.run([sys.executable, GRAPH, path, "--vanilla", "prefix"],
                           capture_output=True, text=True)
        out.append(("cli: text report exits 0 and has five section titles",
                    (p.returncode, p.stdout.count("\n== ")), (0, 5)))
        p = subprocess.run([sys.executable, GRAPH, path, "--item", "nope"],
                           capture_output=True, text=True)
        out.append(("cli: an unknown --item exits 1", p.returncode, 1))
        p = subprocess.run([sys.executable, GRAPH, path, "--section", "compare",
                            "--vanilla", os.path.join(tmp, "nonexistent.json")],
                           capture_output=True, text=True)
        out.append(("cli: a missing --vanilla file exits 1 with one line, no traceback",
                    (p.returncode, len(p.stderr.strip().splitlines()),
                     "cannot read the --vanilla dump" in p.stderr), (1, 1, True)))
        p = subprocess.run([sys.executable, GRAPH, os.path.join(tmp, "none.json")],
                           capture_output=True, text=True)
        out.append(("cli: a missing dump exits 1 with one line, no traceback",
                    (p.returncode, len(p.stderr.strip().splitlines()),
                     "cannot read the dump" in p.stderr), (1, 1, True)))
        p = subprocess.run([sys.executable, GRAPH, path, "--section", "loops"],
                           capture_output=True, text=True)
        out.append(("cli: the loops table title says other ingredients are free, at each "
                    "recipe's maximum_productivity, and has a break-even column",
                    ("other ingredients free" in p.stdout,
                     "yield at each recipe's maximum_productivity" in p.stdout,
                     "break-even" in p.stdout.splitlines()[3]), (True, True, True)))
        p = subprocess.run([sys.executable, GRAPH, path, "--section", "tech", "--tech", "t-odd"],
                           capture_output=True, text=True)
        out.append(("cli: the t-odd row prints its formula note and exits 0",
                    (p.returncode, "count_formula '1e3*L' not evaluated" in p.stdout), (0, True)))
        def cost_rows(*names):
            argv = [path, "--json", "--section", "cost", "--section", "weight"]
            for n in names:
                argv += ["--item", n]
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                graph.main(argv)
            sec = json.loads(buf.getvalue())["sections"]
            return ([(r["type"], r["name"], {x["name"]: x["amount"] for x in r["raw"]})
                     for r in sec["cost"]], [w["name"] for w in sec["weight"]])
        out.append(("cli: a bare --item naming an item and a fluid costs both; weight the item",
                    cost_rows("dual"),
                    ([("item", "dual", {"iron-ore": 2.0}), ("fluid", "dual", {"lava": 2.0})],
                     ["dual"])))
        out.append(("cli: --item fluid:dual is the fluid alone (no weight row)",
                    cost_rows("fluid:dual"), ([("fluid", "dual", {"lava": 2.0})], [])))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = graph.main([path, "--json", "--section", "compare", "--compare", "t-c",
                               "--vanilla", "prefix"])
        cmp_ = json.loads(buf.getvalue())["sections"]["compare"]
        out.append(("cli: --compare t-c sets it beside t-b and t-d (same packs)",
                    (code, cmp_["kind"], [p["name"] for p in cmp_["peers"]]),
                    (0, "technology", ["t-b", "t-d"])))
    return out


def main():
    verbose = "-v" in sys.argv[1:]
    cases = (cost_cases() + weight_cases() + order_cases() + spike_cases() + rounding_cases()
             + silo_cases() + loop_cases() + tech_cases() + compare_cases() + vanilla_cases()
             + cli_cases())
    failed = []
    for label, got, want in cases:
        ok = got == want
        if not ok:
            failed.append(label)
        if verbose or not ok:
            print(f"{'ok  ' if ok else 'FAIL'} {label}")
            if not ok:
                print(f"       got  {got!r}\n       want {want!r}")
    print(f"{'FAIL' if failed else 'PASS'}: {len(cases) - len(failed)} of {len(cases)} cases "
          "as listed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
