import sys, os, math
sys.argv = ["blender", "--background", "--python", "x"]
SCENE_NAME = "REVIEW"
HERE = "/home/user/sami-minhas/donimodays/blender"
__file__ = HERE + "/cast_build.py"
exec(compile(open(HERE + "/cast_build.py").read(), HERE + "/cast_build.py", "exec"))
OUTD = os.environ["RV_OUT"]; os.makedirs(OUTD, exist_ok=True)
from mathutils import Vector
camob = scene.camera
r = scene.render; r.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 24; scene.cycles.use_denoising = True
r.image_settings.file_format = 'PNG'; scene.view_settings.view_transform = 'AgX'
def shot(name, target, dist, az, el, h, w=600, hh=800, lens=60):
    t = Vector(target); a, e = math.radians(az), math.radians(el)
    camob.location = t + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    camob.rotation_euler = (t - camob.location).to_track_quat('-Z', 'Y').to_euler()
    camob.data.lens = lens; camob.data.sensor_fit = 'VERTICAL'; camob.data.sensor_height = 24
    camob.data.lens = 24 / (2 * math.tan(math.atan(h / 2 / dist)))
    r.resolution_x, r.resolution_y = w, hh
    r.filepath = os.path.join(OUTD, name + ".png"); bpy.ops.render.render(write_still=True); print("shot", name, flush=True)
RM = RIGS["morrow"][1]; RV = RIGS["vesper"][1]; RN = RIGS["nix"][1]
# spread them apart so each can be framed alone
mor.location = (0, 0, 0); ves.location = (3, 0, 0); nix.location = (-3, 0, 0.3); upd()
shot("mor_front", (0, 0, 0.3), 2.0, 0, 5, 0.75)
shot("mor_34", (0, 0, 0.3), 2.0, 35, 8, 0.75)
shot("mor_side", (0, 0, 0.3), 2.0, 90, 5, 0.75)
RM["crest_mood"] = -1.0; RM["brow_worry_L"] = RM["brow_worry_R"] = 1.0; upd()
shot("mor_fright_crest", (0, 0.02, 0.45), 1.2, 60, 15, 0.32)
RM["crest_mood"] = 1.0; RM["brow_worry_L"] = RM["brow_worry_R"] = 0.0; upd()
shot("mor_crest_back", (0, 0.03, 0.5), 1.2, 160, 15, 0.3)
shot("ves_front", (3, 0, 0.85), 5.0, 0, 5, 2.0)
shot("ves_34", (3, 0, 0.85), 5.0, 40, 5, 2.0)
shot("ves_back34", (3, 0, 0.85), 5.0, 150, 5, 2.0)
shot("nix_front", (-3, 0, 0.3), 1.0, 0, 0, 0.24)
RN["lid_mischief"] = 1.0; upd(); shot("nix_mischief", (-3.045, 0, 0.3), 0.6, 0, 0, 0.08)
RN["lid_mischief"] = 0.0; RN["lid_innocent"] = 1.0; upd(); shot("nix_innocent", (-3.045, 0, 0.3), 0.6, 0, 0, 0.08)
RN["lid_innocent"] = 0.0; upd(); shot("nix_34", (-3, 0, 0.3), 1.0, 40, 10, 0.24)
print("REVIEW DONE", flush=True)
