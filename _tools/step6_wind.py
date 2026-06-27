import bpy, os, math
from mathutils import Matrix

LIB = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/petal_lib.py"
exec(compile(open(LIB, encoding="utf-8").read(), LIB, "exec"), globals())

SIZE = 0.10   # ~half of previous
blossom_mat = bpy.data.materials.get("BlossomMat") or blossom_material()

# cleanup previous wind rig + the static step5 petal layers (now dynamic)
for nm in ("WindPetal", "PetalEmitter", "WindF", "TurbF", "DragF", "GroundGust", "FallingPetals", "GroundPetals"):
    o = bpy.data.objects.get(nm)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)

# --- single petal instance object ---
vs, faces, cols = petal_geom(Matrix.Identity(4), (1.0, 0.85, 0.92))
pm = bpy.data.meshes.new("WindPetal"); pm.from_pydata([list(v) for v in vs], [], faces); pm.update()
for p in pm.polygons:
    p.use_smooth = True
ca = pm.color_attributes.new("Col", 'BYTE_COLOR', 'POINT')
for i, c in enumerate(cols):
    ca.data[i].color = c
petal = bpy.data.objects.new("WindPetal", pm)
bpy.context.collection.objects.link(petal)
petal.data.materials.append(blossom_mat)
petal.location = (0, 0, 0)

# --- emitter: plane matching the canopy footprint (petals fall only under the tree) ---
bpy.ops.mesh.primitive_grid_add(x_subdivisions=24, y_subdivisions=24, size=13.0, location=(0, 0, 7.5))
emit = bpy.context.active_object; emit.name = "PetalEmitter"   # ±6.5 ~ canopy width
emit.show_instancer_for_render = False
emit.show_instancer_for_viewport = False

# --- force fields: gentle breeze (no gusts) ---
bpy.ops.object.effector_add(type='WIND', location=(-8, 0, 4))
windf = bpy.context.active_object; windf.name = "WindF"
windf.rotation_euler = (0, math.radians(90), 0)   # barely any lateral push
windf.field.strength = 0.04                        # near-zero -> petals fall straight under the tree
windf.field.flow = 0.2

bpy.ops.object.effector_add(type='TURBULENCE', location=(0, 0, 4))
turbf = bpy.context.active_object; turbf.name = "TurbF"
turbf.field.strength = 0.22     # gentle sway only, not lateral drift
turbf.field.size = 1.6

bpy.ops.object.effector_add(type='DRAG', location=(0, 0, 4))
dragf = bpy.context.active_object; dragf.name = "DragF"
dragf.field.linear_drag = 0.12  # low drag so petals actually reach the ground
dragf.field.quadratic_drag = 0.04

# ground-level gentle breeze that intermittently re-lofts settled petals (no gusts)
import random as _r
ADD_GUST = False   # ground re-loft breeze; off until falling/accumulation is verified
if ADD_GUST:
    bpy.ops.object.effector_add(type='TURBULENCE', location=(0, 0, 0.15))
    gust = bpy.context.active_object; gust.name = "GroundGust"
    gust.field.size = 1.0
    gust.field.use_max_distance = True
    gust.field.distance_max = 1.0
    _r.seed(3)
    for _f in range(1, 201, 12):
        gust.field.strength = _r.uniform(0.03, 0.22)
        gust.field.keyframe_insert(data_path="strength", frame=_f)

# --- particle system on emitter ---
emit.modifiers.new("Petals", "PARTICLE_SYSTEM")
psys = emit.particle_systems[-1]
ps = psys.settings
ps.type = 'EMITTER'
ps.count = 4000
ps.frame_start = -60                     # warm-up so the field is full from frame 1 (seamless loop)
ps.frame_end = 400                       # continuous emission across the whole render range
ps.lifetime = 300
ps.emit_from = 'FACE'
ps.use_even_distribution = True
ps.physics_type = 'NEWTON'
ps.mass = 0.1
ps.normal_factor = 0.0
ps.factor_random = 0.15
ps.effector_weights.gravity = 0.80      # steady descent to the ground
ps.render_type = 'OBJECT'
ps.instance_object = petal
ps.particle_size = SIZE
ps.size_random = 0.4
ps.use_rotations = True
ps.rotation_mode = 'VEL'
ps.use_dynamic_rotation = True
ps.angular_velocity_mode = 'RAND'
ps.angular_velocity_factor = 2.0
ps.use_rotation_instance = True

# --- ground collision so petals land & accumulate thinly (not orbit forever) ---
ground = bpy.data.objects.get("Ground")
if ground:
    if not any(m.type == 'COLLISION' for m in ground.modifiers):
        ground.modifiers.new("Collision", "COLLISION")
    ground.collision.damping_factor = 1.0
    ground.collision.friction_factor = 1.0
    ground.collision.use_particle_kill = False

# --- test render at a mid frame (canopy hidden for speed) ---
hidden = []
for o in bpy.data.objects:
    if o.name.startswith("Cluster"):
        hidden.append((o, o.hide_render)); o.hide_render = True

sc = bpy.context.scene
sc.frame_start = 1; sc.frame_end = 110
sc.frame_set(95)
sc.render.image_settings.file_format = 'PNG'
sc.render.filepath = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/petal_test.png"
os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)

for o, h in hidden:
    o.hide_render = h
print("WIND TEST DONE frame=", sc.frame_current)
