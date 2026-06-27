import bpy
trunk = bpy.data.objects.get("Trunk")
print("=== SCENE CHECK ===")
print("total objects:", len(bpy.data.objects))
print("Trunk exists:", trunk is not None)
if trunk:
    print("Trunk modifiers:", [m.name + "(" + m.type + ")" for m in trunk.modifiers])
    print("Trunk material:", [m.name for m in trunk.data.materials])
    mat = trunk.data.materials[0] if trunk.data.materials else None
    if mat:
        print("BarkMat node count:", len(mat.node_tree.nodes))
clusters = [o for o in bpy.data.objects if o.name.startswith("Cluster")]
emit = [o for o in bpy.data.objects if o.name.startswith("BEmit")]
print("Cluster objects:", len(clusters))
print("Emitter objects:", len(emit), "instance_type:", [e.instance_type for e in emit])
total_inst = sum(len(e.data.vertices) for e in emit)
print("total blossom instances:", total_inst)
# viewport shading info
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for sp in area.spaces:
            if sp.type == 'VIEW_3D':
                print("Viewport shading:", sp.shading.type)
print("=== END ===")
