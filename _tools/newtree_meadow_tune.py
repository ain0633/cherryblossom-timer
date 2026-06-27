import bpy, os, math

# ---- richer sky: deeper blue + many horizon-weighted puffy clouds (bg ref) ----
sky = bpy.data.materials["SkyMat"]
nt = sky.node_tree; nt.nodes.clear()
o = nt.nodes.new("ShaderNodeOutputMaterial"); o.location=(700,0)
emis = nt.nodes.new("ShaderNodeEmission"); emis.location=(500,0)
emis.inputs["Strength"].default_value = 1.2
nt.links.new(emis.outputs[0], o.inputs[0])
tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location=(-900,0)
sep = nt.nodes.new("ShaderNodeSeparateXYZ"); sep.location=(-700,-200)
nt.links.new(tc.outputs["Object"], sep.inputs[0])

# vertical blue gradient (deep top -> pale horizon)
gmap = nt.nodes.new("ShaderNodeMapRange"); gmap.location=(-500,-200)
gmap.inputs["From Min"].default_value=-10.0; gmap.inputs["From Max"].default_value=120.0
nt.links.new(sep.outputs["Z"], gmap.inputs["Value"])
ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.location=(-300,-200)
ramp.color_ramp.elements[0].position=0.0; ramp.color_ramp.elements[0].color=(0.66,0.82,0.93,1)  # horizon
ramp.color_ramp.elements[1].position=1.0; ramp.color_ramp.elements[1].color=(0.09,0.33,0.80,1)  # deep top
mid=ramp.color_ramp.elements.new(0.45); mid.color=(0.28,0.56,0.90,1)
nt.links.new(gmap.outputs["Result"], ramp.inputs["Fac"])

# cloud mask: normalized-direction noise -> threshold
cn = nt.nodes.new("ShaderNodeVectorMath"); cn.operation='NORMALIZE'; cn.location=(-700,250)
nt.links.new(tc.outputs["Object"], cn.inputs[0])
noise = nt.nodes.new("ShaderNodeTexNoise"); noise.location=(-500,250)
noise.inputs["Scale"].default_value=3.2; noise.inputs["Detail"].default_value=8.0
noise.inputs["Roughness"].default_value=0.65
nt.links.new(cn.outputs["Vector"], noise.inputs["Vector"])
cramp = nt.nodes.new("ShaderNodeValToRGB"); cramp.location=(-300,250)
cramp.color_ramp.elements[0].position=0.46; cramp.color_ramp.elements[1].position=0.60
nt.links.new(noise.outputs["Fac"], cramp.inputs["Fac"])
# more clouds near horizon, clearer up top
hw = nt.nodes.new("ShaderNodeMapRange"); hw.location=(-500,80)
hw.inputs["From Min"].default_value=10.0; hw.inputs["From Max"].default_value=130.0
hw.inputs["To Min"].default_value=1.0; hw.inputs["To Max"].default_value=0.30; hw.clamp=True
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

# ---- distant trees: all green (remove pink), match reference treeline ----
fp = bpy.data.materials.get("FarPinkMat")
if fp:
    b = fp.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.17, 0.35, 0.12, 1)   # green like FarGreen

# ---- final render ----
sc = bpy.context.scene
sc.view_settings.view_transform='Standard'; sc.view_settings.exposure=0.3
sc.render.film_transparent=False
sc.render.resolution_x=1200; sc.render.resolution_y=1200
sc.render.filepath=r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/newtree.png"
os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)
print("MEADOW TUNE + RENDER DONE")
