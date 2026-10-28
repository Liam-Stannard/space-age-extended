"""Vent Pump, round 4 (T03): the helium sight glass in mix A, and the study's kit changes, for both
round-3 kits (artist A's vpa3_kit over round 2's vpa_kit; artist B's vpb3_kit).

Liam, 2026-10-15 (T02): mix A, "violet, pink pulse per stroke"; the study's kit changes "Yes,
carry them over"; a helium glow is allowed beside the melt's orange.

  carry(K)            the study's kit changes, made on the kit's material table before any part
                      is built: the helium line's ID bands #9C8CB0 (the kit's #B6A6C8 clipped
                      square to the sun), every gauge face ceramic (#B8AE98: the kit's cream face
                      clipped), every "pane" and "glass" a window rather than a lens (transparent
                      with a faint rough gloss: the refracting glass threw white sun glints).
  dark_flanges(fn)    wraps a kit's he_line() so its end flanges or collars are dark steel, not
                      bare (the bare ones glinted to 255).
  sight_tank(K, ...)  one armoured glass sight tank set in the helium line between two points,
                      its axis from p0 (the foot) to p1 (the head): a bolted flange and cap at each
                      end, a stub nozzle on the axis at each end that the line meets, four dark tie
                      rods, a dark backing plate on the far half inside the glass, the liquid and
                      its bubbles. Mix A: grey-violet liquid (#7E7488 as lit) with rising bubbles
                      (#B6A6C8 as lit), lit faintly violet (#9C86CC) while working, flushing
                      peach-pink (#F2A296) as each stroke draws the helium and the level drops,
                      fading back as it refills. Idle: unlit, still, no bubbles. Returns the two
                      line points (p0, p1).
  run4(K, runner)     the kit's own run (stills, the working loop, rotations), then, unless it was
                      a colour map, a check or a partial run: heglow-NN.png, the working loop with
                      the sun, sky, ground and the melt's glow off (the helium glow alone, for its
                      peak) and hemask.png (the sight glass white, everything else black).

Mix A's strengths are the study's (helium-study/vp4_helium_study.py), the peach a touch lower:
violet 0.30, peach 0.34 a stroke, bubbles 0.22 (up by half at the draw); the level drawn 0.48 of the
column (the study's 0.38 read weakly in the smaller tanks), at the kit's sun of 10; the liquid's and bubbles' base colours are scaled by
10 / the concept's sun so they read the same under a stronger sun. Units are tiles.
"""
import math
import os

import bpy
from mathutils import Vector

import rig
from materials import layered

PI = math.pi
LIQ_BASE = "#5A5088"        # the study's: reads as #7E7488 under the kit's sun of 10
BUB_BASE = "#7C6A9C"        # reads as #B6A6C8 (a step darker than the study's #8676A2: lit by a
                            # stronger sun the study's bubbles passed the frost line, L >= 200, sat <= 0.12)
VIO = "#9C86CC"
PEACH = "#F2A296"
BAND = "#9C8CB0"
MIX_A = dict(v=0.30, p=0.34, bub=0.22)     # the study's, the stroke's peach a touch lower: at the
# deepest draw under a sun of 11.5 the study's 0.38 put 1-3 px of the flush at R 255
GLASS_OBJS = []
TANKS = []


# ---------------------------------------------------------------- the kit changes
def _window(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = rig.srgb("#F2EEE8")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Color"].default_value = rig.srgb("#D8D2CC")
    gl.inputs["Roughness"].default_value = 0.18
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs["Fac"].default_value = 0.1
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    return m


def carry(K):
    M, G = K.M, K.GROUP
    # the bands: the kit's own recipe for each kit, in #9C8CB0
    if "he_edge" in M:          # artist B's kit
        band = layered("he_band4", BAND, metal="#5A5260", paint_metal=0.05, paint_rough=0.6, wear=0.3,
                       rust=0.05, dust=0.3, grime=0.4, jitter=0.04)
        K.soften_grain(band)
        K.worn_paint(band, BAND, chips=0.35, under="#5A5260", rust=0.2, wiped=0.0, warm=0.1, mottle=0.0, film=0.25)
    else:                       # artist A's
        band = layered("he_band4", BAND, metal="#6A6070", paint_metal=0.05, paint_rough=0.6, wear=0.3,
                       rust=0.05, dust=0.3, grime=0.4, jitter=0.05)
        K.soften_grain(band)
        K.worn_paint(band, BAND, chips=0.35, under="#6A6070", rust=0.2, wiped=0.0, warm=0.1, sheen=None, mottle=0.0,
                     film=0.25)
    G["he_band4"] = G.get("he_band", ("helium line (grey-violet, bands)", "#B48CFF"))
    M["he_band"] = band
    # the gauge faces: ceramic (artist A's kit has it; artist B's gets the same recipe)
    if "ceramic" not in M:
        c = layered("ceramic", "#B8AE98", metal="#8A8070", paint_metal=0.0, paint_rough=0.7, wear=0.2,
                    rust=0.05, dust=0.4, grime=0.6, jitter=0.05)
        K.soften_grain(c)
        K.worn_paint(c, "#B8AE98", chips=0.3, under="#6A6052", rust=0.3, wiped=0.0, warm=0.4, mottle=0.0, film=0.35)
        M["ceramic"] = c
        G["ceramic"] = ("ceramic", "#F4F0E0")
    M["gauge"] = M["ceramic"]
    # every pane and glass a window
    for k in ("pane", "glass"):
        w = _window(k + "4")
        G[k + "4"] = G.get(k, ("glass", "#A0E0F0"))
        M[k] = w
    _liquid_materials(K)


def dark_flanges(K, fn):
    def he_line(*a, **kw):
        bare = K.M["bare"]
        K.M["bare"] = K.M["dark_steel"]
        try:
            return fn(*a, **kw)
        finally:
            K.M["bare"] = bare
    return he_line


# ---------------------------------------------------------------- the liquid
def _lin(hexc, k):
    c = rig.srgb(hexc)
    return (c[0] * k, c[1] * k, c[2] * k, 1.0)


def _liquid_materials(K):
    K.M["he_glass"] = _window("he_glass")
    K.GROUP["he_glass"] = ("glass", "#A0E0F0")


def _liquid(K, tag, spec=0.12):
    """The liquid (mix A): grey-violet, matte-glossy; emission violet -> peach by 'pk', strength
    'st' times a soft band rising up the column (phase 'ph', seamless)."""
    k = 10.0 / K.SUN_E
    m = bpy.data.materials.new(f"he_liquid_{tag}")
    m.use_nodes = True
    nt = m.node_tree
    L = nt.links
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = _lin(LIQ_BASE, k)
    b.inputs["Roughness"].default_value = 0.5
    b.inputs["Specular IOR Level"].default_value = spec
    st, pk, ph = (nt.nodes.new("ShaderNodeValue") for _ in range(3))
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = 1.0
    wave.inputs["Distortion"].default_value = 1.2
    wave.inputs["Detail"].default_value = 1.0
    L.new(tc.outputs["Object"], wave.inputs["Vector"])
    neg = nt.nodes.new("ShaderNodeMath")
    neg.operation = "MULTIPLY"
    neg.inputs[1].default_value = -1.0
    L.new(ph.outputs[0], neg.inputs[0])
    L.new(neg.outputs[0], wave.inputs["Phase Offset"])
    shim = nt.nodes.new("ShaderNodeMapRange")
    shim.inputs["To Min"].default_value, shim.inputs["To Max"].default_value = 0.8, 1.0
    L.new(wave.outputs["Fac"], shim.inputs["Value"])
    mixn = nt.nodes.new("ShaderNodeMix")
    mixn.data_type = "RGBA"
    mixn.inputs["A"].default_value = rig.srgb(VIO)
    mixn.inputs["B"].default_value = rig.srgb(PEACH)
    L.new(pk.outputs[0], mixn.inputs["Factor"])
    L.new(mixn.outputs["Result"], b.inputs["Emission Color"])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(st.outputs[0], mul.inputs[0])
    L.new(shim.outputs["Result"], mul.inputs[1])
    L.new(mul.outputs[0], b.inputs["Emission Strength"])
    name = f"he_liquid_{tag}"
    K.M[name] = m
    K.GROUP[name] = ("helium (the liquid in the sight glass)", "#C8A0FF")
    return name, (st, pk, ph)


def _bubble(K, tag):
    k = 10.0 / K.SUN_E
    m = bpy.data.materials.new(f"he_bubble_{tag}")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = _lin(BUB_BASE, k)
    b.inputs["Roughness"].default_value = 0.5
    b.inputs["Specular IOR Level"].default_value = 0.15
    st, pk = nt.nodes.new("ShaderNodeValue"), nt.nodes.new("ShaderNodeValue")
    mixn = nt.nodes.new("ShaderNodeMix")
    mixn.data_type = "RGBA"
    mixn.inputs["A"].default_value = rig.srgb(VIO)
    mixn.inputs["B"].default_value = rig.srgb(PEACH)
    nt.links.new(pk.outputs[0], mixn.inputs["Factor"])
    nt.links.new(mixn.outputs["Result"], b.inputs["Emission Color"])
    nt.links.new(st.outputs[0], b.inputs["Emission Strength"])
    name = f"he_bubble_{tag}"
    K.M[name] = m
    K.GROUP[name] = ("helium (the liquid in the sight glass)", "#C8A0FF")
    return name, (st, pk)


def stroke_pulse(centres, rise=0.06, fall=0.36):
    """The draw: fast in at each centre (the level drops), slow out (it refills); loops."""
    def sm(u):
        u = max(0.0, min(1.0, u))
        return u * u * (3 - 2 * u)

    def f(t):
        v = 0.0
        for c in centres:
            d = (t - c) % 1.0
            if d < rise:
                v = max(v, sm(d / rise))
            elif d < rise + fall:
                v = max(v, 1.0 - sm((d - rise) / fall))
        return v
    return f


# ---------------------------------------------------------------- the tank
def sight_tank(K, p0, p1, drawn, r=0.13, level0=0.88, draw=0.48, n_bubbles=10, seed=7, tag=None, spec=0.12):
    """The sight tank set in the helium line from p0 (the foot) to p1 (the head), tiles, model
    space. drawn(t) in [0, 1]: 1 at the deepest draw of a stroke. Returns (p0, p1): the line's
    two ends, inside the tank's stub nozzles."""
    import random
    tag = tag or f"t{len(TANKS)}"
    p0, p1 = Vector(p0), Vector(p1)
    ax = p1 - p0
    Lg = ax.length
    rot = K.along(ax)
    fr = K.pivot(tuple(p0), tuple(rot))
    R = rot.to_matrix()
    # the camera is to the south (-Y): the far half of the glass is toward +Y
    far = R.transposed() @ Vector((0, 1, 0))
    phi = math.atan2(far.y, far.x) if (abs(far.x) + abs(far.y)) > 1e-6 else PI / 2
    stub, cap, fl = 0.05, 0.07, 0.025
    z0g, z1g = stub + cap + fl, Lg - stub - cap - fl            # the glass
    rs = 0.055                                                   # the stubs
    K.cyl((0, 0, stub / 2), rs, stub, "dark_steel", verts=20, bevel=0.004, parent=fr)
    K.cyl((0, 0, Lg - stub / 2), rs, stub, "dark_steel", verts=20, bevel=0.004, parent=fr)
    for zc in (stub + cap / 2, Lg - stub - cap / 2):
        K.cyl((0, 0, zc), r + 0.02, cap, "grey", verts=40, parent=fr)
    for zc in (stub + cap + fl / 2, Lg - stub - cap - fl / 2):
        K.cyl((0, 0, zc), r + 0.04, fl, "dark_steel", verts=40, bevel=0.004, parent=fr)
        for i in range(8):
            a = 2 * PI * (i + 0.5) / 8
            K.cyl(((r + 0.03) * math.cos(a), (r + 0.03) * math.sin(a), zc + (fl / 2 + 0.006) * (1 if zc < Lg / 2 else -1)),
                  0.009, 0.014, "bolt", verts=6, bevel=0, parent=fr)
    g = K.annulus((0, 0, (z0g + z1g) / 2), r - 0.007, r, z1g - z0g, "he_glass", seg=48, parent=fr)
    for a_ in (g,):
        a_.visible_shadow = False
        a_.visible_diffuse = False
        a_.visible_glossy = False
    GLASS_OBJS.append(g)
    rl = r - 0.022
    K.sector((0, 0, (z0g + z1g) / 2), rl + 0.004, r - 0.009, phi - PI / 2 + 0.05, phi + PI / 2 - 0.05,
             z1g - z0g - 0.005, "dark", seg=16, parent=fr)
    for i in range(4):
        a = phi + PI / 4 + i * PI / 2
        K.cyl(((r + 0.025) * math.cos(a), (r + 0.025) * math.sin(a), Lg / 2), 0.009, Lg - 2 * stub - 0.02,
              "dark_steel", verts=8, bevel=0, parent=fr)
    lname, (st, pk, ph) = _liquid(K, tag, spec)
    bname, (bst, bpk) = _bubble(K, tag)
    lp = K.pivot((0, 0, z0g), parent=fr)
    liq = K.cyl((0, 0, 0.5), rl, 1.0, lname, verts=40, bevel=0, parent=lp)
    for o in (liq,):
        o.visible_shadow = False
        o.visible_diffuse = False        # its light shows in the glass; it does not wash the metal
        o.visible_glossy = False
    H = z1g - z0g - 0.015
    rnd = random.Random(seed)
    bub = []
    for i in range(n_bubbles):
        a = phi + PI + rnd.uniform(-0.35 * PI, 0.35 * PI)        # the half toward the camera
        br = rnd.uniform(0.016, 0.024)
        rr = rl - 0.5 * br
        o = K.sphere((0, 0, 0), br, bname, seg=10, parent=fr)
        o.visible_shadow = False
        o.visible_diffuse = False
        o.visible_glossy = False
        bub.append(dict(o=o, x=rr * math.cos(a), y=rr * math.sin(a), r=br, u=rnd.random(), k=rnd.choice((1, 1, 2)),
                        w=rnd.uniform(0.004, 0.01), wp=rnd.random(), ta=a))

    def pose(t, on):
        d = drawn(t) if on else 0.0
        lv = level0 - draw * d
        lp.scale = (1, 1, H * lv)
        top = z0g + H * lv
        for b in bub:
            z = z0g + 0.02 + ((b["u"] + b["k"] * t) % 1.0) * H
            s_ = 0.8 + 0.45 * (z - z0g) / H
            wob = b["w"] * math.sin(2 * PI * (2 * t + b["wp"]))
            b["o"].location = (b["x"] - math.sin(b["ta"]) * wob, b["y"] + math.cos(b["ta"]) * wob, z)
            b["o"].scale = (s_, s_, s_)
            b["o"].hide_render = (not on) or z + b["r"] * s_ > top - 0.008
        st.outputs[0].default_value = (MIX_A["v"] + MIX_A["p"] * d) if on else 0.0
        pk.outputs[0].default_value = d
        ph.outputs[0].default_value = 2 * PI * t
        bst.outputs[0].default_value = MIX_A["bub"] * (1 + 0.5 * d) if on else 0.0
        bpk.outputs[0].default_value = d
    K.ANIM.append(pose)
    TANKS.append(dict(tag=tag, p0=list(p0), p1=list(p1), r=r, length=Lg))
    return tuple(p0), tuple(p1)


# ---------------------------------------------------------------- the extra renders
def run4(K, runner, meta, nf):
    meta = dict(meta, helium_glass=dict(mix="A", tanks=TANKS))
    runner(meta, nf=nf)
    if K.COLMAP or K.ONLY is not None or getattr(K, "CHECK", False):
        return
    nf = K.NF_ARG or nf
    sc = K.sc
    objs = bpy.data.objects
    sun = [o for o in objs if o.type == "LIGHT"]
    bg = sc.world.node_tree.nodes["Background"]
    keep_bg = bg.inputs["Strength"].default_value
    hide = [o for o in objs if o.name.startswith(("ground", "bounce"))]
    for o in sun + hide:
        o.hide_render = True
    bg.inputs["Strength"].default_value = 0.0
    K.ROOT.rotation_euler = (0, 0, 0)
    for f in range(nf):
        K.pose(f / nf, True)
        for sock, _, _ in K.GLOWS:          # the melt's glow off: the helium's alone
            sock.default_value = 0.0
        rig.render(os.path.join(K.OUT, f"heglow-{f:02d}.png"))
    # the mask: the sight glass white, everything else black, no light
    black = bpy.data.materials.new("mask_black")
    white = bpy.data.materials.new("mask_white")
    for m_, c_ in ((black, (0, 0, 0, 1)), (white, (1, 1, 1, 1))):
        m_.use_nodes = True
        nt = m_.node_tree
        nt.nodes.remove(nt.nodes["Principled BSDF"])
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = c_
        nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    K.pose(0.0, False)
    gl = set(o.name for o in GLASS_OBJS)
    for o in K.OBJS:
        if o.type != "MESH":
            continue
        for i in range(len(o.data.materials)):
            o.data.materials[i] = white if o.name in gl else black
    for o in K.STAINS:
        o.hide_render = True
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.cycles.samples = 8
    rig.render(os.path.join(K.OUT, "hemask.png"))
    bg.inputs["Strength"].default_value = keep_bg
    print("helium glass extras: done")
