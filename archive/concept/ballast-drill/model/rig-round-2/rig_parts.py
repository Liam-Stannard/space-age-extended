"""The Ballast Drill's fluid rig, round 2 (task ballast-drill-ports, T03e): slimmer than T03d's
and detailed to the press's finish; imported by rig_take.py into the signed-off model's
namespace G.

Liam on T03d (2026-10-27): "The pipe work doesn't reflect the quality of the rest of the model.
It should be slightly less bulky." So, from the vanilla study (rig-round/study-vanilla-big-drill
.png) again:

THE PATTERN (vanilla's, unchanged from T03d): two runs per direction, each linking a side
connection to the rear one round the corner between them (W-S(-1), E-S(1), turned), along a
gallery round the deck's perimeter; a junction at every connection; north of the centre
drawn behind, south in front; a dry drill shows no plumbing.

THE SIZES (from vanilla's proportions; rig-round-2's report gives the measures):
  vanilla's big drill: its rig pipe 21-26 px across at 64 px a tile (0.33-0.41 tile, about
  0.36), collars 26-27 px; vanilla's pipe entity 39-41 px (0.62); so its rig pipe is about
  0.6 of the pipe it connects to. T03d's bore was 0.56 (36 px), 1.5 times vanilla's rig pipe.
  Here: BORE 0.44 (28 px) -- 0.79 of T03d's, 1.2 of vanilla's rig pipe, 0.7 of the pipe it
  connects to -- the same from the wall fitting's sleeve to the far junction (no narrowing
  anywhere); flanges 0.56; the junction riser 0.48, its head 0.52; the girders 0.20 wide over
  0.10 deep (T03d: a 0.30 box). The end ring that meets vanilla's pipe keeps the signed-off
  port's size (the joins are calibrated on it): the sleeve is bolted into it as into a
  blind flange.

THE CUT-BACK (the plate, every direction): smaller than T03d's, so less of the signed-off model
goes -- outside a rounded square 1.94 out on the straights (T03d 1.86), corner arcs of 0.44,
from Z0 0.53 to Z1 1.25 (T03d 0.60 to 1.40). The south-west housing's door and its fittings move
up 0.50 onto the face that overhangs the gallery.

THE FINISH (the press's, ballast_drill.py cast_iron and layered): the pipe in cast iron with the
press's wear, cavity rust, grime, dry rust on its top, ore dust and rust drips under its flanges;
or painted red oxide chipped to the iron, as the press frame is. Every joint a pair of flanges
with a gasket line, bolts through and hex nuts both sides; bends cast in segments, welded;
U-bolt clamps with nuts on bolted saddles; cast junction riser and head with ribs, bands, a
bolted bonnet and a lifting eye; a pressure gauge on one junction of each pair; a flow arrow
stencilled on each run.

TAKES
  cast     cast-iron pipe, red-oxide junctions; carried on I-section girders over the corners
           (dry, in the plate), a stool on the north legs, the wings' braces under the south
  oxide    the same, the pipe painted red oxide as the press frame, the junctions cast iron
  bracket  cast-iron pipe, no girders: bolted cantilever brackets off the cut-back wall on the
           faces and a post on each leg at the corners (dry, in the plate); the wings' braces go
  hose     an armoured hose of the bore between crimped ferrules, on the girders
"""
import json
import math
import os
import shutil

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

# ---------------------------------------------------------------- numbers
R_AX = 2.24             # the run's axis, out from the centre along a face's normal
R_RUN = 0.22            # the bore's radius: outer 0.44
ARC_C = 1.5             # corner arcs about (+-1.5, +-1.5)
ARC_R = R_AX - ARC_C    # 0.74: the run's bend radius round a corner
CUT_IN = 1.94           # the cut-back's inner face on the straights: inside the flanges (1.96)
CUT_ARC = ARC_R - (R_AX - CUT_IN)  # 0.44
Z0, Z1 = 0.53, 1.25     # the cut-back's floor (the ledge) and roof
Z_RUN = 0.92            # the run's axis: its underside 0.70
R_BODY = 0.24           # the junction's riser
R_HEAD = 0.26           # and its head
POCKET_HW = 0.38        # the wall slot's half-width: the end ring's (0.343) and a lining
FLANGE_R = R_RUN + 0.06  # 0.28: flanges 0.56
GIRDER_Z0, GIRDER_Z1 = 0.532, 0.632
GIRDER_W = 0.20
BRACKET_TOP = 0.66
SADDLE_TOP = Z_RUN - R_RUN - 0.002
SADDLE_HL = R_RUN + 0.045
STUB_SADDLE = 1.40      # the supports along the faces, short of the bends' flanges at 1.5
SPIGOT = 0.30           # a junction head's outlet, to its flange joint
JOINT_H = 0.026         # one flange's thickness

FIT_CONNS = [(-2, -1, "W"), (2, -1, "E"), (1, 2, "S"), (-1, 2, "S")]     # big-mining-drill.lua:570-580

TAKES = {
    "cast": dict(run="pipe", pipe="pipe_iron", body="oxide", support="girder"),
    "oxide": dict(run="pipe", pipe="pipe_oxide", body="pipe_iron", support="girder"),
    "bracket": dict(run="pipe", pipe="pipe_iron", body="oxide", support="bracket"),
    "hose": dict(run="hose", pipe="hose", body="oxide", support="girder"),
}


def fit_conns(deg):
    out = []
    for x, y, f in FIT_CONNS:
        for _ in range(round(deg / 90) % 4):
            x, y, f = -y, x, "NESW"[("NESW".index(f) + 1) % 4]
        out.append((x, y, f))
    return out


def main(G, take, pas, collide):
    if take not in TAKES:
        raise SystemExit(f"rig_parts: take {take!r} is not one of {', '.join(TAKES)}")
    Rig(G, take).go(pas, collide)


class Rig:
    THIN_MATS = ("hose", "hose_brown", "cable", "grease", "copper")
    SKIP_GROUPS = ("dust", "ore", "chute", "ring", "_cutters")

    def __init__(self, G, take):
        self.G, self.take, self.cfg = G, take, TAKES[take]
        self.log = {"take": take, "deleted": [], "cut": [], "moved": [], "sizes": {}}
        self.assembly = {}
        self.pocket_cutters, self.pocket_targets, self.dry = [], [], []
        self.sup_top = GIRDER_Z1 if self.cfg["support"] == "girder" else BRACKET_TOP
        self.materials()

    # ------------------------------------------------------------ materials
    def materials(self):
        G = self.G
        M = G["M"]
        M["pipe_iron"] = G["cast_iron"]("pipe_iron", lo="#3E3C3D", hi="#5E5B5B", ore=0.55, dry=0.5, wear=0.85,
                                        rust=0.5, drips=((Z_RUN + 0.1, 0.35),), drip=0.6, metal="#B4B6BC")
        M["pipe_oxide"] = G["layered"]("pipe_oxide", "#7A2A1C", metal="#9A9CA2", paint_metal=0.12, paint_rough=0.6,
                                       wear=0.85, rust=0.5, dust=0.35, grime=0.7, jitter=0.12,
                                       rust_tint=("#2E180C", "#6E3C1C"), drips=((Z_RUN + 0.1, 0.35),), drip=0.6)
        for m in (M["pipe_iron"], M["pipe_oxide"]):
            for n in m.node_tree.nodes:
                if n.type == "AMBIENT_OCCLUSION":
                    n.samples = 4
                elif n.type == "BEVEL":
                    n.samples = 2

    def mat(self, name, fallback="steel"):
        return name if name in self.G["M"] else fallback

    # ------------------------------------------------------------ geometry helpers
    def bbox(self, o):
        Binv = self.G["BODY"].matrix_world.inverted()
        cs = [Binv @ o.matrix_world @ Vector(c) for c in o.bound_box]
        return Vector([min(c[i] for c in cs) for i in range(3)]), Vector([max(c[i] for c in cs) for i in range(3)])

    def verts(self, o):
        Binv = self.G["BODY"].matrix_world.inverted()
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
        return Z0 <= p.z <= Z1 and self.outside_inner(p.x, p.y)

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
        rot = Vector((0, 0, 1)).rotation_difference(Vector(t).normalized()).to_euler()
        return self.G["cyl"](tuple(c), r, h, mat, group, verts=verts, rot=tuple(rot), bevel=bevel)

    def nut(self, c, t, group, r=0.019, h=0.016):
        return self.along(c, t, r, h, "bolt", group, verts=6, bevel=0.002)

    @staticmethod
    def basis(t):
        t = Vector(t).normalized()
        u = t.cross(Vector((0, 0, 1)))
        if u.length < 1e-3:
            u = t.cross(Vector((1, 0, 0)))
        u.normalize()
        return t, u, t.cross(u)

    def joint(self, c, t, r, group, bolts=8, mat="iron_worn"):
        """A bolted flange joint at c across axis t: two flanges of radius r with a dark gasket
        line between, bolts through, a hex nut on each face."""
        t, u, w = self.basis(t)
        c = Vector(c)
        h = JOINT_H
        for s in (-1, 1):
            self.along(c + t * s * (h / 2 + 0.003), t, r, h, mat, group, verts=40, bevel=0.005)
        self.along(c, t, r - 0.012, 0.007, "dark", group, verts=40, bevel=0.0)
        for k in range(bolts):
            a = 2 * math.pi * (k + 0.5) / bolts
            p = c + (u * math.cos(a) + w * math.sin(a)) * (r - 0.032)
            self.along(p, t, 0.007, 2 * h + 0.05, "steel", group, verts=8, bevel=0.0)
            for s in (-1, 1):
                self.nut(p + t * s * (h + 0.011), t, group)

    def weld_ring(self, c, t, group):
        self.along(c, t, R_RUN + 0.008, 0.016, "seam", group, verts=40, bevel=0.004)

    def plate_box(self, lo, hi, mat, group, bevel=0.006):
        G = self.G

        def build(bm):
            v = [bm.verts.new(p) for p in lo] + [bm.verts.new(p) for p in hi]
            for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
                bm.faces.new([v[i] for i in f])
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        return G["mesh_object"]("block", build, mat, group, bevel)

    # ------------------------------------------------------------ the cut-back
    def inner_loop(self, n_arc=24):
        pts = []
        for k in range(4):
            rot = Matrix.Rotation(math.pi / 2 * k, 2)
            seg = [Vector((ARC_C * i / 10, -CUT_IN)) for i in range(10)]
            arc = [Vector((ARC_C + CUT_ARC * math.cos(t), -ARC_C + CUT_ARC * math.sin(t)))
                   for t in (-math.pi / 2 + math.pi / 2 * i / n_arc for i in range(n_arc))]
            seg2 = [Vector((CUT_IN, -ARC_C + ARC_C * i / 10)) for i in range(10)]
            pts += [rot @ v for v in seg + arc + seg2]
        return pts

    def cutter(self):
        G = self.G
        inner = self.inner_loop()
        outer = [p * (2.9 / max(abs(p.x), abs(p.y))) for p in inner]

        def build(bm):
            n = len(inner)
            rows = [[bm.verts.new((p.x, p.y, z)) for p in loop]
                    for loop, z in ((inner, Z0), (outer, Z0), (outer, Z1), (inner, Z1))]
            for a, b in zip(rows, rows[1:] + rows[:1]):
                for i in range(n):
                    j = (i + 1) % n
                    bm.faces.new((a[i], a[j], b[j], b[i]))
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        o = G["mesh_object"]("rigcut", build, "iron", "_cutters", 0)
        o.hide_render = True
        o.display_type = "WIRE"
        return o

    def cut_back(self):
        G = self.G
        bpy.context.view_layer.update()
        cutter = self.cutter()
        lift = 0.50
        todo = []
        for g, objs in list(G["PARTS"].items()):
            if g in self.SKIP_GROUPS or g.startswith("rig-"):
                continue
            for o in list(objs):
                if o.type not in ("MESH", "CURVE"):
                    continue
                lo, hi = self.bbox(o)
                mat = o.active_material.name if o.active_material else ""
                brace = mat == "leg" and o.name.startswith("rod") and lo.z > 0.05
                if brace and self.cfg["support"] == "bracket":
                    todo.append((g, o, lo, hi, "brace"))
                    continue
                if hi.z < Z0 or lo.z > Z1:
                    continue
                corners = [Vector((x, y)) for x in (lo.x, hi.x) for y in (lo.y, hi.y)]
                if not any(self.outside_inner(c.x, c.y) for c in corners):
                    continue
                todo.append((g, o, lo, hi, None))
        plan = []
        for g, o, lo, hi, why in todo:
            if why == "brace":                  # it propped the wing cut back over the notch
                plan.append(("delete", g, o))
                continue
            c = (lo + hi) / 2
            mat = o.active_material.name if o.active_material else ""
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
                        n_in += self.in_cut(Vector((lo.x + (hi.x - lo.x) * (i + 0.5) / N,
                                                    lo.y + (hi.y - lo.y) * (j + 0.5) / N,
                                                    lo.z + (hi.z - lo.z) * (k + 0.5) / N)))
            share = n_in / N ** 3
            if share == 0 and not inside:
                continue
            plan.append(("delete" if share >= 0.7 and not o.children else "cut", g, o))
        moved = set()
        for act, g, o in plan:
            if act == "move":
                root = o
                while root.parent is not None and root.parent != G["BODY"]:
                    root = root.parent
                if root.name not in moved:
                    moved.add(root.name)
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

    def delete(self, o, g):
        G = self.G
        for ch in list(o.children):
            mw = ch.matrix_world.copy()
            ch.parent = G["BODY"]
            ch.matrix_world = mw
        G["PARTS"][g].remove(o)
        self.log["deleted"].append(o.name)
        bpy.data.objects.remove(o, do_unlink=True)

    # ------------------------------------------------------------ the gallery path
    def ring_path(self, step=0.02):
        pts = []
        for k in range(4):
            rot = Matrix.Rotation(math.pi / 2 * k, 2)
            n = int(2 * ARC_C / step)
            seg = [Vector((-ARC_C + 2 * ARC_C * i / n, -R_AX)) for i in range(n)]
            m = int(ARC_R * math.pi / 2 / step)
            arc = [Vector((ARC_C + ARC_R * math.cos(t), -ARC_C + ARC_R * math.sin(t)))
                   for t in (-math.pi / 2 + math.pi / 2 * i / m for i in range(m))]
            pts += [rot @ v for v in seg + arc]
        return pts

    @staticmethod
    def junction_xy(x, y, f, G):
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
        return [Vector(P)] + [ring[k] for k in idx[1:-1]] + [Vector(Q)]

    @staticmethod
    def resample(pts, step=0.02):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            n = max(1, int((b - a).length / step))
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

    @staticmethod
    def arc_angles(sx, sy):
        a_e = 0.0 if sx > 0 else math.pi
        a_n = math.pi / 2 if sy > 0 else -math.pi / 2
        if abs(a_n - a_e) > math.pi:
            a_n = a_n + 2 * math.pi if a_n < a_e else a_n - 2 * math.pi
        return a_e, a_n

    # ------------------------------------------------------------ the dry rig (plate)
    def leg_frame(self, sx, sy):
        G = self.G
        root, foot = G["LEGS"][(sx, sy)]
        d2 = Vector((sx, sy)).normalized()
        L2 = (foot.xy - root.xy).length
        pitch = math.atan2(root.z - foot.z, L2)

        def top(pp):
            t = max(0.0, min(1.0, (pp - root.xy).dot(d2) / L2))
            z = root.z + (foot.z - root.z) * t
            r_ = 0.2 + (0.15 - 0.2) * t
            if abs(t - 0.75) < 0.12:
                r_ = max(r_, 0.184 + 0.03)                  # its cast band
            return z + r_ / math.cos(pitch)
        return d2, top

    def stool(self, sx, sy, z_top, g, wide=0.07):
        """A cast stool on the leg under the corner's middle, to z_top, gusseted."""
        c = Vector((sx * ARC_C, sy * ARC_C))
        d2, top = self.leg_frame(sx, sy)
        pm = c + d2 * ARC_R
        perp = Vector((-d2.y, d2.x))
        lo, hi = [], []
        for a_, b_ in ((-wide, -0.06), (wide, -0.06), (wide, 0.06), (-wide, 0.06)):
            pp = pm + d2 * a_ + perp * b_
            lo.append((pp.x, pp.y, max(top(pm + d2 * a_) + 0.006, 0.495)))     # level on the leg's band
            hi.append((pp.x, pp.y, z_top))
        self.plate_box(lo, hi, "iron_worn", g)

    def dry_rig(self):
        G = self.G
        g = "body"
        before = set(bpy.data.objects)
        if self.cfg["support"] == "girder":
            self.girders(g)
        else:
            self.brackets(g)
        self.dry = [o for o in bpy.data.objects if o not in before]
        for i, o in enumerate(sorted(self.dry, key=lambda q: q.name)):
            o.name = f"rigdry-{o.name.split('.')[0].lower()}-{i:03d}"
        print(f"RIG dry rig: {len(self.dry)} parts", flush=True)

    def girders(self, g):
        """An I-section girder bent on the run's arc over each corner notch: top and bottom
        flanges, a web, stiffeners both sides, a bolt row along the top; its ends run on as
        straight stubs onto the ledge, on bolted bearing plates."""
        G = self.G
        zb, zt = GIRDER_Z0, GIRDER_Z1
        tf = 0.02
        for sx in (-1, 1):
            for sy in (-1, 1):
                c = Vector((sx * ARC_C, sy * ARC_C))
                a0, a1 = self.arc_angles(sx, sy)
                angs = [a0 + (a1 - a0) * i / 40 for i in range(41)]

                def curved(w, z0, z1, angs=angs, c=c):
                    def build(bm):
                        rows = []
                        for t in angs:
                            u = Vector((math.cos(t), math.sin(t)))
                            q0, q1 = c + u * (ARC_R - w / 2), c + u * (ARC_R + w / 2)
                            rows.append([bm.verts.new((q0.x, q0.y, z0)), bm.verts.new((q1.x, q1.y, z0)),
                                         bm.verts.new((q1.x, q1.y, z1)), bm.verts.new((q0.x, q0.y, z1))])
                        for a, b in zip(rows, rows[1:]):
                            for k in range(4):
                                bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
                        bm.faces.new(list(reversed(rows[0])))
                        bm.faces.new(rows[-1])
                        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
                    return G["mesh_object"]("girder", build, "iron", g, 0.004)
                curved(GIRDER_W, zt - tf, zt)
                curved(0.035, zb + tf, zt - tf)
                curved(GIRDER_W - 0.04, zb, zb + tf)
                for i in range(1, 8):                             # stiffeners, and bolts on the top
                    t = angs[0] + (angs[-1] - angs[0]) * i / 8
                    u = Vector((math.cos(t), math.sin(t)))
                    for s in (-1, 1):
                        p = c + u * (ARC_R + s * 0.05)
                        G["box"]((p.x, p.y, (zb + zt) / 2), (0.06, 0.012, zt - zb - 2 * tf - 0.002), "iron_worn", g,
                                 rot=(0, 0, t), bevel=0.002)
                        if i % 2:                          # clear of the saddles at 0.2, 0.5, 0.8
                            q = c + u * (ARC_R + s * 0.075)
                            G["bolt"]((q.x, q.y, zt + 0.005), 0.011, 0.008, group=g)
                # straight stubs onto the ledge along each face, on bearing plates
                for along_ in ("ew", "ns"):
                    if along_ == "ew":
                        if sy < 0:
                            continue                  # the E/W south junction comes to the corner
                        y0, y1 = sorted((sy * ARC_C, sy * 1.13))
                        ctr, ln = Vector((sx * R_AX, (y0 + y1) / 2)), y1 - y0
                        dims = lambda w, h: (w, ln, h)                    # noqa: E731
                        bp = Vector((sx * R_AX, sy * 1.25))
                    else:
                        x0, x1 = sorted((sx * ARC_C, sx * 1.30))
                        ctr, ln = Vector(((x0 + x1) / 2, sy * R_AX)), x1 - x0
                        dims = lambda w, h: (ln, w, h)                    # noqa: E731
                        bp = Vector((sx * 1.38, sy * R_AX))
                    G["box"]((ctr.x, ctr.y, zt - tf / 2), dims(GIRDER_W, tf), "iron", g, bevel=0.004)
                    G["box"]((ctr.x, ctr.y, (zb + zt) / 2), dims(0.035, zt - zb - 2 * tf), "iron", g, bevel=0.002)
                    G["box"]((ctr.x, ctr.y, zb + tf / 2), dims(GIRDER_W - 0.04, tf), "iron", g, bevel=0.003)
                    G["box"]((bp.x, bp.y, Z0 + 0.001), (0.18, 0.18, 0.0015), "iron_new", g, bevel=0.0)
                # the north legs carry a stool (the south ones: the wings' braces, cut off under it)
                if sy > 0:
                    self.stool(sx, sy, zb - 0.002, g)

    def brackets(self, g):
        """Take "bracket": bolted cantilever brackets off the cut-back wall where the faces'
        supports stand (a back plate, an arm under the run, a diagonal strut), and a post on
        each leg at the corner's middle with a cross-arm."""
        G = self.G
        zt = BRACKET_TOP
        spots = []
        for sx in (-1, 1):
            for sy in (-1, 1):
                spots.append(("NS", Vector((sx * STUB_SADDLE, sy * 1.0))))
                if sy > 0:
                    spots.append(("EW", Vector((sx * 1.0, sy * STUB_SADDLE))))
        for kind, sp in spots:
            if kind == "NS":
                n, lat = Vector((0, 1 if sp.y > 0 else -1)), sp.x
                at = lambda r, n=n, lat=lat: Vector((lat, n.y * r))      # noqa: E731
            else:
                n, lat = Vector((1 if sp.x > 0 else -1, 0)), sp.y
                at = lambda r, n=n, lat=lat: Vector((n.x * r, lat))      # noqa: E731
            rot = math.atan2(n.y, n.x)
            back = at(CUT_IN + 0.008)
            G["box"]((back.x, back.y, (Z0 + 0.86) / 2), (0.012 if kind == "EW" else 0.12, 0.12 if kind == "EW" else 0.012,
                                                         0.86 - Z0 - 0.02), "steel", g, bevel=0.002)
            for zb_ in (Z0 + 0.06, 0.8):
                for s in (-1, 1):
                    q = back + Vector((-n.y, n.x)) * s * 0.04 + n * 0.008
                    G["bolt"]((q.x, q.y, zb_), 0.012, 0.01, group=g, rot=(math.pi / 2, 0, rot + math.pi / 2))
            r0, r1 = CUT_IN + 0.016, R_AX + 0.25
            arm = at((r0 + r1) / 2)
            G["box"]((arm.x, arm.y, zt - 0.02), (r1 - r0 if kind == "EW" else 0.06, 0.06 if kind == "EW" else r1 - r0, 0.04),
                     "steel", g, bevel=0.004)
            # the strut, from the back plate's foot out to under the arm
            pa = at(r0).to_3d() + Vector((0, 0, Z0 + 0.05))
            pb = at(R_AX + 0.12).to_3d() + Vector((0, 0, zt - 0.045))
            G["strut"](tuple(pa), tuple(pb), 0.035, 0.035, 0.035, 0.035, "steel", g)
        for sx in (-1, 1):
            for sy in (-1, 1):
                c = Vector((sx * ARC_C, sy * ARC_C))
                d2, top = self.leg_frame(sx, sy)
                pm = c + d2 * ARC_R
                self.stool(sx, sy, zt - 0.04, g, wide=0.05)
                G["box"]((pm.x, pm.y, zt - 0.02), (0.06, 2 * SADDLE_HL, 0.04), "steel", g,
                         rot=(0, 0, math.atan2(d2.y, d2.x) + math.pi / 2), bevel=0.004)

    # ------------------------------------------------------------ wet, per direction
    def wet(self):
        G = self.G
        for d, deg in G["contract"].DIRECTIONS["four"]:
            conns = fit_conns(deg)
            pairs = [(conns[0], conns[3]), (conns[1], conns[2])]
            sizes = []
            for k, (a, b) in enumerate(pairs):
                before = set(bpy.data.objects)
                JA, JB = self.junction_xy(*a, G), self.junction_xy(*b, G)
                sizes.append(self.pair_run(d, k, a, b, JA, JB, self.path_between(JA, JB)))
                for i, o in enumerate(sorted(set(bpy.data.objects) - before, key=lambda q: q.name)):
                    o.name = f"rig-{d}-p{k}-{o.name.split('.')[0].lower()}-{i:03d}"
                    self.assembly[o.name] = f"{d}:pair{k}"
            self.log["sizes"][d] = sizes
            for side in ("behind", "front"):
                G["PARTS"].setdefault(f"rig-{side}-{d}", [])

    def grp(self, d, y):
        return f"rig-{'behind' if y > 0 else 'front'}-{d}"

    def junction(self, d, conn, J, toward, gauge):
        """The wall fitting and the junction at J: a slot cut into the wall (lined, a bolted
        frame round its mouth), a cast riser standing in it, the connection's sleeve out of it
        to the end ring, and above it the cast head with a bolted bonnet, its outlet spigot
        flanged toward the run."""
        G = self.G
        x, y, f = conn
        g = self.grp(d, J.y)
        n = {"N": Vector((0, 1)), "S": Vector((0, -1)), "E": Vector((1, 0)), "W": Vector((-1, 0))}[f]
        t = Vector((-n.y, n.x))
        ZA = G["ZA"]
        body = self.cfg["body"]
        zl0, zl1 = G["ZB"] + 0.003, Z0 - 0.004
        back = J - n * (R_AX - CUT_IN - 0.006)
        G["box"]((back.x, back.y, (zl0 + zl1) / 2), (abs(t.x) * 2 * (POCKET_HW - 0.012) + abs(n.x) * 0.008,
                                                    abs(t.y) * 2 * (POCKET_HW - 0.012) + abs(n.y) * 0.008, zl1 - zl0),
                 "liner", g, bevel=0.0)
        for s in (-1, 1):
            edge = J + t * s * POCKET_HW
            if abs(edge.x if f in "NS" else edge.y) < G["BAND_HW"] + 0.01:
                continue
            sp = J + t * s * (POCKET_HW - 0.01) + n * ((2.495 - CUT_IN) / 2 - (R_AX - CUT_IN))
            G["box"]((sp.x, sp.y, (zl0 + zl1) / 2), (abs(n.x) * (2.495 - CUT_IN - 0.012) + abs(t.x) * 0.008,
                                                     abs(n.y) * (2.495 - CUT_IN - 0.012) + abs(t.y) * 0.008, zl1 - zl0),
                     "liner", g, bevel=0.0)
            fp = J + t * s * (POCKET_HW + 0.03) + n * (2.495 - R_AX + 0.008)
            G["box"]((fp.x, fp.y, (zl0 + zl1) / 2), (abs(t.x) * 0.06 + abs(n.x) * 0.012, abs(t.y) * 0.06 + abs(n.y) * 0.012,
                                                     zl1 - zl0 - 0.01), "steel", g, bevel=0.003)
            for zb in (zl0 + 0.06, (zl0 + zl1) / 2, zl1 - 0.06):
                bp = fp + n * 0.01
                G["bolt"]((bp.x, bp.y, zb), 0.012, 0.01, group=g, rot=(math.pi / 2, 0, math.atan2(n.y, n.x) + math.pi / 2))
        # the riser: on a bolted foot, cast bands, four ribs
        G["cyl"]((J.x, J.y, 0.02), R_BODY + 0.05, 0.04, "iron", g, verts=40, bevel=0.008)
        for k in range(6):
            a = 2 * math.pi * (k + 0.5) / 6
            G["bolt"]((J.x + (R_BODY + 0.03) * math.cos(a), J.y + (R_BODY + 0.03) * math.sin(a), 0.045), 0.012, 0.01,
                      group=g)
        zr1 = Z_RUN - 0.22
        G["cyl"]((J.x, J.y, (0.04 + zr1) / 2), R_BODY, zr1 - 0.04, body, g, verts=48, bevel=0.01)
        for zr in (0.12, 0.62):
            G["cyl"]((J.x, J.y, zr), R_BODY + 0.012, 0.028, "iron_worn", g, verts=48, bevel=0.004)
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            p = J + Vector((math.cos(a), math.sin(a))) * (R_BODY + 0.012)
            G["box"]((p.x, p.y, (0.16 + 0.58) / 2), (0.028, 0.028, 0.4), "iron_worn", g, rot=(0, 0, a), bevel=0.004)
        # the head: a squat cast body, a flange ring, a domed bonnet bolted on, a lifting eye
        zh0, zh1 = Z_RUN - R_HEAD + 0.02, Z_RUN + 0.13
        G["cyl"]((J.x, J.y, (zh0 + zh1) / 2), R_HEAD, zh1 - zh0, body, g, verts=48, bevel=0.02)
        G["cyl"]((J.x, J.y, zh1 + 0.014), R_HEAD + 0.025, 0.028, "iron_worn", g, verts=48, bevel=0.006)
        G["sphere"]((J.x, J.y, zh1 + 0.028), R_HEAD - 0.05, body, g, squash=0.42)
        for k in range(8):
            a = 2 * math.pi * (k + 0.5) / 8
            self.nut(Vector((J.x + (R_HEAD + 0.008) * math.cos(a), J.y + (R_HEAD + 0.008) * math.sin(a), zh1 + 0.036)),
                     (0, 0, 1), g, r=0.016, h=0.014)
        ze = zh1 + 0.028 + (R_HEAD - 0.05) * 0.42            # a lifting eye on a boss
        G["cyl"]((J.x, J.y, ze + 0.008), 0.032, 0.016, "iron_worn", g, verts=20, bevel=0.003)
        G["ring"]((J.x, J.y, ze + 0.045), 0.034, 0.02, 0.012, "steel", g, verts=24, bevel=0.002,
                  rot=(math.pi / 2, 0, math.atan2(toward.y, toward.x)))
        # the outlet spigot and its joint, toward the run
        self.along(((J + toward * SPIGOT / 2).x, (J + toward * SPIGOT / 2).y, Z_RUN), (toward.x, toward.y, 0), R_RUN,
                   SPIGOT, body, g, verts=40, bevel=0.0)
        jc = J + toward * (SPIGOT + JOINT_H)
        self.joint((jc.x, jc.y, Z_RUN), (toward.x, toward.y, 0), FLANGE_R, g)
        if gauge:
            # a pressure gauge on the head's far side, on a short stem, its dial up to the camera
            back_ = J - toward * (R_HEAD + 0.04)
            self.along((back_.x, back_.y, Z_RUN + 0.02), (toward.x, toward.y, 0), 0.014, 0.1, "brass", g, verts=12)
            gp = J - toward * (R_HEAD + 0.1)
            G["cyl"]((gp.x, gp.y, Z_RUN + 0.07), 0.055, 0.024, "brass", g, verts=24, bevel=0.004)
            G["cyl"]((gp.x, gp.y, Z_RUN + 0.083), 0.044, 0.004, "polish", g, verts=24, bevel=0.0)
            G["box"]((gp.x + 0.012, gp.y + 0.008, Z_RUN + 0.086), (0.03, 0.004, 0.002), "dark", g, rot=(0, 0, 0.6),
                     bevel=0.0)
            G["cyl"]((gp.x, gp.y, Z_RUN + 0.035), 0.012, 0.05, "brass", g, verts=10)
        # the connection: a sleeve of the bore from the riser at ZA out to the end ring (the
        # signed-off port's), bolted into it as into a blind flange, open
        if f == "S":
            ye = -2.53 - ZA / 2
            self.along((J.x, (J.y + ye) / 2 + 0.02, ZA), (0, 1, 0), R_RUN, abs(ye - J.y) - 0.04, "steel", g, verts=48,
                       bevel=0.0)
            G["cyl"]((J.x, ye + 0.035, ZA), G["V_RING_R"] - 0.02, 0.07, "steel", g, verts=48, rot=(math.pi / 2, 0, 0),
                     bevel=0.01)
            for k in range(8):
                a = 2 * math.pi * (k + 0.5) / 8
                self.nut(Vector((J.x + 0.33 * math.cos(a), ye - 0.004, ZA + 0.33 * math.sin(a))), (0, 1, 0), g)
            G["cyl"]((J.x, ye - 0.003, ZA), R_RUN - 0.03, 0.006, "dark", g, verts=32, rot=(math.pi / 2, 0, 0), bevel=0.0)
            self.weld_ring(Vector((J.x, ye + 0.08, ZA)), (0, 1, 0), g)
            end = ye
        elif f == "N":
            ye = 2.495 - 0.025
            self.along((J.x, (J.y + ye) / 2, ZA), (0, 1, 0), R_RUN, abs(ye - J.y), "steel", g, verts=48, bevel=0.0)
            G["cyl"]((J.x, ye, ZA), POCKET_HW - 0.01, 0.04, "steel", g, verts=48, rot=(math.pi / 2, 0, 0), bevel=0.008)
            end = ye
        else:
            sgn = 1 if f == "E" else -1
            xf = sgn * (2.5 - 0.03)
            self.along(((J.x + xf) / 2, J.y, ZA), (1, 0, 0), R_RUN, abs(xf - J.x), "steel", g, verts=48, bevel=0.0)
            G["cyl"]((xf, J.y, ZA), G["H_RING_R"] - 0.02, 0.04, "steel", g, verts=48, rot=(0, math.pi / 2, 0),
                     bevel=0.006)
            for k in range(8):
                a = 2 * math.pi * (k + 0.5) / 8
                self.nut(Vector((xf - sgn * 0.026, J.y + 0.27 * math.cos(a), ZA + 0.27 * math.sin(a))), (1, 0, 0), g,
                         r=0.016, h=0.012)
            self.weld_ring(Vector((xf - sgn * 0.07, J.y, ZA)), (1, 0, 0), g)
            end = xf
        return round(end, 3)

    def pair_run(self, d, k, a, b, JA, JB, pts):
        G = self.G
        cfg = self.cfg
        pts = self.resample(pts, 0.02)
        S = self.cum(pts)
        L = S[-1]
        ta = (pts[3] - pts[0]).normalized()
        tb = (pts[-4] - pts[-1]).normalized()
        self.junction(d, a, JA, ta, gauge=True)
        self.junction(d, b, JB, tb, gauge=False)
        s0, s1 = SPIGOT + 2 * JOINT_H + 0.006, L - SPIGOT - 2 * JOINT_H - 0.006
        body = [Vector((p.x, p.y, Z_RUN)) for p, s in zip(pts, S) if s0 <= s <= s1]
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
                self.tube(pc, R_RUN - 0.006, self.mat("hose", "dark"), g, seg=32, rib=0.07, pitch=0.045, name="run-hose")
            else:
                self.tube(pc, R_RUN, cfg["pipe"], g, seg=36, name="run-pipe")

        def at(s):
            i = min(range(len(S)), key=lambda q: abs(S[q] - s))
            p = pts[i]
            t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            return p, t

        marks = []
        arcs, i = [], 0
        while i < len(pts):
            if self.face_of(pts[i]) is None:
                j = i
                while j < len(pts) and self.face_of(pts[j]) is None:
                    j += 1
                arcs.append((S[i], S[j - 1]))
                i = j
            else:
                i += 1
        for sA, sB in arcs:
            marks += [("joint", sA), ("joint", sB)]
            if sB - sA > 0.9:
                if cfg["run"] != "hose":
                    marks += [("weld", sA + (sB - sA) * q) for q in (0.25, 0.5, 0.75)]
                if cfg["support"] == "girder":
                    marks += [("clamp", sA + (sB - sA) * q) for q in (0.2, 0.5, 0.8)]
                else:
                    marks.append(("clamp", sA + (sB - sA) * 0.5))
        for i in range(1, len(pts)):
            f, fp = self.face_of(pts[i]), self.face_of(pts[i - 1])
            if f is None or fp != f:
                continue
            la, lb = self.lat_of(pts[i - 1]), self.lat_of(pts[i])
            if (la > 0) != (lb > 0):
                marks.append(("joint", S[i]))                 # mid-bay: two spools meet
            for lat_mark in (STUB_SADDLE, -STUB_SADDLE):
                if (la - lat_mark) * (lb - lat_mark) <= 0:
                    north_end = lat_mark > 0
                    if cfg["support"] == "girder":
                        if f in "NS" or north_end:
                            marks.append(("clamp", S[i]))
                    else:
                        if f in "NS" or north_end:
                            marks.append(("clamp", S[i]))
            centres = (1.0, -1.0) if f in "NS" else (1 + G["H_AXIS_V"] - G["ZA"] / 2, -1 + G["H_AXIS_V"] - G["ZA"] / 2)
            for c in centres:
                if (la - c) * (lb - c) <= 0 and (pts[i] - JA).length > 0.45 and (pts[i] - JB).length > 0.45:
                    marks.append(("stool", S[i]))
        # the flow arrow: on the longest straight, from A toward B
        best, run_ = None, None
        for i in range(1, len(pts)):
            f = self.face_of(pts[i])
            if f is not None and f == self.face_of(pts[i - 1]):
                run_ = run_ or S[i - 1]
                if best is None or S[i] - run_ > best[1] - best[0]:
                    best = (run_, S[i])
            else:
                run_ = None
        for kind, s in marks:
            if not (s0 + 0.04 < s < s1 - 0.04):
                continue
            p, t = at(s)
            g = self.grp(d, p.y)
            c3 = Vector((p.x, p.y, Z_RUN))
            t3 = Vector((t.x, t.y, 0)).normalized()
            st = SADDLE_TOP
            if kind == "joint":
                if cfg["run"] == "hose":
                    self.ferrules(c3, t3, g)
                else:
                    self.joint(c3, t3, FLANGE_R, g)
            elif kind == "weld":
                self.weld_ring(c3, t3, g)
            elif kind in ("clamp", "stool"):
                rot = math.atan2(t.y, t.x) + math.pi / 2
                if kind == "stool":
                    G["box"]((p.x, p.y, (Z0 + 0.003 + st) / 2), (2 * SADDLE_HL, 0.11, st - Z0 - 0.003), "iron_worn", g,
                             rot=(0, 0, rot), bevel=0.012)
                else:
                    G["box"]((p.x, p.y, (self.sup_top + 0.003 + st) / 2), (2 * SADDLE_HL, 0.07, st - self.sup_top - 0.003),
                             "steel", g, rot=(0, 0, rot), bevel=0.004)
                self.clamp(c3, t3, g, st)
        if best and best[1] - best[0] > 0.6 and cfg["run"] != "hose":
            p, t = at((best[0] + best[1]) / 2)
            if s0 < (best[0] + best[1]) / 2 < s1:
                self.arrow(Vector((p.x, p.y, Z_RUN)), Vector((t.x, t.y, 0)).normalized(), self.grp(d, p.y))
        return dict(pair=[list(a), list(b)], fitting=2 * R_RUN, riser=2 * R_BODY, head=2 * R_HEAD,
                    run=2 * (R_RUN - (0.006 if cfg["run"] == "hose" else 0)), flanges=2 * FLANGE_R,
                    end_ring="the signed-off port's", length=round(L, 2))

    def ferrules(self, c, t, g):
        """The hose take's joints: a crimped steel ferrule pair with its coupling nut."""
        for s in (-1, 1):
            self.along(c + t * s * 0.05, t, R_RUN + 0.02, 0.08, "steel", g, verts=36, bevel=0.006)
            for q in (0.03, 0.07):
                self.along(c + t * s * q, t, R_RUN + 0.026, 0.008, "steel", g, verts=36, bevel=0.002)
        self.along(c, t, R_RUN + 0.035, 0.03, "bolt", g, verts=6, bevel=0.003)

    def clamp(self, c, t, g, saddle_top):
        """A U-bolt over the run, its legs through the saddle, a hex nut on each."""
        u = Vector((-t.y, t.x, 0))
        rr = R_RUN + 0.014
        pts = [c + u * rr + Vector((0, 0, saddle_top + 0.004 - c.z))]
        pts += [c + u * rr + Vector((0, 0, -0.02 * (1 - q / 4))) for q in range(1, 5)]
        pts += [c + (u * math.cos(a) + Vector((0, 0, 1)) * math.sin(a)) * rr for a in (math.pi * q / 24 for q in range(25))]
        pts += [c - u * rr + Vector((0, 0, saddle_top + 0.004 - c.z))]
        self.tube(self.resample(pts, 0.01), 0.009, "steel", g, seg=10, name="ubolt")
        for s in (-1, 1):
            q = c + u * s * rr
            self.nut(Vector((q.x, q.y, saddle_top + 0.012)), (0, 0, 1), g)

    def arrow(self, c, t, g):
        """A worn stencilled flow arrow on the pipe's top."""
        G = self.G
        size = 0.018
        u = Vector((-t.y, t.x, 0))
        o = c + Vector((0, 0, R_RUN - 0.002)) - t * size * 3 + u * size * 2
        G["stencil"](tuple(o), (0, 0, math.atan2(t.y, t.x)), "...#.../...##../#######/...##../...#...", size, group=g,
                     mat="stencil_worn")

    # ------------------------------------------------------------ the slots, per direction
    def pockets(self):
        G = self.G
        places = set()
        for d, deg in G["contract"].DIRECTIONS["four"]:
            for c in fit_conns(deg):
                J = self.junction_xy(*c, G)
                places.add((round(J.x, 4), round(J.y, 4), c[2]))
        for i in range(4):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -20))
            cb = bpy.context.active_object
            cb.name = f"slotcut{i}"
            cb.hide_render = True
            cb.display_type = "WIRE"
            cb.parent = G["BODY"]
            self.pocket_cutters.append(cb)
        boxes = [self.slot_box(Vector((x, y)), f) for (x, y, f) in places]
        targets = []
        for g, objs in G["PARTS"].items():
            if g in self.SKIP_GROUPS or g.startswith("rig-"):
                continue
            for o in objs:
                if o.type != "MESH":
                    continue
                lo, hi = self.bbox(o)
                if any(all(lo[i] <= c[i] + s[i] / 2 and hi[i] >= c[i] - s[i] / 2 for i in range(3)) for c, s in boxes):
                    targets.append(o)
        for o in targets:
            G["cut"](o, *self.pocket_cutters)
        self.pocket_targets = targets
        print(f"RIG slots: {len(targets)} plate parts take the slot cutters", flush=True)

    @staticmethod
    def slot_box(J, f):
        n = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[f]
        rr0, rr1 = CUT_IN, 2.9
        mid = (rr0 + rr1) / 2
        if f in "NS":
            return Vector((J.x, n[1] * mid, (-0.1 + Z0 + 0.01) / 2)), Vector((2 * POCKET_HW, rr1 - rr0, Z0 + 0.11))
        return Vector((n[0] * mid, J.y, (-0.1 + Z0 + 0.01) / 2)), Vector((rr1 - rr0, 2 * POCKET_HW, Z0 + 0.11))

    def place_pockets(self, d=None):
        G = self.G
        if d is None:
            for cb in self.pocket_cutters:
                cb.location = (0, 0, -20)
        else:
            deg = dict(G["contract"].DIRECTIONS["four"])[d]
            for cb, c in zip(self.pocket_cutters, fit_conns(deg)):
                ctr, s = self.slot_box(self.junction_xy(*c, G), c[2])
                cb.location, cb.scale = ctr, s
        bpy.context.view_layer.update()

    # ------------------------------------------------------------ build and render
    def go(self, pas, collide):
        G = self.G
        if collide:
            pas = "collide"
        self.cut_back()
        self.dry_rig()
        if pas in ("rig", "collide", "preview"):
            self.pockets()
            self.wet()
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
            if d == dirs[0]:
                self.place_pockets(None)
                G["setup"](visible=G["STATIC"] + G["DOORS"])
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
        """As T03d's: every part of the rig against the drill and each other, by BVH overlap of
        the evaluated meshes; a direction's pair (both junctions and the run, welded and bolted
        as one) is one assembly, not tested against itself; each direction alone with its
        slots cut; the dry rig against the rest of the plate."""
        G = self.G
        G["pose"](0)

        def tree(o):
            dg = bpy.context.evaluated_depsgraph_get()
            e = o.evaluated_get(dg)
            me = e.to_mesh()
            mw = G["BODY"].matrix_world.inverted() @ o.matrix_world
            vs = [mw @ v.co for v in me.vertices]
            polys = [tuple(p.vertices) for p in me.polygons]
            e.to_mesh_clear()
            if not polys:
                return None, None
            lo = Vector([min(v[i] for v in vs) for i in range(3)])
            hi = Vector([max(v[i] for v in vs) for i in range(3)])
            return BVHTree.FromPolygons(vs, polys), (lo, hi)

        def meet(a, b):
            return all(a[0][i] <= b[1][i] and b[0][i] <= a[1][i] for i in range(3))

        def info(a, b):
            for nm in (a, b):
                o = bpy.data.objects[nm]
                lo, hi = self.bbox(o)
                m = o.active_material.name if o.active_material else ""
                print(f"RIGINFO {nm} [{m}] {tuple(round(v, 2) for v in lo)} {tuple(round(v, 2) for v in hi)}")

        groups = [g for g in G["PARTS"] if g not in self.SKIP_GROUPS and not g.startswith("rig-")] + ["ring"]
        plate = [o for g in groups for o in G["PARTS"].get(g, []) if o.type == "MESH"]
        dry = [o for o in self.dry if o.type == "MESH"]
        dry_names = {o.name for o in dry}
        self.place_pockets(None)
        trees = {o.name: tree(o) for o in plate}
        found = []
        for o in dry:
            ta, ba = trees[o.name]
            for q in plate:
                if q.name in dry_names:
                    continue
                tb, bb = trees[q.name]
                if ta and tb and meet(ba, bb) and ta.overlap(tb):
                    found.append(f"{o.name} x {q.name}")
        print(f"COLLIDE dry rig: {len(dry)} parts against {len(plate)} plate meshes; clashes {len(found)}", flush=True)
        for c_ in found:
            print("COLLIDE", c_)
            info(*c_.split(" x "))
        total = len(found)
        for d, _ in G["contract"].DIRECTIONS["four"]:
            self.place_pockets(d)
            for o in self.pocket_targets:
                trees[o.name] = tree(o)
            wet = [o for g in (f"rig-behind-{d}", f"rig-front-{d}") for o in G["PARTS"].get(g, []) if o.type == "MESH"]
            wt = {o.name: tree(o) for o in wet}
            found = []
            for o in wet:
                ta, ba = wt[o.name]
                if not ta:
                    continue
                for q in plate:
                    tb, bb = trees[q.name]
                    if tb and meet(ba, bb) and ta.overlap(tb):
                        found.append(f"{o.name} x {q.name}")
                for q in wet:
                    if q.name <= o.name or self.assembly.get(q.name) == self.assembly.get(o.name):
                        continue
                    tb, bb = wt[q.name]
                    if tb and meet(ba, bb) and ta.overlap(tb):
                        found.append(f"{o.name} x {q.name}")
            print(f"COLLIDE wet {d}: {len(wet)} parts; clashes {len(found)}", flush=True)
            for c_ in found:
                print("COLLIDE", c_)
                info(*c_.split(" x "))
            total += len(found)
        print(f"COLLIDE clashes {total}", flush=True)
