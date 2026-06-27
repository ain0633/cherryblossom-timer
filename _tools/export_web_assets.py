import bpy, math, random, os, json
from mathutils import Vector, Matrix

LIB = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/petal_lib.py"
exec(compile(open(LIB, encoding="utf-8").read(), LIB, "exec"), globals())

ASSETS = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/assets/"
os.makedirs(ASSETS, exist_ok=True)

# group -> approximate flower tint color (light/outer -> deep/inner)
GROUP_COLOR = [(0.97, 0.86, 0.91), (0.96, 0.83, 0.89),
               (0.95, 0.72, 0.82), (0.95, 0.69, 0.80),
               (0.93, 0.58, 0.71), (0.92, 0.55, 0.69)]

# ---------- 1) blossom positions (regenerate scatter, sample ~15k) ----------
trunk = bpy.data.objects["Trunk"]
me = trunk.data
skin = me.skin_vertices[0].data
mw = trunk.matrix_world
random.seed(23)
seeds = [(mw @ v.co, sd.radius[0]) for v, sd in zip(me.vertices, skin)
         if (mw @ v.co).z > 1.6 and sd.radius[0] < 0.25]
pts = []
for co, r in seeds:
    k = random.randint(560, 900) if r < 0.13 else random.randint(300, 520)
    for _ in range(k):
        off = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)))
        if off.length == 0:
            continue
        p = co + off.normalized() * random.uniform(0.08, 0.62)
        p.z += random.uniform(-0.05, 0.2)
        pts.append(p)
random.shuffle(pts)
pts = pts[:15000]

zs = [p.z for p in pts]
xs = [p.x for p in pts]; ys = [p.y for p in pts]
cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
zmin, zmax = min(zs), max(zs)
R = max(math.hypot(p.x - cx, p.y - cy) for p in pts) or 1.0

positions = []; colors = []
for p in pts:
    hf = (p.z - zmin) / max(0.01, zmax - zmin)
    of = math.hypot(p.x - cx, p.y - cy) / R
    score = 0.6 * hf + 0.4 * of
    base = 0 if score > 0.66 else (2 if score > 0.40 else 4)
    gi = base + random.randint(0, 1)
    positions.append([round(p.x, 3), round(p.z, 3), round(-p.y, 3)])  # Blender Z-up -> three.js Y-up
    colors.append([round(c, 3) for c in GROUP_COLOR[gi]])

with open(ASSETS + "blossoms.json", "w") as f:
    json.dump({"positions": positions, "colors": colors}, f)
print("blossoms.json:", len(positions), "instances")

# ---------- 2) single web flower GLB (5 petals, vertex-color gradient) ----------
for nm in ("WebFlower",):
    o = bpy.data.objects.get(nm)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
V = []; F = []; C = []
FL = 0.12  # final flower scale (~Blender CLUSTER_SCALE world size)
for pi in range(5):
    petalM = Matrix.Scale(FL, 4) @ Matrix.Rotation(pi * 2 * math.pi / 5, 4, 'Z') @ Matrix.Rotation(-0.35, 4, 'X')
    vs, faces, cols = petal_geom(petalM, (1.0, 1.0, 1.0))   # raw gradient; tint applied per-instance in web
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
fmat = bpy.data.materials.new("WebFlowerMat"); fmat.use_nodes = True
flower.data.materials.append(fmat)

bpy.ops.object.select_all(action='DESELECT')
flower.select_set(True)
bpy.context.view_layer.objects.active = flower
bpy.ops.export_scene.gltf(filepath=ASSETS + "flower.glb", export_format='GLB',
                          use_selection=True, export_apply=True,
                          export_vertex_color='MATERIAL')
print("flower.glb exported")

# ---------- 3) trunk GLB (temporary solid bark material for export) ----------
orig_mats = [m for m in trunk.data.materials]
webbark = bpy.data.materials.new("WebBark"); webbark.use_nodes = True
bb = webbark.node_tree.nodes.get("Principled BSDF")
bb.inputs["Base Color"].default_value = (0.16, 0.115, 0.09, 1)
bb.inputs["Roughness"].default_value = 0.9
trunk.data.materials.clear(); trunk.data.materials.append(webbark)

bpy.ops.object.select_all(action='DESELECT')
trunk.select_set(True)
bpy.context.view_layer.objects.active = trunk
bpy.ops.export_scene.gltf(filepath=ASSETS + "trunk.glb", export_format='GLB',
                          use_selection=True, export_apply=True)

trunk.data.materials.clear()
for m in orig_mats:
    trunk.data.materials.append(m)

bpy.data.objects.remove(flower, do_unlink=True)
sz = os.path.getsize(ASSETS + "trunk.glb") / 1024 / 1024
print("trunk.glb exported  %.2f MB" % sz)
print("EXPORT DONE ->", ASSETS)
