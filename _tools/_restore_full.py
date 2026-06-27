import bpy
CARDS=r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/newtree_cards.py"
exec(compile("AUTO_BUILD=False\n"+open(CARDS,encoding="utf-8").read(),CARDS,'exec'),globals())
build_blossoms(1.0)
c=bpy.data.objects.get("GroundCarpet")
if c: bpy.data.objects.remove(c, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/cherry_blossom_v2.blend")
print("RESTORED full canopy + saved")
