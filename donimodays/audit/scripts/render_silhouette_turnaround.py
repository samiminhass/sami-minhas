import bpy,sys,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=sys.argv[-2]); OUT=sys.argv[-1]; sc=bpy.context.scene; O=bpy.data.objects
for o in sc.objects:
    if o.type=='ARMATURE': o.update_tag()
sc.frame_set(sc.frame_current); bpy.context.view_layer.update()
geo=[o for o in sc.objects if o.type in('MESH','CURVE') and o.visible_get() and not o.hide_render]
print("visible prefixes",sorted({o.name.split('_')[0] for o in geo}))
def mat(name,col,emit):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial')
    if emit: n=nt.nodes.new('ShaderNodeEmission'); n.inputs[0].default_value=col; nt.links.new(n.outputs[0],out.inputs[0])
    else: n=nt.nodes.new('ShaderNodeBsdfDiffuse'); n.inputs[0].default_value=col; nt.links.new(n.outputs[0],out.inputs[0])
    return m
BLACK=mat("sil",(0,0,0,1),True); CLAY=mat("clay",(0.6,0.6,0.6,1),False)
w=bpy.data.worlds.new("W"); w.use_nodes=True; bg=w.node_tree.nodes["Background"]; sc.world=w
cd=bpy.data.cameras.new("tc"); cam=bpy.data.objects.new("tc",cd); sc.collection.objects.link(cam); sc.camera=cam; cd.type='ORTHO'
sun=bpy.data.lights.new("ts",'SUN'); sun.energy=3; so=bpy.data.objects.new("ts",sun); sc.collection.objects.link(so); so.rotation_euler=(math.radians(50),0,math.radians(-35))
sc.render.engine='CYCLES'; sc.cycles.samples=8; sc.cycles.use_denoising=False; sc.render.resolution_x=240; sc.render.resolution_y=320; sc.render.film_transparent=False
sc.view_settings.view_transform='Standard'
chars={"MOR":[o for o in geo if o.name.startswith("MOR_")],"VES":[o for o in geo if o.name.startswith("VES_")],"NIX":[o for o in geo if o.name.startswith("NIX_")]}
for o in geo: o.hide_render=True
for k,objs in chars.items():
    for o in geo: o.hide_render = o not in objs
    pts=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box]
    lo=Vector([min(p[i] for p in pts) for i in range(3)]); hi=Vector([max(p[i] for p in pts) for i in range(3)]); c=(lo+hi)/2
    size=max(hi.z-lo.z,(hi.x-lo.x)*1.33,(hi.y-lo.y)*1.33)*1.12; cd.ortho_scale=size
    for ang in (0,45,90,180):
        a=math.radians(ang); d=Vector((math.sin(a),-math.cos(a),0)); cam.location=c+d*5; cam.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler()
        for mode in ("sil","clay"):
            bpy.context.view_layer.material_override = BLACK if mode=="sil" else CLAY
            bg.inputs[0].default_value=(1,1,1,1) if mode=="sil" else (0.35,0.35,0.35,1); bg.inputs[1].default_value=1.0
            so.hide_render = mode=="sil"
            sc.render.filepath=f"{OUT}/{k}_{mode}_{ang:03d}.png"; bpy.ops.render.render(write_still=True)
