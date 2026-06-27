import bpy, os

sc = bpy.context.scene
hidden = []
for o in bpy.data.objects:
    if o.name.startswith("Cluster"):
        hidden.append((o, o.hide_render)); o.hide_render = True

sc.frame_start = 1
sc.frame_end = 150
sc.render.fps = 24
sc.render.resolution_x = 480
sc.render.resolution_y = 480

base = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/"
seq = base + "seq/"
os.makedirs(seq, exist_ok=True)

sc.render.image_settings.file_format = 'PNG'
sc.render.filepath = seq + "petal_"
bpy.ops.render.render(animation=True)

for o, h in hidden:
    o.hide_render = h
print("SEQ DONE frames %d-%d ->" % (sc.frame_start, sc.frame_end), seq)
