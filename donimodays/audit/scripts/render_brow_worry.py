import bpy,sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=sys.argv[-2]); sc=bpy.context.scene; O=bpy.data.objects
for o in sc.objects:
    if o.type in('MESH','CURVE') and not o.name.startswith(('MOR_','STU','DRM','ENV')) and o.visible_get(): o.hide_render=True
r=O["RIG_MOR"]
def upd():
    r.update_tag(); sc.frame_set(sc.frame_current); bpy.context.view_layer.update()
def cen(o):
    return sum((o.matrix_world@Vector(c) for c in o.bound_box),Vector())/8
upd(); fc=cen(O["MOR_face"])
cd=bpy.data.cameras.new("c"); cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); cd.lens=85
cam.location=fc+Vector((0,-0.9,0.02)); cam.rotation_euler=(Vector((0,0.9,-0.02))).to_track_quat('-Z','Y').to_euler(); sc.camera=cam
sc.render.engine='CYCLES'; sc.cycles.samples=12; sc.cycles.use_denoising=True; sc.render.resolution_x=360; sc.render.resolution_y=300; sc.render.resolution_percentage=100
for w in (-1,0,1):
    r["brow_worry_L"]=w; r["brow_worry_R"]=w; r["mouth_smile"]=-1 if w==1 else 0; upd()
    sc.render.filepath=f"{sys.argv[-1]}/brow_{w:+d}.png"; bpy.ops.render.render(write_still=True)
