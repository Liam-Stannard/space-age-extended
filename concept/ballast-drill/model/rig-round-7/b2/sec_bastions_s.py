# ---------------------------------------------------------------- 1c. (T03i, B2) the plate top's fittings
#
# T03i (task ballast-drill-ports; Liam, 2026-10-28: "Yes, rebuild to it", option B2,
# concept/ballast-drill/plate-concepts/option-b2.svg): the chassis is the plate, flat at PT; the
# batter, its ribs, lip and lifting eyes, the perimeter castings (1d) and the corner housings and
# wings (1e) go. The cabinets merge into four diagonal bastions, one per corner inside the runs'
# bends, each standing on the plate's top from PT; the faces' middles are bare plate. The south
# pair here (the hydraulic pack's south-west, the switchgear's south-east, 2.10 high, cast); the
# north pair, the drive's, carry the gear-houses (3a).
#
# (T03i) one inspection cover, west-south-west, as signed off: on the plate's top now
for (cx, cy, ca) in ((-1.70, -1.0, math.pi / 2),):
    ic = empty("cover", (cx, cy, PT + 0.006), (0, 0, ca))
    box((0, 0, 0), (0.3, 0.22, 0.014), "iron_new", parent=ic, bevel=0.005)
    box((0, 0, -0.002), (0.34, 0.26, 0.01), "iron", parent=ic, bevel=0.004)
    for i in range(4):
        for j in (-1, 1):
            bolt((-0.135 + 0.09 * i, j * 0.11, 0.01), 0.013, 0.01, parent=ic)
    for j in (-1, 1):
        bolt((j * 0.155, 0, 0.01), 0.013, 0.01, parent=ic)
        eye((j * 0.07, 0, 0.004), 0.0, "polish", parent=ic, r=0.022)
    box((0, -0.105, 0.009), (0.24, 0.012, 0.002), "polish", parent=ic, bevel=0.0)

# ---------------------------------------------------------------- 1e. (T03i, B2) the south bastions
#
# B2's plan (plate_concepts.py at 271f85d, option B's sb): from the south face's 0.90 out to the
# gallery's inner line (1.94), the corner cut on the plate's own notch line (|x| + |y| = 3.35, so
# the chamfer face stands on the notch wall's line and nothing overhangs the notch), back along
# y = -1.40 to 1.35 and on the diagonal |x| + |y| = 2.75 to the start. 2.10 high (the housings'
# HOUSE_TOP), in the housings' cast ("house"). The camera sees the south face, the chamfer and the
# roof: the doors, gauge, maker's plate and ribs go there; the hydraulic fittings on the inner
# (diagonal) face low, where the hoses leave across the plate to the rams. The roof cabinet of the
# signed-off south-west housing is absorbed into it (its louvres on the chamfer); the reservoir on
# its roof (5b), the bottles on the south-east's.
HOUSE_TOP = SB_TOP = 2.10
WING_TOP = HOUSE_TOP            # (no wings: names kept for the materials' drips)
HOUSE_N = -1.40
M["house"] = cast_iron("house", lo="#3C3B3D", hi="#5C5B5F", drips=((HOUSE_TOP - 0.03, 0.55), (PT + 0.5, 0.4)),
                       drip=0.8, ore=0.85, dry=0.3, wear=0.85, metal="#B4B6BC")
for _n in M["house"].node_tree.nodes:
    if _n.type == "AMBIENT_OCCLUSION":
        _n.samples = 4
    elif _n.type == "BEVEL":
        _n.samples = 2


def flip(pts, sx):
    return [(sx * x, y) for x, y in pts]


SBY = -1.88                     # T03i: the south face 0.06 back of B2's 1.94, so its ribs, flange, door and
                                # the services on it stay inside the gallery's line (the runs' flanges reach 1.955)
SB_E = [(0.90, SBY), (1.50, SBY), (1.50, -1.85), (1.85, -1.50), (1.94, -1.50), (1.94, -1.40), (1.35, -1.40),
        (0.90, -1.85)]
RT = HOUSE_TOP + 0.04                                     # the roof's cap top
HOUSES = {}
for sx in (-1, 1):
    P = ccw(flip(SB_E, sx))
    stack([(P, PT), (P, HOUSE_TOP)], "house", bevel=0.025, name="bastion")
    # the roof: a cap plate a hair proud of the walls all round, but never past the plate's notch
    # line over the corner (the chamfer: there it is flush), bolted round
    cap = offset_poly(P, 0.02, keep=lambda a, b: not on_notch_line(a, b))
    stack([(cap, HOUSE_TOP), (cap, RT)], "house", bevel=0.01, name="roofcap")
    for (a, b) in zip(P, P[1:] + P[:1]):
        a, b = Vector(a), Vector(b)
        L = (b - a).length
        if L < 0.2:
            continue
        nrm = Vector(((b - a).y, -(b - a).x)).normalized()
        n_b = max(2, int(L / 0.13))
        for k in range(n_b):
            q = a + (b - a) * ((k + 0.5) / n_b) - nrm * 0.045
            bolt((q.x, q.y, RT + 0.004), 0.016, 0.012)
    # its south face: a foot flange on the plate, bolted, and cast ribs at its two ends
    xs0, xs1 = sorted((sx * 0.90, sx * 1.50))
    box(((xs0 + xs1) / 2, SBY - 0.025, PT + 0.04), (xs1 - xs0 - 0.02, 0.05, 0.08), "house", bevel=0.01)
    for k in range(5):
        bolt((xs0 + 0.06 + (xs1 - xs0 - 0.12) * k / 4, SBY - 0.052, PT + 0.045), 0.016, 0.014,
             rot=(math.pi / 2, 0, 0))
    for xr in (sx * 0.95, sx * 1.45):
        box((xr, SBY - 0.0175, (PT + 0.08 + HOUSE_TOP - 0.02) / 2), (0.045, 0.035, HOUSE_TOP - PT - 0.1),
            "iron_worn", bevel=0.008)
    # a cast lip under the roof along the chamfer, and a bolt row down its seam with the south face
    ch = [Vector((sx * 1.50, -1.85)), Vector((sx * 1.85, -1.50))]
    m = (ch[0] + ch[1]) / 2
    nrm = Vector((sx, -1)).normalized()
    box((m.x, m.y, HOUSE_TOP - 0.05), ((ch[1] - ch[0]).length - 0.06, 0.03, 0.06), "iron_worn",
        rot=(0, 0, math.atan2(ch[1].y - ch[0].y, ch[1].x - ch[0].x)), bevel=0.006)
    for k in range(6):
        bolt((sx * 1.50 + sx * 0.012, -1.865, PT + 0.15 + 0.18 * k), 0.013, 0.01, rot=(0, math.pi / 2, 0))
    cx, cy = sx * 1.20, -1.70
    HOUSES[sx] = (cx, cy, SBY)
    if sx > 0:
        eye((1.62, -1.47, RT), 0.0, "steel")


def face_empty(name, a, b, s, z, out=0.0):
    """An empty on the wall face from a to b (plan), s along it from a, at height z, `out` in
    front of it: local x along the face, -y out of it, z up (a south face's frame turned)."""
    a, b = Vector(a), Vector(b)
    t = (b - a).normalized()
    n = Vector((t.y, -t.x))                                  # out of a counter-clockwise outline
    p = a + t * s + n * out
    return empty(name, (p.x, p.y, z), (0, 0, math.atan2(n.x, -n.y)))


# the south-west bastion holds the hydraulic pack: a louvred door on its south face, the pressure
# gauge and the maker's plate on its chamfer, the pump's louvres (the roof cabinet absorbed) high
# on the chamfer, the manifold on its inner face low
ys = SBY
fz = PT + 0.12                                             # the door's sill
dx_ = -1.21
box((dx_, ys - 0.006, fz + 0.3), (0.38, 0.014, 0.56), "iron_new", bevel=0.006)
for k in range(6):
    box((dx_, ys - 0.016, fz + 0.12 + 0.06 * k), (0.28, 0.012, 0.014), "steel", bevel=0.0)
for j in (fz + 0.08, fz + 0.52):                           # hinges, east side
    cyl((dx_ + 0.15, ys - 0.016, j), 0.016, 0.06, "polish", verts=12, bevel=0.0)
box((dx_ - 0.17, ys - 0.02, fz + 0.3), (0.024, 0.016, 0.08), "polish", bevel=0.002)      # its handle
SW_CH = ((-1.85, -1.50), (-1.50, -1.85))                   # the chamfer, counter-clockwise
ge = face_empty("gauge", *SW_CH, 0.17, PT + 0.62)
cyl((0, -0.006, 0), 0.05, 0.012, "steel", verts=20, rot=(math.pi / 2, 0, 0), bevel=0.0, parent=ge)
cyl((0, -0.013, 0), 0.038, 0.003, "polish", verts=20, rot=(math.pi / 2, 0, 0), bevel=0.0, parent=ge)
mp = face_empty("makers", *SW_CH, 0.32, PT + 0.36)
mpi = empty("makers-plate", (0, -0.006, 0), (math.pi / 2, 0, 0), parent=mp)
box((0, 0, 0), (0.16, 0.1, 0.01), "brass", parent=mpi, bevel=0.003)
box((0, 0.015, 0.006), (0.11, 0.018, 0.003), "dark", parent=mpi, bevel=0.0)
box((0, -0.02, 0.006), (0.08, 0.014, 0.003), "dark", parent=mpi, bevel=0.0)
for i in (-1, 1):
    for j in (-1, 1):
        rivet((i * 0.065, j * 0.035, 0.006), 0.008, parent=mpi)
lv = face_empty("louvres", *SW_CH, 0.2475, HOUSE_TOP - 0.3)
box((0, -0.006, 0), (0.34, 0.012, 0.34), "house", parent=lv, bevel=0.004)          # its frame
for k in range(5):
    box((0, -0.016, -0.12 + 0.06 * k), (0.28, 0.012, 0.016), "steel", parent=lv, bevel=0.0)
for i in (-1, 1):
    for j in (-1, 1):
        bolt((i * 0.15, -0.014, j * 0.15), 0.012, 0.009, rot=(math.pi / 2, 0, 0), parent=lv)
LAMP = (-1.60, -1.55, RT)                                  # the status lamp: on its roof (section 5)

# the south-east bastion, the switchgear's: a bolted access panel and a wall junction box on its
# south face, a cable gland low; "50" cast raised on its roof with the weight's mark (5b sets the
# bottles and the valve block beside them)
box((1.12, ys - 0.006, PT + 0.42), (0.26, 0.012, 0.36), "iron_new", bevel=0.004)          # the access panel
for i in (-1, 1):
    for j in (-1, 1):
        bolt((1.12 + i * 0.11, ys - 0.013, PT + 0.42 + j * 0.15), 0.012, 0.01, rot=(math.pi / 2, 0, 0))
GL_SE = (1.33, ys - 0.012, PT + 0.22)                       # a wall gland, low
box((GL_SE[0], GL_SE[1], GL_SE[2]), (0.08, 0.024, 0.09), "iron_new", bevel=0.005)
stencil((1.43, -1.60, RT + 0.002), (0, 0, 0), "###.###/#...#.#/###.#.#/..#.#.#/###.###", 0.024,
        mat="iron_worn", h=0.014)                         # "50", cast raised
stencil((1.62, -1.56, RT + 0.002), (0, 0, 0), ".#./###/###", 0.024, mat="iron_worn", h=0.014)
SE_CH = ((1.50, -1.85), (1.85, -1.50))
for s_ in (0.12, 0.37):                                    # cast ribs on its chamfer, short of the notch's air
    rb = face_empty("rib", *SE_CH, s_, (PT + 0.3 + HOUSE_TOP - 0.1) / 2)
    box((0, -0.012, 0), (0.04, 0.024, HOUSE_TOP - PT - 0.4), "iron_worn", parent=rb, bevel=0.006)

# (the winches' feeds are in 3b, once the winches stand)

