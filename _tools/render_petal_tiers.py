import bpy, os
from mathutils import Vector

OUT = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/petals_seq/"
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene

# hide everything except airborne petals -> transparent, same camera
HIDE_PREFIX = ("Trunk", "Cluster", "BEmit", "GroundCarpet", "FarTree", "SkyDome", "Ground")
saved = {}
for o in bpy.data.objects:
    if o.name.startswith(HIDE_PREFIX):
        saved[o.name] = o.hide_render
        o.hide_render = True
for nm in ("PetalEmitter", "WindPetal"):
    o = bpy.data.objects.get(nm)
    if o:
        saved[nm] = o.hide_render
        o.hide_render = False

# camera: same pulled-back wide framing as the stages (so petals align)
cam = bpy.data.objects["Camera"]
cam.location = (0, -40.0, 5.5)
cam.rotation_euler = (Vector((0, 0, 5.5)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 40
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

# tier index -> emission count (0 = almost-empty tree, 2 = full tree)
# render -60..150: frames <=0 are warm-up (field fills) so 1..150 is a full, seamless loop
TIERS = [(0, 1500), (1, 6000), (2, 12000)]
for idx, cnt in TIERS:
    ps.count = cnt
    d = OUT + ("t%d/" % idx)
    os.makedirs(d, exist_ok=True)
    # clear old frames in this tier
    for fn in os.listdir(d):
        if fn.endswith(".png"):
            os.remove(os.path.join(d, fn))
    sc.frame_start = -60
    sc.frame_end = 150
    sc.render.filepath = d + "petal_"
    bpy.ops.render.render(animation=True)
    # drop warm-up frames (<=0), keep petal_0001..0150
    for fn in os.listdir(d):
        if fn.startswith("petal_-") or fn == "petal_0000.png":
            os.remove(os.path.join(d, fn))
    print("tier %d (count=%d) done" % (idx, cnt))

# restore
ps.count = 2500
sc.render.film_transparent = film_prev
sc.render.image_settings.color_mode = 'RGB'
for name, h in saved.items():
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = h
print("PETAL TIERS DONE")
