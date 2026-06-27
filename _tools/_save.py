import bpy
p=r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/cherry_blossom_v2.blend"
bpy.ops.wm.save_as_mainfile(filepath=p)
tri=sum(len(o.data.polygons) for o in bpy.data.objects if o.type=='MESH' and o.name in ('Trunk','Blossoms'))
print("SAVED", p, "base_faces(Trunk+Blossoms)=", tri)
