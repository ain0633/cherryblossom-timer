import bpy
print("=== BLENDFILE ===", bpy.data.filepath)
trunk = bpy.data.objects.get("Trunk")
print("=== Trunk exists ===", trunk is not None)
if trunk:
    me = trunk.data
    has_skin = len(me.skin_vertices) > 0
    print("Trunk verts:", len(me.vertices), "has_skin:", has_skin)
    mats = [m.name for m in trunk.data.materials]
    print("Trunk materials:", mats)
    bb = [trunk.matrix_world @ v.co for v in me.vertices]
    zs = [p.z for p in bb]
    print("Trunk z range:", round(min(zs), 2), round(max(zs), 2))
print("=== Mesh objects ===")
for o in bpy.data.objects:
    if o.type == 'MESH':
        print(" -", o.name, "verts", len(o.data.vertices))
