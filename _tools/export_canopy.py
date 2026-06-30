import bpy, random, shutil, os
random.seed(7)
ASSETS = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/assets/"

src = bpy.data.objects["Blossoms"]

# work on a copy so the open .blend is untouched
me = src.data.copy()
ob = bpy.data.objects.new("CanopyExport", me)
bpy.context.collection.objects.link(ob)
ob.matrix_world = src.matrix_world.copy()

# pack a per-vertex color attribute "Col" for the web shader:
#   r = Tint.Red / 2   (HSV value factor, *2 in shader -> up to ~1.45)
#   g = Tint.Green / 2 (HSV saturation factor)
#   b = per-card random (0..1) -> bloom threshold (card hidden when b > bloom)
tint = me.color_attributes["Tint"]  # CORNER float
existing = [a.name for a in me.color_attributes]
if "Col" in existing:
    me.color_attributes.remove(me.color_attributes["Col"])
col = me.color_attributes.new("Col", 'BYTE_COLOR', 'POINT')
for poly in me.polygons:
    rnd = random.random()
    li = poly.loop_indices[0]
    tr = min(1.0, tint.data[li].color[0] / 2.0)
    tg = min(1.0, tint.data[li].color[1] / 2.0)
    for vi in poly.vertices:
        col.data[vi].color = (tr, tg, rnd, 1.0)
me.color_attributes.active_color = col

bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True)
bpy.context.view_layer.objects.active = ob
out = ASSETS + "canopy.glb"
bpy.ops.export_scene.gltf(
    filepath=out, export_format='GLB', use_selection=True, export_apply=True,
    export_vertex_color='ACTIVE', export_normals=False,
)
print("canopy.glb size:", os.path.getsize(out), "verts", len(me.vertices), "polys", len(me.polygons))

# copy the card texture next to the glb
img = next(n.image for n in src.data.materials[0].node_tree.nodes if n.type == 'TEX_IMAGE')
shutil.copy(bpy.path.abspath(img.filepath), ASSETS + "flower_card.png")
print("flower_card.png copied")

bpy.data.objects.remove(ob, do_unlink=True)
bpy.data.meshes.remove(me, do_unlink=True)
print("DONE")
