import sys, os, math
sys.argv = ["blender", "--background", "--python", "x"]
SCENE_NAME = "VCMP"; HERE = "/home/user/sami-minhas/donimodays/blender"
src = open(HERE + "/cast_build.py").read()
if os.environ.get("NOSLOT"):
    src = src.replace('if P.get("slot", True):', 'if P.get("slot", False):')
exec(compile(src, "cb", "exec"))
from mathutils import Vector
OUTD = os.environ["OUT"]; os.makedirs(OUTD, exist_ok=True)
for o in mor.children_recursive + nix.children_recursive: o.hide_render = True
ves.location = (0, 0, 0); upd()
cam = scene.camera
def shot(nm, az, sil, el=4, d=6.0, t=Vector((0.05, -0.1, 0.8)), h=2.0):
    a = math.radians(az)
    cam.location = t + Vector((math.sin(a) * math.cos(math.radians(el)), -math.cos(a) * math.cos(math.radians(el)), math.sin(math.radians(el)))) * d
    cam.rotation_euler = (t - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.lens = 24 / (2 * math.tan(math.atan(h / 2 / d)))
    render(os.path.join(OUTD, nm + ".png"), 360, 600, samples=32, silhouette=sil)
shot("a_front", 0, False); shot("b_34", 35, False); shot("c_close", 15, False, el=8, d=3.0, t=Vector((0.04, -0.1, 1.0)), h=0.75)
for o in ves.children_recursive:
    if "halo" in o.name or "fragment" in o.name: o.hide_render = True
shot("d_sil_nohalo", 0, True)
print("VCMP DONE", flush=True)
