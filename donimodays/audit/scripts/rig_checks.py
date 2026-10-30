import bpy,sys,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath=sys.argv[-1]); sc=bpy.context.scene; O=bpy.data.objects
def upd():
    for o in bpy.data.objects:
        if o.type=="ARMATURE": o.update_tag()
    sc.frame_set(sc.frame_current); bpy.context.view_layer.update()
def V(o):
    dg=bpy.context.evaluated_depsgraph_get(); oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=oe.matrix_world
    v=[mw@x.co for x in me.vertices]; p=[list(x.vertices) for x in me.polygons]; oe.to_mesh_clear(); return v,p
def cen(o): v,_=V(o); return sum(v,Vector())/len(v)
def ext(o):
    v,_=V(o); return [min(x[i] for x in v) for i in range(3)],[max(x[i] for x in v) for i in range(3)]
def overlap(a,b):
    va,pa=V(a); vb,pb=V(b); return len(BVHTree.FromPolygons(va,pa).overlap(BVHTree.FromPolygons(vb,pb)))
rigs={k:O[f"RIG_{k}"] for k in ("MOR","VES","NIX")}
D={k:{p:r[p] for p in r.keys() if isinstance(r[p],float)} for k,r in rigs.items()}
def reset():
    for k,r in rigs.items():
        for p,v in D[k].items(): r[p]=v
        for pb in r.pose.bones: pb.location=(0,0,0); pb.rotation_euler=(0,0,0); pb.rotation_quaternion=(1,0,0,0); pb.scale=(1,1,1)
    upd()
reset()
tested={"MOR":{"blink","lid_lower_L","brow_raise_R","brow_worry_L","mouth_smile","mouth_width","crest_mood","crest_lean","grip_L","grip_R"},
        "VES":{"blink","brow_raise_L","lid_lower_R","frag_shelter","frag_spread","frag_fluster","grip_R"},
        "NIX":{"attention","fin_A_flare","fin_B_sweep","lid_close","lid_mischief","lid_innocent"}}
print("== controls never exercised by the stage 5 control tests:",{k:sorted(set(D[k])-tested[k]) for k in D})
# direction checks
def mouth_corners():
    v,_=V(O["MOR_mouth"]); c=sum(v,Vector())/len(v)
    xs=sorted(v,key=lambda q:(q-c).x)
    left=xs[:10]; mid=sorted(v,key=lambda q:abs((q-c).x))[:10]
    return (sum(q.z for q in left)/10)-(sum(q.z for q in mid)/10)
reset(); r=rigs["MOR"]
for val in (-1,0,1):
    r["mouth_smile"]=val; upd(); print(f"MOR mouth_smile={val}: corner height relative to centre {mouth_corners()*1000:+.2f} mm")
reset()
def brow_tilt(side):
    v,_=V(O[f"MOR_brow_{side}"]); c=sum(v,Vector())/len(v)
    # inner end = the end nearer the face centre (x close to face centre x)
    fc=cen(O["MOR_face"])
    inner=sorted(v,key=lambda q:abs(q.x-fc.x))[:8]; outer=sorted(v,key=lambda q:-abs(q.x-fc.x))[:8]
    return (sum(q.z for q in inner)-sum(q.z for q in outer))/8
for side in "LR":
    for val in (-1,0,1):
        r[f"brow_worry_{side}"]=val; upd(); print(f"MOR brow_worry_{side}={val}: inner minus outer end height {brow_tilt(side)*1000:+.2f} mm")
    reset()
# blink coverage: eye area covered? approximate by lid lowest z vs pupil centre z
for val in (0,0.5,1):
    r["blink"]=val; upd(); lz=min(q.z for q in V(O["MOR_lid_L"])[0]); ez=ext(O["MOR_eye_L"]); 
    print(f"MOR blink={val}: upper lid lowest point {lz*1000:.1f} mm; eye spans {ez[0][2]*1000:.1f}..{ez[1][2]*1000:.1f} mm; lower lid top {max(q.z for q in V(O['MOR_lowlid_L'])[0])*1000:.1f}")
reset()
r["blink"]=1; r["lid_lower_L"]=1; upd(); print("MOR blink=1 + lid_lower_L=1: upper/lower lid surface overlaps:",overlap(O["MOR_lid_L"],O["MOR_lowlid_L"]))
reset()
# Morrow crest extremes vs body/face
for cm in (-1,0,1):
    for cl in (-1,1):
        r["crest_mood"]=cm; r["crest_lean"]=cl; upd()
        print(f"MOR crest_mood={cm} crest_lean={cl}: crest-torso overlaps {overlap(O['MOR_crest'],O['MOR_torso'])}, crest-face {overlap(O['MOR_crest'],O['MOR_face'])}")
reset()
print("MOR rest: hand palms vs torso overlaps", overlap(O["MOR_hand_L_palm"],O["MOR_torso"]), overlap(O["MOR_hand_R_palm"],O["MOR_torso"]))
# Vesper head rotation: does halo follow and stay centred on mask?
rv=rigs["VES"]
m0=cen(O["VES_mask"]); h0=cen(O["VES_halo"]); off0=(m0-h0).length
for ang in (20,40):
    rv.pose.bones["head"].rotation_euler=(math.radians(ang),0,0); upd()
    m1=cen(O["VES_mask"]); h1=cen(O["VES_halo"])
    print(f"VES head pitch {ang}deg: mask moves {(m1-m0).length*1000:.1f} mm, halo moves {(h1-h0).length*1000:.1f} mm, mask-halo centre offset {off0*1000:.1f} -> {(m1-h1).length*1000:.1f} mm")
reset()
print("VES halo parent:",O["VES_halo"].parent.name if O["VES_halo"].parent else None,O["VES_halo"].parent_bone, "| mask:",O["VES_mask"].parent_bone, "| frag1:",O["VES_fragment_1"].parent_bone)
print("VES rest: hand vs mantle overlaps",{h:sum(overlap(O[f"VES_hand_{h}_palm"],O[m]) for m in ("VES_mantle_crescent","VES_core","VES_panel_frontL_med","VES_panel_right_med")) for h in "LR"},
      "| hands vs each other", overlap(O["VES_hand_L_palm"],O["VES_hand_R_palm"]))
for sh,sp,fl in ((1,1,1),(1,-1,0),(1,-1,1)):
    rv["frag_shelter"]=sh; rv["frag_spread"]=sp; rv["frag_fluster"]=fl; upd()
    ov=[(a,b) for a in ("VES_fragment_1","VES_fragment_2","VES_fragment_3") for b in ("VES_fragment_1","VES_fragment_2","VES_fragment_3","VES_halo","VES_mask","VES_hood","VES_mantle_crescent") if a<b or b.startswith("VES_h") or b.startswith("VES_m") if a!=b and overlap(O[a],O[b])]
    print(f"VES shelter={sh} spread={sp} fluster={fl}: fragment collisions {ov}")
reset()
# Vesper bow: does the head stay visible / spine range
for a in (0.3,0.6):
    for b in ("spine_1","spine_2","spine_3"): rv.pose.bones[b].rotation_euler=(a,0,0)
    upd(); print(f"VES all spine bones pitched {math.degrees(a):.0f}deg: mask-vs-mantle overlaps {overlap(O['VES_mask'],O['VES_mantle_crescent'])}, halo-vs-mantle {overlap(O['VES_halo'],O['VES_mantle_crescent'])}, halo-vs-hood {overlap(O['VES_halo'],O['VES_hood'])}")
reset()
# Nix
rn=rigs["NIX"]
def eye_h(s): e=ext(O[f"NIX_eye_{s}"]); return [round((e[1][i]-e[0][i])*1000,1) for i in range(3)]
print("NIX eye extents mm (x,y,z) rest:",eye_h("L"),eye_h("R"))
for p in ("lid_mischief","lid_innocent","lid_close"):
    rn[p]=1; upd(); print(f"NIX {p}=1: eye L {eye_h('L')} R {eye_h('R')}"); reset()
for fa in (-1,1):
    for sw in (-1,1):
        rn["fin_A_flare"]=fa; rn["fin_B_flare"]=fa; rn["fin_A_sweep"]=sw; rn["fin_B_sweep"]=sw; upd()
        print(f"NIX flare={fa} sweep={sw}: fin A/B vs body overlaps {overlap(O['NIX_fin_A'],O['NIX_body'])}/{overlap(O['NIX_fin_B'],O['NIX_body'])}, fin vs edge {overlap(O['NIX_fin_A'],O['NIX_edge_1'])}/{overlap(O['NIX_fin_B'],O['NIX_edge_1'])}")
reset()
for at in (-230,-120,0,70):
    rn["attention"]=at; upd(); print(f"NIX attention={at}: bead vs body overlaps {overlap(O['NIX_bead'],O['NIX_body'])}, bead vs edge {overlap(O['NIX_bead'],O['NIX_edge_1'])}, vs fins {overlap(O['NIX_bead'],O['NIX_fin_A'])+overlap(O['NIX_bead'],O['NIX_fin_B'])}")
reset()
# sizes
for o in ("MOR_torso","VES_mantle_crescent","NIX_body"):
    e=ext(O[o]); print(o,"size mm",[round((e[1][i]-e[0][i])*1000) for i in range(3)])
allz={k:[] for k in ("MOR","VES","NIX")}
for o in sc.objects:
    if o.type in('MESH','CURVE') and o.visible_get() and o.name[:3] in allz:
        e=ext(o); allz[o.name[:3]]+= [e[0][2],e[1][2]]
print("overall heights mm",{k:(round(min(v)*1000),round(max(v)*1000)) for k,v in allz.items() if v})
# bone transform locks and rotation modes on controls
for k,r in rigs.items():
    ctrls=[b for b in r.pose.bones if b.custom_shape]
