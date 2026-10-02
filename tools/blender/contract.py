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
KINDS = ("plate", "shadow", "glow", "light", "still")
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
    decl = dict(footprint=list(footprint), canvas=list(canvas), directions=directions,
                passes=[dict(p) for p in passes], animations=[dict(a) for a in animations],
                ports=[dict(tile=list(p["tile"]), face=p["face"]) for p in ports],
                rig=dict(elevation=math.degrees(rig.ELEVATION), px_per_tile=rig.PX_PER_TILE))
    validate(decl, out_dir)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, FILE), "w") as f:
        json.dump(decl, f, indent=1)
    return decl


def load(render_dir):
    path = os.path.join(render_dir, FILE)
    if not os.path.isfile(path):
        raise ContractError(f"{path} is missing: the model did not declare itself "
                            f"(contract.declare writes it beside the renders)")
    with open(path) as f:
        decl = json.load(f)
    validate(decl, path)
    return decl


def validate(decl, where):
    def bad(msg):
        raise ContractError(f"{where}: {msg}")
    for key in ("footprint", "canvas", "directions", "passes", "animations", "ports", "rig"):
        if key not in decl:
            bad(f"declares no {key!r}")
    if decl["directions"] not in DIRECTIONS:
        bad(f"directions {decl['directions']!r} is not one of {', '.join(DIRECTIONS)}")
    if len(decl["footprint"]) != 2 or min(decl["footprint"]) <= 0:
        bad(f"footprint {decl['footprint']} is not [w, h] in tiles")
    if len(decl["canvas"]) != 2 or min(decl["canvas"]) <= 0:
        bad(f"canvas {decl['canvas']} is not [w, h] in px")
    names = set()
    for p in decl["passes"]:
        if p.get("kind") not in KINDS:
            bad(f"pass {p.get('name')!r} has kind {p.get('kind')!r}, not one of {', '.join(KINDS)}")
        if p["kind"] != "still" and not p.get("sheet"):
            bad(f"pass {p['name']!r} names no sheet to pack into")
        if p["name"] in names:
            bad(f"pass {p['name']!r} is declared twice")
        names.add(p["name"])
    kinds = [p["kind"] for p in decl["passes"]]
    if decl["passes"] and kinds.count("plate") != 1:
        bad(f"declares {kinds.count('plate')} plate passes; Appendix C needs exactly one")
    for p in decl["passes"]:
        if p["kind"] == "glow" and not any(q["name"] == p.get("over") and q["kind"] == "plate"
                                           for q in decl["passes"]):
            bad(f"glow pass {p['name']!r} is over {p.get('over')!r}, which is not a plate pass")
    for a in decl["animations"]:
        if not a.get("name") or int(a.get("frames", 0)) < 2:
            bad(f"animation {a} needs a name and at least two frames")
        if a.get("motion") not in MOTIONS:
            bad(f"animation {a['name']!r} has motion {a.get('motion')!r}, not one of {', '.join(MOTIONS)}")
        if a["motion"] == "slide":
            path = a.get("path") or []
            if len(path) != int(a["frames"]) or any(len(p) != 3 for p in path):
                bad(f"slide {a['name']!r} needs a path of {a['frames']} [x, y, z] offsets, one per frame")
            steps = [[c - c0 for c, c0 in zip(p, path[0])] for p in path]
            far = max(steps, key=lambda v: math.hypot(*v))
            if math.hypot(*far) == 0:
                bad(f"slide {a['name']!r} has a path that does not move")
            for v in steps:             # every offset parallel to the longest: one straight line
                cross = (v[1] * far[2] - v[2] * far[1], v[2] * far[0] - v[0] * far[2], v[0] * far[1] - v[1] * far[0])
                if math.hypot(*cross) > 1e-6 * math.hypot(*far) * max(1.0, math.hypot(*v)):
                    bad(f"slide {a['name']!r} has a path that is not a straight line")
    if decl["animations"] and decl["passes"] and "still" not in kinds:
        bad("declares animations but no still pass to hold their frame 0 to")
    w, h = decl["footprint"]
    faces = [p["face"] for p in decl["ports"]]
    for p in decl["ports"]:
        if p["face"] not in FACES:
            bad(f"port {p} faces {p['face']!r}, not one of N, E, S, W")
        if faces.count(p["face"]) > 1:
            bad(f"two ports on face {p['face']}: the engine draws one picture per face")
        x, y = p["tile"]
        edge = {"N": y == -h / 2 + 0.5, "S": y == h / 2 - 0.5,
                "E": x == w / 2 - 0.5, "W": x == -w / 2 + 0.5}[p["face"]]
        inside = abs(x) <= w / 2 - 0.5 and abs(y) <= h / 2 - 0.5 and (x - (w - 1) / 2) % 1 == 0 \
            and (y - (h - 1) / 2) % 1 == 0
        if not (edge and inside):
            bad(f"port tile {p['tile']} is not a tile centre on the {p['face']} edge of a {w}x{h} footprint")


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
