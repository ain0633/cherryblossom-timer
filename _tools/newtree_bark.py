import bpy, os

# ---- image-based bark material (ref 5 color quadrant + bump-derived normal) ----
TEX = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/tex/bark_color.png"

trunk = bpy.data.objects.get("Trunk")
assert trunk, "Trunk not found - run skeleton (step1) first"

img = bpy.data.images.get("bark_color.png")
if not img:
    img = bpy.data.images.load(TEX)
img.colorspace_settings.name = 'sRGB'

mat = bpy.data.materials.get("BarkMat") or bpy.data.materials.new("BarkMat")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (600, 0)
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (300, 0)
nt.links.new(bsdf.outputs[0], out.inputs[0])

tex = nt.nodes.new("ShaderNodeTexImage"); tex.location = (-200, 100); tex.image = img
tex.projection = 'BOX'; tex.projection_blend = 0.25     # box projection -> no UV needed
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

coord = nt.nodes.new("ShaderNodeTexCoord"); coord.location = (-700, 0)
mapn = nt.nodes.new("ShaderNodeMapping"); mapn.location = (-450, 0)
mapn.inputs["Scale"].default_value = (0.55, 0.55, 0.30)  # stretch grain vertically (Z)
nt.links.new(coord.outputs["Object"], mapn.inputs["Vector"])
nt.links.new(mapn.outputs["Vector"], tex.inputs["Vector"])

# bump from bark luminance
bump = nt.nodes.new("ShaderNodeBump"); bump.location = (50, -250)
bump.inputs["Strength"].default_value = 0.45
bump.inputs["Distance"].default_value = 0.04
nt.links.new(tex.outputs["Color"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

bsdf.inputs["Roughness"].default_value = 0.88
for k in ("Specular IOR Level", "Specular"):
    if k in bsdf.inputs:
        bsdf.inputs[k].default_value = 0.15; break

trunk.data.materials.clear(); trunk.data.materials.append(mat)
print("BARK DONE", img.size[0], img.size[1])
