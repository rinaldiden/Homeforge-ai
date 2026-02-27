"""
MURO MISTO ALPI — ITERAZIONE 2
Texture: castle_wall_slates (vincitrice iter1)
Fix: più luminoso, meno contrasto, pietre più grandi, camera più frontale.
Confronto: 3 varianti di parametri per avvicinarsi al riferimento.
"""
import bpy
import os
import math

BASE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.normpath(os.path.join(BASE, "..", "..", "materials", "textures"))
OUT_DIR = os.path.join(BASE, "iterazioni")
os.makedirs(OUT_DIR, exist_ok=True)
hdri_path = os.path.join(TEX_DIR, "alps_field_2k.hdr")

tex = {
    "diff": os.path.join(TEX_DIR, "castle_wall_slates_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "castle_wall_slates_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "castle_wall_slates_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "castle_wall_slates_disp_2k.png"),
    "ao":   os.path.join(TEX_DIR, "castle_wall_slates_ao_2k.jpg"),
}

# 3 parameter variants
VARIANTS = {
    "V1_bright": dict(
        scale=(0.8, 0.8, 0.8),   # Bigger stones
        sat=0.80, val=1.40,       # Much brighter
        contrast=0.15,            # Less contrast (mortar not so black)
        nstr=2.0, bstr=0.5, bdist=0.02,
        disp_scale=0.04, disp_mid=0.5,
    ),
    "V2_warm": dict(
        scale=(0.8, 0.8, 0.8),   # Bigger stones
        sat=0.88, val=1.30,       # Warmer, moderate bright
        contrast=0.18,            # Moderate contrast
        nstr=2.2, bstr=0.6, bdist=0.03,
        disp_scale=0.045, disp_mid=0.45,
    ),
    "V3_deep": dict(
        scale=(0.7, 0.7, 0.7),   # Even bigger stones
        sat=0.85, val=1.25,       # Balanced
        contrast=0.20,            # Strong contrast for deep shadows
        nstr=2.5, bstr=0.7, bdist=0.03,
        disp_scale=0.05, disp_mid=0.45,  # Stronger displacement
    ),
}


def make_pbr_displaced(name, tex, scale, sat, val, contrast, nstr, bstr, bdist,
                       disp_scale, disp_mid):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1000, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (600, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-1400, 0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1200, 0)
    mp.inputs["Scale"].default_value = scale
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])

    def tx(label, path, cs, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.label = label; n.location = loc
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = cs
        n.projection = 'BOX'; n.projection_blend = 0.3
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n

    # Color chain: Diff * AO → BrightContrast → HSV → Base Color
    td = tx("Diff", tex["diff"], "sRGB", (-800, 400))
    ta = tx("AO", tex["ao"], "Non-Color", (-800, 200))

    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
    mx.location = (-400, 300); mx.inputs["Factor"].default_value = 0.85  # Lighter AO
    nt.links.new(td.outputs["Color"], mx.inputs[6])
    nt.links.new(ta.outputs["Color"], mx.inputs[7])

    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location = (-200, 300)
    bc.inputs["Contrast"].default_value = contrast
    bc.inputs["Bright"].default_value = 0.02  # Slight brightness boost
    nt.links.new(mx.outputs[2], bc.inputs["Color"])

    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location = (0, 300)
    hsv.inputs["Saturation"].default_value = sat
    hsv.inputs["Value"].default_value = val
    nt.links.new(bc.outputs["Color"], hsv.inputs["Color"])
    nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])

    # Roughness
    tr = tx("Rough", tex["rough"], "Non-Color", (-800, -50))
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    # Normal + Bump micro
    tn = tx("Nor", tex["nor"], "Non-Color", (-800, -250))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-400, -250)
    nm.inputs["Strength"].default_value = nstr
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    tdi = tx("Disp", tex["disp"], "Non-Color", (-800, -450))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location = (-200, -400)
    bmp.inputs["Strength"].default_value = bstr
    bmp.inputs["Distance"].default_value = bdist
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])
    nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])

    # TRUE displacement
    disp_node = nt.nodes.new("ShaderNodeDisplacement"); disp_node.location = (600, -300)
    disp_node.inputs["Scale"].default_value = disp_scale
    disp_node.inputs["Midlevel"].default_value = disp_mid
    nt.links.new(tdi.outputs["Color"], disp_node.inputs["Height"])
    nt.links.new(disp_node.outputs["Displacement"], out.inputs["Displacement"])

    mat.displacement_method = 'BOTH'
    return mat


for vname, params in VARIANTS.items():
    print(f"\n{'='*60}")
    print(f"Rendering: {vname}")
    print(f"{'='*60}")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # HDRI — brighter, lateral sun for mortar shadows
    world = bpy.data.worlds.new("World"); scene.world = world
    world.use_nodes = True
    wnt = world.node_tree; wnt.nodes.clear()
    bg = wnt.nodes.new("ShaderNodeBackground")
    env = wnt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(hdri_path)
    mpw = wnt.nodes.new("ShaderNodeMapping")
    tcw = wnt.nodes.new("ShaderNodeTexCoord")
    outw = wnt.nodes.new("ShaderNodeOutputWorld")
    bg.inputs["Strength"].default_value = 2.8  # Brighter HDRI
    mpw.inputs["Rotation"].default_value = (0, 0, math.radians(35))  # Strong side light
    wnt.links.new(tcw.outputs["Generated"], mpw.inputs["Vector"])
    wnt.links.new(mpw.outputs["Vector"], env.inputs["Vector"])
    wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
    wnt.links.new(bg.outputs["Background"], outw.inputs["Surface"])

    # Ground
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    gnd = bpy.context.active_object
    mg = bpy.data.materials.new("Ground"); mg.use_nodes = True
    mg.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.06, 0.08, 0.04, 1)
    mg.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95
    gnd.data.materials.append(mg)

    # Wall with displacement
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.25))
    wall = bpy.context.active_object; wall.name = "Wall"
    wall.scale = (4.0, 0.45, 2.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    subsurf = wall.modifiers.new("SubSurf", 'SUBSURF')
    subsurf.subdivision_type = 'SIMPLE'
    subsurf.levels = 0
    subsurf.render_levels = 6

    mat = make_pbr_displaced(f"MistoAlpi_{vname}", tex, **params)
    wall.data.materials.append(mat)

    # Camera — more frontal, closer, showing texture detail
    cam_data = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (1.2, -4.5, 1.5)  # Closer, more centered
    cam_obj.rotation_euler = (math.radians(80), 0, math.radians(8))  # More frontal
    cam_data.lens = 35

    # Render
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

    out_path = os.path.join(OUT_DIR, f"misto_alpi_iter2_{vname}.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"SAVED: {out_path}")

print("\n=== MISTO ALPI ITER 2 — 3 variants DONE ===")
