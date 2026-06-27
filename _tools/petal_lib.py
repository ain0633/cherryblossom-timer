# Shared cherry-blossom geometry library (petal -> flower -> cluster).
# Imported/execed by build scripts. Defines geometry builders + material.
import bpy, math, random
from mathutils import Vector, Matrix

# --- single petal: broad OVATE sakura petal w/ small V-notch, fan from center ---
#   rim runs CCW (normals up): base -> right side -> tip(notch) -> left side
PV = [(0.0,   0.00, 0.00),   # 0  base (flower center)
      (0.16,  0.18, 0.03),   # 1  R1
      (0.30,  0.45, 0.05),   # 2  R2
      (0.34,  0.68, 0.06),   # 3  R3 (widest)
      (0.26,  0.86, 0.07),   # 4  R4
      (0.12,  0.96, 0.08),   # 5  R5 (right of notch, rounded)
      (0.0,   0.90, 0.05),   # 6  NOTCH (small V dip)
      (-0.12, 0.96, 0.08),   # 7  L5 (left of notch)
      (-0.26, 0.86, 0.07),   # 8  L4
      (-0.34, 0.68, 0.06),   # 9  L3 (widest)
      (-0.30, 0.45, 0.05),   # 10 L2
      (-0.16, 0.18, 0.03),   # 11 L1
      (0.0,   0.55, -0.04)]  # 12 center (dipped -> cup)
PF = [(12, i, (i + 1) % 12) for i in range(12)]
PY = 0.96
PINK = Vector((0.88, 0.33, 0.50))
WHITE = Vector((0.99, 0.90, 0.93))


def _clamp(x):
    return max(0.0, min(1.0, x))


def petal_geom(mat, tint):
    vs = [mat @ Vector(p) for p in PV]
    cols = []
    for (x, y, z) in PV:
        t = _clamp(y / PY) ** 1.4   # keep pink lower, white only near the tip
        c = PINK.lerp(WHITE, t)
        cols.append((c.x * tint[0], c.y * tint[1], c.z * tint[2], 1.0))
    return vs, list(PF), cols


def bud_geom(mat, tint):
    s = 0.13
    pts = [(0, 0, -s), (s, 0, 0), (0, s, 0), (-s, 0, 0), (0, -s, 0), (0, 0, s * 1.5)]
    vs = [mat @ Vector(p) for p in pts]
    faces = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1),
             (5, 2, 1), (5, 3, 2), (5, 4, 3), (5, 1, 4)]
    deep = (0.80 * tint[0], 0.28 * tint[1], 0.42 * tint[2], 1.0)
    return vs, faces, [deep] * 6


def build_cluster(name, tint, mat, rng):
    V = []; F = []; C = []

    def emit(vs, faces, cols):
        off = len(V)
        V.extend([list(v) for v in vs]); C.extend(cols)
        for f in faces:
            F.append((f[0] + off, f[1] + off, f[2] + off))

    nflowers = rng.randint(1, 2)
    for _ in range(nflowers):
        fc = Vector((rng.uniform(-0.30, 0.30), rng.uniform(-0.30, 0.30), rng.uniform(-0.20, 0.25)))
        fs = rng.uniform(0.8, 1.1)
        flowerM = (Matrix.Translation(fc)
                   @ Matrix.Rotation(rng.uniform(0, 6.28), 4, 'Z')
                   @ Matrix.Rotation(rng.uniform(-0.5, 0.5), 4, 'X')
                   @ Matrix.Rotation(rng.uniform(-0.5, 0.5), 4, 'Y')
                   @ Matrix.Scale(fs, 4))
        for pi in range(5):
            petalM = flowerM @ Matrix.Rotation(pi * 2 * math.pi / 5, 4, 'Z') @ Matrix.Rotation(-0.35, 4, 'X')
            emit(*petal_geom(petalM, tint))
    for _ in range(rng.randint(0, 1)):
        bc = Vector((rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), rng.uniform(-0.1, 0.35)))
        emit(*bud_geom(Matrix.Translation(bc), tint))

    me = bpy.data.meshes.new(name)
    me.from_pydata(V, [], F); me.update()
    for p in me.polygons:
        p.use_smooth = True
    ca = me.color_attributes.new("Col", 'BYTE_COLOR', 'POINT')
    for i, c in enumerate(C):
        ca.data[i].color = c
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def blossom_material():
    mat = bpy.data.materials.get("BlossomMat")
    if mat:
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new("BlossomMat")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "Col"
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    # soft self-glow so blossoms look luminous/dreamy (not dark)
    if "Emission Color" in bsdf.inputs:
        nt.links.new(attr.outputs["Color"], bsdf.inputs["Emission Color"])
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = 0.28
    bsdf.inputs["Roughness"].default_value = 0.7
    for key, val in (("Subsurface Weight", 0.4),):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = val
    if "Subsurface Radius" in bsdf.inputs:
        bsdf.inputs["Subsurface Radius"].default_value = (0.4, 0.18, 0.22)
    # thin-petal translucency: let light pass through the backside
    if "Subsurface Scale" in bsdf.inputs:
        bsdf.inputs["Subsurface Scale"].default_value = 0.1
    return mat
