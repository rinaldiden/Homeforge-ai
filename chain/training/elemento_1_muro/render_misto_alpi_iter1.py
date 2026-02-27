"""
MURO MISTO ALPI — ITERAZIONE 1
Confronto 4 texture con TRUE DISPLACEMENT (non solo bump).
Obiettivo: trovare la texture base che più si avvicina al riferimento pietraeco.it
Riferimento: pietre miste scisto, giunti profondi scuri, rilievo 3D forte.
"""
import bpy
import os
import math

BASE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.normpath(os.path.join(BASE, "..", "..", "materials", "textures"))
OUT_DIR = os.path.join(BASE, "iterazioni")
os.makedirs(OUT_DIR, exist_ok=True)
hdri_path = os.path.join(TEX_DIR, "alps_field_2k.hdr")

# 4 candidate textures
CANDIDATES = {
    "A_castle_wall_slates": {
        "diff": os.path.join(TEX_DIR, "castle_wall_slates_diff_2k.jpg"),
        "nor":  os.path.join(TEX_DIR, "castle_wall_slates_nor_gl_2k.jpg"),
        "rough": os.path.join(TEX_DIR, "castle_wall_slates_rough_2k.jpg"),
        "disp": os.path.join(TEX_DIR, "castle_wall_slates_disp_2k.png"),
        "ao":   os.path.join(TEX_DIR, "castle_wall_slates_ao_2k.jpg"),
    },
    "B_broken_wall": {
        "diff": os.path.join(TEX_DIR, "broken_wall_diff_2k.jpg"),
        "nor":  os.path.join(TEX_DIR, "broken_wall_nor_gl_2k.jpg"),
        "rough": os.path.join(TEX_DIR, "broken_wall_rough_2k.jpg"),
        "disp": os.path.join(TEX_DIR, "broken_wall_disp_2k.png"),
        "ao":   os.path.join(TEX_DIR, "broken_wall_ao_2k.jpg"),
    },
    "C_stacked_stone_wall": {
        "diff": os.path.join(TEX_DIR, "stacked_stone_wall_diff_2k.jpg"),
        "nor":  os.path.join(TEX_DIR, "stacked_stone_wall_nor_gl_2k.jpg"),
        "rough": os.path.join(TEX_DIR, "stacked_stone_wall_rough_2k.jpg"),
        "disp": os.path.join(TEX_DIR, "stacked_stone_wall_disp_2k.png"),
        "ao":   os.path.join(TEX_DIR, "stacked_stone_wall_ao_2k.jpg"),
    },
    "D_rock_wall_08": {
        "diff": os.path.join(TEX_DIR, "rock_wall_08_diff_2k.jpg"),
        "nor":  os.path.join(TEX_DIR, "rock_wall_08_nor_gl_2k.jpg"),
        "rough": os.path.join(TEX_DIR, "rock_wall_08_rough_2k.jpg"),
        "disp": os.path.join(TEX_DIR, "rock_wall_08_disp_2k.png"),
        "ao":   os.path.join(TEX_DIR, "rock_wall_08_ao_2k.jpg"),
    },
}


def make_pbr_displaced(name, tex, scale=(1.2, 1.2, 1.2), sat=0.82, val=1.15,
                       contrast=0.20, nstr=2.5, bstr=0.9, bdist=0.04,
                       disp_scale=0.035, disp_mid=0.5):
    """
    PBR material con TRUE DISPLACEMENT + bump per micro-detail.
    disp_scale: scala displacement reale in metri (0.035 = 3.5cm di rilievo).
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    # Output
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (1000, 0)

    # Principled BSDF
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (600, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Texture Coordinates + Mapping
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1400, 0)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.location = (-1200, 0)
    mp.inputs["Scale"].default_value = scale
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])

    def tx(label, path, cs, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.label = label
        n.location = loc
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = cs
        n.projection = 'BOX'
        n.projection_blend = 0.3
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n

    # --- COLOR CHAIN: Diff * AO → BrightContrast → HSV → Base Color ---
    td = tx("Diff", tex["diff"], "sRGB", (-800, 400))
    ta = tx("AO", tex["ao"], "Non-Color", (-800, 200))

    # AO multiply
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = 'RGBA'
    mx.blend_type = 'MULTIPLY'
    mx.location = (-400, 300)
    mx.inputs["Factor"].default_value = 1.0
    nt.links.new(td.outputs["Color"], mx.inputs[6])
    nt.links.new(ta.outputs["Color"], mx.inputs[7])

    # Brightness/Contrast — stronger for deep mortar shadow
    bc = nt.nodes.new("ShaderNodeBrightContrast")
    bc.location = (-200, 300)
    bc.inputs["Contrast"].default_value = contrast
    bc.inputs["Bright"].default_value = -0.05  # Slightly darker overall
    nt.links.new(mx.outputs[2], bc.inputs["Color"])

    # HSV
    hsv = nt.nodes.new("ShaderNodeHueSaturation")
    hsv.location = (0, 300)
    hsv.inputs["Saturation"].default_value = sat
    hsv.inputs["Value"].default_value = val
    nt.links.new(bc.outputs["Color"], hsv.inputs["Color"])
    nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])

    # --- ROUGHNESS ---
    tr = tx("Rough", tex["rough"], "Non-Color", (-800, -50))
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    # --- NORMAL MAP → BUMP (for micro-detail on top of displacement) ---
    tn = tx("Nor", tex["nor"], "Non-Color", (-800, -250))
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nm.location = (-400, -250)
    nm.inputs["Strength"].default_value = nstr
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    # Displacement texture (shared with true displacement)
    tdi = tx("Disp", tex["disp"], "Non-Color", (-800, -450))

    # Bump for micro-detail (fine surface grain)
    bmp = nt.nodes.new("ShaderNodeBump")
    bmp.location = (-200, -400)
    bmp.inputs["Strength"].default_value = bstr
    bmp.inputs["Distance"].default_value = bdist
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])
    nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])

    # --- TRUE DISPLACEMENT → Material Output ---
    disp_node = nt.nodes.new("ShaderNodeDisplacement")
    disp_node.location = (600, -300)
    disp_node.inputs["Scale"].default_value = disp_scale
    disp_node.inputs["Midlevel"].default_value = disp_mid
    nt.links.new(tdi.outputs["Color"], disp_node.inputs["Height"])
    nt.links.new(disp_node.outputs["Displacement"], out.inputs["Displacement"])

    # Enable true displacement + bump
    mat.displacement_method = 'BOTH'

    return mat


for cname, tex in CANDIDATES.items():
    print(f"\n{'='*60}")
    print(f"Rendering: {cname}")
    print(f"{'='*60}")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # HDRI
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    wnt = world.node_tree
    wnt.nodes.clear()
    bg = wnt.nodes.new("ShaderNodeBackground")
    env = wnt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(hdri_path)
    mpw = wnt.nodes.new("ShaderNodeMapping")
    tcw = wnt.nodes.new("ShaderNodeTexCoord")
    outw = wnt.nodes.new("ShaderNodeOutputWorld")
    bg.inputs["Strength"].default_value = 2.2
    mpw.inputs["Rotation"].default_value = (0, 0, math.radians(50))
    wnt.links.new(tcw.outputs["Generated"], mpw.inputs["Vector"])
    wnt.links.new(mpw.outputs["Vector"], env.inputs["Vector"])
    wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
    wnt.links.new(bg.outputs["Background"], outw.inputs["Surface"])

    # Ground
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    gnd = bpy.context.active_object
    mg = bpy.data.materials.new("Ground")
    mg.use_nodes = True
    mg.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.06, 0.08, 0.04, 1)
    mg.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95
    gnd.data.materials.append(mg)

    # --- WALL with TRUE DISPLACEMENT ---
    # Cube 4m x 0.45m x 2.5m (classic alpine wall dimensions)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.25))
    wall = bpy.context.active_object
    wall.name = "Wall"
    wall.scale = (4.0, 0.45, 2.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Subdivision for displacement geometry
    subsurf = wall.modifiers.new("SubSurf", 'SUBSURF')
    subsurf.subdivision_type = 'SIMPLE'  # No smoothing, just subdivide
    subsurf.levels = 0          # Viewport: none
    subsurf.render_levels = 6   # Render: 6 levels = ~24K faces per original face

    # Material
    mat = make_pbr_displaced(f"MistoAlpi_{cname}", tex,
        scale=(1.0, 1.0, 1.0),    # 1:1 scale for now
        sat=0.80,                   # Slightly desaturated (alpine grey)
        val=1.10,                   # Moderate brightness
        contrast=0.22,              # Strong contrast for mortar shadows
        nstr=2.5,                   # Strong normal map
        bstr=0.5,                   # Moderate bump on top of displacement
        bdist=0.02,
        disp_scale=0.04,           # 4cm displacement depth
        disp_mid=0.5,
    )
    wall.data.materials.append(mat)

    # Camera — 3/4 view, medium distance, showing wall face
    cam_data = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (2.5, -5.0, 1.8)
    cam_obj.rotation_euler = (math.radians(78), 0, math.radians(12))
    cam_data.lens = 35

    # Render settings — 128 samples for fast comparison
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'AgX'
    try:
        scene.view_settings.look = 'AgX - Medium Contrast'
    except:
        scene.view_settings.look = 'AgX - Base Contrast'

    out_path = os.path.join(OUT_DIR, f"misto_alpi_iter1_{cname}.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"SAVED: {out_path}")

print("\n=== MISTO ALPI ITER 1 — 4 candidate comparison DONE ===")
