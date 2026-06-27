import bpy, math, random, os
from mathutils import Vector, Matrix, Euler

LIB = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/petal_lib.py"
exec(compile(open(LIB, encoding="utf-8").read(), LIB, "exec"), globals())

OUT = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/stages/"
os.makedirs(OUT, exist_ok=True)
CLUSTER_SCALE = 0.072   # puffier, fuller clusters (reference look)
mat = blossom_material()   # rebuild so emission/glow updates apply
TINTS = [(1.00, 0.90, 0.93), (1.00, 0.87, 0.91),   # light (white-pink)
         (1.00, 0.72, 0.83), (1.00, 0.68, 0.80),   # mid pink
         (0.98, 0.52, 0.70), (0.96, 0.45, 0.65)]   # deep pink


def clear(prefixes):
    for o in list(bpy.data.objects):
        if o.name.startswith(prefixes):
            bpy.data.objects.remove(o, do_unlink=True)


def build_canopy(density):
    clear(("Cluster", "BEmit"))
    if density <= 0.001:
        return 0
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
    if not pts:
        return 0
    zs = [p.z for p in pts]
    cx = sum(p.x for p in pts) / len(pts); cy = sum(p.y for p in pts) / len(pts)
    zmin, zmax = min(zs), max(zs)
    R = max(math.hypot(p.x - cx, p.y - cy) for p in pts) or 1.0
    clusters = [build_cluster("Cluster%d" % gi, TINTS[gi], mat, random.Random(100 + gi)) for gi in range(6)]
    groups = {i: [] for i in range(6)}
    for p in pts:
        hf = (p.z - zmin) / max(0.01, zmax - zmin)
        of = math.hypot(p.x - cx, p.y - cy) / R
        score = 0.6 * hf + 0.4 * of
        base = 0 if score > 0.66 else (2 if score > 0.40 else 4)
        if random.random() < 0.12:      # scattered deep-pink pops across the canopy
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
    return len(pts)


def build_carpet(n):
    o = bpy.data.objects.get("GroundCarpet")
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
    if n <= 0:
        return
    random.seed(7)
    V = []; F = []; C = []
    for _ in range(n):
        a = random.uniform(0, 2 * math.pi)
        r = (random.uniform(0, 1) ** 0.5) * 7.5
        x, y = math.cos(a) * r, math.sin(a) * r
        M = (Matrix.Translation((x, y, 0.02))
             @ Euler((random.uniform(-0.16, 0.16), random.uniform(-0.16, 0.16), random.uniform(0, 6.28))).to_matrix().to_4x4()
             @ Matrix.Scale(0.10 * random.uniform(0.7, 1.2), 4))
        tint = (1.0, random.uniform(0.75, 0.92), random.uniform(0.85, 0.95))
        vs, faces, cols = petal_geom(M, tint)
        off = len(V); V.extend([list(v) for v in vs]); C.extend(cols)
        for f in faces:
            F.append((f[0] + off, f[1] + off, f[2] + off))
    cm = bpy.data.meshes.new("GroundCarpet"); cm.from_pydata(V, [], F); cm.update()
    for p in cm.polygons:
        p.use_smooth = True
    ca = cm.color_attributes.new("Col", 'BYTE_COLOR', 'POINT')
    for i, c in enumerate(C):
        ca.data[i].color = c
    co = bpy.data.objects.new("GroundCarpet", cm)
    bpy.context.collection.objects.link(co)
    co.data.materials.append(mat)


# hide airborne petals (those are a real-time overlay in the web)
for nm in ("WindPetal", "PetalEmitter"):
    o = bpy.data.objects.get(nm)
    if o:
        o.hide_render = True

# camera: pulled back, wide 16:9, whole tree with margin
cam = bpy.data.objects["Camera"]
cam.location = (0, -40.0, 5.5)
cam.rotation_euler = (Vector((0, 0, 5.5)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 40
cam.data.clip_end = 1000

sc = bpy.context.scene
sc.view_settings.exposure = 0.35   # brighter, dreamy
sc.render.resolution_x = 1600
sc.render.resolution_y = 900
sc.render.image_settings.file_format = 'JPEG'
sc.render.image_settings.quality = 88

N = 20
for i in range(N):
    f = i / (N - 1)              # 0 = full bloom, 1 = bare
    dens = max(0.0, 1.0 - f)
    carpet = int(f * 5200)
    nc = build_canopy(dens)
    build_carpet(carpet)
    bpy.context.view_layer.update()
    sc.render.filepath = OUT + "stage_%02d.jpg" % i
    bpy.ops.render.render(write_still=True)
    print("stage %02d: bloom=%.2f canopy=%d carpet=%d" % (i, dens, nc, carpet))

for nm in ("WindPetal", "PetalEmitter"):
    o = bpy.data.objects.get(nm)
    if o:
        o.hide_render = False
print("STAGES RENDERED:", N)
