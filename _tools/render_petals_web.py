import bpy, os

OUT = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/petals_seq/"
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene

# hide everything except the airborne petals -> petals on transparent bg, same camera
HIDE_PREFIX = ("Trunk", "Cluster", "BEmit", "GroundCarpet", "FarTree", "SkyDome", "Ground")
saved = {}
for o in bpy.data.objects:
    if o.name.startswith(HIDE_PREFIX):
        saved[o.name] = o.hide_render
        o.hide_render = True
# keep PetalEmitter + WindPetal visible
for nm in ("PetalEmitter", "WindPetal"):
    o = bpy.data.objects.get(nm)
    if o:
        saved[nm] = o.hide_render
        o.hide_render = False

film_prev = sc.render.film_transparent
sc.render.film_transparent = True
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x = 800
sc.render.resolution_y = 800
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
sc.frame_start = 1
sc.frame_end = 96
sc.render.filepath = OUT + "petal_"
bpy.ops.render.render(animation=True)

# restore
sc.render.film_transparent = film_prev
sc.render.image_settings.color_mode = 'RGB'
for name, h in saved.items():
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = h
print("PETAL ALPHA SEQ DONE -> 1..96")
