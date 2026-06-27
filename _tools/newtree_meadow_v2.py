import bpy, os, math, random
random.seed(7)

# ===================== BLUER SKY =====================
sky = bpy.data.materials["SkyMat"]
nt = sky.node_tree; nt.nodes.clear()
o = nt.nodes.new("ShaderNodeOutputMaterial"); o.location=(700,0)
emis = nt.nodes.new("ShaderNodeEmission"); emis.location=(500,0)
emis.inputs["Strength"].default_value = 1.15
nt.links.new(emis.outputs[0], o.inputs[0])
tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location=(-900,0)
sep = nt.nodes.new("ShaderNodeSeparateXYZ"); sep.location=(-700,-200)
nt.links.new(tc.outputs["Object"], sep.inputs[0])
gmap = nt.nodes.new("ShaderNodeMapRange"); gmap.location=(-500,-200)
gmap.inputs["From Min"].default_value=-10.0; gmap.inputs["From Max"].default_value=120.0
nt.links.new(sep.outputs["Z"], gmap.inputs["Value"])
ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.location=(-300,-200)
ramp.color_ramp.elements[0].position=0.0; ramp.color_ramp.elements[0].color=(0.42,0.66,0.92,1)  # horizon (more blue)
ramp.color_ramp.elements[1].position=1.0; ramp.color_ramp.elements[1].color=(0.05,0.24,0.82,1)  # deep top blue
mid=ramp.color_ramp.elements.new(0.45); mid.color=(0.15,0.45,0.90,1)
nt.links.new(gmap.outputs["Result"], ramp.inputs["Fac"])
# clouds (kept lighter so blue dominates)
cn = nt.nodes.new("ShaderNodeVectorMath"); cn.operation='NORMALIZE'; cn.location=(-700,250)
nt.links.new(tc.outputs["Object"], cn.inputs[0])
noise = nt.nodes.new("ShaderNodeTexNoise"); noise.location=(-500,250)
noise.inputs["Scale"].default_value=3.2; noise.inputs["Detail"].default_value=8.0
noise.inputs["Roughness"].default_value=0.65
nt.links.new(cn.outputs["Vector"], noise.inputs["Vector"])
cramp = nt.nodes.new("ShaderNodeValToRGB"); cramp.location=(-300,250)
cramp.color_ramp.elements[0].position=0.50; cramp.color_ramp.elements[1].position=0.62
nt.links.new(noise.outputs["Fac"], cramp.inputs["Fac"])
hw = nt.nodes.new("ShaderNodeMapRange"); hw.location=(-500,80)
hw.inputs["From Min"].default_value=10.0; hw.inputs["From Max"].default_value=120.0
hw.inputs["To Min"].default_value=0.95; hw.inputs["To Max"].default_value=0.15; hw.clamp=True
nt.links.new(sep.outputs["Z"], hw.inputs["Value"])
cfac = nt.nodes.new("ShaderNodeMath"); cfac.operation='MULTIPLY'; cfac.location=(-80,150)
nt.links.new(cramp.outputs["Color"], cfac.inputs[0])
nt.links.new(hw.outputs["Result"], cfac.inputs[1])
white = nt.nodes.new("ShaderNodeRGB"); white.location=(-80,400); white.outputs[0].default_value=(1,1,1,1)
mix = nt.nodes.new("ShaderNodeMix"); mix.data_type='RGBA'; mix.location=(250,0)
nt.links.new(cfac.outputs[0], mix.inputs["Factor"])
nt.links.new(ramp.outputs["Color"], mix.inputs["A"])
nt.links.new(white.outputs[0], mix.inputs["B"])
nt.links.new(mix.outputs["Result"], emis.inputs["Color"])
# bluer ambient
wbg = bpy.context.scene.world.node_tree.nodes.get("Background")
if wbg:
    wbg.inputs[0].default_value=(0.45,0.62,0.92,1); wbg.inputs[1].default_value=0.55

# ===================== DISTANT CHERRY TREES (full bloom, natural) =====================
for o2 in list(bpy.data.objects):
    if o2.name.startswith("FarTree"):
        bpy.data.objects.remove(o2, do_unlink=True)

ftrunk = bpy.data.materials.get("FarTrunkMat") or bpy.data.materials.new("FarTrunkMat")
ftrunk.use_nodes = True
ftrunk.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value=(0.22,0.15,0.11,1)

def pink_mat(name, col):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (col[0],col[1],col[2],1)
    b.inputs["Roughness"].default_value = 0.85
    if "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value=(col[0],col[1],col[2],1)
        b.inputs["Emission Strength"].default_value=0.12
    return m
PINKS = [pink_mat("FarPink1",(0.93,0.66,0.78)),
         pink_mat("FarPink2",(0.86,0.50,0.67)),
         pink_mat("FarPink3",(0.96,0.80,0.87))]

# fuller rounded canopy: dome of lumps (offset x,y,z-frac, scale x,y,z)
LUMPS = [(0.0,0.0,0.95,0.95,0.95,0.85),
         (0.62,0.0,0.55,0.70,0.70,0.65),(-0.62,0.0,0.55,0.70,0.70,0.65),
         (0.0,0.62,0.55,0.70,0.70,0.65),(0.0,-0.62,0.55,0.70,0.70,0.65),
         (0.42,0.42,0.30,0.66,0.66,0.6),(-0.42,-0.42,0.30,0.66,0.66,0.6),
         (-0.42,0.42,0.35,0.62,0.62,0.55),(0.42,-0.42,0.35,0.62,0.62,0.55)]
n = 30
for i in range(n):
    ang = 2*math.pi*i/n + random.uniform(-0.12,0.12)
    rad = random.uniform(42,80)
    x,y = math.cos(ang)*rad, math.sin(ang)*rad
    s = random.uniform(3.2,6.2)
    th = s*0.55; cr = s*0.72
    pmat = random.choice(PINKS)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=s*0.11, radius2=s*0.06,
                                    depth=th, location=(x,y,th/2))
    tr = bpy.context.active_object; tr.name="FarTree%d_trunk"%i
    tr.data.materials.append(ftrunk)
    for j,(ox,oy,ozf,sx,sy,sz) in enumerate(LUMPS):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=cr,
                                              location=(x+ox*cr, y+oy*cr, th+ozf*cr))
        c = bpy.context.active_object; c.name="FarTree%d_c%d"%(i,j)
        c.scale=(sx*random.uniform(0.85,1.12), sy*random.uniform(0.85,1.12), sz)
        for p in c.data.polygons: p.use_smooth=True
        c.data.materials.append(pmat)

# ===================== RENDER =====================
sc = bpy.context.scene
sc.view_settings.view_transform='Standard'; sc.view_settings.exposure=0.3
sc.render.resolution_x=1200; sc.render.resolution_y=1200
sc.render.filepath=r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/newtree.png"
os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)
print("MEADOW V2 (bluer sky + pink far trees) DONE")
