"""Kestrava bakery blockout: builds the set and stand-in characters, renders storyboard frames.

Usage:
  EGL_PLATFORM=surfaceless ~/.blender-venv/bin/python kestrava_blockout.py SHOTS.json OUT_DIR [--blend OUT.blend]

Stand-ins follow Character Bible v0.5 section 8 (1 BU = 1 m, Z-up, characters face -Y).
They are proportion and staging proxies only, not character designs.
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

C = {
    "plaster": (0.30, 0.27, 0.24), "wood_dark": (0.22, 0.14, 0.09), "wood_mid": (0.36, 0.24, 0.14),
    "stone": (0.48, 0.47, 0.45), "whitewash": (0.78, 0.76, 0.70), "cobble": (0.42, 0.41, 0.39),
    "timber": (0.30, 0.20, 0.12), "oven_glow": (1.0, 0.42, 0.08), "flour": (0.90, 0.88, 0.82),
    "sack": (0.74, 0.68, 0.54), "loaf": (0.72, 0.47, 0.22), "loaf_bad": (0.62, 0.38, 0.17),
    "wicker": (0.62, 0.48, 0.28), "sky": (0.58, 0.67, 0.78),
    "m_skin": (0.93, 0.74, 0.60), "m_hair": (0.04, 0.04, 0.05), "m_tunic": (0.93, 0.48, 0.40),
    "m_denim": (0.30, 0.40, 0.55), "m_shoe": (0.75, 0.12, 0.10), "cord": (0.66, 0.52, 0.34),
    "b_skin": (0.88, 0.62, 0.52), "b_jacket": (0.88, 0.84, 0.74), "b_apron": (0.55, 0.58, 0.45),
    "b_trouser": (0.45, 0.15, 0.20), "b_clog": (0.45, 0.30, 0.18), "b_hair": (0.20, 0.12, 0.08),
    "b_nose": (0.90, 0.50, 0.50), "bunny": (0.85, 0.80, 0.68), "stitch": (0.40, 0.26, 0.16),
    "eye_w": (0.95, 0.95, 0.93), "eye_d": (0.05, 0.04, 0.04), "flower": (0.85, 0.75, 0.15),
    "stem": (0.25, 0.45, 0.2), "tray": (0.25, 0.25, 0.27),
}


def coll(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def _finish(o, col, c, parent=None):
    for uc in list(o.users_collection):
        uc.objects.unlink(o)
    c.objects.link(o)
    o.color = (*C[col], 1.0) if isinstance(col, str) else (*col, 1.0)
    if parent is not None:
        o.parent = parent
    return o


def box(c, col, center, dims, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center, rotation=[math.radians(a) for a in rot])
    o = bpy.context.active_object
    o.scale = dims
    return _finish(o, col, c, parent)


def box_span(c, col, x, y, z, parent=None):
    return box(c, col, ((x[0] + x[1]) / 2, (y[0] + y[1]) / 2, (z[0] + z[1]) / 2),
               (x[1] - x[0], y[1] - y[0], z[1] - z[0]), parent=parent)


def sphere(c, col, center, r, scale=(1, 1, 1), rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=center, segments=24, ring_count=12,
                                         rotation=[math.radians(a) for a in rot])
    o = bpy.context.active_object
    o.scale = scale
    bpy.ops.object.shade_smooth()
    return _finish(o, col, c, parent)


def rod(c, col, a, b, r, parent=None):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, location=(a + b) / 2, vertices=16)
    o = bpy.context.active_object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    bpy.ops.object.shade_smooth()
    return _finish(o, col, c, parent)


def cone(c, col, center, r1, r2, depth, parent=None):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth, location=center, vertices=24)
    o = bpy.context.active_object
    bpy.ops.object.shade_smooth()
    return _finish(o, col, c, parent)


def empty(c, name):
    o = bpy.data.objects.new(name, None)
    c.objects.link(o)
    return o


# ---------------------------------------------------------------- set

def build_set():
    c = coll("SET")
    H = 3.4
    box_span(c, "wood_dark", (-3, 3), (-2.5, 2.5), (-0.05, 0))
    box_span(c, "timber", (-3, 3), (-2.5, 2.5), (H, H + 0.05))
    for x in (-2, -0.6, 0.8, 2.2):
        box_span(c, "timber", (x - 0.09, x + 0.09), (-2.5, 2.5), (H - 0.18, H))
    box_span(c, "plaster", (-3, 3), (2.5, 2.6), (0, H))
    box_span(c, "plaster", (-3.1, -3), (-2.5, 2.5), (0, H))
    box_span(c, "plaster", (3, 3.1), (-2.5, 2.5), (0, H))
    # front wall with shop window x[-2.2,-0.4] z[0.7,2.2] and door x[1.2,2.2] z[0,2.1]
    fy = (-2.6, -2.5)
    box_span(c, "plaster", (-3, -2.2), fy, (0, H))
    box_span(c, "plaster", (-2.2, -0.4), fy, (0, 0.7))
    box_span(c, "plaster", (-2.2, -0.4), fy, (2.2, H))
    box_span(c, "plaster", (-0.4, 1.2), fy, (0, H))
    box_span(c, "plaster", (1.2, 2.2), fy, (2.1, H))
    box_span(c, "plaster", (2.2, 3), fy, (0, H))
    for x0, x1 in ((-2.25, -2.15), (-0.45, -0.35)):
        box_span(c, "timber", (x0, x1), (-2.62, -2.48), (0.7, 2.2))
    box_span(c, "timber", (-2.25, -0.35), (-2.62, -2.48), (0.65, 0.72))
    box_span(c, "timber", (-2.25, -0.35), (-2.62, -2.48), (2.18, 2.25))
    # exterior skin of the facade (whitewashed), offset so it does not z-fight
    ey = (-2.64, -2.62)
    box_span(c, "whitewash", (-3.2, -2.25), ey, (0, H + 0.6))
    box_span(c, "whitewash", (-2.25, -0.35), ey, (0, 0.65))
    box_span(c, "whitewash", (-2.25, -0.35), ey, (2.25, H + 0.6))
    box_span(c, "whitewash", (-0.35, 1.2), ey, (0, H + 0.6))
    box_span(c, "whitewash", (1.2, 2.2), ey, (2.1, H + 0.6))
    box_span(c, "whitewash", (2.2, 3.2), ey, (0, H + 0.6))
    box_span(c, "timber", (1.15, 2.25), (-2.7, -2.62), (2.1, 2.2))
    # oven built into back-left wall
    box_span(c, "stone", (-2.95, -1.25), (1.6, 2.5), (0, 2.5))
    box_span(c, "oven_glow", (-2.45, -1.75), (1.57, 1.62), (0.85, 1.35))
    box_span(c, "stone", (-2.6, -1.6), (1.4, 1.6), (0.78, 0.85))
    # counter
    box_span(c, "wood_dark", (-0.6, 1.9), (0.0, 0.6), (0, 0.95))
    box_span(c, "wood_mid", (-0.65, 1.95), (-0.03, 0.63), (0.95, 0.99))
    # roll basket
    bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.12, location=(1.22, 0.3, 1.05), vertices=24)
    _finish(bpy.context.active_object, "wicker", c)
    for dx, dy in ((-0.06, -0.04), (0.06, 0.03), (0.0, 0.07)):
        sphere(c, "loaf", (1.22 + dx, 0.3 + dy, 1.12), 0.05, (1.3, 1, 0.7))
    # tall shelves, back-right
    for z in (0.6, 1.2, 1.8, 2.3):
        box_span(c, "wood_mid", (1.5, 2.9), (2.05, 2.5), (z - 0.04, z))
    for x in (1.5, 2.88):
        box_span(c, "wood_dark", (x - 0.03, x + 0.03), (2.05, 2.5), (0, 2.3))
    for z in (0.6, 1.2, 1.8):
        for i, x in enumerate((1.75, 2.05, 2.35, 2.65)):
            sphere(c, "loaf", (x, 2.28, z + 0.08), 0.1, (1.3, 1, 0.75), rot=(0, 0, 15 * i))
    # flour sacks
    for (x, y, z, s) in ((-0.75, 1.75, 0.28, 1.0), (-0.25, 1.78, 0.28, 1.05), (0.15, 1.8, 0.26, 0.95),
                         (-0.5, 1.8, 0.72, 0.9)):
        sphere(c, "sack", (x, y, z), 0.3, (0.85 * s, 0.6 * s, 0.95 * s))
    # window display stand
    box_span(c, "wood_dark", (-1.95, -0.65), (-2.4, -1.95), (0, 0.72))
    box_span(c, "wood_mid", (-1.6, -1.0), (-2.3, -2.05), (0.72, 0.82))
    for x in (-1.75, -0.85):
        sphere(c, "loaf", (x, -2.17, 0.8), 0.11, (1.3, 1, 0.75))
    # the square outside
    box_span(c, "cobble", (-10, 10), (-16, -2.64), (-0.05, 0))
    for x0, x1, h in ((-8, -3.5, 5.0), (-3.3, 0.6, 6.2), (0.8, 4.2, 5.4), (4.4, 8.5, 6.0)):
        box_span(c, "whitewash", (x0, x1), (-15, -14), (0, h))
        box_span(c, "timber", (x0, x1), (-14.05, -13.95), (h - 0.4, h - 0.25))
        for wx in (x0 + 0.8, (x0 + x1) / 2, x1 - 0.8):
            box_span(c, "timber", (wx - 0.3, wx + 0.3), (-14.06, -13.96), (2.2, 3.2))
    for x0, x1 in ((-10, -8.5), (8.6, 10)):
        box_span(c, "stone", (x0, x1), (-14, -2.7), (0, 4.5))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=0.6, location=(-2.2, -9.0, 0.3), vertices=32)
    _finish(bpy.context.active_object, "stone", c)
    rod(c, "stone", (-2.2, -9.0, 0.6), (-2.2, -9.0, 1.5), 0.12)


# ---------------------------------------------------------------- props

def loaf(c, loc, bad=False, parent=None):
    if bad:
        o = sphere(c, "loaf_bad", loc, 0.12, (1.3, 0.85, 0.6), rot=(14, -10, 25), parent=parent)
        sphere(c, "loaf_bad", (loc[0] + 0.08, loc[1] - 0.03, loc[2] + 0.04), 0.06, parent=parent)
        return o
    return sphere(c, "loaf", loc, 0.12, (1.4, 1, 0.72), parent=parent)


def bunny(c, loc, face=0.0, parent=None):
    root = empty(c, "PRP_Bunny")
    if parent is not None:
        root.parent = parent
    sphere(c, "bunny", (0, 0, 0.07), 0.065, (1, 0.9, 1.15), parent=root)
    sphere(c, "bunny", (0, -0.01, 0.17), 0.055, parent=root)
    rod(c, "bunny", (-0.025, 0, 0.21), (-0.06, 0.02, 0.31), 0.016, parent=root)
    rod(c, "bunny", (0.025, 0, 0.21), (0.07, 0.03, 0.28), 0.016, parent=root)
    box(c, "stitch", (0, -0.06, 0.08), (0.008, 0.01, 0.07), rot=(0, 30, 0), parent=root)
    box(c, "stitch", (0, -0.06, 0.08), (0.008, 0.01, 0.07), rot=(0, -30, 0), parent=root)
    for x in (-0.02, 0.02):
        sphere(c, "eye_d", (x, -0.05, 0.18), 0.007, parent=root)
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(face))
    return root


# ---------------------------------------------------------------- characters

def mila(c, spec):
    rig = empty(c, "CHR01_MILA")
    P = rig
    expr = spec.get("expr", "")
    for x in (-0.07, 0.07):
        box(c, "m_shoe", (x, -0.03, 0.03), (0.09, 0.17, 0.06), parent=P)
        rod(c, "m_denim", (x, 0, 0.06), (x, 0, 0.38), 0.055, parent=P)
    cone(c, "m_tunic", (0, 0, 0.58), 0.19, 0.13, 0.44, parent=P)
    rod(c, "m_skin", (0, 0, 0.78), (0, 0, 0.83), 0.045, parent=P)
    sphere(c, "m_skin", (0, 0, 0.95), 0.145, parent=P)
    sphere(c, "m_hair", (0, 0.045, 0.99), 0.15, (1.04, 1, 0.95), parent=P)
    for x in (-0.05, 0.05):
        sphere(c, "eye_w", (x, -0.128, 0.945), 0.03, parent=P)
        sphere(c, "eye_d", (x, -0.152, 0.945), 0.017, parent=P)
        lift = 0.03 if (expr == "brow_up" and x > 0) else 0.0
        box(c, "m_hair", (x, -0.135, 0.995 + lift), (0.05, 0.015, 0.012), parent=P)
    if spec.get("braid_mustache"):
        rod(c, "m_hair", (0.11, 0.08, 0.93), (0.12, -0.12, 0.89), 0.02, parent=P)
        rod(c, "m_hair", (0.12, -0.155, 0.885), (-0.11, -0.165, 0.895), 0.018, parent=P)
        box(c, "cord", (0.12, -0.03, 0.91), (0.07, 0.07, 0.03), parent=P)
    else:
        rod(c, "m_hair", (0, 0.14, 0.92), (0.02, 0.18, 0.33), 0.035, parent=P)
        for z in (0.8, 0.65, 0.5):
            box(c, "cord", (0.01, 0.17, z), (0.08, 0.07, 0.02), rot=(0, 25, 0), parent=P)
    arms = spec.get("arms", "hold")
    sh_l, sh_r = (0.17, 0, 0.74), (-0.17, 0, 0.74)
    held = None
    if arms == "hold":
        for sh, h in ((sh_l, (0.06, -0.17, 0.6)), (sh_r, (-0.06, -0.17, 0.6))):
            rod(c, "m_tunic", sh, h, 0.04, parent=P)
            sphere(c, "m_skin", h, 0.035, parent=P)
        held = (0, -0.21, 0.52)
    elif arms == "crossed":
        for sh, el in ((sh_l, (0.19, -0.12, 0.6)), (sh_r, (-0.19, -0.12, 0.6))):
            rod(c, "m_tunic", sh, el, 0.04, parent=P)
        rod(c, "m_skin", (0.19, -0.14, 0.63), (-0.15, -0.2, 0.66), 0.035, parent=P)
        rod(c, "m_skin", (-0.19, -0.14, 0.61), (0.15, -0.21, 0.6), 0.035, parent=P)
    elif arms == "shove_side":
        rod(c, "m_tunic", sh_l, (0.55, -0.05, 0.72), 0.04, parent=P)
        rod(c, "m_tunic", sh_r, (-0.2, 0, 0.45), 0.04, parent=P)
        held = (0.62, -0.05, 0.62)
    elif arms == "raise":
        for sh, h in ((sh_l, (0.06, -0.3, 0.95)), (sh_r, (-0.06, -0.3, 0.95))):
            rod(c, "m_tunic", sh, h, 0.04, parent=P)
            sphere(c, "m_skin", h, 0.035, parent=P)
        held = (0, -0.36, 0.86)
    else:
        for sh, h in ((sh_l, (0.21, 0, 0.45)), (sh_r, (-0.21, 0, 0.45))):
            rod(c, "m_tunic", sh, h, 0.04, parent=P)
            sphere(c, "m_skin", h, 0.035, parent=P)
    if spec.get("bunny") and held:
        bunny(c, held, 0, parent=P)
    if spec.get("roll_in_mouth"):
        sphere(c, "loaf", (0, -0.17, 0.87), 0.05, (1.4, 1, 0.8), parent=P)
    place(rig, spec)
    return rig


def borek(c, spec):
    rig = empty(c, "CHR02_BOREK")
    P = rig
    expr = spec.get("expr", "")
    for x in (-0.13, 0.13):
        box(c, "b_clog", (x, -0.04, 0.05), (0.15, 0.27, 0.1), parent=P)
        rod(c, "b_trouser", (x, 0, 0.08), (x, 0, 0.45), 0.1, parent=P)
    puff = 1.08 if expr == "puff" else 1.0
    sphere(c, "b_jacket", (0, 0, 0.82), 1.0, (0.45 * puff, 0.38 * puff, 0.42), parent=P)
    box(c, "b_apron", (0, -0.37, 0.6), (0.62, 0.04, 0.5), parent=P)
    if spec.get("apron_patch"):
        box(c, "bunny", (0.16, -0.395, 0.5), (0.12, 0.01, 0.12), parent=P)
        box(c, "stitch", (0.16, -0.402, 0.5), (0.012, 0.01, 0.15), rot=(0, 45, 0), parent=P)
        box(c, "stitch", (0.16, -0.402, 0.5), (0.012, 0.01, 0.15), rot=(0, -45, 0), parent=P)
    sphere(c, "b_skin", (0, 0, 1.33), 0.21, parent=P)
    for x in (-0.19, 0.19):
        sphere(c, "b_hair", (x, 0.04, 1.4), 0.06, parent=P)
        sphere(c, "b_skin", (x * 1.08, 0.0, 1.33), 0.05, (0.5, 1, 1), parent=P)
    for x in (-0.07, 0.07):
        sphere(c, "eye_w", (x, -0.178, 1.375), 0.022, parent=P)
        sphere(c, "eye_d", (x, -0.196, 1.375), 0.013, parent=P)
        up = 0.05 if (expr in ("brow_up", "surprised") and (x > 0 or expr == "surprised")) else 0.0
        tilt = -12 if x > 0 else 12
        if expr in ("brow_up", "surprised") and up:
            tilt = 0
        box(c, "b_hair", (x * 1.15, -0.185, 1.425 + up), (0.15, 0.05, 0.04), rot=(0, tilt, 0), parent=P)
    sphere(c, "b_nose", (0, -0.225, 1.31), 0.065, parent=P)
    curl = 0.06 if expr in ("mustache_up", "puff") else (-0.05 if expr == "mustache_down" else 0.0)
    for s in (-1, 1):
        rod(c, "b_hair", (0, -0.215, 1.25), (0.17 * s, -0.175, 1.27 + curl), 0.036, parent=P)
        sphere(c, "b_hair", (0.19 * s, -0.16, 1.31 + curl), 0.036, parent=P)
    arms = spec.get("arms", "crossed")
    sh_l, sh_r = (0.42, 0, 1.08), (-0.42, 0, 1.08)
    held_at = None
    if arms == "crossed":
        for sh, el in ((sh_l, (0.42, -0.3, 0.92)), (sh_r, (-0.42, -0.3, 0.92))):
            rod(c, "b_jacket", sh, el, 0.1, parent=P)
        rod(c, "b_skin", (0.44, -0.33, 0.93), (-0.36, -0.44, 0.98), 0.085, parent=P)
        rod(c, "b_skin", (-0.44, -0.33, 0.9), (0.36, -0.45, 0.94), 0.085, parent=P)
    elif arms == "shove_side":
        rod(c, "b_jacket", sh_l, (0.75, -0.05, 1.05), 0.1, parent=P)
        rod(c, "b_skin", (0.75, -0.05, 1.05), (1.0, -0.08, 1.02), 0.08, parent=P)
        rod(c, "b_jacket", sh_r, (-0.5, 0, 0.6), 0.1, parent=P)
        held_at = (1.12, -0.08, 1.02)
    elif arms in ("hold", "inspect"):
        z = 1.2 if arms == "inspect" else 0.98
        for sh, h in ((sh_l, (0.22, -0.55, z)), (sh_r, (-0.22, -0.55, z))):
            rod(c, "b_jacket", sh, ((sh[0] + h[0]) / 2, -0.3, (sh[2] + h[2]) / 2), 0.1, parent=P)
            rod(c, "b_skin", ((sh[0] + h[0]) / 2, -0.3, (sh[2] + h[2]) / 2), h, 0.08, parent=P)
            sphere(c, "b_skin", h, 0.075, parent=P)
        held_at = (0, -0.62, z + 0.04)
    else:
        for sh, h in ((sh_l, (0.52, 0, 0.62)), (sh_r, (-0.52, 0, 0.62))):
            rod(c, "b_jacket", sh, h, 0.1, parent=P)
            sphere(c, "b_skin", h, 0.075, parent=P)
    held = spec.get("holding")
    if held_at and held == "loaf":
        loaf(c, held_at, parent=P)
    elif held_at and held == "loaf_bad":
        loaf(c, held_at, bad=True, parent=P)
    elif held_at and held == "bunny":
        bunny(c, (held_at[0], held_at[1], held_at[2] - 0.1), 0, parent=P)
    place(rig, spec)
    return rig


def place(rig, spec):
    x, y = spec["pos"][:2]
    z = spec["pos"][2] if len(spec["pos"]) > 2 else 0.0
    rig.location = (x, y, z)
    pose = spec.get("pose", "stand")
    rx = {"crouch": 12, "lean": 22, "puff": -8}.get(pose, 0)
    ry = 9 if pose == "wobble" else 0
    rig.rotation_euler = Euler((math.radians(rx), math.radians(ry), math.radians(spec.get("face", 0))), "XYZ")
    sz = {"crouch": 0.8, "hide": 0.62}.get(pose, 1.0)
    rig.scale = (1, 1, sz)


# ---------------------------------------------------------------- shot extras

def extras(c, names):
    if "flour_prints" in names:
        box_span(c, "flour", (0.2, 2.9), (-2.4, -0.05), (0.0, 0.003))
        x, y, i = 1.75, -2.35, 0
        while y < -0.15:
            off = 0.06 if i % 2 else -0.06
            box(c, "wood_dark", (x + off, y, 0.004), (0.055, 0.13, 0.002), rot=(0, 0, -12))
            x -= 0.012
            y += 0.24
            i += 1
    if "lopsided_loaf_counter" in names:
        loaf(c, (0.62, 0.3, 1.04), bad=True)
    if "lopsided_loaf_display" in names:
        loaf(c, (-1.3, -2.17, 0.92), bad=True)
    if "best_loaf_display" in names:
        loaf(c, (-1.3, -2.17, 0.92))
    if "wildflower_basket" in names:
        rod(c, "stem", (1.22, 0.3, 1.08), (1.25, 0.28, 1.26), 0.006)
        sphere(c, "flower", (1.25, 0.28, 1.27), 0.03, (1, 1, 0.5))
    if "tray_oven" in names:
        box(c, "tray", (-2.1, 1.42, 1.0), (0.5, 0.35, 0.02))
        loaf(c, (-2.1, 1.42, 1.07), bad=True)
        for x in (-2.32, -1.88):
            sphere(c, "m_skin", (x, 1.32, 1.02), 0.035)
            rod(c, "m_tunic", (x, 1.32, 1.02), (x * 1.0, 1.0, 0.98), 0.04)
    if "step_stool" in names:
        box_span(c, "wood_mid", (0.5, 0.9), (0.65, 0.95), (0, 0.3))
    if "counter_bunny" in names:
        bunny(c, (1.62, 0.3, 0.99), 0)
    if "counter_bunny_display" in names:
        bunny(c, (0.88, 0.3, 0.99), 0)


# ---------------------------------------------------------------- render

def setup_scene(res):
    s = bpy.context.scene
    s.render.engine = "BLENDER_WORKBENCH"
    s.render.resolution_x, s.render.resolution_y = 1080, 1920
    s.render.resolution_percentage = res
    s.render.fps = 24
    s.display.render_aa = "8"
    sh = s.display.shading
    sh.light = "STUDIO"
    sh.color_type = "OBJECT"
    sh.show_shadows = True
    sh.shadow_intensity = 0.55
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.show_object_outline = True
    sh.object_outline_color = (0.05, 0.04, 0.04)
    s.display.light_direction = (0.35, -0.45, 0.82)
    s.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("Sky")
    w.color = C["sky"]
    s.world = w
    cam_data = bpy.data.cameras.new("CAM")
    cam = bpy.data.objects.new("CAM", cam_data)
    s.collection.objects.link(cam)
    s.camera = cam
    cam_data.clip_start = 0.02
    cam_data.clip_end = 60
    return s, cam


def aim(cam, loc, target):
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = d.to_track_quat("-Z", "Y")


def clear(c):
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def smooth(t):
    return t * t * (3 - 2 * t)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    shots_path, out_dir = Path(argv[0]), Path(argv[1])
    blend_out = argv[argv.index("--blend") + 1] if "--blend" in argv else None
    only = argv[argv.index("--only") + 1].split(",") if "--only" in argv else None
    data = json.loads(shots_path.read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s, cam = setup_scene(data.get("res_percent", 50))
    build_set()
    shot_c = coll("SHOT")
    out_dir.mkdir(parents=True, exist_ok=True)
    for shot in data["shots"]:
        if only and shot["id"] not in only:
            continue
        clear(shot_c)
        for name, spec in shot.get("chars", {}).items():
            (mila if name == "mila" else borek)(shot_c, spec)
        extras(shot_c, shot.get("extras", []))
        cam.data.lens = shot.get("lens", 35)
        move = shot.get("move")
        if move:
            n = shot["frames"]
            step = move.get("step", 1)
            seq = out_dir / f"{shot['id']}_seq"
            seq.mkdir(exist_ok=True)
            for f in ([] if "--stills" in argv else range(0, n, step)):
                t = smooth(min(1.0, max(0.0, (f - move.get("hold_in", 0)) /
                                        max(1, n - move.get("hold_in", 0) - move.get("hold_out", 0)))))
                lerp = lambda a, b: [a[i] + (b[i] - a[i]) * t for i in range(3)]
                aim(cam, lerp(shot["cam"], move.get("cam_end", shot["cam"])), lerp(shot["aim"], move["aim_end"]))
                s.render.filepath = str(seq / f"{f:04d}.png")
                bpy.ops.render.render(write_still=True)
            aim(cam, shot["cam"], shot["aim"])
            s.render.filepath = str(out_dir / f"{shot['id']}.png")
            bpy.ops.render.render(write_still=True)
            aim(cam, move.get("cam_end", shot["cam"]), move["aim_end"])
            s.render.filepath = str(out_dir / f"{shot['id']}_end.png")
            bpy.ops.render.render(write_still=True)
        else:
            aim(cam, shot["cam"], shot["aim"])
            s.render.filepath = str(out_dir / f"{shot['id']}.png")
            bpy.ops.render.render(write_still=True)
        print("rendered", shot["id"])
    if blend_out:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(blend_out).resolve()))


main()
