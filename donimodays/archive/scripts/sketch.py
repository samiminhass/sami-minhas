import sys, os, math
sys.argv = ["blender", "--background", "--python", "x"]
SCENE_NAME = "SKETCH"; HERE = "/home/user/sami-minhas/donimodays/blender"
src = open(HERE + "/cast_build.py").read().split("# ================================================================ STAGE 5: build rigs")[0]
exec(compile(src, "cb", "exec"))
from mathutils import Vector, Matrix
VAR = os.environ["VAR"]; OUTD = os.environ["OUT"]; os.makedirs(OUTD, exist_ok=True)
for r in (mor, ves, nix): r.location = (0, 0, 0); r.rotation_euler = (0, 0, 0)
upd(); apply_color()
O = bpy.data.objects
def kids(root, pre): return [o for o in root.children_recursive if o.name.startswith(pre)]
def ctr(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return sum(pts, Vector()) / len(pts)
def xf(objs, M):
    for o in objs: o.matrix_world = M @ o.matrix_world
def scl(objs, pivot, s):
    s = (s, s, s) if isinstance(s, (int, float)) else s
    xf(objs, Matrix.Translation(pivot) @ Matrix.Diagonal((*s, 1)) @ Matrix.Translation(-pivot))
def mv(objs, d): xf(objs, Matrix.Translation(Vector(d)))
mk = lambda root, names: [o for o in root.children_recursive if any(o.name.startswith(n) for n in names)]
MFACE = mk(mor, ("MOR_face", "MOR_eye", "MOR_pupil", "MOR_lid", "MOR_lowlid", "MOR_brow", "MOR_mouth"))
MEYES = [mk(mor, (f"MOR_eye_{k}", f"MOR_pupil_{k}", f"MOR_lid_{k}", f"MOR_lowlid_{k}")) for k in "LR"]
MBODY = mk(mor, ("MOR_torso", "MOR_ember", "MOR_seam"))
MCREST = mk(mor, ("MOR_crest",)); MARMS = mk(mor, ("MOR_arm", "MOR_shoulder", "MOR_hand"))
VHEAD = mk(ves, ("VES_mask", "VES_eye", "VES_lid", "VES_lowlid", "VES_brow"))
VHALO = mk(ves, ("VES_halo", "VES_fragment"))
VARMS = mk(ves, ("VES_upperarm", "VES_elbow", "VES_forearm", "VES_shoulderjoint", "VES_hand"))
VROBE = [o for o in ves.children_recursive if o.type in {'MESH', 'CURVE'} and o not in VHEAD + VHALO + VARMS]
NALL = [o for o in nix.children_recursive if o.type in {'MESH', 'CURVE'}]
NEYES = [mk(nix, (f"NIX_eye_{k}",)) for k in "LR"]; NBEAD = mk(nix, ("NIX_bead",))
if VAR == "A":
    fc = ctr(MFACE); scl(MFACE, fc, 1.35)
    for g in MEYES: scl(g, ctr(g), 1.15)
    hc = ctr(VHALO); mv(VROBE, (0, 0, 0)); scl(VROBE, Vector((0, 0, 0)), (1, 1, 1.2)); mv(VHEAD + VHALO, (0, 0, 0.29)); mv(VARMS, (0, 0, 0.22))
    scl(VHALO, ctr(VHALO), 1.5)
    scl(NALL, ctr(NALL), 2.0)
elif VAR == "B":
    base = Vector((0, 0, 0.075)); scl(MBODY, base, (0.9, 0.9, 1.25))
    fc = ctr(MFACE); mv(MFACE, (0, 0, 0.25 * (fc.z - 0.075)))
    cb = min((o.matrix_world @ Vector(c) for o in MCREST for c in o.bound_box), key=lambda v: v.z)
    mv(MCREST, (0, 0, 0.25 * (cb.z - 0.075))); cb.z += 0.25 * (cb.z - 0.075); scl(MCREST, cb, 1.7)
    mv(MARMS, (0, 0, 0.064))
    scl(VROBE, Vector((0, 0, 0)), (0.85, 0.85, 1.1)); mv(VHEAD, (0, 0, 0.14)); scl(VHEAD, ctr(VHEAD), 0.9)
    mv(VHALO, (0, 0, 0.14)); scl(VHALO, ctr(VHALO), 1.6)
    for o in VARMS:
        side = -1 if "_L" in o.name else 1
        xf([o], Matrix.Translation((side * -0.03, 0, 0.11)))
    scl(NALL, ctr(NALL), 2.0)
    for g in NEYES: scl(g, ctr(g), 1.45)
    scl(NBEAD, ctr(NBEAD), 1.5)
mor.location = (0, 0, 0); ves.location = (3, 0, 0); nix.location = (-3, 0, 0.3); upd()
cam = scene.camera
def shot(nm, t, h, d):
    t = Vector(t); a = math.radians(20)
    cam.location = t + Vector((math.sin(a), -math.cos(a), 0.08)) * d
    cam.rotation_euler = (t - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.lens = 24 / (2 * math.tan(math.atan(h / 2 / d)))
    render(os.path.join(OUTD, nm + ".png"), 500, 700, samples=32)
shot("morrow", (0, 0, 0.42), 1.0, 3.5); shot("vesper", (3, 0, 1.05), 2.5, 6.0); shot("nix", (-3, 0, 0.3), 0.5, 2.0)
print("SKETCH DONE", flush=True)
