import bpy, os, math, random
from mathutils import Vector, Matrix, Euler

LIB = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/petal_lib.py"
exec(compile(open(LIB, encoding="utf-8").read(), LIB, "exec"), globals())

random.seed(99)
SIZE = 0.18

# reuse existing blossom material (don't recreate -> canopy keeps its material)
blossom_mat = bpy.data.materials.get("BlossomMat") or blossom_material()

# cleanup previous petal layers
for nm in ("FallingPetals", "GroundPetals"):
    o = bpy.data.objects.get(nm)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)


def bake_petals(name, mats_tints):
    V = []; F = []; C = []
    for mat4, tint in mats_tints:
        vs, faces, cols = petal_geom(mat4, tint)
        off = len(V)
        V.extend([list(v) for v in vs]); C.extend(cols)
        for f in faces:
            F.append((f[0] + off, f[1] + off, f[2] + off))
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update()
    for p in me.polygons:
        p.use_smooth = True
    ca = me.color_attributes.new("Col", 'BYTE_COLOR', 'POINT')
    for i, c in enumerate(C):
        ca.data[i].color = c
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(blossom_mat)
    return obj


# --- (1) falling petals in the air (random tumble) ---
air = []
for _ in range(900):
    a = random.uniform(0, 2 * math.pi)
    r = random.uniform(0, 7.0)
    x, y = math.cos(a) * r, math.sin(a) * r
    z = random.uniform(0.4, 6.8)                 # below / around canopy
    rot = Euler((random.uniform(0, 6.28), random.uniform(0, 6.28), random.uniform(0, 6.28)))
    sc = SIZE * random.uniform(0.7, 1.3)
    M = Matrix.Translation((x, y, z)) @ rot.to_matrix().to_4x4() @ Matrix.Scale(sc, 4)
    tint = (1.0, random.uniform(0.80, 0.95), random.uniform(0.88, 0.98))
    air.append((M, tint))
bake_petals("FallingPetals", air)

# --- (2) fallen petals accumulated on the grass (denser under the tree) ---
ground = []
for _ in range(2200):
    a = random.uniform(0, 2 * math.pi)
    r = random.uniform(0, 1) ** 0.6 * 9.0        # denser toward center
    x, y = math.cos(a) * r, math.sin(a) * r
    yaw = random.uniform(0, 6.28)
    tilt = random.uniform(-0.18, 0.18)
    M = (Matrix.Translation((x, y, 0.02))
         @ Euler((tilt, tilt, yaw)).to_matrix().to_4x4()
         @ Matrix.Scale(SIZE * random.uniform(0.7, 1.2), 4))
    tint = (1.0, random.uniform(0.75, 0.92), random.uniform(0.85, 0.95))
    ground.append((M, tint))
bake_petals("GroundPetals", ground)

# --- render ---
sc = bpy.context.scene
sc.render.filepath = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/step_petals.png"
os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)
print("PETALS DONE air=", len(air), "ground=", len(ground))
