import bpy, os
sc = bpy.context.scene
hidden = []
for o in bpy.data.objects:
    if o.name.startswith("Cluster"):
        hidden.append((o, o.hide_render)); o.hide_render = True
sc.frame_start = 1; sc.frame_end = 150
for f in range(1, 111):     # step the sim live to frame 110
    sc.frame_set(f)
sc.render.resolution_x = 480; sc.render.resolution_y = 480
sc.render.image_settings.file_format = 'PNG'
sc.render.filepath = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/petal_check.png"
bpy.ops.render.render(write_still=True)
for o, h in hidden:
    o.hide_render = h
print("CHECK DONE frame 110")
