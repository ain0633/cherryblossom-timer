import bpy, math, random, os
from mathutils import Vector
LIB = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/petal_lib.py"
exec(compile(open(LIB, encoding="utf-8").read(), LIB, "exec"), globals())

CLUSTER_SCALE = 0.072
mat = bpy.data.materials.get("BlossomMat") or blossom_material()
TINTS = [(1.00, 0.90, 0.93), (1.00, 0.87, 0.91), (1.00, 0.72, 0.83),
         (1.00, 0.68, 0.80), (0.98, 0.52, 0.70), (0.96, 0.45, 0.65)]


def clear(prefixes):
    for o in list(bpy.data.objects):
        if o.name.startswith(prefixes):
            bpy.data.objects.remove(o, do_unlink=True)


def build_canopy(density):
    clear(("Cluster", "BEmit"))
    trunk = bpy.data.objects["Trunk"]; me = trunk.data
    skin = me.skin_vertices[0].data; mw = trunk.matrix_world
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
    pts = pts[:int(len(pts) * density)]
    # report canopy extents to size the emitter
    zs = [p.z for p in pts]; xs = [p.x for p in pts]; ys = [p.y for p in pts]
    print("CANOPY extents: x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]" %
          (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
    cx = sum(xs) / len(xs); cy = sum(ys) / len(ys)
    zmin, zmax = min(zs), max(zs)
    R = max(math.hypot(p.x - cx, p.y - cy) for p in pts) or 1.0
    clusters = [build_cluster("Cluster%d" % gi, TINTS[gi], mat, random.Random(100 + gi)) for gi in range(6)]
    groups = {i: [] for i in range(6)}
    for p in pts:
        hf = (p.z - zmin) / max(0.01, zmax - zmin)
        of = math.hypot(p.x - cx, p.y - cy) / R
        score = 0.6 * hf + 0.4 * of
        base = 0 if score > 0.66 else (2 if score > 0.40 else 4)
        if random.random() < 0.12:
            base = 4
        groups[base + random.randint(0, 1)].append(p)
    for gi in range(6):
        em = bpy.data.meshes.new("BEmit%d" % gi)
        em.from_pydata([list(p) for p in groups[gi]], [], []); em.update()
        eo = bpy.data.objects.new("BEmit%d" % gi, em)
        bpy.context.collection.objects.link(eo)
        cl = clusters[gi]
        cl.parent = eo; cl.matrix_parent_inverse.identity()
        cl.location = (0, 0, 0); cl.scale = (CLUSTER_SCALE,) * 3
        eo.instance_type = 'VERTS'
        eo.show_instancer_for_render = False
        eo.show_instancer_for_viewport = False


build_canopy(1.0)
for nm in ("WindPetal", "PetalEmitter"):
    o = bpy.data.objects.get(nm)
    if o:
        o.hide_render = False

cam = bpy.data.objects["Camera"]
cam.location = (0, -40.0, 5.5)
cam.rotation_euler = (Vector((0, 0, 5.5)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 40

sc = bpy.context.scene
sc.render.film_transparent = False
sc.render.image_settings.color_mode = 'RGB'
sc.render.resolution_x = 1600; sc.render.resolution_y = 900
sc.render.image_settings.file_format = 'JPEG'
for f in range(1, 101):        # step sim to steady state
    sc.frame_set(f)
sc.render.filepath = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/petal_align.jpg"
bpy.ops.render.render(write_still=True)
print("ALIGN DIAG DONE")
