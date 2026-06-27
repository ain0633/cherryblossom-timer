import bpy, os, math
from mathutils import Matrix, Vector

LIB = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/petal_lib.py"
exec(compile(open(LIB, encoding="utf-8").read(), LIB, "exec"), globals())

# --- build a single real sakura petal, centered at origin, lying in XY (faces +Z) ---
old = bpy.data.objects.get("PetalSprite")
if old: bpy.data.objects.remove(old, do_unlink=True)
vs, faces, cols = petal_geom(Matrix.Identity(4), (1.0, 1.0, 1.0))
me = bpy.data.meshes.new("PetalSprite"); me.from_pydata([list(v) for v in vs], [], faces); me.update()
for p in me.polygons: p.use_smooth = True
ca = me.color_attributes.new("Col", 'BYTE_COLOR', 'POINT')
for i, c in enumerate(cols): ca.data[i].color = c
obj = bpy.data.objects.new("PetalSprite", me)
bpy.context.collection.objects.link(obj)
obj.data.materials.append(blossom_material())
obj.location = (0.0, -0.48, 0.0)        # centroid (~y0.48) -> world origin
sub = obj.modifiers.new("Subsurf", "SUBSURF"); sub.levels = 2; sub.render_levels = 2  # smooth silhouette
# face-on & centered (tumbling dimension comes from the R3F 3D rotation)

# --- dedicated ortho camera straight-on (+Z) so we get the flat petal silhouette ---
scam = bpy.data.objects.get("SpriteCam")
if not scam:
    cd = bpy.data.cameras.new("SpriteCam"); scam = bpy.data.objects.new("SpriteCam", cd)
    bpy.context.collection.objects.link(scam)
scam.data.type = 'ORTHO'; scam.data.ortho_scale = 1.9
scam.location = (0.0, 0.0, 5.0)
scam.rotation_euler = (0.0, 0.0, 0.0)   # look down -Z
prev_cam = bpy.context.scene.camera
bpy.context.scene.camera = scam

# --- soft front light + fill so the petal reads bright & slightly translucent ---
sun = bpy.data.objects.get("SpriteSun")
if not sun:
    l = bpy.data.lights.new("SpriteSun", "SUN"); sun = bpy.data.objects.new("SpriteSun", l)
    bpy.context.collection.objects.link(sun)
sun.data.energy = 1.5; sun.data.color = (1.0, 0.97, 0.96)
sun.rotation_euler = (math.radians(28), math.radians(-16), 0)
world = bpy.context.scene.world
prev_w = world.node_tree.nodes.get("Background").inputs[1].default_value
world.node_tree.nodes.get("Background").inputs[1].default_value = 0.55  # soft fill (keep pink)

# --- transparent render ---
sc = bpy.context.scene
prev = dict(ft=sc.render.film_transparent, rx=sc.render.resolution_x, ry=sc.render.resolution_y,
            fp=sc.render.filepath, cm=sc.render.image_settings.color_mode, exp=sc.view_settings.exposure)
sc.render.engine = 'BLENDER_EEVEE'
sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = -0.1
sc.render.film_transparent = True
sc.render.resolution_x = 512; sc.render.resolution_y = 512
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
out = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/petals/petal.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
sc.render.filepath = out
# isolate: hide everything except the petal so only it renders (transparent bg)
hidden = []
for o in bpy.data.objects:
    if o.name != "PetalSprite" and o.type in {'MESH'}:
        hidden.append((o, o.hide_render)); o.hide_render = True
bpy.ops.render.render(write_still=True)
for o, h in hidden: o.hide_render = h

# --- restore scene so later tree renders are unaffected ---
sc.render.film_transparent = prev['ft']; sc.render.resolution_x = prev['rx']; sc.render.resolution_y = prev['ry']
sc.render.filepath = prev['fp']; sc.render.image_settings.color_mode = prev['cm']; sc.view_settings.exposure = prev['exp']
world.node_tree.nodes.get("Background").inputs[1].default_value = prev_w
bpy.context.scene.camera = prev_cam
print("PETAL SPRITE DONE ->", out)
