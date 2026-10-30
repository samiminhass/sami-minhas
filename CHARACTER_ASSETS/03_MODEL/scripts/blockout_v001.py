"""Primary blockout v001 for CHR01_MILA and CHR02_BOREK, with the AUD-001 review renders.

Run with the studio Blender build (STUDIO_DIRECTIVES/setup_blender.sh):
    ~/.blender-venv/bin/python CHARACTER_ASSETS/03_MODEL/scripts/blockout_v001.py
Dimensions follow Character Bible v0.6, sections 3C, 4C and 8A. Units are metres, Z-up, characters face -Y.
"""
import json
import math
import os

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "BLOCKOUT_v001")
RAW = os.path.join(OUT, "renders", "raw")
SHEETS = os.path.join(OUT, "renders")
REFS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "02_REFERENCE", "source_images")
os.makedirs(RAW, exist_ok=True)

PALETTE = {
    "MilaSkin": "#E8B48F", "MilaHair": "#1C1A18", "Coral": "#C4613A", "Cream": "#F2E6CE",
    "Denim": "#5B7A9A", "ShoeRed": "#C13B2A", "Sole": "#E8E0D0", "Bunny": "#D4A574",
    "Stitch": "#5A3A22", "EyeWhite": "#F0EDE8", "Iris": "#2A1A10", "BorekSkin": "#D99A7E",
    "Nose": "#C46060", "BorekHair": "#3D2B1A", "Jacket": "#E8DCC8", "Apron": "#8B7355",
    "Trousers": "#6B2D3A", "Clog": "#8A5A35", "Bread": "#A67C52", "Floor": "#8C857C",
}


def srgb_to_linear(hex_colour):
    h = hex_colour.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


def material(key):
    name = f"MAT_BLK_{key}"
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    colour = srgb_to_linear(PALETTE[key])
    bsdf.inputs["Base Color"].default_value = colour
    bsdf.inputs["Roughness"].default_value = 0.25 if key in ("EyeWhite", "Iris") else 0.6
    m.diffuse_color = colour
    return m


# ---------- geometry helpers ----------

def _activate(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o


def _finish(o, name, key, coll):
    o.name = name
    o.data.name = name
    for c in list(o.users_collection):
        c.objects.unlink(o)
    coll.objects.link(o)
    _activate(o)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    o.data.shade_smooth()
    o.data.materials.clear()
    o.data.materials.append(material(key))
    return o


def _join(parts):
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    return bpy.context.active_object


def ellipsoid(coll, name, key, loc, radii, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1, location=loc,
                                         rotation=[math.radians(a) for a in rot])
    o = bpy.context.active_object
    o.scale = radii
    return _finish(o, name, key, coll)


def limb(coll, name, key, p1, p2, r1, r2):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r1, radius2=r2, depth=d.length,
                                    end_fill_type="NOTHING", location=(p1 + p2) / 2)
    o = bpy.context.active_object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    parts = [o]
    for p, r in ((p1, r1), (p2, r2)):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=r, location=p)
        parts.append(bpy.context.active_object)
    return _finish(_join(parts), name, key, coll)


def cone(coll, name, key, loc, r_bottom, r_top, depth, yscale):
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=r_bottom, radius2=r_top, depth=depth, location=loc)
    o = bpy.context.active_object
    o.scale = (1, yscale, 1)
    return _finish(o, name, key, coll)


def tube(coll, name, key, pts, r, radii=None):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 4
    cu.resolution_u = 12
    cu.use_fill_caps = True
    sp = cu.splines.new("NURBS")
    sp.points.add(len(pts) - 1)
    for i, (pt, c) in enumerate(zip(sp.points, pts)):
        pt.co = (c[0], c[1], c[2], 1.0)
        pt.radius = radii[i] if radii else 1.0
    sp.use_endpoint_u = True
    sp.order_u = min(4, len(pts))
    o = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(o)
    _activate(o)
    bpy.ops.object.convert(target="MESH")
    return _finish(bpy.context.active_object, name, key, coll)


def front_shell(coll, name, key, z_top, z_bot, rx_top, ry_top, rx_bot, ry_bot, yoff, thickness=0.015):
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    n = 32
    rings = []
    for z, rx, ry in ((z_top, rx_top, ry_top), (z_bot, rx_bot, ry_bot)):
        rings.append([bm.verts.new((rx * math.cos(math.pi + math.pi * i / n),
                                    yoff + ry * math.sin(math.pi + math.pi * i / n), z))
                      for i in range(n + 1)])
    for i in range(n):
        bm.faces.new((rings[0][i], rings[0][i + 1], rings[1][i + 1], rings[1][i]))
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    mod = o.modifiers.new("Solidify", "SOLIDIFY")
    mod.thickness = thickness
    _activate(o)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return _finish(o, name, key, coll)


def stitch_x(coll, name, key, centre, size, width, thick):
    parts = []
    for ang in (45, -45):
        bpy.ops.mesh.primitive_cube_add(size=1, location=centre, rotation=(0, math.radians(ang), 0))
        o = bpy.context.active_object
        o.scale = (size, thick, width)
        parts.append(o)
    return _finish(_join(parts), name, key, coll)


SIDES = ((1, "L"), (-1, "R"))  # character's left is +X when facing -Y


# ---------- characters ----------

def build_mila(coll):
    P = "CHR01_MILA_"
    ellipsoid(coll, P + "Head", "MilaSkin", (0, 0, 0.995), (0.135, 0.13, 0.155))  # crown 1.15, chin 0.84
    ellipsoid(coll, P + "HairCap", "MilaHair", (0, 0.045, 1.03), (0.165, 0.15, 0.165))  # hair top 1.195
    ellipsoid(coll, P + "HairBangs", "MilaHair", (0, -0.085, 1.10), (0.12, 0.025, 0.045))
    for s, side in SIDES:
        ellipsoid(coll, P + f"HairSide_{side}", "MilaHair", (s * 0.15, 0.04, 0.86), (0.045, 0.055, 0.12))
        ellipsoid(coll, P + f"Ear_{side}", "MilaSkin", (s * 0.132, 0.0, 0.97), (0.02, 0.035, 0.045))
        ellipsoid(coll, P + f"Eye_{side}", "EyeWhite", (s * 0.052, -0.108, 0.985), (0.03, 0.03, 0.03))
        ellipsoid(coll, P + f"Iris_{side}", "Iris", (s * 0.052, -0.136, 0.985), (0.019, 0.006, 0.019))
        ellipsoid(coll, P + f"Brow_{side}", "MilaHair", (s * 0.055, -0.114, 1.035), (0.028, 0.006, 0.006))
    ellipsoid(coll, P + "Nose", "MilaSkin", (0, -0.128, 0.952), (0.016, 0.016, 0.014))
    ellipsoid(coll, P + "Mouth", "Iris", (0, -0.106, 0.905), (0.022, 0.004, 0.004))
    limb(coll, P + "Neck", "MilaSkin", (0, 0, 0.76), (0, 0.005, 0.86), 0.04, 0.04)

    cone(coll, P + "Tunic", "Coral", (0, 0, 0.56), 0.18, 0.115, 0.46, 0.72)  # hem 0.33, top 0.79
    ellipsoid(coll, P + "Shoulders", "Coral", (0, 0, 0.765), (0.14, 0.085, 0.05))
    # Right arm crosses the body to hold the bunny; left arm supports it from below.
    limb(coll, P + "Sleeve_R", "Coral", (-0.12, 0, 0.765), (-0.125, -0.035, 0.67), 0.042, 0.038)
    limb(coll, P + "UpperArm_R", "Cream", (-0.125, -0.035, 0.67), (-0.13, -0.07, 0.58), 0.033, 0.031)
    limb(coll, P + "Forearm_R", "Cream", (-0.13, -0.07, 0.58), (0.05, -0.17, 0.56), 0.031, 0.027)
    ellipsoid(coll, P + "Hand_R", "MilaSkin", (0.06, -0.175, 0.565), (0.03, 0.025, 0.035))
    limb(coll, P + "Sleeve_L", "Coral", (0.12, 0, 0.765), (0.14, -0.02, 0.67), 0.042, 0.038)
    limb(coll, P + "UpperArm_L", "Cream", (0.14, -0.02, 0.67), (0.17, -0.04, 0.58), 0.033, 0.031)
    limb(coll, P + "Forearm_L", "Cream", (0.17, -0.04, 0.58), (0.15, -0.16, 0.46), 0.031, 0.027)
    ellipsoid(coll, P + "Hand_L", "MilaSkin", (0.15, -0.165, 0.45), (0.03, 0.025, 0.035))

    for s, side in SIDES:
        limb(coll, P + f"Capri_{side}", "Denim", (s * 0.06, 0, 0.42), (s * 0.072, -0.005, 0.165), 0.058, 0.05)
        limb(coll, P + f"Shin_{side}", "MilaSkin", (s * 0.072, -0.005, 0.17), (s * 0.078, 0, 0.075), 0.03, 0.026)
        ellipsoid(coll, P + f"Shoe_{side}", "ShoeRed", (s * 0.08, -0.03, 0.045), (0.05, 0.095, 0.038))
        ellipsoid(coll, P + f"Sole_{side}", "Sole", (s * 0.08, -0.03, 0.018), (0.053, 0.098, 0.018))

    tube(coll, P + "Braid", "MilaHair",
         [(-0.09, 0.07, 0.93), (-0.15, 0.02, 0.80), (-0.185, -0.02, 0.65),
          (-0.20, -0.03, 0.50), (-0.21, -0.02, 0.36), (-0.215, -0.01, 0.27)],
         0.034, radii=[1, 1, 0.95, 0.9, 0.8, 0.7])
    ellipsoid(coll, P + "BraidTuft", "MilaHair", (-0.215, -0.01, 0.215), (0.04, 0.035, 0.07))

    # Bunny prop (about 0.30 m), held on Mila's left side as in the reference.
    ellipsoid(coll, "PRP_Bunny_Body", "Bunny", (0.11, -0.135, 0.53), (0.065, 0.055, 0.095))
    ellipsoid(coll, "PRP_Bunny_Head", "Bunny", (0.12, -0.15, 0.655), (0.06, 0.055, 0.055))
    ellipsoid(coll, "PRP_Bunny_Ear_R", "Bunny", (0.085, -0.15, 0.73), (0.022, 0.012, 0.06), rot=(0, -15, 0))
    ellipsoid(coll, "PRP_Bunny_Ear_L", "Bunny", (0.19, -0.14, 0.69), (0.022, 0.012, 0.065), rot=(0, 60, 0))
    ellipsoid(coll, "PRP_Bunny_Leg_R", "Bunny", (0.09, -0.15, 0.43), (0.025, 0.025, 0.055))
    ellipsoid(coll, "PRP_Bunny_Leg_L", "Bunny", (0.14, -0.15, 0.43), (0.025, 0.025, 0.055))
    for x in (0.10, 0.14):
        ellipsoid(coll, f"PRP_Bunny_Eye_{x:.2f}", "Iris", (x, -0.203, 0.665), (0.007, 0.004, 0.007))
    # Crossed-stitch clue (bible 3C): 4 X marks, each ~3.4 cm, 6 mm cord, down the chest seam.
    for i, z in enumerate((0.475, 0.51, 0.545, 0.58), start=1):
        y = -0.135 - 0.055 * math.sqrt(max(0.0, 1 - ((z - 0.53) / 0.095) ** 2)) - 0.002
        stitch_x(coll, f"PRP_Bunny_StitchX_{i}", "Stitch", (0.11, y, z), 0.034, 0.006, 0.004)


def build_borek(coll):
    P = "CHR02_BOREK_"
    ellipsoid(coll, P + "Head", "BorekSkin", (0, 0, 1.355), (0.19, 0.17, 0.195))  # crown 1.55, chin 1.16
    ellipsoid(coll, P + "Jaw", "BorekSkin", (0, -0.08, 1.27), (0.17, 0.12, 0.11))
    for s, side in SIDES:
        ellipsoid(coll, P + f"Ear_{side}", "BorekSkin", (s * 0.19, 0.0, 1.36), (0.03, 0.05, 0.065))
        ellipsoid(coll, P + f"HairTuft_{side}", "BorekHair", (s * 0.175, 0.04, 1.45), (0.05, 0.07, 0.045))
        ellipsoid(coll, P + f"Cheek_{side}", "BorekSkin", (s * 0.11, -0.11, 1.31), (0.07, 0.06, 0.06))
        ellipsoid(coll, P + f"Eye_{side}", "EyeWhite", (s * 0.062, -0.15, 1.40), (0.017, 0.017, 0.017))
        ellipsoid(coll, P + f"Iris_{side}", "Iris", (s * 0.062, -0.166, 1.40), (0.011, 0.004, 0.011))
        ellipsoid(coll, P + f"Brow_{side}", "BorekHair", (s * 0.068, -0.163, 1.435), (0.058, 0.022, 0.022),
                  rot=(0, -s * 12, 0))
        tube(coll, P + f"Mustache_{side}", "BorekHair",
             [(s * 0.0, -0.218, 1.278), (s * 0.06, -0.214, 1.268), (s * 0.11, -0.19, 1.258),
              (s * 0.15, -0.16, 1.276), (s * 0.165, -0.145, 1.315), (s * 0.147, -0.15, 1.342),
              (s * 0.127, -0.16, 1.322)],
             0.024, radii=[1, 1, 0.85, 0.7, 0.55, 0.45, 0.35])
    ellipsoid(coll, P + "Nose", "Nose", (0, -0.19, 1.33), (0.06, 0.055, 0.055))
    ellipsoid(coll, P + "Mustache_C", "BorekHair", (0, -0.215, 1.28), (0.06, 0.03, 0.026))

    ellipsoid(coll, P + "Torso", "Jacket", (0, 0, 0.86), (0.40, 0.33, 0.42))
    ellipsoid(coll, P + "Belly", "Jacket", (0, -0.09, 0.72), (0.34, 0.28, 0.28))
    for s, side in SIDES:
        limb(coll, P + f"UpperArm_{side}", "Jacket", (s * 0.33, -0.02, 1.13), (s * 0.46, -0.25, 0.93), 0.10, 0.092)
    # Crossed arms: right forearm under, left forearm over.
    limb(coll, P + "Forearm_R", "BorekSkin", (-0.46, -0.25, 0.93), (0.24, -0.43, 1.03), 0.09, 0.075)
    ellipsoid(coll, P + "Hand_R", "BorekSkin", (0.27, -0.42, 1.04), (0.07, 0.06, 0.06))
    limb(coll, P + "Forearm_L", "BorekSkin", (0.46, -0.25, 0.93), (-0.24, -0.45, 0.985), 0.09, 0.075)
    ellipsoid(coll, P + "Hand_L", "BorekSkin", (-0.27, -0.44, 0.99), (0.07, 0.06, 0.06))
    front_shell(coll, P + "Apron", "Apron", 0.80, 0.34, 0.42, 0.34, 0.44, 0.38, -0.06)
    for s, side in SIDES:
        limb(coll, P + f"Trouser_{side}", "Trousers", (s * 0.14, 0, 0.48), (s * 0.15, -0.02, 0.21), 0.12, 0.10)
        ellipsoid(coll, P + f"TrouserCuff_{side}", "Trousers", (s * 0.15, -0.02, 0.21), (0.105, 0.105, 0.04))
        limb(coll, P + f"Shin_{side}", "BorekSkin", (s * 0.15, -0.03, 0.21), (s * 0.155, -0.04, 0.10), 0.05, 0.048)
        ellipsoid(coll, P + f"Clog_{side}", "Clog", (s * 0.16, -0.08, 0.06), (0.085, 0.16, 0.06))
    ellipsoid(coll, "PRP_BreadLoaf", "Bread", (0.55, -0.06, 0.66), (0.16, 0.14, 0.15))


CHARACTERS = {
    "CHR01_MILA": dict(build=build_mila, label="Mila", ref="ref_girl_braid.jpg", ref_top=40, ref_sole=577),
    "CHR02_BOREK": dict(build=build_borek, label="Borek", ref="ref_baker.jpg", ref_top=20, ref_sole=575),
}


# ---------- scene, lights, cameras ----------

def new_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "AgX"
    w = bpy.data.worlds.new("WLD_Studio")
    sc.world = w
    if w.node_tree is None:
        w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.18, 0.18, 0.18, 1)
    bg.inputs[1].default_value = 0.6
    return sc


def add_light(name, loc, target, energy, size):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = energy
    ld.size = size
    o = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


def studio_lights(height, cx=0.0):
    t = (cx, 0, height * 0.55)
    add_light("LGT_Key", (cx - 2.2, -3.0, height + 1.8), t, 900, 2.5)
    add_light("LGT_Fill", (cx + 3.0, -2.5, height * 0.7), t, 300, 3.0)
    add_light("LGT_Rim", (cx + 0.5, 3.2, height + 1.5), t, 700, 2.0)


def ortho_camera(cx, cz, scale, resx, resy):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("CAM_Ortho")
    cd.type = "ORTHO"
    cd.ortho_scale = scale
    cd.clip_end = 100
    o = bpy.data.objects.new("CAM_Ortho", cd)
    sc.collection.objects.link(o)
    o.location = (cx, -20, cz)
    o.rotation_euler = (math.radians(90), 0, 0)
    sc.camera = o
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = resx, resy, 100
    return o


def persp_camera(loc, target, lens, resx, resy):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("CAM_TwoShot")
    cd.lens = lens
    o = bpy.data.objects.new("CAM_TwoShot", cd)
    sc.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.camera = o
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = resx, resy, 100
    return o


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def world_verts(o):
    dg = bpy.context.evaluated_depsgraph_get()
    oe = o.evaluated_get(dg)
    me = oe.to_mesh()
    vs = [oe.matrix_world @ v.co for v in me.vertices]
    oe.to_mesh_clear()
    return vs


def build_character(tag, offset=(0, 0, 0), rot_deg=0.0):
    coll = bpy.data.collections.new(tag)
    bpy.context.scene.collection.children.link(coll)
    CHARACTERS[tag]["build"](coll)
    root = bpy.data.objects.new(tag + "_ROOT", None)
    coll.objects.link(root)
    for o in coll.objects:
        if o is not root:
            o.parent = root
    root.location = offset
    root.rotation_euler = (0, 0, math.radians(rot_deg))
    bpy.context.view_layer.update()
    return coll, root


def measure(coll, tag):
    allv = [v for o in coll.objects if o.type == "MESH" for v in world_verts(o)]
    noacc = [v for o in coll.objects if o.type == "MESH" and not o.name.startswith("PRP_") for v in world_verts(o)]
    hv = world_verts(bpy.data.objects[tag + "_Head"])
    crown, chin = max(v.z for v in hv), min(v.z for v in hv)
    top = max(v.z for v in allv)
    return dict(
        crown_m=round(crown, 4), chin_m=round(chin, 4), top_incl_hair_m=round(top, 4),
        head_m=round(crown - chin, 4), heads=round(crown / (crown - chin), 2),
        heads_incl_hair=round(top / (top - chin), 2),
        width_front_m=round(max(v.x for v in allv) - min(v.x for v in allv), 3),
        width_no_accessory_m=round(max(v.x for v in noacc) - min(v.x for v in noacc), 3),
        width_to_height_no_accessory=round((max(v.x for v in noacc) - min(v.x for v in noacc)) / crown, 2),
        rxy=max(math.hypot(v.x, v.y) for v in allv),
        objects=sum(1 for o in coll.objects if o.type == "MESH"),
        faces=sum(len(o.data.polygons) for o in coll.objects if o.type == "MESH"),
    )


# ---------- image helpers ----------

GREY = (150, 150, 150)


def font(size):
    return ImageFont.load_default(size=size)


def on_grey(path):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, GREY + (255,))
    return Image.alpha_composite(bg, im).convert("RGB")


def silhouette(path):
    a = Image.open(path).convert("RGBA").split()[3]
    return Image.merge("RGB", [a.point(lambda v: 255 - v)] * 3)


def sheet(images, labels, title, path):
    w, h = images[0].size
    pad, top = 16, 56
    out = Image.new("RGB", (len(images) * (w + pad) + pad, h + top + pad), (245, 243, 238))
    d = ImageDraw.Draw(out)
    d.text((pad, 12), title, fill=(30, 30, 30), font=font(24))
    for i, (im, lab) in enumerate(zip(images, labels)):
        x = pad + i * (w + pad)
        out.paste(im, (x, top))
        d.text((x + 8, top + 8), lab, fill=(20, 20, 20), font=font(20))
    out.save(path)


# ---------- passes ----------

def character_pass(tag, results):
    new_scene()
    coll, root = build_character(tag)
    m = measure(coll, tag)
    studio_lights(m["top_incl_hair_m"])
    resx, resy = 800, 1000
    scale = max(m["top_incl_hair_m"] * 1.12, 2 * m["rxy"] * 1.08 * resy / resx)
    ortho_camera(0, m["top_incl_hair_m"] * 0.5, scale, resx, resy)
    bpy.context.scene.render.film_transparent = True
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"{tag}_blockout_v001.blend"))

    views = [("front", 0), ("three-quarter", 45), ("side", 90), ("back", 180)]
    for v, a in views:
        root.rotation_euler = (0, 0, math.radians(a))
        render(os.path.join(RAW, f"{tag}_{v}.png"))
    for o in coll.objects:
        if o.name.startswith("PRP_"):
            o.hide_render = True
    for v, a in views[:2]:
        root.rotation_euler = (0, 0, math.radians(a))
        render(os.path.join(RAW, f"{tag}_noaccessory_{v}.png"))

    label = CHARACTERS[tag]["label"]
    raws = [os.path.join(RAW, f"{tag}_{v}.png") for v, _ in views]
    names = [v for v, _ in views]
    colour = [on_grey(p) for p in raws]
    sheet(colour, names, f"{label} blockout v001: neutral studio turnaround (Cycles, orthographic)",
          os.path.join(SHEETS, f"{tag}_turnaround.png"))
    sheet([c.convert("L").convert("RGB") for c in colour], names, f"{label} blockout v001: grayscale",
          os.path.join(SHEETS, f"{tag}_grayscale.png"))
    sil = [silhouette(p) for p in raws] + [silhouette(os.path.join(RAW, f"{tag}_noaccessory_{v}.png"))
                                           for v, _ in views[:2]]
    sheet(sil, names + ["front, no prop", "3/4, no prop"],
          f"{label} blockout v001: black silhouettes and accessory removal", os.path.join(SHEETS, f"{tag}_silhouettes.png"))

    # Reference comparison, both scaled so top-of-figure to sole spans the same height.
    cfg = CHARACTERS[tag]
    ref = Image.open(os.path.join(REFS, cfg["ref"])).convert("RGB")
    ref = ref.crop((0, cfg["ref_top"], ref.width, cfg["ref_sole"]))
    px_per_m = resy / scale
    cz = m["top_incl_hair_m"] * 0.5
    y_top = int(resy / 2 - (m["top_incl_hair_m"] - cz) * px_per_m)
    y_sole = int(resy / 2 - (0 - cz) * px_per_m)
    front = colour[0].crop((0, y_top, resx, y_sole))
    H = 820
    ref = ref.resize((int(ref.width * H / ref.height), H), Image.LANCZOS)
    front = front.resize((int(front.width * H / front.height), H), Image.LANCZOS)
    sheet([ref, front], ["approved reference", "blockout v001 (front ortho)"],
          f"{label}: reference vs blockout, matched top-to-sole height", os.path.join(SHEETS, f"{tag}_vs_reference.png"))
    m.pop("rxy")
    results[tag] = m


def lineup_pass(results):
    new_scene()
    placements = {"CHR01_MILA": -0.85, "CHR02_BOREK": 0.45}
    for tag, x in placements.items():
        build_character(tag, offset=(x, 0, 0))
    studio_lights(1.55, cx=-0.2)
    resx, resy, scale, cx, cz = 1400, 1000, 2.5, 0.03, 0.85
    ortho_camera(cx, cz, scale, resx, resy)
    bpy.context.scene.render.film_transparent = True
    raw = os.path.join(RAW, "lineup_front.png")
    render(raw)
    im = on_grey(raw)
    d = ImageDraw.Draw(im)
    ppm = max(resx, resy) / scale

    def px(x, z):
        return resx / 2 + (x - cx) * ppm, resy / 2 - (z - cz) * ppm

    for tag, x0 in placements.items():
        m = results[tag]
        half = 0.32 if tag == "CHR01_MILA" else 0.66
        k, z = 0, m["crown_m"]
        while z > -1e-6:
            xa, ya = px(x0 - half, z)
            xb, _ = px(x0 + half, z)
            d.line([(xa, ya), (xb, ya)], fill=(200, 30, 30) if k == 0 else (30, 60, 200), width=2)
            d.text((xb + 6, ya - 10), f"{k}", fill=(20, 20, 20), font=font(18))
            k += 1
            z = m["crown_m"] - k * m["head_m"]
        _, yg = px(0, 0)
        tx, _ = px(x0 - half, 0)
        d.text((tx, yg + 12), f"{CHARACTERS[tag]['label']}: {m['heads']} heads skull-only, "
                              f"{m['heads_incl_hair']} incl. hair", fill=(20, 20, 20), font=font(20))
    d.text((16, 12), "Front orthographic head-unit overlay, blockout v001. Red = crown; blue = each head unit "
                     "(crown to chin) down to the floor.", fill=(20, 20, 20), font=font(20))
    im.save(os.path.join(SHEETS, "lineup_head_units.png"))


def projected_px(obj_names, cam, w, h):
    sc = bpy.context.scene
    pts = []
    for n in obj_names:
        for v in world_verts(bpy.data.objects[n]):
            p = world_to_camera_view(sc, cam, v)
            pts.append((p.x * w, (1 - p.y) * h))
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1)


def twoshot_pass(results):
    stagings = {
        "A_mila_near": dict(mila=((-0.12, -1.0, 0), 20), borek=((0.25, 0.7, 0), -15),
                            cam=((0, -4.4, 1.0), (0, 0, 0.8), 55), step=False,
                            label="A: Mila near, Borek mid-ground"),
        "B_borek_near": dict(mila=((-0.28, 0.9, 0), 20), borek=((0.12, -0.9, 0), -15),
                             cam=((0, -4.4, 1.0), (0, 0, 0.8), 55), step=False,
                             label="B: Borek near, Mila far"),
        "C_same_plane": dict(mila=((-0.42, 0, 0.25), 15), borek=((0.38, 0.05, 0), -15),
                             cam=((0, -4.6, 1.0), (0.1, 0, 0.85), 50), step=True,
                             label="C: same plane, Mila on a 25 cm step"),
    }
    full, phone, labels = [], [], []
    for key, st in stagings.items():
        new_scene()
        sc = bpy.context.scene
        build_character("CHR01_MILA", offset=st["mila"][0], rot_deg=st["mila"][1])
        build_character("CHR02_BOREK", offset=st["borek"][0], rot_deg=st["borek"][1])
        fcoll = bpy.data.collections.new("SET")
        sc.collection.children.link(fcoll)
        bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 2, 0))
        _finish(bpy.context.active_object, "SET_Floor", "Floor", fcoll)
        if st["step"]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.42, 0.0, 0.125))
            stp = bpy.context.active_object
            stp.scale = (0.5, 0.5, 0.25)
            _finish(stp, "SET_Step", "Floor", fcoll)
        studio_lights(1.55)
        loc, target, lens = st["cam"]
        cam = persp_camera(loc, target, lens, 720, 1280)
        sc.render.film_transparent = False
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"CHR_twoshot_{key}_blockout_v001.blend"))
        raw = os.path.join(RAW, f"twoshot_{key}.png")
        render(raw)
        stitch = projected_px([f"PRP_Bunny_StitchX_{i}" for i in range(1, 5)], cam, 360, 640)
        one_x = projected_px(["PRP_Bunny_StitchX_2"], cam, 360, 640)
        bunny = projected_px([o.name for o in bpy.data.objects if o.name.startswith("PRP_Bunny_")], cam, 360, 640)
        b_eye = projected_px(["CHR02_BOREK_Eye_L"], cam, 360, 640)
        m_eye = projected_px(["CHR01_MILA_Eye_L"], cam, 360, 640)
        results.setdefault("twoshots", {})[key] = dict(
            label=st["label"], bunny_px_360x640=bunny, bunny_frame_height_pct=round(100 * bunny[1] / 640, 1),
            one_stitch_x_px=one_x, stitch_chain_px=stitch, borek_eye_px=b_eye, mila_eye_px=m_eye)
        im = Image.open(raw).convert("RGB")
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        do = ImageDraw.Draw(ov)
        W, H = im.size
        do.rectangle([0, int(H * 0.80), W, H], fill=(196, 97, 58, 70))
        do.rectangle([int(W * 0.86), int(H * 0.33), W, int(H * 0.80)], fill=(196, 97, 58, 70))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        full.append(im)
        phone.append(im.resize((360, 640), Image.LANCZOS))
        labels.append(st["label"])
    sheet(full, labels, "9:16 two-shot stagings, blockout v001. Shaded bands = approximate platform UI zones.",
          os.path.join(SHEETS, "twoshot_stagings.png"))
    sheet(phone, labels, "Same stagings at 360 x 640 (phone-size proxy)", os.path.join(SHEETS, "twoshot_stagings_360x640.png"))


if __name__ == "__main__":
    results = {"blender": bpy.app.version_string}
    for tag in CHARACTERS:
        character_pass(tag, results)
    lineup_pass(results)
    twoshot_pass(results)
    with open(os.path.join(OUT, "blockout_v001_measurements.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))
