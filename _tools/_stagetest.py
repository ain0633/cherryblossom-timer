import bpy, os
CARDS = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/newtree_cards.py"
exec(compile("AUTO_BUILD=False\n"+open(CARDS,encoding="utf-8").read(), CARDS, 'exec'), globals())
build_blossoms(0.5)
build_carpet(0.5)
sc=bpy.context.scene
sc.render.engine='BLENDER_EEVEE'
sc.render.resolution_x=1600; sc.render.resolution_y=900
sc.render.image_settings.file_format='PNG'
sc.render.filepath=r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/renders/stage_test.png"
bpy.ops.render.render(write_still=True)
print("STAGE TEST DONE")
