import bpy, os
from mathutils import Vector

sc = bpy.context.scene
cam = bpy.data.objects.get("Camera")
old = (tuple(cam.location), tuple(cam.rotation_euler), cam.data.lens)

cam.location = (5.5, -5.5, 4.8)
target = Vector((1.5, 0.5, 4.6))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 85

sc.render.filepath = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/step2_closeup.png"
os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)

cam.location, cam.rotation_euler, cam.data.lens = old[0], old[1], old[2]
print("CLOSEUP DONE")
