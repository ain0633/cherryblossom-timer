import bpy, math, random
from mathutils import Vector

# Cherry skeleton tuned for a ROUND umbrella crown (ref 1/3): central-filled dome,
# slightly slimmer/taller trunk than step1. Topology per ref 2.
random.seed(11)

for o in list(bpy.data.objects):
    if o.type == 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)

verts = []; edges = []; radii = []
def node(p, r):
    verts.append(Vector(p)); radii.append(float(r)); return len(verts) - 1

def chain(start_idx, start_p, direction, length, segs, r_start, r_end,
          droop=0.0, wander=0.12, curve=0.0):
    prev = start_idx; p = Vector(start_p); d = Vector(direction).normalized()
    seg = length / segs; last = prev
    for k in range(1, segs + 1):
        t = k / segs
        dd = Vector((d.x + curve * t, d.y, d.z - droop * t))
        if dd.length > 0: dd.normalize()
        p = p + dd * seg + Vector((random.uniform(-wander, wander),
                                   random.uniform(-wander, wander),
                                   random.uniform(-wander * 0.3, wander * 0.3)))
        r = r_start * (1 - t) + r_end * t
        ni = node(p, r); edges.append((prev, ni)); prev = ni; last = ni
    return last, p

def branch(src_idx, out_dir, length, segs, r_start, r_end,
           droop=0.0, wander=0.12, curve=0.0):
    src_p = verts[src_idx]; pr = radii[src_idx]
    od = Vector(out_dir)
    if od.length > 0: od = od.normalized()
    cdir = Vector((0, 0, 1)) * 0.7 + od * 0.7
    if cdir.length > 0: cdir = cdir.normalized()
    clen = max(0.3, pr * 1.0); cp = src_p + cdir * clen
    cr = pr * 0.8 + r_start * 0.2; ci = node(cp, cr)
    edges.append((src_idx, ci))
    return chain(ci, cp, od, length, segs, r_start, r_end,
                 droop=droop, wander=wander, curve=curve)

def grow(src_idx, src_p, dvec, length, r0, r1, depth, droop_scale=1.0):
    segs = 5 if depth >= 2 else 4
    droop = (0.2 if depth >= 2 else random.uniform(0.35, 0.65)) * droop_scale
    end_idx, end_p = chain(src_idx, src_p, dvec, length, segs, r0, r1,
                           droop=droop, wander=0.16, curve=random.uniform(-0.12, 0.12))
    if depth <= 0: return
    nd = Vector(dvec)
    if nd.length > 0: nd.normalize()
    for _ in range(random.randint(2, 3)):
        ang = random.uniform(0, 2 * math.pi)
        perp = Vector((math.cos(ang), math.sin(ang), 0.0))
        child = nd + perp * random.uniform(0.45, 0.85)  # spread outward
        child.z += random.uniform(-0.05, 0.4)           # tips drift down -> droopy edges
        if child.length > 0: child.normalize()
        grow(end_idx, end_p, child, length * random.uniform(0.62, 0.78),
             r1, max(0.02, r1 * 0.62), depth - 1, droop_scale=droop_scale)

# trunk (slightly slimmer + taller)
base = node((0, 0, 0), 1.20)
trunk_last, trunk_top = chain(base, (0, 0, 0), (0.05, 0.03, 1.0), 3.0, 6, 1.18, 0.72, wander=0.12)
trunk_indices = list(range(base, trunk_last + 1))

# buttress roots
for i in range(9):
    a = 2 * math.pi * i / 9 + random.uniform(-0.2, 0.2)
    chain(base, (0, 0, 0.06), (math.cos(a), math.sin(a), -0.30), 2.0, 4, 0.86, 0.12,
          droop=-0.28, wander=0.12)

# primaries: WIDE umbrella - reach out far + arch, then droopy weeping tips (ref 3)
crown = trunk_indices[2:]
nprim = 8
for i in range(nprim):
    src = crown[int(i / nprim * len(crown))]
    a = 2 * math.pi * i / nprim + random.uniform(-0.22, 0.22)
    up = random.uniform(0.95, 1.35)                     # out + up -> broad rounded dome
    end_idx, end_p = branch(src, (math.cos(a) * 1.05, math.sin(a) * 1.05, up),
                            random.uniform(3.8, 4.8), 6, radii[src] * 0.72, 0.16,
                            droop=0.28, wander=0.2, curve=random.uniform(-0.12, 0.12))
    for _ in range(random.randint(2, 3)):
        ang = a + random.uniform(-0.7, 0.7)
        child = (math.cos(ang) * 0.85, math.sin(ang) * 0.85, random.uniform(0.5, 0.95))
        grow(end_idx, end_p, child, random.uniform(2.6, 3.4), 0.16, 0.06,
             depth=2, droop_scale=1.2)                  # gentle weeping tips

# central fill limbs: taller, low droop to hold the rounded top center (no notch)
for i in range(5):
    a = 2 * math.pi * i / 5 + random.uniform(-0.4, 0.4)
    end_idx, end_p = branch(trunk_last, (math.cos(a) * 0.35, math.sin(a) * 0.35, 1.9),
                            random.uniform(3.0, 3.8), 6, radii[trunk_last] * 0.6, 0.14,
                            droop=0.05, wander=0.22)
    for _ in range(random.randint(2, 3)):
        ang = random.uniform(0, 2 * math.pi)
        child = (math.cos(ang) * 0.5, math.sin(ang) * 0.5, random.uniform(0.8, 1.2))
        grow(end_idx, end_p, child, random.uniform(1.8, 2.6), 0.14, 0.05,
             depth=2, droop_scale=0.5)

# mesh + skin + subsurf
me = bpy.data.meshes.new("Trunk")
me.from_pydata([list(v) for v in verts], edges, []); me.update()
obj = bpy.data.objects.new("Trunk", me)
bpy.context.collection.objects.link(obj)
obj.modifiers.new("Skin", "SKIN")
sv = me.skin_vertices[0].data
for i, r in enumerate(radii): sv[i].radius = (r, r)
sv[base].use_root = True
sub = obj.modifiers.new("Subsurf", "SUBSURF"); sub.levels = 2; sub.render_levels = 2
cs = obj.modifiers.new("Smooth", "CORRECTIVE_SMOOTH")
cs.factor = 0.5; cs.iterations = 8; cs.smooth_type = 'LENGTH_WEIGHTED'
bpy.context.view_layer.objects.active = obj; obj.select_set(True)
bpy.ops.object.shade_smooth()

mat = bpy.data.materials.get("BarkMat") or bpy.data.materials.new("BarkMat")
mat.use_nodes = True
mat.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.20, 0.13, 0.10, 1)
obj.data.materials.clear(); obj.data.materials.append(mat)
print("SKELETON DONE verts=", len(verts), "top_z=", round(max(v.z for v in verts), 2))
