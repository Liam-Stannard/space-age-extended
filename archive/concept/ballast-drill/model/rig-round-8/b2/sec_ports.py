# ---------------------------------------------------------------- 1b. (T03l) the chute ports
#
# T03l (task ballast-drill-ports; Liam, judging T03k: "Close the bays"; chute "Port + drive on
# top"; unused faces "Bolted hatch"; south "Whole face (as drawn)"; the drawing is
# concept/ballast-drill/pipe-concepts/pipe_concepts.py's T03k section): the plate wall runs
# unbroken at PT round every face. In each face's middle a low port goes through it at ground
# level: PORT_HW either side of the face's centre, PORT_H high, its mouth flush with the face, a
# tunnel back to Y_STEP (0.87 deep on N, E and W; 1.11 on the south, whose face is out at SF), the
# plate bridging it. The mouth is framed in bolted steel angle set flush into a rebate; the body
# never turns, so every face has its port, and the three the ore does not leave by are shut by a
# flush bolted hatch (door-<face>: the chute's pass hides its own face's). The tunnel's lining,
# the chute and its drive (section 6) are the chute's, so they turn with it.
PORT_HW, PORT_H, PORT_FR = 0.43, 0.30, 0.04      # the port's clear half-width and height; its frame's width
PORT_CUT = 0.46                       # the tunnel's half-width (the lining, and the chute's nudge, inside it)
PORT_TOP = 0.32                       # the tunnel's roof
REBATE = 0.025                        # the frame's rebate into the face
BAND_HW = 0.70                        # (the old bays' half-width: the plate's seams and the services keep clear of it)
AP = 0.2                              # (the old apron's height: the chute's housings are level with it)
Y_STEP = 1.63                         # the tunnel's back (the old riser's face)
SLOT = 0.45
FACE_DEG = {"N": 0, "E": -90, "S": 180, "W": 90}
FACE_OUT = {"N": E, "E": E, "S": SF, "W": E}
BAYS = {}
port_cutters = []
for face, deg in FACE_DEG.items():
    b = empty(f"bay-{face}", rot=(0, 0, math.radians(deg)))
    BAYS[face] = b
    fo = FACE_OUT[face]
    for (hw, y0, z1) in ((PORT_CUT, Y_STEP, PORT_TOP), (PORT_HW + PORT_FR, fo - REBATE, PORT_H + PORT_FR)):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, (y0 + fo + 0.3) / 2, (z1 - 0.1) / 2))
        c = bpy.context.active_object
        c.scale = (2 * hw, fo + 0.3 - y0, z1 + 0.1)
        c.parent, c.hide_render, c.display_type = b, True, "WIRE"
        port_cutters.append(c)
    # the tunnel's back: a bolted plate (never seen from the camera; it closes the tunnel)
    box((0, Y_STEP + 0.006, PORT_TOP / 2), (2 * PORT_CUT - 0.002, 0.012, PORT_TOP - 0.002), "liner", parent=b,
        bevel=0.003)
    # the frame: two jambs and a lintel of steel angle, in the rebate, flush with the face, bolted
    yf = fo - REBATE / 2 - 0.0005
    for sx in (-1, 1):
        box((sx * (PORT_HW + PORT_FR / 2), yf, (PORT_H + PORT_FR) / 2), (PORT_FR, REBATE - 0.001, PORT_H + PORT_FR - 0.002),
            "steel", parent=b, bevel=0.004)
        for zb in (0.06, 0.18, 0.29):
            bolt((sx * (PORT_HW + PORT_FR / 2), fo + 0.0035, zb), 0.011, 0.008, rot=(math.pi / 2, 0, 0), parent=b)
    box((0, yf, PORT_H + PORT_FR / 2), (2 * PORT_HW - 0.002, REBATE - 0.001, PORT_FR - 0.002), "steel", parent=b,
        bevel=0.004)
    for k in range(5):
        bolt((-0.32 + 0.16 * k, fo + 0.0035, PORT_H + PORT_FR / 2), 0.011, 0.008, rot=(math.pi / 2, 0, 0), parent=b)
    # its sill: a worn steel strip on the ground across the mouth, where the ore leaves
    box((0, fo - 0.03, 0.004), (2 * PORT_HW, 0.06, 0.008), "polish", parent=b, bevel=0.002)
    # the hatch, shut: a flush bolted plate in the frame, two stiffening ribs behind it (unseen),
    # six bolts into the frame's back, a lifting handle
    g = f"door-{face}"
    yh = fo - 0.013
    box((0, yh, PORT_H / 2), (2 * PORT_HW - 0.002, 0.02, PORT_H - 0.002), "iron_new", g, parent=b, bevel=0.004)
    for xx in (-0.15, 0.15):
        box((xx, yh - 0.02, PORT_H / 2), (0.03, 0.02, PORT_H - 0.04), "iron_new", g, parent=b, bevel=0.003)
    for xx in (-0.33, 0.0, 0.33):
        for zz in (0.06, 0.24):
            bolt((xx, fo - 0.0015, zz), 0.015, 0.009, group=g, rot=(math.pi / 2, 0, 0), parent=b)
    for sx in (-1, 1):                                  # the handle's two bosses and its bar
        cyl((sx * 0.07, fo - 0.001, 0.15), 0.014, 0.012, "steel", g, verts=12, rot=(math.pi / 2, 0, 0), parent=b, bevel=0.0)
    box((0, fo + 0.012, 0.15), (0.16, 0.014, 0.014), "polish", g, parent=b, bevel=0.003)
    for sx in (-1, 1):
        box((sx * 0.07, fo + 0.004, 0.15), (0.014, 0.014, 0.014), "polish", g, parent=b, bevel=0.002)
cut(CHASSIS, *port_cutters)

