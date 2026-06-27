import bpy
path = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/cherry_blossom.blend"
bpy.ops.wm.save_as_mainfile(filepath=path)
print("SAVED ->", path)
