"""
MURO MISTO ALPI — ITERAZIONE 4
Ritorno a parametri più bilanciati (iter2 V3 era buono).
Fix: displacement moderato (4cm), AO singola, camera riempie il frame col muro,
colore più caldo/realistico, scala pietre bilanciata.
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


def make_misto_alpi(name, tex):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1200, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (800, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-1600, 0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1400, 0)
    mp.inputs["Scale"].default_value = (0.75, 0.75, 0.75)  # Medium-large stones
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])

    def tx(label, path, cs, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.label = label; n.location = loc
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = cs
        n.projection = 'BOX'; n.projection_blend = 0.3
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n

    # === COLOR: Diff * AO → Contrast → HSV → Color Variation → Base Color ===
    td = tx("Diff", tex["diff"], "sRGB", (-1000, 500))
    ta = tx("AO", tex["ao"], "Non-Color", (-1000, 300))

    # Single AO multiply (not double!)
    mx_ao = nt.nodes.new("ShaderNodeMix")
    mx_ao.data_type = 'RGBA'; mx_ao.blend_type = 'MULTIPLY'
    mx_ao.location = (-600, 400); mx_ao.inputs["Factor"].default_value = 1.0
    nt.links.new(td.outputs["Color"], mx_ao.inputs[6])
    nt.links.new(ta.outputs["Color"], mx_ao.inputs[7])

    # Moderate contrast
    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location = (-400, 400)
    bc.inputs["Contrast"].default_value = 0.18
    bc.inputs["Bright"].default_value = 0.03
    nt.links.new(mx_ao.outputs[2], bc.inputs["Color"])

    # HSV — slightly warm
    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location = (-200, 400)
    hsv.inputs["Saturation"].default_value = 0.88  # A bit more color
    hsv.inputs["Value"].default_value = 1.20       # Good brightness
    nt.links.new(bc.outputs["Color"], hsv.inputs["Color"])

    # Subtle warm/cool variation via noise
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.location = (-600, 100)
    noise.inputs["Scale"].default_value = 1.5   # Large patches
    noise.inputs["Detail"].default_value = 2.0
    noise.inputs["Roughness"].default_value = 0.5
    nt.links.new(tc.outputs["Generated"], noise.inputs["Vector"])

    # Mix: cool grey base ↔ slightly warm shifted version
    warm_shift = nt.nodes.new("ShaderNodeHueSaturation"); warm_shift.location = (0, 200)
    warm_shift.inputs["Hue"].default_value = 0.52       # Tiny warm shift
    warm_shift.inputs["Saturation"].default_value = 1.1  # More saturated in warm areas
    warm_shift.inputs["Value"].default_value = 0.98
    nt.links.new(hsv.outputs["Color"], warm_shift.inputs["Color"])

    color_var = nt.nodes.new("ShaderNodeMix")
    color_var.data_type = 'RGBA'
    color_var.location = (200, 400)
    nt.links.new(noise.outputs["Fac"], color_var.inputs["Factor"])
    nt.links.new(hsv.outputs["Color"], color_var.inputs[6])         # Cool base
    nt.links.new(warm_shift.outputs["Color"], color_var.inputs[7])  # Warm variant

    nt.links.new(color_var.outputs[2], bsdf.inputs["Base Color"])

    # === ROUGHNESS ===
    tr = tx("Rough", tex["rough"], "Non-Color", (-1000, -100))
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    # === NORMAL + BUMP ===
    tn = tx("Nor", tex["nor"], "Non-Color", (-1000, -300))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-600, -300)
    nm.inputs["Strength"].default_value = 2.5
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    tdi = tx("Disp", tex["disp"], "Non-Color", (-1000, -500))
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location = (-400, -450)
    bmp.inputs["Strength"].default_value = 0.6
    bmp.inputs["Distance"].default_value = 0.02
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])
    nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])

    # === TRUE DISPLACEMENT — balanced ===
    disp_node = nt.nodes.new("ShaderNodeDisplacement"); disp_node.location = (800, -300)
    disp_node.inputs["Scale"].default_value = 0.04    # 4cm (not 5.5!)
    disp_node.inputs["Midlevel"].default_value = 0.5  # Centered
    nt.links.new(tdi.outputs["Color"], disp_node.inputs["Height"])
    nt.links.new(disp_node.outputs["Displacement"], out.inputs["Displacement"])

    mat.displacement_method = 'BOTH'
    return mat


# === SCENE ===
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# HDRI
world = bpy.data.worlds.new("World"); scene.world = world
world.use_nodes = True
wnt = world.node_tree; wnt.nodes.clear()
bg = wnt.nodes.new("ShaderNodeBackground")
env = wnt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(hdri_path)
mpw = wnt.nodes.new("ShaderNodeMapping")
tcw = wnt.nodes.new("ShaderNodeTexCoord")
outw = wnt.nodes.new("ShaderNodeOutputWorld")
bg.inputs["Strength"].default_value = 2.5  # Balanced light
mpw.inputs["Rotation"].default_value = (0, 0, math.radians(40))  # Side light
wnt.links.new(tcw.outputs["Generated"], mpw.inputs["Vector"])
wnt.links.new(mpw.outputs["Vector"], env.inputs["Vector"])
wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
wnt.links.new(bg.outputs["Background"], outw.inputs["Surface"])

# Ground
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
gnd = bpy.context.active_object
mg = bpy.data.materials.new("Ground"); mg.use_nodes = True
mg.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.06, 0.07, 0.04, 1)
mg.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95
gnd.data.materials.append(mg)

# Wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.25))
wall = bpy.context.active_object; wall.name = "Wall"
wall.scale = (4.0, 0.45, 2.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

subsurf = wall.modifiers.new("SubSurf", 'SUBSURF')
subsurf.subdivision_type = 'SIMPLE'
subsurf.levels = 0
subsurf.render_levels = 6

wall.data.materials.append(make_misto_alpi("MistoAlpi", tex))

# Camera — frame filled with wall, slight 3/4 angle like product photo
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0.8, -4.2, 1.4)      # More centered, lower
cam_obj.rotation_euler = (math.radians(82), 0, math.radians(6))  # Nearly frontal
cam_data.lens = 42  # Moderate telephoto

# Render — 256 samples
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 256
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

out_path = os.path.join(OUT_DIR, "misto_alpi_iter4_balanced.png")
scene.render.filepath = out_path

print(f"\n=== MISTO ALPI ITER 4 — Balanced displacement + warm/cool variation ===")
bpy.ops.render.render(write_still=True)
print(f"=== SAVED: {out_path} ===")
