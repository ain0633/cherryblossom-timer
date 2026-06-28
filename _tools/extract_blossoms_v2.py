import bpy, json, math, random
random.seed(11)
ASSETS = r"C:/Users/ain06/OneDrive/문서/2026/코드_프로젝트/Cherry Blossom Timer/web/public/assets/"

# light/outer -> deep/inner pink tints
GROUP_COLOR = [(0.97, 0.86, 0.91), (0.96, 0.83, 0.89),
               (0.95, 0.72, 0.82), (0.95, 0.69, 0.80),
               (0.93, 0.58, 0.71), (0.92, 0.55, 0.69)]

ob = bpy.data.objects["Blossoms"]
me = ob.data
mw = ob.matrix_world

# exact canopy: use the real card (polygon) centers from the v2 Blossoms mesh
pts = [mw @ poly.center for poly in me.polygons]
random.shuffle(pts)
TARGET = 20000
pts = pts[:TARGET]
print("Blossoms polys:", len(me.polygons), "-> sampled", len(pts))

xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
zmin, zmax = min(zs), max(zs)
R = max(math.hypot(p.x - cx, p.y - cy) for p in pts) or 1.0

positions = []; colors = []
for p in pts:
    hf = (p.z - zmin) / max(0.01, zmax - zmin)
    of = math.hypot(p.x - cx, p.y - cy) / R
    score = 0.6 * hf + 0.4 * of
    base = 0 if score > 0.66 else (2 if score > 0.40 else 4)
    gi = base + random.randint(0, 1)
    positions.append([round(p.x, 3), round(p.z, 3), round(-p.y, 3)])  # Z-up -> Y-up
    colors.append([round(c, 3) for c in GROUP_COLOR[gi]])

with open(ASSETS + "blossoms.json", "w") as f:
    json.dump({"positions": positions, "colors": colors}, f)
print("blossoms.json (from real cards):", len(positions))
