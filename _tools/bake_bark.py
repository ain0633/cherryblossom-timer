import bpy, os
ASSETS = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/assets/"
sc = bpy.context.scene

# --- duplicate trunk, apply modifiers, decimate ---
src = bpy.data.objects["Trunk"]
bpy.ops.object.select_all(action='DESELECT')
src.select_set(True); bpy.context.view_layer.objects.active = src
bpy.ops.object.duplicate()
bake = bpy.context.active_object
bake.name = "TrunkBake"
for m in list(bake.modifiers):
    try:
        bpy.ops.object.modifier_apply(modifier=m.name)
    except Exception as e:
        print("apply skip", m.name, e)
dec = bake.modifiers.new("D", "DECIMATE"); dec.ratio = 0.6
bpy.ops.object.modifier_apply(modifier=dec.name)

# own copy of the bark material (don't pollute original)
mat = bake.data.materials[0].copy()
bake.data.materials[0] = mat
nt = mat.node_tree

# --- UV unwrap ---
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

# --- bake target images ---
img_col = bpy.data.images.new("bark_basecol", 1024, 1024)
img_nrm = bpy.data.images.new("bark_normal", 1024, 1024, float_buffer=True)
img_nrm.colorspace_settings.name = 'Non-Color'
tex = nt.nodes.new("ShaderNodeTexImage")

sc.render.engine = 'CYCLES'
try:
    sc.cycles.samples = 16
    sc.cycles.use_denoising = False
except Exception:
    pass

def select_tex():
    for n in nt.nodes:
        n.select = False
    tex.select = True
    nt.nodes.active = tex

# base color
tex.image = img_col
select_tex()
bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, margin=4)
img_col.filepath_raw = ASSETS + "bark_basecol.png"; img_col.file_format = 'PNG'; img_col.save()
print("baked base color")

# normal (captures procedural bump furrows)
tex.image = img_nrm
select_tex()
bpy.ops.object.bake(type='NORMAL', margin=4)
img_nrm.filepath_raw = ASSETS + "bark_normal.png"; img_nrm.file_format = 'PNG'; img_nrm.save()
print("baked normal")

sc.render.engine = 'BLENDER_EEVEE'

# --- build baked image material for export ---
bm = bpy.data.materials.new("WebBarkBaked"); bm.use_nodes = True
bnt = bm.node_tree; bb = bnt.nodes.get("Principled BSDF")
tcol = bnt.nodes.new("ShaderNodeTexImage"); tcol.image = img_col
bnt.links.new(tcol.outputs["Color"], bb.inputs["Base Color"])
tnrm = bnt.nodes.new("ShaderNodeTexImage"); tnrm.image = img_nrm
nmap = bnt.nodes.new("ShaderNodeNormalMap")
bnt.links.new(tnrm.outputs["Color"], nmap.inputs["Color"])
bnt.links.new(nmap.outputs["Normal"], bb.inputs["Normal"])
bb.inputs["Roughness"].default_value = 0.9
bake.data.materials.clear(); bake.data.materials.append(bm)

# --- export ---
bpy.ops.object.select_all(action='DESELECT')
bake.select_set(True); bpy.context.view_layer.objects.active = bake
bpy.ops.export_scene.gltf(
    filepath=ASSETS + "trunk.glb", export_format='GLB',
    use_selection=True, export_apply=True,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
)
bpy.data.objects.remove(bake, do_unlink=True)
sz = os.path.getsize(ASSETS + "trunk.glb") / 1024 / 1024
print("BAKE+EXPORT done  trunk.glb %.2f MB" % sz)
