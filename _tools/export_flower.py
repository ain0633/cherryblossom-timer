import bpy, math, os
from mathutils import Matrix
LIB = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/petal_lib.py"
exec(compile(open(LIB, encoding="utf-8").read(), LIB, "exec"), globals())
ASSETS = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/assets/"

o = bpy.data.objects.get("WebFlower")
if o:
    bpy.data.objects.remove(o, do_unlink=True)

V = []; F = []; C = []
FL = 0.12
for pi in range(5):
    petalM = Matrix.Scale(FL, 4) @ Matrix.Rotation(pi * 2 * math.pi / 5, 4, 'Z') @ Matrix.Rotation(-0.35, 4, 'X')
    vs, faces, cols = petal_geom(petalM, (1.0, 1.0, 1.0))  # raw pink->white gradient
    off = len(V); V.extend([list(v) for v in vs]); C.extend(cols)
    for f in faces:
        F.append((f[0] + off, f[1] + off, f[2] + off))
fm = bpy.data.meshes.new("WebFlower"); fm.from_pydata(V, [], F); fm.update()
for p in fm.polygons:
    p.use_smooth = True
ca = fm.color_attributes.new("Col", 'BYTE_COLOR', 'POINT')
for i, c in enumerate(C):
    ca.data[i].color = c
flower = bpy.data.objects.new("WebFlower", fm)
bpy.context.collection.objects.link(flower)

# material that USES the vertex color so the exporter keeps COLOR_0
mat = bpy.data.materials.new("WebFlowerMat"); mat.use_nodes = True
nt = mat.node_tree
bsdf = nt.nodes.get("Principled BSDF")
vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "Col"
nt.links.new(vc.outputs["Color"], bsdf.inputs["Base Color"])
flower.data.materials.append(mat)

bpy.ops.object.select_all(action='DESELECT')
flower.select_set(True)
bpy.context.view_layer.objects.active = flower
bpy.ops.export_scene.gltf(filepath=ASSETS + "flower.glb", export_format='GLB',
                          use_selection=True, export_apply=True,
                          export_vertex_color='ACTIVE')
bpy.data.objects.remove(flower, do_unlink=True)
print("flower.glb re-exported with vertex colors")
