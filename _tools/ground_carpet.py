import bpy, math, random
from mathutils import Matrix, Euler

LIB = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/petal_lib.py"
exec(compile(open(LIB, encoding="utf-8").read(), LIB, "exec"), globals())

random.seed(7)
SIZE = 0.10
blossom_mat = bpy.data.materials.get("BlossomMat") or blossom_material()

o = bpy.data.objects.get("GroundCarpet")
if o:
    bpy.data.objects.remove(o, do_unlink=True)

# thin layer of fallen petals lying flat on the grass (denser under the canopy)
V = []; F = []; C = []
for _ in range(4500):
    a = random.uniform(0, 2 * math.pi)
    r = (random.uniform(0, 1) ** 0.5) * 7.5          # denser toward center
    x, y = math.cos(a) * r, math.sin(a) * r
    yaw = random.uniform(0, 6.28)
    tilt = random.uniform(-0.16, 0.16)
    M = (Matrix.Translation((x, y, 0.02))
         @ Euler((tilt, tilt, yaw)).to_matrix().to_4x4()
         @ Matrix.Scale(SIZE * random.uniform(0.7, 1.2), 4))
    tint = (1.0, random.uniform(0.75, 0.92), random.uniform(0.85, 0.95))
    vs, faces, cols = petal_geom(M, tint)
    off = len(V); V.extend([list(v) for v in vs]); C.extend(cols)
    for f in faces:
        F.append((f[0] + off, f[1] + off, f[2] + off))

me = bpy.data.meshes.new("GroundCarpet"); me.from_pydata(V, [], F); me.update()
for p in me.polygons:
    p.use_smooth = True
ca = me.color_attributes.new("Col", 'BYTE_COLOR', 'POINT')
for i, c in enumerate(C):
    ca.data[i].color = c
ob = bpy.data.objects.new("GroundCarpet", me)
bpy.context.collection.objects.link(ob)
ob.data.materials.append(blossom_mat)
print("CARPET DONE petals=", 4500)
