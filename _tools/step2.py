import bpy, bmesh, math, random, os
from mathutils import Vector

random.seed(23)

BLOSSOM_DENSITY = 1.0   # 0..1  (낙화 연출용 파라미터)

# --- cleanup previous blossom assets (idempotent) ---
for n in ("BlossomEmitter", "Blossom"):
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)

trunk = bpy.data.objects["Trunk"]
me = trunk.data
skin = me.skin_vertices[0].data
mw = trunk.matrix_world

# --- gather canopy seed points: thin branch nodes high enough up ---
seeds = []
for v, sd in zip(me.vertices, skin):
    co = mw @ v.co
    r = sd.radius[0]
    if co.z > 1.6 and r < 0.25:
        seeds.append((co, r))

# --- dense blossom cloud hugging the actual branch structure ---
pts = []
for co, r in seeds:
    # thinner twigs get more blossoms
    k = random.randint(11, 22) if r < 0.13 else random.randint(6, 13)
    for _ in range(k):
        off = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)))
        if off.length == 0:
            continue
        off = off.normalized() * random.uniform(0.12, 0.75)
        p = co + off
        p.z += random.uniform(-0.05, 0.2)   # slight upward bias to round the dome
        pts.append(p)

random.shuffle(pts)
pts = pts[:int(len(pts) * BLOSSOM_DENSITY)]

# --- blossom cluster puff (low-poly icosphere; overlaps into a canopy mass) ---
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.5, location=(0, 0, 0))
blossom = bpy.context.active_object
blossom.name = "Blossom"
pm = blossom.data
bm = bmesh.new(); bm.from_mesh(pm)
for v in bm.verts:
    v.co = v.co * random.uniform(0.78, 1.18)   # irregular blobby shape
bm.to_mesh(pm); bm.free()
for p in pm.polygons:
    p.use_smooth = True

# blossom material: soft pink with translucency
bmat = bpy.data.materials.get("BlossomMat") or bpy.data.materials.new("BlossomMat")
bmat.use_nodes = True
bb = bmat.node_tree.nodes.get("Principled BSDF")
bb.inputs["Base Color"].default_value = (0.93, 0.46, 0.62, 1)
bb.inputs["Roughness"].default_value = 0.7
for key, val in (("Subsurface Weight", 0.25),):
    if key in bb.inputs:
        bb.inputs[key].default_value = val
if "Subsurface Radius" in bb.inputs:
    bb.inputs["Subsurface Radius"].default_value = (0.3, 0.12, 0.16)
blossom.data.materials.append(bmat)
blossom.location = (0, 0, 0)   # lone source sits hidden inside trunk base

# --- emitter mesh (vertices = scatter points) ---
emesh = bpy.data.meshes.new("BlossomEmitter")
emesh.from_pydata([list(p) for p in pts], [], [])
emesh.update()
emitter = bpy.data.objects.new("BlossomEmitter", emesh)
bpy.context.collection.objects.link(emitter)

# --- vertex instancing: one blossom per emitter vertex (deterministic) ---
blossom.scale = (1.45, 1.45, 1.45)
blossom.location = (0, 0, 0)
blossom.parent = emitter
emitter.instance_type = 'VERTS'
emitter.show_instancer_for_render = False
emitter.show_instancer_for_viewport = False

bpy.context.view_layer.update()
pcount = len(pts)

# --- lighting tweak so blossoms read as pink (full env in step 3) ---
bg = bpy.context.scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[1].default_value = 0.35
sun = bpy.data.objects.get("KeySun")
if sun:
    sun.data.energy = 2.6
    sun.data.color = (1.0, 0.95, 0.88)

# --- render ---
sc = bpy.context.scene
sc.render.filepath = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/step2.png"
os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)
print("STEP2 DONE seeds=", len(seeds), "blossoms=", len(pts), "particles=", pcount)
