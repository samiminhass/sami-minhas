"""
STAGE 5 - ANIMATION PREPARATION for Morrow, Vesper, and Nix.
Builds the stage 4 cast (palette v2), then adds armatures, IK, drivers, shape keys,
and named controls on each rig object. Then it TESTS them: every control must move
something, deforming parts are measured for stretching, and poses are rendered using
controls only. Results are written to rig_test_report.md.
Written for Blender 5.2 LTS.
"""
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix, Quaternion, Euler
from mathutils.bvhtree import BVHTree

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else None

# ---------------------------------------------------------------- scene
scene = bpy.data.scenes.new("CAST_Rigged_v05")
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
          tilts=[1.57] * len(pts))   # stage 5: flat ribbon facing front, so it can curl cleanly

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


# ================================================================ STAGE 5: rigging helpers
bpy.context.preferences.filepaths.use_scripts_auto_execute = True
VL = scene.view_layers[0]
def upd():
    """Re-evaluate everything, including drivers. Setting a custom property from Python does not
    trigger driver evaluation on its own, so tag the rigs and re-set the frame."""
    for o in bpy.data.objects:
        if o.type == 'ARMATURE':
            o.update_tag()
    scene.frame_set(scene.frame_current)
    VL.update()

def bbox_center(ob):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return sum(pts, Vector()) / 8

def curve_pts(ob):
    return [ob.matrix_world @ Vector(p.co[:3]) for p in ob.data.splines[0].points]

def to_mesh(ob):
    """Convert a curve object into a mesh object with the same name, world transform baked in."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    me.transform(ob.matrix_world)
    name, colls, part = ob.name, list(ob.users_collection), ob.get("part")
    ob.name = name + "_curve"
    new = bpy.data.objects.new(name, me)
    for c in colls:
        c.objects.link(new)
    new["part"] = part
    if not me.materials and part:
        me.materials.append(mat_for(part))
    for pg in me.polygons:
        pg.use_smooth = True
    bpy.data.objects.remove(ob)
    return new

def centerline(ob, nseg):
    """Points along the curve's real evaluated centreline, evenly spaced by arc length."""
    cu = ob.data.copy(); cu.bevel_depth = 0; cu.extrude = 0
    tmp = bpy.data.objects.new("tmp_cl", cu); scene.collection.objects.link(tmp); tmp.matrix_world = ob.matrix_world
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    pts = [tmp.matrix_world @ v.co for v in me.vertices]
    bpy.data.objects.remove(tmp); bpy.data.curves.remove(cu); bpy.data.meshes.remove(me)
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + (pts[i] - pts[i - 1]).length)
    out = []
    for j in range(nseg + 1):
        target = cum[-1] * j / nseg
        i = max(k for k in range(len(cum)) if cum[k] <= target + 1e-12)
        i = min(i, len(pts) - 2)
        t = (target - cum[i]) / max(cum[i + 1] - cum[i], 1e-12)
        out.append(pts[i].lerp(pts[i + 1], t))
    return out

def make_rig(name, coll, bones):
    """bones: list of dict(name, head, tail, parent=None, up=None, deform=False)."""
    arm = bpy.data.armatures.new(name)
    rig = bpy.data.objects.new(name, arm)
    coll.objects.link(rig)
    arm.display_type = 'STICK'
    with bpy.context.temp_override(scene=scene, view_layer=VL, active_object=rig, object=rig, selected_objects=[rig]):
        VL.objects.active = rig
        bpy.ops.object.mode_set(mode='EDIT')
        for bd in bones:
            eb = arm.edit_bones.new(bd["name"])
            eb.head = Vector(bd["head"]); eb.tail = Vector(bd["tail"])
            if bd.get("up") is not None:
                eb.align_roll(Vector(bd["up"]))
            eb.use_deform = bd.get("deform", True)   # only meshes with an Armature modifier use this
        for bd in bones:
            if bd.get("parent"):
                arm.edit_bones[bd["name"]].parent = arm.edit_bones[bd["parent"]]
        bpy.ops.object.mode_set(mode='OBJECT')
    for pb in rig.pose.bones:
        pb.rotation_mode = 'XYZ'
    return rig

def bone_parent(ob, rig, bone):
    mw = ob.matrix_world.copy()
    b = rig.data.bones[bone]
    pw = rig.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))
    ob.parent = rig; ob.parent_type = 'BONE'; ob.parent_bone = bone
    ob.matrix_parent_inverse = pw.inverted()
    ob.matrix_basis = mw

BLEND = 0.3
def skin(ob, rig, chain, pts, blend=None, min_bw=0.0):
    """blend: blend zone as a fraction of the shorter bone at each joint (1.0 = fully smooth, cloth-like).
    min_bw: minimum blend half-width in metres, so short bones on thick parts never tear."""
    bl_ = BLEND if blend is None else blend
    """Smooth weights along a bone chain. pts = joint positions (len(chain)+1)."""
    mw = ob.matrix_world.copy()
    ob.parent = rig; ob.parent_type = 'OBJECT'; ob.matrix_parent_inverse = rig.matrix_world.inverted(); ob.matrix_basis = mw
    m = ob.modifiers.new("rig", 'ARMATURE'); m.object = rig
    m.use_deform_preserve_volume = True   # dual quaternion: no candy-wrapper collapse at bent joints
    segs = [(Vector(pts[i]), Vector(pts[i + 1])) for i in range(len(chain))]
    lens = [(b - a).length for a, b in segs]
    cum = [0.0]
    for L in lens:
        cum.append(cum[-1] + L)
    centers = [cum[i] + lens[i] / 2 for i in range(len(chain))]
    groups = [ob.vertex_groups.new(name=n) for n in chain]
    for v in ob.data.vertices:
        p = ob.matrix_world @ v.co
        best = None
        for i, (a, b) in enumerate(segs):
            ab = b - a
            t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
            d = (a + ab * t - p).length
            if best is None or d < best[0]:
                best = (d, cum[i] + t * lens[i])
        s_ = best[1]
        nch = len(chain)
        k = max(i for i in range(nch) if cum[i] <= s_ + 1e-9) if s_ > 0 else 0
        k = min(k, nch - 1)
        w = [0.0] * nch
        w[k] = 1.0
        # blend only inside a short zone around each joint, so bones stay rigid between joints
        if k > 0:
            bw = max(bl_ * min(lens[k - 1], lens[k]), min_bw); d = s_ - cum[k]
            if d < bw:
                t = 0.5 + 0.5 * d / bw; w[k] *= t; w[k - 1] += 1 - t
        if k < nch - 1:
            bw = max(bl_ * min(lens[k], lens[k + 1]), min_bw); d = cum[k + 1] - s_
            if d < bw:
                t = 0.5 + 0.5 * d / bw; carry = w[k] * (1 - t); w[k] -= carry; w[k + 1] += carry
        tot = sum(w); w = [x / tot for x in w]
        for g, wt in zip(groups, w):
            if wt > 0:
                g.add([v.index], wt, 'REPLACE')

def place(rig, bone, world_offset):
    """Move a pose bone by a WORLD-space offset (works for bones parented to the rig root)."""
    b = rig.data.bones[bone]
    rig.pose.bones[bone].location = b.matrix_local.to_3x3().inverted() @ Vector(world_offset)

def add_prop(rig, name, default, lo, hi, desc):
    rig[name] = float(default)
    rig.id_properties_ui(name).update(min=lo, max=hi, soft_min=lo, soft_max=hi, description=desc)

def drive(idblock, path, index, expr, rig, props):
    fc = idblock.driver_add(path, index) if index is not None else idblock.driver_add(path)
    d = fc.driver; d.type = 'SCRIPTED'
    for p in props:
        v = d.variables.new(); v.name = p; v.type = 'SINGLE_PROP'
        v.targets[0].id = rig; v.targets[0].data_path = f'["{p}"]'
    d.expression = expr
    return fc

def pb_drive(rig, bone, channel, axis, expr, props):
    return drive(rig.pose.bones[bone], channel, axis, expr, rig, props)

def pole_angle(rig, upper, lower, pole_pos):
    """Pole angle that keeps the chain exactly in its rest pose (armature space)."""
    bu, bl = rig.data.bones[upper], rig.data.bones[lower]
    base_h, base_t, ik_t = bu.head_local, bu.tail_local, bl.tail_local
    pole_normal = (ik_t - base_h).cross(Vector(pole_pos) - base_h)
    proj = pole_normal.cross(base_t - base_h)
    x_axis = bu.matrix_local.col[0].xyz
    a = x_axis.angle(proj)
    if (base_t - base_h).dot(x_axis.cross(proj)) < 0:
        a = -a
    return a

def ik_arm(rig, side, forearm, ik, upper=None, pole=None):
    c = rig.pose.bones[forearm].constraints.new('IK')
    c.target = rig; c.subtarget = ik; c.chain_count = 2
    if pole:
        c.pole_target = rig; c.pole_subtarget = pole
        c.pole_angle = pole_angle(rig, upper, forearm, rig.data.bones[pole].head_local)
        solve_pole(rig, upper, forearm, c)
    return c

def solve_pole(rig, upper, lower, c):
    """Search for the pole angle that leaves the arm exactly in its rest pose."""
    bu, bl = rig.data.bones[upper], rig.data.bones[lower]
    def err(a):
        c.pole_angle = a; upd()
        mu = rig.pose.bones[upper].matrix; ml = rig.pose.bones[lower].matrix
        return ((mu.col[0].xyz - bu.matrix_local.col[0].xyz).length + (mu.col[1].xyz - bu.matrix_local.col[1].xyz).length
                + (ml.col[3].xyz - bl.matrix_local.col[3].xyz).length * 10)
    best = min((err(math.radians(d)), math.radians(d)) for d in range(-180, 180, 10))[1]
    for step in (2.0, 0.25, 0.03):
        cands = [best + math.radians(step) * i for i in range(-6, 7)]
        best = min((err(a), a) for a in cands)[1]
    c.pole_angle = best
    upd()

def pole_pos(sh, el, wr, fallback):
    mid = (Vector(sh) + Vector(wr)) / 2
    bend = Vector(el) - mid
    d = bend.normalized() if bend.length > 1e-4 else Vector(fallback)
    return Vector(el) + d * 0.15

def finger_chain_bones(prefix, pts, parent, up):
    out = []
    for i in range(len(pts) - 1):
        out.append(dict(name=f"{prefix}_{i+1}", head=pts[i], tail=pts[i + 1], parent=(out[-1]["name"] if out else parent), up=up))
    return out

# ================================================================ STAGE 5: Morrow rig
def rig_morrow(root, tag="MOR"):
    O = bpy.data.objects
    coll = root.users_collection[0]
    torso = O[f"{tag}_torso"]
    ARMPTS, FPTS = {}, {}
    hit, n = raycast(torso, (0.012, -1, 0.43), (0, 1, 0))
    right = Vector((1, 0, 0)); up = n.cross(right).normalized(); right = up.cross(n).normalized()
    B = [dict(name="root", head=(0, 0, 0), tail=(0, -0.08, 0)),
         dict(name="body", head=(0, -0.01, 0.1), tail=(0, -0.07, 0.46), parent="root", up=(0, -1, 0)),
         dict(name="ember", head=bbox_center(O[f"{tag}_ember"]), tail=bbox_center(O[f"{tag}_ember"]) + Vector((0, 0, 0.03)), parent="body"),
         dict(name="eye_target", head=hit + n * 0.4, tail=hit + n * 0.4 + Vector((0, 0, 0.03)), parent="body")]   # in FRONT of the face
    for k in ("L", "R"):
        ec = bbox_center(O[f"{tag}_eye_{k}"])
        B += [dict(name=f"eye_{k}", head=ec, tail=ec + n * 0.03, parent="body", up=up),
              dict(name=f"lid_up_{k}", head=ec, tail=ec + right * 0.02, parent="body", up=up),
              dict(name=f"lid_low_{k}", head=ec, tail=ec + right * 0.02, parent="body", up=up)]
        bp = curve_pts(O[f"{tag}_brow_{k}"])
        B.append(dict(name=f"brow_{k}", head=bp[1], tail=bp[1] + n * 0.02, parent="body", up=up))
        legc = bbox_center(O[f"{tag}_leg_{k}"]); footc = bbox_center(O[f"{tag}_foot_{k}"])
        B += [dict(name=f"leg_{k}", head=legc + Vector((0, 0, 0.045)), tail=legc - Vector((0, 0, 0.045)), parent="root", up=(0, -1, 0)),
              dict(name=f"foot_{k}", head=Vector((legc.x, legc.y, 0.03)), tail=footc + Vector((0, -0.05, 0)), parent=f"leg_{k}", up=(0, 0, 1))]
        ap = centerline(O[f"{tag}_arm_{k}"], 2)
        ARMPTS[k] = ap
        palm = bbox_center(O[f"{tag}_hand_{k}_palm"])
        B += [dict(name=f"upperarm_{k}", head=ap[0], tail=ap[1], parent="body", up=(0, -1, 0)),
              dict(name=f"forearm_{k}", head=ap[1], tail=ap[-1], parent=f"upperarm_{k}", up=(0, -1, 0)),
              dict(name=f"hand_{k}", head=ap[-1], tail=palm + (palm - ap[-1]), parent=f"forearm_{k}", up=(0, 0, 1)),
              dict(name=f"hand_IK_{k}", head=ap[-1], tail=palm + (palm - ap[-1]), parent="body", up=(0, 0, 1))]
        pp = pole_pos(ap[0], ap[1], ap[-1], (0, 0.3, -0.2))
        B.append(dict(name=f"elbow_pole_{k}", head=pp, tail=pp + Vector((0, 0, 0.02)), parent="body"))
        for f in ("finger1", "finger2", "thumb"):
            fp = centerline(O[f"{tag}_hand_{k}_{f}"], 3)
            FPTS[(k, f)] = fp
            B += finger_chain_bones(f"{f}_{k}", fp, f"hand_{k}", (0, 0, 1))
    cp = centerline(O[f"{tag}_crest"], 4)
    for i in range(len(cp) - 1):   # crest bones bend around world X: the ribbon curls in its own plane
        yv = (cp[i + 1] - cp[i]).normalized()
        B.append(dict(name=f"crest_{i+1}", head=cp[i], tail=cp[i + 1], parent=("body" if i == 0 else f"crest_{i}"),
                      up=Vector((1, 0, 0)).cross(yv).normalized()))
    rig = make_rig(f"RIG_{tag}", coll, B)
    for i in range(len(cp) - 1):   # crest bends around world X
        pass

    # ---- rigid parts
    for nm in ("torso", "face", "seam_front", "seam_back"):
        if f"{tag}_{nm}" in O:
            bone_parent(O[f"{tag}_{nm}"], rig, "body")
    bone_parent(O[f"{tag}_ember"], rig, "ember")
    for k in ("L", "R"):
        bone_parent(O[f"{tag}_eye_{k}"], rig, "body")
        # re-centre the pupil on the eye's forward axis, so rotation limits keep it on the visible front
        po = O[f"{tag}_pupil_{k}"]; eo = O[f"{tag}_eye_{k}"]
        ec_ = sum((v.co for v in eo.data.vertices), Vector()) / len(eo.data.vertices)
        r_e = max((v.co - ec_).length for v in eo.data.vertices)
        pc_ = sum((v.co for v in po.data.vertices), Vector()) / len(po.data.vertices)
        po.data.transform(Matrix.Translation(ec_ + n * r_e * 0.8 - pc_))
        bone_parent(O[f"{tag}_pupil_{k}"], rig, f"eye_{k}")
        bone_parent(O[f"{tag}_lid_{k}"], rig, f"lid_up_{k}")
        bone_parent(O[f"{tag}_lowlid_{k}"], rig, f"lid_low_{k}")
        bone_parent(O[f"{tag}_brow_{k}"], rig, f"brow_{k}")
        bone_parent(O[f"{tag}_shoulder_{k}"], rig, "body")
        bone_parent(O[f"{tag}_leg_{k}"], rig, f"leg_{k}")
        bone_parent(O[f"{tag}_foot_{k}"], rig, f"foot_{k}")
        bone_parent(O[f"{tag}_hand_{k}_palm"], rig, f"hand_{k}")
        for f, tipn in (("finger1", "fingertip1"), ("finger2", "fingertip2"), ("thumb", "thumbtip")):
            fo = O[f"{tag}_hand_{k}_{f}"]; fp = FPTS[(k, f)]
            fm = to_mesh(fo)
            skin(fm, rig, [f"{f}_{k}_{i+1}" for i in range(len(fp) - 1)], fp, min_bw=0.007)
            bone_parent(O[f"{tag}_hand_{k}_{tipn}"], rig, f"{f}_{k}_{len(fp)-1}")
        ao = O[f"{tag}_arm_{k}"]; ap = ARMPTS[k]
        am = to_mesh(ao)
        skin(am, rig, [f"upperarm_{k}", f"forearm_{k}"], [ap[0], ap[1], ap[-1]], blend=0.4, min_bw=0.025)
        ik_arm(rig, k, f"forearm_{k}", f"hand_IK_{k}", f"upperarm_{k}", f"elbow_pole_{k}")
        cr = rig.pose.bones[f"hand_{k}"].constraints.new('COPY_ROTATION'); cr.target = rig; cr.subtarget = f"hand_IK_{k}"
        dt = rig.pose.bones[f"eye_{k}"].constraints.new('DAMPED_TRACK'); dt.target = rig; dt.subtarget = "eye_target"
        # pupils may glance hard, but never roll past the visible front of the eyeball
        lr = rig.pose.bones[f"eye_{k}"].constraints.new('LIMIT_ROTATION'); lr.owner_space = 'LOCAL'
        lr.use_limit_x = lr.use_limit_z = True; lr.use_limit_y = False
        lr.min_x, lr.max_x = math.radians(-24), math.radians(24)
        lr.min_z, lr.max_z = math.radians(-30), math.radians(30)
    co = O[f"{tag}_crest"]; cm = to_mesh(co)
    skin(cm, rig, [f"crest_{i+1}" for i in range(len(cp) - 1)], cp, blend=0.5, min_bw=0.012)
    mo = O[f"{tag}_mouth"]; mm = to_mesh(mo)
    bone_parent(mm, rig, "body")

    # ---- mouth shape keys, built in the face frame
    mc = sum((Vector(v.co) for v in mm.data.vertices), Vector()) / len(mm.data.vertices)
    mm.shape_key_add(name="Basis")
    for key, fn in (("smile", lambda x, y: (x, y + 0.009 * (x / 0.022) ** 2 - 0.003)),
                    ("frown", lambda x, y: (x, y - 0.009 * (x / 0.022) ** 2 + 0.003)),
                    ("wide", lambda x, y: (x * 1.3, y)), ("narrow", lambda x, y: (x * 0.55, y))):
        kb = mm.shape_key_add(name=key)
        for i, v in enumerate(mm.data.vertices):
            d = Vector(v.co) - mc
            x, y = d.dot(right), d.dot(up)
            z = d - right * x - up * y
            nx, ny = fn(x, y)
            kb.data[i].co = mc + right * nx + up * ny + z

    # ---- controls
    add_prop(rig, "blink", 0, 0, 1, "Closes both eyes")
    for k in ("L", "R"):
        add_prop(rig, f"lid_upper_{k}", 0.3, 0, 1, "Upper lid: 0 open, 1 shut")
        add_prop(rig, f"lid_lower_{k}", 0.1, 0, 1, "Lower lid: raises for delight and squints")
        add_prop(rig, f"brow_raise_{k}", 0, -1, 1, "Brow up (+) or down (-)")
        add_prop(rig, f"brow_worry_{k}", 0, -1, 1, "Inner corner up for worry (+), down for determination (-)")
        add_prop(rig, f"grip_{k}", 0.45, 0, 1, "Curls every finger joint")
        sgn = -1 if k == "L" else 1
        pb_drive(rig, f"lid_up_{k}", "rotation_euler", 1, f"radians(140*(max(u,b)-0.3))", [f"lid_upper_{k}", "blink"])
        rig.pose.bones[f"lid_up_{k}"].driver_remove("rotation_euler", 1)
        fc = drive(rig.pose.bones[f"lid_up_{k}"], "rotation_euler", 1, "radians(140*(max(u,b)-0.3))", rig, [])
        for nm, pp in (("u", f"lid_upper_{k}"), ("b", "blink")):
            v = fc.driver.variables.new(); v.name = nm; v.type = 'SINGLE_PROP'; v.targets[0].id = rig; v.targets[0].data_path = f'["{pp}"]'
        fc = drive(rig.pose.bones[f"lid_low_{k}"], "rotation_euler", 1, "radians(-120*(l-0.1))", rig, [])
        v = fc.driver.variables.new(); v.name = "l"; v.type = 'SINGLE_PROP'; v.targets[0].id = rig; v.targets[0].data_path = f'["lid_lower_{k}"]'
        fc = drive(rig.pose.bones[f"brow_{k}"], "location", 2, "0.007*r", rig, [])
        v = fc.driver.variables.new(); v.name = "r"; v.type = 'SINGLE_PROP'; v.targets[0].id = rig; v.targets[0].data_path = f'["brow_raise_{k}"]'
        fc = drive(rig.pose.bones[f"brow_{k}"], "rotation_euler", 1, f"{sgn}*0.4*w", rig, [])
        v = fc.driver.variables.new(); v.name = "w"; v.type = 'SINGLE_PROP'; v.targets[0].id = rig; v.targets[0].data_path = f'["brow_worry_{k}"]'
        for f in ("finger1", "finger2", "thumb"):
            nb = len([b for b in rig.data.bones if b.name.startswith(f"{f}_{k}_")])
            for i in range(nb):
                fc = drive(rig.pose.bones[f"{f}_{k}_{i+1}"], "rotation_euler", 0, "-0.7*(g-0.45)", rig, [])
                v = fc.driver.variables.new(); v.name = "g"; v.type = 'SINGLE_PROP'; v.targets[0].id = rig; v.targets[0].data_path = f'["grip_{k}"]'
    add_prop(rig, "mouth_smile", 0, -1, 1, "Smile (+) or frown (-)")
    add_prop(rig, "mouth_width", 0, -1, 1, "Wide (+) or small (-)")
    kbs = mm.data.shape_keys.key_blocks
    for key, expr, pr in (("smile", "max(s,0)", "mouth_smile"), ("frown", "max(-s,0)", "mouth_smile"),
                          ("wide", "max(s,0)", "mouth_width"), ("narrow", "max(-s,0)", "mouth_width")):
        fc = kbs[key].driver_add("value"); fc.driver.type = 'SCRIPTED'
        v = fc.driver.variables.new(); v.name = "s"; v.type = 'SINGLE_PROP'; v.targets[0].id = rig; v.targets[0].data_path = f'["{pr}"]'
        fc.driver.expression = expr
    add_prop(rig, "crest_mood", 1, -1, 1, "Emotional antenna: 1 raised (curious), 0 relaxed, -1 curled (frightened)")
    relax = [0.55, 0.35, 0.25, 0.2][:len(cp) - 1]
    curl = [-0.55, -0.55, -0.65, -0.7][:len(cp) - 1]
    for i in range(len(cp) - 1):
        fc = drive(rig.pose.bones[f"crest_{i+1}"], "rotation_euler", 0, f"{relax[i]}*(1-max(m,0)) + {curl[i]}*max(-m,0)", rig, [])
        v = fc.driver.variables.new(); v.name = "m"; v.type = 'SINGLE_PROP'; v.targets[0].id = rig; v.targets[0].data_path = '["crest_mood"]'
    add_prop(rig, "crest_lean", 0, -1, 1, "Swings the whole crest sideways from its root, without bending it")
    fc = drive(rig.pose.bones["crest_1"], "rotation_euler", 2, "0.6*l", rig, [])
    v = fc.driver.variables.new(); v.name = "l"; v.type = 'SINGLE_PROP'; v.targets[0].id = rig; v.targets[0].data_path = '["crest_lean"]'
    rig.parent = root
    return rig

# ================================================================ STAGE 5: Vesper rig
def rig_vesper(root, tag="VES"):
    O = bpy.data.objects
    coll = root.users_collection[0]
    sp = [body_pt((0, 0, 0), z) for z in (0.02, 0.45, 0.9, 1.22)]
    neck_top = body_pt((0, -0.07, 0), 1.3)
    Rh = Euler([math.radians(a) for a in (6, -8, 0)]).to_matrix().to_4x4()
    M = neck_top + Vector((0, -0.03, 0.15))
    hc = M + (Rh @ Vector((0, 0.045, 0.02)))
    Rt = Rh @ Euler((math.radians(-22), 0, math.radians(14))).to_matrix().to_4x4()
    U = Rt @ Vector((1, 0, 0)); V = Rt @ Vector((0, 0, 1)); N = U.cross(V).normalized()
    VFP = {}
    hright = (Rh @ Vector((1, 0, 0))).normalized(); hup = (Rh @ Vector((0, 0, 1))).normalized(); hout = (Rh @ Vector((0, -1, 0))).normalized()
    B = [dict(name="root", head=(0, 0, 0), tail=(0, -0.15, 0)),
         dict(name="spine_1", head=sp[0], tail=sp[1], parent="root", up=(0, -1, 0)),
         dict(name="spine_2", head=sp[1], tail=sp[2], parent="spine_1", up=(0, -1, 0)),
         dict(name="spine_3", head=sp[2], tail=sp[3], parent="spine_2", up=(0, -1, 0)),
         dict(name="neck", head=sp[3], tail=neck_top, parent="spine_3", up=(0, -1, 0)),
         dict(name="head", head=M, tail=M + hup * 0.08, parent="neck", up=hout),
         dict(name="halo", head=hc, tail=hc + N * 0.05, parent="head", up=V),
         dict(name="eye_target", head=M + hout * 0.5, tail=M + hout * 0.5 + Vector((0, 0, 0.04)), parent="head")]
    for i in range(3):
        B.append(dict(name=f"fragment_{i+1}", head=hc, tail=hc + N * 0.04, parent="halo", up=V))
    # mantle follow bones: they copy the spine, plus a baked delay offset (see bake_follow_through)
    for i in range(3):
        B.append(dict(name=f"mantle_{i+1}", head=sp[i], tail=sp[i + 1], parent=("root" if i == 0 else f"mantle_{i}"), up=(0, -1, 0)))
    for k, side in (("L", -1), ("R", 1)):
        ec = bbox_center(O[f"{tag}_eye_{k}"])
        B += [dict(name=f"lid_up_{k}", head=ec, tail=ec + hright * 0.02, parent="head", up=hup),
              dict(name=f"lid_low_{k}", head=ec, tail=ec + hright * 0.02, parent="head", up=hup)]
        bp = curve_pts(O[f"{tag}_brow_{k}"])
        B.append(dict(name=f"brow_{k}", head=bp[1], tail=bp[1] + hout * 0.02, parent="head", up=hup))
        sh = body_pt((side * 0.19 + 0.03, -0.02, 0), 1.1)
        el = sh + Vector((side * 0.07, -0.06, -0.34))
        wr = Vector((side * 0.03 + 0.02, -0.3, 0.72 if side < 0 else 0.64))
        palm = bbox_center(O[f"{tag}_hand_{k}_palm"])
        B += [dict(name=f"upperarm_{k}", head=sh, tail=el, parent="spine_3", up=(0, -1, 0)),
              dict(name=f"forearm_{k}", head=el, tail=wr, parent=f"upperarm_{k}", up=(0, -1, 0)),
              dict(name=f"hand_{k}", head=wr, tail=palm + (palm - wr), parent=f"forearm_{k}", up=(0, -1, 0)),
              dict(name=f"hand_IK_{k}", head=wr, tail=palm + (palm - wr), parent="spine_3", up=(0, -1, 0))]
        pp = pole_pos(sh, el, wr, (side * 0.3, 0.3, 0))
        B.append(dict(name=f"elbow_pole_{k}", head=pp, tail=pp + Vector((0, 0, 0.03)), parent="spine_3"))
        for f in ("finger1", "finger2", "finger3", "thumb"):
            fp = centerline(O[f"{tag}_hand_{k}_{f}"], 3)
            VFP[(k, f)] = fp
            B += finger_chain_bones(f"{f}_{k}", fp, f"hand_{k}", (0, -1, 0))
    rig = make_rig(f"RIG_{tag}", coll, B)

    # deforming mantle: smooth weights along the spine
    chain, pts = ["mantle_1", "mantle_2", "mantle_3"], sp
    for nm in ("core", "panel_back_calm", "mantle_crescent", "panel_right_med", "panel_frontL_med", "hood"):
        skin(O[f"{tag}_{nm}"], rig, chain, pts, blend=1.0)
    tm = to_mesh(O[f"{tag}_mantle_trim"]); skin(tm, rig, chain, pts, blend=1.0)
    bone_parent(O[f"{tag}_neck"], rig, "neck")
    for nm in ("mask",):
        bone_parent(O[f"{tag}_{nm}"], rig, "head")
    bone_parent(O[f"{tag}_halo"], rig, "halo")
    for i in (1, 2):
        bone_parent(O[f"{tag}_halo_break_{i}"], rig, "halo")
    for i in range(3):
        bone_parent(O[f"{tag}_fragment_{i+1}"], rig, f"fragment_{i+1}")
    for k in ("L", "R"):
        bone_parent(O[f"{tag}_eye_{k}"], rig, "head")
        bone_parent(O[f"{tag}_lid_{k}"], rig, f"lid_up_{k}")
        bone_parent(O[f"{tag}_lowlid_{k}"], rig, f"lid_low_{k}")
        bone_parent(O[f"{tag}_brow_{k}"], rig, f"brow_{k}")
        bone_parent(O[f"{tag}_shoulderjoint_{k}"], rig, "spine_3")
        for nm in ("upperarm", "sleeve"):
            bone_parent(O[f"{tag}_{nm}_{k}"], rig, f"upperarm_{k}")
        for nm in ("elbow", "forearm"):
            bone_parent(O[f"{tag}_{nm}_{k}"], rig, f"forearm_{k}")
        bone_parent(O[f"{tag}_hand_{k}_palm"], rig, f"hand_{k}")
        for f, tipn in (("finger1", "fingertip1"), ("finger2", "fingertip2"), ("finger3", "fingertip3"), ("thumb", "thumbtip")):
            fo = O[f"{tag}_hand_{k}_{f}"]; fp = VFP[(k, f)]
            fm = to_mesh(fo); skin(fm, rig, [f"{f}_{k}_{i+1}" for i in range(len(fp) - 1)], fp, min_bw=0.01)
            bone_parent(O[f"{tag}_hand_{k}_{tipn}"], rig, f"{f}_{k}_{len(fp)-1}")
        ik_arm(rig, k, f"forearm_{k}", f"hand_IK_{k}", f"upperarm_{k}", f"elbow_pole_{k}")
        cr = rig.pose.bones[f"hand_{k}"].constraints.new('COPY_ROTATION'); cr.target = rig; cr.subtarget = f"hand_IK_{k}"
    for i in range(3):
        c = rig.pose.bones[f"mantle_{i+1}"].constraints.new('COPY_ROTATION')
        c.target = rig; c.subtarget = f"spine_{i+1}"; c.owner_space = 'LOCAL'; c.target_space = 'LOCAL'; c.mix_mode = 'BEFORE'

    def var(fc, nm, prop):
        v = fc.driver.variables.new(); v.name = nm; v.type = 'SINGLE_PROP'; v.targets[0].id = rig; v.targets[0].data_path = f'["{prop}"]'
    add_prop(rig, "blink", 0, 0, 1, "Closes both eyes")
    for k, sgn in (("L", -1), ("R", 1)):
        add_prop(rig, f"lid_upper_{k}", 0.4 if k == "L" else 0.3, 0, 1, "Upper lid: 0 open, 1 shut")
        add_prop(rig, f"lid_lower_{k}", 0.15, 0, 1, "Lower lid")
        add_prop(rig, f"brow_raise_{k}", 0, -1, 1, "Brow up (+) or down (-). Asymmetry gives dry humour")
        add_prop(rig, f"grip_{k}", 0.6, 0, 1, "Curls every finger joint")
        d0 = 0.4 if k == "L" else 0.3
        fc = drive(rig.pose.bones[f"lid_up_{k}"], "rotation_euler", 1, f"radians(140*(max(u,b)-{d0}))", rig, []); var(fc, "u", f"lid_upper_{k}"); var(fc, "b", "blink")
        fc = drive(rig.pose.bones[f"lid_low_{k}"], "rotation_euler", 1, "radians(-120*(l-0.15))", rig, []); var(fc, "l", f"lid_lower_{k}")
        fc = drive(rig.pose.bones[f"brow_{k}"], "location", 2, "0.012*r", rig, []); var(fc, "r", f"brow_raise_{k}")
        for f in ("finger1", "finger2", "finger3", "thumb"):
            nb = len([b for b in rig.data.bones if b.name.startswith(f"{f}_{k}_")])
            for i in range(nb):
                fc = drive(rig.pose.bones[f"{f}_{k}_{i+1}"], "rotation_euler", 0, "-0.7*(g-0.6)", rig, []); var(fc, "g", f"grip_{k}")
    add_prop(rig, "frag_shelter", 0, 0, 1, "Fragments swing round into a partial sheltering arc")
    add_prop(rig, "frag_spread", 0, -1, 1, "Fragments bunch together (-) or spread apart (+)")
    add_prop(rig, "frag_fluster", 0, 0, 1, "Loss of composure: fragment spacing becomes uneven")
    jitter = (28, -18, 44)
    for i in range(3):
        fc = drive(rig.pose.bones[f"fragment_{i+1}"], "rotation_euler", 1,
                   f"radians(150*s + {(i-1)*22}*p + {jitter[i]}*f)", rig, [])
        var(fc, "s", "frag_shelter"); var(fc, "p", "frag_spread"); var(fc, "f", "frag_fluster")
    rig.parent = root
    return rig

# ================================================================ STAGE 5: Nix rig
def rig_nix(root, tag="NIX"):
    O = bpy.data.objects
    coll = root.users_collection[0]
    od = Vector((math.cos(math.radians(28)), 0, math.sin(math.radians(28))))
    oc = od * 0.034
    U, V = Vector((1, 0, 0)), Vector((0, -0.45, 0.9)).normalized(); N = U.cross(V).normalized()
    B = [dict(name="root", head=(0, 0, 0), tail=(0, 0, -0.06)),
         dict(name="body", head=(0, 0, -0.03), tail=(0, 0, 0.05), parent="root", up=(0, -1, 0)),
         dict(name="attention", head=oc, tail=oc + N * 0.03, parent="body", up=U)]
    fins = {}
    for k in ("A", "B"):
        fo = O[f"{tag}_fin_{k}"]; fp = curve_pts(fo)
        fins[k] = fp
        B += [dict(name=f"fin_{k}", head=fp[0], tail=fp[3], parent="body", up=(0, 1, 0))]
    rig = make_rig(f"RIG_{tag}", coll, B)
    for ob in list(coll.objects):
        if ob.name.startswith(f"{tag}_body") or ob.name.startswith(f"{tag}_edge") or ob.name.startswith(f"{tag}_eye") \
           or ob.name.startswith(f"{tag}_guide"):
            bone_parent(ob, rig, "body")
    bone_parent(O[f"{tag}_bead"], rig, "attention")
    for k in ("A", "B"):   # stubby paddles: rigid, swinging from the base, so they can never tear
        bone_parent(O[f"{tag}_fin_{k}"], rig, f"fin_{k}")
    # live lid cuts: each eye is a clean ellipsoid cut by an invisible box on a lid bone
    body = O[f"{tag}_body"]; dep = 0.03
    fc0 = Vector((-0.045, -dep / 2 - 0.0012, -0.004))
    eye_c = {}
    for k, side in (("L", -1), ("R", 1)):
        ec0 = fc0 + Vector((side * 0.0128, 0, side * -0.003))
        hit_e, _ = raycast(body, (ec0.x, -1, ec0.z), (0, 1, 0))
        eye_c[k] = hit_e + Vector((0, 0.0012, 0)) if hit_e is not None else ec0
    with bpy.context.temp_override(scene=scene, view_layer=VL, active_object=rig, object=rig, selected_objects=[rig]):
        VL.objects.active = rig
        bpy.ops.object.mode_set(mode='EDIT')
        for k in ("L", "R"):
            eb = rig.data.edit_bones.new(f"lid_{k}"); eb.head = eye_c[k]; eb.tail = eye_c[k] + Vector((0, 0, 0.012))
            eb.align_roll(Vector((0, -1, 0))); eb.parent = rig.data.edit_bones["body"]; eb.use_deform = False
        bpy.ops.object.mode_set(mode='OBJECT')
    for k in ("L", "R"):
        rig.pose.bones[f"lid_{k}"].rotation_mode = 'XYZ'
    for k, side in (("L", -1), ("R", 1)):
        eo = O[f"{tag}_eye_{k}"]
        rot = Euler((0, math.radians(side * 10), 0)).to_matrix().to_4x4()
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=28, radius=1)
        xform(bm, Matrix.Translation(eye_c[k]) @ rot @ Matrix.Diagonal((0.0075, 0.0034, 0.012, 1)))
        old = eo.data; me = bpy.data.meshes.new(eo.name); bm.to_mesh(me); bm.free()
        for pg in me.polygons:
            pg.use_smooth = True
        me.materials.append(mat_for("nix_eye")); eo.data = me; bpy.data.meshes.remove(old)
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
        xform(bm, Matrix.Translation(eye_c[k] + Vector((0, 0, 0.012 + 0.02))) @ Matrix.Diagonal((0.04, 0.05, 0.04, 1)))
        cm = bpy.data.meshes.new(f"{tag}_lidcut_{k}"); bm.to_mesh(cm); bm.free()
        cut = bpy.data.objects.new(f"{tag}_lidcut_{k}", cm); coll.objects.link(cut)
        cut.display_type = 'WIRE'; cut.hide_render = True
        bone_parent(cut, rig, f"lid_{k}")
        bmod = eo.modifiers.new("lid", 'BOOLEAN'); bmod.operation = 'DIFFERENCE'; bmod.object = cut; bmod.solver = 'EXACT'
        bone_parent(eo, rig, "body")
    def var(fc, nm, prop):
        v = fc.driver.variables.new(); v.name = nm; v.type = 'SINGLE_PROP'; v.targets[0].id = rig; v.targets[0].data_path = f'["{prop}"]'
    add_prop(rig, "attention", 0, -230, 70, "Degrees: moves the bead around its incomplete orbit toward whatever interests Nix")
    fc = drive(rig.pose.bones["attention"], "rotation_euler", 1, "radians(a)", rig, []); var(fc, "a", "attention")
    for k, sgn in (("A", 1), ("B", -1)):
        add_prop(rig, f"fin_{k}_flare", 0, -1, 1, "Fin flares out (+) or folds in (-)")
        add_prop(rig, f"fin_{k}_sweep", 0, -1, 1, "Fin sweeps back (+) or forward (-)")
        fc = drive(rig.pose.bones[f"fin_{k}"], "rotation_euler", 2, f"{sgn}*1.0*f", rig, []); var(fc, "f", f"fin_{k}_flare")
        fc = drive(rig.pose.bones[f"fin_{k}"], "rotation_euler", 0, "0.9*w", rig, []); var(fc, "w", f"fin_{k}_sweep")
    add_prop(rig, "lid_close", 0, 0, 1, "Lids come down over both eyes")
    add_prop(rig, "lid_mischief", 0, 0, 1, "Lids slant inward: scheming")
    add_prop(rig, "lid_innocent", 0, 0, 1, "Lids slant outward: innocent")
    add_prop(rig, "lid_rest", 0.25, 0, 0.6, "Resting lid cover")
    for k, side in (("L", -1), ("R", 1)):
        fc = drive(rig.pose.bones[f"lid_{k}"], "location", 1, "-0.0205*min(1, max(c, r + 0.2*max(m, i)))", rig, [])
        var(fc, "c", "lid_close"); var(fc, "r", "lid_rest"); var(fc, "m", "lid_mischief"); var(fc, "i", "lid_innocent")
        fc = drive(rig.pose.bones[f"lid_{k}"], "rotation_euler", 1, f"{side}*radians(30*i - 30*m)", rig, [])
        var(fc, "m", "lid_mischief"); var(fc, "i", "lid_innocent")
    rig.parent = root
    return rig

# ================================================================ STAGE 5: build rigs
for r in (mor, ves, nix):
    r.location = (0, 0, 0); r.rotation_euler = (0, 0, 0)
upd()
apply_color()
# heather on the inside faces of Vesper's mantle panels
for nm in ("panel_back_calm", "mantle_crescent", "panel_right_med", "panel_frontL_med", "hood"):
    ob = bpy.data.objects[f"VES_{nm}"]
    me = ob.data
    me.materials.append(MATS["ves_inner"])
    for pg in me.polygons:
        c = pg.center
        axis = spine(c.z)
        radial = Vector((c.x - axis.x, c.y - axis.y, 0))
        if pg.normal.dot(radial) < 0:
            pg.material_index = len(me.materials) - 1

C_WGT = make_coll("WGT_widgets"); C_WGT.hide_render = True; C_WGT.hide_viewport = True
def widget(name, kind):
    if name in bpy.data.objects:
        return bpy.data.objects[name]
    bm = bmesh.new()
    if kind == "circle":
        bmesh.ops.create_circle(bm, cap_ends=False, segments=32, radius=1.0)
    elif kind == "square":
        for a_ in range(4):
            bm.verts.new((math.cos(math.radians(45 + 90 * a_)), 0, math.sin(math.radians(45 + 90 * a_))))
        bm.verts.ensure_lookup_table()
        for a_ in range(4):
            bm.edges.new((bm.verts[a_], bm.verts[(a_ + 1) % 4]))
    elif kind == "diamond":
        pts_ = [(0, 0, 1), (1, 0, 0), (0, 0, -1), (-1, 0, 0)]
        vs = [bm.verts.new(p_) for p_ in pts_]
        for a_ in range(4):
            bm.edges.new((vs[a_], vs[(a_ + 1) % 4]))
    elif kind == "sphere":
        for ax in range(3):
            ring = []
            for a_ in range(24):
                t_ = 2 * math.pi * a_ / 24; v_ = [0, 0, 0]
                v_[ax] = math.cos(t_); v_[(ax + 1) % 3] = math.sin(t_)
                ring.append(bm.verts.new(v_))
            for a_ in range(24):
                bm.edges.new((ring[a_], ring[(a_ + 1) % 24]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); C_WGT.objects.link(ob)
    return ob

WIDGETS = [("root", "circle", 1.6), ("body", "circle", 1.0), ("spine_", "circle", 1.2), ("neck", "circle", 0.8),
           ("head", "circle", 1.2), ("hand_IK_", "square", 0.6), ("elbow_pole_", "diamond", 0.5), ("eye_target", "sphere", 0.5),
           ("halo", "circle", 1.0), ("fragment_", "diamond", 0.6), ("attention", "sphere", 0.5), ("fin_", "diamond", 0.6),
           ("ember", "sphere", 0.6), ("leg_", "circle", 0.8), ("foot_", "square", 0.6)]
def organize(rig):
    arm = rig.data
    cols = {n: arm.collections.new(n) for n in ("Controls", "Face", "Fingers", "Deform and mechanics")}
    for b in arm.bones:
        n = b.name
        pb = rig.pose.bones[n]
        hit = next((w for w in WIDGETS if (n == w[0] or (w[0].endswith("_") and n.startswith(w[0])))), None)
        if hit:
            pb.custom_shape = widget("WGT_" + hit[1], hit[1]); pb.custom_shape_scale_xyz = (hit[2],) * 3
            pb.use_custom_shape_bone_size = True
            cols["Controls"].assign(b)
        elif n.startswith(("lid_", "brow_", "eye_", "crest_")):
            pb.custom_shape = widget("WGT_circle", "circle"); pb.custom_shape_scale_xyz = (0.6,) * 3
            cols["Face"].assign(b)
        elif n.startswith(("finger", "thumb")):
            cols["Fingers"].assign(b)
        else:
            cols["Deform and mechanics"].assign(b)
    cols["Deform and mechanics"].is_visible = False
    arm.display_type = 'OCTAHEDRAL'

RIGS = {"morrow": (mor, rig_morrow(mor)), "vesper": (ves, rig_vesper(ves)), "nix": (nix, rig_nix(nix))}
for _r, _rig in RIGS.values():
    organize(_rig)
upd()

def bake_follow_through(rig, frames, pairs, delay=3, scale=1.0):
    """Follow-through tool. For each (follower_bone, source_bone), key the follower's own rotation so it
    trails the source by `delay` frames. Run it after the source bones are animated."""
    samples = {}
    for f in frames:
        scene.frame_set(f)
        for fol, src in pairs:
            samples[(src, f)] = Vector(rig.pose.bones[src].rotation_euler)
    for f in frames:
        for fol, src in pairs:
            past = samples.get((src, max(frames[0], f - delay)), samples[(src, f)])
            off = (past - samples[(src, f)]) * scale
            pb = rig.pose.bones[fol]
            pb.rotation_euler = off
            pb.keyframe_insert("rotation_euler", frame=f)

def bake_lag(rig, frames, bone, driver_bone, k=0.35, smooth=0.6):
    """Ember-style lag. Keys `bone`'s location opposite to the recent motion of `driver_bone`,
    so it trails behind sudden moves and settles when movement stops."""
    prev = None; off = Vector()
    for f in frames:
        scene.frame_set(f)
        m = rig.matrix_world @ rig.pose.bones[driver_bone].matrix
        pos = m.to_translation()
        vel = (pos - prev) if prev is not None else Vector()
        prev = pos
        off = off * smooth + (-vel * k) * (1 - smooth) * 10
        if off.length > 0.012:
            off = off.normalized() * 0.012
        local = m.to_3x3().inverted() @ off
        pb = rig.pose.bones[bone]
        pb.location = local
        pb.keyframe_insert("location", frame=f)

# ================================================================ STAGE 5: tests
def eval_coords(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    oe = ob.evaluated_get(dg)
    me = oe.to_mesh()
    pts = [oe.matrix_world @ v.co for v in me.vertices]
    oe.to_mesh_clear()
    return pts

def mean(pts):
    return sum(pts, Vector()) / max(1, len(pts))

def part_objects(root):
    return [o for o in root.children_recursive if o.type in {'MESH', 'CURVE'}]

REPORT = []
def report(*a):
    line = " ".join(str(x) for x in a); REPORT.append(line); print(line, flush=True)

def reset(rig):
    for k in list(rig.keys()):
        if k in DEFAULTS[rig.name]:
            rig[k] = DEFAULTS[rig.name][k]
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
    upd()

DEFAULTS = {}
for key, (root, rig) in RIGS.items():
    DEFAULTS[rig.name] = {k: rig[k] for k in rig.keys() if isinstance(rig[k], float)}

CONTROL_TESTS = {
    "morrow": [("blink", 1, "MOR_lid_L"), ("lid_lower_L", 0.9, "MOR_lowlid_L"), ("brow_raise_R", 1, "MOR_brow_R"),
               ("brow_worry_L", 1, "MOR_brow_L"), ("mouth_smile", 1, "MOR_mouth"), ("mouth_smile", -1, "MOR_mouth"),
               ("mouth_width", 1, "MOR_mouth"), ("crest_mood", -1, "MOR_crest"), ("crest_mood", 0, "MOR_crest"), ("crest_lean", 1, "MOR_crest"),
               ("grip_L", 1, "MOR_hand_L_finger1"), ("grip_R", 0, "MOR_hand_R_thumb")],
    "vesper": [("blink", 1, "VES_lid_R"), ("brow_raise_L", 1, "VES_brow_L"), ("lid_lower_R", 0.8, "VES_lowlid_R"),
               ("frag_shelter", 1, "VES_fragment_2"), ("frag_spread", 1, "VES_fragment_1"), ("frag_fluster", 1, "VES_fragment_3"),
               ("grip_R", 1, "VES_hand_R_finger2")],
    "nix": [("attention", -120, "NIX_bead"), ("fin_A_flare", 1, "NIX_fin_A"), ("fin_B_sweep", 1, "NIX_fin_B"),
            ("lid_close", 1, "NIX_eye_L"), ("lid_mischief", 1, "NIX_eye_R"), ("lid_innocent", 1, "NIX_eye_L")],
}
BONE_TESTS = {"morrow": [("hand_IK_L", (0.05, -0.1, 0.12), "MOR_arm_L"), ("body", None, "MOR_torso"), ("eye_target", (0.2, 0, 0.1), "MOR_pupil_R")],
              "vesper": [("hand_IK_R", (-0.15, -0.2, 0.3), "VES_forearm_R"), ("spine_2", None, "VES_mantle_crescent"), ("head", None, "VES_halo")],
              "nix": [("root", None, "NIX_body")]}

passed = failed = 0
report("# Rig test report\n")
report("Generated by stage5_rigging.py in Blender", bpy.app.version_string, "\n")
for key, (root, rig) in RIGS.items():
    report(f"## {key.capitalize()}\n")
    nb = len(rig.data.bones); nd = sum(len(pb.constraints) for pb in rig.pose.bones)
    drivers = rig.animation_data.drivers if rig.animation_data else []
    report(f"- Bones: {nb}. Constraints: {nd}. Bone drivers: {len(drivers)}. Controls: {len(DEFAULTS[rig.name])}.")
    bad = [fc.data_path for fc in drivers if not fc.driver.is_valid]
    for ob in part_objects(root):
        if ob.data.shape_keys and ob.data.shape_keys.animation_data:
            bad += [fc.data_path for fc in ob.data.shape_keys.animation_data.drivers if not fc.driver.is_valid]
    report(f"- Invalid drivers: {len(bad)} {bad[:3] if bad else ''}")
    unrigged = [o.name for o in part_objects(root) if o.parent is not rig and not any(m.type == 'ARMATURE' for m in getattr(o, 'modifiers', []))]
    report(f"- Parts not driven by the rig: {len(unrigged)} {unrigged[:5] if unrigged else ''}")
    for ob in part_objects(root):
        if ob.vertex_groups and ob.type == 'MESH':
            sums = [sum(g.weight for g in v.groups) for v in ob.data.vertices]
            if min(sums) < 0.99 or max(sums) > 1.01:
                report(f"- WEIGHT PROBLEM on {ob.name}: min {min(sums):.2f} max {max(sums):.2f}")
    report("\n| Control | Value | Watched part | Largest movement (mm) | Result |\n| --- | --- | --- | --- | --- |")
    for prop, val, watch in CONTROL_TESTS[key]:
        reset(rig); before = eval_coords(bpy.data.objects[watch])
        rig[prop] = float(val); upd()
        after = eval_coords(bpy.data.objects[watch])
        if len(after) == len(before):
            mv = max((a_ - b_).length for a_, b_ in zip(after, before)) * 1000
        else:   # topology changed (a live cut): compare the extents instead
            lo1 = [min(p_[i] for p_ in before) for i in range(3)]; hi1 = [max(p_[i] for p_ in before) for i in range(3)]
            lo2 = [min(p_[i] for p_ in after) for i in range(3)]; hi2 = [max(p_[i] for p_ in after) for i in range(3)]
            mv = max(abs(x - y) for x, y in zip(lo1 + hi1, lo2 + hi2)) * 1000
        ok = mv > 0.2
        passed += ok; failed += (not ok)
        report(f"| {prop} | {val} | {watch} | {mv:.2f} | {'PASS' if ok else 'FAIL'} |")
    for bone, loc, watch in BONE_TESTS[key]:
        reset(rig); before = mean(eval_coords(bpy.data.objects[watch]))
        pb = rig.pose.bones[bone]
        if loc:
            place(rig, bone, loc)
        else:
            pb.rotation_euler = (0.35, 0.1, 0.2)
        upd()
        after = mean(eval_coords(bpy.data.objects[watch]))
        mv = (after - before).length * 1000
        ok = mv > 0.2
        passed += ok; failed += (not ok)
        report(f"| bone {bone} | {'move' if loc else 'rotate'} | {watch} | {mv:.2f} | {'PASS' if ok else 'FAIL'} |")
    reset(rig)
    report("")

# ================================================================ STAGE 5: control-only pose renders
POSES = {
    "morrow_rest": ("morrow", {}, {}),
    "morrow_worried_hug": ("morrow", {"crest_mood": -1, "crest_lean": -0.7, "lid_upper_L": 0.0, "lid_upper_R": 0.0, "brow_worry_L": 1, "brow_worry_R": 1,
                                       "mouth_smile": -1, "grip_L": 0.9, "grip_R": 0.9},
                           {"hand_IK_L": (0.1, -0.1, 0.1), "hand_IK_R": (-0.1, -0.1, 0.12)}),
    "morrow_delighted_reach": ("morrow", {"crest_mood": 1, "lid_upper_L": 0.0, "lid_upper_R": 0.0, "lid_lower_L": 0.5, "lid_lower_R": 0.5,
                                          "mouth_smile": 1, "mouth_width": 0.6, "brow_raise_L": 0.8, "brow_raise_R": 0.8, "grip_L": 0.1},
                               {"hand_IK_L": (-0.06, -0.12, 0.3), "eye_target": (-0.1, 0.0, 0.3)}),
    "morrow_determined": ("morrow", {"crest_mood": 1, "brow_worry_L": -1, "brow_worry_R": -1, "brow_raise_L": -0.6, "brow_raise_R": -0.6,
                                     "lid_upper_L": 0.48, "lid_upper_R": 0.48, "mouth_smile": -0.2, "mouth_width": -0.4, "grip_L": 1, "grip_R": 1},
                          {"body": ("rot", (0.2, 0, 0))}),
    "vesper_rest": ("vesper", {}, {}),
    "vesper_bow_shelter": ("vesper", {"frag_shelter": 1, "grip_L": 0.75, "lid_upper_L": 0.2, "lid_upper_R": 0.2},
                           {"spine_2": ("rot", (0.35, 0, 0)), "spine_3": ("rot", (0.3, 0, 0)), "neck": ("rot", (0.25, 0, 0)),
                            "hand_IK_L": (0.1, -0.3, -0.1)}),
    "vesper_flustered": ("vesper", {"frag_fluster": 1, "frag_spread": 0.6, "lid_upper_L": 0.0, "lid_upper_R": 0.0, "brow_raise_L": 1, "brow_raise_R": 0.6},
                         {"head": ("rot", (-0.2, 0.3, 0.1))}),
    "nix_rest": ("nix", {}, {}),
    "nix_mischief": ("nix", {"lid_mischief": 1, "attention": -150, "fin_A_flare": 0.6, "fin_B_flare": -0.4}, {"root": ("rot", (0, -0.25, 0))}),
    "nix_embarrassed": ("nix", {"lid_close": 0.6, "lid_innocent": 0.5, "fin_A_flare": -1, "fin_B_flare": -1}, {"root": ("rot", (0, 0, 1.15))}),
}
POSES["morrow_range"] = ("morrow", {"grip_L": 1, "grip_R": 0, "crest_mood": -1, "mouth_smile": 1, "mouth_width": 1},
                         {"hand_IK_L": (0.12, -0.14, 0.18), "hand_IK_R": (0.06, -0.12, 0.22), "body": ("rot", (0.3, 0, 0.15))})
POSES["vesper_range"] = ("vesper", {"grip_L": 1, "grip_R": 0, "frag_shelter": 1, "frag_fluster": 1},
                         {"spine_2": ("rot", (0.4, 0, 0.15)), "spine_3": ("rot", (0.35, 0, 0.1)), "hand_IK_R": (-0.2, -0.3, 0.3)})
POSES["nix_range"] = ("nix", {"fin_A_flare": 1, "fin_B_flare": -1, "fin_A_sweep": 1, "fin_B_sweep": -1, "lid_close": 1}, {})

def apply_pose(name):
    key, props, bones = POSES[name]
    root, rig = RIGS[key]
    reset(rig)
    for p_, v in props.items():
        rig[p_] = float(v)
    for b_, v in bones.items():
        if isinstance(v, tuple) and v and v[0] == "rot":
            rig.pose.bones[b_].rotation_euler = v[1]
        else:
            place(rig, b_, v)
    upd()
    return key, root, rig

report("## Deformation stretch test\n")
report("Every pose below is made with the controls only. For each pose, every deforming part is compared with")
report("its rest shape. An edge ratio under 0.5 means collapsing, over 1.8 means tearing. Edges shorter than")
report("30 percent of the median edge are ignored. Poses ending in `_range` deliberately push the controls")
report("further than the story poses do.\n")
report("| Pose | Parts checked | Worst part | Min edge ratio | Max edge ratio | Result |\n| --- | --- | --- | --- | --- | --- |")
for name in POSES:
    key, root, rig = apply_pose(name)
    worst = None; nparts = 0; glo, ghi = 9, 0
    for ob in part_objects(root):
        if ob.type != 'MESH' or not any(m.type == 'ARMATURE' for m in ob.modifiers):
            continue
        nparts += 1
        rest = [ob.matrix_world @ v.co for v in ob.data.vertices]
        posed = eval_coords(ob)
        lens0 = sorted((rest[e.vertices[0]] - rest[e.vertices[1]]).length for e in ob.data.edges)
        floor_ = 0.3 * lens0[len(lens0) // 2]
        ratios = [(posed[e.vertices[0]] - posed[e.vertices[1]]).length / (rest[e.vertices[0]] - rest[e.vertices[1]]).length
                  for e in ob.data.edges if (rest[e.vertices[0]] - rest[e.vertices[1]]).length > floor_]
        lo_, hi_ = min(ratios), max(ratios)
        bad_ = max(1 / lo_, hi_)
        if worst is None or bad_ > worst[0]:
            worst = (bad_, ob.name, lo_, hi_)
        glo, ghi = min(glo, lo_), max(ghi, hi_)
    if nparts == 0:
        report(f"| {name} | 0 | all parts rigid, nothing can stretch | 1.00 | 1.00 | PASS |")
        passed += 1; reset(rig); continue
    ok = glo > 0.5 and ghi < 1.8
    passed += ok; failed += (not ok)
    report(f"| {name} | {nparts} | {worst[1]} | {glo:.2f} | {ghi:.2f} | {'PASS' if ok else 'FAIL'} |")
    reset(rig)
report("\n## Rig mechanics tests\n")
report("| Test | Measured | Result |\n| --- | --- | --- |")
for key, (root, rig) in RIGS.items():
    reset(rig)
    for c in [c for pb in rig.pose.bones for c in pb.constraints if c.type == 'IK']:
        arm_ob = next((o for o in part_objects(root) if o.name.endswith("_arm_" + c.subtarget[-1])), None) or \
                 next(o for o in part_objects(root) if o.name.endswith("_forearm_" + c.subtarget[-1]))
        c.mute = True; upd(); a_ = eval_coords(arm_ob)
        c.mute = False; upd(); b_ = eval_coords(arm_ob)
        mv = max((x - y).length for x, y in zip(a_, b_)) * 1000
        ok = mv < 0.5; passed += ok; failed += (not ok)
        report(f"| {key}: elbow pole on {c.subtarget} leaves rest pose unchanged | {mv:.3f} mm drift | {'PASS' if ok else 'FAIL'} |")
    ctrl = [b.name for b in rig.data.bones if any(b.name == w[0] or (w[0].endswith('_') and b.name.startswith(w[0])) for w in WIDGETS)]
    missing = [n for n in ctrl if rig.pose.bones[n].custom_shape is None]
    ok = not missing; passed += ok; failed += (not ok)
    report(f"| {key}: every control bone has a viewport widget | {len(ctrl)} controls, {len(missing)} missing | {'PASS' if ok else 'FAIL'} |")
mr_ = RIGS["morrow"][1]; reset(mr_)
hit_, n_ = raycast(bpy.data.objects["MOR_torso"], (0.012, -1, 0.43), (0, 1, 0))
worst_ = 0
for off in ((0.5, 0, 0), (-0.5, 0, 0), (0, 0, 0.45), (0, 0, -0.45), (0.45, 0.2, 0.3), (-0.45, 0.2, -0.3)):
    place(mr_, "eye_target", off); upd()
    for k in ("L", "R"):
        e_ = mean(eval_coords(bpy.data.objects[f"MOR_eye_{k}"])); p_ = mean(eval_coords(bpy.data.objects[f"MOR_pupil_{k}"]))
        worst_ = max(worst_, math.degrees((p_ - e_).angle(n_)))
reset(mr_)
ok = worst_ < 50; passed += ok; failed += (not ok)
report(f"| morrow: pupils stay on the visible front of the eye at extreme gaze | worst {worst_:.1f} degrees from the face direction (limit 50) | {'PASS' if ok else 'FAIL'} |")
r_ = RIGS["vesper"][1]; reset(r_)
r_.pose.bones["spine_2"].rotation_euler = (0.3, 0, 0); upd()
d_ = (r_.pose.bones["mantle_2"].matrix.to_quaternion().rotation_difference(r_.pose.bones["spine_2"].matrix.to_quaternion())).angle
ok = d_ < 1e-3; passed += ok; failed += (not ok)
report(f"| vesper: mantle follow bones match the spine when no delay is baked | {math.degrees(d_):.4f} degrees | {'PASS' if ok else 'FAIL'} |")
reset(r_)
report(f"\n**Total: {passed} passed, {failed} failed.**")

if OUT:
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "rig_test_report.md"), "w").write("\n".join(REPORT) + "\n")
    mode_studio()
    for name in POSES:
        key = POSES[name][0]; root, rig = RIGS[key]
        coll = {"morrow": C_MOR, "vesper": C_VES, "nix": C_NIX}[key]
        set_visible([coll])
        root.location = (0, 0, 0.12 if key == "nix" else 0)
        apply_pose(name)
        objs = [o for o in coll.all_objects if o.type in {'MESH', 'CURVE'} and not o.hide_render]
        vd = (0.62, -1, 0.08) if key == "morrow" else (-0.3, -1, 0.06)   # three-quarter view from the face side shows the crest curl
        frame(cam, objs, vd, lens=70, aspect=0.75, margin=1.2)
        render_c(os.path.join(OUT, f"pose_{name}.png"), 600, 800, samples=48)
        reset(rig)
    for key, (root, rig) in RIGS.items():
        reset(rig)
    for r, k in ((mor, "MOR"), (ves, "VES"), (nix, "NIX")):
        r.location = LINEUP[k][0]; r.rotation_euler = (0, 0, math.radians(LINEUP[k][1]))
    set_visible([C_MOR, C_VES, C_NIX])
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "cast_rigged_v05.blend"))
    print("ALL DONE", flush=True)
