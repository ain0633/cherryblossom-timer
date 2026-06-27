import bpy, os
from mathutils import Vector

trunk = bpy.data.objects["Trunk"]

mat = bpy.data.materials.get("BarkMat")
if mat:
    bpy.data.materials.remove(mat)
mat = bpy.data.materials.new("BarkMat")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
L = nt.links.new

out = nt.nodes.new("ShaderNodeOutputMaterial")
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
L(bsdf.outputs[0], out.inputs[0])
tc = nt.nodes.new("ShaderNodeTexCoord")

# --- vertical furrows (bark cracks) via Voronoi distance-to-edge, stretched on Z ---
mfur = nt.nodes.new("ShaderNodeMapping")
mfur.inputs["Scale"].default_value = (2.5, 2.5, 0.55)   # elongate cells along trunk -> vertical furrows
L(tc.outputs["Object"], mfur.inputs["Vector"])
voro = nt.nodes.new("ShaderNodeTexVoronoi")
voro.feature = 'DISTANCE_TO_EDGE'
voro.inputs["Scale"].default_value = 3.5
L(mfur.outputs["Vector"], voro.inputs["Vector"])
crack = nt.nodes.new("ShaderNodeValToRGB")              # mask: high AT cracks
crack.color_ramp.elements[0].position = 0.0
crack.color_ramp.elements[0].color = (1, 1, 1, 1)
crack.color_ramp.elements[1].position = 0.16
crack.color_ramp.elements[1].color = (0, 0, 0, 1)
L(voro.outputs["Distance"], crack.inputs["Fac"])

# --- wood grain + fine micro detail ---
mgr = nt.nodes.new("ShaderNodeMapping")
mgr.inputs["Scale"].default_value = (5.0, 5.0, 1.3)
L(tc.outputs["Object"], mgr.inputs["Vector"])
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 9.0
noise.inputs["Detail"].default_value = 8.0
noise.inputs["Roughness"].default_value = 0.7
L(mgr.outputs["Vector"], noise.inputs["Vector"])
fine = nt.nodes.new("ShaderNodeTexNoise")
fine.inputs["Scale"].default_value = 28.0
fine.inputs["Detail"].default_value = 6.0
L(mgr.outputs["Vector"], fine.inputs["Vector"])

# --- horizontal cherry lenticels (thin broken dashes) ---
wave = nt.nodes.new("ShaderNodeTexWave")
wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'
wave.inputs["Scale"].default_value = 5.0
wave.inputs["Distortion"].default_value = 2.5
wave.inputs["Detail"].default_value = 2.0
L(tc.outputs["Object"], wave.inputs["Vector"])
wramp = nt.nodes.new("ShaderNodeValToRGB")
wramp.color_ramp.elements[0].position = 0.80
wramp.color_ramp.elements[1].position = 0.90
L(wave.outputs["Fac"], wramp.inputs["Fac"])
dash = nt.nodes.new("ShaderNodeTexNoise")
dash.inputs["Scale"].default_value = 16.0
L(mgr.outputs["Vector"], dash.inputs["Vector"])
dstep = nt.nodes.new("ShaderNodeMath"); dstep.operation = 'GREATER_THAN'
dstep.inputs[1].default_value = 0.5
L(dash.outputs["Fac"], dstep.inputs[0])
lent = nt.nodes.new("ShaderNodeMath"); lent.operation = 'MULTIPLY'
L(wramp.outputs["Color"], lent.inputs[0]); L(dstep.outputs[0], lent.inputs[1])

# --- colors (reddish-brown old cherry bark) ---
brown = nt.nodes.new("ShaderNodeRGB"); brown.outputs[0].default_value = (0.150, 0.080, 0.060, 1)
warm = nt.nodes.new("ShaderNodeRGB"); warm.outputs[0].default_value = (0.275, 0.155, 0.115, 1)
crackcol = nt.nodes.new("ShaderNodeRGB"); crackcol.outputs[0].default_value = (0.060, 0.032, 0.026, 1)
lentcol = nt.nodes.new("ShaderNodeRGB"); lentcol.outputs[0].default_value = (0.340, 0.235, 0.185, 1)

cmix1 = nt.nodes.new("ShaderNodeMix"); cmix1.data_type = 'RGBA'
L(noise.outputs["Fac"], cmix1.inputs["Factor"]); L(brown.outputs[0], cmix1.inputs["A"]); L(warm.outputs[0], cmix1.inputs["B"])
cmix2 = nt.nodes.new("ShaderNodeMix"); cmix2.data_type = 'RGBA'      # darken furrows
L(crack.outputs["Color"], cmix2.inputs["Factor"]); L(cmix1.outputs["Result"], cmix2.inputs["A"]); L(crackcol.outputs[0], cmix2.inputs["B"])
cmix3 = nt.nodes.new("ShaderNodeMix"); cmix3.data_type = 'RGBA'      # lenticel dashes
L(lent.outputs[0], cmix3.inputs["Factor"]); L(cmix2.outputs["Result"], cmix3.inputs["A"]); L(lentcol.outputs[0], cmix3.inputs["B"])

# --- moss: green patches, denser toward the base ---
moss_n = nt.nodes.new("ShaderNodeTexNoise"); moss_n.inputs["Scale"].default_value = 2.5
L(mfur.outputs["Vector"], moss_n.inputs["Vector"])
moss_r = nt.nodes.new("ShaderNodeValToRGB")
moss_r.color_ramp.elements[0].position = 0.60
moss_r.color_ramp.elements[1].position = 0.72
L(moss_n.outputs["Fac"], moss_r.inputs["Fac"])
gsep = nt.nodes.new("ShaderNodeSeparateXYZ")
L(tc.outputs["Object"], gsep.inputs[0])
gmap = nt.nodes.new("ShaderNodeMapRange")
gmap.inputs["From Min"].default_value = 0.3
gmap.inputs["From Max"].default_value = 2.6
gmap.inputs["To Min"].default_value = 0.6     # max ~60% moss blend, only near base
gmap.inputs["To Max"].default_value = 0.0
L(gsep.outputs["Z"], gmap.inputs["Value"])
mossmask = nt.nodes.new("ShaderNodeMath"); mossmask.operation = 'MULTIPLY'
L(moss_r.outputs["Color"], mossmask.inputs[0]); L(gmap.outputs["Result"], mossmask.inputs[1])
mosscol = nt.nodes.new("ShaderNodeRGB"); mosscol.outputs[0].default_value = (0.10, 0.135, 0.055, 1)
cmoss = nt.nodes.new("ShaderNodeMix"); cmoss.data_type = 'RGBA'
L(mossmask.outputs[0], cmoss.inputs["Factor"]); L(cmix3.outputs["Result"], cmoss.inputs["A"]); L(mosscol.outputs[0], cmoss.inputs["B"])
L(cmoss.outputs["Result"], bsdf.inputs["Base Color"])

# --- height -> strong bump (furrows deep, grain medium, micro subtle) ---
hcrack = nt.nodes.new("ShaderNodeMath"); hcrack.operation = 'MULTIPLY'
L(voro.outputs["Distance"], hcrack.inputs[0]); hcrack.inputs[1].default_value = 0.75
hnoise = nt.nodes.new("ShaderNodeMath"); hnoise.operation = 'MULTIPLY'
L(noise.outputs["Fac"], hnoise.inputs[0]); hnoise.inputs[1].default_value = 0.22
hfine = nt.nodes.new("ShaderNodeMath"); hfine.operation = 'MULTIPLY'
L(fine.outputs["Fac"], hfine.inputs[0]); hfine.inputs[1].default_value = 0.08
hadd1 = nt.nodes.new("ShaderNodeMath"); hadd1.operation = 'ADD'
L(hcrack.outputs[0], hadd1.inputs[0]); L(hnoise.outputs[0], hadd1.inputs[1])
hadd2 = nt.nodes.new("ShaderNodeMath"); hadd2.operation = 'ADD'
L(hadd1.outputs[0], hadd2.inputs[0]); L(hfine.outputs[0], hadd2.inputs[1])
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.85
bump.inputs["Distance"].default_value = 0.4
L(hadd2.outputs[0], bump.inputs["Height"])
L(bump.outputs["Normal"], bsdf.inputs["Normal"])

# --- roughness: rougher inside furrows ---
rmul = nt.nodes.new("ShaderNodeMath"); rmul.operation = 'MULTIPLY'
L(crack.outputs["Color"], rmul.inputs[0]); rmul.inputs[1].default_value = 0.15
radd = nt.nodes.new("ShaderNodeMath"); radd.operation = 'ADD'
L(rmul.outputs[0], radd.inputs[0]); radd.inputs[1].default_value = 0.78
L(radd.outputs[0], bsdf.inputs["Roughness"])

trunk.data.materials.clear()
trunk.data.materials.append(mat)

# --- preview: hide blossoms, close up on trunk ---
hidden = []
for o in bpy.data.objects:
    if o.name.startswith("Cluster"):
        hidden.append((o, o.hide_render)); o.hide_render = True
sc = bpy.context.scene
cam = bpy.data.objects.get("Camera")
old = (tuple(cam.location), tuple(cam.rotation_euler), cam.data.lens)
cam.location = (0, -6.5, 2.0)
cam.rotation_euler = (Vector((0, 0, 2.2)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 65
sc.render.filepath = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/step3_bark.png"
os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)
for o, h in hidden:
    o.hide_render = h
cam.location, cam.rotation_euler, cam.data.lens = old[0], old[1], old[2]
print("BARK DONE")
