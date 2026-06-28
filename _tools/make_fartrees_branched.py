import bpy, math, random
random.seed(5)
ASSETS = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/assets/"

# --- clear old FarTrees ---
for o in list(bpy.data.objects):
    if o.name.startswith("FarTree"):
        bpy.data.objects.remove(o, do_unlink=True)


def get_mat(name, col, emis=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1)
    b.inputs["Roughness"].default_value = 0.85
    if emis > 0 and "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (col[0], col[1], col[2], 1)
        b.inputs["Emission Strength"].default_value = emis
    return m


ftrunk = get_mat("FarTrunkMat", (0.22, 0.15, 0.11))
PINKS = [get_mat("FarPink1", (0.93, 0.66, 0.78), 0.12),
         get_mat("FarPink2", (0.86, 0.50, 0.67), 0.12),
         get_mat("FarPink3", (0.96, 0.80, 0.87), 0.12)]

# fuller rounded canopy: dome of lumps (offset x,y, z-frac, scale x,y,z)
LUMPS = [(0.0, 0.0, 0.95, 0.95, 0.95, 0.85),
         (0.62, 0.0, 0.55, 0.70, 0.70, 0.65), (-0.62, 0.0, 0.55, 0.70, 0.70, 0.65),
         (0.0, 0.62, 0.55, 0.70, 0.70, 0.65), (0.0, -0.62, 0.55, 0.70, 0.70, 0.65),
         (0.42, 0.42, 0.30, 0.66, 0.66, 0.6), (-0.42, -0.42, 0.30, 0.66, 0.66, 0.6),
         (-0.42, 0.42, 0.35, 0.62, 0.62, 0.55), (0.42, -0.42, 0.35, 0.62, 0.62, 0.55)]


def build_branches(i, x, y, s, th, cr):
    verts = []; edges = []; radii = []
    def node(p, r):
        verts.append(p); radii.append((r, r)); return len(verts) - 1
    base = node((0, 0, 0), s * 0.12)
    top = node((0, 0, th * 0.85), s * 0.075)
    edges.append((base, top))
    nb = random.randint(4, 5)
    for k in range(nb):
        a = 2 * math.pi * k / nb + random.uniform(-0.35, 0.35)
        ez = th + cr * random.uniform(0.25, 0.62)
        ex = math.cos(a) * cr * random.uniform(0.32, 0.52)
        ey = math.sin(a) * cr * random.uniform(0.32, 0.52)
        mid = node((ex * 0.45, ey * 0.45, th + (ez - th) * 0.5), s * 0.045)
        end = node((ex, ey, ez), s * 0.018)
        edges.append((top, mid)); edges.append((mid, end))
    me = bpy.data.meshes.new("FarTree%d_branch" % i)
    me.from_pydata(verts, edges, [])
    me.update()
    obj = bpy.data.objects.new("FarTree%d_branch" % i, me)
    bpy.context.collection.objects.link(obj)
    obj.location = (x, y, 0)
    obj.modifiers.new("Skin", "SKIN")
    sv = me.skin_vertices[0].data
    for vi, (rx, ry) in enumerate(radii):
        sv[vi].radius = (rx, ry)
    sv[base].use_root = True
    sub = obj.modifiers.new("Subsurf", "SUBSURF"); sub.levels = 1; sub.render_levels = 1
    obj.data.materials.append(ftrunk)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True); bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Skin")
    bpy.ops.object.modifier_apply(modifier="Subsurf")


n = 24
for i in range(n):
    ang = 2 * math.pi * i / n + random.uniform(-0.12, 0.12)
    rad = random.uniform(40, 78)
    x, y = math.cos(ang) * rad, math.sin(ang) * rad
    s = random.uniform(3.2, 6.0)
    th = s * 0.55; cr = s * 0.72
    build_branches(i, x, y, s, th, cr)
    pmat = random.choice(PINKS)
    for j, (ox, oy, ozf, sx, sy, sz) in enumerate(LUMPS):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=cr,
                                              location=(x + ox * cr, y + oy * cr, th + ozf * cr))
        c = bpy.context.active_object; c.name = "FarTree%d_c%d" % (i, j)
        c.scale = (sx * random.uniform(0.85, 1.12), sy * random.uniform(0.85, 1.12), sz)
        for p in c.data.polygons:
            p.use_smooth = True
        c.data.materials.append(pmat)

# --- export ---
bpy.ops.object.select_all(action='DESELECT')
active = None
for o in bpy.data.objects:
    if o.name.startswith("FarTree"):
        o.select_set(True); active = o
bpy.context.view_layer.objects.active = active
bpy.ops.export_scene.gltf(filepath=ASSETS + "fartrees.glb", export_format='GLB',
                          use_selection=True, export_apply=True,
                          export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6)
import os
print("FARTREES BRANCHED DONE  %.2f MB" % (os.path.getsize(ASSETS + "fartrees.glb") / 1024 / 1024))
