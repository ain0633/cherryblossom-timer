import bpy
print("CONNECTED", bpy.app.version_string)
print("engine", bpy.context.scene.render.engine)
print("objects", len(bpy.data.objects))
