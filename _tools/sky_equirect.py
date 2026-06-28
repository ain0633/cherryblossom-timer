import bpy, os, math
ASSETS = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/assets/"
sc = bpy.context.scene

# --- equirectangular panoramic camera at viewer height inside the SkyDome ---
cam = bpy.data.objects.get("EquiCam")
if not cam:
    cd = bpy.data.cameras.new("EquiCam"); cam = bpy.data.objects.new("EquiCam", cd)
    bpy.context.collection.objects.link(cam)
cam.data.type = 'PANO'
bpy.context.scene.render.engine = 'CYCLES'   # cycles must be active before setting pano type
if hasattr(cam.data, 'panorama_type'):
    cam.data.panorama_type = 'EQUIRECTANGULAR'
    print("pano via core ->", cam.data.panorama_type)
elif hasattr(cam.data, 'cycles'):
    cam.data.cycles.panorama_type = 'EQUIRECTANGULAR'
    print("pano via cycles ->", cam.data.cycles.panorama_type)
else:
    print("!! could not set panorama_type")
cam.location = (0.0, 0.0, 6.0)
cam.rotation_euler = (math.radians(90), 0.0, 0.0)   # world +Z -> image up
prev_cam = sc.camera
sc.camera = cam

# --- isolate the sky (hide every other mesh) ---
hidden = []
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name != 'SkyDome':
        hidden.append((o, o.hide_render)); o.hide_render = True

prev = dict(engine=sc.render.engine, rx=sc.render.resolution_x, ry=sc.render.resolution_y,
            fp=sc.render.filepath, ft=sc.render.film_transparent,
            vt=sc.view_settings.view_transform, ex=sc.view_settings.exposure)
sc.render.engine = 'CYCLES'
try:
    sc.cycles.samples = 16; sc.cycles.use_denoising = False
except Exception:
    pass
sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = 0.3
sc.render.film_transparent = False
sc.render.resolution_x = 2048; sc.render.resolution_y = 1024
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92
out = ASSETS + "sky.jpg"
sc.render.filepath = out
bpy.ops.render.render(write_still=True)

# --- restore ---
for o, h in hidden:
    o.hide_render = h
sc.render.engine = prev['engine']; sc.render.resolution_x = prev['rx']; sc.render.resolution_y = prev['ry']
sc.render.filepath = prev['fp']; sc.render.film_transparent = prev['ft']
sc.view_settings.view_transform = prev['vt']; sc.view_settings.exposure = prev['ex']
sc.camera = prev_cam
print("SKY EQUIRECT DONE ->", out, os.path.getsize(out) if os.path.exists(out) else "MISSING")
