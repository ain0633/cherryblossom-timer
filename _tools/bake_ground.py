import bpy, os
ASSETS = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/assets/"
sc = bpy.context.scene

# --- duplicate ground, apply modifiers (Subsurf + Displace -> hill mesh) ---
src = bpy.data.objects["Ground"]
bpy.ops.object.select_all(action='DESELECT')
src.select_set(True); bpy.context.view_layer.objects.active = src
bpy.ops.object.duplicate()
bake = bpy.context.active_object; bake.name = "GroundBake"
for m in list(bake.modifiers):
    try:
        bpy.ops.object.modifier_apply(modifier=m.name)
    except Exception as e:
        print("apply skip", m.name, e)

# own copy of the grass material
mat = bake.data.materials[0].copy()
bake.data.materials[0] = mat
nt = mat.node_tree

# --- ensure UVs (the plane's 0..1 spans the whole ground) ---
if not bake.data.uv_layers:
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.001)
    bpy.ops.object.mode_set(mode='OBJECT')

# --- bake DIFFUSE/COLOR (procedural grass -> texture) ---
img = bpy.data.images.new("grass_basecol", 2048, 2048)
tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img
for n in nt.nodes:
    n.select = False
tex.select = True; nt.nodes.active = tex

sc.render.engine = 'CYCLES'
try:
    sc.cycles.samples = 24; sc.cycles.use_denoising = False
except Exception:
    pass
bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, margin=6)
img.filepath_raw = ASSETS + "grass_basecol.png"; img.file_format = 'PNG'; img.save()
print("baked grass color")

# --- baked image material + export ground.glb ---
bm = bpy.data.materials.new("WebGrass"); bm.use_nodes = True
bnt = bm.node_tree; bb = bnt.nodes.get("Principled BSDF")
tcol = bnt.nodes.new("ShaderNodeTexImage"); tcol.image = img
bnt.links.new(tcol.outputs["Color"], bb.inputs["Base Color"])
bb.inputs["Roughness"].default_value = 1.0
bake.data.materials.clear(); bake.data.materials.append(bm)

sc.render.engine = 'BLENDER_EEVEE'
bpy.ops.object.select_all(action='DESELECT')
bake.select_set(True); bpy.context.view_layer.objects.active = bake
bpy.ops.export_scene.gltf(
    filepath=ASSETS + "ground.glb", export_format='GLB',
    use_selection=True, export_apply=True,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
)
bpy.data.objects.remove(bake, do_unlink=True)
sz = os.path.getsize(ASSETS + "ground.glb") / 1024 / 1024
print("GROUND BAKE+EXPORT done  ground.glb %.2f MB" % sz)
