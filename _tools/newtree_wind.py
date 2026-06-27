import bpy, os, math
from mathutils import Matrix

# Natural petal fall: petals detach from THROUGHOUT the blossom canopy (not a flat
# disc above the tree) and flutter down with breeze + turbulence + drag.
LIB = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/petal_lib.py"
exec(compile(open(LIB, encoding="utf-8").read(), LIB, "exec"), globals())

SIZE = 0.13
blossom_mat = bpy.data.materials.get("BlossomMat") or blossom_material()

for nm in ("WindPetal", "PetalEmitter", "WindF", "TurbF", "DragF"):
    o = bpy.data.objects.get(nm)
    if o: bpy.data.objects.remove(o, do_unlink=True)

# --- single petal instance object ---
vs, faces, cols = petal_geom(Matrix.Identity(4), (1.0, 0.85, 0.92))
pm = bpy.data.meshes.new("WindPetal"); pm.from_pydata([list(v) for v in vs], [], faces); pm.update()
for p in pm.polygons: p.use_smooth = True
ca = pm.color_attributes.new("Col", 'BYTE_COLOR', 'POINT')
for i, c in enumerate(cols): ca.data[i].color = c
petal = bpy.data.objects.new("WindPetal", pm)
bpy.context.collection.objects.link(petal)
petal.data.materials.append(blossom_mat)
petal.location = (0, 0, 0)

# --- emitter = wide plane INSIDE the canopy (z9) -> petals start among the blossoms and
#     fall down through the visible lower column (not a clump in the sky above the tree) ---
bpy.ops.mesh.primitive_grid_add(x_subdivisions=24, y_subdivisions=24, size=15.0, location=(0, 0, 9.0))
emit = bpy.context.active_object; emit.name = "PetalEmitter"
emit.show_instancer_for_render = False
emit.show_instancer_for_viewport = False

# --- force fields: gentle breeze + swirl + drag -> fluttering zig-zag descent ---
bpy.ops.object.effector_add(type='WIND', location=(-8, 0, 5))
windf = bpy.context.active_object; windf.name = "WindF"
windf.rotation_euler = (0, math.radians(90), 0)
windf.field.strength = 0.06
windf.field.flow = 0.2

bpy.ops.object.effector_add(type='TURBULENCE', location=(0, 0, 6))
turbf = bpy.context.active_object; turbf.name = "TurbF"
turbf.field.strength = 0.28        # gentle flutter (not so strong they hover/clump)
turbf.field.size = 2.0

bpy.ops.object.effector_add(type='DRAG', location=(0, 0, 6))
dragf = bpy.context.active_object; dragf.name = "DragF"
dragf.field.use_max_distance = False
dragf.field.linear_drag = 0.4      # moderate drag -> reach terminal velocity ->
dragf.field.quadratic_drag = 0.1   # steady fall, fairly uniform column z0..9

# --- particle system emitted from the canopy faces ---
emit.modifiers.new("Petals", "PARTICLE_SYSTEM")
ps = emit.particle_systems[-1].settings
ps.type = 'EMITTER'
ps.count = 16000
ps.frame_start = -150              # long warm-up so the WHOLE column (canopy->ground) is full
ps.frame_end = 200                 # high emission rate (count over a short span) -> dense column
ps.lifetime = 200
ps.lifetime_random = 0.3
ps.emit_from = 'FACE'
ps.use_even_distribution = True
ps.use_modifier_stack = True
ps.physics_type = 'NEWTON'
ps.mass = 0.1
ps.normal_factor = 0.0
ps.factor_random = 0.06            # tiny initial drift (detach softly)
ps.effector_weights.gravity = 1.0   # with drag -> steady terminal-velocity descent
ps.render_type = 'OBJECT'
ps.instance_object = petal
ps.particle_size = SIZE
ps.size_random = 0.45
ps.use_rotations = True
ps.rotation_mode = 'VEL'
ps.use_dynamic_rotation = True
ps.angular_velocity_mode = 'RAND'
ps.angular_velocity_factor = 3.0
ps.use_rotation_instance = True

# --- ground collision so petals settle (accumulation handled by stage carpet) ---
ground = bpy.data.objects.get("Ground")
if ground:
    if not any(m.type == 'COLLISION' for m in ground.modifiers):
        ground.modifiers.new("Collision", "COLLISION")
    ground.collision.damping_factor = 1.0
    ground.collision.friction_factor = 1.0
    ground.collision.use_particle_kill = True   # remove on landing; accumulation = stage carpet
                                                 # -> all alive petals are in-transit (dense column)

print("WIND RIG DONE (canopy-emitter, gravity 0.70, kill-on-ground)")
