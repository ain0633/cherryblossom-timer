import bpy, os, math, random
from mathutils import Vector
random.seed(7)
L = lambda nt, a, b: nt.links.new(a, b)

# ===================== SKY DOME (blue sky + white clouds) =====================
old = bpy.data.objects.get("SkyDome")
if old:
    bpy.data.objects.remove(old, do_unlink=True)
bpy.ops.mesh.primitive_uv_sphere_add(radius=200, segments=48, ring_count=24)
dome = bpy.context.active_object; dome.name = "SkyDome"
for p in dome.data.polygons:
    p.use_smooth = True
try: dome.visible_shadow = False
except Exception: pass

sky = bpy.data.materials.get("SkyMat")
if sky:
    bpy.data.materials.remove(sky)
sky = bpy.data.materials.new("SkyMat"); sky.use_nodes = True
snt = sky.node_tree; snt.nodes.clear()
so = snt.nodes.new("ShaderNodeOutputMaterial")
emis = snt.nodes.new("ShaderNodeEmission")
snt.links.new(emis.outputs[0], so.inputs[0])
stc = snt.nodes.new("ShaderNodeTexCoord")
ssep = snt.nodes.new("ShaderNodeSeparateXYZ")
snt.links.new(stc.outputs["Object"], ssep.inputs[0])
smap = snt.nodes.new("ShaderNodeMapRange")
smap.inputs["From Min"].default_value = -10.0
smap.inputs["From Max"].default_value = 110.0
snt.links.new(ssep.outputs["Z"], smap.inputs["Value"])
# blue vertical gradient
sramp = snt.nodes.new("ShaderNodeValToRGB")
sramp.color_ramp.elements[0].position = 0.0
sramp.color_ramp.elements[0].color = (0.62, 0.80, 0.93, 1)   # horizon pale blue
sramp.color_ramp.elements[1].position = 1.0
sramp.color_ramp.elements[1].color = (0.12, 0.40, 0.82, 1)   # top deep blue
mid = sramp.color_ramp.elements.new(0.5); mid.color = (0.33, 0.60, 0.90, 1)
snt.links.new(smap.outputs["Result"], sramp.inputs["Fac"])
# fluffy white clouds via noise threshold (normalize direction -> big soft clouds)
cnorm = snt.nodes.new("ShaderNodeVectorMath"); cnorm.operation = 'NORMALIZE'
snt.links.new(stc.outputs["Object"], cnorm.inputs[0])
cnoise = snt.nodes.new("ShaderNodeTexNoise")
cnoise.inputs["Scale"].default_value = 2.2
cnoise.inputs["Detail"].default_value = 6.0
cnoise.inputs["Roughness"].default_value = 0.6
snt.links.new(cnorm.outputs["Vector"], cnoise.inputs["Vector"])
cramp = snt.nodes.new("ShaderNodeValToRGB")
cramp.color_ramp.elements[0].position = 0.54
cramp.color_ramp.elements[1].position = 0.66
snt.links.new(cnoise.outputs["Fac"], cramp.inputs["Fac"])
white = snt.nodes.new("ShaderNodeRGB"); white.outputs[0].default_value = (1.0, 1.0, 1.0, 1)
skymix = snt.nodes.new("ShaderNodeMix"); skymix.data_type = 'RGBA'
snt.links.new(cramp.outputs["Color"], skymix.inputs["Factor"])
snt.links.new(sramp.outputs["Color"], skymix.inputs["A"])
snt.links.new(white.outputs[0], skymix.inputs["B"])
snt.links.new(skymix.outputs["Result"], emis.inputs["Color"])
emis.inputs["Strength"].default_value = 1.25
dome.data.materials.clear(); dome.data.materials.append(sky)

# ===================== GROUND (lush green meadow, gentle hills, wildflowers) =====================
ground = bpy.data.objects.get("Ground")
if ground:
    ground.scale = (6, 6, 1)
    # subdivide + gentle hill displacement
    for m in list(ground.modifiers):
        ground.modifiers.remove(m)
    subd = ground.modifiers.new("Subd", "SUBSURF"); subd.subdivision_type = 'SIMPLE'
    subd.levels = 7; subd.render_levels = 7
    htex = bpy.data.textures.get("HillTex") or bpy.data.textures.new("HillTex", 'CLOUDS')
    htex.noise_scale = 9.0
    disp = ground.modifiers.new("Hills", "DISPLACE")
    disp.texture = htex; disp.texture_coords = 'GLOBAL'
    disp.strength = 0.9; disp.mid_level = 0.5

    gm = bpy.data.materials.get("GroundMat") or bpy.data.materials.new("GroundMat")
    gm.use_nodes = True
    gnt = gm.node_tree; gnt.nodes.clear()
    go = gnt.nodes.new("ShaderNodeOutputMaterial")
    gb = gnt.nodes.new("ShaderNodeBsdfPrincipled")
    gnt.links.new(gb.outputs[0], go.inputs[0])
    gtc = gnt.nodes.new("ShaderNodeTexCoord")
    # green variation
    gn = gnt.nodes.new("ShaderNodeTexNoise"); gn.inputs["Scale"].default_value = 10.0
    gnt.links.new(gtc.outputs["Object"], gn.inputs["Vector"])
    gr = gnt.nodes.new("ShaderNodeValToRGB")
    gr.color_ramp.elements[0].color = (0.15, 0.34, 0.09, 1)   # rich green
    gr.color_ramp.elements[1].color = (0.31, 0.52, 0.17, 1)   # lighter sunlit green
    gnt.links.new(gn.outputs["Fac"], gr.inputs["Fac"])
    # wildflower specks (tiny bright dots)
    fn = gnt.nodes.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 130.0
    gnt.links.new(gtc.outputs["Object"], fn.inputs["Vector"])
    fr = gnt.nodes.new("ShaderNodeValToRGB")
    fr.color_ramp.elements[0].position = 0.80
    fr.color_ramp.elements[1].position = 0.86
    gnt.links.new(fn.outputs["Fac"], fr.inputs["Fac"])
    flw = gnt.nodes.new("ShaderNodeRGB"); flw.outputs[0].default_value = (0.93, 0.92, 0.80, 1)
    gmix = gnt.nodes.new("ShaderNodeMix"); gmix.data_type = 'RGBA'
    gnt.links.new(fr.outputs["Color"], gmix.inputs["Factor"])
    gnt.links.new(gr.outputs["Color"], gmix.inputs["A"])
    gnt.links.new(flw.outputs[0], gmix.inputs["B"])
    gnt.links.new(gmix.outputs["Result"], gb.inputs["Base Color"])
    gb.inputs["Roughness"].default_value = 1.0
    ground.data.materials.clear(); ground.data.materials.append(gm)

# ===================== DISTANT TREES (mostly green, a few pink) =====================
for o in list(bpy.data.objects):
    if o.name.startswith("FarTree"):
        bpy.data.objects.remove(o, do_unlink=True)
fgreen = bpy.data.materials.get("FarGreenMat")
if fgreen:
    bpy.data.materials.remove(fgreen)
fgreen = bpy.data.materials.new("FarGreenMat"); fgreen.use_nodes = True
fgreen.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.18, 0.36, 0.13, 1)
fgreen.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = 1.0
fpink = bpy.data.materials.get("FarPinkMat")
if fpink:
    bpy.data.materials.remove(fpink)
fpink = bpy.data.materials.new("FarPinkMat"); fpink.use_nodes = True
fpink.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.86, 0.64, 0.75, 1)
fpink.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = 1.0
ftrunk = bpy.data.materials.get("FarTrunkMat")
if ftrunk:
    bpy.data.materials.remove(ftrunk)
ftrunk = bpy.data.materials.new("FarTrunkMat"); ftrunk.use_nodes = True
ftrunk.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.20, 0.14, 0.09, 1)

LUMPS = [(0.0, 0.0, 0.50, 1.00, 1.00, 0.85),
         (0.45, 0.10, 0.22, 0.70, 0.70, 0.60),
         (-0.40, 0.20, 0.28, 0.72, 0.72, 0.60),
         (0.05, -0.45, 0.20, 0.66, 0.66, 0.55),
         (-0.15, -0.10, 0.70, 0.55, 0.55, 0.50)]
n = 34
for i in range(n):
    ang = 2 * math.pi * i / n + random.uniform(-0.12, 0.12)
    rad = random.uniform(40, 78)
    x, y = math.cos(ang) * rad, math.sin(ang) * rad
    s = random.uniform(3.0, 6.0)
    th = s * 0.7; cr = s * 0.62
    canopy_mat = fpink if random.random() < 0.22 else fgreen
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=s * 0.10, radius2=s * 0.06,
                                    depth=th, location=(x, y, th / 2))
    tr = bpy.context.active_object; tr.name = "FarTree%d_trunk" % i
    tr.data.materials.append(ftrunk)
    for j, (ox, oy, ozf, sx, sy, sz) in enumerate(LUMPS):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=cr,
                                              location=(x + ox * cr, y + oy * cr, th + ozf * cr))
        c = bpy.context.active_object; c.name = "FarTree%d_c%d" % (i, j)
        c.scale = (sx * random.uniform(0.85, 1.1), sy * random.uniform(0.85, 1.1), sz)
        for p in c.data.polygons:
            p.use_smooth = True
        c.data.materials.append(canopy_mat)

# ===================== CAMERA / LIGHTING =====================
cam = bpy.data.objects.get("Camera")
if cam:
    cam.data.clip_end = 1000.0
sun = bpy.data.objects.get("KeySun")
if sun:
    sun.data.energy = 3.1
    sun.data.color = (1.0, 0.97, 0.90)
    sun.rotation_euler = (math.radians(48), 0, math.radians(35))
    try: sun.data.angle = math.radians(2.0)
    except Exception: pass
world = bpy.context.scene.world
wbg = world.node_tree.nodes.get("Background")
if wbg:
    wbg.inputs[0].default_value = (0.55, 0.70, 0.92, 1)   # blue-sky ambient
    wbg.inputs[1].default_value = 0.6

# ===================== RENDER =====================
sc = bpy.context.scene
sc.view_settings.view_transform = 'Standard'
try: sc.view_settings.look = 'None'
except Exception: pass
sc.render.filepath = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/step_env.png"
os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)
print("ENV DONE objects=", len(bpy.data.objects))
