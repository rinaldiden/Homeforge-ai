"""
ELEMENTO 2 — Tetto Piode — ITERAZIONE 1
Confronto 3 texture: A=roof_slates_02, B=roof_slates_03, C=castle_wall_slates
Setup: superficie tetto 4x3m inclinata 30°, spessore bordo 5cm, HDRI
"""
import bpy
import os
import math

BASE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.normpath(os.path.join(BASE, "..", "..", "materials", "textures"))
OUT_DIR = os.path.join(BASE, "iterazioni")
os.makedirs(OUT_DIR, exist_ok=True)
hdri_path = os.path.join(TEX_DIR, "alps_field_2k.hdr")

TEXTURES = {
    "A_roof_slates_02": {
        "diff": os.path.join(TEX_DIR, "roof_slates_02_diff_2k.jpg"),
        "nor":  os.path.join(TEX_DIR, "roof_slates_02_nor_gl_2k.jpg"),
        "rough": os.path.join(TEX_DIR, "roof_slates_02_rough_2k.jpg"),
        "disp": os.path.join(TEX_DIR, "roof_slates_02_disp_2k.png"),
        "ao":   os.path.join(TEX_DIR, "roof_slates_02_ao_2k.jpg"),
    },
    "B_roof_slates_03": {
        "diff": os.path.join(TEX_DIR, "roof_slates_03_diff_2k.jpg"),
        "nor":  os.path.join(TEX_DIR, "roof_slates_03_nor_gl_2k.jpg"),
        "rough": os.path.join(TEX_DIR, "roof_slates_03_rough_2k.jpg"),
        "disp": os.path.join(TEX_DIR, "roof_slates_03_disp_2k.png"),
        "ao":   os.path.join(TEX_DIR, "roof_slates_03_ao_2k.jpg"),
    },
    "C_castle_wall_slates": {
        "diff": os.path.join(TEX_DIR, "castle_wall_slates_diff_2k.jpg"),
        "nor":  os.path.join(TEX_DIR, "castle_wall_slates_nor_gl_2k.jpg"),
        "rough": os.path.join(TEX_DIR, "castle_wall_slates_rough_2k.jpg"),
        "disp": os.path.join(TEX_DIR, "castle_wall_slates_disp_2k.png"),
        "ao":   os.path.join(TEX_DIR, "castle_wall_slates_ao_2k.jpg"),
    },
}

for name, t in TEXTURES.items():
    for k, p in t.items():
        assert os.path.exists(p), f"Missing: {name}/{k}: {p}"
assert os.path.exists(hdri_path)


def setup_scene():
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
    mp_w = wnt.nodes.new("ShaderNodeMapping")
    tc_w = wnt.nodes.new("ShaderNodeTexCoord")
    out_w = wnt.nodes.new("ShaderNodeOutputWorld")
    bg.inputs["Strength"].default_value = 1.8
    mp_w.inputs["Rotation"].default_value = (0, 0, math.radians(50))
    wnt.links.new(tc_w.outputs["Generated"], mp_w.inputs["Vector"])
    wnt.links.new(mp_w.outputs["Vector"], env.inputs["Vector"])
    wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
    wnt.links.new(bg.outputs["Background"], out_w.inputs["Surface"])
    # Camera — from below looking up at roof (typical viewing angle)
    cam_data = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (2.0, -5.0, 0.5)
    cam_obj.rotation_euler = (math.radians(68), 0, math.radians(12))
    cam_data.lens = 35
    # Render
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 512
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
    return scene


def create_piode_material(name, tex_files, scale=1.5):
    """PBR material for piode roof slates"""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    node_out = nt.nodes.new("ShaderNodeOutputMaterial")
    node_out.location = (1000, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (600, 0)
    nt.links.new(bsdf.outputs["BSDF"], node_out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1400, 0)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.location = (-1200, 0)
    mp.inputs["Scale"].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])

    def tex_n(label, path, cs, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.label = label
        n.location = loc
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = cs
        n.projection = 'BOX'
        n.projection_blend = 0.2
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n

    # Color
    t_diff = tex_n("Diff", tex_files["diff"], "sRGB", (-800, 400))
    t_ao = tex_n("AO", tex_files["ao"], "Non-Color", (-800, 200))
    mix_ao = nt.nodes.new("ShaderNodeMix")
    mix_ao.data_type = 'RGBA'
    mix_ao.blend_type = 'MULTIPLY'
    mix_ao.location = (-400, 300)
    mix_ao.inputs["Factor"].default_value = 1.0
    nt.links.new(t_diff.outputs["Color"], mix_ao.inputs[6])
    nt.links.new(t_ao.outputs["Color"], mix_ao.inputs[7])

    hsv = nt.nodes.new("ShaderNodeHueSaturation")
    hsv.location = (-200, 300)
    hsv.inputs["Saturation"].default_value = 0.75  # Piode are desaturated grey
    hsv.inputs["Value"].default_value = 1.10
    nt.links.new(mix_ao.outputs[2], hsv.inputs["Color"])
    nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])

    # Roughness
    t_rough = tex_n("Rough", tex_files["rough"], "Non-Color", (-800, -50))
    nt.links.new(t_rough.outputs["Color"], bsdf.inputs["Roughness"])

    # Normal + Bump
    t_nor = tex_n("Normal", tex_files["nor"], "Non-Color", (-800, -250))
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nmap.location = (-400, -250)
    nmap.inputs["Strength"].default_value = 1.5
    nt.links.new(t_nor.outputs["Color"], nmap.inputs["Color"])

    t_disp = tex_n("Disp", tex_files["disp"], "Non-Color", (-800, -450))
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (-200, -400)
    bump.inputs["Strength"].default_value = 0.7
    bump.inputs["Distance"].default_value = 0.04
    nt.links.new(t_disp.outputs["Color"], bump.inputs["Height"])
    nt.links.new(nmap.outputs["Normal"], bump.inputs["Normal"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    mat.displacement_method = 'BUMP'
    return mat


def create_roof_slab(name, material):
    """4x3m roof slab tilted 30°, with 5cm thickness"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 2.5))
    roof = bpy.context.active_object
    roof.name = name
    roof.scale = (4.0, 0.05, 3.0)  # 4m wide, 5cm thick, 3m deep
    roof.rotation_euler = (math.radians(60), 0, 0)  # 30° from horizontal
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    roof.data.materials.append(material)
    return roof


# Render all 3 textures
for tex_name, tex_files in TEXTURES.items():
    print(f"\n{'='*60}")
    print(f"Rendering {tex_name}")
    print(f"{'='*60}")

    scene = setup_scene()
    mat = create_piode_material(f"Piode_{tex_name}", tex_files, scale=1.5)
    roof = create_roof_slab(f"Roof_{tex_name}", mat)

    # Ground
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    gnd = bpy.context.active_object
    mat_gnd = bpy.data.materials.new("Gnd")
    mat_gnd.use_nodes = True
    mat_gnd.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.13, 0.05, 1)
    mat_gnd.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95
    gnd.data.materials.append(mat_gnd)

    out_path = os.path.join(OUT_DIR, f"iter1_{tex_name}.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"SAVED: {out_path}")

print("\n=== ITERAZIONE 1 COMPLETA — 3 texture confrontate ===")
