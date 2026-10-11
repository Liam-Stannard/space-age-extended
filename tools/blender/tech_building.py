"""A building's technology icon, rendered from its signed-off model: nothing remodelled.

    BLENDER=/usr/bin/blender tools/blender/render-icons.sh tools/blender/tech_building.py \\
        <out-dir> <tech-name> [<config.json>]

<config.json> (default concept/technology/tech_buildings.json) maps tech names
to their building and how it is shown:

  model        the building's model script (repo-relative)
  yaw          deg the whole building turns on the ground, about its centre,
               on top of whatever its own --icon mode does (vanilla's building
               technologies stand corner-on: tech_rig.py)
  pose         frame to pose the model's animation at (calls its pose(f)), or null
  calls        [[function, args...]]: the model's own functions to call first (a pose
               of a part the main pose() does not move)
  show         PARTS groups to make visible beyond the icon mode's own
  show_objects single objects to make visible (one part of a group)
  emit         {material: hex}: an emission colour set on a material -- the
               Gas Pump's sight glass carries a neutral grey the engine tints in
               game; a still picture has no engine, so the colour is put in here
  heap         {loc: [x, y], r, h}: a heap of kamacite fines on the ground beside
               the building (Vacuum sintering), in the fines icon's material
  world        world fill strength, if the icon wants other than the model's
  sun          a factor on the sun's strength
  mat_inputs   {material: {Principled input: value or hex}}: a material changed for
               the picture (the Gas Pump's sight glass made clear, so its contents show)

How: the model runs exactly as `render.sh <model> --icon` runs it, builds its
scene, poses and shows itself as its icon mode does, and calls rig.render for
its icon. That call is caught here: the game projection's Y stretch is taken
off (a technology icon is a picture, not a sprite on the game's ground), the
building turned by yaw, posed, lit and shadowed as tech_rig.py says, framed and
rendered at 256/128/64/32. Then the run ends, as the icon mode's would.

The models' shading points read world Y divided back by the stretch, so with the
stretch off their surface patterns run 0.87 as long north-south -- surface
grain only; no part moves or changes size.
"""
import json
import math
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import bmesh  # noqa: E402
import bpy  # noqa: E402

import rig  # noqa: E402
import tech_rig  # noqa: E402  (holds the real rig.render before the hook replaces it)


def _args():
    argv = sys.argv[sys.argv.index("--") + 1:]
    out, name = argv[0], argv[1]
    cfg = argv[2] if len(argv) > 2 else os.path.join(REPO, "concept", "technology", "tech_buildings.json")
    return out, name, json.load(open(cfg))[name]


OUT, NAME, CFG = _args()


class _Done(Exception):
    pass


def _heap(cfg):
    """A cone of kamacite fines, as the fines icon builds it (concept/items/kamacite:
    the powder in teal, hsv(174, .20, .50), its worn face hsv(174, .12, .76))."""
    import colorsys
    from mathutils import noise, Vector
    from materials import layered

    def hsv(h, s, v):
        r, g, b = colorsys.hsv_to_rgb(h / 360, s, v)
        return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))
    mat = layered("fines", hsv(174, 0.20, 0.50), metal=hsv(174, 0.12, 0.76), paint_metal=0.3,
                  paint_rough=0.8, wear=0.1, rust=0.03, dust=0.0, grime=0.4, jitter=0.05)
    R, H = cfg["r"], cfg["h"]
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, radius=1.0)
    for v in bm.verts:
        r = min(1.0, math.hypot(v.co.x, v.co.y))
        if v.co.z <= 0:
            v.co.x, v.co.y, v.co.z = v.co.x * R, v.co.y * R, 0.0
            continue
        prof = (1 - r) * (1 - 0.12 * (1 - r) ** 8)
        jit = 1 + 0.06 * noise.noise(v.co * 3.0 + Vector((4, 1, 7)))
        v.co.x, v.co.y = v.co.x * R * jit, v.co.y * R * jit
        v.co.z = H * prof * (1 + 0.05 * noise.noise(v.co * 14.0))
    me = bpy.data.meshes.new("fines_heap")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("fines_heap", me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (cfg["loc"][0], cfg["loc"][1], 0.0)
    return ob


def _visible_meshes():
    out = []
    for o in bpy.context.scene.objects:
        if o.type not in ("MESH", "CURVE") or o.hide_render or o.is_shadow_catcher:
            continue
        if not o.visible_camera or o.name.startswith("bounce"):
            continue
        out.append(o)
    return out


def hook(path, *a, **k):
    g = sys._getframe(1).f_globals            # the model's own globals
    sc = bpy.context.scene
    if os.environ.get("TECH_OWNCAM"):            # trial: the icon mode's own picture, untouched
        sc.render.resolution_x = sc.render.resolution_y = 256
        tech_rig._render(os.path.join(OUT, "owncam.png"))
        lights = [(o.name, o.data.type, round(o.data.energy, 2), o.hide_render) for o in sc.objects if o.type == "LIGHT"]
        print("LIGHTS", lights, "exposure", sc.view_settings.exposure, sc.view_settings.look)
    if CFG.get("pose") is not None and "pose" in g:
        g["pose"](CFG["pose"])
    for fn, *args in CFG.get("calls", ()):
        g[fn](*args)
    for grp in CFG.get("show", ()):
        for o in g.get("PARTS", {}).get(grp, ()):
            o.hide_render = False
    for oname in CFG.get("show_objects", ()):
        bpy.data.objects[oname].hide_render = False
    for mname, hexcol in CFG.get("emit", {}).items():
        m = bpy.data.materials.get(mname)
        if m:
            b = m.node_tree.nodes["Principled BSDF"]
            if not b.inputs["Emission Color"].is_linked:
                b.inputs["Emission Color"].default_value = rig.srgb(hexcol)
            else:
                # a fill whose value pattern drives the emission: tint it by multiplying in
                t = m.node_tree
                src = b.inputs["Emission Color"].links[0].from_socket
                mul = t.nodes.new("ShaderNodeMix")
                mul.data_type = "RGBA"
                mul.blend_type = "MULTIPLY"
                mul.inputs[0].default_value = 1.0
                t.links.new(src, mul.inputs[6])
                mul.inputs[7].default_value = rig.srgb(hexcol)
                t.links.new(mul.outputs[2], b.inputs["Emission Color"])
    for mname, inputs in CFG.get("mat_inputs", {}).items():
        b = bpy.data.materials[mname].node_tree.nodes["Principled BSDF"]
        for k, v in inputs.items():
            b.inputs[k].default_value = rig.srgb(v) if isinstance(v, str) else v
    if "sun" in CFG:
        for o in sc.objects:
            if o.type == "LIGHT" and o.data.type == "SUN":
                o.data.energy *= CFG["sun"]
    if "world" in CFG:
        sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = CFG["world"]
    # the game projection off, the building turned on the ground
    st = bpy.data.objects.get("STRETCH")
    if st and not os.environ.get("TECH_KEEPSTRETCH"):
        st.scale = (1.0, 1.0, 1.0)
        if not os.environ.get("TECH_NOYAW"):
            st.rotation_euler.z += math.radians(CFG.get("yaw", 0.0))
    # the models' own shadow catchers and grounds off: tech_rig lays its own
    # (meshes only: the sun reads is_shadow_catcher True too, and hiding it was round 2's
    # near-black buildings)
    for o in sc.objects:
        if o.type == "MESH" and o.is_shadow_catcher:
            o.hide_render = True
    objs = _visible_meshes()
    if os.environ.get("TECH_DEBUG"):
        print("film_transparent", sc.render.film_transparent, "world", sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value)
        for o in sc.objects:
            if o.type in ("MESH", "CURVE") and not o.hide_render:
                mats = [m.name for m in o.data.materials if m] if hasattr(o.data, "materials") else []
                grp = [k for k, v in g.get("PARTS", {}).items() if o in v]
                print("VIS", o.name, tuple(round(d, 2) for d in o.dimensions), "cam", o.visible_camera,
                      "catch", o.is_shadow_catcher, "hold", o.is_holdout, mats[:3], grp)
        raise _Done()
    if "heap" in CFG:
        objs.append(_heap(CFG["heap"]))
    if not os.environ.get("TECH_NOFLOOR"):
        tech_rig.shadow_floor()
    bpy.context.view_layer.update()
    if os.environ.get("TECH_OWNCAM_AFTER"):      # trial: the icon mode's camera, after the changes above
        sc.render.resolution_x = sc.render.resolution_y = 256
        tech_rig._render(os.path.join(OUT, "owncam-after.png"))
    framing = tech_rig.render_sizes(NAME, objs, OUT, "building")
    tech_rig.declare(OUT, [NAME], framing)
    raise _Done()


rig.render = hook
model = os.path.join(REPO, CFG["model"])
sys.argv = [sys.argv[0], "--", os.path.join(OUT, "_model"), "--icon"]
os.makedirs(os.path.join(OUT, "_model"), exist_ok=True)
sys.path.insert(0, os.path.dirname(model))
try:
    runpy.run_path(model, run_name="__main__")
    raise SystemExit(f"tech_building: {CFG['model']} finished without rendering an icon")
except _Done:
    pass
