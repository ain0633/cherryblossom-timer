import bpy, math, random, os
from mathutils import Vector

LIB = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/petal_lib.py"
exec(compile(open(LIB, encoding="utf-8").read(), LIB, "exec"), globals())

random.seed(23)
BLOSSOM_DENSITY = 1.0   # 0..1 (낙화 연출 파라미터)
CLUSTER_SCALE = 0.056   # 1/5 of previous (realistic small blossoms)

# --- cleanup previous blossom/preview assets ---
for o in list(bpy.data.objects):
    if o.name.startswith(("Cluster", "BEmit", "BlossomEmitter", "Blossom", "PREVIEW_", "Petal")):
        bpy.data.objects.remove(o, do_unlink=True)

trunk = bpy.data.objects["Trunk"]
me = trunk.data
skin = me.skin_vertices[0].data
mw = trunk.matrix_world

# --- canopy seed nodes (thin branches, high enough) ---
seeds = []
for v, sd in zip(me.vertices, skin):
    co = mw @ v.co
    if co.z > 1.6 and sd.radius[0] < 0.25:
        seeds.append((co, sd.radius[0]))

# --- scatter cluster points hugging branch structure ---
pts = []
for co, r in seeds:
    k = random.randint(560, 900) if r < 0.13 else random.randint(300, 520)
    for _ in range(k):
        off = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)))
        if off.length == 0:
            continue
        off = off.normalized() * random.uniform(0.08, 0.62)
        p = co + off
        p.z += random.uniform(-0.05, 0.2)
        pts.append(p)
random.shuffle(pts)
pts = pts[:int(len(pts) * BLOSSOM_DENSITY)]

# --- canopy extents (for color-by-region) ---
xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
zmin, zmax = min(zs), max(zs)
R = max(math.hypot(p.x - cx, p.y - cy) for p in pts) or 1.0

# --- 6 cluster variants: light(top/outer) -> deep(inner/lower) ---
mat = blossom_material()
tints = [(1.00, 0.93, 0.96), (1.00, 0.90, 0.94),   # 0,1 light
         (1.00, 0.84, 0.90), (1.00, 0.81, 0.88),   # 2,3 mid
         (0.99, 0.72, 0.82), (0.98, 0.68, 0.79)]   # 4,5 deep
clusters = []
for gi in range(6):
    cl = build_cluster("Cluster%d" % gi, tints[gi], mat, random.Random(100 + gi))
    clusters.append(cl)

# --- assign each point to a variant by region, build 6 emitters ---
groups = {i: [] for i in range(6)}
for p in pts:
    hf = (p.z - zmin) / max(0.01, zmax - zmin)
    of = math.hypot(p.x - cx, p.y - cy) / R
    score = 0.6 * hf + 0.4 * of
    base = 0 if score > 0.66 else (2 if score > 0.40 else 4)
    groups[base + random.randint(0, 1)].append(p)

for gi in range(6):
    em = bpy.data.meshes.new("BEmit%d" % gi)
    em.from_pydata([list(p) for p in groups[gi]], [], [])
    em.update()
    eo = bpy.data.objects.new("BEmit%d" % gi, em)
    bpy.context.collection.objects.link(eo)
    cl = clusters[gi]
    cl.parent = eo
    cl.matrix_parent_inverse.identity()
    cl.location = (0, 0, 0)
    cl.scale = (CLUSTER_SCALE, CLUSTER_SCALE, CLUSTER_SCALE)
    eo.instance_type = 'VERTS'
    eo.show_instancer_for_render = False
    eo.show_instancer_for_viewport = False

# --- lighting: bright soft sky fill so petal undersides stay luminous ---
# (full teal-gradient sky comes in step 3)
bg = bpy.context.scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.62, 0.74, 0.80, 1)   # light cool-neutral sky
    bg.inputs[1].default_value = 0.6
sun = bpy.data.objects.get("KeySun")
if sun:
    sun.data.energy = 3.2
    sun.data.color = (1.0, 0.95, 0.86)

bpy.context.view_layer.update()

# --- render ---
sc = bpy.context.scene
sc.render.filepath = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/step2.png"
os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)
print("STEP2b DONE clusters=", len(pts), "groups=", {g: len(v) for g, v in groups.items()})
