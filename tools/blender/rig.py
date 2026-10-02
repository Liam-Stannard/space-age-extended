"""Shared Factorio render rig: camera, sun, colour management, passes.

Everything a building model needs to come out in the game's projection. One
Blender unit is one tile. Models are built normally (Z up, north = +Y) and
parented to the turntable inside STRETCH, which scales world Y by
1/sin(ELEVATION) so a ground square projects as a square -- Factorio draws the
ground top-down and un-foreshortened.

Calibration, measured off vanilla rather than copied from a forum:
  ELEVATION  a round pipe is 53 px thick east-west, ~47 px north-south
             (base/graphics/entity/pipe), so sin(elev) = 47/53 -> ~62 deg; 60 used.
  SUN        from the template's lightning-collector shadow, kx 0.79 / ky 0.25:
             a point h above its foot lands kx*h' right and ky*h' up the screen,
             where h' is its own screen height.
"""
import math
import bpy
from mathutils import Vector

ELEVATION = math.radians(60.0)
PX_PER_TILE = 64                     # scale 0.5 source art
SS = 4                               # render at SS x, downsample after (downsample.py):
                                     # texture detail survives and no denoiser smears it
SHADOW_KX, SHADOW_KY = 0.79, 0.25


def srgb(hexstr):
    """Hex sRGB -> linear RGBA, for a base colour."""
    h = hexstr.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 48
    sc.cycles.use_denoising = False
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.color_depth = "8"
    sc.view_settings.view_transform = "Standard"
    # the forum setup's camera grade: a film-style contrast look and a little
    # under-exposure. Pulls the midtones down without clipping the shadows,
    # which the hand-rolled tone curve (grade.py) did
    sc.view_settings.look = "Medium High Contrast"
    sc.view_settings.exposure = -0.3
    sc.render.filter_size = 1.0          # crisp at sprite size
    world = bpy.data.worlds.new("world")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.62, 0.56, 0.48, 1)  # warm fill: vanilla's shadows are
    bg.inputs["Strength"].default_value = 0.14                # coloured, never black
    return sc


def stretch_root():
    root = bpy.data.objects.new("STRETCH", None)
    bpy.context.scene.collection.objects.link(root)
    root.scale = (1.0, 1.0 / math.sin(ELEVATION), 1.0)
    return root


def turntable(stretch):
    """The root a model builds under: an empty inside STRETCH, turned per direction.

    contract.each_direction turns it about the vertical axis with the camera and
    sun fixed. It turns inside the stretch, not with it: STRETCH's scale is the
    projection, and has to stay on world Y whichever way the building faces.
    """
    turn = bpy.data.objects.new("TURN", None)
    bpy.context.scene.collection.objects.link(turn)
    turn.parent = stretch
    return turn


def camera(width_px, height_px, centre_px=None, ss=SS):
    """Ortho camera, world origin at pixel centre_px (default: canvas centre).

    Sizes are final sprite pixels; the render itself is ss times larger.
    """
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = width_px * ss, height_px * ss
    sc.render.resolution_percentage = 100
    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = max(width_px, height_px) / PX_PER_TILE
    cam_data.clip_start, cam_data.clip_end = 0.1, 200
    cam = bpy.data.objects.new("cam", cam_data)
    sc.collection.objects.link(cam)
    tilt = math.pi / 2 - ELEVATION          # from looking straight down
    cam.rotation_euler = (tilt, 0, 0)
    d = 50.0
    cam.location = (0, -d * math.sin(tilt), d * math.cos(tilt))
    if centre_px is not None:
        big = max(width_px, height_px)
        cx, cy = centre_px
        cam_data.shift_x = (width_px / 2 - cx) / big
        cam_data.shift_y = (cy - height_px / 2) / big
    sc.camera = cam
    return cam


def sun(strength=6.0):
    """Sun whose ground shadows match vanilla's kx/ky, in screen terms."""
    s, c = math.sin(ELEVATION), math.cos(ELEVATION)
    # a pole of height h is h*c tiles tall on screen; its shadow tip lands
    # kx*h*c right and ky*h*c up the screen. Up the screen by u tiles is world
    # +Y by u/s on the (unstretched) ground plane.
    lx = SHADOW_KX * c
    ly = SHADOW_KY * c / s
    travel = Vector((lx, ly, -1.0)).normalized()     # direction light moves
    data = bpy.data.lights.new("sun", "SUN")
    data.energy = strength
    data.angle = math.radians(5.0)             # soft-edged shadows, still sharp enough to glint
    obj = bpy.data.objects.new("sun", data)
    bpy.context.scene.collection.objects.link(obj)
    obj.rotation_euler = travel.to_track_quat("-Z", "Y").to_euler()
    return obj


def bounce_ground(size=12):
    """An invisible warm floor that only lights the machine from below.

    The trick from the Factorio forum setup: the camera never sees it, but its
    bounce warms every underside and recess, which is where vanilla's dark tones
    get their colour.
    """
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, -0.002))
    g = bpy.context.active_object
    g.name = "bounce"
    m = bpy.data.materials.new("bounce")
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = srgb("#6A5440")
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
    g.data.materials.append(m)
    g.visible_camera = False
    g.visible_shadow = False
    return g


def ground_catcher(size=12):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    g = bpy.context.active_object
    g.name = "ground"
    g.is_shadow_catcher = True
    return g


def render(path):
    sc = bpy.context.scene
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
