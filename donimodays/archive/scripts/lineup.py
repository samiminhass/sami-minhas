import sys, os, math
sys.argv = ["blender", "--background", "--python", "x"]
SCENE_NAME = "LINEUP"; HERE = "/home/user/sami-minhas/donimodays/blender"
src = open(HERE + "/cast_build.py").read()
if os.environ.get("NOSLOT"):
    src = src.replace('if P.get("slot", True):', 'if P.get("slot", False):')
exec(compile(src, "cb", "exec"))
from mathutils import Vector
OUTD = os.environ["OUT"]; os.makedirs(OUTD, exist_ok=True)
mor.location = (0, 0, 0); mor.rotation_euler = (0, 0, math.radians(-8))
ves.location = (0.62, 0.12, 0); ves.rotation_euler = (0, 0, math.radians(-10))
nix.location = (-0.42, -0.02, 0.5); nix.rotation_euler = (0, 0, math.radians(12)); upd()
cam = scene.camera
def shot(nm, az, t=Vector((0.12, 0, 0.86)), d=7.0, h=2.0):
    a = math.radians(az)
    cam.location = t + Vector((math.sin(a), -math.cos(a), 0.08)) * d
    cam.rotation_euler = (t - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.lens = 24 / (2 * math.tan(math.atan(h / 2 / d)))
    render(os.path.join(OUTD, nm + ".png"), 1000, 1200, samples=64)
if os.environ.get("CLOSE"):
    shot("close_morrow", 20, t=Vector((0, 0, 0.32)), d=3.0, h=0.78)
    shot("close_vesper", 15, t=Vector((0.66, 0.05, 0.95)), d=5.0, h=1.95)
    shot("close_nix", 15, t=Vector((-0.42, -0.02, 0.5)), d=1.5, h=0.26)
else:
    shot("front", 0); shot("three_quarter", 30)
print("LINEUP DONE", flush=True)
