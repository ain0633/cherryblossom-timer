import bpy, math, os
from mathutils import Vector

LOC = Vector((0.4, 44.0, 3.0))     # low front view from +Y, like the screenshot
AIM = Vector((0.0, 0.0, 5.5))      # tree lower-middle
LENS = 46.0

cam = bpy.data.objects["Camera"]
cam.location = LOC
cam.rotation_euler = (AIM - LOC).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = LENS
cam.data.sensor_width = 36.0
cam.data.sensor_fit = 'HORIZONTAL'
cam.data.clip_end = 1000.0
bpy.context.scene.camera = cam

loc = cam.matrix_world.translation
fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1))
tgt = loc + fwd * 30.0
def to_three(v): return (round(v.x, 3), round(v.z, 3), round(-v.y, 3))
hfov = 2 * math.atan((cam.data.sensor_width / 2) / cam.data.lens)
print("three_pos=", to_three(loc))
print("three_lookAt=", to_three(tgt))
print("hfov_deg=", round(math.degrees(hfov), 2), "lens=", LENS)

sc = bpy.context.scene
sc.render.resolution_x = 1600; sc.render.resolution_y = 900
sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = 0.3
sc.render.filepath = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/compose_test.png"
bpy.ops.render.render(write_still=True)
print("RECOMPOSE DONE")
