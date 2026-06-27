import bpy, math, random, os
from mathutils import Vector, Matrix, Euler

LIB = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/petal_lib.py"
exec(compile(open(LIB, encoding="utf-8").read(), LIB, "exec"), globals())

CLUSTER_SCALE = 0.056
OUT = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/"
mat = bpy.data.materials.get("BlossomMat") or blossom_material()
TINTS = [(1.00, 0.93, 0.96), (1.00, 0.90, 0.94),
         (1.00, 0.84, 0.90), (1.00, 0.81, 0.88),
         (0.99, 0.72, 0.82), (0.98, 0.68, 0.79)]


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
    if not pts:
        return 0
    xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    zmin, zmax = min(zs), max(zs)
    R = max(math.hypot(p.x - cx, p.y - cy) for p in pts) or 1.0
    clusters = [build_cluster("Cluster%d" % gi, TINTS[gi], mat, random.Random(100 + gi)) for gi in range(6)]
    groups = {i: [] for i in range(6)}
    for p in pts:
        hf = (p.z - zmin) / max(0.01, zmax - zmin)
        of = math.hypot(p.x - cx, p.y - cy) / R
        score = 0.6 * hf + 0.4 * of
        base = 0 if score > 0.66 else (2 if score > 0.40 else 4)
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


# hide the airborne falling petals for clean stage stills
for nm in ("WindPetal", "PetalEmitter"):
    o = bpy.data.objects.get(nm)
    if o:
        o.hide_render = True

sc = bpy.context.scene
sc.render.resolution_x = 700; sc.render.resolution_y = 700
sc.render.image_settings.file_format = 'PNG'

stages = [("full", 1.00, 250), ("half", 0.50, 2400), ("empty", 0.12, 4800)]
for name, dens, carpet in stages:
    nc = build_canopy(dens)
    build_carpet(carpet)
    bpy.context.view_layer.update()
    sc.render.filepath = OUT + "stage_%s.png" % name
    bpy.ops.render.render(write_still=True)
    print("STAGE %s done: canopy=%d carpet=%d" % (name, nc, carpet))

# restore airborne petals visibility
for nm in ("WindPetal", "PetalEmitter"):
    o = bpy.data.objects.get(nm)
    if o:
        o.hide_render = False
print("ALL STAGES DONE")
