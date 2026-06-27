import bpy, os, random
from mathutils import Vector

LIB = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/petal_lib.py"
exec(compile(open(LIB, encoding="utf-8").read(), LIB, "exec"), globals())

# cleanup previews
for o in list(bpy.data.objects):
    if o.name.startswith(("PREVIEW_", "Cluster", "Petal")):
        bpy.data.objects.remove(o, do_unlink=True)

mat = blossom_material()
rng = random.Random(5)
cl = build_cluster("PREVIEW_Cluster", (1.0, 0.9, 0.94), mat, rng)
cl.location = (8, 0, 3)   # open space, away from the trunk

# dedicated preview camera + light (don't disturb the main scene camera much)
sc = bpy.context.scene
cam = bpy.data.objects.get("Camera")
old_loc = tuple(cam.location); old_rot = tuple(cam.rotation_euler); old_lens = cam.data.lens
cam.location = (8, -4.5, 3.4)
direction = Vector((8, 0, 3)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 80

bg = sc.world.node_tree.nodes.get("Background")
old_bg = bg.inputs[1].default_value
bg.inputs[1].default_value = 0.3

sc.render.filepath = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/preview_flower.png"
os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)

# restore camera/world for the main scene
cam.location = old_loc; cam.rotation_euler = old_rot; cam.data.lens = old_lens
bg.inputs[1].default_value = old_bg
print("PREVIEW DONE verts=", len(cl.data.vertices))
