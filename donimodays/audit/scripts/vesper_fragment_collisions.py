import bpy,sys
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath=sys.argv[-1]); sc=bpy.context.scene; O=bpy.data.objects
def T(o):
    dg=bpy.context.evaluated_depsgraph_get(); oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=oe.matrix_world
    t=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]); oe.to_mesh_clear(); return t
names=["VES_fragment_1","VES_fragment_2","VES_fragment_3","VES_halo","VES_hood","VES_mantle_crescent","VES_mask"]
hits={}
for f in range(1,145):
    sc.frame_set(f); t={n:T(O[n]) for n in names}
    for i,a in enumerate(names[:3]):
        for b in names[i+1:]:
            if t[a].overlap(t[b]): hits.setdefault((a,b),[]).append(f)
    if f==1: print("f1 halo-hood",len(t["VES_halo"].overlap(t["VES_hood"])),"halo-mantle",len(t["VES_halo"].overlap(t["VES_mantle_crescent"])),"halo-mask",len(t["VES_halo"].overlap(t["VES_mask"])))
for k,v in hits.items(): print(k, f"{len(v)} frames, f{v[0]}-f{v[-1]}")
