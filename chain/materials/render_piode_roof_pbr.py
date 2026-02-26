"""
Piode Roof PBR Preview — Slate stone roof + wood beams with HDRI
Textures: castle_wall_slates (roof), weathered_brown_planks (beams)
HDRI: alps_field (Poly Haven CC0)
"""
import bpy
import os
import math
import bmesh

# --- Paths ---
TEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

piode_tex = {
    "diff": os.path.join(TEX_DIR, "castle_wall_slates_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "castle_wall_slates_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "castle_wall_slates_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "castle_wall_slates_disp_2k.png"),
    "ao":   os.path.join(TEX_DIR, "castle_wall_slates_ao_2k.jpg"),
}
wood_tex = {
    "diff": os.path.join(TEX_DIR, "weathered_brown_planks_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "weathered_brown_planks_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "weathered_brown_planks_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "weathered_brown_planks_disp_2k.png"),
    "ao":   os.path.join(TEX_DIR, "weathered_brown_planks_ao_2k.jpg"),
}
hdri_path = os.path.join(TEX_DIR, "alps_field_2k.hdr")

# Verify files
for name, path in {**piode_tex, **{f"wood_{k}": v for k, v in wood_tex.items()}, "hdri": hdri_path}.items():
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing: {path}")
    print(f"  [OK] {name}")

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

node_bg.inputs["Strength"].default_value = 1.8
node_mapping.inputs["Rotation"].default_value = (0, 0, math.radians(120))

wnt.links.new(node_texcoord.outputs["Generated"], node_mapping.inputs["Vector"])
wnt.links.new(node_mapping.outputs["Vector"], node_env.inputs["Vector"])
wnt.links.new(node_env.outputs["Color"], node_bg.inputs["Color"])
wnt.links.new(node_bg.outputs["Background"], node_output.inputs["Surface"])


def create_pbr_material(name, tex_files, scale=(1.0, 1.0, 1.0), sat=1.0, val=1.0):
    """Create a full PBR material from texture files"""
    mat = bpy.data.materials.new(name)
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
    node_map.inputs["Scale"].default_value = scale
    nt.links.new(node_tc.outputs["Generated"], node_map.inputs["Vector"])

    def add_tex(label, filepath, colorspace, loc):
        node = nt.nodes.new("ShaderNodeTexImage")
        node.label = label
        node.location = loc
        node.image = bpy.data.images.load(filepath)
        node.image.colorspace_settings.name = colorspace
        node.projection = 'BOX'
        node.projection_blend = 0.3
        nt.links.new(node_map.outputs["Vector"], node.inputs["Vector"])
        return node

    # Diffuse + AO multiply
    tex_diff = add_tex("Diffuse", tex_files["diff"], "sRGB", (-600, 300))
    tex_ao = add_tex("AO", tex_files["ao"], "Non-Color", (-600, 100))

    node_mix = nt.nodes.new("ShaderNodeMix")
    node_mix.data_type = 'RGBA'
    node_mix.blend_type = 'MULTIPLY'
    node_mix.location = (-200, 200)
    node_mix.inputs["Factor"].default_value = 1.0
    nt.links.new(tex_diff.outputs["Color"], node_mix.inputs[6])
    nt.links.new(tex_ao.outputs["Color"], node_mix.inputs[7])

    # HSV correction
    node_hsv = nt.nodes.new("ShaderNodeHueSaturation")
    node_hsv.location = (0, 200)
    node_hsv.inputs["Saturation"].default_value = sat
    node_hsv.inputs["Value"].default_value = val
    nt.links.new(node_mix.outputs[2], node_hsv.inputs["Color"])
    nt.links.new(node_hsv.outputs["Color"], node_bsdf.inputs["Base Color"])

    # Roughness
    tex_rough = add_tex("Roughness", tex_files["rough"], "Non-Color", (-600, -100))
    nt.links.new(tex_rough.outputs["Color"], node_bsdf.inputs["Roughness"])

    # Normal Map
    tex_nor = add_tex("Normal", tex_files["nor"], "Non-Color", (-600, -300))
    node_normal = nt.nodes.new("ShaderNodeNormalMap")
    node_normal.location = (-200, -300)
    node_normal.inputs["Strength"].default_value = 2.0
    nt.links.new(tex_nor.outputs["Color"], node_normal.inputs["Color"])

    # Displacement → Bump
    tex_disp = add_tex("Displacement", tex_files["disp"], "Non-Color", (-600, -500))
    node_bump = nt.nodes.new("ShaderNodeBump")
    node_bump.location = (-200, -500)
    node_bump.inputs["Strength"].default_value = 0.6
    node_bump.inputs["Distance"].default_value = 0.03
    nt.links.new(tex_disp.outputs["Color"], node_bump.inputs["Height"])
    nt.links.new(node_normal.outputs["Normal"], node_bump.inputs["Normal"])
    nt.links.new(node_bump.outputs["Normal"], node_bsdf.inputs["Normal"])

    mat.displacement_method = 'BUMP'
    return mat


# --- Create Piode Material ---
mat_piode = create_pbr_material(
    "Piode_PBR", piode_tex,
    scale=(2.0, 2.0, 2.0),
    sat=0.7,   # Stone slate is very desaturated
    val=1.15   # Slightly brighten
)

# --- Create Wood Beam Material ---
mat_wood = create_pbr_material(
    "WoodBeam_PBR", wood_tex,
    scale=(1.0, 3.0, 1.0),  # Stretch along beam length
    sat=0.9,
    val=1.1
)


# ====== GEOMETRY ======

# --- Roof slope (single side, viewed from angle) ---
# Create a tilted plane for the roof
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 2.5))
roof = bpy.context.active_object
roof.name = "RoofSlope"
roof.scale = (5.0, 1.0, 3.5)
roof.rotation_euler = (math.radians(55), 0, 0)  # 35° pitch
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
roof.data.materials.append(mat_piode)

# --- Supporting wall (stone) ---
# Create a small stone wall under the roof
mat_stone = create_pbr_material(
    "StoneWall_Support", piode_tex,  # Reuse slates for now
    scale=(1.5, 1.5, 1.5),
    sat=0.75,
    val=1.3
)
# Actually use rock_wall_08 for the wall
from importlib import reload
rock_wall_tex = {
    "diff": os.path.join(TEX_DIR, "rock_wall_08_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "rock_wall_08_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "rock_wall_08_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "rock_wall_08_disp_2k.png"),
    "ao":   os.path.join(TEX_DIR, "rock_wall_08_ao_2k.jpg"),
}
mat_stone = create_pbr_material(
    "StoneWall_Support", rock_wall_tex,
    scale=(1.5, 1.5, 1.5),
    sat=0.75,
    val=1.40
)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 1.0, 0.75))
wall = bpy.context.active_object
wall.name = "SupportWall"
wall.scale = (5.0, 0.45, 1.5)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
wall.data.materials.append(mat_stone)

# --- Wood beams (horizontal, exposed under roof edge) ---
beam_positions = [(-2.0, -0.2, 1.5), (-1.0, -0.2, 1.5), (0.0, -0.2, 1.5),
                  (1.0, -0.2, 1.5), (2.0, -0.2, 1.5)]
for i, pos in enumerate(beam_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    beam = bpy.context.active_object
    beam.name = f"Beam_{i}"
    beam.scale = (0.12, 0.8, 0.10)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    beam.data.materials.append(mat_wood)

# Main ridge beam
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.2, 1.55))
ridge = bpy.context.active_object
ridge.name = "RidgeBeam"
ridge.scale = (5.0, 0.10, 0.12)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
ridge.data.materials.append(mat_wood)

# --- Ground plane (grass-like, subtle) ---
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
mat_ground = bpy.data.materials.new("Ground")
mat_ground.use_nodes = True
bsdf = mat_ground.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.15, 0.2, 0.08, 1.0)
bsdf.inputs["Roughness"].default_value = 0.95
ground.data.materials.append(mat_ground)


# --- Camera ---
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (3.0, -6.0, 3.5)
cam_obj.rotation_euler = (math.radians(65), 0, math.radians(20))
cam_data.lens = 35

# --- Render Settings ---
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

# --- Output ---
output_path = os.path.join(OUT_DIR, "piode_roof_PBR_preview.png")
scene.render.filepath = output_path

print(f"\n=== Rendering piode roof PBR preview ===")
print(f"  Piode: castle_wall_slates (diff/nor/rough/disp/ao)")
print(f"  Wood: weathered_brown_planks")
print(f"  Wall: rock_wall_08")
print(f"  HDRI: alps_field_2k")
print(f"  Samples: 512")
print(f"  Output: {output_path}")

bpy.ops.render.render(write_still=True)
print(f"\n=== DONE: {output_path} ===")
