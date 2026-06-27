import bpy
from mathutils import Vector
cam=bpy.data.objects["Camera"]
cam.location=(6.0,-26.0,5.0)
target=Vector((0,0,5.2))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=50
sc=bpy.context.scene
sc.render.resolution_x=1200; sc.render.resolution_y=1200
bpy.ops.wm.save_as_mainfile(filepath=r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/cherry_blossom_v2.blend")
print("CAM RESTORED + SAVED")
