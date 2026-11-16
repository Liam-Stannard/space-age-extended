"""Where the rig's ends are, per direction, without Blender: for take_sheet.py's clipping crops.
The numbers are rig_parts.py's and ballast_drill.py's (V_AXIS_U, H_AXIS_V, ZA); keep them in step.
"""
import math

R_AX, ARC_C, ZA = 2.24, 1.5, 0.42
V_AXIS_U, H_AXIS_V = 0.5 / 64, 1.0 / 64
FIT_CONNS = [(-2, -1, "W"), (2, -1, "E"), (1, 2, "S"), (-1, 2, "S")]
DIRS = ("north", "east", "south", "west")
NORMAL = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}


def conns(d):
    out = []
    for x, y, f in FIT_CONNS:
        for _ in range(DIRS.index(d)):
            x, y, f = -y, x, "NESW"[("NESW".index(f) + 1) % 4]
        out.append((x, y, f))
    return out


def junction(x, y, f):
    if f in "NS":
        return (x + V_AXIS_U, R_AX if f == "N" else -R_AX)
    return (R_AX if f == "E" else -R_AX, -y + H_AXIS_V - ZA / 2)


def end_ring(x, y, f):
    jx, jy = junction(x, y, f)
    if f == "S":
        return (jx, -2.53 - ZA / 2)
    if f == "N":
        return (jx, 2.47)
    return ((2.47 if f == "E" else -2.47), jy)


def ends(z_head=0.96, z_apex=0.96):       # T03h: the run axis 0.96 (was 0.92)
    """{direction: [(name, (x, y, z)), ...]}: the middle of each junction (its head and its end
    ring), and the middle of each corner the runs turn, in model coordinates (y north)."""
    out = {}
    for d in DIRS:
        cs = conns(d)
        items = []
        for c in cs:
            jx, jy = junction(*c)
            ex, ey = end_ring(*c)
            # the point whose screen position is midway between the head and the end ring
            sx = (jx + ex) / 2
            sy_screen = ((-jy - z_head / 2) + (-ey - ZA / 2)) / 2
            items.append((f"run end at {c[2]}({c[0]},{c[1]})", (sx, -sy_screen, 0.0)))
        for a, b in ((cs[0], cs[3]), (cs[1], cs[2])):
            na, nb = NORMAL[a[2]], NORMAL[b[2]]
            cx, cy = na[0] + nb[0], na[1] + nb[1]
            k = (R_AX - ARC_C) / math.sqrt(2)
            items.append((f"corner {'N' if cy > 0 else 'S'}{'E' if cx > 0 else 'W'}",
                          (cx * (ARC_C + k), cy * (ARC_C + k), z_apex)))
        out[d] = items
    return out
