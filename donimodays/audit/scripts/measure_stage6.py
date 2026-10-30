import bpy,sys,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view as w2c
bpy.ops.wm.open_mainfile(filepath=sys.argv[-1])
sc=bpy.context.scene; O=bpy.data.objects
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920   # the saved file is 1920x1080; the video is 9:16
def grp(prefix): return [o for o in sc.objects if o.type in('MESH','CURVE') and o.name.startswith(prefix) and o.visible_get() and not o.hide_render]
def evalmesh(objs):
    dg=bpy.context.evaluated_depsgraph_get(); V=[];P=[]
    for o in objs:
        oe=o.evaluated_get(dg); me=oe.to_mesh(); off=len(V); mw=oe.matrix_world
        V+= [mw@v.co for v in me.vertices]; P+=[[off+i for i in p.vertices] for p in me.polygons]; oe.to_mesh_clear()
    return V,P
def depth(Va, Bt):
    # max penetration of vertices of A inside closed surface B (nearest-normal sign test)
    d=0.0;n=0
    for v in Va:
        loc,nrm,i,dist=Bt.find_nearest(v)
        if loc is not None and (v-loc).dot(nrm)<0 and dist<0.05: d=max(d,dist); n+=1
    return d,n
PAIRS={
 "MOR hands only vs MOR torso": (grp("MOR_hand_"), [O["MOR_torso"]]),
 "VES hands vs MOR crest": (grp("VES_hand_"), [O["MOR_crest"]]),
 "VES hands vs MOR body/face": (grp("VES_hand_"), [O["MOR_torso"],O["MOR_face"]]),
 "VES any vs MOR any": (grp("VES_"), grp("MOR_")),
 "NIX vs fragment": (grp("NIX_"), [O["S6_dream_fragment"]]),
 "NIX vs MOR": (grp("NIX_"), grp("MOR_")),
 "NIX vs VES": (grp("NIX_"), grp("VES_")),
 "MOR hands/arms vs MOR torso": (grp("MOR_hand_")+[O["MOR_arm_L"],O["MOR_arm_R"]], [O["MOR_torso"]]),
 "MOR hands vs fragment": (grp("MOR_hand_"), [O["S6_dream_fragment"]]),
 "VES hands vs VES mantle": (grp("VES_hand_"), [O["VES_mantle_crescent"],O["VES_panel_frontL_med"],O["VES_panel_right_med"],O["VES_core"]]),
 "MOR crest vs MOR torso": ([O["MOR_crest"]], [O["MOR_torso"]]),
}
marks=sorted([(m.frame,m.camera) for m in sc.timeline_markers if m.camera])
def cam_for(f): return [c for fr,c in marks if fr<=f][-1]
res={k:[] for k in PAIRS}; feet=[]; screen=[]
for f in range(sc.frame_start,sc.frame_end+1):
    sc.frame_set(f)
    for k,(A,B) in PAIRS.items():
        Va,Pa=evalmesh(A); Vb,Pb=evalmesh(B)
        ta=BVHTree.FromPolygons(Va,Pa); tb=BVHTree.FromPolygons(Vb,Pb)
        ov=len(ta.overlap(tb))
        dA,nA=depth(Va,tb) if ov else (0,0)
        res[k].append((f,ov,round(dA*1000,1),nA))
    fl=[]
    for s in "LR":
        V,_=evalmesh([O[f"MOR_foot_{s}"]]); zmin=min(v.z for v in V); c=sum(V,Vector())/len(V)
        fl.append((round(zmin*1000,1),round(c.x*1000,1),round(c.y*1000,1)))
    feet.append((f,fl))
    cam=cam_for(f); info={"f":f,"cam":cam.name}
    for name,objs in (("frag",[O["S6_dream_fragment"]]),("nix",grp("NIX_")),("ves_head",[O["VES_mask"],O["VES_halo"]]),("mor_face",[O["MOR_face"]]),("mor",grp("MOR_")),("ves",grp("VES_"))):
        V,_=evalmesh(objs); pts=[w2c(sc,cam,v) for v in V[::7]]
        xs=[p.x for p in pts]; ys=[p.y for p in pts]
        inside=sum(1 for p in pts if 0<=p.x<=1 and 0<=p.y<=1 and p.z>0)/len(pts)
        info[name]=dict(x0=round(min(xs),3),x1=round(max(xs),3),y0=round(min(ys),3),y1=round(max(ys),3),inframe=round(inside,2))
    # vesper gaze vs nix
    eyes=(sum(evalmesh([O["VES_eye_L"],O["VES_eye_R"]])[0],Vector())/len(evalmesh([O["VES_eye_L"],O["VES_eye_R"]])[0]))
    mask=sum(evalmesh([O["VES_mask"]])[0],Vector())/len(evalmesh([O["VES_mask"]])[0])
    nixc=sum(evalmesh([O["NIX_body"]])[0],Vector())/len(evalmesh([O["NIX_body"]])[0])
    morc=sum(evalmesh([O["MOR_face"]])[0],Vector())/len(evalmesh([O["MOR_face"]])[0])
    fwd=(eyes-mask).normalized()
    info["ves_gaze_to_nix_deg"]=round(math.degrees(fwd.angle(nixc-eyes)),1)
    info["ves_gaze_to_mor_deg"]=round(math.degrees(fwd.angle(morc-eyes)),1)
    info["frag_emit"]=round(O["S6_dream_fragment"].active_material.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value,2) if "Principled BSDF" in O["S6_dream_fragment"].active_material.node_tree.nodes else None
    screen.append(info)
json.dump({"pairs":res,"feet":feet,"screen":screen},open(sys.argv[-2],'w'))
print("done")
