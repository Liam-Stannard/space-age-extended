"""The Ballast Drill's fluid rig (task ballast-drill-ports, T03d): the casings cut back, the
rig, its wall fittings and runs, per take; imported by rig_take.py into the signed-off
model's namespace G.

What vanilla's big mining drill does (rig-round/study, the study sheet): two runs per
direction, each linking a side connection to the rear connection round the corner between
them, laid along the drill's own frame at the perimeter, with a cast junction body at every
connection; north of the centre drawn behind (pipe-connections), south of it in front
(pipe-connections-front); a dry drill shows the frame alone. So here, in every direction, the
runs are W-S(-1) and E-S(1) turned with the drill, on a gallery round the deck's perimeter.

THE CUT-BACK (the plate, every direction: the plate does not turn, and over the four
directions the runs use all four corners and all eight connection tiles). The casings give
way in a band round the perimeter -- outside a rounded square (straights 1.90 out from the
centre, corners on arcs of 0.40 about (+-1.5, +-1.5)), from Z0 up to Z1: the batter's outer
edge planed to a ledge at Z0, the south housings' lower fronts, the north perimeter castings,
the drive cabinets' feet, the south wings' undersides over the notches; the band's small
parts (bolts, clips, glands) removed, and every hose or cable crossing it removed whole (a cut
hose end would hang loose: the clipping rule). The south-west housing's door, gauge and
maker's plate move up onto the face that overhangs the gallery.

THE RIG (dry, in the plate): a curved cast girder over each corner notch, carried on a stool
on the leg, with saddles for the run; on the faces, short stubs of it onto the ledge.

WET (per direction, the wet layers only): at each connection a wall fitting set into the wall
(a slot cut into the casting, lined, a bolted frame round its mouth -- the Reaction Plant
casing's "recessed boss", here a cast riser body standing in the slot) with its sleeve and end
ring at the connection, calibrated to vanilla's pipe as the signed-off port pictures are
(ballast_drill.py fitting()); up from it a cast junction head at the run's height; the run from
head to head along the gallery, at the connection's bore all the way (0.56 outer), on the
girder's saddles at the corners and on stools of its own on the ledge elsewhere.
"""
import json
import math
import os
import shutil

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

# ---------------------------------------------------------------- the gallery's numbers
R_AX = 2.215            # the run's axis, out from the centre along a face's normal
R_RUN = 0.28            # the connection's bore: the signed-off stub's radius (outer 0.56)
ARC_C = 1.5             # corner arcs about (+-1.5, +-1.5)
ARC_R = R_AX - ARC_C    # 0.715: the run's bend radius round a corner
CUT_IN = 1.86           # the cut-back's inner face on the straights: inside the run's flanges
CUT_ARC = ARC_R - (R_AX - CUT_IN)  # 0.36: and round the corners
Z0, Z1 = 0.60, 1.40     # the cut-back's floor (the ledge) and roof
Z_RUN = 1.00            # the run's axis: its underside 0.72
R_BODY = 0.29           # the junction's cast body and head
POCKET_HW = 0.38        # the wall slot's half-width: the end ring's (0.343) and a lining
BEAM_Z0, BEAM_Z1 = 0.602, 0.65    # under the junction heads' flanges (0.66)
SADDLE_TOP = Z_RUN - R_RUN - 0.002
SADDLE_HL = 0.305       # a saddle's half-length across the run: under the clamp's feet
FLANGE_R = R_RUN + 0.06
STUB_SADDLE = 1.40      # the girder stubs' saddle, along the face: clear of the bend's flange at 1.5

FIT_CONNS = [(-2, -1, "W"), (2, -1, "E"), (1, 2, "S"), (-1, 2, "S")]     # big-mining-drill.lua:570-580


def fit_conns(deg):
    """The connections in a direction turned deg clockwise: (x, y, face), y down (as
    ballast_drill.py's fit_conns, in a section of it rig_take.py does not run)."""
    out = []
    for x, y, f in FIT_CONNS:
        for _ in range(round(deg / 90) % 4):
            x, y, f = -y, x, "NESW"[("NESW".index(f) + 1) % 4]
        out.append((x, y, f))
    return out


TAKES = {
    # rigid: cast iron pipe, flanged at every bend and bay; painted junction heads
    "rigid": dict(run="rigid", feed=False),
    # hose: a heavy ribbed hose of the bore, crimped into the junction heads' flanges
    "hose": dict(run="hose", feed=False),
    # feed: rigid, and where each run crosses a bay a tee and a branch of the bore down the
    # bay into a flanged nozzle on the riser: the fluid to the cutting head behind it
    "feed": dict(run="rigid", feed=True),
    # low: vanilla's level -- the casing's skirt cut back to the ground all round (but the bays'
    # floors), the run on the ground at the connection's own height on stools of its own, each
    # junction a cast tee standing in the gallery with a boss into the cut-back wall, and at each
    # corner the run swan-necked up over the leg's root; no girder: dry, the gallery is empty
    "low": dict(run="rigid", feed=False, level="low"),
}
Z_LOW = 0.48            # the low take's run axis: its underside 0.20, over the bays' aprons
Z_LOW_BAY = 0.57        # and over a bay: its flange's rim clear of the shut hatch
Z_APEX = 1.0            # its height over a leg, at the corner's middle


def main(G, take, pas, collide):
    if take not in TAKES:
        raise SystemExit(f"rig_parts: take {take!r} is not one of {', '.join(TAKES)}")
    Rig(G, take).run(pas, collide)


class Rig:
    def __init__(self, G, take):
        self.G, self.take, self.cfg = G, take, TAKES[take]
        self.log = {"take": take, "deleted": [], "cut": [], "moved": [], "sizes": {}}
        self.assembly = {}               # wet object name -> its assembly ("<d>:pair<k>")
        self.pocket_cutters = []
        self.pocket_targets = []
        self.dry = []                    # the rig's own plate parts
        self.low = self.cfg.get("level") == "low"
        self.z0 = -0.1 if self.low else Z0

    # ------------------------------------------------------------ helpers
    def bbox(self, o):
        G = self.G
        Binv = G["BODY"].matrix_world.inverted()
        cs = [Binv @ o.matrix_world @ Vector(c) for c in o.bound_box]
        return Vector([min(c[i] for c in cs) for i in range(3)]), Vector([max(c[i] for c in cs) for i in range(3)])

    def verts(self, o):
        G = self.G
        Binv = G["BODY"].matrix_world.inverted()
        dg = bpy.context.evaluated_depsgraph_get()
        e = o.evaluated_get(dg)
        me = e.to_mesh()
        mw = Binv @ o.matrix_world
        vs = [mw @ v.co for v in me.vertices]
        e.to_mesh_clear()
        return vs

    @staticmethod
    def outside_inner(x, y):
        ax, ay = abs(x), abs(y)
        if ax > ARC_C and ay > ARC_C:
            return math.hypot(ax - ARC_C, ay - ARC_C) >= CUT_ARC
        return ax >= CUT_IN or ay >= CUT_IN

    def in_cut(self, p):
        return self.z0 <= p.z <= Z1 and self.outside_inner(p.x, p.y)

    def inner_loop(self, n_arc=24):
        """The cut-back's inner face, counter-clockwise from the south face's middle."""
        pts = []
        for k in range(4):
            rot = Matrix.Rotation(math.pi / 2 * k, 2)
            seg = [Vector((x, -CUT_IN)) for x in [0.0 + ARC_C * i / 10 for i in range(0, 10)]]
            arc = [Vector((ARC_C + CUT_ARC * math.cos(t), -ARC_C + CUT_ARC * math.sin(t)))
                   for t in (-math.pi / 2 + math.pi / 2 * i / n_arc for i in range(n_arc))]
            seg2 = [Vector((CUT_IN, y)) for y in [-ARC_C + ARC_C * i / 10 for i in range(0, 10)]]
            for v in seg + arc + seg2:
                pts.append(rot @ v)
        return pts

    def cutter(self):
        """The cut-back's volume: between the inner face and a square well outside the
        footprint, from Z0 to Z1."""
        G = self.G
        inner = self.inner_loop()
        outer = [p * (2.9 / max(abs(p.x), abs(p.y))) for p in inner]

        def build(bm):
            n = len(inner)
            rows = []
            for loop, z in ((inner, self.z0), (outer, self.z0), (outer, Z1), (inner, Z1)):
                rows.append([bm.verts.new((p.x, p.y, z)) for p in loop])
            for a, b in zip(rows, rows[1:] + rows[:1]):
                for i in range(n):
                    j = (i + 1) % n
                    bm.faces.new((a[i], a[j], b[j], b[i]))
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        o = G["mesh_object"]("rigcut", build, "iron", "_cutters", 0)
        o.hide_render = True
        o.display_type = "WIRE"
        return o

    # ------------------------------------------------------------ the cut-back
    THIN_MATS = ("hose", "hose_brown", "cable", "grease", "copper", "c_red", "c_blue", "c_green", "c_yellow",
                 "c_black")
    SKIP_GROUPS = ("dust", "ore", "chute", "ring", "_cutters")

    def cut_back(self):
        G = self.G
        bpy.context.view_layer.update()
        cutter = self.cutter()
        # the south-west housing's door, louvres, hinges, handle, gauge and maker's plate: up
        # onto the face that overhangs the gallery
        cx_sw = G["HOUSES"][-1][0]
        lift = 0.62
        moved_roots = set()
        todo = []
        for g, objs in list(G["PARTS"].items()):
            if g in self.SKIP_GROUPS or g.startswith("rig-"):
                continue
            for o in list(objs):
                if o.type not in ("MESH", "CURVE"):
                    continue
                lo, hi = self.bbox(o)
                if hi.z < self.z0 or lo.z > Z1:
                    continue
                if self.low and self.protected(o, lo, hi):
                    continue
                corners = [Vector((x, y)) for x in (lo.x, hi.x) for y in (lo.y, hi.y)]
                if not any(self.outside_inner(c.x, c.y) for c in corners):
                    continue
                todo.append((g, o, lo, hi))
        plan = []
        for g, o, lo, hi in todo:
            c = (lo + hi) / 2
            mat = o.active_material.name if o.active_material else ""
            # the door and its fittings on the south-west housing's face
            if (hi.y < -2.39 and lo.y > -2.5 and -1.52 <= c.x <= -0.86 and 0.74 <= c.z <= 1.4 and lo.x > -1.6
                    and hi.z - lo.z < 0.7):
                plan.append(("move", g, o))
                continue
            vs = self.verts(o)
            inside = sum(1 for v in vs if self.in_cut(v))
            size = (hi - lo).length
            thin = mat in self.THIN_MATS or mat.startswith("c_")
            if thin or size < 0.3:
                if inside or (size < 0.3 and self.in_cut(c)):
                    plan.append(("delete", g, o))
                continue
            n_in, N = 0, 6
            for i in range(N):
                for j in range(N):
                    for k in range(N):
                        p = Vector((lo.x + (hi.x - lo.x) * (i + 0.5) / N, lo.y + (hi.y - lo.y) * (j + 0.5) / N,
                                    lo.z + (hi.z - lo.z) * (k + 0.5) / N))
                        n_in += self.in_cut(p)
            share = n_in / N ** 3
            if share == 0 and not inside:
                continue
            plan.append(("delete" if share >= 0.7 and not o.children else "cut", g, o))
        if self.cfg.get("feed"):
            # the riser's middle bolts, where the feed's nozzle is bolted on in a wet direction
            Binv = G["BODY"].matrix_world.inverted()
            for o in list(G["PARTS"]["body"]):
                if o.type != "MESH" or not o.name.startswith("Cylinder"):
                    continue
                p = Binv @ o.matrix_world.translation
                for f, nv in (("N", (0, 1)), ("S", (0, -1)), ("E", (1, 0)), ("W", (-1, 0))):
                    rad = p.x * nv[0] + p.y * nv[1]
                    lat = p.x if f in "NS" else p.y
                    if abs(rad - G["Y_STEP"]) < 0.02 and abs(lat) < 0.25 and 0.12 < p.z < 0.6:
                        mat = o.active_material.name if o.active_material else ""
                        if mat == "bolt":
                            plan.append(("delete", "body", o))
        for act, g, o in plan:
            if act == "move":
                root = o
                while root.parent is not None and root.parent != G["BODY"]:
                    root = root.parent
                if root.name not in moved_roots:
                    moved_roots.add(root.name)
                    root.location.z += lift
                    self.log["moved"].append(root.name)
            elif act == "delete":
                if o.name in bpy.data.objects:
                    self.delete(o, g)
            else:
                G["cut"](o, cutter)
                self.log["cut"].append(o.name)
        print(f"RIG cut-back: {len(self.log['cut'])} cut, {len(self.log['deleted'])} removed, "
              f"{len(self.log['moved'])} moved", flush=True)

    def protected(self, o, lo, hi):
        """The low take's skirt cut reaches the ground: what it leaves standing there -- each
        bay's floor (apron, kerb, slot frame, hatch, the bolts in them), the legs and their
        cast bands, the pads and what stands on them (the jacks). The wings' braces go: the
        wing they propped is cut back over the notch."""
        mat = o.active_material.name if o.active_material else ""
        c = (lo + hi) / 2
        if mat == "leg" and o.name.startswith("rod") and lo.z > 0.05:
            return False                                     # a brace
        if mat in ("leg", "hazard"):
            return True
        if o.name.startswith("rod") and mat == "iron_worn" and lo.z < 0.12:
            return True                                      # a leg's cast band
        for sx in (-1, 1):
            for sy in (-1, 1):
                if (Vector((c.x, c.y)) - Vector((sx * 2.12, sy * 2.12))).length < 0.5 and hi.z < 0.36:
                    return True                              # on a pad
        if hi.z <= 0.25:
            if abs(c.x) >= abs(c.y):
                lat = max(abs(lo.y), abs(hi.y))
            else:
                lat = max(abs(lo.x), abs(hi.x))
            if lat <= 0.72:
                return True                                  # a bay's floor
        return False

    def delete(self, o, g):
        G = self.G
        for ch in list(o.children):             # keep a child where it is
            mw = ch.matrix_world.copy()
            ch.parent = G["BODY"]
            ch.matrix_world = mw
        G["PARTS"][g].remove(o)
        self.log["deleted"].append(o.name)
        bpy.data.objects.remove(o, do_unlink=True)

    # ------------------------------------------------------------ parts
    def mat(self, name, fallback="steel"):
        return name if name in self.G["M"] else fallback

    def tube(self, pts, r, mat, group, seg=32, rib=0.0, pitch=0.07, caps=True, name="run"):
        G = self.G
        pts = [Vector(p) for p in pts]
        T, Ns, Bs, S = G["frames"](pts)

        def build(bm):
            rows = []
            for i, p in enumerate(pts):
                rr = r * (1 - rib * 0.5 * (1 - math.cos(2 * math.pi * S[i] / pitch))) if rib else r
                rows.append([bm.verts.new(p + (Ns[i] * math.cos(q) + Bs[i] * math.sin(q)) * rr)
                             for q in (2 * math.pi * k / seg for k in range(seg))])
            for a, b in zip(rows, rows[1:]):
                for k in range(seg):
                    bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
            if caps:
                bm.faces.new(list(reversed(rows[0])))
                bm.faces.new(rows[-1])
        return G["mesh_object"](name, build, mat, group, 0, smooth=True)

    def along(self, c, t, r, h, mat, group, verts=40, bevel=0.006):
        """A cylinder of radius r and length h centred at c, its axis along t."""
        G = self.G
        rot = Vector((0, 0, 1)).rotation_difference(Vector(t).normalized()).to_euler()
        return G["cyl"](tuple(c), r, h, mat, group, verts=verts, rot=tuple(rot), bevel=bevel)

    def flange(self, c, t, r, group, h=0.05, bolts=8, mat="iron_worn"):
        G = self.G
        t = Vector(t).normalized()
        out = [self.along(c, t, r, h, mat, group)]
        u = t.cross(Vector((0, 0, 1)))
        if u.length < 1e-3:
            u = t.cross(Vector((1, 0, 0)))
        u.normalize()
        w = t.cross(u)
        rot = Vector((0, 0, 1)).rotation_difference(t).to_euler()
        for k in range(bolts):
            a = 2 * math.pi * (k + 0.5) / bolts
            p = Vector(c) + (u * math.cos(a) + w * math.sin(a)) * (r - 0.045)
            for s in (-1, 1):
                out.append(G["bolt"](tuple(p + t * s * (h / 2 + 0.005)), 0.016, 0.012, group=group, rot=tuple(rot)))
        return out

    def plate_box(self, corners_lo, corners_hi, mat, group):
        """A box from 8 explicit corners: corners_lo / _hi the bottom and top quads."""
        G = self.G

        def build(bm):
            v = [bm.verts.new(p) for p in corners_lo] + [bm.verts.new(p) for p in corners_hi]
            for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
                bm.faces.new([v[i] for i in f])
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        return G["mesh_object"]("stool", build, mat, group, 0.006)

    # ------------------------------------------------------------ the gallery path
    def ring_path(self, step=0.02):
        """The run's axis round the gallery, counter-clockwise, closed: list of (x, y)."""
        pts = []
        for k in range(4):
            rot = Matrix.Rotation(math.pi / 2 * k, 2)
            n = int(2 * ARC_C / step)
            seg = [Vector((-ARC_C + 2 * ARC_C * i / n, -R_AX)) for i in range(n)]
            m = int(ARC_R * math.pi / 2 / step)
            arc = [Vector((ARC_C + ARC_R * math.cos(t), -ARC_C + ARC_R * math.sin(t)))
                   for t in (-math.pi / 2 + math.pi / 2 * i / m for i in range(m))]
            for v in seg + arc:
                pts.append(rot @ v)
        return pts

    @staticmethod
    def junction_xy(x, y, f, G):
        """Where the junction of the connection at pipe_connections (x, y), face f, stands
        (model x, y), on the run's axis: on the signed-off stub's axis (ballast_drill.py
        fitting(): the joins are calibrated there)."""
        cx, cy = x, -y
        if f == "S":
            return Vector((cx + G["V_AXIS_U"], -R_AX))
        if f == "N":
            return Vector((cx + G["V_AXIS_U"], R_AX))
        sgn = 1 if f == "E" else -1
        return Vector((sgn * R_AX, cy + G["H_AXIS_V"] - G["ZA"] / 2))

    def path_between(self, P, Q):
        ring = self.ring_path()
        n = len(ring)
        i = min(range(n), key=lambda k: (ring[k] - P).length)
        j = min(range(n), key=lambda k: (ring[k] - Q).length)
        fwd = [(i + k) % n for k in range((j - i) % n + 1)]
        bwd = [(i - k) % n for k in range((i - j) % n + 1)]
        idx = fwd if len(fwd) <= len(bwd) else bwd
        pts = [Vector(P)] + [ring[k] for k in idx[1:-1]] + [Vector(Q)]
        return pts

    @staticmethod
    def resample(pts, step=0.02):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            L = (b - a).length
            n = max(1, int(L / step))
            out += [a.lerp(b, k / n) for k in range(1, n + 1)]
        return out

    @staticmethod
    def cum(pts):
        s = [0.0]
        for a, b in zip(pts, pts[1:]):
            s.append(s[-1] + (b - a).length)
        return s

    @staticmethod
    def face_of(p):
        """The face a gallery point lies along, or None on a corner arc."""
        ax, ay = abs(p.x), abs(p.y)
        if ax > ARC_C + 1e-6 and ay > ARC_C + 1e-6:
            return None
        if ay >= ax:
            return "N" if p.y > 0 else "S"
        return "E" if p.x > 0 else "W"

    @staticmethod
    def lat_of(p):
        f = Rig.face_of(p)
        if f in ("N", "S"):
            return p.x
        if f in ("E", "W"):
            return p.y
        return None

    # ------------------------------------------------------------ the dry rig (plate)
    def dry_rig(self):
        G = self.G
        if self.low:
            self.dry = []
            print("RIG dry rig: none (the low take)", flush=True)
            return
        g = "body"
        before = set(bpy.data.objects)
        beam_w = 0.30
        for sx in (-1, 1):
            for sy in (-1, 1):
                c = Vector((sx * ARC_C, sy * ARC_C))
                # the curved girder: a box section bent on the run's arc, over the notch
                a0 = math.atan2(sy * 0, sx)                      # from the E/W face ...
                a_e = 0.0 if sx > 0 else math.pi
                a_n = math.pi / 2 if sy > 0 else -math.pi / 2
                n = 36
                angs = [a_e + (a_n - a_e) * i / n if abs(a_n - a_e) <= math.pi else 0 for i in range(n + 1)]
                if abs(a_n - a_e) > math.pi:                     # west to south: go the short way
                    a_n2 = a_n + 2 * math.pi if a_n < a_e else a_n - 2 * math.pi
                    angs = [a_e + (a_n2 - a_e) * i / n for i in range(n + 1)]

                def build(bm, angs=angs, c=c):
                    rows = []
                    for t in angs:
                        u = Vector((math.cos(t), math.sin(t)))
                        q = [c + u * (ARC_R - beam_w / 2), c + u * (ARC_R + beam_w / 2)]
                        rows.append([bm.verts.new((q[0].x, q[0].y, BEAM_Z0)), bm.verts.new((q[1].x, q[1].y, BEAM_Z0)),
                                     bm.verts.new((q[1].x, q[1].y, BEAM_Z1)), bm.verts.new((q[0].x, q[0].y, BEAM_Z1))])
                    for a, b in zip(rows, rows[1:]):
                        for k in range(4):
                            bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
                    bm.faces.new(list(reversed(rows[0])))
                    bm.faces.new(rows[-1])
                    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
                G["mesh_object"]("rig-girder", build, "iron", g, 0.012)
                # its web stiffeners down the outer face and bolts along the top
                for i in range(1, 6):
                    t = angs[0] + (angs[-1] - angs[0]) * i / 6
                    u = Vector((math.cos(t), math.sin(t)))
                    p = c + u * (ARC_R + beam_w / 2 + 0.012)
                    G["box"]((p.x, p.y, (BEAM_Z0 + BEAM_Z1) / 2), (0.024, 0.04, BEAM_Z1 - BEAM_Z0 - 0.01), "iron_worn", g,
                             rot=(0, 0, t), bevel=0.004)
                # the stool on the leg, under the girder's middle (the north corners: the south
                # ones are propped by the wings' braces, cut off under the girder)
                root, foot = G["LEGS"][(sx, sy)]
                d2 = Vector((sx, sy)).normalized()
                pm = c + d2 * ARC_R                               # the arc's middle
                L2 = (foot.xy - root.xy).length

                def leg_top(pp):
                    t = max(0.0, min(1.0, (pp - root.xy).dot(d2) / L2))
                    z = root.z + (foot.z - root.z) * t
                    r_ = max(0.2 + (0.15 - 0.2) * t, 0.18 + 0.004 if abs(t - 0.75) < 0.12 else 0.0)
                    pitch = math.atan2(root.z - foot.z, L2)
                    return z + r_ / math.cos(pitch)
                perp = Vector((-d2.y, d2.x))
                lo, hi = [], []
                for (a_, b_) in ((-0.07, -0.06), (0.07, -0.06), (0.07, 0.06), (-0.07, 0.06)):
                    pp = pm + d2 * a_ + perp * b_
                    # on the leg's cast band there (t 0.75): level, a hair over its rim
                    band_top = root.z + (foot.z - root.z) * 0.75 + 0.184 / math.cos(
                        math.atan2(root.z - foot.z, L2)) + 0.05
                    lo.append((pp.x, pp.y, max(leg_top(pm + d2 * a_) + 0.006, band_top)))
                    hi.append((pp.x, pp.y, BEAM_Z0 - 0.002))
                if sy > 0:
                    self.plate_box(lo, hi, "iron_worn", g)
                # stubs of the girder onto the ledge, along each face, short of the junctions
                for face_axis in ("x", "y"):
                    if face_axis == "x":         # on the E or W face: lat is y
                        lat0, lat1 = sy * ARC_C, sy * (1.13 if sy > 0 else ARC_C)
                        if sy < 0:
                            continue             # the south-side junction comes to the corner
                        y0, y1 = sorted((lat0, lat1))
                        ctr = (sx * R_AX, (y0 + y1) / 2)
                        size = (beam_w, y1 - y0, BEAM_Z1 - BEAM_Z0)
                    else:                        # on the N or S face: lat is x
                        x0, x1 = sorted((sx * ARC_C, sx * 1.33))
                        ctr = ((x0 + x1) / 2, sy * R_AX)
                        size = (x1 - x0, beam_w, BEAM_Z1 - BEAM_Z0)
                    G["box"]((ctr[0], ctr[1], (BEAM_Z0 + BEAM_Z1) / 2), size, "iron", g, bevel=0.01)
        self.dry = [o for o in bpy.data.objects if o not in before]
        for i, o in enumerate(sorted(self.dry, key=lambda q: q.name)):
            o.name = f"rigdry-{o.name.split('.')[0].lower()}-{i:03d}"
        print(f"RIG dry rig: {len(self.dry)} parts", flush=True)

    # ------------------------------------------------------------ wet, per direction
    def wet(self):
        G = self.G
        self.wet_groups = {}
        for d, deg in G["contract"].DIRECTIONS["four"]:
            conns = fit_conns(deg)
            pairs = [(conns[0], conns[3]), (conns[1], conns[2])]       # W-S(-1), E-S(1), turned
            sizes = []
            for k, (a, b) in enumerate(pairs):
                before = set(bpy.data.objects)
                JA = self.junction_xy(*a, G)
                JB = self.junction_xy(*b, G)
                pts = self.path_between(JA, JB)
                sizes.append(self.pair_run(d, k, a, b, JA, JB, pts))
                for i, o in enumerate(sorted(set(bpy.data.objects) - before, key=lambda q: q.name)):
                    o.name = f"rig-{d}-p{k}-{o.name.split('.')[0].lower()}-{i:03d}"
                    self.assembly[o.name] = f"{d}:pair{k}"
            self.log["sizes"][d] = sizes
        for d, _ in G["contract"].DIRECTIONS["four"]:
            for side in ("behind", "front"):
                G["PARTS"].setdefault(f"rig-{side}-{d}", [])

    def grp(self, d, y):
        return f"rig-{'behind' if y > 0 else 'front'}-{d}"

    def junction(self, d, conn, J, toward):
        """The wall fitting and the junction head at J for connection conn = (x, y, face);
        toward: the unit vector, in plan, the run leaves the head by."""
        G = self.G
        x, y, f = conn
        g = self.grp(d, J.y)
        n = {"N": Vector((0, 1)), "S": Vector((0, -1)), "E": Vector((1, 0)), "W": Vector((-1, 0))}[f]
        t = Vector((-n.y, n.x))                                  # along the face
        ZA = G["ZA"]
        if self.low:
            return self.junction_low(d, conn, J, toward, g, n, t)
        # the slot's lining: its back and two sides, inside the cut, below the ledge
        zl0, zl1 = G["ZB"] + 0.003, Z0 - 0.004
        back = J - n * (R_AX - CUT_IN - 0.006)
        G["box"]((back.x, back.y, (zl0 + zl1) / 2), (abs(t.x) * 2 * (POCKET_HW - 0.012) + abs(n.x) * 0.008,
                                                    abs(t.y) * 2 * (POCKET_HW - 0.012) + abs(n.y) * 0.008, zl1 - zl0),
                 "liner", g, bevel=0.0)
        for s in (-1, 1):
            edge = J + t * s * POCKET_HW
            if abs(edge.x if f in "NS" else edge.y) < G["BAND_HW"] + 0.01:
                continue                         # that side is open to a bay: no wall to line
            sp = J + t * s * (POCKET_HW - 0.01) + n * ((2.495 - CUT_IN) / 2 - (R_AX - CUT_IN))
            G["box"]((sp.x, sp.y, (zl0 + zl1) / 2), (abs(n.x) * (2.495 - CUT_IN - 0.012) + abs(t.x) * 0.008,
                                                     abs(n.y) * (2.495 - CUT_IN - 0.012) + abs(t.y) * 0.008, zl1 - zl0),
                     "liner", g, bevel=0.0)
            # the bolted frame round the slot's mouth, on the wall's face
            fp = J + t * s * (POCKET_HW + 0.03) + n * (2.495 - R_AX + 0.008)
            G["box"]((fp.x, fp.y, (zl0 + zl1) / 2), (abs(t.x) * 0.06 + abs(n.x) * 0.012, abs(t.y) * 0.06 + abs(n.y) * 0.012,
                                                     zl1 - zl0 - 0.01), "steel", g, bevel=0.003)
            for zb in (zl0 + 0.08, zl1 - 0.08):
                bp = fp + n * 0.01
                G["bolt"]((bp.x, bp.y, zb), 0.013, 0.01, group=g,
                          rot=(math.pi / 2, 0, math.atan2(n.y, n.x) + math.pi / 2))
        # the cast riser body standing in the slot, on a foot
        G["cyl"]((J.x, J.y, 0.02), R_BODY + 0.05, 0.04, "iron", g, verts=40, bevel=0.008)
        G["cyl"]((J.x, J.y, (0.04 + Z_RUN) / 2), R_BODY, Z_RUN - 0.04, "oxide", g, verts=48, bevel=0.01)
        for zr in (0.3, 0.62):                                    # cast bands round it
            G["cyl"]((J.x, J.y, zr), R_BODY + 0.012, 0.03, "iron_worn", g, verts=48, bevel=0.004)
        # its head: a cast bulb at the run's height, a bolted bonnet on top
        G["sphere"]((J.x, J.y, Z_RUN), R_BODY, "oxide", g)
        G["cyl"]((J.x, J.y, Z_RUN + R_BODY - 0.02), 0.15, 0.05, "iron_worn", g, verts=32, bevel=0.008)
        for k in range(6):
            a = 2 * math.pi * (k + 0.5) / 6
            G["bolt"]((J.x + 0.115 * math.cos(a), J.y + 0.115 * math.sin(a), Z_RUN + R_BODY + 0.01), 0.013, 0.01,
                      group=g)
        G["cyl"]((J.x, J.y, Z_RUN + R_BODY + 0.03), 0.05, 0.03, "polish", g, verts=16, bevel=0.004)
        # the connection: a sleeve of the bore out of the body at ZA, through the slot's
        # mouth, to the end ring where vanilla's pipe meets it (the signed-off stub's)
        if f == "S":
            ye = -2.53 - ZA / 2
            p0, p1 = J, Vector((J.x, ye))
            self.along(((p0.x + p1.x) / 2, (p0.y + p1.y) / 2, ZA), (0, 1, 0), R_RUN, abs(p1.y - p0.y), "steel", g,
                       verts=48, bevel=0.0)
            G["cyl"]((J.x, ye + 0.03, ZA), G["V_RING_R"] - 0.02, 0.06, "steel", g, verts=48, rot=(math.pi / 2, 0, 0),
                     bevel=0.01)
            for k in range(8):
                a = 2 * math.pi * (k + 0.5) / 8
                G["bolt"]((J.x + 0.33 * math.cos(a), ye - 0.002, ZA + 0.33 * math.sin(a)), 0.018, 0.012, group=g,
                          rot=(math.pi / 2, 0, 0))
            G["cyl"]((J.x, ye - 0.003, ZA), 0.2, 0.006, "dark", g, verts=32, rot=(math.pi / 2, 0, 0), bevel=0.0)
            end = ye
        elif f == "N":
            ye = 2.495 - 0.025
            self.along((J.x, (J.y + ye) / 2, ZA), (0, 1, 0), R_RUN, abs(ye - J.y), "steel", g, verts=48, bevel=0.0)
            G["cyl"]((J.x, ye, ZA), POCKET_HW - 0.01, 0.04, "steel", g, verts=48, rot=(math.pi / 2, 0, 0),
                     bevel=0.008)
            end = ye
        else:
            sgn = 1 if f == "E" else -1
            xf = sgn * (2.5 - 0.03)
            self.along(((J.x + xf) / 2, J.y, ZA), (1, 0, 0), R_RUN, abs(xf - J.x), "steel", g, verts=48, bevel=0.0)
            G["cyl"]((xf, J.y, ZA), G["H_RING_R"] - 0.02, 0.04, "steel", g, verts=48, rot=(0, math.pi / 2, 0),
                     bevel=0.006)
            for k in range(8):
                a = 2 * math.pi * (k + 0.5) / 8
                G["bolt"]((xf - sgn * 0.025, J.y + 0.27 * math.cos(a), ZA + 0.27 * math.sin(a)), 0.016, 0.01, group=g,
                          rot=(0, math.pi / 2, 0))
            end = xf
        # the head's flange toward the run
        fc = J + toward * (R_BODY - 0.01)
        self.flange((fc.x, fc.y, Z_RUN), (toward.x, toward.y, 0), FLANGE_R, g)
        return dict(fitting=2 * R_RUN, body=2 * R_BODY, end=round(end, 3))

    def z_profile(self, pts, S):
        """The run's axis height at each point: constant on the ledge takes; on the low take
        the ground level, a little up over each bay's kerb, swan-necked over each corner."""
        if not self.low:
            return [Z_RUN] * len(pts)
        zs = []
        arcs, i = [], 0
        while i < len(pts):
            if self.face_of(pts[i]) is None:
                j = i
                while j < len(pts) and self.face_of(pts[j]) is None:
                    j += 1
                arcs.append((i, j - 1))
                i = j
            else:
                i += 1
        for i, p in enumerate(pts):
            lat = self.lat_of(p)
            if lat is None:
                a, b = next((a, b) for a, b in arcs if a <= i <= b)
                u = (S[i] - S[a]) / max(1e-6, S[b] - S[a])
                zs.append(Z_LOW + (Z_APEX - Z_LOW) * math.sin(math.pi * u) ** 0.8)
            else:
                w = max(0.0, min(1.0, (0.95 - abs(lat)) / 0.2))
                w = w * w * (3 - 2 * w)
                zs.append(Z_LOW + (Z_LOW_BAY - Z_LOW) * w)
        return zs

    def junction_low(self, d, conn, J, toward, g, n, t):
        """The low take's junction: a cast tee standing in the gallery on its foot, the run
        into its side at the run's height, the connection's sleeve out of its face to the end
        ring, and a short spool from its back into a bolted boss on the cut-back wall: where
        the fluid enters the casting."""
        G = self.G
        x, y, f = conn
        ZA = G["ZA"]
        top = 0.86
        G["cyl"]((J.x, J.y, 0.02), R_BODY + 0.05, 0.04, "iron", g, verts=40, bevel=0.008)
        G["cyl"]((J.x, J.y, (0.04 + top) / 2), R_BODY, top - 0.04, "oxide", g, verts=48, bevel=0.012)
        G["cyl"]((J.x, J.y, top - 0.02), R_BODY + 0.02, 0.04, "iron_worn", g, verts=48, bevel=0.008)
        G["sphere"]((J.x, J.y, top), R_BODY - 0.04, "oxide", g, squash=0.55)
        G["cyl"]((J.x, J.y, top + 0.13), 0.13, 0.05, "iron_worn", g, verts=32, bevel=0.008)
        for k in range(6):
            a = 2 * math.pi * (k + 0.5) / 6
            G["bolt"]((J.x + 0.1 * math.cos(a), J.y + 0.1 * math.sin(a), top + 0.165), 0.013, 0.01, group=g)
        # the boss into the wall
        back = J - n * (R_BODY - 0.01)
        wall = J - n * (R_AX - CUT_IN)
        L = (back - wall).length
        mid = (back + wall) / 2
        self.along((mid.x + n.x * 0.012, mid.y + n.y * 0.012, Z_LOW), (n.x, n.y, 0), 0.2, L - 0.024, "steel", g,
                   verts=32, bevel=0.0)                 # from the body's back to the boss's face
        bp = wall + n * 0.012
        G["box"]((bp.x, bp.y, Z_LOW), (abs(t.x) * 0.44 + abs(n.x) * 0.016, abs(t.y) * 0.44 + abs(n.y) * 0.016, 0.44),
                 "iron_worn", g, bevel=0.006)
        for i in (-1, 1):
            for j in (-1, 1):
                q = bp + t * i * 0.17 + n * 0.012
                G["bolt"]((q.x, q.y, Z_LOW + j * 0.17), 0.014, 0.01, group=g,
                          rot=(math.pi / 2, 0, math.atan2(n.y, n.x) + math.pi / 2))
        # the connection's sleeve and end ring, as the ledge takes'
        if f == "S":
            ye = -2.53 - ZA / 2
            self.along((J.x, (J.y + ye) / 2, ZA), (0, 1, 0), R_RUN, abs(ye - J.y), "steel", g, verts=48, bevel=0.0)
            G["cyl"]((J.x, ye + 0.03, ZA), G["V_RING_R"] - 0.02, 0.06, "steel", g, verts=48, rot=(math.pi / 2, 0, 0),
                     bevel=0.01)
            for k in range(8):
                a = 2 * math.pi * (k + 0.5) / 8
                G["bolt"]((J.x + 0.33 * math.cos(a), ye - 0.002, ZA + 0.33 * math.sin(a)), 0.018, 0.012, group=g,
                          rot=(math.pi / 2, 0, 0))
            G["cyl"]((J.x, ye - 0.003, ZA), 0.2, 0.006, "dark", g, verts=32, rot=(math.pi / 2, 0, 0), bevel=0.0)
        elif f == "N":
            ye = 2.495 - 0.025
            self.along((J.x, (J.y + ye) / 2, ZA), (0, 1, 0), R_RUN, abs(ye - J.y), "steel", g, verts=48, bevel=0.0)
            G["cyl"]((J.x, ye, ZA), POCKET_HW - 0.01, 0.04, "steel", g, verts=48, rot=(math.pi / 2, 0, 0), bevel=0.008)
        else:
            sgn = 1 if f == "E" else -1
            xf = sgn * (2.5 - 0.03)
            self.along(((J.x + xf) / 2, J.y, ZA), (1, 0, 0), R_RUN, abs(xf - J.x), "steel", g, verts=48, bevel=0.0)
            G["cyl"]((xf, J.y, ZA), G["H_RING_R"] - 0.02, 0.04, "steel", g, verts=48, rot=(0, math.pi / 2, 0),
                     bevel=0.006)
            for k in range(8):
                a = 2 * math.pi * (k + 0.5) / 8
                G["bolt"]((xf - sgn * 0.025, J.y + 0.27 * math.cos(a), ZA + 0.27 * math.sin(a)), 0.016, 0.01, group=g,
                          rot=(0, math.pi / 2, 0))
        fc = J + toward * (R_BODY - 0.01)
        self.flange((fc.x, fc.y, Z_LOW), (toward.x, toward.y, 0), FLANGE_R, g)
        return dict(fitting=2 * R_RUN, body=2 * R_BODY)

    def pair_run(self, d, k, a, b, JA, JB, pts):
        """Pair k of direction d: both junctions and the run between them."""
        G = self.G
        cfg = self.cfg
        pts = self.resample(pts, 0.02)
        S = self.cum(pts)
        L = S[-1]
        ta = (pts[3] - pts[0]).normalized()
        tb = (pts[-4] - pts[-1]).normalized()
        sa = self.junction(d, a, JA, ta)
        self.junction(d, b, JB, tb)
        ZS = self.z_profile(pts, S)
        # the run between the heads' flanges, split where it crosses y = 0 (north of it
        # drawn behind, south in front, as vanilla's two layers)
        s0, s1 = R_BODY + 0.015, L - R_BODY - 0.015
        body = [Vector((p.x, p.y, z)) for p, s, z in zip(pts, S, ZS) if s0 <= s <= s1]
        pieces, cur = [], [body[0]]
        for p in body[1:]:
            if (p.y > 0) != (cur[-1].y > 0):
                m = cur[-1].lerp(p, cur[-1].y / (cur[-1].y - p.y)) if abs(cur[-1].y - p.y) > 1e-9 else p
                cur.append(m)
                pieces.append(cur)
                cur = [m]
            cur.append(p)
        pieces.append(cur)
        for pc in pieces:
            if len(pc) < 2:
                continue
            g = self.grp(d, sum(p.y for p in pc) / len(pc))
            if cfg["run"] == "hose":
                self.tube(pc, R_RUN - 0.01, self.mat("hose", "dark"), g, seg=36, rib=0.06, pitch=0.06, caps=True,
                          name="run-hose")
            else:
                self.tube(pc, R_RUN, self.mat("ring", "iron"), g, seg=40, caps=True, name="run-pipe")
        # joints and supports, by where they fall along the run
        marks = []

        def at(s):
            i = min(range(len(S)), key=lambda q: abs(S[q] - s))
            p = pts[i]
            t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            return p, t, ZS[i]
        # cast bends: flanged where the corner arc meets each face
        prev = self.face_of(pts[0])
        for i in range(1, len(pts)):
            f = self.face_of(pts[i])
            if (f is None) != (prev is None):
                marks.append(("joint", S[i]))
            prev = f
        # bays: a joint in the middle of each one crossed (lat 0 on a face)
        for i in range(1, len(pts)):
            la, lb = self.lat_of(pts[i - 1]), self.lat_of(pts[i])
            if la is not None and lb is not None and (la > 0) != (lb > 0) and self.face_of(pts[i]) == self.face_of(
                    pts[i - 1]):
                marks.append(("bay", S[i]))
        # supports: the girder's saddles on the arcs (0.2, 0.5, 0.8 of each) and its stubs;
        # elsewhere a stool of the run's own on the ledge at each face tile it passes over
        # with no junction (lat +-1, and the E/W tiles' calibrated centres)
        arc_runs = []
        i = 0
        while i < len(pts):
            if self.face_of(pts[i]) is None:
                j = i
                while j < len(pts) and self.face_of(pts[j]) is None:
                    j += 1
                arc_runs.append((S[i], S[j - 1]))
                i = j
            else:
                i += 1
        for sA, sB in ([] if self.low else arc_runs):
            if sB - sA > 0.9:                # a whole corner
                for fr in (0.2, 0.5, 0.8):
                    marks.append(("clamp", sA + (sB - sA) * fr))
        for i in range(1, len(pts)):
            f = self.face_of(pts[i])
            if f is None or self.face_of(pts[i - 1]) != f:
                continue
            for lat_mark in (STUB_SADDLE, -STUB_SADDLE):
                la, lb = self.lat_of(pts[i - 1]), self.lat_of(pts[i])
                if (la - lat_mark) * (lb - lat_mark) <= 0:
                    # on a girder stub (S/N faces both ends; E/W only the north end); the low
                    # take has no girder: a stool of its own where no junction stands
                    if self.low:
                        if (pts[i] - JA).length > 0.45 and (pts[i] - JB).length > 0.45:
                            marks.append(("stool", S[i]))
                    elif f in "NS" or lat_mark > 0:
                        marks.append(("clamp", S[i]))
        for i in range(1, len(pts)):
            f = self.face_of(pts[i])
            if f is None or self.face_of(pts[i - 1]) != f:
                continue
            la, lb = self.lat_of(pts[i - 1]), self.lat_of(pts[i])
            centres = (1.0, -1.0) if f in "NS" else (1 + G["H_AXIS_V"] - G["ZA"] / 2, -1 + G["H_AXIS_V"] - G["ZA"] / 2)
            for c in centres:
                if (la - c) * (lb - c) <= 0:
                    # not where a junction of this direction stands
                    p = pts[i]
                    if (p - JA).length > 0.4 and (p - JB).length > 0.4:
                        marks.append(("stool", S[i]))
        for kind, s in marks:
            if not (s0 + 0.05 < s < s1 - 0.05):
                continue
            p, t, zr = at(s)
            g = self.grp(d, p.y)
            c3 = Vector((p.x, p.y, zr))
            st = zr - R_RUN - 0.002          # the saddle's top under it
            t3 = Vector((t.x, t.y, 0)).normalized()
            if kind == "bay" and cfg.get("feed"):
                self.feed(d, p, t, g)
                continue
            if kind in ("joint", "bay"):
                if cfg["run"] == "hose":
                    self.along(c3, t3, R_RUN + 0.02, 0.09, "steel", g, verts=40, bevel=0.006)    # a clamp collar
                else:
                    self.flange(c3, t3, FLANGE_R, g, h=0.06)
            elif kind in ("clamp", "stool"):
                if kind == "stool":
                    # a cast stool on the ledge (the ground, on the low take), its top a saddle
                    zb = 0.0 if self.low else Z0 + 0.003
                    G["box"]((p.x, p.y, (zb + st) / 2), (2 * SADDLE_HL, 0.12, st - zb), "iron_worn",
                             g, rot=(0, 0, math.atan2(t.y, t.x) + math.pi / 2), bevel=0.01)
                if kind == "clamp":
                    # the saddle it is bolted down to, across the girder
                    G["box"]((p.x, p.y, (BEAM_Z1 + 0.003 + st) / 2), (2 * SADDLE_HL, 0.09, st - BEAM_Z1 - 0.003), "steel",
                             g, rot=(0, 0, math.atan2(t.y, t.x) + math.pi / 2), bevel=0.004)
                self.clamp(c3, t3, g, st)
        return dict(pair=[list(a), list(b)], fitting=2 * R_RUN, body=2 * R_BODY,
                    run=2 * (R_RUN - (0.01 if cfg["run"] == "hose" else 0)), head=2 * R_RUN,
                    length=round(L, 2), **({"feed": f"reducer 0.56 -> {2 * self.R_FEED:.2f}, line {2 * self.R_FEED:.2f}"} if cfg.get("feed") else {}))

    def clamp(self, c, t, g, saddle_top=SADDLE_TOP):
        """A U-bolt strap over the run, its two feet bolted to the saddle under it."""
        G = self.G
        u = Vector((-t.y, t.x, 0))
        r0, r1, w = R_RUN + 0.004, R_RUN + 0.022, 0.045

        def build(bm):
            n = 20
            rows = []
            for i in range(n + 1):
                a = math.pi * i / n
                d_ = u * math.cos(a) + Vector((0, 0, 1)) * math.sin(a)
                rows.append([bm.verts.new(c + d_ * r0 - t * w / 2), bm.verts.new(c + d_ * r1 - t * w / 2),
                             bm.verts.new(c + d_ * r1 + t * w / 2), bm.verts.new(c + d_ * r0 + t * w / 2)])
            for a_, b_ in zip(rows, rows[1:]):
                for k in range(4):
                    bm.faces.new((a_[k], a_[(k + 1) % 4], b_[(k + 1) % 4], b_[k]))
            bm.faces.new(list(reversed(rows[0])))
            bm.faces.new(rows[-1])
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        G["mesh_object"]("clamp", build, "steel", g, 0.0, smooth=True)
        for s in (-1, 1):
            q = c + u * s * (R_RUN + 0.013)
            G["cyl"]((q.x, q.y, (c.z + saddle_top + 0.004) / 2), 0.009, c.z - saddle_top - 0.004, "steel", g, verts=10,
                     bevel=0.0)
            G["bolt"]((q.x, q.y, saddle_top + 0.026), 0.018, 0.012, group=g)

    R_FEED = 0.15           # the feed line's: a reducer at the tee shows the narrowing

    def feed(self, d, p, t, g):
        """Take "feed": a cast tee in the run over a bay; out of it a reducer cone, the bore
        down to a 0.30 line, under the run, which turns in along the bay and enters a flanged
        nozzle on the riser,
        in front of the cutting head."""
        G = self.G
        n = Vector((p.x, p.y)).normalized()
        if abs(n.x) > abs(n.y):
            n = Vector((1 if n.x > 0 else -1, 0))
        else:
            n = Vector((0, 1 if n.y > 0 else -1))
        ys = G["Y_STEP"]
        zf = 0.45
        rf = self.R_FEED
        a = Vector((p.x, p.y, Z_RUN))
        lat = (p - n * (p.dot(n))).to_3d()
        nn = n.to_3d()

        def q(rad, z):
            return lat + nn * rad + Vector((0, 0, z))
        # the tee: a cast body round the run, its branch outlet flanged
        self.along(tuple(a), (t.x, t.y, 0), R_RUN + 0.045, 0.5, "iron_worn", g, verts=48, bevel=0.012)
        G["sphere"](tuple(a), R_RUN + 0.05, "iron_worn", g)
        z0_, z1_ = Z_RUN - 0.31, 0.56                 # the tee's outlet points down: the reducer under it
        self.flange(tuple(q(R_AX, z0_)), (0, 0, 1), FLANGE_R, g, h=0.05)
        G["rod"](tuple(q(R_AX, z0_)), tuple(q(R_AX, z1_)), R_RUN, rf + 0.01, "iron_worn", g)    # the reducer
        self.flange(tuple(q(R_AX, z1_ + 0.015)), (0, 0, 1), rf + 0.06, g, h=0.03, bolts=6)
        pts = [q(R_AX, z1_), q(R_AX, zf), q(ys + 0.09, zf)]
        sm = [pts[0]]
        for i in range(1, len(pts) - 1):
            pa, pb, pc = pts[i - 1], pts[i], pts[i + 1]
            e = min(0.14, 0.45 * (pa - pb).length, 0.45 * (pc - pb).length)
            s0_, s1_ = pb + (pa - pb).normalized() * e, pb + (pc - pb).normalized() * e
            sm += [sm[-1].lerp(s0_, k / 6) for k in range(1, 7)]
            sm += [(1 - u) ** 2 * s0_ + 2 * (1 - u) * u * pb + u * u * s1_ for u in (k / 12 for k in range(1, 13))]
        sm += [sm[-1].lerp(pts[-1], k / 6) for k in range(1, 7)]
        self.tube(sm, rf, self.mat("ring", "iron"), g, seg=28, name="feed")
        self.flange(tuple(q(ys + 0.075, zf)), (n.x, n.y, 0), rf + 0.07, g, h=0.04, bolts=6)        # the nozzle

    # ------------------------------------------------------------ the slots, per direction
    def pockets(self):
        """One cutter per connection of a direction, moved to its junctions per direction; cut
        into whatever plate part any of the eight slot places reaches."""
        G = self.G
        places = set()
        for d, deg in G["contract"].DIRECTIONS["four"]:
            for c in fit_conns(deg):
                J = self.junction_xy(*c, G)
                places.add((round(J.x, 4), round(J.y, 4), c[2]))
        self.slot_places = places
        for i in range(4):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -20))
            cb = bpy.context.active_object
            cb.name = f"slotcut{i}"
            cb.hide_render = True
            cb.display_type = "WIRE"
            cb.parent = G["BODY"]
            self.pocket_cutters.append(cb)
        boxes = []
        for (x, y, f) in places:
            boxes.append(self.slot_box(Vector((x, y)), f))
        targets = []
        for g, objs in G["PARTS"].items():
            if g in self.SKIP_GROUPS or g.startswith("rig-"):
                continue
            for o in objs:
                if o.type != "MESH":
                    continue
                lo, hi = self.bbox(o)
                for (c, s) in boxes:
                    if all(lo[i] <= c[i] + s[i] / 2 and hi[i] >= c[i] - s[i] / 2 for i in range(3)):
                        targets.append(o)
                        break
        for o in targets:
            G["cut"](o, *self.pocket_cutters)
        self.pocket_targets = targets
        print(f"RIG slots: {len(targets)} plate parts take the slot cutters", flush=True)

    @staticmethod
    def slot_box(J, f):
        n = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[f]
        rr0, rr1 = CUT_IN, 2.9
        mid = (rr0 + rr1) / 2
        lat = J.x if f in "NS" else J.y
        if f in "NS":
            c = Vector((lat, n[1] * mid, (-0.1 + Z0 + 0.01) / 2))
            s = Vector((2 * POCKET_HW, rr1 - rr0, Z0 + 0.11))
        else:
            c = Vector((n[0] * mid, lat, (-0.1 + Z0 + 0.01) / 2))
            s = Vector((rr1 - rr0, 2 * POCKET_HW, Z0 + 0.11))
        return c, s

    def place_pockets(self, d=None):
        G = self.G
        if d is None:
            for cb in self.pocket_cutters:
                cb.location = (0, 0, -20)
        else:
            deg = dict(G["contract"].DIRECTIONS["four"])[d]
            for cb, c in zip(self.pocket_cutters, fit_conns(deg)):
                J = self.junction_xy(*c, G)
                ctr, s = self.slot_box(J, c[2])
                cb.location = ctr
                cb.scale = s
        bpy.context.view_layer.update()

    # ------------------------------------------------------------ build and render
    def build(self, pas):
        self.cut_back()
        self.dry_rig()
        if pas in ("rig", "collide", "preview"):
            self.pockets()
            self.wet()

    def run(self, pas, collide):
        G = self.G
        if collide:
            pas = "collide"
        self.build(pas)
        out = G["OUT_DIR"]
        os.makedirs(out, exist_ok=True)
        side = os.path.join(os.path.dirname(os.path.normpath(out)), "rig-notes")
        os.makedirs(side, exist_ok=True)
        with open(os.path.join(side, f"{pas}-build.json"), "w") as f:
            json.dump(self.log, f, indent=1)
        if pas == "collide":
            self.collide()
            raise SystemExit(0)
        if pas == "plate":
            self.render_plate(side)
        elif pas == "preview":
            self.render_preview()
        else:
            self.render_rig()

    def render_preview(self):
        """Debugging: the whole drill with this take's wet rig, per direction, in one render
        each (no layers), at the samples given (--samples=)."""
        G = self.G
        rig, contract = G["rig"], G["contract"]
        out = G["OUT_DIR"]
        rig.camera(*G["PORT_CANVAS"])
        G["pose"](0)
        dirs = os.environ.get("SAE_RIG_DIRS", "north,east,south,west").split(",")
        for d in contract.each_direction(G["ROOT"], "four"):
            if d not in dirs:
                continue
            G["CHUTE"].location.x = G["NUDGE"][d]
            G["chain"](0)
            self.place_pockets(d)
            shut = tuple(x for x in G["DOORS"] if x != f"door-{G['OPEN'][d]}")
            G["setup"](visible=G["STATIC"] + shut + ("ring", "frame", "chute", f"rig-behind-{d}", f"rig-front-{d}"))
            rig.render(f"{out}/preview-{d}.png")
            G["setup"](visible=G["STATIC"] + G["DOORS"])
            if d == dirs[0]:
                self.place_pockets(None)
                rig.render(f"{out}/preview-dry.png")

    def render_plate(self, side):
        G = self.G
        rig, contract, sc = G["rig"], G["contract"], G["sc"]
        out = G["OUT_DIR"]
        contract.declare(out, canvas=G["CANVAS"], footprint=(5, 5), directions="four",
                         passes=[dict(name="idle", kind="plate", sheet="base"),
                                 dict(name="shadow", kind="shadow", sheet="base-shadow")])
        rig.camera(*G["CANVAS"])
        first = None
        for d in contract.each_direction(G["ROOT"], "four"):
            G["CHUTE"].location.x = G["NUDGE"][d]
            G["pose"](0)
            G["chain"](0)
            shut = tuple(x for x in G["DOORS"] if x != f"door-{G['OPEN'][d]}")
            sc.cycles.samples = G["PLATE_SAMPLES"]
            path = f"{out}/{contract.named('idle', d)}.png"
            if first is None:
                G["setup"](visible=G["STATIC"] + G["DOORS"])
                rig.render(path)
                first = path
                # the stroke's frame 0 over this body (its catchers are the plate's): for the
                # review sheets only, beside the signed-off stroke
                sc.cycles.samples = G["ANIM_SAMPLES"]
                G["setup"](visible=("ring", "frame") + G["PAINTED"],
                           catchers=tuple(x for x in G["STATIC"] if x not in G["PAINTED"]) + shut + ("chute",))
                rig.render(os.path.join(side, "stroke-f0-hi.png"))
                sc.cycles.samples = G["PLATE_SAMPLES"]
            else:
                shutil.copy(first, path)
            G["setup"](visible=G["STATIC"] + shut + ("ring", "frame", "chute"), ground=True)
            for o in [o for objs in G["PARTS"].values() for o in objs]:
                o.visible_camera = False
            rig.render(f"{out}/{contract.named('shadow', d)}.png")
            for o in [o for objs in G["PARTS"].values() for o in objs]:
                o.visible_camera = True

    def render_rig(self):
        G = self.G
        rig, contract = G["rig"], G["contract"]
        out = G["OUT_DIR"]
        contract.declare(out, canvas=G["PORT_CANVAS"], footprint=(5, 5), directions="four",
                         passes=[dict(name="behind", kind="plate", sheet="rig"),
                                 dict(name="still", kind="still"),
                                 dict(name="shadow", kind="shadow", sheet="rig-shadow")],
                         animations=[dict(name="rig-front", frames=2, motion="cycle")])
        rig.camera(*G["PORT_CANVAS"])
        G["pose"](0)
        held = G["STATIC"] + G["DOORS"]
        with open(os.path.join(out, "rig.json"), "w") as f:
            json.dump(dict(take=self.take, units="outer diameter, tiles (64 px a tile)", directions=self.log["sizes"]),
                      f, indent=1)
        for d, deg in contract.DIRECTIONS["four"]:
            self.place_pockets(d)
            b, fr = f"rig-behind-{d}", f"rig-front-{d}"
            G["setup"](visible=(b,), holdouts=held)
            rig.render(f"{out}/{contract.named('behind', d)}.png")
            G["setup"](visible=(fr,), holdouts=held)
            rig.render(f"{out}/{contract.frame('rig-front', 0, d)}.png")
            shutil.copy(f"{out}/{contract.frame('rig-front', 0, d)}.png", f"{out}/{contract.frame('rig-front', 1, d)}.png")
            G["setup"](visible=(b, fr), holdouts=held)
            rig.render(f"{out}/{contract.named('still', d)}.png")
            G["setup"](visible=(b, fr), ground=True)
            for o in G["PARTS"][b] + G["PARTS"][fr]:
                o.visible_camera = False
            rig.render(f"{out}/{contract.named('shadow', d)}.png")
            for o in G["PARTS"][b] + G["PARTS"][fr]:
                o.visible_camera = True

    # ------------------------------------------------------------ collide
    def collide(self):
        """Every part of the rig against the drill and each other, by BVH overlap of the
        evaluated meshes. An assembly (a direction's pair: its two junctions, the run between
        them, its joints, clamps and stools, welded or bolted as one) is not tested against
        itself; the two directions' wet parts never draw together, so each direction is
        tested alone, with that direction's slots cut. The dry rig is tested against the rest
        of the plate."""
        G = self.G
        G["pose"](0)
        dg_objs = lambda groups: [o for g in groups for o in G["PARTS"].get(g, []) if o.type == "MESH"]

        def tree(o):
            dg = bpy.context.evaluated_depsgraph_get()
            e = o.evaluated_get(dg)
            me = e.to_mesh()
            Binv = G["BODY"].matrix_world.inverted()
            mw = Binv @ o.matrix_world
            vs = [mw @ v.co for v in me.vertices]
            polys = [tuple(p.vertices) for p in me.polygons]
            e.to_mesh_clear()
            if not polys:
                return None, None
            lo = Vector([min(v[i] for v in vs) for i in range(3)])
            hi = Vector([max(v[i] for v in vs) for i in range(3)])
            return BVHTree.FromPolygons(vs, polys), (lo, hi)

        def info(a, b):
            for nm in (a, b):
                o = bpy.data.objects[nm]
                lo, hi = self.bbox(o)
                m = o.active_material.name if o.active_material else ""
                print(f"RIGINFO {nm} [{m}] {tuple(round(v, 2) for v in lo)} {tuple(round(v, 2) for v in hi)}")

        def boxes_meet(a, b, eps=0.0):
            return all(a[0][i] <= b[1][i] + eps and b[0][i] <= a[1][i] + eps for i in range(3))

        plate_groups = [g for g in G["PARTS"] if g not in self.SKIP_GROUPS and not g.startswith("rig-")]
        clashes = []
        dry = [o for o in self.dry if o.type == "MESH"]
        dry_names = {o.name for o in dry}
        plate = [o for o in dg_objs(plate_groups + ["ring"])]
        self.place_pockets(None)
        trees = {o.name: tree(o) for o in plate}
        # the dry rig against the rest of the plate
        for o in dry:
            ta, ba = trees[o.name]
            for q in plate:
                if q.name in dry_names or q.name == o.name:
                    continue
                tb, bb = trees[q.name]
                if ta and tb and boxes_meet(ba, bb) and ta.overlap(tb):
                    clashes.append(f"{o.name} x {q.name}")
        n_dry = len(clashes)
        print(f"COLLIDE dry rig: {len(dry)} parts against {len(plate)} plate meshes; clashes {n_dry}", flush=True)
        for c_ in clashes:
            print("COLLIDE", c_)
            info(*c_.split(" x "))
        total = n_dry
        for d, _ in G["contract"].DIRECTIONS["four"]:
            self.place_pockets(d)
            for o in self.pocket_targets:
                trees[o.name] = tree(o)
            wet = dg_objs((f"rig-behind-{d}", f"rig-front-{d}"))
            wt = {o.name: tree(o) for o in wet}
            found = []
            for o in wet:
                ta, ba = wt[o.name]
                if not ta:
                    continue
                for q in plate:
                    tb, bb = trees[q.name]
                    if tb and boxes_meet(ba, bb) and ta.overlap(tb):
                        found.append(f"{o.name} x {q.name}")
                for q in wet:
                    if q.name <= o.name or self.assembly.get(q.name) == self.assembly.get(o.name):
                        continue
                    tb, bb = wt[q.name]
                    if tb and boxes_meet(ba, bb) and ta.overlap(tb):
                        found.append(f"{o.name} x {q.name}")
            print(f"COLLIDE wet {d}: {len(wet)} parts; clashes {len(found)}", flush=True)
            for c_ in found:
                print("COLLIDE", c_)
                info(*c_.split(" x "))
            total += len(found)
        print(f"COLLIDE clashes {total}", flush=True)
