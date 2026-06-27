import bpy
sc = bpy.context.scene
for f in range(1, 251):           # step the sim live to the end
    sc.frame_set(f)
deps = bpy.context.evaluated_depsgraph_get()
emit = bpy.data.objects.get("PetalEmitter").evaluated_get(deps)
ps = emit.particle_systems[0]
parts = ps.particles
states = {}
zs = []
for p in parts:
    states[p.alive_state] = states.get(p.alive_state, 0) + 1
    if p.alive_state in ('ALIVE', 'DYING'):
        zs.append(p.location.z)
print("total particles:", len(parts))
print("states:", states)
if zs:
    print("alive z  min=%.2f max=%.2f avg=%.2f" % (min(zs), max(zs), sum(zs) / len(zs)))
    print("below ground (z<0.05):", sum(1 for z in zs if z < 0.05))
    print("near ground (0<z<0.3):", sum(1 for z in zs if 0 <= z < 0.3))
g = bpy.data.objects.get("Ground")
print("Ground modifiers:", [m.type for m in g.modifiers] if g else None)
print("Ground scale:", tuple(g.scale) if g else None)
