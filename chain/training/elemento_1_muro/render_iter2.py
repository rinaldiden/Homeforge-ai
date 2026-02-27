"""
ELEMENTO 1 — Muro in pietra — ITERAZIONE 2
Fix: camera più lontana, texture scale ridotto (pietre più grandi),
     variazione colore con Color Ramp, muschio sottile, HDRI più luminoso
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
bg.inputs["Strength"].default_value = 2.2  # Brighter
mp_w.inputs["Rotation"].default_value = (0, 0, math.radians(70))  # Better sun angle
wnt.links.new(tc_w.outputs["Generated"], mp_w.inputs["Vector"])
wnt.links.new(mp_w.outputs["Vector"], env.inputs["Vector"])
wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
wnt.links.new(bg.outputs["Background"], out_w.inputs["Surface"])

# === GROUND PLANE ===
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
mat_g = bpy.data.materials.new("GroundMat")
mat_g.use_nodes = True
bsdf_g = mat_g.node_tree.nodes["Principled BSDF"]
bsdf_g.inputs["Base Color"].default_value = (0.12, 0.15, 0.07, 1.0)
bsdf_g.inputs["Roughness"].default_value = 0.95
ground.data.materials.append(mat_g)

# === WALL 3x2m ===
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 1.0))
wall = bpy.context.active_object
wall.name = "StoneWall"
wall.scale = (3.0, 1.0, 2.0)
wall.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# === MATERIAL ===
mat = bpy.data.materials.new("StoneWall_v2")
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
mp.inputs["Scale"].default_value = (1.2, 1.2, 1.2)  # Larger stones
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

# Diffuse
t_diff = tex_node("Diffuse", tex["diff"], "sRGB", (-1000, 500))
# AO
t_ao = tex_node("AO", tex["ao"], "Non-Color", (-1000, 300))

# Multiply Diff * AO
mix_ao = nt.nodes.new("ShaderNodeMix")
mix_ao.data_type = 'RGBA'
mix_ao.blend_type = 'MULTIPLY'
mix_ao.location = (-600, 400)
mix_ao.inputs["Factor"].default_value = 1.0
nt.links.new(t_diff.outputs["Color"], mix_ao.inputs[6])
nt.links.new(t_ao.outputs["Color"], mix_ao.inputs[7])

# HSV — less desaturation, brighter
hsv = nt.nodes.new("ShaderNodeHueSaturation")
hsv.location = (-400, 400)
hsv.inputs["Saturation"].default_value = 0.80  # Keep some warmth
hsv.inputs["Value"].default_value = 1.40  # Brighter for alpine sunlit stone
nt.links.new(mix_ao.outputs[2], hsv.inputs["Color"])

# === SUBTLE MOSS/LICHEN COLOR VARIATION ===
# Noise texture for organic color variation (moss hints)
noise_color = nt.nodes.new("ShaderNodeTexNoise")
noise_color.location = (-800, 150)
noise_color.inputs["Scale"].default_value = 3.0
noise_color.inputs["Detail"].default_value = 6.0
noise_color.inputs["Roughness"].default_value = 0.6
nt.links.new(mp.outputs["Vector"], noise_color.inputs["Vector"])

# Color ramp for moss: mostly neutral, hints of green/brown
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.location = (-600, 150)
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0.85, 0.85, 0.85, 1.0)  # Neutral (most area)
ramp.color_ramp.elements[1].position = 0.7
ramp.color_ramp.elements[1].color = (0.75, 0.80, 0.65, 1.0)  # Subtle green-ish hint
nt.links.new(noise_color.outputs["Fac"], ramp.inputs["Fac"])

# Mix base color * moss variation (very subtle)
mix_moss = nt.nodes.new("ShaderNodeMix")
mix_moss.data_type = 'RGBA'
mix_moss.blend_type = 'MULTIPLY'
mix_moss.location = (-200, 300)
mix_moss.inputs["Factor"].default_value = 1.0
nt.links.new(hsv.outputs["Color"], mix_moss.inputs[6])
nt.links.new(ramp.outputs["Color"], mix_moss.inputs[7])
nt.links.new(mix_moss.outputs[2], bsdf.inputs["Base Color"])

# Roughness
t_rough = tex_node("Roughness", tex["rough"], "Non-Color", (-1000, -50))
nt.links.new(t_rough.outputs["Color"], bsdf.inputs["Roughness"])

# Normal Map
t_nor = tex_node("Normal", tex["nor"], "Non-Color", (-1000, -250))
nmap = nt.nodes.new("ShaderNodeNormalMap")
nmap.location = (-600, -250)
nmap.inputs["Strength"].default_value = 2.5  # Stronger for deep detail
nt.links.new(t_nor.outputs["Color"], nmap.inputs["Color"])

# Displacement → Bump (macro)
t_disp = tex_node("Displacement", tex["disp"], "Non-Color", (-1000, -450))
bump1 = nt.nodes.new("ShaderNodeBump")
bump1.location = (-400, -400)
bump1.inputs["Strength"].default_value = 1.0  # Stronger bump
bump1.inputs["Distance"].default_value = 0.05
nt.links.new(t_disp.outputs["Color"], bump1.inputs["Height"])
nt.links.new(nmap.outputs["Normal"], bump1.inputs["Normal"])

# Micro noise bump
noise_micro = nt.nodes.new("ShaderNodeTexNoise")
noise_micro.location = (-1000, -650)
noise_micro.inputs["Scale"].default_value = 250.0
noise_micro.inputs["Detail"].default_value = 16.0
noise_micro.inputs["Roughness"].default_value = 0.8
nt.links.new(mp.outputs["Vector"], noise_micro.inputs["Vector"])

bump2 = nt.nodes.new("ShaderNodeBump")
bump2.location = (-200, -500)
bump2.inputs["Strength"].default_value = 0.08
bump2.inputs["Distance"].default_value = 0.003
nt.links.new(noise_micro.outputs["Fac"], bump2.inputs["Height"])
nt.links.new(bump1.outputs["Normal"], bump2.inputs["Normal"])

nt.links.new(bump2.outputs["Normal"], bsdf.inputs["Normal"])
mat.displacement_method = 'BUMP'
wall.data.materials.append(mat)

# === CAMERA ===
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
# Pulled back more, slight angle for depth perception
cam_obj.location = (0.5, -5.0, 1.3)
cam_obj.rotation_euler = (math.radians(83), 0, math.radians(3))
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

output_path = os.path.join(OUT_DIR, "iter2_rock_wall_refined.png")
scene.render.filepath = output_path

print(f"\n=== ITER 2 — Rock Wall Refined ===")
print(f"  Scale: 1.2 (larger stones)")
print(f"  Sat: 0.80, Val: 1.40")
print(f"  Normal: 2.5, Bump: 1.0/0.05")
print(f"  Moss variation: subtle green hints")
print(f"  HDRI strength: 2.2")
print(f"  Camera: 50mm at 5m distance")
bpy.ops.render.render(write_still=True)
print(f"=== SAVED: {output_path} ===")
