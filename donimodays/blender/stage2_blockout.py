"""
STAGE 2 - GRAYSCALE BLOCKOUT for Morrow, Vesper, and Nix.
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
scene = bpy.data.scenes.new("CAST_Blockout_v01")
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
C_CAM = make_coll("BLOCKOUT_Cameras")
C_LGT = make_coll("BLOCKOUT_Lights")
C_ENV = make_coll("BLOCKOUT_Studio")

# ---------------------------------------------------------------- materials
# Every object carries a "part" tag. Material schemes map parts to gray values.
VALUE = {  # value-hierarchy test: light protagonist, dark-mid companion, darkest creature
    "mor_shell": .78, "mor_face": .07, "mor_lid": .09, "mor_eye": .86, "mor_pupil": .02,
    "mor_mouth": .02, "mor_joint": .10, "mor_ember": .97, "mor_crest": .55,
    "ves_mantle": .09, "ves_collar": .12, "ves_inner": .2, "ves_brass": .42, "ves_mask": .24, "ves_eye": .62,
    "ves_lid": .30, "ves_brow": .32, "ves_arm": .10, "ves_hand": .14, "ves_neck": .05,
    "nix_body": .03, "nix_eye": .72, "nix_fin": .045, "nix_bead": .97, "nix_guide": .5,
    "dream": .62, "floor": .32,
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
                off *= 1 + rnd.uniform(-jitter, jitter)
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
    """Simple grasping hand: palm block plus fingers and a thumb. fwd = pointing dir, side = thumb side."""
    fwd, side = Vector(fwd).normalized(), Vector(side).normalized()
    up = fwd.cross(side).normalized()
    wrist = Vector(wrist)
    palm_c = wrist + fwd * size * 0.5
    sphere(prefix + "_palm", coll, part, palm_c, (size * 0.42, size * 0.55, size * 0.2),
           rot=basis(side, fwd, up).to_quaternion())
    spread = [(-0.5 + i / max(1, fingers - 1)) if fingers > 1 else 0 for i in range(fingers)]
    for i, s in enumerate(spread):
        base = palm_c + fwd * size * 0.45 + side * s * size * 0.45
        p1 = base + fwd * size * 0.45
        p2 = p1 + fwd * size * 0.3 * (1 - curl) - up * size * 0.35 * curl
        curve(f"{prefix}_finger{i+1}", coll, part, [base, p1, p2], size * thick, [1, .9, .7], kind='POLY')
    tb = palm_c - fwd * size * 0.1 + side * size * 0.48
    curve(prefix + "_thumb", coll, part, [tb, tb + side * size * 0.3 + fwd * size * 0.25, tb + side * size * 0.32 + fwd * size * 0.5],
          size * thick * 1.1, [1, .9, .7], kind='POLY')

# ================================================================ MORROW
def build_morrow(coll, P=None, tag="MOR"):
    """Small forward-leaning porcelain seed. P = pose dict (local coordinates)."""
    P = P or {}
    root = new_root(f"{tag}_root", coll)

    # torso: deformed sphere -> asymmetric forward-leaning seed
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=40, radius=1)
    for vt in bm.verts:
        x, y, z = vt.co
        t = (z + 1) / 2
        X = x * 0.165 * (1 - 0.42 * t ** 1.6) - 0.05 * t ** 2 + (0.02 * math.sin(math.pi * t) if x > 0 else 0)
        Y = y * 0.13 * (1 - 0.30 * t ** 1.6) - 0.12 * t ** 2
        Z = 0.10 + 0.42 * t
        vt.co = (X, Y, Z)
    torso = finish(f"{tag}_torso", bm, coll, "mor_shell")

    # crescent cavity through the torso (front to back)
    cav_c = Vector((-0.012, 0.0, 0.255))
    d = Vector((math.cos(math.radians(50)), 0, math.sin(math.radians(50))))
    a = cylinder("tmpA", coll, "mor_shell", cav_c + Vector((0, -0.4, 0)), cav_c + Vector((0, 0.4, 0)), 0.062, seg=64)
    b = cylinder("tmpB", coll, "mor_shell", cav_c + d * 0.036 + Vector((0, -0.5, 0)), cav_c + d * 0.036 + Vector((0, 0.5, 0)), 0.052, seg=64)
    boolean(a, b)                       # a is now a crescent prism
    boolean(torso, a)                   # cut the crescent through the torso
    torso.data.set_sharp_from_angle(angle=math.radians(45))
    ember_y = -0.012
    sphere(f"{tag}_ember", coll, "mor_ember", cav_c - d * 0.039 + Vector((0, ember_y, 0)) + Vector(P.get("ember_lag", (0, 0, 0))), r=0.0155)

    # face patch: soft dark area, slightly off-centre, on the upper front
    hit, n = raycast(torso, (0.012, -1, 0.405), (0, 1, 0))
    right = Vector((1, 0, 0)); up = n.cross(right).normalized() * -1
    right = up.cross(n).normalized()
    F = basis(right, n * -1, up)  # local +Y points into the body; we use -Y as outward
    out = -n * -1  # outward normal
    out = n
    face_c = hit - n * 0.006
    sphere(f"{tag}_face", coll, "mor_face", face_c, (0.074, 0.022, 0.062), rot=basis(right, n, up).to_quaternion())

    # eyes: one slightly larger. eyelids + pupils, no glow.
    gaze = Vector(P.get("gaze", (0, -1, 0))).normalized()
    lid_close = P.get("lid", 0.30)       # 0 = wide open, 1 = shut
    for side, r_eye in ((-1, 0.019), (1, 0.0235)):
        ec = face_c + right * side * 0.029 + up * 0.012 + n * 0.012
        sphere(f"{tag}_eye_{'L' if side < 0 else 'R'}", coll, "mor_eye", ec, r=r_eye)
        pdir = (n * 0.55 + gaze * 0.45).normalized()
        sphere(f"{tag}_pupil_{'L' if side < 0 else 'R'}", coll, "mor_pupil", ec + pdir * r_eye * 0.78, r=r_eye * 0.42)
        # eyelid: spherical cap over the top of the eye, rotated down by lid_close
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=18, radius=r_eye * 1.14)
        bmesh.ops.delete(bm, geom=[vv for vv in bm.verts if vv.co.z < r_eye * 0.05], context='VERTS')
        tilt = Matrix.Rotation(math.radians(-15 + 85 * lid_close), 4, 'X')
        xform(bm, Matrix.Translation(ec) @ basis(right, n, up) @ tilt)
        finish(f"{tag}_lid_{'L' if side < 0 else 'R'}", bm, coll, "mor_lid")
    # restrained mouth: a short soft arc
    mc = face_c + up * -0.03 + n * 0.02 + right * 0.004
    smile = P.get("smile", 0.25)
    curve(f"{tag}_mouth", coll, "mor_mouth",
          [mc - right * 0.014 + up * 0.004 * smile, mc - up * 0.004 * smile, mc + right * 0.014 + up * 0.004 * smile], 0.0028)

    # ribbon crest: grows from the back of the head, emotional antenna
    hit_b, nb = raycast(torso, (-0.02, 1, 0.47), (0, -1, 0))
    crest = P.get("crest", "raised")
    if crest == "raised":
        pts = [(0, 0, 0), (0.0, 0.025, 0.045), (-0.005, 0.03, 0.095), (-0.01, 0.005, 0.13), (-0.012, -0.025, 0.125)]
    elif crest == "curled":
        pts = [(0, 0, 0), (0, 0.035, 0.01), (0, 0.04, -0.03), (0, 0.015, -0.04)]
    else:  # relaxed
        pts = [(0, 0, 0), (0, 0.04, 0.02), (0, 0.08, 0.0), (0, 0.11, -0.03)]
    pts = [hit_b - nb * 0.004 + Vector(p) for p in pts]
    curve(f"{tag}_crest", coll, "mor_crest", pts, 0.004, [0.55, 1.0, 1.05, 0.75, 0.35][:len(pts)], ribbon=0.026,
          tilts=[0.0, 0.5, 1.0, 1.35, 1.57][:len(pts)])

    # legs + broad soft feet (one foot slightly forward for an uneven stance)
    for side, fwd in ((-1, -0.012), (1, 0.008)):
        x = side * 0.062
        cylinder(f"{tag}_leg_{'L' if side < 0 else 'R'}", coll, "mor_joint", (x, -0.005, 0.035), (x, -0.005, 0.14), 0.03, 0.034)
        sphere(f"{tag}_foot_{'L' if side < 0 else 'R'}", coll, "mor_shell", (x * 1.08, -0.02 + fwd, 0.022), (0.048, 0.064, 0.023))

    # long arms that can hug objects to the chest
    arms = P.get("arms", {})
    for side in (-1, 1):
        key = 'L' if side < 0 else 'R'
        hs, hn = raycast(torso, (side * 1, -0.02, 0.33), (-side, 0, 0))
        sh = hs - Vector((side * 0.012, 0, 0))
        cylinder(f"{tag}_shoulder_{key}", coll, "mor_joint", sh - Vector((side * 0.01, 0, 0)), sh + Vector((side * 0.012, 0, 0)), 0.02)
        default = [sh, sh + Vector((side * 0.055, -0.03, -0.09)), sh + Vector((side * 0.045, -0.07, -0.19))]
        pts = [sh] + [Vector(p) for p in arms.get(key, [])] if key in arms else default
        curve(f"{tag}_arm_{key}", coll, "mor_shell", pts, 0.021, [1.0, .9, .82][:len(pts)] + [.8] * (len(pts) - 3), kind='NURBS')
        wrist = pts[-1]
        fwd = (pts[-1] - pts[-2]).normalized()
        sidev = fwd.cross(Vector((0, 0, 1))).normalized() * (-side)
        if sidev.length < 0.1:
            sidev = Vector((side, 0, 0))
        hand(f"{tag}_hand_{key}", coll, "mor_shell", wrist, fwd, sidev, 0.058, fingers=2, curl=P.get("curl", 0.45), thick=0.15)

    parent_all(root, coll)
    return root

# ================================================================ VESPER
H = 1.56  # about 2.6 x Morrow

def catmull(keys, z):
    zs = [k[0] for k in keys]
    if z <= zs[0]: return keys[0][1]
    if z >= zs[-1]: return keys[-1][1]
    i = max(j for j in range(len(zs) - 1) if zs[j] <= z)
    p0 = keys[max(i - 1, 0)][1]; p1 = keys[i][1]; p2 = keys[i + 1][1]; p3 = keys[min(i + 2, len(keys) - 1)][1]
    t = (z - zs[i]) / (zs[i + 1] - zs[i])
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)

# Tall S-curve: wide stable bell base, narrow waist, a hunched upper mass that
# leans forward and sits off-centre, closing into a hood with no head inside.
PROFILE = [(0, .27), (.2, .215), (.5, .14), (.8, .15), (1.02, .2), (1.18, .19), (1.3, .12), (1.38, .05)]
ZTOP = 1.38
def spine(z):
    s = max(0.0, min(z, ZTOP)) / ZTOP
    return Vector((0.07 * s ** 2.2, 0.05 * math.sin(math.pi * s) - 0.24 * s ** 2.6, 0))

def surf(name, coll, part, phi0, phi1, z0, z1, dr=0.0, hem=0.0, flare=0.0, xoff=0.0, petal=0.0,
         nu=30, nv=44, closed=False, thick=0.012, slant=0.0):
    """Curved shell panel around the spine. petal > 0 narrows the panel toward top and bottom."""
    bm = bmesh.new()
    grid = []
    for i in range(nu + (0 if closed else 1)):
        u = i / nu
        col = []
        for j in range(nv + 1):
            v = j / nv
            w = 1 - petal * (1 - math.sin(math.pi * min(1, v * 1.15))) if petal else 1
            pm = (phi0 + phi1) / 2
            phi = math.radians(pm + (phi0 - pm + (phi1 - phi0) * u) * w)
            zb = z0 + hem * math.sin(math.pi * u)
            z = zb + (z1 - slant * u - zb) * v
            r = catmull(PROFILE, z) + dr + flare * (1 - v) ** 2
            c = spine(z) + Vector((xoff * v, 0, 0))
            col.append(bm.verts.new((c.x + r * math.cos(phi), c.y + r * math.sin(phi) * 0.86, z)))
        grid.append(col)
    n = len(grid)
    for i in range(n if closed else n - 1):
        for j in range(nv):
            i2 = (i + 1) % n
            bm.faces.new((grid[i][j], grid[i2][j], grid[i2][j + 1], grid[i][j + 1]))
    ob = finish(name, bm, coll, part)
    if thick:
        sm = ob.modifiers.new("thick", 'SOLIDIFY'); sm.thickness = thick; sm.offset = -1
        bake_modifiers(ob)
    return ob

def build_vesper(coll, P=None, tag="VES"):
    P = P or {}
    root = new_root(f"{tag}_root", coll)
    # inner core: the muted-plum interior seen through the gaps between panels
    surf(f"{tag}_core", coll, "ves_inner", 0, 360, 0.02, 1.33, dr=-0.025, closed=True, thick=0, nu=40)
    # four large crescent-like mantle panels wrapping from back to front (90 = back, 270 = front)
    surf(f"{tag}_panel_spine", coll, "ves_mantle", 35, 145, 0.0, 1.36, 0.0, 0.04, petal=0.25)
    surf(f"{tag}_panel_left", coll, "ves_mantle", 115, 255, 0.0, 1.3, 0.014, 0.09, petal=0.35)
    surf(f"{tag}_panel_right", coll, "ves_mantle", -75, 65, 0.03, 1.24, 0.016, 0.07, petal=0.35)
    surf(f"{tag}_panel_frontL", coll, "ves_mantle", 212, 288, 0.07, 1.16, 0.03, 0.06, petal=0.45, slant=0.2)
    surf(f"{tag}_panel_frontR", coll, "ves_mantle", 262, 338, 0.0, 0.92, 0.046, 0.07, petal=0.45, slant=-0.16)
    # hood: the offset upper mass, open at the front where the face floats
    surf(f"{tag}_hood", coll, "ves_collar", -62, 242, 0.98, 1.42, 0.05, 0.09, flare=0.06, xoff=0.03, petal=0.2)

    # short neck stub inside the hood opening, with an air gap above it
    nk = spine(1.3)
    neck_top = nk + Vector((0, -0.07, 1.3))
    cylinder(f"{tag}_neck", coll, "ves_neck", nk + Vector((0, -0.02, 1.2)), neck_top, 0.05, 0.034)

    # suspended stone mask, floating in front of the hood
    tilt = P.get("head_tilt", (6, -8, 0))   # euler degrees: nod, roll, turn. default: slight concerned tilt
    Rh = Euler([math.radians(a) for a in tilt]).to_matrix().to_4x4()
    M = neck_top + Vector((0, -0.03, 0.15))
    head = lambda p: M + (Rh @ Vector(p))
    hq = Rh.to_quaternion()
    # mask: long and narrow, heavy brow shelf, small chin
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=32, radius=1)
    for vt in bm.verts:
        x, y, z = vt.co
        w = 0.07 * (1 - 0.35 * max(0, -z) ** 1.5) * (1 + 0.12 * max(0, z))
        vt.co = (x * w, y * 0.055 - (0.012 * max(0, z) if y < 0 else 0), z * 0.105)
    xform(bm, Matrix.Translation(M) @ Rh)
    mask = finish(f"{tag}_mask", bm, coll, "ves_mask")
    for side in (-1, 1):
        sock = sphere("tmp_sock", coll, "ves_mask", head((side * 0.028, -0.06, 0.012)), (0.024, 0.035, 0.019), rot=hq)
        boolean(mask, sock)
    mask.data.set_sharp_from_angle(angle=math.radians(50))
    lid = P.get("lids", (0.4, 0.3))
    brow = P.get("brows", (0.012, -0.004))   # asymmetric: dry humour and concern
    for i, side in enumerate((-1, 1)):
        k = 'L' if side < 0 else 'R'
        ec = head((side * 0.028, -0.043, 0.012))
        sphere(f"{tag}_eye_{k}", coll, "ves_eye", ec, r=0.0135)
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=0.0158)
        bmesh.ops.delete(bm, geom=[vv for vv in bm.verts if vv.co.z < 0.001], context='VERTS')
        xform(bm, Matrix.Translation(ec) @ Rh @ basis(Vector((1, 0, 0)), Vector((0, -1, 0)), Vector((0, 0, 1))) @ Matrix.Rotation(math.radians(-10 + 80 * lid[i]), 4, 'X'))
        finish(f"{tag}_lid_{k}", bm, coll, "ves_lid")
        b0 = head((side * 0.01, -0.062, 0.04 + brow[i] * 0.3)); b1 = head((side * 0.05, -0.052, 0.038 + brow[i]))
        curve(f"{tag}_brow_{k}", coll, "ves_brow", [b0, (b0 + b1) / 2 + Rh @ Vector((0, -0.006, 0.005)), b1], 0.007, [1, 1.15, .7])
    curve(f"{tag}_nose", coll, "ves_mask", [head((0, -0.066, 0.03)), head((0, -0.07, 0.0)), head((0, -0.064, -0.028))], 0.0065, [.6, 1, .8])

    # broken brass halo: tilted back, gap of about 110 deg at the upper right, ends thickened where it broke
    hc = head((0, 0.045, 0.02))
    Rt = Rh @ Euler((math.radians(-22), 0, math.radians(14))).to_matrix().to_4x4()
    U = Rt @ Vector((1, 0, 0)); V = Rt @ Vector((0, 0, 1))
    tube_arc(f"{tag}_halo", coll, "ves_brass", hc, 0.165, 0.012, 100, 350, U, V, seg=72, rscale=(1.0, 1.6))
    for i, (ang, sz) in enumerate(((100, 1.0), (350, 1.0))):
        tube_arc(f"{tag}_halo_break_{i+1}", coll, "ves_brass", hc, 0.165, 0.016, ang - (4 if i else 0), ang + (0 if i else 4), U, V,
                 seg=4, ring=7, rscale=(1.1, 1.6), jitter=0.3, seed=11 + i)
    # three irregular fragments of its own missing structure
    frag = P.get("fragments", [(0.2, 22, 0), (0.215, 50, 1), (0.2, 78, 2)])  # (radius, angle deg, seed)
    for i, (rad, ang, seed) in enumerate(frag):
        o = tube_arc(f"{tag}_fragment_{i+1}", coll, "ves_brass", hc, rad, 0.019, ang - 10 - seed * 2, ang + 10, U, V,
                     seg=10, ring=7, rscale=(1.1, 1.6), jitter=0.28, seed=seed + 3)
        o.data.set_sharp_from_angle(angle=math.radians(35))

    # long articulated arms emerging from under the hood. forearms are heavier than upper arms.
    arms = P.get("arms", {})
    for side in (-1, 1):
        k = 'L' if side < 0 else 'R'
        sh = spine(1.12) + Vector((side * 0.19 + 0.03, -0.02, 1.1))
        if k in arms:
            el, wr = Vector(arms[k][0]), Vector(arms[k][1])
        else:  # formal rest pose: hands loosely clasped in front of the waist
            el = sh + Vector((side * 0.07, -0.06, -0.34))
            wr = Vector((side * 0.035 + 0.02, -0.3, 0.66))
        sphere(f"{tag}_shoulderjoint_{k}", coll, "ves_arm", sh, r=0.034)
        cylinder(f"{tag}_upperarm_{k}", coll, "ves_arm", sh, el, 0.028, 0.03)
        sphere(f"{tag}_elbow_{k}", coll, "ves_arm", el, r=0.033)
        cylinder(f"{tag}_forearm_{k}", coll, "ves_arm", el, wr, 0.04, 0.026)
        fwd = Vector(arms.get(k + "_fwd", (Vector((-side * 0.8, -0.3, -0.5)) if k not in arms else (wr - el)))).normalized()
        sidev = Vector(arms.get(k + "_side", (0, 0, 1) if k not in arms else fwd.cross(Vector((0, 0, 1))).normalized() * side))
        hand(f"{tag}_hand_{k}", coll, "ves_hand", wr, fwd, sidev, 0.09, fingers=3, curl=arms.get(k + "_curl", 0.6), thick=0.12)

    parent_all(root, coll)
    return root

# ================================================================ NIX
def build_nix(coll, P=None, tag="NIX"):
    P = P or {}
    root = new_root(f"{tag}_root", coll)
    R, r, off, dep = 0.075, 0.063, 0.034, 0.03
    od = Vector((math.cos(math.radians(28)), 0, math.sin(math.radians(28))))   # opening direction
    a = cylinder(f"{tag}_body", coll, "nix_body", (0, -dep / 2, 0), (0, dep / 2, 0), R, seg=96)
    b = cylinder("tmpB", coll, "nix_body", od * off + Vector((0, -1, 0)), od * off + Vector((0, 1, 0)), r, seg=96)
    boolean(a, b)
    # the missing section: a bite out of the lower horn
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    xform(bm, Matrix.Translation((0.07, 0, -0.062)) @ Matrix.Rotation(math.radians(40), 4, 'Y') @ Matrix.Diagonal((0.06, 0.2, 0.07, 1)))
    cut = finish("tmpCut", bm, coll, "nix_body")
    boolean(a, cut)
    bv = a.modifiers.new("soft", 'BEVEL'); bv.width = 0.011; bv.segments = 5; bv.limit_method = 'ANGLE'
    bake_modifiers(a)
    a.data.set_sharp_from_angle(angle=math.radians(70))
    # face across the belly (left side of the crescent)
    eye_tilt = P.get("eye_tilt", 0)
    fc = Vector((-0.05, -dep / 2 - 0.0012, -0.004))
    for side in (-1, 1):
        k = 'L' if side < 0 else 'R'
        sphere(f"{tag}_eye_{k}", coll, "nix_eye", fc + Vector((side * 0.0125, 0, side * -0.003)),
               (0.0065, 0.0032, 0.0105), rot=Euler((0, math.radians(side * 10 + eye_tilt), 0)).to_quaternion())
    # two paddle fins on the outer curve, swept back
    fins = P.get("fins", {"A": (128, 0.0), "B": (222, 0.0)})   # (angle on rim, extra sweep)
    for k, (ang, sweep) in fins.items():
        t = math.radians(ang)
        rad = Vector((math.cos(t), 0, math.sin(t)))
        base = rad * (R - 0.006)
        tip = base + rad * 0.045 + Vector((0, 0.02 + sweep, 0)) + Vector((-rad.z, 0, rad.x)) * 0.012
        mid = (base + tip) / 2 + Vector((-rad.z, 0, rad.x)) * 0.01
        curve(f"{tag}_fin_{k}", coll, "nix_fin", [base, mid, tip], 0.004, [0.9, 1.5, 0.5], ribbon=0.011, tilts=[1.57, 1.57, 1.57])
    # incomplete orbit (construction guide, not rendered) and the attention bead
    oc = od * off
    U, V = Vector((1, 0, 0)), Vector((0, -0.45, 0.9)).normalized()
    g = tube_arc(f"{tag}_guide_orbit", coll, "nix_guide", oc, 0.047, 0.0009, 20, 320, U, V, seg=64, ring=6)
    g.hide_render = True
    ba = math.radians(P.get("bead_angle", 250))
    sphere(f"{tag}_bead", coll, "nix_bead", oc + (U * math.cos(ba) + V * math.sin(ba)) * 0.047, r=0.0075)
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
    """Aim cam at the bounding box of objs from view_dir (unit vector from target to camera)."""
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

# ================================================================ build
mor = build_morrow(C_MOR)
ves = build_vesper(C_VES)
nix = build_nix(C_NIX)
studio()
cam = camera()

# lineup positions at true relative scale
LINEUP = {"MOR": ((0, 0, 0), 0), "VES": ((0.62, 0.08, 0), -12), "NIX": ((-0.34, -0.02, 0.46), 14)}
for root, key in ((mor, "MOR"), (ves, "VES"), (nix, "NIX")):
    root.location = LINEUP[key][0]; root.rotation_euler.z = math.radians(LINEUP[key][1])

# ---------------------------------------------------------------- relationship pose
# Dream fragment floats front-left of Morrow. Morrow reaches toward it, Nix has
# already touched it, Vesper stands behind and shelters Morrow while looking away.
DREAM = Vector((-0.26, -0.26, 0.4))
MOR_T = Matrix.LocRotScale(Vector((0, 0, 0)), Euler((math.radians(8), 0, math.radians(-15))), None)
VES_T = Matrix.LocRotScale(Vector((0.36, 0.34, 0)), Euler((0, 0, math.radians(-40))), None)
NIX_T = Matrix.LocRotScale(DREAM + Vector((-0.08, -0.02, 0.05)), Euler((0, math.radians(18), math.radians(-35))), None)
mi, vi = MOR_T.inverted(), VES_T.inverted()
L = lambda Mi, p: Mi @ Vector(p)
dl = mi @ DREAM
shL = Vector((-0.15, -0.03, 0.33))
reach = (dl - shL).normalized()
pose_mor = {
    "gaze": (mi.to_3x3() @ (DREAM - Vector((0, -0.08, 0.42)))).normalized(),
    "lid": 0.08, "crest": "raised", "smile": -0.3, "curl": 0.2,
    "arms": {"L": [shL + reach * 0.13 + Vector((-0.06, 0, 0.04)), shL + reach * 0.28 + Vector((0, 0, 0.02))],  # cautious reach
             "R": [Vector((0.17, -0.1, 0.25)), Vector((0.05, -0.19, 0.27))]},        # other hand hugs its chest
}
morP = build_morrow(C_POSE, pose_mor, tag="POSE_MOR")
morP.matrix_world = MOR_T

pose_ves = {
    "head_tilt": (-14, 10, 38),               # looking up and away: pretending not to worry
    "lids": (0.45, 0.3), "brows": (0.018, -0.006),
    "fragments": [(0.2, 165, 0), (0.22, 190, 1), (0.205, 215, 2)],  # drifting toward Morrow's side
    "arms": {"L": [L(vi, (0.14, 0.12, 0.98)), L(vi, (0.03, -0.04, 0.76))],
             "L_fwd": (vi.to_3x3() @ Vector((-0.45, -0.75, -0.3))).normalized(),
             "L_side": (vi.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized(), "L_curl": 0.7,
             "R": [L(vi, (0.6, 0.18, 0.82)), L(vi, (0.42, 0.0, 0.98))],
             "R_fwd": (vi.to_3x3() @ Vector((-0.5, 0.3, 0.6))).normalized(), "R_curl": 0.8},
}
vesP = build_vesper(C_POSE, pose_ves, tag="POSE_VES")
vesP.matrix_world = VES_T

nixP = build_nix(C_POSE, {"fins": {"A": (60, 0.0), "B": (205, 0.03)}, "bead_angle": 330, "eye_tilt": 15}, tag="POSE_NIX")
nixP.matrix_world = NIX_T
# the dream fragment: a small broken crescent shard
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.04)
import random
rr = random.Random(7)
for vv in bm.verts:
    vv.co *= 1 + rr.uniform(-0.18, 0.18)
xform(bm, Matrix.Translation(DREAM) @ Matrix.Diagonal((1, 0.55, 1.2, 1)))
shard = finish("POSE_dream_fragment", bm, C_POSE, "dream", smooth=False)

# ---------------------------------------------------------------- render review set
def set_visible(colls):
    for c in (C_MOR, C_VES, C_NIX, C_POSE):
        c.hide_render = c not in colls
    for o in C_NIX.all_objects:
        pass

def render(path, w, h, samples=40, silhouette=False):
    r = scene.render
    r.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 6 if silhouette else samples
    scene.cycles.use_denoising = not silhouette
    r.resolution_x, r.resolution_y, r.resolution_percentage = w, h, 100
    r.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'Standard' if silhouette else 'AgX'
    vl = scene.view_layers[0]
    vl.material_override = SIL if silhouette else None
    floor = bpy.data.objects["ENV_floor"]; floor.hide_render = silhouette
    bg = next(n for n in scene.world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (1, 1, 1, 1) if silhouette else (0.22, 0.22, 0.23, 1)
    bg.inputs[1].default_value = 1.0 if silhouette else 0.6
    r.filepath = path
    bpy.ops.render.render(write_still=True)
    print("rendered", path, flush=True)

if OUT:
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "cast_blockout_v01.blend"))
    VIEWS = {"front": 0, "threequarter": -38, "side": -90, "back": 180}
    for key, root, coll in (("morrow", mor, C_MOR), ("vesper", ves, C_VES), ("nix", nix, C_NIX)):
        set_visible([coll])
        keep = (root.location.copy(), root.rotation_euler.copy())
        root.location = (0, 0, 0.0 if key != "nix" else 0.1)
        for vname, ang in VIEWS.items():
            root.rotation_euler = (0, 0, math.radians(ang))
            bpy.context.view_layer.update()
            frame(cam, coll.all_objects, (0, -1, 0.06))
            for sch in ("clay",):
                apply_scheme(sch)
                render(os.path.join(OUT, f"{key}_{vname}_clay.png"), 600, 800)
            render(os.path.join(OUT, f"{key}_{vname}_silhouette.png"), 600, 800, silhouette=True)
        apply_scheme("value"); root.rotation_euler = (0, 0, math.radians(-25)); bpy.context.view_layer.update()
        frame(cam, coll.all_objects, (0, -1, 0.06))
        render(os.path.join(OUT, f"{key}_face_value.png"), 600, 800)
        root.location, root.rotation_euler = keep
    # lineup at true scale
    set_visible([C_MOR, C_VES, C_NIX]); bpy.context.view_layer.update()
    objs = list(C_MOR.all_objects) + list(C_VES.all_objects) + list(C_NIX.all_objects)
    frame(cam, objs, (0, -1, 0.08), lens=70, aspect=1.6)
    for sch in ("clay", "value"):
        apply_scheme(sch); render(os.path.join(OUT, f"lineup_{sch}.png"), 1280, 800)
    render(os.path.join(OUT, "lineup_silhouette.png"), 1280, 800, silhouette=True)
    # relationship pose
    set_visible([C_POSE]); bpy.context.view_layer.update()
    frame(cam, C_POSE.all_objects, (-0.42, -1, 0.12), lens=60, aspect=1.0, margin=1.1)
    for sch in ("clay", "value"):
        apply_scheme(sch); render(os.path.join(OUT, f"relationship_{sch}.png"), 1000, 1000, samples=64)
    render(os.path.join(OUT, "relationship_silhouette.png"), 1000, 1000, silhouette=True)
    apply_scheme("clay")
    set_visible([C_MOR, C_VES, C_NIX])
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "cast_blockout_v01.blend"))
    print("ALL DONE", flush=True)
else:
    apply_scheme("clay")
