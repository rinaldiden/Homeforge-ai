"""
MURO MISTO ALPI — ITERAZIONE 3
Base: V3_deep (vincitrice iter2)
Fix: giunti malta più scuri, displacement più forte, camera migliore,
     più variazione cromatica (hue shift via noise texture overlay).
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
    """
    Material Misto Alpi con:
    - TRUE displacement forte (5cm)
    - AO molto forte per giunti neri
    - Color variation via Noise texture (warm/cool shifts)
    - Strong normal + bump
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1200, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (800, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Tex coords + mapping
    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-1600, 0)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1400, 0)
    mp.inputs["Scale"].default_value = (0.65, 0.65, 0.65)  # Bigger stones
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])

    def tx(label, path, cs, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.label = label; n.location = loc
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = cs
        n.projection = 'BOX'; n.projection_blend = 0.3
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n

    # === COLOR CHAIN ===
    td = tx("Diff", tex["diff"], "sRGB", (-1000, 500))
    ta = tx("AO", tex["ao"], "Non-Color", (-1000, 300))

    # AO multiply — FULL strength for deep dark mortar joints
    mx_ao = nt.nodes.new("ShaderNodeMix")
    mx_ao.data_type = 'RGBA'; mx_ao.blend_type = 'MULTIPLY'
    mx_ao.location = (-600, 400); mx_ao.inputs["Factor"].default_value = 1.0
    nt.links.new(td.outputs["Color"], mx_ao.inputs[6])
    nt.links.new(ta.outputs["Color"], mx_ao.inputs[7])

    # Extra darkening of AO areas — multiply AO twice for really dark joints
    mx_ao2 = nt.nodes.new("ShaderNodeMix")
    mx_ao2.data_type = 'RGBA'; mx_ao2.blend_type = 'MULTIPLY'
    mx_ao2.location = (-400, 400); mx_ao2.inputs["Factor"].default_value = 0.5  # 50% extra AO
    nt.links.new(mx_ao.outputs[2], mx_ao2.inputs[6])
    nt.links.new(ta.outputs["Color"], mx_ao2.inputs[7])

    # Brightness/Contrast — boost contrast for mortar depth
    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location = (-200, 400)
    bc.inputs["Contrast"].default_value = 0.25
    bc.inputs["Bright"].default_value = 0.0
    nt.links.new(mx_ao2.outputs[2], bc.inputs["Color"])

    # HSV — balanced for alpine stone
    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.location = (0, 400)
    hsv.inputs["Saturation"].default_value = 0.85
    hsv.inputs["Value"].default_value = 1.20
    nt.links.new(bc.outputs["Color"], hsv.inputs["Color"])

    # === COLOR VARIATION — Noise-based warm/cool shift ===
    # Large-scale noise to add warm brown patches over cool grey base
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.location = (-600, 100)
    noise.inputs["Scale"].default_value = 2.0  # Large patches
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Roughness"].default_value = 0.6
    nt.links.new(tc.outputs["Generated"], noise.inputs["Vector"])

    # Warm color overlay
    warm = nt.nodes.new("ShaderNodeMix")
    warm.data_type = 'RGBA'; warm.blend_type = 'OVERLAY'
    warm.location = (200, 400); warm.inputs["Factor"].default_value = 0.12  # Subtle
    # Warm brown-grey tint
    warm_color = nt.nodes.new("ShaderNodeRGB"); warm_color.location = (0, 150)
    warm_color.outputs[0].default_value = (0.45, 0.35, 0.28, 1.0)  # Warm brown

    nt.links.new(hsv.outputs["Color"], warm.inputs[6])
    nt.links.new(warm_color.outputs[0], warm.inputs[7])

    # Modulate overlay with noise (only apply warm tint in some areas)
    mix_final = nt.nodes.new("ShaderNodeMix")
    mix_final.data_type = 'RGBA'
    mix_final.location = (400, 400)
    nt.links.new(noise.outputs["Fac"], mix_final.inputs["Factor"])
    nt.links.new(hsv.outputs["Color"], mix_final.inputs[6])    # Cool grey original
    nt.links.new(warm.outputs[2], mix_final.inputs[7])         # Warm-tinted version

    nt.links.new(mix_final.outputs[2], bsdf.inputs["Base Color"])

    # === ROUGHNESS ===
    tr = tx("Rough", tex["rough"], "Non-Color", (-1000, -100))
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])

    # === NORMAL + BUMP ===
    tn = tx("Nor", tex["nor"], "Non-Color", (-1000, -300))
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-600, -300)
    nm.inputs["Strength"].default_value = 2.8  # Strong normal
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])

    tdi = tx("Disp", tex["disp"], "Non-Color", (-1000, -500))

    # Bump for micro-detail
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.location = (-400, -450)
    bmp.inputs["Strength"].default_value = 0.7
    bmp.inputs["Distance"].default_value = 0.025
    nt.links.new(tdi.outputs["Color"], bmp.inputs["Height"])
    nt.links.new(nm.outputs["Normal"], bmp.inputs["Normal"])
    nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])

    # === TRUE DISPLACEMENT (strong) ===
    disp_node = nt.nodes.new("ShaderNodeDisplacement"); disp_node.location = (800, -300)
    disp_node.inputs["Scale"].default_value = 0.055  # 5.5cm! Deep relief
    disp_node.inputs["Midlevel"].default_value = 0.4  # More outward protrusion
    nt.links.new(tdi.outputs["Color"], disp_node.inputs["Height"])
    nt.links.new(disp_node.outputs["Displacement"], out.inputs["Displacement"])

    mat.displacement_method = 'BOTH'
    return mat


# === SCENE ===
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# HDRI — strong lateral light to cast shadows in mortar joints
world = bpy.data.worlds.new("World"); scene.world = world
world.use_nodes = True
wnt = world.node_tree; wnt.nodes.clear()
bg = wnt.nodes.new("ShaderNodeBackground")
env = wnt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(hdri_path)
mpw = wnt.nodes.new("ShaderNodeMapping")
tcw = wnt.nodes.new("ShaderNodeTexCoord")
outw = wnt.nodes.new("ShaderNodeOutputWorld")
bg.inputs["Strength"].default_value = 3.0  # Strong HDRI
mpw.inputs["Rotation"].default_value = (0, 0, math.radians(30))  # Side light for shadow depth
wnt.links.new(tcw.outputs["Generated"], mpw.inputs["Vector"])
wnt.links.new(mpw.outputs["Vector"], env.inputs["Vector"])
wnt.links.new(env.outputs["Color"], bg.inputs["Color"])
wnt.links.new(bg.outputs["Background"], outw.inputs["Surface"])

# Ground — dark alpine earth
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
gnd = bpy.context.active_object
mg = bpy.data.materials.new("Ground"); mg.use_nodes = True
mg.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.06, 0.03, 1)
mg.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95
gnd.data.materials.append(mg)

# Wall with TRUE displacement
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.25))
wall = bpy.context.active_object; wall.name = "Wall"
wall.scale = (4.0, 0.45, 2.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# High subdivision for detailed displacement
subsurf = wall.modifiers.new("SubSurf", 'SUBSURF')
subsurf.subdivision_type = 'SIMPLE'
subsurf.levels = 0
subsurf.render_levels = 7  # Higher for more displacement detail

wall.data.materials.append(make_misto_alpi("MistoAlpi", tex))

# Camera — 3/4 view, closer to wall face, filling frame with stone
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.5, -3.8, 1.6)     # Closer, centered on wall
cam_obj.rotation_euler = (math.radians(82), 0, math.radians(10))
cam_data.lens = 40  # Slight telephoto to flatten perspective like product photo

# Render — 256 samples for better quality
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

out_path = os.path.join(OUT_DIR, "misto_alpi_iter3_deep_mortar.png")
scene.render.filepath = out_path

print(f"\n=== MISTO ALPI ITER 3 — Deep mortar, strong displacement, color variation ===")
bpy.ops.render.render(write_still=True)
print(f"=== SAVED: {out_path} ===")
