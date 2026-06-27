import bpy, math, random, os
from mathutils import Vector

random.seed(11)

# --- clear mesh objects ---
for o in list(bpy.data.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

# --- build woody skeleton (verts + edges + per-node radius) ---
verts = []; edges = []; radii = []

def node(p, r):
    verts.append(Vector(p)); radii.append(float(r)); return len(verts) - 1

def chain(start_idx, start_p, direction, length, segs, r_start, r_end,
          droop=0.0, wander=0.12, curve=0.0):
    prev = start_idx
    p = Vector(start_p)
    d = Vector(direction).normalized()
    seg = length / segs
    last = prev
    for k in range(1, segs + 1):
        t = k / segs
        dd = Vector((d.x + curve * t, d.y, d.z - droop * t))
        if dd.length > 0: dd.normalize()
        p = p + dd * seg + Vector((random.uniform(-wander, wander),
                                   random.uniform(-wander, wander),
                                   random.uniform(-wander * 0.3, wander * 0.3)))
        r = r_start * (1 - t) + r_end * t
        ni = node(p, r)
        edges.append((prev, ni)); prev = ni; last = ni
    return last, p

def branch(src_idx, out_dir, length, segs, r_start, r_end,
           droop=0.0, wander=0.12, curve=0.0):
    """Attach a branch with a thick 'collar' so it swells out of the parent
    (emerges upward, then bends toward out_dir) instead of poking out abruptly."""
    src_p = verts[src_idx]
    pr = radii[src_idx]
    od = Vector(out_dir)
    if od.length > 0: od = od.normalized()
    cdir = Vector((0, 0, 1)) * 0.7 + od * 0.7      # collar leans up then out
    if cdir.length > 0: cdir = cdir.normalized()
    clen = max(0.3, pr * 1.0)
    cp = src_p + cdir * clen
    cr = pr * 0.8 + r_start * 0.2                    # near-parent thickness (no step)
    ci = node(cp, cr)
    edges.append((src_idx, ci))
    return chain(ci, cp, od, length, segs, r_start, r_end,
                 droop=droop, wander=wander, curve=curve)

def grow(src_idx, src_p, dvec, length, r0, r1, depth):
    """Recursive natural branching: each branch spawns 2-3 thinner children,
    biased upward so the crown rounds out instead of splaying flat."""
    segs = 5 if depth >= 2 else 4
    droop = 0.15 if depth >= 2 else random.uniform(0.25, 0.7)
    end_idx, end_p = chain(src_idx, src_p, dvec, length, segs, r0, r1,
                           droop=droop, wander=0.16, curve=random.uniform(-0.12, 0.12))
    if depth <= 0:
        return
    nd = Vector(dvec)
    if nd.length > 0:
        nd.normalize()
    for _ in range(random.randint(2, 3)):
        ang = random.uniform(0, 2 * math.pi)
        perp = Vector((math.cos(ang), math.sin(ang), 0.0))
        child = nd + perp * random.uniform(0.45, 0.95)
        child.z += random.uniform(0.05, 0.45)      # upward bias -> rounded crown
        if child.length > 0:
            child.normalize()
        grow(end_idx, end_p, child, length * random.uniform(0.62, 0.78),
             r1, max(0.02, r1 * 0.62), depth - 1)

# trunk
base = node((0, 0, 0), 1.35)
# thick trunk that rises then divides into a few big limbs (natural rounded crown)
trunk_last, trunk_top = chain(base, (0, 0, 0), (0.05, 0.03, 1.0), 2.8, 6, 1.32, 0.80, wander=0.13)
trunk_indices = list(range(base, trunk_last + 1))

# buttress roots (prominent flare, like the reference)
for i in range(9):
    a = 2 * math.pi * i / 9 + random.uniform(-0.2, 0.2)
    chain(base, (0, 0, 0.06), (math.cos(a), math.sin(a), -0.30), 2.1, 4, 0.98, 0.12,
          droop=-0.28, wander=0.12)

# crown: a few thick limbs (collar) that recursively grow a natural rounded crown
crown = trunk_indices[2:]
nprim = 6
for i in range(nprim):
    src = crown[int(i / nprim * len(crown))]
    a = 2 * math.pi * i / nprim + random.uniform(-0.25, 0.25)
    up = random.uniform(0.9, 1.3)              # rise up + out (not flat splay)
    end_idx, end_p = branch(src, (math.cos(a) * 1.0, math.sin(a) * 1.0, up),
                            random.uniform(3.4, 4.4), 6, radii[src] * 0.72, 0.16,
                            droop=0.2, wander=0.2, curve=random.uniform(-0.12, 0.12))
    for _ in range(random.randint(2, 3)):
        ang = a + random.uniform(-0.7, 0.7)
        child = (math.cos(ang) * 0.8, math.sin(ang) * 0.8, random.uniform(0.7, 1.1))
        grow(end_idx, end_p, child, random.uniform(2.2, 3.0), 0.16, 0.06, depth=2)

# central limbs to fill the crown top
for i in range(3):
    a = random.uniform(0, 2 * math.pi)
    end_idx, end_p = branch(trunk_last, (math.cos(a) * 0.4, math.sin(a) * 0.4, 1.5),
                            random.uniform(2.6, 3.4), 6, radii[trunk_last] * 0.6, 0.14,
                            droop=0.05, wander=0.22)
    for _ in range(random.randint(2, 3)):
        ang = random.uniform(0, 2 * math.pi)
        child = (math.cos(ang) * 0.6, math.sin(ang) * 0.6, random.uniform(0.7, 1.1))
        grow(end_idx, end_p, child, random.uniform(1.8, 2.6), 0.14, 0.05, depth=2)

# --- mesh + skin + subsurf ---
me = bpy.data.meshes.new("Trunk")
me.from_pydata([list(v) for v in verts], edges, [])
me.update()
obj = bpy.data.objects.new("Trunk", me)
bpy.context.collection.objects.link(obj)

obj.modifiers.new("Skin", "SKIN")
sv = me.skin_vertices[0].data
for i, r in enumerate(radii):
    sv[i].radius = (r, r)
sv[base].use_root = True
sub = obj.modifiers.new("Subsurf", "SUBSURF")
sub.levels = 2; sub.render_levels = 2
cs = obj.modifiers.new("Smooth", "CORRECTIVE_SMOOTH")   # relax junction pinching
cs.factor = 0.5
cs.iterations = 8
cs.smooth_type = 'LENGTH_WEIGHTED'

bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.shade_smooth()

# bark material (basic; detailed texturing later)
mat = bpy.data.materials.get("BarkMat") or bpy.data.materials.new("BarkMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.20, 0.13, 0.10, 1)
bsdf.inputs["Roughness"].default_value = 0.85
obj.data.materials.clear(); obj.data.materials.append(mat)

# simple ground for context
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
ground = bpy.context.active_object; ground.name = "Ground"
gm = bpy.data.materials.new("GroundMat"); gm.use_nodes = True
gb = gm.node_tree.nodes.get("Principled BSDF")
gb.inputs["Base Color"].default_value = (0.45, 0.42, 0.20, 1)
gb.inputs["Roughness"].default_value = 1.0
ground.data.materials.append(gm)

# basic key light
sun = bpy.data.objects.get("KeySun")
if not sun:
    l = bpy.data.lights.new("KeySun", "SUN"); l.energy = 3.0
    sun = bpy.data.objects.new("KeySun", l); bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(55), 0, math.radians(35))

# simple teal world
world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.10, 0.45, 0.55, 1)
bg.inputs[1].default_value = 1.0

# camera framing (low angle)
cam = bpy.data.objects.get("Camera")
if not cam:
    cd = bpy.data.cameras.new("Camera"); cam = bpy.data.objects.new("Camera", cd)
    bpy.context.collection.objects.link(cam)
cam.location = (0, -16, 2.6)
direction = Vector((0, 0, 4.0)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 38
bpy.context.scene.camera = cam

# render
sc = bpy.context.scene
for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'):
    try:
        sc.render.engine = eng; break
    except Exception:
        pass
sc.render.resolution_x = 720; sc.render.resolution_y = 720
sc.render.filepath = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/step1.png"
os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)
print("STEP1 DONE engine=", sc.render.engine, "objects=", len(bpy.data.objects))
