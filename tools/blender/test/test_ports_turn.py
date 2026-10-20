#!/usr/bin/env python3
"""contract.py's port faces for turning models (`ports`, `ports_turn`) held to its docs.

  python3 tools/blender/test/test_ports_turn.py

Nothing is rendered and nothing is kept: the test box's declaration is read from box.py's own
source (its DECL and the canvas and rig numbers it is declared with, the module-level
assignments that build them, run without Blender), edited, and validated. Exits 0 when every
case below comes out as listed, 1 naming those that do not.

  reach      reached_faces: four directions, an N port -> N, E, S, W; horizontal-vertical, N ->
             N, E, and S -> S, W; one direction, N -> N; one direction with ports_turn, N ->
             N, E, S, W; no ports -> none.
  box        box.py's declaration (four directions, a port on every face) accepted. Turned with
             only a north port: refused, naming field ports and the missing faces E, S, W, in
             that order. With the north and east ports alone (the fixture before ports turned):
             refused naming S, W.
  hv         horizontal-vertical: N and E refused naming S (E turned 90 is S); N, E, S, W
             accepted; N and S alone refused naming E, W; no ports accepted.
  one        one direction: a north port alone accepted (it does not turn); with ports_turn
             true refused naming E, S, W; with all four faces and ports_turn true accepted (the
             Vacuum Furnace's case); ports_turn true and no ports accepted.
  flag       ports_turn false accepted and changes nothing (one direction, a north port alone);
             ports_turn 1, "true" or null refused naming ports_turn.
  declare    declare() with rig stood in: without ports_turn render.json has no ports_turn key
             and is byte for byte json.dump of the declaration, as before the field existed;
             with ports_turn=True it carries "ports_turn": true; a box turned with a north port
             alone raises ContractError and writes no render.json.
"""
import ast
import copy
import json
import math
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import contract  # noqa: E402

FAILED = []


def check(case, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {case}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILED.append(f"{case}: {detail}")


def assigned(path, names, env=None):
    """Run the module-level assignments to `names` in a Python file, in order, without the rest
    of it (no bpy): their values, by name."""
    env = dict(env or {}, math=math)
    with open(path) as f:
        tree = ast.parse(f.read(), path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
            exec(compile(ast.Module(body=[node], type_ignores=[]), path, "exec"), env)
    return {n: env[n] for n in names}


def rig_numbers():
    r = assigned(os.path.join(TOOLS, "rig.py"), ("ELEVATION", "PX_PER_TILE"))
    return r["ELEVATION"], r["PX_PER_TILE"]


def box_decl():
    """The test box's declaration as contract.declare writes it for its renders (not --ports)."""
    b = assigned(os.path.join(HERE, "box.py"), ("CANVAS", "PORT_CANVAS", "WRECK_CANVAS", "STROKE", "DECL"))
    elevation, ppt = rig_numbers()
    decl = dict(b["DECL"], canvas=b["CANVAS"], rig=dict(elevation=math.degrees(elevation), px_per_tile=ppt))
    return json.loads(json.dumps(decl))


def port(face, tile):
    return dict(face=face, tile=list(tile))


def case(label, decl0, edit, missing=None, field=None):
    """Validate decl0 edited by edit(d). missing: the faces the refusal must name (field ports),
    in order; field: another field the refusal must name. Neither: it must be accepted."""
    d = copy.deepcopy(decl0)
    edit(d)
    want = "ports" if missing else field
    try:
        contract.validate(d, "test")
        check(label, want is None, f"accepted, but should be refused naming {want}")
    except contract.ContractError as e:
        msg = str(e)
        ok = want is not None and f": {want}:" in msg
        if ok and missing:
            ok = f"reach face(s) {', '.join(missing)}, which" in msg
        check(label, ok, f"refused: {msg}" if want is None else f"refused, not naming {want} {missing or ''}: {msg}")


def ports(*ps):
    return lambda d: d.update(ports=list(ps))


def test_reach(box):
    print("reach")
    n, s = port("N", (-0.5, -0.5)), port("S", (0.5, 0.5))
    for label, edit, want in (
            ("four, N", dict(ports=[n]), ["N", "E", "S", "W"]),
            ("horizontal-vertical, N", dict(directions="horizontal-vertical", ports=[n]), ["N", "E"]),
            ("horizontal-vertical, S", dict(directions="horizontal-vertical", ports=[s]), ["S", "W"]),
            ("one, N", dict(directions="one", ports=[n]), ["N"]),
            ("one with ports_turn, N", dict(directions="one", ports=[n], ports_turn=True), ["N", "E", "S", "W"]),
            ("four, no ports", dict(ports=[]), [])):
        got = contract.reached_faces(dict(box, **edit))
        check(f"reached_faces {label} -> {', '.join(want) or 'none'}", got == want, f"got {got}")


def test_box(box):
    print("box")
    n, e = port("N", (-0.5, -0.5)), port("E", (0.5, 0.5))
    check("box.py declares a port on every face",
          sorted(p["face"] for p in box["ports"]) == sorted("NESW"), f"{box['ports']}")
    case("box.py as declared accepted", box, lambda d: None)
    case("box.py turned, a north port alone refused naming E, S, W", box, ports(n), missing=["E", "S", "W"])
    case("box.py turned, north and east alone refused naming S, W", box, ports(n, e), missing=["S", "W"])


def test_hv(box):
    print("hv")
    n, e = port("N", (-0.5, -0.5)), port("E", (0.5, 0.5))
    s, w = port("S", (0.5, 0.5)), port("W", (-0.5, 0.5))

    def hv(*ps):
        return lambda d: d.update(directions="horizontal-vertical", ports=list(ps))
    case("horizontal-vertical N, E refused naming S", box, hv(n, e), missing=["S"])
    case("horizontal-vertical N, E, S, W accepted", box, hv(n, e, s, w))
    case("horizontal-vertical N, S refused naming E, W", box, hv(n, s), missing=["E", "W"])
    case("horizontal-vertical no ports accepted", box, hv())


def test_one(box):
    print("one")
    n, e = port("N", (-0.5, -0.5)), port("E", (0.5, 0.5))
    s, w = port("S", (0.5, 0.5)), port("W", (-0.5, 0.5))

    def one(*ps, **kw):
        return lambda d: d.update(directions="one", ports=list(ps), **kw)
    case("one direction, a north port alone accepted", box, one(n))
    case("one direction, ports_turn, a north port alone refused naming E, S, W", box,
         one(n, ports_turn=True), missing=["E", "S", "W"])
    case("one direction, ports_turn, all four faces accepted", box, one(n, e, s, w, ports_turn=True))
    case("one direction, ports_turn, no ports accepted", box, one(ports_turn=True))


def test_flag(box):
    print("flag")
    n = port("N", (-0.5, -0.5))
    case("ports_turn false accepted (one direction, a north port alone)", box,
         lambda d: d.update(directions="one", ports=[n], ports_turn=False))
    for label, v in (("1", 1), ('"true"', "true"), ("null", None)):
        case(f"ports_turn {label} refused", box, lambda d, v=v: d.update(ports_turn=v), field="ports_turn")


def test_declare(box):
    print("declare")
    elevation, ppt = rig_numbers()
    sys.modules["rig"] = types.SimpleNamespace(ELEVATION=elevation, PX_PER_TILE=ppt)   # declare() reads these
    given = {k: v for k, v in box.items() if k not in ("canvas", "rig")}
    with tempfile.TemporaryDirectory() as tmp:
        plain, flagged, refused = (os.path.join(tmp, d) for d in ("plain", "flagged", "refused"))
        contract.declare(plain, canvas=box["canvas"], **given)
        with open(os.path.join(plain, contract.FILE)) as f:
            text = f.read()
        before = dict(footprint=box["footprint"], canvas=box["canvas"], directions=box["directions"],
                      passes=box["passes"], animations=box["animations"], ports=box["ports"], rig=box["rig"])
        check("without ports_turn: no ports_turn key", "ports_turn" not in json.loads(text), text[:200])
        check("without ports_turn: render.json byte for byte as before the field",
              text == json.dumps(before, indent=1), "differs")
        contract.declare(flagged, canvas=box["canvas"], ports_turn=True, **given)
        with open(os.path.join(flagged, contract.FILE)) as f:
            got = json.load(f).get("ports_turn")
        check("with ports_turn=True: render.json says true", got is True, f"ports_turn {got!r}")
        try:
            contract.declare(refused, canvas=box["canvas"], **dict(given, ports=[port("N", (-0.5, -0.5))]))
            check("turned with a north port alone: declare refuses", False, "accepted")
        except contract.ContractError as e:
            check("turned with a north port alone: declare refuses", "E, S, W" in str(e), str(e))
        check("refused: no render.json written", not os.path.exists(os.path.join(refused, contract.FILE)))


def main():
    if len(sys.argv) != 1:
        sys.exit(__doc__.split("\n\n")[1])
    box = box_decl()
    test_reach(box)
    test_box(box)
    test_hv(box)
    test_one(box)
    test_flag(box)
    test_declare(box)
    print(f"{'FAIL' if FAILED else 'PASS'}: {len(FAILED)} case(s) failed" + "".join(f"\n  {f}" for f in FAILED))
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
