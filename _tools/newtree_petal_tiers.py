import bpy, os
from mathutils import Vector

OUT = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/petals_seq/"
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene

# hide everything except airborne petals -> transparent overlay aligned to the stages
HIDE_PREFIX = ("Trunk", "Blossoms", "GroundCarpet", "FarTree", "SkyDome", "Ground", "Backdrop")
saved = {}
for o in bpy.data.objects:
    if o.name.startswith(HIDE_PREFIX):
        saved[o.name] = o.hide_render
        o.hide_render = True

# SAME baked composition camera as the stages (so petals align with the tree)
cam = bpy.data.objects["Camera"]
cam.location = (0.4, 44.0, 3.0)
cam.rotation_euler = (Vector((0, 0, 5.5)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 46
cam.data.sensor_width = 36.0
cam.data.sensor_fit = 'HORIZONTAL'
cam.data.clip_end = 1000

film_prev = sc.render.film_transparent
sc.render.film_transparent = True
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x = 1280
sc.render.resolution_y = 720
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'

emit = bpy.data.objects["PetalEmitter"]
ps = emit.particle_systems[0].settings

# tier 0 = sparse (near-empty tree) ... tier 2 = heavy (full tree)
TIERS = [(0, 6000), (1, 16000), (2, 30000)]
for idx, cnt in TIERS:
    ps.count = cnt
    d = OUT + ("t%d/" % idx)
    os.makedirs(d, exist_ok=True)
    for fn in os.listdir(d):
        if fn.endswith(".png"): os.remove(os.path.join(d, fn))
    sc.frame_start = -150       # warm-up frames fill the whole column -> 1..150 steady & seamless
    sc.frame_end = 150
    sc.render.filepath = d + "petal_"
    bpy.ops.render.render(animation=True)
    for fn in os.listdir(d):
        if fn.startswith("petal_-") or fn == "petal_0000.png":
            os.remove(os.path.join(d, fn))
    print("tier %d (count=%d) done" % (idx, cnt))

ps.count = 8000
sc.render.film_transparent = film_prev
sc.render.image_settings.color_mode = 'RGB'
for name, h in saved.items():
    o = bpy.data.objects.get(name)
    if o: o.hide_render = h
print("PETAL TIERS DONE ->", OUT)
