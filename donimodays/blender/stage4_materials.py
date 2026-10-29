"""
STAGE 4 - MATERIALS AND LIGHTING for Morrow, Vesper, and Nix.
Builds the stage 3 cast, then applies the colour language and material contrasts,
renders in a neutral studio first, then in one atmospheric dream-world shot.
Glow is limited to Morrow's ember and Nix's bead and coral edge.
Written for Blender 5.2 LTS.

Run inside Blender:  Scripting tab > Open this file > Run Script.
Run headless:        blender --background --python stage2_blockout.py -- <output_dir>

The script builds everything in NEW collections in a NEW scene called
"CAST_Blockout_v01". It does not touch any other scene or object.
If an output directory is given, it also saves a .blend copy and renders
every review view into that directory.
"""
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix, Quaternion, Euler
from mathutils.bvhtree import BVHTree

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else None

# ---------------------------------------------------------------- scene
scene = bpy.data.scenes.new("CAST_Materials_v04")
if bpy.context.window:
    bpy.context.window.scene = scene
else:
    bpy.context.window_manager.windows and None
scene.unit_settings.system = 'METRIC'
root_coll = scene.collection

def make_coll(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or root_coll).children.link(c)
    return c

C_MOR = make_coll("BLOCKOUT_Morrow")
C_VES = make_coll("BLOCKOUT_Vesper")
C_NIX = make_coll("BLOCKOUT_Nix")
C_POSE = make_coll("POSE_Relationship")
C_SIG = make_coll("POSE_Signature")
C_STG = make_coll("POSE_Staging_Vertical")
C_EXP = make_coll("EXPRESSIONS")
C_CAM = make_coll("BLOCKOUT_Cameras")
C_LGT = make_coll("BLOCKOUT_Lights")
C_ENV = make_coll("BLOCKOUT_Studio")

# ---------------------------------------------------------------- materials
# Every object carries a "part" tag. Material schemes map parts to gray values.
VALUE = {  # value-hierarchy test: light protagonist, dark-mid companion, darkest creature
    "mor_shell": .78, "mor_face": .06, "mor_lid": .08, "mor_eye": .88, "mor_pupil": .02,
    "mor_mouth": .6, "mor_joint": .10, "mor_seam": .45, "mor_ember": .97, "mor_crest": .55,
    "ves_mantle": .09, "ves_collar": .12, "ves_inner": .2, "ves_brass": .5, "ves_trim": .45, "ves_mask": .07, "ves_eye": .88,
    "ves_lid": .1, "ves_brow": .13, "ves_arm": .10, "ves_hand": .14, "ves_neck": .05,
    "nix_body": .03, "nix_eye": .86, "nix_fin": .045, "nix_bead": .97, "nix_edge": .95, "nix_guide": .5,
    "dream": .62, "floor": .32, "drm_ground": .1, "drm_moon": .8,
}
MATS = {}
def mat_for(part):
    if part not in MATS:
        m = bpy.data.materials.new("MAT_" + part)
        if m.node_tree is None:
            m.use_nodes = True
        MATS[part] = m
    return MATS[part]

def apply_scheme(scheme):
    for part, m in MATS.items():
        bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        g = 0.5 if scheme == "clay" else VALUE.get(part, .5)
        if part == "floor":
            g = .32
        bsdf.inputs["Base Color"].default_value = (g, g, g, 1)
        bsdf.inputs["Roughness"].default_value = 0.62
        m.diffuse_color = (g, g, g, 1)

SIL = bpy.data.materials.new("MAT_silhouette_black")
if SIL.node_tree is None:
    SIL.use_nodes = True
nt = SIL.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0, 0, 0, 1)
em.inputs["Strength"].default_value = 0
out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], out.inputs[0])

# ---------------------------------------------------------------- helpers
def finish(name, bm, coll, part, smooth=True, sharp_angle=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    if sharp_angle:
        me.set_sharp_from_angle(angle=math.radians(sharp_angle))
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob["part"] = part
    me.materials.append(mat_for(part))
    return ob

def xform(bm, M):
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)

def sphere(name, coll, part, loc, scale=(1, 1, 1), rot=None, r=1.0, u=32, v=20):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r)
    S = Matrix.Diagonal((*scale, 1))
    R = (rot.to_matrix().to_4x4() if rot is not None else Matrix.Identity(4))
    xform(bm, Matrix.Translation(loc) @ R @ S)
    return finish(name, bm, coll, part)

def basis(right, out, up):
    """Matrix mapping local X->right, Y->out, Z->up."""
    return Matrix((right, out, up)).transposed().to_4x4()

def cylinder(name, coll, part, a, b, r1, r2=None, seg=24):
    a, b = Vector(a), Vector(b)
    d = b - a
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2 if r2 else r1, depth=d.length)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    xform(bm, Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4())
    return finish(name, bm, coll, part)

def curve(name, coll, part, pts, radius, radii=None, kind='NURBS', ribbon=0.0, res=3, tilts=None):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    cu.extrude = ribbon
    sp = cu.splines.new(kind)
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
        sp.points[i].radius = radii[i] if radii else 1.0
        if tilts:
            sp.points[i].tilt = tilts[i]
    if kind == 'NURBS':
        sp.order_u = min(4, len(pts)); sp.use_endpoint_u = True; sp.resolution_u = 14
    ob = bpy.data.objects.new(name, cu)
    coll.objects.link(ob)
    ob["part"] = part
    cu.materials.append(mat_for(part))
    return ob

def tube_arc(name, coll, part, center, R, r, a0, a1, U, V, seg=48, ring=12, rscale=(1, 1), jitter=0.0, seed=1):
    """Tube swept along an arc in the plane spanned by U and V, angles in degrees."""
    import random
    rnd = random.Random(seed)
    center, U, V = Vector(center), Vector(U).normalized(), Vector(V).normalized()
    N = U.cross(V)
    bm = bmesh.new()
    rings = []
    for i in range(seg + 1):
        t = math.radians(a0 + (a1 - a0) * i / seg)
        radial = U * math.cos(t) + V * math.sin(t)
        c = center + radial * R
        row = []
        for j in range(ring):
            s = 2 * math.pi * j / ring
            off = radial * math.cos(s) * r * rscale[0] + N * math.sin(s) * r * rscale[1]
            if jitter:
                endness = 1.0 if (i < 2 or i > seg - 2) else 0.12
                off *= 1 + rnd.uniform(-jitter, jitter) * endness
            row.append(bm.verts.new(c + off))
        rings.append(row)
    for i in range(seg):
        for j in range(ring):
            bm.faces.new((rings[i][j], rings[i][(j + 1) % ring], rings[i + 1][(j + 1) % ring], rings[i + 1][j]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(name, bm, coll, part)

def bake_modifiers(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    bpy.data.meshes.remove(old)

def boolean(ob, cutter, op='DIFFERENCE'):
    m = ob.modifiers.new("bool", 'BOOLEAN')
    m.operation = op; m.object = cutter; m.solver = 'EXACT'
    bake_modifiers(ob)
    bpy.data.objects.remove(cutter)

def raycast(ob, origin, direction):
    dg = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(ob, dg)
    hit, nrm, _, _ = tree.ray_cast(Vector(origin), Vector(direction).normalized())
    return hit, nrm

def new_root(name, coll):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = 'PLAIN_AXES'; e.empty_display_size = 0.1
    coll.objects.link(e)
    return e

def parent_all(root, coll):
    """Parent only this character's own parts (matched by name prefix) to its root."""
    prefix = root.name[:-len("root")]
    for ob in coll.objects:
        if ob is not root and ob.parent is None and ob.name.startswith(prefix):
            ob.parent = root

def hand(prefix, coll, part, wrist, fwd, side, size, fingers=2, curl=0.4, thick=0.1):
    """Grasping hand: cupped palm, jointed tapering fingers with round tips, opposable thumb.
    fwd = pointing direction, side = thumb side, curl 0..1 bends every joint toward the palm."""
    fwd, side = Vector(fwd).normalized(), Vector(side).normalized()
    up = fwd.cross(side).normalized()
    side = up.cross(fwd).normalized()
    wrist = Vector(wrist)
    palm_c = wrist + fwd * size * 0.42
    sphere(prefix + "_palm", coll, part, palm_c, (size * 0.42, size * 0.5, size * 0.17),
           rot=basis(side, fwd, up).to_quaternion())
    rad = size * thick
    spread = [(-0.5 + i / max(1, fingers - 1)) if fingers > 1 else 0 for i in range(fingers)]
    for i, s_ in enumerate(spread):
        d = Matrix.Rotation(-s_ * 0.22, 3, up) @ fwd
        base = palm_c + fwd * size * 0.36 + side * s_ * size * 0.42
        pts = [base]
        for L in (0.3, 0.26, 0.2):
            d = Matrix.Rotation(curl * 0.6, 3, side) @ d
            pts.append(pts[-1] + d * L * size)
        curve(f"{prefix}_finger{i+1}", coll, part, pts, rad, [1.0, 0.95, 0.85, 0.72])
        sphere(f"{prefix}_fingertip{i+1}", coll, part, pts[-1], r=rad * 0.74, u=16, v=10)
    tb = palm_c - fwd * size * 0.08 + side * size * 0.4
    d = (side * 0.75 + fwd * 0.6 - up * 0.25).normalized()
    pts = [tb]
    for L in (0.24, 0.2, 0.16):
        pts.append(pts[-1] + d * L * size)
        d = Matrix.Rotation(-0.35 - curl * 0.3, 3, up) @ d
    curve(prefix + "_thumb", coll, part, pts, rad * 1.08, [1.0, 0.95, 0.85, 0.72])
    sphere(prefix + "_thumbtip", coll, part, pts[-1], r=rad * 0.8, u=16, v=10)

def surface_path(ob, guide, direction, lift=0.0015):
    """Project guide points onto a mesh along `direction`. Returns points on the surface."""
    out = []
    for g in guide:
        hit, n = raycast(ob, Vector(g) - Vector(direction) * 1.0, direction)
        if hit is not None:
            out.append(hit + n * lift)
    return out

# ================================================================ MORROW
def build_morrow(coll, P=None, tag="MOR"):
    """Small forward-leaning porcelain seed. P = pose dict in local coordinates."""
    P = P or {}
    root = new_root(f"{tag}_root", coll)

    # torso. upgrade 9: lower body, so the legs are shorter and the stance more planted
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=40, radius=1)
    for vt in bm.verts:
        x, y, z = vt.co
        t = (z + 1) / 2
        X = x * 0.165 * (1 - 0.42 * t ** 1.6) - 0.05 * t ** 2 + (0.02 * math.sin(math.pi * t) if x > 0 else 0)
        Y = y * 0.13 * (1 - 0.30 * t ** 1.6) - 0.12 * t ** 2
        Z = 0.075 + 0.43 * t
        vt.co = (X, Y, Z)
    torso = finish(f"{tag}_torso", bm, coll, "mor_shell")
    # stage 3: beautifully imperfect shell, like a worn river stone
    tex = bpy.data.textures.get("TEX_morrow_wear") or bpy.data.textures.new("TEX_morrow_wear", 'CLOUDS')
    tex.noise_scale = 0.09
    dm = torso.modifiers.new("wear", 'DISPLACE'); dm.texture = tex; dm.strength = 0.0045; dm.mid_level = 0.5
    bake_modifiers(torso)

    # upgrade 3: crescent cavity about 30 percent bigger, fatter belly so the ember can grow
    cav_c = Vector((-0.012, 0.0, 0.235))
    d = Vector((math.cos(math.radians(50)), 0, math.sin(math.radians(50))))
    a = cylinder("tmpA", coll, "mor_shell", cav_c + Vector((0, -0.4, 0)), cav_c + Vector((0, 0.4, 0)), 0.08, seg=72)
    b = cylinder("tmpB", coll, "mor_shell", cav_c + d * 0.05 + Vector((0, -0.5, 0)), cav_c + d * 0.05 + Vector((0, 0.5, 0)), 0.064, seg=72)
    boolean(a, b)
    boolean(torso, a)
    # stage 3: soften the cavity rim so it reads as a carved opening, not a cut
    bv = torso.modifiers.new("rim", 'BEVEL'); bv.width = 0.0045; bv.segments = 3; bv.limit_method = 'ANGLE'
    bv.angle_limit = math.radians(35)
    bake_modifiers(torso)
    torso.data.set_sharp_from_angle(angle=math.radians(60))
    # ember: about 1.7x larger. 2x would touch the walls, which breaks the "floats without touching" rule
    sphere(f"{tag}_ember", coll, "mor_ember", cav_c - d * 0.047 + Vector((0, -0.012, 0)) + Vector(P.get("ember_lag", (0, 0, 0))), r=0.026)

    # face patch, moved higher so it no longer competes with the cavity
    hit, n = raycast(torso, (0.012, -1, 0.43), (0, 1, 0))
    right = Vector((1, 0, 0)); up = n.cross(right).normalized()       # points up the face
    right = up.cross(n).normalized()
    face_c = hit - n * 0.006
    FB = basis(-right, n, up)   # right-handed face frame: local Y = outward normal, local Z = up
    sphere(f"{tag}_face", coll, "mor_face", face_c, (0.074, 0.022, 0.058), rot=FB.to_quaternion())

    gaze = Vector(P.get("gaze", (0, -1, 0))).normalized()
    lid_close = P.get("lid", 0.30)
    brow = P.get("brow", (0.0, 0.0))   # inner-corner raise per eye: + worried, - determined
    for i, (side, r_eye) in enumerate(((-1, 0.019), (1, 0.0235))):
        k = 'L' if side < 0 else 'R'
        ec = face_c + right * side * 0.029 + up * 0.008 + n * 0.012
        sphere(f"{tag}_eye_{k}", coll, "mor_eye", ec, r=r_eye)
        pdir = (n * 0.55 + gaze * 0.45).normalized()
        sphere(f"{tag}_pupil_{k}", coll, "mor_pupil", ec + pdir * r_eye * 0.78, r=r_eye * 0.42)
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=18, radius=r_eye * 1.14)
        bmesh.ops.delete(bm, geom=[vv for vv in bm.verts if vv.co.z < r_eye * 0.05], context='VERTS')
        tilt = Matrix.Rotation(math.radians(70 - 140 * lid_close), 4, 'X')   # 0 = tucked away, 0.5 = half, 1 = shut
        xform(bm, Matrix.Translation(ec) @ FB @ tilt)
        finish(f"{tag}_lid_{k}", bm, coll, "mor_lid")
        # stage 3: lower lid for delight, squints, and embarrassment
        low = P.get("lower", 0.1)
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=18, radius=r_eye * 1.06)
        bmesh.ops.delete(bm, geom=[vv for vv in bm.verts if vv.co.z > -r_eye * 0.05], context='VERTS')
        xform(bm, Matrix.Translation(ec) @ FB @ Matrix.Rotation(math.radians(-70 + 120 * low), 4, 'X'))
        finish(f"{tag}_lowlid_{k}", bm, coll, "mor_lid")
        # upgrade 6: brow ridge along the upper edge of the face patch
        inner = ec - right * side * 0.013 + up * (0.031 + brow[i] * 0.012) + n * 0.004
        outer = ec + right * side * 0.022 + up * (0.03 - brow[i] * 0.005) + n * 0.002
        mid = (inner + outer) / 2 + up * 0.005 + n * 0.003
        curve(f"{tag}_brow_{k}", coll, "mor_face", [inner, mid, outer], 0.0065, [0.9, 1.1, 0.8])
    # upgrade 6: wider, thicker mouth that reads on a phone
    mc = face_c + up * -0.028 + n * 0.023 + right * 0.004
    smile = P.get("smile", 0.25)
    mw = P.get("mouth_w", 1.0)
    curve(f"{tag}_mouth", coll, "mor_mouth",
          [mc - right * 0.022 * mw + up * 0.007 * smile, mc - right * 0.008 * mw - up * 0.004 * smile,
           mc + right * 0.008 * mw - up * 0.005 * smile, mc + right * 0.022 * mw + up * 0.008 * smile], 0.0036, [0.7, 1, 1, 0.7])

    # stage 3: two large repaired seams with metal inlay. one meets the cavity, one runs down the back
    seam1 = surface_path(torso, [(0.06, 0, 0.38), (0.075, 0, 0.35), (0.07, 0, 0.32), (0.085, 0, 0.29), (0.08, 0, 0.26),
                                 (0.06, 0, 0.255)], Vector((0, 1, 0)))
    if len(seam1) >= 3:
        curve(f"{tag}_seam_front", coll, "mor_seam", seam1, 0.0022, [0.4] + [1.0] * (len(seam1) - 2) + [0.5], kind='POLY')
    seam2 = surface_path(torso, [(-0.03, 0, 0.47), (-0.05, 0, 0.42), (-0.035, 0, 0.38), (-0.07, 0, 0.345), (-0.11, 0, 0.3),
                                 (-0.125, 0, 0.24), (-0.118, 0, 0.18)], Vector((0, -1, 0)))
    if len(seam2) >= 3:
        curve(f"{tag}_seam_back", coll, "mor_seam", seam2, 0.0024, [0.4] + [1.0] * (len(seam2) - 2) + [0.4], kind='POLY')

    # ribbon crest
    hit_b, nb = raycast(torso, (-0.02, 1, 0.47), (0, -1, 0))
    crest = P.get("crest", "raised")
    pts = {"raised": [(0, 0, 0), (0.0, 0.025, 0.045), (-0.005, 0.03, 0.095), (-0.01, 0.005, 0.13), (-0.012, -0.025, 0.125)],
           "high": [(0, 0, 0), (0.0, 0.015, 0.06), (-0.004, 0.012, 0.125), (-0.008, -0.005, 0.175), (-0.01, -0.03, 0.19)],
           "curled": [(0, 0, 0), (0, 0.035, 0.01), (0, 0.04, -0.03), (0, 0.015, -0.04)],
           "relaxed": [(0, 0, 0), (0, 0.04, 0.02), (0, 0.08, 0.0), (0, 0.11, -0.03)]}[crest]
    pts = [hit_b - nb * 0.004 + Vector(p) for p in pts]
    curve(f"{tag}_crest", coll, "mor_crest", pts, 0.004, [0.55, 1.0, 1.05, 0.75, 0.35][:len(pts)], ribbon=0.026,
          tilts=[0.0, 0.5, 1.0, 1.35, 1.57][:len(pts)])

    # upgrade 9: shorter legs, broader feet
    feet = P.get("feet", (-0.012, 0.008))
    for side, fwd in zip((-1, 1), feet):
        k = 'L' if side < 0 else 'R'
        x = side * 0.064
        cylinder(f"{tag}_leg_{k}", coll, "mor_joint", (x, -0.005, 0.03), (x, -0.005, 0.11), 0.033, 0.037)
        sphere(f"{tag}_foot_{k}", coll, "mor_shell", (x * 1.1, -0.022 + fwd, 0.024), (0.058, 0.074, 0.026))

    # upgrade 9: tapered arms and bold two-finger hands
    arms = P.get("arms", {})
    for side in (-1, 1):
        k = 'L' if side < 0 else 'R'
        hs, hn = raycast(torso, (side * 1, -0.02, 0.33), (-side, 0, 0))
        sh = hs - Vector((side * 0.012, 0, 0))
        cylinder(f"{tag}_shoulder_{k}", coll, "mor_joint", sh - Vector((side * 0.01, 0, 0)), sh + Vector((side * 0.012, 0, 0)), 0.023)
        default = [sh, sh + Vector((side * 0.06, -0.035, -0.085)), sh + Vector((side * 0.045, -0.075, -0.18))]
        pts = ([sh] + [Vector(p) for p in arms[k]]) if k in arms else default
        curve(f"{tag}_arm_{k}", coll, "mor_shell", pts, 0.022, [1.15, .9, .72] + [.7] * (len(pts) - 3))
        fwd = (pts[-1] - pts[-2]).normalized()
        sidev = fwd.cross(Vector((0, 0, 1))).normalized() * (-side)
        if sidev.length < 0.1:
            sidev = Vector((side, 0, 0))
        hand(f"{tag}_hand_{k}", coll, "mor_shell", pts[-1], fwd, sidev, 0.064, fingers=2, curl=P.get("curl", 0.45), thick=0.21)

    # signature rest pose: Morrow carries a dream fragment hugged to its chest
    if P.get("carry"):
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.052)
        rr = __import__("random").Random(5)
        for vv in bm.verts:
            vv.co *= 1 + rr.uniform(-0.18, 0.18)
        xform(bm, Matrix.Translation(Vector(P["carry"])) @ Matrix.Diagonal((1, 0.6, 1.15, 1)))
        finish(f"{tag}_carried_dream", bm, coll, "dream", smooth=False)

    parent_all(root, coll)
    return root

# ================================================================ VESPER
def catmull(keys, z):
    zs = [k[0] for k in keys]
    if z <= zs[0]: return keys[0][1]
    if z >= zs[-1]: return keys[-1][1]
    i = max(j for j in range(len(zs) - 1) if zs[j] <= z)
    p0 = keys[max(i - 1, 0)][1]; p1 = keys[i][1]; p2 = keys[i + 1][1]; p3 = keys[min(i + 2, len(keys) - 1)][1]
    t = (z - zs[i]) / (zs[i + 1] - zs[i])
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)

PROFILE = [(0, .27), (.2, .215), (.5, .14), (.8, .15), (1.02, .2), (1.18, .19), (1.3, .12), (1.38, .05)]
ZTOP = 1.38
BEND = [0.0]   # 0 = upright. >0 = deep crescent bow (used for the hero and staging poses)

def zmap(z):
    """Height after bending: the bow compresses the upper body downward."""
    s = max(0.0, z) / ZTOP
    return z - BEND[0] * 0.3 * z * s ** 1.5

def spine(z):
    s = max(0.0, min(z, ZTOP)) / ZTOP
    return Vector((0.07 * s ** 2.2, 0.05 * math.sin(math.pi * s) - 0.24 * s ** 2.6 - BEND[0] * 0.42 * s ** 2.4, 0))

def body_pt(off, z):
    """A point at height z on Vesper's bent spine, plus an offset."""
    return spine(z) + Vector(off) + Vector((0, 0, zmap(z)))

def surf(name, coll, part, phi0, phi1, z0, z1, dr=0.0, hem=0.0, flare=0.0, xoff=0.0, petal=0.0,
         nu=30, nv=44, closed=False, thick=0.012, slant=0.0, twist=0.0, edge_trim=None):
    """Curved shell panel around the spine. petal narrows the ends, twist sweeps it diagonally."""
    bm = bmesh.new()
    grid = []
    pm, half = (phi0 + phi1) / 2, (phi1 - phi0) / 2
    for i in range(nu + (0 if closed else 1)):
        u = i / nu
        col = []
        for j in range(nv + 1):
            v = j / nv
            w = 1 - petal * (1 - math.sin(math.pi * min(1, v * 1.15))) if petal else 1
            phi = math.radians(pm + twist * (v - 0.5) + (2 * u - 1) * half * w) if not closed else math.radians(phi0 + 360 * u)
            zb = z0 + hem * math.sin(math.pi * u)
            z = zb + (z1 - slant * u - zb) * v
            r = catmull(PROFILE, z) + dr + flare * (1 - v) ** 2
            c = spine(z) + Vector((xoff * v, 0, 0))
            col.append(bm.verts.new((c.x + r * math.cos(phi), c.y + r * math.sin(phi) * 0.86, zmap(z))))
        grid.append(col)
    n = len(grid)
    for i in range(n if closed else n - 1):
        for j in range(nv):
            i2 = (i + 1) % n
            bm.faces.new((grid[i][j], grid[i2][j], grid[i2][j + 1], grid[i][j + 1]))
    edge_pts = [grid[0][j].co.copy() for j in range(2, int(nv * 0.72), 2)] if edge_trim else None
    ob = finish(name, bm, coll, part)
    if thick:
        sm = ob.modifiers.new("thick", 'SOLIDIFY'); sm.thickness = thick; sm.offset = -1
        bake_modifiers(ob)
    if edge_pts:  # worn brass on this one structural edge only
        n_ = len(edge_pts)
        curve(edge_trim, coll, "ves_trim", edge_pts, 0.0065, [0.3 + 0.7 * math.sin(math.pi * i / (n_ - 1)) for i in range(n_)])
    return ob

def sleeve(name, coll, part, a, b, r1, r2, seg=28):
    """Open flared shell over the upper arm, echoing the mantle panels."""
    a, b = Vector(a), Vector(b)
    d = b - a
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=seg, radius1=r1, radius2=r2, depth=d.length)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    xform(bm, Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4())
    ob = finish(name, bm, coll, part)
    sm = ob.modifiers.new("thick", 'SOLIDIFY'); sm.thickness = 0.008; sm.offset = -1
    bake_modifiers(ob)
    return ob

def build_vesper(coll, P=None, tag="VES"):
    P = P or {}
    BEND[0] = P.get("bend", 0.0)
    root = new_root(f"{tag}_root", coll)
    surf(f"{tag}_core", coll, "ves_inner", 0, 360, 0.02, 1.33, dr=-0.025, closed=True, thick=0, nu=40)
    # upgrade 4: one big sweeping crescent mantle, two medium panels, one small panel, calm back
    surf(f"{tag}_panel_back_calm", coll, "ves_mantle", 30, 150, 0.0, 1.36, 0.0, 0.03, petal=0.12)
    cres = surf(f"{tag}_mantle_crescent", coll, "ves_mantle", 190, 330, 0.0, 1.34, 0.05, 0.05, petal=0.5, twist=95,
                edge_trim=f"{tag}_mantle_trim")
    surf(f"{tag}_panel_right_med", coll, "ves_mantle", -82, 28, 0.0, 1.15, 0.014, 0.06, petal=0.3)
    surf(f"{tag}_panel_frontL_med", coll, "ves_mantle", 205, 278, 0.0, 0.78, 0.02, 0.07, petal=0.35)
    surf(f"{tag}_hood", coll, "ves_collar", -62, 242, 0.98, 1.42, 0.05, 0.09, flare=0.06, xoff=0.03, petal=0.2)

    neck_top = body_pt((0, -0.07, 0), 1.3)
    cylinder(f"{tag}_neck", coll, "ves_neck", body_pt((0, -0.02, 0), 1.2), neck_top, 0.05, 0.034)

    # upgrade 1: dark carved stone mask with a crescent side profile. eyes are the lightest value
    tilt = P.get("head_tilt", (6, -8, 0))
    Rh = Euler([math.radians(a) for a in tilt]).to_matrix().to_4x4()
    M = neck_top + Vector((0, -0.03, 0.15))
    head = lambda p: M + (Rh @ Vector(p))
    hq = Rh.to_quaternion()
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=22, v_segments=16, radius=1)
    for vt in bm.verts:
        x, y, z = vt.co
        w = 0.072 * (1 - 0.45 * max(0, -z) ** 1.4) * (1 + 0.15 * max(0, z))
        yy = y * 0.052
        if y < 0:  # front face: brow and chin push forward, the middle recedes -> crescent profile
            yy -= 0.03 * z * z + 0.012 * max(0, z)
        vt.co = (x * w, yy, z * 0.108)
    xform(bm, Matrix.Translation(M) @ Rh)
    mask = finish(f"{tag}_mask", bm, coll, "ves_mask")
    for side in (-1, 1):
        sock = sphere("tmp_sock", coll, "ves_mask", head((side * 0.029, -0.07, 0.012)), (0.028, 0.04, 0.024), rot=hq)
        boolean(mask, sock)
    mask.data.set_sharp_from_angle(angle=math.radians(22))   # faceted, carved look
    lid = P.get("lids", (0.4, 0.3))
    brow = P.get("brows", (0.012, -0.004))
    for i, side in enumerate((-1, 1)):
        k = 'L' if side < 0 else 'R'
        ec = head((side * 0.029, -0.05, 0.012))
        sphere(f"{tag}_eye_{k}", coll, "ves_eye", ec, r=0.0175)
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=0.0202)
        bmesh.ops.delete(bm, geom=[vv for vv in bm.verts if vv.co.z < 0.001], context='VERTS')
        xform(bm, Matrix.Translation(ec) @ Rh @ basis(Vector((-1, 0, 0)), Vector((0, -1, 0)), Vector((0, 0, 1))) @ Matrix.Rotation(math.radians(70 - 140 * lid[i]), 4, 'X'))
        finish(f"{tag}_lid_{k}", bm, coll, "ves_lid")
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=0.0198)
        bmesh.ops.delete(bm, geom=[vv for vv in bm.verts if vv.co.z > -0.001], context='VERTS')
        low = P.get("lower", (0.15, 0.15))[i]
        xform(bm, Matrix.Translation(ec) @ Rh @ basis(Vector((-1, 0, 0)), Vector((0, -1, 0)), Vector((0, 0, 1))) @ Matrix.Rotation(math.radians(-70 + 120 * low), 4, 'X'))
        finish(f"{tag}_lowlid_{k}", bm, coll, "ves_lid")
        b0 = head((side * 0.008, -0.078, 0.043 + brow[i] * 0.3)); b1 = head((side * 0.055, -0.062, 0.04 + brow[i]))
        curve(f"{tag}_brow_{k}", coll, "ves_brow", [b0, (b0 + b1) / 2 + Rh @ Vector((0, -0.006, 0.006)), b1], 0.0085, [1, 1.2, .7])

    # upgrade 5: halo and fragments twice as thick, fragments chunkier
    hc = head((0, 0.045, 0.02))
    Rt = Rh @ Euler((math.radians(-22), 0, math.radians(14))).to_matrix().to_4x4()
    U = Rt @ Vector((1, 0, 0)); V = Rt @ Vector((0, 0, 1))
    tube_arc(f"{tag}_halo", coll, "ves_brass", hc, 0.17, 0.024, 104, 346, U, V, seg=72, rscale=(1.0, 1.5))
    for i, ang in enumerate((104, 346)):
        tube_arc(f"{tag}_halo_break_{i+1}", coll, "ves_brass", hc, 0.17, 0.03, ang - (6 if i else 0), ang + (0 if i else 6), U, V,
                 seg=4, ring=7, rscale=(1.1, 1.5), jitter=0.3, seed=11 + i)
    frag = P.get("fragments", [(0.215, 22, 0), (0.235, 52, 1), (0.215, 82, 2)])
    for i, (rad, ang, seed) in enumerate(frag):
        o = tube_arc(f"{tag}_fragment_{i+1}", coll, "ves_brass", hc, rad, 0.02, ang - 13 - seed * 2, ang + 13, U, V,
                     seg=14, ring=12, rscale=(1.0, 1.35), jitter=0.22, seed=seed + 3)
        o.data.set_sharp_from_angle(angle=math.radians(35))

    # upgrade 8: much longer hands. one can arch over Morrow's head
    arms = P.get("arms", {})
    for side in (-1, 1):
        k = 'L' if side < 0 else 'R'
        sh = body_pt((side * 0.19 + 0.03, -0.02, 0), 1.1)
        if k in arms:
            el, wr = Vector(arms[k][0]), Vector(arms[k][1])
        else:
            el = sh + Vector((side * 0.07, -0.06, -0.34))
            wr = Vector((side * 0.03 + 0.02, -0.3, 0.72 if side < 0 else 0.64))
        sphere(f"{tag}_shoulderjoint_{k}", coll, "ves_arm", sh, r=0.034)
        cylinder(f"{tag}_upperarm_{k}", coll, "ves_arm", sh, el, 0.028, 0.03)
        sleeve(f"{tag}_sleeve_{k}", coll, "ves_mantle", sh + (sh - el).normalized() * 0.02, sh + (el - sh) * 0.82, 0.05, 0.075)
        sphere(f"{tag}_elbow_{k}", coll, "ves_arm", el, r=0.033)
        cylinder(f"{tag}_forearm_{k}", coll, "ves_arm", el, wr, 0.04, 0.026)
        fwd = Vector(arms.get(k + "_fwd", (Vector((-side * 0.35, -0.25, -0.9)) if k not in arms else (wr - el)))).normalized()
        sidev = Vector(arms.get(k + "_side", (side * 0.2, -1, 0) if k not in arms else fwd.cross(Vector((0, 0, 1))).normalized() * side))
        hand(f"{tag}_hand_{k}", coll, "ves_hand", wr, fwd, sidev, 0.14, fingers=3, curl=arms.get(k + "_curl", 0.6), thick=0.1)

    parent_all(root, coll)
    BEND[0] = 0.0
    return root

# ================================================================ NIX
def build_nix(coll, P=None, tag="NIX"):
    P = P or {}
    root = new_root(f"{tag}_root", coll)
    R, r, off, dep = 0.075, 0.063, 0.034, 0.03
    od = Vector((math.cos(math.radians(28)), 0, math.sin(math.radians(28))))
    a = cylinder(f"{tag}_body", coll, "nix_body", (0, -dep / 2, 0), (0, dep / 2, 0), R, seg=96)
    b = cylinder("tmpB", coll, "nix_body", od * off + Vector((0, -1, 0)), od * off + Vector((0, 1, 0)), r, seg=96)
    boolean(a, b)
    Mcut = Matrix.Translation((0.07, 0, -0.062)) @ Matrix.Rotation(math.radians(40), 4, 'Y') @ Matrix.Diagonal((0.06, 0.2, 0.07, 1))
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); xform(bm, Mcut)
    boolean(a, finish("tmpCut", bm, coll, "nix_body"))
    rm = a.modifiers.new("remesh", 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = 0.0016
    bake_modifiers(a)
    cB0 = od * off
    bm = bmesh.new(); bm.from_mesh(a.data)
    for vt in bm.verts:
        p = vt.co
        q = Vector((p.x, 0, p.z))
        t = min(R - q.length, (q - cB0).length - r)
        f = 0.42 + 0.85 * min(1.0, max(0.0, t / 0.02)) ** 0.8
        vt.co.y = p.y * f
    bm.to_mesh(a.data); bm.free()
    sm = a.modifiers.new("smooth", 'SMOOTH'); sm.factor = 0.9; sm.iterations = 14
    bake_modifiers(a)
    for pg in a.data.polygons:
        pg.use_smooth = True

    # upgrade 2: narrow luminous coral edge along the inner curve of the crescent
    cB = od * off
    Mi = Mcut.inverted()
    def on_body(t):
        p = cB + Vector((math.cos(t), 0, math.sin(t))) * r
        q = Mi @ p
        return p.length < R - 0.004 and not all(abs(c) <= 0.5 for c in q)
    flags = [on_body(math.radians(k)) for k in range(360)]
    start = flags.index(False)
    runs, cur = [], None
    for kk in range(start, start + 361):
        k = kk % 360
        if flags[k] and cur is None:
            cur = kk
        if not flags[k] and cur is not None:
            runs.append((cur, kk - 1)); cur = None
    for i, (a0, a1) in enumerate(runs):
        tube_arc(f"{tag}_edge_{i+1}", coll, "nix_edge", cB, r + 0.0006, 0.0042, a0, a1, Vector((1, 0, 0)), Vector((0, 0, 1)),
                 seg=max(8, (a1 - a0) // 3), ring=10, rscale=(0.45, 1.9))

    # face across the belly. upgrade 7: lid shapes cut across the eyes
    eye_tilt = P.get("eye_tilt", 0)
    lids = P.get("lids", (0.25, -20))      # (amount covered 0..1, slant angle deg)
    fc = Vector((-0.045, -dep / 2 - 0.0012, -0.004))
    for side in (-1, 1):
        k = 'L' if side < 0 else 'R'
        ec0 = fc + Vector((side * 0.0128, 0, side * -0.003))
        hit_e, n_e = raycast(a, (ec0.x, -1, ec0.z), (0, 1, 0))
        ec = hit_e + Vector((0, 0.0012, 0)) if hit_e is not None else ec0
        eye = sphere(f"{tag}_eye_{k}", coll, "nix_eye", ec, (0.0075, 0.0034, 0.012),
                     rot=Euler((0, math.radians(side * 10 + eye_tilt), 0)).to_quaternion())
        cover, slant = lids
        if cover > 0:   # the lid is a slanted cut across the top of the eye shape itself
            rot = Euler((0, math.radians(side * 10 + eye_tilt - slant * side), 0)).to_matrix().to_4x4()
            bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
            xform(bm, Matrix.Translation(ec) @ rot @ Matrix.Translation((0, 0, 0.012 - 0.024 * cover + 0.02)) @ Matrix.Diagonal((0.05, 0.05, 0.04, 1)))
            boolean(eye, finish("tmpLid", bm, coll, "nix_body"))

    # upgrade 10: rounded paddle fins that curl like small crescents
    fins = P.get("fins", {"A": (128, 0.0), "B": (222, 0.0)})
    for k, (ang, sweep) in fins.items():
        t = math.radians(ang)
        rad = Vector((math.cos(t), 0, math.sin(t))); perp = Vector((-rad.z, 0, rad.x))
        base = rad * (R - 0.01)
        pts = [base, base + rad * 0.016 + perp * 0.003, base + rad * 0.027 + perp * 0.011 + Vector((0, sweep * 0.5, 0)),
               base + rad * 0.031 + perp * 0.022 + Vector((0, sweep, 0))]
        f = curve(f"{tag}_fin_{k}", coll, "nix_fin", pts, 0.012, [0.6, 1.15, 1.2, 0.75])
        f.scale = (1, 0.32, 1)

    # upgrade 7: bead twice the size
    oc = od * off
    U, V = Vector((1, 0, 0)), Vector((0, -0.45, 0.9)).normalized()
    g = tube_arc(f"{tag}_guide_orbit", coll, "nix_guide", oc, 0.047, 0.0009, 20, 320, U, V, seg=64, ring=6)
    g.hide_render = True
    ba = math.radians(P.get("bead_angle", 250))
    sphere(f"{tag}_bead", coll, "nix_bead", oc + (U * math.cos(ba) + V * math.sin(ba)) * 0.047, r=0.0125)
    parent_all(root, coll)
    return root

# ================================================================ studio
def studio():
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=20)
    finish("ENV_floor", bm, C_ENV, "floor")
    w = bpy.data.worlds.new("WORLD_studio")
    if w.node_tree is None:
        w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (0.22, 0.22, 0.23, 1); bg.inputs[1].default_value = 0.6
    scene.world = w
    def area(name, loc, energy, size, target=(0, 0, 0.5)):
        L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.size = size
        o = bpy.data.objects.new(name, L); C_LGT.objects.link(o); o.location = loc
        d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        return o
    area("LGT_key", (-1.6, -2.2, 2.4), 420, 1.6)
    area("LGT_fill", (2.2, -1.8, 1.1), 110, 2.0)
    area("LGT_rim", (1.2, 2.3, 2.2), 260, 1.2)

def camera(name="CAM_review"):
    cd = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cd); C_CAM.objects.link(cam)
    scene.camera = cam
    return cam

def frame(cam, objs, view_dir, lens=85, margin=1.18, aspect=0.75):
    pts = []
    for o in objs:
        if o.type in {'MESH', 'CURVE'} and not o.hide_render:
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    c = (lo + hi) / 2
    h = (hi.z - lo.z); w = max(hi.x - lo.x, hi.y - lo.y)
    cam.data.lens = lens; cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24
    vf = 2 * math.atan(12 / lens)
    need = max(h, w / aspect) * margin
    dist = (need / 2) / math.tan(vf / 2)
    vd = Vector(view_dir).normalized()
    cam.location = c + vd * dist
    cam.rotation_euler = (-vd).to_track_quat('-Z', 'Y').to_euler()

def dream_shard(name, coll, loc, seed=7):
    import random
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.04)
    rr = random.Random(seed)
    for vv in bm.verts:
        vv.co *= 1 + rr.uniform(-0.18, 0.18)
    xform(bm, Matrix.Translation(loc) @ Matrix.Diagonal((1, 0.55, 1.2, 1)))
    return finish(name, bm, coll, "dream", smooth=False)

def world_bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type in {'MESH', 'CURVE'} for c in o.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))

# ================================================================ build: neutral cast
mor = build_morrow(C_MOR)
ves = build_vesper(C_VES)
nix = build_nix(C_NIX)
studio()
cam = camera()
LINEUP = {"MOR": ((0, 0, 0), 0), "VES": ((0.62, 0.08, 0), -12), "NIX": ((-0.34, -0.02, 0.46), 14)}
for root, key in ((mor, "MOR"), (ves, "VES"), (nix, "NIX")):
    root.location = LINEUP[key][0]; root.rotation_euler.z = math.radians(LINEUP[key][1])

# ================================================================ relationship pose
DREAM = Vector((-0.26, -0.26, 0.4))
MOR_T = Matrix.LocRotScale(Vector((0, 0, 0)), Euler((math.radians(8), 0, math.radians(-15))), None)
VES_T = Matrix.LocRotScale(Vector((0.36, 0.34, 0)), Euler((0, 0, math.radians(-40))), None)
NIX_T = Matrix.LocRotScale(DREAM + Vector((-0.085, -0.02, 0.05)), Euler((0, math.radians(18), math.radians(-35))), None)
mi, vi = MOR_T.inverted(), VES_T.inverted()
L = lambda Mi, p: Mi @ Vector(p)
dl = mi @ DREAM
shL = Vector((-0.15, -0.03, 0.33))
reach = (dl - shL).normalized()
morP = build_morrow(C_POSE, {
    "gaze": (mi.to_3x3() @ (DREAM - Vector((0, -0.08, 0.44)))).normalized(),
    "lid": 0.05, "crest": "raised", "smile": -0.35, "curl": 0.2, "brow": (0.9, 0.6),     # curious but worried
    "arms": {"L": [shL + reach * 0.13 + Vector((-0.06, 0, 0.04)), shL + reach * 0.28 + Vector((0, 0, 0.02))],
             "R": [Vector((0.17, -0.1, 0.24)), Vector((0.05, -0.2, 0.26))]},
}, tag="POSE_MOR")
morP.matrix_world = MOR_T
vesP = build_vesper(C_POSE, {
    "head_tilt": (-14, 10, 38), "lids": (0.45, 0.3), "brows": (0.018, -0.006),
    "fragments": [(0.215, 165, 0), (0.235, 192, 1), (0.215, 219, 2)],
    "arms": {"L": [L(vi, (0.16, 0.1, 0.98)), L(vi, (0.07, -0.02, 0.8))],
             "L_fwd": (vi.to_3x3() @ Vector((-0.45, -0.75, -0.35))).normalized(),
             "L_side": (vi.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized(), "L_curl": 0.75,
             "R": [L(vi, (0.6, 0.18, 0.82)), L(vi, (0.42, 0.0, 0.98))],
             "R_fwd": (vi.to_3x3() @ Vector((-0.5, 0.3, 0.6))).normalized(), "R_curl": 0.8},
}, tag="POSE_VES")
vesP.matrix_world = VES_T
nixP = build_nix(C_POSE, {"fins": {"A": (60, 0.0), "B": (205, 0.03)}, "bead_angle": 330, "eye_tilt": 15,
                          "lids": (0.35, -25)}, tag="POSE_NIX")   # trying to look innocent
nixP.matrix_world = NIX_T
dream_shard("POSE_dream_fragment", C_POSE, DREAM)

# ================================================================ upgrade 11: signature poses
SIG = {}
# Morrow rest: hugs a dream fragment to its chest, crest relaxed
SIG["morrow_rest"] = build_morrow(C_SIG, {"crest": "relaxed", "lid": 0.4, "smile": 0.5, "brow": (0.3, 0.2), "curl": 0.7,
    "arms": {"L": [Vector((-0.19, -0.1, 0.22)), Vector((-0.06, -0.2, 0.235))],
             "R": [Vector((0.19, -0.1, 0.24)), Vector((0.06, -0.205, 0.26))]},
    "carry": (0.0, -0.24, 0.335)}, tag="SIG_MORREST")
# Morrow hero: braced, determined, crest high
SIG["morrow_hero"] = build_morrow(C_SIG, {"crest": "high", "lid": 0.32, "smile": -0.15, "brow": (-1.0, -1.0), "curl": 0.65,
    "feet": (-0.05, 0.03), "ember_lag": (0, 0.008, 0),
    "arms": {"L": [Vector((-0.235, -0.05, 0.3)), Vector((-0.3, -0.1, 0.37))],
             "R": [Vector((0.235, -0.05, 0.26)), Vector((0.3, -0.1, 0.19))]}}, tag="SIG_MORHERO")
SIG["morrow_hero"].rotation_euler = (math.radians(10), 0, 0)
# Vesper rest: formal, clasped, slight concerned tilt (the default)
SIG["vesper_rest"] = build_vesper(C_SIG, {"head_tilt": (8, -10, 0)}, tag="SIG_VESREST")
# Vesper hero: deep crescent bow, long sheltering arm, fragments drawn into a shelter arc
SIG["vesper_hero"] = build_vesper(C_SIG, {"bend": 0.75, "head_tilt": (24, 6, -6), "lids": (0.25, 0.2), "brows": (0.02, 0.012),
    "fragments": [(0.27, 200, 0), (0.3, 232, 1), (0.27, 264, 2)],
    "arms": {"L": [Vector((-0.33, -0.42, 0.88)), Vector((-0.2, -0.72, 0.62))], "L_fwd": (0.25, -0.75, -0.55), "L_side": (1, 0, 0.2), "L_curl": 0.7,
             "R": [Vector((0.32, -0.38, 0.72)), Vector((0.22, -0.62, 0.5))], "R_fwd": (-0.2, -0.7, -0.6), "R_side": (-1, 0, 0.2), "R_curl": 0.7}},
    tag="SIG_VESHERO")
# Nix rest: smug half-lidded hover, bead pointing up
SIG["nix_rest"] = build_nix(C_SIG, {"lids": (0.45, -28), "bead_angle": 95, "eye_tilt": 8}, tag="SIG_NIXREST")
SIG["nix_rest"].rotation_euler = (0, math.radians(-12), 0)
# Nix hero: banked dart, fins flared, eyes wide, bead forward
SIG["nix_hero"] = build_nix(C_SIG, {"lids": (0.0, 0), "bead_angle": 345, "fins": {"A": (110, 0.025), "B": (250, 0.025)}},
                            tag="SIG_NIXHERO")
SIG["nix_hero"].rotation_euler = (0, math.radians(38), math.radians(-18))

# ================================================================ upgrade 12: vertical staging
ST_V = Matrix.LocRotScale(Vector((0.16, 0.3, 0)), Euler((0, 0, math.radians(-20))), None)
svi = ST_V.inverted()
stV = build_vesper(C_STG, {"bend": 0.6, "head_tilt": (22, 0, -14), "lids": (0.3, 0.25),
    "fragments": [(0.26, 190, 0), (0.28, 222, 1), (0.26, 254, 2)],
    "arms": {"L": [L(svi, (-0.16, 0.0, 0.72)), L(svi, (-0.06, -0.16, 0.66))], "L_fwd": tuple(svi.to_3x3() @ Vector((0.1, -0.7, -0.7))),
             "L_side": tuple(svi.to_3x3() @ Vector((1, 0, 0))), "L_curl": 0.75}}, tag="STG_VES")
stV.matrix_world = ST_V
stM = build_morrow(C_STG, {"crest": "raised", "lid": 0.1, "smile": 0.4, "brow": (0.4, 0.4), "gaze": (0.15, -1, 0.25),
                           "arms": {"R": [Vector((0.2, -0.08, 0.28)), Vector((0.24, -0.12, 0.38))]}}, tag="STG_MOR")
stM.rotation_euler.z = math.radians(10)
bpy.context.view_layer.update()
halo = bpy.data.objects["STG_VES_halo"]
lo, hi = world_bbox([halo])
stN = build_nix(C_STG, {"lids": (0.3, -20), "bead_angle": 300, "fins": {"A": (150, 0.0), "B": (215, 0.0)}}, tag="STG_NIX")
stN.location = ((lo.x + hi.x) / 2 + 0.03, (lo.y + hi.y) / 2, hi.z + 0.07)   # perched on top of Vesper's halo

# ================================================================ stage 3: expression sets
EXPR = {}
MFACE = ("_face", "_eye", "_lid", "_lowlid", "_brow", "_mouth", "_crest", "_pupil")
for name, P in {
    "morrow_delight": {"lid": 0.0, "lower": 0.5, "smile": 1.0, "brow": (0.15, 0.15), "crest": "raised", "mouth_w": 1.2},
    "morrow_worry": {"lid": 0.0, "lower": 0.0, "smile": -0.9, "brow": (1.0, 1.0), "crest": "curled", "mouth_w": 0.8},
    "morrow_determined": {"lid": 0.48, "lower": 0.28, "smile": -0.1, "brow": (-1.0, -1.0), "crest": "high", "mouth_w": 0.9},
    "morrow_embarrassed": {"lid": 0.55, "lower": 0.35, "smile": -0.4, "brow": (0.7, 0.25), "crest": "curled",
                           "gaze": (0.6, -0.6, -0.5), "mouth_w": 0.55},
}.items():
    EXPR[name] = (build_morrow(C_EXP, P, tag="EXP_" + name.upper()), MFACE)
VFACE = ("_mask", "_eye", "_lid", "_lowlid", "_brow", "_halo", "_fragment")
for name, P in {
    "vesper_concern": {"head_tilt": (14, -16, 0), "brows": (0.026, 0.026), "lids": (0.15, 0.15), "lower": (0.0, 0.0)},
    "vesper_dryhumor": {"head_tilt": (-4, 10, 14), "brows": (0.034, -0.014), "lids": (0.7, 0.45), "lower": (0.35, 0.3)},
    "vesper_flustered": {"head_tilt": (-16, 22, -8), "brows": (0.03, 0.03), "lids": (0.0, 0.0), "lower": (0.0, 0.0),
                         "fragments": [(0.2, 8, 0), (0.27, 58, 1), (0.23, 70, 2)]},
}.items():
    EXPR[name] = (build_vesper(C_EXP, P, tag="EXP_" + name.upper()), VFACE)
for name, (P, rot) in {
    "nix_mischief": ({"lids": (0.42, -32), "bead_angle": 300, "eye_tilt": 6}, (0, -10, 0)),
    "nix_innocent": ({"lids": (0.22, 28), "bead_angle": 100, "eye_tilt": -6}, (0, 8, 0)),
    "nix_embarrassed": ({"lids": (0.55, 10), "bead_angle": 200}, (0, 0, 62)),
}.items():
    rt = build_nix(C_EXP, P, tag="EXP_" + name.upper())
    rt.rotation_euler = [math.radians(x) for x in rot]
    rt.location = (0, 0, 0.14)
    EXPR[name] = (rt, ("_body", "_eye", "_lid", "_fin", "_bead", "_edge"))

# ================================================================ render review set
ALL = (C_MOR, C_VES, C_NIX, C_POSE, C_SIG, C_STG, C_EXP)
def set_visible(colls, objs=None):
    for c in ALL:
        c.hide_render = c not in colls
    if objs is not None:  # only these roots' children within C_SIG
        keep = set()
        for r in objs:
            keep.add(r); keep.update(r.children_recursive)
        for o in C_SIG.objects:
            o.hide_render = o not in keep and not o.name.endswith("guide_orbit")
            if o.name.endswith("guide_orbit"):
                o.hide_render = True

def render(path, w, h, samples=40, silhouette=False):
    r = scene.render
    r.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 6 if silhouette else samples
    scene.cycles.use_denoising = not silhouette
    r.resolution_x, r.resolution_y, r.resolution_percentage = w, h, 100
    r.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'Standard' if silhouette else 'AgX'
    scene.view_layers[0].material_override = SIL if silhouette else None
    bpy.data.objects["ENV_floor"].hide_render = silhouette
    bg = next(n for n in scene.world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (1, 1, 1, 1) if silhouette else (0.22, 0.22, 0.23, 1)
    bg.inputs[1].default_value = 1.0 if silhouette else 0.6
    r.filepath = path
    bpy.ops.render.render(write_still=True)
    print("rendered", path, flush=True)

def visible_objs(colls):
    return [o for c in colls for o in c.all_objects if not o.hide_render]

# ================================================================ STAGE 4: materials
def node(nt, kind, loc=(0, 0)):
    n = nt.nodes.new(kind); n.location = loc; return n

def setp(bsdf, name, val):
    if name in bsdf.inputs:
        bsdf.inputs[name].default_value = val

# part -> material definition. colours are linear RGB.
def hx(h):
    """sRGB hex -> linear RGB tuple."""
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

# PALETTE v2 - "moonlit porcelain and ink".
# Quiet desaturated bases, one shared family of warm light accents (amber, antique gold, ember rose).
PAL = {
    # Morrow - curious, warm, fragile, brave: porcelain with a celadon-ink glaze face
    "porcelain": "#ECE3D3", "porcelain_dk": "#D6C8B2", "celadon_ink": "#22403E", "celadon_joint": "#2A4846",
    "pearl": "#F3EEE4", "pupil": "#0D1414", "apricot": "#E59B74", "amber": "#FFB04A", "kintsugi": "#C9A15E",
    # Vesper - patient, formal, melancholy: ink slate, heather mauve, antique gold, warm graphite stone
    "ink_slate": "#1B2130", "ink_slate_lt": "#232A3A", "heather": "#5B4757", "antique_gold": "#B08A52",
    "antique_gold_dk": "#7A5F3A", "graphite": "#2D2A2A", "graphite_lt": "#3D3938", "vesper_pearl": "#E6E2DA",
    "dove_mauve": "#8E8089", "ink_deep": "#151A25",
    # Nix - theatrical, nosy, secretly shy: eclipse aubergine with an oil-slick sheen and an ember-rose edge
    "eclipse": "#1D1424", "eclipse_fin": "#22182A", "lilac_pearl": "#E8E3EE", "ember_rose": "#FF7A5C", "bead": "#FFE3C8",
    # shared dream world
    "dream_glass": "#C9C3DE", "night_ground": "#191522", "night_ground_dk": "#110E18",
}
P = {k: hx(v) for k, v in PAL.items()}

MATDEF = {
    "mor_shell": dict(color=P["porcelain"], color2=P["porcelain_dk"], noise=55, rough=0.5, sss=0.12, sss_r=(0.9, 0.55, 0.4), coat=0.12),
    "mor_face": dict(color=P["celadon_ink"], rough=0.62, coat=0.35, sheen=0.25, sheen_tint=(0.7, 0.9, 0.85)),
    "mor_lid": dict(color=P["celadon_ink"], rough=0.62, coat=0.35),
    "mor_joint": dict(color=P["celadon_joint"], rough=0.65, coat=0.2),
    "mor_eye": dict(color=P["pearl"], rough=0.2, coat=0.7),
    "mor_pupil": dict(color=P["pupil"], rough=0.08, coat=1.0),
    "mor_mouth": dict(color=P["apricot"], rough=0.45),
    "mor_ember": dict(color=P["amber"], emit=P["amber"], emit_s=9.0),
    "mor_crest": dict(color=P["apricot"], rough=0.55, sheen=0.5, sheen_tint=(1.0, 0.8, 0.65), sss=0.3, sss_r=(1.0, 0.5, 0.3)),
    "mor_seam": dict(color=P["kintsugi"], metal=1.0, rough=0.3),
    "dream": dict(color=P["dream_glass"], rough=0.12, trans=0.6, coat=0.6),
    "ves_mantle": dict(color=P["ink_slate"], rough=0.74),
    "ves_collar": dict(color=P["ink_slate_lt"], rough=0.74),
    "ves_inner": dict(color=P["heather"], rough=0.8, sheen=0.3, sheen_tint=(0.9, 0.8, 0.9)),
    "ves_brass": dict(color=P["antique_gold"], color2=P["antique_gold_dk"], noise=30, metal=1.0, rough=0.36, rough2=0.62, aniso=0.35),
    "ves_trim": dict(color=P["antique_gold_dk"], color2=P["antique_gold"], noise=30, metal=1.0, rough=0.45),
    "ves_mask": dict(color=P["graphite"], color2=P["ink_deep"], noise=70, rough=0.72, bump=0.25),
    "ves_lid": dict(color=P["graphite"], rough=0.72),
    "ves_brow": dict(color=P["graphite_lt"], rough=0.66),
    "ves_eye": dict(color=P["vesper_pearl"], rough=0.2, coat=0.6),
    "ves_arm": dict(color=P["ink_deep"], rough=0.7),
    "ves_hand": dict(color=P["dove_mauve"], rough=0.55, sheen=0.2),
    "ves_neck": dict(color=P["ink_deep"], rough=0.8),
    "nix_body": dict(color=P["eclipse"], rough=0.3, coat=0.3, film=380),
    "nix_fin": dict(color=P["eclipse_fin"], rough=0.3, coat=0.3, film=380),
    "nix_eye": dict(color=P["lilac_pearl"], rough=0.4),
    "nix_edge": dict(color=P["ember_rose"], emit=P["ember_rose"], emit_s=12.0),
    "nix_bead": dict(color=P["bead"], emit=P["bead"], emit_s=11.0),
    "nix_guide": dict(color=(0.5, 0.5, 0.5)),
    "floor": dict(color=(0.26, 0.26, 0.27), rough=0.9),
    "drm_ground": dict(color=P["night_ground"], color2=P["night_ground_dk"], noise=6, rough=0.85, bump=0.15),
    "drm_moon": dict(color=hx("#9EA3B3"), emit=hx("#C9CEDC"), emit_s=0.35, rough=0.9),
}

def build_material(m, d):
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = node(nt, "ShaderNodeOutputMaterial", (600, 0))
    b = node(nt, "ShaderNodeBsdfPrincipled", (300, 0))
    nt.links.new(b.outputs[0], out.inputs[0])
    setp(b, "Base Color", (*d["color"], 1)); setp(b, "Roughness", d.get("rough", 0.5)); setp(b, "Metallic", d.get("metal", 0.0))
    setp(b, "Coat Weight", d.get("coat", 0.0)); setp(b, "Sheen Weight", d.get("sheen", 0.0))
    setp(b, "Sheen Tint", (*d.get("sheen_tint", (1, 1, 1)), 1)); setp(b, "Anisotropic", d.get("aniso", 0.0))
    setp(b, "Transmission Weight", d.get("trans", 0.0))
    if d.get("film"):   # oil-slick sheen: teal and rose shift on grazing angles
        setp(b, "Thin Film Thickness", d["film"]); setp(b, "Thin Film IOR", 1.45)
    if d.get("sss"):
        setp(b, "Subsurface Weight", d["sss"]); setp(b, "Subsurface Radius", d.get("sss_r", (1, 1, 1))); setp(b, "Subsurface Scale", 0.01)
    if d.get("emit"):
        setp(b, "Emission Color", (*d["emit"], 1)); setp(b, "Emission Strength", d["emit_s"])
    if d.get("noise"):   # gentle, imperfect variation instead of a flat colour
        nz = node(nt, "ShaderNodeTexNoise", (-500, 0)); nz.inputs["Scale"].default_value = d["noise"]
        nz.inputs["Detail"].default_value = 6
        rp = node(nt, "ShaderNodeMapRange", (-300, 0)); rp.inputs["From Min"].default_value = 0.35; rp.inputs["From Max"].default_value = 0.7
        nt.links.new(nz.outputs["Fac"], rp.inputs["Value"])
        mx = node(nt, "ShaderNodeMix", (0, 100)); mx.data_type = 'RGBA'
        rgba_in = [i for i in mx.inputs if i.type == 'RGBA']
        rgba_in[0].default_value = (*d["color"], 1); rgba_in[1].default_value = (*d["color2"], 1)
        nt.links.new(rp.outputs["Result"], mx.inputs["Factor"])
        nt.links.new([o for o in mx.outputs if o.type == 'RGBA'][0], b.inputs["Base Color"])
        if "rough2" in d:
            rr = node(nt, "ShaderNodeMapRange", (0, -200))
            rr.inputs["To Min"].default_value = d["rough"]; rr.inputs["To Max"].default_value = d["rough2"]
            nt.links.new(rp.outputs["Result"], rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], b.inputs["Roughness"])
        if d.get("bump"):
            bp = node(nt, "ShaderNodeBump", (0, -350)); bp.inputs["Strength"].default_value = d["bump"]
            bp.inputs["Distance"].default_value = 0.002
            nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    m.diffuse_color = (*d["color"], 1)

def apply_color():
    for part, m in MATS.items():
        build_material(m, MATDEF.get(part, dict(color=(0.5, 0.5, 0.5))))
    if "drm_ground" in MATS:   # distant ground fades into the horizon colour instead of a black band
        nt = MATS["drm_ground"].node_tree
        out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
        bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
        cd = node(nt, "ShaderNodeCameraData", (-200, 400))
        mr = node(nt, "ShaderNodeMapRange", (0, 400)); mr.inputs["From Min"].default_value = 3.0; mr.inputs["From Max"].default_value = 14.0
        em = node(nt, "ShaderNodeEmission", (200, 300)); em.inputs["Color"].default_value = (*hx("#2E2636"), 1); em.inputs["Strength"].default_value = 1.0
        mx = node(nt, "ShaderNodeMixShader", (450, 100))
        nt.links.new(cd.outputs["View Distance"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], mx.inputs["Fac"])
        nt.links.new(bsdf.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])

# ================================================================ STAGE 4: atmospheric dream world
C_DRM = make_coll("ENV_DreamWorld")
C_DLG = make_coll("ENV_DreamWorld_Lights")
def dream_world():
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=128, radius=80)
    g = finish("DRM_ground", bm, C_DRM, "drm_ground")
    # the great broken moon: a crescent with a missing piece, far behind
    mc = Vector((1.6, 7.0, 2.4))
    a = cylinder("DRM_moon", C_DRM, "drm_moon", mc, mc + Vector((0, 0.15, 0)), 1.3, seg=128)
    b = cylinder("tmpM", C_DRM, "drm_moon", mc + Vector((0.5, -0.5, 0.32)), mc + Vector((0.5, 0.7, 0.32)), 1.15, seg=128)
    boolean(a, b)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)   # the moon's missing piece
    xform(bm, Matrix.Translation(mc + Vector((-1.1, 0, -0.55))) @ Matrix.Rotation(math.radians(30), 4, 'Y') @ Matrix.Diagonal((0.5, 1, 0.22, 1)))
    boolean(a, finish("tmpMC", bm, C_DRM, "drm_moon"))
    # broken moments drifting in the air
    import random
    rr = random.Random(21)
    for i in range(14):
        p = Vector((rr.uniform(-2.2, 2.2), rr.uniform(0.8, 4.5), rr.uniform(0.3, 2.4)))
        s = rr.uniform(0.025, 0.07)
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=s)
        for vv in bm.verts:
            vv.co *= 1 + rr.uniform(-0.3, 0.3)
        xform(bm, Matrix.Translation(p) @ Euler((rr.random() * 3, rr.random() * 3, rr.random() * 3)).to_matrix().to_4x4())
        finish(f"DRM_shard_{i}", bm, C_DRM, "dream", smooth=False)
    w = bpy.data.worlds.new("WORLD_dream")
    nt = w.node_tree if w.node_tree else (setattr(w, "use_nodes", True) or w.node_tree)
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    tc = node(nt, "ShaderNodeTexCoord", (-800, 0)); sx = node(nt, "ShaderNodeSeparateXYZ", (-600, 0))
    cr = node(nt, "ShaderNodeValToRGB", (-400, 0)); bg = node(nt, "ShaderNodeBackground", (-100, 0))
    wo = node(nt, "ShaderNodeOutputWorld", (100, 0))
    nt.links.new(tc.outputs["Generated"], sx.inputs[0]); nt.links.new(sx.outputs["Z"], cr.inputs["Fac"])
    # world "Generated" z runs from -1 (down) to 1 (up); the horizon is 0
    cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (*hx("#7D615F"), 1)
    cr.color_ramp.elements[1].position = 0.45; cr.color_ramp.elements[1].color = (*hx("#0E1018"), 1)
    e = cr.color_ramp.elements.new(0.13); e.color = (*hx("#3B3044"), 1)
    nt.links.new(cr.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 1.0
    nt.links.new(bg.outputs[0], wo.inputs[0])
    def area(name, loc, energy, size, color, target=(0, 0, 0.5)):
        L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.size = size; L.color = color
        o = bpy.data.objects.new(name, L); C_DLG.objects.link(o); o.location = loc
        o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    area("DLG_moon_rim", (0.6, 3.2, 2.6), 520, 2.5, (0.78, 0.8, 1.0))       # cool moonlight from behind
    area("DLG_warm_key", (-1.7, -1.6, 1.2), 160, 1.2, (1.0, 0.72, 0.5))       # low warm dream light
    area("DLG_plum_fill", (2.0, -1.4, 0.6), 45, 2.0, (0.72, 0.62, 0.78))
    return w

STUDIO_WORLD = scene.world
DREAM_WORLD = dream_world()
C_DRM.hide_render = True; C_DLG.hide_render = True

def mode_studio():
    MODE[0] = "studio"
    scene.world = STUDIO_WORLD; C_LGT.hide_render = False; C_DRM.hide_render = True; C_DLG.hide_render = True
    bpy.data.objects["ENV_floor"].hide_render = False

def mode_dream():
    MODE[0] = "dream"
    scene.world = DREAM_WORLD; C_LGT.hide_render = True; C_DRM.hide_render = False; C_DLG.hide_render = False
    bpy.data.objects["ENV_floor"].hide_render = True

EXPOSURE = {"studio": -0.6, "dream": 0.0}
MODE = ["studio"]
def render_c(path, w, h, samples=96):
    r = scene.render
    r.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = samples; scene.cycles.use_denoising = True
    r.resolution_x, r.resolution_y, r.resolution_percentage = w, h, 100
    r.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.exposure = EXPOSURE[MODE[0]]
    try:
        scene.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    scene.view_layers[0].material_override = None
    r.filepath = path
    bpy.ops.render.render(write_still=True)
    print("rendered", path, flush=True)

if OUT:
    os.makedirs(OUT, exist_ok=True)
    apply_color(); mode_studio()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "cast_materials_v05_palette2.blend"))
    # studio: each character front and three-quarter
    for key, root, coll in (("morrow", mor, C_MOR), ("vesper", ves, C_VES), ("nix", nix, C_NIX)):
        set_visible([coll]); keep = (root.location.copy(), root.rotation_euler.copy())
        root.location = (0, 0, 0.0 if key != "nix" else 0.1)
        for vname, ang in (("front", 0), ("threequarter", -32)):
            root.rotation_euler = (0, 0, math.radians(ang)); bpy.context.view_layer.update()
            frame(cam, coll.all_objects, (0, -1, 0.06))
            render_c(os.path.join(OUT, f"{key}_{vname}_color.png"), 600, 800)
        root.location, root.rotation_euler = keep
    # studio lineup and relationship
    set_visible([C_MOR, C_VES, C_NIX]); bpy.context.view_layer.update()
    frame(cam, visible_objs([C_MOR, C_VES, C_NIX]), (0, -1, 0.08), lens=70, aspect=1.6)
    render_c(os.path.join(OUT, "lineup_studio.png"), 1280, 800)
    set_visible([C_POSE]); bpy.context.view_layer.update()
    frame(cam, visible_objs([C_POSE]), (-0.42, -1, 0.12), lens=60, aspect=1.0, margin=1.1)
    render_c(os.path.join(OUT, "relationship_studio.png"), 1000, 1000)
    # studio expressions
    for key, (root, focus) in EXPR.items():
        set_visible([C_EXP])
        for o in C_EXP.objects:
            o.hide_render = not (o is root or o in root.children_recursive) or o.name.endswith("guide_orbit")
        bpy.context.view_layer.update()
        objs = [o for o in root.children_recursive if any(f in o.name for f in focus) and not o.hide_render]
        frame(cam, objs, (-0.18, -1, 0.05), lens=85, aspect=1.0, margin=1.25)
        render_c(os.path.join(OUT, f"expr_{key}_color.png"), 520, 520, samples=64)
    # atmospheric dream world
    mode_dream()
    set_visible([C_POSE]); bpy.context.view_layer.update()
    frame(cam, visible_objs([C_POSE]), (-0.42, -1, 0.1), lens=50, aspect=1.0, margin=1.3)
    render_c(os.path.join(OUT, "relationship_dream.png"), 1000, 1000, samples=128)
    set_visible([C_STG]); bpy.context.view_layer.update()
    frame(cam, visible_objs([C_STG]), (-0.3, -1, 0.08), lens=45, aspect=9 / 16, margin=1.12)
    render_c(os.path.join(OUT, "staging_vertical_dream.png"), 720, 1280, samples=128)
    mode_studio(); set_visible([C_MOR, C_VES, C_NIX])
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "cast_materials_v05_palette2.blend"))
    print("ALL DONE", flush=True)
else:
    apply_color()
