"""Take C2 on the model (task ballast-drill-ports, T03l; rig-round-7): the wet pipework, per direction,
as concept/ballast-drill/pipe-concepts/pipe_concepts.py's T03k section draws it (Liam, 2026-10-28:
"Yes, build it"). Imported by rig_parts.py; every number not set here is the drawing's (imported).

Per connection, four a direction (vanilla's big mining drill's: W, E, S, S turned):
  the wall fitting  the signed-off end ring, set in a shallow recessed boss in the plate's wall (the
                    south face's too now: the face is out at SF, so its rings sit flush), cut in that
                    direction's wet layers only; the connection's pipe runs on inside the casting
                    (not modelled) up to the gooseneck
  the gooseneck     cast in the plate's top over its own fitting (its axis GN_IN in from the face, its
                    body GN_SET inside it: solid wall all round): a bolted seat, a round cast body with
                    a band, a domed head and a lifting eye, its outlet turned down along the hose
  the hose          0.32 across (vanilla's big drill's), ribbed, in one curve on the drawing's
                    waypoints (Catmull-Rom, as drawn), sagging SAG between its ends; a crimped ferrule
                    and a bolted band clamp at each end
  the end boss      a cast block on the plate against the press's landing shoulder, the hose's nozzle
                    turned down into it through a bolted flange

Where the model differs from the drawing (each in the report):
  - the boss's inner face at BOSS_R0 1.46, not 1.38: the shoulder's cast gussets and bolts stand to
    1.455 (the drawing has no gussets); the hose's end out at R_END_M 1.68 (drawn 1.62), so the
    nozzle stands wholly on the boss
  - the hose's end at z 1.24 (drawn 1.17) and its sag as sin^2 (drawn sin): drawn, the hose's last
    0.2 passes through the boss's top (1.01); the boss ends just round the nozzle (drawn out to 1.74)
  - the E- and W- ends at bearing -27 / -153 (drawn -36 / -144): at -36 the boss meets the snubber
    at 315 degrees (r 1.5, 0.24 square: the drawing has no snubbers)
  - the gooseneck's outlet a cast nose 0.27 long (the drawing's hood reaches 0.16 and the band 0.17): at
    0.17 the clamp would cut the north bastions' corners (the hose passes them 0.026 clear)
  - an E/W ring's recess meets the chute port's frame (the ring's edge reaches 0.463 across the
    face; the frame stands to 0.47): its liners stop at the frame, the frame is that side's edge
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "pipe-concepts")))
import pipe_concepts as P  # noqa: E402

PT = 0.85
FACE = 2.496                      # the plate's N, E and W faces (rig_parts PLATE_FACE)
SF = P.SF                         # 2.74: the south face
R2 = P.R2                         # 0.16: the hose's radius (0.32 across)
GN_R = P.GN_R                     # 0.21: the gooseneck's cast body
GN_IN = P.GN_IN                   # 0.29: its axis in from the face
Z_MOUTH, SAG = P.Z_MOUTH, P.SAG  # 1.15, 0.12
Z_END = 1.24                      # the hose's end (drawn P.Z_END 1.17): its underside clear of the boss it ends over
SH_TOP = 1.01                     # the landing shoulder's top (the model's ZS)
R_END_M = 1.68                    # the hose's end, radially (drawn 1.62)
BEARING = {"N": 70.0, "S": -70.0, "E+": 11.0, "E-": -27.0}     # the ends' bearings, east side (drawn E- -36)
BOSS_R0, BOSS_R1, BOSS_HW = 1.46, 1.82, 0.20
NOZ_R = R2 - 0.01                 # the nozzle's cast body
NOZ_IN = 0.06                     # its axis beyond the hose's end
PORT_EDGE = 0.47                  # the chute port's frame, across the face (sec_ports: PORT_HW + PORT_FR)
NOSE = 0.27                       # the gooseneck's outlet nose, from its axis along the hose's line
NOSE_R = GN_R - 0.04              # 0.17: the nose (the body is 0.21)
S0 = NOSE                         # the hose starts at the nose's flange
RECESS_DEPTH = 0.096              # the recessed boss's depth (rig-round-6: RECESS_BACK 2.40 off the 2.496 face)


def face_out(f):
    return SF if f == "S" else FACE


def key_of(f, lat):
    return P.fit_key(f, lat)


def tag(key):
    return key.replace("+", "p").replace("-", "m")


def end_xy(a):
    return (R_END_M * math.cos(math.radians(a)), R_END_M * math.sin(math.radians(a)))


def waypoints(key):
    """The drawing's plan waypoints (pipe_concepts.base_route_c2), laid for the east side and
    mirrored, the end moved as the module's docstring says; the first point the gooseneck's axis."""
    f, s = key[0], key[1]
    if f == "N":
        pts = [(1.0, FACE - GN_IN), (0.74, 2.10), (0.62, 1.80), end_xy(BEARING["N"])]
    elif f == "S":
        pts = [(1.0, -(SF - GN_IN)), (0.74, -2.12), (0.64, -1.92), end_xy(BEARING["S"])]
    elif s == "+":
        pts = [(FACE - GN_IN, 0.806), (1.92, 0.54), end_xy(BEARING["E+"])]
    else:
        pts = [(FACE - GN_IN, -1.194), (1.66, -1.10), end_xy(BEARING["E-"])]
    pts = P.mirror_route(pts, key)
    pts[0] = P.pc.on_face(f, P.lat_of(key), face_out(f) - GN_IN)
    return pts


def route(key):
    """The hose's line, 3D, from the gooseneck's axis (z Z_MOUTH) to its end (z Z_END), sagging SAG in
    the middle (the drawing's sag; as sin^2, not sin, so it leaves the nose and meets the nozzle level
    rather than at 25 degrees), resampled every 0.01."""
    plan = P.catmull(waypoints(key))
    L = P.length(plan)
    out, acc = [], 0.0
    for i, p in enumerate(plan):
        if i:
            acc += math.hypot(p[0] - plan[i - 1][0], p[1] - plan[i - 1][1])
        u = acc / L
        out.append(Vector((p[0], p[1], Z_MOUTH + (Z_END - Z_MOUTH) * u - SAG * math.sin(math.pi * u) ** 2)))
    res = [out[0]]
    for a, b in zip(out, out[1:]):
        n = max(1, int((b - a).length / 0.01))
        res += [a.lerp(b, k / n) for k in range(1, n + 1)]
    return res


def cum(pts):
    s = [0.0]
    for a, b in zip(pts, pts[1:]):
        s.append(s[-1] + (b - a).length)
    return s


def at(pts, S, s):
    i = min(range(len(S)), key=lambda q: abs(S[q] - s))
    t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
    return pts[i], t


def build(rig, d, conn):
    """One connection's pipework in direction d: the wall fitting, the gooseneck, the hose and the end
    boss. Returns (key, sizes, every object, the hose's pieces, its two ends' ferrules and clamps,
    its centreline). The run (runs.py) is the hose and its ferrules; the gooseneck and the nozzle
    are the hosts its ends go into."""
    G = rig.G
    x, y, f = conn
    lat = rig.fit_lat(x, y, f, G)
    key = key_of(f, lat)
    pts = route(key)
    S = cum(pts)
    L = S[-1]
    A = pts[0]
    gx, gy = A.x, A.y
    g0 = rig.grp(d, gy)
    before = set(bpy.data.objects)
    ring_at = rig.wall_fitting(d, conn, g0)
    # ---- the gooseneck
    gn_before = set(bpy.data.objects)
    zs = PT + 0.001
    G["cyl"]((gx, gy, zs + 0.02), GN_R + 0.05, 0.04, "iron_worn", g0, verts=48, bevel=0.008)        # its seat
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8
        rig.nut(Vector((gx + (GN_R + 0.032) * math.cos(a), gy + (GN_R + 0.032) * math.sin(a), zs + 0.048)), (0, 0, 1),
                g0, r=0.014, h=0.012)
    G["cyl"]((gx, gy, (zs + 0.04 + Z_MOUTH) / 2), GN_R, Z_MOUTH - zs - 0.04, "iron", g0, verts=48, bevel=0.006)
    G["cyl"]((gx, gy, zs + 0.11), GN_R + 0.012, 0.03, "iron_worn", g0, verts=48, bevel=0.004)          # a cast band
    G["cyl"]((gx, gy, Z_MOUTH - 0.03), GN_R + 0.01, 0.024, "iron_worn", g0, verts=48, bevel=0.004)
    G["sphere"]((gx, gy, Z_MOUTH), GN_R, "iron", g0, squash=0.72)                                      # the domed head
    top = Z_MOUTH + GN_R * 0.72
    p1, _ = at(pts, S, S0 + 0.02)
    t_out = (p1 - A).normalized()
    yaw = math.atan2(t_out.y, t_out.x)
    G["cyl"]((gx, gy, top + 0.004), 0.032, 0.016, "iron_worn", g0, verts=20, bevel=0.003)             # the lifting eye
    G["ring"]((gx, gy, top + 0.04), 0.034, 0.02, 0.012, "steel", g0, verts=24, bevel=0.002,
              rot=(math.pi / 2, 0, yaw))
    # the outlet: a cast nose out of the body along the hose's line (the drawing's hood, carried 0.10
    # further so the hose's clamp clears the north bastions' corners), a flange at its end, the hose
    # over a spigot in it
    rig.along(A + t_out * (NOSE - 0.01) / 2, t_out, NOSE_R, NOSE - 0.01, "iron", g0, verts=40, bevel=0.006)
    rig.along(A + t_out * (NOSE - 0.012), t_out, NOSE_R + 0.016, 0.024, "iron_worn", g0, verts=40, bevel=0.005)
    rig.along(A + t_out * (NOSE + 0.02), t_out, R2 - 0.02, 0.06, "iron_worn", g0, verts=32, bevel=0.0)    # the spigot
    _, u_, w_ = rig.basis(t_out)
    for k in range(6):
        a = 2 * math.pi * (k + 0.5) / 6
        q = A + t_out * (NOSE - 0.028) + (u_ * math.cos(a) + w_ * math.sin(a)) * (NOSE_R + 0.004)
        rig.nut(q, t_out, g0, r=0.01, h=0.01)
    gn = [o for o in bpy.data.objects if o not in gn_before]
    # ---- the hose: its two ferrules and clamps, and the ribbed hose between
    E1, t1 = pts[-1], (pts[-1] - pts[-4]).normalized()
    f0 = clamp_end(rig, A + t_out * (NOSE + 0.045), t_out, d)
    f1 = clamp_end(rig, E1 - t1 * 0.035, t1, d)
    i0 = next(i for i, s in enumerate(S) if s >= S0)
    body = [A + t_out * S0] + pts[i0 + 1:]
    hose_objs = []
    pieces, cur = [], [body[0]]
    for p in body[1:]:
        if (p.y > 0) != (cur[-1].y > 0):
            m = cur[-1].lerp(p, cur[-1].y / (cur[-1].y - p.y))
            cur.append(m)
            pieces.append(cur)
            cur = [m]
        cur.append(p)
    pieces.append(cur)
    for pc in pieces:
        if len(pc) < 2:
            continue
        hose_objs.append(rig.tube(pc, R2, "hose_c2", rig.grp(d, sum(p.y for p in pc) / len(pc)), seg=32, rib=0.08,
                                  pitch=0.05, name="hose"))
    # ---- the nozzle, down into the end boss on the plate against the shoulder
    nz_before = set(bpy.data.objects)
    N = E1 + t1 * NOZ_IN
    g1 = rig.grp(d, N.y)
    rig.along(E1 + t1 * (NOZ_IN / 2 - 0.02), t1, NOZ_R, NOZ_IN + 0.04, "pipe_iron", g1, verts=40, bevel=0.0)  # spigot
    ztop = N.z + 0.02
    G["cyl"]((N.x, N.y, (SH_TOP + 0.02 + ztop) / 2), NOZ_R, ztop - SH_TOP - 0.02, "pipe_iron", g1, verts=40,
             bevel=0.004)
    G["sphere"]((N.x, N.y, ztop), NOZ_R, "pipe_iron", g1, squash=0.6)
    G["cyl"]((N.x, N.y, SH_TOP + 0.012), NOZ_R + 0.025, 0.024, "iron_worn", g1, verts=40, bevel=0.004)  # its flange
    for k in range(6):
        a = 2 * math.pi * (k + 0.5) / 6
        rig.nut(Vector((N.x + (NOZ_R + 0.012) * math.cos(a), N.y + (NOZ_R + 0.012) * math.sin(a), SH_TOP + 0.03)),
                (0, 0, 1), g1, r=0.012, h=0.01)
    bear = math.atan2(N.y, N.x)
    c, s_ = math.cos(bear), math.sin(bear)
    r1 = N.xy.length + NOZ_R + 0.03                 # just round the nozzle: the hose passes over the rest

    def bp(r, t, z):
        return (c * r - s_ * t, s_ * r + c * t, z)
    lo = [bp(BOSS_R0, -BOSS_HW, PT + 0.001), bp(r1, -BOSS_HW, PT + 0.001), bp(r1, BOSS_HW, PT + 0.001),
          bp(BOSS_R0, BOSS_HW, PT + 0.001)]
    hi = [(p[0], p[1], SH_TOP) for p in lo]
    rig.plate_box(lo, hi, "iron", g1, bevel=0.014)                                                   # the boss
    # its foot: a cast lip round its outer end, bolted down to the plate
    lo2 = [bp(r1 - 0.12, -BOSS_HW - 0.03, PT + 0.001), bp(r1 + 0.03, -BOSS_HW - 0.03, PT + 0.001),
           bp(r1 + 0.03, BOSS_HW + 0.03, PT + 0.001), bp(r1 - 0.12, BOSS_HW + 0.03, PT + 0.001)]
    rig.plate_box(lo2, [(p[0], p[1], PT + 0.04) for p in lo2], "iron_worn", g1, bevel=0.008)
    for q in (bp(r1 - 0.06, -BOSS_HW - 0.014, PT + 0.046), bp(r1 - 0.06, BOSS_HW + 0.014, PT + 0.046),
              bp(r1 + 0.014, -0.1, PT + 0.046), bp(r1 + 0.014, 0.1, PT + 0.046)):
        rig.nut(Vector(q), (0, 0, 1), g1, r=0.012, h=0.01)
    noz = [o for o in bpy.data.objects if o not in nz_before]
    objs = [o for o in bpy.data.objects if o not in before]
    sizes = dict(key=key, connection=[x, y, f], hose=round(2 * R2, 3), gooseneck=round(2 * GN_R, 3),
                 gooseneck_axis=[round(gx, 3), round(gy, 3)], length=round(L, 3), hose_end=[round(E1.x, 3), round(E1.y, 3)],
                 nozzle=[round(N.x, 3), round(N.y, 3)], lowest_over_plate=round(min(p.z for p in body) - R2 - PT, 3),
                 ring_at=ring_at)
    return key, sizes, objs, hose_objs, f0, f1, body


def clamp_end(rig, c, t, d):
    """A crimped steel ferrule over the hose's end at c (axis t), and a bolted band clamp over it."""
    g = rig.grp(d, c.y)
    before = set(bpy.data.objects)
    rig.along(c, t, R2 + 0.022, 0.07, "steel", g, verts=40, bevel=0.006)
    for q in (-0.02, 0.02):
        rig.along(c + t * q, t, R2 + 0.027, 0.008, "steel", g, verts=40, bevel=0.002)                 # crimps
    _, u, w = rig.basis(t)
    rig.along(c + t * 0.0, t, R2 + 0.034, 0.018, "iron_worn", g, verts=40, bevel=0.003)               # the band
    lug = c - w * (R2 + 0.045)                      # (basis(): w is down for a level t; the lug on top)
    rig.G["box"](tuple(lug), (0.03, 0.03, 0.03), "steel", g, rot=tuple(Vector((0, 0, 1)).rotation_difference(w).to_euler()),
                 bevel=0.004)
    rig.nut(lug + u * 0.022, u, g, r=0.01, h=0.012)
    return [o for o in bpy.data.objects if o not in before]
