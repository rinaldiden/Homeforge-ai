"""
ELEMENTO 1 — Muro in pietra — ITERAZIONE 4
Fix: camera pulled back to show full wall + sky, more color contrast,
     ground with more variation, slightly darker joints
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

# HDRI — rotated to show mountains in background
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
bg.inputs["Strength"].default_value = 1.8  # Slightly lower to avoid washout
mp_w.inputs["Rotation"].default_value = (0, 0, math.radians(50))  # Sun more from the side for contrast
wnt.links.new(tc_w.outputs["Generated"], mp_w.inputs["Vector"])
wnt.links.new(mp_w.outputs["Vector"], env.inputs["Vector"])
wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
wnt.links.new(bg.outputs["Background"], out_w.inputs["Surface"])

# === GROUND ===
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
mat_g = bpy.data.materials.new("GroundMat")
mat_g.use_nodes = True
gnt = mat_g.node_tree
gbsdf = gnt.nodes["Principled BSDF"]
g_tc = gnt.nodes.new("ShaderNodeTexCoord")
g_tc.location = (-800, 0)
g_noise = gnt.nodes.new("ShaderNodeTexNoise")
g_noise.location = (-600, 0)
g_noise.inputs["Scale"].default_value = 8.0
g_noise.inputs["Detail"].default_value = 12.0
g_noise.inputs["Roughness"].default_value = 0.6
gnt.links.new(g_tc.outputs["Generated"], g_noise.inputs["Vector"])
g_ramp = gnt.nodes.new("ShaderNodeValToRGB")
g_ramp.location = (-400, 0)
g_ramp.color_ramp.elements[0].position = 0.0
g_ramp.color_ramp.elements[0].color = (0.06, 0.10, 0.03, 1.0)
g_ramp.color_ramp.elements[1].position = 1.0
g_ramp.color_ramp.elements[1].color = (0.18, 0.25, 0.10, 1.0)
gnt.links.new(g_noise.outputs["Fac"], g_ramp.inputs["Fac"])
gnt.links.new(g_ramp.outputs["Color"], gbsdf.inputs["Base Color"])
gbsdf.inputs["Roughness"].default_value = 0.95
g_bump = gnt.nodes.new("ShaderNodeBump")
g_bump.location = (-200, -200)
g_bump.inputs["Strength"].default_value = 0.5
g_bump.inputs["Distance"].default_value = 0.02
gnt.links.new(g_noise.outputs["Fac"], g_bump.inputs["Height"])
gnt.links.new(g_bump.outputs["Normal"], gbsdf.inputs["Normal"])
ground.data.materials.append(mat_g)

# === WALL CUBE 3.0 x 0.45 x 2.0m ===
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.0))
wall = bpy.context.active_object
wall.name = "StoneWall"
wall.scale = (3.0, 0.45, 2.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# === STONE MATERIAL ===
mat = bpy.data.materials.new("StoneWall_v4")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

node_out = nt.nodes.new("ShaderNodeOutputMaterial")
node_out.location = (1200, 0)
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (800, 0)
nt.links.new(bsdf.outputs["BSDF"], node_out.inputs["Surface"])

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

# === COLOR: Diffuse * AO → HSV → Base Color ===
t_diff = tex_node("Diffuse", tex["diff"], "sRGB", (-1000, 500))
t_ao = tex_node("AO", tex["ao"], "Non-Color", (-1000, 300))

mix_ao = nt.nodes.new("ShaderNodeMix")
mix_ao.data_type = 'RGBA'
mix_ao.blend_type = 'MULTIPLY'
mix_ao.location = (-600, 400)
mix_ao.inputs["Factor"].default_value = 1.0
nt.links.new(t_diff.outputs["Color"], mix_ao.inputs[6])
nt.links.new(t_ao.outputs["Color"], mix_ao.inputs[7])

# HSV: keep natural saturation, moderate brightness
hsv = nt.nodes.new("ShaderNodeHueSaturation")
hsv.location = (-400, 400)
hsv.inputs["Saturation"].default_value = 0.85  # Keep some warmth in stone
hsv.inputs["Value"].default_value = 1.20  # Less bright than iter3 to preserve contrast
nt.links.new(mix_ao.outputs[2], hsv.inputs["Color"])

# Subtle warm/cool variation across wall face
noise_col = nt.nodes.new("ShaderNodeTexNoise")
noise_col.location = (-800, 150)
noise_col.inputs["Scale"].default_value = 2.0
noise_col.inputs["Detail"].default_value = 4.0
nt.links.new(mp.outputs["Vector"], noise_col.inputs["Vector"])

ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.location = (-600, 150)
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0.92, 0.90, 0.88, 1.0)  # Slightly warm
ramp.color_ramp.elements[1].position = 0.65
ramp.color_ramp.elements[1].color = (0.88, 0.90, 0.85, 1.0)  # Slightly cool
nt.links.new(noise_col.outputs["Fac"], ramp.inputs["Fac"])

mix_var = nt.nodes.new("ShaderNodeMix")
mix_var.data_type = 'RGBA'
mix_var.blend_type = 'MULTIPLY'
mix_var.location = (-200, 300)
mix_var.inputs["Factor"].default_value = 1.0
nt.links.new(hsv.outputs["Color"], mix_var.inputs[6])
nt.links.new(ramp.outputs["Color"], mix_var.inputs[7])
nt.links.new(mix_var.outputs[2], bsdf.inputs["Base Color"])

# === ROUGHNESS ===
t_rough = tex_node("Roughness", tex["rough"], "Non-Color", (-1000, -50))
nt.links.new(t_rough.outputs["Color"], bsdf.inputs["Roughness"])

# === NORMALS: NormalMap → Bump(disp) → Bump(micro) ===
t_nor = tex_node("Normal", tex["nor"], "Non-Color", (-1000, -250))
nmap = nt.nodes.new("ShaderNodeNormalMap")
nmap.location = (-600, -250)
nmap.inputs["Strength"].default_value = 2.0  # Back to 2.0, 2.5 was slightly too much
nt.links.new(t_nor.outputs["Color"], nmap.inputs["Color"])

t_disp = tex_node("Displacement", tex["disp"], "Non-Color", (-1000, -450))
bump1 = nt.nodes.new("ShaderNodeBump")
bump1.location = (-400, -400)
bump1.inputs["Strength"].default_value = 0.9
bump1.inputs["Distance"].default_value = 0.05
nt.links.new(t_disp.outputs["Color"], bump1.inputs["Height"])
nt.links.new(nmap.outputs["Normal"], bump1.inputs["Normal"])

noise_m = nt.nodes.new("ShaderNodeTexNoise")
noise_m.location = (-1000, -650)
noise_m.inputs["Scale"].default_value = 300.0
noise_m.inputs["Detail"].default_value = 16.0
nt.links.new(mp.outputs["Vector"], noise_m.inputs["Vector"])
bump2 = nt.nodes.new("ShaderNodeBump")
bump2.location = (-200, -500)
bump2.inputs["Strength"].default_value = 0.06
bump2.inputs["Distance"].default_value = 0.002
nt.links.new(noise_m.outputs["Fac"], bump2.inputs["Height"])
nt.links.new(bump1.outputs["Normal"], bump2.inputs["Normal"])
nt.links.new(bump2.outputs["Normal"], bsdf.inputs["Normal"])

mat.displacement_method = 'BUMP'
wall.data.materials.append(mat)

# === CAMERA — pulled back, 3/4 view showing full wall + sky + ground ===
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (3.5, -6.0, 2.0)
cam_obj.rotation_euler = (math.radians(74), 0, math.radians(22))
cam_data.lens = 35  # Wider lens to capture context

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

output_path = os.path.join(OUT_DIR, "iter4_wall_fullview.png")
scene.render.filepath = output_path

print(f"\n=== ITER 4 — Full wall view with context ===")
print(f"  Wall: 3.0 x 0.45 x 2.0m cube")
print(f"  Camera: 35mm, 3/4 view, 6m distance")
print(f"  HSV: Sat 0.85, Val 1.20 (less washed out)")
print(f"  HDRI: 1.8 strength, sun from side")
bpy.ops.render.render(write_still=True)
print(f"=== SAVED: {output_path} ===")
