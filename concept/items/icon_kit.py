"""Small shared pieces for the item icon scripts (concept/items/<family>/*_icons.py).

Geometry helpers (a bmesh linked as an object, placing, lifting a build onto the
floor, a lathe), and the two finishes the fluid icons need that materials.layered
does not make: a glossy liquid or atom, and an emissive mask laid over an existing
material. Imported inside Blender, after the script has put tools/blender and
concept/items on sys.path.
"""
import colorsys
import math

import bmesh
import bpy
from mathutils import Vector

import rig
from materials import _G


def hsv(h, s, v):
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360, s, v)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def link(bm, name, mats, smooth):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def place(ob, loc=(0, 0, 0), rot=(0, 0, 0)):
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def lift(objs, floor=0.0):
    """Move a build up (or down) so its lowest evaluated point sits on z = floor:
    the bounce floor under it then lights it as it lights the kamacite family."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    zmin = None
    for o in objs:
        if o.type not in ("MESH", "CURVE"):
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        for v in me.vertices:
            z = (ev.matrix_world @ v.co).z
            zmin = z if zmin is None else min(zmin, z)
        ev.to_mesh_clear()
    if zmin is None:
        return objs
    for o in objs:
        if o.parent is None:
            o.location.z += floor - zmin
    return objs


def lathe(name, profile, mats, segments=64, smooth=True, cap_top=False, cap_bottom=False):
    """A surface of revolution about +Z from profile [(r, z), ...], bottom to top.
    r = 0 at an end closes it to a point."""
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        ring = []
        n = 1 if r < 1e-6 else segments
        for i in range(n):
            a = 2 * math.pi * i / segments
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(ring)
    for lo, hi in zip(rings, rings[1:]):
        if len(lo) == 1 and len(hi) == 1:
            continue
        for i in range(segments):
            j = (i + 1) % segments
            if len(lo) == 1:
                bm.faces.new((lo[0], hi[i], hi[j]))
            elif len(hi) == 1:
                bm.faces.new((lo[i], lo[j], hi[0]))
            else:
                bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    if cap_bottom and len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if cap_top and len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return link(bm, name, mats, smooth)


def glossy(name, hexcol, rough=0.18, coat=1.0, coat_rough=0.06, metallic=0.0, rim=None, sss=0.0):
    """A glossy, lacquered body: a liquid drop, an atom. The sun's highlight comes
    from the coat; rim (hex, strength) darkens or tints toward the silhouette, as
    vanilla's drops do (their edges are their deepest colour)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    g = _G(m)
    bsdf = g.n["Principled BSDF"]
    col = rig.srgb(hexcol)
    if rim:
        face = g.node("ShaderNodeLayerWeight", Blend=0.45).outputs["Facing"]
        col = g.mixc(g.math("MULTIPLY", face, rim[1], clamp=True), col, rig.srgb(rim[0]))
        g.l.new(col, bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = col
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Coat Weight"].default_value = coat
    bsdf.inputs["Coat Roughness"].default_value = coat_rough
    if sss:
        bsdf.inputs["Subsurface Weight"].default_value = sss
    return m


def add_glow(mat, mask_fn, colours, strength):
    """Lay emission over a material where mask_fn(g) -> float socket (0..1) is high.
    colours: (dim hex, bright hex), mixed by the mask, so the brightest part of a
    vein or a melt is its whitest."""
    g = _G(mat)
    bsdf = g.n["Principled BSDF"]
    mask = mask_fn(g)
    col = g.mixc(mask, rig.srgb(colours[0]), rig.srgb(colours[1]))
    g.l.new(col, bsdf.inputs["Emission Color"])
    g.l.new(g.math("MULTIPLY", mask, strength), bsdf.inputs["Emission Strength"])
    return mat


def obj_coords(g):
    return g.node("ShaderNodeTexCoord").outputs["Object"]


def flat(name, hexcol, rough=0.5, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rig.srgb(hexcol)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    return m


def unit(v):
    return Vector(v).normalized()
