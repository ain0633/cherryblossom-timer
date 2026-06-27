import bpy, os
ASSETS = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/assets/"
trunk = bpy.data.objects["Trunk"]

# temp solid bark material
orig_mats = [m for m in trunk.data.materials]
webbark = bpy.data.materials.get("WebBark") or bpy.data.materials.new("WebBark")
webbark.use_nodes = True
bb = webbark.node_tree.nodes.get("Principled BSDF")
bb.inputs["Base Color"].default_value = (0.16, 0.115, 0.09, 1)
bb.inputs["Roughness"].default_value = 0.9
trunk.data.materials.clear(); trunk.data.materials.append(webbark)

# temp decimate to cut polycount
dec = trunk.modifiers.new("WebDecimate", "DECIMATE")
dec.ratio = 0.3

bpy.ops.object.select_all(action='DESELECT')
trunk.select_set(True)
bpy.context.view_layer.objects.active = trunk
bpy.ops.export_scene.gltf(
    filepath=ASSETS + "trunk.glb", export_format='GLB',
    use_selection=True, export_apply=True,
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
)

# restore
trunk.modifiers.remove(dec)
trunk.data.materials.clear()
for m in orig_mats:
    trunk.data.materials.append(m)

sz = os.path.getsize(ASSETS + "trunk.glb") / 1024 / 1024
print("trunk.glb (decimated+draco)  %.2f MB" % sz)
