import bpy, statistics as st
sc=bpy.context.scene
emit=bpy.data.objects.get("PetalEmitter")
dg=bpy.context.evaluated_depsgraph_get()
sc.frame_set(1)
psys=emit.evaluated_get(dg).particle_systems[0]
zs=[p.location.z for p in psys.particles if p.alive_state=='ALIVE']
print("alive=",len(zs))
if zs:
    print("zmin=%.2f zmax=%.2f zmean=%.2f"%(min(zs),max(zs),st.mean(zs)))
    for lo,hi in [(-2,0),(0,2),(2,4),(4,6),(6,8),(8,10),(10,13)]:
        c=sum(1 for z in zs if lo<=z<hi)
        print("z[%2d,%2d): %5d %s"%(lo,hi,c,'#'*int(c/40)))
