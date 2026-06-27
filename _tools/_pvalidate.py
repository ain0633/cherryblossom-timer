import bpy, os
from mathutils import Vector
sc=bpy.context.scene
HIDE=("Trunk","Blossoms","GroundCarpet","FarTree","SkyDome","Ground","Backdrop")
for o in bpy.data.objects:
    if o.name.startswith(HIDE): o.hide_render=True
cam=bpy.data.objects["Camera"]
cam.location=(0.4,44.0,3.0); cam.rotation_euler=(Vector((0,0,5.5))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=46; cam.data.sensor_fit='HORIZONTAL'; cam.data.clip_end=1000
sc.render.film_transparent=True; sc.render.engine='BLENDER_EEVEE'
sc.render.resolution_x=1280; sc.render.resolution_y=720
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'
emit=bpy.data.objects["PetalEmitter"]; emit.particle_systems[0].settings.count=16000
d=r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/pv/"
os.makedirs(d,exist_ok=True)
sc.frame_start=-150; sc.frame_end=2; sc.render.filepath=d+"f_"
bpy.ops.render.render(animation=True)
# restore visibility for safety
for o in bpy.data.objects:
    if o.name.startswith(HIDE): o.hide_render=False
sc.render.film_transparent=False; sc.render.image_settings.color_mode='RGB'
print("PVALIDATE DONE")
