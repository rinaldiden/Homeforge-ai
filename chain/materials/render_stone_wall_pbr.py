"""
Stone Wall PBR Preview — Full texture-based material with HDRI lighting
Textures: rock_wall_08 (Poly Haven CC0)
HDRI: alps_field (Poly Haven CC0)
"""
import bpy
import os
import math

# --- Paths ---
TEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

tex_files = {
    "diff": os.path.join(TEX_DIR, "rock_wall_08_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "rock_wall_08_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "rock_wall_08_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "rock_wall_08_disp_2k.png"),
    "ao":   os.path.join(TEX_DIR, "rock_wall_08_ao_2k.jpg"),
}
hdri_path = os.path.join(TEX_DIR, "alps_field_2k.hdr")

# Verify files
for name, path in {**tex_files, "hdri": hdri_path}.items():
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing: {path}")
    print(f"  [OK] {name}: {os.path.basename(path)}")

# --- Clean scene ---
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# --- HDRI Environment ---
world = bpy.data.worlds.new("World_HDRI")
scene.world = world
world.use_nodes = True
wnt = world.node_tree
wnt.nodes.clear()

node_bg = wnt.nodes.new("ShaderNodeBackground")
node_env = wnt.nodes.new("ShaderNodeTexEnvironment")
node_env.image = bpy.data.images.load(hdri_path)
node_mapping = wnt.nodes.new("ShaderNodeMapping")
node_texcoord = wnt.nodes.new("ShaderNodeTexCoord")
node_output = wnt.nodes.new("ShaderNodeOutputWorld")

node_bg.inputs["Strength"].default_value = 1.8  # Brighter HDRI for outdoor alpine light
# Rotate HDRI to get good front-lighting angle
node_mapping.inputs["Rotation"].default_value = (0, 0, math.radians(120))

wnt.links.new(node_texcoord.outputs["Generated"], node_mapping.inputs["Vector"])
wnt.links.new(node_mapping.outputs["Vector"], node_env.inputs["Vector"])
wnt.links.new(node_env.outputs["Color"], node_bg.inputs["Color"])
wnt.links.new(node_bg.outputs["Background"], node_output.inputs["Surface"])

# --- Wall geometry ---
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
wall = bpy.context.active_object
wall.name = "StoneWall"
wall.scale = (3.0, 1.0, 2.0)  # 3m wide x 2m tall
wall.rotation_euler = (math.radians(90), 0, 0)  # Stand upright
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# --- PBR Material ---
mat = bpy.data.materials.new("StoneWall_PBR")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

# Output + BSDF
node_out = nt.nodes.new("ShaderNodeOutputMaterial")
node_out.location = (800, 0)
node_bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
node_bsdf.location = (400, 0)
nt.links.new(node_bsdf.outputs["BSDF"], node_out.inputs["Surface"])

# Texture Coordinate + Mapping
node_tc = nt.nodes.new("ShaderNodeTexCoord")
node_tc.location = (-1200, 0)
node_map = nt.nodes.new("ShaderNodeMapping")
node_map.location = (-1000, 0)
node_map.inputs["Scale"].default_value = (1.5, 1.5, 1.5)
nt.links.new(node_tc.outputs["Generated"], node_map.inputs["Vector"])

def add_image_texture(name, filepath, colorspace, location, projection='BOX'):
    """Add an Image Texture node"""
    node = nt.nodes.new("ShaderNodeTexImage")
    node.name = name
    node.label = name
    node.location = location
    node.image = bpy.data.images.load(filepath)
    node.image.colorspace_settings.name = colorspace
    if projection == 'BOX':
        node.projection = 'BOX'
        node.projection_blend = 0.3
    nt.links.new(node_map.outputs["Vector"], node.inputs["Vector"])
    return node

# Diffuse
tex_diff = add_image_texture("Diffuse", tex_files["diff"], "sRGB", (-600, 300))

# AO
tex_ao = add_image_texture("AO", tex_files["ao"], "Non-Color", (-600, 100))

# Mix diffuse * AO
node_mix_ao = nt.nodes.new("ShaderNodeMix")
node_mix_ao.data_type = 'RGBA'
node_mix_ao.location = (-200, 200)
node_mix_ao.inputs["Factor"].default_value = 0.7  # AO strength
# Blender 5.0: Mix node inputs
nt.links.new(tex_diff.outputs["Color"], node_mix_ao.inputs[6])   # A (color)
nt.links.new(tex_ao.outputs["Color"], node_mix_ao.inputs[7])     # B (color)
node_mix_ao.blend_type = 'MULTIPLY'
node_mix_ao.inputs["Factor"].default_value = 1.0

# Hue/Saturation for color correction
node_hsv = nt.nodes.new("ShaderNodeHueSaturation")
node_hsv.location = (0, 200)
node_hsv.inputs["Saturation"].default_value = 0.75  # More desaturated — Valtellina stone is grey
node_hsv.inputs["Value"].default_value = 1.40  # Brighter for alpine sun-lit stone
nt.links.new(node_mix_ao.outputs[2], node_hsv.inputs["Color"])
nt.links.new(node_hsv.outputs["Color"], node_bsdf.inputs["Base Color"])

# Roughness
tex_rough = add_image_texture("Roughness", tex_files["rough"], "Non-Color", (-600, -100))
nt.links.new(tex_rough.outputs["Color"], node_bsdf.inputs["Roughness"])

# Normal Map
tex_nor = add_image_texture("Normal", tex_files["nor"], "Non-Color", (-600, -300))
node_normal = nt.nodes.new("ShaderNodeNormalMap")
node_normal.location = (-200, -300)
node_normal.inputs["Strength"].default_value = 2.0
nt.links.new(tex_nor.outputs["Color"], node_normal.inputs["Color"])

# Displacement map -> Bump (deep joints)
tex_disp = add_image_texture("Displacement", tex_files["disp"], "Non-Color", (-600, -500))
node_bump1 = nt.nodes.new("ShaderNodeBump")
node_bump1.location = (-200, -500)
node_bump1.inputs["Strength"].default_value = 0.8
node_bump1.inputs["Distance"].default_value = 0.04
nt.links.new(tex_disp.outputs["Color"], node_bump1.inputs["Height"])
nt.links.new(node_normal.outputs["Normal"], node_bump1.inputs["Normal"])

# Micro noise bump (surface roughness per-stone)
node_noise = nt.nodes.new("ShaderNodeTexNoise")
node_noise.location = (-600, -700)
node_noise.inputs["Scale"].default_value = 150.0
node_noise.inputs["Detail"].default_value = 16.0
nt.links.new(node_map.outputs["Vector"], node_noise.inputs["Vector"])

node_bump2 = nt.nodes.new("ShaderNodeBump")
node_bump2.location = (0, -600)
node_bump2.inputs["Strength"].default_value = 0.05
node_bump2.inputs["Distance"].default_value = 0.002
nt.links.new(node_noise.outputs["Fac"], node_bump2.inputs["Height"])
nt.links.new(node_bump1.outputs["Normal"], node_bump2.inputs["Normal"])

nt.links.new(node_bump2.outputs["Normal"], node_bsdf.inputs["Normal"])

# Displacement method
mat.displacement_method = 'BUMP'

# Assign material
wall.data.materials.append(mat)

# --- Camera ---
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0.3, -4.5, 1.0)
cam_obj.rotation_euler = (math.radians(82), 0, math.radians(2))
cam_data.lens = 35  # Wider to capture full 3x2m wall

# --- Render Settings ---
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 512
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# Color management
scene.view_settings.view_transform = 'AgX'
try:
    scene.view_settings.look = 'AgX - Medium Contrast'
except:
    scene.view_settings.look = 'AgX - Base Contrast'

# --- Output ---
output_path = os.path.join(OUT_DIR, "stone_wall_PBR_preview.png")
scene.render.filepath = output_path

print(f"\n=== Rendering stone wall PBR preview ===")
print(f"  Textures: rock_wall_08 (diff/nor/rough/disp/ao)")
print(f"  HDRI: alps_field_2k")
print(f"  Samples: 512")
print(f"  Output: {output_path}")

bpy.ops.render.render(write_still=True)
print(f"\n=== DONE: {output_path} ===")
