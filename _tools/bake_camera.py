import bpy, math, os
from mathutils import Vector

# ---- capture current 3D viewport view into the scene Camera ----
view_mat = None; vlens = 50.0
for win in bpy.context.window_manager.windows:
    for area in win.screen.areas:
        if area.type == 'VIEW_3D':
            sp = area.spaces.active
            view_mat = sp.region_3d.view_matrix.copy()
            vlens = sp.lens
            break
    if view_mat: break
assert view_mat is not None, "no VIEW_3D viewport found"

cam = bpy.data.objects.get("Camera")
if not cam:
    cd = bpy.data.cameras.new("Camera"); cam = bpy.data.objects.new("Camera", cd)
    bpy.context.collection.objects.link(cam)
cam.matrix_world = view_mat.inverted()
cam.data.lens = vlens
cam.data.sensor_width = 36.0
cam.data.sensor_fit = 'HORIZONTAL'
cam.data.clip_end = 1000.0
bpy.context.scene.camera = cam

# ---- report for web sync (Blender Z-up -> three Y-up : [x, z, -y]) ----
loc = cam.matrix_world.translation
fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1))
tgt = loc + fwd * 30.0
def to_three(v): return (round(v.x, 3), round(v.z, 3), round(-v.y, 3))
aspect = 16/9
hfov = 2 * math.atan((cam.data.sensor_width / 2) / cam.data.lens)
print("CAM loc_blender=", tuple(round(c,3) for c in loc), "lens=", round(vlens,2))
print("three_pos=", to_three(loc))
print("three_lookAt=", to_three(tgt))
print("hfov_deg(16:9)=", round(math.degrees(hfov), 2))

# ---- test render ----
sc = bpy.context.scene
sc.render.resolution_x = 1600; sc.render.resolution_y = 900
sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = 0.3
sc.render.filepath = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/compose_test.png"
os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)
print("BAKE CAM DONE")
