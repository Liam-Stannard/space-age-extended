"""What a model tells the packers: render.json, and the names its renders take.

A model writes render.json beside its renders (declare(), below), and pack.py
and pack_ports.py read it (load()). Neither packer knows a building, a size or
a pass: everything they act on is declared here.

  footprint   [w, h] in tiles, as the model faces north
  canvas      [w, h] in sprite px of the renders beside this file; the entity
              origin is the canvas centre
  directions  "one", "four" (north, east, south, west) or
              "horizontal-vertical" (vertical = as modelled, horizontal = turned
              to face east). A model with more than one renders every pass per
              direction by turning its root about the vertical axis, camera
              fixed, into <pass>-<direction>.png
  passes      [{name, kind, sheet, over}], one render each per direction:
                plate   the machine; Appendix C is measured on it
                shadow  the ground catcher alone; packed black
                glow    this pass minus the `over` pass, drawn additively
                paint   this pass where it differs from the `over` pass, drawn
                        as ordinary paint over it: a working layer such as
                        frost, rime or a heat seam that the idle plate must not
                        carry, shown only while the machine works
                light   a white-cut lens the engine tints (alpha above 8 kept)
                still   every animation at frame 0 with the machine: the
                        reference for the frame-0 check; not packed
  animations  [{name, frames, motion, path}], frames <name>-NN.png (and
              <name>-NN-<direction>.png). motion "turn": a part turning about
              its own axis, held to its centroid. motion "slide": a part moving
              in a straight line, whose `path` is its motion curve -- one
              [x, y, z] per frame, the part's offset in tiles as modelled
              (facing north; x east, y north, z up), the same numbers the model
              moves it by. Its centroid in every frame must land on that curve,
              and on its line, to within 1 px
  ports       [{tile, face}]: one fitting per face, `tile` the centre of the
              footprint tile it sits on (tiles, y down, entity centre 0,0, as a
              pipe connection's position), `face` N, E, S or W. Rendered with
              the model facing north, as port-<face>.png and cover-<face>.png
  rig         {elevation, px_per_tile}: the camera's, copied from rig.py by
              declare(), so the packers can put a tile on the screen

Run as a script, it lists a render directory's plate renders, one per direction:
  python3 contract.py plates <render-dir>
"""
import json
import math
import os
import sys

DIRECTIONS = {
    "one": [("", 0)],
    "four": [("north", 0), ("east", 90), ("south", 180), ("west", 270)],
    "horizontal-vertical": [("vertical", 0), ("horizontal", 90)],
}
KINDS = ("plate", "shadow", "glow", "paint", "light", "still")
WORKING = ("glow", "paint")             # the kinds drawn over an `over` plate while working
MOTIONS = ("turn", "slide")
FACES = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}     # tiles, y down
FILE = "render.json"


class ContractError(Exception):
    """A model's declaration, or its renders, do not hold to the contract."""


def named(stem, direction):
    """A pass's or sheet's file stem in one direction."""
    return f"{stem}-{direction}" if direction else stem


def frame(anim, f, direction=""):
    return named(f"{anim}-{f:02d}", direction)


def footprint_in(decl, direction):
    """The footprint as the engine sees it in a direction: turned a quarter, w and h swap."""
    w, h = decl["footprint"]
    deg = dict(DIRECTIONS[decl["directions"]])[direction]
    return (h, w) if deg % 180 else (w, h)


def each_direction(root, directions):
    """Turn `root` to face each direction in turn, yielding its name.

    Clockwise seen from above, as the engine turns a building: north (+Y, the
    way it was modelled) goes to east (+X). The camera and sun stay put, so the
    light falls on each face as it would in game.
    """
    for name, deg in DIRECTIONS[directions]:
        root.rotation_euler.z = -math.radians(deg)
        yield name
    root.rotation_euler.z = 0.0


def declare(out_dir, *, footprint, canvas, directions, passes=(), animations=(), ports=()):
    """Write render.json into out_dir: called by a model, in Blender, before it renders."""
    import rig          # in Blender only: the packers read the numbers from render.json
    decl = dict(footprint=footprint, canvas=canvas, directions=directions,
                passes=passes, animations=animations, ports=ports,
                rig=dict(elevation=math.degrees(rig.ELEVATION), px_per_tile=rig.PX_PER_TILE))
    validate(decl, out_dir)
    decl = json.loads(json.dumps(decl))     # as the packers will read it: tuples are lists
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, FILE), "w") as f:
        json.dump(decl, f, indent=1)
    return decl


def load(render_dir):
    path = os.path.join(render_dir, FILE)
    if not os.path.isfile(path):
        raise ContractError(f"{path} is missing: the model did not declare itself "
                            f"(contract.declare writes it beside the renders)")
    try:
        with open(path) as f:
            decl = json.load(f)
    except (ValueError, UnicodeDecodeError) as e:
        raise ContractError(f"{path}: is not JSON: {e}") from None
    validate(decl, path)
    return decl


def _number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _whole(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _seq(v, n=None):
    return isinstance(v, (list, tuple)) and (n is None or len(v) == n)


def _stem(v):
    """A name that can be a file stem: a non-empty string with no path in it."""
    return isinstance(v, str) and v.strip() != "" and "/" not in v and "\\" not in v


def validate(decl, where):
    """Hold a declaration to the contract, naming the field that breaks it.

    Every field is checked for its type as well as its value, so nothing the
    packers read can fail on them later with a bare KeyError or TypeError.
    """
    def bad(field, msg):
        raise ContractError(f"{where}: {field}: {msg}")

    if not isinstance(decl, dict):
        raise ContractError(f"{where}: is a {type(decl).__name__}, not an object of fields")
    for key in ("footprint", "canvas", "directions", "passes", "animations", "ports", "rig"):
        if key not in decl:
            bad(key, "is not declared")
    if not isinstance(decl["directions"], str) or decl["directions"] not in DIRECTIONS:
        bad("directions", f"{decl['directions']!r} is not one of {', '.join(DIRECTIONS)}")
    for key, unit in (("footprint", "tiles"), ("canvas", "px")):
        v = decl[key]
        if not (_seq(v, 2) and all(_whole(c) and c > 0 for c in v)):
            bad(key, f"{v!r} is not [w, h], two whole numbers of {unit} above 0")
    rig = decl["rig"]
    if not isinstance(rig, dict):
        bad("rig", f"{rig!r} is not an object {{elevation, px_per_tile}}")
    if not (_number(rig.get("elevation")) and 0 < rig["elevation"] < 90):
        bad("rig.elevation", f"{rig.get('elevation')!r} is not an angle in degrees between 0 and 90")
    if not (_number(rig.get("px_per_tile")) and rig["px_per_tile"] > 0):
        bad("rig.px_per_tile", f"{rig.get('px_per_tile')!r} is not a number of px above 0")
    for key in ("passes", "animations", "ports"):
        if not _seq(decl[key]):
            bad(key, f"{decl[key]!r} is not a list")
        for i, item in enumerate(decl[key]):
            if not isinstance(item, dict):
                bad(f"{key}[{i}]", f"{item!r} is not an object")

    names, sheets = set(), set()
    for i, p in enumerate(decl["passes"]):
        field = f"passes[{i}]"
        if "name" not in p:
            bad(f"{field}.name", "is missing: every pass needs a name, its renders' file stem")
        if not _stem(p["name"]):
            bad(f"{field}.name", f"{p['name']!r} is not a name (a non-empty string, no path in it)")
        if p["name"] in names:
            bad(f"{field}.name", f"{p['name']!r} is declared twice")
        names.add(p["name"])
        if p.get("kind") not in KINDS:
            bad(f"{field}.kind", f"{p.get('kind')!r} is not one of {', '.join(KINDS)}")
        if p["kind"] != "still":
            if not _stem(p.get("sheet")):
                bad(f"{field}.sheet", f"{p.get('sheet')!r}: pass {p['name']!r} names no sheet to pack into")
            if p["sheet"] in sheets:
                bad(f"{field}.sheet", f"{p['sheet']!r} is already another pass's sheet")
            sheets.add(p["sheet"])
    kinds = [p["kind"] for p in decl["passes"]]
    if decl["passes"] and kinds.count("plate") != 1:
        bad("passes", f"declares {kinds.count('plate')} plate passes; Appendix C needs exactly one")
    for i, p in enumerate(decl["passes"]):
        if p["kind"] in WORKING and not any(q["name"] == p.get("over") and q["kind"] == "plate"
                                            for q in decl["passes"]):
            bad(f"passes[{i}].over", f"{p['kind']} pass {p['name']!r} is over {p.get('over')!r}, "
                f"which is not a plate pass")

    for i, a in enumerate(decl["animations"]):
        field = f"animations[{i}]"
        if "name" not in a:
            bad(f"{field}.name", "is missing: every animation needs a name, its frames' file stem")
        if not _stem(a["name"]):
            bad(f"{field}.name", f"{a['name']!r} is not a name (a non-empty string, no path in it)")
        if a["name"] in sheets:
            bad(f"{field}.name", f"{a['name']!r} is already the name of a sheet: an animation packs "
                f"into a sheet of its own name")
        sheets.add(a["name"])
        if not (_whole(a.get("frames")) and a["frames"] >= 2):
            bad(f"{field}.frames", f"{a.get('frames')!r}: animation {a['name']!r} needs a whole "
                f"number of frames, at least two")
        if a.get("motion") not in MOTIONS:
            bad(f"{field}.motion", f"{a.get('motion')!r} is not one of {', '.join(MOTIONS)}")
        if a["motion"] == "slide":
            path = a.get("path")
            if not (_seq(path, a["frames"]) and all(_seq(p, 3) and all(_number(c) for c in p) for p in path)):
                bad(f"{field}.path", f"slide {a['name']!r} needs a path of {a['frames']} [x, y, z] "
                    f"offsets in tiles, one per frame")
            steps = [[c - c0 for c, c0 in zip(p, path[0])] for p in path]
            far = max(steps, key=lambda v: math.hypot(*v))
            if math.hypot(*far) == 0:
                bad(f"{field}.path", f"slide {a['name']!r} has a path that does not move")
            for v in steps:             # every offset parallel to the longest: one straight line
                cross = (v[1] * far[2] - v[2] * far[1], v[2] * far[0] - v[0] * far[2], v[0] * far[1] - v[1] * far[0])
                if math.hypot(*cross) > 1e-6 * math.hypot(*far) * max(1.0, math.hypot(*v)):
                    bad(f"{field}.path", f"slide {a['name']!r} has a path that is not a straight line")
    if decl["animations"] and decl["passes"] and "still" not in kinds:
        bad("passes", "declares animations but no still pass to hold their frame 0 to")

    w, h = decl["footprint"]
    faces = set()
    for i, p in enumerate(decl["ports"]):
        field = f"ports[{i}]"
        if not isinstance(p.get("face"), str) or p["face"] not in FACES:
            bad(f"{field}.face", f"{p.get('face')!r} is not one of N, E, S, W")
        if p["face"] in faces:
            bad(f"{field}.face", f"a second port on face {p['face']}: the engine draws one picture per face")
        faces.add(p["face"])
        if not (_seq(p.get("tile"), 2) and all(_number(c) for c in p["tile"])):
            bad(f"{field}.tile", f"{p.get('tile')!r} is not [x, y] in tiles")
        x, y = p["tile"]
        edge = {"N": y == -h / 2 + 0.5, "S": y == h / 2 - 0.5,
                "E": x == w / 2 - 0.5, "W": x == -w / 2 + 0.5}[p["face"]]
        inside = abs(x) <= w / 2 - 0.5 and abs(y) <= h / 2 - 0.5 and (x - (w - 1) / 2) % 1 == 0 \
            and (y - (h - 1) / 2) % 1 == 0
        if not (edge and inside):
            bad(f"{field}.tile", f"{list(p['tile'])} is not a tile centre on the {p['face']} edge "
                f"of a {w}x{h} footprint")


def screen(decl, offset, direction):
    """A model-space offset (tiles: x east, y north, z up, as modelled) in screen px
    (x right, y down) once the building is turned to `direction`.

    The ground projects square (rig.py's STRETCH), so a tile across the ground is
    px_per_tile on the screen either way; a tile of height is cos(elevation) of that.
    """
    a = -math.radians(dict(DIRECTIONS[decl["directions"]])[direction])
    x, y, z = offset
    east, north = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
    ppt = decl["rig"]["px_per_tile"]
    return east * ppt, -(north + z * math.cos(math.radians(decl["rig"]["elevation"]))) * ppt


def outside(port):
    """Centre of the tile the port points into, which the engine draws its pipe picture from."""
    dx, dy = FACES[port["face"]]
    return port["tile"][0] + dx, port["tile"][1] + dy


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "plates":
        sys.exit("usage: contract.py plates <render-dir>")
    try:
        d = load(sys.argv[2])
    except ContractError as e:
        sys.exit(str(e))
    plate = next(p["name"] for p in d["passes"] if p["kind"] == "plate")
    for direction, _ in DIRECTIONS[d["directions"]]:
        print(os.path.join(sys.argv[2], named(plate, direction) + ".png"))
