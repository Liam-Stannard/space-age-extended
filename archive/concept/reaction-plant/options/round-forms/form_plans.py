"""T06g: the three building forms -- where each unit of the Circulator's vessel set stands, the building it belongs
to, and the runs between them (model space, tiles; x east, y north, z up; the footprint +-2.5). forms.py builds
the form named by RP_FORM. Fixed by Liam (2026-10-20): the solution's connection on the north face at x -1, the
gas's at x +1, the output on the south face at x 0, turning with the building.

Liam, 2026-10-21, on T06e's takes: "The pipe connections still don't look right, it would help if it looked more
like a building than some tanks on the ground"; form: "Artist proposes 3 forms"; connections: "Should enter the
building's wall", "Fittings look wrong"; tone: "Raise the sun ~4 %"; added kit: "Keep it".

Keys beyond T06e's (takes.py): building (forms.py building()), walls (connection -> its wall face's distance from
the centre: the fitting is a sleeve on that wall), lift (unit -> dz: built as on the ground, set on the roof or
deck), lifted_clutter, skip (units not built), recv_yz / recv_skid_s (the receiver's axis and skid), valve_z,
instr_h. A run built inside a lifted unit (its own hose) is given as on the ground; every other run is absolute.
"""
import math

PI = math.pi

TAKES = {}

# ------------------------------------------------------------------------------------------------ 1, casing
# 1, "the casing": one riveted housing 0.85 tall over the whole footprint, the outline broken at the two
# front corners by the units that stand on the ground in them (the filter press south-west, the pump house
# south-east). The tall vessels stand up through its roof in bolted collars (the reactor, both legs, the
# condenser, the settling pot); the users of the connections stand on the roof straight over the sleeves
# their connections enter the wall by: the feed drum over the solution's (x -1), the compressor's suction
# bottle on its legs over the gas's (x +1), the receiver over the output's (x 0), each joined to the roof by a
# riser with a visible reducer. The roof carries the rest of the kit (dosing pump, make-up pot, cabinet,
# instrument house, barrels).
ZC = 0.85
# each connection's fitting stands in a recess 0.12 deep in its wall (RECESS), so its sleeve shows its length in
# every direction (a sleeve on a wall 0.2 in from the footprint's edge was a stub facing east or west)
_P1 = [(-1.2, -2.3), (-0.58, -2.3), (-0.58, -2.18), (0.58, -2.18), (0.58, -2.3), (1.5, -2.3), (1.5, -1.5),
       (2.4, -1.5), (2.4, 2.1), (2.2, 2.3), (1.58, 2.3), (1.58, 2.18), (0.42, 2.18), (0.42, 2.3), (-0.42, 2.3),
       (-0.42, 2.18), (-1.58, 2.18), (-1.58, 2.3), (-2.2, 2.3), (-2.4, 2.1), (-2.4, -1.4), (-1.2, -1.4)]
TAKES["casing"] = dict(
    pitch="the casing",
    pitch_lines=[
        "One riveted housing, 0.85 tall, over the whole footprint: the vessels stand up through its roof in bolted collars, the rest of the kit",
        "stands on it, and the two front corners are broken by the units on the ground in them (the filter press, the pump house).",
        "Each connection enters the housing's wall through a flanged sleeve on a bolted boss; its user stands on the roof straight over it, joined",
        "by a riser with a visible reducer: feed drum over the solution's, the compressor's bottle (on legs) over the gas's, receiver over the output's.",
    ],
    building=dict(
        casings=[dict(pts=_P1, z=ZC, dress={
            0: dict(louvres=((0.42, 0.36, 0.3),)),
            4: dict(doors=((0.67, 0.3),)),
            5: dict(louvres=((0.5, 0.3, 0.3),)),
            7: dict(louvres=((0.3, 0.5, 0.34), (0.75, 0.42, 0.34)), stencils=((0.52, 0.4, 0.1, 0.62),)),
            13: dict(stencils=((0.5, 0.36, 0.1, 0.62),)),
            19: dict(doors=((0.62, 0.32),), louvres=((0.25, 0.4, 0.3),)),
            20: dict(louvres=((0.62, 0.36, 0.28),)),
        })],
        clear=[(-1.0, 2.18), (1.0, 2.18), (0.0, -2.18), (2.4, -0.95), (-2.4, 0.6), (0.85, -2.3), (0.0, 2.3)],
        collars=[(-0.1, 0.2, 0.9, ZC), (1.2, -0.72, 0.3, ZC), (-1.2, -0.72, 0.3, ZC), (-1.88, 1.7, 0.5, ZC),
                 (1.95, -0.3, 0.4, ZC), (-1.9, 0.2, 0.44, ZC)],
        hatches=[(-0.75, 1.0, ZC, 0.3, 0.3)],
        # each connection's riser: (x, y, z0, z1, r, rin, mark)
        risers=[(-1.0, 1.68, ZC, 0.8 + ZC - 0.47, 0.2, 0.27, "green"),
                (1.0, 1.75, ZC, ZC + 0.26 - 0.1, 0.2, 0.27, "yellow"),
                (0.0, -1.75, ZC, 0.72 + ZC - 0.39, 0.2, 0.27, "green")],
    ),
    walls={0: 2.18, 1: 2.18, 2: 2.18},
    lift={"feed_drum": ZC, "compressor": ZC, "receiver": ZC, "dosing": ZC, "makeup": ZC, "cabinet": ZC,
          "instrument_house": ZC},
    skip=("manifold", "exchanger"),
    reactor=(-0.1, 0.2),
    legs=[(1.2, -0.72), (-1.2, -0.72)],
    valve=(0.0, -0.95),
    valve_z=ZC,
    drum=dict(kind="ew", x0=-1.2, x1=-0.25, y=1.68, r=0.47, z=0.8, bands=(-0.62,), saddles=(-1.08, -0.4),
              welds=(-0.8,)),
    compressor=dict(kind="v", bottle=(1.0, 1.75), dir=1, skid_w=0.66, motor=0.42, raised=0.26),
    scrubber=(-1.88, 1.7),
    condenser=(1.95, -0.3),
    pot=None,
    makeup=(1.85, -1.1),
    drip_floor=ZC,
    dosing=(-0.65, -1.0),
    settle=(-1.9, 0.2),
    press=(-1.95, -1.985),
    dropbox_w=(0.535, 0.53),
    receiver=(-0.75, 0.8),
    recv_yz=(-1.75, 0.72),
    recv_skid_s=-2.12,
    recv_skid_n=-1.36,
    pumphouse=(2.055, -2.025),
    cabinet=(1.2, -1.82),
    manifold=None,
    exchanger=None,
    drain=None,
    instr=[(2.0, 0.2), (2.27, 0.2), (2.27, 1.0), (2.0, 1.0)],
    instr_h=0.8,
    sockets={
        "north": ((0.85, -2.328, 0.5), (0, -1, 0), "the housing's south wall"),
        "east": ((2.428, -0.95, 0.5), (1, 0, 0), "the housing's east wall"),
        "south": ((0.0, 2.328, 0.5), (0, 1, 0), "the housing's north wall"),
        "west": ((-2.428, 0.6, 0.5), (-1, 0, 0), "the housing's west wall"),
    },
    runs=dict(
        loop1=[(1.2, -0.72, 2.87), (1.1, -0.6, 3.05), (0.8, -0.42, 2.95), (0.62, -0.31, 2.74)],
        loop2=[(-1.2, -0.72, 2.87), (-1.1, -0.62, 3.0), (-0.92, -0.48, 2.6), (-0.78, -0.37, 2.42)],
        gas=[(1.6, 1.3, 2.0), (1.45, 0.5, 1.95), (1.36, -0.15, 1.8), (1.24, -0.46, 1.6)],
        feed=[(-1.05, 1.35, 1.32), (-1.17, 0.75, 1.05), (-1.25, 0.0, 1.0), (-1.2, -0.45, 1.0)],
        dosing=[(-0.6, -0.9, 0.7), (-0.97, -0.85, 0.35)],
        makeup=[(1.7, -0.95, 1.35), (1.58, -0.92, 0.9), (1.6, -0.94, 0.6), (1.435, -0.855, 0.6)],
        scrub=[(-1.6, 1.4, 2.85), (-1.1, 0.6, 3.45), (-0.75, 0.1, 3.5), (-0.6, -0.1, 3.3)],
        vent=[(1.57, -0.21, 1.1), (1.1, -0.1, 1.1), (0.78, -0.02, 1.1)],
        settle=[(-1.65, 0.05, 1.95), (-1.42, -0.55, 1.7)],
        slurry=[(-1.95, -0.26, 1.15), (-1.95, -0.9, 1.25), (-1.7, -1.25, 1.2), (-1.615, -1.42, 1.0),
                (-1.615, -1.53, 1.0)],
        filtrate=[(-1.585, -1.985, 1.33), (-1.585, -1.95, 1.6), (-1.2, -1.82, 1.95), (-0.68, -1.75, 2.03)],
        pump=[(1.62, -1.85, 1.5), (1.4, -1.45, ZC + 0.02)],
        cable=[(1.2, -1.75, 0.95), (1.05, -1.55, 0.7), (1.0, -1.45, 0.02)],
        bundle_e=[(2.13, 0.2, 0.4), (2.13, 0.12, 0.2), (2.13, 0.05, 0.02)],
    ),
    lifted_clutter=[(ZC, [
        ("barrels", 0.45, -1.1, 2, 3),
        ("barrels", -2.18, -1.15, 1, 4),
        ("jbox", 0.45, 1.35, 0.3, 0.22, 0.35),
        ("jbox", -1.95, 0.95, 0.35, 0.3, 0.45),
    ])],
    clutter=[],
    stains=[(2.0, -2.38, 0.4, 0.12, 0.1), (-1.85, -2.38, 0.4, 0.1, -0.05)],
    chain=["solution", "wall sleeve", "riser", "feed drum", "downcomer foot", "riser (gas lift)", "reactor",
           "downcomer", "settling pot", "filter press", "receiver", "output"],
    # from --probe (frame 0 of each layer alone, px over half alpha at 4x; under 40 is not a motion anyone sees)
    unseen={"north": (), "east": ("coupling-dosing",), "south": ("coupling-dosing", "gauge-reactor-upper", "gauge-reactor-lower", "gauge-scrubber", "drip"), "west": ("coupling-compressor", "coupling-pump", "gauge-reactor-upper", "gauge-reactor-lower", "gauge-scrubber", "drip")},
)

# ------------------------------------------------------------------------------------------------ 2, frame
# 2, "the frame": a two-storey steel structure. At the back, a plated room under a deck (1.15 up) the width of
# the building: the two inputs enter its north wall through their sleeves, and their users stand on the deck
# straight over them -- the feed drum on its saddles over the solution's, the compressor's suction bottle on its
# three legs over the gas's, each with its riser up through the deck. In front, an open bay where the reactor
# and its legs stand on the ground inside a ring of four stanchions and girders (2.3 up) that carries the lines;
# the output enters a plated bulkhead between two posts on the front edge, the receiver standing right behind
# it. The press and the pump house hold the front corners, the settling pot and condenser the west side, the
# scrubber the east; a ladder climbs to the deck.
ZD = 1.15
_U = [(-2.48, 0.9), (-2.33, 0.9), (-2.33, 2.03), (2.33, 2.03), (2.33, 0.9), (2.48, 0.9), (2.48, 2.3), (1.58, 2.3),
      (1.58, 2.18), (0.42, 2.18), (0.42, 2.3), (-0.42, 2.3), (-0.42, 2.18), (-1.58, 2.18), (-1.58, 2.3), (-2.48, 2.3)]
TAKES["frame"] = dict(
    pitch="the frame",
    pitch_lines=[
        "A two-storey steel structure: at the back a plated room under a deck 1.15 up; the inputs enter the room's north wall through flanged",
        "sleeves, and their users stand on the deck straight over them (feed drum over the solution's, the compressor's bottle on its legs over the",
        "gas's), each fed by a riser up through the deck. In front, an open bay: the reactor and legs on the ground inside a ring of stanchions and",
        "girders that carries the lines; the output enters a plated bulkhead on the front edge with the receiver right behind it.",
    ],
    building=dict(
        casings=[
            dict(pts=_U, z=ZD - 0.05, dress={
                10: dict(louvres=((0.5, 0.4, 0.3),)),
                5: dict(louvres=((0.5, 0.36, 0.3),)),
                15: dict(louvres=((0.5, 0.36, 0.3),)),
                2: dict(hazard=False),
            }),
            dict(pts=[(-1.38, -2.35), (-0.58, -2.35), (-0.58, -2.23), (0.58, -2.23), (0.58, -2.35), (1.38, -2.35),
                      (1.38, -2.08), (-1.38, -2.08)], z=0.95, dress={
                0: dict(louvres=((0.45, 0.3, 0.26),)), 4: dict(stencils=((0.62, 0.3, 0.08, 0.6),))}),
        ],
        clear=[(-1.0, 2.18), (1.0, 2.18), (0.0, -2.23), (0.9, -2.35), (0.0, 2.3)],
        columns=[(-2.32, 0.98, ZD - 0.08), (2.32, 0.98, ZD - 0.08), (-1.8, 0.98, 2.3), (1.8, 0.98, 2.3),
                 (-1.8, -1.3, 2.3), (1.8, -1.3, 2.3), (-1.47, -2.27, 1.0), (1.47, -2.27, 1.0)],
        beams=[((-2.48, 0.95), (2.48, 0.95), ZD - 0.05), ((-1.8, -1.3), (1.8, -1.3), 2.3),
               ((-1.8, -1.3), (-1.8, 0.98), 2.3), ((1.8, -1.3), (1.8, 0.98), 2.3), ((-1.8, 0.98), (1.8, 0.98), 2.3),
               ((-1.54, -2.27), (1.54, -2.27), 1.0)],
        struts=[((-1.8, -1.3, 1.75), (-1.8, -0.8, 2.18)), ((1.8, -1.3, 1.75), (1.8, -0.8, 2.18)),
                ((-1.8, -1.3, 1.75), (-1.3, -1.3, 2.18)), ((1.8, -1.3, 1.75), (1.3, -1.3, 2.18)),
                ((-1.8, 0.98, 1.75), (-1.8, 0.48, 2.18)), ((1.8, 0.98, 1.75), (1.8, 0.48, 2.18)),
                ((-1.8, 0.98, 1.75), (-1.3, 0.98, 2.18)), ((1.8, 0.98, 1.75), (1.3, 0.98, 2.18))],
        gratings=[(-2.48, 0.9, 2.48, 2.3, ZD, "NWE", True, (("S", 0.0, 0.305), ("S", 0.383, 0.57), ("S", 0.63, 1.0)))],
        collars=[],
        hatches=[],
        risers=[(-1.0, 1.6, ZD, ZD + 0.8 - 0.47, 0.2, 0.27, "green"),
                (1.0, 1.65, ZD, ZD + 0.26 - 0.1, 0.2, 0.27, "yellow")],
    ),
    walls={0: 2.18, 1: 2.18, 2: 2.23},
    lift={"feed_drum": ZD, "compressor": ZD, "makeup": ZD, "dosing": ZD},
    skip=("manifold", "exchanger"),
    reactor=(0.0, -0.15),
    legs=[(1.2, -0.88), (-1.2, -0.88)],
    valve=None,
    drum=dict(kind="ew", x0=-1.5, x1=-0.4, y=1.6, r=0.47, z=0.8, bands=(-1.2,), saddles=(-1.3, -0.6),
              welds=(-0.8,)),
    compressor=dict(kind="v", bottle=(1.0, 1.65), dir=1, skid_w=0.66, motor=0.42, raised=0.26),
    scrubber=(1.95, -0.3),
    scrub_nozzle=(-0.16, -0.16),
    scrub_gauge=-2.2,
    condenser=(-2.05, 0.42),
    pot=None,
    makeup=(0.32, 1.62),
    dosing=(-0.05, 1.12),
    settle=(-2.0, -0.55),
    press=(-1.95, -1.985),
    dropbox_w=(0.535, 0.53),
    receiver=(-0.75, 0.75),
    recv_yz=(-1.66, 0.47),
    recv_skid_s=-2.05,
    recv_skid_n=-1.26,
    pumphouse=(2.055, -2.025),
    cabinet=(1.44, -1.85),
    manifold=None,
    exchanger=None,
    drain=None,
    instr=[(1.9, 0.29), (2.42, 0.29), (2.42, 0.85), (1.9, 0.85)],
    instr_h=1.0,
    drip_a=-0.6,
    sockets={
        "north": ((0.9, -2.378, 0.45), (0, -1, 0), "the front bulkhead"),
        "east": ((2.448, 0.55, 0.6), (1, 0, 0), "the instrument house"),
        "south": ((0.0, 2.328, 0.6), (0, 1, 0), "the room's north wall"),
        "west": ((-2.478, 0.42, 0.45), (-1, 0, 0), "the vent condenser"),
    },
    runs=dict(
        loop1=[(1.2, -0.88, 2.87), (1.1, -0.78, 3.05), (0.9, -0.68, 2.95), (0.77, -0.62, 2.74)],
        loop2=[(-1.2, -0.88, 2.87), (-1.12, -0.82, 3.08), (-0.95, -0.72, 3.2), (-0.76, -0.6, 3.1)],
        foot1=[(0.62, -0.55, 0.32), (0.95, -0.75, 0.3), (1.08, -0.82, 0.3)],
        foot2=[(-0.62, -0.55, 0.32), (-0.95, -0.75, 0.3), (-1.08, -0.82, 0.3)],
        gas=[(1.55, 1.2, 2.55), (1.42, 0.6, 2.5), (1.32, -0.2, 1.9), (1.22, -0.62, 1.55)],
        feed=[(-0.75, 1.27, 1.62), (-0.8, 0.85, 1.5), (-1.05, 0.2, 1.2), (-1.19, -0.62, 1.0)],
        dosing=[(0.15, 1.3, 0.7), (0.0, 1.6, 0.8), (-0.22, 1.6, 0.8)],
        makeup=[(0.0, 1.6, 1.5), (-0.5, 1.6, 1.5), (-0.55, 1.6, 1.27)],
        scrub=[(1.8, -0.45, 2.75), (1.25, -0.25, 3.5), (0.72, -0.12, 3.48), (0.55, -0.1, 3.3)],
        vent=[(-1.66, 0.31, 0.75), (-1.25, 0.2, 0.75), (-0.87, 0.09, 0.75)],
        settle=[(-1.6, -0.5, 1.9), (-1.45, -0.78, 1.7)],
        slurry=[(-1.95, -1.0, 1.1), (-1.6, -1.2, 1.25), (-1.615, -1.42, 1.0), (-1.615, -1.53, 1.0)],
        filtrate=[(-1.585, -1.985, 1.33), (-1.585, -1.95, 1.6), (-1.1, -1.85, 1.55), (-0.55, -1.66, 1.15),
                  (-0.55, -1.66, 0.88)],
        pump=[(1.78, -1.93, 1.6), (1.3, -1.72, 1.2), (1.05, -1.66, 0.5), (0.89, -1.66, 0.47)],
        cable=[(1.58, -1.85, 0.85), (1.6, -1.85, 0.6), (1.63, -1.85, 0.6)],
        bundle_e=[(2.05, 0.28, 0.7), (2.0, 0.24, 0.6), (1.97, 0.21, 0.5)],
    ),
    lifted_clutter=[(ZD, [
        ("barrels", -2.0, 1.25, 2, 3),
        ("jbox", 1.95, 1.12, 0.35, 0.22, 0.4),
        ("jbox", 2.1, 2.12, 0.4, 0.2, 0.4),
        ("jbox", -2.05, 2.13, 0.5, 0.24, 0.45),
        ("tank", -2.15, 1.75, 0.2, 0.9, "grey"),
    ])],
    clutter=[
        ("barrels", 1.1, -1.5, 2, 5),
        ("jbox", 2.1, -1.15, 0.6, 0.5, 0.9),
        ("jbox", -2.15, -1.27, 0.5, 0.4, 0.75),
        ("jbox", -1.15, -1.8, 0.4, 0.5, 0.7),
        ("barrels", 1.15, 0.55, 2, 7),
        ("valve", 1.68, -0.95, 0.5, "red"),
        ("barrels", 0.55, -1.17, 1, 8),
        ("jbox", 1.3, 0.25, 0.35, 0.25, 0.55),
    ],
    ladder_at=(0.5, 0.78, ZD + 0.42, "x"),
    stains=[(2.0, -2.38, 0.4, 0.12, 0.1), (-1.85, -2.38, 0.4, 0.1, -0.05), (0.0, -0.9, 0.3, 0.15)],
    chain=["solution", "wall sleeve", "riser", "feed drum", "downcomer foot", "riser (gas lift)", "reactor",
           "downcomer", "settling pot", "filter press", "receiver", "output"],
    # from --probe (frame 0 of each layer alone, px over half alpha at 4x; under 40 is not a motion anyone sees)
    unseen={"north": ("coupling-dosing", "gauge-reactor-upper", "drip"), "east": ("gauge-scrubber",), "south": ("coupling-dosing", "gauge-reactor-upper", "gauge-reactor-lower", "gauge-scrubber", "drip"), "west": ("coupling-compressor", "coupling-pump", "gauge-reactor-upper", "gauge-scrubber", "drip")},
)

# ------------------------------------------------------------------------------------------------ 3, rotunda
# 3, "the rotunda": the reactor's round house -- a riveted drum wall 3.1 across and 1.3 tall with a conical
# roof, the reactor standing up out of its middle and the two glass legs set into its south flank, one either
# side of the front. A low block across the back takes the inputs through its north wall, the users on its
# roof straight over their sleeves (the feed drum lying north-south over the solution's, the compressor's
# bottle on its legs over the gas's); a porch on the front takes the output, the receiver on its roof. The
# settling pot and condenser stand on the west, the scrubber and instrument house on the east, the press and
# pump house in the front corners.
ZB, ZP = 0.9, 0.85
RC = (0.0, 0.1)
TAKES["rotunda"] = dict(
    pitch="the rotunda",
    pitch_lines=[
        "The reactor's round house: a riveted drum wall 3.1 across with a conical roof, the reactor standing up out of its middle and the two glass",
        "legs set into its front flank. A low block across the back takes the inputs through its north wall, their users on its roof straight over",
        "the sleeves (feed drum over the solution's, the compressor's bottle over the gas's), each fed by a riser; a porch on the front takes the",
        "output, the receiver on its roof. The settling pot and condenser stand west, the scrubber and instrument house east, press and pump house in front.",
    ],
    building=dict(
        casings=[
            dict(pts=[(-2.4, 1.0), (2.4, 1.0), (2.4, 2.15), (2.25, 2.3), (1.58, 2.3), (1.58, 2.18), (0.42, 2.18),
                      (0.42, 2.3), (-0.42, 2.3), (-0.42, 2.18), (-1.58, 2.18), (-1.58, 2.3), (-2.25, 2.3), (-2.4, 2.15)],
                 z=ZB, dress={
                1: dict(louvres=((0.5, 0.34, 0.3),)),
                7: dict(stencils=((0.5, 0.36, 0.1, 0.6),)),
                13: dict(louvres=((0.5, 0.34, 0.3),)),
            }),
            dict(pts=[(-0.7, -2.23), (0.7, -2.23), (0.7, -1.3), (-0.7, -1.3)], z=ZP, dress={
                1: dict(louvres=((0.45, 0.3, 0.3),)), 3: dict(louvres=((0.55, 0.3, 0.3),))}),
        ],
        rotundas=[dict(at=RC, r=1.55, h=1.25, roof_top=1.5, r_top=0.98,
                       clear_angles=((-0.93, 0.25), (-2.21, 0.25)), doors=((-0.6, 0.3),),
                       louvres=((2.6, 0.36, 0.34), (0.5, 0.36, 0.34)))],
        clear=[(-1.0, 2.18), (1.0, 2.18), (0.0, -2.23), (0.52, -2.23), (0.0, 2.3)],
        collars=[(0.0, 0.1, 0.9, 1.5)],
        risers=[(-1.0, 1.85, ZB, ZB + 0.75 - 0.45, 0.2, 0.27, "green"),
                (1.0, 1.8, ZB, ZB + 0.26 - 0.1, 0.2, 0.27, "yellow"),
                (0.0, -1.83, ZP, ZP + 0.7 - 0.39, 0.2, 0.27, "green")],
    ),
    walls={0: 2.18, 1: 2.18, 2: 2.23},
    lift={"feed_drum": ZB, "compressor": ZB, "makeup": ZB, "dosing": ZB, "receiver": ZP},
    skip=("manifold", "exchanger"),
    reactor=RC,
    ladder=-1.95,
    gauge_lo_z=1.75,
    gauge_hi_z=2.32,
    hazard_z=2.85,
    legs=[(1.05, -1.3), (-1.05, -1.3)],
    valve=None,
    drum=dict(kind="ns", x=-1.0, y0=1.4, y1=2.03, r=0.45, z=0.75),
    compressor=dict(kind="v", bottle=(1.0, 1.8), dir=1, skid_w=0.66, motor=0.42, raised=0.26),
    scrubber=(2.02, -0.35),
    scrub_nozzle=(-0.16, 0.16),
    scrub_gauge=-2.0,
    condenser=(-2.05, 0.6),
    pot=None,
    makeup=(-2.0, 1.7),
    dosing=(0.05, 1.95),
    settle=(-2.0, -0.55),
    press=(-1.95, -1.985),
    dropbox_w=(0.535, 0.53),
    receiver=(-0.55, 0.55),
    recv_yz=(-1.83, 0.7),
    recv_skid_s=-2.2,
    recv_skid_n=-1.5,
    pumphouse=(2.055, -2.025),
    cabinet=(1.2, -2.25),
    manifold=None,
    exchanger=None,
    drain=None,
    instr=[(1.8, 0.35), (2.42, 0.35), (2.42, 0.98), (1.8, 0.98)],
    instr_h=1.0,
    drip_a=-1.5,
    sockets={
        "north": ((0.52, -2.258, 0.5), (0, -1, 0), "the front porch"),
        "east": ((2.448, 0.65, 0.6), (1, 0, 0), "the instrument house"),
        "south": ((0.0, 2.328, 0.5), (0, 1, 0), "the back block's north wall"),
        "west": ((-2.428, 1.6, 0.5), (-1, 0, 0), "the back block's west wall"),
    },
    runs=dict(
        loop1=[(1.05, -1.3, 2.87), (0.95, -1.18, 3.05), (0.7, -0.85, 2.95), (0.56, -0.63, 2.74)],
        loop2=[(-1.05, -1.3, 2.87), (-0.95, -1.18, 3.0), (-0.7, -0.85, 2.6), (-0.56, -0.63, 2.42)],
        foot1=[(0.95, -1.2, 0.3), (0.85, -1.05, 0.24)],
        foot2=[(-0.95, -1.2, 0.3), (-0.85, -1.05, 0.24)],
        gas=[(1.55, 1.2, 2.25), (1.4, 0.3, 2.0), (1.25, -0.6, 1.75), (1.12, -1.04, 1.6)],
        feed=[(-1.0, 1.27, 1.65), (-1.3, 0.6, 1.85), (-1.6, -0.4, 2.0), (-1.5, -1.1, 1.95), (-1.33, -1.3, 1.9)],
        dosing=[(0.0, 1.85, 0.65), (-0.53, 1.85, 0.75)],
        makeup=[(-1.7, 1.7, 1.2), (-1.47, 1.75, 0.75)],
        scrub=[(1.8, -0.15, 2.75), (1.25, 0.1, 3.5), (0.72, 0.15, 3.48), (0.55, 0.15, 3.3)],
        vent=[(-1.66, 0.505, 0.55), (-1.5, 0.47, 0.55)],
        settle=[(-1.82, -0.5, 1.85), (-1.5, -0.95, 1.65), (-1.27, -1.13, 1.5)],
        slurry=[(-1.95, -1.0, 1.1), (-1.7, -1.25, 1.25), (-1.615, -1.42, 1.0), (-1.615, -1.53, 1.0)],
        filtrate=[(-1.585, -1.985, 1.33), (-1.585, -1.95, 1.6), (-1.1, -1.85, 2.0), (-0.45, -1.83, 1.98)],
        pump=[(1.81, -1.945, 1.4), (1.3, -1.9, 1.7), (0.9, -1.83, 1.6), (0.69, -1.83, 1.55)],
        cable=[(1.2, -2.1, 0.95), (1.15, -1.95, 0.9), (1.1, -1.88, 0.71)],
        bundle_e=[(1.8, 0.65, 0.6), (1.65, 0.6, 0.55), (1.5, 0.56, 0.5)],
    ),
    lifted_clutter=[(ZB, [
        ("barrels", -2.1, 1.25, 1, 3),
        ("jbox", 2.05, 1.15, 0.4, 0.22, 0.4),
    ])],
    clutter=[
        ("jbox", -2.15, -1.27, 0.5, 0.45, 0.75),
        ("jbox", 1.95, -1.2, 0.5, 0.4, 0.6),
        ("jbox", -1.05, -1.95, 0.5, 0.4, 0.8),
        ("jbox", 1.05, -1.86, 0.5, 0.28, 0.7),
        ("valve", 1.6, -0.95, 0.5, "red"),
    ],
    stains=[(2.0, -2.38, 0.4, 0.12, 0.1), (-1.85, -2.38, 0.4, 0.1, -0.05)],
    chain=["solution", "wall sleeve", "riser", "feed drum", "downcomer", "riser (gas lift)", "reactor",
           "downcomer", "settling pot", "filter press", "receiver", "output"],
    # from --probe (frame 0 of each layer alone, px over half alpha at 4x; under 40 is not a motion anyone sees)
    unseen={"north": (), "east": ("coupling-dosing", "gauge-reactor-lower", "gauge-scrubber", "drip"), "south": ("gauge-reactor-upper", "gauge-reactor-lower", "gauge-scrubber"), "west": ("coupling-compressor", "coupling-pump", "gauge-reactor-upper", "drip")},
)
