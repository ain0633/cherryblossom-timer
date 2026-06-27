import bpy, os

CARDS = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/_tools/newtree_cards.py"
exec(compile("AUTO_BUILD=False\n" + open(CARDS, encoding="utf-8").read(), CARDS, 'exec'), globals())

OUT = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/stages"
os.makedirs(OUT, exist_ok=True)

sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = 0.3
sc.render.resolution_x = 1600; sc.render.resolution_y = 900
sc.render.film_transparent = False
sc.render.image_settings.file_format = 'JPEG'
sc.render.image_settings.quality = 90

N = 20
for i in range(N):
    bloom = 1.0 - i / (N - 1)            # stage_00 = full bloom, stage_19 = bare
    build_blossoms(bloom)
    build_carpet(1.0 - bloom)            # accumulation grows as bloom falls
    sc.render.filepath = os.path.join(OUT, "stage_%02d" % i)
    bpy.ops.render.render(write_still=True)
    print("STAGE %02d bloom=%.3f done" % (i, bloom))

print("ALL STAGES DONE ->", OUT)
