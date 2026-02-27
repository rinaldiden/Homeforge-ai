"""
ELEMENTO 1 — Muro in pietra — ITERAZIONE 3
Fix: CUBO con spessore 0.45m, appoggiato a terra, vista 3/4 angolata,
     terreno con texture, bordi leggermente irregolari
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
    "diff": os.path.join(TEX_DIR, "rock_wall_08_diff_2k.jpg"),
    "nor":  os.path.join(TEX_DIR, "rock_wall_08_nor_gl_2k.jpg"),
    "rough": os.path.join(TEX_DIR, "rock_wall_08_rough_2k.jpg"),
    "disp": os.path.join(TEX_DIR, "rock_wall_08_disp_2k.png"),
    "ao":   os.path.join(TEX_DIR, "rock_wall_08_ao_2k.jpg"),
}
for p in [*tex.values(), hdri_path]:
    assert os.path.exists(p), f"Missing: {p}"

# === SCENE ===
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
bg.inputs["Strength"].default_value = 2.2
mp_w.inputs["Rotation"].default_value = (0, 0, math.radians(70))
wnt.links.new(tc_w.outputs["Generated"], mp_w.inputs["Vector"])
wnt.links.new(mp_w.outputs["Vector"], env.inputs["Vector"])
wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
wnt.links.new(bg.outputs["Background"], out_w.inputs["Surface"])

# === GROUND with grass-like noise texture ===
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
mat_g = bpy.data.materials.new("GroundMat")
mat_g.use_nodes = True
gnt = mat_g.node_tree
gbsdf = gnt.nodes["Principled BSDF"]
# Noise texture for grass variation
g_tc = gnt.nodes.new("ShaderNodeTexCoord")
g_tc.location = (-800, 0)
g_noise = gnt.nodes.new("ShaderNodeTexNoise")
g_noise.location = (-600, 0)
g_noise.inputs["Scale"].default_value = 15.0
g_noise.inputs["Detail"].default_value = 8.0
gnt.links.new(g_tc.outputs["Generated"], g_noise.inputs["Vector"])
g_ramp = gnt.nodes.new("ShaderNodeValToRGB")
g_ramp.location = (-400, 0)
g_ramp.color_ramp.elements[0].position = 0.0
g_ramp.color_ramp.elements[0].color = (0.08, 0.12, 0.04, 1.0)  # Dark grass
g_ramp.color_ramp.elements[1].position = 1.0
g_ramp.color_ramp.elements[1].color = (0.15, 0.22, 0.08, 1.0)  # Light grass
gnt.links.new(g_noise.outputs["Fac"], g_ramp.inputs["Fac"])
gnt.links.new(g_ramp.outputs["Color"], gbsdf.inputs["Base Color"])
gbsdf.inputs["Roughness"].default_value = 0.95
# Ground micro bump
g_bump = gnt.nodes.new("ShaderNodeBump")
g_bump.location = (-200, -200)
g_bump.inputs["Strength"].default_value = 0.3
g_bump.inputs["Distance"].default_value = 0.01
gnt.links.new(g_noise.outputs["Fac"], g_bump.inputs["Height"])
gnt.links.new(g_bump.outputs["Normal"], gbsdf.inputs["Normal"])
ground.data.materials.append(mat_g)

# === WALL — CUBE 3.0 x 0.45 x 2.0m ===
# Use cube for real thickness, base at ground level
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.0))
wall = bpy.context.active_object
wall.name = "StoneWall"
# Half-sizes: X=1.5, Y=0.225, Z=1.0 → full: 3.0 x 0.45 x 2.0
wall.scale = (3.0, 0.45, 2.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# === STONE WALL MATERIAL ===
mat = bpy.data.materials.new("StoneWall_v3")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

node_out = nt.nodes.new("ShaderNodeOutputMaterial")
node_out.location = (1200, 0)
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (800, 0)
nt.links.new(bsdf.outputs["BSDF"], node_out.inputs["Surface"])

# Tex Coord + Mapping
tc = nt.nodes.new("ShaderNodeTexCoord")
tc.location = (-1600, 0)
mp = nt.nodes.new("ShaderNodeMapping")
mp.location = (-1400, 0)
mp.inputs["Scale"].default_value = (1.2, 1.2, 1.2)
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

# COLOR CHAIN: Diffuse * AO → HSV → Moss variation → Base Color
t_diff = tex_node("Diffuse", tex["diff"], "sRGB", (-1000, 500))
t_ao = tex_node("AO", tex["ao"], "Non-Color", (-1000, 300))

mix_ao = nt.nodes.new("ShaderNodeMix")
mix_ao.data_type = 'RGBA'
mix_ao.blend_type = 'MULTIPLY'
mix_ao.location = (-600, 400)
mix_ao.inputs["Factor"].default_value = 1.0
nt.links.new(t_diff.outputs["Color"], mix_ao.inputs[6])
nt.links.new(t_ao.outputs["Color"], mix_ao.inputs[7])

hsv = nt.nodes.new("ShaderNodeHueSaturation")
hsv.location = (-400, 400)
hsv.inputs["Saturation"].default_value = 0.82
hsv.inputs["Value"].default_value = 1.35
nt.links.new(mix_ao.outputs[2], hsv.inputs["Color"])

# Moss/lichen color variation
noise_col = nt.nodes.new("ShaderNodeTexNoise")
noise_col.location = (-800, 150)
noise_col.inputs["Scale"].default_value = 2.5
noise_col.inputs["Detail"].default_value = 5.0
nt.links.new(mp.outputs["Vector"], noise_col.inputs["Vector"])
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.location = (-600, 150)
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0.90, 0.90, 0.88, 1.0)  # Neutral
ramp.color_ramp.elements[1].position = 0.75
ramp.color_ramp.elements[1].color = (0.80, 0.83, 0.70, 1.0)  # Subtle lichen green
nt.links.new(noise_col.outputs["Fac"], ramp.inputs["Fac"])

mix_moss = nt.nodes.new("ShaderNodeMix")
mix_moss.data_type = 'RGBA'
mix_moss.blend_type = 'MULTIPLY'
mix_moss.location = (-200, 300)
mix_moss.inputs["Factor"].default_value = 1.0
nt.links.new(hsv.outputs["Color"], mix_moss.inputs[6])
nt.links.new(ramp.outputs["Color"], mix_moss.inputs[7])
nt.links.new(mix_moss.outputs[2], bsdf.inputs["Base Color"])

# ROUGHNESS
t_rough = tex_node("Roughness", tex["rough"], "Non-Color", (-1000, -50))
nt.links.new(t_rough.outputs["Color"], bsdf.inputs["Roughness"])

# NORMAL CHAIN
t_nor = tex_node("Normal", tex["nor"], "Non-Color", (-1000, -250))
nmap = nt.nodes.new("ShaderNodeNormalMap")
nmap.location = (-600, -250)
nmap.inputs["Strength"].default_value = 2.5
nt.links.new(t_nor.outputs["Color"], nmap.inputs["Color"])

# Bump macro (displacement map)
t_disp = tex_node("Displacement", tex["disp"], "Non-Color", (-1000, -450))
bump1 = nt.nodes.new("ShaderNodeBump")
bump1.location = (-400, -400)
bump1.inputs["Strength"].default_value = 1.0
bump1.inputs["Distance"].default_value = 0.05
nt.links.new(t_disp.outputs["Color"], bump1.inputs["Height"])
nt.links.new(nmap.outputs["Normal"], bump1.inputs["Normal"])

# Bump micro (noise)
noise_m = nt.nodes.new("ShaderNodeTexNoise")
noise_m.location = (-1000, -650)
noise_m.inputs["Scale"].default_value = 250.0
noise_m.inputs["Detail"].default_value = 16.0
noise_m.inputs["Roughness"].default_value = 0.8
nt.links.new(mp.outputs["Vector"], noise_m.inputs["Vector"])
bump2 = nt.nodes.new("ShaderNodeBump")
bump2.location = (-200, -500)
bump2.inputs["Strength"].default_value = 0.08
bump2.inputs["Distance"].default_value = 0.003
nt.links.new(noise_m.outputs["Fac"], bump2.inputs["Height"])
nt.links.new(bump1.outputs["Normal"], bump2.inputs["Normal"])
nt.links.new(bump2.outputs["Normal"], bsdf.inputs["Normal"])

mat.displacement_method = 'BUMP'
wall.data.materials.append(mat)

# === CAMERA — 3/4 view, architectural photography style ===
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
# 3/4 view: slightly to the side and above, looking at wall center
cam_obj.location = (2.5, -4.5, 1.8)
cam_obj.rotation_euler = (math.radians(75), 0, math.radians(22))
cam_data.lens = 50

# === RENDER ===
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

output_path = os.path.join(OUT_DIR, "iter3_wall_3d_34view.png")
scene.render.filepath = output_path

print(f"\n=== ITER 3 — Wall with real thickness, 3/4 view ===")
print(f"  Wall: CUBE 3.0 x 0.45 x 2.0m, base at z=0")
print(f"  View: 3/4 angle, 50mm")
print(f"  Ground: noise-textured grass")
print(f"  Moss variation: subtle lichen hints")
bpy.ops.render.render(write_still=True)
print(f"=== SAVED: {output_path} ===")
