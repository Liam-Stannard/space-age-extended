"""T06h: form 1, the casing, refined (Liam, 2026-10-21: form "1 Casing"; tone "Set it in the refine"; fittings on
east walls "Keep fittings as lit"; the putty grey kept; the left-out kit -- sampling manifold, exchanger, scrubber
drain skid, side-nozzle pot -- "Restore in refine"). A copy of round-forms/form_plans.py (T06g, 6c32ec3, which
stays as committed) with the frame and the rotunda taken out and the casing's changes marked T06h.

T06g's notes follow.
T06g: the three building forms -- where each unit of the Circulator's vessel set stands, the building it belongs
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
          "instrument_house": ZC, "exchanger": ZC, "manifold": ZC, "drain": ZC, "pot": ZC},
    reactor=(-0.1, 0.2),
    legs=[(1.2, -0.72), (-1.2, -0.72)],
    valve=(0.0, -0.95),
    valve_z=ZC,
    drum=dict(kind="ew", x0=-1.2, x1=-0.25, y=1.68, r=0.47, z=0.8, bands=(-0.62,), saddles=(-1.08, -0.4),
              welds=(-0.8,)),
    compressor=dict(kind="v", bottle=(1.0, 1.75), dir=1, skid_w=0.66, motor=0.42, raised=0.26),
    scrubber=(-1.88, 1.7),
    condenser=(1.95, -0.3),
    # T06h: the left-out kit restored on the roof ("Restore in refine"). The side-nozzle pot in the north gap
    # between the feed drum and the compressor's bottle, its nozzle off the reactor's shell (0.62 over the roof,
    # as over the ground before); the exchanger lying east-west between the legs and the receiver; the sampling
    # manifold between the instrument house and the compressor; the scrubber's drain skid down the west roof
    # edge, its header ending in its drain valve. Where the roof is tight a step smaller than T06e's (pot 0.26
    # for 0.30, exchanger 0.25 for 0.30). (The west gap, between the settling pot's and the scrubber's roof
    # collars, leaves 0.38 tile: no pot fits there.)
    pot=(0.3, 1.5),
    pot_r=0.26,
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
    manifold=(1.5, 1.04, 2.3, 1.36),
    exchanger=(0.15, 0.85, -1.15),
    exch_r=0.25,
    drain=(-2.4, -1.36, -2.03, -0.42),
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
        # T06h: the added kit ("Keep it") moved off the gaps the restored kit now takes
        ("barrels", 2.24, -1.3, 1, 3),
        ("barrels", -0.09, -1.26, 1, 4),
        ("jbox", 1.87, 0.75, 0.22, 0.3, 0.35),
        ("jbox", -1.95, 0.95, 0.35, 0.3, 0.45),
    ])],
    clutter=[],
    stains=[(2.0, -2.38, 0.4, 0.12, 0.1), (-1.85, -2.38, 0.4, 0.1, -0.05)],
    chain=["solution", "wall sleeve", "riser", "feed drum", "downcomer foot", "riser (gas lift)", "reactor",
           "downcomer", "settling pot", "filter press", "receiver", "output"],
    # from --probe (frame 0 of each layer alone, px over half alpha at 4x; under 40 is not a motion anyone sees)
    unseen={"north": (), "east": ("coupling-dosing",), "south": ("coupling-dosing", "gauge-reactor-upper", "gauge-reactor-lower", "gauge-scrubber", "drip"), "west": ("coupling-compressor", "coupling-pump", "gauge-reactor-upper", "gauge-reactor-lower", "gauge-scrubber", "drip")},
)
