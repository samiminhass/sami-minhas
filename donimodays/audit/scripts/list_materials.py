import bpy,sys
bpy.ops.wm.open_mainfile(filepath=sys.argv[-1]); O=bpy.data.objects
seen={}
for o in sorted(bpy.context.scene.objects,key=lambda o:o.name):
    if o.type not in('MESH','CURVE') or not o.name[:4] in("MOR_","VES_","NIX_") or not o.visible_get(): continue
    for s in o.material_slots:
        m=s.material
        if not m: continue
        seen.setdefault(m.name,[]).append(o.name)
for m,objs in seen.items():
    mt=bpy.data.materials[m]; b=next((n for n in mt.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if mt.use_nodes else None
    def g(k):
        try: v=b.inputs[k].default_value; return round(v,2) if isinstance(v,float) else tuple(round(x,2) for x in v)[:3]
        except: return None
    print(m, "| rough",g("Roughness"),"coat",g("Coat Weight"),"coatR",g("Coat Roughness"),"thinfilm",g("Thin Film Thickness"),"emit",g("Emission Strength"),"| objs",len(objs),objs[:4])
