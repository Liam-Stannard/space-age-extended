    # ------------------------------------------------------------ T03i (B2): the gallery audit
    def gallery_audit(self):
        """T03i: the body is built to B2, so nothing is cut back: every part of the dry drill that
        stands in the gallery band (outside the gallery's inner line, from the plate's top to over
        the runs' flanges) is listed "GALLERY <name> [<mat>] lo hi"; the band must be clear."""
        G = self.G
        bpy.context.view_layer.update()
        found = []
        for g, objs in list(G["PARTS"].items()):
            if g in self.SKIP_GROUPS or g.startswith("rig-"):
                continue
            for o in objs:
                if o.type not in ("MESH", "CURVE") or o.hide_render or o.name.startswith("chassis"):
                    continue
                lo, hi = self.bbox(o)
                if hi.z <= Z0 + 0.002 or lo.z >= Z1:
                    continue
                vs = self.verts(o)
                n_in = sum(1 for v in vs if Z0 + 0.002 < v.z < Z1 and self.outside_inner(v.x, v.y)
                           and abs(v.x) < 2.6 and abs(v.y) < 2.6)
                if n_in:
                    m = o.active_material.name if o.active_material else ""
                    found.append(f"{o.name} [{m}] {g} verts {n_in}/{len(vs)} lo ({lo.x:.2f},{lo.y:.2f},{lo.z:.2f}) "
                                 f"hi ({hi.x:.2f},{hi.y:.2f},{hi.z:.2f})")
        self.log["gallery"] = found
        for ln in found:
            print("GALLERY", ln, flush=True)
        print(f"RIG gallery audit: {len(found)} parts in the band", flush=True)

    # ------------------------------------------------------------ the plate (T03h; T03i: the body's own)
    def plate(self):
        """T03i (B2): the body's chassis is the plate now (ballast_drill_b2.py: one casting from
        the ground to PT, the notches and bays open, the bays' lining up its height). Here only its
        edge's bolt row (T03h's, the chassis's wall-top row moved to the plate's edge): none where a
        face saddle of any direction stands, nor under any direction's junction flange."""
        G = self.G
        g = "body"
        before = set(bpy.data.objects)
        js = []
        for d, deg in G["contract"].DIRECTIONS["four"]:
            for c in fit_conns(deg):
                js.append(self.junction_xy(*c, G))
        ew = self.riser_lat(1 + G["H_AXIS_V"] - G["ZA"] / 2), self.riser_lat(-1 + G["H_AXIS_V"] - G["ZA"] / 2)
        avoid_ns, avoid_ew = (1.0, -1.0, 1.4, -1.4), ew + (1.4, -1.4)
        nb = 0
        for k4 in range(4):
            rot = Matrix.Rotation(math.pi / 2 * k4, 2)
            for lat in [0.78 + 0.1 * i for i in range(7)] + [-0.78 - 0.1 * i for i in range(7)]:
                v = rot @ Vector((lat, -(G["E"] - 0.05)))
                ns = abs(v.y) > abs(v.x)
                lat_w = v.x if ns else v.y
                if any(abs(lat_w - a_) < 0.085 for a_ in (avoid_ns if ns else avoid_ew)):
                    continue
                if any((v - J).length < R_BODY + 0.03 + 0.03 for J in js):
                    continue
                G["bolt"]((v.x, v.y, PLATE_TOP + 0.007), 0.016, 0.014, group=g)
                nb += 1
        self.plate_parts = [G["CHASSIS"]] + [o for o in bpy.data.objects if o not in before]
        self.log["plate"] = dict(top=PLATE_TOP, face=PLATE_FACE, material="iron", bolts=nb,
                                 note="the body's chassis (ballast_drill_b2.py)")
        print(f"RIG plate: the chassis, top {PLATE_TOP}; {nb} edge bolts", flush=True)

    # ------------------------------------------------------------ T03i: the closed wall fitting
    @staticmethod
    def riser_lat(lat):
        """B2's riser_lat: a junction's riser stands at its fitting, unless that would put it over
        the open bay; then just clear of the bay's edge (the E/W fittings at 0.806: 0.98), the pipe
        jogging to it inside the plate."""
        if abs(lat) - R_HEAD < BAY_HW + 0.02:
            return math.copysign(BAY_HW + R_HEAD + 0.02, lat)
        return lat

    @staticmethod
    def fit_lat(x, y, f, G):
        """The connection's fitting across its face (no jog): x on N/S, y on E/W."""
        if f in "NS":
            return x + G["V_AXIS_U"]
        return -y + G["H_AXIS_V"] - G["ZA"] / 2

    @staticmethod
    def recess_hw(f, G):
        return (POCKET_HW - 0.01 if f == "N" else G["H_RING_R"] - 0.02) + 0.035

    def junction(self, d, conn, J, toward, gauge):
        """T03i (B2; Liam: "Close the slots"; "Keep 1.15"): the junction stands on the plate's top on
        a bolted flange, its head at the run's axis; the connection's pipe runs inside the plate
        (not modelled: the casting) to the wall fitting at the face. On a N, E or W face the end ring
        sits in a shallow recessed boss cut into the plate's wall (lined, a bolted frame either side
        of its mouth, a wall flange at its back where the sleeve leaves the casting), wholly under
        the plate's top; on the south face the ring stands 0.24 proud ("Accept"), the sleeve leaving
        the face through a bolted wall flange. Nothing of it touches the plate: 0.001 off it."""
        G = self.G
        x, y, f = conn
        g = self.grp(d, J.y)
        n = {"N": Vector((0, 1)), "S": Vector((0, -1)), "E": Vector((1, 0)), "W": Vector((-1, 0))}[f]
        t = Vector((-n.y, n.x))
        ZA = G["ZA"]
        body = self.cfg["body"]
        over = self.overhead(J, Z_RUN)
        self.end_joint = []
        lat = self.fit_lat(x, y, f, G)
        F = Vector((lat, n.y * R_AX)) if f in "NS" else Vector((n.x * R_AX, lat))   # the fitting's line, on the gallery
        # the riser: a bolted flange on the plate's top, a short neck up into the head
        zf = PLATE_TOP + 0.001
        G["cyl"]((J.x, J.y, zf + 0.02), R_BODY + 0.03, 0.04, "iron", g, verts=40, bevel=0.008)
        for k in range(6):
            a = 2 * math.pi * (k + 0.5) / 6
            G["bolt"]((J.x + (R_BODY + 0.012) * math.cos(a), J.y + (R_BODY + 0.012) * math.sin(a), zf + 0.045), 0.012,
                      0.01, group=g)
        zh0 = Z_RUN - R_HEAD + 0.02
        G["cyl"]((J.x, J.y, (zf + 0.04 + zh0 + 0.02) / 2), R_BODY, zh0 + 0.02 - zf - 0.04, body, g, verts=48, bevel=0.006)
        # the head: a squat cast body, a flange ring, a domed bonnet bolted on, a lifting eye
        zh1 = Z_RUN + 0.13
        G["cyl"]((J.x, J.y, (zh0 + zh1) / 2), R_HEAD, zh1 - zh0, body, g, verts=48, bevel=0.02)
        G["cyl"]((J.x, J.y, zh0 + 0.03), R_HEAD + 0.012, 0.028, "iron_worn", g, verts=48, bevel=0.004)   # a cast band
        G["cyl"]((J.x, J.y, zh1 + 0.014), R_HEAD + 0.025, 0.028, "iron_worn", g, verts=48, bevel=0.006)
        G["sphere"]((J.x, J.y, zh1 + 0.028), R_HEAD - 0.05, body, g, squash=0.42)
        for k in range(8):
            a = 2 * math.pi * (k + 0.5) / 8
            self.nut(Vector((J.x + (R_HEAD + 0.008) * math.cos(a), J.y + (R_HEAD + 0.008) * math.sin(a), zh1 + 0.036)),
                     (0, 0, 1), g, r=0.016, h=0.014)
        ze = zh1 + 0.028 + (R_HEAD - 0.05) * 0.42
        if over is None or over > ze + 0.1:
            G["cyl"]((J.x, J.y, ze + 0.008), 0.032, 0.016, "iron_worn", g, verts=20, bevel=0.003)
            G["ring"]((J.x, J.y, ze + 0.045), 0.034, 0.02, 0.012, "steel", g, verts=24, bevel=0.002,
                      rot=(math.pi / 2, 0, math.atan2(toward.y, toward.x)))
        else:
            self.log.setdefault("no_eye", {}).setdefault(d, []).append([round(J.x, 3), round(J.y, 3), round(over, 3)])
        # the outlet spigot and its joint, toward the run
        self.along(((J + toward * SPIGOT / 2).x, (J + toward * SPIGOT / 2).y, Z_RUN), (toward.x, toward.y, 0), R_RUN,
                   SPIGOT, body, g, verts=40, bevel=0.0)
        jc = J + toward * (SPIGOT + JOINT_H)
        before_j = set(bpy.data.objects)
        self.joint((jc.x, jc.y, Z_RUN), (toward.x, toward.y, 0), FLANGE_R, g)
        self.end_joint = [o for o in bpy.data.objects if o not in before_j]
        if gauge:
            back_ = J - toward * (R_HEAD + 0.04)
            self.along((back_.x, back_.y, Z_RUN + 0.02), (toward.x, toward.y, 0), 0.014, 0.1, "brass", g, verts=12)
            gp = J - toward * (R_HEAD + 0.1)
            G["cyl"]((gp.x, gp.y, Z_RUN + 0.07), 0.055, 0.024, "brass", g, verts=24, bevel=0.004)
            G["cyl"]((gp.x, gp.y, Z_RUN + 0.083), 0.044, 0.004, "polish", g, verts=24, bevel=0.0)
            G["box"]((gp.x + 0.012, gp.y + 0.008, Z_RUN + 0.086), (0.03, 0.004, 0.002), "dark", g, rot=(0, 0, 0.6),
                     bevel=0.0)
            G["cyl"]((gp.x, gp.y, Z_RUN + 0.035), 0.012, 0.05, "brass", g, verts=10)
        # the wall fitting
        face = PLATE_FACE
        if f == "S":
            ye = -2.53 - ZA / 2
            yw = -face - 0.001                                       # the wall flange's back, 0.001 off the face
            self.along((F.x, yw - 0.011, ZA), (0, 1, 0), R_RUN + 0.06, 0.02, "iron_worn", g, verts=40, bevel=0.004)
            for kk in range(8):
                a_ = 2 * math.pi * (kk + 0.5) / 8
                q = Vector((F.x + (R_RUN + 0.035) * math.cos(a_), yw - 0.028, ZA + (R_RUN + 0.035) * math.sin(a_)))
                self.nut(q, (0, 1, 0), g, r=0.014, h=0.012)
            self.along((F.x, (yw - 0.021 + ye + 0.035) / 2, ZA), (0, 1, 0), R_RUN, abs(ye + 0.035 - (yw - 0.021)), "steel",
                       g, verts=48, bevel=0.0)
            G["cyl"]((F.x, ye + 0.035, ZA), G["V_RING_R"] - 0.02, 0.07, "steel", g, verts=48, rot=(math.pi / 2, 0, 0),
                     bevel=0.01)
            for k in range(8):
                a = 2 * math.pi * (k + 0.5) / 8
                self.nut(Vector((F.x + 0.33 * math.cos(a), ye - 0.004, ZA + 0.33 * math.sin(a))), (0, 1, 0), g)
            G["cyl"]((F.x, ye - 0.003, ZA), R_RUN - 0.03, 0.006, "dark", g, verts=32, rot=(math.pi / 2, 0, 0), bevel=0.0)
            self.weld_ring(Vector((F.x, ye + 0.08, ZA)), (0, 1, 0), g)
            return round(ye, 3)
        # N, E, W: the recessed boss in the plate's wall
        hw = self.recess_hw(f, G)
        z0, z1 = RECESS_Z0, RECESS_Z1
        rb = RECESS_BACK
        nn = Vector((n.x, n.y, 0))
        tt = Vector((t.x, t.y, 0))
        lo_l, hi_l = lat - hw, lat + hw
        if f in "EW":
            # the recess's own plate part only (an E/W ring straddles the bay's edge: Liam, "Accept")
            if lo_l < BAY_HW < hi_l:
                lo_l = BAY_HW + 0.001
            elif lo_l < -BAY_HW < hi_l:
                hi_l = -BAY_HW - 0.001

        def P(r, l, z):                                          # r out along n, l across (the lateral), z
            return (nn * r + Vector((0, 0, z)) + (Vector((0, 1, 0)) if f in "EW" else Vector((1, 0, 0))) * l)
        # its back liner, sill and soffit, inside the cut by 0.001
        lw = hi_l - lo_l - 0.002
        lc = (lo_l + hi_l) / 2
        dims = (lambda a_, w_, h_: (a_, w_, h_)) if f in "EW" else (lambda a_, w_, h_: (w_, a_, h_))
        G["box"](tuple(P(rb + 0.005, lc, (z0 + z1) / 2)), dims(0.008, lw, z1 - z0 - 0.002), "liner", g, bevel=0.0)
        dep = face - rb - 0.012
        G["box"](tuple(P(rb + 0.01 + dep / 2, lc, z0 + 0.005)), dims(dep, lw, 0.008), "liner", g, bevel=0.0)
        G["box"](tuple(P(rb + 0.01 + dep / 2, lc, z1 - 0.005)), dims(dep, lw, 0.008), "liner", g, bevel=0.0)
        for s, ev in ((-1, lat - hw), (1, lat + hw)):
            if abs(ev) < BAY_HW + 0.01:
                continue                                        # that side is the bay's air
            G["box"](tuple(P(rb + 0.01 + dep / 2, ev - s * 0.005, (z0 + z1) / 2)), dims(dep, 0.008, z1 - z0 - 0.002),
                     "liner", g, bevel=0.0)
            fp = P(face + 0.007, ev + s * 0.03, (z0 + z1) / 2)
            G["box"](tuple(fp), dims(0.012, 0.06, z1 - z0 + 0.02), "steel", g, bevel=0.003)
            for zb in (z0 + 0.06, (z0 + z1) / 2, z1 - 0.06):
                bp = P(face + 0.017, ev + s * 0.03, zb)
                G["bolt"](tuple(bp), 0.012, 0.01, group=g, rot=(math.pi / 2, 0, math.atan2(n.y, n.x) + math.pi / 2))
        # the wall flange at its back, the sleeve out to the end ring
        self.along(tuple(P(rb + 0.0105 + 0.01, lat, ZA)), tuple(nn), R_RUN + 0.06, 0.02, "iron_worn", g, verts=40,
                   bevel=0.004)
        for kk in range(6):
            a_ = 2 * math.pi * (kk + 0.5) / 6
            q = P(rb + 0.0105 + 0.027, lat + (R_RUN + 0.035) * math.cos(a_), ZA + (R_RUN + 0.035) * math.sin(a_))
            self.nut(q, tuple(nn), g, r=0.014, h=0.012)
        if f == "N":
            ye = 2.495 - 0.025
            self.along(tuple(P((rb + 0.03 + ye) / 2, lat, ZA)), tuple(nn), R_RUN, ye - rb - 0.03, "steel", g, verts=48,
                       bevel=0.0)
            G["cyl"](tuple(P(ye, lat, ZA)), POCKET_HW - 0.01, 0.04, "steel", g, verts=48, rot=(math.pi / 2, 0, 0),
                     bevel=0.008)
            return round(ye, 3)
        sgn = 1 if f == "E" else -1
        xf = 2.5 - 0.03
        self.along(tuple(P((rb + 0.03 + xf) / 2, lat, ZA)), tuple(nn), R_RUN, xf - rb - 0.03, "steel", g, verts=48,
                   bevel=0.0)
        G["cyl"](tuple(P(xf, lat, ZA)), G["H_RING_R"] - 0.02, 0.04, "steel", g, verts=48, rot=(0, math.pi / 2, 0),
                 bevel=0.006)
        for k in range(8):
            a = 2 * math.pi * (k + 0.5) / 8
            self.nut(P(xf - 0.026, lat + 0.27 * math.cos(a), ZA + 0.27 * math.sin(a)), tuple(nn), g, r=0.016, h=0.012)
        self.weld_ring(P(xf - 0.07, lat, ZA), tuple(nn), g)
        return round(sgn * xf, 3)

    # ------------------------------------------------------------ the recesses, per direction (T03i)
    def pockets(self):
        """T03i: per direction, a cutter for each N/E/W connection's recess (none for the south's
        ring, which stands proud), cutting the plate's parts it meets in that direction's wet
        layers only."""
        G = self.G
        boxes = []
        for d, deg in G["contract"].DIRECTIONS["four"]:
            for c in fit_conns(deg):
                b_ = self.slot_box(c, G)
                if b_ is not None:
                    boxes.append(b_)
        for i in range(4):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -20))
            cb = bpy.context.active_object
            cb.name = f"slotcut{i}"
            cb.hide_render = True
            cb.display_type = "WIRE"
            cb.parent = G["BODY"]
            self.pocket_cutters.append(cb)
        targets = []
        for g, objs in G["PARTS"].items():
            if g in self.SKIP_GROUPS or g.startswith("rig-"):
                continue
            for o in objs:
                if o.type != "MESH":
                    continue
                lo, hi = self.bbox(o)
                if any(all(lo[i] <= c[i] + s[i] / 2 and hi[i] >= c[i] - s[i] / 2 for i in range(3)) for c, s in boxes):
                    targets.append(o)
        for o in targets:
            G["cut"](o, *self.pocket_cutters)
        self.pocket_targets = targets
        print(f"RIG recesses: {len(targets)} plate parts take the recess cutters: "
              f"{sorted(o.name for o in targets)}", flush=True)

    def slot_box(self, c, G):
        x, y, f = c
        if f == "S":
            return None
        n = {"N": (0, 1), "E": (1, 0), "W": (-1, 0)}[f]
        lat = self.fit_lat(x, y, f, G)
        hw = self.recess_hw(f, G)
        rr0, rr1 = RECESS_BACK, 2.9
        mid = (rr0 + rr1) / 2
        zc, zs = (RECESS_Z0 + RECESS_Z1) / 2, RECESS_Z1 - RECESS_Z0
        if f == "N":
            return Vector((lat, mid, zc)), Vector((2 * hw, rr1 - rr0, zs))
        return Vector((n[0] * mid, lat, zc)), Vector((rr1 - rr0, 2 * hw, zs))

    def place_pockets(self, d=None):
        G = self.G
        for cb in self.pocket_cutters:
            cb.location, cb.scale = (0, 0, -20), (1, 1, 1)
        if d is not None:
            deg = dict(G["contract"].DIRECTIONS["four"])[d]
            for cb, c in zip(self.pocket_cutters, fit_conns(deg)):
                b_ = self.slot_box(c, G)
                if b_ is not None:
                    cb.location, cb.scale = b_
        bpy.context.view_layer.update()

