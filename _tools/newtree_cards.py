import bpy, bmesh, math, random
from mathutils import Vector

TEX = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/tex/flower_card.png"

# lighter/airier pink mix (Value mult, Saturation mult) to match ref 1/3
TONES = [(0.85, 1.15)]*18 + [(1.05, 0.95)]*38 + [(1.28, 0.65)]*32 + [(1.45, 0.38)]*12

def get_seeds():
    trunk = bpy.data.objects.get("Trunk")
    assert trunk, "Trunk not found - run skeleton first"
    me = trunk.data; sv = me.skin_vertices[0].data; mw = trunk.matrix_world
    seeds = []
    for i, v in enumerate(me.vertices):
        r = sv[i].radius[0]
        if r < 0.16:
            seeds.append((mw @ v.co, r))
    return seeds

def flower_material():
    img = bpy.data.images.get("flower_card.png") or bpy.data.images.load(TEX)
    img.colorspace_settings.name = 'sRGB'
    mat = bpy.data.materials.get("FlowerCard")
    if mat:
        return mat
    mat = bpy.data.materials.new("FlowerCard"); mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (700,0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (400,0)
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.location = (-300,200); tex.image = img
    attr = nt.nodes.new("ShaderNodeAttribute"); attr.location = (-300,-200); attr.attribute_name = "Tint"
    sep = nt.nodes.new("ShaderNodeSeparateColor"); sep.location = (-100,-200)
    nt.links.new(attr.outputs["Color"], sep.inputs["Color"])
    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location = (100,150)
    nt.links.new(tex.outputs["Color"], hsv.inputs["Color"])
    nt.links.new(sep.outputs[1], hsv.inputs["Saturation"])
    nt.links.new(sep.outputs[0], hsv.inputs["Value"])
    nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.7
    if "Emission Color" in bsdf.inputs:
        nt.links.new(hsv.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 0.18
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    for an, val in (("blend_method","HASHED"),("shadow_method","HASHED"),
                    ("surface_render_method","DITHERED")):
        try: setattr(mat, an, val)
        except Exception: pass
    mat.use_backface_culling = False
    return mat

def build_blossoms(density=1.0, seed=7):
    """Rebuild the Blossoms mesh; each candidate card is kept with prob=density
    (density 0.5 -> ~half the blossoms, evenly thinned -> 'half time, half bloom')."""
    random.seed(seed)
    seeds = get_seeds()
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")
    col_lay = bm.loops.layers.float_color.new("Tint")

    def _quad(pos, u2, v2, size, col):
        h = size*0.5
        p = [pos - u2*h - v2*h, pos + u2*h - v2*h, pos + u2*h + v2*h, pos - u2*h + v2*h]
        vs = [bm.verts.new(c) for c in p]
        f = bm.faces.new(vs)
        for lp, uv in zip(f.loops, [(0,0),(1,0),(1,1),(0,1)]):
            lp[uv_lay].uv = uv; lp[col_lay] = col

    def add_card(pos, n, size, tone):
        n = n.normalized()
        up = Vector((0,0,1))
        if abs(n.dot(up)) > 0.95: up = Vector((0,1,0))
        u = n.cross(up).normalized(); v = u.cross(n).normalized()
        roll = random.uniform(-0.5, 0.5)
        u2 = u*math.cos(roll) + v*math.sin(roll)
        v2 = -u*math.sin(roll) + v*math.cos(roll)
        col = (tone[0], tone[1], 1.0, 1.0)
        _quad(pos, u2, v2, size, col)
        _quad(pos, n, v2, size*0.9, col)

    count = 0
    for pos, r in seeds:
        radial = Vector((pos.x, pos.y, 0))
        if radial.length < 0.01: radial = Vector((random.uniform(-1,1), random.uniform(-1,1), 0))
        radial.normalize()
        k = 14 if r < 0.08 else (9 if r < 0.12 else 5)
        for _ in range(k):
            if random.random() > density:        # thin out by density
                continue
            jit = Vector((random.uniform(-0.45,0.45), random.uniform(-0.45,0.45), random.uniform(-0.35,0.40)))
            d = radial*random.uniform(0.4,1.0) + Vector((0,0,random.uniform(0.1,0.7))) + \
                Vector((random.uniform(-0.5,0.5), random.uniform(-0.5,0.5), 0))
            add_card(pos + jit, d, random.uniform(0.30, 0.52), random.choice(TONES))
            count += 1

    old = bpy.data.objects.get("Blossoms")
    if old: bpy.data.objects.remove(old, do_unlink=True)
    bme = bpy.data.meshes.new("Blossoms"); bm.to_mesh(bme); bm.free()
    obj = bpy.data.objects.new("Blossoms", bme)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(flower_material())
    print("BLOSSOMS density=%.2f cards=%d" % (density, count))
    return obj

def build_carpet(amount, seed=3):
    """Fallen-petal carpet on the grass: flat cards, count grows with amount (0..1).
    Denser toward the trunk; used by stage renders for ground accumulation."""
    random.seed(seed)
    old = bpy.data.objects.get("GroundCarpet")
    if old: bpy.data.objects.remove(old, do_unlink=True)
    amount = max(0.0, min(1.0, amount))
    n = int(3600 * amount)
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")
    col_lay = bm.loops.layers.float_color.new("Tint")
    for _ in range(n):
        a = random.uniform(0, 2*math.pi)
        rr = (random.random()**0.7) * 9.5        # clustered toward center
        cx, cy = math.cos(a)*rr, math.sin(a)*rr
        z = 0.04 + random.uniform(0, 0.02)
        s = random.uniform(0.14, 0.24)
        rot = random.uniform(0, 2*math.pi)
        u2 = Vector((math.cos(rot), math.sin(rot), 0))
        v2 = Vector((-math.sin(rot)*0.96, math.cos(rot)*0.96, random.uniform(-0.06,0.06)))
        pos = Vector((cx, cy, z)); h = s*0.5
        p = [pos - u2*h - v2*h, pos + u2*h - v2*h, pos + u2*h + v2*h, pos - u2*h + v2*h]
        vs = [bm.verts.new(c) for c in p]
        f = bm.faces.new(vs)
        col = random.choice(TONES); col = (col[0], col[1], 1.0, 1.0)
        for lp, uv in zip(f.loops, [(0,0),(1,0),(1,1),(0,1)]):
            lp[uv_lay].uv = uv; lp[col_lay] = col
    bme = bpy.data.meshes.new("GroundCarpet"); bm.to_mesh(bme); bm.free()
    obj = bpy.data.objects.new("GroundCarpet", bme)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(flower_material())
    print("CARPET amount=%.2f petals=%d" % (amount, n))
    return obj

# auto-build full canopy when run directly (main pipeline); stages set AUTO_BUILD=False
try:
    AUTO_BUILD
except NameError:
    AUTO_BUILD = True
if AUTO_BUILD:
    build_blossoms(1.0)
