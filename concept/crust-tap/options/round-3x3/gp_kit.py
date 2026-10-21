"""Gas Pump 3x3, options round (gas-pump-3x3 T02): the shared kit for the three takes.

The Vent Pump's signed-off finish, used whole: kit/ holds the Vent Pump model's kit (vpb3_kit, vpb4_kit,
vp4_glass, vpb5_kit with variant (a), "warmer paints"), copied unchanged but for the import path; its
paints, worn_paint(), the satin floor and the unlit catcher are the Vent Pump's; the light is a step down (SUN_GP).

Added here, for a pump that raises a gas:

  gas window      gas_window(p0, p1, r): a sight glass set in the line, the gas drifting through it in
                  wisps of the vent's colour. Paint, never light: nothing on this building glows. Idle the
                  glass shows empty (dark), as the 2x2 Gas Pump's does. The colour is one RGB node per
                  material (GAS_TINT), so the same model renders siderane (#A8D929, the vent's
                  mining_visualisation_tint) or helium-3 (#8CC7E6) with --helium.
  linkage         link(A, B, r): a rod whose two ends follow A(t, on) and B(t, on) (pitman arms,
                  connecting rods); fourbar(): the beam angle that keeps a pitman's length.
  reducer         reducer(p, q, r0, r1): a cone between two bores, the visible step a line narrows at.
  run_gp()        vpb5_kit.run5()'s surfacing (unlit catcher, softened windows, satin floor), then the
                  kit's run (idle, plate, the working loop, three turns); no glow pass (nothing glows).

  $BLENDER -b --python gp_<n>_*.py -- <out-dir> [--quick] [--frames N] [--only working|idle] [--helium]
           [--check]

Units are tiles; north is +Y; the vent at the centre under the wellhead; one output, the middle of the
north face ({0, -1} in the engine's terms). Not a model; nothing is adopted.
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "kit"))
from vpb5_kit import *  # noqa: F401,F403,E402
import vpb5_kit as K5  # noqa: E402
import vpb3_kit as K  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

HELIUM = "--helium" in K.argv
SIDERANE_HEX = "#A8D929"       # siderane's map_color and mining_visualisation_tint (0.66, 0.85, 0.16)
HELIUM_HEX = "#8CC7E6"         # the helium-3 vent's mining_visualisation_tint (0.55, 0.78, 0.90)
GAS_TINT = []                  # (RGB node, scale)
GAS_FILL = []                  # value nodes: 1 working, 0 idle (the glass empty)
EMPTY = "#2A2C2A"              # the glass's dark when empty


def gas_material(name, k=2, scale=5.0, axis="Z"):
    """The gas seen in a sight glass: wisps drifting along local `axis` (+ downstream) at k wavelengths a
    loop, in the vent's colour from deep (0.42 of it) to full (0.86); idle a dark empty glass. Paint."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    phase = N.new("ShaderNodeValue")
    K.PHASES.append((phase, k))
    wave = N.new("ShaderNodeTexWave")
    wave.bands_direction = axis
    wave.inputs["Scale"].default_value = scale
    wave.inputs["Distortion"].default_value = 9.0
    wave.inputs["Detail"].default_value = 2.5
    wave.inputs["Detail Scale"].default_value = 1.6
    L.new(tc.outputs["Object"], wave.inputs["Vector"])
    neg = N.new("ShaderNodeMath")
    neg.operation = "MULTIPLY"
    neg.inputs[1].default_value = -1.0
    L.new(phase.outputs[0], neg.inputs[0])
    L.new(neg.outputs[0], wave.inputs["Phase Offset"])
    rgb = N.new("ShaderNodeRGB")
    rgb.outputs[0].default_value = rig.srgb(HELIUM_HEX if HELIUM else SIDERANE_HEX)
    GAS_TINT.append(rgb)
    ramp = N.new("ShaderNodeMapRange")
    ramp.inputs["To Min"].default_value = 0.42
    ramp.inputs["To Max"].default_value = 0.86
    L.new(wave.outputs["Fac"], ramp.inputs["Value"])
    mul = N.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    L.new(rgb.outputs[0], mul.inputs["A"])
    comb = N.new("ShaderNodeCombineColor")
    for s in ("Red", "Green", "Blue"):
        L.new(ramp.outputs[0], comb.inputs[s])
    L.new(comb.outputs[0], mul.inputs["B"])
    fill = N.new("ShaderNodeValue")
    GAS_FILL.append(fill)
    mx = N.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    L.new(fill.outputs[0], mx.inputs["Factor"])
    mx.inputs["A"].default_value = rig.srgb(EMPTY)
    L.new(mul.outputs["Result"], mx.inputs["B"])
    L.new(mx.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.55
    K.M[name] = m
    K.GROUP[name] = ("the gas in the sight glass (the vent's colour)", "#A8D929")
    return name


def _gas_pose(t, on):
    for v in GAS_FILL:
        v.outputs[0].default_value = 1.0 if on else 0.0


K.ANIM.append(_gas_pose)
_n_gas = [0]


def gas_window(p0, p1, r=0.1, k=2, name="sight glass"):
    """An armoured sight glass on the axis p0 -> p1 (the gas flows that way): the gas body, the glass over
    it, a dark backing on the far half, a heavy bolted flange at each end, two tie rods behind (none in
    front, so no bars cross the gas). Returns (p0, p1): a line meets each flange square."""
    a, b = Vector(p0), Vector(p1)
    ax = (b - a).normalized()
    L = (b - a).length
    mid = (a + b) / 2
    _n_gas[0] += 1
    mat = gas_material(f"gas_{_n_gas[0]}", k=k, scale=3.5 / max(L, 0.2))
    rot = along(ax)
    cyl(tuple(mid), r * 0.8, L - 0.04, mat, rot=rot, verts=32, bevel=0)
    cyl(tuple(mid), r, L - 0.02, "pane", rot=rot, verts=32, bevel=0)
    for p in (a, b):
        cyl(tuple(p), r + 0.045, 0.07, "dark_steel", rot=rot, verts=32, bevel=0.006)
        cyl(tuple(p - ax * 0.0), r + 0.02, 0.1, "nickel", rot=rot, verts=32, bevel=0.004)
    up = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((0, 1, 0))
    side = ax.cross(up).normalized()
    back = Vector((0, 1, 0)) if abs(ax.y) < 0.9 else Vector((1, 0, 0))
    for s in (-1, 1):
        q = mid + back * (r + 0.02) * 0.7 + up * s * (r + 0.02) * 0.7
        cyl(tuple(q), 0.012, L + 0.06, "bare", rot=rot, verts=8, bevel=0)
    for e, s in ((a, 1), (b, -1)):
        for kk in range(6):
            ang = 2 * PI * (kk + 0.5) / 6
            off = (side * math.cos(ang) + up * math.sin(ang)) * (r + 0.03)
            cyl(tuple(e + off + ax * s * 0.04), 0.011, 0.02, "bolt", rot=rot, verts=6, bevel=0)
    route_label = name
    return tuple(a), tuple(b), route_label


def reducer(p, q, r0, r1, mat="bare"):
    """A concentric reducer from bore r0 at p to r1 at q (the visible step where a line narrows)."""
    a, b = Vector(p), Vector(q)
    cone(tuple((a + b) / 2), r0, r1, (b - a).length, mat, rot=along(b - a), verts=32)
    for e, r in ((a, r0), (b, r1)):
        cyl(tuple(e), r + 0.035, 0.04, "dark_steel", rot=along(b - a), verts=32)


def link(A, B, r=0.03, mat="bare", name="link"):
    """A rod whose ends follow A(t, on) and B(t, on) (model points): a pitman arm or connecting rod."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r, depth=1.0, location=(0, 0, 0))
    o = bpy.context.active_object
    K._finish(o, mat, 0, smooth=True)
    o.name = name

    def pose(t, on):
        a, b = Vector(A(t, on)), Vector(B(t, on))
        o.location = (a + b) / 2
        o.rotation_euler = along(b - a)
        o.scale = (1, 1, (b - a).length)
    K.ANIM.append(pose)
    pose(0.0, False)
    return o


def fourbar(pivot_xz, tail, crank_xz, rc, phi0=0.0, n=720):
    """A walking beam on pivot_xz, its tail `tail` tiles out along +x, a pitman to a crank of radius rc
    on crank_xz: theta(t) for the crank's angle phi0 + 2 pi t, keeping the pitman's length as it is at
    t = 0 with the beam level. Tabulated; returns (theta(t), crank_pin(t), tail_pt(t)) in the XZ plane."""
    px, pz = pivot_xz
    cx, cz = crank_xz

    def pin(t):
        a = phi0 + 2 * PI * t
        return (cx + rc * math.cos(a), cz + rc * math.sin(a))

    def tl(th):
        return (px + tail * math.cos(th), pz + tail * math.sin(th))
    c0 = pin(0.0)
    t0 = tl(0.0)
    Lp = math.hypot(t0[0] - c0[0], t0[1] - c0[1])
    tab = []
    for i in range(n + 1):
        t = i / n
        c = pin(t)
        lo, hi = -0.8, 0.8
        f = lambda th: math.hypot(tl(th)[0] - c[0], tl(th)[1] - c[1]) - Lp  # noqa: E731
        # the tail above the crank: the length grows with theta
        for _ in range(50):
            mid = (lo + hi) / 2
            if f(mid) > 0:
                hi = mid
            else:
                lo = mid
        tab.append((lo + hi) / 2)

    def theta(t):
        x = (t % 1.0) * n
        i = int(x)
        return tab[i] + (tab[min(i + 1, n)] - tab[i]) * (x - i)
    return theta, pin, tl


def corner_notch(x, y, s=0.16):
    """Nothing: a reminder in the takes that each footprint corner is left open or broken by equipment."""
    return None


SUN_GP, WORLD_GP = 10.0, 0.32   # the round's light: the Vent Pump's 13.5 and 0.44 put take 1's plate at p50 94, p95 174;
                                # 10 and 0.32 at p50 79, p95 150 (measure.py's tonal on gp_pack.py's 1x plate)


def clash_check(n=12):
    """--clash: no render. Every part that moves (its world matrix changes over the loop) is tested, at n poses,
    against every other part by BVH overlap; a pair is printed once, with each part's material and where it is.
    Contacts that are meant (a rod in its gland, a pin in its arm, a chain on its sheave) print too: the report
    sorts them by eye."""
    from mathutils.bvhtree import BVHTree
    objs = [o for o in K.OBJS if o.type == "MESH" and o not in K.STAINS]
    dg = bpy.context.evaluated_depsgraph_get()

    def mats():
        bpy.context.view_layer.update()
        return {o.name: o.matrix_world.copy() for o in objs}
    K.pose(0.0, True)
    m0 = mats()
    moving = set()
    for i in range(1, n):
        K.pose(i / n, True)
        mi = mats()
        moving |= {k for k in mi if any(abs(a - b) > 1e-5 for ra, rb in zip(mi[k], m0[k]) for a, b in zip(ra, rb))}
    for o in objs:
        if o.data.shape_keys is None and o.name.startswith("Cylinder") and o.scale.z != 1.0:
            moving.add(o.name)
    seen = {}

    def tree(o):
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = o.matrix_world
        t = BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
        ev.to_mesh_clear()
        return t

    def tag(o):
        m = o.data.materials[0].name if o.data.materials else "?"
        w = o.matrix_world.translation
        return f"{o.name}[{m}]@({w.x:.2f},{w.y:.2f},{w.z:.2f})"
    for i in range(n):
        K.pose(i / n, True)
        bpy.context.view_layer.update()
        dg.update()
        trees = {o.name: tree(o) for o in objs}
        for o in objs:
            if o.name not in moving:
                continue
            for q in objs:
                if q is o or (q.name in moving and q.name < o.name) or q.parent is o.parent and o.parent is not K.ROOT:
                    continue
                if trees[o.name].overlap(trees[q.name]):
                    key = (o.name, q.name)
                    if key not in seen:
                        seen[key] = (i, tag(o), tag(q))
    for (a, b), (i, ta, tb) in sorted(seen.items()):
        print(f"CLASH frame {i}/{n}: {ta} x {tb}")
    # every registered run (pipe, hose, cable, line) against every other part, at frame 0 and mid-loop: a contact
    # more than END tiles from both of the run's ends is a run passing through something (ends sit in their
    # fittings by design and are left to the crops)
    END = 0.14
    root = K.ROOT.matrix_world
    runs = 0
    for t in (0.0, 0.5):
        K.pose(t, True)
        bpy.context.view_layer.update()
        dg.update()
        trees = {o.name: tree(o) for o in objs}
        idx = {o.name: i for i, o in enumerate(K.OBJS)}
        for name, pa, pb, (i0, i1) in K.PIPES:
            ea, eb = root @ pa, root @ pb
            own = {o.name for o in K.OBJS[i0:i1]}
            body = [o for o in K.OBJS[i0:i1] if o.type == "MESH" and o.data.name.startswith("sweep")]
            for o in body:
                me = o.evaluated_get(dg).to_mesh()
                cent = [o.matrix_world @ p.center for p in me.polygons]
                o.evaluated_get(dg).to_mesh_clear()
                for q in objs:
                    if q.name in own:
                        continue
                    hits = trees[o.name].overlap(trees[q.name])
                    far = [cent[a_] for a_, _ in hits if min((cent[a_] - ea).length, (cent[a_] - eb).length) > END]
                    if far:
                        w = far[0]
                        print(f"RUNCLIP t={t}: {name} x {tag(q)} at ({w.x:.2f},{w.y:.2f},{w.z:.2f}), {len(far)} faces")
            runs += 1
    print(f"RUNCLIP runs checked {runs // 2}")
    print(f"CLASH count {len(seen)}, moving parts {len(moving)}")


def run_gp(meta, nf=24):
    if "--clash" in K.argv:
        clash_check()
        return
    if "--sun" not in K.argv:
        K.SUN_E = SUN_GP
    K.WORLD = WORLD_GP if "--world" not in K.argv else K.WORLD
    K5.catcher_unlit()
    K5.soften_windows()
    K5.satin_floor()
    meta = dict(meta, finish="the Vent Pump's (vpb5_kit variant a, warmer paints)", world=K.WORLD,
                gas=HELIUM_HEX if HELIUM else SIDERANE_HEX, helium=HELIUM)
    K.run(meta, nf=nf)
