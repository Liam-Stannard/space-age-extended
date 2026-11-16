# ---------------------------------------------------------------- 3a. the press frame: gear-houses and crown
#
# (The signed-off round 3 to 7 notes, unchanged in what they say of the houses' finish: two
# castings, not twins -- the north-west the original, darker and more worn; the north-east a
# replacement in a newer, brighter coat, a roof hatch, a welded patch -- in red oxide over the
# iron, chipped back to it, rust under the paint; lined inside in pale plate.)
#
# T03i (B2; Liam, 2026-10-28, "North gear-houses on the corner blocks, taller at the back:
# Accept"): each drive cabinet becomes a bastion, B2's nb: from the north face's 0.90 out to the
# gallery's inner line (1.94), its corner cut on the gallery's corner, down the east (west) face to
# 0.81 and back on the diagonal |x| + |y| = 2.75, which faces the column and the camera. It stands
# on the plate from PT to the house's floor. The house is B2's hp over it: a cast floor plate from
# the column's head (GUIDE_TOP) to HB over the bastion and out to the column, on which the winch
# stands as signed off; walls on the bastion's back (north), outer and corner edges, HB to HR; the
# front (south and the diagonal) and the inner side open on the gear under edge lintels; the
# rope down through a bushed hole in the floor. Nothing in the shoe's sweep: the shoe's collar
# passes the diagonal face 0.015 clear between s 0.52 and 1.08 from its outer end, where the face
# is flush (a worn hazard stripe painted on it).
M["house_nw"] = layered("house_nw", "#6A2618", metal="#8E9096", paint_metal=0.12, paint_rough=0.62, wear=0.85,
                        rust=0.45, dust=0.3, grime=0.75, jitter=0.12, rust_tint=("#2E180C", "#6E3C1C"),
                        drips=((HR, 0.6), (HR - 0.3, 0.4)), drip=0.9)
M["house_ne"] = layered("house_ne", "#842E1E", metal="#9A9CA2", paint_metal=0.12, paint_rough=0.58, wear=0.6,
                        rust=0.3, dust=0.3, grime=0.6, jitter=0.1, rust_tint=("#2E180C", "#6E3C1C"),
                        drips=((HR, 0.55),), drip=0.7)
M["oxide"] = layered("oxide", "#7C2C1E", metal="#9A9CA2", paint_metal=0.12, paint_rough=0.6, wear=0.75, rust=0.4,
                     dust=0.35, grime=0.65, jitter=0.12, rust_tint=("#2E180C", "#6E3C1C"))
for _m in (M["house_nw"], M["house_ne"], M["oxide"]):
    for _n in _m.node_tree.nodes:
        if _n.type == "AMBIENT_OCCLUSION":
            _n.samples = 4
        elif _n.type == "BEVEL":
            _n.samples = 2

NB_E = [(1.94, 0.81), (1.94, 1.50), (1.85, 1.50), (1.50, 1.85), (1.50, 1.94), (0.90, 1.94), (0.90, 1.85)]
HP_E = [(1.24, 0.81), (1.94, 0.81), (1.94, 1.50), (1.85, 1.50), (1.50, 1.85), (1.50, 1.94), (0.90, 1.94), (0.90, 1.15)]
WALL_E = [(0.90, 1.94), (1.50, 1.94), (1.50, 1.85), (1.85, 1.50), (1.94, 1.50), (1.94, 0.81)]   # back, corner, outer
EDGE_E = [(1.94, 0.81), (1.24, 0.81), (0.90, 1.15), (0.90, 1.94)]                                # the open edges
FY = 0.81                                  # the house's front edge
SHOE_ZONE = (0.52, 1.08)                   # along the diagonal from its outer end: the collar's sweep


def rod_between(a, b, r, mat, verts=24, group="body", parent=None):
    a, b = Vector(a), Vector(b)
    rot = Vector((0, 0, 1)).rotation_difference(b - a).to_euler()
    return cyl(tuple((a + b) / 2), r, (b - a).length, mat, group, verts=verts, rot=tuple(rot), bevel=0.0,
               parent=parent)


def diag(out):
    """The north bastion's diagonal face: (a, b) counter-clockwise, its length, and s(s_o): the
    distance from a of the point s_o from its outer end (|x| 1.94)."""
    A_out, A_in = (out * 1.94, 0.81), (out * 0.90, 1.85)
    a, b = (A_in, A_out) if out > 0 else (A_out, A_in)
    L = (Vector(b) - Vector(a)).length
    return a, b, L, (lambda s_o: L - s_o) if out > 0 else (lambda s_o: s_o)


CABS = {}
for (x, y, out) in WINCHES:
    hm = "house_ne" if out > 0 else "house_nw"
    NB, HP = ccw(flip(NB_E, out)), ccw(flip(HP_E, out))
    # the bastion, plate to floor, and its foot flange along the diagonal on the plate, bolted
    stack([(NB, PT), (NB, GUIDE_TOP)], hm, bevel=0.02, name="bastion")
    a, b, L, s_at = diag(out)
    for k in range(2):                                      # flange, then its bolts
        fe = face_empty("foot", a, b, L / 2, PT + 0.04)
        box((0, -0.03, 0), (L - 0.14, 0.06, 0.08), "iron", parent=fe, bevel=0.01)
        for i in range(9):
            bolt((-(L - 0.3) / 2 + (L - 0.3) * i / 8, -0.062, 0.005), 0.016, 0.014, rot=(math.pi / 2, 0, 0), parent=fe)
        break
    # cast ribs at the diagonal's ends, out of the shoe's sweep
    for s_o in (0.10, 1.30):
        rb = face_empty("rib", a, b, s_at(s_o), (PT + 0.08 + GUIDE_TOP) / 2)
        box((0, -0.0175, 0), (0.045, 0.035, GUIDE_TOP - PT - 0.1), "iron_worn", parent=rb, bevel=0.008)
    # its louvred door (the drive's, the starter cabinet merged), hinges, handle
    dr = face_empty("door", a, b, s_at(0.36), PT + 0.12)
    box((0, -0.006, 0.4), (0.24, 0.014, 0.8), "liner", parent=dr, bevel=0.006)
    for k in range(8):
        box((0, -0.016, 0.1 + 0.07 * k), (0.17, 0.012, 0.014), "steel", parent=dr, bevel=0.0)
    for zz in (0.06, 0.74):
        cyl((-out * 0.125, -0.016, zz), 0.014, 0.06, "polish", verts=10, bevel=0.0, parent=dr)
    box((out * 0.09, -0.02, 0.42), (0.02, 0.014, 0.08), "polish", parent=dr, bevel=0.002)
    # the hatch north of the sweep, bolted
    ht = face_empty("hatch", a, b, s_at(1.25), PT + 0.65)
    box((0, -0.006, 0), (0.22, 0.014, 0.46), "liner", parent=ht, bevel=0.005)
    for i in (-1, 1):
        for j in (-1, 1):
            bolt((i * 0.09, -0.014, j * 0.2), 0.011, 0.009, rot=(math.pi / 2, 0, 0), parent=ht)
    # the shoe's sweep: flush, a worn hazard stripe painted on it
    hz = face_empty("stripe", a, b, s_at(0.80), 1.86)
    stencil((-0.22, -0.0016, 0), (math.pi / 2, 0, 0), "#..#..#..#./.#..#..#..#/..#..#..#..", 0.04, parent=hz,
            mat="stencil_worn")
    if out > 0:
        # the replacement's welded patch, off-square, its bead round it
        pz = face_empty("patch", a, b, s_at(1.22), PT + 0.22)
        pe = empty("patch-plate", (0, -0.006, 0), (math.pi / 2, math.radians(4), 0), parent=pz)
        box((0, 0, 0), (0.2, 0.15, 0.012), "iron_new", parent=pe, bevel=0.003)
        for (px_, py_, sx_, sy_) in ((0, 0.08, 0.22, 0.01), (0, -0.08, 0.22, 0.01), (0.105, 0, 0.01, 0.17),
                                     (-0.105, 0, 0.01, 0.17)):
            box((px_, py_, 0.004), (sx_, sy_, 0.01), "seam", parent=pe, bevel=0.003)
    CABS[out] = (a, b, L, s_at)

    # the house's floor: from the column's head over the bastion, the winch's platform; the rope's
    # bushed hole through it
    fl = stack([(HP, GUIDE_TOP), (HP, HB)], "iron", bevel=0.012, name="housefloor")
    rx_, ry_ = x + out * DRUM_R, y + 0.13
    cut(fl, cutter_cyl((rx_, ry_, (GUIDE_TOP + HB) / 2), 0.045, 0.4, verts=24))
    ring((rx_, ry_, HB + 0.006), 0.07, 0.045, 0.012, "polish", verts=24, bevel=0.002)
    # walls on the back, corner and outer edges, lined inside
    W = wall_outline(flip(WALL_E, out), 0.05, (x, y))
    stack([(W, HB), (W, HR)], hm, bevel=0.01, name="housewall")
    W2 = wall_outline(offset_chain(flip(WALL_E, out), 0.05, (x, y)), 0.012, (x, y))
    stack([(W2, HB + 0.001), (W2, HR - 0.03)], "liner_pale", bevel=0.003, name="houseliner")
    # the open edges' lintel, the front post on the bastion's corner
    LN = wall_outline(flip(EDGE_E, out), 0.07, (x, y))
    stack([(LN, HR - 0.1), (LN, HR)], "iron_worn", bevel=0.008, name="lintel")
    box((out * 1.90, FY + 0.04, (HB + HR) / 2), (0.08, 0.08, HR - HB), "iron_worn", bevel=0.01)
    # the roof: a cast cover a hair proud all round, rolled edges front and back, riveted round
    RF = offset_poly(HP, 0.03)
    stack([(RF, HR), (RF, HR + 0.06)], hm, bevel=0.03, name="roof")
    rod_between((out * 1.25, FY - 0.03, HR), (out * 1.97, FY - 0.03, HR), 0.05, hm)
    rod_between((out * 0.87, 1.97, HR), (out * 1.50, 1.97, HR), 0.05, hm)
    for (p0, p1) in zip(RF, RF[1:] + RF[:1]):
        p0, p1 = Vector(p0), Vector(p1)
        Lr = (p1 - p0).length
        if Lr < 0.15:
            continue
        nrm = Vector(((p1 - p0).y, -(p1 - p0).x)).normalized()
        n_r = int(Lr / 0.074)
        for k in range(n_r):
            q = p0 + (p1 - p0) * ((k + 0.5) / n_r) - nrm * 0.05
            rivet((q.x, q.y, HR + 0.062), 0.012)
    for zz_ in [HB + 0.08 + 0.09 * k for k in range(7)]:          # down the outer wall's front edge
        rivet((out * 1.945, FY + 0.03, zz_), 0.012)
    if out > 0:
        # the replacement's roof hatch, bolted, a little skew, its lifting eye
        hz_ = empty("roofhatch", (out * 1.20, 1.40, HR + 0.068), (0, 0, math.radians(2.5)))
        box((0, 0, 0), (0.42, 0.32, 0.016), "iron_new", parent=hz_, bevel=0.005)
        for i in range(5):
            for j in (-1, 1):
                bolt((-0.18 + 0.09 * i, j * 0.14, 0.012), 0.013, 0.01, parent=hz_)
        eye((0.1, 0, 0.008), 0.0, "polish", parent=hz_, r=0.024)

# ---------------------------------------------------------------- 3b. the winches' feeds
#
# (T03i: the starter cabinets and their conduits merged into the bastions.) The lubricator on the
# house's floor, its grease lines up to the winch's two bearings.
for (x, y, out) in WINCHES:
    lx, ly = out * 1.62, 0.95
    box((lx, ly, HB + 0.06), (0.1, 0.1, 0.12), "iron_new", bevel=0.01)
    cyl((lx, ly, HB + 0.15), 0.035, 0.06, "brass", verts=16, bevel=0.005)
    cyl((lx, ly, HB + 0.19), 0.02, 0.02, "brass", verts=12, bevel=0.003)
    zg = WINCH_Z + 0.03
    for by2 in (y - 0.25, y + 0.32):
        pipe([(lx, ly, HB + 0.12), (lx, ly, zg), (lx, by2, zg), (x - out * 0.045, by2, zg)], 0.008, "copper",
             bend=0.04)
    box((lx, ly, (HB + zg) / 2 + 0.06), (0.03, 0.03, 0.03), "steel", bevel=0.003)          # a clip on the riser
    cyl((lx, ly - 0.06, HB + 0.0015), 0.07, 0.003, "grease", verts=20, bevel=0.0)           # its drips

