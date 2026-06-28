import bpy, os
ASSETS = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/assets/"
os.makedirs(ASSETS, exist_ok=True)


def export_objs(names, path, apply=True):
    bpy.ops.object.select_all(action='DESELECT')
    active = None
    for n in names:
        o = bpy.data.objects.get(n)
        if o:
            o.select_set(True); active = o
    if active is None:
        print("!! no objects for", path); return
    bpy.context.view_layer.objects.active = active
    bpy.ops.export_scene.gltf(
        filepath=path, export_format='GLB', use_selection=True, export_apply=apply,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    )


# --- distant cherry trees (v2 FarTree0..29, ~9 pink canopy lumps + trunk each) ---
far = [o.name for o in bpy.data.objects if o.name.startswith("FarTree")]
export_objs(far, ASSETS + "fartrees.glb")
print("fartrees.glb:", len(far), "objects")

# --- ground (apply Subsurf + Displace -> rolling hills) ---
export_objs(["Ground"], ASSETS + "ground.glb")
print("ground.glb done")

for f in ("fartrees.glb", "ground.glb"):
    p = ASSETS + f
    if os.path.exists(p):
        print(f, "%.2f MB" % (os.path.getsize(p) / 1024 / 1024))
print("ENV EXPORT DONE")
