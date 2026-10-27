"""The Radiant Generator's --collide (radiant_generator.py): every moving part in every frame of
the loop against every fixed part shown that frame and every other layer's moving parts; then
the fixed machine, part against part. By BVH, in Blender, as the Reaction Plant's circulator.py
does it; the lines it prints are read by tools/blender/measure.py's collide step.

A clash is two parts' faces crossing, or one wholly inside a closed other. MEANT lists the
moving contacts that are the design (a cell let down into its pocket); MEANT_FIXED and seated()
the fixed ones (a fastener on its host). Each is written to collide.txt with its reason; only a
contact no rule explains is printed as a pair line, which fails the run. The counts printed are
of those alone."""
import os
import re

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

DEEP = 0.03         # tiles: 2 px at the sprite's scale; less is two faces meeting
# T08i: a tray's cables and sleeves against its floor, rails and cleats (rg_kit.TRAY_FRAME) are judged,
# not excused as one unit's parts or a cable on its host (T08d's cables ran through the tray's clamp bars
# unflagged); they lie on the floor and under the cleats with a few thousandths to spare, so this is tight
DEEP_TRAY = 0.004
DETAIL_MATS = {"bolt", "seam", "stencil", "hazard", "label", "gauge", "needle", "red", "yellow", "brass", "dark",
               "lamp", "oil", "glint", "bezel", "sil"}

# (layer, this part, the other part: regexes on "name[material] at (x,y,z)", why)
MEANT = [
    ("^crane$", r"\[(lead|lead_new|dark|yellow|bare|dark_steel)\]", r"^carousel: .* at \(-0\.2\d,\+0\.4\d",
     "a hoist letting its cell down into the pick pocket and lifting one out (the pocket's bore is drawn as a "
     "dark disc on the table, not cut; the table's own cells stand in it the same way)"),
    ("^carousel$", r"\[(lead|lead_new|dark|dark_steel|bolt|yellow|bare)\] at \(-0\.2\d,\+0\.4\d", r"^crane: ",
     "the pick pocket a hoist lets its cell down into (the same contact, the carousel's side of it)"),
    ("^commutator$", "", r"\[brass\] at \(\+1\.\d\d,-1\.\d\d", "a brush bearing on the commutator"),
    ("^coupling-converter$", "", r"\[bare\] at \(-0\.1\d,-1\.95,0\.60\)", "the coupling on its shaft"),
    ("^gauge-", r"\[needle\]", r"\[gauge\]", "a needle on its own dial"),
]
# (this fixed part, the other: regexes, why)
MEANT_FIXED = [
    (r"\[lead_new\] at \(\+2\.15,", "", "a tube's lead heat arm, let into the crucible's wall and into the tube's own socket"),
    (r"^Cube\.\d+\[(lead|dark_steel)\] at \(-2\.28,-0\.30", r"\[(lead|bare|dark_steel)\] at \(-1\.05,\+0\.45",
     "the spent bin built against the drum's west side under the chute, its back let into the drum (as round 7 "
     "placed it: moved out, it would stand past the footprint's west edge)"),
]


def check(K, machine, part, layers, pose, nf, show):
    out_dir = K.OUT
    lines, notes = [], []

    def out(s_):
        print(s_, flush=True)
        lines.append(s_)
    RI = K.ROOT.matrix_world.inverted()

    def mat_of(o):
        return o.data.materials[0].name if getattr(o.data, "materials", None) and o.data.materials \
            and o.data.materials[0] else "-"

    def world_mesh(o):
        dg = bpy.context.evaluated_depsgraph_get()
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ev.matrix_world
        vs = [mw @ v.co for v in me.vertices]
        ps = [tuple(p_.vertices) for p_ in me.polygons]
        ev.to_mesh_clear()
        return vs, ps

    def aabb(vs):
        xs, ys, zs = zip(*vs)
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def meet(a, b):
        return all(a[0][i] <= b[1][i] and b[0][i] <= a[1][i] for i in range(3))

    def inside(tree, p_):
        d = Vector((0.5774, 0.5771, 0.5777))
        n, o = 0, p_.copy()
        for _ in range(64):
            hit = tree.ray_cast(o, d)
            if hit[0] is None:
                break
            n += 1
            o = hit[0] + d * 1e-5
        return n % 2 == 1

    class Part:
        def __init__(self, o):
            self.o = o
            self.vs, ps = world_mesh(o)
            self.box = aabb(self.vs) if self.vs else None
            self.tree = BVHTree.FromPolygons(self.vs, ps) if ps else None
            c = RI @ (sum(self.vs, Vector()) / len(self.vs)) if self.vs else Vector()
            lo, hi = (RI @ Vector(self.box[0]), RI @ Vector(self.box[1])) if self.vs else (c, c)
            self.lo = Vector((min(lo.x, hi.x), min(lo.y, hi.y), min(lo.z, hi.z)))
            self.hi = Vector((max(lo.x, hi.x), max(lo.y, hi.y), max(lo.z, hi.z)))
            self.c = c
            self.size = max(abs(hi.x - lo.x), abs(hi.y - lo.y), abs(hi.z - lo.z))
            self.mat = mat_of(o)
            self.desc = f"{o.name}[{self.mat}] at ({c.x:+.2f},{c.y:+.2f},{c.z:.2f})"

    def clash(a, b):
        if a.tree is None or b.tree is None or not meet(a.box, b.box):
            return None
        if a.tree.overlap(b.tree):
            return "cross"
        if meet(b.box, (a.vs[0], a.vs[0])) and inside(b.tree, a.vs[0]):
            return "inside"
        if meet(a.box, (b.vs[0], b.vs[0])) and inside(a.tree, b.vs[0]):
            return "contains"
        return None

    def depth(a, b):
        """How far a's vertices reach inside b (tiles, model space)."""
        d = 0.0
        for v in a.vs:
            if meet(b.box, (v, v)) and inside(b.tree, v):
                hit = b.tree.find_nearest(v)
                if hit[0] is not None:
                    d = max(d, (RI.to_3x3() @ (hit[0] - v)).length)
        return d

    meshes = [o for o in machine if o.type == "MESH" and o not in K.STAINS]
    moving = [o for o in meshes if part[o.name] in layers]
    fixed_objs = [o for o in meshes if part[o.name] not in layers]
    out(f"COLLIDE {len(meshes)} parts, {len(moving)} moving in {len(layers)} layers; the {nf} loop frames")

    def meant(table, *descs):
        for row in table:
            *pats, why = row
            if all(re.search(p_, d_) for p_, d_ in zip(pats, descs)):
                return why
        return None

    fixed = {}
    hits = {}
    for f in range(nf):
        pose(f)
        bpy.context.view_layer.update()
        for o in fixed_objs:
            if o.name not in fixed and show.get(o.name, True):
                fixed[o.name] = Part(o)
        mparts = [(part[o.name], Part(o)) for o in moving if show.get(o.name, True)]
        for la, a in mparts:
            for o in fixed_objs:
                if not show.get(o.name, True):
                    continue
                b = fixed[o.name]
                kind = clash(a, b)
                if kind:
                    hits.setdefault((la, a.desc, b.desc, kind), []).append(f)
        for i, (la, a) in enumerate(mparts):
            for lb, b in mparts[i + 1:]:
                if la == lb:
                    continue
                kind = clash(a, b)
                if kind:
                    hits.setdefault((la, a.desc, lb + ": " + b.desc, kind), []).append(f)
    n_meant = n_clash = 0
    for (g, ad, bd, kind), fs in sorted(hits.items()):
        why = meant(MEANT, g, ad, bd)
        fr = f"{fs[0]}-{fs[-1]}" if fs == list(range(fs[0], fs[-1] + 1)) else ",".join(map(str, fs))
        if why:
            n_meant += 1
            notes.append(f"meant  moving [{g}] {ad} with {bd}: {kind}, frames {fr}  ({why})")
        else:
            n_clash += 1
            out(f"COLLIDE CLASH moving [{g}] {ad} x {bd}: {kind}, frames {fr}")
    out(f"COLLIDE moving: {n_clash} clashes, {n_meant} meant contacts (collide.txt)")

    # the fixed machine, part against part, at frame 0
    pose(0)
    bpy.context.view_layer.update()
    fx = [fixed[o.name] for o in fixed_objs if o.name in fixed]
    pairs, n_real = [], 0
    for i, a in enumerate(fx):
        for b in fx[i + 1:]:
            kind = clash(a, b)
            if not kind:
                continue
            in_tray = tray_pair(a, b, K)
            why = None if in_tray else seated(a, b, MEANT_FIXED, K)
            dp = 0.0 if why else max(depth(a, b), depth(b, a))
            tag = "seated" if why else ("REAL" if dp > (DEEP_TRAY if in_tray else DEEP) else "touch")
            pairs.append((tag, -dp, f"{tag} {a.desc} with {b.desc}: {kind}, {dp:.3f} deep" + (f"  ({why})" if why else "")))
            if tag == "REAL":
                n_real += 1
                out(f"COLLIDE REAL fixed {a.desc} x {b.desc}: {kind}, {dp:.3f} deep")
    order = {"REAL": 0, "touch": 1, "seated": 2}
    out(f"COLLIDE fixed: {n_real} clashes (reaching more than {DEEP} tile into each other, no rule explains "
        f"them), {len(fx)} fixed parts, {len(pairs)} touching pairs (collide.txt)")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "collide.txt"), "w") as f_:
        f_.write("\n".join(lines) + "\n\n" + "\n".join(notes) + "\n\n"
                 + "\n".join(l_ for _, _, l_ in sorted(pairs, key=lambda p_: (order[p_[0]], p_[1], p_[2]))) + "\n")


def tray_pair(a, b, K):
    """A cable or label sleeve against a tray's floor, rails or cleats (T08i)."""
    frame = getattr(K, "TRAY_FRAME", set())
    for x, y in ((a, b), (b, a)):
        if x.o.name in frame and (y.mat.startswith("cable_") or y.mat == "label"):
            return True
    return False


def seated(a, b, table, K):
    """Why two touching fixed parts are meant to touch, or None."""
    floor = K.FLOOR
    if K.UNIT.get(a.o.name) == K.UNIT.get(b.o.name):
        return "one unit's own parts"
    for x, y in ((a, b), (b, a)):
        ends = K.RUN_ENDS.get(K.UNIT.get(x.o.name))
        if ends:
            RI = K.ROOT.matrix_world.inverted()
            pts = [RI @ v for v in x.vs if meet_pt(y, v)] or [RI @ v for v in y.vs if meet_pt(x, v)]
            if pts and all(min((p_ - ends[0]).length, (p_ - ends[1]).length) < 0.35 for p_ in pts):
                return "a run's end let into what it serves"
    for x, y in ((a, b), (b, a)):
        for xr, yr, why in table:
            if re.search(xr, x.desc) and re.search(yr, y.desc):
                return why
    for x, y in ((a, b), (b, a)):
        if x.o.name in floor and y.lo.z < 0.14 and y.o.name not in floor:
            return "a unit standing on the deck, its foot let into the slab (the deck runs under the units)"
        if y.mat in ("tube_glass", "pane") and y.size > x.size:
            return "inside its glass envelope"
        if y.hi.z <= 0.2 and y.lo.z < 0.01 and x.lo.z < 0.2:
            return "standing on a foot plate or skirt, its foot let into it"
    for x, y in ((a, b), (b, a)):
        if x.mat in DETAIL_MATS or x.mat.startswith("cable_"):
            return f"a {x.mat} detail on its host"
        if x.size < 0.16:
            return "a small fitting on its host"
    return None


def meet_pt(part, v):
    """v (world) inside part's box."""
    lo, hi = part.box
    return all(lo[i] <= v[i] <= hi[i] for i in range(3))
