import bpy, math
from mathutils import Vector
cam=bpy.data.objects["Camera"]
cam.location=(3.0,-9.0,6.5)
target=Vector((0,0,7.0))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=70
sc=bpy.context.scene
sc.render.resolution_x=900; sc.render.resolution_y=900
sc.render.filepath=r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/newtree_closeup.png"
bpy.ops.render.render(write_still=True)
print("CLOSEUP DONE")
