import bpy, math, os
from mathutils import Vector

def grad_mat(name, top, bot, zlo, zhi, rough=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial"); o.location=(600,0)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled"); b.location=(350,0)
    b.inputs["Roughness"].default_value = rough
    coord = nt.nodes.new("ShaderNodeTexCoord"); coord.location=(-600,0)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); sep.location=(-400,0)
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.location=(-200,0)
    mr.inputs["From Min"].default_value=zlo; mr.inputs["From Max"].default_value=zhi
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.location=(0,0)
    ramp.color_ramp.elements[0].color=(bot[0],bot[1],bot[2],1)
    ramp.color_ramp.elements[1].color=(top[0],top[1],top[2],1)
    nt.links.new(coord.outputs["Object"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(b.outputs[0], o.inputs[0])
    return m

# ---- backdrop (vertical gradient like ref 1/3) ----
bd = bpy.data.objects.get("Backdrop")
if not bd:
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0,28,30))
    bd = bpy.context.active_object; bd.name="Backdrop"
    bd.rotation_euler=(math.radians(90),0,0)
bd.data.materials.clear()
bd.data.materials.append(grad_mat("BackdropMat",(0.80,0.85,0.90),(0.36,0.44,0.55),-20,55))

# ---- ground: pale blue-grey, soft sheen, receives shadow ----
gr = bpy.data.objects.get("Ground")
if not gr:
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0,0,0))
    gr = bpy.context.active_object; gr.name="Ground"
gm = bpy.data.materials.get("GroundMat") or bpy.data.materials.new("GroundMat")
gm.use_nodes=True; gb=gm.node_tree.nodes.get("Principled BSDF")
gb.inputs["Base Color"].default_value=(0.52,0.58,0.66,1)
gb.inputs["Roughness"].default_value=0.45
gr.data.materials.clear(); gr.data.materials.append(gm)

# ---- world ambient (soft cool) ----
w = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world=w; w.use_nodes=True
wb=w.node_tree.nodes.get("Background")
wb.inputs[0].default_value=(0.55,0.62,0.72,1); wb.inputs[1].default_value=0.6

# ---- warm afternoon key sun + cool fill ----
def sun(name,energy,rot,color):
    o=bpy.data.objects.get(name)
    if not o:
        l=bpy.data.lights.new(name,"SUN"); o=bpy.data.objects.new(name,l)
        bpy.context.collection.objects.link(o)
    o.data.energy=energy; o.data.color=color; o.rotation_euler=rot
    return o
sun("KeySun",3.2,(math.radians(52),math.radians(8),math.radians(40)),(1.0,0.92,0.80))
sun("FillSun",0.8,(math.radians(60),0,math.radians(-120)),(0.75,0.82,0.95))

# ---- camera: front, slightly side, tree ~80% of frame ----
cam=bpy.data.objects.get("Camera")
if not cam:
    cd=bpy.data.cameras.new("Camera"); cam=bpy.data.objects.new("Camera",cd)
    bpy.context.collection.objects.link(cam)
cam.location=(5.5,-31.0,4.6)
target=Vector((0,0,4.8))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=46
bpy.context.scene.camera=cam

# ---- render: EEVEE, Standard view transform, exposure ----
sc=bpy.context.scene
for eng in ('BLENDER_EEVEE_NEXT','BLENDER_EEVEE'):
    try: sc.render.engine=eng; break
    except Exception: pass
sc.view_settings.view_transform='Standard'
sc.view_settings.exposure=0.3
sc.render.film_transparent=False
sc.render.resolution_x=1200; sc.render.resolution_y=1200
cam.data.clip_end=1000
sc.render.filepath=r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/newtree.png"
os.makedirs(os.path.dirname(sc.render.filepath),exist_ok=True)
bpy.ops.render.render(write_still=True)
print("RENDER DONE engine=",sc.render.engine)
