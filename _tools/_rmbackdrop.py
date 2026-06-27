import bpy
for n in ("Backdrop",):
    o=bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o, do_unlink=True)
print("Backdrop removed; objects=", len(bpy.data.objects))
