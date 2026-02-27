"""
ELEMENTO 1 — Muro in pietra — ITERAZIONE 5 (FINALE)
Fix: bordo superiore irregolare via displacement vertex, terreno alpino,
     sporco alla base, contrasto pietre migliorato
"""
import bpy
import os
import math
import bmesh
import random

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
bg.inputs["Strength"].default_value = 1.8
mp_w.inputs["Rotation"].default_value = (0, 0, math.radians(50))
wnt.links.new(tc_w.outputs["Generated"], mp_w.inputs["Vector"])
wnt.links.new(mp_w.outputs["Vector"], env.inputs["Vector"])
wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
wnt.links.new(bg.outputs["Background"], out_w.inputs["Surface"])

# === GROUND — alpine terrain (grass + dirt + rocks) ===
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
mat_g = bpy.data.materials.new("AlpineGround")
mat_g.use_nodes = True
gnt = mat_g.node_tree
gbsdf = gnt.nodes["Principled BSDF"]

g_tc = gnt.nodes.new("ShaderNodeTexCoord")
g_tc.location = (-1000, 0)

# Noise 1: large-scale patches (grass vs dirt)
g_n1 = gnt.nodes.new("ShaderNodeTexNoise")
g_n1.location = (-800, 200)
g_n1.inputs["Scale"].default_value = 4.0
g_n1.inputs["Detail"].default_value = 4.0
gnt.links.new(g_tc.outputs["Generated"], g_n1.inputs["Vector"])

# Noise 2: small-scale variation
g_n2 = gnt.nodes.new("ShaderNodeTexNoise")
g_n2.location = (-800, -100)
g_n2.inputs["Scale"].default_value = 20.0
g_n2.inputs["Detail"].default_value = 10.0
gnt.links.new(g_tc.outputs["Generated"], g_n2.inputs["Vector"])

# Color ramp: grass
g_ramp1 = gnt.nodes.new("ShaderNodeValToRGB")
g_ramp1.location = (-600, 200)
g_ramp1.color_ramp.elements[0].position = 0.0
g_ramp1.color_ramp.elements[0].color = (0.10, 0.14, 0.05, 1.0)  # Dark grass
g_ramp1.color_ramp.elements[1].position = 1.0
g_ramp1.color_ramp.elements[1].color = (0.06, 0.08, 0.03, 1.0)  # Earthy brown-green
gnt.links.new(g_n1.outputs["Fac"], g_ramp1.inputs["Fac"])

# Mix grass with fine noise for detail
g_mix = gnt.nodes.new("ShaderNodeMix")
g_mix.data_type = 'RGBA'
g_mix.blend_type = 'OVERLAY'
g_mix.location = (-400, 100)
g_mix.inputs["Factor"].default_value = 0.3
gnt.links.new(g_ramp1.outputs["Color"], g_mix.inputs[6])
gnt.links.new(g_n2.outputs["Color"], g_mix.inputs[7])
gnt.links.new(g_mix.outputs[2], gbsdf.inputs["Base Color"])

gbsdf.inputs["Roughness"].default_value = 0.95
# Ground bump
g_bump = gnt.nodes.new("ShaderNodeBump")
g_bump.location = (-200, -200)
g_bump.inputs["Strength"].default_value = 0.5
g_bump.inputs["Distance"].default_value = 0.02
gnt.links.new(g_n2.outputs["Fac"], g_bump.inputs["Height"])
gnt.links.new(g_bump.outputs["Normal"], gbsdf.inputs["Normal"])
ground.data.materials.append(mat_g)


# === WALL with IRREGULAR TOP EDGE ===
# Start with a subdivided cube, then displace top vertices randomly
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.0))
wall = bpy.context.active_object
wall.name = "StoneWall"
wall.scale = (3.0, 0.45, 2.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Subdivide top edges for irregularity
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(wall.data)
bm.faces.ensure_lookup_table()
bm.verts.ensure_lookup_table()

# Add loop cuts along X for more vertices on top edge
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=12)
bm = bmesh.from_edit_mesh(wall.data)
bm.verts.ensure_lookup_table()

# Displace top vertices (z > 1.8) randomly in Z
random.seed(42)
for v in bm.verts:
    if v.co.z > 0.85:  # Top portion of wall
        # More displacement near the very top
        factor = (v.co.z - 0.85) / 0.15
        v.co.z += random.uniform(-0.08, 0.04) * factor
        v.co.y += random.uniform(-0.02, 0.02) * factor

bmesh.update_edit_mesh(wall.data)
bpy.ops.object.mode_set(mode='OBJECT')

# === STONE MATERIAL (refined v5) ===
mat = bpy.data.materials.new("StoneWall_v5")
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

# COLOR CHAIN
t_diff = tex_node("Diffuse", tex["diff"], "sRGB", (-1000, 500))
t_ao = tex_node("AO", tex["ao"], "Non-Color", (-1000, 300))

mix_ao = nt.nodes.new("ShaderNodeMix")
mix_ao.data_type = 'RGBA'
mix_ao.blend_type = 'MULTIPLY'
mix_ao.location = (-600, 400)
mix_ao.inputs["Factor"].default_value = 1.0
nt.links.new(t_diff.outputs["Color"], mix_ao.inputs[6])
nt.links.new(t_ao.outputs["Color"], mix_ao.inputs[7])

# Brightness/Contrast node for more punch
bc = nt.nodes.new("ShaderNodeBrightContrast")
bc.location = (-400, 400)
bc.inputs["Bright"].default_value = 0.05
bc.inputs["Contrast"].default_value = 0.15  # More contrast between light stones and dark joints
nt.links.new(mix_ao.outputs[2], bc.inputs["Color"])

hsv = nt.nodes.new("ShaderNodeHueSaturation")
hsv.location = (-200, 400)
hsv.inputs["Saturation"].default_value = 0.85
hsv.inputs["Value"].default_value = 1.15
nt.links.new(bc.outputs["Color"], hsv.inputs["Color"])

# Dirt at base: darken bottom of wall using Object Z gradient
sep_xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
sep_xyz.location = (-1000, 100)
nt.links.new(tc.outputs["Generated"], sep_xyz.inputs["Vector"])

# Map Z: bottom (0) = darker, top (1) = normal
dirt_ramp = nt.nodes.new("ShaderNodeValToRGB")
dirt_ramp.location = (-800, 100)
dirt_ramp.color_ramp.elements[0].position = 0.0
dirt_ramp.color_ramp.elements[0].color = (0.70, 0.68, 0.62, 1.0)  # Dirt tint at base
dirt_ramp.color_ramp.elements[1].position = 0.25
dirt_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)  # Clean upper wall
nt.links.new(sep_xyz.outputs["Z"], dirt_ramp.inputs["Fac"])

mix_dirt = nt.nodes.new("ShaderNodeMix")
mix_dirt.data_type = 'RGBA'
mix_dirt.blend_type = 'MULTIPLY'
mix_dirt.location = (0, 300)
mix_dirt.inputs["Factor"].default_value = 1.0
nt.links.new(hsv.outputs["Color"], mix_dirt.inputs[6])
nt.links.new(dirt_ramp.outputs["Color"], mix_dirt.inputs[7])
nt.links.new(mix_dirt.outputs[2], bsdf.inputs["Base Color"])

# ROUGHNESS
t_rough = tex_node("Roughness", tex["rough"], "Non-Color", (-1000, -50))
nt.links.new(t_rough.outputs["Color"], bsdf.inputs["Roughness"])

# NORMALS
t_nor = tex_node("Normal", tex["nor"], "Non-Color", (-1000, -250))
nmap = nt.nodes.new("ShaderNodeNormalMap")
nmap.location = (-600, -250)
nmap.inputs["Strength"].default_value = 2.0
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

# === CAMERA ===
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (3.0, -5.5, 2.2)
cam_obj.rotation_euler = (math.radians(72), 0, math.radians(20))
cam_data.lens = 35

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

output_path = os.path.join(OUT_DIR, "iter5_wall_final.png")
scene.render.filepath = output_path

print(f"\n=== ITER 5 (FINALE) — Irregular top, dirt at base, alpine ground ===")
print(f"  Wall: 3.0x0.45x2.0 with subdivided irregular top edge")
print(f"  Dirt gradient at base")
print(f"  Ground: alpine grass/dirt noise")
print(f"  Contrast boost: +0.15")
bpy.ops.render.render(write_still=True)
print(f"=== SAVED: {output_path} ===")
