import bpy


def dump_nodes(nt, label):
    print("====", label, "====")
    for n in nt.nodes:
        line = "  " + n.type + " '" + n.name + "'"
        for inp in n.inputs:
            try:
                v = inp.default_value
                if hasattr(v, '__len__') and len(v) in (3, 4):
                    line += " | %s=(%.3f,%.3f,%.3f)" % (inp.name, v[0], v[1], v[2])
                elif isinstance(v, float):
                    line += " | %s=%.3f" % (inp.name, v)
            except Exception:
                pass
        if n.type == 'VALTORGB':
            for e in n.color_ramp.elements:
                c = e.color
                line += " | ramp[%.2f]=(%.3f,%.3f,%.3f)" % (e.position, c[0], c[1], c[2])
        print(line)


def dump_obj(name):
    o = bpy.data.objects.get(name)
    print("########", name)
    if not o:
        print("  (missing)"); return
    for m in o.data.materials:
        if m and m.use_nodes:
            dump_nodes(m.node_tree, m.name)
        else:
            print("  mat:", m.name if m else None)


for nm in ["SkyDome", "Ground", "FarTree0_trunk", "FarTree0_c0", "FarTree1_c0", "FarTree2_c0", "FarTree3_c0"]:
    dump_obj(nm)

# distinct canopy materials across all FarTrees
cm = {}
for o in bpy.data.objects:
    if o.name.startswith("FarTree") and "_c" in o.name:
        for m in o.data.materials:
            cm[m.name if m else None] = cm.get(m.name if m else None, 0) + 1
print("######## FarTree canopy material counts:", cm)

# world background
w = bpy.context.scene.world
if w and w.use_nodes:
    dump_nodes(w.node_tree, "WORLD")
print("######## view_transform:", bpy.context.scene.view_settings.view_transform,
      "exposure:", round(bpy.context.scene.view_settings.exposure, 3))
