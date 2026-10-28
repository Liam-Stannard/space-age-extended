# The routes are laid where this camera sees them: it looks from the south.
# T03i (B2): every service stays off the gallery (outside 1.94 from PT to the runs' flanges, where
# the runs lie in some direction) and out of the shoe's sweep; they run on the plate's top between
# the bastions, the bays' risers and the snubbers, up and over the bastions' faces and roofs, and on
# the gear-houses' roofs and open fronts. Each end in a fitting, a gland or a bulkhead.


def face_pt(a, b, s, z, u=0.0, out=0.0):
    """A point on the wall face a->b (counter-clockwise): s along it, u more along it, `out` in
    front of it, at height z."""
    a, b = Vector(a), Vector(b)
    t = (b - a).normalized()
    n = Vector((t.y, -t.x))
    p = a + t * (s + u) + n * out
    return (p.x, p.y, z)


def fitting(p, n, r=0.03, mat="steel"):
    """A hex hose fitting on a wall at p, its nipple along n (plan); returns the nipple's tip."""
    n = Vector((n[0], n[1], 0)).normalized()
    p = Vector(p)
    along(p + n * 0.02, n, r, 0.03, mat, verts=6)
    along(p + n * 0.055, n, 0.016, 0.035, "brass", verts=12)
    return tuple(p + n * 0.055)


cx_sw, cy_sw, ys_sw = HOUSES[-1]
cx_se, cy_se, ys_se = HOUSES[1]
SW_D = ((-0.90, -1.85), (-1.35, -1.40))              # the south-west bastion's diagonal, counter-clockwise
SE_D = ((1.35, -1.40), (0.90, -1.85))
SW_N = ((-1.35, -1.40), (-1.94, -1.40))              # its north face
SE_N = ((1.94, -1.40), (1.35, -1.40))
# --- the rams' bulkheads, at the bays' risers' corners (on the plate, as signed off)
B_S, B_S2 = bulkhead(-0.6, -1.585, PT + 0.024, 180, 90)    # the south ram's, on its riser's cap rail
B_W, B_W2 = bulkhead(-1.6, -0.86, PT, -60, -90)             # the west ram's, at its riser's corner
B_E = bulkhead(1.56, -0.86, PT, -120)
B_N = bulkhead(-0.76, 1.58, PT, 200)
# --- south-west: the manifold on the bastion's inner face, low; the west ram's outlets on its north face
mf = face_empty("manifold", *SW_D, 0.32, PT + 0.3)
box((0, -0.006, 0), (0.24, 0.012, 0.16), "steel", parent=mf, bevel=0.003)          # its welded plate
box((0, -0.06, 0), (0.18, 0.1, 0.1), "jbox", parent=mf, bevel=0.008)               # the valve block
cyl((0.03, -0.06, 0.08), 0.026, 0.06, "copper", verts=12, bevel=0.004, parent=mf)   # a solenoid
nrm_sw = Vector((1, 1)).normalized()
P_E1 = fitting(face_pt(*SW_D, 0.32, PT + 0.28, -0.045, 0.11), nrm_sw, 0.022)
P_E2 = fitting(face_pt(*SW_D, 0.32, PT + 0.32, 0.045, 0.11), nrm_sw, 0.018)
TOP_MF = face_pt(*SW_D, 0.32, PT + 0.36, 0.0, 0.06)        # its top fitting (the reservoir's feed)
cyl(TOP_MF, 0.02, 0.04, "brass", verts=12, bevel=0.0)
nw_out = Vector((0, 1))
W1 = fitting(face_pt(*SW_N, 0.36, PT + 0.30, 0.0, 0.0), nw_out, 0.026)
W2 = fitting(face_pt(*SW_N, 0.48, PT + 0.26, 0.0, 0.0), nw_out, 0.02)
for s_, z_ in ((0.36, PT + 0.30), (0.48, PT + 0.26)):
    q = face_pt(*SW_N, s_, z_)
    box((q[0], q[1] + 0.006, q[2]), (0.08, 0.012, 0.08), "steel", bevel=0.003)        # their bosses
# --- south-east: the east ram's valve block on the roof's north-east corner; the switchgear's
# junction box on the south face over its gland
VB = (1.76, -1.47, RT)
box((VB[0], VB[1], VB[2] + 0.04), (0.12, 0.1, 0.08), "jbox", bevel=0.008)
cyl((VB[0] - 0.03, VB[1], VB[2] + 0.11), 0.022, 0.06, "copper", verts=12, bevel=0.004)          # its solenoid
cyl((VB[0] + 0.035, VB[1] + 0.01, VB[2] + 0.1), 0.016, 0.04, "steel", verts=12, bevel=0.003)
for yy in (VB[1] - 0.055, VB[1] + 0.055):
    weld((VB[0] - 0.06, yy, VB[2] + 0.004), (VB[0] + 0.06, yy, VB[2] + 0.004))
VB_N = (VB[0] + 0.02, VB[1] + 0.05, VB[2] + 0.04)        # its outlet north, to the east ram
cyl((VB_N[0], VB_N[1] + 0.012, VB_N[2]), 0.016, 0.03, "brass", verts=10, rot=(math.pi / 2, 0, 0), bevel=0.0)
VB_S = (VB[0] - 0.02, VB[1] - 0.05, VB[2] + 0.04)        # its inlet south, from the bottle
cyl((VB_S[0], VB_S[1] - 0.012, VB_S[2]), 0.016, 0.03, "brass", verts=10, rot=(math.pi / 2, 0, 0), bevel=0.0)
JB_SE = (1.33, ys_se, PT + 0.62)
je = empty("jbox-wall", (JB_SE[0], ys_se - 0.002, JB_SE[2]), (-math.pi / 2, 0, 0))
box((0, 0, 0.03), (0.14, 0.18, 0.06), "jbox", parent=je, bevel=0.006)
box((0, 0, 0.063), (0.15, 0.19, 0.008), "jbox", parent=je, bevel=0.003)
for i in (-1, 1):
    for j in (-1, 1):
        bolt((i * 0.055, j * 0.075, 0.07), 0.008, 0.006, parent=je)
# --- north: a junction box on each gear-house's roof
JB_N = {}
for (x, y, out) in WINCHES:
    p_ = (out * 1.42, 0.97, HR + 0.06)
    if out > 0:
        p_ = (1.50, 0.95, HR + 0.06)
    box((p_[0], p_[1], p_[2] + 0.006), (0.18, 0.14, 0.012), "steel", bevel=0.003)
    weld((p_[0] - 0.09, p_[1] - 0.07, p_[2] + 0.004), (p_[0] + 0.09, p_[1] - 0.07, p_[2] + 0.004))
    jbox((p_[0], p_[1], p_[2] + 0.012), (0.15, 0.11, 0.1), math.radians(-4 * out))
    JB_N[out] = p_
# the gear-houses' roofs: on the north-west's a fan cowl over the winch motor's duct and a tray to
# it; on the north-east's a lubricant reservoir on saddles beside the hatch
xw_, yw_, _ = WINCHES[1]
COWL = (-1.30, 1.65, HR + 0.06)
box((COWL[0], COWL[1], COWL[2] + 0.06), (0.24, 0.18, 0.12), "jbox", bevel=0.01)
for k in range(4):
    box((COWL[0], COWL[1] - 0.092, COWL[2] + 0.025 + 0.025 * k), (0.18, 0.012, 0.01), "steel", bevel=0.0)
box((COWL[0], COWL[1], COWL[2] + 0.128), (0.26, 0.2, 0.016), "jbox", bevel=0.004)
for i in (-1, 1):
    weld((COWL[0] + i * 0.12, COWL[1] - 0.09, COWL[2] + 0.004), (COWL[0] + i * 0.12, COWL[1] + 0.09, COWL[2] + 0.004))
TR_NW = tray((-1.30, 1.09), (-1.30, 1.45), HR + 0.12, w=0.08, zf=HR + 0.06)
xe_, ye_, _ = WINCHES[0]
RES = (1.62, 1.20, HR + 0.06)
for dx in (-0.08, 0.08):
    box((RES[0] + dx, RES[1], RES[2] + 0.03), (0.03, 0.14, 0.06), "steel", bevel=0.003)          # saddles
cyl((RES[0], RES[1], RES[2] + 0.1), 0.07, 0.3, "jbox", verts=24, rot=(0, math.pi / 2, 0), bevel=0.01)
for dx in (-0.08, 0.08):
    ring((RES[0] + dx, RES[1], RES[2] + 0.1), 0.077, 0.068, 0.02, "steel", verts=24, bevel=0.0, rot=(0, math.pi / 2, 0))
cyl((RES[0] + 0.06, RES[1], RES[2] + 0.18), 0.022, 0.03, "brass", verts=12, bevel=0.003)          # its filler cap
cyl((RES[0] - 0.06, RES[1] - 0.06, RES[2] + 0.11), 0.02, 0.025, "polish", verts=12, rot=(math.pi / 2, 0, 0), bevel=0.0)

# north-west: the accumulator inside the bastion, its fittings on the diagonal face: high to the
# winch's brake cylinder under the floor, low to the north ram; the north snubbers' bulkheads
a_nw, b_nw, L_nw, s_nw = CABS[-1]
a_ne, b_ne, L_ne, s_ne = CABS[1]
n_nw = Vector((1, -1)).normalized()
n_ne = Vector((-1, -1)).normalized()
F_BRK = fitting(face_pt(a_nw, b_nw, s_nw(0.10), 2.05), n_nw)
F_NR = fitting(face_pt(a_nw, b_nw, s_nw(1.38), PT + 0.14), n_nw)
BRK = (WINCHES[1][0] - 0.14, WINCHES[1][1] - 0.215)
cyl((BRK[0], BRK[1], GUIDE_TOP - 0.06), 0.035, 0.1, "steel", verts=16, bevel=0.004)
SNB = {1: fitting(face_pt(a_ne, b_ne, s_ne(0.62), PT + 0.2), n_ne), -1: fitting(face_pt(a_nw, b_nw, s_nw(0.62), PT + 0.2),
                                                                                  n_nw)}
for out_, (aa, bb, LL, ss), nn in ((1, CABS[1], n_ne), (-1, CABS[-1], n_nw)):
    q = face_pt(aa, bb, ss(0.62), PT + 0.2)
    box(q, (0.08, 0.08, 0.08), "steel", rot=(0, 0, math.atan2(nn.y, nn.x)), bevel=0.004)
# the festoon's junction box on each north bastion's diagonal, low beside the door, and its floor gland
FEST = {}
for out_, (aa, bb, LL, ss) in CABS.items():
    fe_ = face_empty("festoon-box", aa, bb, ss(0.12), 1.60)
    box((0, -0.03, 0), (0.09, 0.06, 0.12), "jbox", parent=fe_, bevel=0.005)
    top_ = face_pt(aa, bb, ss(0.12), 1.54, 0.0, 0.03)
    fg = face_pt(aa, bb, ss(0.16), PT, 0.0, 0.17)
    cyl((fg[0], fg[1], PT + 0.012), 0.045, 0.024, "steel", verts=16, bevel=0.004)
    cyl((fg[0], fg[1], PT + 0.034), 0.028, 0.026, "brass", verts=12, bevel=0.003)
    FEST[out_] = (top_, (fg[0], fg[1], PT + 0.05))

# the south legs' levelling jacks: a ram on each pad, beside the leg, its hose fitting on top
JACKS = {}
for sx, (jx, jy) in ((-1, (-1.95, -2.36)), (1, (2.36, -1.95))):
    box((jx, jy, 0.12), (0.13, 0.13, 0.02), "steel", bevel=0.004)                       # its base, welded on
    cyl((jx, jy, 0.21), 0.05, 0.16, "jbox", verts=20, bevel=0.008)                      # the cylinder
    cyl((jx, jy, 0.3), 0.036, 0.03, "polish", verts=16, bevel=0.003)                    # the rod's gland
    cyl((jx, jy, 0.33), 0.03, 0.04, "steel", verts=16, bevel=0.003)
    cyl((jx + 0.055 * (1 if sx < 0 else 0), jy + 0.055 * (1 if sx > 0 else 0), 0.25), 0.016, 0.03, "brass", verts=10,
        rot=(0, math.pi / 2, 0) if sx < 0 else (math.pi / 2, 0, 0), bevel=0.0)       # its port
    JACKS[sx] = (jx + 0.075 * (1 if sx < 0 else 0), jy + 0.075 * (1 if sx > 0 else 0), 0.25)
# (T03i) each fed through its leg: a gland on the leg's lower band, toward the jack
LEG_GL = {}
for sx in (-1, 1):
    top_, foot_ = LEGS[(sx, -1)]
    c = top_.lerp(foot_, 0.8)
    jp = Vector(JACKS[sx])
    h = Vector((jp.x - c.x, jp.y - c.y, 0)).normalized()
    p = c + h * 0.17
    along(p + h * 0.02, h, 0.028, 0.04, "brass", verts=12)
    LEG_GL[sx] = tuple(p + h * 0.045)

# the bottles' and the reservoir's shells: dished ends on a horizontal shell
def dome(c, ax, r, depth, mat, seg=36, rings=8):
    """A dished end: a half-ellipsoid r across and depth deep, its rim on the shell's end at c,
    bulging along ax (a unit plan vector); built in place."""
    ax = Vector((ax[0], ax[1], 0)).normalized()
    u = Vector((-ax.y, ax.x, 0))
    w = Vector((0, 0, 1))

    def build(bm):
        rows = []
        for i in range(rings):
            th = (math.pi / 2) * i / rings
            rows.append([bm.verts.new(c + (u * math.cos(2 * math.pi * j / seg) + w * math.sin(2 * math.pi * j / seg))
                                      * (r * math.cos(th)) + ax * depth * math.sin(th)) for j in range(seg)])
        pole = bm.verts.new(c + ax * depth)
        for a_, b_ in zip(rows, rows[1:]):
            for j in range(seg):
                k = (j + 1) % seg
                bm.faces.new((a_[j], a_[k], b_[k], b_[j]))
        for j in range(seg):
            bm.faces.new((rows[-1][j], rows[-1][(j + 1) % seg], pole))
        bm.faces.new(list(reversed(rows[0])))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return mesh_object("dome", build, mat, "body", 0.0, smooth=True)


def shell(c, ax, half, r, mat, cap_seg=24):
    """A tank lying along ax: a cylinder with dished ends."""
    ax = Vector((ax[0], ax[1], 0)).normalized()
    SHELLS.append(rod(c + ax * half, c - ax * half, r, r, mat, seg=36))
    for sgn in (-1, 1):
        SHELLS.append(dome(c + ax * sgn * half, ax * sgn, r, r * 0.55, mat, seg=cap_seg))


SHELLS = []
# the south-west reservoir (B2's tank, "reservoir (pump inside)"): lying east-west on the roof, on
# two saddles, strapped; its filler, level switch and breather (the absorbed pump cabinet's) on top
TK_R, TK_H = 0.10, 0.09
TK = Vector((-1.26, -1.80, RT + 0.04 + TK_R))
for xx_ in (TK.x - 0.07, TK.x + 0.07):
    box((xx_, TK.y, RT + 0.02), (0.05, 0.2, 0.04), "steel", bevel=0.004)                       # saddle
    ring((xx_, TK.y, TK.z), TK_R + 0.012, TK_R - 0.002, 0.03, "steel", verts=40, rot=(0, math.pi / 2, 0),
         bevel=0.0)                                                                             # its strap
shell(TK, (1, 0), TK_H, TK_R, "oxide")
cyl((TK.x + 0.05, TK.y + 0.02, TK.z + TK_R + 0.015), 0.03, 0.04, "brass", verts=16, bevel=0.004)     # filler
cyl((TK.x - 0.05, TK.y - 0.03, TK.z + TK_R + 0.02), 0.024, 0.05, "steel", verts=12, bevel=0.003)     # level switch
cyl((TK.x, TK.y + 0.05, TK.z + TK_R + 0.03), 0.03, 0.06, "steel", verts=16, bevel=0.004)             # breather
cyl((TK.x, TK.y + 0.05, TK.z + TK_R + 0.07), 0.045, 0.02, "steel", verts=16, bevel=0.003)
TK_OUT = (TK.x + 0.02, TK.y + TK_R + 0.03, TK.z - 0.03)                                          # its outlet, north
cyl((TK_OUT[0], TK_OUT[1] - 0.015, TK_OUT[2]), 0.02, 0.05, "brass", verts=12, rot=(math.pi / 2, 0, 0), bevel=0.0)
# the south-east bottles (B2's "accumulator bottles"): two lying east-west on the roof's south
# strip, saddled and strapped; a valve on each one's east end, a gauge on the second's
BT = []
BT_R, BT_H = 0.05, 0.11
for yb in (-1.775, -1.875):
    c = Vector((1.25, yb, RT + 0.03 + BT_R))
    shell(c, (1, 0), BT_H, BT_R, "oxide", cap_seg=20)
    cyl(tuple(c + Vector((BT_H + 0.05, 0, 0))), 0.016, 0.04, "brass", verts=12, rot=(0, math.pi / 2, 0), bevel=0.0)
    BT.append(tuple(c + Vector((BT_H + 0.07, 0, 0))))                                            # its valve
for xx_ in (1.19, 1.31):
    box((xx_, -1.825, RT + 0.015), (0.04, 0.22, 0.03), "steel", bevel=0.004)                     # saddle
    for yb in (-1.775, -1.875):
        ring((xx_, yb, RT + 0.03 + BT_R), BT_R + 0.01, BT_R - 0.002, 0.025, "steel", verts=32,
             rot=(0, math.pi / 2, 0), bevel=0.0)                                                 # its strap
cyl((BT[1][0] + 0.03, BT[1][1], BT[1][2] + 0.05), 0.03, 0.012, "brass", verts=16, bevel=0.002)   # the gauge
cyl((BT[1][0] + 0.03, BT[1][1], BT[1][2] + 0.02), 0.008, 0.05, "brass", verts=8, bevel=0.0)
TANK_PARTS = set(SHELLS)

_DG.append(_surface_cache())

# --- hoses
# south-west: supply and return from the manifold, low across the plate to the south ram
hose([P_E1, (-0.95, -1.47, PT + 0.12), (-0.82, -1.53, PT + 0.05), (-0.70, -1.57, PT + 0.05), B_S],
     0.034, "hose", sag=[0.02, 0.0, 0.0, 0.0], rib=0.2)
hose([P_E2, (-0.93, -1.42, PT + 0.10), (-0.75, -1.45, PT + 0.04), (-0.62, -1.48, PT + 0.04), B_S2], 0.022,
     "hose_brown", sag=0.0, rib=0.25)
# to the west ram: out of the north face, north over the plate
hose([W1, (-1.73, -1.25, PT + 0.06), (-1.66, -1.05, PT + 0.05), B_W], 0.034, "hose", sag=[0.02, 0.0, 0.0], rib=0.2)
hose([W2, (-1.62, -1.25, PT + 0.05), (-1.60, -1.06, PT + 0.04), B_W2], 0.022, "hose_brown", sag=0.0, rib=0.25)
# the reservoir's feed: off its outlet north over the roof's inner edge, down the inner face to the
# manifold's top
hose([TK_OUT, (-1.24, -1.62, RT + 0.06), (-1.18, -1.55, RT - 0.1), (-1.16, -1.55, PT + 0.8), (-1.12, -1.58, PT + 0.55),
      (TOP_MF[0], TOP_MF[1], TOP_MF[2] + 0.05)], 0.026, "hose", sag=0.0, rib=0.22)
# south-east: the valve block's hose off the roof's north edge, down the north face to the east ram
hose([VB_N, (VB_N[0], -1.36, RT + 0.03), (1.74, -1.32, 1.6), (1.70, -1.25, 1.0), (1.62, -1.08, PT + 0.05), B_E],
     0.03, "hose_brown", sag=[0.0, 0.02, 0.02, 0.02, 0.0], rib=0.22)
# and the first bottle's to its inlet
hose([BT[0], (1.50, -1.72, RT + 0.06), (1.62, -1.60, RT + 0.06), (VB_S[0], VB_S[1] - 0.03, VB_S[2])], 0.02,
     "hose", sag=0.0, rib=0.25)
# the legs' jacks, each from its gland on the leg
for sx in (-1, 1):
    hose([LEG_GL[sx], JACKS[sx]], 0.022, "hose", sag=0.03, rib=0.25)
# north-west: the accumulator's hoses -- up to the winch's brake cylinder in a slack loop, and low
# across the plate to the north ram
hose([F_BRK, (BRK[0] - 0.12, BRK[1] - 0.02, GUIDE_TOP - 0.2), (BRK[0] - 0.02, BRK[1] - 0.03, GUIDE_TOP - 0.19),
      (BRK[0], BRK[1], GUIDE_TOP - 0.11)], 0.026, "hose", sag=0.03, rib=0.25)
hose([F_NR, (-0.90, 1.70, PT + 0.05), (-0.82, 1.62, PT + 0.04), B_N], 0.03, "hose_brown", sag=0.02, rib=0.22)

# (round 6) the snubbers' hoses: each from a port on its cylinder, slack over the plate, to a
# bulkhead on the nearest bastion
for (xs, ys_, a) in SNUBS:
    sx_, sy_ = (1 if xs > 0 else -1), (1 if ys_ > 0 else -1)
    zp = ZT + 0.2
    if sy_ < 0:
        port = (xs, ys_ - 0.1, zp)
        cyl(port, 0.018, 0.04, "brass", verts=10, rot=(math.pi / 2, 0, 0), bevel=0.0)
        endb = (sx_ * 1.50, HOUSE_N + 0.012, PT + 0.3)
        box((endb[0], HOUSE_N + 0.01, endb[2]), (0.08, 0.02, 0.08), "steel", bevel=0.004)
        mid = [(xs + sx_ * 0.05, ys_ - 0.22, PT + 0.04), (sx_ * 1.38, -1.30, PT + 0.05), (sx_ * 1.49, HOUSE_N + 0.08, PT + 0.2)]
        end = (endb[0], HOUSE_N + 0.03, endb[2])
    else:
        port = (xs + sx_ * 0.1, ys_, zp)
        cyl(port, 0.018, 0.04, "brass", verts=10, rot=(0, math.pi / 2, 0), bevel=0.0)
        tip = SNB[sx_]
        mid = [(xs + sx_ * 0.18, ys_ + 0.08, PT + 0.04), (tip[0] - sx_ * 0.02, tip[1] - 0.18, PT + 0.05)]
        end = tip
    hose([port] + mid + [end], 0.024, "hose" if sy_ < 0 else "hose_brown", sag=0.03, rib=0.24)
    stain(xs + sx_ * 0.05, ys_ - 0.1, 0.06, 0.05, n=3)

_DG[0] = _surface_cache()                                  # the cables lie over the hoses

# --- cables
# south-west: the lamp's supply up out of a gland in the roof beside it
GL_L = (-1.73, -1.45, RT)
cyl((GL_L[0], GL_L[1], RT + 0.012), 0.035, 0.024, "steel", verts=16, bevel=0.003)
bundle([(GL_L[0], GL_L[1], RT + 0.03), (-1.70, -1.52, RT + 0.05), (LAMP[0] - 0.06, LAMP[1] + 0.0, LAMP[2] + 0.03)],
       ("c_green", "c_red"), sag=0.0, glands=(True, True))
# and the manifold's solenoid, from a gland on the north face
GL_M = face_pt(*SW_N, 0.2, PT + 0.45)
box((GL_M[0], GL_M[1] + 0.012, GL_M[2]), (0.07, 0.024, 0.08), "jbox", bevel=0.005)
bundle([(GL_M[0], GL_M[1] + 0.03, GL_M[2]), (-1.30, -1.33, PT + 0.3), (-1.16, -1.43, PT + 0.42),
        face_pt(*SW_D, 0.32, PT + 0.38, 0.03, 0.07)], ("c_yellow", "c_black"), sag=0.02, glands=(True, False))
# south-east: the switchgear's bundle up out of its gland into the wall box, and on out of the box's
# top over the roof's edge to the valve block's solenoid
bundle([(GL_SE[0], ys_se - 0.03, GL_SE[2] + 0.05), (GL_SE[0], ys_se - 0.032, JB_SE[2] - 0.2),
        (JB_SE[0], ys_se - 0.032, JB_SE[2] - 0.095)], ("c_blue", "c_black", "c_red"), sag=0.0, ties=0.12)
bundle([(JB_SE[0] + 0.02, ys_se - 0.032, JB_SE[2] + 0.095), (1.37, ys_se - 0.032, HOUSE_TOP - 0.08),
        (1.47, ys_se - 0.035, RT + 0.05), (1.52, -1.82, RT + 0.05), (1.56, -1.66, RT + 0.05), (1.66, -1.52, RT + 0.05),
        (VB[0] - 0.03, VB[1] - 0.02, VB[2] + 0.14)], ("c_red", "c_blue", "c_green", "c_black", "c_yellow"), r=0.01,
       sag=0.0, ties=0.12)
for zc in (PT + 0.95, PT + 1.1):                              # its clips on the face
    box((1.37, ys_se - 0.008, zc), (0.05, 0.016, 0.02), "steel", bevel=0.002)
# north: from each roof box, over the roof's front edge, hanging down into the house's open front to
# the winch's motor
for (x, y, out) in WINCHES:
    jb = JB_N[out]
    mx_ = x + out * math.sqrt((GEAR_R + 0.07) ** 2 - 0.17 ** 2)
    bundle([(jb[0], jb[1] - 0.065, jb[2] + 0.06), (jb[0] + out * 0.02, FY - 0.04, HR + 0.08),
            (mx_, FY - 0.15, HR - 0.15), (mx_, FY - 0.05, WINCH_Z + 0.06), (mx_, y - 0.18, WINCH_Z + 0.05),
            (mx_, y - 0.02, WINCH_Z + 0.04), (mx_, y + 0.12, WINCH_Z - 0.17 + 0.095)],
           ("c_blue", "c_red", "c_black") if out > 0 else ("c_green", "c_black"), sag=[0.0, 0.0, 0.05, 0.0, 0.0, 0.0],
           ties=0.15)
# and over each roof's outer edge, down to a gland on the outer wall
for (x, y, out) in WINCHES:
    jb = JB_N[out]
    box((out * 1.952, 1.27, HR - 0.30), (0.024, 0.09, 0.09), "jbox", bevel=0.005)
    bundle([(jb[0] + out * 0.08, jb[1] + 0.02, jb[2] + 0.06), (out * 1.75, 1.10, HR + 0.08), (out * 1.93, 1.25, HR + 0.08),
            (out * 1.99, 1.27, HR), (out * 1.975, 1.27, HR - 0.255)], ("c_yellow", "c_black", "c_red", "c_blue"),
           sag=0.0, ties=0.13, glands=(True, False))
# the north-west roof's tray, from its box to the fan cowl; the north-east's box to the reservoir's
# level switch, and a copper line from the reservoir over the roof's front edge to the winch's bearing
bundle([(JB_N[-1][0] + 0.06, JB_N[-1][1] + 0.06, JB_N[-1][2] + 0.06), (-1.30, 1.09, HR + 0.14), (-1.30, 1.45, HR + 0.14),
        (COWL[0], COWL[1] - 0.2, HR + 0.13), (COWL[0], COWL[1] - 0.093, HR + 0.1)], ("c_red", "c_blue", "c_black"),
       sag=0.0, ties=0.12)
bundle([(JB_N[1][0] + 0.03, JB_N[1][1] + 0.06, JB_N[1][2] + 0.06), (RES[0] - 0.08, RES[1] - 0.12, HR + 0.09),
        (RES[0] - 0.06, RES[1] - 0.075, RES[2] + 0.11)], ("c_yellow", "c_green"), sag=0.0)
pipe([(RES[0] - 0.15, RES[1], RES[2] + 0.1), (1.25, RES[1], RES[2] + 0.1), (1.25, FY - 0.03, HR + 0.08),
      (1.25, FY - 0.06, HR - 0.2), (1.20, FY + 0.05, WINCH_Z + 0.1), (xe_, ye_ - 0.25, WINCH_Z + 0.055)], 0.009, "copper",
     bend=0.04)
# (round 5) slung between the two gear-houses' roofs, behind the column and high over the ring's
# travel: the winches' interlock cables and the lubricant line -- slack, clipped at each roof's
# inner edge, over the north band (T03i: the roofs' inner edges at 0.90)
_before_sling = set(bpy.data.objects)
for (mat_, yy, r_, sg) in ((("hose", 1.41, 0.022, 0.16), (None, 1.33, 0.0, 0.12)) if "--nosling" not in argv else ()):
    a_, b_ = (-0.95, yy, HR + 0.08), (0.95, yy + 0.03, HR + 0.08)
    for x_ in (-1.0, 1.0):                                  # the clip on each roof's inner edge
        box((x_, yy, HR + 0.075), (0.06, 0.06, 0.03), "steel", bevel=0.004)
    if mat_:
        hose([(-1.25, yy, HR + 0.09), a_, (0.0, yy + 0.02, HR - 0.3), b_, (1.25, yy + 0.04, HR + 0.09)], r_, mat_,
             sag=[0.0, sg, sg, 0.0], rib=0.25, ends=(True, True))
    else:
        bundle([(JB_N[-1][0] + 0.07, JB_N[-1][1] + 0.06, JB_N[-1][2] + 0.06), (-1.20, yy, HR + 0.1), a_,
                (0.0, yy, HR - 0.25), b_, (1.20, yy + 0.03, HR + 0.1), (JB_N[1][0] - 0.07, JB_N[1][1] + 0.06,
                                                                     JB_N[1][2] + 0.06)],
               ("c_black", "c_red", "c_blue", "c_yellow"), sag=[0.0, 0.0, sg, sg, 0.0, 0.0], ties=0.2)
SLUNG = [o for o in bpy.data.objects if o not in _before_sling and o.parent == BODY]   # the proposal swings them
# the north bastions' festoons: from the box on the diagonal down to the floor gland
for out_, (top_, fg_) in FEST.items():
    bundle([top_, (top_[0] + (fg_[0] - top_[0]) * 0.4, top_[1] + (fg_[1] - top_[1]) * 0.4, PT + 0.45), fg_],
           ("c_black", "c_red", "c_yellow") if out_ > 0 else ("c_blue", "c_green"), r=0.012, sag=[0.06, 0.02],
           ties=0.14, glands=(False, True))
for (sx, sy), (top_, foot_) in LEGS.items():
    u_ = (foot_ - top_).normalized()
    side = u_.cross(Vector((0, 0, 1))).normalized() * (0.1 * sx * sy)
    lift = Vector((0, 0, 0.17))
    a_ = top_ + side + lift + u_ * 0.05
    b_ = foot_ + side + lift - u_ * 0.12
    bundle([tuple(a_), tuple(a_.lerp(b_, 0.5)), tuple(b_), tuple(b_ + Vector((0, 0, -0.1)) + u_ * 0.05)],
           ("c_black", "c_yellow") if sy > 0 else ("c_red", "c_black", "c_blue"), r=0.011, sag=0.0, ties=0.12,
           glands=(False, False))
    for t in (0.3, 0.7):
        q = a_.lerp(b_, t)
        box(tuple(q - lift * 0.4), (0.05, 0.05, 0.05), "steel", rot=(0, 0, math.atan2(u_.y, u_.x)), bevel=0.004)

# --- oil, where the hydraulics leak: on the plate at the manifold and the rams, on the south-east roof
stain(-0.98, -1.45, 0.1, 0.07, n=5)
stain(-1.66, -1.02, 0.09, 0.07, n=5)
stain(-0.72, -1.52, 0.04, 0.06, n=3)
stain(1.66, -1.02, 0.06, 0.06, n=3)
stain(1.68, -1.55, 0.06, 0.05, n=3, z=RT)

