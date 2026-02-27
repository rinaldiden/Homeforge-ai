"""
ELEMENTO 1 — Muro in pietra — ITERAZIONE 1
Obiettivo: confronto texture A (rock_wall_08) vs B (stone_wall)
Setup: muro 3x2m, camera frontale ravvicinata, HDRI alps_field, Cycles 512
Criteri: profondità giunti, colore realistico, variazione pietre, ombre naturali
"""
import bpy
import os
import math

BASE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.join(os.path.dirname(BASE), "..", "materials", "textures")
TEX_DIR = os.path.normpath(TEX_DIR)
OUT_DIR = os.path.join(BASE, "iterazioni")
os.makedirs(OUT_DIR, exist_ok=True)

hdri_path = os.path.join(TEX_DIR, "alps_field_2k.hdr")

TEXTURES = {
    "A_rock_wall_08": {
        "diff": os.path.join(TEX_DIR, "rock_wall_08_diff_2k.jpg"),
        "nor":  os.path.join(TEX_DIR, "rock_wall_08_nor_gl_2k.jpg"),
        "rough": os.path.join(TEX_DIR, "rock_wall_08_rough_2k.jpg"),
        "disp": os.path.join(TEX_DIR, "rock_wall_08_disp_2k.png"),
        "ao":   os.path.join(TEX_DIR, "rock_wall_08_ao_2k.jpg"),
    },
    "B_stone_wall": {
        "diff": os.path.join(TEX_DIR, "stone_wall_diff_2k.jpg"),
        "nor":  os.path.join(TEX_DIR, "stone_wall_nor_gl_2k.jpg"),
        "rough": os.path.join(TEX_DIR, "stone_wall_rough_2k.jpg"),
        "disp": os.path.join(TEX_DIR, "stone_wall_disp_2k.png"),
        "ao":   os.path.join(TEX_DIR, "stone_wall_ao_2k.jpg"),
    },
}

# Verify all files
for name, tex in TEXTURES.items():
    for k, p in tex.items():
        assert os.path.exists(p), f"Missing: {p}"
assert os.path.exists(hdri_path), f"Missing HDRI: {hdri_path}"
print("All files verified OK")


def setup_scene():
    """Clean scene, setup HDRI, camera, render settings"""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # HDRI
    world = bpy.data.worlds.new("World_HDRI")
    scene.world = world
    world.use_nodes = True
    wnt = world.node_tree
    wnt.nodes.clear()
    bg = wnt.nodes.new("ShaderNodeBackground")
    env = wnt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(hdri_path)
    mapping = wnt.nodes.new("ShaderNodeMapping")
    tc = wnt.nodes.new("ShaderNodeTexCoord")
    out = wnt.nodes.new("ShaderNodeOutputWorld")
    bg.inputs["Strength"].default_value = 2.0
    mapping.inputs["Rotation"].default_value = (0, 0, math.radians(90))
    wnt.links.new(tc.outputs["Generated"], mapping.inputs["Vector"])
    wnt.links.new(mapping.outputs["Vector"], env.inputs["Vector"])
    wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
    wnt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    # Camera — frontale, leggermente angolata per profondità
    cam_data = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0.4, -3.0, 1.0)
    cam_obj.rotation_euler = (math.radians(82), 0, math.radians(5))
    cam_data.lens = 50  # 50mm per ritratto architettonico

    # Render settings
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


def create_pbr_wall_material(name, tex_files, scale=1.5, sat=0.75, val=1.3,
                              normal_str=2.0, bump_str=0.8, bump_dist=0.04,
                              micro_bump_str=0.05):
    """Full PBR material with all 5 maps + micro noise bump"""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    node_out = nt.nodes.new("ShaderNodeOutputMaterial")
    node_out.location = (1000, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (600, 0)
    nt.links.new(bsdf.outputs["BSDF"], node_out.inputs["Surface"])

    # Texture Coordinate → Mapping
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1400, 0)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.location = (-1200, 0)
    mp.inputs["Scale"].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])

    def tex_node(label, path, cs, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.label = label
        n.location = loc
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = cs
        n.projection = 'BOX'
        n.projection_blend = 0.3
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n

    # === COLOR CHAIN ===
    # Diffuse
    t_diff = tex_node("Diffuse", tex_files["diff"], "sRGB", (-800, 400))
    # AO
    t_ao = tex_node("AO", tex_files["ao"], "Non-Color", (-800, 200))
    # Multiply diff * AO
    mix_ao = nt.nodes.new("ShaderNodeMix")
    mix_ao.data_type = 'RGBA'
    mix_ao.blend_type = 'MULTIPLY'
    mix_ao.location = (-400, 300)
    mix_ao.inputs["Factor"].default_value = 1.0
    nt.links.new(t_diff.outputs["Color"], mix_ao.inputs[6])
    nt.links.new(t_ao.outputs["Color"], mix_ao.inputs[7])
    # HSV
    hsv = nt.nodes.new("ShaderNodeHueSaturation")
    hsv.location = (-200, 300)
    hsv.inputs["Saturation"].default_value = sat
    hsv.inputs["Value"].default_value = val
    nt.links.new(mix_ao.outputs[2], hsv.inputs["Color"])
    nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])

    # === ROUGHNESS ===
    t_rough = tex_node("Roughness", tex_files["rough"], "Non-Color", (-800, 0))
    nt.links.new(t_rough.outputs["Color"], bsdf.inputs["Roughness"])

    # === NORMAL CHAIN ===
    # Normal map
    t_nor = tex_node("Normal", tex_files["nor"], "Non-Color", (-800, -200))
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nmap.location = (-400, -200)
    nmap.inputs["Strength"].default_value = normal_str
    nt.links.new(t_nor.outputs["Color"], nmap.inputs["Color"])

    # Displacement → Bump (deep joints)
    t_disp = tex_node("Displacement", tex_files["disp"], "Non-Color", (-800, -400))
    bump1 = nt.nodes.new("ShaderNodeBump")
    bump1.location = (-200, -400)
    bump1.inputs["Strength"].default_value = bump_str
    bump1.inputs["Distance"].default_value = bump_dist
    nt.links.new(t_disp.outputs["Color"], bump1.inputs["Height"])
    nt.links.new(nmap.outputs["Normal"], bump1.inputs["Normal"])

    # Micro noise bump (rugosità micro)
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-800, -600)
    noise.inputs["Scale"].default_value = 200.0
    noise.inputs["Detail"].default_value = 16.0
    noise.inputs["Roughness"].default_value = 0.7
    nt.links.new(mp.outputs["Vector"], noise.inputs["Vector"])

    bump2 = nt.nodes.new("ShaderNodeBump")
    bump2.location = (0, -500)
    bump2.inputs["Strength"].default_value = micro_bump_str
    bump2.inputs["Distance"].default_value = 0.002
    nt.links.new(noise.outputs["Fac"], bump2.inputs["Height"])
    nt.links.new(bump1.outputs["Normal"], bump2.inputs["Normal"])

    nt.links.new(bump2.outputs["Normal"], bsdf.inputs["Normal"])

    mat.displacement_method = 'BUMP'
    return mat


def create_wall(name, material, location=(0, 0, 0)):
    """Create 3x2m wall plane"""
    bpy.ops.mesh.primitive_plane_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (3.0, 1.0, 2.0)
    obj.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(material)
    return obj


# === RENDER TEXTURE A ===
print("\n" + "="*60)
print("ITERAZIONE 1A — rock_wall_08")
print("="*60)

scene = setup_scene()
mat_a = create_pbr_wall_material("Wall_A_rock_wall_08", TEXTURES["A_rock_wall_08"],
                                  scale=1.5, sat=0.75, val=1.35,
                                  normal_str=2.0, bump_str=0.8, bump_dist=0.04)
wall_a = create_wall("Wall_A", mat_a)

out_a = os.path.join(OUT_DIR, "iter1_A_rock_wall_08.png")
scene.render.filepath = out_a
bpy.ops.render.render(write_still=True)
print(f"Saved: {out_a}")

# === RENDER TEXTURE B ===
print("\n" + "="*60)
print("ITERAZIONE 1B — stone_wall")
print("="*60)

# Remove wall A, add wall B
bpy.data.objects.remove(wall_a, do_unlink=True)
mat_b = create_pbr_wall_material("Wall_B_stone_wall", TEXTURES["B_stone_wall"],
                                  scale=1.2, sat=0.80, val=1.20,
                                  normal_str=2.0, bump_str=0.8, bump_dist=0.05)
wall_b = create_wall("Wall_B", mat_b)

out_b = os.path.join(OUT_DIR, "iter1_B_stone_wall.png")
scene.render.filepath = out_b
bpy.ops.render.render(write_still=True)
print(f"Saved: {out_b}")

print("\n=== ITERAZIONE 1 COMPLETA ===")
print(f"A: {out_a}")
print(f"B: {out_b}")
