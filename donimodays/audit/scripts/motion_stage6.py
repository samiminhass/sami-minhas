import bpy,sys,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=sys.argv[-1]); sc=bpy.context.scene; O=bpy.data.objects
def cen(o):
    dg=bpy.context.evaluated_depsgraph_get(); oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=oe.matrix_world
    V=[mw@v.co for v in me.vertices]; oe.to_mesh_clear(); return V
track={"nix":"NIX_body","bead":"NIX_bead","ember":"MOR_ember","mor_face":"MOR_face","ves_handR":"VES_hand_R_palm","ves_handL":"VES_hand_L_palm","frag1":"VES_fragment_1","frag2":"VES_fragment_2","frag3":"VES_fragment_3","halo":"VES_halo","ves_mask":"VES_mask","fragment":"S6_dream_fragment"}
out={k:[] for k in track}; out["crest_tip"]=[]; cams={c.name:[] for c in O if c.type=='CAMERA' and c.name.startswith('CAM_')}
for f in range(1,145):
    sc.frame_set(f)
    for k,n in track.items():
        V=cen(O[n]); out[k].append(list(sum(V,Vector())/len(V)))
    V=cen(O["MOR_crest"]); out["crest_tip"].append(list(max(V,key=lambda v:v.z)))
    for c in cams: cams[c].append(list(O[c].matrix_world.translation))
out["cams"]=cams; json.dump(out,open(sys.argv[-2],'w'))
