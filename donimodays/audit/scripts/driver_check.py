import bpy,sys,collections
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
bpy.ops.wm.open_mainfile(filepath=sys.argv[-1])
print("auto exec:",bpy.context.preferences.filepaths.use_scripts_auto_execute)
tot=collections.Counter(); ex=collections.defaultdict(list)
for idb in list(bpy.data.objects)+list(bpy.data.shape_keys)+list(bpy.data.materials):
    ad=getattr(idb,'animation_data',None)
    if not ad: continue
    for fc in ad.drivers:
        d=fc.driver; k=(idb.name.split('_')[0] if hasattr(idb,'name') else '?', d.type, d.is_simple_expression if d.type=='SCRIPTED' else None)
        tot[k]+=1
        if d.type=='SCRIPTED' and not d.is_simple_expression and len(ex[k[0]])<4: ex[k[0]].append(d.expression)
for k,v in sorted(tot.items(),key=str): print(k,v)
print("non-simple examples:",dict(ex))
