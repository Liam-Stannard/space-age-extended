# T03l (Liam: "Port + drive on top"): the chute now lies in its face's port, a tunnel through the
# plate (1b), its mouth flush with the face. The tunnel's lining is the chute's, so it turns with
# it and fills the open port on the screen wherever the chute does not (the base draws every
# port shut by its hatch): a floor plate the chute stands on, the two side walls and the roof,
# bolted, from the tunnel's back to the mouth. Over the mouth, on the plate's top, the chute's
# drive (pipe_concepts.py drive_pts: west of the chute's axis, 0.06 back from the face, 0.30 x
# 0.28, 0.18 high): a gearbox in the chute drive's copper on a bolted base plate, its output
# shaft's bearing cap on top, so the output face reads from the camera in every direction. On
# the south face (out at SF) the chute, its lining and drive stand CHUTE_OUT further out: the
# tunnel 0.24 longer, as drawn.
CHUTE_OUT = {"north": 0.0, "east": 0.0, "south": round(SF - E, 3), "west": 0.0, "": 0.0}
TL_W = PORT_CUT - 0.016                # the lining's half-width: inside the tunnel by the chute's nudge and a hair
box((0, (Y_STEP + 0.02 + CY1) / 2, 0.015), (2 * TL_W, CY1 - Y_STEP - 0.02, 0.03), "liner", "chute", parent=CHUTE,
    bevel=0.003)                                                                      # the floor, on the ground
for sx in (-1, 1):
    box((sx * (TL_W - 0.005), (Y_STEP + 0.02 + CY1) / 2, (0.03 + PORT_TOP - 0.004) / 2),
        (0.01, CY1 - Y_STEP - 0.02, PORT_TOP - 0.034), "liner", "chute", parent=CHUTE, bevel=0.002)   # the walls
    for k in range(4):
        bolt((sx * (TL_W - 0.011), Y_STEP + 0.12 + (CY1 - Y_STEP - 0.2) * k / 3, 0.17), 0.012, 0.008, group="chute",
             rot=(0, math.pi / 2, 0), parent=CHUTE)
box((0, (Y_STEP + 0.02 + CY1) / 2, PORT_TOP - 0.009), (2 * TL_W, CY1 - Y_STEP - 0.02, 0.01), "liner", "chute",
    parent=CHUTE, bevel=0.002)                                                        # the roof, under the lintel
DRV = (-0.19, CY1 - 0.20)
box((DRV[0], DRV[1], PT + 0.0105), (0.36, 0.34, 0.02), "iron_worn", "chute", parent=CHUTE, bevel=0.004)  # base plate
for i in (-1, 1):
    for j in (-1, 1):
        bolt((DRV[0] + i * 0.155, DRV[1] + j * 0.145, PT + 0.025), 0.013, 0.01, group="chute", parent=CHUTE)
box((DRV[0], DRV[1], PT + 0.02 + 0.07), (0.30, 0.28, 0.14), "copper", "chute", parent=CHUTE, bevel=0.016)  # the gearbox
box((DRV[0], DRV[1], PT + 0.17), (0.31, 0.29, 0.02), "copper", "chute", parent=CHUTE, bevel=0.006)        # its lid
for i in range(4):                                   # the lid's bolts
    for j in (-1, 1):
        bolt((DRV[0] - 0.12 + 0.08 * i, DRV[1] + j * 0.128, PT + 0.183), 0.01, 0.008, group="chute", parent=CHUTE)
for sx in (-1, 1):                                   # cooling ribs down its sides
    for k in range(3):
        box((DRV[0] + sx * 0.153, DRV[1] - 0.08 + 0.08 * k, PT + 0.09), (0.012, 0.018, 0.11), "copper", "chute",
            parent=CHUTE, bevel=0.003)
cyl((DRV[0], DRV[1], PT + 0.18 + 0.025), 0.07, 0.05, "steel", "chute", verts=32, parent=CHUTE, bevel=0.006)  # bearing cap
for k in range(6):
    t_ = 2 * math.pi * (k + 0.5) / 6
    bolt((DRV[0] + 0.052 * math.cos(t_), DRV[1] + 0.052 * math.sin(t_), PT + 0.233), 0.008, 0.006, group="chute",
         parent=CHUTE)
cyl((DRV[0], DRV[1], PT + 0.235), 0.022, 0.012, "polish", "chute", verts=16, parent=CHUTE, bevel=0.002)   # the shaft end
cyl((DRV[0] + 0.11, DRV[1] - 0.1, PT + 0.19), 0.012, 0.024, "brass", "chute", verts=10, parent=CHUTE, bevel=0.002)  # breather
DRIVE_BOX = (DRV[0] - 0.18, DRV[0] + 0.18, DRV[1] - 0.17, DRV[1] + 0.17, PT, PT + 0.26)   # its extent, chute's frame
