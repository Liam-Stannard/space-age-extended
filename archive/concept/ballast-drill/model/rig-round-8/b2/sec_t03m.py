
# ---------------------------------------------------------------- 5c. (T03m) the plate top's detail
#
# T03m (Liam, judging T03l: "Plate top: detail needs to be added"): the plate's top, flat cast iron
# since T03i, gets what a working casting collects: bolted replacement patches, a cast joint with its
# bolt rows, the bolt rows of the bridge over each chute port's tunnel, a chequer tread on the south
# apron, scuffed bare iron and oil. Everything clear of every direction's C2 hose, gooseneck and end
# boss (their plan from c2.py), of each face's chute drive (it stands on the plate in its direction),
# the rams and their hoses, the snubbers, the guide feet and the inspection cover: each place checked
# in plan (scratchpad occ.py / details.py: 0.04 or more from any of them).
T03M_RNG = random.Random(3_03_13)


def t03m_patch(cx, cy, hx, hy, deg, mat="iron_new"):
    """A bolted replacement plate on the plate's top: a thin plate, bevelled, its bolts round the edge."""
    pe = empty("t03m-patch", (cx, cy, PT + 0.006), (0, 0, math.radians(deg)))
    box((0, 0, 0), (2 * hx, 2 * hy, 0.012), mat, parent=pe, bevel=0.004)
    nx, ny = max(2, round(2 * hx / 0.085)), max(2, round(2 * hy / 0.085))
    for i in range(nx + 1):
        for j in (-1, 1):
            bolt((-hx + 0.025 + (2 * hx - 0.05) * i / nx, j * (hy - 0.025), 0.009), 0.011, 0.008, parent=pe)
    for j in range(1, ny):
        for i in (-1, 1):
            bolt((i * (hx - 0.025), -hy + 0.025 + (2 * hy - 0.05) * j / ny, 0.009), 0.011, 0.008, parent=pe)
    return pe


def t03m_seam(a, b):
    """A cast joint across the plate's top: a weld bead, a bolt row 0.04 either side, staggered."""
    a, b = Vector(a), Vector(b)
    t = (b - a).normalized()
    n = Vector((-t.y, t.x))
    weld((a.x, a.y, PT + 0.002), (b.x, b.y, PT + 0.002), r=0.008)
    L = (b - a).length
    k = 0
    s = 0.03
    while s < L - 0.02:
        side = 1 if k % 2 else -1
        q = a + t * s + n * side * 0.04
        bolt((q.x, q.y, PT + 0.007), 0.013, 0.011)
        s += 0.045
        k += 1


def t03m_wear(cx, cy, rx, ry, deg, n=4, mat="iron_worn"):
    """Bare iron scuffed through the plate's dust and rust: a few overlapping thin worn blots."""
    for k in range(n):
        ox, oy = T03M_RNG.uniform(-rx, rx) * 0.5, T03M_RNG.uniform(-ry, ry) * 0.5
        o = cyl((cx + ox, cy + oy, PT + 0.0007 + 0.0002 * k), 1.0, 0.0010, mat, verts=24, bevel=0.0)
        o.scale = (rx * T03M_RNG.uniform(0.5, 0.9), ry * T03M_RNG.uniform(0.5, 0.9), 1)
        o.rotation_euler.z = math.radians(deg) + T03M_RNG.uniform(-0.3, 0.3)


# the patches: one on the east strip, one inboard of it (the west strip has the T03i panel, moved there)
t03m_patch(2.17, -0.28, 0.13, 0.15, -3.0, mat="iron")
t03m_patch(1.73, -0.17, 0.10, 0.13, 8.0)
# the south apron's chequer tread, where the crew stand at the south hatch: a steel plate, raised
# diamonds on it in a herringbone, bolted round
tp = t03m_patch(0.0, -1.76, 0.20, 0.11, 0.0, mat="steel")
for i in range(-5, 6):
    for j in range(-2, 3):
        a_ = 45 if (i + j) % 2 else -45
        box((i * 0.03, j * 0.03, 0.0075), (0.02, 0.006, 0.003), "polish", parent=tp, rot=(0, 0, math.radians(a_)), bevel=0.0)
# the cast joints: down the east strip, and across the south apron
t03m_seam((1.97, -0.46), (1.97, 0.06))
t03m_seam((-0.37, -1.97), (0.37, -1.97))
# the bridge over each chute port's tunnel: a bolt row on the plate's top, on the drive's other side
for deg_ in (0, -90, 180, 90):
    for k in range(6):
        q = Vector((0.06 + 0.075 * k, 2.40))
        q.rotate(Matrix.Rotation(math.radians(deg_), 2))
        bolt((q.x, q.y, PT + 0.007), 0.015, 0.012)
# wear and oil
t03m_wear(-0.13, -2.25, 0.09, 0.05, 10.0)
t03m_wear(-2.30, -0.80, 0.05, 0.09, 0.0)
t03m_wear(-1.60, -0.05, 0.07, 0.05, 30.0)
stain(2.30, -0.80, 0.05, 0.08, n=3)
